# Data for the 3-slide Indonesia deck: (1) customer x SN table, (2) TDC 2x2 with Indonesia split Direct / via TWIN, (3) TWIN-customer quadrant 2025 / 2026
# Usage: python deck_data.py <scratchpad dir with tdc_sn.csv + model.json> <HVA_build/quad2.json> <out.json>
import sys, csv, json, re, collections
S, QUAD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
FLOOR_KG = 4.7
def kg(gp, t): return gp / t / 1000 if t else None
# ---------- TDC SN-level (direct + benchmark) ----------
R = list(csv.DictReader(open(f'{S}/tdc_sn.csv', encoding='utf-8')))
for r in R:
    r['t'] = float(r['tons']); r['pgp'] = float(r['ns_thb']) - float(r['af']) - float(r['fi']) - float(r['idle']) - float(r['oadj']) - float(r['ppa']); r['m'] = int(r['month_num']); r['y'] = int(r['year'])
def ytd(rows, y): return [r for r in rows if r['y'] == y and r['m'] <= 9]
def agg(rows): t = sum(r['t'] for r in rows); return dict(t=t, gp=sum(r['pgp'] for r in rows), kg=kg(sum(r['pgp'] for r in rows), t))
SNNAME = {}; SNRX = {}
for r in R: SNNAME.setdefault(r['sn'], r['trade_name'])
# reaction per SN from model.json
M = json.load(open(f'{S}/model.json', encoding='utf-8'))
for r in M['rows']: SNRX.setdefault(r['sn'], r['react'])
RXMAP = {'PO-XL': 'POXL'}
RXFALL = {'SN-365': 'XL', 'SN-028': 'POXL', 'SN-056': 'XL', 'SN-198': 'PO', 'SN-141': 'Others', 'SN-201': 'POXL', 'SN-344': 'POXL', 'SN-093': 'POXL', 'SN-159': 'AC', 'SN-399': 'AC', 'SN-652': 'PO', 'SN-110': 'POXL', 'SN-648': 'MX'}
def rx(sn): return RXMAP.get(SNRX.get(sn, ''), SNRX.get(sn, '')) or RXFALL.get(sn, '')
nonindo = [r for r in R if r['segment'] == 'Non-Indonesia']
def bench(sn): return agg([r for r in ytd(nonindo, 2026) if r['sn'] == sn])
SHORTD = {'PT.INDO ASIA TIRTA MANUNGGAL': 'Indo Asia Tirta', 'PT. CHAROEN POKPHAND INDONESIA': 'CP Indonesia', 'PT. JAPFA FOOD INDONESIA GEDUNG GRAHA PRABA SAMANTA': 'Japfa', 'PT. SO GOOD FOOD GEDUNG GRAHA PRABA SAMANTA': 'So Good Food'}
direct_rows = [r for r in R if r['segment'] == 'Indonesia direct']
_dc = {}
for r in direct_rows:
    c = r['customer'].strip(); _dc.setdefault(c, [0, 0])
    if r['y'] == 2026 and r['m'] <= 9: _dc[c][0] += r['t']
    if r['y'] == 2025 and r['m'] <= 9: _dc[c][1] += r['t']
DIRECT = [(c, SHORTD.get(c, c.title()[:24])) for c, v in sorted(_dc.items(), key=lambda kv: (-kv[1][0], -kv[1][1])) if v[0] > 0 or v[1] > 0]
def cust_block(label, short, rows):
    sns = sorted(set(r['sn'] for r in rows if r['y'] == 2026 or r['y'] == 2025), key=lambda s: -agg([r for r in ytd(rows, 2026) if r['sn'] == s])['t'])
    a25, a26 = agg(ytd(rows, 2025)), agg(ytd(rows, 2026))
    lines = []
    for sn in sns:
        s25, s26 = agg([r for r in ytd(rows, 2025) if r['sn'] == sn]), agg([r for r in ytd(rows, 2026) if r['sn'] == sn])
        if s26['t'] < 30 and s25['t'] < 100 and not (len(sns) == 1): continue
        b = bench(sn)
        lines.append(dict(sn=sn, name=SNNAME.get(sn, sn), rx=rx(sn), t25=s25['t'], t26=s26['t'], kg26=s26['kg'], bt=b['t'], bkg=b['kg'], gap=(s26['kg'] - b['kg']) if (s26['kg'] is not None and b['kg'] is not None) else None))
    # customer-level benchmark = non-Indo on the same SN mix (tonne-weighted by the customer's 2026 tonnes)
    bt = sum(bench(l['sn'])['t'] for l in lines); bgp = sum(bench(l['sn'])['gp'] for l in lines)
    return dict(cust=short, full=label, t25=a25['t'], t26=a26['t'], kg26=a26['kg'], bt=bt, bkg=kg(bgp, bt), gap=(a26['kg'] - kg(bgp, bt)) if a26['kg'] is not None and bt else None, sns=lines)
