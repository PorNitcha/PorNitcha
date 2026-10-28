# Simple 2x2 figure: volume and product-GP contribution 2025 FY -> 2026 Jan-Sep by quadrant role (2025 base), total and Indonesia.
# Inputs: quadrant_artifact_v7.html (DATA = per-account history + 2027 plan), data_actual.csv (whole-book denominators).
# Output: quadrant_evolution_2025_2026.svg / .html (render PNG with Edge headless, see README).
import csv, io, json, re, os
here = os.path.dirname(os.path.abspath(__file__))
t = io.open(os.path.join(here, 'quadrant_artifact_v7.html'), encoding='utf-8').read()
DATA = json.loads(re.search(r'const DATA = (\[.*?\]);', t, re.S).group(1))
FLOOR, MINT = 4700, 100

def f(x):
    try: return float(x or 0)
    except: return 0.0
# whole-book denominators, same filter as quad_v2.py (rows with a reaction group)
book = {'25': [0, 0], '26': [0, 0]}
for r in csv.DictReader(io.open(os.path.join(here, 'data_actual.csv'), encoding='utf-8-sig')):
    if r['Reaction group'] in ('', 'None', '#N/A'): continue
    y = {'Year 2025': '25', 'Year 2026': '26'}.get(r['Year'])
    if not y: continue
    book[y][0] += f(r['Sales Quantity (Tons)'])
    book[y][1] += f(r['Actual Gross Profit (THB)']) + f(r['Idle Cost']) + f(r['PPA']) + f(r['Other Adj'])

isID = lambda d: (d['country'] or '').strip() == 'Indonesia' or 'THAI WAH INDONESIA' in d['name'].upper()
def role(d):
    gp, bt = d['gpp25'], d['t25']
    if gp is None or bt < 5: return 'new'
    g = d['t27'] - bt
    return ('grow' if g > 0 else 'protect') if gp >= FLOOR else ('fix' if g > 0 else 'reprice')

G = {k: {'t25': 0, 't26': 0, 'g25': 0, 'g26': 0, 'n': 0, 'id': {'t25': 0, 't26': 0, 'g25': 0, 'g26': 0, 'n': 0}} for k in ('fix', 'grow', 'protect', 'reprice', 'new', 'other')}
for d in DATA:
    r = role(d) if d['t27'] >= MINT else 'other'
    for tgt in ([G[r]] + ([G[r]['id']] if isID(d) else [])):
        tgt['n'] += 1
        tgt['t25'] += d['t25']; tgt['t26'] += d['t26']
        tgt['g25'] += d['t25'] * (d['gpp25'] or 0); tgt['g26'] += d['t26'] * (d['gpp26'] or 0)
# accounts in TDC history but outside the AP27 book (not in DATA at all) fall into 'other' via the remainder
for y in ('25', '26'):
    G['other']['t' + y] += book[y][0] - sum(G[k]['t' + y] for k in G)
    G['other']['g' + y] += book[y][1] - sum(G[k]['g' + y] for k in G)

pv = lambda k, y, sub=None: (G[k]['id'] if sub else G[k])['t' + y] / book[y][0] * 100
pg = lambda k, y, sub=None: (G[k]['id'] if sub else G[k])['g' + y] / book[y][1] * 100
print('book 2025 %.0f t / %.1f MB   2026 9m %.0f t / %.1f MB' % (book['25'][0], book['25'][1] / 1e6, book['26'][0], book['26'][1] / 1e6))
for k in G:
    print('%-8s n=%3d  vol %4.1f%% -> %4.1f%%   GP %4.1f%% -> %4.1f%%  | Indo n=%d vol %4.1f%% -> %4.1f%%  GP %4.1f%% -> %4.1f%%' % (
        k, G[k]['n'], pv(k, '25'), pv(k, '26'), pg(k, '25'), pg(k, '26'), G[k]['id']['n'], pv(k, '25', 1), pv(k, '26', 1), pg(k, '25', 1), pg(k, '26', 1)))

