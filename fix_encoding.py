data = open('app/static/css/base/typography.css', 'rb').read()
decoded = data.decode('utf-8', 'replace')
open('app/static/css/base/typography.css', 'w', encoding='utf-8').write(decoded)
print("OK - bytes:", len(data), "-> chars:", len(decoded))
# Show first 80 chars
print(repr(decoded[:80]))
