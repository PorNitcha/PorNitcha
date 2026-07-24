# Mid-Term Memory — Fact ที่ Confirm แล้ว ใช้ได้ ~1 ปี

เก็บ fact ที่จบแล้ว confirm แล้ว และคาดว่าจะยังใช้ได้ถูกต้องไปอีกไม่เกิน ~1 ปี
เช่น target/budget ปีนี้, สมมติฐานหลักที่ใช้ทำ forecast ปีนี้, org structure ปัจจุบัน, ราคาที่ negotiate ไว้ปีนี้, นโยบายภายในปีนี้

**กฎ:** ก่อนเริ่มงานเรื่องใด ให้เช็คไฟล์นี้ก่อนเสมอว่ามี fact ที่เกี่ยวข้องหรือไม่ ห้ามถามซ้ำ/สมมติเองถ้ามีบันทึกไว้แล้ว
เมื่อครบอายุหรือไม่จริงแล้ว → ลบ/ปรับปรุงทันที อย่าปล่อยให้ fact เก่าค้างไว้

## ฟอร์แมต entry
| หัวข้อ | Fact | Confirm เมื่อ | คาดว่าใช้ได้ถึง | อ้างอิง/ที่มา |
|---|---|---|---|---|
| _ตัวอย่าง: Budget FY26_ | _รายละเอียด fact_ | _วันที่_ | _วันที่หมดอายุโดยประมาณ_ | _ใครยืนยัน/เอกสารอ้างอิง_ |

---

## รายการปัจจุบัน
| หัวข้อ | Fact | Confirm เมื่อ | คาดว่าใช้ได้ถึง | อ้างอิง/ที่มา |
|---|---|---|---|---|
| TDC Billing Report — โครงสร้างข้อมูล & กฎ exclusion | Raw data: `TDC billing\Billing Report 2025-2026_*.xlsx` sheet Z01. ต้องตัดกากสด (Reactor group ว่าง), Cancelled=X, Billing Type=ZBCN, EUR lines ก่อนคำนวณ ASP/FX. Reactor group mix: PO-XL ~50%, XL ~26%, PO ~11%, Others ~5%, MX ~4.5%, AC ~2.6%. รายละเอียดสูตร ASP/FX เต็มๆ ดูที่ `memory/tdc-billing-methodology.md` | 2026-07-24 | ~2027-07 (จนกว่า SAP/reporting structure จะเปลี่ยน) | สร้างรีพอร์ท TDC_ASP_FX_by_ReactorGroup.html, cross-check กับ TDC_FX_Impact_Report_Mar26.html |
| Daily Root Purchase Report — โครงสร้างไฟล์ & วิธี parse | ไฟล์: SharePoint site TWPCROOTSOURCINGTEAM > General/2026 Daily root report (เดือนปัจจุบัน) และ .../report (เดือนก่อนหน้า, backup). ชื่อไฟล์ "Daily root purchased report - {MM}_{Month} {YYYY}[1].xlsx". อีเมล supattra.janwiset@thaiwah.com เป็นแค่ notification ลิงก์ไปไฟล์นี้ ไม่ต้องรอ. ไฟล์นี้เนื้อหายาวเกิน token limit ของ read_resource เสมอ ต้องอ่านไฟล์ .txt ที่ระบบ save แทนแบบ chunk. 5 โรงงาน TN/TKT/PM/MS/TDC แยกด้วย Root Capacity คงที่ต่อโรงงาน: TN=850, TKT=300, PM=750, MS=700, TDC=400 (ใช้ cross-check ผลรวม MTD purchased กับ summary table ต้นไฟล์เพื่อยืนยัน). ราคารายวันดูจากตาราง "DAILY ROOT PRICE @ 25 %STARCH CONTENT" (5 ค่า/วัน เรียง TN,TKT,PM,MS,TDC) และปริมาณ/starch% ดูจากตารางย่อย "Root Purchased (Tons)" ของแต่ละโรงงาน (คอลัมน์ layout เปลี่ยนเล็กน้อยตามเดือน เช่น TKT มี Native/CF split เฉพาะบางเดือน — ต้อง cross-validate ทุกครั้ง ห้าม hardcode ตำแหน่งคอลัมน์). PM shut down ตั้งแต่ 15-Jul-2026, MS ไม่ซื้อทั้งปีที่ผ่านมา (data=0 ตลอด) — เป็น pattern ปกติไม่ใช่ error. ข้อมูล 30 วันย้อนหลัง + last-reported-date state เก็บที่ `memory/root-price-history.csv` และ `memory/root-price-last-reported.md`. Dashboard artifact id "root-price-dashboard", scheduled task "root-price-daily-update" (จ-ศ 08:30-18:30 ทุก 1 ชม., หยุดถ้าได้ข้อมูลวันนั้นแล้ว) | 2026-07-24 | ~2027-07 (จนกว่าโครงสร้างไฟล์รายงานจะเปลี่ยน) | Por ยืนยันแล้ว, cross-check ตัวเลข 5 โรงงานผ่าน 2 ตารางอิสระในไฟล์ตรงกัน 100% |
| ราคาตลาด external หัวมันสำปะหลัง — แหล่งข้อมูลที่ใช้ได้จริง | สศก. (oae.go.th) ปิดปรับปรุงระบบ (ณ 24-Jul-2026), rakakaset.com ถูก IT บล็อก (high-risk). แหล่งที่เปิดได้จริง: nettathai.org (สมาคมโรงงานผู้ผลิตมันสำปะหลัง ภาคตะวันออกเฉียงเหนือ) — มีแค่ราคาที่ "พิมาย นครราชสีมา" ตรงกับ PM เท่านั้น โพสต์ไม่สม่ำเสมอ (ทุก 2-3 วัน). thaitapioca.org (สมาคมโรงงานผลิตภัณฑ์มันสำปะหลังไทย, ระดับประเทศ) error ตอนเช็ค ลองใหม่ได้ในอนาคต | 2026-07-24 | เช็คซ้ำทุก ~1-2 เดือน (เว็บ สศก. อาจกลับมาใช้งานได้) | Por ขอให้หาแหล่ง external, confirmed ใช้ nettathai ไปก่อนพร้อม caveat |
