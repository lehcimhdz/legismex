from pydantic import BaseModel, ConfigDict
from datetime import date


class CampechePoPublicacion(BaseModel):
    """Representa una publicación del Periódico Oficial de Campeche."""
    model_config = ConfigDict(populate_by_name=True)

    titulo: str
    fecha: date
    url_pdf: str
