// Le harfang (glaces-4), monstre de la Horde des glaces : redessiné par le code d'après le dessin d'origine, dans le
// même cadre (476 × 328, mêmes proportions, même pose) : plumage blanc ombré de gris lavande, les deux ailes grandes
// ouvertes, tête ronde à aigrettes, yeux jaunes furieux sous des sourcils sombres, bec crochu ouvert, serres sombres,
// queue en éventail.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 476, H = 328, PAD = 62;

// ---------- courbes lisses ----------
/**
 * Chemin lisse passant par des points (spline de Catmull-Rom, tangentes mesurées sur les distances : pas de boucle).
 * `src` = "x,y x,y! …" : un point suivi de « ! » est un angle vif (pointe de plume, creux entre deux plumes).
 * Entre deux angles vifs qui se suivent, le bord est bombé vers l'extérieur de `bulge` pixels (une plume est ronde).
 */
function sm(src, bulge = 0, closed = true) {
  let pts = (Array.isArray(src) ? src.join(' ') : src).trim().split(/\s+/).map((s) => {
    const sharp = s.endsWith('!');
    const [x, y] = s.replace('!', '').split(',').map(Number);
    return { x, y, sharp };
  });
  if (bulge && closed) {
    // le sens du tracé (aire signée) donne le côté extérieur
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

/** Un fuseau effilé aux deux bouts (petite plume) : de `a` à `b`, épais de `w` au milieu. */
function spindle(ax, ay, bx, by, w) {
  const L = Math.hypot(bx - ax, by - ay) || 1, nx = -(by - ay) / L, ny = (bx - ax) / L;
  const mx = (ax + bx) / 2, my = (ay + by) / 2;
  return sm(`${P(ax, ay)}! ${P(mx + nx * w / 2, my + ny * w / 2)} ${P(bx, by)}! ${P(mx - nx * w / 2, my - ny * w / 2)}`);
}

/** Une plume : une lame qui va de sa racine (`rx`,`ry`) à sa pointe (`tx`,`ty`), large de `w`, plus ventrue d'un côté (`lean`). */
function feather(rx, ry, tx, ty, w, lean = 0) {
  const L = Math.hypot(tx - rx, ty - ry), ux = (tx - rx) / L, uy = (ty - ry) / L, nx = -uy, ny = ux;
  const at = (f, s) => P(rx + ux * L * f + nx * w * s, ry + uy * L * f + ny * w * s);
  return sm(`${at(0, 0.5 + lean)} ${at(0.55, 0.56 + lean)} ${at(0.86, 0.34 + lean * 0.6)} ${P(tx, ty)}! ${at(0.86, -0.34 + lean * 0.6)} ${at(0.55, -0.56 + lean)} ${at(0, -0.5 + lean)}`);
}
/** La moitié éclairée d'une plume (le côté `side` = 1 ou -1 de sa nervure). */
function featherHalf(rx, ry, tx, ty, w, lean = 0, side = 1, k = 1) {
  const L = Math.hypot(tx - rx, ty - ry), ux = (tx - rx) / L, uy = (ty - ry) / L, nx = -uy, ny = ux;
  const at = (f, s) => P(rx + ux * L * f + nx * w * s, ry + uy * L * f + ny * w * s);
  return sm(`${at(0, 0)} ${at(0.5, 0.02 * side)} ${P(tx, ty)}! ${at(0.86, side * (0.34 + lean * 0.6) * k)} ${at(0.55, side * (0.56 + lean) * k)} ${at(0, side * (0.5 + lean) * k)}`);
}

// ---------- couleurs ----------
const SNOW = { mid: '#cdc6e2', deep: '#aaa0cb' };
const LAV = { base: '#b9aed6' };
const CLAW = { shade: '#45331f', deep: '#2a1d12' };
const BEAK = { deep: '#232128' };
// les ombres portées : une teinte par matière qui la reçoit
const SH = { snow: '#6c5f9c', wing: '#4a3f78', claw: '#1c120a' };

// ---------- dégradés ----------
const defs = [
  lin('g-head', 320, 40, 190, 160, [[0, '#ffffff'], [0.5, '#f9f8fd'], [0.85, '#e9e6f3'], [1, '#d9d4ea']]),
  lin('g-body', 318, 130, 172, 220, [[0, '#ffffff'], [0.45, '#f6f5fb'], [0.8, '#e2deef'], [1, '#c9c2df']]),
  lin('g-covL', 170, 20, 70, 130, [[0, '#ffffff'], [0.6, '#fbfaff'], [1, '#ebe8f5']]),
  lin('g-covA', 190, 40, 70, 170, [[0, '#f8f7fc'], [0.55, '#ebe7f5'], [1, '#d6cfe8']]),
  lin('g-covR', 300, 20, 400, 130, [[0, '#d9d2ea'], [0.55, '#e3ddf1'], [1, '#cfc7e4']]),
  lin('g-edgeR', 300, 80, 420, 10, [[0, '#d9d2ea'], [0.5, '#f1eef9'], [1, '#ffffff']]),
  lin('g-covAR', 300, 50, 410, 170, [[0, '#cbc2e0'], [0.5, '#d3cbe6'], [1, '#bcb1d8']]),
  lin('g-primL', 0, 0, 0, 1, [[0, '#d2c9e6'], [0.5, '#ada1cd'], [1, '#8d80b8']], false),
  lin('g-primR', 0, 0, 0, 1, [[0, '#cdc4e2'], [0.5, '#a699c8'], [1, '#8576b0']], false),
  lin('g-secL', 0, 0, 0, 1, [[0, '#c6bcdd'], [0.6, '#a194c4'], [1, '#8576ae']], false),
  lin('g-secR', 0, 0, 0, 1, [[0, '#a99dc8'], [0.6, '#8577b0'], [1, '#6c5f99']], false),
  lin('g-thigh', 172, 0, 220, 0, [[0, '#b9b0d6'], [0.45, '#e0dbee'], [1, '#f6f4fb']]),
  lin('g-thighR', 0, 220, 0, 248, [[0, '#ffffff'], [0.6, '#f1eff8'], [1, '#d5cfe7']]),
  lin('g-tail', 0, 0, 0, 1, [[0, '#6f6497'], [0.6, '#544978'], [1, '#3e355e']], false),
  lin('g-tailC', 0, 0, 0, 1, [[0, '#e9e5f4'], [0.5, '#c9c0df'], [1, '#9488bd']], false),
  lin('g-toe', 0, 0, 1, 0, [[0, '#3a2a1a'], [0.4, '#6a5236'], [0.78, '#a88d62'], [1, '#7a6142']], false),
  lin('g-nail', 0, 0, 1, 1, [[0, '#f1ead8'], [0.45, '#cfc5ad'], [1, '#7e7690']], false),
  lin('g-beak', 306, 104, 276, 132, [[0, '#8e8a96'], [0.25, '#55525c'], [0.65, '#44414a'], [1, '#2a2830']]),
  lin('g-jaw', 0, 0, 0, 1, [[0, '#fbfaff'], [0.5, '#e2deec'], [1, '#bdb6cd']], false),
  lin('g-mouth', 0, 122, 0, 148, [[0, '#1c0610'], [0.5, '#3e0c1c'], [1, '#7a2034']]),
  rad('g-iris', 0.62, 0.38, 0.75, [[0, '#fffde0'], [0.35, '#fbf487'], [0.75, '#f1d443'], [1, '#d99a22']], false),
  rad('g-pupil', 0.5, 1, 0.66, [[0, '#f26a2a'], [0.32, '#b8341a'], [0.7, '#3a0e0e'], [1, '#14070e']], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#2a1f3a', 0.7], [0.45, '#2a1f3a', 0]], false),
  lin('g-eyelid', 0, 0, 0, 1, [[0, '#f7f5fb'], [0.6, '#e9e5f3'], [1, '#d6cfe7']], false),
  rad('g-disc', 282, 102, 70, [[0, '#ffffff'], [0.7, '#fefdff'], [1, '#f6f4fb']]),
  lin('g-ruff', 240, 150, 300, 62, [[0, '#a99fcb'], [0.35, '#b9b0d6', 0.9], [0.62, '#cfc8e4', 0.35], [0.8, '#e4dff1', 0]]),
  lin('g-tuftSh', 0, 15, 0, 52, [[0, '#cdc6e2', 0.9], [0.65, '#cdc6e2', 0.55], [1, '#cdc6e2', 0]]),
  rad('g-soft', 0.5, 0.5, 0.5, [[0, '#ffffff', 0.9], [1, '#ffffff', 0]], false),
].join('');

// ---------- silhouettes ----------
const S = {
  // l'aile gauche : le bord d'attaque en grand arc, puis les rémiges (pointes vers la gauche), puis les plumes qui pendent
  wingL: sm('208,66 189,67 182,52 165,33 145,19 116,7 91,3 61,4 39,8 16,15 3,22! 34,48! 7,74! 30,90! 19,100! 34,102! 20,119! 46,128! 61,135! 51,167! 88,168! 85,178! 93,179! 94,196! 128,190! 131,206! 156,196! 161,199! 168,202 186,208 214,206 234,176 236,112 226,72', 2.2),
  wingR: sm('310,62 318,58 327,53 345,32 368,19 391,13 420,12 446,16 472,26! 443,52! 465,75! 434,94! 449,117! 418,128! 426,153! 394,157! 393,187! 368,186! 365,190! 356,184! 351,203! 323,195! 318,207! 295,197 272,186 262,130 272,80 296,64', 2.2),
  tail: sm('178,212 168,218! 146,239 118,260 114,265! 136,267 141,262! 149,266 150,272 145,282 142,297! 156,292 171,285! 175,298 178,310! 192,298 206,289! 213,305 219,321! 228,316 244,288! 256,294 269,301! 270,288 269,279! 268,250 240,238 205,236', 1.6),
  // les pattes : la cheville sous la culotte de plumes, trois doigts et leurs griffes (construites plus bas, `FEET`)
  footL: '', footR: '',
  // le corps : la poitrine passe devant les ailes ; deux mèches douces de chaque côté, là où elle les recouvre
  body: sm('190,118 214,110 260,108 300,112 322,122 326,140 323,154 321,169! 315,165! 311,180 305,197! 299,192! 294,204 289,210 281,218 274,228! 271,240 262,247! 253,242 244,247! 236,242 226,246! 218,240 210,247! 201,241 192,245! 183,238 175,232! 171,222 169,213 170,203! 163,206! 170,190 172,181 174,172! 167,175! 175,160 178,144'),
  tuftL: sm('216,52 213,40 211,28 212,15! 224,19 236,26 250,34 248,46 232,54'),
  tuftR: sm('286,40 296,30 306,23 316,18! 316,30 315,42 318,54 304,54 290,48'),
  // la tête : un crâne rond et des joues pleines ; le contour se casse en quelques mèches douces, toutes différentes
  // (elles tombent vers le bas et vers l'extérieur, comme le duvet), jamais en zigzag régulier
  head: sm([
    // le haut du crâne, entre les deux aigrettes : deux petites mèches
    '266,27', '257,21!', '252,29!', '240,32', '227,38', '214,47', '203,58',
    // la joue gauche, la plus large (la tête est tournée vers la droite) : trois mèches
    '196,69', '188,83!', '194,80!', '190,94', '188,104', '181,115!', '189,111!', '189,123', '192,133', '185,143!', '194,139!', '200,148',
    // sous le bec, le duvet du menton qui retombe sur la poitrine
    '211,156', '215,166!', '221,160!', '233,165', '247,176!', '252,168!', '265,170', '278,169', '287,177!', '291,168!', '302,164',
    // la joue droite, plus étroite : trois mèches
    '314,157', '324,147!', '329,153!', '332,134', '334,121!', '341,125!', '336,106', '333,94!', '340,97!', '334,80', '327,66', '317,53',
    '303,40', '290,32', '279,22!', '275,29!',
  ]),
  // le bec : la mandibule du haut, crochue ; celle du bas, pâle, avec l'intérieur de la gueule
  beak: sm('291.5,102.5 296.5,102.5 300.5,104.5 304.5,109 306.3,116 306,124 304,131 301,137 299,143.5! 297,138 294.5,131.5 290,127 283,125 277,124.5 271.5,125! 273.5,118 277.5,112.5 282.5,107.5 287.5,104'),
  jaw: sm('273,121 281,114 289,109 297,112 301,124 301,136 299.5,143 296,147 289,148.6 281,147.8 274.5,145 270.6,141.5 269.6,134 270.6,127'),
};

// ---------- les ailes : des rangées de plumes qui se recouvrent ----------
/** Une rangée de plumes : chaque plume [racine x, y, pointe x, y, largeur, penchant], sa teinte, son ombre sur la précédente. */
function row(list, fill, sh, shO = 0.3, lite = null, liteO = 0.6, side = -1) {
  return list.map(([rx, ry, tx, ty, w, lean = 0]) => {
    const d = feather(rx, ry, tx, ty, w, lean);
    return `<path d="${d}" transform="translate(-3 4)" fill="${sh}" opacity="${shO}"/>` + shape(d, fill)
      + (lite ? shape(featherHalf(rx, ry, tx, ty, w, lean, side), lite, liteO) : '');
  }).join('');
}

// l'aile gauche (pointes vers la gauche et vers le bas) — la lumière vient d'en haut : la moitié du haut de chaque plume est claire
const WL = {
  // les rémiges, du bas vers le haut (celle du dessus recouvre celle du dessous)
  prim: [[150, 150, 51, 167, 34, 0.08], [140, 118, 20, 119, 36, 0.05], [128, 100, 19, 100, 20, 0], [130, 76, 7, 74, 40, 0.05], [120, 38, 3, 22, 42, -0.08]],
  // les plumes qui pendent sous l'aile, de l'extérieur vers le corps
  sec: [[112, 145, 85, 178, 24, 0.1], [134, 152, 94, 196, 32, 0.05], [156, 160, 131, 206, 34, 0], [180, 162, 161, 199, 26, 0]],
};
// les tectrices du dessous de l'aile : deux rangées de plumes blanches, chacune posée sur la suivante, de tailles
// différentes ; leurs racines disparaissent sous la bande blanche du bord d'attaque
const COV_L = {
  // [racine x, y, pointe x, y, largeur, penchant], de la plus basse (dessinée d'abord) à la plus haute
  a: [[206, 140, 176, 191, 26, 0], [194, 126, 151, 180, 24, 0.05], [184, 112, 125, 168, 34, 0.04], [172, 96, 94, 143, 34, 0.06], [162, 86, 77, 111, 24, 0.05], [154, 66, 57, 89, 34, 0.06], [150, 42, 63, 56, 30, 0.05]],
  b: [[214, 112, 196, 152, 24, 0], [206, 96, 175, 137, 28, 0.04], [196, 80, 150, 120, 32, 0.05], [186, 64, 128, 93, 28, 0.05], [176, 50, 100, 71, 32, 0.05], [166, 36, 86, 45, 22, 0.04], [160, 22, 69, 24, 30, 0.02]],
  top: sm('214,82 200,66 182,48 160,30 130,16 96,10 60,10 44,10 70,4 104,4 140,14 168,30 190,52 214,60'),
};
function wingLBody() {
  return use('wingL', 'url(#g-secL)')
    + row(WL.prim, 'url(#g-primL)', SH.wing, 0.36, '#d9d1ec', 0.6, -1)
    + row(WL.sec, 'url(#g-secL)', SH.wing, 0.36, '#c6bbdf', 0.55, 1)
    + row(COV_L.a, 'url(#g-covA)', SH.wing, 0.24, '#ffffff', 0.55, -1)
    + row(COV_L.b, 'url(#g-covL)', SH.wing, 0.18, '#ffffff', 0.7, -1)
    // la bande blanche du bord d'attaque, et sa lumière
    + shape(COV_L.top, '#fbfaff')
    + shape(sm('40,10 70,6 104,6 138,16 166,34 184,56 172,46 146,28 112,16 76,12 50,14'), '#ffffff', 0.95)
    // l'ombre de la tête et du corps près de l'épaule
    + shape(sm('214,56 198,66 188,92 184,130 186,170 192,204 214,204'), SH.wing, 0.16);
}

// l'aile droite (pointes vers la droite) : un peu plus soutenue que la gauche, comme sur le dessin d'origine
const WR = {
  prim: [[346, 148, 426, 153, 34, -0.06], [352, 118, 449, 117, 38, -0.05], [356, 82, 465, 75, 40, -0.05], [350, 44, 472, 26, 42, 0.08]],
  // de l'intérieur vers l'extérieur : chacune recouvre sa voisine de gauche (la lumière vient de droite)
  sec: [[300, 158, 318, 207, 28, 0], [322, 156, 351, 203, 32, -0.05], [344, 150, 365, 190, 24, 0], [360, 146, 393, 187, 32, -0.08]],
};
const COV_R = {
  a: [[294, 146, 307, 194, 24, 0], [306, 134, 334, 188, 30, -0.04], [318, 120, 362, 172, 30, -0.05], [330, 104, 387, 149, 34, -0.05], [340, 88, 406, 121, 28, -0.05], [348, 70, 420, 89, 34, -0.06], [352, 48, 414, 57, 28, -0.04]],
  b: [[292, 112, 312, 147, 24, 0], [300, 96, 334, 125, 30, -0.04], [310, 80, 356, 99, 28, -0.05], [320, 64, 378, 73, 32, -0.05], [332, 48, 396, 49, 26, -0.04], [344, 34, 408, 23, 30, -0.03]],
  top: sm('290,84 300,66 318,48 344,30 376,16 410,10 446,14 420,6 386,6 352,16 324,32 302,50 290,60'),
};
function wingRBody() {
  return use('wingR', 'url(#g-secR)')
    + row(WR.prim, 'url(#g-primR)', SH.wing, 0.36, '#d6cdea', 0.55, 1)
    + row(WR.sec, 'url(#g-secR)', SH.wing, 0.36, '#b5a9d1', 0.5, -1)
    + row(COV_R.a, 'url(#g-covAR)', SH.wing, 0.28, '#e4def2', 0.55, 1)
    + row(COV_R.b, 'url(#g-covR)', SH.wing, 0.22, '#f1edf9', 0.6, 1)
    + shape(COV_R.top, 'url(#g-edgeR)')
    + shape(sm('336,40 356,24 384,14 420,10 446,14 420,16 388,20 360,30'), '#ffffff', 0.95)
    + shape(sm('290,56 308,64 318,96 320,140 312,180 298,200 288,170'), SH.wing, 0.16);
}

// ---------- la queue : un éventail de plumes, sombres à gauche (dans l'ombre des ailes), claire au milieu ----------
const TAIL = [[184, 222, 114, 265, 26, 0], [192, 236, 142, 297, 28, 0], [206, 240, 178, 310, 30, 0], [254, 240, 269, 301, 30, 0], [224, 236, 219, 321, 30, 0]];
function tailBody() {
  return use('tail', 'url(#g-tail)')
    + TAIL.map(([rx, ry, tx, ty, w], i) => {
      const d = feather(rx, ry, tx, ty, w);
      const center = i === 4;
      return `<path d="${d}" transform="translate(-3 4)" fill="${SH.wing}" opacity="0.4"/>`
        + shape(d, center ? 'url(#g-tailC)' : 'url(#g-tail)')
        + shape(featherHalf(rx, ry, tx, ty, w, 0, tx > rx ? -1 : 1), center ? '#f4f1fb' : '#8e83b6', center ? 0.55 : 0.5);
    }).join('');
}

// ---------- les pattes ----------
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
/** Un tube lisse le long d'une ligne (un doigt) : épais de `w` (puis `tipW` au bout), arrondi aux deux bouts. */
function tube(pts, w, tipW = w) {
  const L = pts.length, left = [], right = [];
  pts.forEach(([x, y], i) => {
    const [ax, ay] = pts[Math.max(0, i - 1)], [bx, by] = pts[Math.min(L - 1, i + 1)];
    const d = Math.hypot(bx - ax, by - ay) || 1, nx = -(by - ay) / d, ny = (bx - ax) / d;
    const r = (w + (tipW - w) * (i / (L - 1))) / 2;
    left.push(P(x + nx * r, y + ny * r)); right.push(P(x - nx * r, y - ny * r));
  });
  const [x0, y0] = pts[0], [x1, y1] = pts[1], [xa, ya] = pts[L - 2], [xb, yb] = pts[L - 1];
  const u0 = Math.hypot(x1 - x0, y1 - y0), u1 = Math.hypot(xb - xa, yb - ya);
  const back = P(x0 - ((x1 - x0) / u0) * w * 0.45, y0 - ((y1 - y0) / u0) * w * 0.45);
  const front = P(xb + ((xb - xa) / u1) * tipW * 0.45, yb + ((yb - ya) / u1) * tipW * 0.45);
  return sm(cw([back, ...left, front, ...right.reverse()]));
}
/** Une griffe : un croc courbe qui part du bout d'un doigt (`a`) vers sa pointe (`b`), courbé de `bend`. */
function nail(ax, ay, bx, by, w, bend) {
  const L = Math.hypot(bx - ax, by - ay), ux = (bx - ax) / L, uy = (by - ay) / L, nx = -uy, ny = ux;
  const mx = (ax + bx) / 2 + nx * bend, my = (ay + by) / 2 + ny * bend;
  return sm(cw([P(ax + nx * w / 2 - ux * 2.5, ay + ny * w / 2 - uy * 2.5), P(mx + nx * w * 0.3, my + ny * w * 0.3), `${P(bx, by)}!`, P(mx - nx * w * 0.16, my - ny * w * 0.16), P(ax - nx * w / 2 - ux * 2.5, ay - ny * w / 2 - uy * 2.5)]));
}
// chaque patte : la cheville (sous la culotte de plumes), trois doigts trapus et serrés, une griffe courte au bout de chacun
const FEET = {
  footL: {
    ankle: sm(cw(['194,232', '214,232', '218,246', '211,256', '199,256', '191,247'])),
    toes: [[[198, 248], [191.5, 256], [189, 265], [189.5, 271]], [[205, 250], [205, 260], [205.5, 268], [206, 274]], [[211, 248], [217.5, 255], [220.5, 263], [220, 270]]],
    nails: [[189.5, 271, 193, 280, 6, -2], [206, 274, 207.5, 283, 6, -1.4], [220, 270, 216.5, 279, 5.6, 1.8]],
  },
  footR: {
    ankle: sm(cw(['249,232', '267,232', '270,246', '263,256', '251,256', '245,247'])),
    toes: [[[252, 248], [247, 256], [244.5, 264], [244.5, 270]], [[258.5, 250], [260, 259], [261.5, 267], [262, 273]], [[264, 248], [274, 252], [282, 258], [286, 264]]],
    nails: [[244.5, 270, 247.5, 280, 6.6, -2], [262, 273, 264.2, 283, 6.6, -1.5], [286, 264, 290.6, 273, 6.2, 0.6]],
  },
};
const footD = (f) => [f.ankle, ...f.toes.map((t) => tube(t, 10.6, 8.4)), ...f.nails.map((nl) => nail(...nl))].join('');
function footBody(id) {
  const f = FEET[id];
  return use(id, CLAW.shade) + clip(id,
    // la cheville, dans l'ombre de la culotte de plumes
    shape(f.ankle, CLAW.deep)
    // chaque doigt est un rouleau : sombre à gauche, éclairé à droite ; il pose une ombre douce sur son voisin
    + f.toes.map((t) => {
      const d = tube(t, 10.6, 8.4);
      return `<path d="${d}" transform="translate(-2 2)" fill="${CLAW.deep}" opacity="0.45"/>` + shape(d, 'url(#g-toe)');
    }).join('')
    // les griffes : ivoire, la pointe grise
    + f.nails.map((nl) => shape(nail(...nl), 'url(#g-nail)')).join('')
  );
}

S.footL = footD(FEET.footL); S.footR = footD(FEET.footR);

// ---------- le ventre ----------
// les deux culottes de plumes : leur bas est en mèches, posées sur la cheville
const THIGH_L = sm('176,206 186,198 200,200 211,210 217,224 219,238 216,244! 210,241 206,248! 200,243 193,247! 187,240 180,238! 174,228 172,216');
const THIGH_R = sm('250,236 258,229 270,226 278,228 277,236 274,241! 269,241 265,248! 259,244 252,248! 248,242');
/** Une moucheture : une bande ondulée de `len` pixels, à deux ou trois creux, un peu plus épaisse au milieu. */
function bar(x0, y0, len, k = 3) {
  const top = [], bot = [];
  for (let i = 0; i <= k * 2; i++) {
    const f = i / (k * 2), x = x0 + len * f, th = 2.2 + 2.6 * Math.sin(Math.PI * f);
    const wave = (i % 2 ? 2.2 : -0.6);
    top.push(P(x, y0 + wave - th * 0.2));
    bot.push(`${P(x, y0 + wave + th)}${i % 2 ? '!' : ''}`);
  }
  return sm([`${P(x0 - 2, y0 + 0.5)}!`, ...top.slice(1, -1), `${P(x0 + len + 2, y0 + 0.5)}!`, ...bot.slice(1, -1).reverse()]);
}
// [début x, y, longueur, creux, opacité]
const MARKS = [[203, 170, 32, 3, 0.7], [240, 181, 26, 2, 0.6], [275, 166, 26, 2, 0.5], [214, 203, 22, 2, 0.5], [254, 207, 30, 3, 0.5], [288, 193, 14, 1, 0.4]];

// ---------- le visage : le disque facial de la chouette ----------
// deux lobes ronds autour des yeux (le gauche, proche, plus grand), qui se rejoignent entre les sourcils et sous le bec
const DISC = sm('291,78! 300,68 314,64 327,70 333,84 335,100 332,117 326,133 316,145 304,152 293,157! 278,157 260,154 243,149 229,140 219,127 214,110 215,93 221,79 232,69 247,64 263,64 278,69');
// la collerette qui le borde : quelques petites plumes pointues, toutes différentes [dedans x, y, pointe x, y, largeur]
const RUFF = [[227, 76, 212, 88, 6], [222, 104, 204, 113, 7], [232, 132, 216, 147, 6], [255, 145, 246, 164, 6.5], [298, 147, 304, 166, 6], [321, 129, 335, 141, 5]];
// la collerette : l'ombre douce du bord du disque (en bas à gauche, du côté de l'ombre) et ses petites plumes ; elle
// s'efface vers le haut et vers la droite, où le disque se fond dans le front et la joue éclairée
const ruff = `<g opacity="0.8"><path d="${DISC}" transform="translate(-3 4)" fill="url(#g-ruff)"/>`
  + RUFF.map(([ax, ay, bx, by, w]) => shape(spindle(ax, ay, bx, by, w), 'url(#g-ruff)')).join('') + '</g>';

// ---------- les yeux ----------
/**
 * Un œil de chouette : l'anneau sombre, l'iris jaune en dégradé, la pupille (sombre, rougeoyante en bas), l'ombre de la
 * paupière, deux reflets ; puis le sourcil froncé par-dessus (`brow`, et son reflet `browHi`).
 * `lid` = la paupière fermée du clignement (elle couvre tout l'œil, anneau compris), `lash` = son trait.
 */
function eye(key, cx, cy, rx, ry, px, py, pr, brow, browHi, lid, lash) {
  const iris = `M${n(cx - rx)} ${cy}a${rx} ${ry} 0 1 0 ${n(2 * rx)} 0a${rx} ${ry} 0 1 0 ${n(-2 * rx)} 0Z`;
  return oval(cx, n(cy + 0.3), n(rx + 2.7), n(ry + 2.7), '#2b2238')
    + `<clipPath id="c-${key}"><path d="${iris}"/></clipPath>`
    + `<path d="${iris}" fill="url(#g-iris)"/>`
    + `<g clip-path="url(#c-${key})">`
    + dot(px, py, pr, 'url(#g-pupil)')
    + `<rect x="${cx - rx - 4}" y="${cy - ry - 4}" width="${2 * rx + 8}" height="${n(ry * 1.3)}" fill="url(#g-lid)"/>`
    + dot(n(px - pr * 0.42), n(py - pr * 0.5), n(pr * 0.3), '#fff')
    + dot(n(px + pr * 0.55), n(py + pr * 0.1), n(pr * 0.14), '#fff', 0.95)
    + `</g>`
    + `<g class="a-blink" opacity="0"><path d="${lid}" fill="url(#g-eyelid)"/>${line(lash, '#2b2238', 2.8)}</g>`
    + shape(brow, '#36304e') + shape(browHi, '#6d6390', 0.9);
}

// ---------- les morceaux, du fond vers le devant ----------
const parts = [
  { id: 'wingL', cls: 'a-wL', d: S.wingL, body: clip('wingL', wingLBody()) },
  { id: 'wingR', cls: 'a-wR', d: S.wingR, body: clip('wingR', wingRBody()) },
  { id: 'tail', cls: 'a-tail', d: S.tail, shadow: [{ on: ['wingL'], dx: -3, dy: 4, color: SH.wing, o: 0.3 }], body: clip('tail', tailBody()) },
  { id: 'footL', cls: 'a-fL', d: S.footL, shadow: [{ on: ['tail'], dx: -3, dy: 4, color: SH.claw, o: 0.35 }],
    body: footBody('footL') },
  { id: 'footR', cls: 'a-fR', d: S.footR, shadow: [{ on: ['tail'], dx: -3, dy: 4, color: SH.claw, o: 0.35 }],
    body: footBody('footR') },
  { id: 'body', cls: 'a-body', d: S.body,
    shadow: [{ on: ['wingL', 'wingR'], dx: -4, dy: 5, color: SH.wing, o: 0.3 }, { on: ['tail', 'footL', 'footR'], dx: -2, dy: 4, color: SH.claw, o: 0.35 }],
    body: use('body', 'url(#g-body)') + clip('body',
      // le flanc gauche, dans l'ombre de l'aile : son bord est fait de mèches
      shape(sm('178,140 188,150 191,168 187,188 191,210 183,226 170,214 166,196 167,174 171,154'), SNOW.mid, 0.6)
      // le dessous rond du ventre, dans l'ombre, entre les deux pattes
      + shape(sm('200,222 222,234 246,236 266,230 282,214 290,206 284,224 274,240 252,250 220,250 198,244'), SNOW.mid, 0.75)
      // la culotte de plumes de gauche : une cuisse ronde, ombrée à gauche, son bas en mèches sur la cheville
      + `<path d="${THIGH_L}" transform="translate(-3 4)" fill="${SH.snow}" opacity="0.25"/>`
      + shape(THIGH_L, 'url(#g-thigh)')
      + shape(sm('178,206 190,202 200,210 196,222 190,236 183,238! 176,230'), LAV.base, 0.55)
      + line('M199 200 C207 203 213 212 216.5 224 C218.6 232 218.8 239 216 244', SNOW.deep, 1.4, 0.75)
      // la culotte de droite, éclairée
      + `<path d="${THIGH_R}" transform="translate(-3 4)" fill="${SH.snow}" opacity="0.22"/>`
      + shape(THIGH_R, 'url(#g-thighR)')
      // les mouchetures du harfang : des bandes ondulées, lavande, de longueurs différentes
      + MARKS.map(([x0, y0, len, k, o]) => shape(bar(x0, y0, len, k), SNOW.deep, o)).join('')
      // le ventre arrondi : une lumière douce à droite
      + oval(282, 178, 24, 30, 'url(#g-soft)', 0.7, -20)
    ) },
  // les aigrettes sortent du crâne : leur ombre s'efface vers la base, la tête les recouvre sans trait ni ombre
  { id: 'tuftL', cls: 'a-tL', d: S.tuftL, body: use('tuftL', 'url(#g-head)') + clip('tuftL',
      shape(sm('212,15! 219,30 224,48 214,52 210,34'), 'url(#g-tuftSh)')
      + shape(sm('224,22 236,28 246,36 236,32'), '#ffffff', 0.9)) },
  { id: 'tuftR', cls: 'a-tR', d: S.tuftR, body: use('tuftR', 'url(#g-head)') + clip('tuftR',
      shape(sm('316,18! 311,32 312,50 302,50 307,31'), 'url(#g-tuftSh)')
      + shape(sm('316,20! 316,34 317,48 319,34'), '#ffffff', 0.8)) },
  { id: 'head', cls: 'a-head', d: S.head,
    shadow: [{ on: ['body'], dx: -3, dy: 6, color: SH.snow, o: 0.3 }, { on: ['wingL', 'wingR'], dx: -4, dy: 5, color: SH.wing, o: 0.3 }],
    body: use('head', 'url(#g-head)') + clip('head',
      // le côté gauche du crâne, tourné vers l'ombre, et son bord qui s'arrondit
      shape(sm('220,40 204,52 194,68 188,90 186,114 190,136 200,150 216,160 238,166 236,152 222,140 214,116 215,92 222,72 232,54'), SNOW.mid, 0.5)
      + shape(sm('206,52 194,68 188,90 186,114 190,136 200,150 208,154 199,132 196,110 198,86'), SNOW.deep, 0.3)
      // la lumière du dessus de la tête, à droite, et deux mèches sur le crâne
      + oval(296, 48, 34, 15, 'url(#g-soft)', 0.9, 8)
      + shape(sm('240,40! 250,46 262,58! 248,52'), SNOW.mid, 0.55) + shape(sm('278,36! 289,45 297,57! 285,50'), SNOW.mid, 0.45)
      // le disque facial, plus clair, bordé de sa collerette
      + ruff + shape(DISC, 'url(#g-disc)')
      // l'arcade au-dessus de chaque œil
      + shape(sm('226,66! 240,63 258,68 276,78 292,92! 276,86 258,77 240,71'), SNOW.mid, 0.7)
      + shape(sm('292,92! 302,78 316,68 332,64! 320,72 306,82'), SNOW.mid, 0.6)
    )
    // les yeux sont enfoncés dans le disque : une ombre douce sous chaque anneau
    + oval(252.5, 100.5, 23, 19.5, SNOW.mid, 0.4) + oval(307.5, 102.5, 17, 20, SNOW.mid, 0.35)
    // les yeux : celui de gauche (proche) en grand, celui de droite (fuyant) plus étroit
    + eye('eL', 254.5, 97, 19.5, 15.8, 261, 97.5, 10.4,
      sm('229,74! 246,73 266,80 290,95! 288,103 278,99.5 264,93 250,87.5 238,84'),
      sm('233,75 248,75 266,82 285,93 266,85.5 249,78.5'),
      'M229.6 97.3a24.9 21.4 0 1 0 49.8 0a24.9 21.4 0 1 0 -49.8 0Z', 'M235 99 C246 105.5 264 105.5 275 98')
    + eye('eR', 309.5, 99, 13.2, 16.2, 306.5, 99.5, 8.2,
      sm('291,101! 299,91 311,83 325,78! 325,84.5 316,89 306,95 298,101.5 295,105'),
      sm('294,98 302,90 313,84 322,80 312,86.5 301,93'),
      'M293.3 99.3a16.2 19.6 0 1 0 32.4 0a16.2 19.6 0 1 0 -32.4 0Z', 'M297 101 C303 106 315 106 322 100') },
  { id: 'jaw', cls: 'a-jaw', d: S.jaw, body: clip('jaw',
      use('jaw', 'url(#g-mouth)')
      // la langue, rose, au fond de la gueule
      + shape(sm('271.5,142 273.5,137 278.5,135.5 283,138 281.5,143 276,144.5'), '#b04460') + shape(sm('274,138.5 277.5,137 280.5,138.4 276.6,139.6'), '#ee93a3', 0.85)
      // le bord de la mandibule du bas, et ses deux petites pointes pâles
      + shape(sm('269,142.6 276,145.6 283,146.9! 284.6,141.8 286.6,147.6! 290.4,147.2! 292.3,141.6 294.4,146.3! 299,143.4 302,147 296,150 286,151 276,149 268,145'), 'url(#g-jaw)')
    ) + `<use href="#s-jaw" fill="none" stroke="#2a0812" stroke-width="1.6" opacity="0.85"/>` },
  { id: 'beak', cls: 'a-beak', d: S.beak, shadow: [{ on: ['head', 'jaw'], dx: -2, dy: 4, color: SH.snow, o: 0.38 }],
    body: use('beak', 'url(#g-beak)') + clip('beak',
      // l'arête du bec dans la lumière, et le dessous du crochet dans l'ombre
      shape(sm('296,103 301,104.5 304.5,110 306,118 305.5,126 303.5,133 300,140 302,128 302.5,118 300,110'), '#e6dfc6', 0.95)
      + shape(sm('272,125 280,124 288,125 294,128.5 298,134 299,143.5 294,134 287,129 279,127.5'), BEAK.deep, 0.6)
      + oval(289, 108.5, 3.2, 1.6, '#ffffff', 0.35, -40)
    ) },
];

// ---------- la vie au repos : de lents et puissants battements d'ailes ----------
// Les deux ailes battent ensemble (un oiseau !) ; quand elles s'abaissent, l'oiseau monte. La tête, les aigrettes, le
// bec, la queue et les serres ont chacun leur rythme. Chaque mouvement part de la pose du dessin (0 % = repos) :
// l'attaque s'y termine exactement, le passage de l'une à l'autre ne se voit pas.
// ---------- l'attaque (0,75 s, classe « atk » sur le <svg>) ----------
// élan (0-35 %) : les ailes montent haut, la tête recule, les serres se replient ; coup (35-55 %) : les ailes battent
// vers le bas d'un coup, tout l'oiseau fond vers la droite, la tête et le bec grand ouvert en avant, les serres
// jaillissent vers l'avant ; retour (55-100 %).
const style = `
.a-root{transform-origin:238px 160px;animation:bob 1.9s ease-in-out infinite}
.a-wL{transform-origin:206px 112px;animation:wL 1.9s ease-in-out infinite}
.a-wR{transform-origin:294px 112px;animation:wR 1.9s ease-in-out infinite}
.a-body{transform-origin:240px 246px;animation:body 2.4s ease-in-out infinite alternate}
.a-head{transform-origin:256px 150px;animation:head 3.4s ease-in-out infinite alternate}
.a-tL{transform-origin:226px 50px;animation:tL 2.3s ease-in-out infinite alternate}
.a-tR{transform-origin:302px 50px;animation:tR 2.7s ease-in-out infinite alternate}
.a-jaw{transform-origin:271px 132px;animation:jaw 1.5s ease-in-out infinite alternate}
.a-beak{transform-origin:292px 104px}
.a-tail{transform-origin:222px 236px;animation:tail 2.6s ease-in-out infinite alternate}
.a-fL{transform-origin:204px 240px;animation:fL 2.9s ease-in-out infinite alternate}
.a-fR{transform-origin:257px 240px;animation:fR 3.2s ease-in-out infinite alternate}
.a-blink{animation:blink 5.2s linear infinite}
@keyframes bob{0%,100%{transform:translate(0,0)}55%{transform:translate(0,-5px)}}
@keyframes wL{0%,100%{transform:rotate(0)}50%{transform:rotate(-9deg) scale(1,.94)}}
@keyframes wR{0%,100%{transform:rotate(0)}50%{transform:rotate(9deg) scale(1,.94)}}
@keyframes body{from{transform:scale(1)}to{transform:scale(1.012,1.02)}}
@keyframes head{0%{transform:rotate(0)}60%{transform:rotate(-3deg)}100%{transform:rotate(2deg)}}
@keyframes tL{from{transform:rotate(0)}to{transform:rotate(-6deg)}}
@keyframes tR{from{transform:rotate(0)}to{transform:rotate(6deg)}}
@keyframes jaw{from{transform:rotate(0)}to{transform:rotate(5deg)}}
@keyframes tail{from{transform:rotate(0)}to{transform:rotate(3deg)}}
@keyframes fL{from{transform:rotate(0)}to{transform:rotate(7deg)}}
@keyframes fR{from{transform:rotate(0)}to{transform:rotate(-7deg)}}
@keyframes blink{0%,94%{opacity:0}95%,97.5%{opacity:1}99%,100%{opacity:0}}
.atk .a-root{animation:root-atk .75s ease-in-out}
.atk .a-wL{animation:wL-atk .75s ease-in-out}
.atk .a-wR{animation:wR-atk .75s ease-in-out}
.atk .a-head{animation:head-atk .75s ease-in-out}
.atk .a-tL{animation:tL-atk .75s ease-in-out}
.atk .a-tR{animation:tR-atk .75s ease-in-out}
.atk .a-jaw{animation:jaw-atk .75s ease-in-out}
.atk .a-beak{animation:beak-atk .75s ease-in-out}
.atk .a-tail{animation:tail-atk .75s ease-in-out}
.atk .a-fL{animation:fL-atk .75s ease-in-out}
.atk .a-fR{animation:fR-atk .75s ease-in-out}
@keyframes root-atk{0%{transform:none}32%{transform:translate(-9px,-7px)}47%{transform:translate(16px,5px)}62%{transform:translate(11px,3px)}100%{transform:none}}
@keyframes wL-atk{0%{transform:none}32%{transform:rotate(20deg) scale(1,1.04)}47%{transform:rotate(-17deg) scale(1,.88)}62%{transform:rotate(-9deg) scale(1,.94)}100%{transform:none}}
@keyframes wR-atk{0%{transform:none}32%{transform:rotate(-20deg) scale(1,1.04)}47%{transform:rotate(17deg) scale(1,.88)}62%{transform:rotate(9deg) scale(1,.94)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}32%{transform:translate(-4px,-2px) rotate(-7deg)}47%{transform:translate(9px,3px) rotate(7deg)}64%{transform:translate(6px,2px) rotate(4deg)}100%{transform:none}}
@keyframes tL-atk{0%{transform:none}32%{transform:rotate(-10deg)}47%{transform:rotate(8deg)}100%{transform:none}}
@keyframes tR-atk{0%{transform:none}32%{transform:rotate(10deg)}47%{transform:rotate(-8deg)}100%{transform:none}}
@keyframes jaw-atk{0%{transform:none}32%{transform:rotate(3deg)}46%{transform:rotate(17deg)}66%{transform:rotate(12deg)}100%{transform:none}}
@keyframes beak-atk{0%{transform:none}46%{transform:rotate(-4deg)}66%{transform:rotate(-2deg)}100%{transform:none}}
@keyframes tail-atk{0%{transform:none}32%{transform:rotate(-7deg)}47%{transform:rotate(8deg)}64%{transform:rotate(4deg)}100%{transform:none}}
@keyframes fL-atk{0%{transform:none}32%{transform:rotate(12deg)}50%{transform:translate(3px,5px) rotate(-30deg)}68%{transform:translate(2px,3px) rotate(-18deg)}100%{transform:none}}
@keyframes fR-atk{0%{transform:none}32%{transform:rotate(10deg)}50%{transform:translate(3px,5px) rotate(-26deg)}68%{transform:translate(2px,3px) rotate(-15deg)}100%{transform:none}}
`.replace(/\n/g, '');

// ---------- le rendu ----------
/** Enveloppe chaque groupe de classe `cls` dans un groupe de classe `outer` (la tête emporte le bec, la mâchoire, les aigrettes). */
function nest(s, cls, outer) {
  const open = `<g class="${cls}">`;
  let i = s.indexOf(open);
  while (i >= 0) {
    // la fin du groupe : on compte les groupes ouverts et fermés
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
  let s = figure({ w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  for (const c of ['a-tL', 'a-tR', 'a-jaw', 'a-beak']) s = nest(s, c, 'a-head');
  // tout l'oiseau monte et descend avec ses battements d'ailes
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'glaces-4', w: W, h: H, pad: PAD, foot: [234, 322], svg };
