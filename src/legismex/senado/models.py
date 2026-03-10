from pydantic import BaseModel, Field
from typing import List


class DocumentoSenado(BaseModel):
    """
    Representa un documento publicado en la Gaceta del Senado de la República.
    """
    titulo: str = Field(description="Título o síntesis del documento")
    url: str = Field(
        description="URL hacia la publicación detallada o descarga directa")
    categoria: str = Field(
        description="Categoría en la que fue listado (ej. Iniciativas, Proposiciones, etc.)")


class ReferenciaGaceta(BaseModel):
    """
    Referencia a una gaceta histórica extraída del calendario del Senado.
    """
    fecha: str = Field(
        description="Día del mes o título descriptivo de la gaceta")
    url: str = Field(description="Enlace absoluto hacia la gaceta histórica")
    descripcion: str = Field(
        description="Descripción adicional si existe (ej. Sesión #1 del 26 de octubre...)")


class GacetaSenado(BaseModel):
    """
    Concentrado general de una publicación (día) de la Gaceta del Senado.
    """
    titulo_edicion: str = Field(
        description="Título de la Gaceta (ej. Martes 03 de marzo de 2026 / Gaceta: LXVI/2SPO-268)")
    documentos: List[DocumentoSenado] = Field(
        default_factory=list, description="Listado de todos los asuntos y documentos")
