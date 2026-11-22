// La tortue hargneuse (bayou-2), monstre du Bayou : redessinée par le code d'après le dessin d'origine, dans le même
// cadre (452 × 296, mêmes proportions, même pose) : une tortue trapue tournée vers la droite ; carapace olive bombée
// hérissée de grands pics coniques, bordée d'une bande brune ; tête verte à casque plus clair, œil rouge cerclé de jaune
// sous un sourcil plongeant, bec crochu gris-brun, gueule ouverte à langue rose, mâchoire claire ; plastron beige à
// segments ; pattes trapues à écailles et griffes blanches ; queue pointue à gauche.
// DÉCALQUÉE : silhouette exacte (outils/silhouette.py → master), tête, pattes et carapace relevées par zone.py / silbox ;
// détails lus sur des gros plans quadrillés. La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 452, H = 296, PAD = 40;

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

// ---------- couleurs (relevées sur l'original) ----------
const SHL = { hi: '#e8dc9a', lite: '#a89a5a', base: '#7a6e3c', mid: '#62582e', shade: '#4a4224', deep: '#2e2816' };
const SKIN = { hi: '#d2e08a', lite: '#9ab05a', base: '#6e8a40', mid: '#5a7234', shade: '#3e5226', deep: '#24321a' };
const RIM = { base: '#4e4826', shade: '#2e2a16', lite: '#7a7040' };
const BELLY = { hi: '#ecd2a0', base: '#c8a472', shade: '#8e6c48' };
const SH = { dark: '#140e06' };

// ---------- les formes relevées sur l'original ----------
const SHELL = sm('342,57 305,78 301,76 297,77 291,71 283,74 275,69 268,68 255,43 230,4 224,4 217,18 199,67 189,66 186,63 182,63 178,67 144,37 137,37 135,39 129,90 116,99 91,91 83,92 83,104 87,124 80,131 76,131 74,133 73,151 56,152 52,156 63,177 57,178 50,176 47,178 47,188 51,196 49,198 40,197 40,200 313,200 322,128 342,92');
const LOWER = sm('4,257 4,264 6,266 14,266 51,248 62,244 67,244 72,241 81,241 83,243 82,249 79,254 79,261 74,269 75,274 78,276 76,279 78,289 86,290 88,288 94,288 99,290 102,288 104,290 102,293 109,292 111,289 118,290 125,293 128,289 134,289 136,293 141,293 143,290 151,292 153,287 163,287 165,289 172,288 171,281 173,279 188,280 190,277 200,278 201,270 195,257 201,255 208,245 230,245 232,255 227,269 227,274 230,276 230,287 252,287 256,290 267,289 274,293 279,293 280,288 285,288 288,290 297,289 300,291 305,291 306,287 324,289 324,279 330,278 330,196 27,197 26,203 34,217 20,217 17,219 21,232 13,241');
const HEAD = sm('340,94 338,98 333,102 335,109 330,113 323,126 322,135 320,139 319,158 312,174 310,183 310,193 316,196 317,201 322,205 322,207 319,208 317,206 312,206 311,210 322,221 340,229 355,233 384,233 403,227 413,219 412,214 409,211 407,211 405,217 400,216 398,203 394,194 389,189 381,189 373,184 372,180 376,179 382,171 392,166 407,165 408,161 411,160 417,153 422,153 426,157 431,166 431,168 427,171 427,174 429,177 436,178 437,189 439,192 441,192 444,187 446,177 446,162 442,147 432,130 422,119 401,103 393,101 382,95');
const FRONT = sm('183,205 183,221 194,242 231,243 233,256 229,271 231,273 230,281 233,284 251,285 251,278 253,275 257,274 263,269 273,270 274,273 278,275 282,270 288,267 294,267 300,273 303,273 309,267 317,267 316,261 313,258 306,255 304,243 300,239 299,222 292,214 286,211 278,210 274,207 264,206 260,210 252,210 248,212 243,211 238,216 235,216 232,202 211,202 203,206 197,204');
const LEG_B = sm('146,208 140,211 129,208 117,208 114,210 112,214 100,212 95,218 85,216 84,210 79,210 80,224 85,237 82,243 83,249 80,253 80,261 77,266 79,283 84,285 96,285 96,277 101,277 113,269 122,269 120,259 123,256 149,254 154,252 161,245 163,230 160,222');

