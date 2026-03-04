from pydantic import BaseModel, Field
from typing import List

class QueretaroPoEdicion(BaseModel):
    """
    Representa una edición individual (o un día de publicaciones) del Periódico Oficial del Estado de Querétaro.
    """
    fecha: str = Field(..., description="Fecha de publicación (Ej. 20260303)")
    urls_pdf: List[str] = Field(default_factory=list, description="Lista de URLs a los PDFs que componen la publicación del día")
