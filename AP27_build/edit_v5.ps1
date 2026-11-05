param([string]$Src, [string]$Out, [string]$PngDir, [string]$Sheets, [string]$Bridge, [string]$Admin2)
# In-place edits on a copy of Por's v4 deck -> v5 (never touches the source file):
#  A) slides 4, 10-16: insert "of which: idle cost" row under "Cost of sales (total)" (same font as that row, label indented 8pt)
#  B) slide 6: drop the "of which TDC 2.0" row, add an "AP27 Stretch" column after the Change column (TH P and Non-P less the Waterfall_TH saving)
#  C) slides 7-8: waterfall recoloured to the deck tone (navy totals / cyan up / light-cyan down), all numbers rounded to whole MB, "p.7" -> "p.6"
$ErrorActionPreference = 'Stop'
function RGB($hex) { $r = [Convert]::ToInt32($hex.Substring(0,2),16); $g = [Convert]::ToInt32($hex.Substring(2,2),16); $b = [Convert]::ToInt32($hex.Substring(4,2),16); return $r + $g*256 + $b*65536 }
$NAVY = RGB '19226d'; $CYAN = RGB '00a6dc'; $LCYAN = RGB 'a8def3'; $TEXT = RGB '333f50'
$OLD_TOT = RGB '2b3a8c'; $OLD_RED = RGB 'd64545'; $OLD_GREEN = RGB '2e9e5b'
$DASH = [string][char]0x2013
function N0($v) { $v = [double]$v; if ([Math]::Abs($v) -lt 0.5) { return $DASH }; if ($v -lt 0) { return ('({0:N0})' -f (-$v)) }; return ('{0:N0}' -f $v) }
function RoundAway($v) { return [Math]::Round([double]$v, 0, [MidpointRounding]::AwayFromZero) }

$SJ = Get-Content -LiteralPath $Sheets -Encoding UTF8 -Raw | ConvertFrom-Json
$BR = Get-Content -LiteralPath $Bridge -Encoding UTF8 -Raw | ConvertFrom-Json
$A2 = Get-Content -LiteralPath $Admin2 -Encoding UTF8 -Raw | ConvertFrom-Json
$ENT = @{ 'Starch BU' = 'StarchBU'; 'HVA BU incl. Waxy' = 'HVA incl Waxy'; 'Food BU' = 'FoodBU'; 'NBG BU' = 'NBGBU'; 'TWPC' = 'ConsoAll'
          'Starch TH' = 'StarchTH'; 'TWIT' = 'TWIT'; 'TWFZ' = 'TWFZ'; 'TWIC' = 'TWIC'; 'Vietnam' = 'TotalVN'; 'TDC' = 'TDC'; 'TDC 2.0' = 'TDC2.0'
          'Waxy' = 'Waxy'; 'TWIN' = 'TWIN'; 'TWII' = 'TWII'; 'Food TH' = 'FoodTH'; 'Domestic' = 'FoodTH.Dom'; 'Export' = 'FoodTH.Exp'; 'WG' = 'FoodWG'; 'Food VN' = 'FoodVN' }
$YR = @{ '2025' = '2025'; '2026 LE' = 'LE26'; '2027 AP' = 'AP27'; '2028 AP' = 'AP28' }
$log = New-Object System.Collections.Generic.List[string]

