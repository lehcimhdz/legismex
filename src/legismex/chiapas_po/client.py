import asyncio
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from .models import ChiapasPoEdicion, ChiapasAdministracion


class ChiapasPoClient:
    """Cliente para extraer el Periódico Oficial del Estado de Chiapas por quinquenios."""
    BASE_URL = "https://www.sgg.chiapas.gob.mx/periodico/"

    def __init__(self, **kwargs):
        """
        Inicializa el cliente de PO Chiapas.

        Args:
            **kwargs: Argumentos adicionales para httpx.Client o AsyncClient,
                como timeouts, verificación SSL, proxies, etc.
        """
        self.client_kwargs = {
            "verify": False,  # Ignorar validación SSL de sgg.chiapas.gob.mx
            "timeout": 30.0,
            "follow_redirects": True,
            **kwargs
        }

    def _parsear_html(self, html: str) -> List[ChiapasPoEdicion]:
        soup = BeautifulSoup(html, "html.parser")
        medias = soup.find_all("div", class_="media-body")

        ediciones: List[ChiapasPoEdicion] = []
        for media in medias:
            h5 = media.find("h5")
            if not h5:
                continue

            title_text = h5.text.strip()
            parts = [p.strip() for p in title_text.split(",")]

            numero = ""
            seccion = None
            parte = None
            fecha = ""

            for part in parts:
                if part.startswith("Periódico:"):
                    numero = part.replace("Periódico:", "").strip()
                elif part.startswith("Sección:"):
                    seccion = part.replace("Sección:", "").strip()
                elif part.startswith("Parte:"):
                    parte = part.replace("Parte:", "").strip()
                elif part.startswith("Fecha:"):
                    fecha = part.replace("Fecha:", "").strip()

            a = media.find("a", class_="card-link")
            url_pdf = a["href"] if a else ""

            if numero and fecha and url_pdf:
                # Modificando URL relativa si es necesario (el sitio los sirve absolutos pero previene fallos)
                if url_pdf.startswith("/"):
                    url_pdf = f"https://www.sgg.chiapas.gob.mx{url_pdf}"

                edicion = ChiapasPoEdicion(
                    numero=numero,
                    fecha=fecha,
                    seccion=seccion,
                    parte=parte,
                    url_pdf=url_pdf
                )
                ediciones.append(edicion)

        return ediciones

    def _crear_data(self, anio: Optional[int], mes: Optional[int], numero: Optional[str], pg: int) -> dict:
        return {
            "a": str(anio) if anio else "",
            "m": str(mes) if mes else "",
            "p": str(numero) if numero else "",
            "pg": str(pg)
        }

    def obtener_ediciones(
        self,
        admin: ChiapasAdministracion = ChiapasAdministracion.ADMIN_2024_2030,
        anio: Optional[int] = None,
        mes: Optional[int] = None,
        numero: Optional[str] = None
    ) -> List[ChiapasPoEdicion]:
        """
        Obtiene las ediciones del PO Chiapas de forma síncrona.
        Itera automáticamente todas las páginas disponibles para la búsqueda.

        Args:
            admin: Enum para seleccionar el endpoint del sexenio de gobierno.
            anio: Filtro opcional por año (ej. 2024).
            mes: Filtro opcional por mes (ej. 12).
            numero: Filtro opcional por número de publicación.

        Returns:
            List[ChiapasPoEdicion]: Todos los registros encontrados.
        """
        url = f"{self.BASE_URL}{admin.value}"
        ediciones_totales = []
        pg = 1

        with httpx.Client(**self.client_kwargs) as client:
            while True:
                data = self._crear_data(anio, mes, numero, pg)
                response = client.post(url, data=data, follow_redirects=True)
                response.raise_for_status()

                ediciones_pagina = self._parsear_html(response.text)
                if not ediciones_pagina:
                    break

                ediciones_totales.extend(ediciones_pagina)
                pg += 1

        return ediciones_totales

    async def a_obtener_ediciones(
        self,
        admin: ChiapasAdministracion = ChiapasAdministracion.ADMIN_2024_2030,
        anio: Optional[int] = None,
        mes: Optional[int] = None,
        numero: Optional[str] = None
    ) -> List[ChiapasPoEdicion]:
        """
        Obtiene las ediciones del PO Chiapas de forma asíncrona.
        Itera automáticamente todas las páginas disponibles para la búsqueda.

        Args:
            admin: Enum para seleccionar el endpoint del sexenio de gobierno.
            anio: Filtro opcional por año (ej. 2024).
            mes: Filtro opcional por mes (ej. 12).
            numero: Filtro opcional por número de publicación.

        Returns:
            List[ChiapasPoEdicion]: Todos los registros encontrados.
        """
        url = f"{self.BASE_URL}{admin.value}"
        ediciones_totales = []
        pg = 1

        async with httpx.AsyncClient(**self.client_kwargs) as client:
            while True:
                data = self._crear_data(anio, mes, numero, pg)
                response = await client.post(url, data=data, follow_redirects=True)
                response.raise_for_status()

                ediciones_pagina = self._parsear_html(response.text)
                if not ediciones_pagina:
                    break

                ediciones_totales.extend(ediciones_pagina)
                pg += 1

        return ediciones_totales
