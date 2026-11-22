// L'esprit-flamme cyan du Bayou (bayou-4) : redessiné par le code d'après le dessin d'origine, dans le même cadre
// (375 × 376, mêmes proportions, même pose) : un corps rond fait de flamme, cyan au cœur clair, une couronne de cinq
// langues de feu, un visage méchant (yeux en biais, gueule dentelée), un bras de flamme de chaque côté qui se termine en
// crochets, une queue en S en bas ; il flotte.
// La lumière vient d'en haut à droite (reflet sur le haut du corps, ombres portées en bas à gauche) ; le cœur luit.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 375, H = 376;

/** Courbe lisse qui passe par des points ([x, y] ; [x, y, 1] = coin net). */
function sm(pts, closed = true, k = 1) {
  const N = pts.length;
  const get = (i) => (closed ? pts[(i + N) % N] : pts[Math.max(0, Math.min(N - 1, i))]);
  const tan = (i) => {
    const p = get(i);
    if (p[2] || (!closed && (i === 0 || i === N - 1))) return [0, 0];
    const a = get(i - 1), b = get(i + 1);
    return [((b[0] - a[0]) / 6) * k, ((b[1] - a[1]) / 6) * k];
  };
  let d = `M${n(pts[0][0])} ${n(pts[0][1])}`;
  for (let i = 0; i < (closed ? N : N - 1); i++) {
    const p0 = get(i), p1 = get(i + 1), t0 = tan(i), t1 = tan(i + 1);
    d += `C${n(p0[0] + t0[0])} ${n(p0[1] + t0[1])} ${n(p1[0] - t1[0])} ${n(p1[1] - t1[1])} ${n(p1[0])} ${n(p1[1])}`;
  }
  return d + (closed ? 'Z' : '');
}

/** Une forme effilée (reflet, pli de flamme) : une lentille de (x0, y0) à (x1, y1), bombée vers (cx, cy), large de `w`. */
function taper(x0, y0, cx, cy, x1, y1, w) {
  const dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy) || 1;
  const nx = (-dy / L) * w, ny = (dx / L) * w;
  return `M${n(x0)} ${n(y0)}Q${n(cx + nx)} ${n(cy + ny)} ${n(x1)} ${n(y1)}Q${n(cx - nx)} ${n(cy - ny)} ${n(x0)} ${n(y0)}Z`;
}

// ---------- couleurs ----------
const T = { white: '#eafffd', hi: '#bdfcf6', lite: '#80f8ea', base: '#3fe0d0', mid: '#2cc9bc', shade: '#1aa3a8', deep: '#137a85', line: '#0b4b57' };
// le cœur de la flamme : un cyan très pâle, et un blanc à peine jaune au plus chaud
const CORE = { pale: '#b4fbf1', warm: '#effff1' };
const INK = '#0c3542';
const SH = '#0a3d4c';

// ---------- dégradés ----------
const defs = [
  // les langues de feu : claires au bout, plus soutenues vers le corps
  // tout le feu partage le même dégradé en rond, centré sur le cœur : là où un morceau en recouvre un autre, les couleurs
  // se rejoignent et le raccord ne se voit pas (sauf là où on veut une ombre)
  rad('g-fire', 240, 205, 200, [[0, '#d6fefb'], [0.18, '#aefbf3'], [0.34, '#80f6e9'], [0.48, '#50e6d8'], [0.62, '#36d5c8'], [0.8, '#2bc6bd'], [1, '#22b4b0']]),
  lin('g-tongueL', 60, 0, 200, 0, [[0, '#2aa8b2'], [1, '#4fd6d0']]),
  // le corps : cœur clair (le visage), bord plus soutenu, lumière en haut à droite
  rad('g-glow', 0.5, 0.5, 0.5, [[0, '#f2fffd', 0.85], [0.6, '#d9fffa', 0.35], [1, '#d9fffa', 0]], false),
  lin('g-arm', 0, 0, 1, 0, [[0, '#33d0c4'], [0.6, '#3fdccd'], [1, '#2cc4bd']], false),
  lin('g-armR', 300, 0, 372, 0, [[0, '#28c0bc'], [0.5, '#3fdcce'], [1, '#62f0e0']]),
  lin('g-tail', 0, 280, 0, 372, [[0, '#27bdb8'], [0.6, '#3ad6c8'], [1, '#5eeedf']]),
  rad('g-eye', 0.5, 0.35, 0.75, [[0, '#1f6a7a'], [0.6, '#103f4d'], [1, '#0a2c38']], false),
  lin('g-mouth', 0, 0, 0, 1, [[0, '#082a35'], [0.7, '#0f4552'], [1, '#17606d']], false),
  rad('g-soft', 0.5, 0.5, 0.5, [[0, '#ffffff', 0.9], [1, '#ffffff', 0]], false),
].join('');

