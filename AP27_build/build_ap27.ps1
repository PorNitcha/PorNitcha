# AP2027/AP2028 group consolidation deck for CEO, built with PowerPoint COM from ap27_deck.json
# Style follows the BU AP finance slides (kicker + message title, white cards on light grey, blue BU stacks, waterfalls with data strip)
# Usage: powershell -File build_ap27.ps1 <ap27_deck.json> <out.pptx> <png dir>
param([string]$Json, [string]$Out, [string]$PngDir)
$D = Get-Content -LiteralPath $Json -Encoding UTF8 -Raw | ConvertFrom-Json
function RGB($hex) { $r = [Convert]::ToInt32($hex.Substring(0,2),16); $g = [Convert]::ToInt32($hex.Substring(2,2),16); $b = [Convert]::ToInt32($hex.Substring(4,2),16); return $r + $g*256 + $b*65536 }
$NAVY = RGB '1b2559'; $BLUE = RGB '2337c6'; $MID = RGB '6f8fe8'; $LIGHT = RGB 'afc3f5'; $GREY = RGB 'a6a6a6'
$KICK = RGB '1f78c1'; $GREEN = RGB '2e9e5b'; $RED = RGB 'd64545'; $TEXT = RGB '333f50'; $MUTED = RGB '7f8a9a'
$BG = RGB 'f3f5f9'; $WHITE = RGB 'ffffff'; $TINT = RGB 'eaf0fb'; $LINE = RGB 'd9dee7'; $NOTE = RGB 'e8f1fb'
$FONT = 'Arial'
$BUCOL = @{ Food = $BLUE; Starch = $MID; HVA = $LIGHT; Other = $GREY }
$DASH = [string][char]0x2013; $ARROW = [string][char]0x2192; $DOT = [string][char]0x00B7

function N0($x) { if ($null -eq $x) { return $DASH }; $v = [double]$x; if ([Math]::Abs($v) -lt 0.5) { return $DASH }; if ($v -lt 0) { return ('({0:N0})' -f (-$v)) }; return ('{0:N0}' -f $v) }
function N1($x) { if ($null -eq $x) { return $DASH }; $v = [double]$x; if ([Math]::Abs($v) -lt 0.05) { return $DASH }; if ($v -lt 0) { return ('({0:N1})' -f (-$v)) }; return ('{0:N1}' -f $v) }
function SG($x) { $v = [double]$x; if ([Math]::Abs($v) -lt 0.5) { return '0' }; if ($v -gt 0) { return ('+{0:N0}' -f $v) }; return ('({0:N0})' -f (-$v)) }
function PC($x) { if ($null -eq $x) { return $DASH }; $v = [double]$x; if ([Math]::Abs($v) -gt 1) { return 'n.m.' }; return ('{0:N1}%' -f ($v * 100)) }
function GR($a, $b) { $a = [double]$a; $b = [double]$b; if ($a -le 0.5) { return 'n.m.' }; $g = ($b - $a) / $a; return ('{0}{1:N0}%' -f $(if ($g -ge 0) { '+' } else { '' }), ($g * 100)) }

$wasRunning = [bool](Get-Process POWERPNT -ErrorAction SilentlyContinue)  # never quit a PowerPoint the user already has open
if ($wasRunning -and -not $env:DECK_ALLOW_RUNNING_PPT) { Write-Output 'STOP: PowerPoint is open.'; exit 2 }
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Add(0)
$pres.PageSetup.SlideWidth = [single]960; $pres.PageSetup.SlideHeight = [single]540
$blank = $pres.SlideMaster.CustomLayouts.Item(7)
$script:page = 0

function T($slide, $x, $y, $w, $h, $text, $size, $color, $bold, $align) {
  $s = $slide.Shapes.AddTextbox(1, [single]$x, [single]$y, [single]$w, [single]$h)
  $tf = $s.TextFrame; $tf.WordWrap = -1; $tf.AutoSize = 0
  $tf.MarginLeft = [single]0; $tf.MarginRight = [single]0; $tf.MarginTop = [single]0; $tf.MarginBottom = [single]0
  $tr = $tf.TextRange; $tr.Text = $text; $tr.Font.Name = $FONT; $tr.Font.Size = [single]$size; $tr.Font.Color.RGB = $color
  $tr.Font.Bold = $(if ($bold) { -1 } else { 0 })
  $tr.ParagraphFormat.Alignment = $(if ($align -eq 'c') { 2 } elseif ($align -eq 'r') { 3 } else { 1 })
  $s.Width = [single]$w; $s.Height = [single]$h
  return $s
}
# rich text: list of @(text, bold, color) runs in one box
function TR($slide, $x, $y, $w, $h, $runs, $size) {
  if ($runs.Count -gt 0 -and -not ($runs[0] -is [array])) { $runs = ,$runs }
  $s = T $slide $x $y $w $h '' $size $TEXT $false 'l'
  $tr = $s.TextFrame.TextRange; $pos = 1
  foreach ($r in $runs) {
    $added = $tr.InsertAfter($r[0])
    $added.Font.Name = $FONT; $added.Font.Size = [single]$size; $added.Font.Bold = $(if ($r[1]) { -1 } else { 0 }); $added.Font.Color.RGB = $r[2]
  }
  $s.Width = [single]$w; $s.Height = [single]$h
  return $s
}
function Rect($slide, $x, $y, $w, $h, $fill) {
  $s = $slide.Shapes.AddShape(1, [single]$x, [single]$y, [single]$w, [single]$h)
  $s.Fill.ForeColor.RGB = $fill; $s.Fill.Solid(); $s.Line.Visible = 0; $s.Shadow.Visible = 0
  return $s
}
function Card($slide, $x, $y, $w, $h) {
  $s = $slide.Shapes.AddShape(5, [single]$x, [single]$y, [single]$w, [single]$h)
  $s.Adjustments.Item(1) = [single]0.035
  $s.Fill.ForeColor.RGB = $WHITE; $s.Fill.Solid(); $s.Line.Visible = 0
  $s.Shadow.Visible = -1; $s.Shadow.ForeColor.RGB = (RGB 'b8c0cc'); $s.Shadow.Transparency = [single]0.75; $s.Shadow.Blur = [single]8; $s.Shadow.OffsetX = [single]0; $s.Shadow.OffsetY = [single]2
  return $s
}
function L($slide, $x1, $y1, $x2, $y2, $color, $w, $dash) {
  $s = $slide.Shapes.AddLine([single]$x1, [single]$y1, [single]$x2, [single]$y2)
  $s.Line.ForeColor.RGB = $color; $s.Line.Weight = [single]$w
  if ($dash) { $s.Line.DashStyle = 4 }
  return $s
}
function Kicker($slide, $x, $y, $w, $text) { $s = T $slide $x $y $w 14 $text 9.5 $KICK $true 'l'; $s.TextFrame2.TextRange.Font.Spacing = [single]1; return $s }
function Page($kicker, $title, $source) {
  $script:page++
  $sl = $pres.Slides.AddSlide($pres.Slides.Count + 1, $blank)
  $bgShape = Rect $sl 0 0 960 540 $BG
  Rect $sl 30 20 4 50 $KICK | Out-Null
  Kicker $sl 44 20 860 $kicker | Out-Null
  T $sl 44 36 890 34 $title 22 $NAVY $true 'l' | Out-Null
  if ($source) { T $sl 30 516 820 14 $source 8 $MUTED $false 'l' | Out-Null }
  T $sl 900 516 30 14 ([string]$script:page) 8 $MUTED $false 'r' | Out-Null
  return $sl
}
function Note($slide, $x, $y, $w, $h, $runs) {
  Rect $slide $x $y $w $h $NOTE | Out-Null
  Rect $slide $x $y 3 $h $KICK | Out-Null
  $t = TR $slide ($x + 12) ($y + 6) ($w - 20) ($h - 10) $runs 11
  $t.TextFrame.VerticalAnchor = 3
}

