// Le coq-girouette (epouvantails-1), monstre des Épouvantails : redessiné par le code d'après le dessin d'origine, dans
// le même cadre (361 × 398, mêmes proportions, même pose) : un coq de cuivre roux perché sur la flèche d'une girouette
// de fer ; grande queue de plumes en faucilles (grises au bout, rousses à la racine), aile repliée aux reflets bleu-vert,
// crête rouge à trois lobes, œil jaune furieux sous un sourcil gris, bec ouvert, barbillon sombre ; ses pattes serrent
// la flèche, posée sur un poteau et un socle rond.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. Contour décalqué sur l'original
// (outils/contour.py).
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 361, H = 398, PAD = 44;

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
const COP = { hi: '#ffd08a', lite: '#f6a858', base: '#e08838', mid: '#c06a2c', shade: '#8e4620', deep: '#5a2a12' };
const FEA = { hi: '#eef2f4', lite: '#c4ccd2', base: '#9aa2aa', shade: '#6a7078', deep: '#3e4248' };
const TEAL = { hi: '#a8ecdc', base: '#5ab0a0', shade: '#2e7a72' };
const RED = { hi: '#ff9070', lite: '#f05a3a', base: '#c83420', shade: '#8a1c14', deep: '#521010' };
const IRON = { hi: '#ffffff', lite: '#d4d8de', base: '#9aa0a8', mid: '#70767e', shade: '#4a4e56', deep: '#26282e' };
const SH = { cop: '#3a1808', iron: '#14161a', fea: '#20242a' };

// ---------- les plumes de la queue ----------
/**
 * Une plume en faucille : le long d'une courbe (racine r → contrôle c → pointe t), large de w au milieu, pointue au
 * bout, un peu étroite à la racine. Rend la silhouette, et la moitié du dessus (éclairée) pour le relief.
 */
function quillPts(r, c, t, w, side = 0) {
  const at = (u) => [(1 - u) * (1 - u) * r[0] + 2 * u * (1 - u) * c[0] + u * u * t[0], (1 - u) * (1 - u) * r[1] + 2 * u * (1 - u) * c[1] + u * u * t[1]];
  const U = [0, 0.15, 0.35, 0.55, 0.75, 0.9];
  const L = [], R = [];
  U.forEach((u) => {
    const a = at(Math.max(0, u - 0.02)), b = at(Math.min(1, u + 0.02));
    let dx = b[0] - a[0], dy = b[1] - a[1];
    const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
    const half = (w / 2) * (0.55 + 0.45 * Math.sin(Math.PI * Math.min(1, u * 1.2))) * (u > 0.75 ? (1 - u) / 0.25 * 0.8 + 0.2 : 1);
    const [x, y] = at(u);
    L.push(P(x - dy * half * (side === 1 ? 0 : 1), y + dx * half * (side === 1 ? 0 : 1)));
    R.push(P(x + dy * half * (side === -1 ? 0 : 1), y - dx * half * (side === -1 ? 0 : 1)));
  });
  return [...L, `${P(t[0], t[1])}!`, ...R.reverse()];
}
const quill = (q) => sm(quillPts(q.r, q.c, q.t, q.w * 1.18));
// [racine, contrôle, pointe, largeur], du fond vers le devant
const TAIL = [
  { r: [116, 118], c: [70, 104], t: [28, 70], w: 18, dark: true },
  { r: [170, 150], c: [100, 120], t: [64, 28], w: 34 },
  { r: [178, 150], c: [124, 96], t: [132, 8], w: 36 },
  { r: [160, 168], c: [70, 150], t: [9, 114], w: 36 },
  { r: [156, 186], c: [80, 190], t: [19, 188], w: 32 },
  { r: [160, 206], c: [110, 226], t: [62, 231], w: 26 },
  // les couvertures, plus courtes et rousses, posées sur la racine des grandes plumes
  { r: [182, 152], c: [146, 124], t: [118, 104], w: 30, cov: true },
  { r: [180, 172], c: [140, 158], t: [104, 150], w: 30, cov: true },
  { r: [176, 192], c: [140, 194], t: [100, 200], w: 28, cov: true },
];
function tailBody() {
  return TAIL.map((q) => {
    const d = quill(q);
    const top = sm(quillPts(q.r, q.c, q.t, q.w * 1.18, q.t[0] < q.r[0] ? 1 : -1));
    return `<path d="${d}" transform="translate(-3 4)" fill="${SH.fea}" opacity="0.35"/>`
      + shape(d, q.dark ? COP.deep : `url(#g-q${TAIL.indexOf(q)})`) + shape(top, q.dark ? COP.shade : FEA.hi, q.dark ? 0.6 : 0.4)
      + glint([[q.r[0], q.r[1], 0], [(q.r[0] + 2 * q.c[0] + q.t[0]) / 4, (q.r[1] + 2 * q.c[1] + q.t[1]) / 4, 2], [q.t[0], q.t[1], 0]], q.dark ? COP.deep : FEA.deep, 0.5);
  }).join('');
}

