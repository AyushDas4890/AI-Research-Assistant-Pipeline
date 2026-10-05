// AI Research Assistant — portfolio reel (docs/shotlist.md, APPROVED).
// Every piece of product UI is a real capture of app.py (assets/cap/*.png, 2x). Windows crop and move those captures;
// nothing in the UI is redrawn. Geometry of the captured elements comes from capture_app/measure.mjs (film/geo.js).
// Pure function of time: no timers, no Math.random, nothing mutated in run() (the text-width memo is a pure cache).
(() => {
  const { W, H, put, reg, el, scene, sp, spHit, trk, seg, clamp, lerp, ease, bt, beatOf, beatAt } = C;
  const { line, rise } = TYPE;
  C.fonts = ['700 100px Display', '600 40px UI', '400 40px UI', '400 14px UI'];
  const G = window.GEO, PX = 2, L = 120;            // captures are 2x CSS px; left margin of all type
  const cap = (n) => `../assets/cap/${n}.png`;
  const FRAME = 1 / C.FPS;
  const at = (t, b) => t >= bt(b) - FRAME;          // instant UI swaps land one frame early so they read on the beat
  const pickShot = (t, keys) => keys.reduce((cur, [b, n]) => (at(t, b) ? n : cur), keys[0][1]);
  const push = (t, S, from, to, amt = 0.035) => put(S.root, { s: 1 + amt * ease.inOut(seg(t, from, to)) });

  // ---------------------------------------------------------------- windows onto real captures
  function win(parent, x, y, w, h, shots, cls = 'card win') {
    const card = el('div', { class: cls, style: `width:${w}px;height:${h}px` }, parent);
    reg(card, { x, y });
    const imgs = {};
    for (const n of shots) imgs[n] = reg(el('img', { src: cap(n) }, card), { o: 0 });
    return { card, imgs, w, h };
  }
  // v = { cx, cy, k }: CSS point of the capture at the window's top-left, k = screen px per CSS px
  function show(Wn, n, v) {
    for (const [name, im] of Object.entries(Wn.imgs)) put(im, name === n ? { o: 1, x: -v.cx * v.k, y: -v.cy * v.k, s: v.k / PX } : { o: 0 });
  }
  const loc = (v, x, y) => ({ x: (x - v.cx) * v.k, y: (y - v.cy) * v.k });
  // a card that rises into place: spring travel, opacity snaps on in the first frames (never a fade)
  function cardRise(t, Wn, x, y, beat, preset = 'default', hit = false) {
    const p = hit ? spHit(t, beat, preset, C.LEAD) : sp(t, beat, preset);   // a card has a hard landing: 3-frame lead
    put(Wn.card, { x, y: y + (1 - p) * 260, o: p > 0.002 ? 1 : 0 });
    return p;
  }

  const CURSOR = '<svg width="34" height="46" viewBox="0 0 17 23"><path d="M1.2 1.2v16.6l4.4-4.1 3 7 2.8-1.2-3-6.9h6z" fill="#31333F" stroke="#fff" stroke-width="1.3" stroke-linejoin="round"/></svg>';
  const cursor = (root) => reg(el('div', { class: 'abs', style: 'width:34px;height:46px' }, root, CURSOR), { o: 0 });
  // cursor path: keys [[beat, x, y]]; press: beat of the click (scale dip on snappy)
  function moveCursor(t, cur, keys, press, from, to) {
    const x = trk(t, keys.map(([b, kx]) => [b, kx]), 'default'), y = trk(t, keys.map(([b, , ky]) => [b, ky]), 'default');
    const pb = press == null ? null : beatOf(press);
    const dip = pb == null ? 0 : spHit(t, pb, 'snappy', C.LEAD) - sp(t, pb + 0.1, 'snappy');   // bottoms out on the click
    const b = beatAt(t);
    put(cur, { o: b >= from && b < to ? 1 : 0, x, y, s: 1 - 0.14 * dip });
  }

  // width of a prefix of the typed topic in the input's own face (memoised pure measurement, fonts are loaded first)
  const measureCtx = document.createElement('canvas').getContext('2d');
  const widthMemo = new Map();
  function typedWidth(n) {
    if (!widthMemo.has(n)) { measureCtx.font = '400 14px UI'; widthMemo.set(n, measureCtx.measureText(G.typed.typed.value.slice(0, n)).width); }
    return widthMemo.get(n);
  }

  // ================================================================ 1 · ask  (b0 → b8): topic, Run
  scene({
    name: 'ask', from: 'hook', to: 'plan',
    build(root, S) {
      S.h1 = line(root, 'Give it a topic.', { x: L, y: 110, size: 170, accent: [3] });
      S.h2a = line(root, 'Five agents', { x: L, y: 70, size: 150, accent: [0] });
      S.h2b = line(root, 'take it from here.', { x: L, y: 235, size: 150 });
      const g = G.typed;
      S.Y = 450;
      S.v = { cx: g.label.x - 18, cy: g.label.y - 12, k: 2.4 };              // the caption line above ends at y≈207
      S.h0 = (g.input.y + g.input.h + 14 - S.v.cy) * S.v.k;                 // label + input (button starts at y≈307)
      S.h1px = (G.run_start.status.y + G.run_start.status.h + 14 - S.v.cy) * S.v.k; // + button + status
      S.win = win(root, 0, 0, W - 2 * L, S.h0, ['s01_focus', 's02_typed', 's03_hover', 's04_run_start']);
      S.cover = reg(el('div', { class: 'abs', style: 'background:#f0f2f6' }, S.win.card), { o: 0 });
      S.caret = reg(el('div', { class: 'abs', style: 'width:3px;background:var(--ink)' }, S.win.card), { o: 0 });
      S.cur = cursor(root);
    },
    run(t, b, S) {
      push(t, S, 'hook', 'plan');
      rise(t, S.h1, [-0.4, -0.4, 'hook_w2', 'hook_w2'], beatOf('agents') - 0.2, { exit: 0.2 });
      rise(t, S.h2a, 'agents', null, { stagger: 0.1 });
      rise(t, S.h2b, beatOf('agents') + 0.25, null, { stagger: 0.06 });
      // one window, it grows from the input to the whole form when the run starts
      cardRise(t, S.win, L, S.Y, 'field', 'default', true);
      const grow = sp(t, beatOf('agents') + 0.1, 'default');   // settled before the click so the press reads on its own
      put(S.win.card, { css: { height: lerp(S.h0, S.h1px, grow) + 'px' } });
      const shot = pickShot(t, [[0, 's01_focus'], ['type0', 's02_typed'], [beatOf('run') - 0.5, 's03_hover'], ['running', 's04_run_start']]);
      show(S.win, shot, S.v);
      // typing: the real filled field, with the not-yet-typed characters covered by the field's own fill
      const g = G.typed, len = g.typed.value.length;
      const n = Math.floor(seg(t, 'type0', 3.75) * len + 1e-6);
      const x0 = g.input.x + g.typed.paddingLeft, wN = typedWidth(n), wAll = g.typed.textWidth;
      const inp = loc(S.v, x0 + wN, g.input.y + 6);
      const typing = b >= beatOf('type0') - 0.02 && n < len;
      put(S.cover, { o: typing ? 1 : 0, x: inp.x, y: inp.y, css: { width: (wAll - wN + 4) * S.v.k + 'px', height: (g.input.h - 12) * S.v.k + 'px' } });
      const blinkOn = n < len || Math.floor(b * 2) % 2 === 0;
      const caretOn = b >= beatOf('field') + 0.3 && b < beatOf('run') && blinkOn;
      const c = loc(S.v, x0 + (b < beatOf('type0') ? 0 : wN) + 1, g.input.y + 9);
      put(S.caret, { o: caretOn ? 1 : 0, x: c.x, y: c.y, css: { height: (g.input.h - 18) * S.v.k + 'px' } });
      // cursor glides in and presses Run Research on the beat
      const btn = G.typed.button, bp = loc(S.v, btn.x + btn.w * 0.55, btn.y + btn.h * 0.55);
      moveCursor(t, S.cur, [[0, W - 260, H + 40], [beatOf('agents') - 0.2, L + bp.x - 4, S.Y + bp.y - 6], [beatOf('run') + 0.75, L + bp.x + 360, S.Y + bp.y + 120]],
        'run', beatOf('agents') - 0.2, beatOf('plan'));
    },
  });

  // ================================================================ 2 · run  (b8 → b20): agents, log, self-critique
  const STEP_SHOTS = [['plan', 's05_step1'], ['search', 's06_step2'], ['read', 's07_step3'], ['critic', 's08_step4'], ['retry', 's09_step5']];
  scene({
    name: 'run', from: 'plan', to: 'report',
    build(root, S) {
      S.words = [['Plan.', 'plan', 'search'], ['Search.', 'search', 'read'], ['Read.', 'read', 'critic'], ['Critique.', 'critic', 'gaps']]
        .map(([s, a, z]) => ({ L: line(root, s, { x: L, y: 90, size: 170 }), a, z }));
      S.gapsLine = line(root, 'Finds its own gaps.', { x: L, y: 100, size: 150, accent: [3] });
      S.againLine = line(root, 'Searches again.', { x: L, y: 100, size: 150 });
      S.win = win(root, L, 320, W - 2 * L, 690, STEP_SHOTS.map(([, n]) => n));
      S.v0 = { cx: G.step1.logBlock.x - 14, cy: G.step1.logBlock.y - 14, k: 2.6 };
      // the window grows with the page: its bottom follows the status box under the log, step by step
      S.hKeys = STEP_SHOTS.map(([m], i) => { const st = G[`step${i + 1}`].status; return [m, (st.y + st.h + 16 - S.v0.cy) * S.v0.k]; });
      S.row = reg(el('div', { class: 'abs', style: 'background:color-mix(in srgb, var(--accent) 9%, transparent);border-radius:6px' }, S.win.card), { o: 0 });
      S.bar = reg(el('div', { class: 'abs', style: 'background:var(--accent);border-radius:3px' }, S.win.card), { o: 0 });
      S.under = reg(el('div', { class: 'abs', style: 'background:var(--accent);border-radius:3px' }, S.win.card), { o: 0 });
      // newest log line per step (CSS rects), and the "gaps_found: True" span of the critic line (monospace)
      S.lines = G.step5.logLines;
      const crit = S.lines[3], text = '[CRITIC] Coverage: 0.82 | gaps_found: True | retry_count: 1', cw = crit.w / text.length;
      S.gaps = { x: crit.x + text.indexOf('gaps_found') * cw, w: 'gaps_found: True'.length * cw, y: crit.y + crit.h };
    },
    run(t, b, S) {
      push(t, S, 'plan', 'report', 0.025);
      S.words.forEach(({ L: w, a, z }) => rise(t, w, a, beatOf(z) - 0.2, { stagger: 0.06, exit: 0.2 }));
      rise(t, S.gapsLine, 'gaps', beatOf('retry') - 0.2, { stagger: 0.06, exit: 0.2 });
      rise(t, S.againLine, 'retry', null, { stagger: 0.06 });
      // camera inside the window: punch in on the critic line for the self-critique
      const crit = S.lines[3];
      const tgt = { cx: crit.x - 12, cy: crit.y + crit.h / 2 - 0.42 * 690 / 3.3, k: 3.3 };
      const pin = beatOf('gaps') - 0.15;
      const hk = S.hKeys.filter(([m]) => m !== 'retry').map(([m, h], i) => [i === 0 ? 0 : beatOf(m) - 0.15, h]);
      const wh = trk(t, [...hk, [pin, 690]]);
      put(S.win.card, { y: 320 + (700 - wh) / 2, css: { height: wh + 'px' } });   // stays centred in the lower band as it grows
      const v = { cx: trk(t, [[0, S.v0.cx], [pin, tgt.cx]]), cy: trk(t, [[0, S.v0.cy], [pin, tgt.cy]]), k: trk(t, [[0, S.v0.k], [pin, tgt.k]]) };
      show(S.win, pickShot(t, STEP_SHOTS), v);
      // indicator: accent bar + tinted row on the newest log line (leading edge stiffer, so it stretches on the move)
      const idx = [[beatOf('plan'), 0], [beatOf('search'), 1], [beatOf('read'), 2], [beatOf('critic'), 3], [beatOf('retry'), 4]];
      const ind = Motion.indicator(t, idx.map(([bb, i], j) => [j === 0 ? 0 : bt(bb) - C.leadFor('snappy'), S.lines[i].y - 3, S.lines[i].y + S.lines[i].h + 3]));
      const lw = trk(t, idx.map(([bb, i], j) => [j === 0 ? 0 : bb - 0.1, S.lines[i].w], 'snappy'));
      const blk = G.step5.logBlock;
      const p0 = loc(v, blk.x + 5, ind.start), p1 = loc(v, S.lines[0].x - 8, ind.start);
      put(S.bar, { o: 1, x: p0.x, y: p0.y, css: { width: 3 * v.k + 'px', height: ind.size * v.k + 'px' } });
      put(S.row, { o: 1, x: p1.x, y: p1.y, css: { width: (lw + 16) * v.k + 'px', height: ind.size * v.k + 'px' } });
      // underline snaps under "gaps_found: True" on the click
      const u = spHit(t, 'gaps', 'snappy'), gp = loc(v, S.gaps.x, S.gaps.y + 1);
      put(S.under, { o: u > 0.002 ? 1 : 0, x: gp.x, y: gp.y, css: { width: S.gaps.w * u * v.k + 'px', height: 2 * v.k + 'px' } });
    },
  });

  // ================================================================ 3 · report  (b20 → b24)
  scene({
    name: 'report', from: 'report', to: 'time',
    build(root, S) {
      S.h = line(root, 'Writes a sourced report.', { x: L, y: 90, size: 140, accent: [3] });
      S.win = win(root, L, 320, W - 2 * L, 690, ['s20_done_tall']);
      const d = G.done_tall;
      S.k = 1.5;
      S.y0 = d.status.y - 150; S.y1 = d.reportH1.y - 40;
      S.cx = d.reportH1.x - 26;
      S.ul = reg(el('div', { class: 'abs', style: 'background:var(--accent);border-radius:4px' }, S.win.card), { o: 0 });
    },
    run(t, b, S) {
      push(t, S, 'report', 'time', 0.03);
      rise(t, S.h, -0.4 + beatOf('report'), null, { stagger: 0.06 });
      const sc = ease.inOut(seg(t, 'report', 'report_title')) + 0.06 * seg(t, 'report_title', 'time');
      const v = { cx: S.cx, cy: lerp(S.y0, S.y1, sc), k: S.k };
      show(S.win, 's20_done_tall', v);
      // report H1 glyphs span x 384–1355, baseline region ends y≈876 (measured in s20_done_tall)
      const r = G.done_tall.reportH1, u = spHit(t, 'report_title', 'snappy'), p = loc(v, 384, 884);
      put(S.ul, { o: u > 0.002 ? 1 : 0, x: p.x, y: p.y, css: { width: 971 * u * v.k + 'px', height: '6px' } });
    },
  });

  // ================================================================ 4 · time  (b24 → b28): the proof number
  scene({
    name: 'time', from: 'time', to: 'memory',
    build(root, S) {
      S.num = line(root, '74 s', { x: L, y: 210, size: 400, color: 'var(--accent)' });
      S.digits = S.num.words[0];
      S.sub = line(root, 'from topic to sourced report', { x: L + 10, y: 660, size: 88 });
      // the real finished state: "Research complete", "Agent log", "Total run time: 74.1s" (text ends at x≈518)
      const st = G.done.status, rt = G.done.runTime;
      S.v = { cx: st.x - 16, cy: st.y - 16, k: 2.2 };
      S.ww = 330 * S.v.k; S.wh = (rt.y + 30 - S.v.cy) * S.v.k;
      S.win = win(root, 0, 0, S.ww, S.wh, ['s13_done_top']);
    },
    run(t, b, S) {
      push(t, S, 'time', 'memory', 0.04);
      rise(t, S.num, ['time', 'time'], null, { preset: 'heavy' });
      const n = Math.round(74 * ease.out(seg(t, 'time', 25.5)));
      put(S.digits, { text: String(n) });
      rise(t, S.sub, 'time_sub', null, { stagger: 0.02, preset: 'snappy' });
      cardRise(t, S.win, W - L - S.ww, 260, beatOf('time') + 1, 'default');   // beside the number, sub line runs under both
      show(S.win, 's13_done_top', S.v);
    },
  });

  // ================================================================ 5 · memory  (b28 → b32)
  scene({
    name: 'memory', from: 'memory', to: 'graph',
    build(root, S) {
      S.h1 = line(root, 'Saved to memory.', { x: L, y: 90, size: 150, accent: [2] });
      S.h2 = line(root, 'The next run starts smarter.', { x: L, y: 100, size: 118 });
      const m = G.memory;
      // tight on Past Sessions; the click pulls back so the restored report (its H1) fills the main column
      S.vTight = { cx: 6, cy: G.memory.pastSessions.y - 34, k: 3.2 };
      S.vWide = { cx: 6, cy: G.memory_loaded.reportH1.y - 24, k: 2 };
      S.win = win(root, L, 320, W - 2 * L, 690, ['s00_idle', 's17_memory', 's18_memory_hover', 's19_memory_loaded']);
      S.cur = cursor(root);
    },
    run(t, b, S) {
      push(t, S, 'memory', 'graph', 0.03);
      rise(t, S.h1, -0.4 + beatOf('memory'), beatOf('recall') - 0.2, { stagger: 0.06, exit: 0.2 });
      rise(t, S.h2, 'recall', null, { stagger: 0.05 });
      const pin = beatOf('recall') - 0.15, vt = S.vTight, vw = S.vWide;
      const v = { cx: trk(t, [[0, vt.cx], [pin, vw.cx]]), cy: trk(t, [[0, vt.cy], [pin, vw.cy]]), k: trk(t, [[0, vt.k], [pin, vw.k]]) };
      // the window is only as wide as the sidebar until the click, then grows with the pull-back to show the report
      const sideW = (G.memory.session.x * 2 + G.memory.session.w - vt.cx) * vt.k;
      put(S.win.card, { css: { width: trk(t, [[0, sideW], [pin, W - 2 * L]]) + 'px' } });
      show(S.win, pickShot(t, [[0, 's00_idle'], ['memory_in', 's17_memory'], [beatOf('recall') - 0.3, 's18_memory_hover'], ['recall', 's19_memory_loaded']]), v);
      const s = G.memory.session, p = loc(vt, s.x + s.w * 0.62, s.y + s.h * 0.55);
      moveCursor(t, S.cur, [[0, W - 200, H + 60], [beatOf('memory') + 0.6, L + p.x, 320 + p.y], [beatOf('recall') + 0.8, L + p.x + 420, 320 + p.y + 180]],
        'recall', beatOf('memory') + 0.6, beatOf('graph'));
    },
  });

  // ================================================================ 6 · graph  (b32 → b36): the real agent graph, walked
  // GRAPH_DIAGRAM rows in app.py: 3 [Planner] · 6 [Searcher] · 9 [Reader] · 12 [Critic] · 15 [Writer]
  const NODES = { Planner: 3, Searcher: 6, Reader: 9, Critic: 12, Writer: 15 };
  const WALK = [[32, 'Planner'], [32.5, 'Searcher'], [33, 'Reader'], [33.5, 'Critic'], [34, 'Searcher'], [34.5, 'Reader'], [35, 'Critic'], [35.5, 'Writer']];
  scene({
    name: 'graph', from: 'graph', to: 'end',
    build(root, S) {
      S.h1 = line(root, 'One LangGraph graph.', { x: L, y: 330, size: 104 });
      S.h2 = line(root, 'Five agents.', { x: L, y: 470, size: 104, accent: [0] });
      // the st.code card around the diagram: the <code> box plus Streamlit's 16 px padding, clipped to the 240 px sidebar
      const code = G.idle.sideCode, sc = { x: code.x - 16, y: code.y - 16, w: 240, h: code.h + 32 };
      S.v = { cx: sc.x - 12, cy: sc.y - 12, k: 2 };
      const w = (sc.w + 24) * 2, h = (sc.h + 24) * 2;
      S.x = W - L - w; S.y = (H - h) / 2;
      S.win = win(root, S.x, S.y, w, h, ['s00_idle']);
      S.box = reg(el('div', { class: 'abs', style: 'border:3px solid var(--accent);border-radius:8px;background:color-mix(in srgb, var(--accent) 10%, transparent);box-sizing:border-box' }, S.win.card), { o: 0 });
      const ls = G.idle.sideLines, cw = ls[0].w / 'User Query'.length;
      S.rows = Object.fromEntries(Object.entries(NODES).map(([k, i]) => [k, { x: ls[i].x + cw - 5, y: ls[i].y - 3, w: (k.length + 2) * cw + 10, h: ls[i].h + 6 }]));
    },
    run(t, b, S) {
      push(t, S, 'graph', 'end', 0.035);
      rise(t, S.h1, -0.4 + beatOf('graph'), null, { stagger: 0.06 });
      rise(t, S.h2, beatOf('graph') + 0.5, null, { stagger: 0.06 });
      cardRise(t, S.win, S.x, S.y, -0.6 + beatOf('graph'), 'default');
      show(S.win, 's00_idle', S.v);
      const keys = WALK.map(([bb, n], i) => [i === 0 ? 0 : bt(bb) - C.leadFor('snappy'), S.rows[n].y, S.rows[n].y + S.rows[n].h]);
      const ind = Motion.indicator(t, keys);
      const wv = trk(t, WALK.map(([bb, n], i) => [i === 0 ? 0 : bb - 0.1, S.rows[n].w], 'snappy'));
      const on = spHit(t, 'graph', 'snappy'), p = loc(S.v, S.rows.Planner.x, ind.start);
      put(S.box, { o: on > 0.002 ? 1 : 0, x: p.x, y: p.y, sx: 0.85 + 0.15 * on, css: { width: wv * S.v.k + 'px', height: ind.size * S.v.k + 'px' } });
    },
  });

  // ================================================================ 7 · end  (b36 → b40): the app's own lockup + CTA
  scene({
    name: 'end', from: 'end', to: 'done',
    build(root, S) {
      root.style.background = 'var(--card)';
      S.push = reg(el('div', { class: 'abs', style: `width:${W}px;height:${H}px;transform-origin:${L}px ${H / 2}px` }, root));
      const h = G.idle.h1text, c = G.idle.caption;
      S.k = 2.7;
      S.v = { cx: h.x - 6, cy: h.y - 8, k: S.k };
      const w = (h.x + h.w + 12 - S.v.cx) * S.k, hh = (c.y + c.h + 6 - S.v.cy) * S.k;
      S.mask = el('div', { class: 'abs', style: `overflow:hidden;width:${w}px;height:${hh}px` }, S.push);
      reg(S.mask, { x: L - 6 * S.k, y: 190 });
      S.win = win(S.mask, 0, 0, w, hh, ['s00_idle'], 'abs win');
      S.cta = line(S.push, 'Try the live demo', { x: L, y: 590, size: 136, cls: 'ui', accent: [2, 3] });
      S.url = line(S.push, 'ayushdas4890-ai-research-assistant-pipeline-app-1sjuvf.streamlit.app', { x: L + 4, y: 800, size: 54, cls: 'ui', color: 'var(--ink-2)' });
      S.url.el.style.fontWeight = '400';
      S.sweep = reg(el('div', { class: 'abs', style: 'top:748px;height:8px;background:var(--accent);border-radius:4px' }, S.push), { o: 0 });
    },
    run(t, b, S) {
      put(S.push, { s: 1 + 0.06 * ease.inOut(seg(t, 'end', 'done')) });
      const p = spHit(t, 'end', 'heavy');
      put(S.win.card, { y: (1 - p) * 360 });
      show(S.win, 's00_idle', S.v);
      rise(t, S.cta, 'cta', null, { stagger: 0.05, preset: 'snappy' });
      rise(t, S.url, 'url', null, { preset: 'snappy' });
      // the hold is re-lit: an underline sweeps through the CTA (enters left, leaves right)
      const cw = 1110, sw = Motion.indicator(t, [[0, L, L], [bt(38.5), L, L + cw], [bt(39.25), L + cw, L + cw]]);
      put(S.sweep, { o: sw.size > 0.5 ? 1 : 0, x: sw.start, css: { width: sw.size + 'px' } });
    },
  });

  C.start();
})();
