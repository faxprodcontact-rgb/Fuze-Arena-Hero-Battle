// L'épouvantail (epouvantails-2), monstre des Épouvantails : redessiné par le code d'après le dessin d'origine, dans le
// même cadre (540 × 476, mêmes proportions, même pose) : planté sur son piquet, les bras en croix ; vieux chapeau de
// paille cabossé à bandeau rouge, le bord gauche qui pend et déchiré ; tête en toile de sac, yeux taillés qui luisent
// jaune, gros plis de sourcils froncés, petit nez en trou, bouche en dents de scie éclairée de l'intérieur ; veste
// turquoise à manches déchirées, deux liens de toile aux bras, pièce rouge sur la poitrine, ceinture de cuir à boucle,
// basques en lambeaux fendues devant ; de la paille qui sort du col, des manches, du chapeau et du bas de la veste.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 540, H = 476;

// ---------- couleurs ----------
const SACK = { hi: '#f6e8c8', lite: '#e2cda4', base: '#c9ae82', mid: '#ab9064', shade: '#83694a', deep: '#5a4630' };
const HAT = { hi: '#fbeab4', lite: '#ecd08a', base: '#d2ab5e', mid: '#b88c44', shade: '#8e6630', deep: '#5e4020' };
const STRAW = { hi: '#fff4c0', lite: '#f8d47c', base: '#e2aa48', mid: '#c4862e', shade: '#94601e', deep: '#5e3814' };
const TEAL = { hi: '#a6f2ea', lite: '#62d2cc', base: '#2fb0b2', mid: '#20909c', shade: '#176a7a', deep: '#0e4858' };
const WRAP = { hi: '#f2d08e', base: '#b8843e', shade: '#86561f', deep: '#5a3814' };
const WOOD = { hi: '#c99058', base: '#8a5a32', shade: '#64401f', deep: '#3e240f' };
const SH = { teal: '#06303c', straw: '#4a2a0a', sack: '#3a2614', wood: '#24120a' };

// ---------- outils ----------
/** Courbe lisse qui passe par des points ([x, y] ; [x, y, 1] = coin net). `closed` = forme fermée. */
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
/** Chemin lisse (Catmull-Rom) passant par des points, à la suite d'un chemin déjà commencé. */
function cr(P) {
  let d = '';
  for (let i = 0; i < P.length - 1; i++) {
    const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)];
    d += `C${n(p1[0] + (p2[0] - p0[0]) / 6)} ${n(p1[1] + (p2[1] - p0[1]) / 6)} ${n(p2[0] - (p3[0] - p1[0]) / 6)} ${n(p2[1] - (p3[1] - p1[1]) / 6)} ${n(p2[0])} ${n(p2[1])}`;
  }
  return d;
}
/** Ruban effilé le long d'une ligne : pts = [[x, y, largeur], …]. */
function rib(pts) {
  const L = [], R = [];
  pts.forEach(([x, y, w], i) => {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1];
    const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
    const h = w / 2;
    L.push([x - dy * h, y + dx * h]); R.push([x + dy * h, y - dx * h]);
  });
  R.reverse();
  return `M${n(L[0][0])} ${n(L[0][1])}${cr(L)}L${n(R[0][0])} ${n(R[0][1])}${cr(R)}Z`;
}
/** Un reflet ou une ombre effilée le long d'une ligne. */
const glint = (pts, color, o = 1) => shape(rib(pts), color, o);
const mix = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];

/**
 * Un brin de paille : un fuseau courbe de la racine r (cachée sous le tissu) à la pointe t, large de w à la racine.
 * `sag` place le point de contrôle : 0,5 = brin droit ; plus petit = le brin part à plat puis retombe (ou se relève).
 */
function strandAt([r, t, w, sag = 0.4], u) {
  const c = [(r[0] + t[0]) / 2, r[1] + (t[1] - r[1]) * sag];
  return [(1 - u) * (1 - u) * r[0] + 2 * u * (1 - u) * c[0] + u * u * t[0], (1 - u) * (1 - u) * r[1] + 2 * u * (1 - u) * c[1] + u * u * t[1], w * Math.pow(1 - u, 0.55)];
}
const strandD = (s) => rib([0, 0.3, 0.62, 1].map((u) => strandAt(s, u)));
/** Une touffe = des brins, peints du fond vers le devant. La silhouette est leur réunion. */
const tuft = (strands) => strands.map(strandD).join('');
/**
 * L'habillage d'une touffe : chaque brin à son tour, avec sa petite ombre portée sur ceux d'avant ; les brins du fond
 * plus sombres, ceux de devant (`front`, éclairés) plus clairs ; un reflet en forme sur les brins `lit`.
 */
function strawBody(id, strands, front, lit) {
  const inner = strands.map((s, i) => {
    const d = strandD(s);
    return shape(d, SH.straw, 0.42).replace('<path', '<path transform="translate(-2 3.5)"') + shape(d, `url(#g-${id}${front.includes(i) ? 'F' : ''})`);
  }).join('') + lit.map((i) => {
    const [a, b, c] = [0.36, 0.64, 0.9].map((u) => strandAt(strands[i], u));
    return glint([[a[0] + 0.6, a[1] - 1.2, 0], [b[0] + 0.6, b[1] - 1.6, 4], [c[0], c[1] - 0.6, 0]], STRAW.hi, 0.85);
  }).join('');
  return use(id, `url(#g-${id})`) + clip(id, inner);
}
/** Les deux dégradés d'une touffe, de la racine (à l'ombre) vers le bout des brins : le fond, puis la gerbe de devant. */
const strawGrad = (id, x1, y1, x2, y2) => lin(`g-${id}`, x1, y1, x2, y2, [[0, STRAW.deep], [0.3, STRAW.shade], [0.72, STRAW.mid], [1, STRAW.base]])
  + lin(`g-${id}F`, x1, y1, x2, y2, [[0, STRAW.shade], [0.28, STRAW.mid], [0.6, STRAW.base], [0.88, STRAW.lite], [1, STRAW.hi]]);

