from pydantic import BaseModel, ConfigDict, Field, computed_field
from typing import List, Optional


class SanLuisPoDocumento(BaseModel):
    """Representa una publicación individual del Periódico Oficial de SLP.

    Puede ser una 'Disposición Oficial' o un 'Aviso Judicial y Diverso'.
    """
    model_config = ConfigDict(populate_by_name=True)

    id: int
    fecha_publicacion: str
    titulo: str
    pdf_filename: str = Field(alias="pdf")

    # Mapeo de niveles orgánicos (generalmente nulos para avisos)
    nivel_gobierno: Optional[str] = None
    segundo: Optional[str] = None
    autoridad_emisora: Optional[str] = None

    es_aviso: bool = False

    @computed_field
    @property
    def url_pdf(self) -> str:
        """URL directa para descarga del archivo."""
        return f"https://periodicooficial.slp.gob.mx/api/publicacion/descargar/guest/{self.id}/documento"


class SanLuisPoEdicion(BaseModel):
    """Concentrado de publicaciones correspondientes a un día específico.

    Contiene un listado de `SanLuisPoDocumento` (Disposiciones y Avisos).
    """
    fecha: str
    documentos: List[SanLuisPoDocumento]
