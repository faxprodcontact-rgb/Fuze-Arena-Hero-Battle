// Le croco cuirassé (bayou-6), monstre du Bayou : redessiné par le code d'après le dessin d'origine, dans le même cadre
// (456 × 246, mêmes proportions, même pose) : un gros crocodile vert trapu tourné vers la droite ; dos couvert de
// plaques bombées et hérissé de grands pics, queue relevée à gauche ; tête plate, œil orange furieux sous une arcade
// épaisse, gueule grande ouverte aux crocs blancs, langue rouge, mâchoire du bas claire ; ventre jaune ; quatre pattes
// trapues aux griffes sombres.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. Contour décalqué sur l'original
// (outils/contour.py).
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 456, H = 246, PAD = 40;

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
const GREEN = { hi: '#b4e88a', lite: '#7cc05a', base: '#4e9440', mid: '#3c7a36', shade: '#28582a', deep: '#163a1c' };
const BELLY = { hi: '#fff0a0', base: '#d8b444', shade: '#9a7a24' };
const JAW = { hi: '#e8f6c0', base: '#a8cc7a', shade: '#6a8a4a' };
const SH = { green: '#0a200c', dark: '#1a0a08' };

// ---------- dégradés ----------
const defs = [
  lin('g-body', 300, 30, 120, 220, [[0, GREEN.lite], [0.45, GREEN.base], [1, GREEN.shade]]),
  lin('g-far', 0, 0, 0, 1, [[0, GREEN.mid], [1, GREEN.deep]], false),
  lin('g-leg', 0, 0, 1, 0, [[0, GREEN.shade], [0.6, GREEN.base], [1, GREEN.lite]], false),
  lin('g-head', 420, 10, 300, 120, [[0, '#94d06a'], [0.5, GREEN.base], [1, GREEN.mid]]),
  lin('g-jaw', 0, 0, 0, 1, [[0, JAW.hi], [0.5, JAW.base], [1, JAW.shade]], false),
  lin('g-spike', 0, 0, 1, 0, [[0, GREEN.deep], [0.45, GREEN.mid], [0.8, GREEN.lite], [1, GREEN.base]], false),
  lin('g-belly', 0, 0, 0, 1, [[0, BELLY.hi], [0.5, BELLY.base], [1, BELLY.shade]], false),
  rad('g-eye', 0.4, 0.4, 0.75, [[0, '#fff4c0'], [0.45, '#ffb030'], [1, '#c8500c']], false),
  lin('g-mouth', 0, 60, 0, 170, [[0, '#2a060c'], [0.5, '#5a1420'], [1, '#8a2834']]),
  lin('g-claw', 0, 0, 0, 1, [[0, '#7a6a6a'], [0.5, '#3a2a2a'], [1, '#1a1010']], false),
].join('');

// ---------- le visage ----------
/** Une dent pointue : la moitié du fond dans l'ombre, un filet de lumière sur l'autre flanc. b1, b2 = la racine, t = la pointe. */
function tooth([x1, y1], [x2, y2], [tx, ty]) {
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  const d = `M${x1} ${y1}Q${n((x1 + tx) / 2 - (ty - y1) * 0.08)} ${n((y1 + ty) / 2)} ${tx} ${ty}Q${n((x2 + tx) / 2 + (ty - y2) * 0.08)} ${n((y2 + ty) / 2)} ${x2} ${y2}Z`;
  const half = `M${x1} ${y1}L${tx} ${ty}L${n(mx)} ${n(my)}Z`;
  return shape(d, '#fbf4e8') + shape(half, '#d8c8bc', 0.8) + line(`M${n(mx + (x2 - mx) * 0.5)} ${n(my + (y2 - my) * 0.5)}L${n(tx + (x2 - tx) * 0.2)} ${n(ty + (y2 - ty) * 0.2)}`, '#ffffff', 1.2, 0.9);
}
// les crocs du haut, le long du bord de la mâchoire du haut (de l'œil vers le bout du museau) : [racine 1, racine 2, pointe]
const upAt = (x) => 98 - (x - 298) * 0.33, lowAt = (x) => 104 + (x - 292) * 0.36;
const TEETH_T = [306, 322, 338, 354, 370, 386, 402, 418, 432].map((x, i) => [[x - 6, n(upAt(x - 6) - 2)], [x + 6, n(upAt(x + 6) - 2)], [x - 1, n(upAt(x) + 14 + (i % 2 ? 0 : 5))]]);
const TEETH_B = [306, 321, 336, 351, 366, 381, 396, 410].map((x, i) => [[x - 6, n(lowAt(x - 6) + 2)], [x + 6, n(lowAt(x + 6) + 2)], [x - 1, n(lowAt(x) - 14 - (i % 2 ? 0 : 5))]]);
/** Le tracé d'une dent (sa silhouette). */
const toothD = ([x1, y1], [x2, y2], [tx, ty]) => `M${x1} ${y1}Q${n((x1 + tx) / 2 - (ty - y1) * 0.08)} ${n((y1 + ty) / 2)} ${tx} ${ty}Q${n((x2 + tx) / 2 + (ty - y2) * 0.08)} ${n((y2 + ty) / 2)} ${x2} ${y2}Z`;

