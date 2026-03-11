import httpx
from bs4 import BeautifulSoup
from typing import List
from .models import EdomexGaceta


class EdomexClient:
    """
    Cliente para interactuar con la Gaceta Parlamentaria del Estado de México.
    Extrae la totalidad del archivo histórico directamente de /gacetaanteriores.
    """

    BASE_URL = "https://legislacion.congresoedomex.gob.mx"

    def __init__(self, verify_ssl: bool = False, timeout: float = 30.0):
        # El sitio puede tardar o bloquear sin User-Agent estándar
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers=self.headers,
            timeout=30.0,
            verify=False,
            follow_redirects=True
        )

    def obtener_gacetas(self) -> List[EdomexGaceta]:
        """
        Descarga todos los números de la gaceta parlamentaria publicados 
        durante la legislatura actual desde la sección histórica.
        """
        url = f"{self.BASE_URL}/asuntosparlamentarios/gacetaanteriores"
        response = self.client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        gacetas = []

        anteriores = soup.find_all("div", class_="bloque_ley")
        for prev in anteriores:
            a_tag = prev.find_parent("a")
            pdf_url = a_tag["href"] if a_tag and "href" in a_tag.attrs else ""

            ley_name = prev.find("div", class_="ley_name")
            if ley_name:
                # El HTML tiene un formato muy particular con saltos de linea duros:
                # <span>No. 111 - Año 2</span><br>
                # <b> 27 de \n febrero ... </b>
                span = ley_name.find("span")
                numero = span.get_text(strip=True) if span else ""

                b_tag = ley_name.find("b")
                # Limpiamos los the \n\t y encadenamos con un espacio sencillo
                fecha = ""
                if b_tag:
                    raw_fecha = b_tag.get_text(separator=" ", strip=True)
                    # "27 de febrero, 2026"
                    fecha = " ".join(raw_fecha.split())

                if numero and fecha and pdf_url:
                    gacetas.append(EdomexGaceta(
                        numero=numero,
                        fecha=fecha,
                        url_pdf=pdf_url
                    ))

        return gacetas
