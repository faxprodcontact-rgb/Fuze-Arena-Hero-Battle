// La fée à la flûte (assassins-12) : redessinée par le code d'après le dessin d'origine, dans le même cadre
// (510 × 551, mêmes proportions, même pose) : chignon vert surmonté d'une fleur blanche, oreille pointue, yeux fermés
// de bonheur, joues roses, flûte de bois tenue à deux mains vers la droite, deux ailes bleu pâle translucides, robe
// de feuilles, bottes vertes, sur la pointe des pieds (elle flotte).
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 510, H = 551, PAD = 44;

// ---------- courbes lisses ----------
/**
 * Chemin lisse passant par des points (spline de Catmull-Rom, tangentes mesurées sur les distances : pas de boucle).
 * `src` = "x,y x,y! …" : un point suivi de « ! » est un angle vif (pointe de feuille, bout d'aile).
 */
function sm(src, closed = true) {
  const pts = (Array.isArray(src) ? src.join(' ') : src).trim().split(/\s+/).map((s) => {
    const sharp = s.endsWith('!');
    const [x, y] = s.replace('!', '').split(',').map(Number);
    return { x, y, sharp };
  });
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

/** Un fuseau effilé aux deux bouts (mèche, nervure, cil) : de `a` à `b`, épais de `w` au milieu, courbé de `bend`. */
function spindle(ax, ay, bx, by, w, bend = 0) {
  const L = Math.hypot(bx - ax, by - ay) || 1, nx = -(by - ay) / L, ny = (bx - ax) / L;
  const mx = (ax + bx) / 2 + nx * bend, my = (ay + by) / 2 + ny * bend;
  return sm(`${P(ax, ay)}! ${P(mx + nx * w / 2, my + ny * w / 2)} ${P(bx, by)}! ${P(mx - nx * w / 2, my - ny * w / 2)}`);
}

// ---------- couleurs ----------
const HAIR = { hi: '#f4ffd6', lite: '#bdef93', base: '#7ad06d', mid: '#5cb35f', deep: '#3f8e4e', line: '#2c6a3e' };
const SKIN = { hi: '#fff4e6', base: '#fcdcbc', shade: '#f0b897', deep: '#df997c', line: '#b5684f' };
const LEAF = { hi: '#e4fcba', lite: '#a9ea8a', base: '#76d06a', mid: '#58b55b', deep: '#3b8b49', line: '#2a6939' };
const WOOD = { hi: '#ffecb0', lite: '#f6c868', base: '#e0a447', mid: '#c4823a', shade: '#985a24', line: '#6c3a15' };
const GOLD = { hi: '#fff3b0', base: '#f1c548', mid: '#d79a22', shade: '#9c6510', line: '#6e430a' };
// les ombres portées : une teinte par matière qui la reçoit
const SH = { skin: '#c4664a', hair: '#1f5a33', leaf: '#245a30', wood: '#5c3010' };

// ---------- la flûte : un tube droit, des lèvres au bout de droite ----------
const FL = { ax: 288, ay: 289, bx: 498, by: 243, r0: 9.2, r1: 8.2 };
const FU = (() => { const L = Math.hypot(FL.bx - FL.ax, FL.by - FL.ay); return { x: (FL.bx - FL.ax) / L, y: (FL.by - FL.ay) / L, L }; })();
const FN = { x: -FU.y, y: FU.x }; // la normale : vers le dessous de la flûte
const FA = (Math.atan2(FU.y, FU.x) * 180) / Math.PI; // son angle
/** Un point de la flûte : `t` le long (0 = lèvres, 1 = bout), `s` en travers (-1 = dessus, 1 = dessous). */
const fp = (t, s = 0, k = 1) => {
  const r = (FL.r0 + (FL.r1 - FL.r0) * Math.max(0, Math.min(1, t))) * k;
  return [FL.ax + FU.x * FU.L * t + FN.x * r * s, FL.ay + FU.y * FU.L * t + FN.y * r * s];
};
const fq = (t, s, k) => P(...fp(t, s, k));

// ---------- dégradés ----------
const defs = [
  // les ailes : bleu pâle et translucides, plus soutenues vers la racine, bordure lavande
  lin('g-wingU', 226, 314, 30, 110, [[0, '#6fbde8'], [0.28, '#a9dff9'], [0.62, '#ddf4ff'], [1, '#f4fbff']]),
  lin('g-wingD', 226, 366, 70, 440, [[0, '#6fbde8'], [0.35, '#afe1f9'], [0.75, '#def4ff'], [1, '#f2faff']]),
  lin('g-rim', 0, 0, 1, 1, [[0, '#eee6fd'], [0.45, '#cdbcee'], [1, '#a891d6']], false),
  lin('g-rimD', 0, 0, 1, 0, [[0, '#ad97da'], [0.5, '#cdbcee'], [1, '#e6dcfa']], false),
  // la chevelure : éclairée à droite (presque jaune pâle), plus sombre à gauche et en bas
  lin('g-hair', 404, 92, 176, 236, [[0, '#d0f5a0'], [0.28, '#98e07e'], [0.6, '#72ca69'], [1, '#56a95a']]),
  lin('g-hairB', 0, 180, 0, 300, [[0, '#4a9853'], [1, '#2f7341']]),
  rad('g-bun', 0.66, 0.28, 0.8, [[0, '#f0ffd2'], [0.3, '#b9ec93'], [0.75, '#7ccd6d'], [1, '#56aa5a']], false),
  lin('g-skin', 0, 0, 0, 1, [[0, '#ffeedd'], [0.5, SKIN.base], [1, '#f8caa7']], false),
  rad('g-cheek', 0.5, 0.5, 0.5, [[0, '#f67a74', 0.8], [0.55, '#f88a7e', 0.5], [1, '#f99a88', 0]], false),
  rad('g-soft', 0.5, 0.5, 0.5, [[0, '#fff7ec', 0.9], [1, '#fff7ec', 0]], false),
  lin('g-ear', 104, 190, 192, 244, [[0, '#fff0e0'], [0.55, '#fcdcbc'], [1, '#f2ba98']]),
  lin('g-sleeve', 0, 290, 0, 352, [[0, '#a2e68b'], [0.45, '#76d06a'], [1, '#4fa757']]),
  // les bouffants de la manche : chacun bombé, éclairé en haut à droite
  rad('g-puff0', 240, 312, 34, [[0, '#9be385'], [0.6, '#74cd68'], [1, '#55ad5a']]),
  rad('g-puff1', 282, 312, 34, [[0, '#a4e78b'], [0.6, '#78d06b'], [1, '#57b05b']]),
  rad('g-puff2', 312, 306, 30, [[0, '#a8e98e'], [0.6, '#7ad26c'], [1, '#5ab35c']]),
  rad('g-puff3', 338, 300, 26, [[0, '#acea90'], [0.6, '#7ed46e'], [1, '#5db65e']]),
  lin('g-torso', 226, 0, 354, 0, [[0, '#4fa757'], [0.55, '#72cd68'], [1, '#a0e48b']]),
  lin('g-skirt', 165, 0, 385, 0, [[0, '#3f9450'], [0.5, '#5fbb5e'], [1, '#93dc7b']]),
  lin('g-leg', 0, 0, 1, 0, [[0, '#efbb9b'], [0.45, '#fcdcbc'], [1, '#fff1e0']], false),
  lin('g-boot', 0, 0, 1, 0, [[0, '#479e52'], [0.5, '#74cd68'], [1, '#b2eb8f']], false),
  lin('g-wood', ...fp(0, -1).map(n), ...fp(0, 1).map(n), [[0, WOOD.hi], [0.28, WOOD.lite], [0.6, WOOD.base], [1, WOOD.shade]]),
  lin('g-gold', 0, 0, 0, 1, [[0, GOLD.hi], [0.45, GOLD.base], [1, GOLD.shade]], false),
  lin('g-goldS', 0, 0, 1, 0, [[0, GOLD.shade], [0.5, GOLD.mid], [1, '#e9b23a']], false),
  rad('g-petal', 0.62, 0.25, 0.85, [[0, '#ffffff'], [0.55, '#fbfcff'], [1, '#d3dcee']], false),
  rad('g-heart', 0.38, 0.32, 0.75, [[0, '#fff8c0'], [0.5, '#f8d240'], [1, '#d8961a']], false),
  rad('g-finger', 0.6, 0.28, 0.8, [[0, '#ffeedd'], [0.55, '#fbd9b8'], [1, '#f2c09f']], false),
  rad('g-glow', 0.5, 0.5, 0.5, [[0, '#ffffff', 1], [0.3, '#f6ffd8', 0.85], [1, '#d6ffb0', 0]], false),
  rad('g-ring', 0.5, 0.5, 0.5, [[0.55, '#fffbe0', 0], [0.78, '#fffbe0', 0.9], [1, '#fff3a0', 0]], false),
  lin('g-note', 0, 0, 0, 1, [[0, '#d8ffb8'], [0.5, '#7fd86e'], [1, '#3f9a52']], false),
].join('');

// ---------- silhouettes ----------
const S = {
  // les deux ailes, derrière le dos : la grande en haut (pointe vers le haut à gauche), la petite en bas
  wingU: sm('17,96! 30,104 47,121 63,139! 74,142 96,148 122,156 150,169 188,222 222,282 236,300 238,326 224,336 196,337 162,332 130,321 101,301 74,274 47,240 28,207 16,172 10,138 11,112'),
  wingD: sm('62,441! 70,418 86,394 108,373 132,360 160,351 190,347 218,346 236,352 238,378 214,404 184,420 160,428 130,435 98,441'),
  bun: sm('226,46 233,24 250,11 270,8 291,11 307,23 313,42 309,60 296,74 270,80 244,74 230,62'),
  // la chevelure de derrière : tout le crâne, et deux pointes de la nuque sous l'oreille
  hairB: sm('230,73 204,86 180,106 163,134 155,164 154,196 157,226 161,248 168,266 176,283! 186,281 197,298! 208,296 222,302 250,292 300,272 360,258 404,240 416,200 417,170 414,142 405,118 390,90 360,72 320,64 290,66 258,66'),
  // les jambes, sous la jupe : la pointe des bottes vers le bas
  legL: sm('224,440 221,462 219,478 215,490 212,504 213,519 218,530 225,537 232,540 239,536 245,527 248,512 250,496 252,484 255,468 257,446'),
  legR: sm('276,446 278,466 274,482 267,497 262,510 261,524 265,535 272,540 280,537 288,528 295,515 299,502 306,493 316,485 325,471 329,450'),
  // le bras du fond : il sort de derrière le buste et monte vers la main de droite
  armF: sm('336,316 352,305 372,299 392,295 410,290 426,286 441,284 449,292 447,303 437,315 422,330 405,343 390,353! 378,347 362,349 347,348 337,338'),
  torso: sm('232,298 262,292 300,290 336,294 352,304 356,326 352,350 346,374 342,396 300,404 254,402 228,396 224,372 222,346 224,318'),
  // la robe de feuilles : chaque pointe est une feuille
  skirt: sm('230,385 290,394 340,386 352,402 364,420 376,434 384,446! 372,451 364,456 354,472! 343,461 333,459 320,466! 310,458 300,462 286,476! 276,463 266,463 254,472! 244,461 233,461 218,469! 210,456 203,452 191,459! 186,448 177,445 164,441! 172,427 186,413 202,400 216,391'),
  belt: sm('226,382 258,389 292,393 322,389 344,381 346,390 323,399 292,403 257,399 227,392'),
  // le bras de devant, plié devant la poitrine : épaule à gauche, poignet sous la main près de la bouche
  armN: sm('221,322 224,306 232,298 246,296 260,300 276,300 294,297 312,294 330,290 346,290 356,296 359,306 354,316 342,322 326,330 304,338 282,344 262,348 244,350 230,346 222,336'),
  // la tête
  earR: sm('400,196 412,195 421,199! 415,206 406,213 398,212'),
  earL: sm('108,190! 132,193 156,198 180,205 194,214 196,236 192,250 186,253 176,248 158,236 138,221 121,204'),
  face: sm('216,152 207,196 201,232 201,258 210,275 228,288 250,296 272,299 300,296 340,288 374,276 388,262 396,246 399,226 401,200 404,160 392,124 340,108 270,116'),
  // la chevelure de devant : le dôme, la frange en biais, la mèche qui couvre la racine de l'oreille, la mèche de droite
  cap: sm('229,73 204,86 180,106 163,134 155,164 155,192 166,199 180,204 188,210 192,229 198,248 204,262 207,271! 211,257 214,238 218,218 223,200 228,183 250,176 272,171 288,166 302,160 312,154 318,160 324,168! 328,157 334,154 338,164! 340,148 342,128! 357,146 374,165 388,180 396,198 397,222 396,250! 404,226 411,206 416,190 417,170 414,142 405,118 397,104 390,90 370,74 346,67 318,63 290,66 258,66'),
  bud: sm('358,65 360,59 366,56 372,59 374,65 369,70 362,70'),
  flower: '', flute: '', handN: '', handF: '',
};

// la fleur : cinq pétales arrondis autour du cœur (angle, longueur)
const FC = { x: 367, y: 95 };
const PETALS = [[203, 28], [279, 28], [13, 33], [64, 27], [140, 28]];
const pol = (a, r) => [FC.x + Math.cos((a * Math.PI) / 180) * r, FC.y + Math.sin((a * Math.PI) / 180) * r];
S.flower = sm(PETALS.flatMap(([a, r], i) => {
  const next = PETALS[(i + 1) % PETALS.length][0];
  const mid = a + (((next - a + 360) % 360) / 2);
  return [[a - 27, r * 0.8], [a - 13, r * 0.97], [a, r * 1.02], [a + 13, r * 0.97], [a + 27, r * 0.8], [mid, 15]].map(([aa, rr]) => P(...pol(aa, rr)));
}).join(' '));

// la flûte : bout gauche arrondi (le nœud du bois), bague un peu plus large au bout de droite
S.flute = sm([fq(-0.035, -0.4), ...[0, 0.25, 0.5, 0.75, 0.92].map((t) => fq(t, -1)), `${fq(0.928, -1.22)}!`, fq(0.97, -1.2), `${fq(1.004, -1.0)}`, fq(1.012, 0), fq(1.004, 1.0), fq(0.97, 1.2), `${fq(0.928, 1.22)}!`,
  ...[0.92, 0.75, 0.5, 0.25, 0].map((t) => fq(t, 1)), fq(-0.035, 0.4)]);

// ---------- les mains : quatre doigts repliés sur la flûte, les jointures au-dessus ----------
/** Une main en poing sur la flûte : `fingers` = [x du haut, y du haut, x du bas, y du bas, largeur] pour chaque doigt. */
function fist(fingers, heel) {
  // la silhouette : le talon de la main, puis un renflement par doigt
  const outline = sm(heel);
  const body = fingers.map(([tx, ty, bx, by, w], i) => {
    const L = Math.hypot(bx - tx, by - ty), ux = (bx - tx) / L, uy = (by - ty) / L, nx = -uy, ny = ux, h = w / 2;
    const d = sm([P(tx + nx * h * 0.9, ty + ny * h * 0.9), P(tx - ux * h * 0.6, ty - uy * h * 0.6), P(tx - nx * h * 0.9, ty - ny * h * 0.9),
      P(bx - nx * h, by - ny * h), P(bx + ux * h * 0.8, by + uy * h * 0.8), P(bx + nx * h, by + ny * h)]);
    return { d, tx, ty, bx, by, w, nx, ny, ux, uy, i };
  });
  return { outline, body };
}
const NEAR = fist([[345.5, 266, 343.5, 291, 10.6], [356.5, 263, 355.5, 294, 11.4], [367.5, 264, 367, 294, 11], [378, 269, 378.5, 291, 9.6]],
  '337,292 338,276 340,266 346,260 352,260 357,257 363,258 368,258 374,261 380,263 385,268 389,276 390,286 388,296 381,304 367,308 352,307 342,301');
const FAR = fist([[423, 245, 421.5, 270, 10.4], [434.5, 240, 434, 273, 11.2], [446, 240, 446, 272, 10.8], [456.5, 246, 456, 267, 9.4]],
  '414,270 415,256 417,246 422,240 428,239 433,235 440,234 445,235 451,236 456,239 461,244 463,252 463,262 460,272 454,282 443,290 429,292 418,286');
S.handN = NEAR.outline; S.handF = FAR.outline;

/** L'habillage d'une main : le creux entre les doigts (plus sombre), chaque doigt bombé et éclairé, le talon dans l'ombre. */
function fistBody(id, F, heelShade) {
  return use(id, '#ecb393') + clip(id,
    shape(heelShade, '#e3a283', 0.85)
    + F.body.map((f) => shape(f.d, 'url(#g-finger)')
      // le reflet de la jointure, en haut du doigt
      + oval(n(f.tx + f.ux * 2.5 + f.nx * 1.2), n(f.ty + f.uy * 2.5 + f.ny * 1.2), n(f.w * 0.28), 2, SKIN.hi, 0.9, FA)).join('')
    // les bouts des doigts repliés sous la flûte : le bas du poing passe dans l'ombre
    + `<path d="${heelShade}" transform="translate(0 -9)" fill="${SKIN.shade}" opacity="0.45"/>`);
}

// ---------- les yeux fermés : un trait épais en arc, deux cils à l'extérieur ----------
const EYE_L = sm('246,237! 250,226 258,216 272,209 288,210 299,218 306,234! 299,228 290,221 278,217 265,218 255,226');
const EYE_R = sm('341,237! 345,226 355,217 367,213 378,215 384,223 385,238! 380,229 373,222 364,221 354,225 347,231');
const LASH_L = spindle(251, 224, 240, 212, 3.4, -0.6) + spindle(249, 230, 238, 227, 3, 0.4);
const LASH_R = spindle(381, 222, 391, 210, 3.4, 0.6) + spindle(384, 229, 394, 226, 3, -0.4);

// ---------- la robe : des feuilles pliées en deux qui se recouvrent, des côtés vers le devant ----------
// chaque feuille : le milieu de sa base (sous la ceinture), sa pointe, sa largeur, et sa teinte (0 = ombre, 1 = lumière)
const LEAVES = [
  { base: [238, 390], tip: [164, 441], w: 30, k: 0 },
  { base: [344, 388], tip: [384, 446], w: 26, k: 1 },
  { base: [252, 394], tip: [191, 459], w: 34, k: 0.15 },
  { base: [334, 392], tip: [354, 472], w: 34, k: 0.9 },
  { base: [266, 397], tip: [218, 469], w: 36, k: 0.3 },
  { base: [318, 396], tip: [320, 466], w: 36, k: 0.75 },
  { base: [282, 399], tip: [254, 472], w: 38, k: 0.45 },
  { base: [300, 399], tip: [286, 476], w: 38, k: 0.6 },
];
const mix = (c1, c2, k) => '#' + [0, 2, 4].map((i) => Math.round(parseInt(c1.slice(1 + i, 3 + i), 16) * (1 - k) + parseInt(c2.slice(1 + i, 3 + i), 16) * k).toString(16).padStart(2, '0')).join('');
function leafGeo({ base, tip, w }) {
  const [bx, by] = base, [tx, ty] = tip, L = Math.hypot(tx - bx, ty - by), ux = (tx - bx) / L, uy = (ty - by) / L, nx = -uy, ny = ux;
  const at = (f, s) => P(bx + ux * L * f + nx * w * s, by + uy * L * f + ny * w * s);
  // `s` > 0 : le bord de droite (vu de face, la pointe en bas) ; la feuille est la plus large aux deux cinquièmes
  const right = [at(-0.05, 0.3), at(0.4, 0.5), at(0.75, 0.3)], left = [at(0.75, -0.3), at(0.4, -0.5), at(-0.05, -0.3)];
  const vein = [at(-0.05, 0), at(0.5, 0.03), `${P(tx, ty)}!`];
  return {
    all: sm([...right, `${P(tx, ty)}!`, ...left]),
    // les deux moitiés, de part et d'autre de la nervure
    half1: sm([...vein, ...[...right].reverse()]),
    half2: sm([...vein, ...left]),
    vein: `M${at(0.02, 0)} Q${at(0.5, 0.04)} ${at(0.92, 0)}`,
    tip: [tx, ty], nx, ny, ux, uy,
  };
}
function skirtBody() {
  let s = '';
  LEAVES.forEach((Lf) => {
    const g = leafGeo(Lf);
    // la moitié qui regarde la lumière (vers la droite) est plus claire
    const litRight = g.nx > 0 ? g.half1 : g.half2, shadeLeft = g.nx > 0 ? g.half2 : g.half1;
    s += `<path d="${g.all}" transform="translate(-3 4)" fill="${SH.leaf}" opacity="0.34"/>`;
    s += shape(shadeLeft, mix('#4a9f52', '#76cf69', Lf.k));
    s += shape(litRight, mix('#6cc362', '#c9f3a2', Lf.k));
    s += line(g.vein, mix('#2f7040', '#4f9e4f', Lf.k), 1.3, 0.6);
  });
  return s;
}

// ---------- la manche de devant : l'épaule bombée, puis des bouffants de plus en plus petits jusqu'au poignet ----------
const armTop = (x) => 312 - (x - 255) * 0.25, armBot = (x) => 349 - (x - 255) * 0.34;
// le bord gauche de chaque bouffant (il recouvre le précédent) ; ils rapetissent vers la main, qui vient vers nous
const PUFFS = [[257, 'g-puff1'], [291, 'g-puff2'], [321, 'g-puff3']];
function sleeveBody() {
  let s = '';
  PUFFS.forEach(([x], i) => {
    const t = armTop(x + 8), b = armBot(x + 8), m = (t + b) / 2;
    const d = sm(`${P(x + 10, t - 8)} ${P(x + 2, m - (b - t) * 0.3)} ${P(x - 1, m + 1)} ${P(x + 3, b - 3)} ${P(x + 12, b + 8)} ${P(390, b + 8)} ${P(390, t - 10)}`);
    s += `<path d="${d}" transform="translate(-3 3)" fill="${SH.leaf}" opacity="0.42"/>`;
    s += shape(d, `url(#${PUFFS[i][1]})`);
    // la lumière sur le haut du bouffant
    const w = (PUFFS[i + 1] ? PUFFS[i + 1][0] : 350) - x;
    s += shape(sm(`${P(x + 6, t + 4)} ${P(x + w * 0.45, t + 1.5)} ${P(x + w * 0.8, t + 4)} ${P(x + w * 0.45, t + 7.5)}`), LEAF.hi, 0.75);
  });
  // l'épaule, ronde, par-dessus le haut du bras
  s += `<path d="${sm('214,314 224,298 242,295 258,302 264,322 258,344 240,353 220,346')}" transform="translate(-3 3)" fill="${SH.leaf}" opacity="0.3"/>`
    + shape(sm('214,314 224,298 242,295 258,302 264,322 258,344 240,353 220,346'), 'url(#g-puff0)')
    + oval(240, 307, 13, 6.5, LEAF.hi, 0.7, -12);
  // le dessous du bras dans l'ombre
  s += shape(sm('218,334 230,346 248,350 274,348 302,342 328,332 348,321 357,312 352,326 328,340 300,350 270,354 240,354 216,344'), LEAF.deep, 0.45);
  return s;
}

// ---------- ce qui n'apparaît que dans l'image vivante : poussière de fée, onde et notes de l'attaque ----------
/** Une note de musique (même dessin que celles de Ruka), la tête en (x, y), à l'échelle `k`. */
function note(x, y, k) {
  const src = 'M450 128 C450 124 463 122 463 126 L489 141 C493 146 491 152 486 154 L464 142 L465 178 C466 189 456 196 444 197 C432 198 422 191 422 182 C422 172 433 165 444 165 C447 165 449 165 451 166 Z';
  let i = 0;
  return src.replace(/-?\d+(\.\d+)?/g, (v) => n((i++ % 2 ? (+v - 181) * k + y : (+v - 444) * k + x)));
}
const NOTE_A = { x: 488, y: 214, k: 0.42 }, NOTE_B = { x: 470, y: 188, k: 0.34 };
// l'onde et les notes de l'attaque sont rangées dans le dessin de la flûte : elles suivent le haut du corps.
// Ce ne sont pas des morceaux du personnage : chaque note a son propre contour (le trait passe sous la couleur).
const FX_MARK = '<!--fx-->';
const noteFx = (N, c) => `<g class="${c}"><path d="${note(N.x, N.y, N.k)}" fill="url(#g-note)" stroke="#2a1430" stroke-width="${n(8.8 * N.k * 1.6)}" stroke-linejoin="round" paint-order="stroke"/>`
  + `${oval(N.x - 2.5, N.y - 2.5, n(11 * N.k), n(6.6 * N.k), '#f2ffe0', 0.9, -20)}</g>`;
const TIP = fp(1.02, 0); // le bout de la flûte, d'où part le son
// la poussière de fée : de petites lueurs qui montent et s'éteignent près des ailes
const DUST = [[118, 300, 4.2, 'a-d1'], [70, 372, 3.4, 'a-d2'], [176, 236, 3.6, 'a-d3'], [150, 410, 3, 'a-d4']];
const dust = DUST.map(([x, y, r, c]) => `<g class="${c}" style="transform-origin:${x}px ${y}px">${dot(x, y, r * 2.4, 'url(#g-glow)', 0.8)}${dot(x, y, r * 0.55, '#ffffff')}</g>`).join('');

// ---------- les morceaux, du fond vers le devant ----------
const UP = 'a-up';
const parts = [
  // --- les ailes : membrane translucide, bordure lavande opaque, quelques nervures ---
  { id: 'wingU', cls: 'a-wu', d: S.wingU, body: clip('wingU',
      `<g opacity="0.8">${use('wingU', 'url(#g-wingU)')}`
      // des voiles plus clairs dans la membrane
      + shape(sm('214,300 170,250 118,190 62,126 104,172 156,232 200,286'), '#ffffff', 0.55)
      + shape(sm('212,316 160,300 96,262 48,214 84,262 140,296 196,318'), '#ffffff', 0.35)
      + `</g>`
      // la bordure : une bande lavande le long du bord extérieur, plus large vers la pointe
      + shape(sm('17,96! 30,104 47,121 63,139! 74,142 96,148 122,156 150,169 124,163 98,157 76,152 56,138 38,121 26,112 21,126 22,150 30,178 42,206 60,236 86,266 114,290 142,308 170,320 198,326 226,328 226,336 196,337 162,332 130,321 101,301 74,274 47,240 28,207 16,172 10,138 11,112'), 'url(#g-rim)')
      + shape(sm('26,112 38,121 56,138 76,152 98,157 72,150 52,136 36,122'), '#ffffff', 0.5)
      // nervures : quelques lignes claires qui partent de la racine, de longueurs inégales
      + line('M224 306 C178 262 112 196 40 120', '#ffffff', 2.4, 0.9)
      + line('M222 314 C172 288 114 250 62 220', '#ffffff', 1.7, 0.7)
      + line('M224 322 C188 316 150 304 116 284', '#ffffff', 1.5, 0.6)
      + line('M216 300 C192 256 156 212 112 174', '#ffffff', 1.3, 0.5)
    ) },
  { id: 'wingD', cls: 'a-wd', d: S.wingD, body: clip('wingD',
      `<g opacity="0.8">${use('wingD', 'url(#g-wingD)')}`
      + shape(sm('222,362 176,380 122,408 80,432 124,416 178,392'), '#ffffff', 0.5)
      + `</g>`
      + shape(sm('62,441! 70,418 86,394 108,373 132,360 160,351 190,347 218,346 190,353 162,358 136,368 114,382 96,400 82,424 80,432 102,432 130,426 158,420 184,412 214,404 184,420 160,428 130,435 98,441'), 'url(#g-rimD)')
      + line('M226 360 C178 376 122 404 76 434', '#ffffff', 2.2, 0.9)
      + line('M222 354 C182 358 140 368 104 386', '#ffffff', 1.5, 0.6)
      + line('M222 372 C192 390 160 406 128 422', '#ffffff', 1.4, 0.55)
    ) },

  // --- la poussière de fée, entre les ailes et le corps (image vivante seulement) ---
  { id: 'dust', fx: true, d: '', body: dust },

  // --- la chevelure de derrière et le chignon ---
  { id: 'bun', cls: UP, d: S.bun, body: use('bun', 'url(#g-bun)') + clip('bun',
      shape(sm('228,56 231,34 242,19 258,12 246,26 238,44 240,66'), HAIR.mid, 0.4)
      + shape(sm('272,14 292,14 306,26 311,40 302,30 288,21'), HAIR.hi, 0.9)
      + oval(293, 27, 8, 4, '#ffffff', 0.6, 32)
      + shape(sm('240,62 270,70 300,64 296,76 270,82 244,76'), HAIR.deep, 0.35)
    ) },
  { id: 'hairB', cls: UP, d: S.hairB, body: use('hairB', 'url(#g-hairB)') + clip('hairB',
      shape(spindle(160, 230, 180, 282, 9, 2), HAIR.base, 0.55)
      + shape(spindle(178, 248, 198, 296, 8, 2), HAIR.mid, 0.6)
    ) },

  // --- les jambes ---
  { id: 'legL', cls: 'a-legL', d: S.legL, body: use('legL', 'url(#g-leg)') + clip('legL',
      shape(sm('224,456 230,468 229,482 222,478'), SKIN.shade, 0.5)
      // la botte, son revers de feuilles et sa petite boucle d'or
      + shape(sm('210,487 252,486 252,498 248,512 245,527 239,536 232,540 225,537 218,530 213,519 212,504'), 'url(#g-boot)')
      + shape(sm('216,512 219,526 228,537 221,522'), LEAF.deep, 0.4)
      + shape(sm('244,500 245,514 240,528 242,512'), LEAF.hi, 0.6)
      + shape(sm('210,484 222,490 232,494! 242,489 254,484 254,496 242,499 232,503! 222,499 210,494'), LEAF.hi)
      + line('M212 496 C220 500 226 502 232 503 C238 502 246 500 253 496', LEAF.mid, 1.3, 0.7)
      + dot(232, 497, 2.6, GOLD.base) + dot(231.3, 496.3, 1, GOLD.hi)
    ) },
  { id: 'legR', cls: 'a-legR', d: S.legR, body: use('legR', 'url(#g-leg)') + clip('legR',
      shape(sm('280,468 286,482 282,494 276,484'), SKIN.shade, 0.5)
      // le genou : une lumière douce, pas de trait
      + oval(304, 476, 11, 6, 'url(#g-soft)', 0.8, -20)
      + shape(sm('260,497 307,489 304,500 299,502 295,515 288,528 280,537 272,540 265,535 261,524 261,510'), 'url(#g-boot)')
      + shape(sm('264,514 265,527 272,537 267,523'), LEAF.deep, 0.4)
      + shape(sm('291,510 289,522 283,533 287,520'), LEAF.hi, 0.6)
      + shape(sm('259,494 272,499 284,502! 296,495 309,487 309,498 296,505 284,510! 272,507 259,503'), LEAF.hi)
      + line('M261 505 C270 509 278 510 284 510 C292 508 301 504 308 498', LEAF.mid, 1.3, 0.7)
      + dot(284, 504, 2.6, GOLD.base) + dot(283.3, 503.3, 1, GOLD.hi)
    ) },

  // --- le bras du fond, le buste ---
  { id: 'armF', cls: UP, d: S.armF, body: use('armF', 'url(#g-sleeve)') + clip('armF',
      // le haut de la manche, bouffant, éclairé ; l'avant-bras, plus loin, dans l'ombre de la main
      shape(sm('352,306 372,300 390,297 378,305 360,312'), LEAF.hi, 0.6)
      + shape(sm('398,292 452,280 456,306 430,328 404,346 396,320'), LEAF.mid, 0.75)
      + shape(sm('340,334 376,338 392,334 396,346 390,353! 376,350 350,352'), LEAF.deep, 0.5)
      // le galon d'or qui ferme la manche au coude : il fait le tour du bras (peint d'un bord à l'autre)
      + shape(sm('392,292 401,291 404,316 399,342 390,356 385,354 393,334 396,312'), 'url(#g-goldS)')
      + line('M397 294 C400 312 398 330 392 348', GOLD.hi, 1.2, 0.6)
      // le bracelet du poignet, en travers de l'avant-bras
      + shape(sm('404,289 426,287 450,292 450,303 426,300 405,301'), 'url(#g-gold)')
      + line('M408 291.5 C424 290 438 291 448 294', GOLD.hi, 1.3, 0.85)
    ) },
  { id: 'torso', cls: UP, d: S.torso, shadow: [{ on: ['armF'], dx: -3, dy: 4, color: SH.leaf, o: 0.35 }],
    body: use('torso', 'url(#g-torso)') + clip('torso',
      shape(sm('224,330 240,350 236,376 230,396 222,380'), LEAF.deep, 0.35)
      + shape(sm('326,348 340,342 350,354 346,374 338,394 332,372'), LEAF.hi, 0.5)
      // le cou, dans l'ombre du menton
      + shape(sm('240,292 300,288 336,292 320,304 290,310 256,308'), LEAF.deep, 0.55)
    ) },

  // --- la robe de feuilles et la ceinture ---
  { id: 'skirt', cls: 'a-skirt', d: S.skirt, shadow: [{ on: ['legL', 'legR'], dx: -3, dy: 6, color: SH.skin, o: 0.42 }],
    body: use('skirt', 'url(#g-skirt)') + clip('skirt', skirtBody()) },
  // la ceinture fait le tour de la taille : elle bouge avec le buste (ses deux bouts restent sur les bords du corps)
  { id: 'belt', cls: UP, d: S.belt, shadow: [{ on: ['skirt'], dx: -1, dy: 4, color: SH.leaf, o: 0.38 }],
    body: use('belt', 'url(#g-gold)') + clip('belt',
      line('M228 386 C258 392 292 396 322 392 C330 390 338 387 344 384', GOLD.hi, 1.3, 0.85)
      + shape(sm('226,382 242,386 242,396 227,392'), GOLD.shade, 0.5)
    ) + shape(sm('292,390 302,389 306,396 302,403 292,402'), GOLD.mid) + shape(sm('295,391 301,390 303,395 297,396'), GOLD.hi, 0.9) },

  // --- le bras de devant ---
  { id: 'armN', cls: UP, d: S.armN, shadow: [{ on: ['torso', 'belt', 'skirt', 'armF'], dx: -3, dy: 6, color: SH.leaf, o: 0.42 }],
    body: use('armN', '#62bd5f') + clip('armN', sleeveBody()) },

  // --- la tête ---
  { id: 'earR', cls: UP, d: S.earR, body: use('earR', 'url(#g-skin)') + shape(sm('404,200 414,199 410,205 404,208'), SKIN.shade, 0.6) },
  { id: 'earL', cls: UP, d: S.earL, shadow: [{ on: ['hairB'], dx: -3, dy: 5, color: SH.hair, o: 0.4 }],
    body: use('earL', 'url(#g-ear)') + clip('earL',
      // le creux de l'oreille, rose, et le bord éclairé en haut
      shape(sm('122,201 146,206 170,214 186,226 189,241 176,236 156,224 136,212'), '#eba78f', 0.8)
      + shape(sm('134,205 154,211 172,221 160,219 142,213'), '#d98a78', 0.55)
      + shape(sm('112,192 134,196 158,201 182,208 160,204 136,200'), SKIN.hi, 0.9)
    ) },
  { id: 'face', cls: UP, d: S.face, shadow: [{ on: ['armN', 'torso', 'armF'], dx: -3, dy: 6, color: SH.leaf, o: 0.4 }, { on: ['hairB', 'earL'], dx: -3, dy: 5, color: SH.hair, o: 0.3 }],
    body: use('face', 'url(#g-skin)') + clip('face',
      // le bas de la joue gauche dans l'ombre, et le menton
      shape(sm('202,238 205,260 215,276 231,289 252,296 274,299 290,297 270,292 247,286 228,274 214,258'), SKIN.shade, 0.55)
      + oval(258, 256, 20, 12.5, 'url(#g-cheek)', 1, 8)
      + oval(389, 247, 10, 8, 'url(#g-cheek)', 0.7, 0)
      + oval(356, 190, 26, 15, 'url(#g-soft)', 0.65)
      + oval(312, 236, 16, 9, 'url(#g-soft)', 0.4)
    )
    // les sourcils : épais, verts, bord plus sombre
    + shape(sm('236,196! 245,184 264,176 286,178 305,186 316,196! 315,203! 304,197 288,190 266,187 250,191 240,199'), LEAF.line)
    + shape(sm('239,194! 248,185 265,179 285,181 303,188 312,196 302,193 287,186 266,184 250,188'), LEAF.mid)
    + shape(sm('256,182 272,179 288,182 272,182'), LEAF.lite, 0.85)
    + shape(sm('343,205! 350,193 366,183 383,180 393,184 395,191! 384,189 370,192 356,200 347,207'), LEAF.line)
    + shape(sm('346,203! 353,193 367,185 382,183 391,187 382,186 369,189 356,196'), LEAF.mid)
    + shape(sm('362,187 374,184 384,184 374,186'), LEAF.lite, 0.85)
    // les yeux fermés de bonheur
    + shape(EYE_L, '#24101a') + shape(LASH_L, '#24101a')
    + shape(EYE_R, '#24101a') + shape(LASH_R, '#24101a')
    // le nez : un petit bouton éclairé
    + shape(sm('322,252 326,243 334,240 342,245 344,253 336,258 328,258'), '#f8c3a1')
    + shape(sm('327,246 333,242 340,245 334,247'), SKIN.hi, 0.95)
    + shape(sm('323,253 330,256 338,256 343,252 337,259 328,259'), '#d98a74', 0.8)
    // la joue gonflée qui souffle, et les lèvres en cul de poule posées sur la flûte
    + line('M276 258 C280 264 280 270 277 276', SKIN.line, 1.5, 0.6)
    + oval(300, 277, 7.4, 6.4, '#e57f72') + oval(300.4, 278.4, 4.2, 3.4, '#5a1a1e') + oval(298, 273.2, 2.5, 1.3, '#ffcfbe', 0.9) },
  { id: 'cap', cls: UP, d: S.cap, shadow: [{ on: ['face', 'earL', 'earR'], dx: -2, dy: 5, color: SH.skin, o: 0.3 }, { on: ['hairB'], dx: -3, dy: 5, color: SH.hair, o: 0.35 }],
    body: use('cap', 'url(#g-hair)') + clip('cap',
      // le côté gauche et la mèche qui couvre l'oreille : dans l'ombre de la tête
      shape(sm('150,130 166,112 186,98 196,130 204,170 212,214 210,250 207,271! 198,250 190,228 176,206 158,198 152,170'), HAIR.mid, 0.6)
      + shape(sm('155,176 160,196 180,204 190,212 196,240 204,262 207,271! 199,252 189,228 175,208 159,200'), HAIR.deep, 0.45)
      // les grandes mèches de la frange : des sillons effilés qui partent du sommet, près de la fleur
      + shape(spindle(352, 98, 268, 168, 7, 10), HAIR.deep, 0.42)
      + shape(spindle(316, 84, 232, 176, 6, 12), HAIR.deep, 0.36)
      + shape(spindle(286, 78, 200, 148, 5, 14), HAIR.deep, 0.3)
      + shape(spindle(214, 150, 212, 246, 5, -4), HAIR.deep, 0.35)
      + shape(spindle(378, 108, 330, 150, 5, 4), HAIR.deep, 0.3)
      // le dessus des mèches éclairé, entre les sillons
      + shape(spindle(334, 104, 262, 160, 6, 9), HAIR.lite, 0.55)
      + shape(spindle(300, 92, 236, 158, 5, 10), HAIR.lite, 0.4)
      // la mèche de droite, en pleine lumière
      + shape(sm('356,118 378,146 394,176 402,208 398,246 406,214 410,182 400,148 378,118'), HAIR.hi, 0.8)
      // le reflet brillant : un croissant sur le haut du dôme, plus vif du côté de la lumière
      + shape(sm('232,86 256,74 284,68 314,68 336,72 312,74 284,76 258,82'), HAIR.hi, 0.9)
      + shape(sm('180,116 192,102 206,92 198,108 190,120'), HAIR.hi, 0.45)
      // le reflet bleuté des ailes sur le bord gauche du dôme
      + shape(sm('186,96 172,110 160,134 154,164 155,190 159,170 164,142 176,116'), '#d4efff', 0.55)
      // la petite mèche pâle qui tombe sur le front
      + shape(sm('316,152 324,168! 328,157 334,154 338,164! 337,150 326,147'), HAIR.lite, 0.95)
    ) },
  { id: 'bud', cls: UP, d: S.bud, body: use('bud', '#fff0a6') + oval(368, 61, 2.6, 1.6, '#ffffff', 0.9) + shape(sm('359,67 363,69.5 369,69.5 366,71 361,70.5'), '#e2c058', 0.6) },
  { id: 'flower', cls: UP, d: S.flower, shadow: [{ on: ['cap', 'bud'], dx: -3, dy: 4, color: SH.hair, o: 0.4 }],
    body: use('flower', 'url(#g-petal)') + clip('flower',
      // les pétales de gauche et du bas dans l'ombre ; les plis entre les pétales
      shape(sm('339,100 348,114 360,123 370,110 356,100'), '#c3cee4', 0.55)
      + shape(sm('340,86 344,96 356,96 350,88'), '#c3cee4', 0.4)
      + PETALS.map(([a], i) => {
        const next = PETALS[(i + 1) % PETALS.length][0];
        const mid = a + (((next - a + 360) % 360) / 2);
        return shape(spindle(...pol(mid, 8), ...pol(mid + 4, 22), 2.2, 0), '#a6b3cc', 0.6);
      }).join('')
      + shape(sm('376,70 384,78 386,90 380,84'), '#ffffff', 0.9)
    )
    // le cœur : une petite coupe jaune, sa graine sombre et son reflet
    + oval(FC.x, FC.y, 10, 9, 'url(#g-heart)', 1, -20) + oval(FC.x - 3, FC.y - 3, 3.2, 2.2, '#fffbe0', 0.95, -20) + dot(FC.x + 2, FC.y + 1.5, 1.8, '#9a5a10', 0.85) },

  // --- la flûte et les mains ---
  { id: 'flute', cls: UP, d: S.flute, shadow: [{ on: ['face', 'armN', 'armF', 'torso'], dx: -3, dy: 6, color: SH.skin, o: 0.38 }],
    body: use('flute', 'url(#g-wood)') + clip('flute',
      // l'écorce près des lèvres : un nœud et quelques taches plus sombres
      `<path d="M${fq(-0.05, -1.3)} L${fq(0.17, -1.3)} L${fq(0.17, 1.3)} L${fq(-0.05, 1.3)} Z" fill="${WOOD.mid}" opacity="0.35"/>`
      + oval(...fp(0.035, 0.25).map(n), 3.8, 2.4, WOOD.shade, 0.75, FA) + oval(...fp(0.11, -0.25).map(n), 2.8, 1.7, WOOD.shade, 0.6, FA)
      + oval(...fp(0.7, 0.4).map(n), 2.3, 1.4, WOOD.shade, 0.45, FA)
      // les trous de la flûte, entre les deux mains
      + oval(...fp(0.52, -0.3).map(n), 2.7, 1.8, WOOD.line, 0.9, FA) + oval(...fp(0.585, -0.3).map(n), 2.7, 1.8, WOOD.line, 0.9, FA)
      // le reflet long sur le dessus, et la bague du bout
      + line(`M${fq(0.2, -0.55)} L${fq(0.91, -0.55)}`, WOOD.hi, 2.2, 0.85)
      + `<path d="M${fq(0.925, -1.4)} L${fq(0.945, -1.4)} L${fq(0.945, 1.4)} L${fq(0.925, 1.4)} Z" fill="${WOOD.line}" opacity="0.5"/>`
      + line(`M${fq(0.955, -0.6)} L${fq(0.995, -0.6)}`, WOOD.hi, 1.8, 0.8)
    ) + FX_MARK },
  { id: 'handF', cls: UP, d: S.handF, shadow: [{ on: ['flute', 'armF'], dx: -3, dy: 5, color: SH.wood, o: 0.35 }],
    body: fistBody('handF', FAR, sm('414,270 421,282 433,289 447,288 458,279 462,268 459,284 445,294 427,295 413,285')) },
  { id: 'handN', cls: UP, d: S.handN, shadow: [{ on: ['flute', 'armN', 'face'], dx: -3, dy: 5, color: SH.skin, o: 0.4 }],
    body: fistBody('handN', NEAR, sm('337,288 345,300 360,306 376,304 387,294 389,284 386,300 371,310 352,310 339,300')) },
];

// ---------- la vie au repos : elle flotte, les ailes battent vite, le haut du corps se balance au rythme de la flûte ----------
// Chaque mouvement part de la pose du dessin (keyframe « from » = pose de repos) : l'attaque s'y termine exactement.
// ---------- l'attaque (0,75 s, classe « atk » sur le <svg>) : elle se penche en arrière, puis souffle une note forte ----------
// élan (0-35 %), coup (35-55 %) : la flûte et la tête partent vers la droite, les ailes battent large, une onde et deux
// notes jaillissent du bout de la flûte ; retour (55-100 %).
const [TX, TY] = TIP.map(n);
const style = `
.a-root{transform-origin:290px 400px;animation:float 2.6s ease-in-out infinite alternate}
.a-up{transform-origin:292px 392px;animation:up 1.8s ease-in-out infinite alternate}
.a-skirt{transform-origin:288px 392px;animation:skirt 2.6s ease-in-out infinite alternate}
.a-legL{transform-origin:238px 452px;animation:legL 2.2s ease-in-out infinite alternate}
.a-legR{transform-origin:300px 452px;animation:legR 2.7s ease-in-out infinite alternate}
.a-wu{transform-origin:228px 316px;animation:wu .32s ease-in-out infinite alternate}
.a-wd{transform-origin:228px 368px;animation:wd .37s ease-in-out infinite alternate}
.a-d1{animation:dust 2.8s ease-out infinite}
.a-d2{animation:dust 3.4s ease-out -1.3s infinite}
.a-d3{animation:dust 3.1s ease-out -2.2s infinite}
.a-d4{animation:dust 3.7s ease-out -0.6s infinite}
.a-ring,.a-nA,.a-nB{opacity:0}
.a-ring{transform-origin:${TX}px ${TY}px}
.a-nA{transform-origin:${NOTE_A.x}px ${NOTE_A.y}px}
.a-nB{transform-origin:${NOTE_B.x}px ${NOTE_B.y}px}
@keyframes float{from{transform:translate(0,0)}to{transform:translate(0,-6px)}}
@keyframes up{from{transform:rotate(0)}to{transform:rotate(2deg)}}
@keyframes skirt{from{transform:rotate(0)}to{transform:rotate(-1.2deg)}}
@keyframes legL{from{transform:rotate(0)}to{transform:rotate(4deg)}}
@keyframes legR{from{transform:rotate(0)}to{transform:rotate(-3.5deg)}}
@keyframes wu{from{transform:rotate(0)}to{transform:rotate(-6deg) scale(.95)}}
@keyframes wd{from{transform:rotate(0)}to{transform:rotate(7deg) scale(.96)}}
@keyframes dust{0%{opacity:0;transform:translate(0,8px) scale(.5)}25%{opacity:1}100%{opacity:0;transform:translate(-8px,-32px) scale(1)}}
.atk .a-root{animation:root-atk .75s ease-in-out}
.atk .a-up{animation:up-atk .75s ease-in-out}
.atk .a-skirt{animation:skirt-atk .75s ease-in-out}
.atk .a-legL{animation:legL-atk .75s ease-in-out}
.atk .a-legR{animation:legR-atk .75s ease-in-out}
.atk .a-wu{animation:wu-atk .75s ease-in-out}
.atk .a-wd{animation:wd-atk .75s ease-in-out}
.atk .a-ring{animation:ring-atk .75s ease-out}
.atk .a-nA{animation:nA-atk .75s ease-out}
.atk .a-nB{animation:nB-atk .75s ease-out}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-8px,3px) rotate(-3deg)}46%{transform:translate(14px,-4px) rotate(1.5deg)}62%{transform:translate(10px,-3px) rotate(1deg)}100%{transform:none}}
@keyframes up-atk{0%{transform:none}30%{transform:translate(-3px,1px) rotate(-4deg)}46%{transform:translate(7px,-2px) rotate(1deg)}62%{transform:translate(5px,-1px) rotate(.5deg)}100%{transform:none}}
@keyframes skirt-atk{0%{transform:none}30%{transform:rotate(-3deg)}50%{transform:rotate(4deg)}70%{transform:rotate(2deg)}100%{transform:none}}
@keyframes legL-atk{0%{transform:none}30%{transform:rotate(-7deg)}50%{transform:rotate(9deg)}72%{transform:rotate(3deg)}100%{transform:none}}
@keyframes legR-atk{0%{transform:none}30%{transform:rotate(-6deg)}52%{transform:rotate(8deg)}74%{transform:rotate(2deg)}100%{transform:none}}
@keyframes wu-atk{0%{transform:none}30%{transform:rotate(-9deg) scale(.93)}46%{transform:rotate(14deg) scale(1.05)}60%{transform:rotate(6deg)}100%{transform:none}}
@keyframes wd-atk{0%{transform:none}30%{transform:rotate(10deg) scale(.93)}46%{transform:rotate(-14deg) scale(1.05)}60%{transform:rotate(-6deg)}100%{transform:none}}
@keyframes ring-atk{0%,40%{opacity:0;transform:scale(.2)}50%{opacity:1;transform:scale(.75)}82%,100%{opacity:0;transform:scale(1.7)}}
@keyframes nA-atk{0%,40%{opacity:0;transform:translate(-8px,16px) scale(.4)}52%{opacity:1;transform:translate(0,0) scale(1)}82%{opacity:1;transform:translate(14px,-12px) rotate(8deg)}100%{opacity:0;transform:translate(18px,-16px) rotate(10deg)}}
@keyframes nB-atk{0%,46%{opacity:0;transform:translate(4px,24px) scale(.4)}58%{opacity:1;transform:translate(0,0) scale(1)}86%{opacity:1;transform:translate(10px,-14px) rotate(-6deg)}100%{opacity:0;transform:translate(13px,-18px) rotate(-8deg)}}
`.replace(/\n/g, '');

/** L'image : le rendu commun, puis deux retouches propres à la fée (ailes translucides, groupe d'ensemble qui flotte). */
function svg(anime = true) {
  let s = figure({ w: W, h: H, pad: PAD, defs, style, parts: anime ? parts : parts.filter((p) => !p.fx), anime });
  const fx = `<g class="a-ring">${dot(...TIP.map(n), 30, 'url(#g-ring)')}${dot(...TIP.map(n), 12, 'url(#g-glow)')}</g>` + noteFx(NOTE_B, 'a-nB') + noteFx(NOTE_A, 'a-nA');
  s = s.replace(FX_MARK, anime ? fx : '');
  // les ailes : un trait fin violet à la place de l'aplat sombre du contour, pour qu'on voie à travers la membrane
  const i0 = s.indexOf('<g fill="#2a1430"');
  const i1 = s.indexOf('<g stroke-linecap="round" stroke-linejoin="round">', i0);
  let ol = s.slice(i0, i1);
  for (const w of ['wingU', 'wingD']) ol = ol.replace(`<use href="#s-${w}"/>`, `<use href="#s-${w}" fill="none" stroke="#3b2a62" stroke-width="6"/>`);
  s = s.slice(0, i0) + (anime ? '<g class="a-root">' : '') + ol + s.slice(i1);
  if (anime) s = s.replace(/<\/svg>$/, '</g></svg>');
  return s;
}

module.exports = { id: 'assassins-12', w: W, h: H, pad: PAD, foot: [252, 540], svg };