// ---------- silhouettes ----------
const S = {
  // la couronne : cinq langues de feu, du fond vers le devant ; chacune s'enfonce loin dans le corps
  tFL: sm([[86, 114, 1], [84, 127], [89, 141], [99, 151], [113, 156], [128, 158], [152, 176], [154, 214], [116, 220], [99, 216], [94, 203], [95, 187], [83, 170], [77, 150], [77, 133], [81, 121]]),
  tFR: sm([[303, 72, 1], [300, 86], [304, 98], [318, 112], [326, 130], [322, 150], [312, 166], [309, 179, 1], [315, 182], [321, 174], [325, 168, 1], [327, 181], [327, 196], [318, 210], [300, 224], [262, 206], [262, 150], [278, 134], [291, 126], [297, 114], [290, 99], [291, 84]]),
  tL: sm([[142, 65, 1], [136, 79], [137, 94], [146, 106], [162, 113], [184, 140], [172, 180], [140, 180], [126, 160], [130, 146], [128, 134], [120, 120], [116, 106], [117, 92], [123, 80], [132, 70]]),
  tR: sm([[250, 41, 1], [246, 55], [249, 69], [261, 81], [276, 95], [283, 111], [284, 126], [280, 140], [262, 172], [226, 170], [228, 128], [233, 102], [233, 82], [232, 66], [236, 54], [242, 46]]),
  tC: sm([[185, 3, 1], [201, 11], [213, 21], [219, 35], [215, 50], [216, 64], [224, 77], [238, 92], [244, 130], [230, 168], [190, 172], [160, 150], [154, 124], [152, 98], [155, 78], [166, 61], [184, 46], [192, 33], [192, 21]]),
  // les bras de flamme : ils partent de sous le corps et finissent en crochets
  // le bras gauche : la base (elle finit sur une pointe dressée), puis trois griffes qui partent de dessous elle : le grand
  // crochet du haut, le crochet du bas, la pointe d'en bas. Leurs racines restent loin sous la base.
  armL: sm([[160, 218], [136, 214], [116, 218], [99, 219], [86, 221], [78, 216], [70, 208], [64, 203], [58, 198], [54, 192], [50, 184], [46, 178], [40, 175, 1], [44, 182], [46, 190], [45, 197], [42, 203, 1], [44, 214], [49, 226], [55, 238], [63, 249], [73, 258], [84, 266, 1], [86, 273, 1], [95, 268], [104, 270], [122, 259], [134, 257], [150, 268], [172, 266]]),
  clL1: sm([[33, 168, 1], [25, 170], [15, 176], [8, 186], [5, 198], [5, 210], [8, 222], [14, 230], [22, 236], [30, 239], [38, 242, 1], [56, 246], [78, 246], [100, 238], [98, 228], [80, 224], [60, 216], [46, 210], [40, 205], [32, 203], [25, 198], [21, 190], [23, 180], [28, 172]]),
  clL2: sm([[11, 240, 1], [13, 248], [18, 255], [25, 260], [35, 264], [45, 266], [54, 268, 1], [72, 268], [94, 264], [104, 254], [92, 246], [70, 246], [52, 246], [40, 245], [30, 246], [20, 243]]),
  clL3: sm([[40, 279, 1], [46, 284], [53, 285], [61, 283], [69, 278], [76, 272], [84, 266], [98, 264], [104, 256], [90, 254], [72, 258], [60, 264], [53, 269], [46, 274]]),
  // le bras droit : une petite base sous le corps, le grand crochet qui remonte, la langue du bas
  armR: sm([[298, 222], [309, 226], [311, 236], [308, 243, 1], [314, 240, 1], [316, 249], [322, 258], [324, 270], [318, 283], [306, 292], [293, 297], [286, 297, 1], [288, 303, 1], [279, 300], [273, 292], [268, 270], [282, 240]]),
  clR1: sm([[347, 197, 1], [347, 206], [360, 217], [368, 230], [371, 246], [368, 261], [360, 270], [349, 274], [346, 279, 1], [334, 284], [318, 286], [304, 280], [300, 266], [306, 256], [316, 249], [324, 249], [332, 239], [340, 228], [341, 216], [337, 207], [341, 199]]),
  clR2: sm([[372, 283, 1], [362, 292], [352, 299], [345, 302], [337, 310], [322, 315], [310, 313], [300, 306], [293, 297], [290, 286], [298, 276], [316, 272], [334, 276], [346, 279, 1], [356, 283], [366, 279]]),
  tail: sm([[150, 270], [134, 280], [124, 284], [119, 297], [121, 313], [130, 326], [144, 335], [158, 340], [169, 348], [175, 358], [176, 370, 1], [186, 368], [195, 358], [201, 344], [198, 328], [186, 316], [179, 306], [180, 296], [192, 290], [200, 276]]),
  // le corps : une boule de flamme, au bord haut ondulé (le pied des langues)
  body: sm([[146, 228], [148, 196], [156, 170], [162, 150], [174, 140], [190, 128], [206, 134], [222, 120], [240, 130], [256, 122], [270, 138], [286, 146], [298, 166], [306, 192], [308, 222], [302, 252], [288, 274], [266, 289], [240, 296], [212, 297], [188, 292], [168, 280], [154, 262]]),
};

