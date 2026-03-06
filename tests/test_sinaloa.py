"""Test para SinaloaClient — H. Congreso del Estado de Sinaloa.

Uso:
    cd legismex
    python -m tests.test_sinaloa
"""
import asyncio
from legismex import SinaloaClient


async def main():
    client = SinaloaClient()

    # --- Legislaturas disponibles ---
    legs = await client.a_obtener_legislaturas()
    print(f"Legislaturas disponibles: {[l.nu_legislatura for l in legs]}")

    # --- Iniciativas (LXV = 65) ---
    print()
    print("=" * 60)
    print("Iniciativas — LXV Legislatura (65)")
    print("=" * 60)
    iniciativas = await client.a_obtener_iniciativas("65")
    print(f"  Total: {len(iniciativas)}")
    for ini in iniciativas[-3:]:
        print(f"  [{ini.id}] {ini.fecha} | {(ini.presentada or '')[:40]}")
        print(f"        {(ini.iniciativa or '')[:80]}...")

    # --- Dictámenes ---
    print()
    print("=" * 60)
    print("Dictámenes — LXV Legislatura (65)")
    print("=" * 60)
    dictamenes = await client.a_obtener_dictamenes("65")
    print(f"  Total: {len(dictamenes)}")
    for d in dictamenes[:3]:
        print(f"  [{d.id}] {d.fecha} | {(d.asunto or '')[:70]}...")

    # --- Acuerdos ---
    print()
    print("=" * 60)
    print("Acuerdos — LXV Legislatura (65)")
    print("=" * 60)
    acuerdos = await client.a_obtener_acuerdos("65")
    print(f"  Total: {len(acuerdos)}")
    for a in acuerdos[:3]:
        print(f"  [{a.id}] {a.fecha} | Votación: {a.votacion} | {(a.asunto or '')[:60]}...")

    # --- Decretos ---
    print()
    print("=" * 60)
    print("Decretos — LXV Legislatura (65)")
    print("=" * 60)
    decretos = await client.a_obtener_decretos("65")
    print(f"  Total: {len(decretos)}")
    for d in decretos[:3]:
        print(f"  [{d.id}] {d.fecha} | PDF Voto: {d.pdfvoto} | {(d.asunto or '')[:60]}...")


if __name__ == "__main__":
    asyncio.run(main())
