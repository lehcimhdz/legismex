import httpx
from bs4 import BeautifulSoup
from typing import List

from .models import QueretaroGaceta


class QueretaroClient:
    """
    Cliente para interactuar con el portal de la Legislatura del Estado de Querétaro.
    Extrae la lista completa del repositorio histórico de las Gacetas Legislativas
    publicado a través de tablas generadas por el componente Supsystic de WordPress.
    """

    BASE_URL = "http://legislaturaqueretaro.gob.mx/gacetas-legislativas/"

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def obtener_gacetas(self) -> List[QueretaroGaceta]:
        """
        Extrae todas las Gacetas listadas en el repositorio general.

        Retorna:
            List[QueretaroGaceta]: Lista de objetos Pydantic que representan cada gaceta.
        """
        with httpx.Client(verify=False, timeout=self.timeout, follow_redirects=True) as client:
            response = client.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # En el sitio de Querétaro, las gacetas se pintan en tablas Supsystic Data Tables
        tables = soup.find_all("table", class_="supsystic-table")

        resultados = []

        for table in tables:
            # Generalmente "data-title" contiene la colección como "Gacetas_LXI" o "Gacetas_LX"
            legislatura_tag = table.get("data-title", "Desconocida")

            tbody = table.find("tbody")
            if not tbody:
                continue

            rows = tbody.find_all("tr")

            for row in rows:
                cols = row.find_all("td")

                # Las filas validas tienen 3 columnas (No., Descripción, Archivo)
                if len(cols) >= 3:
                    numero = cols[0].get_text(strip=True)
                    descripcion = cols[1].get_text(strip=True)

                    # Ignorar los "Headers" sueltos que el componente inyecta a veces en las celdas
                    if not numero and not descripcion:
                        continue
                    if descripcion in ["Descripción", "Archivo"] and numero == "No.":
                        continue
                    if not numero and "Legislatura" in descripcion:
                        # Este es un divisor visual
                        continue

                    link_tag = cols[2].find("a")
                    url_pdf = link_tag["href"] if link_tag and link_tag.has_attr(
                        "href") else ""

                    # Requerimos el PDF de forma obligatoria para un registro sensato
                    if not url_pdf:
                        continue

                    gaceta = QueretaroGaceta(
                        legislatura=legislatura_tag,
                        numero=numero,
                        descripcion=descripcion,
                        url_pdf=url_pdf
                    )

                    resultados.append(gaceta)

        return resultados
