# One chart slot with a "Customers" dropdown: TDC customers (2027 plan quadrant) or TWIN customers (Por 30-Oct).
# TWIN on the 2026 base: growth = 2026 annualised (YTD Sep x 12/9) vs FY2025, not YTD vs YTD.
# Usage: python _patch_quad_view_select.py <page.html>
import sys, re
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)
# 1) controls: view dropdown first; TDC-only filters tagged
rep('''  <div class="controls">
    <span class="eyebrow">Base year</span>''', '''  <div class="controls">
    <label class="ctl" for="view">Customers
      <select id="view"><option value="tdc" selected>TDC customers</option><option value="twin">TWIN customers (via PT Thai Wah Indonesia)</option></select>
    </label>
    <span class="eyebrow">Base year</span>''')
rep('<label class="ctl" for="minT">', '<label class="ctl tdcOnly" for="minT">')
rep('<label class="ctl" for="lbl">', '<label class="ctl tdcOnly" for="lbl">')
rep('.grid{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:18px;align-items:start}',
    '.grid{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:18px;align-items:start}\n.grid.single{grid-template-columns:minmax(0,1fr)}')
# 2) move the TWIN section into the chart panel
m = re.search(r'  <div class="section panel">\n    <h2 id="tTitle">.*?<div class="foot" id="twinFoot"></div>\n  </div>\n\n', s, re.S)
assert m
twin = m.group(0)
s = s.replace(twin, '')
inner = twin.split('\n', 1)[1].rsplit('  </div>\n', 1)[0]           # drop the section wrapper
inner = '\n'.join('  ' + l if l else l for l in inner.split('\n'))
rep('''  <div class="grid">
    <div class="panel">
      <h2 id="qTitle">''', '''  <div class="grid" id="chartGrid">
    <div class="panel">
      <div id="vTDC">
      <h2 id="qTitle">''')
rep('''      <div id="newlist" class="foot"></div>
    </div>
    <div class="panel">
      <h2>Four roles on this base</h2>''', '''      <div id="newlist" class="foot"></div>
      </div>
      <div id="vTWIN" hidden>
''' + inner + '''      </div>
    </div>
    <div class="panel" id="rolesPanel">
      <h2>Four roles on this base</h2>''')
# 3) TWIN 2026 base = annualised YTD Sep-26 vs FY2025
rep("const cur = base===25 ? 'y25' : 'y26', prv = base===25 ? 'y24' : 'p25';",
    "const cur = base===25 ? 'y25' : 'y26', prv = base===25 ? 'y24' : 'y25', ann = base===25 ? 1 : 12/9;   // 2026: YTD Sep x 12/9 vs FY2025")
rep("return {d, t, tp, g: t-tp, isNew: tp<5,", "return {d, t, tp, tA: t*ann, g: t*ann-tp, isNew: tp<5,")
rep("${base===25?'FY2025 vs FY2024':'YTD Sep-26 vs YTD Sep-25'}, tonnes (new customers count as growing) →",
    "${base===25?'FY2025 vs FY2024':'2026 annualised (YTD Sep × 12/9) vs FY2025'}, tonnes (new customers count as growing) →")
rep("<span class=\"mono\">Tonnes ${base===25?'FY2024 '+fmt(r.tp)+' → FY2025 ':'YTD Sep-25 '+fmt(r.tp)+' → YTD Sep-26 '}${fmt(r.t)}${r.isNew?' (new)':''}</span>",
    "<span class=\"mono\">Tonnes ${base===25?'FY2024 '+fmt(r.tp)+' → FY2025 '+fmt(r.t):'FY2025 '+fmt(r.tp)+' → 2026 annualised '+fmt(r.tA)+' (YTD Sep '+fmt(r.t)+')'}${r.isNew?' (new)':''}</span>")
rep("`TWIN customers · ${base===25?'FY2025 vs FY2024':'YTD Sep-26 vs YTD Sep-25'} · ${fmt(tt)} t",
    "`TWIN customers · ${base===25?'FY2025 vs FY2024':'2026 annualised vs FY2025'} · ${base===25?'FY2025':'YTD Sep-26'} ${fmt(tt)} t")
rep("Dashed ring = new customer (no prior-year volume), counted as growing.",
    "${base===25?'':'Growth on the 2026 base = YTD Sep-26 tonnes × 12/9 minus FY2025 tonnes; GP/kg and the boxes stay on YTD Sep-26 actuals. '}Dashed ring = new customer (under 5 t in the prior year), counted as growing.")
rep("Same line as the chart above, on TDC's own leg of the margin;", "Same line as the TDC chart, on TDC's own leg of the margin;")
# 4) view switch
rep("document.getElementById('minT').addEventListener('change'", """document.getElementById('view').addEventListener('change',e=>{ const tw = e.target.value==='twin';
  document.getElementById('vTDC').hidden = tw; document.getElementById('vTWIN').hidden = !tw; document.getElementById('rolesPanel').hidden = tw;
  document.getElementById('chartGrid').classList.toggle('single', tw); document.querySelectorAll('.tdcOnly').forEach(x=>x.hidden = tw);
  tw ? drawTwin() : drawQuad(); });
document.getElementById('minT').addEventListener('change'""")
open(p, 'w', encoding='utf-8').write(s); print('ok', len(s))
