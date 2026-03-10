from pydantic import BaseModel, ConfigDict


class VeracruzPoEdicion(BaseModel):
    """Representa una edición de la Gaceta Oficial del Estado de Veracruz."""
    model_config = ConfigDict(populate_by_name=True)

    nombre: str
    fecha_textual: str
    url_pdf: str
