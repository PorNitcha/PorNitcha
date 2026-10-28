# Adds 'Data TDC cust-rx' (customer x reaction, YTD Sep-26, all TDC customers) and 'Indonesia tier & strategy' (formulas)
# to a copy of Por's master file WITHOUT touching other sheets.  Usage: python add_tier_sheet.py <src.xlsx> <csv dir> <out.xlsx>
import sys, csv, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import CellIsRule
src, S, out = sys.argv[1], sys.argv[2], sys.argv[3]
wb = openpyxl.load_workbook(src)
F = 'Arial'
f_norm = Font(name=F, size=9); f_bold = Font(name=F, size=9, bold=True); f_hdr = Font(name=F, size=9, bold=True, color='404040')
f_title = Font(name=F, size=12, bold=True); f_sub = Font(name=F, size=9, italic=True, color='7F7F7F'); f_grey = Font(name=F, size=9, color='7F7F7F'); f_sec = Font(name=F, size=10, bold=True, color='1F3864'); f_in = Font(name=F, size=9, color='0000FF')
fill_hdr = PatternFill('solid', fgColor='F2F2F2'); fill_tot = PatternFill('solid', fgColor='F2F2F2'); fill_in = PatternFill('solid', fgColor='FFF2CC'); fill_rep = PatternFill('solid', fgColor='DDEBF7'); fill_con = PatternFill('solid', fgColor='E2EFDA'); fill_fx = PatternFill('solid', fgColor='FFF2CC')
RED, AMB, GRN = 'F1C7C7', 'FBF0C6', 'E2EFDA'
thin = Side(style='thin', color='BFBFBF'); med = Side(style='medium', color='808080')
NUM0 = '#,##0;[Red]-#,##0;-'; NUM1 = '#,##0.0;[Red]-#,##0.0;-'; NUM2 = '#,##0.00;[Red]-#,##0.00;-'; PCT = '0%;[Red]-0%;-'
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True); WRAP = Alignment(wrap_text=True, vertical='top')
def put(ws, r, c, v, font=f_norm, fmt=None, fill=None, align=None, border=None):
    cell = ws.cell(row=r, column=c, value=v); cell.font = font
    if fmt: cell.number_format = fmt
    if fill: cell.fill = fill
    if align: cell.alignment = align
    if border: cell.border = border
    return cell
for nm in ('Data TDC cust-rx', 'Indonesia tier & strategy'):
    if nm in wb.sheetnames: del wb[nm]
# ---------------- data sheet ----------------
rows = list(csv.DictReader(open(f'{S}/tdc_cust_rx.csv', encoding='utf-8')))
wd = wb.create_sheet('Data TDC cust-rx')
hdr = ['reaction', 'customer', 'country', 'indonesia', 'tons_ytd26', 'ns_thb', 'product_cost', 'idle_ppa_adj', 'product_gp', 'full_gp', 'product_gp_kg', 'full_gp_kg', 'ge5t']
for j, h in enumerate(hdr): put(wd, 1, 1 + j, h, f_hdr, fill=fill_hdr)
for i, x in enumerate(rows):
    r = 2 + i
    put(wd, r, 1, x['reaction']); put(wd, r, 2, x['customer']); put(wd, r, 3, x['country']); put(wd, r, 4, int(x['indonesia']))
    put(wd, r, 5, float(x['tons_ytd26']), f_in, fmt=NUM2); put(wd, r, 6, float(x['ns_thb']), f_in, fmt=NUM0); put(wd, r, 7, float(x['product_cost']), f_in, fmt=NUM0); put(wd, r, 8, float(x['idle_ppa_adj']), f_in, fmt=NUM0)
    put(wd, r, 9, f'=F{r}-G{r}', fmt=NUM0); put(wd, r, 10, f'=I{r}-H{r}', fmt=NUM0)
    put(wd, r, 11, f'=IF(E{r}=0,"",I{r}/(E{r}*1000))', fmt=NUM2); put(wd, r, 12, f'=IF(E{r}=0,"",J{r}/(E{r}*1000))', fmt=NUM2); put(wd, r, 13, f'=IF(E{r}>=5,1,0)')
