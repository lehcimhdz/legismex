from typing import List
import asyncio
import httpx
from bs4 import BeautifulSoup
from .models import TamaulipasGaceta


class TamaulipasClient:
    """Cliente para la Gaceta Parlamentaria del H. Congreso del Estado de Tamaulipas."""

    BASE_URL = "https://www.congresotamaulipas.gob.mx/TrabajoLegislativo/GacetasParlamentarias/GacetasParlamentarias.asp"
    DOMAIN = "https://www.congresotamaulipas.gob.mx"

    def __init__(self, **kwargs):
        """
        Inicializa el cliente de Tamaulipas.

        Args:
            **kwargs: Argumentos adicionales para pasar a httpx.Client o AsyncClient,
                como timeouts, proxies, verificación SSL, etc.
        """
        self.client_kwargs = {
            "verify": False,  # Ignorar validación SSL
            **kwargs
        }

    def _parse(self, html: str, legislatura: int | str) -> List[TamaulipasGaceta]:
        """
        Analiza el HTML de la página de Gacetas de Tamaulipas y extrae los registros.

        Args:
            html (str): Contenido HTML de la página.
            legislatura (int | str): Número de legislatura para asignar a los modelos.

        Returns:
            List[TamaulipasGaceta]: Lista de modelos de las gacetas encontradas.
        """
        soup = BeautifulSoup(html, "html.parser")
        gacetas: List[TamaulipasGaceta] = []

        table = soup.find("table", class_="table")
        if not table:
            return gacetas

        # Omitir el primer tr (sus encabezados)
        rows = table.find_all("tr")[1:]

        for row in rows:
            tds = row.find_all("td")
            # Debe tener 7 columnas según la estructura HTML identificada
            if len(tds) >= 7:
                # Extraer url primero
                a_tag = tds[6].find("a", href=True)
                if not a_tag:
                    continue  # Si no hay link al PDF, la omitimos o podríamos guardarla sin link

                url_path = a_tag["href"]
                # A veces el href ya viene escapado, otras veces tiene espacios
                # Httpx maneja los urls si están bien formados, pero los espacios pueden dar lata
                url_pdf = f"{self.DOMAIN}{url_path}"
                # codificar los espacios simple
                url_pdf = url_pdf.replace(" ", "%20")

                try:
                    gaceta = TamaulipasGaceta(
                        legislatura=legislatura,
                        publicado_el=tds[0].text.strip(),
                        numero=tds[1].text.strip(),
                        tomo=tds[2].text.strip(),
                        fecha_gaceta=tds[3].text.strip(),
                        fecha_sesion=tds[4].text.strip(),
                        sesion=tds[5].text.strip(),
                        url_pdf=url_pdf
                    )
                    gacetas.append(gaceta)
                except Exception as e:
                    # Ignoramos filas anómalas
                    print(f"Error parseando fila de Tamaulipas: {e}")
                    pass

        return gacetas

    def obtener_gacetas(self, legislatura: int | str = 66) -> List[TamaulipasGaceta]:
        """
        Obtiene de forma síncrona el listado de gacetas parlamentarias de una legislatura.

        Args:
            legislatura (int | str): Número de la legislatura a consultar.

        Returns:
            List[TamaulipasGaceta]: Lista de gacetas correspondientes.
        """
        params = {"Legislatura": str(legislatura)}
        with httpx.Client(**self.client_kwargs) as client:
            response = client.get(
                self.BASE_URL, params=params, follow_redirects=True)
            response.raise_for_status()
            html = response.text

        return self._parse(html, legislatura)

    async def a_obtener_gacetas(self, legislatura: int | str = 66) -> List[TamaulipasGaceta]:
        """
        Obtiene de forma asíncrona el listado de gacetas parlamentarias de una legislatura.

        Args:
            legislatura (int | str): Número de la legislatura a consultar.

        Returns:
            List[TamaulipasGaceta]: Lista de gacetas correspondientes.
        """
        params = {"Legislatura": str(legislatura)}
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            response = await client.get(self.BASE_URL, params=params, follow_redirects=True)
            response.raise_for_status()
            html = response.text

        # Si el parsing fuera bloqueante por gran cantidad de datos,
        # podríamos utilizar asyncio.to_thread() pero BeautifulSoup es rápido.
        return self._parse(html, legislatura)
