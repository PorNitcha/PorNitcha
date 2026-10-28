import json, sys
from collections import defaultdict, OrderedDict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.table import Table, TableStyleInfo

S, OUT = sys.argv[1], sys.argv[2]
M = json.load(open(f'{S}/model.json', encoding='utf-8'))
rows = M['rows']; usdthb = M['usdthb']; idrthb = M['idrthb']; usdidr = M['usdidr']; base = M['base']; fxsrc = M['fxsrc']

# ---------- styles ----------
F = 'Arial'
f_norm = Font(name=F, size=9); f_bold = Font(name=F, size=9, bold=True); f_hdr = Font(name=F, size=9, bold=True, color='404040')
f_title = Font(name=F, size=12, bold=True); f_sub = Font(name=F, size=9, italic=True, color='7F7F7F'); f_grey = Font(name=F, size=9, color='7F7F7F')
fill_hdr = PatternFill('solid', fgColor='F2F2F2'); fill_grp = PatternFill('solid', fgColor='E7E6E6'); fill_tot = PatternFill('solid', fgColor='F2F2F2')
RED, AMB, GRN = 'F1C7C7', 'FBF0C6', 'E2EFDA'
thin = Side(style='thin', color='BFBFBF'); med = Side(style='medium', color='808080')
b_bot = Border(bottom=thin); b_hdr = Border(bottom=med); b_left = Border(left=thin)
NUM0 = '#,##0;[Red]-#,##0;-'; NUM1 = '#,##0.0;[Red]-#,##0.0;-'; NUM2 = '#,##0.00;[Red]-#,##0.00;-'; PCT = '0.0%;[Red]-0.0%;-'; FX4 = '0.0000'; FX6 = '0.000000'
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True); LEFT = Alignment(horizontal='left', vertical='center'); RIGHT = Alignment(horizontal='right')

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

# ---------- periods ----------
PERIODS = [('FY2024', lambda r: r['y'] == '2024'), ('FY2025', lambda r: r['y'] == '2025'),
           ('YTD Sep-25', lambda r: '2025-01' <= r['month'] <= '2025-09'), ('YTD Sep-26', lambda r: r['y'] == '2026')]
QS = sorted(set(r['q'] for r in rows))
def qlabel(qq): return f"Q{qq[-1]}'{qq[2:4]}"
KEYS = ('t','t_tdc','ns','cogs','gp','ns_c','gp_c','tdc_ns','tdc_usd','tdc_pcost','tdc_other','tdc_pgp','tdc_fgp','tdc_ns_c','tdc_pgp_c','tdc_fgp_c',
        'chain_pgp','chain_fgp','chain_pgp_c','chain_fgp_c','fx_tdc','fx_usdidr_thb','fx_idrthb_thb','fx_rev_idr','fx_rev_usd','fx_cogs_usd')
def agg(filt, keyfn):
    d = defaultdict(lambda: defaultdict(float))
    for r in rows:
        if not filt(r): continue
        k = keyfn(r); a = d[k]
        for kk in KEYS:
            if kk == 't_tdc': a[kk] += r['t'] if r['src'] == 'TDC' else 0
            else: a[kk] += r[kk]
    return d
def kg(a): return a['t'] * 1000 if a['t'] else None
def kgt(a): return a['t_tdc'] * 1000 if a['t_tdc'] else None
def div(x, y): return x / y if y else None

wb = Workbook()
EXCL = M.get('excluded') or []
EXNOTE = (' · ไม่รวม ' + ' / '.join(EXCL)) if EXCL else ''

