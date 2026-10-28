### Lesson Learned — 17-Aug-2026 (run 14:07)
- **ไฟล์ต้นทางถูก modify แต่ข้อมูลไม่เปลี่ยน** — lastModified ขยับจาก 03:23Z → 06:17Z (13:17 BKK) แต่แถว 14/15/16/17-Aug ทั้ง 6 metric เหมือนเดิมเป๊ะ. **บทเรียน:** lastModified ใหม่ = ต้องอ่านสด (A5) แต่ **ไม่ได้แปลว่ามีข้อมูลใหม่** — ต้อง diff กับ CSV ทุกค่าก่อนสรุป อย่ารีบเขียน CSV/backup ถ้าไม่ต่าง (รอบนี้จึงไม่สร้าง .bak ใหม่ = กันไฟล์บวม)
- **⛔ Blocker ใหม่ที่ยังไม่เคยเจอ: `list_connected_browsers` คืน `[]`** = ไม่มี Chrome extension เชื่อมต่อในรอบ scheduled → step F ทั้งหมด (F12–F19) ทำไม่ได้. **บทเรียน:** ควร **เช็ค browser ก่อน** ลงแรงวาดกราฟ 6 รูป / ประกอบ body (ประหยัด token มาก) — ย้ายการเช็คนี้ไปเป็นขั้นแรกของ step F
- **กฎ 13:00 ทำงานถูกต้อง** — 14:07 > 13:00 + CAG 2/4 ⇒ เข้าเงื่อนไข "ส่งได้พร้อม note รอผลโม่" แต่ติด blocker เบราว์เซอร์ ⇒ ไม่อัปเดต thai_last_sent_date (ถูกต้องตามกฎ "ส่งไม่สำเร็จอย่าอัปเดต state")
- **สัญญาณ default ของแถววันปัจจุบัน (17-Aug) ชัดมาก** ใช้ยืนยัน A0 ได้: total row เป็น `#DIV/0!` + CAG 0.00 + PurchasedVol ว่างทุกโรง + TKT rec = 95.0/95.0/95.0 เท่ากันหมด
- **ประเด็นค้าง (ต้องตามต่อ): TDC ค้างผลโม่ 3 วันติด 14/15/16-Aug** — lag ปกติ 1 วัน ⇒ ผิดปกติ ควรถามฝ่ายโรงงาน TDC


---
## Lesson Learned — 14-Aug-2026 (run 10:20, น้องทุน / root daily)
1. **TDC 13-Aug flip-flop (เข้า 240t แล้วถูกลบภายในนาที):** ไฟล์ต้นทางถูกแก้ 2 ครั้งติด (mod 08:48 ลง TDC 240t → mod 08:49:34 ลบออกกลับเป็นว่าง). รอบ 09:12 อ่านเวอร์ชัน 08:48 (search index lag) เลยบันทึก 240t; รอบ 10:20 อ่านไฟล์สดล่าสุด = TDC ว่าง. **บทเรียน:** ตัวเลขวันเดียวกันเปลี่ยนข้ามรอบได้ — ยึด "ไฟล์ mod ล่าสุด" เป็น truth เสมอ, และ default price (3.97) + volume ว่าง + CBG ว่าง + rec 100.0% = แถว default = **ไม่ได้ลงซื้อ** (default ไม่เคยเขียนทับ volume จริง). เมื่อค่าพลิก ให้ revert CSV/dashboard ตามไฟล์สด + flag ให้ Por.
2. **หา Aug file ยาก:** sharepoint_search ปกติ (query เดือน) ไม่คืน 08_Aug (index lag) และ read_resource folder "report" ตัดรายการที่ 8 (08_Aug = ลำดับ 9 alphabetical จึงหลุด). ไฟล์ Aug อยู่ **ตรงราก .../2026 Daily root report/** ไม่ใช่ใน subfolder report/. **วิธีที่ได้ผล:** query="Daily root purchasing report Recovery TN TKT PM MS TDC" + afterDateTime=วันก่อนหน้า + fileType=xlsx → คืนไฟล์ mod ล่าสุดไฟล์เดียว (itemId ...WQI27B...).
3. **read_resource ไฟล์ใหญ่ (~140KB) เกิน token → save เป็น .txt** ที่ .claude/projects/.../tool-results/ (ไม่ใช่ outputs/ ตรงๆ) — ใช้ `find /sessions/.../mnt -name "mcp-*read_resource*.txt"` หาไฟล์ แล้ว awk 'NR>=<line ของ Sheet: Aug>' ตัดชีต + awk -F'\t' index คอลัมน์ (13-Aug: TN price=$6 vol=$3, TKT $22/$19, PM $42/$39, TDC $74/$71).
4. **/tmp เขียนไม่ได้ (permission) + ลบไฟล์ใน memory/ ไม่ได้ (OneDrive)** — เขียน temp ในโฟลเดอร์ mount, ใช้ `cat a b > main` (overwrite ได้) แต่ `rm`/mv ข้ามอุปกรณ์ไม่ได้. เลี่ยงสร้าง temp ถ้าไม่จำเป็น.
5. artifact read-only ในเซสชัน → เขียนสำเนาแก้ไปที่ outputs/ แล้ว update_artifact ด้วย html_path นั้น (แก้ inline ที่ไฟล์ artifact ตรงๆ ไม่ได้).

