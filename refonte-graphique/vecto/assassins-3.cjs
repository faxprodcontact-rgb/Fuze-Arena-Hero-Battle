// Sable (assassins-3), héroïne Légendaire : redessinée par le code d'après le dessin d'origine, dans le même cadre (532 × 566,
// mêmes proportions, même pose) : une déesse lionne tournée vers la droite ; grand disque solaire doré derrière la tête,
// cobra d'or au front, coiffe sombre qui tombe sur les épaules, yeux d'ambre fardés, museau clair ; large collier
// turquoise, robe blanche à ceinture d'or, cape pourpre ; elle tient en éventail trois lames d'or en forme de feuille.
// DÉCALQUÉE : silhouette exacte (master) ; les aplats de chaque matière relevés sur l'original et lissés par vote
// (outils/couleurs.py --vote → couleurs/assassins-3.json) ; disque solaire mesuré (cercle ajusté sur le bord) ; tête et
// bras aux lames découpés dans la silhouette (outils/decoupe.py) ; visage lu sur un gros plan quadrillé.
// La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');
const { sm, rib, glint, cel } = require('./formes.cjs');

const W = 532, H = 566, PAD = 44;
const SIL = require('./silhouettes/assassins-3.json');
const MAT = require('./couleurs/assassins-3.json');

// ---------- chaque matière, peinte en aplats nets (ombre en bas à gauche, liseré clair en haut à droite) ----------
const TONES = {
  fauve: { hi: '#ffd890', base: '#e0a04a', sh: '#b8742c', deep: '#8a5020' },
  criniere: { hi: '#a87a54', base: '#6e4630', sh: '#4e2e1e', deep: '#2e1a10' },
  or: { hi: '#fffad0', base: '#f8d050', sh: '#d09a28', deep: '#9a6a18' },
  blanc: { hi: '#ffffff', base: '#f4ecdc', sh: '#d4c4a8', deep: '#a89478' },
  turquoise: { hi: '#8ae8e8', base: '#3aa8b4', sh: '#22707e', deep: '#144650' },
  pourpre: { hi: '#c84a5a', base: '#7e2434', sh: '#561624', deep: '#340c16' },
  sombre: { hi: '#4a3028', base: '#24140e', sh: '#140a06', deep: '#0a0402' },
};
const PAINT_SRC = ['criniere', 'pourpre', 'fauve', 'blanc', 'turquoise', 'or', 'sombre'].map((k) => (MAT[k] && MAT[k].d ? cel(MAT[k].d, TONES[k], 4, 1.4) : '')).join('');
const PAINT = '<use href="#p-mat"/>';

