// Ruka, la sirène chanteuse (demons-7) : redessinée par le code d'après le dessin d'origine, dans le même cadre
// (543 × 485, mêmes proportions, même pose) : longue chevelure rousse aux pointes roses, étoile de mer dorée, visage
// en colère qui chante, coquillages, bras tendu paume ouverte, main sur le cœur, ceinture d'or, queue d'écailles
// turquoise qui se replie vers la gauche, nageoire menthe, deux notes bleues.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 543, H = 485;

// ---------- couleurs ----------
const HAIR = { hi: '#ffc07a', lite: '#ff9550', base: '#f25a2e', deep: '#c22a2a', line: '#8d1c22' };
const SKIN = { hi: '#fff0df', base: '#fcd3b1', shade: '#ec9f81', deep: '#d77f63', line: '#a9573f' };
const GOLD = { hi: '#fff6b8', base: '#f8c842', mid: '#e09c22', shade: '#a8690f', line: '#74440a' };
const TAIL = { hi: '#a8fbf0', base: '#34c4da', mid: '#2893d1', shade: '#1b55a2', line: '#143c7c' };
const FIN = { hi: '#dcfff6', base: '#86e8d4', mid: '#4cc4b6', line: '#2a8f8c' };
// les ombres portées : une teinte par matière qui la reçoit
const SH = { skin: '#c9553a', hair: '#7a1020', tail: '#0d2a66' };
const BACK = ['lockA', 'lockB', 'lockC', 'lockD'];

