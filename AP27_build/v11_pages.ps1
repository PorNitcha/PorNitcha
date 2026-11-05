# ================= Admin P page and Admin Non-P page (slides 8-9): the Waterfall_TH sheet, item for item, made presentable =================
$BR = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'bridge.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$SH = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'sheets.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$BP = $BR.P; $BN = $BR.N
function SG1($x) { $q = [double]$x; if ([Math]::Abs($q) -lt 0.05) { return '0.0' }; if ($q -gt 0) { return ('+{0:N1}' -f $q) }; return ('({0:N1})' -f (-$q)) }
function F1($x) { return ('{0:N1}' -f [double]$x) }
$SRC89 = 'Source: BU Review_Admin.xlsx, sheet Waterfall_TH, reproduced item by item. Thailand = TWPC less International (TWIC is International). LE 2026 = FC 9+3; AP 2027 Reporting = AP2027 Board in the P&L. THB million, 1 decimal.'
$TOTC = RGB '2b3a8c'
$twicP = @{ LE26 = -[double]$SH.TWIC.'admin exp - People'.LE26; AP27 = -[double]$SH.TWIC.'admin exp - People'.AP27 }
$twicN = @{ LE26 = -[double]$SH.TWIC.'admin exp - Non-people'.LE26; AP27 = -[double]$SH.TWIC.'admin exp - Non-people'.AP27 }

# items: @(sheet label, display label with line breaks, value, kind) kind = total | step
function AdminPage($title, $sub, $items, $floor, $ceil, $recon) {
  $s = Page $title $SRC89
  Card $s 30 88 600 420 | Out-Null
  T $s 46 100 570 18 $sub 13 $NAVY $true 'l' | Out-Null
  Legend $s 46 121 @(@('Totals', $TOTC), @('Cost increase', $RED), @('Cost decrease', $GREEN))
  $n = $items.Count; $x0 = 46.0; $slot = 568.0 / $n; $bw = [Math]::Min(24, $slot * 0.66); $yTop = 150; $yBase = 400; $k = ($yBase - $yTop) / ($ceil - $floor)
  $run = 0.0; $i = 0
  foreach ($it in $items) {
    $cx = $x0 + $slot * ($i + 0.5); $bx = $cx - $bw / 2; $val = [double]$it[2]
    if ($it[3] -eq 'total') {
      $top = $yBase - ($val - $floor) * $k
      Rect $s $bx $top $bw ($yBase - $top) $TOTC | Out-Null
      Rect $s ($bx - 1) ($yBase - 8) ($bw + 2) 2.2 $WHITE | Out-Null
      T $s ($cx - 24) ($top - 13) 48 11 (F1 $val) 8.5 $NAVY $true 'c' | Out-Null
      $run = $val
    } else {
      $yR = $yBase - ($run - $floor) * $k
      L $s ($bx - $slot + $bw) $yR $bx $yR $MUTED 0.5 $true | Out-Null
      $yA = $yBase - (($run + [Math]::Max(0, $val)) - $floor) * $k; $h = [Math]::Max(1.5, [Math]::Abs($val) * $k)
      Rect $s $bx $yA $bw $h $(if ($val -ge 0) { $RED } else { $GREEN }) | Out-Null
      $ly = $(if ($val -ge 0) { $yA - 11 } else { $yA + $h + 1 })
      T $s ($cx - 24) $ly 48 10 (SG1 $val) 7.5 $(if ($val -ge 0) { $RED } else { $GREEN }) $true 'c' | Out-Null
      $run += $val
    }
    if ($i -lt $n - 1 -and $items[$i + 1][3] -eq 'total') { $yR = $yBase - ($run - $floor) * $k; L $s ($bx + $bw) $yR ($cx + $slot - $bw / 2) $yR $MUTED 0.5 $true | Out-Null }
    T $s ($cx - $slot / 2 - 3) ($yBase + 3) ($slot + 6) 34 $it[1] 7 $(if ($it[3] -eq 'total') { $NAVY } else { $TEXT }) ($it[3] -eq 'total') 'c' | Out-Null
    $i++
  }
  L $s $x0 $yBase ($x0 + $n * $slot) $yBase $LINE 0.75 $false | Out-Null
  T $s 46 ($yBase + 40) 570 22 ('Axis starts at ' + ('{0:N0}' -f $floor) + ' MB so the steps are visible. Items, order and values exactly as in Waterfall_TH; AP 2027 Stretch = Reporting after the saving programme.') 7.5 $MUTED $false 'l' | Out-Null
  # right card: the same bridge as numbers
  Card $s 645 88 285 420 | Out-Null
  Kicker $s 661 100 255 'WATERFALL_TH (THB MILLION)' | Out-Null
  $rows = @(@{ cells = @('Item', 'MB'); bold = $true; color = $NAVY; line = $true; h = 15; size = 8.5 })
  foreach ($it in $items) {
    $val = [double]$it[2]
    $row = @{ cells = @([string]$it[0], $(if ($it[3] -eq 'total') { F1 $val } else { SG1 $val })); h = 14.4; size = 8.5 }
    if ($it[3] -eq 'total') { $row.bold = $true; $row.color = $NAVY; $row.fill = $TINT; $row.line = $true } else { $row.indent = 8; $row.colors = @($TEXT, $(if ($val -ge 0.05) { $RED } elseif ($val -le -0.05) { $GREEN } else { $TEXT })) }
    $rows += $row
  }
  $yy = Grid $s 661 118 @(200, 54) 14.4 $rows
  L $s 661 ($yy + 8) 914 ($yy + 8) $LINE 0.5 $false | Out-Null
  Kicker $s 661 ($yy + 14) 255 'TIES TO P.7' | Out-Null
  T $s 661 ($yy + 29) 253 36 $recon 8 $TEXT $false 'l' | Out-Null
  return $s
}

