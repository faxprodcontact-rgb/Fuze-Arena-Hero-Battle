// Ilian (angels-2), héros Légendaire : redessiné par le code d'après le dessin d'origine, dans le même cadre (560 × 475,
// mêmes proportions, même pose) : un dieu des mers trapu et musclé ; couronne d'or à pointes, grande crinière et
// barbe blanches, gros sourcils blancs froncés, yeux bleu turquoise, nez rond ; épaulières et brassards d'or, cape bleu
// nuit, jupe bleue à ceinture d'or, jambières et sandales d'or ; il tient en travers un grand trident d'or.
// MÉTHODE (comme Rook, assassins-5) : la silhouette exacte de l'original (master) donne le bord ; à l'intérieur, chaque
// pièce est une forme nette relevée sur un gros plan quadrillé, peinte en aplats (une ombre franche en bas à gauche, un
// liseré clair en haut à droite) et quelques détails dessinés (mèches, plis, muscles), jamais les taches de l'original.
// La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');
const { sm, rib, glint, cel, almond } = require('./formes.cjs');
const EL = almond(250, 160, 46, 27, -1, 4.6), ER = almond(310, 160, 46, 27, 1, 4.6);

const W = 560, H = 475, PAD = 44;
const SIL = require('./silhouettes/angels-2.json');

// ---------- couleurs ----------
const SKIN = { hi: '#ffe8d2', base: '#ffc89e', sh: '#e8986e', deep: '#c46e52' };
const WHITE = { hi: '#ffffff', base: '#eef3fb', sh: '#c4d2e8', deep: '#8fa4c8' };
const GOLD = { hi: '#fff4b8', base: '#f6be44', sh: '#c67e1e', deep: '#8a5012' };
const BLUE = { hi: '#68c0f2', base: '#2f88cc', sh: '#1d5c98', deep: '#123b6c' };
const CAPE = { hi: '#62b8ee', base: '#2f7cba', sh: '#1d5690', deep: '#123a66' };
const WOOD = { hi: '#f2be6a', base: '#a0642a', sh: '#6a3c16', deep: '#3e200a' };

