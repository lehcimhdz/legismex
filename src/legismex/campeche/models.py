from typing import Optional
from pydantic import BaseModel, ConfigDict


class CampecheGaceta(BaseModel):
    """Representa un documento de la Gaceta Parlamentaria del Congreso del Estado de Campeche."""
    model_config = ConfigDict(populate_by_name=True)

    titulo: str
    legislatura: str
    url_pdf: str