# ---- waterfall: start bar, floating steps, end bar; returns x centres of every bar
function Waterfall($slide, $x0, $yTop, $yBase, $w, $startLbl, $start, $steps, $endLbl, $end, $vmax, $endFill) {
  $n = $steps.Count + 2; $slot = $w / $n; $bw = [Math]::Min(44, $slot * 0.62); $k = ($yBase - $yTop) / $vmax
  $cx = @()
  $bars = @(@{ name = $startLbl; v = [double]$start; kind = 'total' })
  foreach ($st in $steps) { $bars += @{ name = [string]$st[0]; v = [double]$st[1]; kind = 'step' } }
  $bars += @{ name = $endLbl; v = [double]$end; kind = 'end' }
  $run = 0.0; $prevTopY = $null
  for ($i = 0; $i -lt $n; $i++) {
    $b = $bars[$i]; $c = $x0 + $slot * ($i + 0.5); $cx += $c; $bx = $c - $bw / 2
    if ($b.kind -ne 'step') {
      $h = [Math]::Max(1.5, $b.v * $k); $fill = $(if ($b.kind -eq 'end') { $endFill } else { $NAVY })
      Rect $slide $bx ($yBase - $h) $bw $h $fill | Out-Null
      T $slide ($c - 40) ($yBase - $h - 16) 80 14 (N0 $b.v) 11 $NAVY $true 'c' | Out-Null
      $run = $b.v
    } else {
      $from = $run; $to = $run + $b.v
      $yA = $yBase - [Math]::Max($from, $to) * $k; $h = [Math]::Max(1.5, [Math]::Abs($b.v) * $k)
      Rect $slide $bx $yA $bw $h $(if ($b.v -ge 0) { $GREEN } else { $RED }) | Out-Null
      if ($b.v -ge 0) { T $slide ($c - 40) ($yA - 15) 80 13 (SG $b.v) 10.5 $GREEN $true 'c' | Out-Null }
      else { T $slide ($c - 40) ($yA + $h + 2) 80 13 (SG $b.v) 10.5 $RED $true 'c' | Out-Null }
      $run = $to
    }
    # connector to the next bar at the running level
    if ($i -lt $n - 1) { $yl = $yBase - $run * $k; L $slide ($bx + $bw) $yl ($bx + $slot) $yl $MUTED 0.5 $true | Out-Null }
    T $slide ($c - $slot / 2) ($yBase + 4) $slot 24 $b.name 9 $TEXT $false 'c' | Out-Null
  }
  L $slide $x0 $yBase ($x0 + $w) $yBase $LINE 0.75 $false | Out-Null
  return ,$cx
}

# ---- plain table on shapes (keeps fonts/alignment under control)
function Grid($slide, $x, $y, $widths, $rowH, $rows, $opts) {
  # rows: list of @{ cells = @(...); bold; fill; color; colors (per cell) ; size }
  $yy = $y
  foreach ($r in $rows) {
    $h = $(if ($r.h) { $r.h } else { $rowH })
    if ($r.fill) { $tw = 0; foreach ($cw in $widths) { $tw += $cw }; Rect $slide $x $yy $tw $h $r.fill | Out-Null }
    $xx = $x
    for ($c = 0; $c -lt $widths.Count; $c++) {
      $txt = [string]$r.cells[$c]
      if ($txt -ne '') {
        $col = $(if ($r.colors -and $r.colors[$c]) { $r.colors[$c] } elseif ($r.color) { $r.color } else { $TEXT })
        $al = $(if ($c -eq 0) { 'l' } else { 'r' }); $ind = $(if ($c -eq 0 -and $r.indent) { $r.indent } else { 0 })
        $sz = $(if ($r.size) { $r.size } else { 10 })
        $t = T $slide ($xx + 4 + $ind) $yy ($widths[$c] - 8 - $ind) $h $txt $sz $col ([bool]$r.bold) $al
        $t.TextFrame.VerticalAnchor = 3
        if ($r.italic) { $t.TextFrame.TextRange.Font.Italic = -1 }
      }
      $xx += $widths[$c]
    }
    if ($r.line) { $tw = 0; foreach ($cw in $widths) { $tw += $cw }; L $slide $x ($yy + $h) ($x + $tw) ($yy + $h) $LINE 0.5 $false | Out-Null }
    $yy += $h
  }
  return $yy
}
function DCol($v) { $v = [double]$v; if ($v -ge 0.5) { return $GREEN } elseif ($v -le -0.5) { return $RED } else { return $MUTED } }

