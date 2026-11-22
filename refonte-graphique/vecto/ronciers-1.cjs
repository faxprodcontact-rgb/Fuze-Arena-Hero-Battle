// Le renard de feuilles (ronciers-1), monstre des Ronciers : redessiné par le code d'après le dessin d'origine, dans le
// même cadre (442 × 337, mêmes proportions, même pose) : renard orange de profil tourné vers la droite, qui grogne ;
// grande queue en éventail de feuilles d'automne, manteau de feuilles rouges, orange et jaunes posées en tuiles sur le
// dos, deux oreilles pointues à l'intérieur sombre, œil jaune furieux sous un gros sourcil, museau à truffe noire,
// gueule ouverte à crocs, joues et poitrail crème en touffes, quatre pattes aux petites griffes sombres.
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
  lin('g-fur', 300, 120, 220, 290, [[0, '#ffc864'], [0.45, '#fbaa40'], [1, '#e08a30']]),
  lin('g-head', 390, 100, 270, 210, [[0, '#ffd27a'], [0.45, '#fcae44'], [1, '#e8902e']]),
  lin('g-far', 0, 0, 0, 1, [[0, '#ec9a3c'], [1, '#c4722a']], false),
  lin('g-leg', 0, 0, 1, 0, [[0, '#c4601c'], [0.55, FUR.base], [1, FUR.lite]], false),
  lin('g-cream', 0, 0, 0, 1, [[0, CREAM.hi], [0.55, CREAM.base], [1, CREAM.shade]], false),
  rad('g-tail', 140, 196, 178, [[0, '#a83a16'], [0.3, '#dc6a28'], [0.62, '#f29c38'], [1, '#ffd468']]),
  lin('g-ear', 0, 0, 1, 0, [[0, '#e08a2c'], [0.6, '#fbaa40'], [1, '#ffc864']], false),
  lin('g-earIn', 0, 0, 0, 1, [[0, '#9a4a4e'], [0.6, '#c06d72'], [1, '#d88a84']], false),
  lin('g-earInN', 0, 0, 0, 1, [[0, '#4a1a10'], [0.55, '#8a3a18'], [1, '#e07c1e']], false),
  rad('g-sclera', 0.6, 0.35, 0.8, [[0, '#ffffff'], [0.7, '#fbf6f2'], [1, '#e2d4d4']], false),
  rad('g-iris', 0.62, 0.38, 0.75, [[0, '#fffde0'], [0.4, '#fbf27a'], [0.8, '#e8c83a'], [1, '#b08020']], false),
  rad('g-pupil', 0.5, 0.8, 0.7, [[0, '#5a2a10'], [0.6, '#24100a'], [1, '#120608']], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#3a1408', 0.75], [0.5, '#3a1408', 0]], false),
  lin('g-eyelid', 0, 0, 0, 1, [[0, FUR.lite], [0.6, FUR.base], [1, FUR.mid]], false),
  lin('g-mouth', 0, 172, 0, 218, [[0, '#24060c'], [0.55, '#4e1018'], [1, '#7e2430']]),
  rad('g-nose', 0.62, 0.3, 0.8, [[0, '#6a5a66'], [0.4, '#2e2230'], [1, '#140c14']], false),
].join('');

