import csv, re, json, sys
from collections import defaultdict
S = sys.argv[1]
mo = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
def f(x):
    try: return float(x)
    except: return 0.0

# ---------- FX ----------
BOT24 = {1:35.17,2:35.80,3:35.84,4:36.69,5:36.57,6:36.68,7:36.26,8:35.03,9:33.49,10:33.37,11:34.42,12:34.19}  # approx BOT monthly avg (assumption)
usdthb = {}
w = defaultdict(lambda: [0, 0])
tdc_rows = list(csv.DictReader(open(f'{S}/tdc_twin_rows.csv', encoding='utf-8')))
for r in tdc_rows:
    fx = f(r['Exchange Rate']); ns = f(r['Net Sales Revenue (THB)'])
    if fx > 1 and ns > 0:
        k = '%s-%02d' % (r['Year'][-4:], mo[r['Period']]); w[k][0] += fx * ns; w[k][1] += ns
for k, v in w.items(): usdthb[k] = v[0] / v[1]
for m, v in BOT24.items(): usdthb['2024-%02d' % m] = v
usdthb['2025-03'] = 33.642  # Data_Billing wavg (no TDC->TWIN shipment that month)
def fxsrc_of(k):
    if k < '2025': return 'BOT monthly avg (assumption)'
    if k == '2025-03': return 'TDC Data_Billing wavg'
    return 'TDC invoice rate (wavg)'
fxsrc = {k: fxsrc_of(k) for k in usdthb}
idrthb = {}
for r in csv.DictReader(open(f'{S}/twin_rawww_2024.csv', encoding='utf-8')): idrthb[r['Month'][:7]] = f(r['FX'])
for r in csv.DictReader(open(f'{S}/twin_raw_2025on.csv', encoding='utf-8')): idrthb[r['Month'][:7]] = f(r['FX'])
months = sorted(idrthb)
usdidr = {m: usdthb[m] / idrthb[m] for m in months}
BASE_USDTHB = sum(usdthb['2024-%02d' % m] for m in range(1, 13)) / 12
BASE_IDRTHB = sum(idrthb['2024-%02d' % m] for m in range(1, 13)) / 12
BASE_USDIDR = BASE_USDTHB / BASE_IDRTHB

# ---------- product mapping ----------
TDC_MAP = {'Cassflo 500':'SN-028','Cassflo 600':'SN-344','Cassmax 102':'SN-093','Cassflo 11':'SN-110','Cassflo 800':'SN-201','Casstex 22':'SN-365',
 'Amyrose Crisp':'SN-649','Amyrose Bind D':'SN-648','Cassmax 26':'SN-652','Cassmax 23':'SN-198','Cassmax 100':'SN-145','Cassbake 68':'SN-668','Cassflo 24M':'SN-663','Casstex 43':'SN-115'}
SN_NAME = {v: k for k, v in TDC_MAP.items()}
def norm_prod(name, product=''):
    n = (name or '').strip(); p = (product or '').strip(); low = n.lower()
    if low in ('amyrose bind', 'amyrose bind d'): return 'Amyrose Bind D'
    if low in ('amyrose', 'amyrose crisp'): return 'Amyrose Crisp'
    if low.startswith('pregel') or 'pregel' in p.lower(): return 'Pregelatinized'
    if low.startswith('d2201'): return 'D2201'
    if low.startswith('coarse') or 'coarse' in p.lower(): return 'Coarse flour'
    if low.startswith('sago') or 'sago' in p.lower() or 'pearl' in p.lower(): return 'Sago / pearl'
    if 'native' in p.lower() or low in ('native','twin orchid brand','thai flower brand','rose brand twpc','pandan harum brand','twpc brand','cambodia','tapioca','tapioca starch'): return 'Native starch'
    if low.startswith('casstex hf'): return 'Casstex HF 201'
    if low.startswith('cassflo 40'): return 'Cassflo 40'
    if 'csb' in low or 'roseco' in low or 'roseco' in p.lower() or 'biocompost' in p.lower(): return 'Other (CSB/Roseco)'
    if low == '': return (p.strip() or 'Unknown')
    return n[0].upper() + n[1:]
def norm_cust(c):
    c = (c or '').upper().replace('\xa0', ' ')
    c = re.sub(r'[^A-Z0-9 ]', ' ', c)
    c = re.sub(r'\b(PT|CV|TBK|INC|LTD|CO|LLC|L L C|MR|MRS|DR|IR|M SI|CORPORATION|CORP)\b', ' ', c)
    return re.sub(r'\s+', ' ', c).strip()
