// Eldra (mages-8), héroïne Légendaire : redessinée par le code d'après le dessin d'origine, dans le même cadre (580 × 619,
// mêmes proportions, même pose) : une guerrière singe en garde basse, tournée vers la droite ; deux longues plumes
// brunes qui partent du crâne en arcs, bandeau d'or à médaillon, fourrure brune, grand visage clair au museau rond,
// sourcils froncés, yeux bruns, petit sourire en coin ; cape et tenue rouges à garnitures d'or, ceinture sombre ;
// elle tient en travers un long bâton d'or ; la queue s'enroule derrière elle, bottes sombres à revers de fourrure.
// DÉCALQUÉE : silhouette exacte (master) ; les aplats de chaque matière, clairs et ombres, relevés sur l'original
// (outils/couleurs.py → couleurs/mages-8.json et mages-8-ombres.json) ; plumes, tête et queue découpées dans la
// silhouette (outils/decoupe.py) ; bâton mesuré colonne par colonne ; visage et poings lus sur gros plans quadrillés.
// La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');
const { sm, rib, glint, cel } = require('./formes.cjs');

const W = 580, H = 619, PAD = 44;
const SIL = require('./silhouettes/mages-8.json');
const MAT = require('./couleurs/mages-8.json');
const SHD = require('./couleurs/mages-8-ombres.json');

// ---------- chaque matière, peinte en aplats nets (ombre en bas à gauche, liseré clair en haut à droite) ----------
const TONES = {
  fourrure: { hi: '#c89070', base: '#8e5a40', sh: '#6a3e2a', deep: '#4a2a1c' },
  peau: { hi: '#fff0dc', base: '#ffdcb0', sh: '#eeb888', deep: '#d4956a' },
  rouge: { hi: '#f2766a', base: '#d2443a', sh: '#9a2a26', deep: '#661a18' },
  or: { hi: '#fff0a0', base: '#f2b440', sh: '#c07c22', deep: '#80501a' },
  sombre: { hi: '#5a4044', base: '#2e1e22', sh: '#1a1014', deep: '#0e080a' },
  blanc: { hi: '#ffffff', base: '#e4e0ea', sh: '#b8b0c4', deep: '#8a8098' },
};
// les ombres et reflets de l'original, chacun gardé dans sa matière
const SHADE = [['fourO', 'fourrure', '#5a3424', 0.85], ['peauO', 'peau', '#e8ac7e', 0.75], ['rougeO', 'rouge', '#7a2020', 0.85], ['orO', 'or', '#a8661e', 0.8],
  ['lilas', 'fourrure', '#c8b4d8', 0.7]];
const mclip = Object.keys(TONES).filter((k) => MAT[k]).map((k) => `<clipPath id="m-${k}"><path d="${MAT[k].d}" clip-rule="evenodd"/></clipPath>`).join('');
const paint = ['fourrure', 'rouge', 'sombre', 'peau', 'or', 'blanc'].map((k) => (MAT[k] && MAT[k].d ? cel(MAT[k].d, TONES[k], 6, 3) : '')).join('')
  + SHADE.map(([k, m, c, o]) => (SHD[k] && SHD[k].d ? `<g clip-path="url(#m-${m})"><path d="${SHD[k].d}" fill="${c}" opacity="${o}" fill-rule="evenodd"/></g>` : '')).join('');

