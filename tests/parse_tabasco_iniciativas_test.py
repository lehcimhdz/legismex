import asyncio
import httpx
from bs4 import BeautifulSoup

async def main():
    url = "https://congresotabasco.gob.mx/iniciativas/"
    
    async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        table = soup.find("table")
        if table:
            rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
            print(f"Total rows found: {len(rows)}")
            if rows:
                print("--- FIRST ROW ---")
                cols = [td.get_text(separator=' ', strip=True) for td in rows[0].find_all("td")]
                print(" | ".join(cols))
                
                print("--- LAST ROW ---")
                cols = [td.get_text(separator=' ', strip=True) for td in rows[-1].find_all("td")]
                print(" | ".join(cols))
                
                # Check for PDF links in first row
                tds = rows[0].find_all("td")
                if len(tds) >= 8:
                    a_tag = tds[7].find("a")
                    if a_tag:
                        print(f"First row PDF: {a_tag['href']}")
                        
                # Check if there's any pagination controls rendered in HTML
                pagination = soup.find("div", class_="dataTables_paginate")
                print(f"Pagination HTML: {pagination is not None}")
                
if __name__ == "__main__":
    asyncio.run(main())
