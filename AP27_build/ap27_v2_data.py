# Deck numbers v2: every TWPC total comes from ConsoAll; BU numbers from the BU sheets; Corp/Elim = ConsoAll - BUs
# usage: python ap27_v2_data.py sheets.json ap27_v2.json
import json, sys
X = json.load(open(sys.argv[1], encoding='utf-8'))
SC = ['R24', '2025', 'AP26', 'LE26', 'AP27', 'AP28']
L = {'vol': 'Volume', 'ns': 'Net Sales', 'gp': 'Gross profit', 'dc': 'DC', 'ap': 'A&P', 'sm': 'S&M', 'opba': 'OP Before Admin',
     'adp': 'admin exp - People', 'adn': 'admin exp - Non-people', 'oth': 'Other operating income and expenses',
     'fx': 'Exchange gain/(loss)', 'op': 'Operating profit', 'nonop': 'Net non-operating profit', 'fin': 'Finance income (expense)',
     'cit': 'CIT', 'mi': 'MI', 'np': 'Net profit aft Thanos'}
def v(sheet, k, s): return X[sheet][L[k]][s]
BU = {'Food': 'FoodBU', 'HVA': 'HVA incl Waxy', 'HVAex': 'HVABU', 'Waxy': 'Waxy', 'Starch': 'StarchBU', 'NBG': 'NBGBU'}
CORE = ['Food', 'HVA', 'Starch', 'NBG']          # HVA = incl. Waxy; these four + Corp/Elim = ConsoAll
out = {'scen': SC}

def line(k, s):
    d = {b: v(sh, k, s) for b, sh in BU.items()}
    d['TWPC'] = v('ConsoAll', k, s)
    d['CorpElim'] = d['TWPC'] - sum(d[b] for b in CORE)
    d['ElimBU'] = v('ElimBU', k, s); d['Corp'] = v('Corp', k, s)
    d['Unrec'] = d['CorpElim'] - d['ElimBU'] - d['Corp']    # ConsoAll vs (BU sheets + ElimBU + Corp)
    return d
out['pl'] = {s: {k: line(k, s) for k in L} for s in SC}

# reconciliation report
rec = []
for s in SC:
    for k in ['ns', 'gp', 'opba', 'adp', 'adn', 'op', 'np']:
        u = out['pl'][s][k]['Unrec']
        if abs(u) > 0.05: rec.append([s, L[k], round(out['pl'][s][k]['TWPC'], 2), round(out['pl'][s][k]['TWPC'] - u, 2), round(u, 2)])
out['recon'] = rec

# OPBA stack (Food bottom, HVA incl. Waxy, Starch top; NBG + Corp/Elim below the axis when negative)
out['stack'] = {s: {'Food': v('FoodBU', 'opba', s), 'HVA': v('HVA incl Waxy', 'opba', s), 'Starch': v('StarchBU', 'opba', s),
                    'Other': out['pl'][s]['opba']['NBG'] + out['pl'][s]['opba']['CorpElim'], 'Total': v('ConsoAll', 'opba', s)} for s in SC}
out['strip'] = {s: {'vol': v('ConsoAll', 'vol', s) / 1000, 'ns': v('ConsoAll', 'ns', s), 'gp': v('ConsoAll', 'gp', s),
                    'gm': v('ConsoAll', 'gp', s) / v('ConsoAll', 'ns', s), 'opba': v('ConsoAll', 'opba', s), 'np': v('ConsoAll', 'np', s)} for s in SC}

def bridge(a, b):
    p = out['pl']
    steps = [['Food', p[b]['opba']['Food'] - p[a]['opba']['Food']], ['HVA incl. Waxy', p[b]['opba']['HVA'] - p[a]['opba']['HVA']],
             ['Starch', p[b]['opba']['Starch'] - p[a]['opba']['Starch']], ['NBG', p[b]['opba']['NBG'] - p[a]['opba']['NBG']],
             ['Corp / Elim', p[b]['opba']['CorpElim'] - p[a]['opba']['CorpElim']]]
    return {'start': p[a]['opba']['TWPC'], 'end': p[b]['opba']['TWPC'], 'steps': steps,
            'lvl': {n: [p[a]['opba'][k], p[b]['opba'][k]] for n, k in [('Food', 'Food'), ('HVA incl. Waxy', 'HVA'), ('Starch', 'Starch'), ('NBG', 'NBG'), ('Corp / Elim', 'CorpElim')]}}
out['bridge27'] = bridge('LE26', 'AP27'); out['bridge28'] = bridge('AP27', 'AP28')

# entity OPBA table
ENT = [('Food BU', 'FoodBU', 0), ('Food TH', 'FoodTH', 1), ('Well Grow', 'FoodWG', 1), ('Food VN', 'FoodVN', 1),
       ('HVA BU incl. Waxy', 'HVA incl Waxy', 0), ('TDC', 'TDC', 1), ('TDC 2.0', 'TDC2.0', 1), ('TWIN', 'TWIN', 1), ('TWII', 'TWII', 1), ('Waxy', 'Waxy', 1),
       ('memo: HVA excl. Waxy', 'HVABU', 2),
       ('Starch BU', 'StarchBU', 0), ('Starch TH', 'StarchTH', 1), ('China (TWIT+TWFZ)', 'TotalCN', 1), ('Cambodia (TWIC)', 'TWIC', 1), ('Vietnam (TNT+VTC)', 'TotalVN', 1),
       ('NBG BU', 'NBGBU', 0)]
