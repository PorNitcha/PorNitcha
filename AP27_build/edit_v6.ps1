param([string]$SourceDeck, [string]$OutDeck, [string]$PngDir, [string]$BridgeJson)
# v6 = copy of v5; slide 6 right card becomes the Thai admin bridge table (P-Cost | Non-P | Admin TH) with the p.7-8 (Waterfall_TH) numbers
$ErrorActionPreference = 'Stop'
function RGB($hex) { $r = [Convert]::ToInt32($hex.Substring(0,2),16); $g = [Convert]::ToInt32($hex.Substring(2,2),16); $b = [Convert]::ToInt32($hex.Substring(4,2),16); return $r + $g*256 + $b*65536 }
$NAVY = RGB '19226d'; $TEXT = RGB '333f50'; $TINT = RGB 'e6f5fb'; $LINE = RGB 'd9dee7'; $KICK = RGB '0089c0'; $MUTED = RGB '7f8a9a'
function RoundAway($v) { return [Math]::Round([double]$v, 0, [MidpointRounding]::AwayFromZero) }
function F0($x) { return ('{0:N0}' -f (RoundAway $x)) }
function SG0($x) { $q = RoundAway $x; if ($q -eq 0) { return '0' }; if ($q -gt 0) { return ('+{0:N0}' -f $q) }; return ('({0:N0})' -f (-$q)) }
$BR = Get-Content -LiteralPath $BridgeJson -Encoding UTF8 -Raw | ConvertFrom-Json
$P = $BR.P; $N = $BR.N
$pNR26 = [double]$P.'Rev Bonus 2025' + [double]$P.'Wellgrow Base' + [double]$P.'Special Incentive'
$nNR26 = [double]$N.'Impairment' + [double]$N.'TDC 2.0 Pre-Operating' + [double]$N.'Wellgrow Base' + [double]$N.'TTDI Loyalty 2025'
$pInc = [double]$P.'Salary' + [double]$P.'Medical care' + [double]$P.'Other Welfare' + [double]$P.'Staff recruitment' + [double]$P.'Trainning' + [double]$P.'Other'
$nInc = [double]$N.'Consult Fee' + [double]$N.'Admin' + [double]$N.'IT' + [double]$N.'Other'
$pNR27 = [double]$P.'Wellgrow'
$nNR27 = [double]$N.'Impairment TDC RY (MS1)' + [double]$N.'TDC2.0 pre-operating' + [double]$N.'Wellgrow'
# rows: label, P, N, kind (total | step)
$rows = @(
  @('2026 Reported', [double]$P.'LE 2026', [double]$N.'LE 2026', 'total'),
  @('non-recurring items', $pNR26, $nNR26, 'step'),
  @('2026 Baseline', [double]$P.'2026 Underlying', [double]$N.'2026 Underlying', 'total'),
  @('Baseline incremental', $pInc, $nInc, 'step'),
  @('2027 Baseline', [double]$P.'AP 2027 Base', [double]$N.'AP 2027 Base', 'total'),
  @('non-recurring items', $pNR27, $nNR27, 'step'),
  @('AP2027', [double]$P.'AP 2027 Reporting', [double]$N.'AP 2027 Reporting', 'total'),
  @('Saving', [double]$P.'Saving', [double]$N.'Saving', 'step'),
  @('AP2027 Stretching', [double]$P.'AP 2027 Strech', [double]$N.'AP 2027 Strech', 'total'))
# tie checks against the sheet
if ([Math]::Abs($rows[0][1] + $rows[1][1] - $rows[2][1]) -gt 0.05) { throw 'P 2026 bridge does not tie' }
if ([Math]::Abs($rows[2][1] + $rows[3][1] - $rows[4][1]) -gt 0.05) { throw 'P 2027 base does not tie' }
if ([Math]::Abs($rows[4][1] + $rows[5][1] - $rows[6][1]) -gt 0.05) { throw 'P reporting does not tie' }
if ([Math]::Abs($rows[0][2] + $rows[1][2] - $rows[2][2]) -gt 0.05) { throw 'N 2026 bridge does not tie' }
if ([Math]::Abs($rows[2][2] + $rows[3][2] - $rows[4][2]) -gt 0.05) { throw 'N 2027 base does not tie' }
if ([Math]::Abs($rows[4][2] + $rows[5][2] - $rows[6][2]) -gt 0.05) { throw 'N reporting does not tie' }
if ([Math]::Abs($rows[8][1] + $rows[8][2] - [double]$BR.TOT.'AP 2027 Strech') -gt 0.05) { throw 'TH stretch does not tie to TOT' }