// ---------- dégradés ----------
const defs = [
  lin('g-shell', 320, 20, 120, 200, [[0, '#a89a58'], [0.45, SHL.base], [1, SHL.shade]]),
  rad('g-shellLite', 0.5, 0.5, 0.5, [[0, '#d8cc88', 0.7], [1, '#d8cc88', 0]], false),
  lin('g-spike', 0, 0, 1, 0, [[0, SHL.shade], [0.5, SHL.lite], [0.75, SHL.hi], [1, SHL.lite]], false),
  lin('g-skin', 0, 0, 1, 1, [[0, SKIN.lite], [0.5, SKIN.base], [1, SKIN.shade]], false),
  lin('g-head', 440, 90, 320, 230, [[0, '#a8bc68'], [0.45, SKIN.base], [1, SKIN.mid]]),
  lin('g-lower', 0, 196, 0, 296, [[0, SKIN.shade], [1, SKIN.deep]]),
  lin('g-belly', 0, 0, 0, 1, [[0, BELLY.hi], [0.5, BELLY.base], [1, BELLY.shade]], false),
  lin('g-beak', 0, 0, 1, 1, [[0, '#a8988e'], [0.5, '#6e5e58'], [1, '#3e3230']], false),
  lin('g-jaw', 0, 0, 0, 1, [[0, '#dcd896'], [0.5, '#b4b46e'], [1, '#7a7a4a']], false),
  rad('g-iris', 0.65, 0.5, 0.75, [[0, '#ffe680'], [0.3, '#f0b020'], [0.55, '#c02a1a'], [1, '#5a0a0a']], false),
  lin('g-mouth', 0, 175, 0, 210, [[0, '#3a0a10'], [1, '#8a2a34']]),
  lin('g-claw', 0, 0, 0, 1, [[0, '#ffffff'], [0.6, '#e8e4dc'], [1, '#8a8478']], false),
].join('');

// ---------- les pics : [base gauche, base droite, pointe] (relevés sur l'original), la face droite éclairée ----------
const SPIKES = [[[204, 82], [256, 80], [229, 5]], [[118, 98], [166, 84], [139, 37]], [[300, 94], [338, 98], [343, 57]], [[96, 128], [122, 108], [83, 91]],
  [[150, 128], [192, 116], [172, 102]], [[208, 118], [252, 110], [230, 96]], [[104, 158], [138, 142], [120, 128]], [[62, 168], [86, 150], [56, 132]],
  [[54, 200], [76, 186], [44, 168]], [[268, 104], [300, 108], [283, 88]]];
const spikeFace = ([a, b, t]) => {
  const m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  return shape(`M${a[0]} ${a[1]} L${t[0]} ${t[1]} L${b[0]} ${b[1]} Z`, 'url(#g-spike)')
    + shape(`M${a[0]} ${a[1]} L${t[0]} ${t[1]} L${n(m[0] + (b[0] - a[0]) * 0.08)} ${n(m[1])} Z`, SHL.shade, 0.75)
    + glint([[t[0] + 1, t[1] + 4, 0], [n((t[0] + b[0]) / 2), n((t[1] + b[1]) / 2), 2.4], [b[0] - 2, b[1] - 2, 0]], SHL.hi, 0.85)
    + `<path d="M${a[0]} ${a[1]} L${t[0]} ${t[1]} L${b[0]} ${b[1]}" fill="none" stroke="${SHL.deep}" stroke-width="1.6" opacity="0.6"/>`;
};