// ---------- les formes relevées sur l'original ----------
const BODY = SIL.out; // le corps : toute la silhouette (la tête est posée dessus)
// la tête : la crinière (prise dans la silhouette) réunie à la barbe, pour que les pointes de la barbe se voient sur le torse
const HEAD = sm('346,44 342,43 339,46 335,46 334,38 329,36 326,38 323,49 321,51 316,51 311,47 300,42 296,36 293,16 288,5 283,7 272,33 249,31 244,34 234,35 228,23 224,20 220,23 219,31 215,38 208,38 203,41 195,42 185,50 181,50 173,41 168,42 168,62 150,81 144,100 145,108 140,112 138,118 133,124 131,134 117,143 96,143 79,152 77,160 72,164 68,174 69,177 72,175 76,175 76,172 82,167 86,167 88,169 88,174 85,177 77,177 78,181 81,183 81,187 75,193 72,193 76,198 79,199 79,203 73,210 72,216 59,218 42,224 48,236 56,229 61,229 70,244 77,231 82,230 92,246 107,201 122,190 148,186 164,189 175,193 178,226 190,240 192,258 206,266 210,284 228,288 236,302 245,299 251,299 262,310 274,296 290,298 300,280 316,276 325,257 340,250 348,227 350,187 361,178 353,177 348,172 345,165 345,151 351,143 351,135 354,130 354,110 349,104 348,95 344,90 344,80 346,74');
const CROWN = sm('226,22 224,22 223,25 220,24 218,32 220,33 220,46 215,55 215,59 212,60 212,69 206,77 198,73 193,67 188,66 175,51 173,47 175,43 168,42 168,50 171,51 174,60 178,64 178,67 174,70 176,87 180,89 178,90 178,95 184,95 188,92 192,92 195,90 211,86 219,86 223,82 235,84 236,79 239,75 242,74 246,77 249,77 253,73 253,70 249,70 243,66 240,55 237,55 233,52 233,49 227,40 228,36 231,35 231,33 229,32');
const T = {
  armL: sm('110,244 150,246 172,254 178,270 168,284 150,290 132,296 116,304 100,302 92,286 92,264 98,250'), fistL: sm('211,304 207,302 199,293 193,293 191,291 171,290 167,293 161,293 150,300 141,313 141,321 145,324 145,326 141,330 141,334 146,338 154,336 156,338 161,338 164,341 174,341 182,336 187,336 190,332 196,331 200,327 200,325 205,322 208,318'), armR: sm('381,215 378,214 376,216 364,238 357,237 354,239 347,239 343,235 336,235 329,238 316,247 312,247 310,249 310,261 307,274 311,277 323,280 329,284 348,284 354,276 358,275 364,267 364,264 370,262 376,254 377,249 381,245'), fistR: sm('417,231 410,226 400,223 397,216 392,212 386,211 379,213 369,227 365,237 358,245 358,270 361,271 364,267 364,264 368,263 384,276 394,276 399,274 404,269 404,267 408,265 414,258 414,251 418,247 420,242 420,238'),
  thighL: sm('110,385 110,391 113,402 116,407 120,408 127,406 134,408 149,406 162,410 165,405 184,389 184,387 181,385 181,382 177,378 169,375 163,375 161,371 157,368 138,363 128,364 127,354 123,356 119,363 119,366 114,374 114,382'), thighR: sm('345,358 337,358 325,362 316,368 308,371 305,374 304,379 313,390 317,392 327,392 339,375 344,375 351,371 351,368'), greaveR: sm('357,368 352,368 346,372 338,374 330,384 330,386 327,388 327,398 332,398 334,395 338,394 345,402 344,405 332,403 323,410 325,419 328,422 331,429 329,435 330,439 337,437 349,429 363,427 362,406 364,386 361,382'),
};
// relevées à la main sur le quadrillage
const P = {
  cape: sm('160,206 122,212 86,230 54,252 28,282 12,322 8,372 14,414 44,424 72,408 94,384 108,350 118,306 136,256'),
  capeIn: sm('118,214 92,240 70,280 58,330 56,380 64,410! 40,418 16,410 12,370 16,324 30,286 56,254 88,232'),
  skirt: sm('166,316 304,316 310,350 316,392 308,418 260,428 210,428 172,420 160,392 162,350'),
  hem: sm('160,398 210,408 260,410 314,400 312,420 290,432 250,436 206,434 172,428 158,418'),
  chest: sm('160,246 196,236 236,244 278,242 314,248 334,262 336,296 322,322 250,324 190,322 168,300'),
  belt: sm('172,306 210,309 250,310 290,307 312,302 316,322 290,328 250,330 210,330 172,327'),
  pauL: sm('98,232 104,206 122,192 150,188 176,194 190,210 186,232 170,246 140,252 112,250'),
  pauR: sm('300,226 306,206 324,196 346,200 360,214 356,236 338,250 314,250'),
  bracerL: sm('126,284 146,276 168,280 172,300 166,318 146,322 130,316'),
  greaveL: sm('92,394 118,384 144,388 154,410 150,436 132,448 100,446 86,428 86,406'),
  footL: sm('52,432 96,428 142,430 150,446 146,462 98,468 56,466 46,452'),
  footR: sm('300,432 350,428 392,436 404,452 398,464 340,466 302,464 296,448'),
  face: sm('226,96 258,86 300,86 330,96 340,120 338,150 326,172 300,182 280,190 258,182 238,174 222,160 214,138 216,112'),
  ear: sm('150,138 164,134 176,144 178,164 170,178 156,178 148,162'),
  beard: sm('170,168 196,170 222,182 246,194 268,198 292,194 316,184 338,170 350,190 348,226 340,250! 326,256 316,276! 300,280 290,298! 274,296 262,310! 250,298 236,302! 228,288 210,284! 206,266 192,258! 190,240 178,226! 176,200'),
  stache: sm('222,190 240,184 258,189 272,194 288,189 308,184 330,190 322,199 304,196 288,200 272,202 256,200 240,197 228,200'),
  mouth: sm('246,199 266,196 290,199 288,208 276,214 262,214 250,209'),
  browL: sm('200,122 222,118 248,126 268,142 264,150 244,138 222,132 202,134'),
  browR: sm('334,124 314,124 296,134 284,150 292,154 304,142 318,136 336,134'),
  tuft: sm('206,268 230,262 256,268 270,282 262,300 240,306 216,300 204,286'),
  tri: 'M396 20L560 20L560 244L430 244L404 252L394 232Z',
  crownBand: sm('160,84 200,77 250,73 290,71 330,75 352,82 350,97 330,92 290,88 250,90 200,94 164,101'),
  greaveR: sm('300,374 330,363 356,369 367,392 365,420 353,438 318,441 302,429 297,400'),
  thighR: sm('296,350 330,346 350,356 352,380 330,384 300,384'),
};
// les dents du trident (de la fourche à la pointe) et leurs fers de flèche [pointe, coin gauche, coin droit], relevés
const PRONGS = [[[418, 176], [420, 140], [430, 104], [438, 70]], [[446, 186], [468, 146], [492, 110], [516, 62]], [[490, 204], [512, 180], [532, 154], [548, 132]],
  [[408, 150], [416, 180], [440, 196], [480, 204], [512, 196]]];
