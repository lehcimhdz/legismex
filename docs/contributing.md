# Guía de Contribución para `legismex` 🇲🇽

¡Gracias por tu interés en contribuir a `legismex`! Este proyecto tiene como objetivo abstraer y estandarizar el acceso a la información legislativa y oficial de los 32 estados de la República Mexicana, el Senado, la Cámara de Diputados y el DOF.

Para mantener la calidad, consistencia y facilidad de uso de la biblioteca, te pedimos que sigas estas directrices al agregar un nuevo scraper para un estado o modificar uno existente.

## Estructura de Directorios

Cada entidad o fuente de información debe tener su propio directorio dentro de `src/legismex/`. Si el estado tiene Congreso y Periódico Oficial (PO), se deben crear dos carpetas independientes.

**Ejemplo para Nuevo León:**
* `src/legismex/nuevoleon/` (Para el Congreso o Gaceta Parlamentaria)
* `src/legismex/nuevoleon_po/` (Para el Periódico Oficial)

Cada directorio debe contener al menos los siguientes tres archivos:
1. `__init__.py`: Importa las clases públicas (cliente y modelos).
2. `client.py`: Contiene la lógica del Web Scraper / API Client.
3. `models.py`: Contiene los modelos de datos usando **Pydantic**.

## 1. Modelado de Datos (`models.py`)

Todos los datos extraídos deben ser transformados en objetos estructurados utilizando `pydantic.BaseModel`.

**Reglas:**
* Los nombres de las clases deben seguir el formato `[Estado][Módulo][Clase]`. Ej: `NuevoLeonIniciativa`, `NuevoLeonPoEdicion`.
* Usa `typing.Optional` para campos que puedan no estar presentes.
* Usa alias (`Field(alias="...")`) si consumes una API JSON, para que el modelo mapee correctamente y mantengas atributos en *snake_case* en Python.

## 2. El Cliente Web (`client.py`)

La clase cliente debe llamarse `[Estado]Client` o `[Estado]PoClient` (ej. `NuevoLeonClient`, `NuevoLeonPoClient`).

**Uso de `httpx`:**
* Usa `httpx.Client()` en lugar de `requests` para un mejor rendimiento y soporte asíncrono.
* **SSL Issues**: Muchos portales gubernamentales tienen certificados vencidos. Configura el cliente con `verify=False` si es estrictamente necesario.
* **Tiempos de espera**: Define un `timeout` razonable (por defecto 30.0 segundos).
* **Paridad Síncrona / Asíncrona**: Cuando sea aplicable, provee versiones síncronas (`obtener_gacetas`) y asíncronas (`a_obtener_gacetas`) utilizando `httpx.AsyncClient`.

**Firma de Métodos:**
* Asegúrate de agregar *docstrings* y que los métodos devuelvan listas de los modelos de `Pydantic` definidos. Evita devolver diccionarios crudos o listas genéricas.

## 3. Scripts de Verificación (`tests/`)

Es obligatorio crear un script de validación (auditoría) visual para probar tu código, llamado `verify_[estado]_[modulo].py` dentro de la carpeta `tests/`.

Ejemplo: `tests/verify_nuevoleon_congreso.py`.

Este script debe instanciar tu cliente, realizar una consulta básica (como obtener el último mes o la primera página), e imprimir de forma ordenada los primeros 3 resultados en la terminal para demostrar que el parser y los enlaces a los PDFs funcionan correctamente.

## Flujo de Trabajo (Pull Request)

1. Crea una rama para tu estado o característica (ej. `feat/estado-mexico`).
2. Implementa los modelos, el cliente y el `__init__.py`.
3. Crea y verifica con el script en `tests/`.
4. Añade una sección corta al final del `TUTORIAL.md` con un ejemplo de uso (opcional pero muy recomendado).
5. Haz commit y empuja tus cambios.
6. Abre el PR.

¡Agradecemos mucho tu ayuda para democratizar el acceso a las leyes de México!
