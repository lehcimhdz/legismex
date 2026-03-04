import logging
from typing import List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re

from legismex.puebla.models import PueblaGaceta

# Try to import playwright
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class PueblaClient:
    """
    Cliente para interactuar con la Gaceta Legislativa del Congreso de Puebla.
    Dado que el sitio web utiliza una protección tipo Cloudflare que bloquea 
    a clientes HTTP estándar (como httpx o requests), este cliente emplea 
    'playwright' para renderizar el contenido.
    """
    BASE_URL = "https://www.congresopuebla.gob.mx"
    # Gaceta Legislativa link (Id 12442 for LXII)
    GACETAS_URL = "https://www.congresopuebla.gob.mx/index.php?option=com_content&view=article&id=12442"

    def __init__(self, headless: bool = True):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "La biblioteca 'playwright' no está instalada, pero es requerida "
                "por PueblaClient debido a las mitigaciones de bots (Cloudflare) "
                "del sitio web de Puebla.\n"
                "Instálalo usando 'pip install playwright' seguido de 'playwright install chromium'."
            )
        self.headless = headless
        self.logger = logging.getLogger(__name__)

    def _get_page_content(self, url: str, wait_time: int = 5) -> str:
        """
        Descarga el HTML usando playwright.
        
        Args:
            url (str): La URL a descargar.
            wait_time (int): Segundos a esperar para que Cloudflare termine su verificación.
        """
        import time
        
        self.logger.debug(f"Fetching {url} using Playwright (headless={self.headless})")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ignore_https_errors=True
            )
            page = context.new_page()
            try:
                # Wait until network is idle to pass cloudflare check if required
                page.goto(url, wait_until="networkidle", timeout=60000)
                # Wait additional time for dynamic JS tables if any
                time.sleep(wait_time)
                content = page.content()
                return content
            except Exception as e:
                self.logger.error(f"Error cargando la página con Playwright: {e}")
                raise
            finally:
                browser.close()

    def obtener_gacetas_recientes(self) -> List[PueblaGaceta]:
        """
        Obtiene la lista de gacetas legislativas publicadas en la página actual.
        Para la LXII Legislatura.
        """
        html = self._get_page_content(self.GACETAS_URL, wait_time=5)
        soup = BeautifulSoup(html, "html.parser")
        
        gacetas = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "GACETAS" in href.upper():
                # Extraer texto del link y texto de su componente padre si está suelto
                parent_text = " ".join(a.parent.stripped_strings)
                partes = parent_text.split()
                
                mes = "Desconocido"
                numero = ""
                fecha_texto = parent_text
                
                if len(partes) >= 2:
                    mes = partes[0]
                    numero = partes[1]
                
                # Tratar de encontrar el año legislativo en la url
                anio_legis = None
                match = re.search(r'/(?P<anio>\w+aniolegislativo)/', href, re.IGNORECASE)
                if match:
                    anio_legis = match.group("anio")

                full_url = urljoin(self.BASE_URL, href)
                
                gaceta = PueblaGaceta(
                    mes=mes,
                    numero=numero,
                    fecha_texto=fecha_texto,
                    url_pdf=full_url,
                    anio_legislativo=anio_legis
                )
                gacetas.append(gaceta)
                
        return gacetas