const HEADS = [[[440, 62], [412, 96], [443, 106]], [[521, 55], [470, 96], [507, 121]], [[552, 127], [507, 150], [527, 166]]];
// les pointes de la couronne [pointe, coin gauche, coin droit]
const SPIKES = [[[169, 42], [160, 86], [190, 80]], [[224, 20], [208, 78], [242, 74]], [[285, 4], [264, 74], [306, 74]], [[329, 36], [314, 78], [338, 78]], [[342, 42], [334, 82], [352, 84]]];
const SHAFT_A = [[22, 400, 15], [110, 364, 16], [210, 322, 16]], SHAFT_B = [[326, 344, 15], [364, 278, 16], [392, 222, 16], [414, 178, 15]];

// ---------- dégradés ----------
const defs = [
  lin('g-cape', 140, 200, 20, 420, [[0, CAPE.hi], [0.35, CAPE.base], [1, CAPE.deep]]),
  lin('g-skirt', 0, 316, 0, 430, [[0, BLUE.hi], [0.4, BLUE.base], [1, BLUE.sh]]),
  lin('g-white', 360, 20, 120, 300, [[0, '#ffffff'], [0.55, WHITE.base], [1, WHITE.sh]]),
  lin('g-skin', 0, 90, 0, 330, [[0, '#ffe0c0'], [1, SKIN.base]]),
  lin('g-gold', 0, 0, 0, 475, [[0, '#ffe68a'], [0.5, GOLD.base], [1, '#e0a030']]),
  lin('g-wood', 0, 0, 0, 1, [[0, WOOD.hi], [0.35, WOOD.base], [1, WOOD.deep]], false),
  rad('g-iris', 0.45, 0.4, 0.75, [[0, '#e8ffff'], [0.35, '#5ae0f0'], [0.75, '#1a90c8'], [1, '#0a4a7a']], false),
  lin('g-mouth', 0, 198, 0, 214, [[0, '#3a0c14'], [1, '#8a2e3a']]),
].join('');

// ---------- petits outils ----------
// une pièce : aplat + ombre franche en bas à gauche + liseré clair en haut à droite (formes nettes, relevées à la main)
const piece = (d, pal, w = 6, hw = 3) => cel(d, pal, w, hw);
// une mèche : un long fuseau doux (jamais un trait fin, jamais en rangée)
const lock = (pts, color, o, w = 4) => glint(pts.map(([x, y], i) => [x, y, i === 0 || i === pts.length - 1 ? 0 : w]), color, o);
// le manche du trident : un cylindre de bois, éclairé en haut
const shaft = (pts) => shape(rib(pts), WOOD.base) + glint(pts.map(([x, y, w], i) => [x + 2, y - 3.5, i === 0 || i === pts.length - 1 ? 0 : w * 0.3]), WOOD.hi, 0.95)
  + glint(pts.map(([x, y, w], i) => [x - 2, y + 4, i === 0 || i === pts.length - 1 ? 0 : w * 0.22]), WOOD.deep, 0.8);
