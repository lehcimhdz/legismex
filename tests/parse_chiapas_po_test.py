import asyncio
import httpx
from bs4 import BeautifulSoup
import re

async def test_paginacion():
    url = "https://www.sgg.chiapas.gob.mx/periodico/periodico2430"
    
    # Requesting without filters to get max pagination
    data = {
        "a": "",
        "m": "",
        "p": "",
        "pg": "1"
    }

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(url, data=data)
        response.raise_for_status()
        html = response.text
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Encuentra link de paginacion máxima
        paginacion_links = soup.find_all("a", href=re.compile(r"javascript:paginacion\(\d+\);"))
        max_page = 1
        for a in paginacion_links:
            match = re.search(r"paginacion\((\d+)\)", a["href"])
            if match:
                page_num = int(match.group(1))
                if page_num > max_page:
                    max_page = page_num
                    
        print(f"La paginación máxima encontrada es: {max_page}")

if __name__ == "__main__":
    asyncio.run(test_paginacion())
