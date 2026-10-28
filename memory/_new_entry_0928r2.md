

## รอบ 28-Sep-2026 09:07 ICT (r2) — 🟢 UPDATE (correction) · Gate 1 ขยับอีกครั้ง (mtime 27-Sep 21:54 → 28-Sep 08:54) → re-parse พบ TDC 27-Sep backfill จาก forecast/ว่างเปล่า เป็นซื้อจริง 169 ตัน · CSV+dashboard แก้แล้ว · ไม่ส่งอีเมล · แจ้ง Por

### หมายเหตุ housekeeping
- ไฟล์นี้ (`root-price-last-reported.md`) ยาวเกิน 500KB/3,900 บรรทัด จนเกือบชน token limit ตอนอ่านผ่าน bash → **archive รอบก่อน 25-Sep-2026 ทั้งหมดไปที่ `memory/root-price-last-reported-archive.md`** (สำรองไฟล์เต็มไว้ที่ `root-price-last-reported.md.bak_0928r2_full` ก่อน split) เก็บเฉพาะ 25–28 Sep ไว้ในไฟล์หลัก · รอบถัดๆ ไปควร archive ทุก ~1 สัปดาห์เพื่อไม่ให้ไฟล์บวมอีก

### Gate check
| # | Gate | ค่ารอบนี้ | เทียบรอบ 1 (08:12) | ผล |
|---|---|---|---|---|
| 1 | `09_Sep 2026.xlsx` mtime | `2026-09-28T01:54:29.000Z` (08:54 ICT) | `2026-09-27T14:54:38.000Z` (21:54 ICT) | ✅ **ขยับ (+11ชม.)** → re-parse |
| 2 | อีเมล `put.p` ล่าสุด | "on Sep 26, 2026" (rcvd 27-Sep 09:43 ICT) | เท่าเดิม | ⛔ ไม่ขยับ → ไม่ต้องเปิด TWIC attachment ซ้ำ |

`TZ=Asia/Bangkok date` = 2026-09-28 09:07 → `reporting_date` (T-1) = **2026-09-27** (เท่ากับรอบก่อน — dashboard ไฟล์เดิมชื่อถูกต้องแล้ว ไม่ต้องสร้างไฟล์ใหม่)

### Diff เทียบ CSV ปัจจุบัน (5 โรงไทย, 25–27 Sep, verify CBG=price÷%starch ทุกจุด = ผ่านหมด)
- **TDC 27-Sep: เปลี่ยนจาก "ไม่ซื้อ/forecast" (ทุกช่อง null) → ซื้อจริง 169 ตัน** ราคา 4.11 %ST 23.02% → CBG = 4.11÷23.02% = 17.85 ✓ · %Recovery = 100.0% เป๊ะ (default TDC) → ยังเว้น recovery/CAG เป็น null เหมือนเดิม (แค่ volume/price/starch เปลี่ยนจาก null เป็นค่าจริง)
- TN/TKT/PM/MS 25–27-Sep และ TDC 25–26-Sep: ตรงกับ CSV/รายงานรอบก่อนทุกจุด (diff = 0) — ไม่มีผลโม่ปิดใหม่รอบนี้ (TN/TKT(27)/PM(27)/MS ยัง default/no-data เหมือนเดิม)
- ผลกระทบต่อยอดรวม 27-Sep (5 โรง): ปริมาณ 1,358 → **1,527 ตัน** (+169) · ราคาเฉลี่ยถ่วงน้ำหนัก 3.9431 → **3.9616** · %ST เฉลี่ย 23.4956 → **23.4431** · CBG รวม 16.78 → **16.90** (คำนวณจาก CSV ทั้งหมดด้วยสคริปต์ ไม่ได้พิมพ์จากความจำ)
- ปริมาณรวม 27-Sep (1,527) **ยังคงต่ำสุดในรอบ 30 วัน** (รองลงมา 26-Sep = 1,774, 11-Sep = 1,877) — แต่ไม่ได้ดิ่งรุนแรงเท่าที่รายงานไปตอน 08:12 (ตอนนั้น TDC ยังไม่มีข้อมูล)
- CAG รวม (ex-MS) ยังปิดที่ 22-Sep = 17.737 เหมือนเดิม (TN ค้าง 4 วัน, TDC ค้าง 5 วันแล้ว — 23,24,25,26,27-Sep ซื้อจริงครบทุกวันแต่ %Recovery ยังไม่ปิดสักวัน)

### Verify
- CSV: backup → `root-price-history.csv.bak_0928r2` → upsert 1 แถว (2026-09-27,TDC: price 4.11, volume 169, starch 23.02, cag/recovery ว่าง) → รวม **180 data rows เท่าเดิม** (ไม่มีวันใหม่ ไม่ต้อง roll) ✓
- Dashboard `Daily root dashboard - 27 September 2026.html` (สำรอง `memory/Daily root dashboard - 27 September 2026.html.bak_0928r2` ก่อนแก้): แก้ TDC.price[29]/volume[29]/starch[29] ในกราฟ + header banner/timestamp (09:07) + KPI 4 ใบ (ปริมาณ, ราคา, %ST/CBG, CAG-รวม note) + caveat 6 ย่อหน้า + ตาราง TDC (จาก "ไม่ซื้อ" → "รอผลโม่" พร้อมตัวเลขจริง) + total-row + footnote read-time
- Verify: `node --check` ผ่าน (syntax OK) · เทียบทุกจุดในกราฟกับ CSV ด้วยสคริปต์ (30 วัน × 6 โรง × 5 field = 900 จุด) → **mismatch = 0** ✓ · grep หา string เก่าที่ควรหายไปแล้ว (1,358 / 3.9431 / 16.78 / "TDC ไม่มีการซื้อ" ฯลฯ) → ไม่เจอเหลือ ✓ (ป้องกันบั๊ก L-28Sep-r1a ซ้ำ)
- ⚠️ `verify_artifact` / `update_artifact` / `create_artifact`: ยืนยันซ้ำผ่าน ToolSearch + `list_legacy_live_artifacts` — ไม่มีเครื่องมือเหล่านี้ในเซสชันนี้ (มี legacy live artifact id `root-price-dashboard` บน desktop sidebar แต่แก้จากเซสชันนี้ไม่ได้) เหมือนทุกรอบตั้งแต่ 25-Sep r1 → ไม่ escalate ซ้ำ · ไฟล์ .html บน lovely คือ deliverable หลักที่อัปเดตสำเร็จแล้ว

