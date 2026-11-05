# AP2027/AP2028 group consolidation deck v3 (Option B) on the Thai Wah template, built with PowerPoint COM.
# All numbers and sentences come from ap27_v2.json (ap27_v2_data.py + ap27_v2_text.py: ConsoAll for TWPC totals, BU sheets for BUs).
# Usage: powershell -File build_ap27_v3.ps1 <ap27_v2.json> <out.pptx> <png dir> <template.pptx>
# PowerShell notes: variables are case-insensitive (no lower-case twins of the colour constants), single-element nested arrays
# flatten (TR and the driver loop re-wrap them), and short function names must not be built-in aliases.
param([string]$Json, [string]$Out, [string]$PngDir, [string]$Template)
$DATA = Get-Content -LiteralPath $Json -Encoding UTF8 -Raw | ConvertFrom-Json
$TX = $DATA.txt
function RGB($hex) { $r = [Convert]::ToInt32($hex.Substring(0,2),16); $g = [Convert]::ToInt32($hex.Substring(2,2),16); $b = [Convert]::ToInt32($hex.Substring(4,2),16); return $r + $g*256 + $b*65536 }
# TW brand: navy 19226D, cyan 00A6DC
$NAVY = RGB '19226d'; $CYAN = RGB '00a6dc'; $HVAC = RGB 'a8def3'; $GREY = RGB 'a6a6a6'
$KICK = RGB '0089c0'; $GREEN = RGB '2e9e5b'; $RED = RGB 'd64545'; $TEXT = RGB '333f50'; $MUTED = RGB '7f8a9a'
$WHITE = RGB 'ffffff'; $TINT = RGB 'e6f5fb'; $LINE = RGB 'd9dee7'; $NOTEBG = RGB 'e6f5fb'
$FONT = 'Aptos'
# stacking convention: Food at the bottom, then HVA (incl. Waxy), then Starch on top
$BUCOL = @{ Food = $NAVY; HVA = $HVAC; Starch = $CYAN; Other = $GREY }
$BUTXT = @{ Food = $WHITE; HVA = $NAVY; Starch = $WHITE }
$STACK = @('Food', 'HVA', 'Starch')
$DASH = [string][char]0x2013; $ARROW = [string][char]0x2192; $DOT = [string][char]0x00B7; $DELTA = [string][char]0x0394

function N0($x) { if ($null -eq $x) { return $DASH }; $v = [double]$x; if ([Math]::Abs($v) -lt 0.5) { return $DASH }; if ($v -lt 0) { return ('({0:N0})' -f (-$v)) }; return ('{0:N0}' -f $v) }
function N1($x) { if ($null -eq $x) { return '' }; $v = [double]$x; if ([Math]::Abs($v) -lt 0.05) { return $DASH }; if ($v -lt 0) { return ('({0:N1})' -f (-$v)) }; return ('{0:N1}' -f $v) }
function SG($x) { $v = [double]$x; if ([Math]::Abs($v) -lt 0.5) { return '0' }; if ($v -gt 0) { return ('+{0:N0}' -f $v) }; return ('({0:N0})' -f (-$v)) }
function PC($x) { if ($null -eq $x) { return '' }; $v = [double]$x; if ([Math]::Abs($v) -gt 1) { return 'n.m.' }; return ('{0:N1}%' -f ($v * 100)) }
function GR($a, $b) { $a = [double]$a; $b = [double]$b; if ($a -le 0.5) { return 'n.m.' }; $g = ($b - $a) / $a; return ('{0}{1:N0}%' -f $(if ($g -ge 0) { '+' } else { '' }), ($g * 100)) }
function DCol($v) { $v = [double]$v; if ($v -ge 0.5) { return $GREEN } elseif ($v -le -0.5) { return $RED } else { return $MUTED } }

$wasRunning = [bool](Get-Process POWERPNT -ErrorAction SilentlyContinue)  # never quit a PowerPoint the user already has open
if ($wasRunning -and -not $env:DECK_ALLOW_RUNNING_PPT) { Write-Output 'STOP: PowerPoint is open.'; exit 2 }
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Template, 0, -1, 0)   # untitled copy, no window: the template file is never written
$tw = $null; foreach ($dsg in $pres.Designs) { if ($dsg.Name -eq '6_Office Theme') { $tw = $dsg } }
if ($null -eq $tw) { Write-Output 'STOP: design 6_Office Theme not found'; $pres.Close(); exit 3 }
$coverLayout = $null; $bodyLayout = $null
foreach ($cl in $tw.SlideMaster.CustomLayouts) { if ($cl.Name -eq '2_Title Slide') { $coverLayout = $cl }; if ($cl.Name -eq 'Custom Layout') { $bodyLayout = $cl } }
# keep the template slides until the end: deleting them first makes PowerPoint drop unused layouts
$script:orig = $pres.Slides.Count

# content is laid out for y 88..508 and mapped into the white area above the TW footer bar (72..486)
$script:ymap = $false
function MY($y) { if ($script:ymap) { return 72 + ($y - 88) * (414.0 / 420) } else { return $y } }
function MH($h) { if ($script:ymap) { return $h * (414.0 / 420) } else { return $h } }
function PH($slide, $type) { foreach ($sh in $slide.Shapes) { if ($sh.Type -eq 14 -and $sh.PlaceholderFormat.Type -eq $type) { return $sh } }; return $null }
function Brand($slide) { try { $slide.HeadersFooters.SlideNumber.Visible = -1; $slide.HeadersFooters.Footer.Visible = -1 } catch {} }

