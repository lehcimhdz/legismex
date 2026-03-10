import asyncio
from legismex import ChihuahuaPoClient


def imprimir_edicion(e):
    print(f"[{e.fecha_iso}] {e.titulo}")
    print(f"  > Fecha legible: {e.fecha_legible}")
    if e.url_ejemplar:
        print(f"  > Ejemplar principal: {e.url_ejemplar}")
    if e.url_anexos:
        print(f"  > Anexos detectados: {len(e.url_anexos)}")
        for url in e.url_anexos:
            print(f"      - {url}")


def test_sync():
    print("=== Periódico Oficial de Chihuahua Síncrono (Pág 0, keyword: 'Especial') ===")
    client = ChihuahuaPoClient()
    try:
        ediciones = client.obtener_ediciones(texto="Especial", pagina=0)
        print(f"Total Encontradas en la pág. 0: {len(ediciones)}")
        for e in ediciones[:2]:  # Imprimir las primeras 2
            imprimir_edicion(e)
            print("---")
    except Exception as exc:
        print(f"Error Síncrono: {exc}")


async def test_async():
    print("\n=== Periódico Oficial de Chihuahua Asíncrono (Pág 1) ===")
    client = ChihuahuaPoClient()
    try:
        ediciones = await client.a_obtener_ediciones(pagina=1)
        print(f"Total Encontradas en la pág. 1: {len(ediciones)}")
        for e in ediciones[:1]:
            imprimir_edicion(e)
    except Exception as exc:
        print(f"Error Asíncrono: {exc}")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
