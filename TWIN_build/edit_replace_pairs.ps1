# In-place text replacements from a JSON list of [find, replace] pairs on given slides (keeps formatting).
# Usage: edit_replace_pairs.ps1 <in.pptx> <out.pptx> <pairs.json> <slides comma-separated>
param([string]$InFile, [string]$OutFile, [string]$PairsFile, [string]$Slides)
if (Get-Process POWERPNT -ErrorAction SilentlyContinue) { Write-Output 'STOP: PowerPoint is open. Close it first.'; exit 2 }
$pairs = Get-Content -LiteralPath $PairsFile -Raw | ConvertFrom-Json
Copy-Item -LiteralPath $InFile -Destination $OutFile -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($OutFile, 0, 0, 0)
$hit = @{}
foreach ($n in ($Slides -split ',')) {
  foreach ($sh in $pres.Slides.Item([int]$n).Shapes) {
    if (-not $sh.HasTextFrame) { continue }
    for ($k = 0; $k -lt $pairs.Count; $k++) {
      $res = $sh.TextFrame.TextRange.Replace([string]$pairs[$k][0], [string]$pairs[$k][1])
      if ($null -ne $res) { $hit[$k] = 1 + [int]$hit[$k]; "slide $n pair $k replaced in '$($sh.Name)'" }
    }
  }
}
for ($k = 0; $k -lt $pairs.Count; $k++) { if (-not $hit.ContainsKey($k)) { "pair $k NOT FOUND" } }
$pres.Save()
foreach ($n in ($Slides -split ',')) { $pres.Slides.Item([int]$n).Export(($OutFile -replace '\.pptx$', "_p$n.png"), 'PNG', 1920, 1080) }
$pres.Close(); $app.Quit()
