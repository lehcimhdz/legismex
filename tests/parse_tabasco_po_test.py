import asyncio
import httpx
from bs4 import BeautifulSoup

async def main():
    base_url = "https://tabasco.gob.mx/PeriodicoOficial"
    
    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        # Request page 0
        response = await client.get(base_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Parse table
        table = soup.find("table", class_="table-striped")
        if table:
            rows = table.find("tbody").find_all("tr", class_="datos-periodico") if table.find("tbody") else []
            print(f"Total rows on page 0: {len(rows)}")
            
            if rows:
                print("--- FIRST ROW ---")
                tds = rows[0].find_all("td")
                cols = [td.get_text(separator=' ', strip=True) for td in tds]
                # print(" | ".join(cols))
                print(f"Fecha: {cols[0]}")
                print(f"Número: {cols[1]}")
                print(f"Tipo: {cols[2]}")
                print(f"Suplemento: {cols[3]}")
                # For description, sometimes there is a "more" and "morecontent" handling, let's just get stripped text
                desc_text = cols[4].split("Mostrar ↓")[0].strip() if "Mostrar ↓" in cols[4] else cols[4]
                print(f"Desc: {desc_text[:100]}...")
                
                a_tag = tds[5].find("a")
                pdf_url = a_tag["href"] if a_tag else "No PDF"
                print(f"PDF Url: {pdf_url}")
                
        # Parse pagination
        pager = soup.find("ul", class_="pager__items")
        if pager:
            last_link = pager.find("li", class_="pager__item--last")
            if last_link and last_link.find("a"):
                print(f"Last page link: {last_link.find('a')['href']}")

        # Test request page 1
        response_page1 = await client.get(f"{base_url}?page=1")
        response_page1.raise_for_status()
        soup_page1 = BeautifulSoup(response_page1.text, "html.parser")
        rows_page1 = soup_page1.find("table", class_="table-striped").find("tbody").find_all("tr", class_="datos-periodico")
        print(f"\nTotal rows on page 1: {len(rows_page1)}")
        if rows_page1:
            tds = rows_page1[0].find_all("td")
            num = tds[1].get_text(strip=True)
            print(f"First row on page 1 has number: {num}")

if __name__ == "__main__":
    asyncio.run(main())
