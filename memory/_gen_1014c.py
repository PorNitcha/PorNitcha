import csv,re,json,datetime,subprocess
fn='Daily root dashboard - 13 October 2026.html'
t=open(fn,encoding='utf-8').read()
rows=list(csv.DictReader(open('memory/root-price-history.csv',encoding='utf-8')))
R={(r['date'],r['plant']):r for r in rows}
f=lambda d,p,k:(None if R[(d,p)][k]=='' else float(R[(d,p)][k]))
dates=sorted({r['date'] for r in rows})
def arr(p,k):
    return json.dumps([(int(v) if (k=='volume_tons' and v is not None) else v) for v in [f(d,p,k) for d in dates]])
for p in ['TDC']:
    i=t.find(f'  {p}: {{ label: "{p}"'); j=t.find('\n  },',i); blk=t[i:j]
    for name,k in (('price','price_thb_kg'),('volume','volume_tons'),('starch','starch_pct'),('cag','cag_thb_kg'),('recov','recovery_pct')):
        blk=re.sub(r'(\n    %s:\s+)\[[^\]]*\]'%name,lambda m:m.group(1)+arr(p,k),blk,count=1)
    t=t[:i]+blk+t[j:]
def agg(d,ps):
    v=sum(f(d,p,'volume_tons') for p in ps); pr=sum(f(d,p,'volume_tons')*f(d,p,'price_thb_kg') for p in ps)/v
    st=sum(f(d,p,'volume_tons')*f(d,p,'starch_pct') for p in ps)/v
    return v,pr,st,pr/(st/100)
ps=['TKT','PM','MS','TDC']
v13,p13,s13,c13=agg('2026-10-13',ps); v12,p12,s12,c12=agg('2026-10-12',ps)
print(v13,p13,s13,c13,v12,p12,s12,c12)
vs=f"{v13-v12:+,.0f}, {(v13/v12-1)*100:+.1f}%"
now=subprocess.check_output(['date','+%H:%M'],env={'TZ':'Asia/Bangkok'}).decode().strip()
def sub(old,new,cnt=1):
    global t
    assert t.count(old)>=1,old[:60]
    t=t.replace(old,new)
