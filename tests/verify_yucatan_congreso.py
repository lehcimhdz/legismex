import asyncio
from legismex import YucatanCongresoClient

def test_sync():
    print("=== Obteniendo Iniciativas Yucatán (Síncrono) ===")
    client = YucatanCongresoClient()
    try:
        iniciativas = client.obtener_iniciativas()
        print(f"Total de iniciativas encontradas: {len(iniciativas)}")
        for i in iniciativas[:3]:
            print(f"- {i.legislatura} | {i.fecha_presentada} | {i.descripcion}")
            for doc in i.documentos:
                print(f"   -> Documento ({doc.extension}): {doc.url}")
    except Exception as e:
        print(f"Error en síncrono: {e}")

async def test_async():
    print("\n=== Obteniendo Iniciativas Yucatán (Asíncrono) ===")
    client = YucatanCongresoClient()
    try:
        iniciativas = await client.a_obtener_iniciativas()
        print(f"Total de iniciativas encontradas: {len(iniciativas)}")
    except Exception as e:
        print(f"Error en asíncrono: {e}")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