N = len(rows) + 1
wd.freeze_panes = 'C2'; wd.auto_filter.ref = f'A1:M{N}'
for c in range(1, 14): wd.column_dimensions[L(c)].width = 12
wd.column_dimensions['B'].width = 44
put(wd, 1, 15, 'Source: TDC Profitability data_Actual, Year 2026 (Jan–Sep), all customers, by Customer name (Group) × Reaction group. product_gp = NS − Actual Cost (AF) − F&I (HVA definition); full_gp = product_gp − idle − other adj − PPA. indonesia = 1 for Country = Indonesia or PT THAI WAH INDONESIA (intercompany). ge5t = customers with ≥ 5 t (used for ranking).', f_grey)
def D(col): return f"'Data TDC cust-rx'!${col}$2:${col}${N}"
# ---------------- tier & strategy sheet ----------------
ws = wb.create_sheet('Indonesia tier & strategy')
ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 85
put(ws, 1, 1, 'Indonesia in the HVA GP/kg tiers — where Indonesian accounts sit within each reaction, and whether volume leverages fixed cost', f_title)
put(ws, 2, 1, "YTD Sep-26 · product GP/kg = NS − Actual Cost (AF) − F&I (same basis as the HVA GP tier tracker) · floor / target per reaction from HVA_build tier10.py · capacity t/month from the TWIN file sheet Data (Baseline) — CONFIRM WITH PLANT · all figures are formulas over 'Data TDC cust-rx'", f_sub)
# inputs
RX = ['PO-XL', 'XL', 'PO', 'AC', 'MX', 'Others']
FLOOR = {'PO-XL': 4.0, 'XL': 2.0, 'PO': 4.0, 'AC': 7.0, 'MX': 3.0, 'Others': 4.0}; TLO = {'PO-XL': 6.0, 'XL': 3.2, 'PO': 5.5, 'AC': 9.5, 'MX': 4.0, 'Others': 6.0}
CAP = {'PO-XL': 2000, 'XL': 750, 'PO': 800, 'AC': 250, 'MX': 300, 'Others': 600}
put(ws, 4, 1, 'Inputs (yellow = editable)', f_sec)
put(ws, 5, 1, 'Months in period', f_norm); put(ws, 5, 2, 9, f_in, fill=fill_in)
put(ws, 6, 1, 'Min tonnes for a customer to be ranked', f_norm); put(ws, 6, 2, 5, f_in, fill=fill_in)
MONTHS, MINT = '$B$5', '$B$6'
# ---- A. by reaction ----
r = 8; put(ws, r, 1, 'A. By reaction — Indonesia share, GP/kg vs the rest, fixed-cost leverage and utilisation', f_sec); r += 1
hA = ['Reaction', 'Floor GP/kg', 'Target GP/kg', 'Capacity t/month', 'TDC tons YTD26', 'Indonesia tons', 'Indonesia share', 'Product GP/kg all', 'Product GP/kg Indonesia', 'Product GP/kg non-Indonesia', 'Idle+PPA+adj THB/kg', 'Utilisation', 'Below-floor tons (all)', 'of which Indonesia', 'Indonesia share of below-floor', 'Verdict']
for j, h in enumerate(hA): put(ws, r, 1 + j, h, f_hdr, fill=(fill_in if 2 <= 1 + j <= 4 else (fill_con if 11 <= 1 + j <= 12 else (fill_fx if 1 + j >= 13 else fill_hdr))), align=CENTER, border=Border(bottom=med, left=thin if (1 + j) in (2, 5, 8, 11, 13, 16) else None))
ws.row_dimensions[r].height = 42; r += 1; a0 = r
for g in RX:
    put(ws, r, 1, g, f_bold); put(ws, r, 2, FLOOR[g], f_in, fmt=NUM1, fill=fill_in); put(ws, r, 3, TLO[g], f_in, fmt=NUM1, fill=fill_in); put(ws, r, 4, CAP[g], f_in, fmt=NUM0, fill=fill_in)
    rx = f',{D("A")},$A{r}'
    put(ws, r, 5, f'=SUMIFS({D("E")}{rx})', fmt=NUM0, border=Border(left=thin)); put(ws, r, 6, f'=SUMIFS({D("E")}{rx},{D("D")},1)', fmt=NUM0); put(ws, r, 7, f'=IF(E{r}=0,"",F{r}/E{r})', fmt=PCT)
    put(ws, r, 8, f'=IF(E{r}=0,"",SUMIFS({D("I")}{rx})/(E{r}*1000))', f_bold, fmt=NUM2, border=Border(left=thin))
    put(ws, r, 9, f'=IF(F{r}=0,"",SUMIFS({D("I")}{rx},{D("D")},1)/(F{r}*1000))', f_bold, fmt=NUM2)
    put(ws, r, 10, f'=IF(E{r}-F{r}=0,"",SUMIFS({D("I")}{rx},{D("D")},0)/((E{r}-F{r})*1000))', f_bold, fmt=NUM2)
    put(ws, r, 11, f'=IF(E{r}=0,"",SUMIFS({D("H")}{rx})/(E{r}*1000))', fmt=NUM2, border=Border(left=thin)); put(ws, r, 12, f'=IF(D{r}*{MONTHS}=0,"",E{r}/(D{r}*{MONTHS}))', f_bold, fmt=PCT)
    put(ws, r, 13, f'=SUMIFS({D("E")}{rx},{D("K")},"<"&$B{r})', fmt=NUM0, border=Border(left=thin)); put(ws, r, 14, f'=SUMIFS({D("E")}{rx},{D("K")},"<"&$B{r},{D("D")},1)', fmt=NUM0); put(ws, r, 15, f'=IF(M{r}=0,"",N{r}/M{r})', fmt=PCT)
    put(ws, r, 16, f'=IF(F{r}<5,"n/a",IF(L{r}>=0.8,"Capacity constrained ("&TEXT(L{r},"0%")&") — Indonesia volume displaces "&TEXT(J{r},"0.0")&" THB/kg business: price to market, no volume game",IF(I{r}<B{r},"Spare capacity ("&TEXT(L{r},"0%")&") — volume helps absorb fixed cost, but Indonesia is below the "&TEXT(B{r},"0.0")&" floor: floor price, not open-ended discount","Spare capacity ("&TEXT(L{r},"0%")&") — above floor, volume game acceptable")))', f_norm, align=WRAP, border=Border(left=thin))
    ws.row_dimensions[r].height = 30; r += 1
