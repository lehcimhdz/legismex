from legismex.guanajuato.client import GuanajuatoClient


def imprimir_asunto(a):
    print(f"[{a.fecha}] {a.expediente} (Leg. {a.legislatura})")
    print(f"  > Descripción: {a.descripcion[:100]}...")
    print(f"  > Detalle: {a.url_detalle}")


def test_guanajuato_congreso():
    print("=== Guanajuato Congreso ===")
    client = GuanajuatoClient()
    try:
        # Iniciativas
        print("\n--- Iniciativas ---")
        iniciativas = client.obtener_iniciativas(page=1)
        print(f"Obtenidas {len(iniciativas)} iniciativas")
        for i in iniciativas[:3]:
            imprimir_asunto(i)
            print("-" * 20)

        # Puntos de Acuerdo
        print("\n--- Puntos de Acuerdo ---")
        puntos = client.obtener_puntos_de_acuerdo(page=1)
        print(f"Obtenidos {len(puntos)} puntos")
        for p in puntos[:3]:
            imprimir_asunto(p)
            print("-" * 20)

    except Exception as exc:
        print(f"Error en prueba de Congreso: {exc}")


if __name__ == "__main__":
    test_guanajuato_congreso()
