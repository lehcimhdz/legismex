import httpx
from bs4 import BeautifulSoup
import re

url = "https://www.legisver.gob.mx/Inicio.php?p=sesiones"
r = httpx.get(url, verify=False)
soup = BeautifulSoup(r.content, "lxml")

def clean_url(href):
    if not href:
        return None
    if "javascript:PDF(" in href:
        m = re.search(r"javascript:PDF\(['\"]([^'\"]+)['\"]\)", href)
        if m:
            path = m.group(1).lstrip("../")
            if not path.startswith("http"):
                return f"https://www.legisver.gob.mx/{path}"
            return path
    elif not href.startswith("http") and href.strip() and href != "#":
        path = href.lstrip("../")
        return f"https://www.legisver.gob.mx/{path}"
    return href

for div_year in soup.select("div.col.s12[id]"):
    year_id = div_year.get("id")
    print(f"\n--- AÑO ID: {year_id} ---")
    table = div_year.find("table")
    if not table: continue
    
    current_periodo = "Sin periodo"
    
    for tr in table.select("tbody tr"):
        tds = tr.find_all("td")
        if not tds: continue
        
        # Header/Periodo
        if len(tds) == 1 and tds[0].has_attr("colspan"):
            current_periodo = tds[0].text.strip()
            print(f"> {current_periodo}")
            continue
        
        # Anexo
        if (len(tds) == 2 and tds[1].has_attr("colspan")) or (len(tds) >= 2 and tds[1].get("colspan", "1") != "1"):
            a_tag = tds[1].find("a")
            if a_tag:
                link = clean_url(a_tag.get("href"))
                texto = a_tag.text.strip()
                print(f"  [Anexo] {texto[:60]}... -> {link}")
            continue
        
        # Fila de Sesion normal
        if len(tds) >= 8:
            td_text = tds[0].text.strip()
            if not td_text:
                continue
            fecha = td_text
            sesion = tds[1].text.strip()
            gaceta = clean_url(tds[2].find("a")["href"]) if tds[2].find("a") else None
            acta = clean_url(tds[4].find("a")["href"]) if tds[4].find("a") else None
            print(f"[{fecha}] {sesion} | Gaceta: {gaceta} | Acta: {acta}")

