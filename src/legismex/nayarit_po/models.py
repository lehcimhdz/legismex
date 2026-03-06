from pydantic import BaseModel, ConfigDict
from typing import Optional


class NayaritPoPublicacion(BaseModel):
    """Represanta una publicación del Periódico Oficial del Estado de Nayarit."""
    model_config = ConfigDict(populate_by_name=True)

    id: int
    """Identificador interno de la publicación."""

    fecha_publicacion: str
    """Fecha de publicación (YYYY-MM-DD)."""

    seccion: Optional[str] = None
    """Sección del periódico (ej. 'PRIMERA', 'SEGUNDA')."""

    tomo: Optional[str] = None
    """Tomo en numeración romana (ej. 'CCXVIII')."""

    numero: Optional[str] = None
    """Número de edición (ej. '039')."""

    tiraje: Optional[str] = None
    """Tiraje (ej. '015')."""

    sumario: Optional[str] = None
    """Resumen o extracto del contenido de la publicación."""

    tipo: Optional[str] = None
    """Tipo de publicación (ej. 'LICITACION', 'DECRETO', 'ACUERDO')."""

    nombre_pdf: Optional[str] = None
    """Nombre base del archivo PDF (sin extensión), usado para construir la URL de descarga."""

    @property
    def url_pdf(self) -> Optional[str]:
        """URL directa de descarga del PDF, si está disponible."""
        if not self.nombre_pdf:
            return None
        from urllib.parse import quote
        nombre = quote(f"{self.nombre_pdf}.pdf")
        return f"https://periodicooficial.nayarit.gob.mx/descargar_pdf.php?archivo={nombre}"


class NayaritPoResultado(BaseModel):
    """Resultado paginado devuelto por el API del PO de Nayarit."""
    model_config = ConfigDict(populate_by_name=True)

    publicaciones: list[NayaritPoPublicacion]
    """Lista de publicaciones en la página actual."""

    total: int
    """Total de publicaciones que coinciden con la búsqueda."""

    pagina: int
    """Página actual (1-based)."""

    resultados_por_pagina: int
    """Número de resultados por página (fijo en 10 por el servidor)."""

    @property
    def total_paginas(self) -> int:
        """Total de páginas disponibles."""
        if self.resultados_por_pagina == 0:
            return 0
        import math
        return math.ceil(self.total / self.resultados_por_pagina)
