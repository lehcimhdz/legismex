from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class SonoraPoEdicion(BaseModel):
    """Representa una edición del Periódico Oficial de Sonora."""
    fecha: date
    numero: str
    edicion_tipo: str = Field(
        ..., description="Tipo de edición (Ordinaria, Especial, Sección I, etc.)")
    url_pdf: str
    descripcion: Optional[str] = None


class SonoraPoResultado(BaseModel):
    """Contenedor para resultados de búsqueda de ediciones."""
    anio: int
    mes: Optional[int] = None
    ediciones: List[SonoraPoEdicion]
