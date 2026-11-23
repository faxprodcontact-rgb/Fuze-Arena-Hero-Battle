// Le tambour grondeur (parade-5), monstre de la Parade : redessiné par le code d'après le dessin d'origine, dans le même
// cadre (486 × 500, mêmes proportions, même pose) : un gros tambour rouge couché, cerclé de deux bandes dorées cloutées
// et barré d'un zigzag blanc ; sur sa face droite, une peau blanche cerclée de laiton où grimace un visage rouge
// (étoile au front, gros sourcils froncés, yeux jaunes, nez épaté, gueule ouverte aux crocs blancs, barbe blanche) ;
// deux bras sombres levés qui tiennent des baguettes de laiton à boule rouge baguée d'or ; deux pattes trapues à griffes.
// DÉCALQUÉ : silhouette exacte (master), bras et pattes découpés dans la silhouette (outils/decoupe.py), tambour et barbe
// relevés par leur couleur, bandes dorées et zigzag mesurés colonne par colonne, visage lu sur gros plans quadrillés.
// La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');
const { sm, rib, glint, tooth, nest, cel } = require('./formes.cjs');

const W = 486, H = 500, PAD = 44;

// ---------- couleurs ----------
const RED = { hi: '#ff8a72', lite: '#e4483c', base: '#c22e2a', shade: '#8e1a1e', deep: '#5a0c14', rim: '#e87aa0' };
const GOLD = { hi: '#ffe49a', base: '#eea033', sh: '#b0661c', deep: '#7a3e12' };
const CREAM = { hi: '#fffbf2', base: '#f4e8d6', shade: '#d2bea8', deep: '#a8907c' };
const LIMB = { hi: '#aaa2b2', lite: '#746c7c', base: '#4e4856', shade: '#332e3a', deep: '#1c1822' };
const FACE = { hi: '#ff9c88', lite: '#ec5e50', base: '#d8443a', shade: '#a8282a', deep: '#6a1418' };
const SH = { dark: '#1a0a10' };

