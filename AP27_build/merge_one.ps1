# Copy the base deck to a new name and replace ONE slide with the same-numbered slide from my build (everything else untouched)
param([string]$BaseFile, [string]$MineFile, [string]$Out, [int]$SlideNo, [string]$PngDir)
Copy-Item -LiteralPath $BaseFile -Destination $Out -Force
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open($Out, 0, 0, 0)
try {
  $p.Slides.InsertFromFile($MineFile, $SlideNo, $SlideNo, $SlideNo) | Out-Null
  $p.Slides.Item($SlideNo).Delete()
  $p.Save()
  "slides: " + $p.Slides.Count
  if ($PngDir) { New-Item -ItemType Directory -Force $PngDir | Out-Null; $p.Slides.Item($SlideNo).Export((Join-Path $PngDir ('s{0:D2}.png' -f $SlideNo)), 'PNG', 1600, 900) }
} finally { $p.Close() }
