# generic day generator (data-driven text) — 20-Nov-2026 r2 · same-day refresh 19-Nov (TDC 19-Nov in + TDC 18-Nov corrected; TWIC not in yet)
import csv, re, shutil, json, os, sys
base=os.path.expanduser('~/mnt/lovely/'); mem=base+'memory/'
BK='1125r6'; D='24-Nov'; PD='23-Nov'; NOW='25-Nov-2026 14:1x น.'; DOW='อังคาร'
old=base+'Daily root dashboard - 24 November 2026.html'
new=base+'Daily root dashboard - 24 November 2026.html'
OR='26-Oct ถึง 24-Nov'; FIRST='2026-10-26'; LAST='2026-11-24'
TWMAIL='on Nov 22, 2026'; TWRCV='รับ 23-Nov 12:14 น.'
FC={}
INC={}
INCS={}
N=None
NEWROWS=[('2026-11-24','MS',4.34,227,30.39,17.02,83.9)]
NEWNOTE='<b>อัปเดตรอบนี้ 1 จุด</b> (ไฟล์ต้นทางถูกแก้ 25-Nov 13:50 น.): <b>ผลโม่ MS 24-Nov เข้า: %Recovery 92.0% (placeholder) &rarr; 83.9% &rarr; CAG 17.02</b> (ตรวจ 4.34 &divide; 30.39% = 14.28 &middot; 14.28 &divide; 83.9% = 17.02 ตรงไฟล์) &middot; MS ไม่นับใน CAG รวม จึงไม่กระทบยอดกลุ่ม &middot; MS 22-Nov ยัง 92.0% (placeholder) &middot; PM 21&ndash;22-Nov ยัง 0.0% (ค้างเกิน 2 วัน) &middot; TN 20, 23, 24-Nov ยัง 100.0% = default &middot; TKT 24-Nov ยัง 95.0% (Total=R1=R2) = default &rarr; CAG รวมล่าสุดที่ครบยังเป็น 19-Nov'
BACKNOTE='ตรวจย้อนหลัง 1&ndash;24-Nov ทั้ง 5 โรงกับไฟล์ต้นทางด้วยสคริปต์ (ตรวจสูตร CBG/CAG): เปลี่ยนเฉพาะ 1 จุดข้างต้น'
hdr=['date','plant','price_thb_kg','volume_tons','starch_pct','cag_thb_kg','recovery_pct']
rows=list(csv.DictReader(open(mem+'root-price-history.csv',newline='')))
key={(r['date'],r['plant']):r for r in rows}
assert len(rows)==180
shutil.copy(mem+'root-price-history.csv', mem+'root-price-history.csv.bak_'+BK)
def g(x): return '' if x is None else ('%g'%x)
for dt,p,pr,v,st,cg,rc in NEWROWS:
    key[(dt,p)]=dict(zip(hdr,[dt,p,g(pr),g(v),g(st),g(cg),g(rc)]))
dates=sorted({k[0] for k in key})[-30:]
order=['TN','TKT','PM','MS','TDC','TWIC']
out=[key[(d,p)] for d in dates for p in order]
assert len(out)==180 and dates[0]==FIRST and dates[-1]==LAST, (len(out),dates[0],dates[-1])
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
def fm(x,n=2): return ('{:,.%df}'%n).format(x)
def agg(i,only=None):
    b=[p for p in (only or thai) if S[p]['vol'][i] and S[p]['price'][i] is not None]
    v=sum(S[p]['vol'][i] for p in b); pw=sum(S[p]['price'][i]*S[p]['vol'][i] for p in b)/v
    sb=[p for p in b if S[p]['st'][i] is not None]; vs=sum(S[p]['vol'][i] for p in sb)
    sw=sum(S[p]['st'][i]*S[p]['vol'][i] for p in sb)/vs; pws=sum(S[p]['price'][i]*S[p]['vol'][i] for p in sb)/vs
    return dict(b=b,v=v,p=pw,sb=sb,vs=vs,s=sw,cbg=pws/(sw/100))
