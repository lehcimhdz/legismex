"""Test para NayaritCongresoClient.

Uso:
    cd legismex
    python -m tests.test_nayarit_congreso
"""
import asyncio
from legismex import NayaritCongresoClient


async def main():
    client = NayaritCongresoClient()

    # --- XXXIV Legislatura (actual) ---
    print("=" * 60)
    print("XXXIV Legislatura")
    print("=" * 60)
    iniciativas = await client.a_obtener_iniciativas("XXXIV")
    print(f"  Total iniciativas: {len(iniciativas)}")
    for ini in iniciativas[:5]:
        pdf = ini.url_pdf or "sin PDF"
        print(f"  [{ini.numero}] {ini.fecha_recepcion} | {ini.origen[:40]}")
        print(f"        Dictamen: {ini.dictamen} | PDF: {pdf[-60:]}")

    # --- XXXIII Legislatura ---
    print()
    print("=" * 60)
    print("XXXIII Legislatura")
    print("=" * 60)
    anteriores = await client.a_obtener_iniciativas("XXXIII")
    print(f"  Total iniciativas: {len(anteriores)}")
    for ini in anteriores[:3]:
        print(f"  [{ini.numero}] {ini.fecha_recepcion} | {ini.descripcion[:70]}...")


if __name__ == "__main__":
    asyncio.run(main())
