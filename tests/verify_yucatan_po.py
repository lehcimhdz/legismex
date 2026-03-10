from legismex.yucatan_po.client import YucatanPoClient
from datetime import date


def imprimir_edicion(e):
    print(f"[{e.fecha}] {e.tipo} (No. {e.numero})")
    if e.sumario:
        print(f"  > Sumario: {e.sumario[:100]}...")
    print(f"  > PDF: {e.url_pdf}")


def test_yucatan_po():
    print("=== Yucatán Diario Oficial ===")
    client = YucatanPoClient()
    try:
        # 1. Obtener ediciones de una fecha reciente (Ej. 10 de marzo de 2026)
        # El portal espera YYYY-M-D (sin ceros)
        fecha = "2026-3-10"
        print(f"\n--- Ediciones de {fecha} ---")
        ediciones = client.obtener_ediciones_por_fecha(fecha=fecha)

        print(f"Total ediciones encontradas: {len(ediciones)}")

        if not ediciones:
            print(
                f"No se encontraron ediciones para la fecha {fecha}. Probando 9 de marzo...")
            ediciones = client.obtener_ediciones_por_fecha(fecha="2026-3-9")
            print(f"Total ediciones 9/marzo: {len(ediciones)}")

        # Mostrar las encontradas
        for e in ediciones:
            imprimir_edicion(e)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de D.O.: {exc}")


if __name__ == "__main__":
    test_yucatan_po()