# ---------------- Slide 8: Admin P ----------------
$pLE = [double]$BP.'LE 2026'; $pR = [double]$BP.'AP 2027 Reporting'
$itemsP = @(
  @('LE 2026', 'LE 2026', $pLE, 'total'),
  @('Rev Bonus 2025', "Rev Bonus`r2025", [double]$BP.'Rev Bonus 2025', 'step'),
  @('Wellgrow Base', "Wellgrow`rBase", [double]$BP.'Wellgrow Base', 'step'),
  @('Special Incentive', "Special`rIncentive", [double]$BP.'Special Incentive', 'step'),
  @('2026 Underlying', "2026`rUnderlying", [double]$BP.'2026 Underlying', 'total'),
  @('Salary', 'Salary', [double]$BP.'Salary', 'step'),
  @('Medical care', "Medical`rcare", [double]$BP.'Medical care', 'step'),
  @('Other Welfare', "Other`rWelfare", [double]$BP.'Other Welfare', 'step'),
  @('Staff recruitment', "Staff`rrecruitment", [double]$BP.'Staff recruitment', 'step'),
  @('Training', 'Training', [double]$BP.'Trainning', 'step'),
  @('Other', 'Other', [double]$BP.'Other', 'step'),
  @('AP 2027 Base', "AP 2027`rBase", [double]$BP.'AP 2027 Base', 'total'),
  @('Wellgrow', 'Wellgrow', [double]$BP.'Wellgrow', 'step'),
  @('AP 2027 Reporting', "AP 2027`rReporting", $pR, 'total'),
  @('Saving', 'Saving', [double]$BP.'Saving', 'step'),
  @('AP 2027 Stretch', "AP 2027`rStretch", [double]$BP.'AP 2027 Strech', 'total'))
$reconP = ('LE 2026 ' + (F1 $pLE) + ' and AP 2027 Reporting ' + (F1 $pR) + ' MB are the Admin P Thailand line on p.7 (' + ('{0:N0}' -f $pLE) + ' ' + $ARROW + ' ' + ('{0:N0}' -f $pR) + '); Thailand + International = TWPC (ConsoAll).')
$null = AdminPage ('Admin P (Thailand): ' + (F1 $pLE) + ' ' + $ARROW + ' ' + (F1 $pR) + ' MB in AP 2027, ' + (SG1 ($pR - $pLE)) + ' MB / ' + (SG1 (($pR - $pLE) / $pLE * 100)) + '%') 'Admin P cost (THB million): LE 2026 to AP 2027, per Waterfall_TH' $itemsP 280 360 $reconP

# ---------------- Slide 9: Admin Non-P ----------------
$nLE = [double]$BN.'LE 2026'; $nR = [double]$BN.'AP 2027 Reporting'
$itemsN = @(
  @('LE 2026', 'LE 2026', $nLE, 'total'),
  @('Impairment', 'Impairment', [double]$BN.'Impairment', 'step'),
  @('TDC 2.0 Pre-Operating', "TDC 2.0`rPre-Operating", [double]$BN.'TDC 2.0 Pre-Operating', 'step'),
  @('Wellgrow Base', "Wellgrow`rBase", [double]$BN.'Wellgrow Base', 'step'),
  @('TTDI Loyalty 2025', "TTDI`rLoyalty`r2025", [double]$BN.'TTDI Loyalty 2025', 'step'),
  @('2026 Underlying', "2026`rUnderlying", [double]$BN.'2026 Underlying', 'total'),
  @('Consult Fee', "Consult`rFee", [double]$BN.'Consult Fee', 'step'),
  @('Admin', 'Admin', [double]$BN.'Admin', 'step'),
  @('IT', 'IT', [double]$BN.'IT', 'step'),
  @('Other', 'Other', [double]$BN.'Other', 'step'),
  @('AP 2027 Base', "AP 2027`rBase", [double]$BN.'AP 2027 Base', 'total'),
  @('Impairment TDC RY (MS1)', "Impairment`rTDC RY (MS1)", [double]$BN.'Impairment TDC RY (MS1)', 'step'),
  @('TDC2.0 pre-operating', "TDC2.0`rpre-operating", [double]$BN.'TDC2.0 pre-operating', 'step'),
  @('Wellgrow', 'Wellgrow', [double]$BN.'Wellgrow', 'step'),
  @('AP 2027 Reporting', "AP 2027`rReporting", $nR, 'total'),
  @('Saving', 'Saving', [double]$BN.'Saving', 'step'),
  @('AP 2027 Stretch', "AP 2027`rStretch", [double]$BN.'AP 2027 Strech', 'total'))
$reconN = ('LE 2026 ' + (F1 $nLE) + ' and AP 2027 Reporting ' + (F1 $nR) + ' MB are the Admin Non-P Thailand line on p.7 (' + ('{0:N0}' -f $nLE) + ' ' + $ARROW + ' ' + ('{0:N0}' -f $nR) + '); Thailand + International = TWPC (ConsoAll).')
$null = AdminPage ('Admin Non-P (Thailand): ' + (F1 $nLE) + ' ' + $ARROW + ' ' + (F1 $nR) + ' MB in AP 2027, ' + (SG1 ($nR - $nLE)) + ' MB / ' + (SG1 (($nR - $nLE) / $nLE * 100)) + '%') 'Admin Non-P cost (THB million): LE 2026 to AP 2027, per Waterfall_TH' $itemsN 150 250 $reconN
