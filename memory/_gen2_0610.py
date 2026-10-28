import re,json,datetime
m=json.load(open('memory/_m_0610.json'))
txt=open('memory/_stage1_0610.html',encoding='utf-8').read()
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime('%H:%M')
L=txt.split('\n')
def idx(s,start=0):
    for i,l in enumerate(L):
        if i>=start and s in l: return i
    raise Exception(s)
pend=m['pending']
pl=lambda p:', '.join(pend[p])
# header
i=idx('ข้อมูลล่าสุด (เมื่อวาน)'); L[i]='    ข้อมูลล่าสุด (เมื่อวาน): <b>5-Oct-2026</b> (จันทร์)<br>'
i=idx('<span style="color:#9ca3af"><b style="color:#b45309">'); 
L[i]='    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; 5-Oct: ลงปริมาณ/ราคา 4 โรง (TN/TKT/PM/MS) แต่ %Recovery ยังเป็น default/ว่าง &rarr; รอผลโม่ทั้งหมด &middot; TDC ยังไม่ลงปริมาณ (มีเฉพาะราคา/%ST forecast) &middot; Backfill: TDC 1-Oct ผลโม่เข้าแล้ว 94.5% &middot; TWIC ของ 5-Oct ยังไม่ส่ง</b></span><br>'
i=idx('อัปเดตเมื่อ:'); L[i]=f'    อัปเดตเมื่อ: 6-Oct-2026 {now} น. (ไฟล์ Oct แก้ล่าสุด 6-Oct 06:26 น. &middot; ไฟล์ Sep แก้ล่าสุด 5-Oct 16:49 น. &middot; ทบทวน 6-Sep&ndash;5-Oct เทียบไฟล์ต้นทาง: TDC 1-Oct ผลโม่เข้าแล้ว 94.5% (CAG 18.80) &middot; จุดอื่น diff = 0)</div>'
# KPI
i=idx('class="kpi"')
L[i]='  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย (5-Oct &mdash; ซื้อ 4 โรง · TDC ยังไม่ลงปริมาณ)</div><div class="value">3,400<span class="unit">ตัน &middot; <b>TN 1,049 &middot; TKT 1,032 &middot; PM 813 &middot; MS 506 &middot; TDC &mdash;</b> &middot; เทียบ 4-Oct (4,181 ตัน, 5 โรง) &minus;781, &minus;18.7% &middot; like-for-like 4 โรง (3,748) &minus;348, &minus;9.3%</span></div></div>'
L[i+1]='  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก (5-Oct &middot; 4 โรง)</div><div class="value">3.92<span class="unit">&#3647;/กก. (3.9189) &middot; <b style="color:#1a9850">&minus;0.05 จาก 4-Oct (3.9728)</b></span></div></div>'
L[i+2]='  <div class="kpi"><div class="label">%Starch เฉลี่ยถ่วงน้ำหนัก (5-Oct &middot; 4 โรง)</div><div class="value">23.91<span class="unit">% &middot; <b>&minus;0.11 จุด</b> vs 4-Oct (24.02) &rarr; CBG รวม <b>16.39 (&minus;0.15)</b> vs 16.54</span></div></div>'
L[i+3]='  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = 30-Sep &middot; ไม่รวม MS)</div><div class="value">16.37<span class="unit">&#3647;/กก. (16.366) &middot; <b>4 โรง &middot; 2,464 ตัน</b> &middot; <b style="color:#b45309">1&ndash;5-Oct ปิดไม่ได้ &mdash; 5-Oct รอผลโม่ TN/TKT/PM</b></span></div></div>'
# caveat
i=idx('<div class="caveat">')
L[i+1]='  <b style="color:#b45309">&#9888; 5-Oct: TN/TKT/PM รอผลโม่ (%Recovery default/0.0%) &mdash; CAG รวมยังปิดไม่ได้</b> &mdash; MS %Recovery 92.0% = placeholder ของไฟล์ (ไม่นับเป็นผลโม่จริง) &middot; TN 3.87 / 1,049 ตัน / 24.70% (%Recovery 100.0% = default) &middot; TKT 3.99 / 1,032 ตัน / 23.72% (%Recovery 95.0% R1=R2=Total = default) &middot; PM 3.81 / 813 ตัน / 22.11% (%Recovery 0.0% = ยังไม่มี) &middot; MS 4.05 / 506 ตัน / 25.52% &middot; TDC ปริมาณว่าง (ราคา 4.17 / %ST 24.20% = forecast ไม่แสดง)'
L[i+2]='  <br><b style="color:#374151">Backfill:</b> TDC 1-Oct %Recovery 94.5% (CAG 18.80; verify CBG 4.16&divide;23.41% = 17.77 &rarr; &divide;94.5% = 18.80 ✓) &mdash; TN 1&ndash;5-Oct, TKT 5-Oct, PM 5-Oct, MS 5-Oct และ TDC 2-Oct ยังรอผลโม่ &rarr; CAG รวมของ 1&ndash;5-Oct ยังปิดไม่ได้ (ล่าสุดที่ครบ = 30-Sep: 16.37)'
L[i+3]='  <br><b style="color:#374151">ปริมาณ:</b> 5-Oct รวม 4 โรง 3,400 ตัน vs 4,181 ตัน (4-Oct, 5 โรง) (&minus;781, &minus;18.7%) &middot; like-for-like 4 โรง 3,748 &rarr; 3,400 (&minus;348, &minus;9.3%) &middot; TN &minus;93 (&minus;8.1%) &middot; TKT &minus;151 (&minus;12.8%) &middot; PM +77 (+10.5%) &middot; MS &minus;181 (&minus;26.3%) &middot; TDC ยังไม่ลงปริมาณ'
L[i+4]='  <br><b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย 3.92 (&minus;0.05 vs 4-Oct) &middot; %ST 23.91% (&minus;0.11 จุด) &middot; CBG 16.39 &middot; verify CBG: TN 3.87&divide;24.70% = 15.67 &middot; TKT 3.99&divide;23.72% = 16.82 &middot; PM 3.81&divide;22.11% = 17.23 &middot; MS 4.05&divide;25.52% = 15.87 (ราคา: TN &minus;0.01 &middot; TKT &minus;0.02 &middot; PM &minus;0.09 &middot; MS &minus;0.08)'
L[i+5]='  <br><span style="color:#374151">TWIC (นิติบุคคลแยก): <b>5-Oct ยังไม่ส่งไฟล์</b> (อีเมลล่าสุด = "on Oct 04, 2026" ได้รับ 5-Oct 09:01 น.) &mdash; เว้นว่างไม่เดา &middot; ล่าสุดที่มี 4-Oct (3.01 / 556 ตัน / %ST 21.18 / CAG 13.41 / Rec 106.00%) &middot; ยังขาดของ 13-Sep, 24-Sep, 27-Sep</span>'
# keep anomaly line (i+6); replace pending line
j=idx('ค้างผลโม่ (',i)
L[j]=f'  <br><b>&#128680; ค้างผลโม่ (6-Oct-2026 {now}): TN {pl("TN")}  &middot; TKT {pl("TKT")}  &middot; PM {pl("PM")}  &middot; MS {pl("MS")}  &middot; TDC {pl("TDC")}</b>'
txt='\n'.join(L)
# table
def row(name,code,price,dot,dcls,dtxt,vol,st,cag,rec,badge,bt,detail):
    return f'''    <tr><td><span class="plant-name">{name}</span><br><span class="plant-code">{code}</span></td>
      <td class="num">{price}</td><td class="num">{dot}</td>
      <td class="num">{vol}</td><td class="num">{st}</td><td class="num">{cag}</td><td class="num">{rec}</td>
      <td><span class="badge {badge}">{bt}</span><span class="status-detail">{detail}</span></td>
    </tr>'''
