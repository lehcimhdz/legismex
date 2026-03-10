from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .models import JaliscoEvento, JaliscoPunto, JaliscoDocumento
import re


def parse_eventos_dia(html: str, fecha: str) -> List[JaliscoEvento]:
    """Parse the main html returned by datos_eventos.php to extract the onclick configs"""
    eventos = []
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div')

    for div in divs:
        onclick = div.get('onclick')
        if onclick and 'trae_datos_fecha_sel' in onclick:
            # onclick="trae_datos_fecha_sel('2025-10-06',2,8901)"
            match = re.search(
                r"trae_datos_fecha_sel\('([^']+)',\s*(\d+),\s*(\d+)\)", onclick)
            if match:
                f, t, id_ev = match.groups()
                titulo = div.text.strip()
                eventos.append(JaliscoEvento(
                    fecha=f,
                    titulo=titulo,
                    tipo=int(t),
                    id_evento=int(id_ev)
                ))
    return eventos


def parse_orden_dia(html: str) -> List[Dict[str, Any]]:
    """Parse the Points returned by orden.php. It tracks their optional onclick sub_puntos handler"""
    puntos = []
    soup = BeautifulSoup(html, 'html.parser')

    container = soup.find('div', id="orden_del_dia")
    if not container:
        # fallback to find all .punto divs
        divs = soup.find_all('div', class_='punto')
    else:
        divs = container.find_all('div', class_='punto')

    for div in divs:
        titulo = div.text.strip()
        onclick = div.get('onclick')
        onclick_id = None
        onclick_tipo = None

        if onclick and 'sub_puntos' in onclick:
            match = re.search(r"sub_puntos\((\d+),\s*(\d+)\)", onclick)
            if match:
                onclick_id = int(match.group(1))
                onclick_tipo = int(match.group(2))

        puntos.append({
            "titulo": titulo,
            "onclick_id": onclick_id,
            "onclick_tipo": onclick_tipo
        })

    return puntos


def parse_subpuntos(html: str) -> List[JaliscoDocumento]:
    """Parse the Sub-points returned by suborden.php tracing back URLs inside <a> tags"""
    documentos = []
    soup = BeautifulSoup(html, 'html.parser')

    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href:
            # Find the title going backwards to the previous closest string or simply the parent block
            td = link.find_parent('td')
            if td:
                prev_td = td.find_previous_sibling('td')
                if prev_td:
                    titulo = prev_td.text.strip()
                else:
                    titulo = "Documento Adjunto"
            else:
                titulo = "Documento Adjunto"

            documentos.append(JaliscoDocumento(
                titulo=titulo,
                url=href.strip()
            ))

    return documentos
