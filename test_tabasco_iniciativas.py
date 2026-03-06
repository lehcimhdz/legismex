import asyncio
from legismex.tabasco_iniciativas import TabascoIniciativasClient

def run_sync():
    print("Iniciando prueba SÍNCRONA para obtener Iniciativas del Congreso de Tabasco...")
    client = TabascoIniciativasClient()
    
    # Extraemos solo las del año 2024 para no imprimir 400+
    iniciativas_2024 = client.obtener_iniciativas(anio=2024)
    print(f"Total iniciativas extraídas del año 2024: {len(iniciativas_2024)}")
    
    for ini in iniciativas_2024[:3]:
        print(f"Num: {ini.numero} | Fecha: {ini.fecha} | Título: {ini.titulo[:60]}...")
        print(f"Autor: {ini.presentada_por} | Comisión: {ini.comision}")
        print(f"Enlace PDF: {ini.url_pdf}\n")

async def run_async():
    print("\nIniciando prueba ASÍNCRONA para obtener Iniciativas del Congreso de Tabasco...")
    client = TabascoIniciativasClient()
    
    # Extraemos solo para el año 2026, mes de febrero
    iniciativas_febrero_2026 = await client.a_obtener_iniciativas(anio=2026, mes=2)
    print(f"Total iniciativas extraídas de Febrero 2026: {len(iniciativas_febrero_2026)}")
    
    for ini in iniciativas_febrero_2026[:3]:
        print(f"Num: {ini.numero} | Fecha: {ini.fecha} | Título: {ini.titulo[:60]}...")
        print(f"Enlace PDF: {ini.url_pdf}\n")

if __name__ == "__main__":
    run_sync()
    asyncio.run(run_async())