Copy-Item -LiteralPath $Src -Destination $Out -Force
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open($Out, 0, 0, 0)
try {
  # ---------------------------------------------------------------- A) idle rows
  foreach ($sn in 4, 10, 11, 12, 13, 14, 15, 16) {
    $s = $p.Slides.Item($sn)
    $title = $s.Shapes.Item(2).TextFrame.TextRange.Text
    # Total BU column -> which BU sheet (deep dives); multi-year slides have no 'Total BU'
    $totalBU = $null
    if ($title -match 'Starch') { $totalBU = 'StarchBU' } elseif ($title -match 'HVA') { $totalBU = 'HVA incl Waxy' } elseif ($title -match 'Food') { $totalBU = 'FoodBU' }
    $shapes = @(); for ($i = 1; $i -le $s.Shapes.Count; $i++) { $shapes += $s.Shapes.Item($i) }
    $lab = $null; $gp = $null; $heads = @(); $years = @()
    foreach ($sh in $shapes) {
      if ($sh.HasTextFrame -ne -1) { continue }
      $t = $sh.TextFrame.TextRange.Text
      if ($t -eq 'Cost of sales (total)') { $lab = $sh }
      elseif ($t -eq 'Gross profit') { $gp = $sh }
      elseif ($ENT.ContainsKey($t) -and $sh.Top -lt 110 -and $sh.Top -gt 85) { $heads += $sh }
      elseif ($t -eq 'Total BU' -and $sh.Top -lt 110) { $heads += $sh }
      elseif ($YR.ContainsKey($t) -and $sh.Top -lt 85) { $years += $sh }
    }
    if (-not $lab -or -not $gp) { throw "slide $sn : cost/GP row not found" }
    $rowTop = $lab.Top; $pitch = $gp.Top - $lab.Top
    if ($pitch -lt 10 -or $pitch -gt 20) { throw "slide $sn : odd pitch $pitch" }
    # row cells = shapes on the same top (label + numeric cells)
    $rowCells = @($shapes | Where-Object { $_.Type -ne 14 -and [Math]::Abs($_.Top - $rowTop) -lt 0.8 -and $_.HasTextFrame -eq -1 })
    # shift everything below the row (not placeholders, not the card, not the 'Source:' footer)
    $nShift = 0; $nGrow = 0
    foreach ($sh in $shapes) {
      if ($sh.Type -eq 14) { continue }
      $isCard = ($sh.Type -eq 1 -and $sh.Width -gt 800 -and $sh.Height -gt 300)
      if ($isCard) { continue }
      if ($sh.HasTextFrame -eq -1 -and $sh.TextFrame.TextRange.Text -like 'Source:*') { continue }
      if ($sh.Top -gt $rowTop + 0.8) { $sh.Top = [single]($sh.Top + $pitch); $nShift++ }
      elseif ($sh.Type -eq 1 -and $sh.Top -lt $rowTop -and ($sh.Top + $sh.Height) -gt $rowTop + $pitch -and $sh.Height -gt 2 * $pitch) { $sh.Height = [single]($sh.Height + $pitch); $nGrow++ }
    }
    # duplicate the row cells into the new row
    $nVal = 0
    foreach ($c in $rowCells) {
      $d = $c.Duplicate().Item(1)
      $d.Left = [single]$c.Left; $d.Top = [single]($rowTop + $pitch); $d.Width = [single]$c.Width; $d.Height = [single]$c.Height
      $d.Name = 'idle_' + $c.Name
      if ([Math]::Abs($c.Left - $lab.Left) -lt 0.5) {
        $d.Left = [single]($c.Left + 8); $d.Width = [single]($c.Width - 8)
        $d.TextFrame.TextRange.Text = 'of which: idle cost'
        continue
      }
      $cx = $c.Left + $c.Width / 2
      $h = $heads | Where-Object { $cx -ge $_.Left - 0.5 -and $cx -le $_.Left + $_.Width + 0.5 } | Select-Object -First 1
      $y = $years | Where-Object { $cx -ge $_.Left - 1 -and $cx -le $_.Left + $_.Width + 1 } | Select-Object -First 1
      if (-not $h -or -not $y) { throw "slide $sn : no header/year for cell at $($c.Left) (text '$($c.TextFrame.TextRange.Text)')" }
      $ht = $h.TextFrame.TextRange.Text; $yt = $y.TextFrame.TextRange.Text
      $sheet = $(if ($ht -eq 'Total BU') { $totalBU } else { $ENT[$ht] })
      $scen = $YR[$yt]
      $v = $SJ.$sheet.'Idle'.$scen
      if ($null -eq $v) { throw "slide $sn : no Idle value for $sheet / $scen" }
      $d.TextFrame.TextRange.Text = (N0 $v)
      $nVal++
      $log.Add(('s{0} {1,-18} {2,-7} {3,8} -> {4}' -f $sn, $ht, $yt, ('{0:N1}' -f [double]$v), (N0 $v)))
    }
    "slide $sn : pitch $pitch, shifted $nShift, grew $nGrow tint rects, $nVal idle values"
  }

  # ---------------------------------------------------------------- B) slide 6 admin table
  $s = $p.Slides.Item(6)
  $shapes = @(); for ($i = 1; $i -le $s.Shapes.Count; $i++) { $shapes += $s.Shapes.Item($i) }
  # B1 remove the TDC 2.0 row and move the rows below it up
  $tdcRow = @($shapes | Where-Object { $_.HasTextFrame -eq -1 -and $_.TextFrame.TextRange.Text -eq 'of which TDC 2.0' })
  if ($tdcRow.Count -ne 1) { throw 'slide 6: TDC 2.0 row not found' }
  $tTop = $tdcRow[0].Top; $rowH = $tdcRow[0].Height   # 312.5 / 21.7
  $del = @($shapes | Where-Object { $_.Type -ne 14 -and [Math]::Abs($_.Top - $tTop) -lt 0.8 })
  foreach ($d in $del) { $d.Delete() }
  $shapes = @(); for ($i = 1; $i -le $s.Shapes.Count; $i++) { $shapes += $s.Shapes.Item($i) }
  $nUp = 0
  foreach ($sh in $shapes) {
    if ($sh.Type -eq 14) { continue }
    if ($sh.Top -gt $tTop + 0.8 -and $sh.Top -lt 390) { $sh.Top = [single]($sh.Top - $rowH); $nUp++ }   # rows below + the connector; the takeaway box (391) stays
  }
  # B2 re-layout columns: label unchanged (50..226), then 2025 / AP26 / LE26 / AP27 / Change / AP27 Stretch inside 230..606
  $newLeft = @{ '234' = 230.0; '304' = 288.0; '374' = 346.0; '448' = 410.0; '518' = 468.0 }
  $newW = @{ '234' = 56.0; '304' = 56.0; '374' = 62.0; '448' = 56.0; '518' = 70.0 }
  $stretchL = 540.0; $stretchW = 66.0
  $ap27Cells = @{}   # top -> shape (AP27 column) to clone for the stretch column
  foreach ($sh in $shapes) {
    if ($sh.Type -eq 14) { continue }
    $k = [string][int][Math]::Round($sh.Left)
    if ($sh.HasTextFrame -eq -1 -and $newLeft.ContainsKey($k) -and $sh.Top -gt 100 -and $sh.Top -lt 380) {
      if ($k -eq '448') { $rk = [string][int][Math]::Round($sh.Top); $ap27Cells[$rk] = $sh }
      $sh.Left = [single]$newLeft[$k]; $sh.Width = [single]$newW[$k]
      $sh.TextFrame.MarginLeft = 2; $sh.TextFrame.MarginRight = 2
    }
    elseif ($sh.Type -eq 1 -and [Math]::Abs($sh.Left - 444) -lt 0.6 -and $sh.Height -gt 200) { $sh.Left = [single]407; $sh.Width = [single]62 }   # AP27 tint column
  }
  # B3 stretch column: header + one cell per AP27 cell (same formatting as the AP27 cell), TH P / Non-P less the saving
  $sav = @{ P = -[double]$BR.P.Saving; N = -[double]$BR.N.Saving }   # 7.5 / 7.53 (positive = cost saved)
  $a = $A2.admin2.AP27
  $val = [ordered]@{}
  $thP = -[double]$a.adp.Thailand - $sav.P; $inP = -[double]$a.adp.International; $thN = -[double]$a.adn.Thailand - $sav.N; $inN = -[double]$a.adn.International
  $ns = [double]$a.ns
  $stretch = @{
    'P' = $thP + $inP; 'P:Thailand' = $thP; 'P:International' = $inP
    'N' = $thN + $inN; 'N:Thailand' = $thN; 'N:International' = $inN
    'T' = $thP + $inP + $thN + $inN; 'T:Thailand' = $thP + $thN; 'T:International' = $inP + $inN
    'R' = ($thP + $inP + $thN + $inN) / $ns }
  # walk rows top-down and keep a section pointer (P / N / T) to disambiguate 'Thailand' / 'International'
  $labels = @($shapes | Where-Object { $_.Type -eq 17 -and $_.HasTextFrame -eq -1 -and $_.Left -lt 100 -and $_.Top -gt 130 -and $_.Top -lt 380 } | Sort-Object Top)
  $sec = ''
  $hdr = $null
  foreach ($sh in $shapes) { if ($sh.HasTextFrame -eq -1 -and $sh.TextFrame.TextRange.Text -eq 'AP27' -and $sh.Top -lt 120) { $hdr = $sh } }
  $d = $hdr.Duplicate().Item(1); $d.Left = [single]$stretchL; $d.Top = [single]$hdr.Top; $d.Width = [single]$stretchW; $d.Height = [single]$hdr.Height; $d.TextFrame.TextRange.Text = 'AP27 Stretch'; $d.Name = 'stretch_hdr'
  foreach ($lb in $labels) {
    $t = $lb.TextFrame.TextRange.Text
    if ($t -like 'Admin*non-people*') { $sec = 'N'; $key = 'N' } elseif ($t -like 'Admin*people*') { $sec = 'P'; $key = 'P' } elseif ($t -eq 'Total admin') { $sec = 'T'; $key = 'T' }
    elseif ($t -like 'Admin / net sales*') { $key = 'R' } elseif ($t -eq 'Thailand' -or $t -eq 'International') { $key = "$sec`:$t" } else { $key = $t }
    if (-not $stretch.ContainsKey($key)) { throw "slide 6: no stretch value for '$t'" }
    $rk = [string][int][Math]::Round($lb.Top); $srcCell = $ap27Cells[$rk]
    if (-not $srcCell) { throw "slide 6: no AP27 cell on row '$t'" }
    $d = $srcCell.Duplicate().Item(1); $d.Left = [single]$stretchL; $d.Top = [single]$srcCell.Top; $d.Width = [single]$stretchW; $d.Height = [single]$srcCell.Height; $d.Name = 'stretch_' + $srcCell.Name
    $v = $stretch[$key]
    $d.TextFrame.TextRange.Text = $(if ($key -eq 'R') { ('{0:N1}%' -f ($v * 100)) } else { ('{0:N0}' -f $v) })
    $log.Add(('s6 stretch {0,-28} {1}' -f $key, $d.TextFrame.TextRange.Text))
  }
  "slide 6 : TDC row removed ($($del.Count) shapes), $nUp shapes moved up, stretch column added; total admin stretch = " + ('{0:N2}' -f $stretch['T'])

  # ---------------------------------------------------------------- C) slides 7-8 waterfalls
  function F1($x) { return ('{0:N1}' -f [double]$x) }
  function SG1($x) { $q = [double]$x; if ([Math]::Abs($q) -lt 0.05) { return '0.0' }; if ($q -gt 0) { return ('+{0:N1}' -f $q) }; return ('({0:N1})' -f (-$q)) }
  function F0($x) { return ('{0:N0}' -f (RoundAway $x)) }
  function SG0($x) { $q = RoundAway $x; if ($q -eq 0) { return '0' }; if ($q -gt 0) { return ('+{0:N0}' -f $q) }; return ('({0:N0})' -f (-$q)) }
  $ARROW = [string][char]0x2192
  foreach ($sn in 7, 8) {
    $s = $p.Slides.Item($sn)
    $B = $(if ($sn -eq 7) { $BR.P } else { $BR.N }); $nm = $(if ($sn -eq 7) { 'Admin P' } else { 'Admin Non-P' })
    $map = @{}
    foreach ($pr in $B.PSObject.Properties) {
      $v = [double]$pr.Value
      foreach ($pair in @(@((F1 $v), (F0 $v)), @((SG1 $v), (SG0 $v)))) {
        if ($map.ContainsKey($pair[0]) -and $map[$pair[0]] -ne $pair[1]) { throw "slide $sn : token $($pair[0]) maps to both $($map[$pair[0]]) and $($pair[1])" }
        $map[$pair[0]] = $pair[1]
      }
    }
    $LE = [double]$B.'LE 2026'; $RP = [double]$B.'AP 2027 Reporting'
    $newTitle = ($nm + ' (Thailand): ' + (F0 $LE) + ' ' + $ARROW + ' ' + (F0 $RP) + ' MB in AP 2027, ' + (SG0 ($RP - $LE)) + ' MB / ' + (SG0 (($RP - $LE) / $LE * 100)) + '%')
    $newRecon = ('LE 2026 ' + (F0 $LE) + ' and AP 2027 Reporting ' + (F0 $RP) + ' MB are the ' + $nm + ' Thailand line on p.6 (' + (F0 $LE) + ' ' + $ARROW + ' ' + (F0 $RP) + '); Thailand + International = TWPC (ConsoAll).')
    $nFill = 0; $nCol = 0; $nNum = 0
    for ($i = 1; $i -le $s.Shapes.Count; $i++) {
      $sh = $s.Shapes.Item($i)
      if ($sh.Type -eq 1) {
        $f = $sh.Fill.ForeColor.RGB
        if ($f -eq $OLD_TOT) { $sh.Fill.ForeColor.RGB = $NAVY; $nFill++ }
        elseif ($f -eq $OLD_RED) { $sh.Fill.ForeColor.RGB = $CYAN; $nFill++ }
        elseif ($f -eq $OLD_GREEN) { $sh.Fill.ForeColor.RGB = $LCYAN; $nFill++ }
      }
      if ($sh.HasTextFrame -ne -1) { continue }
      $tr = $sh.TextFrame.TextRange
      $c = $tr.Font.Color.RGB
      if ($c -eq $OLD_RED -or $c -eq $OLD_GREEN) { $tr.Font.Color.RGB = $TEXT; $nCol++ }
      $t = $tr.Text
      $new = $t
      if ($sh.Type -eq 14 -and $t -like ($nm + ' (Thailand)*')) { $new = $newTitle }
      elseif ($t -like 'LE 2026 * are the *') { $new = $newRecon }
      elseif ($t -eq 'TIES TO P.7') { $new = 'TIES TO P.6' }
      elseif ($t -like 'Source:*') { $new = $t.Replace('THB million, 1 decimal.', 'THB million, rounded to whole numbers.') }
      elseif ($t -match '\d\.\d') {
        $new = [regex]::Replace($t, '(?<!TDC ?)[+(]?\d{1,3}(?:,\d{3})*\.\d\)?', { param($m) if ($map.ContainsKey($m.Value)) { return $map[$m.Value] }; throw "slide $sn : unmapped token '$($m.Value)' in '$t'" })
      }
      if ($new -ne $t) { $tr.Text = $new; $nNum++; if ($t.Length -gt 12) { $log.Add("s$sn text: '$t' -> '$new'") } }
      if ($new -match '(?<!TDC ?)\d\.\d') { throw "slide $sn : decimal left in '$new'" }
    }
    "slide $sn : $nFill fills, $nCol text colours, $nNum texts rounded; title = $newTitle"
  }

  $p.Save()
  if ($PngDir) {
    New-Item -ItemType Directory -Force $PngDir | Out-Null
    foreach ($n in 4, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16) { $p.Slides.Item($n).Export((Join-Path $PngDir ('s{0:D2}.png' -f $n)), 'PNG', 1600, 900) }
  }
  "saved: $Out  slides " + $p.Slides.Count
} finally { $p.Close() }
$log | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'edit_v5.log') -Encoding UTF8
"log lines: " + $log.Count
