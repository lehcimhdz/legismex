from pydantic import BaseModel
from typing import List, Optional


class OaxacaDocumento(BaseModel):
    """A single document within an Oaxaca Congress gazette session."""
    numero: str           # Agenda item number (e.g. "1", "15", "36")
    descripcion: str      # Item description
    url_pdfs: List[str]   # One or more PDF URLs (some items have multiple parts)


class OaxacaGaceta(BaseModel):
    """One entry in the Oaxaca Congress Gaceta Parlamentaria (LXVI Legislatura)."""
    id: int               # Sequential gaceta number (1–N)
    numero: str           # Display number like "GP-179"
    tipo: str             # e.g. "Sesión Ordinaria", "Sesión Extraordinaria"
    fecha: str            # DD-MM-YYYY
    url_detalle: str      # Full URL to the detail page
    documentos: Optional[List[OaxacaDocumento]] = None
