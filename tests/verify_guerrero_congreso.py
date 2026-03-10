from legismex.guerrero.client import GuerreroClient

def imprimir_gaceta(g):
    print(f"[{g.fecha}] {g.nombre} (ID: {g.id})")
    print(f"  > Detalle: {g.url_detalle}")
    if g.documentos:
        print(f"  > Documentos extraídos: {len(g.documentos)}")
        for d in g.documentos[:2]:
            print(f"    - {d.tipo}: {d.descripcion[:60]}...")
            print(f"      PDF: {d.url_pdf}")

def test_guerrero_congreso():
    print("=== Guerrero Congreso (Gaceta Parlamentaria) ===")
    client = GuerreroClient()
    try:
        # Obtener gacetas
        print("\n--- Listado de Gacetas (Página 1) ---")
        gacetas, total = client.obtener_gacetas(pagina=1, limite=5, con_documentos=True)
        print(f"Total registros en el sistema: {total}")
        print(f"Gacetas procesadas en esta página: {len(gacetas)}")
        
        for g in gacetas:
            imprimir_gaceta(g)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")

if __name__ == "__main__":
    test_guerrero_congreso()
