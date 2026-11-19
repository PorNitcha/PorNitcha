import os
mem=os.path.expanduser('~/mnt/lovely/memory/')
L=open(mem+'_gen_1118r1.py',encoding='utf-8').read().split('\n')
def idx(prefix):
    h=[i for i,l in enumerate(L) if l.startswith(prefix)]
    assert len(h)==1,(prefix,len(h)); return h[0]
def setl(prefix,new): L[idx(prefix)]=new
def sub(prefix,a,b):
    i=idx(prefix); assert L[i].count(a)==1,(prefix,a,L[i].count(a)); L[i]=L[i].replace(a,b)
setl("BK='1118r1'","BK='1118r4'; D='17-Nov'; PD='16-Nov'; NOW='18-Nov-2026 13:1x น.'; DOW='อังคาร'")
setl("old=base+","old=base+'Daily root dashboard - 17 November 2026.html'")
setl("shutil.copy(old,","shutil.copy(old, mem+'Daily root dashboard - 17 November 2026.html.bak_'+BK)")
setl("assert len(rows)==180 and","assert len(rows)==180 and key[('2026-11-17','TDC')]['price_thb_kg']=='' and key[('2026-11-17','TDC')]['volume_tons']=='' and key[('2026-11-17','TN')]['price_thb_kg']=='3.96'")
setl("NEWROWS=","NEWROWS=[('2026-11-17','TDC',4.10,293,25.43,None,None)]")
setl("assert b3==","assert b3==thai and not noentry and not nobuy and common==thai, (b3,noentry,nobuy,common)")
i=idx("       'MS':"); L.insert(i+1,"EXTRA['TDC']=' &middot; <b>ลงข้อมูลรอบนี้ (13:1x น.)</b> &middot; ปริมาณ 278 &rarr; 293 ตัน (+5.4%)'")
setl("cagtxt=","cagtxt='CAG รวม %s ปิดไม่ได้ (ผลโม่ %s ของ TN, TKT, PM, TDC ยังไม่เข้า; ไม่รวม MS) &mdash; ล่าสุดที่ครบ = %s: %s, %d โรง %s ตัน'%(D,D,lc[0],fm(lc[1]),len(lc[2]),fm(lc[3],0))")
sub("T.append('    <tr class=\"total-row\">"," &middot; 4 โรง (TDC ยังไม่ลงปริมาณ 17-Nov ณ รอบนี้ &rarr; ยังไม่ใช่ยอดครบ 5 โรง)"," &middot; ครบ 5 โรง (TDC ลงข้อมูล 17-Nov แล้วรอบนี้)")
setl("OR='18-Oct","OR='19-Oct ถึง 17-Nov'; n0=s.count(OR); assert n0==2, n0")
setl('    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; {D}:','    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; {D}: ลงข้อมูลครบ {len(b3)} โรง ({tot} = {fm(v3,0)} ตัน) &middot; <b>TDC ลงข้อมูล {D} แล้วรอบนี้</b> ({fm(S["TDC"]["vol"][I],0)} ตัน @ {fm(S["TDC"]["price"][I])} / %ST {fm(S["TDC"]["st"][I])}%) &middot; ผลโม่ {D} ยังไม่เข้าทั้ง 5 โรง (TN 100.0% / PM 100.0% / TKT 95.0% = default &middot; MS 92.0% = placeholder &middot; TDC ว่าง) &middot; <b style="color:#374151">TWIC {D} ยังไม่มีไฟล์ (ล่าสุด = {lab[tj]})</b></b></span><br>')
sub('  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย',' &middot; TDC ยังไม่ลง)',')')
sub('  <div class="kpi"><div class="label">CAG รวม','17-Nov รอ TN, TKT, PM + TDC ยังไม่ลงข้อมูล)','17-Nov รอ TN, TKT, PM, TDC)')
setl('  <b style="color:#b45309">&#9888; {D}:','  <b style="color:#b45309">&#9888; {D}: ลงข้อมูลครบ {len(b3)} โรง ({fm(v3,0)} ตัน: {tot}) &middot; ผลโม่ {D} ยังไม่เข้าทั้ง 5 โรง: TN 100.0% / PM 100.0% / TKT 95.0% (Total=R1=R2) = default, MS 92.0% = placeholder, TDC ช่อง %Recovery ว่าง &rarr; เว้นว่างทั้ง %Recovery และ CAG &mdash; <b>CAG รวม {D} ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = {lc[0]}: {fm(lc[1])}, {len(lc[2])} โรง {fm(lc[3],0)} ตัน (ไม่รวม MS)</b></b>')
setl('  <br><b style="color:#374151">ข้อมูลใหม่','  <br><b style="color:#374151">ข้อมูลใหม่ (รอบนี้ {NOW}):</b> <b>TDC {D} ลงข้อมูลแล้ว</b> ({fm(S["TDC"]["vol"][I],0)} ตัน @ {fm(S["TDC"]["price"][I])} / %ST {fm(S["TDC"]["st"][I])}% / CBG {fm(S["TDC"]["price"][I]/(S["TDC"]["st"][I]/100))} &middot; %Recovery ยังว่าง) &rarr; ยอด {D} ครบ 5 โรงแล้ว &middot; ตรวจย้อนหลัง 1&ndash;16-Nov ทั้ง 5 โรงกับไฟล์ต้นทางทีละค่า: ไม่มีตัวเลขเปลี่ยน ไม่มีผลโม่ย้อนหลังเข้า (TN 12&ndash;16-Nov ยัง 100.0% default &middot; PM 16-Nov ยัง 100.0% &middot; TDC 16-Nov ยังว่าง) &middot; <b style="color:#b45309">TN 16-Nov %ST ยังเป็น 25.00% (ค่ากลม) อาจเป็นค่าชั่วคราว</b> &middot; วันย้อนหลัง (Nov) ที่ CAG รวมยังปิดไม่ได้: {\' &middot; \'.join(openback) or \'&mdash;\'}')
i=idx('  <br><b style="color:#374151">ปริมาณ:</b>'); a=L[i].find(' &middot; <b style="color:#b45309">{D} เป็นยอด'); assert a>0; L[i]=L[i][:a]
open(mem+'_gen_1118r4.py','w',encoding='utf-8').write('\n'.join(L))
