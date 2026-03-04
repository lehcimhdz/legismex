import requests
import sys
import os
from typing import List, Optional

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

from legismex.cdmx.models import DocumentoCdmx
from legismex.cdmx.parser import CdmxParser

class CdmxClient:
    """
    Cliente para interactuar con la plataforma de la Gaceta Parlamentaria 
    y Diarios de Debate del Congreso de la Ciudad de México.
    """
    
    BASE_URL = "https://www.congresocdmx.gob.mx"
    
    def __init__(self, use_tqdm: bool = True):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
        })
        # the user ssl certificates are frequently invalid for government pages
        self._verify_ssl = False
        self.use_tqdm = use_tqdm and tqdm is not None

    def obtener_gacetas_por_url(self, url: str) -> List[DocumentoCdmx]:
        """
        Dada una URL específica de una sección del Congreso CDMX (ej. un año/mes específico),
        descarga el HTML y extrae todos los enlaces a PDFs disponibles.
        """
        # Asegurarse que es una URL absoluta o relativa correcta
        if not url.startswith('http'):
            if url.startswith('/'):
                url = f"{self.BASE_URL}{url}"
            else:
                url = f"{self.BASE_URL}/{url}"

        response = self.session.get(url, verify=self._verify_ssl)
        response.raise_for_status()
        
        return CdmxParser.parse_alertas_pdf(response.text)

    def descargar_pdf(self, url_pdf: str, ruta_destino: str) -> Optional[str]:
        """
        Descarga un PDF de gran tamaño desde la URL proporcionada.
        Muestra una barra de progreso nativa en terminal para mejorar la UX. 
        """
        if not url_pdf.startswith('http'):
            url_pdf = f"{self.BASE_URL}/{url_pdf.lstrip('/')}"
        
        # Ensure target directory exists
        directorios = os.path.dirname(ruta_destino)
        if directorios:
             os.makedirs(directorios, exist_ok=True)
             
        # Request file as stream
        try:
            response = self.session.get(url_pdf, stream=True, verify=self._verify_ssl, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar o descargar el archivo desde {url_pdf}: {e}")
            return None

        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024 * 8  # 8 Kibibyte chunks

        if self.use_tqdm and total_size_in_bytes > 0:
            # Barra de progreso estilizada
            progress_bar = tqdm(
                total=total_size_in_bytes, 
                unit='iB', 
                unit_scale=True, 
                desc=f"Descargando {os.path.basename(ruta_destino)}",
                colour='green'
            )
        else:
            if total_size_in_bytes > 0:
                print(f"Iniciando descarga de {total_size_in_bytes / (1024*1024):.2f} MB hacia {ruta_destino}...")
            else:
                print(f"Iniciando descarga hacia {ruta_destino} (Tamaño desconocido)..")
            progress_bar = None

        try:
            with open(ruta_destino, 'wb') as file:
                for data in response.iter_content(block_size):
                    if progress_bar:
                        progress_bar.update(len(data))
                    file.write(data)
        except Exception as e:
            print(f"Ocurrió un error escribiendo el archivo a disco: {e}")
            return None
        finally:
            if progress_bar:
                progress_bar.close()
                
        # Verificar integridad si el servidor mandó la bandera de tamaño
        if total_size_in_bytes != 0 and progress_bar and progress_bar.n != total_size_in_bytes:
            print("ADVERTENCIA: Algo salió mal, el archivo descargado no coincide con el tamaño del servidor.")
            return None
            
        print(f"¡Descarga exitosa guardada en {ruta_destino}! 🚀")
        return ruta_destino
