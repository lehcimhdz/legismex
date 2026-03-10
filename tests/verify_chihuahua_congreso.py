import asyncio
from legismex import ChihuahuaCongresoClient

def imprimir_sesion(s):
    print(f"[{s.sesion_id}] {s.titulo}")
    print(f"  > Fecha: {s.fecha}")
    if s.url_asistencia:
        print(f"  > Asistencia: {s.url_asistencia}")
    
    if s.documentos_probables:
        print(f"  > Docs Probables: {len(s.documentos_probables)}")
    if s.documentos_desahogados:
        print(f"  > Docs Desahogados: {len(s.documentos_desahogados)}")
    if s.documentos_votacion:
        print(f"  > Docs Votación: {len(s.documentos_votacion)}")

def test_sync():
    print("=== Gaceta de Chihuahua Síncrona (Pág 1) ===")
    client = ChihuahuaCongresoClient()
    try:
        sesiones = client.obtener_sesiones()
        print(f"Total Encontradas: {len(sesiones)}")
        for s in sesiones[:3]: # Imprimir las primeras 3
            imprimir_sesion(s)
            print("---")
    except Exception as exc:
        print(f"Error Síncrono: {exc}")

async def test_async():
    print("\n=== Gaceta de Chihuahua Asíncrona (Pág 2) ===")
    client = ChihuahuaCongresoClient()
    try:
        sesiones = await client.a_obtener_sesiones(pagina=2)
        print(f"Total Encontradas: {len(sesiones)}")
        for s in sesiones[:1]:
            imprimir_sesion(s)
    except Exception as exc:
        print(f"Error Asíncrono: {exc}")

if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