// ---------- dégradés ----------
const defs = [
  lin('g-pole', 250, 0, 288, 0, [[0, WOOD.deep], [0.3, WOOD.shade], [0.62, WOOD.base], [0.86, WOOD.hi], [1, WOOD.base]]),
  strawGrad('strawL', 128, 220, 6, 214),
  strawGrad('strawR', 446, 214, 536, 212),
  strawGrad('strawBL', 232, 326, 168, 404),
  strawGrad('strawBR', 326, 326, 372, 404),
  strawGrad('hairL', 240, 120, 200, 126),
  strawGrad('hairR', 334, 110, 360, 112),
  rad('g-collar', 286, 172, 74, [[0, STRAW.deep], [0.45, STRAW.shade], [0.75, STRAW.mid], [1, STRAW.base]]),
  rad('g-collarF', 286, 172, 74, [[0, STRAW.shade], [0.45, STRAW.mid], [0.7, STRAW.base], [0.9, STRAW.lite], [1, STRAW.hi]]),
  lin('g-coat', 196, 300, 346, 176, [[0, '#136070'], [0.4, TEAL.mid], [0.75, TEAL.base], [1, '#4cc8c4']]),
  lin('g-skirt', 178, 352, 362, 286, [[0, '#0f5262'], [0.45, '#1c8090'], [1, '#34aeb0']]),
  lin('g-armL', 0, 172, 0, 262, [[0, '#4cc2c0'], [0.45, '#2398a2'], [1, '#125e6e']]),
  lin('g-armR', 0, 172, 0, 256, [[0, '#6ad8d2'], [0.45, '#30aeb2'], [1, '#156a7a']]),
  lin('g-wrap', 0, 0, 0, 1, [[0, WRAP.hi], [0.35, WRAP.base], [1, WRAP.deep]], false),
  rad('g-sack', 322, 110, 112, [[0, SACK.lite], [0.4, SACK.base], [1, SACK.mid]]),
  lin('g-hat', 236, 74, 336, 8, [[0, HAT.mid], [0.5, HAT.base], [1, HAT.lite]]),
  lin('g-band', 0, 0, 0, 1, [[0, '#f4593e'], [0.45, '#d4342a'], [1, '#8e1a1c']], false),
  lin('g-belt', 0, 0, 0, 1, [[0, '#b07446'], [0.45, '#80502c'], [1, '#52301a']], false),
  lin('g-buckle', 0, 0, 1, 1, [[0, '#fff2b8'], [0.45, '#e8b84a'], [1, '#9a6418']], false),
  lin('g-patch', 296, 270, 332, 226, [[0, '#a02418'], [0.5, '#dc3e2a'], [1, '#ff6e4c']]),
  rad('g-eye', 0.5, 0.62, 0.62, [[0, '#ffffff'], [0.3, '#fff7a8'], [0.65, '#ffd02e'], [1, '#ea901a']], false),
  rad('g-glow', 0.5, 0.5, 0.5, [[0, '#fff6b0', 0.85], [0.42, '#ffd23a', 0.45], [1, '#ffb020', 0]], false),
  lin('g-mouth', 0, 0, 0, 1, [[0, '#1a0604'], [0.55, '#3a1006'], [1, '#6e260a']], false),
  rad('g-mglow', 0.5, 0.5, 0.5, [[0, '#ffe070', 0.9], [0.45, '#ff9a24', 0.55], [1, '#ff7010', 0]], false),
].join('');

// ---------- touffes de paille ----------
// Chaque mèche : [racine, pointe, largeur, courbure]. Du fond vers le devant ; les numéros « devant » sont éclairés.
// les deux manches : la paille sort du poignet en éventail, les mèches du bas retombent
const ST_L = [[[124, 236], [60, 276], 20, 0.3], [[124, 206], [30, 214], 20, 0.42], [[124, 186], [64, 178], 18, 0.5],
  [[124, 248], [74, 292], 22, 0.3], [[124, 238], [46, 306], 24, 0.28], [[124, 226], [16, 262], 24, 0.32], [[124, 214], [4, 228], 24, 0.4], [[124, 202], [6, 196], 22, 0.46],
  [[124, 190], [40, 176], 20, 0.5], [[124, 182], [92, 166], 16, 0.5]];
const ST_R = [[[448, 240], [494, 270], 18, 0.3], [[448, 216], [512, 232], 20, 0.4], [[448, 194], [506, 180], 18, 0.5],
  [[448, 244], [478, 288], 20, 0.3], [[448, 234], [506, 288], 22, 0.3], [[448, 222], [530, 250], 22, 0.36], [[448, 210], [538, 214], 22, 0.45], [[448, 198], [526, 184], 20, 0.5],
  [[448, 186], [490, 162], 16, 0.5]];
// le bas de la veste : deux gerbes de part et d'autre du piquet, devant lui
const ST_BL = [[[220, 326], [186, 384], 18, 0.35], [[248, 330], [228, 392], 16, 0.42],
  [[204, 322], [152, 374], 18, 0.3], [[214, 326], [170, 396], 20, 0.3], [[262, 330], [262, 394], 16, 0.5], [[252, 330], [240, 410], 18, 0.42], [[226, 328], [192, 408], 20, 0.35],
  [[240, 330], [216, 414], 18, 0.4]];
