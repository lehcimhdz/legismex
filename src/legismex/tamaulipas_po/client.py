import asyncio
from typing import List
import httpx
from bs4 import BeautifulSoup
from .models import TamaulipasPoEdicion, TamaulipasPoDocumento


class TamaulipasPoClient:
    """Cliente para interrogar las publicaciones del Periódico Oficial del Estado de Tamaulipas."""
    BASE_URL = "https://po.tamaulipas.gob.mx/archivo/"

    def __init__(self, **kwargs):
        """
        Inicializa el cliente de PO Tamaulipas.

        Args:
            **kwargs: Argumentos adicionales para httpx.Client o AsyncClient,
                como timeouts, verificación SSL, proxies, etc.
        """
        self.client_kwargs = {
            "verify": False,  # Ignorar validación SSL de .gob.mx si fuera necesario
            "timeout": 30.0,
            **kwargs
        }

    def _parsear_html(self, html: str, anio: int, mes: int) -> List[TamaulipasPoEdicion]:
        """
        Analiza el HTML del calendario devuelto por WordPress y reconstruye las ediciones.

        Args:
            html (str): Contenido de la página `/archivo/?mes=...&ano=...`
            anio (int): Año consultado, para reconstruir la fecha YYYY-MM-DD.
            mes (int): Mes consultado.

        Returns:
            List[TamaulipasPoEdicion]: Ediciones encontradas en ese mes.
        """
        soup = BeautifulSoup(html, "html.parser")
        ediciones: List[TamaulipasPoEdicion] = []

        days = soup.find_all("div", class_="day")
        for day_div in days:
            dia_div = day_div.find("div", class_="dia")
            if not dia_div:
                continue

            dia_text = dia_div.text.strip()
            if not dia_text.isdigit():
                continue

            dia = int(dia_text)

            span = day_div.find("span", class_="d-block")
            if not span:
                continue

            tomo = ""
            numero = ""
            for line in span.strings:
                line = line.strip()
                if line.startswith("Tomo"):
                    tomo = line.replace("Tomo", "").strip()
                elif line.startswith("Num."):
                    numero = line.replace("Num.", "").strip()

            documentos: List[TamaulipasPoDocumento] = []
            for a in span.find_all("a", href=True):
                titulo = a.text.strip()
                url = a["href"].strip()
                if titulo and url:
                    documentos.append(TamaulipasPoDocumento(
                        titulo=titulo, url_pdf=url))

            # Para reconstruir una fecha estándar YYYY-MM-DD (con zero-padding)
            fecha_iso = f"{anio}-{mes:02d}-{dia:02d}"

            if documentos:
                edicion = TamaulipasPoEdicion(
                    fecha=fecha_iso,
                    tomo=tomo,
                    numero=numero,
                    documentos=documentos
                )
                ediciones.append(edicion)

        return ediciones

    def obtener_ediciones(self, anio: int, mes: int) -> List[TamaulipasPoEdicion]:
        """
        Busca las ediciones publicadas en un mes y año específicos de forma síncrona.

        Args:
            anio (int): Ej. 2026
            mes (int): Ej. 3

        Returns:
            List[TamaulipasPoEdicion]: Lista de publicaciones de ese periodo.
        """
        params = {"ano": anio, "mes": mes}
        with httpx.Client(**self.client_kwargs) as client:
            response = client.get(
                self.BASE_URL, params=params, follow_redirects=True)
            response.raise_for_status()
            html = response.text

        return self._parsear_html(html, anio, mes)

    async def a_obtener_ediciones(self, anio: int, mes: int) -> List[TamaulipasPoEdicion]:
        """
        Busca las ediciones publicadas en un mes y año específicos de forma asíncrona.

        Args:
            anio (int): Ej. 2026
            mes (int): Ej. 3

        Returns:
            List[TamaulipasPoEdicion]: Lista de publicaciones de ese periodo.
        """
        params = {"ano": anio, "mes": mes}
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            response = await client.get(self.BASE_URL, params=params, follow_redirects=True)
            response.raise_for_status()
            html = response.text

        return self._parsear_html(html, anio, mes)
