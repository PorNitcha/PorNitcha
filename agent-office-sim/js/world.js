// world.js — วาดผังออฟฟิศ (SVG) + คำนวณจุดยืน/โต๊ะของแต่ละห้อง
(function () {
  'use strict';

  const CFG = window.OFFICE_CONFIG;

  // จุดที่พนักงานยืน/เดินไปหา ต่อห้อง
  function computeSpots(room) {
    const spots = [];
    if (room.type === 'common') {
      spots.push({ x: room.x + room.w * 0.35, y: room.y + room.h * 0.62 });
      spots.push({ x: room.x + room.w * 0.65, y: room.y + room.h * 0.62 });
      spots.push({ x: room.x + room.w * 0.5, y: room.y + room.h * 0.78 });
    } else {
      spots.push({ x: room.x + room.w * 0.28, y: room.y + room.h * 0.6 });
      spots.push({ x: room.x + room.w * 0.72, y: room.y + room.h * 0.6 });
    }
    return spots;
  }

  function el(tag, attrs) {
    const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.entries(attrs || {}).forEach(([k, v]) => node.setAttribute(k, v));
    return node;
  }

  function drawDesk(g, x, y, color) {
    g.appendChild(el('rect', { x: x - 34, y: y - 6, width: 68, height: 30, rx: 6, fill: '#ffffff', stroke: color, 'stroke-width': 2 }));
    g.appendChild(el('rect', { x: x - 24, y: y - 2, width: 20, height: 13, rx: 2, fill: color, opacity: 0.85 })); // โน้ตบุ๊ก
    g.appendChild(el('circle', { cx: x + 16, cy: y + 6, r: 4, fill: '#ffd166' })); // แก้วน้ำ
  }

  function drawPlant(g, x, y) {
    g.appendChild(el('circle', { cx: x, cy: y, r: 12, fill: '#3aa76d', opacity: 0.9 }));
    g.appendChild(el('circle', { cx: x - 8, cy: y + 6, r: 8, fill: '#57c98b', opacity: 0.9 }));
    g.appendChild(el('rect', { x: x - 6, y: y + 10, width: 12, height: 10, rx: 3, fill: '#a9744f' }));
  }

  // โหมดภาพพื้นหลัง: วาดเฉพาะป้ายชื่อห้องเล็ก ๆ ไม่ทับงานศิลป์ในภาพ
  function drawRoomLabel(g, room, theme) {
    const text = `${room.icon} ${room.name}`;
    const w = text.length * 11.5 + 30;
    g.appendChild(el('rect', {
      x: room.x + 10, y: room.y + 10, width: w, height: 34, rx: 17,
      fill: '#ffffff', opacity: 0.85, stroke: theme.primary, 'stroke-opacity': 0.2, 'stroke-width': 1.5,
    }));
    const label = el('text', {
      x: room.x + 24, y: room.y + 33, 'font-size': 17, 'font-weight': 700,
      fill: theme.primary, 'font-family': 'inherit',
    });
    label.textContent = text;
    g.appendChild(label);
  }

  function drawRoom(g, room, theme) {
    const isCommon = room.type === 'common';
    g.appendChild(el('rect', {
      x: room.x, y: room.y, width: room.w, height: room.h, rx: 18,
      fill: isCommon ? '#fdfcf7' : theme.wall,
      stroke: theme.primary, 'stroke-width': 3, 'stroke-opacity': 0.25,
    }));
    // แถบหัวห้อง
    g.appendChild(el('rect', { x: room.x, y: room.y, width: room.w, height: 44, rx: 18, fill: theme.primary, opacity: isCommon ? 0.08 : 0.12 }));
    const label = el('text', {
      x: room.x + 20, y: room.y + 30, 'font-size': 21, 'font-weight': 700,
      fill: theme.primary, 'font-family': 'inherit',
    });
    label.textContent = `${room.icon} ${room.name}`;
    g.appendChild(label);

    if (room.id === 'meeting') {
      g.appendChild(el('ellipse', { cx: room.x + room.w / 2, cy: room.y + room.h * 0.62, rx: room.w * 0.3, ry: 42, fill: '#ffffff', stroke: theme.accent, 'stroke-width': 3 }));
    } else if (room.id === 'pantry') {
      g.appendChild(el('rect', { x: room.x + 24, y: room.y + 64, width: room.w - 48, height: 26, rx: 8, fill: theme.accent, opacity: 0.25 }));
      const coffee = el('text', { x: room.x + room.w / 2, y: room.y + 84, 'font-size': 18, 'text-anchor': 'middle' });
      coffee.textContent = '☕ 🍵 🥤 🍪';
      g.appendChild(coffee);
      drawPlant(g, room.x + room.w - 36, room.y + room.h - 40);
    } else {
      const spots = computeSpots(room);
      spots.forEach((s) => drawDesk(g, s.x, s.y + 18, theme.accent));
      drawPlant(g, room.x + room.w - 34, room.y + room.h - 38);
    }
  }

  function buildFloor(svg) {
    const theme = CFG.theme;
    const { width, height } = CFG.world;
    const imageMode = CFG.background.mode === 'image' && CFG.background.image;
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

    svg.appendChild(el('rect', { x: 0, y: 0, width, height, rx: 26, fill: theme.floor }));

    if (imageMode) {
      // โหมดภาพ: ภาพคือฉากทั้งหมด วาดทับแค่ป้ายชื่อห้อง
      svg.appendChild(el('image', { x: 0, y: 0, width, height, href: CFG.background.image, preserveAspectRatio: 'xMidYMid slice' }));
      const labels = el('g', {});
      CFG.rooms.forEach((room) => drawRoomLabel(labels, room, theme));
      svg.appendChild(labels);
      return;
    }

    // โหมด builtin: วาดทางเดิน + ป้ายบริษัท + ห้องทั้งหมดด้วยโค้ด
    svg.appendChild(el('rect', { x: 24, y: 350, width: width - 48, height: 170, rx: 16, fill: theme.corridor, stroke: theme.primary, 'stroke-opacity': 0.08, 'stroke-width': 2 }));

    const sign = el('text', {
      x: width / 2, y: CFG.corridor.y + 10, 'text-anchor': 'middle',
      'font-size': 42, 'font-weight': 800, fill: theme.primary, opacity: 0.14,
      'letter-spacing': '14',
    });
    sign.textContent = `${CFG.companyName} OFFICE`;
    svg.appendChild(sign);

    const roomsGroup = el('g', {});
    CFG.rooms.forEach((room) => drawRoom(roomsGroup, room, theme));
    svg.appendChild(roomsGroup);
  }

  window.World = {
    build: buildFloor,
    spotsOf(roomId) {
      const room = CFG.rooms.find((r) => r.id === roomId);
      return room ? computeSpots(room) : [];
    },
    room(roomId) {
      return CFG.rooms.find((r) => r.id === roomId) || null;
    },
    commonRooms() {
      return CFG.rooms.filter((r) => r.type === 'common');
    },
  };
})();
