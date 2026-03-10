from pydantic import BaseModel

class DurangoGaceta(BaseModel):
    """Representa una publicación de la Gaceta del Congreso de Durango."""
    numero: str
    fecha: str
    url_pdf: str
    tipo: str  # "Ordinario" o "Comisión Permanente"