## LL 14-Aug-2026 (run 14:07)
- **TDC flip-flop แก้ถาวร:** ไฟล์ 08_Aug lastModified 08:49 ไม่เปลี่ยนทั้งวัน แต่รอบ 10:20–12:07 อ่าน TDC 13-Aug เป็น "ไม่ซื้อ" ผิด — ความจริงมี **240t@4.04/23.70%** มาตั้งแต่เช้า (volume 240t = ค่าจริง ไม่ใช่ default). บทเรียน: volume ที่ไม่ใช่ 0 = ซื้อจริงเสมอ, อย่าเหมาว่า TDC=ไม่ซื้อเพราะ A0 (A0 เตือนเรื่อง %Starch/Recovery/CAG default เท่านั้น ไม่ใช่ volume).
- **เลย 13:00 = อีเมลถึงกำหนดส่งแม้ CAG ไม่ครบ** (note รอผลโม่ TN/TKT/PM/TDC). แต่ autonomous run ส่งเองไม่ได้ (OWA ตัดกราฟ + ไม่มี verify) → HOLD + รายงานให้ Por ส่ง attended. GAP สะสม 9-Aug→14-Aug (5 วัน) ต้องรีบเคลียร์.
- E2 python ผ่าน: รวมไทย 13-Aug = 2,877t, wavg 3.85/21.95%.

