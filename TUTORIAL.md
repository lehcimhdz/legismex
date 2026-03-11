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
pip install legismex
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

> [!WARNING]
> **Bloqueos en Google Colab y Nubes Extranjeras (AWS, Azure, etc.)**
> 
> Muchos servidores gubernamentales en México implementan *firewalls* muy estrictos (Geo-Bloqueo o listas blancas) para evitar ataques automatizados. Por lo tanto, si intentas ejecutar consultas a sitios como la Gaceta Parlamentaria usando **Google Colab**, servidores de Amazon (AWS) en Estados Unidos, o nubes foráneas, es muy probable que te encuentres con un error `ConnectTimeout`.
> 
> Las dependencias gubernamentales silenciosamente "dejan en visto" a las IPs de los mega-centros de datos extranjeros. Para asegurar el funcionamiento, recomendamos ejecutar tus scripts **localmente** usando el proveedor de internet de tu oficina o casa (las IPs residenciales mexicanas son admitidas sin problema), o, de ser indispensable la nube, usar proxies residenciales alojados en México.

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

## Periódico Oficial del Estado de Baja California Sur

Extrae las ediciones por año publicadas por la Secretaría de Finanzas.

```python
import asyncio
from legismex import BcsPoClient

async def obtener_boletines_bcs():
    client = BcsPoClient()
    
    # Obtiene los boletines publicados en 2025
    ediciones_2025 = await client.a_obtener_ediciones(2025)
    
    print(f"Total encontrados 2025: {len(ediciones_2025)}")
    
    for e in ediciones_2025[:3]:
        print(f"Boletín {e.numero} ({e.fecha}): {e.url_pdf}")

if __name__ == "__main__":
    asyncio.run(obtener_boletines_bcs())
```

> [!IMPORTANT]
> **Error "asyncio.run() cannot be called from a running event loop"**
> 
> Si estás ejecutando este código en un **Jupyter Notebook** o **Google Colab**, verás este error. Esto se debe a que el notebook ya tiene un bucle de eventos activo.
> 
> **Solución en Notebooks/Colab:** No uses `asyncio.run()`, simplemente llama a la función con `await` directamente en la celda:
> ```python
> await obtener_boletines_bcs()
> ```

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

## 📜 Paso 18: Gaceta Legislativa de Puebla (Cloudflare Bypass)

El Congreso de Puebla presenta un reto extra: la página de su gaceta cuenta con protecciones anti-bot de Cloudflare, que bloquean peticiones directas de código.

`legismex` ofrece el submódulo `legismex.puebla`, que usa un navegador en el fondo (requiere tener instalada la variante de playwright) para resolver el reto de seguridad silenciosamente y entregarte la lista mensual de PDFs de la Gaceta de la LXI/LXII Legislatura:

```python
from legismex.puebla import PueblaClient

client = PueblaClient(headless=True)

# Esto abrirá brevemente un navegador en segundo plano (headless)
# e interceptará automáticamente los enlaces a las gacetas mensuales.
gacetas = client.obtener_gacetas_recientes()

print(f"Se lograron extraer {len(gacetas)} meses de archivos de Gaceta.")

primer = gacetas[0]
print(f"Legislatura: {primer.legislatura} - Año: {primer.anio_legislativo}")
print(f"Tomos de {primer.mes} ({primer.numero})")
print(f"Enlace PDF Oficial: {primer.url_pdf}")
```

## 📰 Paso 19: Periódico Oficial del Estado de Puebla

El portal del Periódico Oficial del Gobierno de Puebla está dotado de un motor de búsqueda interno poderoso. A través de `legismex.puebla_po` podemos evitar hacer *scraping* visual e interactuar directamente con la Base de Datos que alimenta este motor enviando la petición al backend en formato JSON.

El cliente extrae inteligentemente las propiedades de Tomo, Sección y Número devolviéndolas parseadas:

```python
from legismex.puebla_po import PueblaPoClient

print("Buscando las ediciones más recientes...")
client = PueblaPoClient()

# Consultamos los 10 documentos más recientes
paginacion = client.buscar_ediciones(rango=10, pagina=1)

print(f"La base de datos de Puebla cuenta con: {paginacion.cantidad_total} documentos resguardados.")

# Iteramos los resultados parseados de la primera página
for edicion in paginacion.ediciones[:3]:
    print(f"\n[ID: {edicion.id_publicacion}] Fecha Relativa: {edicion.fecha}")
    print(f"Edición: Tomo {edicion.tomo} | Número {edicion.numero} | Sección {edicion.seccion}")
    print(f"Descripción: {edicion.descripcion[:100]}...")
    print(f" -> Enlace Oficial PDF: {edicion.url_pdf}")
```

La ventaja de este método es su velocidad casi instantánea, obteniendo miles de documentos en menos de un par de segundos.

## 🏛️ Paso 20: Congreso de Querétaro (Gaceta Legislativa)

El portal de la Legislatura del Estado de Querétaro expone sus Gacetas Históricas organizadas por Legislatura usando el componente *Supsystic Data Tables* de WordPress. `legismex.queretaro` procesa el HTML interactuando directamente con las filas para entregarte todos los PDFs reportados:

```python
from legismex.queretaro import QueretaroClient

print("Descargando historial de Gacetas de Querétaro...")
client = QueretaroClient()
gacetas = client.obtener_gacetas()

print(f"Total de Gacetas Históricas disponibles: {len(gacetas)}")

# Inspeccionemos las primeras dos:
for idx, gaceta in enumerate(gacetas[:2], 1):
    print(f"\n[{gaceta.legislatura}] Gaceta #{idx}")
    print(f"Número: {gaceta.numero}")
    print(f"Descripción: {gaceta.descripcion}")
    print(f"Archivo PDF: {gaceta.url_pdf}")
```

La facilidad de este cliente te permite tener una lista enorme de URLs apuntando directamente a PDFs estáticos para su consumo masivo.

## 🌳 Paso 21: Periódico Oficial de Querétaro (La Sombra de Arteaga)

El legendario periódico "La Sombra de Arteaga" utiliza un layout web antiguo estructurado en `<frameset>` y subpáginas de calendarios visuales (ej. `2025.html`). A menudo, una sola edición diaria se publica fragmentada en docenas de PDFs (Parte 1, Parte 2...).

Omitiendo esta fricción analítica, `legismex.queretaro_po` compila todas las partes de una fecha específica agrupándolas en una lista segura, consolidando el documento y evitando filtraciones de datos durante el resguardo:

