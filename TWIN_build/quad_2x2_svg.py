# Simple 2x2 (no bubbles): share of 2027 plan volume and GP per quadrant, Total vs Indonesia, on the 2025 and 2026-annualised bases.
# Data = HVA_build/quad2.json (same as the quadrant artifact). GP share = 2027 plan tonnes x base-year product GP/t. Floor 4,700 THB/t, accounts with 2027 plan >= 100 t.
# Usage: python quad_2x2_svg.py <quad2.json> <out.svg> <out.html>
import sys, json, html
Q, OUT, OUT_HTML = sys.argv[1], sys.argv[2], sys.argv[3]
D = json.load(open(Q, encoding='utf-8')); FLOOR = 4700; MINT = 100
def isID(d): return (d.get('country') or '').strip() == 'Indonesia' or 'THAI WAH INDONESIA' in d['name'].upper()
def role(d, base):
    gp = d['gpp25'] if base == 25 else d['gpp26']; bt = d['t25'] if base == 25 else d['t26a']
    if gp is None or not bt: return 'new'
    g = d['t27'] - bt
    if gp >= FLOOR: return 'grow' if g > 0 else 'protect'
    return 'fix' if g > 0 else 'reprice'
def shares(base):
    rows = [d for d in D if d['t27'] >= MINT and d['t27'] > 0]
    gpv = lambda d: ((d['gpp25'] if base == 25 else d['gpp26']) or 0) * d['t27']
    totV = sum(d['t27'] for d in rows); totG = sum(gpv(d) for d in rows)
    out = {}
    for r in ('grow', 'protect', 'fix', 'reprice', 'new'):
        rs = [d for d in rows if role(d, base) == r]; ids = [d for d in rs if isID(d)]
        tv, tg, iv, ig = sum(d['t27'] for d in rs), sum(gpv(d) for d in rs), sum(d['t27'] for d in ids), sum(gpv(d) for d in ids)
        out[r] = dict(v=tv / totV, g=tg / totG, vi=iv / totV, gi=ig / totG, kg=tg / tv / 1000 if tv else None, kgi=ig / iv / 1000 if iv else None, n=len(rs), ni=len(ids), names=[d['name'] for d in ids], twin=[d for d in ids if 'THAI WAH INDONESIA' in d['name'].upper()])
    return out, totV, totG / 1e6
