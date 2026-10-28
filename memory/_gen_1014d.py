import csv,re,json,subprocess
fn='Daily root dashboard - 13 October 2026.html'
t=open(fn,encoding='utf-8').read()
rows=list(csv.DictReader(open('memory/root-price-history.csv',encoding='utf-8')))
R={(r['date'],r['plant']):r for r in rows}
f=lambda d,p,k:(None if R[(d,p)][k]=='' else float(R[(d,p)][k]))
dates=sorted({r['date'] for r in rows})
def arr(p,k):
    return json.dumps([(int(v) if (k=='volume_tons' and v is not None) else v) for v in [f(d,p,k) for d in dates]])
for p in ['PM','MS']:
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
g=['TN','TKT','PM','TDC']
v11=sum(f('2026-10-11',p,'volume_tons') for p in g); cag11=sum(f('2026-10-11',p,'volume_tons')*f('2026-10-11',p,'cag_thb_kg') for p in g)/v11
print(v13,p13,s13,c13,v12,p12,s12,c12,v11,cag11)
vs=f"{v13-v12:+,.0f}, {(v13/v12-1)*100:+.1f}%"
now=subprocess.check_output(['date','+%H:%M'],env={'TZ':'Asia/Bangkok'}).decode().strip()
def sub(old,new):
    global t
    assert t.count(old)>=1,old[:70]
    t=t.replace(old,new)