```python
from legismex.queretaro_po import QueretaroPoClient

print("Descargando el calendario anual 2025 de La Sombra de Arteaga...")
client = QueretaroPoClient()
ediciones = client.obtener_ediciones_por_ano(2025)

print(f"Total de Días de Publicación encontrados: {len(ediciones)}")

# Las ediciones vienen ordenadas de la más reciente a la más antigua
for idx, edicion in enumerate(ediciones[:2], 1):
    print(f"\nPublicación #{idx} - [Fecha Formato: {edicion.fecha}]")
    print(f"Partes totales publicadas en este día: {len(edicion.urls_pdf)}")
    
    # Imprimiendo los URIs de descarga directa:
    for idx_pdf, url_pdf in enumerate(edicion.urls_pdf, 1):
        print(f"  └─ Parte {idx_pdf}: {url_pdf}")
```

Al utilizar este cliente, los científicos de datos obtienen URIs determinísticas listas para alimentar herramientas OCR de alto volumen.

## Siguientes Pasos

* Consulta el código fuente de [src/legismex/gaceta/client.py](src/legismex/gaceta/client.py) para ver cómo manejamos los tiempos de respuesta.
* Si te interesa descargar los PDFs masivamente y extraer su texto interno, revisa bibliotecas como `PyMuPDF` (`fitz`) combinadas con las URL devueltas por nuestro cliente.

---

## Paso 22: Integrar el Congreso de Guanajuato (Gaceta Parlamentaria)

Guanajuato expone Iniciativas y Puntos de Acuerdo en listas paginadas. El `GuanajuatoClient` esquiva los errores SSL de certificados caducos locales y extrae las publicaciones indicando la página que se desea procesar.

```python
from legismex import GuanajuatoClient

gto = GuanajuatoClient()

# Consultar la página 1 de iniciativas
iniciativas = gto.obtener_iniciativas(page=1)
for i in iniciativas[:3]:
    print(f"[{i.expediente}] - {i.descripcion[:50]}...")
    print(f"Link: {i.url_detalle}")

# Consultar puntos de acuerdo
puntos = gto.obtener_puntos_de_acuerdo(page=2)
print(f"Total encontrados: {len(puntos)}")
```

---

## Paso 23: Integrar el Periódico Oficial de Guanajuato

El portal del Periódico Oficial de Guanajuato es una aplicación Angular que consulta una API REST en `backperiodico.guanajuato.gob.mx`. `GuanajuatoPoClient` consume esos endpoints directamente, sin necesidad de renderizar JavaScript.

```python
from legismex import GuanajuatoPoClient

po = GuanajuatoPoClient()

# Obtener el último ejemplar publicado
ultimos = po.obtener_ultimo_ejemplar()
for u in ultimos:
    print(f"{u.descripcion}: {u.url_pdf}")

# Buscar ediciones por año
resultados = po.buscar(anio="2025", page=5)
for r in resultados:
    print(f"[{r.fecha}] Número {r.numero}, Parte {r.parte}")
    print(f"  -> {r.url_pdf}")
```

---

## Paso 24: Congreso de Michoacán (Gaceta Parlamentaria)

El portal del Congreso de Michoacán usa WordPress con el plugin Themify PTB. `MichoacanClient` raspa el buscador de gacetas con soporte de paginación (10 resultados por página) y filtros por legislatura, título del número, texto y rango de fechas.

```python
from legismex import MichoacanClient

client = MichoacanClient()

# Obtener gacetas de la LXXVI legislatura
gacetas = client.obtener_gacetas(legislatura="lxxvi", page=1)
total = client.obtener_total_paginas(legislatura="lxxvi")

print(f"Total de páginas: {total}")
for g in gacetas[:3]:
    print(f"[{g.fecha}] {g.titulo}")
    print(f"  Desc: {g.descripcion[:80]}...")
    print(f"  PDF: {g.url_pdf}")
```

Legislaturas disponibles: `lxxi`, `lxxii`, `lxxiii`, `lxxiv`, `lxxv`, `lxxvi`, `i-constituyente`.

---

## Paso 25: Periódico Oficial de Michoacán

El portal `periodicooficial.michoacan.gob.mx` usa WordPress con el plugin WP-Filebase.  `MichoacanPoClient` navega el árbol AJAX (Año → Mes → Día → PDFs) cubriendo publicaciones desde 1955.

```python
from legismex import MichoacanPoClient

po = MichoacanPoClient()

# Listar años disponibles
anios = po.obtener_anios()
print(f"Años: {[a.nombre for a in anios[:5]]}")

# Meses de un año
meses = po.obtener_meses(anios[0].cat_id)  # más reciente
print([m.nombre for m in meses])

# Todos los PDFs de un mes
archivos = po.obtener_archivos_por_fecha(2025, mes="Enero")
for a in archivos[:3]:
    print(f"[día {a.dia}] {a.nombre}")
    print(f"  PDF: {a.url_pdf}")
```

---

## Paso 26: Congreso del Estado de Morelos (Documentos Legislativos)

El portal del Congreso de Morelos (`congresomorelos.gob.mx`) usa WordPress con el tema Divi. Todos los documentos legislativos están en una sola página estática con enlaces PDF directos en módulos "blurb". `MorelosClient` raspa la página y categoriza los documentos por sección y periodo.

```python
from legismex import MorelosClient

client = MorelosClient()

# Obtener todos los documentos
docs = client.obtener_documentos()
print(f"Total: {len(docs)}")

# Filtrar por sección
ordenes = client.obtener_documentos(seccion="Orden-del-día")
for o in ordenes[:3]:
    print(f"[{o.periodo}] {o.titulo} → {o.url_pdf}")
```

Secciones disponibles: `Actas-de-sesiones-Solemnes`, `Públicas-Ordinarias`, `Diputación-Permanente`, `Orden-del-día`, `Versiones-estenográficas`, `Leyes-y-Códigos`.

---

## Paso 27: Periódico Oficial de Morelos (Tierra y Libertad)

El portal `periodico.morelos.gob.mx` es una aplicación Laravel (con token CSRF) que usa DataTables server-side para listar los ejemplares del Periódico Oficial. `MorelosPoClient` maneja automáticamente el CSRF y pagina los resultados.

```python
from legismex import MorelosPoClient

po = MorelosPoClient()

# Ejemplares de Enero 2025
items, total = po.obtener_ejemplares(anio=2025, mes=1)
print(f"Total: {total}")
for e in items[:3]:
    print(f"#{e.numero} | {e.edicion} | {e.fecha_publicacion}")
    print(f"  Sumario: {e.sumario[:80]}...")
    print(f"  PDF: {e.url_pdf}")

# Buscar por palabra en el sumario
items, total = po.obtener_ejemplares(anio=2024, buscar_sumario="decreto")
print(f"Resultados 'decreto' en 2024: {total}")
```

