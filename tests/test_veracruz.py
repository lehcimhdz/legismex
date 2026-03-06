from legismex.veracruz import VeracruzClient

def test_veracruz():
    client = VeracruzClient()
    
    print("Obteniendo compendio de gacetas e historial del Congreso de Veracruz...")
    sesiones = client.obtener_gacetas()
    
    print(f"\nTotal sesiones encontradas: {len(sesiones)}")
    
    for ses in sesiones[:4]:
        print(f"\n[{ses.anio_ejercicio} | {ses.periodo}]")
        print(f"{ses.fecha} - {ses.tipo_sesion}")
        
        if ses.gaceta_pdf:
            print(f"  -> Gaceta: {ses.gaceta_pdf}")
        if ses.acta_pdf:
            print(f"  -> Acta: {ses.acta_pdf}")
        if ses.version_estenografica_pdf:
            print(f"  -> V. Estenográfica: {ses.version_estenografica_pdf}")
        
        if ses.audio_urls:
            print(f"  -> Audios ({len(ses.audio_urls)}): {ses.audio_urls[0]}")
        if ses.video_urls:
            print(f"  -> Videos ({len(ses.video_urls)}): {ses.video_urls[0]}")
            
        if ses.anexos:
            print(f"  -> Anexos Adjuntos ({len(ses.anexos)}):")
            for anexo in ses.anexos:
                print(f"     * {anexo.titulo[:80]}...")
                print(f"       DL: {anexo.url_pdf}")


if __name__ == "__main__":
    test_veracruz()
