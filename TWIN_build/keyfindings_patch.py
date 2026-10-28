# Inserts a 'Key findings' sheet (executive summary) at the front of the workbook. Run after build_xlsx.py: python keyfindings_patch.py <dir> <xlsx>
import json, sys
from collections import defaultdict
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import CellIsRule

S, OUT = sys.argv[1], sys.argv[2]
M = json.load(open(f'{S}/model.json', encoding='utf-8')); rows = M['rows']; base = M['base']
F = 'Arial'
f_norm = Font(name=F, size=9); f_bold = Font(name=F, size=9, bold=True); f_hdr = Font(name=F, size=9, bold=True, color='404040')
f_title = Font(name=F, size=13, bold=True); f_sub = Font(name=F, size=9, italic=True, color='7F7F7F'); f_sec = Font(name=F, size=10, bold=True, color='1F3864')
fill_hdr = PatternFill('solid', fgColor='F2F2F2'); fill_tot = PatternFill('solid', fgColor='F2F2F2')
RED, AMB, GRN = 'F1C7C7', 'FBF0C6', 'E2EFDA'
thin = Side(style='thin', color='BFBFBF'); med = Side(style='medium', color='808080')
NUM0 = '#,##0;[Red]-#,##0;-'; NUM1 = '#,##0.0;[Red]-#,##0.0;-'; NUM2 = '#,##0.00;[Red]-#,##0.00;-'
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True); WRAP = Alignment(wrap_text=True, vertical='top')
mb = 1e6
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
PERIODS = [('FY2024', lambda r: r['y'] == '2024'), ('FY2025', lambda r: r['y'] == '2025'),
           ('YTD Sep-25', lambda r: '2025-01' <= r['month'] <= '2025-09'), ('YTD Sep-26', lambda r: r['y'] == '2026')]
KEYS = ('t','ns','gp','gp_c','tdc_ns','tdc_pgp','tdc_fgp','tdc_pgp_c','tdc_fgp_c','chain_pgp','chain_fgp','chain_fgp_c','fx_tdc','fx_usdidr_thb','fx_idrthb_thb')
def agg(filt, keyfn):
    d = defaultdict(lambda: defaultdict(float))
    for r in rows:
        if not filt(r): continue
        a = d[keyfn(r)]
        for k in KEYS: a[k] += r[k]
        a['t_tdc'] += r['t'] if r['src'] == 'TDC' else 0
        if r['src'] == 'TDC': a['gp_tdc'] += r['gp']; a['chain_fgp_tdc'] += r['chain_fgp']
    return d
def div(x, y): return x / y if y else None

wb = load_workbook(OUT)
if 'Key findings' in wb.sheetnames: del wb['Key findings']
ws = wb.create_sheet('Key findings', 0); ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 90
EXCL = M.get('excluded') or []
EXNOTE = (' · ไม่รวม ' + ' / '.join(EXCL)) if EXCL else ''
put(ws, 1, 1, 'TWIN (Indonesia) — กำไรรายลูกค้า 2 ชั้น (TDC ผู้ผลิต + TWIN trading): Key findings' + EXNOTE, f_title)
put(ws, 2, 1, 'หน่วย: บาท / บาทต่อ กก. · ข้อมูล Jan-24 → Sep-26 · constant FX = ค่าเฉลี่ยปี 2024 · รายละเอียดดูชีท Summary / By customer / FX', f_sub)

