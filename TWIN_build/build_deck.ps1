# Build the 2-slide Indonesia deck with PowerPoint COM from deck_data.json
# Usage: powershell -File build_deck.ps1 <deck_data.json> <out.pptx> <png dir>
# Slide 1: customer x SN table (Por's layout 29-Oct: group headers Vol / GP/kg / Benchmarking, vertical group separators, one gap column)
# Slide 2: TDC quadrant (base 2025 / 2026, Indonesia split direct / via TWIN) + TWIN-customer quadrant, simple boxes with labelled mini tables
param([string]$Json, [string]$Out, [string]$PngDir)
$D = Get-Content -LiteralPath $Json -Encoding UTF8 -Raw | ConvertFrom-Json
function RGB($hex) { $r = [Convert]::ToInt32($hex.Substring(0,2),16); $g = [Convert]::ToInt32($hex.Substring(2,2),16); $b = [Convert]::ToInt32($hex.Substring(4,2),16); return $r + $g*256 + $b*65536 }
$DARK = RGB '14213d'; $LINE = RGB '6b7280'; $INDO = RGB 'e4572e'; $GREY = RGB '9ca3af'; $RED = RGB 'c00000'; $WHITE = RGB 'ffffff'; $SEP = RGB 'a6a6a6'
$FILL = @{ protect = (RGB 'e2efda'); grow = (RGB 'ddebf7'); fix = (RGB 'f6dcd4'); reprice = (RGB 'ececec') }
$TCOL = @{ protect = (RGB '2a7d4f'); grow = (RGB '1f5f9f'); fix = (RGB 'c0392b'); reprice = (RGB '6b7280') }
$TITLE = @{ protect = 'PROTECT'; grow = 'GROW WITH MARGIN'; fix = 'FIX PRICE BEFORE VOLUME'; reprice = 'REPRICE / EXIT' }
$FONT = 'Arial'
function Fmt($x, $d) { if ($null -eq $x) { return [string][char]0x2013 }; return ('{0:N' + $d + '}') -f [double]$x }
function Pct($x) { if ($null -eq $x -or [double]$x -lt 0.005) { return [string][char]0x2013 }; return ('{0:N0}%' -f ([double]$x * 100)) }
function GapColor($g) { if ($null -eq $g) { return $LINE }; if ([double]$g -lt 0) { return $RED }; return $DARK }

$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Add(0)
$pres.PageSetup.SlideWidth = [single]960; $pres.PageSetup.SlideHeight = [single]540
$W = $pres.PageSetup.SlideWidth; $H = $pres.PageSetup.SlideHeight
$blank = $pres.SlideMaster.CustomLayouts.Item(7)

function Add-Text($slide, $x, $y, $w, $h, $text, $size, $color, $bold, $align) {
  $s = $slide.Shapes.AddTextbox(1, $x, $y, $w, $h)
  $tf = $s.TextFrame; $tf.WordWrap = -1; $tf.AutoSize = 0
  $tf.MarginLeft = [single]2; $tf.MarginRight = [single]2; $tf.MarginTop = [single]1; $tf.MarginBottom = [single]1
  $tr = $tf.TextRange; $tr.Text = $text; $tr.Font.Name = $FONT; $tr.Font.Size = [single]$size; $tr.Font.Color.RGB = $color
  $tr.Font.Bold = $(if ($bold) { -1 } else { 0 })
  $tr.ParagraphFormat.Alignment = $(if ($align -eq 'c') { 2 } elseif ($align -eq 'r') { 3 } else { 1 })
  $s.Width = [single]$w; $s.Height = [single]$h
  return $s
}
function Add-Rect($slide, $x, $y, $w, $h, $fill) {
  $s = $slide.Shapes.AddShape(1, $x, $y, $w, $h)
  $s.Fill.ForeColor.RGB = $fill; $s.Fill.Solid(); $s.Line.Visible = 0; $s.Shadow.Visible = 0
  return $s
}
function Set-Cell($tbl, $r, $c, $text, $size, $color, $align, $fill, $bold) {
  $cell = $tbl.Cell($r, $c); $tr = $cell.Shape.TextFrame.TextRange
  $tr.Text = $text; $tr.Font.Name = $FONT; $tr.Font.Size = [single]$size; $tr.Font.Color.RGB = $color; $tr.Font.Bold = $(if ($bold) { -1 } else { 0 })
  $tr.ParagraphFormat.Alignment = $(if ($align -eq 'c') { 2 } elseif ($align -eq 'r') { 3 } else { 1 })
  $cell.Shape.TextFrame.MarginLeft = [single]3; $cell.Shape.TextFrame.MarginRight = [single]3; $cell.Shape.TextFrame.MarginTop = [single]1; $cell.Shape.TextFrame.MarginBottom = [single]1
  $cell.Shape.TextFrame.VerticalAnchor = 3
  if ($null -ne $fill) { $cell.Shape.Fill.ForeColor.RGB = $fill; $cell.Shape.Fill.Solid(); $cell.Shape.Fill.Transparency = [single]0 } else { $cell.Shape.Fill.Visible = 0 }
  foreach ($b in 1,2,3,4) { $cell.Borders.Item($b).Visible = 0 }
}
function Set-Border($tbl, $r, $c, $side, $color, $w) { $b = $tbl.Cell($r, $c).Borders.Item($side); $b.Visible = -1; $b.ForeColor.RGB = $color; $b.Weight = [single]$w }
function New-Table($slide, $x, $y, $rows, $cols, $widths, $rowH) {
  $w = 0; foreach ($cw in $widths) { $w += $cw }
  $s = $slide.Shapes.AddTable($rows, $cols, $x, $y, $w, $rowH * $rows)
  $t = $s.Table
  try { $t.ApplyStyle('{2D5ABB26-0587-4C30-8999-92F81FD0307C}', 0) } catch {}
  $t.FirstRow = 0; $t.HorizBanding = 0
  for ($c = 1; $c -le $cols; $c++) { $t.Columns.Item($c).Width = [single]$widths[$c-1] }
  for ($r = 1; $r -le $rows; $r++) { $t.Rows.Item($r).Height = [single]$rowH }
  return $s
}
function Bottom-Border($tbl, $r, $cols, $color, $w) { for ($c = 1; $c -le $cols; $c++) { Set-Border $tbl $r $c 3 $color $w } }

