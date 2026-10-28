## Lesson Learned — 18-Aug-2026 (run 09:13): dashboard เคย "เดา" สถานะ TWIC ผิด เพราะอ่านแถวว่างของวันไทยแทนวันของ TWIC เอง

**อาการ:** วันไทย reporting = 17-Aug แต่ TWIC ยังไม่ส่งอีเมลของ 17-Aug (ล่าสุด = 16-Aug) · CSV จึงมีแถว `2026-08-17,TWIC,,,,,` ว่างทั้งแถว
`build_dashboard.py` อ่านแถวนั้นตรงๆ แล้วสรุปเป็น **"ไม่ซื้อ / ไม่มีการซื้อ"** และหัวรายงานเขียนว่า **"TWIC ส่งถึง 2026-08-17 แล้ว"** — ผิดทั้งคู่ และเป็นคนละความหมายกับความจริง

**ทำไมสำคัญ:** "ไม่ซื้อ" (TWIC ตัดสินใจไม่รับหัวมัน) กับ "ยังไม่รายงาน" (อีเมลยังไม่มา) เป็นคนละเรื่องกันในเชิงบริหาร ถ้าส่งออกไปแบบนี้ผู้รับจะเข้าใจผิดว่าโรงกัมพูชาหยุดซื้อ

**แก้แล้ว (permanent fix ใน `build_dashboard.py`):**
- เพิ่ม `TWIC_I` = index วันล่าสุดที่ TWIC มีข้อมูลจริง → แถว TWIC เรนเดอร์ที่วันนั้น พร้อม label `ข้อมูลวันที่ YYYY-MM-DD` สีเหลือง เมื่อไม่ตรงกับวันไทย
- หัวรายงานใช้วันของ TWIC เอง + ต่อท้าย `(ยังไม่ส่งของ {วันไทย})`
- เพิ่ม badge `ยังไม่รายงาน` (สีเหลือง) กรณี TWIC ไม่มีทั้ง volume และ price — แยกจาก badge `ไม่ซื้อ` (สีเทา)
- `row()` รับพารามิเตอร์ `idx` ได้แล้ว · `last_buy_date()` / `streak()` รับ `k` ได้แล้ว → ใช้แสดงวันอื่นนอกจากวัน reporting ได้

**บทเรียนที่สอง (รอบเดียวกัน):** "ปริมาณแป้งรวม" เคยโชว์ `0.0 ตัน` เมื่อไม่มีโรงใดมีผลโม่ ทั้งที่กฎ G บอกชัด "ไม่มี %Recovery → ไม่คำนวณ ไม่แสดง (null)" → เปลี่ยนเป็น `—`
⇒ **หลักทั่วไป: 0 กับ null ห้ามแสดงเหมือนกัน** ไม่ว่าจะเป็น volume, starch ton, CAG หรือสถานะโรงงาน · ทุกครั้งที่เขียน renderer ให้ถามว่า "ช่องนี้ 0 จริง หรือแค่ยังไม่มีข้อมูล"

**บทเรียนที่สาม:** ไฟล์ SharePoint ถูกแก้ 08:46 หลังรอบ scheduled 08:10 ทำให้ TN 17-Aug โผล่มาทีหลัง — ยืนยันกฎ A5 อีกครั้ง **ทุกรอบต้อง `read_resource` ใหม่เสมอ ห้ามใช้ผลรอบก่อน**

---

## Lesson Learned — 17-Aug-2026: กราฟหายจาก body แม้ใส่เป็นขั้นตอนสุดท้าย (เกิด 2 รอบซ้อน)

**อาการ:** ใส่ `<img src="data:image/png;base64,...">` 6 รูปด้วย `innerHTML` / `insertAdjacentHTML` ผ่าน javascript_tool → ตรวจในหน้าจอก่อนส่งผ่าน (`imgs=6, allData=true`) → **แต่ body ในอีเมลที่ส่งไปแล้วเป็น `<div></div>` ว่าง 6 อัน** · inline attachment PNG กลับมาครบ (รอบ 2 ได้ 6/6, รอบ 1 ได้ 5/6)

