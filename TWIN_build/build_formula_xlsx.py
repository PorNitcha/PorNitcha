# Formula-driven workbook: every derived number is an Excel formula over Data + Assumptions.
# Usage: python build_formula_xlsx.py <dir with model.json> <out.xlsx>
import json, sys
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import CellIsRule

S, OUT = sys.argv[1], sys.argv[2]
M = json.load(open(f'{S}/model.json', encoding='utf-8'))
rows = sorted(M['rows'], key=lambda x: (x['month'], x['label'], x['prod']))
base = M['base']; EXCL = M.get('excluded') or []
EXNOTE = (' · excl. ' + ' / '.join(EXCL)) if EXCL else ''
months = sorted(M['idrthb'])

F = 'Arial'
f_norm = Font(name=F, size=9); f_bold = Font(name=F, size=9, bold=True); f_hdr = Font(name=F, size=9, bold=True, color='404040')
f_title = Font(name=F, size=12, bold=True); f_sub = Font(name=F, size=9, italic=True, color='7F7F7F'); f_grey = Font(name=F, size=9, color='7F7F7F')
f_sec = Font(name=F, size=10, bold=True, color='1F3864'); f_in = Font(name=F, size=9, color='0000FF')
fill_hdr = PatternFill('solid', fgColor='F2F2F2'); fill_grp = PatternFill('solid', fgColor='E7E6E6'); fill_tot = PatternFill('solid', fgColor='F2F2F2'); fill_in = PatternFill('solid', fgColor='FFF2CC')
RED, AMB, GRN = 'F1C7C7', 'FBF0C6', 'E2EFDA'
fill_rep = PatternFill('solid', fgColor='DDEBF7'); fill_con = PatternFill('solid', fgColor='E2EFDA'); fill_fx = PatternFill('solid', fgColor='FFF2CC')
thin = Side(style='thin', color='BFBFBF'); med = Side(style='medium', color='808080')
b_left = Border(left=thin); b_hdr = Border(bottom=med)
NUM0 = '#,##0;[Red]-#,##0;-'; NUM1 = '#,##0.0;[Red]-#,##0.0;-'; NUM2 = '#,##0.00;[Red]-#,##0.00;-'; PCT = '0.0%;[Red]-0.0%;-'
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True); WRAP = Alignment(wrap_text=True, vertical='top')

def put(ws, r, c, v, font=f_norm, fmt=None, fill=None, align=None, border=None):
    cell = ws.cell(row=r, column=c, value=v); cell.font = font
    if fmt: cell.number_format = fmt
    if fill: cell.fill = fill
    if align: cell.alignment = align
    if border: cell.border = border
    return cell
def traffic(ws, rng, lo=0, mid=2, hi=5):
    ws.conditional_formatting.add(rng, CellIsRule(operator='lessThan', formula=[str(lo)], fill=PatternFill('solid', fgColor=RED)))
    ws.conditional_formatting.add(rng, CellIsRule(operator='between', formula=[str(lo), str(mid)], fill=PatternFill('solid', fgColor=AMB)))
    ws.conditional_formatting.add(rng, CellIsRule(operator='greaterThanOrEqual', formula=[str(hi)], fill=PatternFill('solid', fgColor=GRN)))
def widths(ws, d):
    for k, v in d.items(): ws.column_dimensions[k].width = v
def q_of(m): return f"{m[:4]}Q{(int(m[5:]) - 1) // 3 + 1}"

wb = Workbook()

# ---------- period / year separator borders (Por, 26-Oct-2026: every sheet) ----------
def _merge_border(cell, left=None, top=None):
    b = cell.border
    cell.border = Border(left=left or b.left, right=b.right, top=top or b.top, bottom=b.bottom)
def vlines(ws, cols, r1, r2, side=None):
    side = side or thin
    for c in cols:
        for r in range(r1, r2 + 1): _merge_border(ws.cell(row=r, column=c), left=side)
def hlines(ws, rows, c1, c2, side=None):
    side = side or thin
    for r in rows:
        for c in range(c1, c2 + 1): _merge_border(ws.cell(row=r, column=c), top=side)
def year_start_cols(c0, pers):
    """columns where a new period group starts: every FY/YTD column + first quarter of each year"""
    out = []; prev_y = None
    for j, (name, y, mc, qc) in enumerate(pers):
        if qc == '*' or y != prev_y: out.append(c0 + j)
        prev_y = y if qc != '*' else None
    return out
# =====================================================================
# ASSUMPTIONS
# =====================================================================
wa = wb.active; wa.title = 'Assumptions'; wa.sheet_view.showGridLines = False
put(wa, 1, 1, 'Assumptions — base FX rates (editable) · monthly FX · TDC monthly data · TDC rate table per kg', f_title)
put(wa, 2, 1, 'Yellow cells / blue font = editable inputs; the whole workbook recalculates · other cells are formulas or values from the source files', f_sub)
put(wa, 4, 1, 'Base rates (constant FX)', f_sec)
put(wa, 5, 1, 'Base USD/THB'); put(wa, 5, 2, round(base['usdthb'], 4), f_in, fmt='0.0000', fill=fill_in); put(wa, 5, 3, '12-month average of 2024 (= AVERAGE of the monthly table) — any other rate can be entered', f_grey)
put(wa, 6, 1, 'Base IDR/THB'); put(wa, 6, 2, round(base['idrthb'], 7), f_in, fmt='0.0000000', fill=fill_in); put(wa, 6, 3, '12-month average of 2024', f_grey)
put(wa, 7, 1, 'Base USD/IDR'); put(wa, 7, 2, '=B5/B6', fmt='#,##0'); put(wa, 7, 3, 'Formula: Base USD/THB ÷ Base IDR/THB', f_grey)
put(wa, 8, 1, 'Check: avg 2024 USD/THB'); put(wa, 8, 2, '=AVERAGEIFS(B13:B%d,E13:E%d,"2024")' % (12 + len(months), 12 + len(months)), f_grey, fmt='0.0000')
put(wa, 9, 1, 'Check: avg 2024 IDR/THB'); put(wa, 9, 2, '=AVERAGEIFS(C13:C%d,E13:E%d,"2024")' % (12 + len(months), 12 + len(months)), f_grey, fmt='0.0000000')
BASE_U = 'Assumptions!$B$5'; BASE_I = 'Assumptions!$B$6'; BASE_X = 'Assumptions!$B$7'
put(wa, 11, 1, 'Monthly FX rates', f_sec)
for j, h in enumerate(['Month', 'USD/THB', 'IDR/THB', 'USD/IDR (=B/C)', 'Year', 'USD/THB source']): put(wa, 12, 1 + j, h, f_hdr, fill=fill_hdr, border=b_hdr)
for i, m in enumerate(months):
    r = 13 + i
    if m.endswith('-01') and i: hlines(wa, [r], 1, 6, thin)
    put(wa, r, 1, m); put(wa, r, 2, M['usdthb'][m], f_in, fmt='0.0000', fill=fill_in); put(wa, r, 3, M['idrthb'][m], f_in, fmt='0.0000000', fill=fill_in)
    put(wa, r, 4, f'=B{r}/C{r}', fmt='#,##0'); put(wa, r, 5, m[:4]); put(wa, r, 6, M['fxsrc'][m], f_grey)
FX_FIRST, FX_LAST = 13, 12 + len(months)
FX_M = f'Assumptions!$A${FX_FIRST}:$A${FX_LAST}'; FX_U = f'Assumptions!$B${FX_FIRST}:$B${FX_LAST}'; FX_I = f'Assumptions!$C${FX_FIRST}:$C${FX_LAST}'

# TDC monthly (source values) — columns H..R
tdc_m = sorted(((k.split('|')[0], k.split('|')[1], v) for k, v in M['tdc'].items()), key=lambda x: (x[1], x[0]))
r0 = 12
put(wa, 11, 8, 'TDC → PT Thai Wah Indonesia by month × SN (values from TDC Profitability data_Actual; USD = NS ÷ invoice rate per line)', f_sec)
th = ['Month', 'Quarter', 'Year', 'SN', 'Product (TWIN name)', 'Tons', 'NS THB', 'NS USD', 'Actual Cost (AF)', 'F&I', 'Idle', 'Other adj', 'PPA']
for j, h in enumerate(th): put(wa, r0, 8 + j, h, f_hdr, fill=fill_hdr, border=b_hdr)
for i, (m, sn, d) in enumerate(tdc_m):
    r = r0 + 1 + i
    if i and q_of(m)[:4] != q_of(tdc_m[i - 1][0])[:4]: hlines(wa, [r], 8, 20, thin)
    vals = [m, q_of(m), m[:4], sn, M['sn_name'].get(sn, sn), d['t'], d['ns'], d['usd'], d['af'], d['fi'], d['idle'], d['oadj'], d['ppa']]
    for j, v in enumerate(vals): put(wa, r, 8 + j, v, fmt=(NUM1 if j == 5 else (NUM0 if j > 5 else None)))
TM_FIRST, TM_LAST = r0 + 1, r0 + len(tdc_m)
def TM(col): return f'Assumptions!${col}${TM_FIRST}:${col}${TM_LAST}'
# columns: H month, I quarter, J year, K sn, L name, M t, N ns, O usd, P af, Q fi, R idle, S oadj, T ppa

# TDC rate table (SUMIFS over monthly) — columns V..AJ ; keys sn|quarter, sn|year, sn|ALL
keys = []
sns = sorted(set(sn for _, sn, _ in tdc_m), key=lambda s: -sum(d['t'] for _, s2, d in tdc_m if s2 == s))
qs_all = sorted(set(q_of(m) for m, _, _ in tdc_m)); ys_all = sorted(set(m[:4] for m, _, _ in tdc_m))
for sn in sns:
    for qq in qs_all: keys.append((sn, qq, 'Q'))
    for y in ys_all: keys.append((sn, y, 'Y'))
    keys.append((sn, 'ALL', 'ALL'))
put(wa, 11, 22, 'TDC rate table per kg (SUMIFS over the monthly table) — key = SN|period; Data picks the key in its rate_key column', f_sec)
rh = ['key', 'SN', 'Product', 'Period', 'basis', 'Tons', 'NS THB', 'NS USD', 'AF', 'F&I', 'Idle', 'Other adj', 'PPA', 'Transfer price THB/kg', 'USD/kg', 'Product cost THB/kg', 'Idle+PPA+adj THB/kg', 'Product GP THB/kg', 'Full GP THB/kg']
for j, h in enumerate(rh): put(wa, r0, 22 + j, h, f_hdr, fill=fill_hdr, border=b_hdr, align=CENTER)
wa.row_dimensions[r0].height = 30
for i, (sn, per, basis) in enumerate(keys):
    r = r0 + 1 + i
    put(wa, r, 22, f'{sn}|{per}'); put(wa, r, 23, sn); put(wa, r, 24, M['sn_name'].get(sn, sn)); put(wa, r, 25, per); put(wa, r, 26, basis)
    crit_col = {'Q': 'I', 'Y': 'J', 'ALL': None}[basis]
    for j, col in enumerate('MNOPQRST'):  # t ns usd af fi idle oadj ppa
        c = 27 + j
        if crit_col: f = f'=SUMIFS({TM(col)},{TM("K")},$W{r},{TM(crit_col)},$Y{r})'
        else: f = f'=SUMIFS({TM(col)},{TM("K")},$W{r})'
        put(wa, r, c, f, fmt=(NUM1 if j == 0 else NUM0))
    # per kg: AA t, AB ns, AC usd, AD af, AE fi, AF idle, AG oadj, AH ppa
    put(wa, r, 35, f'=IF(AA{r}>0,AB{r}/AA{r}/1000,0)', fmt=NUM2)                      # AI transfer/kg
    put(wa, r, 36, f'=IF(AA{r}>0,AC{r}/AA{r}/1000,0)', fmt='0.0000')                   # AJ usd/kg
    put(wa, r, 37, f'=IF(AA{r}>0,(AD{r}+AE{r})/AA{r}/1000,0)', fmt=NUM2)               # AK product cost/kg
    put(wa, r, 38, f'=IF(AA{r}>0,(AF{r}+AG{r}+AH{r})/AA{r}/1000,0)', fmt=NUM2)         # AL other/kg
    put(wa, r, 39, f'=AI{r}-AK{r}', fmt=NUM2); put(wa, r, 40, f'=AM{r}-AL{r}', fmt=NUM2)  # AM pGP/kg, AN fGP/kg
RK_FIRST, RK_LAST = r0 + 1, r0 + len(keys)
RK_KEY = f'Assumptions!$V${RK_FIRST}:$V${RK_LAST}'
def RK(col): return f'Assumptions!${col}${RK_FIRST}:${col}${RK_LAST}'
widths(wa, {'A': 24, 'B': 12, 'C': 12, 'D': 14, 'E': 6, 'F': 24, 'H': 9, 'I': 8, 'J': 6, 'K': 8, 'L': 16, 'V': 16, 'W': 8, 'X': 16, 'Y': 8, 'Z': 6})
for c in range(13, 21): wa.column_dimensions[L(c)].width = 11
for c in range(27, 41): wa.column_dimensions[L(c)].width = 11
wa.freeze_panes = 'A13'

# =====================================================================
# DATA — inputs + row formulas
# =====================================================================
wd = wb.create_sheet('Data'); wd.sheet_view.zoomScale = 85
inputs = [('month', 'month'), ('year', 'y'), ('month_num', None), ('quarter', 'q'), ('customer', 'label'), ('customer_key', 'cust'), ('customer_group', 'group'), ('country', 'country'),
          ('sale_currency', 'cur'), ('product', 'prod'), ('source', 'src'), ('tdc_sn', 'sn'), ('reaction', 'react'), ('rate_key', None), ('tons', 't'),
          ('twin_ns_idr', 'ns_idr'), ('twin_cogs_idr', 'cogs_idr'), ('twin_ns_thb', 'ns'), ('twin_cogs_thb', 'cogs')]
# formula columns (letter -> header, formula template with {r})
N = len(rows); R1, RN = 2, N + 1
fcols = [
 ('T', 'usdthb_m', '=INDEX(%s,MATCH($A{r},%s,0))' % (FX_U, FX_M), '0.0000'),
 ('U', 'idrthb_m', '=INDEX(%s,MATCH($A{r},%s,0))' % (FX_I, FX_M), '0.0000000'),
 ('V', 'usdidr_m', '=T{r}/U{r}', '#,##0'),
 ('W', 'twin_gp_thb', '=R{r}-S{r}', NUM0),
 ('X', 'twin_ns_usd', '=IF($I{r}="USD",P{r}/V{r},0)', NUM0),
 ('Y', 'twin_cogs_usd', '=Q{r}/V{r}', NUM0),
 ('Z', 'twin_ns_constFX', '=IF($I{r}="USD",X{r}*%s,P{r}*%s)' % (BASE_U, BASE_I), NUM0),
 ('AA', 'twin_cogs_constFX', '=Y{r}*%s' % BASE_U, NUM0),
 ('AB', 'twin_gp_constFX', '=Z{r}-AA{r}', NUM0),
 ('AC', 'twin_gp_idr', '=P{r}-Q{r}', NUM0),
 ('AD', 'twin_ns_idr_constUSDIDR', '=IF($I{r}="USD",X{r}*%s,P{r})' % BASE_X, NUM0),
 ('AE', 'twin_cogs_idr_constUSDIDR', '=Y{r}*%s' % BASE_X, NUM0),
 ('AF', 'twin_gp_idr_constUSDIDR', '=AD{r}-AE{r}', NUM0),
 ('AG', 'fx2_usdidr_twin_cost', '=(AC{r}-AF{r})*U{r}', NUM0),
 ('AH', 'fx3_idrthb_translation', '=AF{r}*(U{r}-%s)' % BASE_I, NUM0),
 ('AI', 'tdc_transfer_kg', '=IF($N{r}="",0,INDEX(%s,MATCH($N{r},%s,0)))' % (RK('AI'), RK_KEY), NUM2),
 ('AJ', 'tdc_usd_kg', '=IF($N{r}="",0,INDEX(%s,MATCH($N{r},%s,0)))' % (RK('AJ'), RK_KEY), '0.0000'),
 ('AK', 'tdc_product_cost_kg', '=IF($N{r}="",0,INDEX(%s,MATCH($N{r},%s,0)))' % (RK('AK'), RK_KEY), NUM2),
 ('AL', 'tdc_idle_ppa_adj_kg', '=IF($N{r}="",0,INDEX(%s,MATCH($N{r},%s,0)))' % (RK('AL'), RK_KEY), NUM2),
 ('AM', 'tdc_ns_thb', '=AI{r}*$O{r}*1000', NUM0),
 ('AN', 'tdc_ns_usd', '=AJ{r}*$O{r}*1000', NUM0),
 ('AO', 'tdc_product_cost', '=AK{r}*$O{r}*1000', NUM0),
 ('AP', 'tdc_idle_ppa_adj', '=AL{r}*$O{r}*1000', NUM0),
 ('AQ', 'tdc_product_gp', '=AM{r}-AO{r}', NUM0),
 ('AR', 'tdc_full_gp', '=AQ{r}-AP{r}', NUM0),
 ('AS', 'tdc_ns_constFX', '=AN{r}*%s' % BASE_U, NUM0),
 ('AT', 'tdc_product_gp_constFX', '=AS{r}-AO{r}', NUM0),
 ('AU', 'tdc_full_gp_constFX', '=AT{r}-AP{r}', NUM0),
 ('AV', 'fx1_usdthb_tdc', '=AM{r}-AS{r}', NUM0),
 ('AW', 'total_gp_product', '=W{r}+AQ{r}', NUM0),
 ('AX', 'total_gp_full', '=W{r}+AR{r}', NUM0),
 ('AY', 'total_gp_product_constFX', '=AB{r}+AT{r}', NUM0),
 ('AZ', 'total_gp_full_constFX', '=AB{r}+AU{r}', NUM0),
 ('BA', 'tons_tdc', '=IF($K{r}="TDC",$O{r},0)', NUM2),
 ('BB', 'fx_total', '=AV{r}+AG{r}+AH{r}', NUM0),
]
for j, (h, _) in enumerate(inputs): put(wd, 1, 1 + j, h, f_hdr, fill=fill_hdr)
from openpyxl.utils import column_index_from_string as CI
for col, h, _, _ in fcols: put(wd, 1, CI(col), h, f_hdr, fill=fill_hdr)
for i, x in enumerate(rows):
    r = R1 + i
    basis = x['tdc_basis']
    rate_key = '' if not x['sn'] else (f"{x['sn']}|{x['q']}" if basis == 'Q' else (f"{x['sn']}|{x['y']}" if basis == 'Y' else f"{x['sn']}|ALL"))
    for j, (h, k) in enumerate(inputs):
        if h == 'month_num': v = int(x['month'][5:])
        elif h == 'rate_key': v = rate_key
        else: v = x[k]
        c = put(wd, r, 1 + j, v, f_in if h in ('tons', 'twin_ns_idr', 'twin_cogs_idr', 'twin_ns_thb', 'twin_cogs_thb') else f_norm)
        if isinstance(v, float): c.number_format = NUM2 if h == 'tons' else NUM0
    for col, h, tmpl, fmt in fcols:
        put(wd, r, CI(col), tmpl.format(r=r), fmt=fmt)
put(wd, 1, 55, 'country_src', f_hdr, fill=fill_hdr)
for i, x in enumerate(rows): put(wd, R1 + i, 55, x.get('country_src', x['country']))
wd.freeze_panes = 'F2'; wd.auto_filter.ref = f'A1:BC{RN}'
for c in range(1, 55): wd.column_dimensions[L(c)].width = 12
wd.column_dimensions['E'].width = 36
def D(col): return f'Data!${col}${R1}:${col}${RN}'

