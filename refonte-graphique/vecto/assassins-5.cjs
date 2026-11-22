// La fille-phénix (assassins-5) : redessinée par le code d'après le dessin d'origine, dans le même cadre (556 × 515,
// mêmes proportions, même pose) : chevelure rousse, diadème d'or à la pierre rouge, yeux ambre et sourire assuré,
// deux grandes ailes de feu déployées (plumes orange à rouge, lumière jaune), traîne de plumes à gauche, robe blanche
// en plumes à la ceinture d'or, bracelets, pattes d'oiseau dorées à griffes, boule de feu dans la main droite.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 556, H = 515;

// ---------- petits outils ----------
/**
 * Courbe lisse qui passe par des points (Catmull-Rom → Bézier). Un point [x, y, 1] est un angle vif.
 * Écriture compacte, pour que le dessin reste léger : `q` décimales (0 pour les grandes formes), coordonnées relatives
 * (« c », « s ») et, aux points lisses, « s » (le premier point de contrôle est le reflet du précédent).
 */
function P(pts, closed = true, q = 0) {
  const N = pts.length, k = 10 ** q;
  const R = (v) => Math.round(v * k);                       // en unités de 1/k, entières (pas de dérive)
  const num = (v) => {
    let t = (v / k).toFixed(q);
    if (q) t = t.replace(/\.?0+$/, '').replace(/^(-?)0\./, '$1.');   // 2.50 → 2.5, 0.5 → .5 (seulement après la virgule)
    return t === '-0' ? '0' : t;
  };
  const list = (vs) => vs.map((v, i) => (i && v >= 0 ? ' ' : '') + num(v)).join('');
  const at = (i) => (closed ? pts[(i + N) % N] : pts[Math.max(0, Math.min(N - 1, i))]);
  const sharp = (i) => !!at(i)[2] || (!closed && (i <= 0 || i >= N - 1));
  const tan = (i, dir) => {
    const p = at(i);
    if (sharp(i)) { const o = at(i + dir); return [(o[0] - p[0]) * dir / 3, (o[1] - p[1]) * dir / 3]; }
    const a = at(i - 1), b = at(i + 1);
    return [(b[0] - a[0]) / 6, (b[1] - a[1]) / 6];
  };
  let X = R(pts[0][0]), Y = R(pts[0][1]);
  let d = `M${list([X, Y])}`;
  const last = closed ? N : N - 1;
  for (let i = 0; i < last; i++) {
    const p = at(i), o = at(i + 1), t1 = tan(i, 1), t2 = tan(i + 1, -1);
    const c2 = [R(o[0] - t2[0]) - X, R(o[1] - t2[1]) - Y], e = [R(o[0]) - X, R(o[1]) - Y];
    d += i > 0 && !sharp(i) ? `s${list([...c2, ...e])}` : `c${list([R(p[0] + t1[0]) - X, R(p[1] + t1[1]) - Y, ...c2, ...e])}`;
    X += e[0]; Y += e[1];
  }
  return closed ? d + 'Z' : d;
}
/** Même chose, mais toujours dans le même sens de rotation : plusieurs boucles dans un chemin s'additionnent. */
function L(pts, q = 0) {
  let a = 0;
  for (let i = 0; i < pts.length; i++) { const p = pts[i], o = pts[(i + 1) % pts.length]; a += p[0] * o[1] - o[0] * p[1]; }
  return P(a < 0 ? pts.slice().reverse() : pts, true, q);
}
/** Le point est-il dans le polygone (ses points de passage) ? */
function inside([x, y], poly) {
  let c = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) c = !c;
  }
  return c;
}
/**
 * La silhouette d'un groupe de plumes : seulement celles qui touchent le bord. Une plume entièrement recouverte par les
 * autres (son intérieur, et son bord élargi de la marge du contour, 4,8 px) n'ajoute rien au contour : on ne la répète
 * pas dans la silhouette. Il faut tester l'intérieur aussi : les autres plumes peuvent laisser un trou en son milieu.
 */
function silhouette(polys) {
  // les points qui doivent être couverts pour qu'une plume soit cachée : son centre, son intérieur, son bord élargi
  const probes = (A) => {
    const cx = A.reduce((t, p) => t + p[0], 0) / A.length, cy = A.reduce((t, p) => t + p[1], 0) / A.length;
    const pts = [[cx, cy]];
    A.forEach((p, k) => {
      const a = A[(k + A.length - 1) % A.length], b = A[(k + 1) % A.length];
      let nx = b[1] - a[1], ny = a[0] - b[0];
      const l = Math.hypot(nx, ny) || 1;
      nx /= l; ny /= l;
      if (nx * (p[0] - cx) + ny * (p[1] - cy) < 0) { nx = -nx; ny = -ny; }
      const m = [(p[0] + b[0]) / 2, (p[1] + b[1]) / 2];
      pts.push([p[0] + nx * 4.8, p[1] + ny * 4.8], [m[0] + nx * 4.8, m[1] + ny * 4.8]);
      for (const f of [0.25, 0.5, 0.75]) pts.push([cx + (p[0] - cx) * f, cy + (p[1] - cy) * f], [cx + (m[0] - cx) * f, cy + (m[1] - cy) * f]);
    });
    return pts;
  };
  const covered = (A, by) => probes(A).every((pt) => by.some((B) => inside(pt, B)));
  // on retire les plumes une à une, chacune testée contre ce qui reste ; puis on vérifie que tout ce qui a été retiré
  // est encore couvert par ce qui est gardé (sinon on le remet)
  let keep = polys.slice();
  for (const A of polys) { const rest = keep.filter((B) => B !== A); if (covered(A, rest)) keep = rest; }
  for (const A of polys) if (!keep.includes(A) && !covered(A, keep)) keep.push(A);
  return keep.map((A) => L(A)).join('');
}

/**
 * Une plume : de sa base à sa pointe, bord d'attaque (`up`) puis bord de fuite (`lo`), chacun donné de la base vers la
 * pointe. La pointe est un angle vif.
 */
const quill = (up, tip, lo) => [...up, [tip[0], tip[1], 1], ...lo.slice().reverse()];
/** Une petite plume en amande, de sa base vers sa pointe ; `w` = largeur, `bend` = courbure (+ vers la gauche du trajet). */
function plume(b, t, w, bend = 0) {
  const dx = t[0] - b[0], dy = t[1] - b[1], len = Math.hypot(dx, dy), ux = dx / len, uy = dy / len, vx = -uy, vy = ux;
  const pt = (s, o) => [b[0] + ux * len * s + vx * (o + bend * Math.sin(Math.PI * s)), b[1] + uy * len * s + vy * (o + bend * Math.sin(Math.PI * s))];
  return [pt(0, w * 0.3), pt(0.3, w * 0.5), pt(0.62, w * 0.42), pt(0.86, w * 0.2), [...pt(1, 0), 1], pt(0.84, -w * 0.24), pt(0.58, -w * 0.46), pt(0.28, -w * 0.5), pt(0, -w * 0.3)];
}
/** Le trait du tuyau d'une plume (fin, de la couleur de la plume en plus sombre). */
const shaft = (b, t, k = 0.9) => [b, [b[0] + (t[0] - b[0]) * k, b[1] + (t[1] - b[1]) * k]];

// ---------- couleurs ----------
const SKIN = { hi: '#fff1e6', base: '#fbd3bd', shade: '#eaa58f', deep: '#d0837a', line: '#a45a52' };
const HAIR = { hi: '#ffb070', lite: '#ff8a46', base: '#f2602a', mid: '#dc4422', deep: '#a8241c', line: '#7c1418' };
const GOLD = { hi: '#fff7c2', base: '#f6c64a', mid: '#e09c26', shade: '#a8661a', line: '#74420c' };
const FEA = { hi: '#ffe98a', lite: '#ffc23a', base: '#ff9a24', mid: '#f4711c', red: '#dc4418', deep: '#a82516', wine: '#7e1a26', line: '#9a2a10' };
const WHITE = { hi: '#ffffff', base: '#f8f3f6', shade: '#d9cbe0', deep: '#ad98bd', line: '#8f7aa6' };
const CLAW = { hi: '#ffffff', base: '#e4dbe6', shade: '#9e8ca6' };
// les ombres portées : une teinte par matière qui la reçoit
const SH = { skin: '#b0504a', hair: '#6c0c18', fea: '#7a1208', white: '#6c5488', gold: '#7a4208' };

// ---------- les plumes ----------
// Chaque plume : son contour (de la base à la pointe et retour), sa base `b` et sa pointe `t` (pour le dégradé et le
// tuyau), et sa gamme de couleurs. Les plumes d'une aile sont dessinées dans UN morceau : la silhouette de l'aile est la
// réunion de ses plumes (un seul contour), et dedans chaque plume pose une ombre douce sur celles qu'elle recouvre.
const PAL = {
  // plumes de l'aile gauche : orange, pointe dorée
  prim: { base: '#dc5418', mid: '#fa8a22', tip: '#ffb83c', edge: '#c8421a', light: '#ffe070', shaft: '#c4421a' },
  cov: { base: '#d64c1a', mid: '#fb9026', tip: '#ffc648', edge: '#c4401a', light: '#ffe27a', shaft: '#b43a18' },
  covHi: { base: '#e05a1c', mid: '#fd9a2a', tip: '#ffcc50', edge: '#c8461a', light: '#ffe888', shaft: '#c4481c' },
  // plumes lie-de-vin (le bas des ailes, la traîne)
  wine: { base: '#6a1220', mid: '#952632', tip: '#c34a40', edge: '#520c18', light: '#ee8a72', shaft: '#5a1018' },
  // aile droite : plus rouge, les grandes plumes pâlissent au bout
  primR: { base: '#d8402a', mid: '#f4702c', tip: '#ffb44c', edge: '#c0321e', light: '#ffe6a6', shaft: '#c03a22' },
  covR: { base: '#c63024', mid: '#ec5c2c', tip: '#ff9a3c', edge: '#ac2620', light: '#ffc868', shaft: '#a82a20' },
  // traîne : orange qui fonce vers la hanche
  tail: { base: '#a42a16', mid: '#e0581c', tip: '#ff9a2c', edge: '#8e2012', light: '#ffc85a', shaft: '#a8341a' },
  // plume orange dont la pointe est trempée dans le lie-de-vin (le bas de l'aile, le haut de la traîne)
  dip: { stops: [[0, '#b8361a'], [0.4, '#f07a22'], [0.66, '#ffb444'], [0.8, '#c24a3c'], [1, '#6a1222']],
    edge: '#9a2a1a', light: '#ffd27a', shaft: '#ffd27a', vane: '#7a1a14' },
};
let fid = 0;
const featherDefs = [], featherGrads = {};
const LIGHT = [Math.SQRT1_2, -Math.SQRT1_2];   // la direction de la lumière (en haut à droite)
/**
 * Le dégradé d'une gamme, de la base à la pointe, dans l'une des 8 directions (partagé par toutes les plumes de même
 * gamme et de même direction, en coordonnées de la boîte de la plume).
 */
