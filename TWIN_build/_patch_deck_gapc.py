# one-off: combined-vs-benchmark gap column + The rest of TWIN block (deck_data.py and build_deck.ps1)
def patch(p, subs):
    s = open(p, encoding='utf-8').read()
    for a, b in subs:
        assert a in s, (p, a[:70]); s = s.replace(a, b, 1)
    open(p, 'w', encoding='utf-8').write(s)
patch('TWIN_build/deck_data.py', [
 ("VIA = ['Heinz', 'Wings', 'Bumi Tirta']", "VIA = ['Heinz', 'Wings', 'Bumi Tirta', 'The rest']"),
 ("bt=b['t'], bkg=b['kg'], gap=(s26['tdc'] - b['kg']) if (s26['tdc'] is not None and b['kg'] is not None) else None))",
  "bt=b['t'], bkg=b['kg'], gap=(s26['tdc'] - b['kg']) if (s26['tdc'] is not None and b['kg'] is not None) else None, gapc=(s26['comb'] - b['kg']) if (s26['comb'] is not None and b['kg'] is not None) else None))"),
 ("    members = sorted(set(r['label'] for r in rows))\n    return dict(cust=g, members=members, t25=a25['t'], t26=a26['t'], tdc=a26['tdc'], twin=a26['twin'], comb=a26['comb'], bt=bt, bkg=kg(bgp, bt), gap=(a26['tdc'] - kg(bgp, bt)) if a26['tdc'] is not None and bt else None, sns=lines)",
  "    members = sorted(set(r['label'] for r in rows)); n26 = len(set(r['label'] for r in tytd(rows, 2026)))\n    return dict(cust=g, members=members, n26=n26, t25=a25['t'], t26=a26['t'], tdc=a26['tdc'], twin=a26['twin'], comb=a26['comb'], bt=bt, bkg=kg(bgp, bt), gap=(a26['tdc'] - kg(bgp, bt)) if a26['tdc'] is not None and bt else None, gapc=(a26['comb'] - kg(bgp, bt)) if a26['comb'] is not None and bt else None, sns=lines)"),
 ("via_total = dict(t25=v25['t'], t26=v26['t'], tdc=v26['tdc'], twin=v26['twin'], comb=v26['comb'], bt=bv['t'], bkg=bv['kg'], gap=v26['tdc'] - bv['kg'])",
  "via_total = dict(t25=v25['t'], t26=v26['t'], tdc=v26['tdc'], twin=v26['twin'], comb=v26['comb'], bt=bv['t'], bkg=bv['kg'], gap=v26['tdc'] - bv['kg'], gapc=v26['comb'] - bv['kg'])"),
 ("print(f\"  {c['cust']} {c['members']}: t25", "print(f\"  {c['cust']} n26={c['n26']} gapc={f(c['gapc'])}: t25"),
])
patch('TWIN_build/build_deck.ps1', [
 ("$cols = 12; $widths = @(112, 42, 112, 38, 46, 46, 44, 44, 50, 52, 50, 52); $rowH = 13.2", "$cols = 13; $widths = @(100, 40, 104, 36, 44, 44, 42, 42, 48, 50, 46, 52, 56); $rowH = 13.2"),
 ("'Bench vol (t)', 'Bench GP/kg', 'Gap TDC vs bench')", "'Bench vol (t)', 'Bench GP/kg', 'Gap TDC vs bench', 'Gap combined vs bench')"),
 ("function CustRow($t, $r, $name, $sub, $t25, $t26, $tdc, $twin, $comb, $bt, $bkg, $gap, $fill) {", "function CustRow($t, $r, $name, $sub, $t25, $t26, $tdc, $twin, $comb, $bt, $bkg, $gap, $fill, $gapc) {"),
 ("Set-Cell $t $r 12 (Fmt $gap 2) 8.5 (GapColor $gap) 'r' $fill\n}", "Set-Cell $t $r 12 (Fmt $gap 2) 8.5 (GapColor $gap) 'r' $fill; Set-Cell $t $r 13 $(if ($null -eq $gapc) { '' } else { Fmt $gapc 2 }) 8.5 (GapColor $gapc) 'r' $fill\n}"),
 ("  $bt = $l.bt; $bkg = $l.bkg; $gap = $l.gap\n  Set-Cell $t $r 10 (Fmt $bt 0) 8 $LINE 'r' $null; Set-Cell $t $r 11 (Fmt $bkg 2) 8 $LINE 'r' $null; Set-Cell $t $r 12 (Fmt $gap 2) 8 (GapColor $gap) 'r' $null\n}",
  "  $bt = $l.bt; $bkg = $l.bkg; $gap = $l.gap; $gapc = $null; if ($null -ne $comb) { $gapc = $l.gapc }\n  Set-Cell $t $r 10 (Fmt $bt 0) 8 $LINE 'r' $null; Set-Cell $t $r 11 (Fmt $bkg 2) 8 $LINE 'r' $null; Set-Cell $t $r 12 (Fmt $gap 2) 8 (GapColor $gap) 'r' $null; Set-Cell $t $r 13 $(if ($null -eq $gapc) { '' } else { Fmt $gapc 2 }) 8 (GapColor $gapc) 'r' $null\n}"),
 ("  $sub = ''; if ($c.cust -eq 'Wings') { $sub = 'Glico, Karunia, Prakarsa' }\n  CustRow $t $r $c.cust $sub $c.t25 $c.t26 $c.tdc $c.twin $c.comb $c.bt $c.bkg $c.gap $CUST; $r++",
  "  $sub = ''; $nm = $c.cust; if ($c.cust -eq 'Wings') { $sub = 'Glico, Karunia, Prakarsa' }; if ($c.cust -eq 'The rest') { $nm = 'The rest of TWIN'; $sub = \"$($c.n26) smaller customers\" }\n  CustRow $t $r $nm $sub $c.t25 $c.t26 $c.tdc $c.twin $c.comb $c.bt $c.bkg $c.gap $CUST $c.gapc; $r++"),
 ("'TDC products, 60 customers' $vt.t25 $vt.t26 $vt.tdc $vt.twin $vt.comb $vt.bt $vt.bkg $vt.gap $TOT;", "'TDC products, all customers' $vt.t25 $vt.t26 $vt.tdc $vt.twin $vt.comb $vt.bt $vt.bkg $vt.gap $TOT $vt.gapc;"),
 ("$kx = 20 + 688 + 12; $kw = $W - $kx - 20", "$kx = 20 + 704 + 10; $kw = $W - $kx - 16"),
 ("($msg -join \"`r\") 8.5 $DARK $false 'l'", "($msg -join \"`r\") 8 $DARK $false 'l'"),
 ("$msg += [char]0x2022 + ' Harum Sari (208 t) is a non-TDC product and sits outside this view.'",
  "$rest = $D.via | Where-Object { $_.cust -eq 'The rest' }\n$msg += [char]0x2022 + ' The rest of TWIN (' + $rest.n26 + ' accounts, ' + (Fmt $rest.t26 0) + ' t) is below benchmark on the TDC leg (' + (Fmt $rest.tdc 2) + ') but TWIN adds ' + (Fmt $rest.twin 2) + ': combined ' + (Fmt $rest.comb 2) + ', ' + (Fmt $rest.gapc 2) + ' vs benchmark.'\n$msg += [char]0x2022 + ' Harum Sari (208 t) is a non-TDC product and sits outside this view.'"),
 ("' Bumi Tirta clears the benchmark at both legs (9.69 combined, 40% of TWIN GP on 18% of its volume).'", "' Bumi Tirta clears the benchmark at both legs (9.69 combined, +6.61 vs benchmark; 40% of TWIN GP on 18% of its volume).'"),
 ("and TWIN adds 0.30 for Heinz and loses 0.53 on Wings.'", "TWIN adds 0.30 for Heinz and loses 0.53 on Wings, so even combined they are 4.9' + [char]0x2013 + '5.7 below.'"),
])
print('ok')
