import httpx
from bs4 import BeautifulSoup
from typing import List
from .models import EdomexPoEdicion, EdomexPoDocumento

class EdomexPoClient:
    """
    Cliente para interactuar con el Periódico Oficial "Gaceta del Gobierno" y LEGISTEL.
    """
    
    BASE_URL = "https://legislacion.edomex.gob.mx"
    
    def __init__(self, verify_ssl: bool = False, timeout: float = 30.0):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.client = httpx.Client(verify=verify_ssl, timeout=timeout, headers=self.headers)

    def obtener_ediciones_recientes(self) -> List[EdomexPoEdicion]:
        """
        Descarga las publicaciones recientes mostradas en la primera página de la tabla.
        Organiza cada edición con sus documentos fraccionados y su url global si existe.
        """
        url = f"{self.BASE_URL}/ve_periodico_oficial"
        response = self.client.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        ediciones = []
        
        filas = soup.select(".views-table tbody tr")
        for fila in filas:
            fecha_cell = fila.select_one(".views-field-field-fecha")
            # "Miércoles Marzo 4,2026"
            fecha = fecha_cell.get_text(strip=True) if fecha_cell else ""
            
            if not fecha:
                continue
                
            sumario_cell = fila.select_one(".views-field-field-sumario")
            if not sumario_cell:
                continue
            
            # Instanciar contenedor
            edicion = EdomexPoEdicion(fecha=fecha, documentos=[])
            
            current_section = "General"
            for p in sumario_cell.find_all("p"):
                clases = p.get("class", [])
                
                # Es un titulo de seccion/dependencia?
                if "text-align-center" in clases:
                    texto_seccion = p.get_text(strip=True)
                    if texto_seccion:
                        current_section = texto_seccion
                    continue
                
                a_tag = p.find("a")
                if a_tag:
                    texto = a_tag.get_text(strip=True)
                    href = a_tag.get("href")
                    
                    if href and href.startswith("/"):
                        href = self.BASE_URL + href
                        
                    if "Descarga la gaceta" in texto:
                        edicion.url_completa = href
                    else:
                        edicion.documentos.append(EdomexPoDocumento(
                            seccion=current_section,
                            titulo=texto,
                            url_pdf=href
                        ))
            
            ediciones.append(edicion)
            
        return ediciones
