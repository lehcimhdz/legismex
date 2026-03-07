from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field

class BcsDocumento(BaseModel):
    """Representa un documento (usualmente PDF) en el portal del Congreso de BCS."""
    titulo: str
    url: str

class BcsSesion(BaseModel):
    """Representa una sesión listada en una categoría de Joomla."""
    titulo: str
    url: str
    fecha: Optional[date] = None

class BcsOrdenDia(BaseModel):
    """Representa el detalle de una Orden del Día."""
    titulo: str
    fecha: Optional[date]
    documentos: List[BcsDocumento] = Field(default_factory=list)

class BcsActa(BaseModel):
    """Representa un Acta de Sesión."""
    titulo: str
    fecha: Optional[date]
    url_pdf: str

class BcsDiario(BaseModel):
    """Representa un Diario de los Debates."""
    titulo: str
    fecha: Optional[date]
    url_pdf: str
