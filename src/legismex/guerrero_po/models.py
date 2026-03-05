from pydantic import BaseModel
from typing import Optional


class GuerreroPoPublicacion(BaseModel):
    """A publication from the Guerrero Official Gazette."""
    titulo: str
    fecha: str
    categoria: str
    url_pdf: Optional[str] = None
    url_detalle: Optional[str] = None
