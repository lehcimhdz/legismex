from pydantic import BaseModel, Field
from typing import List, Optional

class ChihuahuaDocumento(BaseModel):
    """Representa un documento o apartado dentro de la sesión de Chihuahua."""
    titulo: str = Field(description="Título del rubro (ej. 'Puntos del orden del día', 'Iniciativas presentadas')")
    url: str = Field(description="URL absoluta al detalle de los documentos o rubro (ej. 'https://www.congresochihuahua.gob.mx/detalleSesion.php?idsesion=2100&tipo=documento&id=&idtipodocumento=1')")

class ChihuahuaSesion(BaseModel):
    """Representa una sesión publicada en la Gaceta Parlamentaria de Chihuahua."""
    sesion_id: str = Field(description="ID interno de la sesión en el portal del Congreso")
    titulo: str = Field(description="Título superior, ej. 'Gaceta 151 - LXVIII - II Año - I P.O.'")
    descripcion: str = Field(description="Descripción larga de la sesión, ej. 'Sesión Ordinaria del Segundo Periodo...'")
    fecha: str = Field(description="Fecha extraída del bloque, ej. '10 de marzo de 2026'")
    url_video: Optional[str] = Field(default=None, description="Enlace al video de Youtube asociado a la sesión")
    url_asistencia: Optional[str] = Field(default=None, description="URL absoluta al documento de pase de lista o asistencia")
    
    documentos_probables: List[ChihuahuaDocumento] = Field(default_factory=list, description="Documentos listados en 'Orden del día probable'")
    documentos_desahogados: List[ChihuahuaDocumento] = Field(default_factory=list, description="Documentos listados en 'Orden del día desahogado'")
    documentos_votacion: List[ChihuahuaDocumento] = Field(default_factory=list, description="Documentos listados en 'Registro y votación de los asuntos desahogados'")
    asuntos_turnados: List[ChihuahuaDocumento] = Field(default_factory=list, description="Documentos listados en 'Asuntos turnados'")
