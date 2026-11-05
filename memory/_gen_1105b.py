import csv, re, shutil, json, sys
M='/'  # placeholder
import os
base=os.path.expanduser('~/mnt/lovely/')
mem=base+'memory/'
BK='1105r2'
shutil.copy(mem+'root-price-history.csv', mem+'root-price-history.csv.bak_'+BK)
old=base+'Daily root dashboard - 4 November 2026.html'
new=base+'Daily root dashboard - 4 November 2026.html'
shutil.copy(old, old+'.bak_'+BK) if not os.path.exists(old+'.bak_'+BK) else None
rows=list(csv.DictReader(open(mem+'root-price-history.csv',newline='')))
hdr=['date','plant','price_thb_kg','volume_tons','starch_pct','cag_thb_kg','recovery_pct']
key={(r['date'],r['plant']):r for r in rows}
def up(d,p,price='',vol='',st='',cag='',rec=''):
    key[(d,p)]=dict(zip(hdr,[d,p,price,vol,st,cag,rec]))
D='2026-11-04'
up(D,'TN','3.98','275','24.77'); up(D,'TKT','4.1','951','24.33'); up(D,'PM','3.86','285','25.26')
up(D,'MS','4.36','265','29.1'); up(D,'TDC','3.87','255','24.08'); up(D,'TWIC','2.74','512','20.78','13.14','100.39')
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
lab=[ (lambda m,dd:'%d-%s'%(int(dd),{'10':'Oct','11':'Nov'}[m]))(*d[5:].split('-')) for d in dates]
# cross-check CBG/CAG
for p in order:
    for j,d in enumerate(dates):
        pr,st,cg,rc=S[p]['price'][j],S[p]['st'][j],S[p]['cag'][j],S[p]['rec'][j]
        if cg is not None and pr and st and rc:
            cag=pr/(st/100)/(rc/100)
            if abs(cag-cg)>0.06: print('CHECK FAIL',p,d,cag,cg)
# JS
def js(a): return '['+', '.join('null' if v is None else (repr(v)) for v in a)+']'
names={'TN':'อ.เมือง อุดรธานี','TKT':'ท่าคันโท กาฬสินธุ์','PM':'พิมาย โคราช','MS':'แม่สอด ตาก','TDC':'บ้านฉาง ระยอง','TWIC':'TWIC กัมพูชา (Oddar Meanchey)'}
blocks=[]
for p in order:
    b='  %s: { label: "%s", fullName: "%s",\n'%(p,p,names[p])
    b+='    price:  %s,\n    volume: %s,\n    starch: %s,\n    cag:    %s,\n    recov:  %s\n  }'%(js(S[p]['price']),js(S[p]['vol']),js(S[p]['st']),js(S[p]['cag']),js(S[p]['rec']))
    blocks.append(b)
jsnew='const dates = '+json.dumps(lab)+';\n\n// null = ไม่มีค่าที่มีความหมาย · volume 0 = ไม่ซื้อจริง, null = ยังไม่ลงข้อมูล · TWIC แยกจากยอดไทย\nconst plants = {\n'+',\n'.join(blocks)+',\n'
s=open(old,encoding='utf-8').read()
k=s.find('const dates'); e=s.find('};\n\nObject.values(plants)')
s=s[:k]+jsnew+s[e:]
# analytics
I=len(dates)-1; P=I-1
thai=['TN','TKT','PM','MS','TDC']
def agg(i):
    b=[p for p in thai if S[p]['vol'][i]]
    v=sum(S[p]['vol'][i] for p in b)
    pr=sum(S[p]['price'][i]*S[p]['vol'][i] for p in b)/v
    st=sum(S[p]['st'][i]*S[p]['vol'][i] for p in b)/v
    return b,v,pr,st
b3,v3,p3,s3=agg(I); b2,v2,p2,s2=agg(P)
cbg3=p3/(s3/100)
print('4-Nov',b3,v3,p3,s3,cbg3,'| 2-Nov',v2,p2,s2)
# last complete CAG (excl MS)
core=['TN','TKT','PM','TDC']
lc=None
for i in range(I,-1,-1):
    b=[p for p in core if S[p]['vol'][i]]
    if b and all(S[p]['cag'][i] is not None for p in b):
        v=sum(S[p]['vol'][i] for p in b); lc=(lab[i],sum(S[p]['cag'][i]*S[p]['vol'][i] for p in b)/v,b,v); break
