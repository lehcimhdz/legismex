import httpx
from typing import List, Optional
from .models import VeracruzSesion
from .parser import VeracruzParser


class VeracruzClient:
    """Cliente para interactuar con la Gaceta Legislativa del Congreso 
    del Estado de Veracruz de Ignacio de la Llave.
    """

    BASE_URL = "https://www.legisver.gob.mx/Inicio.php?p=sesiones"

    def __init__(self, timeout: float = 30.0, client: Optional[httpx.Client] = None):
        self._timeout = timeout
        self._external_client = client

        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        self._parser = VeracruzParser()

    def _get(self, url: str) -> str:
        """Realiza una petición HTTP GET."""
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
        return response.text

    def obtener_gacetas(self) -> List[VeracruzSesion]:
        """Obtiene el histórico completo de gacetas parlamentarias, incluyendo
        sus anexos, actas, audios, videos y versiones estenográficas.

        Returns:
            Una lista de instancias :class:`VeracruzSesion` completamente 
            pobladas con sus documentos hijos subyacentes.
        """
        html = self._get(self.BASE_URL)
        return self._parser.parse_sesiones(html)