// ---------- le visage (suite) ----------
// ---------- silhouettes (le bord extérieur suit le contour mesuré sur l'original) ----------
// les pics du dos : [base gauche x, base droite x, pointe x, pointe y], la base est posée sur le dos
const SPIKES = [[44, 66, 51, 22], [110, 134, 119, 58], [138, 164, 151, 40], [176, 204, 189, 33], [212, 238, 227, 38]];
const S = {
  // les pattes du fond
  legBF: sm('70,180 100,176 104,200 102,222 96,230! 70,230 70,204'),
  legFF: sm('276,180 302,178 306,200 304,224 300,232! 270,232 272,204'),
  // la queue, relevée en arc à gauche
  tail: sm('100,160 80,150 54,140 34,120 22,100 14,80 18,56 28,40 32,22 51,22! 56,33 61,33 58,60 58,78 64,96 76,110 94,118 118,124'),
  // les pics du dos (derrière le dos)
  spikes: SPIKES.map(([a, b, tx, ty]) => sm(`${a},${ty + 50} ${tx},${ty}! ${b},${ty + 50}`)).join(''),
  // le corps : le dos bombé, le ventre jaune entre les pattes
  body: sm('64,110 90,90 130,74 180,64 230,58 270,48 300,52 312,90 316,130 312,160 300,178 260,196 220,200 180,198 140,196 100,190 74,182 56,170 44,150 46,128'),
  // les pattes de devant (de ce côté)
  legBN: sm('104,170 150,170 168,196 166,215 168,221 162,221 159,223 146,222 143,225 143,231! 130,230 117,233 114,231 108,231 104,234 99,231 92,231 88,233 85,230 68,230! 69,221 66,218 69,213 70,204 74,198 88,184'),
  legFN: sm('196,168 240,168 262,190 282,210 285,225 282,228 282,234! 264,236 261,234 254,234 252,236 244,235 240,237 234,234 227,234 223,236 220,233 199,232! 199,223 196,220 199,214 199,208 195,200 192,186'),
  // la gueule ouverte en coin : le fond rouge (au bout, on voit le décor entre les deux mâchoires), la mâchoire du bas
  // qui descend en biais, la tête et la mâchoire du haut
  mouth: sm('290,100 320,88 350,78 380,70 406,62 410,88 404,120 398,136 370,124 330,114 300,106'),
  jaw: sm('292,104 330,114 360,122 390,130 414,142 423,152 423,159 420,168 416,173 406,180 384,181 373,179 361,173 347,169 318,164 307,164 301,167 295,173 286,166 282,140 284,118'),
  head: sm('266,31 279,29 282,26 283,20 289,14 298,15 304,10 314,10 322,15 334,16 343,21 349,28 359,28 363,26 370,26 374,24 403,19 409,11 417,7 420,7 428,12 438,12! 440,24 438,40 439,52! '
    + '410,60 380,70 350,80 320,90 298,98 284,110 270,100 262,80 260,50'),
  // les crocs (avec leur contour) : ceux du haut pendent sous la mâchoire du haut, ceux du bas se dressent sur la mâchoire du bas
  teethT: TEETH_T.map((t) => toothD(...t)).join(''),
  teethB: TEETH_B.map((t) => toothD(...t)).join(''),
};

