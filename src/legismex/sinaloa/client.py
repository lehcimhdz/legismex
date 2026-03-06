import httpx
import asyncio
from typing import List, Optional

from .models import (
    SinaloaIniciativa,
    SinaloaDictamen,
    SinaloaAcuerdo,
    SinaloaDecreto,
    SinaloaLegislatura,
)

_API_BASE = "https://gaceta.congresosinaloa.gob.mx/api"
_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://gaceta.congresosinaloa.gob.mx",
    "Referer": "https://gaceta.congresosinaloa.gob.mx/",
}

# Número romano → número arábigo para identificar legislaturas
# Las legislaturas van de la 60 (LX) a la 65 (LXV)
LEGISLATURA_ACTUAL = "65"


class SinaloaClient:
    """Cliente para extraer actividad legislativa del H. Congreso del Estado de Sinaloa.

    Consume la API REST en ``gaceta.congresosinaloa.gob.mx/api``, que devuelve
    colecciones completas de la legislatura indicada en una sola petición
    (el filtrado y la paginación son del lado del cliente).

    Datos disponibles por legislatura (LX–LXV, números 60–65):
    - **Iniciativas**: por tipo (individual, conjunto, grupo).
    - **Dictámenes**
    - **Acuerdos**
    - **Decretos**

    Ejemplo síncrono::

        from legismex import SinaloaClient

        client = SinaloaClient()

        # Iniciativas de la legislatura actual (LXV = 65)
        iniciativas = client.obtener_iniciativas()
        print(f"Total: {len(iniciativas)}")
        for ini in iniciativas[:3]:
            print(ini.id, ini.presentada, ini.iniciativa[:60])

        # Dictámenes de otra legislatura
        dictamenes = client.obtener_dictamenes(legislatura="64")
        print(dictamenes[0].asunto)

    Ejemplo asíncrono::

        import asyncio
        from legismex import SinaloaClient

        async def main():
            client = SinaloaClient()
            decretos = await client.a_obtener_decretos()
            acuerdos = await client.a_obtener_acuerdos()
            print(f"Decretos: {len(decretos)} | Acuerdos: {len(acuerdos)}")

        asyncio.run(main())
    """

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "follow_redirects": True,
            "verify": False,  # Certificado SSL del servidor gubernamental es inválido
            **kwargs,
        }

    def _body(self, legislatura: str) -> dict:
        return {"nu_legislatura": str(legislatura)}

    # ------------------------------------------------------------------
    # API síncrona
    # ------------------------------------------------------------------

    def obtener_legislaturas(self) -> List[SinaloaLegislatura]:
        """Devuelve las legislaturas disponibles (LX–LXV)."""
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.post(
                f"{_API_BASE}/obtenerLegislaturas",
                json={},
                headers=_HEADERS,
            )
            resp.raise_for_status()
            return [SinaloaLegislatura(**item) for item in resp.json()]

    def obtener_iniciativas(self, legislatura: str = LEGISLATURA_ACTUAL) -> List[SinaloaIniciativa]:
        """Obtiene todas las iniciativas de la legislatura indicada.

        La API devuelve 3 grupos (individual, conjunto, grupo). Este método
        los combina en una sola lista plana ordenada por ID.

        Args:
            legislatura: Número de legislatura como cadena (ej. ``"65"`` para LXV).
        """
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.post(
                f"{_API_BASE}/obtenerIniciativas",
                json=self._body(legislatura),
                headers=_HEADERS,
            )
            resp.raise_for_status()
            data = resp.json()
            resultados: List[SinaloaIniciativa] = []
            for key in ("individual", "conjunto", "grupo"):
                for item in data.get(key, []):
                    resultados.append(SinaloaIniciativa(**item))
            return sorted(resultados, key=lambda x: x.id)

    def obtener_dictamenes(self, legislatura: str = LEGISLATURA_ACTUAL) -> List[SinaloaDictamen]:
        """Obtiene todos los dictámenes de la legislatura indicada."""
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.post(
                f"{_API_BASE}/obtenerDictamenes",
                json=self._body(legislatura),
                headers=_HEADERS,
            )
            resp.raise_for_status()
            return [SinaloaDictamen(**item) for item in resp.json()]

    def obtener_acuerdos(self, legislatura: str = LEGISLATURA_ACTUAL) -> List[SinaloaAcuerdo]:
        """Obtiene todos los acuerdos de la legislatura indicada."""
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.post(
                f"{_API_BASE}/obtenerAcuerdos",
                json=self._body(legislatura),
                headers=_HEADERS,
            )
            resp.raise_for_status()
            return [SinaloaAcuerdo(**item) for item in resp.json()]

    def obtener_decretos(self, legislatura: str = LEGISLATURA_ACTUAL) -> List[SinaloaDecreto]:
        """Obtiene todos los decretos de la legislatura indicada."""
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.post(
                f"{_API_BASE}/obtenerDecretos",
                json=self._body(legislatura),
                headers=_HEADERS,
            )
            resp.raise_for_status()
            return [SinaloaDecreto(**item) for item in resp.json()]

    # ------------------------------------------------------------------
    # API asíncrona
    # ------------------------------------------------------------------

    async def a_obtener_legislaturas(self) -> List[SinaloaLegislatura]:
        """Versión asíncrona de :meth:`obtener_legislaturas`."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.post(
                f"{_API_BASE}/obtenerLegislaturas",
                json={},
                headers=_HEADERS,
            )
            resp.raise_for_status()
            return [SinaloaLegislatura(**item) for item in resp.json()]

    async def a_obtener_iniciativas(self, legislatura: str = LEGISLATURA_ACTUAL) -> List[SinaloaIniciativa]:
        """Versión asíncrona de :meth:`obtener_iniciativas`."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.post(
                f"{_API_BASE}/obtenerIniciativas",
                json=self._body(legislatura),
                headers=_HEADERS,
            )
            resp.raise_for_status()
            data = resp.json()
            resultados: List[SinaloaIniciativa] = []
            for key in ("individual", "conjunto", "grupo"):
                for item in data.get(key, []):
                    resultados.append(SinaloaIniciativa(**item))
            return sorted(resultados, key=lambda x: x.id)

    async def a_obtener_dictamenes(self, legislatura: str = LEGISLATURA_ACTUAL) -> List[SinaloaDictamen]:
        """Versión asíncrona de :meth:`obtener_dictamenes`."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.post(
                f"{_API_BASE}/obtenerDictamenes",
                json=self._body(legislatura),
                headers=_HEADERS,
            )
            resp.raise_for_status()
            return [SinaloaDictamen(**item) for item in resp.json()]

    async def a_obtener_acuerdos(self, legislatura: str = LEGISLATURA_ACTUAL) -> List[SinaloaAcuerdo]:
        """Versión asíncrona de :meth:`obtener_acuerdos`."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.post(
                f"{_API_BASE}/obtenerAcuerdos",
                json=self._body(legislatura),
                headers=_HEADERS,
            )
            resp.raise_for_status()
            return [SinaloaAcuerdo(**item) for item in resp.json()]

    async def a_obtener_decretos(self, legislatura: str = LEGISLATURA_ACTUAL) -> List[SinaloaDecreto]:
        """Versión asíncrona de :meth:`obtener_decretos`."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.post(
                f"{_API_BASE}/obtenerDecretos",
                json=self._body(legislatura),
                headers=_HEADERS,
            )
            resp.raise_for_status()
            return [SinaloaDecreto(**item) for item in resp.json()]
