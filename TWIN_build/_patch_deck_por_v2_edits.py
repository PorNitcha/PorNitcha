# one-off: Por's v2 edits (29-Oct 16:43): black section bars "TDC / TWIN Portfolio I 2025 - YTD 26" on page 2; TWIN customer rows black
p = 'TWIN_build/build_deck.ps1'; s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s; assert a in s, a[:70]; s = s.replace(a, b, 1)
rep("    $g = $gs[$i]; $col = $(if ($g.grp -eq 'The rest') { $DARK } else { $INDO })", "    $g = $gs[$i]; $col = $(if ($g.grp -eq 'The rest') { $DARK } else { 0 })  # black (Por 29-Oct)")
rep("function Read-Box(", """function Section-Bar($slide, $y, $text) {
  $b = $slide.Shapes.AddShape(1, 37, $y, 903, 24); $b.Fill.ForeColor.RGB = 0; $b.Fill.Solid(); $b.Line.Visible = 0; $b.Shadow.Visible = 0
  $tr = $b.TextFrame.TextRange; $tr.Text = $text; $tr.Font.Name = $FONT; $tr.Font.Size = [single]18; $tr.Font.Color.RGB = $WHITE; $tr.Font.Bold = 0; $tr.ParagraphFormat.Alignment = 2
  $b.TextFrame.VerticalAnchor = 3; $b.TextFrame.MarginTop = [single]0; $b.TextFrame.MarginBottom = [single]0
}
function Read-Box(""")
rep("""$bw = 400; $bh = 160
$by = 96
$script:Q = $D.tdcq.'25'; Draw-Box $s2 70 $by $bw $bh 'Base 2025 actual (FY)' $cellFn2""",
    """$bw = 400; $bh = 150
Section-Bar $s2 58 'TDC Portfolio I 2025 - YTD 26'
$by = 102
$script:Q = $D.tdcq.'25'; Draw-Box $s2 70 $by $bw $bh 'Base 2025 actual (FY)' $cellFn2""")
rep("$by2 = $by + $bh + 52\n", "Section-Bar $s2 ($by + $bh + 26) 'TWIN Portfolio I 2025 - YTD 26'\n$by2 = $by + $bh + 70\n")
rep("Read-Box $s2 ($by2 + $bh + 24) ('Read: '", "Read-Box $s2 ($by2 + $bh + 22) ('Read: '")
open(p, 'w', encoding='utf-8').write(s); print('ok')
