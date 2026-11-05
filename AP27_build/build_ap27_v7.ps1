# AP2027/AP2028 group consolidation deck v5 (02-Nov: 2024 Rebase horizon, scaled bridge, HVA incl. Waxy tables) on the Thai Wah template, built with PowerPoint COM.
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

$SRC = 'Source: P&L LE9+3 file (AP2027-2028); TWPC totals = sheet ConsoAll, BUs = BU sheets. MB = million baht.'
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

$SCL['R24'] = '2024 Rebase'
# ================= 3. TWPC at a glance: 2024 Rebase to 2028 AP, mix chart + commentary beneath =================
$SC3 = @('R24', '2025', 'LE26', 'AP27', 'AP28')
$opba26 = [double]$ST.LE26.opba; $opba27 = [double]$ST.AP27.opba
$s = Page $TX.gl_title $SRC
Card $s 30 88 545 420 | Out-Null
T $s 46 100 500 18 'TWPC financials by BU' 14 $NAVY $true 'l' | Out-Null
T $s 46 119 500 14 'OPBA by BU (MB), 2024 Rebase to 2028 AP' 10 $MUTED $false 'l' | Out-Null
Legend $s 46 138 @(@('Food', $NAVY), @('HVA incl. Waxy', $HVAC), @('Starch', $CYAN), @('NBG & other', $GREY))
$labW = 120; $colW = 82; $cx0 = 46 + $labW
$yBase = 318; $kk = 145 / 1400.0
Rect $s ($cx0 + 3 * $colW) 156 $colW 330 $TINT | Out-Null
for ($i = 0; $i -lt 5; $i++) {
  $scn = $SC3[$i]; $c = $cx0 + $colW * ($i + 0.5); $bw = 40; $bx = $c - $bw / 2
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
# data strip: every figure centred under its bar
$rows = @()
$rows += @{ cells = @('') + ($SC3 | ForEach-Object { $SCL[$_] }); bold = $true; color = $NAVY; line = $true; h = 20; center = $true }
$rows += @{ cells = @('Volume (kt)') + ($SC3 | ForEach-Object { '{0:N0}' -f [double]$ST.$_.vol }); line = $true; center = $true }
$rows += @{ cells = @('  % Vol growth') + ($SC3 | ForEach-Object { $g0 = [double]$DATA.volg.$_; ('{0}{1:N1}%' -f $(if ($g0 -ge 0) { '+' } else { [string][char]0x2212 }), [Math]::Abs($g0 * 100)) }); line = $true; color = $MUTED; italic = $true; center = $true }
$rows += @{ cells = @('Net sales (MB)') + ($SC3 | ForEach-Object { '{0:N0}' -f [double]$ST.$_.ns }); line = $true; center = $true }
$rows += @{ cells = @('Gross profit (MB)') + ($SC3 | ForEach-Object { '{0:N0}' -f [double]$ST.$_.gp }); line = $true; center = $true }
$rows += @{ cells = @('  %GM') + ($SC3 | ForEach-Object { '{0:N1}%' -f ([double]$ST.$_.gm * 100) }); line = $true; color = $MUTED; italic = $true; center = $true }
$rows += @{ cells = @('OPBA (MB)') + ($SC3 | ForEach-Object { '{0:N0}' -f [double]$ST.$_.opba }); line = $true; bold = $true; color = $NAVY; center = $true }
$rows += @{ cells = @('Net profit (MB)') + ($SC3 | ForEach-Object { N0 $ST.$_.np }); line = $true; bold = $true; color = $NAVY; center = $true }
Grid $s 46 336 @($labW, $colW, $colW, $colW, $colW, $colW) 18 $rows | Out-Null
T $s 46 488 510 12 '2028 AP shaded lighter = direction only. NBG and other items shown below the axis when negative.' 8 $MUTED $false 'l' | Out-Null
Card $s 590 88 340 420 | Out-Null
Kicker $s 606 100 310 'OPBA MIX ACROSS THE CORE BUs' | Out-Null
$yy = 120
foreach ($scn in @('2025', 'LE26', 'AP27', 'AP28')) {
  $v = $SK.$scn; $tot = 0.0; foreach ($bu in $STACK) { $tot += [double]$v.$bu }
  T $s 606 $yy 80 13 $SCL[$scn] 10 $NAVY $true 'l' | Out-Null
  T $s 830 $yy 84 13 ((N0 $DATA.mix_total.$scn) + ' MB') 9 $MUTED $false 'r' | Out-Null   # grey label = left-chart total OPBA (ConsoAll)
  $x = 606; $barW = 308
  foreach ($bu in $STACK) {
    $w = $barW * [double]$v.$bu / $tot; Rect $s $x ($yy + 15) $w 16 $BUCOL[$bu] | Out-Null
    T $s $x ($yy + 17) $w 12 ('{0:N0}%' -f ([double]$v.$bu / $tot * 100)) 9 $BUTXT[$bu] $true 'c' | Out-Null
    $x += $w
  }
  $yy += 36
}
Legend $s 606 ($yy) @(@('Food', $NAVY), @('HVA incl. Waxy', $HVAC), @('Starch', $CYAN))
T $s 606 ($yy + 15) 308 11 'Share = BU OPBA / (Food + HVA incl. Waxy + Starch); label = TWPC total OPBA' 7.5 $MUTED $false 'l' | Out-Null
L $s 606 ($yy + 32) 914 ($yy + 32) $LINE 0.5 $false | Out-Null
Kicker $s 606 ($yy + 40) 310 'WHAT AP2027 COMMITS TO' | Out-Null
$yy += 58
foreach ($it in $TX.gl_items) {
  T $s 606 $yy 82 22 $it[0] 16 $NAVY $true 'l' | Out-Null
  TR $s 692 ($yy + 1) 222 38 @(@($it[1], $true, $NAVY), @($it[2], $false, $TEXT)) 9.5 | Out-Null
  $yy += 40
}

# ================= 4. OPBA bridge LE26 -> AP27 -> AP28 on one scale, axis not from zero, no Corp / Elim bar =================
$B4 = $DATA.bridge4
$s = Page $TX.br4_title $SRC
Card $s 30 88 615 420 | Out-Null
T $s 46 100 580 18 'OPBA bridge by BU (MB): 2026 LE to 2027 AP to 2028 AP' 14 $NAVY $true 'l' | Out-Null
$floor = 750.0; $ceil = 1430.0
$sw = 52.0; $x0 = 160.0; $yTop = 140; $yBase = 330; $k = ($yBase - $yTop) / ($ceil - $floor); $bwd = 38
function YV($val) { return $yBase - ([double]$val - $floor) * $k }
$names = @('2026 LE', 'Food', 'HVA incl. Waxy', 'Starch', 'NBG', '2027 AP', ($DELTA + ' 2028 by BU'), '2028 AP')
$cx = @(); for ($i = 0; $i -lt 8; $i++) { $cx += ($x0 + $sw * ($i + 0.5) + $(if ($i -eq 7) { 50 } else { 0 })) }   # room before 2028 AP for the small segment labels
function FYBar($i, $val, $fill, $transp) {
  $top = YV $val
  $rb = Rect $s ($cx[$i] - $bwd / 2) $top $bwd ($yBase - $top) $fill
  if ($transp) { $rb.Fill.Transparency = [single]0.35 }
  # axis-break mark: a white gap near the base shows the bar does not start at zero
  Rect $s ($cx[$i] - $bwd / 2 - 1) ($yBase - 9) ($bwd + 2) 2.5 $WHITE | Out-Null
  T $s ($cx[$i] - 32) ($top - 15) 64 13 (N0 $val) 10.5 $NAVY $true 'c' | Out-Null
}
FYBar 0 $B4.le26 $NAVY $false
$run = [double]$B4.le26
for ($i = 1; $i -le 4; $i++) {
  $dv = [double]$B4.steps27[$i - 1][1]
  L $s ($cx[$i - 1] + $bwd / 2) (YV $run) ($cx[$i] - $bwd / 2) (YV $run) $MUTED 0.5 $true | Out-Null
  $yA = YV ($run + [Math]::Max(0, $dv)); $h = [Math]::Max(1.5, [Math]::Abs($dv) * $k)
  Rect $s ($cx[$i] - $bwd / 2) $yA $bwd $h $(if ($dv -ge 0) { $GREEN } else { $RED }) | Out-Null
  T $s ($cx[$i] - 30) ($yA - 14) 60 13 (SG $dv) 10 $(if ($dv -ge 0) { $GREEN } else { $RED }) $true 'c' | Out-Null
  $run += $dv
}
L $s ($cx[4] + $bwd / 2) (YV $run) ($cx[5] - $bwd / 2) (YV $run) $MUTED 0.5 $true | Out-Null
FYBar 5 $B4.ap27 $CYAN $false
# stacked 2028 increment on the same scale (Food bottom, HVA, Starch, NBG on top)
$segCol = @{ 'Food' = $NAVY; 'HVA incl. Waxy' = $HVAC; 'Starch' = $CYAN; 'NBG' = $GREY }
$segTxt = @{ 'Food' = $WHITE; 'HVA incl. Waxy' = $NAVY; 'Starch' = $WHITE; 'NBG' = $NAVY }
$segShort = @{ 'Food' = 'Food'; 'HVA incl. Waxy' = 'HVA'; 'Starch' = 'Starch'; 'NBG' = 'NBG' }
$cum = [double]$B4.ap27
L $s ($cx[5] + $bwd / 2) (YV $cum) ($cx[6] - $bwd / 2) (YV $cum) $MUTED 0.5 $true | Out-Null
foreach ($p in $B4.inc28) {
  $nm = [string]$p[0]; $dv = [double]$p[1]; $yA = YV ($cum + $dv); $h = [Math]::Max(1.5, $dv * $k)
  Rect $s ($cx[6] - $bwd / 2) $yA $bwd $h $segCol[$nm] | Out-Null
  if ($h -ge 11) { T $s ($cx[6] - $bwd / 2) ($yA + $h / 2 - 5.5) $bwd 11 (SG $dv) 8.5 $segTxt[$nm] $true 'c' | Out-Null }
  else { T $s ($cx[6] + $bwd / 2 + 3) ($yA + $h / 2 - 5.5) 42 11 ($segShort[$nm] + ' ' + (SG $dv)) 7.5 $TEXT $false 'l' | Out-Null }
  $cum += $dv
}
T $s ($cx[6] - 36) ((YV $cum) - 16) 72 14 ('Total ' + (SG ([double]$DATA.inc_total.AP28))) 10.5 $GREEN $true 'c' | Out-Null
L $s ($cx[6] + $bwd / 2 + 46) (YV $cum) ($cx[7] - $bwd / 2) (YV $cum) $MUTED 0.5 $true | Out-Null   # starts after the small segment label
FYBar 7 $B4.ap28 $CYAN $true
L $s $x0 $yBase ($x0 + 8 * $sw + 50) $yBase $LINE 0.75 $false | Out-Null
for ($i = 0; $i -lt 8; $i++) { T $s ($cx[$i] - 31) ($yBase + 4) 62 26 $names[$i] 10 $NAVY $true 'c' | Out-Null }
# total incremental 2026 LE -> 2027 AP: bracket above the BU steps
$yb = (YV ($run + 0)) - 36
L $s $cx[0] $yb $cx[5] $yb $GREEN 1 $false | Out-Null; L $s $cx[0] $yb $cx[0] ($yb + 7) $GREEN 1 $false | Out-Null; L $s $cx[5] $yb $cx[5] ($yb + 7) $GREEN 1 $false | Out-Null
$bx0 = ($cx[0] + $cx[5]) / 2 - 80; Rect $s $bx0 ($yb - 8) 160 16 $WHITE | Out-Null
T $s $bx0 ($yb - 7) 160 14 ('Total incremental ' + (SG ([double]$DATA.inc_total.AP27))) 10.5 $GREEN $true 'c' | Out-Null
# legend for the stacked increment
Legend $s 46 150 @(@('Food', $NAVY), @('HVA', $HVAC))
Legend $s 46 165 @(@('Starch', $CYAN), @('NBG', $GREY))
T $s 46 182 110 24 ('Stacked bar: AP27 ' + $ARROW + ' AP28 by BU') 7.5 $MUTED $false 'l' | Out-Null
# year rows under the chart
L $s 46 362 629 362 $LINE 0.5 $false | Out-Null
$rl = @(@('2026 LE', 'LE26'), @('2027 AP', 'AP27'), @('2028 AP', 'AP28'), @('Growth %', 'g'))
$bn = @('Food', 'HVA incl. Waxy', 'Starch', 'NBG')
for ($ri = 0; $ri -lt 4; $ri++) {
  $ly = 368 + $ri * 19; $key = $rl[$ri][1]
  T $s 46 $ly 100 15 $rl[$ri][0] 10.5 $NAVY $true 'l' | Out-Null
  for ($i = 0; $i -lt 8; $i++) {
    $val = ''
    if ($i -ge 1 -and $i -le 4) {
      $lv = $B4.lvl.($bn[$i - 1])
      if ($key -eq 'g') { $val = $(if ([double]$lv.LE26 -le 0.5) { 'n.m.' } else { GR $lv.LE26 $lv.AP27 }) } else { $val = N0 $lv.$key }
    }
    elseif ($i -eq 0 -and $key -eq 'LE26') { $val = N0 $B4.le26 }
    elseif ($i -eq 5 -and $key -eq 'AP27') { $val = N0 $B4.ap27 }
    elseif ($i -eq 5 -and $key -eq 'g') { $val = GR $B4.le26 $B4.ap27 }
    elseif ($i -eq 6 -and $key -eq 'AP28') { $val = SG ([double]$DATA.inc_total.AP28) }
    elseif ($i -eq 5 -and $key -eq 'LE26') { $val = '' }
    elseif ($i -eq 7 -and $key -eq 'AP28') { $val = N0 $B4.ap28 }
    elseif ($i -eq 7 -and $key -eq 'g') { $val = GR $B4.ap27 $B4.ap28 }
    T $s ($cx[$i] - $sw / 2 - 2) $ly ($sw + 4) 15 $val 10.5 $(if ($key -eq 'g') { $MUTED } else { $TEXT }) ($i -eq 0 -or $i -eq 5 -or $i -eq 6 -or $i -eq 7) 'c' | Out-Null
  }
}
T $s 46 444 580 11 ('Axis starts at ' + ('{0:N0}' -f $floor) + ' MB (not zero) so the increments are visible; one scale for 2027 and 2028. Growth %: BUs and 2027 AP vs 2026 LE; 2028 AP vs 2027 AP.') 7.5 $MUTED $false 'l' | Out-Null
Note $s 46 457 583 42 @(@($TX.br4_note[0], $true, $NAVY), @($TX.br4_note[1], $false, $TEXT))
Card $s 660 88 270 420 | Out-Null
Kicker $s 676 100 240 ('WHAT DRIVES EACH BU ' + $DOT + ' AP27 VS LE') | Out-Null
$yy = 122; $ix = 0
$drv = @($TX.drv | Where-Object { [string]$_[0] -ne 'Corp / Elim' })
foreach ($dv in $drv) {
  $ix++
  T $s 676 $yy 170 17 $dv[0] 13 $NAVY $true 'l' | Out-Null
  T $s 850 $yy 64 17 (SG $dv[1]) 13 (DCol $dv[1]) $true 'r' | Out-Null
  $yy += 17
  $subs = $dv[2]; if ($subs.Count -gt 0 -and -not ($subs[0] -is [array])) { $subs = ,$subs }
  foreach ($sb in $subs) {
    T $s 688 $yy 170 13 $sb[0] 10 $TEXT $false 'l' | Out-Null
    if ($null -ne $sb[1]) { T $s 850 $yy 64 13 (SG $sb[1]) 10 (DCol $sb[1]) $false 'r' | Out-Null }
    $yy += 13.5
  }
  $yy += 8
  if ($ix -lt $drv.Count) { L $s 676 ($yy - 4) 914 ($yy - 4) $LINE 0.5 $false | Out-Null }
}
L $s 676 ($yy + 2) 914 ($yy + 2) $NAVY 0.75 $false | Out-Null
T $s 676 ($yy + 8) 170 17 'Total incremental' 13 $NAVY $true 'l' | Out-Null
T $s 830 ($yy + 8) 84 17 (SG ([double]$DATA.inc_total.AP27)) 13 $GREEN $true 'r' | Out-Null
T $s 676 ($yy + 27) 238 12 'TWPC consolidated, as in the bridge' 8 $MUTED $false 'l' | Out-Null

# ================= 5. OPBA by BU and entity, 2024 Rebase to AP2027 (no Corp / Elim row) =================
$s = Page 'TWIC, TDC, TDC 2.0 and Well Grow carry most of the AP2027 uplift' $SRC
Card $s 30 88 585 420 | Out-Null
$wd = @(214, 72, 64, 64, 68, 72)
Rect $s (46 + 214 + 72 + 64 + 64) 96 68 408 $TINT | Out-Null
$rows = @(@{ cells = @('MB', '2024 Rebase', '2025', '2026 LE', '2027 AP', 'AP27 vs LE26'); bold = $true; color = $NAVY; line = $true; h = 24; size = 10.5 })
foreach ($r in $DATA.entity4) {
  $d1 = [double]$r.AP27 - [double]$r.LE26
  $row = @{ cells = @($r.label, (N0 $r.R24), (N0 $r.'2025'), (N0 $r.LE26), (N0 $r.AP27), (SG $d1)); colors = @($null, $null, $null, $null, $NAVY, (DCol $d1)); h = 16.2; size = 10.5 }
  if ($r.lvl -eq 1) { $row.indent = 12 }
  elseif ($r.lvl -eq 2) { $row.indent = 26; $row.size = 10 }
  elseif ($r.lvl -eq 9) { $row.indent = 12; $row.size = 9.5; $row.h = 15; $row.italic = $true; $row.color = $MUTED; $row.colors = @($MUTED, $MUTED, $MUTED, $MUTED, $MUTED, $MUTED); $row.line = $true }
  else { $row.bold = $true; $row.line = $true; $row.size = 12.5; $row.h = 19.5; $row.color = $NAVY }
  if ($r.lvl -eq -1) { $row.fill = $TINT; $row.color = $NAVY; $row.h = 32; $row.size = 17; $row.colors = @($NAVY, $NAVY, $NAVY, $NAVY, $NAVY, (DCol $d1)) }
  $rows += $row
}
Grid $s 46 96 $wd 16.2 $rows | Out-Null
# concise commentary: four points, card sized to its content
$nSt = $TX.st_short.Count
Card $s 630 88 300 (44 + $nSt * 64) | Out-Null
Kicker $s 646 100 270 'KEY INSIGHTS' | Out-Null
$yy = 122
foreach ($sty in $TX.st_short) {
  T $s 646 $yy 270 22 $sty[0] 18 $NAVY $true 'l' | Out-Null
  T $s 646 ($yy + 24) 270 30 $sty[1] 11 $TEXT $false 'l' | Out-Null
  $yy += 64
}





# ================= 6. From BU OPBA to net profit: P&L table 2024 Rebase to AP2028 =================
$s = Page $TX.walk_title $SRC
Card $s 30 88 615 420 | Out-Null
$wd = @(232, 72, 72, 72, 72, 72)
Rect $s (46 + 232 + 72 * 3) 98 72 357 $TINT | Out-Null
$rows = @(@{ cells = @('MB') + @($DATA.walk_years); bold = $true; color = $NAVY; line = $true; h = 22; size = 9.5 })
foreach ($r in $DATA.walk) {
  $cells = @([string]$r.label) + @($r.vals | ForEach-Object { if ($null -eq $_) { '' } else { N0 $_ } })
  $row = @{ cells = $cells; h = 19.5; size = 10 }
  switch ($r.kind) {
    'sect' { $row.bold = $true; $row.color = $NAVY; $row.h = 18 }
    'bu' { $row.indent = 12 }
    'memo' { $row.indent = 26; $row.italic = $true; $row.color = $MUTED; $row.size = 9 }
    'sub' { $row.indent = 12 }
    'subtotal' { $row.bold = $true; $row.line = $true }
    'line' { $row.line = $true }
    'total' { $row.bold = $true; $row.color = $NAVY; $row.fill = $TINT; $row.line = $true; $row.h = 21 }
  }
  $rows += $row
}
Grid $s 46 98 $wd 19.5 $rows | Out-Null
Card $s 660 88 270 420 | Out-Null
Kicker $s 676 100 240 ('WHAT MOVES NP ' + $DOT + ' AP27 VS 2026 LE') | Out-Null
$ci = 0
foreach ($cal in $TX.np_cal) {
  $y0 = 124 + $ci * 112
  T $s 676 $y0 238 26 $cal[0] 22 $NAVY $true 'l' | Out-Null
  T $s 676 ($y0 + 30) 238 14 $cal[1] 11.5 $NAVY $true 'l' | Out-Null
  T $s 676 ($y0 + 48) 238 50 $cal[2] 10 $TEXT $false 'l' | Out-Null
  L $s 676 ($y0 + 102) 914 ($y0 + 102) $LINE 0.5 $false | Out-Null
  $ci++
}
TR $s 676 352 238 120 @(@($TX.np_note[0], $true, $NAVY), @($TX.np_note[1], $false, $TEXT)) 10.5 | Out-Null

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
$B28 = $DATA.bridge28; $steps = @(); foreach ($p in $B28.steps) { if ([string]$p[0] -ne 'Corp / Elim') { $steps += ,@($p[0], [double]$p[1]) } }   # no Corp / Elim bar
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

# ================= 9-10. Multi-year P&L by BU (year groups x Starch / HVA incl. Waxy / Food / NBG / TWPC) =================
# BU columns stop at OPBA; the TWPC column (ConsoAll) runs down to net profit.
# Row emphasis (Por, 02-Nov): Total selling bold + underline; OPBA bold with double lines above and below;
# Operating profit bold with lines above and below; Net profit bold and highlighted.
function BuPage($years, $title) {
  $s = Page $title $SRC
  Card $s 30 88 900 420 | Out-Null
  $cols = @($DATA.bupl_cols); $nc = $cols.Count; $nY = $years.Count
  $labW0 = 150; $gap = 5; $x0 = 44
  $cw = (870 - $labW0 - ($nY - 1) * $gap) / ($nY * $nc)
  $colX = @(); for ($g = 0; $g -lt $nY; $g++) { for ($j = 0; $j -lt $nc; $j++) { $colX += ($x0 + $labW0 + $g * ($nc * $cw + $gap) + $j * $cw) } }
  $right = $x0 + $labW0 + $nY * ($nc * $cw + $gap) - $gap
  $yH = 93
  for ($g = 0; $g -lt $nY; $g++) {
    $gx = $colX[$g * $nc]
    Rect $s $gx $yH ($nc * $cw) 19 $(if ($years[$g] -eq 'AP27') { $CYAN } else { $NAVY }) | Out-Null
    T $s $gx ($yH + 2) ($nc * $cw) 15 $SCL[$years[$g]] 12 $WHITE $true 'c' | Out-Null
    for ($j = 0; $j -lt $nc; $j++) {
      $isT = ($j -eq $nc - 1)
      Rect $s ($colX[$g * $nc + $j] + 0.5) ($yH + 20) ($cw - 1) 27 $(if ($isT) { $NAVY } else { (RGB 'd9dde6') }) | Out-Null
      $hd = T $s ($colX[$g * $nc + $j] + 1) ($yH + 21) ($cw - 2) 25 $cols[$j] 9 $(if ($isT) { $WHITE } else { $NAVY }) $true 'c'
      $hd.TextFrame.VerticalAnchor = 3
    }
  }
  T $s $x0 ($yH + 33) $labW0 12 'Million baht' 9 $MUTED $false 'l' | Out-Null
  $nRows = $DATA.bupl.($years[0]).Count; $rh = 16.0
  $y0t = $yH + 49
  for ($g = 0; $g -lt $nY; $g++) { Rect $s ($colX[$g * $nc + $nc - 1] + 0.5) ($y0t - 1) ($cw - 1) ($nRows * $rh + 1) $TINT | Out-Null }
  $y = $y0t
  for ($ri = 0; $ri -lt $nRows; $ri++) {
    $r0 = $DATA.bupl.($years[0])[$ri]; $lb = [string]$r0.label
    $isPct = ($r0.kind -eq 'pct'); $bold = [bool]$r0.key
    $isSell = ($lb -eq 'Total selling'); $isOpba = ($lb -eq 'OP before admin'); $isOp = ($lb -eq 'Operating profit'); $isNp = ($lb -eq 'Net profit')
    if ($isNp) { Rect $s $x0 $y ($right - $x0) $rh (RGB 'cdeefa') | Out-Null }
    $lab = $(if ($isPct) { '   ' + $lb } else { $lb })
    $lt = T $s $x0 $y $labW0 $rh $lab 10.5 $(if ($bold) { $NAVY } elseif ($isPct) { $MUTED } else { $TEXT }) $bold 'l'
    $lt.TextFrame.VerticalAnchor = 3; if ($isPct) { $lt.TextFrame.TextRange.Font.Italic = -1 }; if ($isSell) { $lt.TextFrame.TextRange.Font.Underline = -1 }
    for ($g = 0; $g -lt $nY; $g++) {
      $row = $DATA.bupl.($years[$g])[$ri]
      for ($j = 0; $j -lt $nc; $j++) {
        $v = $row.vals[$j]
        if ($null -eq $v) { continue }
        if ($isPct) { $txt = PC $v } elseif ($row.kind -eq 'kt') { $txt = N1 $v } else { $txt = N0 $v }
        $t = T $s ($colX[$g * $nc + $j] + 1) $y ($cw - 5) $rh $txt 10 $(if ($isPct) { $MUTED } elseif ($bold) { $NAVY } else { $TEXT }) $bold 'r'
        $t.TextFrame.VerticalAnchor = 3; if ($isPct) { $t.TextFrame.TextRange.Font.Italic = -1 }; if ($isSell) { $t.TextFrame.TextRange.Font.Underline = -1 }
      }
    }
    if ($isOpba) {
      # double lines above and below
      foreach ($yl in @(($y - 0.2), ($y + 1.6), ($y + $rh - 1.6), ($y + $rh + 0.2))) { L $s $x0 $yl $right $yl $NAVY 0.75 $false | Out-Null }
    } elseif ($isOp) {
      L $s $x0 $y $right $y $NAVY 0.75 $false | Out-Null; L $s $x0 ($y + $rh) $right ($y + $rh) $NAVY 0.75 $false | Out-Null
    } elseif ($bold -or $isPct -or $r0.kind -eq 'kt') { L $s $x0 ($y + $rh) $right ($y + $rh) $LINE 0.5 $false | Out-Null }
    $y += $rh
  }
  $yrLab = @{ '2025' = '2025'; 'LE26' = '2026LE'; 'AP27' = '2027AP'; 'AP28' = '2028AP' }
  $wx = @(); foreach ($yr in $years) { $wx += ($yrLab[$yr] + ' ' + (N0 $DATA.waxy_opba.$yr)) }
  T $s $x0 ($y + 5) 868 20 ('Note: HVA BU includes Waxy. Waxy OPBA (MB): ' + ($wx -join ', ') + '. BU columns stop at OP before admin; TWPC totals = consolidated total (ConsoAll) down to net profit.') 8.5 $MUTED $false 'l' | Out-Null
}
BuPage @('2025', 'LE26', 'AP27') 'Multi-year P&L by BU: 2025, 2026 LE and AP2027'
BuPage @('LE26', 'AP27', 'AP28') 'Multi-year P&L by BU: 2026 LE, AP2027 and AP2028 (direction)'

# ================= 11-16. BU deep dives: 3 BUs x 2 horizons, entity columns, down to OPBA + per-kg block =================
function N2($x) { if ($null -eq $x) { return '' }; $v = [double]$x; if ([Math]::Abs($v) -lt 0.005) { return $DASH }; if ($v -lt 0) { return ('({0:N2})' -f (-$v)) }; return ('{0:N2}' -f $v) }
function PG($x) { if ($null -eq $x) { return 'n.m.' }; $v = [double]$x; if ([Math]::Abs($v) -gt 5) { return 'n.m.' }; return ('{0}{1:N1}%' -f $(if ($v -ge 0) { '+' } else { [string][char]0x2212 }), [Math]::Abs($v * 100)) }
function DDPage($bu, $years, $take, $title) {
  $dd = $DATA.dd.$bu
  $s = Page $title $SRC
  Card $s 30 88 900 420 | Out-Null
  $cols = @($dd.cols); $nc = $cols.Count; $nY = $years.Count
  $labW0 = 138; $gap = 5; $x0 = 44
  $cw = (870 - $labW0 - ($nY - 1) * $gap) / ($nY * $nc)
  $colX = @(); for ($g = 0; $g -lt $nY; $g++) { for ($j = 0; $j -lt $nc; $j++) { $colX += ($x0 + $labW0 + $g * ($nc * $cw + $gap) + $j * $cw) } }
  $right = $x0 + $labW0 + $nY * ($nc * $cw + $gap) - $gap
  $yH = 92
  for ($g = 0; $g -lt $nY; $g++) {
    $gx = $colX[$g * $nc]
    Rect $s $gx $yH ($nc * $cw) 17 $(if ($years[$g] -eq 'AP27') { $CYAN } else { $NAVY }) | Out-Null
    T $s $gx ($yH + 2) ($nc * $cw) 13 $SCL[$years[$g]] 11 $WHITE $true 'c' | Out-Null
    for ($j = 0; $j -lt $nc; $j++) {
      $isT = ($j -eq $nc - 1)
      Rect $s ($colX[$g * $nc + $j] + 0.5) ($yH + 18) ($cw - 1) 24 $(if ($isT) { $NAVY } else { (RGB 'd9dde6') }) | Out-Null
      $hd = T $s ($colX[$g * $nc + $j] + 1) ($yH + 19) ($cw - 2) 22 $cols[$j] 8 $(if ($isT) { $WHITE } else { $NAVY }) $true 'c'
      $hd.TextFrame.VerticalAnchor = 3
    }
  }
  T $s $x0 ($yH + 28) $labW0 12 'Million baht' 8.5 $MUTED $false 'l' | Out-Null
  $rowsY = $dd.years.($years[0]); $nRows = $rowsY.Count; $rh = 13.6
  $y0t = $yH + 44
  $nTot = $nRows + 1
  for ($g = 0; $g -lt $nY; $g++) { Rect $s ($colX[$g * $nc + $nc - 1] + 0.5) ($y0t - 1) ($cw - 1) ($nTot * $rh + 1) $TINT | Out-Null }
  $y = $y0t
  for ($ri = 0; $ri -lt $nRows; $ri++) {
    $r0 = $rowsY[$ri]; $lb = [string]$r0.label
    if ($r0.sect) {
      L $s $x0 ($y + 2) $right ($y + 2) $NAVY 0.75 $false | Out-Null
      T $s $x0 ($y + 3) 300 $rh ([string]$r0.sect) 8.5 $KICK $true 'l' | Out-Null
      $y += $rh
    }
    $isPct = ($r0.kind -eq 'pct'); $isKg = ($r0.kind -eq 'kg'); $bold = [bool]$r0.key
    $isSell = ($lb -eq 'Total selling'); $isOpba = $lb.StartsWith('OP before admin')
    $lab = $(if ($isPct) { '   ' + $lb } else { $lb })
    $lt = T $s $x0 $y $labW0 $rh $lab 9.5 $(if ($bold) { $NAVY } elseif ($isPct) { $MUTED } else { $TEXT }) $bold 'l'
    $lt.TextFrame.VerticalAnchor = 3; if ($isPct) { $lt.TextFrame.TextRange.Font.Italic = -1 }; if ($isSell) { $lt.TextFrame.TextRange.Font.Underline = -1 }
    for ($g = 0; $g -lt $nY; $g++) {
      $row = $dd.years.($years[$g])[$ri]
      for ($j = 0; $j -lt $nc; $j++) {
        $v = $row.vals[$j]
        if ($lb -eq '% Vol growth') { $txt = PG $v }
        elseif ($isPct) { $txt = PC $v }
        elseif ($row.kind -eq 'kt') { $txt = N1 $v }
        elseif ($isKg) { $txt = $(if ($null -eq $v) { 'n.m.' } else { N2 $v }) }
        else { $txt = N0 $v }
        $t = T $s ($colX[$g * $nc + $j] + 1) $y ($cw - 4) $rh $txt 8.5 $(if ($isPct) { $MUTED } elseif ($bold) { $NAVY } else { $TEXT }) $bold 'r'
        $t.TextFrame.VerticalAnchor = 3; if ($isPct) { $t.TextFrame.TextRange.Font.Italic = -1 }; if ($isSell) { $t.TextFrame.TextRange.Font.Underline = -1 }
      }
    }
    if ($isOpba) { foreach ($yl in @(($y - 0.2), ($y + 1.4), ($y + $rh - 1.4), ($y + $rh + 0.2))) { L $s $x0 $yl $right $yl $NAVY 0.75 $false | Out-Null } }
    elseif ($bold -or $isPct -or $r0.kind -eq 'kt') { L $s $x0 ($y + $rh) $right ($y + $rh) $LINE 0.5 $false | Out-Null }
    $y += $rh
  }
  # per-kg takeaways box
  $by = $y + 6; $bh = 488 - $by
  Rect $s $x0 $by ($right - $x0) $bh $NOTEBG | Out-Null
  Rect $s $x0 $by 3 $bh $KICK | Out-Null
  Kicker $s ($x0 + 12) ($by + 4) 500 'UNIT ECONOMICS & PER-KG KEY TAKEAWAYS' | Out-Null
  $runs = @()
  $bi = 0
  foreach ($bl in $dd.take.$take) {
    if ($bi -gt 0) { $runs += ,@([string][char]13, $false, $TEXT) }
    $runs += ,@(([string][char]0x25AA + ' '), $false, $KICK)
    foreach ($rn in $bl) { $runs += ,@([string]$rn[0], [bool]$rn[1], $(if ($rn[1]) { $NAVY } else { $TEXT })) }
    $bi++
  }
  $tb = TR $s ($x0 + 12) ($by + 19) ($right - $x0 - 22) ($bh - 21) $runs 9.5
  $tb.TextFrame.TextRange.ParagraphFormat.SpaceAfter = [single]2
  T $s $x0 491 870 10 ($dd.note + ' Per kg = MB / volume (THB/kg); costs shown negative. n.m. = no volume or start-up base.') 7.5 $MUTED $false 'l' | Out-Null
}
foreach ($bu in @('Starch', 'HVA', 'Food')) {
  $nm = [string]$DATA.dd.$bu.title
  DDPage $bu @('2025', 'LE26', 'AP27') 'A' ($nm + ' deep dive: 2025, 2026 LE and AP2027')
  DDPage $bu @('LE26', 'AP27', 'AP28') 'B' ($nm + ' deep dive: 2026 LE, AP2027 and AP2028 (direction)')
}

# remove the template's own slides, save, export
for ($i = $script:orig; $i -ge 1; $i--) { $pres.Slides.Item($i).Delete() }
$pres.SaveAs($Out)
if ($PngDir) { New-Item -ItemType Directory -Force $PngDir | Out-Null; for ($i = 1; $i -le $pres.Slides.Count; $i++) { $pres.Slides.Item($i).Export((Join-Path $PngDir ('s{0:D2}.png' -f $i)), 'PNG', 1600, 900) } }
$pres.Close()
if (-not $wasRunning) { $app.Quit() }
Write-Output ('saved ' + $Out)









