import os
mem=os.path.expanduser('~/mnt/lovely/memory/')
L=open(mem+'_gen_1118r5.py',encoding='utf-8').read().split('\n')
def idx(prefix):
    h=[i for i,l in enumerate(L) if l.startswith(prefix)]
    assert len(h)==1,(prefix,len(h)); return h[0]
def setl(prefix,new): L[idx(prefix)]=new
def sub(prefix,a,b):
    i=idx(prefix); assert L[i].count(a)==1,(prefix,a,L[i].count(a)); L[i]=L[i].replace(a,b)
setl("BK='1118r5'","BK='1118r6'; D='17-Nov'; PD='16-Nov'; NOW='18-Nov-2026 15:1x น.'; DOW='อังคาร'")
setl("assert len(rows)==180 and","assert len(rows)==180 and key[('2026-11-17','PM')]['cag_thb_kg']=='15.90' and key[('2026-11-17','TDC')]['cag_thb_kg']=='' and key[('2026-11-16','TDC')]['cag_thb_kg']=='' and key[('2026-11-17','TDC')]['volume_tons']=='293' and key[('2026-11-16','TDC')]['volume_tons']=='278'")
setl("NEWROWS=","NEWROWS=[('2026-11-16','TDC',4.01,278,24.54,16.59,98.5),('2026-11-17','TDC',4.1,293,25.43,19.41,83.1)]")
setl("       'PM':",r"""       'PM':' &middot; <b>ปริมาณ 453 &rarr; 664 ตัน (+46.6%)</b> วันที่สองหลังกลับมารับซื้อ',""")
setl("EXTRA['TDC']=",r"""EXTRA['TDC']=' &middot; <b>ผลโม่เข้ารอบนี้ (15:1x น.)</b> &middot; <b style="color:#b91c1c">%Recovery 83.1% ต่ำผิดปกติ (&lt;90%) &rarr; CAG สูงสุดของ TDC ในรอบ 30 วัน</b> &middot; ปริมาณ 278 &rarr; 293 ตัน (+5.4%)'""")
setl("assert lc[0]=='11-Nov' and waitcore==","assert lc[0]=='11-Nov' and waitcore==['TN','TKT'], (waitcore,lc)")
setl("cagtxt=",r"""cagtxt='CAG รวม %s ปิดไม่ได้ (ผลโม่ %s ของ TN, TKT ยังไม่เข้า &middot; PM, TDC เข้าแล้ว; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = %s: %s, %d โรง %s ตัน'%(D,D,lc[0],fm(lc[1]),len(lc[2]),fm(lc[3],0))""")
setl("TWWHY=",r"""TWWHY='อีเมล put.p &ldquo;on Nov 17, 2026&rdquo; (รับ 18-Nov 13:16 น.)'""")
setl('    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; {D}:',r"""    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; {D}: ลงข้อมูลครบ {len(b3)} โรง ({tot} = {fm(v3,0)} ตัน) &middot; <b>ผลโม่ TDC {D} เข้าแล้วรอบนี้</b> (%Recovery {S["TDC"]["rec"][I]:g}% &rarr; CAG {fm(S["TDC"]["cag"][I])} &mdash; ต่ำผิดปกติ) + ผลโม่ TDC {PD} ย้อนหลัง (%Recovery {S["TDC"]["rec"][P]:g}% &rarr; CAG {fm(S["TDC"]["cag"][P])}) &middot; PM {D} เข้าแล้ว (CAG {fm(S["PM"]["cag"][I])}) &middot; ยังรอผลโม่ {D} ของ TN, TKT (TN 100.0% / TKT 95.0% = default &middot; MS 92.0% = placeholder ไม่นับ) &middot; <b style="color:#374151">TWIC {D} เข้าแล้ว ({fm(tw["vol"][I],0)} ตัน @ {fm(tw["price"][I])})</b></b></span><br>""")
sub('  <div class="kpi"><div class="label">CAG รวม','16-Nov รอ TN, PM, TDC &middot; 17-Nov รอ TN, TKT, TDC)','16-Nov รอ TN, PM &middot; 17-Nov รอ TN, TKT)')
setl('  <b style="color:#b45309">&#9888; {D}:',r"""  <b style="color:#b45309">&#9888; {D}: ลงข้อมูลครบ {len(b3)} โรง ({fm(v3,0)} ตัน: {tot}) &middot; ผลโม่ {D}: PM เข้าแล้ว (%Recovery {S["PM"]["rec"][I]:g}%) &middot; TDC เข้าแล้ว (%Recovery {S["TDC"]["rec"][I]:g}%) &middot; ยังไม่เข้า 2 โรงหลัก: TN 100.0% / TKT 95.0% (Total=R1=R2) = default &rarr; เว้นว่างทั้ง %Recovery และ CAG &middot; MS 92.0% = placeholder (ไม่นับ CAG) &mdash; <b>CAG รวม {D} ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = {lc[0]}: {fm(lc[1])}, {len(lc[2])} โรง {fm(lc[3],0)} ตัน (ไม่รวม MS)</b></b>""")
setl('  <br><b style="color:#374151">ข้อมูลใหม่',r"""  <br><b style="color:#374151">ข้อมูลใหม่ (รอบนี้ {NOW}):</b> <b>(1) ผลโม่ TDC {D} เข้าแล้ว</b>: %Recovery {S["TDC"]["rec"][I]:g}% &rarr; CBG {fm(S["TDC"]["price"][I]/(S["TDC"]["st"][I]/100))} &rarr; CAG {fm(S["TDC"]["cag"][I])} <b style="color:#b91c1c">(%Recovery ต่ำกว่า 90% &mdash; ควรยืนยันกับโรงงาน)</b> &middot; <b>(2) ผลโม่ TDC {PD} เข้าย้อนหลัง</b>: %Recovery {S["TDC"]["rec"][P]:g}% &rarr; CBG {fm(S["TDC"]["price"][P]/(S["TDC"]["st"][P]/100))} &rarr; CAG {fm(S["TDC"]["cag"][P])} &middot; ตรวจย้อนหลัง 1&ndash;17-Nov ทั้ง 5 โรงกับไฟล์ต้นทางทีละค่า: ไม่มีตัวเลขอื่นเปลี่ยน (TN 12&ndash;17-Nov ยัง 100.0% default &middot; PM 16-Nov ยัง 0.0% &middot; TKT 17-Nov ยัง 95.0% default) &middot; <b style="color:#b45309">TN 16-Nov %ST ยังเป็น 25.00% (ค่ากลม) อาจเป็นค่าชั่วคราว</b> &middot; วันย้อนหลัง (Nov) ที่ CAG รวมยังปิดไม่ได้: {" &middot; ".join(openback) or "&mdash;"}""")
setl('  <br><span style="color:#374151">TWIC (นิติบุคคลแยก',r"""  <br><span style="color:#374151">TWIC (นิติบุคคลแยก, ไม่รวมยอดไทย): <b>{D} เข้าแล้ว</b> ({TWWHY}) &middot; {twt(tj-1)} &middot; <b>{twt(tj)}</b></span>""")
open(mem+'_gen_1118r6.py','w',encoding='utf-8').write('\n'.join(L))