# ---- 1. headline ----
r = 4
put(ws, r, 1, '1. ภาพรวม', f_sec); r += 1
A = {p: agg(fn, lambda x: 0)[0] for p, fn in PERIODS}
put(ws, r, 1, 'ล้านบาท (ยกเว้นที่ระบุ)', f_hdr, fill=fill_hdr, border=Border(bottom=med))
for j, (p, _) in enumerate(PERIODS): put(ws, r, 2 + j, p, f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med))
put(ws, r, 6, 'Δ YTD', f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med)); r += 1
head = [('ปริมาณ TWIN รวม (ตัน)', lambda a: a['t'], NUM0),
        ('   สินค้าจาก TDC (ตัน)', lambda a: a['t_tdc'], NUM0),
        (('   สินค้าอื่นที่ไม่ใช่ TDC: pregel / D2201 / ฯลฯ (ตัน)' if M.get('excluded') else '   native / sago / อื่น ๆ ไม่ใช่ TDC (ตัน)'), lambda a: a['t'] - a['t_tdc'], NUM0),
        ('TWIN GP', lambda a: a['gp'] / mb, NUM1),
        ('TWIN GP บาท/กก. — ทุกสินค้า', lambda a: div(a['gp'], a['t'] * 1000), NUM2),
        ('TWIN GP บาท/กก. — เฉพาะสินค้า TDC', lambda a: div(a['gp_tdc'], a['t_tdc'] * 1000), NUM2),
        ('TDC product GP (จัดสรร)', lambda a: a['tdc_pgp'] / mb, NUM1),
        ('TDC product GP บาท/กก.', lambda a: div(a['tdc_pgp'], a['t_tdc'] * 1000), NUM2),
        ('TDC full GP บาท/กก.', lambda a: div(a['tdc_fgp'], a['t_tdc'] * 1000), NUM2),
        ('Chain full GP บาท/กก. — ตันสินค้า TDC', lambda a: div(a['chain_fgp_tdc'], a['t_tdc'] * 1000), NUM2),
        ('Chain full GP — ทุกสินค้า', lambda a: a['chain_fgp'] / mb, NUM1),
        ('Chain full GP @ constant FX', lambda a: a['chain_fgp_c'] / mb, NUM1),
        ('FX impact รวม (reported − constant)', lambda a: (a['fx_tdc'] + a['fx_usdidr_thb'] + a['fx_idrthb_thb']) / mb, NUM1)]
r0 = r
for label, fn, fmt in head:
    put(ws, r, 1, label, f_bold if not label.startswith('   ') else f_norm)
    vals = [fn(A[p]) for p, _ in PERIODS]
    for j, v in enumerate(vals): put(ws, r, 2 + j, v, fmt=fmt, border=Border(left=thin) if j == 2 else None)
    d = (vals[3] - vals[2]) if (vals[2] is not None and vals[3] is not None) else None
    put(ws, r, 6, d, f_bold, fmt=fmt, border=Border(left=thin))
    if 'บาท/กก.' in label: traffic(ws, f'B{r}:E{r}', 0, 2, 5)
    r += 1

# ---- 1b. GP 5 levels ----
r += 1
info = {}
for x in rows:
    d = info.setdefault(x['cust'], dict(label=x['label'], prods=defaultdict(float))); d['prods'][x['prod']] += x['t']
put(ws, r, 1, '1b. กำไร 5 ระดับ — TWIN GP · TDC GP (product cost) · TDC GP (full cost) · Total GP (product cost) · Total GP (full cost)', f_sec); r += 1
put(ws, r, 1, 'นิยาม: TDC product cost = Actual Cost (AF) + F&I · TDC full cost = product cost + Idle + PPA + Other adj · Total = TWIN GP + TDC GP · บาท/กก. ของ TDC คิดบนตันสินค้า TDC, ของ TWIN/Total คิดบนตันทั้งหมด', f_sub); r += 1
LV = [('TWIN GP', 'gp', 'all'), ('TDC GP — product cost', 'tdc_pgp', 'tdc'), ('TDC GP — full cost', 'tdc_fgp', 'tdc'),
      ('Total GP — product cost', 'chain_pgp', 'all'), ('Total GP — full cost', 'chain_fgp', 'all')]