// ---------- dégradés ----------
const defs = [
  lin('g-body', 250, 140, 130, 260, [[0, COP.lite], [0.45, COP.base], [1, COP.shade]]),
  lin('g-head', 320, 90, 240, 170, [[0, '#ffbc6a'], [0.5, '#f09a44'], [1, '#c8702e']]),
  lin('g-comb', 0, 0, 0, 1, [[0, RED.lite], [0.5, RED.base], [1, RED.shade]], false),
  lin('g-beak', 0, 0, 0, 1, [[0, '#ffe8a0'], [0.5, '#e8c05a'], [1, '#a87a2a']], false),
  lin('g-iron', 0, 0, 0, 1, [[0, IRON.hi], [0.3, IRON.lite], [0.65, IRON.base], [1, IRON.shade]], false),
  lin('g-ironD', 0, 0, 1, 0, [[0, IRON.deep], [0.35, IRON.shade], [0.7, IRON.base], [1, IRON.mid]], false),
  lin('g-ironX', 0, 0, 1, 0, [[0, IRON.shade], [0.35, IRON.base], [0.7, IRON.hi], [1, IRON.mid]], false),
  lin('g-leg', 0, 0, 1, 0, [[0, '#7a5a2a'], [0.5, '#c8a050'], [1, '#e8c878']], false),
  rad('g-eye', 0.4, 0.4, 0.75, [[0, '#ffffd8'], [0.5, '#fff070'], [1, '#d8b018']], false),
  lin('g-mouth', 0, 0, 0, 1, [[0, '#3a0a0a'], [1, '#8a2a2a']], false),
  ...TAIL.map((q, i) => lin(`g-q${i}`, q.r[0], q.r[1], q.t[0], q.t[1], q.cov ? [[0, COP.shade], [0.5, COP.base], [1, COP.lite]] : [[0, COP.shade], [0.3, '#c0703a'], [0.6, '#a08878'], [0.85, FEA.lite], [1, FEA.hi]])),
  lin('g-wattle', 0, 0, 0, 1, [[0, '#6a2a1e'], [0.5, '#4a1c14'], [1, '#2a0e0a']], false),
].join('');

