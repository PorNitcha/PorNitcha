import csv, re, shutil, json, os, sys
base=os.path.expanduser('~/mnt/lovely/'); mem=base+'memory/'
BK='1113r1'; D='12-Nov'; PD='11-Nov'; NOW='13-Nov-2026 08:3x น.'; DOW='พฤหัสบดี'
old=base+'Daily root dashboard - 11 November 2026.html'
new=base+'Daily root dashboard - 12 November 2026.html'
assert not os.path.exists(new)
shutil.copy(mem+'root-price-history.csv', mem+'root-price-history.csv.bak_'+BK)
rows=list(csv.DictReader(open(mem+'root-price-history.csv',newline='')))
hdr=['date','plant','price_thb_kg','volume_tons','starch_pct','cag_thb_kg','recovery_pct']
key={(r['date'],r['plant']):r for r in rows}
def up(d,p,price='',vol='',st='',cag='',rec=''):
    key[(d,p)]=dict(zip(hdr,[d,p,price,vol,st,cag,rec]))
SRC="""2026-11-01,TN,3.89,387,25.71,,
2026-11-01,PM,3.78,417,25.58,,
2026-11-01,MS,4.35,483,28.31,17.62,87.2
2026-11-01,TDC,3.74,159,22.72,,
2026-11-02,TN,3.95,231,25.64,,
2026-11-02,TKT,4.1,1299,24.44,17.61,95.2
2026-11-02,PM,3.73,161,24.78,21.48,70.1
2026-11-02,MS,4.19,48,28.64,22.15,66.1
2026-11-02,TDC,3.93,221,24.69,16.97,93.8
2026-11-03,TN,4.02,322,25.52,18.29,86.1
2026-11-03,TKT,4.11,1133,24.44,18.12,92.8
2026-11-03,PM,3.86,379,25.31,12.48,122.3
2026-11-03,MS,4.4,499,28.74,,
2026-11-03,TDC,4.06,270,25.15,17.05,94.7
2026-11-04,TN,3.98,275,24.77,14.53,110.6
2026-11-04,TKT,4.1,951,24.33,17.53,96.1
2026-11-04,PM,3.86,285,25.26,,
2026-11-04,MS,4.36,265,29.1,17.47,85.7
2026-11-04,TDC,3.87,255,24.08,17.47,92
2026-11-05,TN,4,391,25.27,,
2026-11-05,TKT,4.01,365,23.46,19.44,87.9
2026-11-05,PM,3.93,247,24.78,15.76,100.6
2026-11-05,MS,4.41,314,28.98,17.39,87.5
2026-11-05,TDC,3.96,257,24.79,17.56,91
2026-11-06,TN,4,371,25.56,,
2026-11-06,TKT,4.11,174,24.78,19.27,86.1
2026-11-06,PM,3.97,509,25.45,15.52,100.5
2026-11-06,MS,4.39,446,28.83,17.49,87.1
2026-11-06,TDC,3.92,334,24.33,17.27,93.3
2026-11-07,TN,3.99,383,25.21,18.19,87
2026-11-07,TKT,4.19,632,25.63,14.12,115.8
2026-11-07,PM,4.04,575,24.9,20.96,77.4
2026-11-07,MS,4.41,303,29.36,16.65,90.2
2026-11-07,TDC,3.93,137,24.17,17.1,95.1
2026-11-08,TN,4,359,24.89,15.21,105.7
2026-11-08,TKT,4.12,643,24.69,,
2026-11-08,PM,4.07,649,25.52,15.88,100.5
2026-11-08,MS,4.44,155,29.38,19.94,75.8
2026-11-08,TDC,3.87,199,23.88,17.33,93.5
2026-11-09,TN,3.98,205,24.79,,
2026-11-09,TKT,4.14,645,24.89,17.09,97.3
2026-11-09,PM,3.75,312,24.5,,
2026-11-09,MS,4.36,157,29.18,,
2026-11-09,TDC,3.84,162,24.14,16.75,95
2026-11-10,TN,4,285,25.45,,
2026-11-10,TKT,4.13,523,24.8,20.16,82.6
2026-11-10,PM,4.03,580,24.83,16.58,97.9
2026-11-10,MS,4.37,218,29.33,17.88,83.4
2026-11-10,TDC,3.88,251,23.5,17.79,92.8
2026-11-11,TN,4,348,25.55,18.03,86.9
2026-11-11,TKT,4.17,547,25.36,16.55,99.4
2026-11-11,PM,4.11,439,25.81,15.74,101.2
2026-11-11,MS,4.4,283,29.73,16.68,88.7
2026-11-11,TDC,3.86,281,23.4,17.24,95.7
2026-11-12,TN,4.03,309,25.83,,
2026-11-12,TKT,4.13,455,24.88,,
2026-11-12,PM,,,,,
2026-11-12,MS,4.33,253,28.58,,
2026-11-12,TDC,4.01,248,25.33,,
2026-11-12,TWIC,,,,,"""
def _f(x): return None if x in ('',None) else float(x)
chg=[]; added=[]
for ln in SRC.strip().split('\n'):
    c=ln.split(',')
    o=key.get((c[0],c[1]))
    if o is None: added.append((c[0],c[1])); up(*c); continue
    ov=[_f(o[h]) for h in hdr[2:]]; nv=[_f(x) for x in c[2:]]
    if ov!=nv:
        chg.append((c[0],c[1],ov,nv)); up(*c)
