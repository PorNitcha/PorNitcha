## 13-Aug-2026 (scheduled run 10:07) — อัปเดต 12-Aug: TDC ซื้อเพิ่ม + TWIC 12-Aug เข้า · ❌ ไม่ส่งอีเมล (12-Aug CAG ยังไม่ครบ + ก่อน 13:00)

### สถานะรอบนี้
- ✅ อ่านไฟล์ Thai ใหม่ "08_Aug 2026.xlsx" (itemId ...WQI27B..., แก้ล่าสุด **13-Aug 09:21 BKK** ใหม่กว่ารอบ 09:10 ที่ 08:45) — save .txt อ่านชีต Aug ด้วย bash
- **12-Aug มีข้อมูลใหม่ (เทียบรอบ 09:10):**
  * **TDC ซื้อแล้ว 295t @ 3.84 / %ST 20.97% / CBG 18.31** (รอบก่อน Action=Stop/ว่าง) — %Recovery=100.0% default + CAG=CBG=18.31 -> **CAG null (รอผลโม่)**
  * TKT 3.85/829t/20.83% (rec 95/95/95 = forecast -> CAG null) — เหมือนเดิม
  * PM 3.86/668t/21.16% (rec 100.0% default, CAG=CBG=18.24 -> null) — เหมือนเดิม
  * TN vol ว่าง (ยังไม่ลงข้อมูลซื้อ; มี stock 760/price 3.78/ST 22.00% แต่ PurchVol ว่าง = ไม่ซื้อ) · MS ไม่ซื้อ
  * **โรงงานไทยที่ซื้อ 12-Aug = TKT + PM + TDC · ยอดรวม 1,792t · CAG ยังไม่ครบเลย (ทุกโรงงานรอผลโม่)**
- **TWIC 12-Aug เข้าแล้ว** (อีเมล put.p รับ 13-Aug 09:07 BKK): 3.07/463t/17.31%/CAG 16.38/rec 108.19% · MTD vol 4,860 validate ผ่าน
- **10-Aug & 11-Aug ไม่มีรีวิชั่นเพิ่ม** — ตรงกับ CSV ทุกช่อง (E2 cross-check ผ่าน)
- CSV: backup .bak21 -> อัปเดต TDC 12-Aug + เพิ่มแถว TWIC 12-Aug (rolling 30 วัน = 14-Jul->12-Aug, 30 dates) · dashboard artifact updated (ยอดรวมไทย 1,792t) + verify
- E2 cross-check python ผ่าน: TWIC CAG=17.74/1.0819=16.39~16.38 · TDC/TKT/PM CBG ตรง

### CAG alert (step D)
- 10:07 < 12:00 -> ยังไม่ถึงเวลา · ไม่แจ้ง · cag_alert_date คงเดิม 2026-08-10

### Email (rule E) — ไม่ส่ง
- thai reporting 12-Aug > thai_last_sent 9-Aug = มีวันค้าง -> ข้ามไปวันล่าสุด (12-Aug)
- โรงงานที่ซื้อ 12-Aug = TKT, PM, TDC · CAG null ทั้งหมด (TKT forecast / PM+TDC default) -> CAG ไม่ครบ
- 10:07 < 13:00 -> เข้าเงื่อนไข "CAG ไม่ครบ + ก่อน 13:00 -> ยังไม่ส่ง"
- TWIC 12-Aug เข้าแล้ว แต่อีเมลหลักยังไม่เคยส่งตั้งแต่ 9-Aug (ยัง pending) -> ไม่ทำ TWIC-only round · TWIC จะรวมไปตอนส่งจริง
- PENDING: รอบถัดไปหลัง 13:00 หรือเมื่อผลโม่ TKT/PM/TDC 12-Aug ลง -> ส่งอีเมลโชว์ 12-Aug (วันเดียว) + TWIC 12-Aug

### STATE
- thai_last_sent_date : 2026-08-09
- twic_last_sent_date : 2026-08-09
- cag_alert_date      : 2026-08-10
- CSV/dashboard       : current ถึง 12-Aug (10-Aug ครบ+revised, 11-Aug ครบ, 12-Aug: TKT+PM+TDC ซื้อแล้ว CAG รอผลโม่ทั้งหมด, TWIC ครบ)

---