// ---------- silhouettes (le bord extérieur suit le contour mesuré sur l'original) ----------
const S = {
  tail: TAIL.map(quill).join(''),
  // les plumes du bas du ventre, sombres, qui pendent sous la queue
  under: sm('160,226 140,240 116,252 96,252 79,246! 92,242 112,236 132,228 150,220'),
  // le socle, le poteau et le raccord en croix sous la flèche
  base: sm('145,379 147,376 153,373 170,369 176,363 177,321 176,310 171,304 196,304 191,310 191,363 195,369 199,369 220,377 221,385 196,390 170,390 148,387'),
  // la flèche : l'empennage (à gauche), la tige, la pointe (à droite)
  arrow: sm('52,274! 92,275 104,288 284,289 287,286 285,266! 337,295! 283,325! 285,320 286,304 283,301 104,301 92,318! 51,318! 64,298 64,292'),
  // les pattes : de longues jambes jaunes, les doigts serrés sur la tige
  legF: sm('160,248 170,248 168,262 164,276 166,284 176,286 178,298 168,302 154,300 148,292 154,282 158,270'),
  legN: sm('198,246 210,248 210,262 214,276 222,282 228,290 224,302 210,304 200,300 198,288 204,278 200,262'),
  // le corps : un gros œuf penché, la poitrine à droite
  body: sm('156,140 190,130 224,124 248,140 256,170 254,200 246,224 230,244 208,256 186,262 160,260 136,252 118,234 114,206 124,176 140,154'),
  // l'aile repliée sur le flanc
  wing: sm('150,170 186,156 220,160 238,178 236,204 222,226 196,240 168,246! 176,236 150,240! 160,228 132,228! 146,216 124,210! 140,198'),
  // la crête rouge à trois lobes
  comb: sm('248,77 251,65 254,60 253,48 260,40! 272,40 282,48 286,54 292,50 296,40 304,26 309,23! 318,36 321,50 324,58 330,58 336,52 341,50! 343,66 341,81 336,92 325,100 300,92 270,88'),
  // le barbillon sombre sous le bec
  wattle: sm('280,156 294,152 300,166 298,182 288,188 278,178'),
  // le bec : la mâchoire du bas (ouverte) et le bec du haut, crochu
  jaw: sm('316,148 332,148 326,162 316,174 308,172 312,160'),
  mouth: sm('300,132 338,136 328,152 318,170 304,180 290,176 284,160 290,144'),
  beak: sm('310,108 328,112 344,122 357,134! 344,138 328,138 314,136 304,126'),
  // la tête et le cou
  head: sm('232,104 252,90 278,84 304,86 324,96 334,114 330,126 314,130 300,134 290,146 282,164 276,180 262,176 248,164 236,142 226,124'),
};