// ---------- les formes relevées sur l'original ----------
const BODY = sm('263,19 258,19 255,17 236,17 229,19 222,27 203,35 185,55 177,71 174,91 176,109 185,127 179,128 172,125 156,125 145,130 140,135 134,148 133,166 136,177 144,191 128,217 119,228 119,231 109,242 109,248 103,261 103,280 112,299 114,300 115,298 125,309 105,320 100,325 88,332 80,340 81,344 85,342 88,344 81,348 76,355 32,398 18,417 10,435 5,456 6,473 9,479 12,478 17,465 27,450 44,445 53,445 61,449 63,456 72,463 80,466 95,466 97,468 97,470 93,473 81,474 75,473 67,469 59,461 57,462 59,469 59,486 63,493 75,506 84,510 74,502 71,498 72,497 78,499 103,499 96,511 93,513 87,527 77,538 74,544 73,556 76,558 81,558 84,560 95,559 101,562 111,560 122,562 130,559 135,561 147,561 152,557 162,557 165,553 164,540 160,535 163,531 162,528 180,505 187,504 189,505 189,511 179,535 180,541 224,546 240,546 244,544 269,541 270,549 274,552 299,552 302,554 331,558 334,556 347,558 351,556 362,556 369,553 369,545 365,536 361,532 348,528 337,521 334,506 335,489 332,484 332,473 320,449 308,434 293,420 288,412 288,398 285,393 288,387 295,382 321,400 341,402 348,360 341,359 337,356 331,357 321,343 325,339 316,326 319,325 326,329 336,330 357,326 367,320 381,303 388,300 397,289 408,281 411,275 410,252 414,245 414,239 408,222 391,208 388,201 373,188 368,177 352,163 353,151 351,142 343,126 335,119 327,120 318,125 315,123 320,109 321,88 318,73 309,54 295,38 279,30 272,23');
const ARM = sm('514,271 508,272 503,276 472,291 450,308 431,326 430,322 456,270 459,255 462,250 462,244 454,248 430,274 418,293 400,330 396,332 387,356 385,358 375,357 366,364 363,362 354,363 348,360 341,402 347,402 349,404 342,411 348,427 354,423 362,422 364,415 367,412 375,413 378,411 383,411 397,403 400,396 405,392 408,384 412,381 420,384 429,379 438,379 446,375 458,374 464,371 472,372 481,366 486,366 491,361 528,338 527,336 521,336 516,338 500,339 493,342 483,343 478,346 470,345 458,352 448,354 439,359 437,358 441,355 441,351 446,345 451,343 457,336 471,329 471,325 488,309 494,300 504,290 513,276');
const HEAD = sm('413,234 408,222 391,208 388,201 373,188 368,177 352,163 353,151 351,142 343,126 335,119 327,120 318,126 307,128 298,120 287,115 278,128 267,137 240,138 212,141 196,131 180,126 165,125 145,130 140,135 134,148 133,166 136,177 144,189 133,207 140,250 170,288 205,300 249,308 300,310 340,310 377,305 381,303 388,300 397,289 408,281 411,273 410,252 414,245');
const SUN = [247.4, 91.8, 72.3];
const SUN_D = `M${n(SUN[0] - SUN[2] - 2)} ${SUN[1]}a${SUN[2] + 2} ${SUN[2] + 2} 0 1 0 ${n(2 * SUN[2] + 4)} 0a${SUN[2] + 2} ${SUN[2] + 2} 0 1 0 ${n(-2 * SUN[2] - 4)} 0Z`;
// les trois lames (de la garde à la pointe) : un filet de lumière sur chacune
const BLADES = [[[392, 362, 6], [410, 330, 12], [440, 282, 12], [461, 246, 0]], [[402, 366, 6], [430, 340, 13], [480, 297, 12], [512, 272, 0]],
  [[410, 374, 6], [440, 362, 13], [490, 350, 11], [526, 338, 0]], [[396, 386, 8], [372, 404, 7], [346, 424, 0]]];

