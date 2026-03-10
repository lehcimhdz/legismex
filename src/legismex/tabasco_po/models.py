from typing import Optional
from pydantic import BaseModel, ConfigDict


class TabascoPoPublicacion(BaseModel):
    """Representa una publicación del Periódico Oficial de Tabasco."""
    model_config = ConfigDict(populate_by_name=True)

    fecha: str
    numero: str
    tipo: str
    suplemento: Optional[str] = None
    descripcion: str
    url_pdf: str
