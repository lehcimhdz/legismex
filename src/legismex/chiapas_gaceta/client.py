import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin
from .models import ChiapasGaceta


class ChiapasGacetaClient:
    """Cliente para obtener Gacetas del H. Congreso del Estado de Chiapas."""

    BASE_URL = "https://web.congresochiapas.gob.mx/trabajo-legislativo/gaceta-parlamentaria"
    API_URL = "https://web.congresochiapas.gob.mx/phpplugins/global_gacetas.php?act=deb_init_data"

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "verify": False,
            "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            **kwargs,
        }

    def _parsear_html(self, html: str) -> List[ChiapasGaceta]:
        """A partir de una página de la Gaceta Parlamentaria, extrae las gacetas de tblDatos."""
        gacetas = []
        soup = BeautifulSoup(html, "html.parser")

        # Hay una o más tablas tblDatos (o sin ID pero que funjan como eso)
        # Nos guiamos por id="tblDatos"
        tables = soup.find_all("table", id="tblDatos")
        for table in tables:
            tbody = table.find("tbody")
            if not tbody:
                continue

            filas = tbody.find_all("tr")
            for fila in filas:
                celdas = fila.find_all("td")

                # De acuerdo al código fuente:
                # td[0]: Num.132
                # td[1]: II
                # td[2]: Gaceta 30 de Enero 2026.
                # td[3]: Primer Periodo Permanente
                # td[4]: Flipbook (a con href)
                # td[5]: Descargable PDF (a con href)

                if len(celdas) >= 6:
                    numero = celdas[0].get_text(strip=True)
                    anio = celdas[1].get_text(strip=True)
                    titulo = celdas[2].get_text(strip=True)
                    periodo = celdas[3].get_text(strip=True)

                    url_flip = ""
                    a_flip = celdas[4].find("a", href=True)
                    if a_flip:
                        url_flip = a_flip["href"]

                    url_pdf = ""
                    a_pdf = celdas[5].find("a", href=True)
                    if a_pdf:
                        url_pdf = a_pdf["href"]

                    # Validar URLs incompletas o erróneas (por ej. si inician con #)
                    if url_pdf.startswith("http"):
                        pass
                    elif url_pdf:
                        url_pdf = urljoin(self.BASE_URL, url_pdf)

                    if url_flip.startswith("http"):
                        pass
                    elif url_flip:
                        url_flip = urljoin(self.BASE_URL, url_flip)

                    gacetas.append(ChiapasGaceta(
                        numero=numero,
                        anio=anio,
                        titulo=titulo,
                        periodo=periodo,
                        url_flipbook=url_flip,
                        url_pdf=url_pdf
                    ))

        return gacetas

    # ----------- Síncrono -----------

    def obtener_gacetas(self) -> List[ChiapasGaceta]:
        """Obtiene todas las gacetas publicadas síncronamente en la página web mediante el endpoint AJAX."""
        payload = {"dir": "../../pdf/gacetas", "margin": 0, "nivel": 0}
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.post(self.API_URL, data=payload)
            resp.raise_for_status()
            return self._parsear_html(resp.text)

    # ----------- Asíncrono -----------

    async def a_obtener_gacetas(self) -> List[ChiapasGaceta]:
        """Obtiene todas las gacetas publicadas de forma asíncrona mediante el endpoint AJAX."""
        payload = {"dir": "../../pdf/gacetas", "margin": 0, "nivel": 0}
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.post(self.API_URL, data=payload)
            resp.raise_for_status()
            return self._parsear_html(resp.text)