put(ws, r, 1, 'ล้านบาท', f_hdr, fill=fill_hdr, border=Border(bottom=med))
for j, (p, _) in enumerate(PERIODS): put(ws, r, 2 + j, p, f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med))
put(ws, r, 6, 'Δ YTD', f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med))
put(ws, r, 7, 'บาท/กก.', f_hdr, fill=fill_hdr, border=Border(bottom=med))
for j, (p, _) in enumerate(PERIODS): put(ws, r, 8 + j, p, f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med))
put(ws, r, 12, 'Δ YTD', f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med)); r += 1
lv0 = r
for label, k, basis in LV:
    bold = label.startswith('Total')
    put(ws, r, 1, label, f_bold if bold else f_norm); put(ws, r, 7, label, f_bold if bold else f_norm)
    mbv = [A[p][k] / mb for p, _ in PERIODS]
    kgv = [div(A[p][k], (A[p]['t_tdc'] if basis == 'tdc' else A[p]['t']) * 1000) for p, _ in PERIODS]
    for j, v in enumerate(mbv): put(ws, r, 2 + j, v, f_bold if bold else f_norm, fmt=NUM1, border=Border(left=thin) if j == 2 else None)
    put(ws, r, 6, mbv[3] - mbv[2], f_bold, fmt=NUM1, border=Border(left=thin))
    for j, v in enumerate(kgv): put(ws, r, 8 + j, v, f_bold if bold else f_norm, fmt=NUM2, border=Border(left=thin) if j == 2 else None)
    put(ws, r, 12, (kgv[3] - kgv[2]) if (kgv[2] is not None and kgv[3] is not None) else None, f_bold, fmt=NUM2, border=Border(left=thin))
    r += 1
traffic(ws, f'H{lv0}:K{r-1}', 0, 2, 5)
# per customer, YTD Sep-26 (all customers) with YTD Sep-25 total GP full for comparison
r += 1
put(ws, r, 1, 'รายลูกค้า — YTD Sep-26 (ทุกราย เรียงตามตัน) · ล้านบาท แล้วตามด้วย บาท/กก.', f_bold); r += 1
hd = ['ลูกค้า', 'ตัน YTD26', 'TWIN GP', 'TDC GP product', 'TDC GP full', 'Total GP product', 'Total GP full', 'TWIN GP /กก.', 'TDC GP product /กก.', 'TDC GP full /กก.', 'Total GP product /กก.', 'Total GP full /กก.', 'Total GP full /กก. YTD25']
for j, h in enumerate(hd): put(ws, r, 1 + j, h, f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med))
put(ws, r, 2, 'ตัน YTD26', f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med))
ws.row_dimensions[r].height = 36; r += 1; lv1 = r
ca5 = agg(lambda x: '2025-01' <= x['month'] <= '2025-09', lambda x: x['cust']); ca6 = agg(lambda x: x['y'] == '2026', lambda x: x['cust'])
def lv_row(label, a6, a5, bold=False):
    global r
    kg_ = a6['t'] * 1000; kgt_ = a6['t_tdc'] * 1000
    vals = [label, a6['t'] or None, a6['gp'] / mb, a6['tdc_pgp'] / mb, a6['tdc_fgp'] / mb, a6['chain_pgp'] / mb, a6['chain_fgp'] / mb,
            div(a6['gp'], kg_), div(a6['tdc_pgp'], kgt_), div(a6['tdc_fgp'], kgt_), div(a6['chain_pgp'], kg_), div(a6['chain_fgp'], kg_), div(a5['chain_fgp'], a5['t'] * 1000)]
    fm = [None, NUM0, NUM2, NUM2, NUM2, NUM2, NUM2, NUM2, NUM2, NUM2, NUM2, NUM2, NUM2]
    for j, (v, f_) in enumerate(zip(vals, fm)): put(ws, r, 1 + j, v, f_bold if bold else f_norm, fmt=f_, fill=fill_tot if bold else None, border=Border(left=thin) if j in (2, 7, 12) else None)
    r += 1
lv_row(f'รวมทุกลูกค้า ({len(info)} ราย)', A['YTD Sep-26'], A['YTD Sep-25'], bold=True)
for k in sorted(info, key=lambda k: -(ca6[k]['t'] if k in ca6 else 0)):
    a6 = ca6.get(k); a5 = ca5.get(k, defaultdict(float))
    if not a6 or a6['t'] <= 0: continue
    lv_row(info[k]['label'], a6, a5)
traffic(ws, f'H{lv1}:M{r-1}', 0, 2, 5)
for cc in ('L', 'M'): ws.column_dimensions[cc].width = 11

