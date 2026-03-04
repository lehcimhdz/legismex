from pydantic import BaseModel
from typing import List, Optional


class GuerreroDocumento(BaseModel):
    """A document within a Guerrero Congressional Gazette."""
    tipo: str
    descripcion: str
    url_pdf: str
    contenido: Optional[str] = None


class GuerreroGaceta(BaseModel):
    """A gazette (session) from the Guerrero State Congress."""
    id: int
    nombre: str
    fecha: str
    url_detalle: str
    documentos: List[GuerreroDocumento] = []
