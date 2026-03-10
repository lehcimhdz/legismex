from pydantic import BaseModel
from typing import List


class NuevoLeonPoEdicion(BaseModel):
    """
    Representa una edición publicada del Periódico Oficial del Estado de Nuevo León.
    """
    numero: str
    fecha: str
    urls_pdf: List[str]
