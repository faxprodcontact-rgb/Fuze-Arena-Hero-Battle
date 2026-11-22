// Le renard de feuilles (ronciers-1), monstre des Ronciers : redessiné par le code d'après le dessin d'origine, dans le
// même cadre (442 × 337, mêmes proportions, même pose) : renard orange de profil tourné vers la droite, qui grogne ;
// grande queue en éventail de feuilles d'automne, manteau de feuilles rouges, orange et jaunes posées en tuiles sur le
// dos, deux oreilles pointues à l'intérieur sombre, œil jaune furieux sous un gros sourcil, museau à truffe noire,
// gueule ouverte à crocs, joues et poitrail crème en touffes, quatre pattes aux petites griffes claires.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 442, H = 337, PAD = 42;

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

// ---------- les feuilles ----------
/** Une feuille : de sa queue (rx, ry), étroite, jusqu'à sa pointe (tx, ty), large de w ; `lean` la rend plus ventrue d'un côté. */
function leafPts(rx, ry, tx, ty, w, lean = 0) {
  const L = Math.hypot(tx - rx, ty - ry), ux = (tx - rx) / L, uy = (ty - ry) / L, nx = -uy, ny = ux;
  const at = (f, s) => P(rx + ux * L * f + nx * w * s, ry + uy * L * f + ny * w * s);
  return [at(0, 0.14), at(0.32, 0.5 + lean), at(0.7, 0.38 + lean * 0.6), `${P(tx, ty)}!`, at(0.7, -0.38 + lean * 0.6), at(0.32, -0.5 + lean), at(0, -0.14)];
}
const leafD = (l) => sm(cw(leafPts(...l)));
/** La moitié de la feuille tournée vers le haut (éclairée), coupée le long de la nervure. */
function leafHalf(rx, ry, tx, ty, w, lean = 0) {
  const L = Math.hypot(tx - rx, ty - ry), ux = (tx - rx) / L, uy = (ty - ry) / L;
  let nx = -uy, ny = ux;
  if (ny > 0) { nx = -nx; ny = -ny; } // le côté du haut
  const at = (f, s) => P(rx + ux * L * f + nx * w * s, ry + uy * L * f + ny * w * s);
  return sm(`${at(0, 0)} ${at(0.5, 0.02)} ${P(tx, ty)}! ${at(0.7, 0.38 + lean * 0.6)} ${at(0.32, 0.5 + lean)} ${at(0, 0.14)}`);
}
/**
 * Des feuilles posées en tuiles : chacune son ombre douce sur celles d'avant, sa couleur, sa moitié du haut plus claire
 * (la nervure est la limite entre les deux moitiés : un côté sombre, un côté clair, jamais un trait).
 */
const LEAF = {
  Y: { base: '#f4ac36', lite: '#ffd66c', o: 0.75 },
  O: { base: '#ec8228', lite: '#ffae4c', o: 0.7 },
  R: { base: '#d4432a', lite: '#f27446', o: 0.75 },
};
function leaves(list, sh = '#6a2008', shO = 0.4) {
  return list.map(([rx, ry, tx, ty, w, lean, c]) => {
    const d = leafD([rx, ry, tx, ty, w, lean]);
    return `<path d="${d}" transform="translate(-3 4)" fill="${sh}" opacity="${shO}"/>` + shape(d, LEAF[c].base)
      + shape(leafHalf(rx, ry, tx, ty, w, lean), LEAF[c].lite, LEAF[c].o)
      + glint([[rx + (tx - rx) * 0.12, ry + (ty - ry) * 0.12, 0], [rx + (tx - rx) * 0.5, ry + (ty - ry) * 0.5 - 1, 2.2], [rx + (tx - rx) * 0.86, ry + (ty - ry) * 0.86, 0]], '#fff4c8', 0.35);
  }).join('');
}

