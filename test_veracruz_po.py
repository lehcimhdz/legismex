import traceback
import httpx
from legismex.veracruz_po import VeracruzPoClient

def test_veracruz_po():
    client = VeracruzPoClient()
    
    print("Obteniendo compendio de tomos de la Gaceta Oficial de Veracruz (Enero de 2024)...")
    try:
        ediciones = client.obtener_ediciones(2024, 1)
        
        print(f"\nTotal de ediciones extraidas: {len(ediciones)}")

        if ediciones:
            print("\n  [ Primeras 10 muestras ]:")
            for e in ediciones[:10]:
                print(f"   * {e.nombre}")
                print(f"     Fecha: {e.fecha_textual}")
                print(f"     URL  : {e.url_pdf}")

            print("\n>> Verificando resolución del PDF de la primera edición...")
            primer_pdf = ediciones[0].url_pdf
            r = httpx.head(primer_pdf, verify=False, follow_redirects=True)
            print(f"Status del Primer PDF: {r.status_code}")
            
    except Exception as e:
        print(f"FAIL :: Error durante la ejecución del test: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_veracruz_po()
