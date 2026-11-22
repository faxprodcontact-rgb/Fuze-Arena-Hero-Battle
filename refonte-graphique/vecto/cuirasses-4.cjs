// Le colimaçon de cristal (cuirasses-4) : redessiné par le code d'après le dessin d'origine, dans le même cadre
// (401 × 386, mêmes proportions, même pose) : grosse coquille de pierre grise en spirale, taches de mousse, bouquet
// de cristaux verts sur le dessus, corps de limace beige qui rampe vers la droite, deux tiges d'yeux en colère,
// bouche boudeuse qui montre une dent.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 401, H = 386;

// ---------- petits outils ----------
/**
 * Courbe lisse qui passe par des points (Catmull-Rom → Bézier). Un point [x, y, 1] est un angle vif.
 * `closed` = forme fermée (sinon un simple trait).
 */
function P(pts, closed = true) {
  const N = pts.length;
  const at = (i) => (closed ? pts[(i + N) % N] : pts[Math.max(0, Math.min(N - 1, i))]);
  const sharp = (i) => !!at(i)[2] || (!closed && (i <= 0 || i >= N - 1));
  // tangente au point i (dir = +1 en partant, -1 en arrivant)
  const tan = (i, dir) => {
    const p = at(i);
    if (sharp(i)) { const q = at(i + dir); return [(q[0] - p[0]) * dir / 3, (q[1] - p[1]) * dir / 3]; }
    const a = at(i - 1), b = at(i + 1);
    return [(b[0] - a[0]) / 6, (b[1] - a[1]) / 6];
  };
  let d = `M${n(pts[0][0])} ${n(pts[0][1])}`;
  const last = closed ? N : N - 1;
  for (let i = 0; i < last; i++) {
    const p = at(i), q = at(i + 1), t1 = tan(i, 1), t2 = tan(i + 1, -1);
    d += `C${n(p[0] + t1[0])} ${n(p[1] + t1[1])} ${n(q[0] - t2[0])} ${n(q[1] - t2[1])} ${n(q[0])} ${n(q[1])}`;
  }
  return closed ? d + 'Z' : d;
}

// ---------- couleurs ----------
const BODY = { hi: '#fbf0c8', lite: '#f3dfa4', base: '#e8cd8c', mid: '#d8b46a', shade: '#b8904e', line: '#8c6634' };
const STONE = { hi: '#ece6da', lite: '#bdb3aa', base: '#958b86', mid: '#7c7279', shade: '#5c5361', deep: '#463e4c', line: '#3a3240' };
const MOSS = { hi: '#a6e46c', base: '#5fb543', mid: '#46993a', deep: '#2f7530' };
const CRY = { hi: '#e6ffd8', lite: '#a2f08a', base: '#5fd254', mid: '#43b446', shade: '#2c8c3a', deep: '#1e6a30' };
// les ombres portées : une teinte par matière qui la reçoit
const SH = { body: '#7d5524', stone: '#2c2434', cry: '#14522a' };

// ---------- la coquille ----------
// la spirale (la ligne de suture entre deux tours) : rayon relevé tous les 15° autour de (172, 257), en partant
// du crochet du centre et en tournant dans le sens inverse des aiguilles d'une montre (vers l'extérieur)
const SC = [172, 257];
const SPI = [
  [-80, 4.5], [-50, 4.8], [-25, 5.6], [0, 6.8], [15, 8.2], [30, 10.6], [45, 14.2], [60, 18.1], [75, 22.6], [90, 25.6],
  [105, 28.5], [120, 31.1], [135, 32.6], [150, 34.1], [165, 35.2], [180, 36.5], [195, 37.6], [210, 38.4], [225, 39.4],
  [240, 40.1], [255, 40.8], [270, 41.2], [285, 41.8], [300, 43], [315, 44.4], [330, 45.9], [345, 48.1], [360, 50.5],
  [375, 53.8], [390, 59], [405, 64.4], [420, 70], [435, 75.6], [450, 79.4], [465, 83.2], [480, 86.4], [495, 88.1],
  [510, 88.5], [525, 88.6], [540, 88.6], [555, 88.5], [570, 88.6], [585, 89.4], [600, 91.6], [612, 94.6],
];
const spiralPts = (from = -999, to = 999, dr = 0) => SPI.filter(([a]) => a >= from && a <= to).map(([a, r]) => {
  const t = (a * Math.PI) / 180;
  return [SC[0] + (r + dr) * Math.cos(t), SC[1] - (r + dr) * Math.sin(t)];
});
const SPIRAL = P(spiralPts(), false);

