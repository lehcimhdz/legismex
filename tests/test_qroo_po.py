import asyncio
from legismex.qroo_po import QrooPoClient


def test_sync():
    print("Iniciando prueba SÍNCRONA para Quintana Roo PO...")
    client = QrooPoClient()

    # Probando Febrero 2026 que sabemos que paginaba en el script original (24 resultados)
    pubs = client.obtener_publicaciones(anio=2026, mes=2)
    print(f"Publicaciones obtenidas en Feb 2026: {len(pubs)}")

    for pub in pubs[:3]:
        print(f"[{pub.fecha}] {pub.tipo} Num. {pub.numero} Tomo {pub.tomo}")
        print(f"  Url: {pub.url_pdf}")


async def test_async():
    print("\nIniciando prueba ASÍNCRONA para Quintana Roo PO...")
    client = QrooPoClient()

    pubs = await client.a_obtener_publicaciones(anio=2026, mes=1)
    print(f"Publicaciones obtenidas en Enero 2026: {len(pubs)}")

    if pubs:
        print(
            f"[{pubs[0].fecha}] {pubs[0].tipo} Num. {pubs[0].numero} Tomo {pubs[0].tomo}")
        print(f"  Url: {pubs[0].url_pdf}")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
