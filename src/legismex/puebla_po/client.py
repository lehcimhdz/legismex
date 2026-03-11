import httpx
import re
from typing import Optional, Dict

from .models import PueblaPoPaginacion, PueblaPoEdicion


class PueblaPoClient:
    """
    Cliente para interactuar con el Periódico Oficial del Estado de Puebla.
    La información es obtenida desde un endpoint interno implementado en PHP (`getjsonnew.php`)
    que permite filtros por tomo, sección, número o palabra clave abierta.
    """

    BASE_URL = "https://periodicooficial.puebla.gob.mx"
    SEARCH_ENDPOINT = f"{BASE_URL}/modules/mod_k2_calendar/tmpl/Default/getjsonnew.php"

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        # Headers mínimos para mimetizar petición de ajax
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/"
        }

    def buscar_ediciones(
        self,
        rango: int = 25,
        pagina: int = 1,
        tomo: str = "0",
        seccion: str = "0",
        numero: str = "0",
        texto: str = "",
        tipob: str = "sumario"
    ) -> PueblaPoPaginacion:
        """
        Realiza una búsqueda avanzada en el portal del Periódico Oficial de Puebla.

        Argumentos:
            rango (int): Resultados por página (ej., 10, 25, 50, 100).
            pagina (int): Número de página a consultar.
            tomo (str): Filtrar por un 'Tomo' en específico, "0" significa Todos.
            seccion (str): Filtrar por una 'Sección' específica, "0" significa Todos.
            numero (str): Filtrar por el 'Número' de periódico, "0" significa Todos.
            texto (str): Palabra clave de búsqueda libre.
            tipob (str): Tipo de búsqueda, puede ser "sumario" o "todo" el documento.

        Retorna:
            PueblaPoPaginacion: Metadatos y lista de documentos `PueblaPoEdicion`.
        """
        data = {
            "origen": "advanced",
            "rango": str(rango),
            "tomo": tomo,
            "seccion": seccion,
            "numero": numero,
            "texto": texto,
            "tipob": tipob,
            "fecha": "0",  # El portal envia 0 cuando es Búsqueda Avanzada genérica
            "pag": str(pagina)
        }

        with httpx.Client(verify=False, timeout=self.timeout, follow_redirects=True) as client:
            response = client.post(self.SEARCH_ENDPOINT,
                                   data=data, headers=self.headers)
            response.raise_for_status()
            json_data = response.json()

        return self._parsear_resultados(json_data)

    def _parsear_resultados(self, json_data: dict) -> PueblaPoPaginacion:
        """
        Parsea los items contenidos en el JSON devuelto por el servidor y extrae metadatos.
        """
        meta_cantidad = json_data.get("amount", 0)
        items = json_data.get("items", [])

        if isinstance(meta_cantidad, str) and meta_cantidad.isdigit():
            meta_cantidad = int(meta_cantidad)

        ediciones = []
        for item in items:
            # item.get('title') => Ej. "Tomo: CDLXXVIII Número: 7 Sección: Segunda"
            raw_title = item.get("title", "")

            # Utilizar REGEX simplificada para mapear campos desde raw_title
            # Tomo: ([^\s]+)\s+Número:\s+([^\s]+)\s+Sección:\s+(.*)
            tomo_val = None
            numero_val = None
            seccion_val = None

            tomo_match = re.search(
                r'Tomo:\s+([a-zA-Z0-9_]+)', raw_title, re.IGNORECASE)
            numero_match = re.search(
                r'Número:\s+([a-zA-Z0-9_\/]+)', raw_title, re.IGNORECASE)
            seccion_match = re.search(
                r'Sección:\s+(.*)', raw_title, re.IGNORECASE)

            if tomo_match:
                tomo_val = tomo_match.group(1).strip()
            if numero_match:
                numero_val = numero_match.group(1).strip()
            if seccion_match:
                seccion_val = seccion_match.group(1).strip()

            archivo = item.get("archivo", "")
            url_pdf = f"{self.BASE_URL}/media/k2/attachments/{archivo}" if archivo else ""

            edicion = PueblaPoEdicion(
                id_publicacion=str(item.get("id", "")),
                fecha=item.get("fecha") if item.get("fecha") else None,
                tomo=tomo_val,
                numero=numero_val,
                seccion=seccion_val,
                descripcion=item.get("descripcion", ""),
                url_pdf=url_pdf,
                archivo_local=archivo
            )

            ediciones.append(edicion)

        return PueblaPoPaginacion(
            cantidad_total=meta_cantidad,
            ediciones=ediciones
        )