for x in chg: print('DIFF',x)
print('ADDED',added)
if {(a,b) for a,b,_,_ in chg}!={('2026-11-11','TDC')}: sys.exit('unexpected diff set - stop')
if len(added)!=6 or any(a!='2026-11-12' for a,_ in added): sys.exit('unexpected added set - stop')
dates=sorted({k[0] for k in key})[-30:]
order=['TN','TKT','PM','MS','TDC','TWIC']
out=[key[(d,p)] for d in dates for p in order]
assert len(out)==180, len(out)
with open(mem+'root-price-history.csv','w',newline='') as f:
    w=csv.DictWriter(f,hdr,lineterminator='\n'); w.writeheader(); w.writerows(out)
def num(v): return float(v) if v not in ('',None) else None
S={p:{k:[] for k in ['price','vol','st','cag','rec']} for p in order}
for d in dates:
    for p in order:
        r=key[(d,p)]
        for k,c in [('price','price_thb_kg'),('vol','volume_tons'),('st','starch_pct'),('cag','cag_thb_kg'),('rec','recovery_pct')]:
            S[p][k].append(num(r[c]))
MON={'09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
lab=['%d-%s'%(int(d[8:]),MON[d[5:7]]) for d in dates]
assert lab[-1]==D and lab[-2]==PD
fail=0
for p in order:
    for j,d in enumerate(dates):
        pr,st,cg,rc=S[p]['price'][j],S[p]['st'][j],S[p]['cag'][j],S[p]['rec'][j]
        if (cg is None)!=(rc is None): print('CAG/REC null mismatch',p,d); fail+=1
        if cg is not None and pr and st and rc:
            cag=pr/(st/100)/(rc/100)
            if abs(cag-cg)>0.06: print('CHECK FAIL',p,d,cag,cg); fail+=1
if fail: sys.exit('formula check failed')
def js(a): return '['+', '.join('null' if v is None else repr(v) for v in a)+']'
names={'TN':'อ.เมือง อุดรธานี','TKT':'ท่าคันโท กาฬสินธุ์','PM':'พิมาย โคราช','MS':'แม่สอด ตาก','TDC':'บ้านฉาง ระยอง','TWIC':'TWIC กัมพูชา (Oddar Meanchey)'}
blocks=[]
for p in order:
    b='  %s: { label: "%s", fullName: "%s",\n'%(p,p,names[p])
    b+='    price:  %s,\n    volume: %s,\n    starch: %s,\n    cag:    %s,\n    recov:  %s\n  }'%(js(S[p]['price']),js(S[p]['vol']),js(S[p]['st']),js(S[p]['cag']),js(S[p]['rec']))
    blocks.append(b)
jsnew='const dates = '+json.dumps(lab)+';\n\n// null = ไม่มีค่าที่มีความหมาย · volume 0 = ไม่ซื้อจริง, null = ยังไม่ลงข้อมูล · TWIC แยกจากยอดไทย\nconst plants = {\n'+',\n'.join(blocks)+',\n'
I=len(dates)-1; P=I-1
thai=['TN','TKT','PM','MS','TDC']; core=['TN','TKT','PM','TDC']
def agg(i,only=None):
    b=[p for p in (only or thai) if S[p]['vol'][i]]
    v=sum(S[p]['vol'][i] for p in b)
    return b,v,sum(S[p]['price'][i]*S[p]['vol'][i] for p in b)/v,sum(S[p]['st'][i]*S[p]['vol'][i] for p in b)/v
b3,v3,p3,s3=agg(I); b2,v2,p2,s2=agg(P); cbg3=p3/(s3/100)
_,v2l,p2l,s2l=agg(P,b3)   # like-for-like: same plants as D
miss=[p for p in thai if not S[p]['vol'][I]]
def core_cag(i):
    b=[p for p in core if S[p]['vol'][i]]
    if b and all(S[p]['cag'][i] is not None for p in b):
        v=sum(S[p]['vol'][i] for p in b); return (lab[i],sum(S[p]['cag'][i]*S[p]['vol'][i] for p in b)/v,b,v)
lc=None; lcprev=None
for i in range(I,-1,-1):
    x=core_cag(i)
    if x and lc is None: lc=x; continue
    if x and lc is not None: lcprev=x; break
openback=[]
for i in range(lab.index('1-Nov'),I):
    if core_cag(i) is None:
        w=[p for p in core if S[p]['vol'][i] and S[p]['cag'][i] is None]
        if w: openback.append('%s (รอ %s)'%(lab[i],', '.join(w)))
an=[]
for p in thai:
    for j in range(len(dates)):
        r=S[p]['rec'][j]
        if r is not None and (r<90 or r>110): an.append('%s %s %g%%'%(p,lab[j],r))
pend={p:[lab[j] for j in range(len(dates)) if S[p]['vol'][j] and S[p]['rec'][j] is None] for p in thai}
twn=[lab[j] for j in range(len(dates)) if S['TWIC']['vol'][j] is None and S['TWIC']['price'][j] is None]
pl=' &middot; '.join('%s %s'%(p,', '.join(pend[p])) for p in thai if pend[p])
waitcore=[p for p in core if S[p]['vol'][I] and S[p]['cag'][I] is None]
def fm(x,n=2): return ('{:,.%df}'%n).format(x)
def dl(a,b):
    d=a-b
    if abs(d)<0.005: return 'flat','green','0.00'
    return ('up','red','+%.2f'%d) if d>0 else ('down','green','%.2f'%d)
def pj_of(p,i=I):
    for q in range(i-1,-1,-1):
        if S[p]['vol'][q]: return q
DEF={'TN':'100.0% = default','TKT':'95.0% (Total=R1=R2) = default','PM':'100.0% = default','MS':'92.0% = placeholder','TDC':'ว่าง'}
def trow(p):
    pr,v,st,cg,rc=[S[p][k][I] for k in ('price','vol','st','cag','rec')]
    pj=pj_of(p)
    pjt='%s (%s / %s ตัน)'%(lab[pj],fm(S[p]['price'][pj]),fm(S[p]['vol'][pj],0))
    f=lambda x,n=2:'&mdash;' if x is None else fm(x,n)
    if v:
        c,dot,t=dl(pr,S[p]['price'][pj]); d='<span class="dot %s"></span><span class="delta %s">%s</span>'%(dot,c,t)
        if rc is not None:
            badge,bcls=('ไม่นับ CAG','wait') if p=='MS' else ('ครบ','ok')
            det='ผลโม่ %s เข้าแล้ว: %%Recovery %g%% &rarr; CBG %s &rarr; CAG %s &middot; เทียบ %s'%(D,rc,fm(pr/(st/100)),fm(cg),pjt)
        else:
            badge,bcls=('ไม่นับ CAG','wait') if p=='MS' else ('รอผลโม่','wait')
            det='ลงข้อมูล %s แล้ว &middot; ยังไม่มีผลโม่ (%%Recovery ในไฟล์ = %s &rarr; เว้นว่าง) &middot; CBG %s &middot; เทียบ %s'%(D,DEF[p],fm(pr/(st/100)),pjt)
    else:
        d='<span class="dot grey"></span><span class="delta flat">&mdash;</span>'; badge,bcls='ยังไม่ลงข้อมูล','wait'; det='ไฟล์ต้นทางยังไม่ลงข้อมูล %s (ช่องปริมาณ/ราคา/%%ST ว่างทั้งแถว ณ %s) &rarr; เว้นว่าง ไม่เดา &middot; ล่าสุด %s'%(D,NOW,pjt); pr=st=cg=rc=None
    return '    <tr><td><span class="plant-name">%s</span><br><span class="plant-code">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>\n      <td><span class="badge %s">%s</span><span class="status-detail">%s</span></td>\n    </tr>'%(names[p],p,f(pr),d,f(v,0) if v else '&mdash;',f(st),f(cg),('&mdash;' if rc is None else '%g'%rc),bcls,badge,det)
T=[trow(p) for p in thai]
tc,tdot,tt=dl(p3,p2)
assert waitcore and lc[0]==PD
cagtxt='CAG รวม %s ปิดไม่ได้ (รอผลโม่ %s; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = %s: %s, %d โรง %s ตัน'%(D,', '.join(waitcore),lc[0],fm(lc[1]),len(lc[2]),fm(lc[3],0)); cagcell='&mdash;'
missnote=(' &middot; <b style="color:#b45309">%s ยังไม่ลงข้อมูล &rarr; ยอดรวมยังไม่ครบ</b>'%', '.join(miss)) if miss else ''
T.append('    <tr class="total-row"><td>รวมโรงงานไทย (%s &mdash; %d โรง)</td>\n      <td class="num">%s</td><td class="num"><span class="dot %s"></span><span class="delta %s">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">&mdash;</td>\n      <td><span class="status-detail">ราคา/%%ST ถ่วงน้ำหนักด้วยปริมาณของโรงที่ซื้อ (รวม MS)%s &middot; เทียบ %s (%d โรง): ราคา %s &rarr; %s / %%ST %s &rarr; %s%% &middot; ปริมาณ %s &rarr; %s ตัน &middot; CBG รวม %s &middot; <b>%s</b></span></td>\n    </tr>'%(D,len(b3),fm(p3),tdot,tc,tt,fm(v3,0),fm(s3),cagcell,missnote,PD,len(b2),fm(p2),fm(p3),fm(s2),fm(s3),fm(v2,0),fm(v3,0),fm(cbg3),cagtxt))
tw=S['TWIC']; tj=max(j for j in range(len(dates)) if tw['vol'][j])
twlast='%s: %s ตัน / %s / %%ST %s%% / %%Recovery %s / CAG %s'%(lab[tj],fm(tw['vol'][tj],0),fm(tw['price'][tj]),fm(tw['st'][tj]),('&mdash;' if tw['rec'][tj] is None else '%g%%'%tw['rec'][tj]),('&mdash;' if tw['cag'][tj] is None else fm(tw['cag'][tj])))
assert tj==P, 'TWIC row logic assumes D missing'
TWWHY='รอบนี้ตรวจอีเมล put.p ไม่ได้ (Microsoft 365 mail ขัดข้องชั่วคราว ณ %s)'%NOW
T.append('    <tr><td><span class="plant-name">TWIC กัมพูชา</span><br><span class="plant-code">TWIC &middot; นิติบุคคลแยก</span></td>\n      <td class="num">&mdash;</td><td class="num"><span class="dot grey"></span><span class="delta flat">&mdash;</span></td>\n      <td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td>\n      <td><span class="badge wait">รอไฟล์</span><span class="status-detail">ยังไม่มีข้อมูล TWIC ของ %s &mdash; %s &rarr; เว้นว่าง ไม่เดา &middot; ล่าสุดที่มี = %s &middot; ไม่รวมยอดไทย</span></td>\n    </tr>'%(D,TWWHY,twlast))
s=open(old,encoding='utf-8').read()
k=s.find('const dates'); e=s.find('};\n\nObject.values(plants)'); assert k>0 and e>k
s=s[:k]+jsnew+s[e:]
ta=s.find('<table>'); tb=s.find('</table>')
thead=s[ta:s.find('</thead>')+len('</thead>')]
s=s[:ta]+thead+'\n'+'\n'.join(T)+'\n'+s[tb:]
tot=' &middot; '.join('%s %s'%(p,fm(S[p]['vol'][I],0)) for p in thai if S[p]['vol'][I])
ms=', '.join(miss)
a=s.find('<div class="updated">'); b=s.find('<div class="kpi-row">'); assert 0<a<b
hd=f'''<div class="updated">
    ข้อมูลล่าสุด (เมื่อวาน): <b>{D}-2026</b> ({DOW})<br>
    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; {D}: ลงข้อมูลแล้ว {len(b3)} โรง ({tot} = {fm(v3,0)} ตัน) &middot; {ms} ยังไม่ลงข้อมูล &middot; ผลโม่ {D} ยังไม่เข้า (ค่าในไฟล์เป็น default/placeholder) &middot; <b style="color:#15803d">ผลโม่ TDC {PD} เข้าแล้ว &rarr; CAG รวม {PD} ปิดได้ = {fm(lc[1])}</b> &middot; <b style="color:#374151">TWIC {D} ยังไม่มีข้อมูล (ล่าสุด = {lab[tj]})</b></b></span><br>
    อัปเดตเมื่อ: {NOW} (T-1 = {D}) (อ่านไฟล์ Nov รอบ {NOW} &middot; TWIC ล่าสุด = {lab[tj]})</div>
</div>

'''
s=s[:a]+hd+s[b:]
b=s.find('<div class="kpi-row">'); c=s.find('<div class="caveat">')
kp=f'''<div class="kpi-row">
  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย ({D} &mdash; {len(b3)} โรง &middot; {ms} ยังไม่ลง)</div><div class="value">{fm(v3,0)}<span class="unit">ตัน &middot; <b>{tot}</b> &middot; เทียบ {len(b3)} โรงเดียวกัน {PD} ({fm(v2l,0)} ตัน) = <b>{(v3/v2l-1)*100:+.1f}%</b> &middot; <span style="color:#b45309">{PD} รวม 5 โรง = {fm(v2,0)} ตัน</span></span></div></div>
  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก ({D} &middot; {len(b3)} โรง)</div><div class="value">{fm(p3)}<span class="unit">&#3647;/กก. ({p3:.4f}) &middot; <b>{p3-p2l:+.2f} vs {PD} {len(b3)} โรงเดียวกัน ({p2l:.4f})</b> &middot; {PD} 5 โรง = {p2:.4f}</span></div></div>
  <div class="kpi"><div class="label">%Starch เฉลี่ยถ่วงน้ำหนัก ({D} &middot; {len(b3)} โรง)</div><div class="value">{fm(s3)}<span class="unit">% &middot; <b>{s3-s2l:+.2f} จุด</b> vs {PD} {len(b3)} โรงเดียวกัน ({fm(s2l)}) &rarr; CBG รวม <b>{fm(cbg3)}</b></span></div></div>
  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = {lc[0]} &middot; ไม่รวม MS)</div><div class="value">{fm(lc[1])}<span class="unit">&#3647;/กก. ({lc[1]:.3f}) &middot; <b>{len(lc[2])} โรง ({', '.join(lc[2])}) &middot; {fm(lc[3],0)} ตัน</b> &middot; ก่อนหน้า {lcprev[0]} = {fm(lcprev[1])} &middot; <b style="color:#b45309">{D} ยังปิดไม่ได้ (รอผลโม่)</b></span></div></div>
</div>

'''
s=s[:b]+kp+s[c:]
c=s.find('<div class="caveat">'); t=s.find('<table>')
ch=[]
for p in b3:
    j=pj_of(p); dd=S[p]['price'][I]-S[p]['price'][j]
    col='#b91c1c' if dd>0.004 else '#15803d'
    ch.append("<b style='color:%s'>%s %+.2f (%s &rarr; %s)</b>"%(col,p,dd,fm(S[p]['price'][j]),fm(S[p]['price'][I])))
vol=' &middot; '.join(('%s %s &rarr; %s'%(p,fm(S[p]['vol'][pj_of(p)],0),fm(S[p]['vol'][I],0))) if S[p]['vol'][I] else ('%s %s &rarr; ยังไม่ลง'%(p,fm(S[p]['vol'][pj_of(p)],0))) for p in thai)
tdc=S['TDC']
cv=f'''<div class="caveat">
  <b style="color:#b45309">&#9888; {D}: ลงข้อมูลแล้ว {len(b3)} โรง ({fm(v3,0)} ตัน) &middot; {ms} ยังไม่ลงข้อมูลในไฟล์ต้นทาง (ช่องว่างทั้งแถว &rarr; เว้นว่าง ไม่เดา &mdash; ยอดรวม {D} จึงยังไม่ครบ) &middot; ผลโม่ {D} ยังไม่เข้า: TN 100.0% / TKT 95.0% (Total=R1=R2) = default, MS 92.0% = placeholder, TDC ว่าง &rarr; เว้นว่างทั้ง %Recovery และ CAG &mdash; <b>CAG รวม {D} ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = {lc[0]}: {fm(lc[1])}, {len(lc[2])} โรง {fm(lc[3],0)} ตัน (ไม่รวม MS)</b></b>
  <br><b style="color:#374151">ข้อมูลใหม่ (รอบนี้):</b> เพิ่มวัน {D} (TN, TKT, MS, TDC) &middot; <b style="color:#15803d">ผลโม่ TDC {PD} เข้าแล้ว: %Recovery {tdc['rec'][P]:g}% &rarr; CAG {fm(tdc['cag'][P])} (CBG {fm(tdc['price'][P]/(tdc['st'][P]/100))}) &rarr; CAG รวม {PD} ปิดได้ = {fm(lc[1])} ({lc[1]:.3f}) เทียบ {lcprev[0]} {fm(lcprev[1])} = {lc[1]-lcprev[1]:+.2f}</b> &middot; จุดอื่น 1&ndash;11-Nov ตรวจกับไฟล์ต้นทาง diff = 0 &middot; ตัดวัน 13-Oct ออกจากช่วง 30 วัน &middot; วันย้อนหลัง (Nov) ที่ CAG รวมยังปิดไม่ได้: {' &middot; '.join(openback) or '&mdash;'}
  <br><b style="color:#374151">ปริมาณ:</b> {D} รวม {fm(v3,0)} ตัน ({len(b3)} โรง) vs {PD} {len(b3)} โรงเดียวกัน {fm(v2l,0)} ตัน = {(v3/v2l-1)*100:+.1f}% ({PD} รวม 5 โรง = {fm(v2,0)} ตัน) &mdash; {vol}
  <br><b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย {fm(p3)} ({PD} {len(b3)} โรงเดียวกัน {fm(p2l)}) &middot; %ST {fm(s3)}% ({PD} {fm(s2l)}%) &middot; CBG {fm(cbg3)} &middot; {' &middot; '.join(ch)}
  <br><span style="color:#374151">TWIC (นิติบุคคลแยก, ไม่รวมยอดไทย): <b>{D} ยังไม่มีข้อมูล &rarr; เว้นว่าง</b> ({TWWHY}) &middot; ล่าสุด {twlast}</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติ (30 วัน, %Recovery &lt;90% หรือ &gt;110%): {' &middot; '.join(an)}</b>
  <br><b>&#128680; ค้างผลโม่ (ณ {D}-2026): {pl} &middot; TWIC ไม่มีข้อมูล: {', '.join(twn) or '&mdash;'}</b>
</div>

'''
s=s[:c]+cv+s[t:]
OR='13-Oct ถึง 11-Nov'; n0=s.count(OR); assert n0==2, n0
s=s.replace(OR,'%s ถึง %s'%(lab[0],D))
fa=s.find('<div class="footnote">'); fb=s.find('</div>',fa); assert fa>0
fn='''<div class="footnote">
  ที่มา (internal): SharePoint &mdash; TWPCROOTSOURCINGTEAM / "Daily root purchased report - 11_Nov 2026" (1&ndash;12-Nov) (อ่านไฟล์รอบ %s) &middot; TWIC: อีเมล put.p@thaiwah.com (ล่าสุด = ของ %s &middot; ของ %s ยังไม่มี &middot; ไม่มีแถว %s) &middot; ราคาที่แสดงคือราคาที่ %%Starch จริงของแต่ละวัน (ไม่ปรับเทียบ 25%%) &middot;
  ที่มา (external): nettathai.org &middot;
  หน้านี้อัปเดตอัตโนมัติเมื่อพบข้อมูลวันใหม่ในไฟล์ต้นทาง
'''%(NOW,lab[tj],D,', '.join(twn) or '&mdash;')
s=s[:fa]+fn+s[fb:]
open(new,'w',encoding='utf-8').write(s)
print('bytes',len(s.encode()))
print(D,b3,v3,round(p3,4),round(s3,3),round(cbg3,3),'|',PD,v2,round(p2,4),round(s2,3),'| LFL',v2l,round(p2l,4),round(s2l,3))
print('lastcomplete',lc,'prev',lcprev,'waitcore',waitcore,'openback',openback)
print('pend',pl); print('twn',twn)
for m in re.finditer(r'11-Nov-2026|11 November|12-Nov-2026 1',s): print('LEFTOVER',s[max(0,m.start()-60):m.start()+50].replace('\n',' '))