a1 = r - 1
put(ws, r, 1, 'Total', f_bold, fill=fill_tot)
for c in (5, 6, 13, 14): put(ws, r, c, f'=SUM({L(c)}{a0}:{L(c)}{a1})', f_bold, fmt=NUM0, fill=fill_tot)
put(ws, r, 7, f'=IF(E{r}=0,"",F{r}/E{r})', f_bold, fmt=PCT, fill=fill_tot); put(ws, r, 15, f'=IF(M{r}=0,"",N{r}/M{r})', f_bold, fmt=PCT, fill=fill_tot)
put(ws, r, 8, f'=SUMPRODUCT(H{a0}:H{a1},E{a0}:E{a1})/E{r}', f_bold, fmt=NUM2, fill=fill_tot); put(ws, r, 9, f'=IF(F{r}=0,"",SUMPRODUCT(--ISNUMBER(I{a0}:I{a1}),I{a0}:I{a1},F{a0}:F{a1})/F{r})', f_bold, fmt=NUM2, fill=fill_tot)
put(ws, r, 10, f'=SUMPRODUCT(--ISNUMBER(J{a0}:J{a1}),J{a0}:J{a1},E{a0}:E{a1}-F{a0}:F{a1})/(E{r}-F{r})', f_bold, fmt=NUM2, fill=fill_tot); put(ws, r, 11, f'=SUMPRODUCT(K{a0}:K{a1},E{a0}:E{a1})/E{r}', f_bold, fmt=NUM2, fill=fill_tot)
put(ws, r, 12, f'=E{r}/(SUM(D{a0}:D{a1})*{MONTHS})', f_bold, fmt=PCT, fill=fill_tot)
for c in (2, 3, 4, 16): put(ws, r, c, None, fill=fill_tot)
ws.conditional_formatting.add(f'L{a0}:L{r}', CellIsRule(operator='greaterThanOrEqual', formula=['0.8'], fill=PatternFill('solid', fgColor=RED)))
ws.conditional_formatting.add(f'L{a0}:L{r}', CellIsRule(operator='lessThan', formula=['0.6'], fill=PatternFill('solid', fgColor=GRN)))
r += 2
# ---- B. Indonesian accounts ranked within their reaction ----
put(ws, r, 1, 'B. Indonesian accounts within each reaction — product GP/kg, tier vs floor/target, rank among all TDC customers with ≥ 5 t (1 = lowest)', f_sec); r += 1
hB = ['Reaction', 'Customer', 'Channel', 'Tons YTD26', 'Share of reaction', 'Product GP/kg', 'Full GP/kg', 'Floor', 'Target', 'Tier', 'Rank (1 = lowest)', 'Customers ranked', 'Percentile', 'Gap to floor THB/kg', 'THB m to reach floor']
for j, h in enumerate(hB): put(ws, r, 1 + j, h, f_hdr, fill=(fill_rep if 4 <= 1 + j <= 7 else (fill_fx if 1 + j in (10, 11, 12, 13) else fill_hdr)), align=CENTER, border=Border(bottom=med, left=thin if (1 + j) in (4, 8, 10, 14) else None))
ws.row_dimensions[r].height = 36; r += 1; b0 = r
indo = [x for x in rows if x['indonesia'] == '1' and float(x['tons_ytd26']) >= 1]
order = {g: i for i, g in enumerate(RX)}
indo.sort(key=lambda x: (order.get(x['reaction'], 9), -float(x['tons_ytd26'])))
for x in indo:
    g = x['reaction']; gi = a0 + RX.index(g)
    put(ws, r, 1, g, f_bold); put(ws, r, 2, x['customer']); put(ws, r, 3, 'TDC → TWIN (intercompany)' if x['customer'] == 'PT THAI WAH INDONESIA' else 'TDC direct', f_grey)
    cr = f',{D("A")},$A{r},{D("B")},$B{r}'
    put(ws, r, 4, f'=SUMIFS({D("E")}{cr})', fmt=NUM0, border=Border(left=thin)); put(ws, r, 5, f'=IF($E${gi}=0,"",D{r}/$E${gi})', fmt=PCT)
    put(ws, r, 6, f'=IF(D{r}=0,"",SUMIFS({D("I")}{cr})/(D{r}*1000))', f_bold, fmt=NUM2); put(ws, r, 7, f'=IF(D{r}=0,"",SUMIFS({D("J")}{cr})/(D{r}*1000))', fmt=NUM2)
    put(ws, r, 8, f'=$B${gi}', fmt=NUM1, border=Border(left=thin)); put(ws, r, 9, f'=$C${gi}', fmt=NUM1)
    put(ws, r, 10, f'=IF(F{r}="","",IF(F{r}<H{r},"Below floor",IF(F{r}<I{r},"Floor to target","At / above target")))', f_bold, border=Border(left=thin))
    put(ws, r, 11, f'=IF(F{r}="","",1+COUNTIFS({D("A")},$A{r},{D("M")},1,{D("K")},"<"&F{r}))', fmt=NUM0); put(ws, r, 12, f'=COUNTIFS({D("A")},$A{r},{D("M")},1)', fmt=NUM0)
    put(ws, r, 13, f'=IF(OR(F{r}="",L{r}=0),"",K{r}/L{r})', fmt=PCT)
    put(ws, r, 14, f'=IF(F{r}="","",F{r}-H{r})', f_bold, fmt=NUM2, border=Border(left=thin)); put(ws, r, 15, f'=IF(F{r}="","",MIN(0,N{r})*D{r}*1000/1000000)', fmt=NUM1)
    r += 1