# =============== README ===============
ws = wb.active; ws.title = 'README'
ws.sheet_view.showGridLines = False
lines = [
 ('TWIN (PT Thai Wah Indonesia) — กำไรรายลูกค้า 2 ชั้น: TDC (ผู้ผลิต) + TWIN (trading)', f_title),
 ('จัดทำ 22-Oct-2026 · หน่วย: บาท (THB) และ บาท/กก. · ข้อมูล Jan-2024 → Sep-2026' + EXNOTE, f_sub),
 (('⚠ เวอร์ชันนี้ตัดสินค้า ' + ' / '.join(EXCL) + ' ออกจากทุกชีทตามที่ Por สั่ง (22-Oct-2026) — เวอร์ชันเต็มดู v2') if EXCL else '', f_bold),
 ('', f_norm),
 ('Business model', f_bold),
 ('TDC ผลิต modified starch แล้วขายให้ TWIN (intercompany, invoice USD, CIF) → TWIN ขายต่อให้ลูกค้า: ในอินโดนีเซียเป็น IDR, นอกอินโดนีเซียเป็น USD (บันทึกบัญชีเป็น IDR) · TWIN ยังขายสินค้าที่ไม่ได้มาจาก TDC (native starch, sago, coarse flour, Fibioca, pregel, D2201) ซึ่งกำไรต้นทางไม่อยู่ใน 2 ไฟล์นี้ → แสดงเฉพาะชั้น TWIN', f_norm),
 ('', f_norm),
 ('Source', f_bold),
 ('1) TWIN customer breakdown.xlsx — sheet "TWIN RAWww" (2024, หน่วย กก.) และ "TWIN Raw data" (Jan-25 → Sep-26, หน่วย ตัน) — ตรวจแล้วตรงกัน 100% ช่วง Jan–Aug-25', f_norm),
 ('2) TDC Profitability_Act 2024-2026_Jul2026_AddPPA.xlsx — sheet data_Actual กรองลูกค้า "PT THAI WAH INDONESIA" (Intercompany, USD) 257 บรรทัด', f_norm),
 ('', f_norm),
 ('นิยามกำไร (ต่อ กก.)', f_bold),
 ('• TWIN GP = TWIN net sales − TWIN COGS (COGS = ราคาซื้อจาก TDC/TWPC + landed cost; ตรวจแล้ว ≈ ราคาขาย TDC + 2–5%) — ไม่มี opex ของ TWIN ในไฟล์ จึงไม่มี TWIN full cost', f_norm),
 ('• TDC product GP = TDC net sales (transfer price) − Actual Cost (col AF) − F&I   [นิยามเดียวกับงาน HVA ของ Por]', f_norm),
 ('• TDC full GP = TDC product GP − Idle − PPA − Other Adj   (= Actual Gross Profit ในไฟล์)', f_norm),
 ('• Chain GP = TWIN GP + TDC GP (product หรือ full) = กำไรรวมของกลุ่มจากการขายให้ลูกค้ารายนั้น', f_norm),
 ('• การกระจาย TDC GP ไปรายลูกค้า: TDC ขายให้ TWIN เป็นลูกค้าเดียว ไม่มีราคาแยกตามลูกค้าปลายทาง → ใช้ TDC GP/กก. ของ product นั้นใน "ไตรมาสเดียวกับที่ TWIN ขาย" (ถ่วงน้ำหนักตัน) × ปริมาณที่ TWIN ขายให้ลูกค้า; ถ้าไตรมาสนั้น TDC ไม่มี shipment ใช้ค่าเฉลี่ยปี (คอลัมน์ tdc_basis ใน Data: Q / Y / ALL)', f_norm),
 ('• ผลคือ "TDC GP ที่จัดสรร" ≠ TDC GP จริงตามเดือนที่ส่งของ (stock timing) — ดู reconciliation ในชีท Summary', f_norm),
 ('', f_norm),
 ('FX — 3 ส่วนที่กระทบ (ดูชีท FX)', f_bold),
 ('① USD/THB (ชั้น TDC): TDC ขาย TWIN เป็น USD → บาทแข็งทำให้ยอดขาย/กำไร TDC เป็นบาทลด (ต้นทุนเป็นบาทอยู่แล้ว)', f_norm),
 ('② USD/IDR (ชั้น TWIN — ต้นทุน): TWIN ซื้อเป็น USD ขายเป็น IDR → รูเปียห์อ่อนทำให้ COGS (IDR) สูงขึ้น ถ้าราคาขาย IDR ไม่ขยับตาม margin หด', f_norm),
 ('③ IDR/THB (ชั้น TWIN — translation): กำไร IDR แปลงเป็นบาท → รูเปียห์อ่อนต่อบาททำให้กำไรเป็นบาทลด (ไม่กระทบกำไรในสกุลท้องถิ่น)', f_norm),
 (f"• Constant FX = ตรึงทุกคู่เงินที่ค่าเฉลี่ยปี 2024: USD/THB {base['usdthb']:.2f} · IDR/THB {base['idrthb']:.6f} (= {1/base['idrthb']:.0f} IDR/THB) · USD/IDR {base['usdidr']:.0f}", f_norm),
 ('• อัตรา USD/THB รายเดือน 2025–26 = อัตรา invoice จริงของ TDC (ถ่วงน้ำหนัก) · Mar-25 ใช้ค่าเฉลี่ย Data_Billing · ปี 2024 ไฟล์ TDC ไม่มีอัตรา → ใช้ค่าเฉลี่ยรายเดือน BOT โดยประมาณ (สมมติฐาน — กระทบเฉพาะ constant-FX ของ TDC ปี 2024)', f_norm),
 ('• IDR/THB รายเดือน = อัตราที่ TWIN ใช้ในไฟล์ · USD/IDR = USD/THB ÷ IDR/THB', f_norm),
 ('• สกุลเงินขายของ TWIN: 2024–Aug-25 ตามคอลัมน์ Currency ในไฟล์; Sep-25 เป็นต้นไปไม่มีคอลัมน์ → ถือว่าลูกค้านอกอินโดนีเซีย (จีน/ฟิลิปปินส์/สิงคโปร์/ดูไบ/ไทย) ขายเป็น USD (สมมติฐาน)', f_norm),
 ('', f_norm),
 ('Caveats', f_bold),
 ('• ชื่อลูกค้าในไฟล์ TWIN สะกดหลายแบบ (PT. / ,PT / เว้นวรรค) → รวมด้วยการ normalize ชื่อ · ชื่อที่แสดงคือชื่อแรกที่พบ', f_norm),
 ('• TDC GP ปี 2024 ใน Q1 ติดลบ (Jan-24 cost > price ในไฟล์) · Q1-25 มี waste-water incident ที่ TDC (ไม่ใช่ benchmark ตามที่ Por เคยระบุ)', f_norm),
 ('• ไฟล์ TDC refresh 8-Oct-2026 (ข้อมูลถึง Sep-26) · ไฟล์ TWIN refresh 22-Oct-2026', f_norm),
 ('', f_norm),
 ('Product mapping TWIN → TDC SN', f_bold),
]
r = 1
for txt, fnt in lines:
    put(ws, r, 1, txt, fnt); r += 1
for twin_name, sn in sorted(((v, k) for k, v in M['sn_name'].items())):
    put(ws, r, 1, f'   {twin_name}  ←  {sn}'); r += 1
