from typing import Optional
from pydantic import BaseModel, ConfigDict


class TabascoIniciativa(BaseModel):
    """Representa una Iniciativa ingresada al Congreso de Tabasco."""
    model_config = ConfigDict(populate_by_name=True)

    numero: str
    titulo: str
    comision: Optional[str] = None
    presentada_por: Optional[str] = None
    fecha: str
    trimestre: Optional[str] = None
    anio: Optional[int] = None
    url_pdf: str
