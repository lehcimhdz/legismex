import httpx
from bs4 import BeautifulSoup


def analyze_historico():
    url = "http://periodicooficial.campeche.gob.mx/sipoec/public/historico"
    print(f"Fetching {url}...")

    with httpx.Client(timeout=30.0, verify=False) as client:
        response = client.get(url)
        print("Status code:", response.status_code)

        soup = BeautifulSoup(response.text, "html.parser")

        # Opciones de formulario o tablas de años?
        forms = soup.find_all("form")
        for i, form in enumerate(forms):
            print(f"\n--- Formulario {i} ---")
            print("Action:", form.get("action"))
            print("Method:", form.get("method"))
            inputs = form.find_all(["input", "select"])
            for inp in inputs:
                print(
                    f"  Input: {inp.get('name')} | Type: {inp.get('type') or inp.name} | Value: {inp.get('value')}")

        # Hay alguna tabla visible al cargar?
        tables = soup.find_all("table")
        print(f"\nFound {len(tables)} tables.")
        if tables:
            rows = tables[0].find_all("tr")
            print(f"Table 0 has {len(rows)} rows.")
            for row in rows[:5]:
                print([c.get_text(strip=True)
                      for c in row.find_all(["th", "td"])])


def test_documentos_anio(anio, page=1):
    url = f"http://periodicooficial.campeche.gob.mx/sipoec/public/documentos?anio={anio}&page={page}"
    print(f"\nFetching {url}...")
    with httpx.Client(timeout=30.0, verify=False) as client:
        response = client.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Encontrar los resultados. En el ejemplo parece que están en una tabla o en rows.
        # Vamos a buscar todos los anchors con data-id
        links = soup.find_all("a", {"data-toggle": "modal"})
        docs_parsed = {}
        for link in links:
            doc_id = link.get("data-id")
            text = link.get_text(separator=" | ", strip=True)
            if doc_id not in docs_parsed:
                docs_parsed[doc_id] = []
            docs_parsed[doc_id].append(text)

        print(
            f"Documentos encontrados en la pagina {page}: {len(docs_parsed)}")
        for doc_id, fields in list(docs_parsed.items())[:3]:
            print(f"  ID: {doc_id} -> {fields}")

        # Paginacion
        pagination = soup.find("ul", class_="pagination")
        if pagination:
            page_items = pagination.find_all("li", class_="page-item")
            print("Paginación hallada:")
            for p in page_items:
                a_tag = p.find("a")
                if a_tag:
                    print(
                        f"  Href: {a_tag.get('href')} | Text: {a_tag.get_text(strip=True)}")
                else:
                    print(
                        f"  Text: {p.get_text(strip=True)} (Active/Disabled)")


def test_pdf_url_inference():
    # ID: 5450 -> ['PO2607PS04032026', '2026-03-04']
    filename = "PO2607PS04032026.pdf"
    date_str = "2026-03-04"
    year, month, _ = date_str.split("-")
    folder = f"{year}{month}"

    inferred_url = f"http://periodicooficial.campeche.gob.mx/sipoec/public/periodicos/{folder}/{filename}"
    print(f"Inferred URL: {inferred_url}")

    with httpx.Client(verify=False) as client:
        resp = client.head(inferred_url)
        print(f"HEAD Status: {resp.status_code}")

    # Test second
    # ID: 5361 -> ['PO2567SS31122025', '2025-12-31']
    filename2 = "PO2567SS31122025.pdf"
    folder2 = "202512"
    inferred_url2 = f"http://periodicooficial.campeche.gob.mx/sipoec/public/periodicos/{folder2}/{filename2}"
    print(f"\nInferred URL 2: {inferred_url2}")

    with httpx.Client(verify=False) as client:
        resp2 = client.head(inferred_url2)
        print(f"HEAD Status 2: {resp2.status_code}")


if __name__ == "__main__":
    test_pdf_url_inference()
    # test_documentos_anio("2026", 1)
    # test_documentos_anio("2025", 1)
