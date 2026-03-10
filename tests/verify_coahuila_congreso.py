import asyncio
from legismex import CoahuilaCongresoClient


def imprimir_iniciativa(init):
    print(f"[{init.fecha}] {init.ponente} ({init.origen})")
    print(f"  > {init.descripcion[:100]}...")
    print(f"  > PDF: {init.url_pdf}")
    print(f"  > DOC: {init.url_abierto}")


def test_sync():
    print("=== Coahuila Congreso (Síncrono) ===")
    client = CoahuilaCongresoClient()
    try:
        iniciativas = client.obtener_iniciativas()
        print(f"Total Encontradas en la primera página: {len(iniciativas)}")
        for e in iniciativas[:3]:  # Imprimir las primeras 3
            imprimir_iniciativa(e)
            print("---")
    except Exception as exc:
        print(f"Error Síncrono: {exc}")


async def test_async():
    print("\n=== Coahuila Congreso (Asíncrono) ===")
    client = CoahuilaCongresoClient()
    try:
        iniciativas = await client.a_obtener_iniciativas()
        print(f"Total Encontradas en la primera página: {len(iniciativas)}")
        for e in iniciativas[:2]:
            imprimir_iniciativa(e)
            print("---")
    except Exception as exc:
        print(f"Error Asíncrono: {exc}")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
