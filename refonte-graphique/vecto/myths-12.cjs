// Zeus (myths-12), héros Légendaire : redessiné par le code d'après le dessin d'origine, dans le même cadre (614 × 598,
// mêmes proportions, même pose) : un dieu sombre et trapu, peau bleu pâle ; couronne de pointes d'acier à gemme bleue,
// grande crinière noire, gros sourcils noirs froncés, yeux cyan, moustache et longue barbe noires ; robe-armure noire
// bordée d'argent, ouverte sur le torse, grosse épaulière à gauche, ceinture à boucle en crâne, pans d'armure, bottes
// de fer ; cape violette qui balaie le sol derrière lui ; le poing droit pend le long du corps, la main gauche serre
// un grand trident d'acier sombre ; une flamme bleue flotte devant son bras gauche.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. La flamme éclaire en bleu le côté
// droit du corps. Contour extérieur décalqué sur l'original (outils/contour.py).
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 614, H = 598, PAD = 50;

// ---------- courbes ----------
/** Chemin lisse par des points "x,y" ("x,y!" = angle vif) ; `bulge` bombe les bords entre deux angles vifs. */
function sm(src, bulge = 0, closed = true) {
  let pts = (Array.isArray(src) ? src.join(' ') : src).trim().split(/\s+/).map((s) => {
    const sharp = s.endsWith('!');
    const [x, y] = s.replace('!', '').split(',').map(Number);
    return { x, y, sharp };
  });
  if (bulge && closed) {
    let area = 0;
    pts.forEach((p, i) => { const q = pts[(i + 1) % pts.length]; area += p.x * q.y - q.x * p.y; });
    const sg = area > 0 ? 1 : -1, out = [];
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
    const a = at(i - 1), b = at(i + 1), d = dist(a, p) + dist(p, b);
    return { x: (b.x - a.x) / d, y: (b.y - a.y) / d };
  };
  let d = `M${n(pts[0].x)} ${n(pts[0].y)}`;
  for (let i = 0; i < (closed ? N : N - 1); i++) {
    const p = at(i), q = at(i + 1), L = dist(p, q) / 3, t1 = tan(i), t2 = tan(i + 1);
    d += `C${n(p.x + t1.x * L)} ${n(p.y + t1.y * L)} ${n(q.x - t2.x * L)} ${n(q.y - t2.y * L)} ${n(q.x)} ${n(q.y)}`;
  }
  return d + (closed ? 'Z' : '');
}
const P = (x, y) => `${n(x)},${n(y)}`;
/** Ruban effilé le long d'une ligne : pts = [[x, y, largeur], …] (reflets, ombres, plis). */
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
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });

// ---------- couleurs ----------
const SKIN = { hi: '#f6faff', base: '#d8e3f4', shade: '#aebcd8', deep: '#8492b8', line: '#5e6a92' };
const HAIR = { base: '#1d1b25', hi: '#5a5878', sheen: '#7a82b4', warm: '#6a5644' };
const ARM = { lite: '#4a4a5e', base: '#2c2c38', deep: '#15151c' };
const SIL = { hi: '#ffffff', lite: '#e4e8f2', base: '#b8bfd2', mid: '#8a91a8', shade: '#5a6078' };
const CAPE = { lite: '#74498e', base: '#4e2e64', deep: '#2a1838' };
const FIRE = { core: '#ffffff', lite: '#b4ecff', base: '#58a8ff', deep: '#2a50d8' };
const SH = { skin: '#4a5478', hair: '#05040a', armor: '#05050a', cape: '#140a1e', iron: '#0a0a10' };

