import csv, re, shutil, json, os, sys
base=os.path.expanduser('~/mnt/lovely/'); mem=base+'memory/'
BK='1111r3'; D='10-Nov'; PD='9-Nov'; NOW='11-Nov-2026 10:1x น.'
old=base+'Daily root dashboard - 10 November 2026.html'
new=base+'Daily root dashboard - 10 November 2026.html'
if os.path.exists(new): shutil.copy(new,new+'.bak_'+BK)
shutil.copy(mem+'root-price-history.csv', mem+'root-price-history.csv.bak_'+BK)
rows=list(csv.DictReader(open(mem+'root-price-history.csv',newline='')))
hdr=['date','plant','price_thb_kg','volume_tons','starch_pct','cag_thb_kg','recovery_pct']
key={(r['date'],r['plant']):r for r in rows}
def up(d,p,price='',vol='',st='',cag='',rec=''):
    key[(d,p)]=dict(zip(hdr,[d,p,price,vol,st,cag,rec]))
up('2026-11-10','TWIC','3.15','575','22.1','14.45','98.48')
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
def agg(i):
    b=[p for p in thai if S[p]['vol'][i]]
    v=sum(S[p]['vol'][i] for p in b)
    return b,v,sum(S[p]['price'][i]*S[p]['vol'][i] for p in b)/v,sum(S[p]['st'][i]*S[p]['vol'][i] for p in b)/v
b3,v3,p3,s3=agg(I); b2,v2,p2,s2=agg(P); cbg3=p3/(s3/100)
lc=None
for i in range(I,-1,-1):
    b=[p for p in core if S[p]['vol'][i]]
    if b and all(S[p]['cag'][i] is not None for p in b):
        v=sum(S[p]['vol'][i] for p in b); lc=(lab[i],sum(S[p]['cag'][i]*S[p]['vol'][i] for p in b)/v,b,v); break
an=[]
for p in thai:
    for j in range(len(dates)):
        r=S[p]['rec'][j]
        if r is not None and (r<90 or r>110): an.append('%s %s %g%%'%(p,lab[j],r))
pend={p:[lab[j] for j in range(len(dates)) if S[p]['vol'][j] and S[p]['rec'][j] is None] for p in thai}
twn=[lab[j] for j in range(len(dates)) if S['TWIC']['vol'][j] is None and S['TWIC']['price'][j] is None]
pl=' &middot; '.join('%s %s'%(p,', '.join(pend[p])) for p in thai if pend[p])
waitcore=[p for p in core if S[p]['vol'][I] and S[p]['cag'][I] is None]
notclosed=[lab[i] for i in range(I,-1,-1) if lab[i]!=lc[0]][:I-lab.index(lc[0])]
notclosed=list(reversed(notclosed))
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
        d='<span class="dot grey"></span><span class="delta flat">&mdash;</span>'; badge,bcls='ไม่ซื้อ/ยังไม่ลง','wait'; det='ไม่มีปริมาณซื้อ %s &middot; ล่าสุด %s'%(D,pjt); pr=st=cg=rc=None
    return '    <tr><td><span class="plant-name">%s</span><br><span class="plant-code">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>\n      <td><span class="badge %s">%s</span><span class="status-detail">%s</span></td>\n    </tr>'%(names[p],p,f(pr),d,f(v,0) if v else '&mdash;',f(st),f(cg),('&mdash;' if rc is None else '%g'%rc),bcls,badge,det)
