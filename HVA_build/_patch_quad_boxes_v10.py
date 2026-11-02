# Quadrant artifact v10 (Por 30-Oct): corner boxes = PPT-style mini table (Total TDC / Indonesia direct / via TWIN x Vol share / GP share / GP/kg),
# all 2027-plan accounts placed (new accounts at estimated product GP/t from quad2_gp_proxy.json, hollow bubbles), GP/kg = actual base-year GP at actual tonnes.
# Usage: python _patch_quad_boxes_v10.py <live artifact html> <quad2_gp_proxy.json> <out.html>
import sys, json
src, proxy, out = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(src, encoding='utf-8').read().split('\n')
# the read-back file starts with the service's own skeleton line; drop it so the page is not wrapped twice
if lines[0].startswith('<!doctype html><html><head><meta charset=utf8>') and lines[1].lower().startswith('<!doctype html>'):
    lines = lines[1:]
s = '\n'.join(lines)
P = json.load(open(proxy, encoding='utf-8'))
PX = {n: [v['25']['gpp'] if v['25']['src'] != 'own' else None, v['26']['gpp'] if v['26']['src'] != 'own' else None] for n, v in P.items() if v['25']['src'] != 'own' or v['26']['src'] != 'own'}
def rep(a, b, cnt=1):
    global s
    assert s.count(a) >= 1, a[:90]
    s = s.replace(a, b, cnt)
# tokens: Indonesia row colour (Por's blue)
rep("--fix-soft:rgba(235,104,52,.10);", "--indo:#156082; --fix-soft:rgba(235,104,52,.10);")
rep("  --fix:#d95926; --grow:#3987e5; --protect:#199e70; --neutral:#9a9b95;\n  --fix-soft:rgba(217,89,38,.16);", "  --fix:#d95926; --grow:#3987e5; --protect:#199e70; --neutral:#9a9b95; --indo:#6fb3dd;\n  --fix-soft:rgba(217,89,38,.16);", 2)
# default: all accounts
rep('<option value="0">all</option><option value="100" selected>100 t</option>', '<option value="0" selected>all</option><option value="100">100 t</option>')
rep("let base = 25, basis = 'gpp', FLOOR = 4700, minT = 100, lblT = 1000;", "let base = 25, basis = 'gpp', FLOOR = 4700, minT = 0, lblT = 1000;")
# proxy map + helpers
i = s.index('const DATA = '); j = s.index('\n', i)
s = s[:j + 1] + 'const PX = ' + json.dumps(PX, ensure_ascii=False) + ';  // estimated product GP/t [2025, 2026] for accounts without own base-year history (own other-year, else base-year TDC average of the SKUs in the 2027 plan)\n' + s[j + 1:]
rep("const baseGp = d => gpOf(d, base===25?'25':'26');",
    """const yKey = () => base===25 ? '25' : '26';
const actT = d => base===25 ? d.t25 : d.t26;   // actual base-year tonnes (2026 = Jan-Sep)
const hasOwn = d => gpOf(d, yKey())!=null && actT(d) >= 5;
const baseGp = d => hasOwn(d) ? gpOf(d, yKey()) : (basis==='gpp' && PX[d.name] && PX[d.name][base===25?0:1]!=null ? PX[d.name][base===25?0:1] : null);
const isTW = d => /THAI WAH INDONESIA/i.test(d.name);
const isDirect = d => (d.country||'').trim()==='Indonesia' && !isTW(d);""")
rep("""function roleOf(d){
  const gp = baseGp(d), bt = baseT(d);
  if (gp==null || bt<5) return 'new';
  const g = d.t27 - bt;""", """function roleOf(d){
  const gp = baseGp(d); if (gp==null) return 'new';
  const bt = hasOwn(d) ? baseT(d) : 0;   // no base-year history = volume growing (Por 29-Oct)
  const g = d.t27 - bt;""")
rep("const pos = d => { const gp = baseGp(d); const g = d.t27-baseT(d); const r = rad(d.t27);",
    "const pos = d => { const gp = baseGp(d); const g = d.t27-(hasOwn(d)?baseT(d):0); const r = rad(d.t27);")