# ---- 2. FX ----
r += 1
put(ws, r, 1, '2. FX — ผลกระทบแยก 3 ส่วน (ล้านบาท, เทียบอัตราเฉลี่ยปี 2024: USD/THB %.2f · USD/IDR %s · IDR/THB %.6f)' % (base['usdthb'], f"{base['usdidr']:,.0f}", base['idrthb']), f_sec); r += 1
put(ws, r, 1, 'ส่วน', f_hdr, fill=fill_hdr, border=Border(bottom=med))
for j, (p, _) in enumerate(PERIODS): put(ws, r, 2 + j, p, f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med))
put(ws, r, 6, 'ความหมาย', f_hdr, fill=fill_hdr, border=Border(bottom=med)); r += 1
fxrows = [('① USD/THB — ชั้น TDC', 'fx_tdc', 'TDC ขาย TWIN เป็น USD, ต้นทุนเป็นบาท → บาทแข็ง (35.3 → 32–33) ทำให้ยอดขาย/กำไร TDC เป็นบาทลด'),
          ('② USD/IDR — ต้นทุนซื้อของ TWIN', 'fx_usdidr_thb', 'TWIN ซื้อ USD ขาย IDR → รูเปียห์อ่อน (15,800 → 17,600/USD) ทำให้ COGS IDR +11% ขณะราคาขาย IDR ไม่ขยับตาม = กระทบกำไรจริงในอินโดนีเซีย (ส่วนใหญ่สุด)'),
          ('③ IDR/THB — translation กำไร TWIN', 'fx_idrthb_thb', 'กำไร IDR แปลงเป็นบาทได้น้อยลง (1 บาท = 448 → 533 IDR) — ไม่กระทบกำไรในสกุลท้องถิ่น')]
for label, k, note in fxrows:
    put(ws, r, 1, label)
    for j, (p, _) in enumerate(PERIODS): put(ws, r, 2 + j, A[p][k] / mb, fmt=NUM1, border=Border(left=thin) if j == 2 else None)
    put(ws, r, 6, note, f_norm, align=WRAP); ws.row_dimensions[r].height = 26; r += 1
put(ws, r, 1, 'FX impact รวม', f_bold, fill=fill_tot)
for j, (p, _) in enumerate(PERIODS): put(ws, r, 2 + j, (A[p]['fx_tdc'] + A[p]['fx_usdidr_thb'] + A[p]['fx_idrthb_thb']) / mb, f_bold, fmt=NUM1, fill=fill_tot, border=Border(left=thin) if j == 2 else None)
put(ws, r, 6, 'ถ้า FX คงที่ chain full GP YTD Sep-26 = %.1f ล้านบาท (%.2f บาท/กก.) แทน %.1f (%.2f) → การถดถอยต่อ กก. ปีนี้เกือบทั้งหมดมาจาก FX ยกเว้นลูกค้า Cassflo 500 รายใหม่ที่เป็นปัญหาราคา' % (
    A['YTD Sep-26']['chain_fgp_c'] / mb, A['YTD Sep-26']['chain_fgp_c'] / (A['YTD Sep-26']['t'] * 1000), A['YTD Sep-26']['chain_fgp'] / mb, A['YTD Sep-26']['chain_fgp'] / (A['YTD Sep-26']['t'] * 1000)), f_norm, fill=fill_tot, align=WRAP)
ws.row_dimensions[r].height = 26; r += 2

# ---- 3. customers ----
put(ws, r, 1, '3. ลูกค้าหลัก (เรียงตามปริมาณ YTD Sep-26) — บาท/กก. · สีไฟจราจร: แดง <0, เหลือง 0–2, เขียว ≥5', f_sec); r += 1
info = {}
for x in rows:
    d = info.setdefault(x['cust'], dict(label=x['label'], prods=defaultdict(float))); d['prods'][x['prod']] += x['t']
