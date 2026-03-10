import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime

from .models import CampechePoPublicacion


class CampechePoClient:
    """Cliente para extraer actas del Periódico Oficial del Estado de Campeche."""
    BASE_URL = "http://periodicooficial.campeche.gob.mx/sipoec/public/documentos"

    def __init__(self, **kwargs):
        """
        Inicializa el cliente del PO de Campeche.

        Args:
            **kwargs: Argumentos adicionales para httpx.Client o AsyncClient.
        """
        self.client_kwargs = {
            "verify": False,
            "timeout": 30.0,
            **kwargs
        }

    def _inferir_url(self, titulo: str, fecha_str: str) -> str:
        """
        Infiere la ruta final del documento combinando su fecha y título.
        Ejemplo: título 'PO2607PS04032026', fecha_str '2026-03-04'
        Resultado: http://.../periodicos/202603/PO2607PS04032026.pdf
        """
        # fecha_str debe ser YYYY-MM-DD
        try:
            year, month, _ = fecha_str.split("-")
            folder = f"{year}{month}"
            # Asegurar la terminacion .pdf en el nombre si no la tiene
            if not titulo.lower().endswith(".pdf"):
                titulo = f"{titulo}.pdf"
            return f"http://periodicooficial.campeche.gob.mx/sipoec/public/periodicos/{folder}/{titulo}"
        except Exception:
            return ""

    def _parsear_html(self, html: str) -> List[CampechePoPublicacion]:
        """Extrae la lista de publicaciones de la página en curso."""
        soup = BeautifulSoup(html, "html.parser")
        gacetas = []

        links = soup.find_all("a", {"data-toggle": "modal"})
        docs_raw = {}
        for link in links:
            doc_id = link.get("data-id")
            # A veces extrae multiples líneas
            text = link.get_text(separator=" | ", strip=True)
            if not doc_id:
                continue

            if doc_id not in docs_raw:
                docs_raw[doc_id] = []
            docs_raw[doc_id].append(text)

        for doc_id, fields in docs_raw.items():
            if len(fields) >= 2:
                # Usualmente el primer elemento es el título (PO260...) y el segundo la fecha (YYYY-MM-DD)
                titulo = fields[0]
                fecha_str = fields[1]

                try:
                    fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                    url_pdf = self._inferir_url(titulo, fecha_str)

                    gacetas.append(CampechePoPublicacion(
                        titulo=titulo,
                        fecha=fecha_obj,
                        url_pdf=url_pdf
                    ))
                except ValueError:
                    # Ignorar registros donde la fecha tenga un formato inesperado
                    pass

        return gacetas

    def _obtener_numero_paginas(self, html: str) -> int:
        """Encuentra la máxima paginación."""
        soup = BeautifulSoup(html, "html.parser")
        pagination = soup.find("ul", class_="pagination")
        if pagination:
            links = pagination.find_all("a")
            for link in links:
                if "Última" in link.get_text(strip=True):
                    href = link.get("href", "")
                    # href luce asi: documentos?anio=2026&page=8
                    if "page=" in href:
                        try:
                            # Parse page number
                            return int(href.split("page=")[1].split("&")[0])
                        except Exception:
                            pass
        return 1

    def obtener_publicaciones(self, anio: int, paginas: Optional[int] = None) -> List[CampechePoPublicacion]:
        """
        Obtiene las publicaciones de un año específico de forma síncrona.

        Args:
            anio: Año de búsqueda (ej. 2026).
            paginas: Límite de páginas a consultar. Si es None, extrae todas las disponibles.
        """
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with httpx.Client(**self.client_kwargs) as client:
                # Descubrir páginacion con el request a page=1
                url_base = f"{self.BASE_URL}?anio={anio}&page=1"
                resp = client.get(url_base)
                resp.raise_for_status()

                total_paginas = self._obtener_numero_paginas(resp.text)

                if paginas is not None:
                    total_paginas = min(paginas, total_paginas)

                resultados = self._parsear_html(resp.text)

                for page in range(2, total_paginas + 1):
                    url = f"{self.BASE_URL}?anio={anio}&page={page}"
                    resp = client.get(url)
                    resp.raise_for_status()
                    resultados.extend(self._parsear_html(resp.text))

                return resultados

    async def a_obtener_publicaciones(self, anio: int, paginas: Optional[int] = None) -> List[CampechePoPublicacion]:
        """
        Obtiene las publicaciones de un año específico de forma asíncrona y transita concurrentemente.
        """
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            async with httpx.AsyncClient(**self.client_kwargs) as client:
                url_base = f"{self.BASE_URL}?anio={anio}&page=1"
                resp = await client.get(url_base)
                resp.raise_for_status()

                total_paginas = self._obtener_numero_paginas(resp.text)

                if paginas is not None:
                    total_paginas = min(paginas, total_paginas)

                resultados = self._parsear_html(resp.text)

                if total_paginas > 1:
                    tareas = []
                    for page in range(2, total_paginas + 1):
                        url = f"{self.BASE_URL}?anio={anio}&page={page}"
                        tareas.append(client.get(url))

                    respuestas = await asyncio.gather(*tareas, return_exceptions=True)
                    for r in respuestas:
                        if isinstance(r, httpx.Response) and r.status_code == 200:
                            resultados.extend(self._parsear_html(r.text))

                return resultados