put(ws, r, 1, '   ไม่ได้มาจาก TDC (ชั้น TWIN เท่านั้น): Native starch, Sago / pearl, Coarse flour, Fibioca, Pregelatinized, D2201, Casstex 31/32, Casstex HF 201, Cassflo 40/880'); r += 1
put(ws, r + 1, 1, 'ชีท: Summary · By customer · By customer-product · Quarterly trend · TDC product rates · FX · Data (pivot-ready)', f_grey)
widths(ws, {'A': 160})

# =============== SUMMARY ===============
ws = wb.create_sheet('Summary'); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 90
put(ws, 1, 1, 'TWIN — ภาพรวมกำไร 2 ชั้น (TDC + TWIN)  ·  ล้านบาท / บาท/กก.' + EXNOTE, f_title)
put(ws, 2, 1, 'คอลัมน์เรียงตามเวลา: รายปี → YTD เทียบ → รายไตรมาส · TDC = เฉพาะสินค้าจาก TDC (จัดสรรตาม product × ไตรมาส)', f_sub)
cols = [(p, lambda r, fn=fn: fn(r)) for p, fn in PERIODS] + [(qlabel(qq), lambda r, qq=qq: r['q'] == qq) for qq in QS]
A = {}
for name, fn in cols:
    a = agg(fn, lambda r: 0)[0]; A[name] = a
hdr_r = 4
put(ws, hdr_r, 1, 'ล้านบาท (ยกเว้นที่ระบุ)', f_hdr, fill=fill_hdr, border=b_hdr)
for j, (name, _) in enumerate(cols):
    put(ws, hdr_r, 2 + j, name, f_hdr, fill=fill_hdr, align=CENTER, border=b_hdr)
mb = 1e6
spec = [
 ('ปริมาณขาย TWIN รวม (ตัน)', lambda a: a['t'], NUM0, True),
 ('   สินค้าจาก TDC (ตัน)', lambda a: a['t_tdc'], NUM0, False),
 ('   สินค้าอื่น native/sago/ฯลฯ (ตัน)', lambda a: a['t'] - a['t_tdc'], NUM0, False),
 ('ชั้น TWIN (trading)', None, None, 'grp'),
 ('TWIN net sales', lambda a: a['ns'] / mb, NUM1, False),
 ('TWIN COGS', lambda a: a['cogs'] / mb, NUM1, False),
 ('TWIN GP', lambda a: a['gp'] / mb, NUM1, True),
 ('TWIN GM %', lambda a: div(a['gp'], a['ns']), PCT, False),
 ('TWIN GP บาท/กก. (ทุกสินค้า)', lambda a: div(a['gp'], kg(a)), NUM2, True),
 ('ชั้น TDC (ผู้ผลิต) — เฉพาะสินค้า TDC, จัดสรรตามที่ TWIN ขาย', None, None, 'grp'),
 ('TDC net sales (transfer price)', lambda a: a['tdc_ns'] / mb, NUM1, False),
 ('TDC product cost (AF + F&I)', lambda a: a['tdc_pcost'] / mb, NUM1, False),
 ('TDC product GP', lambda a: a['tdc_pgp'] / mb, NUM1, True),
 ('Idle + PPA + Other adj', lambda a: a['tdc_other'] / mb, NUM1, False),
 ('TDC full GP', lambda a: a['tdc_fgp'] / mb, NUM1, True),
 ('TDC transfer price บาท/กก.', lambda a: div(a['tdc_ns'], kgt(a)), NUM2, False),
 ('TDC product GP บาท/กก.', lambda a: div(a['tdc_pgp'], kgt(a)), NUM2, True),
 ('TDC full GP บาท/กก.', lambda a: div(a['tdc_fgp'], kgt(a)), NUM2, True),
 ('TWIN GP บาท/กก. (เฉพาะสินค้า TDC)', lambda a: div(sum(r['gp'] for r in rows if r['src'] == 'TDC' and a is A[name] and False) or None, 1), NUM2, False),
 ('รวมทั้ง chain (TWIN + TDC)', None, None, 'grp'),
 ('Chain GP — product basis', lambda a: a['chain_pgp'] / mb, NUM1, True),
 ('Chain GP — full cost basis', lambda a: a['chain_fgp'] / mb, NUM1, True),
 ('Chain GP บาท/กก. — product basis (ทุกตัน)', lambda a: div(a['chain_pgp'], kg(a)), NUM2, False),
 ('Chain GP บาท/กก. — full cost basis (ทุกตัน)', lambda a: div(a['chain_fgp'], kg(a)), NUM2, True),
 ('Chain full GP บาท/กก. — เฉพาะตันสินค้า TDC', lambda a: div(a['chain_fgp'] - (a['gp'] - a['gp_tdc']), kgt(a)) if False else None, NUM2, False),
 ('Constant FX (ตรึงที่ค่าเฉลี่ย 2024)', None, None, 'grp'),
 ('TWIN GP @ constant FX', lambda a: a['gp_c'] / mb, NUM1, False),
 ('TDC product GP @ constant FX', lambda a: a['tdc_pgp_c'] / mb, NUM1, False),
 ('TDC full GP @ constant FX', lambda a: a['tdc_fgp_c'] / mb, NUM1, False),
 ('Chain full GP @ constant FX', lambda a: a['chain_fgp_c'] / mb, NUM1, True),
 ('Chain full GP บาท/กก. @ constant FX', lambda a: div(a['chain_fgp_c'], kg(a)), NUM2, True),
 ('FX impact = reported − constant (ล้านบาท)', None, None, 'grp'),
 ('① USD/THB — ชั้น TDC', lambda a: a['fx_tdc'] / mb, NUM1, False),
 ('② USD/IDR — ต้นทุนซื้อของ TWIN', lambda a: a['fx_usdidr_thb'] / mb, NUM1, False),
 ('③ IDR/THB — translation กำไร TWIN', lambda a: a['fx_idrthb_thb'] / mb, NUM1, False),
 ('FX impact รวม', lambda a: (a['fx_tdc'] + a['fx_usdidr_thb'] + a['fx_idrthb_thb']) / mb, NUM1, True),
]
# TWIN GP/kg for TDC products & chain per TDC tonne need separate aggregation
A_tdc = {}
for name, fn in cols:
    A_tdc[name] = agg(lambda r, fn=fn: fn(r) and r['src'] == 'TDC', lambda r: 0)[0]
