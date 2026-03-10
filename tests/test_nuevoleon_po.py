import time
from legismex.nuevoleon_po import NuevoLeonPoClient


def test():
    print("Testing Nuevo Leon Periódico Oficial Client...")

    start = time.time()
    client = NuevoLeonPoClient()

    ediciones = client.obtener_ediciones_recientes()
    end = time.time()

    print(
        f"Successfully downloaded and completely parsed {len(ediciones)} records in {end-start:.2f} seconds!")

    if ediciones:
        print("\\nFirst item (Most recent):")
        first = ediciones[0]
        for key, value in first.model_dump().items():
            print(f"  {key}: {value}")

        print("\\nLast item (Oldest snippet in table):")
        last = ediciones[-1]
        for key, value in last.model_dump().items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    test()
