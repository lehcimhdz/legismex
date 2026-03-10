from legismex.zacatecas_po.client import ZacatecasPoClient
from datetime import date, timedelta

def imprimir_publicacion(p):
    print(f"[{p.fecha_publicacion}] {p.titulo or p.descripcion or 'Sin título'}")
    if p.tomo:
        print(f"  > Tomo: {p.tomo} (Vol: {p.volumen})")
    print(f"  > PDF: {p.url_pdf}")

def test_zacatecas_po():
    print("=== Zacatecas Periódico Oficial (POEZ API) ===")
    client = ZacatecasPoClient()
    try:
        # 1. Obtener ediciones de los últimos 15 días
        fecha_final = date.today().isoformat()
        fecha_inicial = (date.today() - timedelta(days=15)).isoformat()
        
        print(f"\n--- Ediciones desde {fecha_inicial} hasta {fecha_final} ---")
        ediciones = client.obtener_ediciones(fecha_inicial=fecha_inicial, fecha_final=fecha_final)
        print(f"Total ediciones encontradas: {len(ediciones)}")
        
        if not ediciones:
            print("No se encontraron ediciones en el rango. Probando búsqueda de leyes...")
            leyes = client.buscar_leyes(descripcion="Educación")
            print(f"Total leyes encontradas (Educación): {len(leyes)}")
            for p in leyes[:2]:
                imprimir_publicacion(p)
                print("-" * 20)
        else:
            # Mostrar las 3 más recientes
            for p in ediciones[:3]:
                imprimir_publicacion(p)
                print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")

if __name__ == "__main__":
    test_zacatecas_po()
