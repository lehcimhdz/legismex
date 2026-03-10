from legismex.guanajuato_po.client import GuanajuatoPoClient

def imprimir_edicion(e):
    print(f"[{e.fecha}] No. {e.numero}, Parte {e.parte} (Año {e.anio})")
    print(f"  > Desc: {e.descripcion[:100]}...")
    print(f"  > PDF: {e.url_pdf}")

def test_guanajuato_po():
    print("=== Guanajuato Periódico Oficial ===")
    client = GuanajuatoPoClient()
    try:
        # Último ejemplar
        print("\n--- Último Ejemplar ---")
        ultimos = client.obtener_ultimo_ejemplar()
        print(f"Obtenidos {len(ultimos)} registros")
        for u in ultimos[:2]:
            imprimir_edicion(u)
            print("-" * 20)

        # Búsqueda por palabra
        print("\n--- Búsqueda: 'Reglamento' (2025) ---")
        res = client.buscar(keyword="Reglamento", anio="2025", page_size=5)
        print(f"Obtenidos {len(res)} resultados")
        for r in res[:3]:
            imprimir_edicion(r)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")

if __name__ == "__main__":
    test_guanajuato_po()
