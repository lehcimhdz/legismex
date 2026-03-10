from legismex.sonora.client import SonoraClient

def imprimir_gaceta(g):
    print(f"[{g.fecha_publicacion}] {g.nombre}")
    print(f"  > Tipo: {g.tipo}")
    print(f"  > ID: {g.id}")
    if hasattr(g, 'pdf_urls') and g.pdf_urls:
        print(f"  > PDFs: {len(g.pdf_urls)}")
        for url in g.pdf_urls[:2]:
            print(f"    - {url}")

def test_sonora_congreso():
    print("=== Sonora Congreso (Gaceta API) ===")
    client = SonoraClient()
    try:
        # 1. Obtener Legislaturas
        print("\n--- Legislaturas ---")
        legs = client.obtener_legislaturas()
        for l in legs:
            print(f"  - {l.nombre}: {l.descripcion} (ID: {l.id})")

        # 2. Buscar Gacetas (LXIV)
        leg_clave = "LXIV"
        print(f"\n--- Gacetas de la Legislatura {leg_clave} ---")
        gacetas = client.buscar(legislatura=leg_clave, all_pages=False)
        print(f"Total gacetas encontradas (página 1): {len(gacetas)}")
        
        if not gacetas:
            print(f"No se encontraron gacetas para {leg_clave}.")
            return

        # Mostrar las 3 más recientes
        for g in gacetas[:3]:
            imprimir_gaceta(g)
            print("-" * 20)

        # 3. Probar detalle con PDF
        print("\n--- Probando Detalle de la Gaceta más reciente ---")
        detalle = client.obtener_detalle(gacetas[0].id)
        imprimir_gaceta(detalle)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")

if __name__ == "__main__":
    test_sonora_congreso()
