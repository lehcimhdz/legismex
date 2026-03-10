import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from .models import TlaxcalaPoEdicion

# Joomla page slug → actual year for URL construction
# The site uses "2025-2" as the slug for 2026, "2025" for 2025, and "YYYY" for others
_SLUG_MAP = {
    2026: "2025-2",
    2025: "2025",
}


class TlaxcalaPoClient:
    """Client for the Periódico Oficial del Estado de Tlaxcala.

    The Joomla portal at ``periodico.tlaxcala.gob.mx`` embeds an ``<iframe>``
    pointing to ``publicaciones.tlaxcala.gob.mx/indices/YYYY.php`` for each
    year. This client reads those inner pages directly, extracting the plain
    HTML table (Fecha | No | Contenido | PDF) for years 2011–2026.
    """

    BASE_URL = "https://periodico.tlaxcala.gob.mx"
    INDEX_BASE = "https://publicaciones.tlaxcala.gob.mx/indices"

    # Available years in the site menu (oldest first)
    ANIOS = list(range(2011, 2027))  # 2011–2026

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(follow_redirects=True, timeout=30)
        else:
            self._client = client

    def _index_url(self, anio: int) -> str:
        """Return the direct iframe URL for a given year."""
        return f"{self.INDEX_BASE}/{anio}.php"

    def obtener_ediciones(
        self,
        anio: int,
    ) -> List[TlaxcalaPoEdicion]:
        """Fetch all gazette entries for a given year.

        Args:
            anio: Year between 2011 and 2026.

        Returns:
            List of TlaxcalaPoEdicion objects, one per table row.

        Raises:
            ValueError: If the year is out of range.
            httpx.HTTPError: On connection errors.
        """
        if anio not in self.ANIOS:
            raise ValueError(
                f"Año {anio} fuera de rango. Disponibles: {self.ANIOS}")

        url = self._index_url(anio)
        r = self._client.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        results: List[TlaxcalaPoEdicion] = []
        rows = soup.select("table tr")
        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) < 4:
                continue

            fecha = tds[0].get_text(strip=True)
            # Skip header row
            if fecha.lower() in ("fecha", ""):
                continue

            numero = tds[1].get_text(strip=True)
            contenido = tds[2].get_text(strip=True).strip('"').strip()
            a = tds[3].find("a")
            href = a.get("href", "").strip() if a else ""
            url_pdf = f"{self.INDEX_BASE}/{href}" if href else None

            results.append(
                TlaxcalaPoEdicion(
                    anio=anio,
                    fecha=fecha,
                    numero=numero,
                    contenido=contenido,
                    url_pdf=url_pdf,
                )
            )

        return results
