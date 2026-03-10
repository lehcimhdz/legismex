import asyncio
from legismex.chiapas_po import ChiapasPoClient, ChiapasAdministracion


def run_sync():
    client = ChiapasPoClient()
    print("Consultando el Periódico Oficial de Chiapas Síncrono (2024-12, Admin 2024-2030)")
    # Consultando diciembre de 2024 (pocos registros para test)
    ediciones = client.obtener_ediciones(
        ChiapasAdministracion.ADMIN_2024_2030, anio=2024, mes=12)

    print(f"Total de ediciones síncronas encontradas: {len(ediciones)}")
    for ed in ediciones[:3]:
        print(
            f"Num {ed.numero} | Fecha {ed.fecha} | Sec {ed.seccion} | Par {ed.parte}")
        print(f"URL: {ed.url_pdf}")


async def run_async():
    client = ChiapasPoClient()
    print("\nConsultando el Periódico Oficial de Chiapas Asíncrono (2024-11, Admin 2018-2024)")
    # Consulta asíncrona de noviembre usando el endpoint de la admin pasada
    ediciones = await client.a_obtener_ediciones(ChiapasAdministracion.ADMIN_2018_2024, anio=2024, mes=11)

    print(f"Total de ediciones asíncronas encontradas: {len(ediciones)}")
    for ed in ediciones[:3]:
        print(
            f"Num {ed.numero} | Fecha {ed.fecha} | Sec {ed.seccion} | Par {ed.parte}")
        print(f"URL: {ed.url_pdf}")

if __name__ == "__main__":
    run_sync()
    asyncio.run(run_async())
