import re
import asyncio
from datetime import datetime, date
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .models import BcsDocumento, BcsSesion, BcsOrdenDia, BcsActa, BcsDiario

class BcsCongresoClient:
    """Cliente para extraer información del H. Congreso de Baja California Sur."""
    
    BASE_URL = "https://www.cbcs.gob.mx"
    
    # Categorías para Orden del Día (XVII Legislatura como ejemplo)
    # Se pueden añadir más dinámicamente si es necesario.
    OR_ORDEN_DIA_XVII_2_REC_1 = f"{BASE_URL}/index.php/xvii-legislatura/xvii-leg-segundo-ano/xvii-leg-segundo-ano-primer-periodo-receso/orden-del-dia"
    
    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "follow_redirects": True,
            "verify": False,  # A veces hay problemas de SSL en sitios gubernamentales
            **kwargs,
        }

    def _parsear_fecha(self, texto: str) -> Optional[date]:
        """Intenta extraer una fecha de un texto."""
        meses = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
            "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
        }
        # Ejemplo: "MARTES 03 DE MARZO DE 2026"
        match = re.search(r"(\d{1,2})\s+DE\s+(\w+)\s+DE\s+(\d{4})", texto, re.IGNORECASE)
        if match:
            dia = int(match.group(1))
            mes_str = match.group(2).lower()
            anio = int(match.group(3))
            mes = meses.get(mes_str)
            if mes:
                try:
                    return date(anio, mes, dia)
                except ValueError:
                    return None
        return None

    # ------------------------------------------------------------------
    # Órdenes del Día
    # ------------------------------------------------------------------

    def obtener_ordenes_dia(self, url: str) -> List[BcsSesion]:
        """Lista las sesiones de una categoría de Orden del Día."""
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(url)
            resp.raise_for_status()
            
        soup = BeautifulSoup(resp.text, "html.parser")
        sesiones = []
        
        # En Joomla, el listado de categoría suele estar en una tabla con clase 'table'
        items = soup.select("tr.cat-list-row0, tr.cat-list-row1")
        for item in items:
            link = item.find("a")
            if link:
                titulo = link.get_text(strip=True)
                href = urljoin(url, link["href"])
                fecha = self._parsear_fecha(titulo)
                sesiones.append(BcsSesion(titulo=titulo, url=href, fecha=fecha))
                
        return sesiones

    def obtener_detalle_orden(self, url: str) -> BcsOrdenDia:
        """Extrae los PDFs de una página de detalle de sesión."""
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(url)
            resp.raise_for_status()
            
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # El título del artículo en Joomla suele estar en h2 o en .page-header h2, 
        # o recurrimos a la etiqueta <title>
        header = soup.select_one(".page-header h2, article h2")
        if header:
            titulo = header.get_text(strip=True)
        elif soup.title:
            titulo = soup.title.get_text(strip=True)
        else:
            titulo = "N/A"
            
        fecha = self._parsear_fecha(titulo)
        
        documentos = []
        # Buscar enlaces a PDFs
        links = soup.find_all("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
        for link in links:
            # Si el link no tiene texto, buscamos en el atributo title, o tratamos de agarrar el texto del párrafo contenedor
            doc_titulo = link.get_text(strip=True) or link.get("title")
            if not doc_titulo:
                parent_p = link.find_parent("p")
                if parent_p:
                    # Obtenemos el texto del párrafo excluyendo el enlace mismo
                    texto_p = parent_p.get_text(strip=True)
                    doc_titulo = texto_p[:200] + "..." if len(texto_p) > 200 else texto_p
            
            doc_titulo = doc_titulo or "Documento"
            doc_url = urljoin(url, link["href"])
            documentos.append(BcsDocumento(titulo=doc_titulo, url=doc_url))
            
        return BcsOrdenDia(titulo=titulo, fecha=fecha, documentos=documentos)

    # ------------------------------------------------------------------
    # Actas de Sesión
    # ------------------------------------------------------------------

    def obtener_actas(self, url: str) -> List[BcsActa]:
        """Extrae las actas de una tabla de listado."""
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(url)
            resp.raise_for_status()
            
        soup = BeautifulSoup(resp.text, "html.parser")
        actas = []
        
        # Buscamos filas en la tabla principal de contenido
        rows = soup.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if not cols:
                continue
                
            # Suele haber una columna de título y otra con el icono del PDF
            texto_fila = row.get_text(strip=True)
            link_pdf = row.find("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
            
            if link_pdf:
                titulo = texto_fila
                url_pdf = urljoin(url, link_pdf["href"])
                fecha = self._parsear_fecha(titulo)
                actas.append(BcsActa(titulo=titulo, fecha=fecha, url_pdf=url_pdf))
                
        return actas

    # ------------------------------------------------------------------
    # Diarios de los Debates
    # ------------------------------------------------------------------

    def obtener_diarios(self, url: str) -> List[BcsDiario]:
        """Extrae los diarios de una tabla de listado."""
        # La estructura suele ser idéntica a las Actas
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(url)
            resp.raise_for_status()
            
        soup = BeautifulSoup(resp.text, "html.parser")
        diarios = []
        
        rows = soup.find_all("tr")
        for row in rows:
            link_pdf = row.find("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
            if link_pdf:
                titulo = row.get_text(separator=" ", strip=True)
                url_pdf = urljoin(url, link_pdf["href"])
                fecha = self._parsear_fecha(titulo)
                diarios.append(BcsDiario(titulo=titulo, fecha=fecha, url_pdf=url_pdf))
                
        return diarios

    # ------------------------------------------------------------------
    # Métodos asíncronos
    # ------------------------------------------------------------------

    async def a_obtener_ordenes_dia(self, url: str) -> List[BcsSesion]:
        """Versión asíncrona de obtener_ordenes_dia."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            
        soup = BeautifulSoup(resp.text, "html.parser")
        sesiones = []
        items = soup.select("tr.cat-list-row0, tr.cat-list-row1")
        for item in items:
            link = item.find("a")
            if link:
                titulo = link.get_text(strip=True)
                href = urljoin(url, link["href"])
                fecha = self._parsear_fecha(titulo)
                sesiones.append(BcsSesion(titulo=titulo, url=href, fecha=fecha))
        return sesiones

    async def a_obtener_detalle_orden(self, url: str) -> BcsOrdenDia:
        """Versión asíncrona de obtener_detalle_orden."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            
        soup = BeautifulSoup(resp.text, "html.parser")
        header = soup.select_one(".page-header h2, article h2")
        if header:
            titulo = header.get_text(strip=True)
        elif soup.title:
            titulo = soup.title.get_text(strip=True)
        else:
            titulo = "N/A"
            
        fecha = self._parsear_fecha(titulo)
        
        documentos = []
        links = soup.find_all("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
        for link in links:
            doc_titulo = link.get_text(strip=True) or link.get("title")
            if not doc_titulo:
                parent_p = link.find_parent("p")
                if parent_p:
                    texto_p = parent_p.get_text(strip=True)
                    doc_titulo = texto_p[:200] + "..." if len(texto_p) > 200 else texto_p
            
            doc_titulo = doc_titulo or "Documento"
            doc_url = urljoin(url, link["href"])
            documentos.append(BcsDocumento(titulo=doc_titulo, url=doc_url))
        return BcsOrdenDia(titulo=titulo, fecha=fecha, documentos=documentos)