$SRC = 'Source: P&L AP2027-2028 / LE2026 (9+3) consolidation file (Board version as presented by each BU). MB = million baht. HVA excludes Waxy.'
$SC = @('2025', 'AP26', 'LE26', 'AP27', 'AP28'); $SCL = @{ '2025' = '2025'; 'AP26' = 'AP2026'; 'LE26' = '2026 LE'; 'AP27' = '2027 AP'; 'AP28' = '2028 AP' }

# ================= 1. Title =================
$script:page++
$s = $pres.Slides.AddSlide(1, $blank)
Rect $s 0 0 960 540 $NAVY | Out-Null
Rect $s 60 170 4 120 $KICK | Out-Null
$k = T $s 76 170 700 16 ('TWPC  ' + $DOT + '  ANNUAL PLAN 2027') 11 (RGB '8fb3e8') $true 'l'; $k.TextFrame2.TextRange.Font.Spacing = [single]1.5
T $s 76 192 800 60 'AP2027 group consolidation' 36 $WHITE $true 'l' | Out-Null
T $s 76 240 800 30 ('How each BU contributes to the TWPC plan ' + $DOT + ' AP2028 as direction') 18 (RGB 'cfdcf5') $false 'l' | Out-Null
T $s 76 300 800 16 ('CEO review ' + $DOT + ' November 2026 ' + $DOT + ' Finance / FP&A') 11 (RGB '8fb3e8') $false 'l' | Out-Null
T $s 76 480 820 14 'Numbers as presented in the BU AP sessions; this deck only consolidates them. Private and confidential.' 9 (RGB '8fb3e8') $false 'l' | Out-Null

# ================= 2. Group at a glance =================
$st = $D.strip; $sk = $D.opba_stack
$opba26 = [double]$st.LE26.opba; $opba27 = [double]$st.AP27.opba; $np26 = [double]$st.LE26.np; $np27 = [double]$st.AP27.np
$s = Page ('TWPC ' + $DOT + ' AP2027 AT A GLANCE') ('AP2027: OPBA +' + ('{0:N0}' -f (($opba27/$opba26-1)*100)) + '% to ' + ('{0:N0}' -f $opba27) + ' MB, but net profit only +' + ('{0:N0}' -f ($np27-$np26)) + ' MB to ' + ('{0:N0}' -f $np27) + ' MB') $SRC
Card $s 30 88 545 420 | Out-Null
T $s 46 100 500 18 'TWPC financials by BU' 14 $NAVY $true 'l' | Out-Null
T $s 46 119 500 14 'OPBA by BU (MB), 2025 actual to 2028 AP' 10 $MUTED $false 'l' | Out-Null
# legend
$lx = 46; foreach ($p in @(@('Food', $BLUE), @('Starch', $MID), @('HVA', $LIGHT), @('NBG, Waxy, Corp/Elim', $GREY))) { Rect $s $lx 140 8 8 $p[1] | Out-Null; T $s ($lx + 11) 138 140 12 $p[0] 9 $TEXT $false 'l' | Out-Null; $lx += 11 + 9 + ($p[0].Length * 4.6) }
# columns aligned with the strip below
$labW = 120; $colW = 82; $cx0 = 46 + $labW
$yBase = 330; $kk = 155 / 1400.0
# focus band behind AP27
Rect $s ($cx0 + 3 * $colW) 156 $colW 335 $TINT | Out-Null
for ($i = 0; $i -lt 5; $i++) {
  $scn = $SC[$i]; $c = $cx0 + $colW * ($i + 0.5); $bw = 40; $bx = $c - $bw / 2
  $v = $sk.$scn; $y = $yBase
  foreach ($bu in @('Food', 'Starch', 'HVA')) {
    $h = [double]$v.$bu * $kk; $y -= $h
    $r = Rect $s $bx $y $bw $h $BUCOL[$bu]
    if ($scn -eq 'AP28') { $r.Fill.Transparency = [single]0.35 }
    if ($h -ge 9.5) { T $s $bx ($y + $h / 2 - 6) $bw 12 (N0 $v.$bu) 8.5 $(if ($bu -eq 'HVA') { $NAVY } else { $WHITE }) $true 'c' | Out-Null }
  }
  $oth = [double]$v.Other
  if ($oth -lt 0) { $r = Rect $s $bx $yBase $bw ([Math]::Max(1, -$oth * $kk)) $GREY; if ($scn -eq 'AP28') { $r.Fill.Transparency = [single]0.35 } }
  T $s ($c - 38) ($y - 16) 76 14 (N0 $v.Total) 11 $NAVY $true 'c' | Out-Null
}
# growth pill over AP27
$pill = $s.Shapes.AddShape(9, [single]($cx0 + 3 * $colW + 6), [single]160, [single]($colW - 12), [single]18)
$pill.Fill.Visible = 0; $pill.Line.ForeColor.RGB = $NAVY; $pill.Line.Weight = [single]0.75
$pill.TextFrame.TextRange.Text = ('+' + ('{0:N0}' -f (($opba27/$opba26-1)*100)) + '% vs LE'); $pill.TextFrame.TextRange.Font.Size = [single]8.5; $pill.TextFrame.TextRange.Font.Name = $FONT; $pill.TextFrame.TextRange.Font.Color.RGB = $NAVY; $pill.TextFrame.TextRange.Font.Bold = -1
$pill.TextFrame.MarginLeft = [single]0; $pill.TextFrame.MarginRight = [single]0; $pill.TextFrame.MarginTop = [single]0; $pill.TextFrame.MarginBottom = [single]0