print('lastcomplete',lc)
# anomalies
an=[]
for p in thai:
    for j in range(len(dates)):
        r=S[p]['rec'][j]
        if r is not None and (r<90 or r>110): an.append('%s %s %g%%'%(p,lab[j],r))
pend={}
for p in thai:
    pend[p]=[lab[j] for j in range(len(dates)) if S[p]['vol'][j] and S[p]['rec'][j] is None]
twn=[lab[j] for j in range(len(dates)) if S['TWIC']['vol'][j] is None and S['TWIC']['price'][j] is None]
pl=' &middot; '.join('%s %s'%(p,', '.join(pend[p])) for p in thai if pend[p])
def fm(x,n=2): return ('{:,.%df}'%n).format(x)
def dl(a,b):
    d=a-b
    if abs(d)<0.005: return 'flat','grey' ,'0.00'
    return ('up','red','+%.2f'%d) if d>0 else ('down','green','%.2f'%d)
def prev_price(p):
    for j in range(I-1,-1,-1):
        if S[p]['vol'][j]: return j
prevtxt={}
rowsH=[]
def trow(p,i,badge,bcls,detail,twic=False):
    j=i
    pr,v,st,cg,rc=S[p]['price'][j],S[p]['vol'][j],S[p]['st'][j],S[p]['cag'][j],S[p]['rec'][j]
    pj=None
    for q in range(j-1,-1,-1):
        if S[p]['vol'][q]: pj=q;break
    if pr is not None and v and pj is not None:
        c,dot,t=dl(pr,S[p]['price'][pj]); d='<span class="dot %s"></span><span class="delta %s">%s</span>'%(dot,c,t)
    else: d='<span class="dot grey"></span><span class="delta flat">&mdash;</span>'
    pre='<span class="plant-name">%s</span><br><span class="plant-code">%s</span>'%(names[p] if p!='TWIC' else 'TWIC กัมพูชา', p if p!='TWIC' else 'TWIC &middot; นิติบุคคลแยก')
    pjt='%s (%s / %s ตัน)'%(lab[pj],fm(S[p]['price'][pj]),fm(S[p]['vol'][pj],0)) if pj is not None else ''
    f=lambda x,n=2:'&mdash;' if x is None else fm(x,n)
    return '    <tr><td>%s</td>\n      <td class="num">%s</td><td class="num">%s</td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>\n      <td><span class="badge %s">%s</span><span class="status-detail">%s</span></td>\n    </tr>'%(pre,f(pr),d,f(v,0) if v else '&mdash;',f(st),f(cg),('&mdash;' if rc is None else '%g'%rc),bcls,badge,detail.replace('{PJ}',pjt))
