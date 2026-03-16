f = open('app/static/css/output.css').read()
i = f.find('glass-card')
print("=== .glass-card snippet ===")
print(f[i:i+250])
print()
print("=== backdrop-blur values found ===")
import re
matches = re.findall(r'backdrop-blur:[^;}{]{1,80}', f)
for m in matches[:5]:
    print(m)
