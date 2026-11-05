# v4 additions on top of ap27_v2.json (run ap27_v2_data.py + ap27_v2_text.py first)
# - Corp / BU elim is never shown on its own (management buffer): BU rows are shown, totals are ConsoAll
# - bridge LE26 -> AP27 -> (stacked AP28 increment) -> AP28
# - entity OPBA table with China (TWIT / TWFZ) and NBG (Bioplastic / discontinued) splits
# - P&L walk 2025 / LE26 / AP27 / AP28 from BU OPBA to NP (ConsoAll)
# - BU P&L tables by year (Starch, HVA excl. Waxy, Food, NBG, Waxy, TWPC): BUs stop at OPBA, TWPC runs to NP
# usage: python ap27_v4_data.py sheets.json ap27_v2.json
import json, sys
X = json.load(open(sys.argv[1], encoding='utf-8'))
P = sys.argv[2]
d = json.load(open(P, encoding='utf-8'))
SC = ['R24', '2025', 'AP26', 'LE26', 'AP27', 'AP28']
def v(sh, line, s): return X[sh][line][s]
OPBA = 'OP Before Admin'; NPL = 'Net profit aft Thanos'
def f0(x):
    if x is None or abs(x) < 0.5: return '–'
    return '({:,.0f})'.format(-x) if x < 0 else '{:,.0f}'.format(x)
def sg(x):
    if abs(x) < 0.5: return '0'
    return '+{:,.0f}'.format(x) if x > 0 else '({:,.0f})'.format(-x)
def ab(x): return '{:,.0f}'.format(abs(x))

BUS = [('Food', 'FoodBU'), ('HVA incl. Waxy', 'HVA incl Waxy'), ('Starch', 'StarchBU'), ('NBG', 'NBGBU')]
# ---- bridge with AP28 trajectory (no Corp / Elim bar)
d['bridge4'] = {'le26': v('ConsoAll', OPBA, 'LE26'), 'ap27': v('ConsoAll', OPBA, 'AP27'), 'ap28': v('ConsoAll', OPBA, 'AP28'),
                'steps27': [[n, v(sh, OPBA, 'AP27') - v(sh, OPBA, 'LE26')] for n, sh in BUS],
                'inc28': [[n, v(sh, OPBA, 'AP28') - v(sh, OPBA, 'AP27')] for n, sh in BUS],
                'lvl': {n: {s: v(sh, OPBA, s) for s in ['LE26', 'AP27', 'AP28']} for n, sh in BUS}}

# ---- entity table (no Corp / Elim row; total = ConsoAll)
def disc(s, line=OPBA): return sum(v(x, line, s) for x in ['AnimalFeeds', 'AgBio', 'V9'])
ROWS = [('Food BU', 'FoodBU', 0), ('Food TH', 'FoodTH', 1), ('Well Grow', 'FoodWG', 1), ('Food VN', 'FoodVN', 1),
        ('HVA BU incl. Waxy', 'HVA incl Waxy', 0), ('TDC', 'TDC', 1), ('TDC 2.0', 'TDC2.0', 1), ('TWIN', 'TWIN', 1), ('TWII', 'TWII', 1), ('Waxy', 'Waxy', 1),
        ('memo: HVA excl. Waxy', 'HVABU', 9),
        ('Starch BU', 'StarchBU', 0), ('Starch TH', 'StarchTH', 1), ('China', 'TotalCN', 1), ('TWIT', 'TWIT', 2), ('TWFZ', 'TWFZ', 2),
        ('Cambodia (TWIC)', 'TWIC', 1), ('Vietnam (TNT+VTC)', 'TotalVN', 1),
        ('NBG BU', 'NBGBU', 0), ('Bioplastic', 'BioPlastic', 1), ('Discontinued (feed, AgBio, V9)', None, 1)]
tab = []
for lab, sh, lv in ROWS:
    tab.append({'label': lab, 'lvl': lv, **{s: (v(sh, OPBA, s) if sh else disc(s)) for s in SC}})
