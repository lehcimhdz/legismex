import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Optional
from .models import OaxacaGaceta, OaxacaDocumento


class OaxacaClient:
    """Client for the Gaceta Parlamentaria of the Congreso de Oaxaca (LXVI Legislatura).

    The index is at ``congresooaxaca.gob.mx/parlaments.html`` listing all gacetas,
    each with a detail page at ``/parlamento/{id}.html``.  Documents are stored
    at ``docs66.congresooaxaca.gob.mx/gaceta/{fecha}/{N}.pdf``.
    """

    BASE = "https://www.congresooaxaca.gob.mx"
    INDEX_URL = "https://www.congresooaxaca.gob.mx/parlaments.html"

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(
                follow_redirects=True,
                timeout=30,
                verify=False,   # site has mixed/legacy SSL
            )
        else:
            self._client = client

    # --------------------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------------------

    def listar_gacetas(self) -> List[OaxacaGaceta]:
        """Fetch the index and return all gacetas (without documents).

        Returns:
            List of OaxacaGaceta ordered newest-first (as presented on the site).
        """
        r = self._client.get(self.INDEX_URL)
        r.raise_for_status()
        return self._parse_index(r.text)

    def obtener_gaceta(self, id: int) -> OaxacaGaceta:
        """Fetch a specific gaceta with all its documents.

        Args:
            id: The sequential gaceta number (e.g. 179).

        Returns:
            OaxacaGaceta with ``documentos`` populated.
        """
        detail_url = f"{self.BASE}/parlamento/{id}.html"
        r = self._client.get(detail_url)
        r.raise_for_status()
        gaceta = self._parse_detail(r.text, detail_url, id)
        return gaceta

    def obtener_todas(self, con_documentos: bool = False) -> List[OaxacaGaceta]:
        """Fetch the full list and optionally load documents for each.

        Args:
            con_documentos: If True, fetches each detail page (slow but complete).

        Returns:
            List of OaxacaGaceta objects.
        """
        gacetas = self.listar_gacetas()
        if con_documentos:
            result = []
            for g in gacetas:
                result.append(self.obtener_gaceta(g.id))
            return result
        return gacetas

    # --------------------------------------------------------------------------
    # Parsing helpers
    # --------------------------------------------------------------------------

    def _parse_index(self, html: str) -> List[OaxacaGaceta]:
        """Parse the index page into a list of OaxacaGaceta (no documents)."""
        soup = BeautifulSoup(html, "html.parser")
        gacetas: List[OaxacaGaceta] = []

        # Each gaceta entry: title like "GP-179 Sesión Ordinaria\n03-03-2026\nCONSULTAR"
        # The CONSULTAR links go to parlamento/{id}.html
        consultar_links = [
            a for a in soup.find_all("a")
            if "parlamento/" in a.get("href", "")
        ]

        for a in consultar_links:
            href = a.get("href", "")
            # Derive id from link: parlamento/{id}.html
            try:
                gaceta_id = int(href.split("parlamento/")[1].replace(".html", ""))
            except (IndexError, ValueError):
                continue

            detail_url = urljoin(self.BASE + "/", href)

            # Walk up to find the card container  
            container = a.parent
            for _ in range(5):
                if container is None:
                    break
                text = container.get_text(separator="\n", strip=True)
                if "GP-" in text:
                    break
                container = container.parent

            if container is None:
                continue

            lines = [l.strip() for l in container.get_text(separator="\n").split("\n") if l.strip()]
            # Extract number, tipo, fecha from the lines
            numero = ""
            tipo = ""
            fecha = ""
            for line in lines:
                if line.startswith("GP-"):
                    # "GP-179 Sesión Ordinaria"
                    parts = line.split(" ", 1)
                    numero = parts[0]
                    tipo = parts[1] if len(parts) > 1 else ""
                elif len(line) == 10 and line[2] == "-" and line[5] == "-":
                    # DD-MM-YYYY
                    fecha = line

            gacetas.append(
                OaxacaGaceta(
                    id=gaceta_id,
                    numero=numero,
                    tipo=tipo,
                    fecha=fecha,
                    url_detalle=detail_url,
                )
            )

        return gacetas

    def _parse_detail(self, html: str, page_url: str, gaceta_id: int) -> OaxacaGaceta:
        """Parse a detail page to get the gaceta header and all documents."""
        soup = BeautifulSoup(html, "html.parser")

        # Extract header info from title area (same layout as index card)
        all_text_lines = [
            l.strip() for l in soup.get_text(separator="\n").split("\n")
            if l.strip()
        ]
        numero = ""
        tipo = ""
        fecha = ""
        for line in all_text_lines:
            if line.startswith("GP-"):
                parts = line.split(" ", 1)
                numero = parts[0]
                tipo = parts[1] if len(parts) > 1 else ""
            elif len(line) == 10 and line[2] == "-" and line[5] == "-":
                fecha = line
            if numero and fecha:
                break

        # Parse documents: each is a .list-group-item with number + description + pdf links
        documentos: List[OaxacaDocumento] = []
        items = soup.select(".list-group-item")
        for item in items:
            # Number is in a span (or standalone text node); description follows
            badge = item.select_one("span.badge") or item.select_one("span")
            numero_doc = badge.get_text(strip=True) if badge else ""

            # Description: text of the item excluding badge and link text
            desc_parts = []
            for node in item.descendants:
                if node.name is None:  # text node
                    t = node.strip()
                    if t and t not in ("Documento",):
                        desc_parts.append(t)
            descripcion = " ".join(desc_parts).strip()

            # PDF links: hrefs look like ../../docs66.congresooaxaca.gob.mx/gaceta/N.pdf
            # urljoin from /parlamento/NNN.html resolves them to
            # https://www.congresooaxaca.gob.mx/docs66.congresooaxaca.gob.mx/...
            # We detect this pattern and rewrite to the correct absolute URL.
            pdf_urls = []
            for a in item.select("a"):
                href = a.get("href", "")
                if ".pdf" not in href.lower():
                    continue
                if href.startswith("../../docs66."):
                    # direct rewrite: strip leading ../../
                    resolved = "https://" + href[6:]
                else:
                    resolved = urljoin(page_url, href)
                    # fallback: fix bogus www.congresooaxaca…/docs66… paths
                    resolved = resolved.replace(
                        "https://www.congresooaxaca.gob.mx/docs66.",
                        "https://docs66."
                    )
                pdf_urls.append(resolved)

            if numero_doc or pdf_urls:
                documentos.append(
                    OaxacaDocumento(
                        numero=numero_doc,
                        descripcion=descripcion,
                        url_pdfs=pdf_urls,
                    )
                )

        return OaxacaGaceta(
            id=gaceta_id,
            numero=numero,
            tipo=tipo,
            fecha=fecha,
            url_detalle=page_url,
            documentos=documentos,
        )
