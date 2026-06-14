# Changelog

All notable changes to this project are documented in this file. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Public typed exception hierarchy is now exported from the package root: `LegismexError`, `LegismexConnectionError`, `HTMLParsingError`, `APIResponseError`, `DocumentNotFoundError`.
- New `wrap_httpx_errors(url=None)` context manager that maps `httpx.HTTPStatusError` to `APIResponseError` and any `httpx.RequestError` (timeout, SSL, DNS, etc.) to `LegismexConnectionError`, preserving the original via `__cause__`. Covered by `tests/test_exceptions_wrap.py`.

### Changed
- Federal clients (`GacetaClient`, `SenadoClient`, `DofClient`) and the recently refactored state clients (`CdmxClient`, `JaliscoClient`, `EdomexClient`, `VeracruzPoClient`) now raise typed `legismex` exceptions instead of bare `Exception` / raw `httpx` errors. `CdmxClient.descargar_pdf` keeps its "soft failure → returns None" contract, but now catches the typed exceptions.
- `GacetaClient` gains a shared `_post` helper to match `_get`, so every request path goes through the typed-error wrapper.
- `CdmxClient` constructor now accepts `verify_ssl` and `timeout`; `JaliscoClient` constructor now accepts `timeout`.

### Fixed
- `CdmxClient` and `JaliscoClient` no longer hold a persistent `httpx.Client` instance attribute that leaked when callers never explicitly closed it. The client is opened per request (Jalisco keeps a single client open for the whole eventos cascade).
- `daily-monitor` workflow now awaits the `issues.create()` call and uses only the `bug` label, which exists by default. The previous configuration could finish without filing the alert.

## [1.0.7] — 2026-03

Coverage now spans all 32 Mexican states (Congreso + Periódico Oficial), the Federal Senate, the Cámara de Diputados, the DOF, and the Consejería Jurídica de la CDMX (via headless Playwright).

### Added
- State coverage waves rolled out across the project:
  - Northern/western states: Baja California, BCS, Sonora, Sinaloa, Durango, Zacatecas, Aguascalientes, Jalisco, Colima, Nayarit, Nuevo León, Tamaulipas, Chihuahua, Coahuila, San Luis Potosí.
  - Central states: Estado de México, Morelos, Puebla, Tlaxcala, Hidalgo, Guerrero, Oaxaca, Querétaro, Guanajuato, Michoacán.
  - Southeastern states: Chiapas, Veracruz, Tabasco, Campeche, Quintana Roo, Yucatán.
- Federal coverage: DOF, Cámara de Diputados (gaceta + votaciones + iniciativas), Senado.
- HTDIG search-engine integration for legislative initiatives.
- Detailed vote breakdowns per period and ruling.
- Playwright-based bypass for the Consejería de la CDMX ZK Framework obfuscation.

### Infrastructure
- PyPI publish workflow.
- mkdocs documentation site.
- Strict pydantic v2 models per source.
- 87+ test files covering scrapers, HTTP utilities, and models.
- Pre-commit hooks (ruff).
- `daily-monitor` GitHub Action that auto-files an alert issue if any scraper breaks.
