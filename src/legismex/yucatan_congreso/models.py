from pydantic import BaseModel, Field
from typing import List


class YucatanDocumento(BaseModel):
    """Modelo que representa un documento adjunto a una iniciativa."""
    url: str = Field(description="URL absoluta de descarga del documento")
    extension: str = Field(
        description="Extensión detectada del documento (ej. 'pdf', 'docx')")


class YucatanIniciativa(BaseModel):
    """Modelo que representa una iniciativa presentada en el Congreso de Yucatán."""
    legislatura: str = Field(
        description="Legislatura en la que se presentó la iniciativa (ej. LXIV)")
    descripcion: str = Field(
        description="Título o descripción del contenido de la iniciativa")
    fecha_presentada: str = Field(
        description="Fecha original en la que se promovió la iniciativa")
    presentada_por: str = Field(
        description="Servidor público, grupo o ciudadano promovente")
    fecha_turnada: str = Field(
        description="Fecha en la que fue enviada a la respectiva comisión")
    comision_permanente: str = Field(
        description="Comisión principal asignada para el dictamen")
    documentos: List[YucatanDocumento] = Field(
        description="Lista de documentos anexos localizados")
