import sys, io

path = "/sessions/rcw-017qtlgu7bfjglrcskkavw2e/mnt/lovely/Daily root dashboard - 27 September 2026.html"
with io.open(path, encoding="utf-8") as f:
    content = f.read()

orig_len = len(content)

replacements = []

# 1. TDC price array
old = '    price:  [4.12, 4.29, 4.17, 4.2, 4.19, 4.12, 4.13, 4.17, 4.17, 4.2, 4.18, 4.22, 4.2, 4.05, 4.2, 4.17, 4.17, 4.06, 4.17, 4.12, 4.24, 4.15, 4.22, 4.25, 4.27, 4.07, 4.21, 4.14, 4.21, null],'
new = '    price:  [4.12, 4.29, 4.17, 4.2, 4.19, 4.12, 4.13, 4.17, 4.17, 4.2, 4.18, 4.22, 4.2, 4.05, 4.2, 4.17, 4.17, 4.06, 4.17, 4.12, 4.24, 4.15, 4.22, 4.25, 4.27, 4.07, 4.21, 4.14, 4.21, 4.11],'
replacements.append((old,new))

# 2. TDC volume array
old = '    volume: [191, 154, 376, 276, 314, 239, 343, 307, 278, 318, 338, 355, 298, 201, 251, 260, 233, 172, 298, 196, 208, 215, 127, 196, 272, 280, 390, 239, 318, null],'
new = '    volume: [191, 154, 376, 276, 314, 239, 343, 307, 278, 318, 338, 355, 298, 201, 251, 260, 233, 172, 298, 196, 208, 215, 127, 196, 272, 280, 390, 239, 318, 169],'
replacements.append((old,new))

# 3. TDC starch array
old = '    starch: [23.77, 25.31, 23.96, 24.67, 24.59, 23.44, 23.4, 23.88, 24.06, 24.13, 24.07, 24.59, 24.22, 23.34, 24.46, 23.83, 23.73, 22.74, 23.64, 24.26, 24.39, 23.65, 23.82, 24.47, 24.7, 22.46, 23.96, 22.76, 23.27, null],'
new = '    starch: [23.77, 25.31, 23.96, 24.67, 24.59, 23.44, 23.4, 23.88, 24.06, 24.13, 24.07, 24.59, 24.22, 23.34, 24.46, 23.83, 23.73, 22.74, 23.64, 24.26, 24.39, 23.65, 23.82, 24.47, 24.7, 22.46, 23.96, 22.76, 23.27, 23.02],'
replacements.append((old,new))

missing = []
for old, new in replacements:
    cnt = content.count(old)
    if cnt != 1:
        missing.append((cnt, old[:80]))
    else:
        content = content.replace(old, new)

if missing:
    print("PROBLEM - not exactly 1 match for:")
    for cnt, snippet in missing:
        print(cnt, snippet)
    sys.exit(1)

with io.open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("OK. len before:", orig_len, "len after:", len(content))
