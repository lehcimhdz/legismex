import httpx
import asyncio
from typing import List
from datetime import datetime

from .models import QrooGaceta, QrooDocumento


class QrooClient:
    """Cliente para la Gaceta Parlamentaria del Estado de Quintana Roo."""
    BASE_URL = "https://congresoqroo.gob.mx/api/v1/gaceta"

    def __init__(self, **kwargs):
        self.client_kwargs = {
            "verify": False,
            "timeout": 30.0,
            **kwargs
        }

    def _parsear_gacetas(self, data: List[dict]) -> List[QrooGaceta]:
        resultados = []
        for x in data:
            try:
                # "2026-03-04" -> date
                fecha_pub = datetime.strptime(
                    x.get("fecha_publicacion", ""), "%Y-%m-%d").date()
                g = QrooGaceta(
                    id_gaceta=x.get("id", 0),
                    titulo=x.get("titulo", ""),
                    nomenclatura=x.get("nomenclatura", ""),
                    fecha_publicacion=fecha_pub,
                    extraordinaria=bool(x.get("extraordinaria", False)),
                    documentos=[]
                )
                resultados.append(g)
            except Exception:
                pass
        return resultados

    def _parsear_documentos(self, data: List[dict]) -> List[QrooDocumento]:
        docs = []
        for d in data:
            tipo = d.get("tipo_doc", "")
            titulo = d.get("titulo", "")
            url = d.get("url", "")

            # Hay ocasiones que no reporta URL
            if not url:
                continue

            # Hay logica local en el JS original respecto a `Correspondencia recibida`
            subtipo = d.get("subtipo_doc", "")
            if tipo == "acuerdo_externo" or subtipo == "acuerdo_externo":
                tipo = "Correspondencia recibida"

            docs.append(QrooDocumento(
                titulo=titulo,
                tipo_doc=tipo,
                url=url
            ))
        return docs

    def obtener_gacetas(self, anio: int, mes: int, extraer_documentos: bool = True) -> List[QrooGaceta]:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with httpx.Client(**self.client_kwargs) as client:
                mes_str = str(mes).zfill(2)
                url_mes = f"{self.BASE_URL}/?mes={mes_str}&anio={anio}"
                resp = client.get(url_mes)
                resp.raise_for_status()

                gacetas = self._parsear_gacetas(resp.json())

                if extraer_documentos and gacetas:
                    for g in gacetas:
                        url_doctos = f"{self.BASE_URL}/{g.id_gaceta}/doctos"
                        try:
                            resp_doc = client.get(url_doctos)
                            if resp_doc.status_code == 200:
                                g.documentos = self._parsear_documentos(
                                    resp_doc.json())
                        except httpx.RequestError:
                            pass

                return gacetas

    async def a_obtener_gacetas(self, anio: int, mes: int, extraer_documentos: bool = True) -> List[QrooGaceta]:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            async with httpx.AsyncClient(**self.client_kwargs) as client:
                mes_str = str(mes).zfill(2)
                url_mes = f"{self.BASE_URL}/?mes={mes_str}&anio={anio}"
                resp = await client.get(url_mes)
                resp.raise_for_status()

                gacetas = self._parsear_gacetas(resp.json())

                if extraer_documentos and gacetas:
                    tareas = []
                    for g in gacetas:
                        url_doctos = f"{self.BASE_URL}/{g.id_gaceta}/doctos"
                        tareas.append(client.get(url_doctos))

                    respuestas_docs = await asyncio.gather(*tareas, return_exceptions=True)
                    for gaceta, resp_doc in zip(gacetas, respuestas_docs):
                        if isinstance(resp_doc, httpx.Response) and resp_doc.status_code == 200:
                            gaceta.documentos = self._parsear_documentos(
                                resp_doc.json())

                return gacetas
