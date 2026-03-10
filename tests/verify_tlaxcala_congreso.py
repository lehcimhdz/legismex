from legismex.tlaxcala.client import TlaxcalaClient


def imprimir_documento(d):
    print(f"[{d.categoria}] {d.fecha or 'N/A'}")
    print(f"  > Título: {d.titulo[:100]}...")
    if d.numero:
        print(f"  > Número: {d.numero}")
    print(f"  > PDF: {d.url_pdf}")


def test_tlaxcala_congreso():
    print("=== Tlaxcala Congreso (Trabajo Legislativo LXV) ===")
    client = TlaxcalaClient()
    try:
        # 1. Obtener documentos de una categoría específica (ej. Iniciativas) para el 2025
        categoria = "Iniciativas"
        anio = 2025
        print(f"\n--- {categoria} del año {anio} ---")
        docs = client.obtener_documentos(categoria=categoria, anio=anio)
        print(f"Total documentos encontrados: {len(docs)}")

        if not docs:
            print(
                f"No se encontraron documentos en la categoría {categoria} para {anio}.")
        else:
            # Mostrar los 3 más recientes
            for d in docs[:3]:
                imprimir_documento(d)
                print("-" * 20)

        # 2. Probar otra categoría (ej. Decretos)
        categoria_2 = "Decretos"
        print(f"\n--- {categoria_2} del año {anio} ---")
        docs_2 = client.obtener_documentos(categoria=categoria_2, anio=anio)
        print(f"Total documentos encontrados: {len(docs_2)}")

        for d in docs_2[:3]:
            imprimir_documento(d)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")


if __name__ == "__main__":
    test_tlaxcala_congreso()