// le bas du corps, redessiné pièce par pièce (les aplats automatiques y sont trop morcelés), lu sur un gros plan
const LOWER = sm('0,296! 340,296! 345,566! 0,566!');
const CAPE = sm('126,298 100,312 70,340 45,380 30,420 27,447 45,459 75,463 100,458 132,452 150,420 152,330 142,305');
const CAPE_EDGE = sm('126,298 100,312 70,340 45,380 30,420 27,447 36,452 40,424 54,386 78,348 104,320 128,306');
const TAIL = [[134, 494, 12], [104, 489, 13], [78, 481, 11], [62, 472, 8], [56, 461, 0]];
const SKIRT = sm('200,414 288,412 292,470 290,520 270,540 205,542 196,500 198,460');
const APRON = sm('196,484! 206,476! 214,487! 222,475! 232,487! 242,475! 252,487! 262,475! 272,487! 282,477! 291,485! 290,520 280,540 205,542 196,520');
const BELT = sm('198,396 244,393 288,394 290,414 244,417 198,416');
const BODICE = sm('196,352 222,341 246,349 270,341 292,352 292,392 246,398 198,394');
const COLLAR = sm('132,310 170,305 210,316 245,320 280,314 312,310 318,326 300,348 270,362 246,368 220,362 190,350 160,334 138,322');
const COLLAR_IN = sm('150,318 180,316 212,326 245,330 280,324 306,322 296,340 270,352 246,357 222,352 194,341 166,328');
const ARM_L = sm('100,338 122,328 146,332 152,352 150,384 154,400 150,430 140,442 116,444 96,440 86,424 92,402 100,388 98,360');
const lowerBody = cel(LOWER, TONES.fauve, 5, 2)
  // les muscles des jambes et du bras droit, des creux doux ; les orteils
  + [[[140, 420], [130, 460], [140, 500]], [[180, 430], [190, 470], [184, 505]], [[300, 430], [312, 470], [306, 505]], [[306, 330], [318, 360], [312, 392]]].map((g) => glint(g.map(([x, y], i) => [x, y, i === 1 ? 4 : 0]), TONES.fauve.sh, 0.6)).join('')
  + [[104, 530], [124, 534], [144, 534], [304, 528], [322, 530]].map(([x, y]) => glint([[x, y, 0], [x + 1, y + 10, 2], [x, y + 20, 0]], TONES.fauve.deep, 0.6)).join('')
  + [[92, 545], [113, 549], [134, 550], [155, 547], [296, 543], [315, 545], [334, 541]].map(([x, y]) => oval(x, y, 6, 3, '#fff2d8', 0.8)).join('')
  // la cape pourpre et son ourlet rouge, la queue
  + cel(CAPE, TONES.pourpre, 6, 2) + cel(CAPE_EDGE, { hi: '#ff8070', base: '#d84a3a', sh: '#a83028' }, 3, 1.4)
  + `<path d="${rib(TAIL)}" fill="${TONES.fauve.base}"/>` + glint(TAIL.map(([x, y, w], i) => [x, y - w * 0.25, i === 0 || i === TAIL.length - 1 ? 0 : w * 0.25]), TONES.fauve.hi, 0.8)
  + glint(TAIL.map(([x, y, w], i) => [x, y + w * 0.3, i === 0 || i === TAIL.length - 1 ? 0 : w * 0.22]), TONES.fauve.sh, 0.8)
  // la robe blanche, le tablier d'or à pointes et son ornement, la ceinture d'or et son joyau
  + cel(SKIRT, TONES.blanc, 5, 2) + glint([[214, 420, 0], [222, 450, 3], [218, 478, 0]], TONES.blanc.sh, 0.6) + glint([[270, 420, 0], [276, 450, 3], [272, 478, 0]], TONES.blanc.sh, 0.5)
  + cel(APRON, TONES.or, 5, 2) + cel(sm('220,505 233,497 247,505 249,523 234,531 220,523'), { hi: '#e06048', base: '#8a1a18', sh: '#5a0c0c' }, 2.4, 1.2) + dot(234, 514, 3.2, '#f8d050')
  + cel(BELT, TONES.or, 3, 1.6) + oval(244, 405, 7, 6, '#2aa0b0') + dot(246, 403, 2, '#c8ffff', 0.9)
  // le haut blanc, le collier d'or et de turquoise (une rangée de perles d'or)
  + cel(BODICE, TONES.blanc, 4, 2) + glint([[244, 356, 0], [246, 372, 2], [245, 390, 0]], TONES.blanc.sh, 0.7)
  + cel(COLLAR, TONES.or, 4, 2) + cel(COLLAR_IN, TONES.turquoise, 3, 1.6)
  + [[160, 324], [184, 334], [208, 342], [232, 346], [258, 345], [282, 338], [300, 330]].map(([x, y]) => dot(x, y, 3, '#f8d050') + dot(x + 0.8, y - 0.8, 1, '#ffffff', 0.9)).join('')
  // le bras gauche (fourrure), son bracelet d'or, les doigts du poing
  + cel(ARM_L, TONES.fauve, 5, 2.4) + cel(sm('102,386 126,383 148,384 150,397 126,399 104,400'), TONES.or, 3, 1.4)
  + [[106, 410], [118, 408], [130, 410], [142, 412]].map(([x, y]) => glint([[x, y, 0], [x, y + 12, 1.8], [x - 1, y + 26, 0]], TONES.fauve.deep, 0.7)).join('')
  + glint([[112, 334, 0], [140, 340, 3], [150, 370, 0]], TONES.fauve.hi, 0.6);

