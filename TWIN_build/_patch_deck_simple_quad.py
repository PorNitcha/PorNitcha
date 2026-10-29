# one-off: simple solid-colour quadrant blocks (Keep / Scale / Stop / Fix) with white text, no tables
p = 'TWIN_build/build_deck.ps1'; s = open(p, encoding='utf-8').read()
a = s.index("# ================= helper: compact quadrant box"); b = s.index("# ================= Slide 2:")
new = r'''# ================= helper: simple solid quadrant box =================
$QFILL = @{ protect = (RGB '8fbf9f'); grow = (RGB '2a8c5a'); reprice = (RGB 'c0392b'); fix = (RGB 'e8a317') }
$QWORD = @{ protect = 'Keep'; grow = 'Scale'; reprice = 'Stop'; fix = 'Fix' }
$QSUB = @{ protect = 'above floor, volume flat or down'; grow = 'above floor, volume growing'; reprice = 'below floor, volume down'; fix = 'below floor, volume growing' }
function Draw-Box($slide, $x0, $y0, $w, $h, $label, $cellFn) {
  Add-Text $slide $x0 ($y0 - 15) $w 13 $label 9 $DARK $false 'c' | Out-Null
  $cw = $w / 2; $ch = $h / 2; $g = 4
  $cells = @{ protect = @($x0, $y0); grow = @(($x0 + $cw), $y0); reprice = @($x0, ($y0 + $ch)); fix = @(($x0 + $cw), ($y0 + $ch)) }
  foreach ($k in 'protect','grow','reprice','fix') {
    $cx = $cells[$k][0]; $cy = $cells[$k][1]
    $r = Add-Rect $slide ($cx + $g/2) ($cy + $g/2) ($cw - $g) ($ch - $g) $QFILL[$k] $null 0
    Add-Text $slide ($cx + 8) ($cy + 5) ($cw - 16) 18 $QWORD[$k] 13 $WHITE $true 'l' | Out-Null
    Add-Text $slide ($cx + 8) ($cy + 21) ($cw - 16) 10 $QSUB[$k] 6.5 $WHITE $false 'l' | Out-Null
    & $cellFn $slide $k $cx $cy $cw $ch
  }
  Add-Text $slide $x0 ($y0 + $h + 1) $w 10 ([char]0x2190 + ' volume below base year  |  volume above base year ' + [char]0x2192) 6.5 $LINE $false 'c' | Out-Null
  $v = Add-Text $slide ($x0 - 108) ($y0 + $h/2 - 6) 200 12 ('GP/kg above floor ' + [char]0x2191 + '   below floor ' + [char]0x2193) 6.5 $LINE $false 'c'
  $v.Rotation = [single]270
}
function Add-Lines($slide, $x, $y, $w, $lines, $size) {
  $tb = Add-Text $slide $x $y $w 10 ($lines -join "`r") $size $WHITE $false 'l'
  $tb.TextFrame.TextRange.ParagraphFormat.SpaceAfter = [single]1.5; $tb.TextFrame.AutoSize = 1
}
$cellFn2 = {
  param($slide, $k, $cx, $cy, $cw, $ch)
  $q = $script:Q; $v = $q.roles.$k; $L = @()
  $L += "$($v.n) accounts " + [char]0x00B7 + ' vol ' + (Pct $v.total.v) + ' ' + [char]0x00B7 + ' GP ' + (Pct $v.total.g) + ' ' + [char]0x00B7 + ' ' + (Fmt $v.total.kg 1) + ' THB/kg'
  if ([double]$v.direct.v -ge 0.005) { $L += 'Indonesia direct: vol ' + (Pct $v.direct.v) + ' ' + [char]0x00B7 + ' GP ' + (Pct $v.direct.g) + ' ' + [char]0x00B7 + ' ' + (Fmt $v.direct.kg 1) + ' THB/kg (' + ($v.direct.names -join ', ') + ')' }
  if ([double]$v.twin.v -ge 0.005) { $L += 'via TWIN: vol ' + (Pct $v.twin.v) + ' ' + [char]0x00B7 + ' GP ' + (Pct $v.twin.g) + ' ' + [char]0x00B7 + ' TDC ' + (Fmt $v.twin.kg 1) + ' + TWIN ' + (Fmt $v.twin.twin_kg 1) + ' = ' + (Fmt $v.twin.comb_kg 1) + ' THB/kg' }
  if ($L.Count -eq 1) { $L += 'no Indonesian account' }
  Add-Lines $slide ($cx + 8) ($cy + 34) ($cw - 16) $L 7
}
$cellFn3 = {
  param($slide, $k, $cx, $cy, $cw, $ch)
  $q = $script:Q; $gs = @($q.groups | Where-Object { $_.role -eq $k }); $L = @()
  foreach ($g in $gs) { $L += $g.grp + ': vol ' + (Pct $g.vshare) + ' ' + [char]0x00B7 + ' GP ' + (Pct $g.gshare) + ' ' + [char]0x00B7 + ' TDC ' + (Fmt $g.ptdc 1) + ' + TWIN ' + (Fmt $g.twin 1) + ' = ' + (Fmt $g.pcomb 1) + ' THB/kg ' + [char]0x00B7 + ' ' + (Fmt $g.t 0) + ' t (prev ' + (Fmt $g.tprev 0) + ')' }
  if ($L.Count -eq 0) { $L += [string][char]0x2013 }
  Add-Lines $slide ($cx + 8) ($cy + 34) ($cw - 16) $L 7
}

'''
s = s[:a] + new + s[b:]
# slide 2 subtitle: name the four words
s = s.replace("'Top: TDC customers, share of the 2027 plan", "'Keep = above floor, volume flat or down ' + [char]0x00B7 + ' Scale = above floor, growing ' + [char]0x00B7 + ' Stop = below floor, shrinking (reprice or exit) ' + [char]0x00B7 + ' Fix = below floor, growing (fix price before volume)' + \"`r\" + 'Top: TDC customers, share of the 2027 plan")
s = s.replace("Add-Text $s2 20 34 920 22 (", "Add-Text $s2 20 32 920 30 (")
open(p, 'w', encoding='utf-8').write(s); print('ok')
