// La scène du jeu (720 × 980, sol à partir de y = 560) : mêmes positions que fight-view.ts / idle-scene.ts.
const fs = require('fs');
const { HEROES, ENEMIES } = require('./cast5.cjs');
const { SHARED_DEFS } = require('./kit.cjs');
const W = 720, H = 980, GT = 560, SQ = 0.8;
// lignes de devant écartées (300 / 420 au lieu de 315 / 405) pour que les deux camps ne se chevauchent pas
const HERO_X = { 3: 95, 4: 95, 2: 198, 0: 300, 1: 300 }, ENEMY_X = { 0: 420, 1: 420, 2: 522, 3: 625, 4: 625 };
const ROW_DY = { 0: 90, 3: 90, 2: 180, 1: 270, 4: 270 };
const px = (x) => 360 + (x - 360) * SQ;
function rnd(seed) { let s = seed; return () => ((s = (s * 16807) % 2147483647) / 2147483647); }
const r = rnd(21);

function foliage(x, y, w, h, light, mid, dark, n = 12) {
  let s = `<ellipse cx="${x}" cy="${y + h * 0.15}" rx="${w * 0.55}" ry="${h * 0.42}" fill="${dark}"/>`;
  for (let i = 0; i < n; i++) {
    const a = r() * Math.PI * 2, d = r() * 0.8, cx = x + Math.cos(a) * w * 0.4 * d, cy = y + Math.sin(a) * h * 0.32 * d - h * 0.05, rr = (0.16 + r() * 0.12) * w;
    const lit = (cx - x) / w - (cy - y) / h;
    s += `<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${rr.toFixed(1)}" fill="${lit > 0.15 ? light : lit > -0.15 ? mid : dark}"/>`;
  }
  return s;
}

