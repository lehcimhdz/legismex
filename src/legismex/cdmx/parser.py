import re
from bs4 import BeautifulSoup
from typing import List

from legismex.cdmx.models import DocumentoCdmx


class CdmxParser:
    """
    Parser oficial para las estructuras HTML devueltas por el Congreso de la Ciudad de México.
    Extrae alertas de descargas de PDFs extremadamente pesados.
    """

    BASE_URL = "https://www.congresocdmx.gob.mx"

    @staticmethod
    def parse_alertas_pdf(html_content: str) -> List[DocumentoCdmx]:
        """
        Escanea un archivo HTML buscando contenedores <div class="alert">
        que almacenan enlaces directos a los compilados en PDF de las Gacetas o Diarios de Debate.
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        documentos = []

        # Buscamos todos los contenedores alert
        alertas = soup.find_all('div', class_='alert')

        for alert in alertas:
            # 1. URL PDF
            enlace = alert.find('a')
            if not enlace or not enlace.get('href'):
                continue

            href = enlace['href'].strip()
            # Asegurar URL absoluta
            if not href.startswith('http'):
                url_pdf = f"{CdmxParser.BASE_URL}/{href}"
            else:
                url_pdf = href

            # 2. Título (Usualmente en <strong> dentro del body del alert)
            titulo = ""
            tag_strong = alert.find('strong')
            if tag_strong:
                titulo = tag_strong.get_text(separator=' ', strip=True)

            # 3. Metadatos (Fecha de publicación y tamaño)
            fecha = ""
            peso_etiqueta = ""
            peso_kb = 0.0

            span_meta = alert.find('span', class_='g-font-size-12')
            if span_meta:
                meta_text = span_meta.get_text(strip=True)
                # Formato usual: Fecha de publicación: 03-03-2026 | Tamaño: 44,490 kb.
                if '|' in meta_text:
                    partes = meta_text.split('|')
                    # Extraer fecha
                    fecha_str = partes[0].replace(
                        "Fecha de publicación:", "").strip()
                    if fecha_str:
                        fecha = fecha_str

                    # Extraer tamaño
                    if len(partes) > 1:
                        tamano_str = partes[1].replace("Tamaño:", "").strip()
                        peso_etiqueta = tamano_str

                        # Extraer solo el número flotante (ej "44,490" -> 44490.0)
                        num_match = re.search(r'([\d.,]+)', tamano_str)
                        if num_match:
                            limpio = num_match.group(1).replace(',', '')
                            try:
                                peso_kb = float(limpio)
                            except ValueError:
                                pass

            if titulo and url_pdf:
                documentos.append(
                    DocumentoCdmx(
                        titulo=titulo,
                        fecha=fecha,
                        peso_kb=peso_kb,
                        peso_etiqueta=peso_etiqueta,
                        url_pdf=url_pdf
                    )
                )

        return documentos
