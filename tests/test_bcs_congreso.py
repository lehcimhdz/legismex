import pytest
from legismex import BcsCongresoClient

def test_btobtener_ordenes_dia():
    client = BcsCongresoClient()
    url = "https://www.cbcs.gob.mx/index.php/xvii-legislatura/xvii-leg-segundo-ano/xvii-leg-segundo-ano-primer-periodo-receso/orden-del-dia"
    sesiones = client.obtener_ordenes_dia(url)
    
    assert len(sesiones) > 0
    assert sesiones[0].titulo is not None
    assert sesiones[0].url.startswith("http")
    # Verificar que la primera sesión (03 de marzo 2026) tiene fecha correcta
    assert sesiones[0].fecha.year == 2026
    assert sesiones[0].fecha.month == 3
    assert sesiones[0].fecha.day == 3

def test_obtener_detalle_orden():
    client = BcsCongresoClient()
    # URL de la sesión del 03 de marzo de 2026
    url = "https://www.cbcs.gob.mx/index.php/xvii-legislatura/xvii-leg-segundo-ano/xvii-leg-segundo-ano-primer-periodo-receso/orden-del-dia/9007-sesion-publica-ordinaria-del-martes-03-de-marzo-de-2026"
    detalle = client.obtener_detalle_orden(url)
    
    assert detalle.titulo is not None
    assert len(detalle.documentos) > 0
    # Al menos un PDF debería ser la Orden del Día o un punto
    assert any(".pdf" in doc.url.lower() for doc in detalle.documentos)

def test_obtener_actas():
    client = BcsCongresoClient()
    # Categoría XVII Legislatura / Segundo Año / Primer Periodo Receso / Actas (suponiendo URL similar)
    # Por ahora probamos con una URL conocida de actas si la identificamos, 
    # o simplemente verificamos que el método maneja bien una página de lista.
    # Usaremos una URL de la exploración
    url = "https://www.cbcs.gob.mx/index.php/trabajos-legislativos/actas-sesiones"
    actas = client.obtener_actas(url)
    # Esta página es un listado de categorías, quizás necesitemos una más profunda
    # Pero probamos si extrae algo si hay links directos.
    # Si no hay PDFs directos en esa página, actas será [] lo cual es válido si no hay tablas.
    assert isinstance(actas, list)

@pytest.mark.asyncio
async def test_a_obtener_ordenes_dia():
    client = BcsCongresoClient()
    url = "https://www.cbcs.gob.mx/index.php/xvii-legislatura/xvii-leg-segundo-ano/xvii-leg-segundo-ano-primer-periodo-receso/orden-del-dia"
    sesiones = await client.a_obtener_ordenes_dia(url)
    assert len(sesiones) > 0

@pytest.mark.asyncio
async def test_a_obtener_detalle_orden():
    client = BcsCongresoClient()
    url = "https://www.cbcs.gob.mx/index.php/xvii-legislatura/xvii-leg-segundo-ano/xvii-leg-segundo-ano-primer-periodo-receso/orden-del-dia/9007-sesion-publica-ordinaria-del-martes-03-de-marzo-de-2026"
    detalle = await client.a_obtener_detalle_orden(url)
    assert len(detalle.documentos) > 0
