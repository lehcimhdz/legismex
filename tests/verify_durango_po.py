import asyncio
from legismex import DurangoPoClient

async def run_tests():
    print("=========================================")
    print("VERIFICANDO PERIÓDICO OFICIAL DE DURANGO")
    print("=========================================\n")

    client = DurangoPoClient()

    print("--- 1. Obtener Ediciones Pagina 1 ---")
    ediciones = await client.a_obtener_ediciones(pagina=1)
    print(f"Total ediciones recuperadas: {len(ediciones)}")
    
    for idx, e in enumerate(ediciones[:3]):
        print(f"Edición {idx+1}:")
        print(f"  Título: {e.titulo}")
        print(f"  Fecha: {e.fecha}")
        print(f"  UUID: {e.uuid[:8]}...")
        print(f"  PDF: {e.url_pdf}")
        print(f"  Pubs: {e.cantidad_publicaciones}")
        print("")

if __name__ == "__main__":
    asyncio.run(run_tests())
