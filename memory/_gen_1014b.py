import csv,re,json,datetime,subprocess
M='memory/'
fn='Daily root dashboard - 13 October 2026.html'
t=open(fn,encoding='utf-8').read()
rows=list(csv.DictReader(open(M+'root-price-history.csv',encoding='utf-8')))
R={(r['date'],r['plant']):r for r in rows}
f=lambda d,p,k:(None if R[(d,p)][k]=='' else float(R[(d,p)][k]))
dates=sorted({r['date'] for r in rows})
lab=lambda d:(lambda x:f"{x.day}-{x.strftime('%b')}")(datetime.date.fromisoformat(d))
t=re.sub(r'const dates = \[[^\]]*\];','const dates = '+json.dumps([lab(d) for d in dates])+';',t,count=1)
def arr(p,k):
    out=[f(d,p,k) for d in dates]
    return json.dumps([(int(v) if (k=='volume_tons' and v is not None) else v) for v in out])
for p in ['TN','TKT','PM','MS','TDC','TWIC']:
    i=t.find(f'  {p}: {{ label: "{p}"'); j=t.find('\n  },',i); blk=t[i:j]
    for name,k in (('price','price_thb_kg'),('volume','volume_tons'),('starch','starch_pct'),('cag','cag_thb_kg'),('recov','recovery_pct')):
        blk=re.sub(r'(\n    %s:\s+)\[[^\]]*\]'%name,lambda m:m.group(1)+arr(p,k),blk,count=1)
    t=t[:i]+blk+t[j:]
# ---- stats
def agg(d,ps):
    v=sum(f(d,p,'volume_tons') for p in ps); pr=sum(f(d,p,'volume_tons')*f(d,p,'price_thb_kg') for p in ps)/v
    st=sum(f(d,p,'volume_tons')*f(d,p,'starch_pct') for p in ps)/v
    return v,pr,st,pr/(st/100)
ps=['TKT','PM','MS']
v13,p13,s13,c13=agg('2026-10-13',ps); v12,p12,s12,c12=agg('2026-10-12',ps)
print('13',v13,p13,s13,c13,'12',v12,p12,s12,c12)
cp=['TN','TKT','PM','TDC']
for d in ['2026-10-09','2026-10-10','2026-10-11','2026-10-12','2026-10-13']:
    ok=all(f(d,p,'cag_thb_kg') is not None for p in cp if (f(d,p,'volume_tons') or 0)>0)
    print(d,ok)
cv=sum(f('2026-10-11',p,'volume_tons') for p in cp); cag=sum(f('2026-10-11',p,'volume_tons')*f('2026-10-11',p,'cag_thb_kg') for p in cp)/cv
print('CAG11',cag,cv)
now=subprocess.check_output(['date','+%H:%M'],env={'TZ':'Asia/Bangkok'}).decode().strip()
dv=v13-v12; 
vs=lambda a,b:f"{a-b:+,.0f}, {(a/b-1)*100:+.1f}%"
upd=f'''<div class="updated">
    ข้อมูลล่าสุด (เมื่อวาน): <b>13-Oct-2026</b> (อังคาร)<br>
    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; 13-Oct: ลงข้อมูล TKT + PM + MS (TN, TDC ยังไม่ลงปริมาณ &mdash; ราคา/%ST ในไฟล์เป็น forecast &rarr; เว้นว่าง) &middot; ผลโม่ 13-Oct ยังไม่เข้าเลย (TKT 95.0% / MS 90.0% = default/placeholder / PM 0.0%) &middot; TWIC ส่ง 13-Oct มาแล้ว (70 ตัน, ยังไม่มีผลโม่)</b></span><br>
    อัปเดตเมื่อ: 14-Oct-2026 {now} น. (T-1 = 13-Oct) (ไฟล์ Oct แก้ล่าสุด 14-Oct 08:41 น. &middot; ไฟล์ Sep แก้ล่าสุด 5-Oct 16:49 น. &middot; เทียบรอบ 08:06: PM 13-Oct เพิ่งลงปริมาณ 511 ตัน &middot; TDC 10-Oct, 11-Oct ผลโม่เข้าแล้ว &middot; TWIC เพิ่ม 13-Oct)</div>'''
