import httpx
from typing import Optional, Dict, List
from bs4 import BeautifulSoup

from .models import PeriodoVotacion, VotacionDetalle, ResultadoBusqueda, Iniciativa, BaseDictamenes, Dictamen, DocumentoGaceta, Proposicion
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
        # Default al config general si es vacío
        config_name = f"Gaceta-LXV{'I' if legislatura == '66' else ''}" if legislatura else "Gaceta"

        params = {
            'config': config_name,
            'words': palabra
        }
        res = self._get(url, params=params)
        resultados = GacetaParser.parse_resultados_busqueda(
            res.text, palabra_clave=palabra)

        return resultados

    def obtener_iniciativas(self, legislatura: str = "66", origen: str = "T") -> List[Iniciativa]:
        """
        Obtiene las iniciativas de la Gaceta Parlamentaria.
        Mapea al buscador histórico interno.

        legislatura: "66", "65", etc.
        origen: "T" (Todas), "D" (Dictaminadas), "N" (Sin dictaminar)
        """
        # Según el HTML de muestra el endpoint es dinámico por legislatura
        url = f"{self.BASE_URL}/gp{legislatura}_b_QEjecutivo.php3"

        # En el HTML se usa el método POST
        data = {
            'origen': origen,
            # Parámetros vacíos por defecto según el form: 'anio', 'periodo', 'tipo_perio'
            'anio': '',
            'periodo': '',
            'tipo_perio': ''
        }

        with httpx.Client(timeout=self.timeout, headers=self.headers, verify=self._verify_ssl, follow_redirects=True) as client:
            response = client.post(url, data=data)
            response.encoding = 'iso-8859-1'
            response.raise_for_status()

            # El parser necesita arreglar URLs relativas tal vez
            iniciativas = GacetaParser.parse_iniciativas(response.text)

            # Corregir URLs relativas
            for i in iniciativas:
                if i.url_gaceta and i.url_gaceta.startswith("/"):
                    i.url_gaceta = f"{self.BASE_URL}{i.url_gaceta}"
                if i.url_pdf and i.url_pdf.startswith("/"):
                    i.url_pdf = f"{self.BASE_URL}{i.url_pdf}"

            return iniciativas

    def obtener_bases_dictamenes(self) -> List[BaseDictamenes]:
        """
        Obtiene la lista de bases de datos de dictámenes disponibles por legislatura.
        """
        url = f"{self.BASE_URL}/base/dictas/gp_dictamenes.html"
        res = self._get(url)
        bases = GacetaParser.parse_bases_dictamenes(res.text)

        # Corregir URLs
        for b in bases:
            if b.url_base.startswith("/"):
                b.url_base = f"{self.BASE_URL}{b.url_base}"

        return bases

    def buscar_dictamenes(self, legislatura: str = "66", palabra_clave: str = "") -> List[Dictamen]:
        """
        Busca dictámenes en la Gaceta Parlamentaria por palabra clave en su título.

        Args:
            legislatura (str): Número de la legislatura (ej. "66" o "65").
            palabra_clave (str): Texto a buscar en el título de los dictámenes.

        Returns:
            List[Dictamen]: Lista de objetos Dictamen extraídos de los resultados.
        """
        url = f"https://gaceta.diputados.gob.mx/base/dictas/{legislatura}/gp{legislatura}_bd_encuentra.php3"

        # El formulario de la gaceta manda el parámetro 'texto'
        data = {
            "texto": palabra_clave
        }

        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers, verify=self._verify_ssl, follow_redirects=True) as client:
                response = client.post(url, data=data)
                response.encoding = 'iso-8859-1'
                response.raise_for_status()

                # Parsear el HTML a la lista de dictámenes
                dictamenes = GacetaParser.parse_dictamenes(response.text)

                # Arreglar URLs relativas
                for d in dictamenes:
                    if d.url_gaceta and d.url_gaceta.startswith('/'):
                        d.url_gaceta = "https://gaceta.diputados.gob.mx" + d.url_gaceta
                    if d.url_pdf and d.url_pdf.startswith('/'):
                        d.url_pdf = "https://gaceta.diputados.gob.mx" + d.url_pdf

                return dictamenes

        except httpx.RequestError as exc:
            raise Exception(
                f"Error de red al conectar con el buscador de dictámenes de la Gaceta: {exc}")

    def buscar_proposiciones(self, legislatura: str = "66", palabra_clave: str = "") -> List[Proposicion]:
        """
        Busca proposiciones con punto de acuerdo en la Gaceta Parlamentaria.
        """
        url = f"https://gaceta.diputados.gob.mx/base/propos/{legislatura}/gp{legislatura}_bp_encuentra.php3"
        data = {
            "texto": palabra_clave
        }
        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers, verify=self._verify_ssl, follow_redirects=True) as client:
                response = client.post(url, data=data)
                response.encoding = 'iso-8859-1'
                response.raise_for_status()

                propos = GacetaParser.parse_proposiciones(response.text)
                return propos
        except httpx.RequestError as exc:
            raise Exception(
                f"Error al conectar con la Gaceta (Proposiciones): {exc}")

    def obtener_actas(self, legislatura: str = "66") -> List[DocumentoGaceta]:
        url = f"https://gaceta.diputados.gob.mx/gp{legislatura}_actas.html"
        res = self._get(url)
        return GacetaParser.parse_documentos_gaceta(res.text, "https://gaceta.diputados.gob.mx")

    def obtener_acuerdos(self, legislatura: str = "66") -> List[DocumentoGaceta]:
        url = f"https://gaceta.diputados.gob.mx/gp{legislatura}_acuerdos.html"
        res = self._get(url)
        return GacetaParser.parse_documentos_gaceta(res.text, "https://gaceta.diputados.gob.mx")

    def obtener_agendas(self) -> List[DocumentoGaceta]:
        # El índice de agendas es histórico y principal
        url = "https://gaceta.diputados.gob.mx/gp_agendas.html"
        res = self._get(url)
        return GacetaParser.parse_documentos_gaceta(res.text, "https://gaceta.diputados.gob.mx")

    def obtener_asistencias(self) -> List[DocumentoGaceta]:
        # El índice de asistencias es histórico y principal
        url = "https://gaceta.diputados.gob.mx/gp_asistencias.html"
        res = self._get(url)
        return GacetaParser.parse_documentos_gaceta(res.text, "https://gaceta.diputados.gob.mx")