// les plis d'un poing
const crease = (pts) => lock(pts, SKIN.deep, 0.85, 2.4) + lock(pts.map(([x, y]) => [x + 1.4, y - 2]), SKIN.hi, 0.8, 1.2);
// un œil : blanc, iris turquoise, pupille, reflets, ombre de la paupière, cils
function eye(cx, cy, r, white, lash, hl) {
  return shape(white, '#ffffff') + `<clipPath id="c-e${cx}"><path d="${white}"/></clipPath><g clip-path="url(#c-e${cx})">`
    + dot(cx, cy, r, 'url(#g-iris)') + dot(cx, cy, r * 0.42, '#06202e') + dot(cx + hl[0], cy + hl[1], r * 0.28, '#ffffff') + dot(cx - hl[0] * 0.6, cy + 4, r * 0.12, '#ffffff', 0.9)
    + `<rect x="${cx - 30}" y="${cy - r - 6}" width="60" height="${r}" fill="#0a1a30" opacity="0.25"/></g>` + shape(lash, '#0e0a14')
    + `<g class="a-blink" opacity="0"><path d="${white}" fill="${SKIN.base}" stroke="${SKIN.base}" stroke-width="3"/>${line(`M${cx - r - 8} ${cy + 2} Q${cx} ${cy + 8} ${cx + r + 8} ${cy}`, '#0e0a14', 3)}</g>`;
}

