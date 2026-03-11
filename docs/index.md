# Bienvenido a Legismex 🇲🇽

**Legismex** es la biblioteca definitiva en Python para minar, estructurar y analizar datos legales y resoluciones del gobierno extraídas de los 32 estados de México, el Senado de la República, la Cámara de Diputados y el Diario Oficial de la Federación.

## Motivación

Los sistemas oficiales sufren de asimetría de información y obsolescencia técnica: sistemas en Visual Basic de 1999, barreras de Cloudflare, portales protegidos con JavaScript ofuscado, o simplemente archivos caídos por falta de certificados SSL. 

Legismex unifica estas interfaces caóticas en modelos `Pydantic` estrictamente tipados.

## Instalación

Puedes instalar la librería e integrarla a tu proyecto de Ciencia de Datos o de Análisis Político velozmente.

```bash
pip install legismex
```

*Nota: Para extraer documentos protegidos por el gobierno de la CDMX y Puebla:*
```bash
pip install "legismex[consejeria]"
playwright install chromium
```

## 🦅 Soporte Multi-Cámara e Institucional

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
*   🏝️ **Quintana Roo** (Gaceta Parlamentaria `qroo` y Periódico Oficial `qroo_po`)
*   🌵 **San Luis Potosí** (Congreso `sanluis` y Periódico Oficial `sanluis_po`)
*   🌴 **Colima** (Gaceta Parlamentaria `colima` y Periódico Oficial `colima_po`)
*   🍫 **Tabasco** (Congreso Iniciativas `tabasco_iniciativas` y Periódico Oficial `tabasco_po`)
*   🌺 **Tamaulipas** (Congreso `tamaulipas` y Periódico Oficial `tamaulipas_po`)
*   🌴 **Veracruz** (Congreso `veracruz` y Periódico Oficial `veracruz_po`)
*   🌊 **Nayarit** (Congreso Iniciativas `nayarit_congreso` y Periódico Oficial `nayarit_po`)
*   🌊 **Sinaloa** (Congreso `sinaloa` y Periódico Oficial `sinaloa_po`)
*   🌊 **Baja California Sur**: Congreso del Estado (`bcs_congreso`)
*   🌵 **Baja California**: Congreso del Estado (`bc_congreso`) y Periódico Oficial (`bc_po`)
*   🌴 **Yucatán**: Congreso del Estado (`yucatan_congreso`) y Periódico Oficial (`yucatan_po`)
*   🐶 **Chihuahua**: Congreso del Estado (`chihuahua_congreso`) y Periódico Oficial (`chihuahua_po`)
*   🦖 **Coahuila**: Congreso del Estado (`coahuila_congreso`) y Periódico Oficial (`coahuila_po`)
*   🌵 **Sonora**: Gaceta Parlamentaria `sonora` y Periódico Oficial `sonora_po`
*   🐸 **Guanajuato**: Gaceta Parlamentaria y Periódico Oficial del Estado
*   🦋 **Michoacán**: Gaceta Parlamentaria y Periódico Oficial del Estado
*   🌲 **Durango**: Congreso del Estado (`durango_gaceta`) y Periódico Oficial (`durango_po`)
*   🌋 **Morelos**: Documentos Legislativos del Congreso y Periódico Oficial
*   🌴 **Guerrero**: Gaceta Parlamentaria del Congreso y Periódico Oficial
*   🌋 **Tlaxcala**: Trabajo Legislativo del Congreso LXV y Periódico Oficial
*   🏛️ **Oaxaca**: Gaceta Parlamentaria del Congreso y Periódico Oficial
*   🌵 **Aguascalientes**: Agenda Legislativa del Congreso y Periódico Oficial
*   🏺 **Campeche**: Gaceta Parlamentaria y Periódico Oficial
*   🐆 **Chiapas**: Gaceta Parlamentaria y Periódico Oficial
*   🏛️ **Hidalgo**: Congreso del Estado y Periódico Oficial
*   **Zacatecas:** Congreso del Estado y Periódico Oficial

### 🛠️ Capacidades de Extracción
*   **Votaciones Detalladas:** Analiza el concentrado por periodo y extrae la votación particular de cada dictamen, incluyendo sumatorias de votos.
*   **Motores de Búsqueda (HTDIG):** Conexión directa a buscadores internos para localizar iniciativas, proposiciones y dictámenes.
*   **Iniciativas y Seguimiento:** Obtiene el estatus de trámite, promotores y links directos (PDF/HTML) de asuntos en comisiones.

Revisa el [Tutorial Oficial](tutorial.md) para ver ejemplos de código para cada uno de estos estados.
