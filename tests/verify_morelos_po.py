from legismex.morelos_po.client import MorelosPoClient

def imprimir_ejemplar(e):
    print(f"[{e.fecha_publicacion}] No. {e.numero} ({e.edicion})")
    if e.sumario:
        print(f"  > Sumario: {e.sumario[:150]}...")
    print(f"  > PDF: {e.url_pdf}")

def test_morelos_po():
    print("=== Morelos Periódico Oficial (Tierra y Libertad) ===")
    client = MorelosPoClient()
    try:
        # Obtener ejemplares recientes (2025 o 2026)
        anio = 2025
        print(f"\n--- Ejemplares del {anio} ---")
        docs, total = client.obtener_ejemplares(anio=anio, page_size=5)
        print(f"Total registros encontrados para {anio}: {total}")
        
        for d in docs:
            imprimir_ejemplar(d)
            print("-" * 20)

        # Probar búsqueda por sumario
        keyword = "Reglamento"
        print(f"\n--- Búsqueda Sumario: '{keyword}' ---")
        res, total_res = client.obtener_ejemplares(buscar_sumario=keyword, page_size=3)
        print(f"Resultados para '{keyword}': {total_res}")
        for r in res:
            imprimir_ejemplar(r)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")

if __name__ == "__main__":
    test_morelos_po()
