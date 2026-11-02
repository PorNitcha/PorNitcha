# Derive every number shown in the AP2027/28 CEO consolidation deck from ap27_data.json (comparison-data.json, LE9+3 file)
import json, sys
D = json.load(open(sys.argv[1], encoding='utf-8'))
SC = ['2025', 'AP26', 'LE26', 'AP27', 'AP28']

def g(b, e, s):
    v = D[b].get(e, {}).get(s)
    return float(v) if isinstance(v, (int, float)) else 0.0

BU = ['Foods', 'Starch', 'HVA', 'NBG', 'Waxy']
def other(b, s):  # Corp + ElimBU + anything not in a BU, so BUs always add to TWPC
    return g(b, 'TWPC', s) - sum(g(b, e, s) for e in BU)

out = {}
# ---- slide 2: group headline
out['opba_stack'] = {s: {'Food': g('OP Before Admin', 'Foods', s), 'Starch': g('OP Before Admin', 'Starch', s),
                         'HVA': g('OP Before Admin', 'HVA', s),
                         'Other': g('OP Before Admin', 'NBG', s) + g('OP Before Admin', 'Waxy', s) + other('OP Before Admin', s),
                         'Total': g('OP Before Admin', 'TWPC', s)} for s in SC}
out['strip'] = {s: {'vol': g('Volume', 'TWPC', s) / 1000, 'ns': g('Net sales', 'TWPC', s), 'gp': g('Gross profit', 'TWPC', s),
                    'gm': g('Gross profit', 'TWPC', s) / g('Net sales', 'TWPC', s), 'opba': g('OP Before Admin', 'TWPC', s),
                    'np': g('Net profit', 'TWPC', s)} for s in SC}

# ---- slide 3: LE26 -> AP27 OPBA bridge by BU
def bu_bridge(a, b):
    steps = [('Starch', g('OP Before Admin', 'Starch', b) - g('OP Before Admin', 'Starch', a)),
             ('HVA', g('OP Before Admin', 'HVA', b) - g('OP Before Admin', 'HVA', a)),
             ('Food', g('OP Before Admin', 'Foods', b) - g('OP Before Admin', 'Foods', a)),
             ('NBG', g('OP Before Admin', 'NBG', b) - g('OP Before Admin', 'NBG', a)),
             ('Waxy', g('OP Before Admin', 'Waxy', b) - g('OP Before Admin', 'Waxy', a)),
             ('Corp / Elim', other('OP Before Admin', b) - other('OP Before Admin', a))]
    return {'start': g('OP Before Admin', 'TWPC', a), 'end': g('OP Before Admin', 'TWPC', b), 'steps': steps}
out['bridge27'] = bu_bridge('LE26', 'AP27')
out['bridge28'] = bu_bridge('AP27', 'AP28')

# ---- slide 4: entity table (OPBA)
ROWS = [('Starch BU', 'Starch', 0), ('Starch TH', 'StarchTH', 1), ('China (TWIT+TWFZ)', 'Total CN', 1), ('Cambodia (TWIC)', 'TWIC', 1),
        ('Vietnam (TNT+VTC)', 'Total VN', 1),
        ('HVA BU (excl. Waxy)', 'HVA', 0), ('TDC', 'TDC', 1), ('TDC 2.0', 'TDC2.0', 1), ('TWIN', 'TWIN', 1), ('TWII', 'TWII', 1),
        ('Food BU', 'Foods', 0), ('Food TH', 'FoodTH', 1), ('Well Grow', 'FoodWG', 1), ('Food VN', 'FoodVN', 1),
        ('NBG BU', 'NBG', 0), ('Waxy', 'Waxy', 0)]
tab = []
for lab, e, lvl in ROWS:
    tab.append({'label': lab, 'lvl': lvl, **{s: g('OP Before Admin', e, s) for s in SC}})
tab.append({'label': 'Corp / Elim', 'lvl': 0, **{s: other('OP Before Admin', s) for s in SC}})
tab.append({'label': 'TWPC', 'lvl': -1, **{s: g('OP Before Admin', 'TWPC', s) for s in SC}})
out['entity_opba'] = tab

# ---- slide 5: NP bridge LE26 -> AP27 (OP in the file already contains other op. income, FX and non-op items)
def below(s):  # items between OPBA and NP that are not admin / finance / CIT / MI
    return g('Net profit', 'TWPC', s) - (g('OP Before Admin', 'TWPC', s) + g('Total Admin', 'TWPC', s)
                                         + g('Finance income (expense)', 'TWPC', s) + g('CIT', 'TWPC', s) + g('MI', 'TWPC', s))
oneoff = lambda s: g('Other operating income and expenses', 'TWPC', s) + g('Exchange gain/(loss)', 'TWPC', s) + g('Net non-operating profit', 'TWPC', s)
a, b = 'LE26', 'AP27'
steps = [('OPBA', g('OP Before Admin', 'TWPC', b) - g('OP Before Admin', 'TWPC', a)),
         ('Admin', g('Total Admin', 'TWPC', b) - g('Total Admin', 'TWPC', a)),
         ('2026 other income & FX gain', oneoff(b) - oneoff(a)),
         ('Finance cost', g('Finance income (expense)', 'TWPC', b) - g('Finance income (expense)', 'TWPC', a)),
         ('CIT', g('CIT', 'TWPC', b) - g('CIT', 'TWPC', a)),
         ('MI & other', (g('MI', 'TWPC', b) - g('MI', 'TWPC', a)) + (below(b) - oneoff(b)) - (below(a) - oneoff(a)))]
