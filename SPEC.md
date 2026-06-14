# SPEC: Fix de bugs críticos identificados en auditoría

Documento de seguimiento del set de cambios derivado del análisis del 2026-06-13.
Se prioriza por impacto al usuario final que copia los ejemplos de la doc.

## Bugs a arreglar (en orden de ejecución)

### 1. `docs/excepciones.md` — TypeError en ejemplo de catch
- **Síntoma:** `ZacatecasPoClient.obtener_ediciones()` requiere `fecha_inicial` y `fecha_final`; el ejemplo lo llama sin args.
- **Fix:** pasar fechas válidas en el snippet.

### 2. Excepciones tipadas declaradas pero nunca lanzadas
- **Síntoma:** `legismex.exceptions` define 5 clases (`LegismexError`, `LegismexConnectionError`, `HTMLParsingError`, `APIResponseError`, `DocumentNotFoundError`); ningún client las lanza. `gaceta`, `dof`, `senado` lanzan `raise Exception(...)` genéricos. El bloque `try/except LegismexConnectionError` que la doc recomienda no captura nada.
- **Fix:** envolver `httpx.HTTPStatusError → APIResponseError` y `httpx.RequestError → LegismexConnectionError` en `gaceta/client.py`, `dof/client.py`, `senado/client.py`. Re-exportar las excepciones desde `legismex/__init__.py` para `from legismex import LegismexConnectionError`.

### 3. `VeracruzPoClient` — leak + typo
- **Síntoma:** `__init__` abre `self._sync_client = httpx.Client(...)` que nunca se cierra; `_async_client` se inicializa de forma inconsistente; método público se llama `aobtener_ediciones` (falta `_`). Error message contiene typo `aostener_ediciones`.
- **Fix:** refactor a patrón per-request (`with httpx.Client(**self.client_kwargs)`), método canónico `a_obtener_ediciones`, alias `aobtener_ediciones = a_obtener_ediciones` para backward-compat. Eliminar `close()`, `use_async`, `_sync_client`, `_async_client`. Aceptar y descartar `use_async` vía `**kwargs` para no romper constructores existentes.

### 4. `TlaxcalaPoClient._SLUG_MAP` — código muerto
- **Síntoma:** `_SLUG_MAP = {2026: "2025-2", 2025: "2025"}` definido top-level pero `_index_url(anio)` lo ignora y devuelve `f"{INDEX_BASE}/{anio}.php"`. Para 2026 se pedirá `/indices/2026.php` que el portal no expone (Joomla agrupa el año actual en `2025-2.php`).
- **Fix:** `_index_url` debe consultar `_SLUG_MAP.get(anio, str(anio))`.

### 5. `gaceta/parser.py` — shadow del builtin `abs`
- **Síntoma:** líneas 85 y 98 reasignan `abs = None` y `abs = int(...)` dentro de `parse_votaciones_detalle`. Funciona porque no hay `abs(x)` después, pero contamina el scope y es ruido para los linters.
- **Fix:** renombrar a `abstenc`.

### 6. `EdomexClient` / `EdomexPoClient` — parámetros del constructor ignorados
- **Síntoma:** ambos declaran `verify_ssl: bool = False, timeout: float = 30.0` pero hardcodean `timeout=30.0, verify=False` al construir `httpx.Client`.
- **Fix:** usar los valores recibidos. Aprovechar para migrar a per-request (no hay session reuse legítimo).

### 7. Clientes persistentes sin close — fuga de sockets
- **Síntoma:** `CdmxClient.session`, `JaliscoClient.client`, `EdomexClient.client`, `EdomexPoClient.client` se abren en `__init__` y nunca cierran. Contradice la convención del proyecto declarada en CLAUDE.md.
- **Fix:** convertir todos a per-request `with httpx.Client(...)`. Para Jalisco, el método N+1 abre un único `Client` en el outer scope.

### 8. Re-exports faltantes
- **Síntoma:** modelos públicos de Gaceta (`Iniciativa`, `Dictamen`, `BaseDictamenes`, `DocumentoGaceta`, `Proposicion`) y Senado (`GacetaSenado`, `ReferenciaGaceta`, `DocumentoSenado`) están documentados pero no se exponen desde `legismex/__init__.py` ni desde sus subpaquetes.
- **Fix:** añadir los imports a `legismex/__init__.py`, `gaceta/__init__.py` y `senado/__init__.py` con sus respectivos `__all__`.

## Out of scope (no críticos)

- Rename `tamaño_pagina → tamano_pagina` en Aguascalientes: rompería el verify y dos secciones del tutorial; el código funciona.
- Tests sin asserts reales (`test_*.py` que solo imprimen): refactor grande, riesgo de regresión, no es bug.
- README repeticiones de "Veracruz" y "Gaceta Parlamentaria de Gaceta Parlamentaria": cosmético.
- TUTORIAL faltan secciones para Yucatán/Chihuahua/Coahuila/BC PO/BCS PO/Aguascalientes PO: feature gap, no bug.
- `mkdocs.yml` mojibake en nav: cosmético en una página específica.
- CI ruff vs flake8, smoke test que no corre pytest: cambio de infra, otro PR.

## Validación

Tras cada bloque de cambios:
1. `python3 -c "import sys; sys.path.insert(0, 'src'); import legismex; print('OK')"` para asegurar que el paquete sigue importando.
2. Smoke check de las clases tocadas vía import + introspección.
3. Diff manual para verificar que no se borró comportamiento.
