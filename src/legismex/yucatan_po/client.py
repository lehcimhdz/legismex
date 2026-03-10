import httpx
from bs4 import BeautifulSoup
from typing import List
from .models import YucatanPoEdicion


class YucatanPoClient:
    """
    Cliente para la extracción de las publicaciones del Diario Oficial del Estado de Yucatán.
    Extrae la lista completa de diarios (Matutinas, Suplementos, etc.) emitidos en una fecha determinada.
    """
    BASE_URL = "http://www.yucatan.gob.mx"
    URL_DIARIO = f"{BASE_URL}/gobierno/diario_oficial.php"

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _procesar_html(self, html_content: str, fecha_buscada: str) -> List[YucatanPoEdicion]:
        soup = BeautifulSoup(html_content, "html.parser")
        ediciones = []

        # Cada publicación (Matutina, Suplemento, Índices) viene en un div.seccion_pagina
        secciones = soup.find_all("div", class_="seccion_pagina")

        for sec in secciones:
            # Buscar el subtítulo que define qué es (ej. 'Edición matutina', 'Suplemento')
            subtitulo_tag = sec.find("p", class_="subtitulo")
            if not subtitulo_tag:
                continue

            tipo_edicion = subtitulo_tag.get_text(strip=True)

            # Si es Índice General (contiene años sueltos y es otra estructura)
            # Generalmente la url_pdf está en <a> clasificados como 'pdf'
            if "ndices" in tipo_edicion.lower():
                # En extraer varios PDF si es necesario se podría hacer, pero la solicitud del scraper principal es por ediciones
                pass  # Por diseño nos concentramos en las de la fecha

            # Las ediciones normales (Matutina, Suplemento) tienen un div.small con el número
            numero_tag = sec.find("div", class_="small")
            numero = numero_tag.get_text(strip=True).replace(
                "NUM.", "").strip() if numero_tag and "NUM." in numero_tag.text else ""

            # Buscar el enlace al PDF
            pdf_tag = sec.find("a", class_="pdf", href=True)
            if not pdf_tag:
                continue

            url_pdf = pdf_tag["href"]
            if not url_pdf.startswith("http"):
                url_pdf = f"{self.BASE_URL}{url_pdf}" if url_pdf.startswith(
                    "/") else f"{self.BASE_URL}/{url_pdf}"

            # Extraer el Sumario (div class="sumario")
            sumario_tag = sec.find("div", class_="sumario")
            sumario_texto = sumario_tag.get_text(
                separator="\n", strip=True) if sumario_tag else ""

            ediciones.append(YucatanPoEdicion(
                fecha=fecha_buscada,
                tipo=tipo_edicion,
                numero=numero,
                url_pdf=url_pdf,
                sumario=sumario_texto
            ))

        return ediciones

    def obtener_ediciones_por_fecha(self, fecha: str) -> List[YucatanPoEdicion]:
        """
        Extrae la lista de ediciones publicadas en una fecha de forma síncrona.
        :param fecha: Fecha en formato libre que acepte el portal, preferiblemente YYYY-M-D. Ej: '2026-3-9'
        """
        # Limpiar padding de ceros en el mes y el día ya que el portal espera M-D para no fallar
        try:
            parts = fecha.split("-")
            if len(parts) == 3:
                f_query = f"{parts[0]}-{int(parts[1])}-{int(parts[2])}"
            else:
                f_query = fecha
        except:
            f_query = fecha

        params = {"f": f_query}
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                self.URL_DIARIO, params=params, headers=self.headers)
            response.raise_for_status()
            return self._procesar_html(response.text, fecha)

    async def a_obtener_ediciones_por_fecha(self, fecha: str) -> List[YucatanPoEdicion]:
        """Extrae la lista de ediciones asíncronamente."""
        try:
            parts = fecha.split("-")
            if len(parts) == 3:
                f_query = f"{parts[0]}-{int(parts[1])}-{int(parts[2])}"
            else:
                f_query = fecha
        except:
            f_query = fecha

        params = {"f": f_query}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.URL_DIARIO, params=params, headers=self.headers)
            response.raise_for_status()
            return self._procesar_html(response.text, fecha)
