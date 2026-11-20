// Planches de terrains de combat à faire redessiner par Hailuo : 3 terrains en hauteur par planche, au format que rend
// Hailuo (21:9, 3696 × 1584), et une bande noire en bas pour sa signature. Croquis simples : Hailuo fait le rendu.
// Même disposition pour tous (comme l'écran de combat) : ciel et décor lointain en haut, horizon vers le milieu,
// sol plat et dégagé en bas (là où se tiennent les 10 combattants), décor sur les bords seulement.
//   node terrains-ia.cjs 1 sortie.png   (1 à 4)
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const [, , which, out] = process.argv;
const W = 3696, H = 1584, PW = 1232, PH = 1440, G = 12;
const f = (n) => +n.toFixed(1);
let uid = 0;
// repère de chaque terrain : 1000 × 1200, horizon à y ≈ 600, combattants entre y ≈ 720 et 1120
const grad = (stops, vertical = true) => { const id = 'g' + uid++; return { id, def: `<linearGradient id="${id}" x1="0" y1="0" x2="${vertical ? 0 : 1}" y2="${vertical ? 1 : 0}">${stops.map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`).join('')}</linearGradient>` }; };
const R = (x, y, w, h, c, o = '') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${c}" ${o}/>`;
const P = (d, c, o = '') => `<path d="${d}" fill="${c}" ${o}/>`;
const E = (x, y, rx, ry, c, o = '') => `<ellipse cx="${x}" cy="${y}" rx="${rx}" ry="${ry}" fill="${c}" ${o}/>`;
const C = (x, y, r, c, o = '') => `<circle cx="${x}" cy="${y}" r="${r}" fill="${c}" ${o}/>`;
const S = (d, c, w, o = '') => `<path d="${d}" fill="none" stroke="${c}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" ${o}/>`;
const range = (y, peaks, c, seed = 1) => { let s = seed; const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647); let d = `M0 ${y}`; const n = peaks; for (let i = 0; i <= n; i++) { const x = i * 1000 / n, h = 80 + rnd() * 160; d += ` L${f(x - 500 / n)} ${f(y - h)} L${f(x)} ${f(y - h * 0.4 - 20)}`; } return P(d + ` L1000 ${y} Z`, c); };
const hills = (y, amp, c, seed = 1) => { let s = seed; const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647); let d = `M0 ${y}`; for (let i = 0; i <= 4; i++) { const x = i * 250; d += ` Q${f(x + 125)} ${f(y - amp * (0.5 + rnd()))} ${f(x + 250)} ${f(y - rnd() * amp * 0.3)}`; } return P(d + ` L1000 1200 L0 1200 Z`, c); };
const cloud = (x, y, k, c = '#fff', op = 1) => `<g opacity="${op}">${C(x, y, 40 * k, c)}${C(x + 45 * k, y - 18 * k, 52 * k, c)}${C(x + 100 * k, y, 42 * k, c)}${R(x, y, 100 * k, 40 * k, c)}</g>`;
const tree = (x, y, k, trunk, leaf) => R(x - 12 * k, y - 120 * k, 24 * k, 120 * k, trunk) + C(x, y - 150 * k, 70 * k, leaf) + C(x - 50 * k, y - 110 * k, 50 * k, leaf) + C(x + 50 * k, y - 110 * k, 50 * k, leaf);
const pine = (x, y, k, c, snow) => P(`M${x} ${y - 260 * k} L${x + 90 * k} ${y} L${x - 90 * k} ${y} Z`, c) + (snow ? P(`M${x} ${y - 260 * k} L${x + 36 * k} ${y - 156 * k} L${x - 36 * k} ${y - 156 * k} Z`, snow) : '');
const ground = (top, c1, c2) => { const g = grad([[0, c1], [1, c2]]); return { def: g.def, svg: R(0, top, 1000, 1200 - top, `url(#${g.id})`) }; };
const sky = (c1, c2) => { const g = grad([[0, c1], [1, c2]]); return { def: g.def, svg: R(0, 0, 1000, 700, `url(#${g.id})`) }; };
const arena = (c, line) => E(500, 920, 430, 175, c) + E(500, 920, 430, 175, 'none', `stroke="${line}" stroke-width="10"`) + E(500, 920, 250, 100, 'none', `stroke="${line}" stroke-width="6" opacity="0.6"`);

