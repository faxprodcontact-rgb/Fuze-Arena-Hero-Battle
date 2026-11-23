// Nimue (mages-9), héroïne au nom provisoire : redessinée par le code d'après le dessin d'origine, dans le même cadre
// (527 × 524, mêmes proportions, même pose). Le dessin d'origine montre un dieu de l'orage trapu : grande crinière et
// barbe dorées, couronne de laurier d'or, gros sourcils froncés, yeux ambre, bouche ouverte qui crie ; toge blanche
// aux plis lavande, ceinture et ourlet d'or, cape violette ; le poing droit pend devant lui (bracelet d'or), le poing
// gauche est levé et lance un éclair doré ; sandales lacées.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. Contour décalqué sur l'original
// (outils/contour.py) ; la lueur de l'éclair n'a pas de contour.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 527, H = 524, PAD = 46;

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
const SKIN = { hi: '#fff0dc', lite: '#ffdcb4', base: '#fbc89a', shade: '#e8a07a', deep: '#c8745a', line: '#9a4e3e' };
const GOLD = { hi: '#fff6c8', lite: '#ffe07a', base: '#f6c040', mid: '#dc9a22', shade: '#a8681a', deep: '#6e400e' };
const HAIR = { hi: '#fff4b0', lite: '#ffdc6a', base: '#f2bc3e', shade: '#c8862a', deep: '#8a5418' };
const TOGA = { hi: '#ffffff', base: '#f2f0f8', shade: '#c4bedc', deep: '#9a92bc' };
const CAPE = { lite: '#8a6ae0', base: '#5a3ab0', shade: '#3a2482', deep: '#241654' };
const SH = { skin: '#6a2a1a', hair: '#4a2a08', toga: '#4a3e6e', cape: '#120a2a' };

