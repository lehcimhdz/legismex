from pydantic import BaseModel, ConfigDict, Field, computed_field
from typing import Optional


class ZacatecasPoPublicacion(BaseModel):
    """Representa una publicación del Periódico Oficial de Zacatecas (POEZ).

    Aplica para Ediciones Ordinarias, Suplementos, Leyes, Reglamentos y Códigos.
    """
    model_config = ConfigDict(populate_by_name=True)

    object_id: str = Field(alias="objectId")
    """Identificador interno (UUID-like) empleado para descargas."""

    fecha_publicacion: str = Field(alias="fechaPublicacion")
    """Fecha de publicación en formato YYYY/MM/DD."""

    # Campos que varían según el tipo
    titulo: Optional[str] = None
    """Título o número del suplemento."""

    descripcion: Optional[str] = None
    """Descripción detallada de la publicación o ley."""

    volumen: Optional[str] = None
    """Volumen de la publicación ordinaria."""

    tomo: Optional[str] = None
    """Tomo de la publicación ordinaria."""

    nombre_archivo: Optional[str] = Field(None, alias="nombre")
    """Nombre del archivo PDF original."""

    @computed_field
    @property
    def url_pdf(self) -> str:
        """URL canónica para descargar el PDF."""
        # Se genera apuntando al endpoint de visualización
        return f"https://periodico.zacatecas.gob.mx/visualizar/{self.object_id}"
