
const dates = ["18-Aug", "19-Aug", "20-Aug", "21-Aug", "22-Aug", "23-Aug", "24-Aug", "25-Aug", "26-Aug", "27-Aug", "28-Aug", "29-Aug", "30-Aug", "31-Aug", "1-Sep", "2-Sep", "3-Sep", "4-Sep", "5-Sep", "6-Sep", "7-Sep", "8-Sep", "9-Sep", "10-Sep", "11-Sep", "12-Sep", "13-Sep", "14-Sep", "15-Sep", "16-Sep"];

// null = ไม่มีค่าที่มีความหมาย · volume คง 0 · TWIC แยกจากยอดไทย
const plants = {
  TN: { label: "TN", fullName: "อ.เมือง อุดรธานี",
    price:  [3.65, 3.68, 3.78, 3.7, 3.67, 3.67, 3.67, 3.67, 3.69, 3.63, 3.67, 3.64, 3.64, 3.66, 3.64, 3.68, 3.68, 3.67, 3.65, 3.71, 3.76, 3.81, 3.83, 3.88, 3.82, 3.78, 3.8, 3.82, 3.86, 3.83],
    volume: [948, 563, 659, 550, 693, 999, 1238, 1552, 1113, 613, 864, 971, 1285, 1035, 812, 1007, 839, 796, 663, 615, 692, 1029, 720, 514, 624, 804, 1249, 1172, 1072, 918],
    starch: [22.55, 23.08, 24.35, 23.77, 22.74, 23.11, 22.94, 23.1, 23.38, 22.59, 23.87, 23.17, 23.52, 23.89, 23.47, 23.99, 24.34, 23.86, 23.67, 25.02, 23.75, 23.56, 23.72, 25.27, 23.63, 22.44, 23.35, 23.52, 24.45, 24.08],
    cag:    [16.69, 15.52, 14.12, 15.09, 16.28, 15.91, 15.67, 15.06, 15.29, 16.37, 14.74, 15.28, 15.07, 15.01, 15.85, 16.47, 16, 16.42, 15.94, 15.21, 15.96, 18.35, 16.44, 14.76, null, 18.76, 16.24, 17.54, 15.35, 16.27],
    recov:  [97, 102.7, 109.9, 103.2, 99.2, 99.8, 102.1, 105.5, 103.3, 98.1, 104.3, 102.8, 102.7, 102.1, 97.9, 93.2, 94.5, 93.7, 96.8, 97.5, 99.2, 88.2, 98.2, 104, null, 89.8, 100.2, 92.6, 102.8, 97.8]
  },
  TKT: { label: "TKT", fullName: "ท่าคันโท กาฬสินธุ์",
    price:  [3.88, 3.87, 3.88, 3.95, 3.84, 3.82, 3.82, 3.81, 3.77, 3.83, 3.77, 3.75, 3.78, 3.76, 3.77, 3.76, 3.79, 3.88, 3.88, 3.88, 3.88, 3.87, 3.96, 3.95, 3.9, 4.06, 4.05, 4.13, 4.15, 4.09],
    volume: [1195, 992, 214, 208, 440, 944, 763, 846, 808, 590, 930, 964, 928, 1017, 473, 541, 896, 1215, 1344, 1228, 806, 1013, 800, 572, 333, 782, 1218, 851, 493, 442],
    starch: [21.49, 22.18, 22.46, 23.84, 21.76, 21.26, 21.22, 21.12, 21.36, 22.48, 22.04, 21.88, 22.52, 22.14, 22.31, 22.14, 22.59, 22.2, 22.49, 22.6, 22.49, 22.37, 23.65, 23.69, 22.83, 23.02, 22.82, 24.13, 24.27, 23.57],
    cag:    [16.69, 16.79, 10.25, 45.77, 17.76, 20.96, 18.37, 17.01, 17.48, 16.31, 16.17, 16.45, 15.75, 15.8, 13.48, 17.78, 16.82, 16.73, 16.4, 16.84, 17.22, 16.91, 16.15, 19.54, 18.34, 17.44, 17.39, 17.01, 17.1, 16.78],
    recov:  [108.2, 103.9, 168.5, 36.2, 99.3, 85.7, 98, 106, 101, 104.4, 105.8, 104.2, 106.6, 107.5, 125.3, 95.5, 99.8, 104.5, 105.2, 101.9, 100.2, 102.3, 103.7, 85.4, 93.1, 101.1, 102.1, 100.6, 100, 103.4]
  },
  PM: { label: "PM", fullName: "พิมาย โคราช",
    price:  [3.87, 3.91, 3.83, 3.87, 3.87, 3.92, 3.9, 3.89, 3.86, 3.88, 3.91, 3.93, 3.93, 4, 3.96, 4.01, 3.96, 4.01, 4.05, 4.09, 4.12, 4.1, 4.2, 4.13, 4.2, 4.16, 4.19, 4.2, 4.18, 4.17],
    volume: [451, 665, 334, 241, 325, 601, 757, 651, 671, 531, 790, 718, 816, 540, 561, 403, 627, 917, 642, 475, 1025, 1088, 777, 762, 481, 997, 844, 740, 783, 730],
    starch: [21.3, 21.45, 20.49, 21.16, 21.11, 22.24, 21.92, 21.76, 21.16, 21.52, 21.51, 21.57, 21.52, 22.74, 22.06, 22.78, 20.33, 21.22, 22, 22.52, 21.43, 21.23, 22.86, 21.75, 22.86, 22.14, 22.83, 22.98, 22.48, 22.33],
    cag:    [27.76, 18.52, 16.87, null, 17.69, null, 17.68, 17.78, 18.05, 17.78, 17.64, 17.42, 17.52, 16.73, 17.82, 17.31, 19.07, 18.14, 17.63, 17.29, 18.55, 18.57, 17.14, 17.84, 17.78, 18.39, 17.61, 28.01, 18.12, 18.52],
    recov:  [65.4, 98.4, 110.8, null, 103.6, null, 100.6, 100.6, 101.1, 101.4, 103.1, 104.6, 104.2, 105.2, 100.8, 101.7, 102.1, 104.2, 104.4, 105, 103.6, 104, 107.2, 106.5, 103.3, 102.2, 104.2, 65.3, 102.6, 100.8]
  },
  TDC: { label: "TDC", fullName: "บ้านฉาง ระยอง",
    price:  [4.1, 4.09, 4.09, 4.07, 4.08, 4.13, 4.06, 4.07, 4.18, 4.13, 4.01, 4.12, 4.29, 4.17, 4.2, 4.19, 4.12, 4.13, 4.17, 4.17, 4.2, 4.18, 4.22, 4.2, 4.05, 4.2, 4.17, 4.17, 4.06, 4.17],
    volume: [293, 291, 350, 356, 298, 317, 273, 287, 213, 303, 326, 191, 154, 376, 276, 314, 239, 343, 307, 278, 318, 338, 355, 298, 201, 251, 260, 233, 172, 298],
    starch: [23.36, 23.31, 23.38, 23.41, 23.55, 23.71, 23.44, 23.96, 24.05, 23.52, 22.34, 23.77, 25.31, 23.96, 24.67, 24.59, 23.44, 23.4, 23.88, 24.06, 24.13, 24.07, 24.59, 24.22, 23.34, 24.46, 23.83, 23.73, 22.74, 23.64],
    cag:    [17.96, 18.04, 18.15, 18.34, 18.65, 17.05, 18.08, 17.43, 18.28, 17.6, 19.04, 18.32, 16.85, 17.56, 17.81, 17.74, 18.23, 18, 18.35, 18.52, 17.64, 17.29, 17.07, 17.78, 18.75, 17.94, 18.54, 17.4, 17.77, null],
    recov:  [97.7, 97.3, 96.4, 94.8, 92.9, 102.2, 95.8, 97.5, 95.1, 99.8, 94.3, 94.6, 100.6, 99.1, 95.6, 96, 96.4, 98.1, 95.2, 93.6, 98.7, 100.4, 100.5, 97.6, 92.6, 95.7, 94.4, 101, 100.5, null]
  },
  MS: { label: "MS", fullName: "แม่สอด ตาก",
    price:  [null, null, null, null, null, null, null, null, null, null, null, null, null, null, 3.75, 3.78, 3.71, 3.79, 3.79, 3.84, 3.81, 3.79, 3.81, 3.83, 3.82, 3.82, 3.9, 3.98, 3.99, 3.93],
    volume: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 29, 188, 101, 154, 187, 170, 194, 242, 289, 298, 238, 205, 332, 376, 290, 423],
    starch: [null, null, null, null, null, null, null, null, null, null, null, null, null, null, 20.69, 20.61, 20.15, 21.28, 20.88, 22.22, 21.8, 21.54, 21.73, 23.29, 22.48, 24.16, 23.36, 24.56, 25.7, 23.67],
    cag:    [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 21.52, 19.34, 18.51, null, null, 21.41, 15.86, null, null, 18.4, 38.53, null, 21.28],
    recov:  [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 82.8, 93.9, 93.4, null, null, 81.9, 103.7, null, null, 90.8, 42.1, null, 78]
  },
  TWIC: { label: "TWIC", fullName: "TWIC กัมพูชา (Oddar Meanchey)",
    price:  [3.15, 3.22, 3.32, 3.27, 3.32, 3.23, 3.19, 3.17, 3.31, 3.23, 3.24, 3.14, 3.19, 3.47, 3.32, 3.33, 3.45, 3.35, 3.31, 3.38, 3.34, 3.3, 3.27, 3.31, 3.21, 3.37, null, 3.29, 3.34, 3.36],
    volume: [453, 492, 542, 534, 481, 560, 576, 622, 544, 395, 543, 298, 355, 210, 268, 399, 458, 328, 501, 282, 421, 279, 244, 192, 133, 282, 0, 325, 222, 388],
    starch: [18.06, 18.17, 18.59, 18.57, 18.95, 18.36, 18.3, 18.09, 18.4, 18.05, 18.61, 19.56, 19.67, 21.88, 19.81, 20.52, 21.05, 20.16, 20.84, 20.55, 20.54, 21.02, 19.58, 20.42, 19.39, 21.24, null, 20.28, 21.45, 19.8],
    cag:    [16.27, 17.62, 16.37, 16.43, 17.14, 16.75, 17, 16.4, 16.87, 17.2, 16.42, 15.93, null, 14.65, 16.88, 14.65, 15.5, 16.45, 15.35, 16.43, 15.65, 16, null, 15.37, null, 15.49, null, 15.38, 15.35, 16.17],
    recov:  [107.17, 100.67, 109.09, 107.31, 102.1, 105.01, 102.6, 106.89, 106.71, 104.17, 106.08, 100.63, null, 108.19, 99.27, 110.81, 105.63, 101.09, 103.62, 100.06, 104.04, 98.11, null, 105.39, null, 102.53, null, 105.4, 101.62, 104.91]
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
