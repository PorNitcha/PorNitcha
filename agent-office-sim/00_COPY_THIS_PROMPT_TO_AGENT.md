# คัดลอก prompt นี้ให้ AI ของคุณ (Claude / Codex / ChatGPT)

ใช้เมื่อคุณเพิ่มหรือแก้การ์ดพนักงานใน `employees/*.md` แล้วอยากให้ AI อัพเดตหน้าจอให้

---

```text
คุณคือผู้ดูแล Agent Office Sim ใน repo นี้

งานของคุณ:
1. อ่านการ์ดพนักงานทุกไฟล์ใน employees/*.md (ยกเว้น README.md และ _TEMPLATE.md)
2. อ่าน data/office-config.js เพื่อดู room id ที่มีอยู่
3. อัพเดต data/employees.js ให้ตรงกับการ์ดทุกใบ:
   - id, name, role, avatar, dept, color, personality ตามการ์ด
   - lines = ประโยคติดปากจากการ์ด (3-5 ประโยค)
   - ถ้า dept ในการ์ดไม่มีใน office-config.js ให้ถามฉันก่อนว่าจะเพิ่มห้องใหม่หรือย้ายแผนก
4. ถ้ามีพนักงานใหม่ ให้เพิ่มบทสนทนาที่เข้ากับแผนกของเขาใน data/dialogues.js
   อย่างน้อย 2 topics (ใช้ key เป็นคู่แผนกเรียงตามตัวอักษร เช่น 'hr|sales')
5. ห้ามใส่ข้อมูลอ่อนไหว (เบอร์จริง อีเมลจริง รหัส API) ลงในไฟล์ใด ๆ
6. เสร็จแล้วสรุปว่าเพิ่ม/แก้ใครบ้าง และบอกให้ฉัน refresh หน้า index.html

เริ่มจากรายงานก่อนว่าตอนนี้การ์ดกับ data/employees.js ตรงกันหรือไม่
```

---

## ตัวอย่างการใช้งาน

1. คัดลอก `employees/_TEMPLATE.md` → `employees/somchai.md` แล้วกรอกข้อมูล
2. ส่ง prompt ข้างบนให้ AI (เปิดใช้งานในโฟลเดอร์ repo นี้)
3. AI จะ sync ข้อมูลลง `data/employees.js` + เพิ่มบทสนทนาให้
4. Refresh `index.html` — พนักงานใหม่ปรากฏในออฟฟิศทันที
