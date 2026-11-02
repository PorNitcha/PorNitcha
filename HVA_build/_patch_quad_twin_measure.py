# TWIN view: GP/kg selector (Por 30-Oct) - combined TDC + TWIN (default), TWIN trading margin only, or TDC leg.
# Line on "Base-year average": combined and TWIN = average of that measure on the TWIN book; TDC leg = the TDC chart's line.
# Combined view also shows the TDC customers' average as a dotted reference.
# Usage: python _patch_quad_twin_measure.py <page.html>
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)
rep('''    <span class="eyebrow">Base year</span>''', '''    <label class="ctl twinOnly" for="twm" hidden>GP/kg
      <select id="twm"><option value="comb" selected>Combined TDC + TWIN</option><option value="twin">TWIN trading margin only</option><option value="tdc">TDC leg only</option></select>
    </label>
    <span class="eyebrow">Base year</span>''')
rep("let base = 25, basis = 'gpp', FLOOR = 4700, minT = 0, lblT = 1000, floorMode = 'avg';",
    "let base = 25, basis = 'gpp', FLOOR = 4700, minT = 0, lblT = 1000, floorMode = 'avg', twMeasure = 'comb';")
rep("  const L = FLOOR/1000;\n  const roleT = r => r.comb >= L ?",
    """  const mv = r => r[twMeasure], tSum = rows.reduce((a,r)=>a+r.t,0);
  const mAvg = rows.reduce((a,r)=>a+(twMeasure==='comb'?r.gpC:r.gpW),0)/tSum/1000;
  const L = (floorMode==='avg' && twMeasure!=='tdc') ? mAvg : FLOOR/1000;
  const mName = {comb:'Combined TDC + TWIN', twin:'TWIN trading margin', tdc:'TDC-leg'}[twMeasure];
  const roleT = r => mv(r) >= L ?""")
rep("ys = rows.map(r=>r.comb);", "ys = rows.map(mv);")
rep("sy(r.comb)));", "sy(mv(r))));")
rep("""${floorMode==='avg' ? (base===25?'2025':'2026 YTD')+' TDC average '+L.toFixed(1)+' THB/kg' : 'floor '+L.toFixed(1)+' THB/kg'}</text>`;""",
    """${floorMode==='avg' ? (base===25?'2025':'2026 YTD')+(twMeasure==='tdc'?' TDC customers average ':' TWIN book average ')+L.toFixed(1)+' THB/kg' : 'floor '+L.toFixed(1)+' THB/kg'}</text>`;
  if (twMeasure==='comb' && Math.abs(FLOOR/1000-L) > 0.15){ const yR = sy(FLOOR/1000);
    s += `<line x1="${m.l}" x2="${W-m.r}" y1="${yR}" y2="${yR}" stroke="var(--fg-3)" stroke-dasharray="1 3"/><text x="${m.l+6}" y="${yR-5}" font-size="10" fill="var(--fg-3)" stroke="var(--panel)" stroke-width="3" stroke-linejoin="round" paint-order="stroke">${floorMode==='avg'?'TDC customers average':'floor'} ${(FLOOR/1000).toFixed(1)} THB/kg (reference)</text>`; }""")
rep(">Combined TDC + TWIN ${full?'full-cost':'product'} GP per kg ${base===25?'2025':'2026 YTD'}, THB/kg<",
    ">${mName} ${twMeasure==='twin'?'':(full?'full-cost ':'product ')}GP per kg ${base===25?'2025':'2026 YTD'}, THB/kg<")
rep("Height = combined chain GP per kg: TDC's ${full?'full-cost':'product'} GP on the TDC products sold to these customers (allocated by SKU and quarter) plus TWIN's trading margin, against the same line as the TDC chart (what TDC earns on average across its own customers). ",
    "Height = ${{comb:'combined chain GP per kg: TDC leg plus TWIN trading margin', twin:'TWIN trading margin per kg (TWIN GP on these sales)', tdc:'TDC-leg GP per kg'}[twMeasure]}. TDC leg = TDC's ${full?'full-cost':'product'} GP on the TDC products sold to these customers (allocated by SKU and quarter). Line: ${floorMode!=='avg'?'the selected floor':(twMeasure==='tdc'?'the TDC chart line (TDC customers average)':'the base-year average of this measure on the TWIN book, tonne-weighted'+(twMeasure==='comb'?'; dotted line = TDC customers average for reference':''))}. ")
rep("<p class=\"sub\">PT Thai Wah Indonesia's customers buying TDC products. Height = combined chain GP per kg (TDC + TWIN), against the same line as the TDC chart; the boxes split it into TDC's leg and TWIN's trading margin.</p>",
    "<p class=\"sub\">PT Thai Wah Indonesia's customers buying TDC products. Height = the GP/kg chosen above (combined TDC + TWIN by default); the boxes split it into TDC's leg and TWIN's trading margin.</p>")
rep("document.querySelectorAll('.tdcOnly').forEach(x=>x.hidden = tw);",
    "document.querySelectorAll('.tdcOnly').forEach(x=>x.hidden = tw); document.querySelectorAll('.twinOnly').forEach(x=>x.hidden = !tw);")
rep("document.getElementById('minT').addEventListener('change'",
    "document.getElementById('twm').addEventListener('change',e=>{ twMeasure=e.target.value; drawTwin(); });\ndocument.getElementById('minT').addEventListener('change'")
open(p, 'w', encoding='utf-8').write(s); print('ok', len(s))
