import httpx
from bs4 import BeautifulSoup
from typing import List
from .models import CampecheGaceta


class CampecheClient:
    """Cliente para extraer gacetas parlamentarias del Congreso del Estado de Campeche."""
    BASE_URL = "https://www.congresocam.gob.mx/gaceta/"

    def __init__(self, **kwargs):
        """
        Inicializa el cliente de Campeche.

        Args:
            **kwargs: Argumentos adicionales para httpx.Client o AsyncClient.
        """
        self.client_kwargs = {
            "verify": False,
            "timeout": 30.0,
            **kwargs
        }

    def _parsear_html(self, html: str) -> List[CampecheGaceta]:
        """Extrae la lista de gacetas del HTML provisto."""
        soup = BeautifulSoup(html, "html.parser")
        gacetas = []

        # Las pestañas de legislaturas y sus contenidos están en .tab-content > .tab-pane
        tab_content = soup.find("div", class_="tab-content")
        if not tab_content:
            return gacetas

        panes = tab_content.find_all("div", class_="tab-pane", recursive=False)

        for pane in panes:
            # Intentar buscar el nombre de la legislatura en el id del pane
            pane_id = pane.get("id", "")

            # Buscaremos primero en las navegaciones locales o de escritorio (ul.nav-tabs)
            legislatura_nombre = "NO ESPECIFICADA"
            nav_tabs = soup.find("ul", class_="nav-tabs")
            if nav_tabs:
                tab_link = nav_tabs.find("a", href=f"#{pane_id}")
                if tab_link:
                    legislatura_nombre = tab_link.get_text(
                        separator=" ", strip=True)

            # Parsear los directory-lister-wrapper dentro de este pane
            listers = pane.find_all("div", class_="directory-lister-wrapper")
            for lister in listers:
                enlaces = lister.find_all("a", class_="soubor-link")
                for a_tag in enlaces:
                    titulo = a_tag.get_text(strip=True)
                    url_pdf = a_tag.get("href", "")

                    if url_pdf:
                        gacetas.append(CampecheGaceta(
                            titulo=titulo,
                            legislatura=legislatura_nombre,
                            url_pdf=url_pdf
                        ))

        return gacetas

    def obtener_gacetas(self) -> List[CampecheGaceta]:
        """
        Obtiene el histórico estático completo de gacetas de Campeche de forma síncrona.
        """
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with httpx.Client(**self.client_kwargs) as client:
                response = client.get(self.BASE_URL)
                response.raise_for_status()
                return self._parsear_html(response.text)

    async def a_obtener_gacetas(self) -> List[CampecheGaceta]:
        """
        Obtiene el histórico estático completo de gacetas de Campeche de forma asíncrona.
        """
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            async with httpx.AsyncClient(**self.client_kwargs) as client:
                response = await client.get(self.BASE_URL)
                response.raise_for_status()
                return self._parsear_html(response.text)
