// Ilian (angels-2), héros Légendaire : redessiné par le code d'après le dessin d'origine, dans le même cadre (560 × 475,
// mêmes proportions, même pose) : un dieu des mers trapu et musclé ; couronne d'or à pointes, grande crinière et
// barbe blanches, gros sourcils blancs froncés, yeux bleu turquoise, nez rond ; épaulières et brassards d'or, cape bleu
// nuit, jupe bleue à ceinture d'or, jambières et bottes d'or ; il tient haut un grand trident d'or.
// DÉCALQUÉ : silhouette exacte (master) ; les aplats de chaque matière, clairs et ombres, relevés sur l'original
// (outils/couleurs.py → couleurs/angels-2.json) ; visage, reflets de l'or et du trident dessinés par-dessus d'après un
// gros plan quadrillé. La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');
const { sm, rib, glint, cel } = require('./formes.cjs');

const W = 560, H = 475, PAD = 44;
const SIL = require('./silhouettes/angels-2.json');
const MAT = require('./couleurs/angels-2.json');
const SHD = require('./couleurs/angels-2-ombres.json'); // les ombres et reflets de l'original, par matière

// ---------- chaque matière, peinte en aplats nets (ombre en bas à gauche, liseré clair en haut à droite) ----------
const TONES = {
  blanc: { hi: '#ffffff', base: '#eef2f8', sh: '#a8b8d4', deep: '#7c8cae' },
  bleu: { hi: '#7cc4f4', base: '#3a8ccc', sh: '#1f5c9c', deep: '#143e6e' },
  peau: { hi: '#ffe6cc', base: '#ffc8a0', sh: '#e8936a', deep: '#c0704e' },
  or: { hi: '#fff2a0', base: '#f4b23c', sh: '#c07a1c', deep: '#7e4a10' },
};
// les ombres de l'original (mèches de la barbe, muscles, creux de l'or), chacune gardée dans sa matière
const SHADE = [['blancO', 'blanc', '#a8b8d4', 0.9], ['blanc', 'blanc', '#ffffff', 0.9], ['peauO', 'peau', '#e0895e', 0.85], ['orO', 'or', '#a8661a', 0.9], ['bleuO', 'bleu', '#1c4a80', 0.85]];
const paint = ['bleu', 'peau', 'blanc', 'or'].map((k) => (MAT[k] && MAT[k].d ? cel(MAT[k].d, TONES[k], 7, 3) : '')).join('')
  + `<clipPath id="m-blanc"><path d="${MAT.blanc.d}" clip-rule="evenodd"/></clipPath><clipPath id="m-peau"><path d="${MAT.peau.d}" clip-rule="evenodd"/></clipPath>`
  + `<clipPath id="m-or"><path d="${MAT.or.d}" clip-rule="evenodd"/></clipPath><clipPath id="m-bleu"><path d="${MAT.bleu.d}" clip-rule="evenodd"/></clipPath>`
  + SHADE.map(([k, m, c, o]) => (SHD[k] && SHD[k].d ? `<g clip-path="url(#m-${m})"><path d="${SHD[k].d}" fill="${c}" opacity="${o}" fill-rule="evenodd"/></g>` : '')).join('');

