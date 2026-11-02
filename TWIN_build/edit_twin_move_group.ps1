# In place: move one TWIN customer group (e.g. Heinz) from the 2025 GROW box to the 2025 FIX box of a TWIN-customer quadrant (Por 30-Oct: line = base-year average).
# Duplicates the Grow mini table into the Fix cell (keeps Por's formatting), deletes the other rows in each copy, removes the '–' placeholder in Fix,
# and splits the tonnage line under the tables when there is one (page 4).
# Usage: edit_twin_move_group.ps1 <in.pptx> <out.pptx> <slide> <boxX0> <boxY0> <boxW> <boxH> <group>
param([string]$InFile, [string]$OutFile, [int]$SlideNo, [double]$X0, [double]$Y0, [double]$BW, [double]$BH, [string]$Group)
if (Get-Process POWERPNT -ErrorAction SilentlyContinue) { Write-Output 'STOP: PowerPoint is open. Close it first.'; exit 2 }
Copy-Item -LiteralPath $InFile -Destination $OutFile -Force
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($OutFile, 0, 0, 0)
$sl = $pres.Slides.Item($SlideNo)
$cw = $BW / 2; $ch = $BH / 2
$inGrow = { param($s) $s.Left -ge ($X0 + $cw - 2) -and $s.Left -lt ($X0 + $BW) -and $s.Top -ge ($Y0 - 2) -and $s.Top -lt ($Y0 + $ch) }
$inFix  = { param($s) $s.Left -ge ($X0 + $cw - 2) -and $s.Left -lt ($X0 + $BW) -and $s.Top -ge ($Y0 + $ch - 2) -and $s.Top -lt ($Y0 + $BH) }
$grow = $null; $dash = $null; $ton = $null
foreach ($sh in $sl.Shapes) {
  if ($sh.HasTable -and (& $inGrow $sh) -and $sh.Table.Columns.Count -eq 6) { $grow = $sh }
  elseif ($sh.HasTextFrame -and (& $inFix $sh) -and $sh.TextFrame.TextRange.Text.Trim() -eq [string][char]0x2013) { $dash = $sh }
  elseif ($sh.HasTextFrame -and (& $inGrow $sh) -and $sh.TextFrame.TextRange.Text -like "*$Group*(prev*") { $ton = $sh }
}
if ($null -eq $grow) { 'GROW TABLE NOT FOUND'; $pres.Close(); $app.Quit(); exit 3 }
$t = $grow.Table; $rowG = 0
for ($r = 2; $r -le $t.Rows.Count; $r++) { if ($t.Cell($r, 1).Shape.TextFrame.TextRange.Text.Trim() -eq $Group) { $rowG = $r } }
if ($rowG -eq 0) { "GROUP $Group NOT IN GROW TABLE"; $pres.Close(); $app.Quit(); exit 3 }
$dup = $grow.Duplicate().Item(1); $dup.Left = $grow.Left; $dup.Top = $grow.Top + $ch
# Fix copy keeps only the group; Grow keeps everything else
for ($r = $dup.Table.Rows.Count; $r -ge 2; $r--) { if ($dup.Table.Cell($r, 1).Shape.TextFrame.TextRange.Text.Trim() -ne $Group) { $dup.Table.Rows.Item($r).Delete() } }
$t.Rows.Item($rowG).Delete()
$t.Cell(1, 1).Shape.TextFrame.TextRange.Text = "$($t.Rows.Count - 1) group(s)"
$dup.Table.Cell(1, 1).Shape.TextFrame.TextRange.Text = "$($dup.Table.Rows.Count - 1) group(s)"
"grow table now $($t.Rows.Count - 1) row(s); fix table $($dup.Table.Rows.Count - 1) row(s)"
if ($null -ne $dash) { $dash.Delete(); 'removed placeholder in Fix' }
if ($null -ne $ton) {
  $parts = $ton.TextFrame.TextRange.Text -split ([string][char]0x00B7)
  $mine = ($parts | Where-Object { $_.Trim() -like "$Group *" } | ForEach-Object { $_.Trim() }) -join ''
  $rest = ($parts | Where-Object { $_.Trim() -notlike "$Group *" } | ForEach-Object { $_.Trim() }) -join ([string][char]0x00B7 + ' ')
  $t2 = $ton.Duplicate().Item(1); $t2.Left = $ton.Left
  $ton.TextFrame.TextRange.Text = $rest; $ton.Top = $grow.Top + $grow.Height + 3
  $t2.TextFrame.TextRange.Text = $mine; $t2.Top = $dup.Top + $dup.Height + 3
  "tonnage lines: grow '$rest' | fix '$mine'"
}
$pres.Save(); $sl.Export(($OutFile -replace '\.pptx$', "_p$SlideNo.png"), 'PNG', 1920, 1080)
$pres.Close(); $app.Quit()
