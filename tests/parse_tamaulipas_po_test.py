import httpx
from bs4 import BeautifulSoup
import re
from datetime import datetime

html = """
<div class="day">
  <div class="dia text-right">
    3
  </div>
  <a target="_blank" href="http://po.tamaulipas.gob.mx/wp-content/uploads/2026/03/cli-26-030326.pdf">
      <img src="https://po.tamaulipas.gob.mx/wp-content/themes/po-2022/img/pdf2.jpg">
  </a>
  <span class="d-block">Tomo CLI<br>Num. 026<br>
      <a href="http://po.tamaulipas.gob.mx/wp-content/uploads/2026/03/cli-26-030326.pdf" target="_blank">Legislativo</a> - 
      <a href="http://po.tamaulipas.gob.mx/wp-content/uploads/2026/03/cli-26-030326-EV.pdf" target="_blank"><strong>Edición vespertina</strong></a><br>                        
      <a href="http://po.tamaulipas.gob.mx/wp-content/uploads/2026/03/POJ-026-030326.pdf" target="_blank">Judicial</a>                                              
  </span>
</div>
"""

soup = BeautifulSoup(html, "html.parser")
days = soup.find_all("div", class_="day")

for day_div in days:
    dia_div = day_div.find("div", class_="dia")
    if not dia_div:
        continue
    dia_text = dia_div.text.strip()
    if not dia_text.isdigit():
        continue

    dia = int(dia_text)

    span = day_div.find("span", class_="d-block")
    if span:
        # Extraer todo el texto, podríamos buscar 'Tomo' y 'Num.'
        tomo = ""
        numero = ""
        for line in span.strings:
            line = line.strip()
            if line.startswith("Tomo"):
                tomo = line.replace("Tomo", "").strip()
            elif line.startswith("Num."):
                numero = line.replace("Num.", "").strip()

        # Ahora los links
        links = []
        for a in span.find_all("a", href=True):
            titulo = a.text.strip()
            # a veces es empty o imagen si estuviera fuera del span
            links.append({"titulo": titulo, "url": a["href"]})

        print(f"Día {dia} | Tomo: {tomo} | Num: {numero}")
        for link in links:
            print(f"  - {link['titulo']} : {link['url']}")
