import csv,re,json,shutil,subprocess,os,sys
S=json.loads(open('memory/_src_1019.json').read())
CSV='memory/root-price-history.csv'
OLD='Daily root dashboard - 15 October 2026.html'
NEW='Daily root dashboard - 18 October 2026.html'
import os.path
if not os.path.exists(CSV+'.bak_1019r1'): shutil.copy(CSV,CSV+'.bak_1019r1')
if not os.path.exists('memory/'+OLD+'.bak_1019r1'): shutil.copy(OLD,'memory/'+OLD+'.bak_1019r1')
H=['date','plant','price_thb_kg','volume_tons','starch_pct','cag_thb_kg','recovery_pct']
rows=list(csv.DictReader(open(CSV,encoding='utf-8')))
R={(r['date'],r['plant']):r for r in rows}
# --- diff existing Oct rows vs source (5 Thai plants)
def fx(v,fmt): return '' if v is None else fmt%v
def valid_rec(p,v):
    if p=='TKT':
        t,r1,r2=v[3:6]; 
        if t is None or t==0: return None
        if t==95.0 and r1==95.0 and r2==95.0: return None
        return t
    r=v[3]
    if r is None or r==0.0 or r==100.0: return None
    if p=='MS' and r==90.0: return None
    return r
diffs=[]
NEWR={}
for k,v in sorted(S.items()):
    d,p=k.split('|')
    vol,pr,st=v[0],v[1],v[2]
    if not vol or pr is None:
        NEWR[(d,p)]=dict(date=d,plant=p,price_thb_kg='',volume_tons='0' if vol==0 else '',starch_pct='',cag_thb_kg='',recovery_pct='')
        # keep format consistent with existing: zero volume rows
        continue
    rec=valid_rec(p,v)
    NEWR[(d,p)]=dict(date=d,plant=p,price_thb_kg='%.2f'%pr,volume_tons='%d'%vol,starch_pct='%.2f'%st,cag_thb_kg='',recovery_pct=('%.1f'%rec if rec is not None else ''))
CAG={('2026-10-15','MS'):16.18,('2026-10-15','TDC'):16.47,('2026-10-16','TKT'):16.47,('2026-10-17','TKT'):15.86,('2026-10-16','PM'):15.08}
for key,c in CAG.items():
    r=NEWR[key]; rec=float(r['recovery_pct']); pr=float(r['price_thb_kg']); st=float(r['starch_pct'])
    assert abs(pr/(st/100)/(rec/100)-c)<0.03,key
    r['cag_thb_kg']='%.2f'%c
# existing CAG for rows that were already in CSV & unchanged recovery: keep CSV cag
for key,r in NEWR.items():
    old=R.get(key)
    if old and r['cag_thb_kg']=='' and old['recovery_pct']==r['recovery_pct'] and r['recovery_pct']!='':
        r['cag_thb_kg']=old['cag_thb_kg']
    if old:
        for f in ('price_thb_kg','volume_tons','starch_pct','recovery_pct'):
            a,b=old[f],r[f]
            try: same=(a==b) or (a!='' and b!='' and abs(float(a)-float(b))<1e-9)
            except: same=False
            if not same: diffs.append((key,f,a,b))
print('DIFFS vs existing CSV:'); [print(' ',x) for x in diffs]
# 0-volume rows: keep existing representation if already there
for key,r in NEWR.items():
    old=R.get(key)
    if r['price_thb_kg']=='' and old: R[key]=old if old['price_thb_kg']=='' else r
    else: R[key]=r
# fill defaults for TKT 1-Oct etc: leave as existing
# TWIC
def tw(d,pr,v,st,cag,rec): R[(d,'TWIC')]=dict(date=d,plant='TWIC',price_thb_kg=pr,volume_tons=v,starch_pct=st,cag_thb_kg=cag,recovery_pct=rec)
tw('2026-10-16','2.79','354','20.93','13.50','98.85'); tw('2026-10-17','2.79','393','20.80','12.57','106.70'); tw('2026-10-18','','','','','')
D='2026-10-18'; P='2026-10-17'
plants=['TN','TKT','PM','MS','TDC','TWIC']
for p in plants:
    R.setdefault((D,p),dict(date=D,plant=p,price_thb_kg='',volume_tons='',starch_pct='',cag_thb_kg='',recovery_pct=''))
    for d in ('2026-10-15','2026-10-16','2026-10-17'): R.setdefault((d,p),dict(date=d,plant=p,price_thb_kg='',volume_tons='',starch_pct='',cag_thb_kg='',recovery_pct=''))
