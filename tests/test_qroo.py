import asyncio
from legismex.qroo import QrooClient


def test_sync():
    print("Iniciando prueba SÍNCRONA para Quintana Roo...")
    client = QrooClient()

    gacetas = client.obtener_gacetas(anio=2026, mes=3)
    print(f"Gacetas obtenidas en marzo 2026: {len(gacetas)}")

    for g in gacetas:
        print(f"\n[{g.fecha_publicacion}] Gaceta #{g.id_gaceta} - {g.titulo}")
        print(f"Documentos anexos obtenidos: {len(g.documentos)}")
        for d in g.documentos[:2]:
            print(f"  - ({d.tipo_doc}) {d.titulo}")
            print(f"    {d.url}")


async def test_async():
    print("\nIniciando prueba ASÍNCRONA para Quintana Roo...")
    client = QrooClient()

    gacetas = await client.a_obtener_gacetas(anio=2026, mes=2)
    print(f"Gacetas obtenidas en feb 2026: {len(gacetas)}")
    if gacetas:
        g = gacetas[-1]
        print(f"Última registrada: [{g.fecha_publicacion}] {g.titulo}")
        print(f"Total documentos: {len(g.documentos)}")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