# ---------- SVG ----------
COL = {'fix': '#eb6834', 'grow': '#2a78d6', 'protect': '#1baf7a', 'reprice': '#8a8f98'}
SOFT = {'fix': '#fdf0ea', 'grow': '#eaf1fb', 'protect': '#e8f7f1', 'reprice': '#f1f2f0'}
SHORT = {'PT.INDO ASIA TIRTA MANUNGGAL': 'Indo Asia Tirta', 'PT. CHAROEN POKPHAND INDONESIA': 'CP Indonesia', 'PT THAI WAH INDONESIA': 'Thai Wah Indonesia',
         'PT. JAPFA FOOD INDONESIA GEDUNG GRAHA PRABA SAMANTA': 'Japfa'}
NAME = {'fix': 'FIX PRICE BEFORE VOLUME', 'grow': 'GROW WITH MARGIN', 'protect': 'PROTECT', 'reprice': 'REPRICE / EXIT'}
FG, FG2, FG3 = '#14213d', '#4b5563', '#8a8f98'
W, H = 1000, 600
cw, ch = 400, 190
x0, y0 = 150, 104
cells = {'protect': (x0, y0), 'grow': (x0 + cw + 10, y0), 'reprice': (x0, y0 + ch + 10), 'fix': (x0 + cw + 10, y0 + ch + 10)}
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif" fill="{FG}">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
     f'<text x="24" y="34" font-size="20" font-weight="600">Volume and product GP contribution by customer role: 2025 → 2026</text>',
     f'<text x="24" y="56" font-size="12.5" fill="{FG2}">Roles on the 2025 base (product GP/t vs floor 4,700; 2027 plan vs 2025 volume). Bars = share of the HVA book: grey 2025 FY, colour 2026 Jan–Sep.</text>',
     f'<text x="24" y="74" font-size="12.5" fill="{FG2}">Indonesia = Indonesian accounts inside the role, on the same denominators. pp = change in share, percentage points.</text>']
# axis captions
s.append(f'<text x="{x0 + cw/2}" y="{y0 - 10}" text-anchor="middle" font-size="11.5" fill="{FG2}" font-weight="600">2027 PLAN FLAT OR DOWN vs 2025</text>')
s.append(f'<text x="{x0 + cw + 10 + cw/2}" y="{y0 - 10}" text-anchor="middle" font-size="11.5" fill="{FG2}" font-weight="600">2027 PLAN GROWING vs 2025</text>')
s.append(f'<text transform="translate({x0 - 14} {y0 + ch/2}) rotate(-90)" text-anchor="middle" font-size="11.5" fill="{FG2}" font-weight="600">PRODUCT GP/t 2025 ≥ 4,700</text>')
s.append(f'<text transform="translate({x0 - 14} {y0 + ch + 10 + ch/2}) rotate(-90)" text-anchor="middle" font-size="11.5" fill="{FG2}" font-weight="600">PRODUCT GP/t 2025 &lt; 4,700</text>')

BARMAX = 60.0  # % -> px scale: 100% = 160px
def bar(x, y, k, a, b, label):
    """one metric row: label, 2025 grey bar, 2026 coloured bar, numbers"""
    out = [f'<text x="{x}" y="{y + 11}" font-size="11.5" fill="{FG2}">{label}</text>']
    bx = x + 34
    out.append(f'<rect x="{bx}" y="{y}" width="{max(a,0)*1.3:.1f}" height="6" fill="#c9cbc6"/>')
    out.append(f'<rect x="{bx}" y="{y + 8}" width="{max(b,0)*1.3:.1f}" height="6" fill="{COL[k]}"/>')
    d = b - a
    col = FG2 if abs(d) < 0.5 else ('#1baf7a' if d > 0 else '#d94a2b')
    out.append(f'<text x="{bx + 112}" y="{y + 11}" font-size="12" font-weight="600" font-family="Consolas, Menlo, monospace">{a:.0f}% → {b:.0f}%</text>')
    out.append(f'<text x="{bx + 206}" y="{y + 11}" font-size="11" fill="{col}" font-family="Consolas, Menlo, monospace">{d:+.0f} pp</text>')
    return out

