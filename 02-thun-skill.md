---
name: thun-costing-supplychain
description: วิเคราะห์ต้นทุน (unit cost, BOM cost, landed cost) และผลกระทบทางการเงินของ supply chain ต่อ margin ใช้เมื่อ Por หรือทีมขอเปรียบเทียบต้นทุน, วิเคราะห์ผลกระทบราคาวัตถุดิบ/ค่าขนส่ง, หรือทำ cost-benefit ของ sourcing/production
---

# Skill: Costing & Supply Chain Finance Analysis (น้องทุน)

## เมื่อไหร่ใช้ skill นี้
- ขอวิเคราะห์ unit cost / BOM cost / landed cost
- ถามผลกระทบราคาวัตถุดิบ หรือค่าขนส่งต่อ margin
- ขอเปรียบเทียบทางเลือก sourcing/production (supplier A vs B, ผลิตเอง vs outsource)

## Input ที่ต้องมีก่อนเริ่ม
- โครงสร้างต้นทุน (BOM / cost sheet) ของสินค้า/บริการที่เกี่ยวข้อง
- ราคาวัตถุดิบ/ค่าขนส่งปัจจุบัน และช่วงที่เปลี่ยนแปลง (ถ้าวิเคราะห์ impact)
- ปริมาณ/volume ที่เกี่ยวข้อง เพื่อคำนวณผลกระทบรวม

**ถ้าโครงสร้างต้นทุนไม่ชัดหรือไม่ครบ → ถามกลับก่อนเสมอ ห้ามสมมติตัวเลขต้นทุนเอง**

## ขั้นตอนการทำงาน
1. รวบรวมโครงสร้างต้นทุนปัจจุบัน แยกตาม component (วัตถุดิบ, แรงงาน, overhead, ขนส่ง)
2. คำนวณ unit cost / landed cost ตาม scope ที่ขอ
3. ถ้าเป็นการวิเคราะห์ผลกระทบ (impact): คำนวณ delta ต่อหน่วย × volume = ผลกระทบรวมต่อ P&L
4. ถ้าเป็นการเปรียบเทียบทางเลือก: จัดตารางเทียบ cost, quality/risk, lead time ของแต่ละทางเลือกให้เห็นชัด
5. เชื่อมโยงตัวเลข operation กับผลกระทบต่อ margin ให้ Por เห็นภาพการเงินชัดเจน
6. Sanity check: unit cost รวมกันต้องเท่ากับ total cost, สัดส่วน component สมเหตุสมผลกับธุรกิจ

## Output format
- Cost breakdown table + สรุปผลกระทบต่อ margin (สไตล์ BCG: คลีน, สีสื่อความหมาย)
- ตารางเปรียบเทียบทางเลือก (ถ้ามี) พร้อมข้อเสนอแนะ
- อธิบายศัพท์เทคนิคให้เข้าใจง่ายโดยไม่ทิ้งความแม่นยำ

## 📓 Lesson Learned Protocol (ทำทุกครั้งหลังจบงาน)
ก่อนปิดงาน ให้เพิ่ม entry ใหม่ต่อท้าย "Lesson Learned Log" ด้านล่างของไฟล์นี้ ตามฟอร์แมต:

```
### [วันที่] — [งานที่ทำ เช่น "เทียบต้นทุน Supplier A vs B"]
- สิ่งที่ทำได้ดี:
- สิ่งที่ควรปรับปรุง/ทำให้เร็วขึ้นครั้งหน้า:
- ข้อมูล/แหล่งข้อมูลที่ขาดหรือต้องขอเพิ่มบ่อย:
- สมมติฐานที่ผิดพลาด (ถ้ามี) และวิธีแก้:
- Action สำหรับงานครั้งถัดไป:
```

---

## Lesson Learned Log
_(ยังไม่มี entry — จะเพิ่มหลังจบงานแต่ละครั้ง)_

### 2026-07-24 — สรุปราคา/ปริมาณซื้อหัวมันรายวัน 5 โรงงาน + trend 30 วัน + external benchmark
- สิ่งที่ทำได้ดี: ไม่เชื่อ text dump ของ Excel ตรงๆ (มีตารางซ้อนกันหลายตาราง คอลัมน์ไม่ตรงกันทุกเดือน) — cross-check ตัวเลขผ่าน 2 ตารางอิสระในไฟล์เดียวกัน (ตาราง "DAILY ROOT PRICE" กับตาราง "Root Purchased (Tons)" ต่อโรงงาน) และเทียบผลรวมกับ MTD summary ก่อนเชื่อตัวเลข ช่วยจับได้ว่า TKT มี column layout ต่างจาก TN/PM/MS/TDC (มี Native/CF split เพิ่ม)
- สิ่งที่ควรปรับปรุง/ทำให้เร็วขึ้นครั้งหน้า: read_resource ของไฟล์นี้ยาวเกิน token limit ทุกครั้ง ต้องอ่านไฟล์ .txt ที่ระบบ save แทนเสมอ — เตรียม flow นี้ไว้ล่วงหน้าจะเร็วขึ้น
- ข้อมูล/แหล่งข้อมูลที่ขาดหรือต้องขอเพิ่มบ่อย: ราคาตลาด external ระดับประเทศแบบรายวัน — สศก.(oae.go.th) ปิดปรับปรุงระบบ, rakakaset.com ถูก IT บล็อก เหลือแค่ nettathai.org ที่ครอบคลุมแค่ PM/พิมาย และโพสต์ไม่สม่ำเสมอ ควรถาม Por ว่ามี subscription data (Bloomberg/Reuters) หรือไม่ถ้าต้องการ benchmark ที่แม่นยำกว่านี้
- สมมติฐานที่ผิดพลาด (ถ้ามี): ไม่มี — ทุกตัวเลขที่รายงานผ่าน cross-validation แล้วก่อนส่ง
- Action สำหรับงานครั้งถัดไป: เช็ค oae.go.th ทุก 1-2 เดือนว่ากลับมาใช้งานได้หรือยัง เพื่อสลับเป็นแหล่ง external หลัก (ครอบคลุมทั่วประเทศ รายวัน ดีกว่า nettathai)

