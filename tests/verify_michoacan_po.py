from legismex.michoacan_po.client import MichoacanPoClient


def imprimir_archivo(a):
    print(f"[{a.dia}/{a.mes}/{a.anio}] {a.nombre}")
    print(f"  > PDF: {a.url_pdf}")


def test_michoacan_po():
    print("=== Michoacán Periódico Oficial ===")
    client = MichoacanPoClient()
    try:
        # Obtener años (verificar conexión AJAX)
        print("\n--- Años Disponibles (Top 5) ---")
        anios = client.obtener_anios()
        print(f"Total años en archivo: {len(anios)}")
        for y in anios[:5]:
            print(f"  - {y.nombre} (ID: {y.cat_id})")

        # Probar navegación para el año actual
        anio_actual = anios[0].nombre
        cat_id_anio = anios[0].cat_id
        print(f"\n--- Meses en {anio_actual} ---")
        meses = client.obtener_meses(cat_id_anio)
        for m in meses:
            print(f"  - {m.nombre} (ID: {m.cat_id})")

        if meses:
            # Obtener archivos del primer mes encontrado
            mes_test = meses[0]
            print(f"\n--- Archivos en {mes_test.nombre} {anio_actual} ---")
            archivos = client.obtener_archivos_por_fecha(
                anio=int(anio_actual), mes=mes_test.nombre)
            print(f"Obtenidos {len(archivos)} archivos")
            for a in archivos[:3]:
                imprimir_archivo(a)
                print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")


if __name__ == "__main__":
    test_michoacan_po()