t=re.sub(r'<div class="updated">.*?</div>(?=\s*</div>\s*\n\s*<div class="kpi-row">)',lambda m:upd,t,count=1,flags=re.S)
kpi=f'''<div class="kpi-row">
  <div class="kpi"><div class="label">ปริมาณซื้อโรงงานไทย (13-Oct &mdash; ลงข้อมูล 3 โรง)</div><div class="value">{v13:,.0f}<span class="unit">ตัน &middot; <b>TKT 871 &middot; PM 511 &middot; MS 660</b> &middot; TN, TDC ยังไม่ลง &middot; เทียบ 3 โรงเดียวกันของ 12-Oct ({v12:,.0f} ตัน) <b>{vs(v13,v12)}</b> (ไม่เทียบกับ 2,199 ตันของ 4 โรง 12-Oct)</span></div></div>
  <div class="kpi"><div class="label">ราคาเฉลี่ยถ่วงน้ำหนัก (13-Oct &middot; 3 โรงที่ลงข้อมูล)</div><div class="value">{p13:.2f}<span class="unit">&#3647;/กก. ({p13:.4f}) &middot; <b style="color:#b91c1c">{p13-p12:+.2f} vs 3 โรงเดียวกัน 12-Oct ({p12:.4f})</b> &middot; เทียบข้ามองค์ประกอบโรงไม่ได้</span></div></div>
  <div class="kpi"><div class="label">%Starch เฉลี่ยถ่วงน้ำหนัก (13-Oct &middot; 3 โรงที่ลงข้อมูล)</div><div class="value">{s13:.2f}<span class="unit">% &middot; <b>{s13-s12:+.2f} จุด</b> vs 3 โรงเดียวกัน 12-Oct ({s12:.2f}) &rarr; CBG รวม <b>{c13:.2f}</b></span></div></div>
  <div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = 11-Oct &middot; ไม่รวม MS)</div><div class="value">{cag:.2f}<span class="unit">&#3647;/กก. ({cag:.3f}) &middot; <b>4 โรง (TN, TKT, PM, TDC) &middot; {cv:,.0f} ตัน</b> &middot; <b style="color:#b45309">12-Oct รอผลโม่ TN, PM &middot; 13-Oct รอผลโม่ TKT, PM + ยังไม่ลง TN, TDC</b></span></div></div>
</div>'''
t=re.sub(r'<div class="kpi-row">.*?\n</div>(?=\s*\n\s*<div class="caveat">)',lambda m:kpi,t,count=1,flags=re.S)
cav=f'''<div class="caveat">
  <b style="color:#b45309">&#9888; 13-Oct: ลงข้อมูล TKT + PM + MS &mdash; ยังไม่มีผลโม่ใหม่ (TKT 95.0% ทั้ง recTotal/R1/R2 = default &rarr; เว้นว่าง &middot; MS 90.0% = placeholder &rarr; เว้นว่าง &middot; PM 0.0% = ไม่มีข้อมูล &rarr; เว้นว่าง) &middot; CAG รวม 13-Oct ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = 11-Oct: {cag:.2f}, 4 โรง {cv:,.0f} ตัน</b> &mdash; TKT 3.91 / 871 ตัน / 24.14% &middot; PM 3.72 / 511 ตัน / 24.75% &middot; MS 4.20 / 660 ตัน / 28.65% &middot; TN (ไฟล์ 3.84 / 24.60%), TDC (4.17 / 24.20%) ไม่มีปริมาณ = forecast &rarr; เว้นว่าง
  <br><b style="color:#374151">ผลโม่ใหม่/Backfill:</b> <b>TDC 10-Oct 99.8% (CAG 16.10) และ 11-Oct 97.8% (CAG 16.52) เข้าแล้ว</b> &rarr; CAG รวม 10-Oct และ 11-Oct ครบ 4 โรง &middot; ตรวจย้อนหลัง 1&ndash;12-Oct จุดอื่น diff = 0 &middot; TN, PM, MS 12-Oct ยังรอผลโม่
  <br><b style="color:#374151">ปริมาณ:</b> 13-Oct ลง 3 โรง รวม {v13:,.0f} ตัน (เทียบ 3 โรงเดียวกัน 12-Oct: {v12:,.0f} &rarr; {v13:,.0f}, {vs(v13,v12)}) &mdash; TKT 755 &rarr; 871 (+116, +15.4%) &middot; PM 367 &rarr; 511 (+144, +39.2%) &middot; <b style="color:#b45309">MS 390 &rarr; 660 (+270, +69.2%)</b> &middot; TN, TDC ยังไม่ลง (12-Oct: TN 687, TDC ไม่ลง)
  <br><b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย 3 โรง {p13:.2f} ({p13-p12:+.2f} vs 3 โรงเดียวกัน 12-Oct) &middot; %ST {s13:.2f}% ({s13-s12:+.2f} จุด) &middot; CBG {c13:.2f} &middot; <b style="color:#b91c1c">TKT +0.02 (3.89 &rarr; 3.91)</b> &middot; <b style="color:#b91c1c">PM +0.03 (3.69 &rarr; 3.72)</b> &middot; <b style="color:#b91c1c">MS +0.12 (4.08 &rarr; 4.20)</b> &middot; verify CBG: TKT 3.91&divide;24.14% = 16.20 &middot; PM 3.72&divide;24.75% = 15.03 &middot; MS 4.20&divide;28.65% = 14.66
  <br><span style="color:#374151">TWIC (นิติบุคคลแยก): <b>13-Oct ส่งแล้ว</b> (อีเมล "on Oct 13, 2026" ได้รับ 14-Oct 08:46 น.) &mdash; 70 ตัน / ราคา 2.62 / %ST 19.63% / CBG 13.33 &middot; <b>ยังไม่มีผลโม่ (%Recovery 0.0% &rarr; เว้นว่าง)</b> &middot; ไฟล์ไม่มีแถว 9&ndash;12-Oct (อีเมล 8-Oct แจ้งหยุดเก็บเกี่ยว/ลานรับซื้อพักซื้อชั่วคราว) &rarr; เว้นว่าง ไม่เดา &middot; ยังขาดของ 24-Sep, 27-Sep</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติที่ยังไม่ถูกแก้ (ในช่วง 30 วัน, %Recovery &lt;90% หรือ &gt;110%): TN 22-Sep 89.2% &middot; TN 29-Sep 86.6% &middot; TN 5-Oct 86.0% &middot; TKT 19-Sep 129.5% &middot; TKT 30-Sep 127.5% &middot; TKT 2-Oct 85.3% &middot; PM 14-Sep 65.3% &middot; PM 20-Sep 82.3% &middot; MS 14-Sep 42.1% &middot; MS 16-Sep 78.0% &middot; MS 22-Sep 84.3% &middot; MS 26-Sep 81.2% &middot; MS 30-Sep 71.3% &middot; MS 3-Oct 88.8% &middot; MS 4-Oct 89.6% &middot; MS 5-Oct 89.6% &middot; MS 6-Oct 80.1% &middot; MS 7-Oct 82.3% &middot; MS 8-Oct 89.8%</b>
  <br><b>&#128680; ค้างผลโม่ (14-Oct-2026): TN 27-Sep, 28-Sep, 12-Oct &middot; TKT 20-Sep, 13-Oct &middot; PM 27-Sep, 12-Oct, 13-Oct &middot; MS 15-Sep, 20-Sep, 21-Sep, 25-Sep, 28-Sep, 29-Sep, 12-Oct, 13-Oct &middot; TDC 19-Sep, 23-Sep, 2-Oct &middot; TWIC 13-Oct</b>
</div>'''
t=re.sub(r'<div class="caveat">\s*<b style="color:#b45309">&#9888; 13-Oct.*?\n</div>(?=\s*\n<table>)',lambda m:cav,t,count=1,flags=re.S)
pm_new=f'''    <tr><td><span class="plant-name">พิมาย โคราช</span><br><span class="plant-code">PM</span></td>
      <td class="num">3.72</td><td class="num"><span class="dot red"></span><span class="delta up">+0.03</span></td>
      <td class="num">511</td><td class="num">24.75</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge wait">รอผลโม่</span><span class="status-detail">ยังไม่มีผลโม่ 13-Oct (%Recovery 0.0% = ไม่มีข้อมูล &rarr; เว้นว่าง) &middot; CBG 3.72&divide;24.75% = 15.03 ✓ &middot; ปริมาณ +39.2% จาก 12-Oct (367) &middot; ผลโม่ล่าสุด 11-Oct 107.6% (CAG 14.58) &middot; ค้างผลโม่ 27-Sep, 12-Oct, 13-Oct</span></td>
    </tr>
'''
a=t.find('    <tr><td><span class="plant-name">พิมาย โคราช</span>'); b=t.find('    <tr><td><span class="plant-name">แม่สอด ตาก</span>')
t=t[:a]+pm_new+t[b:]
t=t.replace('ผลโม่ล่าสุด 8-Oct 96.1% (CAG 16.63) &middot; ค้างผลโม่ 19-Sep, 23-Sep, 2-Oct, 10-Oct, 11-Oct','ผลโม่ล่าสุด 11-Oct 97.8% (CAG 16.52) &middot; ค้างผลโม่ 19-Sep, 23-Sep, 2-Oct')
tot=f'''    <tr class="total-row"><td>รวมโรงงานไทย (13-Oct &mdash; ลงข้อมูล 3 โรง)</td>
      <td class="num">{p13:.2f}</td><td class="num"><span class="dot red"></span><span class="delta up">{p13-p12:+.2f}</span></td>
      <td class="num">{v13:,.0f}</td><td class="num">{s13:.2f}</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="status-detail">ราคา/%ST ถ่วงน้ำหนักทุกโรงที่ลงข้อมูล (TKT, PM, MS) &middot; เทียบ 3 โรงเดียวกันของ 12-Oct ({p12:.2f} / {s12:.2f}%) &middot; CBG {c13:.2f} &middot; <b>CAG รวม 13-Oct ปิดไม่ได้ (รอผลโม่ TKT, PM และ TN, TDC ยังไม่ลง) &mdash; ล่าสุดที่ครบ = 11-Oct {cag:.2f} (4 โรง {cv:,.0f} ตัน)</b></span></td>
    </tr>
'''
a=t.find('    <tr class="total-row">'); b=t.find('    <tr><td><span class="plant-name">TWIC')
t=t[:a]+tot+t[b:]
tw='''    <tr><td><span class="plant-name">TWIC กัมพูชา</span><br><span class="plant-code">TWIC &middot; นิติบุคคลแยก</span></td>
      <td class="num">2.62</td><td class="num"><span class="dot grey"></span><span class="delta flat">&mdash;</span></td>
      <td class="num">70</td><td class="num">19.63</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge wait">รอผลโม่</span><span class="status-detail">13-Oct ส่งแล้ว (ยังไม่มีผลโม่ &rarr; %Recovery 0.0% เว้นว่าง) &middot; CBG 2.62&divide;19.63% = 13.33 ✓ &middot; ไฟล์ไม่มีแถว 9&ndash;12-Oct (ไม่เทียบวันก่อน) &middot; 8-Oct ล่าสุดที่มีผลโม่: 2.75 / 138 ตัน / CAG 12.81 &middot; ยังขาดของ 24-Sep, 27-Sep &middot; แยกจากยอดไทย</span></td>
    </tr>
'''
a=t.find('    <tr><td><span class="plant-name">TWIC'); b=t.find('</table>')
t=t[:a]+tw+t[b:]
t=re.sub(r'TWIC: อีเมล put\.p@thaiwah\.com \(ล่าสุด.*?ยังขาดของ 24-Sep, 27-Sep\)','TWIC: อีเมล put.p@thaiwah.com (ล่าสุด = ของ 13-Oct ได้รับ 14-Oct 08:46 น. &middot; ไฟล์ไม่มี 9&ndash;12-Oct &middot; ยังขาดของ 24-Sep, 27-Sep)',t,count=1,flags=re.S)
open(fn,'w',encoding='utf-8').write(t); print(len(t))