// ---------- le visage ----------
const EYE = { x: 296, y: 113, r: 13 };
function eye() {
  const { x, y, r } = EYE;
  return oval(x, y + 0.4, r + 2.6, r + 2.4, '#2a1408')
    + `<clipPath id="c-eye"><circle cx="${x}" cy="${y}" r="${r}"/></clipPath>` + dot(x, y, r, 'url(#g-eye)')
    + `<g clip-path="url(#c-eye)">` + oval(x + 3, y + 1, 5.6, 6.6, '#120806')
    + `<rect x="${x - r - 4}" y="${y - r - 4}" width="${2 * r + 8}" height="${n(r * 1.05)}" fill="#3a1a08" opacity="0.35" transform="rotate(16 ${x} ${y})"/>`
    + dot(x - 3, y - 4, 2.6, '#fff') + dot(x + 6, y + 5, 1.2, '#fff', 0.9) + '</g>'
    + `<g class="a-blink" opacity="0"><circle cx="${x}" cy="${y}" r="${r + 1}" fill="#e89a50"/>${line(`M${x - r} ${y + 3} Q${x} ${y + 8} ${x + r} ${y + 2}`, '#2a1408', 2.4)}</g>`
    // le sourcil : une plume grise qui plonge vers le bec
    + shape(sm('272,94 290,92 308,100 322,112 318,116 302,108 286,102 274,102'), SH.cop, 0.4).replace('<path', '<path transform="translate(-2 3)"')
    + shape(sm('272,94 290,92 308,100 322,112 318,116 302,108 286,102 274,102'), FEA.lite)
    + glint([[276, 95, 0], [298, 96, 2.2], [318, 110, 0]], '#ffffff', 0.85);
}
const headBody = use('head', 'url(#g-head)') + clip('head',
  // le cou à l'ombre (en bas à gauche), la joue claire, le dessus du crâne éclairé, quelques plumes du cou
  shape(sm('226,130 246,158 270,176 292,182 280,200 220,200'), COP.shade, 0.55)
  + glint([[250, 96, 0], [280, 88, 4], [316, 96, 0]], COP.hi, 0.7)
  + [[246, 140, 236, 156], [258, 150, 250, 168], [272, 158, 266, 176]].map(([x0, y0, x1, y1]) => glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 3], [x1, y1, 0]], COP.mid, 0.6)).join('')
  + oval(312, 128, 8, 5, '#ffd8a0', 0.5, -10)
  + eye()
);

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'base', d: S.base, body: use('base', 'url(#g-ironD)') + clip('base',
    // le socle : un disque, son dessus éclairé ; le poteau rond ; le raccord sous la flèche
    shape(sm('145,380 170,372 196,372 221,380 196,384 170,384'), IRON.base, 0.9)
    + shape(sm('145,382 170,386 196,386 221,380 221,392 145,392'), IRON.shade, 0.8)
    + glint([[186, 312, 0], [187, 340, 2.4], [186, 364, 0]], IRON.hi, 0.8)
    + shape(sm('171,304 196,304 192,314 175,314'), IRON.shade, 0.6)) },
  { id: 'tail', cls: 'a-tail', d: S.tail, body: use('tail', COP.mid) + clip('tail', tailBody()) },
  { id: 'under', cls: 'a-bird', d: S.under, shadow: [sh(['tail'], -3, 4, SH.fea, 0.4)], body: use('under', FEA.shade) + clip('under',
    glint([[150, 222, 0], [120, 240, 3], [88, 248, 0]], FEA.lite, 0.6)) },
  { id: 'legF', cls: 'a-bird', d: S.legF, body: use('legF', 'url(#g-leg)') + clip('legF',
    glint([[164, 252, 0], [162, 268, 2], [160, 282, 0]], '#5a3a18', 0.6) + glint([[156, 292, 0], [164, 296, 2.2], [174, 294, 0]], '#5a3a18', 0.7)) },
  { id: 'arrow', cls: 'a-vane', d: S.arrow, shadow: [sh(['base'], -3, 5, SH.iron, 0.5)], body: use('arrow', 'url(#g-iron)') + clip('arrow',
    // la tige ronde (éclairée en haut), la pointe à deux faces, l'empennage en chevrons
    glint([[100, 292, 0], [190, 292, 2.6], [282, 292, 0]], IRON.hi, 0.9)
    + shape('M285 266 L337 295 L285 295 Z', IRON.lite) + shape('M285 295 L337 295 L283 325 Z', IRON.mid)
    + glint([[290, 274, 0], [312, 284, 2], [332, 294, 0]], IRON.hi, 0.9)
    + shape('M52 274 L92 275 L104 288 L64 292 Z', IRON.lite) + shape('M64 298 L104 301 L92 318 L51 318 Z', IRON.mid)
    + line('M72 278 L84 290 M70 314 L82 302', IRON.shade, 2, 0.7)) },
  { id: 'body', cls: 'a-bird', d: S.body, shadow: [sh(['tail', 'under', 'legF', 'arrow'], -4, 5, SH.cop, 0.45)], body: use('body', 'url(#g-body)') + clip('body',
    // la poitrine claire à droite, le ventre à l'ombre en bas à gauche, des reflets bleu-vert sur le flanc
    oval(236, 168, 16, 26, COP.hi, 0.45, -10)
    + shape(sm('116,220 140,240 170,252 206,254 236,240 220,268 120,268'), COP.shade, 0.6)
    + shape(sm('236,196 252,190 252,220 238,236 226,228'), TEAL.base, 0.85) + glint([[240, 200, 0], [248, 210, 2], [244, 226, 0]], TEAL.hi, 0.7)) },
  { id: 'wing', cls: 'a-bird', d: S.wing, shadow: [sh(['body'], -3, 5, SH.cop, 0.45)], body: use('wing', COP.base) + clip('wing',
    // la rangée de couvertures en haut (claires), une bande bleu-vert, les rémiges en bas (plus sombres)
    shape(sm('150,170 186,156 220,160 238,178 220,184 190,180 160,186'), COP.lite, 0.9)
    + [[164, 176], [184, 170], [204, 170], [222, 176]].map(([x, y]) => glint([[x - 8, y + 4, 0], [x, y + 8, 3], [x + 8, y + 4, 0]], COP.mid, 0.7)).join('')
    + shape(sm('150,198 180,192 214,196 236,198 232,212 200,210 170,212 144,214'), TEAL.base, 0.85)
    + glint([[160, 200, 0], [196, 196, 2.2], [230, 202, 0]], TEAL.hi, 0.8)
    + shape(sm('140,214 170,214 200,214 228,212 220,228 196,240 168,246 132,228'), COP.mid, 0.9)
    + [[166, 196], [186, 194], [206, 196], [224, 200]].map(([x, y]) => glint([[x - 9, y - 6, 0], [x, y - 2, 3], [x + 9, y - 6, 0]], COP.mid, 0.5)).join('')
    + [[150, 226, 136, 230], [172, 232, 158, 240], [196, 230, 178, 242]].map(([x0, y0, x1, y1]) => glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 3], [x1, y1, 0]], COP.shade, 0.7)).join('')) },
  { id: 'legN', cls: 'a-bird', d: S.legN, shadow: [sh(['arrow', 'body'], -3, 4, SH.cop, 0.45)], body: use('legN', 'url(#g-leg)') + clip('legN',
    glint([[204, 252, 0], [206, 268, 2], [210, 280, 0]], '#5a3a18', 0.6)
    + glint([[204, 290, 0], [214, 296, 2.2], [224, 294, 0]], '#5a3a18', 0.7) + glint([[206, 284, 0], [216, 286, 1.6], [224, 288, 0]], '#fff0c0', 0.6)) },
  { id: 'comb', cls: 'a-head', d: S.comb, body: use('comb', 'url(#g-comb)') + clip('comb',
    // trois lobes : chacun son côté éclairé à droite, un creux sombre entre eux
    shape(sm('248,80 252,60 256,44 264,40 274,46 282,56 284,90'), RED.shade, 0.6) + glint([[262, 46, 0], [270, 60, 3], [272, 80, 0]], RED.hi, 0.6) + glint([[308, 30, 0], [314, 54, 3.4], [312, 84, 0]], RED.hi, 0.7)
    + glint([[338, 56, 0], [338, 72, 2.6], [332, 88, 0]], RED.hi, 0.6)
    + glint([[290, 54, 0], [292, 70, 3.4], [290, 88, 0]], RED.deep, 0.6) + glint([[322, 60, 0], [324, 74, 3], [322, 92, 0]], RED.deep, 0.5)) },
  { id: 'mouth', cls: 'a-head', d: S.mouth, body: use('mouth', 'url(#g-mouth)') + clip('mouth', oval(306, 166, 12, 6, '#d85a5a', 0.9, -30) + glint([[300, 160, 0], [306, 164, 2], [312, 160, 0]], '#ff9a9a', 0.7)) },
  { id: 'wattle', cls: 'a-head', d: S.wattle, body: use('wattle', 'url(#g-wattle)') + clip('wattle', glint([[300, 150, 0], [306, 162, 2.4], [304, 174, 0]], '#a84a3a', 0.7)) },
  { id: 'jaw', cls: 'a-jaw', d: S.jaw, shadow: [sh(['mouth', 'wattle'], -2, 3, SH.cop, 0.4)], body: use('jaw', 'url(#g-beak)') + clip('jaw', glint([[318, 150, 0], [324, 156, 1.6], [318, 168, 0]], '#fff8d0', 0.8)) },
  { id: 'head', cls: 'a-head', d: S.head, shadow: [sh(['comb', 'body', 'wing', 'wattle', 'jaw', 'mouth'], -3, 5, SH.cop, 0.45)], body: headBody },
  { id: 'beak', cls: 'a-head', d: S.beak, shadow: [sh(['head', 'jaw', 'wattle'], -2, 4, SH.cop, 0.45)], body: use('beak', 'url(#g-beak)') + clip('beak',
    glint([[316, 116, 0], [334, 120, 2.6], [350, 132, 0]], '#fff8d0', 0.85) + shape(sm('310,132 330,134 350,134 340,138 314,140'), '#8a6020', 0.6)
    + oval(322, 121, 2.4, 1.4, '#5a3a10', 0.8)) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : la girouette tourne un peu au vent (le coq et la flèche oscillent sur le poteau, le socle reste posé), la
// queue frémit, la tête picore l'air par petits à-coups, le bec claque, il cligne.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : il se rejette en arrière en dressant la queue (élan), puis plonge la tête
// en avant et donne un grand coup de bec (le bec s'ouvre), la flèche pivote ; tout revient à la pose de repos.
const PIV = { vane: [184, 296], bird: [186, 290], head: [252, 170], jaw: [316, 150], tail: [170, 180] };
const IDLE = {
  'a-vane': ['vane', 'vane 3.6s ease-in-out infinite alternate'],
  'a-bird': ['bird', 'vane 3.6s ease-in-out infinite alternate'],
  'a-tail': ['tail', 'tail 1.9s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 2.2s ease-in-out infinite'],
  'a-jaw': ['jaw', 'jaw 2.2s ease-in-out infinite'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-blink{animation:blink 4.2s linear infinite}
@keyframes vane{from{transform:rotate(-1.2deg)}to{transform:rotate(1.2deg)}}
@keyframes tail{from{transform:none}to{transform:rotate(3deg) scale(1.02)}}
@keyframes head{0%,60%,100%{transform:none}70%{transform:translate(3px,3px) rotate(4deg)}80%{transform:none}88%{transform:translate(2px,2px) rotate(3deg)}}
@keyframes jaw{0%,62%,100%{transform:none}70%{transform:rotate(8deg)}80%{transform:none}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
${atk('a-bird', 'bird-atk')}${atk('a-vane', 'vane-atk')}${atk('a-head', 'head-atk')}${atk('a-jaw', 'jaw-atk')}${atk('a-tail', 'tail-atk')}
@keyframes bird-atk{0%{transform:none}30%{transform:rotate(-7deg)}48%{transform:rotate(8deg)}62%{transform:rotate(6deg)}100%{transform:none}}
@keyframes vane-atk{0%{transform:none}30%{transform:rotate(-4deg)}48%{transform:rotate(5deg)}62%{transform:rotate(3deg)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}30%{transform:translate(-4px,-4px) rotate(-10deg)}48%{transform:translate(12px,8px) rotate(12deg)}62%{transform:translate(9px,6px) rotate(9deg)}100%{transform:none}}
@keyframes jaw-atk{0%{transform:none}30%{transform:rotate(14deg)}44%{transform:rotate(18deg)}52%{transform:rotate(-2deg)}100%{transform:none}}
@keyframes tail-atk{0%{transform:none}30%{transform:rotate(8deg) scale(1.06)}48%{transform:rotate(-6deg)}100%{transform:none}}
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
  // la tête emporte la mâchoire ; l'oiseau emporte la tête et la queue
  s = nest(s, 'a-jaw', 'a-head');
  for (const c of ['a-head', 'a-tail']) s = nest(s, c, 'a-bird');
  return s;
}

module.exports = { id: 'epouvantails-1', w: W, h: H, pad: PAD, foot: [184, 390], svg };
