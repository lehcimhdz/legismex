#!/usr/bin/env python3
import os
import sys
import glob
import subprocess
import argparse
import time


def print_header(text):
    print(f"\n{'=' * 60}")
    print(f"{text.center(60)}")
    print(f"{'=' * 60}")


def run_script(script_path):
    """Ejecuta un script y devuelve True si fue exitoso (código 0)."""
    print(
        f"Buscando lanzar -> {os.path.basename(script_path)}", end="... ", flush=True)
    start_time = time.time()

    try:
        # Capturamos la salida para no inundar la terminal a menos que haya error
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=60  # Timeout de 60s por script
        )
        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ OK ({elapsed:.1f}s)")
            return True, result.stdout
        else:
            print(f"❌ ERROR ({elapsed:.1f}s)")
            print("-" * 40)
            # Solo los últimos 500 caracteres del error
            print(result.stderr.strip()[-500:])
            print("-" * 40)
            return False, result.stderr

    except subprocess.TimeoutExpired:
        print("⏱️  TIMEOUT (Tomó más de 60s)")
        return False, "TimeoutExpired"
    except Exception as e:
        print(f"🔥 FALLO DE EJECUCIÓN: {e}")
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(
        description="Unificador de Pruebas Legismex 🇲🇽")
    parser.add_argument(
        "--estado", type=str, help="Nombre del estado a verificar (ej. 'oaxaca', 'nuevoleon').")
    parser.add_argument("--modulo", type=str, choices=[
                        "congreso", "po"], help="Verificar solo el 'congreso' o el 'po' del estado.")
    parser.add_argument("--all", action="store_true",
                        help="CUIDADO: Ejecuta las pruebas de TODOS los estados (puede demorar minutos).")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Muestra la salida completa de los scripts exitosos.")

    args = parser.parse_args()

    if not (args.estado or args.all):
        parser.print_help()
        sys.exit(1)

    # Buscar archivos de prueba
    test_dir = os.path.join(os.path.dirname(__file__), "tests")

    if not os.path.exists(test_dir):
        print(f"Error: No se encontró el directorio de pruebas: {test_dir}")
        sys.exit(1)

    pattern = "verify_*.py"
    if args.estado:
        if args.modulo:
            pattern = f"verify_{args.estado.lower()}_{args.modulo}.py"
        else:
            pattern = f"verify_{args.estado.lower()}*.py"

    search_path = os.path.join(test_dir, pattern)
    scripts = sorted(s for s in glob.glob(search_path) if "verify_all.py" not in s)

    if not scripts:
        print(f"⚠️  No se encontraron pruebas para el patrón: {pattern}")
        sys.exit(0)

    print_header(
        f"🤖 Ejecutando Verificaciones Legismex ({len(scripts)} scripts)")

    resultados = {"ok": 0, "fail": 0}
    failed_scripts = []

    for script in scripts:
        success, output = run_script(script)
        if success:
            resultados["ok"] += 1
            if args.verbose:
                print(output)
        else:
            resultados["fail"] += 1
            failed_scripts.append(os.path.basename(script))

    print_header("📊 RESUMEN FINAL")
    print(f"Total ejecutados: {len(scripts)}")
    print(f"✅ Exitosos: {resultados['ok']}")
    print(f"❌ Fallidos: {resultados['fail']}")

    if failed_scripts:
        print("\nScripts con fallos:")
        for fs in failed_scripts:
            print(f"  - {fs}")

        sys.exit(1)
    else:
        print("\n🎉 ¡Todo parece funcionar correctamente!")
        sys.exit(0)


if __name__ == "__main__":
    main()
