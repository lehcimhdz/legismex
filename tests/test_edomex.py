from legismex.edomex import EdomexClient
import time


def main():
    print("Probando cliente de Edomex...")
    client = EdomexClient()

    t0 = time.time()
    gacetas = client.obtener_gacetas()
    t1 = time.time()

    print(f"✅ Se obtuvieron {len(gacetas)} gacetas en {t1-t0:.2f} segundos.")

    if gacetas:
        print("\nEjemplo Primer Registro:")
        print(f"  Número: {gacetas[0].numero}")
        print(f"  Fecha:  {gacetas[0].fecha}")
        print(f"  URL:    {gacetas[0].url_pdf}")

        print("\nEjemplo Último Registro:")
        print(f"  Número: {gacetas[-1].numero}")
        print(f"  Fecha:  {gacetas[-1].fecha}")
        print(f"  URL:    {gacetas[-1].url_pdf}")


if __name__ == "__main__":
    main()
