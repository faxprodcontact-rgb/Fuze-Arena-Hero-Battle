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
const HAIR = { sheen: '#645a92', hi: '#b8b0e4', warm: '#9c7a48', warmHi: '#e6c48c', deep: '#09080f' };
const SKIN = { base: '#f8e8e6', shade: '#e6c6cc', deep: '#d2a2b0', line: '#a87482' };
const ARM = { hi: '#9a98b2', lite: '#5c5a6e' };
const SIL = { hi: '#ffffff', lite: '#e4e8f0', base: '#bfc4d2', mid: '#8e94a8', shade: '#5f6478' };
const GOLD = { hi: '#fff4b0', base: '#f4c040', mid: '#dc9a22', shade: '#a2660e', line: '#70420a' };
const RED = { base: '#e0222c', deep: '#8a0a16', line: '#5a0610' };
// les ombres portées : une teinte par matière qui la reçoit
const SH = { skin: '#9a5868', hair: '#05040a', armor: '#06050a', cape: '#1e040a' };
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

// ---------- l'attaque : l'épée tourne autour de l'épaule (A) et du poignet (B) ----------
const SHOULDER = [268, 250], WRIST = [244, 372];
// [instant, A, B] : repos, armé en arrière, coup porté, fin du geste, retour au repos
const SWING = [[0, -0.5, 0], [0.30, 22, -27], [0.46, -20, 56], [0.58, -23, 60], [1, -0.5, 0]];
const rot = (p, c, deg) => { const a = (deg * Math.PI) / 180, x = p[0] - c[0], y = p[1] - c[1]; return [c[0] + x * Math.cos(a) - y * Math.sin(a), c[1] + x * Math.sin(a) + y * Math.cos(a)]; };
/**
 * La traînée du coup, accrochée à la lame (elle tourne avec elle, juste derrière son tranchant du haut) : la zone que
 * la moitié extérieure de la lame vient de balayer, 16° en arrière autour du poignet, effilée vers l'arrière.
 */