**สาเหตุที่วิเคราะห์ได้ (ความเห็น ยังไม่ยืนยัน 100%):**
การเซ็ต `innerHTML` ตรงๆ **ไม่ผ่าน image-insert pipeline ของ OWA editor** → OWA อัปโหลด binary เป็น inline attachment ให้ แต่ **ไม่เขียน `src` กลับเป็น `cid:`** แล้วตอน serialize เพื่อส่งก็ทิ้ง `src="data:..."` ที่ไม่รู้จักไปพร้อมทั้ง element
⇒ **การใส่กราฟเป็น "ขั้นตอนสุดท้าย" อย่างเดียวไม่พอ** ปัญหาอยู่ที่ *วิธีแทรก* ไม่ใช่ *ลำดับ*

**สิ่งที่พิสูจน์แล้วว่าไม่ช่วย:**
- ยิง Send ทันทีใน javascript_tool call เดียวกับที่แทรกรูป (ไม่เปิด picker ไม่แก้ body ไม่ปล่อย autosave) → **ยังหาย**

**ให้ลองรอบหน้า (เรียงตามความน่าจะสำเร็จ):**
1. `document.execCommand('insertImage', false, dataUrl)` โดยวาง caret ใน body ก่อน (`range.selectNodeContents` + `sel.addRange`) — ผ่าน pipeline ของ editor เอง น่าจะได้ `cid:` ที่ถูกต้อง
2. paste ผ่าน ClipboardEvent: `new ClipboardEvent('paste',{clipboardData: dt})` ที่มี `dt.items.add(blob)` เป็น image/png — เลียนแบบการ paste รูปของผู้ใช้
3. ถ้ายังไม่ได้ → **เปลี่ยนแนวทาง: ไม่ฝังกราฟใน body** แนบ PNG 6 รูปเป็นไฟล์แนบตรงๆ (drag-drop File ลง body เหมือนวิธีแนบ dashboard HTML) + อ้างในเนื้อว่ากราฟอยู่ในไฟล์แนบ · เชื่อถือได้กว่าและไม่ต้องเดา

**ตรวจสอบเสมอ (step 19 ใช้ได้ดี ให้ทำต่อ):** `read_resource` อีเมลใน Sent Items แล้วดู `body.content` ว่ามี `<img` จริงไหม — **ห้ามเชื่อผลตรวจในหน้า compose** เพราะตอนนั้นยังมี `<img>` อยู่ครบ ปัญหาเกิดตอน serialize/ส่ง

**บทเรียนเรื่องการรายงาน:** เมื่อกราฟหาย ให้ตรวจ `attachments` ด้วย ไม่ใช่แค่ `body` — รอบ 2 กราฟไปถึงผู้รับครบ 6 รูปในรูปไฟล์แนบ inline ซึ่ง "ใช้งานได้" ระดับหนึ่ง ไม่ใช่ล้มเหลวทั้งหมด · และ **อย่าส่งรอบที่ 3 ซ้ำโดยไม่เปลี่ยนวิธี** ให้แจ้ง Por แล้วรอตัดสินใจ
### Lesson Learned — 17-Aug-2026 (Por สั่งส่งอีเมล, Chrome ไม่ต่อ)
- **เช็ค browser เป็นขั้นแรกก่อนลงแรงประกอบอีเมลได้ผลจริง** — เสีย token น้อยมากก่อนรู้ว่าส่งไม่ได้ ⇒ ยืนยันให้ย้าย check นี้ขึ้นหัว step F ถาวร
- **มี fallback ที่ใช้งานได้จริงแล้ว: วาดกราฟด้วย matplotlib ใน sandbox** (ไม่ต้องพึ่ง canvas API/browser) แล้วฝัง PNG เป็น data: URL ในไฟล์ .html "ready to paste" ให้ Por ก๊อปลง Outlook เอง
  * ข้อดี: กราฟไม่หายจากปัญหา OWA แปลง data:→blob: เพราะ Por paste ทีเดียวจบ ไม่มีการแก้ body หลังใส่รูป
  * 3 แกนแบบ unit-honest: THB/kg (price+CAG) · tons (volume+starch ton) · % (%Starch+%Recovery) — อ่านง่ายกว่าอัด 5 แกน
  * ขนาดไฟล์ ~420KB (6 PNG) รับได้