const S = {
  // la coquille : tour extérieur (bord du haut, de gauche et lèvre de droite), le bas suit la spirale
  shell: P([[277, 268], [284, 240], [286, 212], [283, 190], [270, 163], [252, 146], [228, 132], [200, 124], [167, 122],
    [133, 127], [108, 135], [88, 146], [72, 160], [56, 183], [45, 212], [39, 245], [39, 272], [43, 295], [52, 314],
    [66, 328], [90, 337], [121, 344], [147, 348], [172, 350], [197, 348], [221, 341], [243, 328], [261, 308], [273, 286]]),
  // le pied, de la pointe de la queue jusque sous le cou
  foot: P([[5, 369, 1], [11, 358], [24, 348], [43, 340], [64, 334], [100, 328], [160, 326], [220, 318], [255, 300],
    [285, 290], [305, 300], [318, 322], [323, 350], [322, 370], [300, 376], [260, 374], [210, 377], [160, 376], [110, 373],
    [60, 374], [24, 373]]),
  // le cou et la tête : la bouche est une vraie encoche entre le bec et la lèvre du bas
  head: P([[338, 213], [347, 221], [354, 233], [357, 245], [359, 253], [366, 258], [371, 264], [374, 271], [372, 278],
    [367, 278], [361, 272], [354, 268], [349, 269, 1], [347, 275, 1], [352, 281], [357, 286], [358, 294], [356, 300],
    [351, 300], [345, 296], [337, 304], [330, 315], [325, 330], [325, 344], [331, 357], [334, 366], [330, 372],
    [312, 375], [296, 374], [294, 344], [287, 314], [274, 290], [252, 266], [244, 234], [254, 209], [276, 200], [292, 204], [306, 201],
    [321, 203], [332, 207]]),
  // les tiges des yeux : elles partent de sous la tête
  stalkB: P([[290, 226], [290.5, 190], [291.5, 160], [293, 136], [305, 136], [304, 160], [303.5, 190], [305, 226]]),
  eyeB: P([[302, 103], [316, 108], [321, 122], [316, 136], [302, 141], [288, 136], [283, 122], [288, 108]]),
  stalkF: P([[318, 226], [324, 206], [338, 177], [356, 150], [368, 157], [350, 184], [340, 209], [337, 230]]),
  eyeF: P([[375.5, 121], [388, 126], [393.5, 139.5], [388, 153], [375.5, 158], [363, 153], [357.5, 139.5], [363, 126]]),
  // les cristaux : le grand du milieu passe devant les deux autres ; leur pied est caché par la coquille
  cryL: P([[82, 69, 1], [118, 92, 1], [132, 150, 1], [104, 178, 1], [76, 176, 1], [61, 117, 1]]),
  cryR: P([[218, 68, 1], [231, 101, 1], [227, 140, 1], [188, 140, 1], [189, 86, 1]]),
  cryC: P([[162, 9, 1], [188, 47, 1], [188, 138, 1], [124, 138, 1], [125, 48, 1]]),
};

// ---------- dégradés ----------
const defs = [
  rad('g-shell', 226, 166, 215, [[0, '#b7ada3'], [0.3, '#91877f'], [0.6, '#796f6d'], [0.86, '#5d5359'], [1, '#463d47']]),
  lin('g-body', 0, 200, 0, 376, [[0, '#f1dca0'], [0.45, BODY.base], [1, '#d9b875']]),
  lin('g-neck', 262, 0, 372, 0, [[0, '#bf914c'], [0.25, '#d6b062'], [0.6, BODY.base], [1, '#f2dca0']]),
  lin('g-headTone', 0, 196, 0, 300, [[0, '#f3e6bf', 0.6], [1, '#f3e6bf', 0]]),
  lin('g-foot', 0, 330, 0, 377, [[0, '#e4cf9c'], [0.5, '#d2b986'], [1, '#b49866']]),
  lin('g-stalk', 0, 0, 1, 0, [[0, '#c8aa6c'], [0.45, '#e6cf96'], [1, '#f6e8c0']], false),
  rad('g-ball', 0.62, 0.35, 0.75, [[0, '#ded8d4'], [0.55, '#a69e9c'], [1, '#6e6670']], false),
  rad('g-sclera', 0.6, 0.62, 0.7, [[0, '#ffffff'], [0.7, '#f1f5e6'], [1, '#cfd9c0']], false),
  rad('g-iris', 0.36, 0.78, 0.8, [[0, '#86e0a8'], [0.4, '#2f8a5c'], [0.8, '#123d2a'], [1, '#0b2219']], false),
  rad('g-moss', 0.62, 0.3, 0.75, [[0, '#8cd05a'], [0.55, '#56a83e'], [1, '#3e8434']], false),
  lin('g-cryBase', 0, 92, 0, 150, [[0, '#0f4a24', 0], [1, '#0f4a24', 0.55]]),
  lin('g-cryL', 0, 0, 1, 0, [[0, '#2f9e40'], [1, '#56cc52']], false),
  lin('g-cryR', 0, 0, 1, 0, [[0, '#6adc5c'], [1, '#9cee86']], false),
  lin('g-cryTip', 0, 0, 0, 1, [[0, '#d2ffc0'], [1, '#78e068']], false),
  rad('g-flash', 156, 86, 120, [[0, '#f4ffe8', 0.95], [0.35, '#9cff8a', 0.6], [1, '#5cff70', 0]]),
  rad('g-glow', 0.5, 0.5, 0.5, [[0, '#ffffff', 0.9], [1, '#ffffff', 0]], false),
  lin('g-mouth', 0, 0, 1, 0, [[0, '#2a1410'], [1, '#5a2a1c']], false),
].join('');

