from legismex.sinaloa.client import SinaloaClient


def imprimir_resumen(items, titulo):
    print(f"\n--- {titulo} (Muestra) ---")
    print(f"Total encontrados: {len(items)}")
    for item in items[:2]:
        if hasattr(item, 'iniciativa'):
            print(
                f"  > [{item.id}] {item.presentada}: {item.iniciativa[:100]}...")
        elif hasattr(item, 'asunto'):
            print(f"  > [{item.id}] {item.fecha}: {item.asunto[:100]}...")
        if hasattr(item, 'url_archivo') and item.url_archivo:
            print(f"    PDF: {item.url_archivo}")
        elif hasattr(item, 'archivo') and item.archivo:
            print(f"    PDF: {item.archivo}")


def test_sinaloa_congreso():
    print("=== Sinaloa Congreso (Gaceta API) ===")
    client = SinaloaClient()
    try:
        # 1. Legislaturas
        print("\n--- Legislaturas ---")
        legs = client.obtener_legislaturas()
        for l in legs:
            print(f"  - {l.nombre} (ID: {l.id})")

        # 2. Iniciativas (Legislatura 65)
        leg = "65"
        print(f"\nProbando Legislatura {leg}...")

        iniciativas = client.obtener_iniciativas(legislatura=leg)
        imprimir_resumen(iniciativas, "Iniciativas")

        dictamenes = client.obtener_dictamenes(legislatura=leg)
        imprimir_resumen(dictamenes, "Dictámenes")

        acuerdos = client.obtener_acuerdos(legislatura=leg)
        imprimir_resumen(acuerdos, "Acuerdos")

        decretos = client.obtener_decretos(legislatura=leg)
        imprimir_resumen(decretos, "Decretos")

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")


if __name__ == "__main__":
    test_sinaloa_congreso()
