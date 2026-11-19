import csv, re, shutil, json, os, sys
sys.path.insert(0, os.path.expanduser('~/rp'))
base=os.path.expanduser('~/mnt/lovely/'); mem=base+'memory/'
BK='1118r4'; D='17-Nov'; PD='16-Nov'; NOW='18-Nov-2026 13:1x น.'; DOW='อังคาร'
old=base+'Daily root dashboard - 17 November 2026.html'
new=base+'Daily root dashboard - 17 November 2026.html'
shutil.copy(old, mem+'Daily root dashboard - 17 November 2026.html.bak_'+BK)
hdr=['date','plant','price_thb_kg','volume_tons','starch_pct','cag_thb_kg','recovery_pct']
rows=list(csv.DictReader(open(mem+'root-price-history.csv',newline='')))
key={(r['date'],r['plant']):r for r in rows}
assert len(rows)==180 and key[('2026-11-17','TDC')]['price_thb_kg']=='' and key[('2026-11-17','TDC')]['volume_tons']=='' and key[('2026-11-17','TN')]['price_thb_kg']=='3.96'
shutil.copy(mem+'root-price-history.csv', mem+'root-price-history.csv.bak_'+BK)
def g(x): return '' if x is None else ('%g'%x)
# new day 16-Nov (from source sheet "Nov —", read 17-Nov 08:1x ICT); defaults -> blank
NEWROWS=[('2026-11-17','TDC',4.10,293,25.43,None,None)]
for dt,p,pr,v,st,cg,rc in NEWROWS:
    key[(dt,p)]=dict(zip(hdr,[dt,p,g(pr),g(v),g(st),g(cg),g(rc)]))
dates=sorted({k[0] for k in key})[-30:]
order=['TN','TKT','PM','MS','TDC','TWIC']
out=[key[(d,p)] for d in dates for p in order]
assert len(out)==180, len(out)
assert dates[0]=='2026-10-19' and dates[-1]=='2026-11-17'
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
common=[p for p in thai if S[p]['vol'][I] and S[p]['vol'][P]]
_,v3c,p3c,s3c=agg(I,common); _,v2c,p2c,s2c=agg(P,common)
i11=lab.index('11-Nov'); b11,v11,p11,s11=agg(i11)
noentry=[p for p in thai if S[p]['vol'][I] is None]
nobuy=[p for p in thai if S[p]['vol'][I]==0]
assert b3==thai and not noentry and not nobuy and common==thai, (b3,noentry,nobuy,common)
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
EXTRA={'TN':' &middot; <b style="color:#b45309">TN ค้างผลโม่ต่อเนื่องตั้งแต่ 12-Nov (6 วัน)</b>',
       'TKT':' &middot; ปริมาณ 430 &rarr; 285 ตัน (&minus;33.7%)',
       'PM':' &middot; <b>ปริมาณ 453 &rarr; 664 ตัน (+46.6%)</b> วันที่สองหลังกลับมารับซื้อ',
       'MS':' &middot; 92.0% เป็นค่าเดียวกับแถว forecast 18&ndash;19-Nov &middot; ไม่นับใน CAG รวม'}
EXTRA['TDC']=' &middot; <b>ลงข้อมูลรอบนี้ (13:1x น.)</b> &middot; ปริมาณ 278 &rarr; 293 ตัน (+5.4%)'
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
        det+=EXTRA.get(p,'')
    else:
        assert v is None
        d='<span class="dot grey"></span><span class="delta flat">&mdash;</span>'; badge,bcls='ยังไม่ลงข้อมูล','wait'; det='ไฟล์ต้นทางยังไม่ลงปริมาณ %s (ช่องปริมาณว่าง &middot; ราคา 4.05 / %%ST 25.00%% ในแถวเป็นค่า forecast ณ %s) &rarr; เว้นว่างทั้งแถว ไม่เดา &middot; ล่าสุด %s'%(D,NOW,pjt); pr=st=cg=rc=None
    return '    <tr><td><span class="plant-name">%s</span><br><span class="plant-code">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>\n      <td><span class="badge %s">%s</span><span class="status-detail">%s</span></td>\n    </tr>'%(names[p],p,f(pr),d,vcell,f(st),f(cg),('&mdash;' if rc is None else '%g'%rc),bcls,badge,det)
