import csv,re,json
M='memory/'
src='Daily root dashboard - 12 October 2026.html'
dst='Daily root dashboard - 13 October 2026.html'
t=open(src,encoding='utf-8').read()
rows=list(csv.DictReader(open(M+'root-price-history.csv',encoding='utf-8')))
dates=sorted({r['date'] for r in rows})
import datetime
lab=lambda d:(lambda x:f"{x.day}-{x.strftime('%b')}")(datetime.date.fromisoformat(d))
dl=[lab(d) for d in dates]
t=re.sub(r'const dates = \[[^\]]*\];','const dates = '+json.dumps(dl)+';',t,count=1)
def arr(p,k,dt=lambda x:x):
    out=[]
    for d in dates:
        r=[x for x in rows if x['date']==d and x['plant']==p][0]
        out.append(None if r[k]=='' else float(r[k]))
    return json.dumps([ (int(v) if (k=='volume_tons' and v is not None) else v) for v in out]).replace('null','null')
for p in ['TN','TKT','PM','MS','TDC','TWIC']:
    i=t.find(f'  {p}: {{ label: "{p}"'); j=t.find('\n  },',i)
    blk=t[i:j]
    for name,k in (('price','price_thb_kg'),('volume','volume_tons'),('starch','starch_pct'),('cag','cag_thb_kg'),('recov','recovery_pct')):
        blk=re.sub(r'(\n    %s:\s+)\[[^\]]*\]'%name,lambda m:m.group(1)+arr(p,k),blk,count=1)
    t=t[:i]+blk+t[j:]
# ---- text blocks
H=lambda s:s
upd='''<div class="updated">
    ข้อมูลล่าสุด (เมื่อวาน): <b>13-Oct-2026</b> (อังคาร)<br>
    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; 13-Oct: ลงข้อมูลเพียง TKT + MS (TN, PM, TDC ยังไม่ลงปริมาณ &mdash; ราคา/%ST ในไฟล์เป็น forecast &rarr; เว้นว่าง) &middot; ผลโม่ 13-Oct ยังไม่เข้าเลย (TKT 95.0% / MS 90.0% = default/placeholder) &middot; TWIC 9&ndash;13-Oct ยังไม่ส่ง</b></span><br>
    อัปเดตเมื่อ: 14-Oct-2026 08:xx น. (T-1 = 13-Oct) (ไฟล์ Oct แก้ล่าสุด 14-Oct 07:48 น. &middot; ไฟล์ Sep แก้ล่าสุด 5-Oct 16:49 น. &middot; ทบทวน 14-Sep&ndash;13-Oct เทียบไฟล์ต้นทาง: เพิ่มวัน 13-Oct &middot; ข้อมูลไทย 1&ndash;12-Oct diff = 0)</div>'''
