"""Cliente para la Gaceta Parlamentaria del H. Congreso del Estado de Sonora.

API base: ``https://gestion.api.congresoson.gob.mx/publico/``
"""
import httpx
import asyncio
from typing import List, Optional

from .models import SonoraGaceta, SonoraLegislatura

_API_BASE = "https://gestion.api.congresoson.gob.mx/publico"
_HEADERS = {
    "Accept": "application/json",
    "Origin": "https://congresoson.gob.mx",
    "Referer": "https://congresoson.gob.mx/",
    "User-Agent": "legismex/1.0",
}

# UUIDs de las 7 legislaturas conocidas, del más reciente al más antiguo
LEGISLATURAS: dict[str, str] = {
    "LXIV":  "7c1013d2-f2ac-49ad-9ce0-03a8b23e2ec5",  # Sep 2024 - Sep 2027
    "LXIII": "460dff6b-6fe6-4ea0-9871-10a6f49e8950",  # Sep 2021 - Sep 2024
    "LXII":  "fa348258-b031-4b5b-839a-1669e1ed7fb4",  # Sep 2018 - Sep 2021
    "LXI":   "e1c94bc0-e391-4cad-8bd7-d25d508c5bfb",  # Sep 2015 - Sep 2018
    "LX":    "e230c092-193d-4791-8595-0841cfd38aa8",  # Sep 2012 - Sep 2015
    "LIX":   "55117bb3-08bc-4de3-8910-2d110adf662d",  # Sep 2009 - Sep 2012
    "LVIII": "529b383a-39b9-469e-a443-2bde258acc53",  # Sep 2006 - Sep 2009
}