# strip
$rows = @()
$rows += @{ cells = @('') + ($SC | ForEach-Object { $SCL[$_] }); bold = $true; color = $NAVY; line = $true; h = 20 }
$rows += @{ cells = @('Volume (kt)') + ($SC | ForEach-Object { '{0:N0}' -f [double]$st.$_.vol }); line = $true }
$rows += @{ cells = @('Net sales (MB)') + ($SC | ForEach-Object { '{0:N0}' -f [double]$st.$_.ns }); line = $true }
$rows += @{ cells = @('Gross profit (MB)') + ($SC | ForEach-Object { '{0:N0}' -f [double]$st.$_.gp }); line = $true }
$rows += @{ cells = @('  %GM') + ($SC | ForEach-Object { '({0:N1}%)' -f ([double]$st.$_.gm * 100) }); line = $true; color = $MUTED; italic = $true }
$rows += @{ cells = @('OPBA (MB)') + ($SC | ForEach-Object { '{0:N0}' -f [double]$st.$_.opba }); line = $true; bold = $true; color = $NAVY }
$rows += @{ cells = @('Net profit (MB)') + ($SC | ForEach-Object { '{0:N0}' -f [double]$st.$_.np }); line = $true; bold = $true; color = $NAVY }
Grid $s 46 352 @($labW, $colW, $colW, $colW, $colW, $colW) 19 $rows $null | Out-Null
T $s 46 488 510 12 ('2028 AP shaded lighter = direction only.  Other = NBG + Waxy + Corp/BU eliminations (below the axis when negative).') 8 $MUTED $false 'l' | Out-Null

# right card: what AP2027 commits to
Card $s 590 88 340 300 | Out-Null
Kicker $s 606 100 300 'WHAT AP2027 COMMITS TO' | Out-Null
$b27 = $D.bridge27
$food27 = [double]$sk.AP27.Food; $shareFood = $food27 / ($food27 + [double]$sk.AP27.Starch + [double]$sk.AP27.HVA)
$items = @(
  @(('+' + ('{0:N0}' -f ($opba27 - $opba26))), 'OPBA vs 2026 LE: ', 'every BU grows; Starch, HVA and Food each add ~60 MB'),
  @(('{0:N0}%' -f ($shareFood * 100)), 'of BU OPBA from Food: ', 'still the profit anchor, Well Grow adds a full year'),
  @(('+{0:N0}%' -f (([double]$st.AP27.vol/[double]$st.LE26.vol-1)*100)), 'volume, GM flat: ', ('{0:N1}% vs {1:N1}%, growth is volume-led, not margin-led' -f ([double]$st.AP27.gm*100), ([double]$st.LE26.gm*100))),
  @((SG ($opba27 - [double]$st.AP26.opba)), 'vs AP2026 plan: ', ('AP27 OPBA is still below last year''s plan of {0:N0} MB' -f [double]$st.AP26.opba))
)
$yy = 122
foreach ($it in $items) {
  T $s 606 $yy 92 30 $it[0] 21 $BLUE $true 'l' | Out-Null
  TR $s 700 ($yy + 1) 218 44 @(@($it[1], $true, $NAVY), @($it[2], $false, $TEXT)) 10.5 | Out-Null
  if ($it -ne $items[-1]) { L $s 606 ($yy + 58) 918 ($yy + 58) $LINE 0.5 $false | Out-Null }
  $yy += 64
}
# right card: AP2028 direction
Card $s 590 400 340 108 | Out-Null
Kicker $s 606 412 300 'AP2028 DIRECTION' | Out-Null
T $s 606 430 92 30 ('{0:N0}' -f [double]$st.AP28.opba) 21 $BLUE $true 'l' | Out-Null
TR $s 700 431 218 70 @(@('OPBA, +', $true, $NAVY), @(('{0:N0} MB vs AP27 ' -f ([double]$st.AP28.opba - $opba27)), $true, $NAVY), @(('led by TDC 2.0 ramp-up; net profit {0:N0} MB' -f [double]$st.AP28.np), $false, $TEXT)) 10.5 | Out-Null