// ---------- le visage ----------
// les yeux : une amande sombre coupée en biais par le haut (regard méchant), une pupille blanche
const EYE_L = sm([[189, 176, 1], [214, 186], [237, 203, 1], [232, 214], [220, 223], [205, 222], [194, 212], [188, 195]]);
const EYE_R = sm([[284, 182, 1], [270, 191], [255, 204, 1], [258, 216], [266, 225], [276, 224], [283, 212], [285, 196]]);
// la gueule : un trou sombre aux bords dentelés (deux crocs en haut, deux petites dents en bas)
const MOUTH = 'M205 251 L216 235 L228 248 L236 243 L252 250 L266 239 L263 256 L258 268 L250 272 L246 265 L240 271 L230 270 L226 264 L218 270 L207 270 C204 263 204 257 205 251 Z';
const face = () =>
  // la pupille est un rond blanc ; une petite ride au coin intérieur de l'œil gauche, comme sur l'original
  `<g class="a-eyes">`
  + `<path d="${EYE_L}" fill="url(#g-eye)"/>` + `<path d="${EYE_R}" fill="url(#g-eye)"/>`
  + line('M189 176 C204 182 222 192 237 203', '#05222c', 2.6) + line('M284 182 C274 188 264 196 255 204', '#05222c', 2.6)
  + oval(216, 206, 6.4, 6.6, '#fff') + oval(265, 208, 4.8, 6.2, '#fff')
  + `<g class="a-blink" opacity="0"><path d="${EYE_L}" fill="#8cece3"/><path d="${EYE_R}" fill="#8cece3"/>`
  + line('M190 206 C204 214 222 216 236 206', INK, 3) + line('M256 208 C264 216 276 218 284 206', INK, 3) + `</g>`
  + `</g>`
  + line('M235 196 L238 201', '#16596a', 2, 0.8)
  // la gueule, découpée dans le corps : pas de trait qui la referme, l'intérieur s'assombrit vers le fond
  + `<g class="a-mouth"><path d="${MOUTH}" fill="url(#g-mouth)"/>`
  + `<path d="M210 262 C222 258 246 258 258 262 L256 268 L250 272 L246 265 L240 271 L230 270 L226 264 L218 270 L208 270 Z" fill="#1d6a78" opacity="0.55"/></g>`;

// ---------- les morceaux, du fond vers le devant ----------
/** Une langue de feu : son dégradé, une nappe claire au milieu, l'ombre de son flanc gauche. */
const tongue = (id, lite, dark, extra = '') => use(id, 'url(#g-fire)') + clip(id,
  shape(dark, T.deep, 0.32) + shape(lite, T.hi, 0.75) + extra + band(id));