const EYE = { x: 308, y: 50, r: 14 };
function eye() {
  const { x, y, r } = EYE;
  return oval(x, y + 0.4, r + 2.6, r + 2.4, '#1a0a08')
    + `<clipPath id="c-eye"><circle cx="${x}" cy="${y}" r="${r}"/></clipPath>` + dot(x, y, r, 'url(#g-eye)')
    + `<g clip-path="url(#c-eye)">` + oval(x + 3, y + 1, 4, 9, '#1a0806')
    + `<rect x="${x - r - 4}" y="${y - r - 4}" width="${2 * r + 8}" height="${n(r * 1.1)}" fill="#1a0a08" opacity="0.45" transform="rotate(18 ${x} ${y})"/>`
    + dot(x - 3, y - 3, 2.6, '#fff') + dot(x + 6, y + 6, 1.2, '#fff', 0.9) + '</g>'
    + `<g class="a-blink" opacity="0"><circle cx="${x}" cy="${y}" r="${r + 1}" fill="${GREEN.base}"/>${line(`M${x - r} ${y + 2} Q${x} ${y + 8} ${x + r} ${y + 1}`, '#1a0a08', 2.4)}</g>`
    // l'arcade épaisse au-dessus de l'œil, qui plonge vers le museau (regard furieux)
    + shape(sm('286,34 302,26 320,30 334,42 330,48 314,40 296,40'), SH.green, 0.4).replace('<path', '<path transform="translate(-2 3)"')
    + shape(sm('286,34 302,26 320,30 334,42 330,48 314,40 296,40'), GREEN.mid)
    + glint([[290, 30, 0], [308, 27, 2.6], [326, 36, 0]], GREEN.hi, 0.8);
}
const headBody = use('head', 'url(#g-head)') + clip('head',
  // le dessus du museau éclairé, deux bosses le long du crâne, la narine au bout ; le bord de la mâchoire à l'ombre
  glint([[300, 18, 0], [350, 24, 4], [404, 18, 3], [432, 14, 0]], GREEN.hi, 0.7)
  + oval(418, 20, 6, 4, GREEN.deep, 0.8) + oval(420, 18, 2.4, 1.6, GREEN.hi, 0.6)
  + glint([[300, 92, 4], [350, 76, 5], [400, 60, 4], [436, 48, 3]], GREEN.shade, 0.7)
  + shape(sm('262,80 276,100 290,110 270,112'), GREEN.shade, 0.6)
  + eye()
);

