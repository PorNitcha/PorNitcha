import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import hva_format
"""v7: key accounts (>= 10% of a reaction's 2027 volume) tracked as named rows; the tail in equal-width tiers (gap per reaction) so no tail tier exceeds ~15%.
Plant % vol added for Rayong / TKT in the FY and quarterly blocks. Empty tiers (no volume in any period) are hidden."""
import json, collections, csv, re, math, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL

OUT = r"C:/Users/NitchaSuwongtham/OneDrive - THAIWAH/Desktop/lovely/HVA GP tier tracker 2027 v11.xlsx"
SRC = 'topline_final_copy.xlsx'
RX = ['PO-XL', 'XL', 'PO', 'AC', 'MX', 'Others']
def grid(lo, hi, gap, extra=()):
    n = int(round((hi - lo) / gap)); c = [round(lo + i * gap, 4) for i in range(n + 1)] + [round(x, 4) for x in extra]
    return sorted(set(c))
CUTS = {'PO-XL': grid(2.0, 10.0, 0.5, (5.25, 7.25)), 'XL': grid(0.0, 5.0, 0.5), 'PO': grid(2.0, 8.0, 0.5, (5.25,)), 'AC': grid(7.0, 13.0, 0.5, (11.25,)), 'MX': grid(2.0, 13.0, 0.5), 'Others': grid(2.0, 16.0, 0.5)}
GRIDTXT = {'PO-XL': '0.5 THB/kg (5.0-5.5 and 7.0-7.5 split at 0.25)', 'XL': '0.5 THB/kg', 'PO': '0.5 THB/kg (5.0-5.5 split at 0.25)', 'AC': '0.5 THB/kg (11.0-11.5 split at 0.25)', 'MX': '0.5 THB/kg', 'Others': '0.5 THB/kg'}
KEY_SHARE = 0.10   # customer x reaction with >= this share of the reaction's 2027 plan is a key account (own row)
FLOOR = {'PO-XL': 4.0, 'XL': 2.0, 'PO': 4.0, 'AC': 7.0, 'MX': 3.0, 'Others': 4.0}
TARGET_LO = {'PO-XL': 6.0, 'XL': 3.2, 'PO': 5.5, 'AC': 9.5, 'MX': 4.0, 'Others': 6.0}
RXMAP = {'PX': 'PO-XL', 'XL': 'XL', 'PR': 'PO', 'PO': 'PO', 'AC': 'AC', 'MX': 'MX'}
QS = ['Q1', 'Q2', 'Q3', 'Q4']; MIN_T = 1.0; PLANT = {'TDC': 'RY', 'TKT': 'TKT'}

def norm(n):
    n = str(n).upper().replace('BJ.', '').replace('ฟู๊ด', 'ฟู้ด'); n = re.sub(r'[^A-Z0-9ก-๙]+', '', n); return n[:16]
ALIAS = {'HUIFALINXIAFOODS': 'HUIFA', 'QINGDAOMIRACLESU': 'HUIFA', 'QINGDAOMIRACLE': 'HUIFA', 'MORIIFOODSINC': 'MORIIFOODS', 'FOODTRENDANDSUPE': 'FOODTREND'}
key = lambda n: ALIAS.get(norm(n), norm(n)); num = lambda v: v if isinstance(v, (int, float)) else 0.0
import bisect
def cuts(rx): return CUTS[rx]
def ntier(rx): return len(cuts(rx)) + 1
def tier_of(rx, g): return bisect.bisect_right(cuts(rx), g + 1e-9)
def tname(rx, k):
    c = cuts(rx)
    if k == 0: return f'< {c[0]:g}'
    if k == len(c): return f'\u2265 {c[-1]:g}'
    return f'{c[k-1]:g} \u2013 {c[k]:g}'
def zone_g(rx, g): return 'Below floor' if g < FLOOR[rx] else 'Floor to target' if g < TARGET_LO[rx] else 'Target and above'
def zone(rx, k):
    c = cuts(rx); lo = -1e9 if k == 0 else c[k - 1]; hi = 1e9 if k == len(c) else c[k]
    if hi <= FLOOR[rx]: return 'Below floor'
    if lo >= TARGET_LO[rx]: return 'Target and above'
    if hi <= TARGET_LO[rx]: return 'Floor to target'
    return 'Floor to target'
ZONEF = {'Below floor': 'F8D7D3', 'Floor to target': 'FFF2CC', 'Target and above': 'DDEFD9'}
def action(rx, g):
    fl, lo = FLOOR[rx], TARGET_LO[rx]
    if g < fl: return fl, 'reprice to floor or exit'
    if g < lo: return g + 0.5 * (lo - g), 'pass-through: half-way to target band'
    return g, 'hold'

# ---------- history ----------
T = json.load(open('tiers.json', encoding='utf-8'))
H = {}
for rx in RX:
    for l in T[rx]['lines']: H[(key(l['name']), rx)] = l
code2grp = {}
for r in csv.DictReader(open('data_actual.csv', encoding='utf-8')):
    if r['Customer Code']: code2grp[str(r['Customer Code']).strip()] = r['Customer name (Group)']

# ---------- 2027 plan ----------
wb_src = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
raw = [r for r in wb_src['data'].iter_rows(min_row=8, values_only=True) if r[6] not in (None, '')]
VOL = list(range(78, 90)); COGS = list(range(198, 210)); GP = list(range(222, 234))
lines = []
for r in raw:
    vols = [num(r[j]) for j in VOL]
    if sum(vols) <= 0: continue
    code = str(r[5]).strip() if r[5] not in (None, '-', '') else ''; grp = code2grp.get(code) or r[6]
    lines.append({'rx': RXMAP.get(r[0], 'Others'), 'reactor': r[0], 'plant': PLANT.get(r[3], r[3]), 'grp': grp, 'key': key(grp), 'name': r[6], 'code': code, 'apseg': r[1], 'country': r[9], 'sn': r[11], 'trade': r[12], 'src': r[4],
                  'vol': vols, 'cogs': [num(r[j]) * 1e6 for j in COGS], 'gp': [num(r[j]) * 1e6 for j in GP]})
sncost = collections.defaultdict(lambda: {'RY': [0.0, 0.0], 'TKT': [0.0, 0.0]})
for l in lines:
    x = sncost[(l['rx'], l['sn'])][l['plant']]; x[0] += sum(l['vol']); x[1] += sum(l['cogs'])
gap_sn = {}; gap_rx = collections.defaultdict(lambda: [0.0, 0.0])
for k, d in sncost.items():
    if d['RY'][0] > 0 and d['TKT'][0] > 0:
        g = (d['RY'][1] / d['RY'][0] - d['TKT'][1] / d['TKT'][0]) / 1000; gap_sn[k] = g; gap_rx[k[0]][0] += g * d['TKT'][0]; gap_rx[k[0]][1] += d['TKT'][0]
GAP = {rx: (v[0] / v[1] if v[1] else 0.0) for rx, v in gap_rx.items()}
for l in lines: l['gap'] = 0.0 if l['plant'] == 'RY' else gap_sn.get((l['rx'], l['sn']), GAP.get(l['rx'], 0.0))
apt = collections.defaultdict(lambda: [0.0, 0.0])
for l in lines:
    a = apt[(l['rx'], l['plant'])]; a[0] += sum(l['vol']); a[1] += sum(l['gp'])
