from legismex.tamaulipas_po.client import TamaulipasPoClient
from datetime import date

def imprimir_edicion(e):
    print(f"[{e.fecha}] No. {e.numero} (Tomo: {e.tomo})")
    print(f"  > Documentos: {len(e.documentos)}")
    for doc in e.documentos[:2]:
        print(f"    - {doc.titulo}")
        print(f"      PDF: {doc.url_pdf}")

def test_tamaulipas_po():
    print("=== Tamaulipas Periódico Oficial ===")
    client = TamaulipasPoClient()
    try:
        # 1. Obtener ediciones de marzo 2026 (o el mes actual)
        anio = 2026
        mes = 3
        print(f"\n--- Ediciones de {mes:02d}/{anio} ---")
        ediciones = client.obtener_ediciones(anio=anio, mes=mes)
        
        print(f"Total días con publicaciones: {len(ediciones)}")
        
        if not ediciones:
            print(f"No se encontraron ediciones para {mes:02d}/{anio}. Probando Febrero...")
            ediciones = client.obtener_ediciones(anio=anio, mes=2)
            print(f"Total ediciones Febrero: {len(ediciones)}")

        # Mostrar las 3 más recientes del bloque
        for e in ediciones[-3:]:
            imprimir_edicion(e)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")

if __name__ == "__main__":
    test_tamaulipas_po()
