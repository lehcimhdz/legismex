from legismex.michoacan.client import MichoacanClient


def imprimir_gaceta(g):
    print(f"[{g.fecha}] {g.titulo} (Leg. {g.legislatura})")
    print(f"  > Tomo: {g.tomo} | Número: {g.numero} | Época: {g.epoca}")
    print(f"  > Descripción: {g.descripcion[:100]}...")
    print(f"  > PDF: {g.url_pdf}")


def test_michoacan_congreso():
    print("=== Michoacán Congreso (Gaceta Parlamentaria) ===")
    client = MichoacanClient()
    try:
        # Obtener gacetas de la legislatura actual (LXXVI)
        leg = "lxxvi"
        print(f"\n--- Gacetas Legislatura {leg.upper()} (Página 1) ---")
        gacetas = client.obtener_gacetas(legislatura=leg, page=1)
        print(f"Obtenidas {len(gacetas)} gacetas")

        for g in gacetas[:3]:
            imprimir_gaceta(g)
            print("-" * 20)

        # Probar total de páginas
        total = client.obtener_total_paginas(legislatura=leg)
        print(f"\nTotal de páginas para {leg.upper()}: {total}")

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")


if __name__ == "__main__":
    test_michoacan_congreso()