ca = {p: agg(fn, lambda x: x['cust']) for p, fn in PERIODS}
hdrs = ['ลูกค้า', 'สินค้าหลัก', 'ตัน YTD25', 'ตัน YTD26', 'TWIN GP/กก. YTD25', 'TWIN GP/กก. YTD26', 'TDC full GP/กก. YTD26', 'Chain full GP/กก. YTD25', 'Chain full GP/กก. YTD26', 'Chain full GP MB YTD26', 'Chain full GP MB @const FX']
for j, h in enumerate(hdrs): put(ws, r, 1 + j, h, f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med))
ws.row_dimensions[r].height = 36; r += 1; first = r
def cust_vals(label, top, a5, a6):
    return [label, top, a5['t'] or None, a6['t'] or None, div(a5['gp'], a5['t'] * 1000), div(a6['gp'], a6['t'] * 1000), div(a6['tdc_fgp'], a6['t_tdc'] * 1000),
            div(a5['chain_fgp'], a5['t'] * 1000), div(a6['chain_fgp'], a6['t'] * 1000), a6['chain_fgp'] / mb, a6['chain_fgp_c'] / mb]
fmts = [None, None, NUM0, NUM0, NUM2, NUM2, NUM2, NUM2, NUM2, NUM2, NUM2]
def cust_row(vals, bold=False):
    global r
    for j, (v, fm) in enumerate(zip(vals, fmts)):
        put(ws, r, 1 + j, v, f_bold if bold else (f_sub if j == 1 else f_norm), fmt=fm, fill=fill_tot if bold else None)
    r += 1
n_all = len(info)
cust_row(cust_vals(f'รวมทุกลูกค้า ({n_all} ราย)', 'ทุกสินค้า', A['YTD Sep-25'], A['YTD Sep-26']), bold=True)
custs = sorted(info, key=lambda k: -ca['YTD Sep-26'][k]['t'] if k in ca['YTD Sep-26'] else 0)[:20]
for k in custs:
    a6 = ca['YTD Sep-26'].get(k, defaultdict(float)); a5 = ca['YTD Sep-25'].get(k, defaultdict(float))
    top = ', '.join(p for p, _ in sorted(info[k]['prods'].items(), key=lambda z: -z[1])[:2])
    cust_row(cust_vals(info[k]['label'], top, a5, a6))
rest = set(info) - set(custs)
o5 = agg(lambda x: '2025-01' <= x['month'] <= '2025-09' and x['cust'] in rest, lambda x: 0)[0]
o6 = agg(lambda x: x['y'] == '2026' and x['cust'] in rest, lambda x: 0)[0]
cust_row(cust_vals(f'ลูกค้าอื่น ๆ นอก top 20 ({len(rest)} ราย)', '', o5, o6), bold=True)
for c in ('E', 'F', 'G', 'H', 'I'): traffic(ws, f'{c}{first}:{c}{r-1}', 0, 2, 5)
r += 1

# ---- 4. products ----
put(ws, r, 1, '4. สินค้า TDC ผ่าน TWIN — margin ต่อ กก. แยกชั้น (YTD Sep-25 → YTD Sep-26)', f_sec); r += 1
pa = {p: agg(lambda x, fn=fn: fn(x) and x['src'] == 'TDC', lambda x: x['prod']) for p, fn in PERIODS}
hdrs = ['สินค้า', 'ตัน YTD25', 'ตัน YTD26', 'TDC transfer/กก. YTD26', 'TDC prod GP/กก. YTD25', 'TDC prod GP/กก. YTD26', 'TWIN GP/กก. YTD25', 'TWIN GP/กก. YTD26', 'Chain full GP/กก. YTD25', 'Chain full GP/กก. YTD26']
for j, h in enumerate(hdrs): put(ws, r, 1 + j, h, f_hdr, fill=fill_hdr, align=CENTER, border=Border(bottom=med))
ws.row_dimensions[r].height = 36; r += 1; first = r
T5 = agg(lambda x: '2025-01' <= x['month'] <= '2025-09' and x['src'] == 'TDC', lambda x: 0)[0]; T6 = agg(lambda x: x['y'] == '2026' and x['src'] == 'TDC', lambda x: 0)[0]
vals = ['รวมสินค้า TDC ทั้งหมด', T5['t'], T6['t'], div(T6['tdc_ns'], T6['t'] * 1000), div(T5['tdc_pgp'], T5['t'] * 1000), div(T6['tdc_pgp'], T6['t'] * 1000),
        div(T5['gp'], T5['t'] * 1000), div(T6['gp'], T6['t'] * 1000), div(T5['chain_fgp'], T5['t'] * 1000), div(T6['chain_fgp'], T6['t'] * 1000)]
