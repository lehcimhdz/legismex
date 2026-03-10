from legismex.sinaloa_po.client import SinaloaPoClient
from datetime import date, timedelta


def imprimir_edicion(e):
    print(f"[{e.fecha}] {e.titulo}")
    print(f"  > PDF: {e.pdf_url}")


def test_sinaloa_po():
    print("=== Sinaloa Periódico Oficial (POES) ===")
    client = SinaloaPoClient()
    try:
        # 1. Buscar ediciones recientes (últimos 30 días)
        end_date = date.today().isoformat()
        start_date = (date.today() - timedelta(days=30)).isoformat()

        print(
            f"\n--- Buscando ediciones desde {start_date} hasta {end_date} ---")
        ediciones = client.buscar(start_date=start_date, end_date=end_date)
        print(f"Total ediciones encontradas: {len(ediciones)}")

        if not ediciones:
            print("No se encontraron ediciones en el rango. Probando año 2025...")
            ediciones = client.buscar_anio(2025)
            print(f"Total ediciones 2025: {len(ediciones)}")

        # Mostrar las 3 más recientes
        for e in ediciones[-3:]:
            imprimir_edicion(e)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")


if __name__ == "__main__":
    test_sinaloa_po()
