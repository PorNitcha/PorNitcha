# v7 additions on top of ap27_v2.json (run after ap27_v4_data.py):
# - slide 3: % volume growth row, mix chart 2025-2028 with grey labels = ConsoAll total OPBA
# - slide 4: total incremental figures
# - 6 BU deep-dive tables (3 BUs x 2 horizons) down to OPBA + per-kg block, with data-driven per-kg takeaways
# usage: python ap27_v7_data.py sheets.json ap27_v2.json
import json, sys
X = json.load(open(sys.argv[1], encoding='utf-8'))
P = sys.argv[2]
d = json.load(open(P, encoding='utf-8'))
def v(sh, line, s): return X[sh][line][s]
OPBA = 'OP Before Admin'
PREV = {'R24': 'Y23', '2025': 'R24', 'LE26': '2025', 'AP27': 'LE26', 'AP28': 'AP27'}
YL = {'2025': '2025', 'LE26': '2026 LE', 'AP27': '2027 AP', 'AP28': '2028 AP'}

# ---- slide 3
d['volg'] = {s: v('ConsoAll', 'Volume', s) / v('ConsoAll', 'Volume', PREV[s]) - 1 for s in ['R24', '2025', 'LE26', 'AP27', 'AP28']}
d['mix_total'] = {s: v('ConsoAll', OPBA, s) for s in ['2025', 'LE26', 'AP27', 'AP28']}   # grey label = left-chart total, not the sum of the bars

# ---- slide 4
d['inc_total'] = {'AP27': v('ConsoAll', OPBA, 'AP27') - v('ConsoAll', OPBA, 'LE26'), 'AP28': v('ConsoAll', OPBA, 'AP28') - v('ConsoAll', OPBA, 'AP27')}

# ---- BU deep dives
BU = {
    'Starch': {'title': 'Starch BU', 'cols': [('Starch TH', 'StarchTH'), ('TWIT', 'TWIT'), ('TWFZ', 'TWFZ'), ('TWIC', 'TWIC'), ('Vietnam', 'TotalVN'), ('Total Starch BU', 'StarchBU')],
               'note': 'Total Starch BU includes intercompany eliminations between entities, so the entity columns do not add up to the total.'},
    'HVA': {'title': 'HVA BU', 'cols': [('TDC', 'TDC'), ('TDC 2.0', 'TDC2.0'), ('Waxy', 'Waxy'), ('TWIN', 'TWIN'), ('TWII', 'TWII'), ('Total HVA BU', 'HVA incl Waxy')],
            'note': 'Total HVA BU = HVA incl. Waxy (sheet "HVA incl Waxy"); includes eliminations between HVA entities.'},
    'Food': {'title': 'Food BU', 'cols': [('Food TH', 'FoodTH'), ('Domestic', 'FoodTH.Dom'), ('Export', 'FoodTH.Exp'), ('WG', 'FoodWG'), ('Food VN', 'FoodVN'), ('Total Food BU', 'FoodBU')],
             'note': 'Food TH = Domestic + Export. Total Food BU = Food TH + WG + Food VN after eliminations.'}}
def kg(sh, line, s):
    vol = v(sh, 'Volume', s)
    if vol < 0.5: return None
    if line == 'gpadc': return (v(sh, 'Gross profit', s) + v(sh, 'DC', s)) * 1000 / vol
    return v(sh, line, s) * 1000 / vol
