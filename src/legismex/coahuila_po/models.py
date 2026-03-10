from pydantic import BaseModel, Field
from typing import Optional

class CoahuilaPoEdicion(BaseModel):
    """Representa una publicación del Periódico Oficial del Estado de Coahuila."""
    fecha_publicacion: str = Field(description="Fecha con mes, día y año como aparece en texto")
    tomo: str = Field(description="Tomo en números romanos, e.g. CXXXIII")
    numero: str = Field(description="Número de la publicación")
    tipo: str = Field(description="Clase de publicación, e.g. Ordinario, Sección 1, etc.")
    sumario: str = Field(description="Resumen o listado de contenido de la publicación")
    url_pdf: Optional[str] = Field(None, description="URL absoluta al documento PDF del ejemplar")
    id_sumario: Optional[str] = Field(None, description="ID interno referente al índice sumario")