Endpoints internos: `POST ejemplaresFiltradosPublicoGeneral` con paginación DataTables y parámetros `anios`, `mes`, `buscarSumario`.

---

## Paso 28: Gaceta Parlamentaria del Congreso de Guerrero

La Gaceta Parlamentaria de Guerrero está en `sialgro.dcrsoft.com.mx/gacetaparlamentaria`. Es una app paginada con lista de gacetas y páginas de detalle con tablas de documentos PDF. `GuerreroClient` recorre ambas capas.

```python
from legismex import GuerreroClient

gro = GuerreroClient()

# Listar gacetas
gacetas, total = gro.obtener_gacetas(pagina=1)
print(f"Total: {total}")

# Documentos de una gaceta específica
docs = gro.obtener_documentos(230)
for d in docs[:3]:
    print(f"[{d.tipo}] {d.descripcion[:60]}")
    print(f"  PDF: {d.url_pdf}")
```

Tipos de documento: Actas, Comunicados, Iniciativas, Proyectos de leyes/decretos, Intervenciones, Orden del día.

---

## Paso 29: Periódico Oficial de Guerrero

El portal `periodicooficial.guerrero.gob.mx` es un sitio WordPress con publicaciones paginadas (50/página). `GuerreroPoClient` raspa las tarjetas de publicaciones con filtros opcionales.

```python
from legismex import GuerreroPoClient

po = GuerreroPoClient()

# Todas las publicaciones recientes
pubs = po.obtener_publicaciones()
for p in pubs[:3]:
    print(f"[{p.categoria}] {p.titulo} | {p.fecha}")
    print(f"  PDF: {p.url_pdf}")

# Filtrar por año y categoría
leyes = po.obtener_publicaciones(anio=2025, categoria=25)  # LEYES

# Buscar por palabra clave
decretos = po.obtener_publicaciones(buscar="decreto")
```

Categorías: ACTAS, ACUERDOS, AVISOS, BANDOS, CODIGOS, CONVENIOS, CONVOCATORIAS, DECLARATORIAS, DECRETOS, EDICTOS, FE DE ERRATAS, LEYES, LINEAMIENTOS, NORMAS, REGLAMENTOS, RESOLUCIONES, SENTENCIAS, y más (30 en total).

---

## Paso 30: Congreso del Estado de Tlaxcala (LXV Legislatura)

El portal `congresodetlaxcala.gob.mx/trabajo-legislativo65/` presenta el trabajo legislativo de la LXV Legislatura en una sola página con 12 pestañas (mpc-tabs de Visual Composer) subdividas por año (2024, 2025, 2026).

```python
from legismex import TlaxcalaClient

tlx = TlaxcalaClient()

# Todos los documentos (todos los tabs y años)
docs = tlx.obtener_documentos()
print(f"Total documentos: {len(docs)}")

# Filtrar por categoría
decretos = tlx.obtener_documentos(categoria='Decretos')
iniciativas = tlx.obtener_documentos(categoria='Iniciativas', anio=2025)

# Inspeccionar
for d in decretos[:3]:
    print(f"[{d.anio}] #{d.numero} {d.fecha} — {d.titulo[:60]}")
    print(f"  PDF: {d.url_pdf}")
```

Categorías disponibles: Programa Legislativo, Decretos, Orden del día, Iniciativas, Asistencia, Diario de debates, Acuerdos, Correspondencia, Dictámenes, Votaciones, Versiones estenográficas, Actas de Sesión.

---

## Paso 31: Periódico Oficial del Estado de Tlaxcala

El portal Joomla `periodico.tlaxcala.gob.mx` muestra cada año dentro de un `<iframe>` apuntando a `publicaciones.tlaxcala.gob.mx/indices/YYYY.php`. `TlaxcalaPoClient` lee esa URL directamente.

```python
from legismex import TlaxcalaPoClient

po = TlaxcalaPoClient()

# Obtener todos los registros de un año
eds = po.obtener_ediciones(2026)
print(f"Registros 2026: {len(eds)}")  # 136

for e in eds[:3]:
    print(f"[{e.fecha}] No.{e.numero}: {e.contenido[:60]}")
    print(f"  PDF: {e.url_pdf}")
```

Columnas: `fecha` (YYYY-MM-DD), `numero` (e.g. "Ex", "1Ex", "1-1ª SECC"), `contenido` (descripción), `url_pdf`. Años disponibles: 2011–2026.

---

## Paso 32: Gaceta Parlamentaria del Congreso de Oaxaca (LXVI Legislatura)

El portal `congresooaxaca.gob.mx` lista las gacetas en `parlaments.html` y almacena el detalle de cada sesión en `parlamento/{id}.html`. Los PDFs por punto del orden del día están en el subdominio `docs66.congresooaxaca.gob.mx`.

```python
from legismex import OaxacaClient

oax = OaxacaClient()

# Solo el índice (rápido, 1 request)
gacetas = oax.listar_gacetas()  # 179+ gacetas
g = gacetas[0]  # más reciente
print(f"{g.numero} | {g.tipo} | {g.fecha}")

# Detalle completo con documentos (1 request adicional)
gaceta = oax.obtener_gaceta(179)
for doc in gaceta.documentos:
    print(f"#{doc.numero}: {doc.descripcion[:50]}")
    for pdf in doc.url_pdfs:
        print(f"  {pdf}")
```

Modelos: `OaxacaGaceta` (id, numero, tipo, fecha, url_detalle, documentos) · `OaxacaDocumento` (numero, descripcion, url_pdfs).

---

## Paso 33: Periódico Oficial del Gobierno del Estado de Oaxaca

El sitio `periodicooficial.oaxaca.gob.mx` sirve tres tipos de publicaciones: Ordinario, Extraordinario y Secciones. Cada tipo se obtiene en un solo request desde `busquedadoc.php?type=<Tipo>`. Los PDFs están en `files/YYYY/MM/filename.pdf`. Datos disponibles desde 2010.

```python
from legismex import OaxacaPoClient

po = OaxacaPoClient()

# Todo (12,000+ ediciones)
todas = po.obtener_ediciones()

# Solo Ordinarios de 2026
ords = po.obtener_ediciones(tipo='Ordinario', ano=2026)

# Extraordinarios de marzo 2026
exts = po.obtener_ediciones(tipo='Extraordinario', ano=2026, mes=3)
for e in exts:
    print(f"{e.fecha} | {e.nombre} -> {e.url_pdf}")

# Buscar por keyword en nombre de archivo
resultados = po.buscar('salinas')
```

