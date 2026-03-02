from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from .models import Legislador, IniciativaResumen, ReporteSesionResumen, ReporteSesionItem, ReporteSesionDetalle

class SILParser:
    """
    Clase utilitaria para parsear el HTML del SIL y convertirlo en modelos Pydantic.
    """
    @staticmethod
    def parse_legisladores(html: str) -> List[Legislador]:
        """Extrae la lista de legisladores desde la página de resultados del SIL."""
        soup = BeautifulSoup(html, "lxml")
        legisladores = []
        
        # Buscar todas las filas que contienen datos de legisladores
        filas = soup.find_all("tr", class_="ListDato")
        for fila in filas:
            celdas = fila.find_all("td")
            if len(celdas) >= 2:
                # Celda 0: Nombre y link a perfil
                a_tag = celdas[0].find("a")
                if not a_tag:
                    continue
                
                href = a_tag.get("href", "")
                id_sil = ""
                if "Referencia=" in href:
                    id_sil = href.split("Referencia=")[-1].split("&")[0]
                
                nombre_raw = a_tag.text.strip()
                # Separar apellidos y nombre (formato: "Apellidos, Nombre")
                partes_nombre = nombre_raw.split(",", 1)
                if len(partes_nombre) == 2:
                    apellidos = partes_nombre[0].strip()
                    nombre = partes_nombre[1].strip()
                else:
                    apellidos = nombre_raw
                    nombre = ""
                
                # Celda 1: Grupo Parlamentario
                grupo_parlamentario = celdas[1].text.strip()
                
                leg = Legislador(
                    id_sil=id_sil,
                    nombre_completo=nombre_raw,
                    apellidos=apellidos,
                    nombre=nombre,
                    camara="Por definir", # El listado general a veces no lo especifica, se deduce del request
                    grupo_parlamentario=grupo_parlamentario
                )
                legisladores.append(leg)
                
        return legisladores

    @staticmethod
    def parse_iniciativas(html: str) -> List[IniciativaResumen]:
        """Extrae la lista de iniciativas desde la página de resultados de búsqueda."""
        soup = BeautifulSoup(html, "lxml")
        iniciativas = []
        
        # TODO: Implementar lógica de extracción de la tabla de resultados. 
        # La tabla suele llamarse Resultados Busqueda.
        return iniciativas

    @staticmethod
    def parse_reportes_sesiones_resumen(html: str) -> List[ReporteSesionResumen]:
        """Extrae la lista de sesiones de la tabla principal."""
        soup = BeautifulSoup(html, "lxml")
        tables = soup.find_all('table')
        
        tabla_lista = None
        for t in tables:
            first_row = t.find('tr')
            if first_row:
                headers = [th.text.strip() for th in first_row.find_all(['td', 'th'])]
                if headers == ['Fecha', 'Hora', 'Tipo de sesión']:
                    tabla_lista = t
                    break
                    
        resumenes = []
        if tabla_lista:
            rows = tabla_lista.find_all('tr')
            if len(rows) > 1:
                data_rows = rows[1:]
            else:
                idx = tables.index(tabla_lista)
                data_table = tables[idx+1] if idx + 1 < len(tables) else None
                data_rows = data_table.find_all('tr') if data_table else []
                
            for row in data_rows:
                cells = row.find_all('td')
                if len(cells) == 3:
                    fecha_str = cells[0].text.strip()
                    hora = cells[1].text.strip()
                    tipo = cells[2].text.strip()
                    
                    a_tag = cells[0].find('a')
                    if a_tag and fecha_str:
                        url_det = a_tag.get('href', '')
                        # Si es Url relativa, la arreglamos en el Client
                        try:
                            fecha = datetime.strptime(fecha_str, "%d/%m/%Y").date()
                            resumenes.append(ReporteSesionResumen(
                                fecha=fecha, 
                                hora=hora, 
                                tipo_sesion=tipo, 
                                url_detalle=url_det
                            ))
                        except Exception:
                            pass
        return resumenes

    @staticmethod
    def parse_reporte_sesion_detalle(html: str) -> ReporteSesionDetalle:
        """Extrae el detalle estructurado y contenido crudo de una sesión."""
        soup = BeautifulSoup(html, "lxml")
        tables = soup.find_all('table')
        
        asuntos = []
        
        for i, t in enumerate(tables):
            texto = t.text.replace('\n', ' ').strip()
            # Identificar la tabla que tiene los detalles del promovente y trámite
            if 'Presentadora/Presentador:' in texto and 'Último Trámite:' in texto:
                # La tabla anterior [i-1] contiene el Tipo de asunto y el Título
                if i > 0:
                    prev_t = tables[i-1]
                    prev_texto = prev_t.text.replace('\n', ' ').strip()
                    
                    # Heurística simple para separar el título del tipo (suele estar separado por múltiples espacios)
                    partes_titulo = [p.strip() for p in prev_texto.split('  ') if len(p.strip()) > 0]
                    tipo_asunto = partes_titulo[0] if len(partes_titulo) > 0 else "Desconocido"
                    titulo = " ".join(partes_titulo[1:]) if len(partes_titulo) > 1 else prev_texto
                    
                    # Extraer promovente y trámite
                    tramite_split = texto.split('Último Trámite:')
                    promovente_raw = tramite_split[0].replace('Presentadora/Presentador:', '').strip()
                    tramite_raw = tramite_split[1].strip() if len(tramite_split) > 1 else ""
                    
                    item = ReporteSesionItem(
                        tipo_asunto=tipo_asunto,
                        titulo=titulo,
                        promovente=promovente_raw,
                        tramite=tramite_raw,
                        texto_crudo=prev_texto + " | " + texto
                    )
                    asuntos.append(item)
                    
        return ReporteSesionDetalle(
            asuntos=asuntos,
            texto_raw=soup.text # texto crudo completo para NLP
        )
