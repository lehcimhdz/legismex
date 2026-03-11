from pydantic import BaseModel, Field
from typing import List, Optional


class DofDocumento(BaseModel):
    """
    Representa un documento individual publicado en la Gaceta (DOF).
    Está agrupado conceptualmente bajo una Sección, Organismo y Dependencia.
    """
    seccion: str = Field(
        description="Sección de la gaceta donde se presentó (ej. UNICA SECCION)")
    organismo: str = Field(
        description="Poder u Organismo Autónomo que publica (ej. PODER EJECUTIVO)")
    dependencia: str = Field(
        description="Secretaría o Entidad específica (ej. SECRETARIA DE GOBERNACION)")
    titulo: str = Field(description="Título o síntesis del decreto o acuerdo")
    url: str = Field(description="URL hacia el documento de la nota detallada")
    url_pdf: Optional[str] = Field(default=None, description="URL directa hacia el PDF del documento (si está disponible)")


class DofEdicion(BaseModel):
    """
    Representa una edición diaria del Diario Oficial de la Federación.
    """
    fecha: str = Field(description="Fecha de la edición")
    documentos: List[DofDocumento] = Field(
        default_factory=list, description="Listado de todos los documentos y decretos publicados")
