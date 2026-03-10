from legismex.sanluis_po.client import SanLuisPoClient
from datetime import date, timedelta


def imprimir_documento(d):
    tipo = "AVISO" if d.es_aviso else "DISPOSICIÓN"
    print(f"[{tipo}] {d.autoridad_emisora or 'N/A'}")
    print(f"  > Título: {d.titulo[:100]}...")
    print(f"  > PDF: {d.url_pdf}")


def test_sanluis_po():
    print("=== San Luis Potosí Periódico Oficial ===")
    client = SanLuisPoClient()
    try:
        # Intentar obtener la edición de hace unos días para asegurar que hay datos
        target_date = (date.today() - timedelta(days=5)).isoformat()
        print(f"\n--- Edición del {target_date} ---")
        edicion = client.obtener_edicion_por_fecha(target_date)

        print(f"Total documentos encontrados: {len(edicion.documentos)}")

        if not edicion.documentos:
            print(
                f"No se encontraron documentos para la fecha {target_date}. Probando hoy...")
            edicion = client.obtener_edicion_del_dia()
            print(f"Total documentos hoy: {len(edicion.documentos)}")

        # Mostrar los primeros 5 documentos
        for d in edicion.documentos[:5]:
            imprimir_documento(d)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de P.O.: {exc}")


if __name__ == "__main__":
    test_sanluis_po()