// ---------- le corps (tout sauf la tête) ----------
const bodyPaint =
  // le fond : la doublure sombre de la cape (ce qui reste entre les pièces)
  `<rect x="0" y="0" width="${W}" height="${H}" fill="${CAPE.sh}"/>`
  // la cape : grande nappe bleue, sa doublure plus sombre, deux plis doux
  + `<path d="${P.cape}" fill="url(#g-cape)"/>` + piece(P.capeIn, { hi: CAPE.base, base: CAPE.sh, sh: CAPE.deep }, 5, 2)
  + lock([[132, 230], [96, 290], [74, 360], [70, 404]], CAPE.hi, 0.45, 5) + lock([[110, 236], [72, 290], [44, 350], [30, 404]], CAPE.deep, 0.5, 4)
  // les jambes : cuisses, jambières et sandales d'or
  + piece(T.thighL, SKIN, 6, 3) + piece(P.thighR, SKIN, 5, 2.4)
  + piece(P.greaveL, GOLD, 6, 3) + lock([[100, 400], [120, 392], [142, 396]], GOLD.hi, 0.9, 2.4) + lock([[96, 424], [120, 420], [146, 424]], GOLD.sh, 0.7, 2.4)
  + piece(P.greaveR, GOLD, 6, 3) + lock([[306, 382], [330, 372], [356, 378]], '#fffbe0', 0.9, 2.6) + lock([[304, 410], [330, 404], [362, 410]], GOLD.sh, 0.7, 2.4)
  + oval(332, 392, 9, 8, GOLD.sh, 0.8) + oval(334, 390, 5, 4, '#fffbe0', 0.8)
  + piece(P.footL, GOLD, 5, 2.4) + [[70, 452], [90, 454], [110, 454], [130, 450]].map(([x, y]) => oval(x, y, 7, 5, SKIN.base) + oval(x + 1, y - 1.5, 3, 2, SKIN.hi, 0.9)).join('')
  + piece(P.footR, GOLD, 5, 2.4) + [[322, 452], [342, 454], [362, 452], [382, 450]].map(([x, y]) => oval(x, y, 7, 5, SKIN.base) + oval(x + 1, y - 1.5, 3, 2, SKIN.hi, 0.9)).join('')
  // la jupe bleue : des plis doux, l'ourlet bleu clair, le bord d'or
  + `<path d="${P.skirt}" fill="url(#g-skirt)"/>` + piece(P.skirt, { hi: BLUE.hi, base: 'none', sh: BLUE.sh }, 6, 3)
  + [[188, 330, 182, 410], [220, 332, 216, 414], [252, 332, 252, 416], [284, 330, 290, 410]].map(([x0, y0, x1, y1]) => lock([[x0, y0], [(x0 + x1) / 2 - 2, (y0 + y1) / 2], [x1, y1]], BLUE.sh, 0.6, 4)
    + lock([[x0 + 7, y0], [(x0 + x1) / 2 + 6, (y0 + y1) / 2], [x1 + 7, y1]], BLUE.hi, 0.45, 2.4)).join('')
  + piece(P.hem, { hi: '#d8f2ff', base: '#8ccaf2', sh: '#4e90c8' }, 4, 2) + lock([[164, 400], [210, 410], [260, 412], [312, 402]], GOLD.base, 1, 2.6)
  // le torse nu : pectoraux et ventre (des creux doux), la touffe de poils blancs
  + piece(P.chest, SKIN, 6, 3)
  + lock([[236, 256], [238, 278], [236, 300]], SKIN.sh, 0.6, 3) + lock([[262, 286], [286, 288], [304, 284]], SKIN.sh, 0.55, 3) + lock([[268, 302], [290, 304], [306, 300]], SKIN.sh, 0.5, 2.6)
  + lock([[284, 258], [300, 256], [312, 266]], SKIN.hi, 0.8, 2.6)
  + piece(P.tuft, WHITE, 4, 2) + lock([[214, 274], [228, 290], [236, 302]], WHITE.sh, 0.8, 3) + lock([[240, 270], [250, 286], [252, 300]], WHITE.sh, 0.7, 3)
  // la ceinture d'or et ses pierres bleues
  + piece(P.belt, GOLD, 4, 2) + [[188, 318], [218, 320], [250, 320], [282, 318]].map(([x, y]) => oval(x, y, 4.4, 4, '#2f8fd8') + dot(x + 1.2, y - 1.2, 1.4, '#ffffff', 0.9)).join('')
  // le manche du trident, en bas (sous le poing gauche)
  // (plus de manche dans le poing droit : il ne tient le trident que de la main gauche)
  // les épaulières d'or : une bande claire sur le dessus, deux rivets
  + piece(P.pauL, GOLD, 7, 3) + lock([[110, 214], [140, 198], [176, 200]], '#fffbe0', 0.9, 4) + lock([[106, 236], [140, 240], [180, 232]], GOLD.sh, 0.7, 3)
  + dot(126, 222, 3, GOLD.deep) + dot(160, 222, 3, GOLD.deep)
  + piece(P.pauR, GOLD, 6, 3) + lock([[306, 214], [326, 204], [350, 208]], '#fffbe0', 0.9, 3.4)
  // le bras gauche, son brassard d'or, le poing qui serre le manche
  + piece(T.armL, SKIN, 7, 3) + lock([[98, 270], [104, 288], [120, 298]], SKIN.sh, 0.6, 3.4) + lock([[120, 252], [146, 254], [168, 264]], SKIN.hi, 0.8, 3) + lock([[124, 262], [136, 274], [140, 288]], SKIN.sh, 0.45, 2.6)
  + piece(P.bracerL, GOLD, 4, 2) + lock([[132, 292], [150, 288], [168, 292]], '#fffbe0', 0.85, 2)
  + piece(T.fistL, SKIN, 6, 3) + crease([[160, 304], [176, 300], [192, 304]]) + crease([[158, 318], [176, 314], [196, 318]])
  // le haut du manche, puis le bras droit et son poing (devant le manche)
  + shaft(SHAFT_B)
  + piece(T.armR, SKIN, 6, 3) + lock([[316, 248], [338, 268], [362, 278]], SKIN.sh, 0.6, 3.4) + lock([[320, 232], [344, 228], [366, 236]], SKIN.hi, 0.8, 3)
  // la tête du trident : de l'or poli, un filet de lumière le long de chaque dent, l'ombre sur leur flanc gauche
  + `<path d="${P.tri}" fill="url(#g-gold)"/>`
  // chaque dent : la face droite éclairée, la face gauche à l'ombre ; la pointe en fer de flèche
  + PRONGS.map((g) => lock(g.map(([x, y]) => [x - 4, y + 3]), GOLD.sh, 0.85, 4) + lock(g.map(([x, y]) => [x + 2.5, y - 2]), '#fffbe0', 0.9, 2.6)).join('')
  + HEADS.map(([t, a, b]) => shape(`M${t[0]} ${t[1]}L${a[0]} ${a[1]}L${(a[0] + b[0]) / 2 + 3} ${(a[1] + b[1]) / 2 - 2}Z`, GOLD.sh, 0.7)
    + shape(`M${t[0]} ${t[1]}L${b[0]} ${b[1]}L${(a[0] + b[0]) / 2 + 3} ${(a[1] + b[1]) / 2 - 2}Z`, '#fffbe0', 0.75)).join('')
  // le collier où le manche entre dans la fourche
  + oval(430, 206, 12, 7, GOLD.deep, 0.8, -55) + oval(433, 203, 9, 4, '#fffbe0', 0.7, -55)
  // le poing droit, devant le manche
  + piece(T.fistR, SKIN, 6, 3) + crease([[372, 236], [388, 232], [404, 238]]) + crease([[370, 252], [388, 248], [408, 254]]) + crease([[388, 222], [390, 234], [388, 244]]);