# for cag cross-check on all rows
for (d,p),r in R.items():
    if r['cag_thb_kg'] and r['recovery_pct']:
        pr,st,rc,cg=float(r['price_thb_kg']),float(r['starch_pct']),float(r['recovery_pct']),float(r['cag_thb_kg'])
        assert abs(pr/(st/100)/(rc/100)-cg)<0.06,(d,p,r)
dates=sorted({k[0] for k in R})[-30:]
assert dates[-1]==D and dates[0]=='2026-09-19',(dates[0],dates[-1])
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
vD,pD,sD,cD=agg(D,TH); vP,pP,sP,cP=agg(P,TH)
def cagtot(d):
    ps=[p for p in G if pv(d,p)]
    if not ps or any(f(d,p,'cag_thb_kg') is None for p in ps): return None
    v=sum(pv(d,p) for p in ps); return v,sum(pv(d,p)*f(d,p,'cag_thb_kg') for p in ps)/v,ps
cd=None
for d in reversed(dates):
    c=cagtot(d)
    if c: cd=d; cv,cc,cps=c; break
print('last complete',cd,cv,cc,cps,'| D',vD,pD,sD,cD,'| P',vP,pP,sP,cP)
def pend(p): return [lab(d) for d in dates if pv(d,p) and f(d,p,'recovery_pct') is None]
def lastrec(p,before):
    for d in reversed([x for x in dates if x<before]):
        if f(d,p,'recovery_pct') is not None: return d,f(d,p,'recovery_pct'),f(d,p,'cag_thb_kg')
