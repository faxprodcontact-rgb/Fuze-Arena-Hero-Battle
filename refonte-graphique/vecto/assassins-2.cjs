// Kael (assassins-2), héros : redessiné par le code d'après le dessin d'origine, dans le même cadre (761 × 560, mêmes
// proportions, même pose) : un chevalier démon trapu en armure de plaques gris-noir ; une crinière de flammes orange et
// jaunes, une corne noire recourbée à droite, un visage sombre aux yeux qui brûlent, un rictus à dents serrées ; de
// grosses épaulières, des braises de lave entre les plaques ; une cape en lambeaux derrière lui à gauche ; il tient à
// droite une immense épée noire aux tranchants de feu, à garde dorée.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. Le feu éclaire tout en orange.
// Contour décalqué sur l'original (outils/contour.py).
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 761, H = 560, PAD = 50;

// ---------- courbes lisses (reprises du harfang, glaces-4) ----------
/**
 * Chemin lisse passant par des points. `src` = "x,y x,y! …" (ou une liste) : un point suivi de « ! » est un angle vif.
 * Entre deux angles vifs qui se suivent, le bord est bombé vers l'extérieur de `bulge` pixels.
 */
function sm(src, bulge = 0, closed = true) {
  let pts = (Array.isArray(src) ? src.join(' ') : src).trim().split(/\s+/).map((s) => {
    const sharp = s.endsWith('!');
    const [x, y] = s.replace('!', '').split(',').map(Number);
    return { x, y, sharp };
  });
  if (bulge && closed) {
    let area = 0;
    pts.forEach((p, i) => { const q = pts[(i + 1) % pts.length]; area += p.x * q.y - q.x * p.y; });
    const sg = area > 0 ? 1 : -1;
    const out = [];
    pts.forEach((p, i) => {
      out.push(p);
      const q = pts[(i + 1) % pts.length];
      if (p.sharp && q.sharp) {
        const dx = q.x - p.x, dy = q.y - p.y, L = Math.hypot(dx, dy) || 1;
        out.push({ x: (p.x + q.x) / 2 + (sg * dy / L) * bulge, y: (p.y + q.y) / 2 - (sg * dx / L) * bulge, sharp: false });
      }
    });
    pts = out;
  }
  const N = pts.length;
  const at = (i) => (closed ? pts[(i + N) % N] : pts[Math.max(0, Math.min(N - 1, i))]);
  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y) || 1;
  const tan = (i) => {
    const p = at(i);
    if (p.sharp || (!closed && (i === 0 || i === N - 1))) return { x: 0, y: 0 };
    const a = at(i - 1), b = at(i + 1);
    const d = dist(a, p) + dist(p, b);
    return { x: (b.x - a.x) / d, y: (b.y - a.y) / d };
  };
  let d = `M${n(pts[0].x)} ${n(pts[0].y)}`;
  const last = closed ? N : N - 1;
  for (let i = 0; i < last; i++) {
    const p = at(i), q = at(i + 1), L = dist(p, q) / 3;
    const t1 = tan(i), t2 = tan(i + 1);
    d += `C${n(p.x + t1.x * L)} ${n(p.y + t1.y * L)} ${n(q.x - t2.x * L)} ${n(q.y - t2.y * L)} ${n(q.x)} ${n(q.y)}`;
  }
  return d + (closed ? 'Z' : '');
}
const P = (x, y) => `${n(x)},${n(y)}`;
/** Met une liste de points dans le sens des aiguilles d'une montre : les morceaux d'une même silhouette s'additionnent. */
function cw(pts) {
  let area = 0;
  pts.forEach((p, i) => {
    const q = pts[(i + 1) % pts.length];
    const [x1, y1] = p.replace('!', '').split(',').map(Number), [x2, y2] = q.replace('!', '').split(',').map(Number);
    area += x1 * y2 - x2 * y1;
  });
  return area > 0 ? pts : [...pts].reverse();
}
/** Ruban effilé le long d'une ligne : pts = [[x, y, largeur], …] (reflets et ombres en forme de fuseau). */
function rib(pts) {
  const L = [], R = [];
  pts.forEach(([x, y, w], i) => {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1];
    const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
    L.push(P(x - dy * w / 2, y + dx * w / 2)); R.push(P(x + dy * w / 2, y - dx * w / 2));
  });
  return sm([...L, ...R.reverse()].map((p, i, all) => (i === 0 || i === all.length - 1 || i === L.length - 1 || i === L.length ? `${p}!` : p)));
}
const glint = (pts, color, o = 1) => shape(rib(pts), color, o);

// ---------- couleurs ----------
const ARM = { hi: '#a8a4b4', lite: '#6e6a7a', base: '#45414e', mid: '#34303c', shade: '#221f28', deep: '#121016' };
const SKIN = { hi: '#8a8290', lite: '#5e5664', base: '#433c4a', shade: '#2c2632', deep: '#18141c' };
const FIRE = { core: '#fffbe0', hi: '#fff0a0', lite: '#ffd040', base: '#ff9a1a', mid: '#f26a0a', deep: '#b83a08' };
const GOLD = { hi: '#fff4b8', base: '#f2bc44', shade: '#a86a14', deep: '#6a3e08' };
const SH = { armor: '#050407', fire: '#5a1a04' };