const ST_BR = [[[340, 326], [362, 386], 18, 0.33], [[314, 330], [322, 394], 16, 0.42],
  [[356, 322], [388, 376], 18, 0.3], [[346, 326], [370, 400], 20, 0.3], [[298, 330], [294, 396], 16, 0.5], [[308, 330], [310, 412], 18, 0.42], [[334, 328], [352, 404], 20, 0.36],
  [[320, 330], [332, 414], 18, 0.4]];
// le col : une collerette de paille tout autour du cou, sous le menton (de gauche à droite)
const ST_C = [[[252, 178], [214, 184], 14, 0.5], [[258, 184], [226, 208], 18, 0.45], [[266, 186], [246, 224], 18, 0.45], [[276, 188], [266, 234], 18, 0.45], [[288, 190], [288, 240], 18, 0.45],
  [[300, 188], [312, 234], 18, 0.45], [[310, 186], [332, 220], 18, 0.45], [[318, 182], [350, 200], 17, 0.45], [[322, 178], [360, 182], 14, 0.5]];
// sous le chapeau, de chaque côté de la tête
const ST_HL = [[[240, 138], [208, 150], 14, 0.4], [[240, 124], [199, 132], 15, 0.48], [[240, 110], [204, 110], 14, 0.5]];
const ST_HR = [[[334, 120], [358, 124], 12, 0.5], [[334, 106], [358, 104], 12, 0.5]];

// ---------- silhouettes ----------
const S = {
  pole: 'M253 296 L286 296 C287 360 286 420 285 468 C276 472 261 472 251 468 C252 420 253 360 253 296 Z',
  skirt: sm([[202, 284, 1], [342, 284, 1], [352, 302], [358, 322], [366, 346, 1], [352, 335, 1], [345, 353, 1], [331, 339, 1], [321, 355, 1], [308, 341, 1], [299, 352, 1], [293, 316, 1],
    [287, 351, 1], [275, 338, 1], [263, 353, 1], [249, 339, 1], [235, 352, 1], [221, 337, 1], [207, 350, 1], [195, 334, 1], [174, 345, 1], [180, 322], [190, 302]]),
  coat: 'M206 186 C226 174 256 169 286 169 C312 169 332 173 345 182 C347 210 346 250 348 280 L351 299 Q272 306 193 299 L197 280 C199 250 200 214 206 186 Z',
  // la manche de gauche de l'image (son bras droit) : poignet et dessous déchirés
  armL: sm([[214, 180], [190, 174], [150, 175], [122, 178], [110, 176, 1], [115, 190, 1], [106, 204, 1], [113, 218, 1], [104, 234, 1], [112, 248, 1], [106, 262, 1], [128, 258], [148, 257, 1],
    [151, 268, 1], [156, 264, 1], [161, 273, 1], [166, 262, 1], [171, 257, 1], [184, 254, 1], [187, 264, 1], [192, 260, 1], [196, 252, 1], [206, 246], [214, 222], [217, 200]]),
  // la manche de droite de l'image (son bras gauche)
  armR: sm([[336, 180], [362, 174], [402, 174], [440, 177], [462, 180, 1], [456, 192, 1], [464, 206, 1], [457, 220, 1], [465, 234, 1], [458, 246, 1], [436, 248], [404, 250], [384, 252, 1],
    [380, 262, 1], [374, 258, 1], [369, 267, 1], [364, 255, 1], [352, 254], [342, 248], [334, 228], [333, 204]]),
  head: sm([[234, 98], [226, 122], [228, 150], [240, 174], [262, 188], [288, 193], [314, 187], [334, 171], [345, 146], [346, 120], [340, 98], [290, 90]]),
  hat: sm([[146, 111, 1], [152, 101, 1], [158, 104, 1], [166, 95], [192, 86], [218, 77], [235, 71, 1], [236, 48], [242, 24], [257, 10], [277, 7], [292, 13], [308, 7], [325, 13], [334, 34],
    [338, 62, 1], [364, 67], [386, 73], [402, 79, 1], [394, 88], [372, 96], [342, 101], [300, 104], [262, 103], [228, 102], [196, 104], [170, 108], [154, 113]]),
};

// ---------- le visage ----------
// les orbites (trous dans la toile) et les yeux qui luisent dedans ; le bord du haut, droit et penché vers le nez,
// fait le regard mauvais
const SOCK_L = 'M249 106 L286 122 C284 130 278 135 268 135 C258 135 251 129 249 120 Z';
const GLOW_L = 'M253 110.5 L281 123 C279 129 274 132 267 132 C259 132 254 127 253 120 Z';
const SOCK_R = 'M338 110 L304 125 C306 132 312 136 320 136 C329 135 335 129 338 120 Z';
const GLOW_R = 'M334 114 L309 125.5 C311 130 315 133 320 133 C328 133 332 128 334 121 Z';
const MOUTH = 'M249 147 L259 151 L266 163 L273 154 L288 156 L298 168 L306 157 L320 154 L327 163 L332 151 L339 145 L335 162 L324 175 L314 163 L306 178 L290 181 L281 167 L272 179 L259 173 Z';

/** Un œil : l'orbite sombre, l'œil qui luit (dégradé), l'ombre de la paupière en haut, le cœur blanc. */
function eye(key, sock, glow, lid, core) {
  return shape(sock, '#2a1008')
    + `<clipPath id="c-${key}"><path d="${glow}"/></clipPath><g class="a-flick">`
    + shape(glow, 'url(#g-eye)')
    + `<g clip-path="url(#c-${key})">${line(lid, '#b0560c', 6, 0.75)}${core}</g></g>`;
}
/** Un gros pli de toile en guise de sourcil : son ombre portée, le bourrelet, l'arête éclairée. */
const brow = (d, hiD) => `<path d="${d}" fill="none" stroke="${SACK.deep}" stroke-width="12" transform="translate(-1.5 3)" opacity="0.6"/>`
  + `<path d="${d}" fill="none" stroke="${SACK.mid}" stroke-width="11"/>` + line(hiD, SACK.hi, 3, 0.8);

