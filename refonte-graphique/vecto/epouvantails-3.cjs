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
const STR = [[240, 352, 5], [214, 362, 5], [188, 376, 5], [166, 396, 4.6], [146, 418, 4.4], [122, 434, 4.2], [96, 440, 4], [70, 434, 3.6], [50, 424, 3]];
const STR2 = [[146, 418, 4], [148, 440, 3.6], [140, 460, 3.4], [128, 470, 3]];
/** Un nœud de tissu : deux ailes en triangle bombé de part et d'autre du centre (x, y), tourné de `a` degrés. */
function bow(x, y, a, s = 1) {
  const r = (a * Math.PI) / 180, c = Math.cos(r), si = Math.sin(r);
  const p = (dx, dy) => `${n(x + (dx * c - dy * si) * s)},${n(y + (dx * si + dy * c) * s)}`;
  return sm(`${p(0, -4)} ${p(-14, -20)}! ${p(-24, -12)} ${p(-26, 4)}! ${p(-14, 6)} ${p(0, 4)} ${p(14, 6)} ${p(26, 4)}! ${p(24, -12)} ${p(14, -20)}!`, 2);
}
const BOWS = [[176, 384, -60, 'yel', 1.1], [128, 432, -20, 'bowT', 1], [56, 422, 10, 'bowR', 1.05], [126, 466, 20, 'yel', 0.9]];

// ---------- silhouettes ----------
const S = {
  string: rib(STR) + rib(STR2),
  bows: BOWS.map(([x, y, a, , s]) => bow(x, y, a, s)).join(''),
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
  + oval(268, 176, 26, 22, '#2a0a06') + oval(268, 176, 23, 19, 'url(#g-eye)') + oval(278, 180, 7, 11, '#1a0806') + dot(262, 172, 4, '#fff')
  + oval(358, 178, 22, 19, '#2a0a06') + oval(358, 178, 19.5, 16.5, 'url(#g-eye)') + oval(350, 182, 6, 10, '#1a0806') + dot(352, 174, 3.4, '#fff')
  // les paupières lourdes, penchées vers le milieu : elles coupent le haut des yeux (regard furieux)
  + shape('M238 152 L304 152 L304 180 C290 164 262 160 240 168 Z', RED.base) + line('M240 168 C262 160 290 164 304 180', '#2a0a06', 4)
  + shape('M326 156 L384 156 L384 170 C364 164 340 166 324 182 Z', TEAL.base) + line('M324 182 C340 166 364 164 384 170', '#2a0a06', 4)
  + `<g class="a-blink" opacity="0">${oval(268, 172, 25, 21, RED.base)}${oval(358, 174, 21, 18, TEAL.base)}</g>`
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
  { id: 'string', cls: 'a-tail', d: S.string, body: use('string', STRING) + clip('string', glint(STR.map(([x, y], i) => [x + 1, y - 1.4, i === 0 || i === STR.length - 1 ? 0 : 1.6]), '#a87a5a', 0.8)) },
  { id: 'bows', cls: 'a-tail', d: S.bows, body: BOWS.map(([x, y, a, g, s]) => shape(bow(x, y, a, s), `url(#g-${g})`) + dot(x, y, 4.4 * s, g === 'yel' ? YEL.shade : g === 'bowT' ? TEAL.shade : RED.shade)).join('') },
  { id: 'rag', cls: 'a-kite', d: S.rag, body: use('rag', '#4a3a3a') + clip('rag', glint([[178, 250, 0], [184, 270, 2], [190, 290, 0]], '#8a7a78', 0.7)) },
  { id: 'kite', cls: 'a-kite', d: S.kite, shadow: [sh(['string', 'bows', 'rag'], -4, 6, SH.teal, 0.45)], body: kiteBody },
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
  const s = figure({ w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'epouvantails-3', w: W, h: H, pad: PAD, foot: [220, 474], svg };