# =====================================================================
# SUMIFS helpers
# =====================================================================
PERIODS = [('FY2024', '2024', '<=12', '*'), ('FY2025', '2025', '<=12', '*'), ('YTD Sep-25', '2025', '<=9', '*'), ('YTD Sep-26', '2026', '<=9', '*')]
QS = sorted(set(x['q'] for x in rows))
def qlabel(qq): return f"Q{qq[-1]}'{qq[2:4]}"
QPER = [(qlabel(qq), qq[:4], '<=12', qq) for qq in QS]
MEAS = {'t': 'O', 't_tdc': 'BA', 'ns': 'R', 'cogs': 'S', 'gp': 'W', 'gp_c': 'AB', 'tdc_ns': 'AM', 'tdc_pcost': 'AO', 'tdc_other': 'AP', 'tdc_pgp': 'AQ', 'tdc_fgp': 'AR',
        'tdc_ns_c': 'AS', 'tdc_pgp_c': 'AT', 'tdc_fgp_c': 'AU', 'chain_pgp': 'AW', 'chain_fgp': 'AX', 'chain_pgp_c': 'AY', 'chain_fgp_c': 'AZ', 'fx1': 'AV', 'fx2': 'AG', 'fx3': 'AH', 'fxt': 'BB'}
def SUMIFS(meas, yc, mc, qc, extra=''):
    """yc/mc/qc are cell refs (e.g. 'B$3') or literals"""
    return f'SUMIFS({D(MEAS[meas])},{D("B")},{yc},{D("C")},{mc},{D("D")},{qc}{extra})'
def crit_rows(ws, hdr_r, c0, pers, label_font=f_hdr):
    """write period header + 3 hidden criteria rows (year, month, quarter) above hdr_r; returns (yr_row, m_row, q_row)"""
    yr, mr, qr = hdr_r - 3, hdr_r - 2, hdr_r - 1
    put(ws, yr, c0 - 1, 'crit: year', f_grey); put(ws, mr, c0 - 1, 'crit: month', f_grey); put(ws, qr, c0 - 1, 'crit: quarter', f_grey)
    for j, (name, y, mc, qc) in enumerate(pers):
        put(ws, yr, c0 + j, y, f_grey); put(ws, mr, c0 + j, mc, f_grey); put(ws, qr, c0 + j, qc, f_grey)
        put(ws, hdr_r, c0 + j, name, label_font, fill=fill_hdr, align=CENTER, border=b_hdr)
    for rr in (yr, mr, qr): ws.row_dimensions[rr].hidden = True
    return yr, mr, qr

# =====================================================================
# SUMMARY
# =====================================================================
ws = wb.create_sheet('Summary'); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 90
put(ws, 1, 1, 'TWIN — two-layer GP overview (TDC + TWIN) · THB million / THB per kg' + EXNOTE, f_title)
put(ws, 2, 1, 'Every figure is a SUMIFS formula over the Data sheet · units: THB million / THB per kg · section colours: blue = Reported (actual monthly rates), green = Constant FX (base rates in Assumptions!B5:B6), yellow = FX impact · hidden rows 4–6 hold the SUMIFS criteria', f_sub)
pers = PERIODS + QPER
HR = 7; C0 = 2
put(ws, HR, 1, 'THB million (unless stated)', f_hdr, fill=fill_hdr, border=b_hdr)
yr, mr, qr = crit_rows(ws, HR, C0, pers)
def cref(col, row): return f'{L(col)}${row}'
spec = [
 ('TWIN sales volume (tons)', 't', NUM0, True), ('   TDC-made products (tons)', 't_tdc', NUM0, False), ('   non-TDC products (tons)', 'DIFF:t-t_tdc', NUM0, False),
 ('TWIN layer (trading)', None, None, 'grp'),
 ('TWIN net sales', 'ns', NUM1, False), ('TWIN COGS', 'cogs', NUM1, False), ('TWIN GP', 'gp', NUM1, True), ('TWIN GM %', 'RATIO:gp/ns', PCT, False),
 ('TWIN GP THB/kg (all products)', 'KG:gp/t', NUM2, True),
 ('TDC layer (manufacturer) — TDC products only, allocated to TWIN sales', None, None, 'grp'),
 ('TDC net sales (transfer price)', 'tdc_ns', NUM1, False), ('TDC product cost (AF + F&I)', 'tdc_pcost', NUM1, False), ('TDC product GP', 'tdc_pgp', NUM1, True),
 ('Idle + PPA + Other adj', 'tdc_other', NUM1, False), ('TDC full GP', 'tdc_fgp', NUM1, True),
 ('TDC transfer price THB/kg', 'KG:tdc_ns/t_tdc', NUM2, False), ('TDC product GP THB/kg', 'KG:tdc_pgp/t_tdc', NUM2, True), ('TDC full GP THB/kg', 'KG:tdc_fgp/t_tdc', NUM2, True),
 ('Total chain (TWIN + TDC)', None, None, 'grp'),
 ('Total GP — product cost', 'chain_pgp', NUM1, True), ('Total GP — full cost', 'chain_fgp', NUM1, True),
 ('Total GP THB/kg — product cost', 'KG:chain_pgp/t', NUM2, True), ('Total GP THB/kg — full cost', 'KG:chain_fgp/t', NUM2, True),
 ('Constant FX (base rates in Assumptions)', None, None, 'grp'),
 ('TWIN GP @ constant FX', 'gp_c', NUM1, False), ('TDC net sales @ constant FX', 'tdc_ns_c', NUM1, False), ('TDC product GP @ constant FX', 'tdc_pgp_c', NUM1, False), ('TDC full GP @ constant FX', 'tdc_fgp_c', NUM1, False),
 ('Total GP product @ constant FX', 'chain_pgp_c', NUM1, False), ('Total GP full @ constant FX', 'chain_fgp_c', NUM1, True), ('Total GP full THB/kg @ constant FX', 'KG:chain_fgp_c/t', NUM2, True),
 ('FX impact = reported − constant (THB million)', None, None, 'grp'),
 ('① USD/THB — TDC layer', 'fx1', NUM1, False), ('② USD/IDR — TWIN purchase cost', 'fx2', NUM1, False), ('③ IDR/THB — translation of TWIN GP', 'fx3', NUM1, False), ('FX impact total', 'fxt', NUM1, True),
]
rowof = {}
r = HR + 1
for label, key, fmt, flag in spec:
    if flag == 'grp':
        gf = fill_con if label.startswith('Constant') else (fill_fx if label.startswith('FX') else fill_rep)
        put(ws, r, 1, label, f_bold, fill=gf)
        for j in range(len(pers)): put(ws, r, C0 + j, None, fill=gf)
        r += 1; continue
    put(ws, r, 1, label, f_bold if flag else f_norm); rowof[key] = r
    for j in range(len(pers)):
        c = C0 + j; yc, mc, qc = cref(c, yr), cref(c, mr), cref(c, qr)
        if key.startswith('DIFF:'):
            a, b = key[5:].split('-'); f = f'={L(c)}{rowof[a]}-{L(c)}{rowof[b]}'
        elif key.startswith('RATIO:'):
            a, b = key[6:].split('/'); f = f'=IF({L(c)}{rowof[b]}=0,"",{L(c)}{rowof[a]}/{L(c)}{rowof[b]})'
        elif key.startswith('KG:'):
            a, b = key[3:].split('/'); scale = '' if a in ('t', 't_tdc') else '*1000'  # MB row -> THB: MB*1e6 / (t*1000) = *1000
            f = f'=IF({L(c)}{rowof[b]}=0,"",{L(c)}{rowof[a]}*1000/{L(c)}{rowof[b]})'
        elif key in ('t', 't_tdc'):
            f = '=' + SUMIFS(key, yc, mc, qc)
        else:
            f = '=' + SUMIFS(key, yc, mc, qc) + '/1000000'
        put(ws, r, c, f, f_bold if flag else f_norm, fmt=fmt, border=b_left if j == 4 else None)
    r += 1
for key, rr in rowof.items():
    if key.startswith('KG:'): traffic(ws, f'{L(C0)}{rr}:{L(C0 + len(pers) - 1)}{rr}', 0, 2, 5)
# reconciliation vs TDC actual shipments (SUMIFS over Assumptions monthly table)
r += 1
put(ws, r, 1, 'Reconciliation: actual TDC shipments to TWIN (by invoice month) vs amounts allocated to TWIN sales', f_bold, fill=fill_grp)
for j in range(len(pers)): put(ws, r, C0 + j, None, fill=fill_grp)
r += 1
# need month_num criteria for monthly table: derive from month text -> use a helper: quarter/year columns exist (I, J); month_num not. Use SUMPRODUCT with VALUE(RIGHT(month,2))
def TDCSUM(col, c):
    yc, mc, qc = cref(c, yr), cref(c, mr), cref(c, qr)
    return (f'SUMPRODUCT(({TM("J")}={yc})*(VALUE(RIGHT({TM("H")},2))<=VALUE(MID({mc},3,2)))*(({qc}="*")+({TM("I")}={qc})>0)*{TM(col)})')
rec = [('Actual TDC shipments (tons)', lambda c: '=' + TDCSUM('M', c), NUM0),
       ('Actual TDC net sales', lambda c: '=' + TDCSUM('N', c) + '/1000000', NUM1),
       ('Actual TDC product GP (NS − AF − F&I)', lambda c: '=(' + TDCSUM('N', c) + '-' + TDCSUM('P', c) + '-' + TDCSUM('Q', c) + ')/1000000', NUM1),
       ('Actual TDC full GP', lambda c: '=(' + TDCSUM('N', c) + '-' + TDCSUM('P', c) + '-' + TDCSUM('Q', c) + '-' + TDCSUM('R', c) + '-' + TDCSUM('S', c) + '-' + TDCSUM('T', c) + ')/1000000', NUM1)]
for label, fn, fmt in rec:
    put(ws, r, 1, label)
    for j in range(len(pers)): put(ws, r, C0 + j, fn(C0 + j), fmt=fmt, border=b_left if j == 4 else None)
    r += 1
put(ws, r, 1, 'Difference = stock timing (TDC ships in one month, TWIN sells in another)', f_grey)
vlines(ws, year_start_cols(C0, pers) + [C0 + len(pers)], HR, r - 1)
widths(ws, {'A': 52})
for c in range(C0, C0 + len(pers)): ws.column_dimensions[L(c)].width = 11
ws.freeze_panes = f'B{HR + 1}'
SUMROW = rowof  # for Key findings refs

vol26 = defaultdict(float); vol25 = defaultdict(float); info = {}
for x in rows:
    info[x['label']] = x
    if x['y'] == '2026': vol26[x['label']] += x['t']; vol26[(x['label'], x['prod'])] += x['t']
    if x['y'] == '2025': vol25[x['label']] += x['t']; vol25[(x['label'], x['prod'])] += x['t']
custs = sorted(set(x['label'] for x in rows), key=lambda c: (-vol26[c], -vol25[c]))
# =====================================================================
# REPORTED vs CONSTANT FX
# =====================================================================
ws = wb.create_sheet('Reported vs Constant'); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 90
put(ws, 1, 1, 'Reported GP vs Constant-FX GP — every GP level side by side (THB million and THB per kg)' + EXNOTE, f_title)
put(ws, 2, 1, 'Reported = THB at the actual rate of each month · Constant = all currency pairs held at the base rates in Assumptions!B5:B6 · FX impact = Reported − Constant (negative = FX lowered profit) · SUMIFS formulas over Data', f_sub)
LEVELS = [('TWIN GP', 'gp', 'gp_c', 't'), ('TDC GP — product cost', 'tdc_pgp', 'tdc_pgp_c', 't_tdc'), ('TDC GP — full cost', 'tdc_fgp', 'tdc_fgp_c', 't_tdc'),
          ('Total GP — product cost', 'chain_pgp', 'chain_pgp_c', 't'), ('Total GP — full cost', 'chain_fgp', 'chain_fgp_c', 't')]
pers = PERIODS + QPER
HR = 7; C0 = 3
yr, mr, qr = crit_rows(ws, HR, C0, pers)
put(ws, HR, 1, 'GP level', f_hdr, fill=fill_hdr, border=b_hdr); put(ws, HR, 2, 'View', f_hdr, fill=fill_hdr, border=b_hdr)
r = HR + 1
put(ws, r, 1, 'A. THB million', f_sec); r += 1
tons_row = r
put(ws, r, 1, 'Volume (tons)', f_bold); put(ws, r, 2, 'all', f_grey)
for j in range(len(pers)):
    c = C0 + j; put(ws, r, c, '=' + SUMIFS('t', cref(c, yr), cref(c, mr), cref(c, qr)), f_bold, fmt=NUM0, border=b_left if j == 4 else None)
r += 1; tons_tdc_row = r
put(ws, r, 1, 'TDC product volume (tons)', f_norm); put(ws, r, 2, 'TDC only', f_grey)
for j in range(len(pers)):
    c = C0 + j; put(ws, r, c, '=' + SUMIFS('t_tdc', cref(c, yr), cref(c, mr), cref(c, qr)), fmt=NUM0, border=b_left if j == 4 else None)
r += 1
mb_rows = {}
for label, krep, kcon, _ in LEVELS:
    rr, rc, rf = r, r + 1, r + 2
    put(ws, rr, 1, label, f_bold); put(ws, rr, 2, 'Reported', f_bold, fill=fill_rep); put(ws, rc, 2, 'Constant FX', fill=fill_con); put(ws, rf, 2, 'FX impact', f_grey, fill=fill_fx)
    for j in range(len(pers)):
        c = C0 + j; yc, mc, qc = cref(c, yr), cref(c, mr), cref(c, qr)
        put(ws, rr, c, '=' + SUMIFS(krep, yc, mc, qc) + '/1000000', f_bold, fmt=NUM2, border=b_left if j == 4 else None)
        put(ws, rc, c, '=' + SUMIFS(kcon, yc, mc, qc) + '/1000000', fmt=NUM2, border=b_left if j == 4 else None)
        put(ws, rf, c, f'={L(c)}{rr}-{L(c)}{rc}', f_grey, fmt=NUM2, border=b_left if j == 4 else None)
    for c in range(1, C0 + len(pers)): ws.cell(row=rf, column=c).border = Border(bottom=thin, left=thin if (c - C0) == 4 else None)
    mb_rows[label] = (rr, rc, rf); r += 3
r += 1
put(ws, r, 1, 'B. THB per kg (TDC levels divided by TDC-product tons, others by total tons)', f_sec); r += 1
for label, krep, kcon, tkey in LEVELS:
    rr, rc, rf = r, r + 1, r + 2
    trow = tons_tdc_row if tkey == 't_tdc' else tons_row
    put(ws, rr, 1, label, f_bold); put(ws, rr, 2, 'Reported', f_bold, fill=fill_rep); put(ws, rc, 2, 'Constant FX', fill=fill_con); put(ws, rf, 2, 'FX impact', f_grey, fill=fill_fx)
    mrr, mrc, _ = mb_rows[label]
    for j in range(len(pers)):
        c = C0 + j; cl = L(c)
        put(ws, rr, c, f'=IF({cl}{trow}=0,"",{cl}{mrr}*1000/{cl}{trow})', f_bold, fmt=NUM2, border=b_left if j == 4 else None)
        put(ws, rc, c, f'=IF({cl}{trow}=0,"",{cl}{mrc}*1000/{cl}{trow})', fmt=NUM2, border=b_left if j == 4 else None)
        put(ws, rf, c, f'=IF({cl}{trow}=0,"",{cl}{rr}-{cl}{rc})', f_grey, fmt=NUM2, border=b_left if j == 4 else None)
    for c in range(1, C0 + len(pers)): ws.cell(row=rf, column=c).border = Border(bottom=thin, left=thin if (c - C0) == 4 else None)
    traffic(ws, f'{L(C0)}{rr}:{L(C0 + len(pers) - 1)}{rc}', 0, 2, 5)
    r += 3
r += 1
put(ws, r, 1, 'C. By customer — Reported vs Constant (TWIN GP · TDC full GP · Total GP full cost) · YTD Sep-25 vs YTD Sep-26 · sorted by YTD26 tons', f_sec); r += 1
cm = [('Tons', 't', NUM0), ('TWIN GP Rep MB', 'gp', NUM2), ('TWIN GP Const MB', 'gp_c', NUM2), ('TDC full GP Rep MB', 'tdc_fgp', NUM2), ('TDC full GP Const MB', 'tdc_fgp_c', NUM2),
      ('Total full GP Rep MB', 'chain_fgp', NUM2), ('Total full GP Const MB', 'chain_fgp_c', NUM2), ('FX impact MB', 'DIFF', NUM2),
      ('Total full Rep THB/kg', 'KG:chain_fgp', NUM2), ('Total full Const THB/kg', 'KG:chain_fgp_c', NUM2), ('FX impact THB/kg', 'KGDIFF', NUM2)]
ncm = len(cm); HR2 = r + 4; c0 = 2
yr2, mr2, qr2 = HR2 - 3, HR2 - 2, HR2 - 1
for rr_ in (yr2, mr2, qr2): ws.row_dimensions[rr_].hidden = True
put(ws, HR2, 1, 'Customer', f_hdr, fill=fill_hdr, border=b_hdr)
for pi, (name, y, mc, qc) in enumerate([PERIODS[2], PERIODS[3]]):
    cc = c0 + pi * ncm
    put(ws, HR2 - 4, cc, name, f_bold, fill=fill_grp, align=CENTER); ws.merge_cells(start_row=HR2 - 4, start_column=cc, end_row=HR2 - 4, end_column=cc + ncm - 1)
    for mi, (h, _, _) in enumerate(cm):
        put(ws, yr2, cc + mi, y, f_grey); put(ws, mr2, cc + mi, mc, f_grey); put(ws, qr2, cc + mi, qc, f_grey)
        hf = fill_rep if 'Rep' in h else (fill_con if 'Const' in h else (fill_fx if 'FX' in h else fill_hdr))
        put(ws, HR2, cc + mi, h, f_hdr, fill=hf, align=CENTER, border=Border(bottom=med, left=thin if mi in (0, 1, 3, 5, 7, 8, 10) else None))
ws.row_dimensions[HR2].height = 40
def cust_row2(r, label, bold=False, allc=False):
    put(ws, r, 1, label, f_bold if bold else f_norm, fill=fill_tot if bold else None)
    ex = '' if allc else f',{D("E")},$A{r}'
    for pi in range(2):
        cc = c0 + pi * ncm
        for mi, (h, key, fmt) in enumerate(cm):
            c = cc + mi; yc, mc, qc = cref(c, yr2), cref(c, mr2), cref(c, qr2)
            if key == 't': f = '=' + SUMIFS('t', yc, mc, qc, ex)
            elif key == 'DIFF': f = f'={L(cc + 5)}{r}-{L(cc + 6)}{r}'
            elif key == 'KGDIFF': f = f'=IF({L(cc)}{r}=0,"",{L(cc + 8)}{r}-{L(cc + 9)}{r})'
            elif key.startswith('KG:'):
                src = cc + 5 if key == 'KG:chain_fgp' else cc + 6
                f = f'=IF({L(cc)}{r}=0,"",{L(src)}{r}*1000/{L(cc)}{r})'
            else: f = '=' + SUMIFS(key, yc, mc, qc, ex) + '/1000000'
            put(ws, r, c, f, f_bold if bold else f_norm, fmt=fmt, fill=fill_tot if bold else None, border=b_left if mi in (0, 1, 3, 5, 7, 8, 10) else None)
r = HR2 + 1
cust_row2(r, 'All customers', bold=True, allc=True); r += 1; first2 = r
for cst in custs: cust_row2(r, cst); r += 1
for pi in range(2):
    for mi in (8, 9):
        c = c0 + pi * ncm + mi; traffic(ws, f'{L(c)}{first2 - 1}:{L(c)}{r - 1}', 0, 2, 5)