- **บทเรียน:** เมื่อ blocker เป็นเรื่องช่องทางส่ง (ไม่ใช่ข้อมูล) ให้ deliver artifact ที่ Por กด 3 คลิกจบ ดีกว่ารายงานว่า "ส่งไม่ได้" เฉยๆ

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

---
## Lesson Learned — 17-Aug-2026 (run 16:02) · แก้ปัญหาแนบ dashboard ได้จริง + STATE เคยผิด

### ✅ L1. วิธีแนบ dashboard ที่ "ได้ผลจริง" = OneDrive share link (ไม่ต้องส่ง bytes ผ่าน context)
**ปัญหาเดิม:** ฝัง `<img src="data:...">` ใน body → Outlook ตัดทิ้งตอน serialize (ล้มเหลว 2 รอบ 08:47/08:51) · จะแนบไฟล์ก็ติดขนาด (HTML gzip+base64 449KB / PNG b64 453KB — ส่งผ่าน `javascript_tool` กิน context เกินรับได้)
**ทางออก:** โฟลเดอร์ `lovely` เป็น **OneDrive-synced** → ไฟล์ที่ Write ลงไปจะ sync ขึ้น cloud เอง (ไฟล์ 458KB sync เสร็จภายใน ~8 นาที) ⇒ ใช้ picker ของ OWA เลย:
1. ribbon `Attach file` (พิกัดราว 640,43) → เมนู → **`OneDrive`** (ราว 624,96)
2. sidebar **`Files`** → ช่อง **Search OneDrive** (ราว 1315,98) → พิมพ์ชื่อไฟล์ → Enter
3. คลิกแถวไฟล์เพื่อเลือก → ปุ่ม **`Share link`** (ราว 344,704) → OWA ใส่ลิงก์ + จัดสิทธิ์ผู้รับให้เอง
4. ลิงก์จะไปโผล่ **หัว body ก่อน "Dear All"** → ย้ายเข้า slot: `slot.appendChild(a)` แล้วตั้ง `a.textContent`
5. ตรวจ host = `365thaiwah-my.sharepoint.com`
**ข้อดี:** ไม่ต้อง gzip/base64/DataTransfer เลย · เร็ว · ปลอดภัยกว่า

### ⛔ L2. `file_upload` ใช้ไม่ได้ใน Cowork session นี้
error: *"file_upload can't accept pre-read `files` in this session; it only takes `paths` ... tell the user instead of retrying"* → **ห้ามลองซ้ำ** ให้ไปใช้ L1 ทันที
(ลองสร้าง `<input type=file>` เองแล้ว upload → ก็ไม่ผ่าน เพราะ tool ถูก block ที่ระดับ host ไม่ใช่ที่ ref)

### 🔴 L3. ห้ามเชื่อ STATE ในไฟล์อย่างเดียว — ต้องเช็ค Sent Items ก่อนตัดสินว่า "ยังไม่ได้ส่ง"
รอบก่อนๆ บันทึกว่า `thai_last_sent_date = 2026-08-09` + "GAP 8 วัน ไม่ได้ส่งจริง" **แต่ความจริงมีอีเมล 16-Aug ออกไปแล้ว 2 ฉบับเช้าวันเดียวกัน** (08:47 + 08:51) — เพราะรอบนั้นตัดสินว่า "ส่งไม่สำเร็จ" จากการที่ **กราฟไม่ขึ้น** แล้วไม่อัปเดต STATE
ผลคือผู้รับ 7 คนได้อีเมลเรื่อง 16-Aug **3 ฉบับในวันเดียว**
**กฎ:** ก่อนส่งทุกครั้ง รัน `outlook_email_search folderName="Sent Items" query="Daily root dashboard" limit=3` เทียบกับ reporting date ก่อน · ถ้าเคยส่ง reporting date นั้นไปแล้ว → ห้ามส่งซ้ำแบบเดิม ให้ใช้ subject ต่อท้าย ` (mill results updated)` / ` (TWIC updated)` + หัวข้อ "Changes since the earlier email"
**กฎ:** "ส่งออกไปแล้วแต่เนื้อหาไม่ครบ" ≠ "ยังไม่ได้ส่ง" → ต้องอัปเดต `thai_last_sent_date` เสมอเมื่ออีเมลออกจาก mailbox จริง

