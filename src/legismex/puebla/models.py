from pydantic import BaseModel, HttpUrl
from typing import Optional

class PueblaGaceta(BaseModel):
    """Modelo para representar un documento de Gaceta Legislativa del Congreso de Puebla."""
    mes: str
    numero: str
    fecha_texto: str
    url_pdf: HttpUrl
    legislatura: str = "LXII"
    anio_legislativo: Optional[str] = None
