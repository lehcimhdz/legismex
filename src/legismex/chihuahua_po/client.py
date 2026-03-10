import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from urllib.parse import urljoin
from .models import ChihuahuaPoEdicion


class ChihuahuaPoClient:
    """
    Cliente para la extracción de las publicaciones del Periódico Oficial 
    del Estado de Chihuahua.
    """
    BASE_URL = "https://chihuahua.gob.mx"
    URL_BUSCADOR = f"{BASE_URL}/periodicooficial/buscador"

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        # Es común que drupal/PHP reciba bien los user-agents comunes
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _parsear_edicion(self, row: BeautifulSoup) -> Optional[ChihuahuaPoEdicion]:
        """Extrae la información de una fila (tr) del buscador de Drupal."""

        # Título
        title_td = row.find("td", class_="views-field-title")
        titulo = ""
        if title_td:
            a_tag = title_td.find("a")
            if a_tag:
                titulo = a_tag.get_text(strip=True)

        if not titulo:
            return None

        # Fecha (el primer o segundo field-fecha-de-la-nota, tomaremos la ISO del datetime)
        fecha_tds = row.find_all(
            "td", class_="views-field-field-fecha-de-la-nota")
        fecha_iso = ""
        fecha_legible = ""
        # Tomar la iso del tr si existe
        time_tag = row.find("time")
        if time_tag:
            fecha_iso = time_tag.get("datetime", "")

        # A veces la fecha completa legible viene en el titulo tr?
        # Pero podemos formar la fecha_legible a partir del titulo mismo si es "Sábado 07 de marzo de 2026",
        # ya que la fecha_legible es el texto de ese anchor title en realidad.
        # Mejor asignamos el titulo también como fecha_legible si aplica.
        fecha_legible = titulo

        # Enlace Ejemplar
        ejemplar_td = row.find(
            "td", class_="views-field-field-periodico-oficial")
        url_ejemplar = None
        if ejemplar_td:
            a_ejemplar = ejemplar_td.find("a", type="application/pdf")
            if a_ejemplar:
                url_ejemplar = urljoin(
                    self.BASE_URL, a_ejemplar.get("href", ""))

        # Anexos
        anexos_td = row.find(
            "td", class_="views-field-field-anexos-del-periodico")
        url_anexos = []
        if anexos_td:
            a_anexos = anexos_td.find_all("a", type="application/pdf")
            for a in a_anexos:
                href = a.get("href", "")
                if href:
                    url_anexos.append(urljoin(self.BASE_URL, href))

        return ChihuahuaPoEdicion(
            titulo=titulo,
            fecha_iso=fecha_iso,
            fecha_legible=fecha_legible,
            url_ejemplar=url_ejemplar,
            url_anexos=url_anexos
        )

    def _procesar_html(self, html_content: str) -> List[ChihuahuaPoEdicion]:
        soup = BeautifulSoup(html_content, "html.parser")
        ediciones = []

        rows = soup.find_all("tr")
        for row in rows:
            # Si el tr tiene tds relacionados a results
            if row.find("td", class_="views-field-title"):
                edicion = self._parsear_edicion(row)
                if edicion:
                    ediciones.append(edicion)

        return ediciones

    def obtener_ediciones(self, fecha: str = None, texto: str = None, pagina: int = 0) -> List[ChihuahuaPoEdicion]:
        """
        Extrae las ediciones síncronamente desde el buscador de Drupal.

        :param fecha: Fecha exacta formato 'YYYY-MM-DD' (e.g. '2025-03-05').
        :param texto: Palabras de búsqueda por texto abierto.
        :param pagina: Índice de la página de resultados (comienza en 0).
        """
        params = {"page": pagina}
        if fecha:
            params["field_po_fecha_de_publicacion_value"] = fecha
        if texto:
            params["keys"] = texto

        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                self.URL_BUSCADOR, params=params, headers=self.headers)
            response.raise_for_status()
            return self._procesar_html(response.text)

    async def a_obtener_ediciones(self, fecha: str = None, texto: str = None, pagina: int = 0) -> List[ChihuahuaPoEdicion]:
        """
        Extrae las ediciones asíncronamente desde el buscador de Drupal.
        """
        params = {"page": pagina}
        if fecha:
            params["field_po_fecha_de_publicacion_value"] = fecha
        if texto:
            params["keys"] = texto

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.URL_BUSCADOR, params=params, headers=self.headers)
            response.raise_for_status()
            return self._procesar_html(response.text)