// ---------- le visage ----------
const EYE = { x: 362, y: 151, rx: 15, ry: 13 };
const headBody = use('head', 'url(#g-head)') + clip('head',
  // l'ombre du cou et du bas de la tête ; des taches claires sur la joue
  shape(sm('300,120 330,110 326,160 320,200 334,226 300,236'), SKIN.shade, 0.6)
  + [[330, 170, 3.4], [334, 186, 2.6], [344, 160, 2.4], [326, 150, 2]].map(([x, y, r]) => oval(x, y, r, r * 0.8, SKIN.hi, 0.6)).join('')
  // le casque : la plaque claire du dessus de la tête, jusqu'au bec, son bord plongeant au-dessus de l'œil
  + shape(sm('336,96 360,90 392,96 420,110 440,128 446,146 432,148 410,142 390,144 372,138 352,124 340,118'), '#a8b868')
  + glint([[352, 98, 0], [392, 100, 4], [432, 122, 0]], '#e0e8a8', 0.8)
  + glint([[344, 122, 0], [372, 138, 4], [410, 146, 3], [438, 148, 0]], SKIN.deep, 0.85)
  // l'œil : l'orbite sombre, l'iris rouge cerclé de jaune (à droite), la pupille, le reflet ; la paupière coupée par le casque
  + oval(EYE.x, EYE.y, EYE.rx + 2.6, EYE.ry + 2.4, '#1a0a08')
  + `<clipPath id="c-eye"><ellipse cx="${EYE.x}" cy="${EYE.y}" rx="${EYE.rx}" ry="${EYE.ry}"/></clipPath>`
  + oval(EYE.x, EYE.y, EYE.rx, EYE.ry, 'url(#g-iris)')
  + `<g clip-path="url(#c-eye)">${oval(EYE.x - 3, EYE.y - 1, 6, 8, '#1a0606')}${shape('M340 130 L390 130 L390 146 C376 140 360 138 344 142 Z', '#1a0a08', 0.85)}</g>`
  + dot(EYE.x - 2, EYE.y - 6, 3, '#ffffff') + dot(EYE.x + 7, EYE.y + 5, 1.4, '#ffffff', 0.9)
  + `<g class="a-blink" opacity="0">${oval(EYE.x, EYE.y, EYE.rx + 1, EYE.ry + 1, SKIN.base)}${line(`M${EYE.x - EYE.rx} ${EYE.y + 2} Q${EYE.x} ${EYE.y + 8} ${EYE.x + EYE.rx} ${EYE.y + 1}`, '#1a0a08', 2.4)}</g>`
  // les narines
  + oval(402, 143, 2.6, 2, '#1a2010') + oval(420, 141, 2.4, 1.8, '#1a2010')
  // le bec crochu : la pointe gris-brun qui descend
  + shape(sm('408,146 430,146 444,154 450,170 448,186 440,198 434,184 428,168 416,160'), 'url(#g-beak)')
  + glint([[430, 150, 0], [444, 166, 2.6], [444, 186, 0]], '#d0c4bc', 0.7)
  // la gueule ouverte : l'intérieur sombre, la langue rose
  + `<g class="a-mouth">${shape(sm('344,192 372,180 400,176 424,180 432,190 420,200 396,204 368,202'), 'url(#g-mouth)')}`
  + oval(392, 196, 18, 6, '#e07a82') + glint([[380, 193, 0], [392, 191, 2], [404, 193, 0]], '#ffb0b4', 0.8) + '</g>'
  // la mâchoire du bas, claire, son bord sombre
  + `<g class="a-jaw">${shape(sm('322,200 346,196 372,204 400,206 420,200 416,214 400,226 372,232 340,228 324,216'), 'url(#g-jaw)')}`
  + glint([[330, 200, 0], [372, 207, 2.6], [416, 202, 0]], '#f4f0c0', 0.8) + '</g>'
);

// ---------- les pattes ----------
/** Les doigts et les griffes blanches au bout d'une patte : [x, y] = la pointe de chaque griffe. */
const claws = (list) => list.map(([x, y]) => `<path d="M${x - 9} ${y - 18} Q${x - 9} ${y - 5} ${x + 1} ${y} Q${x + 5} ${y - 10} ${x + 4} ${y - 20} Z" fill="#3a3430"/>`
  + `<path d="M${x - 5} ${y - 12} Q${x - 5} ${y - 4} ${x + 1} ${y} Q${x + 3} ${y - 7} ${x + 3} ${y - 14} Z" fill="url(#g-claw)"/>`
  + glint([[x - 3, y - 12, 0], [x - 2, y - 6, 1.4], [x, y - 2, 0]], '#ffffff', 0.9)).join('');