function T($slide, $x, $y, $w, $h, $str, $size, $color, $bold, $align) {
  $y = MY $y; $h = MH $h
  $s = $slide.Shapes.AddTextbox(1, [single]$x, [single]$y, [single]$w, [single]$h)
  $tf = $s.TextFrame; $tf.WordWrap = -1; $tf.AutoSize = 0
  $tf.MarginLeft = [single]0; $tf.MarginRight = [single]0; $tf.MarginTop = [single]0; $tf.MarginBottom = [single]0
  $tr = $tf.TextRange; $tr.Text = [string]$str; $tr.Font.Name = $FONT; $tr.Font.Size = [single]$size; $tr.Font.Color.RGB = $color
  $tr.Font.Bold = $(if ($bold) { -1 } else { 0 })
  $tr.ParagraphFormat.Alignment = $(if ($align -eq 'c') { 2 } elseif ($align -eq 'r') { 3 } else { 1 })
  $s.Width = [single]$w; $s.Height = [single]$h
  return $s
}
# rich text: list of @(text, bold, color) runs in one box
function TR($slide, $x, $y, $w, $h, $runs, $size) {
  if ($runs.Count -gt 0 -and -not ($runs[0] -is [array])) { $runs = ,$runs }
  $s = T $slide $x $y $w $h '' $size $TEXT $false 'l'
  $tr = $s.TextFrame.TextRange
  foreach ($run in $runs) {
    $added = $tr.InsertAfter([string]$run[0])
    $added.Font.Name = $FONT; $added.Font.Size = [single]$size; $added.Font.Bold = $(if ($run[1]) { -1 } else { 0 }); $added.Font.Color.RGB = $run[2]
  }
  $s.Width = [single]$w; $s.Height = [single](MH $h)
  return $s
}
function Rect($slide, $x, $y, $w, $h, $fill) {
  $y = MY $y; $h = MH $h
  $s = $slide.Shapes.AddShape(1, [single]$x, [single]$y, [single]$w, [single]$h)
  $s.Fill.ForeColor.RGB = $fill; $s.Fill.Solid(); $s.Line.Visible = 0; $s.Shadow.Visible = 0
  return $s
}
function Card($slide, $x, $y, $w, $h) {
  $y = MY $y; $h = MH $h
  $s = $slide.Shapes.AddShape(5, [single]$x, [single]$y, [single]$w, [single]$h)
  $s.Adjustments.Item(1) = [single]0.03
  $s.Fill.ForeColor.RGB = $WHITE; $s.Fill.Solid()
  $s.Line.Visible = -1; $s.Line.ForeColor.RGB = $LINE; $s.Line.Weight = [single]0.75; $s.Shadow.Visible = 0
  return $s
}
function L($slide, $x1, $y1, $x2, $y2, $color, $w, $dash) {
  $y1 = MY $y1; $y2 = MY $y2
  $s = $slide.Shapes.AddLine([single]$x1, [single]$y1, [single]$x2, [single]$y2)
  $s.Line.ForeColor.RGB = $color; $s.Line.Weight = [single]$w
  if ($dash) { $s.Line.DashStyle = 4 }
  return $s
}
function Kicker($slide, $x, $y, $w, $str) { $s = T $slide $x $y $w 14 $str 9.5 $KICK $true 'l'; $s.TextFrame2.TextRange.Font.Spacing = [single]1; return $s }
function Page($title, $source) {
  $script:page++
  $script:ymap = $false
  $sl = $pres.Slides.AddSlide($pres.Slides.Count + 1, $bodyLayout)
  Brand $sl
  $tp = PH $sl 3; if ($null -eq $tp) { $tp = PH $sl 1 }
  $tp.Left = [single]30; $tp.Top = [single]10; $tp.Width = [single]900; $tp.Height = [single]52
  $tp.TextFrame.TextRange.Text = $title; $tp.TextFrame.TextRange.Font.Name = $FONT; $tp.TextFrame.TextRange.Font.Size = [single]24; $tp.TextFrame.TextRange.Font.Bold = -1
  $tp.TextFrame.VerticalAnchor = 3; $tp.TextFrame.WordWrap = -1; $tp.TextFrame.AutoSize = 0
  if ($source) { T $sl 30 491 900 11 $source 7.5 $MUTED $false 'l' | Out-Null }
  $script:ymap = $true
  return $sl
}
function Note($slide, $x, $y, $w, $h, $runs) {
  Rect $slide $x $y $w $h $NOTEBG | Out-Null
  Rect $slide $x $y 3 $h $KICK | Out-Null
  $t = TR $slide ($x + 12) ($y + 6) ($w - 20) ($h - 10) $runs 11
  $t.TextFrame.VerticalAnchor = 3
}
# waterfall: start bar (navy), floating steps (green/red), end bar (cyan); returns the x centre of every bar
function Waterfall($slide, $x0, $yTop, $yBase, $w, $startLbl, $start, $steps, $endLbl, $end, $vmax) {
  $n = $steps.Count + 2; $slot = $w / $n; $bw = [Math]::Min(44, $slot * 0.62); $k = ($yBase - $yTop) / $vmax
  $cx = @()
  $bars = @(@{ name = $startLbl; v = [double]$start; kind = 'total' })
  foreach ($stp in $steps) { $bars += @{ name = [string]$stp[0]; v = [double]$stp[1]; kind = 'step' } }
  $bars += @{ name = $endLbl; v = [double]$end; kind = 'end' }
  $run = 0.0
  for ($i = 0; $i -lt $n; $i++) {
    $bar = $bars[$i]; $c = $x0 + $slot * ($i + 0.5); $cx += $c; $bx = $c - $bw / 2
    if ($bar.kind -ne 'step') {
      $h = [Math]::Max(1.5, $bar.v * $k); $fill = $(if ($bar.kind -eq 'end') { $CYAN } else { $NAVY })
      Rect $slide $bx ($yBase - $h) $bw $h $fill | Out-Null
      T $slide ($c - 40) ($yBase - $h - 16) 80 14 (N0 $bar.v) 11 $NAVY $true 'c' | Out-Null
      $run = $bar.v
    } else {
      $from = $run; $to = $run + $bar.v
      $yA = $yBase - [Math]::Max($from, $to) * $k; $h = [Math]::Max(1.5, [Math]::Abs($bar.v) * $k)
      Rect $slide $bx $yA $bw $h $(if ($bar.v -ge 0) { $GREEN } else { $RED }) | Out-Null
      if ($bar.v -ge 0) { T $slide ($c - 40) ($yA - 15) 80 13 (SG $bar.v) 10.5 $GREEN $true 'c' | Out-Null }
      else { T $slide ($c - 40) ($yA + $h + 2) 80 13 (SG $bar.v) 10.5 $RED $true 'c' | Out-Null }
      $run = $to
    }
    if ($i -lt $n - 1) { $yl = $yBase - $run * $k; L $slide ($bx + $bw) $yl ($bx + $slot) $yl $MUTED 0.5 $true | Out-Null }
    T $slide ($c - $slot / 2) ($yBase + 4) $slot 24 $bar.name 9 $TEXT $false 'c' | Out-Null
  }
  L $slide $x0 $yBase ($x0 + $w) $yBase $LINE 0.75 $false | Out-Null
  return ,$cx
}
# table on shapes: rows = list of hashtables { cells; bold; fill; color; colors; size; h; line; indent; italic }
function Grid($slide, $x, $y, $widths, $rowH, $rows) {
  $yy = $y; $tw0 = 0; foreach ($cw in $widths) { $tw0 += $cw }
  foreach ($row in $rows) {
    $h = $(if ($row.h) { $row.h } else { $rowH })
    if ($row.fill) { Rect $slide $x $yy $tw0 $h $row.fill | Out-Null }
    $xx = $x
    for ($c = 0; $c -lt $widths.Count; $c++) {
      $txt = [string]$row.cells[$c]
      if ($txt -ne '') {
        $col = $(if ($row.colors -and $row.colors[$c]) { $row.colors[$c] } elseif ($row.color) { $row.color } else { $TEXT })
        $al = $(if ($c -eq 0) { 'l' } elseif ($row.center) { 'c' } else { 'r' }); $ind = $(if ($c -eq 0 -and $row.indent) { $row.indent } else { 0 })
        $sz = $(if ($row.size) { $row.size } else { 10 })
        $t = T $slide ($xx + 4 + $ind) $yy ($widths[$c] - 8 - $ind) $h $txt $sz $col ([bool]$row.bold) $al
        $t.TextFrame.VerticalAnchor = 3
        if ($row.italic) { $t.TextFrame.TextRange.Font.Italic = -1 }
      }
      $xx += $widths[$c]
    }
    if ($row.line) { L $slide $x ($yy + $h) ($x + $tw0) ($yy + $h) $LINE 0.5 $false | Out-Null }
    $yy += $h
  }
  return $yy
}
function Legend($slide, $x, $y, $items) { $lx = $x; foreach ($it in $items) { Rect $slide $lx ($y + 2) 8 8 $it[1] | Out-Null; T $slide ($lx + 11) $y 150 12 $it[0] 9 $TEXT $false 'l' | Out-Null; $lx += 11 + 14 + ($it[0].Length * 4.6) } }

