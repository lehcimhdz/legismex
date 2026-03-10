import httpx
from bs4 import BeautifulSoup
from typing import List
from .models import YucatanIniciativa, YucatanDocumento


class YucatanCongresoClient:
    """
    Cliente para la extracción de las Iniciativas del Congreso del Estado de Yucatán.
    Extrae la lista completa y mapea los documentos relacionados.
    """
    BASE_URL = "https://www.congresoyucatan.gob.mx"
    URL_INICIATIVAS = f"{BASE_URL}/gaceta/iniciativas"

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        # El sitio puede restringir peticiones que no pasen headers verosímiles
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.congresoyucatan.gob.mx/",
            "Connection": "keep-alive"
        }

    def _get_httpx_ssl_client(self) -> httpx.Client:
        # Yucatán requiere que nos conectemos con HTTP/1.1 para evadir los bloqueos estrictos o WAF
        return httpx.Client(timeout=self.timeout, verify=False, http1=True, http2=False)

    def _get_httpx_ssl_async_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self.timeout, verify=False, http1=True, http2=False)

    def _procesar_html(self, html_content: str) -> List[YucatanIniciativa]:
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", id="example")
        if not table:
            return []

        tbody = table.find("tbody")
        # Fallback si no hay estructuración thead/tbody explícita
        rows = tbody.find_all("tr") if tbody else table.find_all("tr")[1:]

        iniciativas = []
        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) < 7:
                continue

            legis = tds[0].get_text(strip=True)
            desc = tds[1].get_text(strip=True)
            f_pres = tds[2].get_text(strip=True)
            pres_por = tds[3].get_text(strip=True)
            f_turnada = tds[4].get_text(strip=True)
            comision = tds[5].get_text(strip=True)
            docs_td = tds[6]

            # Buscar documentos
            documentos = []
            for a_tag in docs_td.find_all("a", href=True):
                href = a_tag["href"]
                # Formatear la URL absoluta
                if href.startswith("/"):
                    href = f"{self.BASE_URL}{href}"
                elif not href.startswith("http"):
                    href = f"{self.BASE_URL}/{href}"

                # Intentar detectar extensión desde href o iconos de FontAwesome
                ext = "pdf" if ".pdf" in href.lower(
                ) else "docx" if ".doc" in href.lower() else "desconocido"

                if ext == "desconocido":
                    # Intentar detectar por clase i/svg
                    if a_tag.find("svg", class_="fa-file-pdf") or a_tag.find("i", class_="fa-file-pdf"):
                        ext = "pdf"
                    elif a_tag.find("svg", class_="fa-file-word") or a_tag.find("i", class_="fa-file-word"):
                        ext = "docx"

                documentos.append(YucatanDocumento(url=href, extension=ext))

            iniciativas.append(YucatanIniciativa(
                legislatura=legis,
                descripcion=desc,
                fecha_presentada=f_pres,
                presentada_por=pres_por,
                fecha_turnada=f_turnada,
                comision_permanente=comision,
                documentos=documentos
            ))

        return iniciativas

    def obtener_iniciativas(self) -> List[YucatanIniciativa]:
        """Extrae la lista de iniciativas de forma síncrona."""
        with self._get_httpx_ssl_client() as client:
            response = client.get(self.URL_INICIATIVAS, headers=self.headers)
            response.raise_for_status()
            return self._procesar_html(response.text)

    async def a_obtener_iniciativas(self) -> List[YucatanIniciativa]:
        """Extrae la lista de iniciativas de forma asíncrona."""
        async with self._get_httpx_ssl_async_client() as client:
            response = await client.get(self.URL_INICIATIVAS, headers=self.headers)
            response.raise_for_status()
            return self._procesar_html(response.text)
