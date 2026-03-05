# 🏛️ legismex

> Biblioteca en Python para facilitar el acceso y análisis de información legislativa en México. 🇲🇽


### 🏛️ Soporte Multi-Cámara e Institucional
*   **Cámara de Diputados:** Soporte robusto para la Gaceta Parlamentaria (`gaceta.diputados.gob.mx`), abstrayendo `framesets` antiguos en una API moderna.
*   **Senado de la República:** Integración con `www.senado.gob.mx` para extraer la gaceta diaria estructurada por categorías y el histórico.
*   **Diario Oficial de la Federación:** Integración con `dof.gob.mx` extrayendo el concentrado diario por secciones y dependencias federales.
*   **Congreso de la Ciudad de México:** Rastreador especializado para recuperar y descargar PDFs pesados directos de los Diarios de Debate con barra de progreso interactivos.
*   **Consejería de la CDMX (Gaceta Oficial):** Extrae Gacetas evadiendo la ofuscación de *ZK Framework* a través de control headless nativo con Playwright.
*   **Congreso del Estado de México**: Extrae Iniciativas, Puntos de Acuerdo, y Pronunciamientos de la Gaceta Parlamentaria.
*   **Periódico Oficial del Estado de México**: Permite consultar tomos y documentos oficiales publicados en la "Gaceta del Gobierno".
*   **Congreso de Puebla**: Análisis de las resoluciones, iniciativas y puntos de acuerdo de la Gaceta Legislativa de Puebla.
*   🌋 **Puebla**: Periódico Oficial del Estado
*   🏰 **Querétaro**: Gaceta Legislativa del Congreso del Estado
*   ⚔️ **Querétaro**: Periódico Oficial "La Sombra de Arteaga"
*   🐸 **Guanajuato**: Gaceta Parlamentaria del Congreso del Estado
*   🐸 **Guanajuato**: Periódico Oficial del Estado
*   🦋 **Michoacán**: Gaceta Parlamentaria del Congreso del Estado
*   🦋 **Michoacán**: Periódico Oficial del Estado (archivo 1955–2025)
*   🌋 **Morelos**: Documentos Legislativos del Congreso (LVI Legislatura)
*   🌋 **Morelos**: Periódico Oficial del Estado (archivo 1970–2026, 6,400+ ejemplares)
*   🌴 **Guerrero**: Gaceta Parlamentaria del Congreso (LXIV Legislatura, 185+ gacetas)
*   🌴 **Guerrero**: Periódico Oficial del Estado (30 categorías, desde 1987)
*   🌋 **Tlaxcala**: Trabajo Legislativo del Congreso LXV (Decretos, Iniciativas, Acuerdos, Dictámenes, y 8 categorías más, 2024–2026)
*   **Congreso de Jalisco:** Extrae el calendario de eventos y desgrana las agendas y subpuntos con documentos adjuntos iterando sobre la estructura interna de la Gaceta Parlamentaria.
*   **Congreso de Nuevo León:** Convierte la base de datos DataTables de iniciativas a objetos analíticamente procesables al vuelo.
*   **Periódico Oficial de Nuevo León:** Omite barreras de firewall y parsea la vista ASP.NET empaquetando los enlaces PDF esparcidos.
*   **Gaceta Parlamentaria del Estado de México:** Obtiene el listado completo (histórico) de gacetas parlamentarias extrayendo fechas limpias y enlaces a PDFs originales.
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

### 11. Consultar el Congreso de Jalisco
El portal de la Gaceta Parlamentaria de Jalisco carga la información mediante recuadros interactivos vía AJAX. El submódulo `legismex.jalisco` provee un cliente que itera esta cascada jerárquica automáticamente, devolviendo los Eventos, el Orden del Día y los Documentos nativos (por ejemplo `.docx` y `.pdf`).

```python
from legismex.jalisco import JaliscoClient

client = JaliscoClient()
eventos = client.obtener_eventos_por_fecha("2025-10-06")

for evt in eventos:
    print(f"Evento: {evt.titulo}")
    for pt in evt.puntos_orden:
        print(f"  Punto: {pt.titulo}")
        for doc in pt.documentos:
            print(f"    Adjunto: {doc.titulo}")
            print(f"    URL: {doc.url}")
```

### 12. Consultar el Periódico Oficial de Jalisco
El portal de la Gaceta cuenta con una API subyacente que devuelve los enlaces en crudo. `legismex.jalisco_po` los recupera de manera veloz sin renderizaciones DOM inestables.

