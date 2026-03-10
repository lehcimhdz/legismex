import asyncio
from legismex import TamaulipasClient


def test_sync():
    client = TamaulipasClient()
    print("Obteniendo de forma síncrona la legislatura 66...")
    results = client.obtener_gacetas(66)
    print(f"Total gacetas extruídas: {len(results)}")
    if results:
        print("Ejemplo:", results[0].model_dump())


async def test_async():
    client = TamaulipasClient()
    print("Obteniendo de forma asíncrona la legislatura 65...")
    results = await client.a_obtener_gacetas(65)
    print(f"Total gacetas asíncronas: {len(results)}")
    if results:
        print("Ejemplo:", results[0].model_dump())

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