// ---------- les pièces du milieu du corps, décalquées une à une (outils/zone.py) et dessinées nettes par-dessus ----------
const PIECE = {
  // décalquées automatiquement (zone fermée par le trait noir d'origine)
  fistL: sm('211,304 207,302 199,293 193,293 191,291 171,290 167,293 161,293 150,300 141,313 141,321 145,324 145,326 141,330 141,334 146,338 154,336 156,338 161,338 164,341 174,341 182,336 187,336 190,332 196,331 200,327 200,325 205,322 208,318'), fistR: sm('417,231 410,226 400,223 397,216 392,212 386,211 379,213 369,227 365,237 358,245 358,270 361,271 364,267 364,264 368,263 384,276 394,276 399,274 404,269 404,267 408,265 414,258 414,251 418,247 420,242 420,238'), bracerL: sm('110,244 111,291 150,291 160,289 160,286 156,283 152,275 155,271 160,270 166,265 165,250 156,252 130,253 125,248 119,248 117,243'),
  armL: sm('112,235 107,243 107,248 102,260 101,270 97,276 96,281 100,298 103,301 147,301 158,295 161,292 160,286 156,283 152,275 155,271 160,270 164,266 173,264 178,257 177,251 175,249 168,249 156,252 130,253 125,248 120,248 119,245 121,240 116,235'), armR: sm('381,215 378,214 376,216 364,238 357,237 354,239 347,239 343,235 336,235 329,238 316,247 312,247 310,249 310,261 307,274 311,277 323,280 329,284 348,284 354,276 358,275 364,267 364,264 370,262 376,254 377,249 381,245'), thighL: sm('110,385 110,391 113,402 116,407 120,408 127,406 134,408 149,406 162,410 165,405 184,389 184,387 181,385 181,382 177,378 169,375 163,375 161,371 157,368 138,363 128,364 127,354 123,356 119,363 119,366 114,374 114,382'),
  thighR: sm('345,358 337,358 325,362 316,368 308,371 305,374 304,379 313,390 317,392 327,392 339,375 344,375 351,371 351,368'), greaveR: sm('357,368 352,368 346,372 338,374 330,384 330,386 327,388 327,398 332,398 334,395 338,394 345,402 344,405 332,403 323,410 325,419 328,422 331,429 329,435 330,439 337,437 349,429 363,427 362,406 364,386 361,382'),
  // relevées à la main sur le quadrillage (le trait d'origine n'y est pas fermé)
  pauL: sm('98,232 104,206 122,192 150,188 176,194 190,210 186,232 170,246 140,252 112,250'),
  pauR: sm('300,226 306,206 324,196 346,200 360,214 356,236 338,250 314,250'),
  belt: sm('166,302 200,304 240,306 280,302 302,298 304,316 280,322 240,326 200,324 168,320'),
  chest: sm('172,248 200,240 230,246 270,250 300,250 312,270 306,298 270,302 230,302 190,300 174,286'),
};
// le manche du trident : deux tronçons visibles (mesurés sur l'original), un cylindre doré-brun éclairé en haut
const shaft = (pts) => shape(rib(pts), '#8a5420') + glint(pts.map(([x, y, w], i) => [x + 2, y - 3, i === 0 || i === pts.length - 1 ? 0 : w * 0.35]), '#f6c460', 0.95)
  + glint(pts.map(([x, y, w], i) => [x - 2, y + 3.5, i === 0 || i === pts.length - 1 ? 0 : w * 0.25]), '#4e2a0c', 0.8);
const SHAFT_A = [[22, 400, 15], [110, 364, 16], [210, 322, 16]], SHAFT_B = [[326, 344, 15], [364, 278, 16], [392, 222, 16], [414, 178, 15]];
// les plis des doigts d'un poing : un creux sombre et une arête claire
const crease = (pts) => glint(pts.map(([x, y], i) => [x, y, i === 0 || i === pts.length - 1 ? 0 : 2.6]), '#c0704e', 0.85)
  + glint(pts.map(([x, y], i) => [x + 1.4, y - 2, i === 0 || i === pts.length - 1 ? 0 : 1.4]), '#ffe6cc', 0.8);
const middle = cel(PIECE.chest, TONES.peau, 6, 3) + glint([[196, 262, 0], [222, 270, 4], [248, 268, 0]], '#e8936a', 0.6) + glint([[258, 272, 0], [282, 278, 4], [302, 272, 0]], '#e8936a', 0.6)
  + cel(PIECE.armL, TONES.peau, 7, 3) + glint([[104, 262, 0], [120, 280, 4], [150, 292, 0]], '#e8936a', 0.6)
  + cel(PIECE.armR, TONES.peau, 6, 3) + glint([[314, 248, 0], [336, 270, 4], [362, 280, 0]], '#e8936a', 0.6)
  + cel(PIECE.thighL, TONES.peau, 7, 3) + cel(PIECE.thighR, TONES.peau, 6, 3) + cel(PIECE.greaveR, TONES.or, 6, 3)
  + shaft(SHAFT_A) + shaft(SHAFT_B)
  + cel(PIECE.belt, TONES.or, 5, 2.5) + [[186, 312], [214, 314], [246, 315], [276, 312]].map(([x, y]) => dot(x, y, 4, '#3a8ccc') + dot(x + 1, y - 1, 1.4, '#ffffff', 0.9)).join('')
  + cel(PIECE.pauL, TONES.or, 7, 3) + glint([[110, 214, 0], [140, 196, 4], [176, 196, 0]], '#fff6c8', 0.9)
  + cel(PIECE.pauR, TONES.or, 6, 3) + glint([[306, 214, 0], [326, 204, 3.4], [350, 208, 0]], '#fff6c8', 0.9)
  + cel(PIECE.bracerL, TONES.or, 5, 2.5)
  + cel(PIECE.fistL, TONES.peau, 6, 3) + crease([[160, 304], [176, 300], [192, 304]]) + crease([[158, 318], [176, 314], [196, 318]])
  + cel(PIECE.fistR, TONES.peau, 6, 3) + crease([[372, 236], [388, 232], [404, 238]]) + crease([[370, 252], [388, 248], [408, 254]]) + crease([[388, 222], [390, 234], [388, 244]]);

