import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .models import JaliscoEvento, JaliscoPunto, JaliscoDocumento
from .parser import (
    parse_eventos_dia,
    parse_orden_dia,
    parse_subpuntos
)

class JaliscoClient:
    """Cliente para extraer información de la Gaceta Parlamentaria de Jalisco."""
    
    BASE_URL = "https://gaceta.congresojal.gob.mx"
    
    def __init__(self, verify_ssl: bool = False):
        self.verify_ssl = verify_ssl
        self.client = httpx.Client(verify=self.verify_ssl)

    def obtener_calendario_eventos(self) -> List[Dict[str, Any]]:
        """
        Obtiene el JSON del calendario con las fechas disponibles.
        Retorna una lista de diccionarios, ej: [{'fecha': '2025-10-06', 'tipo': '1'}, ...]
        """
        url = f"{self.BASE_URL}/fechas_eventos.php?nr=1&com=0"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def obtener_eventos_por_fecha(self, fecha: str) -> List[JaliscoEvento]:
        """
        Obtiene los eventos y su respectivo orden del día y documentos para una fecha dada.
        El scrapping se hace en cascada extrayendo Puntos y Subpuntos.
        """
        # 1. Obtener eventos de la fecha
        url_eventos = f"{self.BASE_URL}/datos_eventos.php?fechasel={fecha}&nr=1&com=0"
        res_evt = self.client.get(url_eventos)
        res_evt.raise_for_status()
        
        eventos = parse_eventos_dia(res_evt.text, fecha)
        
        # 2. Por cada evento, traer sus puntos
        for evt in eventos:
            if evt.tipo in (1, 5):
                url_orden = f"{self.BASE_URL}/pleno/orden.php?fec={fecha}&t={evt.tipo}&idsel={evt.id_evento}&nr=1"
            elif evt.tipo == 2:
                url_orden = f"{self.BASE_URL}/com/sesion/orden.php?fec={fecha}&t={evt.tipo}&idsel={evt.id_evento}&nr=1&com=0"
            else:
                continue

            res_orden = self.client.get(url_orden)
            if res_orden.status_code == 200:
                puntos_data = parse_orden_dia(res_orden.text)
                
                # 3. Por cada punto, si tiene subpuntos, traer los documentos
                for pt in puntos_data:
                    punto_obj = JaliscoPunto(titulo=pt["titulo"], documentos=[])
                    if pt["onclick_id"] and pt["onclick_tipo"]:
                        sub_id = pt["onclick_id"]
                        sub_tipo = pt["onclick_tipo"]
                        
                        if sub_tipo == 1:
                            url_sub = f"{self.BASE_URL}/pleno/suborden.php?id_punto={sub_id}&nr=1"
                        elif sub_tipo == 2:
                            url_sub = f"{self.BASE_URL}/com/sesion/suborden.php?id_punto={sub_id}&nr=1"
                        else:
                            url_sub = None
                            
                        if url_sub:
                            res_sub = self.client.get(url_sub)
                            if res_sub.status_code == 200:
                                punto_obj.documentos = parse_subpuntos(res_sub.text)
                    
                    evt.puntos_orden.append(punto_obj)
        
        return eventos