for k, (cx, cy) in cells.items():
    s.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="6" fill="{SOFT[k]}" stroke="{COL[k]}" stroke-opacity=".45"/>')
    s.append(f'<text x="{cx + 14}" y="{cy + 24}" font-size="13" font-weight="700" fill="{COL[k]}">{NAME[k]}</text>')
    s.append(f'<text x="{cx + cw - 14}" y="{cy + 24}" text-anchor="end" font-size="11" fill="{FG3}">{G[k]["n"]} accounts · 2027 plan {sum(d["t27"] for d in DATA if d["t27"]>=MINT and role(d)==k)/1000:.1f} kt</text>')
    yy = cy + 44
    bx0 = cx + 92
    s.append(f'<text x="{cx + 14}" y="{yy + 11}" font-size="11.5" font-weight="600">Total</text>')
    s += bar(bx0, yy, k, pv(k, '25'), pv(k, '26'), 'Vol')
    s += bar(bx0, yy + 24, k, pg(k, '25'), pg(k, '26'), 'GP')
    s.append(f'<line x1="{cx + 14}" x2="{cx + cw - 14}" y1="{yy + 54}" y2="{yy + 54}" stroke="{COL[k]}" stroke-opacity=".25"/>')
    yy2 = yy + 62
    idn = G[k]['id']['n']
    s.append(f'<text x="{cx + 14}" y="{yy2 + 11}" font-size="11.5" font-weight="600">Indonesia</text>')
    if idn:
        s += bar(bx0, yy2, k, pv(k, '25', 1), pv(k, '26', 1), 'Vol')
        s += bar(bx0, yy2 + 24, k, pg(k, '25', 1), pg(k, '26', 1), 'GP')
        names = ', '.join(sorted(SHORT.get(d['name'], ' '.join(re.sub(r'^PT\.? ?', '', d['name']).title().split()[:3])) for d in DATA if d['t27'] >= MINT and role(d) == k and isID(d)))
        s.append(f'<text x="{bx0 + 34}" y="{yy2 + 54}" font-size="10.5" fill="{FG3}">{idn} account{"s" if idn>1 else ""}: {names}</text>')
    else:
        s.append(f'<text x="{bx0 + 34}" y="{yy2 + 11}" font-size="11.5" fill="{FG3}">no Indonesian account in this role</text>')

# remainder lines + legend
ry = y0 + 2 * ch + 10 + 26
s.append(f'<text x="24" y="{ry}" font-size="11" fill="{FG2}">Outside the four roles: new accounts (no 2025 history) vol {pv("new","25"):.0f}% → {pv("new","26"):.0f}%, GP {pg("new","25"):.0f}% → {pg("new","26"):.0f}%  ·  '
         f'2027 plan under 100 t or not in the plan: vol {pv("other","25"):.0f}% → {pv("other","26"):.0f}%, GP {pg("other","25"):.0f}% → {pg("other","26"):.0f}%</text>')
s.append(f'<text x="24" y="{ry + 17}" font-size="11" fill="{FG2}">HVA book (TDC Profitability data_Actual): 2025 FY {book["25"][0]/1000:.1f} kt / product GP {book["25"][1]/1e6:.0f} MB  ·  2026 Jan–Sep {book["26"][0]/1000:.1f} kt / {book["26"][1]/1e6:.0f} MB.  '
         f'Product GP = net sales − Actual Cost − F&amp;I (before idle, PPA, other adj).</text>')
s.append(f'<text x="24" y="{ry + 34}" font-size="10.5" fill="{FG3}">FP&amp;A, 28 Oct 2026 · companion to the HVA customer quadrant page (2025 base, product GP, floor 4,700, plan ≥ 100 t).</text>')
s.append('</svg>')
svg = '\n'.join(s)
io.open(os.path.join(here, 'quadrant_evolution_2025_2026.svg'), 'w', encoding='utf-8').write(svg)
io.open(os.path.join(here, 'quadrant_evolution_2025_2026.html'), 'w', encoding='utf-8').write(
    f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:#fff}}svg{{display:block}}</style></head><body>{svg}</body></html>')
print('written')
