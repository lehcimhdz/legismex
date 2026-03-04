import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from .models import GuanajuatoAsunto
import urllib.parse

class GuanajuatoClient:
    BASE_URL = "https://www.congresogto.gob.mx"

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(base_url=self.BASE_URL, verify=False)
        else:
            self._client = client
            if not self._client.base_url or str(self._client.base_url) == "https:///":
                self._client.base_url = httpx.URL(self.BASE_URL)

    def _parse_table(self, html: str, tipo: str) -> List[GuanajuatoAsunto]:
        soup = BeautifulSoup(html, "html.parser")
        asuntos: List[GuanajuatoAsunto] = []
        
        table = soup.find("table", id="dataTable")
        if not table:
            return asuntos

        tbody = table.find("tbody")
        if not tbody:
            return asuntos

        for row in tbody.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 4:
                expediente = cols[0].get_text(strip=True)
                descripcion_col = cols[1]
                
                # Fetch text and potential link
                descripcion = descripcion_col.get_text(strip=True)
                url_detalle = None
                
                a_tag = descripcion_col.find("a")
                if a_tag and a_tag.has_attr("href"):
                    href = a_tag["href"]
                    # Clean URL and make absolute
                    url_detalle = urllib.parse.urljoin(self.BASE_URL, href)

                fecha = cols[2].get_text(strip=True)
                legislatura_text = cols[3].get_text(strip=True)
                
                if "Legislatura" in legislatura_text:
                    legislatura = legislatura_text.replace("Legislatura ", "").strip()
                else:
                    legislatura = legislatura_text
                
                asuntos.append(
                    GuanajuatoAsunto(
                        expediente=expediente,
                        descripcion=descripcion,
                        fecha=fecha,
                        legislatura=legislatura,
                        url_detalle=url_detalle,
                        tipo=tipo
                    )
                )

        return asuntos

    def obtener_iniciativas(self, page: int = 1) -> List[GuanajuatoAsunto]:
        response = self._client.get(f"/gaceta/iniciativas?page={page}")
        response.raise_for_status()
        return self._parse_table(response.text, "iniciativa")


    def obtener_puntos_de_acuerdo(self, page: int = 1) -> List[GuanajuatoAsunto]:
        response = self._client.get(f"/gaceta/puntos-de-acuerdo?page={page}")
        response.raise_for_status()
        return self._parse_table(response.text, "punto_de_acuerdo")