g=lambda c,cls,t:f'<span class="dot {c}"></span><span class="delta {cls}">{t}</span>'
M='&minus;'
rows=[
 row('อ.เมือง อุดรธานี','TN','3.87',g('green','down',M+'0.01'),0,0,'1,049','24.70','&mdash;','&mdash;','wait','รอผลโม่','ยังไม่มีผลโม่ 5-Oct (%Recovery 100.0% = default) &middot; CBG 3.87&divide;24.70% = 15.67 ✓ &middot; ค้างผลโม่ 1&ndash;5-Oct'),
 row('ท่าคันโท กาฬสินธุ์','TKT','3.99',g('green','down',M+'0.02'),0,0,'1,032','23.72','&mdash;','&mdash;','wait','รอผลโม่','ยังไม่มีผลโม่ 5-Oct (%Recovery 95.0% R1=R2=Total = default) &middot; CBG 3.99&divide;23.72% = 16.82 ✓'),
 row('พิมาย โคราช','PM','3.81',g('green','down',M+'0.09'),0,0,'813','22.11','&mdash;','&mdash;','wait','รอผลโม่','ยังไม่มีผลโม่ 5-Oct (%Recovery 0.0% = ยังไม่มีข้อมูล) &middot; CBG 3.81&divide;22.11% = 17.23 ✓'),
 row('แม่สอด ตาก','MS','4.05',g('green','down',M+'0.08'),0,0,'506','25.52','&mdash;','&mdash;','wait','รอผลโม่','%Recovery 92.0% = placeholder ของไฟล์ (ไม่ใช่ผลโม่จริง) &middot; CBG 4.05&divide;25.52% = 15.87 ✓ &middot; ไม่นับใน CAG รวม'),
 row('บ้านฉาง ระยอง','TDC','&mdash;','<span class="dot grey"></span>','',0,'&mdash;','&mdash;','&mdash;','&mdash;','none','ยังไม่ลงข้อมูล','5-Oct: ปริมาณซื้อว่าง (ราคา/%ST ในไฟล์ = forecast ไม่แสดง) &middot; ค้างผลโม่ 19-Sep, 23-Sep, 2-Oct'),
]
tot='''    <tr class="total-row"><td>รวมโรงงานไทย (5-Oct &mdash; ซื้อ 4 โรง)</td>
      <td class="num">3.92</td><td class="num"><span class="dot green"></span><span class="delta down">&minus;0.05</span></td>
      <td class="num">3,400</td><td class="num">23.91</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="status-detail">ราคา/%ST ถ่วงน้ำหนักทุกโรงที่ซื้อ (รวม MS) &middot; เทียบ 4-Oct (3.97 / 24.02%, 5 โรง) &middot; CBG 16.39 (&minus;0.15) &middot; <b>CAG รวมปิดไม่ได้ (รอผลโม่ TN/TKT/PM) &mdash; ล่าสุดที่ครบ = 30-Sep 16.37 (4 โรง 2,464 ตัน ไม่รวม MS)</b></span></td>
    </tr>'''
