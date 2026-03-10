import time
from legismex.nuevoleon import NuevoLeonClient


def test():
    print("Testing Nuevo Leon Client...")

    start = time.time()
    client = NuevoLeonClient()

    iniciativas = client.obtener_iniciativas()
    end = time.time()

    print(
        f"Successfully downloaded and completely parsed {len(iniciativas)} records in {end-start:.2f} seconds!")

    if iniciativas:
        print("\\nFirst item (Most recent):")
        first = iniciativas[0]
        for key, value in first.model_dump().items():
            print(f"  {key}: {value}")

        print("\\nLast item (Oldest snippet):")
        last = iniciativas[-1]
        for key, value in last.model_dump().items():
            print(f"  {key}: {value}")

    print("\\n\\nTesting filter by Legislature = LXXV")
    iniciativas_lxxv = client.obtener_iniciativas(legislatura="LXXV")
    print(f"Total entries for LXXV: {len(iniciativas_lxxv)}")


if __name__ == "__main__":
    test()
