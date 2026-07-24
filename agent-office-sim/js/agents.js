// agents.js — พนักงานเดิน / เจอกัน / คุยกัน (state machine + conversation manager)
(function () {
  'use strict';

  const CFG = window.OFFICE_CONFIG;
  const WALK_SPEED = 90; // px ต่อวินาที (ก่อนคูณ speed)
  const BUBBLE_MS = 2800; // เวลาการโชว์ 1 ประโยค
  const CHAT_COOLDOWN_MS = 14000;

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function rand(min, max) { return min + Math.random() * (max - min); }
  function pick(list) { return list[Math.floor(Math.random() * list.length)]; }

  // ---------- Agent ----------
  class Agent {
    constructor(data, deskSpot, stageEl) {
      this.data = data;
      this.desk = { x: deskSpot.x, y: deskSpot.y - 26 };
      this.pos = { x: this.desk.x, y: this.desk.y };
      this.waypoints = [];
      this.state = 'desk'; // desk | walking | chatting
      this.afterWalk = null;
      this.nextActionAt = performance.now() + rand(2000, 9000);
      this.chatCooldownUntil = 0;

      this.el = document.createElement('button');
      this.el.className = 'agent';
      this.el.type = 'button';
      this.el.setAttribute('aria-label', `${data.name} — ${data.role}`);
      this.el.innerHTML = `
        <span class="agent-bubble" role="status"></span>
        <span class="agent-avatar" style="--agent-color:${data.color}">${data.avatar}</span>
        <span class="agent-name">${data.name}</span>`;
      this.bubbleEl = this.el.querySelector('.agent-bubble');
      stageEl.appendChild(this.el);
      this.render();
    }

    walkTo(point, afterWalk) {
      const cy = CFG.corridor.y;
      const path = [];
      const inCorridor = (y) => y > 350 && y < 520;
      if (!inCorridor(this.pos.y)) path.push({ x: this.pos.x, y: cy });
      if (!inCorridor(point.y)) {
        path.push({ x: point.x, y: cy });
      }
      path.push({ x: point.x, y: point.y });
      this.waypoints = path;
      this.state = 'walking';
      this.afterWalk = afterWalk || null;
      this.el.classList.add('is-walking');
    }

    say(text, ms) {
      this.bubbleEl.textContent = text;
      this.el.classList.add('is-talking');
      clearTimeout(this._bubbleTimer);
      this._bubbleTimer = setTimeout(() => this.el.classList.remove('is-talking'), ms || BUBBLE_MS);
    }

    update(dt, now, speed) {
      if (this.state === 'walking') {
        const step = (reducedMotion ? 100000 : WALK_SPEED * speed) * dt;
        let remaining = step;
        while (remaining > 0 && this.waypoints.length) {
          const t = this.waypoints[0];
          const dx = t.x - this.pos.x;
          const dy = t.y - this.pos.y;
          const dist = Math.hypot(dx, dy);
          if (dist <= remaining) {
            this.pos = { x: t.x, y: t.y };
            this.waypoints.shift();
            remaining -= dist;
          } else {
            this.pos = { x: this.pos.x + (dx / dist) * remaining, y: this.pos.y + (dy / dist) * remaining };
            remaining = 0;
          }
        }
        if (!this.waypoints.length) {
          this.el.classList.remove('is-walking');
          this.state = 'desk';
          this.nextActionAt = now + rand(4000, 12000);
          if (this.afterWalk) { const cb = this.afterWalk; this.afterWalk = null; cb(); }
        }
      } else if (this.state === 'desk' && now >= this.nextActionAt) {
        this.nextActionAt = now + rand(6000, 16000);
        const roll = Math.random();
        if (roll < 0.55) {
          this.say(window.Dialogue.soloLine(this.data));
        } else if (roll < 0.8 && !reducedMotion) {
          // เดินไปพักที่พื้นที่ส่วนกลาง แล้วเดินกลับโต๊ะ
          const common = pick(window.World.commonRooms());
          const spot = pick(window.World.spotsOf(common.id));
          this.walkTo({ x: spot.x + rand(-20, 20), y: spot.y - 26 }, () => {
            this.nextActionAt = now + rand(3000, 6000);
            setTimeout(() => { if (this.state === 'desk') this.walkTo(this.desk); }, rand(2500, 6000));
          });
        }
      }
      this.render();
    }

    render() {
      this.el.style.transform = `translate(${this.pos.x}px, ${this.pos.y}px)`;
    }
  }

  // ---------- Conversation Manager ----------
  const Conversations = {
    active: [],
    nextMeetAt: performance.now() + 4000,

    tick(now, agents) {
      if (now < this.nextMeetAt) return;
      this.nextMeetAt = now + rand(9000, 18000);

      const free = agents.filter((a) => a.state === 'desk' && now > a.chatCooldownUntil);
      if (free.length < 2) return;
      const a = pick(free);
      const b = pick(free.filter((x) => x !== a));
      if (!b) return;

      a.chatCooldownUntil = b.chatCooldownUntil = now + CHAT_COOLDOWN_MS + 60000; // กันซ้อนระหว่างคุย
      this.start(a, b, now);
    },

    start(a, b, now) {
      const meetRoom = pick(window.World.commonRooms());
      const spots = window.World.spotsOf(meetRoom.id);
      const pa = { x: spots[0].x, y: spots[0].y - 26 };
      const pb = { x: spots[1].x, y: spots[1].y - 26 };

      let arrived = 0;
      const onArrive = () => {
        arrived += 1;
        if (arrived === 2) this.play(a, b);
      };

      if (reducedMotion) {
        // โหมดลดการเคลื่อนไหว: คุยกันจากโต๊ะ (เหมือนโทรหา)
        this.play(a, b);
        return;
      }
      a.state = 'desk'; b.state = 'desk';
      a.walkTo(pa, onArrive);
      b.walkTo(pb, onArrive);
    },

    play(a, b) {
      a.state = 'chatting'; b.state = 'chatting';
      const script = window.Dialogue.conversation(a, b);
      script.forEach((line, i) => {
        setTimeout(() => line.speaker.say(line.text, BUBBLE_MS + 300), i * (BUBBLE_MS + 400));
      });
      const total = script.length * (BUBBLE_MS + 400) + 800;
      setTimeout(() => {
        const now = performance.now();
        a.chatCooldownUntil = now + CHAT_COOLDOWN_MS;
        b.chatCooldownUntil = now + CHAT_COOLDOWN_MS;
        [a, b].forEach((agent) => {
          agent.state = 'desk';
          agent.nextActionAt = now + rand(2000, 5000);
          if (!reducedMotion) agent.walkTo(agent.desk);
        });
      }, total);
    },
  };

  window.Agents = {
    reducedMotion,
    spawn(stageEl) {
      const deskIndexByRoom = {};
      return window.EMPLOYEES.map((emp) => {
        const spots = window.World.spotsOf(emp.dept);
        const idx = deskIndexByRoom[emp.dept] || 0;
        deskIndexByRoom[emp.dept] = idx + 1;
        const spot = spots[idx % spots.length] || { x: 800, y: 450 };
        return new Agent(emp, spot, stageEl);
      });
    },
    update(dt, now, agents, speed) {
      agents.forEach((a) => a.update(dt, now, speed));
      Conversations.tick(now, agents);
    },
  };
})();
