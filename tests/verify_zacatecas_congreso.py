from legismex.zacatecas.client import ZacatecasClient


def imprimir_gaceta(g):
    print(f"[{g.fecha}] No. {g.numero} (Tomo: {g.tomo})")
    print(f"  > Sesión: {g.tipo_sesion}")
    print(f"  > Periodo: {g.periodo} ({g.anio_ejercicio})")
    print(f"  > PDF: {g.url_pdf}")


def test_zacatecas_congreso():
    print("=== Zacatecas Congreso (Gaceta Legislativa LXV) ===")
    client = ZacatecasClient()
    try:
        # 1. Obtener meses disponibles
        print("\n--- Meses disponibles ---")
        meses = client.obtener_meses()
        print(f"Meses encontrados: {len(meses)}")
        if meses:
            print(f"Muestra: {meses[:3]}")

        # 2. Obtener gacetas del mes más reciente o uno específico
        # Si estamos en marzo 2026, probamos con el actual o el anterior
        mes_a_probar = meses[0] if meses else None
        print(f"\n--- Gacetas del mes {mes_a_probar} ---")
        gacetas = client.obtener_gacetas(mes=mes_a_probar)
        print(f"Total gacetas encontradas: {len(gacetas)}")

        if not gacetas:
            print(f"No se encontraron gacetas para el mes {mes_a_probar}.")
        else:
            # Mostrar las 3 más recientes
            for g in gacetas[:3]:
                imprimir_gaceta(g)
                print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")


if __name__ == "__main__":
    test_zacatecas_congreso()
