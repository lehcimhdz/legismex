from pydantic import BaseModel
from typing import Optional


class MorelosDocumento(BaseModel):
    """A legislative document from the Morelos State Congress."""
    titulo: str
    url_pdf: str
    seccion: Optional[str] = None
    periodo: Optional[str] = None