# bubbles: estimated accounts hollow
rep("""    s += `<circle data-i="${DATA.indexOf(d)}" cx="${p.x}" cy="${p.y}" r="${p.r}" fill="${id?ID_GREY:col[r]}" fill-opacity="${id?'.85':'.62'}" stroke="${id?'var(--fg)':(p.clipped?'var(--fg-2)':'var(--panel)')}" stroke-width="${id?1.5:2}"${p.clipped?' stroke-dasharray="3 3"':''}/>`; });""",
    """    const est = !hasOwn(d);
    s += `<circle data-i="${DATA.indexOf(d)}" cx="${p.x}" cy="${p.y}" r="${p.r}" fill="${id?ID_GREY:col[r]}" fill-opacity="${est?'.12':(id?'.85':'.62')}" stroke="${est?(id?ID_GREY:col[r]):(id?'var(--fg)':(p.clipped?'var(--fg-2)':'var(--panel)'))}" stroke-width="${id?1.5:(est?1.2:2)}"${(p.clipped||est)?' stroke-dasharray="3 3"':''}/>`; });""")
# boxes
a = s.index("  // Volume and value contribution per quadrant"); b = s.index("  s += `</g></svg><div class=\"tip\" hidden></div>`;")
new_boxes = r"""  // Boxes: same table as the PPT quadrant. Vol share / GP share = share of 2027 plan tonnes / of GP (plan tonnes x base-year GP/t, estimated for new accounts);
  // GP/kg = ACTUAL base-year GP per kg at actual base-year tonnes, accounts with their own base-year sales only.
  const mk = () => ({n:0, nn:0, t:0, gp:0, ta:0, gpa:0});
  const q = {}; ['fix','grow','protect','reprice'].forEach(r=>q[r]={all:mk(), dir:mk(), tw:mk()});
  hist.forEach(d=>{ const r=roleOf(d); const parts=[q[r].all]; if (isDirect(d)) parts.push(q[r].dir); if (isTW(d)) parts.push(q[r].tw);
    parts.forEach(a=>{ a.n++; if(!hasOwn(d)) a.nn++; a.t+=d.t27; a.gp+=d.t27*baseGp(d); if (hasOwn(d)){ a.ta+=actT(d); a.gpa+=actT(d)*baseGp(d); } }); });
  const planT = rows.reduce((a,d)=>a+d.t27,0);
  const gpTot = Object.values(q).reduce((a,v)=>a+v.all.gp,0);
  const circles = sorted.map(d=>pos(d));
  const BW=262, BH=82, lower=sy(FLOOR);
  const cands = {
    protect:[[m.l+4, m.t+4], [m.l+4, lower-BH-4]],
    grow:[[W-m.r-BW-4, m.t+4], [W-m.r-BW-4, lower-BH-4]],
    fix:[[W-m.r-BW-4, H-m.b-BH-4], [W-m.r-BW-4, (lower+H-m.b)/2-BH/2], [sx(0)+6, H-m.b-BH-4]],
    reprice:[[m.l+4, H-m.b-BH-4], [m.l+4, (lower+H-m.b)/2-BH/2]] };
  const hits = (x,y) => circles.some(c=> c.x+c.r>x && c.x-c.r<x+BW && c.y+c.r>y && c.y-c.r<y+BH);
  const labelOf = {protect:['PROTECT','var(--protect)'], grow:['GROW WITH MARGIN','var(--grow)'], fix:['FIX PRICE BEFORE VOLUME','var(--fix)'], reprice:['REPRICE / EXIT','var(--fg-2)']};
  const kg = a => a.ta ? (a.gpa/a.ta/1000).toFixed(1) : '–';
  const sh = (a,b) => (b && a/b>=0.005) ? Math.round(a/b*100)+'%' : '–';
  s += `<g id="qstats" font-family="var(--font)">`;
  Object.keys(cands).forEach(r=>{ const Q=q[r]; let [x,y]=cands[r][0]; for (const c of cands[r]){ if(!hits(c[0],c[1])){ [x,y]=c; break; } }
    const cV=x+142, cG=x+196, cK=x+BW-8;
    s += `<rect x="${x}" y="${y}" width="${BW}" height="${BH}" rx="4" fill="var(--panel)" fill-opacity=".9" stroke="${labelOf[r][1]}" stroke-opacity=".35"/>`;
    s += `<text x="${x+8}" y="${y+15}" font-size="11" font-weight="600" fill="${labelOf[r][1]}">${labelOf[r][0]}</text>`;
    s += `<text x="${cK}" y="${y+15}" text-anchor="end" font-size="9.5" fill="var(--fg-3)">${Q.all.n} accounts${Q.all.nn?` · ${Q.all.nn} new`:''}</text>`;
    s += `<g font-size="9.5" fill="var(--fg-3)"><text x="${cV}" y="${y+30}" text-anchor="end">Vol share</text><text x="${cG}" y="${y+30}" text-anchor="end">GP share</text><text x="${cK}" y="${y+30}" text-anchor="end">GP/kg</text></g>`;
    s += `<line x1="${x+8}" x2="${cK}" y1="${y+34}" y2="${y+34}" stroke="var(--fg-3)" stroke-width=".6"/>`;
    [['Total TDC', Q.all, 'var(--fg)'], ['Indonesia direct', Q.dir, 'var(--indo)'], ['via TWIN', Q.tw, 'var(--indo)']].forEach(([lab,a,c],i)=>{
      const yy = y+48+i*13; const fill = (i>0 && !a.t) ? 'var(--fg-3)' : c;
      s += `<g font-size="10.5" fill="${fill}"><text x="${x+8}" y="${yy}">${lab}</text><text x="${cV}" y="${yy}" text-anchor="end" font-family="var(--mono)">${sh(a.t,planT)}</text><text x="${cG}" y="${yy}" text-anchor="end" font-family="var(--mono)">${sh(a.gp,gpTot)}</text><text x="${cK}" y="${yy}" text-anchor="end" font-family="var(--mono)">${kg(a)}</text></g>`; }); });
"""
s = s[:a] + new_boxes + s[b:]
# list under the chart: estimated / unplaced accounts
rep("""  const nt = news.reduce((a,d)=>a+d.t27,0);
  const top = [...news].sort((a,b)=>b.t27-a.t27).slice(0,10).map(d=>`${esc(short(d.name))} ${fmt(d.t27)}`).join(' · ');
  document.getElementById('newlist').innerHTML = `<b>No ${base===25?'2025':'2026'} history:</b> ${news.length} accounts, ${fmt(nt)} t in the 2027 plan. Largest: ${top}.`;""",
"""  const estA = hist.filter(d=>!hasOwn(d)); const et = estA.reduce((a,d)=>a+d.t27,0);
  const topE = [...estA].sort((a,b)=>b.t27-a.t27).slice(0,10).map(d=>`${esc(short(d.name))} ${fmt(d.t27)}`).join(' · ');
  const nt = news.reduce((a,d)=>a+d.t27,0);
  document.getElementById('newlist').innerHTML = (estA.length ? `<b>New accounts (no ${base===25?'2025':'2026'} history, hollow bubbles):</b> ${estA.length} accounts, ${fmt(et)} t in the 2027 plan, placed as growing at an estimated GP/t. Largest: ${topE}.` : '')
    + (news.length ? ` <b>Not placed on this GP basis:</b> ${news.length} accounts, ${fmt(nt)} t (estimates exist on product GP only).` : '');""")
