# Add a TWIN-customer quadrant section to the quadrant artifact (Por 30-Oct). Same rules as the PPT TWIN pages:
# y = TDC-leg GP/kg (product, or full when the GP basis is full cost) vs the same line as the TDC chart (base-year TDC average by default),
# x = volume vs prior year (FY2025 vs FY2024 / YTD Sep-26 vs YTD Sep-25), new customers count as growing; boxes = Heinz / Wings / Bumi Tirta / the rest.
# Usage: python _patch_quad_twin_section.py <page.html> <twin_quad.json>
import sys, json
p, tq = sys.argv[1], sys.argv[2]
s = open(p, encoding='utf-8').read()
TW = json.load(open(tq, encoding='utf-8'))
def rep(a, b, n=1):
    global s
    assert s.count(a) >= n, a[:90]
    s = s.replace(a, b, n)
# 1) HTML section, before the migration chart
rep('  <div class="section panel">\n    <h2 id="mTitle">', '''  <div class="section panel">
    <h2 id="tTitle">TWIN customers</h2>
    <p class="sub">PT Thai Wah Indonesia's customers buying TDC products. Same line as the chart above, on TDC's own leg of the margin; the boxes add TWIN's trading margin to show the combined chain.</p>
    <div class="chart" id="twinq"></div>
    <div class="legend">
      <span style="--c:var(--fix)">Fix price before volume</span>
      <span style="--c:var(--grow)">Grow with margin</span>
      <span style="--c:var(--protect)">Protect</span>
      <span style="--c:var(--neutral)">Reprice / exit</span>
    </div>
    <div class="foot" id="twinFoot"></div>
  </div>

  <div class="section panel">
    <h2 id="mTitle">''')
