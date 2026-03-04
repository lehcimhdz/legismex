from legismex.edomex_po import EdomexPoClient
import time

def main():
    print("Probando cliente del Periódico Oficial del Estado de México...")
    client = EdomexPoClient()
    
    t0 = time.time()
    ediciones = client.obtener_ediciones_recientes()
    t1 = time.time()
    
    print(f"✅ Se obtuvieron {len(ediciones)} ediciones en {t1-t0:.2f} segundos.\n")
    
    if ediciones:
        primer = ediciones[0]
        print(f"--- Primera Edición: {primer.fecha} ---")
        if primer.url_completa:
            print(f"⭐ Gaceta Completa PDF: {primer.url_completa}")
            
        print(f"Documentos Internos: {len(primer.documentos)}")
        for idx, doc in enumerate(primer.documentos[:3], 1):
            print(f"  {idx}. [{doc.seccion}] {doc.titulo[:60]}... -> {doc.url_pdf}")

if __name__ == "__main__":
    main()
