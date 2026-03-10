import re
import urllib.parse
from datetime import datetime, date
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup

from .models import BcIniciativa

class BcCongresoClient:
    """
    Cliente para interactuar con la página de Iniciativas del Congreso del Estado de Baja California.
    """
    
    BASE_URL = "https://www.congresobc.gob.mx/TrabajoLegislativo/Iniciativas"
    
    def __init__(self, **client_kwargs):
        """
        Inicializa el cliente con argumentos opcionales para httpx,
        como verificación SSL, timeouts, etc.
        """
        self.client_kwargs = {"verify": False, "timeout": 30.0}
        self.client_kwargs.update(client_kwargs)

    def _parsear_fecha(self, fecha_str: str) -> Optional[date]:
        """Convierte una cadena DD/MM/YYYY o YYYY/MM/DD a un objeto date."""
        if not fecha_str or not fecha_str.strip():
            return None
        fecha_str = fecha_str.strip()
        
        # Mapeos posibles: "2026/02/26" o "26/02/2026"
        for fmt in ("%Y/%m/%d", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(fecha_str, fmt).date()
            except ValueError:
                pass
        return None

    def _extraer_iniciativas_de_tabla(self, soup: BeautifulSoup) -> List[BcIniciativa]:
        """
        Extrae y parsea todas las iniciativas presentes en la tabla actual de ASP.NET.
        """
        iniciativas = []
        table = soup.find("table", {"id": "data-table"})
        if not table:
            # Puede ser la única tabla principal en la vista
            tables = soup.find_all("table")
            # Buscar una tabla que contenga la columna '# DOC.'
            for t in tables:
                header = t.find("tr")
                if header and "# DOC." in header.get_text():
                    table = t
                    break
                    
        if not table:
            return iniciativas
            
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            
            # Si no es un header y tiene la cantidad esperada de columnas
            if len(cells) >= 10 and cells[0].name == "td" and cells[0].get_text(strip=True):
                # Extraer atributos principales
                sesion = cells[0].get_text(strip=True)
                num_doc = cells[1].get_text(strip=True)
                grupo_parlamentario = cells[2].get_text(strip=True)
                tipo = cells[3].get_text(strip=True)
                presentado_por = cells[4].get_text(strip=True)
                turnado_a = cells[5].get_text(strip=True)
                votacion = cells[6].get_text(strip=True)
                fecha_str = cells[7].get_text(strip=True)
                descripcion = cells[8].get_text(strip=True)
                
                # Extraer URL del PDF
                url_pdf = None
                link = cells[9].find("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
                if not link:
                    # Alternativamente, a veces puede estar en otra celda
                    link = row.find("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
                
                if link and link.get("href"):
                    href = link["href"]
                    # Convertir a URL absoluta
                    url_pdf = urllib.parse.urljoin(self.BASE_URL, href)
                
                iniciativa = BcIniciativa(
                    sesion=sesion,
                    num_doc=num_doc,
                    grupo_parlamentario=grupo_parlamentario,
                    tipo=tipo,
                    presentado_por=presentado_por,
                    turnado_a=turnado_a,
                    votacion=votacion,
                    fecha=self._parsear_fecha(fecha_str),
                    descripcion=descripcion,
                    url_pdf=url_pdf
                )
                iniciativas.append(iniciativa)
                
        return iniciativas

    def _obtener_paginacion(self, soup: BeautifulSoup) -> List[str]:
        """Busca el control de paginación y devuelve una lista de event_arguments pendientes."""
        args_pendientes = []
        
        # El pager generalmente está en un row con clase pager, o dentro de otra tabla nidificada.
        pager = soup.find("tr", class_="pager") 
        if not pager:
            table = soup.find("table", {"id": "data-table"}) or soup.find("table")
            if table:
                rows = table.find_all("tr")
                if rows:
                    last_row = rows[-1]
                    if last_row.find("table"):
                        pager = last_row
                        
        if pager:
            links = pager.find_all("a")
            for link in links:
                href = link.get("href", "")
                # __doPostBack('ctl00$MainContent$GridView1','Page$2')
                match = re.search(r"__doPostBack\('(.*?)','(.*?)'\)", href)
                if match:
                    event_arg = match.group(2)
                    args_pendientes.append(event_arg)
                    
        return args_pendientes

    def obtener_iniciativas(self, max_paginas: Optional[int] = 1) -> List[BcIniciativa]:
        """
        Descarga las iniciativas desde el listado paginado.
        
        Args:
            max_paginas (Optional[int]): Límite de páginas a extraer. 
                                         Si es None, extrae todas las disponibles.
        """
        todas_las_iniciativas = []
        
        with httpx.Client(**self.client_kwargs) as client:
            # 1. GET Inicial a la página base
            response = client.get(self.BASE_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extraer de la página inicial
            iniciativas_pagina = self._extraer_iniciativas_de_tabla(soup)
            todas_las_iniciativas.extend(iniciativas_pagina)
            paginas_extraidas = 1
            
            # 2. Paginación
            args_disponibles = self._obtener_paginacion(soup)
            
            # Si solo queríamos la primera página o no hay paginación, cortamos.
            if max_paginas is not None and paginas_extraidas >= max_paginas:
                return todas_las_iniciativas
                
            paginas_visitadas = {"Page$1"} # Asumimos que la página inicial era la 1

            while args_disponibles and (max_paginas is None or paginas_extraidas < max_paginas):
                # Extraemos y filtramos la próxima página a visitar
                siguiente_arg = None
                for arg in list(args_disponibles):
                    args_disponibles.remove(arg)
                    if arg not in paginas_visitadas and "Page$" in arg:
                        siguiente_arg = arg
                        break
                
                if not siguiente_arg:
                    break # Ya no hay páginas nuevas que visitar

                # Buscar variables de estado
                viewstate = soup.find("input", {"name": "__VIEWSTATE"})
                viewstate_gen = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})
                event_valid = soup.find("input", {"name": "__EVENTVALIDATION"})
                
                payload = {
                    "__VIEWSTATE": viewstate["value"] if viewstate else "",
                    "__VIEWSTATEGENERATOR": viewstate_gen["value"] if viewstate_gen else "",
                    "__EVENTVALIDATION": event_valid["value"] if event_valid else "",
                    "__EVENTTARGET": "ctl00$ctl00$ctl00$ContentPlaceHolder1$MainContent$GrdListado", # Target típico detectado
                    "__EVENTARGUMENT": siguiente_arg
                }
                
                # Intentar adivinar el target analizando href (normalmente el grupo 1 de __doPostBack)
                pager_links = soup.find_all("a", href=re.compile(siguiente_arg))
                for link in pager_links:
                     match = re.search(r"__doPostBack\('(.*?)',", link.get("href", ""))
                     if match:
                         payload["__EVENTTARGET"] = match.group(1)
                         break
                
                response = client.post(self.BASE_URL, data=payload)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                
                iniciativas_pagina = self._extraer_iniciativas_de_tabla(soup)
                todas_las_iniciativas.extend(iniciativas_pagina)
                
                paginas_visitadas.add(siguiente_arg)
                paginas_extraidas += 1
                
                # Actualizar las disponibles detectadas en esta página
                nuevos_args = self._obtener_paginacion(soup)
                for arg in nuevos_args:
                    if arg not in paginas_visitadas and arg not in args_disponibles:
                        args_disponibles.append(arg)

        return todas_las_iniciativas

    async def a_obtener_iniciativas(self, max_paginas: Optional[int] = 1) -> List[BcIniciativa]:
        """
        Versión asíncrona de obtener_iniciativas.
        """
        todas_las_iniciativas = []
        
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            response = await client.get(self.BASE_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            todas_las_iniciativas.extend(self._extraer_iniciativas_de_tabla(soup))
            paginas_extraidas = 1
            
            args_disponibles = self._obtener_paginacion(soup)
            
            if max_paginas is not None and paginas_extraidas >= max_paginas:
                return todas_las_iniciativas
                
            paginas_visitadas = {"Page$1"}

            while args_disponibles and (max_paginas is None or paginas_extraidas < max_paginas):
                siguiente_arg = None
                for arg in list(args_disponibles):
                    args_disponibles.remove(arg)
                    if arg not in paginas_visitadas and "Page$" in arg:
                        siguiente_arg = arg
                        break
                
                if not siguiente_arg:
                    break

                viewstate = soup.find("input", {"name": "__VIEWSTATE"})
                viewstate_gen = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})
                event_valid = soup.find("input", {"name": "__EVENTVALIDATION"})
                
                payload = {
                    "__VIEWSTATE": viewstate["value"] if viewstate else "",
                    "__VIEWSTATEGENERATOR": viewstate_gen["value"] if viewstate_gen else "",
                    "__EVENTVALIDATION": event_valid["value"] if event_valid else "",
                    "__EVENTTARGET": "ctl00$ctl00$ctl00$ContentPlaceHolder1$MainContent$GrdListado",
                    "__EVENTARGUMENT": siguiente_arg
                }
                
                pager_links = soup.find_all("a", href=re.compile(siguiente_arg))
                for link in pager_links:
                     match = re.search(r"__doPostBack\('(.*?)',", link.get("href", ""))
                     if match:
                         payload["__EVENTTARGET"] = match.group(1)
                         break
                
                response = await client.post(self.BASE_URL, data=payload)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                
                todas_las_iniciativas.extend(self._extraer_iniciativas_de_tabla(soup))
                
                paginas_visitadas.add(siguiente_arg)
                paginas_extraidas += 1
                
                nuevos_args = self._obtener_paginacion(soup)
                for arg in nuevos_args:
                    if arg not in paginas_visitadas and arg not in args_disponibles:
                        args_disponibles.append(arg)

        return todas_las_iniciativas
