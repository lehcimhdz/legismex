import httpx
from bs4 import BeautifulSoup
from typing import List, TypeVar, Type

from .models import (
    ColimaDocumentoBase,
    ColimaDecreto,
    ColimaAcuerdo,
    ColimaActa,
    ColimaDiarioDebate,
    ColimaIniciativa
)

T = TypeVar("T", bound=ColimaDocumentoBase)


class ColimaClient:
    """Cliente para la Gaceta Parlamentaria del H. Congreso del Estado de Colima."""
    BASE_URL = "https://congresocol.gob.mx/web/www/gaceta/plantilla_datos.php"
    BASE_DOMAIN = "https://congresocol.gob.mx"

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "timeout": 30.0,
            "verify": False,
            "follow_redirects": True,
            **kwargs,
        }

    def _limpiar_url(self, href: str) -> str:
        if not href or href == "N/A" or href == "#":
            return ""
        if href.startswith("http"):
            return href
        return f"{self.BASE_DOMAIN}{href}" if href.startswith("/") else f"{self.BASE_DOMAIN}/{href}"

    def _ejecutar_peticion(self, vtabla: str, legislatura_id: int, legislatura_nombre: str) -> str:
        params = {
            "v": vtabla,
            "l": str(legislatura_id),
            "ld": legislatura_nombre,
            "lc": "%"
        }
        with httpx.Client(**self.client_kwargs) as client:
            resp = client.post(self.BASE_URL, params=params)
            resp.raise_for_status()
            return resp.text

    async def _a_ejecutar_peticion(self, vtabla: str, legislatura_id: int, legislatura_nombre: str) -> str:
        params = {
            "v": vtabla,
            "l": str(legislatura_id),
            "ld": legislatura_nombre,
            "lc": "%"
        }
        async with httpx.AsyncClient(**self.client_kwargs) as client:
            resp = await client.post(self.BASE_URL, params=params)
            resp.raise_for_status()
            return resp.text

    def _parsear_html(self, html: str) -> List[BeautifulSoup]:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("div", class_="row")
        data_rows = []
        for r in rows:
            if r.get("style") and "border-bottom: 1px" in r.get("style", ""):
                # Filtrar si parece un row de encabezados
                first_cell = r.find("div")
                if first_cell:
                    text = first_cell.get_text(strip=True).upper()
                    if text in ["FECHA", "DECRETO", "ACUERDO", "INICIATIVA", "DESCRIPCIÓN"]:
                        continue
                data_rows.append(r)
        return data_rows

    # --- Síncronos ---

    def obtener_decretos(self, legislatura_id: int = 61, legislatura_nombre: str = "LXI Legislatura") -> List[ColimaDecreto]:
        html = self._ejecutar_peticion(
            "tdecretos", legislatura_id, legislatura_nombre)
        rows = self._parsear_html(html)
        resultados = []
        for r in rows:
            cols = r.find_all("div")
            if len(cols) >= 6:
                doc = cols[4].find("a")
                pdf = cols[5].find("a")
                resultados.append(ColimaDecreto(
                    numero=cols[0].get_text(strip=True),
                    descripcion=cols[1].get_text(strip=True),
                    fecha_aprobacion=cols[2].get_text(strip=True),
                    fecha_publicacion=cols[3].get_text(strip=True),
                    url_doc=self._limpiar_url(doc["href"] if doc else ""),
                    url_pdf=self._limpiar_url(pdf["href"] if pdf else "")
                ))
        return resultados

    def obtener_iniciativas(self, legislatura_id: int = 61, legislatura_nombre: str = "LXI Legislatura") -> List[ColimaIniciativa]:
        html = self._ejecutar_peticion(
            "tiniciativas", legislatura_id, legislatura_nombre)
        rows = self._parsear_html(html)
        resultados = []
        for r in rows:
            cols = r.find_all("div")
            if len(cols) >= 4:
                pdf = cols[3].find("a")
                txt_estado = cols[2].get_text(" ", strip=True)

                # Partir texto de estado ("Autor: X Comisión: Y Pendiente")
                autor = ""
                comision = ""
                status = txt_estado

                if "Autor:" in txt_estado:
                    partes = txt_estado.split("Comisión:")
                    autor = partes[0].replace("Autor:", "").strip()
                    if len(partes) > 1:
                        parte2 = partes[1]
                        if "Pendiente" in parte2:
                            comision = parte2.replace("Pendiente", "").strip()
                            status = "Pendiente"
                        elif "Aprobado" in parte2:
                            comision = parte2.replace("Aprobado", "").strip()
                            status = "Aprobado"
                        else:
                            comision = parte2.strip()
                            status = "Desconocido"

                resultados.append(ColimaIniciativa(
                    numero=cols[0].get_text(strip=True),
                    descripcion=cols[1].get_text(strip=True),
                    status=status,
                    autor=autor,
                    comision=comision,
                    url_pdf=self._limpiar_url(pdf["href"] if pdf else "")
                ))
        return resultados

    def obtener_diario_debates(self, legislatura_id: int = 61, legislatura_nombre: str = "LXI Legislatura") -> List[ColimaDiarioDebate]:
        html = self._ejecutar_peticion(
            "tdiario", legislatura_id, legislatura_nombre)
        rows = self._parsear_html(html)
        resultados = []
        for r in rows:
            cols = r.find_all("div")
            if len(cols) >= 4:
                doc = cols[2].find("a")
                pdf = cols[3].find("a")
                resultados.append(ColimaDiarioDebate(
                    fecha=cols[0].get_text(strip=True),
                    descripcion=cols[1].get_text(strip=True),
                    url_doc=self._limpiar_url(doc["href"] if doc else ""),
                    url_pdf=self._limpiar_url(pdf["href"] if pdf else "")
                ))
        return resultados

    def obtener_actas(self, legislatura_id: int = 61, legislatura_nombre: str = "LXI Legislatura") -> List[ColimaActa]:
        html = self._ejecutar_peticion(
            "tactas", legislatura_id, legislatura_nombre)
        rows = self._parsear_html(html)
        resultados = []
        for r in rows:
            cols = r.find_all("div")
            # Actas suelen tener [0] Desc, [1] FechaAprob, [2] FechaPub, [3] DOC, [4] PDF
            if len(cols) >= 5:
                doc = cols[3].find("a")
                pdf = cols[4].find("a")
                resultados.append(ColimaActa(
                    descripcion=cols[0].get_text(strip=True),
                    fecha_aprobacion=cols[1].get_text(strip=True),
                    fecha_publicacion=cols[2].get_text(strip=True),
                    url_doc=self._limpiar_url(doc["href"] if doc else ""),
                    url_pdf=self._limpiar_url(pdf["href"] if pdf else "")
                ))
        return resultados

    # --- Asíncronos ---

    async def a_obtener_decretos(self, legislatura_id: int = 61, legislatura_nombre: str = "LXI Legislatura") -> List[ColimaDecreto]:
        html = await self._a_ejecutar_peticion("tdecretos", legislatura_id, legislatura_nombre)
        rows = self._parsear_html(html)
        resultados = []
        for r in rows:
            cols = r.find_all("div")
            if len(cols) >= 6:
                doc = cols[4].find("a")
                pdf = cols[5].find("a")
                resultados.append(ColimaDecreto(
                    numero=cols[0].get_text(strip=True),
                    descripcion=cols[1].get_text(strip=True),
                    fecha_aprobacion=cols[2].get_text(strip=True),
                    fecha_publicacion=cols[3].get_text(strip=True),
                    url_doc=self._limpiar_url(doc["href"] if doc else ""),
                    url_pdf=self._limpiar_url(pdf["href"] if pdf else "")
                ))
        return resultados

    async def a_obtener_iniciativas(self, legislatura_id: int = 61, legislatura_nombre: str = "LXI Legislatura") -> List[ColimaIniciativa]:
        html = await self._a_ejecutar_peticion("tiniciativas", legislatura_id, legislatura_nombre)
        rows = self._parsear_html(html)
        resultados = []
        for r in rows:
            cols = r.find_all("div")
            if len(cols) >= 4:
                pdf = cols[3].find("a")
                txt_estado = cols[2].get_text(" ", strip=True)

                autor = ""
                comision = ""
                status = txt_estado

                if "Autor:" in txt_estado:
                    partes = txt_estado.split("Comisión:")
                    autor = partes[0].replace("Autor:", "").strip()
                    if len(partes) > 1:
                        parte2 = partes[1]
                        if "Pendiente" in parte2:
                            comision = parte2.replace("Pendiente", "").strip()
                            status = "Pendiente"
                        elif "Aprobado" in parte2:
                            comision = parte2.replace("Aprobado", "").strip()
                            status = "Aprobado"
                        else:
                            comision = parte2.strip()
                            status = "Desconocido"

                resultados.append(ColimaIniciativa(
                    numero=cols[0].get_text(strip=True),
                    descripcion=cols[1].get_text(strip=True),
                    status=status,
                    autor=autor,
                    comision=comision,
                    url_pdf=self._limpiar_url(pdf["href"] if pdf else "")
                ))
        return resultados

    async def a_obtener_diario_debates(self, legislatura_id: int = 61, legislatura_nombre: str = "LXI Legislatura") -> List[ColimaDiarioDebate]:
        html = await self._a_ejecutar_peticion("tdiario", legislatura_id, legislatura_nombre)
        rows = self._parsear_html(html)
        resultados = []
        for r in rows:
            cols = r.find_all("div")
            if len(cols) >= 4:
                doc = cols[2].find("a")
                pdf = cols[3].find("a")
                resultados.append(ColimaDiarioDebate(
                    fecha=cols[0].get_text(strip=True),
                    descripcion=cols[1].get_text(strip=True),
                    url_doc=self._limpiar_url(doc["href"] if doc else ""),
                    url_pdf=self._limpiar_url(pdf["href"] if pdf else "")
                ))
        return resultados

    async def a_obtener_actas(self, legislatura_id: int = 61, legislatura_nombre: str = "LXI Legislatura") -> List[ColimaActa]:
        html = await self._a_ejecutar_peticion("tactas", legislatura_id, legislatura_nombre)
        rows = self._parsear_html(html)
        resultados = []
        for r in rows:
            cols = r.find_all("div")
            if len(cols) >= 5:
                doc = cols[3].find("a")
                pdf = cols[4].find("a")
                resultados.append(ColimaActa(
                    descripcion=cols[0].get_text(strip=True),
                    fecha_aprobacion=cols[1].get_text(strip=True),
                    fecha_publicacion=cols[2].get_text(strip=True),
                    url_doc=self._limpiar_url(doc["href"] if doc else ""),
                    url_pdf=self._limpiar_url(pdf["href"] if pdf else "")
                ))
        return resultados
