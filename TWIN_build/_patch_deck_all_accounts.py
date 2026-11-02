# one-off: TDC quadrants cover every account with a 2027 plan (no 100 t minimum); accounts with no base-year GP use the proxy GP/t; no base-year volume = growing
p = 'TWIN_build/deck_data.py'; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s; assert a in s, a[:70]; s = s.replace(a, b, 1)
rep("D = json.load(open(QUAD, encoding='utf-8')); FLOOR = 4700; MINT = 100",
    "D = json.load(open(QUAD, encoding='utf-8')); FLOOR = 4700; MINT = 0\nimport os\nPROXY = json.load(open(os.path.join(os.path.dirname(QUAD), 'quad2_gp_proxy.json'), encoding='utf-8'))  # TWIN_build/quad_newacct_gp.py\ndef bgp(d, base): return PROXY[d['name']][str(base)]['gpp']\ndef bsrc(d, base): return PROXY[d['name']][str(base)]['src']")
rep("""def role(d, base):
    gp = d['gpp25'] if base == 25 else d['gpp26']; bt = d['t25'] if base == 25 else d['t26a']
    if gp is None or not bt: return 'new'
    g = d['t27'] - bt""",
    """def role(d, base):
    gp = bgp(d, base); bt = (d['t25'] if base == 25 else d['t26a']) or 0
    g = d['t27'] - bt  # no base-year volume = growing (Por 29-Oct: every account in a box)""")
rep("    rows = [d for d in D if d['t27'] >= MINT]\n    gpv = lambda d: ((d['gpp25'] if base == 25 else d['gpp26']) or 0) * d['t27']",
    "    rows = [d for d in D if d['t27'] > MINT]\n    gpv = lambda d: bgp(d, base) * d['t27']")
rep("        out[r] = dict(n=len(rs), total=tot, direct=di, twin=tw)",
    "        px = [d for d in rs if bsrc(d, base) != 'own']\n        out[r] = dict(n=len(rs), total=tot, direct=di, twin=tw, nproxy=len(px), vproxy=sum(d['t27'] for d in px) / totV)")
open(p, 'w', encoding='utf-8').write(s); print('ok')