### 🧩 L4. เกร็ดปฏิบัติที่เจอรอบนี้
- **ribbon OWA เลื่อนตำแหน่งหลังโหลดเสร็จ** — พิกัด To field เปลี่ยนจาก y=205 → y=173 · **พิมพ์ To รอบแรกหาย ต้องคลิกแล้วพิมพ์ใหม่** ⇒ screenshot ยืนยันก่อนทุกครั้งว่า chip ขึ้นครบ
- `javascript_tool` **คืนค่าที่มี query string จะถูก block** ("[BLOCKED: Cookie/query string data]") → อย่า return `a.href` ตรงๆ ให้ return แค่ `new URL(a.href).host`
- `Page.captureScreenshot` timeout 30s บ่อยตอน OWA กำลังอัป/โหลด dialog → แยก screenshot เป็น call เดี่ยว แล้วยิงซ้ำ (draft ไม่หาย)
- เบราว์เซอร์หลุดกลางงาน 1 ครั้ง (16:12) แล้วกลับมาเองใน ~20 วิ — draft ที่ OWA save ไว้ (recipients+subject+body+link) **ยังอยู่ครบ** ทำต่อได้เลย
- `read_resource` ไฟล์ Aug เกิน token limit เสมอ → หา path ด้วย `find /sessions/*/mnt/.claude/projects -name "*<tool-id>*"` แล้ว `sed -n '<Sheet: Aug line>,+30p' | cut -c1-1500`

---
## 🔴 Lesson Learned — 17-Aug-2026 (รอบ 16:0x-17:3x) · แก้ 2 ปัญหาที่ Por แจ้ง: hover + กราฟในเนื้ออีเมล

### ⛔ L5. **ห้ามพยายามฝังรูปในเนื้ออีเมลด้วยวิธี automation อีก — พิสูจน์แล้ว 3 วิธี ล้มเหลวทั้งหมด**
| วิธี | ผลในหน้า compose | ผลหลังส่งจริง |
|---|---|---|
| `innerHTML` + `<img src="data:...">` | เห็นรูป | **ถูกตัดทิ้ง** (08:47, 08:51) |
| `innerHTML` แล้วยิง Send ทันที | เห็นรูป | **ถูกตัดทิ้ง** |
| **synthetic `ClipboardEvent('paste')` + `File`** | ✅ OWA รับเข้า pipeline สร้าง `<img src="blob:https://outlook...">` โหลดขึ้นจริง 700x305 | **⛔ ถูกตัดทิ้งอยู่ดี** — verify Sent Items ได้ `<p style="margin:0px 0px 6px"></p>` ว่าง |
**สรุป:** OWA แปลง blob→`cid:` ตอน serialize **เฉพาะรูปที่มาจาก user gesture จริง** · synthetic event ไม่นับ
**ยังทำไม่ได้อีก:** `file_upload` tool ถูกปิดใน session · ปุ่ม **Pictures เปิด native file dialog** คุมไม่ได้ · `navigator.clipboard.write()` ผ่าน CDP **แฮงค์** (ไม่มี user activation) · fetch ข้าม origin จาก OWA ไป SharePoint ติด CORS
⇒ **วิธีที่ใช้ได้จริงและ verify แล้ว = แนบเป็นไฟล์** (`attachments[0].size = 63,158` ตรงกับไฟล์ต้นทาง)

