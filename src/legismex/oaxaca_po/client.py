import httpx
from bs4 import BeautifulSoup
from typing import List, Optional, Literal
from .models import OaxacaPoEdicion


TIPOS = Literal["Ordinario", "Extraordinario", "Secciones"]
TODOS_LOS_TIPOS = ("Ordinario", "Extraordinario", "Secciones")

# Month abbreviations used in the date column (Spanish)
_MES_MAP = {
    "ene": "01", "feb": "02", "mar": "03", "abr": "04",
    "may": "05", "jun": "06", "jul": "07", "ago": "08",
    "sep": "09", "oct": "10", "nov": "11", "dic": "12",
}


class OaxacaPoClient:
    """Client for the Periódico Oficial del Gobierno del Estado de Oaxaca.

    The site at ``periodicooficial.oaxaca.gob.mx`` serves three document types:
    *Ordinario*, *Extraordinario*, and *Secciones*.  Each type is listed on
    ``busquedadoc.php?type=<Tipo>`` which returns **all** editions of that type
    in a single page (no server-side pagination).

    PDFs are at ``http://periodicooficial.oaxaca.gob.mx/files/YYYY/MM/filename.pdf``.

    Data is available from 2010 to the present.
    """

    BASE = "http://periodicooficial.oaxaca.gob.mx"
    LIST_URL = "http://periodicooficial.oaxaca.gob.mx/busquedadoc.php"

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(
                follow_redirects=True,
                timeout=60,
                verify=False,
            )
        else:
            self._client = client

    # --------------------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------------------

    def obtener_ediciones(
        self,
        tipo: Optional[str] = None,
        mes: Optional[int] = None,
        ano: Optional[int] = None,
    ) -> List[OaxacaPoEdicion]:
        """Fetch Periódico Oficial editions with optional filters.

        Args:
            tipo: One of "Ordinario", "Extraordinario", "Secciones".
                  If None (default), returns all three types combined.
            mes:  Month number 1–12.  Filtered client-side from the full list.
            ano:  4-digit year (e.g. 2025).  Filtered client-side from the full list.

        Returns:
            List of OaxacaPoEdicion sorted newest-first.
        """
        tipos = [tipo] if tipo else list(TODOS_LOS_TIPOS)
        ediciones: List[OaxacaPoEdicion] = []
        for t in tipos:
            ediciones.extend(self._fetch_tipo(t))

        # Client-side filter by year/month
        if ano:
            ediciones = [e for e in ediciones if str(ano) in e.fecha]
        if mes:
            # fecha is like "28/Feb/2026" — filter by month abbreviation or position
            mes_abbrs = {
                1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
                5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
                9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
            }
            abbr = mes_abbrs.get(mes, "")
            ediciones = [e for e in ediciones if f"/{abbr}/" in e.fecha]

        # Sort newest-first by normalising date to YYYY-MM-DD
        ediciones.sort(key=lambda e: self._fecha_key(e.fecha), reverse=True)
        return ediciones

    def buscar(self, texto: str) -> List[OaxacaPoEdicion]:
        """Search editions by filename (case-insensitive substring match).

        Args:
            texto: Keyword to search in the filename.

        Returns:
            List of matching OaxacaPoEdicion.
        """
        todas = self.obtener_ediciones()
        texto_lower = texto.lower()
        return [e for e in todas if texto_lower in e.nombre.lower()]

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def _fetch_tipo(self, tipo: str) -> List[OaxacaPoEdicion]:
        """Fetch all editions of one type."""
        r = self._client.get(f"{self.LIST_URL}?type={tipo}")
        r.raise_for_status()
        return self._parse_list(r.text, tipo)

    def _parse_list(self, html: str, tipo: str) -> List[OaxacaPoEdicion]:
        """Parse the busquedadoc page for a given type."""
        soup = BeautifulSoup(html, "html.parser")
        ediciones: List[OaxacaPoEdicion] = []

        # Find table rows with date + PDF link
        # The table has two columns: Fecha and Documento (PDF link)
        for row in soup.select("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            fecha_text = cells[0].get_text(strip=True)
            pdf_link = cells[1].find("a", href=lambda h: h and ".pdf" in h.lower())
            if not pdf_link or not fecha_text:
                continue
            # Skip header rows
            if fecha_text in ("Fecha", "Documento"):
                continue

            href = pdf_link.get("href", "")
            nombre = pdf_link.get_text(strip=True)
            # Build absolute URL: href is like ./files/YYYY/MM/filename.pdf
            url_pdf = href.replace("./", self.BASE + "/")
            if not url_pdf.startswith("http"):
                url_pdf = self.BASE + "/" + href.lstrip("./")

            ediciones.append(
                OaxacaPoEdicion(
                    tipo=tipo,
                    fecha=fecha_text,
                    nombre=nombre,
                    url_pdf=url_pdf,
                )
            )

        return ediciones

    @staticmethod
    def _fecha_key(fecha: str) -> str:
        """Convert 'DD/Mon/YYYY' to 'YYYY-MM-DD' for sorting."""
        try:
            parts = fecha.split("/")
            if len(parts) == 3:
                dia, mes_abbr, ano = parts
                mes_num = _MES_MAP.get(mes_abbr.lower()[:3], "00")
                return f"{ano}-{mes_num}-{dia.zfill(2)}"
        except Exception:
            pass
        return fecha