// ---------- les formes relevées sur l'original ----------
const PLUMES = sm('31,138 32,142 37,142 48,133 82,113 114,101 151,95 188,97 221,105 249,120 275,144 292,168 265,178 299,178 300,200 372,200 373,178 396,178 371,168 373,150 368,115 362,98 344,66 320,41 310,33 273,14 242,7 208,6 183,9 163,16 160,22 164,26 188,23 216,23 240,26 263,33 295,52 318,77 333,105 340,131 340,165 335,163 325,164 314,144 299,124 283,108 267,96 253,88 229,78 188,71 155,71 133,74 92,87 74,96 53,111 37,127');
// le corps : la silhouette sans les plumes ni la queue (elles bougent seules)
const BODY = sm('26,400 26,406 31,406 40,401 55,397 70,397 90,402 107,411 128,439 111,457 106,469 102,473 105,470 107,471 112,485 111,486 55,486 56,487 51,490 40,491 27,496 20,496 12,500 6,510 9,533 13,540 19,544 28,545 53,538 57,535 63,535 71,531 84,533 89,530 95,539 116,545 115,549 107,557 104,566 74,589 69,601 69,607 74,611 147,613 153,610 169,611 172,609 194,609 198,604 198,594 187,580 187,576 200,565 199,561 231,544 254,537 261,533 281,537 328,535 340,539 345,543 342,549 343,551 361,549 366,552 379,551 392,558 389,565 397,575 397,580 391,592 391,604 396,608 421,609 427,606 430,608 437,607 440,609 471,610 461,607 455,601 457,599 465,601 473,601 476,599 488,601 498,599 503,602 504,600 511,599 513,597 516,599 516,605 518,606 520,603 520,592 515,582 507,575 497,572 479,561 484,554 484,547 476,540 476,536 473,534 474,515 465,494 450,474 427,451 422,449 416,443 416,440 419,436 429,437 436,433 449,434 459,429 465,422 466,416 470,411 469,400 480,394 486,396 495,391 498,393 505,393 511,387 520,385 524,381 532,378 538,378 543,374 569,367 574,360 576,351 571,332 567,325 558,317 539,321 526,329 500,337 488,345 488,330 486,328 487,315 485,307 479,301 461,297 450,289 448,275 445,270 445,263 447,260 447,254 445,251 446,239 440,227 439,221 433,215 431,209 425,201 402,181 396,178 372,178 371,200 301,200 300,178 265,178 246,189 225,211 208,245 207,258 195,260 187,264 179,272 174,281 170,296 170,309 172,312 172,317 176,324 190,334 190,336 181,336 176,334 138,334 98,342 70,355 55,365 36,383');
const HEAD = sm('170,296 170,309 174,321 179,327 191,335 216,345 252,363 282,383 324,397 371,394 412,379 478,363 519,341 521,330 500,337 489,345 487,330 486,328 487,315 485,307 479,301 461,297 450,289 448,275 445,263 447,254 445,251 446,239 438,219 431,209 425,201 405,183 390,175 366,167 291,165 284,170 256,182 246,189 225,211 208,245 207,258 195,260 187,264 179,272 172,286');
const TAIL = sm('52,416 45,426 43,433 36,439 35,442 37,452 42,457 41,470 50,477 50,480 112,480 106,469 99,476 87,462 83,454 82,446 78,441 77,431 85,413 81,410 68,410 59,412');
// le bâton : son axe mesuré colonne par colonne (il remonte plus raide derrière le poing droit) et sa largeur
const STAFF = [[6, 516, 22], [40, 509, 22], [165, 476, 18], [290, 437, 17], [365, 415, 18], [405, 397, 19], [440, 379, 20], [470, 364, 21], [540, 346, 22], [577, 337, 24]];
const RINGS = [24, 44, 236, 330, 506, 528, 556];
const along = (x) => { for (let i = 1; i < STAFF.length; i++) { const [x0, y0, w0] = STAFF[i - 1], [x1, y1, w1] = STAFF[i]; if (x <= x1) { const f = (x - x0) / (x1 - x0); return [y0 + (y1 - y0) * f, w0 + (w1 - w0) * f, Math.atan2(y1 - y0, x1 - x0)]; } } return STAFF[STAFF.length - 1].slice(1).concat(0); };
const STAFF_D = rib(STAFF);
// les poings, relevés sur gros plan
const FIST_L = sm('177,452 188,446 198,437 215,435 232,443 236,452 233,468 225,477 205,479 185,474 173,465');
const FIST_R = sm('396,394 405,378 425,371 445,372 459,380 461,395 455,409 442,422 418,423 401,413');
// le bandeau d'or (bord haut puis bord bas), le médaillon
// le plastron d'or (sous le bâton), la ceinture sombre et sa boucle, la jupe d'or en trois pans
const CHEST = sm('272,432 300,424 340,420 380,425 392,440 388,463 340,469 290,467 274,456');
const BELT = sm('282,466 340,469 390,463 392,478 340,485 284,482');
const SKIRT = [sm('230,488 284,483 290,524 252,521 229,506'), sm('286,483 336,485 338,527 292,525'), sm('338,485 392,479 412,491 404,512 380,525 340,527')];
const BAND = sm('232,240 250,223 265,219 280,215 295,211 325,210 340,211 400,214 415,219 440,226 472,236! 472,250! 440,240 415,230 400,226 340,223 310,224 295,226 280,229 265,236 250,243 235,250!');