r = hdr_r + 1
for label, fn, fmt, flag in spec:
    if flag == 'grp':
        put(ws, r, 1, label, f_bold, fill=fill_grp)
        for j in range(len(cols)): put(ws, r, 2 + j, None, fill=fill_grp)
        r += 1; continue
    put(ws, r, 1, label, f_bold if flag else f_norm)
    for j, (name, _) in enumerate(cols):
        a = A[name]
        if label.startswith('TWIN GP บาท/กก. (เฉพาะ'): v = div(A_tdc[name]['gp'], kg(A_tdc[name]))
        elif label.startswith('Chain full GP บาท/กก. — เฉพาะ'): v = div(A_tdc[name]['chain_fgp'], kg(A_tdc[name]))
        else: v = fn(a)
        put(ws, r, 2 + j, v, f_bold if flag else f_norm, fmt=fmt, border=b_left if j == 4 else None)
    r += 1
# reconciliation block
r += 1
put(ws, r, 1, 'Reconciliation: TDC shipment จริงให้ TWIN (ตามเดือน invoice) vs ที่จัดสรรตามยอดขาย TWIN', f_bold, fill=fill_grp)
for j in range(len(cols)): put(ws, r, 2 + j, None, fill=fill_grp)
r += 1
tdc_act = defaultdict(lambda: defaultdict(float))
for k, d in M['tdc'].items():
    m, sn = k.split('|'); y = m[:4]; qq = f"{y}Q{(int(m[5:]) - 1) // 3 + 1}"
    pers = ['FY' + y]
    if y == '2025' and m <= '2025-09': pers.append('YTD Sep-25')
    if y == '2026': pers.append('YTD Sep-26')
    pers.append(qlabel(qq))
    for p in pers:
        e = tdc_act[p]; e['t'] += d['t']; e['ns'] += d['ns']; e['pgp'] += d['ns'] - d['af'] - d['fi']; e['fgp'] += d['ns'] - d['af'] - d['fi'] - d['idle'] - d['oadj'] - d['ppa']
for label, fn, fmt in [('TDC shipment จริง (ตัน)', lambda e: e['t'], NUM0), ('TDC net sales จริง', lambda e: e['ns'] / mb, NUM1),
                       ('TDC product GP จริง', lambda e: e['pgp'] / mb, NUM1), ('TDC full GP จริง', lambda e: e['fgp'] / mb, NUM1),
                       ('TDC product GP จริง บาท/กก.', lambda e: div(e['pgp'], e['t'] * 1000), NUM2)]:
    put(ws, r, 1, label)
    for j, (name, _) in enumerate(cols): put(ws, r, 2 + j, fn(tdc_act[name]), fmt=fmt, border=b_left if j == 4 else None)
    r += 1
put(ws, r, 1, 'ส่วนต่าง = stock timing (TDC ส่งของเดือนหนึ่ง TWIN ขายอีกเดือน) และ TDC ปี 2024 ขายให้ TWIN บางรายการที่ TWIN ขายในปีถัดไป', f_grey)
widths(ws, {'A': 52})
for c in range(2, 2 + len(cols)): ws.column_dimensions[L(c)].width = 11
ws.freeze_panes = 'B5'
for i, (label, fn, fmt, flag) in enumerate(spec):
    if 'บาท/กก.' in label and 'transfer' not in label:
        rr = hdr_r + 1 + i
        traffic(ws, f'B{rr}:{L(1+len(cols))}{rr}', 0, 2, 5)

