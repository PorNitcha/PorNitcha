# Edit ONLY page 2 of Por's saved deck in place: TDC quadrant GP/kg -> actual base-year product GP at actual tonnes (Por 29-Oct)
# Keeps every manual edit Por made (text runs are replaced, not rebuilt). Usage: powershell -File edit_page2_actual_gp.ps1 <src.pptx> <out.pptx> <deck_data.json>
param([string]$Src, [string]$Out, [string]$Json, [int]$SlideNo = 2, [double]$X0a = 70, [double]$X0b = 530, [double]$TopSplit = 180)
if (Get-Process POWERPNT -ErrorAction SilentlyContinue) { Write-Output 'STOP: PowerPoint is open. Close it first.'; exit 2 }
$D = Get-Content -LiteralPath $Json -Encoding UTF8 -Raw | ConvertFrom-Json
Copy-Item -LiteralPath $Src -Destination $Out -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Out, 0, 0, 0)
$sl = $pres.Slides.Item($SlideNo)
function Fmt1($x) { if ($null -eq $x) { return [string][char]0x2013 }; return ('{0:N1}' -f [double]$x) }
$log = @()
foreach ($sh in $sl.Shapes) {
  if (-not $sh.HasTable) { continue }
  $t = $sh.Table
  if ($t.Columns.Count -ne 4 -or $t.Cell(1, 4).Shape.TextFrame.TextRange.Text.Trim() -ne 'GP/kg') { continue }   # TDC mini tables only
  $base = $(if ($sh.Left -lt 480) { '25' } else { '26' })
  $leftCol = (($sh.Left - $(if ($base -eq '25') { $X0a } else { $X0b })) -lt 100)
  $upper = ($sh.Top -lt $TopSplit)
  $role = $(if ($upper) { $(if ($leftCol) { 'protect' } else { 'grow' }) } else { $(if ($leftCol) { 'reprice' } else { 'fix' }) })
  $v = $D.tdcq.PSObject.Properties[$base].Value.roles.PSObject.Properties[$role].Value
  for ($r = 2; $r -le $t.Rows.Count; $r++) {
    $lab = $t.Cell($r, 1).Shape.TextFrame.TextRange.Text.Trim()
    if ($lab -like 'Total*') { $rowv = $v.total } elseif ($lab -eq 'Indonesia direct') { $rowv = $v.direct } elseif ($lab -eq 'via TWIN') { $rowv = $v.twin } else { continue }
    $tr = $t.Cell($r, 4).Shape.TextFrame.TextRange; $old = $tr.Text.Trim(); $new = Fmt1 $rowv.kg
    if ($old -ne $new -and $old -ne [string][char]0x2013 -and $old -ne '') { $tr.Text = $new; $log += "$base $role $lab : $old -> $new" }
  }
}
# wording: subtitle and TDC footnote
$pairs = @(
  @('GP/kg = base-year product GP in THB/kg at TDC level (floor 4.7)', 'GP/kg = actual product GP in THB/kg at actual tonnes of each year, TDC level (floor 4.7)'),
  @('), placed as growing at own other-year GP/kg or the base-year average GP/kg of their planned SKUs', '): placed as growing, using own other-year or planned-SKU average GP/kg for shares only; excluded from the GP/kg column'),
  @('GP/kg = base-year product GP in THB/kg at TDC level;', 'GP/kg = actual base-year product GP in THB/kg at actual base-year tonnes, TDC level;'),
  @('of plan volume at 4.2 THB/kg)', 'of plan volume at 4.3 THB/kg)')
)
foreach ($sh in $sl.Shapes) {
  if (-not $sh.HasTextFrame) { continue }
  foreach ($p in $pairs) { $res = $sh.TextFrame.TextRange.Replace($p[0], $p[1]); if ($null -ne $res) { $log += "text: " + $p[0].Substring(0, [math]::Min(30, $p[0].Length)) + '...' } }
}
$pres.Save()
$pres.Slides.Item($SlideNo).Export(($Out -replace '\.pptx$', "_p$SlideNo.png"), 'PNG', 1920, 1080)
$pres.Close(); $app.Quit()
$log
