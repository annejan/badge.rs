// badge.rs: badger badger badger ... mushroom! ... a snake! With love to Weebl's badgers,
// made with Badge.Team's own badger, snake and Konsool (CC BY 4.0) and a fly agaric drawn
// here. Click a badger and it hops (five times and it falls over); click anywhere else to go
// to badge.team; type "konsool" and one flies by. No sound, no libraries, nothing inline.
'use strict';

const BEAT = 0.5;                  // 120 BPM
const BADGER_BEATS = 24;           // a badger pops up on each beat, then
const SNAKE_BEATS = 16;            // the snake rides through, and back again
const CYCLE = (BADGER_BEATS + SNAKE_BEATS) * BEAT;
const MAX_BADGERS = 12;
const COLOURS = ['#fdc549', '#e94076', '#009ecf', '#7ac29b', '#e7247f'];
const MUSHROOM_BEATS = [12, 16];   // after the twelfth badger: mushroom, mushroom!

// A fly agaric, 16 x 16 pixels: k outline, R red, r shade, W white spots, c stem, s its shadow.
const MUSHROOM = [
  '.....kkkkkk.....',
  '...kkRRRRRRkk...',
  '..kRRWWRRRRRRk..',
  '.kRRWWWRRRWWRRk.',
  '.kRRRWRRRRWWRRk.',
  'kRRRRRRRWRRRRRRk',
  'kRWWRRRRRRRWWRRk',
  'kRWWRRRRRRRWWRrk',
  'krRRRRWWRRRRRrrk',
  '.krrrrrrrrrrrrk.',
  '..kkkkcccckkkk..',
  '.....kccssk.....',
  '.....kccssk.....',
  '....kcccccsk....',
  '....kcccccsk....',
  '.....kkkkkk.....',
];
const PIXEL = { k: '#3b1f2b', R: '#e5332a', r: '#a8201a', W: '#ffffff', c: '#f3e9d2', s: '#d8c9a8' };
function mushroomSprite() {
  const c = document.createElement('canvas');
  c.width = c.height = 16;
  const g = c.getContext('2d');
  MUSHROOM.forEach((row, y) => [...row].forEach((p, x) => {
    if (PIXEL[p]) { g.fillStyle = PIXEL[p]; g.fillRect(x, y, 1, 1); }
  }));
  return c;
}

const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const canvas = document.getElementById('stage');

if (canvas && !reduceMotion) start();

