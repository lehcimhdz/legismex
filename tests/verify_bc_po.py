from legismex.bc_po.client import BcPoClient
import sys
import os
import asyncio

# Añadir src al path
sys.path.append(os.path.abspath("src"))


async def verify():
    client = BcPoClient()

    print("--- Probando obtener_ediciones (Diciembre 2025) ---")
    resultado = client.obtener_ediciones(2025, 12)
    print(f"Ediciones encontradas: {len(resultado.ediciones)}")
    for ed in resultado.ediciones[:5]:
        print(f"- [{ed.fecha}] No. {ed.numero} ({ed.seccion})")
        print(f"  Tomo: {ed.tomo}")
        print(f"  URL: {ed.url_pdf}")

    print("\n--- Probando a_obtener_ediciones (Enero 2026 - async) ---")
    a_resultado = await client.a_obtener_ediciones(2026, 1)
    print(f"Ediciones (async): {len(a_resultado.ediciones)}")
    if a_resultado.ediciones:
        last = a_resultado.ediciones[0]
        print(f"Ultima edición: {last.fecha} No. {last.numero}")

if __name__ == "__main__":
    asyncio.run(verify())