function featherGrad(pal, ux, uy) {
  const a = Math.round(Math.atan2(uy, ux) / (Math.PI / 4)), id = `g-${pal}${(a + 8) % 8}`;
  if (!featherGrads[id]) {
    const c = PAL[pal], dx = Math.round(Math.cos(a * Math.PI / 4)), dy = Math.round(Math.sin(a * Math.PI / 4));
    featherGrads[id] = lin(id, (1 - dx) / 2, (1 - dy) / 2, (1 + dx) / 2, (1 + dy) / 2, c.stops || [[0, c.base], [0.55, c.mid], [1, c.tip]], false);
  }
  return id;
}
/**
 * Une plume dans une aile : ombre portée sur ce qui est dessous ; la plume en dégradé de sa base à sa pointe ; ses deux
 * moitiés (de part et d'autre du tuyau), celle tournée vers la lumière claire, l'autre plus sombre ; un filet de lumière
 * sur le bord éclairé, un bord plus sombre côté ombre ; le tuyau en trait clair (grandes plumes seulement).
 * Le contour de la plume n'est écrit qu'une fois (dans les defs) : tout le reste le réutilise (<use>).
 */
function feather(f) {
  const k = fid++, c = PAL[f.pal];
  const [bx, by] = f.b, [tx, ty] = f.t, len = Math.hypot(tx - bx, ty - by), ux = (tx - bx) / len, uy = (ty - by) / len;
  const vx = -uy, vy = ux;
  const lit = vx * LIGHT[0] + vy * LIGHT[1] > 0 ? 1 : -1;
  const bend = f.bend || 0;
  // le tuyau : une courbe de la base à la pointe (même courbure que la plume)
  const [cx, cy] = f.ax || [(bx + tx) / 2 + vx * bend * 2, (by + ty) / 2 + vy * bend * 2];
  const R = 120 * -lit;   // vers le côté de l'ombre
  const r = Math.round;
  const vane = `M${r(bx)} ${r(by)}Q${r(cx)} ${r(cy)} ${r(tx)} ${r(ty)}L${r(tx + vx * R)} ${r(ty + vy * R)}L${r(bx + vx * R)} ${r(by + vy * R)}Z`;
  featherDefs.push(`<path id="f${k}" d="${P(f.pts, true, 0)}"/><clipPath id="cf${k}"><use href="#f${k}"/></clipPath>`);
  const u = (attrs) => `<use href="#f${k}"${attrs}/>`;
  const [sx, sy] = f.sh || [-3.5, 3.5];
  const cast = f.so === 0 ? '' : u(` x="${sx}" y="${sy}" fill="${c.cast || '#6a0e06'}" opacity="${f.so || 0.3}"`);
  // le tuyau s'arrête un peu avant la pointe (même courbe, coupée à 90 %)
  const at = (t) => [(1 - t) * (1 - t) * bx + 2 * t * (1 - t) * cx + t * t * tx, (1 - t) * (1 - t) * by + 2 * t * (1 - t) * cy + t * t * ty];
  const [ex, ey] = at(0.9);
  const sw = f.shaft ? line(`M${r(bx)} ${r(by)}Q${r(0.1 * bx + 0.9 * cx)} ${r(0.1 * by + 0.9 * cy)} ${r(ex)} ${r(ey)}`, c.light, f.sw || 1.3, 0.55) : '';
  // sous la plume, sa couleur de bord ; dessus, le dégradé décalé vers la lumière (il laisse un liseré sombre côté ombre)
  return cast + u(` fill="${c.edge}"`)
    + `<g clip-path="url(#cf${k})">${u(` x="1.4" y="-1.4" fill="url(#${featherGrad(f.pal, ux, uy)})"`)}`
    + (f.vane === false ? '' : `<path d="${vane}" fill="${c.vane || c.edge}" opacity="${f.vo || 0.32}"/>`) + `${f.extra || ''}${sw}</g>`;
}
/** Une plume en amande générée (plume()), avec sa gamme. */
const pl = (pal, b, t, w, bend = 0, more = {}) => ({ pal, b, t, bend, pts: plume(b, t, w, bend), vane: pal !== 'white', ...more });

// --- l'aile gauche : quatre grandes rémiges (la plus haute devant), puis trois rangs de couvertures ---
const WL = [
  { pal: 'dip', b: [176, 302], ax: [100, 292], t: [37, 283], shaft: true, pts: [[175, 292], [130, 284], [90, 281], [60, 281], [37, 283, 1], [45, 293], [58, 304], [78, 304], [105, 301], [140, 306], [178, 312]] },
  { pal: 'prim', b: [166, 262], ax: [80, 256], t: [8, 214], shaft: true, pts: [[165, 238], [115, 228], [66, 222], [40, 219], [8, 214, 1], [16, 233], [27, 249], [42, 261], [58, 270], [75, 279], [104, 285], [138, 285], [170, 276]] },
  { pal: 'prim', b: [166, 214], ax: [70, 176], t: [18, 98], shaft: true, pts: [[165, 198], [120, 168], [80, 140], [48, 118], [18, 98, 1], [16, 119], [19, 141], [27, 164], [37, 184], [49, 200], [64, 212], [88, 221], [126, 226], [168, 222]] },
  { pal: 'prim', b: [158, 182], ax: [44, 104], t: [54, 11], shaft: true, pts: [[158, 170], [122, 138], [98, 110], [81, 85], [69, 61], [61, 38], [54, 11, 1], [47, 27], [40, 47], [36, 67], [38, 89], [46, 112], [59, 133], [82, 155], [118, 176], [156, 190]] },
  // les grandes couvertures (rang du bas), pointes vers le haut à gauche : longueurs et angles variés
  pl('dip', [206, 312], [104, 298], 22, 2),
  pl('cov', [236, 292], [150, 280], 22, 3),
  pl('cov', [204, 280], [108, 258], 28, 4),
  pl('cov', [178, 256], [84, 222], 26, 3),
  pl('cov', [154, 234], [48, 200], 32, 5),
  // les couvertures moyennes
  pl('cov', [240, 270], [196, 246], 18, 2),
  pl('cov', [228, 262], [160, 232], 22, 3),
  pl('cov', [204, 242], [120, 206], 28, 4),
  pl('cov', [176, 214], [98, 170], 26, 3),
  pl('cov', [150, 192], [66, 150], 30, 4),
  // les petites couvertures du bord d'attaque : leurs pointes dessinent le bord festonné de l'aile
  pl('covHi', [232, 232], [192, 186], 18, 2),
  pl('covHi', [214, 214], [173, 172], 19, 2),
  pl('covHi', [196, 198], [153, 158], 21, 2),
  pl('covHi', [172, 174], [124, 131], 23, 3),
  pl('covHi', [148, 152], [99, 106], 24, 3),
];
// la racine de l'aile, cachée derrière les cheveux et le buste
const WL_ROOT = [[256, 320], [200, 314], [150, 290], [120, 240], [118, 180], [132, 150], [160, 162], [190, 182], [214, 196],
  [236, 200], [252, 226], [264, 274]];

// --- la traîne : six longues plumes qui partent de la hanche gauche, en éventail ---
const TL = [
  { pal: 'tail', b: [248, 446], ax: [160, 458], t: [92, 493], shaft: true, pts: [[246, 420], [204, 424], [168, 430], [148, 446], [126, 466], [106, 484], [92, 493, 1], [110, 492], [135, 482], [160, 472], [190, 465], [225, 460], [252, 456]] },
  { pal: 'tail', b: [242, 401], ax: [140, 410], t: [57, 447], shaft: true, pts: [[240, 392], [192, 390], [150, 396], [116, 412], [90, 430], [70, 442], [57, 447, 1], [72, 451], [96, 446], [126, 438], [158, 428], [200, 420], [244, 416]] },
  { pal: 'dip', b: [190, 396], ax: [116, 398], t: [57, 419], shaft: true, pts: [[192, 384], [150, 386], [112, 392], [86, 400], [68, 410], [57, 419, 1], [74, 419], [96, 412], [124, 406], [156, 404], [194, 404]] },
  { pal: 'tail', b: [196, 368], ax: [134, 368], t: [83, 388], shaft: true, pts: [[198, 350], [156, 350], [128, 356], [110, 366], [96, 378], [83, 388, 1], [96, 393], [118, 391], [142, 387], [168, 386], [198, 384]],
    extra: shape('M156 356 C132 360 110 370 92 386 C112 376 132 368 158 364 Z', '#fff0a8', 0.55) },
  { pal: 'dip', b: [212, 342], ax: [136, 338], t: [77, 341], shaft: true, pts: [[212, 326], [164, 326], [126, 330], [100, 336], [77, 341, 1], [92, 349], [114, 349], [156, 352], [212, 356]] },
  { pal: 'dip', b: [212, 318], ax: [140, 312], t: [86, 324], shaft: true, pts: [[212, 300], [164, 299], [124, 302], [104, 311], [86, 324, 1], [99, 332], [120, 334], [164, 336], [212, 338]],
    extra: shape('M168 306 C146 306 126 310 110 318 C128 314 148 312 170 312 Z', '#fff0a8', 0.5) },
];
const TL_ROOT = [[262, 334], [214, 318], [196, 340], [196, 400], [214, 440], [250, 462], [272, 430]];

// --- l'aile droite : trois grandes plumes vers le haut à droite, les couvertures, la frange sous le bras ---
const WR = [
  // la frange de plumes lie-de-vin qui pend sous le bras
  pl('wine', [362, 306], [369, 335], 15, -1), pl('wine', [380, 308], [384, 339], 16, -1), pl('wine', [396, 310], [399, 344], 17, -1),
  pl('wine', [412, 312], [414, 347], 17, 0), pl('wine', [428, 312], [428, 345], 16, 1),
  // les trois grandes plumes
  { pal: 'primR', b: [474, 243], ax: [505, 195], t: [532, 163], shaft: true, pts: [[462, 236], [486, 204], [504, 180], [518, 167], [532, 163, 1], [527, 182], [518, 202], [504, 224], [486, 250]] },
  { pal: 'primR', b: [465, 222], ax: [505, 140], t: [539, 67], shaft: true, pts: [[452, 218], [478, 172], [503, 126], [524, 90], [539, 67, 1], [537, 88], [531, 108], [526, 124], [520, 140], [512, 160], [497, 190], [478, 226]] },
  { pal: 'primR', b: [448, 211], ax: [488, 112], t: [534, 10], shaft: true, pts: [[436, 208], [450, 162], [468, 120], [486, 84], [503, 54], [520, 28], [534, 10, 1], [536, 33], [531, 58], [524, 84], [514, 112], [500, 145], [482, 180], [460, 214]],
    extra: shape('M531 20 C522 44 508 76 490 112 C506 80 520 48 528 22 Z', '#fff4c8', 0.55) },
  // les couvertures, pointes vers le haut à droite
  pl('covR', [408, 300], [454, 284], 22, -2), pl('covR', [414, 280], [464, 254], 26, -2),
  pl('covR', [420, 258], [472, 222], 28, -3), pl('covR', [426, 236], [480, 188], 28, -3),
  pl('covR', [430, 212], [478, 150], 26, -3), pl('covR', [404, 254], [442, 206], 24, -2), pl('covR', [410, 230], [446, 170], 24, -2),
  // les petites couvertures du bord d'attaque : leurs pointes, comme des flammes, font les crans du bord
  pl('covR', [520, 122], [502, 48], 14, 3), pl('covR', [500, 150], [475, 76], 15, 3),
  pl('covR', [480, 176], [448, 103], 16, 3), pl('covR', [462, 202], [422, 131], 17, 3),
];
const WR_ROOT = [[366, 304], [378, 232], [394, 172], [412, 150], [440, 150], [462, 170], [474, 210], [474, 300], [430, 316]];

