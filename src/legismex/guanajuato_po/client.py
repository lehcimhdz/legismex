import httpx
from typing import List, Optional
from .models import GuanajuatoPoEdicion


class GuanajuatoPoClient:
    """Client for the Periódico Oficial del Estado de Guanajuato.

    Uses the public REST API at backperiodico.guanajuato.gob.mx to search
    and retrieve official gazette publications with direct PDF download links.
    """

    BASE_URL = "https://backperiodico.guanajuato.gob.mx/api"

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(verify=False)
        else:
            self._client = client

    def _build_search_url(
        self,
        keyword: Optional[str] = None,
        anio: Optional[str] = None,
        numero: Optional[str] = None,
        tipo: Optional[str] = None,
        fecha: Optional[str] = None,
        page_size: int = 10,
        page: int = 1,
    ) -> str:
        kw = keyword or "null"
        a = anio or "null"
        n = numero or "null"
        t = tipo or "null"
        f = fecha or "null"
        return (
            f"{self.BASE_URL}/Periodico/BusquedaPeriodicoPublicacion"
            f"/{kw}/{a}/{n}/{t}/{f}/{page_size}/{page}"
        )

    @staticmethod
    def _parse_items(items: list) -> List[GuanajuatoPoEdicion]:
        results: List[GuanajuatoPoEdicion] = []
        for item in items:
            results.append(
                GuanajuatoPoEdicion(
                    perid=item["perid"],
                    fecha=item["perfecha"],
                    anio=item["peranio"],
                    numero=item["pernumero"],
                    parte=item["perparte"],
                    descripcion=item["perdescripcion"],
                    url_pdf=item.get("perurl", ""),
                    inciso=item.get("perinciso"),
                    total_sumarios=item.get("totsumarios", 0),
                )
            )
        return results

    def buscar(
        self,
        keyword: Optional[str] = None,
        anio: Optional[str] = None,
        numero: Optional[str] = None,
        tipo: Optional[str] = None,
        fecha: Optional[str] = None,
        page_size: int = 10,
        page: int = 1,
    ) -> List[GuanajuatoPoEdicion]:
        """Search for publications with optional filters.

        Args:
            keyword: Free-text search term.
            anio: Year filter (e.g. "2026").
            numero: Issue number filter.
            tipo: Type filter.
            fecha: Date filter.
            page_size: Desired page size (server may not honor exactly).
            page: Page number (1-indexed).

        Returns:
            List of GuanajuatoPoEdicion matching the criteria.
        """
        url = self._build_search_url(keyword, anio, numero, tipo, fecha, page_size, page)
        response = self._client.get(url)
        response.raise_for_status()
        data = response.json()
        return self._parse_items(data.get("objeto", []))

    def obtener_ultimo_ejemplar(self) -> List[GuanajuatoPoEdicion]:
        """Get the latest published issue(s) of the Periódico Oficial."""
        url = f"{self.BASE_URL}/Periodico/UltimoEjemplar"
        response = self._client.get(url)
        response.raise_for_status()
        data = response.json()
        return self._parse_items(data.get("objeto", []))
