# one-off: replace slides 2-3 with (2) combined 4-box page, (3) TDC 2025 + 2026 enlarged, (4) TWIN customers 2025 + 2026 enlarged
p = 'TWIN_build/build_deck.ps1'; s = open(p, encoding='utf-8').read()
a = s.index("# ================= Slide 2: one quadrant"); b = s.index("$pres.SaveAs($Out)")
new = r'''# ================= helper: quadrant box with labelled mini table (scalable) =================
$RH = 10
function Draw-Box($slide, $x0, $y0, $w, $h, $label, $cellFn) {
  $sc = $script:SC
  Add-Text $slide $x0 ($y0 - 15 * $sc) $w (13 * $sc) $label (9 * $sc) $DARK $false 'c' | Out-Null
  $cw = $w / 2; $ch = $h / 2; $g = 4
  $cells = @{ protect = @($x0, $y0); grow = @(($x0 + $cw), $y0); reprice = @($x0, ($y0 + $ch)); fix = @(($x0 + $cw), ($y0 + $ch)) }
  foreach ($k in 'protect','grow','reprice','fix') {
    $cx = $cells[$k][0]; $cy = $cells[$k][1]
    Add-Rect $slide ($cx + $g/2) ($cy + $g/2) ($cw - $g) ($ch - $g) $FILL[$k] | Out-Null
    Add-Text $slide ($cx + 8) ($cy + 4) ($cw - 16) (14 * $sc) $TITLE[$k] (9 * $sc) $TCOL[$k] $true 'l' | Out-Null
    & $cellFn $slide $k $cx $cy $cw $ch
  }
  Add-Text $slide $x0 ($y0 + $h + 1) $w (10 * $sc) ([char]0x2190 + ' volume below base year  |  volume above base year ' + [char]0x2192) (6.5 * $sc) $LINE $false 'c' | Out-Null
  $v = Add-Text $slide ($x0 - 108) ($y0 + $h/2 - 6) 200 12 ('product GP/kg above floor ' + [char]0x2191 + '   below floor ' + [char]0x2193) (6.5 * $sc) $LINE $false 'c'
  $v.Rotation = [single]270
}
function Mini-Header($tt, $labels, $sz) { for ($c = 1; $c -le $labels.Count; $c++) { Set-Cell $tt 1 $c $labels[$c-1] $sz $LINE $(if ($c -eq 1) { 'l' } else { 'r' }) $null $false }; Bottom-Border $tt 1 $labels.Count $LINE 0.5 }
function Fit-Widths($base, $avail) { $sum = 0; foreach ($x in $base) { $sum += $x }; $out = @(); foreach ($x in $base) { $out += [double]$x * $avail / $sum }; return ,$out }
$cellFn2 = {
  param($slide, $k, $cx, $cy, $cw, $ch)
  $sc = $script:SC; $rh = $RH * $sc; $q = $script:Q; $v = $q.roles.$k
  Add-Text $slide ($cx + 8) ($cy + 5) ($cw - 16) (12 * $sc) ("$($v.n) accounts") (6.5 * $sc) $LINE $false 'r' | Out-Null
  $tw = Fit-Widths @(64, 40, 40, 40) ($cw - 16); $ts = New-Table $slide ($cx + 8) ($cy + 18 * $sc) 4 4 $tw $rh; $tt = $ts.Table
  Mini-Header $tt @('', 'Vol share', 'GP share', 'GP/kg') (6.5 * $sc)
  $rowsDef = @(@('Total', $v.total, $DARK), @('Indonesia direct', $v.direct, $INDO), @('via TWIN', $v.twin, $INDO))
  for ($i = 0; $i -lt 3; $i++) {
    $lab = $rowsDef[$i][0]; $p = $rowsDef[$i][1]; $col = $rowsDef[$i][2]
    if ($i -gt 0 -and [double]$p.v -lt 0.005) { $col = $GREY }
    Set-Cell $tt ($i+2) 1 $lab (7 * $sc) $col 'l' $null $false; Set-Cell $tt ($i+2) 2 (Pct $p.v) (7 * $sc) $col 'r' $null $false; Set-Cell $tt ($i+2) 3 (Pct $p.g) (7 * $sc) $col 'r' $null $false; Set-Cell $tt ($i+2) 4 (Fmt $p.kg 1) (7 * $sc) $col 'r' $null $false
  }
  $names = @(); $names += $v.direct.names; $names += $v.twin.names; $y = $cy + 18 * $sc + $rh * 4 + 2
  if ($names.Count -gt 0) { Add-Text $slide ($cx + 8) $y ($cw - 16) (10 * $sc) ($names -join ', ') (6.5 * $sc) $INDO $false 'l' | Out-Null; $y += 9 * $sc }
  if ($null -ne $v.twin.twin_kg) { Add-Text $slide ($cx + 8) $y ($cw - 16) (10 * $sc) ('via TWIN GP/kg: TDC ' + (Fmt $v.twin.kg 1) + ' + TWIN ' + (Fmt $v.twin.twin_kg 1) + ' = ' + (Fmt $v.twin.comb_kg 1) + ' combined') (6.5 * $sc) $DARK $false 'l' | Out-Null }
}
$cellFn3 = {
  param($slide, $k, $cx, $cy, $cw, $ch)
  $sc = $script:SC; $rh = $RH * $sc; $q = $script:Q; $gs = @($q.groups | Where-Object { $_.role -eq $k })
  Add-Text $slide ($cx + 8) ($cy + 5) ($cw - 16) (12 * $sc) ("$($gs.Count) group(s)") (6.5 * $sc) $LINE $false 'r' | Out-Null
  if ($gs.Count -eq 0) { Add-Text $slide ($cx + 8) ($cy + 22 * $sc) ($cw - 16) (10 * $sc) ([string][char]0x2013) (7 * $sc) $GREY $false 'l' | Out-Null; return }
  $tw = Fit-Widths @(44, 32, 32, 24, 26, 26) ($cw - 16); $ts = New-Table $slide ($cx + 8) ($cy + 18 * $sc) ($gs.Count + 1) 6 $tw $rh; $tt = $ts.Table
  Mini-Header $tt @('', 'Vol %', 'GP %', 'TDC', 'TWIN', 'Comb') (6.5 * $sc)
  for ($i = 0; $i -lt $gs.Count; $i++) {
    $g = $gs[$i]; $col = $(if ($g.grp -eq 'The rest') { $DARK } else { $INDO })
    Set-Cell $tt ($i+2) 1 $g.grp (7 * $sc) $col 'l' $null $false; Set-Cell $tt ($i+2) 2 (Pct $g.vshare) (7 * $sc) $col 'r' $null $false; Set-Cell $tt ($i+2) 3 (Pct $g.gshare) (7 * $sc) $col 'r' $null $false
    Set-Cell $tt ($i+2) 4 (Fmt $g.ptdc 1) (7 * $sc) $col 'r' $null $false; Set-Cell $tt ($i+2) 5 (Fmt $g.twin 1) (7 * $sc) $col 'r' $null $false; Set-Cell $tt ($i+2) 6 (Fmt $g.pcomb 1) (7 * $sc) $col 'r' $null $false
  }
  $tl = @(); foreach ($g in $gs) { $tl += ($g.grp + ' ' + (Fmt $g.t 0) + ' t, prev ' + (Fmt $g.tprev 0)) }
  Add-Text $slide ($cx + 8) ($cy + 18 * $sc + $rh * ($gs.Count + 1) + 3) ($cw - 16) (10 * $sc) ($tl -join [string]([char]0x00B7 + ' ')) (6.5 * $sc) $LINE $false 'l' | Out-Null
}
function Read-Box($slide, $y, $text, $size) {
  $mb = Add-Text $slide 70 $y 860 40 $text $size $DARK $false 'l'
  $mb.Fill.ForeColor.RGB = RGB 'fff2cc'; $mb.Fill.Solid(); $mb.Line.Visible = -1; $mb.Line.ForeColor.RGB = RGB 'e4c15a'; $mb.Line.Weight = [single]0.75; $mb.TextFrame.MarginLeft = [single]6; $mb.TextFrame.MarginTop = [single]3; $mb.TextFrame.AutoSize = 1
}
# shared numbers for the read boxes
$f26 = $D.tdcq.'26'.roles.fix; $f25 = $D.tdcq.'25'.roles.fix; $g25 = $D.tdcq.'25'.roles.grow; $rp26 = $D.tdcq.'26'.roles.reprice
$t25 = $D.twinq.'25'; $t26 = $D.twinq.'26'
$heinz25 = $t25.groups | Where-Object { $_.grp -eq 'Heinz' }; $heinz26 = $t26.groups | Where-Object { $_.grp -eq 'Heinz' }; $wings26 = $t26.groups | Where-Object { $_.grp -eq 'Wings' }; $bumi26 = $t26.groups | Where-Object { $_.grp -eq 'Bumi Tirta' }
$n25 = $D.tdcq.'25'.roles.new; $n26 = $D.tdcq.'26'.roles.new
$nt = @(); foreach ($g in @($t26.groups | Where-Object { $_.role -eq 'new' })) { $nt += ($g.grp + ' ' + (Fmt $g.t 0) + ' t at TDC ' + (Fmt $g.ptdc 1) + ' + TWIN ' + (Fmt $g.twin 1) + ' = ' + (Fmt $g.pcomb 1) + ' THB/kg') }
$tdcNote = 'Not in the four quadrants: base 2025 ' + $n25.n + ' accounts with no 2025 history = ' + (Pct $n25.total.v) + ' of plan volume (Indonesia: ' + (($n25.direct.names + $n25.twin.names) -join ', ') + ') ' + [char]0x00B7 + ' base 2026 ' + $n26.n + ' accounts = ' + (Pct $n26.total.v)
$twinNote = '2025: Wings and Harum Sari had no volume ' + [char]0x00B7 + ' 2026, new and not in the quadrants: ' + ($nt -join '; ') + ' ' + [char]0x00B7 + ' Harum Sari 208 t is a non-TDC product, outside this view'
$twinLabel25 = 'Base 2025: FY2025 vs FY2024 ' + [char]0x00B7 + ' ' + (Fmt $t25.total_t 0) + ' t ' + [char]0x00B7 + ' GP/kg TDC ' + (Fmt $t25.total_ptdc 1) + ' + TWIN ' + (Fmt $t25.total_twin 1) + ' = ' + (Fmt $t25.total_pcomb 1)
$twinLabel26 = 'Base 2026: YTD Sep-26 vs YTD Sep-25 ' + [char]0x00B7 + ' ' + (Fmt $t26.total_t 0) + ' t ' + [char]0x00B7 + ' GP/kg TDC ' + (Fmt $t26.total_ptdc 1) + ' + TWIN ' + (Fmt $t26.total_twin 1) + ' = ' + (Fmt $t26.total_pcomb 1)
$readTdc = 'On the 2026 base every Indonesian account with history sits in "Fix price before volume" (direct ' + (Pct $f26.direct.v) + ' of the 2027 plan volume for ' + (Pct $f26.direct.g) + ' of GP at ' + (Fmt $f26.direct.kg 1) + ' THB/kg; via TWIN ' + (Pct $f26.twin.v) + ' for ' + (Pct $f26.twin.g) + ' at ' + (Fmt $f26.twin.kg 1) + ' on the TDC leg).'
$readTwin = 'Inside TWIN, Heinz fell from Grow to Fix and the new Wings tonnes came in below floor with a negative TWIN margin: together ' + (Pct ([double]$heinz26.vshare + [double]$wings26.vshare)) + ' of TWIN' + [char]0x2019 + 's volume for ' + (Pct ([double]$heinz26.gshare + [double]$wings26.gshare)) + ' of its GP, while Bumi Tirta (' + (Pct $bumi26.vshare) + ' of volume, ' + (Pct $bumi26.gshare) + ' of GP) and the tail earn 10+ THB/kg combined.'
$readRole = 'Role for Indonesia = fill otherwise-idle capacity at a floor price: a volume cap on the fix-price book (no growth until price is fixed), growth tonnes only in the Grow quadrant (' + (Pct $D.tdcq.'26'.roles.grow.total.v) + ' of volume, ' + (Pct $D.tdcq.'26'.roles.grow.total.g) + ' of GP). TWIN grows only where the combined margin clears the floor; Heinz and Wings are re-priced in IDR with FX pass-through before any further volume.'

# ================= Slide 2: combined (TDC top, TWIN bottom) =================
$script:SC = 1.0
$s2 = $pres.Slides.AddSlide(2, $blank)
Add-Text $s2 20 10 920 24 ('Indonesia' + [char]0x2019 + 's role is to leverage fixed cost: control its fix-price volume; inside TWIN only Bumi Tirta grows with margin') 14 $DARK $false 'l' | Out-Null
Add-Text $s2 20 34 920 22 ('Vol share / GP share = share of the book shown in each box ' + [char]0x00B7 + ' GP/kg = base-year product GP in THB/kg at TDC level (floor 4.7); via TWIN and TWIN customers also show TDC + TWIN trading margin = combined' + "`r" + 'Top: TDC customers, share of the 2027 plan (GP = plan tonnes ' + [char]0x00D7 + ' base-year GP/t), accounts with a plan ' + [char]0x2265 + ' 100 t ' + [char]0x00B7 + ' Bottom: TWIN customers buying TDC products, share of the TWIN book; volume axis = actual vs prior year because no 2027 plan exists by TWIN customer') 7 $LINE $false 'l' | Out-Null
$bw = 400; $bh = 160
Add-Text $s2 20 68 920 12 'TDC customers (HVA AP 2027 quadrant)' 8.5 $DARK $false 'l' | Out-Null
$by = 96
$script:Q = $D.tdcq.'25'; Draw-Box $s2 70 $by $bw $bh 'Base 2025 actual (FY)' $cellFn2
$script:Q = $D.tdcq.'26'; Draw-Box $s2 530 $by $bw $bh 'Base 2026 YTD-Sep, annualised' $cellFn2
Add-Text $s2 70 ($by + $bh + 11) 860 10 $tdcNote 6.5 $LINE $false 'l' | Out-Null
Add-Text $s2 20 ($by + $bh + 24) 920 12 'TWIN customers (TDC products only)' 8.5 $DARK $false 'l' | Out-Null
$by2 = $by + $bh + 52
$script:Q = $t25; Draw-Box $s2 70 $by2 $bw $bh $twinLabel25 $cellFn3
$script:Q = $t26; Draw-Box $s2 530 $by2 $bw $bh $twinLabel26 $cellFn3
Add-Text $s2 70 ($by2 + $bh + 11) 860 10 $twinNote 6.5 $LINE $false 'l' | Out-Null
Read-Box $s2 ($by2 + $bh + 24) ('Read: ' + $readTdc + ' ' + $readTwin + "`r" + $readRole) 7.5

# ================= Slide 3: TDC customers 2025 vs 2026 =================
$script:SC = 1.3
$s3 = $pres.Slides.AddSlide(3, $blank)
Add-Text $s3 20 10 920 24 'TDC customers: Indonesia moved from Grow + Fix in 2025 to Fix only in 2026' 14 $DARK $false 'l' | Out-Null
Add-Text $s3 20 34 920 22 ('Share of the 2027 plan (volume = plan tonnes, GP = plan tonnes ' + [char]0x00D7 + ' base-year product GP/t) ' + [char]0x00B7 + ' floor 4,700 THB/t product GP ' + [char]0x00B7 + ' accounts with a 2027 plan ' + [char]0x2265 + ' 100 t ' + [char]0x00B7 + ' same data and rules as the HVA AP 2027 customer quadrant' + "`r" + 'Indonesia split into direct export accounts and PT Thai Wah Indonesia (via TWIN) ' + [char]0x00B7 + ' GP/kg = base-year product GP in THB/kg at TDC level; via TWIN also shown as TDC + TWIN trading margin = combined') 7.5 $LINE $false 'l' | Out-Null
$bw3 = 420; $bh3 = 310; $by3 = 100
$script:Q = $D.tdcq.'25'; Draw-Box $s3 60 $by3 $bw3 $bh3 'Base 2025 actual (FY)' $cellFn2
$script:Q = $D.tdcq.'26'; Draw-Box $s3 520 $by3 $bw3 $bh3 'Base 2026 YTD-Sep, annualised' $cellFn2
Add-Text $s3 60 ($by3 + $bh3 + 16) 880 10 $tdcNote 7 $LINE $false 'l' | Out-Null
$read3 = 'Read: on the 2025 base Indonesia direct already sat in Fix (' + (Pct $f25.direct.v) + ' of plan volume at ' + (Fmt $f25.direct.kg 1) + ' THB/kg) while via TWIN was in Grow at ' + (Fmt $g25.twin.kg 1) + ' THB/kg (' + (Fmt $g25.twin.comb_kg 1) + ' combined). ' + $readTdc + ' Japfa moved to Reprice / Exit (' + (Fmt $rp26.direct.kg 1) + ' THB/kg) with its 2027 plan cut to 100 t.' + "`r" + $readRole
Read-Box $s3 ($by3 + $bh3 + 32) $read3 8

# ================= Slide 4: TWIN customers 2025 vs 2026 =================
$s4 = $pres.Slides.AddSlide(4, $blank)
Add-Text $s4 20 10 920 24 'TWIN customers: Heinz fell to Fix and Wings came in below floor; only Bumi Tirta grows with margin' 14 $DARK $false 'l' | Out-Null
Add-Text $s4 20 34 920 22 ('TWIN customers buying TDC products (Heinz / Wings / Bumi Tirta / the rest) ' + [char]0x00B7 + ' Vol % / GP % = share of the TWIN book ' + [char]0x00B7 + ' quadrant rule on the TDC leg: product GP/kg vs floor 4.7 THB/kg' + "`r" + 'Volume axis = actual vs prior year (FY2025 vs FY2024, YTD Sep-26 vs YTD Sep-25) because no 2027 plan exists by TWIN customer ' + [char]0x00B7 + ' TDC / TWIN / Comb = GP/kg on the TDC leg, TWIN trading margin, combined') 7.5 $LINE $false 'l' | Out-Null
$script:Q = $t25; Draw-Box $s4 60 $by3 $bw3 $bh3 $twinLabel25 $cellFn3
$script:Q = $t26; Draw-Box $s4 520 $by3 $bw3 $bh3 $twinLabel26 $cellFn3
Add-Text $s4 60 ($by3 + $bh3 + 16) 880 10 $twinNote 7 $LINE $false 'l' | Out-Null
$read4 = 'Read: in 2025 every TWIN group was above floor (Heinz ' + (Pct $heinz25.vshare) + ' of TWIN volume at ' + (Fmt $heinz25.pcomb 1) + ' THB/kg combined). ' + $readTwin + "`r" + 'Action: TWIN grows only where the combined margin clears the floor (Bumi Tirta, the tail); Heinz and Wings are re-priced in IDR with FX pass-through before any further volume; no new CASSFLO-500 accounts below floor.'
Read-Box $s4 ($by3 + $bh3 + 32) $read4 8

'''
s = s[:a] + new + s[b:]
s = s.replace("foreach ($i in 1..3) { $pres.Slides.Item($i).Export", "foreach ($i in 1..4) { $pres.Slides.Item($i).Export")
open(p, 'w', encoding='utf-8').write(s); print('ok')
