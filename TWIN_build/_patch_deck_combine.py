# one-off: replace slides 2 and 3 of build_deck.ps1 with a single 4-box page
p = 'TWIN_build/build_deck.ps1'; s = open(p, encoding='utf-8').read()
a = s.index("# ================= helper: quadrant box"); b = s.index("$pres.SaveAs($Out)")
new = r'''# ================= helper: compact quadrant box =================
function Draw-Box($slide, $x0, $y0, $w, $h, $label, $cellFn) {
  Add-Text $slide $x0 ($y0 - 15) $w 13 $label 9 $DARK $false 'c' | Out-Null
  $cw = $w / 2; $ch = $h / 2
  $cells = @{ protect = @($x0, $y0); grow = @(($x0 + $cw), $y0); reprice = @($x0, ($y0 + $ch)); fix = @(($x0 + $cw), ($y0 + $ch)) }
  foreach ($k in 'protect','grow','reprice','fix') {
    $cx = $cells[$k][0]; $cy = $cells[$k][1]
    Add-Rect $slide $cx $cy $cw $ch $FILL[$k] $WHITE 2 | Out-Null
    & $cellFn $slide $k $cx $cy $cw $ch
  }
  Add-Line $slide ($x0 + $cw) $y0 ($x0 + $cw) ($y0 + $h) $DARK 1 $false | Out-Null
  Add-Line $slide $x0 ($y0 + $ch) ($x0 + $w) ($y0 + $ch) $DARK 1 $true | Out-Null
  Add-Text $slide $x0 ($y0 + $h + 1) $w 10 ([char]0x2190 + ' volume below base year  |  volume above base year ' + [char]0x2192) 6.5 $LINE $false 'c' | Out-Null
  $v = Add-Text $slide ($x0 - 108) ($y0 + $h/2 - 6) 200 12 ('GP/kg above floor ' + [char]0x2191 + '   below floor ' + [char]0x2193) 6.5 $LINE $false 'c'
  $v.Rotation = [single]270
}
function Cell-Title($slide, $k, $cx, $cy, $cw, $sub) { Add-Text $slide ($cx + 5) ($cy + 2) ($cw - 10) 12 $TITLE[$k] 8 $TCOL[$k] $true 'l' | Out-Null; Add-Text $slide ($cx + 5 + 125) ($cy + 3) ($cw - 135) 11 $sub 6.5 $LINE $false 'l' | Out-Null }
$RH = 10.5
$cellFn2 = {
  param($slide, $k, $cx, $cy, $cw, $ch)
  $q = $script:Q; $v = $q.roles.$k
  Cell-Title $slide $k $cx $cy $cw ("$($v.n) accounts")
  $tw = @(62, 36, 36, 40); $ts = New-Table $slide ($cx + 6) ($cy + 16) 4 4 $tw $RH; $tt = $ts.Table
  Set-Cell $tt 1 1 '' 6.5 $LINE 'l' $null; Set-Cell $tt 1 2 'Vol' 6.5 $LINE 'r' $null; Set-Cell $tt 1 3 'GP' 6.5 $LINE 'r' $null; Set-Cell $tt 1 4 'GP/kg' 6.5 $LINE 'r' $null; Bottom-Border $tt 1 4 $LINE 0.5
  $rowsDef = @(@('Total', $v.total, $DARK), @('Indonesia direct', $v.direct, $INDO), @('via TWIN', $v.twin, $INDO))
  for ($i = 0; $i -lt 3; $i++) {
    $lab = $rowsDef[$i][0]; $p = $rowsDef[$i][1]; $col = $rowsDef[$i][2]
    if ($i -gt 0 -and [double]$p.v -lt 0.005) { $col = $GREY }
    Set-Cell $tt ($i+2) 1 $lab 7 $col 'l' $null; Set-Cell $tt ($i+2) 2 (Pct $p.v) 7 $col 'r' $null; Set-Cell $tt ($i+2) 3 (Pct $p.g) 7 $col 'r' $null; Set-Cell $tt ($i+2) 4 (Fmt $p.kg 1) 7 $col 'r' $null
  }
  $names = @(); $names += $v.direct.names; $names += $v.twin.names
  $y = $cy + 16 + $RH * 4 + 1
  if ($names.Count -gt 0) { Add-Text $slide ($cx + 5) $y ($cw - 10) 10 ($names -join ', ') 6.5 $INDO $false 'l' | Out-Null; $y += 9 }
  if ($null -ne $v.twin.twin_kg) { Add-Text $slide ($cx + 5) $y ($cw - 10) 10 ('via TWIN GP/kg: TDC ' + (Fmt $v.twin.kg 1) + ' + TWIN ' + (Fmt $v.twin.twin_kg 1) + ' = ' + (Fmt $v.twin.comb_kg 1) + ' combined') 6.5 $DARK $false 'l' | Out-Null }
}
$cellFn3 = {
  param($slide, $k, $cx, $cy, $cw, $ch)
  $q = $script:Q; $gs = @($q.groups | Where-Object { $_.role -eq $k })
  Cell-Title $slide $k $cx $cy $cw ("$($gs.Count) group(s)")
  if ($gs.Count -eq 0) { Add-Text $slide ($cx + 5) ($cy + 20) ($cw - 10) 10 ([string][char]0x2013) 7 $GREY $false 'l' | Out-Null; return }
  $tw = @(50, 28, 28, 26, 26, 30); $ts = New-Table $slide ($cx + 5) ($cy + 16) ($gs.Count + 1) 6 $tw $RH; $tt = $ts.Table
  $h = @('', 'Vol', 'GP', 'TDC', 'TWIN', 'Comb.'); for ($c = 1; $c -le 6; $c++) { Set-Cell $tt 1 $c $h[$c-1] 6.5 $LINE $(if ($c -eq 1) { 'l' } else { 'r' }) $null }; Bottom-Border $tt 1 6 $LINE 0.5
  for ($i = 0; $i -lt $gs.Count; $i++) {
    $g = $gs[$i]; $col = $(if ($g.grp -eq 'The rest') { $DARK } else { $INDO })
    Set-Cell $tt ($i+2) 1 $g.grp 7 $col 'l' $null; Set-Cell $tt ($i+2) 2 (Pct $g.vshare) 7 $col 'r' $null; Set-Cell $tt ($i+2) 3 (Pct $g.gshare) 7 $col 'r' $null
    Set-Cell $tt ($i+2) 4 (Fmt $g.ptdc 1) 7 $col 'r' $null; Set-Cell $tt ($i+2) 5 (Fmt $g.twin 1) 7 $col 'r' $null; Set-Cell $tt ($i+2) 6 (Fmt $g.pcomb 1) 7 $col 'r' $null
  }
  $y = $cy + 16 + $RH * ($gs.Count + 1) + 1
  $tl = @(); foreach ($g in $gs) { $tl += ($g.grp + ' ' + (Fmt $g.t 0) + ' t (prev ' + (Fmt $g.tprev 0) + ')') }
  Add-Text $slide ($cx + 5) $y ($cw - 10) 10 ($tl -join [string]([char]0x00B7 + ' ')) 6.5 $LINE $false 'l' | Out-Null
}

# ================= Slide 2: TDC quadrant (top) + TWIN-customer quadrant (bottom) =================
$s2 = $pres.Slides.AddSlide(2, $blank)
Add-Text $s2 20 10 920 24 ('Indonesia' + [char]0x2019 + 's role is to leverage fixed cost ' + [char]0x2014 + ' its fix-price volume has to be controlled, not grown; inside TWIN only Bumi Tirta grows with margin') 15 $DARK $false 'l' | Out-Null
Add-Text $s2 20 34 920 22 ('Top: TDC customers, share of the 2027 plan (volume = plan tonnes, GP = plan tonnes ' + [char]0x00D7 + ' base-year product GP/t), floor 4,700 THB/t product GP, accounts with a plan ' + [char]0x2265 + ' 100 t; Indonesia split into direct export accounts and PT Thai Wah Indonesia (via TWIN); GP/kg = base-year product GP at TDC level, via TWIN also as TDC + TWIN trading margin = combined' + "`r" + 'Bottom: TWIN customers buying TDC products (Heinz / Wings / Bumi Tirta / the rest), share of the TWIN book; same rule on the TDC leg (product GP/kg vs 4.7); volume axis = actual vs prior year (FY2025 vs FY2024, YTD Sep-26 vs YTD Sep-25) because no 2027 plan exists by TWIN customer') 7 $LINE $false 'l' | Out-Null
$bw = 400; $bh = 164
# row 1: TDC
Add-Text $s2 20 62 920 12 'TDC customers (HVA AP 2027 quadrant)' 8.5 $DARK $false 'l' | Out-Null
$by = 90
$script:Q = $D.tdcq.'25'; Draw-Box $s2 70 $by $bw $bh 'Base 2025 actual (FY)' $cellFn2
$script:Q = $D.tdcq.'26'; Draw-Box $s2 530 $by $bw $bh 'Base 2026 YTD-Sep, annualised' $cellFn2
$n25 = $D.tdcq.'25'.roles.new; $n26 = $D.tdcq.'26'.roles.new
Add-Text $s2 70 ($by + $bh + 11) 860 10 ('Not in the four quadrants: base 2025 ' + $n25.n + ' accounts with no 2025 history = ' + (Pct $n25.total.v) + ' of plan volume (Indonesia: ' + (($n25.direct.names + $n25.twin.names) -join ', ') + ') ' + [char]0x00B7 + ' base 2026 ' + $n26.n + ' accounts = ' + (Pct $n26.total.v)) 6.5 $LINE $false 'l' | Out-Null
# row 2: TWIN
Add-Text $s2 20 ($by + $bh + 24) 920 12 'TWIN customers (TDC products only)' 8.5 $DARK $false 'l' | Out-Null
$by2 = $by + $bh + 52
$script:Q = $D.twinq.'25'; Draw-Box $s2 70 $by2 $bw $bh ('Base 2025: FY2025 ' + [char]0x00B7 + ' ' + (Fmt $D.twinq.'25'.total_t 0) + ' t ' + [char]0x00B7 + ' TDC ' + (Fmt $D.twinq.'25'.total_ptdc 1) + ' + TWIN ' + (Fmt $D.twinq.'25'.total_twin 1) + ' = ' + (Fmt $D.twinq.'25'.total_pcomb 1) + ' THB/kg') $cellFn3
$script:Q = $D.twinq.'26'; Draw-Box $s2 530 $by2 $bw $bh ('Base 2026: YTD Sep-26 ' + [char]0x00B7 + ' ' + (Fmt $D.twinq.'26'.total_t 0) + ' t ' + [char]0x00B7 + ' TDC ' + (Fmt $D.twinq.'26'.total_ptdc 1) + ' + TWIN ' + (Fmt $D.twinq.'26'.total_twin 1) + ' = ' + (Fmt $D.twinq.'26'.total_pcomb 1) + ' THB/kg') $cellFn3
$new26 = @($D.twinq.'26'.groups | Where-Object { $_.role -eq 'new' })
$nt = @(); foreach ($g in $new26) { $nt += ($g.grp + ' ' + (Fmt $g.t 0) + ' t at TDC ' + (Fmt $g.ptdc 1) + ' + TWIN ' + (Fmt $g.twin 1) + ' = ' + (Fmt $g.pcomb 1) + ' THB/kg') }
Add-Text $s2 70 ($by2 + $bh + 11) 860 10 ('2025: Wings and Harum Sari had no volume ' + [char]0x00B7 + ' 2026, new and not in the quadrants: ' + ($nt -join '; ') + ' ' + [char]0x00B7 + ' Harum Sari 208 t is a non-TDC product, outside this view') 6.5 $LINE $false 'l' | Out-Null
$f26 = $D.tdcq.'26'.roles.fix
$m2 = 'Read: on the 2026 base every Indonesian account with history sits in "Fix price before volume" (direct ' + (Pct $f26.direct.v) + ' of the 2027 plan volume for ' + (Pct $f26.direct.g) + ' of GP at ' + (Fmt $f26.direct.kg 1) + ' THB/kg; via TWIN ' + (Pct $f26.twin.v) + ' for ' + (Pct $f26.twin.g) + ' at ' + (Fmt $f26.twin.kg 1) + ' on the TDC leg). Inside TWIN, Heinz fell from Grow to Fix and the new Wings tonnes came in below floor with a negative TWIN margin: together 68% of TWIN' + [char]0x2019 + 's volume for 31% of its GP, while Bumi Tirta (18% of volume, 40% of GP) and the tail earn 10+ THB/kg combined.' + "`r" + 'Role for Indonesia = fill otherwise-idle capacity at a floor price: a volume cap on the fix-price book (no growth until price is fixed), growth tonnes only in the Grow quadrant (' + (Pct $D.tdcq.'26'.roles.grow.total.v) + ' of volume, ' + (Pct $D.tdcq.'26'.roles.grow.total.g) + ' of GP). TWIN grows only where the combined margin clears the floor; Heinz and Wings are re-priced in IDR with FX pass-through before any further volume.'
$mb = Add-Text $s2 70 ($by2 + $bh + 24) 860 40 $m2 7.5 $DARK $false 'l'
$mb.Fill.ForeColor.RGB = RGB 'fff2cc'; $mb.Fill.Solid(); $mb.Line.Visible = -1; $mb.Line.ForeColor.RGB = RGB 'e4c15a'; $mb.Line.Weight = [single]0.75; $mb.TextFrame.MarginLeft = [single]6; $mb.TextFrame.MarginTop = [single]3; $mb.TextFrame.AutoSize = 1

'''
s = s[:a] + new + s[b:]
s = s.replace("foreach ($i in 1..3) { $pres.Slides.Item($i).Export", "foreach ($i in 1..2) { $pres.Slides.Item($i).Export")
open(p, 'w', encoding='utf-8').write(s); print('ok')
