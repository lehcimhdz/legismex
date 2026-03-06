from legismex.sanluis_po import SanLuisPoClient

def test_sanluis_po():
    client = SanLuisPoClient()
    
    print("Obteniendo edición del 2026-03-05...")
    edicion = client.obtener_edicion_por_fecha("2026-03-05")
    
    print(f"Fecha consultada: {edicion.fecha}")
    print(f"Total documentos: {len(edicion.documentos)}")
    
    disposiciones = [d for d in edicion.documentos if not d.es_aviso]
    avisos = [d for d in edicion.documentos if d.es_aviso]
    
    print(f" - Disposiciones: {len(disposiciones)}")
    print(f" - Avisos: {len(avisos)}\n")

    for i, doc in enumerate(edicion.documentos, 1):
        if doc.es_aviso:
            print(f"{i}. [AVISO] {doc.titulo}")
        else:
            print(f"{i}. [{doc.nivel_gobierno}] {doc.autoridad_emisora} | {doc.titulo[:80]}...")
        
        print(f"   URL: {doc.url_pdf}\n")

if __name__ == "__main__":
    test_sanluis_po()
