// =============================================================
// OFFICE CONFIG — แก้ไฟล์นี้เพื่อเปลี่ยนออฟฟิศของคุณ
// - เปลี่ยนชื่อบริษัท / สีแบรนด์ / แผนก ได้ที่นี่
// - เพิ่มพนักงานที่ data/employees.js
// =============================================================

window.OFFICE_CONFIG = {
  companyName: 'ไทยวา จำกัด (มหาชน)',
  officeName: 'FP&A Virtual Office',
  tagline: 'Por + 3 AI Employees • Management Account · FP&A · Supply Chain Finance & Costing',

  // Thai Wah brand tokens (จาก brand reference pack)
  theme: {
    primary: '#22155A',   // deep violet
    accent: '#00AEEF',    // electric cyan
    charcoal: '#4D4E4E',
    paper: '#f6f5fb',
    wall: '#ffffff',
    floor: '#ece9f6',
    corridor: '#f9f8fd',
  },

  // พื้นหลัง:
  //   mode: 'builtin' = ใช้ผังออฟฟิศที่วาดด้วยโค้ด (พร้อมใช้ทันที ปรับตามจำนวนห้องอัตโนมัติ)
  //   mode: 'image'   = ใช้ภาพของคุณเอง วางไฟล์ใน assets/backgrounds/ (ต้องจูนพิกัด rooms ให้ตรงภาพเอง)
  background: {
    mode: 'builtin',
  },

  world: { width: 1600, height: 900 },

  // แผนก / ห้อง — ทีม FP&A จริง: Por (Finance Director) คุม 3 AI Employees
  // type: 'room' = ห้องทำงานมีโต๊ะ | 'common' = พื้นที่ส่วนกลาง (จุดเดินไปเจอกัน)
  rooms: [
    { id: 'director',    name: 'ห้อง Por (Finance Director)',      icon: '🎯', type: 'room',   x: 30,   y: 25,  w: 600,  h: 340 },
    { id: 'meeting',     name: 'ห้องประชุม FP&A',                  icon: '🤝', type: 'common', x: 660,  y: 25,  w: 500,  h: 340 },
    { id: 'pantry',      name: 'Pantry',                          icon: '☕', type: 'common', x: 1190, y: 25,  w: 380,  h: 340 },
    { id: 'forecast',    name: 'น้องพยาก — Forecast & Variance',  icon: '📊', type: 'room',   x: 30,   y: 540, w: 500,  h: 345 },
    { id: 'costing',     name: 'น้องทุน — Costing & Supply Chain', icon: '💰', type: 'room',   x: 560,  y: 540, w: 500,  h: 345 },
    { id: 'opportunity', name: 'น้องโอกาส — Margin & Growth',      icon: '🚀', type: 'room',   x: 1090, y: 540, w: 480,  h: 345 },
  ],

  // ทางเดินกลาง — พนักงานใช้เดินข้ามแผนก
  corridor: { y: 460 },
};
