from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ChiapasAdministracion(str, Enum):
    """Endpoints de los servidores para el PO de Chiapas según la administración."""
    ADMIN_2024_2030 = "periodico2430"
    ADMIN_2018_2024 = "periodico1824"
    ADMIN_2012_2018 = "periodico1218"
    ADMIN_2006_2012 = "periodico0612"

class ChiapasPoEdicion(BaseModel):
    """Representa un registro devuelto en el portal del PO de Chiapas."""
    model_config = ConfigDict(populate_by_name=True)

    numero: str
    fecha: str
    seccion: Optional[str] = None
    parte: Optional[str] = None
    url_pdf: str
