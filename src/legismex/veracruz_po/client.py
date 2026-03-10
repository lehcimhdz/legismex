import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
import urllib.parse
from .models import VeracruzPoEdicion


class VeracruzPoClient:
    """Cliente para interactuar con la Gaceta Oficial del Estado de Veracruz (Periódico Oficial)."""

    BASE_URL = "https://editoraveracruz.gob.mx/gacetas/seleccion.php"
    PDF_BASE_URL = "https://editoraveracruz.gob.mx/gacetas/"

    def __init__(self, use_async: bool = False):
        self.use_async = use_async
        self._sync_client = httpx.Client(verify=False, follow_redirects=True)
        self._async_client = None
        if self.use_async:
            self._async_client = httpx.AsyncClient(
                verify=False, follow_redirects=True)

    def _post(self, data: dict) -> str:
        """Realiza una petición POST de forma síncrona."""
        response = self._sync_client.post(self.BASE_URL, data=data)
        response.raise_for_status()
        return response.text

    async def _apost(self, data: dict) -> str:
        """Realiza una petición POST de forma asíncrona."""
        if not self._async_client:
            self._async_client = httpx.AsyncClient(
                verify=False, follow_redirects=True)
        response = await self._async_client.post(self.BASE_URL, data=data)
        response.raise_for_status()
        return response.text

    def _parse(self, html: str) -> List[VeracruzPoEdicion]:
        """Extrae las ediciones del Periódico Oficial del HTML retornado por el API."""
        soup = BeautifulSoup(html, "lxml")
        ediciones = []

        for article in soup.find_all("article", class_="cardGacetaHistorica"):
            data_id = article.get("data-id")
            if not data_id:
                continue

            # Extract plain text content for the name e.g "Gac2024-001 Lunes 01.pdf"
            nombre_raw = article.text.strip()

            # Clean up trailing .pdf if present (for accurate `fecha_textual` display)
            nombre = nombre_raw[:-
                                4] if nombre_raw.lower().endswith(".pdf") else nombre_raw

            # The name is usually "GacYYYY-XXX Day DD [TOMO Ext]"
            # So the date part is basically the "Day DD" part
            parts = nombre.split(" ")
            fecha_textual = ""
            if len(parts) >= 3:
                fecha_textual = f"{parts[1]} {parts[2]}"
            elif len(parts) == 2:
                fecha_textual = parts[1]

            # The URL uses urllib.parse.quote() for spaces to become %20
            # Ensure "Gac2024-001 Lunes 01.pdf" turns into "Gac2024-001%20Lunes%2001.pdf"
            pdf_path_quoted = urllib.parse.quote(data_id)
            url_pdf = f"{self.PDF_BASE_URL}{pdf_path_quoted}"

            ediciones.append(
                VeracruzPoEdicion(
                    nombre=nombre,
                    fecha_textual=fecha_textual,
                    url_pdf=url_pdf
                )
            )

        return ediciones

    def obtener_ediciones(self, anio: int | str, mes: int | str) -> List[VeracruzPoEdicion]:
        """Obtiene las publicaciones de la Gaceta Oficial de Veracruz form un año y mes (1-12)."""
        mes_str = str(mes).zfill(2)
        anio_str = str(anio)
        data = {"anio": anio_str, "mes": mes_str}

        if self.use_async:
            raise RuntimeError("Use aostener_ediciones() in async mode")

        html = self._post(data)
        return self._parse(html)

    async def aobtener_ediciones(self, anio: int | str, mes: int | str) -> List[VeracruzPoEdicion]:
        """Obtiene las publicaciones de la Gaceta Oficial de forma asíncrona."""
        mes_str = str(mes).zfill(2)
        anio_str = str(anio)
        data = {"anio": anio_str, "mes": mes_str}

        if not self.use_async:
            raise RuntimeError(
                "Client must be initialized with use_async=True")

        html = await self._apost(data)
        return self._parse(html)

    async def close(self):
        """Cierra el cliente asíncrono si está activo."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
