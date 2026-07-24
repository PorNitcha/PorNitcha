# assets/backgrounds/ — ภาพพื้นหลังออฟฟิศ

ค่าเริ่มต้นของแอปใช้ภาพ `thaiwah-office.png` ในโฟลเดอร์นี้ (จูนพิกัดห้องใน config ให้ตรงกันแล้ว)

ถ้าลบไฟล์ภาพหรืออยากได้ผังแบบเรียบ ให้สลับ `background.mode` เป็น `'builtin'` ใน `data/office-config.js` — แอปจะวาดผังออฟฟิศด้วยโค้ดโดยไม่ต้องมีไฟล์ภาพใด ๆ

## ใช้ภาพของตัวเองแทน

1. เตรียมภาพมุมมองจากด้านบน (top-down) ขนาดแนะนำ **1600×900** (หรือสัดส่วน 16:9)
2. วางไฟล์ไว้ในโฟลเดอร์นี้ เช่น `thaiwah-office.png`
3. แก้ `data/office-config.js`:

```js
background: { mode: 'image', image: 'assets/backgrounds/thaiwah-office.png' },
```

4. Refresh หน้า — ภาพจะกลายเป็นพื้น และห้อง/พนักงานยังแสดงซ้อนด้านบน
5. ปรับพิกัด `rooms` ใน config ให้ตำแหน่งห้องตรงกับภาพของคุณ

## ตัวอย่าง prompt สำหรับ gen ภาพออฟฟิศ (เช่นใน ChatGPT)

```text
Top-down 2D illustration of a modern office floor plan, 16:9,
flat game-art style like a cozy simulation game,
8 rooms around a central corridor: CEO office, meeting room,
finance, pantry, marketing, sales, supply chain, HR,
brand colors deep violet #22155A and cyan #00AEEF on light background,
clean, no text labels, no people
```

เคล็ดลับ: สั่งว่า "no text labels, no people" เสมอ เพราะป้ายชื่อห้องและตัวพนักงานถูกวาดโดยแอปอยู่แล้ว
