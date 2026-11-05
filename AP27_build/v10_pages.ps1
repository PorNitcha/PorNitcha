# ================= Thai admin pages (slides 7-8 of the 5-Nov deck) from bridge.json (BU Review_Admin.xlsx, Waterfall_TH) =================
$BR = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'bridge.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$BP = $BR.P; $BN = $BR.N; $BT = $BR.TOT
function SG1($x) { $q = [double]$x; if ([Math]::Abs($q) -lt 0.05) { return '0.0' }; if ($q -gt 0) { return ('+{0:N1}' -f $q) }; return ('({0:N1})' -f (-$q)) }
function PCT1($num, $den) { return ('{0:N1}%' -f ([double]$num / [double]$den * 100)) }
$SRC7 = 'Source: BU Review_Admin.xlsx (Waterfall_TH, NonP by Cost Center). Thailand admin per that file: International (TWIT, TWFZ, TWIC, VN, TWIN, TWII, TWIP, Food VN) excluded. LE 2026 = FC 9+3. THB million, 1 decimal.'
$NONP = RGB '00a6dc'; $PCOL = $NAVY; $TOTC = RGB '2b3a8c'

# ---- derived figures (all from the sheet)
$le = [double]$BT.'LE 2026'; $rep = [double]$BT.'AP 2027 Reporting'; $str = [double]$BT.'AP 2027 Strech'; $und = [double]$BT.'Underlying 2026'; $base = [double]$BT.'AP 2027 Base'
$dRep = $rep - $le; $pLE = [double]$BP.'LE 2026'; $pRep = [double]$BP.'AP 2027 Reporting'; $nLE = [double]$BN.'LE 2026'; $nRep = [double]$BN.'AP 2027 Reporting'
$p26 = [double]$BP.'Rev Bonus 2025' + [double]$BP.'Wellgrow Base' + [double]$BP.'Special Incentive'
$n26 = [double]$BN.'Impairment' + [double]$BN.'TDC 2.0 Pre-Operating' + [double]$BN.'Wellgrow Base' + [double]$BN.'TTDI Loyalty 2025'
$pU = [double]$BP.'Salary' + [double]$BP.'Medical care' + [double]$BP.'Other Welfare' + [double]$BP.'Staff recruitment' + [double]$BP.'Trainning' + [double]$BP.'Other'
$nU = [double]$BN.'Consult Fee' + [double]$BN.'Admin' + [double]$BN.'IT' + [double]$BN.'Other'
$p27 = [double]$BP.'Wellgrow'; $n27 = [double]$BN.'Impairment TDC RY (MS1)' + [double]$BN.'TDC2.0 pre-operating' + [double]$BN.'Wellgrow'
$one27 = [double]$BN.'Impairment TDC RY (MS1)' + [double]$BN.'TDC2.0 pre-operating'
$sav = [double]$BT.'Saving'; $inter = [double]$BT.'Inter'; $grp = [double]$BT.'Total incl Inter'; $tgt = [double]$BT.'Target Admin'
$tdcP = [double]$BR.tdc_p.TDC.AP27 - [double]$BR.tdc_p.TDC.LE26; $tdc2P = [double]$BR.tdc_p.'TDC2.0'.AP27
$cc = $BR.cc

