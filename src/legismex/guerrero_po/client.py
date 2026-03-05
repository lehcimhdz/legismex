import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from .models import GuerreroPoPublicacion


class GuerreroPoClient:
    """Client for the Periódico Oficial del Estado de Guerrero.

    Scrapes the WordPress site at ``periodicooficial.guerrero.gob.mx``
    to list gazette publications with optional filters by keyword,
    year, month, day, and category.
    """

    BASE_URL = "https://periodicooficial.guerrero.gob.mx"
    PUB_URL = f"{BASE_URL}/publicaciones/"

    # Category ID → name mapping (from the site's <select>)
    CATEGORIAS = {
        15: "ACTAS", 14: "ACUERDOS", 9002: "ANEXO", 16: "AVISOS",
        17: "BANDOS", 31: "CIRCULARES", 9005: "CODIGOS", 18: "CONVENIOS",
        19: "CONVOCATORIAS", 20: "DECLARATORIAS", 30: "DECRETOS DE EXPROPIACION",
        21: "DECRETOS DEL EJECUTIVO", 22: "DECRETOS DEL LEGISLATIVO",
        8135: "DECRETOS MUNICIPALES", 8104: "DICTAMEN", 23: "EDICTOS",
        24: "FE DE ERRATAS", 9000: "INFORMES", 25: "LEYES",
        9001: "LINEAMIENTOS", 9007: "LISTA", 9006: "MANUAL",
        8011: "NORMAS", 9003: "PRESUPUESTO", 2723: "PROGRAMAS",
        9004: "PROTOCOLO", 26: "REGLAMENTOS", 8110: "RELACIÓN",
        28: "RESOLUCIONES", 29: "SENTENCIAS",
    }

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(follow_redirects=True, timeout=30)
        else:
            self._client = client

    def obtener_publicaciones(
        self,
        pagina: int = 1,
        buscar: Optional[str] = None,
        anio: Optional[int] = None,
        mes: Optional[int] = None,
        dia: Optional[int] = None,
        categoria: Optional[int] = None,
    ) -> List[GuerreroPoPublicacion]:
        """Fetch gazette publications with optional filters and pagination.

        Args:
            pagina: 1-based page number (50 results per page).
            buscar: Free-text keyword search.
            anio: Year filter (1987–2026).
            mes: Month filter (1–12).
            dia: Day filter (1–31).
            categoria: Category ID (use CATEGORIAS keys).

        Returns:
            List of GuerreroPoPublicacion for the requested page.
        """
        params: dict = {}
        if buscar:
            params["buscar"] = buscar
        if anio:
            params["sy"] = str(anio)
        if mes:
            params["sm"] = str(mes)
        if dia:
            params["sd"] = str(dia)
        if categoria:
            params["cat"] = str(categoria)

        if pagina > 1:
            url = f"{self.PUB_URL}page/{pagina}/"
        else:
            url = self.PUB_URL

        r = self._client.get(url, params=params)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        results: List[GuerreroPoPublicacion] = []
        for card in soup.select(".card"):
            title_el = card.select_one(".card-title")
            titulo = title_el.get_text(strip=True) if title_el else ""

            date_el = card.select_one("cite")
            fecha = date_el.get_text(strip=True) if date_el else ""

            cat_el = card.select_one(".card-subtitle a")
            cat_name = cat_el.get_text(strip=True) if cat_el else ""

            pdf_el = card.select_one('a[href$=".pdf"]')
            url_pdf = pdf_el["href"] if pdf_el else None

            detail_links = card.select("a.card-link")
            url_detalle = None
            for a in detail_links:
                href = a.get("href", "")
                if href and ".pdf" not in href:
                    url_detalle = href
                    break

            results.append(
                GuerreroPoPublicacion(
                    titulo=titulo,
                    fecha=fecha,
                    categoria=cat_name,
                    url_pdf=url_pdf,
                    url_detalle=url_detalle,
                )
            )

        return results
