"""Modelos para la Gaceta Parlamentaria del H. Congreso del Estado de Sonora.

API: ``https://gestion.api.congresoson.gob.mx/publico/``
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class SonoraLegislatura(BaseModel):
    """Representa una legislatura del Congreso de Sonora."""
    model_config = ConfigDict(populate_by_name=True)

    id: str
    """UUID de la legislatura, ej. ``'7c1013d2-f2ac-49ad-9ce0-03a8b23e2ec5'``."""

    nombre: str
    """Nombre de la legislatura, ej. ``'Legislatura LXIV'``."""

    descripcion: Optional[str] = None
    """Descripción del periodo, ej. ``'Periodo de Sep. 2024 - Sep. 2027'``."""

    periodo_inicio: Optional[str] = None
    """Fecha de inicio del periodo en ISO-8601."""

    periodo_fin: Optional[str] = None
    """Fecha de fin del periodo en ISO-8601."""

    actual: Optional[bool] = None
    """``True`` si es la legislatura en curso."""

    @classmethod
    def from_api(cls, data: dict) -> "SonoraLegislatura":
        return cls(
            id=data["idLegislatura"],
            nombre=data.get("nombre", ""),
            descripcion=data.get("descripcion"),
            periodo_inicio=data.get("periodoInicio"),
            periodo_fin=data.get("periodoFin"),
            actual=bool(data.get("actual")),
        )


class SonoraGacetaMedia(BaseModel):
    """Archivo adjunto (normalmente PDF) de una gaceta."""
    model_config = ConfigDict(populate_by_name=True)

    nombre: str
    """Nombre del documento, ej. ``'Gaceta No. 2097 - Marzo 03 2026'``."""

    tipo: Optional[str] = None
    """Tipo de recurso, ej. ``'ARCHIVO'``."""

    descripcion: Optional[str] = None
    """Descripción breve, ej. ``'Sesión ordinaria'``."""

    pdf_url: Optional[str] = None
    """URL directa al archivo PDF."""

    @classmethod
    def from_api(cls, data: dict) -> "SonoraGacetaMedia":
        media = data.get("media") or {}
        return cls(
            nombre=data.get("nombre", ""),
            tipo=data.get("tipo"),
            descripcion=data.get("descripcion"),
            pdf_url=media.get("ruta"),
        )


class SonoraGaceta(BaseModel):
    """Representa una edición de la Gaceta Parlamentaria del Congreso de Sonora.

    El sitio ``congresoson.gob.mx/gacetas`` usa una SPA en Astro/React que
    consume la API REST ``gestion.api.congresoson.gob.mx/publico/``. Cada
    gaceta tiene un UUID único, una fecha de publicación, un tipo (``PLENO``,
    ``COMISION``, etc.) y puede tener uno o varios archivos PDF adjuntos.

    Los campos :attr:`periodo` y :attr:`legislatura_nombre` sólo están
    disponibles cuando se solicita con ``expand=legislatura,legislaturaPeriodo``.
    El campo :attr:`pdf_urls` sólo está disponible al consultar el detalle
    con ``expand=mediaGaceta.media``.
    """
    model_config = ConfigDict(populate_by_name=True)

    id: str
    """UUID único de la gaceta."""

    nombre: str
    """Nombre completo, ej. ``'Gaceta No. 2097 - Marzo 03 2026'``."""

    id_legislatura: Optional[str] = None
    """UUID de la legislatura a la que pertenece."""

    legislatura_nombre: Optional[str] = None
    """Nombre legible de la legislatura."""

    periodo: Optional[str] = None
    """Periodo legislativo, ej. ``'Segundo Periodo Ordinario'``."""

    tipo: Optional[str] = None
    """Tipo de sesión: ``'PLENO'``, ``'COMISION'``, etc."""

    fecha_publicacion: Optional[str] = None
    """Fecha de publicación en ISO-8601."""

    archivos: List[SonoraGacetaMedia] = []
    """Lista de archivos adjuntos (PDF). Requiere ``expand=mediaGaceta.media``."""

    @property
    def pdf_urls(self) -> List[str]:
        """Lista de URLs de los PDFs adjuntos."""
        return [a.pdf_url for a in self.archivos if a.pdf_url]

    @classmethod
    def from_api(cls, data: dict) -> "SonoraGaceta":
        leg = data.get("legislatura") or {}
        periodo_obj = data.get("legislaturaPeriodo") or {}
        medias = [SonoraGacetaMedia.from_api(m)
                  for m in data.get("mediaGaceta", [])]
        return cls(
            id=data["id"],
            nombre=data.get("nombre", ""),
            id_legislatura=data.get("idLegislatura"),
            legislatura_nombre=leg.get("nombre"),
            periodo=periodo_obj.get("nombre"),
            tipo=data.get("tipoGaceta"),
            fecha_publicacion=data.get("fechaPublicacion"),
            archivos=medias,
        )