Modelos: `OaxacaPoEdicion` (tipo, fecha, nombre, url_pdf).

---

## Paso 34: Agenda Legislativa del Congreso de Aguascalientes

El Congreso de Aguascalientes expone una API DataTables REST en `/LegislativeAgenda/GetPagedData`. Tiene 14 tipos de promoción (Iniciativas, Decretos, Gaceta Parlamentaria, Actas, etc.) para 3 legislaturas (LXIV, LXV, LXVI). Los PDFs se descargan de `/LegislativeAgenda/Download?id={id}`.

```python
from legismex import AguascalientesClient

c = AguascalientesClient()

# Todas las promociones LXVI (1,861+ registros)
result = c.obtener_promociones(legislatura='LXVI', tamaño_pagina=100)
print(f"Total: {result['total']}")

# Solo iniciativas (tipo_promocion_id=3)
iniciativas = c.listar_todas(legislatura='LXVI', tipo_promocion_id=3)
for ini in iniciativas[:3]:
    print(f"[{ini.numero_agenda}] {ini.contenido[:80]}")
    print(f"  PDF: {ini.url_pdf}")

# Búsqueda por keyword
resultados = c.listar_todas(legislatura='LXVI', busqueda='educación')

# Otras legislaturas
lxv = c.listar_todas(legislatura='LXV', tipo_promocion_id=9)  # Decretos LXV
```

Modelos: `AgsPromocion` (id, numero_agenda, tipo_promocion, contenido, comisiones, url_pdf, resolucion, ...), `AgsComision`.

Tipos de promocion disponibles (import `TIPOS_PROMOCION`):
- 1: ACUERDO LEGISLATIVO, 2: CUENTA PÚBLICA, 3: INICIATIVA, 4: MINUTA
- 5: NOMBRAMIENTO, 6: PUNTO DE ACUERDO, 7: SOLICITUD, 9: DECRETO
- 10: DICTÁMEN, 11: VERSIONES ESTENOGRÁFICAS, 12: ACTAS
- 13: DIARIO DE DEBATES, 14: GACETA PARLAMENTARIA

---

## Paso 35: Gaceta Legislativa del Congreso de Veracruz

El Congreso de Veracruz publica su Gaceta Legislativa en un listado indexado por "Año de Ejercicio Constitucional". El extracto combina la sesión principal con todos los anexos (leyes, decretos) en tablas dinámicas.

`legismex.veracruz` extrae y anida inteligentemente todo en un solo request.

```python
from legismex.veracruz import VeracruzClient

client = VeracruzClient()
gacetas = client.obtener_gacetas()

print(f"Total de sesiones extraídas: {len(gacetas)}")

# Explorar la sesión más reciente
sesion = gacetas[0]
print(f"[{sesion.fecha}] {sesion.tipo_sesion} | {sesion.anio_ejercicio}")
print(f"Gaceta PDF: {sesion.gaceta_pdf}")
print(f"Versión Estenográfica: {sesion.version_estenografica_pdf}")

# Listar los anexos que fueron adjuntados a esta sesión
print(f"Total Anexos (Leyes/Decretos): {len(sesion.anexos)}")
for anexo in sesion.anexos:
    print(f"  -> {anexo.titulo[:50]}... | {anexo.url_pdf}")

# Mostrar todos los audios y videos de la sesión
for mp3 in sesion.audio_urls:
    print(f"  🎵 Audio: {mp3}")
for mp4 in sesion.video_urls:
    print(f"  🎥 Video: {mp4}")
```

Modelos: `VeracruzSesion` (fecha, tipo_sesion, periodo, anio_ejercicio, gaceta_pdf, acta_pdf, version_estenografica_pdf, audio_urls, video_urls, anexos), `VeracruzDocumento` (titulo, url_pdf, es_anexo).

---

## Paso 36: Gaceta Oficial del Estado de Veracruz (Periódico Oficial)

El Periódico Oficial de Veracruz utiliza un mecanismo antiguo enviando el año y mes a un formulario y respondiendo con un listado que incluye cada edición y sus respectivos tomos extraordinarios.

`legismex.veracruz_po` interroga el endpoint de búsqueda y extrae todos los enlaces expuestos construyendo objetos listos para consultar:

```python
from legismex.veracruz_po import VeracruzPoClient

po = VeracruzPoClient()

# Consultar las publicaciones de Febrero (2) del 2024
ediciones = po.obtener_ediciones(anio=2024, mes=2)

print(f"Total de ediciones: {len(ediciones)}")

for edicion in ediciones[:3]:
    print(f" -> {edicion.nombre} | {edicion.fecha_textual}")
    print(f"    Descarga directa: {edicion.url_pdf}")
```

Modelos: `VeracruzPoEdicion` (nombre, fecha_textual, url_pdf).

---

## Paso 37: Gaceta Parlamentaria de Tamaulipas

El Congreso del Estado de Tamaulipas concentra sus Gacetas Parlamentarias en una sola vista para la legislatura vigente. `legismex.tamaulipas` extrae todos los enlaces expuestos construyendo objetos listos para consultar:

```python
from legismex import TamaulipasClient

client = TamaulipasClient()

# Extrae la lista completa de la 66 Legislatura
gacetas = client.obtener_gacetas()

print(f"Total de Gacetas de Tamaulipas: {len(gacetas)}")

for gaceta in gacetas[:3]:
    print(f"[{gaceta.fecha_gaceta}] Sesión {gaceta.sesion} - {gaceta.url_pdf}")
```

Modelos: `TamaulipasGaceta` (legislatura, publicado_el, numero, tomo, fecha_gaceta, fecha_sesion, sesion, url_pdf).

---

## Paso 38: Periódico Oficial del Estado de Tamaulipas

El Periódico Oficial de Tamaulipas distribuye sus ediciones interactivamente a través de un calendario web en WordPress. Con `legismex.tamaulipas_po`, iteramos y mapeamos los días habilitados reconstruyendo los enlaces a las secciones PDF (ej. Extraordinario, Legislativo, Judicial).

```python
from legismex import TamaulipasPoClient

po = TamaulipasPoClient()

# Consultamos Marzo (3) de 2026
ediciones = po.obtener_ediciones(anio=2026, mes=3)

print(f"Total de días de publicación en el mes: {len(ediciones)}")

for edicion in ediciones[:3]:
    print(f"[{edicion.fecha}] Tomo {edicion.tomo} | Núm. {edicion.numero}")
    
    # Cada edición diaria puede contener n anexos
    for documento in edicion.documentos:
        print(f"   -> {documento.titulo}: {documento.url_pdf}")
```