// ---------- dégradés ----------
const defs = [
  rad('g-fireR', 310, 160, 190, [[0, FIRE.hi], [0.35, FIRE.lite], [0.65, FIRE.base], [0.85, FIRE.mid], [1, FIRE.deep]]),
  lin('g-fire', 0, 260, 0, 0, [[0, FIRE.deep], [0.3, FIRE.mid], [0.6, FIRE.base], [0.85, FIRE.lite], [1, FIRE.hi]]),
  lin('g-armor', 0, 0, 0, 1, [[0, '#7a7686'], [0.4, ARM.base], [1, ARM.deep]], false),
  lin('g-armorX', 0, 0, 1, 0, [[0, ARM.shade], [0.55, ARM.base], [1, ARM.lite]], false),
  lin('g-skin', 0, 150, 0, 310, [[0, SKIN.lite], [0.5, SKIN.base], [1, SKIN.shade]]),
  lin('g-horn', 0, 0, 1, 0, [[0, '#1a161e'], [0.5, '#3a3440'], [1, '#6a6274']], false),
  lin('g-cape', 0, 270, 0, 500, [[0, '#2c2834'], [0.5, '#1e1a24'], [1, '#100e14']]),
  lin('g-blade', 490, 380, 740, 110, [[0, '#2a2026'], [0.5, '#3a2a2a'], [1, '#4a3430']]),
  lin('g-gold', 0, 0, 0, 1, [[0, GOLD.hi], [0.45, GOLD.base], [1, GOLD.shade]], false),
  rad('g-eye', 0.5, 0.5, 0.6, [[0, '#ffffff'], [0.35, '#fff4a0'], [0.75, '#ffb020'], [1, '#e06010']], false),
  rad('g-glow', 0.5, 0.5, 0.5, [[0, '#fff4c0', 0.85], [0.42, '#ffa030', 0.45], [1, '#ff6a10', 0]], false),
  rad('g-ember', 0.5, 0.5, 0.5, [[0, '#ffffff'], [0.3, '#ffe070'], [0.7, '#ff8a1a'], [1, '#c83a08']], false),
  lin('g-mouth', 0, 0, 0, 1, [[0, '#1a0806'], [1, '#5a1a0a']], false),
].join('');

// ---------- l'épée : un axe, d'où se déduisent la lame, la garde, la poignée ----------
// mesuré sur l'original : tranchant du haut de (478,283) à (636,140), pointe (741,117), tranchant du bas jusqu'à (733,188) puis (535,348)
const SA = [506, 318], SB = [732.3, 113.6]; // la base de la lame (au-dessus de la garde) et la direction de la pointe
const SL = Math.hypot(SB[0] - SA[0], SB[1] - SA[1]), SU = [(SB[0] - SA[0]) / SL, (SB[1] - SA[1]) / SL], SN = [-SU[1], SU[0]];
/** Un point de l'épée : `f` le long de l'axe (0 = base de la lame, 1 = pointe, négatif = vers le pommeau), `s` en travers (pixels). */
const sp = (f, s) => `${n(SA[0] + SU[0] * SL * f + SN[0] * s)},${n(SA[1] + SU[1] * SL * f + SN[1] * s)}`;
const spa = (f, s) => [n(SA[0] + SU[0] * SL * f + SN[0] * s), n(SA[1] + SU[1] * SL * f + SN[1] * s)];

