import csv, re, shutil, json, os, sys
base=os.path.expanduser('~/mnt/lovely/'); mem=base+'memory/'
BK='1116r3'; D='15-Nov'; PD='14-Nov'; NOW='16-Nov-2026 10:1x น.'; DOW='อาทิตย์'
old=base+'Daily root dashboard - 15 November 2026.html'
new=base+'Daily root dashboard - 15 November 2026.html'
shutil.copy(new, mem+'Daily root dashboard - 15 November 2026.html.bak_'+BK)
shutil.copy(mem+'root-price-history.csv', mem+'root-price-history.csv.bak_'+BK)
rows=list(csv.DictReader(open(mem+'root-price-history.csv',newline='')))
hdr=['date','plant','price_thb_kg','volume_tons','starch_pct','cag_thb_kg','recovery_pct']
key={(r['date'],r['plant']):r for r in rows}
def up(d,p,price='',vol='',st='',cag='',rec=''):
    key[(d,p)]=dict(zip(hdr,[d,p,price,vol,st,cag,rec]))
SRC="""2026-11-15,TKT,4.12,313,25.62,16.47,97.7
2026-11-14,TWIC,3.09,623,21.53,13.74,104.53
2026-11-15,TWIC,3.13,592,21.88,13.45,106.33"""
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
print('ADDED',len(added),added)
exp={('2026-11-15','TKT'),('2026-11-14','TWIC'),('2026-11-15','TWIC')}
if {(a,b) for a,b,_,_ in chg}!=exp: sys.exit('unexpected diff set - stop')
if added: sys.exit('unexpected added set - stop')
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
_,v2l,p2l,s2l=agg(P,b3)
i11=lab.index('11-Nov'); _,v11,p11,s11=agg(i11)
noentry=[p for p in thai if S[p]['vol'][I] is None]
nobuy=[p for p in thai if S[p]['vol'][I]==0]
def core_cag(i):
    b=[p for p in core if S[p]['vol'][i]]
    if any(S[p]['vol'][i] is None for p in core): return None
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
        w=[p for p in core if (S[p]['vol'][i] and S[p]['cag'][i] is None) or S[p]['vol'][i] is None]
        if w: openback.append('%s (รอ %s)'%(lab[i],', '.join(w)))
an=[]
for p in thai:
    for j in range(len(dates)):
        r=S[p]['rec'][j]
        if r is not None and (r<90 or r>110): an.append('%s %s %g%%'%(p,lab[j],r))
pend={p:[lab[j] for j in range(len(dates)) if S[p]['vol'][j] and S[p]['rec'][j] is None] for p in thai}
twn=[lab[j] for j in range(len(dates)) if S['TWIC']['vol'][j] is None and S['TWIC']['price'][j] is None]
pl=' &middot; '.join('%s %s'%(p,', '.join(pend[p])) for p in thai if pend[p])
waitcore=[p for p in core if (S[p]['vol'][I] and S[p]['cag'][I] is None) or S[p]['vol'][I] is None]
def fm(x,n=2): return ('{:,.%df}'%n).format(x)
def dl(a,b):
    d=a-b
    if abs(d)<0.005: return 'flat','green','0.00'
    return ('up','red','+%.2f'%d) if d>0 else ('down','green','%.2f'%d)
def pj_of(p,i=I):
    for q in range(i-1,-1,-1):
        if S[p]['vol'][q]: return q
