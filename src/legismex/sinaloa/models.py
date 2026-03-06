from pydantic import BaseModel, ConfigDict
from typing import Optional


class SinaloaIniciativa(BaseModel):
    """Representa una iniciativa legislativa del H. Congreso del Estado de Sinaloa."""
    model_config = ConfigDict(populate_by_name=True)

    id: int
    """Identificador único de la iniciativa."""

    fecha: Optional[str] = None
    """Fecha de presentación (formato: 'DD/mes/YYYY')."""

    iniciativa: Optional[str] = None
    """Descripción o título de la iniciativa."""

    presentada: Optional[str] = None
    """Autor o promovente de la iniciativa."""

    ratificada: Optional[str] = None
    """Número de ratificación, si aplica."""

    objetivo: Optional[str] = None
    """Objetivo de la iniciativa."""

    leyes: Optional[str] = None
    """Leyes referenciadas."""

    determinacion: Optional[str] = None
    """Fecha o texto de la determinación."""

    pdf: Optional[bool] = None
    """Si existe un PDF adjunto."""

    legis: Optional[str] = None
    """Número de legislatura (ej. '65')."""

    estatus: Optional[str] = None
    """Estatus de la iniciativa."""

    nb_tipo: Optional[str] = None
    """Tipo de proponente (ej. 'diputado', 'ejecutivo')."""


class SinaloaDictamen(BaseModel):
    """Representa un dictamen del H. Congreso del Estado de Sinaloa."""
    model_config = ConfigDict(populate_by_name=True)

    id: int
    fecha: Optional[str] = None
    asunto: Optional[str] = None
    """Descripción del dictamen."""
    pdf: Optional[bool] = None
    legis: Optional[str] = None


class SinaloaAcuerdo(BaseModel):
    """Representa un acuerdo del H. Congreso del Estado de Sinaloa."""
    model_config = ConfigDict(populate_by_name=True)

    id: int
    fecha: Optional[str] = None
    asunto: Optional[str] = None
    """Descripción del acuerdo."""
    pdf: Optional[bool] = None
    dictamen: Optional[str] = None
    """ID del dictamen relacionado."""
    votacion: Optional[bool] = None
    """Si existe documento de votación."""
    legis: Optional[str] = None


class SinaloaDecreto(BaseModel):
    """Representa un decreto del H. Congreso del Estado de Sinaloa."""
    model_config = ConfigDict(populate_by_name=True)

    id: int
    fecha: Optional[str] = None
    asunto: Optional[str] = None
    """Descripción del decreto."""
    pdf: Optional[bool] = None
    pdfvoto: Optional[bool] = None
    """Si existe PDF de votación."""
    pdfobservacion: Optional[bool] = None
    """Si existe PDF de observación del Ejecutivo."""
    legis: Optional[str] = None


class SinaloaLegislatura(BaseModel):
    """Representa una legislatura disponible."""
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    """Número de legislatura (ej. '65')."""

    nombre: Optional[str] = None
    """Nombre de la legislatura (ej. 'LXV Legislatura')."""