// ---------- dégradés ----------
const defs = [
  lin('g-staff', 0, 0, 0, 1, [[0, '#fff2b0'], [0.3, '#f6c450'], [0.7, '#d89028'], [1, '#8a5418']], false),
  rad('g-iris', 0.45, 0.4, 0.75, [[0, '#f8c070'], [0.4, '#d07a28'], [0.8, '#8a3e12'], [1, '#4a1e08']], false),
  rad('g-medal', 0.62, 0.35, 0.8, [[0, '#fff6c0'], [0.4, '#f6c04a'], [1, '#a86a1c']], false),
  mclip, `<g id="p-mat">${paint}</g>`,
].join('');
const PAINT = '<use href="#p-mat"/>';

// ---------- le visage, net par-dessus les aplats ----------
function eye(cx, cy, r, white, lash, hl) {
  return shape(white, '#ffffff') + `<clipPath id="c-e${cx}"><path d="${white}"/></clipPath><g clip-path="url(#c-e${cx})">`
    + dot(cx, cy, r, 'url(#g-iris)') + dot(cx + 0.5, cy + 0.5, r * 0.45, '#1a0806') + dot(cx + hl[0], cy + hl[1], r * 0.3, '#ffffff') + dot(cx - hl[0] * 0.7, cy + 4, r * 0.13, '#ffffff', 0.9)
    + `<rect x="${cx - 30}" y="${cy - r - 8}" width="60" height="${r}" fill="#3a1a10" opacity="0.2"/></g>` + shape(lash, '#1a0c0a')
    + `<g class="a-blink" opacity="0"><path d="${white}" fill="#ffdcb0" stroke="#ffdcb0" stroke-width="3"/>${line(`M${cx - r - 10} ${cy - 1} Q${cx} ${cy + 6} ${cx + r + 10} ${cy - 3}`, '#1a0c0a', 3)}</g>`;
}
const FACE = eye(323, 293, 12, 'M295 288 C304 278 330 275 343 283 C343 296 336 308 322 309 C306 309 297 300 295 288 Z',
    'M290 290 C302 274 332 270 346 282 L343 287 C330 278 306 280 296 294 Z', [-4, -5])
  + eye(403, 291, 11, 'M385 286 C394 277 416 275 427 281 C427 294 420 304 406 305 C392 305 386 296 385 286 Z',
    'M381 288 C392 272 418 269 431 279 L428 284 C416 276 396 278 387 292 Z', [-4, -5])
  // les gros sourcils bruns froncés (plus bas vers le nez)
  + cel(sm('282,254 300,249 318,250 340,256 357,263 358,272 336,267 318,264 300,264 285,266'), TONES.fourrure, 3, 2)
  + cel(sm('380,262 396,256 412,256 428,262 432,272 414,268 398,270 383,276'), TONES.fourrure, 3, 2)
  // la marque au front sous le médaillon, les petites rides du nez, les joues roses
  + shape('M362 232 L376 232 L369 252 Z', '#8a4a2c', 0.8)
  + glint([[408, 302, 0], [418, 306, 1.6], [428, 303, 0]], '#d88a70', 0.8) + oval(414, 309, 9, 4, '#f4a090', 0.45) + oval(300, 318, 12, 5, '#f4a090', 0.35)
  // le museau : narines, taches sombres au bout
  + oval(449, 323, 6, 3.4, '#3a1a12', 1, 10) + oval(467, 325, 3, 2, '#3a1a12') + dot(486, 318, 1.6, '#5a3020', 0.8) + dot(491, 324, 1.4, '#5a3020', 0.8)
  // le sourire en coin
  + line('M374 356 Q380 361 386 356 Q412 360 444 347', '#2a1410', 2.6) + line('M372 351 Q373 355 375 357', '#2a1410', 2.2);

