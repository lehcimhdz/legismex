from pydantic import BaseModel, Field


class QueretaroGaceta(BaseModel):
    """
    Representa una edición individual de la Gaceta Legislativa del Congreso de Querétaro.
    """
    legislatura: str = Field(
        ..., description="Clave de la Legislatura (Ej. Gacetas_LXI, LXI Legislatura, etc.)")
    numero: str = Field(...,
                        description="Número de la Gaceta (Ej. 038 o 034-T-IV)")
    descripcion: str = Field(...,
                             description="Descripción o fecha de la Gaceta")
    url_pdf: str = Field(...,
                         description="URL absoluta al documento PDF descargable")
