---
name: tdc-billing-methodology
description: โครงสร้างข้อมูล Billing Report (Z01) ของ TDC และกฎ exclusion ที่ใช้คำนวณ ASP/FX ให้ถูกต้อง — ใช้เมื่อวิเคราะห์ยอดขาย/ASP/FX ของ TDC จาก raw billing data
metadata:
  type: mid-term
---

Billing Report ของ TDC (Tapioca Development Corp.) อยู่ที่ `TDC billing\Billing Report 2025-2026_*.xlsx`,
worksheet **Z01** (Plant = "Tapioca Development Corp." เสมอ, Division = "10" เสมอ — ไฟล์นี้มีแต่ข้อมูล TDC ไม่ต้อง filter plant เพิ่ม).

**คอลัมน์สำคัญ:** Billing Date, Year(89)/Month(90), Reactor(95)/Reactor group(96) — master mapping สำเร็จรูปอยู่ในไฟล์แล้ว
ไม่ต้อง join เพิ่มจาก `product master_TDC.xlsx`, SN(94), Net Weight-KG(83), Document Currency(64),
Net Val(After Disc)(59, หน่วยตาม currency เดิม), Net Val(After Disc) THB/LOCAL(78, แปลงเป็น THB แล้วด้วย exchange rate ของบิลนั้นๆ),
Cancelled(71), Billing Type(5).

**กฎ exclusion ก่อนคำนวณ ASP/ยอดขาย/FX (confirm แล้วจากการ cross-check กับรีพอร์ทก่อนหน้า):**
1. ตัดแถวที่ Reactor group เป็นค่าว่าง — คือ กากสด (wet cassava residue/by-product) และของที่ยัง unmatched (~37% ของแถวทั้งหมด)
2. ตัดแถวที่ Cancelled = "X" (บิลที่ถูกยกเลิก)
3. ตัดแถวที่ Billing Type = "ZBCN" (เอกสาร reversal/cancellation ที่มี Qty/NetVal เป็นลบอยู่แล้ว)
4. EUR-denominated lines มีน้อยมาก (พบ 1 แถว ~20T) — ตัดออกจาก USD/THB split ได้เลย ไม่กระทบภาพรวม

**Reactor group ที่พบ (เรียงตาม volume):** PO-XL (~50%), XL (~26%), PO (~11%), Others (~5%), MX (~4.5%), AC (~2.6%)

**สูตร ASP:**
- ASP USD ($/kg) = Σ Net Val(USD-invoiced) ÷ Σ Net Weight-KG(USD-invoiced)
- ASP THB (฿/kg) = Σ Net Val(THB-invoiced) ÷ Σ Net Weight-KG(THB-invoiced)
- Combined ASP (฿/kg) = (Σ THB-equivalent revenue ทั้ง USD+THB) ÷ (Σ kg ทั้งหมด)

**สูตร FX Gain/Loss vs reference rate R:** (Actual THB-equivalent revenue จาก USD sales) − (USD revenue × R)
— ค่าบวก = บาทอ่อนกว่า R ช่วงนั้น (ได้ THB มากกว่าสมมติฐาน), ค่าลบ = บาทแข็งกว่า R (ได้ THB น้อยกว่า)

**Data coverage ล่าสุดที่ทำ (ณ 24-Jul-2026):** Jan-2025 ถึง Jun-2026 (18 เดือน), ไฟล์ source refresh ล่าสุด 11-Jul-2026.
ตัวเลข volume ต่างจากรีพอร์ทเก่าที่ทำก่อนหน้า (TDC_FX_Impact_Report_Mar26.html) ไปประมาณ 2–5% — คาดว่าเพราะข้อมูลถูก reconcile ใหม่ระหว่างทาง ไม่ใช่ methodology ผิด (ASP ที่คำนวณได้ตรงกันเป๊ะในหลายเดือน).

ดู [[phayak-forecast-variance]] สำหรับ lesson learned ตอนสร้างรีพอร์ท ASP/FX แบบ interactive HTML ครั้งล่าสุด.
