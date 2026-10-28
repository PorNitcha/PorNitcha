# -*- coding: utf-8 -*-
import sys, io, os

path = os.path.expanduser("~/mnt/lovely/Daily root dashboard - 27 September 2026.html")
with io.open(path, encoding="utf-8") as f:
    content = f.read()

pairs = []

pairs.append(('''    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; 27-Sep: ยังไม่มีผลโม่เข้าเลยสักโรง (TN/TKT/PM/TDC = default, MS = ไม่มีข้อมูล)</b> &middot; <b>TDC ไม่มีการซื้อ (forecast, volume ว่าง)</b> &middot; <b style="color:#166534">&#10003; ปิดผลโม่ย้อนหลัง TKT+PM ครบ 25-Sep และ 26-Sep แล้ว (TKT 102.9%/102.1% &rarr; CAG 16.77/16.65 &middot; PM 100.2%/100.8% &rarr; CAG 17.11/16.92)</b> &middot; <b style="color:#b45309">&#9888; TN/TDC ค้างผลโม่ต่อเนื่อง 4 วัน เกินกรอบปกติ 1&ndash;3 วันแล้ว</b></span><br>''',
'''    <span style="color:#9ca3af"><b style="color:#b45309">&#9888; 27-Sep: ยังไม่มีผลโม่เข้าเลยสักโรง (TN/TKT/PM/TDC = default, MS = ไม่มีข้อมูล)</b> &middot; <b style="color:#166534">&#10003; ปิดผลโม่ย้อนหลัง TKT+PM ครบ 25-Sep และ 26-Sep แล้ว (TKT 102.9%/102.1% &rarr; CAG 16.77/16.65 &middot; PM 100.2%/100.8% &rarr; CAG 17.11/16.92)</b> &middot; <b style="color:#b45309">&#9888; TN ค้างผลโม่ต่อเนื่อง 4 วัน &middot; TDC ค้างผลโม่ต่อเนื่อง 5 วัน (23&ndash;27-Sep) &mdash; เกินกรอบปกติ 1&ndash;3 วันแล้วทั้งคู่</b></span><br>'''))

pairs.append(('''    อัปเดตเมื่อ: 28-Sep-2026 08:12 น. (อ่านไฟล์ต้นทางไทยรอบ 08:12 น. &middot; ไฟล์ต้นทางแก้ล่าสุด 27-Sep 21:54 น. &middot; อีเมล TWIC ล่าสุด = ของ 26-Sep เข้า 27-Sep 09:43 น. &mdash; ยังขาดของ 13-Sep, 24-Sep และ 27-Sep (ปกติจะมาพรุ่งนี้))''',
'''    อัปเดตเมื่อ: 28-Sep-2026 09:07 น. (parse ซ้ำหลัง source แก้เพิ่มรอบ 08:54 น. &middot; พบ TDC 27-Sep ซื้อจริง 169 ตัน ซึ่งก่อนหน้านี้เป็น forecast/ว่างเปล่า &middot; ไฟล์ต้นทางแก้ล่าสุด 28-Sep 08:54 น. &middot; อีเมล TWIC ล่าสุด = ของ 26-Sep เข้า 27-Sep 09:43 น. &mdash; ยังขาดของ 13-Sep, 24-Sep และ 27-Sep (ปกติจะมาพรุ่งนี้))'''))

pairs.append(('''<div class="value">1,358<span class="unit">ตัน &middot; <b>TN 490 &middot; TKT 420 &middot; PM 242 &middot; MS 206 &middot; TDC 0 (ไม่ซื้อ)</b> &middot; <b style="color:#166534">&minus;416 (&minus;23.5%) จาก 26-Sep (1,774)</b> &middot; <b style="color:#b45309">ต่ำสุดในรอบ 30 วัน</b></span></div>''',
'''<div class="value">1,527<span class="unit">ตัน &middot; <b>TN 490 &middot; TKT 420 &middot; PM 242 &middot; MS 206 &middot; TDC 169</b> &middot; <b style="color:#166534">&minus;247 (&minus;13.9%) จาก 26-Sep (1,774)</b> &middot; <b style="color:#b45309">ต่ำสุดในรอบ 30 วัน</b></span></div>'''))