T=[trow(p) for p in thai]
tc,tdot,tt=dl(p3,p2)
if waitcore: cagtxt='CAG รวม %s ปิดไม่ได้ (รอผลโม่ %s; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = %s: %s, %d โรง %s ตัน'%(D,', '.join(waitcore),lc[0],fm(lc[1]),len(lc[2]),fm(lc[3],0)); cagcell='&mdash;'
else: cagtxt='CAG รวม %s = %s (%d โรง %s ตัน; ไม่รวม MS)'%(D,fm(lc[1]),len(lc[2]),fm(lc[3],0)); cagcell=fm(lc[1])
T.append('    <tr class="total-row"><td>รวมโรงงานไทย (%s &mdash; %d โรง)</td>\n      <td class="num">%s</td><td class="num"><span class="dot %s"></span><span class="delta %s">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">&mdash;</td>\n      <td><span class="status-detail">ราคา/%%ST ถ่วงน้ำหนักด้วยปริมาณของโรงที่ซื้อ (รวม MS) &middot; เทียบ %s (%d โรง): ราคา %s &rarr; %s / %%ST %s &rarr; %s%% &middot; ปริมาณ %s &rarr; %s ตัน &middot; CBG รวม %s &middot; <b>%s</b></span></td>\n    </tr>'%(D,len(b3),fm(p3),tdot,tc,tt,fm(v3,0),fm(s3),cagcell,PD,len(b2),fm(p2),fm(p3),fm(s2),fm(s3),fm(v2,0),fm(v3,0),fm(cbg3),cagtxt))
tw=S['TWIC']; tj=max(j for j in range(len(dates)) if tw['vol'][j])
twlast='%s: %s ตัน / %s / %%ST %s%% / %%Recovery %s / CAG %s'%(lab[tj],fm(tw['vol'][tj],0),fm(tw['price'][tj]),fm(tw['st'][tj]),('&mdash;' if tw['rec'][tj] is None else '%g%%'%tw['rec'][tj]),('&mdash;' if tw['cag'][tj] is None else fm(tw['cag'][tj])))
assert tj==I
tpj=max(j for j in range(I) if tw['vol'][j])
twc,twdot,twt=dl(tw['price'][I],tw['price'][tpj])
T.append('    <tr><td><span class="plant-name">TWIC กัมพูชา</span><br><span class="plant-code">TWIC &middot; นิติบุคคลแยก</span></td>\n      <td class="num">%s</td><td class="num"><span class="dot %s"></span><span class="delta %s">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%g</td>\n      <td><span class="badge ok">ครบ</span><span class="status-detail">TWIC ส่งรายงาน %s แล้ว (อีเมล put.p 11-Nov 09:44 น.): %%Recovery %g%% &rarr; CAG %s &middot; เทียบ %s (%s / %s ตัน) &middot; ไม่รวมยอดไทย</span></td>\n    </tr>'%(fm(tw['price'][I]),twdot,twc,twt,fm(tw['vol'][I],0),fm(tw['st'][I]),fm(tw['cag'][I]),tw['rec'][I],D,tw['rec'][I],fm(tw['cag'][I]),lab[tpj],fm(tw['price'][tpj]),fm(tw['vol'][tpj],0)))
s=open(old,encoding='utf-8').read()
k=s.find('const dates'); e=s.find('};\n\nObject.values(plants)'); assert k>0 and e>k
s=s[:k]+jsnew+s[e:]
ta=s.find('<table>'); tb=s.find('</table>')
thead=s[ta:s.find('</thead>')+len('</thead>')]
s=s[:ta]+thead+'\n'+'\n'.join(T)+'\n'+s[tb:]
tot=' &middot; '.join('%s %s'%(p,fm(S[p]['vol'][I],0)) for p in thai if S[p]['vol'][I])
a=s.find('<div class="updated">'); b=s.find('<div class="kpi-row">'); assert 0<a<b
hd='''<div class="updated">
    ข้อมูลล่าสุด (เมื่อวาน): <b>%s-2026</b> (อังคาร)<br>
    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; %s: ลงข้อมูลครบ %d โรง (%s = %s ตัน) &middot; ผลโม่ %s ยังไม่เข้าทั้ง 5 โรง (ค่าในไฟล์เป็น default/placeholder) &middot; <b style="color:#15803d">TWIC %s เข้าแล้ว (ล่าสุด = %s)</b></b></span><br>
    อัปเดตเมื่อ: %s (T-1 = %s) (ไฟล์ Nov แก้ล่าสุด 11-Nov 09:57 น. &middot; TWIC ล่าสุด = %s)</div>
</div>

'''%(D,D,len(b3),tot,fm(v3,0),D,D,lab[tj],NOW,D,lab[tj])
s=s[:a]+hd+s[b:]
b=s.find('<div class="kpi-row">'); c=s.find('<div class="caveat">')
nc=', '.join(notclosed)
kp='''<div class="kpi-row">
  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย (%s &mdash; %d โรง)</div><div class="value">%s<span class="unit">ตัน &middot; <b>%s</b> &middot; %+.1f%% vs %s (%s ตัน)</span></div></div>
  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก (%s &middot; %d โรง)</div><div class="value">%s<span class="unit">&#3647;/กก. (%.4f) &middot; <b>%s vs %s (%.4f)</b></span></div></div>
  <div class="kpi"><div class="label">%%Starch เฉลี่ยถ่วงน้ำหนัก (%s &middot; %d โรง)</div><div class="value">%s<span class="unit">%% &middot; <b>%+.2f จุด</b> vs %s (%s) &rarr; CBG รวม <b>%s</b></span></div></div>
  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = %s &middot; ไม่รวม MS)</div><div class="value">%s<span class="unit">&#3647;/กก. (%.3f) &middot; <b>%d โรง (%s) &middot; %s ตัน</b> &middot; <b style="color:#b45309">%s ยังปิดไม่ได้ (รอผลโม่)</b></span></div></div>
</div>

'''%(D,len(b3),fm(v3,0),tot,(v3/v2-1)*100,PD,fm(v2,0),D,len(b3),fm(p3),p3,'%+.2f'%(p3-p2),PD,p2,D,len(b3),fm(s3),s3-s2,PD,fm(s2),fm(cbg3),lc[0],fm(lc[1]),lc[1],len(lc[2]),', '.join(lc[2]),fm(lc[3],0),nc)
s=s[:b]+kp+s[c:]
c=s.find('<div class="caveat">'); t=s.find('<table>')
ch=[]
for p in thai:
    j=pj_of(p); dd=S[p]['price'][I]-S[p]['price'][j]
    col='#b91c1c' if dd>0.004 else '#15803d'
    ch.append("<b style='color:%s'>%s %+.2f (%s &rarr; %s)</b>"%(col,p,dd,fm(S[p]['price'][j]),fm(S[p]['price'][I])))