APT = {k: v[1] / v[0] / 1000 for k, v in apt.items() if v[0]}
C = collections.defaultdict(lambda: {'grp': '', 'vol': {'RY': [0.0] * 4, 'TKT': [0.0] * 4}, 'gp': {'RY': [0.0] * 4, 'TKT': [0.0] * 4}, 'gcom': [0.0] * 4, 'lines': []})
for l in lines:
    c = C[(l['rx'], l['key'])]; c['grp'] = c['grp'] or l['grp']; c['lines'].append(l)
    for m in range(12):
        q = m // 3; v = l['vol'][m]; c['vol'][l['plant']][q] += v; c['gp'][l['plant']][q] += l['gp'][m]; c['gcom'][q] += l['gp'][m] - l['gap'] * v * 1000
RXTOT = collections.defaultdict(float)
for (rx, k), c in C.items():
    c['t'] = sum(c['vol']['RY']) + sum(c['vol']['TKT']); c['g'] = sum(c['gcom']) / c['t'] / 1000; RXTOT[rx] += c['t']
    h = H.get((k, rx)); c['new'] = not (h and (h['t25'] or h['t26'])); c['h'] = h
    c['tier'] = tier_of(rx, c['g']); c['g_act'], c['act'] = action(rx, c['g']); c['tier_act'] = tier_of(rx, c['g_act'])
for (rx, k), c in C.items(): c['keyacc'] = c['t'] / RXTOT[rx] >= KEY_SHARE
KEYS = {rx: sorted([k for (r_, k) in C if r_ == rx and C[(r_, k)]['keyacc']], key=lambda k: -C[(rx, k)]['t']) for rx in RX}

# row model: per reaction a list of rows: ('key', k) then ('tier', idx); each row has period cells
def z(): return {'n': 0, 'new_n': 0, 't': 0.0, 'gp': 0.0, 'ry_t': 0.0, 'ry_gp': 0.0, 'tk_t': 0.0, 'tk_gp': 0.0, 'top': 0.0}
def hz(): return {'n': 0, 't': 0.0, 'gp': 0.0}
ROWS = {}; CELL = {}
def newcell(): return {'25': hz(), '26': hz(), 'FY': z(), 'Q1': z(), 'Q2': z(), 'Q3': z(), 'Q4': z(), 'A': {'n': 0, 't': 0.0, 'gp': 0.0, 'up': 0.0}}
for rx in RX:
    rows = [('tier', i) for i in range(ntier(rx))]
    ROWS[rx] = rows
    for rid in rows: CELL[(rx, rid)] = newcell()
    for k in KEYS[rx]: CELL[(rx, ('key', k))] = newcell()
keyset = {rx: set(KEYS[rx]) for rx in RX}
for (k, rx), l in H.items():
    for y in ('25', '26'):
        t, g = l['t' + y], l['gp' + y]
        if not t or g is None: continue
        for r_ in ([('tier', tier_of(rx, g / 1000))] + ([('key', k)] if k in keyset[rx] else [])):
            a = CELL[(rx, r_)][y]; a['t'] += t; a['gp'] += t * g / 1000
            if t >= MIN_T: a['n'] += 1
for (rx, k), c in C.items():
  for rid in ([('tier', c['tier'])] + ([('key', k)] if c['keyacc'] else [])):
    for p in ['FY'] + QS:
        idx = range(4) if p == 'FY' else [QS.index(p)]
        ry = sum(c['vol']['RY'][i] for i in idx); tk = sum(c['vol']['TKT'][i] for i in idx); t = ry + tk
        if t <= 0: continue
        a = CELL[(rx, rid)][p]; a['t'] += t; a['gp'] += sum(c['gcom'][i] for i in idx) / 1000
        a['ry_t'] += ry; a['ry_gp'] += sum(c['gp']['RY'][i] for i in idx) / 1000; a['tk_t'] += tk; a['tk_gp'] += sum(c['gp']['TKT'][i] for i in idx) / 1000; a['top'] = max(a['top'], t)
        if t >= MIN_T:
            a['n'] += 1
            if c['new']: a['new_n'] += 1
    rida = ('key', k) if rid[0] == 'key' else ('tier', c['tier_act'])
    b = CELL[(rx, rida)]['A']; b['t'] += c['t']; b['gp'] += c['t'] * c['g_act']; b['up'] += c['t'] * (c['g_act'] - c['g'])
    if c['t'] >= MIN_T: b['n'] += 1

# ---------- workbook ----------
wb = openpyxl.load_workbook(OUT)
NAVY = '1F3A5F'; BLUE = '0000FF'; HFNT = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor=NAVY); SUBF = PatternFill('solid', fgColor='DCE3EC'); GREY = 'F2F2F2'; KEYF = 'E4ECF7'
PERF = {'25': 'E8EEF6', '26': 'FBEFE6', '27': 'E7F3EC', 'Q': 'F3F6F9', 'A': 'FFF7E0'}
thin = Side(style='thin', color='BFBFBF'); med = Side(style='medium', color=NAVY)
NUM, PCT, DEC, MB = '#,##0', '0%', '0.00', '#,##0.0'
def fresh(name, pos):
    if name in wb.sheetnames: del wb[name]
    return wb.create_sheet(name, pos)
ws = fresh('Tier mapping 25-26-27', 1); ws.sheet_view.showGridLines = False
ws['A1'] = 'GP/kg tier mapping by reaction (0.5 THB/kg tiers, finer where volume clusters) · 2025 actual · 2026 YTD · 2027 AP plan FY and by quarter · price-action case'; ws['A1'].font = Font(bold=True, size=13, color=NAVY)
ws['A2'] = (f'Product GP per kg = net sales - Actual Cost (col AF) - F&I (col BX). Tier rows include every customer. A customer x reaction with at least {KEY_SHARE*100:.0f}% of the reaction plan is a KEY ACCOUNT: it is shown as a star memo row under its 2027 tier (indented, not added again), with its own 2025 / 2026 actuals and its share of the tier in "Top cust %". '
            'Tiers empty in every period are hidden; tiers with history but no 2027 volume are grouped and collapsed (use the + at the left to expand). Zone colour = position against the price floor and the target band. '
            '2027 tier = commercial GP/kg at Rayong cost (TKT rows less the measured same-SN cost gap). % vol = share of the reaction (total column) or of that plant volume (Rayong / TKT columns).')
ws['A2'].alignment = Alignment(wrap_text=True, vertical='top'); ws.merge_cells('A2:Z2'); ws.row_dimensions[2].height = 64
cols = [('', 'Tier / key account'), ('', 'Zone')]
for lab in ('2025 actual (FY)', '2026 YTD (Jan–Sep)'): cols += [(lab, s) for s in ('# cust', 'Tonnes', '% vol', 'GP/kg', 'GP THB M')]
cols += [('2027 AP plan FY (Rayong + TKT)', s) for s in ('# cust', 'of which new', 'Tonnes', '% vol', 'Top cust %', 'GP/kg', 'GP THB M')]
cols += [('2027 FY Rayong', s) for s in ('Tonnes', '% of RY', 'Plant GP/kg')] + [('2027 FY TKT', s) for s in ('Tonnes', '% of TKT', 'Plant GP/kg')]
cols += [('Δ FY27 vs 2025', '% vol pts')]
QW = 10
for q in QS: cols += [(f'2027 {q} AP plan', s) for s in ('# cust', 'Tonnes', '% vol', 'GP/kg', 'Rayong t', '% of RY', 'Rayong GP/kg', 'TKT t', '% of TKT', 'TKT GP/kg')]
cols += [('2027 FY price-action case (floor + pass-through)', s) for s in ('# cust', 'Tonnes', '% vol', 'GP/kg', 'GP THB M', 'Uplift THB M')]
NC = len(cols); QB = 27; AB = QB + QW * 4
c0 = 1
while c0 <= NC:
    g = cols[c0 - 1][0]; c1 = c0
    while c1 + 1 <= NC and cols[c1][0] == g: c1 += 1
    if g:
        ws.cell(row=4, column=c0, value=g)
        if c1 > c0: ws.merge_cells(start_row=4, start_column=c0, end_row=4, end_column=c1)
        cell = ws.cell(row=4, column=c0); cell.font = HFNT; cell.fill = HF; cell.alignment = Alignment(horizontal='center')
    c0 = c1 + 1
