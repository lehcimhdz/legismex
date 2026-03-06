import httpx

url2 = "https://www.congresotamaulipas.gob.mx/Parlamentario/RegistroParlamentario/GacetasGlobalPag.aspx?Legislatura=65"
r2 = httpx.get(url2, verify=False, follow_redirects=True)
print(r2.text)
