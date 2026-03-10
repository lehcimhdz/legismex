from bs4 import BeautifulSoup
import re
from typing import List
from .models import PeriodoVotacion, VotacionDetalle, ResultadoBusqueda, Iniciativa, BaseDictamenes, Dictamen, DocumentoGaceta, Proposicion


class GacetaParser:
    """
    Parser especializado para extraer la información estructurada de la Gaceta Parlamentaria.
    """

    @staticmethod
    def parse_periodos_votacion(html: str) -> List[PeriodoVotacion]:
        """
        Extrae los periodos de votación (ej. 'Primer periodo ordinario LXVI') 
        del índice de Votaciones.
        """
        # Suprimir warning de XML al forzar html.parser
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all('a')

        periodos = []
        for l in links:
            href = l.get('href', '')
            texto = l.text.strip()

            # Buscamos links que apunten a /Gaceta/Votaciones/{Leg}/vot...
            if '/Gaceta/Votaciones/' in href and 'vot' in href:
                # Extraer número de legislatura de la ruta, ej: /Gaceta/Votaciones/66/vot66_a1primero.html
                partes = href.split('/')
                try:
                    # Penúltima carpeta suele ser la legisaltura (66, 65)
                    leg = int(partes[-2])
                    periodos.append(PeriodoVotacion(
                        legislatura=leg,
                        nombre=texto,
                        # Para urls que traigan el '/Gaceta/Votaciones' lo respetamos, si es relativa lo arregla el cliente
                        url_base=href
                    ))
                except (ValueError, IndexError):
                    pass

        return periodos

    @staticmethod
    def parse_votaciones_detalle(html: str) -> List[VotacionDetalle]:
        """
        Extrae la lista de votaciones individuales (Asunto, Acta, PDF, Votos)
        desde el código HTML del periodo.
        """
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all('li')
        votaciones = []

        for li in items:
            texto_puro = li.text.strip()

            # Buscando links de PDFs y de Actas (tabla...php3)
            links = li.find_all('a')
            url_pdf = None
            url_acta = None

            for a in links:
                href = a.get('href', '')
                if 'PDF' in href:
                    url_pdf = href
                elif 'Votaciones' in href and 'tabla' in href:
                    if not url_acta:
                        url_acta = href

            # Buscar fecha superior en la jerarquía (etiqueta <font color="#CC0000">)
            parent_ul = li.find_parent('ul')
            fecha_text = "Desconocida"
            if parent_ul:
                prev = parent_ul.find_previous_sibling()
                while prev:
                    if prev.name == 'font':
                        fecha_text = prev.text.strip()
                        break
                    prev = prev.find_previous_sibling()

            # Extraer conteo de votos
            fav = None
            contra = None
            abs = None

            m_fav = re.search(
                r'(\d+)\s+votos\s+(en\s+pro|a\s+favor)', texto_puro, re.IGNORECASE)
            m_contra = re.search(r'(\d+)\s+(en\s+contra)',
                                 texto_puro, re.IGNORECASE)
            m_abs = re.search(r'(\d+)\s+(abstenc)', texto_puro, re.IGNORECASE)

            if m_fav:
                fav = int(m_fav.group(1))
            if m_contra:
                contra = int(m_contra.group(1))
            if m_abs:
                abs = int(m_abs.group(1))

            votaciones.append(VotacionDetalle(
                fecha=fecha_text,
                asunto=texto_puro,  # El texto crudo tiene la síntesis completa
                url_acta=url_acta,
                url_pdf=url_pdf,
                votos_favor=fav,
                votos_contra=contra,
                abstenciones=abs
            ))

        return votaciones

    @staticmethod
    def parse_resultados_busqueda(html: str, palabra_clave: str) -> List[ResultadoBusqueda]:
        """
        Extrae los resultados de búsqueda de Gaceta desde el motor interno (HTDIG).
        """
        soup = BeautifulSoup(html, "html.parser")
        resultados = []
        dls = soup.find_all('dl')

        for dl in dls:
            titulo = ""
            url_origen = ""
            contexto = ""

            dt = dl.find('dt')
            if dt:
                a = dt.find('a')
                if a:
                    titulo = a.text.strip()
                    url_origen = a.get('href', '')

            dd = dl.find('dd')
            if dd:
                contexto = dd.text.strip()

            # Extraer fecha desde el título heurísticamente ("Gaceta Parlamentaria ..., miércoles 30 de abril de 2025")
            fecha_ext = titulo.split(
                ',')[-1].strip() if ',' in titulo else titulo

            resultados.append(ResultadoBusqueda(
                palabra_clave=palabra_clave,
                fecha=fecha_ext,
                contexto=contexto,
                url_origen=url_origen,
                # En gaceta el PDF usualmente tiene el mismo prefijo que su origin HTML,
                # ej: .../2025/abr/20250430-X.html -> .../2025/abr/20250430-X.pdf
                url_pdf=url_origen.replace(
                    '.html', '.pdf') if url_origen.endswith('.html') else None
            ))

        return resultados

    @staticmethod
    def parse_iniciativas(html: str) -> List[Iniciativa]:
        """
        Extrae las iniciativas de los resultados de búsqueda de la Gaceta Parlamentaria.
        """
        soup = BeautifulSoup(html, "html.parser")
        iniciativas = []

        # Las iniciativas están generalmente dentro de <p><font size="-1">
        parrafos = soup.find_all('p')
        for p in parrafos:
            font = p.find('font', size="-1")
            if not font:
                continue

            texto_html = font.decode_contents()

            # Buscar explícitamente el marcador "Fecha:" para confirmar
            if "Fecha:" not in texto_html:
                continue

            partes = [t.strip()
                      for t in texto_html.split('<br/>') if t.strip()]

            # Inicializar los campos
            fecha = ""
            titulo = ""
            promovente = ""
            tramite = ""
            url_gaceta = None
            url_pdf = None
            dictaminada = False

            for index, linea in enumerate(partes):
                # Usar BeautifulSoup en cada línea para extraer los links y quitar formato (ej. <b>)
                linea_soup = BeautifulSoup(linea, "html.parser")
                texto_limpio = linea_soup.get_text().strip()

                if texto_limpio.startswith("Fecha:"):
                    fecha = texto_limpio.replace("Fecha:", "").strip()
                elif texto_limpio.startswith("Que reforma") or texto_limpio.startswith("De decreto") or texto_limpio.startswith("Que adiciona") or texto_limpio.startswith("Que expide"):
                    titulo = texto_limpio
                elif texto_limpio.startswith("Presentada por"):
                    promovente = texto_limpio
                elif ("Turnada" in texto_limpio or "Desechada" in texto_limpio or "Aprobada" in texto_limpio or "Prórroga" in texto_limpio or "Retirada" in texto_limpio or "Dictaminada" in texto_limpio):
                    if not tramite:  # Guardar el primer trámite como principal
                        tramite = texto_limpio
                    else:  # Acumular el historial de trámites
                        tramite += f" | {texto_limpio}"

                    if "Dictaminada" in texto_limpio or "Aprobada" in texto_limpio:
                        dictaminada = True

                # Buscar enlaces
                for a in linea_soup.find_all('a'):
                    href = a.get('href', '')
                    if href:
                        # Si contiene .pdf es el PDF
                        if href.lower().endswith('.pdf') or 'PDF' in href:
                            url_pdf = href
                        # Si contiene Gaceta Parlamentaria, es el documento HTML de gaceta
                        elif 'Gaceta Parlamentaria' in a.text or '.html' in href:
                            url_gaceta = href

            if fecha and (titulo or promovente):
                iniciativas.append(Iniciativa(
                    fecha_presentacion=fecha,
                    titulo=titulo,
                    promovente=promovente,
                    tramite_o_estado=tramite,
                    url_gaceta=url_gaceta,
                    url_pdf=url_pdf,
                    dictaminada=dictaminada
                ))

        return iniciativas

    @staticmethod
    def parse_bases_dictamenes(html: str) -> List[BaseDictamenes]:
        """
        Extrae el índice de las bases de datos de dictámenes por legislatura.
        """
        soup = BeautifulSoup(html, "html.parser")
        bases = []

        # Buscar todos los enlaces <a href="/base/dictas/...">LXVI Legislatura</a>
        links = soup.find_all('a', href=re.compile(r'/base/dictas/\d+/'))

        for a in links:
            url = a.get('href', '')
            titulo = a.text.strip()

            # Buscar el hermano siguiente que es un <br> y luego el <font size="-1">
            periodo = ""
            nxt = a.find_next_sibling('font')
            if nxt:
                periodo = nxt.text.strip()

            # Extraer número de legislatura de la URL (e.g. /base/dictas/66/...)
            m = re.search(r'/dictas/(\d+)/', url)
            leg_num = int(m.group(1)) if m else 0

            if titulo and leg_num:
                bases.append(BaseDictamenes(
                    legislatura=leg_num,
                    titulo=titulo,
                    periodo=periodo,
                    url_base=url
                ))

        return bases

    @staticmethod
    def parse_dictamenes(html: str) -> List[Dictamen]:
        """
        Extrae los dictámenes desde la página de resultados de la Gaceta.
        (Ej: búsqueda por palabra en los dictámenes).
        """
        soup = BeautifulSoup(html, "html.parser")
        dictamenes = []
        html_str = str(soup)

        # Separar estrictamente por la cadena "Fecha: " ya que la Gaceta a veces no anida bien los <p>
        chunks = html_str.split('Fecha: ')
        for chunk in chunks[1:]:
            # Tolerar variaciones de saltos de línea
            partes = re.split(r'(?i)<br\s*/?>', chunk)
            if not partes:
                continue

            # Extraer fecha
            fecha = BeautifulSoup(partes[0], "html.parser").get_text(
            ).strip().split('<')[0].strip()

            titulo = ""
            tramites = ""
            url_gaceta = None
            url_pdf = None

            for idx, linea in enumerate(partes[1:]):
                linea_soup = BeautifulSoup(linea, "html.parser")
                texto_limpio = linea_soup.get_text().strip()

                if (texto_limpio.startswith("De la") or texto_limpio.startswith("Minuta") or texto_limpio.startswith("Iniciativa") or texto_limpio.startswith("Dictamen")):
                    if not titulo:
                        titulo = texto_limpio
                elif texto_limpio and not texto_limpio.startswith("<!--") and "Fecha:" not in texto_limpio:
                    if not tramites:
                        tramites = texto_limpio
                    else:
                        tramites += f" | {texto_limpio}"

                for a in linea_soup.find_all('a'):
                    href = a.get('href', '')
                    if href:
                        if href.lower().endswith('.pdf') or 'PDF' in href:
                            url_pdf = href
                        elif 'Gaceta' in a.text or '.html' in href or '.php3' in href:
                            if not url_gaceta or ('Gaceta' in a.text and '.pdf' not in href):
                                url_gaceta = href

            if fecha and titulo:
                tramites = re.sub(r'<!--.*?-->', '', tramites).strip()
                # Asegurar que no pasen etiquetas HTML
                tramites = BeautifulSoup(tramites, "html.parser").get_text()

                dictamenes.append(Dictamen(
                    fecha=fecha,
                    titulo=titulo,
                    tramites=tramites if tramites else "Sin trámite registrado",
                    url_gaceta=url_gaceta,
                    url_pdf=url_pdf
                ))

        return dictamenes

    @staticmethod
    def parse_documentos_gaceta(html: str, base_url: str) -> List[DocumentoGaceta]:
        """
        Extrae un listado genérico de enlaces a documentos estáticos
        (Actas, Acuerdos, Agendas, Asistencias).
        """
        soup = BeautifulSoup(html, "html.parser")
        docs = []

        # Muchas veces estos listados son puras etiquetas <a> sueltas
        for a in soup.find_all('a', href=True):
            texto = a.get_text().strip()
            href = a['href'].strip()

            # Evitar anclajes internos de la página o correos
            if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('javascript:'):
                continue

            # Evitar enlaces repetitivos de navegación superior
            if texto.lower() in ["home page", "búsquedas", "busca", "regresar", "gaceta parlamentaria"]:
                continue

            # Algunos href vienen con "file://..." en Gaceta, limpiar si pasa
            if href.startswith('http'):
                url_doc = href
            else:
                if href.startswith('/'):
                    url_doc = base_url + href
                else:
                    url_doc = base_url + "/" + href

            docs.append(DocumentoGaceta(
                fecha_o_titulo=texto if texto else "Documento sin título",
                url_documento=url_doc
            ))

        return docs

    @staticmethod
    def parse_proposiciones(html: str) -> List[Proposicion]:
        """
        Extrae proposiciones del buscador HTDIG (Estructura casi idéntica a Inicativas).
        """
        soup = BeautifulSoup(html, "html.parser")
        propos = []
        html_str = str(soup)

        # Igual que iniciativas, separar por "<b>Fecha:</b>" por HTML malformado
        chunks = html_str.split('<b>Fecha:</b>')
        for chunk in chunks[1:]:
            partes = re.split(r'(?i)<br\s*/?>', chunk)
            if not partes:
                continue

            fecha = BeautifulSoup(partes[0], "html.parser").get_text(
            ).strip().split('<')[0].strip()

            titulo = ""
            promotores = ""
            tramite = ""
            aprobada = False
            url_gaceta = None
            url_pdf = None

            for idx, linea in enumerate(partes[1:]):
                linea_soup = BeautifulSoup(linea, "html.parser")
                texto_limpio = linea_soup.get_text().strip()

                if texto_limpio.startswith("Con punto de") or texto_limpio.startswith("Proposición"):
                    if not titulo:
                        titulo = texto_limpio
                elif texto_limpio.startswith("Presentad") or texto_limpio.startswith("Suscrit"):
                    if not promotores:
                        promotores = texto_limpio
                elif texto_limpio and not texto_limpio.startswith("<!--") and "Fecha:" not in texto_limpio:
                    if not tramite:
                        tramite = texto_limpio
                    else:
                        tramite += f" | {texto_limpio}"

                    if "Aprobada" in texto_limpio or "aprobada" in texto_limpio:
                        aprobada = True

                for a in linea_soup.find_all('a'):
                    href = a.get('href', '')
                    if href:
                        if href.lower().endswith('.pdf') or 'PDF' in href:
                            url_pdf = href
                        elif 'Gaceta' in a.text or '.html' in href or '.php3' in href:
                            if not url_gaceta or ('Gaceta' in a.text and '.pdf' not in href):
                                url_gaceta = href

            if fecha and titulo:
                # Limpiar residuos HTML y ruidos de búsqueda HTDIG
                tramite = re.sub(r'<!--.*?-->', '', tramite).strip()
                tramite = BeautifulSoup(tramite, "html.parser").get_text()
                tramite = re.sub(r'Se encontró.*', '', tramite,
                                 flags=re.IGNORECASE).strip()

                propos.append(Proposicion(
                    fecha_presentacion=fecha,
                    titulo=titulo,
                    promovente=promotores if promotores else "No especificado",
                    tramite_o_estado=tramite if tramite else "Sin trámite registrado",
                    url_gaceta=url_gaceta,
                    url_pdf=url_pdf,
                    aprobada=aprobada
                ))

        return propos
