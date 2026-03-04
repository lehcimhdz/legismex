from pydantic import BaseModel
from typing import Optional


class MichoacanPoCategoria(BaseModel):
    """A category node (year, month, or day) in the WP-Filebase tree."""
    cat_id: int
    nombre: str
    tiene_hijos: bool = False


class MichoacanPoArchivo(BaseModel):
    """A single file (PDF) in the Michoacán Periódico Oficial archive."""
    file_id: int
    nombre: str
    url_pdf: str
    anio: Optional[str] = None
    mes: Optional[str] = None
    dia: Optional[str] = None
