// Le cerf-volant (epouvantails-3), monstre des Épouvantails : redessiné par le code d'après le dessin d'origine, dans
// le même cadre (436 × 482, mêmes proportions, même pose) : un cerf-volant en losange penché, fait de quatre pans de
// toile rapiécée (rouge en haut à gauche et en bas à droite, bleu-vert ailleurs), cousus le long des deux baguettes ;
// deux gros yeux jaunes furieux, une gueule en dents de scie qui s'ouvre au milieu ; une queue de ficelle qui ondule
// vers le bas à gauche, ornée de nœuds de tissu jaunes, bleu-vert et rouges.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. Contour décalqué sur l'original.
// Il vole : son ombre est posée au sol sous lui.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 436, H = 482, PAD = 40;

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
const RED = { hi: '#ff9a72', lite: '#f26a40', base: '#e04a2a', shade: '#a82a1c', deep: '#6a1410' };
const TEAL = { hi: '#a8f0e8', lite: '#5ac8c4', base: '#2fa4a8', shade: '#1a7078', deep: '#0e4650' };
const YEL = { hi: '#fff2a0', base: '#f4c430', shade: '#b08414' };
const STRING = '#5a3a24';
const SH = { red: '#3a0a06', teal: '#06262c' };

// ---------- le losange : ses quatre coins et le croisement des baguettes ----------
const T = [328, 10], R = [428, 180], B = [240, 354], L = [146, 172], C = [300, 186];

// ---------- dégradés ----------
const defs = [
  lin('g-red', 0, 0, 1, 1, [[0, RED.lite], [0.5, RED.base], [1, RED.shade]], false),
  lin('g-teal', 1, 0, 0, 1, [[0, TEAL.hi], [0.4, TEAL.lite], [1, TEAL.shade]], false),
  rad('g-eye', 0.4, 0.4, 0.75, [[0, '#fffbd0'], [0.45, '#ffd83a'], [1, '#d08a10']], false),
  lin('g-mouth', 0, 220, 0, 280, [[0, '#2a0806'], [1, '#6a1a10']]),
  lin('g-yel', 0, 0, 1, 1, [[0, YEL.hi], [0.5, YEL.base], [1, YEL.shade]], false),
  lin('g-bowT', 0, 0, 1, 1, [[0, TEAL.hi], [0.5, TEAL.base], [1, TEAL.shade]], false),
  lin('g-bowR', 0, 0, 1, 1, [[0, RED.hi], [0.5, RED.base], [1, RED.shade]], false),
].join('');

