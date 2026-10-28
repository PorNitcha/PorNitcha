### Lesson Learned — 17-Aug-2026 (Por สั่งส่งอีเมล, Chrome ไม่ต่อ)
- **เช็ค browser เป็นขั้นแรกก่อนลงแรงประกอบอีเมลได้ผลจริง** — เสีย token น้อยมากก่อนรู้ว่าส่งไม่ได้ ⇒ ยืนยันให้ย้าย check นี้ขึ้นหัว step F ถาวร
- **มี fallback ที่ใช้งานได้จริงแล้ว: วาดกราฟด้วย matplotlib ใน sandbox** (ไม่ต้องพึ่ง canvas API/browser) แล้วฝัง PNG เป็น data: URL ในไฟล์ .html "ready to paste" ให้ Por ก๊อปลง Outlook เอง
  * ข้อดี: กราฟไม่หายจากปัญหา OWA แปลง data:→blob: เพราะ Por paste ทีเดียวจบ ไม่มีการแก้ body หลังใส่รูป
  * 3 แกนแบบ unit-honest: THB/kg (price+CAG) · tons (volume+starch ton) · % (%Starch+%Recovery) — อ่านง่ายกว่าอัด 5 แกน
  * ขนาดไฟล์ ~420KB (6 PNG) รับได้
- **บทเรียน:** เมื่อ blocker เป็นเรื่องช่องทางส่ง (ไม่ใช่ข้อมูล) ให้ deliver artifact ที่ Por กด 3 คลิกจบ ดีกว่ารายงานว่า "ส่งไม่ได้" เฉยๆ