const headBody = use('head', 'url(#g-sack)') + clip('head',
  // l'ombre propre : un croissant en bas à gauche, jusque sous le menton
  shape('M220 108 C218 150 238 188 286 196 C314 198 332 188 342 172 C320 184 290 186 268 178 C246 168 234 146 232 108 Z', SACK.shade, 0.6)
  // la lumière en haut à droite, un reflet sur la joue
  + oval(330, 128, 8, 17, SACK.hi, 0.35, 12)
  // deux petits plis de toile au menton, là où le sac est serré
  + glint([[268, 186, 0], [276, 190, 2.4], [284, 194, 0]], SACK.deep, 0.5) + glint([[300, 192, 0], [308, 189, 2.2], [316, 184, 0]], SACK.deep, 0.45)
  // les halos des yeux, sur la toile autour des orbites
  + `<g class="a-glowL">${oval(268, 121, 26, 17, 'url(#g-glow)', 1, 24)}</g><g class="a-glowR">${oval(321, 123, 22, 15, 'url(#g-glow)', 1, -24)}</g>`
  // les yeux
  + eye('eL', SOCK_L, GLOW_L, 'M249 106 L286 122', oval(268, 126.5, 6, 2.6, '#fffef2', 0.9, 18))
  + eye('eR', SOCK_R, GLOW_R, 'M338 110 L304 125', oval(320, 128.5, 5, 2.4, '#fffef2', 0.9, -18))
  // les sourcils : deux plis froncés qui plongent vers le nez
  + brow('M243 98 Q266 103 291 117', 'M246 96 Q266 100 288 112') + brow('M344 102 Q322 108 300 121', 'M342 99 Q322 104 302 116')
  // le nez : un petit trou
  + shape('M297 131 C299 134 303 139 304 142 C300 143.5 295 143.5 291 142 C293 138 295 134 297 131 Z', '#2a1008')
  // la bouche en dents de scie : l'épaisseur claire de la toile au bord du bas, le trou, la lueur du dedans
  + `<clipPath id="c-mouth"><path d="${MOUTH}"/></clipPath><g class="a-mouth">`
  + `<path d="${MOUTH}" fill="${SACK.lite}" transform="translate(0 2.4)"/>`
  + `<path d="${MOUTH}" fill="url(#g-mouth)"/>`
  + `<g clip-path="url(#c-mouth)">${oval(294, 180, 38, 15, 'url(#g-mglow)')}</g></g>`
);

// ---------- le chapeau ----------
const BAND = 'M234 50 Q285 58 337 47 L339 63 Q286 72 234 67 Z';
const hatBody = use('hat', 'url(#g-hat)') + clip('hat',
  // le bord du chapeau : l'ombre de la calotte sur sa gauche, la tranche sombre tout le long du devant
  shape('M150 104 C186 88 214 78 236 70 L236 76 C262 80 284 80 300 76 C290 90 250 98 200 104 Z', HAT.mid, 0.55)
  + glint([[148, 112, 6], [196, 104.5, 7], [262, 103.5, 7], [342, 101.5, 7], [398, 85, 6]], HAT.shade, 0.85)
  + glint([[340, 70, 0], [370, 72, 3.4], [398, 79, 0]], HAT.hi, 0.85)
  + glint([[176, 96, 0], [200, 88, 2.4], [224, 80, 0]], HAT.lite, 0.6)
  // la calotte : son flanc gauche à l'ombre, la bosse et le creux du dessus, l'arête droite éclairée
  + shape('M236 72 L236 48 C238 34 244 20 257 10 C250 26 248 46 252 70 Z', HAT.shade, 0.6)
  + glint([[292, 14, 0], [290, 25, 3], [286, 40, 0]], HAT.shade, 0.7) + glint([[296, 15, 0], [295, 25, 1.8], [291, 38, 0]], HAT.hi, 0.75)
  + glint([[312, 10, 0], [326, 18, 3.2], [334, 40, 0]], HAT.hi, 0.85) + oval(304, 20, 7, 3.5, HAT.hi, 0.5, -10)
  // le bandeau rouge : il fait le tour de la calotte (d'un bord à l'autre), clair en haut à droite
  + `<path d="${BAND}" fill="url(#g-band)"/>`
  + glint([[244, 53, 0], [290, 57.5, 2.4], [332, 50, 0]], '#ff9a7a', 0.8)
  + glint([[236, 66, 0], [286, 71, 3], [336, 63, 0]], '#5a0c12', 0.5)
  // l'ombre du bandeau et de la calotte sur le bord, juste dessous
  + glint([[236, 72, 0], [270, 76, 4], [306, 75, 3], [338, 66, 0]], HAT.shade, 0.55)
);

