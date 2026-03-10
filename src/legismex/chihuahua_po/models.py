from pydantic import BaseModel, Field
from typing import List, Optional


class ChihuahuaPoEdicion(BaseModel):
    """Representa una publicación del Periódico Oficial del Estado de Chihuahua."""
    titulo: str = Field(
        description="Título o descripción de la edición, e.g. 'Edición Ordinaria No. 19'")
    fecha_iso: str = Field(
        description="Fecha de publicación en formato ISO, e.g. '2025-03-05T12:00:00Z'")
    fecha_legible: str = Field(
        description="Fecha con mes, día y año como aparece en texto, e.g. 'Miércoles, Marzo 5, 2025'")
    url_ejemplar: Optional[str] = Field(
        None, description="URL absoluta al documento PDF del ejemplar principal")
    url_anexos: List[str] = Field(
        default_factory=list, description="Lista de URLs a PDFs de documentos anexos de esta emisión")