names={'TN':('อ.เมือง อุดรธานี','TN'),'TKT':('ท่าคันโท กาฬสินธุ์','TKT'),'PM':('พิมาย โคราช','PM'),'MS':('แม่สอด ตาก','MS'),'TDC':('บ้านฉาง ระยอง','TDC')}
why={'TN':'%Recovery = 100.0% (default ไฟล์ต้นทาง)','TKT':'R1 = R2 = รวม = 95.0% (default ไฟล์ต้นทาง)','PM':'%Recovery = 0.0% (ไม่มีข้อมูล)','MS':'%Recovery = 90.0% (placeholder ไฟล์ต้นทาง)','TDC':'%Recovery ว่าง'}
trs=''
for p in TH:
    pr,v,st=f(D,p,'price_thb_kg'),int(pv(D,p)),f(D,p,'starch_pct'); p0,v0=f(P,p,'price_thb_kg'),int(pv(P,p))
    dx=round(pr-p0,2); col,cl=('red','up') if dx>0 else ('green','down')
    lr=lastrec(p,D); nm,code=names[p]
    ms=' &middot; ไม่นับใน CAG รวม' if p=='MS' else ''
    cg=f(D,p,'cag_thb_kg'); rc=f(D,p,'recovery_pct')
    if rc is None:
        cgc=rcc='&mdash;'; bcls,btxt='wait','รอผลโม่'; det0=f'ลงข้อมูล 18-Oct แล้ว &middot; ยังไม่มีผลโม่ ({why[p]} &rarr; เว้นว่าง)'
    else:
        cgc=f'{cg:.2f}'; rcc=f'{rc:.1f}%'; bcls,btxt='ok','ครบ'; det0=f'ผลโม่ 18-Oct เข้าแล้ว {rc:.1f}%'
    trs+=f'''    <tr><td><span class="plant-name">{nm}</span><br><span class="plant-code">{code}</span></td>
      <td class="num">{pr:.2f}</td><td class="num"><span class="dot {col}"></span><span class="delta {cl}">{dx:+.2f}</span></td>
      <td class="num">{v}</td><td class="num">{st:.2f}</td><td class="num">{cgc}</td><td class="num">{rcc}</td>
      <td><span class="badge {bcls}">{btxt}</span><span class="status-detail">{det0}{ms} &middot; CBG {pr:.2f}&divide;{st:.2f}% = {pr/(st/100):.2f} ✓ &middot; เทียบ 17-Oct ({p0:.2f} / {v0} ตัน) ปริมาณ {(v/v0-1)*100:+.1f}% &middot; ผลโม่ล่าสุด {lab(lr[0])} {lr[1]:.1f}% (CAG {lr[2]:.2f}) &middot; ค้างผลโม่ {', '.join(pend(p))}</span></td>
    </tr>
'''
dx=round(pD-pP,2); col,cl=('red','up') if dx>0 else ('green','down')
trs+=f'''    <tr class="total-row"><td>รวมโรงงานไทย (18-Oct &mdash; ลงข้อมูล 5 โรง)</td>
      <td class="num">{pD:.2f}</td><td class="num"><span class="dot {col}"></span><span class="delta {cl}">{pD-pP:+.2f}</span></td>
      <td class="num">{int(vD):,}</td><td class="num">{sD:.2f}</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="status-detail">ราคา/%ST ถ่วงน้ำหนักทั้ง 5 โรง (รวม MS) &middot; เทียบ 17-Oct (5 โรงเดียวกัน): ราคา {pP:.2f} &rarr; {pD:.2f} / %ST {sP:.2f} &rarr; {sD:.2f}% &middot; CBG {cD:.2f} &middot; <b>CAG รวม 18-Oct ปิดไม่ได้ (รอผลโม่ TN, TKT, PM, TDC; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = {lab(cd)} {cc:.2f} ({len(cps)} โรง {int(cv):,} ตัน)</b></span></div></td>
    </tr>
'''.replace('</div></td>','</td>')
l=lastrec('TWIC','9999')
trs+=f'''    <tr><td><span class="plant-name">TWIC กัมพูชา</span><br><span class="plant-code">TWIC &middot; นิติบุคคลแยก</span></td>
      <td class="num">&mdash;</td><td class="num"><span class="dot grey"></span></td>
      <td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge wait">ยังไม่ส่ง</span><span class="status-detail">ยังไม่ได้รับอีเมล TWIC ของ 18-Oct (ล่าสุด = 17-Oct: 393 ตัน / 2.79 / %ST 20.80% &middot; ผลโม่ 106.70% CAG 12.57 &middot; 16-Oct: 354 ตัน / 2.79 / 20.93% / 98.85% / CAG 13.50) &middot; ผลโม่ล่าสุด {lab(l[0])} &middot; ค้างผลโม่ {', '.join(pend('TWIC'))} &middot; ไม่มีแถว 15-Oct (ไม่ได้ส่ง) &middot; แยกจากยอดไทย</span></td>
    </tr>
'''
i=t.find('    <tr><td><span class="plant-name">อ.เมือง'); j=t.find('</table>',i); t=t[:i]+trs+t[j:]
now=subprocess.check_output(['date','+%H:%M'],env={'TZ':'Asia/Bangkok','PATH':'/usr/bin:/bin'}).decode().strip()
vols=' &middot; '.join(f'{p} {int(pv(D,p))}' for p in TH)
chg=[]
for p in TH:
    a,b=f(D,p,'price_thb_kg'),f(P,p,'price_thb_kg'); chg.append(f"<b style=\"color:#{'b91c1c' if a>b else '15803d'}\">{p} {a-b:+.2f} ({b:.2f} &rarr; {a:.2f})</b>")
