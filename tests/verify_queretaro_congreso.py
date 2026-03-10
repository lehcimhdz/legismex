from legismex.queretaro.client import QueretaroClient


def imprimir_gaceta(g):
    print(f"[{g.legislatura}] No. {g.numero}")
    print(f"  > Desc: {g.descripcion[:100]}...")
    print(f"  > PDF: {g.url_pdf}")


def test_queretaro_congreso():
    print("=== Querétaro Congreso (Gacetas Legislativas) ===")
    client = QueretaroClient()
    try:
        # Obtener todas las gacetas
        print("\n--- Extrayendo Gacetas de Tablas Supsystic ---")
        gacetas = client.obtener_gacetas()
        print(f"Total gacetas encontradas: {len(gacetas)}")

        if not gacetas:
            print(
                "No se encontraron gacetas. Verifique la URL o la estructura de las tablas.")
            return

        # Mostrar las 5 más recientes (usualmente al inicio de las tablas o según el orden del sitio)
        for g in gacetas[:5]:
            imprimir_gaceta(g)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")


if __name__ == "__main__":
    test_queretaro_congreso()
