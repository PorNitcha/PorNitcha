import csv,re,json,shutil,subprocess
CSV='memory/root-price-history.csv'
OLD='Daily root dashboard - 15 October 2026.html'
NEW='Daily root dashboard - 15 October 2026.html'
shutil.copy(CSV,CSV+'.bak_1016r2'); shutil.copy(OLD,'memory/'+OLD+'.bak_1016r2')
H=['date','plant','price_thb_kg','volume_tons','starch_pct','cag_thb_kg','recovery_pct']
rows=list(csv.DictReader(open(CSV,encoding='utf-8')))
R={(r['date'],r['plant']):r for r in rows}
def setr(d,p,pr,v,st,cag='',rec=''):
    R[(d,p)]=dict(date=d,plant=p,price_thb_kg=pr,volume_tons=v,starch_pct=st,cag_thb_kg=cag,recovery_pct=rec)
def upd(d,p,rec,cag):
    r=R[(d,p)]; pr=float(r['price_thb_kg']); st=float(r['starch_pct'])
    assert abs(pr/(st/100)/(rec/100)-cag)<0.03,(d,p)
    r['recovery_pct']=('%.2f'%rec) if p=='TWIC' else ('%.1f'%rec); r['cag_thb_kg']='%.2f'%cag
upd('2026-10-15','TKT',102.0,15.97); upd('2026-10-15','PM',108.3,14.56); upd('2026-10-14','TWIC',90.02,14.80)
D='2026-10-15'

