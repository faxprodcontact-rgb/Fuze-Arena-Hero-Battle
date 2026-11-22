// Valdis, la renarde (knights-11) : redessinée par le code d'après le dessin d'origine, dans le même cadre
// (620 × 576, mêmes proportions, même pose) : carré blanc, oreilles de renard orange à l'intérieur rose, petite marque
// au front, grands yeux d'ambre, sourire mauvais à crocs, kimono blanc à larges manches, mantelet et ceinture rouges,
// pantalon rouge bouffant, pieds nus de renard, grande queue orange et blanche, flamme bleue au-dessus de la main ouverte.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. La flamme éclaire en bleu le côté
// droit de la chevelure.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 620, H = 576;

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

/** Une forme effilée (mèche, pli) : une lentille de (x0, y0) à (x1, y1), bombée vers (cx, cy), large de `w` au milieu. */
/**
 * Le poing droit : dessiné droit (dans l'axe du bras), puis pivoté de 45° vers la droite autour du poignet, caché sous
 * la manche. Les silhouettes pivotées vont dans S (contour, ombres), les droites dans S0 : l'habillage du poing est
 * dessiné droit et pivoté d'un bloc (voir HAND_ROT plus bas).
 */
const HAND_ROT = [45, 213, 397];
const S0 = {};
function handSil(key, pts) {
  const [a, cx, cy] = HAND_ROT, c = Math.cos((a * Math.PI) / 180), sn = Math.sin((a * Math.PI) / 180);
  S0[key] = sm(pts);
  return sm(pts.map(([x, y, f]) => [cx + (x - cx) * c - (y - cy) * sn, cy + (x - cx) * sn + (y - cy) * c, f]));
}
/** Un doigt replié vers le haut (main ouverte qui tient la flamme) : de la base (cachée dans la paume) au bout arrondi. */
const FING = { fing4: [577, 353, 584, 339, 10], fing3: [567, 357, 573, 338, 11.5], fing2: [557, 360, 561, 340, 12], fing1: [546, 362, 549, 344, 12] };
function fingerPts(bx, by, tx, ty, w) {
  const L = Math.hypot(tx - bx, ty - by), ux = (tx - bx) / L, uy = (ty - by) / L, nx = -uy, ny = ux, h = w / 2;
  const P = (t, k) => [bx + (tx - bx) * t + nx * h * k, by + (ty - by) * t + ny * h * k];
  // le bout : un demi-cercle (le coussinet du doigt), pas une pointe
  const arc = [-0.75, -0.3, 0.3, 0.75].map((a) => [tx + (nx * Math.sin(a * 2) + ux * Math.cos(a * 2)) * h, ty + (ny * Math.sin(a * 2) + uy * Math.cos(a * 2)) * h]);
  return [P(0, 1), P(0.55, 1.02), P(1, 1), arc[3], arc[2], arc[1], arc[0], P(1, -1), P(0.55, -1.02), P(0, -1), [bx - ux * h * 0.7, by - uy * h * 0.7]];
}
/** Le pli d'une phalange : un petit arc en travers du doigt. */
function crease(bx, by, tx, ty, w, t = 0.52) {
  const L = Math.hypot(tx - bx, ty - by), ux = (tx - bx) / L, uy = (ty - by) / L, nx = -uy, ny = ux, h = w * 0.36;
  const cx = bx + (tx - bx) * t, cy = by + (ty - by) * t;
  return `M${n(cx + nx * h)} ${n(cy + ny * h)} Q${n(cx + ux * 2.2)} ${n(cy + uy * 2.2)} ${n(cx - nx * h)} ${n(cy - ny * h)}`;
}
function taper(x0, y0, cx, cy, x1, y1, w) {
  const dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy) || 1;
  const nx = (-dy / L) * w, ny = (dx / L) * w;
  return `M${n(x0)} ${n(y0)}Q${n(cx + nx)} ${n(cy + ny)} ${n(x1)} ${n(y1)}Q${n(cx - nx)} ${n(cy - ny)} ${n(x0)} ${n(y0)}Z`;
}

// ---------- couleurs ----------
const HAIR = { hi: '#fffdf7', base: '#fbf3e3', mid: '#efe4d2', shade: '#d3c3ae', deep: '#ad9a86', line: '#8c7a68' };
const SKIN = { hi: '#fff3e6', base: '#fdd8ba', shade: '#efab8c', deep: '#da8a6c', line: '#ad5c45' };
const FOX = { hi: '#fff1c6', lite: '#ffc96a', base: '#f59a30', mid: '#e27c1c', shade: '#b8560f', line: '#8a3f0c' };
const CLOTH = { hi: '#ffffff', base: '#f3eee9', shade: '#d8cdd8', deep: '#b3a3bc', line: '#8c7a99' };
const RED = { hi: '#ff9a6a', lite: '#f2683b', base: '#da462a', mid: '#bb3323', shade: '#8c2121', deep: '#661624', line: '#561024' };
const ORA = { hi: '#ffc58e', base: '#f3823f', mid: '#dc6229', shade: '#a8411c', line: '#7a2c14' };
const MAR = { hi: '#d36a66', base: '#962431', shade: '#6a1825', line: '#4a0f19' };
const GOLD = { hi: '#fff3b0', base: '#f6c64a', mid: '#dd9a26', shade: '#a2650f', line: '#74440a' };
const FIRE = { core: '#f4feff', hi: '#bdeeff', lite: '#86d0fb', base: '#4ea9f3', mid: '#2f83e4', deep: '#2059c6', line: '#173d98' };
// les ombres portées : une teinte par matière qui la reçoit
const SH = { skin: '#c4553e', hair: '#5c4a3e', cloth: '#6b5884', red: '#45091a', fox: '#7a3208' };