// la queue : un grand éventail de feuilles qui partent de sa racine, du fond vers le devant
// [queue x, y, pointe x, y, largeur, penchant, couleur]
const TAIL = [
  [140, 196, 166, 112, 30, 0, 'O'], [140, 196, 150, 62, 36, 0.04, 'Y'], [140, 198, 40, 232, 44, -0.04, 'O'], [140, 196, 112, 22, 44, 0.04, 'Y'],
  [140, 198, 12, 162, 50, -0.03, 'O'], [140, 196, 58, 6, 50, 0.03, 'Y'], [140, 198, 8, 94, 54, 0, 'O'], [140, 196, 22, 38, 54, 0.02, 'Y'],
];
// le manteau de feuilles du dos : de l'arrière vers l'avant, et de bas en haut (la feuille du dessus recouvre celle du dessous)
const MANTLE = [
  [178, 214, 96, 226, 30, 0.05, 'O'], [176, 190, 100, 176, 34, 0, 'Y'], [182, 166, 118, 134, 30, 0, 'Y'],
  [222, 232, 150, 246, 30, 0.05, 'R'], [226, 206, 138, 206, 38, 0, 'R'], [230, 180, 148, 160, 36, 0, 'O'], [234, 154, 170, 122, 30, 0, 'Y'],
  [268, 236, 204, 246, 28, 0.05, 'O'], [272, 212, 186, 222, 36, 0, 'Y'], [276, 188, 196, 186, 38, 0, 'R'], [280, 162, 206, 148, 34, 0, 'O'], [286, 140, 228, 112, 30, 0, 'Y'],
  [300, 200, 238, 198, 30, 0, 'O'], [302, 174, 242, 162, 30, 0, 'R'],
];

// ---------- couleurs ----------
const FUR = { hi: '#ffe2a0', lite: '#ffc463', base: '#f59a30', mid: '#e07c1e', shade: '#b8561a', deep: '#7a3410' };
const CREAM = { hi: '#ffffff', base: '#fdf2e2', mid: '#f0dcc8', shade: '#d8c0c4', deep: '#a8909a' };
const SH = { fur: '#6a2408', cream: '#7a5a68', dark: '#24080a' };