// ---------- la veste ----------
const coatBody = use('coat', 'url(#g-coat)') + clip('coat',
  // le flanc gauche à l'ombre, une lumière douce en haut à droite
  shape('M188 176 C206 214 210 262 200 306 L180 306 L180 176 Z', TEAL.shade, 0.55)
  + oval(322, 214, 18, 36, TEAL.hi, 0.22, -8)
  // un pli qui descend de l'aisselle gauche
  + glint([[212, 236, 0], [226, 252, 3.4], [244, 268, 0]], TEAL.deep, 0.45) + glint([[216, 232, 0], [230, 247, 2], [247, 263, 0]], TEAL.lite, 0.35)
  // la patte de boutonnage : un creux sombre et une arête claire ; deux boutons et le fil d'un troisième, arraché
  + glint([[285, 184, 0], [284, 230, 3], [283, 281, 0]], TEAL.deep, 0.55) + glint([[288.6, 186, 0], [287.8, 232, 1.8], [287, 281, 0]], TEAL.hi, 0.45)
  + dot(290, 206, 3.6, WRAP.deep) + dot(291, 205, 2.6, WRAP.base) + dot(292, 204, 1, WRAP.hi)
  + dot(290, 258, 3.6, WRAP.deep) + dot(291, 257, 2.6, WRAP.base) + dot(292, 256, 1, WRAP.hi)
  + line('M290 231 C292 235 290 238 292 242', '#e8d8b0', 1.3, 0.9)
  // la pièce rouge cousue sur la poitrine : son ombre, la pièce, l'arête éclairée, deux points de couture
  + shape('M296 230 L310 226 L318 229 L330 225 L333 240 L329 252 L333 266 L318 270 L308 266 L296 271 L298 256 L293 244 Z', SH.teal, 0.4, 0).replace('<path', '<path transform="translate(-2 3)"')
  + shape('M296 230 L310 226 L318 229 L330 225 L333 240 L329 252 L333 266 L318 270 L308 266 L296 271 L298 256 L293 244 Z', 'url(#g-patch)')
  + glint([[312, 228, 0], [322, 228, 1.8], [330, 226.5, 1.4], [332, 238, 0]], '#ff9a7a', 0.85)
  + line('M297 236 L302 232', '#5a0c0c', 1.6, 0.9) + line('M327 266 L332 262', '#5a0c0c', 1.6, 0.9)
  // un accroc sur le flanc : le trou sombre, le bord du tissu éclairé dessous
  + shape('M222 214 L230 218 L236 216 L233 226 L226 230 L224 222 Z', '#0a3440') + line('M224 229 L233 225', TEAL.lite, 1.4, 0.7)
  // l'ombre du col de paille sur le haut de la veste
  + glint([[214, 190, 0], [250, 214, 6], [286, 232, 7], [322, 214, 6], [348, 192, 0]], SH.teal, 0.22)
  // la ceinture de cuir (d'un bord à l'autre) et sa boucle
  + shape('M186 280 Q272 287 358 280 L358 299 Q272 306 186 299 Z', 'url(#g-belt)')
  + glint([[192, 282, 0], [272, 287.5, 2.2], [352, 282, 0]], '#d8a06a', 0.7)
  + shape('M276 281 L297 281 C298 288 298 296 297 303 L277 303 C276 296 276 288 276 281 Z', 'url(#g-buckle)')
  + shape('M280.5 285 L292.5 285 L293 299 L281 299 Z', '#4a2a14')
  + line('M283 292 L292 292', '#d8a83a', 2.2) + line('M277 282.5 L296 282.5', '#fff6c8', 1.2, 0.8)
);

const skirtBody = use('skirt', 'url(#g-skirt)') + clip('skirt',
  // les plis : chaque fois un creux sombre et une arête claire, qui s'élargissent vers l'ourlet
  glint([[232, 300, 0], [228, 326, 3.6], [223, 350, 5]], TEAL.deep, 0.5) + glint([[237, 302, 0], [234, 326, 2.2], [230, 348, 3]], TEAL.lite, 0.4)
  + glint([[264, 302, 0], [262, 328, 3.4], [260, 352, 4.6]], TEAL.deep, 0.45) + glint([[269, 304, 0], [268, 328, 2], [267, 350, 2.8]], TEAL.lite, 0.35)
  + glint([[322, 302, 0], [326, 328, 3.4], [330, 352, 4.6]], TEAL.deep, 0.4) + glint([[327, 302, 0], [332, 326, 2.2], [337, 348, 3]], TEAL.hi, 0.4)
  // le bord du bas, plus sombre ; le fond de la fente, à l'ombre
  + glint([[176, 342, 8], [222, 346, 9], [270, 348, 9], [300, 348, 8], [362, 342, 8]], TEAL.deep, 0.35)
  + glint([[293, 318, 0], [290, 336, 4], [288, 352, 5]], SH.teal, 0.5)
);

