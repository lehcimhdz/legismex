# legismex

Biblioteca en Python para facilitar el trabajo legislativo en México. Extrae, estructura y provee acceso analítico a fuentes gubernamentales clásicas enfrentándose a retos técnicos (frames, SSL obsoletos). Pensado para monitoristas legislativos, analistas de datos y consultoras.

## Características Actuales (MVP: Gaceta Parlamentaria)

Actualmente, `legismex` ofrece soporte para la **Gaceta Parlamentaria de la Cámara de Diputados** (`gaceta.diputados.gob.mx`), abstrayendo sus subpáginas y `framesets` antiguos en una API moderna de Pydantic.

*   **Periodos de Votación:** Lista todos los periodos (ordinarios y extraordinarios) históricos de la Gaceta.
*   **Votaciones Detalladas:** Analiza el concentrado por periodo y extrae la votación particular de cada dictamen, incluyendo Actas, PDFs y la síntesis del texto, sumando los votos "A Favor", "En Contra" y "Abstenciones".
*   **Buscador HTDIG Empotrado:** Se conecta al buscador interno de la Gaceta para extraer contextos, fechas y enlaces de PDF de una "palabra clave" masivamente en distintas legislaturas.

## Instalación desde GitHub

Si deseas instalar y usar la biblioteca directamente en otro proyecto sin clonarla, puedes hacerlo instalándola mediante `pip` apuntando a tu repositorio de GitHub:

```bash
pip install git+https://github.com/lehcimhdz/legismex.git
```

*Nota: Asegúrate de tener Git instalado en el ambiente donde vas a ejecutar el comando `pip install`.*

*(Para desarrollo local)*:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Ejemplo de Uso

```python
from legismex.gaceta import GacetaClient

client = GacetaClient()

# -- 1. Explorar Periodos de Votación --
periodos = client.get_periodos_votacion()
ultimo = periodos[0]
print(f"[{ultimo.legislatura}] {ultimo.nombre}")

# -- 2. Obtener el Detalle Numérico de una Asamblea --
vots = client.get_votaciones_por_periodo(ultimo.url_base)
for v in vots[:3]:
    print(f"{v.fecha}: {v.votos_favor} A Favor, {v.votos_contra} En Contra")
    print(v.asunto)

# -- 3. Buscar Iniciativas/Asuntos Históricos por Palabra Clave --
resultados = client.buscar_palabra_clave("seguridad", legislatura="66")
for r in resultados[:3]:
    print(f"Contexto: {r.contexto}")
    print(f"Descargar PDF: {r.url_pdf}")
```

## Hoja de Ruta
*   Mejorar la extracción per-se del texto interno de los `PDFs` descargados desde Gaceta usando OCR o PyMuPDF.
*   **[DESCARTADO POR AHORA]** Integración directa con las tablas del Sistema de Información Legislativa (SIL) dadas las altas restricciones de origen y WAF anti-scraping en subpáginas de iniciativas.
