import asyncio
import httpx
from bs4 import BeautifulSoup

async def main():
    url = "https://www.congresocam.gob.mx/gaceta/"
    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Look for directory lister wrappers as seen in the HTML snippet
        directory_listers = soup.find_all("div", class_="directory-lister-wrapper")
        print(f"Encontrados {len(directory_listers)} 'directory-lister-wrapper'")
        
        for idx, lister in enumerate(directory_listers):
            print(f"\n--- Lister {idx} ---")
            path = lister.get("mainpath", "Unknown Path")
            print(f"Path: {path}")
            
            files = lister.find_all("a", class_="soubor-link")
            print(f"Archivos encontrados: {len(files)}")
            for file in files[:3]:
                print(f"  - {file.get_text()}: {file.get('href')}")

if __name__ == "__main__":
    asyncio.run(main())