CUST_LABEL = {}
EXPORT_CUST = {'THAI WAH INTERNATIONAL TRADE SHANGHAI':'China','PEOPLE BEE HOON FACTORY PTE':'Singapore','HANA RASA CHARCOAL PRODUCTION AND PACKAGING':'Dubai',
 'COMMODITY QUEST':'Philippines','DEL MONTE PHILIPPINES':'Philippines','TWINPACK CONTAINER':'Philippines','R L POLYMER':'Philippines','ANHUI BBCA INTERNATIONAL':'China',
 'SAN MIGUEL BREWERY':'Philippines','WILLS INTERNATIONAL SALES':'Philippines','TAPIOCA DEVELOPMENT':'Thailand'}

# ---------- TWIN rows ----------
rows = []
for r in csv.DictReader(open(f'{S}/twin_rawww_2024.csv', encoding='utf-8')):
    m = r['Month'][:7]
    if m >= '2025-01': continue
    ck = norm_cust(r['Customer Name']); CUST_LABEL.setdefault(ck, r['Customer Name'].strip())
    rows.append(dict(month=m, cust=ck, group=r['Customer Group Description'], country=r['Country'], cur=r['Currency'],
        prod=norm_prod(r['name'], r['Material Description']), react=(r['Reaction'] or '').split(')')[-1] or 'NS',
        t=f(r['Sales quantity']) / 1000, ns_idr=f(r['Net Sales Revenue(IDR)']), cogs_idr=f(r['Cost']), ns=f(r['Net Sales Revenue (THB)']), cogs=f(r['COGS (THB)'])))
curflag = {}
for r in csv.DictReader(open(f'{S}/twin_rawww_2024.csv', encoding='utf-8')):
    m = r['Month'][:7]
    if m >= '2025-01': curflag[(m, norm_cust(r['Customer Name']), norm_prod(r['name'], r['Product']))] = r['Currency']
for r in csv.DictReader(open(f'{S}/twin_raw_2025on.csv', encoding='utf-8')):
    m = r['Month'][:7]; ck = norm_cust(r['Customer Name']); CUST_LABEL.setdefault(ck, r['Customer Name'].strip())
    prod = norm_prod(r['Trade name'])
    exp = [v for k, v in EXPORT_CUST.items() if ck.startswith(k)]
    country = exp[0] if exp else 'Indonesia'
    cur = curflag.get((m, ck, prod), 'USD' if exp else 'IDR')
    rows.append(dict(month=m, cust=ck, group=r['Group'], country=country, cur=cur, prod=prod, react=r['Reaction'] or 'NS',
        t=f(r['Sales quantity']), ns_idr=f(r['Net Sales Revenue(local)']), cogs_idr=f(r['Cost']), ns=f(r['Net Sales Revenue (THB)']), cogs=f(r['COGS (THB)'])))

# ---------- TDC layer: per SN per month ----------
tdc = defaultdict(lambda: defaultdict(float))
for r in tdc_rows:
    m = '%s-%02d' % (r['Year'][-4:], mo[r['Period']]); sn = r['SN']
    d = tdc[(m, sn)]
    d['t'] += f(r['Sales Quantity (Tons)']); ns = f(r['Net Sales Revenue (THB)']); d['ns'] += ns
    d['af'] += f(r['Actual Cost(THB)']); d['fi'] += f(r['F&I']); d['idle'] += f(r['Idle Cost']); d['oadj'] += f(r['Other Adj']); d['ppa'] += f(r['PPA'])
    fx = f(r['Exchange Rate']); d['usd'] += ns / fx if fx > 1 else ns / usdthb[m]
def q(m):
    y, mm = m.split('-'); return f"{y}Q{(int(mm) - 1) // 3 + 1}"
def tdc_rate(sn, m):
    """tonnage-weighted TDC per-kg rates for product sn in the quarter of m; fallback same year, then all periods"""
    for basis, sel in (('Q', lambda k: q(k[0]) == q(m)), ('Y', lambda k: k[0][:4] == m[:4]), ('ALL', lambda k: True)):
        keys = [k for k in tdc if k[1] == sn and sel(k) and tdc[k]['t'] > 0]
        if keys:
            T = sum(tdc[k]['t'] for k in keys)
            agg = {x: sum(tdc[k][x] for k in keys) / T / 1000 for x in ('ns', 'af', 'fi', 'idle', 'oadj', 'ppa', 'usd')}
            return agg, basis
    return None, None