// ---------- dégradés ----------
const defs = [
  lin('g-white', 420, 40, 120, 300, [[0, '#ffffff'], [0.6, '#eef2f8'], [1, '#d4dcea']]),
  lin('g-blue', 0, 220, 0, 440, [[0, '#62b0ec'], [0.5, '#3a8ccc'], [1, '#2a6aaa']]),
  lin('g-skin', 0, 120, 0, 420, [[0, '#ffe2c4'], [0.5, '#ffd0aa'], [1, '#f4b890']]),
  lin('g-gold', 0, 0, 0, 475, [[0, '#ffe68a'], [0.4, '#f6bc4a'], [1, '#d8922c']]),
  rad('g-iris', 0.45, 0.4, 0.75, [[0, '#e8ffff'], [0.35, '#5ae0f0'], [0.75, '#1a90c8'], [1, '#0a4a7a']], false),
  lin('g-mouth', 0, 196, 0, 212, [[0, '#4a1018'], [1, '#9a3a44']]),
].join('');

// ---------- le visage, dessiné net par-dessus (relevé sur un gros plan) ----------
function eye(cx, cy, r, white, lash, hl) {
  return shape(white, '#ffffff') + `<clipPath id="c-e${cx}"><path d="${white}"/></clipPath><g clip-path="url(#c-e${cx})">`
    + dot(cx, cy, r, 'url(#g-iris)') + dot(cx, cy, r * 0.42, '#06202e') + dot(cx + hl[0], cy + hl[1], r * 0.28, '#ffffff') + dot(cx - hl[0] * 0.6, cy + 4, r * 0.12, '#ffffff', 0.9)
    + `<rect x="${cx - 30}" y="${cy - r - 6}" width="60" height="${r}" fill="#0a1a30" opacity="0.25"/></g>` + shape(lash, '#0e0a14')
    + `<g class="a-blink" opacity="0"><path d="${white}" fill="#ffd0aa" stroke="#ffd0aa" stroke-width="3"/>${line(`M${cx - r - 8} ${cy + 2} Q${cx} ${cy + 8} ${cx + r + 8} ${cy}`, '#0e0a14', 3)}</g>`;
}
const FACE = eye(240, 159, 11.5, 'M212 150 C222 143 246 142 262 150 C264 158 260 166 250 168 C236 170 220 166 214 160 Z',
    'M206 146 C220 136 248 136 264 148 L262 154 C248 145 226 144 214 152 Z', [-4, -6])
  + eye(309, 160, 10.5, 'M290 152 C300 146 318 145 327 150 C327 158 322 166 312 168 C300 168 292 162 290 156 Z',
    'M286 154 C298 142 320 140 330 146 L328 152 C318 147 302 149 292 158 Z', [-4, -6])
  // les gros sourcils blancs, froncés (qui plongent vers le nez), leur ombre
  + `<path d="M202 120 C222 118 248 128 266 146 L258 152 C244 140 224 132 204 132 Z" fill="#7a8aa8" opacity="0.5" transform="translate(-2 3)"/>`
  + shape('M202 120 C222 118 248 128 266 146 L258 152 C244 140 224 132 204 132 Z', '#ffffff')
  + `<path d="M326 124 C310 126 296 136 288 150 L296 154 C304 144 314 138 328 136 Z" fill="#7a8aa8" opacity="0.5" transform="translate(-2 3)"/>`
  + shape('M326 124 C310 126 296 136 288 150 L296 154 C304 144 314 138 328 136 Z', '#ffffff')
  // le nez rond, éclairé
  + oval(277, 177, 13, 8, '#e0906c') + oval(280, 174, 10, 6, '#ffc49c') + oval(284, 172, 3.4, 2, '#ffffff', 0.85)
  // la bouche ouverte sous la moustache : l'intérieur, les dents du haut
  + shape('M246 200 C258 196 278 196 292 200 C288 208 276 212 266 212 C256 212 248 208 246 200 Z', 'url(#g-mouth)')
  + shape('M252 199 C262 197 276 197 286 199 L285 203 C274 201 262 201 253 203 Z', '#ffffff')
  // la moustache blanche par-dessus, ses mèches (une ombre, un reflet)
  + shape(sm('216,186 236,182 256,190 268,194 282,190 302,184 326,190 318,200 298,198 280,200 262,200 244,200 226,198'), '#f4f6fa')
  + glint([[222, 194, 0], [246, 196, 3], [266, 198, 0]], '#a2b4d2', 0.7) + glint([[272, 197, 0], [298, 194, 3], [320, 196, 0]], '#a2b4d2', 0.7);