// ---------- les silhouettes ----------
// le corps
const S = {
  tail: silhouette([TL_ROOT, ...TL.map((f) => f.pts)]),
  wingL: silhouette([WL_ROOT, ...WL.map((f) => f.pts)]),
  wingR: silhouette([WR_ROOT, ...WR.map((f) => f.pts)]),
  // la chevelure de derrière : du sommet de la tête jusqu'aux épaules
  hairB: P([[300, 64], [268, 72], [240, 88], [218, 108], [204, 128], [196, 146], [192, 168], [195, 192], [199, 218],
    [204, 244], [208, 266], [212, 284, 1], [222, 280], [230, 296, 1], [240, 290], [254, 302, 1], [270, 294], [290, 292],
    [304, 280], [338, 280], [366, 294], [384, 296, 1], [392, 286], [404, 290, 1], [406, 272], [413, 238], [412, 198],
    [406, 162], [396, 136], [382, 112], [362, 92], [336, 74]]),
  // les pattes : voir plus bas (tarse, doigts et griffes réunis en une seule silhouette)
  // la jupe de plumes : dessous orange, dessus blanc
  skirtU: P([[226, 388], [228, 420], [236, 444], [250, 456], [266, 446], [286, 436], [306, 434], [330, 434], [350, 442],
    [366, 448], [382, 432], [394, 410], [380, 392], [350, 380], [300, 376], [256, 380]]),
  skirt: P([[262, 357], [354, 357], [366, 370], [380, 384], [392, 401, 1], [380, 404], [389, 418, 1], [372, 416], [360, 430],
    [350, 436, 1], [342, 432], [336, 449, 1], [326, 440], [314, 453, 1], [304, 440], [296, 448, 1], [289, 433], [278, 437, 1],
    [270, 426], [258, 430, 1], [252, 414], [238, 414, 1], [240, 402], [226, 397, 1], [238, 386], [248, 372]]),
  // le buste : robe blanche ; le cou
  neck: P([[296, 252], [342, 252], [340, 272], [346, 290], [318, 300], [290, 290], [296, 272]]),
  torso: P([[276, 280], [296, 291], [318, 296], [340, 290], [352, 281], [354, 300], [351, 322], [349, 342], [352, 362],
    [268, 364], [271, 344], [273, 322], [271, 300]]),
  belt: P([[271, 349, 1], [300, 351], [318, 352], [336, 350], [349.5, 347, 1], [352, 360, 1], [336, 363], [318, 364.5], [300, 364], [267, 362, 1]]),
  clasp: P([[306, 350], [318, 347, 1], [331, 350], [330, 362], [319, 378, 1], [308, 362]]),
  // le bras gauche (main ouverte, basse) et le bras droit (poing levé)
  armL: P([[266, 290], [276, 302], [270, 322], [248, 332], [226, 342], [208, 352], [196, 357], [190, 343], [204, 330],
    [224, 316], [246, 302]]),
  cuffL: P([[185, 336], [198, 328], [211, 321], [218, 330], [224, 346], [213, 355], [200, 363], [191, 352]]),
  handL: P([[194, 340], [180, 339], [166, 340], [154, 342], [147, 344], [143, 347.5], [144, 351], [148, 352.5], [154, 353, 1],
    [146, 355], [140, 358], [140, 362], [145, 364], [152, 364.5, 1], [145, 367], [141, 370], [142, 374], [147, 375], [154, 375, 1],
    [148, 378], [147, 381], [151, 383], [158, 382], [167, 377], [175, 372, 1], [177, 380], [181, 388], [186, 392], [190, 390],
    [192, 380], [194, 368], [198, 357]]),
  armR: P([[346, 288], [376, 290], [406, 293], [408, 323], [380, 323], [358, 320], [344, 310]]),
  cuffR: P([[402, 296], [428, 291], [450, 289], [457, 298], [458, 318], [452, 332], [430, 333], [404, 327]]),
  fist: P([[455, 292], [461, 284], [470, 280], [481, 278], [493, 277], [503, 280], [509, 286], [508.5, 292.5, 1], [511, 299],
    [508.5, 305.5, 1], [510, 312], [505.5, 318, 1], [504, 324], [497, 330], [485, 334], [470, 334], [459, 328], [454, 316],
    [453, 302]]),
  // la boule de feu : seulement un petit point caché dans le poing (le feu n'a pas de contour sombre)
  fire: 'M478 312a3 3 0 1 0 6 0a3 3 0 1 0 -6 0Z',
  // les épaules : des plumes blanches posées sur le haut des bras
  shL: P([[244, 278], [262, 271], [278, 274], [286, 284], [282, 296], [270, 303], [258, 307, 1], [252, 301], [240, 309, 1],
    [234, 302], [222, 306, 1], [222, 298], [212, 298, 1], [224, 288]]),
  shR: P([[338, 276], [354, 268], [370, 268], [383, 276], [392, 283, 1], [380, 284], [392, 292, 1], [378, 292], [384, 300, 1],
    [368, 297], [360, 303, 1], [350, 296], [340, 290]]),
  // la tête
  ear: P([[242, 186], [232, 183], [221, 187], [214, 197], [213, 211], [216, 223], [224, 232], [234, 236], [244, 230]]),
  face: P([[262, 150], [262, 190], [264, 222], [270, 244], [282, 257], [300, 267], [322, 271], [344, 267], [362, 258],
    [376, 245], [384, 228], [387, 205], [387, 175], [383, 145], [360, 118], [320, 110], [280, 118]]),
  lockL: P([[262, 150], [270, 168], [268, 196], [266, 222], [268, 242], [258, 254, 1], [250, 240], [243, 214], [242, 188],
    [246, 164]]),
  lockR: P([[380, 140], [394, 152], [401, 176], [404, 204], [404, 232], [400, 256], [394, 270, 1], [388, 252], [388, 226],
    [388, 196], [385, 170]]),
  cap: P([[204, 132], [216, 110], [234, 93], [252, 83], [262, 76], [266, 68, 1], [278, 63], [292, 59], [304, 62],
    [312, 72], [326, 72], [344, 80], [364, 92], [382, 110], [394, 132], [398, 152], [392, 166, 1], [384, 172],
    [376, 154], [362, 138], [348, 130], [337, 128, 1], [324, 134], [308, 147], [296, 162], [286, 178], [276, 194, 1],
    [268, 190], [258, 176], [246, 164], [232, 160], [216, 152]]),
  tiara: P([[238, 150, 1], [243, 140], [251, 131], [255, 123], [262, 99, 1], [276, 110], [290, 117, 1], [300, 95, 1],
    [311, 107, 1], [312, 80], [318, 43, 1], [327, 55], [336, 71], [345, 88], [352, 101, 1], [357, 98], [364, 84, 1],
    [369, 94, 1], [375, 87, 1], [381, 104], [391, 113], [398, 124], [402, 135], [402.5, 144, 1], [397, 139], [388, 130],
    [376, 122], [362, 117], [350, 118], [344, 128], [338, 142, 1], [332, 128], [326, 119], [314, 116], [300, 118],
    [282, 124], [264, 133], [248, 143]]),
};

// ---------- les yeux ----------
/**
 * Un œil : blanc, iris ambre en dégradé, pupille, ombre de la paupière, reflets ; puis les cils (une forme pleine qui
 * s'étire en trait d'eye-liner vers l'extérieur) et la paupière du bas. `shut` = la courbe de l'œil fermé (clignement).
 */
function eye(key, white, cx, cy, r, lash, lower, shut) {
  return `<clipPath id="c-${key}"><path id="w-${key}" d="${white}"/></clipPath>`
    + `<use href="#w-${key}" fill="#fffaf6"/>`
    + `<g clip-path="url(#c-${key})">`
    + `<circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#g-iris)"/>`
    + `<circle cx="${cx}" cy="${cy}" r="${n(r - 0.7)}" fill="none" stroke="#5a200c" stroke-width="1.4"/>`
    + oval(cx, n(cy - r * 0.18), n(r * 0.6), n(r * 0.64), '#2a0d08')
    + `<path d="M${n(cx - r * 0.66)} ${n(cy + r * 0.5)} A${n(r * 0.82)} ${n(r * 0.82)} 0 0 0 ${n(cx + r * 0.66)} ${n(cy + r * 0.5)}" fill="none" stroke="#ffc46e" stroke-width="1.6" opacity="0.6"/>`
    + `<rect x="${cx - r - 22}" y="${n(cy - r - 10)}" width="${2 * r + 44}" height="${n(r * 1.45)}" fill="url(#g-lid)"/>`
    + oval(n(cx - r * 0.4), n(cy - r * 0.34), n(r * 0.3), n(r * 0.24), '#fff', 1, -20)
    + dot(n(cx + r * 0.4), n(cy - r * 0.18), n(r * 0.15), '#fff', 0.95)
    + `</g>`
    + shape(lash, '#24100e') + shape(lower, '#5a2418', 0.9)
    + `<g class="a-blink" opacity="0"><use href="#w-${key}" fill="#f5c3ac" stroke="#f5c3ac" stroke-width="3"/>${line(shut, '#24100e', 3.2)}</g>`;
}


