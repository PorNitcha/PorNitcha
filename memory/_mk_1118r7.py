import os,shutil
base=os.path.expanduser('~/mnt/lovely/')
F=base+'Daily root dashboard - 17 November 2026.html'; C=base+'memory/root-price-history.csv'
shutil.copy2(C,C+'.bak_1118r7'); shutil.copy2(F,base+'memory/Daily root dashboard - 17 November 2026.html.bak_1118r7')
c=open(C,encoding='utf-8').read()
old='2026-11-17,TKT,4.1,285,25.11,,'; assert c.count(old)==1
c=c.replace(old,'2026-11-17,TKT,4.1,285,25.11,16.21,100.8'); open(C,'w',encoding='utf-8',newline='').write(c)
s=open(F,encoding='utf-8').read()
R=[
('<b>ผลโม่ TDC 17-Nov เข้าแล้วรอบนี้</b> (%Recovery 83.1% &rarr; CAG 19.41 &mdash; ต่ำผิดปกติ) + ผลโม่ TDC 16-Nov ย้อนหลัง (%Recovery 98.5% &rarr; CAG 16.59) &middot; PM 17-Nov เข้าแล้ว (CAG 15.90) &middot; ยังรอผลโม่ 17-Nov ของ TN, TKT (TN 100.0% / TKT 95.0% = default &middot; MS 92.0% = placeholder ไม่นับ)',
 '<b>ผลโม่ TKT 17-Nov เข้าแล้วรอบนี้</b> (%Recovery 100.8% &rarr; CAG 16.21) &middot; TDC 17-Nov เข้าแล้ว (%Recovery 83.1% &rarr; CAG 19.41 &mdash; ต่ำผิดปกติ) &middot; PM 17-Nov เข้าแล้ว (CAG 15.90) &middot; ยังรอผลโม่ 17-Nov ของ TN โรงเดียว (TN 100.0% = default &middot; MS 92.0% = placeholder ไม่นับ)',1),
('17-Nov รอ TN, TKT)','17-Nov รอ TN)',1),
('ผลโม่ 17-Nov: PM เข้าแล้ว (%Recovery 102.7%) &middot; TDC เข้าแล้ว (%Recovery 83.1%) &middot; ยังไม่เข้า 2 โรงหลัก: TN 100.0% / TKT 95.0% (Total=R1=R2) = default &rarr; เว้นว่างทั้ง %Recovery และ CAG',
 'ผลโม่ 17-Nov: TKT เข้าแล้ว (%Recovery 100.8%) &middot; PM เข้าแล้ว (%Recovery 102.7%) &middot; TDC เข้าแล้ว (%Recovery 83.1%) &middot; ยังไม่เข้า 1 โรงหลัก: TN 100.0% = default &rarr; เว้นว่างทั้ง %Recovery และ CAG',1),
('<b>(1) ผลโม่ TDC 17-Nov เข้าแล้ว</b>: %Recovery 83.1% &rarr; CBG 16.12 &rarr; CAG 19.41 <b style="color:#b91c1c">(%Recovery ต่ำกว่า 90% &mdash; ควรยืนยันกับโรงงาน)</b> &middot; <b>(2) ผลโม่ TDC 16-Nov เข้าย้อนหลัง</b>: %Recovery 98.5% &rarr; CBG 16.34 &rarr; CAG 16.59 &middot;',
 '<b>ผลโม่ TKT 17-Nov เข้าแล้ว</b>: %Recovery Total 100.8% (R1 0.0% / R2 100.8%) &rarr; CBG 16.33 &rarr; CAG 16.21 &middot; รอบก่อนหน้า (15:1x น.): TDC 17-Nov %Recovery 83.1% &rarr; CAG 19.41 <b style="color:#b91c1c">(%Recovery ต่ำกว่า 90% &mdash; ควรยืนยันกับโรงงาน)</b> &middot; TDC 16-Nov ย้อนหลัง %Recovery 98.5% &rarr; CAG 16.59 &middot;',1),
('TKT 17-Nov ยัง 95.0% default)','MS 17-Nov ยัง 92.0% placeholder)',1),
('TKT 8-Nov, 17-Nov &middot;','TKT 8-Nov &middot;',1),
('<td class="num">285</td><td class="num">25.11</td><td class="num">&mdash;</td><td class="num">&mdash;</td>','<td class="num">285</td><td class="num">25.11</td><td class="num">16.21</td><td class="num">100.8</td>',1),
('<span class="badge wait">รอผลโม่</span><span class="status-detail">ลงข้อมูล 17-Nov แล้ว &middot; ยังไม่มีผลโม่ (%Recovery ในไฟล์ = 95.0% (Total=R1=R2) = default &rarr; เว้นว่าง) &middot; CBG 16.33 &middot; เทียบ 16-Nov (4.14 / 430 ตัน) &middot;',
 '<span class="badge ok">ครบ</span><span class="status-detail">ผลโม่ 17-Nov เข้าแล้ว: %Recovery 100.8% (R1 0.0% / R2 100.8%) &rarr; CBG 16.33 &rarr; CAG 16.21 &middot; <b>ผลโม่เข้ารอบนี้ (16:1x น.)</b> &middot; เทียบ 16-Nov (4.14 / 430 ตัน) &middot;',1),
('<b>ผลโม่เข้ารอบนี้ (15:1x น.)</b>','ผลโม่เข้ารอบ 15:1x น.',1),
('(ผลโม่ 17-Nov ของ TN, TKT ยังไม่เข้า &middot; PM, TDC เข้าแล้ว; ไม่รวม MS)','(ผลโม่ 17-Nov ของ TN ยังไม่เข้า &middot; TKT, PM, TDC เข้าแล้ว; ไม่รวม MS)',1),
('18-Nov-2026 15:1x น.','18-Nov-2026 16:1x น.',4),
]
for o,n,k in R:
    assert s.count(o)==k,(o[:60],s.count(o)); s=s.replace(o,n)
# JS arrays: TKT block only
i=s.find('  TKT: { label: "TKT"'); j=s.find('},',i); blk=s[i:j]
a='16.47, 16.11, null]'; b='97.7, 100.0, null]'
assert blk.count(a)==1 and blk.count(b)==1
blk=blk.replace(a,'16.47, 16.11, 16.21]').replace(b,'97.7, 100.0, 100.8]')
s=s[:i]+blk+s[j:]
open(F,'w',encoding='utf-8',newline='').write(s); print('patched',len(s))