# ================= Slide 7: overview + waterfall =================
$s = Page ('Thai admin ' + (SG1 $dRep) + ' MB (' + (SG1 ($dRep / $le * 100)).Replace('.0', '') + '%) in AP2027: personnel up, non-personnel flat') $SRC7
Card $s 30 88 570 420 | Out-Null
T $s 46 100 540 18 ('Thai admin bridge, LE 2026 to AP 2027 (THB million), split by Admin P and Admin Non-P') 13 $NAVY $true 'l' | Out-Null
Legend $s 46 121 @(@('Admin P (personnel)', $PCOL), @('Admin Non-P (non-personnel)', $NONP), @('Totals', $TOTC))
# bars: totals carry P+N; steps are one category each
$bars = @(
  @{ lab = 'LE 2026 (9+3)'; v = $le; kind = 'total'; grp = $null },
  @{ lab = 'P'; v = $p26; cat = 'P'; kind = 'step'; grp = '2026 one-offs reversed' }, @{ lab = 'Non-P'; v = $n26; cat = 'N'; kind = 'step'; grp = $null },
  @{ lab = '2026 underlying'; v = $und; kind = 'total'; grp = $null },
  @{ lab = 'P'; v = $pU; cat = 'P'; kind = 'step'; grp = 'Recurring cost growth' }, @{ lab = 'Non-P'; v = $nU; cat = 'N'; kind = 'step'; grp = $null },
  @{ lab = 'AP 2027 base'; v = $base; kind = 'total'; grp = $null },
  @{ lab = 'P'; v = $p27; cat = 'P'; kind = 'step'; grp = '2027 one-offs & Well Grow' }, @{ lab = 'Non-P'; v = $n27; cat = 'N'; kind = 'step'; grp = $null },
  @{ lab = 'AP 2027 (P&L)'; v = $rep; kind = 'total'; grp = $null },
  @{ lab = 'P'; v = [double]$BP.'Saving'; cat = 'P'; kind = 'step'; grp = 'Saving programme' }, @{ lab = 'Non-P'; v = [double]$BN.'Saving'; cat = 'N'; kind = 'step'; grp = $null },
  @{ lab = 'AP 2027 stretch'; v = $str; kind = 'total'; grp = $null })
$floor = 440.0; $ceil = 600.0; $x0 = 52.0; $slot = 520.0 / 13; $bw = 26; $yTop = 146; $yBase = 318; $k = ($yBase - $yTop) / ($ceil - $floor)
function YV7($val) { return $yBase - ([double]$val - $floor) * $k }
$run = 0.0; $i = 0
foreach ($b in $bars) {
  $cx = $x0 + $slot * ($i + 0.5); $bx = $cx - $bw / 2
  if ($b.kind -eq 'total') {
    $top = YV7 $b.v
    Rect $s $bx $top $bw ($yBase - $top) $TOTC | Out-Null
    Rect $s ($bx - 1) ($yBase - 8) ($bw + 2) 2.2 $WHITE | Out-Null    # axis-break mark: bars do not start at zero
    T $s ($cx - 26) ($top - 14) 52 12 ('{0:N1}' -f $b.v) 9 $NAVY $true 'c' | Out-Null
    $run = [double]$b.v
  } else {
    $dv = [double]$b.v; $fill = $(if ($b.cat -eq 'P') { $PCOL } else { $NONP })
    L $s ($cx - $slot / 2 - $bw / 2 + 0) (YV7 $run) ($bx) (YV7 $run) $MUTED 0.5 $true | Out-Null
    $yA = YV7 ($run + [Math]::Max(0, $dv)); $h = [Math]::Max(1.5, [Math]::Abs($dv) * $k)
    Rect $s $bx $yA $bw $h $fill | Out-Null
    $ly = $(if ($dv -ge 0) { $yA - 12 } else { $yA + $h + 1 })
    T $s ($cx - 26) $ly 52 11 (SG1 $dv) 8.5 $(if ($b.cat -eq 'P') { $PCOL } else { (RGB '0089c0') }) $true 'c' | Out-Null
    $run += $dv
  }
  if ($i -lt 12) { $nb = $bars[$i + 1]; if ($nb.kind -eq 'total') { L $s ($bx + $bw) (YV7 $run) ($cx + $slot - $bw / 2) (YV7 $run) $MUTED 0.5 $true | Out-Null } }
  # x labels: P / Non-P tag for steps, group label spanning the pair; totals get their own label
  if ($b.kind -eq 'step') {
    T $s ($cx - $slot / 2) ($yBase + 3) $slot 10 $b.lab 7 $MUTED $false 'c' | Out-Null
    if ($b.grp) { T $s ($cx - $slot / 2) ($yBase + 14) (2 * $slot) 24 $b.grp 8 $TEXT $true 'c' | Out-Null }
  } else { T $s ($cx - $slot / 2 - 4) ($yBase + 3) ($slot + 8) 24 $b.lab 8 $TEXT $true 'c' | Out-Null }
  $i++
}
L $s $x0 $yBase ($x0 + 13 * $slot) $yBase $LINE 0.75 $false | Out-Null
T $s 46 ($yBase + 40) 540 10 ('Axis starts at ' + ('{0:N0}' -f $floor) + ' MB so the steps are visible. AP 2027 (P&L) = AP2027 Board in ConsoAll; stretch = after the saving programme.') 7 $MUTED $false 'l' | Out-Null
# executive summary box
$by = 372; $bh = 112
Rect $s 46 $by 538 $bh $NOTEBG | Out-Null; Rect $s 46 $by 3 $bh $KICK | Out-Null
Kicker $s 58 ($by + 5) 400 'EXECUTIVE SUMMARY' | Out-Null
$runs = @(
  @(([string][char]0x25AA + ' '), $false, $KICK), @('Budget discipline: ', $true, $NAVY),
  @(('Thai admin ' + ('{0:N1}' -f $rep) + ' MB in AP2027 (' + (SG1 $dRep) + ' MB, ' + (SG1 ($dRep / $le * 100)) + '%). The ' + ('{0:N1}' -f (-$sav)) + ' MB saving programme takes it to a ' + ('{0:N1}' -f $str) + ' MB stretch; with International ' + ('{0:N1}' -f $inter) + ' MB the group lands at ' + ('{0:N1}' -f $grp) + ' MB against the ' + ('{0:N0}' -f $tgt) + ' MB target.'), $false, $TEXT),
  @([string][char]13, $false, $TEXT),
  @(([string][char]0x25AA + ' '), $false, $KICK), @('P vs Non-P mix: ', $true, $NAVY),
  @(('personnel ' + ('{0:N1}' -f $pRep) + ' MB = ' + (PCT1 $pRep $rep) + ' of Thai admin (' + (PCT1 $pLE $le) + ' in 2026 LE), ' + (SG1 ($pRep - $pLE)) + ' MB; non-personnel ' + ('{0:N1}' -f $nRep) + ' MB (' + (PCT1 $nRep $rep) + ') is flat, ' + (SG1 ($nRep - $nLE)) + ' MB, as 2026 impairments of ' + ('{0:N1}' -f (-[double]$BN.'Impairment')) + ' MB drop out and 2027 one-offs of ' + ('{0:N1}' -f $one27) + ' MB replace them.'), $false, $TEXT),
  @([string][char]13, $false, $TEXT),
  @(([string][char]0x25AA + ' '), $false, $KICK), @('Net impact: ', $true, $NAVY),
  @(('recurring cost growth ' + (SG1 ($pU + $nU)) + ' MB (' + (SG1 (($pU + $nU) / $und * 100)) + '% on the 2026 underlying of ' + ('{0:N1}' -f $und) + '): personnel ' + (SG1 $pU) + ' (merit, welfare, talent) and non-personnel ' + (SG1 $nU) + ' (professional fees, IT); one-offs and Well Grow net to ' + (SG1 ($p27 + $n27 + $p26 + $n26)) + ' MB.'), $false, $TEXT))
