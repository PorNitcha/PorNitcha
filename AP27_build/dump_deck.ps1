# Dump every shape of a deck (read-only, hidden) to a TSV for diffing: slide, idx, type, name, left, top, w, h, font, size, bold, color, fill, text
param([string]$Path, [string]$OutTsv)
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open($Path, -1, 0, 0)
$lines = New-Object System.Collections.Generic.List[string]
for ($si = 1; $si -le $p.Slides.Count; $si++) {
  $sl = $p.Slides.Item($si); $k = 0
  foreach ($sh in $sl.Shapes) {
    $k++
    $txt = ''; $fn = ''; $fs = ''; $fb = ''; $fc = ''
    if ($sh.HasTextFrame -and $sh.TextFrame.HasText) {
      $tr = $sh.TextFrame.TextRange; $txt = $tr.Text.Replace("`r", ' / ').Replace("`t", ' ')
      $fn = $tr.Font.Name; $fs = $tr.Font.Size; $fb = $tr.Font.Bold; $fc = $tr.Font.Color.RGB
    }
    $fill = ''; try { if ($sh.Fill.Visible) { $fill = $sh.Fill.ForeColor.RGB } } catch {}
    $lines.Add(('{0}`t{1}`t{2}`t{3}`t{4:N1}`t{5:N1}`t{6:N1}`t{7:N1}`t{8}`t{9}`t{10}`t{11}`t{12}`t{13}' -f $si, $k, $sh.Type, $sh.Name, $sh.Left, $sh.Top, $sh.Width, $sh.Height, $fn, $fs, $fb, $fc, $fill, $txt).Replace('`t', "`t"))
  }
}
$p.Close()
[IO.File]::WriteAllLines($OutTsv, $lines, [Text.Encoding]::UTF8)
'dumped ' + $lines.Count
