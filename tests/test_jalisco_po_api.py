import json
from legismex.jalisco_po import JaliscoPoClient

def test():
    print("Testing Jalisco PO Client...")
    
    # 1. Initialize
    client = JaliscoPoClient()
    
    # 2. Search
    print("\\n[1] Buscando ediciones recientes...")
    paginated_results = client.buscar_ediciones(elementos_por_pagina=2)
    print(f"Total entries in DB: {paginated_results.total}")
    
    if not paginated_results.items:
        print("No items found!")
        return
        
    for item in paginated_results.items:
        print(f" - {item.date_newspaper} | Tomo {item.tomo} | {item.description[:60]}...")
        
    # 3. Get Details
    target_id = paginated_results.items[0].id_newspaper
    print(f"\\n[2] Obteniendo detalles absolutos para ID {target_id}...")
    detail = client.obtener_edicion(target_id)
    
    print(f"  > Title/ID: {detail.id}")
    print(f"  > Section: {detail.section}")
    print(f"  > Direct PDF Link: {detail.link}")

if __name__ == "__main__":
    test()
