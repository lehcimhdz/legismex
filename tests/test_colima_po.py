import asyncio
from legismex.colima_po import ColimaPoClient


async def test_po_colima_async():
    client = ColimaPoClient()

    # Extraemos el mes de FEBRERO 2026
    ediciones = await client.a_obtener_ediciones_mes(2026, 2)

    print(f"Total Ediciones Recuperadas de manera asíncrona: {len(ediciones)}")
    for e in ediciones[:5]:
        print(f"[{e.fecha}] Portada madre: {e.url_portada}")
        for p in e.documentos:
            print(f"   --> [{p.titulo}]: {p.url_descarga}")

if __name__ == "__main__":
    asyncio.run(test_po_colima_async())