# =============== BY CUSTOMER ===============
def cust_sheet(title, keyfn, label_fn, extra_cols):
    ws = wb.create_sheet(title); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 85
    put(ws, 1, 1, f'{title} — ปริมาณ / กำไร / กำไรต่อ กก. (บาท)' + EXNOTE, f_title)
    put(ws, 2, 1, 'เรียงตามปริมาณ YTD Sep-26 · ล้านบาท = MB · บาท/กก. = THB/kg · TDC GP/กก. คิดเฉพาะตันสินค้า TDC · Chain = TWIN GP + TDC GP · สีไฟจราจร: แดง <0, เหลือง 0–2, เขียว ≥5 บาท/กก.', f_sub)
    per_agg = {p: agg(fn, keyfn) for p, fn in PERIODS}
    keys = set()
    for d in per_agg.values(): keys |= set(d)
    keys = sorted(keys, key=lambda k: (-per_agg['YTD Sep-26'][k]['t'] if k in per_agg['YTD Sep-26'] else 0, -per_agg['FY2025'][k]['t'] if k in per_agg['FY2025'] else 0))
    metrics = [('ตัน', 't', NUM0, lambda a: a['t'], False), ('TWIN NS MB', 'ns', NUM1, lambda a: a['ns'] / mb, False), ('TWIN GP MB', 'gp', NUM1, lambda a: a['gp'] / mb, False),
               ('TWIN GP /กก.', 'gpkg', NUM2, lambda a: div(a['gp'], kg(a)), True),
               ('TDC prod GP /กก.', 'tpkg', NUM2, lambda a: div(a['tdc_pgp'], kgt(a)), True), ('TDC full GP /กก.', 'tfkg', NUM2, lambda a: div(a['tdc_fgp'], kgt(a)), True),
               ('Chain prod GP /กก.', 'cpkg', NUM2, lambda a: div(a['chain_pgp'], kg(a)), True), ('Chain full GP /กก.', 'cfkg', NUM2, lambda a: div(a['chain_fgp'], kg(a)), True),
               ('Chain full GP MB', 'cf', NUM1, lambda a: a['chain_fgp'] / mb, False),
               ('Chain full GP /กก. @const FX', 'cfkgc', NUM2, lambda a: div(a['chain_fgp_c'], kg(a)), True)]
    nfix = 1 + len(extra_cols)
    hdr1, hdr2 = 4, 5
    put(ws, hdr1, 1, None); put(ws, hdr2, 1, 'ลูกค้า', f_hdr, fill=fill_hdr, border=b_hdr)
    for j, (nm, _) in enumerate(extra_cols): put(ws, hdr2, 2 + j, nm, f_hdr, fill=fill_hdr, border=b_hdr)
    c0 = nfix + 1
    for pi, (p, _) in enumerate(PERIODS):
        cc = c0 + pi * len(metrics)
        put(ws, hdr1, cc, p, f_bold, fill=fill_grp, align=CENTER)
        ws.merge_cells(start_row=hdr1, start_column=cc, end_row=hdr1, end_column=cc + len(metrics) - 1)
        for mi, (nm, _, _, _, _) in enumerate(metrics):
            put(ws, hdr2, cc + mi, nm, f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med, left=thin if mi == 0 else None))
    ws.row_dimensions[hdr2].height = 36
    r = hdr2 + 1
    # total row
    tot = {p: agg(fn, lambda r: 0)[0] for p, fn in PERIODS}
    put(ws, r, 1, 'รวมทั้งหมด', f_bold, fill=fill_tot)
    for j in range(len(extra_cols)): put(ws, r, 2 + j, None, fill=fill_tot)
    for pi, (p, _) in enumerate(PERIODS):
        for mi, (_, _, fmt, fn, _) in enumerate(metrics):
            put(ws, r, c0 + pi * len(metrics) + mi, fn(tot[p]), f_bold, fmt=fmt, fill=fill_tot, border=b_left if mi == 0 else None)
    r += 1; first = r
    for k in keys:
        put(ws, r, 1, label_fn(k))
        for j, (_, efn) in enumerate(extra_cols): put(ws, r, 2 + j, efn(k), f_grey)
        for pi, (p, _) in enumerate(PERIODS):
            a = per_agg[p].get(k)
            for mi, (_, _, fmt, fn, _) in enumerate(metrics):
                put(ws, r, c0 + pi * len(metrics) + mi, fn(a) if a else None, fmt=fmt, border=b_left if mi == 0 else None)
        r += 1
    last = r - 1
    for pi in range(len(PERIODS)):
        for mi, (_, _, _, _, tl) in enumerate(metrics):
            if tl:
                c = c0 + pi * len(metrics) + mi
                traffic(ws, f'{L(c)}{first-1}:{L(c)}{last}', 0, 2, 5)
    widths(ws, {'A': 40});
    for j in range(len(extra_cols)): ws.column_dimensions[L(2 + j)].width = 14
    for c in range(c0, c0 + len(PERIODS) * len(metrics)): ws.column_dimensions[L(c)].width = 9.5
    ws.freeze_panes = ws.cell(row=hdr2 + 1, column=c0)
    ws.auto_filter.ref = f'A{hdr2}:{L(c0 + len(PERIODS)*len(metrics) - 1)}{last}'
    return ws

info = {}
for rr in rows:
    d = info.setdefault(rr['cust'], dict(label=rr['label'], group=set(), country=set(), cur=set(), prods=defaultdict(float)))
    d['group'].add(rr['group']); d['country'].add(rr['country']); d['cur'].add(rr['cur']); d['prods'][rr['prod']] += rr['t']
def topprods(k, n=3):
    p = sorted(info[k]['prods'].items(), key=lambda x: -x[1]); return ', '.join(x[0] for x in p[:n])
cust_sheet('By customer', lambda r: r['cust'], lambda k: info[k]['label'],
           [('กลุ่มลูกค้า', lambda k: '/'.join(sorted(g for g in info[k]['group'] if g))), ('ประเทศ', lambda k: '/'.join(sorted(info[k]['country']))),
            ('สกุลขาย', lambda k: '/'.join(sorted(info[k]['cur']))), ('สินค้าหลัก (ตามตัน)', lambda k: topprods(k))])
pinfo = {}
for rr in rows: pinfo[(rr['cust'], rr['prod'])] = (rr['label'], rr['prod'], rr['src'], rr['react'])
cust_sheet('By customer-product', lambda r: (r['cust'], r['prod']), lambda k: pinfo[tuple(k)][0],
           [('สินค้า', lambda k: pinfo[tuple(k)][1]), ('แหล่งผลิต', lambda k: pinfo[tuple(k)][2]), ('Reaction', lambda k: pinfo[tuple(k)][3])])