const SMEAR = 16;
const smearD = (() => {
  const out = [], inn = [];
  for (let k = 0; k <= 10; k++) {
    const t = -SMEAR * (k / 10);
    out.push(rot([566, 272], WRIST, t));
    inn.push(rot(onAxis(470 + 64 * (k / 10), -10.5), WRIST, t));
  }
  const pts = [...out, ...inn.reverse()];
  return `M${pts.map((q) => `${n(q[0])} ${n(q[1])}`).join(' L')} Z`;
})();
const G0 = onAxis(522, -10.5), G1 = rot(onAxis(548, -10.5), WRIST, -SMEAR);

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
  lin('g-smear', G0[0], G0[1], n(G1[0]), n(G1[1]), [[0, '#ffffff', 0.9], [0.4, '#e4ecff', 0.5], [1, '#ffffff', 0]]),
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
  hl1: 'M244 52 C226 76 212 110 204 140 C196 172 182 204 158 226 C130 246 92 254 62 268 C40 280 24 300 14 324 C7 342 4 360 5 378 C10 362 18 346 30 330 C50 308 82 296 116 284 C152 270 186 252 210 226 C232 200 244 164 250 128 Z',
  hl2: 'M226 140 C214 176 194 214 160 240 C126 264 84 276 58 302 C40 322 32 350 29 378 C27 394 28 408 32 418 C36 404 42 386 52 366 C66 340 92 322 124 306 C164 286 204 262 232 224 Z',
  hl3: 'M232 182 C216 214 188 244 150 268 C114 290 84 312 68 346 C56 372 52 404 52 428 C52 436 53 442 55 447 C62 432 72 414 84 390 C100 360 126 336 160 316 C196 296 226 276 244 250 Z',
  hl4: 'M240 244 C220 270 188 292 156 314 C130 334 114 360 106 390 C101 408 99 426 100 440 C108 426 116 410 126 392 C142 368 166 350 194 336 C216 326 234 316 248 302 Z',
  hl5: 'M246 300 C226 318 200 336 176 352 C160 364 148 380 142 396 C138 404 136 410 136 414 C150 404 168 394 190 384 C210 376 230 370 248 364 Z',
  // la chevelure de droite : trois mèches qui tombent sous le bras levé
  hr1: 'M450 214 C478 230 508 250 532 276 C550 296 562 322 566 348 C568 360 567 370 565 378 C560 362 554 346 544 330 C528 304 504 286 478 270 C462 262 450 256 442 252 Z',
  hr2: 'M448 248 C472 270 496 296 514 326 C528 352 536 380 538 408 C539 422 538 434 536 445 C530 428 524 410 516 392 C504 362 486 336 466 314 C456 304 448 296 442 290 Z',
  hr3: 'M440 288 C456 312 472 338 482 366 C490 390 495 416 496 440 C496 448 495 455 494 462 C488 448 480 432 472 414 C462 392 450 372 438 356 Z',
  // les jambes, bottes comprises
  legL: 'M268 352 L322 352 C322 380 322 410 323 440 C327 452 330 466 330 484 L240 485 C240 470 245 455 252 443 C256 420 260 392 266 368 Z',
  legR: 'M380 352 L436 352 C438 380 441 410 448 444 C460 452 474 462 482 474 C484 478 484 482 482 485 L383 485 C380 474 381 462 384 452 C383 420 381 390 380 352 Z',
  // la jupe rouge sous la ceinture, le pan de fourrure entre les jambes, les tassettes sur les hanches
  skirt: 'M296 312 C330 320 380 320 416 308 L424 362 C404 370 382 374 360 374 C338 374 314 370 294 364 Z',
  fur: 'M330 322 L390 322 C392 345 390 370 386 392 C383 404 379 416 374 428 C368 440 360 448 353 453 C348 456 344 459 340 463 C336 452 333 440 330 430 C326 420 325 410 328 400 C328 370 328 345 330 322 Z',
  torso: 'M300 224 C320 221 345 221 368 223 C385 224 400 228 410 235 C414 255 412 280 408 300 C415 315 425 330 428 345 L292 350 C290 330 294 312 300 298 C296 280 294 255 300 224 Z',
  tassetL: 'M290 320 L334 326 C336 344 334 364 328 386 C314 390 300 388 290 382 C285 362 285 340 290 320 Z',
  tassetR: 'M392 324 L430 316 C437 332 441 354 437 376 C424 382 410 382 396 378 C392 360 391 342 392 324 Z',
  belt: 'M296 300 C330 306 380 305 412 297 L414 316 C380 325 330 326 294 320 Z',
  neck: 'M316 196 C326 200 342 202 352 198 L354 230 L314 230 Z',
  collar: 'M300 226 C316 216 350 215 368 222 C372 230 372 238 368 244 C346 239 322 239 300 244 C296 238 296 231 300 226 Z',
  // le bras levé, le poing serré, le bracelet d'argent, l'épaulière
  armR: 'M405 210 C425 204 445 200 460 194 C470 189 478 181 486 170 L507 199 C498 211 487 220 472 228 C456 236 438 243 418 246 C410 238 405 224 405 210 Z',
  fistR: 'M496 134 C496 126 501 120 508 119 C511 116 516 114 521 116 C524 114 529 113 534 115 C538 113 543 114 547 117 C552 118 556 123 556 129 C559 133 560 139 558 145 C560 151 559 158 555 163 C553 171 547 178 538 183 C530 189 518 193 507 193 C502 190 498 183 497 176 C494 168 493 158 494 150 C493 144 494 139 496 134 Z',
  cuffR: 'M479 178 C482 172 486 168 491 165 C498 173 504 182 509 191 C505 197 501 202 497 206 C491 197 485 187 479 178 Z',
  pauR: 'M389 214 C396 206 408 201 421 200 C425 197 429 195 433 194 C433 197 432 200 431 202 C441 203 448 208 451 216 C447 227 437 235 423 239 C410 241 398 237 391 229 C388 224 387 219 389 214 Z',
  // l'épée : longue poignée rouge baguée d'or, pommeau d'argent, lame, garde d'or
  grip: gripD,
  pommel: 'M147 408 C143 405 138 404 134 406 C130 409 126 415 124 421 C130 423 137 425 143 423 C147 421 149 417 148 413 Z',
  // le bras qui tient l'épée : bras, canon d'avant-bras en argent, gantelet
  uarmS: 'M252 236 L296 240 C294 262 282 280 268 292 L214 294 C220 274 234 254 252 236 Z',
  vamb: 'M211 290 C222 283 250 281 265 285 C267 300 266 318 266 333 C268 339 270 346 269 352 C252 357 228 357 211 351 C209 345 209 338 212 333 C211 318 210 302 211 290 Z',
  fistS: 'M216 349 C226 343 250 341 266 345 C272 355 273 371 270 385 C267 394 260 399 250 399 C238 400 226 398 220 392 C215 384 214 366 216 349 Z',
  // la tête
  ear: 'M264 131 C256 126 247 130 245 140 C243 152 247 164 255 171 C259 174 264 173 267 168 Z',
  sideL: 'M281 118 C274 140 268 164 264 188 C262 200 262 210 266 220 C272 222 278 220 282 214 C288 200 292 182 293 162 C294 146 293 132 291 120 Z',
  pauL: 'M242 252 C246 246 252 242 258 238 C262 226 270 216 280 210 C288 205 296 203 302 203 C304 200 306 198 309 196 C309 200 308 204 307 207 C311 214 313 224 311 234 C310 242 307 249 303 255 C299 259 295 262 291 266 C287 262 282 261 277 264 C272 261 267 261 261 266 C255 262 248 258 242 252 Z',
  face: 'M291 70 L289 145 C289 166 292 182 300 194 C312 207 334 215 362 216 C386 216 406 206 419 191 C428 178 433 162 433 142 L433 70 Z',
  sideR: 'M430 126 C433 144 432 162 427 178 C423 190 419 198 421 206 C429 211 439 210 446 206 C451 190 453 168 453 146 C453 134 452 124 450 114 Z',
  cap: 'M226 72 C244 40 290 12 336 9 C384 6 428 30 446 70 C452 86 454 104 453 124 C449 130 442 134 435 136 C430 128 424 120 417 110 C411 102 407 92 404 80 C390 76 360 74 340 78 C334 86 326 96 318 104 C308 112 300 122 293 132 C286 132 278 131 270 131 C258 132 248 130 238 122 C228 114 222 102 222 90 C222 84 224 78 226 72 Z',
  tiara: 'M364 5 C368 16 374 26 382 36 L398 58 C392 68 386 80 376 98 C370 86 362 76 350 72 L339 64 L354 40 C358 28 361 16 364 5 Z M306 46 C314 52 324 60 336 66 L300 72 C300 62 302 54 306 46 Z M418 36 C421 48 424 60 428 72 L406 66 C410 56 414 46 418 36 Z',
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
    body: lock('hl1', 'url(#g-hairL)',
      'M232 92 C220 130 208 176 182 210 C152 244 104 262 66 282 C44 296 30 316 20 340 C40 312 70 296 104 282 C146 264 184 244 206 212 C224 184 232 140 236 96 Z',
      'M224 128 C216 156 204 184 184 206 C176 214 168 220 158 226 C172 222 182 214 190 204 C206 184 218 160 226 132 Z',
      'M250 128 C244 164 232 200 210 226 C186 252 152 270 116 284 C82 296 50 308 30 330 C40 316 60 304 84 296 C122 282 160 266 188 244 C214 222 236 186 246 140 Z') },
  { id: 'hl2', cls: 'a-hl', d: S.hl2, shadow: [{ on: ['hl1'], dx: -6, dy: 3, color: SH.hair, o: 0.5 }],
    body: lock('hl2', 'url(#g-hairL)',
      'M214 180 C196 214 168 240 130 262 C98 280 68 298 50 326 C44 340 38 356 34 374 C44 344 62 318 92 300 C130 278 170 256 196 226 C206 214 212 198 214 180 Z',
      'M198 210 C186 224 172 236 154 248 C170 242 186 230 198 210 Z',
      'M232 224 C204 262 164 286 124 306 C92 322 66 340 52 366 C46 380 40 398 34 414 C42 392 54 368 72 348 C98 324 132 306 168 288 C198 270 222 250 232 224 Z', HAIR.sheen, HAIR.hi, 0.85) },
  { id: 'hl3', cls: 'a-hl', d: S.hl3, shadow: [{ on: ['hl1', 'hl2'], dx: -6, dy: 3, color: SH.hair, o: 0.5 }],
    body: lock('hl3', 'url(#g-hairL)',
      'M222 214 C204 240 176 262 140 284 C110 302 88 322 76 350 C68 370 62 396 58 420 C68 390 80 364 98 342 C122 316 154 298 186 278 C204 266 216 244 222 214 Z',
      'M204 244 C192 256 178 266 162 276 C178 270 194 258 204 244 Z',
      'M244 250 C224 276 196 296 160 316 C126 336 100 360 84 390 C74 410 64 428 56 444 C66 420 80 392 98 368 C122 336 156 316 190 298 C214 284 234 270 244 250 Z', HAIR.sheen, HAIR.hi, 0.7) },
  { id: 'hl4', cls: 'a-hl2', d: S.hl4, shadow: [{ on: ['hl2', 'hl3'], dx: -6, dy: 3, color: SH.hair, o: 0.5 }],
    body: lock('hl4', 'url(#g-hairL)',
      'M232 262 C210 282 180 302 152 324 C130 342 118 364 110 392 C106 408 104 424 102 436 C110 404 124 374 146 352 C172 326 204 306 228 280 C232 276 234 268 232 262 Z',
      'M214 286 C204 296 192 306 180 316 C192 310 204 300 214 286 Z', '', HAIR.sheen, HAIR.hi, 0.6) },
  { id: 'hl5', cls: 'a-hl2', d: S.hl5, shadow: [{ on: ['hl3', 'hl4'], dx: -6, dy: 3, color: SH.hair, o: 0.5 }],
    body: lock('hl5', 'url(#g-hairL)',
      'M236 314 C216 330 194 344 174 358 C160 368 150 382 144 398 C156 382 172 368 192 356 C210 344 228 330 236 314 Z', '', '', HAIR.sheen, HAIR.hi, 0.55) },
  { id: 'hr1', cls: 'a-hr', d: S.hr1,
    body: lock('hr1', 'url(#g-hairR)',
      'M474 234 C500 250 524 270 540 294 C552 312 558 330 562 346 C552 326 540 308 526 294 C510 278 492 262 472 244 Z',
      'M504 258 C516 268 526 278 534 290 C526 282 516 274 506 266 Z',
      '', HAIR.warm, HAIR.warmHi) },
  { id: 'hr2', cls: 'a-hr', d: S.hr2, shadow: [{ on: ['hr1'], dx: -5, dy: 3, color: SH.hair, o: 0.5 }],
    body: lock('hr2', 'url(#g-hairR)',
      'M466 270 C486 292 504 316 518 344 C526 362 530 378 532 394 C524 374 514 356 504 340 C492 320 478 302 462 284 Z',
      'M490 304 C500 316 508 328 514 342 C506 332 498 322 490 312 Z',
      'M442 290 C458 306 474 324 488 344 C502 366 512 390 518 414 C508 392 496 370 480 350 C468 334 456 320 442 306 Z', HAIR.warm, HAIR.warmHi) },
  { id: 'hr3', cls: 'a-hr', d: S.hr3, shadow: [{ on: ['hr2', 'cape'], dx: -5, dy: 3, color: SH.hair, o: 0.5 }],
    body: lock('hr3', 'url(#g-hairR)',
      'M454 306 C468 328 478 352 486 380 C490 398 492 414 493 428 C488 410 482 392 476 376 C468 352 458 330 448 312 Z',
      'M468 340 C474 352 478 364 481 378 C476 368 471 358 466 348 Z',
      '', HAIR.warm, HAIR.warmHi) },

  // --- les jambes : grèves noires, genouillère bordée d'argent, solerets à plaques ---
  { id: 'legL', d: S.legL, shadow: [{ on: ['cape', ...BACK], dx: -5, dy: 3, color: SH.armor, o: 0.45 }],
    body: use('legL', 'url(#g-armorX)') + clip('legL',
      shape('M300 352 C306 380 308 410 308 438 L322 440 L322 352 Z', ARM.lite, 0.55)
      + shape('M310 380 C313 398 314 414 314 430 C317 414 317 398 315 380 Z', ARM.hi, 0.7)
      // la genouillère
      + shape('M250 433 C272 429 300 429 324 433 L326 448 C300 444 274 444 250 448 Z', '#1a1820')
      + line('M251 434 C274 430 300 430 324 434', SIL.base, 2.2) + line('M251 447 C274 443 300 443 325 447', SIL.mid, 1.6, 0.8)
      + oval(312, 438, 6, 1.6, '#ffffff', 0.8, -4)
      // le soleret : quatre plaques arrondies, éclairées en haut à droite
      + shape('M246 458 C258 452 274 451 288 453 C302 451 318 453 329 460 L330 486 L240 486 Z', '#2a2832')
      + shape('M243 470 C245 463 252 460 258 461 C263 463 265 468 265 474 L265 486 L242 486 C241 480 242 475 243 470 Z', '#3c3a48')
      + shape('M265 468 C266 461 272 458 278 459 C284 460 287 465 287 471 L287 486 L265 486 Z', '#42404e')
      + shape('M287 468 C288 461 294 458 300 459 C306 460 309 465 309 471 L309 486 L287 486 Z', '#474554')
      + shape('M309 469 C310 463 316 460 322 461 C327 463 330 468 330 474 L330 486 L309 486 Z', '#4c4a5a')
      + line('M246 466 C249 462 253 461 257 461.5 M268 463 C271 460 275 459.5 279 460 M290 463 C293 460 297 459.5 301 460 M312 464 C315 461.5 319 461 323 462', '#a4a2ba', 1.8, 0.8)
      + shape('M238 480 L332 480 L332 487 L238 487 Z', '#141218', 0.55)
    ) },
  { id: 'legR', d: S.legR, shadow: [{ on: ['cape', ...BACK], dx: -5, dy: 3, color: SH.armor, o: 0.45 }],
    body: use('legR', 'url(#g-armorX)') + clip('legR',
      shape('M418 352 C424 382 428 412 434 440 L448 446 C442 414 438 382 436 352 Z', ARM.lite, 0.55)
      + shape('M428 384 C431 400 433 416 436 432 C437 414 435 398 432 384 Z', ARM.hi, 0.7)
      + shape('M382 438 C404 434 428 434 450 440 L456 454 C432 449 406 448 383 452 Z', '#1a1820')
      + line('M383 439 C404 435 428 435 450 441', SIL.base, 2.2) + line('M384 452 C406 448 432 449 456 454', SIL.mid, 1.6, 0.8)
      + oval(438, 443, 6, 1.6, '#ffffff', 0.8, 6)
      + shape('M384 462 C400 455 424 453 446 455 C462 457 474 464 482 472 L484 487 L382 487 Z', '#2a2832')
      + shape('M384 472 C386 465 392 462 398 463 C404 464 407 469 407 475 L407 487 L383 487 C383 481 383 476 384 472 Z', '#3c3a48')
      + shape('M407 469 C408 462 415 459 421 460 C428 461 431 466 431 472 L431 487 L407 487 Z', '#42404e')
      + shape('M431 468 C433 461 440 459 446 460 C453 462 456 467 456 473 L456 487 L431 487 Z', '#474554')
      + shape('M456 469 C459 464 466 463 472 466 C478 469 482 474 483 479 L484 487 L456 487 Z', '#4e4c5c')
      + line('M387 467 C390 464 394 463 398 463.5 M410 464 C413 461 417 460.5 421 461 M434 463 C437 460.5 441 460 445 461 M460 466 C464 464 468 464.5 472 466.5', '#a4a2ba', 1.8, 0.8)
      + shape('M380 480 L486 480 L486 487 L380 487 Z', '#141218', 0.55)
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

  // --- le buste : plastron noir à deux coques, gemme rouge, liserés d'argent ---
  { id: 'torso', d: S.torso, shadow: [{ on: BACK, dx: -5, dy: 3, color: SH.hair, o: 0.5 }, { on: ['cape'], dx: -5, dy: 3, color: SH.cape, o: 0.45 }],
    body: use('torso', 'url(#g-armor)') + clip('torso',
      // les deux coques du plastron
      `<path d="M304 250 C312 240 334 238 350 246 C358 258 358 276 350 288 C336 294 314 292 304 284 C298 274 298 260 304 250 Z" fill="#2c2a35"/>`
      + `<path d="M368 244 C380 236 400 237 410 246 C414 260 412 276 404 286 C392 291 376 290 366 282 C362 270 363 256 368 244 Z" fill="#33313d"/>`
      + shape('M314 248 C326 242 340 243 348 250 C340 248 328 248 318 252 Z', ARM.hi, 0.75)
      + shape('M376 243 C390 238 403 241 408 250 C400 246 390 245 380 247 Z', ARM.hi, 0.9)
      + oval(394, 257, 8, 5, '#8a889e', 0.45, -18) + oval(331, 259, 7, 4.4, '#76748a', 0.35, -12)
      + oval(398, 254, 3.4, 1.6, '#ffffff', 0.8, -24) + oval(336, 255, 3, 1.4, '#ffffff', 0.6, -20)
      + shape('M304 284 C314 292 336 294 350 288 L350 296 C334 302 312 300 302 292 Z', '#141218', 0.55)
      + shape('M366 282 C376 290 392 291 404 286 L406 294 C392 300 374 298 364 290 Z', '#141218', 0.5)
      // le galon rouge qui descend de la gemme, sa pointe d'argent
      + shape('M355 268 L373 268 L366 296 L362 296 Z', '#7e1420')
      + shape('M359 270 L369 270 L364 292 Z', '#b02a36', 0.8)
      + shape('M360 290 L368 290 L364 300 Z', SIL.base)
      // les rivets, au bord du col
      + dot(316, 244, 1.8, SIL.lite) + dot(340, 238, 1.6, SIL.lite) + dot(404, 248, 1.8, SIL.lite) + dot(384, 236, 1.6, SIL.lite)
      + dot(306, 276, 1.4, SIL.base, 0.8) + dot(406, 274, 1.4, SIL.base, 0.8)
      // le côté droit, éclairé
      + shape('M404 240 C410 262 410 284 406 300 L414 300 C416 280 414 258 410 236 Z', ARM.lite, 0.7)
    )
      // la gemme du cœur, dans sa monture d'argent
      + shape('M364 246 C370.5 247 376 252.5 377 260 C377 268 371.5 275 364.5 281 C357.5 275 352 268 352 260 C353 252.5 357.5 247 364 246 Z', SIL.base)
      + shape('M364.5 249.5 C369 250.5 373 255 373.5 260.5 C373.5 266.5 369.5 271.5 364.5 276 C359.5 271.5 355.5 266.5 355.5 260.5 C356 255 360 250.5 364.5 249.5 Z', 'url(#g-gem)')
      + shape('M366 252 C369 253.5 370.5 256.5 370.5 259.5 C368 257.5 366.5 255 366 252 Z', '#ffe2d8', 0.95) },
  { id: 'tassetL', d: S.tassetL, shadow: [{ on: ['legL', 'fur', 'skirt'], dx: -3, dy: 5, color: SH.armor, o: 0.45 }],
    body: use('tassetL', 'url(#g-armor)') + clip('tassetL',
      shape('M290 376 C302 382 318 384 332 380 L330 392 L288 392 Z', SIL.base)
      + line('M290 377 C302 383 318 385 332 381', SIL.hi, 1.4, 0.9)
      + shape('M314 330 C326 334 332 348 332 364 C328 350 322 338 312 334 Z', ARM.hi, 0.6)
      + oval(322, 340, 3.4, 1.5, '#ffffff', 0.7, 40)
    ) },
  { id: 'tassetR', d: S.tassetR, shadow: [{ on: ['legR', 'fur', 'cape', 'skirt'], dx: -3, dy: 5, color: SH.armor, o: 0.45 }],
    body: use('tassetR', 'url(#g-armorX)') + clip('tassetR',
      shape('M396 372 C408 377 422 377 438 370 L440 384 L394 384 Z', SIL.base)
      + line('M397 373 C409 378 422 378 437 371', SIL.hi, 1.4, 0.9)
      + shape('M416 324 C428 332 434 346 436 362 C428 348 420 336 410 328 Z', ARM.hi, 0.7)
      + oval(426, 334, 3.4, 1.5, '#ffffff', 0.8, 50)
    ) },
  { id: 'belt', d: S.belt, shadow: [{ on: ['torso', 'fur', 'skirt', 'tassetL', 'tassetR'], dx: -2, dy: 4, color: SH.armor, o: 0.5 }],
    body: use('belt', '#24222c') + clip('belt',
      line('M296 302 C330 308 380 307 412 299', SIL.base, 2, 0.9)
      + line('M295 318 C330 324 380 323 413 314', SIL.mid, 1.6, 0.7)
      + shape('M390 300 L412 297 L414 316 L392 320 Z', '#3c3a48', 0.7)
      + shape('M298 304 L318 307 L318 323 L296 320 Z', '#3c3a48', 0.5)
    )
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
      shape('M410 214 C432 208 452 203 466 195 C474 190 480 183 486 175 C478 190 466 200 450 206 C436 211 422 214 410 218 Z', ARM.hi, 0.6)
      + shape('M420 240 C440 236 458 230 474 222 C488 214 498 206 506 198 L508 206 C496 216 480 226 462 234 C446 240 430 244 418 246 Z', '#121016', 0.5)
      // le renflement du coude, un éclat de lumière sur le dessus
      + shape('M446 206 C456 202 466 198 474 190 C470 200 462 208 450 212 Z', '#7e7c94', 0.6)
      + oval(462, 200, 7, 2, '#ffffff', 0.6, -30) + oval(430, 209, 6, 1.7, '#ffffff', 0.45, -12)
    ) },
  { id: 'fistR', cls: 'a-fist', d: S.fistR,
    body: use('fistR', 'url(#g-armor)') + clip('fistR',
      // les quatre jointures (le haut du poing), éclairées par le haut
      shape('M496 136 C496 127 501 121 508 120 C512 124 514 131 512 138 C506 141 500 140 496 136 Z', '#4a4858')
      + shape('M509 119 C512 116 517 115 521 116 C524 114 529 114 533 116 C534 123 533 131 529 137 C523 139 517 139 512 137 C514 130 513 124 509 119 Z', '#56546a')
      + shape('M533 116 C538 114 543 115 547 118 C549 125 548 132 544 138 C539 139 534 138 530 136 C533 130 534 123 533 116 Z', '#5e5c74')
      + shape('M547 118 C552 119 556 124 556 130 C558 135 557 140 554 144 C551 145 548 144 545 143 C547 135 548 126 547 118 Z', '#66647c')
      + line('M499 128 C502 123 506 121 509 121 M513 117.5 C517 116 521 116 524 115.5 M528 115 C532 114.6 536 114.8 539 115.4 M542 115.8 C546 116.6 550 118.6 553 121.6', '#d8d6ea', 1.8, 0.9)
      // les doigts repliés : quatre phalanges bombées, séparées par un sillon
      + shape('M495 140 C512 145 535 146 558 141 C559 149 558 156 555 162 C534 166 512 166 494 161 C493 154 493 147 495 140 Z', '#302e3a')
      + shape('M498 143 C503 145 508 146 512 146 C511 150 510 154 508 157 C504 155 500 153 497 150 Z', '#46445a', 0.8)
      + shape('M515 146 C520 147 525 147.4 529 147.4 C528 151 527 155 525 158 C521 157 517 156 514 154 Z', '#4c4a60', 0.8)
      + shape('M532 147.4 C537 147 541 146.6 545 146 C545 150 544 154 542 157 C538 157 534 157 531 156 Z', '#54526a', 0.8)
      + shape('M548 145.4 C551 145 554 144 557 143 C557 148 556 152 554 156 C552 156 550 156 547 155 Z', '#5c5a72', 0.8)
      + line('M513.5 139 C514.5 146 514.5 153 513.5 161 M530 139 C531 146 531 154 530 162 M546 141 C547 147 547 154 546 161', '#121016', 1.3, 0.7)
      // le pouce, en travers devant les doigts
      + shape('M496 168 C505 161 520 158 534 160 C542 162 547 167 547 173 C539 181 524 185 508 184 C501 180 496 174 496 168 Z', '#3e3c4a')
      + shape('M501 165 C511 161 525 160 536 163 C525 163 513 165 503 168 Z', '#c4c2d8', 0.75)
      + line('M518 170 C526 170 533 172 539 176', '#121016', 1.3, 0.55)
      // une petite gemme rouge sur le gantelet
      + oval(521, 153, 3.6, 3, 'url(#g-gem)') + dot(522.2, 151.9, 1, '#ffe2d8')
      + shape('M500 182 C512 190 528 190 546 180 L548 194 L498 200 Z', '#121016', 0.45)
    ) },
  { id: 'cuffR', cls: 'a-raise', d: S.cuffR, shadow: [{ on: ['armR', 'fistR'], dx: -3, dy: 4, color: SH.armor, o: 0.5 }],
    body: use('cuffR', 'url(#g-silver)') + clip('cuffR',
      line('M484 172 C490 180 496 190 502 200', SIL.shade, 2.6, 0.6)
      + line('M489 168 C495 176 501 185 506 193', SIL.hi, 2, 0.9)
    ) },
  { id: 'pauR', d: S.pauR, shadow: [{ on: ['armR', 'torso', 'collar'], dx: -3, dy: 5, color: SH.armor, o: 0.5 }],
    body: use('pauR', 'url(#g-armor)') + clip('pauR',
      shape('M392 213 C400 205 413 201 427 201 C440 202 449 207 451 216 C440 210 426 207 412 209 C404 210 397 212 392 216 Z', SIL.base)
      + shape('M404 208 C414 204 428 204 440 207 C428 206 416 207 406 210 Z', SIL.hi, 0.9)
      + shape('M398 226 C410 232 426 232 442 224 L448 228 C434 240 410 242 394 234 Z', '#121016', 0.55)
      + line('M402 222 C414 226 428 225 440 219', '#2a2832', 1.4, 0.6)
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
      + oval(282, 266, 2.4, 6, '#ffffff', 0.5, 30)
    ) },
  { id: 'vamb', cls: 'a-sa', d: S.vamb, shadow: [{ on: ['uarmS', ...BACK, 'cape'], dx: -4, dy: 4, color: SH.armor, o: 0.45 }],
    body: use('vamb', 'url(#g-silverX)') + clip('vamb',
      // le rebord du haut, la bague du bas évasée
      shape('M209 290 C222 283 250 281 267 285 L267 296 C250 292 224 293 209 299 Z', SIL.shade, 0.55)
      + line('M211 291 C222 285 250 283 265 287', SIL.hi, 1.6, 0.9)
      + shape('M209 334 C226 330 252 330 270 334 L272 356 L208 356 Z', SIL.mid, 0.5)
      + line('M210 334 C226 330 252 330 268 334', SIL.hi, 1.8)
      + line('M211 350 C228 354 252 354 269 350', SIL.shade, 2, 0.8)
      + shape('M246 290 C250 302 251 318 250 330 C253 318 254 302 251 290 Z', '#ffffff', 0.85)
    ) },
  { id: 'fistS', cls: 'a-sa', d: S.fistS, shadow: [{ on: ['vamb'], dx: -2, dy: 4, color: SH.armor, o: 0.4 }],
    body: use('fistS', 'url(#g-armor)') + clip('fistS',
      // le dos de la main, puis les doigts serrés sur la poignée
      shape('M220 350 C232 345 252 344 266 347 C268 355 266 362 262 366 C246 364 230 364 218 368 Z', '#4a4858')
      + shape('M226 350 C238 347 252 347 262 349 C252 350 238 351 228 354 Z', '#c4c2d8', 0.8)
      + shape('M218 372 C228 368 244 368 258 370 C266 372 270 378 270 384 C262 382 250 381 238 382 C228 382 220 384 216 386 Z', '#3e3c4a')
      + shape('M216 388 C226 384 242 384 256 386 C264 387 268 390 268 392 C262 397 254 399 246 399 C234 400 224 398 218 393 Z', '#36343f')
      + line('M220 370 C232 367 248 367 262 370 M218 386 C230 383 246 383 262 386', ARM.hi, 1.6, 0.8)
      + line('M238 372 C240 376 240 380 238 384 M252 372 C254 376 254 380 252 384', '#121016', 1.4, 0.55)
      + shape('M214 392 C226 400 248 402 270 394 L270 404 L212 404 Z', '#121016', 0.5)
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
      // la plaque du dessous, ses pointes bordées d'argent
      line('M243 252 C248 257 254 262 261 265 C266 261 271 261 277 263 C282 261 287 262 291 265 C296 261 300 257 303 253', SIL.base, 2.4, 0.95)
      + shape('M259 258 L262 266 L265 259 Z M275 258 L277.5 264.5 L280 258 Z', SIL.hi, 0.9)
      + line('M246 250 C258 245 280 244 300 250', SIL.mid, 1.6, 0.7)
      // la grande plaque du dessus : une coquille bombée, son crochet relevé
      + `<path d="M258 240 C262 226 270 216 280 210 C288 205 296 203 302 203 C304 200 306 198 309 196 C309 200 308 204 307 207 C311 214 313 224 311 234 C310 240 308 245 305 249 C290 250 272 247 258 240 Z" fill="url(#g-plate)"/>`
      + shape('M264 230 C272 218 284 210 298 207 C288 212 278 220 270 232 Z', '#ffffff', 0.85)
      + shape('M302 210 C308 218 310 230 307 242 C312 234 313 222 309 212 Z', '#d6d4e6', 0.7)
      + shape('M258 240 C272 247 290 250 305 249 L303 254 C288 256 270 252 256 245 Z', '#121016', 0.5)
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
      + eye('eL', 'M301 146 C306 139 318 135 333 135 C345 135 353 139 357 145 C358 151 356 157 351 160 C342 163.5 324 163 314 160 C307 157 302 152 301 146 Z', 333.3, 148, 14.5,
        'M301 147 C298 141 295 134 291 127 C296 130 300 132 305 133 C314 130 324 129.5 334 130 C346 130.5 355 134 359 140 C361 143 362 147 361 151 C358 146 355 142 351 139.5 C344 136 337 135.5 331 135.5 C320 135.5 311 137.5 305 141.5 Z M350 134 L357 129.5 L355 135.5 Z M355 137 L361.5 134.5 L358.5 140 Z',
        'M302 149 C308 157 320 162.5 334 163 C344 163 352 160 357 152', 'M302 147 C316 154 344 154 359 147',
        'M296 129 C310 122 336 121 352 126 C358 129 362 134 362 140 C356 132 344 129 332 129 C318 129 306 132 298 136 Z', [-0.46, -0.4, 0.53, -0.08])
      + eye('eR', 'M386.5 147 C388 141 395 137.5 404 136 C412 135 418 136 421.5 140 C423 146 421 153 416 157.5 C408 162 395 161.5 390.5 157 C387.5 154 386 150.5 386.5 147 Z', 402.5, 148.8, 11.5,
        'M385 149 C384 142 388 137 395 134 C403 131 412 130 420 130 C424 129.5 428 127.5 431 124.5 C430.5 129 428.5 132.5 425 135 L422 138 C416 135.5 409 135.5 402 136.5 C394.5 138 389.5 142.5 387.5 149 Z M424 131 L432 128.5 L427 134 Z',
        'M387 151 C391 158 400 162 409 161.5 C415 161 419 157 421.5 150', 'M386.5 148 C397 153.5 412 153.5 422 146',
        'M386 134 C394 127 408 124 420 125 C425 126 428 128 430 131 C420 129 408 130 398 133 C394 134.5 390 137 387 140 Z', [-0.46, -0.4, 0.53, -0.08])
      // les sourcils : épais, froncés vers le nez
      + shape('M302 123 C312 119 328 118 342 121 C351 123 358 127 362 131 C363 135 360 137 356 136 C346 132 334 128 320 126 C312 125 306 125 302 126 Z', '#221822')
      + shape('M385 130 C389 124 398 120 408 117 C413 115.5 418 115 421 115.5 C423 116.5 423 119 420 120 C412 121 403 124 395 128 C391 130.5 388 133 386 133 C384.5 133 384 131.5 385 130 Z', '#221822')
      + line('M310 121 C322 119 336 120 348 124', '#5a4458', 1.1, 0.55) + line('M392 124 C400 120 410 117.5 418 117', '#5a4458', 1.1, 0.55)
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
      shape('M446 124 C449 142 449 160 446 176 C450 162 451 146 450 132 C449 128 448 126 446 124 Z', HAIR.warm, 0.6)
      + shape('M448 136 C449 146 449 156 447 166 C450 156 450 146 449 138 Z', HAIR.warmHi, 0.5)
      + shape('M433 144 C434 160 432 174 427 188 C433 178 436 162 436 148 Z', HAIR.sheen, 0.35)
    ) },
  { id: 'cap', d: S.cap, shadow: [{ on: ['face', 'ear'], dx: -3, dy: 7, color: SH.skin, o: 0.4 }, { on: ['sideL', 'sideR', ...BACK], dx: -3, dy: 6, color: SH.hair, o: 0.5 }],
    body: use('cap', 'url(#g-cap)') + clip('cap',
      // le reflet froid du dessus de la tête (à gauche) et le reflet chaud du côté éclairé
      shape('M238 72 C254 46 282 28 316 21 C290 34 268 54 254 78 C248 78 242 76 238 72 Z', HAIR.sheen, 0.5)
      + shape('M248 76 C258 60 274 46 294 37 C280 50 268 62 260 78 Z', HAIR.hi, 0.45)
      + shape('M404 30 C422 42 436 58 444 78 C446 86 447 94 447 100 C440 82 430 66 418 52 C412 44 408 36 404 30 Z', HAIR.warm, 0.6)
      + shape('M422 52 C430 62 436 72 440 84 C434 76 428 68 422 60 Z', HAIR.warmHi, 0.55)
      // le diadème : son bandeau fait le tour de la tête (plus épais devant, plus fin sur les côtés) ;
      // les mèches qui tombent du sommet le recouvrent de chaque côté
      + `<path d="M232 112 C244 106 252 102 262 98 C276 92 288 86 300 82 C314 77 328 73 344 70 C360 67 376 66 392 66 C406 67 418 69 430 72 C440 75 450 78 458 82 L458 88 C450 84 440 82 430 80 C418 77 406 76 392 75.5 C376 75.5 360 77 344 79.5 C328 82 314 86 302 91 C288 96 276 100 264 104 C254 108 244 112 234 117 Z" fill="url(#g-band)"/>`
      + line('M233 112.5 C262 98.5 300 82.5 344 70.5 C376 66.5 406 67.5 430 72.5 C442 75.5 450 78.5 458 82.5', '#f6f8fc', 1.1, 0.85)
      + line('M235 116 C264 103 302 90 344 78.8 C376 74.8 406 75.8 430 79.5 C442 81.5 450 84 458 87.5', SIL.shade, 1, 0.8)
      + shape('M300 92 C322 85 346 80 370 79 C394 79 420 82 452 92 L452 98 C420 89 394 86 370 86 C346 87 322 91 302 98 Z', HAIR.deep, 0.5)
      // la mèche de gauche passe sur le bandeau
      + shape('M220 64 C238 74 256 86 270 98 C278 105 284 114 287 124 L282 134 L232 134 C222 118 214 98 220 64 Z', 'url(#g-cap)')
      + shape('M262 92 C268 96 272 100 275 104 C270 104 266 104 262 106 Z', HAIR.deep, 0.5)
      + shape('M230 80 C244 90 258 102 268 116 C256 108 242 98 228 88 Z', HAIR.sheen, 0.45)
      + shape('M236 88 C246 96 254 104 260 112 C252 106 244 100 236 94 Z', HAIR.hi, 0.3)
      + shape('M272 98 C279 104 284 112 287 124 L282 128 C280 118 276 108 268 100 Z', HAIR.deep, 0.4)
      // la mèche de droite, aussi
      + shape('M424 50 C437 60 448 74 454 88 C456 96 457 104 456 112 C450 106 443 100 436 95 C433 82 430 66 424 50 Z', 'url(#g-cap)')
      + shape('M436 76 C434 82 435 88 437 95 L432 90 C431 86 432 80 436 76 Z', HAIR.deep, 0.45)
      + shape('M430 58 C440 68 448 80 452 94 C446 84 438 74 430 66 Z', HAIR.warm, 0.55)
      // les mèches du front, de part et d'autre
      + shape('M340 78 C334 86 326 96 318 104 C308 112 300 122 293 132 C300 116 312 100 326 88 Z', HAIR.sheen, 0.4)
      + shape('M404 80 C407 92 411 102 417 110 C424 120 430 128 435 136 C424 124 414 110 408 96 Z', HAIR.warm, 0.55)
    ) },
  { id: 'tiara', d: S.tiara, shadow: [{ on: ['cap', 'face'], dx: -3, dy: 5, color: SH.hair, o: 0.55 }],
    body:
      // chaque pointe a une face claire et une face dans l'ombre, de part et d'autre de son arête
      shape('M364 5 L354 40 L339 64 L350 72 L366 60 Z', '#f4f6fb') + shape('M364 5 L366 60 L398 58 L382 36 Z', '#a8aec2')
      + shape('M339 64 L350 72 C362 76 370 86 376 98 L366 60 Z', '#c8ccd8') + shape('M366 60 L376 98 C386 80 392 68 398 58 Z', '#7c8296')
      + shape('M306 46 L300 72 L318 64 Z', '#ffffff') + shape('M306 46 L318 64 L336 66 C324 60 314 52 306 46 Z', '#9aa0b4')
      + shape('M418 36 L406 66 L418 66 Z', '#f0f2f8') + shape('M418 36 L418 66 L428 72 C424 60 421 48 418 36 Z', '#8c92a6')
      + line('M364 5 L366 60 M339 64 L366 60 L398 58 M366 60 L376 98', '#ffffff', 1, 0.6)
      // la gemme rouge dans sa monture
      + shape('M371 36.5 L385.5 54 L373 73.5 L357.5 56 Z', '#eef1f7') + line('M371 36.5 L385.5 54 L373 73.5 L357.5 56 Z', '#6a6f84', 1, 0.7)
      + shape('M371 41 L381 54 L373 69 L362 56 Z', 'url(#g-gem)') + shape('M371 41 L381 54 L371 55 Z', '#ff8070', 0.8)
      + shape('M371 44 L376 51 L370 51 Z', '#ffe2d8', 0.95) + shape('M362 56 L373 69 L371 55 Z', RED.deep, 0.6) },

  // --- devant tout : la lame, puis la garde d'or ---
  { id: 'blade', cls: 'a-sw', d: S.blade, shadow: [{ on: ['torso', 'tassetL', 'tassetR', 'belt', 'skirt', 'fur', 'legR', 'cape', ...RIGHT, 'hairBack'], dx: -3, dy: 7, color: '#000', o: 0.35 }],
    body: `<g class="a-smear" opacity="0"><path d="${smearD}" fill="url(#g-smear)"/></g>`
      + use('blade', 'url(#g-bladeB)')
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
const EASE = ['cubic-bezier(.3,0,.4,1)', 'cubic-bezier(.7,0,.9,.55)', 'cubic-bezier(.15,.55,.35,1)', 'cubic-bezier(.4,0,.3,1)'];
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
  `.atk .a-smear{animation:smear .75s linear both}`,
  kf('sa-atk', SWING.map(([t, A], i) => [t, R(A), EASE[i]])),
  kf('sw-atk', SWING.map(([t, A, B], i) => [t, swordT(A, B), EASE[i]])),
  kf('raise-atk', [[0, R(0)], [0.3, R(-7)], [0.46, R(5)], [0.62, R(4)], [1, R(0)]]),
  kf('fist-atk', [[0, fistT(0, 1)], [0.3, fistT(-7, 0.94)], [0.46, fistT(5, 1.02)], [0.62, fistT(4, 1)], [1, fistT(0, 1)]]),
  kf('hl-atk', [[0, R(-0.8)], [0.3, R(1.6)], [0.48, R(-2.6)], [0.66, R(1.2)], [0.84, R(-1)], [1, R(-0.8)]]),
  kf('hl2-atk', [[0, R(1.3)], [0.3, R(3)], [0.5, R(-3.2)], [0.68, R(2.2)], [1, R(1.3)]]),
  kf('hr-atk', [[0, R(1)], [0.3, R(2.2)], [0.5, R(-3.6)], [0.68, R(1.6)], [0.86, R(-0.4)], [1, R(1)]]),
  kf('cape-atk', [[0, R(-0.8)], [0.3, R(-2)], [0.52, R(2.6)], [0.72, R(-1.2)], [1, R(-0.8)]]),
  kf('fur-atk', [[0, R(-1.4)], [0.3, R(3)], [0.48, R(-5)], [0.68, R(2.5)], [1, R(-1.4)]]),
  `@keyframes smear{0%,39%{opacity:0}43%{opacity:.85}46%{opacity:1}51%{opacity:.35}55%,100%{opacity:0}}`,
].join('');

module.exports = { id: 'mages-10', w: W, h: H, pad: PAD, foot: [356, 485], svg: (anime = true) => figure({ w: W, h: H, pad: PAD, defs, style, parts, anime }) };
