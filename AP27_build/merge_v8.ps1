# Build v8 from Por's edited v7: keep Por's slides, swap in the regenerated slides 7 and 9-16 from my build.
# Por's own edits on those slides were only deletions (source line on 9-16, Waxy note on slide 10) - re-applied here.
param([string]$PorFile, [string]$MineFile, [string]$Out, [string]$PngDir)
Copy-Item -LiteralPath $PorFile -Destination $Out -Force
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open($Out, 0, 0, 0)     # read-write, no window
$n0 = $p.Slides.Count
# 1) slides 9-16: insert the new ones after 16, then delete the old 9..16
$p.Slides.InsertFromFile($MineFile, 16, 9, 16) | Out-Null
for ($i = 16; $i -ge 9; $i--) { $p.Slides.Item($i).Delete() }
# 2) slide 7: insert the new one after 7, delete the old 7
$p.Slides.InsertFromFile($MineFile, 7, 7, 7) | Out-Null
$p.Slides.Item(7).Delete()
# 3) re-apply Por's deletions on the swapped slides
$removed = 0
for ($i = 9; $i -le 16; $i++) {
  $sl = $p.Slides.Item($i)
  for ($k = $sl.Shapes.Count; $k -ge 1; $k--) {
    $sh = $sl.Shapes.Item($k)
    if ($sh.HasTextFrame -and $sh.TextFrame.HasText) {
      $tx = $sh.TextFrame.TextRange.Text
      if ($tx.StartsWith('Source: P&L LE9+3')) { $sh.Delete(); $removed++ }
      elseif ($i -eq 10 -and $tx.StartsWith('Note: HVA BU includes Waxy')) { $sh.Delete(); $removed++ }
    }
  }
}
"slides before {0}, after {1}; shapes removed {2}" -f $n0, $p.Slides.Count, $removed
for ($i = 1; $i -le $p.Slides.Count; $i++) { $t = ''; foreach ($sh in $p.Slides.Item($i).Shapes) { if ($sh.Type -eq 14 -and $sh.HasTextFrame -and $sh.TextFrame.HasText -and ($sh.PlaceholderFormat.Type -eq 1 -or $sh.PlaceholderFormat.Type -eq 3)) { $t = $sh.TextFrame.TextRange.Text } }; "  {0,2}: {1}" -f $i, $t.Replace([string][char]11, ' ') }
$p.Save()
if ($PngDir) { New-Item -ItemType Directory -Force $PngDir | Out-Null; for ($i = 1; $i -le $p.Slides.Count; $i++) { $p.Slides.Item($i).Export((Join-Path $PngDir ('s{0:D2}.png' -f $i)), 'PNG', 1600, 900) } }
$p.Close()