# ================= Slide 1: customer x SN table =================
$s1 = $pres.Slides.AddSlide(1, $blank)
Add-Text $s1 20 12 920 44 ('Indonesia by customer and product: direct accounts earn 4' + [char]0x2013 + '7 THB/kg less than the same SKUs sold elsewhere; via TWIN only Bumi Tirta beats the benchmark') 16 $DARK $false 'l' | Out-Null
$cols = 12; $widths = @(92, 38, 90, 44, 54, 54, 44, 44, 58, 56, 54, 56); $rowH = 12.2
$rows = 2
foreach ($c in $D.direct) { $rows += 1 + $c.sns.Count }
$rows += 2
foreach ($c in $D.via) { $rows += 1 + $c.sns.Count }
$rows += 2
$TY = 70
$tsh = New-Table $s1 20 $TY $rows $cols $widths $rowH; $t = $tsh.Table
$SECT = RGB 'd9d9d9'; $CUST = RGB 'f2f2f2'; $TOT = RGB 'e2e2e2'
# row 1: group headers (boxed labels)
for ($c = 1; $c -le $cols; $c++) { Set-Cell $t 1 $c '' 7.5 $LINE 'c' $null $false }
$t.Cell(1, 5).Merge($t.Cell(1, 6)); $t.Cell(1, 7).Merge($t.Cell(1, 9)); $t.Cell(1, 10).Merge($t.Cell(1, 12))
Set-Cell $t 1 5 'Vol' 8 $LINE 'c' $null $false; Set-Cell $t 1 7 'GP/kg' 8 $LINE 'c' $null $false; Set-Cell $t 1 10 'Benchmarking : Non-Indonesia' 8 $LINE 'c' $null $false
foreach ($c in 5, 7, 10) { foreach ($side in 1, 2, 3, 4) { Set-Border $t 1 $c $side $SEP 0.75 } }
$t.Rows.Item(1).Height = [single]13
# row 2: column headers
$hdr = @('Customer', 'SN', 'Product', 'Reaction', 'YTD 25', 'YTD 26', 'TDC (1)', 'TWIN (2)', ('Combined' + "`r" + '(1) + (2)'), ('Bench vol' + "`r" + '(t)'), ('Bench' + "`r" + 'GP/kg'), ('Gap vs' + "`r" + 'bench'))
for ($c = 1; $c -le $cols; $c++) { Set-Cell $t 2 $c $hdr[$c-1] 7.5 $LINE $(if ($c -le 4) { 'l' } else { 'c' }) $null $false }
$t.Rows.Item(2).Height = [single]22
Bottom-Border $t 2 $cols $DARK 1
function Sep-Borders($t, $r) { Set-Border $t $r 5 2 $SEP 0.5; Set-Border $t $r 7 2 $SEP 0.5; Set-Border $t $r 10 2 $SEP 0.5; Set-Border $t $r 12 4 $SEP 0.5 }
Sep-Borders $t 2
function CustRow($t, $r, $name, $sub, $t25, $t26, $tdc, $twin, $comb, $bt, $bkg, $gap, $fill) {
  Set-Cell $t $r 1 $name 8 $DARK 'l' $fill $false; Set-Cell $t $r 2 '' 8 $DARK 'l' $fill $false; Set-Cell $t $r 3 $sub 7.5 $LINE 'l' $fill $false; Set-Cell $t $r 4 '' 8 $DARK 'l' $fill $false
  Set-Cell $t $r 5 (Fmt $t25 0) 8 $DARK 'r' $fill $true; Set-Cell $t $r 6 (Fmt $t26 0) 8 $DARK 'r' $fill $true
  Set-Cell $t $r 7 (Fmt $tdc 2) 8 $DARK 'r' $fill $true; Set-Cell $t $r 8 $(if ($null -eq $twin) { '' } else { Fmt $twin 2 }) 8 $DARK 'r' $fill $true; Set-Cell $t $r 9 $(if ($null -eq $comb) { '' } else { Fmt $comb 2 }) 8 $DARK 'r' $fill $true
  Set-Cell $t $r 10 (Fmt $bt 0) 8 $DARK 'r' $fill $true; Set-Cell $t $r 11 (Fmt $bkg 2) 8 $DARK 'r' $fill $true; Set-Cell $t $r 12 (Fmt $gap 2) 8 (GapColor $gap) 'r' $fill $true
  Sep-Borders $t $r
}
function SnRow($t, $r, $l, $tdc, $twin, $comb, $gap) {
  Set-Cell $t $r 1 '' 7.5 $DARK 'l' $null $false; Set-Cell $t $r 2 $l.sn 7.5 $LINE 'l' $null $false; Set-Cell $t $r 3 (($l.name -split '/')[0].Trim()) 7.5 $LINE 'l' $null $false; Set-Cell $t $r 4 $l.rx 7.5 $LINE 'l' $null $false
  Set-Cell $t $r 5 (Fmt $l.t25 0) 7.5 $LINE 'r' $null $false; Set-Cell $t $r 6 (Fmt $l.t26 0) 7.5 $LINE 'r' $null $false
  Set-Cell $t $r 7 (Fmt $tdc 2) 7.5 $LINE 'r' $null $false; Set-Cell $t $r 8 $(if ($null -eq $twin) { '' } else { Fmt $twin 2 }) 7.5 $LINE 'r' $null $false; Set-Cell $t $r 9 $(if ($null -eq $comb) { '' } else { Fmt $comb 2 }) 7.5 $LINE 'r' $null $false
  Set-Cell $t $r 10 (Fmt $l.bt 0) 7.5 $LINE 'r' $null $false; Set-Cell $t $r 11 (Fmt $l.bkg 2) 7.5 $LINE 'r' $null $false; Set-Cell $t $r 12 (Fmt $gap 2) 7.5 (GapColor $gap) 'r' $null $false
  Sep-Borders $t $r
}
function SectRow($t, $r, $text) { $t.Cell($r, 1).Merge($t.Cell($r, $cols)); Set-Cell $t $r 1 $text 8 $DARK 'l' $SECT $false }
$r = 3
SectRow $t $r ('Route to market: TDC ' + [char]0x2192 + ' customer (direct)'); $r++
foreach ($c in $D.direct) {
  CustRow $t $r $c.cust '' $c.t25 $c.t26 $c.kg26 $null $null $c.bt $c.bkg $c.gap $CUST; $r++
  foreach ($l in $c.sns) { SnRow $t $r $l $l.kg26 $null $null $l.gap; $r++ }
}
$dt = $D.direct_total; CustRow $t $r ('Subtotal ' + [char]0x2014 + ' TDC direct') 'all direct accounts' $dt.t25 $dt.t26 $dt.kg26 $null $null $dt.bt $dt.bkg $dt.gap $TOT; Bottom-Border $t $r $cols $LINE 0.75; $r++
SectRow $t $r ('Route to market: TDC ' + [char]0x2192 + ' TWIN ' + [char]0x2192 + ' customer'); $r++
foreach ($c in $D.via) {
  $sub = ''; $nm = $c.cust; if ($c.cust -eq 'Wings') { $sub = 'Glico, Karunia, Prakarsa' }; if ($c.cust -eq 'The rest') { $nm = 'The rest of TWIN'; $sub = "$($c.n26) smaller customers" }
  CustRow $t $r $nm $sub $c.t25 $c.t26 $c.tdc $c.twin $c.comb $c.bt $c.bkg $c.gapc $CUST; $r++
  foreach ($l in $c.sns) { SnRow $t $r $l $l.tdc $l.twin $l.comb $l.gapc; $r++ }
}
$vt = $D.via_total; CustRow $t $r ('Subtotal ' + [char]0x2014 + ' via TWIN') 'TDC products' $vt.t25 $vt.t26 $vt.tdc $vt.twin $vt.comb $vt.bt $vt.bkg $vt.gapc $TOT; Bottom-Border $t $r $cols $LINE 0.75; $r++
# key messages (right)
$kx = 20 + 684 + 14; $kw = $W - $kx - 16
$rest = $D.via | Where-Object { $_.cust -eq 'The rest' }
$msg = @()
$msg += 'Direct (7,400 t at 1.04 THB/kg vs 5.59 benchmark)'
$msg += [char]0x2022 + ' TAPBIND-321 and CASSMAX-23 are sold almost only to Indonesia (benchmark 26 t and 6 t): the Indonesian price is the product price, no other customer funds it.'
$msg += [char]0x2022 + ' CASSTEX-22 (XL) is 0.4' + [char]0x2013 + '0.7 THB/kg for everyone: a product-cost problem, not an Indonesia price problem.'
$msg += [char]0x2022 + ' CP and Japfa buy TAPBIND-321 at 0.3' + [char]0x2013 + '1.3 vs 8.0 for the 26 t sold elsewhere.'
$msg += ''
$msg += 'Via TWIN (3,261 t at 2.11 TDC + 1.79 TWIN = 3.90 combined)'
$msg += [char]0x2022 + ' Bumi Tirta clears the benchmark at both legs (9.69 combined, +6.61 vs benchmark; 40% of TWIN GP on 18% of its volume).'
$msg += [char]0x2022 + ' Heinz and Wings (2,219 t of CASSFLO-500) earn 1.35 at TDC vs 6.55 benchmark; TWIN adds 0.30 for Heinz and loses 0.53 on Wings, so even combined they are 4.9' + [char]0x2013 + '5.7 below.'
$msg += [char]0x2022 + ' The rest of TWIN (' + $rest.n26 + ' accounts, ' + (Fmt $rest.t26 0) + ' t) is below benchmark on the TDC leg (' + (Fmt $rest.tdc 2) + ') but TWIN adds ' + (Fmt $rest.twin 2) + ': combined ' + (Fmt $rest.comb 2) + ', +' + (Fmt $rest.gapc 2) + ' vs benchmark.'
$msg += [char]0x2022 + ' Harum Sari (208 t) is a non-TDC product and sits outside this view.'
$tb = Add-Text $s1 $kx $TY $kw 300 ($msg -join "`r") 8 $DARK $false 'l'
$tb.Fill.ForeColor.RGB = RGB 'fff2cc'; $tb.Fill.Solid(); $tb.Line.Visible = -1; $tb.Line.ForeColor.RGB = RGB 'e4c15a'; $tb.Line.Weight = [single]0.75
$tb.TextFrame.MarginLeft = [single]8; $tb.TextFrame.MarginRight = [single]8; $tb.TextFrame.MarginTop = [single]6
$tb.TextFrame.TextRange.ParagraphFormat.SpaceAfter = [single]3; $tb.TextFrame.AutoSize = 1
Add-Text $s1 20 500 920 28 ('YTD Jan' + [char]0x2013 + 'Sep 2026 ' + [char]0x00B7 + ' GP/kg at full cost (after idle, PPA and other adjustments), same basis as the CEO summary sheet ' + [char]0x00B7 + ' TDC products only (native, sago, Fibioca and coarse flour excluded); TDC GP/kg for via-TWIN rows is allocated by SKU and quarter ' + [char]0x00B7 + ' benchmark = TDC sales of the same SKU to non-Indonesian customers ' + [char]0x00B7 + ' gap = Indonesia ' + [char]0x2212 + ' benchmark (direct: TDC GP/kg; via TWIN: combined GP/kg), negative = red ' + [char]0x00B7 + ' SKUs under 30 t in 2026 are folded into the customer line ' + [char]0x00B7 + ' Source: TDC Profitability data_Actual, TWIN customer breakdown') 7 $LINE $false 'l' | Out-Null

# ================= helper: quadrant box with labelled mini table (scalable) =================
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

$pres.SaveAs($Out)
foreach ($i in 1..4) { $pres.Slides.Item($i).Export((Join-Path $PngDir ("slide$i.png")), 'PNG', 1920, 1080) }
$pres.Close(); $app.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
Write-Output "saved $Out"
