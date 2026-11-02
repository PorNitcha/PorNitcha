# In-place text replace on given slides of a deck (keeps formatting). Usage: edit_replace_text.ps1 <in.pptx> <out.pptx> <find> <replace> <slide numbers comma-separated>
param([string]$InFile, [string]$OutFile, [string]$FindText, [string]$ReplText, [string]$Slides)
if (Get-Process POWERPNT -ErrorAction SilentlyContinue) { Write-Output 'STOP: PowerPoint is open. Close it first.'; exit 2 }
Copy-Item -LiteralPath $InFile -Destination $OutFile -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($OutFile, 0, 0, 0)
foreach ($n in ($Slides -split ',')) {
  foreach ($sh in $pres.Slides.Item([int]$n).Shapes) {
    if (-not $sh.HasTextFrame) { continue }
    $res = $sh.TextFrame.TextRange.Replace($FindText, $ReplText)
    if ($null -ne $res) { "slide $n : replaced in '$($sh.Name)'" }
  }
}
$pres.Save()
foreach ($n in ($Slides -split ',')) { $pres.Slides.Item([int]$n).Export(($OutFile -replace '\.pptx$', "_p$n.png"), 'PNG', 1920, 1080) }
$pres.Close(); $app.Quit()