direct = [cust_block(c, s, [r for r in direct_rows if r['customer'].strip() == c]) for c, s in DIRECT]
d25, d26 = agg(ytd(direct_rows, 2025)), agg(ytd(direct_rows, 2026))
n26 = agg(ytd(nonindo, 2026))
dsn = set(r['sn'] for r in ytd(direct_rows, 2026)); bd = agg([r for r in ytd(nonindo, 2026) if r['sn'] in dsn])
direct_total = dict(t25=d25['t'], t26=d26['t'], kg26=d26['kg'], bt=bd['t'], bkg=bd['kg'], gap=d26['kg'] - bd['kg'])
# ---------- via TWIN (model.json rows, TDC products only) ----------
T = [r for r in M['rows'] if r['src'] == 'TDC']
for r in T: r['m'] = int(r['month'][5:7]); r['yy'] = int(r['y'])
def tagg(rows):
    t = sum(r['t'] for r in rows)
    return dict(t=t, tdc=kg(sum(r['tdc_fgp'] for r in rows), t), twin=kg(sum(r['gp'] for r in rows), t), comb=kg(sum(r['chain_fgp'] for r in rows), t), tdcgp=sum(r['tdc_fgp'] for r in rows), twingp=sum(r['gp'] for r in rows), combgp=sum(r['chain_fgp'] for r in rows),
                ptdc=kg(sum(r['tdc_pgp'] for r in rows), t), pcomb=kg(sum(r['chain_pgp'] for r in rows), t), pcombgp=sum(r['chain_pgp'] for r in rows))
def tytd(rows, y, m=9): return [r for r in rows if r['yy'] == y and r['m'] <= m]
def tfy(rows, y): return [r for r in rows if r['yy'] == y]
def grp(r):
    c = r['country']; l = r['label'].upper()
    if c in ('Heinz', 'Wings'): return c
    if l.startswith('BUMI TIRTA'): return 'Bumi Tirta'
    if l.startswith('HARUM SARI'): return 'Harum Sari'
    return 'The rest'
for r in T: r['grp'] = grp(r)
VIA = ['Heinz', 'Wings', 'Bumi Tirta', 'The rest']
def via_block(g):
    rows = [r for r in T if r['grp'] == g]
    sns = sorted(set(r['sn'] for r in rows), key=lambda s: -tagg([r for r in tytd(rows, 2026) if r['sn'] == s])['t'])
    a25, a26 = tagg(tytd(rows, 2025)), tagg(tytd(rows, 2026))
    lines = []
    for sn in sns:
        s25, s26 = tagg([r for r in tytd(rows, 2025) if r['sn'] == sn]), tagg([r for r in tytd(rows, 2026) if r['sn'] == sn])
        if s26['t'] < 30 and s25['t'] < 100: continue
        b = bench(sn)
        lines.append(dict(sn=sn, name=SNNAME.get(sn, M['sn_name'].get(sn, sn)), rx=rx(sn), t25=s25['t'], t26=s26['t'], tdc=s26['tdc'], twin=s26['twin'], comb=s26['comb'], bt=b['t'], bkg=b['kg'], gap=(s26['tdc'] - b['kg']) if (s26['tdc'] is not None and b['kg'] is not None) else None, gapc=(s26['comb'] - b['kg']) if (s26['comb'] is not None and b['kg'] is not None) else None))
    bt = sum(bench(l['sn'])['t'] for l in lines); bgp = sum(bench(l['sn'])['gp'] for l in lines)
    members = sorted(set(r['label'] for r in rows)); n26 = len(set(r['label'] for r in tytd(rows, 2026)))
    return dict(cust=g, members=members, n26=n26, t25=a25['t'], t26=a26['t'], tdc=a26['tdc'], twin=a26['twin'], comb=a26['comb'], bt=bt, bkg=kg(bgp, bt), gap=(a26['tdc'] - kg(bgp, bt)) if a26['tdc'] is not None and bt else None, gapc=(a26['comb'] - kg(bgp, bt)) if a26['comb'] is not None and bt else None, sns=lines)
