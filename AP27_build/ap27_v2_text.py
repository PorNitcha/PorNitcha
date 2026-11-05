# Writes every sentence / formatted figure for the v2 deck (so the PowerPoint script only lays things out)
# usage: python ap27_v2_text.py ap27_v2.json   (adds key 'txt' and 'appx' in place)
import json, sys
P = sys.argv[1]
d = json.load(open(P, encoding='utf-8'))
pl = d['pl']; st = d['strip']; e = d['ent']
def f0(x):
    if x is None: return '–'
    if abs(x) < 0.5: return '–'
    return '({:,.0f})'.format(-x) if x < 0 else '{:,.0f}'.format(x)
def sg(x):
    if abs(x) < 0.5: return '0'
    return '+{:,.0f}'.format(x) if x > 0 else '({:,.0f})'.format(-x)
def pct(x, dp=0): return ('{:.%df}%%' % dp).format(x * 100)
def ab(x): return '{:,.0f}'.format(abs(x))
def gp(a, b): return '{:.0f}%'.format(abs(b / a - 1) * 100)
def gr(a, b): return '+{:.0f}%'.format((b / a - 1) * 100) if b >= a else '{:.0f}%'.format((b / a - 1) * 100)

o26, o27, o28 = st['LE26']['opba'], st['AP27']['opba'], st['AP28']['opba']
n26, n27, n28 = st['LE26']['np'], st['AP27']['np'], st['AP28']['np']
oo = d['oneoff']['LE26']; one26 = oo['other_inc'] + oo['fx'] + oo['nonop']
lfl = (n27 - n26) + one26
b27 = dict((n, x) for n, x in d['bridge27']['steps']); b28 = dict((n, x) for n, x in d['bridge28']['steps'])
fh = b27['Food'] + b27['HVA incl. Waxy']
def eo(sh, s): return e[sh]['opba'][s]
def dd(sh, a='LE26', b='AP27'): return e[sh]['opba'][b] - e[sh]['opba'][a]
food_m = lambda s: pl[s]['opba']['Food'] / pl[s]['ns']['Food']
hva_m = lambda s: pl[s]['opba']['HVA'] / pl[s]['ns']['HVA']
adm = d['admin']
def atot(s, k): return adm[s]['adp'][k] + adm[s]['adn'][k]
adm_ns = lambda s: -atot(s, 'TWPC') / st[s]['ns']
dadm = atot('AP27', 'TWPC') - atot('LE26', 'TWPC')
dtd2 = atot('AP27', 'TDC 2.0') - atot('LE26', 'TDC 2.0')
dth = atot('AP27', 'TH excl. TDC 2.0') - atot('LE26', 'TH excl. TDC 2.0')
dint = atot('AP27', 'International') - atot('LE26', 'International')
def eadm(x, s): return e[x]['adp'][s] + e[x]['adn'][s]
dvn = eadm('TotalVN', 'AP27') - eadm('TotalVN', 'LE26')
dsth_n = e['StarchTH']['adn']['AP27'] - e['StarchTH']['adn']['LE26']
dfood = eadm('FoodTH&WG', 'AP27') - eadm('FoodTH&WG', 'LE26')
dtdc = eadm('TDC', 'AP27') - eadm('TDC', 'LE26')
T = {}
T['g27'] = gr(o26, o27)
# ---- executive summary
T['ex_title'] = 'Executive summary: OPBA {} in AP2027, led by Food and HVA'.format(T['g27'])
T['ex'] = [
    [f0(o27), 'MB OPBA', 'AP2027 commitment: OPBA {} MB, net profit {} MB'.format(f0(o27), f0(n27)),
     'Net sales grow {} to {:,.1f} B and GP {} to {:,.2f} B (GM {}). OPBA rises {} MB on 2026 LE; net profit rises only {} MB because 2026 LE carries {} MB of FX gain and other income that AP2027 does not plan. Like-for-like, net profit grows about {} MB.'.format(
         gp(st['LE26']['ns'], st['AP27']['ns']), st['AP27']['ns'] / 1000, gp(st['LE26']['gp'], st['AP27']['gp']), st['AP27']['gp'] / 1000, pct(st['AP27']['gm'], 1),
         ab(o27 - o26), ab(n27 - n26), f0(one26), ab(lfl))],
    [sg(fh), 'MB from Food + HVA', 'Growth engines: Food and HVA deliver {} of the OPBA uplift'.format(pct(fh / (o27 - o26))),
     'Food reaches {} MB ({}): Well Grow\'s first full year adds {} MB and margin holds at {}. HVA incl. Waxy reaches {} MB ({}), with TDC {} and TDC 2.0 {}; Waxy moves to break-even, so HVA excl. Waxy is also {} MB. HVA OPBA margin improves from {} to {}.'.format(
         f0(pl['AP27']['opba']['Food']), sg(b27['Food']), ab(dd('FoodWG')), pct(food_m('AP27')), f0(pl['AP27']['opba']['HVA']), sg(b27['HVA incl. Waxy']),
         sg(dd('TDC')), sg(dd('TDC2.0')), f0(pl['AP27']['opba']['HVAex']), pct(hva_m('LE26'), 1), pct(hva_m('AP27'), 1))],
    [f0(o28), 'MB OPBA, AP2028', 'AP2028 direction: OPBA {} MB ({}), net profit {} MB'.format(f0(o28), gr(o27, o28), f0(n28)),
     'TDC 2.0 ramps up to {} MB OPBA and becomes the largest single uplift ({}), taking HVA incl. Waxy to {} MB; Food grows to {} MB.'.format(
         f0(eo('TDC2.0', 'AP28')), sg(dd('TDC2.0', 'AP27', 'AP28')), f0(pl['AP28']['opba']['HVA']), f0(pl['AP28']['opba']['Food']))],
    [pct(adm_ns('AP27'), 1), 'admin / net sales', 'Overheads: admin falls to {} of net sales ({} in 2026 LE)'.format(pct(adm_ns('AP27'), 1), pct(adm_ns('LE26'), 1)),
     'Admin rises {} MB: TDC 2.0 start-up adds {} and International {} (mainly Vietnam), while Thailand excl. TDC 2.0 is {} MB lower, helped by the Sep-26 asset impairment in 2026 LE not recurring.'.format(
         ab(dadm), ab(dtd2), ab(dint), ab(dth))]]