const toes = (list) => list.map(([x, y]) => glint([[x - 9, y + 2, 0], [x, y + 5, 3], [x + 9, y + 2, 0]], SKIN.deep, 0.6) + oval(x + 2, y - 3, 5, 2.6, SKIN.hi, 0.6)).join('');
/** Des écailles en rangées sur une patte : une bosse claire en haut à droite, un creux sombre dessous. */
const scales = (list) => list.map(([x, y, r]) => glint([[x - r, y + r * 0.3, 0], [x, y + r * 0.45, 2.6], [x + r, y + r * 0.2, 0]], SKIN.deep, 0.55) + glint([[x - r * 0.7, y - r * 0.1, 0], [x + r * 0.1, y - r * 0.3, 2.4], [x + r * 0.8, y - r * 0.2, 0]], SKIN.hi, 0.5)).join('');

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  // le fond du bas (pattes du fond, plastron, queue), pris dans la silhouette : tout derrière
  { id: 'lower', cls: 'a-body', d: LOWER, body: use('lower', 'url(#g-lower)') + clip('lower',
    glint([[14, 258, 0], [40, 244, 5], [66, 236, 4], [96, 222, 0]], SKIN.lite, 0.6)) },
  // le plastron beige, en segments
  { id: 'belly', cls: 'a-body', d: sm('136,196 320,196 318,222 300,236 250,240 200,240 160,236 140,222'), shadow: [sh(['lower'], -3, 4, SH.dark, 0.4)],
    body: use('belly', 'url(#g-belly)') + clip('belly', [170, 200, 230, 262, 292].map((x) => glint([[x - 4, 196, 0], [x, 218, 3], [x + 2, 240, 0]], BELLY.shade, 0.7)
      + glint([[x + 2, 196, 0], [x + 6, 218, 1.6], [x + 8, 240, 0]], BELLY.hi, 0.7)).join('') + shape(sm('136,196 320,196 320,204 136,204'), RIM.shade, 0.7)) },
  // la patte arrière (de ce côté)
  { id: 'legB', cls: 'a-legB', d: LEG_B, shadow: [sh(['lower', 'belly'], -3, 5, SH.dark, 0.45)], body: use('legB', 'url(#g-skin)') + clip('legB',
    oval(132, 226, 26, 16, SKIN.hi, 0.35, -10) + scales([[110, 224, 14], [138, 222, 12], [100, 246, 12], [128, 244, 13], [152, 236, 10]]) + toes([[90, 266], [110, 266], [134, 262], [152, 254]])
    + shape(sm('78,262 160,250 168,290 78,290'), SKIN.deep, 0.35)) + claws([[86, 286], [104, 287], [124, 286], [144, 282], [160, 276]]) },
  // la patte avant (de ce côté) et le bas du plastron qui la rejoint
  { id: 'front', cls: 'a-legF', d: FRONT, shadow: [sh(['lower', 'belly'], -3, 5, SH.dark, 0.45)], body: use('front', 'url(#g-skin)') + clip('front',
    shape(sm('183,205 232,202 236,240 196,242 184,222'), 'url(#g-belly)')
    + oval(276, 228, 26, 18, SKIN.hi, 0.35, -10) + scales([[254, 222, 12], [282, 220, 12], [262, 244, 13], [290, 240, 12], [248, 258, 10], [300, 256, 10]]) + toes([[244, 270], [266, 268], [288, 266], [306, 266]])
    + shape(sm('228,264 320,262 320,290 228,290'), SKIN.deep, 0.35)) + claws([[240, 288], [260, 289], [282, 288], [302, 285], [318, 280]]) },
  // la carapace et ses pics (la forme exacte de l'original), la bande brune du bord, les plaques
  { id: 'shell', cls: 'a-shell', d: SHELL, shadow: [sh(['lower', 'belly', 'legB', 'front'], -4, 6, SH.dark, 0.5)], body: use('shell', 'url(#g-shell)') + clip('shell',
    // les plaques : de grandes facettes, chacune un côté éclairé et un côté sombre (pas de rayures)
    [[120, 150, 210, 140], [200, 150, 300, 138], [150, 112, 260, 100], [90, 170, 180, 168]].map(([x0, y0, x1, y1]) => glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2 - 3, 3], [x1, y1, 0]], SHL.deep, 0.5)
      + glint([[x0, y0 - 4, 0], [(x0 + x1) / 2, (y0 + y1) / 2 - 7, 2], [x1, y1 - 4, 0]], SHL.hi, 0.35)).join('')
    + oval(220, 110, 90, 34, 'url(#g-shellLite)', 1, -6) + shape(sm('40,190 100,160 180,150 260,150 320,140 320,200 40,206'), SHL.deep, 0.35)
    + SPIKES.map(spikeFace).join('')
    // la bande brune du bord, qui suit le bas de la carapace, et son reflet
    + shape(sm('40,200 70,186 120,176 180,172 240,172 300,170 320,160 318,190 300,198 200,200 120,202 60,206'), RIM.base)
    + glint([[60, 190, 0], [140, 178, 3], [240, 176, 3], [310, 168, 0]], RIM.lite, 0.9)
    + glint([[60, 204, 4], [180, 200, 5], [300, 198, 4]], RIM.shade, 0.8)) },
  // la tête
  { id: 'head', cls: 'a-head', d: HEAD, shadow: [sh(['shell', 'front', 'lower', 'belly'], -3, 6, SH.dark, 0.45)], body: headBody },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : elle souffle (la carapace se soulève), la tête avance et recule un peu, la gueule s'ouvre et se ferme, elle