// ---------- silhouettes (le bord extérieur suit le contour mesuré sur l'original) ----------
const S = {
  // la cape en lambeaux, derrière à gauche
  cape: sm('150,270 200,300 230,360 220,440 180,480 130,481! 122,470 101,477! 106,458 111,442 100,440 93,449 79,457 79,464 72,472 69,485 64,493! 59,483 59,475 56,472 58,452 48,449 42,453 33,451 25,458 9,480! '
    + '8,467 11,452 27,420 48,397 111,348 136,320 136,314 133,311 119,308 125,301 125,294 110,273 108,266 130,267 149,263'),
  // la crinière de flammes : derrière la tête, de grandes langues de feu qui montent
  fire: sm('246,21! 239,27 237,40 223,55! 217,55 223,59 223,65 210,76 201,77! 198,72 189,71 183,67 177,70! 188,84 189,99 182,104 171,103 163,91! 169,105 187,119 191,125 191,132 180,140 162,144 155,141 146,130! '
    + '145,139 125,156 123,169 133,177 148,180 156,178 161,173 167,173 187,188 187,195 184,198 168,204! 183,215 183,221 180,224 158,222! 161,253 200,260 260,250 300,200 360,170 420,150 440,120 '
    + '427,72 407,54 404,48 396,45 393,41 387,40 379,31 372,29 369,32 368,43 365,46 359,46 350,40 338,38 328,26 323,25 314,15 314,12 309,8 310,0! 292,0! 294,8 285,13 278,23 265,23 257,20'),
  // la corne noire recourbée, à droite
  horn: sm('436,150 448,128 453,128 459,128 465,117 459,89 459,77 463,65 468,60! 470,74 490,110 493,123 492,138 483,160 469,175 454,184 440,180'),
  // les jambes et les bottes de fer
  legL: sm('130,470 210,470 215,515 215,541 212,546 208,546 200,552 201,559 194,559 191,553 133,551 125,548 113,549 102,546 102,538 113,523 113,516 122,505'),
  legR: sm('370,470 452,470 454,508 473,521 484,524 495,542 519,546! 502,549 499,545 471,548 468,551 453,552 411,548 406,543 370,541 366,536 371,526 372,509 366,502 362,491'),
  // les pans d'armure de la jupe
  skirt: sm('190,400 460,396 470,440 456,463 457,479 451,495 440,488 420,492 400,486 368,480 364,470 342,460 336,460 333,463 328,483 320,489 318,494 303,504! 304,489 301,486 294,486 286,495 286,501 279,506! 280,496 274,487 267,487 256,504! 254,499 257,486 254,483 247,483 241,489 237,489 232,498 215,515 200,480 186,440'),
  // le torse cuirassé et la ceinture
  torso: sm('230,300 300,296 380,296 430,300 444,340 440,400 420,412 330,416 240,414 210,400 206,350'),
  // l'épaulière gauche (de l'image), énorme, à plusieurs plaques
  pauL: sm('104,262! 130,262 156,250 180,240 210,236 244,238 270,254 280,282 270,312 246,334 210,346 170,346 146,330 134,314 112,306! 130,298 120,284!'),
  // le bras droit (à gauche de l'image) qui pend devant le corps, et son gantelet près de la ceinture
  armLb: sm('150,318 196,318 216,346 214,374 190,384 162,378 146,352'),
  fistLb: sm('164,362 196,352 226,364 232,390 218,408 188,410 168,398 160,380'),
  // l'épaulière droite et le bras qui tient l'épée
  pauR: sm('408,252 434,240 458,246 470,264 468,290 456,314 432,324 410,316 398,290'),
  armR: sm('420,312 452,304 470,330 476,362 470,388 448,398 428,384 420,350'),
  // l'épée : la lame (de la garde à la pointe), la garde dorée, la poignée et le pommeau
  blade: sm(`${sp(-0.04, 42)}! ${sp(0.84, 50)}! ${sp(1.04, 6)}! ${sp(0.9, -30)}! ${sp(0.78, -48)}! ${sp(0.7, -66)}! ${sp(0.66, -48)}! ${sp(0.56, -64)}! ${sp(0.52, -48)}! ${sp(0.42, -62)}! ${sp(0.38, -48)}! ${sp(0.28, -60)}! ${sp(0.24, -48)}! ${sp(0.14, -56)}! ${sp(0.1, -46)}! ${sp(-0.04, -46)}!`),
  guard: sm(`${sp(-0.04, 56)}! ${sp(0.1, 96)}! ${sp(0.03, 64)}! ${sp(0.04, 0)} ${sp(0.03, -66)}! ${sp(0.12, -104)}! ${sp(-0.04, -60)}! ${sp(-0.07, -26)} ${sp(-0.08, 0)} ${sp(-0.07, 26)}`),
  grip: sm(`${sp(-0.05, 10)}! ${sp(-0.24, 10)}! ${sp(-0.24, -10)}! ${sp(-0.05, -10)}!`),
  pommel: sm(`${sp(-0.24, 14)} ${sp(-0.3, 0)} ${sp(-0.24, -14)} ${sp(-0.21, 0)}`),
  fist: sm('446,352 466,342 486,350 494,368 490,388 474,398 452,396 440,382 438,366'),
  // la tête : le visage sombre, ses joues, le menton
  face: sm('262,180 296,158 344,150 392,156 428,172 446,196 448,210! 462,226 466,240 458,250! 448,256 450,270 442,288 426,304 400,314 366,318 332,310 304,292 280,264 264,232 258,206'),
  // l'oreille pointue à gauche
  ear: sm('276,206 254,186 226,170! 236,196 244,222 258,244 278,250'),
};

// ---------- le visage ----------
// une fissure de lave : une ligne brisée qui rougeoit (un halo orange, un cœur jaune)
const crack = (pts) => { const d = 'M' + pts.map(([x, y]) => `${x} ${y}`).join('L');
  return `<path d="${d}" fill="none" stroke="${FIRE.deep}" stroke-width="4.4" stroke-linejoin="round" stroke-linecap="round" opacity="0.8"/>`
    + `<path d="${d}" fill="none" stroke="${FIRE.base}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>`
    + `<path d="${d}" fill="none" stroke="${FIRE.hi}" stroke-width="0.9" stroke-linejoin="round" stroke-linecap="round"/>`; };