vlines(ws, year_start_cols(C0, pers) + [C0 + len(pers)], HR, HR2 - 6)
vlines(ws, [c0, c0 + ncm, c0 + 2 * ncm], HR2 - 4, r - 1)
widths(ws, {'A': 40, 'B': 12})
for c in range(3, 3 + max(len(pers), 2 * ncm)): ws.column_dimensions[L(c)].width = 10.5
ws.freeze_panes = f'C{HR + 1}'

# =====================================================================
# BY CUSTOMER / BY CUSTOMER-PRODUCT
# =====================================================================
def dim_sheet(title, dims, labels, infos=(), tag_rows=None):
    """dims: list of (header, data_col) criteria columns; labels: ordered tuples of criteria values;
    infos: list of (header, fn(label_tuple)) static description columns (currency, country, ...).
    Per period: volume block, Reported block, Constant-FX block (same metrics), FX impact. Header = period / FX basis / unit / GP level."""
    ws = wb.create_sheet(title); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 85
    put(ws, 1, 1, f'{title} — volume / GP / GP per kg · Reported vs Constant FX' + EXNOTE, f_title)
    put(ws, 2, 1, 'All figures in Thai baht (THB) · Reported = translated at the actual rate of each month · Constant FX = all currency pairs held at the base rates (Assumptions!B5:B6) · FX impact = Reported − Constant · TDC THB/kg uses TDC-product tons, TWIN/Total use total tons · traffic light: red <0, amber 0–2, green ≥5 THB/kg', f_sub)
    GP = [('TWIN GP', 'gp', 'gp_c', 't'), ('TDC GP product cost', 'tdc_pgp', 'tdc_pgp_c', 't_tdc'), ('TDC GP full cost', 'tdc_fgp', 'tdc_fgp_c', 't_tdc'),
          ('Total GP product cost', 'chain_pgp', 'chain_pgp_c', 't'), ('Total GP full cost', 'chain_fgp', 'chain_fgp_c', 't')]
    # (header, key, fmt, block, unit)
    metrics = [('Sales volume', 't', NUM0, 'vol', 'tons'), ('TDC product volume', 't_tdc', NUM0, 'vol', 'tons'), ('TWIN net sales (Reported)', 'ns', NUM1, 'vol', 'THB million')]
    metrics += [(h, k, NUM1, 'Reported', 'THB million') for h, k, _, _ in GP] + [(h, f'KG:{k}/{tk}', NUM2, 'Reported', 'THB per kg') for h, k, _, tk in GP]
    metrics += [(h, k2, NUM1, 'Constant FX', 'THB million') for h, _, k2, _ in GP] + [(h, f'KG:{k2}/{tk}', NUM2, 'Constant FX', 'THB per kg') for h, _, k2, tk in GP]
    metrics += [('Total GP product cost', 'DIFF:chain_pgp-chain_pgp_c', NUM1, 'FX', 'THB million'), ('Total GP full cost', 'DIFF:chain_fgp-chain_fgp_c', NUM1, 'FX', 'THB million'),
               ('Total GP product cost', 'DIFF:KG:chain_pgp/t-KG:chain_pgp_c/t', NUM2, 'FX', 'THB per kg'), ('Total GP full cost', 'DIFF:KG:chain_fgp/t-KG:chain_fgp_c/t', NUM2, 'FX', 'THB per kg')]
    keys = [m[1] for m in metrics]
    def ent_of(h): return 'vol' if 'volume' in h or 'net sales' in h else ('TWIN' if h.startswith('TWIN') else ('TDC' if h.startswith('TDC') else ('Total' if h.startswith('Total') else 'vol')))
    def sep_left(mi):
        # thin line when block, unit or entity changes (entity = TWIN / TDC / Total)
        if mi == 0: return True
        a, b = metrics[mi - 1], metrics[mi]
        return a[3] != b[3] or a[4] != b[4] or ent_of(a[0]) != ent_of(b[0])
    nd = len(dims); ni = len(infos); HR = 10; c0 = nd + ni + 1
    yr, mr, qr = HR - 3, HR - 2, HR - 1
    for rr in (yr, mr, qr): ws.row_dimensions[rr].hidden = True
    for j, (h, _) in enumerate(dims): put(ws, HR, 1 + j, h, f_hdr, fill=fill_hdr, border=b_hdr)
    for j, (h, _) in enumerate(infos): put(ws, HR, 1 + nd + j, h, f_hdr, fill=fill_hdr, border=b_hdr, align=CENTER)
    put(ws, HR - 6, 1, 'Period →', f_grey); put(ws, HR - 5, 1, 'FX basis →', f_grey); put(ws, HR - 4, 1, 'Unit →', f_grey)
    nm = len(metrics)
    BLK = {'vol': ('Volume / sales', 'F2F2F2'), 'Reported': ('REPORTED — THB at actual monthly rates', 'DDEBF7'), 'Constant FX': ('CONSTANT FX — THB at base rates (Assumptions B5:B6)', 'E2EFDA'), 'FX': ('FX IMPACT = Reported − Constant', 'FFF2CC')}
    def spans(level):
        out = []; mi = 0
        while mi < nm:
            v = metrics[mi][level]; mj = mi
            while mj < nm and metrics[mj][level] == v and (level == 3 or metrics[mj][3] == metrics[mi][3]): mj += 1
            out.append((mi, mj, v)); mi = mj
        return out
    for pi, (name, y, mc, qc) in enumerate(PERIODS):
        cc = c0 + pi * nm
        put(ws, HR - 6, cc, name, Font(name=F, size=10, bold=True), fill=fill_grp, align=CENTER, border=Border(left=thin))
        ws.merge_cells(start_row=HR - 6, start_column=cc, end_row=HR - 6, end_column=cc + nm - 1)
        for mi, mj, blk in spans(3):
            lab, col = BLK[blk]
            put(ws, HR - 5, cc + mi, lab, f_hdr, fill=PatternFill('solid', fgColor=col), align=CENTER, border=Border(left=thin))
            if mj - mi > 1: ws.merge_cells(start_row=HR - 5, start_column=cc + mi, end_row=HR - 5, end_column=cc + mj - 1)
        for mi, mj, unit in spans(4):
            put(ws, HR - 4, cc + mi, unit, f_bold, fill=fill_hdr, align=CENTER, border=Border(left=thin, bottom=thin))
            if mj - mi > 1: ws.merge_cells(start_row=HR - 4, start_column=cc + mi, end_row=HR - 4, end_column=cc + mj - 1)
            for k2 in range(mi + 1, mj):
                if sep_left(k2): ws.cell(row=HR - 4, column=cc + k2).border = Border(left=thin, bottom=thin)
        for mi, (h, _, _, blk, unit) in enumerate(metrics):
            put(ws, yr, cc + mi, y, f_grey); put(ws, mr, cc + mi, mc, f_grey); put(ws, qr, cc + mi, qc, f_grey)
            put(ws, HR, cc + mi, h, f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med, left=thin if sep_left(mi) else None))
    ws.row_dimensions[HR].height = 42; ws.row_dimensions[HR - 5].height = 28
    def kgf(key, cc, r):
        a_, b_ = key[3:].split('/'); ca = cc + keys.index(a_); cb = cc + keys.index(b_)
        return f'IF({L(cb)}{r}=0,"",{L(ca)}{r}*1000/{L(cb)}{r})'
    def write_row(r, dimvals, bold=False, extra_crit=True):
        for j, v in enumerate(dimvals): put(ws, r, 1 + j, v, f_bold if bold else f_norm, fill=fill_tot if bold else None)
        for j, (_, fn) in enumerate(infos):
            v = fn(tuple(dimvals)) if extra_crit else ''
            if isinstance(v, str) and v.startswith('FML:'): v = v[4:].format(r=r)
            put(ws, r, 1 + nd + j, v, f_grey, fill=fill_tot if bold else None, align=Alignment(horizontal='center'))
        for pi in range(len(PERIODS)):
            cc = c0 + pi * nm
            for mi, (h, key, fmt, blk, unit) in enumerate(metrics):
                c = cc + mi; yc, mc, qc = cref(c, yr), cref(c, mr), cref(c, qr)
                extra = ''.join(f',{D(dc)},${L(1 + j)}{r}' for j, (_, dc) in enumerate(dims)) if extra_crit else ''
                if key.startswith('DIFF:KG:'):
                    a_, b_ = key[5:].split('-KG:'); b_ = 'KG:' + b_
                    ca = cc + keys.index(a_); cb = cc + keys.index(b_)
                    f = f'=IF(OR({L(ca)}{r}="",{L(cb)}{r}=""),"",{L(ca)}{r}-{L(cb)}{r})'
                elif key.startswith('DIFF:'):
                    a_, b_ = key[5:].split('-'); f = f'={L(cc + keys.index(a_))}{r}-{L(cc + keys.index(b_))}{r}'
                elif key.startswith('KG:'): f = '=' + kgf(key, cc, r)
                elif key in ('t', 't_tdc'): f = '=' + SUMIFS(key, yc, mc, qc, extra)
                else: f = '=' + SUMIFS(key, yc, mc, qc, extra) + '/1000000'
                put(ws, r, c, f, f_bold if bold else f_norm, fmt=fmt, fill=fill_tot if bold else None, border=Border(left=thin if sep_left(mi) else None))
    r = HR + 1
    write_row(r, ['Total'] + [''] * (nd - 1), bold=True, extra_crit=False); r += 1
    first = r
    for lab in labels: write_row(r, list(lab)); r += 1
    last = r - 1
    if tag_rows:
        # subtotal rows by Country / tag (Data column H) below the customer table — Por's request 26-Oct-2026 (rows 76+)
        r += 1
        put(ws, r, 1, 'Subtotal by Country / tag (Data col H) — SUMIFS on the tag, edit tags in Data!H', f_sec); r += 1
        tag_first = r
        for tg in tag_rows:
            put(ws, r, 1, tg, f_bold, fill=fill_tot)
            for j in range(ni): put(ws, r, 1 + nd + j, 'tag' if j == 1 else '', f_grey, fill=fill_tot, align=Alignment(horizontal='center'))
            for pi in range(len(PERIODS)):
                cc = c0 + pi * nm
                for mi, (h, key, fmt, blk, unit) in enumerate(metrics):
                    c = cc + mi; yc, mc, qc = cref(c, yr), cref(c, mr), cref(c, qr)
                    extra = f',{D("H")},$A{r}'
                    if key.startswith('DIFF:KG:'):
                        a_, b_ = key[5:].split('-KG:'); b_ = 'KG:' + b_
                        ca = cc + keys.index(a_); cb = cc + keys.index(b_)
                        f = f'=IF(OR({L(ca)}{r}="",{L(cb)}{r}=""),"",{L(ca)}{r}-{L(cb)}{r})'
                    elif key.startswith('DIFF:'):
                        a_, b_ = key[5:].split('-'); f = f'={L(cc + keys.index(a_))}{r}-{L(cc + keys.index(b_))}{r}'
                    elif key.startswith('KG:'): f = '=' + kgf(key, cc, r)
                    elif key in ('t', 't_tdc'): f = '=' + SUMIFS(key, yc, mc, qc, extra)
                    else: f = '=' + SUMIFS(key, yc, mc, qc, extra) + '/1000000'
                    put(ws, r, c, f, f_bold, fmt=fmt, fill=fill_tot, border=Border(left=thin if sep_left(mi) else None))
            r += 1
        put(ws, r, 1, 'Check: sum of tags = Total', f_grey)
        for pi in range(len(PERIODS)):
            cc = c0 + pi * nm
            for mi, (h, key, fmt, blk, unit) in enumerate(metrics):
                if key in ('t', 't_tdc') or not (key.startswith('KG:') or key.startswith('DIFF:KG:')):
                    c = cc + mi; put(ws, r, c, f'=SUM({L(c)}{tag_first}:{L(c)}{r - 1})-{L(c)}{HR + 1}', f_grey, fmt=fmt)
        for pi in range(len(PERIODS)):
            for mi, (h, key, fmt, blk, unit) in enumerate(metrics):
                if key.startswith('KG:'): c = c0 + pi * nm + mi; traffic(ws, f'{L(c)}{tag_first}:{L(c)}{r - 1}', 0, 2, 5)
        r += 1
    for pi in range(len(PERIODS)):
        for mi, (h, key, fmt, blk, unit) in enumerate(metrics):
            if key.startswith('KG:'): c = c0 + pi * nm + mi; traffic(ws, f'{L(c)}{first - 1}:{L(c)}{last}', 0, 2, 5)
    widths(ws, {'A': 40})
    for j in range(1, nd): ws.column_dimensions[L(1 + j)].width = 16
    for j in range(ni): ws.column_dimensions[L(1 + nd + j)].width = 12
    for c in range(c0, c0 + len(PERIODS) * nm): ws.column_dimensions[L(c)].width = 9.5
    for pi in range(len(PERIODS)):
        cc = c0 + pi * nm
        ws.column_dimensions.group(L(cc + 13), L(cc + nm - 1), hidden=False, outline_level=1)
    ws.freeze_panes = ws.cell(row=HR + 1, column=c0); ws.auto_filter.ref = f'A{HR}:{L(c0 + len(PERIODS) * nm - 1)}{last}'
cinfo = {}
for x in rows:
    d = cinfo.setdefault(x['label'], {'group': set(), 'country': set(), 'cur': set()})
    d['group'].add(x['group']); d['country'].add(x['country']); d['cur'].add(x['cur'])
# info columns are live formulas from Data (edit Data -> these follow); FML: prefix marks a formula template with {r}
INFOS = [('TWIN sale currency (Data col I)', lambda k: 'FML:=IFERROR(INDEX(' + D('I') + ',MATCH($A{r},' + D('E') + ',0)),"")'),
         ('Country / tag (Data col H)', lambda k: 'FML:=IFERROR(INDEX(' + D('H') + ',MATCH($A{r},' + D('E') + ',0)),"")'),
         ('Customer group (Data col G)', lambda k: 'FML:=IFERROR(INDEX(' + D('G') + ',MATCH($A{r},' + D('E') + ',0)),"")')]
ctry = sorted(set(x['country'] for x in rows), key=lambda c: -sum(x['t'] for x in rows if x['country'] == c and x['y'] == '2026'))
dim_sheet('By customer', [('Customer', 'E')], [(c,) for c in custs], INFOS, tag_rows=ctry)
# By country / tag — uses whatever Por types in Data column H (country or group tag such as Heinz / Wings)
ctry = sorted(set(x['country'] for x in rows), key=lambda c: -sum(x['t'] for x in rows if x['country'] == c and x['y'] == '2026'))
dim_sheet('By country-tag', [('Country / tag (Data col H)', 'H')], [(c,) for c in ctry], [])
cps = sorted(set((x['label'], x['prod']) for x in rows), key=lambda k: (-vol26[k], -vol25[k]))
pinfo = {}
for x in rows: pinfo[(x['label'], x['prod'])] = (x['src'], x['sn'])
INFOS_P = [('TWIN sale currency (Data col I)', lambda k: 'FML:=IFERROR(INDEX(' + D('I') + ',MATCH($A{r},' + D('E') + ',0)),"")'),
           ('Source', lambda k: pinfo[tuple(k)][0] + (' ' + pinfo[tuple(k)][1] if pinfo[tuple(k)][1] else ''))]
dim_sheet('By customer-product', [('Customer', 'E'), ('Product', 'J')], cps, INFOS_P)

# =====================================================================
# QUARTERLY TREND
# =====================================================================
ws = wb.create_sheet('Quarterly trend'); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 85
put(ws, 1, 1, "Quarterly trend by customer — Q1'24 → Q3'26" + EXNOTE, f_title)
put(ws, 2, 1, 'SUMIFS formulas over Data · customers sorted by YTD Sep-26 volume · one block per metric', f_sub)
blocks = [('Sales volume (tons)', 't', NUM0), ('TWIN GP (THB million)', 'gp', NUM2), ('TWIN GP THB/kg', 'KG:gp/t', NUM2),
          ('TDC product GP THB/kg (TDC products only)', 'KG:tdc_pgp/t_tdc', NUM2), ('TDC full GP THB/kg (TDC products only)', 'KG:tdc_fgp/t_tdc', NUM2),
          ('Total GP full THB/kg', 'KG:chain_fgp/t', NUM2), ('Total GP full (THB million)', 'chain_fgp', NUM2), ('Total GP full THB/kg @ constant FX', 'KG:chain_fgp_c/t', NUM2)]
r = 4
put(ws, r, 1, 'crit: quarter', f_grey)
for j, qq in enumerate(QS): put(ws, r, 2 + j, qq, f_grey)
ws.row_dimensions[r].hidden = True; QROW = r; r += 1
for title, key, fmt in blocks:
    bf = fill_con if 'constant' in title else fill_rep
    put(ws, r, 1, title, f_bold, fill=bf)
    for j, qq in enumerate(QS): put(ws, r, 2 + j, qlabel(qq), f_hdr, fill=bf, align=CENTER)
    r += 1
    def qf(key, c, rr, cust=None):
        qc = f'{L(c)}${QROW}'; extra = f',{D("E")},$A{rr}' if cust else ''
        if key.startswith('KG:'):
            a, b = key[3:].split('/')
            num = SUMIFS(a, '"*"', '"<=12"', qc, extra); den = SUMIFS(b, '"*"', '"<=12"', qc, extra)
            return f'=IF({den}=0,"",{num}/({den}*1000))'
        f = SUMIFS(key, '"*"', '"<=12"', qc, extra)
        return '=' + f if key in ('t', 't_tdc') else '=' + f + '/1000000'
    put(ws, r, 1, 'Total', f_bold, fill=fill_tot)
    for j in range(len(QS)): put(ws, r, 2 + j, qf(key, 2 + j, r), f_bold, fmt=fmt, fill=fill_tot)
    r += 1; first = r
    for cst in custs:
        put(ws, r, 1, cst)
        for j in range(len(QS)): put(ws, r, 2 + j, qf(key, 2 + j, r, cust=True), fmt=fmt)
        r += 1
    if key.startswith('KG:'): traffic(ws, f'B{first - 1}:{L(1 + len(QS))}{r - 1}', 0, 2, 5)
    r += 1
vlines(ws, [2 + j for j, qq in enumerate(QS) if qq.endswith('Q1')] + [2 + len(QS)], 5, r - 1)
widths(ws, {'A': 40})
for c in range(2, 2 + len(QS)): ws.column_dimensions[L(c)].width = 8.5
ws.freeze_panes = 'B5'

# =====================================================================
# TDC PRODUCT RATES (from Assumptions rate table, Q keys) + TWIN resale
# =====================================================================
ws = wb.create_sheet('TDC product rates'); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 85
put(ws, 1, 1, 'TDC products sold through TWIN — price / cost / GP per kg by quarter (TDC = actual shipments from Assumptions · TWIN = actual sales from Data)', f_title)
put(ws, 2, 1, 'TDC transfer = price TDC charges TWIN (USD translated at the invoice rate) · TWIN ASP = selling price to customers · TWIN GP/kg = ASP − landed COGS', f_sub)
hdrs = ['Product (TWIN name)', 'SN', 'Quarter', 'key', 'TDC shipped (tons)', 'TDC transfer USD/kg', 'TDC transfer THB/kg', 'TDC product cost THB/kg', 'TDC product GP THB/kg',
        'Idle+PPA+adj THB/kg', 'TDC full GP THB/kg', 'TWIN sold (tons)', 'TWIN ASP THB/kg', 'TWIN COGS THB/kg', 'TWIN GP THB/kg', 'Total full GP THB/kg']