class SonoraClient:
    """Cliente para la Gaceta Parlamentaria del H. Congreso del Estado de Sonora.

    El portal ``congresoson.gob.mx/gacetas`` usa una SPA en Astro/React cuya
    data proviene de ``gestion.api.congresoson.gob.mx/publico/``. La API no
    requiere autenticación y devuelve JSON con paginación.

    Legislaturas disponibles (atributo :attr:`LEGISLATURAS`):
    ``'LXIV'`` (2024-2027), ``'LXIII'`` (2021-2024), ``'LXII'``, ``'LXI'``,
    ``'LX'``, ``'LIX'``, ``'LVIII'``.

    Ejemplo síncrono::

        from legismex import SonoraClient

        client = SonoraClient()

        # Legislaturas disponibles
        legs = client.obtener_legislaturas()
        for l in legs:
            print(l.nombre, l.descripcion)

        # Gacetas de la legislatura actual (todas las páginas)
        gacetas = client.buscar(legislatura="LXIV")
        print(f"Total: {len(gacetas)}")
        for g in gacetas[:3]:
            print(g.nombre, g.tipo)

        # Buscar por palabra clave
        resultados = client.buscar(buscar="decreto", legislatura="LXIV")

        # Buscar por rango de fechas
        q1 = client.buscar(
            legislatura="LXIV",
            fecha_inicio="2026-01-01",
            fecha_fin="2026-03-31",
        )

        # Detalle de una gaceta (con PDF)
        detalle = client.obtener_detalle("378d8062-b937-4019-bbf2-0f6690f7e671")
        print(detalle.pdf_urls)

    Ejemplo asíncrono::

        import asyncio
        from legismex import SonoraClient

        async def main():
            client = SonoraClient()
            gacetas = await client.a_buscar(legislatura="LXIV")
            print(f"LXIV: {len(gacetas)} gacetas")

        asyncio.run(main())
    """

    _LIMITE = 50
    _EXPAND_LIST = "legislatura,legislaturaPeriodo"
    _EXPAND_DETAIL = "mediaGaceta.media,legislatura"

    def __init__(self, **kwargs):
        self.client_kwargs = {"timeout": 30.0, "follow_redirects": True, **kwargs}

    def _id_legislatura(self, legislatura: str) -> str:
        """Resuelve una clave legible (ej. 'LXIV') o un UUID directo."""
        if legislatura in LEGISLATURAS:
            return LEGISLATURAS[legislatura]
        return legislatura  # asume UUID directo

    def _list_params(
        self,
        id_leg: str,
        pagina: int,
        buscar: Optional[str],
        fecha_inicio: Optional[str],
        fecha_fin: Optional[str],
    ) -> dict:
        params: dict = {
            "idLegislatura": id_leg,
            "pagina": pagina,
            "limite": self._LIMITE,
            "ordenar": "fechaPublicacion-desc",
            "expand": self._EXPAND_LIST,
        }
        if buscar:
            params["buscar"] = buscar
        if fecha_inicio:
            params["fechaInicio"] = fecha_inicio
        if fecha_fin:
            params["fechaFin"] = fecha_fin
        return params

    # ------------------------------------------------------------------
    # API síncrona
    # ------------------------------------------------------------------

    def obtener_legislaturas(self) -> List[SonoraLegislatura]:
        """Devuelve la lista de legislaturas disponibles (de más reciente a más antigua)."""
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(
                f"{_API_BASE}/legislatura",
                params={"limite": 10, "ordenar": "periodoInicio-desc"},
                headers=_HEADERS,
            )
            resp.raise_for_status()
            return [SonoraLegislatura.from_api(r) for r in resp.json().get("resultado", [])]

    def buscar(
        self,
        legislatura: str = "LXIV",
        buscar: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        all_pages: bool = True,
    ) -> List[SonoraGaceta]:
        """Busca gacetas en una legislatura con filtros opcionales.

        Args:
            legislatura: Clave legible (``'LXIV'``) o UUID de la legislatura.
            buscar: Término de búsqueda en título de la gaceta.
            fecha_inicio: Fecha de inicio en ``'YYYY-MM-DD'``.
            fecha_fin: Fecha de fin en ``'YYYY-MM-DD'``.
            all_pages: Si ``True`` (por defecto), descarga todas las páginas.
        """
        id_leg = self._id_legislatura(legislatura)
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(
                f"{_API_BASE}/gaceta",
                params=self._list_params(id_leg, 1, buscar, fecha_inicio, fecha_fin),
                headers=_HEADERS,
            )
            resp.raise_for_status()
            data = resp.json()
            pag = data["paginacion"]
            total_pages = -(-pag["total"] // pag["limite"])  # ceil
            resultados = [SonoraGaceta.from_api(r) for r in data.get("resultado", [])]

            if all_pages and total_pages > 1:
                for page in range(2, total_pages + 1):
                    resp = client.get(
                        f"{_API_BASE}/gaceta",
                        params=self._list_params(id_leg, page, buscar, fecha_inicio, fecha_fin),
                        headers=_HEADERS,
                    )
                    resp.raise_for_status()
                    resultados.extend(
                        SonoraGaceta.from_api(r) for r in resp.json().get("resultado", [])
                    )
        return resultados

    def obtener_detalle(self, id_gaceta: str) -> SonoraGaceta:
        """Devuelve el detalle de una gaceta incluyendo los archivos PDF adjuntos.

        Args:
            id_gaceta: UUID de la gaceta (ej. ``'378d8062-...'``).
        """
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(
                f"{_API_BASE}/gaceta",
                params={"id": id_gaceta, "expand": self._EXPAND_DETAIL},
                headers=_HEADERS,
            )
            resp.raise_for_status()
            resultados = resp.json().get("resultado", [])
            if not resultados:
                raise ValueError(f"No se encontró la gaceta con id={id_gaceta}")
            return SonoraGaceta.from_api(resultados[0])

    # ------------------------------------------------------------------
    # API asíncrona
    # ------------------------------------------------------------------

    async def a_obtener_legislaturas(self) -> List[SonoraLegislatura]:
        """Versión asíncrona de :meth:`obtener_legislaturas`."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(
                f"{_API_BASE}/legislatura",
                params={"limite": 10, "ordenar": "periodoInicio-desc"},
                headers=_HEADERS,
            )
            resp.raise_for_status()
            return [SonoraLegislatura.from_api(r) for r in resp.json().get("resultado", [])]

    async def a_buscar(
        self,
        legislatura: str = "LXIV",
        buscar: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        all_pages: bool = True,
    ) -> List[SonoraGaceta]:
        """Versión asíncrona de :meth:`buscar`."""
        id_leg = self._id_legislatura(legislatura)
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(
                f"{_API_BASE}/gaceta",
                params=self._list_params(id_leg, 1, buscar, fecha_inicio, fecha_fin),
                headers=_HEADERS,
            )
            resp.raise_for_status()
            data = resp.json()
            pag = data["paginacion"]
            total_pages = -(-pag["total"] // pag["limite"])
            resultados = [SonoraGaceta.from_api(r) for r in data.get("resultado", [])]

            if all_pages and total_pages > 1:
                tareas = [
                    client.get(
                        f"{_API_BASE}/gaceta",
                        params=self._list_params(id_leg, pg, buscar, fecha_inicio, fecha_fin),
                        headers=_HEADERS,
                    )
                    for pg in range(2, total_pages + 1)
                ]
                respuestas = await asyncio.gather(*tareas)
                for r in respuestas:
                    r.raise_for_status()
                    resultados.extend(SonoraGaceta.from_api(x) for x in r.json().get("resultado", []))
        return resultados

    async def a_obtener_detalle(self, id_gaceta: str) -> SonoraGaceta:
        """Versión asíncrona de :meth:`obtener_detalle`."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(
                f"{_API_BASE}/gaceta",
                params={"id": id_gaceta, "expand": self._EXPAND_DETAIL},
                headers=_HEADERS,
            )
            resp.raise_for_status()
            resultados = resp.json().get("resultado", [])
            if not resultados:
                raise ValueError(f"No se encontró la gaceta con id={id_gaceta}")
            return SonoraGaceta.from_api(resultados[0])
