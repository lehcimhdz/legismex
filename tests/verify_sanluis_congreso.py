from legismex.sanluis.client import SanLuisClient


def imprimir_gaceta(g):
    print(f"[{g.fecha_iso}] {g.nombre}")
    print(f"  > Mes: {g.mes}")
    if g.urls_pdf:
        print(f"  > PDFs encontrados: {len(g.urls_pdf)}")
        for url in g.urls_pdf[:2]:
            print(f"    - {url}")


def test_sanluis_congreso():
    print("=== San Luis Potosí Congreso (Gaceta Parlamentaria) ===")
    print("Nota: Este test intenta resolver el reto Sucuri Cloudproxy...")
    client = SanLuisClient()
    try:
        # Obtener gacetas (archivo histórico completo)
        print("\n--- Extrayendo Archivo Histórico ---")
        gacetas = client.obtener_gacetas()
        print(f"Total sesiones encontradas: {len(gacetas)}")

        if not gacetas:
            print(
                "No se encontraron gacetas. Verifique el bypass de Sucuri o la estructura del sitio.")
            return

        # Mostrar las 5 más recientes (usualmente al final de la lista según el parser)
        # El parser agrupa por tabla, así que veamos los últimos registros
        print("\n--- Muestra de Sesiones Recientes ---")
        for g in gacetas[-5:]:
            imprimir_gaceta(g)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")


if __name__ == "__main__":
    test_sanluis_congreso()
