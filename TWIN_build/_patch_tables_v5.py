# Patch tdc_partner_tables.py for v5 (Por 30-Oct): Rest of TDC gets SN / Product / Reaction lines under each customer,
# Por's v4 layout touches (FY 25 + YTD 25 grouped per block, medium box around the benchmark block). China / Indonesia sheets come from Por's saved v4.
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)
rep("""def rvals(a, b, d):
    return [a, b] + [d[p]['t'] for p in PER]""", """def rvals(a, b, d, sn=None, prod=None, rx=None):
    return [a, b, sn, prod, rx] + [d[p]['t'] for p in PER]""")
rep("""    rows_rt.append(('cust', rvals(c, f'{len(custs)} customer' + ('s' if len(custs) != 1 else ''), stats(cx, None, 'all3p'))))""",
    """    rows_rt.append(('country', rvals(c, f'{len(custs)} customer' + ('s' if len(custs) != 1 else ''), stats(cx, None, 'all3p'))))""")
rep("""        rows_rt.append(('sn', rvals(None, cu + (' (related party)' if it[0]['rel'] else ''), d)))""",
    """        rows_rt.append(('cust', rvals(None, cu + (' (related party)' if it[0]['rel'] else ''), d)))
        sns = ord_by(it, lambda r: r['sn'])
        for sn in sns:
            ds = stats([r for r in it if r['sn'] == sn], None, 'all3p')
            if max(ds[p]['t'] for p in PER) < MINT and len(sns) > 1: continue
            rows_rt.append(('sn', rvals(None, None, ds, sn, SNNAME.get(sn, sn), RG.get(sn, '').replace('PO-XL', 'POXL'))))""")
rep("""    if small: rows_rt.append(('sn', rvals(None, f"Other customers""", """    if small: rows_rt.append(('cust', rvals(None, f"Other customers""")
# write(): 'country' rows, return the last table row
rep("""            bold = kind in ('cust', 'sub');""", """            bold = kind in ('cust', 'sub', 'country');""")
rep("""            if kind == 'cust': c.fill = F_CUST
            elif kind == 'sub'""", """            if kind == 'cust': c.fill = F_CUST
            elif kind == 'country': c.fill = F_SUB
            elif kind == 'sub'""")
rep("""    for i, t in enumerate(notes): ws.cell(r + 1 + i, 1, t).font""", """    last = r - 1
    for i, t in enumerate(notes): ws.cell(r + 1 + i, 1, t).font""")
rep("""    ws.freeze_panes = ws.cell(5, len(lead) + 1).coordinate; ws.sheet_view.showGridLines = False""",
    """    ws.freeze_panes = ws.cell(5, len(lead) + 1).coordinate; ws.sheet_view.showGridLines = False
    return last
med = Side(style='medium', color='000000')
def por_layout(ws, groups_at, box, last):
    \"\"\"Por's v4 touches: FY 25 + YTD 25 columns grouped (outline level 1, open) in each block; medium box around the benchmark block\"\"\"
    from openpyxl.utils import get_column_letter as L
    for c1 in groups_at: ws.column_dimensions.group(L(c1), L(c1 + 1), outline_level=1, hidden=False)
    c1, c2 = box
    for r in range(3, last + 1):
        for c in range(c1, c2 + 1):
            x = ws.cell(r, c); b = x.border
            x.border = Border(left=med if c == c1 else b.left, right=med if c == c2 else b.right, top=med if r == 3 else b.top, bottom=med if r == last else b.bottom)""")
rep("""write(ws, 'Rest of TDC — HVA customers outside Indonesia and China, by country and customer, FY 2025 / YTD Sep-25 / YTD Sep-26 (reported FX, THB/kg)', ['Country / route', 'Customer'], RGROUPS, rows_rt,""",
    """last_rt = write(ws, 'Rest of TDC — HVA customers outside Indonesia and China, by country, customer and SN, FY 2025 / YTD Sep-25 / YTD Sep-26 (reported FX, THB/kg)', ['Country / route', 'Customer', 'SN', 'Product', 'Reaction'], RGROUPS, rows_rt,""")
rep("""f'Customers under {MINT} t in every period are grouped per country.""", """f'SN lines under {MINT} t in every period are not shown but are in the customer totals. Customers under {MINT} t in every period are grouped per country.""")
rep("[34, 44] + [8] * 12, (12, 13, 14), (3, 4, 5), 14)", "[30, 44, 8, 18, 8] + [8] * 12, (15, 16, 17), (6, 7, 8), 17)\npor_layout(ws, (6, 9, 12, 15), (12, 17), last_rt)")
open(p, 'w', encoding='utf-8').write(s); print('patched')