// cligne ; les pattes restent plantées.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : elle rentre un peu la tête (élan), puis la projette en avant et mord
// (la mâchoire claque), la carapace bascule ; tout revient à la pose de repos.
const G = [200, 288];
const PIV = { root: G, body: [200, 240], shell: [200, 200], head: [320, 190], jaw: [326, 204], legB: [120, 220], legF: [260, 220] };
const IDLE = {
  'a-shell': ['shell', 'shell 1.6s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 2.2s ease-in-out infinite alternate'],
  'a-jaw': ['jaw', 'jaw .5s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('')
  + ['root', 'body', 'legB', 'legF'].map((k) => `.a-${k}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px}`).join('') + `
.a-mouth{transform-origin:380px 190px;animation:mouth .5s ease-in-out infinite alternate}
.a-blink{animation:blink 4.4s linear infinite}
@keyframes shell{from{transform:none}to{transform:translate(0,-2px) scale(1.005,1.01)}}
@keyframes head{from{transform:none}to{transform:translate(2px,-1px) rotate(-1.5deg)}}
@keyframes jaw{from{transform:none}to{transform:translate(0,2px) rotate(2deg)}}
@keyframes mouth{from{transform:scale(1,.9)}to{transform:scale(1,1.1)}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-head', 'head-atk')}${atk('a-jaw', 'jaw-atk')}${atk('a-shell', 'shell-atk')}
@keyframes root-atk{0%{transform:none}28%{transform:translate(-6px,1px)}46%{transform:translate(18px,-3px)}60%{transform:translate(14px,0)}80%{transform:translate(3px,0)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}28%{transform:translate(-14px,4px) rotate(-6deg)}46%{transform:translate(12px,0) rotate(6deg)}60%{transform:translate(8px,0) rotate(3deg)}100%{transform:none}}
@keyframes jaw-atk{0%{transform:none}28%{transform:translate(0,6px) rotate(10deg)}44%{transform:translate(0,7px) rotate(12deg)}52%{transform:rotate(-3deg)}100%{transform:none}}
@keyframes shell-atk{0%{transform:none}28%{transform:rotate(-2deg)}46%{transform:rotate(2deg)}100%{transform:none}}
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
  let s = figure({ master: require('./silhouettes/bayou-2.json'), w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'bayou-2', w: W, h: H, pad: PAD, foot: G, svg };