volchg=' &middot; '.join(f"{p} {int(pv(P,p))} &rarr; {int(pv(D,p))} ({int(pv(D,p)-pv(P,p)):+,}, {(pv(D,p)/pv(P,p)-1)*100:+.1f}%)" for p in TH)
h1=re.search(r'<h1>.*?</h1>',t,re.S).group(0)
subm=re.search(r'<div class="sub">.*?</div>',t,re.S).group(0)
hdr=f'''<div class="header">
  <div>
    {h1}
    {subm}
  </div>
  <div class="updated">
    ข้อมูลล่าสุด (เมื่อวาน): <b>18-Oct-2026</b> (อาทิตย์)<br>
    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; 18-Oct: ลงข้อมูลครบ 5 โรง ({vols}) &mdash; ยังไม่มีผลโม่ 18-Oct ทั้ง 5 โรง &middot; ผลโม่ใหม่/Backfill: TKT 16-Oct 99.4% / TKT 17-Oct 101.1% / MS 15-Oct 90.6% / TDC 15-Oct 99.8% &middot; TWIC 16-Oct, 17-Oct เข้าแล้ว &middot; TWIC 18-Oct ยังไม่ส่ง</b></span><br>
    อัปเดตเมื่อ: 19-Oct-2026 {now} น. (T-1 = 18-Oct) (ไฟล์ Oct แก้ล่าสุด 19-Oct 08:28 น. &middot; dashboard เดิมค้างที่ 15-Oct จึงเติม 16&ndash;18-Oct)</div>
</div>

'''
kpi=f'''<div class="kpi-row">
  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย (18-Oct &mdash; ลงข้อมูล 5 โรง)</div><div class="value">{int(vD):,}<span class="unit">ตัน &middot; <b>{vols}</b> &middot; เทียบ 17-Oct ({int(vP):,} ตัน): <b>{int(vD-vP):+,}, {(vD/vP-1)*100:+.1f}%</b></span></div></div>
  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก (18-Oct &middot; 5 โรง)</div><div class="value">{pD:.2f}<span class="unit">&#3647;/กก. ({pD:.4f}) &middot; <b style="color:#{'b91c1c' if pD>pP else '15803d'}">{pD-pP:+.2f} vs 17-Oct ({pP:.4f})</b></span></div></div>
  <div class="kpi"><div class="label">%Starch เฉลี่ยถ่วงน้ำหนัก (18-Oct &middot; 5 โรง)</div><div class="value">{sD:.2f}<span class="unit">% &middot; <b>{sD-sP:+.2f} จุด</b> vs 17-Oct ({sP:.2f}) &rarr; CBG รวม <b>{cD:.2f}</b></span></div></div>
  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = {lab(cd)} &middot; ไม่รวม MS)</div><div class="value">{cc:.2f}<span class="unit">&#3647;/กก. ({cc:.3f}) &middot; <b>{len(cps)} โรง (TN, TKT, PM, TDC) &middot; {int(cv):,} ตัน</b> &middot; <b style="color:#b45309">16&ndash;18-Oct ยังปิดไม่ได้ (รอผลโม่ TN, PM, TDC; TKT 18-Oct)</b></span></div></div>
</div>

'''
anom=[]
for p in TH+['TWIC']:
    for d in dates:
        r=f(d,p,'recovery_pct')
        if r is not None and (r<90 or r>110): anom.append(f'{p} {lab(d)} {r:.1f}%')