# =============== QUARTERLY TREND ===============
ws = wb.create_sheet('Quarterly trend'); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 85
put(ws, 1, 1, 'Quarterly trend รายลูกค้า — Q1\'24 → Q3\'26', f_title)
put(ws, 2, 1, 'ลูกค้าเรียงตามปริมาณ YTD Sep-26 (แสดงทุกราย) · แต่ละ block = 1 metric · สีไฟจราจรเฉพาะ block บาท/กก.', f_sub)
qagg = agg(lambda r: True, lambda r: (r['cust'], r['q']))
ytd26 = agg(lambda r: r['y'] == '2026', lambda r: r['cust'])
fy25 = agg(lambda r: r['y'] == '2025', lambda r: r['cust'])
custs = sorted(info, key=lambda k: (-(ytd26[k]['t'] if k in ytd26 else 0), -(fy25[k]['t'] if k in fy25 else 0)))
blocks = [('ปริมาณขาย (ตัน)', lambda a: a['t'], NUM0, False), ('TWIN GP (ล้านบาท)', lambda a: a['gp'] / mb, NUM2, False),
          ('TWIN GP บาท/กก.', lambda a: div(a['gp'], kg(a)), NUM2, True), ('TDC product GP บาท/กก. (เฉพาะสินค้า TDC)', lambda a: div(a['tdc_pgp'], kgt(a)), NUM2, True),
          ('TDC full GP บาท/กก. (เฉพาะสินค้า TDC)', lambda a: div(a['tdc_fgp'], kgt(a)), NUM2, True),
          ('Chain full GP บาท/กก.', lambda a: div(a['chain_fgp'], kg(a)), NUM2, True), ('Chain full GP (ล้านบาท)', lambda a: a['chain_fgp'] / mb, NUM2, False),
          ('Chain full GP บาท/กก. @ constant FX', lambda a: div(a['chain_fgp_c'], kg(a)), NUM2, True)]
r = 4
for title, fn, fmt, tl in blocks:
    put(ws, r, 1, title, f_bold, fill=fill_grp)
    for j, qq in enumerate(QS): put(ws, r, 2 + j, qlabel(qq), f_hdr, fill=fill_grp, align=CENTER)
    r += 1
    tq = agg(lambda r: True, lambda r: r['q'])
    put(ws, r, 1, 'รวมทั้งหมด', f_bold, fill=fill_tot)
    for j, qq in enumerate(QS): put(ws, r, 2 + j, fn(tq[qq]), f_bold, fmt=fmt, fill=fill_tot)
    r += 1; first = r
    for k in custs:
        put(ws, r, 1, info[k]['label'])
        for j, qq in enumerate(QS):
            a = qagg.get([k, qq].__repr__()) if False else qagg.get((k, qq))
            put(ws, r, 2 + j, fn(a) if a and a['t'] else None, fmt=fmt)
        r += 1
    if tl: traffic(ws, f'B{first-1}:{L(1+len(QS))}{r-1}', 0, 2, 5)
    r += 1
widths(ws, {'A': 40})
for c in range(2, 2 + len(QS)): ws.column_dimensions[L(c)].width = 8.5
ws.freeze_panes = 'B4'

# =============== TDC PRODUCT RATES ===============
ws = wb.create_sheet('TDC product rates'); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 85
put(ws, 1, 1, 'สินค้า TDC ที่ขายผ่าน TWIN — ราคา/ต้นทุน/กำไร ต่อ กก. รายไตรมาส (TDC จาก shipment จริง · TWIN จากยอดขายจริง)', f_title)
put(ws, 2, 1, 'TDC transfer = ราคาที่ TDC ขายให้ TWIN (USD แปลงบาท ณ อัตรา invoice) · TWIN ASP = ราคาที่ TWIN ขายลูกค้า (บาท) · TWIN GP/กก. = ASP − landed COGS', f_sub)
hdrs = ['สินค้า (TWIN name)', 'SN', 'ไตรมาส', 'TDC ส่ง (ตัน)', 'TDC transfer USD/กก.', 'USD/THB', 'TDC transfer บาท/กก.', 'TDC product cost บาท/กก.', 'TDC product GP บาท/กก.',
        'Idle+PPA+adj บาท/กก.', 'TDC full GP บาท/กก.', 'TWIN ขาย (ตัน)', 'TWIN ASP บาท/กก.', 'TWIN COGS บาท/กก.', 'TWIN GP บาท/กก.', 'Chain full GP บาท/กก.', 'TWIN share of chain GP']
for j, h in enumerate(hdrs): put(ws, 4, 1 + j, h, f_hdr, fill=fill_hdr, align=CENTER, border=b_hdr)
ws.row_dimensions[4].height = 40
tq = defaultdict(lambda: defaultdict(float))
for k, d in M['tdc'].items():
    m, sn = k.split('|'); qq = f"{m[:4]}Q{(int(m[5:]) - 1) // 3 + 1}"
    e = tq[(sn, qq)]
    for x in ('t', 'ns', 'af', 'fi', 'idle', 'oadj', 'ppa', 'usd'): e[x] += d[x]