# tooltip: say when GP is estimated
rep("""  <span class="mono">XL share ${d.xl25==null?'–':d.xl25+'%'} → ${d.xl26==null?'–':d.xl26+'%'}</span>`;""",
    """  <span class="mono">XL share ${d.xl25==null?'–':d.xl25+'%'} → ${d.xl26==null?'–':d.xl26+'%'}</span>${hasOwn(d)?'':`<br><span class="mono" style="color:var(--fg-3)">No ${base===25?'2025':'2026'} history: placed at estimated product GP/t ${fmt(baseGp(d))}</span>`}`;""")
# footnote text
rep("Accounts with no base-year history (or under 5 t in the base year: Sajo CPK, IFP, LLC 7 Utra) are listed under the chart.",
    "Accounts with no base-year history (or under 5 t in the base year: Sajo CPK, IFP, LLC 7 Utra) count as volume growing and sit at an estimated product GP/t: their own other-year GP/t, else the base-year TDC average of the SKUs in their 2027 plan. They are drawn as hollow dashed bubbles and listed under the chart.")
a = s.index("<b>Boxes in each quadrant</b>"); b = s.index("</div>", a)
s = s[:a] + "<b>Boxes in each quadrant</b> (same as the PPT): Vol share = share of 2027 plan tonnes; GP share = share of GP, where GP = 2027 plan tonnes &times; base-year GP/t on the selected basis (estimated for new accounts); GP/kg = actual base-year GP per kg at actual base-year tonnes, accounts with their own base-year sales only. Rows: Total TDC, Indonesia direct (TDC export accounts in Indonesia), via TWIN (PT Thai Wah Indonesia). With 2027 plan &ge; all, the four boxes add to 100%. THB values are in the role panel on the right." + s[b:]
rep("quadrant volume/value boxes added 28 Oct 2026.", "quadrant volume/value boxes added 28 Oct 2026; boxes restated to Vol share / GP share / GP/kg with every 2027-plan account placed 30 Oct 2026.")
open(out, 'w', encoding='utf-8').write(s); print('written', len(s))
