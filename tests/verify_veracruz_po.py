from legismex.veracruz_po.client import VeracruzPoClient


def imprimir_edicion(e):
    print(f"[{e.fecha_textual}] {e.nombre}")
    print(f"  > PDF: {e.url_pdf}")


def test_veracruz_po():
    print("=== Veracruz Gaceta Oficial (Editora de Gobierno) ===")
    client = VeracruzPoClient()
    try:
        # 1. Obtener ediciones de Enero 2025
        anio = 2025
        mes = 1
        print(f"\n--- Ediciones de {mes:02d}/{anio} ---")
        ediciones = client.obtener_ediciones(anio=anio, mes=mes)

        print(f"Total ediciones encontradas: {len(ediciones)}")

        if not ediciones:
            print(f"No se encontraron ediciones para {mes:02d}/{anio}.")
            return

        # Mostrar las 5 más recientes del bloque
        for e in ediciones[:5]:
            imprimir_edicion(e)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")


if __name__ == "__main__":
    test_veracruz_po()