# 2) data + drawing code, before drawMig
code = r'''
// ---- TWIN customers quadrant (Por 30-Oct) ----
const TW = __TW__;   // per customer: [tonnes, TDC product GP, TDC full GP, TWIN GP, combined product GP, combined full GP] for y24, y25, p25 (YTD Sep-25), y26 (YTD Sep-26)
const TW_GROUPS = ['Heinz', 'Wings', 'Bumi Tirta', 'The rest'];
const twShort = n => n.replace(/^PT\.?\s*/i,'').replace(/,?\s*(PT|CV|TBK)\.?\s*$/i,'').replace(/HEINZ ABC INDONESIA/i,'Heinz ABC').replace(/BUMI TIRTA PANGAN KENCANA/i,'Bumi Tirta').trim().split(' ').map(w=>w.length>3?w.charAt(0)+w.slice(1).toLowerCase():w).join(' ').slice(0,24);
function drawTwin(){
  const W=780, H=500, m={l:70,r:20,t:30,b:48};
  const cur = base===25 ? 'y25' : 'y26', prv = base===25 ? 'y24' : 'p25';
  const full = basis==='gpf'; const iT = full ? 2 : 1, iC = full ? 5 : 4;
  const rows = TW.filter(d=>d[cur][0]>=5).map(d=>{ const t=d[cur][0], tp=d[prv][0];
    return {d, t, tp, g: t-tp, isNew: tp<5, tdc: d[cur][iT]/t/1000, twin: d[cur][3]/t/1000, comb: d[cur][iC]/t/1000, gpC: d[cur][iC], gpT: d[cur][iT], gpW: d[cur][3]}; });
  const L = FLOOR/1000;
  const roleT = r => r.tdc >= L ? ((r.g>0 || r.isNew) ? 'grow' : 'protect') : ((r.g>0 || r.isNew) ? 'fix' : 'reprice');
  const gs = rows.map(r=>r.g), ys = rows.map(r=>r.tdc);
  const xmin = Math.min(-300, Math.floor(Math.min(...gs)/100)*100-100), xmax = Math.max(600, Math.ceil(Math.max(...gs)/100)*100+150);
  const ymin = Math.max(-4, Math.min(-1, Math.floor(Math.min(...ys))-1)), ymax = Math.min(16, Math.max(10, Math.ceil(Math.max(...ys))+1));
  const sx = v => m.l + (Math.max(xmin,Math.min(xmax,v))-xmin)/(xmax-xmin)*(W-m.l-m.r);
  const sy = v => m.t + (ymax-Math.max(ymin,Math.min(ymax,v)))/(ymax-ymin)*(H-m.t-m.b);
  const maxT = Math.max(...rows.map(r=>r.t)); const rad = t => 4 + 26*Math.sqrt(t/maxT);
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="TWIN customer quadrant: TDC-leg GP per kg against volume change versus the prior year">`;
  s += `<rect x="${m.l}" y="${m.t}" width="${sx(0)-m.l}" height="${sy(L)-m.t}" fill="var(--protect-soft)"/><rect x="${sx(0)}" y="${m.t}" width="${W-m.r-sx(0)}" height="${sy(L)-m.t}" fill="var(--grow-soft)"/>`;
  s += `<rect x="${sx(0)}" y="${sy(L)}" width="${W-m.r-sx(0)}" height="${H-m.b-sy(L)}" fill="var(--fix-soft)"/><rect x="${m.l}" y="${sy(L)}" width="${sx(0)-m.l}" height="${H-m.b-sy(L)}" fill="var(--neutral-soft)"/>`;
  for (let y=Math.ceil(ymin/2)*2; y<=ymax; y+=2){ s += `<line x1="${m.l}" x2="${W-m.r}" y1="${sy(y)}" y2="${sy(y)}" stroke="var(--grid)"/><text x="${m.l-8}" y="${sy(y)+4}" text-anchor="end" font-size="11" fill="var(--fg-3)">${y}</text>`; }
  const xstep = (xmax-xmin) > 1500 ? 500 : 250;
  for (let x=Math.ceil(xmin/xstep)*xstep; x<=xmax; x+=xstep){ s += `<text x="${sx(x)}" y="${H-m.b+18}" text-anchor="middle" font-size="11" fill="var(--fg-3)">${x>0?'+':''}${fmt(x)}</text>`; }
  s += `<line x1="${m.l}" x2="${W-m.r}" y1="${sy(L)}" y2="${sy(L)}" stroke="var(--fg-2)" stroke-dasharray="4 4"/><line x1="${sx(0)}" x2="${sx(0)}" y1="${m.t}" y2="${H-m.b}" stroke="var(--fg-2)"/>`;
  s += `<text x="${m.l-8}" y="${sy(L)+4}" text-anchor="end" font-size="11" font-weight="600" fill="var(--fg)">${L.toFixed(1)}</text>`;
  s += `<text x="${m.l+6}" y="${sy(L)-5}" font-size="10" fill="var(--fg-2)" stroke="var(--panel)" stroke-width="3" stroke-linejoin="round" paint-order="stroke">${floorMode==='avg' ? (base===25?'2025':'2026 YTD')+' TDC average '+L.toFixed(1)+' THB/kg' : 'floor '+L.toFixed(1)+' THB/kg'}</text>`;
  s += `<text x="${(m.l+W-m.r)/2}" y="${H-6}" text-anchor="middle" font-size="11" fill="var(--fg-2)">${base===25?'FY2025 vs FY2024':'YTD Sep-26 vs YTD Sep-25'}, tonnes (new customers count as growing) →</text>`;
  s += `<text transform="translate(14 ${(m.t+H-m.b)/2}) rotate(-90)" text-anchor="middle" font-size="11" fill="var(--fg-2)">TDC-leg ${full?'full-cost':'product'} GP per kg ${base===25?'2025':'2026 YTD'}, THB/kg</text>`;
  const sorted = [...rows].sort((a,b)=>b.t-a.t);
  const pos = r => { const rr = rad(r.t); const x = Math.max(m.l+rr, Math.min(W-m.r-rr, sx(r.isNew ? Math.max(r.g, 0) : r.g))); const y = Math.max(m.t+rr, Math.min(H-m.b-rr, sy(r.tdc))); return {x, y, r: rr}; };
  s += `<g id="twbubbles">`;
  sorted.forEach((r,i)=>{ const p=pos(r); const key = r.d.grp!=='The rest';
    s += `<circle data-k="${i}" cx="${p.x}" cy="${p.y}" r="${p.r}" fill="${col[roleT(r)]}" fill-opacity="${key?'.8':'.55'}" stroke="${key?'var(--fg)':'var(--panel)'}" stroke-width="${key?1.2:1.5}"${r.isNew?' stroke-dasharray="3 2"':''}/>`; });
  s += `</g>`;
  // boxes: one row per group present in the quadrant
  const totT = rows.reduce((a,r)=>a+r.t,0), totG = rows.reduce((a,r)=>a+r.gpC,0);
  const circles = sorted.map(pos);
  const BW=244, lower=sy(L);
  const box = {}; ['protect','grow','fix','reprice'].forEach(k=>{ const rs = rows.filter(r=>roleT(r)===k);
    box[k] = {n: rs.length, groups: TW_GROUPS.map(g=>{ const x = rs.filter(r=>r.d.grp===g); const t=x.reduce((a,r)=>a+r.t,0);
      return {g, n:x.length, t, v:t/totT, gp:x.reduce((a,r)=>a+r.gpC,0)/totG, tdc: t?x.reduce((a,r)=>a+r.gpT,0)/t/1000:null, twin: t?x.reduce((a,r)=>a+r.gpW,0)/t/1000:null, comb: t?x.reduce((a,r)=>a+r.gpC,0)/t/1000:null}; }).filter(x=>x.n)}; });
  const BHof = k => 34 + Math.max(1, box[k].groups.length)*11;
  const region = {protect:[m.l+4, sx(0)-BW-4, m.t+4, lower-4], grow:[sx(0)+4, W-m.r-BW-4, m.t+4, lower-4], reprice:[m.l+4, sx(0)-BW-4, lower+4, H-m.b], fix:[sx(0)+4, W-m.r-BW-4, lower+4, H-m.b]};
  const corner = {protect:'tl', grow:'tr', reprice:'bl', fix:'br'};
  const boxRects = [];
  const cover = (x,y,bh) => circles.reduce((acc,c)=>{ const ox=Math.max(0, Math.min(x+BW, c.x+c.r) - Math.max(x, c.x-c.r)); const oy=Math.max(0, Math.min(y+bh, c.y+c.r) - Math.max(y, c.y-c.r)); return acc + ox*oy*(c.r>=12 ? 1000 : 1); }, 0);
  const lab = {protect:['PROTECT','var(--protect)'], grow:['GROW WITH MARGIN','var(--grow)'], fix:['FIX PRICE BEFORE VOLUME','var(--fix)'], reprice:['REPRICE / EXIT','var(--fg-2)']};
  const sh = (a) => !a ? '–' : (a < 0.005 ? '<1%' : Math.round(a*100)+'%');
  const k1 = v => v==null ? '–' : v.toFixed(1);
  s += `<g id="twstats" font-family="var(--font)">`;
  ['protect','grow','fix','reprice'].forEach(k=>{ const bh = BHof(k); const [x0,x1r,y0,y1r] = region[k]; const x1=Math.max(x0,x1r), y1=Math.max(y0, y1r-bh);
    const c = corner[k]; const cx = c[1]==='l' ? x0 : x1, cy = c[0]==='t' ? y0 : y1;
    let best=[cx,cy], bs=Infinity; const nx=Math.max(1,Math.ceil((x1-x0)/6)), ny=Math.max(1,Math.ceil((y1-y0)/6));
    for (let i=0;i<=nx;i++) for (let j=0;j<=ny;j++){ const x=x0+(x1-x0)*i/nx, y=y0+(y1-y0)*j/ny; const sc=cover(x,y,bh)+2*Math.hypot(x-cx,y-cy); if (sc<bs){ bs=sc; best=[x,y]; } }
    const [x,y] = best; boxRects.push([x,y,BW,bh]);
    const cV=x+120, cG=x+150, cT=x+180, cW=x+208, cC=x+BW-7;
    s += `<rect x="${x}" y="${y}" width="${BW}" height="${bh}" rx="4" fill="var(--panel)" fill-opacity=".9" stroke="${lab[k][1]}" stroke-opacity=".35"/>`;
    s += `<text x="${x+7}" y="${y+13}" font-size="10" font-weight="600" fill="${lab[k][1]}">${lab[k][0]}</text><text x="${cC}" y="${y+13}" text-anchor="end" font-size="8.5" fill="var(--fg-3)">${box[k].n} customers</text>`;
    s += `<g font-size="8.5" fill="var(--fg-3)" text-anchor="end"><text x="${cV}" y="${y+26}">Vol %</text><text x="${cG}" y="${y+26}">GP %</text><text x="${cT}" y="${y+26}">TDC</text><text x="${cW}" y="${y+26}">TWIN</text><text x="${cC}" y="${y+26}">Comb</text></g>`;
    s += `<line x1="${x+7}" x2="${cC}" y1="${y+29}" y2="${y+29}" stroke="var(--fg-3)" stroke-width=".6"/>`;
    if (!box[k].groups.length) s += `<text x="${x+7}" y="${y+40}" font-size="9.5" fill="var(--fg-3)">–</text>`;
    box[k].groups.forEach((gq,i)=>{ const yy=y+40+i*11; const c = gq.g==='The rest' ? 'var(--fg)' : 'var(--indo)';
      s += `<g font-size="9.5" fill="${c}"><text x="${x+7}" y="${yy}">${gq.g}${gq.g==='The rest'?` (${gq.n})`:''}</text><g text-anchor="end" font-family="var(--mono)"><text x="${cV}" y="${yy}">${sh(gq.v)}</text><text x="${cG}" y="${yy}">${sh(gq.gp)}</text><text x="${cT}" y="${yy}">${k1(gq.tdc)}</text><text x="${cW}" y="${yy}">${k1(gq.twin)}</text><text x="${cC}" y="${yy}">${k1(gq.comb)}</text></g></g>`; }); });
  s += `</g>`;
  // names: key customers always, others from 50 t; placed after the boxes, away from boxes and other names
  const ovA = (a,b) => Math.max(0, Math.min(a[0]+a[2], b[0]+b[2]) - Math.max(a[0], b[0])) * Math.max(0, Math.min(a[1]+a[3], b[1]+b[3]) - Math.max(a[1], b[1]));
  const labelRects = [];
  s += `<g font-size="10.5" fill="var(--fg)" stroke="var(--panel)" stroke-width="3" stroke-linejoin="round" paint-order="stroke">`;
  sorted.filter(r=>r.d.grp!=='The rest' || r.t>=50).forEach(r=>{ const p=pos(r); const x=p.x, y=p.y, rr=p.r; const txt=twShort(r.d.name); const w=textW(txt)+4, h=15;
    const opts = [[x+rr+3, y+4, 'start'], [x-rr-3, y+4, 'end'], [x, y-rr-4, 'middle'], [x, y+rr+12, 'middle'], [x+rr+3, y+17, 'start'], [x+rr+3, y-9, 'start'], [x-rr-3, y+17, 'end'], [x-rr-3, y-9, 'end'], [x, y-rr-16, 'middle'], [x, y+rr+24, 'middle']];
    const rectOf = ([tx,ty,an]) => [an==='start'?tx:(an==='end'?tx-w:tx-w/2), ty-11.5, w, h];
    const cost = o => { const rc=rectOf(o); const out=(rc[0]<m.l||rc[0]+rc[2]>W-m.r||rc[1]<m.t||rc[1]+rc[3]>H-m.b)?1e6:0; return out + labelRects.reduce((a,q)=>a+ovA(q,rc),0) + 2*boxRects.reduce((a,q)=>a+ovA(q,rc),0); };
    let o=opts[0], bc=Infinity; for (const c of opts){ const kk=cost(c); if (kk<bc){ bc=kk; o=c; } if (kk===0) break; }
    labelRects.push(rectOf(o));
    s += `<text x="${o[0]}" y="${o[1]}" text-anchor="${o[2]}"${r.d.grp!=='The rest'?' font-weight="600" fill="var(--indo)"':''}>${esc(txt)}</text>`; });
  s += `</g></svg><div class="tip" hidden></div>`;
  const el = document.getElementById('twinq'); el.innerHTML = s;
  const tip = el.querySelector('.tip');
  el.querySelectorAll('#twbubbles circle').forEach(c=>{ const r = sorted[+c.dataset.k];
    const show = ev => { tip.innerHTML = `<b>${esc(r.d.name)}</b> <span style="color:var(--fg-3)">· ${r.d.grp}</span><br><span class="mono">Tonnes ${base===25?'FY2024 '+fmt(r.tp)+' → FY2025 ':'YTD Sep-25 '+fmt(r.tp)+' → YTD Sep-26 '}${fmt(r.t)}${r.isNew?' (new)':''}</span><br><span class="mono">GP/kg TDC ${r.tdc.toFixed(2)} + TWIN ${r.twin.toFixed(2)} = ${r.comb.toFixed(2)}</span>`; tip.hidden=false;
      const b = el.getBoundingClientRect(); let x = ev.clientX-b.left+14, y = ev.clientY-b.top+14; if (x+310>b.width) x = ev.clientX-b.left-320; tip.style.left=x+'px'; tip.style.top=y+'px'; };
    c.addEventListener('mouseenter', show); c.addEventListener('mousemove', show); c.addEventListener('mouseleave', ()=>{ tip.hidden=true; }); });
  const tt = rows.reduce((a,r)=>a+r.t,0);
  document.getElementById('tTitle').textContent = `TWIN customers · ${base===25?'FY2025 vs FY2024':'YTD Sep-26 vs YTD Sep-25'} · ${fmt(tt)} t · GP/kg TDC ${(rows.reduce((a,r)=>a+r.gpT,0)/tt/1000).toFixed(1)} + TWIN ${(rows.reduce((a,r)=>a+r.gpW,0)/tt/1000).toFixed(1)} = ${(totG/tt/1000).toFixed(1)}`;
  document.getElementById('twinFoot').innerHTML = `Bubble area = ${base===25?'FY2025':'YTD Sep-26'} tonnes; customers with 5 t or more of TDC products shown (${rows.length}). Height = TDC's ${full?'full-cost':'product'} GP per kg on sales to these customers (allocated by SKU and quarter), against the same line as the TDC chart. Dashed ring = new customer (no prior-year volume), counted as growing. Boxes: Vol % and GP % = share of the TWIN book shown (GP = combined TDC + TWIN), GP/kg = TDC leg + TWIN trading margin = combined. Wings = Glico Wings, Karunia Alam Segar, Prakarsa Alam Segar. Native, sago, Fibioca and coarse flour excluded; Harum Sari (non-TDC product) is outside this view.`;
}
'''.replace('__TW__', json.dumps(TW, ensure_ascii=False))
rep("\nfunction drawMig(){", code + "\nfunction drawMig(){")
# 3) redraw hooks
rep("drawQuad(); drawMig(); });", "drawQuad(); drawMig(); drawTwin(); });", 4)
rep("drawQuad(); drawMig(); drawTable();\nif (document.fonts && document.fonts.ready) document.fonts.ready.then(()=>drawQuad());",
    "drawQuad(); drawMig(); drawTable(); drawTwin();\nif (document.fonts && document.fonts.ready) document.fonts.ready.then(()=>{ drawQuad(); drawTwin(); });")
open(p, 'w', encoding='utf-8').write(s); print('ok', len(s))
