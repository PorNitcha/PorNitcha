# Add an Indonesia highlight to the published quadrant page (works on the saved artifact HTML, not the template)
import sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
n0 = len(s)
R = [
 # control
 ("""    <label class="ctl" for="lbl">Labels &ge;""",
  """    <label class="ctl" for="hiID" style="font-weight:600;color:var(--fg)"><input type="checkbox" id="hiID" checked> Highlight Indonesia</label>
    <label class="ctl" for="lbl">Labels &ge;"""),
 # state
 ("let base = 25, basis = 'gpp', FLOOR = 4700, minT = 100, lblT = 1000;",
  "let base = 25, basis = 'gpp', FLOOR = 4700, minT = 100, lblT = 1000, hiID = true;\nconst isID = d => (d.country||'').trim()==='Indonesia' || /THAI WAH INDONESIA/i.test(d.name);"),
 # bubbles: dim others, ring + always label Indonesia
 ("""    s += `<circle data-i="${DATA.indexOf(d)}" cx="${p.x}" cy="${p.y}" r="${p.r}" fill="${col[r]}" fill-opacity=".62" stroke="${p.clipped?'var(--fg-2)':'var(--panel)'}" stroke-width="2"${p.clipped?' stroke-dasharray="3 3"':''}/>`; });""",
  """    const id = isID(d), dim = hiID && !id;
    s += `<circle data-i="${DATA.indexOf(d)}" cx="${p.x}" cy="${p.y}" r="${p.r}" fill="${col[r]}" fill-opacity="${dim?'.18':'.62'}" stroke="${id?'var(--fg)':(p.clipped?'var(--fg-2)':'var(--panel)')}" stroke-width="${id?3.5:2}"${p.clipped?' stroke-dasharray="3 3"':''}/>`;
    if (id) s += `<circle cx="${p.x}" cy="${p.y}" r="${p.r+5}" fill="none" stroke="var(--fg)" stroke-width="1.5" stroke-dasharray="2 3" pointer-events="none"/>`; });"""),
 ("""  sorted.forEach(d=>{ if (d.t27>=lblT){ const p=pos(d); const x=p.x, y=p.y, r=p.r;
    s += `<text x="${x+r+3}" y="${y+4}" ${x+r+90>W?`text-anchor="end" x="${x-r-3}"`:''}>${esc(short(d.name))}</text>`; }});""",
  """  sorted.forEach(d=>{ const id = isID(d); if (d.t27>=lblT || id){ const p=pos(d); const x=p.x, y=p.y, r=p.r; const dim = hiID && !id;
    s += `<text x="${x+r+3}" y="${y+4}" ${x+r+90>W?`text-anchor="end" x="${x-r-3}"`:''} ${id?'font-weight="700" font-size="11.5"':''} fill="${dim?'var(--fg-3)':'var(--fg)'}">${id?'🇮🇩 ':''}${esc(short(d.name))}</text>`; }});"""),
 # Indonesia panel under the roles
 ("""    return `<div class="role ${r}"><div class="name">${roleName[r]}</div><div class="num">${a.n} accounts · ${fmt(a.t)} t · ${total?Math.round(a.t/total*100):0}% of plan shown</div><div class="list">${names}${a.list.length>8?' …':''}</div></div>`; }).join('');
}""",
  """    return `<div class="role ${r}"><div class="name">${roleName[r]}</div><div class="num">${a.n} accounts · ${fmt(a.t)} t · ${total?Math.round(a.t/total*100):0}% of plan shown</div><div class="list">${names}${a.list.length>8?' …':''}</div></div>`; }).join('');
  // Indonesia: where each account sits on this base
  const ids = DATA.filter(d=>isID(d) && d.t27>0).sort((a,b)=>b.t27-a.t27);
  const idT = ids.reduce((a,d)=>a+d.t27,0), allT = DATA.filter(d=>d.t27>0).reduce((a,d)=>a+d.t27,0);
  const byRole = {}; ids.forEach(d=>{ const r=roleOf(d); byRole[r]=(byRole[r]||0)+d.t27; });
  const roleLine = ['fix','reprice','grow','protect','new'].filter(r=>byRole[r]).map(r=>`<span style="color:${col[r]};font-weight:600">${roleName[r]}</span> ${fmt(byRole[r])} t`).join(' · ');
  const rowsHtml = ids.map(d=>{ const r=roleOf(d); const gp=baseGp(d); const g=d.t27-baseT(d);
    return `<tr><td style="font-family:var(--font)">${esc(short(d.name))}</td><td><span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${col[r]};margin-right:5px;vertical-align:-1px"></span>${roleName[r]}</td><td>${fmt(d.t27)}</td><td>${gp==null?'–':fmt(gp)}</td><td>${gp==null?'–':sgn(g)}</td></tr>`; }).join('');
  document.getElementById('idpanel').innerHTML = `<div class="eyebrow">🇮🇩 Indonesia on this base</div>
    <div class="num" style="font-family:var(--mono);font-size:12px;color:var(--fg-2);margin:4px 0 6px">${ids.length} accounts · ${fmt(idT)} t = ${allT?Math.round(idT/allT*100):0}% of the 2027 plan</div>
    <div style="font-size:12px;margin-bottom:6px">${roleLine}</div>
    <table style="font-size:12px"><thead><tr><th style="text-align:left">Account</th><th style="text-align:left">Quadrant</th><th>2027 t</th><th>GP/t base</th><th>Δ t vs base</th></tr></thead><tbody>${rowsHtml}</tbody></table>
    <div class="foot" style="margin-top:6px">Indonesia = TDC direct export accounts in Indonesia plus PT Thai Wah Indonesia (intercompany). Bubbles with a dark ring; other accounts are dimmed while the highlight is on.</div>`;
}"""),
 # panel placeholder in the roles column
 ("""      <h2>Four roles on this base</h2>
      <div class="roles" id="roles"></div>""",
  """      <h2>Four roles on this base</h2>
      <div class="roles" id="roles"></div>
      <div id="idpanel" style="margin-top:14px;padding-top:12px;border-top:1px solid var(--line)"></div>"""),
 # migration chart: bold Indonesia names
 ("""    s += `<text x="${m.l-10}" y="${y+4}" text-anchor="end" font-size="11.5" fill="var(--fg)">${esc(short(d.name))} <tspan fill="var(--fg-3)">${fmt(d.t27)} t</tspan></text>`;""",
  """    s += `<text x="${m.l-10}" y="${y+4}" text-anchor="end" font-size="11.5" ${isID(d)?'font-weight="700"':''} fill="var(--fg)">${isID(d)?'🇮🇩 ':''}${esc(short(d.name))} <tspan fill="var(--fg-3)">${fmt(d.t27)} t</tspan></text>`;"""),
 # listener
 ("document.getElementById('lbl').addEventListener('change',e=>{ lblT=+e.target.value; drawQuad(); });",
  "document.getElementById('lbl').addEventListener('change',e=>{ lblT=+e.target.value; drawQuad(); });\ndocument.getElementById('hiID').addEventListener('change',e=>{ hiID=e.target.checked; drawQuad(); });"),
 # table: Indonesia rows bold
 ("""  document.querySelector('#tbl tbody').innerHTML = rows.map(d=>`<tr><td>${esc(d.name)}</td>""",
  """  document.querySelector('#tbl tbody').innerHTML = rows.map(d=>`<tr${isID(d)?' style="font-weight:700;background:var(--grow-soft)"':''}><td>${esc(d.name)}</td>"""),
]
for a, b in R:
    assert a in s, a[:80]
    s = s.replace(a, b, 1)
open(out, 'w', encoding='utf-8').write(s)
print('patched', n0, '->', len(s))
