from legismex.consejeria import ConsejeriaClient
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'src')))


def test_consejeria():
    print("Testing ConsejeriaClient...")
    cliente = ConsejeriaClient(headless=True)

    # Buscamos la gaceta "1811"
    gacetas = cliente.buscar_gacetas(criterio="1811")
    print(f"Total encontradas: {len(gacetas)}")

    for g in gacetas:
        print(
            f"- Fecha: {g.fecha} | Numero: {g.numero} | Tiene PDF: {g.tiene_pdf}")

    if gacetas:
        target = next((g for g in gacetas if g.tiene_pdf), None)
        if target:
            print(f"\\nIniciando descarga de {target.numero}...")
            ruta = cliente.descargar_gaceta(
                target, criterio="1811", ruta_destino="/tmp/gaceta_consejeria.pdf")
            if ruta and os.path.exists(ruta):
                print(
                    f"Archivo guardado exitosamente: {ruta} ({os.path.getsize(ruta)} bytes)")
            else:
                print("Fallo en la descarga.")


if __name__ == "__main__":
    test_consejeria()