for j, (_, s) in enumerate(cols, 1):
    c = ws.cell(row=5, column=j, value=s); c.font = Font(bold=True, color=NAVY); c.fill = SUBF; c.alignment = Alignment(horizontal='center', wrap_text=True); c.border = Border(bottom=med)
    ws.column_dimensions[CL(j)].width = 26 if j == 1 else 15 if j == 2 else 8 if s in ('# cust', '% vol', 'of which new', '% vol pts', 'Top cust %', '% of RY', '% of TKT') else 9
ws.row_dimensions[5].height = 30
def put(r, col, v, fmt=None, fill=None, bold=False, color=None):
    c = ws.cell(row=r, column=col, value=v)
    if fmt: c.number_format = fmt
    if fill: c.fill = PatternFill('solid', fgColor=fill)
    if bold or color: c.font = Font(bold=bold, color=color)
    return c
def tot_of(rx, p, kk): return sum(CELL[(rx, rid)][p][kk] for rid in ROWS[rx])
r = 6; summary = {}
for rx in RX:
    rows = ROWS[rx]; gp_ = GRIDTXT[rx]; t_ry, t_tk = APT.get((rx, 'RY')), APT.get((rx, 'TKT'))
    T25, T26 = tot_of(rx, '25', 't'), tot_of(rx, '26', 't'); TQ = {p: tot_of(rx, p, 't') for p in ['FY'] + QS}; TA = tot_of(rx, 'A', 't')
    RY = {p: tot_of(rx, p, 'ry_t') for p in ['FY'] + QS}; TK = {p: tot_of(rx, p, 'tk_t') for p in ['FY'] + QS}
    put(r, 1, rx).font = Font(bold=True, size=12, color=NAVY)
    put(r, 3, f"tier gap {gp_} · star = key account >= {KEY_SHARE*100:.0f}% of reaction · floor {FLOOR[rx]:g} · target band from {TARGET_LO[rx]:g} · AP27 plan product GP/kg: Rayong {t_ry:.2f}" + (f" · TKT {t_tk:.2f}" if t_tk else '') + (f" · measured cost gap RY–TKT {GAP[rx]:.2f}" if rx in GAP else '')).font = Font(italic=True, color='595959')
    for j in range(1, NC + 1): ws.cell(row=r, column=j).border = Border(top=med)
    r += 1; over = []; grouped = []; blk0 = r
    keys_by_tier = collections.defaultdict(list)
    for k in KEYS[rx]: keys_by_tier[C[(rx, k)]['tier']].append(k)
    def write_row(cell, label, zn, memo=False, tier_t=None):
        global r
        fillc = ZONEF[zn.split(' · ')[0]] if memo else ZONEF[zn]
        c0 = put(r, 1, label, fill=fillc, bold=memo); c0.alignment = Alignment(indent=2 if memo else 0)
        put(r, 2, zn, fill=fillc)
        x, y, zz, w = cell['25'], cell['26'], cell['FY'], cell['A']
        put(r, 3, x['n'] or None, NUM, PERF['25']); put(r, 4, round(x['t']) or None, NUM); put(r, 5, x['t'] / T25 if T25 and x['t'] else None, PCT); put(r, 6, x['gp'] / x['t'] if x['t'] else None, DEC); put(r, 7, x['gp'] / 1000 if x['t'] else None, MB)
        put(r, 8, y['n'] or None, NUM, PERF['26']); put(r, 9, round(y['t']) or None, NUM); put(r, 10, y['t'] / T26 if T26 and y['t'] else None, PCT); put(r, 11, y['gp'] / y['t'] if y['t'] else None, DEC); put(r, 12, y['gp'] / 1000 if y['t'] else None, MB)
        put(r, 13, zz['n'] or None, NUM, PERF['27']); put(r, 14, zz['new_n'] or None, NUM); put(r, 15, round(zz['t']) or None, NUM)
        sh = zz['t'] / TQ['FY'] if TQ['FY'] and zz['t'] else None; c_ = put(r, 16, sh, PCT)
        if sh and sh > 0.15 and not memo: c_.font = Font(bold=True, color='C62828'); over.append((label, sh))
        tp = (zz['t'] / tier_t if memo and tier_t else (zz['top'] / zz['t'] if zz['t'] else None)); c_ = put(r, 17, tp, PCT)
        if tp and tp > 0.5 and not memo: c_.font = Font(color='C62828')
        put(r, 18, zz['gp'] / zz['t'] if zz['t'] else None, DEC); put(r, 19, zz['gp'] / 1000 if zz['t'] else None, MB)
        put(r, 20, round(zz['ry_t']) or None, NUM); put(r, 21, zz['ry_t'] / RY['FY'] if RY['FY'] and zz['ry_t'] else None, PCT); put(r, 22, zz['ry_gp'] / zz['ry_t'] if zz['ry_t'] else None, DEC)
        put(r, 23, round(zz['tk_t']) or None, NUM); put(r, 24, zz['tk_t'] / TK['FY'] if TK['FY'] and zz['tk_t'] else None, PCT); put(r, 25, zz['tk_gp'] / zz['tk_t'] if zz['tk_t'] else None, DEC)
        d = (zz['t'] / TQ['FY'] if TQ['FY'] else 0) - (x['t'] / T25 if T25 else 0); put(r, 26, round(d * 100) if abs(d) >= 0.005 else None, '+0;-0;0')
        for qi, q in enumerate(QS):
            b = QB + QW * qi; u = cell[q]
            put(r, b, u['n'] or None, NUM, PERF['Q']); put(r, b + 1, round(u['t']) or None, NUM); put(r, b + 2, u['t'] / TQ[q] if TQ[q] and u['t'] else None, PCT); put(r, b + 3, u['gp'] / u['t'] if u['t'] else None, DEC)
            put(r, b + 4, round(u['ry_t']) or None, NUM); put(r, b + 5, u['ry_t'] / RY[q] if RY[q] and u['ry_t'] else None, PCT); put(r, b + 6, u['ry_gp'] / u['ry_t'] if u['ry_t'] else None, DEC)
            put(r, b + 7, round(u['tk_t']) or None, NUM); put(r, b + 8, u['tk_t'] / TK[q] if TK[q] and u['tk_t'] else None, PCT); put(r, b + 9, u['tk_gp'] / u['tk_t'] if u['tk_t'] else None, DEC)
        put(r, AB, w['n'] or None, NUM, PERF['A']); put(r, AB + 1, round(w['t']) or None, NUM); put(r, AB + 2, w['t'] / TA if TA and w['t'] else None, PCT)
        put(r, AB + 3, w['gp'] / w['t'] if w['t'] else None, DEC); put(r, AB + 4, w['gp'] / 1000 if w['t'] else None, MB); put(r, AB + 5, w['up'] / 1000 if w['up'] else None, MB)
        if memo:
            for j in range(2, NC + 1): ws.cell(row=r, column=j).font = Font(italic=True, color=BLUE)
            ws.cell(row=r, column=1).font = Font(bold=True, italic=True, color=BLUE)
        r += 1
    for rid in rows:
        cell = CELL[(rx, rid)]
        if all(cell[p]['t'] < 1.0 for p in ('25', '26', 'FY', 'A')): continue
        zn = zone(rx, rid[1]); start = r
        write_row(cell, tname(rx, rid[1]), zn)
        for k in keys_by_tier.get(rid[1], []):
            c = C[(rx, k)]; write_row(CELL[(rx, ('key', k))], '\u2605 ' + c['grp'][:34], zone_g(rx, c['g']) + ' \u00b7 ' + f"{c['g']:.2f}", memo=True, tier_t=cell['FY']['t'])
        if cell['FY']['t'] < 1.0: grouped.extend(range(start, r))
    for rr in grouped:
        ws.row_dimensions[rr].outline_level = 1; ws.row_dimensions[rr].hidden = True
    # ---- zone subtotal rows (formulas over the tier rows of this block; star memo rows are excluded because their zone text carries the GP/kg suffix) ----
    blk1 = r - 1; TR = r + 3
    SUMC = [3, 4, 7, 8, 9, 12, 13, 14, 15, 19, 20, 23] + [c for qi in range(4) for c in (QB + QW * qi, QB + QW * qi + 1, QB + QW * qi + 4, QB + QW * qi + 7)] + [AB, AB + 1, AB + 4, AB + 5]
    PCTC = {5: 4, 10: 9, 16: 15, 21: 20, 24: 23, AB + 2: AB + 1}
    for qi in range(4): b = QB + QW * qi; PCTC[b + 2] = b + 1; PCTC[b + 5] = b + 4; PCTC[b + 8] = b + 7
    RATIO = {6: (7, 4), 11: (12, 9), 18: (19, 15), AB + 3: (AB + 4, AB + 1)}          # GP THB M / tonnes * 1000
    WAVG = {22: 20, 25: 23}                                                            # SUMPRODUCT(tonnes x GP/kg) / tonnes
    for qi in range(4): b = QB + QW * qi; WAVG[b + 3] = b + 1; WAVG[b + 6] = b + 4; WAVG[b + 9] = b + 7
    def rng(col): return f"{CL(col)}${blk0}:{CL(col)}${blk1}"
    for zi, zname in enumerate(['Below floor', 'Floor to target', 'Target and above']):
        crit = f'$B${blk0}:$B${blk1},"{zname}"'
        put(r, 1, '\u03a3 ' + zname, fill=ZONEF[zname], bold=True); put(r, 2, zname, fill=ZONEF[zname], bold=True)
        for col in SUMC: put(r, col, f"=SUMIFS({rng(col)},{crit})", NUM if col not in (7, 12, 19, AB + 4, AB + 5) else MB, bold=True)
        for col, tcol in PCTC.items(): put(r, col, f"=IFERROR({CL(tcol)}{r}/{CL(tcol)}${TR},\"\")", PCT, bold=True)
        for col, (gcol, tcol) in RATIO.items(): put(r, col, f"=IFERROR({CL(gcol)}{r}/{CL(tcol)}{r}*1000,\"\")", DEC, bold=True)
        for col, tcol in WAVG.items(): put(r, col, f"=IFERROR(SUMPRODUCT(($B${blk0}:$B${blk1}=\"{zname}\")*{rng(tcol)}*{rng(col)})/SUMIFS({rng(tcol)},{crit}),\"\")", DEC, bold=True)
        put(r, 26, f"=IFERROR(({CL(16)}{r}-{CL(5)}{r})*100,\"\")", '+0;-0;0', bold=True)
        for j in range(1, NC + 1):
            c_ = ws.cell(row=r, column=j); c_.border = Border(top=thin if zi == 0 else None, left=c_.border.left, bottom=c_.border.bottom)
            if j > 2: c_.fill = PatternFill('solid', fgColor=ZONEF[zname])
        r += 1
    for j in range(1, NC + 1): ws.cell(row=r, column=j).fill = PatternFill('solid', fgColor=GREY); ws.cell(row=r, column=j).border = Border(top=thin)
    def tot(col, v, fmt): return put(r, col, v, fmt, GREY, True)
    def plant(col, gp, t, tgt):
        v = gp / t if t else None; c_ = tot(col, v, DEC)
        if v is not None and tgt: c_.font = Font(bold=True, color='2E7D32' if v >= tgt - 0.005 else 'C62828')
    tot(1, 'Total ' + rx, None)
    tot(3, tot_of(rx, '25', 'n'), NUM); tot(4, round(T25), NUM); tot(5, 1 if T25 else None, PCT); tot(6, tot_of(rx, '25', 'gp') / T25 if T25 else None, DEC); tot(7, tot_of(rx, '25', 'gp') / 1000, MB)
    tot(8, tot_of(rx, '26', 'n'), NUM); tot(9, round(T26), NUM); tot(10, 1 if T26 else None, PCT); tot(11, tot_of(rx, '26', 'gp') / T26 if T26 else None, DEC); tot(12, tot_of(rx, '26', 'gp') / 1000, MB)
    tot(13, tot_of(rx, 'FY', 'n'), NUM); tot(14, tot_of(rx, 'FY', 'new_n'), NUM); tot(15, round(TQ['FY']), NUM); tot(16, 1, PCT); tot(18, tot_of(rx, 'FY', 'gp') / TQ['FY'], DEC); tot(19, tot_of(rx, 'FY', 'gp') / 1000, MB)
    tot(20, round(RY['FY']), NUM); tot(21, 1 if RY['FY'] else None, PCT); plant(22, tot_of(rx, 'FY', 'ry_gp'), RY['FY'], t_ry); tot(23, round(TK['FY']), NUM); tot(24, 1 if TK['FY'] else None, PCT); plant(25, tot_of(rx, 'FY', 'tk_gp'), TK['FY'], t_tk)
    for qi, q in enumerate(QS):
        b = QB + QW * qi
        tot(b, tot_of(rx, q, 'n'), NUM); tot(b + 1, round(TQ[q]), NUM); tot(b + 2, 1 if TQ[q] else None, PCT); tot(b + 3, tot_of(rx, q, 'gp') / TQ[q] if TQ[q] else None, DEC)
        tot(b + 4, round(RY[q]), NUM); tot(b + 5, 1 if RY[q] else None, PCT); plant(b + 6, tot_of(rx, q, 'ry_gp'), RY[q], t_ry); tot(b + 7, round(TK[q]), NUM); tot(b + 8, 1 if TK[q] else None, PCT); plant(b + 9, tot_of(rx, q, 'tk_gp'), TK[q], t_tk)
    tot(AB, tot_of(rx, 'A', 'n'), NUM); tot(AB + 1, round(TA), NUM); tot(AB + 2, 1, PCT); tot(AB + 3, tot_of(rx, 'A', 'gp') / TA, DEC); tot(AB + 4, tot_of(rx, 'A', 'gp') / 1000, MB); tot(AB + 5, tot_of(rx, 'A', 'up') / 1000, MB)
    summary[rx] = {'gap': gp_, 'keys': [(C[(rx, k)]['grp'], C[(rx, k)]['t'] / TQ['FY'], C[(rx, k)]['g']) for k in KEYS[rx]], 'over': over, 'tail_max': max([CELL[(rx, ('tier', i))]['FY']['t'] / TQ['FY'] for i in range(ntier(rx))] or [0]), 'grouped': len(grouped)}
    r += 2