// ---------- les morceaux ----------
const sh = (on, dx, dy, color = '#1a0a0c', o = 0.4) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'body', cls: 'a-body', d: BODY, body: use('body', TONES.fourrure.base) + clip('body', PAINT
    + cel(CHEST, TONES.or, 5, 2.4) + [[290, 440], [320, 436], [352, 436], [378, 442]].map(([x, y]) => glint([[x - 10, y + 2, 0], [x, y - 2, 2.4], [x + 10, y + 2, 0]], '#fff6c8', 0.7)).join('')
    + SKIRT.map((d, i) => cel(d, { hi: '#fff0a0', base: ['#eaa83a', '#f4bc4c', '#e8a436'][i], sh: '#b87420', deep: '#80501a' }, 5, 2.4)).join('')
    + cel(BELT, TONES.sombre, 3, 1.6) + `<rect x="306" y="469" width="26" height="12" rx="3" fill="#9a9aa6"/>` + `<rect x="310" y="472" width="18" height="6" rx="2" fill="#3a3a44"/>`
    + glint([[300, 471, 0], [340, 472.5, 1.4], [384, 467, 0]], '#7a5a52', 0.8)) },
  { id: 'tail', cls: 'a-tail', d: TAIL, shadow: [sh(['body'], -3, 5)], body: cel(TAIL, TONES.fourrure, 6, 3) + clip('tail', glint([[56, 414, 0], [76, 412, 2.4], [90, 418, 0]], '#e8b090', 0.7)) },
  { id: 'plumes', cls: 'a-plume', d: PLUMES, shadow: [sh(['body'], -3, 5)], body: cel(PLUMES, TONES.fourrure, 6, 3) + clip('plumes',
    // le filet de lumière sur le dessus de chaque plume
    glint([[40, 132, 0], [90, 98, 3], [150, 82, 3.4], [220, 90, 3], [270, 124, 2.4], [300, 160, 0]], '#e8b090', 0.8)
    + glint([[176, 14, 0], [240, 14, 3], [300, 40, 3.4], [340, 84, 3], [360, 130, 2.4], [362, 168, 0]], '#e8b090', 0.8)) },
  { id: 'head', cls: 'a-head', d: HEAD, shadow: [sh(['body', 'plumes'], -3, 6)], body: use('head', TONES.fourrure.base) + clip('head', PAINT
    // le bandeau d'or et son médaillon
    + cel(BAND, TONES.or, 4, 2) + glint([[256, 226, 0], [320, 213, 2], [400, 217, 2], [450, 230, 0]], '#fff6c8', 0.85)
    + dot(363, 215, 15.5, TONES.or.deep) + dot(363.6, 214.4, 13.5, 'url(#g-medal)')
    + line('M363 215 m-1 0 a3 3 0 1 1 4 3 a6 6 0 1 1 -8 -6 a8 8 0 0 1 10 2', '#8a5418', 2.4)
    + FACE) },
  { id: 'staff', cls: 'a-body', d: STAFF_D, shadow: [sh(['body', 'head'], -3, 6)], body: `<path d="${STAFF_D}" fill="url(#g-staff)"/>` + clip('staff',
    // les bagues sombres et les bouts, un long reflet en haut, l'ombre en bas
    RINGS.map((x) => { const [y, w, a] = along(x); return oval(x, y, 3.2, w * 0.62, '#8a5418', 0.85, a * 180 / Math.PI) + oval(x + 4, y - 1, 1.4, w * 0.5, '#fff2b0', 0.8, a * 180 / Math.PI); }).join('')
    + glint(STAFF.map(([x, y, w], i) => [x + 1, y - w * 0.22, i === 0 || i === STAFF.length - 1 ? 0 : w * 0.16]), '#ffffff', 0.7)
    + glint(STAFF.map(([x, y, w], i) => [x - 1, y + w * 0.3, i === 0 || i === STAFF.length - 1 ? 0 : w * 0.2]), '#7a4a14', 0.5)) },
  { id: 'fistL', cls: 'a-body', d: FIST_L, shadow: [sh(['staff', 'body'], -3, 5)], body: cel(FIST_L, TONES.peau, 5, 2.4) + clip('fistL',
    glint([[198, 446, 0], [198.5, 458, 2], [198, 472, 0]], '#c88a60', 0.85) + glint([[215, 444, 0], [215.5, 458, 2], [215, 474, 0]], '#c88a60', 0.85)
    + glint([[201, 446, 0], [201.5, 458, 1], [201, 468, 0]], '#fff6e8', 0.7) + glint([[218, 446, 0], [218.5, 456, 1], [218, 466, 0]], '#fff6e8', 0.7)) },
  { id: 'fistR', cls: 'a-body', d: FIST_R, shadow: [sh(['staff', 'body', 'head'], -3, 5)], body: cel(FIST_R, TONES.fourrure, 5, 2.4) + clip('fistR',
    [418, 432, 445].map((x) => glint([[x, 380, 0], [x + 0.5, 394, 2.2], [x - 1, 410, 0]], TONES.fourrure.deep, 0.85)
      + glint([[x + 3, 381, 0], [x + 3.5, 392, 1.2], [x + 2, 402, 0]], '#c89070', 0.75)).join('')) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : elle respire, la tête hoche, les plumes et la queue ondulent, elle cligne. Attaque (classe « atk », 0,75 s) :
// elle se ramasse puis bondit en avant, bâton pointé ; les plumes et la queue fouettent l'air ; retour à la garde.
const PIV = { plume: [330, 185], tail: [100, 450], body: [300, 600], head: [330, 360] };
const IDLE = {
  'a-plume': ['plume', 'plume 2.4s ease-in-out infinite alternate'],
  'a-tail': ['tail', 'tail 1.8s ease-in-out infinite alternate'],
  'a-body': ['body', 'body 2s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 2.6s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-root{transform-origin:300px 600px}
.a-blink{animation:blink 4.4s linear infinite}
@keyframes plume{from{transform:rotate(-1.6deg)}to{transform:rotate(1.4deg)}}
@keyframes tail{from{transform:rotate(-4deg)}to{transform:rotate(3deg)}}
@keyframes body{from{transform:none}to{transform:translate(0,-2px) scale(1.004,1.008)}}
@keyframes head{from{transform:none}to{transform:rotate(-1.4deg) translate(0,-1px)}}
@keyframes blink{0%,93%{opacity:0}94.5%,97%{opacity:1}98.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-head', 'head-atk')}${atk('a-plume', 'plume-atk')}${atk('a-tail', 'tail-atk')}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-10px,4px) rotate(-3deg)}48%{transform:translate(24px,-8px) rotate(3deg)}62%{transform:translate(20px,-2px) rotate(2deg)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}30%{transform:rotate(-3deg)}48%{transform:rotate(3deg)}100%{transform:none}}
@keyframes plume-atk{0%{transform:none}30%{transform:rotate(4deg)}50%{transform:rotate(-6deg)}72%{transform:rotate(2deg)}100%{transform:none}}
@keyframes tail-atk{0%{transform:none}30%{transform:rotate(8deg)}50%{transform:rotate(-10deg)}100%{transform:none}}
`.replace(/\n/g, '');

function svg(anime = true) {
  const s = figure({ master: SIL, w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'mages-8', w: W, h: H, pad: PAD, foot: [300, 604], svg };