// ---------- les pattes ----------
/** Une patte : la peau en écailles (des bosses), l'ombre derrière, des griffes sombres au bout des doigts. */
function legBody(id, fill, shadeD, toes, claws) {
  return use(id, fill) + clip(id, shape(shadeD, SH.green, 0.35)
    + toes.map(([x, y]) => glint([[x, y, 0], [x, y + 8, 2.4], [x, y + 14, 0]], GREEN.deep, 0.6)).join(''))
    + claws.map(([x, y]) => `<path d="M${x - 3} ${y - 6} Q${x + 1} ${y} ${x + 3} ${y + 4} Q${x + 4} ${y - 3} ${x + 3} ${y - 8} Z" fill="url(#g-claw)"/>`).join('');
}

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'legBF', cls: 'a-legB', d: S.legBF, body: legBody('legBF', 'url(#g-far)', sm('70,180 82,200 82,232 70,232'), [], [[86, 228], [96, 228]]) },
  { id: 'legFF', cls: 'a-legF', d: S.legFF, body: legBody('legFF', 'url(#g-far)', sm('272,180 284,200 284,234 270,234'), [], [[294, 228], [304, 226]]) },
  { id: 'tail', cls: 'a-tail', d: S.tail, body: use('tail', 'url(#g-body)') + clip('tail',
    // les plaques de la queue : des bosses éclairées en haut à droite, le dessous à l'ombre
    [[50, 40], [46, 62], [48, 84], [60, 104], [80, 118]].map(([x, y]) => oval(x + 2, y - 2, 9, 7, GREEN.lite, 0.5) + oval(x - 2, y + 4, 9, 4, GREEN.shade, 0.5)).join('')
    + shape(sm('16,70 24,100 40,126 60,142 90,156 100,170 60,170 20,140'), GREEN.shade, 0.6)) },
  { id: 'spikes', cls: 'a-body', d: S.spikes, body: use('spikes', GREEN.mid) + clip('spikes',
    SPIKES.map(([a, b, tx, ty]) => shape(`M${a} ${ty + 50} L${tx} ${ty} L${b} ${ty + 50} Z`, 'url(#g-spike)') + glint([[tx + 1, ty + 4, 0], [n((tx + b) / 2), n(ty + 24), 2.4], [b - 2, ty + 46, 0]], GREEN.hi, 0.7)).join('')) },
  { id: 'body', cls: 'a-body', d: S.body, shadow: [sh(['legBF', 'legFF', 'tail', 'spikes'], -4, 5, SH.green, 0.45)], body: use('body', 'url(#g-body)') + clip('body',
    // la cuirasse : des bandes de plaques le long du dos, séparées par des rainures (un côté sombre, une arête claire),
    // coupées en travers ; une lumière sur le haut de chaque bande
    [[[60, 128], [110, 106], [170, 92], [230, 84], [290, 76]], [[56, 154], [110, 140], [170, 130], [230, 122], [300, 112]]].map((L) =>
      glint(L.map(([x, y], i) => [x, y, i === 0 || i === L.length - 1 ? 0 : 4]), GREEN.deep, 0.65) + glint(L.map(([x, y], i) => [x + 1, y + 3, i === 0 || i === L.length - 1 ? 0 : 2]), GREEN.lite, 0.6)).join('')
    + [[120, 80, 116, 108], [176, 70, 172, 94], [232, 62, 230, 86], [126, 110, 122, 140], [184, 98, 180, 130], [240, 90, 238, 122]].map(([x0, y0, x1, y1]) =>
      glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 3.4], [x1, y1, 0]], GREEN.deep, 0.55)).join('')
    + [[[80, 104], [140, 86], [200, 74], [260, 66]], [[80, 134], [150, 118], [210, 108], [270, 98]], [[90, 166], [150, 154], [220, 146], [290, 136]]].map((L) =>
      glint(L.map(([x, y], i) => [x, y, i === 0 || i === L.length - 1 ? 0 : 5]), GREEN.hi, 0.35)).join('')
    + shape(sm('110,178 160,172 220,170 270,168 310,150 316,170 300,200 110,200'), 'url(#g-belly)')
    + [[150, 180], [190, 178], [230, 176], [270, 172]].map(([x, y]) => glint([[x - 10, y, 0], [x, y + 2, 2.4], [x + 10, y, 0]], BELLY.shade, 0.6)).join('')) },
  { id: 'legBN', cls: 'a-legB', d: S.legBN, shadow: [sh(['body', 'legBF'], -4, 5, SH.green, 0.45)], body: legBody('legBN', 'url(#g-leg)', sm('68,190 84,206 92,234 66,234'),
    [[100, 210], [118, 212], [136, 212]], [[92, 230], [110, 232], [128, 232], [144, 230]]) },
  { id: 'legFN', cls: 'a-legF', d: S.legFN, shadow: [sh(['body', 'legFF'], -4, 5, SH.green, 0.45)], body: use('legFN', 'url(#g-leg)') + clip('legFN',
    // la grosse cuisse jaunâtre éclairée, les doigts
    oval(226, 190, 22, 14, BELLY.base, 0.5, -20) + oval(234, 184, 10, 6, BELLY.hi, 0.5, -20)
    + shape(sm('196,190 210,210 214,236 196,236'), SH.green, 0.35)
    + [[226, 214], [244, 216], [262, 214]].map(([x, y]) => glint([[x, y, 0], [x, y + 8, 2.4], [x, y + 14, 0]], GREEN.deep, 0.6)).join(''))
    + [[218, 230], [236, 232], [254, 232], [272, 230]].map(([x, y]) => `<path d="M${x - 3} ${y - 6} Q${x + 1} ${y} ${x + 3} ${y + 4} Q${x + 4} ${y - 3} ${x + 3} ${y - 8} Z" fill="url(#g-claw)"/>`).join('') },
  { id: 'mouth', cls: 'a-head', d: S.mouth, body: use('mouth', 'url(#g-mouth)') + clip('mouth',
    shape('M300 106 C320 94 352 92 380 104 C390 112 386 124 372 126 L300 112 Z', '#d85a68') + glint([[310, 102, 0], [330, 100, 2.4], [350, 104, 0]], '#f8a6ae', 0.8)) },
  { id: 'jaw', cls: 'a-jaw', d: S.jaw, shadow: [sh(['body', 'legFN', 'legFF'], -3, 5, SH.green, 0.4)], body: use('jaw', 'url(#g-jaw)') + clip('jaw',
    // le dessus de la mâchoire éclairé, le dessous à l'ombre, un pli le long de la lèvre
    glint([[296, 110, 0], [350, 124, 3], [416, 146, 0]], JAW.hi, 0.9) + shape(sm('290,162 320,160 360,170 400,176 420,168 420,186 290,186'), JAW.shade, 0.7)
    + glint([[304, 128, 0], [356, 142, 2.4], [410, 156, 0]], JAW.shade, 0.5)) },
  { id: 'teethB', cls: 'a-jaw', d: S.teethB, body: TEETH_B.map((t) => tooth(...t)).join('') },
  { id: 'head', cls: 'a-head', d: S.head, shadow: [sh(['body', 'spikes', 'jaw', 'mouth', 'teethB'], -3, 6, SH.green, 0.45)], body: headBody },
  { id: 'teethT', cls: 'a-head', d: S.teethT, body: TEETH_T.map((t) => tooth(...t)).join('') },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : il souffle (le corps se soulève), la queue balance, la tête hoche, la mâchoire tremble, il cligne.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : il se ramasse en arrière, se jette en avant et referme ses mâchoires d'un
