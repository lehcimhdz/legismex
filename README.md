# 🏛️ legismex

> Biblioteca en Python para facilitar el acceso y análisis de información legislativa en México. 🇲🇽


### 🏛️ Soporte Multi-Cámara e Institucional
*   **Cámara de Diputados:** Soporte robusto para la Gaceta Parlamentaria (`gaceta.diputados.gob.mx`), abstrayendo `framesets` antiguos en una API moderna.
*   **Senado de la República:** Integración con `www.senado.gob.mx` para extraer la gaceta diaria estructurada por categorías y el histórico.
*   **Diario Oficial de la Federación:** Integración con `dof.gob.mx` extrayendo el concentrado diario por secciones y dependencias federales.
*   **Congreso de la Ciudad de México:** Rastreador especializado para recuperar y descargar PDFs pesados directos de los Diarios de Debate con barra de progreso interactivos.
*   **Consejería de la CDMX (Gaceta Oficial):** Extrae Gacetas evadiendo la ofuscación de *ZK Framework* a través de control headless nativo con Playwright.

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

*Nota: Si deseas extraer archivos de la Gaceta Oficial de la Consejería de la CDMX, requieres usar la "instalación avanzada" con `playwright`:*
```bash
pip install "legismex[consejeria] @ git+https://github.com/lehcimhdz/legismex.git"
playwright install chromium
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
El submódulo `legismex.senado` permite interactuar con el portal de la Cámara Alta, extrayendo los documentos de la gaceta del día estructurados por categorías y consultando el archivo histórico.

```python
from legismex.senado import SenadoClient

senado = SenadoClient()
gaceta = senado.obtener_gaceta_del_dia(legislatura="66")

print(f"Edición: {gaceta.titulo_edicion}")
print(f"Total Documentos: {len(gaceta.documentos)}")
print(gaceta.documentos[0].categoria) # ej. "Comunicaciones de Comisiones"

# Extraer el calendario histórico
historicas = senado.get_calendario_gacetas(year=2021, month=10)
print(f"Gacetas en Oct 2021: {len(historicas)}")

# Descargar gaceta específica desde el histórico
gaceta_pasada = senado.obtener_gaceta_por_url(historicas[0].url)
print(f"Edición histórica: {gaceta_pasada.titulo_edicion}")
```

### 8. Diario Oficial de la Federación (DOF)
El submódulo `legismex.dof` permite raspar e instanciar en tiempo real la publicación diaria del Diario Oficial de la Federación separada elegantemente por dependencias y secciones.

```python
from legismex.dof import DofClient

dof_client = DofClient()
edicion_hoy = dof_client.obtener_edicion_del_dia()

print(f"Edición: {edicion_hoy.fecha}")
print(f"Documentos publicados hoy: {len(edicion_hoy.documentos)}")

# Primer decreto
decreto1 = edicion_hoy.documentos[0]
print(f"[{decreto1.organismo}] {decreto1.dependencia}")
print(f"Decreto: {decreto1.titulo}")
print(f"URL: {decreto1.url}")
```

### 9. Congreso CDMX (Descargas Dinámicas con tqdm)
El submódulo `legismex.cdmx` facilita la interacción con el portal en Bootstrap del Congreso local, permitiendo iterar tomos y descargar archivos gigantes mostrando el progreso en tu terminal visualmente.

```python
from legismex.cdmx import CdmxClient

cdmx_client = CdmxClient(use_tqdm=True)

# Parsear un panel pre-renderizado del congreso
url = "https://www.congresocdmx.gob.mx/gaceta-parlamentaria-206-4.html"
documentos = cdmx_client.obtener_gacetas_por_url(url=url)

# Descargar de forma segura con barra de progreso
primer_doc = documentos[0]
print(f"Preparando descarga de: {primer_doc.titulo} de tamaño: {primer_doc.peso_kb} kb")

ruta_local = cdmx_client.descargar_pdf(primer_doc.url_pdf, "./gaceta_cdmx.pdf")
print(f"Guardado en {ruta_local}")
```

### 10. Consultar la Consejería Jurídica de la CDMX (Gaceta Oficial)

El portal de la Consejería oculta los vínculos a sus archivos mediante tecnología *ZK Framework*. Para habilitar la descarga, Legismex controla dinámicamente el navegador en el fondo. Se requiere instalar la adición `[consejeria]`.

```python
from legismex.consejeria import ConsejeriaClient

client = ConsejeriaClient(headless=True)

# Buscar todas las gacetas que hablen sobre la palabra o folio "1811"
gacetas = client.buscar_gacetas(criterio="1811")

for g in gacetas:
    print(f"Gaceta del {g.fecha} No. {g.numero}:\n {g.descripcion}")

# Para interceptar la descarga del archivo:
if gacetas and gacetas[0].tiene_pdf:
    print("Interceptando archivo originado por ZK Framework...")
    ruta = client.descargar_gaceta(
        gaceta=gacetas[0], 
        criterio="1811", 
        ruta_destino="./gaceta_cdmx_consejeria.pdf"
    )
    print("Guardado en:", ruta)
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
*   **`GacetaSenado`**: Colección raíz de una gaceta diaria o de sesión (histórica o reciente).
    *   `titulo_edicion`: str
    *   `documentos`: List[DocumentoSenado]
*   **`DocumentoSenado`**: Instancia validada de un asunto publicado en Senado.
    *   `titulo`: str
    *   `url`: str
    *   `categoria`: str
*   **`ReferenciaGaceta`**: Referencia obtenida a través del calendario histórico.
    *   `fecha`: str
    *   `url`: str
    *   `descripcion`: str

#### Modelos del DOF
*   **`DofEdicion`**: Concentrado con todos los decretos y acuerdos del día.
    *   `fecha`: str
    *   `documentos`: List[DofDocumento]
*   **`DofDocumento`**: Instancia validada de una publicación gubernamental en el DOF.
    *   `seccion`: str
    *   `organismo`: str
    *   `dependencia`: str
    *   `titulo`: str
    *   `url`: str

#### Modelos de la CDMX
*   **`DocumentoCdmx`**: Representa un documento del archivo parlamentario o debate de la Ciudad de México.
    *   `titulo`: str
    *   `fecha`: str
    *   `peso_kb`: float
    *   `peso_etiqueta`: str
    *   `url_pdf`: str
*   **`GacetaConsejeria`**: Instancia local del portal de la Consejería operado bajo ZK Framework.
    *   `descripcion`: str
    *   `fecha`: str
    *   `numero`: str
    *   `tiene_pdf`: bool
    *   `tiene_indice`: bool
    *   `index_absoluto`: int

## Hoja de Ruta
*   Mejorar la extracción per-se del texto interno de los `PDFs` descargados desde Gaceta usando OCR o PyMuPDF.
*   **[DESCARTADO POR AHORA]** Integración directa con las tablas del Sistema de Información Legislativa (SIL) dadas las altas restricciones de origen y WAF anti-scraping en subpáginas de iniciativas.
