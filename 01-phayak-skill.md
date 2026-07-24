---
name: phayak-forecast-variance
description: สร้าง forecast P&L รายเดือน/ไตรมาส และวิเคราะห์ variance ระหว่าง actual กับ forecast/budget พร้อมหาสาเหตุ (driver) ที่กระทบกำไร-ยอดขาย ใช้เมื่อ Por หรือทีมขอ forecast, variance analysis, หรือถามว่า "ทำไม margin/ยอดขายถึงเปลี่ยนไป"
---

# Skill: Forecast & Variance Analysis (น้องพยาก)

## เมื่อไหร่ใช้ skill นี้
- ขอ forecast P&L (เดือน / ไตรมาส / ปี)
- ขอเทียบ actual vs. forecast/budget
- ถามหาสาเหตุที่กำไรหรือยอดขายเปลี่ยนไปจากที่คาด

## Input ที่ต้องมีก่อนเริ่ม
- Actual P&L ล่าสุดจาก SAP/Excel ของ period ที่ต้องการ
- Forecast/Budget เดิมของ period เดียวกัน
- (ถ้ามี) driver ภายนอก เช่น FX, ราคาวัตถุดิบ, seasonality

**ถ้าข้อมูลไม่ครบ → ถามกลับก่อนเสมอ ห้ามเดาตัวเลข**

## ขั้นตอนการทำงาน
1. รวบรวม actual + forecast/budget ของ period เดียวกัน เช็คหน่วยให้ตรงกัน (currency, scale)
2. คำนวณ variance รวม (actual − forecast) ทั้งจำนวนเงินและ %
3. แตก variance เป็น driver ย่อย: volume / price / cost / mix / FX (ตามที่ข้อมูลรองรับ)
4. จัดเรียงเป็น variance bridge (waterfall): forecast → drivers → actual
5. Flag รายการที่ variance ผิดปกติ (เกิน threshold ที่ Por กำหนด หรือ >10% โดย default) พร้อมระบุระดับความมั่นใจของสาเหตุ (fact / estimate / assumption)
6. สรุป executive summary 3-5 bullet: driver หลัก, ความเสี่ยงที่ต้องจับตา, คำแนะนำเบื้องต้น
7. Sanity check ก่อนส่ง: ผลรวม bridge ต้องเท่ากับ variance รวม, % ต้องสมเหตุสมผล, ไม่มี unit mismatch

## Output format
- ตาราง + variance bridge chart สไตล์ BCG (คลีน, สีสื่อความหมาย: เขียว = ดีกว่าคาด, แดง = แย่กว่าคาด, เทา = neutral)
- Executive summary แบบ bullet สั้น ตรงประเด็น
- ระบุชัดว่าอันไหนคือ fact จากข้อมูล อันไหนคือ estimate/สมมติฐาน

## 📓 Lesson Learned Protocol (ทำทุกครั้งหลังจบงาน)
ก่อนปิดงาน ให้เพิ่ม entry ใหม่ต่อท้าย "Lesson Learned Log" ด้านล่างของไฟล์นี้ ตามฟอร์แมต:

```
### [วันที่] — [งานที่ทำ เช่น "Forecast Q3/2026"]
- สิ่งที่ทำได้ดี:
- สิ่งที่ควรปรับปรุง/ทำให้เร็วขึ้นครั้งหน้า:
- ข้อมูล/แหล่งข้อมูลที่ขาดหรือต้องขอเพิ่มบ่อย:
- สมมติฐานที่ผิดพลาด (ถ้ามี) และวิธีแก้:
- Action สำหรับงานครั้งถัดไป:
```

---

## Lesson Learned Log
_(ยังไม่มี entry — จะเพิ่มหลังจบงานแต่ละครั้ง)_

### 2026-07-24 — TDC ASP by Reactor Group & FX Impact Report (HTML, interactive)
- สิ่งที่ทำได้ดี: ก่อนสร้าง output ได้ตรวจ raw data (Billing Report Z01, 7,991 แถว x 101 คอลัมน์) ด้วย Excel COM ก่อนเชื่อค่า — เจอว่าต้อง exclude กากสด (Reactor group ว่าง), เอกสารที่ถูก cancel (flag Cancelled=X), และเอกสาร reversal (Billing Type=ZBCN) ไม่งั้นยอดขาย/ASP จะเพี้ยน แล้ว cross-check ตัวเลขที่คำนวณได้กับรีพอร์ท FX เก่า (TDC_FX_Impact_Report_Mar26.html) ก่อนส่ง — ตัวเลข ASP ตรงเป๊ะ ต่างกันแค่ volume เล็กน้อย (คาดว่าเพราะข้อมูลถูก refresh/reconcile ใหม่เมื่อ 11-Jul-26)
- สิ่งที่ควรปรับปรุง/ทำให้เร็วขึ้นครั้งหน้า: เครื่องนี้ไม่มี Python/Node ติดตั้ง ต้องใช้ Excel COM (PowerShell) อ่าน/export ข้อมูลจาก xlsx แทน — ช้ากว่า pandas พอสมควร ควรเตรียม script ไว้ล่วงหน้าถ้าจะทำซ้ำ; และ Browser pane preview ไฟล์ local นอก working directory (`file://`) จะ render เป็น static snapshot รัน JS ไม่ได้ — ต้องตั้ง local HTTP server (PowerShell HttpListener) ชั่วคราวเพื่อทดสอบ interactive HTML ก่อนส่งมอบ
- ข้อมูล/แหล่งข้อมูลที่ขาดหรือต้องขอเพิ่มบ่อย: ไม่มี — Billing Report Z01 มีครบ (SN, Reactor, Reactor group, ASP USD/THB, exchange rate ต่อบิลอยู่แล้ว)
- สมมติฐานที่ผิดพลาด (ถ้ามี) และวิธีแก้: เขียน formula แสดงค่า signed MB (+/−) ผิดตอนแรก — ใช้ `Math.abs()` ตัด sign ออกไปแล้วไม่ได้เติม "−" กลับตอนค่าเป็นลบ (โชว์เป็นค่าบวกผิดๆ) ตรวจพบจาก preview จริงก่อนส่ง แก้เป็น helper function `fmtSignedMB()` ที่คง sign ไว้ตลอด
- Action สำหรับงานครั้งถัดไป: เก็บ methodology exclusion rules (กากสด/Cancelled=X/ZBCN) ไว้ใน mid-term memory แล้ว ([[tdc-billing-methodology]]) — ครั้งหน้าไม่ต้องมา diagnostic ใหม่ทุกครั้ง แค่ apply กฎเดิมกับข้อมูลที่ refresh ล่าสุด