const { almond: almondK } = require('./formes.cjs');
// les yeux : deux fentes de braise étroites sous l'arcade (l'œil du fond plus étroit, vu de trois quarts)
const KE1 = almondK(374, 218, 40, 15, -1, 3.4), KE2 = almondK(428, 216, 26, 13, 1, 3);
const slit = (A, cx, cy) => `<path d="${A.white}" fill="url(#g-eye)"/>` + oval(cx + 2, cy, 2.2, 5.4, '#3a0a04') + shape(A.lash, '#0c080e');
const faceBody = use('face', 'url(#g-skin)') + clip('face',
  // la lueur du feu sur le haut du crâne, l'ombre de la mâchoire, la pommette éclairée
  glint([[270, 176, 6], [320, 158, 9], [380, 156, 8], [430, 176, 0]], FIRE.mid, 0.55)
  + shape(sm('264,232 284,270 314,298 350,314 400,314 430,302 446,280 446,330 260,330'), SKIN.deep, 0.75)
  + glint([[330, 252, 0], [370, 246, 4], [410, 252, 0]], SKIN.hi, 0.5)
  // la tempe et la joue de profil : un creux sous la pommette, une fissure de lave
  + glint([[300, 214, 0], [314, 246, 4], [330, 270, 0]], SKIN.deep, 0.6)
  + crack([[288, 186], [300, 200], [296, 214], [310, 226]]) + crack([[402, 282], [414, 292], [428, 288]])
  // la lueur des yeux
  + `<g class="a-eyes">${oval(376, 218, 30, 14, 'url(#g-glow)')}${oval(430, 216, 20, 12, 'url(#g-glow)')}</g>`
  + slit(KE1, 376, 218) + slit(KE2, 430, 216)
  // l'arcade lourde et basse, qui plonge vers le nez : elle mange le haut des yeux (regard dur, pas surpris)
  + `<path d="${sm('334,190 372,192 410,198 446,206! 446,214! 420,208 404,212 380,206 352,206 336,204')}" transform="translate(-1 3)" fill="${SKIN.deep}" opacity="0.8"/>`
  + shape(sm('334,190 372,192 410,198 446,206! 446,214! 420,208 404,212 380,206 352,206 336,204'), '#0e0a10')
  + glint([[338, 190, 0], [380, 191, 2], [430, 202, 0]], SKIN.hi, 0.6)
  // le nez qui avance : l'arête éclairée, la narine
  + glint([[440, 214, 0], [452, 228, 2.4], [458, 240, 0]], SKIN.hi, 0.7) + oval(452, 246, 4, 2.4, SKIN.deep, 1, 20)
  // la bouche : un rictus fermé sur le côté, deux crocs qui dépassent au coin
  + line('M396 284 Q420 280 446 270', '#0e0a10', 3.2) + line('M392 280 Q394 285 398 287', '#0e0a10', 2.4)
  + shape('M424 279 L428 291 L433 278 Z', '#f4ece0') + shape('M436 275 L439 285 L443 273 Z', '#f4ece0')
);

// ---------- le feu ----------
/** Les langues de feu de la crinière : chacune un fuseau du plus foncé (racine) au plus clair (pointe). */
// des langues de feu plus claires, courbes et de tailles différentes, qui montent depuis le crâne
// une mèche de feu : de sa racine b (sur le crâne) à sa pointe t, large de w, qui se recourbe en crochet vers l'arrière
function flameLock([bx, by], [tx, ty], w, hook = 0.7) {
  const dx = tx - bx, dy = ty - by, L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L, nx = -uy, ny = ux; // n : vers la gauche de la mèche
  const P2 = (x, y) => `${n(x)} ${n(y)}`;
  const a = [bx - nx * w / 2, by - ny * w / 2], b = [bx + nx * w / 2, by + ny * w / 2];
  return `M${P2(...a)}C${P2(bx + dx * 0.35 - nx * w * 0.65, by + dy * 0.35 - ny * w * 0.65)} ${P2(tx - dx * 0.3 - nx * w * (0.1 + hook), ty - dy * 0.3 - ny * w * (0.1 + hook))} ${P2(tx, ty)}`
    + `C${P2(tx - dx * 0.4 + nx * w * 0.05, ty - dy * 0.4 + ny * w * 0.05)} ${P2(bx + dx * 0.4 + nx * w * 0.6, by + dy * 0.4 + ny * w * 0.6)} ${P2(...b)}Z`;
}
const LOCKS = [
  // derrière : grandes mèches rouge sombre
  [[[262, 214], [106, 120], 70], [[278, 190], [140, 34], 80], [[322, 172], [226, 2], 86], [[368, 162], [322, 4], 76], [[408, 168], [420, 30], 58], [[244, 248], [96, 196], 56]],
  // au milieu : orange
  [[[282, 194], [176, 70], 58], [[330, 174], [270, 26], 62], [[376, 164], [376, 40], 52], [[258, 226], [150, 158], 50], [[410, 176], [446, 84], 40]],
  // devant : jaune, plus courtes
  [[[300, 184], [240, 96], 40], [[350, 170], [326, 82], 40], [[272, 210], [204, 150], 34], [[396, 172], [408, 110], 30]],
];
const LOCK_COL = [['#9a2006', '#e8480c'], ['#e8600a', '#ffa82a'], ['#ffc030', '#fff4c0']];
const fireLocks = LOCKS.map((layer, k) => layer.map(([b, t, w], i) => {
  const d = flameLock(b, t, w), id = `g-lk${k}-${i}`;
  return `<linearGradient id="${id}" gradientUnits="userSpaceOnUse" x1="${b[0]}" y1="${b[1]}" x2="${t[0]}" y2="${t[1]}"><stop offset="0" stop-color="${LOCK_COL[k][0]}"/><stop offset="1" stop-color="${LOCK_COL[k][1]}"/></linearGradient>`
    + (k ? `<path d="${d}" transform="translate(-3 4)" fill="${FIRE.deep}" opacity="0.45"/>` : '') + `<path d="${d}" fill="url(#${id})"/>`;
}).join('')).join('');
const FIRE_D = LOCKS[0].map(([b, t, w]) => flameLock(b, t, w)).join('') + LOCKS[1].map(([b, t, w]) => flameLock(b, t, w)).join('');

