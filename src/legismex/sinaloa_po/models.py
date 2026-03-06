from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import re
from html.parser import HTMLParser


class _TextExtractor(HTMLParser):
    """Parser mínimo para extraer texto plano de un fragmento HTML."""

    def __init__(self):
        super().__init__()
        self._chunks: List[str] = []

    def handle_data(self, data: str):
        data = data.strip()
        if data:
            self._chunks.append(data)

    def get_text(self) -> str:
        return " ".join(self._chunks)


def _extract_pdf_url(html: str) -> Optional[str]:
    """Extrae la primera URL a un archivo PDF del HTML de descripción."""
    match = re.search(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', html, re.IGNORECASE)
    if match:
        return match.group(1)
    # A veces el PDF está en un link "Descargar Archivo" sin extensión .pdf
    match = re.search(r'href=["\']([^"\']*media\.transparencia[^"\']+)["\']', html, re.IGNORECASE)
    return match.group(1) if match else None


def _plain_index(html: str) -> str:
    """Devuelve el índice en texto plano (sin etiquetas HTML)."""
    extractor = _TextExtractor()
    extractor.feed(html)
    return extractor.get_text()


class SinaloaPoEdicion(BaseModel):
    """Representa una edición del Periódico Oficial del Estado de Sinaloa (POES).

    La fuente es el sitio ``strc.transparenciasinaloa.gob.mx/poes/``, que usa
    WordPress + *The Events Calendar* plugin. Cada edición es un «evento» con
    fecha de publicación, número de edición, índice y un PDF descargable.
    """
    model_config = ConfigDict(populate_by_name=True)

    id: int
    """ID interno del evento en WordPress."""

    titulo: str
    """Número de edición, ej. ``'POE No.028'`` o ``'POE No.001 Vesp.'``."""

    slug: str
    """Slug de la URL del evento, ej. ``'poe-no-028-25'``."""

    url: str
    """URL canónica de la edición en el sitio web."""

    fecha: str
    """Fecha de publicación en formato ``'YYYY-MM-DD'``."""

    vespertina: bool = False
    """``True`` si es una edición vespertina."""

    indice_html: Optional[str] = None
    """Descripción HTML completa (incluye el índice de la edición)."""

    indice: Optional[str] = None
    """Índice en texto plano extraído del HTML."""

    pdf_url: Optional[str] = None
    """URL directa al PDF de la edición. Extraída del HTML de descripción."""

    @classmethod
    def from_api(cls, data: dict) -> "SinaloaPoEdicion":
        """Construye una instancia a partir del dict devuelto por la API."""
        titulo: str = data.get("title", "")
        html: str = data.get("description", "") or ""
        fecha_raw: str = data.get("start_date", "")
        fecha = fecha_raw[:10] if fecha_raw else ""
        return cls(
            id=data["id"],
            titulo=titulo,
            slug=data.get("slug", ""),
            url=data.get("url", ""),
            fecha=fecha,
            vespertina="vesp" in titulo.lower(),
            indice_html=html or None,
            indice=_plain_index(html) if html else None,
            pdf_url=_extract_pdf_url(html) if html else None,
        )
