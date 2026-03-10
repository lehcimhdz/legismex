from legismex import AguascalientesClient


def imprimir_promocion(p):
    print(f"[{p.fecha_presentacion}] {p.tipo_promocion} #{p.id}")
    print(f"  > Contenido: {p.contenido[:100]}...")
    if p.tiene_archivo:
        print(f"  > PDF: {p.url_pdf}")
    else:
        print("  > [Sin Archivo]")


def test_aguascalientes_congreso():
    print("=== Aguascalientes Congreso ===")
    client = AguascalientesClient()
    try:
        # Obtener primeras promociones de la LXVI Legislatura
        res = client.obtener_promociones(
            legislatura="LXVI", pagina=1, tamaño_pagina=5)
        print(f"Total registros encontrados: {res['total']}")
        for item in res['items']:
            imprimir_promocion(item)
            print("-" * 20)

        # Probar búsqueda por palabra clave
        print("\n--- Probando búsqueda: 'Salud' ---")
        res_salud = client.obtener_promociones(
            busqueda="Salud", tamaño_pagina=3)
        print(f"Resultados para 'Salud': {res_salud['total']}")
        for item in res_salud['items']:
            imprimir_promocion(item)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")


if __name__ == "__main__":
    test_aguascalientes_congreso()
