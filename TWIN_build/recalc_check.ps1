# Opens the workbook in Excel (hidden), recalculates, saves (so cached values exist), and dumps check cells as JSON.
param([string]$Path, [string]$OutJson)
$x = New-Object -ComObject Excel.Application
$x.Visible = $false; $x.DisplayAlerts = $false
$wb = $x.Workbooks.Open($Path)
$x.CalculateFullRebuild()
$res = @{}
$ws = $wb.Worksheets.Item('Summary')
$res['summary_A'] = @(); $res['summary_B_E'] = @()
for ($r = 8; $r -le 50; $r++) {
  $a = $ws.Cells.Item($r, 1).Text
  $vals = @()
  for ($c = 2; $c -le 5; $c++) { $vals += $ws.Cells.Item($r, $c).Value2 }
  $res['summary_A'] += $a; $res['summary_B_E'] += ,$vals
}
$ws = $wb.Worksheets.Item('By customer')
$res['bycust'] = @()
for ($r = 9; $r -le 14; $r++) {
  $vals = @($ws.Cells.Item($r, 1).Text)
  for ($c = 2; $c -le 16; $c++) { $vals += $ws.Cells.Item($r, $c).Value2 }
  $res['bycust'] += ,$vals
}
$ws = $wb.Worksheets.Item('Key findings')
$res['kf'] = @()
for ($r = 7; $r -le 30; $r++) {
  $vals = @($ws.Cells.Item($r, 1).Text)
  for ($c = 2; $c -le 13; $c++) { $vals += $ws.Cells.Item($r, $c).Value2 }
  $res['kf'] += ,$vals
}
# error scan across all sheets
$errs = @()
foreach ($s in $wb.Worksheets) {
  $ur = $s.UsedRange
  try {
    $ec = $ur.SpecialCells(-4123, 16)  # xlCellTypeFormulas, xlErrors
    foreach ($cell in $ec) { $errs += ($s.Name + '!' + $cell.Address($false,$false) + '=' + $cell.Text); if ($errs.Count -gt 30) { break } }
  } catch {}
}
$res['errors'] = $errs
$wb.Save()
$wb.Close($false)
$x.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($x) | Out-Null
$res | ConvertTo-Json -Depth 5 | Out-File -Encoding utf8 $OutJson
'done'
