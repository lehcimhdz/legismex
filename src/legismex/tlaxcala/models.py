from pydantic import BaseModel
from typing import Optional


class TlaxcalaDocumento(BaseModel):
    """A legislative document from the Tlaxcala Congress (LXV Legislatura)."""
    categoria: str       # Tab name: Decretos, Iniciativas, Acuerdos, etc.
    anio: int            # Year: 2024, 2025, 2026
    numero: Optional[str] = None   # Sequential number (if table row)
    fecha: Optional[str] = None    # Date in DD/Mon/YYYY format
    titulo: str          # Document description
    url_pdf: str         # Direct PDF download URL
