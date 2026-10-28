"""HVA 2027 volume delivery risk by quarter (Q1-Q4 2027) — v9.
Summary / By customer (tonnes) and Summary GP-kg / By customer GP-kg (same layout plus product GP/kg columns); Pivot-ready with GP and GP/kg."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import hva_format
import csv, re, collections, json, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL

OUT = r"C:/Users/NitchaSuwongtham/OneDrive - THAIWAH/Desktop/lovely/HVA 2027 Q1-Q4 volume delivery risk v9.xlsx"
SRC = 'topline_final_copy.xlsx'
RX = ['PO-XL', 'XL', 'PO', 'AC', 'MX', 'Others']
RXMAP = {'PX': 'PO-XL', 'XL': 'XL', 'PR': 'PO', 'PO': 'PO', 'AC': 'AC', 'MX': 'MX'}
PLANT = {'TDC': 'Rayong', 'TKT': 'TKT'}
THRESH = 1.30
QI = {'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 1, 'May': 1, 'Jun': 1, 'Jul': 2, 'Aug': 2, 'Sep': 2, 'Oct': 3, 'Nov': 3, 'Dec': 3}
QN = ["Q1'27", "Q2'27", "Q3'27", "Q4'27"]
TYPES = {'1': '1 New customer', '2': '2 Existing cust, new SKU', '3': '3 +30% vol of 2026 max qtr', '0': '0 Running base (w/i 30%)', 'x': 'x Sold in 25 and 26, not in 2027 plan'}
TYPEF = {'1': 'F1C7C7', '2': 'F8DCC6', '3': 'FBF0C6', '0': 'E2EFDA', 'x': 'ECECEC'}   # muted traffic light
ORDER = ['1', '2', '3', '0']
KEEP = json.load(open(r'C:/Users/NitchaSuwongtham/OneDrive - THAIWAH/Desktop/lovely/memory/hva-coloured-customers.json', encoding='utf-8'))['customer_groups']

def norm(n):
    n = str(n).upper().replace('BJ.', '').replace('ฟู๊ด', 'ฟู้ด'); n = re.sub(r'[^A-Z0-9ก-๙]+', '', n); return n[:16]
ALIAS = {'HUIFALINXIAFOODS': 'HUIFA', 'QINGDAOMIRACLESU': 'HUIFA', 'QINGDAOMIRACLE': 'HUIFA', 'MORIIFOODSINC': 'MORIIFOODS', 'FOODTRENDANDSUPE': 'FOODTREND'}
key = lambda n: ALIAS.get(norm(n), norm(n))
KEEP_N = set(norm(n) for n in KEEP) | set(n.strip() for n in KEEP)
num = lambda v: v if isinstance(v, (int, float)) else 0.0
def f(x):
    try: return float(x)
    except: return 0.0
def kg(g, v): return g / v / 1000 if v else None

# ---------- actuals ----------
rows = list(csv.DictReader(open('data_actual.csv', encoding='utf-8')))
code2grp = {}; grp_name = {}; act_rx = {}; sn_name = {}
a26q = collections.defaultdict(lambda: [0.0] * 4); a25 = collections.defaultdict(float); g26q = collections.defaultdict(lambda: [0.0] * 4); g25 = collections.defaultdict(float)
cust26 = collections.defaultdict(float); cust25 = collections.defaultdict(float)
for r in rows:
    if r['Customer Code']: code2grp[str(r['Customer Code']).strip()] = r['Customer name (Group)']
    k = key(r['Customer name (Group)']); grp_name.setdefault(k, r['Customer name (Group)'])
    if r['Reaction group'] in ('', 'None', '#N/A'): continue
    t = f(r['Sales Quantity (Tons)']); sn = r['SN']; sn_name.setdefault(sn, r['Trade Name'])
    act_rx[(k, sn)] = r['Reaction group'] if r['Reaction group'] in RX else 'Others'
    gp = f(r['Net Sales Revenue (THB)']) - f(r['Actual Cost(THB)']) - f(r['Cost from Freight(THB)']) - f(r['Cost from Insurance(THB)'])
    if r['Year'] == 'Year 2026': a26q[(k, sn)][QI[r['Period']]] += t; g26q[(k, sn)][QI[r['Period']]] += gp; cust26[k] += t
    elif r['Year'] == 'Year 2025': a25[(k, sn)] += t; g25[(k, sn)] += gp; cust25[k] += t

# ---------- 2027 plan ----------
wb_src = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
raw = [r for r in wb_src['data'].iter_rows(min_row=8, values_only=True) if r[6] not in (None, '')]
VOL = list(range(78, 90)); GPc = list(range(222, 234))
L = collections.defaultdict(lambda: {'meta': None, 'm': {'Rayong': [0.0] * 12, 'TKT': [0.0] * 12}, 'g': {'Rayong': [0.0] * 12, 'TKT': [0.0] * 12}})
for r in raw:
    vols = [num(r[j]) for j in VOL]
    if sum(vols) <= 0: continue
    code = str(r[5]).strip() if r[5] not in (None, '-', '') else ''
    grp = code2grp.get(code) or r[6]; k = key(grp); rx = RXMAP.get(r[0], 'Others'); pl = PLANT.get(r[3], r[3])
    c = L[(rx, k, r[11])]
    c['meta'] = c['meta'] or {'rx': rx, 'reactor': r[0], 'grp': grp_name.get(k, grp), 'name': r[6], 'code': code, 'apseg': r[1], 'src': r[4], 'channel': r[7], 'pic': r[8], 'country': r[9], 'sn': r[11], 'trade': r[12] or sn_name.get(r[11], '')}
    for i in range(12): c['m'][pl][i] += vols[i]; c['g'][pl][i] += num(r[GPc[i]]) * 1e6

def classify(k, sn, plan, base):
    cust_hist = cust26.get(k, 0) > 0 or cust25.get(k, 0) > 0
    sku_hist = sum(a26q.get((k, sn), [0] * 4)) > 0 or a25.get((k, sn), 0) > 0
    if not cust_hist: return '1'
    if not sku_hist: return '2'
    return '3' if plan > THRESH * base else '0'
recs = []
for (rx, k, sn), c in L.items():
    m = c['meta']; tot = [c['m']['Rayong'][i] + c['m']['TKT'][i] for i in range(12)]
    q27 = [sum(tot[3 * i:3 * i + 3]) for i in range(4)]; ry = [sum(c['m']['Rayong'][3 * i:3 * i + 3]) for i in range(4)]; tk = [sum(c['m']['TKT'][3 * i:3 * i + 3]) for i in range(4)]
    gry = [sum(c['g']['Rayong'][3 * i:3 * i + 3]) for i in range(4)]; gtk = [sum(c['g']['TKT'][3 * i:3 * i + 3]) for i in range(4)]; g27 = [gry[i] + gtk[i] for i in range(4)]
    b = a26q.get((k, sn), [0.0] * 4); bmax = max(b[0], b[1], b[2])
    ref = max(q27[0], q27[1]) if (q27[0] + q27[1]) > 0 else max(q27[2], q27[3])     # H1 if the line ships in H1, else H2
    ty = classify(k, sn, ref, bmax)
    recs.append(dict(m, key=k, t25=a25.get((k, sn), 0.0), gp25=g25.get((k, sn), 0.0), t26=sum(b), q26=b, gq26=g26q.get((k, sn), [0.0] * 4), jan=tot[0], feb=tot[1], mar=tot[2],
                     q27=q27, ry=ry, tk=tk, g27=g27, gry=gry, gtk=gtk, fy27=sum(tot), ty=ty, bmax=bmax, c26=cust26.get(k, 0.0), c25=cust25.get(k, 0.0)))
recs.sort(key=lambda x: (RX.index(x['rx']), -x['q27'][0], -x['q27'][1], -x['fy27']))
planned = {(x['rx'], x['key'], x['sn']) for x in recs}
notplan = collections.defaultdict(lambda: {'t25': 0.0, 'g25': 0.0, 'n25': set(), 'l25': 0, 't26': 0.0, 'g26': 0.0, 'n26': set(), 'l26': 0, 'q26': [0.0] * 4})
for (k, sn), rx in act_rx.items():
    if (rx, k, sn) in planned: continue
    v25 = a25.get((k, sn), 0.0); v26 = a26q.get((k, sn), [0.0] * 4)
    if v25 <= 0 and sum(v26) <= 0: continue
    o = notplan[rx]
    if v25 > 0: o['t25'] += v25; o['g25'] += g25.get((k, sn), 0.0); o['n25'].add(k); o['l25'] += 1
    if sum(v26) > 0: o['t26'] += sum(v26); o['g26'] += sum(g26q.get((k, sn), [0.0] * 4)); o['n26'].add(k); o['l26'] += 1
    for i in range(4): o['q26'][i] += v26[i]
print('lines', len(recs), '| ' + ' '.join(f"{QN[i]} {sum(x['q27'][i] for x in recs):,.0f}" for i in range(4)), '| FY', round(sum(x['fy27'] for x in recs)))
json.dump({f"{x['rx']}|{x['key']}|{x['sn']}": x['ty'] for x in recs}, open('risk_types.json', 'w', encoding='utf-8'))   # shared with the tracker builder

# ---------- workbook helpers ----------
wb = openpyxl.Workbook()
NAVY = '1F3A5F'; HFNT = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor=NAVY); SUBF = PatternFill('solid', fgColor='DCE3EC'); GREY = 'F2F2F2'
thin = Side(style='thin', color='BFBFBF'); med = Side(style='medium', color=NAVY)
NUM, PCT, DEC2 = '#,##0', '0%', '0.00'
def header(ws, cols, r1, r2, widths):
    c0 = 1; NC = len(cols)
    while c0 <= NC:
        g = cols[c0 - 1][0]; c1 = c0
        while c1 + 1 <= NC and cols[c1][0] == g: c1 += 1
        if g:
            ws.cell(row=r1, column=c0, value=g)
            if c1 > c0: ws.merge_cells(start_row=r1, start_column=c0, end_row=r1, end_column=c1)
            cc = ws.cell(row=r1, column=c0); cc.font = HFNT; cc.fill = HF; cc.alignment = Alignment(horizontal='center')
        c0 = c1 + 1
    for j, (_, s_) in enumerate(cols, 1):
        cc = ws.cell(row=r2, column=j, value=s_); cc.font = Font(bold=True, color=NAVY); cc.fill = SUBF; cc.alignment = Alignment(horizontal='center', wrap_text=True); cc.border = Border(bottom=med)
        ws.column_dimensions[CL(j)].width = widths[j - 1] if j <= len(widths) else 9
    ws.row_dimensions[r2].height = 30
def vlines(ws, cols_, r_from, r_to, hdr_row):
    for j in cols_:
        for rr in range(r_from, r_to + 1):
            cc = ws.cell(row=rr, column=j); cc.border = Border(left=Side(style='thin', color='FFFFFF' if rr == hdr_row else NAVY), top=cc.border.top, bottom=cc.border.bottom)
    for j in range(1, ws.max_column + 1):
        cc = ws.cell(row=hdr_row, column=j); cc.border = Border(left=cc.border.left, top=Side(style='thin', color='FFFFFF'), bottom=Side(style='thin', color='FFFFFF'))
def group_starts(cols):
    out = []; last = None
    for j, (g, _) in enumerate(cols, 1):
        if g != last and g: out.append(j)
        last = g
    return out[1:]   # skip the first group (no left line needed)

# ---------- README ----------
ws = wb.active; ws.title = 'README'
notes = ['HVA 2027 volume delivery risk by reaction group, Q1-Q4 2027 (v9)',
         'Question: how much of each 2027 quarter depends on something that has not happened yet, and of what kind.',
         'Risk types (one per customer group x SN, Rayong + TKT combined):',
         '  1  New customer: the customer group has no invoiced sales in 2025 or 2026 Jan-Sep.',
         '  2  Existing customer, new SKU: the customer bought from us before, but never this SN.',
         '  3  +30% volume vs 2026 max quarter: the customer bought this SN before and the plan quarter (higher of Q1 / Q2 2027; for lines that only ship in H2, higher of Q3 / Q4) is more than 130% of the best 2026 quarter of that customer (max of Q1-Q3 2026). If the SN was bought only in 2025, the base is zero and the line is type 3.',
         '  0  Running base: same customer and SKU, within +30% of the best 2026 quarter.',
         '  x  Sold in 2025 and/or 2026 but not in the 2027 plan at all (Summary only, so the actual columns tie to the profitability file).',
         'The type is one per line and is used for every period, so 2025 FY, 2026 YTD and all four 2027 quarters sit under the same type for that customer x SN; actuals can only fall under 3, 0 or x.',
         'Product GP/kg: actuals = (net sales - Actual Cost - freight - insurance) / tonnes from the profitability file (product basis, before idle, PPA and other adjustments). 2027 = AP plan product GP / tonnes from the data sheet, Rayong + TKT combined and per plant.',
         'Colour of the risk type = risk profile, muted traffic light: 1 soft red (highest), 2 soft orange, 3 soft yellow, 0 soft green (running base), x grey (not in the 2027 plan).',
         'Sheets: Summary and By customer (tonnes, counts, shares) · Summary GP-kg and By customer GP-kg = the same sheets with product GP/kg columns added · Pivot-ready (long format with tonnes, GP and GP/kg).',
         'Sources: 2027 plan = Top Line HVA Thailand_Oct1 Revised ASP_Final.xlsx, sheet "data" (AP + headroom, monthly, customer x SN x plant). Actuals = TDC Profitability_Act 2024-2026_Jul2026_AddPPA, data_Actual (2025 FY, 2026 Jan-Sep). Customer groups matched by code; Huifa + Qingdao Miracle merged. AP customer names in orange where they differ from the profitability customer group.',
         'Prepared 20 Oct 2026 by FP&A.']
for i, n in enumerate(notes, 1):
    c = ws.cell(row=i, column=1, value=n); c.alignment = Alignment(wrap_text=True, vertical='top')
ws['A1'].font = Font(bold=True, size=13, color=NAVY); ws.column_dimensions['A'].width = 150

# ---------- Summary (tonnes) and Summary GP-kg ----------
def build_summary(name, with_gp):
    ws = wb.create_sheet(name); ws.sheet_view.showGridLines = False
    ws['A1'] = ('Volume' + (' and product GP/kg' if with_gp else '')) + ' by reaction group and delivery-risk type: 2025 FY · 2026 YTD Sep · Q1-Q4 2027'; ws['A1'].font = Font(bold=True, size=13, color=NAVY)
    ws['A2'] = ('Row x = customer x SN sold in 2025/2026 but absent from the 2027 plan, so the 2025 and 2026 columns tie to the profitability file. Type = one classification per customer x SN (plan quarter vs the best 2026 quarter, +30%), applied to every period. '
                '# cust = customer groups; # cust x SN = lines. 2027 tonnes = AP plan incl. headroom, Rayong + TKT; TKT t = portion planned at TKT.' + (' GP/kg = product GP / tonnes of the rows in the group; Rayong / TKT GP/kg = per plant.' if with_gp else ''))
    ws['A2'].alignment = Alignment(wrap_text=True, vertical='top'); ws.merge_cells('A2:X2'); ws.row_dimensions[2].height = 45
    act = ['# cust', '# cust×SN', 'Tonnes', '% of reaction'] + (['GP/kg'] if with_gp else [])
    pln = ['# cust', '# cust×SN', 'Tonnes', '% of reaction', 'of which TKT t', 'Best 2026 qtr t'] + (['GP/kg', 'Rayong GP/kg', 'TKT GP/kg'] if with_gp else [])
    blocks = [('2025 FY actual', act), ('2026 YTD Sep actual', act)] + [(f'{QN[i]} plan', pln) for i in range(4)]
    cols = [('', 'Reaction'), ('', 'Risk type')] + [(lab, s_) for lab, subs in blocks for s_ in subs]
    header(ws, cols, 4, 5, [10, 38] + [9] * (len(cols) - 2))
    def put(r, col, v, fmt=None, fill=None, bold=False):
        cc = ws.cell(row=r, column=col, value=v)
        if fmt: cc.number_format = fmt
        if fill: cc.fill = PatternFill('solid', fgColor=fill)
        if bold: cc.font = Font(bold=True)
        return cc
    def gk(sel, qi, pl=None):
        if pl == 'Rayong': v = sum(x['ry'][qi] for x in sel); g = sum(x['gry'][qi] for x in sel)
        elif pl == 'TKT': v = sum(x['tk'][qi] for x in sel); g = sum(x['gtk'][qi] for x in sel)
        else: v = sum(x['q27'][qi] for x in sel); g = sum(x['g27'][qi] for x in sel)
        return kg(g, v)
    def act_vals(sel, y, T, extra_t=0.0, extra_g=0.0, extra_n=None, extra_l=0):
        t = sum(x['t' + y] for x in sel) + extra_t; g = (sum(x['gp25'] for x in sel) if y == '25' else sum(sum(x['gq26']) for x in sel)) + extra_g
        n = len({x['key'] for x in sel if x['t' + y] > 0} | (extra_n or set())); l = sum(1 for x in sel if x['t' + y] > 0) + extra_l
        return [n or None, l or None, t or None, t / T if T and t else None] + ([kg(g, t)] if with_gp else [])
    def plan_vals(sel, qi, T):
        t = sum(x['q27'][qi] for x in sel); n = len({x['key'] for x in sel if x['q27'][qi] > 0}); l = sum(1 for x in sel if x['q27'][qi] > 0)
        return [n or None, l or None, t or None, t / T if T and t else None, sum(x['tk'][qi] for x in sel) or None, sum(x['bmax'] for x in sel) or None] + ([gk(sel, qi), gk(sel, qi, 'Rayong'), gk(sel, qi, 'TKT')] if with_gp else [])
    fa = [NUM, NUM, NUM, PCT] + ([DEC2] if with_gp else []); fp = [NUM, NUM, NUM, PCT, NUM, NUM] + ([DEC2, DEC2, DEC2] if with_gp else [])
    fm = [None, None] + fa + fa + fp * 4
    def write(r, vals, fill=None, bold=False, top=False):
        for j, (v, f_) in enumerate(zip(vals, fm), 1):
            cc = put(r, j, v, f_, fill, bold)
            if top: cc.border = Border(top=thin)
    r = 6; grand = collections.defaultdict(lambda: collections.defaultdict(float))
    for rx in RX:
        sel = [x for x in recs if x['rx'] == rx]
        if not sel: continue
        o = notplan.get(rx, notplan.default_factory())
        T25 = sum(x['t25'] for x in sel) + o['t25']; T26 = sum(x['t26'] for x in sel) + o['t26']; TQ = [sum(x['q27'][i] for x in sel) for i in range(4)]
        put(r, 1, rx).font = Font(bold=True, size=12, color=NAVY)
        for j in range(1, len(cols) + 1): ws.cell(row=r, column=j).border = Border(top=med)
        r += 1
        for ty in ORDER:
            s_ = [x for x in sel if x['ty'] == ty]
            vals = [rx, TYPES[ty]] + act_vals(s_, '25', T25) + act_vals(s_, '26', T26)
            for qi in range(4): vals += plan_vals(s_, qi, TQ[qi])
            write(r, vals); ws.cell(row=r, column=2).fill = PatternFill('solid', fgColor=TYPEF[ty])
            grand['25'][ty] += sum(x['t25'] for x in s_); grand['26'][ty] += sum(x['t26'] for x in s_)
            for qi in range(4): grand[f'q{qi+1}'][ty] += sum(x['q27'][qi] for x in s_)
            r += 1
        xv = [rx, TYPES['x'], len(o['n25']) or None, o['l25'] or None, o['t25'] or None, o['t25'] / T25 if T25 and o['t25'] else None] + ([kg(o['g25'], o['t25'])] if with_gp else []) + \
             [len(o['n26']) or None, o['l26'] or None, o['t26'] or None, o['t26'] / T26 if T26 and o['t26'] else None] + ([kg(o['g26'], o['t26'])] if with_gp else [])
        for qi in range(4): xv += [None, None, None, None, None, max(o['q26'][:3]) or None] + ([None] * 3 if with_gp else [])
        write(r, xv); ws.cell(row=r, column=2).fill = PatternFill('solid', fgColor=TYPEF['x']); grand['25']['x'] += o['t25']; grand['26']['x'] += o['t26']; r += 1
        tot = ['Total ' + rx, ''] + act_vals(sel, '25', T25, o['t25'], o['g25'], o['n25'], o['l25']) + act_vals(sel, '26', T26, o['t26'], o['g26'], o['n26'], o['l26'])
        tot[5] = 1 if T25 else None; tot[5 + len(fa)] = 1 if T26 else None
        for qi in range(4):
            pv = plan_vals(sel, qi, TQ[qi]); pv[3] = 1 if TQ[qi] else None; pv[5] = (pv[5] or 0) + max(o['q26'][:3]); tot += pv
        write(r, tot, GREY, True, True); r += 2
    put(r, 1, 'ALL REACTIONS').font = Font(bold=True, size=12, color=NAVY)
    for j in range(1, len(cols) + 1): ws.cell(row=r, column=j).border = Border(top=med)
    r += 1
    G = {p: sum(grand[p].values()) for p in ('25', '26', 'q1', 'q2', 'q3', 'q4')}
    oall = {'t25': sum(o['t25'] for o in notplan.values()), 'g25': sum(o['g25'] for o in notplan.values()), 't26': sum(o['t26'] for o in notplan.values()), 'g26': sum(o['g26'] for o in notplan.values())}
    for ty in ORDER + ['x']:
        s_ = [x for x in recs if x['ty'] == ty]
        if ty == 'x':
            vals = ['All', TYPES['x'], None, None, oall['t25'] or None, oall['t25'] / G['25'] if G['25'] else None] + ([kg(oall['g25'], oall['t25'])] if with_gp else []) + [None, None, oall['t26'] or None, oall['t26'] / G['26'] if G['26'] else None] + ([kg(oall['g26'], oall['t26'])] if with_gp else []) + [None] * (4 * len(fp))
        else:
            vals = ['All', TYPES[ty]] + act_vals(s_, '25', G['25']) + act_vals(s_, '26', G['26'])
            for qi in range(4): vals += plan_vals(s_, qi, G[f'q{qi+1}'])
            vals[2] = vals[3] = None; vals[2 + len(fa)] = vals[3 + len(fa)] = None
        write(r, vals); ws.cell(row=r, column=2).fill = PatternFill('solid', fgColor=TYPEF[ty]); r += 1
    tot = ['Total', ''] + act_vals(recs, '25', G['25'], oall['t25'], oall['g25']) + act_vals(recs, '26', G['26'], oall['t26'], oall['g26'])
    for qi in range(4): tot += plan_vals(recs, qi, G[f'q{qi+1}'])
    tot[2] = tot[3] = tot[2 + len(fa)] = tot[3 + len(fa)] = None; tot[5] = 1; tot[5 + len(fa)] = 1
    write(r, tot, GREY, True, True); r += 2
    ws.cell(row=r, column=1, value='Reading: 2025 and 2026 columns show what the type-3 and type-0 accounts actually delivered, so the 2027 step-up can be judged against their own history. Types 1 and 2 need a first order before any tonne ships.' + (' GP/kg lets you see whether the risky tonnes are also the thin-margin tonnes.' if with_gp else ''))
    vlines(ws, group_starts(cols), 4, r, 4); ws.freeze_panes = 'C6'
build_summary('Summary', False); build_summary('Summary GP-kg', True)

# ---------- By customer (tonnes) and By customer GP-kg ----------
def build_bycust(name, with_gp):
    ws = wb.create_sheet(name); ws.sheet_view.showGridLines = False
    groups = [('Customer / SKU', ['Reaction', 'Customer group', 'Customer name (AP)', 'Code', 'AP customer type', 'Channel', 'PIC', 'Country', 'SN', 'Trade name']),
              ('Risk type', ['Type (one per customer × SKU)', 'Best 2026 quarter (t)']),
              ('Actual (t)', ['2025 FY', '2026 YTD Sep', "Q1'26", "Q2'26", "Q3'26"]),
              ('2027 plan, total (t)', ["Jan'27", "Feb'27", "Mar'27", "Q1'27", "Q2'27", "H1'27", "Q3'27", "Q4'27", "FY'27"]),
              ('2027 plan, Rayong (t)', QN), ('2027 plan, TKT (t)', QN),
              ('Growth vs best 2026 quarter', QN)]
    if with_gp:
        groups += [('Actual product GP/kg', ['2025 FY', '2026 YTD Sep', "Q1'26", "Q2'26", "Q3'26"]),
                   ('2027 plan product GP/kg, total', QN), ('2027 plan GP/kg, Rayong', QN), ('2027 plan GP/kg, TKT', QN),
                   ('Plan product GP THB M (for weighted average)', QN)]
    groups += [('Follow-up', ['Owner', 'Evidence (PO / trial / approval)', 'Status'])]
    cols = [(g, s_) for g, subs in groups for s_ in subs]; NC = len(cols)
    idx = {}
    for j, (g, s_) in enumerate(cols, 1): idx[(g, s_)] = j
    def col(g, s_): return idx[(g, s_)]
    wid = [8, 30, 30, 9, 9, 9, 6, 11, 8, 15, 30, 10] + [9] * (NC - 15) + [10, 28, 10]
    HR1, HR2, D0 = 2, 3, 4
    header(ws, cols, HR1, HR2, wid)
    tons_cols = list(range(col('Actual (t)', '2025 FY'), col('Growth vs best 2026 quarter', QN[0])))
    growth_cols = [col('Growth vs best 2026 quarter', q) for q in QN]
    gp_cols = list(range(col('Actual product GP/kg', '2025 FY'), col('Plan product GP THB M (for weighted average)', QN[0]))) if with_gp else []
    gpm_cols = [col('Plan product GP THB M (for weighted average)', q) for q in QN] if with_gp else []
    for i, x in enumerate(recs, D0):
        q = x['q27']; b = x['q26']; gq = x['gq26']
        vals = [x['rx'], x['grp'], x['name'], x['code'], x['apseg'], x['channel'], x['pic'], x['country'], x['sn'], x['trade'], TYPES[x['ty']], x['bmax'] or None,
                x['t25'] or None, x['t26'] or None, b[0] or None, b[1] or None, b[2] or None,
                x['jan'] or None, x['feb'] or None, x['mar'] or None, q[0] or None, q[1] or None, (q[0] + q[1]) or None, q[2] or None, q[3] or None, x['fy27'] or None]
        vals += [x['ry'][i] or None for i in range(4)] + [x['tk'][i] or None for i in range(4)]
        vals += [(q[i] / x['bmax'] - 1) if x['bmax'] and q[i] else None for i in range(4)]
        if with_gp:
            vals += [kg(x['gp25'], x['t25']), kg(sum(gq), x['t26']), kg(gq[0], b[0]), kg(gq[1], b[1]), kg(gq[2], b[2])]
            vals += [kg(x['g27'][i], q[i]) for i in range(4)] + [kg(x['gry'][i], x['ry'][i]) for i in range(4)] + [kg(x['gtk'][i], x['tk'][i]) for i in range(4)]
            vals += [x['g27'][i] / 1e6 if q[i] else None for i in range(4)]
        vals += ['', '', '']
        for j, v in enumerate(vals, 1):
            cc = ws.cell(row=i, column=j, value=v)
            if j == 12 or j in tons_cols: cc.number_format = NUM
            elif j in growth_cols: cc.number_format = '+0%;-0%;0%'
            elif j in gp_cols: cc.number_format = DEC2
            elif j in gpm_cols: cc.number_format = '#,##0.00'
        ws.cell(row=i, column=11).fill = PatternFill('solid', fgColor=TYPEF[x['ty']])
        if norm(x['grp']) != norm(x['name']) or x['grp'].strip() in KEEP_N or norm(x['grp']) in KEEP_N: ws.cell(row=i, column=3).font = Font(color='C55A11')
    LAST = len(recs) + D0 - 1
    vlines(ws, group_starts(cols), HR1, LAST, HR1)
    ws.cell(row=1, column=1, value='Filtered total (t)' + (' / weighted GP/kg' if with_gp else '')).font = Font(bold=True, color=NAVY)
    ws.cell(row=1, column=2, value='=SUBTOTAL(3,B{0}:B{1})&" lines"'.format(D0, LAST)).font = Font(bold=True)
    for j in [12] + tons_cols:
        cc = ws.cell(row=1, column=j, value=f"=SUBTOTAL(9,{CL(j)}{D0}:{CL(j)}{LAST})"); cc.number_format = NUM; cc.font = Font(bold=True); cc.fill = PatternFill('solid', fgColor='FFF2CC')
    if with_gp:
        for i, qn in enumerate(QN):
            tc = col('2027 plan, total (t)', qn); gc = gpm_cols[i]; j = col('2027 plan product GP/kg, total', qn)
            cc = ws.cell(row=1, column=j, value=f"=IFERROR(SUBTOTAL(9,{CL(gc)}{D0}:{CL(gc)}{LAST})*1000/SUBTOTAL(9,{CL(tc)}{D0}:{CL(tc)}{LAST}),\"\")"); cc.number_format = DEC2; cc.font = Font(bold=True); cc.fill = PatternFill('solid', fgColor='FFF2CC')
        for j in gpm_cols:
            cc = ws.cell(row=1, column=j, value=f"=SUBTOTAL(9,{CL(j)}{D0}:{CL(j)}{LAST})"); cc.number_format = '#,##0.00'; cc.font = Font(bold=True); cc.fill = PatternFill('solid', fgColor='FFF2CC')
    ws.row_dimensions[1].height = 18
    jan, mar = col('2027 plan, total (t)', "Jan'27"), col('2027 plan, total (t)', "Mar'27")
    ws.column_dimensions.group(CL(jan), CL(mar), hidden=False, outline_level=1); ws.sheet_properties.outlinePr.summaryRight = True
    ws.freeze_panes = f'C{D0}'; ws.auto_filter.ref = f"A{HR2}:{CL(NC)}{LAST}"
build_bycust('By customer', False); build_bycust('By customer GP-kg', True)

# ---------- Pivot-ready ----------
ws = wb.create_sheet('Pivot-ready')
hd = ['Period', 'Reaction', 'Plant', 'Risk type', 'Best 2026 quarter t', 'Customer group', 'SN', 'Trade name', 'Country', 'AP customer type', 'Tonnes', 'Product GP THB M', 'Product GP/kg']
for j, h in enumerate(hd, 1):
    cc = ws.cell(row=1, column=j, value=h); cc.font = HFNT; cc.fill = HF; ws.column_dimensions[CL(j)].width = 30 if j in (4, 6) else 12
for x in recs:
    def row(period, plant, t, g):
        if t: ws.append([period, x['rx'], plant, TYPES[x['ty']], round(x['bmax'], 1), x['grp'], x['sn'], x['trade'], x['country'], x['apseg'], round(t), round(g / 1e6, 3), round(g / t / 1000, 2)])
    row('2025 FY', 'actual', x['t25'], x['gp25']); row('2026 YTD Sep', 'actual', x['t26'], sum(x['gq26']))
    for qi, qn in ((0, "Q1'26"), (1, "Q2'26"), (2, "Q3'26")): row(qn, 'actual', x['q26'][qi], x['gq26'][qi])
    for qi in range(4):
        row(QN[qi], 'Rayong', x['ry'][qi], x['gry'][qi]); row(QN[qi], 'TKT', x['tk'][qi], x['gtk'][qi])
ws.freeze_panes = 'A2'; ws.auto_filter.ref = f"A1:M{ws.max_row}"
hva_format.apply(wb, 'risk')
wb.save(OUT); print('saved', OUT)