// ---------- dégradés ----------
const defs = [
  lin('g-fur', 300, 120, 220, 290, [[0, FUR.lite], [0.4, FUR.base], [1, '#cc6a1e']]),
  lin('g-head', 390, 100, 270, 210, [[0, '#ffcf72'], [0.45, '#f8a43a'], [1, '#d87424']]),
  lin('g-far', 0, 0, 0, 1, [[0, '#d27428'], [1, '#9a4614']], false),
  lin('g-leg', 0, 0, 1, 0, [[0, '#c4601c'], [0.55, FUR.base], [1, FUR.lite]], false),
  lin('g-cream', 0, 0, 0, 1, [[0, CREAM.hi], [0.55, CREAM.base], [1, CREAM.shade]], false),
  rad('g-tail', 140, 196, 178, [[0, '#a83a16'], [0.3, '#dc6a28'], [0.62, '#f29c38'], [1, '#ffd468']]),
  lin('g-ear', 0, 0, 1, 0, [[0, '#d46a20'], [0.6, FUR.base], [1, FUR.lite]], false),
  lin('g-earIn', 0, 0, 0, 1, [[0, '#5a1814'], [0.7, '#8a2a24'], [1, '#b8504a']], false),
  rad('g-sclera', 0.6, 0.35, 0.8, [[0, '#ffffff'], [0.7, '#fbf6f2'], [1, '#e2d4d4']], false),
  rad('g-iris', 0.62, 0.38, 0.75, [[0, '#fffbd8'], [0.35, '#f8e46a'], [0.75, '#e2b02c'], [1, '#a8661a']], false),
  rad('g-pupil', 0.5, 0.8, 0.7, [[0, '#5a2a10'], [0.6, '#24100a'], [1, '#120608']], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#3a1408', 0.75], [0.5, '#3a1408', 0]], false),
  lin('g-eyelid', 0, 0, 0, 1, [[0, FUR.lite], [0.6, FUR.base], [1, FUR.mid]], false),
  lin('g-mouth', 0, 172, 0, 218, [[0, '#24060c'], [0.55, '#4e1018'], [1, '#7e2430']]),
  rad('g-nose', 0.62, 0.3, 0.8, [[0, '#6a5a66'], [0.4, '#2e2230'], [1, '#140c14']], false),
].join('');

// ---------- silhouettes ----------
const S = {
  // les pattes du fond (plus sombres) : la patte arrière gauche, la patte avant droite qui s'avance
  legBF: sm('96,236 120,232 130,256 126,282 126,300 133,312 134,328! 112,331! 92,330! 88,321 94,308 98,286 96,262'),
  legFF: sm('284,226 312,230 328,252 342,276 354,290 370,298 378,308 377,318 369,323! 346,322! 328,321 320,314 324,302 314,284 298,262 286,244'),
  // la queue : la réunion de ses feuilles
  tail: TAIL.map((l) => leafD(l)).join(''),
  // le corps : le dos (caché sous le manteau), le ventre crème entre les pattes
  body: sm('104,200 130,180 170,170 220,166 262,160 300,170 318,196 312,226 296,248 270,260 236,266 196,268 160,266 132,258 112,242 102,222'),
  // les pattes de devant (plus claires) : la patte arrière droite (grosse cuisse), la patte avant gauche
  legBN: sm('110,234 126,216 160,212 188,224 196,246 190,266 182,286 184,300 196,309 205,318 203,329! 180,332! 156,331! 146,325 148,313 154,302 150,284 140,272 122,264 110,252'),
  legFN: sm('226,234 260,234 268,256 262,280 262,297 276,305 291,315 295,325 289,332! 266,333! 246,332! 238,325 240,312 238,290 232,264'),
  // le manteau de feuilles
  mantle: MANTLE.map((l) => leafD(l)).join(''),
  // le poitrail crème, en touffes qui pendent vers l'arrière
  chest: sm('262,150 292,160 318,176 334,196 338,214 332,228! 326,222 324,240! 314,232 306,248! 296,236 284,246! 276,232 262,236! 258,222 250,214 248,190 250,168'),
  // les oreilles, derrière la tête
  earF: sm('252,120 245,86 241,56 243,34! 260,50 280,74 298,98 292,120'),
  earN: sm('312,108 313,74 317,46 322,28! 336,44 352,68 368,96 354,112'),
  // la gueule (l'intérieur, derrière la mâchoire et la tête)
  mouth: sm('356,170 430,171 432,184 420,198 404,212 384,220 364,218 350,206 348,186'),
  // la mâchoire du bas, ouverte
  jaw: sm('344,190 360,198 376,202 394,204 408,204 415,208! 413,215 402,221 386,224 366,222 350,214 340,204'),
  // la tête : le crâne, le museau jusqu'à la truffe, la lèvre du haut, la joue qui finit en touffes vers l'arrière
  head: sm('250,128 258,112 276,102 300,98 326,100 350,106 368,116 378,126 398,138 420,150 432,155 440,160 443,167 437,174 426,176 408,177 388,176 370,174 360,176 354,186 352,196 '
    + '346,205! 338,200 332,215! 324,206 312,222! 304,210 290,220! 284,204 270,207! 268,192 256,191! 258,178 246,169! 250,156 242,146! 248,138'),
};

// ---------- le visage ----------
/** Une dent pointue : la moitié du fond dans l'ombre, un filet de lumière sur l'autre flanc. b1, b2 = la racine, t = la pointe. */
function tooth([x1, y1], [x2, y2], [tx, ty]) {
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  const d = `M${x1} ${y1}Q${n((x1 + tx) / 2 - (ty - y1) * 0.08)} ${n((y1 + ty) / 2)} ${tx} ${ty}Q${n((x2 + tx) / 2 + (ty - y2) * 0.08)} ${n((y2 + ty) / 2)} ${x2} ${y2}Z`;
  const half = `M${x1} ${y1}L${tx} ${ty}L${n(mx)} ${n(my)}Z`;
  return shape(d, '#fbf4e8') + shape(half, '#d8c8bc', 0.8) + line(`M${n(mx + (x2 - mx) * 0.5)} ${n(my + (y2 - my) * 0.5)}L${n(tx + (x2 - tx) * 0.2)} ${n(ty + (y2 - ty) * 0.2)}`, '#ffffff', 1.2, 0.9);
}
const TEETH_T = [[[367, 174], [377, 175], [374, 193]], [[381, 176], [389, 176], [386, 185]], [[395, 176], [406, 177], [403, 194]], [[410, 176], [418, 176], [415, 185]]];
const TEETH_B = [[[355, 198], [364, 200], [360, 189]], [[383, 203], [393, 204], [389, 192]], [[407, 205], [413, 206], [411, 197]]];

/**
 * L'œil : l'anneau sombre, le blanc, l'iris jaune en dégradé, la pupille, l'ombre de la paupière, deux reflets ;
 * puis le gros sourcil froncé par-dessus, qui coupe le haut de l'iris (regard furieux). Le clignement : une paupière de fourrure.
 */
const EYE = { cx: 349, cy: 146, rx: 19, ry: 16, ix: 354, iy: 149, ir: 10.5, pr: 5.2 };
function eye() {
  const { cx, cy, rx, ry, ix, iy, ir, pr } = EYE;
  const white = `M${cx - rx} ${cy}a${rx} ${ry} 0 1 0 ${2 * rx} 0a${rx} ${ry} 0 1 0 ${-2 * rx} 0Z`;
  const brow = 'M314 127 C332 115 360 119 386 135 C388 140 385 146 380 146 C358 137 338 134 321 139 C314 137 311 131 314 127 Z';
  return oval(cx, cy + 0.4, rx + 2.6, ry + 2.6, '#2a1430')
    + `<clipPath id="c-eye"><path d="${white}"/></clipPath><path d="${white}" fill="url(#g-sclera)"/>`
    + `<g clip-path="url(#c-eye)">`
    + dot(ix, iy, ir, 'url(#g-iris)') + dot(ix + 1.4, iy + 0.6, pr, 'url(#g-pupil)')
    + `<rect x="${cx - rx - 3}" y="${cy - ry - 3}" width="${2 * rx + 6}" height="${n(ry * 1.3)}" fill="url(#g-lid)"/>`
    + dot(n(ix - ir * 0.36), n(iy - ir * 0.34), n(ir * 0.26), '#fff') + dot(n(ix + ir * 0.5), n(iy + ir * 0.4), n(ir * 0.12), '#fff', 0.9)
    + '</g>'
    + `<g class="a-blink" opacity="0"><path d="${white}" fill="url(#g-eyelid)" stroke="#2a1430" stroke-width="2.6"/>${line(`M${cx - rx + 2} ${cy + 3} Q${cx} ${cy + 9} ${cx + rx - 1} ${cy + 2}`, '#2a1430', 2.6)}</g>`
    // le sourcil : son ombre portée sur l'œil, le sourcil sombre, son arête éclairée
    + `<path d="${brow}" transform="translate(-2 3)" fill="${SH.dark}" opacity="0.45"/>` + shape(brow, '#5a2010')
    + glint([[318, 125, 0], [340, 119, 2.6], [366, 124, 2.4], [384, 135, 0]], '#c8662a', 0.9);
}

const headBody = use('head', 'url(#g-head)') + clip('head',
  // le bas de la tête, crème : la joue, la lèvre du haut, le dessous du museau
  shape(sm('230,170 262,160 296,166 330,170 352,166 372,162 396,160 420,163 446,166 446,240 230,240'), 'url(#g-cream)')
  // l'ombre propre : le derrière de la tête et la joue, en bas à gauche
  + shape(sm('240,150 256,172 280,190 312,204 346,206 340,232 236,232'), CREAM.shade, 0.45)
  + shape(sm('238,100 258,104 266,120 262,140 250,160 236,160'), FUR.shade, 0.45)
  // le front et l'arête du museau, éclairés
  + glint([[280, 104, 0], [310, 102, 4], [344, 108, 3.6], [368, 118, 0]], FUR.hi, 0.7)
  + glint([[382, 129, 0], [404, 141, 3.2], [428, 153, 0]], FUR.hi, 0.85)
  // une touffe plus claire sur la joue, sous l'œil
  + shape(sm('300,170 318,176 336,182! 326,184 312,184'), CREAM.hi, 0.8)
  // les points des moustaches
  + dot(390, 157, 1.7, '#9a4a1a') + dot(397, 162, 1.5, '#9a4a1a') + dot(389, 166, 1.4, '#9a4a1a')
  // la truffe
  + `<path d="M418 158 C424 151 436 152 441 160 C444 167 439 174 431 174 C423 174 417 168 418 158 Z" fill="url(#g-nose)"/>`
  + oval(434, 157.5, 3.4, 2, '#b4a8b8', 0.85, 20) + oval(426, 167, 2, 1.3, '#0a0408', 0.8, 20)
  // le coin de la gueule, retroussé
  + glint([[356, 176, 0], [362, 182, 3], [362, 190, 0]], '#7a2a2a', 0.55)
  + eye()
);

// ---------- les pattes ----------
/** L'habillage d'une patte : la fourrure, l'ombre du côté arrière, deux plis entre les doigts, trois griffes claires. */
function legBody(id, fill, shadeD, toes, claws, liteD) {
  return use(id, fill) + clip(id,
    shape(shadeD, SH.fur, 0.35)
    + (liteD ? glint(liteD, FUR.hi, 0.5) : '')
    + toes.map(([x, y, x2, y2]) => glint([[x, y, 0], [(x + x2) / 2, (y + y2) / 2, 2.4], [x2, y2, 0]], SH.fur, 0.6)
      + glint([[x + 2, y, 0], [(x + x2) / 2 + 2, (y + y2) / 2, 1.4], [x2 + 2, y2, 0]], FUR.hi, 0.5)).join('')
    + claws.map(([x, y]) => oval(x, y, 2.4, 1.6, '#f6ecdc', 1, 30) + oval(x + 0.6, y - 0.4, 1, 0.6, '#ffffff')).join(''));
}

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'legBF', cls: 'a-legBF', d: S.legBF, body: legBody('legBF', 'url(#g-far)', sm('86,232 102,240 106,270 104,300 112,322 86,334'), [[112, 316, 112, 330], [122, 314, 123, 329]], [[132, 328], [124, 329]]) },
  { id: 'legFF', cls: 'a-legFF', d: S.legFF, body: legBody('legFF', 'url(#g-far)', sm('282,230 296,252 312,278 326,302 330,326 318,326 280,240'), [[352, 308, 354, 321], [362, 306, 364, 320]], [[376, 319], [366, 321], [356, 321]]) },
  { id: 'tail', cls: 'a-tail', d: S.tail, body: use('tail', 'url(#g-tail)') + clip('tail', leaves(TAIL, '#5a1806', 0.38)) },
  { id: 'body', cls: 'a-body', d: S.body, shadow: [sh(['legBF', 'legFF'], -3, 5, SH.dark, 0.45), sh(['tail'], -3, 5, SH.fur, 0.4)],
    body: use('body', 'url(#g-fur)') + clip('body',
      // le ventre crème entre les pattes, son ombre lavande dessous
      shape(sm('140,244 180,250 230,252 280,240 306,226 300,262 140,270'), 'url(#g-cream)')
      + shape(sm('140,258 190,262 240,262 290,250 296,272 140,274'), CREAM.shade, 0.7)) },
  { id: 'legBN', cls: 'a-legBN', d: S.legBN, shadow: [sh(['body', 'tail'], -3, 5, SH.fur, 0.4)],
    body: legBody('legBN', 'url(#g-fur)', sm('108,232 124,250 146,262 156,282 160,300 154,334 104,334'), [[170, 312, 172, 327], [184, 312, 186, 327]], [[202, 326], [192, 328], [182, 329]],
      [[150, 218, 0], [176, 224, 4], [190, 244, 3], [186, 270, 0]]) },
  { id: 'legFN', cls: 'a-legFN', d: S.legFN, shadow: [sh(['body', 'legFF'], -3, 5, SH.fur, 0.4)],
    body: legBody('legFN', 'url(#g-fur)', sm('224,236 234,262 240,290 244,312 240,336 222,336'), [[266, 316, 268, 330], [278, 316, 280, 330]], [[292, 328], [282, 330], [272, 331]],
      [[256, 240, 0], [264, 262, 3.6], [262, 290, 0]]) },
  { id: 'mantle', cls: 'a-body', d: S.mantle, shadow: [sh(['body', 'legBN', 'legFN', 'tail'], -4, 6, SH.fur, 0.45)],
    body: use('mantle', LEAF.O.base) + clip('mantle', leaves(MANTLE)) },
  { id: 'chest', cls: 'a-body', d: S.chest, shadow: [sh(['mantle', 'legFN', 'body'], -3, 5, SH.fur, 0.35)],
    body: use('chest', 'url(#g-cream)') + clip('chest',
      shape(sm('248,170 262,200 286,222 300,238 296,252 248,252'), CREAM.shade, 0.55)
      + glint([[300, 168, 0], [320, 186, 4], [332, 210, 0]], CREAM.hi, 0.9)
      + glint([[288, 214, 0], [300, 226, 2.6], [306, 242, 0]], CREAM.mid, 0.8)) },
  { id: 'earF', cls: 'a-earF', d: S.earF, body: use('earF', 'url(#g-ear)') + clip('earF',
    shape(sm('254,114 249,88 247,58 248,46! 262,62 278,82 290,102 272,112'), 'url(#g-earIn)')
    + shape(sm('292,120 284,106 277,93! 274,104 266,97! 264,110 254,120'), CREAM.mid, 0.9)
    + glint([[248, 40, 0], [262, 56, 2.6], [282, 80, 0]], FUR.hi, 0.7)) },
  { id: 'earN', cls: 'a-earN', d: S.earN, body: use('earN', 'url(#g-ear)') + clip('earN',
    shape(sm('318,106 318,80 320,58 323,44! 334,60 346,80 356,98 340,106'), 'url(#g-earIn)')
    + shape(sm('358,114 349,101 344,88! 340,100 332,92! 331,106 320,114'), CREAM.mid, 0.9)
    + glint([[326, 34, 0], [342, 52, 3], [362, 86, 0]], FUR.hi, 0.75)) },
  { id: 'mouth', cls: 'a-head', d: S.mouth, body: use('mouth', 'url(#g-mouth)') + clip('mouth',
    // la langue, au fond, et les dents du bas suivent la mâchoire (même mouvement qu'elle) ; puis les dents du haut
    `<g class="a-teeth">${shape('M356 206 C364 194 382 191 398 197 C406 201 406 210 400 214 L356 216 Z', '#d85a68')
    + glint([[366, 198, 0], [380, 195, 3], [394, 198, 0]], '#f49aa2', 0.8)
    + TEETH_B.map((t) => tooth(...t)).join('')}</g>`
    + TEETH_T.map((t) => tooth(...t)).join('')) },
  { id: 'jaw', cls: 'a-jaw', d: S.jaw, shadow: [sh(['chest'], -3, 5, SH.cream, 0.35)], body: use('jaw', 'url(#g-cream)') + clip('jaw',
    shape(sm('340,210 366,220 392,222 414,212 414,228 340,228'), CREAM.shade, 0.7)
    + glint([[360, 201, 0], [384, 205, 2.4], [408, 206, 0]], '#fff8f0', 0.9)) },
  { id: 'head', cls: 'a-head', d: S.head, shadow: [sh(['mantle', 'earF', 'earN'], -3, 6, SH.fur, 0.4), sh(['chest', 'jaw'], -3, 5, SH.cream, 0.28)], body: headBody },
];

