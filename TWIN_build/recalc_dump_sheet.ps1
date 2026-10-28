# Recalc, error-scan, save, and dump one sheet's used range (first N rows x M cols) to JSON
param([string]$Path, [string]$Sheet, [int]$Rows, [int]$Cols, [string]$OutJson)
$x = New-Object -ComObject Excel.Application
$x.Visible = $false; $x.DisplayAlerts = $false
$wb = $x.Workbooks.Open($Path)
$x.CalculateFullRebuild()
$errs = @()
foreach ($s in $wb.Worksheets) {
  try { $ec = $s.UsedRange.SpecialCells(-4123, 16); foreach ($cell in $ec) { $errs += ($s.Name + '!' + $cell.Address($false,$false) + '=' + $cell.Text); if ($errs.Count -gt 30) { break } } } catch {}
}
$ws = $wb.Worksheets.Item($Sheet)
$grid = @()
for ($r = 1; $r -le $Rows; $r++) {
  $vals = @()
  for ($c = 1; $c -le $Cols; $c++) { $v = $ws.Cells.Item($r, $c).Value2; if ($v -eq $null) { $vals += '' } else { $vals += $v } }
  $grid += ,$vals
}
$wb.Save(); $wb.Close($false); $x.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($x) | Out-Null
@{ errors = $errs; grid = $grid } | ConvertTo-Json -Depth 4 | Out-File -Encoding utf8 $OutJson
'done'
