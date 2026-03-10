import sys
from legismex.oaxaca.client import OaxacaClient

def imprimir_gaceta(g):
    print(f"[{g.fecha}] {g.numero} - {g.tipo} (ID: {g.id})")
    print(f"  > Detalle: {g.url_detalle}")
    if g.documentos:
        print(f"  > Documentos extraídos: {len(g.documentos)}")
        for d in g.documentos[:3]:
            print(f"    - [{d.numero}] {d.descripcion[:100]}...")
            if d.url_pdfs:
                print(f"      PDFs: {', '.join(d.url_pdfs)}")

def test_oaxaca_congreso():
    print("=== Oaxaca Congreso (LXVI Legislatura) ===")
    client = OaxacaClient() # verify=False ya está en el __init__
    try:
        # 1. Listar gacetas (Índice)
        print("\n--- Listado de Gacetas (Índice) ---")
        gacetas = client.listar_gacetas()
        print(f"Total gacetas en el índice: {len(gacetas)}")
        if not gacetas:
            print("No se encontraron gacetas en el índice.")
            return

        # Mostrar las 3 primeras
        for g in gacetas[:3]:
            print(f"- {g.numero} ({g.fecha})")
        
        # 2. Obtener detalle de la más reciente
        target = gacetas[0]
        print(f"\n--- Detalle Gaceta ID: {target.id} ---")
        g_detalle = client.obtener_gaceta(target.id)
        imprimir_gaceta(g_detalle)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")

if __name__ == "__main__":
    test_oaxaca_congreso()
