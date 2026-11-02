# TWIT HVA table (Por 30-Oct) in the layout of the Indonesia customer x SN table, YTD Sep-25 and YTD Sep-26 side by side.
# Writes an Excel sheet (values, formatted). Benchmarks two ways: same SN and same reaction group (Por 30-Oct).  Usage: python twit_table_out.py <twit_table.json> <out.xlsx>
import sys, json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
J, XL = sys.argv[1], sys.argv[2]
D = json.load(open(J, encoding='utf-8'))
SHORT = {'Guangdong Jinkai Food Technology Co., Ltd.': 'Guangdong Jinkai', 'Shanghai Wujia Trading Co., Ltd.': 'Shanghai Wujia', 'Shanghai Suihang International Trade Co., Ltd.': 'Shanghai Suihang',
         'Guangzhou Xiangda Food Co.,Ltd': 'Guangzhou Xiangda', 'ThaiWah Food (Zhejiang) Co., Ltd': 'ThaiWah Food Zhejiang', 'TOYAR CHEMICALS CO., LIMITED': 'Toyar Chemicals'}
NOTE = {'ThaiWah Food (Zhejiang) Co., Ltd': 'related party', 'Huifa (incl. Qingdao Miracle)': ''}
RX = {}
for b in D['via']:
    for l in b['sns']: RX.setdefault(l['sn'], l['rx'])
COLS = ['Customer', 'SN', 'Product', 'Reaction', 'YTD 25', 'YTD 26', 'YTD 25', 'YTD 26', 'YTD 25', 'YTD 26', 'YTD 25', 'YTD 26', 'Bench vol\nYTD 26 (t)', 'YTD 25', 'YTD 26', 'YTD 25', 'YTD 26', 'Bench vol\nYTD 26 (t)', 'YTD 25', 'YTD 26', 'YTD 25', 'YTD 26']
GROUPS = [(5, 6, 'Vol (t)'), (7, 8, 'TDC GP/kg (1)'), (9, 10, 'TWIT GP/kg (2)'), (11, 12, 'Combined (1) + (2)'), (13, 15, 'Benchmark by SN: TDC – non-China'), (16, 17, 'Gap vs SN bench'), (18, 20, 'Benchmark by reaction: TDC – non-China'), (21, 22, 'Gap vs reaction bench')]
NC = len(COLS)
rows = []   # (kind, values[NC])
def num(v): return None if v is None else v
def line(kind, a, b, c, d, x, via):
    rows.append((kind, [a, b, c, d, x['t25'], x['t26'], x['tdc25'], x['tdc26'], x.get('tw25') if via else None, x.get('tw26') if via else None,
                        x.get('c25') if via else None, x.get('c26') if via else None, x['bt'] or None, x['b25'], x['b26'], x['g25'], x['g26'], x['rbt'] or None, x['rb25'], x['rb26'], x['rg25'], x['rg26']]))
rows.append(('sec', ['1  Route to market: TDC → China customer (direct)'] + [None] * (NC - 1)))
for b in D['direct']:
    line('cust', b['cust'], None, None, None, b, False)
    for l in b['sns']: line('sn', None, l['sn'], l['name'], l['rxg'].replace('PO-XL', 'POXL'), l, False)
line('sub', 'Subtotal — TDC direct China', None, 'all direct accounts', None, D['direct_total'], False)
rows.append(('sec', ['2  Route to market: TDC → TWIT → customer'] + [None] * (NC - 1)))
for b in D['via']:
    nm = SHORT.get(b['cust'], b['cust']); note = b.get('note') or NOTE.get(b['cust'], '')
    line('cust', nm, None, note, None, b, True)
    for l in b['sns']: line('sn', None, l['sn'], l['name'].title() if l['name'].isupper() else l['name'], l['rxg'].replace('PO-XL', 'POXL'), l, True)
line('sub', 'Subtotal — via TWIT', None, 'HVA, TDC products', None, D['via_total'], True)
# ---------- Excel ----------
wb = Workbook(); ws = wb.active; ws.title = 'TWIT HVA table'
GREY, DARK, GREEN, RED = '595959', '262626', '00A651', 'C00000'
thin = Side(style='thin', color='808080'); hair = Side(style='hair', color='BFBFBF')
f_sec = PatternFill('solid', fgColor='D9D9D9'); f_cust = PatternFill('solid', fgColor='F2F2F2'); f_sub = PatternFill('solid', fgColor='E7E6E6')
ws['A1'] = 'TWIT HVA (modified starch) — TDC direct China vs TDC → TWIT → customer, YTD Sep-25 vs YTD Sep-26 (reported FX, THB/kg)'; ws['A1'].font = Font(name='Arial', size=11, bold=True, color=DARK)
for c1, c2, t in GROUPS:
    ws.cell(3, c1, t); ws.merge_cells(start_row=3, start_column=c1, end_row=3, end_column=c2)
    for c in range(c1, c2 + 1): ws.cell(3, c).border = Border(bottom=thin, left=thin if c == c1 else None)
    ws.cell(3, c1).font = Font(name='Arial', size=9, bold=True, color=GREY); ws.cell(3, c1).alignment = Alignment(horizontal='center')