// ---------- les braises de lave entre les plaques ----------
const EMBERS = [[330, 340, 16], [196, 470, 14], [400, 468, 12], [300, 400, 8], [252, 330, 6]];
const embers = EMBERS.map(([x, y, r]) => `<g class="a-ember">${oval(x, y, r * 2.2, r * 1.6, 'url(#g-glow)')}${oval(x, y, r * 0.55, r * 0.4, 'url(#g-ember)')}</g>`).join('');

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
/** Une plaque d'armure bombée : sa forme, l'arête claire en haut à droite, le bord sombre en bas à gauche. */
const { cel } = require('./formes.cjs');
const plate = (d, hiPts, shPts) => `<path d="${d}" fill="${ARM.deep}" transform="translate(-2 3)" opacity="0.8"/>` + shape(d, 'url(#g-armor)') + (hiPts ? glint(hiPts, '#d4d0dc', 0.75) : '') + (shPts ? glint(shPts, ARM.deep, 0.8) : '');
// ---------- les jambes (redessinées) ----------
const { ellipse } = require('./formes.cjs');
const legSet = (thigh, knee, boot, cracks, toe) => ({ thigh: rib(thigh), knee, boot, cracks, toe });
const LEG = {
  Lp: legSet([[178, 462, 64], [168, 500, 56], [160, 528, 50]], [162, 500, 24, 20], sm('118,508 194,506 202,528 208,560! 88,560! 84,546 96,530 116,524'), [[[134, 528], [146, 542], [162, 536], [174, 548]]], [90, 556, 24, 16]),
  Rp: legSet([[404, 462, 64], [414, 498, 56], [420, 524, 50]], [418, 498, 24, 20], sm('382,506 456,506 462,524 494,532 520,546 524,560! 380,560! 376,540'), [[[420, 526], [436, 540], [452, 534], [470, 546]]], [474, 558, 24, 16]),
};
LEG.L = LEG.Lp.thigh + LEG.Lp.boot + ellipse(...LEG.Lp.knee);
LEG.R = LEG.Rp.thigh + LEG.Rp.boot + ellipse(...LEG.Rp.knee);
const ARMOR_PAL = { hi: '#8a8698', base: ARM.base, sh: ARM.shade, deep: ARM.deep };
function legPaint(L) {
  const [kx, ky, krx, kry] = L.knee, kd = ellipse(kx, ky, krx, kry);
  return `<path d="${L.thigh}" fill="url(#g-armor)"/>` + cel(L.thigh, { ...ARMOR_PAL, base: 'none' }, 6, 3)
    // la botte de fer : le bout bombé, une semelle sombre, la lumière sur le dessus
    + `<path d="${L.boot}" fill="url(#g-armor)"/>` + cel(L.boot, { ...ARMOR_PAL, base: 'none' }, 6, 3)
    + shape(`M${L.toe[0]} ${L.toe[1]}a${L.toe[2]} ${L.toe[3]} 0 0 1 ${2 * L.toe[2]} 0Z`, ARM.lite, 0.8) + glint([[L.toe[0] + 6, L.toe[1] - 4, 0], [L.toe[0] + L.toe[2], L.toe[1] - L.toe[3] + 3, 2.4], [L.toe[0] + 2 * L.toe[2] - 6, L.toe[1] - 4, 0]], ARM.hi, 0.8)
    + L.cracks.map(crack).join('')
    // la genouillère ronde et sa pointe
    + `<path d="${kd}" transform="translate(-2 4)" fill="${ARM.deep}" opacity="0.7"/>` + cel(kd, { hi: ARM.hi, base: ARM.lite, sh: ARM.base, deep: ARM.shade }, 5, 2.4)
    + shape(`M${kx - 7} ${ky - kry + 6}L${kx} ${ky - kry - 12}L${kx + 7} ${ky - kry + 6}Z`, ARM.mid) + shape(`M${kx} ${ky - kry - 12}L${kx + 7} ${ky - kry + 6}L${kx + 1} ${ky - kry + 6}Z`, ARM.hi, 0.7)
    + dot(kx, ky, 5, FIRE.base) + dot(kx, ky, 2.4, FIRE.hi);
}

