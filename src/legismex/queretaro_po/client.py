import httpx
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin

from .models import QueretaroPoEdicion

class QueretaroPoClient:
    """
    Cliente para extraer las publicaciones del Periódico Oficial del Estado de Querétaro ("La Sombra de Arteaga").
    """
    BASE_URL = "https://lasombradearteaga.segobqueretaro.gob.mx/"

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def obtener_ediciones_por_ano(self, anio: int) -> List[QueretaroPoEdicion]:
        """
        Extrae todas las ediciones listadas en el calendario visual de un año específico.
        
        Args:
            anio: Año de las publicaciones a consultar (ej. 2025).
            
        Returns:
            List[QueretaroPoEdicion]: Lista de publicaciones para el año.
        """
        url_calendario = f"{self.BASE_URL}{anio}.html"
        
        with httpx.Client(verify=False, timeout=self.timeout) as client:
            try:
                response = client.get(url_calendario)
                response.raise_for_status()
            except httpx.HTTPError:
                return []
                
            response.encoding = 'windows-1252'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Encontrar los links en el calendario (generalmente getlist.php o getfile.php)
            links = soup.find_all('a', href=True)
            
            ediciones_dict = {}
            
            for link in links:
                href = link.get('href')
                
                # Links to a list of pdfs for a day: getlist.php?p1=20250102
                # Links to a single pdf for a day: getfile.php?p1=20251215-01.pdf
                
                if 'getlist.php' in href:
                    partes = href.split('p1=')
                    if len(partes) > 1:
                        fecha = partes[1].split('&')[0][:8] # YYYYMMDD
                        if not fecha.isdigit(): continue
                        
                        if fecha not in ediciones_dict:
                            ediciones_dict[fecha] = []
                            
                        # Extraer la lista de PDFs de esta pagina
                        lista_url = urljoin(self.BASE_URL, href)
                        try:
                            list_resp = client.get(lista_url)
                            list_resp.encoding = 'windows-1252'
                            list_soup = BeautifulSoup(list_resp.text, 'html.parser')
                            pdf_links = list_soup.find_all('a', href=True)
                            for pdf_link in pdf_links:
                                pdf_href = pdf_link.get('href')
                                if 'getfile.php' in pdf_href or '.pdf' in pdf_href.lower() or 'descarga.php' in pdf_href.lower():
                                    ediciones_dict[fecha].append(urljoin(self.BASE_URL, pdf_href))
                        except Exception:
                            pass
                        
                elif 'getfile.php' in href or '.pdf' in href.lower() or 'descarga.php' in href.lower():
                    # Intenta extraer la fecha del formato p1=20250102-01.pdf o similar
                    import re
                    match = re.search(r'(20\d{6})', href)
                    if match:
                        fecha = match.group(1)
                    else:
                        fecha = "Desconocida"
                        
                    if fecha != "Desconocida":
                        if fecha not in ediciones_dict:
                            ediciones_dict[fecha] = []
                        ediciones_dict[fecha].append(urljoin(self.BASE_URL, href))
            
            resultados = []
            for fecha, urls in ediciones_dict.items():
                if urls:
                    # Remove duplicates while preserving order
                    unique_urls = []
                    for u in urls:
                        if u not in unique_urls:
                            unique_urls.append(u)
                    resultados.append(QueretaroPoEdicion(fecha=fecha, urls_pdf=unique_urls))
                    
            # Sort by date descending
            resultados.sort(key=lambda x: x.fecha, reverse=True)
            
            return resultados
