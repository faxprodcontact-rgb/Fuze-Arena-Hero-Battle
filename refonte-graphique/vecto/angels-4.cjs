// Séraphin (angels-4), héros : redessinée par le code d'après le dessin d'origine, dans le même cadre (563 × 486,
// mêmes proportions, même pose) : une sorcière des mers à la peau lavande ; longue chevelure bleu nuit qui flotte à
// gauche, nageoire orange en guise d'oreille, oreille pointue, yeux d'or sous des sourcils froncés, marque au front,
// sourire à petits crocs ; elle tient à deux mains un bâton de bois ficelé terminé par un crochet d'argent ; ceinture
// corail ; à la place des jambes, des tentacules violets aux ventouses claires qui s'étalent au sol.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. Contour décalqué sur l'original
// (outils/contour.py).
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 563, H = 486, PAD = 46;

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
const SKIN = { hi: '#ece2fa', lite: '#d4c4ee', base: '#b8a4dc', shade: '#9480bc', deep: '#6e5a98', line: '#4e3c74' };
const HAIR = { base: '#2c2444', hi: '#6a64a8', sheen: '#8a84c8', deep: '#14101e' };
const TENT = { hi: '#d6a8f0', lite: '#a872cc', base: '#8656a3', shade: '#5e3480', deep: '#3a1c56' };
const FIN = { hi: '#ffe0b0', lite: '#ffb874', base: '#f08a4c', shade: '#c0503a', deep: '#7a2c38' };
const WOOD = { hi: '#c89070', base: '#8a5840', shade: '#5e3a2a', deep: '#3a2018' };
const SH = { skin: '#3a2a5e', hair: '#06040c', tent: '#1e0a30', wood: '#1a0c08' };

