from pydantic import BaseModel
from typing import List, Optional


class AgsComision(BaseModel):
    """A commission associated with a legislative promotion."""
    id: int
    orden: int
    descripcion: str
    es_organo_legislativo: bool


class AgsPromocion(BaseModel):
    """A single legislative promotion in the Congreso de Aguascalientes agenda.

    Covers all 14 promotion types:
    1=ACUERDO LEGISLATIVO, 2=CUENTA PÚBLICA, 3=INICIATIVA, 4=MINUTA,
    5=NOMBRAMIENTO, 6=PUNTO DE ACUERDO, 7=SOLICITUD, 9=DECRETO,
    10=DICTÁMEN, 11=VERSIONES ESTENOGRÁFICAS, 12=ACTAS,
    13=DIARIO DE DEBATES, 14=GACETA PARLAMENTARIA
    """
    id: int
    numero_agenda: str                  # e.g. "416"
    tipo_promocion: str                 # e.g. "DECRETO"
    tipo_promocion_id: int              # numeric type id (1-14)
    legislatura_id: int                 # 64=LXIV, 65=LXV, 66=LXVI
    contenido: str                      # full text description
    comisiones: List[AgsComision]
    fecha_presentacion: Optional[str]   # ISO datetime string
    fecha_turno: Optional[str]
    resolucion: Optional[str]           # e.g. "EN TRÁMITE"
    resolucion_id: Optional[int]
    tipo_sesion: Optional[str]
    tipo_sesion_id: Optional[int]
    sesion_ordinaria: Optional[bool]
    tiene_archivo: bool                 # True if a PDF file is available
    # Full URL to download PDF (if available)
    url_pdf: Optional[str]
    nombre_archivo: Optional[str]       # Raw filename from API
    activo: bool