for j, h in enumerate(hdrs): put(ws, 4, 1 + j, h, f_hdr, fill=fill_hdr, align=CENTER, border=b_hdr)
ws.row_dimensions[4].height = 40
r = 5
for sn in sns:
    for qq in QS:
        key = f'{sn}|{qq}'
        put(ws, r, 1, M['sn_name'].get(sn, sn)); put(ws, r, 2, sn, f_grey); put(ws, r, 3, qlabel(qq), align=CENTER); put(ws, r, 4, key, f_grey)
        mt = f'MATCH($D{r},{RK_KEY},0)'
        for j, col in enumerate(['AA', 'AJ', 'AI', 'AK', 'AM', 'AL', 'AN']):
            put(ws, r, 5 + j, f'=INDEX({RK(col)},{mt})', fmt=(NUM0 if j == 0 else ('0.0000' if j == 1 else NUM2)))
        ex = f',{D("L")},$B{r}'
        tt = SUMIFS('t', '"*"', '"<=12"', f'"{qq}"', ex)
        put(ws, r, 12, '=' + tt, fmt=NUM0, border=b_left)
        put(ws, r, 13, f'=IF(L{r}=0,"",{SUMIFS("ns", chr(34)+"*"+chr(34), chr(34)+"<=12"+chr(34), chr(34)+qq+chr(34), ex)}/(L{r}*1000))', fmt=NUM2)
        put(ws, r, 14, f'=IF(L{r}=0,"",{SUMIFS("cogs", chr(34)+"*"+chr(34), chr(34)+"<=12"+chr(34), chr(34)+qq+chr(34), ex)}/(L{r}*1000))', fmt=NUM2)
        put(ws, r, 15, f'=IF(L{r}=0,"",M{r}-N{r})', fmt=NUM2)
        put(ws, r, 16, f'=IF(L{r}=0,"",O{r}+K{r})', fmt=NUM2)
        if qq.endswith('Q1') and qq != QS[0]: hlines(ws, [r], 1, 16, thin)
        r += 1
    r += 1
traffic(ws, f'I5:I{r}', 0, 2, 5); traffic(ws, f'K5:K{r}', 0, 2, 5); traffic(ws, f'O5:O{r}', 0, 2, 5); traffic(ws, f'P5:P{r}', 0, 2, 5)
widths(ws, {'A': 18, 'B': 8, 'C': 8, 'D': 14})
for c in range(5, 17): ws.column_dimensions[L(c)].width = 11
ws.freeze_panes = 'E5'

# =====================================================================
# FX (monthly, formulas)
# =====================================================================
ws = wb.create_sheet('FX'); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 90
put(ws, 1, 1, 'FX — monthly exchange rates and FX impact split into 3 parts (THB million, reported − constant FX) · all formulas', f_title)
put(ws, 2, 1, 'Base rates in Assumptions!B5:B7 · negative = FX made THB profit lower than at constant rates', f_sub)
hdrs = ['Month', 'USD/THB', 'IDR/THB', 'USD/IDR', '', 'TWIN sold (tons)', '① USD/THB TDC layer', '② USD/IDR TWIN cost', '③ IDR/THB TWIN translation', 'FX total', '',
        'TDC NS reported', 'TDC NS @const', 'TWIN GP reported', 'TWIN GP @const', 'Total full GP reported', 'Total full GP @const']
for j, h in enumerate(hdrs): put(ws, 4, 1 + j, h, f_hdr, fill=fill_hdr, align=CENTER, border=b_hdr)
ws.row_dimensions[4].height = 40
r = 5
for m in months:
    put(ws, r, 1, m)
    if m.endswith('-01') and m != months[0]: hlines(ws, [r], 1, 17, thin)
    put(ws, r, 2, f'=INDEX({FX_U},MATCH($A{r},{FX_M},0))', fmt='0.00'); put(ws, r, 3, f'=INDEX({FX_I},MATCH($A{r},{FX_M},0))', fmt='0.000000'); put(ws, r, 4, f'=B{r}/C{r}', fmt='#,##0')
    def ms(meas): return f'SUMIFS({D(MEAS[meas])},{D("A")},$A{r})'
    put(ws, r, 6, '=' + ms('t'), fmt=NUM0)
    for j, meas in enumerate(['fx1', 'fx2', 'fx3', 'fxt']): put(ws, r, 7 + j, '=' + ms(meas) + '/1000000', fmt=NUM2)
    for j, meas in enumerate(['tdc_ns', 'tdc_ns_c', 'gp', 'gp_c', 'chain_fgp', 'chain_fgp_c']): put(ws, r, 12 + j, '=' + ms(meas) + '/1000000', fmt=NUM1)
    r += 1
r += 1
put(ws, r, 1, 'Quarterly / annual summary (linked to Summary sheet)', f_bold, fill=fill_grp)
for j in range(1, len(hdrs)): put(ws, r, 1 + j, None, fill=fill_grp)
r += 1
for pi, (name, y, mc, qc) in enumerate(QPER + PERIODS):
    sc = L(C0 + (len(PERIODS) + pi if pi < len(QPER) else pi - len(QPER)))
    bold = name.startswith(('FY', 'YTD'))
    if name.startswith("Q1'") or name == 'FY2024': hlines(ws, [r], 1, 17, thin)
    put(ws, r, 1, name, f_bold if bold else f_norm, fill=fill_tot if bold else None)
    put(ws, r, 6, f'=Summary!{sc}{SUMROW["t"]}', fmt=NUM0)
    for j, key in enumerate(['fx1', 'fx2', 'fx3', 'fxt']): put(ws, r, 7 + j, f'=Summary!{sc}{SUMROW[key]}', f_bold if bold else f_norm, fmt=NUM2)
    for j, key in enumerate(['tdc_ns', 'tdc_ns_c', 'gp', 'gp_c', 'chain_fgp', 'chain_fgp_c']):
        put(ws, r, 12 + j, f'=Summary!{sc}{SUMROW[key]}' if key in SUMROW else None, f_bold if bold else f_norm, fmt=NUM1)
    r += 1
r += 1
for n in ['Method (see formulas in the Data sheet)',
          '① TDC layer: fx1 = tdc_ns_thb − tdc_ns_usd × Base USD/THB  (TDC cost is in THB, unchanged)',
          '② TWIN cost layer: fx2 = (actual GP IDR − GP IDR if USD/IDR = base) × IDR/THB of the month, where base GP IDR = NS IDR − COGS USD × Base USD/IDR',
          '③ TWIN translation layer: fx3 = base GP IDR × (IDR/THB of the month − Base IDR/THB)',
          'Check: fx2 + fx3 = TWIN GP reported − TWIN GP @const always (algebraic identity)']:
    put(ws, r, 1, n, f_bold if n.startswith('Method') else f_grey); r += 1
widths(ws, {'A': 11, 'B': 9, 'C': 10, 'D': 9, 'E': 2, 'F': 10, 'G': 11, 'H': 11, 'I': 12, 'J': 9, 'K': 2, 'L': 10, 'M': 10, 'N': 10, 'O': 10, 'P': 11, 'Q': 11})
ws.freeze_panes = 'B5'

# =====================================================================
# KEY FINDINGS (formula tables)
# =====================================================================
ws = wb.create_sheet('Key findings', 0); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 90
put(ws, 1, 1, 'TWIN (Indonesia) — two-layer customer profitability (TDC manufacturer + TWIN trading): Key findings' + EXNOTE, f_title)
put(ws, 2, 1, 'Units: THB / THB per kg · data Jan-24 → Sep-26 · tables are formulas linked to Summary/Data · constant-FX base rates editable in Assumptions!B5:B6', f_sub)
r = 4
put(ws, r, 1, '1. Five GP levels — TWIN GP · TDC GP (product cost) · TDC GP (full cost) · Total GP (product cost) · Total GP (full cost)   [colours: blue Reported · green Constant FX · yellow FX impact]', f_sec); r += 1
put(ws, r, 1, 'Definitions: TDC product cost = Actual Cost (AF) + F&I · TDC full cost = product cost + Idle + PPA + Other adj · Total = TWIN GP + TDC GP · TDC THB/kg uses TDC-product tons, TWIN/Total use total tons', f_sub); r += 1
put(ws, r, 1, 'THB million', f_hdr, fill=fill_hdr, border=b_hdr)
for j, (p, *_) in enumerate(PERIODS): put(ws, r, 2 + j, p, f_hdr, fill=fill_hdr, align=CENTER, border=b_hdr)
put(ws, r, 6, 'Δ YTD', f_hdr, fill=fill_hdr, align=CENTER, border=b_hdr); put(ws, r, 7, 'THB per kg', f_hdr, fill=fill_hdr, border=b_hdr)
for j, (p, *_) in enumerate(PERIODS): put(ws, r, 8 + j, p, f_hdr, fill=fill_hdr, align=CENTER, border=b_hdr)
put(ws, r, 12, 'Δ YTD', f_hdr, fill=fill_hdr, align=CENTER, border=b_hdr); r += 1
lv0 = r
LV = [('TWIN sales volume (tons)', 't', None), ('   TDC-made products (tons)', 't_tdc', None), ('TWIN GP', 'gp', 'KG:gp/t'), ('TDC GP — product cost', 'tdc_pgp', 'KG:tdc_pgp/t_tdc'), ('TDC GP — full cost', 'tdc_fgp', 'KG:tdc_fgp/t_tdc'),
      ('Total GP — product cost', 'chain_pgp', 'KG:chain_pgp/t'), ('Total GP — full cost', 'chain_fgp', 'KG:chain_fgp/t'), ('Total GP full @ constant FX', 'chain_fgp_c', 'KG:chain_fgp_c/t'), ('FX impact total', 'fxt', None)]
for label, k, kk in LV:
    bold = label.startswith(('Total', 'TWIN sales volume'))
    lf = fill_con if 'constant' in label else (fill_fx if label.startswith('FX') else None)
    put(ws, r, 1, label, f_bold if bold else f_norm, fill=lf); put(ws, r, 7, label if kk else None, f_bold if bold else f_norm, fill=lf if kk else None)
    if label.startswith(('TDC GP — product', 'Total GP — product')): hlines(ws, [r], 1, 12, thin)
    for j in range(4):
        sc = L(C0 + j)
        put(ws, r, 2 + j, f'=Summary!{sc}{SUMROW[k]}', f_bold if bold else f_norm, fmt=NUM0 if k in ('t', 't_tdc') else NUM1, border=b_left if j == 2 else None)
        if kk: put(ws, r, 8 + j, f'=Summary!{sc}{SUMROW[kk]}', f_bold if bold else f_norm, fmt=NUM2, border=b_left if j == 2 else None)
    put(ws, r, 6, f'=E{r}-D{r}', f_bold, fmt=NUM0 if k in ('t', 't_tdc') else NUM1, border=b_left)
    if kk: put(ws, r, 12, f'=IF(OR(K{r}="",J{r}=""),"",K{r}-J{r})', f_bold, fmt=NUM2, border=b_left)
    r += 1
traffic(ws, f'H{lv0 + 2}:K{r - 1}', 0, 2, 5)
r += 1
put(ws, r, 1, '2. FX — impact split into 3 parts (THB million, reported − constant FX at the Assumptions base rates)', f_sec); r += 1
fx0 = r
put(ws, r, 1, 'Component', f_hdr, fill=fill_hdr, border=b_hdr)
for j, (p, *_) in enumerate(PERIODS): put(ws, r, 2 + j, p, f_hdr, fill=fill_hdr, align=CENTER, border=b_hdr)
put(ws, r, 6, 'Meaning', f_hdr, fill=fill_hdr, border=b_hdr); r += 1
for label, k, note in [('① USD/THB — TDC layer', 'fx1', 'TDC invoices TWIN in USD while its cost is in THB → a stronger baht lowers TDC sales/GP in THB'),
                       ('② USD/IDR — TWIN purchase cost', 'fx2', 'TWIN buys in USD and sells in IDR → a weaker rupiah raises COGS in IDR while IDR selling prices do not follow = real profit lost in Indonesia (largest part)'),
                       ('③ IDR/THB — translation of TWIN GP', 'fx3', 'IDR profit translates into fewer baht — no effect on local-currency profit'),
                       ('FX impact total', 'fxt', '')]:
    bold = k == 'fxt'
    put(ws, r, 1, label, f_bold if bold else f_norm, fill=fill_tot if bold else None)
    for j in range(4): put(ws, r, 2 + j, f'=Summary!{L(C0 + j)}{SUMROW[k]}', f_bold if bold else f_norm, fmt=NUM1, fill=fill_tot if bold else None, border=b_left if j == 2 else None)
    put(ws, r, 6, note, f_norm, align=WRAP); ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=12); ws.row_dimensions[r].height = 26; r += 1
r += 1
put(ws, r, 1, '3. By customer — YTD Sep-26, all customers (sorted by tons) · THB million then THB per kg · SUMIFS formulas over Data', f_sec); r += 1
hd = ['Customer', 'Tons YTD26', 'TWIN GP MB', 'TDC GP product MB', 'TDC GP full MB', 'Total GP product MB', 'Total GP full MB', 'TWIN GP THB/kg', 'TDC GP product THB/kg', 'TDC GP full THB/kg', 'Total GP product THB/kg', 'Total GP full THB/kg', 'Total GP full THB/kg YTD25']
for j, h in enumerate(hd): put(ws, r, 1 + j, h, f_hdr, fill=(fill_rep if 1 <= j <= 11 else fill_hdr), align=CENTER, border=b_hdr)
ws.row_dimensions[r].height = 36; r += 1; lv1 = r
def kf_row(r, label, bold=False, allc=False):
    ex = '' if allc else f',{D("E")},$A{r}'
    put(ws, r, 1, label, f_bold if bold else f_norm, fill=fill_tot if bold else None)
    y6 = ('"2026"', '"<=9"', '"*"'); y5 = ('"2025"', '"<=9"', '"*"')
    tt = SUMIFS('t', *y6, ex); tt_tdc = SUMIFS('t_tdc', *y6, ex)
    put(ws, r, 2, '=' + tt, f_bold if bold else f_norm, fmt=NUM0, fill=fill_tot if bold else None, border=b_left)
    for j, k in enumerate(['gp', 'tdc_pgp', 'tdc_fgp', 'chain_pgp', 'chain_fgp']):
        put(ws, r, 3 + j, '=' + SUMIFS(k, *y6, ex) + '/1000000', f_bold if bold else f_norm, fmt=NUM2, fill=fill_tot if bold else None)
    for j, (k, den) in enumerate([('gp', 'B'), ('tdc_pgp', None), ('tdc_fgp', None), ('chain_pgp', 'B'), ('chain_fgp', 'B')]):
        dd = f'B{r}' if den else f'({tt_tdc})'
        put(ws, r, 8 + j, f'=IF({dd}=0,"",{L(3 + j)}{r}*1000/{dd})', f_bold if bold else f_norm, fmt=NUM2, fill=fill_tot if bold else None, border=b_left if j == 0 else None)
    t5 = SUMIFS('t', *y5, ex)
    put(ws, r, 13, f'=IF({t5}=0,"",{SUMIFS("chain_fgp", *y5, ex)}/({t5}*1000))', f_bold if bold else f_norm, fmt=NUM2, fill=fill_tot if bold else None, border=b_left)
kf_row(r, f'All customers ({len(custs)})', bold=True, allc=True); r += 1
for cst in custs:
    if vol26[cst] <= 0: continue
    kf_row(r, cst); r += 1
traffic(ws, f'H{lv1}:M{r - 1}', 0, 2, 5)
r_c_end = r - 1
r += 1
put(ws, r, 1, '4. Findings (static text as of 22-Oct-2026 — figures in the text do not move with the base rates)', f_sec); r += 1
findings = [
 'Scope: Native starch / Sago-pearl / Fibioca / Coarse flour excluded, leaving modified starch (TDC products = 92% of tons) + pregel / D2201 / others · YTD26 volume 3,551 t (+80% vs YTD25 1,969) but Total GP full fell from 15.7 to 13.3 THB m → 7.99 → 3.74 THB/kg (TWIN 3.01 → 1.80, TDC product 6.14 → 3.09)',
 'Cassflo 500 = 65% of tons but Total GP full is down to 1.5 THB/kg (YTD25 6.3): Heinz ABC 1,219 t (34%) TWIN margin 0.30 THB/kg (YTD25 1.31), Total full 6.05 → 1.65 · three new customers Karunia Alam Segar / Prakarsa Alam Segar / Glico Wings, 1,000 t (28%), sold below cost at TWIN (−0.4 to −0.7 THB/kg), Total full < 1 → these 4 accounts = 62% of tons but only ~2.8 THB m (21%) of Total GP — a price-vs-cost problem, not only FX',
 'Profit is concentrated in distributors and premium SKUs: Bumi Tirta Pangan Kencana 588 t (17%) delivers 5.7 THB m = 43% of Total GP full at 9.7 THB/kg · Prima Erindo 9.6, Astamulya 10.1, Nippn 16.2, Diamond Brand 13.6 THB/kg → value sits in Cassmax 102 / Cassflo 600 / Cassflo 800 / Casstex 22 (Total 8–15 THB/kg), not Cassflo 500',
 'FX YTD26 total −19.2 THB m vs 2024 average rates (① USD/THB TDC layer −8.5 ② USD/IDR TWIN cost −7.9 ③ IDR/THB translation −2.8) · FY25 −8.7 · at constant FX Total GP full YTD26 would be 32.5 THB m (9.14 THB/kg) instead of 13.3 (3.74) → half of the decline is FX, half is Cassflo 500 price/cost · part ② is real profit lost in Indonesia — consider a USD/IDR price-adjustment clause with Heinz and the new accounts',
 'Next steps: (1) set a floor for Cassflo 500 Total GP full in Indonesia (e.g. ≥ 4 THB/kg) and review the 3 new accounts before renewal (2) push mix toward Cassmax 102 / Cassflo 600 / Cassflo 800 / Casstex 22 via distributors (3) add a USD/IDR clause to IDR pricing (4) review TDC Cassflo 500 cost, which rose until product GP/kg fell to 2.3 (Q1–Q2/26)',
 'Assumptions to confirm: 2024 USD/THB uses approximate BOT averages (not in the TDC file — editable in Assumptions column B) · TDC GP per customer is allocated by product × quarter (rate_key in Data; TDC sells to TWIN as one customer) · TWIN opex is not in the file → full cost exists only at the TDC layer · the full version incl. native/sago is file v2',
]
for i, t in enumerate(findings):
    put(ws, r, 1, f'{i + 1}.', f_bold, align=Alignment(vertical='top')); put(ws, r, 2, t, f_norm, align=WRAP)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=13); ws.row_dimensions[r].height = 42; r += 1
vlines(ws, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], lv0 - 1, lv0 + len(LV) - 1, thin)
vlines(ws, [2, 3, 4, 5, 6], fx0, fx0 + 4, thin)
vlines(ws, [2, 3, 4, 6, 8, 9, 11, 13, 14], lv1 - 1, r_c_end, thin)
for c, w in zip('ABCDEFGHIJKLM', (46, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12)): ws.column_dimensions[c].width = w
ws.freeze_panes = 'A4'

