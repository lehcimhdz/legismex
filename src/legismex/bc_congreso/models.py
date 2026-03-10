from typing import Optional
from datetime import date
from pydantic import BaseModel, Field


class BcIniciativa(BaseModel):
    """
    Representa una iniciativa, proposición o posicionamiento en el Congreso de Baja California.
    Extraído de: https://www.congresobc.gob.mx/TrabajoLegislativo/Iniciativas
    """
    sesion: Optional[str] = Field(
        None, description="Número o identificador de la sesión.")
    num_doc: Optional[str] = Field(
        None, description="Número de documento consecutivo en la sesión.")
    grupo_parlamentario: Optional[str] = Field(
        None, description="Grupo parlamentario o comisión de origen.")
    tipo: Optional[str] = Field(
        None, description="Tipo de documento (Iniciativa, Posicionamiento, etc.).")
    presentado_por: Optional[str] = Field(
        None, description="Autor o autores del documento.")
    turnado_a: Optional[str] = Field(
        None, description="Comisión o estatus a donde se turnó el documento.")
    votacion: Optional[str] = Field(
        None, description="Sentido de la votación o estatus.")
    fecha: Optional[date] = Field(
        None, description="Fecha en que se presentó el documento.")
    descripcion: Optional[str] = Field(
        None, description="Descripción textual del documento.")
    url_pdf: Optional[str] = Field(
        None, description="URL absoluta al documento PDF.")
