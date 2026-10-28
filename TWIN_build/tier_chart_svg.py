# One-picture CEO summary (pure-Python SVG, no matplotlib): Indonesian accounts on each reaction's product GP/kg ladder, YTD Sep-26
# Usage: python tier_chart_svg.py <dir with tdc_cust_rx.csv> <out.svg> [<out.html>]
import sys, csv, math, html
S, OUT = sys.argv[1], sys.argv[2]; OUT_HTML = sys.argv[3] if len(sys.argv) > 3 else None
FLOOR = {'PO-XL': 4.0, 'XL': 2.0, 'PO': 4.0, 'AC': 7.0, 'Others': 4.0}
TARGET = {'PO-XL': 6.0, 'XL': 3.2, 'PO': 5.5, 'AC': 9.5, 'Others': 6.0}
CAP = {'PO-XL': 2000, 'XL': 750, 'PO': 800, 'AC': 250, 'Others': 600}
RX = ['PO-XL', 'XL', 'PO', 'AC', 'Others']
SHORT = {'PT.INDO ASIA TIRTA MANUNGGAL': 'Indo Asia Tirta', 'PT. CHAROEN POKPHAND INDONESIA': 'CP Indonesia', 'PT. JAPFA FOOD INDONESIA GEDUNG GRAHA PRABA SAMANTA': 'Japfa',
         'PT. SO GOOD FOOD GEDUNG GRAHA PRABA SAMANTA': 'So Good Food', 'PT THAI WAH INDONESIA': 'TWIN (interco)'}
rows = [r for r in csv.DictReader(open(f'{S}/tdc_cust_rx.csv', encoding='utf-8')) if r['reaction'] in RX]
for r in rows:
    r['t'] = float(r['tons_ytd26']); r['gp'] = (float(r['ns_thb']) - float(r['product_cost'])) / (r['t'] * 1000) if r['t'] else None; r['indo'] = r['indonesia'] == '1'