$SRC = 'Source: P&L LE9+3 file (AP2027-2028); TWPC totals = sheet ConsoAll, BUs = BU sheets, Corp / Elim = ConsoAll ' + [char]0x2212 + ' BUs. MB = million baht.'
$SC = @('2025', 'AP26', 'LE26', 'AP27', 'AP28'); $SCL = @{ '2025' = '2025'; 'AP26' = 'AP2026'; 'LE26' = '2026 LE'; 'AP27' = '2027 AP'; 'AP28' = '2028 AP' }
$ST = $DATA.strip; $SK = $DATA.stack; $PL = $DATA.pl
$script:page = 0

# ================= 1. Cover =================
$script:page++
$s = $pres.Slides.AddSlide($pres.Slides.Count + 1, $coverLayout)
Brand $s
$tp = PH $s 3; if ($null -eq $tp) { $tp = PH $s 1 }
$tp.TextFrame.TextRange.Text = ('AP2027' + [char]11 + 'group consolidation'); $tp.TextFrame.TextRange.Font.Name = $FONT
$sub = PH $s 4; if ($null -eq $sub) { $sub = PH $s 2 }
if ($null -ne $sub) { $sub.TextFrame.TextRange.Text = ('How each BU contributes' + [char]13 + 'AP2028 as direction' + [char]13 + 'CEO review, Nov 2026'); $sub.TextFrame.TextRange.Font.Name = $FONT }

# ================= 2. Executive summary =================
$s = Page $TX.ex_title $SRC
Card $s 30 88 900 420 | Out-Null
Kicker $s 46 100 600 'KEY TAKEAWAYS FOR THE CEO' | Out-Null
$yy = 122
$ix = 0
foreach ($ex in $TX.ex) {
  $ix++
  T $s 46 ($yy + 4) 140 30 $ex[0] 26 $NAVY $true 'l' | Out-Null
  T $s 46 ($yy + 38) 140 14 $ex[1] 9 $MUTED $false 'l' | Out-Null
  T $s 200 ($yy + 2) 714 18 $ex[2] 13 $NAVY $true 'l' | Out-Null
  T $s 200 ($yy + 24) 714 62 $ex[3] 10.5 $TEXT $false 'l' | Out-Null
  $yy += 96
  if ($ix -lt 4) { L $s 46 ($yy - 8) 914 ($yy - 8) $LINE 0.5 $false | Out-Null }
}