pairs.append(('''<div class="value">3.94<span class="unit">&#3647;/กก. (3.9431) &middot; <b style="color:#166534">&minus;0.09 (&minus;2.3%) จาก 26-Sep (4.0351)</b> &middot; ลงชัดเจน</span></div>''',
'''<div class="value">3.96<span class="unit">&#3647;/กก. (3.9616) &middot; <b style="color:#166534">&minus;0.07 (&minus;1.8%) จาก 26-Sep (4.0351)</b> &middot; ลงชัดเจน</span></div>'''))

pairs.append(('''<div class="value">23.50<span class="unit">% &middot; <b style="color:#b45309">&minus;0.70 จุด</b> &rarr; CBG รวม <b style="color:#b45309">16.78 (+0.11)</b> &mdash; ขึ้นเล็กน้อยแม้ราคาลง เพราะ %ST ลดแรงกว่า</span></div>''',
'''<div class="value">23.44<span class="unit">% &middot; <b style="color:#b45309">&minus;0.76 จุด</b> &rarr; CBG รวม <b style="color:#b45309">16.90 (+0.22)</b> &mdash; ขึ้นเล็กน้อยแม้ราคาลง เพราะ %ST ลดแรงกว่า</span></div>'''))

pairs.append(('''<div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = 22-Sep &middot; ไม่รวม MS)</div><div class="value">17.74<span class="unit">&#3647;/กก. (17.737) &middot; <b>4 โรง &middot; 2,985 ตัน</b> &middot; <b style="color:#b45309">27-Sep ยังปิดไม่ได้ &mdash; รอผลโม่ TN/TDC (ค้าง 4 วัน) &middot; TKT/PM รอเฉพาะวันนี้ (ปกติ)</b></span></div></div>''',
'''<div class="kpi"><div class="label">CAG รวม (ล่าสุดที่ครบ = 22-Sep &middot; ไม่รวม MS)</div><div class="value">17.74<span class="unit">&#3647;/กก. (17.737) &middot; <b>4 โรง &middot; 2,985 ตัน</b> &middot; <b style="color:#b45309">27-Sep ยังปิดไม่ได้ &mdash; รอผลโม่ TN (ค้าง 4 วัน) และ TDC (ค้าง 5 วัน) &middot; TKT/PM รอเฉพาะวันนี้ (ปกติ)</b></span></div></div>'''))

