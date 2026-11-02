# In TDC mini tables (header GP/kg) on one slide: any value cell smaller than its row label gets the label's font size (for dash cells Por shrank that now hold numbers)
param([string]$InFile, [string]$OutFile, [int]$SlideNo)
if (Get-Process POWERPNT -ErrorAction SilentlyContinue) { Write-Output 'STOP: PowerPoint is open. Close it first.'; exit 2 }
Copy-Item -LiteralPath $InFile -Destination $OutFile -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($OutFile, 0, 0, 0)
foreach ($sh in $pres.Slides.Item($SlideNo).Shapes) {
  if (-not $sh.HasTable) { continue }; $t = $sh.Table
  if ($t.Columns.Count -ne 4 -or $t.Cell(1, 4).Shape.TextFrame.TextRange.Text.Trim() -ne 'GP/kg') { continue }
  for ($r = 2; $r -le $t.Rows.Count; $r++) {
    $ls = $t.Cell($r, 1).Shape.TextFrame.TextRange.Font.Size
    for ($c = 2; $c -le 4; $c++) { $tr = $t.Cell($r, $c).Shape.TextFrame.TextRange
      if ($tr.Text.Trim() -match '\d' -and $tr.Font.Size -lt $ls) { "row $r col $c : $($tr.Text.Trim()) size $($tr.Font.Size) -> $ls"; $tr.Font.Size = $ls } }
  }
}
$pres.Save(); $pres.Slides.Item($SlideNo).Export(($OutFile -replace '\.pptx$', "_p$SlideNo.png"), 'PNG', 1920, 1080)
$pres.Close(); $app.Quit()