def table(bu, s):
    rows = []
    def r(label, fn, kind='mb', key=False, sect=None):
        rows.append({'label': label, 'kind': kind, 'key': key, 'sect': sect, 'vals': [fn(sh) for _, sh in BU[bu]['cols']]})
    ns = lambda sh: v(sh, 'Net Sales', s)
    sell = lambda sh: v(sh, 'DC', s) + v(sh, 'A&P', s) + v(sh, 'S&M', s)
    pct = lambda num, den: (num / den) if abs(den) > 0.5 else None
    r('Volume (kt)', lambda sh: v(sh, 'Volume', s) / 1000, 'kt')
    r('% Vol growth', lambda sh: (v(sh, 'Volume', s) / v(sh, 'Volume', PREV[s]) - 1) if v(sh, 'Volume', PREV[s]) > 0.5 else None, 'pct')
    r('Net sales', ns, key=True)
    r('Cost of sales (total)', lambda sh: v(sh, 'Total COST', s))
    r('Gross profit', lambda sh: v(sh, 'Gross profit', s), key=True)
    r('%GM', lambda sh: pct(v(sh, 'Gross profit', s), ns(sh)), 'pct')
    r('DC', lambda sh: v(sh, 'DC', s)); r('A&P', lambda sh: v(sh, 'A&P', s)); r('S&M', lambda sh: v(sh, 'S&M', s))
    r('Total selling', sell, key=True)
    r('% selling', lambda sh: pct(sell(sh), ns(sh)), 'pct')
    r('OP before admin (OPBA)', lambda sh: v(sh, OPBA, s), key=True)
    r('%OPBA', lambda sh: pct(v(sh, OPBA, s), ns(sh)), 'pct')
    r('Net sales / kg', lambda sh: kg(sh, 'Net Sales', s), 'kg', sect='PER KG (THB/kg)')
    r('COGS / kg', lambda sh: kg(sh, 'Total COST', s), 'kg')
    r('GP / kg', lambda sh: kg(sh, 'Gross profit', s), 'kg', key=True)
    r('DC / kg', lambda sh: kg(sh, 'DC', s), 'kg')
    r('GP after DC / kg', lambda sh: kg(sh, 'gpadc', s), 'kg', key=True)
    for x in rows:   # self-checks on every column
        pass
    t = {x['label']: x['vals'] for x in rows}
    for j in range(len(BU[bu]['cols'])):
        assert abs(t['Gross profit'][j] + t['Total selling'][j] - t['OP before admin (OPBA)'][j]) < 1e-6, (bu, s, j)
        if t['GP / kg'][j] is not None:
            assert abs(t['Net sales / kg'][j] + t['COGS / kg'][j] - t['GP / kg'][j]) < 1e-6
            assert abs(t['GP / kg'][j] + t['DC / kg'][j] - t['GP after DC / kg'][j]) < 1e-6
    return rows
d['dd'] = {bu: {'title': BU[bu]['title'], 'cols': [c for c, _ in BU[bu]['cols']], 'note': BU[bu]['note'],
                'years': {s: table(bu, s) for s in ['2025', 'LE26', 'AP27', 'AP28']}} for bu in BU}

# ---- per-kg takeaways (runs of [text, bold]); every number comes from the tables above
def f2(x): return '{:,.2f}'.format(x)
def chg(a, b, unit=' THB/kg'):
    dx = b - a; p = (dx / abs(a) * 100) if abs(a) > 1e-9 else 0
    return '{}{:,.2f}{} ({}{:.0f}%)'.format('+' if dx >= 0 else '–', abs(dx), unit, '+' if p >= 0 else '–', abs(p))
