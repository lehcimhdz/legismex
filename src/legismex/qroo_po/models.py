from pydantic import BaseModel, ConfigDict
from datetime import date


class QrooPoPublicacion(BaseModel):
    """Representa una publicación del Periódico Oficial de Quintana Roo."""
    model_config = ConfigDict(populate_by_name=True)

    fecha: date
    tipo: str
    numero: str
    tomo: str
    url_pdf: str
