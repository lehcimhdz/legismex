import asyncio
from legismex import BcsPoClient


def test_sync():
    print("=== Obteniendo ediciones BCS PO Síncrono (2025) ===")
    client = BcsPoClient()
    try:
        ediciones = client.obtener_ediciones(2025)
        print(f"Total de ediciones encontradas: {len(ediciones)}")
        for e in ediciones[:5]:
            print(f"- {e.numero} ({e.fecha}): {e.url_pdf}")
    except Exception as e:
        print(f"Error en síncrono: {e}")


async def test_async():
    print("\n=== Obteniendo ediciones BCS PO Asíncrono (2024) ===")
    client = BcsPoClient()
    try:
        ediciones = await client.a_obtener_ediciones(2024)
        print(f"Total de ediciones encontradas: {len(ediciones)}")
        for e in ediciones[:5]:
            print(f"- {e.numero} ({e.fecha}): {e.url_pdf}")
    except Exception as e:
        print(f"Error en asíncrono: {e}")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