const parts = [
  { id: 'cape', cls: 'a-cape', d: S.cape, body: use('cape', 'url(#g-cape)') + clip('cape',
    glint([[140, 290, 0], [100, 360, 6], [60, 420, 6], [30, 460, 0]], ARM.lite, 0.4) + glint([[170, 300, 0], [150, 380, 6], [120, 450, 0]], ARM.deep, 0.6)
    + oval(130, 300, 40, 30, FIRE.mid, 0.25)) },
  { id: 'fire', cls: 'a-fire', free: true, d: FIRE_D, body: fireLocks },
  { id: 'legL', free: true, d: LEG.L, shadow: [sh(['cape'], -4, 4, SH.armor, 0.45)], body: legPaint(LEG.Lp) },
  { id: 'legR', free: true, d: LEG.R, shadow: [sh(['cape'], -4, 4, SH.armor, 0.45)], body: legPaint(LEG.Rp) },
  { id: 'skirt', d: S.skirt, shadow: [sh(['legL', 'legR', 'cape'], -4, 5, SH.armor, 0.5)], body: use('skirt', 'url(#g-armor)') + clip('skirt',
    // des pans d'armure qui se recouvrent, chacun son arête claire ; deux braises entre les plaques
    [[200, 420, 260, 500], [270, 420, 300, 500], [320, 420, 330, 480], [370, 420, 380, 480], [420, 420, 450, 480]].map(([x0, y0, x1, y1]) =>
      glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 4], [x1, y1, 0]], ARM.deep, 0.7) + glint([[x0 + 6, y0, 0], [(x0 + x1) / 2 + 6, (y0 + y1) / 2, 2.4], [x1 + 6, y1, 0]], ARM.hi, 0.5)).join('')) },
  { id: 'torso', d: S.torso, shadow: [sh(['cape', 'fire', 'skirt'], -5, 5, SH.armor, 0.5)], body: use('torso', 'url(#g-armor)') + clip('torso',
    // le plastron en deux pectoraux bombés, la ceinture de cuir à rivets, la lueur de la lave au centre
    plate(sm('236,310 300,304 336,316 330,360 296,372 250,362'), [[250, 314, 0], [296, 308, 3], [330, 320, 0]], [[244, 364, 3], [296, 372, 4], [328, 362, 3]])
    + plate(sm('340,316 380,304 426,310 436,352 410,370 350,364'), [[350, 312, 0], [390, 306, 3], [430, 318, 0]], [[352, 366, 3], [400, 372, 4], [432, 356, 3]])
    + shape(sm('210,388 330,392 440,386 440,406 330,412 214,408'), '#2a1c1c') + [[240, 398], [290, 400], [380, 398], [420, 396]].map(([x, y]) => dot(x, y, 3, ARM.hi)).join('')
    + oval(338, 344, 30, 22, 'url(#g-glow)')
    + crack([[256, 330], [272, 338], [282, 330], [300, 340]]) + crack([[376, 326], [392, 336], [404, 330], [418, 342]])
    + shape('M316 304 L330 322 L326 334 L338 352 L350 334 L346 322 L360 304 L348 316 L338 306 L328 316 Z', FIRE.lite) + shape('M330 320 L338 338 L346 320 L338 328 Z', FIRE.core)) },
  { id: 'pauL', cls: 'a-body', d: S.pauL, shadow: [sh(['torso', 'cape', 'fire'], -4, 6, SH.armor, 0.5)], body: use('pauL', 'url(#g-armor)') + clip('pauL',
    // une grosse plaque de roche bombée (claire en haut à droite), deux pointes, des fissures de lave qui rougeoient
    cel(S.pauL, { hi: ARM.lite, base: ARM.base, sh: ARM.shade, deep: ARM.deep }, 8, 3)
    + shape('M168 262 L182 222 L196 258 Z', ARM.mid) + shape('M182 222 L196 258 L186 258 Z', ARM.lite, 0.8)
    + shape('M212 258 L232 226 L240 262 Z', ARM.mid) + shape('M232 226 L240 262 L232 262 Z', ARM.lite, 0.8)
    + crack([[150, 300], [170, 296], [178, 308], [200, 304]]) + crack([[210, 320], [226, 312], [236, 318]])
    + glint([[150, 262, 0], [200, 244, 2.4], [262, 250, 0]], FIRE.base, 0.7)) },
  // les flammes le long des deux tranchants (sans contour : elles brûlent), derrière la lame
  // le feu le long des deux tranchants (sans contour : il brûle), derrière la lame : une bordure ondulée et irrégulière
  // (orange, puis jaune contre la lame), et quelques braises qui s'envolent au-dessus
  { id: 'swordFire', cls: 'a-sword', d: 'M-900 -900', body: `<g class="a-sglow">`
    + `<ellipse cx="${spa(0.45, 0)[0]}" cy="${spa(0.45, 0)[1]}" rx="${n(SL * 0.68)}" ry="88" transform="rotate(${n(Math.atan2(SU[1], SU[0]) * 180 / Math.PI)} ${spa(0.45, 0)[0]} ${spa(0.45, 0)[1]})" fill="url(#g-glow)" opacity="0.6"/>`
    + [[-46, -1, 0.0, 0.72, [6, 14, 9, 20, 12, 24, 10, 17, 22, 13, 19, 8, 4]], [44, 1, 0.0, 0.86, [5, 10, 16, 9, 18, 12, 22, 14, 10, 18, 9, 14, 6, 3]]].map(([s0, side, f0, f1, W]) => {
      const pts = W.map((w, i) => { const f = f0 + (f1 - f0) * (i / (W.length - 1)); const p = spa(f, s0 + side * (w / 2 - 2)); return [p[0], p[1], i === 0 || i === W.length - 1 ? 0 : w]; });
      const inner = W.map((w, i) => { const f = f0 + (f1 - f0) * (i / (W.length - 1)); const p = spa(f, s0 + side * 2); return [p[0], p[1], i === 0 || i === W.length - 1 ? 0 : Math.min(7, w * 0.45)]; });
      return shape(rib(pts), FIRE.mid, 0.95) + shape(rib(pts.map(([x, y, w]) => [x, y, w * 0.6])), FIRE.base, 0.95) + shape(rib(inner), FIRE.hi, 0.95);
    }).join('')
    + [[0.2, -70, 3], [0.33, -64, 2.4], [0.47, -76, 2], [0.58, -62, 2.6], [0.12, -58, 2], [0.66, -72, 1.8]].map(([f, off, r]) => { const p = spa(f, off); return oval(p[0], p[1], r * 1.6, r, FIRE.base, 0.9, -42) + dot(p[0], p[1], r * 0.5, FIRE.hi); }).join('')
    + '</g>' },
  { id: 'blade', cls: 'a-sword', free: true, d: S.blade, shadow: [sh(['torso', 'pauR', 'skirt'], -4, 6, SH.armor, 0.4)], body: use('blade', 'url(#g-blade)') + clip('blade',
    // la lame noire : le tranchant du haut incandescent, une seule gorge de lave au milieu, l'arête claire du dos
    glint([spa(-0.02, -41).concat(4), spa(0.4, -41).concat(6), spa(0.7, -42).concat(4), spa(1, 6).concat(0)], FIRE.mid, 0.95)
    + glint([spa(-0.02, -43).concat(0), spa(0.4, -43).concat(2.4), spa(0.7, -44).concat(0)], FIRE.hi, 0.95)
    + glint([spa(0.04, 2).concat(0), spa(0.3, 4).concat(9), spa(0.62, 5).concat(8), spa(0.84, 4).concat(0)], FIRE.deep, 0.95)
    + glint([spa(0.06, 2).concat(0), spa(0.3, 4).concat(5.4), spa(0.62, 5).concat(4.6), spa(0.82, 4).concat(0)], FIRE.base, 0.95)
    + glint([spa(0.1, 2).concat(0), spa(0.3, 4).concat(1.8), spa(0.6, 5).concat(1.6), spa(0.78, 4).concat(0)], FIRE.core, 0.95)
    + glint([spa(0, 40).concat(0), spa(0.45, 44).concat(2.4), spa(0.85, 46).concat(0)], '#8a7e8c', 0.7)
    // la facette claire de la pointe (le chanfrein)
    + shape(`M${spa(0.71, -46).join(' ')} L${spa(1.01, 8).join(' ')} L${spa(0.86, -10).join(' ')} Z`, '#6a5a60', 0.8)) },
  { id: 'grip', cls: 'a-sword', free: true, d: S.grip, body: use('grip', '#3a2420') + clip('grip', glint([spa(-0.06, 4).concat(0), spa(-0.15, 4).concat(3), spa(-0.24, 4).concat(0)], '#8a5a4a', 0.7)) },
  { id: 'pommel', cls: 'a-sword', free: true, d: S.pommel, body: use('pommel', 'url(#g-gold)') },
  { id: 'guard', cls: 'a-sword', free: true, d: S.guard, shadow: [sh(['blade', 'torso', 'grip'], -3, 5, SH.armor, 0.45)], body: use('guard', 'url(#g-gold)') + clip('guard',
    glint([spa(0.02, 50).concat(0), spa(0.03, 20).concat(3), spa(0.03, -20).concat(3), spa(0.02, -50).concat(0)], GOLD.hi, 0.9)
    + glint([spa(-0.04, 40).concat(0), spa(-0.05, 0).concat(3), spa(-0.04, -40).concat(0)], GOLD.shade, 0.8)
    + oval(...spa(0, 0), 7, 6, '#c83a2a') + oval(...spa(0.004, -2), 2.4, 1.8, '#ffd0c0')) },
  { id: 'pauR', cls: 'a-sword', d: S.pauR, shadow: [sh(['torso', 'fire'], -3, 5, SH.armor, 0.5)], body: use('pauR', 'url(#g-armor)') + clip('pauR',
    plate(sm('402,262 430,246 460,250 470,272 448,284 418,286'), [[414, 254, 0], [440, 246, 3], [464, 260, 0]], [[404, 286, 3], [440, 288, 4], [468, 280, 3]])
    + glint([[404, 300, 0], [430, 314, 3], [456, 310, 0]], ARM.deep, 0.6)) },
  { id: 'armR', cls: 'a-sword', d: S.armR, shadow: [sh(['torso', 'pauR'], -3, 5, SH.armor, 0.45)], body: use('armR', 'url(#g-armorX)') + clip('armR',
    glint([[430, 320, 0], [460, 340, 3], [470, 370, 0]], ARM.hi, 0.5)) },
  { id: 'fist', cls: 'a-sword', d: S.fist, shadow: [sh(['guard', 'armR', 'blade'], -3, 5, SH.armor, 0.45)], body: use('fist', 'url(#g-armor)') + clip('fist',
    // le gantelet : des doigts de fer en plaques, une arête claire
    [[446, 372, 490, 368], [444, 386, 494, 384], [448, 400, 488, 398]].map(([x1, y1, x2, y2]) => glint([[x1, y1, 0], [(x1 + x2) / 2, (y1 + y2) / 2, 3], [x2, y2, 0]], ARM.deep, 0.7)
      + glint([[x1, y1 - 3, 0], [(x1 + x2) / 2, (y1 + y2) / 2 - 3, 1.6], [x2, y2 - 3, 0]], ARM.hi, 0.5)).join('')) },
  { id: 'armLb', cls: 'a-body', d: S.armLb, shadow: [sh(['torso', 'skirt', 'pauL'], -4, 5, SH.armor, 0.5)], body: use('armLb', 'url(#g-armorX)') + clip('armLb',
    plate(sm('148,330 196,322 214,346 196,354 152,352'), [[156, 330, 0], [184, 324, 3], [210, 342, 0]], [[150, 352, 3], [180, 356, 4], [208, 350, 3]])) },
  { id: 'fistLb', cls: 'a-body', d: S.fistLb, shadow: [sh(['armLb', 'torso', 'skirt'], -3, 5, SH.armor, 0.5)], body: use('fistLb', 'url(#g-armor)') + clip('fistLb',
    [[172, 372, 222, 368], [170, 386, 226, 384], [176, 400, 218, 398]].map(([x1, y1, x2, y2]) => glint([[x1, y1, 0], [(x1 + x2) / 2, (y1 + y2) / 2, 3], [x2, y2, 0]], ARM.deep, 0.75)
      + glint([[x1, y1 - 3, 0], [(x1 + x2) / 2, (y1 + y2) / 2 - 3, 1.6], [x2, y2 - 3, 0]], '#d4d0dc', 0.6)).join('')) },
  { id: 'ear', cls: 'a-head', free: true, d: S.ear, shadow: [sh(['fire', 'pauL'], -3, 4, SH.fire, 0.4)], body: use('ear', 'url(#g-skin)') + clip('ear', shape(sm('266,212 248,196 236,186 246,212 256,234 268,240'), SKIN.deep, 0.7)) },
  { id: 'face', cls: 'a-head', free: true, d: S.face, shadow: [sh(['fire', 'pauL', 'torso', 'ear'], -4, 6, SH.armor, 0.45)], body: faceBody },
  // --- les braises et la lueur de l'épée (sans contour : elles brillent) ---
  { id: 'embers', d: 'M-900 -900', body: embers },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : la crinière de flammes danse, les braises et les yeux palpitent, la cape ondule, la tête hoche à peine,
