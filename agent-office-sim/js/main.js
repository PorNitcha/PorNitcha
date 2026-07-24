// main.js — boot ฉาก, ปุ่มควบคุม, การ์ดพนักงาน, งาน scale ให้พอดีจอ
(function () {
  'use strict';

  const CFG = window.OFFICE_CONFIG;
  let speed = 1;
  let paused = false;

  function applyTheme() {
    const root = document.documentElement;
    Object.entries({
      '--brand-primary': CFG.theme.primary,
      '--brand-accent': CFG.theme.accent,
      '--brand-charcoal': CFG.theme.charcoal,
      '--brand-paper': CFG.theme.paper,
    }).forEach(([k, v]) => root.style.setProperty(k, v));
    document.title = `${CFG.officeName} — AI Employee Office`;
    document.getElementById('office-name').textContent = CFG.officeName;
    document.getElementById('office-tagline').textContent = CFG.tagline;
  }

  function fitStage() {
    const wrap = document.getElementById('world-wrap');
    const stage = document.getElementById('world-stage');
    const scale = Math.min(1, wrap.clientWidth / CFG.world.width);
    stage.style.transform = `scale(${scale})`;
    wrap.style.height = `${CFG.world.height * scale + 8}px`;
  }

  function showCard(agent) {
    const panel = document.getElementById('employee-card');
    panel.innerHTML = `
      <button class="card-close" type="button" aria-label="ปิดการ์ด">✕</button>
      <div class="card-head">
        <span class="card-avatar" style="--agent-color:${agent.data.color}">${agent.data.avatar}</span>
        <div>
          <strong>${agent.data.name}</strong>
          <div class="card-role">${agent.data.role}</div>
        </div>
      </div>
      <p class="card-personality">🧠 ${agent.data.personality}</p>
      <p class="card-dept">🚪 แผนก: ${window.World.room(agent.data.dept)?.name || agent.data.dept}</p>
      <p class="card-hint">แก้ไขพนักงานคนนี้ได้ที่ <code>employees/</code> และ <code>data/employees.js</code></p>`;
    panel.hidden = false;
    panel.querySelector('.card-close').addEventListener('click', () => { panel.hidden = true; });
  }

  function boot() {
    applyTheme();
    const svg = document.getElementById('office-floor');
    window.World.build(svg);

    const stage = document.getElementById('world-stage');
    const agents = window.Agents.spawn(stage);
    agents.forEach((agent) => agent.el.addEventListener('click', () => showCard(agent)));

    document.getElementById('agent-count').textContent = `พนักงาน AI: ${agents.length} คน`;

    document.getElementById('btn-pause').addEventListener('click', (e) => {
      paused = !paused;
      e.currentTarget.textContent = paused ? '▶ เล่นต่อ' : '⏸ พัก';
    });
    document.getElementById('btn-speed').addEventListener('click', (e) => {
      speed = speed === 1 ? 2 : 1;
      e.currentTarget.textContent = `⚡ x${speed}`;
    });

    if (window.Agents.reducedMotion) {
      document.getElementById('motion-note').hidden = false;
    }

    fitStage();
    window.addEventListener('resize', fitStage);

    // ใช้ setInterval แทน requestAnimationFrame เพื่อให้ฉากยังเดินต่อ
    // แม้แท็บถูกเบราว์เซอร์ throttle (rAF หยุดสนิทเมื่อแท็บไม่ active)
    let last = performance.now();
    setInterval(() => {
      const now = performance.now();
      // clamp 1 วินาที: แท็บ background (timer โดน throttle) ยังเดินเวลาใกล้จริง
      const dt = Math.min(1, (now - last) / 1000);
      last = now;
      if (!paused) window.Agents.update(dt, now, agents, speed);
    }, 1000 / 30);
  }

  document.addEventListener('DOMContentLoaded', boot);
})();
