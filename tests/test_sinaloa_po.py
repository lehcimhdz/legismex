"""Test para SinaloaPoClient — Periódico Oficial del Estado de Sinaloa.

Uso:
    cd legismex
    python -m tests.test_sinaloa_po
"""
import asyncio
from legismex import SinaloaPoClient


async def main():
    client = SinaloaPoClient()

    # --- Mes actual (marzo 2026) ---
    print("=" * 60)
    print("Ediciones de marzo 2026")
    print("=" * 60)
    marzo = await client.a_buscar_mes(2026, 3)
    print(f"  Total: {len(marzo)}")
    for e in marzo:
        flag = " [VESP]" if e.vespertina else ""
        print(f"  {e.fecha} | {e.titulo}{flag}")
        if e.pdf_url:
            print(f"           PDF: {e.pdf_url}")

    # --- Enero 2026 ---
    print()
    print("=" * 60)
    print("Ediciones de enero 2026")
    print("=" * 60)
    enero = await client.a_buscar_mes(2026, 1)
    print(f"  Total: {len(enero)}")
    for e in enero[:4]:
        flag = " [VESP]" if e.vespertina else ""
        print(f"  {e.fecha} | {e.titulo}{flag}")
        if e.indice:
            print(f"           Índice: {e.indice[:80]}...")

    # --- Año completo 2025 ---
    print()
    print("=" * 60)
    print("Ediciones año 2025 (all_pages=True)")
    print("=" * 60)
    anio_2025 = await client.a_buscar_anio(2025)
    print(f"  Total 2025: {len(anio_2025)}")
    vesp = [e for e in anio_2025 if e.vespertina]
    print(f"  De las cuales vespertinas: {len(vesp)}")
    con_pdf = [e for e in anio_2025 if e.pdf_url]
    print(f"  Con PDF encontrado: {len(con_pdf)}")


if __name__ == "__main__":
    asyncio.run(main())