// ---------- la spirale : une seule bande, ombrée du côté de la lumière, éclairée de l'autre ----------
function spiral() {
  const sp = (tx, ty, color, w, o) => `<path d="${SPIRAL}" transform="translate(${tx} ${ty})" fill="none" stroke="${color}" stroke-width="${w}" opacity="${o}"/>`;
  // la lumière vient d'en haut : chaque tour est un boudin, sombre juste au-dessus de la rainure, clair juste dessous
  // (sur les côtés de la spirale, le filet clair passe sous la rainure : il ne se voit qu'en haut et en bas de chaque tour)
  return sp(0, -9, STONE.deep, 14, 0.3) + sp(0, -5, STONE.deep, 10, 0.35)
    + sp(0, 12, '#fff4e4', 12, 0.08) + sp(0, 9, '#fff4e4', 7, 0.16) + sp(0, 6.6, '#efe6d8', 2.6, 0.9)
    + sp(0, 0, '#3a3240', 10, 0.8) + sp(0, -1, '#231c28', 4.4, 1);
}

/**
 * Une tache de mousse au bord doux : trois copies emboîtées (de la plus large et transparente à la plus petite et
 * pleine), puis une touche claire vers la lumière.
 */
const moss = (pts, lite) => {
  const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length, cy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
  const sc = (k) => P(pts.map(([x, y]) => [cx + (x - cx) * k, cy + (y - cy) * k]));
  return shape(sc(1.1), MOSS.base, 0.2) + shape(sc(1), MOSS.mid, 0.4) + `<path d="${sc(0.84)}" fill="url(#g-moss)" opacity="0.85"/>`
    + (lite ? shape(P(lite), MOSS.hi, 0.2) : '');
};

// ---------- les yeux ----------
/**
 * Un œil au bout d'une tige : globe gris, blanc décalé vers l'avant, grosse pupille presque noire (un peu de vert en
 * bas), coupée en biais par la paupière (le regard en colère), deux reflets. Le clignement : le globe recouvre le blanc.
 * `lid` = [x0, y0, x1, y1] : la ligne de la paupière, plus basse vers l'arrière.
 */
function stalkEye(k, cx, cy, r, sx, sy, sr, px, py, lid) {
  const white = `M${n(sx - sr)} ${n(sy)}A${sr} ${sr} 0 1 0 ${n(sx + sr)} ${n(sy)}A${sr} ${sr} 0 1 0 ${n(sx - sr)} ${n(sy)}Z`;
  const [x0, y0, x1, y1] = lid;
  const cover = `M${n(x0 - 6)} ${n(sy - sr - 8)}L${n(x1 + 6)} ${n(sy - sr - 8)}L${n(x1 + 6)} ${n(y1)}L${n(x0 - 6)} ${n(y0)}Z`;
  return `<clipPath id="c-${k}"><path d="${white}"/></clipPath>`
    + `<path d="${white}" fill="url(#g-sclera)"/>`
    + `<g clip-path="url(#c-${k})">`
    + oval(px, py, n(sr * 0.86), n(sr * 0.8), 'url(#g-iris)')
    + oval(n(px + 1), n(py - 1.2), n(sr * 0.6), n(sr * 0.58), '#08120e')
    + `<path d="${cover}" fill="#8e8587"/>`
    + `<path d="M${n(x0 - 6)} ${n(y0 - 2.4)}L${n(x1 + 6)} ${n(y1 - 2.4)}" stroke="#bdb4b2" stroke-width="1.6" opacity="0.8"/>`
    + `<path d="M${n(x0 - 6)} ${n(y0)}L${n(x1 + 6)} ${n(y1)}" stroke="#3e3640" stroke-width="2.2"/>`
    + dot(n(px + sr * 0.38), n(py - sr * 0.48), n(sr * 0.29), '#fff')
    + dot(n(px - sr * 0.74), n(py - sr * 0.1), n(sr * 0.11), '#fff', 0.9)
    + `</g>`
    + `<path d="${white}" fill="none" stroke="#5a525c" stroke-width="1.3" opacity="0.6"/>`
    + `<g class="a-blink" opacity="0"><circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#g-ball)"/>${line(`M${n(sx - sr + 1)} ${n(sy + 1)}Q${n(sx)} ${n(sy + sr * 0.5)} ${n(sx + sr - 1)} ${n(sy)}`, '#3e3640', 2.4)}</g>`;
}

