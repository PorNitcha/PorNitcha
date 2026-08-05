# Root Price — Last Reported / Last Emailed State

## STATE (ตัวควบคุมการส่งอีเมล — อัปเดตทุกครั้งที่ส่ง)
- `thai_last_sent_date`  : **2026-08-02**   (reporting date ของไทยที่ส่งอีเมลไปแล้ว)
- `twic_last_sent_date`  : **2026-08-01**   (วันที่ข้อมูล TWIC ที่ส่งไปแล้ว/ถือว่าครอบคลุมแล้ว)
- หมายเหตุ: อีเมล 2-Aug ที่ส่งจริงเมื่อ 3-Aug 18:35 **ยังไม่มี TWIC** (เพิ่ม TWIC เข้า dashboard ทีหลัง)
  Por สั่งให้ข้ามการส่งรอบ TWIC ของคืนนี้ และเริ่ม cadence ใหม่ตั้งแต่พรุ่งนี้ → จึง set twic_last_sent_date = 2026-08-01

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

## ผู้รับอีเมล (อัปเดต 4-Aug-2026 — 7 คน)
1. nitcha.s@thaiwah.com — Por (Finance Director)
2. wipada.k@thaiwah.com — Wipada Kiatwuttikrai
3. napatkanok.k@thaiwah.com — Napatkanok Khunasakpitak
4. benjamas.p@thaiwah.com — Benjamas Prateeppornnarong (Senior Manager, Supply Chain Finance & Costing)
5. patcharin.w@thaiwah.com — Patcharin Wachiraworakam  *(เพิ่ม 4-Aug)*
6. supattra.k@thaiwah.com — Supattra Kemasith  *(เพิ่ม 4-Aug)*
7. chintaapha.k@thaiwah.com — Chintaapha Kitikunanon  *(เพิ่ม 4-Aug)*
หมายเหตุ: 3 คนที่เพิ่มใหม่ อยู่ในรายชื่อผู้รับ "Daily root purchased report" ของทีม sourcing อยู่แล้ว (ยืนยันอีเมลถูกต้อง)

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
