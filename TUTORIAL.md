# Tutorial: Análisis de la Gaceta Parlamentaria con `legismex`

Bienvenido al tutorial paso a paso de **`legismex`**. En esta guía aprenderás cómo extraer, analizar y exportar datos históricos y actuales de la Gaceta Parlamentaria de México utilizando nuestra API moderna construida sobre Pydantic.

## Requisitos Previos

*   Python 3.8 o superior.
*   Conocimientos básicos de cómo ejecutar scripts en Python.
*   (Opcional pero recomendado) Saber usar `pandas` si deseas exportar los datos a CSV o Excel para analizarlos posteriormente.

---

## 🛠 Paso 1: Instalación

Si aún no tienes instalada la biblioteca, puedes hacerlo directamente desde el repositorio o en tu entorno local.

Abre tu terminal y ejecuta:

```bash
pip install git+https://github.com/lehcimhdz/legismex.git
```

## 🌐 Paso 2: Conectarse y Obtener Periodos Legislativos

El primer paso para trabajar con la Gaceta es entender cómo está organizada temporalmente. La información se agrupa por "Periodos" (Ordinarios, Extraordinarios, Recesos) dentro de cada Legislatura (ej. Legislatura LXVI, LXV, etc.).

Vamos a escribir nuestro primer script para listar los periodos disponibles:

```python
from legismex.gaceta import GacetaClient

# Inicializamos el cliente. Por defecto maneja tiempos de espera de 30s 
# e ignora errores de certificados SSL obsoletos muy comunes en sitios del gobierno.
client = GacetaClient()

print("Consultando el índice histórico de la Gaceta...")
periodos = client.get_periodos_votacion()

print(f"\n¡Se encontraron {len(periodos)} periodos registrados!")

# Veamos los 3 periodos más recientes
print("\nÚltimos 3 periodos:")
for p in periodos[:3]:
    print(f"- Legislatura {p.legislatura}: {p.nombre}")
    print(f"  Enlace interno: {p.url_base}")
```

**Explicación:** `get_periodos_votacion()` procesa el HTML antiguo de la Gaceta y lo convierte en una lista interactiva de objetos `PeriodoVotacion`. Cada objeto ya contiene la URL base lista para usarse en el siguiente paso.

---

## 📊 Paso 3: Analizando Votaciones Particulares

Una vez que tenemos los periodos, el verdadero valor está en ver **qué** se votó y **cómo** se votó en esos lapsos. 

Tomemos el periodo más reciente de la lista anterior y extraigamos todas sus votaciones:

```python
# Tomamos el primer periodo devuelto (el más reciente)
ultimo_periodo = periodos[0]

print(f"Descargando detalles de votación para: {ultimo_periodo.nombre}...")

# Pasamos la propiedad `url_base` al cliente
votaciones = client.get_votaciones_por_periodo(ultimo_periodo.url_base)

print(f"\nSe encontraron {len(votaciones)} registros de votaciones en este periodo.")

# Vamos a inspeccionar el primer dictamen o asunto votado
primera_votacion = votaciones[0]

print("\n--- DETALLE DE LA ÚLTIMA VOTACIÓN ---")
print(f"Fecha de Asamblea: {primera_votacion.fecha}")
print(f"Asunto / Síntesis: {primera_votacion.asunto}")
print(f"Votos a Favor:     {primera_votacion.votos_favor}")
print(f"Votos en Contra:   {primera_votacion.votos_contra}")
print(f"Abstenciones:      {primera_votacion.abstenciones}")

if primera_votacion.url_pdf:
    print(f"PDF del Dictamen:  {primera_votacion.url_pdf}")
```

**Nota sobre los datos:** No todas las filas en la Gaceta contienen votos numéricos (algunas pueden ser acuerdos verbales o actas sin votación nominal). En esos casos, los campos de `votos_favor`, `votos_contra` o `abstenciones` serán `None`.

---

## 🔍 Paso 4: Búsqueda Masiva de Palabras Clave

