# Replace one worksheet in Por's workbook with the same-named sheet from a generated workbook, keeping every other sheet exactly as Por saved it (Excel COM).
# Uses its own Excel instance and quits only that instance.  Usage: swap_sheet.ps1 <por.xlsx> <generated.xlsx> <sheet name> <out.xlsx>
param([string]$Por, [string]$Gen, [string]$Sheet, [string]$Out)
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false; $xl.DisplayAlerts = $false
try {
  $wp = $xl.Workbooks.Open($Por, 0, $true)
  $wg = $xl.Workbooks.Open($Gen, 0, $true)
  $old = $wp.Worksheets.Item($Sheet); $idx = $old.Index
  $prev = $wp.Worksheets.Item($idx - 1)
  $wg.Worksheets.Item($Sheet).Copy([Type]::Missing, $prev)       # lands right after the sheet before the old one
  $new = $wp.Worksheets.Item($idx)
  $old.Delete(); $new.Name = $Sheet
  $wp.Worksheets.Item(1).Activate()
  $wp.SaveAs($Out, 51)
  $names = @(); foreach ($s in $wp.Worksheets) { $names += $s.Name }
  "saved $Out : " + ($names -join ' | ')
  $wg.Close($false); $wp.Close($false)
} finally { $xl.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($xl) }
