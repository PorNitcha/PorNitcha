# Root Price — Last Reported / Last Emailed State

## STATE (ตัวควบคุมการส่งอีเมล — อัปเดตทุกครั้งที่ส่ง)
- `thai_last_sent_date`  : **2026-08-04**   (ข้าม 3-Aug/4-Aug ตามที่ Por สั่ง 5-Aug — ให้เริ่มส่งจากข้อมูล 5-Aug เป็นต้นไป)
- `twic_last_sent_date`  : **2026-08-04**   (มีข้อมูล TWIC ถึง 4-Aug แล้ว)
- `cag_alert_date`       : **2026-08-04**   (วันล่าสุดที่แจ้ง Por เรื่อง CAG ไม่มาภายใน 12:00 — กันแจ้งซ้ำ)   (วันที่ข้อมูล TWIC ที่ส่งไปแล้ว/ถือว่าครอบคลุมแล้ว)
- หมายเหตุ: อีเมล 2-Aug ที่ส่งจริงเมื่อ 3-Aug 18:35 **ยังไม่มี TWIC** (เพิ่ม TWIC เข้า dashboard ทีหลัง)
  Por สั่งให้ข้ามการส่งรอบ TWIC ของคืนนี้ และเริ่ม cadence ใหม่ตั้งแต่พรุ่งนี้ → จึง set twic_last_sent_date = 2026-08-01

## บันทึกการตัดสินใจ 5-Aug-2026
- Por สั่ง: **ไม่ต้องส่งอีเมลของ 4-Aug** (ที่ค้างเพราะเบราว์เซอร์หลุด + ตัวแนบไฟล์บั๊ก) → **รอข้อมูลวันที่ 5-Aug แล้วค่อยส่ง**
- จึงตั้ง thai_last_sent_date = 2026-08-04 เพื่อให้ระบบข้าม 4-Aug และส่งอีเมลรอบถัดไปเมื่อ **ข้อมูลไทย 5-Aug ครบ** (คาดว่าลงไฟล์ราว 6-Aug เพราะไฟล์อัปเดต T-1)
- **TODO เมื่อเบราว์เซอร์กลับมา:** ลบ draft ค้างชื่อ "Daily root dashboard - 4 August 2026" ใน Outlook > Drafts (ไม่มีไฟล์แนบ ไม่ควรส่ง) — draft ไม่ส่งเองอยู่แล้ว จึงไม่เร่งด่วน
- อีเมล 5-Aug เมื่อส่ง: subject `Daily root dashboard - 5 August 2026`, ผู้รับ 8 คน, แนบกราฟ 6 + HTML ตามปกติ

---

## กฎการส่งอีเมล (Por ยืนยัน 3-Aug-2026) — ไทยเป็นตัวตั้ง
ทุกรอบที่รัน ให้หา `thai_reporting_date` (วันล่าสุดที่ไทยครบทุกโรงงาน) และ `twic_latest_date` (วันล่าสุดที่ TWIC มี) แล้ว:
1. ถ้า `thai_reporting_date` > `thai_last_sent_date`
   → **ส่งอีเมล** พร้อมข้อมูล TWIC เท่าที่มี ณ ตอนนั้น
   → อัปเดต **ทั้ง** thai_last_sent_date และ twic_last_sent_date (= twic_latest_date)
   *(เคสนี้ครอบคลุมข้อยกเว้นของ Por: ถ้า TWIC มาก่อน มันจะถูกรวมมาในอีเมลนี้เอง = ส่งรอบเดียว)*
2. ถ้าไม่เข้าข้อ 1 แต่ `twic_latest_date` > `twic_last_sent_date`
   → **ส่งอีเมลรอบที่สอง** (TWIC updated) subject ต่อท้ายด้วย `(TWIC updated)`
   → อัปเดตเฉพาะ twic_last_sent_date
3. นอกจากนั้น → **หยุดเงียบๆ ไม่ส่งอะไร**

ผลลัพธ์ที่ควรได้: ปกติวันละ 2 รอบ (ไทยก่อน แล้ว TWIC ตามมา) แต่ถ้า TWIC พร้อมก่อนไทย จะได้รอบเดียวรวมกัน