/** Une bande plus sombre le long du bord, à l'intérieur : elle sépare les langues qui se recouvrent. */
const band = (id, w = 7, o = 0.45) => `<use href="#s-${id}" fill="none" stroke="${T.deep}" stroke-width="${w}" opacity="${o}"/>`;
const parts = [
  { id: 'tFL', cls: 'a-tFL', d: S.tFL,
    body: tongue('tFL', taper(86, 120, 92, 140, 112, 152, 3), 'M86 114 C80 128 78 146 84 166 C90 182 96 196 99 214 L90 214 C86 196 74 176 74 150 C74 134 78 122 86 114 Z',
      shape(taper(100, 170, 116, 186, 140, 196, 5), T.lite, 0.6) + shape(taper(84, 138, 92, 158, 108, 170, 2.5), T.lite, 0.8)) },
  { id: 'tFR', cls: 'a-tFR', d: S.tFR, shadow: [{ on: ['tFL'], dx: -3, dy: 3, color: SH, o: 0.3 }],
    body: tongue('tFR', taper(302, 80, 306, 104, 320, 126, 3.5), 'M291 84 C290 99 297 114 291 126 C284 138 272 150 268 172 L262 172 L262 150 C272 134 288 120 290 100 Z',
      shape(taper(314, 176, 320, 182, 324, 172, 2), T.hi, 0.8) + shape(taper(300, 146, 312, 170, 306, 200, 4), T.lite, 0.5)
      + shape(taper(298, 104, 308, 124, 306, 146, 2.5), T.lite, 0.8)) },
  { id: 'tL', cls: 'a-tL', d: S.tL, shadow: [{ on: ['tFL'], dx: -3, dy: 3, color: SH, o: 0.3 }],
    body: tongue('tL', taper(140, 72, 138, 92, 150, 108, 3.5), 'M132 70 C122 80 116 94 117 108 C119 122 128 134 130 148 L124 150 C118 132 110 118 112 100 C114 88 122 76 132 70 Z',
      shape(taper(126, 96, 124, 116, 136, 134, 2.5), T.lite, 0.8)) },
  { id: 'tR', cls: 'a-tR', d: S.tR, shadow: [{ on: ['tFR'], dx: -3, dy: 3, color: SH, o: 0.3 }],
    body: tongue('tR', taper(248, 50, 256, 78, 276, 104, 4), 'M242 46 C234 56 232 70 233 84 C234 100 230 118 228 136 L222 136 C224 116 226 98 226 82 C226 66 232 54 242 46 Z',
      shape(taper(240, 72, 242, 96, 252, 118, 2.5), T.lite, 0.8)) },
  { id: 'tC', cls: 'a-tC', d: S.tC, shadow: [{ on: ['tL', 'tR'], dx: -4, dy: 3, color: SH, o: 0.32 }],
    rim: { on: ['tL', 'tR'], color: T.deep, w: 1.1, o: 0.6 },
    body: tongue('tC', taper(188, 10, 206, 26, 206, 52, 4) + taper(196, 60, 200, 92, 214, 120, 6), 'M192 21 C194 33 186 44 172 54 C160 64 152 80 152 98 C152 116 156 134 164 150 L156 150 C146 132 144 112 146 94 C148 74 160 58 176 46 C186 38 190 30 192 21 Z',
      shape(taper(168, 88, 176, 112, 188, 134, 3), T.lite, 0.7) + shape(taper(176, 58, 170, 82, 176, 106, 3), T.lite, 0.8)
      + shape(taper(204, 40, 212, 60, 222, 82, 2.5), T.hi, 0.7)) },
  // le bras gauche : il passe sous le corps
  { id: 'armL', cls: 'a-armL', d: S.armL, shadow: [{ on: ['tFL'], dx: -3, dy: 4, color: SH, o: 0.32 }],
    body: use('armL', 'url(#g-fire)') + clip('armL', band('armL') +
      // le dessous du bras, plus sombre ; la grande nappe claire du dessus
      shape('M12 246 C26 262 48 270 74 268 C100 266 124 258 150 262 L160 290 L0 290 Z', T.deep, 0.4)
      + shape('M60 230 C84 240 112 244 140 236 C116 250 88 254 62 246 Z', T.deep, 0.35)
      + shape(taper(56, 204, 90, 226, 144, 226, 6), T.hi, 0.7)
      + shape(taper(20, 204, 30, 222, 60, 232, 4), T.lite, 0.8)
      // les crochets : une nappe claire le long de chaque courbe
      + shape(taper(30, 172, 14, 190, 18, 222, 3), T.lite, 0.9)
      + shape(taper(40, 180, 42, 192, 34, 202, 2), T.hi, 0.7)
      + shape(taper(16, 244, 26, 252, 46, 256, 2.4), T.hi, 0.7)
      + shape(taper(66, 252, 98, 258, 132, 250, 3), T.lite, 0.7)) },
  // le bras droit
  { id: 'armR', cls: 'a-armR', d: S.armR, shadow: [{ on: ['tFR'], dx: -3, dy: 4, color: SH, o: 0.32 }],
    body: use('armR', 'url(#g-fire)') + clip('armR', band('armR') +
      shape('M286 290 C304 300 326 306 346 296 C356 290 364 286 372 283 L372 320 L280 320 Z', T.deep, 0.45)
      + shape(taper(320, 252, 338, 226, 346, 200, 3.5), T.hi, 0.8)
      + shape(taper(304, 270, 336, 262, 362, 236, 5), T.lite, 0.7)
      + shape(taper(296, 292, 330, 296, 366, 282, 3), T.lite, 0.6)
      + shape(taper(312, 238, 332, 228, 340, 210, 2), T.hi, 0.8)) },
  // la queue en S
  { id: 'tail', cls: 'a-tail', d: S.tail,
    body: use('tail', 'url(#g-fire)') + clip('tail', band('tail') +
      shape('M124 284 C118 300 122 318 136 330 C152 340 168 346 174 360 L176 372 L110 372 L110 284 Z', T.deep, 0.42)
      + shape(taper(156, 300, 176, 326, 188, 360, 5), T.hi, 0.75)
      + shape(taper(134, 300, 140, 318, 158, 330, 3), T.lite, 0.6)) },

  // le corps et son visage
  { id: 'body', cls: 'a-body', d: S.body,
    shadow: [{ on: ['armL', 'armR', 'tail'], dx: -3, dy: 6, color: SH, o: 0.38 }],
    rim: { on: ['armL', 'armR', 'tail'], color: T.deep, w: 1, o: 0.55 },
    body: use('body', 'url(#g-fire)') + clip('body',
      // le cœur qui luit
      `<ellipse class="a-core" cx="236" cy="212" rx="58" ry="52" fill="url(#g-glow)"/>`
      // les flammes qui montent dans le corps : de grandes langues claires effilées
      + shape(taper(176, 150, 178, 182, 166, 214, 5), T.lite, 0.55)
      + shape(taper(206, 136, 212, 160, 210, 180, 4), T.hi, 0.6)
      + shape(taper(256, 130, 262, 152, 258, 176, 4), T.hi, 0.6)
      + shape(taper(284, 150, 296, 176, 298, 204, 4), T.lite, 0.6)
      // le flanc gauche, plus soutenu
      + shape('M146 228 C148 200 156 176 170 160 C164 186 164 214 172 240 C176 256 186 272 200 284 C176 278 156 258 146 228 Z', T.mid, 0.35)
      // le bas du corps dans l'ombre, puis un liseré clair (le reflet du sol)
      + shape('M146 232 C150 262 170 286 204 294 C238 300 276 290 300 262 L310 320 L140 320 Z', T.shade, 0.45)
      + shape('M184 290 C210 297 246 296 272 286 C252 292 214 296 186 293 Z', T.white, 0.85)
      // le reflet du haut, à droite
      + shape(taper(262, 140, 288, 156, 300, 184, 4), T.white, 0.75)
      + face()) },
];

