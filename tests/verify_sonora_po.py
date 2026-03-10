from legismex.sonora_po.client import SonoraPoClient
from datetime import date

def imprimir_edicion(e):
    print(f"[{e.fecha}] No. {e.numero} ({e.edicion_tipo})")
    if e.descripcion:
        print(f"  > Desc: {e.descripcion[:100]}...")
    print(f"  > PDF: {e.url_pdf}")

def test_sonora_po():
    print("=== Sonora Boletín Oficial ===")
    client = SonoraPoClient()
    try:
        # 1. Obtener ediciones de un mes reciente (ej. Enero 2026)
        anio = 2026
        mes = 1
        print(f"\n--- Ediciones de {mes}/{anio} ---")
        res = client.obtener_ediciones(anio=anio, mes=mes)
        
        print(f"Total ediciones encontradas: {len(res.ediciones)}")
        
        if not res.ediciones:
            print(f"No se encontraron ediciones para {mes}/{anio}. Probando Febrero...")
            res = client.obtener_ediciones(anio=anio, mes=2)
            print(f"Total ediciones Febrero: {len(res.ediciones)}")

        # Mostrar las 5 más recientes del bloque obtenido
        # Las ediciones suelen venir ordenadas por fecha en el sitio
        for e in res.ediciones[:5]:
            imprimir_edicion(e)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")

if __name__ == "__main__":
    test_sonora_po()