### 2026-07-27 (รอบบ่าย) — Blocked: SharePoint connector ไม่พร้อมใช้งานในรอบนี้
- สิ่งที่ทำได้ดี: ไม่เดา/ไม่สร้างข้อมูลปลอมเมื่อเข้าถึง SharePoint ไม่ได้ — ตรวจสอบด้วย ToolSearch (keyword "sharepoint", "file search", exact UUID เดิม mcp__6e71354d-47b4-495b-a3b4-4096c7a277ed__*) และ mcp__mcp-registry__list_connectors/search_mcp_registry แล้วไม่พบ tool/connector ตัวไหนเลยในรอบนี้ ก่อนสรุปว่า blocked จริง
- สิ่งที่ควรปรับปรุง/ทำให้เร็วขึ้นครั้งหน้า: ยังไม่ทราบสาเหตุที่ connector หายไป (ต่างจากรอบเช้าของวันเดียวกันที่ยังใช้งานได้ปกติ อ้างอิง state file reported 2026-07-27) — ควรแจ้ง Por ให้เช็คสถานะ connector "TWPCROOTSOURCINGTEAM"/SharePoint ใน Cowork settings
- ข้อมูล/แหล่งข้อมูลที่ขาดหรือต้องขอเพิ่มบ่อย: SharePoint connector หายไปทั้งหมดในรอบนี้ (ไม่ใช่แค่ auth หมดอายุ — ไม่มี tool ปรากฏเลย)
- สมมติฐานที่ผิดพลาด (ถ้ามี): ไม่มี — ไม่ได้แตะ CSV/dashboard/state file เลยเพราะไม่มีข้อมูลใหม่ที่ verify ได้
- Action สำหรับงานครั้งถัดไป: รอบถัดไป (ทุก 1 ชม.) ให้ลองใหม่อัตโนมัติ — ถ้า connector กลับมา ให้ทำงานตามปกติ; ถ้ายัง blocked ต่อเนื่องหลายรอบ ให้ escalate เป็นข้อความแยกถึง Por ไม่ใช่แค่ log เงียบๆ

### 2026-07-27 — Catch-up run (state file ค้างที่ 23-Jul, ต้อง backfill 3 วัน 24/25/26-Jul)
- สิ่งที่ทำได้ดี: เจอว่า state file ล้าหลังไป 3 วัน (ไม่ได้รันตั้งแต่ 24-Jul) — จับได้จาก cross-check "latest complete day" ในไฟล์ (26-Jul มี Purchased volume ไม่ว่าง) vs state file (23-Jul) แล้ว backfill ทั้ง 3 วันให้ครบก่อนอัปเดต dashboard/CSV แทนที่จะรายงานแค่วันล่าสุดวันเดียว. จับได้ว่า 27-Jul (วันปัจจุบัน) เป็นแค่ placeholder/template row (ค่า %Starch default ซ้ำกันทุกแถวอนาคต เช่น 20.80%, 18.40%) ไม่ใช่ข้อมูลจริง — ไม่เอามารายงาน
- สิ่งที่ควรปรับปรุง/ทำให้เร็วขึ้นครั้งหน้า: เมื่อต้อง shift กราฟ 30 วันไปข้างหน้า 3 วัน ต้องคำนวณ drop-3-append-3 ทีละ array ต่อโรงงาน (price/volume/starch) ระวัง index ผิดพลาด ควรมี script ช่วยคำนวณแทนการนับมือถ้าข้อมูลเยอะกว่านี้
- ข้อมูล/แหล่งข้อมูลที่ขาดหรือต้องขอเพิ่มบ่อย: nettathai.org โพสต์ 17/20/22/24-Jul แล้วแต่คอลัมน์ "พิมาย" ยังเป็น "-" ต่อเนื่องมาตั้งแต่ 15-Jul — แหล่งนี้ไม่ครอบคลุม PM ในช่วงนี้เลย. ลอง catalog.oae.go.th (เจอจาก WebSearch) แต่ต้อง login เข้าระบบ ไม่ใช่หน้าราคาสาธารณะแบบเดิม จึงยังไม่นับว่า oae.go.th กลับมาใช้งานได้ปกติ
- สมมติฐานที่ผิดพลาด (ถ้ามี): ไม่มี — cross-validate ตัวเลข TN/TKT/PM/MS/TDC ผ่าน 2 ตารางอิสระในไฟล์ (per-plant table vs แถวรวม row 1) ตรงกันทุกวันก่อนรายงาน
- Action สำหรับงานครั้งถัดไป: ติดตาม PM ต่อว่าปริมาณซื้อจะกลับสู่ระดับปกติ (~500-750 ตัน) เมื่อไหร่ หลัง shut down 15-24 Jul แล้วกลับมาซื้อน้อยมาก (69-85 ตัน) 25-26 Jul — ถ้ายังต่ำต่อเนื่องอีกหลายวัน ควรแจ้ง Por เป็นประเด็นแยก