function background() {
  let s = `<defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f8fe2"/><stop offset="0.55" stop-color="#93cdf6"/><stop offset="0.9" stop-color="#fdeccb"/><stop offset="1" stop-color="#ffdca8"/></linearGradient>
    <radialGradient id="sun" cx="0.78" cy="0.3" r="0.6"><stop offset="0" stop-color="#fffbe6"/><stop offset="0.1" stop-color="#fff2c0" stop-opacity="0.9"/><stop offset="0.4" stop-color="#ffe7a8" stop-opacity="0.3"/><stop offset="1" stop-color="#ffe7a8" stop-opacity="0"/></radialGradient>
    <linearGradient id="grass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a5d672"/><stop offset="0.3" stop-color="#7cbd58"/><stop offset="1" stop-color="#3b7a3c"/></linearGradient>
    <linearGradient id="fog" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff4dc" stop-opacity="0"/><stop offset="1" stop-color="#fff4dc" stop-opacity="0.7"/></linearGradient>
    <radialGradient id="plat" cx="0.5" cy="0.4" r="0.6"><stop offset="0" stop-color="#f0e2c4"/><stop offset="0.7" stop-color="#d9c6a0"/><stop offset="1" stop-color="#b8a27c"/></radialGradient>
    <radialGradient id="vig" cx="0.5" cy="0.55" r="0.75"><stop offset="0.6" stop-color="#0a0820" stop-opacity="0"/><stop offset="1" stop-color="#0a0820" stop-opacity="0.38"/></radialGradient>
    <filter id="far"><feGaussianBlur stdDeviation="1.8"/></filter><filter id="mid"><feGaussianBlur stdDeviation="0.8"/></filter>
    <filter id="tex" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.03 0.1" numOctaves="4" seed="8"/><feColorMatrix values="0 0 0 0 0.2  0 0 0 0 0.3  0 0 0 0 0.1  0 0 0 0.35 0"/></filter>
    <filter id="stoneTex" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.5 0.9" numOctaves="3" seed="2"/><feColorMatrix values="0 0 0 0 0.3  0 0 0 0 0.22  0 0 0 0 0.12  0 0 0 0.22 0"/></filter>
    <clipPath id="platClip"><ellipse cx="360" cy="795" rx="352" ry="168"/></clipPath>
  </defs>`;
  s += `<rect width="${W}" height="${GT + 20}" fill="url(#sky)"/><rect width="${W}" height="${GT + 20}" fill="url(#sun)"/>`;
  // nuages
  const cloud = (x, y, k) => { let c = `<g filter="url(#mid)" transform="translate(${x} ${y}) scale(${k})"><ellipse cx="0" cy="18" rx="120" ry="20" fill="#cfdcec"/>`;
    for (const [cx, cy, rr] of [[-70, 8, 34], [-30, -10, 46], [20, -22, 52], [70, -2, 40], [100, 12, 26], [-100, 16, 22]]) c += `<circle cx="${cx}" cy="${cy}" r="${rr}" fill="#e9f0f8"/>`;
    for (const [cx, cy, rr] of [[-26, -18, 34], [26, -30, 38], [70, -10, 26]]) c += `<circle cx="${cx + 6}" cy="${cy - 6}" r="${rr}" fill="#fff"/>`; return c + '</g>'; };
  s += cloud(150, 250, 0.7) + cloud(430, 170, 0.5) + cloud(640, 330, 0.6);
  // montagnes lointaines à facettes
  let far = '';
  for (const [x, top, w] of [[60, 400, 150], [230, 340, 190], [420, 390, 150], [590, 330, 200], [730, 400, 140]]) {
    far += `<path d="M${x - w} 545 L${x} ${top} L${x + w} 545 Z" fill="#a9c2e0"/><path d="M${x} ${top} L${x + w} 545 L${x + w * 0.25} 545 Z" fill="#cbdcef"/>`;
    far += `<path d="M${x} ${top} L${x - w * 0.2} ${top + 44} L${x - w * 0.05} ${top + 37} L${x + w * 0.06} ${top + 52} L${x + w * 0.24} ${top + 42} Z" fill="#fff"/><path d="M${x} ${top} L${x - w * 0.2} ${top + 44} L${x - w * 0.07} ${top + 38} Z" fill="#dbe6f3"/>`;
  }
  s += `<g filter="url(#far)">${far}</g><rect y="400" width="${W}" height="160" fill="url(#fog)"/>`;
  // château au loin
  s += `<g transform="translate(470 452)" filter="url(#mid)">
    <path d="M0 96 L0 30 L-5 30 L-5 16 L3 16 L3 23 L10 23 L10 16 L18 16 L18 23 L25 23 L25 16 L33 16 L33 30 L28 30 L28 96 Z" fill="#b5ac9f"/><path d="M18 16 L18 23 L25 23 L25 16 L33 16 L33 30 L28 30 L28 96 L16 96 L16 30 Z" fill="#d4ccc0"/>
    <path d="M14 16 L14 -10 L34 -3 L14 4" fill="#e0344a"/><path d="M13 16 L13 -12" stroke="#5a4a3a" stroke-width="2"/>
    <path d="M36 96 L36 50 L100 50 L100 96 Z" fill="#a9a094"/><path d="M70 50 L100 50 L100 96 L70 96 Z" fill="#c8c0b4"/>
    <path d="M36 50 h8 v-8 h8 v8 h8 v-8 h8 v8 h8 v-8 h8 v8 h8 v-8 h8 v8" fill="none" stroke="#a9a094" stroke-width="8"/>
    <path d="M100 96 L100 22 L95 22 L95 8 L103 8 L103 15 L110 15 L110 8 L118 8 L118 15 L125 15 L125 8 L133 8 L133 22 L128 22 L128 96 Z" fill="#b5ac9f"/><path d="M118 8 L118 15 L125 15 L125 8 L133 8 L133 22 L128 22 L128 96 L116 96 L116 22 Z" fill="#d4ccc0"/>
    <path d="M114 8 L114 -18 L134 -11 L114 -4" fill="#e0344a"/><path d="M113 8 L113 -20" stroke="#5a4a3a" stroke-width="2"/>
    <path d="M58 96 v-22 q10 -14 20 0 v22 Z" fill="#4a423c"/><path d="M8 50 q5 -8 10 0 v14 h-10 Z M108 44 q5 -8 10 0 v14 h-10 Z" fill="#4a423c"/></g>`;
  // forêt à l'horizon
  let forest = '';
  for (let i = 0; i < 26; i++) forest += foliage(i * 30 + r() * 16 - 10, 536 + r() * 12, 52 + r() * 18, 46 + r() * 12, '#9fd27e', '#79b264', '#4f8a52', 10);
  s += `<g filter="url(#mid)">${forest}</g>`;
  // herbe du terrain (vue plongeante)
  s += `<rect y="${GT - 6}" width="${W}" height="${H - GT + 6}" fill="url(#grass)"/><rect y="${GT - 6}" width="${W}" height="${H - GT + 6}" filter="url(#tex)" opacity="0.55"/>`;
  // palissade et bannières au bord du terrain
  for (let x = -10; x < W + 20; x += 46) s += `<path d="M${x} 584 L${x} 552 L${x + 6} 544 L${x + 12} 552 L${x + 12} 584 Z" fill="#7a5232"/><path d="M${x + 6} 544 L${x + 12} 552 L${x + 12} 584 L${x + 7} 584 Z" fill="#9a6c44"/>`;
  s += `<path d="M-10 560 L${W + 10} 560 L${W + 10} 568 L-10 568 Z" fill="#6a4628"/><path d="M-10 560 L${W + 10} 560" stroke="#b08458" stroke-width="2"/>`;
  for (const [x, c1, c2] of [[130, '#e0344a', '#a01c30'], [590, '#3f78d8', '#27509a']]) s += `<path d="M${x} 590 L${x} 470" stroke="#5a3c22" stroke-width="6"/><path d="M${x} 590 L${x} 470" stroke="#8a6238" stroke-width="2"/><path d="M${x + 3} 474 L${x + 52} 480 L${x + 40} 500 L${x + 52} 522 L${x + 3} 528 Z" fill="${c1}"/><path d="M${x + 3} 500 L${x + 40} 500 L${x + 52} 522 L${x + 3} 528 Z" fill="${c2}"/><circle cx="${x + 22}" cy="500" r="8" fill="#f2c25a"/><circle cx="${x}" cy="468" r="6" fill="#f2c25a"/>`;

  // ---------- plateforme de pierre (arène), vue plongeante ----------
  const cx = 360, cy = 795, rx = 352, ry = 168;
  s += `<ellipse cx="${cx}" cy="${cy + 26}" rx="${rx + 14}" ry="${ry + 12}" fill="#1e3a1c" opacity="0.45" filter="url(#far)"/>`;
  s += `<ellipse cx="${cx}" cy="${cy + 16}" rx="${rx}" ry="${ry}" fill="#7c6a50"/><ellipse cx="${cx}" cy="${cy + 9}" rx="${rx}" ry="${ry}" fill="#99866a"/>`;
  s += `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="url(#plat)"/>`;
  // dalles : 3 anneaux découpés en secteurs, teintes légèrement différentes
  const pt = (k, a) => `${(cx + rx * k * Math.cos(a)).toFixed(1)} ${(cy + ry * k * Math.sin(a)).toFixed(1)}`;
  let slabs = '';
  const rings = [[0.36, 0.68, 10, 0.2], [0.68, 1, 16, 0]];
  for (const [k0, k1, n, off] of rings) for (let i = 0; i < n; i++) {
    const a0 = off + (i / n) * Math.PI * 2, a1 = off + ((i + 1) / n) * Math.PI * 2;
    const tint = ['#e8d8b6', '#dccaa4', '#f2e4c8', '#d2be98'][Math.floor(r() * 4)];
    slabs += `<path d="M${pt(k0, a0)} L${pt(k1, a0)} A${rx * k1} ${ry * k1} 0 0 1 ${pt(k1, a1)} L${pt(k0, a1)} A${rx * k0} ${ry * k0} 0 0 0 ${pt(k0, a0)} Z" fill="${tint}" stroke="#8f7a58" stroke-width="2.2" stroke-linejoin="round"/>`;
    slabs += `<path d="M${pt(k0 + 0.02, a0 + 0.03)} L${pt(k1 - 0.02, a0 + 0.03)}" stroke="#fff8e6" stroke-width="1.6" opacity="0.7"/>`;
  }
  slabs += `<ellipse cx="${cx}" cy="${cy}" rx="${rx * 0.36}" ry="${ry * 0.36}" fill="#ecdcba" stroke="#8f7a58" stroke-width="2.2"/>`;
  // emblème central : étoile à 8 branches
  let star = '';
  for (let i = 0; i < 8; i++) { const a = (i / 8) * Math.PI * 2, b = a + Math.PI / 8, c = a - Math.PI / 8; star += `<path d="M${pt(0.3, a)} L${pt(0.11, b)} L${pt(0, 0)} L${pt(0.11, c)} Z" fill="${i % 2 ? '#c9a05a' : '#b58a44'}"/>`; }
  slabs += star + `<ellipse cx="${cx}" cy="${cy}" rx="${rx * 0.07}" ry="${ry * 0.07}" fill="#e6ac3c" stroke="#8a5a16" stroke-width="2"/>`;
  // fissures et mousse
  slabs += `<path d="M150 760 l22 10 l8 18 l20 6 M520 850 l-18 -12 l-6 -18 l-22 -8 M420 700 l14 12 l2 14" stroke="#7a6648" stroke-width="2" fill="none" opacity="0.8"/>`;
  for (let i = 0; i < 9; i++) { const a = r() * Math.PI * 2; const [x, y] = pt(0.9 + r() * 0.08, a).split(' ').map(Number); slabs += `<ellipse cx="${x}" cy="${y}" rx="${14 + r() * 14}" ry="${5 + r() * 4}" fill="#6fa852" opacity="0.8"/>`; }
  s += `<g clip-path="url(#platClip)">${slabs}<rect x="0" y="600" width="${W}" height="380" filter="url(#stoneTex)" opacity="0.5"/><ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="none" stroke="#fff8e6" stroke-width="3" opacity="0.5"/></g>`;

  // herbes, fleurs et pierres autour (plus grandes vers le bas)
  const tuft = (x, y, k, c1, c2) => `<g transform="translate(${x.toFixed(0)} ${y.toFixed(0)}) scale(${k.toFixed(2)})"><path d="M-8 0 Q-12 -16 -18 -22 Q-8 -16 -4 0 Z" fill="${c2}"/><path d="M-4 0 Q-3 -22 2 -30 Q2 -14 2 0 Z" fill="${c1}"/><path d="M1 0 Q6 -18 14 -24 Q8 -12 6 0 Z" fill="${c2}"/><path d="M4 0 Q12 -10 20 -12 Q12 -6 9 0 Z" fill="${c1}"/></g>`;
  for (let i = 0; i < 90; i++) {
    const x = r() * W, y = 590 + r() * 390;
    if (((x - cx) / (rx + 6)) ** 2 + ((y - cy - 6) / (ry + 14)) ** 2 < 1) continue;
    const k = 0.45 + ((y - 590) / 390) * 0.9;
    s += tuft(x, y, k, '#8fca68', '#5a9a46');
    if (r() > 0.75) s += `<g transform="translate(${(x + 6).toFixed(0)} ${(y - 20 * k).toFixed(0)}) scale(${k.toFixed(2)})"><circle r="4.4" fill="${r() > 0.5 ? '#fff3a0' : '#ffb0cf'}"/><circle r="1.8" fill="#f2a23a"/></g>`;
  }
  s += `<rect width="${W}" height="${H}" fill="url(#vig)"/>`;
  return s;
}

