import os
mem=os.path.expanduser('~/mnt/lovely/memory/')
L=open(mem+'_gen_1118r4.py',encoding='utf-8').read().split('\n')
def idx(prefix):
    h=[i for i,l in enumerate(L) if l.startswith(prefix)]
    assert len(h)==1,(prefix,len(h)); return h[0]
def setl(prefix,new): L[idx(prefix)]=new
def sub(prefix,a,b):
    i=idx(prefix); assert L[i].count(a)==1,(prefix,a,L[i].count(a)); L[i]=L[i].replace(a,b)
setl("BK='1118r4'","BK='1118r5'; D='17-Nov'; PD='16-Nov'; NOW='18-Nov-2026 14:1x น.'; DOW='อังคาร'")
setl("assert len(rows)==180 and","assert len(rows)==180 and key[('2026-11-17','PM')]['cag_thb_kg']=='' and key[('2026-11-17','PM')]['price_thb_kg']=='4.02' and key[('2026-11-17','TWIC')]['price_thb_kg']=='' and key[('2026-11-17','TDC')]['volume_tons']=='293'")
setl("def g(x):","def g(x): return '' if x is None else (x if isinstance(x,str) else '%g'%x)")
setl("NEWROWS=","NEWROWS=[('2026-11-17','PM',4.02,664,24.63,'15.90',102.7),('2026-11-17','TWIC','3.10',510,21.96,13.61,103.62)]")
setl("       'PM':",r"""       'PM':' &middot; <b>ผลโม่เข้ารอบนี้ (14:1x น.)</b> &middot; <b>ปริมาณ 453 &rarr; 664 ตัน (+46.6%)</b> วันที่สองหลังกลับมารับซื้อ',""")
setl("EXTRA['TDC']=",r"""EXTRA['TDC']=' &middot; ปริมาณ 278 &rarr; 293 ตัน (+5.4%)'""")
setl("assert lc[0]=='11-Nov' and waitcore==","assert lc[0]=='11-Nov' and waitcore==['TN','TKT','TDC'], (waitcore,lc)")
setl("cagtxt=",r"""cagtxt='CAG รวม %s ปิดไม่ได้ (ผลโม่ %s ของ TN, TKT, TDC ยังไม่เข้า &middot; PM เข้าแล้ว; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = %s: %s, %d โรง %s ตัน'%(D,D,lc[0],fm(lc[1]),len(lc[2]),fm(lc[3],0))""")
sub("T.append('    <tr class=\"total-row\">"," &middot; ครบ 5 โรง (TDC ลงข้อมูล 17-Nov แล้วรอบนี้)"," &middot; ครบ 5 โรง")
setl("assert lab[tj]==","assert lab[tj]=='17-Nov' and tj==I and tw['vol'][I-1]")
setl("TWWHY=",r"""TWWHY='อีเมล put.p &ldquo;on Nov 17, 2026&rdquo; (รับ 18-Nov 13:16 น.) เข้าแล้วรอบนี้'""")
i=idx("T.append('    <tr><td><span class=\"plant-name\">TWIC")
L[i:i+1]=["twc,twdot,twd=dl(tw['price'][I],tw['price'][I-1])",
r"""T.append('    <tr><td><span class="plant-name">TWIC กัมพูชา</span><br><span class="plant-code">TWIC &middot; นิติบุคคลแยก</span></td>\n      <td class="num">%s</td><td class="num"><span class="dot %s"></span><span class="delta %s">%s</span></td>\n      <td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%g</td>\n      <td><span class="badge ok">ครบ</span><span class="status-detail">%s &middot; %%Recovery %g%% &rarr; CAG %s &middot; เทียบ %s (%s / %s ตัน) &middot; ไม่รวมยอดไทย</span></td>\n    </tr>'%(fm(tw['price'][I]),twdot,twc,twd,fm(tw['vol'][I],0),fm(tw['st'][I]),fm(tw['cag'][I]),tw['rec'][I],TWWHY,tw['rec'][I],fm(tw['cag'][I]),lab[I-1],fm(tw['price'][I-1]),fm(tw['vol'][I-1],0)))"""]
setl('    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; {D}:',r"""    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; {D}: ลงข้อมูลครบ {len(b3)} โรง ({tot} = {fm(v3,0)} ตัน) &middot; <b>ผลโม่ PM {D} เข้าแล้วรอบนี้</b> (%Recovery {S["PM"]["rec"][I]:g}% &rarr; CAG {fm(S["PM"]["cag"][I])}) &middot; ยังรอผลโม่ {D} ของ TN, TKT, TDC (TN 100.0% / TKT 95.0% = default &middot; TDC ว่าง &middot; MS 92.0% = placeholder ไม่นับ) &middot; <b style="color:#374151">TWIC {D} เข้าแล้วรอบนี้ ({fm(tw["vol"][I],0)} ตัน @ {fm(tw["price"][I])})</b></b></span><br>""")
sub('    อัปเดตเมื่อ:','on Nov 16, 2026','on Nov 17, 2026')
sub('  <div class="kpi"><div class="label">CAG รวม','17-Nov รอ TN, TKT, PM, TDC)','17-Nov รอ TN, TKT, TDC)')
setl('  <b style="color:#b45309">&#9888; {D}:',r"""  <b style="color:#b45309">&#9888; {D}: ลงข้อมูลครบ {len(b3)} โรง ({fm(v3,0)} ตัน: {tot}) &middot; ผลโม่ {D}: PM เข้าแล้ว (%Recovery {S["PM"]["rec"][I]:g}%) &middot; ยังไม่เข้า 3 โรงหลัก: TN 100.0% / TKT 95.0% (Total=R1=R2) = default, TDC ช่อง %Recovery ว่าง &rarr; เว้นว่างทั้ง %Recovery และ CAG &middot; MS 92.0% = placeholder (ไม่นับ CAG) &mdash; <b>CAG รวม {D} ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = {lc[0]}: {fm(lc[1])}, {len(lc[2])} โรง {fm(lc[3],0)} ตัน (ไม่รวม MS)</b></b>""")
setl('  <br><b style="color:#374151">ข้อมูลใหม่',r"""  <br><b style="color:#374151">ข้อมูลใหม่ (รอบนี้ {NOW}):</b> <b>(1) ผลโม่ PM {D} เข้าแล้ว</b>: %Recovery {S["PM"]["rec"][I]:g}% &rarr; CBG {fm(S["PM"]["price"][I]/(S["PM"]["st"][I]/100))} &rarr; CAG {fm(S["PM"]["cag"][I])} &middot; <b>(2) TWIC {D} เข้าแล้ว</b>: {twt(I)} &middot; ตรวจย้อนหลัง 1&ndash;16-Nov ทั้ง 5 โรงกับไฟล์ต้นทางทีละค่า: ไม่มีตัวเลขเปลี่ยน ไม่มีผลโม่ย้อนหลังเข้า (TN 12&ndash;16-Nov ยัง 100.0% default &middot; PM 16-Nov ยัง 0.0% &middot; TDC 16-Nov ยังว่าง) &middot; <b style="color:#b45309">TN 16-Nov %ST ยังเป็น 25.00% (ค่ากลม) อาจเป็นค่าชั่วคราว</b> &middot; วันย้อนหลัง (Nov) ที่ CAG รวมยังปิดไม่ได้: {" &middot; ".join(openback) or "&mdash;"}""")
setl('  <br><span style="color:#374151">TWIC (นิติบุคคลแยก',r"""  <br><span style="color:#374151">TWIC (นิติบุคคลแยก, ไม่รวมยอดไทย): <b>{D} เข้าแล้วรอบนี้</b> ({TWWHY}) &middot; {twt(tj-1)} &middot; <b>{twt(tj)}</b></span>""")
sub('  ที่มา (internal):',' &middot; ของ %s ยังไม่มี)',')')
setl("'''%(NOW,lab[tj],D)","'''%(NOW,lab[tj])")
open(mem+'_gen_1118r5.py','w',encoding='utf-8').write('\n'.join(L))