Modelos: `TamaulipasPoEdicion` (fecha, tomo, numero, documentos), `TamaulipasPoDocumento` (titulo, url_pdf).

---

### 🐆 Chiapas - Gaceta Parlamentaria
El Congreso del Estado de Chiapas renderiza su tabla de gacetas de manera asíncrona mediante un API estática basada en PHP. `legismex` efectúa la llamada interna con los parámetros adecuados, entregándote el historial completo de un solo golpe.

```python
from legismex import ChiapasGacetaClient

client = ChiapasGacetaClient()
gacetas = client.obtener_gacetas()

print(f"Total de publicaciones extraídas: {len(gacetas)}")

for gaceta in gacetas[:2]:
    print(f"[{gaceta.periodo}] {gaceta.numero} - {gaceta.titulo}")
    print(f" -> Enlace: {gaceta.url_pdf}\n")
```

### 🐆 Chiapas - Periódico Oficial de Chiapas aloja sus publicaciones segregadas por sexenios (`periodico0612` hasta `periodico2430`). El cliente de `legismex.chiapas_po` gestiona la segmentación, extrayendo las páginas automáticamente. 

```python
from legismex import ChiapasPoClient, ChiapasAdministracion

client = ChiapasPoClient()

# Consultamos los diarios publicados en Diciembre de 2024 del sexenio entrante
ediciones = client.obtener_ediciones(
    admin=ChiapasAdministracion.ADMIN_2024_2030,
    anio=2024,
    mes=12
)

print(f"Total de registros encontrados: {len(ediciones)}")

for edicion in ediciones[:3]:
    print(f"Num: {edicion.numero} | Fecha: {edicion.fecha}")
    print(f"Sección: {edicion.seccion} | Parte: {edicion.parte}")
    print(f"Descargar PDF: {edicion.url_pdf}\n")
```

Modelos: `ChiapasPoEdicion` (numero, fecha, seccion, parte, url_pdf), `ChiapasAdministracion` (Endpoints por quinquenio).

---

## Paso 40: Iniciativas del Congreso del Estado de Tabasco

La extracción de datos de Tabasco resuelve la totalidad de los cientos de entradas de una legislatura en una sola llamada (el sitio no pagina los requests HTML del lado del servidor). El cliente `TabascoIniciativasClient` hace el filtro por mes y año localmente antes de devolver el arreglo acotado en memoria.

```python
from legismex import TabascoIniciativasClient

client = TabascoIniciativasClient()

# Extraemos las iniciativas del mes de Febrero 2026
iniciativas_febrero = client.obtener_iniciativas(anio=2026, mes=2)
print("Total de iniciativas de ese mes:", len(iniciativas_febrero))

for ini in iniciativas_febrero[:3]:
    print(f"[{ini.fecha}] Num {ini.numero}")
    print(f"Título: {ini.titulo}")
    print(f"Turnada a comisión: {ini.comision}")
    print(f"PDF: {ini.url_pdf}\n")
```

Modelos devueltos: `TabascoIniciativa` (numero, titulo, comision, presentada_por, fecha, trimestre, anio, url_pdf).

---

## Paso 41: Periódico Oficial del Estado de Tabasco

El Periódico Oficial de Tabasco se extrae de forma paginada. El cliente `TabascoPoClient` permite realizar búsquedas específicas o simplemente navegar por las últimas ediciones publicadas.

```python
from legismex import TabascoPoClient

client = TabascoPoClient()

# Obtener las últimas 20 publicaciones (2 páginas de 10 c/u)
publicaciones = client.obtener_publicaciones(paginas=2)

for pub in publicaciones:
    print(f"[{pub.fecha}] Edición: {pub.numero} ({pub.tipo})")
    print(f"Descripción: {pub.descripcion}")
    print(f"PDF: {pub.url_pdf}\n")

# También soporta búsquedas por texto (ej. un año o institución)
pubs_2025 = client.obtener_publicaciones(busqueda="2025", paginas=1)
```

Modelos: `TabascoPoPublicacion` (fecha, numero, tipo, suplemento, descripcion, url_pdf).

---

## Paso 42: Gaceta Parlamentaria de Campeche

El Congreso de Campeche aglutina las últimas cuatro legislaturas en una única vista organizada por pestañas UI. La integración explota esta base para brindar un listado masivo en una sola petición a gran velocidad.

```python
from legismex import CampecheClient
import asyncio

async def main():
    client = CampecheClient()
    
    # Obtener el acumulado histórico (sincrónico o asincrónico)
    gacetas = await client.a_obtener_gacetas()
    
    # Listar las 5 revistas agregadas más recientes
    for gaceta in gacetas[:5]:
        print(f"[{gaceta.legislatura}] : {gaceta.titulo}")
        print(f" Enlace: {gaceta.url_pdf}\n")

asyncio.run(main())
```

Modelo devuelto: `CampecheGaceta` (titulo, legislatura, url_pdf).

---

## Paso 43: Periódico Oficial de Campeche

El SIPOEC del Estado de Campeche permite buscar el catálogo de edictos u oficios periódicos según el año. El integrador permite leer N páginas de un año y descifrar la ruta lógica que el propio portal emplea usando el nombre y el mes de publicación, previniendo sobrecargas del API REST.

```python
from legismex import CampechePoClient
import asyncio

async def get_po():
    client = CampechePoClient()
    
    # Consultamos las primeras 2 pags de 2026
    documentos = await client.a_obtener_publicaciones(anio=2026, paginas=2)
    
    for d in documentos:
        print(f"[{d.fecha}] {d.titulo}")
        print(f"Link de Recuperación: {d.url_pdf}")

asyncio.run(get_po())
```

Modelo devuelto: `CampechePoPublicacion` (titulo, fecha, url_pdf).

---

## Paso 44: Gaceta Parlamentaria de Quintana Roo

El Congreso del Estado de Quintana Roo basa su gaceta en la tecnología Nuxt bajo un modelo de consumo de APIs en formato JSON. El integrador permite orquestar de manera nativa la obtención tanto de los IDs mensuales como del arbol de documentos adheridos (y sus URLs en crudo correspondientes) sin depender de scraping de HTML pesado ni navegadores en tiempo real.