// ---------- la queue : une ficelle qui ondule, et ses nœuds ----------
// la ficelle passe par les nœuds (mesurés sur l'original : jaune 172,372 ; bleu-vert 118,410 ; rouge 50,410 ; jaune du bas 112,460)
const STR = [[240, 352, 5], [206, 362, 5], [172, 374, 5], [146, 394, 4.6], [120, 410, 4.4], [92, 420, 4], [64, 414, 3.6], [36, 410, 3]];
const STR2 = [[120, 410, 4], [118, 434, 3.6], [112, 460, 3.2], [104, 474, 2.6]];
// la queue entière (ficelle et nœuds) prise dans la silhouette de l'original ; les couleurs des nœuds relevées sur l'original
const TAIL_D = sm('248,359 235,355 218,325 216,330 221,336 219,338 216,337 212,341 201,342 192,347 186,348 174,358 166,336 159,329 151,329 147,338 146,348 131,368 131,372 149,373 162,370 166,374 156,386 147,407 134,423 131,420 132,407 128,392 115,395 100,403 96,409 96,416 108,423 115,424 120,428 114,434 103,438 82,438 73,434 64,427 67,424 75,424 81,418 81,415 79,412 80,403 66,390 61,380 57,383 60,388 60,394 56,400 55,406 52,408 51,416 47,407 34,394 34,386 28,376 24,377 24,381 27,385 28,394 30,397 27,399 11,400 5,404 4,407 14,408 31,424 45,426 31,433 29,436 29,440 37,452 41,452 48,442 55,439 58,433 74,442 85,445 87,447 87,457 82,466 82,470 88,471 90,477 95,479 110,472 126,469 137,460 145,458 166,435 167,430 138,426 151,413 161,391 170,380 175,382 171,402 177,424 180,424 209,391 207,387 194,385 190,382 189,378 197,369 203,365 209,365 215,361 224,361 232,358 240,366');
const COLS = {"yel": ["87,457 85,468 95,469 93,459 91,457", "104,460 104,464 112,465 115,468 125,467 131,463 131,458 129,457 128,452 117,453 116,450 112,450 106,456 106,459", "164,430 155,427 136,427 136,432 131,434 132,453 137,453 138,456 144,455 164,434", "152,328 150,345 146,347 140,353 140,357 136,359 136,370 151,371 160,368 165,368 166,373 171,373 172,376 175,377 175,385 177,386 177,415 183,416 206,392 206,387 194,384 189,380 187,371 191,365 191,361 186,361 184,364 171,361 171,352 169,344 167,343 164,336 161,333 161,330"], "teal": ["99,404 98,412 102,412 105,407 109,407 110,403 114,403 115,407 118,410 125,412 125,421 129,421 129,399 126,397 125,394 115,394 112,397 103,400", "222,318 222,327 226,332 228,339 232,343 232,348 236,348 237,342 234,332 235,323 234,321 231,321 229,318"], "red": ["98,472 109,471 110,469 117,469 118,464 112,458 105,458 102,461 102,463 99,464", "65,390 61,390 58,394 55,403 55,409 53,412 48,412 46,410 46,406 40,400 39,396 36,393 32,393 30,398 14,398 11,400 11,406 15,407 27,421 40,425 39,428 35,429 31,433 31,441 35,442 36,447 41,447 45,441 54,436 54,430 51,429 52,426 54,426 55,428 60,428 62,433 67,433 67,429 62,428 61,424 68,423 72,419 77,419 79,417 76,400 74,397 70,397 69,393"]};
const KNOTS = [[172, 372, 'yel'], [118, 410, 'bowT'], [50, 410, 'bowR'], [112, 460, 'yel']];
/** Un nœud de tissu : deux ailes en triangle bombé de part et d'autre du centre (x, y), tourné de `a` degrés. */
function bow(x, y, a, s = 1) {
  const r = (a * Math.PI) / 180, c = Math.cos(r), si = Math.sin(r);
  const p = (dx, dy) => `${n(x + (dx * c - dy * si) * s)},${n(y + (dx * si + dy * c) * s)}`;
  return sm(`${p(0, -4)} ${p(-14, -20)}! ${p(-24, -12)} ${p(-26, 4)}! ${p(-14, 6)} ${p(0, 4)} ${p(14, 6)} ${p(26, 4)}! ${p(24, -12)} ${p(14, -20)}!`, 2);
}
const BOWS = [[176, 384, -60, 'yel', 1.1], [128, 432, -20, 'bowT', 1], [56, 422, 10, 'bowR', 1.05], [126, 466, 20, 'yel', 0.9]];

// ---------- silhouettes ----------
const S = {
  tail: TAIL_D,
  kite: sm(`${T[0]},${T[1]}! ${R[0]},${R[1]}! ${B[0]},${B[1]}! ${L[0]},${L[1]}!`),
  // les deux rubans de toile déchirée qui pendent sous le coin gauche
  rag: sm('176,244 184,258 186,272 194,286 196,296! 182,290 176,280 168,284! 166,270 168,258'),
};

