import httpx
import asyncio
from typing import List, Optional

from .models import NayaritPoPublicacion, NayaritPoResultado

_API_URL = "https://periodicooficial.nayarit.gob.mx/controllers/PublicacionesController.php"
_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}


def _parse_response(data: dict) -> NayaritPoResultado:
    """Convierte la respuesta JSON del servidor en un NayaritPoResultado."""
    publicaciones = [
        NayaritPoPublicacion(**item)
        for item in data.get("resultados", [])
    ]
    return NayaritPoResultado(
        publicaciones=publicaciones,
        total=data.get("total", 0),
        pagina=data.get("pagina", 1),
        resultados_por_pagina=data.get("resultadosPorPagina", 10),
    )


class NayaritPoClient:
    """Cliente para extraer publicaciones del Periódico Oficial del Estado de Nayarit.

    Fuente: https://periodicooficial.nayarit.gob.mx/publicaciones

    El portal usa un único endpoint PHP que acepta peticiones POST:
    ``POST /controllers/PublicacionesController.php``

    Tipos de búsqueda soportados:
    - **Por fecha**: busca una edición específica por fecha.
    - **Por palabra clave**: búsqueda de texto libre en el sumario/tipo.
    - **Avanzada**: combina palabra clave + rango de fechas.

    Todos los métodos soportan paginación automática (opción ``all_pages=True``).

    Ejemplo síncrono::

        from legismex import NayaritPoClient

        client = NayaritPoClient()

        # Publicaciones de una fecha específica
        pub = client.buscar_por_fecha("2026-03-05")
        print(f"Publicaciones: {pub.total}")
        for p in pub.publicaciones:
            print(p.tipo, p.sumario[:60], p.url_pdf)

        # Búsqueda por palabra con todas las páginas
        resultados = client.buscar_por_palabra("decreto", all_pages=True)

    Ejemplo asíncrono::

        import asyncio
        from legismex import NayaritPoClient

        async def main():
            client = NayaritPoClient()
            resultado = await client.a_buscar_por_fecha("2026-03-05")
            for pub in resultado.publicaciones:
                print(pub.numero, pub.tipo, pub.url_pdf)

        asyncio.run(main())
    """

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "verify": False,  # Certificado SSL del servidor gubernamental es inválido
            "follow_redirects": True,
            **kwargs,
        }

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _payload(self, tipo: str, datos: str, pagina: int) -> str:
        return f"tipo={tipo}&datos={datos}&pagina={pagina}"

    def _fetch_page(self, client: httpx.Client, tipo: str, datos: str, pagina: int) -> NayaritPoResultado:
        resp = client.post(
            _API_URL,
            content=self._payload(tipo, datos, pagina),
            headers=_HEADERS,
        )
        resp.raise_for_status()
        return _parse_response(resp.json())

    async def _a_fetch_page(self, client: httpx.AsyncClient, tipo: str, datos: str, pagina: int) -> NayaritPoResultado:
        resp = await client.post(
            _API_URL,
            content=self._payload(tipo, datos, pagina),
            headers=_HEADERS,
        )
        resp.raise_for_status()
        return _parse_response(resp.json())

    def _collect_all_pages(self, client: httpx.Client, tipo: str, datos: str) -> NayaritPoResultado:
        """Descarga todas las páginas y las consolida en un único NayaritPoResultado."""
        primera = self._fetch_page(client, tipo, datos, 1)
        todas = list(primera.publicaciones)
        for p in range(2, primera.total_paginas + 1):
            page = self._fetch_page(client, tipo, datos, p)
            todas.extend(page.publicaciones)
        primera.publicaciones = todas
        return primera

    async def _a_collect_all_pages(self, client: httpx.AsyncClient, tipo: str, datos: str) -> NayaritPoResultado:
        """Asíncrono: descarga todas las páginas en paralelo."""
        primera = await self._a_fetch_page(client, tipo, datos, 1)
        if primera.total_paginas <= 1:
            return primera

        tareas = [
            self._a_fetch_page(client, tipo, datos, p)
            for p in range(2, primera.total_paginas + 1)
        ]
        resto = await asyncio.gather(*tareas)
        todas = list(primera.publicaciones)
        for r in resto:
            todas.extend(r.publicaciones)
        primera.publicaciones = todas
        return primera

    # ------------------------------------------------------------------
    # API síncrona
    # ------------------------------------------------------------------

    def buscar_por_fecha(self, fecha: str, pagina: int = 1, all_pages: bool = False) -> NayaritPoResultado:
        """Busca publicaciones por fecha.

        Args:
            fecha: Fecha en formato ``YYYY-MM-DD``.
            pagina: Número de página (1-based). Ignorado si ``all_pages=True``.
            all_pages: Si es ``True``, descarga todas las páginas automáticamente.

        Returns:
            :class:`NayaritPoResultado` con la lista de publicaciones.
        """
        from urllib.parse import quote
        datos = f"fecha%3D{fecha}"
        with httpx.Client(**self.client_kwargs) as client:
            if all_pages:
                return self._collect_all_pages(client, "fecha", datos)
            return self._fetch_page(client, "fecha", datos, pagina)

    def buscar_por_palabra(self, palabra: str, pagina: int = 1, all_pages: bool = False) -> NayaritPoResultado:
        """Busca publicaciones por palabra clave en el sumario/tipo.

        Args:
            palabra: Texto a buscar.
            pagina: Número de página. Ignorado si ``all_pages=True``.
            all_pages: Si es ``True``, descarga todas las páginas automáticamente.
        """
        from urllib.parse import quote
        datos = f"palabra%3D{quote(palabra)}"
        with httpx.Client(**self.client_kwargs) as client:
            if all_pages:
                return self._collect_all_pages(client, "palabra", datos)
            return self._fetch_page(client, "palabra", datos, pagina)

    def buscar_avanzada(
        self,
        palabra: str,
        fecha_inicio: str,
        fecha_fin: str,
        pagina: int = 1,
        all_pages: bool = False,
    ) -> NayaritPoResultado:
        """Búsqueda avanzada: combina palabra clave con rango de fechas.

        Args:
            palabra: Texto a buscar.
            fecha_inicio: Fecha de inicio (``YYYY-MM-DD``).
            fecha_fin: Fecha de fin (``YYYY-MM-DD``).
            pagina: Número de página. Ignorado si ``all_pages=True``.
            all_pages: Si es ``True``, descarga todas las páginas.
        """
        from urllib.parse import quote
        datos = f"palabra%3D{quote(palabra)}%26fecha_inicio%3D{fecha_inicio}%26fecha_fin%3D{fecha_fin}"
        with httpx.Client(**self.client_kwargs) as client:
            if all_pages:
                return self._collect_all_pages(client, "palabra-fecha", datos)
            return self._fetch_page(client, "palabra-fecha", datos, pagina)

    # ------------------------------------------------------------------
    # API asíncrona
    # ------------------------------------------------------------------

    async def a_buscar_por_fecha(self, fecha: str, pagina: int = 1, all_pages: bool = False) -> NayaritPoResultado:
        """Versión asíncrona de :meth:`buscar_por_fecha`."""
        datos = f"fecha%3D{fecha}"
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            if all_pages:
                return await self._a_collect_all_pages(client, "fecha", datos)
            return await self._a_fetch_page(client, "fecha", datos, pagina)

    async def a_buscar_por_palabra(self, palabra: str, pagina: int = 1, all_pages: bool = False) -> NayaritPoResultado:
        """Versión asíncrona de :meth:`buscar_por_palabra`."""
        from urllib.parse import quote
        datos = f"palabra%3D{quote(palabra)}"
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            if all_pages:
                return await self._a_collect_all_pages(client, "palabra", datos)
            return await self._a_fetch_page(client, "palabra", datos, pagina)

    async def a_buscar_avanzada(
        self,
        palabra: str,
        fecha_inicio: str,
        fecha_fin: str,
        pagina: int = 1,
        all_pages: bool = False,
    ) -> NayaritPoResultado:
        """Versión asíncrona de :meth:`buscar_avanzada`."""
        from urllib.parse import quote
        datos = f"palabra%3D{quote(palabra)}%26fecha_inicio%3D{fecha_inicio}%26fecha_fin%3D{fecha_fin}"
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            if all_pages:
                return await self._a_collect_all_pages(client, "palabra-fecha", datos)
            return await self._a_fetch_page(client, "palabra-fecha", datos, pagina)
