# one-off: slide labels/footnotes for the all-accounts TDC quadrants
p = 'TWIN_build/build_deck.ps1'; s = open(p, encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s; assert s.count(a) >= cnt, a[:70]; s = s.replace(a, b, cnt)
rep("(\"$($v.n) accounts\") (6.5 * $sc) $LINE $false 'r' | Out-Null\n  $tw = Fit-Widths @(74, 42, 42, 36)",
    "($(if ($v.nproxy -gt 0) { \"$($v.n) accounts \" + [char]0x00B7 + \" $($v.nproxy) new\" } else { \"$($v.n) accounts\" })) (6.5 * $sc) $LINE $false 'r' | Out-Null\n  $tw = Fit-Widths @(74, 42, 42, 36)")
rep("$tdcNote = 'Not in the four quadrants: base 2025 ' + $n25.n + ' accounts with no 2025 history = ' + (Pct $n25.total.v) + ' of plan volume (Indonesia: ' + (($n25.direct.names + $n25.twin.names) -join ', ') + ') ' + [char]0x00B7 + ' base 2026 ' + $n26.n + ' accounts = ' + (Pct $n26.total.v)",
    "$np25 = 0; $vp25 = 0; $np26 = 0; $vp26 = 0; foreach ($k in 'grow','protect','fix','reprice') { $np25 += $D.tdcq.'25'.roles.$k.nproxy; $vp25 += [double]$D.tdcq.'25'.roles.$k.vproxy; $np26 += $D.tdcq.'26'.roles.$k.nproxy; $vp26 += [double]$D.tdcq.'26'.roles.$k.vproxy }\n$tdcNote = 'All accounts with a 2027 plan are included, so each base adds to 100% ' + [char]0x00B7 + ' new = no GP in the base year (base 2025: ' + $np25 + ' accounts, ' + (Pct $vp25) + ' of plan volume; base 2026: ' + $np26 + ', ' + (Pct $vp26) + '): counted as volume growing and valued at their own other-year GP/kg, else at the base-year TDC average GP/kg of the SKUs in their 2027 plan'")
rep("accounts with a plan ' + [char]0x2265 + ' 100 t", "all accounts with a 2027 plan")
rep("accounts with a 2027 plan ' + [char]0x2265 + ' 100 t", "all accounts with a 2027 plan")
rep("$readTdc = 'On the 2026 base every Indonesian account with history sits in", "$readTdc = 'On the 2026 base every Indonesian account with history sits in")
open(p, 'w', encoding='utf-8').write(s); print('ok')
