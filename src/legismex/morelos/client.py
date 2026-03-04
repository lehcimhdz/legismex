import httpx
from bs4 import BeautifulSoup, Tag
from typing import List, Optional
from .models import MorelosDocumento


class MorelosClient:
    """Client for the Congreso del Estado de Morelos (LVI Legislatura).

    Scrapes the single "Documentos Legislativos" page built with WordPress/Divi
    to extract all PDF links organised by section (actas, órdenes del día,
    versiones estenográficas, legislación, etc.).
    """

    BASE_URL = "https://congresomorelos.gob.mx"
    PAGE_URL = f"{BASE_URL}/documentos-legislativos/"

    # Anchor IDs that delimit each section on the page
    SECCIONES = {
        "Actas-de-sesiones-Solemnes": "Actas de sesiones Solemnes",
        "Públicas-Ordinarias": "Actas de sesiones Públicas Ordinarias",
        "Diputación-Permanente": "Actas de sesiones de la Diputación Permanente",
        "Orden-del-día": "Orden del día",
        "Versiones-estenográficas": "Versiones estenográficas",
        "Leyes-y-Códigos": "Legislación (Leyes y Códigos)",
    }

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(follow_redirects=True, timeout=30)
        else:
            self._client = client

    def _fetch_page(self) -> BeautifulSoup:
        response = self._client.get(self.PAGE_URL)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    @staticmethod
    def _normalise_url(href: str, base: str) -> str:
        """Turn relative paths and broken server paths into absolute URLs."""
        if href.startswith("http:///srv/htdocs"):
            # Broken links left by the CMS — attempt to fix
            href = href.replace("http:///srv/htdocs", "")
        if href.startswith("/"):
            return base + href
        return href

    def obtener_documentos(
        self, seccion: Optional[str] = None
    ) -> List[MorelosDocumento]:
        """Return all legislative documents from the page.

        Args:
            seccion: Optional section anchor ID to filter by (e.g.
                     "Orden-del-día"). Use SECCIONES keys for valid values.
                     If None, all documents are returned.

        Returns:
            List of MorelosDocumento with titulo, url_pdf, seccion, and
            periodo (when detectable).
        """
        soup = self._fetch_page()
        results: List[MorelosDocumento] = []

        # Walk all blurb links that point to PDFs
        for a_tag in soup.select(".et_pb_blurb a[href$='.pdf']"):
            href = a_tag.get("href", "")
            if not href:
                continue

            # Extract title from the closest <h4>
            blurb = a_tag.find_parent(class_="et_pb_blurb")
            h4 = blurb.find("h4") if blurb else None
            titulo = h4.get_text(strip=True).replace("⬇️", "").strip() if h4 else ""
            if not titulo:
                titulo = a_tag.get_text(strip=True).replace("⬇️", "").strip()

            # Determine which section this belongs to
            sec_label = self._find_section(a_tag)

            # Detect periodo
            periodo = self._find_periodo(a_tag)

            url = self._normalise_url(href, self.BASE_URL)

            results.append(
                MorelosDocumento(
                    titulo=titulo,
                    url_pdf=url,
                    seccion=sec_label,
                    periodo=periodo,
                )
            )

        if seccion:
            target_label = self.SECCIONES.get(seccion, seccion)
            results = [d for d in results if d.seccion == target_label]

        return results

    def _find_section(self, tag: Tag) -> Optional[str]:
        """Walk up the DOM to find the nearest section anchor ID."""
        for parent in tag.parents:
            if not isinstance(parent, Tag):
                continue
            # Check preceding siblings for section anchor blurbs
            for prev in parent.find_all_previous(attrs={"id": True}):
                pid = prev.get("id", "")
                if pid in self.SECCIONES:
                    return self.SECCIONES[pid]
        return None

    @staticmethod
    def _find_periodo(tag: Tag) -> Optional[str]:
        """Try to detect 'Primer Periodo' or 'Segundo Periodo' nearby."""
        for parent in tag.parents:
            if not isinstance(parent, Tag):
                continue
            for prev in parent.find_all_previous(class_="et_pb_blurb"):
                h4 = prev.find("h4")
                if h4:
                    text = h4.get_text(strip=True)
                    if "Primer Periodo" in text:
                        return "Primer Periodo"
                    if "Segundo Periodo" in text:
                        return "Segundo Periodo"
                    # Stop when we find a section header instead
                    if "Actas" in text or "Orden" in text or "Versiones" in text:
                        break
        return None