// ---------- silhouettes ----------
// Tête et pattes décalquées sur le dessin d'origine : leur bord extérieur suit le contour du trait noir d'origine,
// rentré de l'épaisseur de notre contour (mesuré sur l'image, pas à l'œil).
const S = {
  // les pattes du fond (plus sombres) : la patte arrière gauche, la patte avant droite qui s'avance
  legBF: sm('106,224 98,234 95,250 93,268 91,278 91,288 89,298 84,311 85,321! 96,323 116,323 126,321! 124,314 117,309 113,305 114,292 116,286 119,283 124,268 126,246 120,230'),
  legFF: sm('288,240 300,228 318,226 324,233 320,241 321,252 320,260 327,268 340,288 349,298 359,297 367,300 372,308 372,317! 331,316! 330,310 325,304 318,296 311,292 306,287 299,284 291,278 289,270 286,256'),
  // la queue : la réunion de ses feuilles
  tail: TAIL.map((l) => leafD(l)).join(''),
  // le corps : le dos (caché sous le manteau), le ventre entre les pattes
  body: sm('104,200 130,180 170,170 220,166 262,160 300,170 318,196 316,226 300,248 289,268 282,264 270,265 262,268 240,270 224,272 214,266 204,268 196,276 170,276 146,280 132,283 118,282 110,262 102,232'),
  // les pattes de devant (plus claires) : la patte arrière droite et sa grosse cuisse, la patte avant gauche
  legBN: sm('124,232 140,226 170,222 192,230 204,246 206,262 200,272 195,280 189,281 180,283 176,288 176,294 178,299 183,303 191,304 195,308 198,316! 156,317! 156,309 154,302 152,291 148,283 140,262 130,246'),
  legFN: sm('222,244 240,236 262,238 270,252 266,268 263,272 263,279 270,305 274,309 284,310 291,317 292,326! 282,329 267,328 260,329 244,326! 243,315 241,303 235,292 228,283 227,276 222,262'),
  // le manteau de feuilles
  mantle: MANTLE.map((l) => leafD(l)).join(''),
  // le cou et le poitrail, crème, sous la joue et jusqu'entre les pattes ; son bord arrière en touffes contre les feuilles
  chest: sm('256,170 280,190 300,198 330,200 346,208 338,210 330,217 329,228 324,236 312,252 296,266 284,265 270,266 256,258 248,250! 253,240 244,231! 251,222 244,211! 251,203 246,191! 253,182'),
  // les oreilles, derrière la tête : celle du fond est large, celle de devant plus fine
  earF: sm('247,41! 259,49 289,67 307,83 302,100 276,114 260,108 256,95 252,79 246,52'),
  earN: sm('313,86 316,79 319,51 323.5,33! 336,49 355,77 363,94 366,104 344,108 318,100'),
  // la gueule (l'intérieur, derrière la mâchoire et la tête) ; devant, le croc du haut dépasse
  mouth: sm('352,168 390,172 428,170 431,178 425,182 421,190! 417,184 410,185 405,189 398,192 395,198 398,204 392,212 372,210 354,204 345,192'),
  // la mâchoire du bas, ouverte
  jaw: sm('338,206 346,199 352,199 364,205 380,209 392,210 398,206! 400,212 397,219 389,223 376,223 362,217 348,211'),
  // la tête : le crâne entre les oreilles (avec les touffes claires au pied de l'oreille), le front, le stop, le museau
  // jusqu'à la truffe, la lèvre du haut, puis la joue en touffes qui partent vers l'arrière, et la nuque
  head: sm('270,108 288,96 304,88 312,85 322,90 332,89 338,95 350,92 356,98 366,98 371,106 391,119 397,125 399,134 400,142 404,146 420,153 430,157 434,161 435,167 '
    + '432,173 424,179 416,183 408,185 400,184 392,182 382,178 372,176 362,175 354,176 349,184 346,194 '
    + '341,203! 332,198 323,206! 315,200 305,205! 297,198 287,201! 281,193 272,193! 270,184 260,174! 262,164 251,154! 256,144 246,132! 254,124 247,116! 258,114'),
};

