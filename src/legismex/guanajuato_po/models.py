from pydantic import BaseModel
from typing import Optional


class GuanajuatoPoEdicion(BaseModel):
    """Represents a single issue (part) of the Periódico Oficial de Guanajuato."""
    perid: int
    fecha: str
    anio: str
    numero: int
    parte: int
    descripcion: str
    url_pdf: str
    inciso: Optional[str] = None
    total_sumarios: int = 0
