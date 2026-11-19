param([string]$Orig, [string]$Clean)
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false; $xl.DisplayAlerts = $false; $xl.AskToUpdateLinks = $false; $xl.EnableEvents = $false
try {
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $a = $xl.Workbooks.Open($Orig, 0, $true); $tA = $sw.Elapsed.TotalSeconds
  $sw.Restart()
  $b = $xl.Workbooks.Open($Clean, 0, $true); $tB = $sw.Elapsed.TotalSeconds
  "open seconds: original=$([math]::Round($tA,1)) clean=$([math]::Round($tB,1))"
  "clean name in Excel: $($b.Name)  (contains 'Repaired' => repair happened)"
  "names: $($a.Names.Count) -> $($b.Names.Count)"
  $la = $a.LinkSources(1); $lb = $b.LinkSources(1)
  "links: $(@($la).Count) -> $(@($lb).Count)"
  $xl.CalculateFull()
  $diff = 0; $cells = 0; $samples = @()
  foreach ($sa in $a.Worksheets) {
    $sb = $b.Worksheets.Item($sa.Name)
    $ra = $sa.UsedRange; $addr = $ra.Address()
    $va = $ra.Value2; $vb = $sb.Range($addr).Value2
    if ($va -isnot [array]) { $va = ,$va; $vb = ,$vb }
    $r1 = $va.GetLowerBound(0); $r2 = $va.GetUpperBound(0); $c1 = $va.GetLowerBound(1); $c2 = $va.GetUpperBound(1)
    $sd = 0
    for ($r = $r1; $r -le $r2; $r++) { for ($c = $c1; $c -le $c2; $c++) {
      $x = $va[$r,$c]; $y = $vb[$r,$c]; $cells++
      if ($x -is [double] -and $y -is [double]) { if ([math]::Abs($x-$y) -gt 1e-6*[math]::Max(1,[math]::Abs($x))) { $sd++ } }
      elseif ("$x" -ne "$y") { $sd++ }
      if ($sd -gt 0 -and $samples.Count -lt 15 -and ("$x" -ne "$y")) { $samples += "$($sa.Name)!R$($r)C$($c): '$x' vs '$y'" }
    } }
    if ($sd) { "  DIFF $($sa.Name): $sd cells" }
    $diff += $sd
  }
  "cells compared: $cells   differing: $diff"
  $samples
} finally {
  foreach ($w in @($xl.Workbooks)) { $w.Close($false) }
  $xl.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($xl)
}