# ---------- Por's country overrides (memory/twin-customer-country.json, keyed by customer_key) ----------
import os as _os
_ovp = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'memory', 'twin-customer-country.json')
for r in rows: r['country_src'] = r['country']
if _os.path.exists(_ovp):
    _ov = json.load(open(_ovp, encoding='utf-8')).get('overrides', {})
    for r in rows:
        r['country_src'] = r['country']
        if r['cust'] in _ov: r['country'] = _ov[r['cust']]['country']
# ---------- optional exclusion (python build_model.py <dir> excl) ----------
EXCLUDE = {'Native starch', 'Sago / pearl', 'Fibioca', 'Coarse flour'} if (len(sys.argv) > 2 and sys.argv[2] == 'excl') else set()
if EXCLUDE: rows = [r for r in rows if r['prod'] not in EXCLUDE]
# ---------- enrich ----------
out = []
for r in rows:
    m = r['month']; kg = r['t'] * 1000
    r['gp'] = r['ns'] - r['cogs']
    r['usdidr'] = usdidr[m]; r['idrthb'] = idrthb[m]; r['usdthb'] = usdthb[m]
    cogs_usd = r['cogs_idr'] / usdidr[m]
    r['cogs_usd'] = cogs_usd
    if r['cur'] == 'USD':
        r['ns_usd'] = r['ns_idr'] / usdidr[m]; r['ns_c'] = r['ns_usd'] * BASE_USDTHB
    else:
        r['ns_usd'] = 0.0; r['ns_c'] = r['ns_idr'] * BASE_IDRTHB
    r['cogs_c'] = cogs_usd * BASE_USDTHB
    r['gp_c'] = r['ns_c'] - r['cogs_c']
    # FX decomposition of TWIN GP (reported - constant), 3 components:
    #  (a) IDR/THB translation of IDR revenue: ns_idr*(idrthb_m - base)
    #  (b) USD/THB translation of USD revenue: ns_usd*(usdthb_m - base)
    #  (c) COGS (USD-denominated purchases) translated: -(cogs_usd*(usdthb_m - base))
    #  note: in IDR books, (a)+(c) also embed USD/IDR move; shown here on a THB view
    r['fx_rev_idr'] = r['ns_idr'] * (idrthb[m] - BASE_IDRTHB) if r['cur'] != 'USD' else 0.0
    r['fx_rev_usd'] = r['ns_usd'] * (usdthb[m] - BASE_USDTHB)
    r['fx_cogs_usd'] = -cogs_usd * (usdthb[m] - BASE_USDTHB)
    # alternative view in IDR terms: what TWIN's IDR GP would be if USD/IDR stayed at base
    r['gp_idr'] = r['ns_idr'] - r['cogs_idr']
    r['cogs_idr_c'] = cogs_usd * BASE_USDIDR
    r['ns_idr_c'] = r['ns_usd'] * BASE_USDIDR if r['cur'] == 'USD' else r['ns_idr']
    r['gp_idr_c'] = r['ns_idr_c'] - r['cogs_idr_c']
    r['fx_usdidr_thb'] = (r['gp_idr'] - r['gp_idr_c']) * idrthb[m]   # USD/IDR effect on TWIN IDR GP, in THB at month rate
    r['fx_idrthb_thb'] = r['gp_idr_c'] * (idrthb[m] - BASE_IDRTHB)    # IDR/THB translation of (constant-USD/IDR) GP
    sn = TDC_MAP.get(r['prod'])
    r['sn'] = sn or ''
    r['src'] = 'TDC' if sn else 'Non-TDC'
    if sn:
        rate, basis = tdc_rate(sn, m)
        r['tdc_basis'] = basis
        r['tdc_ns'] = rate['ns'] * kg; r['tdc_usd'] = rate['usd'] * kg
        r['tdc_pcost'] = (rate['af'] + rate['fi']) * kg
        r['tdc_other'] = (rate['idle'] + rate['oadj'] + rate['ppa']) * kg
        r['tdc_pgp'] = r['tdc_ns'] - r['tdc_pcost']; r['tdc_fgp'] = r['tdc_pgp'] - r['tdc_other']
        r['tdc_ns_c'] = r['tdc_usd'] * BASE_USDTHB
        r['tdc_pgp_c'] = r['tdc_ns_c'] - r['tdc_pcost']; r['tdc_fgp_c'] = r['tdc_pgp_c'] - r['tdc_other']
        r['fx_tdc'] = r['tdc_ns'] - r['tdc_ns_c']
    else:
        r['tdc_basis'] = ''
        for k in ('tdc_ns','tdc_usd','tdc_pcost','tdc_other','tdc_pgp','tdc_fgp','tdc_ns_c','tdc_pgp_c','tdc_fgp_c','fx_tdc'): r[k] = 0.0
    r['chain_pgp'] = r['gp'] + r['tdc_pgp']; r['chain_fgp'] = r['gp'] + r['tdc_fgp']
    r['chain_pgp_c'] = r['gp_c'] + r['tdc_pgp_c']; r['chain_fgp_c'] = r['gp_c'] + r['tdc_fgp_c']
    r['label'] = CUST_LABEL[r['cust']]
    r['q'] = q(m); r['y'] = m[:4]
    out.append(r)

