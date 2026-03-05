from pydantic import BaseModel
from typing import Literal


class OaxacaPoEdicion(BaseModel):
    """A single edition of the Periódico Oficial del Gobierno del Estado de Oaxaca."""
    tipo: Literal["Ordinario", "Extraordinario", "Secciones"]
    fecha: str        # DD/Mon/YYYY  e.g. "28/Feb/2026"
    nombre: str       # Filename e.g. "ORD09-2026-02-28.pdf"
    url_pdf: str      # Full absolute URL to the PDF
