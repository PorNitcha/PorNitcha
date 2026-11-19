s=open('_gen_1116d.py',encoding='utf-8').read()
R=[
("BK='1116r4'","BK='1116r5'"),
("NOW='16-Nov-2026 11:1x น.'","NOW='16-Nov-2026 13:1x น.'"),
('SRC="""2026-11-13,MS,4.32,367,28.6,18.98,79.6\n2026-11-14,MS,4.38,246,30.52,15.89,90.3\n2026-11-15,TDC,4.06,170,24.77,,"""','SRC="""2026-11-15,MS,4.31,242,28.64,16.33,92.2"""'),
("exp={('2026-11-13','MS'),('2026-11-14','MS'),('2026-11-15','TDC')}","exp={('2026-11-15','MS')}"),
("ผลโม่ {D}: TKT เข้าแล้ว (97.7%) &middot; TN ยังเป็น default &middot; TDC ยังว่าง &middot; <b style=\"color:#374151\">ใหม่รอบนี้: TDC {D} ลงข้อมูลแล้ว &middot; ผลโม่ MS 13, 14-Nov เข้าแล้ว</b>","ผลโม่ {D}: TKT เข้าแล้ว (97.7%) &middot; MS เข้าแล้ว (92.2%, ไม่นับ CAG รวม) &middot; TN ยังเป็น default &middot; TDC ยังว่าง &middot; <b style=\"color:#374151\">ใหม่รอบนี้: ผลโม่ MS {D} เข้าแล้ว</b>"),
("TN 100.0% = default, MS 92.0% = placeholder, TDC ช่องว่าง &rarr; เว้นว่างทั้ง %Recovery และ CAG","MS เข้าแล้ว (92.2% &rarr; CAG 16.33; ไม่นับ CAG รวม) &middot; TN 100.0% = default, TDC ช่องว่าง &rarr; เว้นว่างทั้ง %Recovery และ CAG"),
]
for a,b in R:
    assert s.count(a)==1,(s.count(a),a[:40]); s=s.replace(a,b)
i=s.find("NEWTXT='"); j=s.find('\n',i)
s=s[:i]+"NEWTXT='ผลโม่ MS %s เข้าแล้ว: %%Recovery %g%% (เดิม 92.0%% = placeholder) &rarr; CBG %s &rarr; CAG %s (MS ไม่นับใน CAG รวม &rarr; KPI รวมไม่เปลี่ยน)'%(D,S['MS']['rec'][I],fm(S['MS']['price'][I]/(S['MS']['st'][I]/100)),fm(S['MS']['cag'][I]))"+s[j:]
open('_gen_1116e.py','w',encoding='utf-8').write(s)
