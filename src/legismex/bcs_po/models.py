from pydantic import BaseModel, Field

class BcsPoEdicion(BaseModel):
    """
    Modelo que representa una edición del Periódico Oficial de Baja California Sur.
    En este estado los boletines se publican en el sitio de la Secretaría de Finanzas.
    """
    fecha: str = Field(description="Fecha de publicación de la edición")
    numero: str = Field(description="Número de la edición del boletín")
    url_pdf: str = Field(description="URL al documento PDF")