tab.append({'label': 'TWPC total', 'lvl': -1, **{s: v('ConsoAll', OPBA, s) for s in SC}})
d['entity4'] = tab
d['nbg'] = {s: {'bio': v('BioPlastic', OPBA, s), 'disc': disc(s), 'nbg': v('NBGBU', OPBA, s)} for s in SC}

# ---- P&L walk (slide 6): BU OPBA -> NP, 4 years, ConsoAll below the BU lines
YW = ['R24', '2025', 'LE26', 'AP27', 'AP28']
c = lambda line, s: v('ConsoAll', line, s)
walk = []
def add(label, vals, kind):
    walk.append({'label': label, 'kind': kind, 'vals': vals})
add('BU OPBA', [None] * len(YW), 'sect')
WALK_BUS = [('HVA incl. Waxy', 'HVA incl Waxy'), ('Food', 'FoodBU'), ('Starch', 'StarchBU'), ('NBG', 'NBGBU')]   # order set by Por for this table
for n, sh in WALK_BUS:
    add(n + ' BU' if n != 'HVA incl. Waxy' else 'HVA BU incl. Waxy', [v(sh, OPBA, s) for s in YW], 'bu')
    if sh == 'HVA incl Waxy': add('of which Waxy', [v('Waxy', OPBA, s) for s in YW], 'memo')   # Waxy sits right under HVA
add('Total BU OPBA', [c(OPBA, s) for s in YW], 'total')
add('Admin ' + '–' + ' people', [c('admin exp - People', s) for s in YW], 'sub')
add('Admin ' + '–' + ' non-people', [c('admin exp - Non-people', s) for s in YW], 'sub')
add('Total admin', [c('admin exp - People', s) + c('admin exp - Non-people', s) for s in YW], 'subtotal')
add('Other operating income & FX', [c('Operating profit', s) - c(OPBA, s) - c('admin exp - People', s) - c('admin exp - Non-people', s) for s in YW], 'sub')
add('Operating profit (OP)', [c('Operating profit', s) for s in YW], 'total')
add('Net non-operating profit', [c('Net non-operating profit', s) for s in YW], 'sub')
add('Finance income (expense)', [c('Finance income (expense)', s) for s in YW], 'sub')
add('CIT (incl. PPA)', [c('Net income before MI', s) - c('Operating profit', s) - c('Net non-operating profit', s) - c('Finance income (expense)', s) for s in YW], 'line')
add('MI', [c('MI', s) for s in YW], 'line')
add('Net profit (NP)', [c(NPL, s) for s in YW], 'total')
# tie checks
for i, s in enumerate(YW):
    g = {r['label']: r['vals'][i] for r in walk}
    assert abs(g['Total BU OPBA'] + g['Total admin'] + g['Other operating income & FX'] - g['Operating profit (OP)']) < 1e-6
    assert abs(g['Operating profit (OP)'] + g['Net non-operating profit'] + g['Finance income (expense)'] + g['CIT (incl. PPA)'] + g['MI'] - g['Net profit (NP)']) < 1e-6
d['walk'] = walk; d['walk_years'] = ['2024 Rebase', '2025', '2026 LE', 'AP2027', 'AP2028']
d['buffer'] = {s: c(OPBA, s) - sum(v(sh, OPBA, s) for _, sh in BUS) for s in YW}   # what the BU rows do not show (for the chat note only)