DEF={'TN':'100.0% = default','TKT':'95.0% (Total=R1=R2) = default','PM':'100.0% = default','MS':'92.0% = placeholder','TDC':'ว่าง'}
HOL='หมายเหตุในไฟล์ต้นทาง: &ldquo;หยุดเทศกาลแข่งเรือ&rdquo; 12&ndash;15-Nov'
def trow(p):
    pr,v,st,cg,rc=[S[p][k][I] for k in ('price','vol','st','cag','rec')]
    pj=pj_of(p)
    pjt='%s (%s / %s ตัน)'%(lab[pj],fm(S[p]['price'][pj]),fm(S[p]['vol'][pj],0))
    f=lambda x,n=2:'&mdash;' if x is None else fm(x,n)
    vcell='&mdash;'
    if v:
        vcell=f(v,0)
        c,dot,t=dl(pr,S[p]['price'][pj]); d='<span class="dot %s"></span><span class="delta %s">%s</span>'%(dot,c,t)
        if rc is not None:
            badge,bcls=('ไม่นับ CAG','wait') if p=='MS' else ('ครบ','ok')
            det='ผลโม่ %s เข้าแล้ว: %%Recovery %g%% &rarr; CBG %s &rarr; CAG %s &middot; เทียบ %s'%(D,rc,fm(pr/(st/100)),fm(cg),pjt)
        else:
            badge,bcls=('ไม่นับ CAG','wait') if p=='MS' else ('รอผลโม่','wait')
            det='ลงข้อมูล %s แล้ว &middot; ยังไม่มีผลโม่ (%%Recovery ในไฟล์ = %s &rarr; เว้นว่าง) &middot; CBG %s &middot; เทียบ %s'%(D,DEF[p],fm(pr/(st/100)),pjt)
    elif v==0:
        vcell='0'
        d='<span class="dot grey"></span><span class="delta flat">&mdash;</span>'; badge,bcls='ไม่ซื้อ','none'; det='หยุดรับซื้อ (%s) &middot; ซื้อล่าสุด %s'%(HOL,pjt); pr=st=cg=rc=None
    else:
        d='<span class="dot grey"></span><span class="delta flat">&mdash;</span>'; badge,bcls='ยังไม่ลงข้อมูล','wait'; det='ไฟล์ต้นทางยังไม่ลงปริมาณ %s (ช่องปริมาณว่าง &middot; ราคา/%%ST ในแถวเป็นค่า forecast ณ %s) &rarr; เว้นว่าง ไม่เดา &middot; ล่าสุด %s'%(D,NOW,pjt); pr=st=cg=rc=None
    return '    <tr><td><span class="plant-name">%s</span><br><span class="plant-code">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>\n      <td><span class="badge %s">%s</span><span class="status-detail">%s</span></td>\n    </tr>'%(names[p],p,f(pr),d,vcell,f(st),f(cg),('&mdash;' if rc is None else '%g'%rc),bcls,badge,det)