// --- seulement quand il est animé : des feuilles arrachées à la queue pendant l'attaque (sans contour) ---
const FLY = [[60, 60, -30, 'Y'], [34, 140, 10, 'O'], [90, 30, -60, 'R']], FLYL = 15;
const flying = { id: 'fly', d: 'M-900 -900', body: FLY.map(([x, y, a, c], i) => `<g class="a-fly${i + 1}"><g transform="rotate(${a} ${x} ${y})">`
  + shape(leafD([x + FLYL, y, x - FLYL, y, 13, 0]), LEAF[c].base) + shape(leafHalf(x + FLYL, y, x - FLYL, y, 13, 0), LEAF[c].lite, 0.8) + '</g></g>').join('') };

// ---------- la vie au repos et l'attaque ----------
// Repos : il gronde. Le corps (avec le manteau et le poitrail) se soulève à chaque souffle, la tête suit en hochant un
// peu, la mâchoire tremble de colère, la queue balance son éventail, les oreilles frémissent de temps en temps, il cligne.
// Les pattes restent plantées.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : il se ramasse en arrière (élan), bondit en avant la gueule grande
// ouverte, mord (la mâchoire claque), la queue fouette et perd quelques feuilles ; puis il revient exactement à sa place.
// L'attaque s'ajoute au repos (animation-composition) ; le bond lui-même est porté par un groupe qui contient tout.
const G = [232, 331];
const PIV = { root: G, body: [210, 268], head: [300, 172], jaw: [350, 192], tail: [140, 196], earF: [270, 114], earN: [336, 106],
  legBF: [112, 240], legBN: [160, 224], legFN: [246, 240], legFF: [296, 236] };
