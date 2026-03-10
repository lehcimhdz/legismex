import asyncio
from legismex.colima import ColimaClient


async def test_colima():
    client = ColimaClient()

    print("Obteniendo decretos de la legislatura 61...")
    decretos = await client.a_obtener_decretos(61, "LXI Legislatura")
    print(f"Total Decretos encontrados: {len(decretos)}")
    if decretos:
        d = decretos[0]
        print(
            f"[{d.numero}] {d.descripcion[:50]}... (Aprob: {d.fecha_aprobacion}) -> PDF: {d.url_pdf}")

    print("\nObteniendo diario de debates de la legislatura 61...")
    diarios = await client.a_obtener_diario_debates(61, "LXI Legislatura")
    print(f"Total Diarios encontrados: {len(diarios)}")
    if diarios:
        dia = diarios[0]
        print(f"[{dia.fecha}] {dia.descripcion[:50]}... -> PDF: {dia.url_pdf}")

    print("\nObteniendo iniciativas de la legislatura 61...")
    iniciativas = client.obtener_iniciativas(61, "LXI Legislatura")
    print(f"Total Iniciativas encontradas: {len(iniciativas)}")
    if iniciativas:
        i = iniciativas[0]
        print(f"[{i.numero}] {i.descripcion[:50]}... (Estatus: {i.status})")

    print("\nObteniendo actas...")
    actas = client.obtener_actas(61, "LXI Legislatura")
    print(f"Total Actas encontradas: {len(actas)}")
    if actas:
        a = actas[0]
        print(f"[{a.fecha_aprobacion}] {a.descripcion[:50]}...")

if __name__ == "__main__":
    asyncio.run(test_colima())
