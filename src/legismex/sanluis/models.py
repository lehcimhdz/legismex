from pydantic import BaseModel
from typing import List


class SanLuisGaceta(BaseModel):
    """Gaceta Parlamentaria del Congreso del Estado de San Luis Potosí.

    Each instance represents one plenary session with its associated PDF files.

    Attributes:
        mes:         Human-readable month/year label, e.g. ``"Septiembre, 2015"``.
        nombre:      Session name, e.g. ``"Sesión Ordinaria No. 1"``.
        fecha_iso:   ISO-8601 datetime string from the Drupal ``content`` attr,
                     e.g. ``"2015-09-17T11:00:00-05:00"``. Empty string if absent.
        fecha_texto: Localised label, e.g.
                     ``"Jueves, Septiembre 17, 2015 - 11:00"``.
        urls_pdf:    Ordered list of direct PDF URLs for this session (1 – N).
    """

    mes: str
    nombre: str
    fecha_iso: str
    fecha_texto: str
    urls_pdf: List[str]