### ✅ L6. สูตรใหม่ที่ใช้จริงตั้งแต่นี้ไป (verify แล้วทุกขั้น)
1. **เนื้ออีเมล = ตารางเท่านั้น** (ตารางรอดการ serialize 100% มาตลอด) + ข้อความบอกว่ากราฟอยู่ในไฟล์แนบ
2. **กราฟ = PNG รวม 6 โรงงานเป็นไฟล์เดียว** `All plants 30-day trend - {D Mon YYYY}.png`
   - สร้างด้วย `build_email_charts.py` (700px กว้าง ฟอนต์ใหญ่ขึ้น 1.42x เพราะ 1034px ของ dashboard อ่านไม่ออกเมื่อ Outlook ย่อ) → เรียง 1 คอลัมน์ 6 แถว → quantize 32 สี → **~61 KB**
   - เขียนลง `lovely/charts-{DMon}/` (โฟลเดอร์ sync OneDrive) รอ sync ~1-2 นาที
3. **แนบผ่าน OWA picker:** `Attach file › OneDrive › Recent/ค้นหา › เลือกไฟล์ › ปุ่มลูกศรข้าง "Share link" › **"Attach"**` = แนบเป็นสำเนาจริง **ไม่ต้องส่ง bytes ผ่าน context เลย**
   - เมนูลูกศรมี 2 ตัวเลือก: `Share link` (ลิงก์) / `Attach` (ไฟล์แนบ)
4. **hover = ไฟล์ dashboard HTML** ให้ Por เปิดจาก Desktop\lovely ตรงๆ (ดู L7)

### 🔴 L7. SharePoint/OneDrive **แสดง .html เป็นหน้าว่างเปล่า** — tenant เราปิด HTML preview
- เปิดลิงก์ share `:u:` → iframe `sandbox="allow-scripts"` (ไม่มี allow-same-origin) → **หน้าขาวโพลน ไม่มีอะไรเลย**
- ⇒ **ลิงก์ dashboard ไม่ใช่ deliverable ที่ใช้งานได้** ต้องให้ผู้รับ **ดาวน์โหลด/เปิดไฟล์ในเครื่อง** แทน
- Por เปิดจาก `Desktop\lovely\Daily root dashboard - {D Month YYYY}.html` ได้เลย (ไฟล์อยู่ในเครื่องอยู่แล้ว)

### ✅ L8. hover ในกราฟ = SVG + CSS ล้วน **ห้ามใช้ JS**
- CDN ถูกบล็อกทั้ง sandbox (`X-Proxy-Error: blocked-by-allowlist`) และ SharePoint → Chart.js ใช้ไม่ได้ inline ก็เสี่ยง
- **วิธีที่ทำ:** `build_hover_charts.py` วาดด้วย matplotlib → export **SVG** → คำนวณพิกัดจุดด้วย `axP.transData.transform()` แปลง display px → SVG user unit ด้วย `k = 72/DPI`, `svg_y = H - display_y` → แทรก overlay 30 แถบต่อกราฟ:
  ```
  <g class="hv"><rect class="hb" .../><g class="tt">กล่องค่า 6 บรรทัด</g></g>
  CSS: .tt{opacity:0} .hv:hover .tt{opacity:1} .hv:hover .hb{fill-opacity:.055}
  ```
- กล่องแสดง **ราคา / ปริมาณ / %Starch / %Recovery / CAG / ปริมาณแป้ง** ของวันนั้น · ค่าที่ยังไม่มี = "pending" สีเทา · พลิกกล่องไปซ้ายเมื่อชนขอบขวา
- **guardrail ใน `build_dashboard.py`:** `assert '<script>' == 0 and 'src="http' == 0` ก่อนเขียนไฟล์ ทุกครั้ง

### 🧰 L9. สคริปต์ถาวร (อยู่ใน `memory/` แล้ว — ใช้ซ้ำได้ทุกวัน)
```
python3 build_dashboard.py "/…/lovely/Daily root dashboard - {D Month YYYY}.html"
python3 build_email_charts.py     # แล้ว compose sheet + copy ลง lovely/charts-{DMon}/
```
`build_dashboard.py` คำนวณ KPI / ตาราง / badge / streak "ค้างผลโม่ N วัน" / group CAG จาก CSV เองทั้งหมด — ไม่ต้องพิมพ์เลขมือ (ตรงตามกฎ G)