for j, v in enumerate(vals): put(ws, r, 1 + j, v, f_bold, fmt=None if j == 0 else (NUM0 if j < 3 else NUM2), fill=fill_tot)
r += 1
prods = sorted(set(pa['YTD Sep-26']) | set(pa['YTD Sep-25']), key=lambda p: -(pa['YTD Sep-26'][p]['t'] if p in pa['YTD Sep-26'] else 0))
for p in prods:
    a6 = pa['YTD Sep-26'].get(p, defaultdict(float)); a5 = pa['YTD Sep-25'].get(p, defaultdict(float))
    if a6['t'] + a5['t'] < 5: continue
    vals = [p, a5['t'] or None, a6['t'] or None, div(a6['tdc_ns'], a6['t'] * 1000), div(a5['tdc_pgp'], a5['t'] * 1000), div(a6['tdc_pgp'], a6['t'] * 1000),
            div(a5['gp'], a5['t'] * 1000), div(a6['gp'], a6['t'] * 1000), div(a5['chain_fgp'], a5['t'] * 1000), div(a6['chain_fgp'], a6['t'] * 1000)]
    for j, v in enumerate(vals): put(ws, r, 1 + j, v, fmt=None if j == 0 else (NUM0 if j < 3 else NUM2))
    r += 1
for c in ('E', 'F', 'G', 'H', 'I', 'J'): traffic(ws, f'{c}{first}:{c}{r-1}', 0, 2, 5)
r += 1

