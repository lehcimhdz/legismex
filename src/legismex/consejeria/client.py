import os
import time
from typing import List, Optional

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

from legismex.consejeria.models import GacetaConsejeria

class ConsejeriaClient:
    """
    Cliente para interactuar con la Gaceta Oficial de la Ciudad de México,
    alojada en el portal de la Consejería Jurídica (ZK Framework).
    Dada su arquitectura AJAX fuertemente acoplada, este submódulo requiere `playwright`.
    """
    
    BASE_URL = "https://data.consejeria.cdmx.gob.mx/BusquedaGaceta/"
    
    def __init__(self, headless: bool = True):
        if sync_playwright is None:
            raise ImportError(
                "El módulo legismex.consejeria requiere playwright instalado. "
                "Instálalo usando: pip install 'legismex[consejeria]' o 'pip install playwright' "
                "y posteriormente ejecuta 'playwright install chromium'."
            )
        self.headless = headless

    def _ejecutar_busqueda_interna(self, page, criterio: Optional[str] = None, fecha: Optional[str] = None):
        """
        Navega a la url y llena el formulario correspondiente.
        """
        page.goto(self.BASE_URL, wait_until='networkidle')
        
        if fecha:
            # Seleccionar pestaña Buscar por Fecha
            tab_fecha = page.locator('span.z-tab-text', has_text="POR FECHA").first
            tab_fecha.wait_for()
            tab_fecha.click()
            time.sleep(1) # animacion zk
            
            # Hay dos inputs en POR FECHA
            # ZK permite escribir en readonly usando force evaluate o invocando click
            # Vamos a usar evaluate para sobreescribir los dateboxes
            inputs = page.locator('input.z-datebox-input')
            inputs.nth(0).evaluate(f"el => el.value = '{fecha}'")
            inputs.nth(1).evaluate(f"el => el.value = '{fecha}'")
            
            # Clic al botón buscar de la tab Fecha
            # Es el segundo o tercer icono de busqueda en el DOM, busquemos el visible
            search_btns = page.locator('img[src="/BusquedaGaceta/images/buscar.png"]')
            for i in range(search_btns.count()):
                btn = search_btns.nth(i)
                if btn.is_visible():
                    btn.click()
                    break
        elif criterio:
            # Quedarse en la pestaña BÚSQUEDA (default)
            textbox = page.locator('input.z-textbox').first
            textbox.wait_for()
            textbox.fill(criterio)
            
            search_btns = page.locator('img[src="/BusquedaGaceta/images/buscar.png"]')
            for i in range(search_btns.count()):
                btn = search_btns.nth(i)
                if btn.is_visible():
                    btn.click()
                    break
        else:
            # Busqueda general sin filtros (devuelve los mas recientes)
            search_btns = page.locator('img[src="/BusquedaGaceta/images/buscar.png"]')
            for i in range(search_btns.count()):
                btn = search_btns.nth(i)
                if btn.is_visible():
                    btn.click()
                    break

        # Esperamos a que la tabla de resultados cargue
        # La tabla correcta es un z-grid que tiene una columna PUBLICACIÓN
        target_grid = page.locator('div.z-grid:has(th.z-column:has-text("PUBLICACIÓN"))')
        try:
            target_grid.locator('tr.z-row').first.wait_for(timeout=15000)
        except Exception:
            return None # no results or timeout
            
        return target_grid.locator('tr.z-row')

    def buscar_gacetas(self, criterio: Optional[str] = None, fecha: Optional[str] = None) -> List[GacetaConsejeria]:
        """
        Inicia un navegador Chromium headless, realiza la búsqueda y parsea los elementos.
        """
        resultados = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            
            rows = self._ejecutar_busqueda_interna(page, criterio, fecha)
            if rows:
                for i in range(rows.count()):
                    r = rows.nth(i)
                    cells = r.locator('td')
                    if cells.count() >= 5:
                        descripcion = cells.nth(0).inner_text().strip()
                        pub = cells.nth(1).inner_text().strip()
                        num = cells.nth(2).inner_text().strip()
                        
                        btn_pdf = cells.nth(4).locator('img[src="/BusquedaGaceta/images/pdf-16.png"]')
                        tiene_pdf = btn_pdf.count() > 0
                        
                        resultados.append(
                            GacetaConsejeria(
                                descripcion=descripcion,
                                fecha=pub,
                                numero=num,
                                tiene_pdf=tiene_pdf,
                                tiene_indice=True,
                                index_absoluto=i
                            )
                        )
            browser.close()
        return resultados

    def descargar_gaceta(self, gaceta: GacetaConsejeria, criterio: Optional[str] = None, fecha: Optional[str] = None, ruta_destino: str = "./gaceta.pdf") -> Optional[str]:
        """
        Re-ejecuta el contexto de la búsqueda de ZK internamente, localiza el índice absoluto
        del resultado parametrizado, e intercepta el objeto de descarga File de Chromium.
        """
        if not gaceta.tiene_pdf or gaceta.index_absoluto == -1:
            print("Esta gaceta no posee un PDF descargable disponible.")
            return None

        # Asegurar directorio
        directorios = os.path.dirname(ruta_destino)
        if directorios:
             os.makedirs(directorios, exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            
            print(f"Abriendo navegador para interceptar Gaceta {gaceta.numero}...")
            rows = self._ejecutar_busqueda_interna(page, criterio, fecha)
            
            if rows and rows.count() > gaceta.index_absoluto:
                target_row = rows.nth(gaceta.index_absoluto)
                pdf_btn = target_row.locator('td').nth(4).locator('button').first
                
                print("Esperando binario desde ZK Server...")
                try:
                    with page.expect_download(timeout=60000) as download_info:
                        pdf_btn.click()
                    download = download_info.value
                    download.save_as(ruta_destino)
                    print(f"¡Descarga de la Gaceta CDMX exitosa en: {ruta_destino}!")
                    browser.close()
                    return ruta_destino
                except Exception as e:
                    print(f"Ocurrió un error al interceptar el frame de descarga: {e}")
            else:
                print("El estado ZK cambió o los parámetros no coinciden para replicar la sesión.")
                
            browser.close()
            return None
