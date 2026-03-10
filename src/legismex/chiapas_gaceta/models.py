from pydantic import BaseModel
from typing import Optional


class ChiapasGaceta(BaseModel):
    """Representa una publicación de la Gaceta Parlamentaria del H. Congreso del Estado de Chiapas."""
    numero: str
    anio: str
    titulo: str
    periodo: str
    url_pdf: str = ""
    url_flipbook: str = ""
