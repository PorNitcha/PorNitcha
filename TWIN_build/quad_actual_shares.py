# TDC quadrant boxes on ACTUAL base-year data (Por 30-Oct, same rule as quadrant artifact v11):
# accounts with own base-year sales >= 5 t (incl. no 2027 plan); Vol share = actual base-year tonnes, GP share = actual base-year product GP, GP/kg actual.
# Quadrant = product GP/t vs floor 4,700 and 2027 plan vs base year (2025 FY / 2026 annualised). Output has the same shape as deck_data.json['tdcq'].
# Usage: python quad_actual_shares.py <HVA_build/quad2.json> <out.json>
import json, sys
D = json.load(open(sys.argv[1], encoding='utf-8'))
MODE = sys.argv[3] if len(sys.argv) > 3 else 'avg'   # 'avg' = base-year average product GP/t (Por 30-Oct), or a number e.g. 4700
isTW = lambda d: 'THAI WAH INDONESIA' in d['name'].upper()
isD = lambda d: (d.get('country') or '').strip() == 'Indonesia' and not isTW(d)
out = {}
for b in ('25', '26'):
    tk, bk, gk = ('t25', 't25', 'gpp25') if b == '25' else ('t26', 't26a', 'gpp26')
    own = [d for d in D if d[gk] is not None and d[tk] >= 5]
    T = sum(d[tk] for d in own); G = sum(d[tk] * d[gk] for d in own)
    FLOOR = G / T if MODE == 'avg' else float(MODE)
    def role(d):
        g = d['t27'] - d[bk]
        return ('grow' if g > 0 else 'protect') if d[gk] >= FLOOR else ('fix' if g > 0 else 'reprice')
    roles = {}
    for r in ('protect', 'grow', 'fix', 'reprice'):
        def part(sel):
            x = [d for d in own if role(d) == r and sel(d)]; t = sum(d[tk] for d in x); g = sum(d[tk] * d[gk] for d in x)
            return dict(v=t / T, g=g / G, kg=(g / t / 1000) if t else None, names=[d['name'] for d in x])
        roles[r] = dict(n=sum(1 for d in own if role(d) == r), nproxy=0, total=part(lambda d: True), direct=part(isD), twin=part(isTW))
    out[b] = dict(base=int(b), totT=T, totG=G / 1e6, floor=FLOOR, roles=roles)
json.dump({'tdcq': out}, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for b in out:
    for r, v in out[b]['roles'].items():
        print(b, r, v['n'], *[f"{k}:{v[k]['v']*100:.1f}/{v[k]['g']*100:.1f}/{'-' if v[k]['kg'] is None else round(v[k]['kg'],1)}" for k in ('total', 'direct', 'twin')])