// ---------- la vie ----------
// Au repos (propriétés `translate`, `rotate`, `scale`) : l'esprit flotte, chaque langue lèche vers le haut à son rythme,
// les bras ondulent, la queue fouette doucement, le cœur luit, les yeux clignent.
// L'attaque (classe `atk` sur le <svg>, 0,75 s) passe par `transform`, qui s'ajoute au repos : il se ramasse (élan), bondit
// vers la droite en s'étirant, les flammes s'embrasent et traînent derrière, la gueule s'ouvre en grand ; puis il revient.
const CENTER = [228, 215];
const PIV = { tC: [198, 140], tL: [152, 150], tR: [250, 150], tFL: [130, 190], tFR: [290, 180], armL: [160, 245], armR: [290, 260], tail: [170, 280], body: CENTER };
const AT = [0, 30, 45, 58, 100];
const MOVE = [[0, 0], [-16, 10], [52, -8], [46, -6], [0, 0]];
const SQUASH = [[1, 1], [0.9, 0.8], [1.14, 1.02], [1.08, 1.02], [1, 1]];
const FLARE = [[1, 1], [0.92, 0.82], [1.1, 1.22], [1.06, 1.14], [1, 1]];
/** Le mouvement d'ensemble de l'attaque, vu depuis le pivot `o` du morceau, avec en plus son propre étirement et sa rotation. */
function lunge(o, i, f = [1, 1], turn = 0) {
  const [sx, sy] = SQUASH[i], [tx, ty] = MOVE[i];
  const vx = (1 - sx) * (CENTER[0] - o[0]) + tx, vy = (1 - sy) * (CENTER[1] - o[1]) + ty;
  return `translate(${n(vx)}px,${n(vy)}px) scale(${n(sx * f[0])},${n(sy * f[1])}) rotate(${turn}deg)`;
}
const kf = (name, f) => `@keyframes ${name}{${AT.map((p, i) => `${p}%{transform:${f(i)}}`).join('')}}`;
const TURN = { tongue: [0, 4, -10, -7, 0], armL: [0, 10, -12, -8, 0], armR: [0, 12, -18, -12, 0], tail: [0, -10, 16, 10, 0] };
const FLOAT = 'float 2.4s ease-in-out infinite alternate';
const LICK = { tC: '1.1s', tL: '.9s -.4s', tR: '1s -.7s', tFL: '1.3s -.2s', tFR: '1.2s -.9s' };
const IDLE = {
  ...Object.fromEntries(Object.entries(LICK).map(([k, v]) => [k, `${FLOAT},lick ${v.split(' ')[0]} ease-in-out ${v.split(' ')[1] || '0s'} infinite alternate`])),
  armL: `${FLOAT},waveL 1.7s ease-in-out infinite alternate`,
  armR: `${FLOAT},waveR 2s ease-in-out -.6s infinite alternate`,
  tail: `${FLOAT},swish 1.5s ease-in-out infinite alternate`,
  body: `${FLOAT},puff 2.4s ease-in-out infinite alternate`,
};
const style = [
  ...Object.entries(PIV).map(([k, [x, y]]) => `.a-${k}{transform-origin:${x}px ${y}px;animation:${IDLE[k]}}`),
  '.a-core{transform-origin:236px 212px;animation:core 1.2s ease-in-out infinite alternate}',
  '.a-blink{animation:blink 5.2s linear infinite}',
  '.a-mouth{transform-origin:236px 254px}',
  '.a-eyes{transform-origin:236px 204px}',
  '@keyframes float{from{translate:0 2px}to{translate:0 -6px}}',
  '@keyframes lick{from{rotate:-3deg;scale:1 1}to{rotate:2.5deg;scale:.95 1.08}}',
  '@keyframes waveL{from{rotate:-4deg}to{rotate:5deg}}',
  '@keyframes waveR{from{rotate:5deg}to{rotate:-4deg}}',
  '@keyframes swish{from{rotate:-6deg}to{rotate:7deg}}',
  '@keyframes puff{from{scale:1 1}to{scale:1.015 .985}}',
  '@keyframes core{from{transform:scale(.9);opacity:.7}to{transform:scale(1.08);opacity:1}}',
  '@keyframes blink{0%,94%{opacity:0}95.5%,97.5%{opacity:1}99%,100%{opacity:0}}',
  // --- l'attaque ---
  ...Object.keys(PIV).map((k) => `.atk .a-${k}{animation:${IDLE[k]},atk-${k} .75s ease-in-out}`),
  '.atk .a-mouth{animation:roar .75s ease-in-out}',
  '.atk .a-eyes{animation:glare .75s ease-in-out}',
  ...['tC', 'tL', 'tR', 'tFL', 'tFR'].map((k) => kf(`atk-${k}`, (i) => lunge(PIV[k], i, FLARE[i], TURN.tongue[i]))),
  kf('atk-armL', (i) => lunge(PIV.armL, i, [1, 1], TURN.armL[i])),
  kf('atk-armR', (i) => lunge(PIV.armR, i, [1, 1], TURN.armR[i])),
  kf('atk-tail', (i) => lunge(PIV.tail, i, [1, 1], TURN.tail[i])),
  kf('atk-body', (i) => lunge(PIV.body, i)),
  kf('roar', (i) => `scale(${[1, 0.9, 1.15, 1.1, 1][i]},${[1, 0.8, 1.5, 1.35, 1][i]})`),
  kf('glare', (i) => `scale(1,${[1, 0.78, 1.08, 1.04, 1][i]})`),
].join('');

module.exports = { id: 'bayou-4', w: W, h: H, pad: 90, foot: [190, 362],
  svg: (anime = true) => figure({ w: W, h: H, pad: 90, outline: INK, defs, style, parts, anime }) };
