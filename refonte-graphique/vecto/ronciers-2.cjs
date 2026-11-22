// Le blaireau moussu (ronciers-2), monstre des Ronciers : redessiné par le code d'après le dessin d'origine, dans le
// même cadre (394 × 294, mêmes proportions, même pose) : un gros blaireau brun tourné vers la droite, le dos couvert
// d'une couverture de mousse verte d'où poussent deux champignons rouges à pois blancs ; tête rayée (bande crème,
// masque sombre), petites oreilles rondes, œil jaune-vert furieux, gueule ouverte aux crocs, truffe noire ; quatre
// pattes trapues aux griffes claires.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. Contour décalqué sur l'original
// (outils/contour.py).
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 394, H = 294, PAD = 40;

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
const FUR = { hi: '#b08a68', lite: '#8a6448', base: '#6a4836', mid: '#54382c', shade: '#3a2620', deep: '#1e1214' };
const MOSS = { hi: '#e8ff8a', lite: '#b8e04a', base: '#8ec034', shade: '#5a8a22', deep: '#34561a' };
const CREAM = { hi: '#fffaf0', base: '#f0e6d0', shade: '#c8b8a0' };
const MUSH = { hi: '#ff8a6a', base: '#d83a22', shade: '#9a1e14', stem: '#e8d6bc', stemSh: '#a8906e' };
const SH = { fur: '#120808', moss: '#1a2a08' };

// ---------- dégradés ----------
const defs = [
  lin('g-fur', 260, 90, 80, 280, [[0, FUR.lite], [0.45, FUR.base], [1, FUR.shade]]),
  lin('g-furFar', 0, 0, 0, 1, [[0, FUR.mid], [1, FUR.deep]], false),
  lin('g-leg', 0, 0, 1, 0, [[0, FUR.shade], [0.6, FUR.base], [1, FUR.lite]], false),
  lin('g-moss', 240, 70, 40, 180, [[0, MOSS.lite], [0.45, MOSS.base], [1, MOSS.shade]]),
  lin('g-head', 340, 110, 240, 210, [[0, '#8a6448'], [0.5, '#644632'], [1, '#3e2a22']]),
  lin('g-cap', 0, 0, 0, 1, [[0, MUSH.hi], [0.45, MUSH.base], [1, MUSH.shade]], false),
  lin('g-stem', 0, 0, 1, 0, [[0, MUSH.stemSh], [0.6, MUSH.stem], [1, '#fff6e6']], false),
  lin('g-cream', 0, 0, 0, 1, [[0, CREAM.hi], [0.6, CREAM.base], [1, CREAM.shade]], false),
  rad('g-eye', 0.45, 0.4, 0.75, [[0, '#ffffe0'], [0.45, '#e8f26a'], [1, '#8aa21a']], false),
  lin('g-mouth', 0, 186, 0, 232, [[0, '#2a060c'], [0.55, '#5a1420'], [1, '#8a2834']]),
  rad('g-nose', 0.6, 0.3, 0.8, [[0, '#6a6070'], [0.4, '#2a2430'], [1, '#0c080e']], false),
  lin('g-claw', 0, 0, 0, 1, [[0, '#ffffff'], [0.5, '#e4e2ea'], [1, '#9a98a8']], false),
].join('');

