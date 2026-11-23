// Thor (myths-10), héros Légendaire au nom provisoire : redessiné par le code d'après le dessin d'origine, dans le même
// cadre (539 × 525, mêmes proportions, même pose). Le dessin d'origine montre une femme-araignée : un buste de jeune
// femme à la peau claire, cheveux noirs en chignon piqué de deux épingles d'argent, perles rouges sur le front, grands
// yeux rouges sous des sourcils noirs, sourire malicieux ; elle tient deux poignards d'argent levés ; ceinture rouge ;
// à la place des jambes, un corps d'araignée gris-noir à huit pattes pointues, marqué de rouge.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. Contour décalqué sur l'original.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 539, H = 525, PAD = 44;

// ---------- courbes lisses (reprises du harfang, glaces-4) ----------
/**
 * Chemin lisse passant par des points. `src` = "x,y x,y! …" (ou une liste) : un point suivi de « ! » est un angle vif.
 * Entre deux angles vifs qui se suivent, le bord est bombé vers l'extérieur de `bulge` pixels.
 */
function sm(src, bulge = 0, closed = true) {
  let pts = (Array.isArray(src) ? src.join(' ') : src).trim().split(/\s+/).map((s) => {
    const sharp = s.endsWith('!');
    const [x, y] = s.replace('!', '').split(',').map(Number);
    return { x, y, sharp };
  });
  if (bulge && closed) {
    let area = 0;
    pts.forEach((p, i) => { const q = pts[(i + 1) % pts.length]; area += p.x * q.y - q.x * p.y; });
    const sg = area > 0 ? 1 : -1;
    const out = [];
    pts.forEach((p, i) => {
      out.push(p);
      const q = pts[(i + 1) % pts.length];
      if (p.sharp && q.sharp) {
        const dx = q.x - p.x, dy = q.y - p.y, L = Math.hypot(dx, dy) || 1;
        out.push({ x: (p.x + q.x) / 2 + (sg * dy / L) * bulge, y: (p.y + q.y) / 2 - (sg * dx / L) * bulge, sharp: false });
      }
    });
    pts = out;
  }
  const N = pts.length;
  const at = (i) => (closed ? pts[(i + N) % N] : pts[Math.max(0, Math.min(N - 1, i))]);
  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y) || 1;
  const tan = (i) => {
    const p = at(i);
    if (p.sharp || (!closed && (i === 0 || i === N - 1))) return { x: 0, y: 0 };
    const a = at(i - 1), b = at(i + 1);
    const d = dist(a, p) + dist(p, b);
    return { x: (b.x - a.x) / d, y: (b.y - a.y) / d };
  };
  let d = `M${n(pts[0].x)} ${n(pts[0].y)}`;
  const last = closed ? N : N - 1;
  for (let i = 0; i < last; i++) {
    const p = at(i), q = at(i + 1), L = dist(p, q) / 3;
    const t1 = tan(i), t2 = tan(i + 1);
    d += `C${n(p.x + t1.x * L)} ${n(p.y + t1.y * L)} ${n(q.x - t2.x * L)} ${n(q.y - t2.y * L)} ${n(q.x)} ${n(q.y)}`;
  }
  return d + (closed ? 'Z' : '');
}
const P = (x, y) => `${n(x)},${n(y)}`;
/** Met une liste de points dans le sens des aiguilles d'une montre : les morceaux d'une même silhouette s'additionnent. */
function cw(pts) {
  let area = 0;
  pts.forEach((p, i) => {
    const q = pts[(i + 1) % pts.length];
    const [x1, y1] = p.replace('!', '').split(',').map(Number), [x2, y2] = q.replace('!', '').split(',').map(Number);
    area += x1 * y2 - x2 * y1;
  });
  return area > 0 ? pts : [...pts].reverse();
}
/** Ruban effilé le long d'une ligne : pts = [[x, y, largeur], …] (reflets et ombres en forme de fuseau). */
function rib(pts) {
  const L = [], R = [];
  pts.forEach(([x, y, w], i) => {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1];
    const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
    L.push(P(x - dy * w / 2, y + dx * w / 2)); R.push(P(x + dy * w / 2, y - dx * w / 2));
  });
  return sm([...L, ...R.reverse()].map((p, i, all) => (i === 0 || i === all.length - 1 || i === L.length - 1 || i === L.length ? `${p}!` : p)));
}
const glint = (pts, color, o = 1) => shape(rib(pts), color, o);