A veces no quieres explorar periodo por periodo, sino buscar **cuántas veces se ha hablado de un tema**. `legismex` tiene un puente directo al motor de búsqueda interno de la Gaceta (HTDIG).

Busquemos todas las iniciativas o menciones sobre "ciberseguridad" en la Legislatura 66:

```python
termino = "ciberseguridad"
print(f"\nBuscando el término '{termino}' en los registros de la Gaceta...")

resultados = client.buscar_palabra_clave(termino, legislatura="66")

print(f"Se encontraron {len(resultados)} menciones de '{termino}'.")

for i, res in enumerate(resultados[:2], 1):
    print(f"\nHallazgo #{i} - Fecha: {res.fecha}")
    print(f"Contexto: {res.contexto.strip()}")
    if res.url_pdf:
        print(f"Descargar PDF: {res.url_pdf}")
```

*Tip: Puedes pasar `legislatura=""` (cadena vacía) para buscar a través de absolutamente todos los años históricos.*

---

## 📅 Paso 5: Consultar Iniciativas y su Estatus

Otra función clave es extraer el catálogo de iniciativas que presentan los diputados o el Ejecutivo, junto con su estado (turnada, dictaminada, desechada). Con esto, en lugar de descargar periodo por periodo, interactúas con la base de datos de iniciativas por Legislatura.

Por defecto, la función busca en la Legislatura 66 y trae "Todas" (`origen="T"`).

```python
print("\nObteniendo el catálogo de iniciativas recientes...")
iniciativas = client.obtener_iniciativas(legislatura="66", origen="T")

print(f"Se encontraron {len(iniciativas)} iniciativas registradas.")

# Inspeccionemos las primeras dos:
for i, ini in enumerate(iniciativas[:2], 1):
    print(f"\nIniciativa #{i}")
    print(f"Fecha:       {ini.fecha_presentacion}")
    print(f"Asunto:      {ini.titulo[:100]}...") # Truncamos el título largo
    print(f"Promovido:   {ini.promovente}")
    print(f"Trámite:     {ini.tramite_o_estado}")
    print(f"Dictaminada: {'✅ Sí' if ini.dictaminada else '⏳ No'}")
    if ini.url_gaceta:
        print(f"Enlace Web:  {ini.url_gaceta}")
```

Este tipo de listado resulta muy práctico para crear rastreadores que te notifiquen cuando una iniciativa importante finalmente es votada y pasa de estar `Turnada` a ser declarada como `Dictaminada` e incorporada a la ley.

---

Este tipo de listado resulta muy práctico para crear rastreadores que te notifiquen cuando una iniciativa importante finalmente es votada y pasa de estar `Turnada` a ser declarada como `Dictaminada` e incorporada a la ley.

---

## 5. Consultar y Buscar Dictámenes

La biblioteca también te permite buscar dictámenes presentados en la Gaceta Parlamentaria por palabra clave (buscando en sus títulos o descripciones).

### Código de Ejemplo

```python
from legismex.gaceta import GacetaClient

# Inicializar cliente
cliente = GacetaClient()

# Buscar dictámenes que contengan la palabra "ley" en la legislatura 66
dictamenes = cliente.buscar_dictamenes(legislatura="66", palabra_clave="ley")

print(f"Se encontraron {len(dictamenes)} dictámenes.")

if dictamenes:
    # Mostrar el primer resultado
    d = dictamenes[0]
    print(f"Fecha: {d.fecha}")
    print(f"Dictamen: {d.titulo}")
    print(f"Trámites: {d.tramites}")
    if d.url_pdf:
        print(f"Documento (PDF): {d.url_pdf}")
```

---

## 6. Proposiciones y Documentos Estáticos (Actas, Acuerdos, Agendas, Asistencias)

La Gaceta también cuenta con un buscador idéntico para **Proposiciones con punto de acuerdo** y directorios históricos en formato de texto.

