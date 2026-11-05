# In-place text edit on slide 2 (exec summary, admin bullet): only the two figures change, formatting untouched
param([string]$File, [string]$PngDir)
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open($File, 0, 0, 0)
try {
  $sl = $p.Slides.Item(2); $hits = 0
  $pairs = @(@('International 15 (mainly Vietnam)', 'International 14 (mainly Vietnam)'), @('Thailand excl. TDC 2.0 is 12 MB lower', 'Thailand excl. TDC 2.0 is 11 MB lower'))
  foreach ($sh in $sl.Shapes) {
    if (-not ($sh.HasTextFrame -and $sh.TextFrame.HasText)) { continue }
    foreach ($pr in $pairs) {
      $tr = $sh.TextFrame.TextRange
      if ($tr.Text.Contains($pr[0])) { $null = $tr.Replace($pr[0], $pr[1]); $hits++ }
    }
  }
  "replacements: $hits"
  foreach ($sh in $sl.Shapes) { if ($sh.HasTextFrame -and $sh.TextFrame.HasText -and $sh.TextFrame.TextRange.Text.StartsWith('Admin rises')) { 'now: ' + $sh.TextFrame.TextRange.Text } }
  if ($hits -eq 2) { $p.Save(); 'saved' } else { 'NOT saved - expected 2 replacements' }
  if ($PngDir) { New-Item -ItemType Directory -Force $PngDir | Out-Null; $sl.Export((Join-Path $PngDir 's02.png'), 'PNG', 1600, 900) }
} finally { $p.Close() }
