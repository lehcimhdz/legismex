from pydantic import BaseModel, field_validator
from typing import List, Optional, Union


class AgsPoEdicion(BaseModel):
    """A single edition (section) of the Periódico Oficial del Estado de Aguascalientes.

    The POE is published as one or more sections (secciones) per date.
    Each section is a separate PDF identified by its ``IdPeriodico``.
    """
    id: int                             # IdPeriodico — unique PDF ID
    fecha_publicacion: str              # ISO date, e.g. "2025-01-06T00:00:00"
    fecha_captura: Optional[str]
    numero: Optional[Union[str, int]]  # Issue number, e.g. "45" or 45
    tomo: Optional[Union[str, int]]
    # "ORDINARIO", "EXTRAORDINARIO", "VESPERTINA"
    edicion: Optional[str]
    seccion: Optional[str]            # "PRIMERA SECCION", etc.
    contenido: Optional[str]          # OCR content/index text
    dependencias: Optional[str]       # HTML list of issuing Autoridades
    url_pdf: str                      # Full URL to the PDF


class AgsPoPublicacionCalendario(BaseModel):
    """A calendar entry showing which editions were published on a given date."""
    fecha_publicacion: str            # ISO datetime string
    ediciones: str                    # Comma-separated edition types
    num_secciones: int               # Number of sections published that day