# =====================================================================
# README
# =====================================================================
ws = wb.create_sheet('README', 1); ws.sheet_view.showGridLines = False
lines = [
 ('TWIN (PT Thai Wah Indonesia) — two-layer customer profitability: TDC (manufacturer) + TWIN (trading) — formula version', f_title),
 ('Prepared 26-Oct-2026 · units: Thai baht (THB) and THB per kg · data Jan-2024 → Sep-2026' + EXNOTE, f_sub),
 ('', f_norm),
 ('Workbook structure (every figure is a formula)', f_bold),
 ('• Assumptions — all inputs: base rates (B5:B6, yellow), monthly USD/THB & IDR/THB (yellow), TDC → TWIN monthly data by SN (values from the TDC file), TDC rate table per kg (SUMIFS)', f_norm),
 ('• Data — one row = one TWIN sales line (month × customer × product); columns A–S are values from the TWIN file (blue = input) · columns T onward are all formulas (FX, constant FX, TDC allocation, Total GP, 3-part FX impact)', f_norm),
 ('• Summary / Reported vs Constant / By customer / By country-tag / By customer-product / Quarterly trend / FX / Key findings — SUMIFS over Data (hidden criteria rows for year/month/quarter sit above each header)', f_norm),
 ('• TDC product rates — INDEX/MATCH on the Assumptions rate table + SUMIFS of TWIN sales', f_norm),
 ('• Indonesia portfolio — whole chain by customer (TDC direct export + via TWIN) with same-SN benchmarks vs Non-Indonesia and total TDC, from the Data TDC SN sheet (all TDC customers by month × segment × customer × SN)', f_norm),
 ('', f_norm),
 ('Business model', f_bold),
 ('TDC manufactures modified starch and sells it to TWIN (intercompany, invoiced in USD, CIF) → TWIN resells to customers: in IDR inside Indonesia, in USD outside (booked in IDR)', f_norm),
 ('', f_norm),
 ('GP definitions', f_bold),
 ('• TWIN GP = TWIN net sales − TWIN COGS (COGS = purchase price from TDC + landed cost ≈ TDC selling price + 2–5%) — TWIN opex is not in the file', f_norm),
 ('• TDC product GP = TDC net sales (transfer price) − Actual Cost (AF) − F&I · TDC full GP = product GP − Idle − PPA − Other Adj', f_norm),
 ('• Total GP = TWIN GP + TDC GP · TDC GP per customer = the product rate per kg in the same quarter TWIN sold × tons TWIN sold (rate_key in Data column N; if TDC shipped nothing that quarter the year or all-period rate is used)', f_norm),
 ('', f_norm),
 ('Constant FX method (formulas in Data)', f_bold),
 ('Hold every currency pair at the base rate (default = 2024 average) and recompute what THB profit would have been if exchange rates had not moved:', f_norm),
 ('• TDC layer: TDC NS @const = NS USD × Base USD/THB (NS USD = NS THB ÷ invoice rate) · TDC cost is in THB and unchanged → TDC GP @const = NS @const − cost', f_norm),
 ('• TWIN layer: COGS USD = COGS IDR ÷ USD/IDR of the month → COGS @const = COGS USD × Base USD/THB · IDR customers: NS @const = NS IDR × Base IDR/THB · USD customers: NS @const = (NS IDR ÷ USD/IDR) × Base USD/THB → TWIN GP @const = NS @const − COGS @const', f_norm),
 ('• FX impact = reported − constant, split in 3: ① fx1 = TDC NS − TDC NS @const · ② fx2 = (actual GP IDR − GP IDR at constant USD/IDR) × IDR/THB of the month · ③ fx3 = GP IDR at constant USD/IDR × (IDR/THB of the month − Base IDR/THB) · fx2 + fx3 = TWIN GP − TWIN GP @const always', f_norm),
 ('• Monthly USD/IDR = USD/THB ÷ IDR/THB · USD/THB 2025–26 = TDC invoice rates (weighted) · 2024 is missing from the TDC file → approximate BOT monthly averages (editable in Assumptions)', f_norm),
 ('', f_norm),
 ('Caveats', f_bold),
 ('• TWIN sale currency after Aug-25 is not in the file → customers outside Indonesia are assumed to be invoiced in USD (sale_currency column in Data is editable — the FX formulas use this column, not country)', f_norm),
 ('• The country column in Data is a descriptive tag Por can edit (e.g. Heinz / Wings) — By customer / By customer-product / By country-tag read it by formula, and the builder keeps the edits in memory/twin-customer-country.json for every future update', f_norm),
 ('• Customer names in the TWIN file are spelled inconsistently → normalised (customer_key) · TDC Q1-2024 product GP is negative in the source data', f_norm),
 ('• Source: TWIN customer breakdown.xlsx (TWIN RAWww 2024 / TWIN Raw data 2025+) · TDC Profitability_Act 2024-2026_Jul2026_AddPPA.xlsx (data_Actual, customer PT THAI WAH INDONESIA)', f_norm),
]
for i, (t, fnt) in enumerate(lines): put(ws, 1 + i, 1, t, fnt)
widths(ws, {'A': 170})

# =====================================================================
# CFO ONE-PAGE — Total / Heinz / Wings / The rest, YoY YTD with bridge + hypotheses (all formulas)
# =====================================================================
ws = wb.create_sheet('CFO one-page', 1); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 80
GROUPS = [('Total', None), ('Heinz', 'Heinz'), ('Wings', 'Wings'), ('The rest', 'REST')]
P25 = ('"2025"', '"<=9"', '"*"'); P26 = ('"2026"', '"<=9"', '"*"')
members = {}
for x in rows:
    if x['y'] in ('2025', '2026'): members.setdefault(x['country'], set()).add(x['label'])
def mem(tag): return ', '.join(sorted(members.get(tag, [])))[:180]
put(ws, 1, 1, 'TWIN — CFO one-page: YoY YTD Sep-25 → YTD Sep-26 by group (Total / Heinz / Wings / The rest)' + EXNOTE, f_title)
put(ws, 2, 1, 'All THB · every figure is a formula (SUMIFS on Data; group = tag in Data column H, edit there) · Reported unless stated · constant FX = base rates in Assumptions!B5:B6 · Δ% on THB/kg rows = change in THB/kg', f_sub)
put(ws, 3, 1, f"Heinz = {mem('Heinz')}   ·   Wings = {mem('Wings')}   ·   The rest = everything else (Total − Heinz − Wings)", f_grey)
# ---- A. KPI table ----
HR = 5; C0 = 3; SUB = ['YTD Sep-25', 'YTD Sep-26', 'Δ', 'Δ%']
put(ws, HR, 1, 'A. KPI by group', f_sec); put(ws, HR + 1, 1, 'Metric', f_hdr, fill=fill_hdr, border=b_hdr); put(ws, HR + 1, 2, 'Unit', f_hdr, fill=fill_hdr, border=b_hdr)
for gi, (gname, tag) in enumerate(GROUPS):
    cc = C0 + gi * 4
    put(ws, HR, cc, gname, f_bold, fill=(fill_rep if gi == 0 else fill_grp), align=CENTER, border=Border(left=thin)); ws.merge_cells(start_row=HR, start_column=cc, end_row=HR, end_column=cc + 3)
    for j, h in enumerate(SUB): put(ws, HR + 1, cc + j, h, f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med, left=thin if j == 0 else None))
KPI = [  # (label, unit, kind, key or (num,den), fmt)
 ('Sales volume', 'tons', 'sum', 't', NUM0), ('   of which TDC products', 'tons', 'sum', 't_tdc', NUM0),
 ('TWIN net sales', 'THB m', 'sum', 'ns', NUM1), ('TWIN ASP', 'THB/kg', 'kg', ('ns', 't'), NUM2), ('TWIN landed COGS', 'THB/kg', 'kg', ('cogs', 't'), NUM2),
 ('TWIN GP', 'THB m', 'sum', 'gp', NUM2), ('TWIN GP', 'THB/kg', 'kg', ('gp', 't'), NUM2),
 ('TDC transfer price', 'THB/kg', 'kg', ('tdc_ns', 't_tdc'), NUM2), ('TDC product cost (AF+F&I)', 'THB/kg', 'kg', ('tdc_pcost', 't_tdc'), NUM2),
 ('TDC GP product cost', 'THB m', 'sum', 'tdc_pgp', NUM2), ('TDC GP product cost', 'THB/kg', 'kg', ('tdc_pgp', 't_tdc'), NUM2),
 ('TDC GP full cost', 'THB m', 'sum', 'tdc_fgp', NUM2), ('TDC GP full cost', 'THB/kg', 'kg', ('tdc_fgp', 't_tdc'), NUM2),
 ('Total GP product cost', 'THB m', 'sum', 'chain_pgp', NUM2), ('Total GP full cost', 'THB m', 'sum', 'chain_fgp', NUM2), ('Total GP full cost', 'THB/kg', 'kg', ('chain_fgp', 't'), NUM2),
 ('Total GP full cost @ constant FX', 'THB m', 'sum', 'chain_fgp_c', NUM2), ('Total GP full cost @ constant FX', 'THB/kg', 'kg', ('chain_fgp_c', 't'), NUM2),
 ('FX impact ① USD/THB (TDC layer)', 'THB m', 'sum', 'fx1', NUM2), ('FX impact ② USD/IDR (TWIN cost)', 'THB m', 'sum', 'fx2', NUM2), ('FX impact ③ IDR/THB (translation)', 'THB m', 'sum', 'fx3', NUM2), ('FX impact total', 'THB m', 'sum', 'fxt', NUM2)]
MEAS['cogs'] = 'S'
kpi_row = {}
r = HR + 2
def gsum(key, per, tag):
    ex = '' if tag is None else f',{D("H")},"{tag}"'
    f = SUMIFS(key, *per, ex)
    return f if key in ('t', 't_tdc') else f + '/1000000'
for label, unit, kind, key, fmt in KPI:
    kpi_row[(label, unit)] = r
    put(ws, r, 1, label, f_bold if unit == 'THB/kg' or label.startswith(('Total', 'FX impact total')) else f_norm); put(ws, r, 2, unit, f_grey)
    for gi, (gname, tag) in enumerate(GROUPS):
        cc = C0 + gi * 4
        for j, per in enumerate((P25, P26)):
            c = cc + j
            if tag == 'REST':
                f = f'={L(C0 + j)}{r}-{L(C0 + 4 + j)}{r}-{L(C0 + 8 + j)}{r}' if kind == 'sum' else None
                if kind == 'kg': f = None  # REST THB/kg rows are filled after the loop from the REST THB m and tons rows
            if tag != 'REST':
                if kind == 'sum': f = '=' + gsum(key, per, tag)
                else:
                    num, den = key
                    numf = gsum(num, per, tag); denf = gsum(den, per, tag)
                    f = f'=IF({denf}=0,"",{numf}*1000/({denf}))'
            if f: put(ws, r, c, f, f_bold if unit == 'THB/kg' else f_norm, fmt=fmt, border=Border(left=thin) if j == 0 else None)
        put(ws, r, cc + 2, f'=IF(OR({L(cc)}{r}="",{L(cc+1)}{r}=""),"",{L(cc+1)}{r}-{L(cc)}{r})', f_bold, fmt=fmt)
        put(ws, r, cc + 3, None if label.startswith('FX impact') else f'=IF(OR({L(cc)}{r}="",{L(cc+1)}{r}="",{L(cc)}{r}=0),"",{L(cc+1)}{r}/{L(cc)}{r}-1)', f_grey, fmt=PCT)
    r += 1
# REST kg rows: THB m row (rest) * 1000 / tons row (rest)
den_row = {'t': kpi_row[('Sales volume', 'tons')], 't_tdc': kpi_row[('   of which TDC products', 'tons')]}
num_row = {'ns': ('TWIN net sales', 'THB m'), 'cogs': None, 'gp': ('TWIN GP', 'THB m'), 'tdc_ns': None, 'tdc_pcost': None, 'tdc_pgp': ('TDC GP product cost', 'THB m'),
           'tdc_fgp': ('TDC GP full cost', 'THB m'), 'chain_fgp': ('Total GP full cost', 'THB m'), 'chain_fgp_c': ('Total GP full cost @ constant FX', 'THB m')}
cc = C0 + 12
for label, unit, kind, key, fmt in KPI:
    if kind != 'kg': continue
    rr = kpi_row[(label, unit)]; num, den = key
    for j, per in enumerate((P25, P26)):
        c = cc + j; dref = f'{L(c)}{den_row[den]}'
        if num_row.get(num):
            nref = f'{L(c)}{kpi_row[num_row[num]]}'; f = f'=IF({dref}=0,"",{nref}*1000/{dref})'
        else:  # no THB m row for this numerator: rest = total − heinz − wings of the raw sums
            tot = gsum(num, per, None); hz = gsum(num, per, 'Heinz'); wg = gsum(num, per, 'Wings')
            f = f'=IF({dref}=0,"",({tot}-{hz}-{wg})*1000/{dref})'
        put(ws, rr, c, f, f_bold, fmt=fmt, border=Border(left=thin) if j == 0 else None)
for lab in [k for k in kpi_row if k[1] == 'THB/kg' and 'GP' in k[0]]:
    rr = kpi_row[lab]
    for gi in range(4): traffic(ws, f'{L(C0 + gi*4)}{rr}:{L(C0 + gi*4 + 1)}{rr}', 0, 2, 5)
kpi_end = r - 1
# ---- B. YoY bridge of Total GP full cost ----
r += 1
put(ws, r, 1, 'B. YoY bridge — Total GP full cost (THB m): YTD Sep-25 → YTD Sep-26', f_sec); r += 1
put(ws, r, 1, 'Step', f_hdr, fill=fill_hdr, border=b_hdr); put(ws, r, 2, 'How computed', f_hdr, fill=fill_hdr, border=b_hdr)
for gi, (gname, _) in enumerate(GROUPS): put(ws, r, C0 + gi * 4, gname, f_hdr, fill=(fill_rep if gi == 0 else fill_grp), align=CENTER, border=Border(bottom=med, left=thin)); ws.merge_cells(start_row=r, start_column=C0 + gi * 4, end_row=r, end_column=C0 + gi * 4 + 1)
r += 1; b0 = r
gp_m = kpi_row[('Total GP full cost', 'THB m')]; gp_kg = kpi_row[('Total GP full cost', 'THB/kg')]; gpc_m = kpi_row[('Total GP full cost @ constant FX', 'THB m')]
t_row = kpi_row[('Sales volume', 'tons')]; twin_m = kpi_row[('TWIN GP', 'THB m')]; tdc_m = kpi_row[('TDC GP full cost', 'THB m')]
fx_rows = [kpi_row[('FX impact ① USD/THB (TDC layer)', 'THB m')], kpi_row[('FX impact ② USD/IDR (TWIN cost)', 'THB m')], kpi_row[('FX impact ③ IDR/THB (translation)', 'THB m')]]
steps = [('Total GP full cost YTD Sep-25', 'reported', lambda c: f'={L(c)}{gp_m}'),
         ('+ Volume effect', '(tons26 − tons25) × GP/kg25; new group: GP26 ex-FX', lambda c: f'=IF({L(c)}{gp_kg}="",{L(c)}{b0+4}-{L(c)}{b0+3},({L(c+1)}{t_row}-{L(c)}{t_row})*{L(c)}{gp_kg}/1000)'),
         ('+ Price / cost / mix (ex-FX)', 'residual = ΔGP − volume − FX', lambda c: f'={L(c+1)}{gp_m}-{L(c)}{gp_m}-{L(c)}{b0+1}-{L(c)}{b0+3}'),
         ('+ FX effect', 'ΔFX impact (26 − 25)', lambda c: f'=({L(c+1)}{fx_rows[0]}+{L(c+1)}{fx_rows[1]}+{L(c+1)}{fx_rows[2]})-({L(c)}{fx_rows[0]}+{L(c)}{fx_rows[1]}+{L(c)}{fx_rows[2]})'),
         ('→ Total GP full cost YTD Sep-26', 'reported', lambda c: f'={L(c+1)}{gp_m}'),
         ('check (should be 0)', 'start + steps − end', lambda c: f'={L(c)}{b0}+{L(c)}{b0+1}+{L(c)}{b0+2}+{L(c)}{b0+3}-{L(c)}{b0+4}'),
         ('   FX ① USD/THB (TDC layer)', 'Δ', lambda c: f'={L(c+1)}{fx_rows[0]}-{L(c)}{fx_rows[0]}'),
         ('   FX ② USD/IDR (TWIN cost)', 'Δ', lambda c: f'={L(c+1)}{fx_rows[1]}-{L(c)}{fx_rows[1]}'),
         ('   FX ③ IDR/THB (translation)', 'Δ', lambda c: f'={L(c+1)}{fx_rows[2]}-{L(c)}{fx_rows[2]}'),
         ('   of ΔGP: TWIN layer', 'ΔTWIN GP', lambda c: f'={L(c+1)}{twin_m}-{L(c)}{twin_m}'),
         ('   of ΔGP: TDC layer (full cost)', 'ΔTDC GP full', lambda c: f'={L(c+1)}{tdc_m}-{L(c)}{tdc_m}')]
for i, (lab, how, fn) in enumerate(steps):
    bold = lab.startswith(('Total', '→ Total'))
    put(ws, r, 1, lab, f_bold if bold else (f_grey if lab.startswith('check') else f_norm)); put(ws, r, 2, how, f_grey)
    for gi in range(4):
        c = C0 + gi * 4
        put(ws, r, c, fn(c), f_bold if bold else f_norm, fmt=NUM2, fill=(fill_fx if 'FX' in lab else None), border=Border(left=thin))
    r += 1
