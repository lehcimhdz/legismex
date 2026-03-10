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
*   **Quintana Roo** (Gaceta Parlamentaria `qroo` y Periódico Oficial `qroo_po`)
*   **San Luis Potosí** (Congreso `sanluis` y Periódico Oficial `sanluis_po`)
*   **Colima** (Gaceta Parlamentaria `colima` y Periódico Oficial `colima_po`)
*   **Tabasco** (Congreso Iniciativas `tabasco_iniciativas` y Periódico Oficial `tabasco_po`)
*   **Tamaulipas** (Congreso `tamaulipas` y Periódico Oficial `tamaulipas_po`)
*   **Veracruz** (Congreso `veracruz`)
*   🌊 **Nayarit** (Congreso Iniciativas `nayarit_congreso` y Periódico Oficial `nayarit_po` — API REST interna, 3 tipos de búsqueda)
*   🌊 **Sinaloa** (Congreso `sinaloa` — Iniciativas, Dictámenes, Acuerdos y Decretos vía API REST, legislaturas LX–LXV; Periódico Oficial `sinaloa_po` — ediciones ordinarias y vespertinas con PDF directo)
*   🌊 **Baja California Sur**: Congreso del Estado (`bcs_congreso`) — Extracción de Órdenes del Día, Actas y Diario de los Debates (XVII Legislatura).
*   🌵 **Baja California**: 
    *   Congreso del Estado (`bc_congreso`) — Extracción de iniciativas, posicionamientos y recolección de URLs de PDF con navegación de ASP.NET.
    *   Periódico Oficial del Estado (`bc_po`) — Consultas integradas para POES mensual y descargas desde CDN.
*   🌴 **Yucatán**:
    *   Congreso del Estado (`yucatan_congreso`) — Scraper con simulación de navegación TLS para evadir bloqueos, tabla de Iniciativas completas con anexos.
    *   Periódico Oficial del Estado (`yucatan_po`) — Extrae las ediciones publicadas en una fecha dada junto a sus sumarios.
*   🐶 **Chihuahua**: 
    *   Congreso del Estado (`chihuahua_congreso`) — Extrae las Sesiones publicadas en la Gaceta Parlamentaria con soporte a paginado, agrupamiento de documentos por fase de sesión (probables, desahogados, votación y turnados) y ligas de YouTube.
    *   Periódico Oficial del Estado (`chihuahua_po`) — Extrae las emisiones del PO con filtrado de fechas, palabras clave y anexos aledaños en formato de PDF expuestos de forma directa.
*   🦖 **Coahuila**: 
    *   Congreso del Estado (`coahuila_congreso`) — Extrae el listado de Iniciativas de la Legislatura actual almacenadas en la base de datos de PrimeFaces.
    *   Periódico Oficial del Estado (`coahuila_po`) — Extrae e indexa las ediciones y anexos publicados en un año específico con URLs directas de sus repositorios escondidos.
*   🌵 **Sonora**: Gaceta Parlamentaria `sonora` (REST API, 7 legislaturas) y Periódico Oficial `sonora_po` (Joomla Scraping, archivo 1981–2026).
*   🐸 **Guanajuato**: Gaceta Parlamentaria del Congreso del Estado
*   🐸 **Guanajuato**: Periódico Oficial del Estado
*   🦋 **Michoacán**: Gaceta Parlamentaria del Congreso del Estado
*   🦋 **Michoacán**: Periódico Oficial del Estado (archivo 1955–2025)
*   🌲 **Durango**:
    *   Congreso del Estado (`durango_gaceta`) — Gacetas ordinarias y de la Comisión Permanente.
    *   Periódico Oficial del Estado (`durango_po`) — Ediciones publicadas alojadas en AWS S3.