// ---------- dégradés ----------
const defs = [
  rad('g-sun', 0.6, 0.32, 0.8, [[0, '#fff0b0'], [0.3, '#ffb848'], [0.7, '#f27a22'], [1, '#c85414']], false),
  lin('g-blade', 0, 0, 1, 1, [[0, '#fff6c0'], [0.4, '#f8d050'], [1, '#c88a20']], false),
  rad('g-iris', 0.45, 0.4, 0.75, [[0, '#fff0a0'], [0.4, '#e8a030'], [1, '#8a4a10']], false),
  `<g id="p-mat">${PAINT_SRC}</g>`,
].join('');

// ---------- le visage, net par-dessus les aplats ----------
const FACE =
  // le museau clair, puis le cobra d'or au front et sa gemme rouge
  cel(sm('312,248 340,240 372,246 404,258 410,272 394,286 360,292 330,288 312,274'), { hi: '#fff4d8', base: '#f6d8a4', sh: '#dcb478' }, 3, 1.6)
  + cel(sm('279,130 287,114 299,118 309,130 313,150 305,168 296,171 288,161 282,146'), TONES.or, 3, 1.6)
  + glint([[290, 120, 0], [302, 134, 1.8], [306, 152, 0]], '#ffffff', 0.8) + dot(298, 156, 4.4, '#c02818') + dot(299.4, 154.6, 1.4, '#ffd0c0') +
  // l'œil gauche (grand, fardé) : blanc, iris d'ambre, pupille, reflet ; le trait de fard qui s'étire en aile
  shape(sm('238,212 252,203 272,201 292,206 294,214 286,226 270,231 252,228 241,220'), '#fffaf0')
  + `<clipPath id="c-eyeS"><path d="${sm('238,212 252,203 272,201 292,206 294,214 286,226 270,231 252,228 241,220')}"/></clipPath>`
  + `<g clip-path="url(#c-eyeS)">${dot(271, 217, 11.5, 'url(#g-iris)')}${dot(272, 217, 5, '#1a0a04')}${dot(267, 212, 2.6, '#ffffff')}</g>`
  + shape(sm('226,213! 240,204 256,199 276,198 296,204 296,209 276,204 256,205 242,210'), '#1a0c08')
  + shape(sm('240,222 256,229 272,231 286,227 284,230 270,234 254,232'), '#3a1e10', 0.8)
  // l'œil droit (de trois quarts), plus petit
  + shape(sm('340,212 350,206 361,208 362,217 354,223 344,220'), '#fffaf0') + dot(352, 215, 5.6, 'url(#g-iris)') + dot(353, 215, 2.6, '#1a0a04') + dot(350.5, 212.5, 1.3, '#ffffff')
  + shape(sm('337,211! 348,204 362,205 364,209 350,208'), '#1a0c08')
  + `<g class="a-blink" opacity="0">${shape(sm('236,212 252,201 272,199 294,205 296,215 286,228 270,233 252,230 239,221'), TONES.fauve.base)}${shape(sm('338,212 350,204 363,207 364,218 354,225 342,221'), TONES.fauve.base)}`
  + `${line('M238 218 Q266 230 294 214', '#1a0c08', 3)}${line('M339 216 Q352 222 363 214', '#1a0c08', 2.4)}</g>`
  // les sourcils sombres, froncés vers le nez
  + cel(sm('230,190 250,182 274,184 296,196 297,203 274,194 250,192 232,198'), TONES.criniere, 3, 1.6)
  + cel(sm('342,196 354,189 366,191 366,198 354,197 344,203'), TONES.criniere, 2.4, 1.4)
  // le nez de lionne, les points des moustaches, la bouche en coin
  + cel(sm('372,229 388,226 400,232 399,243 388,248 376,244'), { hi: '#c8906a', base: '#8a4a24', sh: '#5a2c12' }, 2.4, 1.4)
  + [[318, 254], [326, 258], [322, 264], [332, 262], [316, 268]].map(([x, y]) => dot(x, y, 1.8, '#4a2410', 0.8)).join('')
  + line('M322 284 Q350 292 388 280', '#2a1208', 2.6);