// ---------- silhouettes (le bord extérieur suit le contour mesuré sur l'original) ----------
const S = {
  // les pattes du fond, plus sombres
  legBF: sm('100,232 130,232 132,256 126,268 125,275! 108,277 104,262'),
  legFF: sm('232,226 262,228 262,250 261,264 266,278! 237,278 236,256'),
  // le corps : un gros dos rond, le ventre entre les pattes
  body: sm('20,150 40,120 70,100 130,80 200,74 250,82 290,100 300,130 310,170 300,210 285,220 268,222 256,232 252,250 240,262 200,268 168,264 140,250 126,256 110,262 92,262 60,260 30,258 14,236 12,200'),
  // les pattes de devant (de ce côté)
  legBN: sm('18,214 74,220 96,240 92,262 92,276! 78,282 29,280! 26,268 18,250'),
  legFN: sm('158,224 214,224 238,244 236,262 234,284! 198,286 169,282! 168,264 160,246'),
  // la couverture de mousse sur le dos, son bord du bas effiloché
  moss: sm('14,172 20,150! 22,138 34,134! 40,122 52,116! 56,104 70,100! 76,90 92,88! 100,80 116,80! 124,72 140,74! 148,66 160,70! 176,64 186,70! 200,64 208,72! 222,68 230,76! 244,74 250,84! 262,90 262,104! 254,120 240,140 228,152! 220,144 210,160! 198,150 186,168! 172,156 158,172! 146,160 130,178! 118,166 102,182! 90,168 74,186! 62,172 46,186! 36,172 24,184!'),
  // les deux champignons : les pieds, puis les chapeaux
  stemS: sm('88,62 100,62 102,82 96,92 88,90'),
  stemB: sm('155,40 171,40 173,70 166,82 156,82 153,66'),
  capS: sm('68,62 74,47 81,41 90,37 100,37 108,39 118,46 122,56 112,66 96,70 79,72 70,68'),
  capB: sm('139,34 139,24 148,13 163,7 176,9 188,16 195,30 194,36 182,43 160,45 146,41'),
  // la tête : les oreilles rondes, la gueule (dedans), la mâchoire du bas, la tête
  earF: sm('228,78 246,80 260,86 264,104 258,122 242,126 230,116 226,96'),
  earN: sm('292,92 298,84 308,80 318,88 322,104 318,116 304,118 294,108'),
  mouth: sm('282,182 342,188 354,198 346,212 332,226 304,230 286,222 278,204'),
  jaw: sm('274,210 300,216 324,220 338,214 340,226 330,232 304,236 282,230 270,222'),
  head: sm('228,116 246,104 270,98 296,96 320,106 336,122 356,140 362,154 376,166 388,180 386,192 376,200 360,198 346,196 334,190 312,186 290,184 278,196 270,212 258,206 246,194 236,174 226,148'),
};

// ---------- le visage ----------
/** Une dent pointue : la moitié du fond dans l'ombre, un filet de lumière sur l'autre flanc. b1, b2 = la racine, t = la pointe. */
function tooth([x1, y1], [x2, y2], [tx, ty]) {
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  const d = `M${x1} ${y1}Q${n((x1 + tx) / 2 - (ty - y1) * 0.08)} ${n((y1 + ty) / 2)} ${tx} ${ty}Q${n((x2 + tx) / 2 + (ty - y2) * 0.08)} ${n((y2 + ty) / 2)} ${x2} ${y2}Z`;
  const half = `M${x1} ${y1}L${tx} ${ty}L${n(mx)} ${n(my)}Z`;
  return shape(d, '#fbf4e8') + shape(half, '#d8c8bc', 0.8) + line(`M${n(mx + (x2 - mx) * 0.5)} ${n(my + (y2 - my) * 0.5)}L${n(tx + (x2 - tx) * 0.2)} ${n(ty + (y2 - ty) * 0.2)}`, '#ffffff', 1.2, 0.9);
}
const TEETH_T = [[[294, 185], [302, 186], [298, 196]], [[306, 186], [317, 187], [312, 203]], [[322, 188], [330, 189], [326, 198]], [[334, 190], [344, 192], [340, 203]]];
const TEETH_B = [[[290, 222], [298, 224], [294, 213]], [[304, 226], [314, 226], [310, 211]], [[320, 224], [328, 222], [324, 213]]];

