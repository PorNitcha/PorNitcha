import os,re,json
m=os.path.expanduser('~/mnt/lovely/memory/')
NEW=json.loads('''{"16TN":["312","4.00","25.00","100.0","16.00"],"16TKT":["430","4.14","25.70","100.0","16.11","102.0","96.6"],"16PM":["453","3.95","23.51","100.0","16.80"],"16MS":["235","4.33","29.28","103.3","14.32"],"16TDC":["278","4.01","24.54","","0.00"],"12TN":["309","4.03","25.83","100.0","15.60"],"13TN":["280","3.99","25.50","100.0","15.65"],"14TN":["158","4.04","26.21","100.0","15.41"],"15TN":["257","4.03","26.46","100.0","15.23"]}''')
s=open(m+'_gen_1117r11.py',encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a)
    s=s.replace(a,b)
def cut(a,b,new):
    global s
    assert s.count(a)==1 and s.count(b)>=1,(s.count(a),s.count(b),a)
    i=s.find(a); j=s.find(b,i); assert j>i
    s=s[:i]+new+s[j:]
rep("BK='1117r11'; D='16-Nov'; PD='15-Nov'; NOW='17-Nov-2026 18:4x น.'; DOW='จันทร์'","BK='1118r1'; D='17-Nov'; PD='16-Nov'; NOW='18-Nov-2026 08:1x น.'; DOW='อังคาร'")
rep("old=base+'Daily root dashboard - 15 November 2026.html'","old=base+'Daily root dashboard - 16 November 2026.html'")
rep("new=base+'Daily root dashboard - 16 November 2026.html'","new=base+'Daily root dashboard - 17 November 2026.html'")
rep("shutil.copy(new, mem+","shutil.copy(old, mem+")
rep("assert len(rows)==180 and key[('2026-11-16','TN')]['price_thb_kg']=='4' and key[('2026-11-16','TKT')]['recovery_pct']=='' and key[('2026-11-16','MS')]['recovery_pct']=='103.3'","assert len(rows)==180 and ('2026-11-17','TN') not in key and key[('2026-11-16','TWIC')]['price_thb_kg']=='' and key[('2026-11-16','TKT')]['recovery_pct']=='100'")
cut("NEWROWS=[","dates=sorted({k[0] for k in key})[-30:]","""NEWROWS=[('2026-11-17','TN',3.96,293,25.12,None,None),('2026-11-17','TKT',4.10,285,25.11,None,None),('2026-11-17','PM',4.02,664,24.63,None,None),('2026-11-17','MS',4.35,269,30.66,None,None),('2026-11-17','TDC',None,None,None,None,None),('2026-11-17','TWIC',None,None,None,None,None),('2026-11-16','TWIC',3.03,406,21.64,13.85,101.01)]
for dt,p,pr,v,st,cg,rc in NEWROWS:
    key[(dt,p)]=dict(zip(hdr,[dt,p,g(pr),g(v),g(st),g(cg),g(rc)]))
""")
rep("assert dates[0]=='2026-10-18' and dates[-1]=='2026-11-16'","assert dates[0]=='2026-10-19' and dates[-1]=='2026-11-17'")
rep("assert b3==thai and not noentry and not nobuy and common==['TN','TKT','MS','TDC'], (b3,noentry,nobuy,common)","assert b3==['TN','TKT','PM','MS'] and noentry==['TDC'] and not nobuy and common==['TN','TKT','PM','MS'], (b3,noentry,nobuy,common)")
cut("EXTRA={","def trow(p):","""EXTRA={'TN':' &middot; <b style="color:#b45309">TN ค้างผลโม่ต่อเนื่องตั้งแต่ 12-Nov (6 วัน)</b>',
       'TKT':' &middot; ปริมาณ 430 &rarr; 285 ตัน (&minus;33.7%)',
       'PM':' &middot; <b>ปริมาณ 453 &rarr; 664 ตัน (+46.6%)</b> วันที่สองหลังกลับมารับซื้อ',
       'MS':' &middot; 92.0% เป็นค่าเดียวกับแถว forecast 18&ndash;19-Nov &middot; ไม่นับใน CAG รวม'}
""")
rep("assert lc[0]=='11-Nov' and waitcore==['TN','PM','TDC'], (waitcore,lc)","assert lc[0]=='11-Nov' and waitcore==['TN','TKT','PM','TDC'], (waitcore,lc)")
rep("(ผลโม่ %s ของ TN, PM, TDC ยังไม่เข้า; ไม่รวม MS)","(ผลโม่ %s ของ TN, TKT, PM ยังไม่เข้า &middot; TDC ยังไม่ลงข้อมูล; ไม่รวม MS)")
rep("&middot; ครบ 5 โรง (TDC ลงข้อมูลแล้วรอบ 09:2x น.) &middot; PM กลับมารับซื้อ &middot; ส่วนต่างราคา","&middot; 4 โรง (TDC ยังไม่ลงปริมาณ 17-Nov ณ รอบนี้ &rarr; ยังไม่ใช่ยอดครบ 5 โรง) &middot; ส่วนต่างราคา")
rep("assert lab[tj]=='15-Nov'","assert lab[tj]=='16-Nov'")
rep("TWWHY='อีเมล put.p ล่าสุด = &ldquo;on Nov 15, 2026&rdquo; (รับ 16-Nov 09:42 น.) &middot; ยังไม่มีอีเมลของ 16-Nov ณ %s'%NOW","TWWHY='อีเมล put.p ล่าสุด = &ldquo;on Nov 16, 2026&rdquo; (รับ 17-Nov 20:18 น.) &middot; ยังไม่มีอีเมลของ 17-Nov ณ %s'%NOW")
cut("&middot; PM กลับมารับซื้อ (หลังหยุดเทศกาลแข่งเรือ 12&ndash;15-Nov) &middot; TDC ลงข้อมูลแล้ว (รอบ 09:2x น.)","<b style=\"color:#374151\">TWIC {D} ยังไม่มีไฟล์","&middot; <b>TDC ยังไม่ลงปริมาณ {D}</b> (ช่องว่าง &rarr; เว้นทั้งแถว) &middot; ผลโม่ {D} ยังไม่เข้าทั้ง 4 โรง (TN 100.0% / PM 100.0% / TKT 95.0% = default &middot; MS 92.0% = placeholder) &middot; TWIC 16-Nov เข้าแล้ว ({fm(tw['vol'][tj],0)} ตัน @ {fm(tw['price'][tj])} / CAG {fm(tw['cag'][tj])}) &middot; ")
rep("TWIC ล่าสุด = อีเมล on Nov 15, 2026)</div>","TWIC ล่าสุด = อีเมล on Nov 16, 2026)</div>")
rep("({D} &mdash; ครบ {len(b3)} โรง)</div>","({D} &mdash; {len(b3)} โรง &middot; TDC ยังไม่ลง)</div>")
rep("12&ndash;16-Nov ยังปิดไม่ได้ (12&ndash;15-Nov รอผลโม่ TN &middot; 16-Nov รอผลโม่ TN, PM, TDC)","12&ndash;17-Nov ยังปิดไม่ได้ (12&ndash;15-Nov รอผลโม่ TN &middot; 16-Nov รอ TN, PM, TDC &middot; 17-Nov รอ TN, TKT, PM + TDC ยังไม่ลงข้อมูล)")
cut("  <b style=\"color:#b45309\">&#9888; {D}: ลงข้อมูลแล้ว {len(b3)} โรง ({fm(v3,0)} ตัน) &middot; PM กลับมารับซื้อ","  <br><b style=\"color:#374151\">ปริมาณ:</b>","""  <b style="color:#b45309">&#9888; {D}: ลงข้อมูลแล้ว {len(b3)} โรง ({fm(v3,0)} ตัน: {tot}) &middot; <b>TDC ยังไม่ลงปริมาณ</b> (ช่องปริมาณว่าง &middot; ราคา 4.05 / %ST 25.00% ในแถวเป็น forecast &rarr; เว้นทั้งแถว) &middot; ผลโม่ {D} ยังไม่เข้าทั้ง 4 โรง: TN 100.0% / PM 100.0% / TKT 95.0% (Total=R1=R2) = default, MS 92.0% = placeholder &rarr; เว้นว่างทั้ง %Recovery และ CAG &mdash; <b>CAG รวม {D} ปิดไม่ได้ &mdash; ล่าสุดที่ครบ = {lc[0]}: {fm(lc[1])}, {len(lc[2])} โรง {fm(lc[3],0)} ตัน (ไม่รวม MS)</b></b>
  <br><b style="color:#374151">ข้อมูลใหม่ (รอบนี้ {NOW}):</b> <b>วันใหม่ {D}</b> ({len(b3)} โรงไทย) &middot; <b>TWIC 16-Nov เข้าแล้ว</b> ({twt(tj)}) &middot; ตรวจ 1&ndash;16-Nov ทั้ง 5 โรงกับไฟล์ต้นทาง: ไม่มีตัวเลขเปลี่ยน ไม่มีผลโม่ย้อนหลังเข้า (TN 12&ndash;16-Nov ยัง 100.0% default &middot; PM 16-Nov ยัง 100.0% &middot; TDC 16-Nov ยังว่าง) &middot; <b style="color:#b45309">TN 16-Nov %ST ยังเป็น 25.00% (ค่ากลม) อาจเป็นค่าชั่วคราว</b> &middot; วันย้อนหลัง (Nov) ที่ CAG รวมยังปิดไม่ได้: {' &middot; '.join(openback) or '&mdash;'}
""")
rep("<b style=\"color:#b45309\">เทียบ 11-Nov (5 โรง ก่อน PM หยุด) {fm(v11,0)} &rarr; {fm(v3,0)} ตัน = {(v3/v11-1)*100:+.1f}%</b>","<b style=\"color:#b45309\">{D} เป็นยอด {len(b3)} โรง (TDC ยังไม่ลง) จึงยังเทียบยอดรวม 5 โรงไม่ได้</b>")
rep("OR='17-Oct ถึง 15-Nov'","OR='18-Oct ถึง 16-Nov'")
rep("(1&ndash;16-Nov) (อ่านไฟล์รอบ","(1&ndash;17-Nov) (อ่านไฟล์รอบ")
rep("r'1[0-5]-Nov|15 November|16-Nov-2026 1'","r'16 November|17-Nov-2026 1'")
open(m+'_gen_1118r1.py','w',encoding='utf-8').write(s)
# backfill diff: old SRC vs new for keys read this run
old=json.loads(re.search(r"SRC=json.loads\('''(.*?)'''\)",open(m+'_diff_1117r4.py',encoding='utf-8').read(),re.S).group(1))
for k,v in NEW.items():
    if old[k]!=v: print('SRC CHANGED',k,old[k],'->',v)
print('ok')