### ไฟล์
- `memory/root-price-history.csv` — อัปเดตแล้ว (180 rows, window 29-Aug→27-Sep, TDC 27-Sep เติมค่าจริงแล้ว)
- `Daily root dashboard - 27 September 2026.html` — แก้ในไฟล์เดิม (ไม่ได้สร้างไฟล์ใหม่ เพราะ T-1 ยังเป็น 27-Sep เหมือนรอบก่อน) · สำรอง `memory/Daily root dashboard - 27 September 2026.html.bak_0928r2`
- `memory/root-price-last-reported.md` — archive เนื้อหาก่อน 25-Sep ไปที่ `root-price-last-reported-archive.md` แล้ว (สำรองเต็มไว้ที่ `.bak_0928r2_full`)
- ไม่ส่งอีเมล / ไม่เปิด compose / ไม่สร้าง .eml ตามกฎข้อ 0 ✓

### State
- `data_updated_through` : **2026-09-27** (ราคา/ปริมาณ/%ST ครบทั้ง 5 โรงไทยแล้ว รวม TDC หลัง backfill · %Recovery/CAG: TKT/PM ปิดถึง 26-Sep, TN ค้าง 4 วัน (24–27), TDC ค้าง 5 วัน (23–27, ซื้อจริงครบทุกวัน), MS ไม่มีข้อมูล 3 วัน)
- `twic_latest` : **2026-09-26** (ไม่เปลี่ยนจากรอบก่อน) · `twic_missing_dates` : **13-Sep, 24-Sep**
- `source_file_mtime_seen` : **2026-09-28T01:54:29.000Z**
- `twic_email_seen` : **on Sep 26, 2026** (ไม่เปลี่ยน)
- `live_artifact_synced_through` : **2026-09-22 (ค้างต่อ — เครื่องมือไม่พร้อมจากเซสชันนี้ ไม่เปลี่ยนจากรอบก่อน)**
- `last_complete_group_cag` : **22-Sep = 17.737 ฿/กก.** (ไม่เปลี่ยน)
- **รอบถัดไป gate** : mtime > `2026-09-28T01:54:29.000Z` หรือ TWIC อีเมล "on Sep 27, 2026"
- แจ้ง Por: ส่ง push notification (TDC 27-Sep backfill เป็นซื้อจริง 169 ตัน แก้ตัวเลขปริมาณ/ราคาเฉลี่ยของ 27-Sep จากที่แจ้งไปตอน 08:12 · TN/TDC ยังค้างผลโม่)

### Lesson Learned
- **L-28Sep-r2a: gate ขยับได้แม้ภายใน ~1 ชั่วโมงหลังรอบก่อนอัปเดตสำเร็จ และอาจมีข้อมูลจริงเปลี่ยน (ไม่ใช่แค่ recalc เฉยๆ)** — รอบนี้พบว่า SharePoint แก้แถว TDC 27-Sep จาก forecast-blank เป็นซื้อจริงภายใน ~1 ชม. หลัง r1 ปิดงาน ต้อง re-parse+diff ทุกครั้งที่ mtime ขยับไม่ว่าจะเพิ่งอัปเดตสำเร็จมากี่นาทีก่อนหน้าก็ตาม (ตรงตาม L-25Sep-r6 เดิม แต่ยืนยันซ้ำว่าใช้ได้แม้ gap สั้นมาก)
- **L-28Sep-r2b: การ "ไม่มีการซื้อ" ในรายงานก่อนหน้าอาจเป็นแค่ backfill ที่ยังมาไม่ถึง ไม่ใช่ fact ถาวร** — เมื่อพบว่าแถว forecast/ว่างเปล่า (volume ว่างแต่มี price/%ST) เปลี่ยนเป็นมีค่า volume จริงในรอบถัดมา ให้ถือเป็นการซื้อจริงที่มาช้า (เหมือนกฎ %Recovery มาช้า) ไม่ใช่แค่ "ไม่ซื้อ" แล้วจบ — ต้องคอย re-check แถว forecast ทุกรอบที่ gate ขยับเช่นกัน
- **L-28Sep-r2c: ไฟล์ log `root-price-last-reported.md` ต้อง archive เป็นระยะ** — ปล่อยไว้ 2 เดือนบวมถึง 518KB/3,899 บรรทัด จน `cat` ผ่าน bash เกือบชน token limit เต็มๆ 2 ครั้งติดตอนเริ่มรอบนี้ → แก้แล้วด้วยการ archive รอบก่อน 25-Sep ออกไปไฟล์แยก แนะนำให้ archive ทุกสัปดาห์จากนี้ (เก็บแค่ ~7 วันล่าสุดในไฟล์หลัก)