```python
from legismex.gaceta import GacetaClient
client = GacetaClient()

# 1. Proposiciones
proposiciones = client.buscar_proposiciones(legislatura="66", palabra_clave="salud")
print(f"Proposiciones encontradas: {len(proposiciones)}")
if proposiciones:
    print(proposiciones[0].titulo)

# 2. Documentos estáticos (Devuelven nombre/fecha y link)
actas = client.obtener_actas(legislatura="66")
acuerdos = client.obtener_acuerdos(legislatura="66")
agendas = client.obtener_agendas()
asistencias = client.obtener_asistencias()

print(f"Primer acta disponible: {actas[0].fecha_o_titulo} ({actas[0].url_documento})")
```

---

## 🏛 Paso 7: La Gaceta del Senado (Beta)

El Senado de la República maneja su Gaceta bajo una infraestructura web completamente distinta a la de Diputados. Para consultar la Gaceta diaria del Senado, `legismex` provee el submódulo `senado`.

En la Gaceta del Senado, los documentos se agrupan por clasificaciones (ej. Iniciativas, Proposiciones, Comunicaciones, etc.).

```python
from legismex.senado import SenadoClient

senado_client = SenadoClient()

print("Consultando la Gaceta del Senado del día...")
gaceta_senado = senado_client.obtener_gaceta_del_dia(legislatura="66")

print(f"\nEdición Actual: {gaceta_senado.titulo_edicion}")
print(f"Total de Documentos de Hoy: {len(gaceta_senado.documentos)}")

# Mostrar el primer documento encontrado de la categoría "Iniciativas"
iniciativas_hoy = [doc for doc in gaceta_senado.documentos if doc.categoria == 'Iniciativas']

if iniciativas_hoy:
    primera_ini = iniciativas_hoy[0]
    print("\n[EJEMPLO DE INICIATIVA EN SENADO]")
    print(f"Título: {primera_ini.titulo}")
    print(f"URL del documento: {primera_ini.url}")

# Extraer del calendario histórico del Senado
historicas = senado_client.get_calendario_gacetas(year=2021, month=10)
print(f"\nSe publicaron {len(historicas)} Gacetas en Octubre de 2021.")

# Descargar desde URL histórica
gaceta_pasada = senado_client.obtener_gaceta_por_url(historicas[0].url)
print(f"Edición histórica descargada: {gaceta_pasada.titulo_edicion}")
```

---

## 💾 Paso 8: Exportando Datos para Análisis (con Pandas)

Ya que `legismex` usa **Pydantic**, convertir las respuestas a formatos tabulares para machine learning o visualización de datos es increíblemente fácil.

Aquí mostramos cómo guardar todas las votaciones de un periodo en un archivo Excel o CSV usando la librería `pandas`:

```python
# Requiere tener instalado pandas: pip install pandas
import pandas as pd

# 1. Convertimos la lista de objetos Pydantic a una lista de diccionarios
datos_para_df = [v.model_dump() for v in votaciones]
# (Podrías hacer lo mismo para `iniciativas` o `resultados` de búsqueda)

# 2. Creamos el DataFrame de Pandas
df = pd.DataFrame(datos_para_df)

# 3. Limpiamos un poco los datos (rellenamos valores nulos con 0 para los votos)
df['votos_favor'] = df['votos_favor'].fillna(0)
df['votos_contra'] = df['votos_contra'].fillna(0)
df['abstenciones'] = df['abstenciones'].fillna(0)

# 4. Guardamos el resultado en CSV
df.to_csv('votaciones_recientes.csv', index=False, encoding='utf-8')

print("\n¡Datos exportados con éxito a 'votaciones_recientes.csv'!")
print(df.head()) # Muestra las primeras 5 filas en la terminal
```

¡Felicidades! Ahora tienes los datos listos para cruzarlos, graficarlos o alimentarlos a tableros interactivos (como PowerBI, Tableau o Streamlit).

---

## 🇲🇽 Paso 9: Diario Oficial de la Federación (DOF)

