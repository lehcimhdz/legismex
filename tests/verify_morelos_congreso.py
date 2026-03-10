from legismex.morelos.client import MorelosClient


def imprimir_documento(d):
    print(f"[{d.seccion}] {d.titulo}")
    if d.periodo:
        print(f"  > Periodo: {d.periodo}")
    print(f"  > PDF: {d.url_pdf}")


def test_morelos_congreso():
    print("=== Morelos Congreso (LVI Legislatura) ===")
    client = MorelosClient()
    try:
        # Obtener todos los documentos (o una muestra)
        print("\n--- Documentos Legislativos (Muestra) ---")
        docs = client.obtener_documentos()
        print(f"Total documentos encontrados: {len(docs)}")

        # Mostrar los primeros 5
        for d in docs[:5]:
            imprimir_documento(d)
            print("-" * 20)

        # Probar filtrado por sección
        sec = "Orden-del-día"
        print(f"\n--- Filtrado por Sección: {sec} ---")
        ordenes = client.obtener_documentos(seccion=sec)
        print(f"Documentos en {sec}: {len(ordenes)}")
        for o in ordenes[:3]:
            imprimir_documento(o)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")


if __name__ == "__main__":
    test_morelos_congreso()