# ================= 3. OPBA bridge LE26 -> AP27 by BU =================
$steps = @(); foreach ($p in $b27.steps) { $steps += ,@($p[0], [double]$p[1]) }
$s = Page ('TWPC ' + $DOT + ' AP2027 OPBA BRIDGE BY BU') ('Starch, HVA and Food each add ~60 MB; NBG moves close to break-even') $SRC
Card $s 30 88 560 420 | Out-Null
T $s 46 100 520 18 'OPBA, 2026 LE to 2027 AP (MB)' 14 $NAVY $true 'l' | Out-Null
$cx = Waterfall $s 46 140 330 528 '2026 LE' ([double]$b27.start) $steps '2027 AP' ([double]$b27.end) 1150 $BLUE
# data strip aligned under the bars
$e = $D.entity_opba
function Ent($lab) { foreach ($r in $D.entity_opba) { if ($r.label -eq $lab) { return $r } }; return $null }
$buRows = @('Starch BU', 'HVA BU (excl. Waxy)', 'Food BU', 'NBG BU', 'Waxy', 'Corp / Elim')
$slot = 528 / 8.0
$yS = 366
T $s 46 $yS 120 14 '' 9 $TEXT $false 'l' | Out-Null
$lines = @(@('2026 LE', 'LE26'), @('2027 AP', 'AP27'), @('Growth', 'g'))
$ly = $yS
foreach ($ln in $lines) {
  for ($i = 0; $i -lt 8; $i++) {
    $c = $cx[$i]
    if ($i -eq 0) { $v = $(if ($ln[1] -eq 'LE26') { N0 $b27.start } elseif ($ln[1] -eq 'g') { '' } else { '' }) }
    elseif ($i -eq 7) { $v = $(if ($ln[1] -eq 'AP27') { N0 $b27.end } elseif ($ln[1] -eq 'g') { GR $b27.start $b27.end } else { '' }) }
    else { $r = Ent $buRows[$i - 1]; $v = $(if ($ln[1] -eq 'g') { if ($i -eq 6) { 'n.m.' } else { GR $r.LE26 $r.AP27 } } else { N0 $r.($ln[1]) }) }
    $col = $(if ($ln[1] -eq 'g') { $MUTED } else { $TEXT })
    T $s ($c - $slot / 2) $ly $slot 14 $v 9.5 $col ($i -eq 0 -or $i -eq 7) 'c' | Out-Null
  }
  $ly += 17
}
T $s 46 ($yS - 4) 40 0 '' 8 $MUTED $false 'l' | Out-Null
L $s 46 ($yS - 4) 574 ($yS - 4) $LINE 0.5 $false | Out-Null
TR $s 46 ($yS + 52) 520 12 @(@('Rows: OPBA 2026 LE / 2027 AP / growth by BU (MB). ', $false, $MUTED)) 8 | Out-Null
$up = 0.0; foreach ($p in $b27.steps) { if ([double]$p[1] -gt 0) { $up += [double]$p[1] } }
Note $s 46 440 528 56 @(@('Broad-based plan: ', $true, $NAVY), @(('Starch +{0:N0}, HVA +{1:N0} and Food +{2:N0} MB together make up {3:N0}% of the +{4:N0} MB uplift; Corp and BU eliminations take back {5:N0} MB.' -f [double]$b27.steps[0][1], [double]$b27.steps[1][1], [double]$b27.steps[2][1], ((([double]$b27.steps[0][1] + [double]$b27.steps[1][1] + [double]$b27.steps[2][1]) / ($opba27 - $opba26)) * 100), ($opba27 - $opba26), (-[double]$b27.steps[5][1])), $false, $TEXT))
# right card: what drives each BU
Card $s 605 88 325 420 | Out-Null
Kicker $s 621 100 300 ('WHAT DRIVES EACH BU ' + $DOT + ' ' + [char]0x0394 + ' OPBA VS 2026 LE') | Out-Null
function D27($lab) { $r = Ent $lab; return [double]$r.AP27 - [double]$r.LE26 }
$drv = @(
  @('Starch', (D27 'Starch BU'), @(@('Cambodia (TWIC)', (D27 'Cambodia (TWIC)')), @('Starch TH', (D27 'Starch TH')), @('China', (D27 'China (TWIT+TWFZ)')), @('Vietnam', (D27 'Vietnam (TNT+VTC)')))),
  @('HVA', (D27 'HVA BU (excl. Waxy)'), @(@('TDC', (D27 'TDC')), @('TDC 2.0 (first year)', (D27 'TDC 2.0')), @('TWIN', (D27 'TWIN')), @('TWII', (D27 'TWII')))),
  @('Food', (D27 'Food BU'), @(@('Well Grow (full year)', (D27 'Well Grow')), @('Food TH', (D27 'Food TH')), @('Food VN', (D27 'Food VN')))),
  @('NBG', (D27 'NBG BU'), @(@(('Bioplastic ' + (N0 (Ent 'NBG BU').LE26) + ' ' + $ARROW + ' ' + (N0 (Ent 'NBG BU').AP27)), $null))),
  @('Corp / Elim', (D27 'Corp / Elim'), @(@('Corp cost and BU eliminations', $null)))
)
$yy = 122
foreach ($dv in $drv) {
  T $s 621 $yy 200 16 $dv[0] 12 $NAVY $true 'l' | Out-Null
  T $s 840 $yy 74 16 (SG $dv[1]) 12 (DCol $dv[1]) $true 'r' | Out-Null
  $yy += 18
  $subs = $dv[2]; if ($subs.Count -gt 0 -and -not ($subs[0] -is [array])) { $subs = ,$subs }
  foreach ($sub in $subs) {
    T $s 633 $yy 200 13 $sub[0] 10 $TEXT $false 'l' | Out-Null
    if ($null -ne $sub[1]) { T $s 840 $yy 74 13 (SG $sub[1]) 10 (DCol $sub[1]) $false 'r' | Out-Null }
    $yy += 14
  }
  $yy += 8
  if ($dv -ne $drv[-1]) { L $s 621 ($yy - 5) 914 ($yy - 5) $LINE 0.5 $false | Out-Null }
}

