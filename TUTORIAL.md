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

## 💾 Paso 5: Exportando Datos para Análisis (con Pandas)

Ya que `legismex` usa **Pydantic**, convertir las respuestas a formatos tabulares para machine learning o visualización de datos es increíblemente fácil.

Aquí mostramos cómo guardar todas las votaciones de un periodo en un archivo Excel o CSV usando la librería `pandas`:

```python
# Requiere tener instalado pandas: pip install pandas
import pandas as pd

# 1. Convertimos la lista de objetos Pydantic a una lista de diccionarios
datos_para_df = [v.model_dump() for v in votaciones]

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

## Siguientes Pasos

* Consulta el código fuente de [src/legismex/gaceta/client.py](src/legismex/gaceta/client.py) para ver cómo manejamos los tiempos de respuesta.
* Si te interesa descargar los PDFs masivamente y extraer su texto interno, revisa bibliotecas como `PyMuPDF` (`fitz`) combinadas con las URL devueltas por nuestro cliente.