# ---- at a glance (right card)
T['gl_title'] = 'AP2027: OPBA {} to {} MB, but net profit only +{:.0f} MB to {} MB'.format(T['g27'], f0(o27), n27 - n26, f0(n27))
T['gl_items'] = [
    [sg(o27 - o26), 'OPBA vs 2026 LE: ', 'every BU grows; Food, HVA and Starch each add {}–{} MB'.format(round(min(b27['Food'], b27['Starch'], b27['HVA incl. Waxy'])), round(max(b27['Food'], b27['Starch'], b27['HVA incl. Waxy'])))],
    [pct(pl['AP27']['opba']['Food'] / (pl['AP27']['opba']['Food'] + pl['AP27']['opba']['HVA'] + pl['AP27']['opba']['Starch'])), 'of core-BU OPBA from Food: ', 'still the profit anchor; Well Grow adds a full year'],
    [gr(st['LE26']['vol'], st['AP27']['vol']), 'volume, GM flat: ', '{} vs {}; growth is volume-led'.format(pct(st['AP27']['gm'], 1), pct(st['LE26']['gm'], 1))],
    [sg(o27 - st['AP26']['opba']), 'vs AP2026 plan: ', 'AP2027 OPBA is still below last year\'s plan of {} MB'.format(f0(st['AP26']['opba']))]]
T['gl_28'] = ['OPBA, {} MB vs AP27 '.format(sg(o28 - o27)), 'led by TDC 2.0 ramp-up; net profit {} MB'.format(f0(n28))]
# ---- OPBA bridge
T['br_title'] = 'Food, HVA and Starch each add {}–{} MB; NBG moves close to break-even'.format(round(min(b27['Food'], b27['Starch'], b27['HVA incl. Waxy'])), round(max(b27['Food'], b27['Starch'], b27['HVA incl. Waxy'])))
T['br_note'] = ['Broad-based plan: ', 'Food {}, HVA incl. Waxy {} and Starch {} MB make up {} of the {} MB uplift; Corp and BU eliminations take back {} MB.'.format(
    sg(b27['Food']), sg(b27['HVA incl. Waxy']), sg(b27['Starch']), pct((b27['Food'] + b27['HVA incl. Waxy'] + b27['Starch']) / (o27 - o26)), sg(o27 - o26), f0(-b27['Corp / Elim']))]
