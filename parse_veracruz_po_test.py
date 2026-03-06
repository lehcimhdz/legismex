import httpx
from bs4 import BeautifulSoup

url = "https://editoraveracruz.gob.mx/gacetas/seleccion.php"
data = {"anio": "2024", "mes": "01"}
r = httpx.post(url, data=data, verify=False, follow_redirects=True)

soup = BeautifulSoup(r.content, "lxml")

print("--- Enlaces encontrados ---")
for a in soup.find_all("a", href=True):
    print(a.text.strip(), "->", a["href"])

print("\n--- Eventos onclick ---")
for tag in soup.find_all(attrs={"onclick": True})[:10]:
    print(tag.name, tag.text.strip(), "->", tag["onclick"])
