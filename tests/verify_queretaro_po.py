from legismex.queretaro_po.client import QueretaroPoClient


def imprimir_edicion(e):
    print(f"[Fecha: {e.fecha}]")
    print(f"  > PDFs encontrados: {len(e.urls_pdf)}")
    for url in e.urls_pdf[:2]:
        print(f"    - {url}")


def test_queretaro_po():
    print("=== Querétaro Periódico Oficial (La Sombra de Arteaga) ===")
    client = QueretaroPoClient()
    try:
        # Obtener ediciones del 2025
        anio = 2025
        print(f"\n--- Ediciones del {anio} ---")
        ediciones = client.obtener_ediciones_por_ano(anio)
        print(f"Total días con publicaciones en {anio}: {len(ediciones)}")

        if not ediciones:
            print(f"No se encontraron ediciones para el año {anio}.")
            return

        # Mostrar las 3 más recientes
        for e in ediciones[:3]:
            imprimir_edicion(e)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")


if __name__ == "__main__":
    test_queretaro_po()