---

## ผู้รับอีเมล (อัปเดต 5-Aug-2026 — 8 คน)
1. nitcha.s@thaiwah.com — Por (Finance Director)
2. wipada.k@thaiwah.com — Wipada Kiatwuttikrai
3. napatkanok.k@thaiwah.com — Napatkanok Khunasakpitak
4. benjamas.p@thaiwah.com — Benjamas Prateeppornnarong (Senior Manager, Supply Chain Finance & Costing)
5. patcharin.w@thaiwah.com — Patcharin Wachiraworakam  *(เพิ่ม 4-Aug)*
6. supattra.k@thaiwah.com — Supattra Kemasith  *(เพิ่ม 4-Aug)*
7. chintaapha.k@thaiwah.com — Chintaapha Kitikunanon  *(เพิ่ม 4-Aug)*
8. nittaya.p@thaiwah.com — Nittaya Puengpradit  *(เพิ่ม 5-Aug)*
หมายเหตุ: 3 คนที่เพิ่มใหม่ อยู่ในรายชื่อผู้รับ "Daily root purchased report" ของทีม sourcing อยู่แล้ว (ยืนยันอีเมลถูกต้อง)

---

## บทเรียนสำคัญ 5-Aug-2026 — %Recovery / CAG มาช้ากว่า volume 1 วัน
Por ทักว่าตัวเลข TKT/TDC วันที่ 3-Aug "มาไม่ครบ" → ตรวจแล้ว**พบว่าถูกต้อง** และวันถัดมาไฟล์ถูกแก้จริง:
| plant | 3-Aug ตอนแรก | 3-Aug หลังโรงงานลงจริง |
|---|---|---|
| TKT | recovery 95.0% (=ค่า Forecast) ทั้ง Total/Native/CF · CAG 19.57 | recovery **102.9%** (Native 103.1 / CF 102.6) · CAG **18.06** |
| TDC | consumption ว่าง · recovery 100.0% · CAG 17.66 | consumption 316 · recovery **97.3%** · CAG **18.15** |
| PM  | recovery 100.0% · CAG 18.01 | recovery **0.0%** (ยังไม่ลงผลโม่) → CAG = null |

**รูปแบบที่เจอ:** ปริมาณซื้อ + ราคา มาครบตั้งแต่ T-1 แต่ **ผลการโม่ (%Recovery, CAG) ตามมาอีก ~1 วัน**
ระหว่างที่ยังไม่ลง ไฟล์จะใส่ค่าตั้งต้นไว้ ทำให้ดูเหมือนมีข้อมูลแล้วทั้งที่ยังไม่จริง

**วิธีจับ placeholder (ใช้แล้วตั้งแต่ 5-Aug):** ถือว่าไม่ใช่ค่าจริงเมื่อเข้าเงื่อนไขใดเงื่อนไขหนึ่ง
1. Root consumption ว่างหรือ 0
2. %Recovery = 0.0%
3. %Recovery = 100.0% พอดี **และ** |CAG − CBG| < 0.02 (คือ CAG ไม่ได้ถูกหารด้วย recovery จริง)
4. (TKT) %Recovery Total = Native = CF เท่ากันเป๊ะและลงตัว เช่น 95.0% → เป็นค่า Forecast
→ กรณีเหล่านี้ให้ตั้ง **ทั้ง %Recovery และ CAG เป็น null** (เดิมตั้ง null เฉพาะ recovery แต่ยังโชว์ CAG ซึ่งทำให้เข้าใจผิด)

**ผลต่อ CAG ระดับกลุ่มในไฟล์:** 3-Aug ตอนแรกไฟล์โชว์ 23.72 หลังแก้กลายเป็น **31.73** เพราะ PM recovery ตกเป็น 0
→ ตัวเลข group CAG ในวันที่ข้อมูลยังไม่ครบ **บิดเบือนได้มาก** เวลารายงานต้องกำกับเสมอว่าโรงงานไหนยังรอผลโม่

---

