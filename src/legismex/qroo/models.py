from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import List, Optional


class QrooDocumento(BaseModel):
    """Representa un documento anexo a una Gaceta de Quintana Roo."""
    model_config = ConfigDict(populate_by_name=True)

    titulo: str
    tipo_doc: str
    url: str


class QrooGaceta(BaseModel):
    """Representa una edición de la Gaceta de Quintana Roo."""
    model_config = ConfigDict(populate_by_name=True)

    id_gaceta: int
    titulo: str
    nomenclatura: str
    fecha_publicacion: date
    extraordinaria: bool
    documentos: List[QrooDocumento] = []