tw = agg(lambda r: r['src'] == 'TDC', lambda r: (r['sn'], r['q']))
vol_sn = defaultdict(float)
for (sn, qq), e in tq.items(): vol_sn[sn] += e['t']
r = 5
for sn in sorted(vol_sn, key=lambda s: -vol_sn[s]):
    for qq in QS:
        e = tq.get((sn, qq)); w_ = tw.get((sn, qq))
        if not e and not w_: continue
        put(ws, r, 1, M['sn_name'].get(sn, sn)); put(ws, r, 2, sn, f_grey); put(ws, r, 3, qlabel(qq), align=CENTER)
        if e and e['t'] > 0:
            k_ = e['t'] * 1000
            vals = [e['t'], e['usd'] / k_, e['ns'] / e['usd'] if e['usd'] else None, e['ns'] / k_, (e['af'] + e['fi']) / k_, (e['ns'] - e['af'] - e['fi']) / k_,
                    (e['idle'] + e['oadj'] + e['ppa']) / k_, (e['ns'] - e['af'] - e['fi'] - e['idle'] - e['oadj'] - e['ppa']) / k_]
            fmts = [NUM0, NUM2, NUM2, NUM2, NUM2, NUM2, NUM2, NUM2]
        else:
            vals = [None] * 8; fmts = [NUM0] + [NUM2] * 7
        for j, (v, fm) in enumerate(zip(vals, fmts)): put(ws, r, 4 + j, v, fmt=fm)
        if w_ and w_['t'] > 0:
            k2 = w_['t'] * 1000
            vals = [w_['t'], w_['ns'] / k2, w_['cogs'] / k2, w_['gp'] / k2, w_['chain_fgp'] / k2, div(w_['gp'], w_['chain_fgp']) if w_['chain_fgp'] > 0 else None]
        else: vals = [None] * 6
        for j, (v, fm) in enumerate(zip(vals, [NUM0, NUM2, NUM2, NUM2, NUM2, PCT])): put(ws, r, 12 + j, v, fmt=fm, border=b_left if j == 0 else None)
        r += 1
    r += 1
traffic(ws, f'I5:I{r}', 0, 2, 5); traffic(ws, f'K5:K{r}', 0, 2, 5); traffic(ws, f'O5:O{r}', 0, 2, 5); traffic(ws, f'P5:P{r}', 0, 2, 5)
widths(ws, {'A': 18, 'B': 8, 'C': 8})
for c in range(4, 18): ws.column_dimensions[L(c)].width = 11
ws.freeze_panes = 'D5'; ws.auto_filter.ref = f'A4:Q{r-1}'

# =============== FX ===============
ws = wb.create_sheet('FX'); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 90
put(ws, 1, 1, 'FX — อัตราแลกเปลี่ยนรายเดือน และผลกระทบแยก 3 ส่วน (ล้านบาท, reported − constant FX)', f_title)
put(ws, 2, 1, f"Constant FX = ค่าเฉลี่ยปี 2024: USD/THB {base['usdthb']:.3f} · IDR/THB {base['idrthb']:.6f} ({1/base['idrthb']:.0f} IDR ต่อ 1 บาท) · USD/IDR {base['usdidr']:.0f} · ค่าลบ = FX ทำให้กำไรเป็นบาทต่ำกว่าถ้า FX คงที่", f_sub)
hdrs = ['เดือน', 'USD/THB', 'ที่มา USD/THB', 'IDR/THB', 'USD/IDR', '', 'TWIN ขาย (ตัน)', '① USD/THB ชั้น TDC', '② USD/IDR ต้นทุน TWIN', '③ IDR/THB translation TWIN', 'FX รวม',
        '', 'TDC NS reported', 'TDC NS @const', 'TWIN GP reported', 'TWIN GP @const', 'Chain full GP reported', 'Chain full GP @const']
for j, h in enumerate(hdrs): put(ws, 4, 1 + j, h, f_hdr, fill=fill_hdr, align=CENTER, border=b_hdr)
ws.row_dimensions[4].height = 40
mag = agg(lambda r: True, lambda r: r['month'])
r = 5
for m in sorted(idrthb):
    a = mag.get(m, defaultdict(float))
    vals = [m, usdthb[m], fxsrc[m], idrthb[m], usdidr[m], None, a['t'], a['fx_tdc'] / mb, a['fx_usdidr_thb'] / mb, a['fx_idrthb_thb'] / mb,
            (a['fx_tdc'] + a['fx_usdidr_thb'] + a['fx_idrthb_thb']) / mb, None, a['tdc_ns'] / mb, a['tdc_ns_c'] / mb, a['gp'] / mb, a['gp_c'] / mb, a['chain_fgp'] / mb, a['chain_fgp_c'] / mb]
    fmts = [None, NUM2, None, FX6, NUM0, None, NUM0, NUM2, NUM2, NUM2, NUM2, None, NUM1, NUM1, NUM1, NUM1, NUM1, NUM1]
    for j, (v, fm) in enumerate(zip(vals, fmts)): put(ws, r, 1 + j, v, f_grey if j == 2 else f_norm, fmt=fm)
    r += 1
r += 1
put(ws, r, 1, 'สรุปรายไตรมาส / รายปี', f_bold, fill=fill_grp)
for j in range(1, len(hdrs)): put(ws, r, 1 + j, None, fill=fill_grp)
r += 1
for name, fn in [(qlabel(qq), (lambda r_, qq=qq: r_['q'] == qq)) for qq in QS] + [(p, fn) for p, fn in PERIODS]:
    a = agg(fn, lambda r_: 0)[0]
    fxm = {k: [] for k in ('u', 'i', 'x')}
    for m in idrthb:
        if fn(dict(q=f"{m[:4]}Q{(int(m[5:]) - 1) // 3 + 1}", y=m[:4], month=m)): fxm['u'].append(usdthb[m]); fxm['i'].append(idrthb[m]); fxm['x'].append(usdidr[m])
    avg = lambda l: sum(l) / len(l) if l else None
    vals = [name, avg(fxm['u']), 'avg', avg(fxm['i']), avg(fxm['x']), None, a['t'], a['fx_tdc'] / mb, a['fx_usdidr_thb'] / mb, a['fx_idrthb_thb'] / mb,
            (a['fx_tdc'] + a['fx_usdidr_thb'] + a['fx_idrthb_thb']) / mb, None, a['tdc_ns'] / mb, a['tdc_ns_c'] / mb, a['gp'] / mb, a['gp_c'] / mb, a['chain_fgp'] / mb, a['chain_fgp_c'] / mb]
    bold = name.startswith(('FY', 'YTD'))
    for j, (v, fm) in enumerate(zip(vals, fmts)): put(ws, r, 1 + j, v, f_bold if bold else (f_grey if j == 2 else f_norm), fmt=fm, fill=fill_tot if bold else None)
    r += 1
