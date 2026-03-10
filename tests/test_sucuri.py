import base64
import re

S = 'dT0nNCcgKyAiZCIgKyAiNiIgKyBTdHJpbmcuZnJvbUNoYXJDb2RlKDQ4KSArICI0IiArIFN0cmluZy5mcm9tQ2hhckNvZGUoNTUpICsgIjAiICsgIjkiICsgJzMnICsgU3RyaW5nLmZyb21DaGFyQ29kZSg1NikgKyAnZCcgKyBTdHJpbmcuZnJvbUNoYXJDb2RlKDU2KSArIFN0cmluZy5mcm9tQ2hhckNvZGUoNTYpICsgU3RyaW5nLmZyb21DaGFyQ29kZSg1MSkgKyAnMScgKyAiNCIgKyAiNCIgKyBTdHJpbmcuZnJvbUNoYXJDb2RlKDUzKSArIFN0cmluZy5mcm9tQ2hhckNvZGUoNTApICsgJzInICsgJzAnICsgJ2InICsgJzAnICsgU3RyaW5nLmZyb21DaGFyQ29kZSg5NykgKyAiNiIgKyBTdHJpbmcuZnJvbUNoYXJDb2RlKDU3KSArIFN0cmluZy5mcm9tQ2hhckNvZGUoNTUpICsgIjAiICsgU3RyaW5nLmZyb21DaGFyQ29kZSgxMDIpICsgU3RyaW5nLmZyb21DaGFyQ29kZSg1MSkgKyAnOScgKyAiNCIgKyAnJztkb2N1bWVudC5jb29raWU9J3MnKyd1JysnYycrJ3UnKydyJysnaScrJ18nKydjJysnbCcrJ28nKyd1JysnZCcrJ3AnKydyJysnbycrJ3gnKyd5JysnXycrJ3UnKyd1JysnaScrJ2QnKydfJysnZicrJzcnKyc0JysnYycrJzYnKycxJysnZCcrJzAnKyc2JysiPSIgKyB1ICsgJztwYXRoPS87bWF4LWFnZT04NjQwMCc7IGxvY2F0aW9uLnJlbG9hZCgpOw=='

decoded = base64.b64decode(S).decode('utf-8')
print("--- Decoded JS ---")
print(decoded)


def evaluate_js_string_concat(expr):
    # evaluate things like '4' + "d" + String.fromCharCode(50)
    result = ""
    parts = expr.split('+')
    for p in parts:
        p = p.strip()
        if p.startswith("'") or p.startswith('"'):
            result += p[1:-1]
        elif 'String.fromCharCode' in p:
            num = int(re.search(r'\d+', p).group())
            result += chr(num)
    return result


# Extract u assignment
u_match = re.search(r"u=([^;]+);", decoded)
if u_match:
    u_expr = u_match.group(1)
    u_val = evaluate_js_string_concat(u_expr)
    print("u =", u_val)

# Extract cookie name
cookie_match = re.search(
    r"document\.cookie=(.+?)\s*\+\s*\"=\"\s*\+\s*u", decoded)
if cookie_match:
    cookie_expr = cookie_match.group(1)
    cookie_name = evaluate_js_string_concat(cookie_expr)
    print("cookie_name =", cookie_name)
