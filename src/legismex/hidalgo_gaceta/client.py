import re
import asyncio
from datetime import date
from typing import List, Optional, Dict
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .models import HidalgoSession, HidalgoDocumento, HidalgoDetalleSesion

class HidalgoGacetaClient:
    """Cliente para obtener gacetas y documentos del Congreso de Hidalgo."""

    BASE_URL = "https://congresohidalgo.gob.mx/acervo_legislativo/"
    GACETA_URL = urljoin(BASE_URL, "gaceta")

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "follow_redirects": True,
            **kwargs,
        }

    def _parsear_listado(self, html: str) -> List[HidalgoSession]:
        """Parsea el HTML del listado de gacetas."""
        soup = BeautifulSoup(html, "html.parser")
        sesiones = []
        
        # Cada sesión está en un <a> con clase document-row
        items = soup.find_all("a", class_="document-row")
        for item in items:
            href = item.get("href", "")
            # href ej: "gaceta/957"
            session_id = href.split("/")[-1] if "/" in href else href
            url_detalle = urljoin(self.GACETA_URL + "/", session_id)
            
            # Tipo: SESIÓN ORDINARIA, SOLEMNE, etc.
            tipo_span = item.find("span", class_="bg-slate-100")
            tipo = tipo_span.get_text(strip=True) if tipo_span else "DESCONOCIDO"
            
            # Título
            titulo_h3 = item.find("h3")
            titulo = titulo_h3.get_text(strip=True) if titulo_h3 else "Sin título"
            
            # Fecha (en el div hidden md:block o en el p movil)
            fecha_div = item.find("div", class_="hidden md:block")
            fecha_text = fecha_div.get_text(strip=True) if fecha_div else ""
            
            if not fecha_text:
                fecha_p = item.find("p", class_="md:hidden")
                fecha_text = fecha_p.get_text(strip=True) if fecha_p else ""
            
            # Formato: 28/01/2026
            try:
                d, m, a = map(int, fecha_text.split("/"))
                fecha_obj = date(a, m, d)
            except Exception:
                fecha_obj = date(1900, 1, 1)

            sesiones.append(HidalgoSession(
                session_id=session_id,
                titulo=titulo,
                fecha=fecha_obj,
                tipo=tipo,
                url_detalle=url_detalle
            ))
            
        return sesiones

    def _parsear_detalle(self, html: str, session_id: str) -> HidalgoDetalleSesion:
        """Parsea el HTML de la página de detalle de una sesión."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Título
        header = soup.find("h1")
        titulo = header.get_text(strip=True) if header else "Sesión " + session_id
        
        # Fecha: suele estar en un div con clase que contiene la palabra 'FECHA'
        # o simplemente como un texto suelto que coincide con el patrón.
        fecha_obj = date(1900, 1, 1)
        fecha_text = ""
        
        # Intentar encontrar el texto que contiene FECHA DD/MM/AAAA
        fecha_match = re.search(r"(\d{2}/\d{2}/\d{4})", html)
        if fecha_match:
            fecha_text = fecha_match.group(1)
            try:
                d, m, a = map(int, fecha_text.split("/"))
                fecha_obj = date(a, m, d)
            except Exception:
                pass

        documentos = []
        # Los documentos están en bloques cards
        cards = soup.find_all("div", class_="bg-white")
        
        # Patrones de archivos que indican que NO hay contenido real
        PATRONES_INEXISTENTES = [
            "EN-PROCESO", "NO-EXISTIERON", "SIN-RESPUESTAS", 
            "NO-DICTAMENES", "NO-ACUERDOS", "NO-RESPUESTAS"
        ]
        
        for card in cards:
            title_div = card.find("h3") or card.find("div", class_="text-slate-900")
            if not title_div:
                continue
                
            nombre = title_div.get_text(strip=True)
            link_a = card.find("a", href=True)
            if not link_a:
                continue
                
            url = link_a["href"]
            es_zip = url.lower().endswith(".zip")
            
            url_upper = url.upper()
            es_existente = not any(p in url_upper for p in PATRONES_INEXISTENTES)
            
            # Limpiar nombre de ruidos de texto detectados en la verificación
            nombre = nombre.split("•")[0].strip()
            nombre = re.sub(r"\s+", " ", nombre)

            documentos.append(HidalgoDocumento(
                nombre=nombre,
                url=url,
                es_existente=es_existente,
                es_zip=es_zip
            ))
            
        return HidalgoDetalleSesion(
            session_id=session_id,
            titulo=titulo,
            fecha=fecha_obj,
            documentos=documentos
        )

    def obtener_sesiones(self, periodo: Optional[int] = None, mes: Optional[int] = None, 
                         tipo: Optional[int] = None, pagina: int = 1) -> List[HidalgoSession]:
        """Obtiene el listado de sesiones con filtros opcionales."""
        params = {"pagina": pagina}
        if periodo: params["periodo"] = periodo
        if mes: params["mes"] = mes
        if tipo: params["tipo"] = tipo
        
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(self.GACETA_URL, params=params)
            resp.raise_for_status()
            
        return self._parsear_listado(resp.text)

    async def a_obtener_sesiones(self, periodo: Optional[int] = None, mes: Optional[int] = None, 
                               tipo: Optional[int] = None, pagina: int = 1) -> List[HidalgoSession]:
        """Versión asíncrona de obtener_sesiones."""
        params = {"pagina": pagina}
        if periodo: params["periodo"] = periodo
        if mes: params["mes"] = mes
        if tipo: params["tipo"] = tipo
        
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(self.GACETA_URL, params=params)
            resp.raise_for_status()
            
        return self._parsear_listado(resp.text)

    def obtener_detalle_sesion(self, session_id: str) -> HidalgoDetalleSesion:
        """Obtiene los detalles y documentos de una sesión específica."""
        url = urljoin(self.GACETA_URL + "/", session_id)
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(url)
            resp.raise_for_status()
            
        return self._parsear_detalle(resp.text, session_id)

    async def a_obtener_detalle_sesion(self, session_id: str) -> HidalgoDetalleSesion:
        """Versión asíncrona de obtener_detalle_sesion."""
        url = urljoin(self.GACETA_URL + "/", session_id)
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            
        return self._parsear_detalle(resp.text, session_id)
