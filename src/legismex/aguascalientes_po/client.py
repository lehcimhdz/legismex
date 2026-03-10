import httpx
from typing import List, Optional, Iterator
from .models import AgsPoEdicion, AgsPoPublicacionCalendario


class AguascalientesPoClient:
    """Client for the Periódico Oficial del Estado de Aguascalientes.

    The site at ``eservicios2.aguascalientes.gob.mx/periodicooficial`` is an
    ASP.NET WebForms application with PageMethods (ASMX) JSON endpoints.

    Endpoints used:
    - ``default.aspx/obtenerInformacion`` — paginated search (500 items/page)
    - ``default.aspx/edicionesCalendario`` — all publication dates (5,458 entries)
    - PDF files at ``Archivos/{IdPeriodico}.pdf``

    Total archive: ~8,991 editions covering editions from the 1990s through
    the present (Ordinario, Extraordinario, Vespertina).

    Filters available:
    - ``fecha_inicio`` / ``fecha_fin``: date range as ``MM/dd/yyyy`` (e.g. 12/31/2024)
    - ``edicion_id``: 0=All, 1=ORDINARIO, 2=EXTRAORDINARIO, 3=VESPERTINA
    - ``seccion_id``: 0=All, 1-10=Secciones 1ª–10ª, 52=Vespertina,
      53-107=Further seccions, 58=Extraordinario
    - ``orden_gobierno_id``: e.g. 1=PODER LEGISLATIVO, 2=PODER EJECUTIVO, 3=PODER JUDICIAL
    - ``tipo_publicacion_id``: doc type (1=DECRETO, 2=REGLAMENTO, ...)
    - ``nombre_documento``: keyword in document name
    - ``contenido``: keyword in document content (OCR)
    """

    BASE = "https://eservicios2.aguascalientes.gob.mx/periodicooficial"
    PAGE_SIZE = 500

    EDICIONES = {
        0: "Sin asignar",
        1: "ORDINARIO",
        2: "EXTRAORDINARIO",
        3: "VESPERTINA",
    }

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(
                follow_redirects=True,
                timeout=60,
            )
        else:
            self._client = client

        self._asmx_headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-Requested-With": "XMLHttpRequest",
        }

    # --------------------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------------------

    def obtener_ediciones(
        self,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        edicion_id: int = 0,
        seccion_id: int = 0,
        orden_gobierno_id: Optional[int] = None,
        tipo_publicacion_id: Optional[str] = None,
        nombre_documento: Optional[str] = None,
        contenido: Optional[str] = None,
        pagina: int = 1,
    ) -> dict:
        """Fetch one page (500 items) of Periódico Oficial editions.

        Args:
            fecha_inicio:       Start date in ``MM/dd/yyyy`` format. E.g. ``"12/31/2025"``.
            fecha_fin:          End date in ``MM/dd/yyyy`` format. E.g. ``"12/31/2025"``.
            edicion_id:         0=All, 1=ORDINARIO, 2=EXTRAORDINARIO, 3=VESPERTINA.
            seccion_id:         0=All; 1–10 for Secciones 1ª–10ª.
            orden_gobierno_id:  Issuing authority ID. None=All.
            tipo_publicacion_id: Document type ID. None=All.
            nombre_documento:   Keyword in document name.
            contenido:          Keyword in document content (OCR text).
            pagina:             1-based page number (500 items per page).

        Returns:
            dict with keys:
                - ``items``: list of AgsPoEdicion
                - ``total``: total matching records
                - ``pagina``: current page
                - ``paginas``: total pages
        """
        indice_actual = (pagina - 1) * self.PAGE_SIZE + 1

        # El sitio espera fechas con formato "dd/MM/yyyy 0:0:0"
        def format_date(d: Optional[str]) -> str:
            if not d:
                return ""
            if " " not in d:
                return f"{d} 0:0:0"
            return d

        payload = {
            "fipub": format_date(fecha_inicio),
            "ffpub": format_date(fecha_fin),
            "actualIndice": None,
            "IdOrdenGobierno": str(orden_gobierno_id) if orden_gobierno_id else "",
            "IdDependencia": None,
            "numero": "",
            "IdEdicion": str(edicion_id or 0),
            "IdTipoPublicacion": str(tipo_publicacion_id or ""),
            "NombreDocumento": nombre_documento or "",
            "IdTomo": "",
            "IdSeccion": str(seccion_id or 0),
            "Contenido": contenido or "",
            "indiceActual": indice_actual,
        }

        raw = self._call("obtenerInformacion", payload)
        if not raw:
            return {"items": [], "total": 0, "pagina": pagina, "paginas": 0}

        total = raw[0].get("Total", 0)
        paginas = (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE
        items = [self._parse_edicion(d) for d in raw]

        return {
            "items": items,
            "total": total,
            "pagina": pagina,
            "paginas": paginas,
        }

    def listar_todas(
        self,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        edicion_id: int = 0,
        seccion_id: int = 0,
        orden_gobierno_id: Optional[int] = None,
        tipo_publicacion_id: Optional[str] = None,
        nombre_documento: Optional[str] = None,
        contenido: Optional[str] = None,
    ) -> List[AgsPoEdicion]:
        """Fetch ALL editions matching the filters (handles pagination automatically).

        Warning: with no filters this fetches all ~8,991 records across ~18
        pages of 500 items each, making 18 HTTP requests. Apply filters to
        reduce the scope.

        Returns:
            List of all ``AgsPoEdicion`` matching the filters.
        """
        all_items: List[AgsPoEdicion] = []
        pagina = 1

        while True:
            result = self.obtener_ediciones(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                edicion_id=edicion_id,
                seccion_id=seccion_id,
                orden_gobierno_id=orden_gobierno_id,
                tipo_publicacion_id=tipo_publicacion_id,
                nombre_documento=nombre_documento,
                contenido=contenido,
                pagina=pagina,
            )
            all_items.extend(result["items"])
            if pagina >= result["paginas"] or not result["items"]:
                break
            pagina += 1

        return all_items

    def calendario(self) -> List[AgsPoPublicacionCalendario]:
        """Return all publication dates in the archive (5,458+ entries).

        Each entry shows which edition types were published on a given date
        and how many sections. Useful for building a date index.

        Returns:
            List of ``AgsPoPublicacionCalendario`` sorted by date.
        """
        raw = self._call("edicionesCalendario", {})
        if not raw:
            return []
        return [
            AgsPoPublicacionCalendario(
                fecha_publicacion=d.get("fechapublicacion", ""),
                ediciones=d.get("ediciones", ""),
                num_secciones=d.get("fechas", 0),
            )
            for d in raw
        ]

    def url_pdf(self, id_periodico: int) -> str:
        """Build the PDF URL for a given IdPeriodico.

        Args:
            id_periodico: The ``id`` field from ``AgsPoEdicion``.

        Returns:
            Full URL to the PDF on ``eservicios2.aguascalientes.gob.mx``.
        """
        return f"{self.BASE}/Archivos/{id_periodico}.pdf"

    # --------------------------------------------------------------------------
    # Internal helpers
    # --------------------------------------------------------------------------

    def _call(self, method: str, payload: dict):
        """Call an ASP.NET PageMethod and return the parsed JSON 'd' value."""
        import json
        r = self._client.post(
            f"{self.BASE}/default.aspx/{method}",
            headers=self._asmx_headers,
            content=json.dumps(payload),
        )
        r.raise_for_status()
        d = r.json().get("d", "")
        if not d:
            return None
        return json.loads(d)

    def _parse_edicion(self, d: dict) -> AgsPoEdicion:
        """Convert raw API dict to AgsPoEdicion."""
        id_ = d.get("IdPeriodico") or d.get("idPeriodico", 0)
        return AgsPoEdicion(
            id=id_,
            fecha_publicacion=d.get("FechaPublicacion", ""),
            fecha_captura=d.get("FechaCaptura"),
            numero=d.get("Numero"),
            tomo=d.get("Tomo"),
            edicion=d.get("Edicion"),
            seccion=d.get("Seccion"),
            contenido=d.get("Contenido"),
            dependencias=d.get("Dependencias"),
            url_pdf=self.url_pdf(id_),
        )
