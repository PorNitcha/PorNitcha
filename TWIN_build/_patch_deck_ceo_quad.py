# one-off: replace the cluttered slide 2 with a single base-2026 quadrant + 3 callouts
p = 'TWIN_build/build_deck.ps1'; s = open(p, encoding='utf-8').read()
a = s.index("# ================= helper: simple quadrant box"); b = s.index("$pres.SaveAs($Out)")
new = r'''# ================= Slide 2: one quadrant (base 2026) + Indonesia callouts =================
$s2 = $pres.Slides.AddSlide(2, $blank)
Add-Text $s2 20 14 920 30 ('Indonesia' + [char]0x2019 + 's role is to leverage fixed cost ' + [char]0x2014 + ' every Indonesian account sits in "Fix price before volume", so its volume is capped until price is fixed') 15 $DARK $false 'l' | Out-Null
Add-Text $s2 20 46 920 14 ('TDC customer quadrant, base 2026 (YTD Sep annualised) vs 2027 plan ' + [char]0x00B7 + ' % = share of the 2027 plan volume and of its GP at 2026 product GP/kg ' + [char]0x00B7 + ' floor 4.7 THB/kg ' + [char]0x00B7 + ' orange = Indonesian accounts (direct export and via PT Thai Wah Indonesia)') 8 $LINE $false 'l' | Out-Null
$Q = $D.tdcq.'26'; $Q25 = $D.tdcq.'25'
$x0 = 60; $y0 = 84; $bw = 560; $bh = 340; $cw = $bw / 2; $ch = $bh / 2; $g = 5
$cells = @{ protect = @($x0, $y0); grow = @(($x0 + $cw), $y0); reprice = @($x0, ($y0 + $ch)); fix = @(($x0 + $cw), ($y0 + $ch)) }
foreach ($k in 'protect','grow','reprice','fix') {
  $cx = $cells[$k][0]; $cy = $cells[$k][1]; $v = $Q.roles.$k
  Add-Rect $s2 ($cx + $g/2) ($cy + $g/2) ($cw - $g) ($ch - $g) $FILL[$k] | Out-Null
  Add-Text $s2 ($cx + 14) ($cy + 10) ($cw - 28) 18 $TITLE[$k] 11 $TCOL[$k] $true 'l' | Out-Null
  Add-Text $s2 ($cx + 14) ($cy + 34) ($cw - 28) 30 ((Pct $v.total.v) + ' of volume  ' + [char]0x00B7 + '  ' + (Pct $v.total.g) + ' of GP') 17 $DARK $false 'l' | Out-Null
  Add-Text $s2 ($cx + 14) ($cy + 62) ($cw - 28) 14 ("$($v.n) accounts " + [char]0x00B7 + ' average ' + (Fmt $v.total.kg 1) + ' THB/kg') 8 $LINE $false 'l' | Out-Null
  $L = @()
  if ([double]$v.direct.v -ge 0.005) { $L += 'Indonesia direct  ' + (Pct $v.direct.v) + ' of volume ' + [char]0x00B7 + ' ' + (Pct $v.direct.g) + ' of GP ' + [char]0x00B7 + ' ' + (Fmt $v.direct.kg 1) + ' THB/kg' + "`r" + '   ' + ($v.direct.names -join ', ') }
  if ([double]$v.twin.v -ge 0.005) { $L += 'via TWIN  ' + (Pct $v.twin.v) + ' of volume ' + [char]0x00B7 + ' ' + (Pct $v.twin.g) + ' of GP ' + [char]0x00B7 + ' ' + (Fmt $v.twin.kg 1) + ' THB/kg at TDC (+ ' + (Fmt $v.twin.twin_kg 1) + ' TWIN margin)' + "`r" + '   PT Thai Wah Indonesia: Heinz, Wings, Bumi Tirta and 35 smaller customers' }
  if ($k -eq 'grow') { $L += 'No Indonesian account. In 2025 via TWIN was here at 6.1 THB/kg (' + (Pct $Q25.roles.grow.twin.v) + ' of volume).' }
  if ($k -eq 'protect') { $L += 'No Indonesian account.' }
  if ($k -eq 'reprice' -and $v.direct.names.Count -gt 0) { $L += ($v.direct.names -join ', ') + ' (' + (Fmt $v.direct.kg 1) + ' THB/kg, plan cut to 100 t)' }
  $col = $(if ($k -eq 'grow' -or $k -eq 'protect') { $GREY } else { $INDO })
  $tb = Add-Text $s2 ($cx + 14) ($cy + 82) ($cw - 28) 60 ($L -join "`r") 8.5 $col $false 'l'
  $tb.TextFrame.TextRange.ParagraphFormat.SpaceAfter = [single]4; $tb.TextFrame.AutoSize = 1
}
Add-Text $s2 $x0 ($y0 + $bh + 4) $bw 12 ([char]0x2190 + ' 2027 plan below 2026 volume   |   2027 plan above 2026 volume ' + [char]0x2192) 8 $LINE $false 'c' | Out-Null
$v = Add-Text $s2 ($x0 - 120) ($y0 + $bh/2 - 7) 220 14 ('product GP/kg above floor ' + [char]0x2191 + '      below floor ' + [char]0x2193) 8 $LINE $false 'c'
$v.Rotation = [single]270
$n26 = $Q.roles.new
Add-Text $s2 $x0 ($y0 + $bh + 18) $bw 12 ('Not shown: ' + $n26.n + ' accounts with no 2026 history = ' + (Pct $n26.total.v) + ' of plan volume') 7 $LINE $false 'l' | Out-Null
# right: three callouts
$rx = 650; $rw = 290; $f = $Q.roles.fix; $tw25 = $Q25.roles.grow.twin; $tw26 = $f.twin
$tq = $D.twinq.'26'; $bumi = $tq.groups | Where-Object { $_.grp -eq 'Bumi Tirta' }; $heinz = $tq.groups | Where-Object { $_.grp -eq 'Heinz' }; $wings = $tq.groups | Where-Object { $_.grp -eq 'Wings' }
$indoV = [double]$f.direct.v + [double]$f.twin.v; $indoG = [double]$f.direct.g + [double]$f.twin.g
function Callout($slide, $x, $y, $w, $big, $head, $body) {
  Add-Rect $slide $x $y $w 104 (RGB 'f7f7f7') | Out-Null
  Add-Text $slide ($x + 12) ($y + 8) ($w - 24) 30 $big 20 $INDO $false 'l' | Out-Null
  Add-Text $slide ($x + 12) ($y + 36) ($w - 24) 16 $head 9 $DARK $true 'l' | Out-Null
  $tb = Add-Text $slide ($x + 12) ($y + 52) ($w - 24) 48 $body 8 $DARK $false 'l'
  $tb.TextFrame.AutoSize = 1
}
Callout $s2 $rx 84 $rw ((Pct $indoV) + ' of volume for ' + (Pct $indoG) + ' of GP') 'Indonesia in the 2027 plan' ('All of it in "Fix price before volume": direct ' + (Pct $f.direct.v) + ' / ' + (Pct $f.direct.g) + ' (Indo Asia Tirta, CP Indonesia), via TWIN ' + (Pct $f.twin.v) + ' / ' + (Pct $f.twin.g) + '. Nothing in Grow or Protect.')
Callout $s2 $rx 198 $rw ((Fmt $tw25.kg 1) + ' ' + [char]0x2192 + ' ' + (Fmt $tw26.kg 1) + ' THB/kg') 'Via TWIN fell from Grow to Fix' ('TDC product GP/kg on sales to PT Thai Wah Indonesia, 2025 ' + [char]0x2192 + ' 2026 YTD. TWIN' + [char]0x2019 + 's own margin also fell ' + (Fmt $D.twinq.'25'.total_twin 1) + ' ' + [char]0x2192 + ' ' + (Fmt $tq.total_twin 1) + ', so the chain earns ' + (Fmt $tw26.comb_kg 1) + ' vs ' + (Fmt $tw25.comb_kg 1) + ' a year ago.')
Callout $s2 $rx 312 $rw ((Pct ([double]$heinz.vshare + [double]$wings.vshare)) + ' of TWIN volume below floor') 'Inside TWIN: Heinz and Wings' ('Heinz + Wings = ' + (Pct ([double]$heinz.vshare + [double]$wings.vshare)) + ' of TWIN' + [char]0x2019 + 's volume for ' + (Pct ([double]$heinz.gshare + [double]$wings.gshare)) + ' of its GP (' + (Fmt $heinz.pcomb 1) + ' and ' + (Fmt $wings.pcomb 1) + ' THB/kg combined). Bumi Tirta is the only account growing with margin: ' + (Pct $bumi.vshare) + ' of volume, ' + (Pct $bumi.gshare) + ' of GP at ' + (Fmt $bumi.pcomb 1) + ' combined.')
# bottom message
$m2 = 'Role for Indonesia = fill otherwise-idle capacity at a floor price. Decision asked: cap 2027 Indonesian volume in the fix-price book at the 2026 level until price is restored to the reaction floor; re-price Indo Asia Tirta, CP and Japfa at the next tender; re-index Heinz and Wings in IDR with FX pass-through; grow TWIN only where the combined margin clears the floor (Bumi Tirta, the tail).'
$mb = Add-Text $s2 60 448 880 40 $m2 8.5 $DARK $false 'l'
$mb.Fill.ForeColor.RGB = RGB 'fff2cc'; $mb.Fill.Solid(); $mb.Line.Visible = -1; $mb.Line.ForeColor.RGB = RGB 'e4c15a'; $mb.Line.Weight = [single]0.75; $mb.TextFrame.MarginLeft = [single]8; $mb.TextFrame.MarginTop = [single]5; $mb.TextFrame.AutoSize = 1
Add-Text $s2 60 500 880 24 ('Base 2025 view and the TWIN-customer quadrant are in the backup. Quadrant rule: product GP/kg vs floor 4.7 THB/kg (4.0 full cost + idle/PPA) and 2027 plan vs 2026 annualised volume, accounts with a plan ' + [char]0x2265 + ' 100 t. Via TWIN = PT Thai Wah Indonesia buying TDC products for Heinz, Wings, Bumi Tirta and 35 smaller customers; Harum Sari (non-TDC product) excluded.') 7 $LINE $false 'l' | Out-Null

'''
s = s[:a] + new + s[b:]
open(p, 'w', encoding='utf-8').write(s); print('ok')