// ---------- les morceaux, du fond vers le devant ----------
const parts = [
  // --- les cristaux (derrière la coquille, ils bougent avec elle) ---
  { id: 'cryL', cls: 'a-shell', d: S.cryL,
    body: use('cryL', CRY.mid) + clip('cryL',
      // la pointe : face gauche en demi-teinte, face droite éclairée ; le corps : face avant, face de droite
      shape('M82 69 L61 117 L99 118 Z', CRY.base)
      + shape('M82 69 L99 118 L118 92 Z', 'url(#g-cryTip)')
      + shape('M61 117 L99 118 L110 178 L74 178 Z', 'url(#g-cryL)')
      + shape('M99 118 L118 92 L132 150 L110 178 Z', 'url(#g-cryR)')
      // la lumière dans la pierre : une lame claire, une veine plus sombre, l'arête de devant
      + shape('M72 124 L79 124 L90 176 L83 176 Z', CRY.lite, 0.45)
      + shape('M86 122 L91 122 L101 176 L96 176 Z', CRY.deep, 0.22)
      + line('M61 117 L99 118 L118 92', '#efffe6', 1.4, 0.55) + line('M99 118 L110 178', '#efffe6', 1.6, 0.6)
      + `<g class="a-g1">${shape('M84 76 L67 112 L73 113 Z', CRY.hi, 0.9)}${shape('M103 126 L108 125 L117 170 L111 172 Z', CRY.hi, 0.65)}</g>`
      + `<rect x="50" y="92" width="90" height="90" fill="url(#g-cryBase)"/>`
      + `<g class="a-cflash" opacity="0">${use('cryL', '#eaffd8')}</g>`
    ) },
  { id: 'cryR', cls: 'a-shell', d: S.cryR,
    body: use('cryR', CRY.mid) + clip('cryR',
      shape('M218 68 L196 90 L211 108 Z', CRY.base)
      + shape('M218 68 L211 108 L231 101 Z', 'url(#g-cryTip)')
      + shape('M196 90 L211 108 L212 140 L190 140 L190 92 Z', 'url(#g-cryL)')
      + shape('M211 108 L231 101 L227 140 L212 140 Z', 'url(#g-cryR)')
      + shape('M200 104 L204 107 L204 138 L200 138 Z', CRY.deep, 0.22)
      + line('M196 90 L211 108 L231 101', '#efffe6', 1.4, 0.55) + line('M211 108 L212 140', '#efffe6', 1.5, 0.6)
      + `<g class="a-g2">${shape('M219 75 L228 99 L223 101 Z', CRY.hi, 0.9)}${shape('M216 113 L221 112 L220 136 L216 136 Z', CRY.hi, 0.6)}</g>`
      + `<rect x="185" y="92" width="50" height="50" fill="url(#g-cryBase)"/>`
      + `<g class="a-cflash" opacity="0">${use('cryR', '#eaffd8')}</g>`
    ) },
  { id: 'cryC', cls: 'a-shell', d: S.cryC,
    // un éclat vert autour des cristaux : invisible au repos, il flambe pendant l'attaque
    body: `<g class="a-flash" opacity="0"><ellipse cx="156" cy="88" rx="118" ry="96" fill="url(#g-flash)"/></g>`
      + use('cryC', CRY.mid) + clip('cryC',
        shape('M162 9 L125 48 L164 61 Z', CRY.base)
        + shape('M162 9 L164 61 L188 47 Z', 'url(#g-cryTip)')
        + shape('M125 48 L164 61 L165 138 L124 138 Z', 'url(#g-cryL)')
        + shape('M164 61 L188 47 L188 138 L165 138 Z', 'url(#g-cryR)')
        // la lumière qui court dans la pierre : lames claires, une veine sombre, les arêtes vives
        + shape('M138 60 L146 63 L148 134 L140 134 Z', CRY.lite, 0.5)
        + shape('M150 65 L154 66 L156 134 L152 134 Z', CRY.deep, 0.22)
        + shape('M176 58 L183 54 L184 134 L177 134 Z', '#d9ffc8', 0.45)
        + line('M125 48 L164 61 L188 47', '#efffe6', 1.5, 0.6) + line('M164 61 L165 138', '#efffe6', 2, 0.75)
        + `<g class="a-g3">${shape('M161 15 L131 47 L138 49 Z', CRY.hi, 0.95)}${shape('M168 69 L173 67 L174 126 L169 128 Z', CRY.hi, 0.6)}`
        // une petite étoile de lumière sur la pointe
        + shape('M170 30 L172 37 L179 39 L172 41 L170 48 L168 41 L161 39 L168 37 Z', '#ffffff', 0.95) + `</g>`
        + `<rect x="120" y="92" width="72" height="50" fill="url(#g-cryBase)"/>`
        + `<g class="a-cflash" opacity="0">${use('cryC', '#eaffd8')}</g>`
      ) },

  // --- le pied : la queue sort de sous la coquille ---
  { id: 'foot', d: S.foot,
    body: use('foot', 'url(#g-foot)') + clip('foot',
      // le dessus de la queue, dans la lumière ; le bas, dans l'ombre
      shape('M8 362 C20 350 40 343 62 339 C48 346 30 354 16 366 Z', BODY.hi, 0.75)
      + shape('M5 369 C40 371 120 371 200 372 C250 372 290 371 318 366 L318 380 L0 380 Z', BODY.shade, 0.45)
      // le pli de la sole, le long du bas du pied
      + line('M40 366 C90 365 150 366 210 367 C250 367 280 365 305 362', BODY.mid, 2, 0.55)
      // quelques marques de la peau, irrégulières
      + line('M36 352 C33 356 35 360 40 359', BODY.line, 1.8, 0.5)
      + line('M58 353 C62 351 66 352 66 356', BODY.line, 1.6, 0.45)
      + line('M84 356 C88 359 93 358 95 354', BODY.line, 1.6, 0.4)
      + line('M24 361 C27 359 30 360 31 363', BODY.line, 1.4, 0.4)
      + line('M212 362 C214 359 218 359 220 361', BODY.line, 1.4, 0.35)
    ) },

  // --- les tiges des yeux, puis les yeux ---
  { id: 'stalkB', cls: 'a-sb', d: S.stalkB,
    body: use('stalkB', 'url(#g-stalk)') + clip('stalkB',
      shape('M290 226 L290.5 190 L291.5 160 L293 136 L297 136 L295.5 170 L295 226 Z', BODY.shade, 0.4)
      + shape('M300 140 L303 140 L302 200 L299 200 Z', BODY.hi, 0.7)) },
  { id: 'eyeB', cls: 'a-sb', d: S.eyeB, shadow: [{ on: ['stalkB'], dx: -2, dy: 5, color: SH.body, o: 0.45 }],
    body: use('eyeB', 'url(#g-ball)') + stalkEye('eb', 302, 122, 19, 307.5, 122.5, 14, 308, 123.5, [294, 117.5, 321, 110.5]) },
  { id: 'stalkF', cls: 'a-sf', d: S.stalkF,
    body: use('stalkF', 'url(#g-stalk)') + clip('stalkF',
      shape('M318 226 L324 206 L338 177 L356 150 L360 152 L343 180 L330 208 L325 228 Z', BODY.shade, 0.4)
      + shape('M343 189 L357 162 L361 164 L347 191 Z', BODY.hi, 0.7)) },
  { id: 'eyeF', cls: 'a-sf', d: S.eyeF, shadow: [{ on: ['stalkF'], dx: -2, dy: 5, color: SH.body, o: 0.45 }],
    body: use('eyeF', 'url(#g-ball)') + stalkEye('ef', 375.5, 139.5, 18.4, 380, 140.5, 13.2, 380.5, 141, [367, 134, 393, 127]) },

  // --- le cou et la tête ---
  { id: 'head', cls: 'a-head', d: S.head, shadow: [{ on: ['foot'], dx: -5, dy: 3, color: SH.body, o: 0.3 }],
    body: use('head', 'url(#g-neck)') + clip('head',
      // la tête, plus claire et plus grise que le cou
      `<rect x="262" y="190" width="130" height="120" fill="url(#g-headTone)"/>`
      // le front et le dessus de la tête dans la lumière
      + shape('M300 206 C318 203 336 208 348 222 C354 232 357 244 357 252 C350 240 340 226 326 216 C316 210 306 208 300 206 Z', BODY.hi, 0.7)
      // le cou : deux grands plis de la peau, chacun avec son ombre et son bord éclairé
      + shape('M276 292 C286 308 293 330 296 374 L306 374 C304 344 298 318 286 300 Z', BODY.shade, 0.4)
      + shape('M289 306 C298 324 303 346 305 374 L308 374 C307 346 302 322 291 304 Z', BODY.hi, 0.3)
      + shape('M321 318 C325 334 327 352 324 371 L316 371 C320 352 320 334 321 318 Z', BODY.shade, 0.38)
      + shape('M323 322 C327 338 329 354 327 371 L324 371 C326 354 325 338 322 324 Z', BODY.hi, 0.4)
      // le dessous du menton et de la lèvre, dans l'ombre
      + shape('M325 330 C327 318 333 308 341 301 C335 312 331 322 331 336 C331 348 333 358 335 366 L326 368 C324 356 324 344 325 330 Z', BODY.shade, 0.45)
      // le bec (la lèvre du haut) : dessus clair, dessous dans l'ombre
      + shape('M352 256 C360 256 368 260 372 268 C368 264 360 262 352 262 Z', BODY.hi, 0.85)
      + shape('M354 268 C361 272 367 278 372 278 C370 281 365 281 361 277 C358 273 355 270 350 269 Z', BODY.shade, 0.6)
      // la bouche ouverte : le fond sombre recule vers le coin, une grosse dent et une petite
      + shape('M349 269 C342 269 334 272 329 278 C333 282 339 284 345 283 C348 281 350 279 352 281 L347 275 Z', 'url(#g-mouth)')
      + shape('M338 271 L347 271 L343.5 282 Z', '#f2efe2')
      + shape('M338 271 L341.5 271 L340.5 278 Z', '#ffffff', 0.9)
      + shape('M331 277 L336.5 276 L334.5 281.5 Z', '#e6e0ce', 0.95)
      // la lèvre du bas qui boude : une avancée claire au-dessus, bien ombrée dessous
      + shape('M333 286 C340 283 349 283 354 287 C356 291 356 295 355 298 C351 292 343 288 333 288 Z', BODY.hi, 0.65)
      + shape('M339 297 C345 299 351 301 356 300 C352 303.5 345 303.5 339 300 Z', BODY.shade, 0.7)
      // la moue : le coin de la bouche descend en un pli effilé
      + shape('M331 279 C322 280 312 286 306 296 C305 299 305 302 306 304 C308 297 314 290 322 286 C326 284 329 283 332 283 Z', BODY.line, 0.85)
      // le sourcil : un gros bourrelet de peau en biais (il descend vers le bec), clair dessus, un pli sombre dessous
      + shape('M310 240 C320 242 332 247 342 253 L340 257 C330 252 320 248 309 246 Z', BODY.shade, 0.35)
      + shape('M306 234.5 C306.5 230.5 311 229.5 316 230.5 C326 232.5 337 238.5 345 245.5 C347.5 248 346.5 252.5 342.5 252.5 C333 247.5 322 242.5 311.5 240 C308 239.2 305.8 237.5 306 234.5 Z', '#f1dfae')
      + shape('M308 233 C311 231 316 231 321 232.5 C329 234.5 337 239 343 244.5 C335 240.5 326 236 318 234 C313 233 310 233.5 308 233 Z', BODY.hi)
      + line('M310 240.3 C321 242.6 333 247.6 342.5 252.6', BODY.line, 1.8, 0.65)
      // l'œil du visage : grand blanc coupé en biais en haut, grosse pupille, reflets
      + `<clipPath id="c-fe"><path id="s-fe" d="M312.5 245 C321 246.5 331 249.5 338.5 252.5 C339.5 259 334.5 264.5 326.5 264.5 C318.5 264.5 312.5 259 312.5 251 Z"/></clipPath>`
      + `<use href="#s-fe" fill="#fbfbf4"/>`
      + `<g clip-path="url(#c-fe)">${oval(327.5, 255, 7.2, 7.6, '#0e1116')}${dot(330.5, 251.5, 2.2, '#fff')}${dot(322.8, 258.6, 1, '#fff', 0.85)}`
      + `${oval(325, 262, 12, 3.5, '#cfd6e0', 0.5)}</g>`
      + `<use href="#s-fe" fill="none" stroke="#33241c" stroke-width="1.5"/>`
      + line('M311 244.5 C321 246 331 249 340 252.5', '#33241c', 2.8)
      + `<g class="a-blink" opacity="0"><use href="#s-fe" fill="${BODY.lite}" stroke="${BODY.lite}" stroke-width="2"/>${line('M312 251 C320 256 331 257 339 253', '#33241c', 2.4)}</g>`
    ) },

  // --- la coquille, devant tout le corps ---
  { id: 'shell', cls: 'a-shell', d: S.shell,
    shadow: [{ on: ['foot', 'head'], dx: -5, dy: 6, color: SH.body, o: 0.42 }, { on: ['cryL', 'cryR', 'cryC'], dx: -3, dy: 5, color: SH.cry, o: 0.4 }],
    rim: { on: ['head', 'foot'], color: '#3e3236', w: 1.3, o: 0.75 },
    body: use('shell', 'url(#g-shell)') + clip('shell',
      // le tour extérieur : un liseré de lumière sur le bord du haut et sur la lèvre, l'ombre en bas à gauche
      `<path d="${P([[50, 200], [64, 170], [90, 146], [124, 129], [167, 122], [212, 127], [250, 145], [276, 172], [287, 206], [287, 240], [280, 266]], false)}" fill="none" stroke="${STONE.hi}" stroke-width="7" opacity="0.55"/>`
      + `<path d="${P([[40, 230], [40, 270], [46, 300], [60, 322], [84, 337], [120, 346], [160, 351]], false)}" fill="none" stroke="#2c2436" stroke-width="16" opacity="0.28"/>`
      + `<path d="${P([[42, 236], [42, 272], [47, 298], [59, 318]], false)}" fill="none" stroke="#9fb4c8" stroke-width="2.4" opacity="0.45"/>`
      // la lèvre de l'ouverture, claire, contre la tête
      + shape(P([[279, 266], [285, 240], [287, 212], [283, 190], [278, 196], [279, 222], [276, 248], [270, 268]]), '#bcb2a6', 0.7)
      // la mousse : des plaques aux bords déchiquetés, relevées sur l'original (sous les cristaux, à gauche, deux à droite)
      + moss([[136, 123], [110, 129], [72, 152], [73, 166], [65, 171], [54, 189], [57, 198], [64, 204], [74, 199], [86, 201],
        [91, 194], [102, 195], [105, 184], [118, 186], [127, 184], [131, 178], [129, 170], [138, 163], [142, 140]],
        [[80, 160], [96, 148], [116, 138], [132, 134], [124, 146], [106, 154], [90, 166]])
      + moss([[52, 207], [51, 218], [42, 221], [37, 252], [44, 279], [56, 295], [70, 282], [84, 270], [82, 252], [69, 241],
        [64, 221]],
        [[48, 226], [58, 224], [62, 236], [52, 240]])
      + moss([[260, 288], [243, 281], [227, 283], [213, 291], [212, 303], [223, 317], [224, 325], [247, 326], [249, 320],
        [261, 305]],
        [[226, 290], [242, 286], [254, 293], [244, 296], [232, 297]])
      + moss([[211, 163], [212, 174], [227, 175], [231, 181], [238, 180], [239, 176], [251, 176], [248, 162], [240, 150],
        [226, 151]],
        [[226, 156], [238, 154], [245, 162], [236, 163]])
      // la spirale
      + spiral()
      // le cœur de la spirale, plus clair
      + oval(168, 262, 17, 15, 'url(#g-glow)', 0.22)
      // quelques fissures de la pierre, irrégulières, avec leur arête éclairée
      + line('M171 262 L172 268 L170 275', STONE.line, 1.5, 0.7) + line('M178 262 L179 271', STONE.line, 1.3, 0.6)
      + line('M120 180 L128 186 L126 194', STONE.line, 1.5, 0.6) + line('M121 179 L129 185', STONE.hi, 1, 0.5)
      + line('M232 214 L242 218 L246 228', STONE.line, 1.5, 0.6) + line('M233 213 L243 217', STONE.hi, 1, 0.5)
      + line('M200 312 L206 320 L204 330', STONE.line, 1.5, 0.6)
      + line('M104 236 L112 244 L110 252', STONE.line, 1.4, 0.55)
      + line('M150 316 L156 322 L166 323', STONE.line, 1.4, 0.5)
      + line('M262 196 L270 204', STONE.line, 1.4, 0.5)
      // la grande lumière du haut de la coquille
      + shape(P([[150, 132], [190, 129], [230, 140], [258, 160], [240, 156], [204, 142], [170, 137]]), '#ffffff', 0.3)
    ) },
];

