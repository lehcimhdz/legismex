import unittest
import asyncio
from datetime import date
from legismex import SonoraPoClient

class TestSonoraPo(unittest.TestCase):
    def setUp(self):
        self.client = SonoraPoClient()

    def test_obtener_ediciones_2026_enero(self):
        """Prueba la obtención de ediciones de enero 2026."""
        resultado = self.client.obtener_ediciones(2026, mes=1)
        self.assertEqual(resultado.anio, 2026)
        self.assertEqual(resultado.mes, 1)
        self.assertGreater(len(resultado.ediciones), 0)
        
        # Verificar la primera edición (según exploración previa)
        # Jueves 01 de Enero de 2026. CCXVII Edición Especial.
        primera = resultado.ediciones[0]
        self.assertEqual(primera.fecha, date(2026, 1, 1))
        self.assertEqual(primera.edicion_tipo, "Especial")
        self.assertIn("boletin.php?id=", primera.url_pdf)
        print(f"\n[OK] 2026-01: {len(resultado.ediciones)} ediciones encontradas.")

    def test_obtener_ediciones_2025_completo(self):
        """Prueba la obtención de todas las ediciones de 2025."""
        resultado = self.client.obtener_ediciones(2025)
        self.assertEqual(resultado.anio, 2025)
        self.assertIsNone(resultado.mes)
        self.assertGreater(len(resultado.ediciones), 100) # Debería haber muchas
        print(f"[OK] 2025: {len(resultado.ediciones)} ediciones encontradas.")

    def test_async_obtener_ediciones(self):
        """Prueba la versión asíncrona."""
        async def run_test():
            resultado = await self.client.a_obtener_ediciones(2026, mes=1)
            self.assertGreater(len(resultado.ediciones), 0)
        
        asyncio.run(run_test())
        print("[OK] Async test passed.")

if __name__ == "__main__":
    unittest.main()
