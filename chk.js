
const dates = ["14-Sep", "15-Sep", "16-Sep", "17-Sep", "18-Sep", "19-Sep", "20-Sep", "21-Sep", "22-Sep", "23-Sep", "24-Sep", "25-Sep", "26-Sep", "27-Sep", "28-Sep", "29-Sep", "30-Sep", "1-Oct", "2-Oct", "3-Oct", "4-Oct", "5-Oct", "6-Oct", "7-Oct", "8-Oct", "9-Oct", "10-Oct", "11-Oct", "12-Oct", "13-Oct"];

// null = ไม่มีค่าที่มีความหมาย · volume 0 = ไม่ซื้อจริง, null = ยังไม่ลงข้อมูล · TWIC แยกจากยอดไทย
const plants = {
  TN: { label: "TN", fullName: "อ.เมือง อุดรธานี",
    price:  [3.82, 3.86, 3.83, 3.83, 3.86, 3.81, 3.83, 3.81, 3.84, 3.82, 3.83, 3.86, 3.88, 3.88, 3.85, 3.84, 3.84, 3.85, 3.86, 3.87, 3.88, 3.87, 3.86, 3.79, 3.79, 3.76, 3.75, 3.75, 3.75, null],
    volume: [1172, 1072, 918, 585, 705, 581, 928, 929, 1098, 1001, 1106, 976, 463, 490, 756, 732, 805, 958, 971, 1265, 1142, 1049, 750, 602, 739, 862, 779, 821, 687, null],
    starch: [23.52, 24.45, 24.08, 23.98, 24.64, 23.55, 23.79, 23.18, 24.02, 23.51, 23.83, 24.67, 25.01, 24.59, 23.95, 23.73, 24.28, 24.24, 24.56, 25.01, 24.95, 24.7, 24.75, 24.39, 24.37, 24.46, 24.24, 24.38, 24.4, null],
    cag:    [17.54, 15.35, 16.27, 17.22, 16.02, 16.94, 16.71, 16.29, 17.92, 16.67, 15.9, 15.82, 15.97, null, null, 18.68, 16.78, 16.84, 16.46, 16.78, 16.36, 18.21, 16.64, 16.41, 16.32, 16.09, 16.36, 16.05, 14.7, null],
    recov:  [92.6, 102.8, 97.8, 92.8, 97.8, 95.5, 96.3, 100.9, 89.2, 97.5, 101.1, 98.9, 97.1, null, null, 86.6, 94.3, 94.3, 95.5, 92.2, 95.1, 86.0, 93.7, 94.7, 95.3, 95.6, 94.6, 95.8, 104.6, null]
  },
  TKT: { label: "TKT", fullName: "ท่าคันโท กาฬสินธุ์",
    price:  [4.13, 4.15, 4.09, 4.09, 4.1, 4.03, 4.06, 4.02, 4.03, 4.04, 4.05, 4.02, 4.08, 4.08, 4.05, 4.04, 4.02, null, 4.04, 4.01, 4.01, 3.99, 3.96, 3.95, 3.95, 3.93, 3.89, 3.88, 3.89, 3.91],
    volume: [851, 493, 442, 461, 333, 600, 806, 940, 932, 1041, 702, 954, 388, 420, 597, 599, 640, 0, 655, 786, 1183, 1032, 1115, 1002, 968, 964, 580, 473, 755, 871],
    starch: [24.13, 24.27, 23.57, 23.45, 23.5, 22.54, 22.94, 22.32, 22.47, 22.64, 22.87, 23.28, 24.0, 24.17, 23.75, 23.49, 23.27, null, 23.56, 23.02, 23.06, 23.72, 23.24, 23.72, 23.93, 23.56, 23.56, 23.55, 23.72, 24.14],
    cag:    [17.01, 17.1, 16.78, 16.46, 16.61, 13.8, null, 18.34, 17.4, 17.45, 17.29, 16.77, 16.65, 16.28, 17.34, 16.29, 13.55, null, 20.11, 17.36, 16.85, 16.32, 16.79, 16.3, 16.05, 17.41, 16.49, 16.56, 15.36, null],
    recov:  [100.6, 100.0, 103.4, 105.9, 105.1, 129.5, null, 98.2, 103.1, 102.2, 102.4, 102.9, 102.1, 103.7, 98.4, 105.6, 127.5, null, 85.3, 100.4, 103.2, 103.1, 101.5, 102.1, 102.9, 95.8, 100.1, 99.5, 106.8, null]
  },
  PM: { label: "PM", fullName: "พิมาย โคราช",
    price:  [4.2, 4.18, 4.17, 4.13, 4.17, 4.19, 4.17, 4.11, 4.08, 3.98, 3.97, 3.96, 3.97, 3.87, 3.9, 3.93, 3.91, 3.92, 3.91, 3.91, 3.9, 3.81, 3.79, 3.74, 3.73, 3.58, 3.67, 3.7, 3.69, 3.72],
    volume: [740, 783, 730, 830, 773, 397, 821, 844, 683, 516, 1022, 581, 311, 242, 499, 437, 689, 377, 795, 1153, 736, 813, 770, 593, 1260, 488, 706, 398, 367, 511],
    starch: [22.98, 22.48, 22.33, 21.32, 22.37, 22.5, 22.21, 23.13, 22.69, 22.32, 22.28, 23.1, 23.29, 21.4, 21.85, 22.64, 22.37, 21.97, 22.15, 22.1, 22.79, 22.11, 22.72, 22.54, 23.14, 21.71, 22.99, 23.6, 23.44, 24.75],
    cag:    [28.01, 18.12, 18.52, 19.01, 18.51, 18.47, 22.81, 17.15, 17.85, 17.33, 17.68, 17.11, 16.92, null, 17.71, 17.32, 17.4, 17.77, 17.28, 17.07, 16.36, 16.46, 15.58, 15.95, 15.65, 16.36, 15.18, 13.52, 13.52, null],
    recov:  [65.3, 102.6, 100.8, 101.9, 100.7, 100.9, 82.3, 103.6, 100.7, 102.9, 100.8, 100.2, 100.8, null, 100.8, 100.2, 100.4, 100.4, 102.2, 103.7, 104.6, 104.7, 107.1, 104.0, 103.0, 100.8, 105.2, 116.0, 116.5, null]
  },
  MS: { label: "MS", fullName: "แม่สอด ตาก",
    price:  [3.98, 3.99, 3.93, 4.01, 4.02, 3.92, 4.11, 3.98, 4.13, 4.07, 4.21, 4.03, 4.1, 3.9, 3.89, 4.32, 4.05, 4.16, 4.17, 4.19, 4.13, 4.05, 4.16, 4.08, 4.28, 4.17, 4.17, 4.09, 4.08, 4.19],
    volume: [376, 290, 423, 404, 360, 461, 254, 241, 295, 522, 517, 438, 294, 206, 139, 78, 263, 553, 650, 743, 687, 506, 593, 629, 651, 658, 774, 399, 390, 669],
    starch: [24.56, 25.7, 23.67, 23.84, 24.24, 22.29, 25.92, 24.59, 26.48, 25.54, 26.01, 23.79, 25.15, 21.98, 21.51, 28.02, 23.78, 26.28, 26.2, 26.43, 25.69, 25.52, 27.49, 26.54, 28.59, 27.99, 28.11, 27.04, 27.42, 28.68],
    cag:    [38.53, null, 21.28, 18.64, 15.9, 19.08, null, null, 18.5, 17.69, 16.72, null, 20.07, 18.99, null, null, 23.9, 17.49, 17.12, 17.86, 17.94, 17.72, 18.89, 18.67, 16.68, 16.3, 16.28, 16.49, 15.99, null],
    recov:  [42.1, null, 78.0, 90.2, 104.3, 92.2, null, null, 84.3, 90.1, 96.8, null, 81.2, 93.4, null, null, 71.3, 90.5, 93.0, 88.8, 89.6, 89.6, 80.1, 82.3, 89.8, 91.4, 91.1, 91.7, 93.0, null]
  },
  TDC: { label: "TDC", fullName: "บ้านฉาง ระยอง",
    price:  [4.17, 4.06, 4.17, 4.12, 4.24, 4.15, 4.22, 4.25, 4.27, 4.07, 4.21, 4.14, 4.21, 4.11, 4.13, 4.13, 4.16, 4.16, 4.09, 4.06, 3.99, 3.95, 3.86, 3.86, 3.89, null, 3.78, 3.78, 3.76, 3.72],
    volume: [233, 172, 298, 196, 208, 215, 127, 196, 272, 280, 390, 239, 318, 169, 222, 365, 330, 367, 410, 402, 433, 245, 271, 202, 247, 0, 317, 255, 225, 183],
    starch: [23.73, 22.74, 23.64, 24.26, 24.39, 23.65, 23.82, 24.47, 24.7, 22.46, 23.96, 22.76, 23.67, 23.02, 22.7, 22.54, 23.14, 23.41, 23.37, 23.22, 23.59, 24.54, 22.93, 23.73, 24.33, null, 23.53, 23.41, 23.58, 22.47],
    cag:    [17.4, 17.77, 18.14, 17.11, 17.45, null, 18.79, 17.67, 17.87, null, 18.87, 19.38, 18.18, 19.09, 18.84, 19.18, 18.66, 18.8, null, 18.22, 17.6, 17.29, 17.97, 16.61, 16.63, null, 16.1, 16.52, null, null],
    recov:  [101.0, 100.5, 97.3, 99.2, 99.6, null, 94.3, 98.3, 96.7, null, 93.1, 93.9, 97.8, 93.5, 96.6, 95.5, 96.3, 94.5, null, 96.0, 96.1, 93.1, 93.7, 97.9, 96.1, null, 99.8, 97.8, null, null]
  },
  TWIC: { label: "TWIC", fullName: "TWIC กัมพูชา (Oddar Meanchey)",
    price:  [3.29, 3.34, 3.36, 3.36, 3.38, 3.34, 3.27, 3.03, 3.15, 3.08, null, 3.08, 2.88, null, 2.98, 2.99, 3.01, 3.09, 2.87, 2.84, 3.01, 2.8, 2.83, 2.74, 2.75, null, null, null, null, 2.62],
    volume: [325, 222, 388, 490, 511, 497, 460, 304, 357, 360, null, 391, 112, null, 158, 355, 371, 512, 418, 489, 556, 402, 519, 190, 138, null, null, null, null, 70],
    starch: [20.28, 21.45, 19.8, 19.86, 20.36, 20.45, 21.12, 20.2, 20.61, 20.2, null, 21.43, 18.98, null, 20.96, 20.63, 20.44, 20.59, 20.25, 20.01, 21.18, 19.85, 20.4, 20.42, 20.43, null, null, null, null, 19.63],
    cag:    [15.38, 15.35, 16.17, 16.1, 15.94, 15.54, 15.81, 14.97, 16.98, 14.48, null, 15.02, null, null, 13.64, 14.07, 14.21, 14.38, 13.46, 13.25, 13.41, 13.65, 13.87, 13.12, 12.81, null, null, null, null, null],
    recov:  [105.4, 101.62, 104.91, 105.17, 104.27, 105.06, 98.05, 100.28, 90.06, 105.33, null, 95.72, null, null, 104.17, 102.86, 103.82, 104.42, 105.29, 107.29, 106.0, 103.16, 100.02, 102.31, 105.11, null, null, null, null, null]
  },
};