// ---------- dégradés ----------
const defs = [
  lin('g-cape', 0, 280, 0, 500, [[0, CAPE.lite], [0.4, CAPE.base], [1, CAPE.shade]]),
  lin('g-hair', 300, 80, 120, 300, [[0, HAIR.lite], [0.5, HAIR.base], [1, HAIR.shade]]),
  lin('g-skin', 0, 130, 0, 260, [[0, SKIN.hi], [0.5, SKIN.lite], [1, SKIN.base]]),
  lin('g-skinB', 0, 0, 0, 1, [[0, SKIN.lite], [0.55, SKIN.base], [1, SKIN.shade]], false),
  lin('g-toga', 330, 280, 160, 470, [[0, TOGA.hi], [0.5, TOGA.base], [1, TOGA.shade]]),
  lin('g-gold', 0, 0, 0, 1, [[0, GOLD.hi], [0.4, GOLD.base], [1, GOLD.shade]], false),
  lin('g-goldX', 0, 0, 1, 0, [[0, GOLD.shade], [0.45, GOLD.base], [0.8, GOLD.hi], [1, GOLD.mid]], false),
  lin('g-leaf', 0, 0, 1, 0, [[0, GOLD.mid], [0.5, GOLD.lite], [1, GOLD.hi]], false),
  rad('g-iris', 0.55, 0.7, 0.8, [[0, '#fff0c0'], [0.3, '#f0b030'], [0.7, '#a86010'], [1, '#4a2408']], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#5a2a10', 0.7], [0.5, '#5a2a10', 0]], false),
  rad('g-blush', 0.5, 0.5, 0.5, [[0, '#ff8070', 0.5], [1, '#ff8070', 0]], false),
  lin('g-mouth', 0, 248, 0, 286, [[0, '#3a0a0a'], [0.6, '#6a1a1a'], [1, '#a83a3a']]),
  // en travers de la lame d'énergie : très claire au milieu, elle s'efface vers les bords
  rad('g-aura', 0.5, 0.5, 0.5, [[0, '#ffffff', 0.95], [0.45, '#fff2a8', 0.78], [0.75, '#ffdc60', 0.38], [1, '#ffd040', 0]], false),
  rad('g-glow', 0.5, 0.5, 0.5, [[0, '#fffbe0', 0.9], [0.42, '#ffe070', 0.45], [1, '#ffc830', 0]], false),
  lin('g-bolt', 0, 0, 1, 1, [[0, '#ffffff'], [0.5, '#fff4a0'], [1, '#ffc830']], false),
].join('');

// ---------- silhouettes (le bord extérieur suit le contour mesuré sur l'original) ----------
const S = {
  // la cape : derrière, elle descend des épaules jusqu'au sol à gauche, et dépasse à droite derrière la toge
  cape: sm('72,290 54,313 47,329 47,344 50,363 25,399 12,428 7,458 14,479 39,489! 80,470 120,450 180,440 260,440 330,452 345,449 350,440 351,433 361,427 379,425 388,430 396,439! 397,430 394,416 384,398 370,386 350,378 335,375 321,368 300,330 200,300'),
  // la crinière, derrière la tête
  mane: sm('117,110 150,100 200,96 250,96 296,100 304,120 300,140 307,164 310,186 311,202 318,215 316,240 310,268 296,292 240,318 180,312 120,300 72,290 61,276 61,258 73,237 93,228 102,217 102,203 107,197 106,183 110,164 120,143 123,129'),
  // les jambes et les sandales
  legL: sm('86,440 150,440 152,470 149,484 138,484 135,487 135,494 144,504 146,512! 130,512 104,516 54,514! 50,512 57,500 57,494 54,491 60,470 76,452'),
  legR: sm('270,440 330,446 327,462 327,478 355,495 362,497 366,506 366,512! 321,514 307,512 271,512! 270,504 275,494 275,488 268,470'),
  // la toge : du torse à l'ourlet, la ceinture d'or
  toga: sm('140,290 200,300 270,300 318,292 320,330 324,360 318,400 326,440 310,458 270,470 230,470 200,472 160,470 150,460 140,430 142,380 132,330'),
  belt: sm('150,374 220,378 290,376 300,372 302,390 290,394 220,396 150,392'),
  // le bras droit (à gauche de l'image) qui pend devant : l'épaule, l'avant-bras, le bracelet d'or, le poing
  armR: sm('72,290 100,280 128,286 140,304 138,330 150,344 160,362 150,376 124,378 108,366 92,346 72,322 62,300'),
  cuffR: sm('100,348 148,336 162,364 152,378 114,384 100,370'),
  fistR: sm('100,376 122,372 148,374 158,388 156,412 146,424 126,428 106,422 96,406 96,388'),
  // le bras gauche, levé : l'épaule (sous la crinière), l'avant-bras, le bracelet, le poing serré
  armL: sm('300,268 330,258 344,268 360,248 380,240 396,256 384,276 372,288 344,310 320,330 304,320 296,296'),
  cuffL: sm('344,244 376,232 392,250 386,270 360,278 346,264'),
  fistL: sm('352,206 362,186 384,176 408,178 422,190 424,210 418,228 400,240 380,244 362,238 350,224'),
  // la barbe, qui tombe sur la poitrine
  beard: sm('152,212 164,226 180,236 198,240 216,236 236,234 256,236 276,232 292,226 302,214 308,232 306,256 298,276 286,292 272,302! 266,316! 252,310 244,326! 234,312 222,318! 216,304 202,304! 196,290 182,288! 178,272 164,266! 162,250 150,238'),
  // la bouche ouverte, dans la barbe
  mouthO: sm('216,262 228,254 244,252 260,254 270,260 268,276 258,290 244,296 230,292 220,280'),
  // l'oreille, à gauche du visage
  ear: sm('110,206 120,198 134,202 140,220 136,242 124,250 112,242 106,226'),
  // le visage
  face: sm('150,150 180,136 230,130 280,134 306,152 312,184 306,220 294,246 270,262 240,268 212,262 188,248 166,226 152,198 148,172'),
  // la moustache, au-dessus de la bouche
  stache: sm('194,256 204,244 222,238 242,242 262,238 282,242 296,254 292,266! 280,256 262,251 242,253 222,251 206,256 198,268!'),
  // la couronne de laurier : un bandeau de feuilles d'or et ses grandes pointes
  crown: sm('124,138 120,120 117,93! 133,102 140,110 146,110 152,101 160,100 164,96 164,74 169,60! 183,73 193,92 199,92 202,89 204,91 216,91 219,88 222,72 229,58! 237,70 243,89 246,92 252,92 261,78 265,64! 269,75 272,96 278,104 284,104 296,92 304,87! 303,108 301,116 296,130 296,140 260,132 220,128 180,132 140,146'),
  // le front sous la couronne : une mèche qui descend au milieu
  forelock: sm('204,128 222,124 242,128 236,150 228,166! 222,146 210,140'),
};

// ---------- le visage ----------
function eye(key, white, cx, cy, r, lash, lower, shut, hl) {
  return `<clipPath id="c-${key}"><path d="${white}"/></clipPath><path d="${white}" fill="#fffdf8"/>`
    + `<g clip-path="url(#c-${key})">`
    + dot(cx, cy, r, 'url(#g-iris)') + `<circle cx="${cx}" cy="${cy}" r="${n(r - 0.8)}" fill="none" stroke="#4a2408" stroke-width="1.6"/>`
    + dot(n(cx - r * 0.05), n(cy - r * 0.08), n(r * 0.46), '#1a0a04')
    + `<rect x="${cx - r - 16}" y="${cy - r - 6}" width="${2 * r + 32}" height="${n(r * 1.25)}" fill="url(#g-lid)"/>`
    + dot(n(cx + hl[0] * r), n(cy + hl[1] * r), n(r * 0.26), '#fff') + dot(n(cx + hl[2] * r), n(cy + hl[3] * r), n(r * 0.13), '#fff', 0.95)
    + '</g>' + line(lower, SKIN.line, 1.6, 0.85) + shape(lash, '#2a1408')
    + `<g class="a-blink" opacity="0"><path d="${white}" fill="${SKIN.lite}" stroke="${SKIN.lite}" stroke-width="3"/>${line(shut, '#2a1408', 3)}</g>`;
}
const EYE_L = 'M176 204 C186 194 206 192 222 197 C231 201 233 210 231 219 C224 230 208 234 194 231 C182 228 175 216 176 204 Z';
const EYE_R = 'M244 205 C252 196 272 194 286 200 C291 209 289 221 280 227 C269 232 254 230 247 221 C243 216 243 210 244 205 Z';
const faceBody = use('face', 'url(#g-skin)') + clip('face',
  // l'ombre de la couronne sur le front, le côté gauche et le bas du visage dans l'ombre, la lumière sur la joue droite
  glint([[148, 150, 8], [200, 140, 10], [260, 140, 10], [308, 156, 8]], SKIN.shade, 0.5)
  + shape(sm('146,170 160,206 180,236 210,256 196,270 146,270'), SKIN.base, 0.8)
  + oval(286, 176, 12, 18, SKIN.hi, 0.6, 10)
  + oval(178, 236, 13, 8, 'url(#g-blush)') + oval(290, 236, 9, 6, 'url(#g-blush)', 0.8)
  + eye('eL', EYE_L, 206, 214, 13, 'M174 206 C186 192 208 190 224 196 C232 200 235 207 234 214 L228 212 C224 204 214 200 202 200 C190 200 182 204 178 210 Z',
    'M188 228 C198 233 214 233 226 226', 'M178 210 C196 222 216 222 230 214', [-0.36, -0.36, 0.42, 0.32])
  + eye('eR', EYE_R, 265, 213, 11.5, 'M242 208 C252 196 272 193 288 199 L287 204 C274 200 258 201 250 212 Z',
    'M252 224 C262 228 274 228 282 222', 'M246 212 C260 222 276 222 286 210', [-0.34, -0.36, 0.4, 0.34])
  // les paupières du haut, lourdes et penchées vers le nez (elles coupent le haut de l'œil) : le regard en colère
  + shape('M168 184 L242 184 L242 212 L236 212 C218 201 196 197 174 203 Z', SKIN.lite)
  + shape('M240 184 L298 184 L296 199 C278 196 258 200 244 212 L238 212 Z', SKIN.lite)
  + line('M172 204 C194 196 218 200 237 212', '#2a1408', 4.2) + line('M242 213 C258 201 278 196 297 199', '#2a1408', 4.2)
  // les sourcils : deux grosses mèches dorées très froncées (le bout près du nez bien plus bas), ombrées dessous
  + shape(sm('160,178 174,168 200,172 224,186 236,202 226,206 206,196 184,188 166,190'), SH.hair, 0.35).replace('<path', '<path transform="translate(-1 3)"')
  + shape(sm('160,178 174,168 200,172 224,186 236,202 226,206 206,196 184,188 166,190'), HAIR.shade)
  + shape(sm('166,175 176,171 198,174 214,180 198,178 178,176'), HAIR.lite, 0.85)
  + shape(sm('242,204 252,190 274,180 296,180 300,190 290,192 270,194 252,206'), SH.hair, 0.35).replace('<path', '<path transform="translate(-1 3)"')
  + shape(sm('242,204 252,190 274,180 296,180 300,190 290,192 270,194 252,206'), HAIR.shade)
  + shape(sm('262,186 276,182 294,182 290,185 276,185'), HAIR.lite, 0.85)
);

// ---------- l'éclair (sans contour : il brille) ----------
// la grande lame d'énergie qui sort du poing (mesurée sur l'original : du poing (400,190) à la pointe (512,12), large
// d'environ 120 px avec sa lueur) : une lueur ovale allongée qui s'efface vers les bords, et un cœur plus clair
const auraBody = `<g class="a-glow"><ellipse cx="452" cy="104" rx="132" ry="62" transform="rotate(-57.8 452 104)" fill="url(#g-aura)"/>`
  + shape(rib([[396, 190, 0], [418, 152, 36], [446, 108, 50], [476, 62, 44], [500, 28, 26], [514, 10, 0]]), '#fff6c8', 0.8)
  + shape(rib([[400, 184, 0], [422, 148, 22], [450, 104, 30], [480, 58, 24], [508, 18, 0]]), '#fffdf0', 0.92)
  + shape(rib([[404, 176, 0], [430, 136, 10], [462, 86, 12], [500, 28, 0]]), '#ffffff', 0.95) + '</g>';
const BOLT = 'M396 182 L428 136 L418 134 L458 86 L446 86 L500 30 L466 98 L478 98 L440 144 L450 146 L410 188 Z';
const boltBody = `<g class="a-bolt">${shape(BOLT, 'url(#g-bolt)', 0.95)}${shape('M404 178 L432 140 L424 139 L460 94 L452 94 L490 46 L462 102 L470 102 L438 144 L444 146 Z', '#ffffff', 0.9)}</g>`
  + [[504, 40, 0], [492, 100, 1], [420, 120, 2]].map(([x, y, i]) => `<g class="a-spark${i + 1}">${shape(`M${x} ${y - 7}L${x + 2} ${y - 2}L${x + 7} ${y}L${x + 2} ${y + 2}L${x} ${y + 7}L${x - 2} ${y + 2}L${x - 7} ${y}L${x - 2} ${y - 2}Z`, '#fffbe0')}</g>`).join('');

/** Une feuille de laurier posée sur le bandeau, penchée de `a` degrés ; `half` = sa moitié à l'ombre. */
function leafPt(x, y, a, half = false) {
  const r = (a * Math.PI) / 180, ux = Math.sin(r), uy = -Math.cos(r), nx = -uy, ny = ux, L = 22, w = 8;
  const tip = [x + ux * L, y + uy * L], base = [x - ux * 4, y - uy * 4];
  const side = (s) => [x + ux * L * 0.4 + nx * w * s, y + uy * L * 0.4 + ny * w * s];
  const [a1, a2] = [side(1), side(-1)];
  return half ? `M${n(base[0])} ${n(base[1])}Q${n(a1[0])} ${n(a1[1])} ${n(tip[0])} ${n(tip[1])}Z`
    : `M${n(base[0])} ${n(base[1])}Q${n(a1[0])} ${n(a1[1])} ${n(tip[0])} ${n(tip[1])}Q${n(a2[0])} ${n(a2[1])} ${n(base[0])} ${n(base[1])}Z`;
}

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'cape', cls: 'a-cape', d: S.cape, body: use('cape', 'url(#g-cape)') + clip('cape',
    // l'intérieur de la cape, plus clair, qui se retourne ; de grands plis en fuseaux
    shape(sm('7,458 30,420 60,390 90,380 110,400 100,440 80,470 39,489 14,479'), CAPE.lite, 0.55)
    + glint([[70, 310, 0], [50, 380, 5], [30, 440, 6], [20, 470, 0]], CAPE.deep, 0.5)
    + glint([[100, 330, 0], [90, 400, 5], [70, 460, 0]], CAPE.lite, 0.4)
    + glint([[350, 384, 0], [372, 404, 4], [390, 428, 0]], CAPE.lite, 0.6)) },
  { id: 'mane', cls: 'a-head', d: S.mane, shadow: [sh(['cape'], -4, 5, SH.cape, 0.5)], body: use('mane', 'url(#g-hair)') + clip('mane',
    // de grandes mèches dorées : un creux plus sombre entre elles, la mèche éclairée en haut à droite
    [[130, 160, 92, 230], [126, 200, 80, 266], [150, 240, 120, 296], [330, 150, 344, 186], [320, 210, 312, 250], [300, 250, 290, 290]].map(([x0, y0, x1, y1]) =>
      glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 6], [x1, y1, 0]], HAIR.shade, 0.55)).join('')
    + [[140, 150, 108, 210], [338, 140, 354, 170], [116, 220, 84, 250]].map(([x0, y0, x1, y1]) =>
      glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 4], [x1, y1, 0]], HAIR.hi, 0.65)).join('')) },
  { id: 'legL', d: S.legL, shadow: [sh(['cape'], -4, 4, SH.cape, 0.45)], body: use('legL', 'url(#g-skinB)') + clip('legL',
    // le mollet ; les lanières d'or de la sandale en croix ; la semelle
    shape(sm('86,440 150,440 152,470 138,476 96,474'), SKIN.shade, 0.5)
    + glint([[84, 462, 3], [116, 472, 4], [150, 464, 3]], GOLD.base, 0.95) + glint([[80, 482, 3], [112, 490, 4], [140, 486, 3]], GOLD.base, 0.95)
    + glint([[92, 456, 3], [112, 470, 3.4], [132, 488, 3]], GOLD.mid, 0.9)
    + shape(sm('50,504 146,506 146,518 50,518'), GOLD.shade)) },
  { id: 'legR', d: S.legR, shadow: [sh(['cape'], -4, 4, SH.cape, 0.45)], body: use('legR', 'url(#g-skinB)') + clip('legR',
    shape(sm('270,440 300,444 296,474 274,476'), SKIN.shade, 0.5)
    + glint([[268, 464, 3], [300, 472, 4], [330, 466, 3]], GOLD.base, 0.95) + glint([[274, 484, 3], [320, 492, 4], [356, 498, 3]], GOLD.base, 0.95)
    + glint([[280, 458, 3], [300, 474, 3.4], [318, 490, 3]], GOLD.mid, 0.9)
    + shape(sm('268,506 368,506 368,518 268,518'), GOLD.shade)) },
  { id: 'toga', d: S.toga, shadow: [sh(['cape', 'mane', 'legL', 'legR'], -4, 5, SH.toga, 0.4)], body: use('toga', 'url(#g-toga)') + clip('toga',
    // de grands plis lavande (un creux sombre, une arête claire), l'ourlet d'or en biais, le bas à l'ombre
    [[200, 300, 186, 370], [250, 310, 236, 366], [180, 400, 170, 456], [226, 400, 224, 462], [272, 400, 286, 454]].map(([x0, y0, x1, y1]) =>
      glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 6], [x1, y1, 2]], TOGA.shade, 0.75)
      + glint([[x0 + 5, y0, 0], [(x0 + x1) / 2 + 5, (y0 + y1) / 2, 3], [x1 + 5, y1, 1]], TOGA.hi, 0.9)).join('')
    + glint([[150, 450, 6], [230, 462, 7], [320, 440, 6]], GOLD.base, 0.95) + glint([[152, 447, 0], [230, 459, 2], [318, 437, 0]], GOLD.hi, 0.9)
    + shape(sm('140,430 200,460 260,462 320,440 320,480 140,480'), TOGA.shade, 0.5)
    + shape(sm('132,296 160,290 200,302 250,330 290,360 300,376 270,376 230,350 190,326 150,314'), TOGA.hi, 0.9)
    + glint([[140, 306, 0], [200, 318, 4], [270, 360, 0]], TOGA.shade, 0.7)) },
  { id: 'belt', d: S.belt, shadow: [sh(['toga'], -2, 4, SH.toga, 0.45)], body: use('belt', 'url(#g-gold)') + clip('belt',
    glint([[152, 377, 0], [220, 381, 2], [298, 376, 0]], GOLD.hi, 0.9) + shape(sm('214,376 232,376 234,396 214,396'), GOLD.mid)) },
  { id: 'aura', cls: 'a-fire', d: 'M-900 -900', body: auraBody },
  { id: 'armL', cls: 'a-armL', d: S.armL, shadow: [sh(['toga', 'mane', 'cape'], -4, 5, SH.skin, 0.4)], body: use('armL', 'url(#g-skinB)') + clip('armL',
    glint([[306, 300, 0], [340, 290, 4], [376, 260, 0]], SKIN.hi, 0.6) + glint([[310, 322, 0], [344, 306, 4], [378, 282, 0]], SKIN.deep, 0.5)) },
  { id: 'cuffL', cls: 'a-armL', d: S.cuffL, shadow: [sh(['armL'], -2, 4, SH.skin, 0.45)], body: use('cuffL', 'url(#g-goldX)') + clip('cuffL',
    glint([[348, 252, 0], [364, 242, 2.4], [386, 244, 0]], GOLD.hi, 0.9) + glint([[350, 266, 0], [368, 262, 2.4], [384, 264, 0]], GOLD.shade, 0.7)) },
  { id: 'fistL', cls: 'a-armL', d: S.fistL, shadow: [sh(['cuffL', 'armL', 'mane'], -3, 5, SH.skin, 0.45)], body: use('fistL', 'url(#g-skinB)') + clip('fistL',
    // le poing serré vu de face : quatre doigts repliés (creux et bosses), le pouce par-dessus
    [[364, 196, 366, 230], [378, 190, 380, 232], [394, 190, 394, 232]].map(([x1, y1, x2, y2]) => glint([[x1, y1, 0], [(x1 + x2) / 2, (y1 + y2) / 2, 2.6], [x2, y2, 0]], SKIN.deep, 0.65)).join('')
    + shape(sm('356,214 380,208 406,212 414,222 396,226 372,226'), SKIN.hi, 0.6) + oval(400, 186, 8, 4, SKIN.hi, 0.8, -12)) },
  { id: 'ear', cls: 'a-head', d: S.ear, shadow: [sh(['mane'], -3, 4, SH.hair, 0.4)], body: use('ear', 'url(#g-skinB)') + clip('ear',
    shape(sm('116,212 126,208 132,224 128,240 120,236 122,222'), SKIN.deep, 0.6) + oval(124, 206, 4, 3, SKIN.hi, 0.8)) },
  { id: 'face', cls: 'a-head', d: S.face, shadow: [sh(['mane'], -4, 4, SH.skin, 0.35)], body: faceBody },
  { id: 'beard', cls: 'a-head', d: S.beard, shadow: [sh(['toga'], -4, 6, SH.hair, 0.45), sh(['face'], -3, 4, SH.skin, 0.3)], body: use('beard', 'url(#g-hair)') + clip('beard',
    // de grosses mèches bouclées qui descendent en pointe : un creux doré sombre, une arête claire (plus claire à droite)
    [[[156, 214], [166, 238], [162, 262], [170, 282]], [[176, 238], [186, 258], [184, 280], [194, 298]], [[204, 262], [208, 282], [204, 300], [212, 312]],
      [[230, 284], [234, 300], [232, 318]], [[258, 280], [262, 296], [256, 312]], [[282, 258], [286, 276], [278, 294]], [[300, 214], [304, 236], [298, 262]]]
      .map((h, i) => glint(h.map(([x, y], k) => [x, y, k === 0 || k === h.length - 1 ? 0 : 4.4]), HAIR.shade, 0.75)
        + glint(h.map(([x, y], k) => [x + 5, y - 2, k === 0 || k === h.length - 1 ? 0 : 2.2]), i > 4 ? '#fff4c0' : HAIR.lite, 0.85)).join('')) },
  { id: 'mouthO', cls: 'a-head', d: S.mouthO, body: use('mouthO', 'url(#g-mouth)') + clip('mouthO',
    shape('M216 260 C230 253 252 252 270 258 L269 265 C252 260 232 260 217 266 Z', '#ffffff') + oval(244, 289, 13, 6, '#e86a6a', 0.9)) },
  { id: 'stache', cls: 'a-head', d: S.stache, shadow: [sh(['face'], -2, 4, SH.skin, 0.45)], body: use('stache', 'url(#g-hair)') + clip('stache',
    glint([[210, 246, 0], [230, 242, 2.4], [246, 246, 0]], HAIR.hi, 0.8) + glint([[250, 244, 0], [266, 241, 2.4], [284, 249, 0]], HAIR.hi, 0.8)) },
  { id: 'nose', cls: 'a-head', d: sm('228,234 238,226 252,228 258,238 254,248 242,252 230,248 225,241'), shadow: [sh(['beard', 'stache', 'face'], -2, 4, SH.skin, 0.4)],
    body: use('nose', '#f8b49a') + clip('nose', oval(236, 246, 10, 5, SKIN.deep, 0.6) + oval(248, 233, 4, 2.6, '#fff4ec', 0.9)) },
  { id: 'forelock', cls: 'a-head', d: S.forelock, shadow: [sh(['face'], -2, 4, SH.skin, 0.4)], body: use('forelock', 'url(#g-hair)') },
  { id: 'crown', cls: 'a-head', d: S.crown, shadow: [sh(['face', 'mane', 'forelock'], -3, 6, SH.hair, 0.5)], body: use('crown', GOLD.mid) + clip('crown',
    // les feuilles de laurier : chacune une face claire et une face dorée plus sombre, le long du bandeau
    [[117, 93, 134, 132], [169, 60, 162, 112], [229, 58, 224, 108], [265, 64, 260, 112], [304, 87, 290, 124]].map(([tx, ty, bx, by]) =>
      shape(`M${bx - 10} ${by} L${tx} ${ty} L${bx + 10} ${by} Z`, 'url(#g-leaf)') + shape(`M${bx - 10} ${by} L${tx} ${ty} L${bx} ${by} Z`, GOLD.mid, 0.7)).join('')
    + [[132, 142], [150, 130], [170, 122], [192, 118], [214, 116], [238, 118], [260, 120], [280, 126], [298, 134]].map(([x, y], i) =>
      shape(leafPt(x, y, i % 2 ? -30 : 30), 'url(#g-leaf)') + shape(leafPt(x, y, i % 2 ? -30 : 30, true), GOLD.mid, 0.6)).join('')) },
  { id: 'armR', cls: 'a-armR', d: S.armR, shadow: [sh(['toga', 'cape', 'mane'], -4, 5, SH.skin, 0.4)], body: use('armR', 'url(#g-skinB)') + clip('armR',
    // le gros bras musclé : l'épaule ronde éclairée, le biceps, l'ombre dessous
    oval(110, 300, 22, 14, SKIN.hi, 0.6, -20) + glint([[70, 310, 0], [96, 336, 5], [120, 358, 0]], SKIN.deep, 0.5)
    + glint([[120, 300, 0], [132, 320, 3], [136, 340, 0]], SKIN.shade, 0.6)) },
  { id: 'cuffR', cls: 'a-armR', d: S.cuffR, shadow: [sh(['armR', 'toga'], -2, 4, SH.skin, 0.45)], body: use('cuffR', 'url(#g-goldX)') + clip('cuffR',
    glint([[104, 352, 0], [128, 342, 2.4], [156, 344, 0]], GOLD.hi, 0.9) + glint([[108, 372, 0], [132, 370, 2.4], [154, 372, 0]], GOLD.shade, 0.7)) },
  { id: 'fistR', cls: 'a-armR', d: S.fistR, shadow: [sh(['cuffR', 'toga', 'cape'], -3, 5, SH.skin, 0.45)], body: use('fistR', 'url(#g-skinB)') + clip('fistR',
    [[110, 392, 146, 392], [108, 404, 148, 406], [112, 416, 144, 418]].map(([x1, y1, x2, y2]) => glint([[x1, y1, 0], [(x1 + x2) / 2, (y1 + y2) / 2, 2.6], [x2, y2, 0]], SKIN.deep, 0.6)).join('')
    + oval(140, 384, 10, 5, SKIN.hi, 0.7, -10)) },
  { id: 'bolt', cls: 'a-fire', d: 'M-900 -900', body: boltBody },
];
// ---------- la vie au repos et l'attaque ----------
// Repos : il gronde. La tête (crinière, barbe, couronne) hoche, le poing levé crépite d'électricité (l'éclair et sa lueur
// palpitent, des étincelles jaillissent), la cape ondule, le poing du bas se serre, il cligne.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : il arme le poing levé en arrière (élan), puis l'abat vers l'avant ;
// l'éclair s'allonge et éclate, la cape se soulève ; tout revient à la pose de repos.
const PIV = { head: [236, 300], cape: [120, 300], armL: [318, 300], armR: [100, 300], fire: [398, 190] };
const IDLE = {
  'a-head': ['head', 'head 2.8s ease-in-out infinite alternate'],
  'a-cape': ['cape', 'cape 3.6s ease-in-out infinite alternate'],
  'a-armL': ['armL', 'armL 2.2s ease-in-out infinite alternate'],
  'a-armR': ['armR', 'armR 3s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-fire{transform-origin:${PIV.armL[0]}px ${PIV.armL[1]}px;animation:armL 2.2s ease-in-out infinite alternate}
.a-glow{transform-origin:440px 120px;animation:glow 1.1s ease-in-out infinite alternate}
.a-bolt{transform-origin:398px 186px;animation:bolt .5s steps(2) infinite}
.a-spark1,.a-spark2,.a-spark3{opacity:0}
.a-spark1{animation:spark 1.2s ease-out infinite}.a-spark2{animation:spark 1.5s ease-out -.5s infinite}.a-spark3{animation:spark 1.1s ease-out -.8s infinite}
.a-blink{animation:blink 4.4s linear infinite}
@keyframes head{from{transform:none}to{transform:translate(0,-2px) rotate(-1.2deg)}}
@keyframes cape{from{transform:none}to{transform:rotate(1.4deg)}}
@keyframes armL{from{transform:none}to{transform:rotate(-2deg)}}
@keyframes armR{from{transform:none}to{transform:rotate(1.6deg)}}
@keyframes glow{from{transform:scale(.9);opacity:.75}to{transform:scale(1.08);opacity:1}}
@keyframes bolt{0%{transform:none;opacity:1}50%{transform:scale(1.04,.96) skewX(-3deg);opacity:.85}100%{transform:none;opacity:1}}
@keyframes spark{0%{transform:scale(.4);opacity:0}25%{opacity:1}100%{transform:scale(1.3);opacity:0}}
@keyframes blink{0%,93%{opacity:0}94.5%,97%{opacity:1}98.5%,100%{opacity:0}}
${atk('a-armL', 'armL-atk')}${atk('a-head', 'head-atk')}${atk('a-cape', 'cape-atk')}${atk('a-armR', 'armR-atk')}
.atk .a-fire{animation:armL-atk .75s ease-in-out}
.atk .a-glow{animation:glow-atk .75s ease-in-out}
@keyframes armL-atk{0%{transform:none}32%{transform:rotate(-14deg)}50%{transform:rotate(16deg)}64%{transform:rotate(12deg)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}32%{transform:rotate(-2deg)}50%{transform:translate(3px,1px) rotate(2deg)}100%{transform:none}}
@keyframes cape-atk{0%{transform:none}32%{transform:rotate(2deg)}52%{transform:rotate(-3deg) scale(1.02,1)}100%{transform:none}}
@keyframes armR-atk{0%{transform:none}32%{transform:rotate(4deg)}52%{transform:rotate(-4deg)}100%{transform:none}}
@keyframes glow-atk{0%{transform:none}32%{transform:scale(.9)}50%{transform:scale(1.7)}64%{transform:scale(1.35)}100%{transform:none}}
`.replace(/\n/g, '');

module.exports = { id: 'mages-9', w: W, h: H, pad: PAD, foot: [210, 514],
  svg: (anime = true) => figure({ master: require('./silhouettes/mages-9.json'), w: W, h: H, pad: PAD, defs, style, parts, anime }) };