// ---------- les pattes ----------
/** Un doigt d'oiseau : de sa base `b` à son bout `t` (largeur w0 → w1), deux phalanges bombées et un bout arrondi. */
function toe(b, t, w0, w1) {
  const dx = t[0] - b[0], dy = t[1] - b[1], len = Math.hypot(dx, dy), ux = dx / len, uy = dy / len, vx = -uy, vy = ux;
  const pt = (s, o) => [b[0] + ux * len * s + vx * o, b[1] + uy * len * s + vy * o];
  const side = (k) => [pt(-0.1, k * w0 / 2), pt(0.28, k * (w0 / 2 + 1.2)), pt(0.5, k * ((w0 + w1) / 4 - 0.4)), pt(0.72, k * (w1 / 2 + 1.4)),
    pt(0.94, k * w1 / 2)];
  return [...side(1), pt(1.05, w1 * 0.25), pt(1.09, 0), pt(1.05, -w1 * 0.25), ...side(-1).reverse()];
}
/** Une griffe recourbée : de la base (bout du doigt) vers la pointe ; `w` = épaisseur à la base, `bend` = courbure. */
function talon(b, t, w, bend) {
  const dx = t[0] - b[0], dy = t[1] - b[1], len = Math.hypot(dx, dy), ux = dx / len, uy = dy / len, vx = -uy, vy = ux;
  const pt = (s, o) => [b[0] + ux * len * s + vx * (o + bend * Math.sin(Math.PI * s * 0.9)), b[1] + uy * len * s + vy * (o + bend * Math.sin(Math.PI * s * 0.9))];
  return [pt(-0.2, w * 0.5), pt(0.4, w * 0.42), pt(0.78, w * 0.2), [...pt(1, 0), 1], pt(0.7, -w * 0.18), pt(0.3, -w * 0.4), pt(-0.2, -w * 0.5)];
}
const LEG_L = { tarsus: [[237, 420], [268, 420], [267, 444], [262, 462], [257, 474], [243, 480], [231, 474], [229, 458], [233, 440]],
  toes: [toe([236, 458], [180, 485], 17, 12.5), toe([240, 466], [200, 494], 17, 12.5), toe([248, 470], [219, 497], 16, 12), toe([257, 458], [262, 485], 14, 11)],
  claws: [talon([180, 485], [166, 502], 11, -2.5), talon([200, 493], [191, 510], 11, -2), talon([218, 496], [207, 509], 10, -2), talon([262, 484], [268, 502], 10, 2)] };
const LEG_R = { tarsus: [[345, 420], [384, 420], [386, 440], [391, 455], [396, 466], [381, 474], [361, 474], [352, 460], [348, 440]],
  toes: [toe([387, 458], [444, 481], 17, 12.5), toe([384, 466], [426, 490], 17, 12.5), toe([376, 470], [406, 494], 16, 12), toe([359, 458], [351, 484], 14, 11)],
  claws: [talon([443, 482], [459, 500], 11, 2.5), talon([425, 490], [436, 507], 11, 2), talon([405, 493], [410, 509], 10, 1.5), talon([351, 483], [345, 501], 10, -2)] };
S.legL = [LEG_L.tarsus, ...LEG_L.toes, ...LEG_L.claws].map((p) => L(p)).join('');
S.legR = [LEG_R.tarsus, ...LEG_R.toes, ...LEG_R.claws].map((p) => L(p)).join('');
const legDefs = [];
/** Le dessin d'une patte : tarse en dégradé, doigts (chacun écrit une fois, réutilisé), un pli à chaque doigt, griffes nacrées. */
function legBody(id, leg, grad, front) {
  const r = Math.round;
  const toes = leg.toes.map((t, i) => {
    legDefs.push(`<path id="${id}t${i}" d="${P(t, true, 0)}"/>`);
    const u = (a) => `<use href="#${id}t${i}"${a}/>`;
    return u(' x="-1.5" y="2.5" fill="#6a3a0a" opacity=".35"') + u(' fill="url(#g-toe)" stroke="#8a5414" stroke-width="1.3" stroke-opacity=".55"');
  }).join('');
  // un pli au milieu de chaque doigt (la phalange) et un reflet sur le dessus
  const folds = leg.toes.map((t) => {
    const m0 = t[2], m1 = t[t.length - 3];
    return `M${r(m0[0])} ${r(m0[1])}Q${r((m0[0] + m1[0]) / 2 + 1.5)} ${r((m0[1] + m1[1]) / 2 + 1.5)} ${r(m1[0])} ${r(m1[1])}`;
  }).join('');
  const shine = leg.toes.map((t) => `M${r(t[1][0])} ${r(t[1][1] - 1)}L${r(t[3][0])} ${r(t[3][1] - 1)}`).join('');
  const claws = leg.claws.map((c) => P(c, true, 0)).join('');
  const glint = leg.claws.map((c) => `M${r(c[1][0])} ${r(c[1][1])}Q${r((c[1][0] + c[3][0]) / 2 + 1)} ${r((c[1][1] + c[3][1]) / 2)} ${r(c[3][0])} ${r(c[3][1])}`).join('');
  return clip(id, toes + shape(P(leg.tarsus, true, 0), grad) + line(folds, '#8a5414', 1.4, 0.5) + line(shine, '#fff0b8', 1.5, 0.5)
    // le côté du tarse dans l'ombre, le reflet sur le devant
    + shape(front, '#fff0b8', 0.5)
    + `<rect x="${leg.tarsus[0][0] - 60}" y="484" width="160" height="30" fill="#7a4810" opacity="0.18"/>`)
    + shape(claws, 'url(#g-claw)') + line(glint, '#ffffff', 1.2, 0.85);
}

// ---------- la jupe : rangs de plumes blanches, et les plumes de feu du dessous ----------
PAL.white = { base: '#d8cce6', mid: '#f6f1f8', tip: '#ffffff', edge: '#a894c4', light: '#ffffff', shaft: '#b6a6cc' };
PAL.under = { base: '#b4441a', mid: '#ee8a3c', tip: '#ffcc7c', edge: '#963616', light: '#ffe2a6', shaft: '#b85a26' };
const SKIRT_U = [
  pl('under', [252, 390], [231, 446], 30, -3), pl('under', [268, 398], [255, 455], 26, -2),
  pl('under', [356, 398], [367, 450], 28, 2), pl('under', [372, 392], [389, 438], 28, 3),
];
const SKIRT = [
  // le rang du bas : ses pointes font l'ourlet (les plus longues au milieu, elles s'écartent sur les côtés)
  pl('white', [252, 384], [227, 400], 17, -2), pl('white', [264, 392], [243, 418], 18, -2), pl('white', [278, 398], [262, 433], 20, -2),
  pl('white', [292, 400], [289, 447], 19, -1), pl('white', [306, 402], [304, 452], 18, 0), pl('white', [321, 402], [319, 456], 20, 1),
  pl('white', [335, 400], [339, 449], 18, 1), pl('white', [349, 398], [353, 437], 20, 2), pl('white', [362, 394], [375, 420], 18, 2),
  pl('white', [372, 388], [393, 404], 17, 2),
  // le rang du milieu
  pl('white', [257, 374], [233, 393], 18, -2), pl('white', [270, 380], [255, 409], 20, -2), pl('white', [286, 384], [280, 421], 21, -1),
  pl('white', [302, 386], [301, 429], 20, 0), pl('white', [318, 386], [323, 431], 21, 1), pl('white', [334, 384], [341, 424], 20, 1),
  pl('white', [350, 380], [361, 411], 20, 2), pl('white', [363, 376], [384, 397], 18, 2),
  // le rang du haut, sous la ceinture
  pl('white', [272, 362], [262, 389], 22, -1), pl('white', [290, 364], [288, 395], 22, -1), pl('white', [309, 366], [311, 399], 24, 0),
  pl('white', [328, 364], [333, 397], 22, 1), pl('white', [346, 362], [355, 390], 22, 1),
];
const SKIRT_TOP = [[260, 352], [356, 352], [372, 374], [360, 386], [262, 386], [246, 374]];
S.skirtU = silhouette(SKIRT_U.map((f) => f.pts));
S.skirt = silhouette([SKIRT_TOP, ...SKIRT.map((f) => f.pts)]);