out['np_bridge'] = {'start': g('Net profit', 'TWPC', a), 'end': g('Net profit', 'TWPC', b), 'steps': steps}
out['np_check'] = out['np_bridge']['start'] + sum(v for _, v in steps) - out['np_bridge']['end']
out['below'] = {}
for s in SC:
    lv = {'OPBA': g('OP Before Admin', 'TWPC', s), 'Admin': g('Total Admin', 'TWPC', s), 'Other income & FX': oneoff(s),
          'Finance cost': g('Finance income (expense)', 'TWPC', s), 'CIT': g('CIT', 'TWPC', s)}
    lv['MI & other'] = g('Net profit', 'TWPC', s) - sum(lv.values())
    lv['Net profit'] = g('Net profit', 'TWPC', s)
    out['below'][s] = lv
out['vol_sth'] = {s: g('Volume', 'StarchTH', s) / 1000 for s in SC}
out['admin_tdc2'] ={s: g('Total Admin', 'TDC2.0', s) for s in SC}
out['oneoff'] = {s: {'other_inc': g('Other operating income and expenses', 'TWPC', s), 'fx': g('Exchange gain/(loss)', 'TWPC', s),
                     'nonop': g('Net non-operating profit', 'TWPC', s)} for s in SC}
NPB = [('Food', 'Foods'), ('Starch', 'Starch'), ('HVA', 'HVA'), ('NBG', 'NBG'), ('Waxy', 'Waxy')]
out['np_bu'] = {s: dict([(l, g('Net profit', e, s)) for l, e in NPB] + [('Corp / Elim', other('Net profit', s)), ('TWPC', g('Net profit', 'TWPC', s))]) for s in SC}
out['np_entity'] = {e: {s: g('Net profit', e, s) for s in SC} for e in ['StarchTH', 'TWIC', 'TDC', 'TDC2.0', 'FoodTH', 'FoodWG', 'Corp']}

# ---- appendix: conso P&L by BU
LINES = [('Volume (kt)', 'Volume', 1 / 1000), ('Net sales', 'Net sales', 1), ('Gross profit', 'Gross profit', 1), ('%GM', None, None),
         ('DC', 'DC', 1), ('A&P', 'A&P', 1), ('S&M', 'S&M', 1), ('OP before admin', 'OP Before Admin', 1), ('%OPBA', None, None),
         ('Admin - people', 'admin exp - People', 1), ('Admin - non-people', 'admin exp - Non-people', 1),
         ('Operating profit', 'Operating profit', 1), ('Finance income (expense)', 'Finance income (expense)', 1),
         ('CIT', 'CIT', 1), ('MI', 'MI', 1), ('Net profit', 'Net profit', 1)]
COLS = [('Starch BU', 'Starch'), ('HVA BU', 'HVA'), ('Food BU', 'Foods'), ('NBG BU', 'NBG'), ('Waxy', 'Waxy'), ('Corp / Elim', None), ('TWPC', 'TWPC')]
def pl(s):
    res = []
    for lab, blk, k in LINES:
        row = {'label': lab, 'vals': []}
        for cl, e in COLS:
            if blk is None:
                base = 'Gross profit' if lab == '%GM' else 'OP Before Admin'
                ns = g('Net sales', e, s) if e else other('Net sales', s)
                num = g(base, e, s) if e else other(base, s)
                row['vals'].append(num / ns if abs(ns) > 0.5 else None)
            else:
                row['vals'].append((g(blk, e, s) if e else other(blk, s)) * k)
        res.append(row)
    return res
out['pl_cols'] = [c for c, _ in COLS]
out['pl'] = {s: pl(s) for s in ['LE26', 'AP27', 'AP28']}
# volume: eliminations make the Corp/Elim column meaningless for tonnes -> blank
for s in out['pl']:
    out['pl'][s][0]['vals'][5] = None
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# console check
print('np bridge check (should be 0):', round(out['np_check'], 6))
for k in ['bridge27', 'bridge28', 'np_bridge']:
    br = out[k]; print(k, round(br['start'], 1), [(n, round(v, 1)) for n, v in br['steps']], round(br['end'], 1))
for s in SC:
    st = out['opba_stack'][s]; print(s, {k: round(v, 1) for k, v in st.items()}, {k: round(v, 3) for k, v in out['strip'][s].items()})
print('oneoff', {s: {k: round(v, 1) for k, v in out['oneoff'][s].items()} for s in SC})
print('np_bu', {s: {k: round(v, 1) for k, v in out['np_bu'][s].items()} for s in ['LE26', 'AP27', 'AP28']})
print('admin TDC2', out['admin_tdc2'])
for s in ['LE26', 'AP27']:
    for r in out['pl'][s]:
        print(s, r['label'].ljust(26), ' '.join(('%9.1f' % v if abs(v) > 1.5 else '%9.3f' % v) if v is not None else '        -' for v in r['vals']))
