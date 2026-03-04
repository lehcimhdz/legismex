from pydantic import BaseModel
from typing import List, Optional

class EdomexPoDocumento(BaseModel):
    seccion: str
    titulo: str
    url_pdf: str

class EdomexPoEdicion(BaseModel):
    fecha: str
    url_completa: Optional[str] = None
    documentos: List[EdomexPoDocumento]