period_starts = [3, 8, 13, 26, QB, QB + QW, QB + 2 * QW, QB + 3 * QW, AB]
plant_splits = [20, 23] + [QB + QW * i + 4 for i in range(4)] + [QB + QW * i + 7 for i in range(4)]
for j in period_starts + plant_splits:
    for rr in range(4, r):
        c = ws.cell(row=rr, column=j); colr = 'FFFFFF' if rr == 4 else NAVY; style = 'medium' if (rr == 4 and j in period_starts) else 'thin'
        c.border = Border(left=Side(style=style, color=colr), top=c.border.top, bottom=c.border.bottom)
for j in range(1, NC + 1):
    c = ws.cell(row=4, column=j); c.border = Border(left=c.border.left, top=Side(style='thin', color='FFFFFF'), bottom=Side(style='thin', color='FFFFFF'))
notes = ['Reading the sheet',
         '- Blue italic star rows are memo lines (key accounts): they are already inside the tier above them and are NOT added again. The three \u03a3 rows per reaction sum the tier rows by zone (formulas); the Total row is the reaction total.',
         '- Tier rows include all customers. Star rows are memo lines for key accounts (>= 10% of the reaction 2027 plan), shown under the tier they sit in for 2027; "Top cust %" on a star row = that account share of the tier. Their 2025 / 2026 actuals are on the same row, so the step from history to plan is visible per account.',
         '- % vol in red = a tier above 15% of the reaction; Top cust % in red on a tier row = one customer is more than half of that tier. Rows with history but no 2027 volume are grouped and collapsed (outline + at the left).',
         '• % of RY / % of TKT = the tier\'s share of that plant\'s volume in the period. Rayong / TKT GP/kg = plant GP/kg as in the AP plan; on total rows green = at or above the AP27 plan GP/kg for that plant.',
         '• Price-action case: key accounts and tail lines below floor go to the floor (or exit); floor-to-target lines close half the gap; target+ hold. Uplift = extra product GP vs the plan at the same tonnes.',
         '• Sources: TDC Profitability_Act 2024-2026_Jul2026_AddPPA (data_Actual, incl. zero-tonne adjustment rows); Top Line HVA Thailand_Oct1 Revised ASP_Final.xlsx sheet "data" (AP + headroom). Rebuilt 20 Oct 2026 (v7).']
