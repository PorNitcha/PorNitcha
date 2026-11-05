param([string]$BaseFile, [string]$MineFile, [string]$Out, [string]$PngDir)
Copy-Item -LiteralPath $BaseFile -Destination $Out -Force
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open($Out, 0, 0, 0)
try {
  foreach ($n in 7, 8, 9) { $p.Slides.InsertFromFile($MineFile, $n, $n - 6, $n - 6) | Out-Null; $p.Slides.Item($n).Delete() }
  $p.Save(); "slides: " + $p.Slides.Count
  if ($PngDir) { New-Item -ItemType Directory -Force $PngDir | Out-Null; foreach ($n in 7, 8, 9) { $p.Slides.Item($n).Export((Join-Path $PngDir ('s{0:D2}.png' -f $n)), 'PNG', 1600, 900) } }
} finally { $p.Close() }
