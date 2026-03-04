import httpx
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from .models import MichoacanPoArchivo, MichoacanPoCategoria


class MichoacanPoClient:
    """Client for the Periódico Oficial del Estado de Michoacán.

    Navigates the WP-Filebase AJAX tree at periodicooficial.michoacan.gob.mx
    to list years, months, days, and individual gazette PDFs.  The archive
    spans from 1955 to the present.
    """

    BASE_URL = "https://periodicooficial.michoacan.gob.mx"
    AJAX_URL = f"{BASE_URL}/?wpfilebase_ajax=1"

    def __init__(self, client: Optional[httpx.Client] = None):
        if client is None:
            self._client = httpx.Client(follow_redirects=True, timeout=30)
        else:
            self._client = client

    def _fetch_tree(self, base: int = 0) -> list:
        """Fetch children of a tree node via the WP-Filebase AJAX endpoint."""
        response = self._client.post(
            self.AJAX_URL,
            data={"wpfb_action": "tree", "type": "browser", "base": str(base)},
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _parse_name(html: str) -> str:
        """Extract the display name from a WP-Filebase node's HTML."""
        soup = BeautifulSoup(html, "html.parser")
        link = soup.find("a")
        return link.get_text(strip=True) if link else ""

    @staticmethod
    def _parse_url(html: str) -> str:
        """Extract the URL from a WP-Filebase file node."""
        soup = BeautifulSoup(html, "html.parser")
        link = soup.find("a")
        return link.get("href", "") if link else ""

    def obtener_anios(self) -> List[MichoacanPoCategoria]:
        """List all available years in the archive.

        Returns:
            Sorted list of year categories (most recent first).
        """
        nodes = self._fetch_tree(0)
        years: List[MichoacanPoCategoria] = []
        for node in nodes:
            if node.get("type") != "cat":
                continue
            cat_id = node.get("cat_id")
            if cat_id is None or cat_id == 0:
                continue
            name = self._parse_name(node.get("text", ""))
            if not name.isdigit():
                continue
            year_int = int(name)
            if year_int < 1900 or year_int > 2100:
                continue
            years.append(
                MichoacanPoCategoria(
                    cat_id=int(cat_id),
                    nombre=name,
                    tiene_hijos=node.get("hasChildren", False),
                )
            )
        years.sort(key=lambda y: int(y.nombre), reverse=True)
        return years

    def obtener_meses(self, cat_id_anio: int) -> List[MichoacanPoCategoria]:
        """List months available within a year category.

        Args:
            cat_id_anio: The cat_id of the year (from obtener_anios).
        """
        nodes = self._fetch_tree(cat_id_anio)
        months: List[MichoacanPoCategoria] = []
        for node in nodes:
            if node.get("type") != "cat":
                continue
            cid = node.get("cat_id")
            if cid is None or cid == 0:
                continue
            name = self._parse_name(node.get("text", ""))
            months.append(
                MichoacanPoCategoria(
                    cat_id=int(cid),
                    nombre=name,
                    tiene_hijos=node.get("hasChildren", False),
                )
            )
        return months

    def obtener_dias(self, cat_id_mes: int) -> List[MichoacanPoCategoria]:
        """List days available within a month category.

        Args:
            cat_id_mes: The cat_id of the month (from obtener_meses).
        """
        return self.obtener_meses(cat_id_mes)  # same structure

    def obtener_archivos(
        self,
        cat_id: int,
        anio: Optional[str] = None,
        mes: Optional[str] = None,
        dia: Optional[str] = None,
    ) -> List[MichoacanPoArchivo]:
        """List PDF files inside a given category (day or month).

        This method returns only file nodes at the given level.  If the
        category still contains sub-categories (months or days), those
        are skipped — use obtener_meses / obtener_dias to descend first.

        Args:
            cat_id: Category ID to list files from.
            anio: Optional year label for metadata.
            mes: Optional month label for metadata.
            dia: Optional day label for metadata.
        """
        nodes = self._fetch_tree(cat_id)
        files: List[MichoacanPoArchivo] = []
        for node in nodes:
            fid = node.get("file_id")
            if fid is None:
                continue
            name = self._parse_name(node.get("text", ""))
            url = self._parse_url(node.get("text", ""))
            files.append(
                MichoacanPoArchivo(
                    file_id=int(fid),
                    nombre=name,
                    url_pdf=url,
                    anio=anio,
                    mes=mes,
                    dia=dia,
                )
            )
        return files

    def obtener_archivos_por_fecha(
        self, anio: int, mes: Optional[str] = None
    ) -> List[MichoacanPoArchivo]:
        """Convenience method: list all PDFs for a year (or year+month).

        Args:
            anio: Year to search (e.g. 2025).
            mes: Optional month name in Spanish (e.g. "Enero").

        Returns:
            List of all PDF files found, descending to the day level.
        """
        years = self.obtener_anios()
        year_cat = next(
            (y for y in years if y.nombre == str(anio)), None
        )
        if year_cat is None:
            return []

        months = self.obtener_meses(year_cat.cat_id)
        if mes:
            months = [
                m for m in months
                if m.nombre.lower() == mes.lower()
            ]

        all_files: List[MichoacanPoArchivo] = []
        for month in months:
            days = self.obtener_dias(month.cat_id)
            for day in days:
                files = self.obtener_archivos(
                    day.cat_id,
                    anio=str(anio),
                    mes=month.nombre,
                    dia=day.nombre,
                )
                all_files.extend(files)
            # Also check for files directly under the month (no day sub-folder)
            direct = self.obtener_archivos(
                month.cat_id,
                anio=str(anio),
                mes=month.nombre,
            )
            all_files.extend(direct)

        return all_files