T['drv'] = [
    ['Food', b27['Food'], [['Well Grow (full year)', dd('FoodWG')], ['Food TH', dd('FoodTH')], ['Food VN', dd('FoodVN')]]],
    ['HVA incl. Waxy', b27['HVA incl. Waxy'], [['TDC', dd('TDC')], ['TDC 2.0 (first year)', dd('TDC2.0')], ['Waxy', dd('Waxy')], ['TWIN', dd('TWIN')], ['TWII', dd('TWII')]]],
    ['Starch', b27['Starch'], [['Cambodia (TWIC)', dd('TWIC')], ['Starch TH', dd('StarchTH')], ['China', dd('TotalCN')], ['Vietnam', dd('TotalVN')]]],
    ['NBG', b27['NBG'], [['Bioplastic {} → {}'.format(f0(eo('NBGBU', 'LE26')), f0(eo('NBGBU', 'AP27'))), None]]],
    ['Corp / Elim', b27['Corp / Elim'], [['Corp cost and BU eliminations', None]]]]
# ---- entity slide stories
T['stories'] = [
    ['{} → {}'.format(f0(eo('TWIC', 'LE26')), f0(eo('TWIC', 'AP27'))), 'TWIC turns positive: the largest Starch gain'],
    ['{} → {}'.format(f0(eo('TDC2.0', 'AP27')), f0(eo('TDC2.0', 'AP28'))), 'TDC 2.0 starts in 2027 and scales in AP28'],
    [sg(dd('FoodWG')), 'Well Grow full year: over half of Food\'s uplift']]
# ---- OPBA -> NP
nb = dict((n, x) for n, x in d['np_bridge']['steps'])
T['np_title'] = 'OPBA {} MB but NP +{:.0f} MB: 2026 one-offs and TDC 2.0 costs absorb it'.format(sg(o27 - o26), n27 - n26)
T['np_note'] = ['Like-for-like NP grows about {} MB: '.format(ab(lfl)), '2026 LE carries {} MB of FX gain and other operating income that AP27 does not plan. Of the {} MB admin, TDC 2.0 is {} MB.'.format(f0(one26), sg(-nb['Admin']), f0(-dtd2))]
T['np_cal'] = [[sg(dtd2), 'TDC 2.0 overhead', 'Admin for TDC 2.0 rises from {} to {} MB in its first operating year.'.format(f0(-atot('LE26', 'TDC 2.0')), f0(-atot('AP27', 'TDC 2.0')))],
               [f0(one26), 'Not repeated in AP27', '2026 LE includes FX gain {}, other operating income {} and non-operating {} MB.'.format(f0(oo['fx']), f0(oo['other_inc']), f0(oo['nonop']))]]
T['np_ann'] = ['TDC 2.0 {}'.format(sg(dtd2)), 'FX {}, other {}'.format(f0(oo['fx']), f0(oo['other_inc']))]
# ---- admin slide
T['ad_title'] = 'Admin +{:.0f} MB in AP2027 is TDC 2.0 and International; Thailand is lower'.format(-dadm)
T['ad_cal'] = [
    [sg(dtd2), 'TDC 2.0 start-up', 'People {} and non-people {} MB as the plant starts operating; {} MB in AP28.'.format(
        sg(-(adm['AP27']['adp']['TDC 2.0'] - adm['LE26']['adp']['TDC 2.0'])), sg(-(adm['AP27']['adn']['TDC 2.0'] - adm['LE26']['adn']['TDC 2.0'])), f0(-atot('AP28', 'TDC 2.0')))],
    [sg(dth), 'Thailand excl. TDC 2.0', 'Starch TH non-people down {} MB (the ~23 MB Sep-26 asset impairment in 2026 LE does not recur) and TDC down {}, partly offset by Food TH & WG up {}.'.format(
        ab(dsth_n), ab(dtdc), ab(dfood))],
    [sg(dint), 'International', 'Vietnam {} MB, plus China and TWIN; Cambodia slightly lower.'.format(sg(-dvn))]]
T['ad_note'] = ['Admin / net sales {} → {} → {}: '.format(pct(adm_ns('LE26'), 1), pct(adm_ns('AP27'), 1), pct(adm_ns('AP28'), 1)),
                'overheads grow more slowly than the business; the AP2027 increase is the cost of starting TDC 2.0.']
# ---- AP28
T['a28_title'] = 'AP2028 direction: OPBA {} MB, with TDC 2.0 as the next growth engine'.format(f0(o28))
T['a28_ann'] = {'Food': 'Food TH {}\rFood VN {}'.format(sg(dd('FoodTH', 'AP27', 'AP28')), sg(dd('FoodVN', 'AP27', 'AP28'))),
                'HVA incl. Waxy': 'TDC 2.0 {}\rTDC {}'.format(sg(dd('TDC2.0', 'AP27', 'AP28')), sg(dd('TDC', 'AP27', 'AP28'))),
                'Starch': 'TWIC {}\rStarch TH {}'.format(sg(dd('TWIC', 'AP27', 'AP28')), sg(dd('StarchTH', 'AP27', 'AP28')))}