tw='''    <tr><td><span class="plant-name">TWIC กัมพูชา</span><br><span class="plant-code">TWIC &middot; นิติบุคคลแยก</span></td>
      <td class="num">&mdash;</td><td class="num"><span class="dot grey"></span></td>
      <td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge none">ยังไม่ลงข้อมูล</span><span class="status-detail">5-Oct: ยังไม่ได้รับไฟล์ (ล่าสุด = 4-Oct: 3.01 / 556 ตัน / CAG 13.41) &middot; ยังขาดของ 13-Sep, 24-Sep, 27-Sep &middot; แยกจากยอดไทย</span></td>
    </tr>'''
a=txt.index('<tbody>')+len('<tbody>'); b=txt.index('</tbody>')
txt=txt[:a]+'\n'+'\n'.join(rows+[tot,tw])+'\n  '+txt[b:]
txt=txt.replace('(5-Sep ถึง 4-Oct-2026)','(6-Sep ถึง 5-Oct-2026)').replace('ช่วง 30 วันนี้ (5-Sep ถึง 4-Oct)','ช่วง 30 วันนี้ (6-Sep ถึง 5-Oct)')
txt=txt.replace('(1&ndash;4-Oct) และ "09_Sep 2026" (5&ndash;30-Sep) (อ่านไฟล์รอบ 5-Oct-2026 09:15 น.)','(1&ndash;5-Oct) และ "09_Sep 2026" (6&ndash;30-Sep) (อ่านไฟล์รอบ 6-Oct-2026 %s น.)'%now)
txt=txt.replace('(ล่าสุด = ของ 4-Oct &middot; ยังขาดของ 13-Sep, 24-Sep, 27-Sep)','(ล่าสุด = ของ 4-Oct; 5-Oct ยังไม่ส่ง &middot; ยังขาดของ 13-Sep, 24-Sep, 27-Sep)')
open('Daily root dashboard - 5 October 2026.html','w',encoding='utf-8').write(txt)