Object.values(plants).forEach(p => {
  p.starchTon = p.volume.map((v, i) =>
    (v === null || !v || p.starch[i] === null || p.recov[i] === null || p.recov[i] === undefined)
      ? null : Math.round(v * (p.starch[i] / 100) * (p.recov[i] / 100) * 10) / 10);
});

const externalPM = dates.map(d => d === '15-Jul' ? 3.60 : null);

function isolatedPt(arr, r) {
  return (ctx) => {
    const i = ctx.dataIndex;
    if (arr[i] === null || arr[i] === undefined) return 0;
    const prev = i > 0 ? arr[i-1] : null;
    const next = i < arr.length-1 ? arr[i+1] : null;
    return (prev === null || prev === undefined) && (next === null || next === undefined) ? (r || 3) : 0;
  };
}

const lastDay = dates[dates.length - 1];
function completeness(p) {
  const i = p.volume.length - 1;
  const vol = p.volume[i];
  if (vol === null) return {cls:'none', label:'ยังไม่ลงข้อมูล', detail:`${lastDay}: ยังไม่มีข้อมูล`};
  if (!vol)          return {cls:'none', label:'ไม่ซื้อ', detail:`${lastDay}: ไม่มีการซื้อ`};
  const miss = [];
  if (p.price[i]  == null) miss.push('ราคา');
  if (p.starch[i] == null) miss.push('%Starch');
  if (p.recov[i]  == null) miss.push('%Recovery');
  if (p.cag[i]    == null) miss.push('CAG');
  if (!miss.length) return {cls:'ok', label:'ครบ', detail:`${lastDay}: ข้อมูลครบทุกช่อง`};
  return {cls:'wait', label:'รอผลโม่', detail:`${lastDay}: ขาด ${miss.join(' + ')}`};
}