## LL 17-Aug-2026 (run 09:55)
- **Windows path ของ tool-results ไม่ mount ใน bash** — รอบนี้ `find /sessions/.../mnt` หาไฟล์ .txt ที่ read_resource save ไว้ **ไม่เจอ** (อยู่ใต้ `C:\...\.claude\projects\...\tool-results\` ซึ่งไม่อยู่ใน mount). วิธีที่ได้ผล: ใช้ **Grep tool** (ไม่ใช่ bash grep) หา `^## Sheet:` และ `^1[4-7]-Aug` บน Windows path ตรงๆ แล้วใช้ **Read tool offset/limit** ดึงแถวที่ต้องการ (แถวยาวมาก Grep จะขึ้น "[Omitted long matching line]" → ต้อง Read). อัปเดต LL#3 ของ 14-Aug: อย่าเสียเวลากับ `find` ใน bash ก่อน — ลอง Grep/Read tool ก่อนเลย.
- **แถวชีต Aug ↔ วันที่:** row 2059 = header "## Sheet: Aug", 13-Aug=line 2078, 14=2079, 15=2080, 16=2081, 17=2082 (วันนี้=forecast default) → mapping = line 2065 + วันที่
- **TWIC inline image เดียวครอบคลุมหลายวัน** — image001.jpg เป็นตาราง 10-16 Aug + MTD ทั้งก้อน จึงอ่านอีเมลฉบับล่าสุดฉบับเดียวพอ ไม่ต้องเปิดย้อนทีละวัน (ประหยัดมาก เวลาข้อมูลค้างหลายวัน)
- **%Recovery = 0.00% ≠ "รอผลโม่"** — TWIC 16-Aug rec 0.00%, CAG #DIV/0!, starch output 0, carry over 244t = **ซื้อแล้วแต่ไม่ได้เดินเครื่องโม่** ต้องแยก wording จาก "รอผลโม่" (ฝั่งไทยที่เป็น default 100.0%) เวลาเขียน dashboard/อีเมล
- **TDC ค้างผลโม่ 3 วันติด (14/15/16-Aug)** — ผิดปกติกว่า lag 1 วัน ควร flag ให้ Por ถามฝ่ายโรงงาน
- **external PM overlay ต้องเลื่อนตามหน้าต่าง 30 วัน** — จุด 15-Jul หลุดออกแล้ว ต้องเปลี่ยนเป็น 3-Aug (3.95 @25%) ไม่งั้นกราฟ PM ไม่มี overlay เลยแบบเงียบๆ
- E2 python ผ่านทุกข้อ: รวมไทย 16-Aug = 2,563t, wavg 3.82 / 21.18%

## LL 17-Aug-2026 (run 10:06)
- **Grep/Read tool workflow ยืนยันใช้ได้ซ้ำ** — ทำตาม LL รอบ 09:55 แล้วเร็วขึ้นมาก: `Grep ^## Sheet:` → `Grep ^(14|15|16|17)-Aug\t` (ได้เลขบรรทัด แม้ขึ้น "[Omitted long matching line]") → `Read offset/limit` ทีละแถว. **mapping line = 2065 + วันที่** ถูกต้อง ตรวจแล้วรอบนี้
- **ต้องอ่านไฟล์สดทุกรอบจริงๆ ถึงจะยืนยันได้ว่า "ไม่มี revision"** — รอบนี้ห่างรอบก่อนแค่ 11 นาที ข้อมูลไม่เปลี่ยน แต่การอ่านสดคือสิ่งเดียวที่พิสูจน์ได้ อย่าข้ามเพราะ "เพิ่งอ่านไป"
- **เช็คแถววันนี้ (T-0) ด้วย** เพื่อกันเข้าใจผิดว่ามีข้อมูลใหม่: 17-Aug มี Stock (TN 1,465 / TKT 170 / TDC 148) แต่ **PurchasedVol ว่าง** + rec default 100.0% + CAG 0.00 ⇒ ยังไม่รายงาน. Stock ≠ Purchase — อย่าอ่านสลับคอลัมน์
- **ไฟล์ temp ใน memory/ ลบไม่ได้จาก bash** (`rm: Operation not permitted`) → เขียน state ให้ใช้ `cat new old > tmp && mv tmp target` ได้ปกติ แต่ไฟล์ `_new_*.md` จะค้างไว้ ไม่กระทบอะไร (มี `_run_*.md` ค้างจากรอบก่อนๆ อยู่แล้ว)
- **GAP อีเมล 8 วัน (9-Aug → 17-Aug) ยังไม่เคลียร์** — สาเหตุเชิงระบบ: scheduled run ส่วนใหญ่ตกก่อน 13:00 + CAG ไม่เคยครบ ทำให้กฎ E บล็อกทุกรอบ. ข้อเสนอถึง Por: ตั้ง scheduled run เพิ่มรอบ ~13:30 หรือผ่อนกฎให้ส่งได้เมื่อ CAG ค้าง > 2 วัน
- E2 python ผ่านทุกข้อ (CBG 4/4 ตรงไฟล์ · รวมไทย 16-Aug = 2,563t · wavg 3.818 / 21.18% · CSV 180 แถว/30 วัน)

### Lesson Learned — 17-Aug-2026 (run 11:05)
- **ไฟล์ต้นทางไทยถูกแก้หลายรอบต่อวันจริง** — รอบ 10:06 อ่านแล้วไม่มี CAG เลย (0/4) แต่ไฟล์ถูก modify อีกครั้ง **10:23 น.** แล้วผลโม่ TKT + PM ลงมา ⇒ ยืนยันกฎ A5: **ต้องเทียบ `lastModifiedDateTime` กับเวลารอบก่อนทุกครั้ง ห้ามข้าม** ถ้าใหม่กว่า = ต้องอ่านสดใหม่ทั้งหมด
- **สัญญาณแยก "ค่าจริง" vs "default" ใช้ได้ผลตาม A0:** PM 16-Aug rec = 97.4% (ไม่ใช่ 100.0 พอดี) และ TKT Total/Native/CF = 107.8/108.2/106.3 (ต่างกัน) ⇒ ค่าจริงทั้งคู่ · TN/TDC ยังเป็น 100.0% พอดี + CAG=CBG ⇒ default
- **`read_resource` ของไฟล์ Excel เกิน token limit** → ระบบเซฟเป็น .txt แต่ path ที่แจ้งเป็น Windows path; ใน bash ต้อง `find /sessions/... -name "*<id>*"` เพราะ path จริงคือ `/sessions/<s>/mnt/.claude/projects/...` (ไม่ใช่ `mnt/outputs/.claude/...`)
- **artifact index.html เป็น read-only ใน session** — Edit ตรงๆ ไม่ได้ ต้อง Write ไฟล์ใหม่ลง outputs แล้วส่ง path นั้นเข้า `update_artifact`
- **`mv` ข้ามอุปกรณ์ไม่ได้** บน mount ของ OneDrive → ใช้ `cp` แทนเวลาเขียนทับไฟล์ memory
- ⚠️ **ไฟล์ `root-price-last-reported.md` บวมถึง ~216 KB / 1,556 บรรทัด** — `cat` ทั้งไฟล์ทะลุ token limit แล้ว ต้อง `head`/`tail` เท่านั้น · **ควรตัดเก็บเฉพาะ ~10 รอบล่าสุด** แล้ว archive ที่เหลือ (เสนอ Por)
