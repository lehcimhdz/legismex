from legismex.guerrero_po.client import GuerreroPoClient


def imprimir_publicacion(p):
    print(f"[{p.fecha}] {p.categoria}")
    print(f"  > Título: {p.titulo[:100]}...")
    print(f"  > PDF: {p.url_pdf}")
    print(f"  > Detalle: {p.url_detalle}")


def test_guerrero_po():
    print("=== Guerrero Periódico Oficial ===")
    client = GuerreroPoClient()
    try:
        # Publicaciones recientes
        print("\n--- Publicaciones Recientes ---")
        pubs = client.obtener_publicaciones(pagina=1)
        print(f"Obtenidas {len(pubs)} publicaciones")
        for p in pubs[:3]:
            imprimir_publicacion(p)
            print("-" * 20)

        # Búsqueda por año y categoría (LEYES = 25)
        print("\n--- Búsqueda: Leyes del 2025 ---")
        leyes = client.obtener_publicaciones(anio=2025, categoria=25)
        print(f"Obtenidas {len(leyes)} leyes")
        for l in leyes[:2]:
            imprimir_publicacion(l)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")


if __name__ == "__main__":
    test_guerrero_po()