(function boot(n){
  if (typeof Chart === 'undefined') {
    if (n > 100) { document.getElementById('plantChartGrid').innerHTML='<div style="padding:24px;color:#b03030;font-size:13px">โหลดไลบรารีกราฟ (Chart.js) ไม่สำเร็จ — เครือข่ายอาจบล็อก CDN</div>'; return; }
    return setTimeout(function(){ boot(n+1); }, 100);
  }
const grid = document.getElementById('plantChartGrid');
Object.entries(plants).forEach(([code, p]) => {
  const box = document.createElement('div'); box.className='chart-box';
  const st = completeness(p);
  box.innerHTML = `
    <div class="plant-chart-title">${code} — ${p.fullName}</div>
    <div class="plant-chart-sub">ราคา, ปริมาณซื้อ, %Starch, ปริมาณแป้ง, CAG, %Recovery (30 วันย้อนหลัง)</div>
    <div style="margin:-2px 0 8px 0"><span class="badge ${st.cls}">${st.label}</span><span class="status-detail">${st.detail}</span></div>
    <div class="plant-chart-wrap"><canvas id="chart-${code}"></canvas></div>`;
  grid.appendChild(box);
  const datasets = [
    { type:'bar', label:'ปริมาณซื้อ (ตัน)', data:p.volume, backgroundColor:'rgba(214,217,222,0.6)', borderColor:'#c7cbd1', borderWidth:1, yAxisID:'yVolume', order:3 },
    { type:'line', label:'ราคา (บาท/กก.)', data:p.price, borderColor:'#0b2540', backgroundColor:'#0b2540', borderWidth:2.5, pointRadius:isolatedPt(p.price,3), tension:0.15, yAxisID:'yPrice', spanGaps:false, order:1 },
    { type:'line', label:'%Starch', data:p.starch, borderColor:'#e0821f', backgroundColor:'#e0821f', borderWidth:1.5, borderDash:[4,3], pointRadius:isolatedPt(p.starch,2.5), tension:0.15, yAxisID:'yStarch', spanGaps:false, order:2 },
    { type:'line', label:'ปริมาณแป้ง (ตัน)', data:p.starchTon, borderColor:'#1a9850', backgroundColor:'#1a9850', borderWidth:1.5, borderDash:[4,3], pointRadius:isolatedPt(p.starchTon,2.5), tension:0.15, yAxisID:'yVolume', spanGaps:false, order:2 },
    { type:'line', label:'CAG ต้นทุนหลังโม่ (บาท/กก.)', data:p.cag, borderColor:'#8e44ad', backgroundColor:'#8e44ad', borderWidth:2, pointRadius:isolatedPt(p.cag,3), tension:0.15, yAxisID:'yCag', spanGaps:false, order:1 },
    { type:'line', label:'%Recovery', data:p.recov, borderColor:'#0e8aa8', backgroundColor:'#0e8aa8', borderWidth:0, pointRadius:2.5, pointStyle:'circle', showLine:false, yAxisID:'yRecov', spanGaps:false, order:0 }
  ];
  if (code === 'PM') datasets.push({ type:'line', label:'External: พิมาย @25% (Nettathai)', data:externalPM, borderColor:'#d73027', backgroundColor:'#d73027', pointStyle:'star', pointRadius:7, showLine:false, yAxisID:'yPrice', order:0 });
  try {
  new Chart(document.getElementById('chart-'+code), { type:'bar', data:{ labels:dates, datasets },
    options:{ responsive:true, maintainAspectRatio:false, interaction:{ mode:'index', intersect:false },
      plugins:{ legend:{ position:'bottom', labels:{ boxWidth:10, font:{ size:10 } } }, tooltip:{ titleFont:{ size:11 }, bodyFont:{ size:11 } } },
      scales:{
        x:{ ticks:{ font:{ size:9 }, maxRotation:0, autoSkip:true, maxTicksLimit:8 }, grid:{ display:false } },
        yPrice:{ position:'left', ticks:{ font:{ size:10 } }, grid:{ color:'#eceef1' }, title:{ display:true, text:'ราคา บาท/กก.', font:{ size:9 }, color:'#0b2540' } },
        yStarch:{ position:'left', ticks:{ font:{ size:10 } }, grid:{ display:false }, title:{ display:true, text:'%Starch', font:{ size:9 }, color:'#e0821f' } },
        yRecov:{ position:'left', ticks:{ font:{ size:10 } }, grid:{ display:false }, title:{ display:true, text:'%Recovery', font:{ size:9 }, color:'#0e8aa8' } },
        yVolume:{ position:'right', ticks:{ font:{ size:10 } }, grid:{ display:false }, title:{ display:true, text:'ตัน', font:{ size:9 } }, beginAtZero:true },
        yCag:{ position:'right', ticks:{ font:{ size:10 } }, grid:{ display:false }, title:{ display:true, text:'CAG บาท/กก.', font:{ size:9 }, color:'#8e44ad' } }
      } } });
  } catch (err) { const w=box.querySelector('.plant-chart-wrap'); if(w) w.innerHTML='<div style="padding:20px;color:#b03030;font-size:12px">โหลดกราฟไม่สำเร็จ: '+(err&&err.message?err.message:err)+'</div>'; }
});
})(0);
