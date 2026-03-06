import httpx
import asyncio
from typing import List

from .models import NayaritIniciativa

# API interna del Congreso de Nayarit
_API_BASE = "https://utics.congresonayarit.gob.mx"
_TABLA_URL = f"{_API_BASE}/iniciativas/tabla/{{legislatura}}"

# Legislaturas disponibles (XXXIV es la más reciente)
LEGISLATURAS = ("XXXIV", "XXXIII", "XXXII", "XXXI", "XXX")


def _parse_item(item: dict) -> NayaritIniciativa:
    """Convierte un objeto JSON de la API en un NayaritIniciativa."""
    return NayaritIniciativa(
        numero=item["numero"],
        fecha_recepcion=item.get("fecha_recepcion") or "",
        origen=item.get("origen") or "",
        anio_legislatura=item.get("anio") or "",
        periodo=item.get("periodo") or "",
        descripcion=item.get("descripcion") or "",
        url_pdf=item.get("iniciativa") or None,
        fecha_pleno=item.get("fecha_pleno") or None,
        turno_comision=item.get("turno_a_comision") or None,
        dictamen=item.get("dictamen") or None,
        legislatura=item.get("legislatura") or None,
    )


class NayaritCongresoClient:
    """Cliente para extraer iniciativas legislativas del H. Congreso del Estado de Nayarit.

    Consume la API REST en ``utics.congresonayarit.gob.mx/iniciativas/tabla/{LEGISLATURA}``,
    que devuelve una lista JSON de todas las iniciativas de la legislatura indicada.

    Ejemplo síncrono::

        from legismex import NayaritCongresoClient

        client = NayaritCongresoClient()
        # XXXIV Legislatura (actual)
        iniciativas = client.obtener_iniciativas()
        # Legislatura anterior
        iniciativas = client.obtener_iniciativas("XXXIII")

        for ini in iniciativas:
            print(ini.numero, ini.descripcion[:80])

    Ejemplo asíncrono::

        import asyncio
        from legismex import NayaritCongresoClient

        async def main():
            client = NayaritCongresoClient()
            iniciativas = await client.a_obtener_iniciativas()
            for ini in iniciativas:
                print(ini.numero, ini.fecha_recepcion, ini.url_pdf)

        asyncio.run(main())

    Para obtener todas las legislaturas en paralelo::

        async def todas():
            client = NayaritCongresoClient()
            tareas = [client.a_obtener_iniciativas(leg) for leg in client.LEGISLATURAS]
            resultados = await asyncio.gather(*tareas)
            return resultados
    """

    LEGISLATURAS = LEGISLATURAS
    """Tupla con los números romanos de las legislaturas disponibles, de más reciente a más antigua."""

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "follow_redirects": True,
            **kwargs,
        }

    # ------------------------------------------------------------------
    # API síncrona
    # ------------------------------------------------------------------

    def obtener_iniciativas(self, legislatura: str = "XXXIV") -> List[NayaritIniciativa]:
        """Descarga y parsea las iniciativas de la legislatura indicada.

        Args:
            legislatura: Número romano de la legislatura. Valores válidos:
                ``"XXXIV"`` (default), ``"XXXIII"``, ``"XXXII"``, ``"XXXI"``, ``"XXX"``.

        Returns:
            Lista de :class:`NayaritIniciativa`.
        """
        url = _TABLA_URL.format(legislatura=legislatura.upper())
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return [_parse_item(item) for item in data]

    # ------------------------------------------------------------------
    # API asíncrona
    # ------------------------------------------------------------------

    async def a_obtener_iniciativas(self, legislatura: str = "XXXIV") -> List[NayaritIniciativa]:
        """Versión asíncrona de :meth:`obtener_iniciativas`.

        Args:
            legislatura: Número romano de la legislatura.

        Returns:
            Lista de :class:`NayaritIniciativa`.
        """
        url = _TABLA_URL.format(legislatura=legislatura.upper())
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return [_parse_item(item) for item in data]
