from pydantic import BaseModel, ConfigDict
from typing import Optional

class ColimaDocumentoBase(BaseModel):
    """Clase base de documentos para la legislatura de Colima."""
    model_config = ConfigDict(populate_by_name=True)
    descripcion: str
    url_doc: Optional[str] = None
    url_pdf: Optional[str] = None

class ColimaDecreto(ColimaDocumentoBase):
    """Representa un Decreto."""
    numero: str
    fecha_aprobacion: str
    fecha_publicacion: str

class ColimaAcuerdo(ColimaDocumentoBase):
    """Representa un Acuerdo."""
    numero: str
    fecha_aprobacion: str

class ColimaActa(ColimaDocumentoBase):
    """Representa un Acta o Síntesis."""
    fecha_aprobacion: str
    fecha_publicacion: str

class ColimaDiarioDebate(ColimaDocumentoBase):
    """Representa la versión estenográfica (Diario de los Debates)."""
    fecha: str

class ColimaIniciativa(ColimaDocumentoBase):
    """Representa una Iniciativa."""
    numero: str
    status: str
    autor: Optional[str] = None
    comision: Optional[str] = None
