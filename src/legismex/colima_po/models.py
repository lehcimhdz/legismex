from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class ColimaPoDocumento(BaseModel):
    """Representa un documento o suplemento de una edición del Periódico Oficial de Colima."""
    model_config = ConfigDict(populate_by_name=True)
    titulo: str
    url_descarga: str


class ColimaPoEdicion(BaseModel):
    """Representa un día de publicación en el Periódico Oficial de Colima."""
    model_config = ConfigDict(populate_by_name=True)
    fecha: str
    url_portada: str
    documentos: List[ColimaPoDocumento]