vol=' &middot; '.join('%s %s &rarr; %s'%(p,fm(S[p]['vol'][pj_of(p)],0),fm(S[p]['vol'][I],0)) for p in thai)
cv='''<div class="caveat">
  <b style="color:#b45309">&#9888; %s: ลงข้อมูลครบ %d โรง (%s ตัน) &middot; ผลโม่ %s ยังไม่เข้า: TN 100.0%% / TKT 95.0%% (Total=R1=R2) / PM 100.0%% = default, MS 92.0%% = placeholder, TDC ว่าง &rarr; เว้นว่างทั้ง %%Recovery และ CAG &mdash; <b>CAG รวม %s ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = %s: %s, %d โรง %s ตัน (ไม่รวม MS)</b></b>
  <br><b style="color:#374151">ข้อมูลใหม่ (รอบนี้):</b> TWIC %s เข้าแล้ว (อีเมล put.p 11-Nov 09:44 น.) &middot; โรงงานไทย 5&ndash;10-Nov ตรวจกับไฟล์ต้นทาง diff = 0 (ผลโม่ 10-Nov ยังไม่เข้า)
  <br><b style="color:#374151">ปริมาณ:</b> %s รวม %s ตัน (%d โรง) vs %s %s ตัน (%d โรง) = %+.1f%% &mdash; %s
  <br><b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย %s (%s %s) &middot; %%ST %s%% (%s %s%%) &middot; CBG %s &middot; %s
  <br><span style="color:#374151">TWIC (นิติบุคคลแยก, ไม่รวมยอดไทย): <b>%s เข้าแล้ว</b> &middot; %s</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติ (30 วัน, %%Recovery &lt;90%% หรือ &gt;110%%): %s</b>
  <br><b>&#128680; ค้างผลโม่ (ณ %s-2026): %s &middot; TWIC ไม่มีข้อมูล: %s</b>
</div>

'''%(D,len(b3),fm(v3,0),D,nc,lc[0],fm(lc[1]),len(lc[2]),fm(lc[3],0),D,D,fm(v3,0),len(b3),PD,fm(v2,0),len(b2),(v3/v2-1)*100,vol,fm(p3),PD,fm(p2),fm(s3),PD,fm(s2),fm(cbg3),' &middot; '.join(ch),D,twlast,' &middot; '.join(an),D,pl,', '.join(twn) or '&mdash;')
s=s[:c]+cv+s[t:]
s=s.replace('11-Oct ถึง 9-Nov','%s ถึง %s'%(lab[0],D))
fa=s.find('<div class="footnote">'); fb=s.find('</div>',fa); assert fa>0
fn='''<div class="footnote">
  ที่มา (internal): SharePoint &mdash; TWPCROOTSOURCINGTEAM / "Daily root purchased report - 11_Nov 2026" (1&ndash;10-Nov) (อ่านไฟล์รอบ 11-Nov-2026 10:1x น.) &middot; TWIC: อีเมล put.p@thaiwah.com (ล่าสุด = ของ %s &middot; ไม่มีแถว %s) &middot; ราคาที่แสดงคือราคาที่ %%Starch จริงของแต่ละวัน (ไม่ปรับเทียบ 25%%) &middot;
  ที่มา (external): nettathai.org &middot;
  หน้านี้อัปเดตอัตโนมัติเมื่อพบข้อมูลวันใหม่ในไฟล์ต้นทาง
'''%(lab[tj],', '.join(twn) or '&mdash;')
s=s[:fa]+fn+s[fb:]
open(new,'w',encoding='utf-8').write(s)
print('bytes',len(s.encode()))
print(D,b3,v3,round(p3,4),round(s3,3),round(cbg3,3),'|',PD,v2,round(p2,4),round(s2,3))
print('lastcomplete',lc,'waitcore',waitcore,'notclosed',notclosed)
print('pend',pl); print('twn',twn); print('anoms',an)
print('leftover 9-Nov-2026:',s.count('9-Nov-2026'),'| 9 November:',s.count('9 November'))