A3=agg(I); A2=agg(P)
common=[p for p in thai if p in A3['b'] and p in A2['b']]
commons=[p for p in common if p in A3['sb'] and p in A2['sb']]
C3=agg(I,common); C2=agg(P,common); CS3=agg(I,commons); CS2=agg(P,commons)
noentry=[p for p in thai if S[p]['vol'][I] is None]
nobuy=[p for p in thai if S[p]['vol'][I]==0]
nost=[p for p in A3['b'] if S[p]['st'][I] is None]
def waiting(i): return [p for p in core if (S[p]['vol'][i] and S[p]['cag'][i] is None) or S[p]['vol'][i] is None]
def core_cag(i):
    if waiting(i): return None
    b=[p for p in core if S[p]['vol'][i]]
    if not b: return None
    v=sum(S[p]['vol'][i] for p in b); return (lab[i],sum(S[p]['cag'][i]*S[p]['vol'][i] for p in b)/v,b,v)
lc=None; lcprev=None
for i in range(I,-1,-1):
    x=core_cag(i)
    if x and lc is None: lc=x; continue
    if x and lc is not None: lcprev=x; break
ilc=lab.index(lc[0])
def wtxt(i):
    ne=[p for p in core if S[p]['vol'][i] is None]; w=[p for p in waiting(i) if p not in ne]
    t=[]
    if w: t.append('รอผลโม่ '+', '.join(w))
    if ne: t.append(', '.join(ne)+' ยังไม่ลงข้อมูล')
    return ' + '.join(t)
openall=['%s (%s)'%(lab[i],wtxt(i)) for i in range(lab.index('1-Nov'),I+1) if waiting(i)]
openafter=['%s %s'%(lab[i],wtxt(i)) for i in range(ilc+1,I+1) if waiting(i)]
an=[]
for p in thai:
    for j in range(len(dates)):
        r=S[p]['rec'][j]
        if r is not None and (r<90 or r>110): an.append('%s %s %g%%'%(p,lab[j],r))
pend={p:[lab[j] for j in range(len(dates)) if S[p]['vol'][j] and S[p]['rec'][j] is None] for p in thai}
def streak(p):
    n=0
    for j in range(I,-1,-1):
        if S[p]['vol'][j] and S[p]['rec'][j] is None: n+=1
        elif S[p]['vol'][j]: break
    return n
twn=[lab[j] for j in range(len(dates)) if S['TWIC']['vol'][j] is None and S['TWIC']['price'][j] is None]
pl=' &middot; '.join('%s %s'%(p,', '.join(pend[p])) for p in thai if pend[p])
def dl(a,b):
    d=a-b
    if abs(d)<0.005: return 'flat','green','0.00'
    return ('up','red','+%.2f'%d) if d>0 else ('down','green','%.2f'%d)
def pj_of(p,i=I):
    for q in range(i-1,-1,-1):
        if S[p]['vol'][q]: return q
DEF={'TN':'100.0% = default','TKT':'95.0% (Total=R1=R2) = default','PM':'100.0% = default','MS':'92.0% = placeholder','TDC':'ว่าง'}
def volchg(p):
    v=S[p]['vol'][I]; pv=S[p]['vol'][P]
    if not v or not pv: return ''
    c=(v/pv-1)*100; t='ปริมาณ %s &rarr; %s ตัน (%s%.1f%%)'%(fm(pv,0),fm(v,0),'+' if c>=0 else '&minus;',abs(c))
    return ' &middot; '+('<b>%s</b>'%t if abs(c)>=25 else t)
