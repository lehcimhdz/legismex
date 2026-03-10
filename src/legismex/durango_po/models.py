from pydantic import BaseModel
from typing import List

class DurangoPoEdicion(BaseModel):
    """Representa una publicación del Periódico Oficial del Estado de Durango."""
    uuid: str
    titulo: str
    fecha: str
    cantidad_publicaciones: str
    url_pdf: str = ""
    es_bis: bool = False
    es_extraordinario: bool = False
