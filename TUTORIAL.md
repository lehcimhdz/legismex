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

## ⚖️ Paso 11: Extraer Gacetas de la Consejería CDMX (ZK Framework)

La Consejería Jurídica de la CDMX es la única fuente de información que bloquea el scraping HTTP tradicional utilizando la arquitectura AJAX cifrada del enrutador *ZK Framework*, por lo que los archivos están enterrados detrás de "UUIDs" aleatorios y botones que no indican su enlace web ("src").

Para solucionar esto, si realizas la instalación extendida con el tag `[consejeria]` y usas `playwright install chromium`, el submódulo nativo `legismex.consejeria` piloteará automatizadamente una pestaña invisible. 

```python
from legismex.consejeria import ConsejeriaClient

print("Abriendo sesión de Playwright con ZK Framework...")
cliente_consejeria = ConsejeriaClient(headless=True)

# Buscar todas las Gacetas históricas que correspondan al folio o término 1811 
gacetas = cliente_consejeria.buscar_gacetas(criterio="1811")

# Si requerimos buscar el concentrado por fecha, sería:
# gacetas = cliente_consejeria.buscar_gacetas(fecha="2026-03-03")

print(f"Se encontraron: {len(gacetas)} PDFs de Gacetas Históricas.")

if gacetas:
    primera_gaceta = gacetas[0]
    print(f"Descrip: {primera_gaceta.descripcion}")
    print(f"Fecha: {primera_gaceta.fecha}")
    print(f"Número: {primera_gaceta.numero}")
    
    # ⚠️ AVISO PARA DESCARGAR PDF ⚠️
    if primera_gaceta.tiene_pdf:
        print("Manejando click invisible al PDF para interceptar flujo de Bytes...")
        ruta_absoluta = cliente_consejeria.descargar_gaceta(
            gaceta=primera_gaceta, 
            criterio="1811", 
            ruta_destino='./gaceta_consejeria.pdf'
        )
        print(f"¡El PDF oculto se interceptó exitosamente a {ruta_absoluta}!")
```

## 🌮 Paso 12: Extraer Gacetas del Congreso de Jalisco

El Congreso de Jalisco organiza su plataforma de Gaceta Parlamentaria a través de un calendario dinámico que utiliza peticiones web (AJAX) para cargar de manera modular sus datos. Gracias al submódulo `legismex.jalisco`, podemos obtener los Eventos, el Orden del Día y los archivos adjuntos (Word, PDFs) listos para descargas directas.

```python
from legismex.jalisco import JaliscoClient

print("Conectando con la Gaceta de Jalisco...")
client = JaliscoClient()

# 1. Podemos obtener el calendario completo para saber de qué fechas podemos extraer info
calendario = client.obtener_calendario_eventos()
print(f"Hay {len(calendario)} fechas históricas y programadas registradas.")

# 2. Requerir una fecha específica
fecha = "2025-10-06"
print(f"\nConsultando eventos del {fecha}...")

eventos = client.obtener_eventos_por_fecha(fecha)

# 3. Iteramos todos los puntos y documentos adjuntos de dicho evento en cascada
for evt in eventos:
    print(f"\n[EVENTO {evt.tipo} - ID {evt.id_evento}]: {evt.titulo}")
    
    for pt in evt.puntos_orden:
        print(f"  Punto: {pt.titulo}")
        
        for doc in pt.documentos:
            # Documento de Microsoft Word (.docx) o Google Docs
            print(f"    ├─ Adjunto: {doc.titulo}")
            print(f"    └─ Enlace Directo: {doc.url}")
```

La estructura en árbol (`Evento -> Puntos -> Documentos`) de Pydantic facilita cruzar los documentos contra su acta u orden respectivo.

## 📰 Paso 13: Periódico Oficial del Estado de Jalisco

Jalisco, adicionalmente a su Congreso, cuenta con el Periódico Oficial operado por el gobierno estatal. El portal (una SPA hecha en Angular) consume una veloz API JSON interconectada que `legismex` aprovecha (`legismex.jalisco_po`) para ofrecer tiempos de extracción insuperables sin procesar HTML. 

```python
from legismex.jalisco_po import JaliscoPoClient

print("Buscando las ediciones más recientes...")
client = JaliscoPoClient()

# 1. Podemos buscar ediciones por palabra clave o por fecha
paginacion = client.buscar_ediciones(elementos_por_pagina=3)
print(f"Se encontraron un total de {paginacion.total} publicaciones en la BD.")

# 2. Iteramos los resúmenes iniciales
for edicion_resumen in paginacion.items:
    print(f"\n[FECHA: {edicion_resumen.date_newspaper}] - Tomo {edicion_resumen.tomo}")
    print(f"Descripción: {edicion_resumen.description[:50]}...")
    
    # 3. Solicitamos el detalle cruzando el ID único para extraer el archivo PDF
    detalle_completo = client.obtener_edicion(edicion_resumen.id_newspaper)
    
    if detalle_completo.link:
        print(f" -> Enlace oficial al PDF: {detalle_completo.link}")
```

La asombrosa velocidad de esta API te permite escanear la hemeroteca e indexar PDFs completos fácilmente.

