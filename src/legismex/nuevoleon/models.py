from pydantic import BaseModel
from typing import Optional


class NuevoLeonIniciativa(BaseModel):
    """
    Representa una iniciativa de ley extraída del portal del 
    H. Congreso del Estado de Nuevo León.
    """
    expediente: str
    legislatura: str
    promovente: str
    asunto: str
    comision: str
    fecha: str
    estado: str
    url_pdf: Optional[str] = None