// ---------- le losange ----------
const P2 = (p) => `${p[0]} ${p[1]}`;
const tri = (a, b, c) => `M${P2(a)} L${P2(b)} L${P2(c)} Z`;
const kiteBody = use('kite', 'url(#g-teal)') + clip('kite',
  // les quatre pans : rouge en haut à gauche, bleu-vert en haut à droite, bleu-vert en bas à gauche, rouge en bas à droite
  shape(tri(T, C, L), 'url(#g-red)') + shape(tri(T, R, C), 'url(#g-teal)') + shape(tri(L, C, B), 'url(#g-teal)') + shape(tri(C, R, B), 'url(#g-red)')
  // l'ombre en bas à gauche, la lumière en haut à droite de chaque pan
  + shape(tri([L[0], L[1] + 4], [B[0] - 4, B[1]], [C[0] - 30, C[1] + 60]), TEAL.deep, 0.35)
  + shape(tri([C[0] + 10, C[1] - 6], [T[0] + 2, T[1] + 30], [R[0] - 40, R[1] - 20]), TEAL.hi, 0.35)
  + shape(tri([T[0] - 6, T[1] + 30], [L[0] + 40, L[1] - 10], [C[0] - 10, C[1] - 20]), RED.hi, 0.3)
  // les coutures le long des baguettes : une rainure (sombre + claire) et des points de couture
  + glint([[T[0], T[1], 0], [C[0] + 12, (T[1] + C[1]) / 2, 5], [C[0], C[1], 4], [B[0] + 30, (C[1] + B[1]) / 2, 5], [B[0], B[1], 0]], '#3a1a10', 0.6)
  + glint([[L[0], L[1], 0], [(L[0] + C[0]) / 2, L[1] + 6, 4], [C[0], C[1], 4], [(C[0] + R[0]) / 2, C[1] + 2, 4], [R[0], R[1], 0]], '#3a1a10', 0.55)
  + [0.15, 0.3, 0.45, 0.6, 0.75].map((f) => { const x = T[0] + (B[0] - T[0]) * f + 8, y = T[1] + (B[1] - T[1]) * f; return line(`M${n(x - 4)} ${n(y - 2)} L${n(x + 4)} ${n(y + 2)}`, '#f6e0c0', 1.6, 0.8); }).join('')
  // des pièces rapiécées : un carré bleu-vert sur le pan rouge du bas, un bord effiloché
  + shape('M332 262 L360 250 L370 276 L342 288 Z', TEAL.base, 0.95) + line('M334 264 L360 252 M342 286 L368 274', '#f6e0c0', 1.4, 0.7)
  // les yeux : l'œil furieux à gauche, l'autre à droite, sous des sourcils de toile froncés
  + `<g class="a-eyes">`
  + oval(268, 176, 26, 22, '#2a0a06') + oval(268, 176, 23, 19, 'url(#g-eye)') + oval(275, 179, 7, 11, '#1a0806') + dot(270, 173, 3.6, '#fff')
  + oval(356, 176, 26, 22, '#2a0a06') + oval(356, 176, 23, 19, 'url(#g-eye)') + oval(363, 179, 7, 11, '#1a0806') + dot(358, 173, 3.6, '#fff')
  // les paupières lourdes, penchées vers le milieu : elles coupent le haut des yeux (regard furieux)
  + shape('M238 152 L304 152 L304 180 C290 164 262 160 240 168 Z', RED.base) + line('M240 168 C262 160 290 164 304 180', '#2a0a06', 4)
  + shape('M386 152 L320 152 L320 180 C334 164 362 160 384 168 Z', TEAL.base) + line('M384 168 C362 160 334 164 320 180', '#2a0a06', 4)
  + `<g class="a-blink" opacity="0">${oval(268, 172, 25, 21, RED.base)}${oval(356, 172, 25, 21, TEAL.base)}</g>`
  + '</g>'
  + shape('M232 150 C254 138 284 142 306 166 L298 172 C280 154 256 150 236 158 Z', RED.deep)
  + shape('M392 152 C372 142 346 146 322 170 L330 176 C350 156 372 152 390 160 Z', TEAL.deep)
  // la gueule en dents de scie, au milieu sous les yeux
  + `<g class="a-mouth"><path d="M246 228 L262 238 L270 226 L282 240 L294 224 L304 242 L316 226 L326 240 L340 230 L334 250 L322 268 L310 254 L300 276 L288 256 L276 272 L266 252 L254 262 Z" fill="url(#g-mouth)"/>`
  + shape('M262 238 L270 226 L282 240 Z M294 224 L304 242 L316 226 Z M322 268 L310 254 L300 276 Z M276 272 L266 252 L254 262 Z', '#fff4d0') + '</g>'
);

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'tail', cls: 'a-tail', d: S.tail, body: use('tail', STRING) + clip('tail',
    // la ficelle (le fond) : un reflet ; puis les ailes des nœuds dans leurs couleurs, une bosse claire et un pli sombre
    glint(STR.map(([x, y], i) => [x + 1, y - 1.6, i === 0 || i === STR.length - 1 ? 0 : 1.8]), '#a87a5a', 0.8)
    + [['yel', 'g-yel', YEL.shade], ['teal', 'g-bowT', TEAL.shade], ['red', 'g-bowR', RED.shade]].map(([k, g, dk]) => COLS[k].map((t) => {
      const d = sm(t);
      return shape(d, `url(#${g})`) + `<path d="${d}" fill="${dk}" opacity="0.35" transform="translate(-2 3)"/>`;
    }).join('')).join('')
    + KNOTS.map(([x, y, g]) => dot(x, y, 5.5, g === 'yel' ? YEL.shade : g === 'bowT' ? TEAL.shade : RED.shade) + dot(x + 1.5, y - 1.5, 2, '#ffffff', 0.6)).join('')) },
  { id: 'rag', cls: 'a-kite', d: S.rag, body: use('rag', '#4a3a3a') + clip('rag', glint([[178, 250, 0], [184, 270, 2], [190, 290, 0]], '#8a7a78', 0.7)) },
  { id: 'kite', cls: 'a-kite', d: S.kite, shadow: [sh(['tail', 'rag'], -4, 6, SH.teal, 0.45)], body: kiteBody },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : il flotte dans le vent (il monte, descend et se balance autour de son centre), la queue ondule et ses nœuds