// ---------- la tête ----------
const headPaint =
  // la crinière blanche : de grandes mèches qui tombent vers le bas à gauche (un creux bleuté, une arête claire)
  `<path d="${HEAD}" fill="url(#g-white)"/>`
  + [[[150, 100], [114, 146], [82, 190]], [[166, 126], [138, 176], [116, 216]], [[132, 88], [100, 120], [72, 150]], [[176, 160], [160, 204], [150, 240]],
    [[346, 106], [360, 150], [356, 196]], [[204, 70], [180, 92], [164, 112]], [[332, 64], [352, 84], [362, 110]]]
    .map((h, i) => lock(h, WHITE.deep, 0.55, 5 - (i % 2)) + lock(h.map(([x, y]) => [x + 5, y - 3]), '#ffffff', 0.9, 2.6)).join('')
  // l'oreille
  + piece(P.ear, SKIN, 4, 2) + lock([[158, 146], [166, 156], [164, 170]], SKIN.deep, 0.7, 2.4)
  // le visage : le front plissé, la joue gauche dans l'ombre, la lumière sur la joue droite
  + piece(P.face, SKIN, 7, 3)
  + lock([[262, 104], [282, 100], [302, 104]], SKIN.sh, 0.6, 1.8) + lock([[266, 114], [282, 111], [298, 114]], SKIN.sh, 0.5, 1.6)
  + oval(326, 150, 8, 14, SKIN.hi, 0.6, 10)
  // les yeux bleu turquoise
  + eye(252, 161, 12, EL.white, EL.lash, [-4, -5]) + eye(308, 161, 12, ER.white, ER.lash, [-4, -5])
  // les gros sourcils blancs froncés, leur ombre portée
  + `<path d="${P.browL}" transform="translate(-2 3)" fill="${SKIN.deep}" opacity="0.5"/><path d="${P.browR}" transform="translate(-2 3)" fill="${SKIN.deep}" opacity="0.5"/>`
  + piece(P.browL, WHITE, 3, 1.6) + piece(P.browR, WHITE, 3, 1.6)
  // la barbe : une grande masse blanche, quelques grosses mèches, la bouche ouverte, la moustache par-dessus
  + `<path d="${P.beard}" transform="translate(-3 4)" fill="${SKIN.deep}" opacity="0.45"/>` + piece(P.beard, WHITE, 7, 3)
  + [[[196, 196], [204, 236], [220, 270]], [[226, 214], [234, 252], [244, 288]], [[262, 220], [266, 258], [264, 294]], [[300, 214], [298, 248], [290, 278]], [[330, 200], [328, 232], [316, 260]]]
    .map((h) => lock(h, WHITE.sh, 0.75, 4) + lock(h.map(([x, y]) => [x + 4, y - 2]), '#ffffff', 0.95, 2)).join('')
  + `<path d="${P.mouth}" fill="url(#g-mouth)"/>` + shape('M250 200 C262 198 278 198 288 200 L287 204 C276 202 262 202 251 204 Z', '#ffffff')
  + `<path d="${P.stache}" transform="translate(-2 3)" fill="${WHITE.deep}" opacity="0.5"/>` + piece(P.stache, { hi: '#ffffff', base: '#f8faff', sh: WHITE.sh }, 2.4, 1.4)
  + lock([[222, 196], [244, 192], [266, 198]], WHITE.sh, 0.8, 2.6) + lock([[282, 197], [304, 191], [326, 194]], WHITE.sh, 0.8, 2.6)
  // le nez rond, éclairé
  + oval(277, 177, 13, 8, SKIN.sh) + oval(280, 174, 10, 6, '#ffc49c') + oval(284, 172, 3.4, 2, '#ffffff', 0.85)
  // la couronne d'or : chaque pointe a sa face éclairée et sa face à l'ombre ; une bande sombre au pied ; deux gemmes
  + SPIKES.map(([t, a, b]) => `<path d="M${t[0]} ${t[1]}L${a[0]} ${a[1]}L${b[0]} ${b[1]}Z" transform="translate(-2 3)" fill="${GOLD.deep}" opacity="0.5"/>`
    + shape(`M${t[0]} ${t[1]}L${a[0]} ${a[1]}L${b[0]} ${b[1]}Z`, GOLD.base) + shape(`M${t[0]} ${t[1]}L${(a[0] + b[0]) / 2} ${a[1]}L${b[0]} ${b[1]}Z`, '#fff0a0')
    + shape(`M${t[0]} ${t[1]}L${a[0]} ${a[1]}L${a[0] + (b[0] - a[0]) * 0.25} ${a[1]}Z`, GOLD.sh, 0.7)).join('')
  + `<path d="${P.crownBand}" transform="translate(-2 4)" fill="${WHITE.deep}" opacity="0.6"/>` + piece(P.crownBand, GOLD, 4, 2)
  + [[226, 86], [286, 82], [334, 86]].map(([x, y]) => oval(x, y, 4.6, 3.8, '#2f8fd8') + oval(x + 1.2, y - 1.2, 1.4, 1, '#ffffff', 0.9)).join('');

