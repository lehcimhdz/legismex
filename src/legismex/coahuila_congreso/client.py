import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
import re
from .models import CoahuilaIniciativa


class CoahuilaCongresoClient:
    """
    Cliente para la extracción de Iniciativas del H. Congreso del Estado de Coahuila.
    Extrae la lista de iniciativas desde la aplicación JSF (PrimeFaces).
    """
    URL_INICIATIVAS = "https://www.congresocoahuila.gob.mx/estadistica/iniciativa"

    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _extraer_url_onclick(self, button_tag) -> Optional[str]:
        """Extrae la URL contenida en window.open('...') dentro del atributo onclick."""
        if not button_tag:
            return None
        onclick_attr = button_tag.get("onclick", "")
        # Extraer usando regex window.open('URL')
        match = re.search(r"window\.open\('([^']+)'\)", onclick_attr)
        if match:
            return match.group(1)
        return None

    def _parsear_iniciativa(self, row: BeautifulSoup) -> Optional[CoahuilaIniciativa]:
        """Extrae la información de un tr de la tabla PrimeFaces."""
        tds = row.find_all("td")
        # En la tabla principal hay 8 columnas
        if len(tds) < 8:
            return None

        fecha = tds[0].get_text(strip=True)
        origen = tds[1].get_text(strip=True)
        ponente = tds[2].get_text(strip=True)
        descripcion = tds[3].get_text(strip=True)
        legislatura = tds[4].get_text(strip=True)
        anio_legislativo = tds[5].get_text(strip=True)

        url_pdf = None
        url_abierto = None

        try:
            # pdf button is in column 6
            btn_pdf = tds[6].find("button")
            url_pdf = self._extraer_url_onclick(btn_pdf)

            # docx button is in column 7
            btn_docx = tds[7].find("button")
            url_abierto = self._extraer_url_onclick(btn_docx)
        except Exception:
            pass

        # Validar si realmente hay un registro vacio, JSF a veces inyecta tr vacios para padding
        if not fecha and not descripcion:
            return None

        return CoahuilaIniciativa(
            fecha=fecha,
            origen=origen,
            ponente=ponente,
            descripcion=descripcion,
            legislatura=legislatura,
            anio_legislativo=anio_legislativo,
            url_pdf=url_pdf,
            url_abierto=url_abierto
        )

    def _procesar_html(self, html_content: str) -> List[CoahuilaIniciativa]:
        soup = BeautifulSoup(html_content, "html.parser")
        iniciativas = []

        # Encontrar la tabla que tiene los resultados data
        tbody = soup.find("tbody", id="frm:grid_data")
        if not tbody:
            return iniciativas

        rows = tbody.find_all("tr", recursive=False)
        for row in rows:
            iniciativa = self._parsear_iniciativa(row)
            if iniciativa:
                iniciativas.append(iniciativa)

        return iniciativas

    def obtener_iniciativas(self) -> List[CoahuilaIniciativa]:
        """
        Extrae la primera página de iniciativas (más recientes) síncronamente.
        """
        with httpx.Client(timeout=self.timeout, follow_redirects=True, verify=False) as client:
            response = client.get(self.URL_INICIATIVAS, headers=self.headers)
            response.raise_for_status()
            return self._procesar_html(response.text)

    async def a_obtener_iniciativas(self) -> List[CoahuilaIniciativa]:
        """
        Extrae la primera página de iniciativas (más recientes) asíncronamente.
        """
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
            response = await client.get(self.URL_INICIATIVAS, headers=self.headers)
            response.raise_for_status()
            return self._procesar_html(response.text)
