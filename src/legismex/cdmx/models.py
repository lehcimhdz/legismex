from pydantic import BaseModel, Field

class DocumentoCdmx(BaseModel):
    """
    Representa un documento oficial (PDF usualmente) de la Gaceta o Diario de los Debates
    del Congreso de la Ciudad de México.
    """
    titulo: str = Field(description="Título descriptivo del número o la edición completa")
    fecha: str = Field(description="Fecha de la sesión o gaceta")
    peso_kb: float = Field(description="Peso aproximado del archivo en Kilobytes para cálculos matemáticos")
    peso_etiqueta: str = Field(description="Descripción original del peso leída en el portal (ej. '44,490 kb.')")
    url_pdf: str = Field(description="URL absoluta o relativa hacia el archivo para su descarga")