// ---------- les morceaux ----------
const sh = (on, dx, dy, color = '#1a0a0c', o = 0.4) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'body', cls: 'a-body', d: BODY, body: use('body', TONES.fauve.base) + clip('body', PAINT + lowerBody) },
  // le disque solaire, derrière la tête : rayonnement doux, cercle doré, liseré
  { id: 'sun', cls: 'a-sun', d: SUN_D, shadow: [sh(['body'], -3, 5)], body: `<circle cx="${SUN[0]}" cy="${SUN[1]}" r="${SUN[2] + 3}" fill="#f2c040"/>`
    + `<circle cx="${SUN[0]}" cy="${SUN[1]}" r="${SUN[2] - 3}" fill="url(#g-sun)"/>`
    + `<circle cx="${SUN[0]}" cy="${SUN[1]}" r="${SUN[2] - 10}" fill="none" stroke="#fff4b0" stroke-width="3" opacity="0.55"/>`
    + glint([[200, 40, 0], [246, 25, 4], [296, 40, 0]], '#ffffff', 0.7) },
  { id: 'head', cls: 'a-head', d: HEAD, shadow: [sh(['body', 'sun'], -3, 6)], body: use('head', TONES.fauve.base) + clip('head', PAINT + FACE) },
  { id: 'arm', cls: 'a-arm', d: ARM, shadow: [sh(['body', 'head'], -3, 5)], body: use('arm', TONES.or.base) + clip('arm', PAINT
    // les lames nettes : une feuille d'or, sa moitié à l'ombre, l'arête claire
    + BLADES.map((b) => `<path d="${rib(b)}" transform="translate(-2 3)" fill="#3a1c08" opacity="0.4"/>` + shape(rib(b), 'url(#g-blade)')
      + shape(rib(b.map(([x, y, w]) => [x - w * 0.18, y + w * 0.22, w * 0.5])), '#c08a20', 0.75)
      + glint(b.map(([x, y, w], i) => [x + w * 0.12, y - w * 0.15, i === 0 || i === b.length - 1 ? 0 : 1.6]), '#ffffff', 0.85)).join('')
    // le poing qui serre les lames
    + cel(sm('376,360 392,352 408,358 414,374 408,392 392,398 378,392 370,376'), TONES.fauve, 3, 1.6)
    + [[384, 362, 382, 392], [394, 360, 393, 394], [404, 364, 403, 390]].map(([x0, y0, x1, y1]) => glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 1.6], [x1, y1, 0]], TONES.fauve.deep, 0.7)).join('')) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : elle respire, la tête hoche, le disque solaire palpite, les lames oscillent, elle cligne. Attaque (classe
// « atk », 0,75 s) : elle arme son bras puis lance d'un geste vif les lames vers l'avant en bondissant ; retour en garde.
const PIV = { body: [240, 560], sun: [247, 92], head: [300, 300], arm: [360, 390] };
const IDLE = {
  'a-body': ['body', 'body 2s ease-in-out infinite alternate'],
  'a-sun': ['sun', 'sun 2.4s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 2.6s ease-in-out infinite alternate'],
  'a-arm': ['arm', 'arm 1.8s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-root{transform-origin:240px 560px}
.a-blink{animation:blink 4.4s linear infinite}
@keyframes body{from{transform:none}to{transform:translate(0,-2px) scale(1.004,1.008)}}
@keyframes sun{from{transform:scale(1)}to{transform:scale(1.03)}}
@keyframes head{from{transform:none}to{transform:rotate(-1.4deg) translate(0,-1px)}}
@keyframes arm{from{transform:rotate(-2deg)}to{transform:rotate(2deg)}}
@keyframes blink{0%,93%{opacity:0}94.5%,97%{opacity:1}98.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-head', 'head-atk')}${atk('a-arm', 'arm-atk')}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-8px,2px) rotate(-2deg)}48%{transform:translate(20px,-6px) rotate(2deg)}62%{transform:translate(16px,-2px)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}30%{transform:rotate(-2deg)}48%{transform:rotate(2deg)}100%{transform:none}}
@keyframes arm-atk{0%{transform:none}30%{transform:rotate(-10deg)}48%{transform:rotate(9deg) translate(6px,0)}64%{transform:rotate(5deg)}100%{transform:none}}
`.replace(/\n/g, '');

function svg(anime = true) {
  const s = figure({ master: SIL, w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'assassins-3', w: W, h: H, pad: PAD, foot: [240, 560], svg };