```python
from legismex.jalisco_po import JaliscoPoClient

client = JaliscoPoClient()
resultados = client.buscar_ediciones(elementos_por_pagina=1)

if resultados.items:
    # Resolvemos el detalle absoluto del primer resultado para obtener links
    detalle = client.obtener_edicion(resultados.items[0].id_newspaper)
    print(f"Edición: {detalle.post_date}")
    print(f"URL de Descarga Directa: {detalle.link}")
```

### 13. Consultar Iniciativas del Congreso de Nuevo León
El H. Congreso de Nuevo León mantiene un listado ágil de las iniciativas presentadas, que `legismex.nuevoleon` consume íntegramente de una sola petición.

```python
from legismex.nuevoleon import NuevoLeonClient

client = NuevoLeonClient()

# Puedes obtener TODO el histórico... o filtrar por una Legislatura:
iniciativas_lxxvii = client.obtener_iniciativas(legislatura="LXXVII")

print(f"Total en LXXVII: {len(iniciativas_lxxvii)}")

for ini in iniciativas_lxxvii[:2]:
    print(f"[{ini.fecha}] Promueve: {ini.promovente}")
    print(f"Asunto: {ini.asunto}")
    print(f"Dictamen PDF: {ini.url_pdf}\n")
```

### 14. Consultar Periódico Oficial de Nuevo León
El Gobierno de NL divide las ediciones del periódico en archivos fragmentados. `legismex` simplifica el proceso extrayendo todos los enlaces vinculados a un solo día.

```python
from legismex.nuevoleon_po import NuevoLeonPoClient

po_client = NuevoLeonPoClient()
ediciones = po_client.obtener_ediciones_recientes()

for edicion in ediciones[:2]:
    print(f"\nFecha: {edicion.fecha}")
    print(f"No. de Ejemplar: {edicion.numero}")
    print(f"Partes o tomos PDF: {len(edicion.urls_pdf)}")
    
    if edicion.urls_pdf:
        print(f"URL de la Parte 1: {edicion.urls_pdf[0]}")
```

### 15. Consultar Gaceta del Estado de México (Edomex)
La LXI y LXII Legislatura del Estado de México aloja su gaceta en un portal moderno y unificado. Con un solo comando podemos extraer más de un centenar de ediciones:

```python
from legismex.edomex import EdomexClient

client = EdomexClient()
gacetas_edomex = client.obtener_gacetas()

print(f"Total históricas: {len(gacetas_edomex)}")

for gaceta in gacetas_edomex[:2]:
    print(f"[{gaceta.fecha}] {gaceta.numero} -> {gaceta.url_pdf}")
```

### 16. Consultar Gaceta de Puebla
El Congreso de Puebla protege la vista de su Gaceta Legislativa con Cloudflare, pero a través de `legismex.puebla` (que requiere la adición `[consejeria]` / instalación de `playwright`), puedes extraer los índices mensuales automáticamente esquivando la página de comprobación:

```python
from legismex.puebla_po import PueblaPoClient

client = PueblaPoClient()
resultado = client.buscar_ediciones(rango=10, pagina=1)

for gaceta in resultado.ediciones:
    print(f"Tomo: {gaceta.tomo} | Num: {gaceta.numero} | Sec: {gaceta.seccion} -> PDF: {gaceta.url_pdf}")
```

### 🪨 Querétaro - Congreso
Gacetas Publicadas por la LXI Legislatura (entre otras) de Querétaro.

```python
from legismex.queretaro import QueretaroClient

client = QueretaroClient()
gacetas = client.obtener_gacetas()

print(f"Total Gacetas: {len(gacetas)}")
```

### 🌳 Querétaro - Periódico Oficial

"La Sombra de Arteaga" iterando a través del compendio del año.

```python
from legismex.queretaro_po import QueretaroPoClient

qro_po_client = QueretaroPoClient()

# Get issues from 2025
ediciones_2025 = qro_po_client.obtener_ediciones_por_ano(2025)

for edicion in ediciones_2025[:3]:
    print(f"Fecha: {edicion.fecha}")
    for url in edicion.urls_pdf:
        print(f"  -> {url}")
```

#### Guanajuato - Congreso del Estado

Extracts initiatives and points of agreement that legislators present inside the state parliament.

```python
from legismex import GuanajuatoClient

gto_client = GuanajuatoClient()

iniciativas = gto_client.obtener_iniciativas(page=1)
puntos_de_acuerdo = gto_client.obtener_puntos_de_acuerdo(page=2)

print(iniciativas[0].expediente)
print(iniciativas[0].descripcion)
print(iniciativas[0].url_detalle)

print(puntos_de_acuerdo[0].expediente)
```

