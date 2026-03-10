import logging
import sys
from legismex.puebla.client import PueblaClient

# Configurar logging para ver detalles de Playwright si es necesario
logging.basicConfig(level=logging.INFO)


def imprimir_gaceta(g):
    print(f"[{g.mes}] Gaceta No. {g.numero}")
    print(f"  > Texto: {g.fecha_texto}")
    print(f"  > Año Leg.: {g.anio_legislativo}")
    print(f"  > PDF: {g.url_pdf}")


def test_puebla_congreso():
    print("=== Puebla Congreso (LXII Legislatura) ===")
    print("Nota: Este test utiliza Playwright para evadir Cloudflare. Puede tardar unos segundos...")

    try:
        client = PueblaClient(headless=True)
        gacetas = client.obtener_gacetas_recientes()

        print(f"\nObtenidas {len(gacetas)} gacetas legislativas.")

        if not gacetas:
            print("No se encontraron gacetas. Es posible que la estructura del sitio haya cambiado o Cloudflare haya bloqueado el acceso.")
            return

        # Mostrar las 5 más recientes
        for g in gacetas[:5]:
            imprimir_gaceta(g)
            print("-" * 20)

    except ImportError as e:
        print(f"Error: {e}")
        print("Asegúrate de haber corrido: pip install playwright && playwright install chromium")
    except Exception as exc:
        print(f"Error inesperado en prueba de Puebla: {exc}")


if __name__ == "__main__":
    test_puebla_congreso()