T=[trow(p) for p in thai]
tc,tdot,tt=dl(p3c,p2c)
assert lc[0]=='11-Nov' and waitcore==['TN','TKT','PM','TDC'], (waitcore,lc)
ct=', '.join(common)
cagtxt='CAG รวม %s ปิดไม่ได้ (ผลโม่ %s ของ TN, TKT, PM, TDC ยังไม่เข้า; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = %s: %s, %d โรง %s ตัน'%(D,D,lc[0],fm(lc[1]),len(lc[2]),fm(lc[3],0))
T.append('    <tr class="total-row"><td>รวมโรงงานไทย (%s &mdash; %d โรง)</td>\n      <td class="num">%s</td><td class="num"><span class="dot %s"></span><span class="delta %s">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">&mdash;</td><td class="num">&mdash;</td>\n      <td><span class="status-detail">ราคา/%%ST ถ่วงน้ำหนักด้วยปริมาณของโรงที่ซื้อ (รวม MS) &middot; ครบ 5 โรง (TDC ลงข้อมูล 17-Nov แล้วรอบนี้) &middot; ส่วนต่างราคาเทียบ %s เฉพาะ %d โรงที่ซื้อทั้งสองวัน (%s): ราคา %s &rarr; %s / %%ST %s &rarr; %s%% &middot; ปริมาณ %s &rarr; %s ตัน &middot; CBG รวม %d โรง %s &middot; <b>%s</b></span></td>\n    </tr>'%(D,len(b3),fm(p3),tdot,tc,tt,fm(v3,0),fm(s3),PD,len(common),ct,fm(p2c),fm(p3c),fm(s2c),fm(s3c),fm(v2c,0),fm(v3c,0),len(b3),fm(cbg3),cagtxt))
tw=S['TWIC']; tj=max(j for j in range(len(dates)) if tw['vol'][j])
assert lab[tj]=='16-Nov'
def twt(j): return '%s: %s ตัน / %s / %%ST %s%% / %%Recovery %g%% / CAG %s'%(lab[j],fm(tw['vol'][j],0),fm(tw['price'][j]),fm(tw['st'][j]),tw['rec'][j],fm(tw['cag'][j]))
twlast=twt(tj)
TWWHY='อีเมล put.p ล่าสุด = &ldquo;on Nov 16, 2026&rdquo; (รับ 17-Nov 20:18 น.) &middot; ยังไม่มีอีเมลของ 17-Nov ณ %s'%NOW
T.append('    <tr><td><span class="plant-name">TWIC กัมพูชา</span><br><span class="plant-code">TWIC &middot; นิติบุคคลแยก</span></td>\n      <td class="num">&mdash;</td><td class="num"><span class="dot grey"></span><span class="delta flat">&mdash;</span></td>\n      <td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td>\n      <td><span class="badge wait">รอไฟล์</span><span class="status-detail">ยังไม่มีข้อมูล TWIC ของ %s &mdash; %s &rarr; เว้นว่าง ไม่เดา &middot; ล่าสุดที่มี = %s &middot; ไม่รวมยอดไทย</span></td>\n    </tr>'%(D,TWWHY,twlast))
s=open(old,encoding='utf-8').read()
k=s.find('const dates'); e=s.find('};\n\nObject.values(plants)'); assert k>0 and e>k
s=s[:k]+jsnew+s[e:]
ta=s.find('<table>'); tb=s.find('</table>')
thead=s[ta:s.find('</thead>')+len('</thead>')]
s=s[:ta]+thead+'\n'+'\n'.join(T)+'\n'+s[tb:]
tot=' &middot; '.join('%s %s'%(p,fm(S[p]['vol'][I],0)) for p in thai if S[p]['vol'][I])
a=s.find('<div class="updated">'); b=s.find('<div class="kpi-row">'); assert 0<a<b
hd=f'''<div class="updated">
    ข้อมูลล่าสุด (เมื่อวาน): <b>{D}-2026</b> ({DOW})<br>
    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; {D}: ลงข้อมูลครบ {len(b3)} โรง ({tot} = {fm(v3,0)} ตัน) &middot; <b>TDC ลงข้อมูล {D} แล้วรอบนี้</b> ({fm(S["TDC"]["vol"][I],0)} ตัน @ {fm(S["TDC"]["price"][I])} / %ST {fm(S["TDC"]["st"][I])}%) &middot; ผลโม่ {D} ยังไม่เข้าทั้ง 5 โรง (TN 100.0% / PM 100.0% / TKT 95.0% = default &middot; MS 92.0% = placeholder &middot; TDC ว่าง) &middot; <b style="color:#374151">TWIC {D} ยังไม่มีไฟล์ (ล่าสุด = {lab[tj]})</b></b></span><br>
    อัปเดตเมื่อ: {NOW} (T-1 = {D}) (อ่านไฟล์ Nov รอบ {NOW} &middot; TWIC ล่าสุด = อีเมล on Nov 16, 2026)</div>
</div>

'''
s=s[:a]+hd+s[b:]
b=s.find('<div class="kpi-row">'); c=s.find('<div class="caveat">')
kp=f'''<div class="kpi-row">
  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย ({D} &mdash; {len(b3)} โรง)</div><div class="value">{fm(v3,0)}<span class="unit">ตัน &middot; <b>{tot}</b> &middot; {PD} ({len(b2)} โรง: {', '.join(b2)}) = {fm(v2,0)} ตัน &middot; เทียบ {len(common)} โรงที่ซื้อทั้งสองวัน ({ct}) {fm(v2c,0)} &rarr; {fm(v3c,0)} ตัน = <b>{(v3c/v2c-1)*100:+.1f}%</b></span></div></div>
  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก ({D} &middot; {len(b3)} โรง)</div><div class="value">{fm(p3)}<span class="unit">&#3647;/กก. ({p3:.4f}) &middot; <b>{len(common)} โรงเดียวกัน ({ct}): {p2c:.4f} &rarr; {p3c:.4f} = {p3c-p2c:+.2f}</b> &middot; {PD} {len(b2)} โรง = {p2:.4f} &middot; 11-Nov 5 โรง = {p11:.4f}</span></div></div>
  <div class="kpi"><div class="label">%Starch เฉลี่ยถ่วงน้ำหนัก ({D} &middot; {len(b3)} โรง)</div><div class="value">{fm(s3)}<span class="unit">% &middot; <b>{len(common)} โรงเดียวกัน: {fm(s2c)} &rarr; {fm(s3c)} = {s3c-s2c:+.2f} จุด</b> &middot; {PD} {len(b2)} โรง = {fm(s2)} &rarr; CBG รวม {len(b3)} โรง <b>{fm(cbg3)}</b></span></div></div>
  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = {lc[0]} &middot; ไม่รวม MS)</div><div class="value">{fm(lc[1])}<span class="unit">&#3647;/กก. ({lc[1]:.3f}) &middot; <b>{len(lc[2])} โรง ({', '.join(lc[2])}) &middot; {fm(lc[3],0)} ตัน</b> &middot; ก่อนหน้า {lcprev[0]} = {fm(lcprev[1])} &middot; <b style="color:#b45309">12&ndash;17-Nov ยังปิดไม่ได้ (12&ndash;15-Nov รอผลโม่ TN &middot; 16-Nov รอ TN, PM, TDC &middot; 17-Nov รอ TN, TKT, PM, TDC)</b></span></div></div>
</div>

'''
s=s[:b]+kp+s[c:]
c=s.find('<div class="caveat">'); t=s.find('<table>')
ch=[]
for p in b3:
    j=pj_of(p); dd=S[p]['price'][I]-S[p]['price'][j]
    col='#b91c1c' if dd>0.004 else '#15803d'
    ch.append("<b style='color:%s'>%s %+.2f (%s &rarr; %s%s)</b>"%(col,p,dd,fm(S[p]['price'][j]),fm(S[p]['price'][I]),'' if j==P else ' เทียบ '+lab[j]))