// ---------- les formes relevées sur l'original ----------
const ell = (cx, cy, rx, ry) => `M${n(cx - rx)} ${cy}a${rx} ${ry} 0 1 0 ${n(2 * rx)} 0a${rx} ${ry} 0 1 0 ${n(-2 * rx)} 0Z`;
// le tambour et sa face : la région rouge-or-blanc d'un seul tenant (bras et pattes sombres exclus)
const DRUM = sm('98,220 91,236 84,256 78,261 71,290 70,317 72,335 80,362 86,370 92,388 103,394 108,400 136,413 170,425 180,425 198,431 235,432 252,430 266,428 273,421 297,423 320,426 363,424 374,413 383,408 391,389 406,359 413,339 417,315 417,293 416,273 413,266 409,252 410,238 399,214 389,212 368,195 352,187 341,184 309,184 275,177 214,177 192,179 166,183 143,190 128,196 117,204');
// les bras (baguette et boule comprises) et les pattes : la silhouette coupée par un polygone (ils filent sous le tambour)
const ARM_L = sm('12,44 5,62 5,79 11,96 23,108 31,112 46,114 67,109 86,131 83,136 82,146 77,155 77,164 115,201 113,205 114,207 128,213 190,196 187,184 184,180 177,182 171,174 162,170 149,159 144,148 143,138 129,117 124,113 113,115 90,91 89,88 93,81 94,74 93,57 88,46 77,33 60,25 39,25 26,31');
const ARM_R = sm('465,13 448,6 430,6 414,12 401,24 396,33 393,47 394,60 397,67 397,70 394,72 394,78 379,92 365,111 354,113 349,118 346,133 343,138 343,147 337,152 335,160 319,171 308,175 304,180 298,180 302,190 319,195 378,206 382,204 382,202 376,198 383,188 385,180 397,164 397,135 394,127 400,122 401,117 424,90 441,92 459,88 472,77 480,63 482,53 480,34 473,21');
const LEG_L = sm('54,485 58,492 67,494 89,494 95,496 99,492 117,495 119,492 131,493 133,490 145,493 144,484 139,475 127,463 116,464 113,461 114,450 116,448 122,451 138,450 145,446 163,426 182,431 210,434 210,360 77,360 74,366 73,376 70,379 65,378 63,381 67,394 74,397 78,393 86,398 92,395 99,402 105,405 99,413 82,406 78,406 70,412 68,442 56,459 52,468 54,474');
const LEG_R = sm('212,395 212,435 224,435 231,443 241,450 241,456 243,459 230,471 233,475 231,484 235,493 279,493 283,495 306,495 309,491 325,493 324,484 313,465 309,463 301,463 296,465 286,462 290,458 290,454 294,451 294,441 290,431 297,429 302,444 308,451 310,459 315,460 321,468 325,476 331,469 336,475 341,481 345,481 343,473 336,471 330,450 325,451 326,438 330,433 337,427 342,434 345,430 345,395');
// la barbe blanche (relevée par sa couleur ; le haut suit la lèvre du bas)
const BEARD = sm('397,385 384,392 366,400 348,408 330,410 312,407 296,401 284,404 284,415 284,425 288,422 293,427 290,432 301,430 304,436 311,433 311,438 305,438 307,448 312,452 322,460 322,469 329,464 329,472 342,482 346,482 344,474 337,472 331,451 325,450 327,440 331,431 336,428 341,432 346,431 354,431 358,437 360,441 365,430 370,437 372,446 366,446 367,451 365,455 369,459 367,466 367,474 371,477 372,468 376,461 376,443 382,439 384,419 389,414 387,402 396,394');
// la face : le cercle de laiton et la peau (ellipses relevées sur le bord de l'anneau)
const RING = ell(328, 300, 92, 120), SKIN = [329, 302, 74, 108];
// les deux bandes dorées, mesurées colonne par colonne (bord haut, puis bord bas en revenant)
const BAND_T = sm('84,246 100,235 108,230 116,223 124,217 132,213 148,208 164,205 196,200 220,197 252,198 280,197! 282,223! 252,226 220,226 196,227 164,231 148,235 132,238 116,243 108,245 100,250 86,260');
const BAND_B = sm('78,357 92,362 100,366 116,371 132,375 148,378 164,381 188,385 204,387 220,388 252,388 290,390! 290,420! 252,419 220,418 204,416 188,415 164,410 148,405 132,398 116,394 100,386 80,376');
// le zigzag blanc : ses sommets (lus sur la ligne blanche, à chaque hauteur)
const ZIG = 'M89 250L114 363L146 237L172 377L208 226L233 392';
// les clous des bandes
const STUDS = [[100, 239], [141, 220], [189, 211], [262, 205], [97, 372], [135, 390], [185, 402], [257, 405]];
// le visage : le rouge commence sous l'étoile et les sourcils
const MASK = sm('256,240 262,230! 287,231 300,226 311,223! 329,193! 348,223! 362,230 375,234 390,232 404,236! 440,236! 440,440! 230,440! 230,240!');
const BROW_L = sm('258,233 287,231 313,244 334,257 339,267 330,269 312,266 287,259 268,253 257,247');
const BROW_R = sm('404,234 378,234 356,246 342,257 337,267 350,269 359,266 378,259 396,251 405,246');
const NOSE = sm('333,266 344,262 351,268 356,286 364,298 363,308 354,312 346,309 338,312 328,309 325,299 333,286');
const MOUTH = sm('270,330 300,334 330,336 360,333 388,327 389,345 385,362 377,381 363,398 340,410 313,411 296,403 287,393 280,373 273,350');

