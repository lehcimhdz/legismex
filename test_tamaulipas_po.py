import asyncio
from legismex import TamaulipasPoClient

def run_sync():
    client = TamaulipasPoClient()
    print("Consultando el Periódico Oficial de Tamaulipas (Marzo 2026)")
    ediciones = client.obtener_ediciones(2026, 3)
    
    print(f"Total de ediciones síncronas encontradas: {len(ediciones)}")
    for ed in ediciones[:3]:
        print(ed.model_dump())

async def run_async():
    client = TamaulipasPoClient()
    ediciones = await client.a_obtener_ediciones(2026, 3)
    print(f"Total de ediciones asíncronas encontradas: {len(ediciones)}")

if __name__ == "__main__":
    run_sync()
    asyncio.run(run_async())