json.dump(dict(rows=out, usdthb=usdthb, idrthb=idrthb, usdidr=usdidr, fxsrc=fxsrc,
               base=dict(usdthb=BASE_USDTHB, idrthb=BASE_IDRTHB, usdidr=BASE_USDIDR),
               tdc={f'{k[0]}|{k[1]}': dict(v) for k, v in tdc.items()}, sn_name=SN_NAME, excluded=sorted(EXCLUDE)),
          open(f'{S}/model.json', 'w', encoding='utf-8'))
print('rows', len(out), 'base USD/THB %.3f IDR/THB %.6f USD/IDR %.0f' % (BASE_USDTHB, BASE_IDRTHB, BASE_USDIDR))
tot = defaultdict(lambda: defaultdict(float))
for r in out:
    for k in ('t','ns','gp','ns_c','gp_c','tdc_ns','tdc_pgp','tdc_fgp','tdc_pgp_c','tdc_fgp_c','fx_rev_idr','fx_rev_usd','fx_cogs_usd','fx_tdc','fx_usdidr_thb','fx_idrthb_thb'): tot[r['y']][k] += r[k]
    tot[r['y']]['t_tdc'] += r['t'] if r['src'] == 'TDC' else 0
for y in sorted(tot):
    d = tot[y]
    print(y, 't=%.0f (TDC prod %.0f) TWIN NS=%.1fMB GP=%.2fMB (%.0f/t) | constGP=%.2fMB | TDC pGP=%.2fMB fGP=%.2fMB | const pGP=%.2f fGP=%.2f' % (
        d['t'], d['t_tdc'], d['ns']/1e6, d['gp']/1e6, d['gp']/d['t'], d['gp_c']/1e6, d['tdc_pgp']/1e6, d['tdc_fgp']/1e6, d['tdc_pgp_c']/1e6, d['tdc_fgp_c']/1e6))
    print('    FX TWIN: revIDR %.2f revUSD %.2f cogsUSD %.2f = %.2f | alt: USD/IDR %.2f + IDR/THB %.2f = %.2f | FX TDC %.2f' % (
        d['fx_rev_idr']/1e6, d['fx_rev_usd']/1e6, d['fx_cogs_usd']/1e6, (d['fx_rev_idr']+d['fx_rev_usd']+d['fx_cogs_usd'])/1e6,
        d['fx_usdidr_thb']/1e6, d['fx_idrthb_thb']/1e6, (d['fx_usdidr_thb']+d['fx_idrthb_thb'])/1e6, d['fx_tdc']/1e6))
act = defaultdict(lambda: defaultdict(float))
for (m, sn), d in tdc.items():
    y = m[:4]; act[y]['t'] += d['t']; act[y]['ns'] += d['ns']; act[y]['pgp'] += d['ns']-d['af']-d['fi']; act[y]['fgp'] += d['ns']-d['af']-d['fi']-d['idle']-d['oadj']-d['ppa']
for y in sorted(act): print('TDC actual', y, 't=%.0f NS=%.1fMB pGP=%.2fMB fGP=%.2fMB' % (act[y]['t'], act[y]['ns']/1e6, act[y]['pgp']/1e6, act[y]['fgp']/1e6))
print('basis counts', {b: sum(1 for r in out if r['tdc_basis'] == b) for b in ('Q', 'Y', 'ALL', '')})
print('non-TDC prods', sorted(set(r['prod'] for r in out if r['src'] == 'Non-TDC')))
print('TDC prods', sorted(set(r['prod'] for r in out if r['src'] == 'TDC')))
print('USD rows', sum(1 for r in out if r['cur'] == 'USD'), 'customers', sorted(set(r['label'] for r in out if r['cur'] == 'USD')))
