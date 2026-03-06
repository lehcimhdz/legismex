from legismex.sanluis import SanLuisClient
import time

def test_sanluis_gacetas():
    print("Iniciando prueba de integración: Congreso de San Luis Potosí")
    client = SanLuisClient()
    
    start_time = time.time()
    gacetas = client.obtener_gacetas()
    elapsed = time.time() - start_time
    
    print(f"Total sesiones históricas obtenidas: {len(gacetas)}")
    print(f"Tiempo de respuesta: {elapsed:.2f} segundos")
    print("-" * 50)
    
    if gacetas:
        print("Muestra de las 3 primeras sesiones:")
        for gaceta in gacetas[:3]:
            print(f"[{gaceta.mes}] {gaceta.nombre} | Fecha ISO: {gaceta.fecha_iso} | Fecha Texto: {gaceta.fecha_texto}")
            for url in gaceta.urls_pdf:
                print(f"  PDF Link: {url}")
            print()
            
        print("Muestra de las 3 últimas sesiones (más recientes):")
        for gaceta in gacetas[-3:]:
            print(f"[{gaceta.mes}] {gaceta.nombre} | Fecha ISO: {gaceta.fecha_iso} | Fecha Texto: {gaceta.fecha_texto}")
            for url in gaceta.urls_pdf:
                print(f"  PDF Link: {url}")
            print()
    else:
        print("ERROR: No se obtuvieron gacetas.")

if __name__ == "__main__":
    test_sanluis_gacetas()
