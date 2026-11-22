// Le dino-voile (bayou-1), monstre du Bayou : redessiné par le code d'après le dessin d'origine, dans le même cadre
// (407 × 413, mêmes proportions, même pose) : petit dinosaure vert dressé sur ses deux pattes, tourné vers la droite ;
// grande crête orange en éventail sur la tête, voile orange sur le dos, nageoire orange sur la queue, ventre crème,
// œil orange furieux sous une arcade froncée, gueule ouverte aux crocs pointus, petit bras griffu replié, pattes
// arrière puissantes aux griffes claires.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. Contour décalqué sur l'original
// (outils/contour.py).
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 407, H = 413, PAD = 44;

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
const GREEN = { hi: '#b4f2bc', lite: '#74d892', base: '#44b46c', mid: '#30995a', shade: '#207a48', deep: '#145a36' };
const ORA = { hi: '#ffe0a0', lite: '#ffb455', base: '#f58c2c', shade: '#cc621a', deep: '#8e3c10' };
const CREAM = { hi: '#fffcec', base: '#fbe7b6', shade: '#dcbd88' };
const SH = { green: '#0c3a22', orange: '#6a2608', cream: '#7a5a30' };

// ---------- dégradés ----------
const defs = [
  lin('g-green', 330, 120, 150, 360, [[0, '#7ade98'], [0.45, GREEN.base], [1, GREEN.shade]]),
  lin('g-greenFar', 0, 0, 0, 1, [[0, GREEN.mid], [1, GREEN.deep]], false),
  lin('g-tail', 140, 240, 10, 160, [[0, GREEN.base], [0.6, GREEN.mid], [1, '#2a8a52']]),
  lin('g-crest', 250, 110, 318, 10, [[0, ORA.deep], [0.3, ORA.shade], [0.7, ORA.base], [1, ORA.lite]]),
  lin('g-sail', 0, 0, 0, 1, [[0, ORA.lite], [0.5, ORA.base], [1, ORA.shade]], false),
  lin('g-belly', 0, 0, 0, 1, [[0, CREAM.hi], [0.5, CREAM.base], [1, CREAM.shade]], false),
  rad('g-eye', 0.6, 0.35, 0.8, [[0, '#fff6b0'], [0.35, '#ffd23a'], [0.75, '#f08a18'], [1, '#b04a0c']], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#1a3a1a', 0.75], [0.5, '#1a3a1a', 0]], false),
  lin('g-eyelid', 0, 0, 0, 1, [[0, GREEN.lite], [1, GREEN.mid]], false),
  lin('g-mouth', 0, 156, 0, 206, [[0, '#2a060c'], [0.55, '#5a1420'], [1, '#8a2834']]),
  lin('g-claw', 0, 0, 0, 1, [[0, '#ffffff'], [0.5, '#ece6d8'], [1, '#a89c8c']], false),
].join('');

// ---------- silhouettes (le bord extérieur suit le contour mesuré sur l'original) ----------
const S = {
  // la patte du fond (à gauche), plus sombre, et son pied aux orteils vers la gauche
  legF: sm('106,296 146,300 152,330 141,343 126,348 121,354 121,378 129,389 132,400! 110,400 104,404! 101,402 75,400 55,401! 64,376 78,357 80,346 87,331 93,325 102,322 105,312'),
  // la nageoire orange sur la queue (derrière la queue)
  fin: sm('44,200! 56,217 63,219 72,219! 74,217 80,217 86,214! 88,216 105,219 120,228 128,237 134,237 137,234 136,213 132,209 138,198 138,192 143,187 144,180 '
    + '151,173 151,170 154,166 167,155 174,155 185,149 210,149 220,152 220,158 217,167 217,181 220,192 230,208 236,214 200,236 150,250 110,246 70,232'),
  // la queue : de la pointe (en haut à gauche) jusqu'aux hanches
  tail: sm('7,157! 14,154 22,157 30,164 37,177 41,198 48,212 62,232 92,246 130,252 160,250 150,300 103,303 91,302 70,295 51,282 35,264 29,252 23,232 22,180 16,165'),
  // le corps : des hanches à la poitrine (le haut caché sous la voile, le dessous entre les pattes)
  body: sm('96,252 140,232 190,222 236,212 262,206 286,226 290,258 282,282 262,302 258,322 236,330 211,327 182,330 165,325 156,325 141,343 126,348 108,330 103,303 94,282'),
  // le cou et la tête, la crête derrière ; la gueule (l'intérieur), la mâchoire du bas
  crest: sm('319,7! 299,11 280,20 268,28 245,49 240,57 236,69 230,86 229,106 236,118 256,112 280,104 306,100 333,98 320,79 312,60 310,47 311,28'),
  neck: sm('232,212 241,203 249,184 255,170 252,150 251,136 258,120 290,120 312,156 316,192 305,212 296,236 286,258 286,272 266,292 244,262'),
  mouth: sm('316,168 352,160 386,154 380,170 370,184 368,200 352,204 330,196 312,188'),
  jaw: sm('306,190 330,186 350,192 362,192 365,196 368,201! 366,206 351,211 338,209 321,203 313,203 302,200'),
  head: sm('238,118 250,106 270,98 294,93 318,92 333,96 348,100 358,106 385,131 392,135 398,141 396,149 386,155 370,160 352,166 334,174 318,186 304,190 288,176 270,156 254,136 246,120'),
  // le petit bras replié et sa main à trois griffes
  arm: sm('270,266 290,262 298,266 303,260 309,258 314,259 319,264 321,269 321,276 317,282 307,286 304,281 297,281 285,287 274,286'),
  // la patte de devant : grosse cuisse, tibia, grand pied aux griffes vers la droite
  legN: sm('196,288 240,280 262,298 266,318 267,331 263,342 259,346 257,353 254,358 260,367 272,374 290,373 302,375 314,386 319,398! 308,397 305,400 294,402 264,401 248,398 206,397! 205,382 209,368 213,363 221,358 226,344 220,330 198,318'),
};

// ---------- le visage ----------
/** Une dent pointue : la moitié du fond dans l'ombre, un filet de lumière sur l'autre flanc. b1, b2 = la racine, t = la pointe. */
function tooth([x1, y1], [x2, y2], [tx, ty]) {
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  const d = `M${x1} ${y1}Q${n((x1 + tx) / 2 - (ty - y1) * 0.08)} ${n((y1 + ty) / 2)} ${tx} ${ty}Q${n((x2 + tx) / 2 + (ty - y2) * 0.08)} ${n((y2 + ty) / 2)} ${x2} ${y2}Z`;
  const half = `M${x1} ${y1}L${tx} ${ty}L${n(mx)} ${n(my)}Z`;
  return shape(d, '#fbf4e8') + shape(half, '#d8c8bc', 0.8) + line(`M${n(mx + (x2 - mx) * 0.5)} ${n(my + (y2 - my) * 0.5)}L${n(tx + (x2 - tx) * 0.2)} ${n(ty + (y2 - ty) * 0.2)}`, '#ffffff', 1.2, 0.9);
}
const TEETH_T = [[[338, 170], [347, 168], [343, 180]], [[351, 164], [361, 162], [356, 177]], [[364, 160], [374, 158], [369, 173]], [[376, 157], [386, 154], [382, 167]]];
const TEETH_B = [[[334, 192], [342, 194], [339, 184]], [[348, 195], [356, 196], [353, 185]], [[358, 194], [366, 194], [363, 183]]];

/** L'œil : l'anneau sombre, l'iris orange en dégradé, la pupille, l'ombre de la paupière, deux reflets ; l'arcade froncée. */
const EYE = { x: 321, y: 134, r: 17 };
function eye() {
  const { x, y, r } = EYE;
  const brow = 'M290 112 C306 106 328 110 348 122 C351 127 349 132 344 132 C328 124 310 120 296 122 C289 120 287 114 290 112 Z';
  return oval(x, y + 0.5, r + 2.8, r + 2.6, '#1e2a1a')
    + `<clipPath id="c-eye"><circle cx="${x}" cy="${y}" r="${r}"/></clipPath>`
    + dot(x, y, r, 'url(#g-eye)')
    + `<g clip-path="url(#c-eye)">`
    + oval(x + 2, y + 1, 5.4, 10, '#120808') + `<rect x="${x - r - 4}" y="${y - r - 4}" width="${2 * r + 8}" height="${n(r * 1.2)}" fill="url(#g-lid)"/>`
    + dot(x - 3.5, y - 5, 3, '#fff') + dot(x + 6, y + 6, 1.4, '#fff', 0.9)
    + '</g>'
    + `<g class="a-blink" opacity="0"><circle cx="${x}" cy="${y}" r="${r + 1}" fill="url(#g-eyelid)"/>${line(`M${x - r} ${y + 3} Q${x} ${y + 9} ${x + r} ${y + 2}`, '#1e2a1a', 2.6)}</g>`
    + `<path d="${brow}" transform="translate(-2 3)" fill="${SH.green}" opacity="0.5"/>` + shape(brow, GREEN.deep)
    + glint([[294, 110, 0], [318, 108, 2.6], [342, 118, 0]], GREEN.lite, 0.8);
}

const headBody = use('head', 'url(#g-green)') + clip('head',
  // le dessous de la tête à l'ombre, le dessus du museau éclairé, deux écailles plus sombres, la narine
  shape(sm('250,130 270,156 292,176 318,188 350,170 380,160 400,156 400,200 240,200'), GREEN.shade, 0.5)
  + glint([[300, 100, 0], [340, 102, 4], [372, 120, 3], [394, 138, 0]], GREEN.hi, 0.7)
  + oval(352, 118, 3, 2, GREEN.deep, 0.6) + oval(364, 126, 2.4, 1.6, GREEN.deep, 0.5) + oval(286, 150, 2.6, 1.8, GREEN.deep, 0.5)
  + oval(386, 138, 3.4, 2, '#0e3a20', 0.9, -20)
  // le coin de la gueule
  + glint([[312, 176, 0], [320, 182, 3], [324, 190, 0]], '#0e3a20', 0.6)
  + eye()
);

// ---------- les pattes et la main ----------
/** Une griffe claire en croc : de la racine (x, y) vers la pointe, longue de `len`, tournée de `a` degrés. */
const claw = (x, y, len, a) => `<g transform="rotate(${a} ${x} ${y})">${shape(`M${x - 3.4} ${y} Q${x - 2} ${y + len * 0.7} ${x + 2} ${y + len} Q${x + 3.6} ${y + len * 0.5} ${x + 3.4} ${y} Z`, 'url(#g-claw)')}</g>`;

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'legF', cls: 'a-legF', d: S.legF, body: use('legF', 'url(#g-greenFar)') + clip('legF',
    // la cuisse et le pied du fond, plus sombres ; les orteils séparés par deux creux ; les griffes claires
    shape(sm('86,330 120,320 130,350 120,380 128,402 56,404'), GREEN.deep, 0.35)
    + glint([[78, 382, 0], [84, 392, 2.4], [86, 400, 0]], GREEN.deep, 0.7) + glint([[98, 380, 0], [100, 392, 2.4], [100, 401, 0]], GREEN.deep, 0.6)
    + claw(60, 392, 10, 60) + claw(80, 394, 9, 30) + claw(100, 395, 8, 15)) },
  { id: 'fin', cls: 'a-tail', d: S.fin, body: use('fin', 'url(#g-sail)') + clip('fin',
    // les côtes de la voile : quelques fuseaux plus sombres qui s'ouvrent en éventail depuis le dos
    [[70, 236, 60, 212], [110, 246, 100, 220], [150, 236, 150, 176], [182, 226, 186, 156], [212, 220, 214, 158]].map(([x0, y0, x1, y1]) =>
      glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 4], [x1, y1, 0]], ORA.shade, 0.55)).join('')
    + glint([[160, 168, 0], [186, 154, 4], [212, 152, 0]], ORA.hi, 0.8) + glint([[60, 214, 0], [80, 218, 3], [100, 220, 0]], ORA.hi, 0.6)) },
  { id: 'tail', cls: 'a-tail', d: S.tail, shadow: [sh(['fin', 'legF'], -3, 5, SH.green, 0.45)], body: use('tail', 'url(#g-tail)') + clip('tail',
    // le dessous crème de la queue, un reflet sur le dessus
    shape(sm('22,190 30,240 46,270 74,292 104,302 120,300 104,290 70,276 46,250 34,220'), 'url(#g-belly)')
    + glint([[24, 160, 0], [36, 186, 3], [56, 222, 4], [96, 244, 0]], GREEN.hi, 0.5)) },
  { id: 'body', cls: 'a-body', d: S.body, shadow: [sh(['tail', 'fin', 'legF'], -4, 5, SH.green, 0.45)], body: use('body', 'url(#g-green)') + clip('body',
    // le ventre crème (dessous), son ombre ; une lumière sur le dos
    shape(sm('150,300 190,306 230,304 268,290 290,262 300,262 290,330 140,340'), 'url(#g-belly)')
    + glint([[150, 316, 0], [200, 326, 5], [250, 320, 0]], CREAM.shade, 0.7)
    + glint([[150, 236, 0], [200, 226, 4], [250, 216, 0]], GREEN.hi, 0.5)
    + oval(176, 262, 3, 2, GREEN.deep, 0.5) + oval(206, 248, 2.4, 1.6, GREEN.deep, 0.5) + oval(232, 272, 2.6, 1.8, GREEN.deep, 0.45)) },
  { id: 'neck', cls: 'a-body', d: S.neck, shadow: [sh(['body', 'fin'], -3, 5, SH.green, 0.4)], body: use('neck', 'url(#g-green)') + clip('neck',
    // la gorge crème qui descend sur la poitrine
    shape(sm('300,196 312,200 300,236 288,262 280,284 262,292 270,262 284,230'), 'url(#g-belly)')
    + glint([[258, 130, 0], [254, 160, 3.4], [246, 196, 0]], GREEN.shade, 0.5)) },
  { id: 'arm', cls: 'a-arm', d: S.arm, rim: { on: ['neck', 'body'], color: GREEN.deep, w: 1.4, o: 0.9 }, shadow: [sh(['neck', 'body'], -3, 5, SH.green, 0.45)], body: use('arm', 'url(#g-green)') + clip('arm',
    // les doigts repliés : deux creux sombres, les bouts éclairés ; les petites griffes
    glint([[306, 266, 0], [310, 272, 2.2], [312, 280, 0]], GREEN.deep, 0.7) + glint([[314, 264, 0], [316, 270, 2], [316, 278, 0]], GREEN.deep, 0.6)
    + shape(sm('272,280 290,284 300,282 306,288 272,290'), GREEN.shade, 0.6)
    + oval(312, 262, 3, 2, GREEN.hi, 0.8))
    + claw(306, 258, 6, 200) + claw(314, 260, 6, 215) + claw(320, 268, 6, 235) },
  { id: 'legN', cls: 'a-legN', d: S.legN, rim: { on: ['body', 'tail'], color: GREEN.deep, w: 1.6, o: 0.9 }, shadow: [sh(['body', 'legF', 'tail'], -4, 5, SH.green, 0.45)], body: use('legN', 'url(#g-green)') + clip('legN',
    // la grosse cuisse éclairée en haut à droite, l'ombre derrière ; le pied : deux creux entre les orteils
    glint([[214, 292, 0], [240, 286, 4], [260, 300, 3], [264, 318, 0]], GREEN.hi, 0.55)
    + shape(sm('196,300 214,320 226,344 220,362 208,372 204,404 190,404'), GREEN.deep, 0.35)
    + glint([[262, 380, 0], [270, 390, 2.6], [272, 400, 0]], GREEN.deep, 0.7) + glint([[284, 380, 0], [290, 390, 2.6], [292, 400, 0]], GREEN.deep, 0.6)
    + glint([[272, 376, 0], [296, 378, 2.6], [310, 388, 0]], GREEN.hi, 0.6))
    + claw(272, 396, 9, -40) + claw(294, 396, 9, -55) + claw(316, 394, 9, -75) },
  { id: 'crest', cls: 'a-crest', d: S.crest, body: use('crest', 'url(#g-crest)') + clip('crest',
    // la crête en éventail : des côtes en fuseaux qui s'ouvrent depuis le crâne, un bord éclairé
    [[244, 104, 246, 50], [262, 104, 272, 30], [282, 100, 296, 18], [302, 98, 314, 22]].map(([x0, y0, x1, y1]) =>
      glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 4.4], [x1, y1, 0]], ORA.shade, 0.5)).join('')
    + glint([[312, 30, 0], [314, 56, 3], [326, 86, 0]], ORA.hi, 0.85)) },
  { id: 'mouth', cls: 'a-head', d: S.mouth, body: use('mouth', 'url(#g-mouth)') + clip('mouth',
    `<g class="a-teeth">${shape('M318 190 C326 178 342 174 356 180 C362 184 362 192 356 196 L318 198 Z', '#e0707a')
    + glint([[326, 182, 0], [338, 178, 3], [350, 182, 0]], '#f8a6ae', 0.8) + TEETH_B.map((t) => tooth(...t)).join('')}</g>`
    + TEETH_T.map((t) => tooth(...t)).join('')) },
  { id: 'jaw', cls: 'a-jaw', d: S.jaw, shadow: [sh(['neck'], -3, 5, SH.green, 0.4)], body: use('jaw', 'url(#g-green)') + clip('jaw',
    shape(sm('300,204 326,206 346,210 368,206 368,216 300,216'), 'url(#g-belly)') + glint([[318, 191, 0], [340, 194, 2.4], [362, 195, 0]], GREEN.hi, 0.7)) },
  { id: 'head', cls: 'a-head', d: S.head, rim: { on: ['neck'], color: GREEN.deep, w: 1.2, o: 0.6 }, shadow: [sh(['crest', 'neck', 'jaw'], -3, 6, SH.green, 0.45)], body: headBody },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : il souffle (le corps se soulève), la tête hoche, la mâchoire tremble, la queue et sa nageoire balancent, la