// ---------- le visage ----------
/** Une dent pointue : la moitié du fond dans l'ombre, un filet de lumière sur l'autre flanc. b1, b2 = la racine, t = la pointe. */
function tooth([x1, y1], [x2, y2], [tx, ty]) {
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  const d = `M${x1} ${y1}Q${n((x1 + tx) / 2 - (ty - y1) * 0.08)} ${n((y1 + ty) / 2)} ${tx} ${ty}Q${n((x2 + tx) / 2 + (ty - y2) * 0.08)} ${n((y2 + ty) / 2)} ${x2} ${y2}Z`;
  const half = `M${x1} ${y1}L${tx} ${ty}L${n(mx)} ${n(my)}Z`;
  return shape(d, '#fbf4e8') + shape(half, '#d8c8bc', 0.8) + line(`M${n(mx + (x2 - mx) * 0.5)} ${n(my + (y2 - my) * 0.5)}L${n(tx + (x2 - tx) * 0.2)} ${n(ty + (y2 - ty) * 0.2)}`, '#ffffff', 1.2, 0.9);
}
// les dents du haut (le gros croc au milieu, le croc de devant qui dépasse) ; celles du bas, plantées dans la mâchoire
const TEETH_T = [[[356, 172], [364, 173], [361, 182]], [[366, 174], [375, 175], [371, 186]], [[378, 176], [389, 178], [385, 192]], [[400, 181], [409, 182], [406, 191]], [[416, 178], [426, 177], [421, 190]]];
const TEETH_B = [[[359, 205], [367, 207], [364, 195]], [[371, 209], [381, 211], [377, 199]], [[384, 212], [392, 212], [389, 201]], [[393, 210], [400, 206], [398, 196]]];

/**
 * L'œil, en forme de haricot : le bord du haut est droit et penché vers le nez (le sourcil le coupe), le bas est rond.
 * L'anneau sombre, le blanc, l'iris jaune, la pupille, l'ombre de la paupière, deux reflets ; puis le sourcil épais
 * qui plonge vers le museau. Le clignement : une paupière de fourrure.
 */
const EYE = 'M325 126 L374 141 C375 150 369 157 358 160 C346 162 335 159 329 152 C323 145 322 135 325 126 Z';
const IRIS = { x: 353, y: 148, r: 11.5, p: 7.4 };
function eye() {
  const { x, y, r, p } = IRIS;
  const brow = 'M322 119 C340 123 360 129 377 135 C380 137 380 142 376 143 C366 141 356 138 346 135 C336 132 330 130 324 128 C320 126 319 121 322 119 Z';
  return `<path d="${EYE}" fill="#2a1430" stroke="#2a1430" stroke-width="5"/>`
    + `<clipPath id="c-eye"><path d="${EYE}"/></clipPath><path d="${EYE}" fill="url(#g-sclera)"/>`
    + `<g clip-path="url(#c-eye)">`
    + dot(x, y, r, 'url(#g-iris)') + dot(x - 0.4, y - 3, p, 'url(#g-pupil)')
    + `<rect x="322" y="126" width="56" height="14" fill="url(#g-lid)" transform="rotate(17 350 134)"/>`
    + dot(x + 5.5, y - 2.5, 2.4, '#fff') + dot(x - 4.5, y + 4.5, 1.1, '#fff', 0.9)
    + '</g>'
    + `<g class="a-blink" opacity="0"><path d="${EYE}" fill="url(#g-eyelid)" stroke="#2a1430" stroke-width="2.6"/>${line('M327 144 Q348 158 373 147', '#2a1430', 2.6)}</g>`
    // le sourcil : son ombre portée sur l'œil, le sourcil sombre, le bourrelet de fourrure éclairé au-dessus
    + `<path d="${brow}" transform="translate(-1.5 2.5)" fill="${SH.dark}" opacity="0.4"/>` + shape(brow, '#3a1408')
    + glint([[326, 117, 0], [346, 119, 3.4], [366, 125, 3], [380, 131, 0]], FUR.hi, 0.8);
}

