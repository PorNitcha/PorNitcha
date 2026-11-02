# In-place fix of the CASSTEX-22 bullet on page 1 (Por 30-Oct): SN-365 non-Indonesia benchmark is 87% Barentz Turkey (bidding), not a market benchmark
# Usage: powershell -File edit_p1_casstex_bullet.ps1 <src.pptx> <out.pptx>
param([string]$InFile, [string]$OutFile)
if (Get-Process POWERPNT -ErrorAction SilentlyContinue) { Write-Output 'STOP: PowerPoint is open. Close it first.'; exit 2 }
$en = [string][char]0x2013; $minus = [string][char]0x2212; $ap = [string][char]0x2019
$find = 'CASSTEX-22 (XL) is 0.4' + $en + '0.7 THB/kg for everyone: bidding customers to Barentz Gida, not an Indonesia price problem.'   # Por's v5 wording (30-Oct 09:07)
$repl = 'CASSTEX-22 (XL): 0.4' + $en + '0.7 THB/kg only with bidding customers (Barentz Gida, 87% of the non-Indonesia benchmark, and Indonesia). Other non-Indonesian buyers (174 t) earn about 6.2 THB/kg, so the gap is bidding price, not product cost.'
Copy-Item -LiteralPath $InFile -Destination $OutFile -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($OutFile, 0, 0, 0)
$n = 0
foreach ($sh in $pres.Slides.Item(1).Shapes) {
  if (-not $sh.HasTextFrame) { continue }
  $res = $sh.TextFrame.TextRange.Replace($find, $repl)
  if ($null -ne $res) { $n++; "replaced in shape '$($sh.Name)' top=$($sh.Top.ToString('0')) height now=$($sh.Height.ToString('0'))" }
}
if ($n -eq 0) { 'NOT FOUND' }
$pres.Save()
$pres.Slides.Item(1).Export(($OutFile -replace '\.pptx$', '_p1.png'), 'PNG', 1920, 1080)
$pres.Close(); $app.Quit()