# ================= 4. BU / entity table =================
$s = Page ('TWPC ' + $DOT + ' OPBA BY BU AND ENTITY') ('TWIC, TDC, TDC 2.0 and Well Grow carry most of the AP2027 uplift') $SRC
Card $s 30 88 640 420 | Out-Null
$wd = @(150, 58, 58, 58, 64, 58, 68, 68)
Rect $s (46 + 150 + 58 * 3) 98 64 362 $TINT | Out-Null
$rows = @(@{ cells = @('OPBA (MB)', '2025', 'AP2026', '2026 LE', '2027 AP', '2028 AP', ([string][char]0x0394 + ' vs LE'), ([string][char]0x0394 + ' vs AP26')); bold = $true; color = $NAVY; line = $true; h = 22; size = 9.5 })
foreach ($r in $D.entity_opba) {
  $d1 = [double]$r.AP27 - [double]$r.LE26; $d2 = [double]$r.AP27 - [double]$r.AP26
  $row = @{ cells = @($r.label, (N0 $r.'2025'), (N0 $r.AP26), (N0 $r.LE26), (N0 $r.AP27), (N0 $r.AP28), (SG $d1), (SG $d2)); colors = @($null, $null, $null, $null, $NAVY, $MUTED, (DCol $d1), (DCol $d2)); h = 18.5 }
  if ($r.lvl -eq 1) { $row.indent = 12; $row.size = 9.5 } else { $row.bold = $true; $row.line = $true }
  if ($r.lvl -eq -1) { $row.fill = $TINT; $row.color = $NAVY; $row.h = 21 }
  $rows += $row
}
Grid $s 46 98 $wd 18.5 $rows $null | Out-Null
# right callouts
Card $s 685 88 245 420 | Out-Null
Kicker $s 701 100 220 'THREE ENTITY STORIES' | Out-Null
function Cal($y, $big, $head, $body) { T $s 701 $y 214 28 $big 20 $BLUE $true 'l' | Out-Null; T $s 701 ($y + 28) 214 14 $head 11 $NAVY $true 'l' | Out-Null; T $s 701 ($y + 44) 214 60 $body 10 $TEXT $false 'l' | Out-Null }
$twic = Ent 'Cambodia (TWIC)'; $tdc2 = Ent 'TDC 2.0'; $wg = Ent 'Well Grow'; $tdc = Ent 'TDC'
Cal 122 ((N0 $twic.LE26) + ' ' + $ARROW + ' ' + (N0 $twic.AP27)) 'TWIC turns positive' ('Cambodia swings +' + ('{0:N0}' -f ([double]$twic.AP27 - [double]$twic.LE26)) + ' MB to the largest Starch gain; AP28 ' + (N0 $twic.AP28) + ' MB.')
L $s 701 222 914 222 $LINE 0.5 $false | Out-Null
Cal 232 ((N0 $tdc2.AP27) + ' ' + $ARROW + ' ' + (N0 $tdc2.AP28)) 'TDC 2.0 starts, then scales' ('First-year OPBA ' + (N0 $tdc2.AP27) + ' MB; becomes the biggest single uplift in AP28. Legacy TDC ' + (N0 $tdc.AP27) + ' ' + $ARROW + ' ' + (N0 $tdc.AP28) + ' MB as volume moves across.')
L $s 701 340 914 340 $LINE 0.5 $false | Out-Null
Cal 350 ('+' + ('{0:N0}' -f ([double]$wg.AP27 - [double]$wg.LE26))) 'Well Grow full year' ('Well Grow OPBA ' + (N0 $wg.LE26) + ' MB (Sep-Dec 2026) ' + $ARROW + ' ' + (N0 $wg.AP27) + ' MB in 2027: more than half of the Food BU uplift.')

# ================= 5. OPBA to NP =================
$nb = $D.np_bridge; $nsteps = @(); foreach ($p in $nb.steps) { $nsteps += ,@($p[0], [double]$p[1]) }
$oo = $D.oneoff.LE26
$s = Page ('TWPC ' + $DOT + ' FROM OPBA TO NET PROFIT') ('OPBA +' + ('{0:N0}' -f [double]$nb.steps[0][1]) + ' MB but NP +' + ('{0:N0}' -f ([double]$nb.end - [double]$nb.start)) + ' MB: 2026 one-offs and TDC 2.0 costs absorb it') $SRC
Card $s 30 88 560 420 | Out-Null
T $s 46 100 520 18 'Net profit, 2026 LE to 2027 AP (MB)' 14 $NAVY $true 'l' | Out-Null
$nsteps[0][0] = 'OPBA'; $nsteps[1][0] = 'Admin'; $nsteps[2][0] = '2026 other inc. & FX gain'; $nsteps[3][0] = 'Finance cost'; $nsteps[4][0] = 'CIT'; $nsteps[5][0] = 'MI & other'
$cx = Waterfall $s 46 150 360 528 '2026 LE NP' ([double]$nb.start) $nsteps '2027 AP NP' ([double]$nb.end) 430 $BLUE
$adm2 = [double]$D.admin_tdc2.AP27 - [double]$D.admin_tdc2.LE26
T $s ($cx[2] - 33) 392 66 26 ('TDC 2.0 ' + (SG $adm2)) 8.5 $MUTED $false 'c' | Out-Null
T $s ($cx[3] - 33) 392 66 26 ('FX ' + (N0 $oo.fx) + ', other ' + (N0 $oo.other_inc)) 8.5 $MUTED $false 'c' | Out-Null
$lfl = ([double]$nb.end - [double]$nb.start) - [double]$nb.steps[2][1]
Note $s 46 430 528 66 @(@(('Like-for-like NP grows about +' + ('{0:N0}' -f $lfl) + ' MB: '), $true, $NAVY), @(('2026 LE carries {0:N0} MB of FX gain and other operating income that AP27 does not plan. Of the +{1:N0} MB admin, TDC 2.0 is {2:N0} MB.' -f ([double]$oo.fx + [double]$oo.other_inc + [double]$oo.nonop), (-[double]$nb.steps[1][1]), (-$adm2)), $false, $TEXT))
# below-OPBA lines at group level (BU scorecards stop at OPBA)
Card $s 605 88 325 420 | Out-Null
Kicker $s 621 100 300 'BELOW OPBA, GROUP LEVEL (MB)' | Out-Null
$rows = @(@{ cells = @('', '2026 LE', '2027 AP', [string][char]0x0394); bold = $true; color = $NAVY; line = $true; h = 20 })
foreach ($ln in @('OPBA', 'Admin', 'Other income & FX', 'Finance cost', 'CIT', 'MI & other', 'Net profit')) {
  $a = [double]$D.below.LE26.$ln; $b = [double]$D.below.AP27.$ln
  $row = @{ cells = @($ln, (N0 $a), (N0 $b), (SG ($b - $a))); colors = @($null, $null, $NAVY, (DCol ($b - $a))); line = $true; h = 19 }
  if ($ln -eq 'OPBA' -or $ln -eq 'Net profit') { $row.bold = $true; $row.fill = $TINT; $row.color = $NAVY }
  $rows += $row
}
$yy = Grid $s 621 120 @(118, 62, 62, 52) 19 $rows $null
function Cal2($y, $big, $head, $body) { T $s 621 $y 90 24 $big 18 $BLUE $true 'l' | Out-Null; T $s 712 ($y + 2) 202 14 $head 10.5 $NAVY $true 'l' | Out-Null; T $s 712 ($y + 17) 202 44 $body 9.5 $TEXT $false 'l' | Out-Null }
$sth = Ent 'Starch TH'
Cal2 ($yy + 18) (SG $adm2) 'TDC 2.0 overhead' ('Admin for TDC 2.0 rises from ' + (N0 (-[double]$D.admin_tdc2.LE26)) + ' to ' + (N0 (-[double]$D.admin_tdc2.AP27)) + ' MB in its first operating year; the rest of the group holds admin broadly flat.')
L $s 621 ($yy + 80) 914 ($yy + 80) $LINE 0.5 $false | Out-Null
Cal2 ($yy + 92) (N0 ([double]$oo.fx + [double]$oo.other_inc + [double]$oo.nonop)) 'Not repeated in AP27' ('2026 LE includes FX gain ' + (N0 $oo.fx) + ', other operating income ' + (N0 $oo.other_inc) + ' and non-operating ' + (N0 $oo.nonop) + ' MB; AP27 plans none of these.')