b1 = r - 1
put(ws, r, 1, 'Total Indonesia', f_bold, fill=fill_tot); put(ws, r, 4, f'=SUM(D{b0}:D{b1})', f_bold, fmt=NUM0, fill=fill_tot)
put(ws, r, 6, f'=IF(D{r}=0,"",SUMPRODUCT(--ISNUMBER(F{b0}:F{b1}),F{b0}:F{b1},D{b0}:D{b1})/D{r})', f_bold, fmt=NUM2, fill=fill_tot); put(ws, r, 7, f'=IF(D{r}=0,"",SUMPRODUCT(--ISNUMBER(G{b0}:G{b1}),G{b0}:G{b1},D{b0}:D{b1})/D{r})', f_bold, fmt=NUM2, fill=fill_tot)
put(ws, r, 10, f'="Below floor: "&TEXT(SUMIFS(D{b0}:D{b1},J{b0}:J{b1},"Below floor")/D{r},"0%")&" of Indonesian tonnes"', f_bold, fill=fill_tot); put(ws, r, 15, f'=SUM(O{b0}:O{b1})', f_bold, fmt=NUM1, fill=fill_tot)
for c in (2, 3, 5, 8, 9, 11, 12, 13, 14): put(ws, r, c, None, fill=fill_tot)
for c in ('F', 'G'):
    ws.conditional_formatting.add(f'{c}{b0}:{c}{b1}', CellIsRule(operator='lessThan', formula=[f'$H{b0}'], fill=PatternFill('solid', fgColor=RED)))
