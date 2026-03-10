from legismex.tamaulipas.client import TamaulipasClient

def imprimir_gaceta(g):
    print(f"[{g.fecha_gaceta}] No. {g.numero} (Tomo: {g.tomo})")
    print(f"  > Sesión: {g.sesion} ({g.fecha_sesion})")
    print(f"  > Publicado: {g.publicado_el}")
    print(f"  > PDF: {g.url_pdf}")

def test_tamaulipas_congreso():
    print("=== Tamaulipas Congreso (Gaceta ASP) ===")
    client = TamaulipasClient()
    try:
        # 1. Obtener gacetas de la legislatura actual (66)
        leg = 66
        print(f"\n--- Gacetas de la Legislatura {leg} ---")
        gacetas = client.obtener_gacetas(legislatura=leg)
        print(f"Total gacetas encontradas: {len(gacetas)}")
        
        if not gacetas:
            print(f"No se encontraron gacetas para la legislatura {leg}.")
            return

        # Mostrar las 5 más recientes
        for g in gacetas[:5]:
            imprimir_gaceta(g)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")

if __name__ == "__main__":
    test_tamaulipas_congreso()