const headBody = use('head', 'url(#g-head)') + clip('head',
  // le bas de la tête, crème : la joue en touffes, la lèvre du haut, le dessous du museau
  shape(sm('236,192 262,178 282,174 301,170 322,164 346,161 370,157 390,152 412,153 440,160 446,240 236,240'), 'url(#g-cream)')
  // le bas de la joue, à l'ombre (lavande), au-dessus des touffes
  + shape(sm('266,188 290,190 314,194 338,196 346,212 266,212'), CREAM.shade, 0.6)
  // la nuque à l'ombre, en bas à gauche
  + shape(sm('240,114 258,120 268,140 266,166 260,184 240,184'), FUR.shade, 0.45)
  // les touffes claires au pied de l'oreille de devant
  + shape(sm('322,96 330,90 336,99 346,92 352,101 362,99 368,108 330,108'), FUR.hi, 0.6)
  // le front et l'arête du museau, éclairés
  + glint([[282, 100, 0], [304, 92, 3.6], [330, 96, 0]], FUR.hi, 0.6)
  + glint([[404, 145, 0], [418, 151, 3], [430, 157, 0]], FUR.hi, 0.85)
  // la tache orange et les points des moustaches
  + oval(393, 154, 2.4, 1.8, '#c8641c', 0.9) + dot(391, 160, 1.3, '#5a2a1a') + dot(397, 164, 1.2, '#5a2a1a') + dot(390, 167, 1.2, '#5a2a1a') + dot(396, 170, 1.1, '#5a2a1a')
  // la truffe
  + `<path d="M412 159 C416 152 427 151 436 155 C441 158 442 166 438 171 C433 175 423 175 417 171 C412 168 411 163 412 159 Z" fill="url(#g-nose)"/>`
  + oval(421, 156.5, 3.6, 1.8, '#d8d0dc', 0.9, -10)
  // le coin de la gueule, retroussé
  + glint([[352, 174, 0], [350, 182, 2.6], [347, 190, 0]], '#7a2a2a', 0.5)
  + eye()
);

