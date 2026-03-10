from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class VeracruzDocumento(BaseModel):
    """Representa un documento anexo a una sesión del Congreso de Veracruz."""
    model_config = ConfigDict(populate_by_name=True)

    titulo: str
    url_pdf: str
    es_anexo: bool = True


class VeracruzSesion(BaseModel):
    """Representa una sesión legislativa (Solemne, Ordinaria, Extraordinaria) del Congreso de Veracruz."""
    fecha: str
    tipo_sesion: str

    # Contexto temporal en la legislatura
    periodo: str
    anio_ejercicio: str

    # Documentos principales
    gaceta_pdf: Optional[str] = None
    acta_pdf: Optional[str] = None
    version_estenografica_pdf: Optional[str] = None

    # Multimedia
    audio_urls: List[str] = Field(default_factory=list)
    video_urls: List[str] = Field(default_factory=list)

    # Anexos vinculados (Leyes, Decretos, Comunicados dentro de la sesión)
    anexos: List[VeracruzDocumento] = Field(default_factory=list)