def trow(p):
    pr,v,st,cg,rc=[S[p][k][I] for k in ('price','vol','st','cag','rec')]
    pj=pj_of(p)
    pjt='%s (%s / %s ตัน)'%(lab[pj],fm(S[p]['price'][pj]),fm(S[p]['vol'][pj],0))
    f=lambda x,n=2:'&mdash;' if x is None else fm(x,n)
    vcell='&mdash;'
    if v:
        vcell=f(v,0)
        c,dot,t=dl(pr,S[p]['price'][pj]); d='<span class="dot %s"></span><span class="delta %s">%s</span>'%(dot,c,t)
        cbgt='CBG %s'%fm(pr/(st/100)) if st else '<b style="color:#b45309">%ST ยังไม่ลงในไฟล์ต้นทาง &rarr; เว้นว่าง (CBG คำนวณไม่ได้)</b>'
        if rc is not None:
            badge,bcls=('ไม่นับ CAG','wait') if p=='MS' else ('ครบ','ok')
            det='ผลโม่ %s เข้าแล้ว: %%Recovery %g%% &rarr; %s &rarr; CAG %s &middot; เทียบ %s'%(D,rc,cbgt,fm(cg),pjt)
        else:
            badge,bcls=('ไม่นับ CAG','wait') if p=='MS' else ('รอผลโม่','wait')
            det='ลงข้อมูล %s แล้ว &middot; ยังไม่มีผลโม่ (%%Recovery ในไฟล์ = %s &rarr; เว้นว่าง) &middot; %s &middot; เทียบ %s'%(D,DEF[p],cbgt,pjt)
        det+=volchg(p)
        n=streak(p)
        if p!='MS' and n>=3: det+=' &middot; <b style="color:#b45309">%s ค้างผลโม่ต่อเนื่อง %d วัน (ตั้งแต่ %s)</b>'%(p,n,[lab[j] for j in range(len(dates)) if S[p]['vol'][j] and S[p]['rec'][j] is None][-n])
        if p=='MS': det+=' &middot; ไม่นับใน CAG รวม'
    elif v==0:
        d='<span class="dot grey"></span><span class="delta flat">&mdash;</span>'; badge,bcls='ไม่ซื้อ','wait'; det='ไม่มีการรับซื้อ %s &middot; ล่าสุด %s'%(D,pjt); pr=st=cg=rc=None; vcell='0'
    else:
        d='<span class="dot grey"></span><span class="delta flat">&mdash;</span>'; badge,bcls='ยังไม่ลงข้อมูล','wait'
        det=(INC[p]+' &middot; ล่าสุด %s'%pjt) if p in INC else 'ไฟล์ต้นทางยังไม่ลงปริมาณ %s (ช่องปริมาณว่าง &middot; %s ในแถวเป็นค่า forecast ณ %s) &rarr; เว้นว่างทั้งแถว ไม่เดา &middot; ล่าสุด %s'%(D,FC.get(p,'ราคา/%ST'),NOW,pjt)
        if p in INC: badge='ลงไม่ครบ'
        pr=st=cg=rc=None
    return '    <tr><td><span class="plant-name">%s</span><br><span class="plant-code">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>\n      <td><span class="badge %s">%s</span><span class="status-detail">%s</span></td>\n    </tr>'%(names[p],p,f(pr),d,vcell,f(st),f(cg),('&mdash;' if rc is None else '%g'%rc),bcls,badge,det)