// ---------- la vie au repos ----------
// les tiges se balancent chacune à son rythme, le cou s'étire un peu (il rampe), la coquille suit le pas,
// les cristaux scintillent, les yeux clignent.
// L'attaque (classe « atk » sur le <svg>, 0,75 s) : il rentre dans sa coquille (tête et tiges rétrécies), puis jaillit
// tête en avant pendant que les cristaux flambent, et revient exactement à la pose du repos.
const HEAD_O = [300, 372];   // le pied du cou : la tête rétrécit et s'étire depuis ce point
// [pourcentage, décalage x, décalage y, échelle] de la tête pendant l'attaque
const HEAD_ATK = [[0, 0, 0, 1], [35, -16, 5, 0.85], [50, 24, -3, 1.05], [62, 20, -2, 1.04], [100, 0, 0, 1]];
const STALK_B = [297, 214], STALK_F = [330, 214];   // le pied de chaque tige, sous la tête
const tf = (dx, dy, rot, sc) => `translate(${n(dx)}px,${n(dy)}px) rotate(${rot}deg) scale(${sc})`;
const kf = (name, rows) => `@keyframes ${name}{${rows.map(([p, t]) => `${p}%{transform:${t}}`).join('')}}`;
/** Une tige suit la tête (son pied reste planté dans la tête), puis tourne et s'allonge autour de son pied. */
const stalkAtk = (name, base, moves) => kf(name, HEAD_ATK.map(([p, dx, dy, sc], i) => {
  const x = HEAD_O[0] + dx + sc * (base[0] - HEAD_O[0]), y = HEAD_O[1] + dy + sc * (base[1] - HEAD_O[1]);
  return [p, tf(x - base[0], y - base[1], moves[i][0], moves[i][1])];
}));
const style = `
.a-sb{transform-origin:${STALK_B[0]}px ${STALK_B[1]}px;animation:sb 2.6s ease-in-out infinite alternate}
.a-sf{transform-origin:${STALK_F[0]}px ${STALK_F[1]}px;animation:sf 3.3s ease-in-out -0.8s infinite alternate}
.a-head{transform-origin:${HEAD_O[0]}px ${HEAD_O[1]}px;animation:head 2.2s ease-in-out infinite alternate}
.a-shell{transform-origin:172px 350px;animation:shell 2.2s ease-in-out infinite alternate}
.a-g1{animation:glint 2.1s ease-in-out infinite alternate}
.a-g2{animation:glint 1.7s ease-in-out -0.6s infinite alternate}
.a-g3{animation:glint 2.7s ease-in-out -1.3s infinite alternate}
.a-blink{animation:blink 4.2s linear infinite}
@keyframes sb{from{transform:none}to{transform:rotate(-4deg)}}
@keyframes sf{from{transform:none}to{transform:rotate(5deg)}}
@keyframes head{from{transform:none}to{transform:scale(1.025,0.985)}}
@keyframes shell{from{transform:none}to{transform:rotate(-0.7deg)}}
@keyframes glint{from{opacity:0.25}to{opacity:1}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
.atk .a-head{animation:head-atk .75s ease-in-out}
.atk .a-sb{animation:sb-atk .75s ease-in-out}
.atk .a-sf{animation:sf-atk .75s ease-in-out}
.atk .a-shell{animation:shell-atk .75s ease-in-out}
.atk .a-flash{animation:flash .75s ease-out}
.atk .a-cflash{animation:cflash .75s ease-out}
.atk .a-g1,.atk .a-g2,.atk .a-g3{animation:glint-atk .75s ease-out}
${kf('head-atk', HEAD_ATK.map(([p, dx, dy, sc]) => [p, tf(dx, dy, 0, sc)]))}
${stalkAtk('sb-atk', STALK_B, [[0, 1], [10, 0.5], [-12, 1.1], [-8, 1.06], [0, 1]])}
${stalkAtk('sf-atk', STALK_F, [[0, 1], [-10, 0.5], [14, 1.1], [9, 1.06], [0, 1]])}
@keyframes shell-atk{0%{transform:rotate(0deg)}35%{transform:rotate(-3deg)}50%{transform:rotate(2deg)}62%{transform:rotate(1.6deg)}100%{transform:rotate(0deg)}}
@keyframes flash{0%,30%{opacity:0}48%{opacity:1}100%{opacity:0}}
@keyframes cflash{0%,34%{opacity:0}46%{opacity:.6}60%{opacity:.15}100%{opacity:0}}
@keyframes glint-atk{0%,30%{opacity:0.25}48%{opacity:1}100%{opacity:0.25}}
`.replace(/\n/g, '');

module.exports = { id: 'cuirasses-4', w: W, h: H, pad: 40, foot: [172, 377],
  svg: (anime = true) => figure({ w: W, h: H, pad: 40, outline: '#221c26', defs, style, parts, anime }) };