# ================= 6. AP2028 direction =================
$b28 = $D.bridge28; $steps = @(); foreach ($p in $b28.steps) { $steps += ,@($p[0], [double]$p[1]) }
$s = Page ('TWPC ' + $DOT + ' AP2028 DIRECTION') ('AP2028 direction: OPBA ' + ('{0:N0}' -f [double]$b28.end) + ' MB, with TDC 2.0 as the next growth engine') $SRC
Card $s 30 88 560 420 | Out-Null
T $s 46 100 520 18 'OPBA, 2027 AP to 2028 AP (MB)' 14 $NAVY $true 'l' | Out-Null
$cx = Waterfall $s 46 140 350 528 '2027 AP' ([double]$b28.start) $steps '2028 AP' ([double]$b28.end) 1450 $BLUE
$tdcD = [double]$tdc.AP28 - [double]$tdc.AP27; $tdc2D = [double]$tdc2.AP28 - [double]$tdc2.AP27
T $s ($cx[2] - 36) 380 72 26 ('TDC 2.0 ' + (SG $tdc2D) + "`r" + 'TDC ' + (SG $tdcD)) 8.5 $MUTED $false 'c' | Out-Null
$f28 = Ent 'Food BU'
T $s ($cx[3] - 36) 380 72 26 ('Food TH ' + (SG ([double](Ent 'Food TH').AP28 - [double](Ent 'Food TH').AP27)) + "`r" + 'Food VN ' + (SG ([double](Ent 'Food VN').AP28 - [double](Ent 'Food VN').AP27))) 8.5 $MUTED $false 'c' | Out-Null
$st28 = Ent 'Starch BU'
T $s ($cx[1] - 36) 380 72 26 ('TWIC ' + (SG ([double]$twic.AP28 - [double]$twic.AP27)) + "`r" + 'Starch TH ' + (SG ([double]$sth.AP28 - [double]$sth.AP27))) 8.5 $MUTED $false 'c' | Out-Null
Note $s 46 430 528 66 @(@('Direction, not a commitment: ', $true, $NAVY), @(('{0:N0}% of the +{1:N0} MB comes from HVA, and within it TDC 2.0 adds {2} MB while legacy TDC gives back {3} MB. AP28 therefore depends on the TDC 2.0 volume ramp.' -f (([double]$b28.steps[1][1] / ([double]$b28.end - [double]$b28.start)) * 100), ([double]$b28.end - [double]$b28.start), (SG $tdc2D), (N0 (-$tdcD))), $false, $TEXT))
# mix card
Card $s 605 88 325 420 | Out-Null
Kicker $s 621 100 300 'OPBA MIX ACROSS THE THREE CORE BUs' | Out-Null
$yy = 128
foreach ($scn in @('LE26', 'AP27', 'AP28')) {
  $v = $sk.$scn; $tot = [double]$v.Food + [double]$v.Starch + [double]$v.HVA
  T $s 621 $yy 80 14 $SCL[$scn] 10.5 $NAVY $true 'l' | Out-Null
  T $s 840 $yy 74 14 ((N0 $tot) + ' MB') 9.5 $MUTED $false 'r' | Out-Null
  $x = 621; $barW = 293
  foreach ($bu in @('Food', 'Starch', 'HVA')) {
    $w = $barW * [double]$v.$bu / $tot; Rect $s $x ($yy + 18) $w 22 $BUCOL[$bu] | Out-Null
    T $s $x ($yy + 22) $w 14 ('{0:N0}%' -f ([double]$v.$bu / $tot * 100)) 9.5 $(if ($bu -eq 'HVA') { $NAVY } else { $WHITE }) $true 'c' | Out-Null
    $x += $w
  }
  $yy += 62
}
$lx = 621; foreach ($p in @(@('Food', $BLUE), @('Starch', $MID), @('HVA', $LIGHT))) { Rect $s $lx ($yy - 6) 8 8 $p[1] | Out-Null; T $s ($lx + 11) ($yy - 8) 60 12 $p[0] 9 $TEXT $false 'l' | Out-Null; $lx += 70 }
L $s 621 ($yy + 14) 914 ($yy + 14) $LINE 0.5 $false | Out-Null
T $s 621 ($yy + 24) 100 30 ('{0:N0}' -f [double]$st.AP28.np) 21 $BLUE $true 'l' | Out-Null
TR $s 712 ($yy + 26) 202 70 @(@(('Net profit AP28, +{0:N0} MB vs AP27. ' -f ([double]$st.AP28.np - $np27)), $true, $NAVY), @(('Corp/Elim NP ({0:N0}) MB includes a ({1:N0}) MB net non-operating item at group level.' -f (-[double]$D.np_bu.AP28.'Corp / Elim'), (-[double]$D.oneoff.AP28.nonop)), $false, $TEXT)) 9.5 | Out-Null
T $s 621 ($yy + 100) 293 30 'Share = BU OPBA / (Food + Starch + HVA). NBG, Waxy and Corp/Elim excluded.' 8 $MUTED $false 'l' | Out-Null