# ================= 3. TWPC at a glance =================
$opba26 = [double]$ST.LE26.opba; $opba27 = [double]$ST.AP27.opba
$s = Page $TX.gl_title $SRC
Card $s 30 88 545 420 | Out-Null
T $s 46 100 500 18 'TWPC financials by BU' 14 $NAVY $true 'l' | Out-Null
T $s 46 119 500 14 'OPBA by BU (MB), 2025 actual to 2028 AP' 10 $MUTED $false 'l' | Out-Null
Legend $s 46 138 @(@('Food', $NAVY), @('HVA incl. Waxy', $HVAC), @('Starch', $CYAN), @('NBG, Corp/Elim', $GREY))
$labW = 120; $colW = 82; $cx0 = 46 + $labW
$yBase = 330; $kk = 155 / 1400.0
Rect $s ($cx0 + 3 * $colW) 156 $colW 335 $TINT | Out-Null
for ($i = 0; $i -lt 5; $i++) {
  $scn = $SC[$i]; $c = $cx0 + $colW * ($i + 0.5); $bw = 40; $bx = $c - $bw / 2
  $v = $SK.$scn; $y = $yBase
  foreach ($bu in $STACK) {
    $h = [double]$v.$bu * $kk; $y -= $h
    $r = Rect $s $bx $y $bw $h $BUCOL[$bu]
    if ($scn -eq 'AP28') { $r.Fill.Transparency = [single]0.35 }
    if ($h -ge 9.5) { T $s $bx ($y + $h / 2 - 6) $bw 12 (N0 $v.$bu) 8.5 $BUTXT[$bu] $true 'c' | Out-Null }
  }
  $oth = [double]$v.Other
  if ($oth -lt 0) { $r = Rect $s $bx $yBase $bw ([Math]::Max(1, -$oth * $kk)) $GREY; if ($scn -eq 'AP28') { $r.Fill.Transparency = [single]0.35 } }
  T $s ($c - 38) ($y - 16) 76 14 (N0 $v.Total) 11 $NAVY $true 'c' | Out-Null
}
$pill = $s.Shapes.AddShape(9, [single]($cx0 + 3 * $colW + 6), [single](MY 157), [single]($colW - 12), [single]17)
$pill.Fill.Visible = 0; $pill.Line.ForeColor.RGB = $NAVY; $pill.Line.Weight = [single]0.75
$pill.TextFrame.TextRange.Text = ($TX.g27 + ' vs LE'); $pill.TextFrame.TextRange.Font.Size = [single]8.5; $pill.TextFrame.TextRange.Font.Name = $FONT; $pill.TextFrame.TextRange.Font.Color.RGB = $NAVY; $pill.TextFrame.TextRange.Font.Bold = -1
$pill.TextFrame.MarginLeft = [single]0; $pill.TextFrame.MarginRight = [single]0; $pill.TextFrame.MarginTop = [single]0; $pill.TextFrame.MarginBottom = [single]0
$rows = @()
$rows += @{ cells = @('') + ($SC | ForEach-Object { $SCL[$_] }); bold = $true; color = $NAVY; line = $true; h = 20 }
$rows += @{ cells = @('Volume (kt)') + ($SC | ForEach-Object { '{0:N0}' -f [double]$ST.$_.vol }); line = $true }
$rows += @{ cells = @('Net sales (MB)') + ($SC | ForEach-Object { '{0:N0}' -f [double]$ST.$_.ns }); line = $true }
$rows += @{ cells = @('Gross profit (MB)') + ($SC | ForEach-Object { '{0:N0}' -f [double]$ST.$_.gp }); line = $true }
$rows += @{ cells = @('  %GM') + ($SC | ForEach-Object { '({0:N1}%)' -f ([double]$ST.$_.gm * 100) }); line = $true; color = $MUTED; italic = $true }
$rows += @{ cells = @('OPBA (MB)') + ($SC | ForEach-Object { '{0:N0}' -f [double]$ST.$_.opba }); line = $true; bold = $true; color = $NAVY }
$rows += @{ cells = @('Net profit (MB)') + ($SC | ForEach-Object { '{0:N0}' -f [double]$ST.$_.np }); line = $true; bold = $true; color = $NAVY }
Grid $s 46 352 @($labW, $colW, $colW, $colW, $colW, $colW) 19 $rows | Out-Null
T $s 46 488 510 12 '2028 AP shaded lighter = direction only. NBG + Corp/Elim shown below the axis when negative.' 8 $MUTED $false 'l' | Out-Null
Card $s 590 88 340 300 | Out-Null
Kicker $s 606 100 300 'WHAT AP2027 COMMITS TO' | Out-Null
$yy = 122; $ix = 0
foreach ($it in $TX.gl_items) {
  $ix++
  T $s 606 $yy 92 30 $it[0] 21 $NAVY $true 'l' | Out-Null
  TR $s 700 ($yy + 1) 218 44 @(@($it[1], $true, $NAVY), @($it[2], $false, $TEXT)) 10.5 | Out-Null
  if ($ix -lt 4) { L $s 606 ($yy + 58) 918 ($yy + 58) $LINE 0.5 $false | Out-Null }
  $yy += 64
}
Card $s 590 400 340 108 | Out-Null
Kicker $s 606 412 300 'AP2028 DIRECTION' | Out-Null
T $s 606 430 92 30 (N0 $ST.AP28.opba) 21 $NAVY $true 'l' | Out-Null
TR $s 700 431 218 70 @(@($TX.gl_28[0], $true, $NAVY), @($TX.gl_28[1], $false, $TEXT)) 10.5 | Out-Null