T=[trow(p) for p in thai]
tc,tdot,tt=dl(C3['p'],C2['p'])
ct=', '.join(common); cst=', '.join(commons); nb=len(A3['b'])
cov='ครบ 5 โรง' if nb==5 else '%d โรง (%s &rarr; ยังไม่ใช่ยอดครบ 5 โรง)'%(nb,' &middot; '.join([INCS.get(p,'%s ยังไม่ลงปริมาณ %s'%(p,D)) for p in noentry]+['%s ไม่ซื้อ'%p for p in nobuy]))
stnote='' if not nost else ' &middot; <b style="color:#b45309">%%ST/CBG รวมคิดจาก %d โรงที่ลง %%ST แล้ว (%s) &mdash; %s ยังไม่ลง %%ST</b>'%(len(A3['sb']),', '.join(A3['sb']),', '.join(nost))
wI=waiting(I)
if wI: cagtxt='CAG รวม %s ปิดไม่ได้ (%s; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = %s: %s, %d โรง %s ตัน'%(D,wtxt(I),lc[0],fm(lc[1]),len(lc[2]),fm(lc[3],0))
else: cagtxt='CAG รวม %s = %s (%d โรง %s ตัน; ไม่รวม MS)'%(D,fm(lc[1]),len(lc[2]),fm(lc[3],0))
T.append('    <tr class="total-row"><td>รวมโรงงานไทย (%s &mdash; %d โรง)</td>\n      <td class="num">%s</td><td class="num"><span class="dot %s"></span><span class="delta %s">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">&mdash;</td><td class="num">&mdash;</td>\n      <td><span class="status-detail">ราคา/%%ST ถ่วงน้ำหนักด้วยปริมาณของโรงที่ซื้อ (รวม MS) &middot; %s%s &middot; ส่วนต่างราคาเทียบ %s เฉพาะ %d โรงที่ซื้อทั้งสองวัน (%s): ราคา %s &rarr; %s &middot; ปริมาณ %s &rarr; %s ตัน &middot; %%ST (%s) %s &rarr; %s%% &middot; CBG รวม %d โรง %s &middot; <b>%s</b></span></td>\n    </tr>'%(D,nb,fm(A3['p']),tdot,tc,tt,fm(A3['v'],0),fm(A3['s']),cov,stnote,PD,len(common),ct,fm(C2['p']),fm(C3['p']),fm(C2['v'],0),fm(C3['v'],0),cst,fm(CS2['s']),fm(CS3['s']),len(A3['sb']),fm(A3['cbg']),cagtxt))
tw=S['TWIC']; tj=max(j for j in range(len(dates)) if tw['vol'][j])
def twt(j): return '%s: %s ตัน / %s / %%ST %s%% / %%Recovery %g%% / CAG %s'%(lab[j],fm(tw['vol'][j],0),fm(tw['price'][j]),fm(tw['st'][j]),tw['rec'][j],fm(tw['cag'][j]))
assert tj==P-1 and tw['vol'][I] is None and tw['vol'][P] is None
TWWHY='อีเมล put.p ล่าสุด = &ldquo;%s&rdquo; (%s) &middot; ยังไม่มีอีเมลของ 23-Nov และ %s ณ %s'%(TWMAIL,TWRCV,D,NOW)
T.append('    <tr><td><span class="plant-name">TWIC กัมพูชา</span><br><span class="plant-code">TWIC &middot; นิติบุคคลแยก</span></td>\n      <td class="num">&mdash;</td><td class="num"><span class="dot grey"></span><span class="delta flat">&mdash;</span></td>\n      <td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td>\n      <td><span class="badge wait">รอไฟล์</span><span class="status-detail">ยังไม่มีข้อมูล TWIC ของ 23-Nov และ %s (ค้าง 2 วัน) &mdash; %s &rarr; เว้นว่าง ไม่เดา &middot; ล่าสุดที่มี = %s &middot; ไม่รวมยอดไทย</span></td>\n    </tr>'%(D,TWWHY,twt(tj)))
s=open(old,encoding='utf-8').read()
k=s.find('const dates'); e=s.find('};\n\nObject.values(plants)'); assert k>0 and e>k
s=s[:k]+jsnew+s[e:]
ta=s.find('<table>'); tb=s.find('</table>')
thead=s[ta:s.find('</thead>')+len('</thead>')]
s=s[:ta]+thead+'\n'+'\n'.join(T)+'\n'+s[tb:]
tot=' &middot; '.join('%s %s'%(p,fm(S[p]['vol'][I],0)) for p in A3['b'])
pendI=[p for p in A3['b'] if S[p]['rec'][I] is None]
miss=''.join([(' &middot; <b>%s</b> (เว้นทั้งแถว)'%INCS[p]) if p in INCS else ' &middot; <b>%s ยังไม่ลงปริมาณ %s</b> (ช่องว่าง &rarr; เว้นทั้งแถว)'%(p,D) for p in noentry]+[' &middot; <b>%s ไม่รับซื้อ %s</b> (ไฟล์ต้นทางลง 0 ตัน)'%(p,D) for p in nobuy]+[' &middot; <b>%s ยังไม่ลง %%ST</b> (เว้นว่าง)'%p for p in nost])
deft=' / '.join('%s %s'%(p,DEF[p].replace(' (Total=R1=R2)','')) for p in pendI)
rect='ผลโม่ %s ยังไม่เข้าทั้ง %d โรงที่ลงข้อมูล (%s)'%(D,len(pendI),deft) if len(pendI)==nb else 'ผลโม่ %s ยังรอ %s'%(D,', '.join(pendI))
entered='ลงข้อมูลครบ 5 โรง' if nb==5 else 'ลงข้อมูลแล้ว %d โรง'%nb
a=s.find('<div class="updated">'); b=s.find('<div class="kpi-row">'); assert 0<a<b
hd=f'''<div class="updated">
    ข้อมูลล่าสุด (เมื่อวาน): <b>{D}-2026</b> ({DOW})<br>
    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; {D}: {entered} ({tot} = {fm(A3['v'],0)} ตัน){miss} &middot; {rect} &middot; <b style="color:#374151">TWIC 23-Nov และ {D} ยังไม่มีไฟล์ (ล่าสุด = {lab[tj]})</b></b></span><br>
    อัปเดตเมื่อ: {NOW} (T-1 = {D}) (อ่านไฟล์ Nov รอบ {NOW} &middot; TWIC ล่าสุด = อีเมล {TWMAIL})</div>
</div>

'''
s=s[:a]+hd+s[b:]
b=s.find('<div class="kpi-row">'); c=s.find('<div class="caveat">')
k1='' if nb==5 else ' &middot; '+' &middot; '.join([p+' ยังไม่ลง' for p in noentry]+[p+' ไม่ซื้อ' for p in nobuy])
k3='' if not nost else ' &middot; ไม่รวม '+', '.join(nost)
kp=f'''<div class="kpi-row">
  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย ({D} &mdash; {nb} โรง{k1})</div><div class="value">{fm(A3['v'],0)}<span class="unit">ตัน &middot; <b>{tot}</b> &middot; {PD} ({len(A2['b'])} โรง) = {fm(A2['v'],0)} ตัน &middot; เทียบ {len(common)} โรงที่ซื้อทั้งสองวัน ({ct}) {fm(C2['v'],0)} &rarr; {fm(C3['v'],0)} ตัน = <b>{(C3['v']/C2['v']-1)*100:+.1f}%</b></span></div></div>
  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก ({D} &middot; {nb} โรง)</div><div class="value">{fm(A3['p'])}<span class="unit">&#3647;/กก. ({A3['p']:.4f}) &middot; <b>{len(common)} โรงเดียวกัน ({ct}): {C2['p']:.4f} &rarr; {C3['p']:.4f} = {C3['p']-C2['p']:+.2f}</b> &middot; {PD} {len(A2['b'])} โรง = {A2['p']:.4f}</span></div></div>
  <div class="kpi"><div class="label">%Starch เฉลี่ยถ่วงน้ำหนัก ({D} &middot; {len(A3['sb'])} โรง{k3})</div><div class="value">{fm(A3['s'])}<span class="unit">% &middot; <b>{len(commons)} โรงเดียวกัน ({cst}): {fm(CS2['s'])} &rarr; {fm(CS3['s'])} = {CS3['s']-CS2['s']:+.2f} จุด</b> &middot; {PD} {len(A2['sb'])} โรง = {fm(A2['s'])} &rarr; CBG รวม {len(A3['sb'])} โรง <b>{fm(A3['cbg'])}</b></span></div></div>
  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = {lc[0]} &middot; ไม่รวม MS)</div><div class="value">{fm(lc[1])}<span class="unit">&#3647;/กก. ({lc[1]:.3f}) &middot; <b>{len(lc[2])} โรง ({', '.join(lc[2])}) &middot; {fm(lc[3],0)} ตัน</b> &middot; ก่อนหน้า {lcprev[0]} = {fm(lcprev[1])} &middot; <b style="color:#b45309">ยังปิดไม่ได้: {' &middot; '.join(openafter) or '&mdash;'}</b></span></div></div>
</div>

'''
s=s[:b]+kp+s[c:]
c=s.find('<div class="caveat">'); t=s.find('<table>')
ch=[]
for p in A3['b']:
    j=pj_of(p); dd=S[p]['price'][I]-S[p]['price'][j]
    col='#b91c1c' if dd>0.004 else '#15803d'
    ch.append("<b style='color:%s'>%s %+.2f (%s &rarr; %s%s)</b>"%(col,p,dd,fm(S[p]['price'][j]),fm(S[p]['price'][I]),'' if j==P else ' เทียบ '+lab[j]))
