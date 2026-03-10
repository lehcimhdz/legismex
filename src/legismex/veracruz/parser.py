import re
from typing import List
from bs4 import BeautifulSoup
from .models import VeracruzSesion, VeracruzDocumento


class VeracruzParser:
    """Parsea el HTML de legisver.gob.mx para extraer sesiones legislativas,
    versiones estenográficas, actas, audios, videos y anexos con iniciativas.
    """

    @staticmethod
    def _clean_url(href: str) -> str | None:
        """Extrae o limpia el URL. Las descargas usan javascript:PDF() 
        o URLs relativos de forma inconsistente."""
        if not href:
            return None
        href = href.strip()

        if "javascript:PDF(" in href:
            m = re.search(r"javascript:PDF\(['\"]([^'\"]+)['\"]\)", href)
            if m:
                path = m.group(1).lstrip("../")
                if not path.startswith("http"):
                    return f"https://www.legisver.gob.mx/{path}"
                return path

        if not href.startswith("http") and href and href != "#":
            path = href.lstrip("../")
            return f"https://www.legisver.gob.mx/{path}"

        return href if href and href != "#" else None

    def parse_sesiones(self, html: str) -> List[VeracruzSesion]:
        """Extrae el compendio completo de sesiones parseando las tablas
        anidadas en los contenedores divisores por año.
        """
        soup = BeautifulSoup(html, "lxml")
        sesiones: List[VeracruzSesion] = []

        # El contenido está separado en tabs con ids correspondientes a los años o legislatura.
        # Iteramos sobre los divs con clase col s12 y attributo id.
        for div_year in soup.select("div.col.s12[id]"):
            table = div_year.find("table")
            if not table:
                continue

            current_anio_ejercicio = ""
            current_periodo = ""
            current_sesion: VeracruzSesion | None = None

            for tr in table.select("tbody tr"):
                tds = tr.find_all("td")
                if not tds:
                    continue

                # Identificar separadores o headers de la tabla (Suelen tener colspan grande, 8 p.ej.)
                if len(tds) == 1 and tds[0].has_attr("colspan"):
                    texto_header = tds[0].text.strip()
                    if "Año de Ejercicio" in texto_header:
                        current_anio_ejercicio = texto_header
                    else:
                        current_periodo = texto_header
                    continue

                # Identificar Anexos vinculados a la sesión principal activa.
                # Estos ocupan 2 o más columnas visualmente saltando la fecha.
                is_anexo = False
                if len(tds) == 2 and tds[1].has_attr("colspan"):
                    is_anexo = True
                elif len(tds) > 1 and tds[1].get("colspan", "1") != "1":
                    # Muchas veces el colspan puede ser 5 u 8 y estar en tds[1] (la segunda col)
                    # o simplemente carece de la lista completa de TD
                    is_anexo = True

                if is_anexo and current_sesion:
                    a_tag = tds[1].find("a")
                    if a_tag:
                        anexo = VeracruzDocumento(
                            titulo=a_tag.text.strip(),
                            url_pdf=self._clean_url(a_tag.get("href")) or "",
                            es_anexo=True
                        )
                        # Solo agregarlo si extrajimos link
                        if anexo.url_pdf:
                            current_sesion.anexos.append(anexo)
                    continue

                # Si no es separador ni anexo, es una fila regular (sesión principal)
                if len(tds) >= 8:
                    td_fecha_text = tds[0].text.strip()
                    # A veces hay celdas fantasma donde la fila principal empieza vacía en fecha.
                    if not td_fecha_text:
                        continue

                    fecha = td_fecha_text
                    tipo_sesion = tds[1].text.strip()

                    # 2: Gaceta, 3: Versión Estenográfica, 4: Acta
                    gaceta_a = tds[2].find("a")
                    version_a = tds[3].find("a") if len(tds) > 3 else None
                    acta_a = tds[4].find("a") if len(tds) > 4 else None

                    # Extraer enlaces
                    gaceta_url = self._clean_url(
                        gaceta_a.get("href")) if gaceta_a else None
                    version_url = self._clean_url(
                        version_a.get("href")) if version_a else None
                    acta_url = self._clean_url(
                        acta_a.get("href")) if acta_a else None

                    # Instanciar nueva sesión y activarla
                    nueva_sesion = VeracruzSesion(
                        fecha=fecha,
                        tipo_sesion=tipo_sesion,
                        periodo=current_periodo,
                        anio_ejercicio=current_anio_ejercicio,
                        gaceta_pdf=gaceta_url,
                        acta_pdf=acta_url,
                        version_estenografica_pdf=version_url
                    )

                    # 5: Audio 1, 6: Audio 2, 7: Video 1, 8: Video 2
                    # Agrupar audios y videos según se encuentren enlaces
                    for col_idx in range(5, len(tds)):
                        col_a = tds[col_idx].find("a")
                        if col_a:
                            media_link = self._clean_url(col_a.get("href"))
                            if not media_link:
                                continue

                            if media_link.endswith((".mp3", ".ogg", "m4a")):
                                nueva_sesion.audio_urls.append(media_link)
                            elif media_link.endswith((".mp4", ".mov", ".avi", "youtube.com", "youtu.be")) or "video" in col_a.get("href", ""):
                                nueva_sesion.video_urls.append(media_link)

                    sesiones.append(nueva_sesion)
                    current_sesion = nueva_sesion

        return sesiones
