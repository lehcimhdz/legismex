import asyncio
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from .models import TabascoIniciativa


class TabascoIniciativasClient:
    """Cliente para extraer las Iniciativas del portal web del Congreso del Estado de Tabasco."""
    BASE_URL = "https://congresotabasco.gob.mx/iniciativas/"

    def __init__(self, **kwargs):
        """
        Inicializa el cliente de Iniciativas Tabasco.

        Args:
            **kwargs: Argumentos adicionales para httpx.Client o AsyncClient,
                como timeouts, verificación SSL, proxies, etc.
        """
        self.client_kwargs = {
            "timeout": 35.0,
            "verify": False,
            "follow_redirects": True,
            **kwargs,
        }

    def _parsear_html(self, html: str, anio_filtro: Optional[int] = None, mes_filtro: Optional[int] = None) -> List[TabascoIniciativa]:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        if not table:
            return []

        tbody = table.find("tbody")
        if not tbody:
            return []

        iniciativas: List[TabascoIniciativa] = []
        rows = tbody.find_all("tr")

        for row in rows:
            tds = row.find_all("td")
            if len(tds) < 8:
                continue

            numero = tds[0].get_text(strip=True)
            titulo = tds[1].get_text(strip=True)
            comision = tds[2].get_text(strip=True)
            presentada_por = tds[3].get_text(strip=True)
            fecha = tds[4].get_text(strip=True)
            trimestre = tds[5].get_text(strip=True)

            anio_str = tds[6].get_text(strip=True)
            anio = int(anio_str) if anio_str.isdigit() else None

            a_tag = tds[7].find("a")
            url_pdf = a_tag["href"] if a_tag else ""

            # Filtro opcional local
            if anio_filtro and anio != anio_filtro:
                continue

            if mes_filtro and fecha:
                # fecha asume formato dd/mm/yyyy
                fecha_parts = fecha.split("/")
                if len(fecha_parts) == 3:
                    mes_fila = int(fecha_parts[1])
                    if mes_fila != mes_filtro:
                        continue

            iniciativa = TabascoIniciativa(
                numero=numero,
                titulo=titulo,
                comision=comision if comision else None,
                presentada_por=presentada_por if presentada_por else None,
                fecha=fecha,
                trimestre=trimestre if trimestre else None,
                anio=anio,
                url_pdf=url_pdf
            )
            iniciativas.append(iniciativa)

        return iniciativas

    def obtener_iniciativas(
        self,
        anio: Optional[int] = None,
        mes: Optional[int] = None
    ) -> List[TabascoIniciativa]:
        """
        Obtiene las iniciativas del portal web de forma síncrona.
        Tarda unos segundos en renderizar la gran tabla que contiene los registros estáticos.

        Args:
            anio: Filtro opcional por año (ej. 2024).
            mes: Filtro opcional por mes (ej. 12).

        Returns:
            List[TabascoIniciativa]: Todos los registros encontrados en la tabla acorde a los filtros.
        """
        import warnings
        # Desactivando el advertencia de recurso InsecureRequestWarning solo para Tabasco
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with httpx.Client(**self.client_kwargs) as client:
                response = client.get(self.BASE_URL)
                response.raise_for_status()

                return self._parsear_html(response.text, anio_filtro=anio, mes_filtro=mes)

    async def a_obtener_iniciativas(
        self,
        anio: Optional[int] = None,
        mes: Optional[int] = None
    ) -> List[TabascoIniciativa]:
        """
        Obtiene las iniciativas del portal web de forma asíncrona.

        Args:
            anio: Filtro opcional por año (ej. 2024).
            mes: Filtro opcional por mes (ej. 12).

        Returns:
            List[TabascoIniciativa]: Todos los registros encontrados en la tabla acorde a los filtros.
        """
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            async with httpx.AsyncClient(**self.client_kwargs) as client:
                response = await client.get(self.BASE_URL)
                response.raise_for_status()

                return self._parsear_html(response.text, anio_filtro=anio, mes_filtro=mes)