El **Diario Oficial de la Federación** es el órgano del Gobierno Constitucional de los Estados Unidos Mexicanos, que tiene la función de publicar en el territorio nacional, leyes, reglamentos, acuerdos, circulares, órdenes y demás actos expedidos por los poderes de la Federación, a fin de que éstos sean observados y aplicados debidamente.

Con `legismex.dof` puedes obtener la publicación diaria lista para analizarse, estructurada por dependencias y secciones.

```python
from legismex.dof import DofClient

dof_client = DofClient()
edicion_hoy = dof_client.obtener_edicion_del_dia()

print(f"\n--- Diario Oficial de la Federación: {edicion_hoy.fecha} ---")
print(f"Total de Documentos de Hoy: {len(edicion_hoy.documentos)}")

# A diferencia de la Gaceta, el DOF agrupa por "Sección", "Organismo" y "Dependencia".
# Busquemos los publicados por la Secretaría de Hacienda (u otras si están disponibles hoy):
for doc in edicion_hoy.documentos[:3]: # Mostramos los 3 primeros en general
    print(f"\n[{doc.seccion}] {doc.organismo}")
    print(f"🏛️ {doc.dependencia}")
    print(f"📝 Decreto/Acuerdo: {doc.titulo}")
    print(f"🔗 URL: {doc.url}")
```

La tabla diaria del DOF separa visualmente en cascada la información, por lo que el objeto `DofDocumento` hereda a qué dependencia y sección pertenece al momento de extraerse de manera fidedigna.

---

## 🏙️ Paso 10: Congreso de la CDMX y Descargas Masivas

El portal del Congreso de la Ciudad de México publica los Diarios de Debates y Gacetas en grandes bloques de paginación o archivos PDF que comúnmente superan los **20-40 Megabytes** dificultando su consumo silencioso. 

El módulo `legismex.cdmx` soluciona esto extrayendo el *peso real del archivo* antes de iniciar la solicitud, y usa una **barra de progreso nativa en terminal (`tqdm`)** para mejorar la Experiencia de Usuario durante iteraciones largas.

```python
from legismex.cdmx import CdmxClient

# El cliente usa _tqdm_ por defecto si la librería está instalada 
cliente_cdmx = CdmxClient()

print("Consultando URL de la Gaceta Parlamentaria III Legislatura...")
url_tomo = "https://www.congresocdmx.gob.mx/gaceta-parlamentaria-206-4.html"

# Aquí estamos leyendo las etiquetas <div class="alert"> del sitio de CDMX
documentos = cliente_cdmx.obtener_gacetas_por_url(url=url_tomo)

print(f"Se encontraron: {len(documentos)} PDFs para descargar.\n")

if documentos:
    primer_doc = documentos[0]
    print(f"Título: {primer_doc.titulo}")
    print(f"Fecha: {primer_doc.fecha}")
    
    # ⚠️ ADVIRTIR AL USUARIO DEL PESO ⚠️
    print(f"Tamaño reportado: {primer_doc.peso_etiqueta} ({primer_doc.peso_kb} kb)")
    print(f"Obtenido desde: {primer_doc.url_pdf}")

    print("\n--- INICIANDO DESCARGA ---")
    
    # Esta función renderizará una barra verde en la consola con la velocidad
    # de descarga, tiempo restante estimado y tamaño en MB reales.
    ruta_final = cliente_cdmx.descargar_pdf(
        url_pdf=primer_doc.url_pdf, 
        ruta_destino='./mi_gaceta_cdmx.pdf'
    )
    
    if ruta_final:
        print(f"¡El archivo pesado se guardó en {ruta_final}!")
```

## Siguientes Pasos

* Consulta el código fuente de [src/legismex/gaceta/client.py](src/legismex/gaceta/client.py) para ver cómo manejamos los tiempos de respuesta.
* Si te interesa descargar los PDFs masivamente y extraer su texto interno, revisa bibliotecas como `PyMuPDF` (`fitz`) combinadas con las URL devueltas por nuestro cliente.
