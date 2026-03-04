from pydantic import BaseModel, Field
from typing import Optional, List

class PueblaPoEdicion(BaseModel):
    """
    Representa una edición individual del Periódico Oficial del Estado de Puebla.
    """
    id_publicacion: str = Field(..., description="ID interno del documento")
    fecha: Optional[str] = Field(None, description="Fecha de publicación (puede no estar presente si la fecha específica no se indexa de inmediato)")
    tomo: Optional[str] = Field(None, description="Tomo de la publicación")
    numero: Optional[str] = Field(None, description="Número de la publicación")
    seccion: Optional[str] = Field(None, description="Sección de la publicación")
    descripcion: str = Field(..., description="Descripción o sumario de la publicación")
    url_pdf: str = Field(..., description="URL absoluta al documento PDF")
    archivo_local: str = Field(..., description="Nombre del archivo originalmente servido")

class PueblaPoPaginacion(BaseModel):
    """
    Representa la respuesta completa de la API con metadatos de paginación.
    """
    cantidad_total: int = Field(0, description="Total de resultados encontrados en la búsqueda")
    ediciones: List[PueblaPoEdicion] = Field(default_factory=list, description="Lista de ediciones devueltas para la página actual")
