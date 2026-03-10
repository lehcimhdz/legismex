import httpx
import asyncio
import re
from bs4 import BeautifulSoup
from typing import List
from .models import DurangoPoEdicion


class DurangoPoClient:
    """Cliente para obtener publicaciones del Periódico Oficial del Estado de Durango."""

    BASE_URL = "https://periodicooficial.durango.gob.mx"

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "verify": False,
            "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            **kwargs,
        }

    def _parsear_ediciones_lista(self, html: str) -> List[DurangoPoEdicion]:
        """A partir de una página de lista, extrae los UUIDs y los metadatos relevantes."""
        ediciones = []
        soup = BeautifulSoup(html, "html.parser")

        # En la página principal suele haber unas 'cards' superiores (<article class="card-periodico">)
        # y una lista/grilla en la parte inferior (<div class="... md:grid-cols-6 ...">)
        # La forma más genérica es buscar los enlaces `a` con /periodicos/UUID
        links = soup.find_all("a", href=True)
        vistos = set()

        for link in links:
            href = link["href"]
            match_uuid = re.search(r'/periodicos/([0-9a-f\-]{36})', href)
            if not match_uuid:
                continue

            uuid = match_uuid.group(1)
            if uuid in vistos:
                continue

            vistos.add(uuid)

            # Subir o buscar el contexto del elemento para extraer títulos y fecha
            parent = link.find_parent("div", class_=re.compile(r"grid-cols-6"))
            if parent:
                # Estructura de Lista
                h3 = parent.find("h3")
                fecha_span = parent.find_all("span", class_="text-gray-60")

                titulo = h3.get_text(
                    separator=" ", strip=True) if h3 else f"Edición {uuid[:8]}"
                fecha = fecha_span[0].get_text(
                    strip=True) if len(fecha_span) > 0 else "N/A"
                pubs = fecha_span[1].get_text(
                    strip=True) if len(fecha_span) > 1 else ""

                es_bis = "Bis" in titulo
                es_extraordinario = "Ext" in titulo or "Extra" in titulo

                ediciones.append(DurangoPoEdicion(
                    uuid=uuid,
                    titulo=titulo,
                    fecha=fecha,
                    cantidad_publicaciones=pubs,
                    es_bis=es_bis,
                    es_extraordinario=es_extraordinario
                ))
            else:
                # Tratar de ver si está en una Card destacada
                card = link.find_parent("article", class_="card-periodicos")
                if card:
                    h3 = card.find("h3")
                    time_tag = card.find("time")
                    titulo = h3.get_text(
                        separator=" ", strip=True) if h3 else f"Edición {uuid[:8]}"
                    fecha = time_tag.get_text(
                        strip=True) if time_tag else "N/A"
                    es_bis = "Bis" in titulo
                    es_extraordinario = "Ext" in titulo or "Extra" in titulo

                    ediciones.append(DurangoPoEdicion(
                        uuid=uuid,
                        titulo=titulo,
                        fecha=fecha,
                        cantidad_publicaciones="",
                        es_bis=es_bis,
                        es_extraordinario=es_extraordinario
                    ))

        return ediciones

    def _extraer_pdf(self, detail_html: str) -> str:
        """Extrae el primer enlace al PDF alojado en S3 desde el HTML del Next.js bundle."""
        links = re.findall(
            r'https://transp23\.s3\.amazonaws\.com/[^\"]*\.pdf', detail_html)
        # Evitar duplicados retornando el primero si existe
        if links:
            return links[0]
        return ""

    # ----------- Síncronos -----------

    def obtener_ediciones(self, pagina: int = 1) -> List[DurangoPoEdicion]:
        """Obtiene las publicaciones de una página específica."""
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.get(f"{self.BASE_URL}/periodicos?pagina={pagina}")
            resp.raise_for_status()
            ediciones = self._parsear_ediciones_lista(resp.text)

            # Obtener el PDF para cada edición (Síncrono N+1)
            for ed in ediciones:
                det_resp = client.get(f"{self.BASE_URL}/periodicos/{ed.uuid}")
                ed.url_pdf = self._extraer_pdf(det_resp.text)

            return ediciones

    # ----------- Asíncronos -----------

    async def a_obtener_ediciones(self, pagina: int = 1) -> List[DurangoPoEdicion]:
        """Obtiene las publicaciones y sus URLs de descarga de forma asíncrona concurrente."""
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.get(f"{self.BASE_URL}/periodicos?pagina={pagina}")
            resp.raise_for_status()
            ediciones = self._parsear_ediciones_lista(resp.text)

            async def armar_edicion(ed: DurangoPoEdicion):
                try:
                    det = await client.get(f"{self.BASE_URL}/periodicos/{ed.uuid}")
                    ed.url_pdf = self._extraer_pdf(det.text)
                except httpx.RequestError:
                    ed.url_pdf = ""
                return ed

            resultados = await asyncio.gather(*(armar_edicion(e) for e in ediciones))
            return list(resultados)