tab = [{'label': l, 'lvl': lv, **{s: v(sh, 'opba', s) for s in SC}} for l, sh, lv in ENT]
tab.append({'label': 'Corp / Elim', 'lvl': 0, **{s: out['pl'][s]['opba']['CorpElim'] for s in SC}})
tab.append({'label': 'TWPC (ConsoAll)', 'lvl': -1, **{s: v('ConsoAll', 'opba', s) for s in SC}})
out['entity_opba'] = tab
out['ent'] = {sh: {k: {s: v(sh, k, s) for s in SC} for k in ['opba', 'np', 'vol', 'adp', 'adn']} for sh in
              ['StarchTH', 'TotalCN', 'TWIC', 'TotalVN', 'TDC', 'TDC2.0', 'TWIN', 'TWII', 'Waxy', 'FoodTH&WG', 'FoodTH', 'FoodWG', 'FoodVN', 'NBGBU', 'Corp', 'ElimBU', 'HVABU', 'HVA incl Waxy', 'FoodBU', 'StarchBU']}

# NP bridge LE26 -> AP27 at group level (ConsoAll)
def g(k, s): return v('ConsoAll', k, s)
def oneoff(s): return g('oth', s) + g('fx', s) + g('nonop', s)
def admin(s): return g('adp', s) + g('adn', s)
def resid(s): return g('np', s) - (g('opba', s) + admin(s) + oneoff(s) + g('fin', s) + g('cit', s))   # MI + PPA-CIT + other small lines
a, b = 'LE26', 'AP27'
out['np_bridge'] = {'start': g('np', a), 'end': g('np', b), 'steps': [
    ['OPBA', g('opba', b) - g('opba', a)], ['Admin', admin(b) - admin(a)], ['2026 other inc. & FX gain', oneoff(b) - oneoff(a)],
    ['Finance cost', g('fin', b) - g('fin', a)], ['CIT', g('cit', b) - g('cit', a)], ['MI & other', resid(b) - resid(a)]]}
out['np_check'] = out['np_bridge']['start'] + sum(x[1] for x in out['np_bridge']['steps']) - out['np_bridge']['end']
out['below'] = {s: {'OPBA': g('opba', s), 'Admin': admin(s), 'Other income & FX': oneoff(s), 'Finance cost': g('fin', s), 'CIT': g('cit', s),
                    'MI & other': resid(s), 'Net profit': g('np', s)} for s in SC}
out['oneoff'] = {s: {'other_inc': g('oth', s), 'fx': g('fx', s), 'nonop': g('nonop', s)} for s in SC}

# Admin P / Non-P: Thailand vs International (entity sheets); TDC 2.0 shown on its own inside TH
TH = ['StarchTH', 'TDC', 'Waxy', 'FoodTH&WG', 'NBGBU', 'Corp']
INTER = ['TotalCN', 'TWIC', 'TotalVN', 'TWIN', 'TWII', 'FoodVN']
adm = {}
for s in SC:
    r = {}
    for k in ['adp', 'adn']:
        th = sum(v(x, k, s) for x in TH); td2 = v('TDC2.0', k, s); it = sum(v(x, k, s) for x in INTER)
        tot = g(k, s)
        r[k] = {'TH excl. TDC 2.0': th, 'TDC 2.0': td2, 'International': it, 'Elim / other': tot - th - td2 - it, 'TWPC': tot}
    r['by_entity'] = {x: v(x, 'adp', s) + v(x, 'adn', s) for x in TH + ['TDC2.0'] + INTER}
    adm[s] = r
out['admin'] = adm
out['admin_groups'] = {'TH': TH, 'INTER': INTER}

# multi-year P&L summary (LE26 / AP27 / AP28) by BU: NS, GP, OPBA; NP for TWPC only
SUMROWS = [('Food BU', 'Food'), ('HVA BU incl. Waxy', 'HVA'), ('  of which HVA excl. Waxy', 'HVAex'), ('  of which Waxy', 'Waxy'),
           ('Starch BU', 'Starch'), ('NBG BU', 'NBG'), ('Corp / Elim', 'CorpElim'), ('TWPC (ConsoAll)', 'TWPC')]
out['summary'] = [{'label': l, 'key': k, **{m: {s: out['pl'][s][m][k] for s in ['LE26', 'AP27', 'AP28']} for m in ['ns', 'gp', 'opba']}} for l, k in SUMROWS]

json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- console checks
print('NP bridge residual (must be 0):', round(out['np_check'], 6))
for s in SC:
    st = out['stack'][s]; tot = st['Food'] + st['HVA'] + st['Starch'] + st['Other']
    print(s, 'stack sum - ConsoAll OPBA =', round(tot - st['Total'], 6), {k: round(x, 1) for k, x in st.items()})
for k in ['bridge27', 'bridge28']:
    br = out[k]; print(k, round(br['start'], 1), [(n, round(x, 1)) for n, x in br['steps']], round(br['end'], 1), 'tie', round(br['start'] + sum(x for _, x in br['steps']) - br['end'], 6))
print('np_bridge', [(n, round(x, 1)) for n, x in out['np_bridge']['steps']])
print('RECON variances (ConsoAll vs BU sheets + ElimBU + Corp):')
for r in rec: print('  ', r)
for s in ['LE26', 'AP27', 'AP28']:
    a2 = out['admin'][s]
    print(s, 'P', {k: round(x, 1) for k, x in a2['adp'].items()}, '| NonP', {k: round(x, 1) for k, x in a2['adn'].items()})
for r in out['summary']:
    print(r['label'].ljust(28), [round(r['opba'][s], 1) for s in ['LE26', 'AP27', 'AP28']], [round(r['ns'][s], 1) for s in ['LE26', 'AP27', 'AP28']])

