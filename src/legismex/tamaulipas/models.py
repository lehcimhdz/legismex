from pydantic import BaseModel, ConfigDict


class TamaulipasGaceta(BaseModel):
    """Representa un registro de la Gaceta Parlamentaria del Congreso de Tamaulipas."""
    model_config = ConfigDict(populate_by_name=True)

    legislatura: int | str
    publicado_el: str
    numero: str
    tomo: str
    fecha_gaceta: str
    fecha_sesion: str
    sesion: str
    url_pdf: str