for i, n in enumerate(notes):
    c = ws.cell(row=r + i, column=1, value=n)
    if i == 0: c.font = Font(bold=True, color=NAVY)
USER_NOTES = {'PO-XL': '0.5-1.0', 'XL': '0.25-0.50'}
for rx, note in USER_NOTES.items():
    for rw in range(6, r):
        if ws.cell(row=rw, column=1).value == rx:
            c = ws.cell(row=rw, column=2, value=note); c.fill = PatternFill('solid', fgColor='FFFF00'); c.font = Font(bold=True, color='7F6000'); ws.cell(row=rw, column=1).fill = PatternFill('solid', fgColor='FFFF00')
ws.sheet_properties.outlinePr.summaryBelow = False
ws.freeze_panes = 'C6'; ws.sheet_properties.pageSetUpPr = openpyxl.worksheet.properties.PageSetupProperties(fitToPage=True); ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0


# ===================== 2027 plug-and-play =====================
ws = fresh('2027 plug-and-play', 2); ws.sheet_view.showGridLines = False
ws['A1'] = '2027 plug-and-play: change the % of volume per tier and plant, keep each plant volume and GP/kg target fixed'; ws['A1'].font = Font(bold=True, size=13, color=NAVY)
ws['A2'] = ('Yellow cells are inputs: % of Rayong volume and % of TKT volume per tier (each column must add to 100%), and the plant GP/kg per tier (defaults = AP plan; for tiers with no plan volume the default is the tier mid-point, plus the RY-TKT cost gap for TKT). '
            'Everything else is a formula. The LOCKED row holds the AP27 plant tonnes and plant GP/kg (and their combination for the two plants); the CHECK row shows the gap of your mix to those locks - aim for zero. '
            '2025 / 2026 columns are actuals for reference. Note: here the 2-plant GP/kg is on plant basis (tonne-weighted Rayong + TKT), unlike the commercial (Rayong-cost) basis on the Tier mapping sheet.')
ws['A2'].alignment = Alignment(wrap_text=True, vertical='top'); ws.merge_cells('A2:W2'); ws.row_dimensions[2].height = 66
pcols = [('', 'Tier (THB/kg)'), ('', 'Zone')]
for lab in ('2025 actual (FY)', '2026 YTD (Jan-Sep)'): pcols += [(lab, s_) for s_ in ('# cust', 'Tonnes', '% vol', 'GP/kg', 'GP THB M')]
pcols += [('2027 Rayong (plug)', s_) for s_ in ('% of RY  [input]', 'Tonnes', 'GP/kg  [input]')] + [('2027 TKT (plug)', s_) for s_ in ('% of TKT  [input]', 'Tonnes', 'GP/kg  [input]')]
pcols += [('2027 two plants (result)', s_) for s_ in ('Tonnes', '% vol', 'GP/kg', 'GP THB M', '# cust (plan)')]
PNC = len(pcols); c0 = 1
while c0 <= PNC:
    g = pcols[c0 - 1][0]; c1 = c0
    while c1 + 1 <= PNC and pcols[c1][0] == g: c1 += 1
    if g:
        ws.cell(row=4, column=c0, value=g)
        if c1 > c0: ws.merge_cells(start_row=4, start_column=c0, end_row=4, end_column=c1)
        cell = ws.cell(row=4, column=c0); cell.font = HFNT; cell.fill = HF; cell.alignment = Alignment(horizontal='center')
    c0 = c1 + 1
for j, (_, s_) in enumerate(pcols, 1):
    c = ws.cell(row=5, column=j, value=s_); c.font = Font(bold=True, color=NAVY); c.fill = SUBF; c.alignment = Alignment(horizontal='center', wrap_text=True); c.border = Border(bottom=med)
    ws.column_dimensions[CL(j)].width = 26 if j == 1 else 16 if j == 2 else 10
ws.row_dimensions[5].height = 32
INP = 'FFF2CC'
def pput(r, col, v, fmt=None, fill=None, bold=False, color=None, italic=False):
    c = ws.cell(row=r, column=col, value=v)
    if fmt: c.number_format = fmt
    if fill: c.fill = PatternFill('solid', fgColor=fill)
    if bold or color or italic: c.font = Font(bold=bold, color=color, italic=italic)
    return c
