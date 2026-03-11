import os
import glob
import subprocess
import sys
import time
from typing import List, Tuple

def run_verification_scripts():
    """
    Busca y ejecuta todos los archivos tests/verify_*.py y reporta su estado.
    """
    scripts = glob.glob("tests/verify_*.py")
    scripts = [s for s in scripts if "verify_all.py" not in s]
    scripts.sort()

    total = len(scripts)
    passed = 0
    failed = []

    print(f"🚀 Iniciando Auditoría Masiva de Legismex ({total} estados/scripts)...")
    print("=" * 70)
    print(f"{'ESTADO / SCRIPT':<45} | {'STATUS':<10}")
    print("-" * 70)

    for script in scripts:
        script_name = os.path.basename(script).replace("verify_", "").replace(".py", "").capitalize()
        
        start_time = time.time()
        try:
            # Ejecutamos con un timeout de 60 segundos por si algún sitio del gobierno está colgado
            result = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
                timeout=60
            )
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"{script_name:<45} | ✅ PASS ({duration:.1f}s)")
                passed += 1
            else:
                print(f"{script_name:<45} | ❌ FAIL ({duration:.1f}s)")
                # Extraer la última línea del error para el reporte
                error_msg = result.stderr.strip().split('\n')[-1] if result.stderr else "Error desconocido"
                failed.append((script_name, error_msg))
                
        except subprocess.TimeoutExpired:
            print(f"{script_name:<45} | ⏳ TIMEOUT")
            failed.append((script_name, "Timeout de 60s excedido"))
        except Exception as e:
            print(f"{script_name:<45} | 🛑 ERROR")
            failed.append((script_name, str(e)))

    print("=" * 70)
    print(f"📊 RESUMEN FINAL: {passed}/{total} Pasaron")
    
    if failed:
        print("\n❌ DETALLE DE FALLOS:")
        for name, err in failed:
            print(f"  - {name}: {err}")
        sys.exit(1)
    else:
        print("\n✨ ¡Todos los estados están operacionales!")
        sys.exit(0)

if __name__ == "__main__":
    # Asegurarnos de estar en la raíz del repo
    if not os.path.exists("src/legismex"):
        print("Error: Ejecuta este script desde la raíz del repositorio.")
        sys.exit(1)
        
    run_verification_scripts()