```python
from legismex import QrooClient
import asyncio

async def test_qroo():
    client = QrooClient()
    
    # Obtener todas las gacetas publicadas en el mes 3 del año 2026.
    # El flag "extraer_documentos=True" (por defecto) encadenará peticiones asyncio 
    #   para traer el anexo y los archivos de cada boletín devuelto.
    gacetas = await client.a_obtener_gacetas(anio=2026, mes=3)
    
    for g in gacetas:
        print(f"[{g.fecha_publicacion}] {g.nomenclatura} - {g.titulo}")
        for doc in g.documentos:
            print(f"  - ({doc.tipo_doc}) {doc.titulo}")
            print(f"    URL: {doc.url}")

asyncio.run(test_qroo())
```

Modelo devuelto: `QrooGaceta` el cual contiene localmente una lista tipada del modelo esclavo `QrooDocumento`.

---

## Paso 45: Periódico Oficial del Estado de Quintana Roo

El Periódico Oficial del Estado de Quintana Roo exhibe un buscador histórico de avanzada. Esta integración procesa todo por el sistema de fechas, solicitando el equivalente a todo un mes del calendario y resolviendo la paginación de los registros descubiertos que tengan un documento PDF adjunto.

```python
from legismex import QrooPoClient
import asyncio

async def test_qroo_po():
    client = QrooPoClient()
    
    # Extraer todas las publicaciones del mes de Febrero del 2026.
    # El motor rastrea el "1 de Feb" hasta "28 de Feb" internamente iterando sus páginas.
    pubs = await client.a_obtener_publicaciones(anio=2026, mes=2)
    
    print(f"Total: {len(pubs)}")
    for pub in pubs[:5]:
        print(f"[{pub.fecha}] {pub.tipo} Num.{pub.numero} Tomo {pub.tomo}")
        print(f"  URL: {pub.url_pdf}")

asyncio.run(test_qroo_po())
```

Modelo devuelto: `QrooPoPublicacion` (fecha, tipo, numero, tomo, url_pdf).

---

## Paso 46: H. Congreso del Estado de Colima

Este módulo extrae la información de la **Gaceta Parlamentaria del Congreso del Estado de Colima**. Obtiene decretos, actas, diario de debates e iniciativas conectándose a su endpoint por AJAX interactuando con su vista centralizada, discriminando correctamente entre cabeceras y devolviendo resultados estructurados según el tipo resolutivo.

```python
import asyncio
from legismex.colima import ColimaClient, ColimaDecreto, ColimaIniciativa

async def main():
    client = ColimaClient()
    
    # Extraemos Decretos e Iniciativas para la Legislatura "LXI Legislatura" (id=61)
    decretos = await client.a_obtener_decretos(legislatura_id=61, legislatura_nombre="LXI Legislatura")
    print(f"Total Decretos: {len(decretos)}")
    if decretos:
        print(decretos[0].numero, "-", decretos[0].descripcion, "->", decretos[0].url_pdf)
        
    iniciativas = await client.a_obtener_iniciativas(legislatura_id=61, legislatura_nombre="LXI Legislatura")
    print(f"Total Iniciativas: {len(iniciativas)}")
    if iniciativas:
        print(iniciativas[0].numero, "- Estatus:", iniciativas[0].status)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Paso 48: Periódico Oficial del Estado de Nayarit

Este módulo extrae publicaciones del **Periódico Oficial del Gobierno del Estado de Nayarit** (`periodicooficial.nayarit.gob.mx`). Soporta tres tipos de búsqueda enviando peticiones POST al endpoint PHP del portal, con paginación automática opcional.

Tipos de búsqueda disponibles:

| Método | descripción |
|---|---|
| `buscar_por_fecha("YYYY-MM-DD")` | Todas las publicaciones de una fecha |
| `buscar_por_palabra("término")` | Búsqueda de texto libre en sumarios |
| `buscar_avanzada("término", "fecha_inicio", "fecha_fin")` | Combina palabra clave + rango de fechas |

```python
import asyncio
from legismex import NayaritPoClient

async def main():
    client = NayaritPoClient()

    # 1. Por fecha
    resultado = await client.a_buscar_por_fecha("2026-03-05")
    print(f"Publicaciones del 2026-03-05: {resultado.total}")
    for pub in resultado.publicaciones:
        print(f"  [{pub.seccion}] {pub.tipo}: {(pub.sumario or '')[:60]}...")
        print(f"  PDF: {pub.url_pdf}")

    # 2. Por palabra (página 1 de muchas)
    decreto = await client.a_buscar_por_palabra("decreto")
    print(f"\n'decreto' → {decreto.total} registros ({decreto.total_paginas} páginas)")

    # 3. Búsqueda avanzada con rango de fechas
    avanzada = await client.a_buscar_avanzada("ley", "2026-01-01", "2026-03-01")
    print(f"\nLeyes (ene–mar 2026): {avanzada.total} resultados")
    for pub in avanzada.publicaciones[:3]:
        print(f"  {pub.fecha_publicacion} | {pub.tipo}: {(pub.sumario or '')[:60]}...")

if __name__ == "__main__":
    asyncio.run(main())
```

**Paginación automática** (descarga todas las páginas en paralelo):
```python
# Obtiene los 2,114 decretos históricos en un solo llamado
todos = await client.a_buscar_por_palabra("decreto", all_pages=True)
print(f"Total descargados: {len(todos.publicaciones)}")
```

---

## Paso 49: H. Congreso del Estado de Sinaloa

Este módulo extrae la actividad legislativa completa del **H. Congreso del Estado de Sinaloa** (`gaceta.congresosinaloa.gob.mx`). El portal es una SPA Vue.js que carga todos los datos de cada legislatura en **una sola petición JSON**; el filtrado y la paginación son del lado del cliente.

Legislaturas disponibles: **LX–LXV** (números `"60"` al `"65"`).

Datos disponibles:
- **Iniciativas** — combinadas de 3 grupos (individual, conjunto, grupo)
- **Dictámenes**
- **Acuerdos**
- **Decretos**

```python
import asyncio
from legismex import SinaloaClient

