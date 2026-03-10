"""Test para NayaritPoClient — Periódico Oficial del Estado de Nayarit.

Uso:
    cd legismex
    python -m tests.test_nayarit_po
"""
import asyncio
from legismex import NayaritPoClient


async def main():
    client = NayaritPoClient()

    # --- Búsqueda por fecha ---
    print("=" * 60)
    print("Búsqueda por fecha: 2026-03-05")
    print("=" * 60)
    resultado = await client.a_buscar_por_fecha("2026-03-05")
    print(f"  Total: {resultado.total} | Páginas: {resultado.total_paginas}")
    for pub in resultado.publicaciones:
        print(f"  [{pub.numero}] {pub.tipo} | Sección: {pub.seccion}")
        print(f"        {(pub.sumario or '')[:80]}...")
        print(f"        PDF: {pub.url_pdf}")

    # --- Búsqueda por palabra ---
    print()
    print("=" * 60)
    print("Búsqueda por palabra: 'decreto' (página 1)")
    print("=" * 60)
    resultado2 = await client.a_buscar_por_palabra("decreto")
    print(f"  Total: {resultado2.total} | Páginas: {resultado2.total_paginas}")
    for pub in resultado2.publicaciones[:3]:
        print(
            f"  [{pub.fecha_publicacion}] {pub.tipo}: {(pub.sumario or '')[:60]}...")

    # --- Búsqueda avanzada ---
    print()
    print("=" * 60)
    print("Búsqueda avanzada: 'ley' entre 2026-01-01 y 2026-03-01")
    print("=" * 60)
    resultado3 = await client.a_buscar_avanzada("ley", "2026-01-01", "2026-03-01")
    print(f"  Total: {resultado3.total} | Páginas: {resultado3.total_paginas}")
    for pub in resultado3.publicaciones[:3]:
        print(
            f"  [{pub.fecha_publicacion}] {pub.tipo}: {(pub.sumario or '')[:60]}...")


if __name__ == "__main__":
    asyncio.run(main())
