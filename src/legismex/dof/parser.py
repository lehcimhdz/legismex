from bs4 import BeautifulSoup
from legismex.dof.models import DofEdicion, DofDocumento


class DofParser:
    """
    Clase utilitaria para convertir el HTML antiguo devuelto por el buscador y portal del 
    Diario Oficial de la Federación (dof.gob.mx) a objetos Pydantic.
    """

    @staticmethod
    def parse_edicion_dia(html_content: str, fecha_edicion: str = "Reciente") -> DofEdicion:
        """
        Extrae todos los documentos del concentrado del día.
        Itera sobre las filas del HTML determinando el contexto de la jerarquía (Sección -> Organismo -> Dependencia).

        :param html_content: Texto puro en HTML extraído de dof.gob.mx.
        :param fecha_edicion: Opcional. String para describir el periodo o la fecha actual.
        :return: Objeto DofEdicion con los documentos mapeados.
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        documentos = []

        current_seccion = "UNICA SECCION"
        current_poder = "SIN PODER"
        current_dependencia = "SIN DEPENDENCIA"

        # La tabla agrupa en cascada los datos
        for tr in soup.select('tr'):
            # Buscar Sección
            td_seccion = tr.find('td', class_='txt_blanco')
            if td_seccion and 'bgcolor' in td_seccion.attrs and td_seccion['bgcolor'] == '#737373':
                current_seccion = td_seccion.get_text(
                    strip=True).replace('\xa0', '').strip()
                continue

            # Buscar Poder/Organismo
            td_poder = tr.find('td', class_='txt_blanco2')
            if td_poder and 'bgcolor' in td_poder.attrs and td_poder['bgcolor'] == '#B2B2B2':
                current_poder = td_poder.get_text(
                    strip=True).replace('\xa0', '').strip()
                continue

            # Buscar Dependencia
            td_dep = tr.find('td', class_='subtitle_azul')
            if td_dep:
                dep_text = td_dep.get_text(
                    separator=' ', strip=True).replace('\xa0', '').strip()
                if dep_text.endswith("WORD"):
                    dep_text = dep_text[:-4].strip()

                if dep_text:
                    current_dependencia = dep_text
                continue

            # Buscar Documento
            enlace = tr.find('a', class_='enlaces')
            if enlace and 'nota_detalle.php' in enlace.get('href', ''):
                url = enlace['href']
                titulo = enlace.get_text(strip=True)

                documentos.append(
                    DofDocumento(
                        seccion=current_seccion,
                        organismo=current_poder,
                        dependencia=current_dependencia,
                        titulo=titulo,
                        url=url
                    )
                )

        return DofEdicion(
            fecha=fecha_edicion,
            documentos=documentos
        )
