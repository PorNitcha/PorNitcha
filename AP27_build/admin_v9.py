# Slide 7 v9: Admin P / Non-P split Thailand vs International (Por's definition, 02-Nov-2026)
# International = TWIT, TWFZ, VTC, TNT, TWII, TWIN, TWIP, Food VN; Thailand = ConsoAll - International (balancing, incl. TWIC, TDC 2.0, eliminations, Corp)
# usage: python admin_v9.py sheets.json ap27_v2.json
import json, sys
X = json.load(open(sys.argv[1], encoding='utf-8'))
P = sys.argv[2]; d = json.load(open(P, encoding='utf-8'))
INTER = ['TWIT', 'TWFZ', 'TWIC', 'VTC', 'TNT', 'TWII', 'TWIN', 'TWIP', 'FoodVN']   # TWIC in International (Por, 04-Nov) = Waterfall_TH basis
L = {'adp': 'admin exp - People', 'adn': 'admin exp - Non-people'}
SC = ['2025', 'AP26', 'LE26', 'AP27']
def v(sh, k, s): return X[sh][L[k]][s]
a2 = {}
for s in SC:
    r = {}
    for k in L:
        tot = v('ConsoAll', k, s); it = sum(v(x, k, s) for x in INTER)
        r[k] = {'Thailand': tot - it, 'International': it, 'TWPC': tot, 'TDC 2.0': v('TDC2.0', k, s)}
    r['ns'] = X['ConsoAll']['Net Sales'][s]
    a2[s] = r
d['admin2'] = a2
def tot(s, g): return a2[s]['adp'][g] + a2[s]['adn'][g]
def ent(sh, s): return v(sh, 'adp', s) + v(sh, 'adn', s)
def sg(x): return '0' if abs(x) < 0.5 else ('+{:,.0f}'.format(x) if x > 0 else '({:,.0f})'.format(-x))
def ab(x): return '{:,.0f}'.format(abs(x))
dT = tot('AP27', 'TWPC') - tot('LE26', 'TWPC'); dTH = tot('AP27', 'Thailand') - tot('LE26', 'Thailand'); dIN = tot('AP27', 'International') - tot('LE26', 'International')
dT2 = tot('AP27', 'TDC 2.0') - tot('LE26', 'TDC 2.0'); dTHx = dTH - dT2
dVN = (ent('TNT', 'AP27') + ent('VTC', 'AP27')) - (ent('TNT', 'LE26') + ent('VTC', 'LE26'))
dCN = (ent('TWIT', 'AP27') + ent('TWFZ', 'AP27')) - (ent('TWIT', 'LE26') + ent('TWFZ', 'LE26'))
dHI = sum(ent(x, 'AP27') - ent(x, 'LE26') for x in ['TWIN', 'TWII', 'TWIP'])
dFV = ent('FoodVN', 'AP27') - ent('FoodVN', 'LE26'); dTW = ent('TWIC', 'AP27') - ent('TWIC', 'LE26')
dSTn = v('StarchTH', 'adn', 'AP27') - v('StarchTH', 'adn', 'LE26'); dTDC = ent('TDC', 'AP27') - ent('TDC', 'LE26'); dFTH = ent('FoodTH&WG', 'AP27') - ent('FoodTH&WG', 'LE26')
T = d['txt']
T['ad9_title'] = 'Admin +{:.0f} MB in AP2027: TDC 2.0 and International up, rest of TH lower'.format(-dT)
T['ad9_cal'] = [
    [sg(-dT2), 'TDC 2.0 start-up (in Thailand)', 'People {} and non-people {} MB as the plant starts operating; {} MB in AP28.'.format(
        sg(-(v('TDC2.0', 'adp', 'AP27') - v('TDC2.0', 'adp', 'LE26'))), sg(-(v('TDC2.0', 'adn', 'AP27') - v('TDC2.0', 'adn', 'LE26'))), ab(ent('TDC2.0', 'AP28')))],
    [sg(-dTHx), 'Thailand excl. TDC 2.0', 'Starch TH non-people down {} MB (the ~23 MB Sep-26 asset impairment in 2026 LE does not recur) and TDC down {}, partly offset by Food TH & WG up {}.'.format(ab(dSTn), ab(dTDC), ab(dFTH))],
    [sg(-dIN), 'International', ', '.join('{} {}'.format(n, sg(-x)) for n, x in [('Vietnam (TNT, VTC)', dVN), ('China (TWIT, TWFZ)', dCN), ('Cambodia (TWIC)', dTW), ('TWIN / TWII / TWIP', dHI), ('Food VN', dFV)] if abs(x) >= 0.5) + ' MB.']]
T['ad9_note'] = ['Admin / net sales {:.1f}% → {:.1f}%: '.format(-tot('LE26', 'TWPC') / a2['LE26']['ns'] * 100, -tot('AP27', 'TWPC') / a2['AP27']['ns'] * 100),
                 'overheads grow more slowly than the business; the AP2027 increase is mainly the cost of starting TDC 2.0.']
# exec summary (slide 2) admin bullet uses the same TH / International definition
T['ex'][3][3] = 'Admin rises {} MB: TDC 2.0 start-up adds {} and International {} (mainly Vietnam), while Thailand excl. TDC 2.0 is {} MB lower, helped by the Sep-26 asset impairment in 2026 LE not recurring.'.format(ab(dT), ab(dT2), ab(dIN), ab(dTHx))
print('EX4:', T['ex'][3][3])
d['txt'] = T
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for s in SC:
    print(s, {k: {g: round(x, 1) for g, x in a2[s][k].items()} for k in L})
print('change AP27 vs LE26: total', round(dT, 1), 'TH', round(dTH, 1), '(TDC2.0', round(dT2, 1), ', TH excl', round(dTHx, 1), ') Inter', round(dIN, 1))
print(len(T['ad9_title']), T['ad9_title']); [print(c) for c in T['ad9_cal']]; print(T['ad9_note'])