const T = {
  meadow: () => { const s = sky('#5aa8ff', '#cfe8ff'), g = ground(600, '#6cc04a', '#3e8a2a');
    return s.def + g.def + '|' + s.svg + C(760, 170, 70, '#fff3b0') + cloud(120, 160, 1.2) + cloud(520, 110, 0.9) + hills(600, 160, '#8fd06a', 3) + hills(640, 90, '#76c055', 5) + g.svg
      + R(110, 330, 70, 270, '#c9b089') + P('M145 300 L80 340 L210 340 Z', '#8a4a3a') + `<g transform="translate(145 330)">${[0, 1, 2, 3].map((i) => R(-8, -150, 16, 150, '#f4ecd8', `transform="rotate(${i * 90 + 20})"`)).join('')}${C(0, 0, 16, '#6a4a3a')}</g>`
      + [0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => R(i * 120, 640, 14, 70, '#9a6a3a')).join('') + R(0, 650, 1000, 12, '#9a6a3a') + R(0, 680, 1000, 12, '#9a6a3a')
      + arena('#c9a46a', '#a8844e') + E(70, 1080, 80, 60, '#e8c060') + E(930, 1060, 90, 66, '#e8c060') + [[200, 760], [820, 780], [120, 900], [880, 930]].map(([x, y]) => C(x, y, 10, '#ff6a8a') + C(x + 20, y + 8, 8, '#fff26a')).join(''); },
  bramble: () => { const s = sky('#1e4a2a', '#7ab86a'), g = ground(620, '#3a6a2a', '#1e3a18');
    return s.def + g.def + '|' + s.svg + P('M380 0 L460 0 L620 700 L300 700 Z', '#e8ffb0', 'opacity="0.25"') + [80, 220, 760, 900].map((x, i) => R(x - 40, 0, 80, 700, '#3a2a1a') + C(x, 60, 160, '#2a5a22')).join('') + range(640, 6, '#2a4a20', 9) + g.svg
      + S('M0 520 Q180 380 300 540', '#4a2a1a', 26) + S('M1000 500 Q820 380 700 560', '#4a2a1a', 26) + arena('#4a6a2a', '#2a3a14')
      + [[90, 1000], [930, 1020], [150, 760], [860, 780]].map(([x, y]) => R(x - 8, y - 40, 16, 40, '#e8d8c0') + E(x, y - 44, 36, 22, '#d0304a')).join('') + [[300, 300], [650, 260], [500, 420], [820, 480]].map(([x, y]) => C(x, y, 8, '#f8ff9a', 'opacity="0.9"')).join(''); },
  bayou: () => { const s = sky('#2a5a5a', '#bfe0c8'), g = ground(640, '#3a5a4a', '#22382e');
    return s.def + g.def + '|' + s.svg + E(500, 600, 600, 60, '#e8fff0', 'opacity="0.5"') + [60, 200, 800, 940].map((x) => R(x - 30, 120, 60, 520, '#3a3024') + E(x, 140, 150, 60, '#2a4a2a') + S(`M${x - 80} 160 L${x - 70} 330 M${x + 60} 170 L${x + 70} 300`, '#8aa87a', 12)).join('') + R(0, 600, 1000, 60, '#3a6a6a') + g.svg
      + R(80, 760, 840, 330, '#7a5a3a') + [0, 1, 2, 3, 4, 5, 6].map((i) => R(80 + i * 120, 760, 6, 330, '#5a4028')).join('') + E(500, 920, 360, 140, '#8a6a46', 'opacity="0.5"')
      + [[40, 1150], [960, 1140], [30, 720]].map(([x, y]) => E(x, y, 60, 18, '#5a9a4a')).join('') + [[120, 700], [880, 700]].map(([x, y]) => R(x - 6, y - 120, 12, 120, '#3a3024') + C(x, y - 130, 22, '#ffcc5a')).join(''); },
  ash: () => { const s = sky('#5a1a1a', '#ff8a3a'), g = ground(620, '#4a3a34', '#2a1e1a');
    return s.def + g.def + '|' + s.svg + P('M560 620 L700 300 L760 300 L900 620 Z', '#3a2a28') + P('M700 300 Q730 200 680 100 Q760 180 760 300 Z', '#ff6a1a', 'opacity="0.9"') + C(730, 120, 60, '#5a4a48', 'opacity="0.8"') + range(640, 5, '#4a2a24', 4)
      + [[140, 600], [380, 610]].map(([x, y]) => R(x - 8, y - 140, 16, 140, '#1e1410') + E(x, y - 150, 110, 30, '#1e1410')).join('') + g.svg + arena('#5a4a40', '#2a1e1a')
      + S('M60 820 L180 860 L260 840 M760 1100 L860 1040 L960 1060 M120 1120 L220 1080', '#ff7a2a', 10) + [[300, 400], [480, 320], [620, 450], [880, 360]].map(([x, y]) => C(x, y, 6, '#ffb040')).join(''); },
  tundra: () => { const s = sky('#1e3a6a', '#bfe8ff'), g = ground(620, '#eaf6ff', '#b8d8ee');
    return s.def + g.def + '|' + s.svg + S('M60 160 Q300 60 520 180 Q740 280 960 120', '#6affc0', 40, 'opacity="0.5"') + S('M80 240 Q320 150 560 250 Q780 330 980 200', '#b07aff', 26, 'opacity="0.4"') + range(620, 5, '#9ab8d8', 6) + range(650, 7, '#d8ecff', 8)
      + [70, 170, 860, 950].map((x, i) => pine(x, 640 + (i % 2) * 20, 1, '#2a5a4a', '#fff')).join('') + g.svg + arena('#d0ecff', '#9ac8e8')
      + [[100, 1050], [900, 1000], [60, 800]].map(([x, y]) => P(`M${x} ${y} L${x + 20} ${y - 90} L${x + 40} ${y} Z M${x + 30} ${y} L${x + 50} ${y - 60} L${x + 70} ${y} Z`, '#9feaff')).join(''); },
  storm: () => { const s = sky('#1a1638', '#5a5a8a'), g = ground(640, '#6a6a7a', '#3a3a4a');
    return s.def + g.def + '|' + s.svg + cloud(60, 140, 2, '#3a3660') + cloud(520, 100, 1.8, '#3a3660') + S('M640 120 L590 260 L640 260 L580 420', '#ffe95a', 12) + [[90, 650, 1.4], [230, 660, 1], [790, 650, 1.2], [930, 660, 1.5]].map(([x, y, k]) => P(`M${x - 70 * k} ${y} L${x - 20 * k} ${y - 360 * k} L${x + 10 * k} ${y - 380 * k} L${x + 70 * k} ${y} Z`, '#4a4658')).join('')
      + S('M240 470 Q500 560 760 470', '#8a6a4a', 8) + g.svg + arena('#7a7a8a', '#4a4a5a') + [0, 1, 2].map((i) => S(`M${100 + i * 60} ${760 + i * 120} Q500 ${720 + i * 120} ${900 - i * 40} ${770 + i * 120}`, '#e8f0ff', 6, 'opacity="0.35"')).join(''); },
  temple: () => { const s = sky('#ff9a4a', '#ffe0a0'), g = ground(620, '#e8c47a', '#c49a50');
    return s.def + g.def + '|' + s.svg + C(500, 330, 110, '#fff3c0', 'opacity="0.9"') + hills(620, 120, '#d8a860', 12)
      + R(300, 300, 400, 320, '#a8743a') + P('M280 300 L500 200 L720 300 Z', '#8a5a2a') + [0, 1, 2, 3, 4].map((i) => R(320 + i * 85, 330, 40, 290, '#c8904a')).join('') + R(450, 470, 100, 150, '#3a2410')
      + [[110, 620], [890, 620]].map(([x, y]) => R(x - 50, y - 330, 100, 330, '#b07a3a') + C(x, y - 360, 50, '#b07a3a') + R(x - 70, y - 40, 140, 40, '#8a5a2a')).join('') + g.svg + arena('#d8b06a', '#a87a3a')
      + [0, 1, 2, 3].map((i) => R(260 + i * 130, 860, 110, 6, '#a87a3a', 'opacity="0.5"')).join(''); },
  abyss: () => { const s = sky('#04122a', '#0a4a7a'), g = ground(640, '#1a4a6a', '#0a2238');
    return s.def + g.def + '|' + s.svg + [[200, 0], [420, 0], [700, 0], [880, 0]].map(([x]) => P(`M${x - 40} 0 L${x} ${160 + (x % 7) * 20} L${x + 40} 0 Z`, '#0a1a2a')).join('') + P('M340 0 L460 0 L620 700 L240 700 Z', '#6ad8ff', 'opacity="0.15"')
      + P('M560 640 L640 470 L860 430 L900 640 Z', '#3a2a24') + R(700, 330, 12, 160, '#3a2a24') + range(660, 6, '#0a2a44', 14) + g.svg + arena('#2a6a8a', '#14445a')
      + [[90, 760], [930, 800], [60, 1040], [950, 1080]].map(([x, y]) => S(`M${x} ${y} Q${x - 30} ${y - 80} ${x} ${y - 160}`, '#ff6a9a', 14) + S(`M${x + 20} ${y} Q${x + 50} ${y - 70} ${x + 30} ${y - 130}`, '#ff6a9a', 10)).join('')
      + [[250, 260], [760, 200], [500, 360]].map(([x, y]) => E(x, y, 40, 30, '#c08aff', 'opacity="0.8"') + S(`M${x - 20} ${y + 20} l0 60 M${x} ${y + 25} l0 70 M${x + 20} ${y + 20} l0 60`, '#c08aff', 4, 'opacity="0.6"')).join('') + [[200, 900], [800, 950], [480, 700]].map(([x, y]) => C(x, y, 12, '#9affff', 'opacity="0.8"')).join(''); },
  tower: () => { const s = sky('#3a6adf', '#e0eaff'), g = ground(700, '#8a8aa0', '#5a5a70');
    return s.def + g.def + '|' + s.svg + cloud(40, 520, 2.2, '#fff', 0.9) + cloud(560, 560, 2, '#fff', 0.9) + cloud(300, 620, 1.6, '#f0f4ff') + cloud(120, 160, 0.8) + cloud(700, 120, 0.7)
      + [[180, 300], [820, 260], [520, 200]].map(([x, y]) => P(blobPath(x, y, 50), '#7a7a8a')).join('') + g.svg + E(500, 700, 520, 60, '#6a6a80') + arena('#9a9ab4', '#6a6a88')
      + E(500, 920, 330, 130, 'none', 'stroke="#6ad8ff" stroke-width="8" opacity="0.8"') + [[80, 760], [920, 760], [60, 1080], [940, 1080]].map(([x, y]) => R(x - 30, y - 220, 60, 220, '#b0b0c4') + R(x - 40, y - 230, 80, 20, '#9a9ab0')).join(''); },
  dungeon: () => { const s = sky('#0e0a1a', '#2a2040'), g = ground(640, '#3a3448', '#1a1626');
    return s.def + g.def + '|' + s.svg + P('M0 0 L1000 0 L1000 300 Q500 520 0 300 Z', '#1a1426') + [[150, 0], [380, 0], [640, 0], [860, 0]].map(([x]) => P(`M${x - 30} 0 L${x} ${200 + (x % 5) * 30} L${x + 30} 0 Z`, '#2a2238')).join('')
      + R(380, 330, 240, 310, '#0a0610') + P('M380 330 Q500 240 620 330 Z', '#0a0610') + g.svg + arena('#4a4458', '#2a2438')
      + [[90, 720], [140, 760], [880, 700], [930, 760], [60, 1100], [950, 1060]].map(([x, y], i) => P(`M${x} ${y} L${x + 20} ${y - 110} L${x + 40} ${y} Z`, i % 2 ? '#7a5aff' : '#4ac8ff')).join('')
      + E(170, 1040, 90, 40, '#ffc94a') + E(830, 1050, 100, 44, '#ffc94a') + [[300, 560], [700, 560]].map(([x, y]) => R(x - 6, y - 60, 12, 60, '#5a4030') + C(x, y - 70, 18, '#ff9a3a')).join(''); },
  arena: () => { const s = sky('#4a9aff', '#d8ecff'), g = ground(640, '#e0c48a', '#b8945a');
    return s.def + g.def + '|' + s.svg + cloud(100, 120, 1) + cloud(640, 90, 1.1) + P('M0 640 L0 330 Q500 250 1000 330 L1000 640 Z', '#c8a878') + [0, 1, 2, 3, 4, 5, 6, 7].map((i) => R(40 + i * 125, 380 - Math.abs(3.5 - i) * 12, 60, 110, '#6a4a30')).join('')
      + R(0, 520, 1000, 120, '#a8865a') + [[120, 330], [380, 280], [620, 280], [880, 330]].map(([x, y]) => R(x - 3, y - 120, 6, 120, '#5a4030') + P(`M${x + 3} ${y - 120} l90 25 l-90 25 Z`, '#d0304a')).join('') + g.svg + arena('#e8d098', '#b89058')
      + E(500, 920, 70, 30, '#c09a60'); },
  lair: () => { const s = sky('#1a0608', '#5a1410'), g = ground(640, '#3a1e1a', '#1e0e0c');
    return s.def + g.def + '|' + s.svg + R(330, 220, 340, 420, '#2a1210') + P('M330 220 Q500 100 670 220 Z', '#2a1210') + [0, 1, 2, 3].map((i) => R(360 + i * 80, 260, 22, 380, '#4a2a24')).join('')
      + S('M330 300 Q160 360 40 300 M670 300 Q840 360 960 300', '#6a5a58', 16) + [[100, 640], [900, 640]].map(([x, y]) => R(x - 40, y - 380, 80, 380, '#3a1e1a')).join('') + g.svg + arena('#4a2a24', '#ff5a1a')
      + S('M0 760 Q200 800 300 1200 M1000 760 Q800 800 700 1200', '#ff6a1a', 22, 'opacity="0.8"') + [[200, 680], [800, 680]].map(([x, y]) => R(x - 24, y - 70, 48, 70, '#4a3a38') + C(x, y - 90, 34, '#ff7a2a')).join(''); },
};
function blobPath(x, y, r) { return `M${x - r} ${y} Q${x - r} ${y - r} ${x} ${y - r} Q${x + r} ${y - r} ${x + r} ${y} Q${x + r * 0.6} ${y + r * 1.4} ${x} ${y + r * 1.6} Q${x - r * 0.6} ${y + r * 1.4} ${x - r} ${y} Z`; }

const SHEETS = { 1: ['meadow', 'bramble', 'bayou'], 2: ['ash', 'tundra', 'storm'], 3: ['temple', 'abyss', 'tower'], 4: ['dungeon', 'arena', 'lair'] };
let defs = '', body = '';
SHEETS[which].forEach((k, i) => {
  const [d, s] = T[k]().split('|');
  defs += d;
  body += `<svg x="${i * PW + G}" y="0" width="${PW - 2 * G}" height="${PH}" viewBox="0 0 1000 1200" preserveAspectRatio="none">${s}</svg>`;
});
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><defs>${defs}</defs><rect width="${W}" height="${H}" fill="#000"/>${body}</svg>`;
(async () => {
  const tmp = path.join(require('os').tmpdir(), `terrains-${which}.html`);
  fs.writeFileSync(tmp, `<html><body style="margin:0;background:#000">${svg}</body></html>`);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: W, height: H } });
  await p.goto('file://' + tmp); await p.waitForTimeout(500); await p.screenshot({ path: out }); await b.close();
  console.log(out, SHEETS[which].join(' | '));
})();
