from pydantic import BaseModel
from typing import Optional

class GuanajuatoAsunto(BaseModel):
    expediente: str
    descripcion: str
    fecha: str
    legislatura: str
    url_detalle: Optional[str] = None
    tipo: str  # 'iniciativa' or 'punto_de_acuerdo'