via = [via_block(g) for g in VIA]
v25, v26 = tagg(tytd(T, 2025)), tagg(tytd(T, 2026))
vsn = set(r['sn'] for r in tytd(T, 2026)); bv = agg([r for r in ytd(nonindo, 2026) if r['sn'] in vsn])
via_total = dict(t25=v25['t'], t26=v26['t'], tdc=v26['tdc'], twin=v26['twin'], comb=v26['comb'], bt=bv['t'], bkg=bv['kg'], gap=v26['tdc'] - bv['kg'], gapc=v26['comb'] - bv['kg'])
# ---------- TWIN-customer quadrant (groups) ----------
GROUPS = ['Heinz', 'Wings', 'Bumi Tirta', 'Harum Sari', 'The rest']
def twin_quad(base):
    # base 2025: GP/kg FY2025, growth FY2025 vs FY2024; base 2026: GP/kg YTD Sep-26, growth YTD Sep-26 vs YTD Sep-25
    cur = (lambda rows: tfy(rows, 2025)) if base == 25 else (lambda rows: tytd(rows, 2026))
    prev = (lambda rows: tfy(rows, 2024)) if base == 25 else (lambda rows: tytd(rows, 2025))
    allc = tagg(cur(T)); out = []
    for g in GROUPS:
        rows = [r for r in T if r['grp'] == g]; c = tagg(cur(rows)); p = tagg(prev(rows))
        if c['t'] < 1 and p['t'] < 1: continue
        if c['t'] < 1: role = 'exit'
        elif p['t'] < 1: role = 'grow' if (c['ptdc'] or 0) >= FLOOR_KG else 'fix'  # new in base year = volume growing (Por 29-Oct)
        else:
            above = (c['ptdc'] or 0) >= FLOOR_KG; growing = c['t'] > p['t']
            role = ('grow' if growing else 'protect') if above else ('fix' if growing else 'reprice')
        out.append(dict(grp=g, role=role, isnew=p['t'] < 1, t=c['t'], tprev=p['t'], tdc=c['tdc'], twin=c['twin'], comb=c['comb'], ptdc=c['ptdc'], pcomb=c['pcomb'], vshare=c['t'] / allc['t'], gshare=c['pcombgp'] / allc['pcombgp'] if allc['pcombgp'] else None, n=len(set(r['label'] for r in cur(rows)))))
    return dict(base=base, total_t=allc['t'], total_tdc=allc['tdc'], total_twin=allc['twin'], total_comb=allc['comb'], total_ptdc=allc['ptdc'], total_pcomb=allc['pcomb'], groups=out)
twinq = {25: twin_quad(25), 26: twin_quad(26)}
# ---------- TDC 2x2 with Indonesia split ----------
D = json.load(open(QUAD, encoding='utf-8')); FLOOR = 4700; MINT = 0
import os
PROXY = json.load(open(os.path.join(os.path.dirname(QUAD), 'quad2_gp_proxy.json'), encoding='utf-8'))  # TWIN_build/quad_newacct_gp.py
def bgp(d, base): return PROXY[d['name']][str(base)]['gpp']
def bsrc(d, base): return PROXY[d['name']][str(base)]['src']
def isTW(d): return 'THAI WAH INDONESIA' in d['name'].upper()
def isID(d): return (d.get('country') or '').strip() == 'Indonesia' and not isTW(d)
def role(d, base):
    gp = bgp(d, base); bt = (d['t25'] if base == 25 else d['t26a']) or 0
    g = d['t27'] - bt  # no base-year volume = growing (Por 29-Oct: every account in a box)
    if gp >= FLOOR: return 'grow' if g > 0 else 'protect'
    return 'fix' if g > 0 else 'reprice'
SHORT = {'PT.INDO ASIA TIRTA MANUNGGAL': 'Indo Asia Tirta', 'PT. CHAROEN POKPHAND INDONESIA': 'CP Indonesia', 'PT THAI WAH INDONESIA': 'TWIN (interco)', 'PT. JAPFA FOOD INDONESIA GEDUNG GRAHA PRABA SAMANTA': 'Japfa'}
TWIN_KG = {25: 2.98, 26: 1.79}
def tdc_quad(base):
    rows = [d for d in D if d['t27'] > MINT]
    gpv = lambda d: bgp(d, base) * d['t27']
    totV = sum(d['t27'] for d in rows); totG = sum(gpv(d) for d in rows); out = {}
    for r in ('grow', 'protect', 'fix', 'reprice', 'new'):
        rs = [d for d in rows if role(d, base) == r]
        def part(sel):
            x = [d for d in rs if sel(d)]; tv = sum(d['t27'] for d in x); tg = sum(gpv(d) for d in x)
            # GP/kg shown = ACTUAL base-year product GP at ACTUAL base-year tonnes, accounts with own base-year sales only (Por 29-Oct)
            tk, gk = ('t25', 'gpp25') if base == 25 else ('t26', 'gpp26')
            xa = [d for d in x if d[tk] and d[gk] is not None and bsrc(d, base) == 'own']; ta = sum(d[tk] for d in xa)
            return dict(v=tv / totV, g=tg / totG, kg=(sum(d[tk] * d[gk] for d in xa) / ta / 1000) if ta else None, kg_plan=tg / tv / 1000 if tv else None, t_act=ta, names=[SHORT.get(d['name'].strip(), d['name'].strip()[:16]) for d in x])
        tot = part(lambda d: True); di = part(isID); tw = part(isTW)
        tw['twin_kg'] = TWIN_KG[base] if tw['v'] else None
        tw['comb_kg'] = (tw['kg'] + TWIN_KG[base]) if tw['v'] else None
        px = [d for d in rs if bsrc(d, base) != 'own']
        out[r] = dict(n=len(rs), total=tot, direct=di, twin=tw, nproxy=len(px), vproxy=sum(d['t27'] for d in px) / totV)
    return dict(base=base, totV=totV, totG=totG / 1e6, roles=out)
