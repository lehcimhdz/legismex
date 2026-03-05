import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from .models import TlaxcalaDocumento


class TlaxcalaClient:
    """Client for the Trabajo Legislativo of the Congreso de Tlaxcala (LXV).

    Scrapes the Visual Composer tab layout at
    ``congresodetlaxcala.gob.mx/trabajo-legislativo65/``.
    The page renders all data server-side with 12 legislative categories
    (Decretos, Iniciativas, Acuerdos, etc.) each split across yearly panels
    (2024, 2025, 2026).
    """

    URL = "https://congresodetlaxcala.gob.mx/trabajo-legislativo65/"

    # Tab names in order as they appear on the page
    CATEGORIAS = [
        "Programa Legislativo",
        "Decretos",
        "Orden del día",
        "Iniciativas",
        "Asistencia",
        "Diario de debates",
        "Acuerdos",
        "Correspondencia",
        "Dictámenes",
        "Votaciones",
        "Versiones estenográficas",
        "Actas de Sesión",
    ]

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(follow_redirects=True, timeout=60)
        else:
            self._client = client
        self._soup: Optional[BeautifulSoup] = None

    def _get_soup(self) -> BeautifulSoup:
        """Fetch and cache the main page."""
        if self._soup is None:
            r = self._client.get(self.URL)
            r.raise_for_status()
            self._soup = BeautifulSoup(r.text, "html.parser")
        return self._soup

    def _parse_panel(self, panel, categoria: str, anio: int) -> List[TlaxcalaDocumento]:
        """Parse documents from a single year panel within a tab."""
        docs: List[TlaxcalaDocumento] = []

        # Most tabs use a table with columns: Número, Fecha, <description with PDF>
        rows = panel.select("table tr")
        if rows:
            for tr in rows:
                tds = tr.find_all("td")
                if len(tds) < 2:
                    continue
                pdf_a = tr.find("a", href=lambda h: h and ".pdf" in h.lower())
                if not pdf_a:
                    continue

                # Extract columns depending on number of cells
                if len(tds) >= 3:
                    numero = tds[0].get_text(strip=True)
                    fecha = tds[1].get_text(strip=True)
                    titulo = pdf_a.get_text(strip=True)
                else:
                    numero = None
                    fecha = tds[0].get_text(strip=True) if len(tds) > 1 else None
                    titulo = pdf_a.get_text(strip=True)

                docs.append(
                    TlaxcalaDocumento(
                        categoria=categoria,
                        anio=anio,
                        numero=numero or None,
                        fecha=fecha or None,
                        titulo=titulo,
                        url_pdf=pdf_a["href"],
                    )
                )
        else:
            # Fallback: plain <a href="*.pdf"> links (e.g. Programa Legislativo)
            for a in panel.select("a[href]"):
                if ".pdf" in a.get("href", "").lower():
                    docs.append(
                        TlaxcalaDocumento(
                            categoria=categoria,
                            anio=anio,
                            titulo=a.get_text(strip=True),
                            url_pdf=a["href"],
                        )
                    )

        return docs

    def obtener_documentos(
        self,
        categoria: Optional[str] = None,
        anio: Optional[int] = None,
    ) -> List[TlaxcalaDocumento]:
        """Fetch all legislative documents with optional filters.

        Args:
            categoria: Filter by category name (partial match, case-insensitive).
                       E.g. ``'Decretos'``, ``'Iniciativas'``, ``'Acuerdos'``.
            anio: Filter by year (2024, 2025 or 2026).

        Returns:
            List of TlaxcalaDocumento objects matching the filters.
        """
        soup = self._get_soup()

        # Tab nav items map to tab panels by position
        nav_items = soup.select(".mpc-tabs__nav-item .mpc-button__title")
        tab_names = [n.get_text(strip=True) for n in nav_items]
        panels = soup.select(".mpc-tab")

        results: List[TlaxcalaDocumento] = []

        for tab_panel, tab_name in zip(panels, tab_names):
            # Apply category filter
            if categoria and categoria.lower() not in tab_name.lower():
                continue

            # Each tab has inner year panels (.vc_tta-panel)
            year_panels = tab_panel.select(".vc_tta-panel")
            for year_panel in year_panels:
                year_el = year_panel.select_one(".vc_tta-title-text")
                try:
                    yr = int(year_el.get_text(strip=True)) if year_el else 0
                except ValueError:
                    yr = 0

                if anio and yr != anio:
                    continue

                docs = self._parse_panel(year_panel, tab_name, yr)
                results.extend(docs)

        return results