W, H = 1500, 660; LEFT, TOP, BOT = 60, 150, 100; GAP = 26
PW = (W - LEFT - 20 - GAP * (len(RX) - 1)) / len(RX); PH = H - TOP - BOT
GREY, INDO, DARK, LINE = '#b8bcc2', '#e4572e', '#14213d', '#6b7280'
FONT = "font-family='Arial, Helvetica, sans-serif'"
def esc(t): return html.escape(str(t))
out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><rect width='{W}' height='{H}' fill='white'/>"]
out.append(f"<text x='{LEFT}' y='44' {FONT} font-size='24' font-weight='700' fill='{DARK}'>Indonesia sits at the bottom of the GP/kg ladder in every reaction it buys</text>")
out.append(f"<text x='{LEFT}' y='70' {FONT} font-size='12' fill='{LINE}'>Orange = Indonesian accounts (direct export + PT Thai Wah Indonesia intercompany) · grey = all other TDC customers with ≥ 5 t · bubble area = YTD Sep-26 tonnes · bands = HVA tier (red below floor, amber floor–target, green at/above target)</text>")
out.append(f"<text x='{LEFT}' y='88' {FONT} font-size='12' fill='{LINE}'>Product GP per kg = net sales − actual cost − F&amp;I (same basis as the HVA GP tier tracker) · YTD Jan–Sep 2026 · source: TDC Profitability data_Actual</text>")
def rad(t): return 4 + 22 * math.sqrt(t / 2500)
for k, g in enumerate(RX):
    x0 = LEFT + k * (PW + GAP)
    rs = [r for r in rows if r['reaction'] == g and r['t'] >= 5 and r['gp'] is not None]
    tot = sum(r['t'] for r in rows if r['reaction'] == g); indo_t = sum(r['t'] for r in rows if r['reaction'] == g and r['indo']); util = tot / (CAP[g] * 9)
    ymin = min(-1.0, min(r['gp'] for r in rs) - 0.5); ymax = max(TARGET[g] + 4, min(max(r['gp'] for r in rs), 18) + 1.5)
    sy = lambda v: TOP + (ymax - max(ymin, min(ymax, v))) / (ymax - ymin) * PH
    out.append(f"<rect x='{x0}' y='{sy(FLOOR[g])}' width='{PW}' height='{sy(ymin)-sy(FLOOR[g])}' fill='#f6dcd4'/>")
    out.append(f"<rect x='{x0}' y='{sy(TARGET[g])}' width='{PW}' height='{sy(FLOOR[g])-sy(TARGET[g])}' fill='#fbf0c6'/>")
    out.append(f"<rect x='{x0}' y='{sy(ymax)}' width='{PW}' height='{sy(TARGET[g])-sy(ymax)}' fill='#e2efda'/>")
    for v in range(int(math.ceil(ymin)), int(ymax) + 1, 2):
        out.append(f"<line x1='{x0}' x2='{x0+PW}' y1='{sy(v)}' y2='{sy(v)}' stroke='white' stroke-width='1'/><text x='{x0-6}' y='{sy(v)+4}' {FONT} font-size='10' fill='{LINE}' text-anchor='end'>{v}</text>")
    out.append(f"<line x1='{x0}' x2='{x0+PW}' y1='{sy(FLOOR[g])}' y2='{sy(FLOOR[g])}' stroke='{LINE}' stroke-width='1.2' stroke-dasharray='5 4'/>")
    out.append(f"<line x1='{x0}' x2='{x0+PW}' y1='{sy(TARGET[g])}' y2='{sy(TARGET[g])}' stroke='{LINE}' stroke-width='1.2' stroke-dasharray='2 3'/>")
    out.append(f"<text x='{x0+4}' y='{sy(FLOOR[g])-3}' {FONT} font-size='10' fill='{LINE}'>floor {FLOOR[g]:.1f}</text>")
    out.append(f"<text x='{x0+4}' y='{sy(TARGET[g])-3}' {FONT} font-size='10' fill='{LINE}'>target {TARGET[g]:.1f}</text>")
    out.append(f"<text x='{x0+PW/2}' y='{TOP-26}' {FONT} font-size='15' font-weight='700' fill='{DARK}' text-anchor='middle'>{g}</text>")
    out.append(f"<text x='{x0+PW/2}' y='{TOP-9}' {FONT} font-size='11' fill='{LINE}' text-anchor='middle'>{tot:,.0f} t · Indonesia {indo_t/tot*100:.0f}%</text>")
    others = sorted([r for r in rs if not r['indo']], key=lambda r: -r['t'])
    for i, r in enumerate(others):
        cx = x0 + PW * (0.12 + 0.76 * ((i * 0.6180339887) % 1.0)); cy = sy(r['gp'])
        out.append(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{rad(r['t']):.1f}' fill='{GREY}' fill-opacity='0.75' stroke='white' stroke-width='0.8'/>")
    ids = sorted([r for r in rs if r['indo']], key=lambda r: -r['t'])
    labels = []
    for i, r in enumerate(ids):
        cx = x0 + PW * (0.3 if len(ids) == 1 else 0.18 + 0.28 * i / (len(ids) - 1)); cy = sy(r['gp']); rr = rad(r['t'])
        out.append(f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{rr:.1f}' fill='{INDO}' fill-opacity='0.9' stroke='{DARK}' stroke-width='1'/>")
        labels.append((cx, cy, rr, SHORT.get(r['customer'], r['customer'][:16]), r['gp'], r['t']))
    # labels: stacked at the right of the bubbles in GP order, pushed apart vertically, with leader lines
    labels.sort(key=lambda l: -l[1])  # bottom of panel first (largest y); stack upwards into the empty upper zone
    ys = []
    for (cx, cy, rr, nm, gp, t) in labels:
        ty = min(cy, TOP + PH - 8)
        moved = True
        while moved:
            moved = False
            for py in ys:
                if abs(py - ty) < 28: ty = py - 28; moved = True
        ys.append(ty)
    for (cx, cy, rr, nm, gp, t), ty in zip(labels, ys):
        tx = x0 + PW * 0.62
        out.append(f"<line x1='{cx+rr:.1f}' y1='{cy:.1f}' x2='{tx-4:.1f}' y2='{ty-4:.1f}' stroke='{DARK}' stroke-width='0.8' stroke-opacity='0.6'/>")
        out.append(f"<text x='{tx:.1f}' y='{ty:.1f}' {FONT} font-size='11' font-weight='700' fill='{DARK}'>{esc(nm)}</text>")
        out.append(f"<text x='{tx:.1f}' y='{ty+12:.1f}' {FONT} font-size='10' fill='{DARK}'>{gp:.1f} THB/kg · {t:,.0f} t</text>")
    col = INDO if util >= 0.8 else '#2a7d4f'
    out.append(f"<text x='{x0+PW/2}' y='{TOP+PH+22}' {FONT} font-size='12' font-weight='700' fill='{col}' text-anchor='middle'>utilisation {util*100:.0f}% {'(full)' if util >= 0.8 else '(spare)'}</text>")
    out.append(f"<text x='{x0+PW/2}' y='{TOP+PH+38}' {FONT} font-size='10' fill='{LINE}' text-anchor='middle'>{'volume displaces higher-margin business' if util >= 0.8 else 'volume absorbs idle cost (0.6–1.0 THB/kg)'}</text>")
out.append(f"<text x='{LEFT}' y='{H-30}' {FONT} font-size='11' fill='{LINE}'>Read: a full reactor (PO-XL, XL) makes Indonesian volume a displacement of 6–7 THB/kg business, not a fixed-cost play; a spare reactor (PO, AC, Others) can take volume at a floor price but not below it.</text>")
out.append(f"<text x='{LEFT}' y='{H-14}' {FONT} font-size='11' fill='{LINE}'>Capacity per reaction from the Baseline sheet — confirm nameplate with the plant (XL shows above 100%). Floor / target per reaction = HVA GP tier tracker.</text>")
out.append("</svg>")
svg = '\n'.join(out)
open(OUT, 'w', encoding='utf-8').write(svg)
if OUT_HTML: open(OUT_HTML, 'w', encoding='utf-8').write(f"<!doctype html><html><head><meta charset='utf-8'><style>body{{margin:0;background:white}}</style></head><body>{svg}</body></html>")
print('saved', OUT)