## CAG (Cost After Grind) — เพิ่มเข้า dataset แล้ว 2026-08-03
- นิยาม: CAG = Cost before grind ÷ %Recovery  (ตรวจสอบแล้วตรงกับสูตรในไฟล์)
  และ Cost before grind = ราคา ÷ %Starch
- ดึงค่าจาก column "Cost after grind(THB/Kg.)" ของแต่ละ plant block ในชีต master (July/Aug)
- **วันที่ไม่ได้เดินเครื่อง (consumption = 0) จะไม่มี %Recovery → ไม่มี CAG → เก็บเป็นค่าว่าง/null**
  (อย่าใส่ 0 เพราะจะทำให้กราฟดิ่งลงผิด)
- CAG ต่อโรงงานช่วง 30 วันนี้: 11.46 – 61.78 บาท/กก. ค่าที่สูงผิดปกติเกิดในวันที่ recovery ต่ำมาก
  เช่น TKT 30-Jul recovery 28.3% → CAG 61.78 (เป็นค่าจริง ไม่ใช่ error)
- **CAG ระดับกลุ่ม (total) ในไฟล์ ไม่เท่ากับค่าเฉลี่ยถ่วงน้ำหนักด้วยปริมาณของ CAG รายโรงงาน**
  ไฟล์ใช้ Avg Recovery ของกลุ่มคำนวณ (2-Aug: group CAG = 21.88 แต่ weighted avg รายโรงงาน = 17.43)
  → ถ้าจะโชว์ CAG รวม ให้ใช้ตัวเลขจากไฟล์โดยตรง ห้ามคำนวณเอง

## วิธี parse ไฟล์ master (บทเรียนสำคัญ)
- read_resource คืนค่าเป็น text dump บรรทัดเดียวยาวมาก ต้อง split ด้วย date token
- ต้องเก็บเฉพาะ occurrence **แรก** ของแต่ละวันที่ (occurrence หลังๆ คือ label ของกราฟ)
- หา block ของแต่ละโรงงานด้วย "capacity token" เป็น anchor: TN=850, PM=750, MS=700,
  TKT=300 (ก.ค.) → **550 (ส.ค. เปลี่ยนแล้ว)**, TDC=250/400
- ต้อง validate anchor ด้วย pattern ก่อนหน้า (price, %starch, cost) เพราะบางวัน stock บังเอิญ = capacity
- วันที่โรงงานหยุด column จะยุบหาย → block สั้นลง ให้ถือว่าไม่มีข้อมูล (vol 0, CAG null)
- หา CAG ใน right block ด้วยวิธี "ข้าม token ที่ลงท้าย % แล้วเอาตัวเลขตัวแรก" (ตำแหน่ง fix ไม่ได้
  เพราะบางวัน %Recovery หายไป ทำให้ index เลื่อน — เคยพลาดได้ค่า expense มาแทน CAG)

## หมายเหตุสถานะโรงงาน
- PM (พิมาย) shut down 15–24 Jul, กลับมา 25-Jul (69 t) และเดินเครื่องเต็มที่ในเดือน ส.ค. (540 t, 220 t)
- MS (แม่สอด) ยังไม่มีการซื้อเลย (ค่า 0 จริง ไม่ใช่ข้อมูลขาด)
- 31-Jul ไม่มีการลงข้อมูลในไฟล์ ก.ค. (null ทั้งวัน)
- TKT capacity เปลี่ยนจาก 300 → 550 ตั้งแต่เดือน ส.ค.


## %Recovery — เพิ่มเข้า dataset แล้ว 2026-08-03
- อยู่ใน column "%Recovery" ของ plant block (TKT ใช้ %Recovery **Total**)
- ดึงด้วยกฎ: token ตัวที่ 3 ของ right block **ถ้าลงท้ายด้วย %** เท่านั้น
  (ถ้าไม่ลงท้ายด้วย % แปลว่าวันนั้นไม่มี recovery และ token นั้นคือ CAG แล้ว)
- **ระวัง placeholder:** ไฟล์ใส่ `100.0%` ในวันที่คำนวณ recovery จริงไม่ได้ สังเกตได้จาก CAG = CBG พอดี
  → กฎ: ถ้า recovery = 100.0% **และ** |CAG − CBG| < 0.02 ให้ถือเป็น **null** (ไม่ใช่ recovery จริง)
  ตรวจสอบแล้วตรงกับชีตราย plant ที่ช่อง Recovery ว่างจริง
