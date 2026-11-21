// Dernières planches pour Hailuo (21/11/2026) : tout ce qui manquait encore au jeu.
//   node planches-fin.cjs <nom> sortie.png      noms : equipements, effets, boutique, defense, logo, guilde, monde
// Croquis simples (Hailuo fait le rendu) : formes et couleurs pour les objets, émojis pour donner l'idée des pictos.
// Format 4K 16:9 (3840 × 2160) ; la case en bas à droite reste vide (signature de Hailuo).
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const [, , which, out] = process.argv;
const W = 3840, H = 2160;

// ---------- petits dessins (repère 100 × 100) ----------
const INK = '#2a2238';
const p = (d, fill, w = 3) => `<path d="${d}" fill="${fill}" stroke="${INK}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"/>`;
const c = (x, y, r, fill, w = 3) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="${INK}" stroke-width="${w}"/>`;
const svg = (inner, glow) => `<svg viewBox="0 0 100 100" width="100%" height="100%">${glow ? `<defs><filter id="gl"><feGaussianBlur stdDeviation="4"/></filter></defs><g filter="url(#gl)" opacity=".75">${inner.replace(/stroke="[^"]*"/g, `stroke="${glow}"`).replace(/fill="(?!none)[^"]*"/g, `fill="${glow}"`)}</g>` : ''}${inner}</svg>`;

// raretés : gris, vert, bleu, violet, or, rouge
const RAR = ['#8d939c', '#5aa84a', '#3b7dd8', '#9a55d6', '#f0bf2e', '#d83a3e'];
const LIGHT = ['#c9ced6', '#a6e08f', '#9cc8ff', '#d3a8ff', '#ffe58a', '#ff9a8a'];
const gem = (x, y, r, col) => p(`M${x} ${y - r} L${x + r} ${y} L${x} ${y + r} L${x - r} ${y} Z`, col, 2);
function sword(r) {
  const col = RAR[r], blade = r >= 4 ? LIGHT[r] : '#e8eef5';
  let s = p('M50 6 L59 20 L59 62 L41 62 L41 20 Z', blade);
  if (r >= 3) s += `<path d="M50 22 L50 56" stroke="${RAR[r]}" stroke-width="3"/>`;
  s += p(r >= 4 ? 'M22 58 Q30 66 40 62 L60 62 Q70 66 78 58 L74 70 L26 70 Z' : 'M30 60 L70 60 L70 69 L30 69 Z', col);
  s += p('M45 69 L55 69 L55 86 L45 86 Z', '#6b4a2a') + c(50, 91, 6, col);
  if (r >= 2) s += gem(50, 64, 4, r >= 5 ? '#ffd23a' : LIGHT[r]);
  return svg(s, r >= 4 ? LIGHT[r] : null);
}
function armor(r) {
  const col = RAR[r];
  let s = p('M27 22 L42 15 Q50 22 58 15 L73 22 L82 42 L70 46 L68 86 L32 86 L30 46 L18 42 Z', col);
  s += p('M42 15 Q50 22 58 15 L58 30 Q50 36 42 30 Z', r >= 4 ? '#ffe58a' : '#d9d2c3', 2);
  if (r >= 1) s += `<path d="M32 66 L68 66" stroke="${INK}" stroke-width="3"/>`;
  if (r >= 2) s += gem(50, 48, 7, LIGHT[r]);
  if (r >= 3) s += p('M18 42 L10 30 L27 22 Z', LIGHT[r], 2) + p('M82 42 L90 30 L73 22 Z', LIGHT[r], 2);
  return svg(s, r >= 4 ? LIGHT[r] : null);
}
function helmet(r) {
  const col = RAR[r];
  let s = '';
  if (r >= 3) s += p('M50 20 Q66 0 82 12 Q70 14 56 26 Z', r >= 5 ? '#ff6a3a' : LIGHT[r]);
  if (r >= 4) s += p('M24 40 Q8 26 12 10 Q22 26 32 32 Z', '#f4ecd8') + p('M76 40 Q92 26 88 10 Q78 26 68 32 Z', '#f4ecd8');
  s += p('M24 66 Q24 18 50 18 Q76 18 76 66 L76 80 L24 80 Z', col);
  s += p('M32 50 L68 50 L68 58 L32 58 Z', '#2a2238', 2) + p('M47 58 L53 58 L53 80 L47 80 Z', LIGHT[r], 2);
  if (r >= 2) s += gem(50, 32, 5, LIGHT[r]);
  if (r >= 5) s += p('M34 22 L38 10 L44 20 L50 6 L56 20 L62 10 L66 22 Z', '#ffd23a', 2);
  return svg(s, r >= 4 ? LIGHT[r] : null);
}
function boots(r) {
  const col = RAR[r];
  let s = '';
  if (r >= 4) s += p('M34 30 Q14 22 8 6 Q24 12 36 22 Z', '#f4ecd8');
  s += p('M36 16 L60 16 L60 62 L82 70 Q88 84 78 88 L30 88 L33 62 Z', r === 0 ? '#8a5a30' : col);
  s += p('M34 16 L62 16 L62 28 L34 28 Z', r === 0 ? '#6b4a2a' : LIGHT[r], 2) + p('M30 80 L82 80 Q86 88 78 88 L30 88 Z', '#4a3020', 2);
  if (r >= 2) s += gem(48, 22, 4, r >= 5 ? '#ffd23a' : '#ffffff');
  return svg(s, r >= 4 ? LIGHT[r] : null);
}
const emo = (e, bg) => `<div class="emo${[...e.replace(/\uFE0F/g, '')].length > 1 ? ' two' : ''}" ${bg ? `style="background:${bg}"` : ''}>${e}</div>`;

// ---------- les planches ----------
const SHEETS = {
  // 4 rangées (arme, armure, casque, bottes) × 6 raretés ; 7e colonne vide
  equipements: { cols: 7, rows: 4, cells: [sword, armor, helmet, boots].flatMap((f) => [0, 1, 2, 3, 4, 5].map((r) => f(r)).concat([null])) },
  effets: {
    cols: 7, rows: 4,
    cells: [
      // 5 panoplies
      emo('🔥⚔️', '#ffd6cc'), emo('🏰', '#e3ddd2'), emo('⚡', '#dbe8ff'), emo('🦇', '#f0d0dc'), emo('🛡️', '#fff0b8'),
      // 14 effets
      emo('🔥'), emo('☠️'), emo('🩸'), emo('🌿➕'), emo('💫'), emo('🤐'), emo('🐌'), emo('😠'),
      emo('⚔️⬆️'), emo('⚔️⬇️'), emo('🛡️⬆️'), emo('🛡️⬇️'), emo('👢⬆️'), emo('🎯⬆️'),
      // 5 ligues
      emo('🥉', '#e8c9a8'), emo('🥈', '#e3e6ea'), emo('🥇', '#fff0b8'), emo('💠', '#d8f4f4'), emo('💎', '#d6e6ff'),
      // dos de carte (portrait)
      `<div class="card">✦</div>`,
      null, null, null,
    ],
  },
  boutique: {
    cols: 6, rows: 3,
    cells: [
      emo('🎁💎'), emo('🌱💎'), emo('💳✨'), emo('🎟️⭐'), emo('📺🚫'), emo('💎'),
      emo('💎💎'), emo('💰💎'), emo('🏔️💎'), emo('🏮👢'), emo('🛒🐴'), emo('🏛️📜'),
      emo('🏹🦌'), emo('🏺✨'), emo('🪜🏰'), emo('⛩️🔮'), null, null,
    ],
  },
  guilde: {
    cols: 6, rows: 3,
    cells: [
      emo('🦁', '#dbe8ff'), emo('🐺', '#e3e6ea'), emo('🐉', '#ffd6cc'), emo('🦅', '#fff0b8'), emo('🔥🐦', '#ffd6cc'), emo('🐙', '#d8f4f4'),
      emo('🌳', '#d9f2cf'), emo('🪓', '#e8d8c8'), emo('👑', '#fff0b8'), emo('🌙', '#e0d6ff'), emo('☀️', '#fff0b8'), emo('⚓', '#dbe8ff'),
      emo('🦉🎓'), emo('🦉😄'), emo('🦉👉'), emo('🦉😮'), null, null,
    ],
  },
};

// carte du mode Défense : 3 versions (prairie, désert, neige), chemin et socles aux places du jeu (src/core/data/defense.ts)
function defenseSheet() {
  const src = fs.readFileSync(path.join(__dirname, '..', 'src', 'core', 'data', 'defense.ts'), 'utf8');
  const arr = (name) => JSON.parse(src.match(new RegExp(`${name}[^=]*=\\s*(\\[[\\s\\S]*?\\]);`))[1].replace(/\s/g, '').replace(/,\]/g, ']'));
  const PATH = arr('DEFENSE_PATH'), PADS = arr('DEFENSE_PADS');
  const MW = 720, MH = 1100, ph = 1880, pw = Math.round(ph * MW / MH), gap = Math.round((W - 3 * pw) / 4);
  const looks = [['#7cc860', '#5aa840', '#d8b878', '#a8804e'], ['#f0d090', '#d8b060', '#c89858', '#8a6236'], ['#eef6ff', '#c8def0', '#a8c8e0', '#6a8aa8']];
  return looks.map(([g1, g2, road, edge], i) => {
    const d = 'M' + PATH.map(([x, y]) => `${x} ${y}`).join(' L');
    const deco = [[40, 40], [690, 60], [40, 760], [690, 540], [60, 1040], [680, 1060], [330, 40]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="34" fill="${g2}" stroke="${INK}" stroke-width="4"/>`).join('');
    const pads = PADS.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="46" fill="#b8b0a0" stroke="${INK}" stroke-width="6"/><circle cx="${x}" cy="${y}" r="30" fill="#d8d0c0"/>`).join('');
    const [ex, ey] = PATH[PATH.length - 1];
    const svgMap = `<svg viewBox="0 0 ${MW} ${MH}" width="${pw}" height="${ph}" preserveAspectRatio="none"><rect width="${MW}" height="${MH}" fill="${g1}"/>${deco}
      <path d="${d}" fill="none" stroke="${edge}" stroke-width="104" stroke-linejoin="round"/><path d="${d}" fill="none" stroke="${road}" stroke-width="84" stroke-linejoin="round"/>
      ${pads}<rect x="${ex - 70}" y="${MH - 100}" width="140" height="90" rx="14" fill="#8a6a4a" stroke="${INK}" stroke-width="6"/><path d="M${ex - 80} ${MH - 96} L${ex} ${MH - 150} L${ex + 80} ${MH - 96} Z" fill="#c84a3a" stroke="${INK}" stroke-width="6"/>
      <rect x="0" y="100" width="40" height="100" fill="#5a4a3a" stroke="${INK}" stroke-width="6"/></svg>`;
    return `<div style="position:absolute;left:${gap + i * (pw + gap)}px;top:30px">${svgMap}</div>`;
  }).join('');
}

// logo, icône de l'application, écran de chargement
function logoSheet() {
  return `<div style="position:absolute;left:120px;top:420px;width:1000px;height:1000px;border-radius:180px;background:linear-gradient(#ffb347,#e8503a);border:12px solid ${INK};display:flex;align-items:center;justify-content:center;overflow:hidden"><img src="file:///home/user/fuze-arena-hero-battle/public/art/c/knights-4.webp" style="width:1500px;margin-top:500px"></div>
  <div style="position:absolute;left:1260px;top:560px;width:1300px;height:700px;display:flex;flex-direction:column;align-items:center;justify-content:center">
    <div style="font:900 230px/1 Impact, sans-serif;color:#ffcf3a;-webkit-text-stroke:14px ${INK}">FUZE ARENA</div>
    <div style="margin-top:30px;padding:16px 60px;background:#d83a3e;border:10px solid ${INK};border-radius:20px;font:900 110px/1 Impact, sans-serif;color:#fff">HERO BATTLE</div>
    <div style="font-size:240px;margin-top:-20px">⚔️</div></div>
  <div style="position:absolute;left:2720px;top:40px;width:1000px;height:1780px;background:linear-gradient(#ff9a4a,#ffe0a0 55%,#6a8a4a 56%,#3a5a2a);border:8px solid ${INK}">
        <div style="position:absolute;left:-20px;right:-20px;top:600px;height:900px"><img src="file:///home/user/fuze-arena-hero-battle/public/art/c/mages-12.webp" style="position:absolute;left:-30px;top:0px;width:560px"><img src="file:///home/user/fuze-arena-hero-battle/public/art/c/angels-9.webp" style="position:absolute;left:480px;top:-40px;width:560px"><img src="file:///home/user/fuze-arena-hero-battle/public/art/c/knights-4.webp" style="position:absolute;left:180px;top:330px;width:640px"><img src="file:///home/user/fuze-arena-hero-battle/public/art/c/assassins-8.webp" style="position:absolute;left:-60px;top:420px;width:480px"><img src="file:///home/user/fuze-arena-hero-battle/public/art/c/mages-6.webp" style="position:absolute;left:600px;top:420px;width:440px"></div>
    <div style="position:absolute;left:120px;right:120px;bottom:120px;height:60px;border-radius:30px;background:#2a2238;border:6px solid #ffcf3a"></div></div>`;
}

// carte du monde : 8 régions de la campagne reliées par un chemin, la Tour au milieu ; coin bas droit = mer
function worldSheet() {
  const R = [[420, 1560, '#8fd06a', '🌾'], [700, 1000, '#3e8a2a', '🌲'], [380, 560, '#4a7a5a', '🐊'], [1180, 380, '#c8603a', '🌋'],
    [1900, 300, '#e8f4ff', '🏔️'], [2600, 420, '#6a6a8a', '⛈️'], [3150, 760, '#f0c070', '🏛️'], [2900, 1300, '#2a6a9a', '🌊']];
  const blobs = R.map(([x, y, col, e]) => `<div style="position:absolute;left:${x - 330}px;top:${y - 260}px;width:660px;height:520px;border-radius:48% 52% 45% 55%;background:${col};border:10px solid ${INK};display:flex;align-items:center;justify-content:center;font-size:230px">${e}</div>`).join('');
  const pts = R.map(([x, y]) => `${x},${y}`).join(' ');
  return `<div style="position:absolute;inset:0;background:#4aa8d8"></div>
    <div style="position:absolute;left:120px;top:80px;width:3300px;height:1800px;border-radius:40% 30% 45% 35%;background:#d8c890;border:14px solid ${INK}"></div>
    ${blobs}<svg style="position:absolute;inset:0" width="${W}" height="${H}"><polyline points="${pts}" fill="none" stroke="#fff6d8" stroke-width="22" stroke-dasharray="40 30"/></svg>
    <svg style="position:absolute;left:1700px;top:640px" width="420" height="640" viewBox="0 0 100 150"><path d="M30 150 L36 40 L64 40 L70 150 Z" fill="#b8b0c8" stroke="#2a2238" stroke-width="4"/><path d="M26 40 L50 6 L74 40 Z" fill="#6a4ad0" stroke="#2a2238" stroke-width="4"/><rect x="44" y="60" width="12" height="18" fill="#2a2238"/><rect x="44" y="100" width="12" height="18" fill="#2a2238"/></svg>`;
}


// carte du monde v2 : 8 plateaux bien séparés (un seul paysage chacun), reliés par des ponts, en zigzag ; la Tour au milieu
function worldSheet2() {
  const R = [[520, 1640, '#8fd06a', '🌾'], [1420, 1700, '#3e8a2a', '🌳'], [2320, 1700, '#4a8a6a', '🐊'], [3220, 1600, '#d88a4a', '🌋'],
    [3220, 620, '#eef6ff', '🏔️'], [2320, 520, '#7a7a9a', '⛈️'], [1420, 520, '#f0c070', '🏛️'], [520, 620, '#2a8aaa', '🌀']];
  const plat = R.map(([x, y, col, e]) => `<div style="position:absolute;left:${x - 360}px;top:${y - 280}px;width:720px;height:560px;border-radius:50%;background:#8a6a4a;border:12px solid ${INK}"></div>
    <div style="position:absolute;left:${x - 360}px;top:${y - 330}px;width:720px;height:520px;border-radius:50%;background:${col};border:12px solid ${INK};display:flex;align-items:center;justify-content:center;font-size:260px">${e}</div>`).join('');
  const bridges = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7]].map(([a, b]) => {
    const [x1, y1] = R[a], [x2, y2] = R[b], mx = (x1 + x2) / 2, my = (y1 + y2) / 2 - 40, len = Math.hypot(x2 - x1, y2 - y1) - 680, ang = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
    return `<div style="position:absolute;left:${mx - len / 2}px;top:${my - 45}px;width:${len}px;height:90px;background:repeating-linear-gradient(90deg,#c89858 0 50px,#8a6236 50px 60px);border:10px solid ${INK};transform:rotate(${ang}deg)"></div>`;
  }).join('');
  return `<div style="position:absolute;inset:0;background:#4aa8d8"></div>${bridges}${plat}
    <svg style="position:absolute;left:1700px;top:700px" width="440" height="720" viewBox="0 0 100 160"><ellipse cx="50" cy="150" rx="48" ry="10" fill="#8a6a4a" stroke="#2a2238" stroke-width="3"/><path d="M30 150 L36 40 L64 40 L70 150 Z" fill="#b8b0c8" stroke="#2a2238" stroke-width="4"/><path d="M26 40 L50 6 L74 40 Z" fill="#6a4ad0" stroke="#2a2238" stroke-width="4"/><rect x="44" y="60" width="12" height="18" fill="#2a2238"/><rect x="44" y="100" width="12" height="18" fill="#2a2238"/></svg>`;
}

let body;
if (SHEETS[which]) {
  const { cols, rows, cells } = SHEETS[which], cw = W / cols, ch = H / rows;
  body = cells.map((x, i) => x ? `<div class="cell" style="--s:${Math.round(Math.min(cw, ch) * 0.78)}px;--f:${Math.round(Math.min(cw, ch) * 0.42)}px;left:${(i % cols) * cw}px;top:${Math.floor(i / cols) * ch}px;width:${cw}px;height:${ch}px">${x.replace('width="100%" height="100%"', `width="${Math.round(Math.min(cw, ch) * 0.8)}" height="${Math.round(Math.min(cw, ch) * 0.8)}"`)}</div>` : '').join('');
} else if (which === 'defense') body = defenseSheet();
else if (which === 'logo') body = logoSheet();
else if (which === 'monde') body = worldSheet();
else if (which === 'monde2') body = worldSheet2();
else throw new Error('planche inconnue : ' + which);
const bg = which === 'defense' ? '#000' : '#fff';
const html = `<html><head><style>body{margin:0;width:${W}px;height:${H}px;position:relative;background:${bg};overflow:hidden;font-family:'Noto Color Emoji',sans-serif}
.cell{position:absolute;display:flex;align-items:center;justify-content:center;box-sizing:border-box}
.cell>*{flex:none}
.cell svg{width:var(--s);height:var(--s)}
.emo{width:var(--s);height:var(--s);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:var(--f);white-space:nowrap;letter-spacing:-.25em}
.emo.two{font-size:calc(var(--f) * .72)}
.card{height:calc(var(--s) * 1.05);aspect-ratio:0.72;border-radius:28px;background:linear-gradient(#3a3a9a,#1e1e5a);border:14px solid #f0bf2e;display:flex;align-items:center;justify-content:center;font-size:200px;color:#f0bf2e}
</style></head><body>${body}</body></html>`;
(async () => {
  const tmp = path.join(require('os').tmpdir(), `planche-${which}.html`);
  fs.writeFileSync(tmp, html);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: W, height: H } });
  await pg.goto('file://' + tmp); await pg.waitForTimeout(600); await pg.screenshot({ path: out }); await b.close();
  console.log(out);
})();