// ---------- la couronne : sa forme prise dans la silhouette (les pointes dépassent seules au-dessus des cheveux) ----------
const CROWN = sm('226,22 224,22 223,25 220,24 218,32 220,33 220,46 215,55 215,59 212,60 212,69 206,77 198,73 193,67 188,66 175,51 173,47 175,43 168,42 168,50 171,51 174,60 178,64 178,67 174,70 176,87 180,89 178,90 178,95 184,95 188,92 192,92 195,90 211,86 219,86 223,82 235,84 236,79 239,75 242,74 246,77 249,77 253,73 253,70 249,70 243,66 240,55 237,55 233,52 233,49 227,40 228,36 231,35 231,33 229,32') + sm('283,6 277,20 279,27 269,52 267,54 264,54 262,64 258,66 255,72 263,79 265,84 276,86 283,90 293,88 297,85 310,81 315,81 322,84 329,92 334,91 339,93 340,86 342,83 342,79 340,78 343,77 344,63 341,63 339,61 339,58 342,55 344,55 344,48 338,48 334,51 332,37 327,37 324,46 324,49 327,50 327,53 324,56 320,56 320,62 317,63 316,68 311,70 310,73 307,73 304,70 299,70 298,56 294,57 285,51 286,16 289,14 288,6');
const crown = cel(CROWN, TONES.or, 6, 3)
  // une arête claire sur chaque pointe (la face droite éclairée), une bande plus sombre au pied ; gemmes bleues au bandeau
  + `<clipPath id="c-crown"><path d="${CROWN}"/></clipPath><g clip-path="url(#c-crown)">`
  + [[[184, 52], [190, 90]], [[227, 26], [234, 82]], [[286, 8], [290, 88]], [[327, 40], [330, 88]], [[340, 50], [344, 86]]].map(([t, b]) =>
    shape(`M${t[0]} ${t[1]} L${b[0] + 14} ${b[1]} L${b[0]} ${b[1]} Z`, '#fff2a0', 0.75) + shape(`M${t[0]} ${t[1]} L${b[0]} ${b[1]} L${b[0] - 14} ${b[1]} Z`, '#c98a26', 0.6)).join('')
  + glint([[176, 86, 6], [230, 88, 8], [290, 90, 8], [346, 86, 6]], '#a8661a', 0.85) + '</g>'
  + [[230, 80], [290, 82]].map(([x, y]) => oval(x, y, 4.4, 3.6, '#2f8fd8') + oval(x + 1.2, y - 1.2, 1.4, 1, '#ffffff', 0.9)).join('');

// ---------- les reflets de l'or (couronne, trident) : des filets clairs, jamais des rayures ----------
const GOLD_HI = [[[180, 70, 0], [192, 50, 3], [198, 40, 0]], [[232, 62, 0], [240, 40, 3], [244, 30, 0]], [[276, 50, 0], [284, 24, 3.4], [288, 10, 0]],
  [[318, 66, 0], [326, 50, 3], [330, 42, 0]], [[410, 210, 0], [440, 150, 3], [452, 110, 0]], [[478, 160, 0], [500, 110, 2.6], [512, 72, 0]],
  [[500, 200, 0], [524, 170, 2.6], [546, 140, 0]], [[60, 392, 0], [200, 320, 3], [330, 262, 0]]];
const goldHi = GOLD_HI.map((g) => glint(g, '#fff6c8', 0.85)).join('');

// ---------- les mèches des cheveux et de la barbe : de longs fuseaux gris-bleu (creux) et blancs (reflets), qui suivent
// le sens des mèches de l'original (vers le bas à gauche pour la crinière, vers le bas pour la barbe), jamais en rangées
const HAIR = [[[150, 110], [118, 150], [84, 190]], [[166, 130], [140, 176], [118, 214]], [[140, 96], [104, 126], [70, 150]], [[176, 160], [160, 200], [150, 236]],
  [[352, 110], [366, 150], [360, 196]], [[340, 140], [348, 180], [338, 216]], [[214, 210], [224, 240], [232, 266]], [[262, 220], [262, 250], [258, 278]],
  [[300, 214], [298, 244], [290, 268]], [[236, 222], [244, 252], [248, 276]]];