const KH = +(process.env.KH || 0.58), KG = +(process.env.KG || 0.54), KB = +(process.env.KB || 0.64);
const TOP = { protector: 10, warrior: 6, archer: 24, healer: 6, assassin: 24, grunt: 10, rogue: 44, brute: 10, shaman: 22, hunter: 24 };
function scene() {
  const cast = [];
  const heroTeam = { 0: 'protector', 1: 'warrior', 2: 'healer', 3: 'archer', 4: 'assassin' };
  const foeTeam = { 0: 'grunt', 1: 'rogue', 2: 'brute', 3: 'shaman', 4: 'hunter' };
  const hp = { protector: 1, warrior: 0.82, healer: 1, archer: 0.94, assassin: 0.7, grunt: 0.45, rogue: 0.8, brute: 0.9, shaman: 1, hunter: 0.66 };
  for (const [slot, name] of Object.entries(heroTeam)) cast.push({ name, c: HEROES[name], x: px(HERO_X[slot]), y: GT + ROW_DY[slot] + 56, flip: false, k: KH });
  for (const [slot, name] of Object.entries(foeTeam)) cast.push({ name, c: ENEMIES[name], x: px(ENEMY_X[slot]), y: GT + ROW_DY[slot] + 56, flip: true, k: name === 'brute' ? KB : KG });
  cast.sort((a, b) => a.y - b.y);
  let s = '', bars = '';
  for (const u of cast) {
    s += `<ellipse cx="${u.x}" cy="${u.y - 1}" rx="${62 * u.k}" ry="${14 * u.k}" fill="#2a1c10" opacity="0.4" filter="url(#g3)"/>`;
    const tx = u.flip ? u.x + 106 * u.k : u.x - 106 * u.k;
    const tr = `translate(${tx} ${u.y - 228 * u.k}) scale(${u.flip ? -u.k : u.k} ${u.k})`;
    s += `<g transform="${tr}">${u.c.glow}</g><g transform="${tr}" filter="url(#sil)">${u.c.body}</g>`;
    // barres de vie et d'énergie (comme dans le jeu)
    const by = u.y - 228 * u.k + TOP[u.name] * u.k - 14, w = 52;
    bars += `<rect x="${u.x - w / 2 - 2}" y="${by - 2}" width="${w + 4}" height="12" rx="5" fill="#120a1c" opacity="0.85"/><rect x="${u.x - w / 2}" y="${by}" width="${w * hp[u.name]}" height="8" rx="3.5" fill="${u.flip ? '#e5484d' : '#3ccf7a'}"/><rect x="${u.x - w / 2}" y="${by}" width="${w * hp[u.name]}" height="3" rx="1.5" fill="#fff" opacity="0.35"/>`;
    if (!u.flip) bars += `<rect x="${u.x - w / 2}" y="${by + 11}" width="${w * (0.3 + hp[u.name] * 0.5)}" height="3.4" rx="1.5" fill="#4fd1ff"/>`;
  }
  const defs = [...Object.values(HEROES), ...Object.values(ENEMIES)].map((c) => c.defs).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><defs>${SHARED_DEFS}${defs}</defs>${background()}${s}${bars}</svg>`;
}
fs.writeFileSync('scene.html', `<html><body style="margin:0;background:#000">${scene()}</body></html>`);