$tb = TR $s 58 ($by + 20) 520 ($bh - 24) $runs 9
$tb.TextFrame.TextRange.ParagraphFormat.SpaceAfter = [single]2
# right card: data table
Card $s 615 88 315 420 | Out-Null
Kicker $s 631 100 280 'BRIDGE DATA (THB MILLION)' | Out-Null
$wd = @(139, 48, 48, 48)
$rows = @(@{ cells = @('', 'P', 'Non-P', 'Total'); bold = $true; color = $NAVY; line = $true; h = 16; size = 8.5 })
foreach ($ln in $BR.lines) {
  $lab = [string]$ln[0]; $pv = [double]$ln[1]; $nv = [double]$ln[2]; $kind = [string]$ln[3]
  $cells = @($lab, $(if ($kind -eq 'line') { SG1 $pv } else { '{0:N1}' -f $pv }), $(if ($kind -eq 'line') { SG1 $nv } else { '{0:N1}' -f $nv }), $(if ($kind -eq 'line') { SG1 ($pv + $nv) } else { '{0:N1}' -f ($pv + $nv) }))
  if ($kind -eq 'line') { foreach ($j in 1, 2) { if ([Math]::Abs(@($pv, $nv)[$j - 1]) -lt 0.05) { $cells[$j] = $DASH } } }
  $row = @{ cells = $cells; h = 14.4; size = 8 }
  if ($kind -eq 'total') { $row.bold = $true; $row.color = $NAVY; $row.fill = $TINT; $row.line = $true }
  elseif ($kind -eq 'subtotal') { $row.bold = $true; $row.color = $NAVY; $row.line = $true }
  else { $row.indent = 8; $row.color = $TEXT }
  $rows += $row
}
$yy = Grid $s 631 118 $wd 14.4 $rows
T $s 631 ($yy + 6) 283 44 ('( ) = lower cost / credit. 2026 one-offs: impairment of the Maesod cassava-flour line and TKT/TWBP assets (non-cash), TDC 2.0 pre-operating, special incentive; the 2025 bonus-accrual reversal is a credit that flattered 2026.') 7 $MUTED $false 'l' | Out-Null

