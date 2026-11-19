import os
m=os.path.expanduser('~/mnt/lovely/memory/')
s=open(m+'_gen_1117r4.py',encoding='utf-8').read()
R=[
("BK='1117r4'","BK='1117r11'"),
("NOW='17-Nov-2026 11:1x น.'","NOW='17-Nov-2026 18:4x น.'"),
("key[('2026-11-16','TN')]['price_thb_kg']=='3.85'","key[('2026-11-16','TN')]['price_thb_kg']=='4' and key[('2026-11-16','TKT')]['recovery_pct']==''"),
("NEWROWS=[('TN',4.00,312,25.00,None,None)]","NEWROWS=[('TKT',4.14,430,25.70,16.11,100.0)]"),
("       'PM':' &middot; กลับมารับซื้อวันแรก","       'TKT':' &middot; <b>ผลโม่เข้าในรอบ 18:4x น.</b> (รอบก่อนเป็น 95.0% default) &middot; R1 102.0% / R2 96.6% / Total 100.0%',\n       'PM':' &middot; กลับมารับซื้อวันแรก"),
("set(waitcore)==set(core), (waitcore,lc)","waitcore==['TN','PM','TDC'], (waitcore,lc)"),
("(ผลโม่ %s ของ TN, TKT, PM, TDC ยังไม่เข้า; ไม่รวม MS)","(ผลโม่ %s ของ TN, PM, TDC ยังไม่เข้า; ไม่รวม MS)"),
("ผลโม่ {D}: เข้าแล้วเฉพาะ MS (103.3% &rarr; CAG 14.32 &middot; ไม่นับ CAG รวม) &middot; TN, TKT, PM, TDC ยังไม่เข้า (ค่าในไฟล์เป็น default/ว่าง)","ผลโม่ {D}: เข้าแล้ว TKT (100.0% &rarr; CAG 16.11 &middot; ใหม่รอบ 18:4x น.) และ MS (103.3% &rarr; CAG 14.32 &middot; ไม่นับ CAG รวม) &middot; TN, PM, TDC ยังไม่เข้า (ค่าในไฟล์เป็น default/ว่าง)"),
("16-Nov รอผลโม่ TN, TKT, PM, TDC)","16-Nov รอผลโม่ TN, PM, TDC)"),
("ผลโม่ {D}: MS เข้าแล้ว (103.3% &rarr; CAG 14.32 &middot; ไม่นับ CAG รวม) &middot; ยังไม่เข้า: TN 100.0% / PM 100.0% / TKT 95.0% (Total=R1=R2) = default, TDC ว่าง","ผลโม่ {D}: TKT เข้าแล้ว (100.0% &rarr; CAG 16.11) &middot; MS เข้าแล้ว (103.3% &rarr; CAG 14.32 &middot; ไม่นับ CAG รวม) &middot; ยังไม่เข้า: TN 100.0% / PM 100.0% = default, TDC ว่าง"),
("<b style=\"color:#374151\">ข้อมูลใหม่ (รอบนี้):</b> <b>TN {D} ราคาแก้","<b style=\"color:#374151\">ข้อมูลใหม่ (รอบนี้ 18:4x น.):</b> <b>ผลโม่ TKT {D} เข้า: %Recovery 95.0% (default) &rarr; 100.0%</b> (R1 102.0% / R2 96.6%) &rarr; CAG {fm(S['TKT']['cag'][I])} (ตรวจ: {fm(S['TKT']['price'][I])} &divide; {fm(S['TKT']['st'][I])}% = CBG {fm(S['TKT']['price'][I]/(S['TKT']['st'][I]/100))} &divide; 100.0% = {fm(S['TKT']['price'][I]/(S['TKT']['st'][I]/100)/1.0)} &#10003;) &middot; <b style=\"color:#374151\">รอบ 11:1x น.:</b> <b>TN {D} ราคาแก้"),
]
for a,b in R:
    assert s.count(a)==1,(s.count(a),a)
    s=s.replace(a,b)
open(m+'_gen_1117r11.py','w',encoding='utf-8').write(s)
print('ok')