// coup sec (la gueule s'ouvre en grand puis claque), la queue fouette ; puis il revient exactement à sa place.
const G = [200, 232];
const PIV = { root: G, body: [190, 200], head: [290, 130], jaw: [292, 120], tail: [100, 150], legB: [110, 180], legF: [230, 180] };
const IDLE = {
  'a-body': ['body', 'body 1.5s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 2.6s ease-in-out infinite alternate'],
  'a-jaw': ['jaw', 'jaw .5s ease-in-out infinite alternate'],
  'a-tail': ['tail', 'tail 2.2s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('')
  + ['root', 'legB', 'legF'].map((k) => `.a-${k}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px}`).join('') + `
.a-blink{animation:blink 4.4s linear infinite}
@keyframes body{from{transform:none}to{transform:translate(0,-2px) scale(1.004,1.012)}}
@keyframes head{from{transform:none}to{transform:rotate(-1.4deg)}}
@keyframes jaw{from{transform:none}to{transform:rotate(2.4deg)}}
@keyframes tail{from{transform:rotate(-2deg)}to{transform:rotate(3deg)}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-body', 'body-atk')}${atk('a-head', 'head-atk')}${atk('a-jaw', 'jaw-atk')}${atk('a-tail', 'tail-atk')}
${atk('a-legB', 'legB-atk')}${atk('a-legF', 'legF-atk')}
@keyframes root-atk{0%{transform:none}28%{transform:translate(-8px,2px)}46%{transform:translate(26px,-4px)}60%{transform:translate(22px,0)}80%{transform:translate(4px,0)}100%{transform:none}}
@keyframes body-atk{0%{transform:none}28%{transform:scale(0.98,0.96)}46%{transform:scale(1.03,0.99)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}28%{transform:rotate(-8deg)}44%{transform:rotate(-10deg)}52%{transform:rotate(4deg)}62%{transform:rotate(3deg)}100%{transform:none}}
@keyframes jaw-atk{0%{transform:none}28%{transform:rotate(10deg)}44%{transform:rotate(12deg)}52%{transform:rotate(-14deg)}62%{transform:rotate(-12deg)}100%{transform:none}}
@keyframes tail-atk{0%{transform:none}28%{transform:rotate(6deg)}46%{transform:rotate(-10deg)}62%{transform:rotate(-5deg)}100%{transform:none}}
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
  let s = figure({ w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  // la tête emporte la mâchoire ; le corps emporte la tête et la queue
  s = nest(s, 'a-jaw', 'a-head');
  for (const c of ['a-head', 'a-tail']) s = nest(s, c, 'a-body');
  // tout le crocodile se jette en avant pendant l'attaque
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'bayou-6', w: W, h: H, pad: PAD, foot: G, svg };