def vtxt(p):
    v=S[p]['vol'][I]; pv=S[p]['vol'][P]
    f=lambda x:'ยังไม่ลง' if x is None else ('หยุด' if x==0 else fm(x,0))
    return '%s %s &rarr; %s'%(p,f(pv),f(v))
vol=' &middot; '.join(vtxt(p) for p in thai)
daytot=[]
for j in range(lab.index('11-Nov'),I+1):
    bb,vv,pp,ss=agg(j)
    daytot.append('%s %s ตัน (%d โรง) @ %s'%(lab[j],fm(vv,0),len(bb),fm(pp)))
pmj=pj_of('PM')
cv=f'''<div class="caveat">
  <b style="color:#b45309">&#9888; {D}: ลงข้อมูลครบ {len(b3)} โรง ({fm(v3,0)} ตัน: {tot}) &middot; ผลโม่ {D} ยังไม่เข้าทั้ง 5 โรง: TN 100.0% / PM 100.0% / TKT 95.0% (Total=R1=R2) = default, MS 92.0% = placeholder, TDC ช่อง %Recovery ว่าง &rarr; เว้นว่างทั้ง %Recovery และ CAG &mdash; <b>CAG รวม {D} ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = {lc[0]}: {fm(lc[1])}, {len(lc[2])} โรง {fm(lc[3],0)} ตัน (ไม่รวม MS)</b></b>
  <br><b style="color:#374151">ข้อมูลใหม่ (รอบนี้ {NOW}):</b> <b>TDC {D} ลงข้อมูลแล้ว</b> ({fm(S["TDC"]["vol"][I],0)} ตัน @ {fm(S["TDC"]["price"][I])} / %ST {fm(S["TDC"]["st"][I])}% / CBG {fm(S["TDC"]["price"][I]/(S["TDC"]["st"][I]/100))} &middot; %Recovery ยังว่าง) &rarr; ยอด {D} ครบ 5 โรงแล้ว &middot; ตรวจย้อนหลัง 1&ndash;16-Nov ทั้ง 5 โรงกับไฟล์ต้นทางทีละค่า: ไม่มีตัวเลขเปลี่ยน ไม่มีผลโม่ย้อนหลังเข้า (TN 12&ndash;16-Nov ยัง 100.0% default &middot; PM 16-Nov ยัง 100.0% &middot; TDC 16-Nov ยังว่าง) &middot; <b style="color:#b45309">TN 16-Nov %ST ยังเป็น 25.00% (ค่ากลม) อาจเป็นค่าชั่วคราว</b> &middot; วันย้อนหลัง (Nov) ที่ CAG รวมยังปิดไม่ได้: {' &middot; '.join(openback) or '&mdash;'}
  <br><b style="color:#374151">ปริมาณ:</b> {' &middot; '.join(daytot)} &mdash; {D} vs {PD}: {vol} &middot; {len(common)} โรงที่ซื้อทั้งสองวัน ({ct}) {fm(v2c,0)} &rarr; {fm(v3c,0)} ตัน = {(v3c/v2c-1)*100:+.1f}%
  <br><b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย {len(b3)} โรง {fm(p3)} &middot; %ST {fm(s3)}% &middot; CBG {fm(cbg3)} &middot; {len(common)} โรงเดียวกัน ({ct}): ราคา {fm(p2c)} &rarr; {fm(p3c)} / %ST {fm(s2c)}% &rarr; {fm(s3c)}% &middot; {' &middot; '.join(ch)}
  <br><span style="color:#374151">TWIC (นิติบุคคลแยก, ไม่รวมยอดไทย): <b>{D} ยังไม่มีข้อมูล &rarr; เว้นว่าง</b> ({TWWHY}) &middot; ล่าสุดที่มี {twt(tj-1)} &middot; {twt(tj)}</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติ (30 วัน, %Recovery &lt;90% หรือ &gt;110%): {' &middot; '.join(an)}</b>
  <br><b>&#128680; ค้างผลโม่ (ณ {D}-2026): {pl} &middot; TWIC ไม่มีข้อมูล: {', '.join(twn) or '&mdash;'}</b>
</div>

'''
s=s[:c]+cv+s[t:]
OR='19-Oct ถึง 17-Nov'; n0=s.count(OR); assert n0==2, n0
s=s.replace(OR,'%s ถึง %s'%(lab[0],D))
fa=s.find('<div class="footnote">'); fb=s.find('</div>',fa); assert fa>0
fn='''<div class="footnote">
  ที่มา (internal): SharePoint &mdash; TWPCROOTSOURCINGTEAM / "Daily root purchased report - 11_Nov 2026" (1&ndash;17-Nov) (อ่านไฟล์รอบ %s) &middot; TWIC: อีเมล put.p@thaiwah.com (ล่าสุด = ของ %s &middot; ของ %s ยังไม่มี) &middot; ราคาที่แสดงคือราคาที่ %%Starch จริงของแต่ละวัน (ไม่ปรับเทียบ 25%%) &middot;
  ที่มา (external): nettathai.org &middot;
  หน้านี้อัปเดตอัตโนมัติเมื่อพบข้อมูลวันใหม่ในไฟล์ต้นทาง
'''%(NOW,lab[tj],D)
s=s[:fa]+fn+s[fb:]
open(new,'w',encoding='utf-8').write(s)
print('bytes',len(s.encode()))
print(D,b3,v3,round(p3,4),round(s3,3),round(cbg3,3),'|',PD,b2,v2,round(p2,4),round(s2,3),'| common',common,v2c,v3c,round(p2c,4),round(p3c,4),round(s2c,3),round(s3c,3),'| 11-Nov',v11,round(p11,4))
print('lastcomplete',lc,'prev',lcprev,'waitcore',waitcore)
print('pend',pl); print('twn',twn); print('daytot',daytot); print('ch',ch)
hd0=s[:s.find('<div class="updated">')]
for m in re.finditer(r'16 November|17-Nov-2026 1',hd0+thead): print('LEFTOVER',(hd0+thead)[max(0,m.start()-80):m.start()+60].replace('\n',' '))
