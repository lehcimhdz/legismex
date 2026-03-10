# 🛠️ Manejo de Errores y Excepciones

Legismex cuenta con un sistema formal de excepciones para ayudarte a manejar las impredecibles caídas de los portales gubernamentales de México de manera elegante ("Fail Gracefully").

Todas las excepciones se encuentran en el módulo `legismex.exceptions`.

## Jerarquía de Excepciones

Todas las excepciones heredan de `LegismexError`:

- `LegismexError`: La clase base para todos los errores de la librería.
  - `LegismexConnectionError`: Lanzada por caídas de servidor, timeouts o certificados SSL inválidos.
  - `HTMLParsingError`: Lanzada cuando el Congreso o PO cambió el diseño de su página y los selectores de Beautiful Soup ya no coinciden.
  - `APIResponseError`: Lanzada cuando una API REST/JSON interna de un estado cambia su *payload* o devuelve error 500.
  - `DocumentNotFoundError`: Lanzada cuando buscas una gaceta o publicación que no existe en el sistema oficial.

## Ejemplo de Uso (Try/Except)

Si deseas blindar tu código en producción sin que tu programa aborte ejecución:

```python
from legismex import ZacatecasPoClient
from legismex.exceptions import HTMLParsingError, LegismexConnectionError

client = ZacatecasPoClient()

try:
    ediciones = client.obtener_ediciones()
    print(f"Éxito: {len(ediciones)}")

except LegismexConnectionError:
    print("🚨 El servidor del Gobierno de Zacatecas se cayó. Reintentando...")
except HTMLParsingError:
    print("🚨 El Gobierno renovó su página web. Hay que actualizar el scraper.")
```
