import httpx
from typing import Optional, Dict, List
from .models import Legislador, IniciativaResumen, ReporteSesionResumen, ReporteSesionDetalle
from .parser import SILParser

class SILClient:
    """
    Cliente principal para interactuar con el Sistema de Información Legislativa (SIL).
    Maneja las peticiones HTTP base con un User-Agent adecuado.
    """
    BASE_URL = "http://sil.gobernacion.gob.mx/Librerias/pp_Principal.php"

    def __init__(self, timeout: float = 30.0):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        self.timeout = timeout

    def _get(self, url: str, params: Optional[Dict] = None) -> httpx.Response:
        """Realiza una petición GET genérica."""
        with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
            response = client.get(url, params=params)
            # El SIL usa ISO-8859-1 en la mayoría de sus páginas
            response.encoding = 'iso-8859-1'
            response.raise_for_status()
            return response

    def get_reportes_sesiones(self, camara: str = "diputados") -> List[ReporteSesionResumen]:
        """
        Obtiene la lista de los reportes de sesión de la cámara indicada.
        camara: "diputados" (1) o "senadores" (2)
        """
        c_id = "1" if camara.lower() == "diputados" else "2"
        # Usamos parámetros genéricos amplios para traer del histórico general o actual
        url = f"http://sil.gobernacion.gob.mx/Reportes/Sesion/ResultadoSesiones2.php"
        params = {
            "Camara": c_id,
            "Cve_Leg": "66", # Por defecto busquemos la más reciente (66)
            "Fec_ini": "01/01/2000", # Rango muy amplio para capturar lo disponible por default
            "Fec_fin": "31/12/2030"
        }
        res = self._get(url, params=params)
        resumenes = SILParser.parse_reportes_sesiones_resumen(res.text)
        
        # Corrigiendo URLs relativas
        for r in resumenes:
            if r.url_detalle.startswith("./"):
                r.url_detalle = f"http://sil.gobernacion.gob.mx/Reportes/Sesion/{r.url_detalle[2:]}"
                
        return resumenes
        
    def get_reporte_sesion(self, url_detalle: str) -> ReporteSesionDetalle:
        """
        Descarga y estrucura la información completa de un reporte de sesión dado su URL.
        """
        res = self._get(url_detalle)
        return SILParser.parse_reporte_sesion_detalle(res.text)

    # TODO: Implementar métodos para legisladores e iniciativas
