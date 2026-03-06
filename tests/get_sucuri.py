import httpx
import base64

resp = httpx.get("https://congresosanluis.gob.mx/trabajo/trabajo-legislativo/gacetas-parlamentarias", verify=False)
html = resp.text
import re
match = re.search(r"S='([^']+)'", html)
print("S matched:", bool(match))
if match:
    encoded = match.group(1)
    decoded = base64.b64decode(encoded).decode('utf-8')
    print("--- DECODED ---")
    print(decoded)