tdcq = {25: tdc_quad(25), 26: tdc_quad(26)}
json.dump(dict(direct=direct, direct_total=direct_total, via=via, via_total=via_total, twinq=twinq, tdcq=tdcq, floor_kg=FLOOR_KG), open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
# ---- print summary ----
def f(x, d=2): return '–' if x is None else f'{x:,.{d}f}'
print('DIRECT');
for c in direct:
    print(f"  {c['cust']}: t25 {f(c['t25'],0)} t26 {f(c['t26'],0)} kg {f(c['kg26'])} | bench {f(c['bt'],0)} t @ {f(c['bkg'])} gap {f(c['gap'])}")
    for l in c['sns']: print(f"     {l['sn']} {l['name'][:22]:22} {l['rx']:6} t25 {f(l['t25'],0):>6} t26 {f(l['t26'],0):>6} kg {f(l['kg26']):>6} | bench {f(l['bt'],0):>6} @ {f(l['bkg']):>6} gap {f(l['gap'])}")
print('  TOTAL', {k: f(v, 0 if k.startswith('t') or k == 'bt' else 2) for k, v in direct_total.items()})
print('VIA TWIN')
for c in via:
    print(f"  {c['cust']} n26={c['n26']} gapc={f(c['gapc'])}: t25 {f(c['t25'],0)} t26 {f(c['t26'],0)} TDC {f(c['tdc'])} TWIN {f(c['twin'])} comb {f(c['comb'])} | bench {f(c['bt'],0)} @ {f(c['bkg'])} gap {f(c['gap'])}")
    for l in c['sns']: print(f"     {l['sn']} {l['name'][:22]:22} {l['rx']:6} t25 {f(l['t25'],0):>6} t26 {f(l['t26'],0):>6} TDC {f(l['tdc']):>6} TWIN {f(l['twin']):>6} comb {f(l['comb']):>6} | bench {f(l['bt'],0):>6} @ {f(l['bkg']):>6} gap {f(l['gap'])}")
print('  TOTAL', {k: f(v, 0 if k in ('t25', 't26', 'bt') else 2) for k, v in via_total.items()})
for b in (25, 26):
    q = twinq[b]; print(f"TWIN QUAD base {b}: total {f(q['total_t'],0)} t TDC {f(q['total_tdc'])} TWIN {f(q['total_twin'])} comb {f(q['total_comb'])}")
    for g in q['groups']: print(f"   {g['grp']:12} {g['role']:8} t {f(g['t'],0):>6} prev {f(g['tprev'],0):>6} pTDC {f(g['ptdc'])} pcomb {f(g['pcomb'])} TDC {f(g['tdc'])} TWIN {f(g['twin'])} comb {f(g['comb'])} vol% {f(g['vshare']*100,0)} GP% {f((g['gshare'] or 0)*100,0)} n {g['n']}")
for b in (25, 26):
    q = tdcq[b]; print(f"TDC QUAD base {b}")
    for r, v in q['roles'].items(): print(f"   {r:8} n {v['n']:3} total v {f(v['total']['v']*100,0)}% g {f(v['total']['g']*100,0)}% kg {f(v['total']['kg'],1)} | direct v {f(v['direct']['v']*100,0)}% g {f(v['direct']['g']*100,0)}% kg {f(v['direct']['kg'],1)} {v['direct']['names']} | twin v {f(v['twin']['v']*100,0)}% g {f(v['twin']['g']*100,0)}% kg {f(v['twin']['kg'],1)} comb {f(v['twin']['comb_kg'],1)}")
