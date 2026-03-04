import httpx
from typing import List, Optional

from .models import JaliscoPoResumen, JaliscoPoEdicion, JaliscoPoPaginacion

class JaliscoPoClient:
    """
    Cliente oficial para interactuar con la API REST del
    Periódico Oficial del Estado de Jalisco (periodicooficial.jalisco.gob.mx).
    """
    BASE_URL = "https://apiperiodico.jalisco.gob.mx/api/newspaper"

    def __init__(self, verify_ssl: bool = False):
        self.verify_ssl = verify_ssl

    def buscar_ediciones(
        self, 
        fecha: str = "", 
        palabra_clave: str = "", 
        pagina: int = 1,
        elementos_por_pagina: int = 100
    ) -> JaliscoPoPaginacion:
        """
        Busca las ediciones del periódico oficial usando la API pública.
        
        :param fecha: Formato YYYY-MM-DD
        :param palabra_clave: Texto a buscar en el contenido.
        :param pagina: El número de página (para la paginación).
        :param elementos_por_pagina: La cantidad de resultados (hasta 100 por defecto para evitar múltiples hits).
        :return: Modelo `JaliscoPoPaginacion` con metadata y la lista resumida.
        """
        url = f"{self.BASE_URL}/public"
        params = {
            "fecha": fecha,
            "search": palabra_clave,
            "page": pagina,
            "perPage": elementos_por_pagina
        }
        
        with httpx.Client(verify=self.verify_ssl) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("errors"):
                raise ValueError(f"Error devuelto por la API del PO Jalisco: {data.get('errors')}")
                
            result = data.get("result", {})
            items = []
            
            for item in result.get("data", []):
                items.append(JaliscoPoResumen(**item))
                
            return JaliscoPoPaginacion(
                items=items,
                current_page=result.get("current_page", 1),
                last_page=result.get("last_page", 1),
                total=result.get("total", 0)
            )

    def obtener_edicion(self, id_newspaper: int) -> JaliscoPoEdicion:
        """
        Obtiene el detalle completo de una publicación, lo cual
        sirve para descubrir la URL del PDF que la sustenta.
        
        :param id_newspaper: El identificador numérico interno (`id_newspaper`).
        :return: Modelo `JaliscoPoEdicion`.
        """
        url = f"{self.BASE_URL}/public/find"
        params = {"id": id_newspaper}
        
        with httpx.Client(verify=self.verify_ssl) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("errors"):
                raise ValueError(f"Error devuelto por la API del PO Jalisco: {data.get('errors')}")
                
            result = data.get("result", {})
            return JaliscoPoEdicion(**result)
