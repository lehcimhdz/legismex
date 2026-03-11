import httpx
import asyncio
from typing import List, Optional
from datetime import date

from .models import SinaloaPoEdicion

_API_BASE = "https://strc.transparenciasinaloa.gob.mx/wp-json/tribe/events/v1/events"
_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "legismex/1.0",
}


class SinaloaPoClient:
    """Cliente para el Periódico Oficial del Estado de Sinaloa (POES).

    El sitio ``strc.transparenciasinaloa.gob.mx/poes/`` usa WordPress con
    *The Events Calendar* plugin. Cada edición del POE se registra como un
    evento con fecha, número, índice de contenido y un PDF descargable.

    Parámetros disponibles:
    - ``start_date`` / ``end_date``: rango de fechas (``'YYYY-MM-DD'``).
    - ``all_pages``: si es ``True`` descarga todas las páginas automáticamente.

    Ejemplo síncrono::

        from legismex import SinaloaPoClient

        client = SinaloaPoClient()

        # Ediciones del primer trimestre de 2026
        ediciones = client.buscar(start_date="2026-01-01", end_date="2026-03-31")
        print(f"Total: {len(ediciones)}")
        for e in ediciones[:3]:
            print(f"  {e.fecha} | {e.titulo} | PDF: {e.pdf_url}")

        # Edición única de hoy (si hay)
        hoy = client.buscar(start_date="2026-03-06", end_date="2026-03-06")

    Ejemplo asíncrono::

        import asyncio
        from legismex import SinaloaPoClient

        async def main():
            client = SinaloaPoClient()
            ediciones = await client.a_buscar(
                start_date="2025-01-01",
                end_date="2025-12-31",
                all_pages=True,
            )
            print(f"Año 2025: {len(ediciones)} ediciones")

        asyncio.run(main())
    """

    _PER_PAGE = 50

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "verify": False,
            "follow_redirects": True,
            **kwargs,
        }

    def _params(
        self,
        start_date: Optional[str],
        end_date: Optional[str],
        page: int,
    ) -> dict:
        params: dict = {
            "per_page": self._PER_PAGE,
            "page": page,
            "status": "publish",
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return params

    # ------------------------------------------------------------------
    # API síncrona
    # ------------------------------------------------------------------

    def buscar(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        all_pages: bool = True,
    ) -> List[SinaloaPoEdicion]:
        """Busca ediciones del POES en el rango de fechas indicado.

        Args:
            start_date: Fecha de inicio (``'YYYY-MM-DD'``). Por defecto no filtra.
            end_date: Fecha de fin (``'YYYY-MM-DD'``). Por defecto no filtra.
            all_pages: Si es ``True`` (por defecto) descarga todas las páginas.
        """
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(_API_BASE, params=self._params(
                start_date, end_date, 1), headers=_HEADERS)
            resp.raise_for_status()
            data = resp.json()
            total_pages = int(data.get("total_pages", 1))
            events = data.get("events", [])
            resultados = [SinaloaPoEdicion.from_api(e) for e in events]

            if all_pages and total_pages > 1:
                for page in range(2, total_pages + 1):
                    resp = client.get(_API_BASE, params=self._params(
                        start_date, end_date, page), headers=_HEADERS)
                    resp.raise_for_status()
                    blk = resp.json()
                    resultados.extend(SinaloaPoEdicion.from_api(e)
                                      for e in blk.get("events", []))

        return sorted(resultados, key=lambda e: e.fecha)

    def buscar_anio(self, anio: int, all_pages: bool = True) -> List[SinaloaPoEdicion]:
        """Devuelve todas las ediciones de un año completo.

        Args:
            anio: Año de 4 dígitos, ej. ``2025``.
        """
        return self.buscar(
            start_date=f"{anio}-01-01",
            end_date=f"{anio}-12-31",
            all_pages=all_pages,
        )

    def buscar_mes(self, anio: int, mes: int) -> List[SinaloaPoEdicion]:
        """Devuelve todas las ediciones de un mes específico.

        Args:
            anio: Año de 4 dígitos.
            mes: Mes (1–12).
        """
        from calendar import monthrange
        ultimo_dia = monthrange(anio, mes)[1]
        return self.buscar(
            start_date=f"{anio}-{mes:02d}-01",
            end_date=f"{anio}-{mes:02d}-{ultimo_dia}",
        )

    # ------------------------------------------------------------------
    # API asíncrona
    # ------------------------------------------------------------------

    async def a_buscar(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        all_pages: bool = True,
    ) -> List[SinaloaPoEdicion]:
        """Versión asíncrona de :meth:`buscar`."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(_API_BASE, params=self._params(start_date, end_date, 1), headers=_HEADERS)
            resp.raise_for_status()
            data = resp.json()
            total_pages = int(data.get("total_pages", 1))
            events = data.get("events", [])
            resultados = [SinaloaPoEdicion.from_api(e) for e in events]

            if all_pages and total_pages > 1:
                tareas = [
                    client.get(_API_BASE, params=self._params(
                        start_date, end_date, pg), headers=_HEADERS)
                    for pg in range(2, total_pages + 1)
                ]
                respuestas = await asyncio.gather(*tareas)
                for resp in respuestas:
                    resp.raise_for_status()
                    blk = resp.json()
                    resultados.extend(SinaloaPoEdicion.from_api(e)
                                      for e in blk.get("events", []))

        return sorted(resultados, key=lambda e: e.fecha)

    async def a_buscar_anio(self, anio: int, all_pages: bool = True) -> List[SinaloaPoEdicion]:
        """Versión asíncrona de :meth:`buscar_anio`."""
        return await self.a_buscar(
            start_date=f"{anio}-01-01",
            end_date=f"{anio}-12-31",
            all_pages=all_pages,
        )

    async def a_buscar_mes(self, anio: int, mes: int) -> List[SinaloaPoEdicion]:
        """Versión asíncrona de :meth:`buscar_mes`."""
        from calendar import monthrange
        ultimo_dia = monthrange(anio, mes)[1]
        return await self.a_buscar(
            start_date=f"{anio}-{mes:02d}-01",
            end_date=f"{anio}-{mes:02d}-{ultimo_dia}",
        )
