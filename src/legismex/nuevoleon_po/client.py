import httpx
from bs4 import BeautifulSoup
from typing import List

from .models import NuevoLeonPoEdicion

class NuevoLeonPoClient:
    """
    Cliente para extraer del Periódico Oficial del Estado de Nuevo León,
    basado en su portal clásico de ASP.NET WebForms.
    """
    BASE_URL = "https://sistec.nl.gob.mx/Transparencia_2015_LYPOE/Acciones/PeriodicoOficial.aspx"

    def __init__(self, verify_ssl: bool = False, timeout: float = 30.0):
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        # NL's firewall will drop requests without a User-Agent
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def obtener_ediciones_recientes(self) -> List[NuevoLeonPoEdicion]:
        """
        Descarga la tabla listada en el portal principal del PO.
        
        :return: Lista de modelos `NuevoLeonPoEdicion`.
        """
        resultados = []
        
        with httpx.Client(verify=self.verify_ssl, timeout=self.timeout, headers=self.headers) as client:
            response = client.get(self.BASE_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", id="dgData")
            
            if not table:
                return []
                
            rows = table.find_all("tr")
            
            for row in rows[1:]: # Omitimos el primer tr (Header)
                cols = row.find_all("td", recursive=False)
                
                if len(cols) == 3:
                    numero = cols[0].get_text(strip=True)
                    fecha = cols[1].get_text(strip=True)
                    
                    # La tercera columna anida links en formato <a>
                    urls_pdf = []
                    links = cols[2].find_all("a", href=True)
                    for a in links:
                        # Usualmente ya son absolutos (ej. http://sistec.nl.gob.mx/...)
                        urls_pdf.append(a['href'])
                    
                    edicion = NuevoLeonPoEdicion(
                        numero=numero,
                        fecha=fecha,
                        urls_pdf=urls_pdf
                    )
                    resultados.append(edicion)
                
        return resultados
