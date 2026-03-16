import os, re

css_dir = 'app/static/css'
style = open(f'{css_dir}/style.css').read()
imports = re.findall(r"@import\s+'([^']+)'", style)

print(f"{'FILE':<45} {'EXISTS':>8} {'SIZE':>8} {'SYNTAX_OK':>10}")
print("-" * 75)

for imp in imports:
    path = os.path.join(css_dir, imp)
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    if exists:
        try:
            content = open(path).read()
            # Simple syntax check: count braces
            opens = content.count('{')
            closes = content.count('}')
            ok = "OK" if opens == closes else f"MISMATCH {opens}/{closes}"
        except Exception as e:
            ok = f"ERR: {e}"
    else:
        ok = "MISSING"
    print(f"{imp:<45} {str(exists):>8} {size:>8} {ok:>10}")
