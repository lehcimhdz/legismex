# Bienvenido a Legismex 🇲🇽

**Legismex** es la biblioteca definitiva en Python para minar, estructurar y analizar datos legales y resoluciones del gobierno extraídas de los 32 estados de México, el Senado de la República, la Cámara de Diputados y el Diario Oficial de la Federación.

## Motivación

Los sistemas oficiales sufren de asimetría de información y obsolescencia técnica: sistemas en Visual Basic de 1999, barreras de Cloudflare, portales protegidos con JavaScript ofuscado, o simplemente archivos caídos por falta de certificados SSL. 

Legismex unifica estas interfaces caóticas en modelos `Pydantic` estrictamente tipados.

## Instalación

Puedes instalar la librería e integrarla a tu proyecto de Ciencia de Datos o de Análisis Político velozmente.

```bash
pip install git+https://github.com/lehcimhdz/legismex.git
```

*Nota: Para extraer documentos protegidos por el gobierno de la CDMX y Puebla:*
```bash
pip install "legismex[consejeria]  @ git+https://github.com/lehcimhdz/legismex.git"
playwright install chromium
```

## Prácticamente Soporte Total 🦅

Ya sea que necesites compilar *Iniciativas de Ley* en Nuevo León, descargar Gacetas ocultas de la CDMX o mapear resoluciones judiciales en Michoacán, tenemos conectores dedicados.

Revisa el [Tutorial Oficial](tutorial.md) para ejemplos de código.
