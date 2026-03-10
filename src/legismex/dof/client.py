import httpx
from typing import Optional, Dict
from datetime import datetime

from legismex.dof.models import DofEdicion
from legismex.dof.parser import DofParser


class DofClient:
    """
    Cliente oficial para la extracción de publicaciones y documentos
    del Diario Oficial de la Federación (dof.gob.mx).
    """

    BASE_URL = "https://www.dof.gob.mx"

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }

    def __init__(self, timeout: float = 15.0, headers: Optional[Dict] = None):
        """
        Inicializa el cliente de extracción del DOF.

        :param timeout: Tiempo máximo de espera en segundos para la conexión HTTP.
        :param headers: Cabeceras personalizadas HTTP opcionales.
        """
        self.timeout = timeout
        self.headers = headers or self.DEFAULT_HEADERS
        # Importante: Algunos sitios gubernamentales tienen configuraciones SSL variables.
        self._verify_ssl = False

    def obtener_edicion_del_dia(self, date_label: str = "Hoy") -> DofEdicion:
        """
        Obtiene el concentrado principal del DOF publicado en el día actual.

        :param date_label: Etiqueta textual opcional para fechar la extracción.
        :return: Objeto DofEdicion validado por Pydantic.
        """
        url = f"{self.BASE_URL}/index.php"

        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers, verify=self._verify_ssl, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()

                html_content = response.text
                return DofParser.parse_edicion_dia(html_content, fecha_edicion=date_label)

        except httpx.HTTPStatusError as exc:
            raise Exception(
                f"HTTP error {exc.response.status_code} - al consultar el DOF: {url}")
        except httpx.RequestError as exc:
            raise Exception(
                f"Error de red al conectar con el servidor del DOF: {exc}")
