// Planches de l'interface à faire redessiner par Hailuo : pictos, objets de l'accueil, boutons et cadres.
// 16 éléments par planche (6 × 3, les 2 dernières cases vides pour la signature), 4K 3840 × 2160, fond blanc, sans texte.
// Croquis = les pictos actuels du jeu (src/game/ui/kit.tsx) + des croquis simples pour ce qui n'en a pas encore.
//   node ui-ia.cjs 1..6 sortie.png
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const [, , which, out] = process.argv;
const W = 3840, H = 2160, CW = W / 6, CH = H / 3;

// ---- les pictos du jeu, lus dans kit.tsx (JSX → SVG), dans un repère 24 × 24
const kit = fs.readFileSync(path.join(__dirname, '..', 'src', 'game', 'ui', 'kit.tsx'), 'utf8');
const ICONS = {};
for (const m of kit.slice(kit.indexOf('const ICONS'), kit.indexOf('export function Icon')).matchAll(/^ {2}(\w+): <>(.*)<\/>,$/gm)) ICONS[m[1]] = m[2];
const ink = '#4a4a6a';
const icon = (name, color = ink) => `<g transform="scale(${100 / 24})">${ICONS[name].replace(/currentColor/g, color)}</g>`;

// ---- croquis simples, repère 100 × 100
const P = (d, fill, stroke = '#3a3a52', w = 3) => `<path d="${d}" fill="${fill}" stroke="${stroke}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"/>`;
const C = (x, y, r, fill, stroke = '#3a3a52', w = 3) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${w}"/>`;
const R = (x, y, w, h, rx, fill, stroke = '#3a3a52', sw = 3) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
const star = (cx, cy, r0, r1, fill, stroke) => { let d = ''; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, r = i % 2 ? r1 : r0; d += (i ? 'L' : 'M') + (cx + Math.cos(a) * r).toFixed(1) + ' ' + (cy + Math.sin(a) * r).toFixed(1); } return P(d + 'Z', fill, stroke); };
const chest = (open) => open
  ? P('M14 50 L86 50 L82 88 L18 88 Z', '#b07a3a') + P('M14 50 L86 50 L82 60 L18 60 Z', '#e0b040') + C(30, 44, 9, '#ffd84a', '#b8860b') + C(48, 40, 10, '#ffd84a', '#b8860b') + C(66, 44, 9, '#ffd84a', '#b8860b') + C(56, 32, 6, '#ff5fa2', '#b0246a') + P('M16 50 L22 18 L78 18 L84 50', '#9a6430') + R(44, 64, 12, 12, 2, '#ffd84a', '#b8860b')
  : P('M14 44 Q50 18 86 44 L86 88 L14 88 Z', '#b07a3a') + P('M14 50 L86 50 L86 58 L14 58 Z', '#e0b040') + P('M30 30 L30 88 M70 30 L70 88', 'none', '#7a4a1a', 4) + R(42, 50, 16, 16, 3, '#ffd84a', '#b8860b');