ws.conditional_formatting.add(f'J{b0}:J{b1}', CellIsRule(operator='equal', formula=['"Below floor"'], fill=PatternFill('solid', fgColor=RED)))
ws.conditional_formatting.add(f'J{b0}:J{b1}', CellIsRule(operator='equal', formula=['"Floor to target"'], fill=PatternFill('solid', fgColor=AMB)))
ws.conditional_formatting.add(f'J{b0}:J{b1}', CellIsRule(operator='equal', formula=['"At / above target"'], fill=PatternFill('solid', fgColor=GRN)))
r += 2
# ---- C. what the fixed-cost argument is worth ----
put(ws, r, 1, 'C. Is this a volume game that leverages fixed cost?', f_sec); r += 1
for t in [
 '• The only fixed-cost benefit visible in the profitability file is idle cost + PPA (column K in table A, about 0.6–1.0 THB/kg at current loads); product cost (AF) already carries absorbed overhead. Indonesia\'s price gap to the rest of the book is 3–5 THB/kg, so filling an empty reactor recovers at most a quarter of what the price gives away.',
 '• Where utilisation is low (PO, AC, Others, MX) extra volume genuinely absorbs fixed cost: accept a lower tier, but not below the HVA floor, and switch volume rebates off once utilisation passes ~70%.',
 '• Where the reactor is full (XL above nameplate, PO-XL at ~86%) every Indonesian tonne displaces a tonne that earns 6–7 THB/kg elsewhere: Indonesia must pay the market tier or lose allocation. This is where a volume cap belongs, not across the board.',
 '• XL as a whole sits below its floor (Indonesia is half of it, the rest earns ~2.0): XL is a commodity reaction by nature. Either run it deliberately as a cost-leadership line (debottleneck, cost-down, indexed contracts) or migrate Casstex 22 / Tapbind 321 buyers to differentiated grades.']:
    put(ws, r, 1, t, f_norm, align=WRAP); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=16); ws.row_dimensions[r].height = 30; r += 1
r += 1
put(ws, r, 1, 'D. Strategic / long-term recommendations', f_sec); r += 1
recs = [
 ('1. Two explicit roles for Indonesia', 'Capacity-filler on PO / AC / Others (floor price, rebates tied to utilisation < 70%); market role on XL / PO-XL (same tier as other export customers or lower allocation). Apply any volume cap to XL / PO-XL only.'),
 ('2. Decide what XL is for', 'Half of XL is Indonesia at ~1.6 THB/kg and the rest earns ~2.0, so the reaction is below floor as a whole. Choose: cost-leadership line with long indexed contracts, or migrate Casstex 22 / Tapbind 321 customers to differentiated grades and release the line. Leaving it as is locks ~9,500 t a year into the lowest tier.'),
 ('3. Reposition TWIN as the premium and long-tail channel', 'TWIN adds 5–10 THB/kg on small accounts and premium SNs but destroys value on Heinz and Wings (TWIN margin 0.3 to −0.5). Serve large Cassflo 500 accounts direct with a transfer-price floor; let TWIN grow Cassmax 102 / 26, Amyrose, Cassflo 600 / 800. Target premium share of Indonesian volume from ~7% to 20% by 2028.'),
 ('4. Make the HVA tier floors contractual', 'About 80% of Indonesian direct tonnage is below floor. Renewals carry the reaction floor as the minimum, a USD/IDR indexation clause and volume commitments tied to price tiers; track each account\'s tier quarterly (table B).'),
 ('5. Use concentration as leverage', 'For SN-056, SN-198 and SN-365 Indonesia is 63–100% of TDC volume: no alternative buyer today, but no alternative supplier at that scale for them either. Negotiate the three direct accounts together on a two-year path from ~1.3 to 3 THB/kg rather than one-off increases.'),
 ('Caveat', 'Capacity per reaction comes from the TWIN file sheet Data (Baseline); XL utilisation above 100% suggests that figure is stale — confirm nameplate with the plant before quoting utilisation. TDC GP in the via-TWIN channel is at transfer price (intercompany), not the end-customer price.')]
for h, t in recs:
    put(ws, r, 1, h, f_bold, align=WRAP); put(ws, r, 3, t, f_norm, align=WRAP); ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=16); ws.row_dimensions[r].height = 40; r += 1
ws.column_dimensions['A'].width = 30; ws.column_dimensions['B'].width = 40; ws.column_dimensions['C'].width = 22
for c in range(4, 17): ws.column_dimensions[L(c)].width = 12
ws.column_dimensions['P'].width = 60
ws.freeze_panes = 'A4'
# place the new sheets after 'CEO summary'
order = wb.sheetnames
for nm in ('Indonesia tier & strategy', 'Data TDC cust-rx'):
    sh = wb[nm]; wb._sheets.remove(sh); wb._sheets.insert(order.index('CEO summary') + 1, sh)
wb.save(out); print('saved', out, 'data rows', len(rows), 'indo rows', len(indo))
