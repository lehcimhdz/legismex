from legismex.bcs_congreso.client import BcsCongresoClient
import sys
import os
import asyncio

# Añadir src al path
sys.path.append(os.path.abspath("src"))


async def verify():
    client = BcsCongresoClient()
    url = "https://www.cbcs.gob.mx/index.php/xvii-legislatura/xvii-leg-segundo-ano/xvii-leg-segundo-ano-primer-periodo-receso/orden-del-dia"

    print("--- Probando obtener_ordenes_dia ---")
    sesiones = client.obtener_ordenes_dia(url)
    print(f"Sesiones encontradas: {len(sesiones)}")
    for s in sesiones[:3]:
        print(f"- {s.titulo} ({s.fecha})")
        print(f"  URL: {s.url}")

    if sesiones:
        print("\n--- Probando obtener_detalle_orden ---")
        detalle = client.obtener_detalle_orden(sesiones[0].url)
        print(f"Título: {detalle.titulo}")
        print(f"Fecha: {detalle.fecha}")
        print(f"Documentos: {len(detalle.documentos)}")
        for d in detalle.documentos[:5]:
            print(f"  * {d.titulo}: {d.url}")

    print("\n--- Probando a_obtener_ordenes_dia (async) ---")
    a_sesiones = await client.a_obtener_ordenes_dia(url)
    print(f"Sesiones (async): {len(a_sesiones)}")

    print("\n--- Probando obtener_actas ---")
    actas_url = "https://www.cbcs.gob.mx/index.php/trabajos-legislativos/actas-sesiones"
    actas = client.obtener_actas(actas_url)
    print(
        f"Actas encontradas: {len(actas)} (Nota: esta página puede requerir navegación más profunda)")

if __name__ == "__main__":
    asyncio.run(verify())