# ================= Slide 8: drivers (why & how) =================
$s = Page ('Admin: merit and TDC 2.0 funded, ' + ('{0:N0}' -f (-$sav)) + ' MB savings keep the ' + ('{0:N0}' -f $tgt) + ' MB target') $SRC7
function DrvCard($x, $title, $sub, $rowsIn) {
  Card $s $x 88 445 304 | Out-Null
  Kicker $s ($x + 16) 100 410 $title | Out-Null
  T $s ($x + 16) 114 410 13 $sub 9.5 $NAVY $true 'l' | Out-Null
  $w3 = @(246, 62, 105)
  $rows = @(@{ cells = @('Driver', 'MB', 'Nature'); bold = $true; color = $NAVY; line = $true; h = 15; size = 8.5 })
  foreach ($r in $rowsIn) {
    $kind = [string]$r[3]
    $row = @{ cells = @([string]$r[0], $(if ($kind -eq 'line') { SG1 $r[1] } else { '{0:N1}' -f [double]$r[1] }), [string]$r[2]); h = 14.6; size = 8.5; colors = @($null, $null, $MUTED) }
    if ($kind -eq 'total') { $row.bold = $true; $row.color = $NAVY; $row.fill = $TINT; $row.line = $true; $row.colors = @($NAVY, $NAVY, $MUTED) }
    elseif ($kind -eq 'subtotal') { $row.bold = $true; $row.color = $NAVY; $row.line = $true; $row.colors = @($NAVY, $NAVY, $MUTED) }
    else { $row.indent = 8; $row.colors = @($TEXT, $(if ([double]$r[1] -ge 0.05) { $RED } elseif ([double]$r[1] -le -0.05) { $GREEN } else { $TEXT }), $MUTED) }
    $rows += $row
  }
  return (Grid $s ($x + 16) 130 $w3 14.6 $rows)
}
$pRows = @(
  @('LE 2026 (9+3)', $pLE, '', 'total'),
  @('Reversal of 2025 bonus accrual (credit in 2026)', [double]$BP.'Rev Bonus 2025', '2026 one-off', 'line'),
  @('Special incentive 2026', [double]$BP.'Special Incentive', '2026 one-off', 'line'),
  @('Well Grow base (Sep-Dec 2026)', [double]$BP.'Wellgrow Base', 'base', 'line'),
  @('2026 underlying', [double]$BP.'2026 Underlying', '', 'subtotal'),
  @(('Merit & inflation (salary; ' + (PCT1 $BP.'Salary' $BP.'2026 Underlying') + ' of base)'), [double]$BP.'Salary', 'recurring', 'line'),
  @('Medical care & other welfare', ([double]$BP.'Medical care' + [double]$BP.'Other Welfare'), 'recurring', 'line'),
  @('Recruitment & training (talent)', ([double]$BP.'Staff recruitment' + [double]$BP.'Trainning'), 'recurring', 'line'),
  @('Other personnel', [double]$BP.'Other', 'recurring', 'line'),
  @('AP 2027 base', [double]$BP.'AP 2027 Base', '', 'subtotal'),
  @('Well Grow full year', $p27, 'structural', 'line'),
  @('AP 2027 reporting (P&L)', $pRep, '', 'total'),
  @('Saving programme', [double]$BP.'Saving', 'target', 'line'),
  @('AP 2027 stretch', [double]$BP.'AP 2027 Strech', '', 'total'))
