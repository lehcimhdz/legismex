from pydantic import BaseModel, Field
from typing import Optional

class GacetaConsejeria(BaseModel):
    """
    Representa un ejemplar de la Gaceta Oficial de la Ciudad de México 
    emitida por la Consejería Jurídica y de Servicios Legales.
    """
    descripcion: str = Field(description="Texto contenido en la primera columna, usualmente una síntesis de los decretos contenidos")
    fecha: str = Field(description="Fecha en la que se publicó la gaceta (ej. 2026-03-09)")
    numero: str = Field(description="Número de gaceta o tomo (ej. 'No. 29', '1811 Tomo 1')")
    
    # no URL exposed due to ZK Framework limitations, we expose whether it HAS a PDF button
    tiene_pdf: bool = Field(default=False, description="Indica si existe un botón de PDF disponible para descargarse")
    tiene_indice: bool = Field(default=False, description="Indica si existe un botón de Índice o detalles disponible")
    
    index_absoluto: int = Field(default=-1, description="Índice local asignado por Playwright para localizarla al descargar el PDF")
