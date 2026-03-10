from legismex.yucatan_congreso.client import YucatanCongresoClient

def imprimir_iniciativa(ini):
    print(f"[{ini.fecha_presentada}] {ini.legislatura}")
    print(f"  > Descripción: {ini.descripcion[:100]}...")
    print(f"  > Presentada por: {ini.presentada_por}")
    print(f"  > Turnada a: {ini.comision_permanente} ({ini.fecha_turnada})")
    print(f"  > Documentos: {len(ini.documentos)}")
    for doc in ini.documentos:
        print(f"    - [{doc.extension}] {doc.url}")

def test_yucatan_congreso():
    print("=== Yucatán Congreso (Iniciativas) ===")
    client = YucatanCongresoClient()
    try:
        # 1. Obtener iniciativas
        print("\n--- Obteniendo iniciativas ---")
        iniciativas = client.obtener_iniciativas()
        print(f"Total iniciativas encontradas: {len(iniciativas)}")
        
        if not iniciativas:
            print("No se encontraron iniciativas.")
            return

        # Mostrar las 3 más recientes del listado
        for ini in iniciativas[:3]:
            imprimir_iniciativa(ini)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")

if __name__ == "__main__":
    test_yucatan_congreso()