pairs.append(('''  <b style="color:#b45309">&#9888; 27-Sep: ยังไม่มีผลโม่เข้าเลยสักโรงในกลุ่มไทย</b> &mdash; TN/TKT/PM/TDC แสดง %Recovery = default เป๊ะ (TN/PM/TDC 100.0% &middot; TKT 95.0%/95.0%/95.0%) &rarr; เว้น CAG/%Recovery ว่างทั้ง 4 โรง &middot; MS แสดง %Recovery 0.0% (ไม่มีข้อมูล เช่นเคย) &middot; <b>TDC ไม่มีการซื้อจริง</b> (แถวในไฟล์ต้นทางเป็น forecast: มีราคา/%Starch แต่ volume ว่าง) &rarr; เว้นทุกช่องเป็น null
  <br><b style="color:#166534">&#128994; ข่าวดี: TKT+PM ปิดผลโม่ย้อนหลังครบ 25-Sep และ 26-Sep แล้ว</b> &mdash; TKT: 25-Sep %Recovery 102.9% (R1 103.0% / R2 102.7%) &rarr; CAG 16.77 &#3647;/กก. &middot; 26-Sep %Recovery 102.1% (R1 103.3% / R2 100.1%) &rarr; CAG 16.65 &#3647;/กก. &middot; PM: 25-Sep %Recovery 100.2% &rarr; CAG 17.11 &middot; 26-Sep %Recovery 100.8% &rarr; CAG 16.92 &middot; verify TKT 26-Sep: CBG 4.08&divide;24.00% = 17.00 ✓ &middot; CAG = 17.00&divide;102.1% = 16.65 ✓ &middot; verify PM 26-Sep: CBG 3.97&divide;23.29% = 17.05 ✓ &middot; CAG = 17.05&divide;100.8% = 16.92 ✓
  <br><b style="color:#b45309">&#128680; TN/TDC ค้างผลโม่เกินกรอบปกติแล้ว</b> &mdash; TN: %Recovery = default (100.0%) ต่อเนื่อง 4 วัน (24, 25, 26, 27-Sep) &middot; TDC: %Recovery = default (100.0%) ต่อเนื่อง 4 วันที่ซื้อจริงล่าสุด (23, 24, 25, 26-Sep) และ 27-Sep ไม่มีการซื้อเลย &mdash; ปกติผลโม่จะมาภายใน 1&ndash;3 วัน ควรตามงานโรงงานทั้ง 2 แห่ง
  <br><b style="color:#b45309">&#128680; ปริมาณซื้อรวม 5 โรง ลดฮวบต่อเนื่อง 2 วัน &mdash; ต่ำสุดในรอบ 30 วัน</b> &mdash; 24-Sep 3,737 &rarr; 26-Sep 1,774 &rarr; 27-Sep <b>1,358 ตัน</b> (&minus;416 ตัน, &minus;23.5% จาก 26-Sep &middot; รวม 3 วันลด &minus;63.7%) &middot; TN/TKT เพิ่มเล็กน้อย (+27 / +32 ตัน) &middot; PM ลด &minus;69 ตัน (&minus;22.2%) MS ลด &minus;88 ตัน (&minus;29.9%) TDC ไม่ซื้อเลย (&minus;318 ตัน, &minus;100%) &mdash; ควรตรวจสอบว่าเป็นผลจากช่วงวันหยุด/เทศกาลหรือ supply ตึงจริง
  <br><b style="color:#166534">&#10003; ราคาเฉลี่ยลงชัดเจน</b> 4.04 (4.0351) &rarr; 3.94 (3.9431) (&minus;0.09, &minus;2.3%) &middot; %ST ลด &minus;0.70 จุด &rarr; CBG รวม 16.67 &rarr; 16.78 (+0.11) &mdash; ขึ้นเล็กน้อยแม้ราคาลง เพราะ %ST ลดแรงกว่าสัดส่วนราคา
  <br><span style="color:#374151">TWIC: ล่าสุดที่มีข้อมูล = 26-Sep &mdash; ราคา 2.88 (&minus;0.20 จาก 25-Sep) ปริมาณ 112 ตัน (&minus;279, &minus;71.4%) %ST 18.98% (&minus;2.45 จุด) %Recovery 0.0% (ไม่มีข้อมูล) &rarr; CAG เว้นว่าง &middot; verify CBG = 2.8841&divide;18.978% = 15.20 ✓ &middot; ยังไม่ส่งของ 27-Sep (ปกติมาวันถัดไป) &middot; ยังขาดของ 13-Sep และ 24-Sep</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติที่ยังไม่ถูกแก้ (ในช่วง 30 วัน): PM 14-Sep 65.3% &middot; PM 20-Sep 82.3% &middot; MS 14-Sep 42.1% &middot; TKT 19-Sep 129.5% (R2 154.8%) &middot; TN 22-Sep 89.2%</b>
  <br><b>&#128680; ค้างผลโม่ (28-Sep 08:12): TN 11-Sep &middot; TN 24&ndash;27-Sep (4 วันติด) &middot; TDC 19-Sep &middot; TDC 23&ndash;26-Sep (4 วันติด) + 27-Sep ไม่มีซื้อ &middot; MS 11, 12, 15, 20, 21-Sep &middot; MS 25&ndash;27-Sep (3 วันติด, ไม่มีข้อมูล) &middot; TKT/PM 27-Sep (รอปกติ 1 วัน)</b> &middot; TWIC 13-Sep และ 24-Sep ยังหาย &middot; <span style="color:#166534">TKT/PM 25&ndash;26-Sep ปิดแล้วรอบนี้</span>''',
'''  <b style="color:#b45309">&#9888; 27-Sep: ยังไม่มีผลโม่เข้าเลยสักโรงในกลุ่มไทย</b> &mdash; TN/TKT/PM/TDC แสดง %Recovery = default เป๊ะ (TN/PM/TDC 100.0% &middot; TKT 95.0%/95.0%/95.0%) &rarr; เว้น CAG/%Recovery ว่างทั้ง 4 โรง &middot; MS แสดง %Recovery 0.0% (ไม่มีข้อมูล เช่นเคย) &middot; <b>แก้ไข: TDC มีการซื้อจริง 169 ตัน</b> (source แก้แถวจาก forecast/ว่างเปล่า เป็นข้อมูลซื้อจริงในรอบนี้ &mdash; ราคา 4.11 %ST 23.02% แต่ %Recovery ยังเป็น default 100.0% เหมือนโรงอื่น) &rarr; volume/price/%ST ใช้ค่าจริง เว้นเฉพาะ CAG/%Recovery เป็น null
  <br><b style="color:#166534">&#128994; ข่าวดี: TKT+PM ปิดผลโม่ย้อนหลังครบ 25-Sep และ 26-Sep แล้ว</b> &mdash; TKT: 25-Sep %Recovery 102.9% (R1 103.0% / R2 102.7%) &rarr; CAG 16.77 &#3647;/กก. &middot; 26-Sep %Recovery 102.1% (R1 103.3% / R2 100.1%) &rarr; CAG 16.65 &#3647;/กก. &middot; PM: 25-Sep %Recovery 100.2% &rarr; CAG 17.11 &middot; 26-Sep %Recovery 100.8% &rarr; CAG 16.92 &middot; verify TKT 26-Sep: CBG 4.08&divide;24.00% = 17.00 ✓ &middot; CAG = 17.00&divide;102.1% = 16.65 ✓ &middot; verify PM 26-Sep: CBG 3.97&divide;23.29% = 17.05 ✓ &middot; CAG = 17.05&divide;100.8% = 16.92 ✓
  <br><b style="color:#b45309">&#128680; TN/TDC ค้างผลโม่เกินกรอบปกติแล้ว</b> &mdash; TN: %Recovery = default (100.0%) ต่อเนื่อง 4 วัน (24, 25, 26, 27-Sep) &middot; TDC: %Recovery = default (100.0%) ต่อเนื่อง 5 วัน (23, 24, 25, 26, 27-Sep &mdash; ซื้อจริงทุกวันแล้ว แค่ผลโม่ยังไม่ปิด) &mdash; ปกติผลโม่จะมาภายใน 1&ndash;3 วัน ควรตามงานโรงงานทั้ง 2 แห่ง
  <br><b style="color:#b45309">&#128680; ปริมาณซื้อรวม 5 โรง ลดต่อเนื่อง 2 วัน &mdash; ต่ำสุดในรอบ 30 วัน</b> &mdash; 24-Sep 3,737 &rarr; 26-Sep 1,774 &rarr; 27-Sep <b>1,527 ตัน</b> (&minus;247 ตัน, &minus;13.9% จาก 26-Sep &middot; รวม 3 วันลด &minus;59.1%) &middot; TN/TKT เพิ่มเล็กน้อย (+27 / +32 ตัน) &middot; PM ลด &minus;69 ตัน (&minus;22.2%) MS ลด &minus;88 ตัน (&minus;29.9%) TDC ลด &minus;149 ตัน (&minus;46.9%, ซื้อจริง 169 ตัน หลัง backfill) &mdash; ไม่ใช่ pattern วันอาทิตย์ปกติ (13-Sep และ 20-Sep ซึ่งเป็นวันอาทิตย์ก่อนหน้า มีปริมาณ 3,903 และ 2,936 ตัน) &mdash; ควรตรวจสอบว่าเป็นผลจากช่วงวันหยุด/เทศกาลหรือ supply ตึงจริง
  <br><b style="color:#166534">&#10003; ราคาเฉลี่ยลงชัดเจน</b> 4.04 (4.0351) &rarr; 3.96 (3.9616) (&minus;0.07, &minus;1.8%) &middot; %ST ลด &minus;0.76 จุด &rarr; CBG รวม 16.67 &rarr; 16.90 (+0.22) &mdash; ขึ้นเล็กน้อยแม้ราคาลง เพราะ %ST ลดแรงกว่าสัดส่วนราคา
  <br><span style="color:#374151">TWIC: ล่าสุดที่มีข้อมูล = 26-Sep &mdash; ราคา 2.88 (&minus;0.20 จาก 25-Sep) ปริมาณ 112 ตัน (&minus;279, &minus;71.4%) %ST 18.98% (&minus;2.45 จุด) %Recovery 0.0% (ไม่มีข้อมูล) &rarr; CAG เว้นว่าง &middot; verify CBG = 2.8841&divide;18.978% = 15.20 ✓ &middot; ยังไม่ส่งของ 27-Sep (ปกติมาวันถัดไป) &middot; ยังขาดของ 13-Sep และ 24-Sep</span>
  <br><b style="color:#b45309">&#128680; ค่าผิดปกติที่ยังไม่ถูกแก้ (ในช่วง 30 วัน): PM 14-Sep 65.3% &middot; PM 20-Sep 82.3% &middot; MS 14-Sep 42.1% &middot; TKT 19-Sep 129.5% (R2 154.8%) &middot; TN 22-Sep 89.2%</b>
  <br><b>&#128680; ค้างผลโม่ (28-Sep 09:07): TN 11-Sep &middot; TN 24&ndash;27-Sep (4 วันติด) &middot; TDC 19-Sep &middot; TDC 23&ndash;27-Sep (5 วันติด, ซื้อจริงทุกวันแล้ว) &middot; MS 11, 12, 15, 20, 21-Sep &middot; MS 25&ndash;27-Sep (3 วันติด, ไม่มีข้อมูล) &middot; TKT/PM 27-Sep (รอปกติ 1 วัน)</b> &middot; TWIC 13-Sep และ 24-Sep ยังหาย &middot; <span style="color:#166534">TKT/PM 25&ndash;26-Sep ปิดแล้วรอบนี้</span>'''))

