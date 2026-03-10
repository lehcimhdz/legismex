import asyncio
from legismex import CoahuilaPoClient

def imprimir_edicion(edicion):
    print(f"[{edicion.fecha_publicacion}] Tomo {edicion.tomo} | {edicion.tipo} - No.{edicion.numero}")
    print(f"  > ID Sumario: {edicion.id_sumario}")
    print(f"  > Sumario: {edicion.sumario[:100]}...")
    print(f"  > PDF: {edicion.url_pdf}")

def test_sync():
    print("=== Coahuila P.O. (Síncrono) ===")
    client = CoahuilaPoClient()
    try:
        ediciones = client.obtener_ediciones(anio=2026)
        print(f"Total Encontradas: {len(ediciones)}")
        for e in ediciones[:3]: # Imprimir solo 3
            imprimir_edicion(e)
            print("---")
    except Exception as exc:
        print(f"Error Síncrono: {exc}")

async def test_async():
    print("\n=== Coahuila P.O. (Asíncrono) ===")
    client = CoahuilaPoClient()
    try:
        ediciones = await client.a_obtener_ediciones(anio=2025)
        print(f"Total Encontradas [2025]: {len(ediciones)}")
        for e in ediciones[:2]:
            imprimir_edicion(e)
            print("---")
    except Exception as exc:
        print(f"Error Asíncrono: {exc}")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
