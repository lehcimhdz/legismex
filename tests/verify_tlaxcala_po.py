from legismex.tlaxcala_po.client import TlaxcalaPoClient


def imprimir_edicion(e):
    print(f"[{e.fecha}] No. {e.numero}")
    print(f"  > Contenido: {e.contenido[:100]}...")
    print(f"  > PDF: {e.url_pdf}")


def test_tlaxcala_po():
    print("=== Tlaxcala Periódico Oficial (Índices Joomla) ===")
    client = TlaxcalaPoClient()
    try:
        # 1. Obtener ediciones del año 2026
        anio = 2026
        print(f"\n--- Ediciones del año {anio} ---")
        ediciones = client.obtener_ediciones(anio=anio)
        print(f"Total ediciones encontradas: {len(ediciones)}")

        if not ediciones:
            print(f"No se encontraron ediciones para el año {anio}.")
            return

        # Mostrar las 5 más recientes
        for e in ediciones[:5]:
            imprimir_edicion(e)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")


if __name__ == "__main__":
    test_tlaxcala_po()