# ================= 4. OPBA bridge LE26 -> AP27 =================
$B27 = $DATA.bridge27
$steps = @(); foreach ($p in $B27.steps) { $steps += ,@($p[0], [double]$p[1]) }
$s = Page $TX.br_title $SRC
Card $s 30 88 560 420 | Out-Null
T $s 46 100 520 18 'OPBA bridge by BU, 2026 LE to 2027 AP (MB)' 14 $NAVY $true 'l' | Out-Null
$wx0 = 140; $ww = 434
$cx = Waterfall $s $wx0 140 328 $ww '2026 LE' ([double]$B27.start) $steps '2027 AP' ([double]$B27.end) 1150
$slot = $ww / 7.0
L $s 46 362 574 362 $LINE 0.5 $false | Out-Null
$rlab = @('2026 LE OPBA (MB)', '2027 AP OPBA (MB)', 'Growth vs 2026 LE')
for ($ri = 0; $ri -lt 3; $ri++) {
  $ly = 368 + $ri * 18
  T $s 46 $ly 92 14 $rlab[$ri] 9 $NAVY $true 'l' | Out-Null
  for ($i = 0; $i -lt 7; $i++) {
    $c = $cx[$i]; $val = ''
    if ($i -eq 0) { if ($ri -eq 0) { $val = N0 $B27.start } }
    elseif ($i -eq 6) { if ($ri -eq 1) { $val = N0 $B27.end } elseif ($ri -eq 2) { $val = GR $B27.start $B27.end } }
    else {
      $nm = [string]$B27.steps[$i - 1][0]; $pair = $B27.lvl.$nm
      if ($ri -eq 0) { $val = N0 $pair[0] } elseif ($ri -eq 1) { $val = N0 $pair[1] } else { $val = $(if ($nm -eq 'Corp / Elim' -or [double]$pair[0] -le 0.5) { 'n.m.' } else { GR $pair[0] $pair[1] }) }
    }
    T $s ($c - $slot / 2) $ly $slot 14 $val 9.5 $(if ($ri -eq 2) { $MUTED } else { $TEXT }) ($i -eq 0 -or $i -eq 6) 'c' | Out-Null
  }
}
Note $s 46 440 528 56 @(@($TX.br_note[0], $true, $NAVY), @($TX.br_note[1], $false, $TEXT))
Card $s 605 88 325 420 | Out-Null
Kicker $s 621 100 300 ('WHAT DRIVES EACH BU ' + $DOT + ' ' + $DELTA + ' OPBA VS 2026 LE') | Out-Null
$yy = 120; $ix = 0
foreach ($dv in $TX.drv) {
  $ix++
  T $s 621 $yy 200 16 $dv[0] 12 $NAVY $true 'l' | Out-Null
  T $s 840 $yy 74 16 (SG $dv[1]) 12 (DCol $dv[1]) $true 'r' | Out-Null
  $yy += 17
  $subs = $dv[2]; if ($subs.Count -gt 0 -and -not ($subs[0] -is [array])) { $subs = ,$subs }
  foreach ($sb in $subs) {
    T $s 633 $yy 200 13 $sb[0] 10 $TEXT $false 'l' | Out-Null
    if ($null -ne $sb[1]) { T $s 840 $yy 74 13 (SG $sb[1]) 10 (DCol $sb[1]) $false 'r' | Out-Null }
    $yy += 13.5
  }
  $yy += 7
  if ($ix -lt $TX.drv.Count) { L $s 621 ($yy - 4) 914 ($yy - 4) $LINE 0.5 $false | Out-Null }
}

# ================= 5. OPBA by BU and entity + mix =================
$s = Page 'TWIC, TDC, TDC 2.0 and Well Grow carry most of the AP2027 uplift' $SRC
Card $s 30 88 525 420 | Out-Null
$wd = @(150, 52, 56, 56, 60, 56, 58)
Rect $s (46 + 150 + 52 + 56 + 56) 98 60 373 $TINT | Out-Null
$rows = @(@{ cells = @('OPBA (MB)', '2025', 'AP2026', '2026 LE', '2027 AP', '2028 AP', ($DELTA + ' vs LE')); bold = $true; color = $NAVY; line = $true; h = 22; size = 9.5 })
foreach ($r in $DATA.entity_opba) {
  $d1 = [double]$r.AP27 - [double]$r.LE26
  $row = @{ cells = @($r.label, (N0 $r.'2025'), (N0 $r.AP26), (N0 $r.LE26), (N0 $r.AP27), (N0 $r.AP28), (SG $d1)); colors = @($null, $null, $null, $null, $NAVY, $MUTED, (DCol $d1)); h = 18.5 }
  if ($r.lvl -eq 1) { $row.indent = 12; $row.size = 9.5 }
  elseif ($r.lvl -eq 2) { $row.indent = 12; $row.size = 9; $row.italic = $true; $row.color = $MUTED; $row.colors = @($MUTED, $MUTED, $MUTED, $MUTED, $MUTED, $MUTED, $MUTED); $row.line = $true }
  else { $row.bold = $true; $row.line = $true }
  if ($r.lvl -eq -1) { $row.fill = $TINT; $row.color = $NAVY; $row.h = 21 }
  $rows += $row
}
Grid $s 46 98 $wd 18.5 $rows | Out-Null
Card $s 570 88 360 420 | Out-Null
Kicker $s 586 100 330 'OPBA MIX ACROSS THE CORE BUs' | Out-Null
$yy = 124
foreach ($scn in @('LE26', 'AP27', 'AP28')) {
  $v = $SK.$scn; $tot = 0.0; foreach ($bu in $STACK) { $tot += [double]$v.$bu }
  T $s 586 $yy 80 14 $SCL[$scn] 10.5 $NAVY $true 'l' | Out-Null
  T $s 830 $yy 84 14 ((N0 $tot) + ' MB') 9.5 $MUTED $false 'r' | Out-Null
  $x = 586; $barW = 328
  foreach ($bu in $STACK) {
    $w = $barW * [double]$v.$bu / $tot; Rect $s $x ($yy + 17) $w 20 $BUCOL[$bu] | Out-Null
    T $s $x ($yy + 21) $w 13 ('{0:N0}%' -f ([double]$v.$bu / $tot * 100)) 9.5 $BUTXT[$bu] $true 'c' | Out-Null
    $x += $w
  }
  $yy += 50
}
Legend $s 586 ($yy - 4) @(@('Food', $NAVY), @('HVA incl. Waxy', $HVAC), @('Starch', $CYAN))
T $s 586 ($yy + 12) 328 12 'Share = BU OPBA / (Food + HVA incl. Waxy + Starch)' 8 $MUTED $false 'l' | Out-Null
L $s 586 ($yy + 32) 914 ($yy + 32) $LINE 0.5 $false | Out-Null
$yy += 42
foreach ($sty in $TX.stories) {
  T $s 586 $yy 112 24 $sty[0] 17 $NAVY $true 'l' | Out-Null
  T $s 702 ($yy + 2) 212 30 $sty[1] 10 $TEXT $false 'l' | Out-Null
  $yy += 40
}