# ---- 5. findings ----
put(ws, r, 1, '5. ข้อสรุป', f_sec); r += 1
Y6 = A['YTD Sep-26']; Y5 = A['YTD Sep-25']
findings = [
 'Volume โตแต่เป็นของบาง — ปริมาณ YTD26 ที่เพิ่ม (%s → %s ตัน) เกือบทั้งหมดคือ native starch / sago ที่ไม่ใช่ของ TDC: Thai Wah International Shanghai รายเดียว ~3,665 ตันที่ 1.6 บาท/กก. และลูกค้าฟิลิปปินส์/จีนรายใหม่ (Anhui BBCA, Twinpack, San Miguel) ที่ ~2 บาท/กก. — กำไรต้นทาง (TWPC) ของกลุ่มนี้ไม่อยู่ใน 2 ไฟล์' % (f"{Y5['t']:,.0f}", f"{Y6['t']:,.0f}"),
 'Cassflo 500 คือตัวฉุดทั้ง 2 ชั้น (71% ของตันสินค้า TDC): TDC product GP/กก. ตก 5.65 → 2.33 (ต้นทุนขึ้น ขณะ transfer price ลง 27.2 → 26.1) ส่วน TWIN เหลือ 0.17 บาท/กก. · Heinz ABC (1,219 ตัน) chain full GP 7.39 → 2.83 บาท/กก. · ลูกค้า Cassflo 500 รายใหม่ 3 ราย (Karunia Alam Segar, Prakarsa Alam Segar, Glico Wings รวม ~1,000 ตัน) TWIN ขายต่ำกว่าทุน −0.4 ถึง −0.7 บาท/กก. chain full < 1 บาท/กก. → ปัญหาราคา ไม่ใช่ FX',
 'ลูกค้าที่กำไรดีคือ distributor และ Cassmax 102: Bumi Tirta Pangan Kencana 9.7, Prima Erindo 9.6 บาท/กก. (chain full) และ Cassmax 102 ทุกราย ~14 บาท/กก. แต่ปริมาณเล็ก · Casstex 22 / Cassflo 600 TWIN margin ยังดี (5.9 / 6.7) แต่ TDC product GP หายไปครึ่งหนึ่ง',
 'FX YTD26 รวม %.1f ล้านบาท เทียบอัตราเฉลี่ย 2024 (① USD/THB ชั้น TDC %.1f ② USD/IDR ต้นทุน TWIN %.1f ③ IDR/THB translation %.1f) · ปี 2025 ทั้งปี %.1f ล้านบาทสัดส่วนคล้ายกัน · ส่วน ② ใหญ่สุดและเป็นกำไรจริงที่หายในอินโดนีเซีย → ควรทบทวนกลไกส่งผ่านราคา IDR (price adjustment clause ตาม USD/IDR) กับลูกค้าหลัก' % (
    (Y6['fx_tdc'] + Y6['fx_usdidr_thb'] + Y6['fx_idrthb_thb']) / mb, Y6['fx_tdc'] / mb, Y6['fx_usdidr_thb'] / mb, Y6['fx_idrthb_thb'] / mb,
    (A['FY2025']['fx_tdc'] + A['FY2025']['fx_usdidr_thb'] + A['FY2025']['fx_idrthb_thb']) / mb),
 'ข้อเสนอถัดไป: (1) ตั้ง floor chain full GP สำหรับ Cassflo 500 ในอินโดนีเซีย (เช่น ≥ 4 บาท/กก.) และทบทวนราคา 3 รายใหม่ก่อนต่อสัญญา (2) ผลัก mix ไป Cassmax 102 / Cassflo 600 / Casstex 22 ที่ chain ≥ 8 บาท/กก. (3) ขอไฟล์ TWPC profitability เพื่อเติมชั้นต้นทางของ native/sago ให้ครบ chain',
 'สมมติฐานที่ต้องยืนยัน: USD/THB ปี 2024 ใช้ค่า BOT โดยประมาณ (ไฟล์ TDC ไม่มี) · ลูกค้านอกอินโดหลัง Aug-25 ถือว่าขาย USD · TDC GP รายลูกค้า = จัดสรรตาม product × ไตรมาส (TDC ขาย TWIN เป็นลูกค้าเดียว) · ไม่มี opex TWIN ในไฟล์ → full cost มีเฉพาะชั้น TDC',
]
if EXCL:
    fx6 = (Y6['fx_tdc'] + Y6['fx_usdidr_thb'] + Y6['fx_idrthb_thb']) / mb
    findings = [
     'ขอบเขต: ตัด Native starch / Sago-pearl / Fibioca / Coarse flour ออก เหลือ modified starch (TDC 92%% ของตัน) + pregel / D2201 / อื่น ๆ · ปริมาณ YTD26 %s ตัน (+%.0f%% vs YTD25 %s) แต่ chain full GP ลดจาก %.1f เป็น %.1f ล้านบาท → กำไรต่อ กก. ตก %.2f → %.2f บาท/กก. (TWIN %.2f → %.2f, TDC product %.2f → %.2f)' % (
        f"{Y6['t']:,.0f}", (Y6['t'] / Y5['t'] - 1) * 100, f"{Y5['t']:,.0f}", Y5['chain_fgp'] / mb, Y6['chain_fgp'] / mb,
        Y5['chain_fgp'] / (Y5['t'] * 1000), Y6['chain_fgp'] / (Y6['t'] * 1000), Y5['gp'] / (Y5['t'] * 1000), Y6['gp'] / (Y6['t'] * 1000),
        Y5['tdc_pgp'] / (Y5['t_tdc'] * 1000), Y6['tdc_pgp'] / (Y6['t_tdc'] * 1000)),
     'Cassflo 500 = 65% ของตัน แต่ chain full GP เหลือ 1.5 บาท/กก. (YTD25 6.3): Heinz ABC 1,219 ตัน (34%) TWIN margin เหลือ 0.30 บาท/กก. (YTD25 1.31) chain full 6.05 → 1.65 บาท/กก. · ลูกค้าใหม่ 3 ราย Karunia Alam Segar / Prakarsa Alam Segar / Glico Wings รวม 1,000 ตัน (28%) TWIN ขายต่ำกว่าทุน −0.4 ถึง −0.7 บาท/กก. chain full < 1 บาท/กก. → 4 รายนี้ = 62% ของตัน แต่ให้ chain GP เพียง ~2.8 ล้านบาท (21%) — เป็นปัญหาราคาต่อทุน ไม่ใช่ FX อย่างเดียว',
     'กำไรกระจุกที่ distributor และ SKU พรีเมียม: Bumi Tirta Pangan Kencana 588 ตัน (17%%) ให้ chain full GP 5.7 ล้านบาท = 43%% ของทั้งหมด ที่ 9.7 บาท/กก. (Cassflo 800 / Cassmax 102 / Casstex 22) · Prima Erindo 9.6, Astamulya 10.1, Nippn 16.2, Diamond Brand 13.6 บาท/กก. · ลูกค้ารายเล็กนอก top 20 (chain ~%.1f บาท/กก.) ดีกว่าค่าเฉลี่ยมาก → มูลค่าอยู่ที่ Cassmax 102 / Cassflo 600 / Cassflo 800 / Casstex 22 (chain 8–15 บาท/กก.) ไม่ใช่ Cassflo 500',
     'FX YTD26 รวม %.1f ล้านบาท เทียบอัตราเฉลี่ย 2024 (① USD/THB ชั้น TDC %.1f ② USD/IDR ต้นทุน TWIN %.1f ③ IDR/THB translation %.1f) · FY25 ทั้งปี %.1f · ถ้า FX คงที่ chain full GP YTD26 = %.1f ล้านบาท (%.2f บาท/กก.) แทน %.1f (%.2f) → ครึ่งหนึ่งของการถดถอยมาจาก FX อีกครึ่งจากราคา/ต้นทุน Cassflo 500 · ส่วน ② คือกำไรจริงที่หายในอินโดนีเซีย ควรมี price adjustment ตาม USD/IDR กับ Heinz และรายใหม่' % (
        fx6, Y6['fx_tdc'] / mb, Y6['fx_usdidr_thb'] / mb, Y6['fx_idrthb_thb'] / mb,
        (A['FY2025']['fx_tdc'] + A['FY2025']['fx_usdidr_thb'] + A['FY2025']['fx_idrthb_thb']) / mb,
        Y6['chain_fgp_c'] / mb, Y6['chain_fgp_c'] / (Y6['t'] * 1000), Y6['chain_fgp'] / mb, Y6['chain_fgp'] / (Y6['t'] * 1000)),
     'ข้อเสนอถัดไป: (1) ตั้ง floor chain full GP ของ Cassflo 500 ในอินโดนีเซีย (เช่น ≥ 4 บาท/กก. = ระดับ YTD25 ของ Heinz) และทบทวนราคา 3 รายใหม่ก่อนต่อสัญญา/ยอมปล่อย volume (2) ผลัก mix ไป Cassmax 102 / Cassflo 600 / Cassflo 800 / Casstex 22 ผ่าน distributor (3) ใส่ USD/IDR clause ในราคา IDR (4) ตรวจต้นทุน TDC ของ Cassflo 500 ที่ขึ้นจน product GP/กก. เหลือ 2.3 (ไตรมาส 1–2/26)',
     'สมมติฐานที่ต้องยืนยัน: USD/THB ปี 2024 ใช้ค่า BOT โดยประมาณ (ไฟล์ TDC ไม่มี) · TDC GP รายลูกค้า = จัดสรรตาม product × ไตรมาส (TDC ขาย TWIN เป็นลูกค้าเดียว; stock timing ทำให้ยอดจัดสรร ≠ shipment จริง ดู Summary) · ไม่มี opex TWIN ในไฟล์ → full cost มีเฉพาะชั้น TDC · เวอร์ชันเต็มรวม native/sago ดูไฟล์ v2',
    ]
    o_rest = o6
    findings[2] = findings[2] % (div(o_rest['chain_fgp'], o_rest['t'] * 1000) or 0)
for i, t in enumerate(findings):
    put(ws, r, 1, f'{i+1}.', f_bold, align=Alignment(vertical='top'))
    put(ws, r, 2, t, f_norm, align=WRAP); ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=11)
    ws.row_dimensions[r].height = 42; r += 1
for c, wdt in zip('ABCDEFGHIJK', (46, 22, 11, 11, 11, 11, 11, 11, 11, 11, 12)): ws.column_dimensions[c].width = wdt
ws.freeze_panes = 'A4'
wb.active = 0
wb.save(OUT)
print('Key findings added', OUT)
