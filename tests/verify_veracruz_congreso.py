from legismex.veracruz.client import VeracruzClient

def imprimir_sesion(s):
    print(f"[{s.fecha}] {s.tipo_sesion}")
    print(f"  > Periodo: {s.periodo} ({s.anio_ejercicio})")
    if s.gaceta_pdf:
        print(f"  > Gaceta PDF: {s.gaceta_pdf}")
    
    total_docs = len(s.anexos)
    print(f"  > Anexos: {total_docs}")
    # Mostrar hasta 3 anexos
    for doc in s.anexos[:3]:
        print(f"    - {doc.titulo[:80]}...")
        print(f"      PDF: {doc.url_pdf}")

def test_veracruz_congreso():
    print("=== Veracruz Congreso (Gaceta Legislativa) ===")
    client = VeracruzClient()
    try:
        # 1. Obtener todas las gacetas/sesiones
        print("\n--- Obteniendo sesiones ---")
        sesiones = client.obtener_gacetas()
        print(f"Total sesiones encontradas: {len(sesiones)}")
        
        if not sesiones:
            print("No se encontraron sesiones.")
            return

        # Mostrar las 3 más recientes
        for s in sesiones[:3]:
            imprimir_sesion(s)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")

if __name__ == "__main__":
    test_veracruz_congreso()
