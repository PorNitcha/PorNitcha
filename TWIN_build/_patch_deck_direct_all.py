# one-off: all direct customers in the table; tighter rows
def patch(p, subs):
    s = open(p, encoding='utf-8').read()
    for a, b in subs:
        assert a in s, (p, a[:70]); s = s.replace(a, b, 1)
    open(p, 'w', encoding='utf-8').write(s)
patch('TWIN_build/deck_data.py', [
 ("DIRECT = [('PT.INDO ASIA TIRTA MANUNGGAL', 'Indo Asia Tirta'), ('PT. CHAROEN POKPHAND INDONESIA', 'CP Indonesia'), ('PT. JAPFA FOOD INDONESIA GEDUNG GRAHA PRABA SAMANTA', 'Japfa')]\ndirect_rows = [r for r in R if r['segment'] == 'Indonesia direct']",
  "SHORTD = {'PT.INDO ASIA TIRTA MANUNGGAL': 'Indo Asia Tirta', 'PT. CHAROEN POKPHAND INDONESIA': 'CP Indonesia', 'PT. JAPFA FOOD INDONESIA GEDUNG GRAHA PRABA SAMANTA': 'Japfa', 'PT. SO GOOD FOOD GEDUNG GRAHA PRABA SAMANTA': 'So Good Food'}\ndirect_rows = [r for r in R if r['segment'] == 'Indonesia direct']\n_dc = {}\nfor r in direct_rows:\n    c = r['customer'].strip(); _dc.setdefault(c, [0, 0])\n    if r['y'] == 2026 and r['m'] <= 9: _dc[c][0] += r['t']\n    if r['y'] == 2025 and r['m'] <= 9: _dc[c][1] += r['t']\nDIRECT = [(c, SHORTD.get(c, c.title()[:24])) for c, v in sorted(_dc.items(), key=lambda kv: (-kv[1][0], -kv[1][1])) if v[0] > 0 or v[1] > 0]"),
 ("direct = [cust_block(c, s, [r for r in direct_rows if r['customer'] == c]) for c, s in DIRECT]", "direct = [cust_block(c, s, [r for r in direct_rows if r['customer'].strip() == c]) for c, s in DIRECT]"),
 ("        if s26['t'] < 30 and s25['t'] < 100: continue\n        b = bench(sn)\n        lines.append(dict(sn=sn, name=SNNAME.get(sn, sn)", "        if s26['t'] < 30 and s25['t'] < 100 and not (len(sns) == 1): continue\n        b = bench(sn)\n        lines.append(dict(sn=sn, name=SNNAME.get(sn, sn)"),
])
patch('TWIN_build/build_deck.ps1', [
 ("$cols = 13; $widths = @(100, 40, 104, 36, 44, 44, 42, 42, 48, 50, 46, 52, 56); $rowH = 13.2", "$cols = 13; $widths = @(100, 40, 104, 36, 44, 44, 42, 42, 48, 50, 46, 52, 56); $rowH = 12.2"),
 ("'incl. So Good Food'", "'all direct accounts'"),
])
s = open('TWIN_build/build_deck.ps1', encoding='utf-8').read()
# smaller fonts in table rows
a = s.index('function CustRow'); b = s.index('$SECT = RGB')
blk = s[a:b].replace(" 8.5 $DARK", " 8 $DARK").replace(" 8.5 (GapColor", " 8 (GapColor").replace(" 8 $LINE", " 7.5 $LINE").replace(" 8 (GapColor $gap) 'r' $null", " 7.5 (GapColor $gap) 'r' $null").replace(" 8 (GapColor $gapc) 'r' $null", " 7.5 (GapColor $gapc) 'r' $null").replace(" 8 $DARK 'l' $null", " 7.5 $DARK 'l' $null")
s = s[:a] + blk + s[b:]
open('TWIN_build/build_deck.ps1', 'w', encoding='utf-8').write(s)
print('ok')
