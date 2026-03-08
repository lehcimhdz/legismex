from pydantic import BaseModel, ConfigDict
from typing import Optional


class ZacatecasGaceta(BaseModel):
    """Representa una entrada en la Gaceta Parlamentaria del Congreso de Zacatecas."""
    model_config = ConfigDict(populate_by_name=True)

    tomo: str
    """Tomo de la gaceta (número romano, e.g. 'VI')."""

    numero: str
    """Número de la gaceta dentro del tomo."""

    fecha: str
    """Fecha de la sesión (e.g. '05 de Marzo de 2026')."""

    tipo_sesion: str
    """Tipo de sesión (e.g. 'Sesión Ordinaria', 'Sesión Solemne', 'Sesión Previa')."""

    url_pdf: str
    """URL directa al documento PDF de la gaceta."""

    periodo: Optional[str] = None
    """Periodo legislativo (e.g. 'Segundo periodo ordinario'), cuando está disponible."""

    anio_ejercicio: Optional[str] = None
    """Año de ejercicio constitucional (e.g. 'SEGUNDO AÑO DE EJERCICIO CONSTITUCIONAL')."""