# ---- BU P&L tables by year (slides 9-10)
COLS = [('Starch BU', 'StarchBU'), ('HVA BU incl. Waxy', 'HVA incl Waxy'), ('Food BU', 'FoodBU'), ('NBG BU', 'NBGBU'), ('TWPC', 'ConsoAll')]   # Waxy inside HVA; its OPBA goes in a note
def bupl(s):
    rows = []
    def r(label, fn, kind='mb', key=False, twpc_only=False):
        vals = []
        for _, sh in COLS:
            vals.append(None if (twpc_only and sh != 'ConsoAll') else fn(sh))
        rows.append({'label': label, 'kind': kind, 'key': key, 'vals': vals})
    ns = lambda sh: v(sh, 'Net Sales', s)
    sell = lambda sh: v(sh, 'DC', s) + v(sh, 'A&P', s) + v(sh, 'S&M', s)
    r('Volume (kt)', lambda sh: v(sh, 'Volume', s) / 1000, 'kt')
    PVB = {'2025': 'R24', 'LE26': '2025', 'AP27': 'LE26', 'AP28': 'AP27'}
    r('% Vol growth', lambda sh: (v(sh, 'Volume', s) / v(sh, 'Volume', PVB[s]) - 1) if v(sh, 'Volume', PVB[s]) > 0.5 else None, 'pct')
    r('Net sales', ns, key=True)
    r('Cost of sales (total)', lambda sh: v(sh, 'Total COST', s))
    r('Gross profit', lambda sh: v(sh, 'Gross profit', s), key=True)
    r('%GM', lambda sh: v(sh, 'Gross profit', s) / ns(sh) if abs(ns(sh)) > 0.5 else None, 'pct')
    r('DC', lambda sh: v(sh, 'DC', s)); r('A&P', lambda sh: v(sh, 'A&P', s)); r('S&M', lambda sh: v(sh, 'S&M', s))
    r('Total selling', sell, key=True)
    r('% selling', lambda sh: sell(sh) / ns(sh) if abs(ns(sh)) > 0.5 else None, 'pct')
    r('OP before admin', lambda sh: v(sh, OPBA, s), key=True)
    r('%OPBA', lambda sh: v(sh, OPBA, s) / ns(sh) if abs(ns(sh)) > 0.5 else None, 'pct')
    r('Admin - people', lambda sh: v(sh, 'admin exp - People', s), twpc_only=True)
    r('Admin - non-people', lambda sh: v(sh, 'admin exp - Non-people', s), twpc_only=True)
    r('Total admin', lambda sh: v(sh, 'admin exp - People', s) + v(sh, 'admin exp - Non-people', s), key=True, twpc_only=True)
    r('Other op. income & FX', lambda sh: v(sh, 'Operating profit', s) - v(sh, OPBA, s) - v(sh, 'admin exp - People', s) - v(sh, 'admin exp - Non-people', s), twpc_only=True)
    r('Operating profit', lambda sh: v(sh, 'Operating profit', s), key=True, twpc_only=True)
    r('Net non-operating profit', lambda sh: v(sh, 'Net non-operating profit', s), twpc_only=True)
    r('Finance income (expense)', lambda sh: v(sh, 'Finance income (expense)', s), twpc_only=True)
    r('CIT (incl. PPA)', lambda sh: v(sh, 'Net income before MI', s) - v(sh, 'Operating profit', s) - v(sh, 'Net non-operating profit', s) - v(sh, 'Finance income (expense)', s), twpc_only=True)
    r('MI', lambda sh: v(sh, 'MI', s), twpc_only=True)
    r('Net profit', lambda sh: v(sh, NPL, s), key=True, twpc_only=True)
    # TWPC column self-check: GP + selling = OPBA, and the walk adds to NP
    t = {x['label']: x['vals'][-1] for x in rows}
    assert abs(t['Gross profit'] + t['Total selling'] - t['OP before admin']) < 1e-6, s
    assert abs(t['OP before admin'] + t['Admin - people'] + t['Admin - non-people'] + t['Other op. income & FX'] - t['Operating profit']) < 1e-6
    assert abs(t['Operating profit'] + t['Net non-operating profit'] + t['Finance income (expense)'] + t['CIT (incl. PPA)'] + t['MI'] - t['Net profit']) < 1e-6
    return rows
