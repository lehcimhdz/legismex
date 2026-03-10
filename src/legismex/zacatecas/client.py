import httpx
from bs4 import BeautifulSoup
from typing import List, Optional

from .models import ZacatecasGaceta

_BASE = "https://www.congresozac.gob.mx"
_GACETA_URL = f"{_BASE}/65/gaceta"


def _build_url(mes: Optional[str]) -> str:
    """Construye la URL para el mes indicado.

    Args:
        mes: Mes en formato ``MMYYYY`` (e.g. ``'032026'``).
             ``None`` para el mes actual.
    """
    if mes:
        return f"{_GACETA_URL}&mes={mes}"
    return _GACETA_URL


def _parse_gacetas(html: str) -> List[ZacatecasGaceta]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    gacetas: List[ZacatecasGaceta] = []
    periodo_actual: Optional[str] = None

    # Extraer el año de ejercicio (header arriba de la tabla)
    # Ejemplo: SEGUNDO AÑO DE EJERCICIO CONSTITUCIONAL
    anio_tag = soup.find("font", color="#424242")
    anio_ejercicio = anio_tag.get_text(strip=True) if anio_tag else None

    for tr in table.find_all("tr")[1:]:  # saltar encabezado
        cells = tr.find_all(["td", "th"])
        if len(cells) < 6:
            continue

        periodo_txt = cells[0].get_text(strip=True)
        if periodo_txt:
            periodo_actual = periodo_txt

        tomo = cells[1].get_text(strip=True)
        numero = cells[2].get_text(strip=True)
        fecha = cells[3].get_text(strip=True)

        # Tipo de sesión — el texto del enlace en la columna 4
        tipo_link = cells[4].find("a")
        tipo_sesion = tipo_link.get_text(
            strip=True) if tipo_link else cells[4].get_text(strip=True)

        # PDF — enlace en la columna 5 (botón rojo)
        pdf_link = cells[5].find("a", href=True)
        if not pdf_link:
            continue
        href = pdf_link["href"]
        url_pdf = href if href.startswith("http") else f"{_BASE}{href}"

        if not tomo and not numero:
            continue

        gacetas.append(
            ZacatecasGaceta(
                tomo=tomo,
                numero=numero,
                fecha=fecha,
                tipo_sesion=tipo_sesion.rstrip(),
                url_pdf=url_pdf,
                periodo=periodo_actual,
                anio_ejercicio=anio_ejercicio,
            )
        )

    return gacetas


def _parse_meses(html: str) -> List[str]:
    """Extrae los identificadores de mes disponibles (formato MMYYYY)."""
    soup = BeautifulSoup(html, "html.parser")
    meses: List[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "&mes=" in href:
            mes = href.split("&mes=")[-1]
            if mes not in meses:
                meses.append(mes)
    return meses


class ZacatecasClient:
    """Cliente para la Gaceta Parlamentaria del Congreso del Estado de Zacatecas (LXV Legislatura).

    Raspa ``congresozac.gob.mx/65/gaceta`` extrayendo las gacetas por mes.
    Cada entrada incluye tomo, número, fecha, tipo de sesión y enlace al PDF.

    Ejemplo síncrono::

        from legismex import ZacatecasClient

        client = ZacatecasClient()
        gacetas = client.obtener_gacetas()          # mes actual
        gacetas = client.obtener_gacetas("022026")  # Febrero 2026

        for g in gacetas:
            print(g.numero, g.fecha, g.tipo_sesion, g.url_pdf)

    Ejemplo asíncrono::

        import asyncio
        from legismex import ZacatecasClient

        async def main():
            client = ZacatecasClient()
            gacetas = await client.a_obtener_gacetas()
            for g in gacetas:
                print(g.numero, g.fecha, g.url_pdf)

        asyncio.run(main())

    Para listar todos los meses disponibles::

        meses = client.obtener_meses()
        # ['032026', '022026', '012026', ...]
    """

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "follow_redirects": True,
            "verify": False,
            **kwargs,
        }

    # ------------------------------------------------------------------
    # API síncrona
    # ------------------------------------------------------------------

    def obtener_gacetas(self, mes: Optional[str] = None) -> List[ZacatecasGaceta]:
        """Descarga y parsea las gacetas del mes indicado.

        Args:
            mes: Mes en formato ``MMYYYY`` (e.g. ``'032026'``).
                 Si se omite, devuelve el mes actual publicado en la portada.

        Returns:
            Lista de :class:`ZacatecasGaceta` ordenada de más reciente a más antigua.
        """
        url = _build_url(mes)
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return _parse_gacetas(resp.text)

    def obtener_meses(self) -> List[str]:
        """Devuelve la lista de meses disponibles en formato ``MMYYYY``.

        Returns:
            Lista de strings como ``['032026', '022026', ...]`` de más reciente a más antigua.
        """
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(_GACETA_URL)
            resp.raise_for_status()
            return _parse_meses(resp.text)

    # ------------------------------------------------------------------
    # API asíncrona
    # ------------------------------------------------------------------

    async def a_obtener_gacetas(self, mes: Optional[str] = None) -> List[ZacatecasGaceta]:
        """Versión asíncrona de :meth:`obtener_gacetas`.

        Args:
            mes: Mes en formato ``MMYYYY``. Si se omite, devuelve el mes actual.

        Returns:
            Lista de :class:`ZacatecasGaceta`.
        """
        url = _build_url(mes)
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return _parse_gacetas(resp.text)

    async def a_obtener_meses(self) -> List[str]:
        """Versión asíncrona de :meth:`obtener_meses`."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(_GACETA_URL)
            resp.raise_for_status()
            return _parse_meses(resp.text)