- ช่วงค่าจริง 30 วันล่าสุด: 28.3% – 149.7% (ต่ำสุด TKT 30-Jul = 28.3% ทำให้ CAG พุ่งเป็น 61.78)

## กฎการแสดงผลกราฟ (Por ยืนยัน 2026-08-03)
- **ห้ามใช้ 0 กับ price / %starch / starch ton / CAG / %recovery** — ถ้าไม่มีค่าจริงให้เป็น null
  เพื่อให้เส้น "ขาดช่วง" แทนที่จะดิ่งลงศูนย์ (ตั้ง `spanGaps: false` ทุก line series)
- **volume คงค่า 0 ไว้** เพราะแท่ง 0 = ซื้อจริง 0 ตัน เป็นข้อมูลที่มีความหมาย
- ใน CSV ใช้ค่าว่าง (empty) แทน null


## รอบ 3-Aug-2026 (scheduled run เย็น)
- 3-Aug มีเพียง **PM ที่ซื้อ 525 ตัน @3.75 ฿/กก., %starch 20.82%, CBG=CAG=18.01**
  (recovery ในไฟล์ = 100.0% placeholder → null ตามกฎ)
- **TKT หยุดซื้อ 3-Aug** สต็อกยกมา 640 ตัน (ชีต TKT ระบุ purchased = 0 ชัดเจน)
- **TDC ลงเป็น 0 ทุกช่อง** ในชีตราย plant → ยืนยันไม่มีการซื้อ · TDC capacity ในไฟล์ ส.ค. = **400** (ไม่ใช่ 250)
- **TN ต้องระวัง:** master ลง stock 0 / purchased 0 แต่ **ชีตราย plant ของ TN ยังไม่มีแถว 3-Aug เลย**
  → บันทึกเป็น volume 0 แต่แจ้ง Por ว่าอาจยังไม่อัปเดต (ตอนรอบถัดไปให้เช็กซ้ำว่าตัวเลข TN 3-Aug เปลี่ยนหรือไม่)
- CAG กลุ่ม 3-Aug (จากไฟล์) = **22.80** ฿/กก., group avg recovery = 79% (ห้ามคำนวณเอง — ยืนยันกฎเดิม)
- External (nettathai): โพสต์ล่าสุด **30 ก.ค. 2569** แต่ช่อง "พิมาย" = "-" ไม่มีราคาประกาศ
  → root-price-external.csv ไม่มีข้อมูลใหม่ ยังคงมีแค่จุด 15-Jul (25% = 3.60, 30% = 4.00)
- ราคาอ้างอิงในไฟล์ที่เป็น forecast default (TN 3.78 / TKT 3.83 / TDC 3.97) **ห้ามนับเป็นราคาซื้อจริง**
  สังเกตได้จากค่าซ้ำกันทุกวันตั้งแต่ 4-Aug เป็นต้นไป

## TWIC (กัมพูชา) — เพิ่มเข้า dashboard 2026-08-03
- **แหล่งข้อมูล: อีเมลจาก put.p@thaiwah.com** หัวข้อ "TWIC daily root purchased report on {Mon, DD YYYY}"
  ส่งทุกวันทำการ (จ-ศ) เช้าประมาณ 08:00-09:00 รายงานข้อมูล "ของวันก่อนหน้า"
- ไฟล์แนบเป็น .xlsx แต่ **connector อ่าน binary ไม่ได้** → ให้อ่านจาก **inline image** ในเนื้ออีเมลแทน
  (read_resource บน attachment URI ของ image001.jpg / image002.jpg คืนค่าเป็นรูปที่อ่านได้)
- **ลำดับ image ไม่คงที่!** ต้องเปิดดูทั้งสองรูป
  * รูปหนึ่งคือ "ตารางสรุปรายวันของเดือน" (Date / Stock / Purchased Volume (Tons) / Price(KHR) / **Price(THB)** /
    Starch(%) / Actual root Consumption / Carry Over / Starch output / **Cost before grind** / **Recovery(%)** /
    **Cost after grind** / Gap / Expense / Est.Starch / Exchange rate) + แถว MTD
  * อีกรูปคือรายละเอียดระดับ supplier (FARMER / BROKER) ของวันนั้นวันเดียว