d['bupl_cols'] = [a for a, _ in COLS]
d['bupl'] = {s: bupl(s) for s in ['2025', 'LE26', 'AP27', 'AP28']}
d['waxy_opba'] = {s: v('Waxy', OPBA, s) for s in ['2025', 'LE26', 'AP27', 'AP28']}
# short, executive commentary for the entity slide
cn5 = lambda sh, a, b: v(sh, OPBA, b) - v(sh, OPBA, a)
d['txt']['st_short'] = [
    ['{} → {}'.format(f0(v('TWIC', OPBA, 'LE26')), f0(v('TWIC', OPBA, 'AP27'))), 'TWIC turns profitable: largest Starch gain'],
    ['{} / {}'.format(sg(cn5('TDC', 'LE26', 'AP27')), sg(cn5('TDC2.0', 'LE26', 'AP27'))), 'TDC recovers; TDC 2.0 adds {} MB in year one'.format(f0(v('TDC2.0', OPBA, 'AP27')))],
    [sg(cn5('FoodWG', 'LE26', 'AP27')), 'Well Grow first full year: over half of Food\'s {}'.format(sg(cn5('FoodBU', 'LE26', 'AP27')))],
    ['{} → {}'.format(f0(v('BioPlastic', OPBA, 'LE26')), f0(v('BioPlastic', OPBA, 'AP27'))), 'Bioplastic loss nearly closed in the AP27 plan']]

# ---- texts that change in v4
T = d['txt']
b4 = d['bridge4']; inc = dict(b4['inc28']); s27 = dict(b4['steps27'])
T['br4_title'] = 'Each core BU adds {}–{} MB in AP2027; AP2028 adds a further {} MB'.format(
    round(min(s27['Food'], s27['HVA incl. Waxy'], s27['Starch'])), round(max(s27['Food'], s27['HVA incl. Waxy'], s27['Starch'])), ab(b4['ap28'] - b4['ap27']))
T['br4_note'] = ['2027 to 2028: ', 'HVA incl. Waxy adds {} MB (TDC 2.0), Food {}, Starch {} and NBG {}; AP2028 OPBA reaches {} MB. AP2028 is direction, not a commitment.'.format(
    sg(inc['HVA incl. Waxy']), sg(inc['Food']), sg(inc['Starch']), sg(inc['NBG']), f0(b4['ap28']))]
n = d['nbg']
T['nbg_story'] = ['{} → {}'.format(f0(n['2025']['nbg']), f0(n['LE26']['nbg'])),
                  'NBG 2025 to 2026 LE: discontinued businesses go from {} to zero; Bioplastic stays at {} and {}.'.format(f0(n['2025']['disc']), f0(n['2025']['bio']), f0(n['LE26']['bio']))]
T['nbg_plan'] = ['{} → {}'.format(f0(n['LE26']['bio']), f0(n['AP27']['bio'])), 'Bioplastic in AP2027 plan: loss cut to {} MB, the whole NBG improvement in 2027.'.format(f0(n['AP27']['bio']))]
cn = lambda sh, s: v(sh, OPBA, s)
T['china_story'] = ['{} → {}'.format(f0(cn('TWFZ', 'LE26')), f0(cn('TWFZ', 'AP27'))), 'TWFZ drives China ({}); TWIT broadly flat at {} MB.'.format(sg(cn('TotalCN', 'AP27') - cn('TotalCN', 'LE26')), f0(cn('TWIT', 'AP27')))]
T['walk_title'] = 'From BU OPBA to net profit: OPBA +{} MB in AP2027, net profit +{} MB'.format(ab(c(OPBA, 'AP27') - c(OPBA, 'LE26')), ab(c(NPL, 'AP27') - c(NPL, 'LE26')))
T['a28_cards'][1] = [f0(c(NPL, 'AP28')), 'Net profit', '{} MB vs AP27; includes a {} MB non-operating item at group level'.format(sg(c(NPL, 'AP28') - c(NPL, 'AP27')), f0(c('Net non-operating profit', 'AP28')))]
T['gl_items3'] = T['gl_items']
d['txt'] = T
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('bridge27 steps', [(a, round(b, 1)) for a, b in b4['steps27']], 'inc28', [(a, round(b, 1)) for a, b in b4['inc28']])
print('hidden buffer (ConsoAll OPBA - BU rows):', {k: round(x, 1) for k, x in d['buffer'].items()})
for k in ['br4_title', 'walk_title']: print(len(T[k]), T[k])
for k in ['br4_note', 'nbg_story', 'nbg_plan', 'china_story']: print(k, T[k])
for r in walk: print(r['label'].ljust(32), ['–' if x is None else round(x, 1) for x in r['vals']])