// l'épée oscille dans son poing.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : il lève son épée en arrière (élan), puis l'abat en avant en un grand
// coup de taille (35–55 %) ; les flammes se couchent puis jaillissent ; tout revient à la pose de repos.
const PIV = { head: [340, 320], fire: [300, 240], cape: [150, 300], sword: [450, 330] };
const IDLE = {
  'a-head': ['head', 'head 3s ease-in-out infinite alternate'],
  'a-fire': ['fire', 'fire 1s ease-in-out infinite alternate'],
  'a-cape': ['cape', 'cape 3.6s ease-in-out infinite alternate'],
  'a-sword': ['sword', 'sword 2.8s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-eyes{animation:eyes 1.2s ease-in-out infinite alternate}
.a-ember{animation:ember 1.4s ease-in-out infinite alternate}
@keyframes head{from{transform:none}to{transform:rotate(-1deg)}}
@keyframes fire{from{transform:none}to{transform:scale(1.03,1.06) skewX(-2deg)}}
@keyframes cape{from{transform:none}to{transform:rotate(1.2deg)}}
@keyframes sword{from{transform:none}to{transform:rotate(-1.4deg)}}
@keyframes eyes{from{opacity:.7}to{opacity:1}}
@keyframes ember{from{opacity:.6}to{opacity:1}}
.a-sglow{animation:ember 1s ease-in-out infinite alternate}
${atk('a-sword', 'sword-atk')}${atk('a-head', 'head-atk')}${atk('a-fire', 'fire-atk')}${atk('a-cape', 'cape-atk')}
@keyframes sword-atk{0%{transform:none}32%{transform:rotate(-18deg)}50%{transform:rotate(16deg)}64%{transform:rotate(12deg)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}32%{transform:rotate(-2deg)}50%{transform:translate(3px,1px) rotate(2deg)}100%{transform:none}}
@keyframes fire-atk{0%{transform:none}32%{transform:scale(.96,.9) skewX(4deg)}50%{transform:scale(1.06,1.14) skewX(-6deg)}100%{transform:none}}
@keyframes cape-atk{0%{transform:none}32%{transform:rotate(2deg)}52%{transform:rotate(-3deg)}100%{transform:none}}
`.replace(/\n/g, '');

module.exports = { id: 'assassins-2', w: W, h: H, pad: PAD, foot: [300, 552],
  svg: (anime = true) => figure({ master: require('./silhouettes/assassins-2.json'), w: W, h: H, pad: PAD, defs, style, parts, anime }) };
