import re
from typing import Optional
from bs4 import BeautifulSoup
from legismex.senado.models import GacetaSenado, DocumentoSenado


class SenadoParser:
    """
    Parser para extraer componentes e información de la nueva Gaceta del Senado.
    """
    BASE_URL = "https://www.senado.gob.mx"

    @classmethod
    def _limpiar_url(cls, href: str) -> Optional[str]:
        if not href:
            return None
        if href.startswith('javascript:'):
            return None
        if href.startswith('http'):
            return href.strip()
        # Si es URL relativa, agregar el dominio del Senado
        return f"{cls.BASE_URL}{href.strip()}"

    @classmethod
    def parse_gaceta_dia(cls, html: str) -> GacetaSenado:
        """
        Extrae todos los documentos listados en la Gaceta del Senado de un día en particular.
        """
        soup = BeautifulSoup(html, 'html.parser')

        titulo_edicion = "Gaceta del Senado"

        headings = soup.find_all('div', class_='panel-heading')
        for h in headings:
            text = h.get_text(strip=True)
            if '/ Gaceta:' in text or 'Gaceta:' in text:
                titulo_edicion = text
                break

        lista_documentos = []

        # En el Senado, los documentos están dentro de filas de la tabla principal
        tabla = soup.select_one('section#mySection table.table-striped')

        filas = []
        if tabla:
            filas = tabla.find_all('tr', recursive=False)
            if not filas:
                tbodys = tabla.find_all('tbody', recursive=False)
                if tbodys:
                    filas = tbodys[0].find_all('tr', recursive=False)

        if not filas:
            # Fallback en caso de que cambien la estructura: buscar por divs panel-body
            filas = [div for div in soup.find_all(
                'div', class_='panel-body') if div.find('a')]

        categoria_actual = "Documento General"

        for fila in filas:
            # Si en esta fila se declara una nueva categoría, la actualizamos
            cat_div = fila.find('div', style=re.compile(
                r'background-color:\s*#cfcfcf', re.I))
            if cat_div:
                categoria_actual = cat_div.get_text(strip=True)

            enlaces = fila.find_all('a', href=True)
            for a in enlaces:
                url_original = a.get('href', '')

                # Nos interesan principalmente los documentos de la gaceta que enlazan a 'documento/{id}'
                if 'documento' not in url_original:
                    continue

                doc_nombre = a.get_text(strip=True)
                # A veces la etiqueta <a> envuelve otra etiqueta o no tiene texto directo
                if not doc_nombre:
                    parent = a.parent
                    if parent:
                        doc_nombre = parent.get_text(strip=True)

                url_absoluta = cls._limpiar_url(url_original)

                if doc_nombre and url_absoluta:
                    lista_documentos.append(
                        DocumentoSenado(
                            titulo=doc_nombre,
                            url=url_absoluta,
                            categoria=categoria_actual
                        )
                    )

        return GacetaSenado(
            titulo_edicion=titulo_edicion,
            documentos=lista_documentos
        )