# ================= 7. Points for discussion =================
$s = Page ('TWPC ' + $DOT + ' FOR CEO DISCUSSION') 'Four points to settle before AP2027 is locked' 'FP&A view based on the consolidated BU OPBA. Source as previous pages.'
Card $s 30 88 900 420 | Out-Null
Kicker $s 46 100 400 'WHERE THE PLAN IS EXPOSED (OPBA, MB)' | Out-Null
$foodTH = Ent 'Food TH'; $vs = $D.vol_sth
$pts = @(
  @((SG ($opba27 - [double]$st.AP26.opba)), 'Ambition level vs AP2026', ('AP27 OPBA {0:N0} MB is still below the AP2026 plan of {1:N0} MB, although it is +{2:N0}% on 2026 LE and +{3:N0}% on 2025 actual ({4:N0}).' -f $opba27, [double]$st.AP26.opba, (($opba27/$opba26-1)*100), (($opba27/[double]$st.'2025'.opba-1)*100), [double]$st.'2025'.opba)),
  @(('{0:N0}%' -f ($shareFood * 100)), 'Concentration on Food', ('Food is {0:N0}% of core-BU OPBA. Of Food''s {1} MB uplift, Well Grow (full year) brings {2}; Food TH itself grows {3} MB.' -f ($shareFood * 100), (SG ([double]$b27.steps[2][1])), (SG ([double]$wg.AP27 - [double]$wg.LE26)), (SG ([double]$foodTH.AP27 - [double]$foodTH.LE26)))),
  @((SG ([double]$tdc.AP27 - [double]$tdc.LE26)), 'TDC recovery on flat volume', (('TDC OPBA {0} ' -f (N0 $tdc.LE26)) + $ARROW + (' {0} MB with volume ~44 kt in both years: the uplift has to come from price, mix and cost.' -f (N0 $tdc.AP27)))),
  @((SG ([double]$sth.AP27 - [double]$sth.LE26)), 'Starch TH: volume up, OPBA lags', (('Starch TH volume {0:N0} ' -f [double]$vs.LE26) + $ARROW + (' {0:N0} kt (+{1:N0}%), yet OPBA only {2} ' -f [double]$vs.AP27, (([double]$vs.AP27/[double]$vs.LE26-1)*100), (N0 $sth.LE26)) + $ARROW + (' {0} MB; the AP2026 plan was {1} MB.' -f (N0 $sth.AP27), (N0 $sth.AP26))))
)
$yy = 126
foreach ($p in $pts) {
  T $s 46 $yy 130 28 $p[0] 22 $BLUE $true 'l' | Out-Null
  T $s 190 ($yy + 1) 720 15 $p[1] 12 $NAVY $true 'l' | Out-Null
  T $s 190 ($yy + 20) 720 40 $p[2] 11 $TEXT $false 'l' | Out-Null
  $yy += 92
  if ($p -ne $pts[-1]) { L $s 46 ($yy - 16) 914 ($yy - 16) $LINE 0.5 $false | Out-Null }
}

# ================= 8-9. Appendix P&L by BU =================
function PLPage($scn, $title, $kickText) {
  $s = Page $kickText $title $SRC
  Card $s 30 88 900 420 | Out-Null
  $cols = @($D.pl_cols)
  $wd = @(190) + (@(96) * 7)
  $hdr = @{ cells = @('MB') + $cols; bold = $true; color = $NAVY; line = $true; h = 22 }
  $rows = @($hdr)
  foreach ($r in $D.pl.$scn) {
    $isPct = $r.label.StartsWith('%'); $isKey = @('Net sales', 'Gross profit', 'OP before admin', 'Operating profit', 'Net profit') -contains $r.label
    $cells = @($(if ($isPct) { '  ' + $r.label } else { $r.label }))
    for ($c = 0; $c -lt $cols.Count; $c++) {
      $v = $r.vals[$c]
      if ($isPct) { $cells += $(if ($c -eq 5) { '' } else { PC $v }) }
      elseif ($r.label -like 'Volume*') { $cells += $(if ($null -eq $v) { '' } else { N1 $v }) }
      else { $cells += (N0 $v) }
    }
    $row = @{ cells = $cells; h = 19.5; line = $isKey -or $r.label -like 'Volume*' -or $isPct }
    if ($isKey) { $row.bold = $true; $row.color = $NAVY }
    if ($isPct) { $row.color = $MUTED; $row.italic = $true }
    if ($r.label -eq 'OP before admin' -or $r.label -eq 'Net profit') { $row.fill = $TINT }
    $rows += $row
  }
  Grid $s 46 98 $wd 19.5 $rows $null | Out-Null
  T $s 46 494 860 12 'Corp / Elim = TWPC minus the five BUs (corporate items and inter-BU eliminations). Volume not meaningful for Corp / Elim. n.m. = not meaningful.' 8 $MUTED $false 'l' | Out-Null
}
PLPage 'LE26' 'Appendix: 2026 LE (9+3) consolidated P&L by BU (base year)' ('APPENDIX ' + $DOT + ' 2026 LE P&L')
PLPage 'AP27' 'Appendix: AP2027 consolidated P&L by BU' ('APPENDIX ' + $DOT + ' AP2027 P&L')
PLPage 'AP28' 'Appendix: AP2028 consolidated P&L by BU (direction)' ('APPENDIX ' + $DOT + ' AP2028 P&L')

$pres.SaveAs($Out)
if ($PngDir) { New-Item -ItemType Directory -Force $PngDir | Out-Null; for ($i = 1; $i -le $pres.Slides.Count; $i++) { $pres.Slides.Item($i).Export((Join-Path $PngDir ('s{0:D2}.png' -f $i)), 'PNG', 1600, 900) } }
$pres.Close()
if (-not $wasRunning) { $app.Quit() }
Write-Output ('saved ' + $Out)