// ---------- dégradés ----------
const defs = [
  lin('g-drum', 260, 180, 140, 430, [[0, RED.lite], [0.45, RED.base], [1, RED.shade]]),
  lin('g-limb', 1, 0, 0, 1, [[0, LIMB.lite], [0.45, LIMB.base], [1, LIMB.deep]], false),
  lin('g-ring', 400, 190, 250, 410, [[0, CREAM.hi], [0.55, CREAM.base], [1, CREAM.shade]]),
  lin('g-face', 400, 220, 280, 340, [[0, FACE.lite], [0.6, FACE.base], [1, FACE.shade]]),
  lin('g-mouth', 0, 330, 0, 410, [[0, '#12030a'], [0.6, '#2a060e'], [1, '#5a1018']]),
  lin('g-beard', 0, 395, 0, 485, [[0, '#fbf8f2'], [0.5, '#e4dcd2'], [1, '#a89e94']]),
  lin('g-stick', 0, 0, 1, 0, [[0, '#8a5a2c'], [0.45, '#d8a85c'], [0.8, '#f6e2b0'], [1, '#c8964a']], false),
  rad('g-ball', 0.7, 0.28, 0.85, [[0, '#ffb890'], [0.3, '#f45a3c'], [0.75, '#c42a20'], [1, '#741010']], false),
  rad('g-eye', 0.55, 0.4, 0.7, [[0, '#fffbe0'], [0.45, '#ffe46a'], [1, '#e8a020']], false),
  rad('g-stud', 0.65, 0.3, 0.8, [[0, '#fff2c0'], [0.4, '#f0b040'], [1, '#8a4a14']], false),
  `<clipPath id="c-skin"><path d="${ell(...SKIN)}"/></clipPath>`,
  `<clipPath id="c-ballL"><circle cx="48.5" cy="68" r="45"/></clipPath><clipPath id="c-ballR"><circle cx="436.5" cy="47.5" r="45"/></clipPath>`,
].join('');

