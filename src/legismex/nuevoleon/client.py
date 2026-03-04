import httpx
from bs4 import BeautifulSoup
from typing import List, Optional

from .models import NuevoLeonIniciativa

class NuevoLeonClient:
    """
    Cliente para extraer del H. Congreso del Estado de Nuevo León,
    basado en el volcado principal JSON usado para su DataTable.
    """
    BASE_URL = "https://www.hcnl.gob.mx/iniciativas_lxxvii/iniciativas.txt"

    def __init__(self, verify_ssl: bool = False):
        self.verify_ssl = verify_ssl

    def obtener_iniciativas(self, legislatura: Optional[str] = None) -> List[NuevoLeonIniciativa]:
        """
        Descarga todas las iniciativas disponibles del sitio web de NL.
        Dado que el sistema aloja hasta ~2,500 en un solo archivo plano,
        esta función descarga la totalidad y parsea sus campos envueltos en HTML.

        :param legislatura: Opcional. String exacto de la legislatura, ej. "LXXVII". 
                            Si se provee, filtra los resultados.
        :return: Lista de modelos `NuevoLeonIniciativa`.
        """
        resultados = []
        
        with httpx.Client(verify=self.verify_ssl) as client:
            # NL's DataTables consumen de este JSON plano gigante
            response = client.get(self.BASE_URL)
            response.raise_for_status()
            data = response.json()
            
            items = data.get("data", [])
            for row in items:
                # Filtrado por Legislatura antes de parsear HTML para ahorrar ciclos
                row_legislatura = row[10] if len(row) > 10 else ""
                
                if legislatura and getattr(row_legislatura, 'strip', lambda: '')() != legislatura:
                    continue
                    
                # Extracción y Limpieza
                # 0: <span class='badge'...>Exp, 21130 / LXXVII </span>
                exp_html = row[0] if len(row) > 0 else ""
                exp_clean = BeautifulSoup(exp_html, "html.parser").get_text(separator=" ").strip()
                
                # 9: Promovente oculto en texto plano (en la vista web esto se representa por un tag en col 2)
                promovente = row[9] if len(row) > 9 else ""
                
                # 4: Asunto <div class='txtsmall'><a href...
                asunto_html = row[4] if len(row) > 4 else ""
                asunto_clean = BeautifulSoup(asunto_html, "html.parser").get_text(separator=" ").strip()
                
                # 5: Comisión
                comision_html = row[5] if len(row) > 5 else ""
                comision_clean = BeautifulSoup(comision_html, "html.parser").get_text(separator=" ").strip()
                
                # 6: Fecha <div class='txtsmall'>25/02/2026</div>
                fecha_html = row[6] if len(row) > 6 else ""
                fecha_clean = BeautifulSoup(fecha_html, "html.parser").get_text(separator=" ").strip()
                
                # 7: Estado
                estado_html = row[7] if len(row) > 7 else ""
                estado_clean = BeautifulSoup(estado_html, "html.parser").get_text(separator=" ").strip()
                
                # 8: PDF <a href='https://...' ...
                pdf_html = row[8] if len(row) > 8 else ""
                url_pdf = None
                if pdf_html:
                    pdf_soup = BeautifulSoup(pdf_html, "html.parser")
                    a_tag = pdf_soup.find("a")
                    if a_tag and "href" in a_tag.attrs:
                        url_pdf = a_tag["href"]
                        # Si por alguna razón es relativa, construir absoluta
                        if url_pdf and not url_pdf.startswith("http"):
                            if url_pdf.startswith("/"):
                                url_pdf = f"https://www.hcnl.gob.mx{url_pdf}"
                            else:
                                url_pdf = f"https://www.hcnl.gob.mx/iniciativas_lxxvii/{url_pdf}"

                # Parsear y Appendar
                iniciativa = NuevoLeonIniciativa(
                    expediente=exp_clean,
                    legislatura=row_legislatura.strip() if row_legislatura else "",
                    promovente=promovente.strip(),
                    asunto=asunto_clean,
                    comision=comision_clean,
                    fecha=fecha_clean,
                    estado=estado_clean,
                    url_pdf=url_pdf
                )
                resultados.append(iniciativa)
                
        return resultados