*   🌋 **Morelos**: Documentos Legislativos del Congreso (LVI Legislatura)
*   🌋 **Morelos**: Periódico Oficial del Estado (archivo 1970–2026, 6,400+ ejemplares)
*   🌴 **Guerrero**: Gaceta Parlamentaria del Congreso (LXIV Legislatura, 185+ gacetas)
*   🌴 **Guerrero**: Periódico Oficial del Estado (30 categorías, desde 1987)
*   🌋 **Tlaxcala**: Trabajo Legislativo del Congreso LXV (Decretos, Iniciativas, Acuerdos, Dictámenes, y 8 categorías más, 2024–2026)
*   🌋 **Tlaxcala**: Periódico Oficial del Estado (1000+ registros/año, desde 2011)
*   🏛️ **Oaxaca**: Gaceta Parlamentaria del Congreso LXVI (179+ sesiones, PDFs por punto del orden del día)
*   🏛️ **Oaxaca**: Periódico Oficial del Gobierno del Estado (12,000+ ediciones desde 2010 — Ordinario, Extraordinario, Secciones)
*   🌵 **Aguascalientes**: Agenda Legislativa del Congreso LXVI/LXV/LXIV (1,861+ promociones — 14 tipos: Iniciativas, Decretos, Gaceta Parlamentaria, Actas y más)
*   🌵 **Aguascalientes**: Periódico Oficial del Estado (8,991+ ediciones desde los 90s — Ordinario, Extraordinario, Vespertina — con calendario de 5,458 fechas)
*   🌵 **Baja California**: Periódico Oficial del Estado
*   🌵 **San Luis Potosí**: Gaceta Parlamentaria del Congreso del Estado (Sesiones Ordinarias y Extraordinarias desde la LXII Legislatura, un solo request)
*   🌵 **San Luis Potosí**: Periódico Oficial del Estado (Consumo directo de la API JSON de VueJS mapeando Disposiciones y Avisos Judiciales)
*   🌴 **Veracruz**: Gaceta Legislativa del Congreso del Estado (Extracción anidada de sesiones, periodos, anexos, actas, audios y videos en un solo compilado)
*   🌴 **Veracruz**: Periódico Oficial del Estado (Traducción de requests de formulario a extracción en masa de gacetas anuales con tomos vinculados)
*   🌺 **Tamaulipas**: Gaceta Parlamentaria del Congreso (Obtiene en volumen el registro íntegro de la legislatura vigente extraído de tabla HTML).
*   🌺 **Tamaulipas**: Periódico Oficial del Estado (Raspa el calendario en formato WordPress recuperando enlaces de Ediciones Vespertinas/Legislativas/Judiciales por mes).
*   🏛️ **Veracruz**: Sesiones del Congreso (Transita el listado en formato tabla, obteniendo enlaces relativos de actas, diario de los debates, audios, síntesis y el orden del día de las asambleas).
*   🏺 **Campeche**: Gaceta Parlamentaria (Procesa el histórico simultáneo global de legislaturas extrayendo más de 800 gacetas en una petición estática basada en pestañas).
*   🏺 **Campeche**: Periódico Oficial del Estado (Lee y pagina el listado HTML de la biblioteca virtual del SIPOEC, infiriendo velozmente la URL de descarga local del PDF a partir del título y fecha sin consultar el API de expedición).
*   🌊 **San Luis Potosí**: Gaceta Parlamentaria (Procesa el histórico simultáneo global de legislaturas renderizado estáticamente desde posts-table-pro usando BeautifulSoup in-memory).
*   🐆 **Chiapas**: Gaceta Parlamentaria (Obtiene de un solo golpe todas las publicaciones de periodos ordinarios y permanentes enviando el payload HTTP correspondiente a su API AJAX oculta).
*   🐆 **Chiapas**: Periódico Oficial del Estado (Extrae masivamente publicaciones abarcando décadas usando los endpoints del sexenio y parseando la paginación de respuestas).
*   🍫 **Tabasco**: Gaceta Parlamentaria (Procesa el histórico simultáneo global renderizado estáticamente desde posts-table-pro usando BeautifulSoup in-memory).
*   🏝️ **Quintana Roo**: Gaceta Parlamentaria (Integración masiva a la API REST subyacente de su SPA Nuxt.js extrayendo metadatos y documentos concatenados saltando el parseo de HTML).
*   🏝️ **Quintana Roo**: Periódico Oficial del Estado (Extrae masivamente publicaciones mediante rangos interpolados de principio a fin del mes dado resolviendo peticiones de GET iterativas asíncronas).
*   🍫 **Tabasco**: Periódico Oficial del Estado (Extractor paginado que permite búsquedas por término y año mediante una redirección GET simplificada).
*   **Congreso de Jalisco:** Extrae el calendario de eventos y desgrana las agendas y subpuntos con documentos adjuntos iterando sobre la estructura interna de la Gaceta Parlamentaria.
*   **Congreso de Nuevo León:** Convierte la base de datos DataTables de iniciativas a objetos analíticamente procesables al vuelo.
*   **Periódico Oficial de Nuevo León:** Omite barreras de firewall y parsea la vista ASP.NET empaquetando los enlaces PDF esparcidos.
*   **Gaceta Parlamentaria de Gaceta Parlamentaria:** Obtiene el listado completo (histórico) de gacetas parlamentarias extrayendo fechas limpias y enlaces a PDFs originales.
*   **Congreso de Hidalgo:** Extrae sesiones y sus documentos asociados (órdenes del día, actas, diarios de debates) filtrando por año, mes y tipo.
*   **Periódico Oficial de Hidalgo:** Sistema de búsqueda avanzada que extrae sumarios detallados y construye enlaces directos a los archivos PDF institucionales.
*   **Congreso de Zacatecas:** Consulta la Gaceta Parlamentaria (LXV Legislatura) permitiendo listar y descargar ediciones por mes (formato MMYYYY).
*   **Periódico Oficial de Zacatecas:** Plataforma unificada que permite descargar ediciones ordinarias por rango de fechas, además de extraer ágilmente suplementos, leyes, códigos y reglamentos vigentes desde sus endpoints JSON nativos.
*   **Periódico Oficial de Sonora:** Scraping y mapeo de años a Joomla SP Builder (1981-2026).
*   **Periódico Oficial de Zacatecas:** Interfaz con Parse API y descargas resolviendo ID del objeto con redirecciones dinámicas a PDFS.
*   **Periódico Oficial de Durango:** API híbrida asíncrona validando Next.js server payload y extracción en profundidad de links nativos (Amazon S3).
*   **Congreso de Durango (Gaceta):** Extracción desde un CMS basado en WordPress (TablePress) extrayendo publicaciones de la Comisión Permanente y del Periodo Ordinario empaquetando URLs directas al PDF de cada edición.
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

## 📖 Uso Detallado (API)

Debido a la extensa cobertura de **legismex** (soportando a los 32 estados, el Senado y el DOF), hemos movido la documentación completa con ejemplos de código para cada módulo al archivo oficial de tutorial.

Por favor consulta el archivo **[👉 TUTORIAL.md](TUTORIAL.md)**.

Ahí encontrarás cómo buscar votaciones, iniciativas, gacetas, y periódicos oficiales estado por estado, además de instrucciones para manejar descargas masivas o sortear bloqueos de seguridad institucionales.

## 🤝 Contribuir

Si deseas agregar un nuevo estado o mejorar uno existente, nuestra comunidad es vital para abarcar toda la geografía mexicana.

Revisa nuestra guía de contribución en **[CONTRIBUTING.md](CONTRIBUTING.md)** para conocer las convenciones de estructuración y código.

