# Interactive 2x2 page: volume and product-GP contribution by customer role (2025 base) for 2025 FY, 2026 Jan-Sep and the AP2027 plan,
# with a plant filter (Rayong / TKT / both) that applies to the AP2027 bars. Inputs: quadrant_artifact_v7.html (DATA), ap27_plant.json, data_actual.csv.
import csv, io, json, re, os
here = os.path.dirname(os.path.abspath(__file__))
t = io.open(os.path.join(here, 'quadrant_artifact_v7.html'), encoding='utf-8').read()
DATA = json.loads(re.search(r'const DATA = (\[.*?\]);', t, re.S).group(1))
AP = json.load(io.open(os.path.join(here, 'ap27_plant.json'), encoding='utf-8'))
FLOOR, MINT = 4700, 100
def f(x):
    try: return float(x or 0)
    except: return 0.0
book = {'25': [0, 0], '26': [0, 0]}
for r in csv.DictReader(io.open(os.path.join(here, 'data_actual.csv'), encoding='utf-8-sig')):
    if r['Reaction group'] in ('', 'None', '#N/A'): continue
    y = {'Year 2025': '25', 'Year 2026': '26'}.get(r['Year'])
    if not y: continue
    book[y][0] += f(r['Sales Quantity (Tons)']); book[y][1] += f(r['Actual Gross Profit (THB)']) + f(r['Idle Cost']) + f(r['PPA']) + f(r['Other Adj'])
isID = lambda d: (d['country'] or '').strip() == 'Indonesia' or 'THAI WAH INDONESIA' in d['name'].upper()
def role(d):
    if d['t27'] < MINT: return 'other'
    gp, bt = d['gpp25'], d['t25']
    if gp is None or bt < 5: return 'new'
    g = d['t27'] - bt
    return ('grow' if g > 0 else 'protect') if gp >= FLOOR else ('fix' if g > 0 else 'reprice')
rows = []
for d in DATA:
    a = AP.get(d['name'], {'RY': [0, 0], 'TKT': [0, 0]})
    rows.append({'n': d['name'], 'id': 1 if isID(d) else 0, 'r': role(d), 't25': d['t25'], 't26': d['t26'],
                 'g25': round(d['t25'] * (d['gpp25'] or 0)), 'g26': round(d['t26'] * (d['gpp26'] or 0)),
                 'ry': a['RY'][0], 'ryg': a['RY'][1], 'tk': a['TKT'][0], 'tkg': a['TKT'][1]})
# plan lines that matched no DATA account -> 'other' bucket (so plant totals equal the AP sheet)
matched_ry = sum(v['RY'][0] for v in AP.values()); matched_tk = sum(v['TKT'][0] for v in AP.values())
sheet = json.load(io.open(os.path.join(here, 'ap27_plant_totals.json'), encoding='utf-8')) if os.path.exists(os.path.join(here, 'ap27_plant_totals.json')) else None
if sheet:
    rows.append({'n': 'Plan lines not matched to an account', 'id': 0, 'r': 'other', 't25': 0, 't26': 0, 'g25': 0, 'g26': 0,
                 'ry': round(sheet['RY'][0] - matched_ry, 1), 'ryg': round(sheet['RY'][1] - sum(v['RY'][1] for v in AP.values())),
                 'tk': round(sheet['TKT'][0] - matched_tk, 1), 'tkg': round(sheet['TKT'][1] - sum(v['TKT'][1] for v in AP.values()))})
acc_t25 = sum(r['t25'] for r in rows); acc_g25 = sum(r['g25'] for r in rows); acc_t26 = sum(r['t26'] for r in rows); acc_g26 = sum(r['g26'] for r in rows)
# whole-book remainder (TDC accounts outside the AP27 book) -> 'other'
rows.append({'n': 'TDC accounts outside the 2027 plan', 'id': 0, 'r': 'other', 't25': round(book['25'][0] - acc_t25, 1), 't26': round(book['26'][0] - acc_t26, 1),
             'g25': round(book['25'][1] - acc_g25), 'g26': round(book['26'][1] - acc_g26), 'ry': 0, 'ryg': 0, 'tk': 0, 'tkg': 0})

html = io.open(os.path.join(here, 'quad_ap27_template.html'), encoding='utf-8').read()
html = html.replace('/*ROWS*/[]', json.dumps(rows, ensure_ascii=False, separators=(',', ':')))
io.open(os.path.join(here, 'quadrant_ap27_by_plant.html'), 'w', encoding='utf-8').write(html)
# console check
def share(sel, pl):
    tot_t = sum(sel(r)[0] for r in rows); tot_g = sum(sel(r)[1] for r in rows)
    out = {}
    for k in ('fix', 'grow', 'protect', 'reprice', 'new', 'other'):
        rr = [r for r in rows if r['r'] == k]; ii = [r for r in rr if r['id']]
        out[k] = (sum(sel(r)[0] for r in rr) / tot_t * 100, sum(sel(r)[1] for r in rr) / tot_g * 100, sum(sel(r)[0] for r in ii) / tot_t * 100, sum(sel(r)[1] for r in ii) / tot_g * 100)
    return tot_t, tot_g, out
for lab, sel in [('2025', lambda r: (r['t25'], r['g25'])), ('2026', lambda r: (r['t26'], r['g26'])), ('AP27 both', lambda r: (r['ry'] + r['tk'], r['ryg'] + r['tkg'])),
                 ('AP27 RY', lambda r: (r['ry'], r['ryg'])), ('AP27 TKT', lambda r: (r['tk'], r['tkg']))]:
    tt, tg, o = share(sel, lab)
    print('%-9s %6.0f t %6.1f MB | ' % (lab, tt, tg / 1e6) + '  '.join('%s v%2.0f%% g%2.0f%% (ID v%2.0f g%2.0f)' % (k[:4], *o[k]) for k in o))
