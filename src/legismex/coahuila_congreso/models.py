from pydantic import BaseModel, Field
from typing import Optional


class CoahuilaIniciativa(BaseModel):
    """Representa una iniciativa extraída del Congreso de Coahuila."""
    fecha: str = Field(description="Fecha de presentación, e.g. '02/03/2026'")
    origen: str = Field(description="Origen de la iniciativa, e.g. 'Diputado'")
    ponente: str = Field(description="Nombre o lista de ponentes")
    descripcion: str = Field(
        description="Descripción o título de la iniciativa")
    legislatura: str = Field(
        description="Legislatura correspondiente, e.g. 'LXIII'")
    anio_legislativo: str = Field(description="Año legislativo, e.g. '2026'")
    url_pdf: Optional[str] = Field(
        None, description="Enlace al documento base en formato PDF")
    url_abierto: Optional[str] = Field(
        None, description="Enlace al documento base en formato abierto (DOCX)")