// ---------- les morceaux ----------
const parts = [
  { id: 'body', cls: 'a-body', d: BODY, body: clip('body', bodyPaint) },
  { id: 'head', cls: 'a-head', d: HEAD, shadow: [{ on: ['body'], dx: -4, dy: 6, color: '#0e1a3a', o: 0.4 }], body: clip('head', headPaint) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : il respire (le corps monte et descend un peu), la tête hoche, il cligne. Attaque (classe « atk », 0,75 s) :
// il se ramasse puis bondit en avant en pointant le trident ; tout revient à la pose de repos.
const PIV = { head: [260, 280], body: [240, 460] };
const IDLE = {
  'a-head': ['head', 'head 2.8s ease-in-out infinite alternate'],
  'a-body': ['body', 'body 2s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-root{transform-origin:240px 460px}
.a-blink{animation:blink 4.4s linear infinite}
@keyframes head{from{transform:none}to{transform:rotate(-1.4deg)}}
@keyframes body{from{transform:none}to{transform:scale(1.004,1.012)}}
@keyframes blink{0%,93%{opacity:0}94.5%,97%{opacity:1}98.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-head', 'head-atk')}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-8px,4px) rotate(-3deg)}48%{transform:translate(22px,-6px) rotate(4deg)}62%{transform:translate(18px,-2px) rotate(3deg)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}30%{transform:rotate(-2deg)}48%{transform:rotate(2deg)}100%{transform:none}}
`.replace(/\n/g, '');

function svg(anime = true) {
  const s = figure({ master: SIL, w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'angels-2', w: W, h: H, pad: PAD, foot: [230, 462], svg };