// ---------- les pattes ----------
/** L'habillage d'une patte : la fourrure, l'ombre du côté arrière, deux plis entre les doigts, trois griffes sombres. */
function legBody(id, fill, shadeD, toes, claws, liteD) {
  return use(id, fill) + clip(id,
    shape(shadeD, SH.fur, 0.35)
    + (liteD ? glint(liteD, FUR.hi, 0.5) : '')
    + toes.map(([x, y, x2, y2]) => glint([[x, y, 0], [(x + x2) / 2, (y + y2) / 2, 2.4], [x2, y2, 0]], SH.fur, 0.6)
      + glint([[x + 2, y, 0], [(x + x2) / 2 + 2, (y + y2) / 2, 1.4], [x2 + 2, y2, 0]], FUR.hi, 0.5)).join('')
    + claws.map(([x, y]) => oval(x, y, 2.6, 1.7, '#3a2418', 1, 30) + oval(x + 0.7, y - 0.5, 1, 0.6, '#d8c8b8')).join(''));
}

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'legBF', cls: 'a-legBF', d: S.legBF, body: legBody('legBF', 'url(#g-far)', sm('80,228 100,238 104,270 100,300 104,328 78,328'), [[106, 311, 107, 322], [116, 310, 117, 322]], [[124, 320], [114, 322], [104, 322]]) },
  { id: 'legFF', cls: 'a-legFF', d: S.legFF, body: legBody('legFF', 'url(#g-far)', sm('284,236 300,262 316,286 332,302 336,322 320,322 282,250'), [[352, 302, 353, 315], [362, 302, 363, 315]], [[371, 315], [362, 316], [352, 316]]) },
  { id: 'tail', cls: 'a-tail', d: S.tail, body: use('tail', 'url(#g-tail)') + clip('tail', leaves(TAIL, '#5a1806', 0.38)) },
  { id: 'body', cls: 'a-body', d: S.body, shadow: [sh(['legBF', 'legFF'], -3, 5, SH.dark, 0.45), sh(['tail'], -3, 5, SH.fur, 0.4)],
    body: use('body', 'url(#g-fur)') + clip('body',
      // le ventre crème entre les pattes, son ombre lavande dessous
      shape(sm('140,260 190,264 240,260 290,250 306,236 300,290 140,290'), 'url(#g-cream)')
      + shape(sm('140,272 190,272 240,268 290,260 296,290 140,290'), CREAM.shade, 0.7)) },
  { id: 'legBN', cls: 'a-legBN', d: S.legBN, shadow: [sh(['body', 'tail', 'legBF'], -3, 5, SH.fur, 0.4)],
    body: legBody('legBN', 'url(#g-fur)', sm('120,232 136,250 146,272 154,296 158,322 138,322'), [[176, 305, 177, 316], [186, 305, 187, 316]], [[196, 315], [186, 317], [176, 317]],
      [[166, 226, 0], [194, 236, 4], [204, 256, 3], [198, 276, 0]]) },
  { id: 'legFN', cls: 'a-legFN', d: S.legFN, shadow: [sh(['body', 'legFF'], -3, 5, SH.fur, 0.4)],
    body: legBody('legFN', 'url(#g-fur)', sm('218,240 230,262 238,290 246,312 248,332 216,332'), [[266, 314, 267, 327], [278, 313, 279, 326]], [[290, 325], [280, 328], [269, 328]],
      [[258, 240, 0], [266, 256, 3.6], [266, 276, 2.4], [272, 300, 0]]) },
  { id: 'mantle', cls: 'a-body', d: S.mantle, shadow: [sh(['body', 'legBN', 'legFN', 'tail'], -4, 6, SH.fur, 0.45)],
    body: use('mantle', LEAF.O.base) + clip('mantle', leaves(MANTLE)) },
  { id: 'chest', cls: 'a-body', d: S.chest, shadow: [sh(['mantle', 'body'], -3, 4, SH.fur, 0.22), sh(['legFN', 'legFF'], -3, 5, SH.fur, 0.35)],
    body: use('chest', 'url(#g-cream)') + clip('chest',
      // le bas du poitrail à l'ombre (lavande), un reflet devant
      shape(sm('244,238 262,252 284,258 304,254 318,244 316,272 244,272'), CREAM.shade, 0.6)
      + glint([[318, 206, 0], [330, 216, 3], [328, 232, 0]], CREAM.hi, 0.9)) },
  { id: 'earF', cls: 'a-earF', d: S.earF, body: use('earF', 'url(#g-ear)') + clip('earF',
    // l'intérieur rose sombre, le bord orange à droite, la touffe crème au fond
    shape(sm('250,50 262,58 282,74 292,90 284,104 266,108 260,100 257,86 253,70'), 'url(#g-earIn)')
    + shape(sm('294,104 290,92 284,82 281,92 275,82 272,94 265,88 266,100 262,110 280,112'), CREAM.mid, 0.95)
    + glint([[252, 44, 0], [270, 56, 2.6], [296, 76, 0]], FUR.hi, 0.7)) },
  { id: 'earN', cls: 'a-earN', d: S.earN, body: use('earN', 'url(#g-ear)') + clip('earN',
    // l'intérieur brun sombre vers la pointe, qui s'éclaircit vers le bas
    shape(sm('320,54 324,40 334,52 350,76 358,96 344,102 322,98 319,76'), 'url(#g-earInN)')
    + glint([[326, 36, 0], [344, 54, 3], [362, 88, 0]], FUR.hi, 0.75)) },
  { id: 'mouth', cls: 'a-head', d: S.mouth, body: use('mouth', 'url(#g-mouth)') + clip('mouth',
    // la langue, au fond, et les dents du bas suivent la mâchoire (même mouvement qu'elle) ; puis les dents du haut
    `<g class="a-teeth">${shape('M350 204 C356 190 372 186 386 192 C392 196 392 204 386 208 L350 210 Z', '#d85a68')
    + glint([[358, 194, 0], [370, 190, 3], [384, 194, 0]], '#f49aa2', 0.8)
    + TEETH_B.map((t) => tooth(...t)).join('')}</g>`
    + TEETH_T.map((t) => tooth(...t)).join('')) },
  { id: 'jaw', cls: 'a-jaw', d: S.jaw, shadow: [sh(['chest'], -3, 5, SH.cream, 0.35)], body: use('jaw', 'url(#g-cream)') + clip('jaw',
    shape(sm('336,212 362,220 390,224 402,214 404,230 336,230'), CREAM.shade, 0.7)
    + glint([[354, 201, 0], [376, 208, 2.4], [396, 208, 0]], '#fff8f0', 0.9)) },
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
const PIV = { root: G, body: [210, 268], head: [300, 180], jaw: [344, 200], tail: [140, 196], earF: [282, 104], earN: [338, 100],
  legBF: [110, 236], legBN: [166, 232], legFN: [244, 248], legFF: [302, 240] };
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