b_end = r - 1
# ---- C. Hypotheses ----
r += 1
put(ws, r, 1, 'C. Hypotheses to review with CFO — evidence and verdict are live formulas (change the base FX or tags and they update)', f_sec); r += 1
for j, h in enumerate(['#', 'Hypothesis', 'Evidence (YTD25 → YTD26)', '', '', '', '', '', '', '', '', 'Verdict']): put(ws, r, 1 + j, h, f_hdr, fill=fill_hdr, border=b_hdr)
ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=11); r += 1
H, W, Rr, T = C0 + 4, C0 + 8, C0 + 12, C0  # first col of each group
def ref(gcol, row, j): return f'{L(gcol + j)}{row}'
def t2(a): return f'TEXT({a},"0.00")'
asp = kpi_row[('TWIN ASP', 'THB/kg')]; cogs = kpi_row[('TWIN landed COGS', 'THB/kg')]; tgp_kg = kpi_row[('TWIN GP', 'THB/kg')]
tp = kpi_row[('TDC transfer price', 'THB/kg')]; tpc = kpi_row[('TDC product cost (AF+F&I)', 'THB/kg')]; tpg_kg = kpi_row[('TDC GP product cost', 'THB/kg')]
gpc_kg = kpi_row[('Total GP full cost @ constant FX', 'THB/kg')]; fxt = kpi_row[('FX impact total', 'THB m')]
hyps = [
 ('H1', 'Heinz: the GP collapse is price erosion at TWIN plus higher TDC cost, not volume (volume is flat).',
  f'="Tons "&TEXT({ref(H,t_row,0)},"#,##0")&" → "&TEXT({ref(H,t_row,1)},"#,##0")&" · TWIN ASP "&{t2(ref(H,asp,0))}&" → "&{t2(ref(H,asp,1))}&" · landed COGS "&{t2(ref(H,cogs,0))}&" → "&{t2(ref(H,cogs,1))}&" · TDC product cost "&{t2(ref(H,tpc,0))}&" → "&{t2(ref(H,tpc,1))}&" · Total GP full "&{t2(ref(H,gp_kg,0))}&" → "&{t2(ref(H,gp_kg,1))}&" THB/kg"',
  f'=IF(ABS({ref(H,t_row,1)}/{ref(H,t_row,0)}-1)<0.1,IF(AND({ref(H,asp,1)}<{ref(H,asp,0)},{ref(H,tpc,1)}>{ref(H,tpc,0)}),"Supported — price down & cost up, volume flat",IF({ref(H,asp,1)}<{ref(H,asp,0)},"Partly — price down, cost not up","Partly — cost up, price held")),"Not supported — volume moved >10%")'),
 ('H2', 'Wings: volume was won at a negative TWIN margin; the chain stays positive only because TDC still earns product GP.',
  f'="Tons "&TEXT({ref(W,t_row,0)},"#,##0")&" → "&TEXT({ref(W,t_row,1)},"#,##0")&" · TWIN GP "&{t2(ref(W,tgp_kg,1))}&" THB/kg · TDC GP product "&{t2(ref(W,tpg_kg,1))}&" · Total GP full "&{t2(ref(W,gp_kg,1))}&" THB/kg (YTD26)"',
  f'=IF({ref(W,t_row,1)}=0,"No volume tagged Wings — set tags in Data!H",IF(AND({ref(W,tgp_kg,1)}<0,{ref(W,gp_kg,1)}>0),"Supported — TWIN negative, chain positive via TDC",IF({ref(W,tgp_kg,1)}<0,"Partly — TWIN negative and chain negative too","Not supported — TWIN margin positive")))'),
 ('H3', 'The rest (long tail of accounts) carries the profit: its Total GP/kg is a multiple of Heinz and Wings — mix shift is the lever.',
  f'="Rest Total GP full "&{t2(ref(Rr,gp_kg,0))}&" → "&{t2(ref(Rr,gp_kg,1))}&" THB/kg vs Heinz "&{t2(ref(H,gp_kg,1))}&" · Rest share of Total GP "&TEXT({ref(Rr,gp_m,1)}/{ref(T,gp_m,1)},"0%")&" on "&TEXT({ref(Rr,t_row,1)}/{ref(T,t_row,1)},"0%")&" of tons"',
  f'=IF({ref(H,gp_kg,1)}<=0,"Supported — Heinz at or below zero",IF({ref(Rr,gp_kg,1)}/{ref(H,gp_kg,1)}>=2,"Supported — rest earns "&TEXT({ref(Rr,gp_kg,1)}/{ref(H,gp_kg,1)},"0.0")&"x Heinz per kg","Not supported — gap below 2x"))'),
 ('H4', 'Reported Total GP fell despite +80% volume because FX (mainly ② USD/IDR on TWIN cost) more than offset the volume gain — at constant FX, Total GP would have risen.',
  f'="ΔTotal GP reported "&{t2(f"{L(T+1)}{gp_m}-{L(T)}{gp_m}")}&" THB m · volume effect +"&{t2(f"{L(T)}{b0+1}")}&" · FX effect "&{t2(f"{L(T)}{b0+3}")}&" (① "&{t2(f"{L(T)}{b0+6}")}&" ② "&{t2(f"{L(T)}{b0+7}")}&" ③ "&{t2(f"{L(T)}{b0+8}")}&") · at constant FX "&{t2(ref(T,gpc_m,0))}&" → "&{t2(ref(T,gpc_m,1))}&" THB m"',
  f'=IF(AND({L(T+1)}{gp_m}<{L(T)}{gp_m},{ref(T,gpc_m,1)}>{ref(T,gpc_m,0)}),"Supported — at constant FX GP +"&{t2(f"{ref(T,gpc_m,1)}-{ref(T,gpc_m,0)}")}&" THB m; FX "&{t2(f"{L(T)}{b0+3}")}&", largest = "&IF(MIN({L(T)}{b0+6},{L(T)}{b0+7},{L(T)}{b0+8})={L(T)}{b0+7},"② USD/IDR",IF(MIN({L(T)}{b0+6},{L(T)}{b0+7},{L(T)}{b0+8})={L(T)}{b0+6},"① USD/THB","③ IDR/THB")),IF({L(T+1)}{gp_m}>={L(T)}{gp_m},"n/a — reported GP did not fall","Not supported — GP falls even at constant FX"))'),
 ('H5', 'Even at constant FX the margin per kg deteriorated → there is an underlying price/cost problem beyond FX (mainly Cassflo 500).',
  f'="Total GP full @ constant FX "&{t2(ref(T,gpc_kg,0))}&" → "&{t2(ref(T,gpc_kg,1))}&" THB/kg · Heinz "&{t2(ref(H,gpc_kg,0))}&" → "&{t2(ref(H,gpc_kg,1))}&" · Rest "&{t2(ref(Rr,gpc_kg,0))}&" → "&{t2(ref(Rr,gpc_kg,1))}',
  f'=IF({ref(T,gpc_kg,1)}<{ref(T,gpc_kg,0)},"Supported — constant-FX GP/kg fell "&{t2(f"{ref(T,gpc_kg,1)}-{ref(T,gpc_kg,0)}")}&" THB/kg","Not supported — constant-FX GP/kg held")'),
]
for hid, text, ev, vd in hyps:
    put(ws, r, 1, hid, f_bold, align=Alignment(vertical='top')); put(ws, r, 2, text, f_norm, align=WRAP)
    put(ws, r, 3, ev, f_grey, align=WRAP); ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=11)
    put(ws, r, 12, vd, f_bold, align=WRAP); ws.merge_cells(start_row=r, start_column=12, end_row=r, end_column=18)
    ws.row_dimensions[r].height = 44; r += 1
put(ws, r, 1, 'Reading guide: Reported = THB at actual monthly rates · constant FX holds USD/THB, IDR/THB and USD/IDR at the Assumptions base rates · Total GP = TWIN GP + TDC GP · tags for Heinz / Wings are set in Data column H (the rest = all other tags)', f_grey)
widths(ws, {'A': 34, 'B': 24})
for c in range(C0, C0 + 16): ws.column_dimensions[L(c)].width = 9.2
ws.print_options.horizontalCentered = True; ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.print_area = f'A1:R{r}'
vlines(ws, [C0 + gi * 4 for gi in range(4)] + [C0 + 16], HR, kpi_end, thin)

# =====================================================================
# DATA TDC SN (all TDC customers by month x segment x customer x SN) + INDONESIA PORTFOLIO (Por's handwritten template)
# =====================================================================
import csv as _csv
tsn = list(_csv.DictReader(open(f'{S}/tdc_sn.csv', encoding='utf-8')))
wt = wb.create_sheet('Data TDC SN'); wt.sheet_view.zoomScale = 85
tcols = ['month', 'year', 'month_num', 'quarter', 'segment', 'customer', 'sn', 'trade_name', 'tons', 'ns_thb', 'af', 'fi', 'idle', 'oadj', 'ppa']
for j, h in enumerate(tcols + ['product_cost', 'product_gp', 'full_gp']): put(wt, 1, 1 + j, h, f_hdr, fill=fill_hdr)
for i, x in enumerate(tsn):
    r = 2 + i
    for j, h in enumerate(tcols):
        v = x[h]
        if h in ('tons', 'ns_thb', 'af', 'fi', 'idle', 'oadj', 'ppa'): v = float(v)
        elif h == 'month_num': v = int(v)
        put(wt, r, 1 + j, v, f_in if h in ('tons', 'ns_thb', 'af', 'fi', 'idle', 'oadj', 'ppa') else f_norm, fmt=(NUM2 if h == 'tons' else (NUM0 if h in ('ns_thb', 'af', 'fi', 'idle', 'oadj', 'ppa') else None)))
    put(wt, r, 16, f'=K{r}+L{r}', fmt=NUM0); put(wt, r, 17, f'=J{r}-P{r}', fmt=NUM0); put(wt, r, 18, f'=Q{r}-M{r}-N{r}-O{r}', fmt=NUM0)
TN = len(tsn) + 1
wt.freeze_panes = 'G2'; wt.auto_filter.ref = f'A1:R{TN}'
for c in range(1, 19): wt.column_dimensions[L(c)].width = 12
wt.column_dimensions['F'].width = 40; wt.column_dimensions['H'].width = 22
put(wt, 1, 20, 'Source: TDC Profitability data_Actual, ALL customers. segment = TWIN (intercompany) / Indonesia direct (export to Indonesia, by customer) / Non-Indonesia (all other customers, aggregated per SN). product_cost = AF + F&I; full_gp = NS − product_cost − idle − other adj − PPA.', f_grey)
def TS(col): return f"'Data TDC SN'!${col}$2:${col}${TN}"
def TSUM(col, yc, mc, extra): return f'SUMIFS({TS(col)},{TS("B")},{yc},{TS("C")},{mc}{extra})'

ws = wb.create_sheet('Indonesia portfolio', 2); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 85
put(ws, 1, 1, 'Indonesia portfolio — whole chain by customer: TDC direct export + via TWIN · volume FY24 / FY25 / YTD · YTD Sep-26 NS, GP per kg (TWIN + TDC = combined) · benchmark = same SN sold outside Indonesia and total TDC' + EXNOTE, f_title)
put(ws, 2, 1, "All THB, reported FX · TDC direct rows = TDC's own invoice to the Indonesian customer (no TWIN layer) · via-TWIN rows = TWIN sale to the end customer + TDC GP allocated per product (see README) · TWIN rows limited to customers whose source country is Indonesia (Data col BC) · Benchmarks from 'Data TDC SN' (all TDC customers): Non-Indonesia = every customer outside Indonesia, Total TDC = all customers incl. Indonesia and TWIN", f_sub)
# criteria (hidden rows 4-5): year / month for E..H volume columns; YTD Sep-26 for the rest
VOLP = [('FY2024', '2024', '<=12'), ('FY2025', '2025', '<=12'), ('YTD Sep-25', '2025', '<=9'), ('YTD Sep-26', '2026', '<=9')]
put(ws, 4, 1, 'crit: year', f_grey); put(ws, 5, 1, 'crit: month', f_grey)
for j, (nm, y, mc) in enumerate(VOLP): put(ws, 4, 5 + j, y, f_grey); put(ws, 5, 5 + j, mc, f_grey)
put(ws, 4, 9, '2026', f_grey); put(ws, 5, 9, '<=9', f_grey)   # I4/I5 = YTD Sep-26 criteria used by all '26 columns
ws.row_dimensions[4].hidden = True; ws.row_dimensions[5].hidden = True
Y26, M26 = '$I$4', '$I$5'
HR = 7
grp_hdr = [(1, 4, 'Customer / channel / SN', fill_hdr), (5, 8, 'Volume (tons)', fill_hdr), (9, 15, 'YTD Sep-26 — THB (Reported)', fill_rep),
           (16, 18, 'Benchmark same SN, YTD Sep-26 — NON-INDONESIA (TDC)', fill_con), (19, 21, 'Benchmark same SN, YTD Sep-26 — TOTAL TDC (all customers)', fill_con), (22, 23, 'Gap vs Total TDC (Indonesia combined − benchmark)', fill_fx)]
for c1, c2, lab, fl in grp_hdr:
    put(ws, HR - 1, c1, lab, f_bold, fill=fl, align=CENTER, border=Border(left=thin))
    if c2 > c1: ws.merge_cells(start_row=HR - 1, start_column=c1, end_row=HR - 1, end_column=c2)
hdrs = ['Customer', 'Channel', 'SN', 'Product', 'FY2024', 'FY2025', 'YTD Sep-25', 'YTD Sep-26', 'NS (THB m)', 'TWIN GP THB/kg', 'TDC GP product THB/kg', 'TDC GP full THB/kg', 'Combined GP product THB/kg', 'Combined GP full THB/kg', 'Combined GP full (THB m)',
        'Vol (tons)', 'TDC GP product THB/kg', 'TDC GP full THB/kg', 'Vol (tons)', 'TDC GP product THB/kg', 'TDC GP full THB/kg', 'Product GP THB/kg', 'Full GP THB/kg']
for j, h in enumerate(hdrs): put(ws, HR, 1 + j, h, f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med, left=thin if (1 + j) in (1, 5, 9, 10, 11, 13, 15, 16, 19, 22) else None))
put(ws, HR, 24, 'leaf', f_grey); ws.column_dimensions['X'].width = 4
ws.row_dimensions[HR].height = 44
MB = '/1000000'
def bench(r, snref):
    """benchmark columns P..U for the SN in snref (cell ref) — blank if no SN"""
    for base, seg in ((16, '"Non-Indonesia"'), (19, None)):
        ex = f',{TS("G")},{snref}' + (f',{TS("E")},{seg}' if seg else '')
        t = TSUM('I', Y26, M26, ex)
        put(ws, r, base, f'=IF({snref}="","",{t})', fmt=NUM0, border=Border(left=thin))
        put(ws, r, base + 1, f'=IF(OR({snref}="",{L(base)}{r}=0),"",{TSUM("Q", Y26, M26, ex)}/({L(base)}{r}*1000))', fmt=NUM2)
        put(ws, r, base + 2, f'=IF(OR({snref}="",{L(base)}{r}=0),"",{TSUM("R", Y26, M26, ex)}/({L(base)}{r}*1000))', fmt=NUM2)
    put(ws, r, 22, f'=IF(OR(T{r}="",M{r}=""),"",M{r}-T{r})', f_bold, fmt=NUM2, border=Border(left=thin))
    put(ws, r, 23, f'=IF(OR(U{r}="",N{r}=""),"",N{r}-U{r})', f_bold, fmt=NUM2)
def summary_line(r, r1, r2, label, level, bold=True, fill=None, chan='via TWIN', sn_txt=None, prod_txt=None):
    """customer / group summary over breakdown rows r1..r2: sums for tons, NS, GP THB m and benchmark volumes; tonne-weighted per-kg"""
    fnt = f_bold if bold else f_norm
    put(ws, r, 1, label, fnt, fill=fill); put(ws, r, 2, chan, f_grey, fill=fill); put(ws, r, 3, sn_txt, f_grey, fill=fill); put(ws, r, 4, prod_txt, f_grey, fill=fill)
    X = f'$X{r1}:$X{r2}'   # leaf flag (1 on product lines only) -> no double counting of nested summary lines
    for c in (5, 6, 7, 8, 9, 15, 16, 19):
        put(ws, r, c, f'=SUMPRODUCT({X},{L(c)}{r1}:{L(c)}{r2})', fnt, fmt=NUM0, fill=fill, border=Border(left=thin) if c in (5, 9, 15, 16, 19) else None)
    for c in (10, 11, 12, 13, 14, 17, 18, 20, 21):
        cl = L(c)
        put(ws, r, c, f'=IF(SUMPRODUCT({X},--ISNUMBER({cl}{r1}:{cl}{r2}),H{r1}:H{r2})=0,"",SUMPRODUCT({X},--ISNUMBER({cl}{r1}:{cl}{r2}),{cl}{r1}:{cl}{r2},H{r1}:H{r2})/SUMPRODUCT({X},--ISNUMBER({cl}{r1}:{cl}{r2}),H{r1}:H{r2}))', fnt, fmt=NUM2, fill=fill, border=Border(left=thin) if c in (10, 11, 13) else None)
    put(ws, r, 22, f'=IF(OR(T{r}="",M{r}=""),"",M{r}-T{r})', fnt, fmt=NUM2, fill=fill, border=Border(left=thin)); put(ws, r, 23, f'=IF(OR(U{r}="",N{r}=""),"",N{r}-U{r})', fnt, fmt=NUM2, fill=fill)
    if level: ws.row_dimensions[r].outline_level = level
port_rows = {}
# ---- rows: TDC direct ----
r = HR + 1
put(ws, r, 1, 'TDC direct export to Indonesia', f_sec); r += 1
direct = {}
for x in tsn:
    if x['segment'] == 'Indonesia direct':
        k = (x['customer'], x['sn']); d = direct.setdefault(k, {'tn': x['trade_name'], 'v26': 0.0, 'v25': 0.0, 'vall': 0.0})
        if x['year'] == '2026': d['v26'] += float(x['tons'])
        if x['year'] == '2025': d['v25'] += float(x['tons'])
        d['vall'] += float(x['tons'])
d_first = r
dc26 = {}; dc25 = {}
for (cust, sn), d in direct.items(): dc26[cust] = dc26.get(cust, 0) + d['v26']; dc25[cust] = dc25.get(cust, 0) + d['v25']
def direct_line(r, cust, sn, d, indent=False):
    fnt = f_grey if indent else f_norm
    put(ws, r, 1, ('   • ' if indent else '') + cust, fnt); put(ws, r, 2, 'TDC direct', f_grey); put(ws, r, 3, sn, f_grey); put(ws, r, 4, d['tn'], f_grey)
    cref_ = f'TRIM(SUBSTITUTE($A{r},"•",""))' if indent else f'$A{r}'
    ex = f',{TS("E")},"Indonesia direct",{TS("F")},{cref_},{TS("G")},$C{r}'
    for j in range(4): put(ws, r, 5 + j, '=' + TSUM('I', f'{L(5+j)}$4', f'{L(5+j)}$5', ex), fnt, fmt=NUM0, border=Border(left=thin) if j == 0 else None)
    put(ws, r, 9, '=' + TSUM('J', Y26, M26, ex) + MB, fnt, fmt=NUM0, border=Border(left=thin))
    put(ws, r, 10, None, f_grey, border=Border(left=thin))
    put(ws, r, 11, f'=IF(H{r}=0,"",{TSUM("Q", Y26, M26, ex)}/(H{r}*1000))', fnt, fmt=NUM2, border=Border(left=thin))
    put(ws, r, 12, f'=IF(H{r}=0,"",{TSUM("R", Y26, M26, ex)}/(H{r}*1000))', fnt, fmt=NUM2)
    put(ws, r, 13, f'=K{r}', f_grey if indent else f_bold, fmt=NUM2, border=Border(left=thin)); put(ws, r, 14, f'=L{r}', f_grey if indent else f_bold, fmt=NUM2)
    put(ws, r, 15, '=' + TSUM('R', Y26, M26, ex) + MB, fnt, fmt=NUM0, border=Border(left=thin))
    bench(r, f'$C{r}'); put(ws, r, 24, 1, f_grey)
dcusts = sorted(dc26, key=lambda c: (-dc26[c], -dc25[c], c))
for cust in dcusts:
    cl = [(k, d) for k, d in sorted(direct.items(), key=lambda kv: (-kv[1]['v26'], -kv[1]['v25'])) if k[0] == cust and d['vall'] >= 1]
    if not cl: continue
    if len(cl) == 1:
        direct_line(r, cust, cl[0][0][1], cl[0][1]); port_rows['direct:' + cust] = r; r += 1; continue
    hdr_row = r; r += 1
    for (c_, sn), d in cl: direct_line(r, c_, sn, d, indent=True); ws.row_dimensions[r].outline_level = 1; r += 1
    summary_line(hdr_row, hdr_row + 1, r - 1, cust, 0, chan='TDC direct', sn_txt=f'{len(cl)} SNs', prod_txt='multiple (see breakdown)')
    port_rows['direct:' + cust] = hdr_row
d_last = r - 1
put(ws, r, 1, 'Subtotal — TDC direct', f_bold, fill=fill_tot)
exd = f',{TS("E")},"Indonesia direct"'
for j in range(4): put(ws, r, 5 + j, '=' + TSUM('I', f'{L(5+j)}$4', f'{L(5+j)}$5', exd), f_bold, fmt=NUM0, fill=fill_tot)
put(ws, r, 9, '=' + TSUM('J', Y26, M26, exd) + MB, f_bold, fmt=NUM0, fill=fill_tot)
put(ws, r, 11, f'=IF(H{r}=0,"",{TSUM("Q", Y26, M26, exd)}/(H{r}*1000))', f_bold, fmt=NUM2, fill=fill_tot)
put(ws, r, 12, f'=IF(H{r}=0,"",{TSUM("R", Y26, M26, exd)}/(H{r}*1000))', f_bold, fmt=NUM2, fill=fill_tot)
put(ws, r, 13, f'=K{r}', f_bold, fmt=NUM2, fill=fill_tot); put(ws, r, 14, f'=L{r}', f_bold, fmt=NUM2, fill=fill_tot)
put(ws, r, 15, '=' + TSUM('R', Y26, M26, exd) + MB, f_bold, fmt=NUM0, fill=fill_tot)
for c in (2, 3, 4, 10, 16, 17, 18, 19, 20, 21, 22, 23): put(ws, r, c, None, fill=fill_tot)
d_sub = r; port_rows['d_sub'] = r; r += 2
# ---- rows: via TWIN (Indonesia source country) ----
put(ws, r, 1, 'Via TWIN (PT Thai Wah Indonesia) — customers in Indonesia', f_sec); r += 1
tag_members = {}
for x in rows:
    if x.get('country_src', x['country']) == 'Indonesia': tag_members.setdefault(x['country'], set()).add(x['label'])
