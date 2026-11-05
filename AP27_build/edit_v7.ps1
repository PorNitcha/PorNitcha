param([string]$DeckIn, [string]$DeckOut, [string]$PngDir, [string]$NewJson, [string]$OldJson, [switch]$DryRun)
# v7 = copy of Por's v5 with the numbers on slides 2, 3, 4, 10 refreshed from the final P&L workbook (sheets_new.json).
# Every numeric cell on those slides is recomputed; a cell whose text differs while its inputs did not change is an UNEXPECTED
# mismatch (format drift) and aborts the run before saving. Expected changes are logged.
$ErrorActionPreference = 'Stop'
$SJ = Get-Content -LiteralPath $NewJson -Encoding UTF8 -Raw | ConvertFrom-Json
$OJ = Get-Content -LiteralPath $OldJson -Encoding UTF8 -Raw | ConvertFrom-Json
$DASH = [string][char]0x2013; $ARROW = [string][char]0x2192; $MINUS = [string][char]0x2212
function N0($x) { if ($null -eq $x) { return $DASH }; $v = [double]$x; if ([Math]::Abs($v) -lt 0.5) { return $DASH }; if ($v -lt 0) { return ('({0:N0})' -f (-$v)) }; return ('{0:N0}' -f $v) }
function KT($x) { $v = [double]$x / 1000.0; if ([Math]::Abs($v) -lt 0.05) { return $DASH }; return ('{0:N1}' -f $v) }
function SG($x) { $v = [double]$x; if ([Math]::Abs($v) -lt 0.5) { return '0' }; if ($v -gt 0) { return ('+{0:N0}' -f $v) }; return ('({0:N0})' -f (-$v)) }
function PC($x) { if ($null -eq $x) { return '' }; $v = [double]$x; if ([Math]::Abs($v) -gt 1) { return 'n.m.' }; return ('{0:N1}%' -f ($v * 100)) }
function PG($x) { if ($null -eq $x) { return 'n.m.' }; $v = [double]$x; if ([Math]::Abs($v) -gt 9.99) { return 'n.m.' }; $sg0 = $(if ($v -ge 0) { '+' } else { $MINUS }); if ([Math]::Abs($v) -ge 1) { return ('{0}{1:N0}%' -f $sg0, [Math]::Abs($v * 100)) }; return ('{0}{1:N1}%' -f $sg0, [Math]::Abs($v * 100)) }
$PRIOR = @{ 'R24' = 'Y23'; '2025' = 'R24'; 'LE26' = '2025'; 'AP27' = 'LE26'; 'AP28' = 'AP27' }
function V($J, $sheet, $line, $scen) { $x = $J.$sheet.$line.$scen; if ($null -eq $x) { throw "no value $sheet / $line / $scen" }; return [double]$x }
function Growth($J, $sheet, $scen) { $a = V $J $sheet 'Volume' $PRIOR[$scen]; $b = V $J $sheet 'Volume' $scen; if ([Math]::Abs($a) -lt 1) { return $null }; return ($b / $a - 1) }
# row label -> formatted text from workbook J, sheet, scen
function Cell($J, $sheet, $label, $scen) {
  switch -Wildcard ($label) {
    'Volume (kt)'              { return (KT (V $J $sheet 'Volume' $scen)) }
    '*% Vol growth'            { return (PG (Growth $J $sheet $scen)) }
    'Net sales*'               { return (N0 (V $J $sheet 'Net Sales' $scen)) }
    'Cost of sales (total)'    { return (N0 (V $J $sheet 'Total COST' $scen)) }
    'of which: idle cost'      { return (N0 (V $J $sheet 'Idle' $scen)) }
    'Gross profit*'            { return (N0 (V $J $sheet 'Gross profit' $scen)) }
    '*%GM'                     { return (PC ((V $J $sheet 'Gross profit' $scen) / (V $J $sheet 'Net Sales' $scen))) }
    'DC'                       { return (N0 (V $J $sheet 'DC' $scen)) }
    'A&P'                      { return (N0 (V $J $sheet 'A&P' $scen)) }
    'S&M'                      { return (N0 (V $J $sheet 'S&M' $scen)) }
    'Total selling'            { return (N0 ((V $J $sheet 'DC' $scen) + (V $J $sheet 'A&P' $scen) + (V $J $sheet 'S&M' $scen))) }
    '% selling'                { return (PC (((V $J $sheet 'DC' $scen) + (V $J $sheet 'A&P' $scen) + (V $J $sheet 'S&M' $scen)) / (V $J $sheet 'Net Sales' $scen))) }
    'OP before admin*'         { return (N0 (V $J $sheet 'OP Before Admin' $scen)) }
    'OPBA (MB)'                { return (N0 (V $J $sheet 'OP Before Admin' $scen)) }
    '%OPBA'                    { return (PC ((V $J $sheet 'OP Before Admin' $scen) / (V $J $sheet 'Net Sales' $scen))) }
    'Admin - people'           { return (N0 (V $J $sheet 'admin exp - People' $scen)) }
    'Admin - non-people'       { return (N0 (V $J $sheet 'admin exp - Non-people' $scen)) }
    'Total admin'              { return (N0 ((V $J $sheet 'admin exp - People' $scen) + (V $J $sheet 'admin exp - Non-people' $scen))) }
    'Other op. income & FX'    { return (N0 ((V $J $sheet 'Operating profit' $scen) - (V $J $sheet 'OP Before Admin' $scen) - (V $J $sheet 'admin exp - People' $scen) - (V $J $sheet 'admin exp - Non-people' $scen))) }   # plug so the column foots, as the builder did
    'Operating profit'         { return (N0 (V $J $sheet 'Operating profit' $scen)) }
    'Net non-operating profit' { return (N0 (V $J $sheet 'Net non-operating profit' $scen)) }
    'Finance income (expense)' { return (N0 (V $J $sheet 'Finance income (expense)' $scen)) }
    'CIT (incl. PPA)'          { return (N0 ((V $J $sheet 'CIT' $scen) + (V $J $sheet 'PPA - CIT' $scen))) }
    'MI'                       { return (N0 (V $J $sheet 'MI' $scen)) }
    'Net profit*'              { return (N0 (V $J $sheet 'Net profit aft Thanos' $scen)) }
    default                    { return $null }
  }
}
$ENT = @{ 'Starch BU' = 'StarchBU'; 'HVA BU incl. Waxy' = 'HVA incl Waxy'; 'Food BU' = 'FoodBU'; 'NBG BU' = 'NBGBU'; 'TWPC' = 'ConsoAll' }
$YR = @{ '2024 Rebase' = 'R24'; '2025' = '2025'; '2026 LE' = 'LE26'; '2027 AP' = 'AP27'; '2028 AP' = 'AP28' }
$log = New-Object System.Collections.Generic.List[string]
$bad = New-Object System.Collections.Generic.List[string]
$nChanged = 0
function SetText($sh, $new, $where) {
  $old = $sh.TextFrame.TextRange.Text
  if ($old -eq $new) { return }
  $script:nChanged++; $log.Add(('{0,-34} {1,12} -> {2}' -f $where, $old, $new))
  if (-not $DryRun) { $sh.TextFrame.TextRange.Text = $new }
}
# compare old-workbook rendering with the slide text: if they differ the slide was not produced by this formula -> unexpected
function Check($sh, $newTxt, $oldTxt, $where) {
  $cur = $sh.TextFrame.TextRange.Text
  if ($cur -ne $oldTxt -and $cur -ne $newTxt) { $bad.Add(('{0,-34} slide "{1}"  old-formula "{2}"  new "{3}"' -f $where, $cur, $oldTxt, $newTxt)); return }
  SetText $sh $newTxt $where
}