// ---------- dégradés ----------
const baseDefs = [
  lin('g-hairB', 0, 70, 0, 302, [[0, '#e8501f'], [0.45, '#c42e1c'], [1, '#86161a']]),
  lin('g-hair', 0, 0, 0, 1, [[0, '#ff7a3a'], [0.5, '#f2602a'], [1, '#d4401f']], false),
  lin('g-skin', 0, 0, 0, 1, [[0, '#ffe6d6'], [0.6, SKIN.base], [1, '#f2b9a2']], false),
  lin('g-armL', 0, 290, 0, 360, [[0, '#ffe4d2'], [0.55, SKIN.base], [1, '#eaa892']]),
  lin('g-armR', 0, 286, 0, 334, [[0, '#ffe8d8'], [0.55, SKIN.base], [1, '#eaa892']]),
  lin('g-gold', 0, 0, 0, 1, [[0, GOLD.hi], [0.4, GOLD.base], [1, GOLD.shade]], false),
  lin('g-tiara', 0, 44, 0, 150, [[0, '#fff4b0'], [0.45, '#f2cc5a'], [1, '#c98a24']]),
  lin('g-legL', 230, 0, 268, 0, [[0, '#84480e'], [0.5, '#bf8026'], [1, '#e6b048']]),
  lin('g-legR', 348, 0, 392, 0, [[0, '#84480e'], [0.5, '#bf8026'], [1, '#e6b048']]),
  lin('g-toe', 0, 462, 0, 500, [[0, '#dea23c'], [1, '#985a14']]),
  lin('g-white', 0, 0, 0, 1, [[0, '#ffffff'], [0.6, WHITE.base], [1, WHITE.shade]], false),
  lin('g-torso', 264, 0, 358, 0, [[0, '#cbbad8'], [0.3, '#f1ebf4'], [0.7, '#ffffff'], [1, '#f4eef6']]),
  lin('g-claw', 0, 0, 0, 1, [[0, '#f4f0f8'], [0.45, '#c8bcd6'], [1, '#7a6a8c']], false),
  lin('g-cuffL', 0, 0, 1, 0, [[0, '#8a3a12'], [0.5, '#c0601e'], [1, '#e08a36']], false),
  lin('g-cuffR', 0, 0, 0, 1, [[0, '#7a3a16'], [0.5, '#4e1e0a'], [1, '#2e1006']], false),
  rad('g-iris', 0.5, 0.9, 0.85, [[0, '#f8b45a'], [0.3, '#e07a26'], [0.62, '#93401a'], [1, '#4a160a']], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#3a1408', 0.7], [0.55, '#3a1408', 0]], false),
  rad('g-blush', 0.5, 0.5, 0.5, [[0, '#ff8a6e', 0.5], [1, '#ff8a6e', 0]], false),
  rad('g-faceSh', 0.78, 0.28, 0.95, [[0, '#fff3ea', 0], [0.62, '#fff3ea', 0], [1, '#d88a78', 0.55]], false),
  rad('g-soft', 0.5, 0.5, 0.5, [[0, '#fff6ee', 0.85], [1, '#fff6ee', 0]], false),
  // les lumières d'ensemble des ailes
  rad('g-wlGlow', 0.5, 0.5, 0.5, [[0, '#ffe680', 0.42], [0.6, '#ffd060', 0.16], [1, '#ffd060', 0]], false),
  rad('g-wlRoot', 0.5, 0.5, 0.5, [[0, '#8a1408', 0.5], [1, '#8a1408', 0]], false),
  rad('g-wrGlow', 0.5, 0.5, 0.5, [[0, '#ffd070', 0.3], [1, '#ffd070', 0]], false),
  rad('g-wrRoot', 0.5, 0.5, 0.5, [[0, '#7a0c10', 0.45], [1, '#7a0c10', 0]], false),
  // le feu : halo, flamme, cœur
  rad('g-halo', 0.5, 0.5, 0.5, [[0, '#ffe080', 0.85], [0.45, '#ffa030', 0.4], [1, '#ff7a20', 0]], false),
  lin('g-flame', 0, 284, 0, 196, [[0, '#f0581a'], [0.4, '#fb8a26'], [1, '#ffae3a']]),
  lin('g-flame2', 0, 280, 0, 206, [[0, '#ffbe44'], [0.55, '#ffdc68'], [1, '#fff0a0']]),
  rad('g-core', 495, 248, 27, [[0, '#ffffff'], [0.55, '#fffbe4'], [1, '#fff3b0', 0]]),
  rad('g-blast', 0.3, 0.5, 0.7, [[0, '#fffbe0', 0.95], [0.4, '#ffc040', 0.75], [1, '#ff6a1c', 0]], false),
];

// ---------- les morceaux, du fond vers le devant ----------
const parts = [
  // --- la traîne et les deux ailes, derrière tout ---
  { id: 'tail', cls: 'a-tail', d: S.tail, body: clip('tail', shape(L(TL_ROOT), '#8a2014') + TL.map(feather).join('')) },
  { id: 'wingL', cls: 'a-wl', d: S.wingL, shadow: [{ on: ['tail'], dx: -5, dy: 5, color: SH.fea, o: 0.35 }],
    body: clip('wingL', shape(L(WL_ROOT), '#d04a1a') + WL.map(feather).join('')
      + `<ellipse cx="118" cy="196" rx="112" ry="92" fill="url(#g-wlGlow)"/><ellipse cx="236" cy="286" rx="70" ry="60" fill="url(#g-wlRoot)"/>`) },
  { id: 'wingR', cls: 'a-wr', d: S.wingR, body: clip('wingR', shape(L(WR_ROOT), '#c03020') + WR.map(feather).join('')
      + `<ellipse cx="490" cy="150" rx="70" ry="110" fill="url(#g-wrGlow)"/><ellipse cx="400" cy="268" rx="56" ry="60" fill="url(#g-wrRoot)"/>`) },

  // --- la chevelure de derrière ---
  { id: 'hairB', cls: 'a-hairB', d: S.hairB, shadow: [{ on: ['wingL', 'wingR'], dx: -6, dy: 5, color: SH.fea, o: 0.42 }],
    body: use('hairB', 'url(#g-hairB)') + clip('hairB',
      // de grandes mèches : un creux sombre entre elles, une lumière sur leur dos
      shape('M214 140 C204 170 204 210 210 246 C213 264 218 276 224 286 C220 266 218 240 219 210 C220 182 224 160 230 146 Z', HAIR.line, 0.45)
      + shape('M236 140 C228 170 228 206 234 240 C238 260 244 276 252 292 C248 266 245 236 246 206 C247 180 250 158 256 142 Z', HAIR.lite, 0.4)
      + shape('M222 120 C212 140 206 164 206 190 C210 166 218 144 230 126 Z', HAIR.hi, 0.35)
      // à droite, derrière la tresse
      + shape('M398 150 C406 180 408 214 404 248 C402 266 398 280 392 292 C398 270 400 244 400 216 C400 190 398 168 392 150 Z', HAIR.line, 0.45)
      + shape('M404 160 C410 186 412 214 410 240 C408 214 406 188 400 166 Z', HAIR.lite, 0.4)
    ) },

  // --- les pattes ---
  { id: 'legL', d: S.legL, rim: { on: ['tail'], color: '#4a1208', w: 1.2, o: 0.75 }, shadow: [{ on: ['tail'], dx: -4, dy: 4, color: SH.fea, o: 0.35 }], body: legBody('legL', LEG_L, 'url(#g-legL)', 'M257 424 C261 440 259 456 253 470 L249 470 C254 456 255 440 252 424 Z') },
  { id: 'legR', d: S.legR, body: legBody('legR', LEG_R, 'url(#g-legR)', 'M371 424 C375 440 380 456 388 468 L384 470 C376 456 371 440 367 424 Z') },

  // --- la jupe : les plumes de feu du dessous, puis les plumes blanches ---
  { id: 'skirtU', d: S.skirtU, shadow: [{ on: ['legL', 'legR'], dx: -3, dy: 6, color: '#6a3a08', o: 0.4 }],
    body: clip('skirtU', SKIRT_U.map(feather).join('')) },
  { id: 'skirt', d: S.skirt, shadow: [{ on: ['legL', 'legR'], dx: -3, dy: 7, color: '#6a3a08', o: 0.45 }, { on: ['skirtU', 'tail'], dx: -3, dy: 6, color: SH.fea, o: 0.4 }],
    body: clip('skirt', shape(L(SKIRT_TOP), '#e8e0ee') + SKIRT.map(feather).join('')) },

  // --- le cou et le buste ---
  { id: 'neck', d: S.neck, shadow: [{ on: ['hairB'], dx: -4, dy: 4, color: SH.hair, o: 0.35 }],
    body: use('neck', 'url(#g-skin)') + clip('neck', shape('M290 250 L346 250 L346 276 C334 284 306 284 290 276 Z', SKIN.shade, 0.75)) },
  { id: 'torso', d: S.torso, shadow: [{ on: ['hairB', 'wingL', 'wingR'], dx: -5, dy: 4, color: SH.fea, o: 0.35 }],
    body: use('torso', 'url(#g-torso)') + clip('torso',
      // la poitrine : deux rondeurs, l'ombre sous chacune et entre elles, la lumière en haut à droite
      shape('M276 318 C284 326 300 328 314 322 C304 332 288 334 276 328 Z', '#b8a4cc', 0.5)
      + shape('M322 322 C330 328 342 328 350 320 C346 332 334 334 322 330 Z', '#b8a4cc', 0.45)
      + oval(340, 306, 9, 7, '#ffffff', 0.95)
      + shape('M318 302 C315 312 316 322 320 330 C322 320 322 310 318 302 Z', '#b8a4cc', 0.55)
      // le ventre : deux grandes plumes douces, à peine marquées
      + shape('M286 336 C296 332 306 334 312 340 C304 340 296 342 288 346 Z', '#c8b8da', 0.55)
      + shape('M324 340 C330 334 340 332 348 336 C342 340 334 342 326 346 Z', '#c8b8da', 0.5)
      // l'encolure : une petite rangée de plumes au bord du tissu, pas toutes pareilles
      + shape('M272 288 C278 296 288 300 296 296 C290 304 280 304 272 298 Z', '#d6c8e2', 0.85)
      + shape('M296 296 C303 304 312 306 318 302 C312 310 302 310 296 304 Z', '#d6c8e2', 0.85)
      + shape('M318 302 C325 306 334 304 340 296 C337 306 328 310 318 308 Z', '#d6c8e2', 0.75)
      + shape('M340 296 C346 300 352 296 356 288 C356 298 350 304 340 302 Z', '#d6c8e2', 0.7)
      // le côté gauche dans l'ombre, sous le bras
      + shape('M266 300 C272 320 272 342 268 364 L284 364 C286 344 285 322 279 302 Z', '#a894c4', 0.45)
      // le collier d'or, ses perles, sa pierre
      + line('M280 286 C292 296 306 302 318 302 C330 302 344 294 352 284', GOLD.line, 4.2, 0.9)
      + line('M280 286 C292 296 306 302 318 302 C330 302 344 294 352 284', GOLD.base, 2.6, 1)
      + line('M282 285.5 C293 294.5 306 300 318 300.2', GOLD.hi, 1, 0.8)
      + dot(288, 292.5, 2.2, GOLD.hi) + dot(301, 299, 2.2, GOLD.hi) + dot(336, 298.5, 2.2, GOLD.hi) + dot(347, 290.5, 2.2, GOLD.hi)
    )
    + shape('M318 297 L326 304 L319 318 L311 305 Z', GOLD.shade)
    + shape('M318 300 L323.5 305 L318.6 315 L313.4 305.4 Z', '#f06a1c') + shape('M318 300 L318.6 315 L313.4 305.4 Z', '#ffb050')
    + shape('M316.6 303 L318 301.4 L318.2 306 Z', '#ffffff', 0.9) },
  { id: 'belt', d: S.belt, shadow: [{ on: ['torso', 'skirt'], dx: -2, dy: 5, color: SH.white, o: 0.4 }],
    body: use('belt', 'url(#g-gold)') + clip('belt',
      // le haut de la ceinture éclairé, le bas dans l'ombre, le côté gauche (tourné vers l'ombre) plus sombre
      shape('M268 349 C290 352 318 354 350 347 L351 352 C318 358 290 356 268 353 Z', GOLD.hi, 0.85)
      + shape('M266 359 C292 363 318 365 352 358 L353 366 L266 366 Z', GOLD.shade, 0.65)
      + `<rect x="262" y="344" width="22" height="24" fill="${GOLD.shade}" opacity="0.4"/>`
      // deux petits rivets de chaque côté de la boucle
      + dot(296, 357, 1.8, GOLD.line, 0.7) + dot(296, 356.4, 0.8, GOLD.hi) + dot(341, 355.5, 1.8, GOLD.line, 0.7) + dot(341, 354.9, 0.8, GOLD.hi)) },
  { id: 'clasp', d: S.clasp, shadow: [{ on: ['belt', 'skirt'], dx: -2, dy: 5, color: SH.gold, o: 0.4 }],
    body: use('clasp', 'url(#g-gold)')
      + shape('M318 347 L331 350 L330 362 L319 378 Z', GOLD.base) + shape('M318 347 L319 378 L308 362 L306 350 Z', GOLD.mid)
      + shape('M318 353 L324 357 L319 367 L313 357 Z', '#f06a1c') + shape('M318 353 L319 367 L313 357 Z', '#ffb050')
      + line('M321 349 L329 352', GOLD.hi, 1.4, 0.9) },

  // --- le bras gauche, main ouverte vers le bas ---
  { id: 'armL', cls: 'a-armL', d: S.armL, rim: { on: ['tail', 'wingL'], color: '#4a1208', w: 1.3, o: 0.8 }, shadow: [{ on: ['wingL', 'tail', 'hairB'], dx: -5, dy: 5, color: SH.fea, o: 0.38 }, { on: ['torso'], dx: -3, dy: 4, color: SH.white, o: 0.4 }],
    body: use('armL', 'url(#g-armL)') + clip('armL',
      shape('M276 306 C266 318 250 328 230 338 C220 344 208 350 196 356 L200 362 L280 330 Z', SKIN.shade, 0.6)
      + shape('M250 302 C238 310 224 318 212 328 C226 322 240 314 254 306 Z', SKIN.hi, 0.8)) },
  { id: 'cuffL', cls: 'a-armL', d: S.cuffL, shadow: [{ on: ['armL'], dx: -2, dy: 3, color: SH.skin, o: 0.35 }],
    rim: { on: ['tail', 'wingL'], color: '#4a1208', w: 1.3, o: 0.8 },
    body: use('cuffL', 'url(#g-cuffL)') + clip('cuffL',
      // le cuir fauve : un reflet en longueur sur le dessus, l'ombre dessous, un liseré clair à chaque bout
      shape('M190 336 C200 330 208 326 214 324 C206 331 198 336 192 341 Z', '#ffcf8a', 0.85)
      + shape('M196 360 C204 356 212 352 222 347 L226 352 L200 368 Z', '#6a2a0c', 0.55)
      + line('M186 337 C190 345 193 353 199 362', '#ffd8a0', 1.6, 0.7) + line('M211 322 C215 330 219 338 223 346', '#8a3a10', 1.6, 0.6)) },
  { id: 'handL', cls: 'a-armL', d: S.handL, rim: { on: ['tail', 'wingL'], color: '#4a1208', w: 1.3, o: 0.85 }, shadow: [{ on: ['tail', 'wingL'], dx: -4, dy: 5, color: SH.fea, o: 0.4 }],
    body: use('handL', 'url(#g-armL)') + clip('handL',
      // le dessous des doigts et du pouce dans l'ombre, la lumière sur le dos de la main
      shape('M196 362 C186 370 176 376 160 382 L150 390 L200 394 Z', SKIN.shade, 0.5)
      + shape('M190 341 C176 340 162 341 150 345 C162 344 176 344 188 346 Z', SKIN.hi, 0.9)
      + oval(176, 352, 10, 6, 'url(#g-soft)', 0.8, -8))
    // les doigts : un pli entre chacun (il part du creux entre deux doigts), le pli du pouce
    + line('M154 353 C160 352.5 166 352.5 172 353.5', SKIN.line, 1.5, 0.85)
    + line('M152 364.5 C158 363.5 164 362.5 170 362.5', SKIN.line, 1.5, 0.85)
    + line('M154 375 C159 373.5 164 372 170 370.5', SKIN.line, 1.5, 0.85)
    + line('M175 372 C178 366 182 362 188 360', SKIN.line, 1.4, 0.7) },
  // les plumes blanches de l'épaule gauche
  { id: 'shL', d: S.shL, shadow: [{ on: ['armL', 'torso', 'hairB', 'wingL'], dx: -3, dy: 5, color: SH.white, o: 0.4 }],
    body: use('shL', 'url(#g-white)') + clip('shL',
      // trois plumes qui se recouvrent, chacune avec son ombre ; le haut éclairé et teinté de rose par le feu
      shape('M212 298 C224 292 238 292 250 296 L240 309 L234 302 L222 306 L222 298 Z', '#b9a6d0', 0.75)
      + shape('M226 290 C238 284 252 284 264 290 C252 290 240 292 230 296 Z', '#d8c8e6', 0.9)
      + shape('M244 280 C256 274 270 272 282 278 C270 278 258 282 248 286 Z', '#ffffff')
      + shape('M250 276 C262 271 276 272 284 280 C276 276 264 275 254 279 Z', '#ffd8c8', 0.7)
      + line('M232 300 C244 294 256 292 268 294', '#a894c4', 1.3, 0.75) + line('M248 288 C258 284 268 284 278 288', '#a894c4', 1.2, 0.6)) },
  // --- la boule de feu (dans la main droite) : halo, flamme, cœur blanc, braises ---
  { id: 'fire', cls: 'a-armR', d: S.fire,
    body: `<ellipse cx="499" cy="232" rx="78" ry="62" fill="url(#g-halo)"/>`
      + `<g class="a-fire">`
      // la flamme orange : ronde en bas, une couronne de langues qui penchent vers la droite
      + shape(P([[491, 284], [474, 280], [461, 270], [453, 256], [452, 241], [456, 228], [460, 219], [462, 209, 1], [468, 216],
        [472, 222], [476, 212], [480, 202, 1], [485, 211], [489, 218], [494, 207], [499, 196, 1], [504, 207], [508, 214], [514, 206],
        [520, 198, 1], [523, 209], [527, 216], [533, 212], [541, 208, 1], [540, 222], [543, 236], [542, 252], [536, 265], [524, 276],
        [508, 283]]), 'url(#g-flame)')
      // la flamme jaune, dedans
      + `<g class="a-flame2">` + shape(P([[492, 281], [475, 277], [463, 267], [457, 253], [458, 238], [462, 227], [466, 219, 1],
        [472, 226], [477, 222], [482, 211, 1], [488, 220], [494, 214], [499, 204, 1], [505, 215], [511, 217], [517, 207, 1], [522, 218],
        [529, 222], [535, 220, 1], [535, 234], [535, 250], [530, 263], [519, 274], [505, 280]]), 'url(#g-flame2)') + `</g>`
      // le cœur blanc
      + `<g class="a-core"><ellipse cx="495" cy="248" rx="27" ry="25" fill="url(#g-core)"/>`
      + shape(P([[493, 273], [481, 267], [476, 255], [478, 244], [482, 237], [486, 231, 1], [491, 240], [496, 236], [501, 227, 1],
        [505, 238], [510, 246], [512, 257], [507, 267]]), '#fffdf0', 0.92) + `</g>`
      // la petite langue de feu qui sort du poing
      + shape(P([[487, 284], [483, 271], [488, 260, 1], [491, 268], [495, 254, 1], [498, 268], [496, 284]]), '#f2601c', 0.9)
      + `</g>`
      // les braises qui montent
      + `<g class="a-emb1">${dot(482, 196, 2.4, '#ffd36a')}${dot(482, 196, 1.1, '#fffbe8')}</g>`
      + `<g class="a-emb2">${dot(516, 190, 2, '#ffd36a')}${dot(516, 190, 0.9, '#fffbe8')}</g>`
      + `<g class="a-emb3">${dot(500, 184, 1.8, '#ffb040')}</g>`
      // le jet de flammes de l'attaque : invisible au repos
      + `<g class="a-blast" opacity="0"><ellipse cx="536" cy="238" rx="46" ry="34" fill="url(#g-blast)"/>`
      + shape(P([[504, 216], [532, 208], [562, 214, 1], [548, 226], [576, 238, 1], [548, 250], [562, 262, 1], [532, 268], [504, 260]]), '#ffd862', 0.85)
      + shape(P([[504, 228], [530, 224], [556, 238, 1], [530, 252], [504, 248]]), '#fffbe8', 0.9) + `</g>` },

  // --- le bras droit tendu, le poing fermé ---
  { id: 'armR', cls: 'a-armR', d: S.armR, rim: { on: ['wingR'], color: '#4a1208', w: 1.3, o: 0.8 }, shadow: [{ on: ['wingR', 'torso'], dx: -3, dy: 5, color: SH.fea, o: 0.35 }],
    body: use('armR', 'url(#g-armR)') + clip('armR',
      shape('M344 312 C362 318 384 320 410 318 L410 330 L340 330 Z', SKIN.shade, 0.6)
      + shape('M356 293 C372 294 388 295 404 297 C388 299 372 299 358 298 Z', SKIN.hi, 0.85)) },
  { id: 'cuffR', cls: 'a-armR', d: S.cuffR, rim: { on: ['wingR'], color: '#2a0c04', w: 1.3, o: 0.8 }, shadow: [{ on: ['armR'], dx: -3, dy: 3, color: SH.skin, o: 0.4 }],
    body: use('cuffR', 'url(#g-cuffR)') + clip('cuffR',
      // le cuir : des reflets en longueur, l'anneau d'or au poignet
      shape('M406 300 C418 297 432 295 446 294 C432 299 418 302 406 304 Z', '#c2702c', 0.7)
      + shape('M410 312 C420 310 432 309 444 309 C432 313 420 315 410 316 Z', '#a0521e', 0.45)
      + `<path d="M449 290 C446 302 446 320 450 333" fill="none" stroke="${GOLD.line}" stroke-width="8"/>`
      + `<path d="M449 290 C446 302 446 320 450 333" fill="none" stroke="${GOLD.base}" stroke-width="5"/>`
      + `<path d="M447.5 296 C446 304 446 314 447.5 322" fill="none" stroke="${GOLD.hi}" stroke-width="1.6"/>`) },
  { id: 'fist', cls: 'a-armR', d: S.fist, shadow: [{ on: ['cuffR'], dx: -3, dy: 3, color: '#1a0802', o: 0.45 }],
    rim: { on: ['wingR'], color: '#4a1208', w: 1.3, o: 0.8 },
    // le haut du poing garde son contour sombre contre la flamme (le feu n'a pas de contour à lui)
    body: `<clipPath id="c-fistTop"><rect x="446" y="262" width="70" height="30"/></clipPath>`
      + `<g clip-path="url(#c-fistTop)"><use href="#s-fist" fill="none" stroke="#2a1430" stroke-width="8.8"/></g>`
      + use('fist', 'url(#g-skin)') + clip('fist',
      // le dessous du poing dans l'ombre, le dessus éclairé
      shape('M452 314 C460 326 474 331 490 331 C499 331 505 325 509 316 L512 342 L448 342 Z', SKIN.shade, 0.65)
      + shape('M464 284 C476 280 490 279 502 283 C490 284 476 286 466 290 Z', SKIN.hi, 0.95)
      // les quatre doigts repliés, sur la droite : chacun bombé, éclairé en haut
      + shape('M482 281 C494 280 504 282 509 287 C509 291 505 293 499 293 C492 293 486 291 482 289 Z', '#ffe4d2', 0.85)
      + shape('M484 295 C495 295 506 297 511 300 C510 304 505 305 498 305 C491 305 486 303 484 301 Z', '#ffe4d2', 0.65)
      + shape('M483 308 C494 309 505 310 509 313 C507 317 502 318 496 318 C489 317 485 315 483 313 Z', '#ffe4d2', 0.5))
    + line('M483 293 C491 295 500 295 508.5 292.5', SKIN.line, 1.7, 0.9) + line('M484 305 C492 307 501 307 508.5 305.5', SKIN.line, 1.7, 0.9)
    + line('M483 317 C490 319 498 319 505.5 318', SKIN.line, 1.7, 0.85)
    // le pouce, couché en travers, avec son ongle
    + shape('M458 300 C466 297 478 298 487 303 C492 307 492 313 487 317 C480 320 470 318 463 313 C458 310 456 305 458 300 Z', SKIN.base)
    + shape('M460 312 C468 318 480 320 488 316 C486 321 478 323 470 321 C465 319 461 316 460 312 Z', SKIN.shade, 0.7)
    + line('M458 300 C466 297 478 298 487 303 C492 307 492 313 487 317', SKIN.line, 1.6, 0.85)
    + shape('M481 305 C485 305 488 308 487 312 C484 313 481 311 480 308 Z', '#fff3ea', 0.95)
    + oval(470, 303, 7, 2.4, '#fff3ea', 0.9, -6) },
  // les plumes blanches de l'épaule droite
  { id: 'shR', d: S.shR, shadow: [{ on: ['armR', 'torso', 'hairB', 'wingR'], dx: -3, dy: 5, color: SH.white, o: 0.4 }],
    body: use('shR', 'url(#g-white)') + clip('shR',
      shape('M350 296 C362 298 374 298 384 300 L378 292 L392 292 L380 284 L392 283 C384 290 370 292 356 290 Z', '#b9a6d0', 0.7)
      + shape('M340 280 C350 272 364 268 378 272 C366 274 354 278 344 286 Z', '#ffffff')
      + shape('M356 270 C368 268 380 272 388 280 C378 276 368 274 358 275 Z', '#ffd8c8', 0.7)
      + line('M346 290 C358 288 370 288 382 290', '#a894c4', 1.3, 0.7)) },

  // --- la tête ---
  { id: 'ear', cls: 'a-head', d: S.ear, shadow: [{ on: ['hairB'], dx: -4, dy: 3, color: SH.hair, o: 0.35 }],
    body: use('ear', 'url(#g-skin)')
      + shape('M236 192 C228 190 221 196 220 206 C219 216 223 225 230 229 C226 221 225 212 227 204 C229 198 232 195 236 192 Z', SKIN.shade, 0.75)
      + line('M234 200 C229 203 228 210 231 216', SKIN.line, 1.5, 0.7)
      // la boucle d'oreille : un anneau d'or qui pend sous le lobe
      + `<path d="M233 236 C224 238 219 248 221 258 C223 266 231 268 237 262 C242 256 242 246 238 239" fill="none" stroke="${GOLD.line}" stroke-width="5.4"/>`
      + `<path d="M233 236 C224 238 219 248 221 258 C223 266 231 268 237 262 C242 256 242 246 238 239" fill="none" stroke="${GOLD.base}" stroke-width="3.2"/>`
      + line('M226 244 C223 250 223 256 225 260', GOLD.hi, 1.4, 0.9) },
  { id: 'face', cls: 'a-head', d: S.face, rim: { on: ['neck', 'torso'], color: SKIN.line, w: 1.1, o: 0.6 },
    shadow: [{ on: ['neck', 'torso'], dx: -2, dy: 7, color: SH.skin, o: 0.45 }, { on: ['hairB'], dx: -3, dy: 5, color: SH.hair, o: 0.35 }],
    body: use('face', 'url(#g-skin)') + clip('face',
      `<rect x="250" y="110" width="150" height="170" fill="url(#g-faceSh)"/>`
      + oval(281, 233, 17, 11, 'url(#g-blush)') + oval(378, 233, 13, 10, 'url(#g-blush)')
      + oval(352, 160, 22, 13, 'url(#g-soft)', 0.6, -10)
    )
    // le rose des joues : une petite tache en cœur sous l'œil gauche, comme sur le dessin
    + shape('M285 226 C283 222.5 278.5 223 278.5 227 C278.5 230.5 282 233 285.5 235 C289 233 292.5 230.5 292.5 227 C292.5 223 288 222.5 285 226 Z', '#ee8c72', 0.8)
    // les yeux : gros iris ambre, trait de cils épais qui s'étire en pointe vers l'extérieur
    + eye('eL', 'M271 205 C276 200 288 197.5 300 198 C307 198.5 312 202 313.5 206 C312 212 306 217.5 298 219.5 C291 220.5 285 219 280.5 216 C276.5 213 273 209.5 271 205 Z', 297.5, 207.5, 12.6,
      P([[257, 185, 1], [266, 189.8], [277, 191], [289, 190.5], [301, 191], [309, 194.5], [313.5, 200], [314.5, 205.5, 1], [312, 202.5],
        [307, 199], [300, 198], [288, 197.5], [276, 200], [271, 205, 1], [267.5, 200], [258.5, 197.5, 1], [264, 194.8], [261.5, 191]], true, 1),
      'M270.5 205 C273.5 211 279 216.5 287 219.2 C293 221 302 220.4 308 217.6 C303 222.4 295 223.4 287.5 222.2 C278.5 220.2 272.4 214 270.5 205 Z', 'M270 206 C282 215 301 215 313 207')
    + eye('eR', 'M349.5 206 C351 202 357 199.5 365 199 C374 198.5 382 199.5 385.5 202 C386 208.5 383 214 377 217 C369 220 358 220 353 216 C350.5 213.5 349 210 349.5 206 Z', 361.5, 207.5, 12,
      P([[345.5, 207.5, 1], [347.5, 201], [353.5, 195], [362, 191.5], [373, 190], [383, 189.5], [389, 186], [394, 182.5, 1], [391, 189.5],
        [388, 193.5], [389.5, 198, 1], [385.5, 202, 1], [380, 199.5], [374, 198.5], [365, 199], [357, 199.5], [351, 202.5], [349.5, 206, 1]], true, 1),
      'M386 203 C385.5 210.5 381 216 373 218.6 C366 220.6 358 220 353.5 216.8 C358 222.2 367 223.2 375 221.2 C383 218.8 387.5 211.5 386 203 Z', 'M348 206 C359 215 377 215 386 205')
    // le pli de la paupière, fin, au-dessus de chaque œil
    + line('M279 186.5 C290 184.5 302 185.5 311.5 192', SKIN.line, 1.3, 0.75) + line('M352 191.5 C361 187.5 373 185.5 385 187', SKIN.line, 1.3, 0.75)
    // les sourcils, épais et arqués : ils descendent vers le nez (l'air assuré)
    + shape(P([[279, 175.5], [291, 173.5], [304, 176.5], [313, 181.5], [319.5, 186.5, 1], [316, 190.5], [307, 186.5], [296, 182.5], [285, 181], [278, 180.5]], true, 1), '#a92e26')
    + shape(P([[344.5, 190.5], [345.5, 184.5], [351, 178], [361, 174], [373, 172.5], [382.5, 174.5, 1], [381.5, 180.5], [370, 180], [360, 182.5], [352, 187], [347.5, 192.5, 1]], true, 1), '#a92e26')
    + line('M283 176.8 C292 175.2 302 177.5 310 181.5', '#d8604c', 1.4, 0.75) + line('M349 182.5 C356 177 366 174.6 378 175', '#d8604c', 1.4, 0.75)
    // le nez : une touche rose, le petit trait du bout
    + oval(338.5, 230.5, 5.5, 3.4, '#ee9a88', 0.35)
    + line('M345 226 C346.8 229 346.4 232 344 234', SKIN.line, 1.2, 0.4) + line('M333.5 232.5 C336.5 235 340 235.5 343.5 234.5', '#9a4a42', 1.7, 0.85)
    + oval(340, 226, 2.2, 1.6, '#fff4ec', 0.9)
    // la bouche : un sourire en coin, les dents du haut, la lèvre du bas rouge
    + `<clipPath id="c-mouth"><path id="s-mouth" d="M308 244 C315 247 324 248.2 333 247.6 C338.5 247.2 342 245.8 345 243.6 C342.5 249.5 336 255.2 327.5 256.2 C319 257 312 252 308 244 Z"/></clipPath>`
    + `<use href="#s-mouth" fill="#6a1620"/>`
    + `<g clip-path="url(#c-mouth)">${shape('M316 247.6 C323 249 331 249 338 247.6 L337 250.4 C330 251.6 323 251.6 317 250.4 Z', '#fff8f0')}${oval(327.5, 257.5, 12.5, 5.6, '#b23440')}${shape('M321 254.6 C325 253.6 330 253.6 334 254.6 C330 254.4 325 254.4 321 254.6 Z', '#f07a7a', 0.7)}</g>`
    + shape('M302.6 239.6 C304.6 239.8 306.4 241.8 308.4 243.6 C315.6 247.4 326 248.4 334.6 247.6 C339.2 247.2 342.8 245.6 345.6 242.8 C347 241.4 348.6 239.6 350.4 239.2 C349.6 241.2 348.4 243.4 346.8 245.2 C343.6 248.4 339.6 249.4 334.8 249.6 C325.6 250 315 249 307.8 246 C305.2 244.4 303.4 242.2 302.6 239.6 Z', '#3a1210') },
  { id: 'lockL', cls: 'a-head', d: S.lockL, shadow: [{ on: ['face', 'ear'], dx: -3, dy: 4, color: SH.skin, o: 0.4 }, { on: ['hairB'], dx: -3, dy: 4, color: SH.hair, o: 0.3 }],
    body: use('lockL', 'url(#g-hair)')
      + shape('M258 160 C262 180 259 206 257 228 C256 238 256 246 258 252 C252 240 250 222 252 200 C253 184 254 170 258 160 Z', HAIR.hi, 0.5)
      + shape('M266 170 C266 194 262 222 262 246 C266 228 270 204 270 178 Z', HAIR.line, 0.35) },
  { id: 'lockR', cls: 'a-head', d: S.lockR, shadow: [{ on: ['face'], dx: -3, dy: 4, color: SH.skin, o: 0.4 }],
    body: use('lockR', 'url(#g-hair)') + clip('lockR',
      // la tresse : des maillons qui se recouvrent ; le bas éclairé par la boule de feu
      shape('M388 160 C396 166 401 176 400 186 C394 182 389 176 386 168 Z', HAIR.line, 0.35)
      + shape('M388 186 C397 192 402 202 402 212 C395 208 389 202 387 194 Z', HAIR.line, 0.35)
      + shape('M388 212 C397 218 403 228 402 238 C395 234 390 228 388 220 Z', HAIR.line, 0.35)
      + shape('M393 164 C398 168 400 174 400 180 C396 176 394 170 393 164 Z', HAIR.hi, 0.7)
      + shape('M394 190 C399 194 401 200 401 206 C397 202 395 196 394 190 Z', HAIR.hi, 0.7)
      + `<path d="M386 226 C394 232 404 238 404 250 C402 262 397 268 394 270 C390 262 386 250 386 238 Z" fill="#ffc94a" opacity="0.75"/>`
      + shape('M396 240 C400 246 401 254 398 262 C396 254 395 248 396 240 Z', '#fff2a0', 0.9)
    ) },
  { id: 'cap', cls: 'a-head', d: S.cap, shadow: [{ on: ['face', 'ear', 'lockL', 'lockR'], dx: -3, dy: 6, color: SH.skin, o: 0.36 }, { on: ['hairB'], dx: -3, dy: 5, color: SH.hair, o: 0.3 }],
    body: use('cap', 'url(#g-hair)') + clip('cap',
      // le côté gauche de la tête, à l'ombre ; le sommet un peu plus sombre (derrière le diadème)
      shape('M204 132 C218 108 240 88 264 74 C250 96 238 120 232 150 C224 148 212 144 204 132 Z', HAIR.mid, 0.6)
      + shape('M252 84 C276 66 306 60 330 70 C350 78 370 92 384 108 L360 112 C330 96 290 92 252 104 Z', HAIR.deep, 0.28)
      // le dessous des franges, recourbé, dans l'ombre
      + shape('M337 128 C324 134 308 147 296 162 C288 174 282 184 276 194 C280 182 286 170 292 160 C302 146 316 136 330 130 Z', HAIR.deep, 0.7)
      + shape('M337 128 C350 130 364 140 376 154 C382 162 386 168 392 166 C386 160 380 150 372 142 C362 134 350 128 337 128 Z', HAIR.deep, 0.7)
      // les mèches de la frange : des creux effilés qui suivent la chute des cheveux
      + shape('M322 124 C312 138 304 152 298 166 C304 150 312 136 318 124 Z', HAIR.line, 0.55)
      + shape('M300 120 C288 134 280 150 276 168 C276 150 284 134 294 120 Z', HAIR.line, 0.45)
      + shape('M270 126 C262 138 256 152 254 166 C252 150 256 136 264 126 Z', HAIR.line, 0.4)
      + shape('M356 124 C366 134 374 146 380 160 C372 148 364 138 352 128 Z', HAIR.line, 0.5)
      + shape('M374 118 C384 128 392 140 396 154 C388 142 380 132 370 122 Z', HAIR.line, 0.4)
      // les reflets : une bande claire sous le diadème, coupée en mèches, et le haut de la tête
      + shape('M250 150 C262 138 280 128 300 124 C290 132 278 140 268 150 C262 152 256 152 250 150 Z', '#ffc28a', 0.8)
      + shape('M304 124 C312 122 320 122 326 124 C318 128 310 134 304 140 C302 134 302 128 304 124 Z', '#ffc28a', 0.7)
      + shape('M348 124 C362 126 376 132 388 142 C380 140 370 138 362 138 C356 134 352 130 348 124 Z', '#ffc28a', 0.75)
      + shape('M270 74 C282 64 296 62 308 68 C296 68 284 72 274 80 Z', HAIR.hi, 0.7)
      + shape('M326 76 C342 80 356 88 368 98 C354 92 340 86 326 82 Z', HAIR.hi, 0.5)
    ) },
  { id: 'tiara', cls: 'a-head', d: S.tiara, shadow: [{ on: ['cap', 'face', 'hairB'], dx: -3, dy: 5, color: SH.hair, o: 0.4 }],
    body: use('tiara', 'url(#g-tiara)') + clip('tiara',
      // le bandeau : liseré clair en haut, ombre en bas
      shape('M238 150 C252 136 280 122 310 116 L314 116 C284 123 258 136 242 152 Z', GOLD.hi, 0.85)
      + shape('M248 143 C262 134 282 125 300 119 L314 117 L318 124 L300 126 C282 131 262 140 246 151 Z', GOLD.shade, 0.45)
      + shape('M350 118 C366 117 384 124 399 140 L406 146 L404 150 C390 136 372 126 352 125 Z', GOLD.shade, 0.45)
      // chaque pointe : une face claire (à droite, vers la lumière) et une face dans l'ombre, de part et d'autre de l'arête
      + shape('M262 99 L254 124 L265 127 Z', GOLD.mid, 0.9) + shape('M262 99 L265 127 L276 110 Z', GOLD.hi, 0.9)
      + shape('M300 95 L291 117 L301 118 Z', GOLD.mid, 0.9) + shape('M300 95 L301 118 L311 107 Z', GOLD.hi, 0.9)
      + shape('M364 84 L358 99 L366 101 Z', GOLD.mid, 0.9) + shape('M364 84 L366 101 L369 94 Z', GOLD.hi, 0.9)
      + shape('M375 87 L371 100 L378 104 Z', GOLD.mid, 0.9) + shape('M375 87 L378 104 L381 104 Z', GOLD.hi, 0.9)
      // le grand cimier : face gauche dans la lumière douce, face droite claire, le bas qui se resserre vers le front
      + shape('M318 43 L312 80 L311 107 L320 104 L322 70 Z', GOLD.mid, 0.55)
      + shape('M318 43 L322 70 L345 88 L336 71 L327 55 Z', GOLD.hi, 0.9)
      + shape('M311 107 L326 119 L338 142 L332 128 L320 112 Z', GOLD.shade, 0.6)
      + shape('M352 101 L344 128 L338 142 L346 120 Z', GOLD.shade, 0.6)
    )
    // la monture de la pierre : un anneau d'or plus sombre
    + shape('M332 76 L346 98 L336 128 L321 102 Z', GOLD.shade)
    // la pierre rouge, taillée
    + shape('M332 81 L343 99 L335 123 L324 102 Z', '#c8201e')
    + shape('M332 81 L334 99 L324 102 Z', '#ff7262') + shape('M332 81 L343 99 L334 99 Z', '#e83a30')
    + shape('M324 102 L334 99 L335 123 Z', '#a0141a') + shape('M334 99 L343 99 L335 123 Z', '#760c12')
    + shape('M328.5 90 L331.5 86 L332.5 95 Z', '#ffffff', 0.95) + dot(338, 104, 1.2, '#ffd0c8', 0.8) },
];

const defs = [...baseDefs, ...Object.values(featherGrads), ...featherDefs, ...legDefs].join('');

// ---------- la vie au repos ----------
// Les ailes respirent (elles s'ouvrent et se referment un peu, chacune à son rythme), la traîne ondule, la tête et la
// chevelure bougent ensemble, les bras accompagnent, le feu danse (la flamme s'étire depuis le poing, le cœur palpite,
// des braises montent), les yeux clignent.
// L'attaque (classe « atk » sur le <svg>, 0,75 s) : les ailes se lèvent et le bras se replie (élan, 0–35 %), puis les ailes
// battent pendant qu'elle projette la boule de feu vers l'avant (35–55 %), et tout revient à la pose du repos (55–100 %).
// Le bras ne fait que tourner et s'étirer depuis l'épaule : sa racine reste cachée sous les plumes de l'épaule.
// Chaque animation du repos part de la pose de base (« from » = aucune transformation, pas de délai) : la fin de
// l'attaque retombe exactement dessus.
const PIV = { wl: [226, 262], wr: [428, 264], tail: [236, 420], head: [318, 290], armR: [350, 300], armL: [262, 294], fire: [491, 280] };
const o = (k) => `transform-origin:${PIV[k][0]}px ${PIV[k][1]}px`;
const style = `
.a-wl{${o('wl')};animation:wl 3.2s ease-in-out infinite alternate}
.a-wr{${o('wr')};animation:wr 3.7s ease-in-out infinite alternate}
.a-tail{${o('tail')};animation:tail 4.3s ease-in-out infinite alternate}
.a-head{${o('head')};animation:head 3s ease-in-out infinite alternate}
.a-hairB{${o('head')};animation:hairB 3s ease-in-out infinite alternate}
.a-armR{${o('armR')};animation:armR 2.6s ease-in-out infinite alternate}
.a-armL{${o('armL')};animation:armL 3.5s ease-in-out infinite alternate}
.a-fire{${o('fire')};animation:fire .9s ease-in-out infinite alternate}
.a-flame2{${o('fire')};animation:flame2 .62s ease-in-out infinite alternate}
.a-core{transform-origin:494px 252px;animation:core .75s ease-in-out infinite alternate}
.a-emb1{animation:emb 1.7s linear infinite}
.a-emb2{animation:emb 1.7s linear -.6s infinite}
.a-emb3{animation:emb 1.7s linear -1.15s infinite}
.a-blink{animation:blink 4.4s linear infinite}
@keyframes wl{from{transform:none}to{transform:rotate(2.6deg)}}
@keyframes wr{from{transform:none}to{transform:rotate(-2.6deg)}}
@keyframes tail{from{transform:none}to{transform:rotate(-1.6deg)}}
@keyframes head{from{transform:none}to{transform:rotate(-1.1deg)}}
@keyframes hairB{from{transform:none}to{transform:rotate(-1.5deg)}}
@keyframes armR{from{transform:none}to{transform:rotate(-1.6deg)}}
@keyframes armL{from{transform:none}to{transform:rotate(2.2deg)}}
@keyframes fire{from{transform:none}to{transform:scale(.95,1.08) skewX(-3deg)}}
@keyframes flame2{from{transform:none}to{transform:scale(1.04,.94) skewX(3deg)}}
@keyframes core{from{transform:none;opacity:1}to{transform:scale(.9);opacity:.8}}
@keyframes emb{0%{transform:translate(0,14px);opacity:0}20%{opacity:1}100%{transform:translate(6px,-34px);opacity:0}}
@keyframes blink{0%,93%{opacity:0}94.5%,97%{opacity:1}98.5%,100%{opacity:0}}
.atk .a-wl{animation:wl-atk .75s ease-in-out}
.atk .a-wr{animation:wr-atk .75s ease-in-out}
.atk .a-tail{animation:tail-atk .75s ease-in-out}
.atk .a-head{animation:head-atk .75s ease-in-out}
.atk .a-hairB{animation:hairB-atk .75s ease-in-out}
.atk .a-armR{animation:armR-atk .75s ease-in-out}
.atk .a-armL{animation:armL-atk .75s ease-in-out}
.atk .a-fire{animation:fire-atk .75s ease-in-out}
.atk .a-blast{animation:blast .75s ease-out}
@keyframes wl-atk{0%{transform:none}32%{transform:rotate(8deg)}48%{transform:rotate(-7deg)}60%{transform:rotate(-5deg)}100%{transform:none}}
@keyframes wr-atk{0%{transform:none}32%{transform:rotate(-8deg)}48%{transform:rotate(7deg)}60%{transform:rotate(5deg)}100%{transform:none}}
@keyframes tail-atk{0%{transform:none}32%{transform:rotate(2deg)}50%{transform:rotate(-3deg)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}32%{transform:rotate(-2deg)}50%{transform:rotate(2deg)}62%{transform:rotate(1.6deg)}100%{transform:none}}
@keyframes hairB-atk{0%{transform:none}32%{transform:rotate(-2.4deg)}50%{transform:rotate(2.6deg)}62%{transform:rotate(2deg)}100%{transform:none}}
@keyframes armR-atk{0%{transform:none}32%{transform:rotate(-7deg) scale(.95,1)}50%{transform:rotate(2deg) scale(1.11,1)}62%{transform:rotate(1.5deg) scale(1.08,1)}100%{transform:none}}
@keyframes armL-atk{0%{transform:none}32%{transform:rotate(5deg)}50%{transform:rotate(-3deg)}100%{transform:none}}
@keyframes fire-atk{0%{transform:none}32%{transform:scale(1.2)}50%{transform:translate(8px,0) scale(1.4,1.25)}64%{transform:scale(1.15)}100%{transform:none}}
@keyframes blast{0%,36%{opacity:0;transform:none}48%{opacity:1;transform:translate(6px,0)}70%{opacity:0;transform:translate(16px,0)}100%{opacity:0;transform:none}}
`.replace(/\n/g, '');

module.exports = { id: 'assassins-5', w: W, h: H, pad: 50, foot: [314, 500],
  svg: (anime = true) => figure({ w: W, h: H, pad: 50, defs, style, parts, anime }) };
