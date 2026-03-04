import httpx
from typing import Optional
from typing import List, Dict

from legismex.senado.models import GacetaSenado
from legismex.senado.parser import SenadoParser


class SenadoClient:
    """
    Cliente oficial para la extracción de publicaciones y documentos
    del Senado de la República (www.senado.gob.mx).
    """

    BASE_URL = "https://www.senado.gob.mx"
    # User-Agent estandar tipo navegador moderno para evadir bloqueos básicos
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }

    def __init__(self, timeout: float = 15.0, headers: Optional[Dict] = None):
        """
        Inicializa el cliente de extracción del Senado.

        :param timeout: Tiempo máximo de espera en segundos para la conexión HTTP.
        :param headers: Cabeceras personalizadas HTTP opcionales.
        """
        self.timeout = timeout
        self.headers = headers or self.DEFAULT_HEADERS
        # Importante: El Senado tiene SSL bien configurado, pero verify=False es
        # por si hubiera un proxy o certificado auto-firmado a futuro
        self._verify_ssl = False

    def obtener_gaceta_del_dia(self, legislatura: str = "66") -> GacetaSenado:
        """
        Obtiene la última gaceta del día publicada por el Senado, con
        las categorías e iniciativas presentadas en la sesión.

        :param legislatura: Opcional. Indica la legislatura, por defecto la '66'.
        :return: Objeto GacetaSenado validado por Pydantic.
        """
        url = f"{self.BASE_URL}/{legislatura}/gaceta_del_senado"

        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers, verify=self._verify_ssl, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()

                html_content = response.text
                return SenadoParser.parse_gaceta_dia(html_content)

        except httpx.HTTPStatusError as exc:
            raise Exception(f"HTTP error {exc.response.status_code} - al consultar la Gaceta del Senado: {url}")
        except httpx.RequestError as exc:
            raise Exception(f"Error de red al conectar con el servidor del Senado: {exc}")
