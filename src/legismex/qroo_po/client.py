import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime, date
import calendar

from .models import QrooPoPublicacion


class QrooPoClient:
    """Cliente para el Periódico Oficial del Estado de Quintana Roo."""
    BASE_URL = "http://po.segob.qroo.gob.mx/sitiopo"

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "verify": False,
            "follow_redirects": True,
            **kwargs
        }

    def _preparar_parametros(self, anio: int, mes: int, pagina: int = 1) -> dict:
        _, ultimo_dia = calendar.monthrange(anio, mes)
        fecha_inicio = f"{anio}-{mes:02d}-01"
        fecha_fin = f"{anio}-{mes:02d}-{ultimo_dia:02d}"

        params = {
            "Titulo": "",
            "FechaPublicacion": fecha_inicio,
            "FechaPublicacion2": fecha_fin,
            "IdTipo": "0",  # Todos
            "IdEpoca": "0",  # Todos
            "Buscar": "1"
        }
        if pagina > 1:
            params["Pagina"] = str(pagina)

        return params

    def _extraer_publicaciones_de_html(self, html: str) -> List[QrooPoPublicacion]:
        soup = BeautifulSoup(html, "html.parser")
        resultados = []

        tables = soup.find_all("table")
        if len(tables) > 1:
            table = tables[1]
            rows = table.find_all("tr")
            # Ignoramos la cabecera (index 0)
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) > 2:
                    try:
                        # Estructura: [0:Ver, 1:PDF, 2:Dia, 3:Mes, 4:Anio, 5:Tipo, 6:Numero, 7:Tomo, 8:Epoca, 9:Indices]
                        link_tag = cols[1].find("a")
                        if not link_tag:
                            continue

                        # Limpiar href url
                        href = link_tag.get("href", "")
                        url_pdf = f"{self.BASE_URL}/{href}" if not href.startswith(
                            "http") else href

                        dia_str = cols[2].get_text(strip=True)
                        anio_str = cols[4].get_text(strip=True)

                        # Mapear mes texto a int
                        meses_es = {"Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
                                    "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12}
                        mes_str = cols[3].get_text(strip=True)

                        mes_num = meses_es.get(mes_str.capitalize(), 1)
                        fecha = date(int(anio_str), mes_num, int(dia_str))

                        tipo = cols[5].get_text(strip=True)
                        numero = cols[6].get_text(strip=True)
                        tomo = cols[7].get_text(strip=True)

                        pub = QrooPoPublicacion(
                            fecha=fecha,
                            tipo=tipo,
                            numero=numero,
                            tomo=tomo,
                            url_pdf=url_pdf
                        )
                        resultados.append(pub)
                    except Exception:
                        pass
        return resultados

    def _obtener_total_paginas(self, html: str) -> int:
        soup = BeautifulSoup(html, "html.parser")
        pag = soup.find("form", {"name": "FormularioPaginado"})
        if pag:
            texto = pag.get_text(strip=True)
            # Ej: Mostrando 1 - 24 de un total de 28 registros.Número de página:1, 2
            # Evaluamos cuantas opciones hay en el select
            select = pag.find("select", {"name": "Pagina"})
            if select:
                opts = select.find_all("option")
                return len(opts)
        return 1

    def obtener_publicaciones(self, anio: int, mes: int) -> List[QrooPoPublicacion]:
        """Obtiene las publicaciones del Periódico Oficial para un mes y año específicos (Síncrono)."""
        publicaciones = []
        with httpx.Client(**self.client_kwargs) as client:
            url = f"{self.BASE_URL}/BusquedaAvanzada.php"

            # Request inicial
            params = self._preparar_parametros(anio, mes, 1)
            resp = client.get(url, params=params)
            resp.raise_for_status()

            html = resp.text
            publicaciones.extend(self._extraer_publicaciones_de_html(html))

            total_paginas = self._obtener_total_paginas(html)

            # Iterar resto
            for p in range(2, total_paginas + 1):
                params_p = self._preparar_parametros(anio, mes, p)
                resp_p = client.get(url, params=params_p)
                if resp_p.status_code == 200:
                    publicaciones.extend(
                        self._extraer_publicaciones_de_html(resp_p.text))

        return publicaciones

    async def a_obtener_publicaciones(self, anio: int, mes: int) -> List[QrooPoPublicacion]:
        """Obtiene las publicaciones del Periódico Oficial para un mes y año específicos (Asíncrono)."""
        publicaciones = []
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            url = f"{self.BASE_URL}/BusquedaAvanzada.php"

            # Request inicial
            params = self._preparar_parametros(anio, mes, 1)
            resp = await client.get(url, params=params)
            resp.raise_for_status()

            html = resp.text
            publicaciones.extend(self._extraer_publicaciones_de_html(html))

            total_paginas = self._obtener_total_paginas(html)

            if total_paginas > 1:
                tareas = []
                for p in range(2, total_paginas + 1):
                    params_p = self._preparar_parametros(anio, mes, p)
                    tareas.append(client.get(url, params=params_p))

                respuestas = await asyncio.gather(*tareas, return_exceptions=True)
                for resp_p in respuestas:
                    if isinstance(resp_p, httpx.Response) and resp_p.status_code == 200:
                        publicaciones.extend(
                            self._extraer_publicaciones_de_html(resp_p.text))

        # Evitar traslape ordenando todo
        publicaciones.sort(key=lambda x: x.fecha, reverse=True)
        return publicaciones
