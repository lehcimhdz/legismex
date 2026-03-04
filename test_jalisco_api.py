import json
from legismex.jalisco import JaliscoClient

def test_jalisco_full():
    print("Testing Jalisco Client...")
    client = JaliscoClient()
    
    # 1. Calendario
    print("Fetching calendar...")
    cal = client.obtener_calendario_eventos()
    print(f"Found {len(cal)} dates. First date: {cal[0]}")
    
    # 2. Eventos 2025-10-06
    print("\nFetching events for 2025-10-06...")
    eventos = client.obtener_eventos_por_fecha("2025-10-06")
    print(f"Found {len(eventos)} events")
    
    for evt in eventos:
        print(f"\n--- Evento: {evt.titulo} ---")
        print(f"Tipo: {evt.tipo}, ID: {evt.id_evento}")
        print(f"Puntos de Orden ({len(evt.puntos_orden)}):")
        for i, pt in enumerate(evt.puntos_orden):
            print(f"  {i+1}. {pt.titulo}")
            for doc in pt.documentos:
                print(f"     -> Doc: {doc.titulo}")
                print(f"     -> URL: {doc.url}")

if __name__ == "__main__":
    test_jalisco_full()
