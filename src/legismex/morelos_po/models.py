from pydantic import BaseModel
from typing import Optional


class MorelosPoEjemplar(BaseModel):
    """An issue of the Morelos Official Gazette (Periódico Oficial)."""
    numero: str
    edicion: str
    fecha_publicacion: str
    url_pdf: str
    sumario: Optional[str] = None
