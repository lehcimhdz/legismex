from legismex.tabasco_po.client import TabascoPoClient

def imprimir_publicacion(p):
    print(f"[{p.fecha}] No. {p.numero} ({p.tipo})")
    if p.suplemento:
        print(f"  > Suplemento: {p.suplemento}")
    print(f"  > Desc: {p.descripcion[:100]}...")
    print(f"  > PDF: {p.url_pdf}")

def test_tabasco_po():
    print("=== Tabasco Periódico Oficial ===")
    client = TabascoPoClient()
    try:
        # 1. Obtener publicaciones de la primera página (recientes)
        print("\n--- Publicaciones Recientes (Página 1) ---")
        publicaciones = client.obtener_publicaciones(paginas=1)
        print(f"Total publicaciones encontradas: {len(publicaciones)}")
        
        if not publicaciones:
            print("No se encontraron publicaciones recientes.")
        else:
            for p in publicaciones[:3]:
                imprimir_publicacion(p)
                print("-" * 20)

        # 2. Probar búsqueda por año 2025
        busqueda = "2025"
        print(f"\n--- Buscando '{busqueda}' ---")
        resultados = client.obtener_publicaciones(busqueda=busqueda, paginas=1)
        print(f"Total resultados para '{busqueda}': {len(resultados)}")
        
        for p in resultados[:3]:
            imprimir_publicacion(p)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")

if __name__ == "__main__":
    test_tabasco_po()