$yL = DrvCard 30 ('ADMIN P (PERSONNEL) ' + $DOT + ' DRIVERS') ('Thai P ' + ('{0:N1}' -f $pLE) + ' ' + $ARROW + ' ' + ('{0:N1}' -f $pRep) + ' MB, ' + (SG1 ($pRep - $pLE)) + ' MB / ' + (SG1 (($pRep - $pLE) / $pLE * 100)) + '%; underlying ' + (SG1 $pU) + ' MB / ' + (SG1 ($pU / [double]$BP.'2026 Underlying' * 100)) + '%') $pRows
T $s 46 ($yL + 4) 413 26 ('TDC 2.0 team ' + ('{0:N1}' -f $tdc2P) + ' MB in AP2027 is largely transferred from TDC Rayong, ' + (SG1 $tdcP) + ' MB; net ' + (SG1 ($tdc2P + $tdcP)) + ' MB, already inside the lines above (entity P cost, BU Review_Admin).') 7.5 $MUTED $false 'l' | Out-Null
$nRows = @(
  @('LE 2026 (9+3)', $nLE, '', 'total'),
  @('Impairment: Maesod flour line, TKT, TWBP (non-cash)', [double]$BN.'Impairment', '2026 one-off', 'line'),
  @('TDC 2.0 pre-operating 2026', [double]$BN.'TDC 2.0 Pre-Operating', '2026 one-off', 'line'),
  @('TTDI loyalty 2025', [double]$BN.'TTDI Loyalty 2025', '2026 one-off', 'line'),
  @('Well Grow base (Sep-Dec 2026)', [double]$BN.'Wellgrow Base', 'base', 'line'),
  @('2026 underlying', [double]$BN.'2026 Underlying', '', 'subtotal'),
  @('Professional / consulting fees', [double]$BN.'Consult Fee', 'recurring', 'line'),
  @('Admin & facility', [double]$BN.'Admin', 'recurring', 'line'),
  @(('IT & digital (' + ('{0:N1}' -f $cc.IT.AP27) + ' MB)'), [double]$BN.'IT', 'recurring', 'line'),
  @('Other', [double]$BN.'Other', 'recurring', 'line'),
  @('AP 2027 base', [double]$BN.'AP 2027 Base', '', 'subtotal'),
  @('TDC Rayong MS1 write-off (non-cash)', [double]$BN.'Impairment TDC RY (MS1)', '2027 one-off', 'line'),
  @('TDC 2.0 pre-operating 2027', [double]$BN.'TDC2.0 pre-operating', '2027 one-off', 'line'),
  @('Well Grow full year', [double]$BN.'Wellgrow', 'structural', 'line'),
  @('AP 2027 reporting (P&L)', $nRep, '', 'total'),
  @('Saving programme', [double]$BN.'Saving', 'target', 'line'),
  @('AP 2027 stretch', [double]$BN.'AP 2027 Strech', '', 'total'))