GROUP_TAGS = {t for t, m in tag_members.items() if t != 'Indonesia' and len(m) > 1}   # e.g. Wings (3 customers) -> one line
tw = {}
for x in rows:
    if x.get('country_src', x['country']) != 'Indonesia': continue
    ent = x['country'] if x['country'] in GROUP_TAGS else x['label']
    k = (ent, x['prod']); d = tw.setdefault(k, {'sn': x['sn'], 'v26': 0.0, 'v25': 0.0, 'vall': 0.0, 'tag': x['country'], 'grp': x['country'] in GROUP_TAGS})
    if x['y'] == '2026': d['v26'] += x['t']
    if x['y'] == '2025': d['v25'] += x['t']
    d['vall'] += x['t']
tc26 = {}; tc25 = {}
for (ent, prod), d in tw.items(): tc26[ent] = tc26.get(ent, 0) + d['v26']; tc25[ent] = tc25.get(ent, 0) + d['v25']
t_first = r
import os as _os
# ---- top-80% customers (by YTD Sep-26 volume) shown as-is; the rest = one summary line + breakdown rows (outline level 1)
ents = sorted({e for e, _ in tw}, key=lambda e: (-tc26[e], -tc25[e], e))
tot26 = sum(tc26.values()) or 1
top_set = set(); cum = 0.0
for e in ents:
    if cum < 0.8 * tot26: top_set.add(e); cum += tc26[e]
_pin = json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'memory', 'twin-customer-country.json'), encoding='utf-8')).get('pinned_customers', []) if _os.path.exists(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'memory', 'twin-customer-country.json')) else []
for e in ents:
    if any(e.upper().startswith(pp.upper()) for pp in _pin): top_set.add(e)   # Por: always shown on its own line (e.g. Garudafood)
rest_ents = [e for e in ents if e not in top_set]
lines = [(k, d) for k, d in sorted(tw.items(), key=lambda kv: (-tc26[kv[0][0]], -tc25[kv[0][0]], kv[0][0], -kv[1]['v26'], -kv[1]['v25'])) if d['vall'] >= 1]
def twin_line(r, ent, prod, d, indent=False):
    fnt = f_grey if indent else f_norm
    if d['grp']:
        label = f"{ent} group ({' / '.join(sorted(tag_members[ent]))})"
        put(ws, r, 1, ('   • ' if indent else '') + label, f_grey if indent else f_bold); put(ws, r, 2, f'via TWIN · tag {ent}', f_grey)
        ex = f',{D("H")},"{ent}",{D("J")},$D{r}'
    else:
        put(ws, r, 1, ('   • ' if indent else '') + ent, fnt); put(ws, r, 2, 'via TWIN' + ('' if d['tag'] == 'Indonesia' else f" · {d['tag']}"), f_grey)
        ex = f',{D("E")},' + (f'TRIM(SUBSTITUTE($A{r},"•",""))' if indent else f'$A{r}') + f',{D("J")},$D{r}'
    put(ws, r, 3, d['sn'] or '', f_grey); put(ws, r, 4, prod, f_grey)
    for j in range(4): put(ws, r, 5 + j, '=' + SUMIFS('t', f'{L(5+j)}$4', f'{L(5+j)}$5', '"*"', ex), fnt, fmt=NUM0, border=Border(left=thin) if j == 0 else None)
    put(ws, r, 9, '=' + SUMIFS('ns', Y26, M26, '"*"', ex) + MB, fnt, fmt=NUM0, border=Border(left=thin))
    put(ws, r, 10, f'=IF(H{r}=0,"",{SUMIFS("gp", Y26, M26, chr(34)+"*"+chr(34), ex)}/(H{r}*1000))', fnt, fmt=NUM2, border=Border(left=thin))
    put(ws, r, 11, f'=IF(OR($C{r}="",H{r}=0),"",{SUMIFS("tdc_pgp", Y26, M26, chr(34)+"*"+chr(34), ex)}/(H{r}*1000))', fnt, fmt=NUM2, border=Border(left=thin))
    put(ws, r, 12, f'=IF(OR($C{r}="",H{r}=0),"",{SUMIFS("tdc_fgp", Y26, M26, chr(34)+"*"+chr(34), ex)}/(H{r}*1000))', fnt, fmt=NUM2)
    put(ws, r, 13, f'=IF(H{r}=0,"",{SUMIFS("chain_pgp", Y26, M26, chr(34)+"*"+chr(34), ex)}/(H{r}*1000))', f_grey if indent else f_bold, fmt=NUM2, border=Border(left=thin))
    put(ws, r, 14, f'=IF(H{r}=0,"",{SUMIFS("chain_fgp", Y26, M26, chr(34)+"*"+chr(34), ex)}/(H{r}*1000))', f_grey if indent else f_bold, fmt=NUM2)
    put(ws, r, 15, '=' + SUMIFS('chain_fgp', Y26, M26, '"*"', ex) + MB, fnt, fmt=NUM0, border=Border(left=thin))
    bench(r, f'$C{r}'); put(ws, r, 24, 1, f_grey)
def write_customer(r, ent, base_level):
    """one customer (or group tag): single line if one product, else summary line + product lines one level deeper. returns next row"""
    cl = [(k, d) for k, d in lines if k[0] == ent]
    if not cl: return r
    if len(cl) == 1:
        (e, prod), d = cl[0]; twin_line(r, e, prod, d, indent=base_level > 0)
        if base_level: ws.row_dimensions[r].outline_level = base_level
        return r + 1
    hdr_row = r; r += 1
    for (e, prod), d in cl:
        twin_line(r, e, prod, d, indent=True); ws.row_dimensions[r].outline_level = base_level + 1; r += 1
    d0 = cl[0][1]
    label = (f"{ent} group ({' / '.join(sorted(tag_members[ent]))})" if d0['grp'] else ent)
    summary_line(hdr_row, hdr_row + 1, r - 1, ('   • ' if base_level else '') + label, base_level, bold=not base_level,
                 chan='via TWIN' + (f' · tag {ent}' if d0['grp'] else ('' if d0['tag'] == 'Indonesia' else f" · {d0['tag']}")),
                 sn_txt=f'{len(cl)} SNs', prod_txt='multiple (see breakdown)')
    return r
for ent in ents:
    if ent in top_set: port_rows['twin:' + ent] = r; r = write_customer(r, ent, 0)
top_last = r - 1
if rest_ents:
    rest_row = r; port_rows['REST'] = r; r += 1
    for ent in rest_ents: r = write_customer(r, ent, 1)
    summary_line(rest_row, rest_row + 1, r - 1, f'The rest — {len(rest_ents)} customers below the top-80% volume line (breakdown below, collapsible)', 0, fill=fill_tot, sn_txt=None, prod_txt=None)
ws.sheet_properties.outlinePr.summaryBelow = False
t_last = r - 1
put(ws, r, 1, 'Subtotal — via TWIN (Indonesia)', f_bold, fill=fill_tot)
ext = f',{D("BC")},"Indonesia"'
for j in range(4): put(ws, r, 5 + j, '=' + SUMIFS('t', f'{L(5+j)}$4', f'{L(5+j)}$5', '"*"', ext), f_bold, fmt=NUM0, fill=fill_tot)
put(ws, r, 9, '=' + SUMIFS('ns', Y26, M26, '"*"', ext) + MB, f_bold, fmt=NUM0, fill=fill_tot)
put(ws, r, 10, f'=IF(H{r}=0,"",{SUMIFS("gp", Y26, M26, chr(34)+"*"+chr(34), ext)}/(H{r}*1000))', f_bold, fmt=NUM2, fill=fill_tot)
tt = SUMIFS('t_tdc', Y26, M26, '"*"', ext)
put(ws, r, 11, f'=IF({tt}=0,"",{SUMIFS("tdc_pgp", Y26, M26, chr(34)+"*"+chr(34), ext)}/({tt}*1000))', f_bold, fmt=NUM2, fill=fill_tot)
put(ws, r, 12, f'=IF({tt}=0,"",{SUMIFS("tdc_fgp", Y26, M26, chr(34)+"*"+chr(34), ext)}/({tt}*1000))', f_bold, fmt=NUM2, fill=fill_tot)
put(ws, r, 13, f'=IF(H{r}=0,"",{SUMIFS("chain_pgp", Y26, M26, chr(34)+"*"+chr(34), ext)}/(H{r}*1000))', f_bold, fmt=NUM2, fill=fill_tot)
put(ws, r, 14, f'=IF(H{r}=0,"",{SUMIFS("chain_fgp", Y26, M26, chr(34)+"*"+chr(34), ext)}/(H{r}*1000))', f_bold, fmt=NUM2, fill=fill_tot)
put(ws, r, 15, '=' + SUMIFS('chain_fgp', Y26, M26, '"*"', ext) + MB, f_bold, fmt=NUM0, fill=fill_tot)
for c in (2, 3, 4, 16, 17, 18, 19, 20, 21, 22, 23): put(ws, r, c, None, fill=fill_tot)
t_sub = r; port_rows['t_sub'] = r; r += 2
# ---- grand total + benchmarks ----
put(ws, r, 1, 'TOTAL INDONESIA (direct + via TWIN)', f_bold, fill=fill_rep)
for j in range(4): put(ws, r, 5 + j, f'={L(5+j)}{d_sub}+{L(5+j)}{t_sub}', f_bold, fmt=NUM0, fill=fill_rep)
put(ws, r, 9, f'=I{d_sub}+I{t_sub}', f_bold, fmt=NUM0, fill=fill_rep)
put(ws, r, 10, f'=IF(H{r}=0,"",IFERROR(J{t_sub}*H{t_sub},0)/H{r})', f_bold, fmt=NUM2, fill=fill_rep)
put(ws, r, 13, f'=IF(H{r}=0,"",(IFERROR(M{d_sub}*H{d_sub},0)+IFERROR(M{t_sub}*H{t_sub},0))/H{r})', f_bold, fmt=NUM2, fill=fill_rep)
put(ws, r, 14, f'=IF(H{r}=0,"",(O{d_sub}+O{t_sub})*1000/H{r})', f_bold, fmt=NUM2, fill=fill_rep)
put(ws, r, 15, f'=O{d_sub}+O{t_sub}', f_bold, fmt=NUM0, fill=fill_rep)
for c in (2, 3, 4, 11, 12, 16, 17, 18, 19, 20, 21, 22, 23): put(ws, r, c, None, fill=fill_rep)
g_tot = r; port_rows['g_tot'] = r; r += 1
put(ws, r, 1, 'Benchmark — TDC Non-Indonesia, all SNs (YTD Sep-26)', f_bold, fill=fill_con)
exn = f',{TS("E")},"Non-Indonesia"'
for j in range(4): put(ws, r, 5 + j, '=' + TSUM('I', f'{L(5+j)}$4', f'{L(5+j)}$5', exn), f_bold, fmt=NUM0, fill=fill_con)
put(ws, r, 9, '=' + TSUM('J', Y26, M26, exn) + MB, f_bold, fmt=NUM0, fill=fill_con)
put(ws, r, 11, f'=IF(H{r}=0,"",{TSUM("Q", Y26, M26, exn)}/(H{r}*1000))', f_bold, fmt=NUM2, fill=fill_con)
put(ws, r, 12, f'=IF(H{r}=0,"",{TSUM("R", Y26, M26, exn)}/(H{r}*1000))', f_bold, fmt=NUM2, fill=fill_con)
put(ws, r, 15, '=' + TSUM('R', Y26, M26, exn) + MB, f_bold, fmt=NUM0, fill=fill_con)
for c in (2, 3, 4, 10, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23): put(ws, r, c, None, fill=fill_con)
r += 1
put(ws, r, 1, 'Benchmark — TOTAL TDC, all customers & SNs (YTD Sep-26)', f_bold, fill=fill_con)
for j in range(4): put(ws, r, 5 + j, '=' + TSUM('I', f'{L(5+j)}$4', f'{L(5+j)}$5', ''), f_bold, fmt=NUM0, fill=fill_con)
put(ws, r, 9, '=' + TSUM('J', Y26, M26, '') + MB, f_bold, fmt=NUM0, fill=fill_con)
put(ws, r, 11, f'=IF(H{r}=0,"",{TSUM("Q", Y26, M26, "")}/(H{r}*1000))', f_bold, fmt=NUM2, fill=fill_con)
put(ws, r, 12, f'=IF(H{r}=0,"",{TSUM("R", Y26, M26, "")}/(H{r}*1000))', f_bold, fmt=NUM2, fill=fill_con)
put(ws, r, 15, '=' + TSUM('R', Y26, M26, '') + MB, f_bold, fmt=NUM0, fill=fill_con)
for c in (2, 3, 4, 10, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23): put(ws, r, c, None, fill=fill_con)
r += 2
for n in ['Notes', 'Volume columns use the period criteria in hidden rows 4–5; every other column is YTD Sep-26 (I4:I5).',
          'TDC direct rows: GP per kg = TDC product GP (NS − AF − F&I) and full GP (− idle − other adj − PPA) on TDC\'s invoice to the customer; no TWIN layer, so Combined = TDC.',
          'Via-TWIN rows: TWIN GP = TWIN NS − landed COGS; TDC GP = allocated rate of the same product/quarter (Data cols AQ/AR); Combined = TWIN + TDC. Rows without an SN (e.g. pregel, D2201) have no TDC layer.',
          'Benchmarks compare the same SN: Non-Indonesia = TDC sales to every customer outside Indonesia (domestic Thailand + other exports); Total TDC = all customers incl. Indonesia direct and TWIN intercompany. Gap = Indonesia combined − Total TDC benchmark (product and full GP per kg); negative (red) = Indonesia earns less per kg than TDC overall, positive (green) = earns more.',
          'Via TWIN: customers that together make up the top 80% of YTD Sep-26 volume are listed individually; the others are summed in "The rest" with their breakdown underneath (rows grouped, use the outline buttons to collapse). FY2024 volume column is hidden (outline group on column E).',
          'Group tags (Heinz / Wings) appear in the Channel column; a tag shared by several customers (Wings) is shown as one line per product (SUMIFS on Data col H). Customers are ranked by YTD Sep-26 volume, lines of the same customer kept together. Row set = customers whose source country is Indonesia (Data col BC), so Philippines / China / Singapore / Dubai customers of TWIN are excluded.']:
    put(ws, r, 1, n, f_bold if n == 'Notes' else f_grey); r += 1
for c in (10, 11, 12, 13, 14, 17, 18, 20, 21): traffic(ws, f'{L(c)}{HR+1}:{L(c)}{g_tot}', 0, 2, 5)
# gap = Indonesia − benchmark: negative = Indonesia earns less per kg than TDC overall (red), positive = earns more (green)
ws.conditional_formatting.add(f'V{HR+1}:W{g_tot}', CellIsRule(operator='lessThan', formula=['-1'], fill=PatternFill('solid', fgColor=RED)))
ws.conditional_formatting.add(f'V{HR+1}:W{g_tot}', CellIsRule(operator='greaterThan', formula=['1'], fill=PatternFill('solid', fgColor=GRN)))
widths(ws, {'A': 40, 'B': 14, 'C': 8, 'D': 16})
for c in range(5, 24): ws.column_dimensions[L(c)].width = 10
ws.column_dimensions['V'].width = 12; ws.column_dimensions['W'].width = 12
ws.column_dimensions['E'].hidden = True; ws.column_dimensions.group('E', 'E', hidden=True, outline_level=1)  # FY2024 volume kept but hidden (Por's layout)
ws.freeze_panes = f'E{HR + 1}'

# =====================================================================
# CEO SUMMARY — Indonesia: by channel / by customer / by product (SN), two channels side by side
# =====================================================================
PF = "'Indonesia portfolio'!"
ws = wb.create_sheet('CEO summary', 3); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 85
put(ws, 1, 1, 'Indonesia — CEO summary: TDC direct export vs TDC → TWIN → customers · YTD Sep-25 vs YTD Sep-26 (THB, reported FX)' + EXNOTE, f_title)
put(ws, 2, 1, 'GP = full cost, whole chain (TDC direct: TDC invoice GP; via TWIN: TWIN GP + TDC GP allocated) · benchmark = Total TDC full GP/kg on the same SN mix (all customers, YTD Sep-26) · Gap = Indonesia − benchmark (negative/red = Indonesia earns less per kg) · all formulas (Data / Data TDC SN / Indonesia portfolio)', f_sub)
Y25c, M25c = '"2025"', '"<=9"'
exD = f',{TS("E")},"Indonesia direct"'; exT = f',{D("BC")},"Indonesia"'
def d_t(per, ex=''): return TSUM('I', *per, exD + ex)
def d_ns(per, ex=''): return TSUM('J', *per, exD + ex)
def d_gp(per, ex=''): return TSUM('R', *per, exD + ex)
def t_t(per, ex=''): return SUMIFS('t', per[0], per[1], '"*"', exT + ex)
def t_ns(per, ex=''): return SUMIFS('ns', per[0], per[1], '"*"', exT + ex)
def t_gp(per, ex=''): return SUMIFS('chain_fgp', per[0], per[1], '"*"', exT + ex)
P25 = (Y25c, M25c); P26 = ('"2026"', '"<=9"')   # literal criteria (Y26/M26 point to cells on the portfolio sheet)
HDR = ['', 'Channel', 'Vol YTD Sep-25 (t)', 'Vol YTD Sep-26 (t)', 'YoY vol %', 'NS YTD26 (THB m)', 'GP YTD25 (THB m)', 'GP YTD26 (THB m)', 'GP/kg YTD25', 'GP/kg YTD26', 'Non-Indonesia Vol (t)', 'Non-Indonesia GP/kg', 'Total TDC Vol (t)', 'Total TDC GP/kg', 'Gap vs Non-Indonesia', 'Gap vs Total TDC']
def header(r, first):
    put(ws, r, 1, first, f_hdr, fill=fill_hdr, border=b_hdr)
    for j, h in enumerate(HDR[1:]):
        c = 2 + j
        put(ws, r, c, h, f_hdr, fill=(fill_rep if 3 <= c <= 10 else (fill_con if c in (11, 12, 13, 14) else (fill_fx if c in (15, 16) else fill_hdr))), align=CENTER, border=Border(bottom=med, left=thin if c in (3, 6, 9, 11, 13, 15) else None))
    ws.row_dimensions[r].height = 32
def kpi_row(r, label, chan, t25, t26, ns26, gp25, gp26, bench_ref, bold=False, fill=None, grey=False, bench_ni=None, vol_ni=None, vol_tdc=None):
    fnt = f_bold if bold else (f_grey if grey else f_norm)
    put(ws, r, 1, label, fnt, fill=fill); put(ws, r, 2, chan, f_grey, fill=fill)
    put(ws, r, 3, '=' + t25, fnt, fmt=NUM0, fill=fill, border=Border(left=thin)); put(ws, r, 4, '=' + t26, fnt, fmt=NUM0, fill=fill)
    put(ws, r, 5, f'=IF(C{r}=0,"",D{r}/C{r}-1)', f_grey, fmt=PCT, fill=fill)
    put(ws, r, 6, '=' + ns26 + MB, fnt, fmt=NUM0, fill=fill, border=Border(left=thin))
    put(ws, r, 7, '=' + gp25 + MB, fnt, fmt=NUM1, fill=fill); put(ws, r, 8, '=' + gp26 + MB, fnt, fmt=NUM1, fill=fill)
    put(ws, r, 9, f'=IF(C{r}=0,"",G{r}*1000/C{r})', fnt, fmt=NUM2, fill=fill, border=Border(left=thin)); put(ws, r, 10, f'=IF(D{r}=0,"",H{r}*1000/D{r})', fnt, fmt=NUM2, fill=fill)
    put(ws, r, 11, vol_ni, fnt, fmt=NUM0, fill=fill, border=Border(left=thin)); put(ws, r, 12, bench_ni, fnt, fmt=NUM2, fill=fill)
    put(ws, r, 13, vol_tdc, fnt, fmt=NUM0, fill=fill, border=Border(left=thin)); put(ws, r, 14, bench_ref, fnt, fmt=NUM2, fill=fill)
    put(ws, r, 15, f'=IF(OR(J{r}="",L{r}=""),"",J{r}-L{r})', fnt, fmt=NUM2, fill=fill, border=Border(left=thin)); put(ws, r, 16, f'=IF(OR(J{r}="",N{r}=""),"",J{r}-N{r})', fnt, fmt=NUM2, fill=fill)