const EYE = { x: 298, y: 158, r: 10 };
function eye() {
  const { x, y, r } = EYE;
  return oval(x, y + 0.4, r + 2.6, r + 2.2, '#140a08')
    + `<clipPath id="c-eye"><circle cx="${x}" cy="${y}" r="${r}"/></clipPath>` + dot(x, y, r, 'url(#g-eye)')
    + `<g clip-path="url(#c-eye)">` + oval(x + 2, y + 1, 4, 5.4, '#120806')
    + `<rect x="${x - r - 4}" y="${y - r - 4}" width="${2 * r + 8}" height="${n(r * 1.05)}" fill="#140a08" opacity="0.55" transform="rotate(14 ${x} ${y})"/>`
    + dot(x - 2.5, y - 3, 2.2, '#fff') + dot(x + 5, y + 4, 1, '#fff', 0.9) + '</g>'
    + `<g class="a-blink" opacity="0"><circle cx="${x}" cy="${y}" r="${r + 1}" fill="${FUR.base}"/>${line(`M${x - r} ${y + 2} Q${x} ${y + 7} ${x + r} ${y + 1}`, '#140a08', 2.4)}</g>`;
}
const headBody = use('head', 'url(#g-head)') + clip('head',
  // la bande crème sur le front et le dessus du museau, le masque sombre qui passe par l'œil, le bas du museau crème
  shape(rib([[222, 132, 12], [250, 126, 16], [290, 128, 16], [326, 140, 15], [352, 156, 12], [372, 170, 8]]), 'url(#g-cream)')
  + shape(rib([[240, 150, 14], [268, 148, 18], [300, 156, 20], [334, 166, 16], [360, 176, 10], [378, 182, 4]]), FUR.deep, 0.92)
  + shape(sm('286,182 312,178 340,178 366,180 384,186 378,198 358,198 334,194 300,190'), 'url(#g-cream)')
  // la joue en touffes (sous l'œil, vers l'arrière)
  + shape(sm('240,176 256,170 270,178 268,196! 260,186 252,200! 246,186'), FUR.lite, 0.8)
  + glint([[256, 104, 0], [290, 100, 3], [320, 110, 0]], FUR.hi, 0.6)
  // la truffe noire et son reflet
  + `<path d="M366 182 C370 174 382 172 390 178 C394 184 392 194 386 198 C378 202 368 198 366 190 Z" fill="url(#g-nose)"/>` + oval(382, 178, 3.4, 2, '#c8c0d0', 0.9, -10)
  + eye()
  // le sourcil sombre, froncé
  + shape(sm('280,142 296,138 314,146 322,154 316,156 300,150 284,150'), FUR.deep)
);

