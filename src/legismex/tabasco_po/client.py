import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
import asyncio
from .models import TabascoPoPublicacion

class TabascoPoClient:
    """Cliente para extraer publicaciones del Periódico Oficial de Tabasco."""
    BASE_URL = "https://tabasco.gob.mx/PeriodicoOficial"

    def __init__(self, **kwargs):
        """
        Inicializa el cliente del Periódico Oficial de Tabasco.

        Args:
            **kwargs: Argumentos adicionales para httpx.Client o AsyncClient.
        """
        self.client_kwargs = {
            "verify": False,
            "timeout": 30.0,
            **kwargs
        }

    def _parsear_html(self, html: str) -> List[TabascoPoPublicacion]:
        """Parsea el HTML de la tabla de publicaciones."""
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="table-striped")
        if not table:
            return []

        tbody = table.find("tbody")
        if not tbody:
            return []

        publicaciones = []
        rows = tbody.find_all("tr", class_="datos-periodico")
        
        for row in rows:
            tds = row.find_all("td")
            if len(tds) < 6:
                continue

            fecha = tds[0].get_text(strip=True)
            numero = tds[1].get_text(strip=True)
            tipo = tds[2].get_text(strip=True)
            suplemento = tds[3].get_text(strip=True) or None
            
            # Limpiar descripción (quitar "Mostrar ↓")
            desc_td = tds[4]
            desc_text = desc_td.get_text(separator=" ", strip=True)
            if "Mostrar ↓" in desc_text:
                desc_text = desc_text.split("Mostrar ↓")[0].strip()
            
            a_tag = tds[5].find("a")
            url_pdf = a_tag["href"] if a_tag else ""

            publicaciones.append(TabascoPoPublicacion(
                fecha=fecha,
                numero=numero,
                tipo=tipo,
                suplemento=suplemento,
                descripcion=desc_text,
                url_pdf=url_pdf
            ))
        
        return publicaciones

    def obtener_publicaciones(
        self, 
        busqueda: str = "", 
        paginas: int = 1
    ) -> List[TabascoPoPublicacion]:
        """
        Obtiene las publicaciones de forma síncrona.

        Args:
            busqueda: Término de búsqueda opcional (ej. "2025").
            paginas: Número de páginas a extraer (10 resultados por página).
        """
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            todas_publicaciones = []
            with httpx.Client(**self.client_kwargs) as client:
                for p in range(paginas):
                    if busqueda:
                        url = f"{self.BASE_URL}/resultado/{busqueda}/{p}"
                    else:
                        url = f"{self.BASE_URL}?page={p}"
                    
                    response = client.get(url)
                    response.raise_for_status()
                    pubs = self._parsear_html(response.text)
                    if not pubs:
                        break
                    todas_publicaciones.extend(pubs)
            return todas_publicaciones

    async def a_obtener_publicaciones(
        self, 
        busqueda: str = "", 
        paginas: int = 1
    ) -> List[TabascoPoPublicacion]:
        """
        Obtiene las publicaciones de forma asíncrona.

        Args:
            busqueda: Término de búsqueda opcional.
            paginas: Número de páginas a extraer.
        """
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            todas_publicaciones = []
            async with httpx.AsyncClient(**self.client_kwargs) as client:
                for p in range(paginas):
                    if busqueda:
                        url = f"{self.BASE_URL}/resultado/{busqueda}/{p}"
                    else:
                        url = f"{self.BASE_URL}?page={p}"
                    
                    response = await client.get(url)
                    response.raise_for_status()
                    pubs = self._parsear_html(response.text)
                    if not pubs:
                        break
                    todas_publicaciones.extend(pubs)
            return todas_publicaciones
