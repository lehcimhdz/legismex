from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class PeriodoVotacion(BaseModel):
    legislatura: int
    nombre: str
    url_base: str


class VotacionDetalle(BaseModel):
    fecha: str
    asunto: str
    url_acta: Optional[str] = None
    url_pdf: Optional[str] = None
    votos_favor: Optional[int] = None
    votos_contra: Optional[int] = None
    abstenciones: Optional[int] = None


class ResultadoBusqueda(BaseModel):
    palabra_clave: str
    fecha: str
    contexto: str
    url_origen: str
    url_pdf: Optional[str] = None


class Iniciativa(BaseModel):
    fecha_presentacion: str
    titulo: str
    promovente: str
    tramite_o_estado: str
    url_gaceta: Optional[str] = None
    url_pdf: Optional[str] = None
    dictaminada: bool = False


class BaseDictamenes(BaseModel):
    legislatura: int
    titulo: str
    periodo: str
    url_base: str


class Dictamen(BaseModel):
    fecha: str
    titulo: str
    tramites: str
    url_gaceta: Optional[str] = None
    url_pdf: Optional[str] = None


class DocumentoGaceta(BaseModel):
    fecha_o_titulo: str
    url_documento: str


class Proposicion(BaseModel):
    fecha_presentacion: str
    titulo: str
    promovente: str
    tramite_o_estado: str
    url_gaceta: Optional[str] = None
    url_pdf: Optional[str] = None
    aprobada: bool = False