def wavg(col, rows_):
    r0_, r1_ = rows_[0], rows_[-1]
    return f'=IF(SUMPRODUCT(--ISNUMBER({col}{r0_}:{col}{r1_}),D{r0_}:D{r1_})=0,"",SUMPRODUCT(--ISNUMBER({col}{r0_}:{col}{r1_}),{col}{r0_}:{col}{r1_},D{r0_}:D{r1_})/SUMPRODUCT(--ISNUMBER({col}{r0_}:{col}{r1_}),D{r0_}:D{r1_}))'
# ---- A. by channel
r = 4; put(ws, r, 1, 'A. By channel', f_sec); r += 1
header(r, 'Channel'); r += 1; a0 = r
ROWA = {}
kpi_row(r, 'TDC direct export to Indonesian customers', 'TDC → customer', d_t(P25), d_t(P26), d_ns(P26), d_gp(P25), d_gp(P26), None); ROWA['direct'] = r; r += 1
kpi_row(r, 'TDC → TWIN → Indonesian customers', 'TDC → TWIN → customer', t_t(P25), t_t(P26), t_ns(P26), t_gp(P25), t_gp(P26), None); ROWA['twin'] = r; r += 1
kpi_row(r, 'Total Indonesia', 'both', f'C{ROWA["direct"]}+C{ROWA["twin"]}', f'D{ROWA["direct"]}+D{ROWA["twin"]}', f'(F{ROWA["direct"]}+F{ROWA["twin"]})*1000000', f'(G{ROWA["direct"]}+G{ROWA["twin"]})*1000000', f'(H{ROWA["direct"]}+H{ROWA["twin"]})*1000000', None, bold=True, fill=fill_tot); ROWA['total'] = r; r += 1
exN = f',{TS("E")},"Non-Indonesia"'
kpi_row(r, 'Reference: TDC Non-Indonesia (all other customers)', 'TDC → customer', TSUM('I', *P25, exN), TSUM('I', *P26, exN), TSUM('J', *P26, exN), TSUM('R', *P25, exN), TSUM('R', *P26, exN), None, grey=True); ROWA['nonindo'] = r; r += 1
kpi_row(r, 'Reference: Total TDC (all customers)', 'TDC', TSUM('I', *P25, ''), TSUM('I', *P26, ''), TSUM('J', *P26, ''), TSUM('R', *P25, ''), TSUM('R', *P26, ''), None, grey=True); ROWA['tdc'] = r; r += 1
# ---- B. by customer
r += 1; put(ws, r, 1, 'B. By customer (customer level; Wings = 3 customers under one tag; The rest = TWIN customers below the top-80% volume line)', f_sec); r += 1
header(r, 'Customer'); r += 1; b0 = r
dir_rows = []
for cust in dcusts:
    key = 'direct:' + cust
    if key not in port_rows: continue
    pr = port_rows[key]; ex = f',{TS("F")},"{cust}"'
    kpi_row(r, cust, 'TDC → customer', d_t(P25, ex), d_t(P26, ex), d_ns(P26, ex), d_gp(P25, ex), d_gp(P26, ex), f'={PF}U{pr}', bench_ni=f'={PF}R{pr}', vol_ni=f'={PF}P{pr}', vol_tdc=f'={PF}S{pr}'); dir_rows.append(r); r += 1
kpi_row(r, 'Subtotal — TDC direct', 'TDC → customer', d_t(P25), d_t(P26), d_ns(P26), d_gp(P25), d_gp(P26), wavg('N', dir_rows), bold=True, fill=fill_tot, bench_ni=wavg('L', dir_rows)); bsub_d = r; r += 1
twin_rows = []
for ent in ents:
    if ent not in top_set: continue
    pr = port_rows['twin:' + ent]
    d0 = next(d for (e, _), d in lines if e == ent)
    if d0['grp']: ex = f',{D("H")},"{ent}"'; label = f"{ent} group ({' / '.join(sorted(tag_members[ent]))})"
    else: ex = f',{D("E")},"{ent}"'; label = ent
    kpi_row(r, label, 'TDC → TWIN → customer', t_t(P25, ex), t_t(P26, ex), t_ns(P26, ex), t_gp(P25, ex), t_gp(P26, ex), f'={PF}U{pr}', bench_ni=f'={PF}R{pr}', vol_ni=f'={PF}P{pr}', vol_tdc=f'={PF}S{pr}'); twin_rows.append(r); r += 1
if rest_ents:
    tr0, tr1 = twin_rows[0], twin_rows[-1]
    kpi_row(r, f'The rest — {len(rest_ents)} smaller TWIN customers', 'TDC → TWIN → customer', f'{t_t(P25)}-SUM(C{tr0}:C{tr1})', f'{t_t(P26)}-SUM(D{tr0}:D{tr1})', f'({t_ns(P26)}-SUM(F{tr0}:F{tr1})*1000000)', f'({t_gp(P25)}-SUM(G{tr0}:G{tr1})*1000000)', f'({t_gp(P26)}-SUM(H{tr0}:H{tr1})*1000000)', f'={PF}U{port_rows["REST"]}', bench_ni=f'={PF}R{port_rows["REST"]}'); twin_rows.append(r); r += 1   # benchmark volume left blank: summing SN volumes across 56 customers would double count
kpi_row(r, 'Subtotal — via TWIN', 'TDC → TWIN → customer', t_t(P25), t_t(P26), t_ns(P26), t_gp(P25), t_gp(P26), wavg('N', twin_rows), bold=True, fill=fill_tot, bench_ni=wavg('L', twin_rows)); bsub_t = r; r += 1
kpi_row(r, 'Total Indonesia', 'both', f'C{bsub_d}+C{bsub_t}', f'D{bsub_d}+D{bsub_t}', f'(F{bsub_d}+F{bsub_t})*1000000', f'(G{bsub_d}+G{bsub_t})*1000000', f'(H{bsub_d}+H{bsub_t})*1000000', f'=IF(D{bsub_d}+D{bsub_t}=0,"",(N{bsub_d}*D{bsub_d}+N{bsub_t}*D{bsub_t})/(D{bsub_d}+D{bsub_t}))', bold=True, fill=fill_rep, bench_ni=f'=IF(D{bsub_d}+D{bsub_t}=0,"",(L{bsub_d}*D{bsub_d}+L{bsub_t}*D{bsub_t})/(D{bsub_d}+D{bsub_t}))'); btot = r; r += 1
# channel benchmarks in section A = the customer-section subtotals (same SN-mix weighting)
for key_, src_, fnt_, fl_ in (('direct', bsub_d, f_norm, None), ('twin', bsub_t, f_norm, None), ('total', btot, f_bold, fill_tot)):
    put(ws, ROWA[key_], 11, f'=D{ROWA["nonindo"]}', fnt_, fmt=NUM0, fill=fl_, border=Border(left=thin)); put(ws, ROWA[key_], 12, f'=L{src_}', fnt_, fmt=NUM2, fill=fl_)
    put(ws, ROWA[key_], 13, f'=D{ROWA["tdc"]}', fnt_, fmt=NUM0, fill=fl_, border=Border(left=thin)); put(ws, ROWA[key_], 14, f'=N{src_}', fnt_, fmt=NUM2, fill=fl_)
for key_ in ('nonindo', 'tdc'):
    put(ws, ROWA[key_], 11, f'=D{ROWA["nonindo"]}', f_grey, fmt=NUM0, border=Border(left=thin)); put(ws, ROWA[key_], 12, f'=J{ROWA["nonindo"]}', f_grey, fmt=NUM2)
    put(ws, ROWA[key_], 13, f'=D{ROWA["tdc"]}', f_grey, fmt=NUM0, border=Border(left=thin)); put(ws, ROWA[key_], 14, f'=J{ROWA["tdc"]}', f_grey, fmt=NUM2)
# ---- C. by product (SN): two channels side by side, each with its own gaps
r += 1; put(ws, r, 1, 'C. By product (SN) — YTD Sep-26, sorted by Indonesia volume · gap = channel GP/kg − benchmark (same SN)', f_sec); r += 1
grp = [(1, 2, 'Product', fill_hdr), (3, 8, 'TDC direct → customer', fill_rep), (9, 14, 'TDC → TWIN → customer', fill_rep), (15, 19, 'Total Indonesia', fill_tot), (20, 23, 'Benchmark same SN, YTD Sep-26 (volume and full GP/kg)', fill_con)]
for c1, c2, lab, fl in grp:
    put(ws, r, c1, lab, f_bold, fill=fl, align=CENTER, border=Border(left=thin))
    if c2 > c1: ws.merge_cells(start_row=r, start_column=c1, end_row=r, end_column=c2)
r += 1
h3 = ['SN', 'Product', 'Vol YTD25 (t)', 'Vol YTD26 (t)', 'GP YTD26 (THB m)', 'GP/kg YTD26', 'Gap vs Non-Indo', 'Gap vs Total TDC',
      'Vol YTD25 (t)', 'Vol YTD26 (t)', 'GP YTD26 (THB m)', 'GP/kg YTD26', 'Gap vs Non-Indo', 'Gap vs Total TDC',
      'Vol YTD26 (t)', 'GP YTD26 (THB m)', 'GP/kg YTD26', 'Gap vs Non-Indo', 'Gap vs Total TDC', 'Non-Indonesia Vol (t)', 'Non-Indonesia GP/kg', 'Total TDC Vol (t)', 'Total TDC GP/kg']
GAPC = (7, 8, 13, 14, 18, 19)
for j, h in enumerate(h3):
    c = 1 + j
    put(ws, r, c, h, f_hdr, fill=(fill_fx if c in GAPC else (fill_con if c in (20, 21, 22, 23) else fill_hdr)), align=CENTER, border=Border(bottom=med, left=thin if c in (1, 3, 7, 9, 13, 15, 18, 20, 22) else None))
ws.row_dimensions[r].height = 32; r += 1; c0r = r
snvol = {}; snname = {}
for x in tsn:
    if x['segment'] == 'Indonesia direct' and x['year'] == '2026': snvol[x['sn']] = snvol.get(x['sn'], 0) + float(x['tons'])
    snname[x['sn']] = x['trade_name']
for x in rows:
    if x.get('country_src', x['country']) == 'Indonesia' and x['sn'] and x['y'] == '2026': snvol[x['sn']] = snvol.get(x['sn'], 0) + x['t']
def gap_pair(r, kgcol, c_ni, c_tdc):
    put(ws, r, c_ni, f'=IF(OR({kgcol}{r}="",U{r}=""),"",{kgcol}{r}-U{r})', f_bold, fmt=NUM2, border=Border(left=thin))
    put(ws, r, c_tdc, f'=IF(OR({kgcol}{r}="",W{r}=""),"",{kgcol}{r}-W{r})', f_bold, fmt=NUM2)
for sn in sorted(snvol, key=lambda k: -snvol[k]):
    if snvol[sn] < 1: continue
    put(ws, r, 1, sn, f_bold); put(ws, r, 2, snname.get(sn, ''), f_grey)
    exs = f',{TS("G")},"{sn}"'; ext2 = f',{D("L")},"{sn}"'
    put(ws, r, 3, '=' + d_t(P25, exs), fmt=NUM0, border=Border(left=thin)); put(ws, r, 4, '=' + d_t(P26, exs), fmt=NUM0)
    put(ws, r, 5, '=' + d_gp(P26, exs) + MB, fmt=NUM1); put(ws, r, 6, f'=IF(D{r}<1,"",E{r}*1000/D{r})', f_bold, fmt=NUM2)
    gap_pair(r, 'F', 7, 8)
    put(ws, r, 9, '=' + t_t(P25, ext2), fmt=NUM0, border=Border(left=thin)); put(ws, r, 10, '=' + t_t(P26, ext2), fmt=NUM0)
    put(ws, r, 11, '=' + t_gp(P26, ext2) + MB, fmt=NUM1); put(ws, r, 12, f'=IF(J{r}<1,"",K{r}*1000/J{r})', f_bold, fmt=NUM2)
    gap_pair(r, 'L', 13, 14)
    put(ws, r, 15, f'=D{r}+J{r}', fmt=NUM0, fill=fill_tot, border=Border(left=thin)); put(ws, r, 16, f'=E{r}+K{r}', fmt=NUM1, fill=fill_tot); put(ws, r, 17, f'=IF(O{r}<1,"",P{r}*1000/O{r})', f_bold, fmt=NUM2, fill=fill_tot)
    gap_pair(r, 'Q', 18, 19)
    exn_ = f',{TS("G")},"{sn}",{TS("E")},"Non-Indonesia"'
    put(ws, r, 20, '=' + TSUM('I', *P26, exn_), fmt=NUM0, border=Border(left=thin)); put(ws, r, 21, f'=IF(T{r}=0,"",{TSUM("R", *P26, exn_)}/(T{r}*1000))', fmt=NUM2)
    put(ws, r, 22, '=' + TSUM('I', *P26, exs), fmt=NUM0, border=Border(left=thin)); put(ws, r, 23, f'=IF(V{r}=0,"",{TSUM("R", *P26, exs)}/(V{r}*1000))', fmt=NUM2)
    r += 1
c1r = r - 1
put(ws, r, 1, 'Total (TDC SNs sold into Indonesia)', f_bold, fill=fill_tot); put(ws, r, 2, None, fill=fill_tot)
for c in (3, 4, 5, 9, 10, 11, 15, 16): put(ws, r, c, f'=SUM({L(c)}{c0r}:{L(c)}{c1r})', f_bold, fmt=(NUM1 if c in (5, 11, 16) else NUM0), fill=fill_tot, border=Border(left=thin) if c in (3, 9, 15) else None)
put(ws, r, 6, f'=IF(D{r}=0,"",E{r}*1000/D{r})', f_bold, fmt=NUM2, fill=fill_tot); put(ws, r, 12, f'=IF(J{r}=0,"",K{r}*1000/J{r})', f_bold, fmt=NUM2, fill=fill_tot); put(ws, r, 17, f'=IF(O{r}=0,"",P{r}*1000/O{r})', f_bold, fmt=NUM2, fill=fill_tot)
for c in (20, 22): put(ws, r, c, f'=SUM({L(c)}{c0r}:{L(c)}{c1r})', f_bold, fmt=NUM0, fill=fill_tot, border=Border(left=thin))
for c, col in ((21, 'U'), (23, 'W')):
    put(ws, r, c, f'=IF(SUMPRODUCT(--ISNUMBER({col}{c0r}:{col}{c1r}),O{c0r}:O{c1r})=0,"",SUMPRODUCT(--ISNUMBER({col}{c0r}:{col}{c1r}),{col}{c0r}:{col}{c1r},O{c0r}:O{c1r})/SUMPRODUCT(--ISNUMBER({col}{c0r}:{col}{c1r}),O{c0r}:O{c1r}))', f_bold, fmt=NUM2, fill=fill_tot)
# channel-level benchmarks on the total row weighted by that channel's own SN volume
for kgcol, volcol, c_ni, c_tdc in (('F', 'D', 7, 8), ('L', 'J', 13, 14), ('Q', 'O', 18, 19)):
    for c, bcol in ((c_ni, 'U'), (c_tdc, 'W')):
        w_ = f'SUMPRODUCT(--ISNUMBER({bcol}{c0r}:{bcol}{c1r}),{volcol}{c0r}:{volcol}{c1r})'
        put(ws, r, c, f'=IF(OR({kgcol}{r}="",{w_}=0),"",{kgcol}{r}-SUMPRODUCT(--ISNUMBER({bcol}{c0r}:{bcol}{c1r}),{bcol}{c0r}:{bcol}{c1r},{volcol}{c0r}:{volcol}{c1r})/{w_})', f_bold, fmt=NUM2, fill=fill_tot, border=Border(left=thin) if c == c_ni else None)
ctot = r; r += 2
put(ws, r, 1, "Notes: via-TWIN products without a TDC SN (pregel, D2201) are in sections A/B but not in C · GP YTD25 for 'The rest' = via-TWIN subtotal − listed customers · benchmarks in A/B = volume sold outside Indonesia (or total TDC) of the same SN mix and its full GP/kg, weighted by each customer's SN mix (from Indonesia portfolio); in A the volumes are the whole Non-Indonesia / Total TDC book; aggregated rows (The rest, subtotals) show no benchmark volume because the same SN would be counted once per customer · gaps in C per channel = that channel's GP/kg − the same-SN benchmark; on the Total row the benchmark is weighted by that channel's own SN volumes · YoY compares Jan–Sep of both years", f_grey)
for rr in list(range(a0, ROWA['tdc'] + 1)) + list(range(b0, btot + 1)): traffic(ws, f'I{rr}:J{rr}', 0, 2, 5)
traffic(ws, f'F{c0r}:F{ctot}', 0, 2, 5); traffic(ws, f'L{c0r}:L{ctot}', 0, 2, 5); traffic(ws, f'Q{c0r}:Q{ctot}', 0, 2, 5)
for rng in (f'O{a0}:P{btot}', f'G{c0r}:H{ctot}', f'M{c0r}:N{ctot}', f'R{c0r}:S{ctot}'):
    ws.conditional_formatting.add(rng, CellIsRule(operator='lessThan', formula=['-1'], fill=PatternFill('solid', fgColor=RED)))
    ws.conditional_formatting.add(rng, CellIsRule(operator='greaterThan', formula=['1'], fill=PatternFill('solid', fgColor=GRN)))
widths(ws, {'A': 46, 'B': 22})
for c in range(3, 24): ws.column_dimensions[L(c)].width = 10.5
ws.freeze_panes = 'C4'
ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.print_area = f'A1:W{r}'

# ---------- apply Por's manual format profile (memory/twin-format-profile.json) ----------
import os as _os
_pp = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'memory', 'twin-format-profile.json')
if _os.path.exists(_pp):
    from openpyxl.styles.colors import Color
    prof = json.load(open(_pp, encoding='utf-8'))
    for name, sp in prof['sheets'].items():
        if name not in wb.sheetnames: continue
        ws = wb[name]
        if sp.get('columns'):
            # reset builder's own groups, then apply Por's
            for k, v in list(ws.column_dimensions.items()):
                v.outline_level = 0; v.hidden = False; v.collapsed = False
            for k, v in sp['columns'].items():
                cd = ws.column_dimensions[k]
                cd.outline_level = v['level']; cd.hidden = v['hidden']; cd.collapsed = v['collapsed']
                if v.get('width'): cd.width = v['width']
            ws.sheet_properties.outlinePr.summaryBelow = sp['outline']['summaryBelow']; ws.sheet_properties.outlinePr.summaryRight = sp['outline']['summaryRight']
        for r in range(1, ws.max_row + 1):
            c = ws.cell(row=r, column=1)
            if c.value and str(c.value) in sp.get('colA_fills', {}):
                f = sp['colA_fills'][str(c.value)]
                c.fill = PatternFill('solid', fgColor=Color(theme=f['theme'], tint=f['tint'])) if 'theme' in f else PatternFill('solid', fgColor=f['rgb'])
        if sp.get('freeze'): ws.freeze_panes = sp['freeze']
        if sp.get('zoom'): ws.sheet_view.zoomScale = sp['zoom']
    print('format profile applied from', prof.get('_source'))
wb.save(OUT)
print('saved', OUT, 'data rows', N, 'rate keys', len(keys))