- **ตารางสรุปโชว์ย้อนหลังแค่ ~11-12 วัน** ถ้าต้องการ 30 วันต้องเปิดอีเมลหลายฉบับคาบเกี่ยวกัน
  (เช่น ฉบับวันที่ 11, 22, 31 ของเดือน) แล้วเช็ควันซ้ำให้ตรงกัน
- **Validate เสมอ:** ผลรวม purchased รายวันต้องเท่ากับแถว MTD ในรูป (เคยเช็คแล้วตรง 926 / 1,495 / 2,569 t)
- ใช้ **Price(THB)** (แปลงจาก KHR แล้ว ~120-121 KHR/THB) เพื่อเทียบกับโรงงานไทยได้
- Recovery = 0.00% ในวันที่ไม่ได้โม่ → CAG แสดง #DIV/0! → เก็บเป็น null (เหมือนโรงงานไทย)
- วันอาทิตย์ไม่มีแถวในตาราง = ไม่มีการซื้อ → volume 0, ที่เหลือ null
- **TWIC ช้ากว่าโรงงานไทย 1 วัน** (ณ 3-Aug: ไทยมีถึง 2-Aug แต่ TWIC มีถึง 1-Aug เท่านั้น)
- **ห้ามรวม TWIC เข้ายอด total ของโรงงานไทย** — คนละนิติบุคคล (TWPC Investment Cambodia),
  ราคาตั้งต้นเป็น KHR, และไฟล์ต้นทางของไทยก็ไม่ได้รวม TWIC ในยอดกลุ่ม → แสดงเป็นบรรทัด/กราฟแยก
- ราคา TWIC ต่ำกว่าไทยมาก (~2.4-2.9 vs 3.7-3.9 THB/kg) แต่ %starch ก็ต่ำกว่า (~16-17% vs 20-23%)
  → เทียบกันควรดูที่ CAG/ต้นทุนต่อแป้ง ไม่ใช่ราคาหัวมันดิบเพียวๆ

---

## รอบ 5-Aug-2026 (scheduled run เย็น 17:13) — อัปเดตข้อมูล + ยังคงถือ email ตามที่ Por สั่งรออนุมัติ
- ไฟล์ไทย 08_Aug 2026 (แก้ไขล่าสุด 5-Aug 16:49): reporting date = 4-Aug (T-1)
- **ข้อมูลใหม่รอบนี้: ผลโม่ของ PM มาแล้วย้อนหลัง 2-3-4 Aug** (ก่อนหน้าเป็น placeholder/null)
  * PM 2-Aug: recovery 94.3% · CAG 18.51
  * PM 3-Aug: recovery 94.2% · CAG 19.12
  * PM 4-Aug: recovery 95.8% · CAG 18.59
  → อัปเดต root-price-history.csv (backup .bak7) + dashboard แล้ว (PM 4-Aug badge = ครบ)
- **4-Aug ยังรอผลโม่ 2 โรงงาน: TN และ TDC** (ไฟล์ใส่ recovery 100.0% + CAG=CBG = placeholder → null)
  TKT+PM ครบ · CAG กลุ่มจากไฟล์ 4-Aug = 23.88 (Avg Recovery 73.6% ยังบิดเบือนจาก placeholder 2 โรงงาน)
- **CAG alert (step D):** เลย 12:00 แล้ว · 4-Aug ปริมาณ+ราคาครบ แต่ TN/TDC ยังไม่มี CAG → flag ให้ Por ตามทีม (set cag_alert_date=2026-08-04)
- **Email: ยังไม่ส่ง** — thai_root_date (4-Aug) > thai_last_sent_date (2-Aug) และเลย 13:00 (ปกติเข้าเงื่อนไขส่ง)
  แต่ STATE ระบุชัดว่า Por ขอ **อนุมัติก่อน**ส่งของ 3-Aug/4-Aug → รอบอัตโนมัตินี้จึง **ไม่ส่งเอง** รายงาน Por เพื่อขออนุมัติแทน
  (ไม่แก้ thai_last_sent_date / twic_last_sent_date — คงไว้ 2-Aug / 1-Aug จนกว่า Por อนุมัติ)
