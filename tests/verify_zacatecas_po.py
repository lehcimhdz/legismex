import asyncio
from legismex import ZacatecasPoClient

async def run_tests():
    print("==================================")
    print("VERIFICANDO ZACATECAS PO")
    print("==================================\n")

    client = ZacatecasPoClient()

    # 1. Periódicos Ordinarios
    fecha_ini = "2026-03-01"
    fecha_fin = "2026-03-31"
    print(f"--- 1. Ordinarios ({fecha_ini} a {fecha_fin}) ---")
    ordinarios = await client.a_obtener_ediciones(fecha_ini, fecha_fin)
    print(f"Búsqueda inicial: {len(ordinarios)} resultados.")
    if ordinarios:
        primero = ordinarios[0]
        print(f"Primero: {primero.nombre_archivo} | ID: {primero.object_id}")
        print(f"URL PDF: {primero.url_pdf}")
        print(f"Tomo: {primero.tomo} | Volumen: {primero.volumen}")
    print("\n")

    # 2. Suplementos
    print("--- 2. Suplementos ---")
    suplementos = await client.a_buscar_suplementos()
    print(f"Total suplementos recuperados: {len(suplementos)}")
    if suplementos:
        sup = suplementos[0]
        print(f"Primero: {sup.fecha_publicacion} | ID: {sup.object_id}")
        print(f"Título: {sup.titulo[:60]}...")
        print(f"URL PDF: {sup.url_pdf}")
    print("\n")

    # 3. Leyes
    print("--- 3. Leyes ---")
    leyes = await client.a_buscar_leyes()
    print(f"Total leyes recuperadas: {len(leyes)}")
    if leyes:
        ley = leyes[0]
        print(f"Primero: {ley.fecha_publicacion} | ID: {ley.object_id}")
        print(f"Descripción: {ley.descripcion}")
        print(f"URL PDF: {ley.url_pdf}")
    print("\n")

    # 4. Reglamentos (Síncrono para probar ambas modalidades)
    print("--- 4. Reglamentos (Síncrono) ---")
    reglamentos = client.obtener_reglamentos()
    print(f"Total reglamentos recuperados: {len(reglamentos)}")
    if reglamentos:
        reg = reglamentos[0]
        print(f"Primero: {reg.fecha_publicacion} | ID: {reg.object_id}")
        print(f"Descripción: {reg.descripcion}")
    print("\n")

    # 5. Códigos (Síncrono)
    print("--- 5. Códigos (Síncrono) ---")
    codigos = client.obtener_codigos()
    print(f"Total códigos recuperados: {len(codigos)}")
    if codigos:
        cod = codigos[0]
        print(f"Primero: {cod.fecha_publicacion} | ID: {cod.object_id}")
        print(f"Descripción: {cod.descripcion}")
    print("\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
