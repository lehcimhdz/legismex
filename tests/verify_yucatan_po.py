import asyncio
from legismex import YucatanPoClient

def test_sync():
    print("=== Yucatán PO Síncrono (09/03/2026) ===")
    client = YucatanPoClient()
    try:
        ediciones = client.obtener_ediciones_por_fecha("2026-03-09")
        print(f"Total Encontradas: {len(ediciones)}")
        for e in ediciones:
            print(f"- {e.tipo} ({e.fecha}) Num. {e.numero}")
            print(f"  URL: {e.url_pdf}")
            # print(f"  Sumario: {e.sumario[:80]}...")
    except Exception as exc:
        print(f"Error Síncrono: {exc}")

async def test_async():
    print("\n=== Yucatán PO Asíncrono (09/03/2026) ===")
    client = YucatanPoClient()
    try:
        ediciones = await client.a_obtener_ediciones_por_fecha("2026-03-09")
        print(f"Total Encontradas: {len(ediciones)}")
        for e in ediciones:
            print(f"- {e.tipo} ({e.fecha}) Num. {e.numero}")
    except Exception as exc:
        print(f"Error Asíncrono: {exc}")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