// ---------- couleurs ----------
const SKIN = { hi: '#fff6ec', lite: '#ffe8d4', base: '#fbd8bc', shade: '#e8b098', deep: '#c47c70', line: '#9a4e4a' };
const HAIR = { base: '#241820', hi: '#5a4a5a', sheen: '#7a6a80', deep: '#0e080c' };
const CHIT = { hi: '#a8acb8', lite: '#6e7080', base: '#45464f', mid: '#33343c', shade: '#22222a', deep: '#121218' };
const RED = { hi: '#ff8070', base: '#d8282a', shade: '#8a1418', deep: '#4a0a0c' };
const SIL = { hi: '#ffffff', lite: '#e4e8f0', base: '#b4bccc', shade: '#6e7488' };
const SH = { skin: '#5a2a2a', chit: '#06060a', hair: '#06040a' };

// ---------- dégradés ----------
const defs = [
  lin('g-chit', 300, 300, 100, 480, [[0, CHIT.lite], [0.45, CHIT.base], [1, CHIT.shade]]),
  lin('g-leg', 0, 0, 1, 0, [[0, CHIT.deep], [0.45, CHIT.mid], [0.8, CHIT.lite], [1, CHIT.base]], false),
  lin('g-legFar', 0, 0, 1, 0, [[0, CHIT.deep], [0.6, CHIT.shade], [1, CHIT.mid]], false),
  lin('g-hair', 300, 40, 160, 260, [[0, '#3a2c38'], [0.5, HAIR.base], [1, '#16101a']]),
  lin('g-skin', 0, 120, 0, 280, [[0, SKIN.hi], [0.5, SKIN.lite], [1, SKIN.base]]),
  lin('g-skinB', 0, 0, 0, 1, [[0, SKIN.lite], [0.55, SKIN.base], [1, SKIN.shade]], false),
  lin('g-silver', 0, 0, 1, 0, [[0, SIL.shade], [0.35, SIL.base], [0.65, SIL.hi], [1, SIL.base]], false),
  lin('g-red', 0, 0, 0, 1, [[0, RED.hi], [0.45, RED.base], [1, RED.shade]], false),
  rad('g-gem', 0.62, 0.3, 0.75, [[0, '#ffd0c8'], [0.3, '#ff4a40'], [0.7, RED.base], [1, RED.deep]], false),
  rad('g-iris', 0.5, 0.7, 0.8, [[0, '#ffd0a0'], [0.3, '#ff6a3a'], [0.7, '#c8241a'], [1, '#5a0a0a']], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#2a0a14', 0.7], [0.5, '#2a0a14', 0]], false),
  rad('g-blush', 0.5, 0.5, 0.5, [[0, '#ff6a6a', 0.55], [1, '#ff6a6a', 0]], false),
  lin('g-mouth', 0, 250, 0, 272, [[0, '#4a0a1a'], [1, '#a83a4a']]),
].join('');

// ---------- les pattes d'araignée : de grosses pattes courbes qui montent de la hanche, plient au genou et descendent
// en s'affinant jusqu'à une pointe posée au sol ----------
/** Une patte : [hanche, genou, pointe, largeur] ; un ruban qui passe par la hanche, une bosse au-dessus du genou, le genou,
 * un point poussé vers l'extérieur sur la descente, puis la pointe. */
function legPts([h, k, t, w]) {
  const out = Math.sign(t[0] - h[0]) || 1;
  return [[h[0], h[1], w * 1.1], [(h[0] + k[0]) / 2, Math.min(h[1], k[1]) - 14, w * 1.3], [k[0], k[1], w * 1.25],
    [k[0] * 0.45 + t[0] * 0.55 + out * 12, k[1] * 0.45 + t[1] * 0.55, w * 0.85], [t[0], t[1], 3]];
}
const legD = (L) => rib(legPts(L));
// du fond (FAR, plus sombres) vers le devant (NEAR)
const FAR = [[[200, 392], [118, 346], [40, 404], 26], [[226, 414], [214, 440], [222, 496], 22], [[296, 414], [292, 436], [286, 474], 22], [[340, 392], [420, 368], [470, 446], 26]];
const NEAR = [[[196, 404], [80, 372], [14, 492], 34], [[214, 414], [130, 398], [92, 478], 32], [[236, 420], [170, 420], [126, 498], 32], [[310, 418], [340, 404], [370, 497], 32],
  [[334, 404], [404, 380], [460, 494], 34]];

// ---------- silhouettes ----------
const S = {
  // l'abdomen rond de l'araignée, derrière à gauche, et le céphalothorax sous la taille
  abdomen: sm('66,337 93,318 127,310 158,310 194,316 220,340 226,380 210,410 170,426 120,424 80,410 50,390 42,369'),
  thorax: sm('190,360 230,352 300,352 350,362 366,390 350,420 300,436 240,436 200,424 182,396'),
  legsFar: FAR.map(legD).join(''),
  legsNear: NEAR.map(legD).join(''),
  // le buste : les épaules, la poitrine, la taille (avec la ceinture rouge), le bras droit plié
  torso: sm('204,278 230,270 280,268 330,276 352,300 346,330 330,356 300,366 240,366 210,356 196,330 194,300'),
  belt: sm('200,350 300,354 356,348 360,372 300,380 200,376'),
  // les bras : le droit (à gauche de l'image) replié devant, qui tient le poignard du bas ; le gauche levé, qui tient l'autre
  armR: sm('214,292 238,288 262,304 296,316 336,318 362,320 372,336 356,348 320,348 280,340 240,330 214,316'),
  handR: sm('340,314 362,306 384,310 392,326 384,342 364,348 344,344 336,330'),
  armL: sm('356,282 380,264 400,236 412,212 428,206 438,220 430,246 412,278 392,302 370,312'),
  handL: sm('396,190 414,180 432,184 442,198 440,216 428,228 410,228 396,216 392,202'),
  // les poignards : lame, garde, poignée (le haut tenu par la main gauche, le bas par la main droite)
  daggerU: sm('402,190 395,183 401,183 411,177 422,178 430,172 444,144 458,123 503,72! 476,129 452,162 440,175 438,188 432,200'),
  daggerL: sm('384,320 383,316 389,321 396,321 454,290 489,277 526,267! 494,289 453,310 446,311 438,316 418,319 397,327 392,336'),
  // la tête : la chevelure derrière, le chignon, le visage, la frange
  hairBack: sm('170,112 158,85 169,55 179,44 200,36 238,32 256,40 262,60 291,63 313,66 334,74 351,85 367,103 380,112 390,128 395,148 396,180 390,214 370,240 330,250 260,250 200,240 170,236 142,212 142,178 146,170 154,138'),
  bun: sm('170,62 178,44 196,34 220,30 240,34 256,46 258,62 246,78 222,86 196,84 176,76'),
  pins: rib([[162, 22, 9], [204, 52, 10], [246, 84, 9]]) + rib([[262, 10, 9], [228, 46, 10], [190, 100, 9]]),
  ear: sm('162,196 178,188 192,200 196,226 188,246 172,248 160,232 156,212'),
  face: sm('184,150 230,136 290,132 350,140 386,160 392,196 386,232 370,256 342,272 300,282 260,280 226,268 200,246 186,214 182,182'),
  fringe: sm('182,160 196,118 230,92 278,82 330,88 366,108 388,140 392,170 380,174! 368,146 352,124 330,112 310,132! 296,108 270,104 246,118 222,140 204,168 196,196!'),
};

// ---------- le visage ----------
function eye(key, white, cx, cy, r, lash, lower, shut, hl) {
  return `<clipPath id="c-${key}"><path d="${white}"/></clipPath><path d="${white}" fill="#fff"/>`
    + `<g clip-path="url(#c-${key})">`
    + dot(cx, cy, r, 'url(#g-iris)') + `<circle cx="${cx}" cy="${cy}" r="${n(r - 0.9)}" fill="none" stroke="#5a0a0a" stroke-width="1.8"/>`
    + dot(n(cx), n(cy - r * 0.05), n(r * 0.46), '#200404')
    + `<rect x="${cx - r - 16}" y="${cy - r - 8}" width="${2 * r + 32}" height="${n(r * 1.3)}" fill="url(#g-lid)"/>`
    + dot(n(cx + hl[0] * r), n(cy + hl[1] * r), n(r * 0.27), '#fff') + dot(n(cx + hl[2] * r), n(cy + hl[3] * r), n(r * 0.13), '#fff', 0.95)
    + '</g>' + shape(lash, '#140a10') + line(lower, SKIN.line, 1.6, 0.85)
    + `<g class="a-blink" opacity="0"><path d="${white}" fill="${SKIN.lite}" stroke="${SKIN.lite}" stroke-width="3"/>${line(shut, '#140a10', 3)}</g>`;
}
// les deux yeux bâtis pareil (amande, trait d'eye-liner qui s'étire vers l'extérieur), le droit un peu plus petit (trois quarts)
const EYE_L = 'M241 207 C250 195 276 191 292 202 C294 212 286 222 270 225 C256 227 245 219 241 207 Z';
const EYE_R = 'M366 207 C358 196 338 193 329 203 C328 213 336 222 349 224 C360 224 366 216 366 207 Z';
const LASH_L = rib([[295, 206, 0], [283, 194.5, 5.8], [264, 191.5, 6.6], [248, 196, 6], [238, 203, 4.4], [229, 193, 0]]);
const LASH_R = rib([[327, 205, 0], [337, 195.5, 5.2], [352, 193.5, 6], [364, 197.5, 5.2], [369, 203, 4], [377, 192, 0]]);
const faceBody = use('face', 'url(#g-skin)') + clip('face',
  // l'ombre de la frange sur le front, le côté gauche et le menton dans l'ombre, la lumière sur la joue droite
  glint([[186, 166, 8], [250, 150, 10], [320, 150, 10], [386, 168, 8]], SKIN.shade, 0.55)
  + shape(sm('180,200 194,236 220,264 260,282 236,290 180,290'), SKIN.shade, 0.6)
  + oval(372, 196, 10, 18, SKIN.hi, 0.6, 10)
  + oval(230, 240, 14, 9, 'url(#g-blush)') + oval(366, 244, 9, 6, 'url(#g-blush)', 0.8) + dot(372, 236, 1.6, SKIN.line)
  // la marque au front : une perle rouge et une petite goutte
  + oval(324, 162, 9, 8, 'url(#g-gem)') + oval(326, 159, 2.4, 1.6, '#fff', 0.9) + shape('M324 172 C326 176 326 180 324 184 C322 180 322 176 324 172 Z', '#4a0a14')
  // les sourcils épais, arqués
  + shape(rib([[234, 187, 0], [250, 179.5, 6.6], [272, 177, 8], [295, 182, 5.4], [306, 189, 0]]), '#140a10')
  + shape(rib([[331, 187, 0], [342, 180.5, 5.8], [360, 178, 7], [376, 181.5, 5], [385, 188, 0]]), '#140a10')
  + eye('eL', EYE_L, 267, 210, 14, LASH_L, 'M248 222 C258 228 276 228 288 220', 'M240 208 Q266 220 293 206', [-0.36, -0.4, 0.4, 0.3])
  + eye('eR', EYE_R, 348, 211, 12.5, LASH_R, 'M334 220 C342 225 356 225 362 219', 'M329 206 Q348 218 366 207', [-0.36, -0.4, 0.4, 0.3])
  // le nez, petit et rond
  + oval(318, 240, 6, 4, SKIN.shade, 0.7) + oval(320, 237, 3, 2, SKIN.hi, 0.9)
  // le sourire malicieux : la bouche ouverte, les dents du haut, la langue ; le coin relevé
  + `<path d="M276 254 C292 262 320 262 340 252 C338 266 322 276 304 276 C290 276 280 268 276 254 Z" fill="url(#g-mouth)"/>`
  + shape('M280 256 C296 262 320 262 336 254 L335 259 C320 266 296 266 281 260 Z', '#ffffff') + oval(306, 270, 10, 3.6, '#e86a7a', 0.9)
  + line('M274 252 L270 248', SKIN.line, 2)
);

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const legBody = (id, list, fill) => use(id, fill) + clip(id, list.map((L) => {
  const P = legPts(L);
  // une arête claire le long du dessus de la patte, une ombre dessous, deux anneaux (articulations) plus sombres
  return glint(P.map(([x, y, w], i) => [x + 2, y - w * 0.22, i === 0 || i === P.length - 1 ? 0 : w * 0.22]), CHIT.hi, 0.55)
    + glint(P.map(([x, y, w], i) => [x - 2, y + w * 0.25, i === 0 || i === P.length - 1 ? 0 : w * 0.25]), CHIT.deep, 0.6)
    + [1, 2].map((i) => oval(P[i][0], P[i][1], P[i][2] * 0.5, P[i][2] * 0.16, CHIT.deep, 0.8, i === 1 ? 70 : 40)).join('')
    + oval(P[2][0], P[2][1] + 4, 6, 4, RED.base, 0.75);
}).join(''));
const parts = [
  // le fond des pattes, pris dans la silhouette de l'original (tout derrière : ce que les pattes dessinées ne couvrent pas)
  { id: 'legsBase', cls: 'a-legsF', d: sm('6,453 6,457 10,457 12,459 7,467 7,473 10,475 9,492 13,500 20,502 27,498 40,472 46,467 45,462 50,457 54,447 62,441 67,448 84,463 83,475 92,485 90,487 96,488 96,484 102,479 103,473 109,476 106,485 106,510 111,518 118,518 124,511 131,498 135,498 141,502 144,501 154,504 188,506 194,508 196,511 201,511 207,514 209,510 210,518 215,521 219,520 225,513 229,514 238,510 293,504 296,502 319,503 326,499 338,497 344,492 339,489 346,483 347,478 356,472 370,497 370,503 374,504 380,516 388,518 392,515 394,510 392,495 396,494 397,489 395,472 391,464 384,456 383,449 377,435 363,412 364,410 384,405 388,409 399,413 400,418 414,429 416,436 422,441 427,453 435,461 453,500 451,503 439,504 439,506 454,508 458,507 464,509 470,504 471,498 470,473 465,454 465,447 443,403 427,380 37,380 33,388 33,394 39,394 41,399 25,419 16,438'), body: use('legsBase', 'url(#g-legFar)') },
  { id: 'legsFar', cls: 'a-legsF', d: S.legsFar, body: legBody('legsFar', FAR, 'url(#g-legFar)') },
  { id: 'abdomen', cls: 'a-abd', d: S.abdomen, shadow: [sh(['legsFar'], -4, 5, SH.chit, 0.45)], body: use('abdomen', 'url(#g-chit)') + clip('abdomen',
    // la bosse éclairée en haut à droite, le dessous à l'ombre, les marques rouges en sablier
    oval(150, 334, 46, 18, CHIT.hi, 0.45, -8) + oval(130, 330, 18, 6, '#ffffff', 0.4, -8)
    + shape(sm('46,380 80,404 120,420 170,422 212,404 200,430 60,430'), CHIT.deep, 0.6)
    + shape('M120 352 L136 366 L120 380 L104 366 Z', RED.base, 0.85) + shape('M160 360 L172 372 L160 384 L148 372 Z', RED.base, 0.8)) },
  { id: 'thorax', cls: 'a-body', d: S.thorax, shadow: [sh(['abdomen', 'legsFar'], -4, 5, SH.chit, 0.45)], body: use('thorax', 'url(#g-chit)') + clip('thorax',
    oval(290, 376, 40, 12, CHIT.hi, 0.4) + shape(sm('186,404 240,428 300,432 360,412 360,440 186,440'), CHIT.deep, 0.6)) },
  { id: 'legsNear', cls: 'a-legsN', d: S.legsNear, shadow: [sh(['abdomen', 'thorax', 'legsFar'], -4, 6, SH.chit, 0.45)], body: legBody('legsNear', NEAR, 'url(#g-leg)') },
  { id: 'hairBack', cls: 'a-head', d: S.hairBack, shadow: [sh(['abdomen'], -4, 5, SH.hair, 0.4)], body: use('hairBack', 'url(#g-hair)') + clip('hairBack',
    shape(sm('260,70 310,70 350,88 376,116 360,100 320,84 280,80'), HAIR.sheen, 0.55) + glint([[160, 140, 0], [150, 190, 4], [160, 230, 0]], HAIR.hi, 0.5)
    + glint([[388, 140, 0], [394, 180, 3], [388, 220, 0]], HAIR.sheen, 0.5)) },
  { id: 'bun', cls: 'a-head', d: S.bun, shadow: [sh(['hairBack', 'pins'], -3, 5, SH.hair, 0.45)], body: use('bun', 'url(#g-hair)') + clip('bun',
    shape(sm('196,40 226,34 250,46 236,48 212,46'), HAIR.sheen, 0.6) + glint([[180, 60, 0], [200, 76, 3], [232, 80, 0]], HAIR.deep, 0.6)) },
  { id: 'pins', cls: 'a-head', d: S.pins, shadow: [sh(['bun', 'hairBack'], -3, 4, SH.hair, 0.5)], body: use('pins', 'url(#g-silver)') + clip('pins', glint([[164, 18, 0], [206, 48, 2.4], [244, 78, 0]], '#ffffff', 0.9) + glint([[260, 8, 0], [228, 42, 2.4], [194, 94, 0]], '#ffffff', 0.9)) + dot(163, 22, 4, 'url(#g-gem)') + dot(262, 11, 4, 'url(#g-gem)') },
  { id: 'torso', cls: 'a-body', d: S.torso, shadow: [sh(['thorax', 'hairBack', 'abdomen'], -4, 5, SH.skin, 0.4)], body: use('torso', 'url(#g-skinB)') + clip('torso',
    // le haut moulant rouge sombre sous la poitrine, l'ombre du cou, la lumière sur l'épaule droite
    shape(sm('206,320 260,330 330,326 350,330 340,360 206,360'), RED.shade, 0.9)
    + shape(sm('250,270 320,272 318,296 290,304 258,298'), SKIN.shade, 0.6) + oval(336, 296, 12, 10, SKIN.hi, 0.6)) },
  { id: 'belt', cls: 'a-body', d: S.belt, shadow: [sh(['thorax', 'torso'], -2, 4, SH.chit, 0.5)], body: use('belt', 'url(#g-red)') + clip('belt',
    glint([[204, 356, 0], [280, 360, 2.4], [354, 354, 0]], RED.hi, 0.7) + shape(sm('258,352 276,350 280,380 262,380'), RED.shade, 0.8)) },
  { id: 'daggerU', cls: 'a-armL', d: S.daggerU, shadow: [sh(['hairBack', 'torso'], -3, 5, SH.chit, 0.4)], body: use('daggerU', 'url(#g-silver)') + clip('daggerU',
    glint([[440, 172, 0], [470, 128, 2.4], [500, 76, 0]], '#ffffff', 0.9) + shape(sm('395,183 411,177 422,178 428,188 412,196 400,194'), '#3a2a2a')) },
  { id: 'daggerL', cls: 'a-armR', d: S.daggerL, shadow: [sh(['legsNear', 'thorax'], -3, 5, SH.chit, 0.4)], body: use('daggerL', 'url(#g-silver)') + clip('daggerL',
    glint([[400, 318, 0], [460, 292, 2.4], [522, 270, 0]], '#ffffff', 0.9) + shape(sm('383,316 396,321 400,330 392,336 384,330'), '#3a2a2a')) },
  { id: 'armL', cls: 'a-armL', d: S.armL, shadow: [sh(['torso', 'hairBack'], -3, 5, SH.skin, 0.4)], body: use('armL', 'url(#g-skinB)') + clip('armL',
    glint([[372, 290, 0], [404, 250, 3], [428, 214, 0]], SKIN.hi, 0.6) + glint([[372, 306, 0], [398, 280, 3], [420, 244, 0]], SKIN.shade, 0.6)) },
  { id: 'handL', cls: 'a-armL', d: S.handL, shadow: [sh(['daggerU', 'armL'], -3, 5, SH.skin, 0.45)], body: use('handL', 'url(#g-skinB)') + clip('handL',
    [[402, 196, 436, 196], [400, 208, 438, 208], [404, 220, 432, 220]].map(([x1, y1, x2, y2]) => glint([[x1, y1, 0], [(x1 + x2) / 2, y1 + 1, 2.4], [x2, y2, 0]], SKIN.deep, 0.6)).join('')) },
  { id: 'ear', cls: 'a-head', d: S.ear, shadow: [sh(['hairBack'], -3, 4, SH.hair, 0.4)], body: use('ear', 'url(#g-skinB)') + clip('ear', shape(sm('166,204 180,200 186,222 180,240 170,232'), SKIN.deep, 0.6)) },
  { id: 'face', cls: 'a-head', d: S.face, shadow: [sh(['hairBack', 'torso', 'ear'], -3, 5, SH.skin, 0.4)], body: faceBody },
  { id: 'fringe', cls: 'a-head', d: S.fringe, shadow: [sh(['face', 'ear'], -3, 6, SH.skin, 0.45)], body: use('fringe', 'url(#g-hair)') + clip('fringe',
    shape(sm('240,96 286,86 332,94 362,112! 330,104 290,98'), HAIR.sheen, 0.55)
    // les perles rouges sur le front, de part et d'autre
    + oval(232, 150, 7, 6, 'url(#g-gem)') + oval(382, 160, 6, 5.4, 'url(#g-gem)')) },
  { id: 'armR', cls: 'a-armR', d: S.armR, shadow: [sh(['torso', 'belt', 'thorax'], -3, 5, SH.skin, 0.4)], body: use('armR', 'url(#g-skinB)') + clip('armR',
    glint([[220, 300, 0], [280, 316, 3], [340, 322, 0]], SKIN.hi, 0.6) + glint([[224, 316, 0], [280, 334, 3], [340, 344, 0]], SKIN.shade, 0.6)
    + glint([[318, 318, 4], [322, 332, 4], [320, 346, 4]], '#f4ecdc', 0.9)) },
  { id: 'handR', cls: 'a-armR', d: S.handR, shadow: [sh(['daggerL', 'armR', 'legsNear'], -3, 5, SH.skin, 0.45)], body: use('handR', 'url(#g-skinB)') + clip('handR',
    [[346, 318, 384, 316], [344, 330, 388, 330], [348, 342, 380, 342]].map(([x1, y1, x2, y2]) => glint([[x1, y1, 0], [(x1 + x2) / 2, y1 + 1, 2.4], [x2, y2, 0]], SKIN.deep, 0.6)).join('')) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : les pattes d'araignée piétinent (les deux rangées en décalé), le buste se balance, la tête penche, les
// poignards tournoient un peu, elle cligne.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : elle se ramasse sur ses pattes, puis frappe des deux poignards en
// avant (le haut descend, le bas pique) ; tout revient à la pose de repos.
const PIV = { body: [280, 400], head: [290, 280], legsF: [260, 400], legsN: [260, 410], abd: [200, 380], armL: [360, 300], armR: [230, 300] };
const IDLE = {
  'a-body': ['body', 'body 1.8s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 2.6s ease-in-out infinite alternate'],
  'a-legsF': ['legsF', 'legsF .6s ease-in-out infinite alternate'],
  'a-legsN': ['legsN', 'legsN .6s ease-in-out -.3s infinite alternate'],
  'a-abd': ['abd', 'abd 2s ease-in-out infinite alternate'],
  'a-armL': ['armL', 'armL 2.2s ease-in-out infinite alternate'],
  'a-armR': ['armR', 'armR 2.4s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-blink{animation:blink 4.4s linear infinite}
@keyframes body{from{transform:none}to{transform:translate(0,-3px) rotate(-1deg)}}
@keyframes head{from{transform:none}to{transform:rotate(-2deg)}}
@keyframes legsF{from{transform:none}to{transform:translate(0,-2px) scale(1.01,.98)}}
@keyframes legsN{from{transform:none}to{transform:translate(0,-2px) scale(.99,1.02)}}
@keyframes abd{from{transform:none}to{transform:rotate(1.5deg)}}
@keyframes armL{from{transform:none}to{transform:rotate(-3deg)}}
@keyframes armR{from{transform:none}to{transform:rotate(2deg)}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
${atk('a-armL', 'armL-atk')}${atk('a-armR', 'armR-atk')}${atk('a-body', 'body-atk')}${atk('a-head', 'head-atk')}${atk('a-legsN', 'legs-atk')}${atk('a-legsF', 'legs-atk')}
@keyframes armL-atk{0%{transform:none}32%{transform:rotate(-12deg)}50%{transform:rotate(18deg)}64%{transform:rotate(14deg)}100%{transform:none}}
@keyframes armR-atk{0%{transform:none}32%{transform:translate(-8px,0) rotate(6deg)}50%{transform:translate(14px,-4px) rotate(-6deg)}64%{transform:translate(10px,-2px) rotate(-4deg)}100%{transform:none}}
@keyframes body-atk{0%{transform:none}32%{transform:translate(-6px,4px) rotate(-2deg)}50%{transform:translate(10px,-2px) rotate(3deg)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}32%{transform:rotate(-3deg)}50%{transform:rotate(3deg)}100%{transform:none}}
@keyframes legs-atk{0%{transform:none}32%{transform:scale(1.03,.94)}50%{transform:scale(.98,1.04)}100%{transform:none}}
`.replace(/\n/g, '');

// ---------- le rendu ----------
/** Enveloppe chaque groupe de classe `cls` dans un groupe de classe `outer` (repris du harfang). */
function nest(s, cls, outer) {
  const open = `<g class="${cls}">`;
  let i = s.indexOf(open);
  while (i >= 0) {
    let depth = 0, j = i;
    const re = /<g[\s>]|<\/g>/g;
    re.lastIndex = i;
    let m;
    while ((m = re.exec(s))) {
      depth += m[0] === '</g>' ? -1 : 1;
      if (depth === 0) { j = m.index + 4; break; }
    }
    s = s.slice(0, i) + `<g class="${outer}">` + s.slice(i, j) + '</g>' + s.slice(j);
    i = s.indexOf(open, i + outer.length + 14 + open.length);
  }
  return s;
}

function svg(anime = true) {
  let s = figure({ master: require('./silhouettes/myths-10.json'), w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  // le buste emporte la tête et les bras
  for (const c of ['a-head', 'a-armL', 'a-armR']) s = nest(s, c, 'a-body');
  return s;
}

module.exports = { id: 'myths-10', w: W, h: H, pad: PAD, foot: [240, 498], svg };
