from legismex.oaxaca_po.client import OaxacaPoClient


def imprimir_edicion(e):
    print(f"[{e.fecha}] {e.nombre} ({e.tipo})")
    print(f"  > PDF: {e.url_pdf}")


def test_oaxaca_po():
    print("=== Oaxaca Periódico Oficial ===")
    client = OaxacaPoClient()
    try:
        # 1. Obtener ediciones Ordinarias recientes
        print("\n--- Ediciones Ordinarias (Muestra) ---")
        ediciones = client.obtener_ediciones(tipo="Ordinario", ano=2025)
        print(f"Total ediciones Ordinarias en 2025: {len(ediciones)}")
        for e in ediciones[:3]:
            imprimir_edicion(e)
            print("-" * 20)

        # 2. Probar filtrado por mes (Feb/2026 o similar)
        anio_actual = 2026
        mes_num = 2  # Febrero
        print(f"\n--- Ediciones en 0{mes_num}/{anio_actual} ---")
        mes_filtro = client.obtener_ediciones(ano=anio_actual, mes=mes_num)
        print(f"Ediciones encontradas en Febrero 2026: {len(mes_filtro)}")
        for m in mes_filtro[:2]:
            imprimir_edicion(m)
            print("-" * 20)

        # 3. Búsqueda por palabra clave
        keyword = "extraordinario"
        print(f"\n--- Búsqueda: '{keyword}' ---")
        res = client.buscar(keyword)
        print(f"Resultados para '{keyword}': {len(res)}")
        for r in res[:2]:
            imprimir_edicion(r)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")


if __name__ == "__main__":
    test_oaxaca_po()