# ================= 6. From OPBA to net profit (group level) =================
$NB = $DATA.np_bridge; $nsteps = @(); foreach ($p in $NB.steps) { $nsteps += ,@($p[0], [double]$p[1]) }
$s = Page $TX.np_title $SRC
Card $s 30 88 560 420 | Out-Null
T $s 46 100 520 18 'Net profit, 2026 LE to 2027 AP (MB)' 14 $NAVY $true 'l' | Out-Null
$cx = Waterfall $s 46 150 360 528 '2026 LE NP' ([double]$NB.start) $nsteps '2027 AP NP' ([double]$NB.end) 430
T $s ($cx[2] - 33) 392 66 26 $TX.np_ann[0] 8.5 $MUTED $false 'c' | Out-Null
T $s ($cx[3] - 33) 392 66 26 $TX.np_ann[1] 8.5 $MUTED $false 'c' | Out-Null
Note $s 46 430 528 66 @(@($TX.np_note[0], $true, $NAVY), @($TX.np_note[1], $false, $TEXT))
Card $s 605 88 325 420 | Out-Null
Kicker $s 621 100 300 'BELOW OPBA, GROUP LEVEL (MB)' | Out-Null
$rows = @(@{ cells = @('', '2026 LE', '2027 AP', $DELTA); bold = $true; color = $NAVY; line = $true; h = 20 })
foreach ($ln in @('OPBA', 'Admin', 'Other income & FX', 'Finance cost', 'CIT', 'MI & other', 'Net profit')) {
  $a = [double]$DATA.below.LE26.$ln; $b = [double]$DATA.below.AP27.$ln
  $row = @{ cells = @($ln, (N0 $a), (N0 $b), (SG ($b - $a))); colors = @($null, $null, $NAVY, (DCol ($b - $a))); line = $true; h = 19 }
  if ($ln -eq 'OPBA' -or $ln -eq 'Net profit') { $row.bold = $true; $row.fill = $TINT; $row.color = $NAVY }
  $rows += $row
}
$yy = Grid $s 621 120 @(118, 62, 62, 52) 19 $rows
$ci = 0
foreach ($cal in $TX.np_cal) {
  $y0 = $yy + 18 + $ci * 76
  T $s 621 $y0 90 24 $cal[0] 18 $NAVY $true 'l' | Out-Null
  T $s 712 ($y0 + 2) 202 14 $cal[1] 10.5 $NAVY $true 'l' | Out-Null
  T $s 712 ($y0 + 17) 202 44 $cal[2] 9.5 $TEXT $false 'l' | Out-Null
  if ($ci -eq 0) { L $s 621 ($y0 + 64) 914 ($y0 + 64) $LINE 0.5 $false | Out-Null }
  $ci++
}

# ================= 7. Admin P vs Non-P, Thailand vs International =================
$AD = $DATA.admin
$s = Page $TX.ad_title $SRC
Card $s 30 88 585 420 | Out-Null
T $s 46 100 540 18 'Admin expenses by type and geography (MB)' 14 $NAVY $true 'l' | Out-Null
$ascn = @('2025', 'LE26', 'AP27', 'AP28')
$wd = @(200, 66, 66, 70, 66, 80)
Rect $s (46 + 200 + 66 + 66) 124 70 310 $TINT | Out-Null
$rows = @(@{ cells = @('', '2025', '2026 LE', '2027 AP', '2028 AP', ($DELTA + ' AP27 vs LE')); bold = $true; color = $NAVY; line = $true; h = 22; size = 9.5 })
function AdRow($label, $vals, $kind) {
  $dd = [double]$vals[2] - [double]$vals[1]
  $row = @{ cells = @($label, (N0 $vals[0]), (N0 $vals[1]), (N0 $vals[2]), (N0 $vals[3]), (SG $dd)); colors = @($null, $null, $null, $NAVY, $MUTED, (DCol $dd)); h = 19 }
  if ($kind -eq 'head') { $row.bold = $true; $row.color = $NAVY; $row.line = $true }
  elseif ($kind -eq 'total') { $row.bold = $true; $row.color = $NAVY; $row.fill = $TINT; $row.line = $true; $row.h = 21 }
  else { $row.indent = 12; $row.size = 9.5 }
  return $row
}
$GEO = @('TH excl. TDC 2.0', 'TDC 2.0', 'International')
foreach ($typ in @(@('adp', ('Admin ' + $DASH + ' people')), @('adn', ('Admin ' + $DASH + ' non-people')))) {
  $kt = $typ[0]
  $rows += AdRow $typ[1] @($ascn | ForEach-Object { [double]$AD.$_.$kt.TWPC }) 'head'
  foreach ($gg in $GEO) { $rows += AdRow $gg @($ascn | ForEach-Object { [double]$AD.$_.$kt.$gg }) 'sub' }
  $eo = @($ascn | ForEach-Object { [double]$AD.$_.$kt.'Elim / other' }); $mx = 0.0; foreach ($q in $eo) { $mx = [Math]::Max($mx, [Math]::Abs($q)) }
  if ($mx -ge 0.5) { $rows += AdRow 'Elim / other' $eo 'sub' }
}
$rows += AdRow 'Total admin' @($ascn | ForEach-Object { [double]$AD.$_.adp.TWPC + [double]$AD.$_.adn.TWPC }) 'total'
foreach ($gg in $GEO) { $rows += AdRow $gg @($ascn | ForEach-Object { [double]$AD.$_.adp.$gg + [double]$AD.$_.adn.$gg }) 'sub' }
$pr = @{ cells = @('Admin / net sales') + ($ascn | ForEach-Object { '{0:N1}%' -f (-([double]$AD.$_.adp.TWPC + [double]$AD.$_.adn.TWPC) / [double]$ST.$_.ns * 100) }) + @(''); italic = $true; color = $MUTED; h = 19; line = $true }
$rows += $pr
$yy = Grid $s 46 124 $wd 19 $rows
Note $s 46 ($yy + 10) 553 44 @(@($TX.ad_note[0], $true, $NAVY), @($TX.ad_note[1], $false, $TEXT))
Card $s 630 88 300 420 | Out-Null
Kicker $s 646 100 270 ('WHAT MOVES ADMIN ' + $DOT + ' AP27 VS 2026 LE') | Out-Null
T $s 646 116 270 12 'MB, P&L sign: ( ) = higher cost' 8 $MUTED $false 'l' | Out-Null
T $s 646 462 270 40 'TH = Starch TH, TDC, Waxy, Food TH & WG, NBG, Corp. International = China, TWIC, Vietnam, TWIN, TWII, Food VN. Impairment: Finance BU review, Act Sep''26.' 7.5 $MUTED $false 'l' | Out-Null
$ci = 0
foreach ($cal in $TX.ad_cal) {
  $y0 = 136 + $ci * 120
  T $s 646 $y0 268 26 $cal[0] 22 $NAVY $true 'l' | Out-Null
  T $s 646 ($y0 + 30) 268 14 $cal[1] 11.5 $NAVY $true 'l' | Out-Null
  T $s 646 ($y0 + 48) 268 60 $cal[2] 10 $TEXT $false 'l' | Out-Null
  if ($ci -lt 2) { L $s 646 ($y0 + 110) 914 ($y0 + 110) $LINE 0.5 $false | Out-Null }
  $ci++
}