T=[]
T.append(trow('TN',I,'รอผลโม่','wait','ลงข้อมูล 4-Nov แล้ว &middot; ยังไม่มีผลโม่ (%Recovery = 100.0% = default &rarr; เว้นว่าง) &middot; เทียบ {PJ}'))
T.append(trow('TKT',I,'รอผลโม่','wait','ลงข้อมูล 4-Nov แล้ว &middot; ยังไม่มีผลโม่ (Total = R1 = R2 = 95.0% = default &rarr; เว้นว่าง) &middot; เทียบ {PJ}'))
T.append(trow('PM',I,'รอผลโม่','wait','ลงข้อมูล 4-Nov แล้ว &middot; ยังไม่มีผลโม่ (%Recovery = 100.0% = default &rarr; เว้นว่าง) &middot; เทียบ {PJ}'))
T.append(trow('MS',I,'ไม่นับ CAG','wait','ลงข้อมูล 4-Nov แล้ว &middot; ยังไม่มีผลโม่ (%Recovery = 92.0% = placeholder &rarr; เว้นว่าง) &middot; เทียบ {PJ}'))
T.append(trow('TDC',I,'รอผลโม่','wait','ลงข้อมูล 4-Nov แล้ว &middot; ยังไม่มีผลโม่ (%Recovery ว่าง &rarr; เว้นว่าง) &middot; เทียบ {PJ}'))
tc,tdot,tt=dl(p3,p2)
T.append('    <tr class="total-row"><td>รวมโรงงานไทย (4-Nov &mdash; 5 โรง)</td>\n      <td class="num">%s</td><td class="num"><span class="dot %s"></span><span class="delta %s">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">&mdash;</td><td class="num">&mdash;</td>\n      <td><span class="status-detail">ราคา/%%ST ถ่วงน้ำหนักด้วยปริมาณของโรงที่ซื้อ (รวม MS) &middot; เทียบ 3-Nov (5 โรง): ราคา %s &rarr; %s / %%ST %s &rarr; %s%% &middot; ปริมาณ %s &rarr; %s ตัน &middot; CBG รวม %s &middot; <b>CAG รวม 4-Nov ปิดไม่ได้ (รอผลโม่ TN, TKT, PM, TDC; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = %s: %s, %d โรง %s ตัน</b></span></td>\n    </tr>'%(fm(p3),tdot,tc,tt,fm(v3,0),fm(s3),fm(p2),fm(p3),fm(s2),fm(s3),fm(v2,0),fm(v3,0),fm(cbg3),lc[0],fm(lc[1]),len(lc[2]),fm(lc[3],0)))
tj=max(j for j in range(len(dates)) if S['TWIC']['vol'][j])
tp=[q for q in range(tj-1,-1,-1) if S['TWIC']['vol'][q]][0]
T.append(trow('TWIC',tj,'ครบ','ok','TWIC %s &middot; CBG 13.19 &rarr; CAG %s (%%Rec %g%%) &middot; เทียบ %s (%s / %s ตัน / CAG %s) &middot; ไม่รวมยอดไทย'%(lab[tj],fm(S['TWIC']['cag'][tj]),S['TWIC']['rec'][tj],lab[tp],fm(S['TWIC']['price'][tp]),fm(S['TWIC']['vol'][tp],0),fm(S['TWIC']['cag'][tp]))))
s=open(old,encoding='utf-8').read()
k=s.find('const dates'); e=s.find('};\n\nObject.values(plants)')
s=s[:k]+jsnew+s[e:]
ta=s.find('<table>'); tb=s.find('</table>')
thead=s[ta:s.find('</thead>')+len('</thead>')]
s=s[:ta]+thead+'\n'+'\n'.join(T)+'\n'+s[tb:]
a=s.find('<div class="updated">'); b=s.find('<div class="kpi-row">')
tot=' &middot; '.join('%s %s'%(p,fm(S[p]['vol'][I],0)) for p in ['TN','TKT','PM','MS','TDC'])
hd='''<div class="updated">
    ข้อมูลล่าสุด (เมื่อวาน): <b>4-Nov-2026</b> (พุธ)<br>
    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; 4-Nov: ลงข้อมูลครบ 5 โรง (%s = %s ตัน) &middot; <b>TDC ลงปริมาณแล้ว (255 ตัน)</b> &middot; ผลโม่ 4-Nov ยังไม่เข้าทั้ง TN/TKT/PM/TDC (default/ว่าง) &rarr; เว้นว่าง &middot; <b style="color:#374151">TWIC 4-Nov เข้าแล้ว: 512 ตัน / 2.74 / CAG 13.14</b></b></span><br>
    อัปเดตเมื่อ: 5-Nov-2026 09:5x น. (T-1 = 4-Nov) (ไฟล์ Nov แก้ล่าสุด 5-Nov 09:17 น. &middot; TWIC ล่าสุด = 4-Nov)</div>
</div>

'''%(tot,fm(v3,0))
s=s[:a]+hd+s[b:]
b=s.find('<div class="kpi-row">'); c=s.find('<div class="caveat">')
kp='''<div class="kpi-row">
  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย (4-Nov &mdash; 5 โรง)</div><div class="value">%s<span class="unit">ตัน &middot; <b>%s</b> &middot; %+.1f%% vs 3-Nov (%s ตัน)</span></div></div>
  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก (4-Nov &middot; 5 โรง)</div><div class="value">%s<span class="unit">&#3647;/กก. (%.4f) &middot; <b>%s vs 3-Nov (%.4f)</b></span></div></div>
  <div class="kpi"><div class="label">%%Starch เฉลี่ยถ่วงน้ำหนัก (4-Nov &middot; 5 โรง)</div><div class="value">%s<span class="unit">%% &middot; <b>%+.2f จุด</b> vs 3-Nov (%s) &rarr; CBG รวม <b>%s</b></span></div></div>
  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = %s &middot; ไม่รวม MS)</div><div class="value">%s<span class="unit">&#3647;/กก. (%.3f) &middot; <b>%d โรง (%s) &middot; %s ตัน</b> &middot; <b style="color:#b45309">4-Nov ยังปิดไม่ได้ (รอผลโม่ TN, TKT, PM, TDC)</b></span></div></div>
</div>

'''%(fm(v3,0),tot,(v3/v2-1)*100,fm(v2,0),fm(p3),p3,'%+.2f'%(p3-p2),p2,fm(s3),s3-s2,fm(s2),fm(cbg3),lc[0],fm(lc[1]),lc[1],len(lc[2]),', '.join(lc[2]),fm(lc[3],0))
s=s[:b]+kp+s[c:]
c=s.find('<div class="caveat">'); t=s.find('<table>')
ch=[]
for p in ['TN','TKT','PM','MS','TDC']:
    j=prev_price(p); dd=S[p]['price'][I]-S[p]['price'][j]
    col='#b91c1c' if dd>0.004 else '#15803d'
    ch.append("<b style='color:%s'>%s %+.2f (%s &rarr; %s)</b>"%(col,p,dd,fm(S[p]['price'][j]),fm(S[p]['price'][I])))
