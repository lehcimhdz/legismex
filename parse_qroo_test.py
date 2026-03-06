import httpx
import json

def test_api():
    base_url = "https://congresoqroo.gob.mx/api/v1"
    
    # 1. Probar el listado mensual (marzo 2026)
    mes = "03"
    anio = "2026"
    url_mes = f"{base_url}/gaceta/?mes={mes}&anio={anio}"
    print(f"Probando {url_mes}")
    
    with httpx.Client(verify=False, timeout=30.0) as client:
        resp = client.get(url_mes)
        print("Status", resp.status_code)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Resultados: {len(data)}")
            if len(data) > 0:
                print("Ejemplo:", json.dumps(data[0], indent=2, ensure_ascii=False))

    # 2. Probar un ID de gaceta especifico qroo nos habia dado el 475
    url_id = f"{base_url}/gaceta/475/doctos"
    print(f"\nProbando {url_id}")
    with httpx.Client(verify=False, timeout=30.0) as client:
        resp = client.get(url_id)
        print("Status", resp.status_code)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Resultados en doctos: {len(data)}")
            if len(data) > 0:
                print("Ejemplo:", json.dumps(data[0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_api()
