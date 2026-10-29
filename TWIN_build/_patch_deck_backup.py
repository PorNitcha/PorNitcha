# one-off: add backup slide 3 (TDC quadrant base 2025 + TWIN-customer quadrants 2025 / 2026) in the simple page-2 style
p = 'TWIN_build/build_deck.ps1'; s = open(p, encoding='utf-8').read()
b = s.index("$pres.SaveAs($Out)")
new = r'''# ================= Slide 3 (backup): TDC base 2025 + TWIN customers 2025 / 2026 =================
$s3 = $pres.Slides.AddSlide(3, $blank)
Add-Text $s3 20 12 920 26 'Backup: in 2025 TWIN was the only Indonesian account in Grow; by 2026 Heinz and the new Wings volume pulled TWIN below floor' 14 $DARK $false 'l' | Out-Null
Add-Text $s3 20 40 920 14 ('Same quadrant rule as page 2: product GP/kg vs floor 4.7 THB/kg, volume vs base year ' + [char]0x00B7 + ' % = share of volume and GP of the book in each quadrant ' + [char]0x00B7 + ' orange = Indonesian accounts / TWIN customer groups') 8 $LINE $false 'l' | Out-Null
function Draw-Simple($slide, $x0, $y0, $w, $h, $head, $sub, $cellFn) {
  Add-Text $slide $x0 ($y0 - 34) $w 16 $head 10 $DARK $true 'c' | Out-Null
  Add-Text $slide $x0 ($y0 - 18) $w 14 $sub 7.5 $LINE $false 'c' | Out-Null
  $cw = $w / 2; $ch = $h / 2; $g = 4
  $cells = @{ protect = @($x0, $y0); grow = @(($x0 + $cw), $y0); reprice = @($x0, ($y0 + $ch)); fix = @(($x0 + $cw), ($y0 + $ch)) }
  foreach ($k in 'protect','grow','reprice','fix') {
    $cx = $cells[$k][0]; $cy = $cells[$k][1]
    Add-Rect $slide ($cx + $g/2) ($cy + $g/2) ($cw - $g) ($ch - $g) $FILL[$k] | Out-Null
    Add-Text $slide ($cx + 8) ($cy + 6) ($cw - 16) 12 $TITLE[$k] 7.5 $TCOL[$k] $true 'l' | Out-Null
    & $cellFn $slide $k ($cx + 8) ($cy + 22) ($cw - 16)
  }
  Add-Text $slide $x0 ($y0 + $h + 2) $w 10 ([char]0x2190 + ' volume down  |  volume up ' + [char]0x2192) 6.5 $LINE $false 'c' | Out-Null
  $v = Add-Text $slide ($x0 - 82) ($y0 + $h/2 - 6) 150 12 ('above floor ' + [char]0x2191 + '   below floor ' + [char]0x2193) 6.5 $LINE $false 'c'
  $v.Rotation = [single]270
}
function Big-Line($slide, $x, $y, $w, $vs, $gs) { Add-Text $slide $x $y $w 18 ((Pct $vs) + ' vol  ' + [char]0x00B7 + '  ' + (Pct $gs) + ' GP') 12 $DARK $false 'l' | Out-Null }
$cellTdc = {
  param($slide, $k, $x, $y, $w)
  $v = $script:QB.roles.$k
  Big-Line $slide $x $y $w $v.total.v $v.total.g
  Add-Text $slide $x ($y + 19) $w 10 ("$($v.n) accounts " + [char]0x00B7 + ' ' + (Fmt $v.total.kg 1) + ' THB/kg') 6.5 $LINE $false 'l' | Out-Null
  $L = @()
  if ([double]$v.direct.v -ge 0.005) { $L += 'Direct ' + (Pct $v.direct.v) + ' vol ' + [char]0x00B7 + ' ' + (Fmt $v.direct.kg 1) + ' THB/kg: ' + ($v.direct.names -join ', ') }
  if ([double]$v.twin.v -ge 0.005) { $L += 'via TWIN ' + (Pct $v.twin.v) + ' vol ' + [char]0x00B7 + ' TDC ' + (Fmt $v.twin.kg 1) + ' + TWIN ' + (Fmt $v.twin.twin_kg 1) + ' = ' + (Fmt $v.twin.comb_kg 1) + ' THB/kg' }
  if ($L.Count -gt 0) { $tb = Add-Text $slide $x ($y + 33) $w 30 ($L -join "`r") 7 $INDO $false 'l'; $tb.TextFrame.AutoSize = 1 }
}
$cellTwin = {
  param($slide, $k, $x, $y, $w)
  $gs = @($script:QB.groups | Where-Object { $_.role -eq $k })
  if ($gs.Count -eq 0) { Add-Text $slide $x $y $w 14 ([string][char]0x2013) 10 $GREY $false 'l' | Out-Null; return }
  $sv = 0; $sg = 0; foreach ($g in $gs) { $sv += [double]$g.vshare; $sg += [double]$g.gshare }
  Big-Line $slide $x $y $w $sv $sg
  $L = @(); foreach ($g in $gs) { $L += $g.grp + ': ' + (Pct $g.vshare) + ' vol ' + [char]0x00B7 + ' ' + (Fmt $g.pcomb 1) + ' THB/kg combined' }
  $col = $(if ($gs.Count -eq 1 -and $gs[0].grp -eq 'The rest') { $DARK } else { $INDO })
  $tb = Add-Text $slide $x ($y + 21) $w 30 ($L -join "`r") 7 $col $false 'l'; $tb.TextFrame.AutoSize = 1
}
$qw = 280; $qh = 280; $qy = 110
$script:QB = $D.tdcq.'25'; Draw-Simple $s3 50 $qy $qw $qh 'TDC customers, base 2025' 'FY2025 vs 2027 plan (share of plan)' $cellTdc
$t25 = $D.twinq.'25'; $t26 = $D.twinq.'26'
$script:QB = $t25; Draw-Simple $s3 360 $qy $qw $qh 'TWIN customers, 2025' ('FY2025 vs FY2024 ' + [char]0x00B7 + ' ' + (Fmt $t25.total_t 0) + ' t ' + [char]0x00B7 + ' ' + (Fmt $t25.total_pcomb 1) + ' THB/kg combined') $cellTwin
$script:QB = $t26; Draw-Simple $s3 670 $qy $qw $qh 'TWIN customers, 2026' ('YTD Sep-26 vs YTD Sep-25 ' + [char]0x00B7 + ' ' + (Fmt $t26.total_t 0) + ' t ' + [char]0x00B7 + ' ' + (Fmt $t26.total_pcomb 1) + ' THB/kg combined') $cellTwin
# one read line under each quadrant
$r1 = 'Indonesia direct was already in Fix in 2025 (' + (Fmt $D.tdcq.'25'.roles.fix.direct.kg 1) + ' THB/kg); TWIN was in Grow at ' + (Fmt $D.tdcq.'25'.roles.grow.twin.comb_kg 1) + ' THB/kg combined. Japfa had no 2025 history.'
$heinz25 = $t25.groups | Where-Object { $_.grp -eq 'Heinz' }; $heinz26 = $t26.groups | Where-Object { $_.grp -eq 'Heinz' }; $wings26 = $t26.groups | Where-Object { $_.grp -eq 'Wings' }
$r2 = 'Every TWIN group was above floor. Heinz was ' + (Pct $heinz25.vshare) + ' of TWIN volume at ' + (Fmt $heinz25.pcomb 1) + ' THB/kg combined.'
$r3 = 'Heinz dropped to Fix (' + (Fmt $heinz26.pcomb 1) + ' THB/kg combined). Wings is new at ' + (Fmt $wings26.pcomb 1) + ' (not in a quadrant). Only Bumi Tirta still grows with margin.'
$ry = $qy + $qh + 18
foreach ($pair in @(@(50, $r1), @(360, $r2), @(670, $r3))) { $tb = Add-Text $s3 $pair[0] $ry $qw 40 $pair[1] 8 $DARK $false 'l'; $tb.TextFrame.AutoSize = 1 }
$nt = @(); foreach ($g in @($t26.groups | Where-Object { $_.role -eq 'new' })) { $nt += ($g.grp + ' ' + (Fmt $g.t 0) + ' t at ' + (Fmt $g.pcomb 1) + ' THB/kg combined') }
Add-Text $s3 50 500 880 24 ('Not in a quadrant: TDC base 2025 ' + $D.tdcq.'25'.roles.new.n + ' accounts with no 2025 history (' + (Pct $D.tdcq.'25'.roles.new.total.v) + ' of plan volume, incl. Japfa) ' + [char]0x00B7 + ' TWIN 2026 new groups: ' + ($nt -join '; ') + ' ' + [char]0x00B7 + ' Harum Sari 208 t is a non-TDC product, excluded ' + [char]0x00B7 + ' TWIN quadrants use actual vs prior year because no 2027 plan exists by TWIN customer; GP/kg = product GP, TDC leg vs floor, combined = TDC + TWIN trading margin') 7 $LINE $false 'l' | Out-Null

'''
s = s[:b] + new + s[b:]
s = s.replace("foreach ($i in 1..2) { $pres.Slides.Item($i).Export", "foreach ($i in 1..3) { $pres.Slides.Item($i).Export")
open(p, 'w', encoding='utf-8').write(s); print('ok')
