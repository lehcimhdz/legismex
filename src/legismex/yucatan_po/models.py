from pydantic import BaseModel, Field

class YucatanPoEdicion(BaseModel):
    """Modelo que representa una edición del Diario Oficial del Estado de Yucatán."""
    fecha: str = Field(description="Fecha de publicación de la edición (ej. 2026-03-09)")
    tipo: str = Field(description="Tipo de la publicación (ej. 'Edición matutina', 'Suplemento', 'Índices generales')")
    numero: str = Field(description="Número de ejemplar (ej. 35,931). Puede ser vacío si es un Índice General")
    url_pdf: str = Field(description="URL absoluta de descarga del archivo PDF íntegro")
    sumario: str = Field(default="", description="Sumario extraído en texto que indica el contenido de la publicación")