async def main():
    client = SinaloaClient()

    # Consultar legislaturas disponibles
    legs = await client.a_obtener_legislaturas()
    for l in legs:
        print(f"  {l.id} — {l.nombre}")

    # Iniciativas de la LXV Legislatura (actual = "65")
    iniciativas = await client.a_obtener_iniciativas("65")
    print(f"\nIniciativas (LXV): {len(iniciativas)}")
    for ini in iniciativas[:3]:
        print(f"  [{ini.id}] {ini.fecha} | {(ini.presentada or '')[:40]}")
        print(f"        {(ini.iniciativa or '')[:80]}...")

    # Dictámenes, Acuerdos y Decretos en paralelo
    dictamenes, acuerdos, decretos = await asyncio.gather(
        client.a_obtener_dictamenes("65"),
        client.a_obtener_acuerdos("65"),
        client.a_obtener_decretos("65"),
    )

    print(f"\nDictámenes: {len(dictamenes)} | Acuerdos: {len(acuerdos)} | Decretos: {len(decretos)}")

    print(f"\nÚltimo decreto: [{decretos[0].id}] {decretos[0].fecha}")
    print(f"  {(decretos[0].asunto or '')[:80]}...")

if __name__ == "__main__":
    asyncio.run(main())
```

**Versión síncrona:**
```python
from legismex import SinaloaClient

client = SinaloaClient()
# Legislatura anterior (LXIV = 64)
iniciativas_64 = client.obtener_iniciativas("64")
print(f"LXIV — Iniciativas: {len(iniciativas_64)}")
```

---

## Paso 50: Periódico Oficial del Estado de Sinaloa (POES)

Este módulo extrae las ediciones del **Periódico Oficial del Estado de Sinaloa** desde `strc.transparenciasinaloa.gob.mx/poes/`. El sitio es WordPress con *The Events Calendar* plugin; cada edición es un «evento» con fecha, número, índice de contenido y un PDF descargable en `media.transparencia.sinaloa.gob.mx`.

Características:
- **Ediciones ordinarias** y **vespertinas** (detectadas automáticamente).
- **PDF directo** extraído del HTML de la descripción.
- **Índice en texto plano** de la edición.
- Búsqueda por **fecha**, **mes** o **año completo**.

```python
import asyncio
from legismex import SinaloaPoClient

async def main():
    client = SinaloaPoClient()

    # Mes específico
    marzo = await client.a_buscar_mes(2026, 3)
    print(f"Marzo 2026: {len(marzo)} ediciones")
    for e in marzo:
        flag = " [VESP]" if e.vespertina else ""
        print(f"  {e.fecha} | {e.titulo}{flag}")
        print(f"           PDF: {e.pdf_url}")

    # Año completo (descarga todas las páginas en paralelo)
    ediciones_2025 = await client.a_buscar_anio(2025)
    vesp = [e for e in ediciones_2025 if e.vespertina]
    print(f"\n2025: {len(ediciones_2025)} ediciones ({len(vesp)} vespertinas)")

    # Rango personalizado
    q1 = await client.a_buscar(start_date="2025-01-01", end_date="2025-03-31")
    print(f"Q1 2025: {len(q1)} ediciones")

asyncio.run(main())
```

**Versión síncrona:**
```python
from legismex import SinaloaPoClient

client = SinaloaPoClient()
enero = client.buscar_mes(2026, 1)
print(f"Enero 2026: {len(enero)} ediciones")
for e in enero[:3]:
    print(f"  {e.fecha} | {e.titulo} → {e.pdf_url}")
```

---

## Paso 51: Gaceta Parlamentaria del H. Congreso del Estado de Sonora

El módulo `sonora` extrae las Gacetas Parlamentarias del [Congreso del Estado de Sonora](https://congresoson.gob.mx/gacetas). El sitio es una SPA en Astro/React que consume la API REST `gestion.api.congresoson.gob.mx/publico/` — sin autenticación.

Características:
- **7 legislaturas** disponibles de LVIII (2006) a LXIV (2024–2027).
- Tipos de sesión: **PLENO** y **COMISION**.
- **PDF adjunto** recuperable vía detalle con `expand=mediaGaceta.media`.
- Búsqueda por **palabra clave** y **rango de fechas**.
- Paginación automática con descargas paralelas (async).

```python
import asyncio
from legismex import SonoraClient

async def main():
    client = SonoraClient()

    # Legislaturas disponibles
    legs = await client.a_obtener_legislaturas()
    for l in legs:
        print(f"{l.nombre}: {l.descripcion}")

    # Todas las gacetas de la legislatura actual (LXIV)
    gacetas = await client.a_buscar(legislatura="LXIV")
    print(f"LXIV: {len(gacetas)} gacetas")
    pleno = [g for g in gacetas if g.tipo == "PLENO"]
    print(f"  Pleno: {len(pleno)} | Comisión: {len(gacetas)-len(pleno)}")

    # Filtrar por fecha
    enero = await client.a_buscar(
        legislatura="LXIV",
        fecha_inicio="2026-01-01",
        fecha_fin="2026-01-31",
    )
    print(f"Enero 2026: {len(enero)} gacetas")

    # Detalle con PDF
    detalle = await client.a_obtener_detalle(gacetas[0].id)
    print(f"PDF: {detalle.pdf_urls[0] if detalle.pdf_urls else 'N/A'}")

asyncio.run(main())
```

**Versión síncrona:**
```python
from legismex import SonoraClient

client = SonoraClient()
# Legislatura anterior (LXIII)
lxiii = client.buscar(legislatura="LXIII")
print(f"LXIII: {len(lxiii)} gacetas")
```

---

### Paso 52: Periódico Oficial del Estado de Sonora (sonora_po)

El módulo `sonora_po` permite obtener las ediciones del Boletín Oficial de Sonora navegando por años y meses (archivo histórico 1981–2026).

```python
from legismex import SonoraPoClient

client = SonoraPoClient()

# Obtener ediciones de un mes específico (Enero 2026)
resultado = client.obtener_ediciones(anio=2026, mes=1)
print(f"Ediciones en {resultado.anio}-{resultado.mes}: {len(resultado.ediciones)}")

for ed in resultado.ediciones:
    print(f"[{ed.fecha}] {ed.edicion_tipo} No. {ed.numero} - PDF: {ed.url_pdf}")

# Obtener todas las ediciones de un año
resultado_2025 = client.obtener_ediciones(anio=2025)
print(f"Total ediciones en 2025: {len(resultado_2025.ediciones)}")

# Versión asíncrona
import asyncio

async def fetch():
    res = await client.a_obtener_ediciones(2026, mes=2)
    print(f"Febrero 2026: {len(res.ediciones)} ediciones")

asyncio.run(fetch())
```

---

## Paso 55: Gaceta Legislativa de Hidalgo

Para consultar las gacetas del Congreso de Hidalgo, utiliza el `HidalgoGacetaClient`. Puedes listar sesiones con filtros de año, mes y tipo, y luego obtener el detalle de los documentos asociados.

```python
from legismex import HidalgoGacetaClient

client = HidalgoGacetaClient()