// ---------- les pattes ----------
/** Une patte : la fourrure, l'ombre derrière, des touffes au-dessus du pied, des griffes claires. */
function legBody(id, fill, shadeD, claws) {
  return use(id, fill) + clip(id, shape(shadeD, SH.fur, 0.35))
    + claws.map(([x, y]) => `<path d="M${x - 3} ${y - 6} Q${x + 2} ${y} ${x + 5} ${y + 3} Q${x + 3} ${y - 4} ${x + 3} ${y - 8} Z" fill="url(#g-claw)"/>`).join('');
}

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'legBF', cls: 'a-legB', d: S.legBF, body: legBody('legBF', 'url(#g-furFar)', sm('100,232 112,250 110,278 98,278'), [[118, 272], [126, 270]]) },
  { id: 'legFF', cls: 'a-legF', d: S.legFF, body: legBody('legFF', 'url(#g-furFar)', sm('232,226 244,250 244,280 232,280'), [[252, 274], [260, 274]]) },
  { id: 'body', cls: 'a-body', d: S.body, shadow: [sh(['legBF', 'legFF'], -4, 5, SH.fur, 0.45)], body: use('body', 'url(#g-fur)') + clip('body',
    // le flanc éclairé à droite, le ventre à l'ombre ; quelques touffes de poils (creux sombre + pointe claire)
    oval(260, 170, 30, 40, FUR.hi, 0.35, -10)
    + shape(sm('20,230 60,250 120,256 170,258 220,258 260,240 300,214 300,280 20,280'), FUR.shade, 0.55)
    + [[60, 210], [110, 220], [170, 210], [220, 200], [264, 190]].map(([x, y]) => glint([[x, y - 14, 0], [x - 3, y, 3], [x - 8, y + 12, 0]], FUR.deep, 0.5)
      + glint([[x + 4, y - 14, 0], [x + 1, y, 2], [x - 4, y + 12, 0]], FUR.hi, 0.4)).join('')) },
  { id: 'legBN', cls: 'a-legB', d: S.legBN, shadow: [sh(['body', 'legBF'], -4, 5, SH.fur, 0.45)], body: legBody('legBN', 'url(#g-leg)', sm('18,214 40,236 46,262 40,282 18,282'),
    [[40, 278], [56, 279], [72, 278], [86, 274]]) },
  { id: 'legFN', cls: 'a-legF', d: S.legFN, shadow: [sh(['body', 'legFF'], -4, 5, SH.fur, 0.45)], body: legBody('legFN', 'url(#g-leg)', sm('158,224 178,244 184,268 180,288 158,288'),
    [[180, 280], [196, 282], [212, 282], [226, 280]]) },
  { id: 'moss', cls: 'a-moss', d: S.moss, shadow: [sh(['body'], -4, 6, SH.moss, 0.45)], body: use('moss', 'url(#g-moss)') + clip('moss',
    // la mousse : l'ombre du bas, une grande lumière sur le dessus, quelques touffes en fuseaux qui partent dans tous
    // les sens (jamais en rangées), des petits brins clairs sur le bord du haut
    shape(sm('14,176 40,150 90,146 150,140 210,128 250,118 246,150 228,160 14,190'), MOSS.shade, 0.6)
    + shape(sm('60,104 110,86 170,76 230,80 252,96 220,104 160,108 100,118 54,128'), MOSS.lite, 0.65)
    + [[80, 130, 66, 150, 5], [130, 120, 120, 146, 6], [184, 110, 196, 136, 5], [224, 112, 214, 138, 4], [50, 150, 40, 170, 4], [156, 140, 170, 160, 4], [104, 144, 92, 166, 5]].map(([x0, y0, x1, y1, w]) =>
      glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, w], [x1, y1, 0]], MOSS.deep, 0.55)).join('')
    + [[96, 92, 104, 82], [150, 76, 158, 68], [204, 74, 210, 66], [44, 124, 50, 116]].map(([x0, y0, x1, y1]) => glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 2.4], [x1, y1, 0]], MOSS.hi, 0.85)).join('')) },
  { id: 'stemS', cls: 'a-mushS', d: S.stemS, shadow: [sh(['moss'], -3, 4, SH.moss, 0.45)], body: use('stemS', 'url(#g-stem)') },
  { id: 'capS', cls: 'a-mushS', d: S.capS, shadow: [sh(['stemS', 'moss'], -3, 5, SH.fur, 0.4)], body: use('capS', 'url(#g-cap)') + clip('capS',
    shape(sm('70,66 96,62 120,58 112,68 96,72 76,72'), '#f6dcc0') + glint([[80, 46, 0], [100, 40, 3], [116, 48, 0]], MUSH.hi, 0.8)
    + dot(86, 50, 3.4, '#fff8ee') + dot(102, 46, 2.6, '#fff8ee') + dot(112, 56, 2.2, '#fff8ee') + dot(78, 58, 2, '#fff8ee')) },
  { id: 'stemB', cls: 'a-mushB', d: S.stemB, shadow: [sh(['moss'], -3, 4, SH.moss, 0.45)], body: use('stemB', 'url(#g-stem)') },
  { id: 'capB', cls: 'a-mushB', d: S.capB, shadow: [sh(['stemB', 'moss'], -3, 5, SH.fur, 0.4)], body: use('capB', 'url(#g-cap)') + clip('capB',
    shape(sm('140,38 160,40 182,40 194,34 186,44 160,46 144,44'), '#f6dcc0') + glint([[150, 16, 0], [168, 10, 3], [186, 18, 0]], MUSH.hi, 0.8)
    + dot(158, 20, 4, '#fff8ee') + dot(176, 16, 3, '#fff8ee') + dot(186, 28, 2.6, '#fff8ee') + dot(150, 30, 2.4, '#fff8ee') + dot(170, 32, 2, '#fff8ee')) },
  { id: 'earF', cls: 'a-head', d: S.earF, body: use('earF', 'url(#g-head)') + clip('earF', oval(246, 104, 9, 13, FUR.deep, 0.9) + glint([[234, 84, 0], [252, 82, 2.6], [262, 96, 0]], CREAM.base, 0.8)) },
  { id: 'earN', cls: 'a-head', d: S.earN, body: use('earN', 'url(#g-head)') + clip('earN', oval(307, 102, 7, 9, FUR.deep, 0.9) + glint([[296, 88, 0], [308, 82, 2.4], [318, 92, 0]], CREAM.base, 0.8)) },
  { id: 'mouth', cls: 'a-head', d: S.mouth, body: use('mouth', 'url(#g-mouth)') + clip('mouth',
    `<g class="a-teeth">${shape('M286 220 C294 206 312 202 328 208 C334 212 334 220 328 224 L286 226 Z', '#e0707a')
    + glint([[294, 212, 0], [308, 208, 3], [322, 212, 0]], '#f8a6ae', 0.8) + TEETH_B.map((t) => tooth(...t)).join('')}</g>`
    + TEETH_T.map((t) => tooth(...t)).join('')) },
  { id: 'jaw', cls: 'a-jaw', d: S.jaw, shadow: [sh(['body'], -3, 5, SH.fur, 0.4)], body: use('jaw', 'url(#g-cream)') + clip('jaw',
    shape(sm('270,224 300,232 330,230 342,224 342,238 270,238'), CREAM.shade, 0.7)) },
  { id: 'head', cls: 'a-head', d: S.head, shadow: [sh(['earF', 'earN', 'body', 'moss', 'jaw'], -3, 6, SH.fur, 0.45)], body: headBody },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : il gronde. Le corps se soulève à chaque souffle, la tête hoche, la mâchoire tremble, les champignons
