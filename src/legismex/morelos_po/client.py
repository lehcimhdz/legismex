import re
import httpx
from typing import List, Optional
from .models import MorelosPoEjemplar


class MorelosPoClient:
    """Client for the Periódico Oficial del Estado de Morelos (Tierra y Libertad).

    Queries the Laravel/DataTables server-side API at
    ``periodico.morelos.gob.mx`` to list and paginate gazette issues
    (ejemplares) from 1970 to the present, with optional year, month,
    and sumario keyword filters.
    """

    BASE_URL = "https://periodico.morelos.gob.mx"
    DT_ENDPOINT = f"{BASE_URL}/ejemplaresFiltradosPublicoGeneral"

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(follow_redirects=True, timeout=30)
        else:
            self._client = client
        self._csrf: Optional[str] = None

    def _ensure_csrf(self) -> str:
        """Fetch a page to obtain a CSRF token for the Laravel backend."""
        if self._csrf is None:
            r = self._client.get(f"{self.BASE_URL}/ejemplares")
            r.raise_for_status()
            m = re.search(r'csrf-token.*?content="(.*?)"', r.text)
            if not m:
                raise RuntimeError("No se pudo obtener el token CSRF")
            self._csrf = m.group(1)
        return self._csrf

    @staticmethod
    def _strip_html(html: str) -> str:
        """Remove HTML tags from a sumario string."""
        return re.sub(r"<[^>]+>", "", html).strip()

    def obtener_ejemplares(
        self,
        anio: Optional[int] = None,
        mes: Optional[int] = None,
        buscar_sumario: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> tuple[List[MorelosPoEjemplar], int]:
        """Fetch gazette issues with optional filters and pagination.

        Args:
            anio: Year to filter by (1970-2026). None = all years.
            mes: Month (1-12). None = all months.
            buscar_sumario: Free-text keyword search on the sumario.
            page: 1-based page number.
            page_size: Results per page (max 100).

        Returns:
            A tuple of (list of MorelosPoEjemplar, total_records).
        """
        csrf = self._ensure_csrf()
        start = (page - 1) * page_size

        payload = {
            "draw": page,
            "start": start,
            "length": page_size,
            "columns[0][data]": "",
            "columns[1][data]": "nomPublicacion",
            "columns[2][data]": "edicion",
            "columns[3][data]": "fechaPublicacion",
            "columns[4][data]": "URL",
            "order[0][column]": 3,
            "order[0][dir]": "desc",
            "search[value]": "",
            "anios": str(anio) if anio else "%",
            "mes": f"{mes:02d}" if mes else "%",
            "buscarSumario": buscar_sumario or "",
        }

        r = self._client.post(
            self.DT_ENDPOINT,
            headers={"X-CSRF-TOKEN": csrf},
            data=payload,
        )

        if r.status_code == 419:
            # CSRF expired — refresh and retry once
            self._csrf = None
            csrf = self._ensure_csrf()
            r = self._client.post(
                self.DT_ENDPOINT,
                headers={"X-CSRF-TOKEN": csrf},
                data=payload,
            )

        r.raise_for_status()
        body = r.json()

        total = body.get("recordsFiltered", 0)
        items: List[MorelosPoEjemplar] = []

        for row in body.get("data", []):
            edicion_raw = row.get("edicion", "")
            edicion_map = {
                "ORDINARIA": "Ordinaria",
                "EXTRAORDINARIA": "Extraordinaria",
                "ALCANCE": "Alcance",
            }
            edicion = edicion_map.get(edicion_raw, edicion_raw)

            url_path = row.get("URL", "")
            url_pdf = f"{self.BASE_URL}/descargarPDF{url_path}"

            sumario_html = row.get("sumario", "")
            sumario = self._strip_html(sumario_html) if sumario_html else None

            items.append(
                MorelosPoEjemplar(
                    numero=row.get("nomPublicacion", ""),
                    edicion=edicion,
                    fecha_publicacion=row.get("fechaPublicacion", ""),
                    url_pdf=url_pdf,
                    sumario=sumario,
                )
            )

        return items, total