# ================= 8. AP2028 direction =================
$B28 = $DATA.bridge28; $steps = @(); foreach ($p in $B28.steps) { $steps += ,@($p[0], [double]$p[1]) }
$s = Page $TX.a28_title $SRC
Card $s 30 88 600 420 | Out-Null
T $s 46 100 560 18 'OPBA bridge by BU, 2027 AP to 2028 AP (MB)' 14 $NAVY $true 'l' | Out-Null
$cx = Waterfall $s 46 140 350 568 '2027 AP' ([double]$B28.start) $steps '2028 AP' ([double]$B28.end) 1450
$ai = 1
foreach ($nm in @('Food', 'HVA incl. Waxy', 'Starch')) {
  T $s ($cx[$ai] - 40) 382 80 26 ([string]$TX.a28_ann.$nm -replace "`r", [string][char]13) 8.5 $MUTED $false 'c' | Out-Null
  $ai++
}
Note $s 46 430 568 66 @(@($TX.a28_note[0], $true, $NAVY), @($TX.a28_note[1], $false, $TEXT))
Card $s 645 88 285 420 | Out-Null
Kicker $s 661 100 260 'AP2028 AT A GLANCE' | Out-Null
$ci = 0
foreach ($cal in $TX.a28_cards) {
  $y0 = 124 + $ci * 122
  T $s 661 $y0 250 30 $cal[0] 24 $NAVY $true 'l' | Out-Null
  T $s 661 ($y0 + 32) 250 14 $cal[1] 11.5 $NAVY $true 'l' | Out-Null
  T $s 661 ($y0 + 50) 250 56 $cal[2] 10 $TEXT $false 'l' | Out-Null
  if ($ci -lt 2) { L $s 661 ($y0 + 110) 914 ($y0 + 110) $LINE 0.5 $false | Out-Null }
  $ci++
}

# ================= 9. Multi-year P&L summary by BU =================
$s = Page $TX.sum_title $SRC
Card $s 30 88 900 420 | Out-Null
$wd = @(184, 74, 74, 74, 74, 74, 74, 74, 74, 74)
$x0 = 46; $gx = $x0 + 184
foreach ($gi in 0, 1, 2) {
  $gl = @('Net sales (MB)', 'Gross profit (MB)', 'OP before admin (MB)')[$gi]
  T $s ($gx + $gi * 222) 100 222 14 $gl 10.5 $NAVY $true 'c' | Out-Null
  L $s ($gx + $gi * 222 + 6) 117 ($gx + $gi * 222 + 216) 117 $NAVY 0.75 $false | Out-Null
  Rect $s ($gx + $gi * 222 + 74) 120 74 242 $TINT | Out-Null
}
$hdr = @('') ; foreach ($gi in 0, 1, 2) { $hdr += @('2026 LE', '2027 AP', '2028 AP') }
$rows = @(@{ cells = $hdr; bold = $true; color = $NAVY; line = $true; h = 22; size = 9.5 })
foreach ($r in $DATA.summary) {
  $cells = @([string]$r.label)
  foreach ($m in @('ns', 'gp', 'opba')) { foreach ($scn in @('LE26', 'AP27', 'AP28')) { $cells += (N0 $r.$m.$scn) } }
  $row = @{ cells = $cells; h = 24; line = $true }
  if (([string]$r.label).StartsWith('  ')) { $row.indent = 10; $row.italic = $true; $row.color = $MUTED; $row.size = 9.5; $row.cells[0] = ([string]$r.label).Trim() }
  else { $row.bold = $true; $row.color = $NAVY }
  if ($r.key -eq 'TWPC') { $row.fill = $TINT; $row.h = 26 }
  $rows += $row
}
$np = @('Net profit, TWPC (group level)') + @('', '', '', '', '', '') + @($DATA.strip.LE26.np, $DATA.strip.AP27.np, $DATA.strip.AP28.np | ForEach-Object { N0 $_ })
$rows += @{ cells = $np; bold = $true; color = $NAVY; h = 24; line = $true }
$yy = Grid $s $x0 120 $wd 24 $rows
$sm = $DATA.summary
function SumRow($key) { foreach ($q in $DATA.summary) { if ($q.key -eq $key) { return $q } }; return $null }
$fd = SumRow 'Food'; $hv = SumRow 'HVA'; $sc0 = SumRow 'Starch'
Note $s 46 ($yy + 14) 868 50 @(@(('OPBA path 2026 LE ' + $ARROW + ' 2027 AP ' + $ARROW + ' 2028 AP: '), $true, $NAVY),
  @(('Food {0} {1} {2} {1} {3} MB; HVA incl. Waxy {4} {1} {5} {1} {6} MB (x{7:N1}); Starch {8} {1} {9} {1} {10} MB. BU performance is measured at OPBA; net profit is shown for the group only.' -f (N0 $fd.opba.LE26), $ARROW, (N0 $fd.opba.AP27), (N0 $fd.opba.AP28), (N0 $hv.opba.LE26), (N0 $hv.opba.AP27), (N0 $hv.opba.AP28), ([double]$hv.opba.AP28 / [double]$hv.opba.LE26), (N0 $sc0.opba.LE26), (N0 $sc0.opba.AP27), (N0 $sc0.opba.AP28)), $false, $TEXT))