### 2026-07-27 (รอบถัดไป) — Blocked ต่อเนื่องรอบที่ 2: SharePoint connector ยังไม่พร้อมใช้งาน
- สิ่งที่ทำได้ดี: เช็คซ้ำครบทุกช่องทาง (ToolSearch keyword "sharepoint"/"office 365"/UUID เดิม, mcp__mcp-registry__search_mcp_registry) ก่อนสรุปว่า blocked จริง ไม่เดา/ไม่สร้างข้อมูลปลอม ไม่แตะ CSV/dashboard/state file เลย
- สิ่งที่ควรปรับปรุง/ทำให้เร็วขึ้นครั้งหน้า: รอบที่แล้ว (รอบบ่ายก่อนหน้า) log ไว้เงียบๆอย่างเดียว รอบนี้ทำตาม action เดิมที่ตั้งไว้ — เพราะ blocked ต่อเนื่อง 2 รอบในวันเดียวกันแล้ว จึง escalate เป็นข้อความแยกถึง Por แทนการ log เงียบๆ
- ข้อมูล/แหล่งข้อมูลที่ขาดหรือต้องขอเพิ่มบ่อย: SharePoint connector (site TWPCROOTSOURCINGTEAM) หายไปจากรายการ tool/connector ทั้งหมดต่อเนื่อง 2 รอบ — ไม่ใช่ auth expire (ไม่มี tool ปรากฏเลยแม้แต่ตัวเดียว)
- สมมติฐานที่ผิดพลาด (ถ้ามี): ไม่มี
- Action สำหรับงานครั้งถัดไป: ถ้ารอบถัดไปยัง blocked อีก ให้ escalate ซ้ำทุกรอบจนกว่า Por confirm ว่าแก้ไขแล้ว (อย่ากลับไป log เงียบๆ)

### 2026-07-27 15:38 (+07:00) — Blocked ต่อเนื่องรอบที่ 3: SharePoint connector ยังไม่พร้อมใช้งาน
- สิ่งที่ทำได้ดี: เช็คครบทุกช่องทางอีกครั้งตาม action เดิม — ToolSearch keyword "sharepoint"/UUID เดิม mcp__6e71354d-47b4-495b-a3b4-4096c7a277ed__*/"office 365 excel file drive document" และ mcp__mcp-registry__search_mcp_registry + mcp__mcp-registry__list_connectors (ขอ keyword sharepoint/microsoft/office) → ผลลัพธ์ "No installed connectors found" ยืนยันชัดเจนว่า connector หายไปจริง ไม่ใช่แค่ auth หมดอายุ ไม่แตะ CSV/dashboard/state file ตามเดิม
- สิ่งที่ควรปรับปรุง/ทำให้เร็วขึ้นครั้งหน้า: escalate ต่อเนื่องตาม action ที่ตั้งไว้ (ไม่ log เงียบๆ) — ควรพิจารณาแจ้ง Por ว่าถ้า connector ไม่กลับมาภายในวันนี้ ให้หยุด/pause scheduled task ชั่วคราวแทนที่จะปล่อยให้รันแล้ว blocked ซ้ำทุกชั่วโมงโดยไม่มีประโยชน์เพิ่ม
- ข้อมูล/แหล่งข้อมูลที่ขาดหรือต้องขอเพิ่มบ่อย: SharePoint connector (site TWPCROOTSOURCINGTEAM) หายไปต่อเนื่อง 3 รอบในวันเดียวกันแล้ว (บ่าย, รอบถัดไป, และรอบนี้ 15:38)
- สมมติฐานที่ผิดพลาด (ถ้ามี): ไม่มี
- Action สำหรับงานครั้งถัดไป: ถ้ายัง blocked ต่อเนื่องเกิน 3-4 รอบ ให้แนะนำ Por พิจารณา pause scheduled task จนกว่าจะแก้ connector เสร็จ แทนที่จะรันซ้ำเปล่าประโยชน์ทุกชั่วโมง