pa=' &middot; '.join(f'{p} '+', '.join(pend(p)) for p in TH+['TWIC'] if pend(p))
cav=f'''<div class="caveat">
  <b style="color:#b45309">&#9888; 18-Oct: ลงข้อมูลครบ 5 โรง &mdash; <b>ยังไม่มีผลโม่ 18-Oct</b> (TN/PM/MS/TDC ค่า default/ว่าง, TKT = 95.0% default &rarr; เว้นว่าง) &middot; <b>CAG รวม 18-Oct ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = {lab(cd)}: {cc:.2f}, {len(cps)} โรง {int(cv):,} ตัน</b></b> &mdash; TN 3.79 / 420 ตัน / 24.51% &middot; TKT 3.94 / 502 ตัน / 24.57% &middot; PM 3.71 / 609 ตัน / 23.69% &middot; MS 4.36 / 505 ตัน / 28.29% &middot; TDC 3.75 / 363 ตัน / 23.24%
  <br><b style="color:#374151">ผลโม่ใหม่/Backfill (รอบนี้):</b> <b style="color:#b45309">TKT 16-Oct 99.4% (CAG 16.47) &middot; TKT 17-Oct 101.1% (CAG 15.86) &middot; MS 15-Oct 90.6% (CAG 16.18) &middot; TDC 15-Oct 99.8% (CAG 16.47) &middot; TWIC 16-Oct 98.85% (CAG 13.50) &middot; TWIC 17-Oct 106.70% (CAG 12.57) &middot; CAG รวม 15-Oct ปิดครบแล้ว (TN/TKT/PM/TDC)</b> &middot; 16-Oct: PM 103.6% (CAG 15.08) เข้าแล้ว &middot; จุดอื่น 1&ndash;14-Oct ฝั่งไทย diff = 0
  <br><b style="color:#374151">ปริมาณ:</b> 18-Oct รวม {int(vD):,} ตัน vs 17-Oct {int(vP):,} ({int(vD-vP):+,}, {(vD/vP-1)*100:+.1f}%) &mdash; {volchg}
  <br><b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย 5 โรง {pD:.2f} (17-Oct {pP:.2f}) &middot; %ST {sD:.2f}% &middot; CBG {cD:.2f} &middot; {' &middot; '.join(chg)} &middot; verify CBG: '''+' &middot; '.join(f"{p} {f(D,p,'price_thb_kg'):.2f}&divide;{f(D,p,'starch_pct'):.2f}% = {f(D,p,'price_thb_kg')/(f(D,p,'starch_pct')/100):.2f}" for p in TH)+f'''
  <br><span style="color:#374151">TWIC (นิติบุคคลแยก): <b>18-Oct ยังไม่ส่ง</b> (อีเมลล่าสุด "on Oct 17, 2026" rcvd 18-Oct 13:17 น.) &middot; 17-Oct: 393 ตัน / 2.79 / %ST 20.80% / 106.70% / CAG 12.57 &middot; 16-Oct: 354 ตัน / 2.79 / 20.93% / 98.85% / CAG 13.50 &middot; <b>15-Oct ไม่มีอีเมล/ไม่มีแถว</b> &middot; 13-Oct: 70 ตัน (ผลโม่ 0.0% = ไม่มีข้อมูล) &middot; ไม่มีแถว 9&ndash;12-Oct &middot; ยังขาดของ 24-Sep, 27-Sep</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติ (ในช่วง 30 วัน, %Recovery &lt;90% หรือ &gt;110%): {' &middot; '.join(anom)}</b>
  <br><b>&#128680; ค้างผลโม่ (19-Oct-2026): {pa}</b>
</div>

'''
i=t.find('<div class="header">'); j=t.find('<table>'); t=t[:i]+hdr+kpi+cav+t[j:]
t,n=re.subn(r'แนวโน้ม 30 วันย้อนหลัง \([^)]*\)','แนวโน้ม 30 วันย้อนหลัง (19-Sep ถึง 18-Oct-2026)',t); assert n==1
t=t.replace('ช่วง 30 วันนี้ (16-Sep ถึง 15-Oct)','ช่วง 30 วันนี้ (19-Sep ถึง 18-Oct)')
t,n=re.subn(r'ที่มา \(internal\):.*?ยังขาดของ 24-Sep, 27-Sep\) &middot;','ที่มา (internal): SharePoint &mdash; TWPCROOTSOURCINGTEAM / "Daily root purchased report - 10_Oct 2026" (1&ndash;18-Oct) และ "09_Sep 2026" (19&ndash;30-Sep) (อ่านไฟล์รอบ 19-Oct-2026) &middot; TWIC: อีเมล put.p@thaiwah.com (ล่าสุด = ของ 17-Oct ได้รับ 18-Oct 13:17 น. &middot; ยังไม่มีของ 18-Oct &middot; ไม่มี 15-Oct &middot; ไม่มีแถว 9&ndash;12-Oct &middot; ยังขาดของ 24-Sep, 27-Sep) &middot;',t,flags=re.S); assert n==1
open(NEW,'w',encoding='utf-8').write(t)
js=re.search(r'<script>\nconst dates.*?(?=Object\.values\(plants\))',t,re.S).group(0).replace('<script>\n','',1)
open(os.path.expanduser('~/_chk.js'),'w').write(js+'\nconsole.log(JSON.stringify({dates,plants}));')
print(len(t),'anom',len(anom))