const sleeveL = use('armL', 'url(#g-armL)') + clip('armL',
  // l'arête éclairée du haut, le dessous à l'ombre, le creux du poignet
  glint([[214, 181, 0], [180, 179, 3.2], [140, 181, 3], [114, 183, 0]], TEAL.hi, 0.45)
  + glint([[108, 260, 10], [150, 258, 10], [204, 250, 10]], TEAL.deep, 0.5)
  + glint([[113, 180, 0], [118, 218, 5], [113, 258, 0]], SH.teal, 0.55)
  // un pli à l'épaule
  + glint([[198, 196, 0], [206, 214, 3], [208, 236, 0]], TEAL.deep, 0.4) + glint([[202, 192, 0], [210, 210, 1.8], [212, 230, 0]], TEAL.lite, 0.35)
  // le lien de toile autour du bras : son ombre, le lien, l'arête éclairée à droite
  + shape('M148 168 C144 200 144 232 150 266 L186 266 C182 232 182 200 186 168 Z', SH.teal, 0.45).replace('<path', '<path transform="translate(-3 4)"')
  + shape('M150 168 C146 200 146 232 152 266 L188 266 C184 232 184 200 188 168 Z', 'url(#g-wrap)')
  + glint([[185, 176, 0], [182, 206, 2.6], [182, 236, 2.2], [186, 258, 0]], WRAP.hi, 0.6)
  + glint([[166, 182, 0], [164, 214, 2.4], [168, 250, 0]], WRAP.shade, 0.5)
);
const sleeveR = use('armR', 'url(#g-armR)') + clip('armR',
  glint([[338, 181, 0], [380, 177, 3.4], [430, 179, 3.2], [458, 183, 0]], TEAL.hi, 0.55)
  + glint([[336, 252, 10], [400, 252, 10], [462, 248, 10]], TEAL.deep, 0.5)
  + glint([[458, 182, 0], [454, 214, 4.4], [458, 246, 0]], SH.teal, 0.5)
  + glint([[352, 192, 0], [356, 212, 2.6], [354, 232, 0]], TEAL.deep, 0.35)
  + shape('M388 168 C392 200 392 232 388 260 L410 260 C414 232 414 200 410 168 Z', SH.teal, 0.45).replace('<path', '<path transform="translate(-3 4)"')
  + shape('M390 168 C394 200 394 232 390 260 L412 260 C416 232 416 200 412 168 Z', 'url(#g-wrap)')
  + glint([[410, 176, 0], [413, 206, 2.6], [413, 236, 2.2], [410, 252, 0]], WRAP.hi, 0.6)
  + glint([[396, 182, 0], [398, 214, 2.2], [396, 248, 0]], WRAP.shade, 0.5)
);

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  // --- le piquet, planté dans le sol ---
  { id: 'pole', cls: 'a-body', d: S.pole, body: use('pole', 'url(#g-pole)') + clip('pole',
    glint([[280, 300, 0], [281, 380, 2.4], [280, 466, 0]], '#e0b07a', 0.6)
    + glint([[262, 330, 0], [261, 372, 2.6], [263, 404, 0]], WOOD.deep, 0.6) + glint([[265, 334, 0], [264.5, 370, 1.4], [266, 400, 0]], WOOD.hi, 0.5)
    + oval(270, 428, 4.5, 7, WOOD.deep, 0.8) + oval(271.5, 426, 2, 3.4, WOOD.hi, 0.6)
    + shape('M251 452 C262 458 276 458 286 452 L286 474 L250 474 Z', WOOD.deep, 0.6)) },
  // --- les fonds de paille, pris dans la silhouette de l'original (tout derrière : les pointes fines des brins) ---
  { id: 'strawBaseL', cls: 'a-strawL', d: 'M111 141 L107 142 L97 138 L93 144 L88 143 L84 146 L80 145 L72 148 L67 145 L53 144 L40 150 L38 155 L44 152 L58 152 L64 159 L67 167 L62 169 L63 172 L67 176 L76 180 L73 182 L65 182 L58 178 L53 178 L55 180 L59 180 L61 183 L51 183 L28 188 L18 194 L13 200 L10 201 L8 205 L5 219 L6 225 L9 225 L13 218 L22 214 L30 215 L21 225 L23 229 L30 225 L46 224 L26 240 L27 241 L32 237 L41 239 L32 251 L30 264 L31 275 L46 263 L45 261 L48 255 L51 253 L52 257 L59 252 L60 258 L65 249 L69 245 L71 246 L62 263 L57 277 L56 289 L50 307 L51 311 L60 300 L74 293 L79 282 L85 259 L89 252 L91 255 L87 265 L86 281 L89 280 L92 275 L93 269 L99 259 L101 267 L104 268 L108 260 L113 255 L116 256 L122 248 L132 244 L132 172 L111 170 L103 165 L100 165 L93 154 L98 150 L101 154 L107 157 L115 151 L115 145Z', body: use('strawBaseL', 'url(#g-strawL)') },
  { id: 'strawBaseR', cls: 'a-strawR', d: 'M509 161 L495 169 L488 171 L479 179 L470 184 L466 181 L468 171 L460 174 L453 174 L450 177 L440 181 L440 260 L445 261 L450 267 L453 267 L453 262 L451 259 L458 258 L456 254 L458 251 L469 269 L468 262 L464 256 L466 255 L470 257 L476 265 L474 273 L478 278 L478 284 L475 289 L478 289 L485 283 L486 268 L495 277 L494 286 L496 287 L502 279 L499 263 L492 251 L495 248 L495 245 L504 244 L512 258 L512 267 L516 265 L516 255 L518 253 L517 242 L514 235 L507 229 L525 227 L530 230 L537 216 L537 209 L535 209 L527 201 L519 200 L526 195 L526 192 L515 198 L501 198 L500 189 L497 191 L488 190 L495 186 L503 185 L502 178 L509 170 L511 165Z', body: use('strawBaseR', 'url(#g-strawR)') },
  { id: 'strawBaseB', cls: 'a-strawBL', d: 'M167 339 L168 344 L182 340 L184 342 L166 357 L167 358 L171 355 L173 356 L169 360 L166 367 L156 377 L151 376 L151 381 L153 383 L167 379 L178 373 L185 366 L191 364 L192 365 L185 377 L186 380 L200 368 L201 374 L199 382 L201 385 L192 400 L196 402 L195 406 L199 411 L209 396 L213 395 L217 390 L219 390 L228 381 L228 376 L231 376 L234 373 L237 379 L236 390 L239 392 L241 397 L247 393 L248 394 L247 401 L244 405 L244 410 L246 412 L245 415 L239 419 L237 423 L238 425 L244 429 L248 420 L249 430 L285 430 L286 420 L250 419 L250 330 L174 330ZM290 330 L290 373 L293 385 L297 388 L296 384 L298 374 L301 384 L314 399 L314 401 L318 399 L324 401 L325 399 L322 391 L322 382 L323 381 L326 383 L326 368 L328 369 L328 375 L330 368 L340 379 L341 365 L353 379 L362 382 L365 386 L367 386 L369 382 L379 378 L386 370 L386 368 L384 368 L380 371 L357 348 L362 347 L362 343 L356 330ZM290 393 L290 410 L292 418 L296 410 L296 406Z', body: use('strawBaseB', 'url(#g-strawBL)') },
  // --- la paille du bas de la veste, devant le piquet ---
  { id: 'strawBL', cls: 'a-strawBL', d: tuft(ST_BL), shadow: [sh(['pole'], -3, 5, SH.wood, 0.5)], body: strawBody('strawBL', ST_BL, [6, 7], [7]) },
  { id: 'strawBR', cls: 'a-strawBR', d: tuft(ST_BR), shadow: [sh(['pole'], -3, 5, SH.wood, 0.5)], body: strawBody('strawBR', ST_BR, [6, 7], [7]) },
  // --- la paille des manches ---
  { id: 'strawL', cls: 'a-strawL', d: tuft(ST_L), body: strawBody('strawL', ST_L, [6, 7, 8, 9], [7, 8]) },
  { id: 'strawR', cls: 'a-strawR', d: tuft(ST_R), body: strawBody('strawR', ST_R, [5, 6, 7, 8], [6, 7]) },
  // --- les basques, sous la ceinture ---
  { id: 'skirt', cls: 'a-skirt', d: S.skirt, shadow: [sh(['strawBL', 'strawBR', 'pole'], -3, 6, SH.straw, 0.55)], body: skirtBody },
  // --- le haut de la veste ---
  { id: 'coat', cls: 'a-body', d: S.coat, shadow: [sh(['skirt'], -3, 6, SH.teal, 0.55)], body: coatBody },
  // --- les manches, par-dessus les épaules ---
  { id: 'armL', cls: 'a-body', d: S.armL, shadow: [sh(['coat'], -3, 5, SH.teal, 0.45), sh(['strawL'], -2, 5, SH.straw, 0.55)], body: sleeveL },
  { id: 'armR', cls: 'a-body', d: S.armR, shadow: [sh(['coat'], -3, 5, SH.teal, 0.45), sh(['strawR'], -2, 5, SH.straw, 0.55)], body: sleeveR },
  // --- la collerette de paille ---
  { id: 'collar', cls: 'a-collar', d: tuft(ST_C), shadow: [sh(['coat', 'armL', 'armR'], -3, 6, SH.teal, 0.45)], body: strawBody('collar', ST_C, [4, 5, 6, 7, 8], [5, 7]) },
  // --- la tête : la paille qui dépasse sous le chapeau, le sac, puis le chapeau ---
  { id: 'hairL', cls: 'a-head', d: tuft(ST_HL), body: strawBody('hairL', ST_HL, [1, 2], [2]) },
  { id: 'hairR', cls: 'a-head', d: tuft(ST_HR), body: strawBody('hairR', ST_HR, [1], [1]) },
  { id: 'head', cls: 'a-head', d: S.head, shadow: [sh(['collar', 'coat'], -3, 6, SH.straw, 0.5), sh(['hairL', 'hairR'], -3, 4, SH.straw, 0.4)], body: headBody },
  { id: 'hat', cls: 'a-head', d: S.hat, shadow: [sh(['head', 'hairL', 'hairR'], -4, 6, SH.sack, 0.5)], body: hatBody },
];

