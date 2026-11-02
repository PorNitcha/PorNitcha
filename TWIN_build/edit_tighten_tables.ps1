# In place: tighten the TDC quadrant mini tables on one slide (zero top/bottom cell padding, minimum row height) and keep the text lines under each table attached to it.
# Usage: edit_tighten_tables.ps1 <in.pptx> <out.pptx> <slide>
param([string]$InFile, [string]$OutFile, [int]$SlideNo)
if (Get-Process POWERPNT -ErrorAction SilentlyContinue) { Write-Output 'STOP: PowerPoint is open. Close it first.'; exit 2 }
Copy-Item -LiteralPath $InFile -Destination $OutFile -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($OutFile, 0, 0, 0)
$sl = $pres.Slides.Item($SlideNo)
$tables = @(); foreach ($sh in $sl.Shapes) { if ($sh.HasTable -and $sh.Table.Columns.Count -eq 4 -and $sh.Table.Cell(1, 4).Shape.TextFrame.TextRange.Text.Trim() -eq 'GP/kg') { $tables += $sh } }
foreach ($sh in $tables) {
  $t = $sh.Table; $bottom0 = $sh.Top + $sh.Height
  $below = @(); foreach ($o in $sl.Shapes) { if (-not $o.HasTable -and $o.Type -eq 17 -and $o.HasTextFrame -and $o.TextFrame.TextRange.Text.Trim() -ne '' -and $o.TextFrame.TextRange.Text.Trim() -notmatch '^(PROTECT|GROW WITH MARGIN|REPRICE / EXIT|FIX PRICE BEFORE VOLUME)$' -and [math]::Abs($o.Left - $sh.Left) -lt 15 -and $o.Width -le $sh.Width + 20 -and $o.Top -ge $bottom0 - 3 -and $o.Top -lt $bottom0 + 25) { $below += ,@($o, ($o.Top - $bottom0)) } }
  for ($r = 1; $r -le $t.Rows.Count; $r++) { for ($c = 1; $c -le $t.Columns.Count; $c++) { $tf = $t.Cell($r, $c).Shape.TextFrame; $tf.MarginTop = [single]0; $tf.MarginBottom = [single]0 }; $t.Rows.Item($r).Height = [single]1 }
  $bottom1 = $sh.Top + $sh.Height
  foreach ($p in $below) { $p[0].Top = [single]($bottom1 + [math]::Max(1, $p[1])) }
  "table at $([math]::Round($sh.Left)),$([math]::Round($sh.Top)) : height $([math]::Round($bottom0 - $sh.Top,1)) -> $([math]::Round($sh.Height,1)), moved $($below.Count) line(s)"
}
$pres.Save(); $sl.Export(($OutFile -replace '\.pptx$', "_p$SlideNo.png"), 'PNG', 1920, 1080)
$pres.Close(); $app.Quit()