# ================= 10-12. Appendix P&L by BU =================
function PLPage($scn, $title) {
  $s = Page $title $SRC
  Card $s 30 88 900 420 | Out-Null
  $cols = @($DATA.appx_cols)
  $wd = @(164) + (@(88) * 8)
  Rect $s (46 + 164 + 88 * 3) 98 88 345 $TINT | Out-Null
  $rows = @(@{ cells = @('MB') + $cols; bold = $true; color = $NAVY; line = $true; h = 24; size = 9.5 })
  foreach ($r in $DATA.appx.$scn) {
    $isPct = ($r.kind -eq 'pct')
    $cells = @($(if ($isPct) { '  ' + $r.label } else { $r.label }))
    foreach ($v in $r.vals) {
      if ($isPct) { $cells += (PC $v) } elseif ($r.kind -eq 'kt') { $cells += (N1 $v) } else { $cells += (N0 $v) }
    }
    $row = @{ cells = $cells; h = 19; line = ($r.key -or $isPct -or $r.kind -eq 'kt'); size = 9.5 }
    if ($r.key) { $row.bold = $true; $row.color = $NAVY }
    if ($isPct) { $row.color = $MUTED; $row.italic = $true }
    if ($r.label -eq 'OP before admin' -or $r.label -eq 'Net profit') { $row.fill = $TINT }
    $rows += $row
  }
  Grid $s 46 98 $wd 19 $rows | Out-Null
  T $s 46 470 868 24 ('HVA incl. Waxy = HVA excl. Waxy + Waxy (sheet "HVA incl Waxy"). Starch + HVA incl. Waxy + Food + NBG + Corp / Elim = TWPC (ConsoAll) on every line. Corp / Elim volume not meaningful; n.m. = not meaningful.') 8 $MUTED $false 'l' | Out-Null
}
PLPage 'LE26' 'Appendix: 2026 LE (9+3) consolidated P&L by BU (base year)'
PLPage 'AP27' 'Appendix: AP2027 consolidated P&L by BU'
PLPage 'AP28' 'Appendix: AP2028 consolidated P&L by BU (direction)'

# ================= 13. Reconciliation to ConsoAll =================
$s = Page 'Appendix: every TWPC total in this deck ties to the ConsoAll sheet' $SRC
Card $s 30 88 900 420 | Out-Null
$wd = @(200, 100, 100, 90, 130, 110)
$rows = @(@{ cells = @('MB', 'ConsoAll', 'This deck', 'Difference', 'BU sheets + Corp + ElimBU', 'Unreconciled'); bold = $true; color = $NAVY; line = $true; h = 24; size = 9.5 })
foreach ($scn in @('LE26', 'AP27', 'AP28')) {
  $rows += @{ cells = @($SCL[$scn], '', '', '', '', ''); bold = $true; color = $NAVY; h = 18 }
  foreach ($kv in @(@('ns', 'Net sales'), @('gp', 'Gross profit'), @('opba', 'OP before admin'), @('adp', 'Admin - people'), @('adn', 'Admin - non-people'), @('np', 'Net profit'))) {
    $tot = [double]$PL.$scn.($kv[0]).TWPC; $un = [double]$PL.$scn.($kv[0]).Unrec
    $deck = $tot   # every deck total is read from ConsoAll
    $row = @{ cells = @($kv[1], ('{0:N1}' -f $tot), ('{0:N1}' -f $deck), ('{0:N1}' -f ($deck - $tot)), ('{0:N1}' -f ($tot - $un)), ('{0:N1}' -f $un)); indent = 12; h = 16; size = 9; colors = @($null, $null, $null, $GREEN, $null, $(if ([Math]::Abs($un) -ge 0.05) { $RED } else { $MUTED })) }
    $rows += $row
  }
}
$yy = Grid $s 46 98 $wd 16 $rows
T $s 46 ($yy + 8) 868 40 ('Unreconciled = ConsoAll ' + [char]0x2212 + ' (StarchBU + HVABU + Waxy + FoodBU + NBGBU + ElimBU + Corp). It sits inside Corp / Elim in this deck so that every table adds to ConsoAll. ConsoAll row 2 lists the BU sheets without Corp, but its values include the Corp sheet.') 9 $TEXT $false 'l' | Out-Null

# remove the template's own slides, save, export
for ($i = $script:orig; $i -ge 1; $i--) { $pres.Slides.Item($i).Delete() }
$pres.SaveAs($Out)
if ($PngDir) { New-Item -ItemType Directory -Force $PngDir | Out-Null; for ($i = 1; $i -le $pres.Slides.Count; $i++) { $pres.Slides.Item($i).Export((Join-Path $PngDir ('s{0:D2}.png' -f $i)), 'PNG', 1600, 900) } }
$pres.Close()
if (-not $wasRunning) { $app.Quit() }
Write-Output ('saved ' + $Out)



