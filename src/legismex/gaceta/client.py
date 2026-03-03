import httpx
from typing import Optional, Dict, List
from .models import PeriodoVotacion, VotacionDetalle, ResultadoBusqueda
from .parser import GacetaParser

class GacetaClient:
    """
    Cliente para interactuar con la Gaceta Parlamentaria.
    Maneja las peticiones HTTP ignorando errores de SSL obsoletos comunes en sitios gubernamentales.
    """
    BASE_URL = "http://gaceta.diputados.gob.mx"

    def __init__(self, timeout: float = 30.0):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        self.timeout = timeout
        
        # Desactivamos verificación SSL estrictamente para dominios .gob
        self._verify_ssl = False

    def _get(self, url: str, params: Optional[Dict] = None) -> httpx.Response:
        """Realiza una petición GET genérica soportando redirects y sin check SSL."""
        with httpx.Client(timeout=self.timeout, headers=self.headers, verify=self._verify_ssl, follow_redirects=True) as client:
            response = client.get(url, params=params)
            # La Gaceta acostumbra usar ISO-8859-1 en sus páginas
            response.encoding = 'iso-8859-1'
            response.raise_for_status()
            return response

    def get_periodos_votacion(self) -> List[PeriodoVotacion]:
        """
        Obtiene la lista de los periodos de votación disponibles históricamente.
        """
        url = f"{self.BASE_URL}/gp_votaciones.html"
        res = self._get(url)
        periodos = GacetaParser.parse_periodos_votacion(res.text)
        
        # Corregir URLs relativas
        for p in periodos:
            if p.url_base.startswith("/"):
                p.url_base = f"{self.BASE_URL}{p.url_base}"
            elif not p.url_base.startswith("http"):
                p.url_base = f"{self.BASE_URL}/{p.url_base}"
                
        return periodos

    def get_votaciones_por_periodo(self, url_periodo: str) -> List[VotacionDetalle]:
        """
        Descarga el detalle extendido de todas las votaciones (asuntos, votos, oficios)
        llevadas a cabo en un periodo legislativo en particular.
        """
        res = self._get(url_periodo)
        votaciones = GacetaParser.parse_votaciones_detalle(res.text)
        
        # Corregir URLs relativas de actas y PDFs usando la base de gaceta
        for v in votaciones:
            if v.url_pdf and v.url_pdf.startswith("/"):
                v.url_pdf = f"{self.BASE_URL}{v.url_pdf}"
            if v.url_acta and v.url_acta.startswith("/"):
                v.url_acta = f"{self.BASE_URL}{v.url_acta}"
                
        return votaciones

    def buscar_palabra_clave(self, palabra: str, legislatura: str = "66") -> List[ResultadoBusqueda]:
        """
        Busca una palabra clave en todo el histórico de la Gaceta Parlamentaria 
        usando el motor HTDIG integrado en el sitio.
        
        legislatura: Puede ser "66", "65", etc. o un string vacío "" para buscar en todas.
        """
        url = f"{self.BASE_URL}/cgi-bin/HTDIG/htsearch"
        config_name = f"Gaceta-LXV{'I' if legislatura == '66' else ''}" if legislatura else "Gaceta" # Default al config general si es vacío
        
        params = {
            'config': config_name,
            'words': palabra
        }
        res = self._get(url, params=params)
        resultados = GacetaParser.parse_resultados_busqueda(res.text, palabra_clave=palabra)
        
        return resultados