def up(a, b, more='rises', less='falls'): return more if b >= a else less
def mb(x): return '{}{:,.0f} MB'.format('+' if x >= 0 else '–', abs(x))
def takeaways(bu, a, b):
    k = lambda sh, line, s: kg(sh, line, s)
    if bu == 'Starch':
        T = 'StarchBU'
        ents = [('Starch TH', 'StarchTH'), ('TWIT', 'TWIT'), ('TWFZ', 'TWFZ'), ('TWIC', 'TWIC'), ('Vietnam', 'TotalVN')]
        g = [(n, k(sh, 'gpadc', a), k(sh, 'gpadc', b)) for n, sh in ents if k(sh, 'gpadc', a) is not None and k(sh, 'gpadc', b) is not None and v(sh, 'Volume', a) >= 1000]   # ignore start-up bases < 1 kt
        best = max(g, key=lambda x: x[2] - x[1]); worst = min(g, key=lambda x: x[2] - x[1])
        rank = sorted([(n, k(sh, 'gpadc', b)) for n, sh in ents if k(sh, 'gpadc', b) is not None], key=lambda x: -x[1])
        return [
            [['Spread: ', True], ['ASP {} → {} and COGS/kg {} → {} THB/kg, so '.format(f2(k(T, 'Net Sales', a)), f2(k(T, 'Net Sales', b)), f2(-k(T, 'Total COST', a)), f2(-k(T, 'Total COST', b))), False],
             ['GP/kg moves {} to {}'.format(chg(k(T, 'Gross profit', a), k(T, 'Gross profit', b)), f2(k(T, 'Gross profit', b))), True], ['.', False]],
            [['Entities ({}): '.format(YL[b]), True], ['GP after DC/kg ' + ', '.join('{} {}'.format(n, f2(x)) for n, x in rank) + '. ', False],
             ['Largest gain: {} {}'.format(best[0], chg(best[1], best[2])), True], ['; {}: {} {}.'.format('smallest' if worst[2] - worst[1] >= 0 else 'decline', worst[0], chg(worst[1], worst[2])), False]],
            [['Logistics: ', True], ['DC/kg {} → {} THB/kg; '.format(f2(-k(T, 'DC', a)), f2(-k(T, 'DC', b))), False],
             ['GP after DC/kg {} to {}'.format(chg(k(T, 'gpadc', a), k(T, 'gpadc', b)), f2(k(T, 'gpadc', b))), True],
             ['; OPBA {}.'.format(mb(v(T, OPBA, b) - v(T, OPBA, a))), False]]]
    if bu == 'HVA':
        T = 'HVA incl Waxy'
        sh2 = lambda s: v('TDC2.0', 'Volume', s) / v(T, 'Volume', s)
        vg = v(T, 'Volume', b) / v(T, 'Volume', a) - 1
        cg_a, cg_b = -k(T, 'Total COST', a), -k(T, 'Total COST', b)
        tdc2 = k('TDC2.0', 'Gross profit', b); tdc = k('TDC', 'Gross profit', b)
        return [
            [['Mix: ', True], ['TDC 2.0 rises from {:.0f}% to {:.0f}% of HVA volume; HVA net sales/kg {} '.format(sh2(a) * 100, sh2(b) * 100, up(k(T, 'Net Sales', a), k(T, 'Net Sales', b))), False],
             [chg(k(T, 'Net Sales', a), k(T, 'Net Sales', b)), True], [' to {}.'.format(f2(k(T, 'Net Sales', b))), False]],
            [['Unit margin: ', True], ['GP after DC/kg {} to {}'.format(chg(k(T, 'gpadc', a), k(T, 'gpadc', b)), f2(k(T, 'gpadc', b))), True],
             ['; in {} TDC 2.0 earns {} GP/kg vs TDC {}.'.format(YL[b], f2(tdc2) if tdc2 is not None else 'n.m.', f2(tdc)), False]],
            [['Cost absorption: ', True], ['volume {}{:.0f}% while COGS/kg {} {} → {} THB/kg'.format('+' if vg >= 0 else '–', abs(vg) * 100, up(cg_a, cg_b), f2(cg_a), f2(cg_b)), False],
             ['; OPBA {}.'.format(mb(v(T, OPBA, b) - v(T, OPBA, a))), True]]]
    if bu == 'Food':
        T = 'FoodBU'
        return [
            [['Channel ({}): '.format(YL[b]), True], ['Export {} vs Domestic {} net sales/kg; '.format(f2(k('FoodTH.Exp', 'Net Sales', b)), f2(k('FoodTH.Dom', 'Net Sales', b))), False],
             ['GP after DC/kg Export {} vs Domestic {}'.format(f2(k('FoodTH.Exp', 'gpadc', b)), f2(k('FoodTH.Dom', 'gpadc', b))), True], ['.', False]],
            [['Geography: ', True], ['GP after DC/kg Food TH {} → {}, Food VN {} → {} THB/kg: '.format(f2(k('FoodTH', 'gpadc', a)), f2(k('FoodTH', 'gpadc', b)), f2(k('FoodVN', 'gpadc', a)), f2(k('FoodVN', 'gpadc', b))), False],
             ['Food VN {}'.format(chg(k('FoodVN', 'gpadc', a), k('FoodVN', 'gpadc', b))), True], ['; Well Grow at {} THB/kg lifts the BU average.'.format(f2(k('FoodWG', 'gpadc', b))), False]],
            [['Cost & freight: ', True], ['COGS/kg {} → {}, DC/kg {} → {} THB/kg; '.format(f2(-k(T, 'Total COST', a)), f2(-k(T, 'Total COST', b)), f2(-k(T, 'DC', a)), f2(-k(T, 'DC', b))), False],
             ['GP after DC/kg {}'.format(chg(k(T, 'gpadc', a), k(T, 'gpadc', b))), True], [', OPBA {}.'.format(mb(v(T, OPBA, b) - v(T, OPBA, a))), False]]]
for bu in BU:
    d['dd'][bu]['take'] = {'A': takeaways(bu, 'LE26', 'AP27'), 'B': takeaways(bu, 'AP27', 'AP28')}
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('volg', {s: round(x * 100, 1) for s, x in d['volg'].items()}, 'inc', {s: round(x, 1) for s, x in d['inc_total'].items()})
for bu in BU:
    for h in ['A', 'B']:
        for bl in d['dd'][bu]['take'][h]:
            print(bu, h, '|', ''.join(t for t, _ in bl))
r = d['dd']['Starch']['years']['AP27']
for x in r: print(x['label'].ljust(24), [None if y is None else round(y, 2) for y in x['vals']])



