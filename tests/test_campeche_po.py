import asyncio
from legismex.campeche_po import CampechePoClient


def test_sync():
    print("Iniciando prueba SÍNCRONA para Campeche PO...")
    client = CampechePoClient()

    pubs = client.obtener_publicaciones(anio=2026, paginas=1)
    print(f"Total publicaciones obtenidas: {len(pubs)}")
    print("\nEjemplos:")
    for pub in pubs[:3]:
        print(f"[{pub.fecha}] {pub.titulo} -> {pub.url_pdf}")


async def test_async():
    print("\nIniciando prueba ASÍNCRONA para Campeche PO...")
    client = CampechePoClient()

    pubs = await client.a_obtener_publicaciones(anio=2025, paginas=3)
    print(f"Total publicaciones obtenidas (3 páginas): {len(pubs)}")
    if pubs:
        print(
            f"Última registrada: [{pubs[-1].fecha}] {pubs[-1].titulo} -> {pubs[-1].url_pdf}")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
