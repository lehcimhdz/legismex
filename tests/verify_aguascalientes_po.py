from legismex import AguascalientesPoClient
from datetime import datetime, timedelta

def imprimir_edicion(e):
    print(f"[{e.fecha_publicacion}] {e.edicion} - No. {e.numero}")
    print(f"  > Tomo: {e.tomo} | Sección: {e.seccion}")
    print(f"  > Dependencias: {e.dependencias}")
    print(f"  > PDF: {e.url_pdf}")

def test_aguascalientes_po():
    print("=== Aguascalientes Periódico Oficial ===")
    client = AguascalientesPoClient()
    try:
        # Definir rango de fechas (Un solo día conocido con records, usando MM/DD/YYYY)
        inicio = "05/15/2024"
        fin = "05/15/2024"
        
        print(f"Consultando del {inicio} al {fin} (MM/DD/YYYY)...")
        res = client.obtener_ediciones(fecha_inicio=inicio, fecha_fin=fin, pagina=1)
        
        print(f"Total ediciones encontradas en el rango: {res['total']}")
        for item in res['items'][:5]:
            imprimir_edicion(item)
            print("-" * 20)
            
        # Consultar calendario
        print("\n--- Consultando calendario (primeros 5 registros) ---")
        cal = client.calendario()
        print(f"Registros en el calendario: {len(cal)}")
        for entry in cal[:5]:
            print(f"Fecha: {entry.fecha_publicacion} | Ediciones: {entry.ediciones}")

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")

if __name__ == "__main__":
    test_aguascalientes_po()