for i, h in enumerate(COLS, 1):
    c = ws.cell(4, i, h); c.font = Font(name='Arial', size=8.5, bold=True, color=GREY); c.alignment = Alignment(horizontal='left' if i <= 4 else 'right', vertical='bottom', wrap_text=True)
    c.border = Border(bottom=thin)
ws.row_dimensions[4].height = 26
FMT = {5: '#,##0', 6: '#,##0', 13: '#,##0', 18: '#,##0'}
r0 = 5
for k, (kind, v) in enumerate(rows):
    r = r0 + k
    g26 = v[16]
    good = g26 is not None and g26 >= 0 and kind in ('cust', 'sn')
    for i, x in enumerate(v, 1):
        c = ws.cell(r, i, x)
        bold = kind in ('cust', 'sub', 'sec')
        color = GREEN if good else DARK if kind != 'sn' or i in (1,) else GREY
        if i in (16, 17, 21, 22) and isinstance(x, (int, float)) and x < 0: color = RED; bold = True if kind != 'sn' else False
        c.font = Font(name='Arial', size=9, bold=bold if (kind == 'sec' or i == 1 or i >= 5) else False, color=color)
        if i >= 5: c.number_format = FMT.get(i, '0.00;-0.00'); c.alignment = Alignment(horizontal='right')
        if kind == 'sec': c.fill = f_sec
        elif kind == 'cust': c.fill = f_cust
        elif kind == 'sub': c.fill = f_sub; c.border = Border(top=thin, bottom=thin)
        if i in (5, 7, 9, 11, 13, 16, 18, 21) and kind != 'sec': c.border = Border(left=hair, top=c.border.top, bottom=c.border.bottom)
    if kind == 'sn': ws.cell(r, 2).font = Font(name='Arial', size=9, color=GREEN if good else GREY)
last = r0 + len(rows) - 1
notes = ['(1) TDC GP/kg = full-cost GP (net sales − actual cost − F&I − idle − PPA − other adj.), TDC Profitability data_Actual. On the TWIT rows it is TDC\'s own GP on its sales to TWIT of the same SN in the same quarter, applied to TWIT\'s tonnes.',
         '(2) TWIT GP/kg = TWIT reported GP in THB (TWIT Raw data, monthly reported FX). Combined = (1) + (2) = what the group keeps per kg sold to the end customer.',
         'Benchmark = TDC full-cost GP/kg on the same SN to third-party customers outside China (related parties TWIN and TW India left out), weighted by each customer\'s own SN mix in that year. Bench vol = non-China tonnes YTD Sep-26 on the customer\'s SNs.',
         f"SNs sold only in China have no benchmark (e.g. SN-534 JF-206 to SunChina, SN-495 Cassmax 33, SN-112 Tapfil-860): the benchmark covers {D['direct_total']['cov25']:.0%} / {D['direct_total']['cov26']:.0%} of direct tonnes and {D['via_total']['cov25']:.0%} / {D['via_total']['cov26']:.0%} of TWIT tonnes (YTD 25 / YTD 26).",
         "Benchmark by reaction = TDC full-cost GP/kg of all non-China third-party sales in the SN's reaction group (TDC 'Reaction group'), weighted by the customer's own reaction mix; covers every SN. YTD 25 → YTD 26: " + ', '.join(f"{g} {a:.2f} → {b:.2f}" for g, (a, b) in D['rx_bench'].items()) + '.',
         'Gap: direct rows = TDC GP/kg − benchmark; TWIT rows = combined GP/kg − benchmark (for both SN and reaction). Green row = at or above the SN benchmark in YTD 26.',
         'HVA only: native starch, tapioca coarse / pearl, sago, premix and guar excluded. SN lines under 20 t in both years are not shown but are in the customer totals. YTD = January–September.']
for i, t in enumerate(notes):
    c = ws.cell(last + 2 + i, 1, t); c.font = Font(name='Arial', size=8, color=GREY)
W = [30, 8, 22, 9, 9, 9, 8, 8, 8, 8, 9, 9, 10, 8, 8, 8, 8, 10, 8, 8, 8, 8]
for i, w in enumerate(W, 1): ws.column_dimensions[ws.cell(4, i).column_letter].width = w
ws.freeze_panes = 'E5'; ws.sheet_view.showGridLines = False
wb.save(XL)
print('ok', len(rows), 'rows')