pairs.append(('''    <tr><td><span class="plant-name">บ้านฉาง ระยอง</span><br><span class="plant-code">TDC</span></td>
      <td class="num">&mdash;</td><td class="num"><span class="dot grey"></span><span class="delta flat">&mdash;</span></td>
      <td class="num">0</td><td class="num">&mdash;</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge none">ไม่ซื้อ</span><span class="status-detail">ไม่มีการซื้อ 27-Sep (แถวในไฟล์ต้นทางเป็น forecast &mdash; volume ว่าง) &rarr; เว้นทุกช่องเป็น null &middot; ผลโม่ค้างต่อเนื่องตั้งแต่ 23-Sep (4 วันซื้อจริงล่าสุด) &mdash; เกินกรอบปกติ 1&ndash;3 วันแล้ว</span></td></tr>''',
'''    <tr><td><span class="plant-name">บ้านฉาง ระยอง</span><br><span class="plant-code">TDC</span></td>
      <td class="num">4.11</td><td class="num"><span class="dot green"></span><span class="delta down">&minus;0.10</span></td>
      <td class="num">169</td><td class="num">23.02</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="badge wait">รอผลโม่</span><span class="status-detail">แก้ไข: มีการซื้อจริง 169 ตัน (source แก้จาก forecast เป็นข้อมูลซื้อจริงแล้ว) &middot; %Recovery แสดง 100.0% เป๊ะ = ค่า default &rarr; ยังไม่มีผลโม่ &middot; ค้างต่อเนื่อง 5 วันแล้ว (23&ndash;27-Sep) &mdash; เกินกรอบปกติ 1&ndash;3 วัน</span></td></tr>'''))

