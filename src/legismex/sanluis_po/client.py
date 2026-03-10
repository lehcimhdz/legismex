import httpx
from datetime import date
from typing import List, Optional

from .models import SanLuisPoDocumento, SanLuisPoEdicion


class SanLuisPoClient:
    """Cliente para el Periódico Oficial del Estado de San Luis Potosí.

    El sitio web moderno (desarrollado con VueJS) consume directamente 
    endpoints JSON que dividen las publicaciones del día en niveles de 
    gobierno y avisos generales.

    Este cliente agrupa esas peticiones en una sola entidad.
    """

    BASE_URL = "https://periodicooficial.slp.gob.mx"
    ENDPOINT_DISPOSICIONES = "/api/publicacion/{fecha}/gt"
    ENDPOINT_AVISOS = "/api/publicacion/aviso/{fecha}/gt"

    def __init__(self, timeout: float = 30.0, client: Optional[httpx.Client] = None):
        self._timeout = timeout
        self._external_client = client

        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
        }

    def _get(self, url: str) -> dict:
        """Helper para hacer peticiones GET a los endpoints JSON."""
        if self._external_client is not None:
            response = self._external_client.get(url)
        else:
            with httpx.Client(
                timeout=self._timeout,
                headers=self._headers,
                verify=False,
                follow_redirects=True,
            ) as client:
                response = client.get(url)

        response.raise_for_status()
        return response.json()

    def obtener_edicion_por_fecha(self, fecha: str) -> SanLuisPoEdicion:
        """Obtiene la edición completa del POE para una fecha específica.

        El cliente realizará dos peticiones a la API del portal para 
        juntar las disposiciones oficiales y los avisos judiciales en 
        un solo listado de documentos.

        Args:
            fecha: Cadena en formato ISO ``YYYY-MM-DD``.

        Returns:
            Instancia de :class:`SanLuisPoEdicion` que encapsula la lista 
            de :class:`SanLuisPoDocumento`. Si no hay publicaciones ese 
            día, la lista vendrá vacía.
        """
        documentos: List[SanLuisPoDocumento] = []

        # 1. Petición de Disposiciones Oficiales
        url_disp = f"{self.BASE_URL}{self.ENDPOINT_DISPOSICIONES.format(fecha=fecha)}"
        data_disp = self._get(url_disp)

        if data_disp.get("success"):
            for nivel in ["nivel1", "nivel2", "nivel3"]:
                items = data_disp.get(nivel, [])
                for item in items:
                    # Validar IDs vacíos/fantasmas (a veces retornan nulls o strings)
                    if not item.get("id"):
                        continue

                    doc = SanLuisPoDocumento.model_validate(
                        {**item, "es_aviso": False})
                    documentos.append(doc)

        # 2. Petición de Avisos Judiciales
        url_aviso = f"{self.BASE_URL}{self.ENDPOINT_AVISOS.format(fecha=fecha)}"
        try:
            data_aviso = self._get(url_aviso)
            if data_aviso.get("success"):
                items = data_aviso.get("publicacionesAv", [])
                for item in items:
                    if not item.get("id"):
                        continue

                    doc = SanLuisPoDocumento.model_validate(
                        {**item, "es_aviso": True})
                    documentos.append(doc)
        except Exception:
            # Los avisos podrían fallar (ej. timeout de db o HTTP ratelimiting),
            # pero no deberíamos crashear la extracción completa
            pass

        return SanLuisPoEdicion(fecha=fecha, documentos=documentos)

    def obtener_edicion_del_dia(self) -> SanLuisPoEdicion:
        """Descarga la edición del día en curso (Hoy)."""
        fecha_hoy = date.today().isoformat()
        return self.obtener_edicion_por_fecha(fecha_hoy)