### 2026-07-27 16:36 (+07:00) — Blocked ต่อเนื่องรอบที่ 4: SharePoint connector ยังไม่พร้อมใช้งาน
- สิ่งที่ทำได้ดี: เช็คซ้ำครบทุกช่องทางตาม protocol เดิม (ToolSearch "sharepoint"/"6e71354d"/"sharepoint_search sharepoint_folder_search read_resource", mcp__mcp-registry__search_mcp_registry, mcp__mcp-registry__list_connectors) → ทุกช่องทางว่างเปล่า/"No installed connectors found" เหมือนเดิม ยืนยัน blocked จริง ไม่แตะ CSV/dashboard/state file ตามเดิม
- สิ่งที่ควรปรับปรุง/ทำให้เร็วขึ้นครั้งหน้า: นี่คือรอบที่ 4 ในวันเดียวกันแล้ว (บ่าย, รอบถัดไป, 15:38, 16:36) — ทำตาม action ที่ตั้งไว้ครั้งก่อน คือ escalate ถึง Por พร้อมแนะนำให้ pause scheduled task จนกว่า IT/Por จะแก้ไข connector เสร็จ
- ข้อมูล/แหล่งข้อมูลที่ขาดหรือต้องขอเพิ่มบ่อย: SharePoint connector (site TWPCROOTSOURCINGTEAM) หายไปต่อเนื่อง 4 รอบติดกันในวันเดียวกัน — ไม่ใช่ auth expire (ไม่มี tool ปรากฏเลยแม้แต่ตัวเดียวทุกรอบ)
- สมมติฐานที่ผิดพลาด (ถ้ามี): ไม่มี
- Action สำหรับงานครั้งถัดไป: แจ้ง Por แบบ escalate ชัดเจนพร้อมข้อเสนอ pause scheduled task รอบนี้ — ถ้า Por ไม่ pause และรอบถัดไปยัง blocked ต่อ ให้ escalate ซ้ำอีกครั้ง

### 2026-07-29 — Connector กลับมาใช้งานได้แล้ว: Catch-up backfill 27-Jul (เติมค่าที่ขาด) + 28-Jul (ใหม่)
- สิ่งที่ทำได้ดี: connector SharePoint กลับมาใช้งานได้ปกติแล้ว (ไม่ต้อง escalate ต่อ) — read_resource ยาวเกิน token limit เหมือนเดิม จึงอ่านไฟล์ .txt ที่ระบบ save ผ่าน bash/python แทน (เร็วกว่า Read ทีละ chunk มาก) แล้วเขียน python script แยก token ด้วย regex `\s{2,}` (เพราะไฟล์นี้ไม่ได้ใช้ tab คั่นจริง ใช้ multi-space) จากนั้นหา anchor ด้วยค่า Root Capacity คงที่ (TN=850,TKT=300,PM=750,MS=700,TDC=400) เพื่อยืนยันตำแหน่ง field "Price" ในแต่ละ plant block ก่อนเชื่อว่าถูกต้อง — cross-check กับตาราง sub-table ปริมาณ/%starch จนตรงกัน 100% ทุกวันก่อนบันทึก ยังคงจับได้ว่าแถว 29-Jul (วันปัจจุบัน) มีแค่ PM ที่เป็นค่าจริง ส่วน TN/TKT/TDC ยังเป็น placeholder (Stock=0 เหมือน 30/31-Jul ที่เป็นอนาคตแน่นอน) จึงไม่เอามารายงานเป็น "complete day"
- สิ่งที่ควรปรับปรุง/ทำให้เร็วขึ้นครั้งหน้า: การ parse field แบบ variable-width ต่อ plant (TN/PM=14 fields, TKT=16-18 fields, MS=6-9 fields ขึ้นกับว่ามีการซื้อหรือไม่) เสี่ยง error สูงถ้าทำมือ — ควรเขียน python parser แบบ reusable (หา anchor ด้วย capacity แล้วนับถอยหลัง 3 field ไปหา Price) เก็บไว้ใช้ซ้ำทุกรอบแทนการนับ token มือใหม่ทุกครั้ง
- ข้อมูล/แหล่งข้อมูลที่ขาดหรือต้องขอเพิ่มบ่อย: nettathai.org เช็คใหม่พบโพสต์ 17/20/22/24-Jul แต่คอลัมน์ "พิมาย" ยังเป็น "-" ต่อเนื่องมาตั้งแต่ 15-Jul (กำลังผลิตแถบนั้น <50%) — ยังไม่มี external benchmark ใหม่สำหรับ PM มา >2 สัปดาห์แล้ว ควรแจ้ง Por ชัดเจนว่าแหล่งนี้ไม่ค่อยมีประโยชน์ช่วงนี้
- สมมติฐานที่ผิดพลาด (ถ้ามี): ไม่มี — cross-validate ปริมาณ/%starch ผ่าน 2 ตารางอิสระ (sub-table ต่อโรงงาน vs pivot row 1) ตรงกันทุกวันก่อนรายงาน ราคายืนยันด้วย capacity anchor เช่นกัน
- Action สำหรับงานครั้งถัดไป: ติดตาม TN ที่หยุดซื้อกะทันหันวันที่ 28-Jul (0 ตัน) หลังซื้อต่อเนื่องมาหลายวัน — ถ้ายังหยุดต่อเนื่องอีก 2-3 วัน ควรแจ้ง Por เป็นประเด็นแยก; ติดตาม PM ต่อว่าปริมาณ/ราคาจะนิ่งเมื่อไหร่หลังไต่ขึ้นต่อเนื่อง 5 วันติด (69→85→234→412→129บางส่วน)

