from pydantic import BaseModel


class EdomexGaceta(BaseModel):
    numero: str
    fecha: str
    url_pdf: str
