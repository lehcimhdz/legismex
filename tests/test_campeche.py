import asyncio
from legismex.campeche import CampecheClient


def test_sync():
    print("Iniciando prueba SÍNCRONA para Campeche...")
    client = CampecheClient()

    gacetas = client.obtener_gacetas()
    print(f"Total gacetas obtenidas (todas las legislaturas): {len(gacetas)}")

    legislaturas = {}
    for g in gacetas:
        legislaturas[g.legislatura] = legislaturas.get(g.legislatura, 0) + 1

    print("\nConteo por Legislatura:")
    for leg, count in legislaturas.items():
        print(f"  - {leg}: {count}")

    print("\nEjemplos:")
    for gaceta in gacetas[:3]:
        print(f"[{gaceta.legislatura}] {gaceta.titulo} -> {gaceta.url_pdf}")


async def test_async():
    print("\nIniciando prueba ASÍNCRONA para Campeche...")
    client = CampecheClient()

    gacetas = await client.a_obtener_gacetas()
    print(f"Total gacetas obtenidas de manera asíncrona: {len(gacetas)}")
    if gacetas:
        print(
            f"Última registrada: [{gacetas[-1].legislatura}] {gacetas[-1].titulo}")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
