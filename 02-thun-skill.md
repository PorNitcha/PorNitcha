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