const hairStrands = '<g clip-path="url(#m-blanc)">' + HAIR.map((h, i) => glint(h.map(([x, y], k) => [x, y, k === 1 ? 4.4 - (i % 3) : 0]), '#a8b8d4', 0.8)
  + glint(h.map(([x, y], k) => [x + 3, y - 2, k === 1 ? 2.2 : 0]), '#ffffff', 0.9)).join('') + '</g>';

// ---------- les morceaux (la tête, le corps et la cape sont trois parts d'une même silhouette : pas d'ombre entre elles) ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'body', cls: 'a-body', d: sm('523,55 518,54 510,58 471,87 468,95 471,98 475,98 475,101 448,139 432,157 423,144 424,132 435,112 443,111 446,108 446,63 443,61 439,63 421,86 415,91 412,96 415,101 390,133 389,148 393,160 397,166 398,172 409,184 409,190 405,193 407,199 403,204 401,211 398,214 393,211 379,213 372,222 367,232 367,236 363,238 356,232 363,228 363,223 361,221 364,217 360,214 366,208 364,203 335,262 290,286 229,286 172,258 140,240 90,232 75,208 73,210 75,214 73,216 60,218 41,224 27,231 14,243 7,257 5,267 7,289 17,315 18,342 16,345 12,370 13,385 17,392 14,396 14,403 17,409 24,416 33,420 46,410 53,408 71,395 77,395 81,388 85,385 94,383 100,385 91,398 77,428 59,448 56,456 56,463 71,469 88,471 125,470 140,467 145,462 145,452 142,441 162,422 169,429 180,428 186,430 193,426 199,425 202,427 214,426 219,429 228,427 236,430 239,428 251,428 256,425 266,425 275,421 289,419 297,421 304,432 304,436 299,446 299,458 303,462 315,464 332,462 338,466 353,468 374,468 400,463 401,452 398,444 391,440 383,439 374,429 365,425 364,417 365,404 367,401 367,384 364,379 362,357 350,327 351,318 374,288 382,287 388,278 398,278 402,276 404,272 415,262 422,244 422,237 415,227 423,226 427,220 431,219 432,214 439,208 445,206 467,223 472,223 477,218 487,213 503,213 522,183 526,173 529,171 533,175 536,175 544,159 547,148 557,129 555,125 545,128 540,132 509,147 506,151 508,159 486,182 479,185 469,185 460,179 486,142 497,120 501,117 506,122 511,120 516,105 517,93 521,79'), body: clip('body', paint + goldHi + middle) },
  { id: 'head', cls: 'a-head', d: sm('346,44 342,43 335,52 334,38 329,36 326,38 324,47 319,54 311,47 300,42 297,39 293,17 288,5 283,7 272,34 249,31 243,34 233,35 228,23 224,20 220,23 219,31 215,38 208,38 203,41 195,42 185,50 181,50 173,41 168,42 167,50 169,62 164,65 150,81 144,101 146,107 140,112 138,118 133,124 131,134 117,143 96,143 81,150 78,154 77,160 70,168 70,176 84,166 91,171 82,180 80,179 81,177 77,178 78,181 84,184 75,193 72,193 76,198 82,199 75,208 89,231 140,240 172,258 229,286 290,286 334,263 364,203 363,200 366,195 366,185 363,179 353,177 348,172 345,164 345,151 351,143 351,136 354,130 354,110 348,102 348,95 343,88 346,72'), body: clip('head', paint + crown + goldHi + FACE + hairStrands) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : il respire (le corps monte et descend un peu), la tête hoche, la cape ondule, il cligne. Attaque (classe
// « atk », 0,75 s) : il se ramasse puis bondit en avant en pointant le trident ; tout revient à la pose de repos.
const PIV = { head: [260, 280], body: [240, 460], cape: [120, 200] };
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
@keyframes cape{from{transform:none}to{transform:rotate(1.6deg)}}
@keyframes blink{0%,93%{opacity:0}94.5%,97%{opacity:1}98.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-head', 'head-atk')}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-8px,4px) rotate(-3deg)}48%{transform:translate(22px,-6px) rotate(4deg)}62%{transform:translate(18px,-2px) rotate(3deg)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}30%{transform:rotate(-2deg)}48%{transform:rotate(2deg)}100%{transform:none}}
@keyframes cape-atk{0%{transform:none}30%{transform:rotate(3deg)}50%{transform:rotate(-4deg)}100%{transform:none}}
`.replace(/\n/g, '');

function svg(anime = true) {
  const s = figure({ master: SIL, w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'angels-2', w: W, h: H, pad: PAD, foot: [230, 462], svg };
