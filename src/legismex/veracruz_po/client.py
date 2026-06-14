import httpx
from bs4 import BeautifulSoup
from typing import List
import urllib.parse
from .models import VeracruzPoEdicion
from legismex.exceptions import wrap_httpx_errors


class VeracruzPoClient:
    """Cliente para interactuar con la Gaceta Oficial del Estado de Veracruz (Periódico Oficial)."""

    BASE_URL = "https://editoraveracruz.gob.mx/gacetas/seleccion.php"
    PDF_BASE_URL = "https://editoraveracruz.gob.mx/gacetas/"

    def __init__(self, **kwargs):
        # Backward-compat: ignora ``use_async`` si lo pasa código viejo.
        kwargs.pop("use_async", None)

        self.client_kwargs = {
            "verify": False,
            "follow_redirects": True,
            "timeout": 30.0,
            **kwargs,
        }

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
        """Obtiene las publicaciones de la Gaceta Oficial de Veracruz para un año y mes (1-12)."""
        mes_str = str(mes).zfill(2)
        anio_str = str(anio)
        data = {"anio": anio_str, "mes": mes_str}

        with httpx.Client(**self.client_kwargs) as client, wrap_httpx_errors(self.BASE_URL):
            response = client.post(self.BASE_URL, data=data)
            response.raise_for_status()
            return self._parse(response.text)

    async def a_obtener_ediciones(self, anio: int | str, mes: int | str) -> List[VeracruzPoEdicion]:
        """Versión asíncrona de :meth:`obtener_ediciones`."""
        mes_str = str(mes).zfill(2)
        anio_str = str(anio)
        data = {"anio": anio_str, "mes": mes_str}

        async with httpx.AsyncClient(**self.client_kwargs) as client:
            with wrap_httpx_errors(self.BASE_URL):
                response = await client.post(self.BASE_URL, data=data)
                response.raise_for_status()
                return self._parse(response.text)

    # Backward-compat: nombre anterior (mantener referencias existentes que vivían en el codebase).
    aobtener_ediciones = a_obtener_ediciones