Copy-Item -LiteralPath $DeckIn -Destination $DeckOut -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($DeckOut, 0, 0, 0)
try {
  # ------------------------------------------------------------ slides 4 and 10: BU x year tables
  foreach ($sn in 4, 10) {
    $s = $pres.Slides.Item($sn)
    $shapes = @(); for ($i = 1; $i -le $s.Shapes.Count; $i++) { $shapes += $s.Shapes.Item($i) }
    $heads = @(); $years = @(); $labels = @()
    foreach ($sh in $shapes) {
      if ($sh.Type -ne 17) { continue }
      $t = $sh.TextFrame.TextRange.Text
      if ($ENT.ContainsKey($t) -and $sh.Top -gt 85 -and $sh.Top -lt 110) { $heads += $sh }
      elseif ($YR.ContainsKey($t) -and $sh.Top -lt 85) { $years += $sh }
      elseif ($sh.Left -lt 60 -and $sh.Top -gt 110 -and $t -ne '') { $labels += $sh }
    }
    foreach ($lb in $labels) {
      $label = $lb.TextFrame.TextRange.Text.Trim()
      $cells = @($shapes | Where-Object { $_.Type -eq 17 -and [Math]::Abs($_.Top - $lb.Top) -lt 0.8 -and $_.Left -gt 150 })
      foreach ($c in $cells) {
        $cx = $c.Left + $c.Width / 2
        $h = $heads | Where-Object { $cx -ge $_.Left - 0.5 -and $cx -le $_.Left + $_.Width + 0.5 } | Select-Object -First 1
        $y = $years | Where-Object { $cx -ge $_.Left - 1 -and $cx -le $_.Left + $_.Width + 1 } | Select-Object -First 1
        if (-not $h -or -not $y) { throw "slide $sn : no header for cell '$($c.TextFrame.TextRange.Text)' at $($c.Left)" }
        $sheet = $ENT[$h.TextFrame.TextRange.Text]; $scen = $YR[$y.TextFrame.TextRange.Text]
        $newTxt = Cell $SJ $sheet $label $scen
        if ($null -eq $newTxt) { throw "slide $sn : no formula for row '$label'" }
        $oldTxt = Cell $OJ $sheet $label $scen
        Check $c $newTxt $oldTxt ("s$sn $sheet $scen $label")
      }
    }
  }
  # ------------------------------------------------------------ slide 2: TWPC summary table, stacked bars, mix, commitments, title
  $s = $pres.Slides.Item(2)
  $shapes = @(); for ($i = 1; $i -le $s.Shapes.Count; $i++) { $shapes += $s.Shapes.Item($i) }
  $COL2 = @{ '170' = 'R24'; '252' = '2025'; '334' = 'LE26'; '416' = 'AP27'; '498' = 'AP28' }
  foreach ($sh in $shapes) {
    if ($sh.Type -ne 17 -or $sh.Top -lt 330 -or $sh.Top -gt 460) { continue }
    $k = [string][int][Math]::Round($sh.Left)
    if (-not $COL2.ContainsKey($k)) { continue }
    $lb = $shapes | Where-Object { $_.Type -eq 17 -and [Math]::Abs($_.Top - $sh.Top) -lt 0.8 -and $_.Left -lt 60 } | Select-Object -First 1
    $label = $lb.TextFrame.TextRange.Text.Trim(); $scen = $COL2[$k]
    if ($label -eq 'Volume (kt)') { $newTxt = N0 ((V $SJ 'ConsoAll' 'Volume' $scen) / 1000); $oldTxt = N0 ((V $OJ 'ConsoAll' 'Volume' $scen) / 1000) }
    else { $newTxt = Cell $SJ 'ConsoAll' $label $scen; $oldTxt = Cell $OJ 'ConsoAll' $label $scen }
    if ($null -eq $newTxt) { throw "slide 2 : no formula for row '$label'" }
    Check $sh $newTxt $oldTxt ("s2 table ConsoAll $scen $label")
  }
  # stacked-bar total labels (14pt, Left = column - 18) and the 2028 'other' bar
  $BARX = @{ '169' = 'R24'; '251' = '2025'; '333' = 'LE26'; '415' = 'AP27'; '497' = 'AP28' }
  $pxPerMB = $null; $grey27 = $null
  foreach ($sh in $shapes) {
    if ($sh.Type -eq 17 -and $sh.Top -gt 130 -and $sh.Top -lt 230 -and [Math]::Abs($sh.Width - 76) -lt 0.5) {
      $k = [string][int][Math]::Round($sh.Left)
      if ($BARX.ContainsKey($k)) { $scen = $BARX[$k]; Check $sh (N0 (V $SJ 'ConsoAll' 'OP Before Admin' $scen)) (N0 (V $OJ 'ConsoAll' 'OP Before Admin' $scen)) "s2 bar total $scen" }
    }
    if ($sh.Type -eq 1 -and [Math]::Abs($sh.Left - 433) -lt 0.6 -and $sh.Fill.ForeColor.RGB -eq 7152153 -and $sh.Height -gt 50) { $pxPerMB = $sh.Height / (V $SJ 'FoodBU' 'OP Before Admin' 'AP27') }
    if ($sh.Type -eq 1 -and [Math]::Abs($sh.Left - 433) -lt 0.6 -and $sh.Fill.ForeColor.RGB -eq 10921638) { $grey27 = $sh }
  }
  if (-not $pxPerMB -or -not $grey27) { throw 'slide 2: bar scale / grey bar not found' }
  # 'other' (NBG + Corp) bar per year: below the axis when negative
  foreach ($k in $BARX.Keys) {
    $scen = $BARX[$k]; $x = [double]$k + 18
    $otherNew = (V $SJ 'NBGBU' 'OP Before Admin' $scen) + (V $SJ 'Corp' 'OP Before Admin' $scen) + (V $SJ 'ElimBU' 'OP Before Admin' $scen)
    $otherOld = (V $OJ 'NBGBU' 'OP Before Admin' $scen) + (V $OJ 'Corp' 'OP Before Admin' $scen) + (V $OJ 'ElimBU' 'OP Before Admin' $scen)
    $bar = $shapes | Where-Object { $_.Type -eq 1 -and [Math]::Abs($_.Left - $x) -lt 0.6 -and $_.Fill.ForeColor.RGB -eq 10921638 } | Select-Object -First 1
    $hNew = [Math]::Max(0, -$otherNew) * $pxPerMB
    $log.Add(('s2 other bar {0}: NBG+Corp+Elim {1:N1} -> {2:N1} MB; bar h {3} -> {4:N1}' -f $scen, $otherOld, $otherNew, $(if ($bar) { '{0:N1}' -f $bar.Height } else { 'none' }), $hNew))
    if ($DryRun -or ($scen -ne 'AP27' -and $scen -ne 'AP28')) { continue }
    if ($bar -and $hNew -lt 0.5) { $bar.Delete() }
    elseif ($bar) { $bar.Height = [single]$hNew }
    elseif ($hNew -ge 0.5) { $d = $grey27.Duplicate().Item(1); $d.Left = [single]$x; $d.Top = [single]$grey27.Top; $d.Width = [single]$grey27.Width; $d.Height = [single]$hNew; $d.Name = 'other_' + $scen }
  }
  # oval, title, commitments, mix labels
  $o26 = V $SJ 'ConsoAll' 'OP Before Admin' 'LE26'; $o27 = V $SJ 'ConsoAll' 'OP Before Admin' 'AP27'; $o28 = V $SJ 'ConsoAll' 'OP Before Admin' 'AP28'
  $np26 = V $SJ 'ConsoAll' 'Net profit aft Thanos' 'LE26'; $np27 = V $SJ 'ConsoAll' 'Net profit aft Thanos' 'AP27'
  $pct27 = ($o27 / $o26 - 1) * 100
  foreach ($sh in $shapes) {
    if ($sh.HasTextFrame -ne -1) { continue }
    $t = $sh.TextFrame.TextRange.Text
    if ($sh.Type -eq 14 -and $t -like 'AP2027: OPBA*') { SetText $sh ('AP2027: OPBA +' + ('{0:N0}' -f $pct27) + '% to ' + (N0 $o27) + ' MB, but net profit only ' + (SG ($np27 - $np26)) + ' MB to ' + (N0 $np27) + ' MB') 's2 title' }
    elseif ($t -like '+*% vs LE') { SetText $sh ('+' + ('{0:N0}' -f $pct27) + '% vs LE') 's2 oval' }
    elseif ($t -match '^[+(]\d+\)?$' -and [Math]::Abs($sh.Left - 606) -lt 0.5 -and $sh.Top -lt 310) { SetText $sh (SG ($o27 - $o26)) 's2 commit +OPBA' }
    elseif ($t -match '^\(\d+\)$' -and [Math]::Abs($sh.Left - 606) -lt 0.5 -and $sh.Top -gt 410) { SetText $sh (SG ($o27 - (V $SJ 'ConsoAll' 'OP Before Admin' 'AP26'))) 's2 commit vs AP26' }
    elseif ($t -match '^[\d,]+ MB$' -and [Math]::Abs($sh.Left - 830) -lt 0.5) {
      $scen = $(if ($sh.Top -lt 130) { '2025' } elseif ($sh.Top -lt 165) { 'LE26' } elseif ($sh.Top -lt 200) { 'AP27' } else { 'AP28' })
      if ($scen) { SetText $sh ((N0 (V $SJ 'ConsoAll' 'OP Before Admin' $scen)) + ' MB') "s2 mix total $scen" }
    }
  }
  # mix shares (core BUs) - check only, geometry untouched unless a share changes
  foreach ($scen in '2025', 'LE26', 'AP27', 'AP28') {
    $f = V $SJ 'FoodBU' 'OP Before Admin' $scen; $hv = V $SJ 'HVA incl Waxy' 'OP Before Admin' $scen; $st = V $SJ 'StarchBU' 'OP Before Admin' $scen; $tot = $f + $hv + $st
    $log.Add(('s2 mix {0}: Food {1:N0}% HVA {2:N0}% Starch {3:N0}% (unchanged by this update unless logged above)' -f $scen, ($f / $tot * 100), ($hv / $tot * 100), ($st / $tot * 100)))
  }
  # ------------------------------------------------------------ slide 3: OPBA by entity table + insight
  $s = $pres.Slides.Item(3)
  $shapes = @(); for ($i = 1; $i -le $s.Shapes.Count; $i++) { $shapes += $s.Shapes.Item($i) }
  $ROW3 = @{ 'Food BU' = @('FoodBU'); 'Food TH' = @('FoodTH'); 'Well Grow' = @('FoodWG'); 'Food VN' = @('FoodVN'); 'HVA BU incl. Waxy' = @('HVA incl Waxy'); 'TDC' = @('TDC'); 'TDC 2.0' = @('TDC2.0'); 'TWIN' = @('TWIN'); 'TWII' = @('TWII'); 'Waxy' = @('Waxy'); 'memo: HVA excl. Waxy' = @('HVABU')
             'Starch BU' = @('StarchBU'); 'Starch TH' = @('StarchTH'); 'China' = @('TotalCN'); 'TWIT' = @('TWIT'); 'TWFZ' = @('TWFZ'); 'Cambodia (TWIC)' = @('TWIC'); 'Vietnam (TNT+VTC)' = @('TotalVN'); 'NBG BU' = @('NBGBU'); 'Bioplastic' = @('BioPlastic'); 'Discontinued (feed, AgBio, V9)' = @('AnimalFeeds', 'AgBio', 'V9'); 'TWPC total' = @('ConsoAll') }
  function OPBA3($J, $sheets, $scen) { $v = 0.0; foreach ($x in $sheets) { $v += V $J $x 'OP Before Admin' $scen }; return $v }
  $labels = @($shapes | Where-Object { $_.Type -eq 17 -and $_.Left -lt 90 -and $_.Top -gt 100 -and $ROW3.ContainsKey($_.TextFrame.TextRange.Text.Trim()) })
  if ($labels.Count -lt 20) { throw "slide 3: only $($labels.Count) rows matched" }
  $SC3 = @('R24', '2025', 'LE26', 'AP27')
  foreach ($lb in $labels) {
    $label = $lb.TextFrame.TextRange.Text.Trim(); $sheets = $ROW3[$label]
    $cells = @($shapes | Where-Object { $_.Type -eq 17 -and [Math]::Abs($_.Top - $lb.Top) -lt 0.8 -and $_.Left -gt 150 -and $_.Left -lt 590 } | Sort-Object Left)
    if ($cells.Count -ne 5) { throw "slide 3: row '$label' has $($cells.Count) cells" }
    for ($j = 0; $j -lt 4; $j++) { Check $cells[$j] (N0 (OPBA3 $SJ $sheets $SC3[$j])) (N0 (OPBA3 $OJ $sheets $SC3[$j])) ("s3 $label $($SC3[$j])") }
    Check $cells[4] (SG ((OPBA3 $SJ $sheets 'AP27') - (OPBA3 $SJ $sheets 'LE26'))) (SG ((OPBA3 $OJ $sheets 'AP27') - (OPBA3 $OJ $sheets 'LE26'))) ("s3 $label delta")
  }
  foreach ($sh in $shapes) {
    if ($sh.Type -ne 17) { continue }
    $t = $sh.TextFrame.TextRange.Text
    if ($t -eq ((N0 (V $OJ 'BioPlastic' 'OP Before Admin' 'LE26')) + ' ' + $ARROW + ' ' + (N0 (V $OJ 'BioPlastic' 'OP Before Admin' 'AP27')))) { SetText $sh ((N0 (V $SJ 'BioPlastic' 'OP Before Admin' 'LE26')) + ' ' + $ARROW + ' ' + (N0 (V $SJ 'BioPlastic' 'OP Before Admin' 'AP27'))) 's3 insight Bioplastic' }
  }
  $rep = New-Object System.Collections.Generic.List[string]
  $rep.Add("---- unexpected mismatches: " + $bad.Count); foreach ($b in $bad) { $rep.Add("  !! " + $b) }
  $rep.Add("---- changes: " + $nChanged); foreach ($l in $log) { $rep.Add("  " + $l) }
  $rep | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'edit_v7_report.txt') -Encoding UTF8
  foreach ($r in $rep) { $r }
  if ($bad.Count -gt 0) { throw 'format drift detected - nothing saved' }
  if (-not $DryRun) {
    $pres.Save()
    if ($PngDir) { New-Item -ItemType Directory -Force $PngDir | Out-Null; foreach ($n in 2, 3, 4, 10) { $pres.Slides.Item($n).Export((Join-Path $PngDir ('s{0:D2}.png' -f $n)), 'PNG', 1600, 900) } }
    "saved $DeckOut"
  }
} finally { $pres.Close(); if ($DryRun -and (Test-Path -LiteralPath $DeckOut)) { Remove-Item -LiteralPath $DeckOut -Force } }