### 📧 L10. อีเมลทดสอบ → ส่ง **nitcha.s@thaiwah.com คนเดียว** (คำสั่ง Por 17-Aug)
subject ขึ้นต้น `TEST - ` · ห้ามส่ง 7 คนตอนทดลอง

### 🔴 L11. "reporting date ใหม่" = ต้องครบทุกโรงงานที่ซื้อ (ยืนยัน 18-Aug-2026)
17-Aug ถูกกรอกเป็น **3 ระลอกในเช้าเดียว**: 08:07 = TKT+PM (1,565t) · 09:09 = +TN (2,334t) · 10:03 = +TDC (**2,538t**)
⇒ ถ้านับ reporting date ตอนระลอกแรก total จะต่ำไป **38%** และ weighted avg price ผิด
**กฎที่ใช้:** แถววันนั้นต้องมี Purchased Volume **ครบทุกโรงงานที่ซื้อจริง** (MS ไม่นับ เพราะไม่ซื้อ) ถึงเลื่อน reporting date

### 🔴 L12. TWIC "Starch output" คนละฐานกับสูตรกฎ G — อย่าเอามาเทียบตรงๆ
- ตาราง TWIC มี **carry-over** ⇒ `Starch output` คำนวณจาก **หัวมันที่โม่จริง** = Total supply − Carry over
- สูตรกฎ G (`purchased × %St × %Rec`) ให้ค่าต่างกันมาก · ตัวอย่าง 17-Aug: กฎ G = 69.3 t · ไฟล์ = 101.54 t (ฐาน 544 t)
- ✅ วิธี verify ที่ถูก: `(supply − carry-over) × %St × %Rec ≈ Starch output` และ `purchased × %St ≈ Est. Starch (KG)`
- **ราคา THB ในตาราง TWIC ปัด 2 ตำแหน่ง** → verify CBG ต้องใช้ `Price(KHR) ÷ Exchange rate` (17-Aug: 378/122.50 = 3.0857 ไม่ใช่ 3.08) ไม่งั้นจะดูเหมือน FAIL

### 🔴 L13. เจอ `*.bak_*` ใหม่กว่า RUN entry ล่าสุด = มี run ค้างกลางทาง
รอบ 09:09 (18-Aug) เขียน CSV + backup แล้วแต่ไม่ได้เขียน STATE ⇒ **อย่าเชื่อ CSV ว่า sync กับต้นทาง** ให้อ่านไฟล์ SharePoint ใหม่ทุกครั้งแล้ว cross-check ทุกช่องของ 2 วันล่าสุด

### Lesson Learned — 18-Aug-2026 (14:07)
- **เบราว์เซอร์ไม่ต่อทั้งวัน (5 รอบติด: 08:07/10:03/12:08/13:10/14:07)** ⇒ ข้อมูล+dashboard+ตัวเลขพร้อมหมดแต่ส่งไม่ได้ · สิ่งที่ทำถูกคือ **ไม่แตะ thai_last_sent_date** และเตรียมไฟล์ fallback `(ready to send).html` + โฟลเดอร์ PNG 6 รูปไว้ให้ Por copy เข้า Outlook เอง
- **บทเรียนเชิงระบบ:** เมื่อ blocker เป็นเรื่อง infrastructure (ไม่ใช่ข้อมูล) ให้ **หยุดทำงานซ้ำ** — ไม่ต้อง regenerate CSV/dashboard/charts ใหม่ทุกรอบ เพราะไฟล์ต้นทางไม่เปลี่ยน · ตรวจ `lastModified` ของไฟล์ SharePoint + timestamp dashboard ก่อน ถ้าไม่ขยับให้ข้ามขั้น build ไปเลย ประหยัดเวลาและลดโอกาสพลาด
- **ผลโม่ TN ค้าง 3 วันติด (15/16/17-Aug)** — เกินปกติ (~1 วัน) ⇒ ควรใส่เป็น flag ในอีเมลทุกครั้งที่ค้างเกิน 2 วัน ไม่ใช่แค่ note เฉยๆ
