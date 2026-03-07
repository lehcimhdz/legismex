import re
import asyncio
from datetime import date
from typing import List, Optional
import ssl
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

from .models import BcPoEdicion, BcPoResultado

class BcPoClient:
    """Cliente para obtener ediciones del Periódico Oficial de Baja California."""

    BASE_URL = "https://periodicooficial.ebajacalifornia.gob.mx/oficial/"
    AJAX_URL = urljoin(BASE_URL, "librerias/ajax/ajaxConsultaPublicaciones.jsp")
    CDN_URL = "https://wsextbc.ebajacalifornia.gob.mx/CdnBc/api/Imagenes/ObtenerImagenDeSistema"

    MESES = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    def __init__(self, **kwargs):
        # Configuración de SSL para evitar HANDSHAKE_FAILURE en servidores antiguos
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        # Forzar ciphers más compatibles
        self.ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')

        self.client_kwargs = {
            "timeout": 30.0,
            "follow_redirects": True,
            "verify": self.ssl_context,
            **kwargs,
        }

    def _parsear_ediciones(self, html: str, anio: int, mes_nombre: str) -> List[BcPoEdicion]:
        """Parsea el bloque HTML devuelto por el AJAX para extraer ediciones."""
        soup = BeautifulSoup(html, "html.parser")
        ediciones = []
        
        # El AJAX devuelve una lista de <p><a>...</a></p>
        links = soup.find_all("a")
        for link in links:
            texto = link.get_text(strip=True)
            # Ejemplo: "TOMO CXXXII 30 DE DICIEMBRE DE 2025 No.78  NÚMERO ESPECIAL - SECCIÓN I"
            # Ejemplo: "TOMO CXXXII 26 DE DICIEMBRE DE 2025 No.76  SECCIÓN III"
            
            # Regex para extraer los componentes principales
            # Tomo, Fecha, Numero, Seccion
            pattern = r"TOMO\s+([I|V|X|L|C]+)\s+(.*?)\s+No\.(\d+)\s+(.*)"
            match = re.search(pattern, texto, re.IGNORECASE)
            
            if not match:
                continue
                
            tomo = match.group(1)
            fecha_str = match.group(2)
            numero = match.group(3)
            seccion = match.group(4).strip()
            
            # Limpiar sección de guiones iniciales
            seccion = re.sub(r"^[-\s]+", "", seccion)
            if not seccion:
                seccion = "ÚNICA"

            # Parsear fecha: "30 DE DICIEMBRE DE 2025"
            date_match = re.search(r"(\d{1,2})\s+DE\s+(\w+)\s+DE\s+(\d{4})", fecha_str, re.IGNORECASE)
            if date_match:
                d = int(date_match.group(1))
                m_name = date_match.group(2).lower()
                a = int(date_match.group(3))
                
                mes_map = {v.lower(): k for k, v in self.MESES.items()}
                m = mes_map.get(m_name, 1)
                fecha_obj = date(a, m, d)
            else:
                continue

            # La URL ya viene en el href del link en la respuesta AJAX actual
            url_pdf = link.get("href", "")
            if not url_pdf or not url_pdf.startswith("http"):
                # Fallback a construcción manual si es necesario
                fmt_fecha = fecha_obj.strftime("%Y%m%d")
                nombre_archivo = f"Periodico-{numero}-{tomo}-{fmt_fecha}-{seccion}.pdf"
                params = {
                    "sistemaSolicitante": f"PeriodicoOficial/{anio}/{mes_nombre}",
                    "nombreArchivo": nombre_archivo,
                    "descargar": "false"
                }
                query = "&".join([f"{k}={quote(v)}" for k, v in params.items()])
                url_pdf = f"{self.CDN_URL}?{query}"
            
            ediciones.append(BcPoEdicion(
                tomo=tomo,
                numero=numero,
                fecha=fecha_obj,
                seccion=seccion,
                url_pdf=url_pdf
            ))
            
        return ediciones

    def obtener_ediciones(self, anio: int, mes: int) -> BcPoResultado:
        """Obtiene las ediciones de un año y mes específicos."""
        mes_nombre = self.MESES.get(mes)
        if not mes_nombre:
            raise ValueError(f"Mes inválido: {mes}")

        payload = {"anio": anio, "mes": mes}
        
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.post(self.AJAX_URL, data=payload)
            resp.raise_for_status()
            # print(f"DEBUG HTML: {resp.text[:500]}...")
            
        ediciones = self._parsear_ediciones(resp.text, anio, mes_nombre)
        return BcPoResultado(anio=anio, mes=mes, ediciones=ediciones)

    async def a_obtener_ediciones(self, anio: int, mes: int) -> BcPoResultado:
        """Versión asíncrona de obtener_ediciones."""
        mes_nombre = self.MESES.get(mes)
        if not mes_nombre:
            raise ValueError(f"Mes inválido: {mes}")

        payload = {"anio": anio, "mes": mes}
        
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.post(self.AJAX_URL, data=payload)
            resp.raise_for_status()
            
        ediciones = self._parsear_ediciones(resp.text, anio, mes_nombre)
        return BcPoResultado(anio=anio, mes=mes, ediciones=ediciones)