pairs.append(('''    <tr class="total-row"><td>รวมโรงงานไทย (27-Sep &mdash; 5 โรง)</td><td class="num">3.94</td><td class="num"><span class="dot green"></span><span class="delta down">&minus;0.09</span></td>
      <td class="num">1,358</td><td class="num">23.50</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="status-detail">ราคา/%ST ถ่วงน้ำหนัก 5 โรง (TDC ไม่มีซื้อ) &middot; CBG 16.78 (+0.11) &middot; <b>CAG รวมยังปิดไม่ได้ (รอผลโม่ TN/TDC ค้าง 4 วัน)</b> &middot; อ้างอิงล่าสุดที่ครบ = 22-Sep 17.74 &middot; <b style="color:#b45309">ปริมาณรวมต่ำสุดในรอบ 30 วัน ลดต่อเนื่อง 2 วัน</b></span></td></tr>''',
'''    <tr class="total-row"><td>รวมโรงงานไทย (27-Sep &mdash; 5 โรง)</td><td class="num">3.96</td><td class="num"><span class="dot green"></span><span class="delta down">&minus;0.07</span></td>
      <td class="num">1,527</td><td class="num">23.44</td><td class="num">&mdash;</td><td class="num">&mdash;</td>
      <td><span class="status-detail">ราคา/%ST ถ่วงน้ำหนัก 5 โรง (รวม TDC 169 ตันหลัง backfill) &middot; CBG 16.90 (+0.22) &middot; <b>CAG รวมยังปิดไม่ได้ (รอผลโม่ TN ค้าง 4 วัน &middot; TDC ค้าง 5 วัน)</b> &middot; อ้างอิงล่าสุดที่ครบ = 22-Sep 17.74 &middot; <b style="color:#b45309">ปริมาณรวมต่ำสุดในรอบ 30 วัน ลดต่อเนื่อง 2 วัน</b></span></td></tr>'''))

