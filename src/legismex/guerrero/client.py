import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from .models import GuerreroGaceta, GuerreroDocumento


class GuerreroClient:
    """Client for the Gaceta Parlamentaria del Congreso de Guerrero
    (LXIV Legislatura).

    Scrapes the paginated list at ``sialgro.dcrsoft.com.mx/gacetaparlamentaria``
    and each gazette's detail page to extract session documents with their
    PDF links (hosted at ``congresogro.com/assets/``).
    """

    BASE_URL = "http://sialgro.dcrsoft.com.mx/gacetaparlamentaria"
    LIST_URL = f"{BASE_URL}/gazettes/"

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(follow_redirects=True, timeout=30)
        else:
            self._client = client

    def _fetch_soup(self, url: str) -> BeautifulSoup:
        r = self._client.get(url)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def obtener_gacetas(
        self,
        pagina: int = 1,
        limite: int = 20,
        buscar: Optional[str] = None,
        con_documentos: bool = False,
    ) -> tuple[List[GuerreroGaceta], int]:
        """Fetch the paginated list of gazettes.

        Args:
            pagina: 1-based page number.
            limite: Results per page (default 20, max ~100).
            buscar: Optional keyword search on gazette name.
            con_documentos: If True, also fetches each gazette's detail
                page to populate the ``documentos`` list.  This is slower
                because it makes one extra HTTP request per gazette.

        Returns:
            A tuple of (list of GuerreroGaceta, total_records).
        """
        params: dict = {"limit_start": pagina, "limit_count": limite}
        if buscar:
            url = f"{self.BASE_URL}/gazettes/List"
            params["search"] = buscar
        else:
            url = self.LIST_URL

        soup = self._fetch_soup(f"{url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")

        # Total records
        total_span = soup.select_one("span.total-records")
        total = int(total_span.get_text(strip=True)) if total_span else 0

        # Parse rows
        tbody = soup.select_one("tbody.page-data")
        gacetas: List[GuerreroGaceta] = []

        if tbody:
            for tr in tbody.find_all("tr"):
                cells = tr.find_all(["td", "th"])
                if len(cells) < 5:
                    continue

                # cells: [#, id, name, date, auth, btn]
                id_link = cells[1].find("a", href=True)
                gac_id = int(id_link.get_text(strip=True)) if id_link else 0
                url_detalle = id_link["href"] if id_link else ""
                nombre = cells[2].get_text(strip=True)
                fecha_span = cells[3].find("span")
                fecha = fecha_span.get_text(strip=True) if fecha_span else cells[3].get_text(strip=True)

                gaceta = GuerreroGaceta(
                    id=gac_id,
                    nombre=nombre,
                    fecha=fecha,
                    url_detalle=url_detalle,
                )

                if con_documentos:
                    gaceta.documentos = self._fetch_documentos(url_detalle)

                gacetas.append(gaceta)

        return gacetas, total

    # ------------------------------------------------------------------
    # Detail
    # ------------------------------------------------------------------

    def obtener_documentos(self, gaceta_id: int) -> List[GuerreroDocumento]:
        """Fetch all documents for a specific gazette by its ID.

        Args:
            gaceta_id: The numeric gazette identifier.

        Returns:
            List of GuerreroDocumento with tipo, descripción, and url_pdf.
        """
        url = f"{self.BASE_URL}/gazettes/view/{gaceta_id}"
        return self._fetch_documentos(url)

    def _fetch_documentos(self, url: str) -> List[GuerreroDocumento]:
        """Parse the documents table from a gazette detail page."""
        soup = self._fetch_soup(url)
        tables = soup.find_all("table")
        if len(tables) < 2:
            return []

        doc_table = tables[1]
        docs: List[GuerreroDocumento] = []

        for tr in doc_table.find_all("tr")[1:]:  # skip header
            cells = tr.find_all(["td", "th"])
            if len(cells) < 4:
                continue

            # cells: [#, Tipo, Descripción, Archivo(link), Contenido]
            tipo = cells[1].get_text(strip=True)
            descripcion = cells[2].get_text(strip=True)

            pdf_link = cells[3].find("a", href=True)
            if not pdf_link:
                continue
            url_pdf = pdf_link["href"]

            contenido = cells[4].get_text(strip=True) if len(cells) > 4 else None

            docs.append(
                GuerreroDocumento(
                    tipo=tipo,
                    descripcion=descripcion,
                    url_pdf=url_pdf,
                    contenido=contenido,
                )
            )

        return docs
