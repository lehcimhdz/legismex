# legismex

Biblioteca en Python para facilitar el trabajo legislativo en México. Extrae, estructura y provee acceso analítico a fuentes gubernamentales clásicas enfrentándose a retos técnicos (frames, SSL obsoletos). Pensado para monitoristas legislativos, analistas de datos y consultoras.

## Características Actuales (MVP: Gaceta Parlamentaria)

Actualmente, `legismex` ofrece soporte para la **Gaceta Parlamentaria de la Cámara de Diputados** (`gaceta.diputados.gob.mx`), abstrayendo sus subpáginas y `framesets` antiguos en una API moderna de Pydantic.

*   **Periodos de Votación:** Lista todos los periodos (ordinarios y extraordinarios) históricos de la Gaceta.
*   **Votaciones Detalladas:** Analiza el concentrado por periodo y extrae la votación particular de cada dictamen, incluyendo Actas, PDFs y la síntesis del texto, sumando los votos "A Favor", "En Contra" y "Abstenciones".
*   **Buscador HTDIG Empotrado:** Se conecta al buscador interno de la Gaceta para extraer contextos, fechas y enlaces de PDF de una "palabra clave" masivamente en distintas legislaturas.
*   **Iniciativas:** Accede al registro de iniciativas del Ejecutivo y de Grupos Parlamentarios, obteniendo el estatus de trámite, promotores y links directos a su publicación.

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

## Uso Detallado (API)

A continuación se explican las 4 funciones principales expuestas por `GacetaClient`. Todas retornan objetos de **Pydantic**, por lo que puedes acceder a sus datos como atributos (ej. `resultado.fecha`) o convertirlos a diccionarios con `.model_dump()`.

### 1. Obtener Periodos de Votación
Extrae el índice histórico de todos los periodos registrados en la Gaceta (Ordinarios, Extraordinarios, etc.).
```python
from legismex.gaceta import GacetaClient

client = GacetaClient()
periodos = client.get_periodos_votacion()

ultimo = periodos[0]
print(f"[{ultimo.legislatura}] {ultimo.nombre}")
```
*   **Retorna:** Una lista de objetos `PeriodoVotacion`.

### 2. Descargar Votaciones por Periodo
Extrae el detalle de cada votación ocurrida en un periodo específico (asuntos tratados, quién propuso, actas y el resultado numérico de la votación).
```python
# Usamos el URL base del periodo obtenido en el paso anterior
vots = client.get_votaciones_por_periodo(ultimo.url_base)

for v in vots[:3]:
    print(f"{v.fecha}: {v.votos_favor} A Favor, {v.votos_contra} En Contra")
    print(f"Dictamen: {v.url_pdf}")
```
*   **Retorna:** Una lista de objetos `VotacionDetalle`.

### 3. Buscar Iniciativas/Asuntos por Palabra Clave
Utiliza el motor de búsqueda interno (HTDIG) de la Gaceta para encontrar menciones de cualquier término en todos los diarios y gacetas históricas. Ideal para "Sub-Scrapping".
```python
# Busca la palabra "seguridad" en la Legislatura 66
resultados = client.buscar_palabra_clave("seguridad", legislatura="66")

for r in resultados[:3]:
    print(f"Contexto: {r.contexto}")
    print(f"Descargar PDF: {r.url_pdf}")
```
*   **Retorna:** Una lista de objetos `ResultadoBusqueda`.

### 4. Consultar Iniciativas
Extrae el concentrado de las iniciativas presentadas, conectándose a las bases de datos por legislatura de la Gaceta Parlamentaria.

```python
# Obtener todas las iniciativas de la Legislatura 66
iniciativas = client.obtener_iniciativas(legislatura="66", origen="T")

for ini in iniciativas[:3]:
    print(f"[{ini.fecha_presentacion}] {ini.titulo}")
    print(f"Estado: {ini.tramite_o_estado}")
    print(f"Dictaminada: {'Sí' if ini.dictaminada else 'No'}")
```
*   **Retorna:** Una lista de objetos `Iniciativa`.

## Referencia de Modelos (Pydantic)

La librería serializa la información escrapeada en los siguientes modelos fuertemente tipados:

*   **`PeriodoVotacion`**: Representa un semestre o lapso (ej. "Primer periodo ordinario LXVI").
    *   `legislatura`: int
    *   `nombre`: str
    *   `url_base`: str
*   **`VotacionDetalle`**: Representa el acta de una votación particular, con saldos de votos si aplica.
    *   `fecha`: str
    *   `asunto`: str (Contiene la síntesis legislativa)
    *   `url_acta`: Optional[str]
    *   `url_pdf`: Optional[str]
    *   `votos_favor`: Optional[int]
    *   `votos_contra`: Optional[int]
    *   `abstenciones`: Optional[int]
*   **`ResultadoBusqueda`**: Un hit devuelto por el buscador interno.
    *   `palabra_clave`: str
    *   `fecha`: str
    *   `contexto`: str (Extracto textual donde aparece la palabra clave)
    *   `url_origen`: str
    *   `url_pdf`: Optional[str]
*   **`Iniciativa`**: Registro de seguimiento de una iniciativa particular.
    *   `fecha_presentacion`: str
    *   `titulo`: str
    *   `promovente`: str
    *   `tramite_o_estado`: str
    *   `url_gaceta`: Optional[str]
    *   `url_pdf`: Optional[str]
    *   `dictaminada`: bool

## Hoja de Ruta
*   Mejorar la extracción per-se del texto interno de los `PDFs` descargados desde Gaceta usando OCR o PyMuPDF.
*   **[DESCARTADO POR AHORA]** Integración directa con las tablas del Sistema de Información Legislativa (SIL) dadas las altas restricciones de origen y WAF anti-scraping en subpáginas de iniciativas.
