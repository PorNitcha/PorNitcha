# one-off: a TWIN group with no prior-year volume counts as volume growing, placed by TDC-leg product GP/kg (Wings -> Fix)
def patch(p, subs):
    s = open(p, encoding='utf-8').read()
    for a, b in subs:
        assert a in s, (p, a[:70]); s = s.replace(a, b, 1)
    open(p, 'w', encoding='utf-8').write(s)
patch('TWIN_build/deck_data.py', [
 ("        elif p['t'] < 1: role = 'new'\n", "        elif p['t'] < 1: role = 'grow' if (c['ptdc'] or 0) >= FLOOR_KG else 'fix'  # new in base year = volume growing (Por 29-Oct)\n"),
 ("out.append(dict(grp=g, role=role, t=c['t'], tprev=p['t'],", "out.append(dict(grp=g, role=role, isnew=p['t'] < 1, t=c['t'], tprev=p['t'],"),
])
patch('TWIN_build/build_deck.ps1', [
 ("Set-Cell $tt ($i+2) 1 $g.grp (7 * $sc) $col 'l' $null $false;", "Set-Cell $tt ($i+2) 1 $(if ($g.isnew) { $g.grp + ' (new)' } else { $g.grp }) (7 * $sc) $col 'l' $null $false;"),
 ("$twinNote = '2025: Wings and Harum Sari had no volume ' + [char]0x00B7 + ' 2026, new and not in the quadrants: ' + ($nt -join '; ') + ' ' + [char]0x00B7 + ' Harum Sari 208 t is a non-TDC product, outside this view'",
  "$twinNote = '2025: Wings and Harum Sari had no volume ' + [char]0x00B7 + ' 2026: Wings is new (no YTD Sep-25 volume), counted as volume growing and placed by its TDC GP/kg ' + [char]0x00B7 + ' Harum Sari 208 t is a non-TDC product, outside this view'"),
])
print('ok')
