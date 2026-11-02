# One-off patch (Por 30-Oct): add "benchmark by reaction" + "gap vs reaction bench" columns to twit_table_out.py and drop the HTML preview (Excel only).
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:70]); s = s.replace(a, b)
s = s[:s.index('# ---------- HTML preview ----------')] + "print('ok', len(rows), 'rows')\n"
rep("J, XL, HT = sys.argv[1], sys.argv[2], sys.argv[3]", "J, XL = sys.argv[1], sys.argv[2]")
rep("# Writes an Excel sheet (values, formatted) and an HTML page for a PNG preview.  Usage: python twit_table_out.py <twit_table.json> <out.xlsx> <out.html>",
    "# Writes an Excel sheet (values, formatted). Benchmarks two ways: same SN and same reaction group (Por 30-Oct).  Usage: python twit_table_out.py <twit_table.json> <out.xlsx>")
H = "'Bench vol\\nYTD 26 (t)', 'YTD 25', 'YTD 26', 'YTD 25', 'YTD 26']"
rep(H, H[:-1] + ", " + H)
rep("(13, 15, 'Benchmark: TDC – non-China'), (16, 17, 'Gap vs bench')]",
    "(13, 15, 'Benchmark by SN: TDC – non-China'), (16, 17, 'Gap vs SN bench'), (18, 20, 'Benchmark by reaction: TDC – non-China'), (21, 22, 'Gap vs reaction bench')]")
rep("rows = []   # (kind, values[17])", "NC = len(COLS)\nrows = []   # (kind, values[NC])")
rep("x['bt'] or None, x['b25'], x['b26'], x['g25'], x['g26']]))", "x['bt'] or None, x['b25'], x['b26'], x['g25'], x['g26'], x['rbt'] or None, x['rb25'], x['rb26'], x['rg25'], x['rg26']]))")
rep("[None] * 16))", "[None] * (NC - 1)))", 2)
rep("line('sn', None, l['sn'], l['name'], RX.get(l['sn'], ''), l, False)", "line('sn', None, l['sn'], l['name'], l['rxg'].replace('PO-XL', 'POXL'), l, False)")
rep("l['name'].title() if l['name'].isupper() else l['name'], l['rx'], l, True)", "l['name'].title() if l['name'].isupper() else l['name'], l['rxg'].replace('PO-XL', 'POXL'), l, True)")
rep("        if i >= 16 and isinstance(x, (int, float)) and x < 0:", "        if i in (16, 17, 21, 22) and isinstance(x, (int, float)) and x < 0:")
rep("FMT = {5: '#,##0', 6: '#,##0', 13: '#,##0'}", "FMT = {5: '#,##0', 6: '#,##0', 13: '#,##0', 18: '#,##0'}")
rep("if i in (5, 7, 9, 11, 13, 16) and kind != 'sec'", "if i in (5, 7, 9, 11, 13, 16, 18, 21) and kind != 'sec'")
rep("W = [30, 8, 22, 9, 9, 9, 8, 8, 8, 8, 9, 9, 10, 8, 8, 8, 8]", "W = [30, 8, 22, 9, 9, 9, 8, 8, 8, 8, 9, 9, 10, 8, 8, 8, 8, 10, 8, 8, 8, 8]")
rep("""         'Gap: direct rows = TDC GP/kg − benchmark; TWIT rows = combined GP/kg − benchmark. Green row = at or above benchmark in YTD 26.',""",
    """         "Benchmark by reaction = TDC full-cost GP/kg of all non-China third-party sales in the SN's reaction group (TDC 'Reaction group'), weighted by the customer's own reaction mix; covers every SN. YTD 25 → YTD 26: " + ', '.join(f"{g} {a:.2f} → {b:.2f}" for g, (a, b) in D['rx_bench'].items()) + '.',
         'Gap: direct rows = TDC GP/kg − benchmark; TWIT rows = combined GP/kg − benchmark (for both SN and reaction). Green row = at or above the SN benchmark in YTD 26.',""")
open(p, 'w', encoding='utf-8').write(s); print('patched out')
d = p.replace('twit_table_out.py', 'twit_table_data.py'); t = open(d, encoding='utf-8').read()
a = "tdc_to_twit={y: dict(t=v['t'], kg=v['kg']) for y, v in tdc_to_twit.items()},"
assert t.count(a) == 1
t = t.replace(a, a + " rx_bench={g: (bench_rg(g, 2025)['kg'], bench_rg(g, 2026)['kg']) for g in ('PO', 'PO-XL', 'XL', 'Others') if bench_rg(g, 2026)['t']},")
open(d, 'w', encoding='utf-8').write(t); print('patched data')