- TWIC latest = 4-Aug (อยู่ใน CSV แล้ว) · ไม่มี TWIC วันใหม่

---
## รอบ 6-Aug-2026 (scheduled run เช้า 10:1x) — อัปเดตข้อมูล 5-Aug · ยังไม่ถึงคิวส่งอีเมล
- ไฟล์ไทย 08_Aug 2026 (แก้ไขล่าสุด 6-Aug 08:27): reporting date = **5-Aug** (T-1)
- **5-Aug ปริมาณ+ราคา+%Starch ครบทุกโรงงานที่ซื้อ (root complete)** แต่ **ผลโม่ (CAG/%Recovery) ยังไม่ลงเลยสักโรงงาน**
  * TN 489t @3.78 (23.04%) · TKT 792t @3.93 (21.37%) · PM 603t @3.81 (22.16%) · TDC 244t @3.78 (20.90%) · MS ไม่ซื้อ
  * placeholder: TN/PM = cons ว่าง + rec 100.0% (CAG=CBG) · TDC rec 100.0% (CAG=CBG) · **TKT rec Total=Native=CF=95.0% (ค่า forecast)** → ทั้งหมดตั้ง CAG/rec = null
  * ราคาไทยขึ้นทุกโรงงานเทียบ 4-Aug (TN +0.02, TKT +0.03, PM +0.05, TDC +0.02) · wavg 3.84 · รวม 5 โรงไทย 2,128 t
  * group CAG ในไฟล์ 23.68 (AvgRec 73.8%) — บิดเบือนจาก placeholder ทั้ง 4 โรง ไม่ใช้
- **แก้ CSV:** TDC 5-Aug เดิมเป็น 0 (ตอน run ก่อนยังไม่ลง) → อัปเดตเป็น 244/3.78/20.9 (backup .bak8) · 1–4 Aug ตรงกับ CSV เดิมทุกค่า ไม่มี revision
- **4-Aug ตอนนี้ครบสมบูรณ์แล้ว** (TN rec 95.5%/CAG 17.07 · TDC rec 97.0%/CAG 18.09 ผลโม่มาแล้ว) — ยืนยัน pattern ผลโม่ช้า ~1 วัน
- **TWIC:** อีเมลล่าสุด "Aug, 04 2026" (put.p ส่ง 5-Aug เช้า) · **ยังไม่มีอีเมล 5-Aug** → twic_latest = 4-Aug (อยู่ใน CSV แล้ว) ไม่มีของใหม่
- **Dashboard:** อัปเดตเป็นหน้าต่าง 7-Jul→5-Aug (rolling 30) · badge 5-Aug: TN/TKT/PM/TDC = รอผลโม่(เหลือง) · MS = ไม่ซื้อ(เทา) · TWIC = ยังไม่ลงข้อมูล 5-Aug · verify แล้วไม่มี error
- **CAG alert (step D):** ยังไม่ถึง 12:00 (รันเช้า) → ไม่แจ้ง · cag_alert_date คงเดิม 2026-08-04
- **Email (rule E):** thai_root_date(5-Aug) > thai_last_sent(4-Aug) = มีวันใหม่ที่ต้องส่ง **แต่ CAG ยังไม่ครบ และยังไม่ถึง 13:00** → **ยังไม่ส่ง (รอ CAG มาก่อน)** · ไม่แก้ state
- **รอบถัดไป:** ถ้าผลโม่ 5-Aug ลงครบ → ส่งอีเมล 5-Aug ได้ทันที · ถ้าเลย 13:00 แล้วยังไม่ครบ → ส่งได้เลยพร้อม note "รอผลโม่" · ถ้าเลย 12:00 แล้วยังไม่ครบ → แจ้ง Por (step D)
- STATE คงเดิม: thai_last_sent=2026-08-04 · twic_last_sent=2026-08-04 · cag_alert=2026-08-04
