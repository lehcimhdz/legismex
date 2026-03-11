import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
import urllib.parse
import re
from .models import CoahuilaPoEdicion


class CoahuilaPoClient:
    """
    Cliente para extraer datos del Periódico Oficial del Estado de Coahuila.
    Extrae la lista completa de ediciones agrupadas por año desde un Response unificado.
    """
    URL_BASE = "https://periodico.segobcoahuila.gob.mx"
    URL_BUSQUEDA = f"{URL_BASE}/BusquedaPorA%C3%B1o.asp"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _extraer_url_pdf(self, html_str: str) -> Optional[str]:
        """Extrae la URL del PDF del evento onclick 'cargarIframe('verPDFpc.asp?file=X', ...)'"""
        match = re.search(r"cargarIframe\('([^']+)'", html_str)
        if match:
            url_relativa = match.group(1)
            # El botón "PERIODICO" tiene `verPDFpc.asp?file=...`
            if url_relativa.startswith("verPDFpc.asp"):
                return urllib.parse.urljoin(f"{self.URL_BASE}/", url_relativa)
        return None

    def _extraer_id_sumario(self, html_str: str) -> Optional[str]:
        """Extraer el ID de sumario del evento 'cargarIframe('versumariocompleto.asp?Id_Sumario=X', ...)'"""
        match = re.search(r"Id_Sumario=([^']+)", html_str)
        if match:
            return match.group(1)
        return None

    def _procesar_edicion(self, row: BeautifulSoup) -> Optional[CoahuilaPoEdicion]:
        """Procesa un `tr` de la tabla HTML y lo convierte en objeto Pydantic"""
        tds = row.find_all("td")
        if len(tds) < 6:
            return None

        # Columna 0: Botones "INDICE" y "PERIODICO"
        botones_html = str(tds[0])
        # Solo me interesa extraer la URL base al PDF
        url_pdf = None
        id_sumario = self._extraer_id_sumario(botones_html)

        # Buscamos multiples 'cargarIframe' porque hay 2 botones
        for m in re.finditer(r"cargarIframe\('([^']+)'", botones_html):
            url_rel = m.group(1)
            if "verPDFpc.asp" in url_rel:
                url_pdf = urllib.parse.urljoin(f"{self.URL_BASE}/", url_rel)

        fecha_publicacion = tds[1].get_text(strip=True)
        tomo = tds[2].get_text(strip=True)
        numero = tds[3].get_text(strip=True)
        tipo = tds[4].get_text(strip=True)
        sumario = tds[5].get_text(separator="\n", strip=True)

        if not fecha_publicacion and not numero:
            return None

        return CoahuilaPoEdicion(
            fecha_publicacion=fecha_publicacion,
            tomo=tomo,
            numero=numero,
            tipo=tipo,
            sumario=sumario,
            url_pdf=url_pdf,
            id_sumario=id_sumario
        )

    def _procesar_html(self, html_content: str) -> List[CoahuilaPoEdicion]:
        soup = BeautifulSoup(html_content, "html.parser")
        ediciones = []

        # La tabla se llama publicationsTable
        table = soup.find("table", id="publicationsTable")
        if not table:
            return ediciones

        tbody = table.find("tbody")
        if not tbody:
            return ediciones

        # Obtenemos las filas que no son detalles dinámicos generados por datatable en móviles (child)
        rows = tbody.find_all("tr", recursive=False)
        for row in rows:
            # Descartar filas child que Responsive DataTables inyecta
            if "child" in row.get("class", []):
                continue

            edicion = self._procesar_edicion(row)
            if edicion:
                ediciones.append(edicion)

        return ediciones

    def obtener_ediciones(self, anio: int) -> List[CoahuilaPoEdicion]:
        """Extrae todas las publicaciones del P.O. de un año específico de forma Síncrona."""
        params = {"Ano": str(anio)}
        with httpx.Client(timeout=self.timeout, follow_redirects=True, verify=False) as client:
            response = client.get(
                self.URL_BUSQUEDA, params=params, headers=self.headers)
            response.raise_for_status()
            # La página puede venir en windows-1252 o iso-8859-1 en vez de utf-8 a veces
            response.encoding = 'utf-8'
            return self._procesar_html(response.text)

    async def a_obtener_ediciones(self, anio: int) -> List[CoahuilaPoEdicion]:
        """Extrae todas las publicaciones del P.O. de un año específico de forma Asíncrona."""
        params = {"Ano": str(anio)}
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
            response = await client.get(self.URL_BUSQUEDA, params=params, headers=self.headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return self._procesar_html(response.text)