r += 1
notes = ['วิธีคิด', '① ชั้น TDC: TDC net sales (USD) × (อัตรา invoice − อัตราฐาน) — ต้นทุน TDC เป็นบาทจึงไม่เปลี่ยน',
         '② ชั้น TWIN ต้นทุน: COGS ของ TWIN เป็นของที่ซื้อเป็น USD → GP ในสกุล IDR ถ้า USD/IDR คงที่ − GP IDR จริง แล้วแปลงบาทที่อัตราเดือนนั้น (ราคาขาย IDR ถือว่าไม่เปลี่ยน; ลูกค้าที่ขายเป็น USD ส่วนนี้ ≈ 0 เพราะซื้อ-ขายสกุลเดียวกัน)',
         '③ ชั้น TWIN translation: GP (IDR, หลังตรึง USD/IDR) × (IDR/THB เดือนนั้น − อัตราฐาน) — กระทบเฉพาะตอนแปลงเป็นบาท ไม่กระทบกำไรจริงในอินโดนีเซีย',
         'มุมมองอื่น (เท่ากันในผลรวม): แยกเป็น revenue IDR translation / revenue USD translation / COGS USD translation — ดูคอลัมน์ fx_rev_idr, fx_rev_usd, fx_cogs_usd ในชีท Data']
for n in notes: put(ws, r, 1, n, f_bold if n == 'วิธีคิด' else f_grey); r += 1
widths(ws, {'A': 11, 'B': 9, 'C': 22, 'D': 10, 'E': 9, 'F': 2, 'G': 10, 'H': 11, 'I': 11, 'J': 12, 'K': 9, 'L': 2, 'M': 10, 'N': 10, 'O': 10, 'P': 10, 'Q': 11, 'R': 11})
ws.freeze_panes = 'B5'

# =============== DATA ===============
ws = wb.create_sheet('Data')
cols_d = [('month', 'month'), ('year', 'y'), ('quarter', 'q'), ('customer', 'label'), ('customer_key', 'cust'), ('customer_group', 'group'), ('country', 'country'), ('sale_currency', 'cur'),
          ('product', 'prod'), ('source', 'src'), ('tdc_sn', 'sn'), ('reaction', 'react'), ('tdc_rate_basis', 'tdc_basis'),
          ('tons', 't'), ('twin_ns_idr', 'ns_idr'), ('twin_cogs_idr', 'cogs_idr'), ('twin_ns_thb', 'ns'), ('twin_cogs_thb', 'cogs'), ('twin_gp_thb', 'gp'),
          ('usdthb_m', 'usdthb'), ('idrthb_m', 'idrthb'), ('usdidr_m', 'usdidr'), ('twin_ns_usd', 'ns_usd'), ('twin_cogs_usd', 'cogs_usd'),
          ('twin_ns_constFX', 'ns_c'), ('twin_cogs_constFX', 'cogs_c'), ('twin_gp_constFX', 'gp_c'),
          ('tdc_ns_thb', 'tdc_ns'), ('tdc_ns_usd', 'tdc_usd'), ('tdc_product_cost', 'tdc_pcost'), ('tdc_idle_ppa_adj', 'tdc_other'), ('tdc_product_gp', 'tdc_pgp'), ('tdc_full_gp', 'tdc_fgp'),
          ('tdc_ns_constFX', 'tdc_ns_c'), ('tdc_product_gp_constFX', 'tdc_pgp_c'), ('tdc_full_gp_constFX', 'tdc_fgp_c'),
          ('chain_product_gp', 'chain_pgp'), ('chain_full_gp', 'chain_fgp'), ('chain_product_gp_constFX', 'chain_pgp_c'), ('chain_full_gp_constFX', 'chain_fgp_c'),
          ('fx1_usdthb_tdc', 'fx_tdc'), ('fx2_usdidr_twin_cost', 'fx_usdidr_thb'), ('fx3_idrthb_twin_translation', 'fx_idrthb_thb'),
          ('fx_rev_idr', 'fx_rev_idr'), ('fx_rev_usd', 'fx_rev_usd'), ('fx_cogs_usd', 'fx_cogs_usd')]
for j, (h, _) in enumerate(cols_d): put(ws, 1, 1 + j, h, f_hdr, fill=fill_hdr)
for i, rr in enumerate(sorted(rows, key=lambda x: (x['month'], x['label'], x['prod']))):
    for j, (_, k) in enumerate(cols_d):
        v = rr.get(k)
        c = ws.cell(row=2 + i, column=1 + j, value=v); c.font = f_norm
        if isinstance(v, float): c.number_format = NUM2 if abs(v) < 100 else NUM0
ws.freeze_panes = 'E2'; ws.auto_filter.ref = f'A1:{L(len(cols_d))}{len(rows)+1}'
for j in range(len(cols_d)): ws.column_dimensions[L(1 + j)].width = 13
ws.column_dimensions['D'].width = 38

wb.save(OUT)
print('saved', OUT)