plants=['TN','TKT','PM','MS','TDC','TWIC']
dates=sorted({k[0] for k in R})[-30:]
assert dates[-1]==D and dates[0]=='2026-09-16'
out=[R[(d,p)] for d in dates for p in plants]; assert len(out)==180
with open(CSV,'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,H,lineterminator='\n'); w.writeheader(); w.writerows(out)
R={(r['date'],r['plant']):r for r in out}
f=lambda d,p,k:(None if R[(d,p)][k]=='' else float(R[(d,p)][k]))
MON=['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct']
def lab(d):
    y,m,dd=map(int,d.split('-')); return f"{dd}-{MON[m]}"
t=open(OLD,encoding='utf-8').read()
def arr(p,k): return json.dumps([(int(v) if (k=='volume_tons' and v is not None) else v) for v in [f(d,p,k) for d in dates]])
for p in plants:
    i=t.find(f'  {p}: {{ label: "{p}"'); j=t.find('\n  },',i); assert i>0 and j>i; blk=t[i:j]
    for name,k in (('price','price_thb_kg'),('volume','volume_tons'),('starch','starch_pct'),('cag','cag_thb_kg'),('recov','recovery_pct')):
        blk,n=re.subn(r'(\n    %s:\s+)\[[^\]]*\]'%name,lambda m:m.group(1)+arr(p,k),blk,count=1); assert n==1
    t=t[:i]+blk+t[j:]
t,n=re.subn(r'const dates = \[[^\]]*\];','const dates = '+json.dumps([lab(d) for d in dates])+';',t,count=1); assert n==1
pv=lambda d,p:f(d,p,'volume_tons')
TH=['TN','TKT','PM','MS','TDC']; G=['TN','TKT','PM','TDC']
def agg(d,ps):
    ps=[p for p in ps if pv(d,p)]; v=sum(pv(d,p) for p in ps)
    pr=sum(pv(d,p)*f(d,p,'price_thb_kg') for p in ps)/v; st=sum(pv(d,p)*f(d,p,'starch_pct') for p in ps)/v
    return v,pr,st,pr/(st/100)
P='2026-10-14'
v15,p15,s15,c15=agg(D,TH); v14,p14,s14,c14=agg(P,TH)
def cagtot(d):
    ps=[p for p in G if pv(d,p)]
    if not ps or any(f(d,p,'cag_thb_kg') is None for p in ps): return None
    v=sum(pv(d,p) for p in ps); return v,sum(pv(d,p)*f(d,p,'cag_thb_kg') for p in ps)/v,ps
for d in reversed(dates):
    c=cagtot(d)
    if c: cd=d; cv,cc,cps=c; break
print('last complete',cd,cv,cc,cps,'| 15',v15,p15,s15,c15,'| 14',v14,p14,s14,c14)
def pend(p): return [lab(d) for d in dates if pv(d,p) and f(d,p,'recovery_pct') is None]
def lastrec(p,before):
    for d in reversed([x for x in dates if x<before]):
        if f(d,p,'recovery_pct') is not None: return d,f(d,p,'recovery_pct'),f(d,p,'cag_thb_kg')
names={'TN':('อ.เมือง อุดรธานี','TN'),'TKT':('ท่าคันโท กาฬสินธุ์','TKT'),'PM':('พิมาย โคราช','PM'),'MS':('แม่สอด ตาก','MS'),'TDC':('บ้านฉาง ระยอง','TDC')}
why={'TN':'%Recovery = 100.0% (default ไฟล์ต้นทาง)','TKT':'R1 = R2 = รวม = 95.0% (default ไฟล์ต้นทาง)','PM':'%Recovery = 0.0% (ไม่มีข้อมูล)','MS':'%Recovery = 90.0% (placeholder ไฟล์ต้นทาง)','TDC':'%Recovery ว่าง'}
trs=''
for p in TH:
    pr,v,st=f(D,p,'price_thb_kg'),int(pv(D,p)),f(D,p,'starch_pct'); p0,v0=f(P,p,'price_thb_kg'),int(pv(P,p))
    dx=round(pr-p0,2); col,cl=('red','up') if dx>0 else ('green','down'); 
    lr=lastrec(p,D); nm,code=names[p]
    ms=' &middot; ไม่นับใน CAG รวม' if p=='MS' else ''
    cg=f(D,p,'cag_thb_kg'); rc=f(D,p,'recovery_pct')
    if rc is None:
        cgc=rcc='&mdash;'; bcls,btxt='wait','รอผลโม่'; det0=f'ลงข้อมูล 15-Oct แล้ว &middot; ยังไม่มีผลโม่ ({why[p]} &rarr; เว้นว่าง)'
    else:
        cgc=f'{cg:.2f}'; rcc=f'{rc:.1f}%'; bcls,btxt='ok','ครบ'; det0=f'ผลโม่ 15-Oct เข้าแล้ว {rc:.1f}%'+(' (R1 104.3% / R2 99.7%)' if p=='TKT' else '')+f' &middot; CAG {pr/(st/100):.2f}&divide;{rc:.1f}% = {cg:.2f} ✓'
    trs+=f'''    <tr><td><span class="plant-name">{nm}</span><br><span class="plant-code">{code}</span></td>
      <td class="num">{pr:.2f}</td><td class="num"><span class="dot {col}"></span><span class="delta {cl}">{dx:+.2f}</span></td>
      <td class="num">{v}</td><td class="num">{st:.2f}</td><td class="num">{cgc}</td><td class="num">{rcc}</td>
      <td><span class="badge {bcls}">{btxt}</span><span class="status-detail">{det0}{ms} &middot; CBG {pr:.2f}&divide;{st:.2f}% = {pr/(st/100):.2f} ✓ &middot; เทียบ 14-Oct ({p0:.2f} / {v0} ตัน) ปริมาณ {(v/v0-1)*100:+.1f}% &middot; ผลโม่ล่าสุด {lab(lr[0])} {lr[1]:.1f}% (CAG {lr[2]:.2f}) &middot; ค้างผลโม่ {', '.join(pend(p))}</span></td>
    </tr>
'''
dx=round(p15-p14,2); col,cl=('red','up') if dx>0 else ('green','down')
trs+=f'''    <tr class="total-row"><td>รวมโรงงานไทย (15-Oct &mdash; ลงข้อมูล 5 โรง)</td>
      <td class="num">{p15:.2f}</td><td class="num"><span class="dot {col}"></span><span class="delta {cl}">{p15-p14:+.2f}</span></td>
      <td class="num">{int(v15):,}</td><td class="num">{s15:.2f}</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="status-detail">ราคา/%ST ถ่วงน้ำหนักทั้ง 5 โรง (รวม MS) &middot; เทียบ 14-Oct (องค์ประกอบ 5 โรงเดียวกัน): ราคา {p14:.2f} &rarr; {p15:.2f} / %ST {s14:.2f} &rarr; {s15:.2f}% &middot; CBG {c15:.2f} &middot; <b>CAG รวม 15-Oct ปิดไม่ได้ (รอผลโม่ TN, TDC; ไม่รวม MS; TKT/PM เข้าแล้ว) &mdash; ล่าสุดที่ครบ = {lab(cd)} {cc:.2f} ({len(cps)} โรง {int(cv):,} ตัน)</b></span></td>
    </tr>
'''
l=lastrec('TWIC','9999')
trs+=f'''    <tr><td><span class="plant-name">TWIC กัมพูชา</span><br><span class="plant-code">TWIC &middot; นิติบุคคลแยก</span></td>
      <td class="num">&mdash;</td><td class="num"><span class="dot grey"></span></td>
      <td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge wait">ยังไม่ส่ง</span><span class="status-detail">ยังไม่ได้รับอีเมล TWIC ของ 15-Oct (ล่าสุด = 14-Oct: 108 ตัน / 2.71 / %ST 20.32% &middot; ผลโม่ 14-Oct เข้าแล้ว 90.02% CAG 14.80) &middot; ผลโม่ล่าสุด {lab(l[0])} &middot; ค้างผลโม่ {', '.join(pend('TWIC'))} &middot; แยกจากยอดไทย</span></td>
    </tr>
'''
i=t.find('    <tr><td><span class="plant-name">อ.เมือง'); j=t.find('</table>',i); t=t[:i]+trs+t[j:]
now=subprocess.check_output(['date','+%H:%M'],env={'TZ':'Asia/Bangkok','PATH':'/usr/bin:/bin'}).decode().strip()
vols=' &middot; '.join(f'{p} {int(pv(D,p))}' for p in TH)
chg=[]
for p in TH:
    a,b=f(D,p,'price_thb_kg'),f(P,p,'price_thb_kg'); chg.append(f"<b style=\"color:#{'b91c1c' if a>b else '15803d'}\">{p} {a-b:+.2f} ({b:.2f} &rarr; {a:.2f})</b>")
volchg=' &middot; '.join(f"{p} {int(pv(P,p))} &rarr; {int(pv(D,p))} ({int(pv(D,p)-pv(P,p)):+,}, {(pv(D,p)/pv(P,p)-1)*100:+.1f}%)" for p in TH)
gv14=cagtot(P)
hdr=f'''<div class="header">
  <div>
    <h1>สรุปราคาหัวมัน (Root Purchase) — Thaiwah Group</h1>
    <div class="sub">ข้อมูลการซื้อหัวมันจริงของ Thaiwah (Internal) — 5 โรงงานไทย + TWIC กัมพูชา</div>
  </div>
  <div class="updated">
    ข้อมูลล่าสุด (เมื่อวาน): <b>15-Oct-2026</b> (พฤหัส)<br>
    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; 15-Oct: ลงข้อมูลครบ 5 โรง ({vols}) &mdash; ผลโม่ 15-Oct เข้าแล้ว TKT 102.0% (CAG 15.97) / PM 108.3% (CAG 14.56) &middot; ยังรอ TN, MS, TDC &middot; TWIC 14-Oct ผลโม่เข้าแล้ว 90.02% (CAG 14.80) &middot; TWIC 15-Oct ยังไม่ส่ง</b></span><br>
    อัปเดตเมื่อ: 16-Oct-2026 {now} น. (T-1 = 15-Oct) (ไฟล์ Oct แก้ล่าสุด 16-Oct 09:51 น. &middot; เทียบรอบก่อนหน้า: <b>ผลโม่ใหม่ TKT 15-Oct 102.0% / PM 15-Oct 108.3% / TWIC 14-Oct 90.02%</b> &middot; ตัวเลขอื่นไม่เปลี่ยน)</div>
</div>

'''
c14t=f'CAG รวม 14-Oct = {cc:.2f} ({len(cps)} โรง {int(cv):,} ตัน)' if cd==P else ''
kpi=f'''<div class="kpi-row">
  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย (15-Oct &mdash; ลงข้อมูล 5 โรง)</div><div class="value">{int(v15):,}<span class="unit">ตัน &middot; <b>{vols}</b> &middot; เทียบ 14-Oct ({int(v14):,} ตัน): <b>{int(v15-v14):+,}, {(v15/v14-1)*100:+.1f}%</b></span></div></div>
  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก (15-Oct &middot; 5 โรง)</div><div class="value">{p15:.2f}<span class="unit">&#3647;/กก. ({p15:.4f}) &middot; <b style="color:#{'b91c1c' if p15>p14 else '15803d'}">{p15-p14:+.2f} vs 14-Oct ({p14:.4f})</b></span></div></div>
  <div class="kpi"><div class="label">%Starch เฉลี่ยถ่วงน้ำหนัก (15-Oct &middot; 5 โรง)</div><div class="value">{s15:.2f}<span class="unit">% &middot; <b>{s15-s14:+.2f} จุด</b> vs 14-Oct ({s14:.2f}) &rarr; CBG รวม <b>{c15:.2f}</b></span></div></div>
  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = {lab(cd)} &middot; ไม่รวม MS)</div><div class="value">{cc:.2f}<span class="unit">&#3647;/กก. ({cc:.3f}) &middot; <b>{len(cps)} โรง (TN, TKT, PM, TDC) &middot; {int(cv):,} ตัน</b> &middot; <b style="color:#b45309">15-Oct รอผลโม่ TN, TDC (TKT, PM เข้าแล้ว)</b></span></div></div>
</div>

'''
anom=[]
for p in TH+['TWIC']:
    for d in dates:
        r=f(d,p,'recovery_pct')
        if r is not None and (r<90 or r>110): anom.append(f'{p} {lab(d)} {r:.1f}%')
pa=' &middot; '.join(f'{p} '+', '.join(pend(p)) for p in TH+['TWIC'] if pend(p))
cav=f'''<div class="caveat">
  <b style="color:#b45309">&#9888; 15-Oct: ลงข้อมูลครบ 5 โรง &mdash; <b>ผลโม่ 15-Oct เข้าแล้ว TKT 102.0% / PM 108.3%</b> (TN 100.0% / MS 90.0% = default/placeholder, TDC ว่าง &rarr; เว้นว่าง) &middot; <b>CAG รวม 15-Oct ปิดไม่ได้ (รอ TN, TDC; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = {lab(cd)}: {cc:.2f}, {len(cps)} โรง {int(cv):,} ตัน</b></b> &mdash; TN 3.77 / 483 ตัน / 24.47% &middot; TKT 3.90 / 715 ตัน / 23.94% &middot; PM 3.63 / 314 ตัน / 23.03% &middot; MS 4.22 / 424 ตัน / 28.79% &middot; TDC 3.72 / 228 ตัน / 22.64%
  <br><b style="color:#374151">ผลโม่ใหม่/Backfill:</b> <b style="color:#b45309">TKT 15-Oct 102.0% (CAG 15.97) &middot; PM 15-Oct 108.3% (CAG 14.56) &middot; TWIC 14-Oct 90.02% (CAG 14.80) &middot; CAG รวมล่าสุดที่ครบ {lab(cd)} = {cc:.2f} (ไม่เปลี่ยน)</b> &middot; จุดอื่น 1&ndash;14-Oct ฝั่งไทย diff = 0
  <br><b style="color:#374151">ปริมาณ:</b> 15-Oct รวม {int(v15):,} ตัน vs 14-Oct {int(v14):,} ({int(v15-v14):+,}, {(v15/v14-1)*100:+.1f}%) &mdash; {volchg}
  <br><b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย 5 โรง {p15:.2f} (14-Oct {p14:.2f}) &middot; %ST {s15:.2f}% &middot; CBG {c15:.2f} &middot; {' &middot; '.join(chg)} &middot; verify CBG: '''+' &middot; '.join(f"{p} {f(D,p,'price_thb_kg'):.2f}&divide;{f(D,p,'starch_pct'):.2f}% = {f(D,p,'price_thb_kg')/(f(D,p,'starch_pct')/100):.2f}" for p in TH)+f'''
  <br><span style="color:#374151">TWIC (นิติบุคคลแยก): <b>15-Oct ยังไม่ส่ง</b> (อีเมลล่าสุด "on Oct 14, 2026") &middot; 14-Oct: 108 ตัน / 2.71 / %ST 20.32% &middot; ผลโม่ 90.02% CAG 14.80 (อีเมล 16-Oct 09:31 น. ส่งไฟล์ 14-Oct ฉบับอัปเดต) &middot; 13-Oct: 70 ตัน / 2.62 / %ST 19.63% &middot; ไม่มีแถว 9&ndash;12-Oct (อีเมล 8-Oct แจ้งหยุดเก็บเกี่ยว/ลานรับซื้อพักซื้อชั่วคราว) &middot; ยังขาดของ 24-Sep, 27-Sep</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติที่ยังไม่ถูกแก้ (ในช่วง 30 วัน, %Recovery &lt;90% หรือ &gt;110%): {' &middot; '.join(anom)}</b>
  <br><b>&#128680; ค้างผลโม่ (16-Oct-2026): {pa}</b>
</div>

'''
i=t.find('<div class="header">'); j=t.find('<table>'); t=t[:i]+hdr+kpi+cav+t[j:]
t,n=re.subn(r'แนวโน้ม 30 วันย้อนหลัง \([^)]*\)','แนวโน้ม 30 วันย้อนหลัง (16-Sep ถึง 15-Oct-2026)',t); assert n==1
t=t.replace('ช่วง 30 วันนี้ (15-Sep ถึง 14-Oct)','ช่วง 30 วันนี้ (16-Sep ถึง 15-Oct)')
t,n=re.subn(r'ที่มา \(internal\):.*?ยังขาดของ 24-Sep, 27-Sep\) &middot;','ที่มา (internal): SharePoint &mdash; TWPCROOTSOURCINGTEAM / "Daily root purchased report - 10_Oct 2026" (1&ndash;15-Oct) และ "09_Sep 2026" (16&ndash;30-Sep) (อ่านไฟล์รอบ 16-Oct-2026) &middot; TWIC: อีเมล put.p@thaiwah.com (ล่าสุด = ของ 14-Oct ฉบับล่าสุดได้รับ 16-Oct 09:31 น. &middot; ยังไม่มีของ 15-Oct &middot; ไฟล์ไม่มี 9&ndash;12-Oct &middot; ยังขาดของ 24-Sep, 27-Sep) &middot;',t,flags=re.S); assert n==1
open(NEW,'w',encoding='utf-8').write(t)
js=re.search(r'<script>\nconst dates.*?(?=Object\.values\(plants\))',t,re.S).group(0).replace('<script>\n','',1)
open(__import__('os').path.expanduser('~/_chk.js'),'w').write(js+'\nconsole.log(JSON.stringify({dates,plants}));')
print(len(t), 'anom',len(anom))
