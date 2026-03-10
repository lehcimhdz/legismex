import asyncio
from legismex import ChiapasGacetaClient


async def run_tests():
    print("=========================================")
    print("VERIFICANDO GACETA DE CHIAPAS")
    print("=========================================\n")

    client = ChiapasGacetaClient()

    print("--- 1. Obtener Gacetas ---")
    gacetas = await client.a_obtener_gacetas()
    print(f"Total gacetas recuperadas: {len(gacetas)}")

    for idx, e in enumerate(gacetas[:5]):
        print(f"Edición {idx+1}:")
        print(f"  Número: {e.numero}")
        print(f"  Año: {e.anio}")
        print(f"  Título: {e.titulo}")
        print(f"  Periodo: {e.periodo}")
        print(f"  Flipbook: {e.url_flipbook}")
        print(f"  PDF: {e.url_pdf}")
        print("")

if __name__ == "__main__":
    asyncio.run(run_tests())