// crête frémit, le petit bras s'agite, il cligne. Les pattes restent plantées.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : il se ramasse en arrière, se jette en avant la gueule grande ouverte
// et mord (la mâchoire claque), la queue fouette, la crête se dresse ; puis il revient exactement à sa place.
const G = [212, 400];
const PIV = { root: G, body: [200, 330], head: [262, 200], jaw: [308, 192], tail: [130, 270], crest: [262, 108], arm: [276, 274], legF: [120, 306], legN: [226, 300] };
const IDLE = {
  'a-body': ['body', 'body 1.4s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 2.4s ease-in-out infinite alternate'],
  'a-jaw': ['jaw', 'jaw .4s ease-in-out infinite alternate'],
  'a-teeth': ['jaw', 'jaw .4s ease-in-out infinite alternate'],
  'a-tail': ['tail', 'tail 2.2s ease-in-out infinite alternate'],
  'a-crest': ['crest', 'crest 1.8s ease-in-out infinite alternate'],
  'a-arm': ['arm', 'arm 1.1s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('')
  + ['root', 'legF', 'legN'].map((k) => `.a-${k}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px}`).join('') + `
.a-blink{animation:blink 4.2s linear infinite}
@keyframes body{from{transform:none}to{transform:translate(0,-2.4px) scale(1.006,1.012)}}
@keyframes head{from{transform:none}to{transform:translate(0.5px,-1.4px) rotate(-1.8deg)}}
@keyframes jaw{from{transform:none}to{transform:rotate(1.8deg)}}
@keyframes tail{from{transform:rotate(-1.5deg)}to{transform:rotate(2.5deg)}}
@keyframes crest{from{transform:none}to{transform:rotate(-2.4deg)}}
@keyframes arm{from{transform:none}to{transform:rotate(-8deg)}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-body', 'body-atk')}${atk('a-head', 'head-atk')}${atk('a-jaw', 'jaw-atk')}${atk('a-teeth', 'jaw-atk')}${atk('a-tail', 'tail-atk')}
${atk('a-crest', 'crest-atk')}${atk('a-arm', 'arm-atk')}${atk('a-legF', 'legF-atk')}${atk('a-legN', 'legN-atk')}
@keyframes root-atk{0%{transform:none}28%{transform:translate(-8px,2px) rotate(-2deg)}46%{transform:translate(26px,-6px) rotate(3deg)}60%{transform:translate(22px,0) rotate(1deg)}80%{transform:translate(4px,0)}100%{transform:none}}
@keyframes body-atk{0%{transform:none}28%{transform:scale(0.98,0.96)}46%{transform:scale(1.03,0.99)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}28%{transform:rotate(-10deg)}46%{transform:translate(4px,4px) rotate(8deg)}60%{transform:translate(3px,2px) rotate(5deg)}82%{transform:rotate(-1deg)}100%{transform:none}}
@keyframes jaw-atk{0%{transform:none}28%{transform:rotate(16deg)}40%{transform:rotate(19deg)}50%{transform:rotate(-4deg)}62%{transform:rotate(-3deg)}100%{transform:none}}
@keyframes tail-atk{0%{transform:none}28%{transform:rotate(-7deg)}46%{transform:rotate(9deg)}62%{transform:rotate(5deg)}100%{transform:none}}
@keyframes crest-atk{0%{transform:none}28%{transform:rotate(4deg)}46%{transform:rotate(-8deg)}62%{transform:rotate(-4deg)}100%{transform:none}}
@keyframes arm-atk{0%{transform:none}28%{transform:rotate(10deg)}46%{transform:rotate(-26deg)}62%{transform:rotate(-14deg)}100%{transform:none}}
@keyframes legF-atk{0%{transform:none}28%{transform:rotate(-5deg)}46%{transform:rotate(12deg)}62%{transform:rotate(4deg)}100%{transform:none}}
@keyframes legN-atk{0%{transform:none}28%{transform:rotate(5deg)}46%{transform:rotate(-12deg)}62%{transform:rotate(-4deg)}100%{transform:none}}
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
  // la tête emporte la mâchoire et la crête ; le corps emporte la tête, la queue et le bras
  for (const c of ['a-jaw', 'a-crest']) s = nest(s, c, 'a-head');
  for (const c of ['a-head', 'a-tail', 'a-arm']) s = nest(s, c, 'a-body');
  // tout le dinosaure bondit pendant l'attaque
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'bayou-1', w: W, h: H, pad: PAD, foot: G, svg };
