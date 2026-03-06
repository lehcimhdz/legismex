from pydantic import BaseModel, ConfigDict
from typing import Optional


class NayaritIniciativa(BaseModel):
    """Representa una iniciativa legislativa del H. Congreso del Estado de Nayarit."""
    model_config = ConfigDict(populate_by_name=True)

    numero: int
    """Número de la iniciativa dentro de la legislatura."""

    fecha_recepcion: str
    """Fecha en la que fue recibida la iniciativa (DD/MM/YYYY)."""

    origen: str
    """Diputado, Ejecutivo, Poder Judicial o Ayuntamiento que presenta la iniciativa."""

    anio_legislatura: str
    """Año de la legislatura al que pertenece (Primero, Segundo, Tercero)."""

    periodo: str
    """Periodo ordinario en que fue presentada."""

    descripcion: str
    """Descripción completa del objeto de la iniciativa."""

    url_pdf: Optional[str] = None
    """URL directa al documento PDF de la iniciativa."""

    fecha_pleno: Optional[str] = None
    """Fecha en que se presentó en el Pleno (DD/MM/YYYY), si aplica."""

    turno_comision: Optional[str] = None
    """Comisión o comisiones a las que fue turnada."""

    dictamen: Optional[str] = None
    """Estado del dictamen: 'Resuelta', 'En estudio', etc."""

    legislatura: Optional[str] = None
    """Designación romana de la legislatura (e.g., 'XXXIV')."""