r = 6
for rx in RX:
    rows = ROWS[rx]; t_ry, t_tk = APT.get((rx, 'RY')), APT.get((rx, 'TKT'))
    T25, T26 = tot_of(rx, '25', 't'), tot_of(rx, '26', 't'); RYT, TKT_, TOT = tot_of(rx, 'FY', 'ry_t'), tot_of(rx, 'FY', 'tk_t'), tot_of(rx, 'FY', 't')
    RYG, TKG = tot_of(rx, 'FY', 'ry_gp'), tot_of(rx, 'FY', 'tk_gp')
    pput(r, 1, rx).font = Font(bold=True, size=12, color=NAVY)
    pput(r, 3, f"tier gap {GRIDTXT[rx]} · locked: Rayong {RYT:,.0f} t @ {t_ry or 0:.2f}" + (f" · TKT {TKT_:,.0f} t @ {t_tk:.2f}" if TKT_ else '') + f" · two plants {TOT:,.0f} t @ {(RYG + TKG) / TOT:.2f} (plant basis)").font = Font(italic=True, color='595959')
    for j in range(1, PNC + 1): ws.cell(row=r, column=j).border = Border(top=med)
    r += 1; blk0 = r
    keys_by_tier = collections.defaultdict(list)
    for k in KEYS[rx]: keys_by_tier[C[(rx, k)]['tier']].append(k)
    cuts_ = cuts(rx)
    for rid in rows:
        cell = CELL[(rx, rid)]; i = rid[1]
        if all(cell[p]['t'] < 1.0 for p in ('25', '26', 'FY')) and not (0 < i < len(cuts_)): continue   # keep every in-grid tier (plug targets), drop empty open-ended ends
        zn = zone(rx, i); x, y, zz = cell['25'], cell['26'], cell['FY']
        mid = (cuts_[i - 1] + cuts_[i]) / 2 if 0 < i < len(cuts_) else (cuts_[0] - 0.25 if i == 0 else cuts_[-1] + 0.25)
        pput(r, 1, tname(rx, i), fill=ZONEF[zn]); pput(r, 2, zn, fill=ZONEF[zn])
        pput(r, 3, x['n'] or None, NUM); pput(r, 4, round(x['t']) or None, NUM); pput(r, 5, x['t'] / T25 if T25 and x['t'] else None, PCT); pput(r, 6, x['gp'] / x['t'] if x['t'] else None, DEC); pput(r, 7, x['gp'] / 1000 if x['t'] else None, MB)
        pput(r, 8, y['n'] or None, NUM); pput(r, 9, round(y['t']) or None, NUM); pput(r, 10, y['t'] / T26 if T26 and y['t'] else None, PCT); pput(r, 11, y['gp'] / y['t'] if y['t'] else None, DEC); pput(r, 12, y['gp'] / 1000 if y['t'] else None, MB)
        pput(r, 13, zz['ry_t'] / RYT if RYT else 0, PCT, INP); pput(r, 14, f"=M{r}*$N${{TR}}", NUM); pput(r, 15, (zz['ry_gp'] / zz['ry_t']) if zz['ry_t'] else round(mid, 2), DEC, INP)
        pput(r, 16, zz['tk_t'] / TKT_ if TKT_ else 0, PCT, INP); pput(r, 17, f"=P{r}*$Q${{TR}}", NUM); pput(r, 18, (zz['tk_gp'] / zz['tk_t']) if zz['tk_t'] else round(mid + GAP.get(rx, 0.0), 2), DEC, INP)
        pput(r, 19, f"=N{r}+Q{r}", NUM); pput(r, 20, f"=IFERROR(S{r}/$S${{TR}},\"\")", PCT); pput(r, 21, f"=IFERROR((N{r}*O{r}+Q{r}*R{r})/S{r},\"\")", DEC); pput(r, 22, f"=(N{r}*O{r}+Q{r}*R{r})/1000", MB); pput(r, 23, zz['n'] or None, NUM)
        r += 1
        for k in keys_by_tier.get(i, []):
            c = C[(rx, k)]; kc = CELL[(rx, ('key', k))]; kz = kc['FY']; k25 = kc['25']; k26 = kc['26']
            pput(r, 1, '★ ' + c['grp'][:34], fill=ZONEF[zn], bold=True, italic=True, color=BLUE).alignment = Alignment(indent=2)
            pput(r, 2, f"{zone_g(rx, c['g'])} · {c['g']:.2f}", fill=ZONEF[zn], italic=True, color=BLUE)
            vals = {3: k25['n'] or None, 4: round(k25['t']) or None, 5: k25['t'] / T25 if T25 and k25['t'] else None, 6: k25['gp'] / k25['t'] if k25['t'] else None, 7: k25['gp'] / 1000 if k25['t'] else None,
                    8: k26['n'] or None, 9: round(k26['t']) or None, 10: k26['t'] / T26 if T26 and k26['t'] else None, 11: k26['gp'] / k26['t'] if k26['t'] else None, 12: k26['gp'] / 1000 if k26['t'] else None,
                    13: kz['ry_t'] / RYT if RYT else None, 14: round(kz['ry_t']) or None, 15: kz['ry_gp'] / kz['ry_t'] if kz['ry_t'] else None, 16: kz['tk_t'] / TKT_ if TKT_ else None, 17: round(kz['tk_t']) or None, 18: kz['tk_gp'] / kz['tk_t'] if kz['tk_t'] else None,
                    19: round(kz['t']) or None, 20: kz['t'] / TOT if TOT else None, 21: (kz['ry_gp'] + kz['tk_gp']) / kz['t'] if kz['t'] else None, 22: (kz['ry_gp'] + kz['tk_gp']) / 1000 if kz['t'] else None, 23: 1}
            fm_ = {3: NUM, 4: NUM, 5: PCT, 6: DEC, 7: MB, 8: NUM, 9: NUM, 10: PCT, 11: DEC, 12: MB, 13: PCT, 14: NUM, 15: DEC, 16: PCT, 17: NUM, 18: DEC, 19: NUM, 20: PCT, 21: DEC, 22: MB, 23: NUM}
            for col, v in vals.items(): pput(r, col, v, fm_[col], italic=True, color=BLUE)
            r += 1
    blk1 = r - 1; TR = r + 3
    # replace the {TR} placeholders in this block's formulas now that TR is known
    for rr in range(blk0, blk1 + 1):
        for col in (14, 17, 20):
            v = ws.cell(row=rr, column=col).value
            if isinstance(v, str) and '{TR}' in v: ws.cell(row=rr, column=col).value = v.replace('{TR}', str(TR + 1 if col in (14, 17) else TR))   # tonnes use the LOCKED plant totals (row TR+1); % vol uses the mix total (row TR)
    def prng(col): return f"{CL(col)}${blk0}:{CL(col)}${blk1}"
    for zi, zname in enumerate(['Below floor', 'Floor to target', 'Target and above']):
        crit = f'$B${blk0}:$B${blk1},"{zname}"'
        pput(r, 1, 'Σ ' + zname, fill=ZONEF[zname], bold=True); pput(r, 2, zname, fill=ZONEF[zname], bold=True)
        for col in (3, 4, 7, 8, 9, 12, 13, 14, 16, 17, 19, 22, 23): pput(r, col, f"=SUMIFS({prng(col)},{crit})", PCT if col in (13, 16) else (MB if col in (7, 12, 22) else NUM), bold=True)
        pput(r, 5, f"=IFERROR(D{r}/D${TR},\"\")", PCT, bold=True); pput(r, 10, f"=IFERROR(I{r}/I${TR},\"\")", PCT, bold=True); pput(r, 20, f"=IFERROR(S{r}/S${TR},\"\")", PCT, bold=True)
        pput(r, 6, f"=IFERROR(G{r}/D{r}*1000,\"\")", DEC, bold=True); pput(r, 11, f"=IFERROR(L{r}/I{r}*1000,\"\")", DEC, bold=True); pput(r, 21, f"=IFERROR(V{r}/S{r}*1000,\"\")", DEC, bold=True)
        pput(r, 15, f"=IFERROR(SUMPRODUCT(($B${blk0}:$B${blk1}=\"{zname}\")*{prng(14)}*{prng(15)})/SUMIFS({prng(14)},{crit}),\"\")", DEC, bold=True)
        pput(r, 18, f"=IFERROR(SUMPRODUCT(($B${blk0}:$B${blk1}=\"{zname}\")*{prng(17)}*{prng(18)})/SUMIFS({prng(17)},{crit}),\"\")", DEC, bold=True)
        for j in range(3, PNC + 1): ws.cell(row=r, column=j).fill = PatternFill('solid', fgColor=ZONEF[zname])
        for j in range(1, PNC + 1): ws.cell(row=r, column=j).border = Border(top=thin if zi == 0 else None)
        r += 1
    # Total row (formulas = sum of the three zone rows)
    z1, z3 = TR - 3, TR - 1
    pput(r, 1, 'Total ' + rx + ' (your mix)', fill=GREY, bold=True)
    for col in (3, 4, 7, 8, 9, 12, 13, 14, 16, 17, 19, 22, 23): pput(r, col, f"=SUM({CL(col)}{z1}:{CL(col)}{z3})", PCT if col in (13, 16) else (MB if col in (7, 12, 22) else NUM), GREY, True)
    pput(r, 5, 1 if T25 else None, PCT, GREY, True); pput(r, 10, 1 if T26 else None, PCT, GREY, True); pput(r, 20, f"=IFERROR(S{r}/S{r},\"\")", PCT, GREY, True)
    pput(r, 6, f"=IFERROR(G{r}/D{r}*1000,\"\")", DEC, GREY, True); pput(r, 11, f"=IFERROR(L{r}/I{r}*1000,\"\")", DEC, GREY, True)
    pput(r, 15, f"=IFERROR(SUMPRODUCT({prng(14)},{prng(15)})/N{r},\"\")", DEC, GREY, True); pput(r, 18, f"=IFERROR(SUMPRODUCT({prng(17)},{prng(18)})/Q{r},\"\")", DEC, GREY, True)
    pput(r, 21, f"=IFERROR(V{r}/S{r}*1000,\"\")", DEC, GREY, True)
    for j in range(1, PNC + 1): ws.cell(row=r, column=j).border = Border(top=thin)
    r += 1
    # LOCKED row (AP27 plan)
    pput(r, 1, 'LOCKED: AP27 plant tonnes and GP/kg', fill='D9D9D9', bold=True)
    pput(r, 13, 1, PCT, 'D9D9D9', True); pput(r, 14, round(RYT), NUM, 'D9D9D9', True); pput(r, 15, t_ry, DEC, 'D9D9D9', True)
    pput(r, 16, 1 if TKT_ else None, PCT, 'D9D9D9', True); pput(r, 17, round(TKT_), NUM, 'D9D9D9', True); pput(r, 18, t_tk, DEC, 'D9D9D9', True)
    pput(r, 19, round(TOT), NUM, 'D9D9D9', True); pput(r, 20, 1, PCT, 'D9D9D9', True); pput(r, 21, (RYG + TKG) / TOT if TOT else None, DEC, 'D9D9D9', True); pput(r, 22, (RYG + TKG) / 1000, MB, 'D9D9D9', True)
    LR = r; r += 1
    # CHECK row
    pput(r, 1, 'CHECK (should be 0): your mix minus locked', bold=True, color='C62828')
    for col, fmt in ((13, '+0.0%;-0.0%;0.0%'), (14, '+#,##0;-#,##0;0'), (15, '+0.00;-0.00;0.00'), (16, '+0.0%;-0.0%;0.0%'), (17, '+#,##0;-#,##0;0'), (18, '+0.00;-0.00;0.00'), (19, '+#,##0;-#,##0;0'), (21, '+0.00;-0.00;0.00'), (22, '+#,##0.0;-#,##0.0;0.0')):
        pput(r, col, f"=IFERROR({CL(col)}{TR}-{CL(col)}{LR},\"\")", fmt, bold=True, color='C62828')
    r += 2