// battent en retard, la gueule s'ouvre et se ferme, il cligne.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : il pique en arrière (élan) puis plonge en avant en tournoyant à moitié,
// la gueule grande ouverte ; tout revient à la pose de repos.
const style = `
.a-root{transform-origin:300px 186px;animation:float 2.4s ease-in-out infinite alternate}
.a-kite{transform-origin:300px 186px}
.a-tail{transform-origin:240px 352px;animation:tail 1.6s ease-in-out infinite alternate}
.a-mouth{transform-origin:292px 250px;animation:mouth 1.2s ease-in-out infinite alternate}
.a-blink{animation:blink 4.2s linear infinite}
@keyframes float{from{transform:translate(0,0) rotate(-3deg)}to{transform:translate(4px,-10px) rotate(3deg)}}
@keyframes tail{from{transform:rotate(-6deg)}to{transform:rotate(7deg)}}
@keyframes mouth{from{transform:scale(1,.85)}to{transform:scale(1,1.08)}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
.atk .a-root{animation:float 2.4s ease-in-out infinite alternate,root-atk .75s ease-in-out;animation-composition:replace,add}
.atk .a-mouth{animation:mouth-atk .75s ease-in-out}
.atk .a-tail{animation:tail 1.6s ease-in-out infinite alternate,tail-atk .75s ease-in-out;animation-composition:replace,add}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-10px,-6px) rotate(-10deg)}50%{transform:translate(24px,10px) rotate(18deg)}64%{transform:translate(18px,6px) rotate(10deg)}100%{transform:none}}
@keyframes mouth-atk{0%{transform:none}30%{transform:scale(1,.8)}50%{transform:scale(1.08,1.35)}64%{transform:scale(1.04,1.2)}100%{transform:none}}
@keyframes tail-atk{0%{transform:none}30%{transform:rotate(10deg)}50%{transform:rotate(-14deg)}100%{transform:none}}
`.replace(/\n/g, '');

function svg(anime = true) {
  const s = figure({ master: require('./silhouettes/epouvantails-3.json'), w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'epouvantails-3', w: W, h: H, pad: PAD, foot: [220, 474], svg };
