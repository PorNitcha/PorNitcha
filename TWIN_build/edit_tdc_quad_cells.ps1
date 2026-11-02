# Edit TDC quadrant mini tables in place on one slide of Por's saved deck: header count, Vol share, GP share, GP/kg from deck_data.json (keeps Por's formatting)
# Keeps every manual edit Por made (text runs are replaced, not rebuilt). Usage: powershell -File edit_page2_actual_gp.ps1 <src.pptx> <out.pptx> <deck_data.json>
param([string]$Src, [string]$Out, [string]$Json, [int]$SlideNo = 2, [double]$X0a = 70, [double]$X0b = 530, [double]$TopSplit = 180)
if (Get-Process POWERPNT -ErrorAction SilentlyContinue) { Write-Output 'STOP: PowerPoint is open. Close it first.'; exit 2 }
$D = Get-Content -LiteralPath $Json -Encoding UTF8 -Raw | ConvertFrom-Json
Copy-Item -LiteralPath $Src -Destination $Out -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Out, 0, 0, 0)
$sl = $pres.Slides.Item($SlideNo)
function Pct($x) { if ($null -eq $x -or [double]$x -eq 0) { return [string][char]0x2013 }; if ([math]::Abs([double]$x) -lt 0.005) { return '<1%' }; return ('{0:N0}%' -f ([double]$x * 100)) }
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
  $hc = $t.Cell(1, 1).Shape.TextFrame.TextRange; $oldh = $hc.Text.Trim()
  if ($oldh -ne '') { $newh = $(if ($v.nproxy -gt 0) { "$($v.n) accts " + [char]0x00B7 + " $($v.nproxy) new" } else { "$($v.n) accounts" }); if ($oldh -ne $newh) { $hc.Text = $newh; $log += "$base $role header : $oldh -> $newh" } }
  for ($r = 2; $r -le $t.Rows.Count; $r++) {
    $lab = $t.Cell($r, 1).Shape.TextFrame.TextRange.Text.Trim()
    if ($lab -like 'Total*') { $rowv = $v.total } elseif ($lab -eq 'Indonesia direct') { $rowv = $v.direct } elseif ($lab -eq 'via TWIN') { $rowv = $v.twin } else { continue }
    if ($t.Cell($r, 2).Shape.TextFrame.TextRange.Text.Trim() -eq [string][char]0x2013 -and (Pct $rowv.v) -eq '<1%') { continue }   # Por blanked this tiny row: leave the whole row
    foreach ($cc in @(@(2, (Pct $rowv.v)), @(3, (Pct $rowv.g)), @(4, (Fmt1 $rowv.kg)))) {
      $tr = $t.Cell($r, $cc[0]).Shape.TextFrame.TextRange; $old = $tr.Text.Trim(); $new = $cc[1]
      if ($old -ne $new -and $old -ne '' -and -not ($old -eq [string][char]0x2013 -and $new -eq '<1%')) {   # keep Por's blanked tiny rows
        $tr.Text = $new; $log += "$base $role $lab c$($cc[0]) : $old -> $new"
        # a grey (empty) Indonesia row that now has data takes the Indonesia blue (Por's colour)
        if ($lab -ne 'Total TDC' -and $lab -notlike 'Total*' -and $new -ne [string][char]0x2013 -and $tr.Font.Color.RGB -eq 11510684) {
          for ($c2 = 1; $c2 -le 4; $c2++) { $f = $t.Cell($r, $c2).Shape.TextFrame.TextRange.Font; if ($f.Color.RGB -eq 11510684) { $f.Color.RGB = 8544277 } }
        }
      }
    }
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