# Listar sesiones de Enero 2026
sesiones = client.obtener_sesiones(periodo=2026, mes=1)

for s in sesiones:
    print(f"[{s.fecha}] {s.titulo}")
    
    # Obtener detalle de la primera sesión encontrada
    detalle = client.obtener_detalle_sesion(s.session_id)
    for doc in detalle.documentos:
        if doc.es_existente:
            print(f"  - Documento: {doc.nombre}")
            print(f"    URL: {doc.url}")
```

---

## Paso 56: Periódico Oficial del Estado de Hidalgo

El `HidalgoPoClient` permite realizar búsquedas avanzadas en el Periódico Oficial. Puedes buscar por rango de fechas, términos en el sumario y tipo de edición.

```python
from datetime import date
from legismex import HidalgoPoClient

client = HidalgoPoClient()

# Buscar ediciones de la primera semana de marzo 2026
desde = date(2026, 3, 1)
hasta = date(2026, 3, 7)
resultado = client.buscar(fecha_desde=desde, fecha_hasta=hasta)

print(f"Ediciones encontradas: {resultado.total_registros}")

for edicion in resultado.ediciones:
    print(f"[{edicion.fecha}] {edicion.nombre}")
    print(f"Sumario: {edicion.sumario[:100]}...")
    print(f"PDF: {edicion.url_pdf}\n")
```

---

## Paso 57: Gaceta Parlamentaria de Zacatecas

Para consultar la actividad del Congreso de Zacatecas (LXV Legislatura), utiliza el `ZacatecasClient`. Este cliente extrae las gacetas organizadas por mes.

```python
from legismex import ZacatecasClient

client = ZacatecasClient()

# Listar meses disponibles (formato MMYYYY)
meses = client.obtener_meses()
print(f"Meses disponibles: {meses[:5]}...")

# Obtener gacetas del mes actual
gacetas = client.obtener_gacetas()

# O de un mes específico (ej. Febrero 2026)
# gacetas = client.obtener_gacetas("022026")

for g in gacetas:
    print(f"[{g.fecha}] {g.tipo_sesion} - No. {g.numero}")
    print(f"URL PDF: {g.url_pdf}\n")
```

**Versión asíncrona:**
```python
import asyncio
from legismex import ZacatecasClient

async def main():
    client = ZacatecasClient()
    gacetas = await client.a_obtener_gacetas("032026")
    for g in gacetas:
        print(f"{g.fecha}: {g.url_pdf}")

asyncio.run(main())
```

### Paso 58: Consultar el Periódico Oficial del Estado de Zacatecas

La API del POEZ interactúa mediante JSON puro hacia distintas colecciones de documentos. `ZacatecasPoClient` consolida todo permitiendo extraer periódicos ordinarios, suplementos y todo el marco normativo histórico.

```python
import asyncio
from legismex import ZacatecasPoClient

async def probar_zacatecas_po():
    client = ZacatecasPoClient()
    
    # 1. Obtener ediciones ordinarias en un rango
    ordinarios = await client.a_obtener_ediciones(fecha_inicial="2026-03-01", fecha_final="2026-03-31")
    print(f"Ordinarios encontrados: {len(ordinarios)}")
    
    # 2. Obtener Suplementos
    suplementos = await client.a_buscar_suplementos()
    print(f"Suplementos recientes: {len(suplementos)}")
    
    # 3. Mostrar la Ley más antigua disponible (última de la lista)
    leyes = await client.a_buscar_leyes()
    if leyes:
        ley_antigua = leyes[-1]
        print(f"\nLey más antigua:")
        print(f"Fecha: {ley_antigua.fecha_publicacion}")
        print(f"Título: {ley_antigua.descripcion}")
        print(f"Enlace PDF: {ley_antigua.url_pdf}")

if __name__ == "__main__":
    asyncio.run(probar_zacatecas_po())
```

### Paso 59: Extraer Gacetas del Congreso de Durango

El cliente `DurangoGacetaClient` está diseñado para leer las tablas `TablePress` incrustadas en el CMS de WordPress del Congreso del Estado de Durango y obtener los enlaces directos a las publicaciones de los periodos Ordinario y Permanente.

```python
import asyncio
from legismex import DurangoGacetaClient

async def probar_durango_gaceta():
    client = DurangoGacetaClient()
    
    # Extraer gacetas del periodo ordinario (tabla tablepress-41)
    ordinarios = await client.a_obtener_ordinarios()
    print(f"Ordinarios recuperados: {len(ordinarios)}")
    
    if ordinarios:
        print(f"Primera gaceta ordinaria: {ordinarios[0].numero} | Publicada el: {ordinarios[0].fecha}")
        print(f"Enlace PDF: {ordinarios[0].url_pdf}")
        
    print("-" * 40)
    
    # Extraer gacetas de la Comisión Permanente (tabla tablepress-88)
    permanente = await client.a_obtener_permanente()
    print(f"Permanentes recuperadas: {len(permanente)}")
    
    # También puedes obtener todas combinadas en una sola llamada:
    todas = await client.a_obtener_todas()
    print(f"\nTotal combinadas en el sistema: {len(todas)}")

if __name__ == "__main__":
    asyncio.run(probar_durango_gaceta())
```

### Paso 60: Extraer Periódico Oficial del Estado de Durango

El cliente `DurangoPoClient` resuelve automáticamente la estructura modular extraída de React Server Components de Next.js, escaneando internamente las URL embebidas alojadas en Amazon S3.

```python
from legismex import DurangoPoClient
import asyncio

async def probar_durango_po():
    client = DurangoPoClient()
    # Se consulta la primera página de publicaciones
    ediciones = await client.a_obtener_ediciones(pagina=1)
    
    for ed in ediciones[:3]:
        print(f"[{ed.fecha}] {ed.titulo}")
        print(f"S3 URL: {ed.url_pdf}")

if __name__ == "__main__":
    asyncio.run(probar_durango_po())
```

## 58. Congreso del Estado de Baja California (`bc_congreso`)

Para descargar iniciativas de ley, posicionamientos y proposiciones ingresadas en el Congreso de Baja California:

```python
import asyncio
from legismex import BcCongresoClient

async def extraer_bc():
    client = BcCongresoClient()
    # Para extraer la primera página:
    iniciativas = await client.a_obtener_iniciativas(max_paginas=1)
    
    print(f"Total extraídas: {len(iniciativas)}")
    for i in iniciativas[:3]:
        print(f"[{i.fecha}] {i.tipo} by {i.presentado_por} -> {i.url_pdf}")

asyncio.run(extraer_bc())
```
