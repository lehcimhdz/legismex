from pydantic import BaseModel
from typing import Optional


class TlaxcalaPoEdicion(BaseModel):
    """One gazette entry from the Periódico Oficial de Tlaxcala."""
    anio: int
    fecha: str               # YYYY-MM-DD
    numero: str              # e.g. "Ex", "1Ex", "1-1ª SECC", "2-2ª SECC"
    contenido: str           # Document description (full text without wrapping quotes)
    url_pdf: Optional[str] = None   # Absolute PDF URL