### Entry — 6-Aug-2026 18:20 (scheduled run, รอบเย็นที่สอง)
- สิ่งที่ทำได้ดี: run นี้ทำงานถูกจังหวะที่สุด = **ไม่มีข้อมูลใหม่ → ไม่ส่งอีเมล (หยุดเงียบ)** ตาม Rule E. ก่อนตัดสิน verify Sent Items จริง แทนที่จะเชื่อ state ที่ค้าง — พบว่า note ในไฟล์ state เขียน twic_last_sent_date=08-04 พร้อมข้อความว่า "TWIC 5-Aug ยังไม่มาตอนส่ง" แต่พออ่าน body อีเมล 5-Aug (ส่ง 18:18) จริงกลับ **มี TWIC 5-Aug ครบ** (3.25/467t/18.32%/CAG17.83/rec99.6%) → ถ้าเชื่อ state ตรงๆ จะยิงอีเมล "(TWIC updated)" ซ้ำทันที. แก้ state เป็น 08-05 กันพลาด
- บทเรียนหลัก: **state file เชื่อไม่ได้ 100% ถ้าตัวเลข/note ในนั้นขัดกับหลักฐานจริง — ก่อนส่งอีเมลรอบ TWIC-updated ต้อง verify Sent Items ว่ารอบก่อนหน้ามี TWIC วันนั้นไปแล้วหรือยัง** (เพิ่มเป็น pre-check ถาวรของ Rule E ข้อ 2)
- ข้อควรระวังเรื่องวันที่: วันนี้ 6-Aug แต่ไฟล์มีแถว 6-Aug อยู่แล้ว (PM ลงจริง 573t@3.77) — อย่าเผลอเอา 6-Aug มารายงาน เพราะ 6-Aug = วันนี้ (T) ไม่ใช่ T-1. reporting date ต้อง = 5-Aug เสมอ. TN/TKT/TDC ของ 6-Aug ยัง blank/default
- 5-Aug mill result (TN/TKT/TDC) ยัง placeholder (rec 100.0% + CAG=CBG) ถึงเย็น 6-Aug = ผลโม่ช้ากว่าปกติ >1 วัน. อีเมล 5-Aug ส่งไปพร้อม note "Pending mill result" แล้ว (ถูกตาม Rule E: เลย 13:00 ส่งได้พร้อม note) — รอบถัดไปถ้า CAG มาให้ refresh CSV/dashboard ได้เลย (ไม่ต้องส่งอีเมลใหม่เพราะวันไม่เปลี่ยน)
- Action ครั้งถัดไป: ถ้าพรุ่งนี้ (7-Aug run) เห็น CAG ของ TN/TKT/TDC 5-Aug มาแล้ว → อัปเดต CSV+dashboard เงียบๆ ไม่ต้องอีเมล; อีเมลรอบใหม่จะเกิดเมื่อ thai_root_date ขยับเป็น 6-Aug