$yR = DrvCard 485 ('ADMIN NON-P (NON-PERSONNEL) ' + $DOT + ' DRIVERS') ('Thai Non-P ' + ('{0:N1}' -f $nLE) + ' ' + $ARROW + ' ' + ('{0:N1}' -f $nRep) + ' MB, ' + (SG1 ($nRep - $nLE)) + ' MB / ' + (SG1 (($nRep - $nLE) / $nLE * 100)) + '%; underlying ' + (SG1 $nU) + ' MB / ' + (SG1 ($nU / [double]$BN.'2026 Underlying' * 100)) + '%') $nRows
# bottom banner: action plan + likely questions
$by = 404; $bh = 100
Rect $s 30 $by 900 $bh $NOTEBG | Out-Null; Rect $s 30 $by 3 $bh $KICK | Out-Null
Kicker $s 42 ($by + 5) 420 ('ACTION PLAN & EFFICIENCY') | Out-Null
Kicker $s 492 ($by + 5) 420 ('WHAT THE CEO / BU HEADS WILL ASK') | Out-Null
$exOne = $rep - $one27
$ccOff = ([double]$cc.HR.AP27 - [double]$cc.HR.under26) + ([double]$cc.Farm.AP27 - [double]$cc.Farm.under26) + ([double]$cc.Account.AP27 - [double]$cc.Account.under26)
$runsL = @(
  @(([string][char]0x25AA + ' '), $false, $KICK), @(('Saving programme ' + ('{0:N1}' -f (-$sav)) + ' MB (P ' + ('{0:N1}' -f (-[double]$BP.'Saving')) + ' / Non-P ' + ('{0:N1}' -f (-[double]$BN.'Saving')) + ') '), $true, $NAVY), @(('takes Thai admin to ' + ('{0:N1}' -f $str) + ' MB; with International ' + ('{0:N1}' -f $inter) + ' the group is ' + ('{0:N1}' -f $grp) + ' vs the ' + ('{0:N0}' -f $tgt) + ' MB target.'), $false, $TEXT),
  @([string][char]13, $false, $TEXT),
  @(([string][char]0x25AA + ' '), $false, $KICK), @(('Ex 2027 one-offs (' + ('{0:N1}' -f $one27) + ' MB) Thai admin is ' + ('{0:N1}' -f $exOne) + ' MB, flat vs 2026 LE (' + ('{0:N1}' -f $le) + ')'), $true, $NAVY), @((' while absorbing merit ' + (SG1 $BP.'Salary') + ' and Well Grow ' + (SG1 ($p27 + [double]$BN.'Wellgrow')) + '.'), $false, $TEXT),
  @([string][char]13, $false, $TEXT),
  @(([string][char]0x25AA + ' '), $false, $KICK), @('Offsets already built in: ', $true, $NAVY), @(('HR ' + (SG1 ([double]$cc.HR.AP27 - [double]$cc.HR.under26)) + ', Farm ' + (SG1 ([double]$cc.Farm.AP27 - [double]$cc.Farm.under26)) + ', Accounting ' + (SG1 ([double]$cc.Account.AP27 - [double]$cc.Account.under26)) + ' MB non-P vs 2026, ' + (SG1 $ccOff) + ' MB in total.'), $false, $TEXT))
$runsR = @(
  @(([string][char]0x25AA + ' '), $false, $KICK), @('"Why is personnel +11%?" ', $true, $NAVY), @(('2026 was flattered by the ' + ('{0:N1}' -f $BP.'Rev Bonus 2025') + ' MB bonus-accrual reversal; underlying growth is ' + (SG1 ($pU / [double]$BP.'2026 Underlying' * 100)) + '% (merit ' + (PCT1 $BP.'Salary' $BP.'2026 Underlying') + ', welfare, talent).'), $false, $TEXT),
  @([string][char]13, $false, $TEXT),
  @(([string][char]0x25AA + ' '), $false, $KICK), @('"Is TDC 2.0 adding overhead?" ', $true, $NAVY), @(('Its ' + ('{0:N1}' -f $tdc2P) + ' MB team is mostly transferred from TDC Rayong, ' + (SG1 $tdcP) + ' MB, net ' + (SG1 ($tdc2P + $tdcP)) + ' MB; the ' + ('{0:N1}' -f $BN.'TDC2.0 pre-operating') + ' MB pre-operating cost is one-off.'), $false, $TEXT),
  @([string][char]13, $false, $TEXT),
  @(([string][char]0x25AA + ' '), $false, $KICK), @('"Where is the IT / SAP spend?" ', $true, $NAVY), @(('IT is flat in 2027 (' + ('{0:N1}' -f $cc.IT.AP27) + ' MB, ' + (SG1 ([double]$cc.IT.AP27 - [double]$cc.IT.under26)) + '); the SAP GROW step-up (' + (SG1 ([double]$cc.IT.AP28 - [double]$cc.IT.AP27)) + ' MB to ' + ('{0:N1}' -f $cc.IT.AP28) + ') is an AP2028 item.'), $false, $TEXT))
$t1 = TR $s 42 ($by + 20) 440 ($bh - 24) $runsL 8.5; $t1.TextFrame.TextRange.ParagraphFormat.SpaceAfter = [single]2
$t2 = TR $s 492 ($by + 20) 430 ($bh - 24) $runsR 8.5; $t2.TextFrame.TextRange.ParagraphFormat.SpaceAfter = [single]2