#### Guanajuato - Periódico Oficial del Estado

Consulta y descarga las ediciones del Periódico Oficial a través de la API REST oculta en su portal Angular.

```python
from legismex import GuanajuatoPoClient

po = GuanajuatoPoClient()

# Último ejemplar publicado
ultimos = po.obtener_ultimo_ejemplar()
print(ultimos[0].descripcion, ultimos[0].url_pdf)

# Búsqueda paginada
resultados = po.buscar(anio="2025", page=5)
for r in resultados:
    print(f"[{r.fecha}] Num.{r.numero} Parte {r.parte} - {r.descripcion}")
    print(f"  PDF: {r.url_pdf}")
```

#### Michoacán - Congreso del Estado

Extrae las gacetas parlamentarias del Congreso de Michoacán iterando sobre el buscador PTB de WordPress con soporte de paginación y filtros por legislatura, título y fecha.

```python
from legismex import MichoacanClient

mich = MichoacanClient()

# Obtener gacetas de la legislatura LXXVI
gacetas = mich.obtener_gacetas(legislatura="lxxvi", page=1)
total_pags = mich.obtener_total_paginas(legislatura="lxxvi")
print(f"Total páginas: {total_pags}")

for g in gacetas[:3]:
    print(f"[{g.fecha}] {g.titulo} - {g.descripcion[:60]}...")
    print(f"  PDF: {g.url_pdf}")
```

#### Michoacán - Periódico Oficial

Navega el árbol WP-Filebase del Periódico Oficial de Michoacán (archivo 1955–2025) para listar años, meses, días y descargar PDFs directamente.

```python
from legismex import MichoacanPoClient

po = MichoacanPoClient()

# Ver años disponibles
anios = po.obtener_anios()
print(f"Años: {[a.nombre for a in anios[:5]]}")

# Listar PDFs de Enero 2025
archivos = po.obtener_archivos_por_fecha(2025, mes="Enero")
for a in archivos[:3]:
    print(f"[{a.dia}] {a.nombre} → {a.url_pdf}")
```

#### Morelos - Congreso del Estado

Raspa la página de "Documentos Legislativos" del Congreso de Morelos (WordPress/Divi) extrayendo actas, órdenes del día, versiones estenográficas y legislación con sus enlaces PDF directos.

```python
from legismex import MorelosClient

mor = MorelosClient()

# Obtener todos los documentos legislativos (130+)
docs = mor.obtener_documentos()
print(f"Total: {len(docs)}")

# Filtrar por sección: "Orden-del-día"
ordenes = mor.obtener_documentos(seccion="Orden-del-día")
for o in ordenes[:3]:
    print(f"[{o.periodo}] {o.titulo}")
    print(f"  PDF: {o.url_pdf}")
```

#### Morelos - Periódico Oficial

Consulta la API DataTables del Periódico Oficial de Morelos con manejo automático de tokens CSRF, paginación server-side y filtros por año, mes y palabra clave en el sumario (6,400+ ejemplares desde 1970).

```python
from legismex import MorelosPoClient

po = MorelosPoClient()

# Listar ejemplares de enero 2025
items, total = po.obtener_ejemplares(anio=2025, mes=1)
print(f"Total: {total}")
for e in items[:3]:
    print(f"#{e.numero} | {e.edicion} | {e.fecha_publicacion}")
    print(f"  PDF: {e.url_pdf}")
```

#### Guerrero - Gaceta Parlamentaria

Raspa la Gaceta Parlamentaria del Congreso de Guerrero (LXIV Legislatura) extrayendo 185+ gacetas con sus documentos clasificados por tipo (Actas, Iniciativas, Comunicados, etc.) y sus PDFs.

```python
from legismex import GuerreroClient

gro = GuerreroClient()

# Listar gacetas (paginado)
gacetas, total = gro.obtener_gacetas(pagina=1)
print(f"Total: {total}")

# Obtener documentos de una gaceta
docs = gro.obtener_documentos(gaceta_id=230)
for d in docs[:3]:
    print(f"[{d.tipo}] {d.descripcion[:60]}...")
    print(f"  PDF: {d.url_pdf}")
```

#### Guerrero - Periódico Oficial

Raspa el portal WordPress del Periódico Oficial de Guerrero con filtros por palabra clave, año, mes, día y categoría (30 categorías: Leyes, Decretos, Acuerdos, etc.).