### 🔎 บทเรียน 7-Aug-2026 — หาไฟล์เดือนปัจจุบันใน SharePoint
- `sharepoint_search` ด้วย query ตรงๆ ("08_Aug 2026" / "Aug 2026") **หาไฟล์เดือนปัจจุบันไม่เจอ** (index ยังไม่ทัน / ไฟล์อยู่ top-level ไม่ใช่โฟลเดอร์ report)
- **วิธีที่ได้ผล:** `sharepoint_search(query="Daily root purchased report", folderName="2026 Daily root report")` → เจอ "08_Aug 2026.xlsx" ที่ top-level ทันที
- read_resource ของไฟล์นี้เป็นแบบ **"Workbook: 16 worksheets" tab-separated** (5,067 บรรทัด เกิน token) → ระบบ save เป็น .txt ใน `.claude/projects/.../tool-results/` (อยู่ใน mnt ที่ bash เข้าถึงได้ผ่าน /sessions/*/mnt/.claude/projects/...) → parse ด้วย python: sheet "Aug" แถว header ที่ col A="Date", data rows 1-Aug..31-Aug, block ต่อโรงงาน = TN(cap850,16คอล) TKT(cap550,มี Recovery Total/Native/CF, 20คอล) PM(cap750) MS(cap700) TDC(cap400)
- **ระวัง bash timeout:** `find /` แบบ wildcard กว้างๆ + grep tabs บนไฟล์บรรทัดยาว → ค้าง 120s ให้ระบุ path ตรงหรือ scope find ให้แคบ

## Lesson 10-Aug-2026 (run 10:12) — TWIC ส่งช้ากว่าปกติ + TKT recovery > 110% เป็นค่าจริง
- **TWIC 9-Aug เข้ามา 09:55** (put.p) — ช้ากว่ากรอบปกติ 10:20-10:40 เล็กน้อย · รอบเช้า 09:17/09:44 ยังไม่มี ต้องเช็คซ้ำรอบสาย
- **TKT 9-Aug %Recovery Total = 114.7% (Native 111.2 / CF 122.6)** — ค่าเกิน 100% เยอะ แต่ **เป็นค่าจริง** เพราะ Total/Native/CF ต่างกันหมด (ตาม A0 TKT exception) ไม่ใช่ placeholder → บันทึกเป็นผลโม่จริง (CAG 16.16 ต่ำเพราะ recovery สูง)
- ย้ำ: อย่าเห็น recovery > 100% แล้วเข้าใจผิดว่าผิดพลาด — โรงงานมี carry-over stock ทำให้ผลผลิตแป้ง/ปริมาณโม่ในวันนั้นสูงกว่าปริมาณซื้อได้ (สังเกตได้จาก CAG < CBG)
- routine: 2 จุดข้อมูลใหม่ (TKT ผลโม่ + TWIC 9-Aug) verify ผ่าน identity ทั้งคู่ · dashboard ต้องเขียนไฟล์ใหม่ลง outputs เสมอ (index.html read-only) แล้ว update_artifact

## Lesson 10-Aug-2026 (รอบ 11:15) — root-price-history.csv เป็น CRLF: sed `$` anchor ไม่ match
- อาการ: `sed -i 's/^...,,$/.../' ` ไม่แก้แถว PM 9-Aug เลย (grep ยังเห็นค่าเดิม) — เพราะไฟล์ลงท้ายบรรทัดด้วย `\r\n` (CRLF) ตัว `$` จึงไปติดหน้า `\r` ไม่ตรง pattern
- ยืนยันด้วย `grep ... | cat -A` เห็น `^M$` ท้ายบรรทัด
- **วิธีที่ได้ผล:** แก้ด้วย line number + เติม `\r` กลับเอง: `sed -i '178s/.*/<new line>\r/' file` แล้ว verify ด้วย `cat -A` ว่ายังมี `^M$` ครบ
- routine round: PM 9-Aug ผลโม่ลง (rec 96.3/CAG 19.00) → 3/4 · ยังไม่ส่งอีเมล (ก่อน 13:00, ขาด TDC) · ทุกอย่างเป็นไปตาม SKILL ไม่มี anomaly อื่น

---
### 📓 Lesson Learned 10-Aug-2026 (run 16:07) — เบราว์เซอร์หลุดตอนถึงคิวส่งจริง + dashboard stale จาก partial run
- **สถานการณ์:** run ก่อนหน้า ~16:00 อัปเดต CSV (เติมผลโม่ TDC 8/9-Aug) แต่ **ไม่ได้เขียน log / ไม่ได้ส่งอีเมล / dashboard อัปเดตไม่ครบ** (KPI ยัง 3/4 แต่ arrays TDC ยัง null,null — ขัดแย้งกันเอง) → เป็น partial run ที่ค้าง
  * **บทเรียน:** อย่าเชื่อว่า CSV = dashboard sync กันเสมอ · ทุกรอบต้อง verify file↔CSV (E2) และเช็ค dashboard ว่าตรงกับ CSV จริง โดยเฉพาะเมื่อ backup timestamp ล่าสุดไม่มี log คู่กัน
- **การ verify ที่ได้ผล:** สคริปต์ python เทียบ file↔CSV ต้องระวัง **awk 1-based vs python 0-based** — รอบแรกใช้ index ผิด (ไม่ลบ 1) เจอ 104 mismatch หลอกๆ (คอลัมน์เลื่อน 1 ช่อง) · แก้เป็น idx=col-1 → 0 mismatch · **เตือนตัวเอง: field index ใน python ต้อง −1 จากเลขคอลัมน์ที่นับแบบ awk**
- **เบราว์เซอร์หลุดตอนถึงคิวส่ง:** 9-Aug ครบ 4/4 + เลย 13:00 = เข้าเงื่อนไขส่งเต็มที่ แต่ `list_connected_browsers`=[] (ลองซ้ำ 2 ครั้งหลังรอ) → ทำตามกฎเป๊ะ: **ไม่ส่ง, ไม่แก้ last_sent_date, แจ้ง Por ในสรุป** (เหมือนเคส 4-Aug ที่เบราว์เซอร์หลุด) — งานที่ไม่ต้องใช้เบราว์เซอร์ (verify CSV + fix dashboard + update artifact) ทำให้เสร็จก่อน เพื่อให้ "พร้อมส่งทันที" เมื่อเบราว์เซอร์กลับมา
- **update_artifact จากไฟล์ dashboard ของ email:** ไฟล์ที่ใช้แนบอีเมล **ไม่มี** cowork-artifact-meta และใช้ chart.js tag แบบเปล่า · ก่อนส่งเข้า update_artifact ต้อง (1) แทรก meta block หลัง `<!DOCTYPE html>` (2) เปลี่ยน chart.js เป็น tag เต็มที่มี integrity+crossorigin ตามที่ tool บังคับ · เขียนลง outputs (ระวังพิมพ์ session-id path ผิด — เคยพลาด ENOENT) แล้ว verify_artifact

### Lesson Learned — 13-Aug-2026 (run 15:07)
- ไฟล์ Thai xlsx lastModified ขยับ (14:51) แต่ diff จริงอยู่แค่ row live วันนี้ (13-Aug, ไม่ใช่ reporting date) → 10/11/12-Aug ตรง CSV เป๊ะ. บทเรียน: lastModified ใหม่ ≠ reporting data เปลี่ยนเสมอ ต้อง diff field-by-field ก่อนตัดสินใจแตะ CSV. รอบนี้ถูกต้องที่ไม่ backup/ไม่แก้ CSV.
- อีเมล 12-Aug ยัง DUE (เลย 13:00, มีวันค้างตั้งแต่ 9-Aug) แต่ autonomous run คง HOLD ตาม policy เดิม (chart-strip 7-Aug + ผู้รับ 7 คน). GAP สะสม 5 วัน — ต้องให้ Por ส่ง attended พร้อม regen .eml (ตัวเดิม stale). ย้ำ: อย่า auto-advance thai_last_sent_date.

### LL 13-Aug 17:06 (scheduled, autonomous)
- ไม่มีข้อมูลใหม่: 12-Aug (reporting T-1) ตรง CSV เป๊ะ · 13-Aug ยัง live/forecast · TWIC ยัง Aug-12 → ไม่แตะ CSV/dashboard.
- SharePoint search index ล้าหลัง (คืนแต่ไฟล์เก่า ไม่โชว์ 08_Aug) → workaround: read_resource ด้วย path URI `file:///{driveId}/root:/General/2026 Daily root report/Daily root purchased report - 08_Aug 2026.xlsx` (เกิน token → save .txt แล้ว awk ชีต Aug จากบรรทัด 2059).
- อีเมล 12-Aug ยัง DUE แต่ HOLD ต่อ (autonomous ไม่มี Por, OWA ตัด inline chart) — คงกฎเดิมทั้งวัน · GAP ยังไม่ส่งจริงตั้งแต่ 9-Aug.

### LL 13-Aug 18:06 (scheduled, autonomous) — รอบปิดวัน
- ไม่มีข้อมูลใหม่ (รอบที่ 8 ของวัน): Thai xlsx lastModified 14:51:40 BKK คงเดิมเป๊ะ (ไม่ถูกแก้ตั้งแต่รอบ 15:07) · TWIC ยัง Aug-12 (put.p ไม่ส่งใหม่) → ไม่แตะ CSV/dashboard.
- sharepoint_search รอบนี้ **หาไฟล์ 08_Aug เจอ** ด้วย query "Daily root purchased report 08_Aug 2026" + folderName "2026 Daily root report" + fileType xlsx (ก่อนหน้านี้รอบ 17:06 หาไม่เจอ) → index sync ไม่คงที่ ควรลอง query เจาะชื่อไฟล์ก่อน fallback path URI.
- E2 verify ผ่าน (python จาก CSV): ไทยรวม 1,792t / avg 3.852 · TDC CAG 20.48 = CSV · TKT/PM CAG null รอผลโม่ · TWIC 16.38.
- อีเมล 12-Aug ยัง DUE (18:06 > 13:00) แต่ HOLD ต่อ (autonomous, chart-strip risk) — **GAP สะสม 4 วันทำการตั้งแต่ 9-Aug** · ปิดวันแล้วยังไม่มีรอบ attended → ต้องเน้นย้ำให้ Por ส่งเอง. อย่า auto-advance thai_last_sent_date.

### LL 14-Aug 08:18 (scheduled, autonomous) — ข้อมูลใหม่ 13-Aug + ผลโม่หลายวันลงพร้อมกันตอนเช้า
- วันใหม่ (T-1=13-Aug): Thai xlsx lastModified 14-Aug 07:26 BKK → มี 13-Aug ครบ · sharepoint_search query "Daily root purchased report 08_Aug" เจอไฟล์ทันที (index sync วันนี้โอเค) · read_resource เกิน token → save .txt, `awk 'NR>=2059'` ชีต Aug.
- **บทเรียนสำคัญ — sweep revision หลายวัน:** ผลโม่ลงย้อนหลัง **พร้อมกัน 3 จุด** ตอนเช้า: TN 11-Aug (rec 106.2/CAG 15.72), TKT 12-Aug (rec 111.2/CAG 16.63), PM 12-Aug (rec 95.4/CAG 19.12) — ทั้งหมดเดิม null. ⇒ อย่าเช็ค revision แค่ T-2; ต้องกวาด **ทุกวันที่ยัง CAG=null ใน CSV** (เทียบ recovery/CAG กับ file) ทุกเช้า.
- TKT A0 exception ยืนยันใช้ได้: 12-Aug rec Total/Native/CF = 111.2/108.2/119.6 (ต่างกัน=จริง) → เก็บ Total 111.2 · ขณะที่ 13-Aug = 95/95/95 (เท่ากันลงตัว=forecast) → null. แยกได้ชัด.
- **TDC default row:** 13-Aug TDC มี price 3.97 + starch 21.35% แต่ **purch vol ว่าง + TotalSupply=0** = ยังไม่ลงข้อมูลซื้อ/ไม่ซื้อ → เก็บ null ทั้งแถว (ห้ามเอา price default มาใส่). ตั้ง badge "ยังไม่ลงข้อมูล".
- E2 ผ่านหมด (CBG=price÷starch, CAG=CBG÷rec, revisions reconcile). CSV backup .bak23, เลื่อน window 15-Jul→13-Aug. update_artifact สำเร็จ (regen จาก CSV, arrays ตรงของเดิมเป๊ะ + revisions).
- **Email: ไม่ส่ง — ถูกต้องตามกฎ E** (08:18 < 13:00 **และ** CAG 13-Aug ไม่ครบ ทั้ง TN/TKT/PM รอผลโม่). ไม่ใช่การ HOLD เฉยๆ แต่เป็น "ยังไม่ถึงกำหนด" จริงๆ. GAP จริงตั้งแต่ 9-Aug ยังคาอยู่ → รอบ attended/หลัง 13:00 ค่อยส่ง (โชว์ 13-Aug วันเดียว, ข้ามวันค้าง). อย่า advance thai_last_sent_date.

### Lesson Learned — 17-Aug-2026 (run 17:33) · reporting date ต้องไม่เลื่อนตามแถวที่กรอกไม่ครบ
- **สิ่งที่เจอ:** ไฟล์ไทยถูกแก้ 17:13 แล้ว **PM กรอกแถว 17-Aug ล่วงหน้าโรงเดียว** (691t) ขณะที่ TN/TKT/TDC ยังว่าง และ 17-Aug คือ "วันนี้" ไม่ใช่ T-1
- **ความเสี่ยงที่เกือบเกิด:** generator ใช้ `D = dates[-1]` (วันล่าสุดใน CSV) → dashboard/อีเมลจะเลื่อนไป 17-Aug อัตโนมัติ · แล้วกฎ F (เลย 13:00 ส่งได้) จะทำให้ส่งอีเมลตารางเกือบว่าง ห่างจากอีเมล 16-Aug ที่ส่งจริง 16:15 เพียง ~1 ชม.
- **กฎที่เพิ่ม:**
  1. **reporting date = วันล่าสุดที่ "โรงงานที่ซื้อกรอกหัวมันครบ"** ไม่ใช่วันล่าสุดที่มีตัวเลขโผล่มาช่องใดช่องหนึ่ง · แถวที่มีแค่ 1 โรง + consumption ว่าง = ยังไม่ใช่ reporting date
  2. `build_dashboard.py` รับ **arg ที่ 2 = reporting date** เพื่อ pin ไว้ ห้ามพึ่ง `dates[-1]`
  3. ข้อมูลบางส่วนของวันถัดไป **บันทึกลง CSV ได้** (เป็นค่าจริง) แต่ **ห้ามใช้ทริกเกอร์อีเมล**
- **บั๊ก path:** `build_dashboard.py` / `build_hover_charts.py` hardcode `/sessions/stoic-optimistic-edison/...` = session id เก่า → รอบใหม่รันไม่ได้ · แก้เป็น `os.path.dirname(os.path.abspath(__file__))` แล้ว · **บทเรียน: ห้าม hardcode session path ในสคริปต์ที่ต้องรันข้ามรอบ**
- **วิธียืนยันว่าค่าเป็นของจริงไม่ใช่ default (ใช้ซ้ำได้):** เทียบกับแถววันถัดไปที่ยังว่าง (= ชุด default) + cross-check `Expense ÷ ปริมาณ = ราคา` และ `Est.Starch ÷ ปริมาณ = %ST` + `Stock วันนี้ = TotalSupply − Consumption ของเมื่อวาน`

---
### Lesson Learned — 2026-08-17 18:32 (รอบเย็น)
- **รอบที่ข้อมูลไม่เปลี่ยนเลย ก็ยังต้องอ่านไฟล์ต้นทางสดใหม่** (กฎ A5) แล้วค่อยเทียบกับ CSV — ครั้งนี้ตรงกันทุกช่อง จึงไม่แก้ CSV และไม่ rebuild dashboard ประหยัดเวลาไปมาก · เกณฑ์ตัดสิน "ต้อง rebuild ไหม" = มีค่าใดใน CSV เปลี่ยนหรือไม่ ไม่ใช่ "รันรอบใหม่แล้วต้องสร้างใหม่"
- **แถว 17-Aug ที่มีแต่ PM = ยังไม่ใช่วันใหม่** — TN/TKT/TDC โชว์ stock + price/starch default (TN 3.78/22.00%, TKT 3.83/rec 95.0% ลงตัว, TDC 3.97/21.35%) และ **ไม่มี Purchased Volume** → ตามกฎ A1 ห้ามเลื่อน reporting date · ยืนยันซ้ำอีกครั้งว่า signature ของ default คือ "ไม่มี Purchased Volume"
- **TKT คอลัมน์ Starch(%) ในไฟล์ดิบเป็นตัวเลข KG (เช่น 230,991.00) ไม่ใช่ %** เพราะ block TKT มี Native/CF แทรกทำให้ offset เลื่อน → ต้อง**คำนวณ %Starch จาก `price ÷ CBG`** (3.85/18.50 = 20.81%) ตรงกับที่ CSV เก็บไว้ ✓ อย่าอ่านช่องนั้นตรงๆ
- **ยืนยันกฎ A0 ใช้ได้จริง:** TN 16-Aug %Rec = 100.0% พอดี + CAG 17.10 = CBG 17.10 → รอผลโม่ · TDC เช่นกัน (100.0%, 17.57 = 17.57) · ส่วน TKT %Rec Total/Native/CF ต่างกัน (107.8/108.2/106.3) = ค่าจริง ✓
- **ไม่ส่งอีเมลก็ถือว่างานสำเร็จ** — กฎ F ไม่เข้าเงื่อนไขทั้ง 3 ข้อ (วันใหม่ / mill updated / TWIC updated) → บันทึก STATE แล้วรายงาน Por ว่าทำไมถึงไม่ส่ง ดีกว่าส่งซ้ำ
- **ประเด็นค้างที่ต้องตาม:** TDC ค้างผลโม่จริง 3 วัน (14/15/16-Aug ล้วนเป็น rec 100.0% placeholder) · TN ค้าง 16-Aug — สะสมมาหลายรอบแล้ว ควรให้ Por ทักฝ่ายโรงงาน