Copy-Item -LiteralPath $SourceDeck -Destination $OutDeck -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($OutDeck, 0, 0, 0)
try {
  $s = $pres.Slides.Item(6)
  # ---- clear the right card content (keep card rect idx 87, kicker idx 88, footnote idx 90)
  $kicker = $null; $note = $null; $foot = $null; $toDelete = @()
  for ($i = 1; $i -le $s.Shapes.Count; $i++) {
    $sh = $s.Shapes.Item($i)
    if ($sh.Type -eq 14 -or $sh.Left -lt 640) { continue }
    if ($sh.Type -eq 1 -and $sh.Width -gt 250 -and $sh.Height -gt 300) { continue }   # the card itself
    $t = $(if ($sh.HasTextFrame -eq -1) { $sh.TextFrame.TextRange.Text } else { '' })
    if ($t -like 'WHAT MOVES ADMIN*') { $kicker = $sh; continue }
    if ($t -like 'MB; + = higher cost*') { $note = $sh; continue }
    if ($t -like 'International = TWIT*') { $foot = $sh; continue }
    $toDelete += $sh
  }
  if (-not $kicker -or -not $note -or -not $foot) { throw 'slide 6 right card: expected shapes not found' }
  foreach ($sh in $toDelete) { $sh.Delete() }
  "deleted $($toDelete.Count) shapes from the right card"
  $kicker.TextFrame.TextRange.Text = 'ADMIN THAILAND BRIDGE ' + [string][char]0x00B7 + ' LE 2026 TO AP 2027'
  $note.TextFrame.TextRange.Text = 'MB, whole numbers; per Waterfall_TH, same figures as p.7 (P-Cost) and p.8 (Non-P); Admin TH = P-Cost + Non-P'
  $note.Height = [single]22
  # ---- table
  $x0 = 646.0; $wLab = 118.0; $cols = @(766.0, 816.0, 866.0); $wc = 48.0
  $y = 128.0; $hh = 14.0; $rh = 15.6
  function TB($slide, $l, $t, $w, $h, $txt, $size, $color, $bold, $align) {
    $b = $slide.Shapes.AddTextbox(1, [single]$l, [single]$t, [single]$w, [single]$h)
    $tf = $b.TextFrame; $tf.AutoSize = 0; $tf.WordWrap = -1; $tf.MarginLeft = 2; $tf.MarginRight = 2; $tf.MarginTop = 0; $tf.MarginBottom = 0; $tf.VerticalAnchor = 3
    $tr = $tf.TextRange; $tr.Text = $txt; $tr.Font.Name = 'Aptos'; $tr.Font.Size = [single]$size; $tr.Font.Bold = [int]$bold; $tr.Font.Color.RGB = [int]$color; $tr.ParagraphFormat.Alignment = [int]$align
    $b.Left = [single]$l; $b.Top = [single]$t; $b.Width = [single]$w; $b.Height = [single]$h
    return $b
  }
  function LN($slide, $x1, $y1, $x2, $y2, $color) { $l = $slide.Shapes.AddLine([single]$x1, [single]$y1, [single]$x2, [single]$y2); $l.Line.ForeColor.RGB = [int]$color; $l.Line.Weight = [single]0.5; return $l }
  # header
  TB $s $x0 $y $wLab $hh 'MB' 8.5 $NAVY -1 1 | Out-Null
  $hdrs = @('P-Cost', 'Non-P', 'Admin TH')
  for ($c = 0; $c -lt 3; $c++) { TB $s $cols[$c] $y $wc $hh $hdrs[$c] 8.5 $NAVY -1 3 | Out-Null }
  $y += $hh; LN $s $x0 $y 914 $y $LINE | Out-Null
  foreach ($r in $rows) {
    $isTot = ($r[3] -eq 'total')
    if ($isTot) { $rc = $s.Shapes.AddShape(1, [single]$x0, [single]$y, [single](914 - $x0), [single]$rh); $rc.Fill.ForeColor.RGB = [int]$TINT; $rc.Line.Visible = 0; $rc.Fill.Solid() }
    $vals = @($r[1], $r[2], ($r[1] + $r[2]))
    $lblL = $(if ($isTot) { $x0 } else { $x0 + 8 })
    TB $s $lblL $y ($wLab - ($lblL - $x0)) $rh $r[0] 9 $(if ($isTot) { $NAVY } else { $TEXT }) $(if ($isTot) { -1 } else { 0 }) 1 | Out-Null
    for ($c = 0; $c -lt 3; $c++) {
      $txt = $(if ($isTot) { F0 $vals[$c] } else { SG0 $vals[$c] })
      TB $s $cols[$c] $y $wc $rh $txt 9 $(if ($isTot) { $NAVY } else { $TEXT }) $(if ($isTot) { -1 } else { 0 }) 3 | Out-Null
    }
    "{0,-22} {1,6} {2,6} {3,6}" -f $r[0], $(if ($isTot) { F0 $vals[0] } else { SG0 $vals[0] }), $(if ($isTot) { F0 $vals[1] } else { SG0 $vals[1] }), $(if ($isTot) { F0 $vals[2] } else { SG0 $vals[2] })
    $y += $rh
    if ($isTot) { LN $s $x0 $y 914 $y $LINE | Out-Null }
  }
  TB $s $x0 ($y + 6) 268 24 ('Non-recurring 2026 = bonus reversal, special incentive, impairment, TDC 2.0 pre-operating, TTDI loyalty, Well Grow base; 2027 = TDC Rayong MS1 write-off, TDC 2.0 pre-operating, Well Grow full year. Detail on p.7-8.') 7.5 $MUTED 0 1 | Out-Null
  $pres.Save()
  if ($PngDir) { New-Item -ItemType Directory -Force $PngDir | Out-Null; $s.Export((Join-Path $PngDir 's06.png'), 'PNG', 1600, 900) }
  "saved $OutDeck"
} finally { $pres.Close() }
