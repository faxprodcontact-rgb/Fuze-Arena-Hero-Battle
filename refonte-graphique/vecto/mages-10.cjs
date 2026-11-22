// La dame noire (mages-10) : redessinée par le code d'après le dessin d'origine, dans le même cadre (572 × 496, mêmes
// proportions, même pose) : très longue chevelure noire étalée des deux côtés, diadème d'argent à gemme rouge, visage
// pâle aux yeux rouges, sourire en coin ; armure de plaques noires bordée d'argent, gemme rouge sur la poitrine ; poing
// gauche levé (gantelet serré), la main droite tient une longue épée droite en travers de la taille ; cape rouge
// sombre derrière, fourrure blanche aux hanches, bottes de fer noires.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : elle arme son épée en arrière, puis tranche vers l'avant en
// descendant (traînée de lumière), le poing levé recule pour l'élan ; cheveux, cape et fourrure suivent le mouvement.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 572, H = 496, PAD = 60;

// ---------- couleurs ----------
const HAIR = { sheen: '#645a92', hi: '#b8b0e4', warm: '#58547e', warmHi: '#8a86ba', deep: '#09080f' };
const SKIN = { base: '#f8e8e6', shade: '#e6c6cc', deep: '#d2a2b0', line: '#a87482' };
const ARM = { lite: '#5c5a6e' };
const SIL = { hi: '#ffffff', lite: '#e4e8f0', base: '#bfc4d2', mid: '#8e94a8', shade: '#5f6478' };
const GOLD = { hi: '#fff4b0', base: '#f4c040', mid: '#dc9a22', shade: '#a2660e', line: '#70420a' };
const RED = { base: '#e0222c', deep: '#8a0a16', line: '#5a0610' };
// les ombres portées : une teinte par matière qui la reçoit
const SH = { skin: '#9a5868', hair: '#05040a', armor: '#06050a', cape: '#1e040a' };
// le reflet froid des plaques noires (lumière d'en haut à droite), en formes, jamais en traits
const SPEC = '#a8a4ec';
const LEFT = ['hl1', 'hl2', 'hl3', 'hl4', 'hl5'];
const RIGHT = ['hr1', 'hr2', 'hr3'];
const BACK = ['hairBack', ...LEFT, ...RIGHT];

// ---------- l'épée : un axe, d'où se déduisent la lame, la poignée et les bagues ----------
const NX = 0.319, NY = 0.948; // la normale à l'axe (vers le bas à droite) ; l'axe monte vers la droite (pente 0,337)
const onAxis = (x, off = 0) => { const y = 365 + (290 - x) * 0.337; return [n(x + off * NX), n(y + off * NY)]; };
const P = (pt) => `${pt[0]} ${pt[1]}`;
const bladeD = `M${P(onAxis(288, -10.5))} L${P(onAxis(547, -10.5))} L566 272 L${P(onAxis(551, 10.5))} L${P(onAxis(288, 10.5))} Z`;
const gripD = (() => {
  const a1 = onAxis(145.4, -6.5), a2 = onAxis(145.4, 6.5), b1 = onAxis(271.5, -6.5), b2 = onAxis(271.5, 6.5);
  return `M${P(a1)} L${P(b1)} A6.5 6.5 0 0 1 ${P(b2)} L${P(a2)} A6.5 6.5 0 0 1 ${P(a1)} Z`;
})();

/**
 * Les reflets de la chevelure : une ou deux nappes douces par côté, à cheval sur plusieurs mèches (chaque mèche la
 * peint dans sa propre forme, au même endroit : on lit une seule lumière sur la masse, pas des rayures).
 */
const SHEEN_L1 = oval(162, 234, 96, 30, 'url(#g-sheenSoft)', 1, -37);
const SHEEN_L2 = oval(150, 332, 58, 18, 'url(#g-sheenSoft)', 0.7, -48);
const SHEEN_R = oval(508, 304, 64, 22, 'url(#g-sheenSoft)', 0.85, 52);

// ---------- l'attaque : l'épée tourne autour de l'épaule (A) et du poignet (B) ----------
const SHOULDER = [268, 250], WRIST = [244, 372];
// [instant, A, B] : repos, armé en arrière, coup porté, fin du geste, retour au repos
const SWING = [[0, -0.5, 0], [0.30, 22, -27], [0.46, -20, 56], [0.58, -23, 60], [1, -0.5, 0]];
const rot = (p, c, deg) => { const a = (deg * Math.PI) / 180, x = p[0] - c[0], y = p[1] - c[1]; return [c[0] + x * Math.cos(a) - y * Math.sin(a), c[1] + x * Math.sin(a) + y * Math.cos(a)]; };
// la courbe de vitesse de chaque étape du coup (la même que dans l'animation)
const EASE = ['cubic-bezier(.3,0,.4,1)', 'cubic-bezier(.7,0,.9,.55)', 'cubic-bezier(.15,.55,.35,1)', 'cubic-bezier(.4,0,.3,1)'];
function bezier(spec) {
  const [x1, y1, x2, y2] = spec.match(/[\d.]+/g).map(Number);
  return (x) => {
    let lo = 0, hi = 1;
    for (let i = 0; i < 40; i++) { const t = (lo + hi) / 2, xt = 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t * t * x2 + t ** 3; if (xt < x) lo = t; else hi = t; }
    const t = (lo + hi) / 2;
    return 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t * t * y2 + t ** 3;
  };
}
/** La pose de l'épée [A, B] à un instant de l'attaque (de 0 à 1). */
const poseAt = (t) => {
  let i = 0;
  while (i < SWING.length - 2 && t >= SWING[i + 1][0]) i++;
  const [t0, A0, B0] = SWING[i], [t1, A1, B1] = SWING[i + 1], y = bezier(EASE[i])((t - t0) / (t1 - t0));
  return [A0 + (A1 - A0) * y, B0 + (B1 - B0) * y];
};
const bladePt = (pt, t) => { const [A, B] = poseAt(t); return rot(rot(pt, WRIST, B), SHOULDER, A); };
/**
 * La traînée du coup : posée sur le chemin que le bout de la lame parcourt pendant la partie rapide du coup (40 à 46 %
 * de l'attaque), de son tranchant jusqu'au milieu de la lame ; fine et transparente du côté d'où vient la lame.
 */
const TR0 = 0.40, TR1 = 0.46;
const trailD = (() => {
  const out = [], inn = [];
  for (let k = 0; k <= 16; k++) {
    const t = TR0 + (TR1 - TR0) * (k / 16);
    out.push(bladePt([566, 272], t));
    inn.push(bladePt(onAxis(548 - 118 * (k / 16), -10.5), t));
  }
  const pts = [...out, ...inn.reverse()];
  return `M${pts.map((q) => `${n(q[0])} ${n(q[1])}`).join(' L')} Z`;
})();
const T0 = bladePt([566, 272], TR0), T1 = bladePt([566, 272], TR1);

