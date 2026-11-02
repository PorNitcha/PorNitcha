# Patch tdc_partner_tables.py for v4 (Por 30-Oct):
# 1) direct rows keep the empty partner / combined columns (v3 dropped them, so every later column shifted 6 places left)
# 2) China / Indonesia: SN benchmark = non-China / non-Indonesia third parties; reaction benchmark = total TDC (all customers)
# 3) Rest of TDC: reaction benchmark (total TDC) only
# plus a row-length check in write() so a shifted row can never be saved again.
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)
rep("'all3p': lambda r: not r['rel']}", "'all3p': lambda r: not r['rel'], 'total': lambda r: True}")
rep("def stats(items, via, pop):", "def stats(items, via, pop, rpop='total'):")
rep("rbt, brx, _ = bmix(w, pop, p, 'rg')", "rbt, brx, _ = bmix(w, rpop, p, 'rg')")
rep("    if via is not None: v += [d[p]['prt'] for p in PER] + [d[p]['comb'] for p in PER]\n",
    "    v += [d[p]['prt'] for p in PER] + [d[p]['comb'] for p in PER]   # empty on direct rows, but always present so columns line up\n")
rep("+ [d[p]['bsn'] for p in PER] + [d[p]['gsn'] for p in PER] + [d[p]['brx'] for p in PER] + [d[p]['grx'] for p in PER]\nrows_rt",
    "+ [d[p]['brx'] for p in PER] + [d[p]['grx'] for p in PER]\nrows_rt")
rep("""        g = v[gsn26 - 1]; good""", """        assert len(v) == nc, (title[:20], kind, len(v), nc, v[:3])
        g = v[gsn26 - 1]; good""")
rep("(f'Benchmark by reaction: TDC – {popname}', ['Bench vol\\nYTD 26 (t)'] + P3)", "('Benchmark by reaction: total TDC', ['Bench vol\\nYTD 26 (t)'] + P3)")
rep("""            f"Benchmark by reaction = the same customers, all SNs in the same TDC reaction group, weighted by the customer's own reaction mix; covers every SN. FY 25 / YTD 25 / YTD 26: {rxnote(pop)}.",""",
    """            f"Benchmark by reaction = total TDC (all customers, every country, incl. intercompany) in the same TDC reaction group, weighted by the customer's own reaction mix; covers every SN. Bench vol = total TDC tonnes YTD Sep-26 in those groups. FY 25 / YTD 25 / YTD 26: {rxnote('total')}.",""")
rep("RGROUPS = [('Vol (t)', P3), ('TDC GP/kg', P3), ('Benchmark by SN: TDC third-party average', P3), ('Gap vs SN bench', P3), ('Benchmark by reaction: TDC third-party average', P3), ('Gap vs reaction bench', P3)]",
    "RGROUPS = [('Vol (t)', P3), ('TDC GP/kg', P3), ('Benchmark by reaction: total TDC', P3), ('Gap vs reaction bench', P3)]")
rep("""       'Benchmark by SN / by reaction = TDC full-cost GP/kg of all TDC third-party customers (every country; TWIN, TWIT, TW India and Thai Wah PCL left out) on the same SN / reaction group, weighted by the row\\'s own mix. Gap = TDC GP/kg − benchmark. Green row = at or above the SN benchmark in YTD 26.',""",
    """       f"Benchmark by reaction = total TDC full-cost GP/kg (all customers, every country, incl. intercompany) in the same TDC reaction group, weighted by the row's own reaction mix. FY 25 / YTD 25 / YTD 26: {rxnote('total')}. Gap = TDC GP/kg − benchmark. Green row = at or above the benchmark in YTD 26.",""")
rep("[34, 44] + [8] * 18, (12, 13, 14, 18, 19, 20), (3, 4, 5), 14)", "[34, 44] + [8] * 12, (11, 12, 13), (3, 4, 5), 13)")
open(p, 'w', encoding='utf-8').write(s); print('patched')
