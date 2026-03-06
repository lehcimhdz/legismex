from typing import List
from pydantic import BaseModel, ConfigDict

class TamaulipasPoDocumento(BaseModel):
    """Representa un documento de la edición (ej. Judicial, Legislativo)."""
    titulo: str
    url_pdf: str

class TamaulipasPoEdicion(BaseModel):
    """Representa un día consolidado del Periódico Oficial de Tamaulipas."""
    model_config = ConfigDict(populate_by_name=True)

    fecha: str
    tomo: str
    numero: str
    documentos: List[TamaulipasPoDocumento]