const S = {
  star: star(50, 52, 40, 17, '#ffd84a', '#c08a10'),
  starEmpty: star(50, 52, 40, 17, '#c8ccd8', '#8a8fa3'),
  fusion: C(36, 50, 22, '#a35cff') + C(64, 50, 22, '#ffc94a') + P('M50 30 L56 50 L50 70 L44 50 Z', '#fff'),
  rebirth: P('M50 18 A32 32 0 1 1 20 40', 'none', '#2a9d8f', 9) + P('M10 28 L22 44 L34 28 Z', '#2a9d8f') + C(50, 50, 10, '#7cf7c1', '#2a9d8f'),
  goldMine: P('M10 86 L30 40 L50 30 L70 40 L90 86 Z', '#7a6a5a') + P('M36 86 L36 62 Q50 50 64 62 L64 86 Z', '#2a2230') + C(30, 82, 9, '#ffd84a', '#b8860b') + C(70, 82, 9, '#ffd84a', '#b8860b'),
  essenceSpring: P('M20 80 Q50 92 80 80 L80 86 Q50 98 20 86 Z', '#2a9d8f') + P('M50 20 C62 38 68 48 68 58 A18 18 0 0 1 32 58 C32 48 38 38 50 20 Z', '#7cf7c1', '#2a9d8f'),
  armory: P('M18 70 L82 70 L74 86 L26 86 Z', '#5a5a6a') + P('M30 54 L70 54 L82 70 L18 70 Z', '#7a7a8a') + P('M58 14 L64 18 L42 54 L36 50 Z', '#d7dce6') + P('M34 46 L44 54', 'none', '#c98a3a', 6),
  bag: P('M24 36 Q24 86 50 86 Q76 86 76 36 Z', '#c98a3a') + P('M34 36 Q34 18 50 18 Q66 18 66 36', 'none', '#8a5a20', 6) + R(42, 46, 16, 12, 3, '#ffd84a', '#b8860b'),
  forge: P('M16 70 L84 70 L76 84 L24 84 Z', '#5a5a6a') + P('M22 56 L78 56 L84 70 L16 70 Z', '#7a7a8a') + P('M40 18 L72 18 L72 34 L40 34 Z', '#9aa3b5') + P('M54 34 L54 54', 'none', '#a0703a', 7),
  recycle: P('M50 16 L66 40 L56 40 L56 56 L44 56 L44 40 L34 40 Z', '#4fd1c5') + P('M22 62 L50 84 L78 62', 'none', '#4fd1c5', 9) + C(50, 70, 6, '#b388ff'),
  fire: P('M50 10 C70 34 82 46 74 70 A26 26 0 0 1 26 70 C20 52 34 42 38 28 C44 40 48 44 50 10 Z', '#ff6a1a', '#b03a10') + P('M50 50 C60 60 62 68 56 78 A10 10 0 0 1 42 74 C40 66 46 60 50 50 Z', '#ffd040', '#e08a10', 2),
  wind: P('M12 36 L66 36 A12 12 0 1 0 54 24', 'none', '#2a9a8e', 9) + P('M12 54 L80 54 A12 12 0 1 1 68 66', 'none', '#2a9a8e', 9) + P('M20 72 L48 72', 'none', '#7ce0c8', 7),
  water: P('M50 10 C68 36 78 50 78 64 A28 28 0 0 1 22 64 C22 50 32 36 50 10 Z', '#3a8cff', '#1a4aa8') + P('M36 62 A14 14 0 0 0 48 76', 'none', '#cfe8ff', 6),
  earth: P('M14 80 L34 30 L50 50 L62 22 L88 80 Z', '#8a6a3a', '#4a3418') + P('M34 30 L42 48 L50 50 M62 22 L68 46', 'none', '#c8a46a', 4) + P('M10 80 L90 80', 'none', '#5a8a2a', 8),
  protector: P('M50 10 L84 22 L84 48 Q84 76 50 90 Q16 76 16 48 L16 22 Z', '#4c8dff', '#1d4fa8') + P('M50 24 L50 78 M30 44 L70 44', 'none', '#dce8ff', 6),
  warrior: P('M22 84 L74 20 L82 26 L30 90 Z', '#d7dce6', '#5c606d') + P('M78 84 L26 20 L18 26 L70 90 Z', '#d7dce6', '#5c606d') + R(40, 50, 20, 8, 2, '#c98a3a'),
  marksman: P('M24 14 Q74 50 24 86', 'none', '#a0703a', 7) + P('M24 14 L24 86', 'none', '#e8e0d0', 2) + P('M18 50 L86 50', 'none', '#5c606d', 4) + P('M86 50 L74 42 L74 58 Z', '#9aa3b5'),
  assassin: P('M24 82 L64 26 L76 18 L72 32 L32 88 Z', '#c8ccd8', '#4a4e5c') + P('M76 82 L36 26 L24 18 L28 32 L68 88 Z', '#8a90a8', '#4a4e5c') + C(50, 54, 6, '#e5484d'),
  healer: R(38, 14, 24, 72, 6, '#4adf7a', '#1a8a40') + R(14, 38, 72, 24, 6, '#4adf7a', '#1a8a40') + R(42, 42, 16, 16, 3, '#c8ffd4', '#1a8a40', 0),
  support: C(50, 34, 18, '#ffd84a', '#c08a10') + P('M20 84 Q20 58 50 58 Q80 58 80 84 Z', '#ffc94a', '#c08a10') + P('M50 6 L50 14 M28 12 L33 19 M72 12 L67 19', 'none', '#ffd84a', 5),
  hp: P('M50 86 L16 50 A18 18 0 0 1 50 26 A18 18 0 0 1 84 50 Z', '#e5484d', '#8a1c20'),
  atk: P('M50 8 L58 20 L58 64 L42 64 L42 20 Z', '#d7dce6', '#5c606d') + R(30, 62, 40, 8, 3, '#c98a3a') + R(45, 70, 10, 18, 3, '#7a4a1a'),
  def: P('M50 12 L82 22 L82 46 Q82 74 50 88 Q18 74 18 46 L18 22 Z', '#9aa3b5', '#5c606d'),
  speed: P('M20 80 L44 80 L44 30 L60 30 L60 70 L80 70 L80 84 L20 84 Z', '#a0703a', '#5a3a10') + P('M62 34 Q82 22 90 30 M62 44 Q84 36 90 44', 'none', '#e8f4ff', 5),
  crit: C(50, 50, 34, 'none', '#e5484d', 6) + C(50, 50, 18, 'none', '#e5484d', 6) + C(50, 50, 5, '#e5484d') + P('M50 8 L50 26 M50 74 L50 92 M8 50 L26 50 M74 50 L92 50', 'none', '#e5484d', 5),
  dodge: P('M20 70 Q46 70 52 46 Q58 24 84 24', 'none', '#7fc8ff', 7) + P('M16 50 Q36 50 42 32', 'none', '#cfe8ff', 5) + P('M28 86 Q52 86 60 64', 'none', '#cfe8ff', 5),
  critDmg: star(50, 50, 40, 16, '#ffb040', '#c04a10') + P('M50 30 L56 46 L50 70 L44 46 Z', '#fff', '#c04a10', 2),
  tenacity: P('M30 86 L30 46 Q30 30 44 30 L70 30 Q80 30 80 42 L80 86 Z', '#e0ac7e', '#8a5a3a') + P('M44 30 L44 54 M56 30 L56 54 M68 30 L68 54', 'none', '#8a5a3a', 3),
  chestClosed: chest(false),
  chestOpen: chest(true),
  hourglass: R(22, 10, 56, 10, 3, '#a0703a') + R(22, 80, 56, 10, 3, '#a0703a') + P('M28 20 L72 20 L54 50 L72 80 L28 80 L46 50 Z', '#e8f4ff', '#5a4a3a') + P('M36 28 L64 28 L52 46 L48 46 Z', '#ffd84a', 'none') + P('M34 78 L66 78 L50 62 Z', '#ffd84a', 'none'),
  questChest: chest(false).replace(/#b07a3a/g, '#9aa3b5'),
  summonPortal: C(50, 50, 40, '#a35cff', '#5b2a9f') + C(50, 50, 28, '#5b2a9f', '#c8a0ff') + star(50, 50, 16, 7, '#fff', '#c8a0ff'),
  crown: P('M14 74 L20 28 L36 50 L50 18 L64 50 L80 28 L86 74 Z', '#ffd84a', '#c08a10') + R(14, 74, 72, 12, 3, '#e0b040', '#c08a10') + C(50, 64, 6, '#e5484d'),
  trophy: P('M30 14 L70 14 L70 40 A20 20 0 0 1 30 40 Z', '#ffd84a', '#c08a10') + P('M30 22 L16 22 A14 14 0 0 0 30 46 M70 22 L84 22 A14 14 0 0 1 70 46', 'none', '#c08a10', 5) + R(44, 58, 12, 16, 2, '#e0b040', '#c08a10') + R(30, 74, 40, 12, 3, '#a0703a'),
  defeat: P('M26 84 L52 40 L60 44 L34 88 Z', '#9aa3b5', '#5c606d') + P('M60 36 L74 12 L82 16 L68 40 Z', '#9aa3b5', '#5c606d') + R(20, 76, 22, 8, 3, '#7a4a1a'),
  goldPile: C(30, 70, 14, '#ffd84a', '#b8860b') + C(56, 72, 14, '#ffd84a', '#b8860b') + C(44, 54, 14, '#ffd84a', '#b8860b') + C(70, 56, 12, '#ffd84a', '#b8860b') + C(56, 38, 12, '#ffd84a', '#b8860b'),
  gemPile: P('M20 60 L32 46 L44 60 L32 80 Z', '#ff5fa2', '#b0246a') + P('M44 56 L58 38 L72 56 L58 82 Z', '#ff5fa2', '#b0246a') + P('M62 66 L72 54 L84 66 L72 84 Z', '#ff5fa2', '#b0246a'),
  badge: C(50, 50, 30, '#e5484d', '#8a1c20') + P('M50 32 L50 56 M50 66 L50 68', 'none', '#fff', 8),
  levelUp: P('M50 12 L82 48 L62 48 L62 86 L38 86 L38 48 L18 48 Z', '#3ccf7a', '#1a8a40'),
  // ---- boutons et cadres (vides, sans texte)
  btnGreen: R(6, 30, 88, 40, 20, '#3ccf7a', '#1a8a40', 4) + R(12, 34, 76, 12, 6, '#8af0b0', 'none', 0),
  btnRed: R(6, 30, 88, 40, 20, '#e5484d', '#8a1c20', 4) + R(12, 34, 76, 12, 6, '#ff9a9a', 'none', 0),
  btnBlue: R(6, 30, 88, 40, 20, '#4c8dff', '#1d4fa8', 4) + R(12, 34, 76, 12, 6, '#9ac0ff', 'none', 0),
  btnPurple: R(6, 30, 88, 40, 20, '#8f4cf0', '#4a1a8a', 4) + R(12, 34, 76, 12, 6, '#c8a0ff', 'none', 0),
  btnGold: R(6, 30, 88, 40, 20, '#ffc94a', '#b8860b', 4) + R(12, 34, 76, 12, 6, '#fff0a8', 'none', 0),
  btnGrey: R(6, 30, 88, 40, 20, '#4a4f6e', '#2a2d44', 4) + R(12, 34, 76, 12, 6, '#7a80a0', 'none', 0),
  roundBtn: C(50, 50, 38, '#2c3260', '#ffc94a', 6) + C(50, 50, 30, 'none', '#4a5290', 3),
  closeBtn: C(50, 50, 30, '#2c3260', '#c7cbe0', 4) + P('M38 38 L62 62 M62 38 L38 62', 'none', '#fff', 7),
  frameCommon: R(16, 8, 68, 84, 10, '#2c3260', '#9aa0b5', 7),
  frameRare: R(16, 8, 68, 84, 10, '#2c3260', '#3d8bff', 7),
  frameEpic: R(16, 8, 68, 84, 10, '#2c3260', '#a35cff', 7),
  frameLegend: R(16, 8, 68, 84, 10, '#2c3260', '#ffc94a', 7) + star(50, 8, 8, 3.5, '#ffd84a', '#c08a10'),
  panel: R(6, 14, 88, 72, 8, '#232850', '#ffc94a', 3) + R(10, 18, 80, 10, 4, '#2c3260', 'none', 0),
  ribbon: P('M4 40 L16 40 L12 50 L16 60 L4 60 Z', '#a8343a') + P('M96 40 L84 40 L88 50 L84 60 L96 60 Z', '#a8343a') + R(14, 34, 72, 28, 4, '#e5484d', '#8a1c20'),
  resPill: R(8, 36, 84, 28, 14, '#14162b', '#3a4180', 3) + C(22, 50, 10, '#ffd84a', '#b8860b') + C(80, 50, 9, '#3ccf7a', '#1a8a40') + P('M80 44 L80 56 M74 50 L86 50', 'none', '#fff', 3),
  tabBar: R(4, 34, 92, 32, 10, '#1b1e3a', '#3a4180', 3) + R(36, 30, 28, 40, 10, '#2c3260', '#ffc94a', 3) + C(50, 50, 7, '#ffc94a', 'none', 0),
  avatarFrame: C(50, 50, 38, 'none', '#ffc94a', 8) + C(50, 50, 30, '#2c3260', 'none', 0) + C(74, 76, 11, '#14162b', '#ffc94a', 3),
};
const it = (name) => (S[name] ? `<svg viewBox="0 0 100 100" width="100" height="100">${S[name]}</svg>` : `<svg viewBox="0 0 100 100" width="100" height="100">${icon(name)}</svg>`);

const SHEETS = {
  1: ['gold', 'essence', 'gems', 'scrolls', 'basicScrolls', 'crystals', 'fragments', 'dust', 'arenaTokens', 'guildCoins', 'power', 'gift', 'ad', 'clock', 'lock', 'star'],
  2: ['campaign', 'heroes', 'summon', 'adventure', 'guild', 'calendar', 'mail', 'quests', 'shop', 'pass', 'ranking', 'friends', 'chat', 'settings', 'fusion', 'rebirth'],
  3: ['tower', 'missions', 'dungeons', 'dailyBoss', 'arena', 'defense', 'goldMine', 'essenceSpring', 'armory', 'weapon', 'armor', 'helmet', 'boots', 'bag', 'forge', 'recycle'],
  4: ['fire', 'wind', 'water', 'earth', 'protector', 'warrior', 'marksman', 'assassin', 'healer', 'support', 'hp', 'atk', 'def', 'speed', 'crit', 'dodge'],
  5: ['chestClosed', 'chestOpen', 'hourglass', 'questChest', 'summonPortal', 'crown', 'trophy', 'defeat', 'starEmpty', 'goldPile', 'gemPile', 'critDmg', 'tenacity', 'badge', 'levelUp', 'avatarFrame'],
  6: ['btnGreen', 'btnRed', 'btnBlue', 'btnPurple', 'btnGold', 'btnGrey', 'roundBtn', 'closeBtn', 'frameCommon', 'frameRare', 'frameEpic', 'frameLegend', 'panel', 'ribbon', 'resPill', 'chestClosed'],
};
SHEETS[6][15] = 'tabBar';
const list = SHEETS[which];
for (const n of list) if (!S[n] && !ICONS[n]) throw new Error('inconnu : ' + n);
let body = '';
list.forEach((n, i) => {
  const col = i % 6, row = Math.floor(i / 6), k = 4.6;
  body += `<g transform="translate(${col * CW + CW / 2 - 50 * k} ${row * CH + CH / 2 - 50 * k}) scale(${k})">${it(n).replace(/^<svg[^>]*>|<\/svg>$/g, '')}</g>`;
});
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="#fff"/>${body}</svg>`;
(async () => {
  const tmp = path.join(require('os').tmpdir(), `ui-${which}.html`);
  fs.writeFileSync(tmp, `<html><body style="margin:0">${svg}</body></html>`);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: W, height: H } });
  await p.goto('file://' + tmp); await p.waitForTimeout(400); await p.screenshot({ path: out }); await b.close();
  console.log(out, list.join(' | '));
})();
module.exports = { SHEETS };
