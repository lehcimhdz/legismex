from typing import List, Optional
from pydantic import BaseModel, Field


class JaliscoDocumento(BaseModel):
    titulo: str = Field(
        description="Título o descripción del documento adjunto")
    url: str = Field(description="URL al documento (PDF, DOCX, etc.)")


class JaliscoPunto(BaseModel):
    titulo: str = Field(
        description="Descripción del punto en el orden del día")
    documentos: List[JaliscoDocumento] = Field(
        default_factory=list, description="Documentos vinculados a este punto")


class JaliscoEvento(BaseModel):
    fecha: str = Field(description="Fecha del evento en formato YYYY-MM-DD")
    titulo: str = Field(description="Título descriptivo de la sesión")
    tipo: int = Field(
        description="Código del tipo de evento (1=Pleno, 2=Comisión, etc.)")
    id_evento: int = Field(description="ID interno del evento en Jalisco")
    puntos_orden: List[JaliscoPunto] = Field(
        default_factory=list, description="Puntos agendados para este evento")
