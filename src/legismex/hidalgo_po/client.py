import httpx
import asyncio
from typing import List, Optional
from datetime import date
from .models import HidalgoPoEdicion, HidalgoPoResultado


class HidalgoPoClient:
    """
    Cliente para el Periódico Oficial del Estado de Hidalgo (POEH).
    Permite buscar ediciones por fecha, término y tipo de edición.
    """
    BASE_URL = "https://periodico.hidalgo.gob.mx/s-internos/inventario/public/"
    AJAX_URL = f"{BASE_URL}ajax/buscar_periodicos.php"
    PDF_BASE_URL = "https://periodico.hidalgo.gob.mx/POEHpdfpublic/"

    def __init__(self, timeout: int = 30):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.BASE_URL}busqueda-periodicos.php"
        }
        self.timeout = timeout

    def _build_params(self, fecha_desde: date, fecha_hasta: date, term: str = "", tipo_edicion: str = "", page: int = 1) -> dict:
        return {
            "search_term": term,
            "tipo_edicion": tipo_edicion,
            "fecha_desde": fecha_desde.isoformat(),
            "fecha_hasta": fecha_hasta.isoformat(),
            "page": page
        }

    def _process_response(self, data: dict, page: int) -> HidalgoPoResultado:
        ediciones_raw = data.get("data", [])
        ediciones = []
        for item in ediciones_raw:
            # Construir URL del PDF usando el barcode
            barcode = item.get("barcode", "")
            url_pdf = f"{self.PDF_BASE_URL}{barcode}.pdf" if barcode else ""

            edicion = HidalgoPoEdicion(**item, url_pdf=url_pdf)
            ediciones.append(edicion)

        # Estimar paginación si no viene explícita (el JSON de Hidalgo suele ser simple)
        # Nota: Si el sitio proporciona 'total' o 'pages', usarlos aquí.
        # Basado en la exploración anterior, el JSON tiene 'data' pero no siempre metadatos de paginación claros.
        # Asumiremos valores por defecto o extraeremos si están presentes.
        return HidalgoPoResultado(
            ediciones=ediciones,
            # Pendiente: confirmar si viene el total real
            total_registros=len(ediciones),
            pagina_actual=page,
            total_paginas=1  # Pendiente: lógica de paginación avanzada
        )

    def buscar(self, fecha_desde: date, fecha_hasta: date, term: str = "", tipo_edicion: str = "", page: int = 1) -> HidalgoPoResultado:
        """Busca ediciones de forma síncrona."""
        params = self._build_params(
            fecha_desde, fecha_hasta, term, tipo_edicion, page)
        with httpx.Client(headers=self.headers, timeout=self.timeout, follow_redirects=True, verify=False) as client:
            response = client.get(self.AJAX_URL, params=params)
            response.raise_for_status()
            return self._process_response(response.json(), page)

    async def a_buscar(self, fecha_desde: date, fecha_hasta: date, term: str = "", tipo_edicion: str = "", page: int = 1) -> HidalgoPoResultado:
        """Busca ediciones de forma asíncrona."""
        params = self._build_params(
            fecha_desde, fecha_hasta, term, tipo_edicion, page)
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True, verify=False) as client:
            response = await client.get(self.AJAX_URL, params=params)
            response.raise_for_status()
            return self._process_response(response.json(), page)