## 🤠 Paso 14: Extraer Iniciativas Históricas de Nuevo León

El H. Congreso del Estado de Nuevo León alimenta su catálogo de iniciativas con un concentrado masivo. A través del submódulo `legismex.nuevoleon`, extraer los +2000 registros presentados desde legislaturas anteriores hasta la fecha toma tan solo un par de segundos, ya completamente limpios de etiquetas HTML.

```python
from legismex.nuevoleon import NuevoLeonClient

print("Descargando corpus de Iniciativas de Nuevo León...")
client = NuevoLeonClient()

iniciativas = client.obtener_iniciativas()
print(f"Se lograron mapear un total histórico de {len(iniciativas)} iniciativas.")

# Si sólo nos interesa la actual legislatura "LXXVII":
iniciativas_lxxvii = client.obtener_iniciativas(legislatura="LXXVII")

for ini in iniciativas_lxxvii[:3]:
    print(f"\nExpediente: {ini.expediente}")
    print(f"Promovente: {ini.promovente}")
    print(f"Asunto: {ini.asunto}")
    print(f"Fue turnada a la comisión: {ini.comision}")
    print(f"Enlace Oficial PDF: {ini.url_pdf}")
```

El modelo `NuevoLeonIniciativa` de Pydantic facilita su guardado inmediato en Pandas o Bases de Datos.

## 📰 Paso 15: Periódico Oficial de Nuevo León y Fragmentación

Otra asimetría clásica gubernamental es que el portal principal (`sistec.nl.gob.mx`) del Periódico Oficial divide cada edición impresa diaria en múltiples archivos PDF, a menudo listando "Parte 1", "Parte 2", o "Parte 3" dentro de la misma casilla bajo una tabla clásica de ASP.NET sin etiquetado de clases moderno.

Para simplificarlo, usa el cliente web `NuevoLeonPoClient`. A diferencia de otras entidades, el cliente ya inyecta los *User-Agents* necesarios para burlar el Firewall y devuelve el modelo consolidado:

```python
from legismex.nuevoleon_po import NuevoLeonPoClient

print("Descargando la tabla principal del Periódico Oficial de N.L.")
po_client = NuevoLeonPoClient()

ediciones = po_client.obtener_ediciones_recientes()

for edicion in ediciones[:3]:
    print(f"\n[{edicion.fecha}] Ejemplar No. {edicion.numero}")
    print(f"⚠️ ¡Esta edición se divide en {len(edicion.urls_pdf)} fragmentos!")
    
    # Podemos listar los PDFs subidos en esa celda
    for idx, pdf in enumerate(edicion.urls_pdf, 1):
        print(f"   Parte {idx}: {pdf}")
```

Este encapsulamiento asegura que no pierdas secciones de un decreto que pudieran haber sido publicadas en el Apéndice o en la "Parte 04" de ese mismo día.

## 🏛️ Paso 16: Histórico Extendido: Estado de México (Edomex)

Las legislaturas recientes del Estado de México consolidan su estructura dentro del subdirectorio `/gacetaanteriores`, exponiendo cientos de ediciones del periodo con fechas desglosadas en múltiples nodos HTML.

El submódulo simplifica todo dejándote el año, la fecha sanitizada y el enlace al PDF listo para ser almacenado:

```python
from legismex.edomex import EdomexClient

client = EdomexClient()
gacetas = client.obtener_gacetas()

# Obtén la gaceta deseada (ej. número índice de la tabla).
primer = gacetas[0]
print(f"[{primer.anio}] Gaceta del: {primer.fecha}")

for idx, pdf in enumerate(primer.urls_pdf, 1):
    print(f"   Parte {idx}: {pdf}")

## 📜 Paso 17: Periódico Oficial "Gaceta del Gobierno" (EdoMéx)

A través del portal `LEGISTEL`, el gobierno estatal publica su periódico oficial organizando los bandos y oficios categorizados por las distintas secretarías o dependencias de gobierno.

```python
from legismex.edomex_po import EdomexPoClient

client = EdomexPoClient()

# Trae hasta 1000 ediciones oficiales.
ediciones = client.obtener_ediciones_recientes()

primer = ediciones[0]
print(f"Gaceta del Gobierno: {primer.fecha}")

# Muchas veces incluyen el compendio total
if primer.url_completa:
    print(f"Descarga Gaceta Completa: {primer.url_completa}")

# Documentos unitarios clasificados por dependencia
for doc in primer.documentos[:3]:
    print(f"[{doc.seccion}] {doc.titulo[:60]} -> {doc.url_pdf}")
```


print(f"\nDescargados {len(gacetas)} volúmenes del Edomex.")
reciente = gacetas[0]
print(f"  Última Gaceta: {reciente.numero} (Publicada el {reciente.fecha})")
print(f"  Descargar en: {reciente.url_pdf}")
```

## Siguientes Pasos

* Consulta el código fuente de [src/legismex/gaceta/client.py](src/legismex/gaceta/client.py) para ver cómo manejamos los tiempos de respuesta.
* Si te interesa descargar los PDFs masivamente y extraer su texto interno, revisa bibliotecas como `PyMuPDF` (`fitz`) combinadas con las URL devueltas por nuestro cliente.
