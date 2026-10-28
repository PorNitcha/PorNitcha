import csv,re,json,shutil,sys
from datetime import date,timedelta
CSV='memory/root-price-history.csv'
shutil.copy(CSV,CSV+'.bak_1015r1')
rows=list(csv.DictReader(open(CSV,encoding='utf-8')))
H=['date','plant','price_thb_kg','volume_tons','starch_pct','cag_thb_kg','recovery_pct']
R={(r['date'],r['plant']):r for r in rows}
def up(d,p,pr='',v='',st='',cag='',rec=''):
    R[(d,p)]=dict(date=d,plant=p,price_thb_kg=pr,volume_tons=v,starch_pct=st,cag_thb_kg=cag,recovery_pct=rec)
# backfill: TKT 13-Oct real recovery (R1 104.7 / R2 99.2 differ)
old=R[('2026-10-13','TKT')]; up('2026-10-13','TKT',old['price_thb_kg'],old['volume_tons'],old['starch_pct'],'15.86','102.1')
# new day 14-Oct (T-1)
D='2026-10-14'
up(D,'TN','3.76','553','24.91'); up(D,'TKT','3.89','743','23.53'); up(D,'PM','3.74','182','24.99'); up(D,'MS','4.20','533','28.54')
up(D,'TDC'); up(D,'TWIC')
plants=['TN','TKT','PM','MS','TDC','TWIC']
dates=sorted({k[0] for k in R})
dates=dates[-30:]
assert len(dates)==30 and dates[-1]==D and dates[0]=='2026-09-15',dates
out=[R[(d,p)] for d in dates for p in plants]
assert len(out)==180
with open(CSV,'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,H,lineterminator='\r\n' if False else '\n'); w.writeheader(); w.writerows(out)
R={(r['date'],r['plant']):r for r in out}
f=lambda d,p,k:(None if R[(d,p)][k]=='' else float(R[(d,p)][k]))
# CBG/CAG check
bad=[]
for d in dates:
    for p in plants:
        pr,st,cg,rc=f(d,p,'price_thb_kg'),f(d,p,'starch_pct'),f(d,p,'cag_thb_kg'),f(d,p,'recovery_pct')
        if pr and st and rc and cg and abs(pr/(st/100)/(rc/100)-cg)>0.05: bad.append((d,p,pr/(st/100)/(rc/100),cg))
print('CAG check mismatches >0.05:',bad)
def lab(d):
    y,m,dd=map(int,d.split('-')); return f"{dd}-{['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct'][m]}"
dl=[lab(d) for d in dates]
fn_old='Daily root dashboard - 13 October 2026.html'; fn_new='Daily root dashboard - 14 October 2026.html'
t=open(fn_old,encoding='utf-8').read()
def arr(p,k):
    return json.dumps([(int(v) if (k=='volume_tons' and v is not None) else v) for v in [f(d,p,k) for d in dates]])
for p in plants:
    i=t.find(f'  {p}: {{ label: "{p}"'); j=t.find('\n  },',i) if p!='TWIC' else t.find('\n  },\n};',i)
    blk=t[i:j]
    for name,k in (('price','price_thb_kg'),('volume','volume_tons'),('starch','starch_pct'),('cag','cag_thb_kg'),('recov','recovery_pct')):
        blk,n=re.subn(r'(\n    %s:\s+)\[[^\]]*\]'%name,lambda m:m.group(1)+arr(p,k),blk,count=1); assert n==1,(p,name)
    t=t[:i]+blk+t[j:]
t,n=re.subn(r'const dates = \[[^\]]*\];','const dates = '+json.dumps(dl)+';',t,count=1); assert n==1
# ---- aggregates
def pv(d,p): return f(d,p,'volume_tons')
def agg(d,ps):
    ps=[p for p in ps if pv(d,p)]; v=sum(pv(d,p) for p in ps)
    pr=sum(pv(d,p)*f(d,p,'price_thb_kg') for p in ps)/v; st=sum(pv(d,p)*f(d,p,'starch_pct') for p in ps)/v
    return v,pr,st,pr/(st/100)
TH=['TN','TKT','PM','MS','TDC']
v14,p14,s14,c14=agg(D,TH)
d13='2026-10-13'
same=['TKT','PM','MS']
v13,p13,s13,c13=agg(d13,same); v14s,p14s,s14s,c14s=agg(D,same)
G=['TN','TKT','PM','TDC']
def cagtot(d):
    ps=[p for p in G if pv(d,p)]
    if not ps or any(f(d,p,'cag_thb_kg') is None for p in ps): return None
    v=sum(pv(d,p) for p in ps); return v,sum(pv(d,p)*f(d,p,'cag_thb_kg') for p in ps)/v,ps
lastc=None
for d in reversed(dates):
    c=cagtot(d)
    if c: lastc=(d,c); break
print('last CAG complete',lastc)
cd,(cv,cc,cps)=lastc
# ---- per plant info
def lastrec(p):
    for d in reversed(dates):
        if f(d,p,'recovery_pct') is not None: return d,f(d,p,'recovery_pct'),f(d,p,'cag_thb_kg')
def prev_price(p):
    for d in reversed(dates[:-1]):
        if f(d,p,'price_thb_kg') is not None and pv(d,p): return d,f(d,p,'price_thb_kg'),pv(d,p)
def pend(p): return [lab(d) for d in dates if pv(d,p) and f(d,p,'recovery_pct') is None]
names={'TN':'อ.เมือง อุดรธานี','TKT':'ท่าคันโท กาฬสินธุ์','PM':'พิมาย โคราช','MS':'แม่สอด ตาก','TDC':'บ้านฉาง ระยอง'}
def dlt(p):
    pr=f(D,p,'price_thb_kg'); d0,p0,v0=prev_price(p); x=round(pr-p0,2)
    if x>0: return 'red','up',f'+{x:.2f}',d0,p0,v0
    if x<0: return 'green','down',f'{x:.2f}',d0,p0,v0
    return 'green','flat','0.00',d0,p0,v0
reason={'TN':'%Recovery 100.0% = default','TKT':'recTotal = R1 = R2 = 95.0% = default','PM':'%Recovery 0.0% = ไม่มีข้อมูล','MS':'%Recovery 90.0% = placeholder'}
def row(p):
    if not pv(D,p):
        lr=lastrec(p)
        return f'''    <tr><td><span class="plant-name">{names[p]}</span><br><span class="plant-code">{p}</span></td>
      <td class="num">&mdash;</td><td class="num"><span class="dot grey"></span><span class="delta flat">&mdash;</span></td>
      <td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge none">ยังไม่ลงข้อมูล</span><span class="status-detail">14-Oct ไม่มีปริมาณ (ไฟล์มีราคา 4.17 / %ST 24.20% = forecast &rarr; เว้นว่าง) &middot; ผลโม่ล่าสุด {lab(lr[0])} {lr[1]:.1f}% (CAG {lr[2]:.2f}) &middot; ค้างผลโม่ {', '.join(pend(p))}</span></td>
    </tr>
'''
    c,cl,s,d0,p0,v0=dlt(p); pr=f(D,p,'price_thb_kg'); v=pv(D,p); st=f(D,p,'starch_pct')
    lr=lastrec(p); vc=(v/v0-1)*100
    ms=' &middot; ไม่นับใน CAG รวม' if p=='MS' else ''
    return f'''    <tr><td><span class="plant-name">{names[p]}</span><br><span class="plant-code">{p}</span></td>
      <td class="num">{pr:.2f}</td><td class="num"><span class="dot {c}"></span><span class="delta {cl}">{s}</span></td>
      <td class="num">{int(v):,}</td><td class="num">{st:.2f}</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge wait">รอผลโม่</span><span class="status-detail">ยังไม่มีผลโม่ 14-Oct ({reason[p]} &rarr; เว้นว่าง) &middot; CBG {pr:.2f}&divide;{st:.2f}% = {pr/(st/100):.2f} ✓{ms} &middot; เทียบ {lab(d0)} ({p0:.2f} / {int(v0):,} ตัน) ปริมาณ {vc:+.1f}% &middot; ผลโม่ล่าสุด {lab(lr[0])} {lr[1]:.1f}% (CAG {lr[2]:.2f}) &middot; ค้างผลโม่ {', '.join(pend(p))}</span></td>
    </tr>
'''
tw=lambda k:f(D,'TWIC',k)
tw_last=[d for d in dates if f(d,'TWIC','recovery_pct') is not None][-1]
tw_pend=[lab(d) for d in dates if pv(d,'TWIC') and f(d,'TWIC','recovery_pct') is None]
tbl='<table>\n'+t[t.find('<table>')+8:t.find('<tr><td><span class="plant-name">อ.เมือง'.replace('<tr>','    <tr>'))] if False else None
head_tbl=t[t.find('<table>'):t.find('    <tr><td><span class="plant-name">อ.เมือง')]
tot=f'''    <tr class="total-row"><td>รวมโรงงานไทย (14-Oct &mdash; ลงข้อมูล 4 โรง)</td>
      <td class="num">{p14:.2f}</td><td class="num"><span class="dot {'red' if p14s>p13 else 'green'}"></span><span class="delta {'up' if p14s>p13 else 'down'}">{p14s-p13:+.2f}</span></td>
      <td class="num">{int(v14):,}</td><td class="num">{s14:.2f}</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="status-detail">ราคา/%ST ถ่วงน้ำหนักทุกโรงที่ลงข้อมูล (TN, TKT, PM, MS) &middot; เทียบเฉพาะ 3 โรงเดียวกับ 13-Oct (TKT, PM, MS): {p13:.2f} &rarr; {p14s:.2f} / %ST {s13:.2f} &rarr; {s14s:.2f}% &middot; CBG {c14:.2f} &middot; <b>CAG รวม 14-Oct ปิดไม่ได้ (รอผลโม่ TN, TKT, PM; TDC ไม่ลงข้อมูล) &mdash; ล่าสุดที่ครบ = {lab(cd)} {cc:.2f} ({len(cps)} โรง {int(cv):,} ตัน)</b></span></td>
    </tr>
'''
twr=f'''    <tr><td><span class="plant-name">TWIC กัมพูชา</span><br><span class="plant-code">TWIC &middot; นิติบุคคลแยก</span></td>
      <td class="num">&mdash;</td><td class="num"><span class="dot grey"></span><span class="delta flat">&mdash;</span></td>
      <td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge none">ยังไม่ส่งข้อมูล</span><span class="status-detail">อีเมล "on Oct 14, 2026" ยังไม่เข้า (ล่าสุด = 13-Oct: 2.62 / 70 ตัน / %ST 19.63% ยังไม่มีผลโม่) &rarr; เว้นว่าง ไม่เดา &middot; ผลโม่ล่าสุด {lab(tw_last)} &middot; ค้างผลโม่ {', '.join(tw_pend)} &middot; แยกจากยอดไทย</span></td>
    </tr>
'''
newtbl=head_tbl+''.join(row(p) for p in TH)+tot+twr+'</table>'
i=t.find('<table>'); j=t.find('</table>')+8
t=t[:i]+newtbl+t[j:]
# ---- header+KPI+caveat
def pdiff(p):
    d0=prev_price(p); return f'{p} {d0[1]:.2f} &rarr; {f(D,p,"price_thb_kg"):.2f}'
ab=[]
for p in TH:
    for d in dates:
        r=f(d,p,'recovery_pct')
        if r is not None and (r<90 or r>110): ab.append(f'{p} {lab(d)} {r:.1f}%')
vols=' &middot; '.join(f'{p} {int(pv(D,p))}' for p in ['TN','TKT','PM','MS'])
pend_all=' &middot; '.join(f'{p} '+', '.join(pend(p)) for p in TH)+(' &middot; TWIC '+', '.join(tw_pend) if tw_pend else '')
hdr_i=t.find('<div class="updated">'); kpi_i=t.find('<div class="kpi-row">'); tbl_i=t.find('<table>')
import subprocess
now=subprocess.check_output(['date','+%H:%M'],env={'TZ':'Asia/Bangkok','PATH':'/usr/bin:/bin'}).decode().strip()
newhdr=f'''<div class="updated">
    ข้อมูลล่าสุด (เมื่อวาน): <b>14-Oct-2026</b> (พุธ)<br>
    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; 14-Oct: ลงข้อมูล TN + TKT + PM + MS (TDC ยังไม่ลงปริมาณ &mdash; ราคา/%ST ในไฟล์เป็น forecast &rarr; เว้นว่าง) &middot; ผลโม่ 14-Oct ยังไม่เข้า (TN 100.0% / TKT 95.0% = default / PM 0.0% / MS 90.0% = placeholder) &middot; TWIC ยังไม่ส่งของ 14-Oct</b></span><br>
    อัปเดตเมื่อ: 15-Oct-2026 {now} น. (T-1 = 14-Oct) (ไฟล์ Oct แก้ล่าสุด 14-Oct 22:51 น. &middot; ไฟล์ Sep แก้ล่าสุด 5-Oct 16:49 น. &middot; เทียบรอบก่อนหน้า: <b>ผลโม่ใหม่ TKT 13-Oct %Recovery 102.1% (CAG 15.86)</b> &middot; ตัวเลข 1&ndash;13-Oct อื่นไม่เปลี่ยน)</div>
</div>

'''
kpi=f'''<div class="kpi-row">
  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย (14-Oct &mdash; ลงข้อมูล 4 โรง)</div><div class="value">{int(v14):,}<span class="unit">ตัน &middot; <b>{vols}</b> &middot; TDC ยังไม่ลง &middot; เทียบ 3 โรงเดียวกันของ 13-Oct (TKT, PM, MS = {int(v13):,} ตัน): <b>{int(v14s):,} ตัน, {int(v14s-v13):+,}, {(v14s/v13-1)*100:+.1f}%</b></span></div></div>
  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก (14-Oct &middot; 4 โรงที่ลงข้อมูล)</div><div class="value">{p14:.2f}<span class="unit">&#3647;/กก. ({p14:.4f}) &middot; <b style="color:#b91c1c">{p14s-p13:+.2f} vs 3 โรงเดียวกัน 13-Oct ({p13:.4f})</b> &middot; เทียบข้ามองค์ประกอบโรงไม่ได้</span></div></div>
  <div class="kpi"><div class="label">%Starch เฉลี่ยถ่วงน้ำหนัก (14-Oct &middot; 4 โรงที่ลงข้อมูล)</div><div class="value">{s14:.2f}<span class="unit">% &middot; <b>{s14s-s13:+.2f} จุด</b> vs 3 โรงเดียวกัน 13-Oct ({s13:.2f}) &rarr; CBG รวม <b>{c14:.2f}</b></span></div></div>
  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = {lab(cd)} &middot; ไม่รวม MS)</div><div class="value">{cc:.2f}<span class="unit">&#3647;/กก. ({cc:.3f}) &middot; <b>{len(cps)} โรง (TN, TKT, PM, TDC) &middot; {int(cv):,} ตัน</b> &middot; <b style="color:#b45309">14-Oct รอผลโม่ TN, TKT, PM (TDC ไม่ลงข้อมูล) &middot; 13-Oct ยังไม่ลง TN + รอผลโม่ PM, TDC &middot; 12-Oct รอผลโม่ TDC</b></span></div></div>
</div>

'''
cav=f'''<div class="caveat">
  <b style="color:#b45309">&#9888; 14-Oct: ลงข้อมูล TN + TKT + PM + MS &mdash; ยังไม่มีผลโม่ใหม่ของวันนี้ (TN 100.0% = default &rarr; เว้นว่าง &middot; TKT 95.0% ทั้ง recTotal/R1/R2 = default &rarr; เว้นว่าง &middot; PM 0.0% = ไม่มีข้อมูล &rarr; เว้นว่าง &middot; MS 90.0% = placeholder &rarr; เว้นว่าง &middot; TDC ไม่ลงปริมาณ) &middot; CAG รวม 14-Oct ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = {lab(cd)}: {cc:.2f}, {len(cps)} โรง {int(cv):,} ตัน</b> &mdash; TN {f(D,'TN','price_thb_kg'):.2f} / 553 ตัน / {f(D,'TN','starch_pct'):.2f}% &middot; TKT 3.89 / 743 ตัน / 23.53% &middot; PM 3.74 / 182 ตัน / 24.99% &middot; MS 4.20 / 533 ตัน / 28.54% &middot; TDC (ไฟล์ 4.17 / 24.20%) ไม่มีปริมาณ = forecast &rarr; เว้นว่าง
  <br><b style="color:#374151">ผลโม่ใหม่/Backfill:</b> <b style="color:#b45309">TKT 13-Oct ผลโม่เข้าแล้ว 102.1% (R1 104.7% / R2 99.2%) &rarr; CAG 15.86</b> &middot; ตรวจย้อนหลัง 8&ndash;13-Oct จุดอื่น diff = 0 &middot; 13-Oct: TN ไม่ลงปริมาณ (0 &rarr; เว้นว่าง), PM 0.0% / MS 90.0% / TDC ว่าง ยังรอผลโม่
  <br><b style="color:#374151">ปริมาณ:</b> 14-Oct ลง 4 โรง รวม {int(v14):,} ตัน &mdash; เทียบ 3 โรงเดียวกัน (TKT, PM, MS) 13-Oct: {int(v13):,} &rarr; {int(v14s):,} ({int(v14s-v13):+,}, {(v14s/v13-1)*100:+.1f}%) &mdash; TKT 871 &rarr; 743 ({743-871:+d}, {(743/871-1)*100:+.1f}%) &middot; <b style="color:#b45309">PM 511 &rarr; 182 ({182-511:+d}, {(182/511-1)*100:+.1f}%)</b> &middot; MS 669 &rarr; 533 ({533-669:+d}, {(533/669-1)*100:+.1f}%) &middot; TN กลับมาลงข้อมูล 553 ตัน (12-Oct: 687, {553-687:+d}, {(553/687-1)*100:+.1f}%) &middot; TDC ไม่ลง (13-Oct: 183)
  <br><b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย 4 โรง {p14:.2f} &middot; %ST {s14:.2f}% &middot; CBG {c14:.2f} &middot; <b style="color:#b91c1c">TN +0.01 vs 12-Oct (3.75 &rarr; 3.76)</b> &middot; <b style="color:#15803d">TKT -0.02 (3.91 &rarr; 3.89)</b> &middot; <b style="color:#b91c1c">PM +0.02 (3.72 &rarr; 3.74)</b> &middot; <b style="color:#b91c1c">MS +0.01 (4.19 &rarr; 4.20)</b> &middot; verify CBG: TN 3.76&divide;24.91% = {3.76/.2491:.2f} &middot; TKT 3.89&divide;23.53% = {3.89/.2353:.2f} &middot; PM 3.74&divide;24.99% = {3.74/.2499:.2f} &middot; MS 4.20&divide;28.54% = {4.20/.2854:.2f}
  <br><span style="color:#374151">TWIC (นิติบุคคลแยก): <b>14-Oct ยังไม่ส่ง</b> (อีเมลล่าสุด "on Oct 13, 2026" ได้รับ 14-Oct 08:46 น.) &rarr; เว้นว่าง ไม่เดา &middot; 13-Oct: 70 ตัน / 2.62 / %ST 19.63% (ยังไม่มีผลโม่) &middot; ไฟล์ไม่มีแถว 9&ndash;12-Oct (อีเมล 8-Oct แจ้งหยุดเก็บเกี่ยว/ลานรับซื้อพักซื้อชั่วคราว) &middot; ยังขาดของ 24-Sep, 27-Sep</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติที่ยังไม่ถูกแก้ (ในช่วง 30 วัน, %Recovery &lt;90% หรือ &gt;110%): {' &middot; '.join(ab)}</b>
  <br><b>&#128680; ค้างผลโม่ (15-Oct-2026): {pend_all}</b>
</div>

'''
t=t[:hdr_i]+newhdr+kpi+cav+t[tbl_i:]
t=re.sub(r'แนวโน้ม 30 วันย้อนหลัง \([^)]*\)',f'แนวโน้ม 30 วันย้อนหลัง (15-Sep ถึง 14-Oct-2026)',t,count=1)
t=t.replace('ช่วง 30 วันนี้ (14-Sep ถึง 13-Oct)','ช่วง 30 วันนี้ (15-Sep ถึง 14-Oct)')
t=t.replace('(1&ndash;13-Oct) และ "09_Sep 2026" (14&ndash;30-Sep) (อ่านไฟล์รอบ 14-Oct-2026)','(1&ndash;14-Oct) และ "09_Sep 2026" (15&ndash;30-Sep) (อ่านไฟล์รอบ 15-Oct-2026)')
t=t.replace('(ล่าสุด = ของ 13-Oct ได้รับ 14-Oct 08:46 น. &middot; ไฟล์ไม่มี 9&ndash;12-Oct &middot; ยังขาดของ 24-Sep, 27-Sep)','(ล่าสุด = ของ 13-Oct ได้รับ 14-Oct 08:46 น. &middot; ของ 14-Oct ยังไม่เข้า &middot; ไฟล์ไม่มี 9&ndash;12-Oct &middot; ยังขาดของ 24-Sep, 27-Sep)')
open(fn_new,'w',encoding='utf-8').write(t)
# verify arrays vs CSV
js=re.search(r'<script>\nconst dates.*?(?=Object\.values\(plants\))',t,re.S).group(0)
open('/tmp/_chk.js','w').write(js+'\nconsole.log(JSON.stringify({dates,plants}));')
print(len(t),'bytes written',fn_new)