// ---------- petites pièces ----------
// une baguette de laiton (de la boule vers la main), éclairée en haut à droite
function stick(x0, y0, x1, y1, w) {
  const L = Math.hypot(x1 - x0, y1 - y0), nx = -(y1 - y0) / L, ny = (x1 - x0) / L; // normale (vers le bas-gauche)
  const at = (f, s) => [n(x0 + (x1 - x0) * f + nx * s), n(y0 + (y1 - y0) * f + ny * s)];
  const body = rib([[x0, y0, w], [x1, y1, w]]);
  return shape(body, '#c8964a') + shape(rib([at(0, w * 0.28).concat(w * 0.45), at(1, w * 0.28).concat(w * 0.45)]), '#8a5a2c', 0.85)
    + shape(rib([at(0.05, -w * 0.18).concat(w * 0.3), at(0.95, -w * 0.18).concat(w * 0.3)]), '#f6e2b0', 0.9)
    + shape(rib([at(0.1, -w * 0.26).concat(w * 0.1), at(0.9, -w * 0.26).concat(w * 0.1)]), '#ffffff', 0.7);
}
// une boule rouge baguée d'or : band = la bague (bord haut puis bord bas), coupée dans la boule
function ball(cx, cy, r, band, side) {
  return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#g-ball)"/>`
    + `<g clip-path="url(#c-ball${side})">`
    + cel(band, GOLD, 4, 2)
    // l'ombre ronde en bas à gauche, le reflet en haut à droite
    + `<path d="${ell(cx - r * 0.12, cy + r * 0.12, r * 1.02, r * 1.02)} ${ell(cx + r * 0.08, cy - r * 0.1, r * 0.95, r * 0.95)}" fill-rule="evenodd" fill="#5a0a0c" opacity="0.45"/>`
    + oval(cx + r * 0.32, cy - r * 0.48, r * 0.26, r * 0.13, '#ffffff', 0.75, -28) + dot(cx + r * 0.55, cy - r * 0.18, r * 0.06, '#ffffff', 0.8)
    + '</g>';
}
// un clou doré
const stud = ([x, y], r = 4.6) => dot(x - 0.6, y + 0.8, r + 1.2, GOLD.deep, 0.9) + dot(x, y, r, 'url(#g-stud)') + dot(x + r * 0.35, y - r * 0.4, r * 0.3, '#ffffff', 0.9);
// une griffe claire (racine b1-b2, pointe t), le flanc gauche à l'ombre
function claw([x1, y1], [x2, y2], [tx, ty]) {
  const d = `M${x1} ${y1}Q${n(x1 + (tx - x1) * 0.2)} ${n(ty - 2)} ${tx} ${ty}Q${n(x2 + 2)} ${n((y2 + ty) / 2)} ${x2} ${y2}Z`;
  const half = `M${x1} ${y1}Q${n(x1 + (tx - x1) * 0.2)} ${n(ty - 2)} ${tx} ${ty}L${n((x1 + x2) / 2 + 1)} ${n((y1 + y2) / 2 + 2)}Z`;
  return shape(d, '#eee6dc') + shape(half, '#9c8e86', 0.85) + line(`M${n((x1 + x2) / 2 + 3)} ${n((y1 + y2) / 2 + 1)}Q${n(x2)} ${n((y2 + ty) / 2)} ${n(tx - 1)} ${n(ty - 3)}`, '#ffffff', 1.3, 0.8);
}

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color = SH.dark, o = 0.45) => ({ on, dx, dy, color, o });
const armBody = (id) => use(id, 'url(#g-limb)');
const parts = [
  { id: 'armL', cls: 'a-armL', d: ARM_L, body: armBody('armL') + clip('armL',
    // les reflets sur le poing et l'avant-bras
    glint([[96, 119, 0], [112, 113, 3.2], [126, 119, 0]], LIMB.hi, 0.75) + glint([[128, 122, 0], [136, 138, 3.4], [134, 152, 0]], LIMB.hi, 0.55)
    + glint([[146, 162, 0], [160, 172, 3.6], [172, 188, 0]], LIMB.hi, 0.5) + glint([[86, 146, 0], [94, 160, 3], [106, 172, 0]], LIMB.deep, 0.6)
    // le bracelet doré
    + cel(sm('96,158 118,150 140,145 143,157 122,163 100,170'), GOLD, 4, 2)
    + stick(66, 84, 102, 120, 15) + ball(48.5, 68, 45, sm('0,65 30,58 60,50 96,42! 96,60! 64,64 36,73 0,85!'), 'L')) },
  { id: 'armR', cls: 'a-armR', d: ARM_R, body: armBody('armR') + clip('armR',
    glint([[366, 114, 0], [384, 116, 3.2], [396, 128, 0]], LIMB.hi, 0.75) + glint([[388, 132, 0], [392, 146, 3], [388, 160, 0]], LIMB.hi, 0.5)
    + glint([[318, 172, 0], [336, 158, 3.4], [356, 150, 0]], LIMB.hi, 0.5) + glint([[350, 122, 0], [352, 140, 3], [346, 156, 0]], LIMB.deep, 0.55)
    + cel(sm('370,151 382,148 393,145 396,158 385,161 374,165'), GOLD, 3, 2)
    + stick(421, 68, 386, 112, 17)
    // la douille sombre où la baguette entre dans la boule
    + oval(414, 75, 10, 5, LIMB.shade, 1, -52)
    + ball(436.5, 47.5, 45, sm('390,50 420,46 450,42 484,37! 484,56! 452,58 422,62 390,68!'), 'R')) },
  { id: 'legL', cls: 'a-legL', d: LEG_L, body: use('legL', 'url(#g-limb)') + clip('legL',
    glint([[116, 408, 0], [134, 424, 3.6], [134, 446, 0]], LIMB.hi, 0.6) + dot(126, 432, 2.4, '#f4e2bc', 0.9)
    + glint([[64, 458, 0], [92, 453, 3], [122, 460, 0]], LIMB.hi, 0.5) + glint([[72, 449, 0], [96, 451, 2.6], [118, 454, 0]], LIMB.deep, 0.6)
    + glint([[66, 380, 0], [72, 388, 2.4], [80, 394, 0]], LIMB.hi, 0.45)
    + claw([74, 471], [92, 466], [95, 490]) + claw([99, 469], [115, 467], [119, 489]) + claw([121, 472], [135, 470], [144, 492])) },
  { id: 'legR', cls: 'a-legR', d: LEG_R, body: use('legR', 'url(#g-limb)') + clip('legR',
    glint([[262, 432, 0], [284, 442, 3.4], [290, 460, 0]], LIMB.hi, 0.6) + glint([[236, 470, 0], [262, 464, 3], [292, 467, 0]], LIMB.hi, 0.5)
    + glint([[240, 458, 0], [262, 460, 2.4], [284, 462, 0]], LIMB.deep, 0.55)
    + claw([252, 482], [266, 479], [271, 492]) + claw([278, 479], [293, 476], [298, 493]) + claw([301, 479], [317, 476], [325, 494])) },
  { id: 'body', cls: 'a-body', d: DRUM, shadow: [sh(['armL', 'armR', 'legL', 'legR'], -3, 6)], body: use('body', 'url(#g-drum)') + clip('body',
    // le dessus du tambour, plus clair, et le dessous, plus sombre
    shape(sm('60,262! 84,246 100,235 116,223 132,213 164,205 220,197 280,197! 280,160! 60,160!'), '#e0605c', 0.75)
    + shape(sm('60,376! 100,386 132,398 164,410 204,416 252,419 290,420! 290,450! 60,450!'), RED.deep, 0.55)
    // le reflet rose sur le bord gauche (la lumière de rebord), la lueur du haut à droite
    + glint([[96, 228, 0], [80, 262, 6], [74, 310, 7], [80, 352, 5], [90, 382, 0]], RED.rim, 0.55)
    + glint([[120, 196, 0], [180, 186, 4], [250, 183, 3], [300, 188, 0]], '#ffb0a0', 0.5)
    + oval(196, 290, 46, 34, RED.lite, 0.35, -10)
    // les petites vis du milieu
    + [[173, 297], [173, 310], [175, 323]].map(([x, y]) => dot(x, y, 1.8, RED.deep, 0.8) + dot(x + 0.5, y - 0.5, 0.8, '#ff9a80', 0.8)).join('')
    // le zigzag blanc (une ombre, la ligne, un fil de lumière), puis les bandes dorées par-dessus ses bouts
    + `<path d="${ZIG}" transform="translate(-1.3 1.5)" fill="none" stroke="#7a1418" stroke-width="7" stroke-linejoin="miter" stroke-miterlimit="12" opacity="0.5"/>`
    + `<path d="${ZIG}" fill="none" stroke="${CREAM.base}" stroke-width="6" stroke-linejoin="miter" stroke-miterlimit="12"/>`
    + `<path d="${ZIG}" transform="translate(1 -0.6)" fill="none" stroke="${CREAM.hi}" stroke-width="1.6" stroke-linejoin="miter" stroke-miterlimit="12" opacity="0.9"/>`
    + `<path d="${ZIG}" transform="translate(-1.6 1)" fill="none" stroke="${CREAM.shade}" stroke-width="1.6" stroke-linejoin="miter" stroke-miterlimit="12" opacity="0.8"/>`
    + `<path d="${BAND_T}" transform="translate(-2 4)" fill="${SH.dark}" opacity="0.35"/>` + cel(BAND_T, GOLD, 6, 3)
    + `<path d="${BAND_B}" transform="translate(-2 4)" fill="${SH.dark}" opacity="0.35"/>` + cel(BAND_B, GOLD, 7, 3)
    + STUDS.map((p) => stud(p)).join('')) },
  { id: 'face', cls: 'a-body', d: RING, shadow: [sh(['body'], -4, 5, SH.dark, 0.4)], body: shape(RING, '#b07a42') + clip('face',
    // l'anneau de laiton : un liseré doré sur le bord gauche, la peau crème
    shape(ell(332, 300, 90, 119), 'url(#g-ring)')
    + [[241, 290], [241, 306], [243, 322], [247, 338], [252, 353], [259, 367], [246, 258], [252, 242]].map(([x, y]) => dot(x, y, 2.6, '#8a5a30') + dot(x + 0.7, y - 0.8, 1, '#f4d8a8')).join('')
    + oval(248, 330, 3.5, 6, FACE.base, 0.35) + oval(262, 384, 3, 4, FACE.base, 0.3) + oval(404, 352, 2.5, 5, FACE.base, 0.3)
    // la peau : un creux d'ombre sous l'anneau, puis le visage
    + shape(ell(...SKIN), CREAM.shade) + shape(ell(SKIN[0] + 2, SKIN[1] - 2, SKIN[2] - 1.5, SKIN[3] - 1.5), '#f8efe2')
    + `<g clip-path="url(#c-skin)">`
    + shape(MASK, 'url(#g-face)')
    // l'étoile : sa moitié droite plus claire
    + shape('M329 194L348 223L336 236L330 214Z', FACE.hi, 0.5)
    // la joue droite et la gauche dans l'ombre le long de l'anneau
    + shape(sm('256,250 270,262 272,320 262,360 250,340'), FACE.shade, 0.6)
    // les creux des yeux, les yeux jaunes, les pupilles, les reflets
    + oval(299, 279, 24, 19, FACE.deep, 0.95) + oval(369, 279, 21, 19, FACE.deep, 0.95)
    + oval(299, 277, 20, 15, '#c06a16') + oval(299.6, 276.4, 18.4, 13.6, 'url(#g-eye)')
    + oval(369, 278, 17, 15, '#c06a16') + oval(369.5, 277.5, 15.6, 13.6, 'url(#g-eye)')
    + dot(303, 276, 7.6, '#1e0606') + dot(367, 278.5, 6.6, '#1e0606') + dot(306, 280, 1.8, '#ffffff', 0.9) + dot(364.5, 281.5, 1.6, '#ffffff', 0.9)
    + `<g class="a-blink" opacity="0">${oval(299, 277, 21, 16, FACE.base)}${oval(369, 278, 18, 16, FACE.base)}${line('M280 282 Q299 290 319 281', FACE.deep, 2.4)}${line('M352 281 Q369 289 387 280', FACE.deep, 2.4)}</g>`
    // l'ombre sous les sourcils : elle mange le haut des yeux en biais (le regard furieux)
    + shape(sm('274,262! 290,258 300,263 318,273 328,287! 336,280! 334,262 300,248 272,248!'), '#3a0a10')
    + shape(sm('346,277! 368,267 386,259 394,262! 396,246! 362,254 342,266!'), '#3a0a10')
    // les gros sourcils froncés (ils coupent le haut des yeux)
    + `<path d="${BROW_L}" transform="translate(-1 4)" fill="${FACE.deep}" opacity="0.6"/><path d="${BROW_R}" transform="translate(-1 4)" fill="${FACE.deep}" opacity="0.6"/>`
    + cel(BROW_L, { hi: FACE.hi, base: FACE.lite, sh: FACE.shade, deep: FACE.deep }, 4, 2.4)
    + cel(BROW_R, { hi: FACE.hi, base: FACE.lite, sh: FACE.shade, deep: FACE.deep }, 4, 2.4)
    // le nez épaté, ses narines ; le pli sous le nez, la lèvre du haut et ses plis
    + `<path d="${NOSE}" transform="translate(-2 3)" fill="${FACE.deep}" opacity="0.5"/>` + cel(NOSE, { hi: FACE.hi, base: FACE.lite, sh: FACE.shade }, 4, 2)
    + oval(336, 305, 3.6, 2.4, '#3a0608') + oval(354, 305, 3.6, 2.4, '#3a0608')
    + shape(sm('262,314 292,308 326,312 346,316 366,311 398,305 406,320 400,334 268,337'), FACE.shade, 0.7)
    + glint([[270, 320, 0], [292, 316, 3], [318, 321, 0]], FACE.hi, 0.55) + glint([[358, 319, 0], [378, 314, 3], [398, 313, 0]], FACE.hi, 0.55)
    + glint([[322, 313, 0], [345, 319, 2.4], [368, 313, 0]], FACE.deep, 0.8)
    // la gueule ouverte : le fond sombre, la langue, les crocs du haut ; ceux du bas bougent avec la mâchoire
    // les joues crèmes de part et d'autre de la gueule (la peau du tambour), tachées de rouge
    + shape(sm('248,312! 262,316 272,326 276,345 280,372 290,398 298,412! 248,412!'), CREAM.base)
    + shape(sm('391,380 400,376 412,372! 412,412! 384,412!'), CREAM.base)
    + oval(262, 330, 4, 7, FACE.base, 0.35) + oval(268, 362, 3, 5, FACE.base, 0.3) + oval(396, 392, 3, 4, FACE.base, 0.3)
    + `<path d="${MOUTH}" fill="url(#g-mouth)"/>`
    // la gencive crème d'où pendent les crocs du haut
    + shape(sm('268,324 300,327 330,329 360,327 390,322 391,332 360,335 330,337 300,335 270,333'), CREAM.base)
    + glint([[272, 326, 0], [330, 331, 2], [388, 324, 0]], CREAM.hi, 0.8)
    + [[[272, 330], [282, 331], [277, 343]], [[281, 331], [301, 333], [290, 349]], [[303, 333], [328, 335], [318, 361]], [[331, 335], [355, 334], [343, 358]], [[359, 333], [377, 331], [368, 351]], [[377, 331], [386, 329], [381, 343]]].map(([a, b, t]) => tooth(a, b, t)).join('')
    + `<g class="a-jaw2">${oval(326, 393, 30, 13, '#a8242e')}${oval(334, 387, 14, 4, '#e0606a', 0.7)}`
    + [[[298, 402], [311, 403], [305, 376]], [[357, 396], [370, 393], [364, 369]], [[369, 393], [377, 391], [374, 372]], [[331, 408], [347, 407], [339, 394]], [[347, 406], [358, 404], [352, 394]]].map(([a, b, t]) => tooth(a, b, t)).join('') + '</g>'
    + '</g>') },
  // la barbe blanche, sous la gueule (elle bouge avec la mâchoire)
  { id: 'beard', cls: 'a-jaw', d: BEARD, shadow: [sh(['legL', 'legR', 'face', 'body'], -3, 4, SH.dark, 0.4)], body: use('beard', 'url(#g-beard)') + clip('beard',
    glint([[284, 410, 0], [320, 413, 5], [360, 404, 5], [398, 388, 0]], '#ffffff', 0.75)
    + [300, 317, 334, 350, 366, 380].map((x, i) => glint([[x, 414, 0], [x - 1, 438, 3.2], [x + 2, 468 - (i % 2) * 8, 0]], '#857a72', 0.55)
      + glint([[x + 6, 416, 0], [x + 6, 436, 1.8], [x + 7, 456, 0]], '#ffffff', 0.55)).join('')) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : les baguettes battent la mesure (un bras puis l'autre), le tambour respire, la mâchoire gronde, il cligne,
// les pattes piétinent. Attaque (classe « atk », 0,75 s) : il arme ses deux baguettes en arrière, puis bondit en avant
// et frappe des deux baguettes, la gueule grande ouverte ; tout revient à la pose de repos.
const PIV = { armL: [168, 196], armR: [318, 188], body: [240, 440], legL: [110, 420], legR: [270, 440], jaw: [340, 400] };
const IDLE = {
  'a-armL': ['armL', 'armL .9s ease-in-out infinite alternate'],
  'a-armR': ['armR', 'armR .9s ease-in-out infinite alternate-reverse'],
  'a-body': ['body', 'body 1.8s ease-in-out infinite alternate'],
  'a-legL': ['legL', 'legL 1.8s ease-in-out infinite alternate'],
  'a-legR': ['legR', 'legR 1.8s ease-in-out infinite alternate-reverse'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-root{transform-origin:240px 490px}
.a-jaw,.a-jaw2{transform-origin:${PIV.jaw[0]}px ${PIV.jaw[1]}px;animation:jaw .5s ease-in-out infinite alternate}
.a-blink{animation:blink 4s linear infinite}
@keyframes armL{from{transform:none}to{transform:rotate(5deg)}}
@keyframes armR{from{transform:none}to{transform:rotate(-5deg)}}
@keyframes body{from{transform:none}to{transform:translate(0,-2px) scale(1.006,1.012)}}
@keyframes legL{from{transform:none}to{transform:translate(0,-1.5px)}}
@keyframes legR{from{transform:none}to{transform:translate(0,-1.5px)}}
@keyframes jaw{from{transform:none}to{transform:translate(0,2.5px)}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-armL', 'armL-atk')}${atk('a-armR', 'armR-atk')}
.atk .a-jaw,.atk .a-jaw2{animation:jaw .5s ease-in-out infinite alternate,jaw-atk .75s ease-in-out;animation-composition:replace,add}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-10px,2px) rotate(-2deg)}50%{transform:translate(16px,-6px) rotate(2deg)}64%{transform:translate(13px,0)}84%{transform:translate(4px,0)}100%{transform:none}}
@keyframes armL-atk{0%{transform:none}30%{transform:rotate(-12deg)}50%{transform:rotate(28deg)}64%{transform:rotate(22deg)}100%{transform:none}}
@keyframes armR-atk{0%{transform:none}30%{transform:rotate(-16deg)}50%{transform:rotate(15deg)}64%{transform:rotate(11deg)}100%{transform:none}}
@keyframes jaw-atk{0%{transform:none}30%{transform:translate(0,2px)}50%{transform:translate(0,7px)}70%{transform:translate(0,5px)}100%{transform:none}}
`.replace(/\n/g, '');

const SIL = require('./silhouettes/parade-5.json');
function svg(anime = true) {
  let s = figure({ master: SIL, w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  s = nest(s, 'a-jaw', 'a-body'); // la barbe suit aussi le souffle du tambour
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'parade-5', w: W, h: H, pad: PAD, foot: [240, 494], svg };
