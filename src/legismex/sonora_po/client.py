import re
from datetime import date
from typing import List, Optional, Dict
import httpx
from bs4 import BeautifulSoup

from .models import SonoraPoEdicion, SonoraPoResultado

class SonoraPoClient:
    """Cliente para interactuar con el Boletín Oficial de Sonora."""
    
    BASE_URL = "https://boletinoficial.sonora.gob.mx/index.php"
    BOLETIN_URL = "https://boletinoficial.sonora.gob.mx/boletin.php"
    
    # Mapeo de años a IDs de página de Joomla (extraído del portal)
    ANIOS_IDS: Dict[int, int] = {
        2026: 100, 2025: 91, 2024: 82, 2023: 45, 2022: 46, 2021: 47, 2020: 48, 2019: 49,
        2018: 50, 2017: 51, 2016: 52, 2015: 53, 2014: 54, 2013: 55, 2012: 56, 2011: 57,
        2010: 58, 2009: 59, 2008: 60, 2007: 61, 2006: 62, 2005: 63, 2004: 64, 2003: 65,
        2002: 66, 2001: 67, 2000: 68, 1999: 69, 1998: 70, 1997: 71, 1996: 72, 1995: 84,
        1994: 85, 1993: 86, 1992: 87, 1991: 88, 1990: 89, 1989: 90, 1988: 92, 1987: 93,
        1986: 96, 1985: 98, 1984: 97, 1983: 94, 1982: 95, 1981: 99
    }
    
    MESES_MAP = {
        1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR", 5: "MAY", 6: "JUN",
        7: "JUL", 8: "AGO", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DIC"
    }

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def _parsear_fecha(self, texto: str) -> Optional[date]:
        """Extrae la fecha de un texto como 'Viernes 02 de Enero de 2026'."""
        meses = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
            "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
        }
        match = re.search(r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", texto, re.IGNORECASE)
        if match:
            dia = int(match.group(1))
            mes_str = match.group(2).lower()
            anio = int(match.group(3))
            mes = meses.get(mes_str)
            if mes:
                return date(anio, mes, dia)
        return None

    def _extraer_ediciones_html(self, html: str, anio: int, mes: Optional[int] = None) -> List[SonoraPoEdicion]:
        """Parsea el HTML de la página anual y extrae las ediciones."""
        soup = BeautifulSoup(html, "html.parser")
        ediciones = []
        
        # Encontrar los contenedores de pestañas
        # Cada mes está en un div con un ID referenciado por la lista de pestañas
        tabs_nav = soup.select("ul.sppb-nav-tabs li a")
        tabs_map = {}
        for a in tabs_nav:
            mes_nombre = a.get_text(strip=True).upper()
            target_id = a.get("href", "").replace("#", "")
            if target_id:
                tabs_map[mes_nombre] = target_id
        
        # Si se especificó mes, solo procesamos ese
        meses_a_procesar = [self.MESES_MAP[mes]] if mes else self.MESES_MAP.values()
        
        for mes_nombre in meses_a_procesar:
            target_id = tabs_map.get(mes_nombre)
            if not target_id:
                continue
            
            tab_pane = soup.find("div", id=target_id)
            if not tab_pane:
                continue
            
            # Las ediciones suelen estar en listas o párrafos con enlaces boletin.php?id=...
            # Según la exploración previa, son enlaces directos
            links = tab_pane.find_all("a", href=re.compile(r"boletin\.php\?id=\d+"))
            for link in links:
                texto = link.get_text(separator=" ", strip=True)
                url_pdf = link["href"]
                if not url_pdf.startswith("http"):
                    url_pdf = f"https://boletinoficial.sonora.gob.mx/{url_pdf}"
                
                # Extraer info del texto: "Lunes 12 de Enero de 2026. CCXVII Número 4 Secc. I."
                fecha = self._parsear_fecha(texto)
                if not fecha:
                    continue
                
                # Extraer Número y Tipo
                # Ejemplo: "... Número 4 Secc. I." o "... Edición Especial."
                tipo = "Ordinaria"
                numero = "N/A"
                
                match_num = re.search(r"Número\s+(\d+)", texto)
                if match_num:
                    numero = match_num.group(1)
                
                if "Especial" in texto:
                    tipo = "Especial"
                elif "Secc." in texto:
                    match_secc = re.search(r"Secc\.\s+(\w+)", texto)
                    secc = match_secc.group(1) if match_secc else "I"
                    tipo = f"Sección {secc}"
                
                descripcion = ""
                # El texto siguiente al enlace suele ser la descripción
                parent_li = link.find_parent("li")
                if parent_li:
                    descripcion = parent_li.get_text(strip=True).replace(texto, "").strip()
                
                ediciones.append(SonoraPoEdicion(
                    fecha=fecha,
                    numero=numero,
                    edicion_tipo=tipo,
                    url_pdf=url_pdf,
                    descripcion=descripcion if descripcion else None
                ))
        
        return ediciones

    def obtener_ediciones(self, anio: int, mes: Optional[int] = None) -> SonoraPoResultado:
        """Obtiene las ediciones de un año y opcionalmente un mes."""
        page_id = self.ANIOS_IDS.get(anio)
        if not page_id:
            raise ValueError(f"Año {anio} no soportado o no encontrado.")
            
        params = {
            "option": "com_sppagebuilder",
            "view": "page",
            "id": page_id
        }
        
        with httpx.Client(timeout=self.timeout, follow_redirects=True, verify=False) as client:
            resp = client.get(self.BASE_URL, params=params)
            resp.raise_for_status()
            ediciones = self._extraer_ediciones_html(resp.text, anio, mes)

        return SonoraPoResultado(anio=anio, mes=mes, ediciones=ediciones)

    async def a_obtener_ediciones(self, anio: int, mes: Optional[int] = None) -> SonoraPoResultado:
        """Versión asíncrona de obtener_ediciones."""
        page_id = self.ANIOS_IDS.get(anio)
        if not page_id:
            raise ValueError(f"Año {anio} no soportado o no encontrado.")
            
        params = {
            "option": "com_sppagebuilder",
            "view": "page",
            "id": page_id
        }
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
            resp = await client.get(self.BASE_URL, params=params)
            resp.raise_for_status()
            ediciones = self._extraer_ediciones_html(resp.text, anio, mes)

        return SonoraPoResultado(anio=anio, mes=mes, ediciones=ediciones)