T=[trow(p) for p in thai]
tc,tdot,tt=dl(p3,p2l)
assert waitcore and lc[0]=='11-Nov', (waitcore,lc)
cagtxt='CAG รวม %s ปิดไม่ได้ (รอ %s; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = %s: %s, %d โรง %s ตัน'%(D,', '.join(waitcore),lc[0],fm(lc[1]),len(lc[2]),fm(lc[3],0))
missnote=''
if noentry: missnote+=' &middot; <b style="color:#b45309">%s ยังไม่ลงข้อมูล &rarr; ยอดรวมยังไม่ครบ</b>'%', '.join(noentry)
if nobuy: missnote+=' &middot; %s หยุดรับซื้อ'%', '.join(nobuy)
b3t=', '.join(b3)
T.append('    <tr class="total-row"><td>รวมโรงงานไทย (%s &mdash; %d โรง)</td>\n      <td class="num">%s</td><td class="num"><span class="dot %s"></span><span class="delta %s">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">&mdash;</td><td class="num">&mdash;</td>\n      <td><span class="status-detail">ราคา/%%ST ถ่วงน้ำหนักด้วยปริมาณของโรงที่ซื้อ (รวม MS)%s &middot; เทียบ %s (%s โรงเดียวกัน): ราคา %s &rarr; %s / %%ST %s &rarr; %s%% &middot; ปริมาณ %s &rarr; %s ตัน &middot; CBG รวม %s &middot; <b>%s</b></span></td>\n    </tr>'%(D,len(b3),fm(p3),tdot,tc,tt,fm(v3,0),fm(s3),missnote,PD,b3t,fm(p2l),fm(p3),fm(s2l),fm(s3),fm(v2l,0),fm(v3,0),fm(cbg3),cagtxt))
tw=S['TWIC']; tj=max(j for j in range(len(dates)) if tw['vol'][j])
twlast='%s: %s ตัน / %s / %%ST %s%% / %%Recovery %s / CAG %s'%(lab[tj],fm(tw['vol'][tj],0),fm(tw['price'][tj]),fm(tw['st'][tj]),('&mdash;' if tw['rec'][tj] is None else '%g%%'%tw['rec'][tj]),('&mdash;' if tw['cag'][tj] is None else fm(tw['cag'][tj])))
assert lab[tj]==D
TWWHY='อีเมล put.p ล่าสุด = &ldquo;on Nov 13, 2026&rdquo; (รับ 14-Nov 08:57 น.) &middot; ยังไม่มีอีเมลของ 14-Nov และ 15-Nov ณ %s'%NOW
T.append('    <tr><td><span class="plant-name">TWIC กัมพูชา</span><br><span class="plant-code">TWIC &middot; นิติบุคคลแยก</span></td>\n      <td class="num">&mdash;</td><td class="num"><span class="dot grey"></span><span class="delta flat">&mdash;</span></td>\n      <td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td>\n      <td><span class="badge wait">รอไฟล์</span><span class="status-detail">ยังไม่มีข้อมูล TWIC ของ 14-Nov และ %s &mdash; %s &rarr; เว้นว่าง ไม่เดา &middot; ล่าสุดที่มี = %s &middot; ไม่รวมยอดไทย</span></td>\n    </tr>'%(D,TWWHY,twlast))
c_,dot_,t_=dl(tw['price'][I],tw['price'][P])
TWSRC='อีเมล put.p &ldquo;on Nov 15, 2026&rdquo; (รับ 16-Nov 09:42 น.)'
T[-1]='    <tr><td><span class="plant-name">TWIC กัมพูชา</span><br><span class="plant-code">TWIC &middot; นิติบุคคลแยก</span></td>\n      <td class="num">%s</td><td class="num"><span class="dot %s"></span><span class="delta %s">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%g</td>\n      <td><span class="badge ok">ครบ</span><span class="status-detail">%s &middot; %%Recovery %g%% &rarr; CBG %s &rarr; CAG %s &middot; เทียบ %s (%s / %s ตัน) &middot; ไม่รวมยอดไทย</span></td>\n    </tr>'%(fm(tw['price'][I]),dot_,c_,t_,fm(tw['vol'][I],0),fm(tw['st'][I]),fm(tw['cag'][I]),tw['rec'][I],TWSRC,tw['rec'][I],fm(tw['price'][I]/(tw['st'][I]/100)),fm(tw['cag'][I]),PD,fm(tw['price'][P]),fm(tw['vol'][P],0))
s=open(old,encoding='utf-8').read()
k=s.find('const dates'); e=s.find('};\n\nObject.values(plants)'); assert k>0 and e>k
s=s[:k]+jsnew+s[e:]
ta=s.find('<table>'); tb=s.find('</table>')
thead=s[ta:s.find('</thead>')+len('</thead>')]
s=s[:ta]+thead+'\n'+'\n'.join(T)+'\n'+s[tb:]
tot=' &middot; '.join('%s %s'%(p,fm(S[p]['vol'][I],0)) for p in thai if S[p]['vol'][I])
ne=', '.join(noentry); nb=', '.join(nobuy)
a=s.find('<div class="updated">'); b=s.find('<div class="kpi-row">'); assert 0<a<b
hd=f'''<div class="updated">
    ข้อมูลล่าสุด (เมื่อวาน): <b>{D}-2026</b> ({DOW})<br>
    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; {D}: ลงข้อมูลแล้ว {len(b3)} โรง ({tot} = {fm(v3,0)} ตัน) &middot; {nb} หยุดรับซื้อ (เทศกาลแข่งเรือ 12&ndash;15-Nov) &middot; {ne} ยังไม่ลงข้อมูล &middot; ผลโม่ {D}: TKT เข้าแล้ว (97.7%) &middot; TN ยังเป็น default &middot; <b style="color:#374151">TWIC 14&ndash;15-Nov เข้าแล้ว</b></b></span><br>
    อัปเดตเมื่อ: {NOW} (T-1 = {D}) (อ่านไฟล์ Nov + อีเมล TWIC รอบ {NOW})</div>
</div>

'''
s=s[:a]+hd+s[b:]
b=s.find('<div class="kpi-row">'); c=s.find('<div class="caveat">')
kp=f'''<div class="kpi-row">
  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย ({D} &mdash; {len(b3)} โรง &middot; {nb} หยุด &middot; {ne} ยังไม่ลง)</div><div class="value">{fm(v3,0)}<span class="unit">ตัน &middot; <b>{tot}</b> &middot; เทียบ {len(b3)} โรงเดียวกัน {PD} ({fm(v2l,0)} ตัน) = <b>{(v3/v2l-1)*100:+.1f}%</b> &middot; <span style="color:#b45309">11-Nov (5 โรง ก่อน PM หยุด) = {fm(v11,0)} ตัน</span></span></div></div>
  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก ({D} &middot; {len(b3)} โรง)</div><div class="value">{fm(p3)}<span class="unit">&#3647;/กก. ({p3:.4f}) &middot; <b>{p3-p2l:+.2f} vs {PD} {len(b3)} โรงเดียวกัน ({p2l:.4f})</b> &middot; 11-Nov 5 โรง = {p11:.4f}</span></div></div>
  <div class="kpi"><div class="label">%Starch เฉลี่ยถ่วงน้ำหนัก ({D} &middot; {len(b3)} โรง)</div><div class="value">{fm(s3)}<span class="unit">% &middot; <b>{s3-s2l:+.2f} จุด</b> vs {PD} {len(b3)} โรงเดียวกัน ({fm(s2l)}) &rarr; CBG รวม <b>{fm(cbg3)}</b></span></div></div>
  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = {lc[0]} &middot; ไม่รวม MS)</div><div class="value">{fm(lc[1])}<span class="unit">&#3647;/กก. ({lc[1]:.3f}) &middot; <b>{len(lc[2])} โรง ({', '.join(lc[2])}) &middot; {fm(lc[3],0)} ตัน</b> &middot; ก่อนหน้า {lcprev[0]} = {fm(lcprev[1])} &middot; <b style="color:#b45309">12&ndash;15-Nov ยังปิดไม่ได้ (รอผลโม่ TN ทุกวัน)</b></span></div></div>
</div>

'''
s=s[:b]+kp+s[c:]
c=s.find('<div class="caveat">'); t=s.find('<table>')
ch=[]
for p in b3:
    j=pj_of(p); dd=S[p]['price'][I]-S[p]['price'][j]
    col='#b91c1c' if dd>0.004 else '#15803d'
    ch.append("<b style='color:%s'>%s %+.2f (%s &rarr; %s)</b>"%(col,p,dd,fm(S[p]['price'][j]),fm(S[p]['price'][I])))