// ---------- dégradés ----------
const defs = [
  // la chevelure : orange au sommet, rouge au milieu, rose aux pointes (le long de la chute)
  lin('g-hair', 250, 40, 14, 372, [[0, '#ff9148'], [0.22, '#f4582c'], [0.52, '#df3a2e'], [0.76, '#d5335c'], [0.9, '#dc4f9a'], [1, '#f39acb']]),
  lin('g-skin', 0, 0, 0, 1, [[0, '#ffe8d2'], [0.6, SKIN.base], [1, '#f6bf9b']], false),
  lin('g-armL', 0, 246, 0, 340, [[0, '#ffe8d2'], [0.5, SKIN.base], [1, '#f2b08c']]),
  lin('g-armR', 0, 232, 0, 296, [[0, '#ffe8d2'], [0.55, SKIN.base], [1, '#f2b08c']]),
  rad('g-cheekL', 0.3, 0.62, 0.5, [[0, '#fff3e4', 0.9], [1, '#fff3e4', 0]], false),
  lin('g-gold', 0, 0, 0, 1, [[0, GOLD.hi], [0.4, GOLD.base], [1, GOLD.shade]], false),
  lin('g-cuff', 0, 0, 0, 1, [[0, '#fff2a8'], [0.28, '#f9cc48'], [0.72, '#e09a20'], [1, '#9c600c']], false),
  lin('g-tail', 372, 350, 214, 478, [[0, '#7df0e6'], [0.28, '#38c6dc'], [0.6, '#2a8fd2'], [1, '#1c4c9c']]),
  rad('g-tailGlow', 322, 398, 62, [[0, '#c4fff6', 0.55], [1, '#c4fff6', 0]]),
  lin('g-tailRim', 340, 0, 376, 0, [[0, '#eefb9c', 0], [0.5, '#eefb9c', 0.5], [1, '#fbffc8', 0.95]]),
  lin('g-frill', 0, 0, 0, 1, [[0, '#e3d2f8'], [1, '#9d7bd0']], false),
  lin('g-fin', 207, 452, 50, 372, [[0, '#3fb3ac'], [0.3, '#6edbc8'], [0.75, '#a5f4e0'], [1, '#d6fff3']]),
  lin('g-shell', 0, 0, 0, 1, [[0, '#ffffff'], [0.45, '#cfe6fd'], [1, '#7fa9ea']], false),
  lin('g-note', 0, 0, 0, 1, [[0, '#8fbcff'], [0.5, '#4a69ea'], [1, '#2b3bb0']], false),
  rad('g-iris', 0.5, 0.78, 0.8, [[0, '#a6fbf4'], [0.42, '#2bc4e2'], [0.8, '#12789f'], [1, '#0b4f73']], false),
  rad('g-blush', 0.5, 0.5, 0.5, [[0, '#ff7f86', 0.55], [1, '#ff7f86', 0]], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#1a2a4a', 0.6], [0.42, '#1a2a4a', 0]], false),
  lin('g-mouth', 0, 0, 0, 1, [[0, '#4d0f22'], [1, '#8a1f33']], false),
  lin('g-tailTop', 0, 362, 0, 404, [[0, '#0d2a66', 0.55], [1, '#0d2a66', 0]]),
  lin('g-beltSh', 0, 0, 0, 1, [[0.5, '#8a4a08', 0], [1, '#8a4a08', 0.55]], false),
  lin('g-beltL', 203, 0, 282, 0, [[0, '#8a4a08', 0.5], [1, '#8a4a08', 0]]),
  // une lumière douce, pour arrondir une épaule ou une joue
  rad('g-soft', 0.5, 0.5, 0.5, [[0, '#fff6ea', 0.85], [1, '#fff6ea', 0]], false),
].join('');

// ---------- silhouettes ----------
const S = {
  // la grande chevelure, derrière : quatre grandes mèches qui se recouvrent, de l'extérieur vers le corps
  lockA: 'M170 56 L152 76 C140 96 124 124 112 152 C100 182 90 222 78 252 C70 274 58 292 42 304 C30 313 19 318 8 321 C14 335 30 351 50 359 C90 330 124 280 146 230 C162 190 180 140 204 90 Z',
  lockB: 'M186 70 C168 112 152 156 134 204 C118 246 98 290 74 324 C60 344 45 360 28 372 C38 379 51 383 64 383 C106 350 140 300 164 248 C182 204 200 150 228 90 Z',
  lockC: 'M208 80 C188 134 172 188 152 242 C134 290 112 334 86 370 C76 384 66 394 56 401 C66 405 77 406 89 403 L122 420 L172 440 C188 380 202 300 216 240 L228 104 Z',
  lockD: 'M224 120 C214 180 204 240 190 300 C180 344 168 384 154 420 L190 446 L205 440 C209 424 209 400 205 378 L240 330 L250 200 Z',
  // la nageoire : deux lobes
  fin: 'M207 443 C196 431 176 411 151 382 C133 364 109 349 88 331 C85 352 86 381 78 408 C58 420 34 432 12 444 C10 448 11 452 16 456 C12 461 14 467 19 471 C46 471 78 476 108 476 C138 476 164 468 184 464 C192 462 200 461 207 462 Z',
  // la queue : elle descend de la taille, se replie et repart vers la gauche
  tail: 'M204 352 C203 366 204 378 208 385 C228 396 254 410 272 426 C254 432 230 437 207 442 L207 462 C232 472 270 479 303 473 C340 465 367 438 370 404 C372 376 364 352 348 336 Z',
  torso: 'M228 248 C254 242 310 244 338 258 C340 284 340 312 342 340 L346 366 L206 372 C201 340 202 292 207 270 C210 258 218 252 228 248 Z',
  // la chevelure de droite : elle tombe sur l'épaule, passe derrière le bras et ressort en trois pointes
  hairR: 'M366 170 L394 170 C394 190 390 212 384 228 C381 240 379 248 380 256 L394 298 C408 304 419 320 421 341 C417 335 413 331 408 328 C409 338 408 346 406 353 C401 346 397 339 393 333 C391 338 388 341 385 344 C381 336 372 330 362 326 L352 340 L340 336 C337 316 334 290 334 264 C334 250 338 240 344 234 L372 226 Z',
  frill: 'M204 360 L350 348 L352 362 C351 370 345 373 339 371 C337 379 328 383 320 379 C316 387 304 389 297 384 C292 391 279 392 272 386 C266 392 253 391 247 385 C241 389 229 387 225 381 C218 383 209 379 206 373 Z',
  belt: 'M203 344 C236 358 300 358 347 337 L350 361 C304 381 240 380 204 370 Z',
  shellL: 'M272 299 C262 298 250 290 248 280 C246 274 250 268 256 270 C257 264 266 261 270 266 C274 261 284 262 286 268 C292 266 297 272 296 279 C295 289 284 298 272 299 Z',
  shellR: 'M313 302 C304 300 297 292 297 283 C296 277 300 272 305 274 C307 268 315 266 318 271 C322 267 331 269 332 275 C337 276 339 283 336 289 C333 297 323 303 313 302 Z',
  // le bras tendu : avant-bras, main ouverte, grand bracelet d'or
  farmR: 'M392 261 C410 259 426 259 441 259 L445 282 C430 287 412 292 392 296 Z',
  handR: 'M441 259 C446 257 450 253 453 248 C456 240 462 231 468 228 C473 226 477 228 477 233 C477 238 474 242 471 246 C482 244 495 239 505 236 C510 234 515 236 515 240 C515 242 514 243 512 244 C516 244 519 247 518 250 C518 253 516 254 513 255 C516 256 517 259 516 262 C515 264 512 265 510 264 C512 268 510 272 505 273 C492 277 474 282 459 284 C453 284 448 284 445 282 Z',
  cuff: 'M374 253 C382 251 392 253 397 256 C402 267 402 288 397 300 C391 303 382 303 374 301 C369 288 369 266 374 253 Z',
  // le bras replié, le poing sur le cœur
  armL: 'M240 256 C236 248 222 245 211 252 C201 259 196 274 197 290 C198 304 204 315 213 322 C223 329 237 333 251 335 C267 337 283 338 296 337 L298 301 C284 301 268 302 254 302 C246 302 240 299 237 293 C235 280 236 268 240 256 Z',
  handL: 'M286 303 C289 297 298 294 306 295 C313 294 321 297 324 302 C328 304 330 309 328 313 C331 316 331 322 328 325 C329 329 327 334 322 335 C319 339 311 340 304 339 C296 340 289 338 286 333 C282 327 282 312 286 303 Z',
  thumbL: 'M288 305 C292 299 302 296 310 299 C314 301 315 306 311 308 C304 307 296 308 290 311 C287 310 287 307 288 305 Z',
  // la tête
  ear: 'M188 147 C177 138 162 144 161 160 C160 176 167 189 179 191 C186 192 191 186 191 178 Z',
  face: 'M206 118 L206 152 C204 172 205 192 211 207 C219 224 233 238 252 247 C268 254 285 257 300 257 C317 257 338 252 356 240 C372 229 384 210 387 186 L388 118 L340 60 Z',
  lock: 'M194 128 C188 148 187 170 190 190 C192 202 198 208 200 220 C202 236 196 248 187 257 C200 254 211 243 213 228 C215 214 208 204 206 190 C204 174 207 150 213 128 Z',
  cap: 'M141 112 C143 63 198 13 276 10 C337 8 391 45 396 104 C398 130 397 160 393 186 C390 206 385 224 379 238 L369 240 C377 222 383 200 384 176 C385 160 383 146 379 134 C367 116 353 96 345 80 L340 62 C334 84 320 104 296 114 C272 124 244 128 222 130 C212 131 204 134 199 139 C188 132 170 131 157 138 C149 142 144 150 141 160 C137 146 138 128 141 112 Z',
  star: 'M203 40 L204 71 L235 72 L209 92 L218 124 L188 107 L158 119 L169 92 L147 74 L179 68 Z',
  note1: 'M450 128 C450 124 463 122 463 126 L489 141 C493 146 491 152 486 154 L464 142 L465 178 C466 189 456 196 444 197 C432 198 422 191 422 182 C422 172 433 165 444 165 C447 165 449 165 451 166 Z',
  note2: 'M518 52 C518 47 533 47 533 52 L534 100 C535 113 524 121 511 122 C497 123 487 115 487 105 C487 94 499 86 512 86 C515 86 517 86 519 87 Z',
};

// ---------- les écailles ----------
/** Des rangées d'écailles en quinconce, en arcs autour d'un point haut : la queue paraît ronde. */
function scales() {
  const CX = 318, CY = 40, DR = 13.2, DA = (3.5 * Math.PI) / 180;
  const at = (a, r) => [CX + Math.sin(a) * r, CY + Math.cos(a) * r];
  let rim = '', glow = '', shade = '';
  let row = 0;
  for (let r = 322; r < 470; r += DR, row++) {
    for (let k = -16; k <= 12; k++) {
      const a = (k + (row % 2 ? 0.5 : 0)) * DA;
      const [tx, ty] = at(a, r);
      if (tx < 188 || tx > 388 || ty < 352 || ty > 492) continue;
      const u = (rr, sh = 0) => {
        const [x1, y1] = at(a - DA / 2, rr - DR * 0.92 + sh), [x2, y2] = at(a + DA / 2, rr - DR * 0.92 + sh);
        const [c1x, c1y] = at(a - DA / 2, rr + DR * 0.3 + sh), [c2x, c2y] = at(a + DA / 2, rr + DR * 0.3 + sh);
        return `M${n(x1)} ${n(y1)}C${n(c1x)} ${n(c1y)} ${n(c2x)} ${n(c2y)} ${n(x2)} ${n(y2)}`;
      };
      rim += u(r);
      shade += u(r, 2.6);
      // le reflet : un petit arc à l'intérieur du bord, du côté de la lumière
      const [h1x, h1y] = at(a - DA * 0.08, r - DR * 0.3), [hcx, hcy] = at(a + DA * 0.3, r - DR * 0.24), [h2x, h2y] = at(a + DA * 0.36, r - DR * 0.62);
      glow += `M${n(h1x)} ${n(h1y)}Q${n(hcx)} ${n(hcy)} ${n(h2x)} ${n(h2y)}`;
    }
  }
  return `<path d="${shade}" fill="none" stroke="${TAIL.line}" stroke-width="4.4" opacity="0.16"/>`
    + `<path d="${rim}" fill="none" stroke="${TAIL.line}" stroke-width="1.6" opacity="0.55"/>`
    + `<path d="${glow}" fill="none" stroke="#d8fffa" stroke-width="1.9" opacity="0.7"/>`;
}

// ---------- les yeux ----------
/**
 * Un œil : blanc, iris en dégradé, pupille, ombre de la paupière, reflets ; puis les cils (une forme pleine) et la
 * paupière du bas. `shut` = la courbe de l'œil fermé (clignement).
 */
function eye(key, white, cx, cy, r, lash, lower, shut) {
  return `<clipPath id="c-${key}"><path d="${white}"/></clipPath>`
    + `<path d="${white}" fill="#fff"/>`
    + `<g clip-path="url(#c-${key})">`
    + `<circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#g-iris)"/>`
    + `<circle cx="${cx}" cy="${cy}" r="${r - 1}" fill="none" stroke="#083a58" stroke-width="2.2"/>`
    + dot(cx, n(cy - r * 0.06), n(r * 0.46), '#062033')
    + `<path d="M${n(cx - r * 0.7)} ${n(cy + r * 0.45)} A${n(r * 0.84)} ${n(r * 0.84)} 0 0 0 ${n(cx + r * 0.7)} ${n(cy + r * 0.45)}" fill="none" stroke="#d2fffb" stroke-width="2.2" opacity="0.8"/>`
    + `<rect x="${cx - r - 16}" y="${cy - r - 10}" width="${2 * r + 32}" height="${n(r * 1.5)}" fill="url(#g-lid)"/>`
    + dot(n(cx - r * 0.44), n(cy - r * 0.42), n(r * 0.27), '#fff')
    + dot(n(cx + r * 0.42), n(cy + r * 0.2), n(r * 0.13), '#fff', 0.95)
    + `</g>`
    + shape(lash, '#1e0d22') + line(lower, '#5a2f2c', 1.7, 0.9)
    + `<g class="a-blink" opacity="0"><path d="${white}" fill="#f6c3a2" stroke="#f6c3a2" stroke-width="3"/>${line(shut, '#1e0d22', 3.4)}</g>`;
}

/** Une grande mèche de la chevelure : sa couleur, une nappe claire du côté de la lumière, le liseré rose de sa pointe. */
const backLock = (id, glow, tip, extra = '') => use(id, 'url(#g-hair)') + clip(id, glow + (tip ? shape(tip, '#ffd6ea', 0.85) : '') + extra);

// ---------- les morceaux, du fond vers le devant ----------
const parts = [
  // --- la grande chevelure : quatre mèches, chacune fait de l'ombre sur la précédente ---
  { id: 'lockA', cls: 'a-hl', d: S.lockA,
    body: backLock('lockA', shape('M128 132 C116 170 102 212 84 252 C104 220 120 180 132 142 Z', HAIR.hi, 0.6), 'M10 321 C22 320 33 314 44 305 C35 318 22 326 12 327 Z') },
  { id: 'lockB', cls: 'a-hl', d: S.lockB, shadow: [{ on: ['lockA'], dx: -7, dy: 1, color: SH.hair, o: 0.24 }],
    body: backLock('lockB', shape('M168 122 C154 168 136 220 106 276 C134 238 156 186 172 130 Z', HAIR.lite, 0.75), 'M30 372 C40 369 50 362 58 354 C52 366 42 374 33 376 Z') },
  { id: 'lockC', cls: 'a-hl', d: S.lockC, shadow: [{ on: ['lockA', 'lockB'], dx: -7, dy: 1, color: SH.hair, o: 0.24 }],
    body: backLock('lockC', shape('M178 226 C168 264 148 308 118 352 C150 316 172 270 182 232 Z', HAIR.lite, 0.6), 'M58 401 C66 396 74 388 82 378 C78 390 70 400 62 404 Z') },
  { id: 'lockD', cls: 'a-hl', d: S.lockD, shadow: [{ on: ['lockC'], dx: -7, dy: 1, color: SH.hair, o: 0.24 }],
    body: backLock('lockD', '', '', `<path d="${S.lockD}" fill="#8f1422" opacity="0.3"/>`) },

  // --- la nageoire : membrane menthe, trois grands plis, reflets ---
  { id: 'fin', cls: 'a-fin', d: S.fin,
    body: use('fin', 'url(#g-fin)') + clip('fin',
      // les plis de la membrane : de larges éventails plus sombres, effilés vers la racine
      shape('M206 447 C172 420 136 388 104 352 C126 388 164 426 205 453 Z', FIN.line, 0.4)
      + shape('M206 451 C160 444 116 430 78 408 C108 440 160 452 205 457 Z', FIN.line, 0.55)
      + shape('M205 457 C150 458 92 462 30 458 C92 472 150 468 205 461 Z', FIN.line, 0.35)
      // la racine, dans l'ombre de la queue
      + shape('M207 443 C196 440 188 446 188 452 C188 458 196 462 207 462 Z', '#1f7f80', 0.55)
      // le bord de fuite, plus clair et presque transparent
      + shape('M88 331 C85 352 86 381 78 408 L86 404 C93 382 93 356 94 338 Z', FIN.hi, 0.85)
      + shape('M12 444 C10 448 11 452 16 456 C12 461 14 467 19 471 L28 470 C24 464 24 456 27 448 Z', FIN.hi, 0.7)
      // deux grandes nappes de lumière
      + shape('M100 346 C122 368 148 394 178 426 C150 404 122 384 98 362 Z', FIN.hi, 0.7)
      + shape('M34 446 C76 438 122 440 164 450 C122 447 76 448 32 452 Z', FIN.hi, 0.65)
    ) },

  // --- la queue : écailles turquoise, reflet doré sur le galbe ---
  { id: 'tail', d: S.tail, shadow: [{ on: ['fin'], dx: -6, dy: 0, color: '#1f7f80', o: 0.35 }],
    body: use('tail', 'url(#g-tail)') + clip('tail',
      `<circle cx="322" cy="398" r="62" fill="url(#g-tailGlow)"/>`
      + scales()
      + `<rect x="196" y="350" width="190" height="56" fill="url(#g-tailTop)"/>`
      // le creux du repli et le dessous de la queue, dans l'ombre
      + shape('M208 385 C228 396 254 410 272 426 C254 432 230 437 207 442 L207 448 C234 444 262 438 286 428 C266 410 238 394 210 380 Z', '#0d2a66', 0.45)
      + shape('M207 462 C232 472 270 479 303 473 C330 467 352 450 364 428 C348 452 322 466 296 468 C264 470 232 464 207 454 Z', '#0d2a66', 0.38)
      + `<rect x="336" y="330" width="40" height="150" fill="url(#g-tailRim)"/>`
    ) },

  // --- le torse ---
  { id: 'torso', d: S.torso, shadow: [{ on: BACK, dx: -5, dy: 3, color: SH.hair, o: 0.3 }],
    body: use('torso', 'url(#g-skin)') + line('M293 262 C294 268 294 273 293 278', SKIN.line, 1.5, 0.6) },
  { id: 'hairR', cls: 'a-hr', d: S.hairR, shadow: [{ on: ['torso'], dx: -4, dy: 3, color: SH.skin, o: 0.4 }],
    body: use('hairR', 'url(#g-hair)') + clip('hairR',
      // près du cou, la chevelure est dans l'ombre de la tête
      shape('M334 264 C334 250 338 240 344 234 L369 238 C372 246 374 252 375 258 L376 300 L386 300 C372 316 356 330 340 336 Z', SH.hair, 0.42)
      + shape('M398 304 C409 312 416 324 419 337 C417 322 411 310 403 301 Z', HAIR.lite, 0.9)
      + shape('M388 304 C396 316 402 332 405 348 C406 330 402 314 394 300 Z', HAIR.lite, 0.5)
      + shape('M393 333 C389 322 382 312 373 304 C381 316 386 327 389 339 Z', HAIR.line, 0.5)
      + shape('M408 328 C405 318 399 308 391 300 C399 312 403 320 405 332 Z', HAIR.line, 0.5)
      + shape('M352 262 C346 280 344 300 348 320 C352 300 354 282 358 264 Z', HAIR.line, 0.4)
    ) },
  { id: 'frill', d: S.frill, shadow: [{ on: ['tail'], dx: -2, dy: 5, color: SH.tail, o: 0.38 }],
    body: use('frill', 'url(#g-frill)')
      + line('M339 371 C340 366 340 362 339 358 M320 379 C321 373 321 368 320 363 M297 384 C298 378 298 372 297 367 M272 386 C273 380 273 374 272 369 M247 385 C248 379 248 374 247 369 M225 381 C226 376 226 372 225 368', '#7c5ab0', 1.5, 0.55) },
  { id: 'belt', d: S.belt, shadow: [{ on: ['frill', 'tail'], dx: -1, dy: 5, color: '#4a2a7c', o: 0.35 }],
    body: use('belt', 'url(#g-gold)') + clip('belt',
      `<path d="${S.belt}" fill="url(#g-beltSh)"/>`
      + shape('M203 344 C236 358 300 358 347 337 L348 343 C300 364 236 364 203 350 Z', GOLD.hi, 0.9)
      + `<rect x="200" y="340" width="90" height="44" fill="url(#g-beltL)"/>`
    ) + line('M205 365 C240 375 302 375 349 356', GOLD.line, 1.4, 0.45) },
  { id: 'shellL', d: S.shellL, shadow: [{ on: ['torso'], dx: -3, dy: 4, color: SH.skin, o: 0.4 }],
    body: use('shellL', 'url(#g-shell)')
      + line('M272 297 L252 279 M272 297 L260 270 M272 297 L271 267 M272 297 L283 269 M272 297 L293 278', '#6f97dc', 1.5, 0.75)
      + shape('M250 279 C249 273 252 270 256 272 C258 266 265 264 269 268 C264 268 260 270 258 275 C254 274 251 276 250 279 Z', '#fff', 0.95)
      + shape('M272 299 C262 298 252 291 249 283 C256 290 264 294 272 294 C282 294 291 288 296 280 C294 290 284 298 272 299 Z', '#5f8ad4', 0.4) },
  { id: 'shellR', d: S.shellR, shadow: [{ on: ['torso', 'shellL'], dx: -3, dy: 4, color: SH.skin, o: 0.4 }],
    body: use('shellR', 'url(#g-shell)')
      + line('M313 300 L300 282 M313 300 L307 274 M313 300 L318 271 M313 300 L329 276 M313 300 L336 288', '#6f97dc', 1.5, 0.75)
      + shape('M299 283 C298 278 301 274 305 276 C307 270 314 268 317 272 C312 272 309 275 307 279 C303 278 300 280 299 283 Z', '#fff', 0.95)
      + shape('M313 302 C304 300 298 294 297 286 C302 292 308 296 315 296 C324 296 332 291 337 284 C336 294 324 303 313 302 Z', '#5f8ad4', 0.4) },

  // --- le bras tendu ---
  { id: 'farmR', cls: 'a-arm', d: S.farmR, shadow: [{ on: ['hairR'], dx: -3, dy: 6, color: SH.hair, o: 0.4 }],
    body: use('farmR', 'url(#g-armR)') + clip('farmR',
      shape('M392 286 C412 283 430 279 446 273 L446 300 L392 300 Z', SKIN.shade, 0.5)
      + shape('M400 263 C412 262 426 262 438 262 C426 265 412 266 400 267 Z', SKIN.hi, 0.9)
    ) },
  { id: 'handR', cls: 'a-arm', d: S.handR, body: use('handR', 'url(#g-armR)') + clip('handR',
    // le dessous de la main et l'ombre du pouce sur la paume
    shape('M445 275 C468 278 490 272 508 264 L510 278 L445 290 Z', SKIN.shade, 0.5)
    + shape('M453 248 C458 253 461 258 461 265 C466 258 470 252 471 246 C466 250 459 251 453 248 Z', SKIN.shade, 0.45)
    + shape('M464 234 C467 230 472 229 474 232 C470 234 467 238 466 243 Z', SKIN.hi, 0.9)
    + shape('M478 252 C487 249 496 246 504 243 C496 250 487 254 478 256 Z', SKIN.hi, 0.8)
  )
    // les doigts, le pli du pouce, la ligne de la paume
    + line('M512 244 C504 247 496 251 489 254', SKIN.line, 1.5)
    + line('M513 255 C505 258 498 260 491 262', SKIN.line, 1.5)
    + line('M510 264 C504 266 498 268 493 269', SKIN.line, 1.5)
    + line('M471 247 C467 252 463 258 461 264', SKIN.line, 1.5)
    + line('M465 272 C472 268 481 267 488 269', SKIN.line, 1.3, 0.6)
    // le bracelet de perles
    + [262, 266.6, 271.2, 275.8, 280.4].map((y, i) => dot(n(441.8 + i * 0.8), y, 2.7, '#8a5a3c') + dot(n(441.8 + i * 0.8), y, 1.9, '#fff4dc') + dot(n(442.3 + i * 0.8), y - 0.6, 0.7, '#fff')).join('') },
  { id: 'cuff', cls: 'a-arm', d: S.cuff, shadow: [{ on: ['hairR'], dx: -4, dy: 5, color: SH.hair, o: 0.4 }, { on: ['farmR'], dx: 4, dy: 2, color: SH.skin, o: 0.35 }],
    body: use('cuff', 'url(#g-cuff)') + clip('cuff',
      shape('M374 253 C379 252 383 252 386 253 C382 266 382 288 386 302 C382 303 378 302 374 301 C369 288 369 266 374 253 Z', '#fff7c0', 0.55)
      + shape('M392 254 C394 254 396 255 397 256 C402 267 402 288 397 300 C396 301 394 302 392 302 C396 290 396 266 392 254 Z', GOLD.shade, 0.5)
      + shape('M370 289 C380 293 392 293 402 289 L402 306 L370 306 Z', GOLD.shade, 0.35)
      + line('M378 259 C376 268 376 280 378 290', '#fffbe0', 2.2, 0.95)
    ) },

  // --- le bras replié, le poing sur le cœur ---
  { id: 'armL', d: S.armL, rim: { on: ['torso'], color: SKIN.line, w: 1.2, o: 0.75 },
    shadow: [{ on: ['torso', 'shellL'], dx: -1, dy: 5, color: SH.skin, o: 0.42 }, { on: BACK, dx: -5, dy: 3, color: SH.hair, o: 0.3 }],
    body: use('armL', 'url(#g-armL)') + clip('armL',
      // le dessous de l'avant-bras, le dehors et l'intérieur du bras
      shape('M198 295 C200 307 205 316 213 322 C223 329 237 333 251 335 C267 337 283 338 296 337 L296 328 C280 329 262 328 246 325 C230 322 214 314 204 300 Z', SKIN.shade, 0.6)
      + shape('M211 252 C201 259 196 274 197 290 C198 300 201 309 206 315 C203 300 204 284 208 270 C210 263 214 257 219 252 Z', SKIN.shade, 0.4)
      + shape('M240 256 C236 266 235 280 237 293 C231 288 229 276 231 264 Z', SKIN.shade, 0.4)
      + oval(219, 270, 11, 17, 'url(#g-soft)', 1, 14)
      // le bracelet d'or
      + `<path d="M257 295 C249 308 248 326 253 343" fill="none" stroke="${GOLD.line}" stroke-width="8"/>`
      + `<path d="M257 295 C249 308 248 326 253 343" fill="none" stroke="${GOLD.base}" stroke-width="5.4"/>`
      + `<path d="M253 303 C250 311 249 319 250 327" fill="none" stroke="${GOLD.hi}" stroke-width="1.8"/>`
    ) },
  { id: 'handL', d: S.handL, rim: { on: ['torso', 'shellL', 'shellR', 'belt'], color: SKIN.line, w: 1.2, o: 0.75 },
    shadow: [{ on: ['torso', 'shellL', 'shellR', 'belt'], dx: -2, dy: 5, color: SH.skin, o: 0.4 }],
    body: use('handL', 'url(#g-armL)') + clip('handL',
      shape('M286 333 C289 338 296 340 304 339 C311 340 319 339 322 335 C327 334 329 329 328 325 C322 331 312 334 302 333 C294 333 288 329 285 322 C284 326 284 330 286 333 Z', SKIN.shade, 0.6)
    )
    // les phalanges : deux petits traits au bord du poing
    + line('M328 313 C324 312 320 312 316 313', SKIN.line, 1.5)
    + line('M328 325 C324 323 320 323 316 324', SKIN.line, 1.5) },
  // le pouce, posé sur le dessus du poing
  { id: 'thumbL', d: S.thumbL, rim: { on: ['handL'], color: SKIN.line, w: 1.2, o: 0.75 },
    shadow: [{ on: ['handL'], dx: -1, dy: 3, color: SH.skin, o: 0.35 }],
    body: use('thumbL', 'url(#g-armL)') + oval(300, 302, 6, 2.4, 'url(#g-soft)', 1, -8) },

  // --- la tête ---
  { id: 'ear', d: S.ear, shadow: [{ on: BACK, dx: -4, dy: 3, color: SH.hair, o: 0.32 }],
    body: use('ear', 'url(#g-skin)')
      + shape('M184 152 C175 147 167 153 167 163 C167 174 172 183 179 185 C174 178 172 170 173 163 C174 157 178 153 184 152 Z', SKIN.shade, 0.7)
      + line('M183 158 C178 160 176 166 178 172', SKIN.line, 1.6, 0.7) },
  { id: 'face', d: S.face, rim: { on: ['torso', 'armL'], color: SKIN.line, w: 1.2, o: 0.6 },
    shadow: [{ on: ['torso', 'armL', 'shellL', 'shellR'], dx: -2, dy: 8, color: SH.skin, o: 0.42 }, { on: ['hairR', ...BACK], dx: -3, dy: 7, color: SH.hair, o: 0.38 }],
    body: use('face', 'url(#g-skin)') + clip('face',
      `<rect x="200" y="140" width="110" height="110" fill="url(#g-cheekL)"/>`
      + oval(238, 198, 24, 15, 'url(#g-blush)') + oval(366, 199, 19, 14, 'url(#g-blush)')
    )
    // les peintures de guerre des joues
    + line('M228 180 L236 198 M236 176 L246 200 M245 180 L251 195', '#e8566e', 4.6, 0.85)
    + line('M359 187 L364 199 M366 185 L371 196', '#e8566e', 4.4, 0.85)
    // les yeux
    + eye('eL', 'M233 158 C238 149 254 143 270 144 C281 145 289 150 292 158 C293 166 291 174 287 178 C277 184 257 184 245 178 C237 173 232 166 233 158 Z', 268, 166.5, 17,
      'M220 141 C226 146 231 149 236 150 C246 141 260 136 274 137 C286 138 294 146 296 157 C297 163 296 169 294 174 C292 166 288 158 282 153 C272 146 254 147 242 155 C239 157 236 161 234 166 C232 161 229 157 226 155 L218 155 L224 151 C222 148 221 144 220 141 Z',
      'M240 178 C252 185 274 185 288 178', 'M234 166 C248 177 276 177 293 164')
    + eye('eR', 'M329 159 C333 151 346 146 358 147 C367 148 373 152 375 159 C376 167 374 174 370 178 C361 184 345 184 336 178 C331 173 328 166 329 159 Z', 349, 168.5, 15.5,
      'M389 141 C384 146 380 150 376 151 C368 143 356 139 345 140 C335 141 328 148 326 158 C325 164 326 169 328 174 C330 166 333 160 338 155 C347 148 362 149 372 156 C375 158 377 162 378 166 C380 162 382 158 384 156 L391 156 L386 152 C387 149 388 145 389 141 Z',
      'M335 178 C345 185 361 185 371 178', 'M327 166 C340 177 362 177 377 166')
    // les sourcils froncés, la petite cicatrice du front
    + shape('M245 125 C263 126 286 135 305 145 C308 149 307 155 303 157 C286 149 264 140 244 136 C240 133 241 127 245 125 Z', '#9a1e26')
    + shape('M377 126 C362 129 343 138 327 147 C324 151 325 156 329 158 C344 150 362 142 379 137 C383 134 381 128 377 126 Z', '#9a1e26')
    + line('M248 128 C264 130 282 137 299 145', '#d2504a', 1.6, 0.7) + line('M375 129 C361 133 346 139 333 147', '#d2504a', 1.6, 0.7)
    + line('M312 124 L327 133 M322 122 L317 135', '#6b2a22', 2.2, 0.85)
    // le nez : une seule touche d'ombre
    + oval(320.5, 189.5, 2.6, 1.9, '#c9705a', 0.85, -12)
    // la bouche grande ouverte : elle chante
    + `<g class="a-mouth"><clipPath id="c-mouth"><path id="s-mouth" d="M283 203 C298 198 319 199 335 203 C336 216 330 232 318 242 C310 249 294 249 287 242 C279 234 275 218 283 203 Z"/></clipPath>`
    + `<use href="#s-mouth" fill="url(#g-mouth)"/>`
    + `<g clip-path="url(#c-mouth)">`
    + oval(302, 240, 17, 11, '#f47f86') + shape('M290 236 C296 231 308 231 314 236 C308 234 296 234 290 236 Z', '#ffb0b0', 0.8) + line('M302 234 L303 248', '#c9505c', 1.5)
    + shape('M279 200 C296 195 320 196 339 200 L336 212 C320 207 298 206 281 212 Z', '#fff') + line('M282 212 C298 207 320 208 336 213', '#b8c4e0', 1.6, 0.8)
    + `</g><use href="#s-mouth" fill="none" stroke="#3d0d1c" stroke-width="2.4"/></g>` },
  { id: 'lock', cls: 'a-lock', d: S.lock, shadow: [{ on: ['face', 'ear'], dx: -3, dy: 3, color: SH.skin, o: 0.38 }, { on: BACK, dx: -4, dy: 3, color: SH.hair, o: 0.3 }],
    body: use('lock', 'url(#g-hair)')
      + shape('M200 140 C196 158 195 176 198 192 C200 202 206 210 208 222 C209 232 206 242 200 250 C204 240 204 230 202 222 C199 210 193 204 192 192 C190 176 194 156 200 140 Z', HAIR.hi, 0.75) },
  { id: 'cap', d: S.cap, shadow: [{ on: ['face', 'ear'], dx: -3, dy: 8, color: SH.skin, o: 0.36 }, { on: BACK, dx: -3, dy: 7, color: SH.hair, o: 0.3 }],
    body: use('cap', 'url(#g-hair)') + clip('cap',
      // le bord droit, dans l'ombre de la tête
      shape('M345 80 C353 96 367 116 379 134 C383 146 385 160 384 176 C383 200 377 222 369 240 L379 238 C391 206 398 150 396 104 C386 96 366 86 345 80 Z', HAIR.deep, 0.32)
      // la grande lumière du dessus de la tête
      + shape('M190 78 C206 46 240 24 284 18 C254 34 228 56 212 86 C204 86 196 82 190 78 Z', HAIR.hi, 0.55)
      // la raie et les mèches de la frange : des formes effilées, pas des traits
      + shape('M340 62 C334 84 320 104 296 114 C272 124 244 128 222 130 C246 124 272 116 292 106 C314 96 330 82 340 62 Z', HAIR.line, 0.45)
      + shape('M340 62 C344 76 352 92 364 110 C354 98 346 86 340 62 Z', HAIR.line, 0.5)
      + shape('M336 42 C318 68 288 92 246 106 C292 96 324 72 336 42 Z', HAIR.line, 0.3)
      + shape('M352 40 C368 60 382 86 388 118 C386 88 374 62 352 40 Z', HAIR.line, 0.3)
      // le reflet brillant : un croissant en travers des mèches, et son écho
      + shape('M228 98 C250 68 292 53 332 55 C300 66 264 82 228 98 Z', '#ffe2b8', 0.9)
      + shape('M356 58 C374 70 385 90 388 114 C380 98 370 86 362 78 C362 70 360 64 356 58 Z', '#ffe2b8', 0.85)
    ) },
  { id: 'star', d: S.star, shadow: [{ on: ['cap', 'ear', 'lock', ...BACK], dx: -3, dy: 5, color: SH.hair, o: 0.4 }],
    body:
      // chaque branche a une face claire et une face dans l'ombre, de part et d'autre de son arête
      shape('M188 86 L179 68 L203 40 Z', '#fff2a8') + shape('M188 86 L203 40 L204 71 Z', '#f2bd3e')
      + shape('M188 86 L204 71 L235 72 Z', '#ffe072') + shape('M188 86 L235 72 L209 92 Z', '#cf9020')
      + shape('M188 86 L209 92 L218 124 Z', '#f0b838') + shape('M188 86 L218 124 L188 107 Z', '#b97a16')
      + shape('M188 86 L188 107 L158 119 Z', '#dea02a') + shape('M188 86 L158 119 L169 92 Z', '#b6780f')
      + shape('M188 86 L169 92 L147 74 Z', '#e8ad32') + shape('M188 86 L147 74 L179 68 Z', '#ffe98f')
      + line('M188 86 L203 40 M188 86 L235 72 M188 86 L218 124 M188 86 L158 119 M188 86 L147 74', '#fff8d0', 1.3, 0.8)
      + dot(188, 86, 3, '#fff8d0') },

  // --- les notes de son chant ---
  { id: 'note1', cls: 'a-n1', d: S.note1, body: use('note1', 'url(#g-note)')
    + oval(439, 177, 10, 6, '#c4e6ff', 0.9, -18) + line('M455 131 L457 164', '#c4e6ff', 2.6, 0.8) + line('M467 130 L486 141', '#c4e6ff', 2.4, 0.75) },
  { id: 'note2', cls: 'a-n2', d: S.note2, body: use('note2', 'url(#g-note)')
    + oval(506, 100, 11, 7, '#c4e6ff', 0.9, -16) + line('M523 55 L525 88', '#c4e6ff', 3, 0.8) },
];

// ---------- la vie au repos : la chevelure ondule, la nageoire bat, le bras accompagne le chant, les notes flottent ----------
const style = `
.a-hl{transform-origin:210px 110px;animation:hl 4.4s ease-in-out infinite alternate}
.a-hr{transform-origin:386px 230px;animation:hr 3.6s ease-in-out infinite alternate}
.a-lock{transform-origin:203px 130px;animation:hr 3.2s ease-in-out infinite alternate}
.a-fin{transform-origin:207px 452px;animation:fin 2.6s ease-in-out infinite alternate}
.a-arm{transform-origin:372px 278px;animation:arm 2.2s ease-in-out infinite alternate}
.a-mouth{transform-origin:308px 202px;animation:mouth 1.1s ease-in-out infinite alternate}
.a-n1{animation:note 2.4s ease-in-out infinite alternate}
.a-n2{animation:note 2.4s ease-in-out -1.2s infinite alternate}
.a-blink{animation:blink 4.6s linear infinite}
@keyframes hl{from{transform:rotate(-0.8deg)}to{transform:rotate(1.1deg)}}
@keyframes hr{from{transform:rotate(-1.5deg)}to{transform:rotate(1.5deg)}}
@keyframes fin{from{transform:rotate(-3.5deg)}to{transform:rotate(3deg)}}
@keyframes arm{from{transform:rotate(-1.6deg)}to{transform:rotate(1.8deg)}}
@keyframes mouth{from{transform:scale(1,0.88)}to{transform:scale(1,1.04)}}
@keyframes note{from{transform:translate(0,3px) rotate(-3deg)}to{transform:translate(2px,-7px) rotate(4deg)}}
@keyframes blink{0%,93%{opacity:0}94.5%,97%{opacity:1}98.5%,100%{opacity:0}}
`.replace(/\n/g, '');

module.exports = { id: 'demons-7', w: W, h: H, pad: 24, svg: (anime = true) => figure({ w: W, h: H, pad: 24, defs, style, parts, anime }) };
