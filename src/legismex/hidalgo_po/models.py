from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date

class HidalgoPoEdicion(BaseModel):
    id: str
    nombre: str = Field(alias="name")
    sumario: str
    numero_edicion: str = Field(alias="numedicion")
    numero_paginas: str = Field(alias="numpagina")
    barcode: str
    fecha: date = Field(alias="publish")
    tipo_edicion_nombre: str = Field(alias="tipo_edicion_name")
    url_ejemplar: str = Field(alias="link_ejemplar")
    url_pdf: str

    class Config:
        populate_by_name = True

class HidalgoPoResultado(BaseModel):
    ediciones: List[HidalgoPoEdicion]
    total_registros: int
    pagina_actual: int
    total_paginas: int
