import httpx
from typing import List, Optional
from .models import ZacatecasPoPublicacion

class ZacatecasPoClient:
    """Cliente para interactuar con la API del Periódico Oficial del Estado de Zacatecas (POEZ)."""
    
    BASE_URL = "https://periodico.zacatecas.gob.mx"
    
    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "verify": False,  # Frecuentes problemas SSL en sitios gubernamentales
            **kwargs,
        }

    def _parsear_lista(self, json_data: dict) -> List[ZacatecasPoPublicacion]:
        """Convierte la respuesta JSON en una lista de modelos Pydantic."""
        docs = json_data.get("Documentos", [])
        return [ZacatecasPoPublicacion.model_validate(doc) for doc in docs]

    def _post_request(self, endpoint: str, data: dict) -> List[ZacatecasPoPublicacion]:
        """Ejecuta una petición POST (application/x-www-form-urlencoded)."""
        url = f"{self.BASE_URL}{endpoint}"
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.post(url, data=data)
            resp.raise_for_status()
            return self._parsear_lista(resp.json())

    def _get_request(self, endpoint: str) -> List[ZacatecasPoPublicacion]:
        """Ejecuta una petición GET."""
        url = f"{self.BASE_URL}{endpoint}"
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return self._parsear_lista(resp.json())

    async def _a_post_request(self, endpoint: str, data: dict) -> List[ZacatecasPoPublicacion]:
        """Versión asíncrona de _post_request."""
        url = f"{self.BASE_URL}{endpoint}"
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.post(url, data=data)
            resp.raise_for_status()
            return self._parsear_lista(resp.json())

    async def _a_get_request(self, endpoint: str) -> List[ZacatecasPoPublicacion]:
        """Versión asíncrona de _get_request."""
        url = f"{self.BASE_URL}{endpoint}"
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return self._parsear_lista(resp.json())

    # --- Métodos Públicos Síncronos ---
    
    def obtener_ediciones(self, fecha_inicial: str, fecha_final: str) -> List[ZacatecasPoPublicacion]:
        """Obtiene periódicos ordinarios en un rango de fechas (YYYY-MM-DD)."""
        data = {"fechaInicial": fecha_inicial, "fechaFinal": fecha_final}
        return self._post_request("/busqueda/periodicoMesAnio", data)

    def buscar_suplementos(self, titulo: Optional[str] = None) -> List[ZacatecasPoPublicacion]:
        """Obtiene los suplementos. Filtra por título si se proporciona."""
        if titulo:
            return self._post_request("/busqueda/suplementos", {"titulo": titulo})
        return self._get_request("/obtener/suplementos")

    def buscar_leyes(self, descripcion: Optional[str] = None) -> List[ZacatecasPoPublicacion]:
        """Obtiene las leyes. Filtra por descripción si se proporciona."""
        if descripcion:
            return self._post_request("/busqueda/leyes", {"descripcion": descripcion})
        return self._get_request("/obtener/leyes")

    def obtener_reglamentos(self) -> List[ZacatecasPoPublicacion]:
        """Obtiene el listado de reglamentos estatales."""
        return self._get_request("/obtener/reglamentosestatales")

    def obtener_codigos(self) -> List[ZacatecasPoPublicacion]:
        """Obtiene el listado de códigos del estado."""
        return self._get_request("/obtener/codigos")

    # --- Métodos Públicos Asíncronos ---
    
    async def a_obtener_ediciones(self, fecha_inicial: str, fecha_final: str) -> List[ZacatecasPoPublicacion]:
        data = {"fechaInicial": fecha_inicial, "fechaFinal": fecha_final}
        return await self._a_post_request("/busqueda/periodicoMesAnio", data)

    async def a_buscar_suplementos(self, titulo: Optional[str] = None) -> List[ZacatecasPoPublicacion]:
        if titulo:
            return await self._a_post_request("/busqueda/suplementos", {"titulo": titulo})
        return await self._a_get_request("/obtener/suplementos")

    async def a_buscar_leyes(self, descripcion: Optional[str] = None) -> List[ZacatecasPoPublicacion]:
        if descripcion:
            return await self._a_post_request("/busqueda/leyes", {"descripcion": descripcion})
        return await self._a_get_request("/obtener/leyes")

    async def a_obtener_reglamentos(self) -> List[ZacatecasPoPublicacion]:
        return await self._a_get_request("/obtener/reglamentosestatales")

    async def a_obtener_codigos(self) -> List[ZacatecasPoPublicacion]:
        return await self._a_get_request("/obtener/codigos")
