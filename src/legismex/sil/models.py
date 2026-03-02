from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class Legislador(BaseModel):
    id_sil: str = Field(..., description="ID interno del legislador en el SIL")
    nombre_completo: str
    apellidos: str
    nombre: str
    camara: str = Field(..., description="'Diputado' o 'Senador'")
    grupo_parlamentario: str
    estado: Optional[str] = None
    distrito: Optional[str] = None
    tipo_eleccion: Optional[str] = Field(None, description="Ej. Mayoría Relativa, Representación Proporcional")
    suplente_de: Optional[str] = None

class IniciativaResumen(BaseModel):
    id_sil: str = Field(..., description="ID interno de la iniciativa (ej. clave numérica o alfanumérica en URL)")
    titulo: str
    fecha_presentacion: Optional[date] = None
    presentada_por: str = Field(..., description="Quién la presentó (Legislador, Grupo Parlamentario, Ejecutivo, etc.)")
    turno_comision: Optional[str] = None
    estatus: str = Field(..., description="Ej. Pendiente, Aprobada, Desechada")
    gaceta_url: Optional[str] = None

class IniciativaDetalle(IniciativaResumen):
    sinopsis: str
    documento_url: Optional[str] = None
    # Aquí podríamos agregar campos más complejos luego como: votaciones, dictámenes, etc.

class ReporteSesionResumen(BaseModel):
    fecha: date
    hora: str
    tipo_sesion: str
    url_detalle: str

class ReporteSesionItem(BaseModel):
    tipo_asunto: str
    titulo: str
    promovente: Optional[str] = None
    tramite: Optional[str] = None
    texto_crudo: Optional[str] = None

class ReporteSesionDetalle(BaseModel):
    fecha: Optional[date] = None
    resumen: Optional[ReporteSesionResumen] = None
    asuntos: List[ReporteSesionItem] = []
    texto_raw: str = Field(..., description="Contenido de texto sin estructurar para análisis NLP")
