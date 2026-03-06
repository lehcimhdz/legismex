"""Tests para SonoraClient — Gaceta Parlamentaria del H. Congreso del Estado de Sonora.

Uso:
    cd legismex
    python -m tests.test_sonora
"""
import asyncio
from legismex import SonoraClient


async def main():
    client = SonoraClient()

    # -------------------------------------------------------------------
    print("=" * 60)
    print("Legislaturas disponibles")
    print("=" * 60)
    legs = await client.a_obtener_legislaturas()
    for l in legs:
        actual = " ← actual" if l.actual else ""
        print(f"  {l.nombre} | {l.descripcion}{actual}")

    # -------------------------------------------------------------------
    print()
    print("=" * 60)
    print("Gacetas LXIV (legislatura actual, todas las páginas)")
    print("=" * 60)
    gacetas_lxiv = await client.a_buscar(legislatura="LXIV")
    print(f"  Total LXIV: {len(gacetas_lxiv)}")
    pleno = [g for g in gacetas_lxiv if g.tipo == "PLENO"]
    comision = [g for g in gacetas_lxiv if g.tipo == "COMISION"]
    print(f"  Pleno: {len(pleno)} | Comisión: {len(comision)}")
    print(f"  Últimas 3:")
    for g in gacetas_lxiv[:3]:
        print(f"    [{g.tipo}] {g.nombre} | Periodo: {g.periodo}")

    # -------------------------------------------------------------------
    print()
    print("=" * 60)
    print("Búsqueda por palabra clave: 'decreto'")
    print("=" * 60)
    decretos = await client.a_buscar(legislatura="LXIV", buscar="decreto")
    print(f"  Resultados: {len(decretos)}")
    for g in decretos[:3]:
        print(f"    {g.nombre}")

    # -------------------------------------------------------------------
    print()
    print("=" * 60)
    print("Búsqueda por rango de fechas: enero 2026")
    print("=" * 60)
    enero = await client.a_buscar(
        legislatura="LXIV",
        fecha_inicio="2026-01-01",
        fecha_fin="2026-01-31",
    )
    print(f"  Enero 2026: {len(enero)} gacetas")
    for g in enero[:3]:
        print(f"    {g.fecha_publicacion[:10]} | {g.nombre}")

    # -------------------------------------------------------------------
    print()
    print("=" * 60)
    print("Detalle de gaceta (con PDF)")
    print("=" * 60)
    # Tomamos la primera gaceta de la lista
    primer_id = gacetas_lxiv[0].id
    detalle = await client.a_obtener_detalle(primer_id)
    print(f"  Nombre: {detalle.nombre}")
    print(f"  Tipo: {detalle.tipo}")
    if detalle.pdf_urls:
        print(f"  PDF: {detalle.pdf_urls[0]}")
    else:
        print("  Sin PDF adjunto")

    # -------------------------------------------------------------------
    print()
    print("=" * 60)
    print("Gacetas LXIII (legislatura anterior)")
    print("=" * 60)
    lxiii = await client.a_buscar(legislatura="LXIII")
    print(f"  Total LXIII: {len(lxiii)}")


if __name__ == "__main__":
    asyncio.run(main())
