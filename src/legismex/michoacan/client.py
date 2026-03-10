import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from .models import MichoacanGaceta


class MichoacanClient:
    """Client for the Gaceta Parlamentaria of the Michoacán State Congress.

    Scrapes the WordPress/PTB search endpoint at congresomich.gob.mx to
    retrieve gazette entries with filters for legislatura, title, keyword,
    and date range.
    """

    BASE_URL = "http://congresomich.gob.mx"

    LEGISLATURAS = ["lxxvi", "lxxv", "lxxiv",
                    "lxxiii", "lxxii", "lxxi", "i-constituyente"]

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(follow_redirects=True, timeout=30)
        else:
            self._client = client

    @staticmethod
    def _parse_articles(html: str, legislatura: Optional[str] = None) -> List[MichoacanGaceta]:
        soup = BeautifulSoup(html, "html.parser")
        results: List[MichoacanGaceta] = []

        for article in soup.select("article.ptb_post"):
            fecha_el = article.select_one("time.ptb_extra_post_date")
            titulo_el = article.select_one("h3.ptb_post_title")
            epoca_el = article.select_one(".ptb_epoca")
            tomo_el = article.select_one(".ptb_tomo_")
            numero_el = article.select_one(".ptb_numero")
            pdf_el = article.select_one("a.ptb_extra_pdf")
            texto_el = article.select_one(".ptb_texto_")

            def _clean(el, prefix: str = "") -> str:
                if el is None:
                    return ""
                text = el.get_text(strip=True)
                if prefix and text.startswith(prefix):
                    text = text[len(prefix):].strip()
                return text

            results.append(
                MichoacanGaceta(
                    fecha=_clean(fecha_el),
                    titulo=_clean(titulo_el),
                    epoca=_clean(epoca_el, "Época:") or None,
                    tomo=_clean(tomo_el, "Tomo:") or None,
                    numero=_clean(numero_el, "Número:") or None,
                    descripcion=_clean(texto_el, "Titulo:"),
                    url_pdf=pdf_el.get("href") if pdf_el else None,
                    legislatura=legislatura,
                )
            )
        return results

    @staticmethod
    def _parse_total_pages(html: str) -> int:
        soup = BeautifulSoup(html, "html.parser")
        nav = soup.select_one(".ptb_pagenav")
        if not nav:
            return 1
        page_links = nav.select("a.page-numbers:not(.next)")
        if not page_links:
            return 1
        try:
            return int(page_links[-1].get_text(strip=True))
        except (ValueError, IndexError):
            return 1

    def obtener_gacetas(
        self,
        legislatura: Optional[str] = None,
        titulo: Optional[str] = None,
        texto: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        page: int = 1,
    ) -> List[MichoacanGaceta]:
        """Fetch gazette entries from the Michoacán Congress.

        Args:
            legislatura: Legislature slug (e.g. "lxxvi"). Use LEGISLATURAS for valid values.
            titulo: Filter by gazette number/title.
            texto: Filter by description keyword.
            fecha_desde: Start date filter (DD/MM/YYYY).
            fecha_hasta: End date filter (DD/MM/YYYY).
            page: Page number (1-indexed, 10 results per page).

        Returns:
            List of MichoacanGaceta objects for the requested page.
        """
        params = {
            "f": "gacetas_",
            "ptb-search": "1",
        }
        if legislatura:
            params["legislatura_"] = legislatura.lower()
        if titulo:
            params["title"] = titulo
        if texto:
            params["texto"] = texto
        if fecha_desde:
            params["fecha-from"] = fecha_desde
        if fecha_hasta:
            params["fecha-to"] = fecha_hasta

        if page > 1:
            url = f"{self.BASE_URL}/ptb-search/page/{page}/"
        else:
            url = f"{self.BASE_URL}/ptb-search/"

        response = self._client.get(url, params=params)
        response.raise_for_status()
        return self._parse_articles(response.text, legislatura)

    def obtener_total_paginas(
        self,
        legislatura: Optional[str] = None,
        titulo: Optional[str] = None,
        texto: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
    ) -> int:
        """Get the total number of pages for a given search query."""
        params = {
            "f": "gacetas_",
            "ptb-search": "1",
        }
        if legislatura:
            params["legislatura_"] = legislatura.lower()
        if titulo:
            params["title"] = titulo
        if texto:
            params["texto"] = texto
        if fecha_desde:
            params["fecha-from"] = fecha_desde
        if fecha_hasta:
            params["fecha-to"] = fecha_hasta

        response = self._client.get(
            f"{self.BASE_URL}/ptb-search/", params=params)
        response.raise_for_status()
        return self._parse_total_pages(response.text)
