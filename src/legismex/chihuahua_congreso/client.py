import httpx
from bs4 import BeautifulSoup
import re
from typing import List, Optional
from .models import ChihuahuaSesion, ChihuahuaDocumento


class ChihuahuaCongresoClient:
    """
    Cliente para la extracción de la Gaceta Parlamentaria del
    H. Congreso del Estado de Chihuahua.
    """
    BASE_URL = "https://www.congresochihuahua.gob.mx"
    URL_BASE_GACETA = f"{BASE_URL}/sesiones.php"

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _parse_detalle_url(self, js_call: str) -> Optional[str]:
        """
        Convierte una llamada JS "javascript: detalle(2097,'documento','',1)"
        en una URL de la forma "https://www.congresochihuahua.gob.mx/detalleSesion.php?idsesion=2097&tipo=documento&id=&idtipodocumento=1"
        """
        match = re.search(r"detalle\((.*?)\)", js_call)
        if match:
            # Los args son (idsesion, tipo, id, idtipodocumento)
            args_str = match.group(1)
            # Separar por comas (cuidado con comillas)
            args = [arg.strip().strip("'").strip('"')
                    for arg in args_str.split(",")]
            # Manejar el hecho de que algunos argumentos pueden no estar
            idsesion = args[0] if len(args) > 0 else ""
            tipo = args[1] if len(args) > 1 else ""
            id_doc = args[2] if len(args) > 2 else ""
            idtipodoc = args[3] if len(args) > 3 else ""

            return f"{self.BASE_URL}/detalleSesion.php?idsesion={idsesion}&tipo={tipo}&id={id_doc}&idtipodocumento={idtipodoc}"
        return None

    def _parsear_sesion(self, article: BeautifulSoup) -> Optional[ChihuahuaSesion]:
        # Título principal y descripción
        title_block = article.find("figure", class_="event_title")
        if not title_block:
            return None

        titulo = title_block.find("h3").get_text(
            strip=True) if title_block.find("h3") else ""
        h4 = title_block.find("h4")
        descripcion = h4.get_text(strip=True) if h4 else ""

        # Obtener sesion_id del href en el h4 si existe
        sesion_id = ""
        if h4 and h4.find("a"):
            js_call = h4.find("a").get("href", "")
            match = re.search(r"detalle\((\d+),", js_call)
            if match:
                sesion_id = match.group(1)

        # Metadatos (Fecha, Video, Asistencia)
        url_video = None
        url_asistencia = None
        fecha = ""

        meta = article.find("figure", class_="event_meta")
        if meta:
            anchors = meta.find_all("a", class_="btn btn-default")
            for a in anchors:
                text = a.get_text(strip=True)
                href = a.get("href", "")

                if a.find("i", class_="fa-calendar"):
                    fecha = text
                elif a.find("i", class_="fa-youtube-play"):
                    url_video = href
                elif a.find("i", class_="fa-check-square-o"):
                    parsed = self._parse_detalle_url(href)
                    url_asistencia = parsed if parsed else href

        sesion = ChihuahuaSesion(
            sesion_id=sesion_id,
            titulo=titulo,
            descripcion=descripcion,
            fecha=fecha,
            url_video=url_video,
            url_asistencia=url_asistencia,
        )

        # Buscar las 4 columnas de contenido
        alert_blocks = article.find_all("div", class_="alert-search")
        for alert in alert_blocks:
            h4_header = alert.find("h4")
            if not h4_header:
                continue

            header_text = h4_header.get_text(strip=True).lower()
            links = alert.find_all("a")

            docs = []
            for link in links:
                js_href = link.get("href", "")
                parsed_url = self._parse_detalle_url(js_href)
                if parsed_url:
                    docs.append(ChihuahuaDocumento(
                        titulo=link.get_text(strip=True),
                        url=parsed_url
                    ))

            if "probable" in header_text:
                sesion.documentos_probables = docs
            elif "desahogado" in header_text and "votación" not in header_text and "registro" not in header_text:
                sesion.documentos_desahogados = docs
            elif "votación" in header_text:
                sesion.documentos_votacion = docs
            elif "turnado" in header_text:
                sesion.asuntos_turnados = docs

        return sesion

    def _procesar_html(self, html_content: str) -> List[ChihuahuaSesion]:
        soup = BeautifulSoup(html_content, "html.parser")
        sesiones = []

        articles = soup.find_all("article", class_="event_listing_wrapper")
        for article in articles:
            s = self._parsear_sesion(article)
            if s:
                sesiones.append(s)

        return sesiones

    def obtener_sesiones(self, pagina: int = 1) -> List[ChihuahuaSesion]:
        """
        Extrae las sesiones de la página indicada de la Gaceta Parlamentaria de forma síncrona.
        :param pagina: El número de página (por defecto 1).
        """
        params = {"pag": pagina, "pagina": "gacetas"}
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(self.URL_BASE_GACETA,
                                  params=params, headers=self.headers)
            response.raise_for_status()
            return self._procesar_html(response.text)

    async def a_obtener_sesiones(self, pagina: int = 1) -> List[ChihuahuaSesion]:
        """Extrae las sesiones de la página indicada asíncronamente."""
        params = {"pag": pagina, "pagina": "gacetas"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.URL_BASE_GACETA, params=params, headers=self.headers)
            response.raise_for_status()
            return self._procesar_html(response.text)
