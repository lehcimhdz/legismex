from datetime import date
from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class HidalgoDocumento(BaseModel):
    """Representa un documento individual (PDF o ZIP) asociado a una sesión."""
    nombre: str
    url: str
    es_existente: bool = True
    es_zip: bool = False

class HidalgoGaceta(BaseModel):
    """Representa una entrada en el listado de gacetas."""
    session_id: str
    titulo: str
    fecha: date
    tipo: str
    url_detalle: str

class HidalgoGacetaDetalle(BaseModel):
    """Representa el contenido detallado de una sesión específica."""
    session_id: str
    titulo: str
    fecha: date
    documentos: List[HidalgoDocumento]