// ---------- dégradés ----------
const defs = [
  lin('g-hairL', 240, 120, 40, 430, [[0, '#2a2538'], [0.45, '#1c1926'], [1, '#121017']]),
  lin('g-hairR', 446, 220, 540, 460, [[0, '#2c2734'], [0.5, '#211c28'], [1, '#15121a']]),
  lin('g-cap', 330, 8, 360, 140, [[0, '#2e293e'], [0.55, '#201c2b'], [1, '#17151d']]),
  lin('g-side', 0, 0, 0, 1, [[0, '#231f2c'], [1, '#15131a']], false),
  lin('g-skin', 0, 70, 0, 216, [[0, '#fff7f5'], [0.55, SKIN.base], [1, '#efd2d6']]),
  rad('g-cheekL', 0.5, 0.5, 0.5, [[0, '#ffffff', 0.7], [1, '#ffffff', 0]], false),
  lin('g-faceL', 289, 0, 330, 0, [[0, '#d9b2bc', 0.7], [1, '#d9b2bc', 0]]),
  lin('g-neck', 0, 198, 0, 230, [[0, '#c5949f'], [1, '#e2c2c8']]),
  lin('g-armor', 0, 0, 0, 1, [[0, '#4a4858'], [0.45, '#34323e'], [1, '#211f29']], false),
  lin('g-armorX', 0, 0, 1, 0, [[0, '#211f29'], [0.55, '#34323e'], [1, '#4e4c60']], false),
  rad('g-cup', 0.64, 0.26, 0.8, [[0, '#6a6882'], [0.4, '#3e3c4c'], [1, '#1e1c26']], false),
  lin('g-rim', 0, 0, 0, 1, [[0, '#ffffff'], [0.5, '#d4d8e6'], [1, '#8e94a8']], false),
  lin('g-belt', 0, 0, 0, 1, [[0, '#a4a4b8'], [0.45, '#66667e'], [1, '#3a3a4c']], false),
  lin('g-leg', 0, 0, 1, 0, [[0, '#15131b'], [0.35, '#23212b'], [0.7, '#353347'], [0.88, '#4a4862'], [1, '#2a2836']], false),
  rad('g-sheenSoft', 0.5, 0.5, 0.5, [[0, '#a49ee6', 0.62], [0.45, '#9a94de', 0.32], [1, '#9a94de', 0]], false),
  lin('g-plate', 0, 0, 0, 1, [[0, '#9896ac'], [0.35, '#6a687c'], [1, '#3a3846']], false),
  lin('g-sleeve', 0, 0, 0, 1, [[0, '#5a586c'], [0.35, '#3c3a48'], [1, '#22202a']], false),
  lin('g-band', 0, 0, 0, 1, [[0, '#eef0f6'], [0.5, '#a9aec0'], [1, '#6a6f84']], false),
  lin('g-silver', 0, 0, 0, 1, [[0, '#ffffff'], [0.35, '#dadeea'], [0.72, '#9ea4b8'], [1, '#6a6f84']], false),
  lin('g-silverX', 0, 0, 1, 0, [[0, '#6a6f84'], [0.3, '#a6acbe'], [0.66, '#f4f6fa'], [0.84, '#d2d6e2'], [1, '#868ca2']], false),
  lin('g-gold', 0, 0, 0, 1, [[0, GOLD.hi], [0.4, GOLD.base], [1, GOLD.shade]], false),
  lin('g-goldX', 0, 0, 1, 0, [[0, GOLD.shade], [0.45, GOLD.base], [0.8, GOLD.hi], [1, GOLD.mid]], false),
  rad('g-gem', 0.62, 0.3, 0.75, [[0, '#ffd2c4'], [0.25, '#ff5a50'], [0.6, RED.base], [1, RED.deep]], false),
  lin('g-cape', 0, 240, 0, 462, [[0, '#7e1a28'], [0.6, '#621422'], [1, '#470d18']]),
  lin('g-skirt', 0, 310, 0, 374, [[0, '#5a0e18'], [0.5, '#8e1a26'], [1, '#6e1420']]),
  lin('g-grip', 0, 0, 0, 1, [[0, '#c23a3c'], [0.45, '#8e1a24'], [1, '#560c14']], false),
  lin('g-fur', 0, 322, 0, 410, [[0, '#7e1820'], [0.32, '#d65a30'], [0.55, '#f5a46e'], [0.76, '#ffe2cc'], [1, '#ffffff']]),
  lin('g-furDark', 0, 404, 0, 462, [[0, '#6e6a7e'], [0.45, '#4a4656'], [1, '#26242e']]),
  lin('g-bladeT', 0, 0, 0, 1, [[0, '#ffffff'], [1, '#e2e6f0']], false),
  lin('g-bladeB', 0, 0, 0, 1, [[0, '#b8bed0'], [1, '#8a90a6']], false),
  lin('g-glint', 0, 0, 1, 0, [[0, '#ffffff', 0], [0.5, '#ffffff', 0.95], [1, '#ffffff', 0]], false),
  lin('g-trail', n(T0[0]), n(T0[1]), n(T1[0]), n(T1[1]), [[0, '#ffffff', 0], [0.45, '#dfe8ff', 0.35], [1, '#ffffff', 0.92]]),
  rad('g-iris', 0.5, 0.8, 0.85, [[0, '#ffc08a'], [0.28, '#ff6a32'], [0.62, '#d82418'], [1, '#6e0810']], false),
  rad('g-blush', 0.5, 0.5, 0.5, [[0, '#ff8088', 0.5], [1, '#ff8088', 0]], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#2a0614', 0.75], [0.5, '#2a0614', 0]], false),
  lin('g-shadowEye', 0, 0, 0, 1, [[0, '#a06a86', 0], [1, '#a06a86', 0.55]], false),
  lin('g-lip', 0, 0, 0, 1, [[0, '#8e1a2e'], [1, '#cc4252']], false),
].join('');

// ---------- silhouettes ----------
const S = {
  // la cape, derrière tout : elle s'évase à gauche sous la poignée et à droite entre les mèches
  cape: 'M272 236 C246 270 220 318 200 360 C186 392 166 426 148 458 C162 452 176 438 192 426 C206 416 222 408 240 402 L330 398 L390 400 C420 412 446 428 466 444 C478 452 488 458 494 462 C500 440 503 410 500 380 C495 340 480 300 462 270 C450 252 438 240 428 236 Z',
  // la masse de la chevelure derrière la tête et le dos (presque toute cachée)
  hairBack: 'M232 66 C214 100 204 150 200 200 C198 250 206 300 220 340 C228 360 238 374 250 380 L300 372 L380 332 L440 318 C452 300 466 270 462 230 C458 190 452 140 448 100 C444 76 436 56 420 40 C394 20 366 14 336 14 C290 16 254 38 232 66 Z',
  // la chevelure de gauche : cinq grandes mèches en éventail, de l'extérieur vers le corps
  hl1: 'M244 52 C226 76 212 110 204 140 C196 172 182 204 158 226 C130 246 92 254 62 268 C40 280 24 300 14 324 C7 342 3 358 3 372 C3 380 0 386 -5 389 C3 384 10 372 14 360 C19 348 24 338 30 330 C50 308 82 296 116 284 C152 270 186 252 210 226 C232 200 244 164 250 128 Z',
  hl2: 'M226 140 C214 176 194 214 160 240 C126 264 84 276 58 302 C40 322 32 350 28 380 C25 400 24 418 26 434 C31 418 37 398 43 380 C46 373 49 369 52 366 C66 340 92 322 124 306 C164 286 204 262 232 224 Z',
  hl3: 'M232 182 C216 214 188 244 150 268 C114 290 84 312 68 346 C56 372 53 398 54 418 C55 427 58 433 64 436 C67 426 74 408 84 390 C100 360 126 336 160 316 C196 296 226 276 244 250 Z',
  hl4: 'M240 244 C220 270 188 292 156 314 C130 334 114 360 105 390 C99 410 97 426 100 438 C103 446 110 449 117 446 C112 440 112 428 117 412 C120 404 123 398 126 392 C142 368 166 350 194 336 C216 326 234 316 248 302 Z',
  hl5: 'M246 300 C226 318 200 336 176 352 C160 364 150 378 145 390 C141 399 137 405 131 409 C142 404 156 396 170 390 C178 387 184 385 190 384 C210 376 230 370 248 364 Z',
  // la chevelure de droite : trois mèches qui tombent sous le bras levé
  hr1: 'M450 214 C478 230 508 250 532 276 C550 296 562 322 566 348 C568 360 567 370 565 378 C560 362 554 346 544 330 C528 304 504 286 478 270 C462 262 450 256 442 252 Z',
  hr2: 'M448 248 C472 270 496 296 514 326 C528 352 536 380 538 408 C539 422 538 434 536 445 C530 428 524 410 516 392 C504 362 486 336 466 314 C456 304 448 296 442 290 Z',
  hr3: 'M440 288 C456 312 472 338 482 366 C490 390 495 416 496 440 C496 448 495 455 494 462 C488 448 480 432 472 414 C462 392 450 372 438 356 Z',
  // les jambes, bottes comprises
  legL: 'M268 352 L322 352 C322 370 322 386 322 400 C324 405 324 416 322 426 C321 434 319 442 318 449 C323 457 329 469 330 484 L240 485 C240 473 245 463 253 457 C258 454 262 452 265 450 C264 442 262 434 261 426 C259 416 259 405 262 400 C263 384 264 368 268 352 Z',
  legR: 'M380 352 L436 352 C436 370 437 386 438 400 C440 405 440 416 438 426 C437 434 435 442 433 449 C446 452 460 457 472 463 C479 467 483 473 484 479 C485 482 484 485 482 486 L384 486 C381 479 380 469 382 461 C383 456 384 452 385 449 C383 442 381 434 380 426 C378 416 378 405 380 400 C380 384 380 368 380 352 Z',
  // la jupe rouge sous la ceinture, le pan de fourrure entre les jambes, les tassettes sur les hanches
  skirt: 'M296 312 C330 320 380 320 416 308 L424 362 C404 370 382 374 360 374 C338 374 314 370 294 364 Z',
  fur: 'M330 322 L390 322 C392 345 390 370 386 392 C383 400 378 408 373 414 C368 426 362 438 354 448 C349 454 344 459 340 463 C336 456 333 448 330 440 C326 430 325 418 327 406 C328 380 328 348 330 322 Z',
  torso: 'M300 224 C320 221 345 221 368 223 C385 224 400 228 410 236 C415 252 415 270 410 284 C406 294 403 303 403 312 L404 330 L302 332 L303 312 C303 302 301 294 298 284 C294 268 295 250 300 224 Z',
  tassetL: 'M290 320 L334 326 C336 344 334 364 328 386 C314 390 300 388 290 382 C285 362 285 340 290 320 Z',
  tassetR: 'M392 324 L430 316 C437 332 441 354 437 376 C424 382 410 382 396 378 C392 360 391 342 392 324 Z',
  belt: 'M298 300 C330 307 378 306 406 298 L408 316 C378 325 330 327 296 320 Z',
  neck: 'M316 196 C326 200 342 202 352 198 L354 230 L314 230 Z',
  collar: 'M300 226 C316 216 350 215 368 222 C372 230 372 238 368 244 C346 239 322 239 300 244 C296 238 296 231 300 226 Z',
  // le bras levé, le poing serré, le bracelet d'argent, l'épaulière
  armR: 'M405 210 C425 204 445 200 460 194 C470 189 478 181 486 170 L507 199 C498 211 487 220 472 228 C456 236 438 243 418 246 C410 238 405 224 405 210 Z',
  fistR: 'M496 134 C496 126 501 120 508 119 C511 116 516 114 521 116 C524 114 529 113 534 115 C538 113 543 114 547 117 C552 118 556 123 556 129 C559 133 560 139 558 145 C560 151 559 158 555 163 C553 171 547 178 538 183 C530 189 518 193 507 193 C502 190 498 183 497 176 C494 168 493 158 494 150 C493 144 494 139 496 134 Z',
  cuffR: 'M479 178 C482 172 486 168 491 165 C498 173 504 182 509 191 C505 197 501 202 497 206 C491 197 485 187 479 178 Z',
  pauR: 'M386 216 C392 207 404 202 417 201 C422 199 427 197 432 195 C431 199 430 203 428 206 C436 210 440 218 438 226 C432 234 420 238 406 238 C396 237 389 232 387 226 C385 222 385 219 386 216 Z',
  // l'épée : longue poignée rouge baguée d'or, pommeau d'argent, lame, garde d'or
  grip: gripD,
  pommel: 'M147 408 C143 405 138 404 134 406 C130 409 126 415 124 421 C130 423 137 425 143 423 C147 421 149 417 148 413 Z',
  // le bras qui tient l'épée : bras, canon d'avant-bras en argent, gantelet
  uarmS: 'M252 236 L296 240 C294 262 282 280 268 292 L214 294 C220 274 234 254 252 236 Z',
  vamb: 'M207 287 C220 279 250 277 269 283 C270 287 268 291 265 293 C266 306 266 320 265 330 C270 334 272 342 271 351 C252 357 228 357 210 352 C208 344 209 337 213 332 C213 318 213 305 213 294 C209 293 206 290 207 287 Z',
  fistS: 'M215 348 C228 343 252 342 268 346 C273 352 276 362 275 372 C277 377 277 383 274 387 C272 391 268 393 264 393 C262 396 258 398 253 398 C250 401 245 402 240 401 C236 403 230 403 226 401 C220 400 216 395 215 388 C213 376 213 360 215 348 Z',
  // la tête
  ear: 'M264 131 C256 126 247 130 245 140 C243 152 247 164 255 171 C259 174 264 173 267 168 Z',
  sideL: 'M281 118 C274 140 268 164 264 188 C262 200 262 210 266 220 C272 222 278 220 282 214 C288 200 292 182 293 162 C294 146 293 132 291 120 Z',
  pauL: 'M242 251 C246 245 252 242 258 239 C261 228 267 219 276 213 C276 209 275 205 272 200 C278 202 282 205 285 210 C290 207 296 206 301 207 C302 202 305 198 309 195 C310 200 310 205 308 210 C312 217 314 226 312 236 C311 243 309 249 305 254 C303 257 300 259 297 260 L293 267 L287 261 L277 270 L271 263 L260 269 L255 261 C250 258 246 255 242 251 Z',
  face: 'M291 70 L289 145 C289 166 292 182 300 194 C312 207 334 215 362 216 C386 216 406 206 419 191 C428 178 433 162 433 142 L433 70 Z',
  sideR: 'M430 126 C433 144 432 162 427 178 C423 190 419 198 421 206 C429 211 439 210 446 206 C451 190 453 168 453 146 C453 134 452 124 450 114 Z',
  cap: 'M226 72 C244 40 290 12 336 9 C384 6 428 30 446 70 C452 86 454 104 453 124 C449 130 442 134 435 136 C430 128 424 120 417 110 C411 102 407 92 404 80 C390 76 360 74 340 78 C334 86 326 96 318 104 C308 112 300 122 293 132 C286 132 278 131 270 131 C258 132 248 130 238 122 C228 114 222 102 222 90 C222 84 224 78 226 72 Z',
  tiara: 'M364 5 C368 16 374 26 382 36 L398 58 C392 68 386 80 376 98 C370 86 362 76 350 72 L339 64 L354 40 C358 28 361 16 364 5 Z M306 51 C314 57 324 65 336 71 L300 77 C300 67 302 59 306 51 Z M418 41 C421 53 424 65 428 77 L406 71 C410 61 414 51 418 41 Z',
  blade: bladeD,
  guard: 'M283 330 C290 328 298 331 300 337 C301 341 298 343 295 341 C293 338 290 337 288 338 C290 350 292 362 296 374 C299 384 302 392 304 398 C304 403 299 405 295 402 C292 398 290 392 287 386 C283 374 279 360 277 346 C276 338 278 332 283 330 Z M265 371 A7.5 7.5 0 1 1 280 371 A7.5 7.5 0 1 1 265 371 Z',
};

// ---------- les yeux ----------
/**
 * Un œil : blanc, grand iris rouge en dégradé, pupille, ombre de la paupière, reflets ; puis le fard sous le sourcil,
 * les cils (une forme pleine, avec l'aile au coin extérieur) et le bas de l'œil. `shut` = l'œil fermé (clignement).
 */
function eye(key, white, cx, cy, r, lash, lower, shut, shadow, hl) {
  return shape(shadow, 'url(#g-shadowEye)')
    + `<clipPath id="c-${key}"><path d="${white}"/></clipPath>`
    + `<path d="${white}" fill="#fff"/>`
    + `<g clip-path="url(#c-${key})">`
    + `<path d="${white}" fill="none" stroke="#e6cdd8" stroke-width="3.4"/>`
    + `<circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#g-iris)"/>`
    + `<circle cx="${cx}" cy="${cy}" r="${r - 0.9}" fill="none" stroke="${RED.line}" stroke-width="1.8"/>`
    + oval(cx, n(cy - r * 0.2), n(r * 0.5), n(r * 0.54), '#22030a')
    + `<path d="M${n(cx - r * 0.64)} ${n(cy + r * 0.45)} A${n(r * 0.8)} ${n(r * 0.8)} 0 0 0 ${n(cx + r * 0.64)} ${n(cy + r * 0.45)}" fill="none" stroke="#ffcf9e" stroke-width="1.8" opacity="0.7"/>`
    + `<rect x="${cx - r - 20}" y="${cy - r - 8}" width="${2 * r + 40}" height="${n(r * 1.4)}" fill="url(#g-lid)"/>`
    + dot(n(cx + hl[0] * r), n(cy + hl[1] * r), n(r * 0.23), '#fff')
    + dot(n(cx + hl[2] * r), n(cy + hl[3] * r), n(r * 0.14), '#fff', 0.95)
    + `</g>`
    + line(lower, '#3a1a2a', 1.6, 0.9) + shape(lash, '#170a14')
    + `<g class="a-blink" opacity="0"><path d="${white}" fill="#f2dcdc" stroke="#f2dcdc" stroke-width="3"/>${line(shut, '#170a14', 3.2)}</g>`;
}

// le bandeau du diadème : un arc d'ellipse autour du crâne (centre 364,132 ; 112 × 62), plus épais au milieu
const bandPt = (x, off) => { const dx = (x - 364) / 112; return [x, n(132 - 62 * Math.sqrt(Math.max(0, 1 - dx * dx)) + off)]; };
const bandHalf = (x) => 1.6 + 2.6 * (1 - Math.abs(x - 364) / 112);
const BAND_X = [256, 264, 276, 290, 306, 324, 344, 364, 384, 404, 422, 438, 452, 464];
const bandLine = (sgn) => BAND_X.map((x) => bandPt(x, sgn * bandHalf(x)));
const polyline = (pts) => `M${pts.map((p) => `${p[0]} ${p[1]}`).join(' L')}`;
const BAND = `${polyline(bandLine(-1))} L${bandLine(1).reverse().map((p) => `${p[0]} ${p[1]}`).join(' L')} Z`;
const BAND_TOP = polyline(BAND_X.map((x) => bandPt(x, -bandHalf(x) + 0.7)));
const BAND_LOW = polyline(BAND_X.map((x) => bandPt(x, bandHalf(x) - 0.6)));

/** Une mèche : sa couleur, l'ombre de son bord, une nappe de reflet (violet à gauche, chaud à droite), un reflet vif. */
const lock = (id, grad, sheen, hi, shade, sheenColor = HAIR.sheen, hiColor = HAIR.hi, k = 1) => use(id, grad)
  + clip(id, (shade ? shape(shade, HAIR.deep, 0.55) : '') + (sheen ? shape(sheen, sheenColor, n(0.34 * k)) : '') + (hi ? shape(hi, hiColor, n(0.55 * k)) : ''));

// ---------- les morceaux, du fond vers le devant ----------
const parts = [
  // --- la cape : rouge sombre, un pli plus clair de chaque côté ---
  { id: 'cape', cls: 'a-cape', d: S.cape,
    body: use('cape', 'url(#g-cape)') + clip('cape',
      shape('M240 300 C222 340 198 392 160 448 C186 420 214 386 236 352 Z', '#a8283a', 0.55)
      + shape('M150 456 C166 440 186 424 206 414 C190 428 172 444 156 458 Z', '#d2485a', 0.7)
      + shape('M440 300 C462 340 480 390 490 446 C478 400 458 352 432 318 Z', '#b02c3e', 0.6)
      + shape('M456 350 C470 390 482 424 492 458 L470 444 C464 414 456 384 446 356 Z', '#2e0610', 0.45)
      + shape('M392 402 C420 414 446 430 468 446 C444 436 418 424 392 414 Z', '#2e0610', 0.5)
    ) },
  // --- la chevelure, derrière ---
  { id: 'hairBack', d: S.hairBack, shadow: [{ on: ['cape'], dx: -4, dy: 4, color: SH.cape, o: 0.5 }],
    body: use('hairBack', '#15131b') },
  { id: 'hl1', cls: 'a-hl', d: S.hl1,
    body: lock('hl1', 'url(#g-hairL)', '', '',
      'M250 128 C244 164 232 200 210 226 C186 252 152 270 116 284 C82 296 50 308 30 330 C40 316 60 304 84 296 C122 282 160 266 188 244 C214 222 236 186 246 140 Z')
      + clip('hl1', SHEEN_L1) },
  { id: 'hl2', cls: 'a-hl', d: S.hl2, shadow: [{ on: ['hl1'], dx: -6, dy: 3, color: SH.hair, o: 0.5 }],
    body: lock('hl2', 'url(#g-hairL)', '', '',
      'M232 224 C204 262 164 286 124 306 C92 322 66 340 52 366 C46 380 40 398 34 414 C42 392 54 368 72 348 C98 324 132 306 168 288 C198 270 222 250 232 224 Z')
      + clip('hl2', SHEEN_L1) },
  { id: 'hl3', cls: 'a-hl', d: S.hl3, shadow: [{ on: ['hl1', 'hl2'], dx: -6, dy: 3, color: SH.hair, o: 0.5 }],
    body: lock('hl3', 'url(#g-hairL)', '', '',
      'M244 250 C224 276 196 296 160 316 C126 336 100 360 84 390 C74 410 64 428 56 444 C66 420 80 392 98 368 C122 336 156 316 190 298 C214 284 234 270 244 250 Z')
      + clip('hl3', SHEEN_L1 + SHEEN_L2) },
  { id: 'hl4', cls: 'a-hl2', d: S.hl4, shadow: [{ on: ['hl2', 'hl3'], dx: -6, dy: 3, color: SH.hair, o: 0.5 }],
    body: lock('hl4', 'url(#g-hairL)', '', '', '') + clip('hl4', SHEEN_L2) },
  { id: 'hl5', cls: 'a-hl2', d: S.hl5, shadow: [{ on: ['hl3', 'hl4'], dx: -6, dy: 3, color: SH.hair, o: 0.5 }],
    body: lock('hl5', 'url(#g-hairL)', '', '', '') + clip('hl5', SHEEN_L2) },
  { id: 'hr1', cls: 'a-hr', d: S.hr1, body: lock('hr1', 'url(#g-hairR)', '', '', '') + clip('hr1', SHEEN_R) },
  { id: 'hr2', cls: 'a-hr', d: S.hr2, shadow: [{ on: ['hr1'], dx: -5, dy: 3, color: SH.hair, o: 0.5 }],
    body: lock('hr2', 'url(#g-hairR)', '', '',
      'M442 290 C458 306 474 324 488 344 C502 366 512 390 518 414 C508 392 496 370 480 350 C468 334 456 320 442 306 Z')
      + clip('hr2', SHEEN_R) },
  { id: 'hr3', cls: 'a-hr', d: S.hr3, shadow: [{ on: ['hr2', 'cape'], dx: -5, dy: 3, color: SH.hair, o: 0.5 }],
    body: lock('hr3', 'url(#g-hairR)', '', '', '') + clip('hr3', SHEEN_R) },

  // --- les jambes : cuisse, genouillère bombée bordée d'argent, grève qui s'affine, soleret à plaques ---
  { id: 'legL', d: S.legL, shadow: [{ on: ['cape', ...BACK], dx: -5, dy: 3, color: SH.armor, o: 0.45 }],
    body: use('legL', 'url(#g-leg)') + clip('legL',
      // le liseré d'argent du bord extérieur, et le reflet froid du devant
      shape('M264 356 C263 372 262 388 261 398 L265 398 C266 388 267 372 268 356 Z', SIL.mid, 0.75)
      + shape('M309 356 C313 370 314 384 313 396 C310 384 308 370 305 357 Z', SPEC, 0.6)
      // la genouillère : une coque bombée, bordée d'argent, une pointe au milieu
      + shape('M263 404 C269 399 280 397 291 397 C302 397 313 399 319 404 C321 412 317 420 309 426 C303 430 297 434 291 438 C285 434 279 430 273 426 C265 420 261 412 263 404 Z', '#0c0b10', 0.45, )
      + shape('M263 402 C269 397 280 395 291 395 C302 395 313 397 319 402 C321 410 317 418 309 424 C303 428 297 432 291 436 C285 432 279 428 273 424 C265 418 261 410 263 402 Z', 'url(#g-cup)')
      + shape('M262 403 C268 396 280 393 291 393 C302 393 314 396 320 403 L317 404 C311 399 301 397 291 397 C281 397 271 399 265 404 Z', 'url(#g-rim)')
      + line('M291 397 L291 434', '#5a586e', 1.2, 0.7)
      + shape('M287 397 L291 383 L295 397 Z', 'url(#g-rim)') + shape('M291 383 L295 397 L291 395 Z', SIL.shade, 0.6)
      + shape('M298 400 C307 401 314 404 317 409 C311 406 305 404 296 403 Z', SPEC, 0.85) + oval(306, 401.5, 3.2, 1.3, '#ffffff', 0.85, 12)
      // la grève, qui s'affine vers la cheville : un reflet sur le devant, un liseré d'argent en bas
      + shape('M308 431 C311 436 312 442 311 447 C308 441 306 436 303 432 Z', SPEC, 0.7)
      + shape('M262 446 C280 443 304 443 320 445 L320 449 C304 447 280 447 263 450 Z', 'url(#g-rim)')
      // le soleret : quatre lames arrondies, éclairées en haut à droite, bordées d'argent
      + shape('M246 455 C258 450 274 449 288 451 C302 449 318 451 329 458 L331 487 L239 487 Z', '#1c1a22')
      + shape('M242 471 C243 463 249 459 255 459 C261 460 265 465 265 472 L265 486 L241 486 C240 480 241 475 242 471 Z', 'url(#g-cup)')
      + shape('M265 468 C266 461 272 458 278 458 C284 459 287 464 287 470 L287 486 L265 486 Z', 'url(#g-cup)')
      + shape('M287 468 C288 461 294 458 300 458 C306 459 309 464 309 470 L309 486 L287 486 Z', 'url(#g-cup)')
      + shape('M309 469 C310 462 316 459 322 460 C327 462 330 467 330 474 L330 486 L309 486 Z', 'url(#g-cup)')
      + line('M244 466 C247 461 251 459.6 255 459.6 M267 462 C270 459.4 274 458.4 278 458.4 M289 462 C292 459.4 296 458.4 300 458.4 M311 463 C314 460.4 318 459.6 322 460.4', SIL.base, 1.8, 0.9)
      + oval(283, 462, 2.6, 1.2, '#ffffff', 0.8, 10) + oval(305, 462, 2.6, 1.2, '#ffffff', 0.85, 10) + oval(326, 465, 2.4, 1.2, '#ffffff', 0.85, 30)
      + shape('M238 480 L332 480 L332 487 L238 487 Z', '#0e0d12', 0.6)
    ) },
  { id: 'legR', d: S.legR, shadow: [{ on: ['cape', ...BACK], dx: -5, dy: 3, color: SH.armor, o: 0.45 }],
    body: use('legR', 'url(#g-leg)') + clip('legR',
      shape('M382 356 C381 372 380 388 380 398 L384 398 C384 388 385 372 386 356 Z', SIL.mid, 0.75)
      + shape('M425 356 C429 370 431 384 431 396 C427 384 425 370 421 357 Z', SPEC, 0.6)
      // la genouillère
      + shape('M381 404 C387 399 398 397 409 397 C420 397 431 399 437 404 C439 412 435 420 427 426 C421 430 415 434 409 438 C403 434 397 430 391 426 C383 420 379 412 381 404 Z', '#0c0b10', 0.45)
      + shape('M381 402 C387 397 398 395 409 395 C420 395 431 397 437 402 C439 410 435 418 427 424 C421 428 415 432 409 436 C403 432 397 428 391 424 C383 418 379 410 381 402 Z', 'url(#g-cup)')
      + shape('M380 403 C386 396 398 393 409 393 C420 393 432 396 438 403 L435 404 C429 399 419 397 409 397 C399 397 389 399 383 404 Z', 'url(#g-rim)')
      + line('M409 397 L409 434', '#5a586e', 1.2, 0.7)
      + shape('M405 397 L409 383 L413 397 Z', 'url(#g-rim)') + shape('M409 383 L413 397 L409 395 Z', SIL.shade, 0.6)
      + shape('M416 400 C425 401 432 404 435 409 C429 406 423 404 414 403 Z', SPEC, 0.85) + oval(424, 401.5, 3.2, 1.3, '#ffffff', 0.85, 12)
      // la grève
      + shape('M425 431 C428 436 429 442 428 447 C425 441 423 436 420 432 Z', SPEC, 0.7)
      + shape('M383 446 C398 443 420 443 434 445 L434 449 C420 447 398 447 384 450 Z', 'url(#g-rim)')
      // le soleret, long et pointu vers la droite : deux lames sur le cou-de-pied, le bout ferré
      + shape('M384 449 C400 447 420 447 433 449 C446 452 460 457 472 463 C479 467 483 473 484 479 L484 488 L382 488 Z', '#1c1a22')
      + shape('M384 453 C400 450 420 450 434 452 C446 455 458 460 468 466 L466 470 C456 464 444 459 432 457 C420 455 400 455 384 458 Z', '#3c3a4a')
      + shape('M383 462 C400 459 420 459 432 462 C444 465 456 470 465 476 L462 480 C453 475 442 470 430 467 C418 464 400 464 383 467 Z', '#46445a')
      + line('M385 453 C400 450 420 450 434 452 C446 455 458 460 468 466', SIL.base, 1.6, 0.9)
      + line('M384 462 C400 459 420 459 432 462 C444 465 456 470 465 476', SIL.mid, 1.4, 0.8)
      + shape('M462 466 C470 468 478 472 482 478 C483 481 483 484 482 486 L458 486 C458 479 459 472 462 466 Z', 'url(#g-cup)')
      + line('M462 466 C470 468 478 472 482 478', SIL.hi, 1.6, 0.9)
      + shape('M440 455 C450 457 458 461 464 466 C456 463 448 460 438 458 Z', SPEC, 0.75) + oval(474, 472, 3, 1.4, '#ffffff', 0.9, 30)
      + shape('M380 480 L486 480 L486 488 L380 488 Z', '#0e0d12', 0.6)
    ) },

  // --- la jupe rouge, sous la ceinture ---
  { id: 'skirt', d: S.skirt, shadow: [{ on: ['legL', 'legR'], dx: -4, dy: 4, color: SH.armor, o: 0.5 }],
    body: use('skirt', 'url(#g-skirt)') + clip('skirt',
      shape('M404 318 C410 334 414 350 414 366 L424 362 L416 308 Z', '#c23a48', 0.55)
      + shape('M300 330 C304 342 306 354 306 366 L296 364 L296 318 Z', '#3a0810', 0.4)
    ) },
  // --- le pan de fourrure : drap rouge et orangé, bordure de fourrure blanche, bout sombre ---
  { id: 'fur', cls: 'a-fur', d: S.fur, shadow: [{ on: ['legL', 'legR', 'skirt'], dx: -4, dy: 3, color: SH.armor, o: 0.45 }],
    body: use('fur', 'url(#g-fur)') + clip('fur',
      // la bordure de fourrure blanche, sur les côtés
      shape('M330 338 C334 354 337 370 337 388 L327 392 C327 374 328 356 330 338 Z', '#fffaf6', 0.95)
      + shape('M390 334 C386 352 384 370 384 386 L389 386 C391 368 392 352 390 334 Z', '#fffaf6', 0.95)
      // le bout sombre de la fourrure ; par-dessus, la frange blanche en dents de loup souples (pointes vers le haut
      // dans le drap orangé, touffes vers le bas sur le bout sombre)
      + shape('M324 400 L392 396 L392 470 L322 470 Z', 'url(#g-furDark)')
      + shape('M327 392 C330 386 332 378 335 371 C338 378 341 384 345 388 C348 380 351 373 354 367 C357 374 360 381 363 386 C366 379 369 373 373 368 C376 374 380 380 386 384 L388 386 C386 394 384 402 381 409 C378 404 375 401 371 401 C369 407 365 413 360 415 C357 409 353 405 348 405 C345 411 341 415 336 414 C333 408 330 403 327 399 Z', '#fffaf6')
      + shape('M327 399 C330 403 333 408 336 414 C341 415 345 411 348 405 C346 409 342 411 338 410 C334 407 330 403 327 399 Z M360 415 C365 413 369 407 371 401 C369 405 366 409 362 411 Z', '#cdbfc6', 0.8)
      + shape('M350 412 C354 424 355 436 351 448 C358 438 360 424 357 412 Z', '#a8a4b8', 0.5)
      // l'ombre de la ceinture, la lumière du côté droit
      + shape('M326 318 L394 318 L394 334 C370 328 350 328 326 334 Z', '#3a0810', 0.45)
      + shape('M376 352 C382 368 382 384 378 398 C386 384 388 366 386 352 Z', '#ffffff', 0.55)
    ) },

  // --- le buste : plastron à deux coques galbées bordées d'argent, taille serrée, gemme rouge ---
  { id: 'torso', d: S.torso, shadow: [{ on: BACK, dx: -5, dy: 3, color: SH.hair, o: 0.5 }, { on: ['cape'], dx: -5, dy: 3, color: SH.cape, o: 0.45 }],
    body: use('torso', 'url(#g-armor)') + clip('torso',
      // le ventre : une lame en travers sous les coques, qui serre la taille
      shape('M302 297 C322 303 386 303 405 295 L405 303 C386 311 322 311 302 305 Z', '#121016', 0.55)
      + line('M303 295 C322 301 386 301 405 293', SIL.mid, 1.2, 0.75)
      // le flanc droit, éclairé : un reflet froid qui suit la taille
      + shape('M407 242 C412 256 412 272 407 286 C404 294 402 302 402 312 L398 312 C398 300 401 290 404 282 C408 268 408 254 404 244 Z', SPEC, 0.55)
      // les deux coques bombées, leur ombre sur le ventre
      + shape('M302 254 C310 241 333 237 352 245 C359 256 359 275 352 287 C339 293 316 292 304 285 C298 275 298 263 302 254 Z', 'url(#g-cup)')
      + shape('M368 245 C380 236 400 236 411 245 C415 258 414 275 406 286 C394 291 377 290 367 283 C362 271 363 257 368 245 Z', 'url(#g-cup)')
      + shape('M304 285 C316 292 339 293 352 287 L351 295 C338 300 316 299 303 292 Z', '#0c0b10', 0.55)
      + shape('M367 283 C377 290 394 291 406 286 L405 293 C393 298 377 297 366 290 Z', '#0c0b10', 0.5)
      // leurs liserés d'argent : le haut de la coque gauche, le haut et le bord éclairé de la coque droite
      + shape('M301 256 C309 240 333 235 354 244 L352 247 C334 240 311 243 304 256 Z', 'url(#g-rim)')
      + shape('M366 247 C378 234 401 234 413 244 C417 258 416 276 407 288 L405 286 C412 275 412 259 409 247 C399 239 381 239 369 249 Z', 'url(#g-rim)')
      // les reflets froids et leurs points de lumière
      + shape('M334 247 C343 248 350 253 352 261 C347 256 341 252 332 250 Z', SPEC, 0.8)
      + shape('M392 242 C401 243 408 249 410 257 C405 251 399 247 390 245 Z', SPEC, 0.9)
      + oval(344, 251, 3, 1.4, '#ffffff', 0.8, 28) + oval(401, 247, 3.4, 1.5, '#ffffff', 0.9, 30)
      // le galon rouge qui descend de la gemme, sa pointe d'argent
      + shape('M355 268 L373 268 L366 296 L362 296 Z', '#7e1420')
      + shape('M359 270 L369 270 L364 292 Z', '#b02a36', 0.8)
      + shape('M360 290 L368 290 L364 300 Z', SIL.base)
      // les rivets, au bord des coques
      + dot(308, 251, 1.6, SIL.lite) + dot(346, 243, 1.5, SIL.lite) + dot(373, 243, 1.5, SIL.lite) + dot(408, 248, 1.6, SIL.lite)
    )
      // la gemme du cœur, dans sa monture d'argent
      + shape('M364 246 C370.5 247 376 252.5 377 260 C377 268 371.5 275 364.5 281 C357.5 275 352 268 352 260 C353 252.5 357.5 247 364 246 Z', SIL.base)
      + shape('M364.5 249.5 C369 250.5 373 255 373.5 260.5 C373.5 266.5 369.5 271.5 364.5 276 C359.5 271.5 355.5 266.5 355.5 260.5 C356 255 360 250.5 364.5 249.5 Z', 'url(#g-gem)')
      + shape('M366 252 C369 253.5 370.5 256.5 370.5 259.5 C368 257.5 366.5 255 366 252 Z', '#ffe2d8', 0.95) },
  { id: 'tassetL', d: S.tassetL, shadow: [{ on: ['legL', 'fur', 'skirt'], dx: -3, dy: 5, color: SH.armor, o: 0.45 }],
    body: use('tassetL', 'url(#g-armor)') + clip('tassetL',
      shape('M290 376 C302 382 318 384 332 380 L330 392 L288 392 Z', 'url(#g-rim)')
      + shape('M289 322 C286 342 286 362 290 380 L293 380 C290 362 290 342 292 323 Z', SIL.mid, 0.8)
      + shape('M314 330 C326 334 332 348 332 364 C328 350 322 338 312 334 Z', SPEC, 0.7)
      + oval(322, 340, 3.4, 1.5, '#ffffff', 0.7, 40)
    ) },
  { id: 'tassetR', d: S.tassetR, shadow: [{ on: ['legR', 'fur', 'cape', 'skirt'], dx: -3, dy: 5, color: SH.armor, o: 0.45 }],
    body: use('tassetR', 'url(#g-armorX)') + clip('tassetR',
      shape('M396 372 C408 377 422 377 438 370 L440 384 L394 384 Z', 'url(#g-rim)')
      + shape('M430 318 C437 334 440 354 437 374 L434 374 C437 354 434 334 428 320 Z', '#dcdfe9', 0.85)
      + shape('M416 324 C428 332 434 346 436 362 C428 348 420 336 410 328 Z', SPEC, 0.8)
      + oval(426, 334, 3.4, 1.5, '#ffffff', 0.8, 50)
    ) },
  { id: 'belt', d: S.belt, shadow: [{ on: ['torso', 'fur', 'skirt', 'tassetL', 'tassetR'], dx: -2, dy: 4, color: SH.armor, o: 0.5 }],
    body: use('belt', 'url(#g-belt)') + clip('belt',
      // le bord du haut en argent, le bas dans l'ombre, les plaques
      shape('M298 300 C330 307 378 306 406 298 L406 302 C378 310 330 311 298 304 Z', '#f2f4f9', 0.85)
      + shape('M296 316 C330 323 378 321 408 312 L408 318 C378 327 330 329 296 322 Z', '#15131b', 0.5)
      + line('M320 307 L320 324 M390 303 L390 320', '#2e2c3a', 1.4, 0.7)
      + shape('M392 303 C398 302 403 301 406 300 L406 304 C402 305 397 306 392 307 Z', '#ffffff', 0.55)
    )
      // le fermoir d'argent, à droite de la boucle
      + shape('M368 306 C368 303 370 302 373 302 L381 302 C384 302 385 304 385 307 L385 316 C385 319 383 320 380 320 L373 320 C370 320 368 318 368 316 Z', 'url(#g-silver)')
      + shape('M372 307 L381 307 L381 315 L372 315 Z', '#2e2c3a') + line('M372 307.5 L381 307.5', '#ffffff', 1, 0.7)
      // la boucle : une gemme rouge sertie d'or
      + `<circle cx="358" cy="313" r="9" fill="url(#g-gold)"/>` + `<circle cx="358" cy="313" r="9" fill="none" stroke="${GOLD.line}" stroke-width="1.2" opacity="0.7"/>`
      + `<circle cx="358" cy="313" r="5.6" fill="url(#g-gem)"/>` + dot(360, 311, 1.6, '#ffe2d8') },

  // --- le cou et le gorgerin ---
  { id: 'neck', d: S.neck, body: use('neck', 'url(#g-neck)') },
  { id: 'collar', d: S.collar, shadow: [{ on: ['neck', 'torso'], dx: -2, dy: 4, color: SH.armor, o: 0.4 }],
    body: use('collar', '#25232d') + clip('collar',
      shape('M316 226 C326 223 342 223 352 226 L336 243 Z', '#5e0e1a')
      + shape('M322 228 C330 226.5 338 226.5 346 228 L335.5 239 Z', '#9a2232', 0.85)
      + line('M316 226 L336 243 L352 226', '#9aa0b4', 1.3, 0.8)
      + line('M301 227 C316 218 350 217 367 223', SIL.base, 1.8, 0.9)
      + line('M300 242 C322 237 346 237 368 242', SIL.mid, 1.4, 0.7)
    ) },

  // --- le bras levé ---
  { id: 'armR', cls: 'a-raise', d: S.armR, shadow: [{ on: ['torso', ...BACK], dx: -4, dy: 5, color: SH.armor, o: 0.45 }],
    body: use('armR', 'url(#g-sleeve)') + clip('armR',
      shape('M410 214 C432 208 452 203 466 195 C474 190 480 183 486 175 C478 190 466 200 450 206 C436 211 422 214 410 218 Z', SPEC, 0.7)
      + shape('M420 240 C440 236 458 230 474 222 C488 214 498 206 506 198 L508 206 C496 216 480 226 462 234 C446 240 430 244 418 246 Z', '#121016', 0.5)
      // le renflement du coude, un éclat de lumière sur le dessus
      + shape('M446 206 C456 202 466 198 474 190 C470 200 462 208 450 212 Z', '#7e7c94', 0.6)
      + oval(462, 200, 7, 2, '#ffffff', 0.6, -30) + oval(430, 209, 6, 1.7, '#ffffff', 0.45, -12)
    ) },
  { id: 'fistR', cls: 'a-fist', d: S.fistR,
    body: use('fistR', 'url(#g-armor)') + clip('fistR',
      // les quatre jointures (le haut du poing) : des plaques bombées, éclairées en haut à droite, bordées d'argent
      shape('M496 136 C496 127 501 121 508 120 C512 124 514 131 512 138 C506 141 500 140 496 136 Z', 'url(#g-cup)')
      + shape('M509 119 C512 116 517 115 521 116 C524 114 529 114 533 116 C534 123 533 131 529 137 C523 139 517 139 512 137 C514 130 513 124 509 119 Z', 'url(#g-cup)')
      + shape('M533 116 C538 114 543 115 547 118 C549 125 548 132 544 138 C539 139 534 138 530 136 C533 130 534 123 533 116 Z', 'url(#g-cup)')
      + shape('M547 118 C552 119 556 124 556 130 C558 135 557 140 554 144 C551 145 548 144 545 143 C547 135 548 126 547 118 Z', 'url(#g-cup)')
      + line('M499 128 C502 123 506 121 509 121 M513 117.5 C517 116 521 116 524 115.5 M528 115 C532 114.6 536 114.8 539 115.4 M542 115.8 C546 116.6 550 118.6 553 121.6', '#d8d6ea', 1.8, 0.9)
      + shape('M528 117 C537 115 546 117 552 122 C546 120 538 119 530 120 Z', SPEC, 0.8)
      // les quatre doigts repliés : des phalanges bombées, séparées par des creux sombres
      + shape('M495 140 C512 145 535 146 558 141 C559 149 558 156 555 163 C534 167 512 167 494 162 C493 155 493 147 495 140 Z', '#0c0b10')
      + shape('M497 144 C501 143 507 144 511 145.5 C512 151 511 157 509 162 C504 162 499 161 496 159 C495 154 495 149 497 144 Z', 'url(#g-cup)')
      + shape('M514 146.5 C519 147 524 147.5 528 147.5 C529 153 528 159 526 164 C521 164.5 517 164.5 513 163.5 C512 158 512 152 514 146.5 Z', 'url(#g-cup)')
      + shape('M531 147.5 C536 147.5 540 147 544 146.5 C545 152 544 158 542 163.5 C538 164.5 534 164.5 530 164 C529 158 529 152 531 147.5 Z', 'url(#g-cup)')
      + shape('M547 146 C550 145.5 553 144.5 556 143.5 C557 149 556 155 554 161 C552 162 549 162.5 546 162.5 C545 156 545 151 547 146 Z', 'url(#g-cup)')
      + oval(507, 147.5, 2.4, 1.1, '#d8d6ea', 0.8, 10) + oval(524, 150, 2.4, 1.1, '#d8d6ea', 0.85, 6)
      + oval(540, 150, 2.4, 1.1, '#e4e2f2', 0.9, 0) + oval(552.5, 148, 2, 1, '#e4e2f2', 0.9, -10)
      // le pouce, en travers devant les doigts
      + shape('M496 168 C505 161 520 158 534 160 C542 162 547 167 547 173 C539 181 524 185 508 184 C501 180 496 174 496 168 Z', 'url(#g-cup)')
      + shape('M501 165 C511 161 525 160 536 163 C525 163 513 165 503 168 Z', '#c4c2d8', 0.75)
      + shape('M532 162 C539 163 545 167 546.5 172 C541 171 536 168 532 165 Z', '#9896b0', 0.6)
      + line('M518 170 C526 170 533 172 539 176', '#0c0b10', 1.3, 0.55)
      + shape('M500 182 C512 190 528 190 546 180 L548 194 L498 200 Z', '#121016', 0.45)
    ) },
  { id: 'cuffR', cls: 'a-raise', d: S.cuffR, shadow: [{ on: ['armR', 'fistR'], dx: -3, dy: 4, color: SH.armor, o: 0.5 }],
    body: use('cuffR', 'url(#g-silver)') + clip('cuffR',
      line('M484 172 C490 180 496 190 502 200', SIL.shade, 2.6, 0.6)
      + line('M489 168 C495 176 501 185 506 193', SIL.hi, 2, 0.9)
    ) },
  { id: 'pauR', d: S.pauR, shadow: [{ on: ['armR', 'torso', 'collar'], dx: -3, dy: 5, color: SH.armor, o: 0.5 }],
    body: use('pauR', 'url(#g-cup)') + clip('pauR',
      // trois lames qui se recouvrent, chacune bordée d'argent en haut
      shape('M386 222 C396 214 412 212 426 214 C432 215 437 218 440 222 L440 240 L384 240 Z', '#2c2a36')
      + shape('M387 230 C397 223 412 222 426 224 C431 225 435 227 438 229 L440 240 L384 240 Z', '#24222c')
      + line('M386 222 C396 214 412 212 426 214 C432 215 437 218 440 222', SIL.base, 1.6, 0.9)
      + line('M387 230 C397 223 412 222 426 224 C431 225 435 227 438 229', SIL.mid, 1.4, 0.8)
      // le liseré d'argent du bord du haut, jusqu'à la pointe
      + shape('M385 217 C391 206 404 200 417 199 C422 197 427 195 433 193 L431 198 C426 200 422 202 418 203 C405 204 394 209 388 218 Z', 'url(#g-rim)')
      + shape('M404 206 C412 203 420 203 428 204 C420 205 412 207 405 210 Z', SPEC, 0.85) + oval(416, 204, 3.2, 1.3, '#ffffff', 0.9, -6)
      + shape('M388 232 C398 238 420 240 438 230 L438 242 L386 242 Z', '#0c0b10', 0.5)
    ) },

  // --- l'épée (derrière la main) : la poignée et le pommeau ---
  { id: 'grip', cls: 'a-sw', d: S.grip, shadow: [{ on: ['cape', ...LEFT, 'hairBack'], dx: -3, dy: 5, color: SH.cape, o: 0.5 }],
    body: use('grip', 'url(#g-grip)')
      // les bagues d'or
      + [[153, 4.5], [186, 3], [210, 6]].map(([x, w]) => {
        const a = onAxis(x - w, -7.4), b = onAxis(x + w, -7.4), c = onAxis(x + w, 7.4), d = onAxis(x - w, 7.4);
        return `<path d="M${P(a)} L${P(b)} L${P(c)} L${P(d)} Z" fill="url(#g-goldX)"/>` + line(`M${P(onAxis(x - w + 1.6, -6))} L${P(onAxis(x - w + 1.6, 6))}`, GOLD.hi, 1.2, 0.8);
      }).join('')
      + line(`M${P(onAxis(146, -3.2))} L${P(onAxis(270, -3.2))}`, '#e86a6a', 1.4, 0.5) },
  { id: 'pommel', cls: 'a-sw', d: S.pommel, shadow: [{ on: ['cape', ...LEFT], dx: -3, dy: 5, color: SH.cape, o: 0.5 }],
    body: use('pommel', 'url(#g-band)')
      + shape('M147 408 C143 405 138 404 134 406 C132 408 130 411 128 414 C134 412 140 411 148 413 Z', '#ffffff', 0.6)
      + shape('M124 421 C130 423 137 425 143 423 C147 421 149 417 148 413 C142 418 134 420 124 421 Z', SIL.shade, 0.6) },

  // --- le bras qui tient l'épée ---
  { id: 'uarmS', cls: 'a-sa', d: S.uarmS, shadow: [{ on: ['torso', ...BACK], dx: -4, dy: 4, color: SH.armor, o: 0.4 }],
    body: use('uarmS', 'url(#g-sleeve)') + clip('uarmS',
      shape('M276 244 C286 246 292 250 294 254 C290 270 280 282 268 290 C276 276 282 262 276 244 Z', ARM.lite, 0.7)
      + shape('M214 294 C222 276 234 258 246 246 C240 262 232 278 228 294 Z', '#121016', 0.45)
      + shape('M284 246 C290 250 292 256 290 264 C287 256 284 251 280 248 Z', SPEC, 0.75)
      + oval(282, 266, 2.4, 6, '#ffffff', 0.45, 30)
    ) },
  { id: 'vamb', cls: 'a-sa', d: S.vamb, shadow: [{ on: ['uarmS', ...BACK, 'cape'], dx: -4, dy: 4, color: SH.armor, o: 0.45 }],
    body: use('vamb', 'url(#g-silverX)') + clip('vamb',
      // le rebord évasé du haut : sa face de dessus éclairée, son dessous qui fait de l'ombre
      shape('M207 287 C220 279 250 277 269 283 C268 287 266 290 264 292 C248 288 226 288 212 293 C209 292 207 290 207 287 Z', '#eef0f6', 0.6)
      + shape('M213 294 C228 289 250 289 265 293 L265 300 C250 296 228 296 213 301 Z', SIL.shade, 0.55)
      // le côté gauche dans l'ombre, l'arête du milieu éclairée
      + shape('M213 296 L220 296 C219 308 219 320 220 332 L213 332 Z', SIL.shade, 0.45)
      + shape('M236 296 C239 306 240 318 239 330 L244 330 C245 318 244 306 241 296 Z', '#ffffff', 0.85)
      + line('M245.5 298 C247.5 308 247.5 320 246.5 330', SIL.shade, 1.2, 0.7)
      // une ligne de plaques en travers
      + line('M214 312 C228 309 250 309 265 312', SIL.mid, 1.2, 0.75)
      // la bague du bas, évasée
      + shape('M211 333 C228 328 252 328 266 331 C270 336 271 343 271 351 C252 357 228 357 210 352 C209 344 209 338 211 333 Z', SIL.mid, 0.35)
      + line('M212 334 C228 329 252 329 266 332', '#ffffff', 1.6, 0.9)
      + line('M211 350 C228 355 252 355 270 350', SIL.shade, 1.8, 0.8)
      // deux rivets sur le rebord
      + dot(220, 287, 1.5, SIL.shade, 0.8) + dot(258, 285, 1.5, SIL.shade, 0.8)
    ) },
  { id: 'fistS', cls: 'a-sa', d: S.fistS, shadow: [{ on: ['vamb'], dx: -2, dy: 4, color: SH.armor, o: 0.4 }],
    body: use('fistS', 'url(#g-armor)') + clip('fistS',
      // le dos de la main : une plaque bordée d'argent sous le canon, un reflet froid
      shape('M215 348 C228 343 252 342 268 346 C273 352 276 360 274 362 L218 380 C214 372 214 360 215 348 Z', '#3e3c4c')
      + line('M216 349 C228 344 252 343 267 347', SIL.base, 1.6, 0.85)
      + shape('M246 347 C256 346 264 348 270 352 C262 351 254 350 246 351 Z', SPEC, 0.85) + oval(262, 349, 3, 1.2, '#ffffff', 0.85, 8)
      // les quatre jointures, alignées sur la poignée
      + oval(223, 378, 6.6, 3.4, '#4e4c62', 1, -18.6) + oval(236, 373.7, 6.6, 3.4, '#545268', 1, -18.6)
      + oval(249, 369.4, 6.6, 3.4, '#5a586e', 1, -18.6) + oval(262, 365.1, 6.6, 3.4, '#626078', 1, -18.6)
      + oval(225, 376.6, 3, 1.1, '#c4c2d8', 0.8, -18.6) + oval(238, 372.3, 3, 1.1, '#c4c2d8', 0.8, -18.6)
      + oval(251, 368, 3, 1.1, '#c4c2d8', 0.85, -18.6) + oval(264, 363.7, 3, 1.1, '#d4d2e6', 0.9, -18.6)
      // les doigts, refermés sur la poignée : quatre phalanges séparées par un sillon, le bout replié dessous
      + line('M229.8 379.7 C232 386 234 391 236.8 396.6 M242.6 375.4 C244.8 381.7 246.8 386.7 249.6 392.3 M255.4 371.1 C257.6 377.4 259.6 382.4 262.4 388', '#0e0d12', 1.4, 0.75)
      + shape('M227 384 C229 389 231 393 233 396 C230 393 228 389 226 385 Z M240 380 C242 385 244 389 246 392 C243 389 241 385 239 381 Z M253 375.5 C255 380.5 257 384.5 259 387.5 C256 384.5 254 380.5 252 376.5 Z M266 371 C268 376 270 380 272 383 C269 380 267 376 265 372 Z', '#8e8ca6', 0.7)
      + shape('M215 388 C220 397 236 404 254 398 C264 395 272 390 276 384 L278 406 L212 406 Z', '#0c0b10', 0.5)
    ) },

  // --- la tête : oreille, mèche de devant, épaulière, visage, mèche droite, chevelure du dessus, diadème ---
  { id: 'ear', d: S.ear, shadow: [{ on: BACK, dx: -4, dy: 3, color: SH.hair, o: 0.5 }],
    body: use('ear', 'url(#g-skin)')
      + shape('M261 138 C255 135 250 139 250 147 C250 156 254 164 259 168 C255 160 254 152 255 146 C256 142 258 139 261 138 Z', SKIN.shade, 0.8)
      + line('M259 145 C255 148 255 155 258 160', SKIN.line, 1.4, 0.7) },
  { id: 'sideL', cls: 'a-sl', d: S.sideL, shadow: [{ on: ['ear'], dx: -3, dy: 3, color: SH.skin, o: 0.45 }, { on: BACK, dx: -4, dy: 3, color: SH.hair, o: 0.5 }],
    body: use('sideL', 'url(#g-side)') + clip('sideL',
      shape('M286 128 C282 150 278 174 274 196 C272 206 270 214 268 220 C276 204 282 184 286 162 C288 148 288 136 286 128 Z', HAIR.sheen, 0.5)
      + shape('M284 142 C281 158 278 174 275 188 C280 174 283 158 285 144 Z', HAIR.hi, 0.55)
    ) },
  { id: 'pauL', d: S.pauL, shadow: [{ on: ['uarmS', 'torso', 'sideL', ...BACK], dx: -3, dy: 5, color: SH.armor, o: 0.5 }],
    body: use('pauL', '#2a2832') + clip('pauL',
      // la plaque du dessous : ses pointes, bordées d'argent
      shape('M242 251 C252 250 272 252 300 256 L297 260 L293 267 L287 261 L277 270 L271 263 L260 269 L255 261 C250 258 246 255 242 251 Z', '#2e2c38')
      + line('M246 254 L255 261 L260 269 L271 263 L277 270 L287 261 L293 267 L297 260 L303 256', SIL.base, 2, 0.9)
      + shape('M257 262 L260 268 L263 263 Z M273 264 L277 269 L280 264 Z M289 262 L293 266 L295 261 Z', '#ffffff', 0.85)
      // la coquille du dessus, bombée, ses deux cornes
      + `<path d="M258 241 C261 228 267 219 276 213 C276 209 275 205 272 200 C278 202 282 205 285 210 C290 207 296 206 301 207 C302 202 305 198 309 195 C310 200 310 205 308 210 C312 217 314 226 312 236 C311 242 309 247 306 251 C290 253 272 250 258 241 Z" fill="url(#g-plate)"/>`
      // son liseré d'argent le long du bord du haut, un reflet froid, un point de lumière
      + shape('M259 240 C262 227 268 218 277 212 C284 208 292 206 301 207 L301 210 C292 210 284 212 279 215 C270 221 264 230 262 241 Z', 'url(#g-rim)', 0.9)
      + shape('M270 226 C278 217 289 212 300 211 C290 215 281 221 274 230 Z', SPEC, 0.8)
      + oval(292, 213, 4, 1.6, '#ffffff', 0.85, -14)
      + shape('M304 212 C310 220 312 230 309 242 C313 234 314 222 310 213 Z', '#d6d4e6', 0.6)
      // l'ombre de la coquille sur la plaque du dessous
      + shape('M258 241 C272 250 290 253 306 251 L304 256 C288 258 270 255 256 247 Z', '#0c0b10', 0.5)
    ) },
  { id: 'face', d: S.face, rim: { on: ['neck', 'collar'], color: SKIN.line, w: 1, o: 0.5 },
    shadow: [{ on: ['neck', 'collar', 'torso', 'pauL', 'pauR'], dx: -2, dy: 7, color: SH.skin, o: 0.45 }, { on: BACK, dx: -3, dy: 6, color: SH.hair, o: 0.5 }],
    body: use('face', 'url(#g-skin)') + clip('face',
      `<rect x="289" y="70" width="44" height="150" fill="url(#g-faceL)"/>`
      + oval(372, 178, 46, 34, 'url(#g-cheekL)')
      + oval(313, 169, 13, 8, 'url(#g-blush)') + oval(421, 170, 8, 6, 'url(#g-blush)')
      // sous la mâchoire, l'ombre du cou
      + shape('M300 194 C312 207 334 215 362 216 C386 216 406 206 419 191 C410 206 390 214 362 214 C336 214 314 206 300 194 Z', SKIN.deep, 0.5)
    )
      // la marque du front : un croissant de lune
      + shape('M365.5 108 C365.5 115 368.5 119 372 119 C375.5 119 378.5 115 378.5 108 C376.5 112 374.5 113.8 372 113.8 C369.5 113.8 367.5 112 365.5 108 Z', '#3a2434')
      + dot(372, 109.2, 1.7, '#3a2434')
      // les yeux : grands iris, paupières lourdes, regard assuré
      + eye('eL', 'M300 148 C306 145 316 142.5 328 142 C339 141.8 350 144 358 150 C359 155 356 159.5 351 162 C342 165 324 164.5 314 161.5 C307 159 302 154 300 148 Z', 331, 150, 14,
        'M299 149 C296 144 292 139 287 134 C293 136 298 138 302 140 C311 136.5 326 134.5 340 136 C349 137 356 141 360 147 C361.5 149.5 361.5 152 360.5 154 C357 150 353 147 347 145 C337 142.5 322 142.5 311 144.5 C306 145.5 302.5 147 299 149 Z',
        'M302 151.5 C308 158.5 320 163.5 334 164 C344 164 352 161 357 154', 'M300 149 C316 155 344 155 359 149',
        'M297 140 C310 132 336 130 354 135 C359 138 362 142 362 147 C356 140 344 137 332 137 C318 137 306 139 298 144 Z', [-0.42, -0.08, 0.5, 0.22])
      // l'œil gauche : le même que le droit en miroir, un peu plus étroit (il est du côté éloigné)
      + eye('eR', 'M427.8 149.0 C423.0 146.0 415.0 143.5 405.4 143.0 C396.6 142.8 387.8 145.0 381.4 151.0 C380.6 156.0 383.0 160.5 387.0 163.0 C394.2 166.0 408.6 165.5 416.6 162.5 C422.2 160.0 426.2 155.0 427.8 149.0 Z', 403, 151, 13.5,
        'M428.6 150.0 C431.0 145.0 434.2 140.0 438.2 135.0 C433.4 137.0 429.4 139.0 426.2 141.0 C419.0 137.5 407.0 135.5 395.8 137.0 C388.6 138.0 383.0 142.0 379.8 148.0 C378.6 150.5 378.6 153.0 379.4 155.0 C382.2 151.0 385.4 148.0 390.2 146.0 C398.2 143.5 410.2 143.5 419.0 145.5 C423.0 146.5 425.8 148.0 428.6 150.0 Z',
        'M426.2 152.5 C421.4 159.5 411.8 164.5 400.6 165.0 C392.6 165.0 386.2 162.0 382.2 155.0', 'M427.8 150.0 C415.0 156.0 392.6 156.0 380.6 150.0',
        'M430.2 141.0 C419.8 133.0 399.0 131.0 384.6 136.0 C380.6 139.0 378.2 143.0 378.2 148.0 C383.0 141.0 392.6 138.0 402.2 138.0 C413.4 138.0 423.0 140.0 429.4 145.0 Z', [-0.42, -0.08, 0.5, 0.22])
      // les sourcils : épais, ils plongent vers le nez (le regard malicieux)
      + shape('M298 123 C306 118 318 116 330 118 C342 120 353 126 361 133 C364 136 362 139 358 138.5 C350 134 340 130 328 128 C318 126 308 126 300 128 C297 127 296 125 298 123 Z', '#221822')
      + shape('M425 116 C420 113 412 113 404 116 C396 119 389 124 385 130 C383 133 384 137 388 136.5 C393 131 400 126 408 123.5 C414 122 420 121 424 121 C427 120 427 117 425 116 Z', '#221822')
      + line('M306 120 C318 117.5 332 119 346 125', '#5a4458', 1.1, 0.55) + line('M418 115.5 C410 116.5 400 120.5 392 126', '#5a4458', 1.1, 0.55)
      // le nez
      + line('M380.5 160.5 C384.5 164 386 169 383.5 173 C381.5 175.5 378.5 176.5 375.5 176', SKIN.line, 1.5, 0.8)
      + oval(374, 174.5, 4.6, 2.2, SKIN.deep, 0.55, -8) + oval(382, 168, 1.8, 3, '#ffffff', 0.7, -10)
      // la bouche : un sourire en coin, lèvres rouges, une ligne de dents
      + shape('M346 184 C352 187 359 188.5 366 188.5 C375 188.5 382 186.5 388 183.5 C386 190 379 196.5 367.5 197.5 C356.5 197.5 349.5 192 346 184 Z', 'url(#g-lip)')
      + shape('M357 187.6 C364 189.4 372 189.4 380 187.2 L378.6 190.2 C372 191.4 364 191.4 358.6 190.2 Z', '#fff6f4')
      + shape('M357 193.5 C362.5 195.6 371 195.6 377 193.2 C371 194.4 362.5 194.6 357 193.5 Z', '#ffa8b0', 0.9)
      + line('M342.5 182 C350 186.5 358 188.4 366 188.4 C375 188.4 383 186.5 390.5 181.5', '#3e101e', 2.1)
      + line('M341 179.6 C341.8 181.4 343 182.6 344.6 183.4', '#3e101e', 1.6) + line('M392 179.4 C391.2 181.2 390 182.4 388.4 183.2', '#3e101e', 1.6)
      + line('M359 201 C364.5 202.4 370 202.4 375 201', SKIN.deep, 1.3, 0.65) },
  { id: 'sideR', cls: 'a-sr', d: S.sideR, shadow: [{ on: ['face'], dx: -3, dy: 4, color: SH.skin, o: 0.45 }, { on: ['armR', 'pauR', ...BACK], dx: -3, dy: 4, color: SH.hair, o: 0.5 }],
    body: use('sideR', 'url(#g-side)') + clip('sideR',
      oval(444, 156, 7, 26, 'url(#g-sheenSoft)', 0.8, 4)
    ) },
  { id: 'cap', d: S.cap, shadow: [{ on: ['face', 'ear'], dx: -3, dy: 7, color: SH.skin, o: 0.4 }, { on: ['sideL', 'sideR', ...BACK], dx: -3, dy: 6, color: SH.hair, o: 0.5 }],
    body: use('cap', 'url(#g-cap)') + clip('cap',
      // le reflet froid du dessus de la tête (à gauche) et le reflet chaud du côté éclairé
      shape('M238 72 C254 46 282 28 316 21 C290 34 268 54 254 78 C248 78 242 76 238 72 Z', HAIR.sheen, 0.5)
      + shape('M248 76 C258 60 274 46 294 37 C280 50 268 62 260 78 Z', HAIR.hi, 0.45)
      + oval(426, 58, 26, 11, 'url(#g-sheenSoft)', 0.8, 52)
      // le diadème : son bandeau suit le tour du crâne (un arc d'ellipse, plus fin sur les côtés qui fuient) ;
      // ses deux bouts passent sous les mèches qui tombent du sommet
      + shape(BAND, 'url(#g-band)')
      + line(BAND_TOP, '#f6f8fc', 1.1, 0.85) + line(BAND_LOW, SIL.shade, 1, 0.8)
      + shape('M300 90 C322 83 346 79 366 78 C388 79 412 83 444 94 L444 100 C412 90 388 86 366 85 C346 86 322 90 302 97 Z', HAIR.deep, 0.45)
      // la mèche de gauche passe sur le bandeau ; le bandeau s'assombrit en passant dessous
      + shape('M266 90 C273 96 278 103 281 111 L276 113 C273 106 268 99 261 94 Z', '#0c0b10', 0.5)
      + shape('M220 64 C238 74 256 86 270 98 C278 105 284 114 287 124 L282 134 L232 134 C222 118 214 98 220 64 Z', 'url(#g-cap)')
      + shape('M230 80 C244 90 258 102 268 116 C256 108 242 98 228 88 Z', HAIR.sheen, 0.45)
      + shape('M272 98 C279 104 284 112 287 124 L282 128 C280 118 276 108 268 100 Z', HAIR.deep, 0.4)
      // la mèche de droite, aussi
      + shape('M427 64 C430 74 433 84 435 93 L430 92 C428 84 426 75 423 66 Z', '#0c0b10', 0.45)
      + shape('M424 50 C437 60 448 74 454 88 C456 96 457 104 456 112 C450 106 443 100 436 95 C433 82 430 66 424 50 Z', 'url(#g-cap)')
      + shape('M436 76 C434 82 435 88 437 95 L432 90 C431 86 432 80 436 76 Z', HAIR.deep, 0.45)
      // les mèches du front, de part et d'autre
      + shape('M340 78 C334 86 326 96 318 104 C308 112 300 122 293 132 C300 116 312 100 326 88 Z', HAIR.sheen, 0.4)
      + shape('M404 80 C407 92 411 102 417 110 C424 120 430 128 435 136 C424 124 414 110 408 96 Z', HAIR.warm, 0.55)
    ) },
  { id: 'tiara', d: S.tiara, shadow: [{ on: ['cap', 'face'], dx: -3, dy: 5, color: SH.hair, o: 0.55 }],
    body:
      // chaque pointe a une face claire et une face dans l'ombre, de part et d'autre de son arête
      shape('M364 5 L354 40 L339 64 L350 72 L366 60 Z', '#f4f6fb') + shape('M364 5 L366 60 L398 58 L382 36 Z', '#a8aec2')
      + shape('M339 64 L350 72 C362 76 370 86 376 98 L366 60 Z', '#c8ccd8') + shape('M366 60 L376 98 C386 80 392 68 398 58 Z', '#7c8296')
      + shape('M306 51 L300 77 L318 69 Z', '#ffffff') + shape('M306 51 L318 69 L336 71 C324 65 314 57 306 51 Z', '#9aa0b4')
      + shape('M418 41 L406 71 L418 71 Z', '#f0f2f8') + shape('M418 41 L418 71 L428 77 C424 65 421 53 418 41 Z', '#8c92a6')
      + line('M364 5 L366 60 M339 64 L366 60 L398 58 M366 60 L376 98', '#ffffff', 1, 0.6)
      // la gemme rouge dans sa monture
      + shape('M371 36.5 L385.5 54 L373 73.5 L357.5 56 Z', '#eef1f7') + line('M371 36.5 L385.5 54 L373 73.5 L357.5 56 Z', '#6a6f84', 1, 0.7)
      + shape('M371 41 L381 54 L373 69 L362 56 Z', 'url(#g-gem)') + shape('M371 41 L381 54 L371 55 Z', '#ff8070', 0.8)
      + shape('M371 44 L376 51 L370 51 Z', '#ffe2d8', 0.95) + shape('M362 56 L373 69 L371 55 Z', RED.deep, 0.6) },

  // --- devant tout : la lame, puis la garde d'or ---
  { id: 'blade', cls: 'a-sw', d: S.blade, shadow: [{ on: ['torso', 'tassetL', 'tassetR', 'belt', 'skirt', 'fur', 'legR', 'cape', ...RIGHT, 'hairBack'], dx: -3, dy: 7, color: '#000', o: 0.35 }],
    body: use('blade', 'url(#g-bladeB)')
      // le tranchant du haut, éclairé ; l'arête au milieu
      + shape(`M${P(onAxis(288, -10.5))} L${P(onAxis(547, -10.5))} L566 272 L${P(onAxis(551, 0))} L${P(onAxis(288, 0))} Z`, 'url(#g-bladeT)')
      + line(`M${P(onAxis(300, 0))} L${P(onAxis(546, 0))}`, '#7a8098', 1.4, 0.8)
      + line(`M${P(onAxis(300, -9))} L${P(onAxis(540, -9))}`, '#ffffff', 1.3, 0.9)
      + line(`M${P(onAxis(300, 9.4))} L${P(onAxis(546, 9.4))}`, '#6a6f86', 1.2, 0.7)
      // la base décorée de la lame
      + shape(`M${P(onAxis(298, -6))} L${P(onAxis(318, -3))} L${P(onAxis(324, 0))} L${P(onAxis(318, 3))} L${P(onAxis(298, 6))} Z`, 'url(#g-gold)')
      // l'éclat qui court le long de la lame (au repos)
      + clip('blade', `<g class="a-glint" opacity="0"><path d="M${P(onAxis(300, -14))} L${P(onAxis(318, -14))} L${P(onAxis(306, 14))} L${P(onAxis(288, 14))} Z" fill="url(#g-glint)"/></g>`) },
  { id: 'guard', cls: 'a-sw', d: S.guard, shadow: [{ on: ['blade', 'fistS', 'tassetL', 'legL', 'torso'], dx: -3, dy: 4, color: '#000', o: 0.35 }],
    body: use('guard', 'url(#g-goldX)')
      + shape('M288 338 C290 350 292 362 296 374 C299 384 302 392 304 398 C300 394 296 384 293 374 C290 362 288 350 287 340 Z', GOLD.hi, 0.85)
      + shape('M283 330 C290 328 298 331 300 337 C296 334 290 333 285 334 Z', GOLD.hi, 0.9)
      + shape('M277 346 C279 360 283 374 287 386 C290 392 292 398 295 402 C290 400 286 394 284 388 C280 376 277 360 277 346 Z', GOLD.shade, 0.6)
      + `<circle cx="272.5" cy="371" r="7.5" fill="url(#g-gold)"/>` + oval(274, 368, 3.4, 2.2, GOLD.hi, 0.9, -20) },
];

// ---------- la vie au repos, puis l'attaque ----------
// Au repos : la chevelure et la cape ondulent, le poing levé se serre, l'épée suit le bras, un éclat court sur la lame,
// elle cligne des yeux. Attaque : chaque morceau qui bouge a sa version « .atk », qui finit exactement sur la pose de
// départ de son mouvement de repos (le passage de l'un à l'autre ne se voit pas).
const kf = (name, frames) => `@keyframes ${name}{${frames.map(([t, v, ease]) => `${n(t * 100)}%{transform:${v}${ease ? `;animation-timing-function:${ease}` : ''}}`).join('')}}`;
const R = (d) => `rotate(${d}deg)`;
const WX = WRIST[0] - SHOULDER[0], WY = WRIST[1] - SHOULDER[1];
const swordT = (A, B) => `rotate(${A}deg) translate(${WX}px,${WY}px) rotate(${B}deg) translate(${-WX}px,${-WY}px)`;
const FX = 494 - 418, FY = 186 - 222; // le poignet levé, depuis l'épaule
const fistT = (A, s) => `rotate(${A}deg) translate(${FX}px,${FY}px) scale(${s}) translate(${-FX}px,${-FY}px)`;
const style = [
  `.a-cape{transform-origin:350px 238px;animation:cape 3.8s ease-in-out infinite alternate}`,
  `.a-hl{transform-origin:248px 120px;animation:hl 4.4s ease-in-out infinite alternate}`,
  `.a-hl2{transform-origin:244px 252px;animation:hl2 3.6s ease-in-out infinite alternate-reverse}`,
  `.a-hr{transform-origin:448px 228px;animation:hr 3.4s ease-in-out infinite alternate}`,
  `.a-sl{transform-origin:286px 124px;animation:sl 3s ease-in-out infinite alternate}`,
  `.a-sr{transform-origin:442px 122px;animation:sr 3.2s ease-in-out -0.6s infinite alternate}`,
  `.a-fur{transform-origin:360px 324px;animation:fur 2.4s ease-in-out infinite alternate}`,
  `.a-raise{transform-origin:418px 222px;animation:raise 2.6s ease-in-out infinite alternate}`,
  `.a-fist{transform-origin:418px 222px;animation:fist 2.6s ease-in-out infinite alternate}`,
  `.a-sa{transform-origin:${SHOULDER[0]}px ${SHOULDER[1]}px;animation:sa 3s ease-in-out infinite alternate}`,
  `.a-sw{transform-origin:${SHOULDER[0]}px ${SHOULDER[1]}px;animation:sw 3s ease-in-out infinite alternate}`,
  `.a-glint{animation:glint 3.4s ease-in-out infinite}`,
  `.a-blink{animation:blink 4.6s linear infinite}`,
  kf('cape', [[0, R(-0.8)], [1, R(1)]]),
  kf('hl', [[0, R(-0.8)], [1, R(1)]]),
  kf('hl2', [[0, R(-1)], [1, R(1.3)]]),
  kf('hr', [[0, R(1)], [1, R(-1.2)]]),
  kf('sl', [[0, R(-1.2)], [1, R(1.2)]]),
  kf('sr', [[0, R(1)], [1, R(-1.4)]]),
  kf('fur', [[0, R(-1.4)], [1, R(1.4)]]),
  kf('raise', [[0, R(0)], [1, R(-1.6)]]),
  kf('fist', [[0, fistT(0, 1)], [1, fistT(-1.6, 0.965)]]),
  kf('sa', [[0, R(-0.5)], [1, R(0.7)]]),
  kf('sw', [[0, swordT(-0.5, 0)], [1, swordT(0.7, 0)]]),
  `@keyframes glint{0%{transform:translate(0px,0px);opacity:0}6%{opacity:1}34%{transform:translate(237px,-80px);opacity:0}100%{transform:translate(237px,-80px);opacity:0}}`,
  `@keyframes blink{0%,93%{opacity:0}94.5%,97%{opacity:1}98.5%,100%{opacity:0}}`,
  // l'attaque
  `.atk .a-sa{animation:sa-atk .75s linear both}.atk .a-sw{animation:sw-atk .75s linear both}`,
  `.atk .a-raise{animation:raise-atk .75s ease-in-out both}.atk .a-fist{animation:fist-atk .75s ease-in-out both}`,
  `.atk .a-hl{animation:hl-atk .75s ease-in-out both}.atk .a-hl2{animation:hl2-atk .75s ease-in-out both}.atk .a-hr{animation:hr-atk .75s ease-in-out both}`,
  `.atk .a-cape{animation:cape-atk .75s ease-in-out both}.atk .a-fur{animation:fur-atk .75s ease-in-out both}`,
  `.atk .a-trail{animation:trail .75s linear both}`,
  kf('sa-atk', SWING.map(([t, A], i) => [t, R(A), EASE[i]])),
  kf('sw-atk', SWING.map(([t, A, B], i) => [t, swordT(A, B), EASE[i]])),
  kf('raise-atk', [[0, R(0)], [0.3, R(-7)], [0.46, R(5)], [0.62, R(4)], [1, R(0)]]),
  kf('fist-atk', [[0, fistT(0, 1)], [0.3, fistT(-7, 0.94)], [0.46, fistT(5, 1.02)], [0.62, fistT(4, 1)], [1, fistT(0, 1)]]),
  kf('hl-atk', [[0, R(-0.8)], [0.3, R(1.6)], [0.48, R(-2.6)], [0.66, R(1.2)], [0.84, R(-1)], [1, R(-0.8)]]),
  kf('hl2-atk', [[0, R(1.3)], [0.3, R(3)], [0.5, R(-3.2)], [0.68, R(2.2)], [1, R(1.3)]]),
  kf('hr-atk', [[0, R(1)], [0.3, R(2.2)], [0.5, R(-3.6)], [0.68, R(1.6)], [0.86, R(-0.4)], [1, R(1)]]),
  kf('cape-atk', [[0, R(-0.8)], [0.3, R(-2)], [0.52, R(2.6)], [0.72, R(-1.2)], [1, R(-0.8)]]),
  kf('fur-atk', [[0, R(-1.4)], [0.3, R(3)], [0.48, R(-5)], [0.68, R(2.5)], [1, R(-1.4)]]),
  `@keyframes trail{0%,41%{opacity:0}44%{opacity:.9}46.5%{opacity:1}50%{opacity:.5}55%,100%{opacity:0}}`,
].join('');

// la traînée, posée devant tout (seulement dans l'image animée)
const TRAIL = `<g class="a-trail" opacity="0"><path d="${trailD}" fill="url(#g-trail)"/></g>`;
const svg = (anime = true) => {
  const s = figure({ w: W, h: H, pad: PAD, defs, style, parts, anime });
  return anime ? s.replace(/<\/svg>$/, `${TRAIL}</svg>`) : s;
};

module.exports = { id: 'mages-10', w: W, h: H, pad: PAD, foot: [356, 485], svg };