T['a28_note'] = ['Direction, not a commitment: ', '{} of the {} MB comes from HVA incl. Waxy; within it TDC 2.0 adds {} MB while legacy TDC gives back {} MB, so AP2028 depends on the TDC 2.0 volume ramp.'.format(
    pct(b28['HVA incl. Waxy'] / (o28 - o27)), sg(o28 - o27), sg(dd('TDC2.0', 'AP27', 'AP28')), f0(-dd('TDC', 'AP27', 'AP28')))]
T['a28_cards'] = [[f0(o28), 'OPBA', '{} MB vs AP27 ({})'.format(sg(o28 - o27), gr(o27, o28))],
                  [f0(n28), 'Net profit', '{} MB vs AP27; Corp/Elim NP {} MB includes a {} MB non-operating item'.format(sg(n28 - n27), f0(pl['AP28']['np']['CorpElim']), f0(d['oneoff']['AP28']['nonop']))],
                  [f0(pl['AP28']['opba']['HVA']), 'HVA incl. Waxy OPBA', 'TDC 2.0 {} MB vs legacy TDC {} MB'.format(f0(eo('TDC2.0', 'AP28')), f0(eo('TDC', 'AP28')))]]
# ---- multi-year summary
T['sum_title'] = 'Multi-year view: Food stays the anchor, HVA triples OPBA by AP2028'
T['sum_check'] = round(pl['AP28']['opba']['HVA'] / pl['LE26']['opba']['HVA'], 2)

# ---- appendix P&L tables (each column ties to ConsoAll by construction: Corp/Elim = ConsoAll - BUs)
COLS = [('Starch BU', 'Starch'), ('HVA excl. Waxy', 'HVAex'), ('Waxy', 'Waxy'), ('HVA incl. Waxy', 'HVA'), ('Food BU', 'Food'), ('NBG BU', 'NBG'), ('Corp / Elim', 'CorpElim'), ('TWPC (ConsoAll)', 'TWPC')]
def appx(s):
    p = pl[s]; rows = []
    def val(k, c): return p[k][c]
    def add(label, fn, kind='mb', key=False):
        rows.append({'label': label, 'kind': kind, 'key': key, 'vals': [fn(c) for _, c in COLS]})
    add('Volume (kt)', lambda c: None if c == 'CorpElim' else val('vol', c) / 1000, 'kt')
    add('Net sales', lambda c: val('ns', c), key=True)
    add('Gross profit', lambda c: val('gp', c), key=True)
    add('%GM', lambda c: (val('gp', c) / val('ns', c)) if c != 'CorpElim' and abs(val('ns', c)) > 0.5 else None, 'pct')
    add('DC', lambda c: val('dc', c)); add('A&P', lambda c: val('ap', c)); add('S&M', lambda c: val('sm', c))
    add('OP before admin', lambda c: val('opba', c), key=True)
    add('%OPBA', lambda c: (val('opba', c) / val('ns', c)) if c != 'CorpElim' and abs(val('ns', c)) > 0.5 else None, 'pct')
    add('Admin - people', lambda c: val('adp', c)); add('Admin - non-people', lambda c: val('adn', c))
    add('Other op. income & FX', lambda c: val('op', c) - val('opba', c) - val('adp', c) - val('adn', c))
    add('Operating profit', lambda c: val('op', c), key=True)
    add('Finance income (expense)', lambda c: val('fin', c))
    add('CIT & other', lambda c: val('np', c) - val('op', c) - val('fin', c) - val('mi', c))
    add('MI', lambda c: val('mi', c))
    add('Net profit', lambda c: val('np', c), key=True)
    return rows
d['appx_cols'] = [c for c, _ in COLS]
d['appx'] = {s: appx(s) for s in ['LE26', 'AP27', 'AP28']}
# self-check: in every appendix table, the four core BUs + Corp/Elim must add to the ConsoAll column
for s in d['appx']:
    for r in d['appx'][s]:
        if r['kind'] != 'mb': continue
        v = r['vals']; tot = v[0] + v[3] + v[4] + v[5] + v[6]
        assert abs(tot - v[7]) < 1e-6, (s, r['label'], tot, v[7])
d['txt'] = T
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k in ['ex_title', 'gl_title', 'br_title', 'np_title', 'ad_title', 'a28_title', 'sum_title']: print(k, len(T[k]), T[k])
for x in T['ex']: print('EX', x[0], '|', x[2], '|', x[3])
for x in T['ad_cal']: print('AD', x)
print('HVA x', T['sum_check'])