function start() {
  const ctx = canvas.getContext('2d');
  const badger = new Image();
  badger.src = '/badger.webp';
  const snake = new Image();
  snake.src = '/snake.webp';
  const konsool = new Image();
  konsool.src = '/konsool.webp';
  const mushroom = mushroomSprite();
  document.documentElement.classList.add('live');

  // Pause and play, for everything that moves (WCAG 2.2.2); P does the same. Paused, the
  // clock stands still, so everything picks up where it was.
  let pausedAt = null, pausedFor = 0;
  const clock = () => (pausedAt ?? performance.now()) - pausedFor;
  const pauseButton = document.getElementById('pause');
  function setPaused(on) {
    if (on === (pausedAt !== null)) return;
    if (on) pausedAt = performance.now();
    else {
      pausedFor += performance.now() - pausedAt;
      pausedAt = null;
      requestAnimationFrame(frame);
    }
    pauseButton.setAttribute('aria-pressed', String(on));
    pauseButton.textContent = on ? 'Play' : 'Pause';
  }
  pauseButton.hidden = false;
  pauseButton.addEventListener('click', () => setPaused(pausedAt === null));
  addEventListener('keydown', (event) => {
    if ((event.key === 'p' || event.key === 'P') && !event.target.closest?.('button')) setPaused(pausedAt === null);
  });

  // Each badger's box on screen this frame, front ones last; and what's been done to them
  // this round: hops, and whether it fell over.
  let boxes = [];
  let poked = new Map();
  let round = -1;
  const hit = (event) => {
    for (let i = boxes.length - 1; i >= 0; i -= 1) {
      const b = boxes[i];
      if (event.clientX > b.x && event.clientX < b.x + b.w && event.clientY > b.y && event.clientY < b.y + b.h) return b.k;
    }
    return -1;
  };
  canvas.addEventListener('click', (event) => {
    const k = hit(event);
    if (k < 0) {
      location.href = 'https://badge.team/';
      return;
    }
    const p = poked.get(k) || { hops: 0, at: -10 };
    p.hops += 1;
    p.at = clock() / 1000;
    poked.set(k, p);
  });

  // Type konsool and one flies by.
  let typed = '';
  let flyby = -10;
  addEventListener('keydown', (event) => {
    if (event.key.length !== 1) return;
    typed = (typed + event.key.toLowerCase()).slice(-7);
    if (typed === 'konsool') flyby = clock() / 1000;
  });

  let W = 0, H = 0, dpr = 1;
  function layout() {
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = innerWidth;
    H = innerHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
  }
  layout();
  addEventListener('resize', layout);

  const confetti = Array.from({ length: 90 }, () => ({
    x: Math.random(), y: Math.random(), r: Math.random() * Math.PI * 2,
    v: 0.04 + Math.random() * 0.08, spin: (Math.random() - 0.5) * 4,
    size: 4 + Math.random() * 6, colour: COLOURS[Math.floor(Math.random() * COLOURS.length)],
    shape: Math.floor(Math.random() * 3),
  }));

  // Where badger k stands: rows from the front, the back rows smaller and higher up.
  function spot(k, size) {
    const cols = Math.max(3, Math.min(6, Math.floor(W / (size * 0.85))));
    const row = Math.floor(k / cols);
    const col = k % cols;
    const inRow = Math.min(cols, MAX_BADGERS - row * cols);
    const tall = H > W;                                  // phones: more rows, stacked higher
    const scale = 1 - row * (tall ? 0.12 : 0.25);
    const gap = W / (inRow + 0.4);
    const x = gap * (col + 0.7) + (row % 2 ? gap * 0.25 : 0);
    const ground = H * 0.92 - row * size * (tall ? 0.8 : 0.5);
    return { x, ground, scale, row };
  }

  const ease = (a, b, t) => Math.min(1, Math.max(0, (t - a) / (b - a)));
  const back = (u) => 1 + 2.7 * (u - 1) ** 3 + 1.7 * (u - 1) ** 2;   // ease out, with overshoot

  function drawBadger(k, beat, phase, size, sink) {
    const { x, ground, scale } = spot(k, size);
    const age = beat - k + phase;                       // beats since this one popped up
    if (age < 0) return;
    const pop = back(Math.min(1, age / 0.5));
    const squat = Math.exp(-8 * phase);
    const h = size * scale;
    const w = h * badger.width / badger.height;
    const tilt = ((beat + k) % 2 ? 1 : -1) * 0.07 * (1 - squat * 0.5);
    const p = poked.get(k);
    const since = p ? clock() / 1000 - p.at : 10;
    const fallen = p && p.hops >= 5;
    const hop = !fallen && since < 0.45 ? Math.sin(Math.PI * since / 0.45) * h * 0.3 : 0;
    const fall = fallen ? -1.45 * Math.min(1, since / 0.5) : 0;   // over on its back, slowly
    const y = ground + h * (1 - pop) + sink * (H - ground + h) - hop;   // duck, right off the screen
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(fallen ? fall : tilt);
    if (!fallen) ctx.scale(1 + 0.06 * squat, 1 - 0.09 * squat);
    ctx.drawImage(badger, -w / 2, -h, w, h);
    ctx.restore();
    boxes.push({ k, x: x - w / 2, y: y - h, w, h });
    if (since < 0.6 && !fallen) word('!', x + w * 0.3, y - h * 1.05, h * 0.25, COLOURS[p.hops % COLOURS.length], 1, 0);
  }

  function word(text, x, y, size, colour, punch, shake) {
    ctx.save();
    ctx.translate(x + (Math.random() - 0.5) * shake, y + (Math.random() - 0.5) * shake);
    ctx.scale(punch, punch);
    ctx.font = `900 ${size}px Impact, 'Arial Black', sans-serif`;
    const fit = Math.min(1, W * 0.8 / ctx.measureText(text).width);   // phones: shrink to fit
    ctx.scale(fit, fit);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.lineJoin = 'round';
    ctx.lineWidth = size * 0.14;
    ctx.strokeStyle = '#662483';
    ctx.strokeText(text, 0, 0);
    ctx.fillStyle = colour;
    ctx.fillText(text, 0, 0);
    ctx.restore();
  }

  const t0 = clock();
  let last = t0;
  function frame() {
    if (pausedAt !== null) return;
    const now = clock();
    const dt = Math.min(0.1, (now - last) / 1000);
    last = now;
    const t = ((now - t0) / 1000) % CYCLE;
    const r = Math.floor((now - t0) / 1000 / CYCLE);
    if (r !== round) {                                    // a new round: all badgers back up
      round = r;
      poked = new Map();
    }
    boxes = [];
    const beat = Math.floor(t / BEAT);
    const phase = (t % BEAT) / BEAT;
    const snakeTime = Math.max(0, t - BADGER_BEATS * BEAT);
    const snaking = beat >= BADGER_BEATS;

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const sky = ctx.createLinearGradient(0, 0, 0, H);
    sky.addColorStop(0, '#1b1532');
    sky.addColorStop(1, snaking ? '#4a1d4f' : '#2f2160');
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, W, H);

    // Confetti, falling a little faster on the beat (and a lot faster for the snake).
    const kick = Math.exp(-6 * phase);
    for (const c of confetti) {
      c.y += c.v * dt * (1 + kick + (snaking ? 3 : 0));
      c.r += c.spin * dt;
      if (c.y > 1.05) { c.y = -0.05; c.x = Math.random(); }
      ctx.save();
      ctx.translate(c.x * W, c.y * H);
      ctx.rotate(c.r);
      ctx.fillStyle = c.colour;
      if (c.shape === 0) ctx.fillRect(-c.size / 2, -c.size / 4, c.size, c.size / 2);
      else if (c.shape === 1) { ctx.beginPath(); ctx.arc(0, 0, c.size / 3, 0, Math.PI * 2); ctx.fill(); }
      else { ctx.beginPath(); ctx.moveTo(0, -c.size / 2); ctx.lineTo(c.size / 2, c.size / 2); ctx.lineTo(-c.size / 2, c.size / 2); ctx.fill(); }
      ctx.restore();
    }

    const size = Math.min(H * 0.34, W * 0.36);
    if (badger.complete && badger.naturalWidth) {
      const count = Math.min(MAX_BADGERS, beat + 1);
      const sink = snaking ? ease(0, 2 * BEAT, snakeTime) ** 2 : 0;
      const order = Array.from({ length: count }, (_, k) => k).sort((a, b) => spot(b, size).row - spot(a, size).row);
      for (const k of order) drawBadger(k, Math.min(beat, BADGER_BEATS), snaking ? 0 : phase, size, sink);
    }

    const mushrooming = beat >= MUSHROOM_BEATS[0] && beat < MUSHROOM_BEATS[1];
    if (mushrooming) {
      // A fly agaric pops up between the badgers, bouncing on the beat.
      const m = Math.min(H * 0.26, W * 0.3);
      const up = back(Math.min(1, (t - MUSHROOM_BEATS[0] * BEAT) / 0.4));
      const bounce = Math.exp(-8 * phase) * m * 0.08;
      ctx.save();
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(mushroom, W / 2 - m / 2, H * 0.62 - m * up + bounce, m, m);
      ctx.restore();
      word('MUSHROOM!', W / 2, H * 0.3, Math.min(W * 0.12, H * 0.14), COLOURS[beat % COLOURS.length], 1 + 0.25 * kick, 0);
    } else if (!snaking) {
      word('BADGER', W / 2, H * 0.3, Math.min(W * 0.16, H * 0.16), COLOURS[beat % COLOURS.length], 1 + 0.25 * kick, 0);
    } else if (snake.complete && snake.naturalWidth) {
      // The snake rides through from the left, the board's rounded nose first, hovering; then
      // turns and comes back the other way, a bit higher up.
      const pass = snakeTime / (SNAKE_BEATS * BEAT / 2);
      const back = pass >= 1;
      const u = pass % 1;
      const sh = Math.min(H * 0.45, W * 0.5);
      const sw = sh * snake.width / snake.height;
      const across = -sw * 0.6 + u * (W + sw * 1.2);
      const x = back ? W - across : across;
      const y = H * (back ? 0.55 : 0.62) + Math.sin(snakeTime * 7) * sh * 0.04;
      ctx.save();
      ctx.translate(x, y);
      if (back) ctx.scale(-1, 1);
      // Speed lines behind the board.
      ctx.globalAlpha = 0.6;
      for (let i = 0; i < 6; i += 1) {
        ctx.fillStyle = COLOURS[i % COLOURS.length];
        ctx.fillRect(-sw * 0.3 - W - sw, sh * (0.1 + i * 0.06), W + sw, sh * 0.02);
      }
      ctx.globalAlpha = 1;
      ctx.rotate(Math.sin(snakeTime * 3.5) * 0.04);
      ctx.drawImage(snake, -sw / 2, -sh / 2, sw, sh);
      ctx.restore();
      const text = ['SNAKE!', 'A SNAKE!', 'SNAAAKE!', "OH, IT'S A SNAKE!"][Math.floor((beat - BADGER_BEATS) / 4)];
      word(text, W / 2, H * 0.3, Math.min(W * 0.13, H * 0.15), '#e94076', 1 + 0.15 * kick, Math.min(W, H) * 0.02);
    }

    // The Konsool flying by, when called for.
    const fly = now / 1000 - flyby;
    if (fly < 4 && konsool.complete && konsool.naturalWidth) {
      const kh = Math.min(H * 0.4, W * 0.45);
      const kw = kh * konsool.width / konsool.height;
      const x = W + kw - fly / 4 * (W + kw * 2);
      const y = H * 0.35 + Math.sin(fly * 4) * kh * 0.08;
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(Math.sin(fly * 3) * 0.12);
      ctx.drawImage(konsool, -kw / 2, -kh / 2, kw, kh);
      ctx.restore();
      word('KONSOOL!', W / 2, H * 0.62 - kh * 0.1, Math.min(W * 0.1, H * 0.11), '#7ac29b', 1, 0);
    }

    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}
