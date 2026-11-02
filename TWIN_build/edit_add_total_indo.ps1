# In place: add a "Total Indonesia" row (direct + via TWIN) above the Indonesia rows of every TDC quadrant mini table on one slide (Por 30-Oct).
# Copies the formatting of the Indonesia row below it, keeps Por's blanked rows blank, and moves the lines under the table down by one row.
# Usage: edit_add_total_indo.ps1 <in.pptx> <out.pptx> <deck_actual_avg.json> <slide> <x0 left box> <x0 right box> <top split> <max px below table to shift>
param([string]$InFile, [string]$OutFile, [string]$Json, [int]$SlideNo, [double]$X0a, [double]$X0b, [double]$TopSplit, [double]$MaxBelow)
if (Get-Process POWERPNT -ErrorAction SilentlyContinue) { Write-Output 'STOP: PowerPoint is open. Close it first.'; exit 2 }
$D = Get-Content -LiteralPath $Json -Encoding UTF8 -Raw | ConvertFrom-Json
$DASH = [string][char]0x2013; $BLUE = 8544277; $GREYC = 11510684
function Pct($x) { if ($null -eq $x -or [double]$x -eq 0) { return $DASH }; if ([math]::Abs([double]$x) -lt 0.005) { return '<1%' }; return ('{0:N0}%' -f ([double]$x * 100)) }
function Fmt1($x) { if ($null -eq $x) { return $DASH }; return ('{0:N1}' -f [double]$x) }
Copy-Item -LiteralPath $InFile -Destination $OutFile -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($OutFile, 0, 0, 0)
$sl = $pres.Slides.Item($SlideNo)
$tables = @(); foreach ($sh in $sl.Shapes) { if ($sh.HasTable -and $sh.Table.Columns.Count -eq 4 -and $sh.Table.Cell(1, 4).Shape.TextFrame.TextRange.Text.Trim() -eq 'GP/kg') { $tables += $sh } }
foreach ($sh in $tables) {
  $t = $sh.Table
  $base = $(if ($sh.Left -lt 480) { '25' } else { '26' })
  $leftCol = (($sh.Left - $(if ($base -eq '25') { $X0a } else { $X0b })) -lt 100)
  $role = $(if ($sh.Top -lt $TopSplit) { $(if ($leftCol) { 'protect' } else { 'grow' }) } else { $(if ($leftCol) { 'reprice' } else { 'fix' }) })
  $v = $D.tdcq.PSObject.Properties[$base].Value.roles.PSObject.Properties[$role].Value
  $idx = @(); for ($r = 2; $r -le $t.Rows.Count; $r++) { $lab = $t.Cell($r, 1).Shape.TextFrame.TextRange.Text.Trim(); if ($lab -eq 'Indonesia direct' -or $lab -eq 'via TWIN') { $idx += $r } ; if ($lab -eq 'Total Indonesia') { $idx = @(-1); break } }
  if ($idx.Count -eq 0) { "$base $role : no Indonesia rows (Por removed them) - skipped"; continue }
  if ($idx[0] -eq -1) { "$base $role : already has Total Indonesia - skipped"; continue }
  $allBlank = $true; foreach ($r in $idx) { if ($t.Cell($r, 2).Shape.TextFrame.TextRange.Text.Trim() -ne $DASH) { $allBlank = $false } }
  $src = $idx[0]; $h0 = $sh.Height; $bottom0 = $sh.Top + $sh.Height
  $null = $t.Rows.Add($src); $new = $src; $src = $src + 1
  $vals = $(if ($allBlank) { @('Total Indonesia', $DASH, $DASH, $DASH) } else { @('Total Indonesia', (Pct $v.indo.v), (Pct $v.indo.g), (Fmt1 $v.indo.kg)) })
  $col = $(if ($vals[1] -eq $DASH) { $GREYC } else { $BLUE })
  for ($c = 1; $c -le 4; $c++) {
    $s = $t.Cell($src, $c).Shape; $n = $t.Cell($new, $c).Shape
    $n.TextFrame.TextRange.Text = $vals[$c - 1]
    $f = $n.TextFrame.TextRange.Font; $f.Name = $s.TextFrame.TextRange.Font.Name; $f.Size = $t.Cell($src, 1).Shape.TextFrame.TextRange.Font.Size; $f.Bold = $s.TextFrame.TextRange.Font.Bold; $f.Color.RGB = $col
    $n.TextFrame.TextRange.ParagraphFormat.Alignment = $s.TextFrame.TextRange.ParagraphFormat.Alignment
    $n.TextFrame.MarginLeft = $s.TextFrame.MarginLeft; $n.TextFrame.MarginRight = $s.TextFrame.MarginRight; $n.TextFrame.MarginTop = $s.TextFrame.MarginTop; $n.TextFrame.MarginBottom = $s.TextFrame.MarginBottom
    $n.TextFrame.VerticalAnchor = $s.TextFrame.VerticalAnchor
    $n.Fill.Visible = $s.Fill.Visible
    foreach ($b in 1,2,3,4) { $t.Cell($new, $c).Borders.Item($b).Visible = 0 }
  }
  $t.Rows.Item($new).Height = $t.Rows.Item($src).Height
  $dh = $sh.Height - $h0
  # move the lines under this table (names, via TWIN GP/kg) down by the added height
  foreach ($o in $sl.Shapes) { if (-not $o.HasTable -and $o.HasTextFrame -and $o.TextFrame.TextRange.Text.Trim() -ne '' -and $o.Type -eq 17 -and [math]::Abs($o.Left - $sh.Left) -lt 15 -and $o.Width -le $sh.Width + 20 -and $o.Top -ge $bottom0 - 3 -and $o.Top -lt $bottom0 + $MaxBelow) { $o.Top = $o.Top + $dh } }   # only text lines right under the table
  "$base $role : added Total Indonesia " + ($vals -join ' | ') + "  (+$([math]::Round($dh,1)) pt)"
}
$pres.Save(); $sl.Export(($OutFile -replace '\.pptx$', "_p$SlideNo.png"), 'PNG', 1920, 1080)
$pres.Close(); $app.Quit()
