import asyncio
from legismex.tabasco_po import TabascoPoClient


def test_sync():
    print("Iniciando prueba SÍNCRONA para Periódico Oficial de Tabasco...")
    client = TabascoPoClient()

    # Obtener 2 páginas de resultados generales
    publicaciones = client.obtener_publicaciones(paginas=2)
    print(f"Total publicaciones obtenidas (2 páginas): {len(publicaciones)}")

    for pub in publicaciones[:3]:
        print(
            f"[{pub.fecha}] Núm: {pub.numero} | Tipo: {pub.tipo} | Suplemento: {pub.suplemento}")
        print(f"Desc: {pub.descripcion[:100]}...")
        print(f"PDF: {pub.url_pdf}\n")


async def test_async():
    print("Iniciando prueba ASÍNCRONA para Periódico Oficial de Tabasco (Búsqueda '2025')...")
    client = TabascoPoClient()

    # Buscar "2025" y obtener 1 página
    publicaciones = await client.a_obtener_publicaciones(busqueda="2025", paginas=1)
    print(
        f"Total publicaciones obtenidas para '2025' (1 página): {len(publicaciones)}")

    for pub in publicaciones[:3]:
        print(f"[{pub.fecha}] Núm: {pub.numero} | Tipo: {pub.tipo}")
        print(f"PDF: {pub.url_pdf}\n")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
