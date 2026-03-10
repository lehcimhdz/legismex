import httpx
import re
from bs4 import BeautifulSoup
from typing import List, Dict
import asyncio

from .models import BcsPoEdicion


class BcsPoClient:
    """
    Cliente para interactuar con el portal de Boletines Oficiales de Baja California Sur.
    Extrae las ediciones por año desde la página de finanzas.bcs.gob.mx.
    """
    BASE_URL = "https://finanzas.bcs.gob.mx"
    INDEX_URL = f"{BASE_URL}/boletines-oficiales/"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _procesar_html_anio(self, html_content: str) -> List[BcsPoEdicion]:
        """
        Procesa el HTML de la página de un año específico, extrayendo las ediciones
        tanto de las tablas inyectadas por variables JS como de tablas HTML estándar.
        """
        ediciones_dict: Dict[str, BcsPoEdicion] = {}

        # 1. Parsear variables JavaScript si existen
        # El sitio puede inyectar HTML de las tablas dentro de variables (ej. let enero = '<table>...';)
        pattern = re.compile(r"let\s+\w+\s*=\s*'([^']*)';")
        matches = pattern.findall(html_content)
        for table_html in matches:
            self._extraer_ediciones_de_tabla(table_html, ediciones_dict)

        # 2. Si no se encontraron por JS, o además de JS hay tablas, buscamos tablas HTML estándar
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")
        for t in tables:
            self._extraer_ediciones_de_tabla(str(t), ediciones_dict)

        # Devolvemos la lista limpia sin duplicados por url
        return list(ediciones_dict.values())

    def _extraer_ediciones_de_tabla(self, table_html: str, ediciones_dict: Dict[str, BcsPoEdicion]):
        soup = BeautifulSoup(table_html, "html.parser")
        rows = soup.find_all("tr")
        for r in rows:
            tds = r.find_all("td")
            if len(tds) >= 2:
                title_text = tds[0].get_text(strip=True)
                link_tag = tds[1].find("a", href=True)
                if not link_tag:
                    # En algunos años, el enlace puede estar en el primer td
                    link_tag = tds[0].find("a", href=True)

                if not link_tag or not title_text:
                    continue

                href = link_tag["href"]
                # Formatear la URL absoluta
                if href.startswith("/"):
                    href = f"{self.BASE_URL}{href}"
                elif not href.startswith("http"):
                    href = f"{self.BASE_URL}/{href}"

                # Evitar procesar el mismo PDF dos veces si está tanto en JS como en tabla estática
                if href in ediciones_dict:
                    continue

                # Extraer Número y Fecha. Ejemplo: "Boletín No. 49 - Fecha 30/11/2024"
                m_num = re.search(
                    r"Bolet[ií]n\s+No\.?\s*([a-zA-Z0-9\s]+)\s*(?:-|$)", title_text, re.IGNORECASE)
                m_date = re.search(
                    r"Fecha\s+(\d{2}/\d{2}/\d{4})", title_text, re.IGNORECASE)

                b_num = m_num.group(1).strip() if m_num else "Sin Número"
                b_date = m_date.group(1).strip() if m_date else "Sin Fecha"

                # Limpieza extra
                if b_num.endswith("-"):
                    b_num = b_num[:-1].strip()

                edición = BcsPoEdicion(
                    numero=b_num,
                    fecha=b_date,
                    url_pdf=href
                )
                ediciones_dict[href] = edición

    def _obtener_urls_por_anio_sync(self) -> Dict[int, str]:
        """Obtiene el diccionario de años y sus URLs desde la página principal de boletines."""
        with httpx.Client(timeout=self.timeout, verify=False, follow_redirects=True) as client:
            response = client.get(self.INDEX_URL, headers=self.headers)
            response.raise_for_status()

            return self._parsear_urls_anio(response.text)

    async def _obtener_urls_por_anio_async(self) -> Dict[int, str]:
        """Obtiene el diccionario de años y sus URLs (Asíncrono)."""
        async with httpx.AsyncClient(timeout=self.timeout, verify=False, follow_redirects=True) as client:
            response = await client.get(self.INDEX_URL, headers=self.headers)
            response.raise_for_status()

            return self._parsear_urls_anio(response.text)

    def _parsear_urls_anio(self, html: str) -> Dict[int, str]:
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a")
        year_links = {}
        for link in links:
            text = link.get_text(strip=True)
            href = link.get("href")
            if text.isdigit() and len(text) == 4 and href:
                year_links[int(text)] = href
        return year_links

    def obtener_ediciones(self, anio: int) -> List[BcsPoEdicion]:
        """
        Obtiene las ediciones del Periódico Oficial para un año determinado (Síncrono).

        Args:
            anio: El año a consultar (ej. 2024).

        Returns:
            Lista de objetos BcsPoEdicion.
        """
        urls_por_anio = self._obtener_urls_por_anio_sync()
        url_anio_path = urls_por_anio.get(anio)

        if not url_anio_path:
            raise ValueError(
                f"No se encontró URL para el año {anio} en el portal.")

        url_completa = url_anio_path if url_anio_path.startswith(
            "http") else f"{self.BASE_URL}{url_anio_path}"

        with httpx.Client(timeout=self.timeout, verify=False, follow_redirects=True) as client:
            response = client.get(url_completa, headers=self.headers)
            response.raise_for_status()
            return self._procesar_html_anio(response.text)

    async def a_obtener_ediciones(self, anio: int) -> List[BcsPoEdicion]:
        """
        Obtiene las ediciones del Periódico Oficial para un año determinado (Asíncrono).

        Args:
            anio: El año a consultar (ej. 2024).

        Returns:
            Lista de objetos BcsPoEdicion.
        """
        urls_por_anio = await self._obtener_urls_por_anio_async()
        url_anio_path = urls_por_anio.get(anio)

        if not url_anio_path:
            raise ValueError(
                f"No se encontró URL para el año {anio} en el portal.")

        url_completa = url_anio_path if url_anio_path.startswith(
            "http") else f"{self.BASE_URL}{url_anio_path}"

        async with httpx.AsyncClient(timeout=self.timeout, verify=False, follow_redirects=True) as client:
            response = await client.get(url_completa, headers=self.headers)
            response.raise_for_status()
            return self._procesar_html_anio(response.text)
