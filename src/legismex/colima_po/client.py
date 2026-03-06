import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime

from .models import ColimaPoEdicion, ColimaPoDocumento

class ColimaPoClient:
    """Cliente para extraer ediciones del Periódico Oficial del Estado de Colima."""
    BASE_URL = "https://periodicooficial.col.gob.mx/p"

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "verify": False,  # Ignorar problemas de SSL del sitio web oficial
            **kwargs
        }

    def _url_str(self, path: str) -> str:
        if path.startswith("http"):
            return path
        return f"{self.BASE_URL}/{path}"

    def _parse_portada(self, html: str, url_portada: str, fecha_str: str) -> ColimaPoEdicion:
        # Base de la URL de la portada para construir PDFs relativos
        base_dir = url_portada.rsplit("/", 1)[0]
        
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a")
        
        docs = []
        for p in links:
            href = p.get("href", "")
            if ".pdf" in href.lower():
                texto = p.get_text(strip=True)
                
                # Intentamos sacar mejor descripción del TR
                parent = p.find_parent("tr")
                if parent:
                    # Limpiamos el separador
                    texto = " | ".join([s for s in parent.stripped_strings if s and "PDF" not in s]) or texto

                docs.append(ColimaPoDocumento(
                    titulo=texto,
                    url_descarga=f"{base_dir}/{href}"
                ))

        return ColimaPoEdicion(
            fecha=fecha_str,
            url_portada=url_portada,
            documentos=docs
        )

    # --- Síncronos ---

    def _obtener_portada(self, client: httpx.Client, href_dia: str) -> ColimaPoEdicion:
        url_portada = self._url_str(href_dia)
        # href_dia es tipo '02022026/portada.htm' -> extraemos la fecha '02022026'
        parts = href_dia.split("/")
        fecha_str = parts[0] if parts else ""
        if len(fecha_str) == 8:
            # Formatear a YYYY-MM-DD
            try:
                fecha_str = datetime.strptime(fecha_str, "%d%m%Y").strftime("%Y-%m-%d")
            except ValueError:
                pass

        resp = client.get(url_portada)
        if resp.status_code == 200:
            return self._parse_portada(resp.text, url_portada, fecha_str)
        return ColimaPoEdicion(fecha=fecha_str, url_portada=url_portada, documentos=[])

    def obtener_ediciones_mes(self, year: int, month: int) -> List[ColimaPoEdicion]:
        """Obtiene todas las ediciones publicadas en un mes específico."""
        with httpx.Client(**self.client_kwargs) as client:
            url_calendario = f"{self.BASE_URL}/princi.php?liga={month}_{year}"
            resp = client.get(url_calendario)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            calendar_links = soup.find_all("a")

            ediciones = []
            for enlace in calendar_links:
                href = enlace.get("href", "")
                if href.endswith("portada.htm"):
                    ediciones.append(self._obtener_portada(client, href))

            return ediciones

    # --- Asíncronos ---

    async def _a_obtener_portada(self, client: httpx.AsyncClient, href_dia: str) -> ColimaPoEdicion:
        url_portada = self._url_str(href_dia)
        parts = href_dia.split("/")
        fecha_str = parts[0] if parts else ""
        if len(fecha_str) == 8:
            try:
                fecha_str = datetime.strptime(fecha_str, "%d%m%Y").strftime("%Y-%m-%d")
            except ValueError:
                pass

        resp = await client.get(url_portada)
        if resp.status_code == 200:
            return self._parse_portada(resp.text, url_portada, fecha_str)
        return ColimaPoEdicion(fecha=fecha_str, url_portada=url_portada, documentos=[])

    async def a_obtener_ediciones_mes(self, year: int, month: int) -> List[ColimaPoEdicion]:
        """Obtiene de manera asíncrona todas las ediciones publicadas en un mes específico."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            url_calendario = f"{self.BASE_URL}/princi.php?liga={month}_{year}"
            resp = await client.get(url_calendario)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            calendar_links = soup.find_all("a")

            tareas = []
            for enlace in calendar_links:
                href = enlace.get("href", "")
                if href.endswith("portada.htm"):
                    tareas.append(self._a_obtener_portada(client, href))

            resultados = await asyncio.gather(*tareas)
            return list(resultados)