TWIN_KG = {25: 2.98, 26: 1.79}  # TWIN trading GP/kg on TDC products: FY2025 / YTD Sep-26 (TWIN customer profitability model, excl native/sago/fibioca/coarse)
SHORT = {'PT.INDO ASIA TIRTA MANUNGGAL': 'Indo Asia Tirta', 'PT. CHAROEN POKPHAND INDONESIA': 'CP Indonesia', 'PT THAI WAH INDONESIA': 'TWIN (interco)', 'PT. JAPFA FOOD INDONESIA GEDUNG GRAHA PRABA SAMANTA': 'Japfa', 'PT. SO GOOD FOOD GEDUNG GRAHA PRABA SAMANTA': 'So Good Food'}
DARK, LINE, INDO, GREY = '#14213d', '#6b7280', '#e4572e', '#9ca3af'
FILL = {'protect': '#e2efda', 'grow': '#ddebf7', 'fix': '#f6dcd4', 'reprice': '#ececec'}
TCOL = {'protect': '#2a7d4f', 'grow': '#1f5f9f', 'fix': '#c0392b', 'reprice': '#6b7280'}
TITLE = {'protect': 'PROTECT', 'grow': 'GROW WITH MARGIN', 'fix': 'FIX PRICE BEFORE VOLUME', 'reprice': 'REPRICE / EXIT'}
FONT = "font-family='Arial, Helvetica, sans-serif'"
W, H = 1500, 720
out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><rect width='{W}' height='{H}' fill='white'/>"]
out.append(f"<text x='50' y='44' {FONT} font-size='24' fill='{DARK}'>Indonesia's role is to leverage fixed cost — so its volume in the fix-price quadrant has to be controlled, not grown</text>")
out.append(f"<text x='50' y='68' {FONT} font-size='12.5' fill='{LINE}'>Share of the 2027 plan · volume = 2027 plan tonnes · GP = 2027 plan tonnes × base-year product GP/t · floor 4,700 THB/t product GP · accounts with a 2027 plan ≥ 100 t</text>")
out.append(f"<text x='50' y='86' {FONT} font-size='12.5' fill='{LINE}'>Indonesia = direct export accounts + PT Thai Wah Indonesia (intercompany) · same data and quadrant rules as the customer quadrant page (HVA AP 2027)</text>")
out.append(f"<text x='50' y='104' {FONT} font-size='12.5' fill='{LINE}'>GP/kg = base-year product GP in THB/kg at TDC level · TWIN (interco) also shown as TDC + TWIN's own trading margin on the same products = combined chain GP/kg</text>")
def pct(x): return f'{x*100:.0f}%' if x >= 0.005 else '–'
def kg(x): return f'{x:.1f}' if x is not None else '–'
def box(x0, y0, w, h, base, label):
    sh, totV, totG = shares(base)
    out.append(f"<text x='{x0+w/2}' y='{y0-14}' {FONT} font-size='16' fill='{DARK}' text-anchor='middle'>{label}</text>")
    cw, ch = w / 2, h / 2
    cells = {'protect': (x0, y0), 'grow': (x0 + cw, y0), 'reprice': (x0, y0 + ch), 'fix': (x0 + cw, y0 + ch)}
    for r, (cx, cy) in cells.items():
        s = sh[r]
        out.append(f"<rect x='{cx}' y='{cy}' width='{cw}' height='{ch}' fill='{FILL[r]}' stroke='white' stroke-width='3'/>")
        out.append(f"<text x='{cx+14}' y='{cy+24}' {FONT} font-size='13' font-weight='700' fill='{TCOL[r]}'>{TITLE[r]}</text>")
        out.append(f"<text x='{cx+14}' y='{cy+40}' {FONT} font-size='10.5' fill='{LINE}'>{s['n']} accounts</text>")
        # mini table
        tx = cx + 18; ty = cy + 66
        out.append(f"<text x='{tx+100}' y='{ty}' {FONT} font-size='11' fill='{LINE}' text-anchor='middle'>Vol</text><text x='{tx+165}' y='{ty}' {FONT} font-size='11' fill='{LINE}' text-anchor='middle'>GP</text><text x='{tx+240}' y='{ty}' {FONT} font-size='11' fill='{LINE}' text-anchor='middle'>GP/kg</text>")
        out.append(f"<line x1='{tx}' x2='{tx+275}' y1='{ty+6}' y2='{ty+6}' stroke='{LINE}' stroke-width='0.8'/>")
        out.append(f"<text x='{tx}' y='{ty+26}' {FONT} font-size='13' fill='{DARK}'>Total</text><text x='{tx+100}' y='{ty+26}' {FONT} font-size='13' fill='{DARK}' text-anchor='middle'>{pct(s['v'])}</text><text x='{tx+165}' y='{ty+26}' {FONT} font-size='13' fill='{DARK}' text-anchor='middle'>{pct(s['g'])}</text><text x='{tx+240}' y='{ty+26}' {FONT} font-size='13' fill='{DARK}' text-anchor='middle'>{kg(s['kg'])}</text>")
        ic = INDO if s['vi'] >= 0.005 else GREY
        out.append(f"<text x='{tx}' y='{ty+48}' {FONT} font-size='13' fill='{ic}'>Indonesia</text><text x='{tx+100}' y='{ty+48}' {FONT} font-size='13' fill='{ic}' text-anchor='middle'>{pct(s['vi'])}</text><text x='{tx+165}' y='{ty+48}' {FONT} font-size='13' fill='{ic}' text-anchor='middle'>{pct(s['gi'])}</text><text x='{tx+240}' y='{ty+48}' {FONT} font-size='13' fill='{ic}' text-anchor='middle'>{kg(s['kgi'])}</text>")
        if s['names']:
            nm = ', '.join(SHORT.get(n, n[:14]) for n in s['names'])
            out.append(f"<text x='{tx}' y='{ty+66}' {FONT} font-size='10' fill='{INDO}'>{html.escape(nm)}</text>")
        for d in s['twin']:
            tdc = (d['gpp25'] if base == 25 else d['gpp26']) / 1000; tw = TWIN_KG[base]
            out.append(f"<text x='{tx}' y='{ty+84}' {FONT} font-size='10.5' fill='{DARK}'>TWIN GP/kg: TDC {tdc:.1f} + TWIN {tw:.1f} = {tdc+tw:.1f} combined</text>")
    # axes labels
    out.append(f"<line x1='{x0+cw}' x2='{x0+cw}' y1='{y0}' y2='{y0+h}' stroke='{DARK}' stroke-width='1.2'/><line x1='{x0}' x2='{x0+w}' y1='{y0+ch}' y2='{y0+ch}' stroke='{DARK}' stroke-width='1.2' stroke-dasharray='5 4'/>")
    out.append(f"<text x='{x0+w/2}' y='{y0+h+18}' {FONT} font-size='11' fill='{LINE}' text-anchor='middle'>← 2027 plan below base-year volume  |  2027 plan above base-year volume →</text>")
    out.append(f"<text transform='translate({x0-12} {y0+h/2}) rotate(-90)' {FONT} font-size='11' fill='{LINE}' text-anchor='middle'>product GP/t above floor ↑   below floor ↓</text>")
    n = sh['new']
    out.append(f"<text x='{x0}' y='{y0+h+36}' {FONT} font-size='10.5' fill='{LINE}'>Not in the four quadrants: {n['n']} accounts with no {('2025' if base == 25 else '2026')} history = {pct(n['v'])} of plan volume" + (f" (Indonesia: {', '.join(SHORT.get(x, x[:14]) for x in n['names'])})" if n['names'] else '') + f" · plan shown {totV:,.0f} t, GP {totG:,.0f} THB m</text>")
box(80, 138, 620, 420, 25, 'Base 2025 actual (FY)')
box(820, 138, 620, 420, 26, 'Base 2026 YTD-Sep, annualised')
# message
out.append(f"<rect x='80' y='620' width='1360' height='60' fill='#fff2cc' stroke='#e4c15a' stroke-width='1'/>")
out.append(f"<text x='96' y='644' {FONT} font-size='13' fill='{DARK}'>Read: on the 2026 base every Indonesian account that has history sits in \"Fix price before volume\" (22% of the 2027 plan volume for 13% of its GP) — none is in Grow or Protect.</text>")
out.append(f"<text x='96' y='666' {FONT} font-size='12.5' fill='{DARK}'>Role for Indonesia = fill otherwise-idle capacity at a floor price. That means a volume cap on the fix-price book (no growth until price is fixed), not a growth target; growth tonnes belong to the Grow quadrant (27% of volume, 59% of GP).</text>")
out.append("</svg>")
svg = '\n'.join(out)
open(OUT, 'w', encoding='utf-8').write(svg)
open(OUT_HTML, 'w', encoding='utf-8').write(f"<!doctype html><html><head><meta charset='utf-8'><style>body{{margin:0;background:white}}</style></head><body>{svg}</body></html>")
print('saved', OUT)
