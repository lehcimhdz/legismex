# legismex

Biblioteca en Python para facilitar el trabajo legislativo en México. Extrae, estructura y provee acceso analítico a fuentes como el Sistema de Información Legislativa (SIL), permitiendo a monitoristas legislativos, analistas de datos y consultoras acceder a datos limpios.

## Características Actuales (MVP)

Actualmente, `legismex` ofrece soporte inicial para el **Sistema de Información Legislativa (SIL)**.

*   **Reportes de Sesión:** Listado de sesiones recientes de la Cámara de Diputados y la Cámara de Senadores (Efemérides, Iniciativas, Dictámenes, etc.).
*   **Extracción de Detalle Estructurado:** Parsea el detalle de cada asunto discutido en sesión, separando el tipo de asunto, el título, el promovente y los trámites.
*   **Texto para NLP:** Extrae de manera adicional el contenido crudo completo de la sesión (~190,000 caracteres por sesión) para facilitar modelos de Procesamiento de Lenguaje Natural (NLP).
*   **Modelos Fuertes:** Usa `Pydantic` para estructurar la salida de los datos legislativos de forma estricta.

## Instalación

*Se requiere Python 3.9 o superior.*

Puedes instalar las dependencias de desarrollo locales con:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Ejemplo de Uso

```python
from legismex.sil import SILClient

client = SILClient()

# 1. Obtener lista de las sesiones más recientes en la Cámara de Senadores
sesiones_senado = client.get_reportes_sesiones(camara="senadores")
print(f"Última sesión: {sesiones_senado[0].fecha} - {sesiones_senado[0].tipo_sesion}")

# 2. Obtener el detalle a fondo de la última asamblea
detalle = client.get_reporte_sesion(sesiones_senado[0].url_detalle)

# Asuntos Estructurados
for asunto in detalle.asuntos[:3]:
    print(f"[{asunto.tipo_asunto}] {asunto.promovente}: {asunto.titulo[:50]}...")

# Contexto no estructurado para IA o Búsquedas textuales completas
texto_crudo = detalle.texto_raw
print(f"Total Caracteres Crudos: {len(texto_crudo)}")
```

## Pruebas

Para correr la pequeña suite de pruebas estructurales:
```bash
pytest tests/
```

## Hoja de Ruta
*   **[EN DESARROLLO]** Módulo de Iniciativas y Legisladores (Extracción detallada de Perfiles y Votaciones).
*   Integración con Diario Oficial de la Federación (DOF).
*   Soporte para Gaceta Parlamentaria.