def vtxt(p):
    v=S[p]['vol'][I]; pv=S[p]['vol'][P]
    f=lambda x:'ยังไม่ลง' if x is None else ('หยุด' if x==0 else fm(x,0))
    return '%s %s &rarr; %s'%(p,f(pv),f(v))
vol=' &middot; '.join(vtxt(p) for p in thai)
daytot=[]
for j in range(I-6,I+1):
    aa=agg(j); daytot.append('%s %s ตัน (%d โรง) @ %s'%(lab[j],fm(aa['v'],0),len(aa['b']),fm(aa['p'])))
part='' if nb==5 else ' &middot; <b style="color:#b45309">%s เป็นยอด %d โรง (%s) จึงยังเทียบยอดรวม 5 โรงไม่ได้</b>'%(D,nb,' &middot; '.join([p+' ยังไม่ลง' for p in noentry]+[p+' ไม่ซื้อ' for p in nobuy]))
cv=f'''<div class="caveat">
  <b style="color:#b45309">&#9888; {D}: {entered} ({fm(A3['v'],0)} ตัน: {tot}){miss} &middot; {rect} &rarr; เว้นว่างทั้ง %Recovery และ CAG &mdash; <b>{cagtxt}</b></b>
  <br><b style="color:#374151">ข้อมูลใหม่ (รอบนี้ {NOW}):</b> {NEWNOTE} ({nb} โรงไทย) &middot; {BACKNOTE} &middot; วันย้อนหลัง (Nov) ที่ CAG รวมยังปิดไม่ได้: {' &middot; '.join(openall) or '&mdash;'}
  <br><b style="color:#374151">ปริมาณ:</b> {' &middot; '.join(daytot)} &mdash; {D} vs {PD}: {vol} &middot; {len(common)} โรงที่ซื้อทั้งสองวัน ({ct}) {fm(C2['v'],0)} &rarr; {fm(C3['v'],0)} ตัน = {(C3['v']/C2['v']-1)*100:+.1f}%{part}
  <br><b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย {nb} โรง {fm(A3['p'])} &middot; %ST {fm(A3['s'])}% ({len(A3['sb'])} โรง) &middot; CBG {fm(A3['cbg'])} &middot; {len(common)} โรงเดียวกัน ({ct}): ราคา {fm(C2['p'])} &rarr; {fm(C3['p'])} &middot; %ST ({cst}) {fm(CS2['s'])}% &rarr; {fm(CS3['s'])}% &middot; {' &middot; '.join(ch)}
  <br><span style="color:#374151">TWIC (นิติบุคคลแยก, ไม่รวมยอดไทย): <b>23-Nov และ {D} ยังไม่มีข้อมูล &rarr; เว้นว่าง</b> ({TWWHY}) &middot; ล่าสุดที่มี {twt(tj-1)} &middot; {twt(tj)}</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติ (30 วัน, %Recovery &lt;90% หรือ &gt;110%): {' &middot; '.join(an)}</b>
  <br><b>&#128680; ค้างผลโม่ (ณ {D}-2026): {pl} &middot; TWIC ไม่มีข้อมูล: {', '.join(twn) or '&mdash;'}</b>
</div>

'''
s=s[:c]+cv+s[t:]
n0=s.count(OR); assert n0==2, n0
s=s.replace(OR,'%s ถึง %s'%(lab[0],D))
fa=s.find('<div class="footnote">'); fb=s.find('</div>',fa); assert fa>0
fn='''<div class="footnote">
  ที่มา (internal): SharePoint &mdash; TWPCROOTSOURCINGTEAM / "Daily root purchased report - 11_Nov 2026" (1&ndash;%s) (อ่านไฟล์รอบ %s) &middot; TWIC: อีเมล put.p@thaiwah.com (ล่าสุด = ของ %s &middot; ของ 23-Nov และ %s ยังไม่มี) &middot; ราคาที่แสดงคือราคาที่ %%Starch จริงของแต่ละวัน (ไม่ปรับเทียบ 25%%) &middot;
  ที่มา (external): nettathai.org &middot;
  หน้านี้อัปเดตอัตโนมัติเมื่อพบข้อมูลวันใหม่ในไฟล์ต้นทาง
'''%(D,NOW,lab[tj],D)
s=s[:fa]+fn+s[fb:]
open(new,'w',encoding='utf-8',newline='').write(s)
print('bytes',len(s.encode()))
print('A3',{k:(round(v,4) if isinstance(v,float) else v) for k,v in A3.items()})
print('A2',{k:(round(v,4) if isinstance(v,float) else v) for k,v in A2.items()})
print('C2/C3',common,C2['v'],C3['v'],round(C2['p'],4),round(C3['p'],4),'| CS',commons,round(CS2['s'],3),round(CS3['s'],3))
print('lastcomplete',lc,'prev',lcprev); print('openafter',openafter); print('pend',pl); print('twn',twn); print('an',an)
for m in re.finditer(r'19 November|20-Nov-2026|ถึง 19-Nov',s): print('LEFTOVER',s[max(0,m.start()-80):m.start()+60].replace('\n',' '))