```python
from legismex import GuerreroPoClient

po = GuerreroPoClient()

# Publicaciones recientes (50 por página)
pubs = po.obtener_publicaciones()
for p in pubs[:3]:
    print(f"[{p.categoria}] {p.titulo} | {p.fecha}")
    print(f"  PDF: {p.url_pdf}")

# Filtrar por año y categoría LEYES (id=25)
leyes = po.obtener_publicaciones(anio=2025, categoria=25)
```

#### Tlaxcala - Congreso LXV

Raspa el portal del Congreso de Tlaxcala extrayendo las 12 categorías documentales (Decretos, Iniciativas, Orden del día, Acuerdos, Dictámenes, Votaciones, etc.) por año de ejercicio.

```python
from legismex import TlaxcalaClient

tlx = TlaxcalaClient()

# Todos los documentos
docs = tlx.obtener_documentos()
for d in docs[:3]:
    print(f"[{d.anio}] [{d.categoria}] #{d.numero} {d.fecha}")
    print(f"  {d.titulo[:70]}")
    print(f"  PDF: {d.url_pdf}")

# Solo Decretos 2025
decretos = tlx.obtener_documentos(categoria='Decretos', anio=2025)
```

### 17. Periódico Oficial de Puebla

Consulte la API del Periódico Oficial y págine entre los miles de resultados disponibles:

```python
from pprint import pprint
from legismex.puebla_po import PueblaPoClient

cliente = PueblaPoClient()

# Consultar la última página de publicaciones (25 por página default)
resultado = cliente.buscar_ediciones(rango=25, pagina=1)

print(f"Total histórico: {resultado.cantidad_total}")
for edicion in resultado.ediciones[:2]:
    print(f"Tomo: {edicion.tomo} | Num: {edicion.numero} | Sec: {edicion.seccion}")
    print(f"URL PDF: {edicion.url_pdf}")
    print("---")
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

#### Modelos de Jalisco
*   **`JaliscoEvento`**: Evento registrado en el calendario (ej. Sesión de Pleno, Comisiones).
    *   `fecha`: str
    *   `titulo`: str
    *   `tipo`: int
    *   `id_evento`: int
    *   `puntos_orden`: List[JaliscoPunto]
*   **`JaliscoPunto`**: Punto individual dentro del orden del día de un evento.
    *   `titulo`: str
    *   `documentos`: List[JaliscoDocumento]
*   **`JaliscoDocumento`**: Documento final adjunto o embebido (pdf, docx).
    *   `titulo`: str
    *   `url`: str

#### Modelos del Periódico Oficial de Jalisco
*   **`JaliscoPoResumen`**: Vista previa de una edición en listas o búsquedas.
    *   `id_newspaper`: int
    *   `date_newspaper`: str
    *   `tomo`: str
    *   `number`: str
    *   `description`: str
*   **`JaliscoPoEdicion`**: Detalle definitivo de la publicación.
    *   `id`: int
    *   `post_date`: str
    *   `link`: str (Enlace directo al PDF)

#### Modelos de Nuevo León
*   **`NuevoLeonIniciativa`**: Propuesta de ley de los diputados del H. Congreso de Nuevo León.
    *   `expediente`: str
    *   `legislatura`: str
    *   `promovente`: str
    *   `asunto`: str
    *   `comision`: str
    *   `fecha`: str
    *   `estado`: str
    *   `url_pdf`: Optional[str]
*   **`NuevoLeonPoEdicion`**: Registro agrupado del Periódico Oficial (Estado de Nuevo León).
    *   `numero`: str
    *   `fecha`: str
    *   `urls_pdf`: List[str]
*   **`EdomexGaceta`**: Número de Gaceta Parlamentaria del Estado de México.
    *   `numero`: str
    *   `fecha`: str
    *   `url_pdf`: str

#### Modelos de Puebla
*   **`PueblaGaceta`**: Gaceta legislativa mensual del Congreso de Puebla.
    *   `mes`: str
    *   `numero`: str
    *   `fecha_texto`: str
    *   `url_pdf`: HttpUrl
    *   `legislatura`: str
    *   `anio_legislativo`: Optional[str]

## Hoja de Ruta
*   Mejorar la extracción per-se del texto interno de los `PDFs` descargados desde Gaceta usando OCR o PyMuPDF.
*   **[DESCARTADO POR AHORA]** Integración directa con las tablas del Sistema de Información Legislativa (SIL) dadas las altas restricciones de origen y WAF anti-scraping en subpáginas de iniciativas.