// ---------- dégradés ----------
const defs = [
  lin('g-cape', 0, 280, 0, 590, [[0, '#5c3874'], [0.5, CAPE.base], [1, '#341f46']]),
  lin('g-capeIn', 20, 560, 140, 380, [[0, '#7a52a0'], [0.6, '#5a3a78'], [1, '#3a2450']]),
  lin('g-hair', 0, 70, 0, 330, [[0, '#2e2b3c'], [0.5, HAIR.base], [1, '#131218']]),
  lin('g-beard', 0, 210, 0, 362, [[0, '#2a2426'], [0.5, '#1a1618'], [1, '#100c0e']]),
  lin('g-plateM', 0, 0, 0, 1, [[0, '#a4a8bc'], [0.45, '#5e6276'], [1, '#2a2c38']], false),
  lin('g-skin', 0, 140, 0, 280, [[0, SKIN.hi], [0.55, SKIN.base], [1, SKIN.shade]]),
  lin('g-skinB', 0, 0, 0, 1, [[0, '#eef4ff'], [0.5, SKIN.base], [1, SKIN.shade]], false),
  lin('g-armor', 0, 0, 0, 1, [[0, '#45455a'], [0.45, ARM.base], [1, ARM.deep]], false),
  lin('g-armorX', 0, 0, 1, 0, [[0, ARM.deep], [0.55, ARM.base], [1, '#4e4e66']], false),
  lin('g-silver', 0, 0, 0, 1, [[0, '#ffffff'], [0.35, '#dadeea'], [0.72, '#9ea4b8'], [1, '#6a6f84']], false),
  lin('g-silverX', 0, 0, 1, 0, [[0, '#6a6f84'], [0.3, '#a6acbe'], [0.66, '#f4f6fa'], [0.84, '#d2d6e2'], [1, '#868ca2']], false),
  lin('g-spike', 0, 0, 1, 0, [[0, '#4a4e64'], [0.4, '#9aa0b6'], [0.62, '#f2f4fa'], [0.8, '#c4c9d8'], [1, '#6a7088']], false),
  lin('g-iron', 0, 0, 1, 0, [[0, '#22222a'], [0.35, '#3c3c48'], [0.7, '#6a6a7a'], [0.86, '#9a9cac'], [1, '#4a4a56']], false),
  lin('g-ironV', 0, 0, 0, 1, [[0, '#8a8c9c'], [0.4, '#55555f'], [1, '#2a2a32']], false),
  lin('g-gold', 0, 0, 0, 1, [[0, '#fff2b0'], [0.4, '#e8b844'], [1, '#9a6414']], false),
  lin('g-belt', 0, 0, 0, 1, [[0, '#4a3434'], [0.5, '#2e2024'], [1, '#1a1214']], false),
  lin('g-bone', 0, 0, 0, 1, [[0, '#ffffff'], [0.5, '#efe8da'], [1, '#c2b6a2']], false),
  lin('g-boot', 0, 0, 0, 1, [[0, '#8a8ea2'], [0.4, '#5a5e72'], [1, '#2e3040']], false),
  rad('g-gem', 0.62, 0.3, 0.75, [[0, '#eaffff'], [0.3, '#6adcff'], [0.7, '#1e86d0'], [1, '#0a3a7a']], false),
  rad('g-iris', 0.55, 0.75, 0.8, [[0, '#f0ffff'], [0.3, '#7ce4fa'], [0.68, '#1e9ad6'], [1, '#0a3a6e']], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#0a1430', 0.7], [0.5, '#0a1430', 0]], false),
  rad('g-blush', 0.5, 0.5, 0.5, [[0, '#ff8a9a', 0.45], [1, '#ff8a9a', 0]], false),
  rad('g-glow', 0.5, 0.5, 0.5, [[0, '#e8f8ff', 0.85], [0.42, '#6ab4ff', 0.45], [1, '#3a7aff', 0]], false),
  lin('g-flame', 0, 0, 0, 1, [[0, '#d8f6ff'], [0.35, '#7cc8ff'], [0.75, '#3a78ff'], [1, '#2a48d0']], false),
  lin('g-flameIn', 0, 0, 0, 1, [[0, '#ffffff'], [0.5, '#c8f0ff'], [1, '#7cc8ff']], false),
  rad('g-blueLight', 0.5, 0.5, 0.5, [[0, '#6ab4ff', 0.5], [1, '#6ab4ff', 0]], false),
].join('');

// ---------- silhouettes (le bord extérieur suit le contour mesuré sur l'original) ----------
const S = {
  // la cape : elle part des épaules et balaie le sol à gauche ; elle déborde un peu derrière le bras gauche
  cape: sm('146,285 121,317 117,350 109,380 94,397 72,416 56,427 36,446 24,461 10,486! 13,501 25,522 35,532! 40,504 59,503 70,508 86,521 84,532 101,546 105,554 123,561 146,575 '
    + '109,583! 150,586 200,560 260,540 300,520 330,470 300,330 '
    + '440,300 466,330 472,400 466,470 440,500 380,300'),
  // la crinière, derrière la tête et sur les épaules
  hairBack: sm('254,80 280,68 310,64 340,66 368,74 386,92 404,110 422,138 434,156 436,176 428,196 422,222 420,240 428,260 444,278 440,296 434,312 410,330 300,330 200,322 '
    + '121,317! 110,309 120,300 146,284 140,258 162,240 163,216 155,195 168,166 192,146 206,122 228,98'),
  // le trident : les trois pointes en flèche, le croissant, le col, la hampe (la main gauche la serre)
  trident: sm('476,11! 456,59 452,83 453,102 466,127 474,133 485,129 503,130 509,137 509,146 506,149 509,164 506,170 509,173! 510,199 504,296 501,585! 507,585! 513,431 519,331 531,186 533,175! 537,172 536,163 542,156 '
    + '539,151 541,139 548,133 576,133 581,137 597,117 601,108 605,86 605,61 596,11! 576,61 582,66! 582,88 577,99 566,108 546,109 538,96 539,61! 546,54 537,8! 517,51 522,58! 521,80 518,95 508,107 '
    + '498,107 488,104 480,96 477,89 477,70! 480,62 487,54'),
  // les jambes et les bottes de fer (la gauche de l'image pointe à gauche, la droite à droite)
  legL: sm('180,500 260,500 262,520 266,546 268,590 227,594 214,594 200,590 176,588 158,586 154,572 162,556 176,548 178,520'),
  legR: sm('344,498 448,498 450,520 454,546 466,558 474,572 477,588 425,588 405,590 389,592 342,592 340,566 344,548 346,520'),
  // les pans d'armure sous la ceinture : le tablier du milieu, les deux pans des côtés
  skirt: sm('200,446 448,446 452,500 432,512 372,518 370,528 302,528 298,522 232,524 196,508'),
  // le torse : la robe-armure noire, ouverte sur la poitrine
  torso: sm('186,300 300,288 420,292 446,318 450,380 442,430 430,448 200,450 190,420 178,360'),
  // le bras gauche (à droite de l'image), sous la flamme, et sa main qui serre la hampe
  armL: sm('418,300 452,308 472,340 482,370 494,382 492,420 470,434 446,422 436,382 424,340'),
  handL: sm('480,374 494,364 512,360 528,366 536,384 534,404 530,420 522,430 504,434 488,428 480,410 476,392'),
  // la ceinture et sa boucle en crâne
  belt: sm('220,420 442,414 444,444 222,452'),
  skull: sm('312,436 316,424 334,417 352,421 361,434 358,450 349,458 347,474 331,477 324,464 315,456'),
  // le bras droit (à gauche de l'image) qui pend : la manche, le poing de peau bleue, la grosse épaulière
  armR: sm('160,360 212,366 208,410 200,446 150,448 140,420 148,384'),
  fistR: sm('130,438 152,432 178,434 189,448 186,468 172,482 150,485 132,479 120,466 118,452'),
  pauR: sm('150,332 168,306 200,296 238,300 258,318 256,346 240,366 206,372 170,370 152,356'),
  // la barbe : sous la moustache, elle couvre le haut de la poitrine et finit en pointe
  beard: sm('244,212 252,214 258,232 272,250 290,262 304,272 316,280 334,284 352,286 372,282 388,272 400,258 408,236 412,210 420,212 422,240 418,268 414,292 404,314 390,332 374,342 362,348 352,362! 342,352 330,358! 322,346 306,334 290,314 274,292 258,268 246,244'),
  // la cape posée sur les épaules
  mantleL: sm('126,280 160,258 200,262 236,284 242,306 206,318 170,322 140,320 122,302'),
  mantleR: sm('394,272 420,262 446,272 458,296 448,318 420,314 400,298'),
  // l'oreille (à gauche de l'image) et le visage
  ear: sm('208,198 222,192 234,204 236,230 228,248 214,251 203,238 199,218'),
  face: sm('244,154 300,144 352,148 404,150 412,166 414,200 410,236 402,256 380,268 350,274 318,272 290,268 268,258 252,240 245,210'),
  // la moustache, épaisse, dont les bouts tombent dans la barbe
  stache: sm('304,270 306,260 318,252 334,250 352,257 368,250 386,252 398,260 400,272 394,280! 386,270 368,264 352,266 336,264 318,270 308,280!'),
  // la couronne : un bandeau épais qui suit le crâne, la pointe d'argent qui descend sur le front, les pointes d'acier
  crown: sm('228,158 230,150! 226,128! 240,142! 242,140! 247,114! 262,134! 272,128! 286,58! 302,122! 320,120! 334,8! 350,120! 362,122! 376,62! 392,128! 398,132! 408,104! 418,140! 422,144! 432,126! 436,150! 440,160 '
    + '434,166 410,152 380,146 360,147 352,166! 344,147 310,147 280,151 252,158 232,168'),
};

// ---------- le visage ----------
/** Un œil : blanc, grand iris cyan, pupille, ombre de la paupière, reflets ; la paupière du haut épaisse ; le bas fin. */
function eye(key, white, cx, cy, r, lash, lower, shut, hl) {
  return `<clipPath id="c-${key}"><path d="${white}"/></clipPath><path d="${white}" fill="#fbfdff"/>`
    + `<g clip-path="url(#c-${key})">`
    + `<path d="${white}" fill="none" stroke="#c6d2e8" stroke-width="3"/>`
    + dot(cx, cy, r, 'url(#g-iris)') + `<circle cx="${cx}" cy="${cy}" r="${n(r - 0.8)}" fill="none" stroke="#0a3a6e" stroke-width="1.6"/>`
    + dot(n(cx - r * 0.08), n(cy - r * 0.12), n(r * 0.44), '#06182e')
    + `<rect x="${cx - r - 16}" y="${cy - r - 6}" width="${2 * r + 32}" height="${n(r * 1.3)}" fill="url(#g-lid)"/>`
    + dot(n(cx + hl[0] * r), n(cy + hl[1] * r), n(r * 0.26), '#fff') + dot(n(cx + hl[2] * r), n(cy + hl[3] * r), n(r * 0.13), '#fff', 0.95)
    + '</g>' + line(lower, '#5e6a92', 1.6, 0.85) + shape(lash, '#101018')
    + `<g class="a-blink" opacity="0"><path d="${white}" fill="${SKIN.base}" stroke="${SKIN.base}" stroke-width="3"/>${line(shut, '#101018', 3)}</g>`;
}
const EYE_L = 'M276 213 C288 208 306 207 320 209 C328 212 332 216 333 221 C322 226 306 227 292 224 C284 222 279 218 276 213 Z';
const EYE_R = 'M366 218 C374 213 390 212 403 214 C404 219 400 225 393 227 C383 229 372 227 366 218 Z';
const faceBody = use('face', 'url(#g-skin)') + clip('face',
  // l'ombre du côté gauche et sous les pommettes ; la lumière douce sur le front et la joue droite
  shape(sm('240,150 262,160 262,200 270,236 290,262 260,280 236,280'), SKIN.shade, 0.55)
  + glint([[246, 160, 6], [300, 152, 8], [352, 156, 7], [408, 158, 6]], SKIN.shade, 0.6)
  + oval(390, 176, 16, 24, SKIN.hi, 0.55, 10)
  // les joues rosies et la petite marque sur le front
  + oval(272, 236, 12, 7, 'url(#g-blush)') + oval(404, 232, 8, 6, 'url(#g-blush)', 0.7) + oval(293, 163, 3.6, 2.6, '#e8a0a8', 0.6)
  // les sourcils : deux gros blocs noirs, froncés (le bout près du nez plus bas)
  + shape(sm('262,180 272,172 300,170 330,178 346,190 344,200 330,196 302,189 276,190 264,190'), '#101018')
  + glint([[274, 174, 0], [300, 172, 2.6], [330, 180, 0]], '#4a4a66', 0.8)
  + shape(sm('358,202 362,192 384,182 410,178 418,184 416,192 392,195 370,200'), '#101018')
  + glint([[368, 190, 0], [390, 182, 2.4], [412, 180, 0]], '#4a4a66', 0.8)
  // les yeux
  + eye('eL', EYE_L, 307, 220, 12, 'M267 212 C282 201 306 199 323 203 C332 206 337 213 338 220 L332 219 C326 213 316 211 304 211 C292 211 282 214 276 219 Z',
    'M286 224 C298 229 316 229 330 222', 'M276 210 C292 220 316 221 332 217', [-0.38, -0.36, 0.42, 0.32])
  + eye('eR', EYE_R, 388, 221, 9.5, 'M359 218 C369 208 390 205 408 211 L407 216 C392 213 377 213 368 220 Z',
    'M370 222 C380 227 392 226 400 222', 'M366 214 C378 222 394 222 404 212', [-0.36, -0.36, 0.4, 0.34])
  // le nez : un bout rond éclairé, l'ombre dessous et sur le côté gauche
  + shape(sm('350,226 356,234 366,238 368,246 360,250 348,248 342,242 346,234'), SKIN.shade, 0.7)
  + oval(360, 237, 5, 4, SKIN.hi, 0.9) + oval(352, 246, 3, 1.6, SKIN.deep, 0.7) + oval(364, 247, 2.6, 1.5, SKIN.deep, 0.6)
  // la bouche sous la moustache : la lèvre du bas, pâle
  + shape(sm('328,262 346,266 368,264 376,270 352,276 330,272'), '#c4cde4') + glint([[334, 268, 0], [352, 270, 2.2], [370, 268, 0]], '#f2f6ff', 0.8)
);

// ---------- la flamme bleue (sans contour : elle brille) ----------
const FLAME = sm('446,458 426,446 414,420 420,396 412,372 426,350 422,326 438,312 436,290 452,300 458,276 470,256! 468,290 478,306 472,330 482,350 476,378 486,400 478,428 466,450');
const FLAME_IN = sm('448,446 434,430 430,406 438,386 434,364 446,348 446,330 456,318 460,340 466,358 462,384 470,404 462,428');
const FLAME_CORE = sm('450,434 442,416 446,396 452,380 458,396 460,418');
const flameBody = `<g class="a-glow"><ellipse cx="450" cy="380" rx="64" ry="96" fill="url(#g-glow)"/></g>`
  + `<g class="a-flame">${shape(FLAME, 'url(#g-flame)', 0.92)}${shape(FLAME_IN, 'url(#g-flameIn)', 0.9)}${shape(FLAME_CORE, '#ffffff', 0.95)}`
  + glint([[430, 320, 0], [436, 306, 2.4], [438, 290, 0]], FIRE.lite, 0.8) + '</g>'
  + [[418, 300, 0], [478, 270, 1], [404, 340, 2]].map(([x, y, i]) => `<g class="a-ember${i + 1}">${oval(x, y, 3, 4.4, FIRE.lite, 0.9)}${dot(x, y, 1.6, '#fff')}</g>`).join('');

// ---------- les morceaux, du fond vers le devant ----------
const ARMORS = ['torso', 'skirt', 'belt', 'armR', 'pauR', 'legL', 'legR'];
const parts = [
  { id: 'cape', cls: 'a-cape', d: S.cape, body: use('cape', 'url(#g-cape)') + clip('cape',
    // le dedans de la cape, plus clair, qui se retourne en bas à gauche ; deux grands plis
    shape(sm('10,486 40,470 70,452 100,440 120,452 110,500 120,540 140,566 109,583 70,560 35,532 13,501'), 'url(#g-capeIn)')
    + glint([[110, 330, 0], [86, 400, 5], [52, 460, 6], [30, 500, 0]], CAPE.lite, 0.45)
    + glint([[140, 360, 0], [126, 440, 6], [120, 520, 4], [128, 560, 0]], CAPE.deep, 0.6)
    + glint([[60, 470, 0], [80, 510, 4], [104, 548, 0]], '#9a72c2', 0.5)) },
  { id: 'hairBack', cls: 'a-hair', d: S.hairBack, shadow: [sh(['cape'], -4, 5, SH.cape, 0.5)], body: use('hairBack', 'url(#g-hair)') + clip('hairBack',
    // de grandes mèches : un reflet bleuté sur le haut du crâne, des mèches plus claires qui tombent sur les épaules
    // de grandes mèches ondulées : chacune un côté sombre et un reflet (bleuté en haut, brun chaud vers le bas)
    shape(sm('232,100 214,124 198,152 186,184! 196,170 206,148 222,124'), HAIR.hi, 0.6)
    + shape(sm('210,150 192,182 180,214 172,246 160,270 150,292! 168,272 184,246 194,214 204,182'), '#3a3448', 0.85)
    + shape(sm('186,226 176,256 164,284 146,306! 168,290 184,262 194,236'), HAIR.warm, 0.55)
    + shape(sm('256,86 290,72 330,70 368,80 386,98! 360,86 330,80 290,82'), HAIR.sheen, 0.5)
    + shape(sm('404,118 420,146 430,176 428,208! 424,178 414,148'), HAIR.sheen, 0.6)
    + shape(sm('420,222 426,252 438,276 436,300 428,314! 430,290 424,264 416,240'), HAIR.warm, 0.6)
    + shape(sm('226,170 232,210 240,248 236,290! 228,250 222,210'), '#0a090e', 0.6)) },
  { id: 'legL', d: S.legL, shadow: [sh(['cape', 'hairBack'], -4, 4, SH.armor, 0.45)], body: use('legL', 'url(#g-armor)') + clip('legL',
    // la jambière (une arête claire à droite), la bande d'argent sous le genou, la botte de fer au bout rond tourné à
    // gauche : deux plaques bombées sur le pied, une lumière sur le bout, la semelle sombre
    glint([[250, 504, 0], [256, 522, 3.4], [258, 538, 0]], ARM.lite, 0.8)
    + shape(sm('176,537 264,535 266,550 174,552'), 'url(#g-silver)') + glint([[180, 538, 0], [222, 536, 1.6], [262, 536, 0]], '#ffffff', 0.8)
    + shape(sm('152,556 270,554 272,596 152,596'), 'url(#g-boot)')
    + shape(sm('156,572 176,560 210,556 232,560 230,572 206,574 180,580 160,586'), '#9a9eb2', 0.8)
    + glint([[160, 578, 0], [184, 566, 2.4], [214, 562, 0]], '#e8ecf6', 0.85)
    + glint([[196, 586, 0], [204, 576, 2.4], [216, 566, 0]], '#2a2c38', 0.7) + glint([[218, 586, 0], [224, 576, 2.4], [234, 566, 0]], '#2a2c38', 0.6)
    + shape(sm('150,588 272,588 272,600 150,600'), '#1a1b24')) },
  { id: 'legR', d: S.legR, shadow: [sh(['cape'], -4, 4, SH.armor, 0.45)], body: use('legR', 'url(#g-armor)') + clip('legR',
    glint([[436, 504, 0], [444, 520, 3.4], [448, 534, 0]], ARM.lite, 0.8)
    + shape(sm('342,533 454,531 456,546 340,548'), 'url(#g-silver)') + glint([[348, 534, 0], [400, 532, 1.6], [452, 532, 0]], '#ffffff', 0.8)
    + shape(sm('402,516 418,516 418,534 402,534'), 'url(#g-silverX)') + shape(sm('406,520 414,520 414,530 406,530'), '#2a2c38')
    + shape(sm('338,552 470,550 480,596 338,596'), 'url(#g-boot)')
    + shape(sm('412,560 444,558 466,566 476,580 452,580 430,574 412,572'), '#9a9eb2', 0.8)
    + glint([[420, 562, 0], [448, 562, 2.4], [470, 574, 0]], '#e8ecf6', 0.85)
    + glint([[402, 586, 0], [410, 574, 2.4], [420, 562, 0]], '#2a2c38', 0.7) + glint([[380, 586, 0], [386, 574, 2.4], [394, 562, 0]], '#2a2c38', 0.6)
    + shape(sm('336,586 482,586 482,600 336,600'), '#1a1b24')) },
  { id: 'skirt', d: S.skirt, shadow: [sh(['legL', 'legR'], -4, 5, SH.armor, 0.5)], body: use('skirt', 'url(#g-armor)') + clip('skirt',
    // le tablier du milieu bordé d'argent, les deux pans des côtés et leur bordure d'argent en biais
    shape(sm('300,450 372,450 372,528 300,528'), ARM.deep, 0.5)
    + glint([[300, 512, 6], [336, 516, 6], [372, 512, 6]], SIL.base, 0.95) + glint([[302, 510, 0], [336, 513, 2], [370, 510, 0]], SIL.hi, 0.9)
    + glint([[198, 498, 5], [240, 512, 5.4], [290, 520, 5]], SIL.base, 0.95) + glint([[202, 496, 0], [244, 509, 2], [286, 516, 0]], SIL.hi, 0.8)
    + glint([[378, 506, 5], [414, 500, 5.4], [448, 492, 5]], SIL.base, 0.95) + glint([[382, 503, 0], [414, 497, 2], [444, 490, 0]], SIL.hi, 0.8)
    + glint([[314, 470, 0], [318, 490, 3], [316, 506, 0]], ARM.lite, 0.6)) },
  { id: 'torso', d: S.torso, shadow: [sh(['hairBack', 'cape'], -5, 4, SH.hair, 0.5), sh(['skirt'], -3, 5, SH.armor, 0.5)], body: use('torso', 'url(#g-armor)') + clip('torso',
    // la poitrine nue (bleu pâle), entre les bords de la robe ; les muscles en grandes formes douces
    shape(sm('206,366 240,352 290,356 334,370 350,398 340,422 292,428 240,424 206,412'), 'url(#g-skinB)')
    + shape(sm('210,396 240,404 280,410 320,408 344,404 338,424 290,430 240,426 208,414'), SKIN.shade, 0.6)
    + oval(300, 380, 20, 9, SKIN.hi, 0.6, 8) + glint([[248, 390, 0], [270, 398, 3], [292, 400, 0]], SKIN.shade, 0.7)
    // les revers de la robe, bordés d'argent ; la lumière bleue de la flamme sur le flanc droit
    + glint([[200, 360, 0], [214, 368, 5], [206, 412, 4], [200, 440, 0]], SIL.base, 0.85)
    + glint([[352, 360, 0], [354, 398, 5], [344, 428, 0]], SIL.base, 0.8)
    + oval(440, 380, 22, 50, 'url(#g-blueLight)')) },
  { id: 'belt', d: S.belt, shadow: [sh(['torso', 'skirt'], -2, 5, SH.armor, 0.55)], body: use('belt', 'url(#g-belt)') + clip('belt',
    glint([[224, 424, 0], [330, 420, 2.4], [440, 418, 0]], '#7a5a5a', 0.8)
    + [[246, 434], [270, 433], [384, 430], [410, 429]].map(([x, y]) => shape(sm(`${x - 6},${y - 3} ${x},${y - 6}! ${x + 6},${y - 3} ${x + 4},${y + 4} ${x - 4},${y + 4}`), '#8a2a2a', 0.8)).join('')) },
  { id: 'skull', d: S.skull, shadow: [sh(['belt', 'skirt'], -3, 5, SH.armor, 0.55)], body: use('skull', 'url(#g-bone)') + clip('skull',
    // les orbites, le nez, les dents ; l'ombre de la mâchoire
    shape(sm('318,440 326,434 334,438 334,448 324,450'), '#2a1e22') + shape(sm('340,438 349,433 357,438 354,448 344,449'), '#2a1e22')
    + shape(sm('334,452 337,448 340,452 337,456'), '#3a2a2a')
    + shape(sm('326,460 350,458 348,474 330,476'), '#d8cdb8') + line('M332 462 L332 474 M338 461 L338 475 M344 461 L344 474', '#5a4a42', 1.2, 0.8)
    + oval(348, 424, 5, 3, '#ffffff', 0.9)) },
  { id: 'armR', cls: 'a-armR', d: S.armR, shadow: [sh(['torso', 'cape', 'hairBack'], -4, 5, SH.armor, 0.45)], body: use('armR', 'url(#g-armor)') + clip('armR',
    // la manche sombre, puis le brassard : deux bandes d'argent qui font le tour de l'avant-bras
    glint([[200, 372, 0], [204, 392, 3], [202, 406, 0]], ARM.lite, 0.7)
    + shape(sm('140,404 208,402 206,446 140,448'), 'url(#g-armorX)')
    + glint([[140, 408, 4], [174, 410, 4.4], [208, 406, 4]], SIL.base, 0.95) + glint([[140, 436, 4], [172, 440, 4.4], [206, 436, 4]], SIL.base, 0.95)
    + glint([[144, 407, 0], [174, 408, 1.6], [204, 405, 0]], '#ffffff', 0.85)) },
  { id: 'fistR', cls: 'a-armR', d: S.fistR, shadow: [sh(['armR', 'cape'], -3, 5, SH.skin, 0.45)], body: use('fistR', 'url(#g-skinB)') + clip('fistR',
    // les doigts repliés (des creux sombres entre eux, des bosses éclairées), le pouce par-dessus
    shape(sm('118,456 140,462 160,470 186,462 186,488 118,488'), SKIN.shade, 0.75)
    + [[132, 452, 134, 476], [146, 452, 148, 480], [160, 454, 162, 480]].map(([x1, y1, x2, y2]) => glint([[x1, y1, 0], [(x1 + x2) / 2, (y1 + y2) / 2, 2.4], [x2, y2, 0]], SKIN.deep, 0.7)
      + glint([[x1 + 2.4, y1, 0], [(x1 + x2) / 2 + 2.4, (y1 + y2) / 2, 1.4], [x2 + 2.4, y2, 0]], SKIN.hi, 0.6)).join('')
    + shape(sm('160,440 180,438 188,450 180,458 164,456'), SKIN.hi, 0.7)) },
  { id: 'mantleL', cls: 'a-cape', d: S.mantleL, shadow: [sh(['torso', 'hairBack', 'cape'], -4, 5, SH.cape, 0.5)], body: use('mantleL', 'url(#g-cape)') + clip('mantleL',
    glint([[140, 284, 0], [180, 266, 5], [226, 284, 0]], CAPE.lite, 0.7) + glint([[136, 310, 0], [180, 316, 4], [230, 306, 0]], CAPE.deep, 0.6)) },
  { id: 'mantleR', cls: 'a-cape', d: S.mantleR, shadow: [sh(['torso', 'hairBack', 'cape'], -4, 5, SH.cape, 0.5)], body: use('mantleR', 'url(#g-cape)') + clip('mantleR',
    glint([[402, 276, 0], [428, 266, 4], [452, 284, 0]], CAPE.lite, 0.8)) },
  { id: 'pauR', cls: 'a-armR', d: S.pauR, shadow: [sh(['armR', 'torso', 'hairBack', 'cape', 'mantleL'], -3, 6, SH.armor, 0.5)], body: use('pauR', 'url(#g-plateM)') + clip('pauR',
    // trois plaques en écailles, de haut en bas : chacune bombée (claire en haut à droite), son ombre sur la suivante
    [[300, 0], [326, 1], [350, 2]].map(([y, i]) => {
      const d = `M${148 + i * 2} ${y + 34} C${160 + i * 2} ${y + 8} 200 ${y - 4} ${246 - i * 4} ${y + 6} C${258 - i * 2} ${y + 14} ${258 - i * 2} ${y + 30} ${250 - i * 4} ${y + 40} C220 ${y + 30} 180 ${y + 28} ${148 + i * 2} ${y + 34} Z`;
      return `<path d="${d}" transform="translate(-3 5)" fill="${SH.armor}" opacity="0.45"/><path d="${d}" fill="url(#g-plateM)"/>`
        + glint([[160 + i * 2, y + 22, 0], [200, y + 4, 3], [240 - i * 4, y + 8, 0]], SIL.hi, 0.8);
    }).join('')
    + shape(sm('212,336 220,330 228,336 220,342'), 'url(#g-gold)') + oval(221, 334, 2, 1.2, '#fff8d0')) },
  { id: 'ear', cls: 'a-head', d: S.ear, shadow: [sh(['hairBack'], -3, 4, SH.hair, 0.5)], body: use('ear', 'url(#g-skinB)') + clip('ear',
    shape(sm('212,206 224,202 228,222 222,240 214,236 216,220'), SKIN.shade, 0.8) + oval(226, 208, 3, 5, SKIN.hi, 0.8)) },
  { id: 'face', cls: 'a-head', d: S.face, shadow: [sh(['hairBack', 'ear'], -4, 4, SH.skin, 0.4)], body: faceBody },
  { id: 'beard', cls: 'a-head', d: S.beard, shadow: [sh(['torso', 'belt'], -4, 6, SH.hair, 0.5), sh(['face'], -3, 4, SH.skin, 0.35)], body: use('beard', 'url(#g-beard)') + clip('beard',
    // de grandes mèches de barbe, plus claires vers la droite, qui finissent en pointe
    shape(sm('290,272 312,280 330,300 334,330 328,352 316,330 300,306 286,284'), '#3a302a', 0.8)
    + shape(sm('360,282 384,276 400,290 398,316 384,334 366,344 372,318 366,296'), '#4e4034', 0.8)
    + glint([[340, 284, 0], [346, 316, 4], [350, 352, 0]], HAIR.warm, 0.6)
    + glint([[396, 268, 0], [406, 288, 3], [402, 310, 0]], '#7a6450', 0.7)
    + glint([[264, 262, 0], [276, 286, 4], [292, 306, 0]], '#0c0a0a', 0.6)) },
  { id: 'stache', cls: 'a-head', d: S.stache, shadow: [sh(['face'], -2, 4, SH.skin, 0.45)], body: use('stache', '#18141a') + clip('stache',
    glint([[316, 256, 0], [334, 252, 2.4], [350, 258, 0]], '#4a3c38', 0.8) + glint([[358, 256, 0], [374, 253, 2.4], [388, 259, 0]], '#5a4a44', 0.8)) },
  { id: 'crown', cls: 'a-head', d: S.crown, shadow: [sh(['face', 'hairBack'], -3, 6, SH.hair, 0.55)], body: use('crown', '#30323f') + clip('crown',
    // les pointes d'acier : une face claire à droite, une face sombre à gauche ; le bandeau sombre bordé d'argent
    [[318, 122, 334, 8, 352, 122], [270, 130, 286, 58, 304, 124], [360, 124, 376, 62, 394, 130], [240, 144, 247, 114, 264, 136], [396, 134, 408, 104, 420, 142]].map(([a, b, tx, ty, c, d]) =>
      shape(`M${a} ${b}L${tx} ${ty}L${c} ${d}Z`, 'url(#g-spike)') + shape(`M${a} ${b}L${tx} ${ty}L${n((a + c) / 2 - 2)} ${n((b + d) / 2)}Z`, '#5a5e74', 0.7)
      + glint([[tx + 1, ty + 8, 0], [n((tx + c) / 2 - 2), n((ty + d) / 2), 2.4], [c - 4, d - 4, 0]], '#ffffff', 0.85)).join('')
    // les deux petites pointes devant la crinière
    + shape('M228 152 L226 128 L242 144 Z', 'url(#g-spike)') + shape('M420 146 L432 126 L438 152 Z', 'url(#g-spike)')
    // le bandeau : bordé d'argent en haut et en bas, plus clair à droite
    + glint([[234, 160, 0], [262, 146, 4], [300, 136, 4], [334, 134, 4], [372, 136, 4], [410, 146, 4], [436, 160, 0]], '#1e1f28', 0.9)
    + glint([[240, 164, 0], [282, 152, 1.6], [330, 148, 1.6], [384, 148, 1.6], [430, 162, 0]], SIL.mid, 0.7)
    + glint([[386, 138, 0], [412, 146, 4], [430, 156, 0]], '#5a5e76', 0.7)
    + shape('M344 150 L360 150 L352 166 Z', 'url(#g-silverX)')
    // la gemme bleue au milieu, dans sa monture, et la pointe d'argent qui descend sur le front
    + shape(sm('326,110 342,100 358,110 352,128 336,128'), 'url(#g-silver)') + shape(sm('332,112 342,106 352,112 348,124 338,124'), 'url(#g-gem)')
    + oval(345, 110, 2.6, 1.6, '#ffffff')) },
  { id: 'trident', cls: 'a-tri', d: S.trident, shadow: [sh(['hairBack', 'cape', 'torso'], -4, 6, SH.iron, 0.4)], body: use('trident', 'url(#g-ironV)') + clip('trident',
    // la hampe : une arête claire à droite, l'ombre à gauche ; le col doré ; les pointes : un filet de lumière
    glint([[527, 180, 0], [518, 330, 4], [510, 450, 3], [505, 580, 0]], '#a8aaba', 0.8)
    + glint([[510, 180, 0], [506, 330, 4], [502, 580, 0]], '#18181e', 0.7)
    + shape(sm('504,158 540,156 542,168 504,170'), 'url(#g-gold)')
    + glint([[478, 18, 0], [464, 70, 3], [470, 118, 2], [500, 126, 0]], '#c8ccda', 0.8)
    + glint([[538, 16, 0], [532, 60, 3], [530, 96, 0]], '#e8ecf6', 0.85)
    + glint([[598, 18, 0], [600, 70, 3], [590, 112, 2], [560, 128, 0]], '#c8ccda', 0.7)
    + glint([[486, 120, 0], [520, 118, 3], [560, 124, 0]], '#60606e', 0.6)) },
  { id: 'armL', cls: 'a-tri', d: S.armL, shadow: [sh(['torso', 'hairBack', 'cape'], -4, 5, SH.armor, 0.45)], body: use('armL', 'url(#g-armorX)') + clip('armL',
    shape(sm('468,370 496,376 496,420 468,420'), 'url(#g-silverX)') + oval(456, 380, 18, 40, 'url(#g-blueLight)')) },
  { id: 'handL', cls: 'a-tri', d: S.handL, shadow: [sh(['trident', 'armL'], -3, 5, SH.skin, 0.45)], body: use('handL', 'url(#g-skinB)') + clip('handL',
    // les doigts qui entourent la hampe (creux et bosses), le pouce replié par-dessus
    shape(sm('476,404 500,412 530,408 540,438 476,438'), SKIN.shade, 0.7)
    + [[504, 382, 534, 386], [504, 396, 536, 400], [502, 410, 532, 414]].map(([x1, y1, x2, y2]) => glint([[x1, y1, 0], [(x1 + x2) / 2, (y1 + y2) / 2, 2.4], [x2, y2, 0]], SKIN.deep, 0.7)
      + glint([[x1, y1 - 2.6, 0], [(x1 + x2) / 2, (y1 + y2) / 2 - 2.6, 1.4], [x2, y2 - 2.6, 0]], SKIN.hi, 0.6)).join('')
    + shape(sm('486,370 506,364 522,368 516,378 494,380'), SKIN.hi, 0.75)
    + oval(476, 400, 12, 22, 'url(#g-blueLight)')) },
  // --- la flamme (sans silhouette : aucun contour, elle brille) ---
  { id: 'flame', cls: 'a-fire', d: 'M-900 -900', body: flameBody },
];

// ---------- la vie au repos, puis l'attaque ----------
// Repos : il respire (la tête et la barbe montent un peu), la crinière et la cape ondulent, le poing droit se serre,
// le trident oscille à peine dans sa main, la flamme danse (elle s'étire, son halo palpite, des étincelles montent),
// il cligne des yeux.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : il lève le trident (élan, 0–35 %), puis le plante en avant vers
// la droite (35–55 %) pendant que la flamme explose et que la cape se soulève ; tout revient à la pose de repos.
const PIV = { head: [326, 300], hair: [300, 200], cape: [150, 300], armR: [200, 340], tri: [440, 320], fire: [450, 450] };
const IDLE = {
  'a-head': ['head', 'head 3.2s ease-in-out infinite alternate'],
  'a-hair': ['hair', 'hair 3.6s ease-in-out infinite alternate'],
  'a-cape': ['cape', 'cape 4.2s ease-in-out infinite alternate'],
  'a-armR': ['armR', 'armR 3s ease-in-out infinite alternate'],
  'a-tri': ['tri', 'tri 3.4s ease-in-out infinite alternate'],
  'a-fire': ['fire', 'fire .9s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-glow{transform-origin:450px 380px;animation:glow 1.3s ease-in-out infinite alternate}
.a-flame{transform-origin:450px 456px;animation:flame .62s ease-in-out infinite alternate}
.a-ember1,.a-ember2,.a-ember3{opacity:0}
.a-ember1{animation:ember 1.6s ease-out infinite}.a-ember2{animation:ember 1.9s ease-out -.7s infinite}.a-ember3{animation:ember 1.4s ease-out -1.1s infinite}
.a-blink{animation:blink 4.6s linear infinite}
@keyframes head{from{transform:none}to{transform:translate(0,-2px) rotate(-.6deg)}}
@keyframes hair{from{transform:none}to{transform:translate(0,-1.4px) rotate(.8deg)}}
@keyframes cape{from{transform:none}to{transform:rotate(1.4deg) scale(1.01,1)}}
@keyframes armR{from{transform:none}to{transform:rotate(-1.6deg)}}
@keyframes tri{from{transform:none}to{transform:rotate(-.8deg)}}
@keyframes fire{from{transform:none}to{transform:translate(0,-2px)}}
@keyframes glow{from{transform:scale(.92);opacity:.8}to{transform:scale(1.08);opacity:1}}
@keyframes flame{from{transform:scale(1,1) skewX(0deg)}to{transform:scale(.94,1.07) skewX(-3deg)}}
@keyframes ember{0%{transform:translate(0,12px);opacity:0}20%{opacity:1}100%{transform:translate(4px,-46px);opacity:0}}
@keyframes blink{0%,93%{opacity:0}94.5%,97%{opacity:1}98.5%,100%{opacity:0}}
${atk('a-tri', 'tri-atk')}${atk('a-head', 'head-atk')}${atk('a-hair', 'hair-atk')}${atk('a-cape', 'cape-atk')}${atk('a-armR', 'armR-atk')}${atk('a-fire', 'fire-atk')}
.atk .a-glow{animation:glow-atk .75s ease-in-out}
@keyframes tri-atk{0%{transform:none}32%{transform:translate(-6px,-14px) rotate(-10deg)}50%{transform:translate(18px,6px) rotate(12deg)}64%{transform:translate(14px,4px) rotate(9deg)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}32%{transform:rotate(-2deg)}50%{transform:translate(3px,1px) rotate(2deg)}100%{transform:none}}
@keyframes hair-atk{0%{transform:none}32%{transform:rotate(-1.5deg)}52%{transform:rotate(2.4deg)}100%{transform:none}}
@keyframes cape-atk{0%{transform:none}32%{transform:rotate(2deg)}52%{transform:rotate(-3deg) scale(1.03,1)}100%{transform:none}}
@keyframes armR-atk{0%{transform:none}32%{transform:rotate(4deg)}52%{transform:rotate(-4deg)}100%{transform:none}}
@keyframes fire-atk{0%{transform:none}32%{transform:translate(-4px,-6px) scale(.9)}50%{transform:translate(16px,-4px) scale(1.35)}64%{transform:translate(10px,-2px) scale(1.2)}100%{transform:none}}
@keyframes glow-atk{0%{transform:none}32%{transform:scale(.9)}50%{transform:scale(1.6)}64%{transform:scale(1.3)}100%{transform:none}}
`.replace(/\n/g, '');

module.exports = { id: 'myths-12', w: W, h: H, pad: PAD, foot: [318, 592],
  svg: (anime = true) => figure({ master: require('./silhouettes/myths-12.json'), w: W, h: H, pad: PAD, defs, style, parts, anime }) };
