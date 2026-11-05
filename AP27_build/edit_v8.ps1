param([string]$DeckIn, [string]$DeckOut, [string]$PngDir, [string]$SheetsJson)
# v8 = copy of v7; slide 3: numeric columns move 56pt left (label column narrower) and a '2028 AP' OPBA column is added after 'AP27 vs LE26'
$ErrorActionPreference = 'Stop'
$SJ = Get-Content -LiteralPath $SheetsJson -Encoding UTF8 -Raw | ConvertFrom-Json
$DASH = [string][char]0x2013
function N0($x) { $v = [double]$x; if ([Math]::Abs($v) -lt 0.5) { return $DASH }; if ($v -lt 0) { return ('({0:N0})' -f (-$v)) }; return ('{0:N0}' -f $v) }
function V($sheet, $scen) { $x = $SJ.$sheet.'OP Before Admin'.$scen; if ($null -eq $x) { throw "no value $sheet / $scen" }; return [double]$x }
$ROW3 = @{ 'Food BU' = @('FoodBU'); 'Food TH' = @('FoodTH'); 'Well Grow' = @('FoodWG'); 'Food VN' = @('FoodVN'); 'HVA BU incl. Waxy' = @('HVA incl Waxy'); 'TDC' = @('TDC'); 'TDC 2.0' = @('TDC2.0'); 'TWIN' = @('TWIN'); 'TWII' = @('TWII'); 'Waxy' = @('Waxy'); 'memo: HVA excl. Waxy' = @('HVABU')
           'Starch BU' = @('StarchBU'); 'Starch TH' = @('StarchTH'); 'China' = @('TotalCN'); 'TWIT' = @('TWIT'); 'TWFZ' = @('TWFZ'); 'Cambodia (TWIC)' = @('TWIC'); 'Vietnam (TNT+VTC)' = @('TotalVN'); 'NBG BU' = @('NBGBU'); 'Bioplastic' = @('BioPlastic'); 'Discontinued (feed, AgBio, V9)' = @('AnimalFeeds', 'AgBio', 'V9'); 'TWPC total' = @('ConsoAll') }
$SHIFT = 56.0; $NEWL = 548.0; $NEWW = 48.0
Copy-Item -LiteralPath $DeckIn -Destination $DeckOut -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($DeckOut, 0, 0, 0)
try {
  $s = $pres.Slides.Item(3)
  $shapes = @(); for ($i = 1; $i -le $s.Shapes.Count; $i++) { $shapes += $s.Shapes.Item($i) }
  $hdr27 = $null; $ap27Cells = @{}; $labels = @(); $nShift = 0
  foreach ($sh in $shapes) {
    if ($sh.Type -eq 14 -or $sh.Type -eq 7) { continue }
    if ($sh.Type -eq 1 -and $sh.Width -gt 250) { continue }                       # cards / total-row tint (full width)
    if ($sh.Type -eq 9) { continue }                                               # row connectors keep their span
    if ($sh.Left -ge 620) { continue }                                             # right card
    if ($sh.Type -eq 17) {
      $t = $sh.TextFrame.TextRange.Text
      if ($sh.Left -lt 100) {                                                      # label column: narrower
        if ($sh.Top -gt 100 -and $ROW3.ContainsKey($t.Trim())) { $labels += $sh }
        continue
      }
      if ($t -eq '2027 AP' -and $sh.Top -lt 100) { $hdr27 = $sh }
      if ([Math]::Abs($sh.Left - 464) -lt 0.6 -and $sh.Top -gt 100) { $rk = [string][int][Math]::Round($sh.Top); $ap27Cells[$rk] = $sh }
    }
    if ($sh.Left -ge 200) {
      $sh.Left = [single]($sh.Left - $SHIFT); $nShift++
      if ($sh.Type -eq 1 -and $sh.Line.Visible -eq -1 -and $sh.Width -gt 150) { $sh.Width = [single](546 - $sh.Left) }   # Por's dashed highlight boxes: end before the new column
    }
  }
  if (-not $hdr27 -or $labels.Count -lt 20) { throw "slide 3: header or rows not found ($($labels.Count))" }
  $d = $hdr27.Duplicate().Item(1); $d.Left = [single]$NEWL; $d.Top = [single]$hdr27.Top; $d.Width = [single]$NEWW; $d.Height = [single]$hdr27.Height; $d.TextFrame.TextRange.Text = '2028 AP'; $d.Name = 'hdr_2028'
  $out = @()
  foreach ($lb in ($labels | Sort-Object Top)) {
    $label = $lb.TextFrame.TextRange.Text.Trim()
    $rk = [string][int][Math]::Round($lb.Top); $src27 = $ap27Cells[$rk]
    if (-not $src27) { throw "slide 3: no 2027 cell for '$label'" }
    $v = 0.0; foreach ($x in $ROW3[$label]) { $v += V $x 'AP28' }
    $d = $src27.Duplicate().Item(1); $d.Left = [single]$NEWL; $d.Top = [single]$src27.Top; $d.Width = [single]$NEWW; $d.Height = [single]$src27.Height; $d.TextFrame.TextRange.Text = (N0 $v); $d.Name = 'ap28_' + $src27.Name
    $out += ('{0,-32} {1,8}' -f $label, (N0 $v))
  }
  "shifted $nShift shapes; added header + $($out.Count) cells"
  $out
  # tie: TWPC AP28 = ConsoAll
  "ConsoAll AP28 OPBA = " + ('{0:N1}' -f (V 'ConsoAll' 'AP28'))
  $pres.Save()
  if ($PngDir) { New-Item -ItemType Directory -Force $PngDir | Out-Null; $s.Export((Join-Path $PngDir 's03.png'), 'PNG', 1600, 900) }
  "saved $DeckOut"
} finally { $pres.Close() }
