import httpx
from typing import List, Optional, Iterator
from .models import AgsPromocion, AgsComision


# Map legislature display name → internal ID
LEGISLATURAS = {
    "LXIV": 64,
    "LXV": 65,
    "LXVI": 66,
}

# All promotion types with their IDs
TIPOS_PROMOCION = {
    1:  "ACUERDO LEGISLATIVO",
    2:  "CUENTA PÚBLICA",
    3:  "INICIATIVA",
    4:  "MINUTA",
    5:  "NOMBRAMIENTO",
    6:  "PUNTO DE ACUERDO",
    7:  "SOLICITUD",
    9:  "DECRETO",
    10: "DICTÁMEN",
    11: "VERSIONES ESTENOGRÁFICAS",
    12: "ACTAS",
    13: "DIARIO DE DEBATES",
    14: "GACETA PARLAMENTARIA",
}


class AguascalientesClient:
    """Client for the Agenda Legislativa of the Congreso de Aguascalientes.

    The site at ``congresoags.gob.mx`` exposes a server-side DataTables API
    at ``/LegislativeAgenda/GetPagedData`` that serves all 14 promotion types
    for the LXIV (64), LXV (65), and LXVI (66) legislatures through
    the same endpoint.

    PDFs are downloaded via ``/LegislativeAgenda/Download?id={id}``.
    """

    BASE = "https://congresoags.gob.mx"
    API_URL = "https://congresoags.gob.mx/LegislativeAgenda/GetPagedData"

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(
                follow_redirects=True,
                timeout=60,
            )
        else:
            self._client = client

    # --------------------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------------------

    def obtener_promociones(
        self,
        legislatura: str = "LXVI",
        tipo_promocion_id: Optional[int] = None,
        busqueda: Optional[str] = None,
        pagina: int = 1,
        tamaño_pagina: int = 100,
    ) -> dict:
        """Fetch one page of legislative promotions.

        Args:
            legislatura:       "LXIV", "LXV", or "LXVI".
            tipo_promocion_id: Filter by type (1-14). See TIPOS_PROMOCION or
                               use the category name constants.
                               If None, returns all types.
            busqueda:          Keyword search term.
            pagina:            1-based page number.
            tamaño_pagina:     Records per page (default 100, max 9999 for all).

        Returns:
            dict with keys:
                 - ``items``: list of AgsPromocion
                 - ``total``: total matching records
                 - ``pagina``: current page
                 - ``paginas``: total pages
        """
        leg_id = LEGISLATURAS.get(legislatura, 66)
        params: dict = {
            "legislatureId": leg_id,
            "page": pagina,
            "pageSize": tamaño_pagina,
        }
        if tipo_promocion_id:
            params["promotionTypeId"] = tipo_promocion_id
        if busqueda:
            params["searchTerm"] = busqueda

        r = self._client.get(self.API_URL, params=params)
        r.raise_for_status()
        raw = r.json()

        items = [self._parse_item(d) for d in raw.get("data", [])]
        total = raw.get("recordsTotal", 0)
        paginas = (total + tamaño_pagina - 1) // tamaño_pagina

        return {
            "items": items,
            "total": total,
            "pagina": pagina,
            "paginas": paginas,
        }

    def listar_todas(
        self,
        legislatura: str = "LXVI",
        tipo_promocion_id: Optional[int] = None,
        busqueda: Optional[str] = None,
    ) -> List[AgsPromocion]:
        """Fetch ALL promotions (handles pagination automatically).

        Warning: fetches all records in one large request using pageSize=9999.
        This is the most efficient approach given the API supports it.

        Args:
            legislatura:       "LXIV", "LXV", or "LXVI".
            tipo_promocion_id: Optional type filter.
            busqueda:          Optional keyword search.

        Returns:
            List of all AgsPromocion matching the filters.
        """
        result = self.obtener_promociones(
            legislatura=legislatura,
            tipo_promocion_id=tipo_promocion_id,
            busqueda=busqueda,
            pagina=1,
            tamaño_pagina=9999,
        )
        return result["items"]

    def url_pdf(self, item_id: int) -> str:
        """Build the PDF download URL for a given promotion ID.

        Args:
            item_id: The ``id`` field from AgsPromocion.

        Returns:
            Full URL to the PDF on ``congresoags.gob.mx``.
        """
        return f"{self.BASE}/LegislativeAgenda/Download?id={item_id}"

    # --------------------------------------------------------------------------
    # Parsing
    # --------------------------------------------------------------------------

    def _parse_item(self, d: dict) -> AgsPromocion:
        """Convert raw API dict to AgsPromocion."""
        file_path = d.get("filePath") or None
        has_file = bool(file_path and file_path.strip())
        item_id = d.get("id", 0)

        comisiones = []
        for c in d.get("commissions", []):
            comisiones.append(
                AgsComision(
                    id=c.get("id", 0),
                    orden=c.get("order", 0),
                    descripcion=c.get("description", ""),
                    es_organo_legislativo=c.get("legislativeOrgan", False),
                )
            )

        return AgsPromocion(
            id=item_id,
            numero_agenda=d.get("agendaNumber", ""),
            tipo_promocion=d.get("promotionType", ""),
            tipo_promocion_id=d.get("promotionTypeID", 0),
            legislatura_id=d.get("legislatureID", 66),
            contenido=d.get("content", ""),
            comisiones=comisiones,
            fecha_presentacion=d.get("presentationDate"),
            fecha_turno=d.get("turnDate"),
            resolucion=d.get("resolution"),
            resolucion_id=d.get("resolutionID"),
            tipo_sesion=d.get("sessionType"),
            tipo_sesion_id=d.get("sessionTypeID"),
            sesion_ordinaria=d.get("ordinarySession"),
            tiene_archivo=has_file,
            url_pdf=self.url_pdf(item_id) if has_file else None,
            nombre_archivo=file_path,
            activo=d.get("isActive", True),
        )