for j in (3, 8, 13, 16, 19):
    for rr in range(4, r):
        c = ws.cell(row=rr, column=j); c.border = Border(left=Side(style='thin', color='FFFFFF' if rr == 4 else NAVY), top=c.border.top, bottom=c.border.bottom)
for j in range(1, PNC + 1):
    c = ws.cell(row=4, column=j); c.border = Border(left=c.border.left, top=Side(style='thin', color='FFFFFF'), bottom=Side(style='thin', color='FFFFFF'))
pnotes = ['How to use',
          '1. Start from the AP mix (defaults). Change the yellow % of RY / % of TKT cells to move volume between tiers; keep each plant column summing to 100% (CHECK row = 0).',
          '2. The plant GP/kg per tier (yellow) is the price position of that tier; adjust it only if you expect the tier itself to be priced differently.',
          '3. Read the result: Total GP/kg per plant and for the two plants vs the LOCKED AP27 values; the CHECK row shows the gap. A mix that moves tonnes down a tier must be offset by tonnes up a tier to hold the lock.',
          '4. Star rows (blue italic) are memo lines for key accounts inside the tier above; they are not summed. The three Σ rows sum the tiers by zone.',
          '5. Quarterly phasing and the price-action case are on the Tier mapping sheet; this sheet works on full-year 2027 only.']
for i, n in enumerate(pnotes):
    c = ws.cell(row=r + i, column=1, value=n)
    if i == 0: c.font = Font(bold=True, color=NAVY)
ws.freeze_panes = 'C6'; ws.sheet_properties.pageSetUpPr = openpyxl.worksheet.properties.PageSetupProperties(fitToPage=True); ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0

# ---- Tier definition ----
ws4 = fresh('Tier definition', 2)
hd = ['Reaction', 'Key accounts (>= 10% of 2027 plan, memo rows)', 'Tier gap (THB/kg)', 'Grid from', 'Grid to', 'Price floor', 'Target band from', 'AP27 plan GP/kg Rayong', 'AP27 plan GP/kg TKT', 'Measured cost gap RY-TKT', 'Largest tier 2027 (% of reaction)', 'Tiers above 15%']
for j, h in enumerate(hd, 1):
    c = ws4.cell(row=1, column=j, value=h); c.font = HFNT; c.fill = HF; c.alignment = Alignment(wrap_text=True, vertical='center'); ws4.column_dimensions[CL(j)].width = [10, 70, 36, 8, 8, 9, 10, 11, 11, 12, 14, 40][j - 1]
ws4.row_dimensions[1].height = 45
for i, rx in enumerate(RX, 2):
    s = summary[rx]; cc_ = cuts(rx)
    ws4.append([rx, '; '.join(f"{n[:30]} {sh*100:.0f}% @ {g:.2f}" for n, sh, g in s['keys']) or 'none', GRIDTXT[rx], cc_[0], cc_[-1], FLOOR[rx], TARGET_LO[rx], round(APT.get((rx, 'RY'), 0), 2) or None, round(APT[(rx, 'TKT')], 2) if (rx, 'TKT') in APT else None,
                round(GAP[rx], 2) if rx in GAP else None, s['tail_max'], '; '.join(f"{t} {sh*100:.0f}%" for t, sh in s['over']) or 'none'])
    ws4.cell(row=i, column=11).number_format = PCT
    for j in (2, 12): ws4.cell(row=i, column=j).alignment = Alignment(wrap_text=True, vertical='top')
ws4.append([]); ws4.append(['Grids, floors and the key-account threshold are parameters of the build script (GRID / FLOOR / TARGET_LO / KEY_SHARE); the sheet is generated, not formula-driven.'])

