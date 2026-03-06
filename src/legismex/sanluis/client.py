import base64
import httpx
import re
from typing import List, Optional, Tuple

from .models import SanLuisGaceta
from .parser import SanLuisParser


class SanLuisClient:
    """Client for the Gaceta Parlamentaria of the Congreso del Estado de San Luis Potosí.

    The portal (``congresosanluis.gob.mx``) runs Drupal 7 and publishes all
    sessions in a **single static page** — no pagination, no AJAX.

    A single GET to the gacetas URL delivers the complete historical archive
    (Sesiones Ordinarias y Extraordinarias desde la LXII Legislatura, 2015–present).

    Example::

        from legismex.sanluis import SanLuisClient

        client = SanLuisClient()
        gacetas = client.obtener_gacetas()

        print(f"Total sesiones: {len(gacetas)}")
        for g in gacetas[:3]:
            print(f"[{g.mes}] {g.nombre} | {g.fecha_iso[:10]}")
            for url in g.urls_pdf:
                print(f"  PDF: {url}")
    """

    BASE_URL = "https://congresosanluis.gob.mx"
    GACETAS_PATH = "/trabajo/trabajo-legislativo/gacetas-parlamentarias"

    def __init__(self, timeout: float = 30.0, client: Optional[httpx.Client] = None):
        self._timeout = timeout
        self._external_client = client

        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _solve_sucuri_challenge(self, html: str) -> Tuple[str, str]:
        """Solves the Sucuri Cloudproxy JS challenge to extract the bypass cookie."""
        # Find the base64 encoded string
        match = re.search(r"S='([^']+)'", html)
        if not match:
            raise ValueError("No se encontró el string base64 del reto Sucuri.")
        
        encoded_js = match.group(1)
        decoded_js = base64.b64decode(encoded_js).decode("utf-8")
        
        # Evaluate simple JS string concatenation like '4' + "d" + String.fromCharCode(50)
        def evaluate_js_string_concat(expr: str) -> str:
            result = ""
            for p in expr.split("+"):
                p = p.strip()
                if p.startswith("'") or p.startswith('"'):
                    result += p[1:-1]
                elif "String.fromCharCode" in p:
                    char_match = re.search(r"\d+", p)
                    if char_match:
                        result += chr(int(char_match.group()))
            return result

        # Extract cookie variable name from document.cookie assignment
        cookie_assign_match = re.search(r'document\.cookie=(.+?)\s*\+\s*"="\s*\+\s*(\w+)', decoded_js)
        if not cookie_assign_match:
            raise ValueError("No se pudo extraer el nombre de la cookie del JS decodificado.")
        
        cookie_name_expr = cookie_assign_match.group(1)
        val_var_name = cookie_assign_match.group(2)

        # Extract value assignment
        val_match = re.search(rf"(?:var\s+)?{val_var_name}=([^;]+);", decoded_js)
        if not val_match:
            raise ValueError(f"No se pudo extraer el valor '{val_var_name}' del JS decodificado.")
        
        u_val = evaluate_js_string_concat(val_match.group(1))
        cookie_name = evaluate_js_string_concat(cookie_name_expr)
        
        return cookie_name, u_val

    def _get(self, url: str) -> httpx.Response:
        """Perform a GET request, SSL verification disabled (common for .gob.mx).
        
        Handles Sucuri Cloudproxy 307 temporary redirects automatically.
        """
        def make_request(client, extra_cookies=None):
            return client.get(url, cookies=extra_cookies)

        cookies = {}
        if self._external_client is not None:
            response = make_request(self._external_client)
            client_used = self._external_client
        else:
            client_used = httpx.Client(
                timeout=self._timeout,
                headers=self._headers,
                verify=False,
                follow_redirects=True,
            )
            response = make_request(client_used)

        # Ensure we close the client only if we created it
        try:
            # Handle Sucuri 307 Redirect JS Challenge
            if response.status_code == 307 and "Sucuri/Cloudproxy" in response.headers.get("Server", ""):
                try:
                    cookie_name, cookie_val = self._solve_sucuri_challenge(response.text)
                    cookies[cookie_name] = cookie_val
                    response = make_request(client_used, extra_cookies=cookies)
                except Exception:
                    pass # Fallback to original raise if solving fails

            response.raise_for_status()
            return response
        finally:
            if self._external_client is None:
                client_used.close()

    def obtener_gacetas(self) -> List[SanLuisGaceta]:
        """Fetch and parse the complete list of Gacetas Parlamentarias.

        A single HTTP request retrieves the entire historical archive
        (Sesiones Ordinarias, Extraordinarias, etc.) from the current and
        past legislatures published on the site.

        Returns:
            List of :class:`SanLuisGaceta`, one per plenary session,
            ordered chronologically (oldest first).
        """
        url = f"{self.BASE_URL}{self.GACETAS_PATH}"
        response = self._get(url)
        return SanLuisParser.parse_gacetas(response.text)
