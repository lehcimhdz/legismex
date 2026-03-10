from datetime import date
from typing import List, Optional
from pydantic import BaseModel


class BcPoEdicion(BaseModel):
    """Representa una edición del Periódico Oficial de Baja California."""
    tomo: str
    numero: str
    fecha: date
    seccion: str
    url_pdf: str


class BcPoResultado(BaseModel):
    """Resultado de búsqueda de ediciones para un periodo específico."""
    anio: int
    mes: Optional[int] = None
    ediciones: List[BcPoEdicion]