# ---- 2025 / 2026 sheets ----
for sheet, y, pos in (('2025 actual', '25', 3), ('2026 YTD', '26', 4)):
    s_ = fresh(sheet, pos)
    hd = ['Reaction', 'Row', 'Zone', '# customers', 'Tonnes', '% of reaction', 'Product GP (THB M)', 'Product GP/kg', 'Reaction total t', 'Reaction GP/kg']
    for j, h in enumerate(hd, 1):
        c = s_.cell(row=1, column=j, value=h); c.font = HFNT; c.fill = HF; c.alignment = Alignment(wrap_text=True)
    for j, w in enumerate([10, 34, 18, 11, 10, 11, 14, 12, 13, 12], 1): s_.column_dimensions[CL(j)].width = w
    rr = 2
    for rx in RX:
        tt = tot_of(rx, y, 't'); gg = tot_of(rx, y, 'gp')
        for rid in ROWS[rx]:
            a = CELL[(rx, rid)][y]
            if a['t'] <= 0: continue
            lab = tname(rx, rid[1]); zn = zone(rx, rid[1])
            s_.append([rx, lab, zn, a['n'], round(a['t']), a['t'] / tt if tt else 0, round(a['gp'] / 1000, 2), round(a['gp'] / a['t'], 2), round(tt), round(gg / tt, 2) if tt else None])
            s_.cell(row=rr, column=2).fill = PatternFill('solid', fgColor=ZONEF[zn]); s_.cell(row=rr, column=6).number_format = PCT; rr += 1
            for k in KEYS[rx]:
                h = H.get((k, rx))
                if not h or not h['t' + y] or h['gp' + y] is None or tier_of(rx, h['gp' + y] / 1000) != rid[1]: continue
                s_.append([rx, '   \u2605 ' + C[(rx, k)]['grp'][:34], zone_g(rx, h['gp' + y] / 1000), 1, round(h['t' + y]), h['t' + y] / tt if tt else 0, round(h['gp' + y] * h['t' + y] / 1e6, 2), round(h['gp' + y] / 1000, 2), None, None])
                s_.cell(row=rr, column=2).fill = PatternFill('solid', fgColor=ZONEF[zn]); s_.cell(row=rr, column=6).number_format = PCT; rr += 1
    s_.freeze_panes = 'A2'

# ---- Line list: add key-account flag and tier on the new grid ----
ws3 = fresh('Line list', 6)
hd = ['Reaction', 'Reactor', 'Plant', 'Customer group', 'Key account?', 'Customer name (AP)', 'Code', 'AP customer type', 'Country', 'SN', 'Trade name', '2025 t (cust×reaction)', '2025 GP/kg', '2026 YTD t', '2026 GP/kg', 'New account?', '2027 plan t', 'Q1 t', 'Q2 t', 'Q3 t', 'Q4 t',
      'Plan plant GP/kg', 'Cost gap to RY', 'Commercial GP/kg (line)', 'Customer commercial GP/kg (FY)', 'Tier (customer)', 'Zone', 'Action', 'Commercial GP/kg after action', 'Plant GP/kg after action', 'Plan GP THB M', 'GP THB M after action', 'Owner', 'Price agreed (date)', 'Status']
wid = [8, 7, 6, 30, 8, 30, 9, 10, 11, 8, 14, 9, 8, 9, 8, 8, 9, 7, 7, 7, 7, 9, 8, 10, 11, 12, 16, 30, 10, 10, 9, 9, 10, 12, 10]
for j, h in enumerate(hd, 1):
    c = ws3.cell(row=1, column=j, value=h); c.font = HFNT; c.fill = HF; c.alignment = Alignment(wrap_text=True, vertical='center'); ws3.column_dimensions[CL(j)].width = wid[j - 1]
ws3.row_dimensions[1].height = 45
ls = sorted(lines, key=lambda l: (RX.index(l['rx']), l['plant'], -sum(l['vol'])))
for i, l in enumerate(ls, 2):
    c = C[(l['rx'], l['key'])]; h = c['h'] or {}; v = sum(l['vol']); gpl = sum(l['gp']) / v / 1000; gcl = gpl - l['gap']; up = c['g_act'] - c['g']; zn = zone_g(l['rx'], c['g'])
    ws3.append([l['rx'], l['reactor'], l['plant'], c['grp'], '\u2605 key' if c['keyacc'] else '', l['name'], l['code'], l['apseg'], l['country'], l['sn'], l['trade'],
                h.get('t25') or None, round(h['gp25'] / 1000, 2) if h.get('gp25') is not None else None, h.get('t26') or None, round(h['gp26'] / 1000, 2) if h.get('gp26') is not None else None,
                'new' if c['new'] else '', round(v), round(sum(l['vol'][0:3])), round(sum(l['vol'][3:6])), round(sum(l['vol'][6:9])), round(sum(l['vol'][9:12])),
                round(gpl, 2), round(l['gap'], 2) if l['gap'] else None, round(gcl, 2), round(c['g'], 2), tname(l['rx'], c['tier']), zn, c['act'], round(gcl + up, 2), round(gpl + up, 2),
                round(sum(l['gp']) / 1e6, 2), round((sum(l['gp']) + up * v * 1000) / 1e6, 2), '', '', ''])
    ws3.cell(row=i, column=26).fill = PatternFill('solid', fgColor=ZONEF[zn]); ws3.cell(row=i, column=27).fill = PatternFill('solid', fgColor=ZONEF[zn])
    if c['keyacc']: ws3.cell(row=i, column=5).fill = PatternFill('solid', fgColor=KEYF)
ws3.freeze_panes = 'F2'; ws3.auto_filter.ref = f"A1:{CL(len(hd))}{len(ls) + 1}"
if 'README' in wb.sheetnames:
    wr = wb['README']
    wr['A11'] = ('v11 (20 Oct 2026): new sheet "2027 plug-and-play" (inputs = % of Rayong / % of TKT volume per tier and plant GP/kg per tier; plant tonnes and GP/kg locked to AP27; CHECK row). Three zone subtotal rows per reaction on both sheets (formulas). Key-account memo rows in blue italic: inside their tier, not summed again.')
    wr['A11'].alignment = Alignment(wrap_text=True, vertical='top')
    wr['A10'] = ('v9 (20 Oct 2026): key-account memo rows now carry the same colour as their tier. v8: tiers at 0.5 THB/kg for every reaction, with 0.25 splits where volume clusters (PO-XL 5.0-5.5 and 7.0-7.5, PO 5.0-5.5, AC 11.0-11.5). Tier rows include all customers; key accounts (>= 10% of a reaction) are shown as star memo rows under their tier, not separated out. '
                'Tiers with history but no 2027 volume are grouped and collapsed. Plant volume shares (% of Rayong, % of TKT) in the FY and quarterly blocks.')
    wr['A10'].alignment = Alignment(wrap_text=True, vertical='top')
wb.move_sheet('2027 plug-and-play', offset=wb.sheetnames.index('Tier mapping 25-26-27') + 1 - wb.sheetnames.index('2027 plug-and-play'))
hva_format.apply(wb, 'tracker')
wb.save(OUT); print('saved', wb.sheetnames)
for rx, s in summary.items():
    print(f"{rx:7s} gap {s['gap']} | key: " + ('; '.join(f"{n[:20]} {sh*100:.0f}% @{g:.2f}" for n, sh, g in s['keys']) or 'none') + f" | largest tier {s['tail_max']*100:.0f}% | >15%: " + ('; '.join(f'{t} {sh*100:.0f}%' for t, sh in s['over']) or 'none') + f" | grouped rows {s['grouped']}")