const IDLE = {
  'a-body': ['body', 'body 1.3s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 2.6s ease-in-out infinite alternate'],
  'a-jaw': ['jaw', 'jaw .34s ease-in-out infinite alternate'],
  'a-teeth': ['jaw', 'jaw .34s ease-in-out infinite alternate'],
  'a-tail': ['tail', 'tail 2.2s ease-in-out infinite alternate'],
  'a-earF': ['earF', 'earF 3.7s linear infinite'],
  'a-earN': ['earN', 'earN 4.3s linear -1.2s infinite'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('')
  + ['root', 'legBF', 'legBN', 'legFN', 'legFF'].map((k) => `.a-${k}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px}`).join('') + `
.a-blink{animation:blink 4.4s linear infinite}
.a-fly1,.a-fly2,.a-fly3{opacity:0}
@keyframes body{from{transform:none}to{transform:translate(0,-2.4px) scale(1.006,1.012)}}
@keyframes head{from{transform:none}to{transform:translate(0.6px,-1px) rotate(-1.6deg)}}
@keyframes jaw{from{transform:none}to{transform:rotate(1.6deg)}}
@keyframes tail{from{transform:rotate(-1.5deg)}to{transform:rotate(3deg)}}
@keyframes earF{0%,84%{transform:none}88%{transform:rotate(-7deg)}92%{transform:rotate(2deg)}96%,100%{transform:none}}
@keyframes earN{0%,86%{transform:none}90%{transform:rotate(6deg)}94%{transform:rotate(-2deg)}98%,100%{transform:none}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-body', 'body-atk')}${atk('a-head', 'head-atk')}${atk('a-jaw', 'jaw-atk')}${atk('a-teeth', 'jaw-atk')}${atk('a-tail', 'tail-atk')}
${atk('a-legBF', 'legB-atk')}${atk('a-legBN', 'legB-atk')}${atk('a-legFN', 'legF-atk')}${atk('a-legFF', 'legF-atk')}
.atk .a-fly1{animation:fly1 .75s ease-out}.atk .a-fly2{animation:fly2 .75s ease-out}.atk .a-fly3{animation:fly3 .75s ease-out}
@keyframes root-atk{0%{transform:none}28%{transform:translate(-8px,2px) rotate(-1.5deg)}46%{transform:translate(30px,-8px) rotate(2deg)}60%{transform:translate(26px,0) rotate(0.5deg)}80%{transform:translate(4px,0)}100%{transform:none}}
@keyframes body-atk{0%{transform:none}28%{transform:scale(0.98,0.95)}46%{transform:scale(1.04,0.98)}60%{transform:scale(1.02,0.99)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}28%{transform:rotate(-9deg)}46%{transform:translate(5px,4px) rotate(7deg)}60%{transform:translate(3px,2px) rotate(4deg)}82%{transform:rotate(-1deg)}100%{transform:none}}
@keyframes jaw-atk{0%{transform:none}28%{transform:rotate(14deg)}40%{transform:rotate(17deg)}50%{transform:rotate(-4deg)}62%{transform:rotate(-3deg)}100%{transform:none}}
@keyframes tail-atk{0%{transform:none}28%{transform:rotate(-9deg)}46%{transform:rotate(12deg)}62%{transform:rotate(6deg)}100%{transform:none}}
@keyframes legB-atk{0%{transform:none}28%{transform:rotate(-6deg)}46%{transform:rotate(14deg)}62%{transform:rotate(5deg)}100%{transform:none}}
@keyframes legF-atk{0%{transform:none}28%{transform:rotate(6deg)}46%{transform:rotate(-16deg)}62%{transform:rotate(-6deg)}100%{transform:none}}
${FLY.map(([x, y], i) => `.a-fly${i + 1}{transform-origin:${x}px ${y}px}@keyframes fly${i + 1}{0%,38%{opacity:0;transform:none}50%{opacity:1;transform:translate(${-10 - i * 4}px,${-6 + i * 6}px) rotate(${(i % 2 ? 1 : -1) * 40}deg)}90%{opacity:0;transform:translate(${-46 - i * 10}px,${20 + i * 14}px) rotate(${(i % 2 ? 1 : -1) * 160}deg)}100%{opacity:0;transform:none}}`).join('')}
`.replace(/\n/g, '');

// ---------- le rendu ----------
/** Enveloppe chaque groupe de classe `cls` dans un groupe de classe `outer` (repris du harfang). */
function nest(s, cls, outer) {
  const open = `<g class="${cls}">`;
  let i = s.indexOf(open);
  while (i >= 0) {
    let depth = 0, j = i;
    const re = /<g[\s>]|<\/g>/g;
    re.lastIndex = i;
    let m;
    while ((m = re.exec(s))) {
      depth += m[0] === '</g>' ? -1 : 1;
      if (depth === 0) { j = m.index + 4; break; }
    }
    s = s.slice(0, i) + `<g class="${outer}">` + s.slice(i, j) + '</g>' + s.slice(j);
    i = s.indexOf(open, i + outer.length + 14 + open.length);
  }
  return s;
}

function svg(anime = true) {
  let s = figure({ w: W, h: H, pad: PAD, defs, style, parts: anime ? [...parts, flying] : parts, anime });
  if (!anime) return s;
  // la tête emporte les oreilles et la mâchoire ; le corps emporte la tête et la queue
  for (const c of ['a-earF', 'a-earN', 'a-jaw']) s = nest(s, c, 'a-head');
  for (const c of ['a-head', 'a-tail']) s = nest(s, c, 'a-body');
  // tout le renard bondit pendant l'attaque
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'ronciers-1', w: W, h: H, pad: PAD, foot: G, svg };