# banner
sub('ลงข้อมูล TKT + PM + MS (TN, TDC ยังไม่ลงปริมาณ','ลงข้อมูล TKT + PM + MS + TDC (TN ยังไม่ลงปริมาณ')
sub('(TKT 95.0% / MS 90.0% = default/placeholder / PM 0.0%)','(TKT 95.0% / MS 90.0% = default/placeholder / PM 0.0% / TDC ว่าง)')
t=re.sub(r'อัปเดตเมื่อ: 14-Oct-2026 \d\d:\d\d น\. \(T-1 = 13-Oct\) \(.*?\)</div>',lambda m:f'อัปเดตเมื่อ: 14-Oct-2026 {now} น. (T-1 = 13-Oct) (ไฟล์ Oct แก้ล่าสุด 14-Oct 09:55 น. &middot; ไฟล์ Sep แก้ล่าสุด 5-Oct 16:49 น. &middot; เทียบรอบ 09:05: TDC ลงปริมาณ 12-Oct (225 ตัน) และ 13-Oct (183 ตัน) เพิ่ม &middot; ข้อมูลอื่น 1&ndash;13-Oct diff = 0)</div>',t,count=1,flags=re.S)
# KPI
t=re.sub(r'ปริมาณซื้อโรงงานไทย \(13-Oct &mdash; ลงข้อมูล 3 โรง\)</div><div class="value">[\d,]+<span class="unit">.*?</span></div></div>',lambda m:f'ปริมาณซื้อโรงงานไทย (13-Oct &mdash; ลงข้อมูล 4 โรง)</div><div class="value">{v13:,.0f}<span class="unit">ตัน &middot; <b>TKT 871 &middot; PM 511 &middot; MS 660 &middot; TDC 183</b> &middot; TN ยังไม่ลง &middot; เทียบ 4 โรงเดียวกันของ 12-Oct ({v12:,.0f} ตัน) <b>{vs}</b> (ไม่เทียบกับ 2,199 ตันของ 4 โรงอื่น 12-Oct)</span></div></div>',t,count=1,flags=re.S)
t=re.sub(r'(ราคาเฉลี่ยถ่วงน้ำหนัก \(13-Oct &middot; )3 โรงที่ลงข้อมูล\)</div><div class="value">.*?</span></div></div>',lambda m:f'{m.group(1)}4 โรงที่ลงข้อมูล)</div><div class="value">{p13:.2f}<span class="unit">&#3647;/กก. ({p13:.4f}) &middot; <b style="color:#b91c1c">{p13-p12:+.2f} vs 4 โรงเดียวกัน 12-Oct ({p12:.4f})</b> &middot; เทียบข้ามองค์ประกอบโรงไม่ได้</span></div></div>',t,count=1,flags=re.S)
t=re.sub(r'(%Starch เฉลี่ยถ่วงน้ำหนัก \(13-Oct &middot; )3 โรงที่ลงข้อมูล\)</div><div class="value">.*?</span></div></div>',lambda m:f'{m.group(1)}4 โรงที่ลงข้อมูล)</div><div class="value">{s13:.2f}<span class="unit">% &middot; <b>{s13-s12:+.2f} จุด</b> vs 4 โรงเดียวกัน 12-Oct ({s12:.2f}) &rarr; CBG รวม <b>{c13:.2f}</b></span></div></div>',t,count=1,flags=re.S)
sub('13-Oct รอผลโม่ TKT, PM + ยังไม่ลง TN, TDC</b></span></div></div>','13-Oct รอผลโม่ TKT, PM, TDC + ยังไม่ลง TN</b></span></div></div>')
sub('12-Oct รอผลโม่ TN, PM &middot; 13-Oct รอผลโม่ TKT','12-Oct รอผลโม่ TN, PM, TDC &middot; 13-Oct รอผลโม่ TKT')
# caveat
sub('<b style="color:#b45309">&#9888; 13-Oct: ลงข้อมูล TKT + PM + MS &mdash; ยังไม่มีผลโม่ใหม่','<b style="color:#b45309">&#9888; 13-Oct: ลงข้อมูล TKT + PM + MS + TDC &mdash; ยังไม่มีผลโม่ใหม่')
sub('PM 0.0% = ไม่มีข้อมูล &rarr; เว้นว่าง) &middot; CAG รวม 13-Oct','PM 0.0% = ไม่มีข้อมูล &rarr; เว้นว่าง &middot; TDC ว่าง) &middot; CAG รวม 13-Oct')
sub('TN (ไฟล์ 3.84 / 24.60%), TDC (4.17 / 24.20%) ไม่มีปริมาณ = forecast','TDC 3.72 / 183 ตัน / 22.47% &middot; TN (ไฟล์ 3.84 / 24.60%) ไม่มีปริมาณ = forecast')
sub('ตรวจย้อนหลัง 1&ndash;12-Oct จุดอื่น diff = 0 &middot; TN, PM, MS 12-Oct ยังรอผลโม่','<b>TDC ลงปริมาณ 12-Oct (3.76 / 225 ตัน / 23.58%) และ 13-Oct (3.72 / 183 ตัน / 22.47%) แล้ว &mdash; ผลโม่ยังไม่เข้า (ว่าง)</b> &middot; ตรวจย้อนหลัง 1&ndash;13-Oct จุดอื่น diff = 0 &middot; TN, PM, MS, TDC 12-Oct ยังรอผลโม่')
t=re.sub(r'<b style="color:#374151">ปริมาณ:</b> 13-Oct ลง 3 โรง.*?\n',lambda m:f'<b style="color:#374151">ปริมาณ:</b> 13-Oct ลง 4 โรง รวม {v13:,.0f} ตัน (เทียบ 4 โรงเดียวกัน 12-Oct: {v12:,.0f} &rarr; {v13:,.0f}, {vs}) &mdash; TKT 755 &rarr; 871 (+116, +15.4%) &middot; PM 367 &rarr; 511 (+144, +39.2%) &middot; <b style="color:#b45309">MS 390 &rarr; 660 (+270, +69.2%)</b> &middot; TDC 225 &rarr; 183 (-42, -18.7%) &middot; TN ยังไม่ลง (12-Oct: 687)\n',t,count=1,flags=re.S)
t=re.sub(r'<b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย 3 โรง.*?\n',lambda m:f'<b style="color:#374151">ราคา/คุณภาพ:</b> ราคาเฉลี่ย 4 โรง {p13:.2f} ({p13-p12:+.2f} vs 4 โรงเดียวกัน 12-Oct) &middot; %ST {s13:.2f}% ({s13-s12:+.2f} จุด) &middot; CBG {c13:.2f} &middot; <b style="color:#b91c1c">TKT +0.02 (3.89 &rarr; 3.91)</b> &middot; <b style="color:#b91c1c">PM +0.03 (3.69 &rarr; 3.72)</b> &middot; <b style="color:#b91c1c">MS +0.12 (4.08 &rarr; 4.20)</b> &middot; <b style="color:#15803d">TDC -0.04 (3.76 &rarr; 3.72)</b> &middot; verify CBG: TKT 3.91&divide;24.14% = 16.20 &middot; PM 3.72&divide;24.75% = 15.03 &middot; MS 4.20&divide;28.65% = 14.66 &middot; TDC 3.72&divide;22.47% = 16.56\n',t,count=1,flags=re.S)
sub('TDC 19-Sep, 23-Sep, 2-Oct &middot; TWIC 13-Oct','TDC 19-Sep, 23-Sep, 2-Oct, 12-Oct, 13-Oct &middot; TWIC 13-Oct')
sub('MS 15-Sep, 20-Sep, 21-Sep, 25-Sep, 28-Sep, 29-Sep, 12-Oct, 13-Oct &middot; TDC','MS 15-Sep, 20-Sep, 21-Sep, 25-Sep, 28-Sep, 29-Sep, 12-Oct, 13-Oct &middot; TDC')
# TDC row
a=t.find('    <tr><td><span class="plant-name">บ้านฉาง ระยอง</span>'); b=t.find('    <tr class="total-row">')
tdc='''    <tr><td><span class="plant-name">บ้านฉาง ระยอง</span><br><span class="plant-code">TDC</span></td>
      <td class="num">3.72</td><td class="num"><span class="dot green"></span><span class="delta down">-0.04</span></td>
      <td class="num">183</td><td class="num">22.47</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge wait">รอผลโม่</span><span class="status-detail">ยังไม่มีผลโม่ 13-Oct (%Recovery ว่าง) &middot; CBG 3.72&divide;22.47% = 16.56 ✓ &middot; ปริมาณ -18.7% จาก 12-Oct (225) &middot; ผลโม่ล่าสุด 11-Oct 97.8% (CAG 16.52) &middot; ค้างผลโม่ 19-Sep, 23-Sep, 2-Oct, 12-Oct, 13-Oct</span></td>
    </tr>
'''
t=t[:a]+tdc+t[b:]
# total row
a=t.find('    <tr class="total-row">'); b=t.find('    <tr><td><span class="plant-name">TWIC')
tot=f'''    <tr class="total-row"><td>รวมโรงงานไทย (13-Oct &mdash; ลงข้อมูล 4 โรง)</td>
      <td class="num">{p13:.2f}</td><td class="num"><span class="dot red"></span><span class="delta up">{p13-p12:+.2f}</span></td>
      <td class="num">{v13:,.0f}</td><td class="num">{s13:.2f}</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="status-detail">ราคา/%ST ถ่วงน้ำหนักทุกโรงที่ลงข้อมูล (TKT, PM, MS, TDC) &middot; เทียบ 4 โรงเดียวกันของ 12-Oct ({p12:.2f} / {s12:.2f}%) &middot; CBG {c13:.2f} &middot; <b>CAG รวม 13-Oct ปิดไม่ได้ (รอผลโม่ TKT, PM, TDC และ TN ยังไม่ลง) &mdash; ล่าสุดที่ครบ = 11-Oct 15.93 (4 โรง 1,947 ตัน)</b></span></td>
    </tr>
'''
t=t[:a]+tot+t[b:]
open(fn,'w',encoding='utf-8').write(t)
