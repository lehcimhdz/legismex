import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin
from .models import DurangoGaceta


class DurangoGacetaClient:
    """Cliente para extraer Gacetas de la LXX Legislatura del Congreso de Durango."""

    BASE_URL_ORDINARIO = "https://congresodurango.gob.mx/gacetas-de-la-lxx-legislatura/"
    BASE_URL_PERMANENTE = "https://congresodurango.gob.mx/comision-permanente/"

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "verify": False,
            "follow_redirects": True,
            **kwargs,
        }

    def _parsear_tabla(self, html: str, table_id: str, tipo_gaceta: str, base_url: str) -> List[DurangoGaceta]:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", id=table_id)
        if not table:
            return []

        gacetas = []
        tbody = table.find("tbody")
        if not tbody:
            return []

        for row in tbody.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 3:
                numero = cols[0].get_text(strip=True)
                fecha = cols[1].get_text(strip=True)
                url_pdf = ""

                a_tag = cols[2].find("a")
                if a_tag and "href" in a_tag.attrs:
                    url_pdf = urljoin(base_url, a_tag["href"])

                if numero and url_pdf:
                    gacetas.append(DurangoGaceta(
                        numero=numero,
                        fecha=fecha,
                        url_pdf=url_pdf,
                        tipo=tipo_gaceta
                    ))
        return gacetas

    # --- Síncronos ---

    def obtener_ordinarios(self) -> List[DurangoGaceta]:
        """Obtiene las gacetas del periodo ordinario (tabla tablepress-41)."""
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(self.BASE_URL_ORDINARIO)
            resp.raise_for_status()
            return self._parsear_tabla(resp.text, "tablepress-41", "Ordinario", self.BASE_URL_ORDINARIO)

    def obtener_permanente(self) -> List[DurangoGaceta]:
        """Obtiene las gacetas de la comisión permanente (tabla tablepress-88)."""
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(self.BASE_URL_PERMANENTE)
            resp.raise_for_status()
            return self._parsear_tabla(resp.text, "tablepress-88", "Comisión Permanente", self.BASE_URL_PERMANENTE)

    def obtener_todas(self) -> List[DurangoGaceta]:
        """Obtiene y combina tanto ordinarias como de la permanente."""
        return self.obtener_ordinarios() + self.obtener_permanente()

    # --- Asíncronos ---

    async def a_obtener_ordinarios(self) -> List[DurangoGaceta]:
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(self.BASE_URL_ORDINARIO)
            resp.raise_for_status()
            return self._parsear_tabla(resp.text, "tablepress-41", "Ordinario", self.BASE_URL_ORDINARIO)

    async def a_obtener_permanente(self) -> List[DurangoGaceta]:
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(self.BASE_URL_PERMANENTE)
            resp.raise_for_status()
            return self._parsear_tabla(resp.text, "tablepress-88", "Comisión Permanente", self.BASE_URL_PERMANENTE)

    async def a_obtener_todas(self) -> List[DurangoGaceta]:
        ordinarios, permanentes = await asyncio.gather(
            self.a_obtener_ordinarios(),
            self.a_obtener_permanente()
        )
        return ordinarios + permanentes
