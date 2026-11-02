# Proxy product GP/t for accounts with no actual GP in the base year, so every 2027-plan account can be placed in a quadrant (Por 29-Oct: boxes must add to 100%)
# Rule per account and base year: own base-year GP/t -> own other-year GP/t -> base-year TDC average product GP/t of the SKUs in its AP 2027 plan (all customers) -> reaction average -> TDC average
# Usage: python quad_newacct_gp.py <HVA_build dir> <out.json>
import csv, collections, json, re, sys, openpyxl
HB, OUT = sys.argv[1], sys.argv[2]
def f(x):
    try: return float(x)
    except: return 0.0
def norm(n):
    n = (n or '').upper().replace('BJ.', '').replace('ฟู๊ด', 'ฟู้ด'); n = re.sub(r'[^A-Z0-9ก-๙]+', '', n); return n[:16]
ALIAS = {'HUIFALINXIAFOODS': 'HUIFA', 'QINGDAOMIRACLESU': 'HUIFA', 'QINGDAOMIRACLE': 'HUIFA', 'MORIIFOODSINC': 'MORIIFOODS', 'FOODTRENDANDSUPE': 'FOODTREND'}
key = lambda n: ALIAS.get(norm(n), norm(n))
# base-year product GP/t by SN and by reaction, all TDC customers (2026 = YTD)
sn = {y: collections.defaultdict(lambda: [0.0, 0.0]) for y in ('25', '26')}; rx = {y: collections.defaultdict(lambda: [0.0, 0.0]) for y in ('25', '26')}; tot = {y: [0.0, 0.0] for y in ('25', '26')}
rd = csv.reader(open(f'{HB}/data_actual.csv', encoding='utf-8')); h = next(rd)
I = {n: h.index(n) for n in ('Year', 'SN', 'Reaction group', 'Sales Quantity (Tons)', 'Actual Gross Profit (THB)', 'Idle Cost', 'Other Adj', 'PPA')}
for r in rd:
    y = {'Year 2025': '25', 'Year 2026': '26'}.get(r[I['Year']]); g = r[I['Reaction group']]
    if not y or g in ('', 'None', '#N/A'): continue
    t = f(r[I['Sales Quantity (Tons)']]); gp = f(r[I['Actual Gross Profit (THB)']]) + f(r[I['Idle Cost']]) + f(r[I['Other Adj']]) + f(r[I['PPA']])
    for acc in (sn[y][r[I['SN']]], rx[y][g], tot[y]): acc[0] += t; acc[1] += gp
avg = lambda a: a[1] / a[0] if a[0] > 0 else None
# AP 2027 tonnes by customer x SN (AP + headroom, Jan-Dec 27)
wb = openpyxl.load_workbook(f'{HB}/topline_final_copy.xlsx', read_only=True, data_only=True); ws = wb['data']
mix = collections.defaultdict(lambda: collections.defaultdict(float)); rxof = {}
for i, row in enumerate(ws.iter_rows(min_row=7, values_only=True)):
    name, r_, s_ = row[6], row[10], row[11]
    if not name or not s_: continue
    t = sum(f(v) for v in row[13:37])
    if t <= 0: continue
    mix[key(name)][str(s_).strip()] += t; rxof[str(s_).strip()] = r_
RXMAP = {'POXL': 'PO-XL', 'PO-XL': 'PO-XL'}
D = json.load(open(f'{HB}/quad2.json', encoding='utf-8'))
out = {}
for d in D:
    k = key(d['name']); rec = {}
    for y, oy in (('25', '26'), ('26', '25')):
        own = d['gpp' + y]
        if own is not None and (d['t25'] if y == '25' else d['t26']) >= 5:  # under 5 t = no history (Sajo CPK, IFP, LLC 7 Utra), same rule as the quadrant chart
            rec[y] = dict(gpp=own, src='own'); continue
        if d['gpp' + oy] is not None and (d['t26'] if oy == '26' else d['t25']) >= 5:
            rec[y] = dict(gpp=d['gpp' + oy], src='own_other_year'); continue
        m = mix.get(k)
        if m:
            T = G = 0.0; how = set()
            for s_, t in m.items():
                v = avg(sn[y][s_]) if sn[y][s_][0] >= 5 else None; h_ = 'sku'
                if v is None:
                    rr = RXMAP.get(str(rxof.get(s_) or '').strip(), str(rxof.get(s_) or '').strip()); v = avg(rx[y][rr]) if rr in rx[y] else None; h_ = 'reaction'
                if v is None: v = avg(tot[y]); h_ = 'tdc'
                T += t; G += t * v; how.add(h_)
            rec[y] = dict(gpp=round(G / T), src='proxy_' + '+'.join(sorted(how)))
        else:
            rec[y] = dict(gpp=round(avg(tot[y])), src='proxy_tdc')
    out[d['name']] = rec
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
c = collections.Counter(v[y]['src'] for v in out.values() for y in ('25', '26')); print(c)
for d in sorted(D, key=lambda d: -d['t27'])[:200]:
    r = out[d['name']]
    if r['25']['src'] != 'own' or r['26']['src'] != 'own':
        if d['t27'] >= 300: print(f"{d['name'][:34]:34} t27 {d['t27']:>5} | 25 {r['25']['gpp']:>6} {r['25']['src']:22} | 26 {r['26']['gpp']:>6} {r['26']['src']}")