# header banner/timestamp
t=re.sub(r'อัปเดตเมื่อ: 14-Oct-2026 \d\d:\d\d น\. \(T-1 = 13-Oct\) \(.*?\)</div>',lambda m:f'อัปเดตเมื่อ: 14-Oct-2026 {now} น. (T-1 = 13-Oct) (ไฟล์ Oct แก้ล่าสุด 14-Oct 10:58 น. &middot; ไฟล์ Sep แก้ล่าสุด 5-Oct 16:49 น. &middot; เทียบรอบ 10:04: <b>PM 11-Oct %Recovery ปรับ 107.6% &rarr; 116.0%</b>, ผลโม่ใหม่ PM 12-Oct 116.5% และ MS 12-Oct 93.0%, MS 13-Oct ปรับปริมาณ/ราคา/%ST 660/4.20/28.65% &rarr; 669/4.19/28.68%)</div>',t,count=1,flags=re.S)
# KPI1
sub('MS 660 &middot; TDC 183','MS 669 &middot; TDC 183')
t=re.sub(r'(ปริมาณซื้อโรงงานไทย \(13-Oct &mdash; ลงข้อมูล 4 โรง\)</div><div class="value">)[\d,]+(<span class="unit">.*?เทียบ 4 โรงเดียวกันของ 12-Oct \(1,737 ตัน\) <b>)[^<]*</b>',lambda m:f'{m.group(1)}{v13:,.0f}{m.group(2)}{vs}</b>',t,count=1,flags=re.S)
t=re.sub(r'(ราคาเฉลี่ยถ่วงน้ำหนัก \(13-Oct &middot; 4 โรงที่ลงข้อมูล\)</div><div class="value">)[^<]*<span class="unit">&#3647;/กก\. \([\d.]+\) &middot; <b style="color:#b91c1c">[^<]*</b>',lambda m:f'{m.group(1)}{p13:.2f}<span class="unit">&#3647;/กก. ({p13:.4f}) &middot; <b style="color:#b91c1c">{p13-p12:+.2f} vs 4 โรงเดียวกัน 12-Oct ({p12:.4f})</b>',t,count=1,flags=re.S)
t=re.sub(r'(%Starch เฉลี่ยถ่วงน้ำหนัก \(13-Oct &middot; 4 โรงที่ลงข้อมูล\)</div><div class="value">)[^<]*<span class="unit">% &middot; <b>[^<]*</b> vs 4 โรงเดียวกัน 12-Oct \(24\.47\) &rarr; CBG รวม <b>[^<]*</b>',lambda m:f'{m.group(1)}{s13:.2f}<span class="unit">% &middot; <b>{s13-s12:+.2f} จุด</b> vs 4 โรงเดียวกัน 12-Oct ({s12:.2f}) &rarr; CBG รวม <b>{c13:.2f}</b>',t,count=1,flags=re.S)
# KPI4 : 11-Oct CAG group revised
sub('15.93<span class="unit">&#3647;/กก. (15.935)',f'{cag11:.2f}<span class="unit">&#3647;/กก. ({cag11:.3f})')
sub('ล่าสุดที่ครบ = 11-Oct: 15.93, 4 โรง 1,947 ตัน',f'ล่าสุดที่ครบ = 11-Oct: {cag11:.2f} (ปรับจาก 15.93 เพราะ PM 11-Oct %Recovery ปรับเป็น 116.0%), 4 โรง {v11:,.0f} ตัน')
sub('ล่าสุดที่ครบ = 11-Oct 15.93 (4 โรง 1,947 ตัน)',f'ล่าสุดที่ครบ = 11-Oct {cag11:.2f} (4 โรง {v11:,.0f} ตัน)')
sub('12-Oct รอผลโม่ TN, PM, TDC &middot; 13-Oct รอผลโม่ TKT, PM, TDC','12-Oct รอผลโม่ TN, TDC (PM ปิดแล้ว 116.5%) &middot; 13-Oct รอผลโม่ TKT, PM, TDC')
# caveat
sub('MS 4.20 / 660 ตัน / 28.65%','MS 4.19 / 669 ตัน / 28.68%')
sub('<b>TDC ลงปริมาณ 12-Oct','<b style="color:#b45309">PM 11-Oct %Recovery ปรับย้อนหลัง 107.6% &rarr; 116.0% (CAG 14.58 &rarr; 13.52) &middot; ผลโม่ใหม่ PM 12-Oct 116.5% (CAG 13.52) และ MS 12-Oct 93.0% (CAG 15.99) &middot; MS 13-Oct ปรับ 660/4.20/28.65% &rarr; 669/4.19/28.68%</b> &middot; <b>TDC ลงปริมาณ 12-Oct')
sub('TN, PM, MS, TDC 12-Oct ยังรอผลโม่','TN, TDC 12-Oct ยังรอผลโม่')
sub('<b style="color:#b45309">MS 390 &rarr; 660 (+270, +69.2%)</b>','<b style="color:#b45309">MS 390 &rarr; 669 (+279, +71.5%)</b>')
sub('<b style="color:#b91c1c">MS +0.12 (4.08 &rarr; 4.20)</b>','<b style="color:#b91c1c">MS +0.11 (4.08 &rarr; 4.19)</b>')
sub('MS 4.20&divide;28.65% = 14.66 &middot; TDC','MS 4.19&divide;28.68% = 14.61 &middot; TDC')
sub('<b style="color:#b45309">&#128680; ค่าผิดปกติที่ยังไม่ถูกแก้ (ในช่วง 30 วัน, %Recovery &lt;90% หรือ &gt;110%): ','<b style="color:#b45309">&#128680; ค่าผิดปกติที่ยังไม่ถูกแก้ (ในช่วง 30 วัน, %Recovery &lt;90% หรือ &gt;110%): PM 11-Oct 116.0% &middot; PM 12-Oct 116.5% &middot; ')
sub('PM 27-Sep, 12-Oct, 13-Oct &middot; MS 15-Sep, 20-Sep, 21-Sep, 25-Sep, 28-Sep, 29-Sep, 12-Oct, 13-Oct','PM 27-Sep, 13-Oct &middot; MS 15-Sep, 20-Sep, 21-Sep, 25-Sep, 28-Sep, 29-Sep, 13-Oct')
# PM row
sub('ผลโม่ล่าสุด 11-Oct 107.6% (CAG 14.58) &middot; ค้างผลโม่ 27-Sep, 12-Oct, 13-Oct','ผลโม่ล่าสุด 12-Oct 116.5% (CAG 13.52 &middot; สูงผิดปกติ) &middot; 11-Oct ปรับย้อนหลังเป็น 116.0% (CAG 13.52) &middot; ค้างผลโม่ 27-Sep, 13-Oct')
# MS row
sub('<td class="num">4.20</td><td class="num"><span class="dot red"></span><span class="delta up">+0.12</span></td>\n      <td class="num">660</td><td class="num">28.65</td>','<td class="num">4.19</td><td class="num"><span class="dot red"></span><span class="delta up">+0.11</span></td>\n      <td class="num">669</td><td class="num">28.68</td>')
sub('CBG 4.20&divide;28.65% = 14.66 ✓ &middot; ไม่นับใน CAG รวม &middot; ปริมาณ +69.2% จาก 12-Oct (390) &middot; ผลโม่ล่าสุด 11-Oct 91.7% (CAG 16.49)','CBG 4.19&divide;28.68% = 14.61 ✓ &middot; ไม่นับใน CAG รวม &middot; ปริมาณ +71.5% จาก 12-Oct (390) &middot; ผลโม่ล่าสุด 12-Oct 93.0% (CAG 15.99)')
# total row
a=t.find('    <tr class="total-row">'); b=t.find('    <tr><td><span class="plant-name">TWIC')
tr=t[a:b]
tr=re.sub(r'<td class="num">3\.94</td>',f'<td class="num">{p13:.2f}</td>',tr,1)
tr=re.sub(r'<span class="delta up">\+0\.06</span>',f'<span class="delta up">{p13-p12:+.2f}</span>',tr,1)
tr=tr.replace('2,225',f'{v13:,.0f}').replace('25.48',f'{s13:.2f}').replace('CBG 15.45',f'CBG {c13:.2f}')
t=t[:a]+tr+t[b:]
open(fn,'w',encoding='utf-8').write(t)