// ---------- dégradés ----------
const defs = [
  lin('g-hair', 300, 0, 120, 320, [[0, '#3a3058'], [0.5, HAIR.base], [1, '#1c1830']]),
  lin('g-skin', 0, 90, 0, 250, [[0, SKIN.hi], [0.5, SKIN.lite], [1, SKIN.base]]),
  lin('g-skinB', 0, 0, 0, 1, [[0, SKIN.lite], [0.55, SKIN.base], [1, SKIN.shade]], false),
  lin('g-fin', 196, 170, 80, 80, [[0, FIN.deep], [0.3, FIN.shade], [0.65, FIN.base], [1, FIN.lite]]),
  lin('g-tent', 0, 330, 0, 480, [[0, TENT.lite], [0.4, TENT.base], [1, TENT.shade]]),
  lin('g-tentFar', 0, 330, 0, 480, [[0, TENT.base], [1, TENT.deep]]),
  lin('g-sash', 0, 0, 0, 1, [[0, '#ffb890'], [0.45, '#e88f6d'], [1, '#b8503e']], false),
  lin('g-wood', 0, 0, 1, 0, [[0, WOOD.shade], [0.5, WOOD.base], [1, WOOD.hi]], false),
  lin('g-hook', 470, 80, 548, 140, [[0, '#ffffff'], [0.4, '#dce2ea'], [0.75, '#9aa6b8'], [1, '#5e6a80']]),
  rad('g-iris', 0.5, 0.7, 0.8, [[0, '#fff8c0'], [0.35, '#ffe23a'], [0.75, '#e8a810'], [1, '#8a5a08']], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#1e0a30', 0.7], [0.5, '#1e0a30', 0]], false),
  rad('g-blush', 0.5, 0.5, 0.5, [[0, '#ff6a8a', 0.55], [1, '#ff6a8a', 0]], false),
  lin('g-mouth', 0, 196, 0, 216, [[0, '#3a0a1a'], [1, '#8a2a3a']]),
].join('');

// ---------- les tentacules ----------
/** Un tentacule : un ruban qui s'affine jusqu'à la pointe, le dessus éclairé, une ligne de ventouses claires dessous. */
const TENTS = [
  // [ligne du milieu : [x, y, largeur], …], du fond vers le devant
  { id: 't1', far: true, pts: [[200, 346, 38], [140, 352, 34], [90, 360, 26], [56, 372, 16], [38, 378, 5]] },
  { id: 't2', far: true, pts: [[330, 346, 40], [380, 356, 38], [420, 382, 30], [444, 414, 20], [452, 446, 10], [450, 458, 4]] },
  { id: 't3', pts: [[210, 352, 44], [160, 380, 38], [110, 412, 30], [70, 440, 20], [34, 448, 12], [16, 432, 7], [20, 424, 3]] },
  { id: 't4', pts: [[232, 360, 46], [212, 400, 38], [186, 432, 30], [156, 458, 20], [126, 470, 7]] },
  { id: 't5', pts: [[318, 360, 46], [340, 400, 40], [360, 432, 30], [380, 458, 20], [398, 470, 7]] },
  { id: 't6', pts: [[270, 362, 48], [272, 400, 40], [268, 436, 30], [262, 462, 18], [254, 474, 6]] },
];
const tentD = (t) => rib(t.pts);
function tentBody(t) {
  const P = t.pts;
  // le reflet du dessus (côté droit de la marche), l'ombre du dessous, puis les ventouses le long du bord du bas
  const side = (k, s) => P.map(([x, y, w], i) => {
    const a = P[Math.max(0, i - 1)], b = P[Math.min(P.length - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1];
    const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
    return [x - dy * w * k, y + dx * w * k, w * s];
  });
  const lite = side(-0.22, 0.28), shade = side(0.26, 0.34), cups = side(0.14, 0);
  return use(t.id, `url(#g-${t.far ? 'tentFar' : 'tent'})`) + clip(t.id,
    shape(rib(shade), TENT.deep, 0.5) + shape(rib(lite), TENT.hi, 0.45)
    + cups.slice(0, -1).map(([x, y], i) => {
      const r = Math.max(1.4, P[i][2] * 0.09);
      return oval(n(x), n(y), n(r * 1.3), n(r), '#f0d6ff', 0.75) + oval(n(x - 0.4), n(y + 0.3), n(r * 0.6), n(r * 0.45), TENT.shade, 0.7);
    }).join(''));
}

// ---------- silhouettes (le bord extérieur suit le contour mesuré sur l'original) ----------
const S = {
  // la chevelure : le grand dôme et les longues mèches qui flottent à gauche, quelques mèches qui tombent à droite
  hair: sm('272,8 313,14 351,35 372,59 387,88 392,110 393,129 392,147 390,152 391,179 389,191 381,206 365,222! 360,222 356,226 356,232 359,235 371,235 376,233 381,228 384,221 '
    + '392,215 403,214! 396,240 380,250 340,250 300,240 230,250 200,280 180,300 140,320 100,330 80,325! 82,318 77,315 80,311 80,303 77,300 71,300 60,305 53,305 42,300 36,291! '
    + '53,288 69,272 72,264 73,247 77,236 77,229 75,227! 86,208 86,202 83,199 77,199 68,205 54,219 47,240! 46,224 53,206 63,195 63,191 71,188 89,175 103,158 103,152 '
    + '100,149 82,146! 99,130 99,127 103,122 101,106 95,95 83,83 76,79! 95,76 114,77 133,82 143,87 150,87 154,83 160,69 170,54 189,35 212,21 237,13'),
  // la nageoire orange (une oreille de poisson) et l'oreille pointue
  fin: sm('202,172 186,184 168,186 140,174 112,150 100,124 90,98 78,80! 102,86 124,92 148,98 172,108 194,124 206,146'),
  ear: sm('216,130 206,116 198,104 194,90! 210,102 222,118 226,138 220,162 210,158'),
  // le corps : le cou, les épaules, le buste
  body: sm('254,226 302,228 314,248 338,254 352,274 348,300 344,330 300,338 240,338 212,330 206,300 204,274 220,256 244,248'),
  // la ceinture corail
  sash: sm('198,322 250,332 300,334 346,326 352,348 300,356 250,356 196,346'),
  // le bâton (de bas à gauche en haut à droite) et le crochet d'argent
  staff: rib([[290, 334, 17], [340, 286, 17], [384, 236, 16.5], [418, 188, 16], [444, 146, 15], [458, 120, 13]]),
  // le chiffon violet noué en boule au sommet du bâton
  knot: sm('412,140 424,128 440,126 452,134 454,150 446,164 448,176 438,182 424,178 414,166 408,152'),
  hook: sm('459,111 462,101 474,85 495,75 514,75 535,85 544,95 553,114 554,125 551,135 540,148! 544,138 544,130 537,125 532,107 526,101 515,96 504,96 495,99 485,110 482,125 475,127 466,128'),
  // les liens de cuir qui pendent sous le bâton
  straps: sm('396,240 410,238 414,256 410,276 406,298 402,306! 396,300 398,278 394,262 388,276 384,290 378,298! 376,286 382,266 388,250'),
  // le bras de gauche (le sien droit) et sa main sur le bas du bâton
  armR: sm('200,262 220,252 240,260 246,280 244,294 264,292 294,288 310,294 308,314 282,320 250,322 226,318 210,306 198,286'),
  handR: sm('292,276 312,270 332,276 342,290 340,306 326,316 306,316 292,306 288,292'),
  // le bras de droite (le sien gauche) qui monte vers le haut du bâton, et sa main
  armL: sm('330,234 352,228 376,226 394,222 404,232 398,250 376,258 352,262 334,262'),
  handL: sm('384,214 398,208 414,210 428,220 432,234 426,246 412,250 396,248 386,238 382,226'),
  // le visage (et le cou)
  face: sm('206,108 240,94 290,88 340,92 372,104 384,130 384,164 376,196 362,222 340,240 312,250 286,250 260,242 236,226 218,202 206,170 202,138'),
  // la frange, par-dessus le front
  bangs: sm('204,112 214,84 238,62 270,50 306,50 340,58 366,74 380,94 386,118 376,126! 366,106 356,96 350,118! 338,98 320,84 300,92 288,104! 284,86 262,88 244,98 230,112 216,138!'),
};

// ---------- le visage ----------
function eye(key, white, cx, cy, r, lash, lower, shut) {
  return `<clipPath id="c-${key}"><path d="${white}"/></clipPath><path d="${white}" fill="#fff"/>`
    + `<g clip-path="url(#c-${key})">`
    + dot(cx, cy, r, 'url(#g-iris)') + `<circle cx="${cx}" cy="${cy}" r="${n(r - 0.9)}" fill="none" stroke="#6a4206" stroke-width="1.8"/>`
    + oval(cx, n(cy + 0.5), n(r * 0.22), n(r * 0.62), '#1a0c06')
    + `<rect x="${cx - r - 14}" y="${cy - r - 8}" width="${2 * r + 28}" height="${n(r * 1.3)}" fill="url(#g-lid)"/>`
    + dot(n(cx - r * 0.4), n(cy - r * 0.42), n(r * 0.26), '#fff') + dot(n(cx + r * 0.42), n(cy + r * 0.3), n(r * 0.13), '#fff', 0.95)
    + '</g>' + shape(lash, '#1a0c22') + line(lower, '#4e3c74', 1.6, 0.9)
    + `<g class="a-blink" opacity="0"><path d="${white}" fill="${SKIN.lite}" stroke="${SKIN.lite}" stroke-width="3"/>${line(shut, '#1a0c22', 3)}</g>`;
}
const EYE_L = 'M234 150 C244 142 264 140 282 146 C292 150 297 158 297 166 C294 176 282 182 266 182 C250 182 238 172 234 160 Z';
const EYE_R = 'M318 156 C328 148 346 146 358 150 C362 158 360 170 352 177 C342 182 330 180 322 172 C318 168 316 162 318 156 Z';
const faceBody = use('face', 'url(#g-skin)') + clip('face',
  // l'ombre sous la frange, la joue gauche et la mâchoire dans l'ombre ; la lumière sur la joue droite
  glint([[206, 120, 8], [260, 104, 10], [320, 104, 10], [372, 116, 8]], SKIN.shade, 0.55)
  + shape(sm('200,150 216,180 236,214 266,236 300,244 330,240 312,260 250,260 200,230'), SKIN.base, 0.7)
  + oval(352, 136, 12, 20, SKIN.hi, 0.6, 12)
  // les joues rosées, la marque au front
  + oval(232, 184, 14, 9, 'url(#g-blush)') + oval(356, 188, 9, 7, 'url(#g-blush)', 0.8)
  + shape('M312 124 L318 130 L312 138 L306 130 Z', '#2a1a40')
  // les sourcils, froncés (épais, qui plongent vers le nez)
  + shape(sm('244,126 262,124 284,134 298,146 296,152 280,144 260,136 246,134'), '#1a0c22')
  + shape(sm('324,148 338,136 356,130 364,134 356,140 340,148 328,154'), '#1a0c22')
  + eye('eL', EYE_L, 264, 164, 14.5, 'M230 152 C242 138 266 136 286 142 C296 146 302 154 302 162 L296 160 C292 152 280 147 264 147 C250 147 240 152 236 160 Z',
    'M244 178 C254 184 274 184 288 178', 'M234 160 C252 172 280 172 297 164')
  + eye('eR', EYE_R, 340, 165, 12, 'M314 156 C326 144 346 141 362 146 L360 152 C346 148 330 151 322 160 Z',
    'M326 176 C334 180 346 180 354 175', 'M318 162 C332 172 350 172 360 158')
  // le nez : un bout rond éclairé, une ombre dessous
  + oval(313, 186, 7, 5, SKIN.shade, 0.7) + oval(315, 182, 4.4, 3, SKIN.hi, 0.9)
  // la bouche : un grand sourire ouvert, la lèvre du haut et deux petits crocs, la langue
  + `<path d="M280 198 C292 202 312 204 328 200 C326 210 316 218 302 218 C290 218 282 210 280 198 Z" fill="url(#g-mouth)"/>`
  + shape('M284 200 C296 204 314 205 326 201 L325 205 C312 208 296 207 285 204 Z', '#ffffff')
  + shape('M292 204 L295 211 L298 205 Z', '#ffffff') + shape('M314 205 L317 212 L320 205 Z', '#ffffff')
  + oval(304, 214, 8, 3, '#e86a8a', 0.9)
  + line('M278 197 L274 194', SKIN.line, 2) + line('M298 228 C304 230 312 230 318 228', SKIN.shade, 2, 0.8)
);

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'hair', cls: 'a-hair', d: S.hair, body: use('hair', 'url(#g-hair)') + clip('hair',
    // de grandes mèches qui flottent : un reflet bleu clair sur le dôme, des mèches plus claires qui s'envolent à gauche
    shape(sm('300,14 344,30 372,60 384,96! 364,64 340,40'), HAIR.sheen, 0.55)
    + shape(sm('120,200 100,236 82,270 54,292! 90,262 112,232 132,206'), HAIR.hi, 0.5)
    + shape(sm('150,236 120,270 96,310 80,322! 110,296 136,262 160,240'), HAIR.hi, 0.45)
    + shape(sm('110,150 90,180 66,200 52,214! 80,198 104,176 120,156'), HAIR.hi, 0.4)
    + shape(sm('180,60 160,96 150,140 152,190 170,240! 166,190 168,140 178,100 196,70'), '#5a5688', 0.45)
    + glint([[376, 150, 0], [384, 190, 3], [372, 228, 0]], HAIR.sheen, 0.5)) },
  ...TENTS.filter((t) => t.far).map((t) => ({ id: t.id, cls: `a-${t.id}`, d: tentD(t), body: tentBody(t) })),
  { id: 'fin', cls: 'a-fin', d: S.fin, shadow: [sh(['hair'], -3, 4, SH.hair, 0.5)], body: use('fin', 'url(#g-fin)') + clip('fin',
    // les rayons de la nageoire : des fuseaux qui partent de la base, sombres d'un côté, clairs de l'autre
    [[198, 160, 92, 96], [196, 150, 112, 92], [194, 140, 136, 98], [198, 166, 120, 150]].map(([x0, y0, x1, y1]) =>
      glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 4], [x1, y1, 0]], FIN.shade, 0.6)
      + glint([[x0, y0 - 3, 0], [(x0 + x1) / 2, (y0 + y1) / 2 - 3, 2], [x1, y1 - 3, 0]], FIN.hi, 0.55)).join('')) },
  { id: 'body', cls: 'a-body', d: S.body, shadow: [sh(['hair'], -4, 4, SH.hair, 0.5)], body: use('body', 'url(#g-skinB)') + clip('body',
    // le cou à l'ombre du menton, la poitrine et le ventre en formes douces, un petit nombril
    shape(sm('248,222 312,224 314,248 300,258 262,258 250,246'), SKIN.line, 0.75)
    + glint([[228, 262, 0], [250, 258, 3], [270, 262, 0]], SKIN.shade, 0.6) + glint([[312, 256, 0], [330, 258, 3], [346, 270, 0]], SKIN.shade, 0.6)
    + oval(290, 270, 30, 12, SKIN.hi, 0.4, 4) + glint([[262, 290, 0], [290, 296, 3], [320, 292, 0]], SKIN.shade, 0.6)
    + oval(292, 318, 3, 2, SKIN.deep, 0.8)) },
  ...TENTS.filter((t) => !t.far).map((t) => ({ id: t.id, cls: `a-${t.id}`, d: tentD(t), shadow: [sh(['t1', 't2'], -3, 5, SH.tent, 0.45)], body: tentBody(t) })),
  { id: 'sash', cls: 'a-body', d: S.sash, shadow: [sh(['body', 't3', 't4', 't5', 't6'], -3, 5, SH.tent, 0.5)], body: use('sash', 'url(#g-sash)') + clip('sash',
    glint([[200, 328, 0], [270, 338, 2.4], [346, 330, 0]], '#ffe0c8', 0.8)
    + [[220, 340], [250, 344], [284, 345], [318, 342]].map(([x, y]) => oval(x, y, 4, 2.6, '#ffd0a0', 0.8)).join('')) },
  { id: 'staff', cls: 'a-staff', d: S.staff, shadow: [sh(['body', 'sash', 'hair', 't5', 't6'], -4, 6, SH.wood, 0.4)], body: use('staff', 'url(#g-wood)') + clip('staff',
    // le bois : une arête claire, l'ombre ; les ficelles enroulées (paires sombre + claire)
    glint([[286, 334, 0], [380, 252, 2.6], [468, 128, 0]], WOOD.hi, 0.7)
    + [[350, 280], [364, 266], [432, 172], [440, 160]].map(([x, y]) => glint([[x - 5, y - 6, 0], [x, y, 3], [x + 5, y + 6, 0]], WOOD.deep, 0.75)).join('')) },
  { id: 'straps', cls: 'a-staff', d: S.straps, shadow: [sh(['hair'], -3, 5, SH.hair, 0.4)], body: use('straps', WOOD.shade) + clip('straps',
    glint([[404, 232, 0], [408, 260, 2.4], [402, 296, 0]], WOOD.hi, 0.6) + glint([[386, 252, 0], [380, 270, 2], [372, 286, 0]], WOOD.hi, 0.5)) },
  { id: 'knot', cls: 'a-staff', d: S.knot, shadow: [sh(['staff', 'hook'], -3, 5, SH.wood, 0.4)], body: use('knot', '#7a6a98') + clip('knot',
    // un chiffon froissé : des plis sombres et des bosses claires
    shape(sm('414,150 426,140 438,142 430,156 418,160'), '#a898c8', 0.9) + shape(sm('436,130 448,136 450,148 440,146'), '#b8aad6', 0.85)
    + glint([[418, 168, 0], [432, 162, 3], [446, 168, 0]], '#4a3c68', 0.7) + glint([[424, 132, 0], [434, 146, 2.4], [430, 160, 0]], '#4a3c68', 0.5)) },
  { id: 'hook', cls: 'a-staff', d: S.hook, shadow: [sh(['staff'], -3, 5, SH.wood, 0.4)], body: use('hook', 'url(#g-hook)') + clip('hook',
    glint([[470, 96, 0], [500, 80, 3], [532, 86, 3], [548, 108, 0]], '#ffffff', 0.9) + glint([[488, 112, 0], [506, 98, 3], [530, 106, 0]], '#5e6a80', 0.6)) },
  { id: 'armL', cls: 'a-staff', d: S.armL, shadow: [sh(['body', 'hair', 'staff'], -3, 5, SH.skin, 0.45)], body: use('armL', 'url(#g-skinB)') + clip('armL',
    glint([[340, 236, 0], [370, 230, 3], [396, 226, 0]], SKIN.hi, 0.6) + glint([[340, 258, 0], [370, 256, 3], [396, 248, 0]], SKIN.deep, 0.5)) },
  { id: 'handL', cls: 'a-staff', d: S.handL, shadow: [sh(['staff', 'armL', 'hair'], -3, 5, SH.skin, 0.45)], body: use('handL', 'url(#g-skinB)') + clip('handL',
    // les doigts qui serrent le bâton : des creux et des bosses éclairées, le pouce par-dessus
    [[392, 220, 424, 224], [390, 232, 426, 236], [394, 243, 420, 246]].map(([x1, y1, x2, y2]) => glint([[x1, y1, 0], [(x1 + x2) / 2, (y1 + y2) / 2, 2.4], [x2, y2, 0]], SKIN.deep, 0.65)
      + glint([[x1, y1 - 2.6, 0], [(x1 + x2) / 2, (y1 + y2) / 2 - 2.6, 1.4], [x2, y2 - 2.6, 0]], SKIN.hi, 0.6)).join('')
    + oval(404, 212, 8, 3.4, SKIN.hi, 0.7, -8)) },
  { id: 'face', cls: 'a-head', d: S.face, shadow: [sh(['hair', 'body', 'fin'], -4, 5, SH.skin, 0.45)], body: faceBody },
  { id: 'lockL', cls: 'a-head', d: sm('214,104 228,120 224,160 216,196 206,216! 202,182 204,140 208,114'), shadow: [sh(['face'], -2, 4, SH.skin, 0.4)],
    body: use('lockL', 'url(#g-hair)') + clip('lockL', glint([[218, 118, 0], [218, 150, 2.4], [210, 190, 0]], HAIR.hi, 0.5)) },
  { id: 'lockR', cls: 'a-head', d: sm('364,98 380,118 388,158 388,198 382,228! 376,196 372,158 366,124'), shadow: [sh(['face'], -2, 4, SH.skin, 0.4)],
    body: use('lockR', 'url(#g-hair)') + clip('lockR', glint([[372, 114, 0], [382, 156, 2.4], [384, 200, 0]], HAIR.sheen, 0.6)) },
  { id: 'ear', cls: 'a-head', d: S.ear, shadow: [sh(['hair', 'fin', 'lockL'], -3, 4, SH.hair, 0.45)], body: use('ear', 'url(#g-skinB)') + clip('ear',
    shape(sm('206,112 214,124 218,144 212,152'), SKIN.deep, 0.6)) },
  { id: 'bangs', cls: 'a-head', d: S.bangs, shadow: [sh(['face', 'ear'], -3, 6, SH.skin, 0.45)], body: use('bangs', 'url(#g-hair)') + clip('bangs',
    shape(sm('276,54 320,56 352,70 372,92! 346,74 318,64'), HAIR.sheen, 0.55) + glint([[226, 100, 0], [246, 86, 3], [268, 80, 0]], HAIR.hi, 0.45)) },
  { id: 'armR', cls: 'a-armR', d: S.armR, shadow: [sh(['body', 'sash', 'staff', 'hair'], -3, 5, SH.skin, 0.45)], body: use('armR', 'url(#g-skinB)') + clip('armR',
    // l'épaule ronde éclairée, le coude, un bracelet fin au poignet
    oval(224, 252, 14, 10, SKIN.hi, 0.6, -20) + glint([[226, 288, 0], [256, 302, 3], [290, 314, 0]], SKIN.deep, 0.5)
    + glint([[232, 276, 0], [244, 284, 2.6], [252, 296, 0]], SKIN.deep, 0.6)
    + glint([[282, 278, 3], [286, 296, 3], [284, 312, 3]], '#f4ecff', 0.9)) },
  { id: 'handR', cls: 'a-armR', d: S.handR, shadow: [sh(['staff', 'armR', 'body', 'sash'], -3, 5, SH.skin, 0.45)], body: use('handR', 'url(#g-skinB)') + clip('handR',
    [[300, 284, 334, 284], [298, 296, 336, 298], [300, 308, 330, 310]].map(([x1, y1, x2, y2]) => glint([[x1, y1, 0], [(x1 + x2) / 2, (y1 + y2) / 2, 2.4], [x2, y2, 0]], SKIN.deep, 0.65)
      + glint([[x1, y1 - 2.6, 0], [(x1 + x2) / 2, (y1 + y2) / 2 - 2.6, 1.4], [x2, y2 - 2.6, 0]], SKIN.hi, 0.6)).join('')) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : elle flotte (le haut du corps monte et descend), la chevelure et la nageoire ondulent, chaque tentacule
// ondoie à son rythme, le bâton oscille dans ses mains, elle cligne des yeux.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : elle arme son crochet en arrière (élan), puis le rabat en avant vers la
// droite (frappe) pendant que les tentacules se tendent ; tout revient à la pose de repos.
const PIV = { up: [280, 340], head: [292, 240], hair: [260, 120], fin: [200, 160], staff: [340, 246], armR: [220, 250],
  t1: [200, 346], t2: [330, 346], t3: [210, 352], t4: [230, 360], t5: [318, 360], t6: [268, 362] };
const IDLE = {
  'a-head': ['head', 'head 3s ease-in-out infinite alternate'],
  'a-hair': ['hair', 'hair 3.4s ease-in-out infinite alternate'],
  'a-fin': ['fin', 'fin 1.6s ease-in-out infinite alternate'],
  'a-staff': ['staff', 'staff 2.6s ease-in-out infinite alternate'],
  'a-armR': ['armR', 'armR 2.6s ease-in-out infinite alternate'],
  'a-body': ['up', 'up 2.2s ease-in-out infinite alternate'],
  'a-t1': ['t1', 'tl 2.4s ease-in-out infinite alternate'],
  'a-t2': ['t2', 'tr 2.8s ease-in-out infinite alternate'],
  'a-t3': ['t3', 'tl 3.1s ease-in-out -.6s infinite alternate'],
  'a-t4': ['t4', 'tl 2.6s ease-in-out -1.1s infinite alternate'],
  'a-t5': ['t5', 'tr 2.9s ease-in-out -.4s infinite alternate'],
  'a-t6': ['t6', 'tr 3.3s ease-in-out -1.4s infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-blink{animation:blink 4.4s linear infinite}
@keyframes up{from{transform:none}to{transform:translate(0,-3px)}}
@keyframes head{from{transform:none}to{transform:rotate(-1.6deg)}}
@keyframes hair{from{transform:none}to{transform:rotate(1.8deg)}}
@keyframes fin{from{transform:none}to{transform:rotate(-6deg)}}
@keyframes staff{from{transform:none}to{transform:rotate(-1.6deg)}}
@keyframes armR{from{transform:none}to{transform:rotate(-1.2deg)}}
@keyframes tl{from{transform:rotate(-2deg)}to{transform:rotate(3deg)}}
@keyframes tr{from{transform:rotate(2deg)}to{transform:rotate(-3deg)}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
${atk('a-staff', 'staff-atk')}${atk('a-armR', 'armR-atk')}${atk('a-head', 'head-atk')}${atk('a-hair', 'hair-atk')}${atk('a-fin', 'fin-atk')}
${atk('a-t3', 'tl-atk')}${atk('a-t4', 'tl-atk')}${atk('a-t1', 'tl-atk')}${atk('a-t5', 'tr-atk')}${atk('a-t6', 'tr-atk')}${atk('a-t2', 'tr-atk')}
@keyframes staff-atk{0%{transform:none}32%{transform:rotate(-13deg)}50%{transform:rotate(15deg)}64%{transform:rotate(11deg)}100%{transform:none}}
@keyframes armR-atk{0%{transform:none}32%{transform:translate(4px,6px) rotate(-3deg)}50%{transform:translate(-8px,-6px) rotate(3deg)}64%{transform:translate(-6px,-4px) rotate(2deg)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}32%{transform:rotate(-3deg)}50%{transform:translate(3px,1px) rotate(3deg)}100%{transform:none}}
@keyframes hair-atk{0%{transform:none}32%{transform:rotate(-2deg)}52%{transform:rotate(4deg)}100%{transform:none}}
@keyframes fin-atk{0%{transform:none}32%{transform:rotate(8deg)}52%{transform:rotate(-12deg)}100%{transform:none}}
@keyframes tl-atk{0%{transform:none}32%{transform:rotate(4deg)}52%{transform:rotate(-7deg)}100%{transform:none}}
@keyframes tr-atk{0%{transform:none}32%{transform:rotate(-4deg)}52%{transform:rotate(7deg)}100%{transform:none}}
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
  let s = figure({ w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  // le haut du corps (avec la tête, les cheveux, la nageoire, le bâton et les bras) flotte au-dessus des tentacules
  for (const c of ['a-head', 'a-hair', 'a-fin', 'a-staff', 'a-armR']) s = nest(s, c, 'a-body');
  return s;
}

module.exports = { id: 'angels-4', w: W, h: H, pad: PAD, foot: [272, 470], svg };