t=re.sub(r'<div class="updated">.*?</div>(?=\s*</div>\s*\n\s*<div class="kpi-row">)',lambda m:upd,t,count=1,flags=re.S)
kpi='''<div class="kpi-row">
  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย (13-Oct &mdash; ลงข้อมูล 2 โรง)</div><div class="value">1,531<span class="unit">ตัน &middot; <b>TKT 871 &middot; MS 660</b> &middot; TN, PM, TDC ยังไม่ลง &middot; เทียบ 2 โรงเดียวกันของ 12-Oct (1,145 ตัน) <b>+386, +33.7%</b> (ไม่เทียบกับ 2,199 ตันของ 4 โรง 12-Oct)</span></div></div>
  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก (13-Oct &middot; 2 โรงที่ลงข้อมูล)</div><div class="value">4.04<span class="unit">&#3647;/กก. (4.0350) &middot; <b style="color:#b91c1c">+0.08 vs 2 โรงเดียวกัน 12-Oct (3.9547)</b> &middot; เทียบข้ามองค์ประกอบโรงไม่ได้ (MS ราคาสูงกว่าเฉลี่ย)</span></div></div>
  <div class="kpi"><div class="label">%Starch เฉลี่ยถ่วงน้ำหนัก (13-Oct &middot; 2 โรงที่ลงข้อมูล)</div><div class="value">26.08<span class="unit">% &middot; <b>+1.10 จุด</b> vs 2 โรงเดียวกัน 12-Oct (24.98) &rarr; CBG รวม <b>15.47</b></span></div></div>
  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = 9-Oct &middot; ไม่รวม MS)</div><div class="value">16.70<span class="unit">&#3647;/กก. (16.697) &middot; <b>3 โรง (TN, TKT, PM) &middot; 2,314 ตัน</b> &middot; <b style="color:#b45309">10-Oct, 11-Oct รอผลโม่ TDC &middot; 12-Oct รอผลโม่ TN, PM &middot; 13-Oct รอผลโม่ TKT + ยังไม่ลง TN, PM, TDC</b></span></div></div>
</div>'''
t=re.sub(r'<div class="kpi-row">.*?\n</div>(?=\s*\n\s*<div class="caveat">)',lambda m:kpi,t,count=1,flags=re.S)
cav='''<div class="caveat">
  <b style="color:#b45309">&#9888; 13-Oct: ลงข้อมูล TKT + MS เท่านั้น &mdash; ยังไม่มีผลโม่ใหม่ (TKT 95.0% ทั้ง recTotal/R1/R2 = default &rarr; เว้นว่าง &middot; MS 90.0% = placeholder &rarr; เว้นว่าง) &middot; CAG รวม 13-Oct ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = 9-Oct: 16.70, 3 โรง 2,314 ตัน</b> &mdash; TKT 3.91 / 871 ตัน / 24.14% &middot; MS 4.20 / 660 ตัน / 28.65% &middot; TN (ไฟล์ 3.84 / 24.60%), PM (4.04 / 23.50%), TDC (4.17 / 24.20%) ไม่มีปริมาณ = forecast &rarr; เว้นว่าง
  <br><b style="color:#374151">ผลโม่ใหม่/Backfill:</b> ไม่มีผลโม่ใหม่รอบนี้ &middot; ตรวจย้อนหลัง 1&ndash;12-Oct เทียบไฟล์ต้นทาง diff = 0 (TKT 12-Oct 106.8% / CAG 15.36 คงเดิม) &middot; TN, PM, MS 12-Oct และ TDC 10-Oct, 11-Oct ยังรอผลโม่
  <br><b style="color:#374151">ปริมาณ:</b> 13-Oct ลง 2 โรง รวม 1,531 ตัน (เทียบ 2 โรงเดียวกัน 12-Oct: 1,145 &rarr; 1,531, +386, +33.7%) &mdash; TKT 755 &rarr; 871 (+116, +15.4%) &middot; <b style="color:#b45309">MS 390 &rarr; 660 (+270, +69.2%)</b> &middot; TN, PM, TDC ยังไม่ลง (12-Oct: TN 687, PM 367, TDC ไม่ลง)
  <br><b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย 2 โรง 4.04 (+0.08 vs 2 โรงเดียวกัน 12-Oct) &middot; %ST 26.08% (+1.10 จุด) &middot; CBG 15.47 &middot; <b style="color:#b91c1c">TKT +0.02 (3.89 &rarr; 3.91)</b> &middot; <b style="color:#b91c1c">MS +0.12 (4.08 &rarr; 4.20)</b> &middot; verify CBG: TKT 3.91&divide;24.14% = 16.20 &middot; MS 4.20&divide;28.65% = 14.66 &middot; TKT %ST 23.72 &rarr; 24.14, MS 27.42 &rarr; 28.65
  <br><span style="color:#374151">TWIC (นิติบุคคลแยก): <b>9&ndash;13-Oct ยังไม่ส่ง</b> (อีเมลล่าสุด = "on Oct 08, 2026" ได้รับ 9-Oct 08:25 น.) &rarr; เว้นว่าง ไม่เดา &middot; 8-Oct ล่าสุด: ราคา 2.75 / 138 ตัน / %ST 20.43% / %Rec 105.11% / CAG 12.81 &middot; ยังขาดของ 24-Sep, 27-Sep, 9-Oct ถึง 13-Oct</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติที่ยังไม่ถูกแก้ (ในช่วง 30 วัน, %Recovery &lt;90% หรือ &gt;110%): TN 22-Sep 89.2% &middot; TN 29-Sep 86.6% &middot; TN 5-Oct 86.0% &middot; TKT 19-Sep 129.5% &middot; TKT 30-Sep 127.5% &middot; TKT 2-Oct 85.3% &middot; PM 14-Sep 65.3% &middot; PM 20-Sep 82.3% &middot; MS 14-Sep 42.1% &middot; MS 16-Sep 78.0% &middot; MS 22-Sep 84.3% &middot; MS 26-Sep 81.2% &middot; MS 30-Sep 71.3% &middot; MS 3-Oct 88.8% &middot; MS 4-Oct 89.6% &middot; MS 5-Oct 89.6% &middot; MS 6-Oct 80.1% &middot; MS 7-Oct 82.3% &middot; MS 8-Oct 89.8%</b>
  <br><b>&#128680; ค้างผลโม่ (14-Oct-2026): TN 27-Sep, 28-Sep, 12-Oct &middot; TKT 20-Sep, 13-Oct &middot; PM 27-Sep, 12-Oct &middot; MS 15-Sep, 20-Sep, 21-Sep, 25-Sep, 28-Sep, 29-Sep, 12-Oct, 13-Oct &middot; TDC 19-Sep, 23-Sep, 2-Oct, 10-Oct, 11-Oct</b>
</div>'''
t=re.sub(r'<div class="caveat">\s*<b style="color:#b45309">&#9888; 12-Oct.*?\n</div>(?=\s*\n<table>)',lambda m:cav,t,count=1,flags=re.S)
def none_row(name,code,detail):
    return f'''    <tr><td><span class="plant-name">{name}</span><br><span class="plant-code">{code}</span></td>
      <td class="num">&mdash;</td><td class="num"><span class="dot grey"></span><span class="delta flat">&mdash;</span></td>
      <td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge none">ยังไม่ลงข้อมูล</span><span class="status-detail">{detail}</span></td>
    </tr>
'''
tb='\n'+none_row('อ.เมือง อุดรธานี','TN','13-Oct ไม่มีปริมาณ (ไฟล์ราคา 3.84 / %ST 24.60% = forecast &rarr; เว้นว่าง) &middot; ปริมาณล่าสุด 12-Oct 687 ตัน (ผลโม่รอ) &middot; ผลโม่ล่าสุด 11-Oct 95.8% (CAG 16.05) &middot; ค้างผลโม่ 27-Sep, 28-Sep, 12-Oct')
tb+=f'''    <tr><td><span class="plant-name">ท่าคันโท กาฬสินธุ์</span><br><span class="plant-code">TKT</span></td>
      <td class="num">3.91</td><td class="num"><span class="dot red"></span><span class="delta up">+0.02</span></td>
      <td class="num">871</td><td class="num">24.14</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge wait">รอผลโม่</span><span class="status-detail">ยังไม่มีผลโม่ 13-Oct (recTotal = R1 = R2 = 95.0% = default &rarr; เว้นว่าง) &middot; CBG 3.91&divide;24.14% = 16.20 ✓ &middot; ปริมาณ +15.4% จาก 12-Oct (755) &middot; ผลโม่ล่าสุด 12-Oct 106.8% (CAG 15.36) &middot; ค้างผลโม่ 20-Sep, 13-Oct</span></td>
    </tr>
'''
tb+=none_row('พิมาย โคราช','PM','13-Oct ไม่มีปริมาณ (ไฟล์ราคา 4.04 / %ST 23.50% = forecast &rarr; เว้นว่าง) &middot; ปริมาณล่าสุด 12-Oct 367 ตัน (ผลโม่รอ) &middot; ผลโม่ล่าสุด 11-Oct 107.6% (CAG 14.58) &middot; ค้างผลโม่ 27-Sep, 12-Oct')
tb+=f'''    <tr><td><span class="plant-name">แม่สอด ตาก</span><br><span class="plant-code">MS</span></td>
      <td class="num">4.20</td><td class="num"><span class="dot red"></span><span class="delta up">+0.12</span></td>
      <td class="num">660</td><td class="num">28.65</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge wait">รอผลโม่</span><span class="status-detail">ยังไม่มีผลโม่ 13-Oct (%Recovery 90.0% = placeholder &rarr; เว้นว่าง) &middot; CBG 4.20&divide;28.65% = 14.66 ✓ &middot; ไม่นับใน CAG รวม &middot; ปริมาณ +69.2% จาก 12-Oct (390) &middot; ผลโม่ล่าสุด 11-Oct 91.7% (CAG 16.49)</span></td>
    </tr>
'''
tb+=none_row('บ้านฉาง ระยอง','TDC','13-Oct ไม่มีปริมาณ (ราคา 4.17 / %ST 24.20% = forecast &rarr; เว้นว่าง) &middot; ผลโม่ล่าสุด 8-Oct 96.1% (CAG 16.63) &middot; ค้างผลโม่ 19-Sep, 23-Sep, 2-Oct, 10-Oct, 11-Oct')
tb+='''    <tr class="total-row"><td>รวมโรงงานไทย (13-Oct &mdash; ลงข้อมูล 2 โรง)</td>
      <td class="num">4.04</td><td class="num"><span class="dot red"></span><span class="delta up">+0.08</span></td>
      <td class="num">1,531</td><td class="num">26.08</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="status-detail">ราคา/%ST ถ่วงน้ำหนักทุกโรงที่ลงข้อมูล (TKT, MS) &middot; เทียบ 2 โรงเดียวกันของ 12-Oct (3.95 / 24.98%) &middot; CBG 15.47 &middot; <b>CAG รวม 13-Oct ปิดไม่ได้ (รอผลโม่ TKT และ TN, PM, TDC ยังไม่ลง) &mdash; ล่าสุดที่ครบ = 9-Oct 16.70 (3 โรง 2,314 ตัน)</b></span></td>
    </tr>
'''
tb+=none_row('TWIC กัมพูชา','TWIC &middot; นิติบุคคลแยก','9&ndash;13-Oct ยังไม่มีอีเมลจาก put.p (ล่าสุด = 8-Oct: 2.75 / 138 ตัน / CAG 12.81) &middot; เว้นว่าง ไม่เดา &middot; ยังขาดของ 24-Sep, 27-Sep &middot; แยกจากยอดไทย').replace('ยังไม่ลงข้อมูล','ยังไม่ส่ง')
t=re.sub(r'(</thead>).*?(</table>)',lambda m:m.group(1)+tb+m.group(2),t,count=1,flags=re.S)
t=t.replace('แนวโน้ม 30 วันย้อนหลัง (13-Sep ถึง 12-Oct-2026)','แนวโน้ม 30 วันย้อนหลัง (14-Sep ถึง 13-Oct-2026)')
t=t.replace('ช่วง 30 วันนี้ (13-Sep ถึง 12-Oct)','ช่วง 30 วันนี้ (14-Sep ถึง 13-Oct)')
t=re.sub(r'ที่มา \(internal\):.*?ราคาที่แสดงคือราคาที่',lambda m:'ที่มา (internal): SharePoint &mdash; TWPCROOTSOURCINGTEAM / "Daily root purchased report - 10_Oct 2026" (1&ndash;13-Oct) และ "09_Sep 2026" (14&ndash;30-Sep) (อ่านไฟล์รอบ 14-Oct-2026) &middot; TWIC: อีเมล put.p@thaiwah.com (ล่าสุด = ของ 8-Oct ได้รับ 9-Oct 08:25 น. &middot; ยังไม่มีของ 9&ndash;13-Oct &middot; ยังขาดของ 24-Sep, 27-Sep) &middot; ราคาที่แสดงคือราคาที่',t,count=1,flags=re.S)
open(dst,'w',encoding='utf-8').write(t)
print(len(t))