// ---------- dégradés ----------
const defs = [
  lin('g-tail', 210, 530, 70, 330, [[0, '#c95816'], [0.3, '#ea8126'], [0.68, '#f8a236'], [1, '#ffc65e']]),
  lin('g-fur', 120, 400, 40, 540, [[0, '#ffffff'], [0.45, '#fcf6ee'], [1, '#ddd0c6']]),
  // les ombres et lumières douces de la queue (des taches fondues, jamais des traits)
  rad('g-tailShade', 0.5, 0.5, 0.5, [[0, '#a9440f', 0.6], [1, '#a9440f', 0]], false),
  rad('g-tailLight', 0.5, 0.5, 0.5, [[0, '#ffd27a', 0.85], [1, '#ffd27a', 0]], false),
  rad('g-furShade', 0.5, 0.5, 0.5, [[0, '#a8968a', 0.55], [1, '#a8968a', 0]], false),
  // la chevelure : ivoire chaud, presque blanc en haut à droite, gris chaud en bas à gauche
  lin('g-hairF', 452, 92, 226, 250, [[0, '#fffdf6'], [0.35, '#fbf4e6'], [0.66, '#f3e9d8'], [0.88, '#e2d3bf'], [1, '#d2c0aa']]),
  // l'ombre douce du côté gauche de la tête : une tache fondue, sans bord
  rad('g-hairL', 0.5, 0.5, 0.5, [[0, '#b3a08c', 0.55], [0.6, '#b3a08c', 0.3], [1, '#b3a08c', 0]], false),
  lin('g-hairB', 150, 0, 500, 0, [[0, '#baa999'], [0.18, '#d3c5b6'], [0.4, '#e9dfd1'], [0.84, '#f6f1ea'], [1, '#e6f0f8']]),
  // le bas du carré, plus sombre : le gris chaud des pointes
  lin('g-hairBot', 0, 200, 0, 312, [[0, '#9e8b77', 0], [0.5, '#9e8b77', 0.3], [1, '#9e8b77', 0.55]]),
  // le dessous de la frange, qui s'assombrit doucement vers les pointes
  lin('g-fringeSh', 352, 156, 342, 206, [[0, '#c9b8a2', 0], [1, '#c9b8a2', 0.38]]),
  // une lumière douce (cheveux, reflets) : une tache fondue, sans bord
  rad('g-sheen', 0.5, 0.5, 0.5, [[0, '#ffffff', 0.95], [0.55, '#ffffff', 0.5], [1, '#ffffff', 0]], false),
  rad('g-sheenR', 0.5, 0.5, 0.5, [[0, '#ffb08a', 0.85], [1, '#ffb08a', 0]], false),
  // la lumière bleue de la flamme sur la chevelure et la joue
  rad('g-blue', 560, 250, 125, [[0, '#6cc2ff', 0.95], [0.55, '#8fd2ff', 0.55], [1, '#9ad6ff', 0]]),
  lin('g-ear', 0, 0, 0, 1, [[0, '#ffbf5c'], [0.5, '#f59a30'], [1, '#dd781b']], false),
  lin('g-pink', 0, 0, 0, 1, [[0, '#ffc9bf'], [0.6, '#f2a19b'], [1, '#df8486']], false),
  lin('g-skin', 0, 0, 0, 1, [[0, '#ffe9d4'], [0.6, SKIN.base], [1, '#f6bf9c']], false),
  lin('g-fingTop', 0, 0, 0, 1, [[0, '#d8f2ff', 0.7], [0.5, '#d8f2ff', 0]], false),
  lin('g-foot', 0, 0, 0, 1, [[0, '#f9d2b0'], [0.6, '#f0b892'], [1, '#d68a68']], false),
  rad('g-cheek', 0.32, 0.6, 0.55, [[0, '#fff3e4', 0.9], [1, '#fff3e4', 0]], false),
  rad('g-blush', 0.5, 0.5, 0.5, [[0, '#ff7f7a', 0.5], [1, '#ff7f7a', 0]], false),
  rad('g-iris', 0.5, 0.8, 0.82, [[0, '#ffeaa2'], [0.4, '#f7b23e'], [0.78, '#b9680f'], [1, '#673206']], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#2a1406', 0.65], [0.45, '#2a1406', 0]], false),
  lin('g-mouth', 0, 0, 0, 1, [[0, '#4a0d1e'], [1, '#86202f']], false),
  lin('g-cloth', 0, 0, 0, 1, [[0, '#ffffff'], [0.55, '#f3eee9'], [1, '#d9cfd9']], false),
  lin('g-sleeveR', 0, 344, 0, 438, [[0, '#ffffff'], [0.45, '#f1ecef'], [1, '#cdbfd0']]),
  lin('g-sleeveIn', 0, 0, 0, 1, [[0, '#a685a9'], [1, '#5c4166']], false),
  lin('g-red', 0, 0, 0, 1, [[0, '#f26a3c'], [0.5, '#d9452a'], [1, '#a82b22']], false),
  lin('g-legL', 182, 0, 312, 0, [[0, '#a92d1f'], [0.5, '#d4432a'], [1, '#ee6439']]),
  lin('g-legR', 364, 0, 472, 0, [[0, '#b93524'], [0.45, '#e2522e'], [1, '#c53b25']]),
  lin('g-belt', 0, 408, 0, 444, [[0, '#ff9a5a'], [0.3, '#ec6b33'], [0.75, '#d4542a'], [1, '#a83d1c']]),
  rad('g-knot', 0.62, 0.3, 0.75, [[0, '#ffa463'], [0.55, '#ea6a2f'], [1, '#b34219']], false),
  lin('g-ora', 0, 0, 0, 1, [[0, '#ffa465'], [1, '#d7602a']], false),
  lin('g-maroon', 0, 0, 0, 1, [[0, '#c2474a'], [0.5, '#962431'], [1, '#5f1622']], false),
  lin('g-capeL', 290, 304, 236, 366, [[0, '#f26c40'], [0.45, '#d8452a'], [1, '#9e2622']]),
  lin('g-capeR', 446, 316, 396, 356, [[0, '#c84a46'], [0.5, '#9a2630'], [1, '#621624']]),
  lin('g-beltL', 250, 0, 312, 0, [[0, '#7a2c14', 0.45], [1, '#7a2c14', 0]]),
  lin('g-gold', 0, 0, 0, 1, [[0, GOLD.hi], [0.45, GOLD.base], [1, GOLD.shade]], false),
  lin('g-waist', 0, 384, 0, 436, [[0, '#6b5884', 0], [1, '#6b5884', 0.32]]),
  lin('g-wrap', 0, 0, 0, 1, [[0, '#fff4dc'], [1, '#e2c49a']], false),
  // la flamme bleue : halo, langues, cœur blanc
  rad('g-halo', 550, 268, 92, [[0, '#9adaff', 0.6], [0.5, '#8fd4ff', 0.28], [1, '#8fd4ff', 0]]),
  lin('g-flame', 0, 170, 0, 326, [[0, '#2f86ea'], [0.45, '#48a6f4'], [1, '#78c6fb']]),
  lin('g-flameIn', 0, 200, 0, 330, [[0, '#8fd5ff'], [1, '#d9f5ff']]),
  rad('g-core', 548, 303, 26, [[0, '#ffffff'], [0.5, '#f2fdff'], [1, '#c8f0ff', 0]]),
  // la flamme lancée : une boule de feu à traîne
  lin('g-shot', 478, 0, 600, 0, [[0, '#8fd4ff', 0], [0.45, '#4ea9f3', 0.85], [1, '#2f86ea']]),
  rad('g-shotHalo', 0.5, 0.5, 0.5, [[0, '#9adaff', 0.6], [1, '#9adaff', 0]], false),
  rad('g-shotCore', 0.5, 0.5, 0.5, [[0, '#ffffff'], [0.6, '#effcff'], [1, '#c8f0ff', 0]], false),
  rad('g-soft', 0.5, 0.5, 0.5, [[0, '#fff6ea', 0.85], [1, '#fff6ea', 0]], false),
].join('');

// ---------- silhouettes ----------
const S = {
  // la queue : un croissant qui part de derrière la jambe et remonte en pointe vers la gauche
  tail: sm([[66, 323, 1], [48, 334], [33, 350], [22, 372], [15, 398], [14, 425], [17, 452], [26, 476], [40, 497], [58, 516], [80, 532], [106, 544], [132, 549], [160, 548], [190, 540], [222, 518], [236, 476], [222, 440], [202, 414], [184, 396], [168, 390], [152, 399], [132, 404], [112, 399], [95, 390], [80, 378], [69, 361], [62, 341]]),
  // le pan de tissu bordeaux qui dépasse derrière la jambe droite
  flapR: sm([[452, 478], [478, 496], [500, 506], [503, 514], [494, 520], [472, 523], [455, 518]]),
  // les pieds nus : quatre gros orteils à griffes
  footL: sm([[154, 546], [152, 556], [157, 563], [166, 564], [173, 560, 1], [178, 566], [190, 567], [201, 564], [205, 560, 1], [210, 566], [220, 566], [229, 561], [232, 557, 1], [238, 560], [244, 557], [247, 550], [253, 548], [262, 546], [266, 540], [262, 528], [240, 524], [210, 524], [182, 528], [164, 535]]),
  footR: sm([[402, 540], [403, 552], [410, 557], [430, 558], [440, 561], [450, 562], [460, 565], [470, 564], [474, 560, 1], [480, 564], [487, 563], [490, 559, 1], [495, 560], [499, 554], [496, 546], [486, 540], [474, 535], [458, 532], [438, 531], [416, 533]]),
  // le pantalon bouffant
  legL: sm([[240, 418], [300, 416], [316, 450], [312, 486], [301, 512], [288, 530], [270, 543], [248, 540], [224, 537], [198, 535], [176, 530], [180, 515], [192, 498], [206, 478], [220, 458], [232, 440]]),
  legR: sm([[362, 420], [440, 422], [452, 446], [460, 470], [467, 492], [471, 512], [469, 530], [446, 537], [420, 539], [398, 537], [386, 528], [379, 510], [372, 490], [365, 466], [361, 440]]),
  // le pan de la ceinture qui retombe sur la cuisse droite
  sashR: sm([[402, 413], [424, 423], [446, 436], [465, 451], [470, 463, 1], [450, 462], [430, 450], [406, 434]]),
  // le tablier blanc et les deux rubans du nœud
  apron: sm([[322, 436], [374, 436], [378, 466], [373, 495], [361, 499, 1], [351, 492, 1], [340, 499, 1], [327, 494, 1], [319, 468]]),
  loopL: sm([[330, 437], [304, 443], [282, 452], [266, 462, 1], [282, 467], [306, 462], [330, 452]]),
  tieL: sm([[328, 442], [346, 448], [334, 466], [320, 484], [312, 496, 1], [298, 490, 1], [304, 474], [316, 456]]),
  tieR: sm([[346, 449], [362, 442], [378, 456], [392, 474], [404, 488, 1], [392, 496, 1], [380, 480], [364, 463]]),
  neck: sm([[334, 298], [398, 298], [402, 330], [384, 352], [358, 364], [334, 350], [328, 325]]),
  // le kimono : col en V, la poitrine, le flanc
  torso: sm([[218, 326], [260, 313], [300, 315], [328, 322, 1], [357, 353, 1], [392, 320, 1], [418, 320], [444, 336], [432, 370], [410, 388], [400, 408], [404, 430], [330, 436], [266, 432], [250, 410], [236, 372]]),
  belt: sm([[252, 411, 1], [290, 417], [322, 423], [362, 424], [400, 419], [430, 413], [446, 410, 1], [451, 419], [448, 430, 1], [430, 433], [400, 437], [362, 443], [322, 444], [290, 441], [254, 435, 1]]),
  knot: sm([[322, 430], [330, 420], [343, 416], [357, 419], [365, 428], [364, 441], [355, 449], [342, 451], [329, 447], [322, 439]]),
  // le bras gauche : la manche, puis le poing posé sur la hanche
  sleeveL: sm([[212, 325], [252, 322], [266, 336], [262, 352], [252, 370], [248, 387], [252, 410, 1], [237, 406], [220, 403], [202, 406], [186, 411], [172, 409], [160, 404, 1], [164, 392], [170, 379], [173, 365], [179, 351], [194, 337]]),
  fistL: handSil('fistL', [[190, 402], [206, 399], [224, 397], [240, 398], [249, 404], [251, 418], [249, 438], [242, 449], [224, 453], [205, 452], [192, 447], [184, 437], [182, 422], [184, 410]]),
  // les doigts repliés, du haut vers le bas, au bout du poing
  fk1: handSil('fk1', [[220, 411], [236, 410], [248, 412], [253, 417], [251, 422], [238, 423], [221, 422]]),
  fk2: handSil('fk2', [[221, 422], [237, 421], [249, 423], [254, 428], [252, 433], [239, 434], [222, 433]]),
  fk3: handSil('fk3', [[221, 433], [236, 432], [247, 434], [252, 439], [250, 444], [238, 445], [222, 444]]),
  fk4: handSil('fk4', [[220, 444], [232, 443], [241, 445], [245, 449], [242, 453], [232, 454], [221, 453]]),
  // le bras droit : la grande manche ouverte, la main paume en haut
  thumbL: handSil('thumbL', [[205, 404], [216, 400], [227, 402], [236, 407], [243, 413], [244, 420], [239, 424], [232, 421], [223, 415], [213, 410], [206, 409]]),
  sleeveR: sm([[404, 338], [440, 344], [466, 352], [492, 350], [499, 362], [503, 390], [508, 430], [494, 436], [474, 432], [458, 424], [446, 412], [434, 398], [418, 390], [404, 386], [398, 362]]),
  handR: sm([[492, 352], [500, 340], [505, 330], [512, 323], [520, 323], [526, 330], [528, 340], [533, 348], [544, 352], [558, 351], [570, 347], [579, 346], [583, 352], [580, 362], [572, 370], [560, 376], [536, 380], [510, 380], [494, 375]]),
  // le bout des doigts repliés, vus de face
  fing4: sm(fingerPts(...FING.fing4)),
  fing3: sm(fingerPts(...FING.fing3)),
  fing2: sm(fingerPts(...FING.fing2)),
  fing1: sm(fingerPts(...FING.fing1)),
  // le mantelet rouge sur les épaules
  capeL: sm([[332, 332], [316, 318], [296, 309], [270, 305], [244, 307], [222, 314], [208, 325], [204, 336, 1], [214, 344], [232, 348], [252, 352], [270, 360], [288, 368], [302, 373, 1], [314, 362], [324, 348]]),
  capeR: sm([[384, 326], [396, 318], [412, 314], [428, 318], [442, 328], [450, 342, 1], [440, 350], [426, 356], [412, 358, 1], [404, 350], [392, 344]]),
  // la tête : le carré (dos), les oreilles, le visage, puis le dessus de la chevelure et la frange
  hairB: sm([[212, 118], [196, 138], [187, 160], [182, 184], [172, 203], [153, 221, 1], [172, 223], [179, 232], [180, 250], [182, 266], [180, 282, 1], [192, 276, 1], [198, 288], [206, 302, 1], [214, 290, 1], [224, 298], [236, 310, 1], [250, 305], [270, 300], [290, 292], [312, 280], [330, 268], [388, 292], [400, 312], [412, 318], [428, 322], [442, 320, 1], [449, 305], [456, 290], [463, 280], [474, 272, 1], [466, 252], [463, 238], [468, 226], [476, 232, 1], [482, 222], [493, 216, 1], [483, 207], [478, 194], [475, 178], [469, 158], [460, 141], [447, 126], [420, 96], [380, 76], [335, 72], [290, 78], [245, 95]]),
  earS: sm([[238, 212], [222, 207], [210, 214], [205, 232], [206, 252], [213, 267], [226, 276], [240, 277], [252, 260], [252, 225]]),
  earL: sm([[249, 13, 1], [262, 30], [280, 52], [296, 70], [318, 90], [300, 118], [260, 135], [228, 150], [214, 140], [214, 112], [217, 85], [224, 58], [234, 36]]),
  earR: sm([[429, 19, 1], [438, 40], [445, 70], [447, 100], [447, 122], [430, 125], [400, 105], [378, 82], [386, 62], [400, 45], [415, 30]]),
  face: sm([[258, 160], [300, 140], [350, 132], [400, 136], [440, 152], [446, 180], [443, 215], [441, 248], [438, 270], [432, 288], [423, 299], [411, 308], [397, 314], [381, 319], [365, 321], [349, 320], [331, 316], [312, 309], [296, 299], [284, 286], [268, 258], [258, 225]]),
  hairF: sm([[214, 146], [228, 128], [252, 110], [280, 96], [306, 84], [330, 73], [355, 70], [378, 74], [402, 88], [428, 104], [450, 124], [462, 142], [471, 164], [476, 190], [481, 204], [489, 214, 1], [474, 224], [458, 226], [447, 214], [434, 194], [418, 171], [402, 150, 1], [399, 160], [392, 170], [381, 179], [370, 188, 1], [379, 170, 1], [366, 181], [355, 188], [345, 195], [334, 204, 1], [348, 185, 1], [331, 196], [320, 202], [305, 211, 1], [318, 193, 1], [302, 202], [292, 206], [283, 212, 1], [278, 224], [275, 238], [276, 251], [288, 262, 1], [279, 262, 1], [281, 272], [294, 285, 1], [283, 284, 1], [286, 296], [291, 305, 1], [278, 300], [262, 307, 1], [257, 294], [252, 280], [246, 258], [242, 236], [240, 216], [232, 207], [213, 205, 1], [221, 192], [219, 176], [214, 161], [212, 150]]),
};

// ---------- les yeux ----------
/**
 * Un œil : blanc, iris d'ambre en dégradé, pupille, ombre de la paupière, reflets ; puis les cils (une forme pleine) et
 * la paupière du bas. `shut` = la courbe de l'œil fermé (clignement).
 */
function eye(key, white, cx, cy, rx, ry, lash, lower, shut) {
  return `<clipPath id="c-${key}"><path d="${white}"/></clipPath>`
    + `<path d="${white}" fill="#fff"/>`
    + `<g clip-path="url(#c-${key})">`
    + `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="url(#g-iris)"/>`
    + `<ellipse cx="${cx}" cy="${cy}" rx="${rx - 0.9}" ry="${ry - 0.9}" fill="none" stroke="#4a2104" stroke-width="2"/>`
    + `<ellipse cx="${cx}" cy="${n(cy - ry * 0.16)}" rx="${n(rx * 0.6)}" ry="${n(ry * 0.66)}" fill="#1f0c04"/>`
    + `<path d="M${n(cx - rx * 0.72)} ${n(cy + ry * 0.42)} A${n(rx * 0.86)} ${n(ry * 0.8)} 0 0 0 ${n(cx + rx * 0.72)} ${n(cy + ry * 0.42)}" fill="none" stroke="#ffe7a0" stroke-width="2.2" opacity="0.85"/>`
    + `<rect x="${cx - rx - 20}" y="${cy - ry - 10}" width="${2 * rx + 40}" height="${n(ry * 1.45)}" fill="url(#g-lid)"/>`
    + dot(n(cx - rx * 0.4), n(cy - ry * 0.4), n(rx * 0.3), '#fff')
    + dot(n(cx + rx * 0.42), n(cy - ry * 0.02), n(rx * 0.17), '#fff', 0.95)
    + `</g>`
    + shape(lash, '#1e0c18') + line(lower, '#7a3b2a', 1.7, 0.85)
    // le clignement : la paupière (couleur de peau) couvre l'œil et ses cils, il ne reste qu'un trait épais
    + `<g class="a-blink" opacity="0"><path d="${white}" fill="#f6c6a6" stroke="#f6c6a6" stroke-width="3"/><path d="${lash}" fill="#f6c6a6" stroke="#f6c6a6" stroke-width="2"/>${line(shut, '#1e0c18', 4.2)}</g>`;
}

// ---------- les morceaux, du fond vers le devant ----------
const UPPER = ['torso', 'capeL', 'capeR', 'sleeveL', 'sleeveR'];
const parts = [
  // --- la queue : orange à la racine et à la pointe, fourrure blanche sur le ventre de la courbe ---
  { id: 'tail', cls: 'a-tail', d: S.tail,
    body: use('tail', 'url(#g-tail)') + clip('tail',
      // la fourrure blanche : de grandes touffes pointent vers la pointe orange, la racine orange y avance en langues
      shape('M-10 392 L14 396 C20 391 25 382 28 374 C31 383 35 391 41 398 C45 388 48 377 50 366 C54 378 59 390 66 398 C69 393 72 389 74 384 C77 391 82 397 90 401 L150 398 L150 404 C134 407 122 412 114 416 C110 418 106 419 101 420 C108 424 113 428 116 433 C104 440 90 446 76 452 C88 458 98 464 104 470 C98 474 93 477 88 480 C95 484 101 488 104 493 C116 500 134 502 152 505 C168 508 184 512 200 520 L200 580 L-10 580 Z', 'url(#g-fur)')
      // le dessous de la queue, dans l'ombre : de grandes ombres fondues
      + oval(70, 512, 70, 34, 'url(#g-furShade)', 1, 38) + oval(26, 446, 22, 52, 'url(#g-furShade)', 0.8, -4)
      // la pointe : une lumière douce côté lumière
      + oval(58, 356, 9, 26, 'url(#g-tailLight)', 1, 8)
      // la racine orange : une ombre large en bas, une lumière large en haut
      + oval(158, 500, 66, 22, 'url(#g-tailShade)', 1, -8) + oval(170, 428, 52, 16, 'url(#g-tailLight)', 1, 18)
      // une lumière douce sur le galbe de la fourrure
      + oval(40, 440, 9, 36, 'url(#g-sheen)', 0.9, -8)
    ) },

  // --- le pan bordeaux derrière la jambe droite ---
  { id: 'flapR', cls: 'a-flap', d: S.flapR,
    body: use('flapR', 'url(#g-maroon)') + clip('flapR',
      shape('M456 480 C472 492 488 502 502 510 L500 514 C486 508 470 500 456 492 Z', MAR.hi, 0.7)
      + shape('M458 512 C474 514 488 516 500 514 L494 522 L460 524 Z', MAR.line, 0.45)) },

  // --- les pieds nus : gros orteils ronds de renard, griffes claires ---
  { id: 'footL', d: S.footL, shadow: [{ on: ['tail'], dx: -5, dy: 2, color: SH.fox, o: 0.3 }],
    body: use('footL', 'url(#g-foot)') + clip('footL',
      // le dessous des orteils, dans l'ombre ; le dessus du pied éclairé
      shape('M150 552 C162 560 178 562 196 564 C214 566 232 562 248 552 L250 572 L146 572 Z', SKIN.deep, 0.4)
      + shape('M164 536 C186 528 216 526 244 530 L250 538 C220 534 190 536 168 544 Z', SKIN.hi, 0.6)
      + oval(190, 550, 9, 6, 'url(#g-soft)', 1) + oval(218, 551, 8, 5, 'url(#g-soft)', 1))
      // les creux entre les orteils
      + line('M173 560 C171 553 172 547 176 541', SKIN.line, 1.7, 0.9)
      + line('M205 561 C203 554 204 548 207 542', SKIN.line, 1.7, 0.9)
      + line('M232 557 C231 551 232 546 235 542', SKIN.line, 1.7, 0.9)
      // les griffes
      + shape('M156 556 C158 561 162 563 167 562 C166 558 162 556 156 556 Z', '#fff6ea')
      + shape('M183 559 C185 565 190 567 196 566 C195 561 190 559 183 559 Z', '#fff6ea')
      + shape('M212 559 C214 564 219 566 225 564 C224 560 219 558 212 559 Z', '#fff6ea')
      + shape('M236 554 C238 558 241 560 245 558 C244 555 241 553 236 554 Z', '#fff6ea') },
  { id: 'footR', d: S.footR,
    body: use('footR', 'url(#g-foot)') + clip('footR',
      // la plante, le dessous des orteils
      shape('M400 546 C420 552 444 554 470 556 L470 572 L396 572 Z', '#c27264', 0.55)
      + shape('M410 538 C434 532 462 532 486 540 L490 546 C462 540 434 540 412 544 Z', SKIN.hi, 0.6)
      + oval(462, 552, 9, 6, 'url(#g-soft)', 1))
      + line('M474 560 C473 553 474 548 477 544', SKIN.line, 1.7, 0.9)
      + line('M490 558 C489 553 490 549 493 546', SKIN.line, 1.7, 0.9)
      + shape('M459 558 C462 563 467 564 472 562 C470 558 466 557 459 558 Z', '#fff6ea')
      + shape('M480 557 C482 561 486 562 489 560 C488 557 485 556 480 557 Z', '#fff6ea')
      + shape('M493 553 C495 557 497 558 499 556 C498 553 496 552 493 553 Z', '#fff6ea') },

  // --- le pantalon bouffant : un grand galbe éclairé, quelques plis, les bandes molletières déchirées au bas ---
  { id: 'legL', d: S.legL, shadow: [{ on: ['tail'], dx: -6, dy: 3, color: SH.fox, o: 0.32 }, { on: ['footL'], dx: -2, dy: 5, color: SH.skin, o: 0.45 }],
    body: use('legL', 'url(#g-legL)') + clip('legL',
      // le dedans de la jambe, sombre
      shape('M318 470 C310 500 296 524 278 546 L240 546 C262 528 284 500 296 466 Z', RED.deep, 0.55)
      // le galbe de la cuisse
      + shape(taper(252, 458, 270, 466, 300, 470, 9), RED.hi, 0.35) + shape(taper(268, 462, 282, 464, 298, 466, 3), '#ffb48c', 0.7)
      // les plis
      + shape(taper(238, 446, 220, 476, 202, 508, 5), RED.shade, 0.55)
      + shape(taper(244, 452, 230, 478, 214, 502, 2.2), RED.lite, 0.6)
      + shape(taper(302, 432, 290, 462, 268, 494, 4), RED.shade, 0.45)
      + shape(taper(222, 503, 242, 508, 264, 506, 3), RED.shade, 0.45)
      // les bandes molletières, au bord déchiré
      + shape('M168 518 C180 516 188 514 196 515 L203 508 L209 516 C222 516 234 514 245 516 L252 509 L257 518 C266 519 274 520 282 523 L294 546 L166 546 Z', 'url(#g-wrap)')
      + line('M176 527 C206 524 240 526 274 533', '#c79a6a', 1.5, 0.8)
      + shape('M168 533 C206 532 246 536 288 544 L288 550 L166 550 Z', '#b07651', 0.4)
    ) },
  { id: 'legR', d: S.legR, shadow: [{ on: ['flapR'], dx: -3, dy: 3, color: SH.red, o: 0.45 }, { on: ['footR'], dx: -2, dy: 5, color: SH.skin, o: 0.45 }],
    body: use('legR', 'url(#g-legR)') + clip('legR',
      shape('M360 450 C368 480 376 506 392 540 L370 540 L360 470 Z', RED.deep, 0.5)
      + shape(taper(418, 446, 434, 466, 440, 494, 8), RED.hi, 0.35) + shape(taper(428, 448, 436, 462, 440, 478, 2.6), '#ffb48c', 0.7)
      + shape(taper(392, 440, 400, 476, 406, 512, 4.5), RED.shade, 0.5)
      + shape(taper(400, 446, 407, 476, 413, 506, 2), RED.lite, 0.5)
      + shape(taper(448, 450, 456, 480, 460, 512, 4), RED.shade, 0.45)
      + shape('M382 518 C392 517 402 515 410 516 L417 508 L423 517 C434 517 446 516 454 517 L461 511 L466 519 C470 519 474 520 478 520 L478 548 L378 548 Z', 'url(#g-wrap)')
      + line('M388 527 C414 525 444 525 472 529', '#c79a6a', 1.5, 0.8)
      + shape('M380 534 C414 534 444 536 478 538 L478 548 L378 548 Z', '#b07651', 0.4)
    ) },
  // le pan de la ceinture qui retombe sur la cuisse droite
  { id: 'sashR', d: S.sashR, shadow: [{ on: ['legR'], dx: -3, dy: 4, color: SH.red, o: 0.45 }],
    body: use('sashR', 'url(#g-maroon)') + clip('sashR',
      shape(taper(404, 416, 440, 428, 468, 458, 3), '#e98c82', 0.65)
      + shape(taper(408, 436, 436, 448, 458, 462, 2.5), MAR.line, 0.5)) },

  // --- le tablier blanc entre les jambes, les rubans du nœud ---
  { id: 'apron', d: S.apron, shadow: [{ on: ['legL', 'legR'], dx: -4, dy: 4, color: SH.red, o: 0.4 }],
    body: use('apron', 'url(#g-cloth)') + clip('apron',
      shape('M316 482 L380 480 L380 504 L316 504 Z', RED.mid)
      + shape('M316 482 L380 480 L380 485 L316 487 Z', RED.lite, 0.8)
      + shape(taper(346, 442, 342, 462, 346, 484, 3), CLOTH.shade, 0.8)) },
  { id: 'loopL', d: S.loopL, shadow: [{ on: ['legL', 'apron'], dx: -3, dy: 4, color: SH.red, o: 0.4 }],
    body: use('loopL', 'url(#g-ora)') + clip('loopL',
      shape(taper(328, 440, 296, 446, 268, 462, 4), '#ffd88e', 0.9)
      + shape(taper(330, 452, 300, 462, 272, 464, 3), ORA.shade, 0.55)) },
  { id: 'tieL', d: S.tieL, shadow: [{ on: ['legL', 'apron'], dx: -3, dy: 4, color: SH.red, o: 0.4 }],
    body: use('tieL', 'url(#g-ora)') + clip('tieL',
      shape(taper(342, 444, 326, 466, 304, 490, 3.5), ORA.hi, 0.85)
      + shape(taper(330, 446, 316, 466, 300, 484, 2.5), ORA.shade, 0.5)) },
  { id: 'tieR', d: S.tieR, shadow: [{ on: ['legR', 'apron'], dx: -3, dy: 4, color: SH.red, o: 0.4 }],
    body: use('tieR', 'url(#g-ora)') + clip('tieR',
      shape(taper(360, 442, 380, 464, 398, 488, 3.5), ORA.hi, 0.85)
      + shape(taper(356, 452, 372, 470, 388, 490, 2.5), ORA.shade, 0.5)) },

  // --- le cou et son collier ---
  { id: 'neck', cls: 'a-bob', d: S.neck,
    body: use('neck', SKIN.shade) + clip('neck',
      shape('M330 298 L402 298 L402 336 C388 342 372 344 356 342 C344 338 334 330 328 320 Z', SKIN.deep, 0.6))
      + line('M335 330 C342 342 349 352 357 357 C365 352 373 342 381 330', '#5a2430', 1.6, 0.9)
      + `<path d="M352 355 C352 350 357 348 361 350 C365 352 366 358 362 361 C359 363 358 366 360 370 C354 368 351 362 352 355 Z" fill="url(#g-gold)" stroke="${GOLD.line}" stroke-width="1.2"/>` },

  // --- le kimono : panneau rouge du côté gauche, col orange en travers ---
  { id: 'torso', cls: 'a-chest', d: S.torso, shadow: [{ on: ['legL', 'legR', 'apron', 'tieL', 'tieR'], dx: -3, dy: 5, color: SH.red, o: 0.35 }],
    body: use('torso', 'url(#g-cloth)') + clip('torso',
      // le kimono blanc sous le bras, dans l'ombre
      shape('M246 330 C248 370 252 404 258 436 L284 436 C278 404 270 370 262 334 Z', CLOTH.deep, 0.45)
      // le revers rouge du kimono : une bande qui descend de l'épaule à la ceinture, son liseré d'or
      + shape('M272 322 L298 317 C305 332 309 348 311 364 L314 436 L294 436 C292 404 288 374 283 350 C280 338 277 330 272 322 Z', 'url(#g-red)')
      + shape(taper(292, 346, 301, 390, 302, 432, 2.4), '#ffb898', 0.55)
      + line('M311 362 C313 386 314 410 314 434', GOLD.base, 2.2)
      // le col orange qui croise la poitrine
      + shape('M319 347 L328 341 L393 409 L383 415 Z', 'url(#g-ora)')
      + line('M328 342 L393 410', ORA.hi, 1.4, 0.8)
      // le pli du kimono, la courbe de la poitrine, l'ombre du flanc
      + line('M341 356 C346 374 351 392 356 410', CLOTH.line, 1.5, 0.45)
      + line('M396 350 C403 366 403 386 398 402', CLOTH.line, 1.5, 0.5)
      + shape('M404 384 C398 396 398 412 402 436 L430 436 L430 380 Z', CLOTH.deep, 0.45)
      + `<rect x="236" y="380" width="210" height="60" fill="url(#g-waist)"/>`
    ) },

  // --- la ceinture et son gros nœud rond ---
  { id: 'belt', d: S.belt, shadow: [{ on: ['legL', 'legR', 'apron', 'tieL', 'tieR', 'sashR', 'tail'], dx: -2, dy: 5, color: SH.red, o: 0.4 }],
    body: use('belt', 'url(#g-belt)') + clip('belt',
      // la lumière du bord du haut, qui suit la courbe de la taille
      shape(sm([[248, 410, 1], [290, 416], [322, 422], [362, 423], [400, 418], [430, 412], [452, 408, 1], [452, 414, 1], [430, 418], [400, 424], [362, 429], [322, 428], [290, 422], [248, 416, 1]]), ORA.hi, 0.8)
      // l'ombre du bas, le bout gauche qui tourne dans l'ombre, le bout droit qui tourne vers la lumière
      + shape(sm([[248, 430, 1], [290, 436], [322, 439], [362, 438], [400, 432], [430, 428], [454, 424, 1], [454, 448, 1], [248, 448, 1]]), ORA.shade, 0.4)
      + `<rect x="248" y="404" width="64" height="46" fill="url(#g-beltL)"/>`
      + shape(taper(446, 413, 450, 421, 447, 429, 2), ORA.hi, 0.7)
      // deux plis
      + line('M262 425 C276 428 292 432 306 434', ORA.shade, 1.6, 0.5)
      + line('M384 432 C400 429 416 425 432 421', ORA.shade, 1.6, 0.5)) },
  { id: 'knot', d: S.knot, shadow: [{ on: ['belt', 'apron', 'tieL', 'tieR'], dx: -3, dy: 4, color: SH.red, o: 0.4 }],
    body: use('knot', 'url(#g-knot)')
      // une spirale gravée
      + line('M343 433 C346 430 350 433 348 437 C345 441 338 438 338 432 C338 425 347 422 353 427 C359 433 355 444 344 446 C334 447 326 441 327 431', ORA.shade, 1.8, 0.8)
      + oval(353, 423, 6, 3, ORA.hi, 0.85, 10) },

  // le poing : le dos de la main, éclairé, et le talon de la main en bas à gauche
  { id: 'fistL', cls: 'a-bob', d: S.fistL, rim: { on: ['sleeveL', 'belt'], color: SKIN.line, w: 1.1, o: 0.7 },
    shadow: [{ on: ['tail', 'legL', 'belt'], dx: -3, dy: 5, color: SH.fox, o: 0.35 }],
    body: use('fistL', 'url(#g-skin)') + clip('fistL',
      // le dessous du poing et son côté extérieur dans l'ombre, l'ombre du poignet sous la manche
      shape('M178 436 C186 450 204 456 222 456 C232 456 238 452 242 446 L244 462 L174 462 Z', SKIN.shade, 0.6)
      + shape('M180 410 C183 428 188 442 197 452 L176 456 Z', SKIN.shade, 0.5)
      + shape('M184 404 C200 401 218 398 236 397 L238 405 C220 406 202 409 186 413 Z', SKIN.deep, 0.42)
      // le dos de la main éclairé, et le relief des jointures avant les doigts
      + oval(200, 426, 9, 14, 'url(#g-soft)', 1, 0)
      + [[217, 416], [218, 427], [218, 438]].map(([x, y]) => oval(x, y, 3, 4.2, '#fff4ea', 0.55)).join('')) },
  // les doigts repliés : quatre phalanges, chacune pose une ombre douce sur la suivante (les jointures se lisent)
  ...['fk4', 'fk3', 'fk2', 'fk1'].map((id, i, all) => ({
    id, cls: 'a-bob', d: S[id], rim: { on: ['fistL', ...all.slice(0, i)], color: SKIN.line, w: 1.1, o: 0.8 },
    shadow: [{ on: ['fistL', ...all.slice(0, i)], dx: -2, dy: 3, color: SH.skin, o: 0.4 }],
    body: use(id, SKIN.shade) + clip(id, `<use href="#s-${id}" fill="url(#g-skin)" transform="translate(1.5 -2.5)"/>`) })),
  // le pouce, couché sur le dessus du poing, son ongle au bout
  { id: 'thumbL', cls: 'a-bob', d: S.thumbL, rim: { on: ['fistL', 'fk1'], color: SKIN.line, w: 1.1, o: 0.8 },
    shadow: [{ on: ['fistL', 'fk1', 'fk2'], dx: -2, dy: 4, color: SH.skin, o: 0.42 }],
    body: use('thumbL', 'url(#g-skin)') + clip('thumbL',
      shape('M200 410 C212 416 226 422 238 428 L236 436 L194 420 Z', SKIN.shade, 0.55)
      + oval(218, 405, 10, 3, 'url(#g-soft)', 1, 30))
      // l'ongle, au bout du pouce replié sur l'index
      + shape('M237 412 C241 412 244 415 244 419 C242 421 239 421 237 419 C235 417 235 414 237 412 Z', '#ffe9dc', 0.95) },

  // --- le bras gauche : la manche (coude dehors, bas qui pend, poignet en biais), le poing serré sur la hanche ---
  { id: 'sleeveL', cls: 'a-bob', d: S.sleeveL, rim: { on: ['torso'], color: CLOTH.line, w: 1.1, o: 0.6 },
    shadow: [{ on: ['torso', 'belt', 'fistL', 'thumbL'], dx: -2, dy: 5, color: SH.cloth, o: 0.4 }, { on: ['tail'], dx: -5, dy: 4, color: SH.fox, o: 0.3 }],
    body: use('sleeveL', 'url(#g-cloth)') + clip('sleeveL',
      // le dessous du bras et le bas de la manche qui pend sous le coude, dans l'ombre
      shape('M168 366 C174 384 188 396 210 398 C226 396 240 390 248 380 L252 396 L186 418 L154 414 Z', CLOTH.shade, 0.5)
      + shape('M156 384 C166 396 178 403 194 407 L186 416 L152 414 Z', CLOTH.deep, 0.45)
      // le pli du coude
      + shape(taper(192, 358, 214, 374, 240, 366, 4.5), CLOTH.shade, 0.8)
      + shape(taper(236, 344, 216, 348, 200, 358, 3), CLOTH.shade, 0.6)
      // le liseré rouge du poignet, en biais
      + shape('M180 404 C194 401 208 398 222 397 C234 397 244 400 252 403 L254 412 C244 408 232 405 220 404 C206 405 194 408 180 412 Z', RED.lite)
      + shape('M180 409 C194 406 208 403 220 402 C234 402 244 405 254 409 L254 413 C244 409 232 406 220 405 C206 406 194 409 180 413 Z', RED.shade, 0.55)) },
  // --- le bras droit : la grande manche, la main ouverte ---
  { id: 'sleeveR', cls: 'a-arm', d: S.sleeveR, rim: { on: ['torso'], color: CLOTH.line, w: 1.1, o: 0.6 },
    shadow: [{ on: ['torso', 'belt', 'sashR'], dx: -3, dy: 5, color: SH.cloth, o: 0.38 }],
    body: use('sleeveR', 'url(#g-sleeveR)') + clip('sleeveR',
      // le dedans violine de la manche ouverte
      shape('M489 370 C496 368 502 372 505 382 L510 432 L494 438 C491 420 489 398 489 370 Z', 'url(#g-sleeveIn)')
      + shape('M406 386 C420 392 436 402 448 414 C462 428 480 434 500 436 L500 444 L404 444 Z', CLOTH.deep, 0.5)
      + shape(taper(456, 356, 448, 386, 458, 414, 4), CLOTH.shade, 0.75)
      + shape(taper(428, 356, 424, 372, 428, 390, 2.5), CLOTH.shade, 0.6)
      + shape('M412 344 C440 346 466 354 492 352 L492 358 C466 360 440 352 412 350 Z', '#ffffff', 0.9)) },
  // la flamme bleue : pas de contour sombre (elle brille), derrière les doigts. Elle s'anime à part : le halo respire
  // (a-halo), la flamme vacille depuis sa base (a-fl, ses langues claires a-fl2), le cœur pulse (a-core), les gouttes
  // montent (a-sp) ; pendant l'attaque, tout s'embrase (a-flare).
  { id: 'flame', cls: 'a-arm', d: '',
    body: `<g class="a-flare"><circle class="a-halo" cx="550" cy="268" r="92" fill="url(#g-halo)"/>`
      + `<path d="M536 352 C533 340 535 330 541 322 L557 322 C561 330 561 342 554 354 Z" fill="${FIRE.hi}" opacity="0.9"/>`
      + `<g class="a-fl">`
      // le corps de la flamme : une langue centrale en S, une langue de chaque côté
      + `<path d="M548 326 C528 326 508 316 503 298 C499 284 503 270 509 258 C511 251 512 244 513 236 C518 246 522 256 526 266 C527 250 530 236 535 222 C539 210 541 198 541 188 C541 180 545 174 550 170 C548 178 549 186 553 196 C558 208 562 222 564 236 C566 246 567 256 568 266 C574 256 582 246 590 236 C590 248 592 258 595 266 C600 280 600 298 592 310 C584 320 566 326 548 326 Z" fill="url(#g-flame)" stroke="${FIRE.mid}" stroke-width="1.8"/>`
      + shape(taper(544, 196, 538, 226, 538, 258, 2.6), FIRE.lite, 0.8)
      + shape(taper(513, 242, 510, 262, 512, 282, 2), FIRE.lite, 0.7)
      + shape(taper(589, 242, 592, 262, 590, 286, 2), FIRE.deep, 0.35)
      + `<g class="a-fl2"><path d="M548 322 C532 322 518 314 514 300 C511 290 514 280 520 272 C523 280 528 286 534 290 C534 272 538 254 545 238 C551 254 556 272 557 290 C563 286 568 280 572 272 C578 282 581 294 578 304 C574 316 562 322 548 322 Z" fill="url(#g-flameIn)"/></g>`
      + `<ellipse class="a-core" cx="548" cy="303" rx="25" ry="18" fill="url(#g-core)"/>`
      + `</g>`
      // les gouttes de feu qui s'échappent
      + `<g class="a-sp" fill="${FIRE.base}">`
      + `<path d="M550 166 C548 162 549 157 551 153 C553 157 553 162 550 166 Z"/>`
      + `<path d="M522 199 C520 196 521 192 523 190 C525 192 525 196 522 199 Z"/>`
      + `<path d="M515 221 C513 216 514 211 517 207 C519 211 519 216 515 221 Z"/>`
      + `<path d="M512 234 C510 231 511 228 513 226 C515 228 515 231 512 234 Z"/>`
      + `<path d="M560 196 C558 193 559 189 561 187 C563 189 563 193 560 196 Z"/>`
      + `<path d="M584 215 C582 211 583 207 586 204 C588 207 588 211 584 215 Z"/>`
      + `<path d="M587 232 C585 228 586 224 589 221 C591 224 591 228 587 232 Z"/>`
      + `</g></g>`
      // la boule de feu lancée pendant l'attaque (invisible au repos)
      + `<g class="a-shot" opacity="0"><circle cx="576" cy="290" r="36" fill="url(#g-shotHalo)"/>`
      + `<path d="M600 290 C600 303 589 313 575 313 C548 313 518 303 474 292 C518 281 548 267 575 267 C589 267 600 277 600 290 Z" fill="url(#g-shot)"/>`
      + `<path d="M593 290 C593 299 585 306 575 306 C557 306 537 300 508 291 C537 282 557 274 575 274 C585 274 593 281 593 290 Z" fill="${FIRE.hi}" opacity="0.85"/>`
      + `<ellipse cx="578" cy="290" rx="12" ry="10" fill="url(#g-shotCore)"/>`
      + `<path d="M520 276 C517 273 518 269 521 267 C523 270 523 273 520 276 Z M528 307 C525 304 526 300 529 298 C531 301 531 304 528 307 Z M496 284 C493 281 494 278 497 276 C499 279 499 282 496 284 Z" fill="${FIRE.base}"/>`
      + `</g>` },
  { id: 'handR', cls: 'a-arm', d: S.handR, rim: { on: ['sleeveR'], color: SKIN.line, w: 1.1, o: 0.7 },
    shadow: [{ on: ['sleeveR'], dx: -3, dy: 4, color: SH.cloth, o: 0.35 }],
    body: use('handR', 'url(#g-skin)') + clip('handR',
      // le creux de la paume, éclairé en bleu par la flamme ; le dessous de la main
      oval(540, 352, 18, 10, '#bfe6ff', 0.6, -8)
      + shape('M496 370 C520 376 548 376 570 366 L576 384 L494 384 Z', SKIN.shade, 0.65)
      + oval(512, 334, 4.5, 8, 'url(#g-soft)', 1, 14)
      // le bracelet
      + `<path d="M497 348 C493 356 493 368 497 377" fill="none" stroke="${GOLD.line}" stroke-width="5.6"/>`
      + `<path d="M497 348 C493 356 493 368 497 377" fill="none" stroke="${GOLD.base}" stroke-width="3.4"/>`)
      // le pli du pouce, la séparation des doigts du fond
      + line('M527 339 C530 345 532 351 533 357', SKIN.line, 1.4, 0.75) },
  // le bout des doigts : chacun pose une ombre douce sur la paume ; un trait fin dessine son bord du haut
  ...['fing4', 'fing3', 'fing2', 'fing1'].map((id, i, all) => {
    const [bx, by, tx, ty, w] = FING[id];
    return {
      id, cls: 'a-arm', d: S[id], rim: { on: all.slice(0, i), color: SKIN.line, w: 1.1, o: 0.8 },
      shadow: [{ on: ['handR', ...all.slice(0, i)], dx: -2.5, dy: 2.5, color: SH.skin, o: 0.38 }],
      body: use(id, SKIN.shade) + clip(id,
        `<use href="#s-${id}" fill="url(#g-skin)" transform="translate(2 -1)"/>`
        + use(id, 'url(#g-fingTop)')
        + line(crease(bx, by, tx, ty, w, 0.4), SKIN.line, 1.1, 0.5)
        + oval(n(tx + 1.8), n(ty - 1), 2.2, 2.8, '#fff6ec', 0.75, 15)),
    };
  }),

  // --- le mantelet rouge sur les épaules ---
  { id: 'capeL', cls: 'a-bob', d: S.capeL, shadow: [{ on: ['torso', 'sleeveL'], dx: -3, dy: 6, color: SH.red, o: 0.35 }],
    body: use('capeL', 'url(#g-capeL)') + clip('capeL',
      // le rond de l'épaule, éclairé ; le dessous, contre le bras, dans l'ombre
      oval(272, 316, 36, 10, 'url(#g-sheenR)', 1, 4)
      + shape('M200 330 C212 338 226 344 242 348 L240 364 L196 364 Z', RED.deep, 0.4)
      // le grand pli qui descend de l'épaule vers la pointe, son bord éclairé
      + shape(taper(256, 314, 278, 342, 298, 370, 5), RED.shade, 0.5)
      + shape(taper(266, 312, 290, 336, 306, 364, 2.5), '#ff9a72', 0.55))
      // l'ourlet doré suit le bord du châle
      + line('M208 341 C228 347 250 351 270 359 C282 365 292 369 300 372', GOLD.base, 2.2, 0.95) },
  { id: 'capeR', cls: 'a-bob', d: S.capeR, shadow: [{ on: ['torso', 'sleeveR'], dx: -3, dy: 6, color: SH.red, o: 0.35 }],
    body: use('capeR', 'url(#g-capeR)') + clip('capeR',
      // le rond de l'épaule, éclairé ; un pli qui retombe
      oval(422, 322, 20, 6, 'url(#g-sheenR)', 1, 16)
      + shape(taper(410, 318, 418, 338, 414, 358, 4), MAR.shade, 0.5))
      + line('M392 345 C404 352 418 356 448 344', GOLD.base, 2, 0.9) },

  // --- la tête ---
  // le carré, derrière : on n'en voit que les côtés (à gauche dans l'ombre, à droite éclairé en bleu par la flamme)
  { id: 'hairB', cls: 'a-bob', d: S.hairB, shadow: [{ on: ['capeL', 'capeR', 'torso', 'neck'], dx: -3, dy: 6, color: SH.red, o: 0.35 }],
    body: use('hairB', 'url(#g-hairB)') + clip('hairB',
      // le dedans du carré, près du visage
      shape('M240 196 C226 222 222 254 232 284 C238 296 246 304 254 308 L262 308 L262 196 Z', HAIR.deep, 0.3)
      + `<rect x="150" y="200" width="120" height="120" fill="url(#g-hairBot)"/>`
      // le haut du côté gauche tourne vers la lumière ; une lueur douce sur chaque pointe du bas
      + oval(198, 172, 12, 36, 'url(#g-sheen)', 0.55, 20)
      + oval(187, 258, 6, 18, 'url(#g-sheen)', 0.6, 6) + oval(209, 276, 6, 20, 'url(#g-sheen)', 0.6, -4)
      // une ombre courte sépare les pointes
      + shape(taper(192, 276, 192, 260, 195, 244, 2.6), HAIR.deep, 0.6)
      + shape(taper(214, 290, 212, 274, 215, 258, 2.6), HAIR.deep, 0.6)
      // à droite : la mèche éclairée en bleu par la flamme, son côté plus sombre contre le visage
      + `<rect x="420" y="120" width="90" height="210" fill="url(#g-blue)"/>`
      + shape(taper(442, 214, 447, 260, 438, 306, 6), HAIR.shade, 0.6)
      + oval(464, 242, 7, 30, 'url(#g-sheen)', 0.7, -10)) },
  // l'oreille (humaine) sur le côté de la tête, devant le carré
  { id: 'earS', cls: 'a-bob', d: S.earS, shadow: [{ on: ['hairB'], dx: -3, dy: 4, color: SH.hair, o: 0.35 }],
    body: use('earS', 'url(#g-skin)')
      + shape('M236 216 C226 213 216 218 213 232 C211 246 214 258 222 266 C228 270 236 270 240 266 C232 260 226 250 226 238 C226 228 230 220 236 216 Z', SKIN.shade, 0.75)
      + line('M231 226 C225 233 225 244 229 252', SKIN.line, 1.5, 0.7) },
  // les oreilles de renard : orange dehors, rose dedans, duvet blanc au creux ; leur base passe sous la chevelure
  { id: 'earL', cls: 'a-earL', d: S.earL, shadow: [{ on: ['hairB'], dx: -3, dy: 4, color: SH.hair, o: 0.3 }],
    body: use('earL', 'url(#g-ear)') + clip('earL',
      shape('M249 24 C262 44 276 66 288 92 C276 104 252 116 228 130 C224 100 230 60 249 24 Z', 'url(#g-pink)')
      + shape('M252 16 C266 34 284 56 302 76 L296 84 C282 64 266 44 250 26 Z', FOX.hi, 0.9)
      + shape('M234 36 C224 62 218 92 216 132 L223 130 C223 98 229 66 240 42 Z', FOX.shade, 0.35)
      + shape('M236 124 C240 112 246 102 255 94 C254 102 256 108 260 112 C264 102 271 95 280 91 C277 101 278 109 283 115 C268 124 250 128 236 124 Z', '#fffaf4')
      + shape('M244 120 C252 118 262 116 272 112 C264 118 254 122 244 124 Z', '#d9c9d2', 0.7)) },
  { id: 'earR', cls: 'a-earR', d: S.earR, shadow: [{ on: ['hairB'], dx: -3, dy: 4, color: SH.hair, o: 0.3 }],
    body: use('earR', 'url(#g-ear)') + clip('earR',
      shape('M428 30 C420 50 412 74 406 100 C420 110 434 116 446 118 C446 90 440 58 428 30 Z', 'url(#g-pink)')
      + shape('M432 22 C440 44 445 74 446 112 L441 112 C440 80 436 52 427 32 Z', FOX.hi, 0.8)
      + shape('M392 58 C402 46 414 34 426 26 L428 32 C416 42 404 54 396 66 Z', FOX.lite, 0.6)
      + shape('M412 110 C416 100 422 92 430 86 C430 94 432 100 436 104 C438 96 442 90 447 86 L447 118 C434 118 422 116 412 110 Z', '#fffaf4')) },
  { id: 'face', cls: 'a-bob', d: S.face, rim: { on: ['hairB'], color: SKIN.line, w: 1.1, o: 0.6 },
    shadow: [{ on: ['neck', 'capeL', 'capeR', 'torso'], dx: -2, dy: 8, color: SH.skin, o: 0.45 }, { on: ['hairB', 'earS'], dx: -3, dy: 4, color: SH.hair, o: 0.3 }],
    body: use('face', 'url(#g-skin)') + clip('face',
      `<rect x="255" y="190" width="120" height="130" fill="url(#g-cheek)"/>`
      + shape('M262 196 C276 230 286 266 312 306 L300 306 C280 286 266 258 258 226 Z', SKIN.shade, 0.55)
      + oval(300, 282, 22, 13, 'url(#g-blush)') + oval(424, 278, 14, 11, 'url(#g-blush)')
      // la lumière bleue de la flamme sur la joue droite
      + `<rect x="400" y="180" width="60" height="140" fill="url(#g-blue)" opacity="0.4"/>`)
    // la marque de la joue
    + shape('M295 264 C298 262 303 262 306 265 C305 269 302 273 300 275 C298 272 294 268 295 264 Z', '#e0545e')
    + oval(301, 266, 2, 1.2, '#ff9aa0', 0.9)
    // les yeux : la paupière du haut est une ligne droite qui plonge vers le nez et coupe le haut de l'iris
    + eye('eL', 'M287 231 C302 225 324 228 346 241 C344 249 336 255 322 256 C306 257 294 251 289 243 C287 239 286 235 287 231 Z', 322, 243, 13.5, 15,
      'M278 220 C283 223 287 225 290 226 C305 221 326 224 351 239 L352 244 C340 237 324 231 307 231 C299 231 293 235 289 240 C286 235 283 229 278 220 Z',
      'M291 247 C300 254 312 257 325 256 C334 255 340 251 344 246', 'M289 239 C304 247 328 249 345 242')
    + eye('eR', 'M386 243 C400 231 420 226 441 227 C443 234 443 241 440 247 C435 253 424 256 412 256 C400 256 391 250 386 243 Z', 413, 244, 12.5, 14,
      'M383 244 C396 231 418 223 442 223 L438 216 C442 218 445 221 446 224 L451 221 C450 226 447 229 443 232 C432 230 420 231 410 234 C400 237 392 241 384 248 Z',
      'M394 250 C401 254 411 257 422 256 C431 255 437 251 440 247', 'M387 244 C402 252 426 252 441 240')
    // les sourcils : brun sombre, épais, ils plongent vers le nez et appuient sur l'œil
    + shape('M280 205 C300 201 322 207 342 219 C350 224 356 230 360 238 C352 238 345 235 338 231 C320 221 302 215 283 214 C279 212 278 208 280 205 Z', '#4a2e27')
    + shape('M380 238 C387 227 401 217 419 209 C431 204 442 200 451 198 C453 203 452 208 448 211 C432 214 416 222 402 231 C394 236 387 240 380 238 Z', '#4a2e27')
    + line('M286 207 C304 205 322 210 338 219', '#86625a', 1.4, 0.8) + line('M398 221 C412 213 428 206 445 202', '#86625a', 1.4, 0.8)
    + line('M358 210 C355 215 355 221 357 226', SKIN.line, 1.3, 0.5)
    // la petite marque du front : trois langues de feu
    + `<g transform="translate(375 207) scale(0.85) translate(-375 -207)">` + shape('M375 195 C379 200 382 205 382 209 C382 214 379 217 375 217 C371 217 368 214 368 209 C368 205 371 200 375 195 Z', '#6c1f30')
    + shape('M375 203 C376 206 377 208 377 210 C377 212 376 213 375 213 C374 211 374 207 375 203 Z', '#d0465a', 0.9)
    + `<path d="M363 204 C366 207 368 211 368 214 C368 216 366 218 364 218 C362 218 360 216 360 213 C360 210 361 207 363 204 Z" fill="#6c1f30" transform="rotate(-28 364 213)"/>`
    + `<path d="M387 204 C389 207 390 210 390 213 C390 216 388 218 386 218 C384 218 382 216 382 214 C382 211 384 207 387 204 Z" fill="#6c1f30" transform="rotate(28 386 213)"/>` + `</g>`
    // le nez
    + oval(374, 267, 4.4, 2.8, '#e58e7f', 0.95) + line('M383 256 C388 261 389 266 385 271', SKIN.line, 1.5, 0.55)
    // la bouche grande ouverte : rire mauvais, crocs
    + `<g class="a-mouth"><clipPath id="c-mouth"><path id="s-mouth" d="M331 277 C346 280 372 281 397 277 C396 289 390 300 380 306 C370 312 352 311 342 303 C335 296 332 287 331 277 Z"/></clipPath>`
    + `<use href="#s-mouth" fill="url(#g-mouth)"/>`
    + `<g clip-path="url(#c-mouth)">`
    + oval(362, 308, 20, 9, '#ef7672') + shape('M350 304 C356 300 368 300 374 304 C368 302 356 302 350 304 Z', '#ffb0a8', 0.85)
    + shape('M328 274 L400 274 L398 281 C396 285 393 289 390 293 L387 286 C378 288 368 288 358 288 C352 288 348 287 344 286 L340 293 C337 289 334 285 332 281 Z', '#fff')
    + line('M345 286 C352 288 372 289 386 287', '#c9c8de', 1.4, 0.8)
    + `</g><use href="#s-mouth" fill="none" stroke="#3a0c18" stroke-width="2.4"/></g>` },
  // le dessus de la chevelure et la frange : ivoire presque blanc en haut à droite, gris chaud dans l'ombre à gauche
  { id: 'hairF', cls: 'a-bob', d: S.hairF,
    shadow: [{ on: ['face', 'earS'], dx: -3, dy: 7, color: SH.skin, o: 0.4 }, { on: ['hairB', 'earL', 'earR'], dx: -2, dy: 3, color: SH.hair, o: 0.14 }],
    body: use('hairF', 'url(#g-hairF)') + clip('hairF',
      // la lumière bleue de la flamme
      `<rect x="430" y="110" width="70" height="130" fill="url(#g-blue)"/>`
      // l'ombre douce, gris chaud, du côté gauche et du bas de la tête
      + oval(222, 238, 38, 78, 'url(#g-hairL)', 1, 8)
      // la lumière du dessus de la tête, venue d'en haut à droite : deux grandes lueurs fondues, pas une bande
      + oval(374, 100, 62, 22, 'url(#g-sheen)', 1, 14) + oval(298, 114, 34, 14, 'url(#g-sheen)', 0.7, -20)
      // la raie : la frange part de l'épi vers la gauche, la mèche de droite vers la droite
      + shape(taper(386, 110, 397, 130, 402, 150, 3.5), HAIR.shade, 0.7)
      // le dessous de la frange s'assombrit doucement vers les pointes
      + `<path d="M270 186 L320 168 L372 146 L404 128 L414 196 L270 236 Z" fill="url(#g-fringeSh)"/>`
      // une lueur douce sur chaque grande mèche de la frange
      + oval(371, 150, 7, 22, 'url(#g-sheen)', 0.8, 32) + oval(339, 163, 8, 24, 'url(#g-sheen)', 0.75, 40)
      // la mèche de droite : son côté plus sombre contre le visage, sa lumière dehors
      + shape(taper(404, 154, 430, 182, 447, 214, 4.5), HAIR.shade, 0.55)
      + oval(462, 174, 8, 30, 'url(#g-sheen)', 0.8, -28)
      // la mèche devant la joue gauche : une lumière douce
      + oval(268, 254, 6, 26, 'url(#g-sheen)', 0.7, -12)) },
];


// ---------- la vie ----------
// Au repos (propriétés `translate`, `rotate`, `scale`) : le buste respire, la tête et les bras suivent, les oreilles
// frémissent de temps en temps, la queue balaie, la flamme vacille, les yeux clignent.
// L'attaque (classe `atk` sur le <svg>, 0,75 s) passe par la propriété `transform` : elle s'ajoute au repos sans le couper,
// et revient à zéro à la fin, donc le passage de l'un à l'autre ne se voit pas. Elle ramène la main en arrière (la flamme se
// ramasse), pousse la paume vers l'avant : la flamme part en boule de feu à traîne, puis une nouvelle renaît dans la main.
const WAIST = [330, 440], SHOULDER = [410, 352], EAR_L = [266, 120], EAR_R = [420, 112], TAIL = [226, 482], FLAME = [549, 326];
const rad_ = (d) => (d * Math.PI) / 180;
const rot = ([x, y], a) => [x * Math.cos(rad_(a)) - y * Math.sin(rad_(a)), x * Math.sin(rad_(a)) + y * Math.cos(rad_(a))];
/** Le haut du corps penche de `lean` degrés autour de la taille ; le morceau (pivot `o`) bouge en plus de `t` et tourne de `turn`. */
function bend(o, lean, t = [0, 0], turn = 0) {
  const [vx, vy] = rot([o[0] + t[0] - WAIST[0], o[1] + t[1] - WAIST[1]], lean);
  return `translate(${n(vx + WAIST[0] - o[0])}px,${n(vy + WAIST[1] - o[1])}px) rotate(${n(lean + turn)}deg)`;
}
// les temps forts de l'attaque : élan (30 %), frappe (45 %), tenue (58 %), retour
const AT = [0, 30, 45, 58, 100];
const LEAN = [0, -3, 3.5, 3, 0];
const kf = (name, f) => `@keyframes ${name}{${AT.map((p, i) => `${p}%{transform:${f(i)}}`).join('')}}`;
const ARM = { t: [[0, 0], [-6, 2], [18, -2], [16, -2], [0, 0]], turn: [0, -14, 3, 2, 0] };
const style = [
  '.a-chest,.a-bob{transform-origin:330px 440px}',
  '.a-chest{animation:breath 3.2s ease-in-out infinite alternate}',
  '.a-bob{animation:bob 3.2s ease-in-out infinite alternate}',
  '.a-earL{transform-origin:266px 120px;animation:bob 3.2s ease-in-out infinite alternate,earL 5.4s linear infinite}',
  '.a-earR{transform-origin:420px 112px;animation:bob 3.2s ease-in-out infinite alternate,earR 6.3s linear -2.2s infinite}',
  '.a-arm{transform-origin:410px 352px;animation:bob 3.2s ease-in-out infinite alternate,sway 2.6s ease-in-out infinite alternate}',
  '.a-tail{transform-origin:226px 482px;animation:tail 3.8s ease-in-out infinite alternate}',
  '.a-flap{transform-origin:456px 488px;animation:flap 2.4s ease-in-out infinite alternate}',
  '.a-flare,.a-fl,.a-fl2{transform-origin:549px 326px}',
  '.a-shot{transform-origin:576px 290px}',
  '.a-fl{animation:fl .8s ease-in-out infinite alternate}',
  '.a-fl2{animation:fl2 .55s ease-in-out infinite alternate}',
  '.a-core{transform-origin:548px 303px;animation:core .7s ease-in-out infinite alternate}',
  '.a-halo{transform-origin:550px 268px;animation:halo 1.1s ease-in-out infinite alternate}',
  '.a-sp{animation:sp 1.3s ease-in-out infinite alternate}',
  '.a-blink{animation:blink 4.6s linear infinite}',
  '.a-mouth{transform-origin:364px 279px}',
  '@keyframes breath{from{scale:1 1}to{scale:1 1.012}}',
  '@keyframes bob{from{translate:0 0}to{translate:0 -1.5px}}',
  '@keyframes earL{0%,70%{rotate:0deg}74%{rotate:-7deg}78%{rotate:1deg}81%{rotate:-4deg}86%,100%{rotate:0deg}}',
  '@keyframes earR{0%,72%{rotate:0deg}76%{rotate:7deg}80%{rotate:-1deg}83%{rotate:4deg}88%,100%{rotate:0deg}}',
  '@keyframes sway{from{rotate:-1deg}to{rotate:1.4deg}}',
  '@keyframes tail{from{rotate:-1.8deg}to{rotate:2.4deg}}',
  '@keyframes flap{from{rotate:-2deg}to{rotate:3deg}}',
  '@keyframes fl{from{transform:scale(1,1) skewX(0deg)}to{transform:scale(.96,1.06) skewX(-2.5deg)}}',
  '@keyframes fl2{from{transform:scale(1,1) skewX(1deg)}to{transform:scale(1.05,.94) skewX(-1.5deg)}}',
  '@keyframes core{from{transform:scale(.92);opacity:.85}to{transform:scale(1.06);opacity:1}}',
  '@keyframes halo{from{transform:scale(.94);opacity:.8}to{transform:scale(1.05);opacity:1}}',
  '@keyframes sp{from{transform:translate(0,3px);opacity:.55}to{transform:translate(0,-5px);opacity:1}}',
  '@keyframes blink{0%,93%{opacity:0}94.5%,97%{opacity:1}98.5%,100%{opacity:0}}',
  // --- l'attaque : elle ramène la flamme en arrière, puis la projette vers l'avant ; la queue fouette ---
  '.atk .a-chest{animation:breath 3.2s ease-in-out infinite alternate,lean .75s ease-in-out}',
  '.atk .a-bob{animation:bob 3.2s ease-in-out infinite alternate,lean .75s ease-in-out}',
  '.atk .a-earL{animation:bob 3.2s ease-in-out infinite alternate,earL 5.4s linear infinite,earLa .75s ease-in-out}',
  '.atk .a-earR{animation:bob 3.2s ease-in-out infinite alternate,earR 6.3s linear -2.2s infinite,earRa .75s ease-in-out}',
  '.atk .a-arm{animation:bob 3.2s ease-in-out infinite alternate,sway 2.6s ease-in-out infinite alternate,arm .75s ease-in-out}',
  '.atk .a-tail{animation:tail 3.8s ease-in-out infinite alternate,whip .75s ease-in-out}',
  '.atk .a-flare{animation:flare .75s ease-in-out}',
  '.atk .a-shot{animation:shot .75s ease-out}',
  '.atk .a-mouth{animation:roar .75s ease-in-out}',
  kf('lean', (i) => `rotate(${LEAN[i]}deg)`),
  kf('earLa', (i) => bend(EAR_L, LEAN[i], [0, 0], [0, -6, -12, -9, 0][i])),
  kf('earRa', (i) => bend(EAR_R, LEAN[i], [0, 0], [0, 6, 12, 9, 0][i])),
  kf('arm', (i) => bend(SHOULDER, LEAN[i], ARM.t[i], ARM.turn[i])),
  kf('whip', (i) => `rotate(${[0, 7, -8, -5, 0][i]}deg)`),
  '@keyframes flare{0%{transform:scale(1);opacity:1}30%{transform:scale(.85);opacity:1}38%{transform:scale(1.3);opacity:1}43%,70%{transform:scale(.05);opacity:0}90%{transform:scale(1.08);opacity:1}100%{transform:scale(1);opacity:1}}',
  '@keyframes shot{0%,36%{opacity:0;transform:translate(-16px,6px) scale(.8)}41%{opacity:1;transform:translate(0,0) scale(1.4)}62%{opacity:1;transform:translate(60px,-6px) scale(1.6,1.4)}74%,100%{opacity:0;transform:translate(84px,-8px) scale(1.7,1.3)}}',
  kf('roar', (i) => `scale(${[1, 1, 1.07, 1.05, 1][i]},${[1, 0.92, 1.28, 1.2, 1][i]})`),
].join('');

const HAND = ['fistL', 'fk1', 'fk2', 'fk3', 'fk4', 'thumbL'];
for (const p of parts) {
  if (!HAND.includes(p.id)) continue;
  p.body = `<g transform="rotate(${HAND_ROT.join(' ')})">${p.body.split(`#s-${p.id}"`).join(`#s0-${p.id}"`).split(`#c-${p.id})`).join(`#c0-${p.id})`)}</g>`;
}
const handDefs = HAND.map((k) => `<path id="s0-${k}" d="${S0[k]}"/><clipPath id="c0-${k}"><use href="#s0-${k}"/></clipPath>`).join('');

module.exports = { id: 'knights-11', w: W, h: H, pad: 110, foot: [329, 566], svg: (anime = true) => figure({ w: W, h: H, pad: 110, defs: defs + handDefs, style, parts, anime }) };