pairs.append(('''  ที่มา (internal): SharePoint &mdash; TWPCROOTSOURCINGTEAM / "Daily root purchased report - 09_Sep 2026" (อ่านไฟล์รอบ 28-Sep-2026 08:12 น.) &middot; TWIC: อีเมล put.p@thaiwah.com (รายงานล่าสุด = ของ 26-Sep เข้า 27-Sep 09:43 น. &middot; ยังขาดของ 13-Sep, 24-Sep และ 27-Sep) &middot; ราคาที่แสดงคือราคาที่ %Starch จริงของแต่ละวัน (ไม่ปรับเทียบ 25%) &middot;''',
'''  ที่มา (internal): SharePoint &mdash; TWPCROOTSOURCINGTEAM / "Daily root purchased report - 09_Sep 2026" (อ่านไฟล์ล่าสุดรอบ 28-Sep-2026 09:07 น. &mdash; parse ซ้ำเพราะ source แก้เพิ่มหลัง 08:12 น.) &middot; TWIC: อีเมล put.p@thaiwah.com (รายงานล่าสุด = ของ 26-Sep เข้า 27-Sep 09:43 น. &middot; ยังขาดของ 13-Sep, 24-Sep และ 27-Sep) &middot; ราคาที่แสดงคือราคาที่ %Starch จริงของแต่ละวัน (ไม่ปรับเทียบ 25%) &middot;'''))

missing = []
for i,(old,new) in enumerate(pairs):
    cnt = content.count(old)
    if cnt != 1:
        missing.append((i, cnt))
    else:
        content = content.replace(old, new)

if missing:
    print("PROBLEM at indices (idx,count):", missing)
    sys.exit(1)

with io.open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("ALL", len(pairs), "REPLACEMENTS OK. final length:", len(content))
