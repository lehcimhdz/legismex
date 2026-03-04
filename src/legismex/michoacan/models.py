from pydantic import BaseModel
from typing import Optional


class MichoacanGaceta(BaseModel):
    """A single entry from the Gaceta Parlamentaria of Michoacán."""
    fecha: str
    titulo: str
    epoca: Optional[str] = None
    tomo: Optional[str] = None
    numero: Optional[str] = None
    descripcion: str
    url_pdf: Optional[str] = None
    legislatura: Optional[str] = None
