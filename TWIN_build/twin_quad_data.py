# Per-customer TWIN data (TDC products only) for the TWIN-customer quadrant in the quadrant artifact (Por 30-Oct)
# periods: y24 = FY2024, y25 = FY2025, p25 = YTD Sep-25, y26 = YTD Sep-26; per period tonnes, TDC-leg product/full GP, TWIN GP, combined product/full GP (THB)
# Usage: python twin_quad_data.py <model.json> <out.json>
import json, sys, collections
M = json.load(open(sys.argv[1], encoding='utf-8'))
R = [r for r in M['rows'] if r['src'] == 'TDC']
def grp(r):
    c = r['country']; l = r['label'].upper()
    if c in ('Heinz', 'Wings'): return c
    if l.startswith('BUMI TIRTA'): return 'Bumi Tirta'
    return 'The rest'
P = {'y24': lambda r: r['y'] == '2024', 'y25': lambda r: r['y'] == '2025', 'p25': lambda r: r['y'] == '2025' and int(r['month'][5:7]) <= 9, 'y26': lambda r: r['y'] == '2026' and int(r['month'][5:7]) <= 9}
C = collections.defaultdict(lambda: {k: [0.0] * 6 for k in P})
G = {}
for r in R:
    k = r['label'].strip(); G[k] = grp(r)
    for pk, f in P.items():
        if f(r):
            a = C[k][pk]; a[0] += r['t']; a[1] += r['tdc_pgp']; a[2] += r['tdc_fgp']; a[3] += r['gp']; a[4] += r['chain_pgp']; a[5] += r['chain_fgp']
out = []
for k, v in C.items():
    if max(v['y25'][0], v['y26'][0], v['y24'][0], v['p25'][0]) < 1: continue
    out.append(dict(name=k, grp=G[k], **{pk: [round(x, 3) for x in v[pk]] for pk in P}))
out.sort(key=lambda d: -max(d['y25'][0], d['y26'][0]))
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False)
for pk in ('y25', 'y26'):
    tot = [sum(d[pk][i] for d in out) for i in range(6)]
    print(pk, f"t {tot[0]:,.0f} | TDC prod {tot[1]/tot[0]/1000:.2f} full {tot[2]/tot[0]/1000:.2f} | TWIN {tot[3]/tot[0]/1000:.2f} | comb prod {tot[4]/tot[0]/1000:.2f} full {tot[5]/tot[0]/1000:.2f} | customers {sum(1 for d in out if d[pk][0]>=1)}")
for d in out[:12]: print(f"  {d['name'][:32]:32} {d['grp']:10} y24 {d['y24'][0]:7,.0f} y25 {d['y25'][0]:7,.0f} p25 {d['p25'][0]:6,.0f} y26 {d['y26'][0]:6,.0f} | TDC26 {d['y26'][1]/max(d['y26'][0],1e-9)/1000:5.2f}")