// --- seulement quand il est animé : des brins de paille qui s'envolent pendant l'attaque (sans contour) ---
const BITS = [[516, 200, -14], [524, 230, 8], [506, 262, 26], [504, 176, -28]];
const bits = { id: 'bits', d: 'M-900 -900', body: BITS.map(([x, y, a], i) => `<g class="a-bit${i + 1}"><g transform="rotate(${a} ${x} ${y})">`
  + glint([[x - 12, y, 0], [x, y, 4.4], [x + 12, y, 0]], STRAW.lite) + glint([[x - 10, y + 1.2, 0], [x, y + 1.8, 2], [x + 11, y + 0.8, 0]], STRAW.mid, 0.85) + '</g></g>').join('') };

// ---------- la vie au repos et l'attaque ----------
// Repos : le vent. La tête se penche doucement (avec le chapeau), la paille des manches et du bas frémit, chaque touffe à
// son rythme, les basques bougent un peu ; les yeux luisent et vacillent comme une flamme, le reste est planté.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : tout le pantin se penche en arrière sur son piquet (élan), puis se jette
// vers la droite, la tête en avant, les touffes de paille hérissées, les yeux qui flambent, la bouche qui s'ouvre et
// des brins qui s'envolent ; puis il revient exactement à sa place. L'attaque s'ajoute au repos (animation-composition).
const G = [268, 470];
const PIV = { body: G, head: [286, 186], collar: [286, 190], strawL: [118, 218], strawR: [454, 214], strawBL: [226, 326], strawBR: [330, 326], skirt: [272, 288] };
const IDLE = {
  'a-head': ['head', 'head 3.4s ease-in-out infinite alternate'],
  'a-collar': ['collar', 'collar 2.6s ease-in-out infinite alternate'],
  'a-strawL': ['strawL', 'strawL 2.2s ease-in-out infinite alternate'],
  'a-strawR': ['strawR', 'strawR 2.7s ease-in-out infinite alternate'],
  'a-strawBL': ['strawBL', 'strawBL 2.9s ease-in-out infinite alternate'],
  'a-strawBR': ['strawBR', 'strawBR 3.3s ease-in-out infinite alternate'],
  'a-skirt': ['skirt', 'skirt 3.8s ease-in-out infinite alternate'],
};
// tout bascule autour du pied du piquet G (qui reste planté) : [décalage x, y, rotation], aux mêmes instants pour tous
const LEAN = { 0: [0, 0, 0], 30: [0, 0, -4], 48: [0, 0, 7], 62: [0, 0, 5], 82: [0, 0, -0.8], 100: [0, 0, 0] };
/** Une image clé : la bascule commune autour de G, puis le mouvement propre du morceau autour de son pivot O. */
const key = (O, p, [dx, dy, r], [orot = 0, osc = 1] = []) => `${p}%{transform:translate(${dx}px,${dy}px) translate(${G[0] - O[0]}px,${G[1] - O[1]}px) rotate(${r}deg) translate(${O[0] - G[0]}px,${O[1] - G[1]}px) rotate(${orot}deg) scale(${osc})}`;
const atkKeys = (name, k, own = {}) => `@keyframes ${name}{${Object.keys(LEAN).map((p) => key(PIV[k], p, LEAN[p], own[p])).join('')}}`;
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-body{transform-origin:${G[0]}px ${G[1]}px}
.a-glowL{transform-origin:268px 121px;animation:glow 1.5s ease-in-out infinite alternate}
.a-glowR{transform-origin:321px 123px;animation:glow 1.8s ease-in-out -.6s infinite alternate}
.a-flick{animation:flick 4.6s linear infinite}
.a-mouth{transform-origin:294px 160px}
.a-bit1,.a-bit2,.a-bit3,.a-bit4{opacity:0}
@keyframes head{from{transform:none}to{transform:rotate(-2.4deg)}}
@keyframes collar{from{transform:none}to{transform:rotate(1.2deg) scale(1.02)}}
@keyframes strawL{from{transform:none}to{transform:rotate(3deg) scale(1.02)}}
@keyframes strawR{from{transform:none}to{transform:rotate(-3.4deg) scale(1.02)}}
@keyframes strawBL{from{transform:none}to{transform:rotate(2.6deg)}}
@keyframes strawBR{from{transform:none}to{transform:rotate(-2.6deg)}}
@keyframes skirt{from{transform:none}to{transform:rotate(-0.8deg) scale(1.01,1.02)}}
@keyframes glow{from{transform:scale(.9);opacity:.8}to{transform:scale(1.1);opacity:1}}
@keyframes flick{0%,86%{opacity:1}88%{opacity:.35}90%{opacity:1}92%{opacity:.55}94%,100%{opacity:1}}
${atk('a-body', 'body-atk')}${atk('a-head', 'head-atk')}${atk('a-collar', 'collar-atk')}${atk('a-strawL', 'strawL-atk')}${atk('a-strawR', 'strawR-atk')}
${atk('a-strawBL', 'strawBL-atk')}${atk('a-strawBR', 'strawBR-atk')}${atk('a-skirt', 'skirt-atk')}
${atkKeys('body-atk', 'body')}
${atkKeys('head-atk', 'head', { 30: [-6], 48: [8], 62: [5], 82: [-1] })}
${atkKeys('collar-atk', 'collar', { 30: [2, 0.97], 48: [-3, 1.08], 62: [-2, 1.04] })}
${atkKeys('strawL-atk', 'strawL', { 30: [7, 0.92], 48: [-9, 1.16], 62: [-6, 1.08], 82: [1, 1] })}
${atkKeys('strawR-atk', 'strawR', { 30: [-8, 0.9], 48: [10, 1.2], 62: [6, 1.1], 82: [-1, 1] })}
${atkKeys('strawBL-atk', 'strawBL', { 30: [3, 0.96], 48: [-6, 1.1], 62: [-4, 1.05] })}
${atkKeys('strawBR-atk', 'strawBR', { 30: [-3, 0.96], 48: [6, 1.1], 62: [4, 1.05] })}
${atkKeys('skirt-atk', 'skirt', { 30: [1.5], 48: [-3, 1.03], 62: [-2, 1.02] })}
.atk .a-glowL,.atk .a-glowR{animation:glow-atk .75s ease-in-out}
.atk .a-flick{animation:none}
.atk .a-mouth{animation:mouth-atk .75s ease-in-out}
.atk .a-bit1{animation:bit1 .75s ease-out}.atk .a-bit2{animation:bit2 .75s ease-out}.atk .a-bit3{animation:bit3 .75s ease-out}.atk .a-bit4{animation:bit4 .75s ease-out}
@keyframes glow-atk{0%{transform:none}30%{transform:scale(.8)}48%{transform:scale(1.7)}62%{transform:scale(1.4)}100%{transform:none}}
@keyframes mouth-atk{0%{transform:none}30%{transform:scale(.96,.9)}48%{transform:scale(1.06,1.3)}62%{transform:scale(1.04,1.2)}100%{transform:none}}
${BITS.map(([x, y], i) => `.a-bit${i + 1}{transform-origin:${x}px ${y}px}`).join('')}
${BITS.map(([, , a], i) => `@keyframes bit${i + 1}{0%,40%{opacity:0;transform:translate(0,0) rotate(0deg)}52%{opacity:1;transform:translate(${12 + i * 3}px,${(i - 1.5) * 5}px) rotate(${(i % 2 ? 1 : -1) * 30}deg)}85%{opacity:0;transform:translate(${40 + i * 4}px,${(i - 1.5) * 14 - 6}px) rotate(${(i % 2 ? 1 : -1) * 120}deg)}100%{opacity:0;transform:translate(0,0)}}`).join('')}
`.replace(/\n/g, '');

module.exports = { id: 'epouvantails-2', w: W, h: H, pad: 46, foot: G,
  svg: (anime = true) => figure({ master: require('./silhouettes/epouvantails-2.json'), w: W, h: H, pad: 46, defs, style, parts: anime ? [...parts, bits] : parts, anime }) };
