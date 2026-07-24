// dialogue.js — เลือกบทพูด: พูดคนเดียวที่โต๊ะ + บทคุยระหว่างสองคนตามคู่แผนก
(function () {
  'use strict';

  function pick(list) {
    return list[Math.floor(Math.random() * list.length)];
  }

  function topicFor(deptA, deptB) {
    const topics = window.DIALOGUE_TOPICS;
    const key = [deptA, deptB].sort().join('|');
    const pool = topics[key] && topics[key].length ? topics[key] : topics.default;
    return pick(pool);
  }

  window.Dialogue = {
    soloLine(employee) {
      return pick(employee.lines);
    },

    // คืน array ของ { speaker: agent, text } สลับผู้เริ่มคุย (a) กับคู่สนทนา (b)
    conversation(agentA, agentB) {
      const script = topicFor(agentA.data.dept, agentB.data.dept);
      // ถ้า key ถูก sort สลับกับผู้เริ่มจริง ให้คงลำดับประโยคไว้แต่สลับคนพูดตามลำดับ index
      const sorted = [agentA.data.dept, agentB.data.dept].sort();
      const firstSpeaker = sorted[0] === agentA.data.dept ? agentA : agentB;
      const secondSpeaker = firstSpeaker === agentA ? agentB : agentA;
      return script.map((text, i) => ({
        speaker: i % 2 === 0 ? firstSpeaker : secondSpeaker,
        text: text
          .replaceAll('{a}', firstSpeaker.data.name)
          .replaceAll('{b}', secondSpeaker.data.name),
      }));
    },
  };
})();
