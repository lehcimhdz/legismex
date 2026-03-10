import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from legismex import BcCongresoClient

def verify_sync():
    print("--- Probando obtener_iniciativas (sync - limit: 2 páginas) ---")
    client = BcCongresoClient()
    iniciativas = client.obtener_iniciativas(max_paginas=2)
    
    print(f"Iniciativas de BC extraídas: {len(iniciativas)}")
    for i in iniciativas[:3]:
        print(f"[{i.fecha or 'Sin fecha'}] Sesión: {i.sesion} - Doc: {i.num_doc}")
        print(f"  Tipo: {i.tipo} (Presentado por: {i.presentado_por})")
        print(f"  Votación/Estatus: {i.votacion}")
        print(f"  Desc: {i.descripcion[:80]}...")
        print(f"  PDF: {i.url_pdf}")
        print()

async def verify_async():
    print("--- Probando a_obtener_iniciativas (async - limit: 1 página) ---")
    client = BcCongresoClient()
    iniciativas = await client.a_obtener_iniciativas(max_paginas=1)
    print(f"Iniciativas extraídas asíncronamente: {len(iniciativas)}")

if __name__ == "__main__":
    verify_sync()
    asyncio.run(verify_async())
