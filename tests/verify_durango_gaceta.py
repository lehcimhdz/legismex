import asyncio
from legismex import DurangoGacetaClient


async def run_tests():
    print("==================================")
    print("VERIFICANDO DURANGO GACETA")
    print("==================================\n")

    client = DurangoGacetaClient()

    # 1. Obtener Ordinarios
    print("--- 1. Ordinarios ---")
    ordinarios = await client.a_obtener_ordinarios()
    print(f"Total ordinarios recuperados: {len(ordinarios)}")
    if ordinarios:
        primero = ordinarios[0]
        print(f"Primero: {primero.numero} | Fecha: {primero.fecha}")
        print(f"URL PDF: {primero.url_pdf}")
        print(f"Tipo: {primero.tipo}")
    print("\n")

    # 2. Obtener Permanente
    print("--- 2. Comisión Permanente ---")
    permanentes = await client.a_obtener_permanente()
    print(f"Total permanentes recuperados: {len(permanentes)}")
    if permanentes:
        perm = permanentes[0]
        print(f"Primero: {perm.numero} | Fecha: {perm.fecha}")
        print(f"URL PDF: {perm.url_pdf}")
        print(f"Tipo: {perm.tipo}")
    print("\n")

    # 3. Conjuntas
    print("--- 3. Extracción Combinada ---")
    todas = await client.a_obtener_todas()
    print(f"Total combinadas: {len(todas)}")
    print("\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