vol=' &middot; '.join('%s %s &rarr; %s'%(p,fm(S[p]['vol'][prev_price(p)],0),fm(S[p]['vol'][I],0)) for p in ['TN','TKT','PM','MS','TDC'])
cv='''<div class="caveat">
  <b style="color:#b45309">&#9888; 4-Nov: ลงข้อมูลครบ 5 โรง (%s ตัน) &middot; ผลโม่ 4-Nov ยังไม่เข้า: TN 100.0%% / PM 100.0%% / TKT 95.0%% = default; MS 92.0%% = placeholder; TDC ว่าง &rarr; เว้นว่าง &mdash; <b>CAG รวม 4-Nov ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = %s: %s, %d โรง %s ตัน</b></b>
  <br><b style="color:#374151">ข้อมูลใหม่ (รอบนี้):</b> TDC 4-Nov ลงปริมาณแล้ว (255 ตัน / 3.87 / %%ST 24.08%%) &middot; 1&ndash;3-Nov ตรวจเทียบไฟล์ต้นทาง diff = 0
  <br><b style="color:#374151">ปริมาณ:</b> 4-Nov รวม %s ตัน (5 โรง) vs 3-Nov %s ตัน (5 โรง) &mdash; %s
  <br><b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย %s (3-Nov %s) &middot; %%ST %s%% (3-Nov %s%%) &middot; CBG %s &middot; %s
  <br><span style="color:#374151">TWIC (นิติบุคคลแยก, ไม่รวมยอดไทย): <b>4-Nov: 512 ตัน / 2.74 (-0.04) / %%ST 20.78%% / %%Recovery 100.39%% / CAG 13.14</b> &middot; 3-Nov: 576 ตัน / 2.78 / CAG 13.03 &middot; (ตัวเลข 4-Nov อ่านจากรูปตารางในอีเมล TWIC &mdash; ไม่มีไฟล์แนบ xlsx)</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติ (30 วัน, %%Recovery &lt;90%% หรือ &gt;110%%): %s</b>
  <br><b>&#128680; ค้างผลโม่ (4-Nov-2026): %s &middot; TWIC ไม่มีข้อมูล: %s</b>
</div>

'''%(fm(v3,0),lc[0],fm(lc[1]),len(lc[2]),fm(lc[3],0),fm(v3,0),fm(v2,0),vol,fm(p3),fm(p2),fm(s3),fm(s2),fm(cbg3),' &middot; '.join(ch),' &middot; '.join(an),pl,', '.join(twn))
s=s[:c]+cv+s[t:]
s=s.replace('(5-Oct ถึง 3-Nov-2026)','(6-Oct ถึง 4-Nov-2026)').replace('ช่วง 30 วันนี้ (5-Oct ถึง 3-Nov)','ช่วง 30 วันนี้ (6-Oct ถึง 4-Nov)')
s=s.replace('(อ่านไฟล์รอบ 4-Nov-2026)','(อ่านไฟล์รอบ 5-Nov-2026)')
open(new,'w',encoding='utf-8').write(s)
print(len(s)); print('anoms',an); print(pl); print(twn)