def vtxt(p):
    v=S[p]['vol'][I]; pv=S[p]['vol'][P]
    f=lambda x:'ยังไม่ลง' if x is None else ('หยุด' if x==0 else fm(x,0))
    return '%s %s &rarr; %s'%(p,f(pv),f(v))
vol=' &middot; '.join(vtxt(p) for p in thai)
new_rec=[]
for j in range(lab.index('12-Nov'),I+1):
    for p in ['TN','TKT','PM','MS','TDC']:
        if S[p]['rec'][j] is not None:
            new_rec.append('%s %s %g%% &rarr; CAG %s'%(p,lab[j],S[p]['rec'][j],fm(S[p]['cag'][j])))
daytot=[]
for j in range(lab.index('11-Nov'),I+1):
    bb,vv,pp,ss=agg(j)
    daytot.append('%s %s ตัน (%d โรง) @ %s'%(lab[j],fm(vv,0),len(bb),fm(pp)))
tw12=lab.index('14-Nov'); tw13=lab.index('15-Nov')
def twt(j): return '%s: %s ตัน / %s / %%ST %s%% / %%Recovery %g%% / CAG %s'%(lab[j],fm(tw['vol'][j],0),fm(tw['price'][j]),fm(tw['st'][j]),tw['rec'][j],fm(tw['cag'][j]))
cv=f'''<div class="caveat">
  <b style="color:#b45309">&#9888; {D}: ลงข้อมูลแล้ว {len(b3)} โรง ({fm(v3,0)} ตัน) &middot; {nb} หยุดรับซื้อ ({HOL} &rarr; ปริมาณ 0) &middot; {ne} ยังไม่ลงปริมาณในไฟล์ต้นทาง (แถวเป็นค่า forecast &rarr; เว้นว่าง ไม่เดา &mdash; ยอดรวม {D} จึงยังไม่ครบ) &middot; ผลโม่ {D}: TKT เข้าแล้ว (97.7% &rarr; CAG 16.47) &middot; TN 100.0% = default, MS 92.0% = placeholder &rarr; เว้นว่างทั้ง %Recovery และ CAG &mdash; <b>CAG รวม {D} ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = {lc[0]}: {fm(lc[1])}, {len(lc[2])} โรง {fm(lc[3],0)} ตัน (ไม่รวม MS)</b></b>
  <br><b style="color:#374151">ข้อมูลใหม่ (รอบนี้):</b> <b style="color:#15803d">TKT 15-Nov ผลโม่เข้าแล้ว (R1 0.0% / R2 97.7% / Total 97.7% &rarr; CAG 16.47) &middot; TWIC 14-Nov และ 15-Nov เข้าแล้ว</b> &middot; ผลโม่ที่เข้าแล้วช่วง 12&ndash;15-Nov: {' &middot; '.join(new_rec)} &middot; จุดอื่น 8&ndash;15-Nov ตรวจกับไฟล์ต้นทาง diff = 0 &middot; วันย้อนหลัง (Nov) ที่ CAG รวมยังปิดไม่ได้: {' &middot; '.join(openback) or '&mdash;'}
  <br><b style="color:#374151">ปริมาณ:</b> {' &middot; '.join(daytot)} &mdash; {D} vs {PD}: {vol} &middot; {D} เทียบ {len(b3)} โรงเดียวกัน {PD} = {(v3/v2l-1)*100:+.1f}% &middot; <b style="color:#b45309">เทียบ 11-Nov (ก่อน PM หยุด) {fm(v11,0)} &rarr; {fm(v3,0)} ตัน = {(v3/v11-1)*100:+.1f}% (PM หยุด + TDC ยังไม่ลง)</b>
  <br><b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย {fm(p3)} ({PD} {len(b3)} โรงเดียวกัน {fm(p2l)}) &middot; %ST {fm(s3)}% ({PD} {fm(s2l)}%) &middot; CBG {fm(cbg3)} &middot; {' &middot; '.join(ch)}
  <br><span style="color:#374151">TWIC (นิติบุคคลแยก, ไม่รวมยอดไทย): <b>เข้าใหม่รอบนี้</b> ({TWSRC}): {twt(tw12)} &middot; {twt(tw13)}</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติ (30 วัน, %Recovery &lt;90% หรือ &gt;110%): {' &middot; '.join(an)}</b>
  <br><b>&#128680; ค้างผลโม่ (ณ {D}-2026): {pl} &middot; TWIC ไม่มีข้อมูล: {', '.join(twn) or '&mdash;'}</b>
</div>

'''
s=s[:c]+cv+s[t:]
OR='%s ถึง %s'%(lab[0],D); n0=s.count(OR); assert n0==2, n0
s=s.replace(OR,'%s ถึง %s'%(lab[0],D))
fa=s.find('<div class="footnote">'); fb=s.find('</div>',fa); assert fa>0
fn='''<div class="footnote">
  ที่มา (internal): SharePoint &mdash; TWPCROOTSOURCINGTEAM / "Daily root purchased report - 11_Nov 2026" (1&ndash;15-Nov) (อ่านไฟล์รอบ %s) &middot; TWIC: อีเมล put.p@thaiwah.com (ล่าสุด = ของ %s &middot; ไม่มีแถว %s) &middot; ราคาที่แสดงคือราคาที่ %%Starch จริงของแต่ละวัน (ไม่ปรับเทียบ 25%%) &middot;
  ที่มา (external): nettathai.org &middot;
  หน้านี้อัปเดตอัตโนมัติเมื่อพบข้อมูลวันใหม่ในไฟล์ต้นทาง
'''%(NOW,lab[tj],', '.join(twn) or '&mdash;')
s=s[:fa]+fn+s[fb:]
open(new,'w',encoding='utf-8').write(s)
print('bytes',len(s.encode()))
print(D,b3,v3,round(p3,4),round(s3,3),round(cbg3,3),'|',PD,b2,v2,round(p2,4),round(s2,3),'| LFL',v2l,round(p2l,4),round(s2l,3),'| 11-Nov',v11,round(p11,4),round(s11,3))
print('lastcomplete',lc,'prev',lcprev,'waitcore',waitcore,'openback',openback)
print('pend',pl); print('twn',twn); print('daytot',daytot); print('new_rec',new_rec)
for m in re.finditer(r'12-Nov-2026|12 November|13-Nov-2026 08',s): print('LEFTOVER',s[max(0,m.start()-60):m.start()+50].replace('\n',' '))
