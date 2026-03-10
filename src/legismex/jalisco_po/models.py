from pydantic import BaseModel
from typing import Optional, List


class JaliscoPoResumen(BaseModel):
    """
    Representa una previsualización de una gaceta o publicación
    del Periódico Oficial del Estado de Jalisco al listarlos en el buscador.
    """
    id_newspaper: int
    date_newspaper: str
    tomo: Optional[str] = None
    number: Optional[str] = None
    description: str
    section: Optional[str] = None
    special: bool = False
    special_description: Optional[str] = None


class JaliscoPoEdicion(BaseModel):
    """
    Representa la edición completa y en detalle de una publicación,
    incluyendo de forma directa los URLs absolutos a sus PDFs.
    """
    id: int
    post_date: str
    volume: Optional[str] = None
    number: Optional[str] = None
    description: str
    section: Optional[str] = None
    special: bool = False
    special_description: Optional[str] = None
    link: Optional[str] = None
    print_link: Optional[str] = None


class JaliscoPoPaginacion(BaseModel):
    items: List[JaliscoPoResumen]
    current_page: int
    last_page: int
    total: int
