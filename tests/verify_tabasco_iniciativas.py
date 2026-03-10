from legismex.tabasco_iniciativas.client import TabascoIniciativasClient


def imprimir_iniciativa(ini):
    print(f"[{ini.fecha}] No. {ini.numero}")
    print(f"  > Título: {ini.titulo[:100]}...")
    print(f"  > Presentada por: {ini.presentada_por}")
    print(f"  > PDF: {ini.url_pdf}")


def test_tabasco_iniciativas():
    print("=== Tabasco Iniciativas (Congreso) ===")
    print("Nota: Este test descarga una tabla grande, puede tardar unos segundos...")
    client = TabascoIniciativasClient()
    try:
        # 1. Obtener iniciativas del 2024
        anio = 2024
        print(f"\n--- Iniciativas del año {anio} ---")
        iniciativas = client.obtener_iniciativas(anio=anio)
        print(f"Total iniciativas encontradas en {anio}: {len(iniciativas)}")

        if not iniciativas:
            print(f"No se encontraron iniciativas para el año {anio}.")
            return

        # Mostrar las 5 más recientes del bloque
        for ini in iniciativas[:5]:
            imprimir_iniciativa(ini)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de Iniciativas: {exc}")


if __name__ == "__main__":
    test_tabasco_iniciativas()
