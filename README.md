# 🏛️ legismex

> Biblioteca en Python para facilitar el acceso y análisis de información legislativa en México. 🇲🇽


### 🏛️ Soporte Multi-Cámara
*   **Cámara de Diputados:** Soporte robusto para la Gaceta Parlamentaria (`gaceta.diputados.gob.mx`), abstrayendo `framesets` antiguos en una API moderna.
*   **Senado de la República (Beta):** Integración inicial con `www.senado.gob.mx` para extraer la gaceta diaria estructurada por categorías.

### 🛠️ Capacidades de Extracción
*   **Votaciones Detalladas:** Analiza el concentrado por periodo y extrae la votación particular de cada dictamen, incluyendo sumatorias de votos.
*   **Motores de Búsqueda (HTDIG):** Conexión directa a buscadores internos para localizar iniciativas, proposiciones y dictámenes por palabra clave.
*   **Iniciativas y Seguimiento:** Obtiene el estatus de trámite, promotores y links directos (PDF/HTML) de asuntos en comisiones.
*   **Instrumentos Legislativos:** Acceso a Actas, Acuerdos, Agendas y Asistencias de forma indexada.


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

### 5. Buscar Dictámenes
Busca dictámenes en la base de datos de la Gaceta y devuelve detalles como a favor y en contra, usando un término de búsqueda.

```python
dictamenes = client.buscar_dictamenes(legislatura="66", palabra_clave="ley")

for d in dictamenes[:2]:
    print(f"[{d.fecha}] {d.titulo}")
    print(f"Trámites: {d.tramites}")
    print(f"PDF: {d.url_pdf}")
```
*   **Retorna:** Una lista de objetos `Dictamen`.

### 6. Extraer Proposiciones, Actas, Asistencias, Acuerdos y Agendas
`legismex` también provee métodos de extracción limpia para documentos genéricos, así como búsqueda avanzada de proposiciones con punto de acuerdo:

```python
# Buscar proposiciones que hablen de 'salud' en la L66
propos = client.buscar_proposiciones(legislatura="66", palabra_clave="salud")

# Obtener listado estático de URLs hacia actas de Pleno o Acuerdos
actas = client.obtener_actas(legislatura="66")
asistencias = client.obtener_asistencias()

print(f"Total proposiciones de salud: {len(propos)}")
print(f"Total actas registradas: {len(actas)}")
```

### 7. Gaceta del Senado (Beta)
El submódulo `legismex.senado` permite interactuar con el portal de la Cámara Alta, extrayendo los documentos de la gaceta del día estructurados por categorías.

```python
from legismex.senado import SenadoClient

senado = SenadoClient()
gaceta = senado.obtener_gaceta_del_dia(legislatura="66")

print(f"Edición: {gaceta.titulo_edicion}")
print(f"Total Documentos: {len(gaceta.documentos)}")
print(gaceta.documentos[0].categoria) # ej. "Comunicaciones de Comisiones"
```

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
*   **`Dictamen`**: Representa el resultado de búsqueda de un dictamen.
    *   `fecha`: str
    *   `titulo`: str
    *   `tramites`: str
    *   `url_gaceta`: Optional[str]
    *   `url_pdf`: Optional[str]
*   **`Proposicion`**: Similar a Iniciativa, con datos como: `fecha_presentacion`, `titulo`, `promovente`, `tramite_o_estado`, `aprobada`, `url_gaceta`, `url_pdf`.
*   **`DocumentoGaceta`**: Enlace estático para Asistencias, Agendas o Actas sumamente sencillo (`fecha_o_titulo`, `url_documento`).
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

#### Modelos del Senado
*   **`GacetaSenado`**: Colección raíz de una gaceta diaria o de sesión.
    *   `titulo_edicion`: str
    *   `documentos`: List[DocumentoSenado]
*   **`DocumentoSenado`**: Instancia validada de un asunto publicado en Senado.
    *   `titulo`: str
    *   `url`: str
    *   `categoria`: str

## Hoja de Ruta
*   Mejorar la extracción per-se del texto interno de los `PDFs` descargados desde Gaceta usando OCR o PyMuPDF.
*   **[DESCARTADO POR AHORA]** Integración directa con las tablas del Sistema de Información Legislativa (SIL) dadas las altas restricciones de origen y WAF anti-scraping en subpáginas de iniciativas.