// tremblotent sur la mousse, il cligne. Les pattes restent plantées.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : il se ramasse, charge en avant la gueule grande ouverte et mord, les
// champignons ballottent ; puis il revient exactement à sa place.
const G = [150, 284];
const PIV = { root: G, body: [160, 260], head: [262, 200], jaw: [276, 214], mushS: [94, 88], mushB: [162, 80], moss: [140, 150], legB: [60, 230], legF: [200, 232] };
const IDLE = {
  'a-body': ['body', 'body 1.5s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 2.4s ease-in-out infinite alternate'],
  'a-jaw': ['jaw', 'jaw .36s ease-in-out infinite alternate'],
  'a-teeth': ['jaw', 'jaw .36s ease-in-out infinite alternate'],
  'a-mushS': ['mushS', 'mush 1.3s ease-in-out infinite alternate'],
  'a-mushB': ['mushB', 'mush 1.6s ease-in-out -.5s infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('')
  + ['root', 'legB', 'legF', 'moss'].map((k) => `.a-${k}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px}`).join('') + `
.a-blink{animation:blink 4.2s linear infinite}
@keyframes body{from{transform:none}to{transform:translate(0,-2.4px) scale(1.006,1.014)}}
@keyframes head{from{transform:none}to{transform:translate(0.6px,-1.2px) rotate(-1.6deg)}}
@keyframes jaw{from{transform:none}to{transform:rotate(1.8deg)}}
@keyframes mush{from{transform:rotate(-2.5deg)}to{transform:rotate(3deg)}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-body', 'body-atk')}${atk('a-head', 'head-atk')}${atk('a-jaw', 'jaw-atk')}${atk('a-teeth', 'jaw-atk')}
${atk('a-mushS', 'mush-atk')}${atk('a-mushB', 'mush-atk')}${atk('a-legB', 'legB-atk')}${atk('a-legF', 'legF-atk')}
@keyframes root-atk{0%{transform:none}28%{transform:translate(-8px,2px) rotate(-1.5deg)}46%{transform:translate(24px,-4px) rotate(1.5deg)}60%{transform:translate(20px,0)}80%{transform:translate(4px,0)}100%{transform:none}}
@keyframes body-atk{0%{transform:none}28%{transform:scale(0.98,0.96)}46%{transform:scale(1.03,0.99)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}28%{transform:rotate(-8deg)}46%{transform:translate(4px,3px) rotate(6deg)}60%{transform:translate(3px,2px) rotate(4deg)}82%{transform:rotate(-1deg)}100%{transform:none}}
@keyframes jaw-atk{0%{transform:none}28%{transform:rotate(14deg)}40%{transform:rotate(16deg)}50%{transform:rotate(-3deg)}62%{transform:rotate(-2deg)}100%{transform:none}}
@keyframes mush-atk{0%{transform:none}28%{transform:rotate(8deg)}46%{transform:rotate(-12deg)}64%{transform:rotate(6deg)}82%{transform:rotate(-2deg)}100%{transform:none}}
@keyframes legB-atk{0%{transform:none}28%{transform:rotate(-5deg)}46%{transform:rotate(9deg)}62%{transform:rotate(3deg)}100%{transform:none}}
@keyframes legF-atk{0%{transform:none}28%{transform:rotate(5deg)}46%{transform:rotate(-10deg)}62%{transform:rotate(-3deg)}100%{transform:none}}
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
  let s = figure({ master: require('./silhouettes/ronciers-2.json'), w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  // la tête emporte la mâchoire ; le corps emporte la tête, la mousse et les champignons
  s = nest(s, 'a-jaw', 'a-head');
  for (const c of ['a-head', 'a-moss', 'a-mushS', 'a-mushB']) s = nest(s, c, 'a-body');
  // tout le blaireau charge pendant l'attaque
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'ronciers-2', w: W, h: H, pad: PAD, foot: G, svg };
