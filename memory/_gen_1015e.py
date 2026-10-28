import csv,re,json,shutil,subprocess
CSV='memory/root-price-history.csv'
FN='Daily root dashboard - 14 October 2026.html'
shutil.copy(CSV,CSV+'.bak_1015r5'); shutil.copy(FN,'memory/'+FN+'.bak_1015r5')
rows=list(csv.DictReader(open(CSV,encoding='utf-8')))
H=['date','plant','price_thb_kg','volume_tons','starch_pct','cag_thb_kg','recovery_pct']
R={(r['date'],r['plant']):r for r in rows}
D='2026-10-14'
R[(D,'TDC')]=dict(date=D,plant='TDC',price_thb_kg='3.74',volume_tons='321',starch_pct='23.11',cag_thb_kg='',recovery_pct='')
plants=['TN','TKT','PM','MS','TDC','TWIC']
dates=sorted({k[0] for k in R})
assert len(dates)==30 and dates[-1]==D
out=[R[(d,p)] for d in dates for p in plants]; assert len(out)==180
with open(CSV,'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,H,lineterminator='\n'); w.writeheader(); w.writerows(out)
R={(r['date'],r['plant']):r for r in out}
f=lambda d,p,k:(None if R[(d,p)][k]=='' else float(R[(d,p)][k]))
def lab(d):
    y,m,dd=map(int,d.split('-')); return f"{dd}-{['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct'][m]}"
t=open(FN,encoding='utf-8').read()
def arr(p,k): return json.dumps([(int(v) if (k=='volume_tons' and v is not None) else v) for v in [f(d,p,k) for d in dates]])
p='TDC'
i=t.find(f'  {p}: {{ label: "{p}"'); j=t.find('\n  },',i); blk=t[i:j]
for name,k in (('price','price_thb_kg'),('volume','volume_tons'),('starch','starch_pct'),('cag','cag_thb_kg'),('recov','recovery_pct')):
    blk,n=re.subn(r'(\n    %s:\s+)\[[^\]]*\]'%name,lambda m:m.group(1)+arr(p,k),blk,count=1); assert n==1
t=t[:i]+blk+t[j:]
pv=lambda d,p:f(d,p,'volume_tons')
def agg(d,ps):
    ps=[p for p in ps if pv(d,p)]; v=sum(pv(d,p) for p in ps)
    pr=sum(pv(d,p)*f(d,p,'price_thb_kg') for p in ps)/v; st=sum(pv(d,p)*f(d,p,'starch_pct') for p in ps)/v
    return v,pr,st,pr/(st/100)
TH=['TN','TKT','PM','MS','TDC']
v14,p14,s14,c14=agg(D,TH)
same=['TKT','PM','MS','TDC']; d13='2026-10-13'
v13,p13,s13,c13=agg(d13,same); v14s,p14s,s14s,c14s=agg(D,same)
G=['TN','TKT','PM','TDC']
def cagtot(d):
    ps=[p for p in G if pv(d,p)]
    if not ps or any(f(d,p,'cag_thb_kg') is None for p in ps): return None
    v=sum(pv(d,p) for p in ps); return v,sum(pv(d,p)*f(d,p,'cag_thb_kg') for p in ps)/v,ps
for d in reversed(dates):
    c=cagtot(d)
    if c: cd=d; cv,cc,cps=c; break
print('last complete',cd,cv,cc,cps,'| 14-Oct agg',v14,p14,s14,c14,'| same',v13,p13,s13,v14s,p14s,s14s)
def pend(p): return [lab(d) for d in dates if pv(d,p) and f(d,p,'recovery_pct') is None]
def lastrec(p):
    for d in reversed(dates):
        if f(d,p,'recovery_pct') is not None: return d,f(d,p,'recovery_pct'),f(d,p,'cag_thb_kg')
pr,v,st=3.74,321,23.11
d0,p0,v0='13-Oct',3.72,183; lr=lastrec('TDC'); dx=round(pr-p0,2)
tdc=f'''    <tr><td><span class="plant-name">บ้านฉาง ระยอง</span><br><span class="plant-code">TDC</span></td>
      <td class="num">{pr:.2f}</td><td class="num"><span class="dot red"></span><span class="delta up">{dx:+.2f}</span></td>
      <td class="num">{v}</td><td class="num">{st:.2f}</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge wait">รอผลโม่</span><span class="status-detail">ลงข้อมูลแล้ว (ไฟล์ล่าสุด) &middot; ยังไม่มีผลโม่ 14-Oct (%Recovery ว่าง &rarr; เว้นว่าง) &middot; CBG {pr:.2f}&divide;{st:.2f}% = {pr/(st/100):.2f} ✓ &middot; เทียบ {d0} ({p0:.2f} / {v0} ตัน) ปริมาณ {(v/v0-1)*100:+.1f}% &middot; ผลโม่ล่าสุด {lab(lr[0])} {lr[1]:.1f}% (CAG {lr[2]:.2f}) &middot; ค้างผลโม่ {', '.join(pend('TDC'))}</span></td>
    </tr>
'''
i=t.find('    <tr><td><span class="plant-name">บ้านฉาง'); j=t.find('    <tr class="total-row">')
t=t[:i]+tdc+t[j:]
col='red' if p14s>p13 else 'green'; cl='up' if p14s>p13 else 'down'
tot=f'''    <tr class="total-row"><td>รวมโรงงานไทย (14-Oct &mdash; ลงข้อมูล 5 โรง)</td>
      <td class="num">{p14:.2f}</td><td class="num"><span class="dot {col}"></span><span class="delta {cl}">{p14s-p13:+.2f}</span></td>
      <td class="num">{int(v14):,}</td><td class="num">{s14:.2f}</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="status-detail">ราคา/%ST ถ่วงน้ำหนักทุกโรงที่ลงข้อมูล (TN, TKT, PM, MS, TDC) &middot; เทียบเฉพาะ 4 โรงเดียวกับ 13-Oct (TKT, PM, MS, TDC): {p13:.2f} &rarr; {p14s:.2f} / %ST {s13:.2f} &rarr; {s14s:.2f}% &middot; CBG {c14:.2f} &middot; <b>CAG รวม 14-Oct ปิดไม่ได้ (รอผลโม่ TDC; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = {lab(cd)} {cc:.2f} ({len(cps)} โรง {int(cv):,} ตัน)</b></span></td>
    </tr>
'''
i=t.find('    <tr class="total-row">'); j=t.find('    <tr><td><span class="plant-name">TWIC')
t=t[:i]+tot+t[j:]
# header/kpi/caveat edits
now=subprocess.check_output(['date','+%H:%M'],env={'TZ':'Asia/Bangkok','PATH':'/usr/bin:/bin'}).decode().strip()
def sub(a,b):
    global t
    assert t.count(a)==1,a[:60]; t=t.replace(a,b)
sub('(TDC ยังไม่ลงปริมาณ &mdash; ราคา/%ST ในไฟล์เป็น forecast &rarr; เว้นว่าง) &middot; ผลโม่ 14-Oct เข้าครบแล้ว TN 86.3% / TKT 100.3% / PM 102.3% / MS 85.1%','&mdash; TDC ลงข้อมูลใหม่: 321 ตัน / 3.74 / %ST 23.11% ยังไม่มีผลโม่) &middot; ผลโม่ 14-Oct เข้าแล้ว TN 86.3% / TKT 100.3% / PM 102.3% / MS 85.1%')
t=t.replace('ลงข้อมูล TN + TKT + PM + MS (','ลงข้อมูล TN + TKT + PM + MS',1) if False else t
t=re.sub(r'อัปเดตเมื่อ: 15-Oct-2026 \d\d:\d\d น\. \(T-1 = 14-Oct\) \(ไฟล์ Oct แก้ล่าสุด 15-Oct 10:49 น\.',f'อัปเดตเมื่อ: 15-Oct-2026 {now} น. (T-1 = 14-Oct) (ไฟล์ Oct แก้ล่าสุด 15-Oct 11:56 น.',t,count=1)
sub('<b>TWIC 14-Oct เข้าใหม่: 108 ตัน / 2.71 / %ST 20.32% (ยังไม่มีผลโม่) &middot; ข้อมูลโรงงานไทยไม่เปลี่ยน</b>','<b>TDC 14-Oct ลงข้อมูลใหม่: 321 ตัน / 3.74 / %ST 23.11% (ยังไม่มีผลโม่ &rarr; CAG รวม 14-Oct ปิดไม่ได้) &middot; โรงอื่นไม่เปลี่ยน</b>')
# KPI
i=t.find('<div class="kpi-row">'); j=t.find('<div class="caveat">')
vols=' &middot; '.join(f'{p} {int(pv(D,p))}' for p in ['TN','TKT','PM','MS','TDC'])
kpi=f'''<div class="kpi-row">
  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย (14-Oct &mdash; ลงข้อมูล 5 โรง)</div><div class="value">{int(v14):,}<span class="unit">ตัน &middot; <b>{vols}</b> &middot; เทียบ 4 โรงเดียวกันของ 13-Oct (TKT, PM, MS, TDC = {int(v13):,} ตัน): <b>{int(v14s):,} ตัน, {int(v14s-v13):+,}, {(v14s/v13-1)*100:+.1f}%</b></span></div></div>
  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก (14-Oct &middot; 5 โรง)</div><div class="value">{p14:.2f}<span class="unit">&#3647;/กก. ({p14:.4f}) &middot; <b style="color:#{'b91c1c' if p14s>p13 else '15803d'}">{p14s-p13:+.2f} vs 4 โรงเดียวกัน 13-Oct ({p13:.4f})</b> &middot; เทียบข้ามองค์ประกอบโรงไม่ได้</span></div></div>
  <div class="kpi"><div class="label">%Starch เฉลี่ยถ่วงน้ำหนัก (14-Oct &middot; 5 โรง)</div><div class="value">{s14:.2f}<span class="unit">% &middot; <b>{s14s-s13:+.2f} จุด</b> vs 4 โรงเดียวกัน 13-Oct ({s13:.2f}) &rarr; CBG รวม <b>{c14:.2f}</b></span></div></div>
  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = {lab(cd)} &middot; ไม่รวม MS)</div><div class="value">{cc:.2f}<span class="unit">&#3647;/กก. ({cc:.3f}) &middot; <b>{len(cps)} โรง (TN, TKT, PM, TDC) &middot; {int(cv):,} ตัน</b> &middot; <b style="color:#b45309">14-Oct รอผลโม่ TDC &middot; 13-Oct ยังไม่ลง TN + รอผลโม่ PM, TDC &middot; 12-Oct รอผลโม่ TDC</b></span></div></div>
</div>

'''
t=t[:i]+kpi+t[j:]
sub('&mdash; ผลโม่ 14-Oct เข้าครบแล้ว: <b','&mdash; ผลโม่ 14-Oct เข้า 4 โรง (TDC ลงข้อมูลแล้ว รอผลโม่): <b')
sub('&middot; TDC ไม่ลงปริมาณ &middot; <b>CAG รวม 14-Oct = 16.63 (TN+TKT+PM, 1,478 ตัน, ไม่รวม MS)</b></b>',f'&middot; TDC 321 ตัน รอผลโม่ &middot; <b>CAG รวม 14-Oct ปิดไม่ได้ (รอ TDC; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = {lab(cd)}: {cc:.2f}, {len(cps)} โรง {int(cv):,} ตัน</b></b>')
sub('&middot; TDC (ไฟล์ 4.17 / 24.20%) ไม่มีปริมาณ = forecast &rarr; เว้นว่าง','&middot; TDC 3.74 / 321 ตัน / 23.11%')
sub('<b style="color:#b45309">TKT 13-Oct 102.1% (CAG 15.86) &middot; ผลโม่ 14-Oct: TN/TKT/PM/MS เข้าแล้วทั้ง 4 โรง</b>','<b style="color:#b45309">TKT 13-Oct 102.1% (CAG 15.86) &middot; ผลโม่ 14-Oct: TN/TKT/PM/MS เข้าแล้ว &middot; TDC 14-Oct ลงข้อมูลใหม่ (ยังไม่มีผลโม่)</b>')
i=t.find('<b style="color:#374151">ปริมาณ:</b>'); j=t.find('<br>',i)
t=t[:i]+f'<b style="color:#374151">ปริมาณ:</b> 14-Oct ลง 5 โรง รวม {int(v14):,} ตัน &mdash; เทียบ 4 โรงเดียวกัน (TKT, PM, MS, TDC) 13-Oct: {int(v13):,} &rarr; {int(v14s):,} ({int(v14s-v13):+,}, {(v14s/v13-1)*100:+.1f}%) &mdash; TKT 871 &rarr; 743 (-128, -14.7%) &middot; <b style="color:#b45309">PM 511 &rarr; 182 (-329, -64.4%)</b> &middot; MS 669 &rarr; 533 (-136, -20.3%) &middot; TDC 183 &rarr; 321 (+138, +75.4%) &middot; TN กลับมาลงข้อมูล 553 ตัน (12-Oct: 687, -134, -19.5%)\n  '+t[j:]
sub('ราคาเฉลี่ย 4 โรง 3.92 &middot; %ST 25.37% &middot; CBG 15.46',f'ราคาเฉลี่ย 5 โรง {p14:.2f} &middot; %ST {s14:.2f}% &middot; CBG {c14:.2f}')
sub('&middot; MS 4.20&divide;28.54% = 14.72','&middot; MS 4.20&divide;28.54% = 14.72 &middot; <b style="color:#b91c1c">TDC +0.02 vs 13-Oct (3.72 &rarr; 3.74)</b> &middot; TDC 3.74&divide;23.11% = 16.18')
pa=' &middot; '.join(f'{p} '+', '.join(pend(p)) for p in TH)+' &middot; TWIC 26-Sep, 13-Oct, 14-Oct'
i=t.find('<b>&#128680; ค้างผลโม่ (15-Oct-2026):'); j=t.find('</b>',i)
t=t[:i]+f'<b>&#128680; ค้างผลโม่ (15-Oct-2026): {pa}'+t[j:]
open(FN,'w',encoding='utf-8').write(t)
js=re.search(r'<script>\nconst dates.*?(?=Object\.values\(plants\))',t,re.S).group(0)
open('/tmp/_chk.js','w').write(js+'\nconsole.log(JSON.stringify({dates,plants}));')
print(len(t))
