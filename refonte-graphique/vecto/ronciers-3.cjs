// Le porc-épic des ronces (ronciers-3), monstre des Ronciers : redessiné par le code d'après le dessin d'origine, dans le
// même cadre (455 × 355, mêmes proportions, même pose) : un porc-épic trapu tourné vers la droite ; une grande gerbe de
// piquants beiges à pointe sombre qui part du dos en éventail, des feuilles vertes et des baies rouges piquées à leur
// pied ; corps de fourrure brun-mauve, tête tan à crête sombre, petite oreille ronde, œil jaune furieux à iris rouge,
// museau à truffe noire, gueule ouverte aux crocs ; pattes courtes à griffes claires.
// DÉCALQUÉ : silhouette exacte (master), pointe de chaque piquant relevée sur la silhouette, corps et tête pris dans la
// silhouette (outils/decoupe.py), feuilles et baies relevées par leur couleur. La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');
const { sm, rib, glint, tooth, nest } = require('./formes.cjs');

const W = 455, H = 355, PAD = 40;

// ---------- couleurs ----------
const QUILL = { hi: '#f0dcb0', lite: '#c8a878', base: '#8e6c4a', mid: '#6a4c34', shade: '#4a3222', deep: '#22140e' };
const FUR = { hi: '#a08070', lite: '#7a5c4e', base: '#5e4438', shade: '#42302a', deep: '#261a16' };
const FACE = { hi: '#e8b47a', lite: '#c08048', base: '#94602f', shade: '#6e4426', deep: '#3e2616' };
const SH = { dark: '#140a08' };

// ---------- les formes relevées sur l'original ----------
const BODY = sm('330,204 310,189 282,182 237,182 199,188 159,198 118,215 88,236 84,291 106,289 107,290 99,298 99,300 111,299 118,296 126,296 129,298 124,303 124,310 121,314 123,321 116,335 117,346 165,348 178,347 179,342 217,341 218,337 216,332 209,324 205,322 211,321 214,324 217,324 219,320 246,319 247,324 251,323 259,330 256,339 260,342 259,348 275,350 324,350 322,346 323,344 336,344 336,228');
const HEAD = sm('300,196 300,320 338,320 341,317 338,307 356,301 371,302 395,310 414,310 421,304 421,300 418,294 413,296 409,292 405,292 401,289 399,284 403,280 407,282 405,285 406,289 414,285 419,292 425,287 437,287 439,290 444,290 446,288 452,272 452,264 449,258 431,238 424,235 420,229 384,206 353,192 328,190');
// la pointe de chaque piquant, relevée sur la silhouette ; le piquant part du dos vers elle
const TIPS = '40,74 41,128 78,173 7,156 59,196 45,200 73,205 30,205 84,233 20,253 72,265 63,273 53,289 106,289 402,282 428,165 376,177 398,156 385,157 410,118 372,139 383,114 362,130 378,70 338,114 343,85 326,103 326,32 301,65 292,87 274,11 262,68 257,57 250,77 220,4 217,69 205,36 204,51 182,16 186,72 174,57 175,83 117,17 139,95 88,57 105,92 116,114'.split(' ').map((q) => q.split(',').map(Number))
  .filter(([x, y]) => y < 236 && !(x > 395 && y > 240));
const C = [236, 262]; // le centre du dos, d'où rayonnent les piquants
const QUILLS = TIPS.map(([x, y]) => {
  const dx = x - C[0], dy = y - C[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L;
  const b = [C[0] + ux * Math.min(70, L * 0.45), C[1] + uy * Math.min(70, L * 0.45)];
  return { t: [x, y], b, L: Math.hypot(x - b[0], y - b[1]), w: Math.max(26, Math.min(40, L * 0.2)) };
}).sort((a, b) => b.L - a.L);
// un rang de piquants plus courts, devant, entre les grands (comme sur l'original : plusieurs rangs qui se recouvrent)
const ANG = TIPS.map(([x, y]) => Math.atan2(y - C[1], x - C[0])).sort((a, b) => a - b);
const INNER = ANG.slice(0, -1).map((a, i) => (a + ANG[i + 1]) / 2).filter((a, i) => i % 2 === 0).map((a, i) => {
  const r0 = 52, r1 = 118 + (i % 3) * 14;
  const b = [C[0] + Math.cos(a) * r0, C[1] + Math.sin(a) * r0], t = [C[0] + Math.cos(a) * r1, C[1] + Math.sin(a) * r1];
  return { t, b, L: r1 - r0, w: 30 };
}).filter((q) => q.t[1] < 222);
const quillD = (q) => rib([[q.b[0], q.b[1], q.w * 0.9], [(q.b[0] * 0.75 + q.t[0] * 0.25), (q.b[1] * 0.75 + q.t[1] * 0.25), q.w], [(q.b[0] * 0.4 + q.t[0] * 0.6), (q.b[1] * 0.4 + q.t[1] * 0.6), q.w * 0.55], [q.t[0], q.t[1], 0]]);
// les baies : [x, y, rayon] (centres et tailles relevés par leur couleur sur l'original)
const BERRIES = [[151, 249, 10.9], [186, 237, 6.5], [244, 220, 7.4], [198, 221, 8.5], [212, 202, 4.3], [272, 197, 6.7], [316, 158, 4.7]];

// la guirlande : un ruban vert le long du dos, et des feuilles pointues qui en sortent vers l'extérieur
const ARC = [[96, 252, 0], [124, 226, 12], [164, 206, 14], [208, 194, 14], [252, 188, 14], [296, 186, 13], [332, 190, 10], [352, 200, 0]];
const LEAVES = [[104, 246, 74, 238], [126, 228, 102, 206], [150, 214, 136, 188], [176, 204, 168, 176], [204, 196, 202, 168], [232, 190, 240, 164], [262, 188, 274, 162],
  [290, 186, 306, 164], [318, 188, 340, 172], [340, 194, 364, 186]].map(([x, y, tx, ty], i) => ({ x, y, tx, ty, w: 12 + (i % 3) * 3 }));
const leafD = ({ x, y, tx, ty, w }) => { const L = Math.hypot(tx - x, ty - y), nx = -(ty - y) / L * w / 2, ny = (tx - x) / L * w / 2;
  return `M${x} ${y} Q${n((x + tx) / 2 + nx)} ${n((y + ty) / 2 + ny)} ${tx} ${ty} Q${n((x + tx) / 2 - nx)} ${n((y + ty) / 2 - ny)} ${x} ${y} Z`; };
const leafHalfD = ({ x, y, tx, ty, w }) => { const L = Math.hypot(tx - x, ty - y), nx = -(ty - y) / L * w / 2, ny = (tx - x) / L * w / 2;
  return `M${x} ${y} Q${n((x + tx) / 2 + nx)} ${n((y + ty) / 2 + ny)} ${tx} ${ty} Z`; };

// ---------- dégradés ----------
const defs = [
  rad('g-quills', 236, 262, 250, [[0, QUILL.deep], [0.4, QUILL.shade], [0.75, QUILL.mid], [1, QUILL.deep]]),
  lin('g-body', 320, 190, 120, 340, [[0, FUR.lite], [0.5, FUR.base], [1, FUR.shade]]),
  lin('g-head', 440, 200, 310, 300, [[0, FACE.lite], [0.5, FACE.base], [1, FACE.shade]]),
  rad('g-eye', 0.4, 0.4, 0.75, [[0, '#ffffe8'], [0.5, '#f8e070'], [1, '#d0a020']], false),
  rad('g-berry', 0.62, 0.32, 0.75, [[0, '#ffd0b0'], [0.3, '#ff6a40'], [0.75, '#d02a18'], [1, '#7a0a08']], false),
  lin('g-leaf', 0, 0, 1, 1, [[0, '#d8f080'], [0.5, '#8ab838'], [1, '#4a7a1e']], false),
  lin('g-mouth', 0, 272, 0, 302, [[0, '#2a060c'], [1, '#7a2030']]),
  rad('g-nose', 0.6, 0.3, 0.8, [[0, '#7a7080'], [0.4, '#2a2430'], [1, '#0c080e']], false),
].join('');

// ---------- un piquant : clair sur le dessus (côté lumière), une arête sombre, la pointe sombre ----------
function quillBody(q) {
  const d = quillD(q), [bx, by] = q.b, [tx, ty] = q.t;
  const ux = (tx - bx) / q.L, uy = (ty - by) / q.L;
  const at = (f, sd) => [bx + (tx - bx) * f - uy * sd, by + (ty - by) * f + ux * sd];
  // la face à l'ombre (le côté gauche du piquant), la face éclairée tan, la pointe presque noire
  const side = ux > 0 ? 1 : -1;
  return `<path d="${d}" transform="translate(-3 4)" fill="${SH.dark}" opacity="0.45"/>` + shape(d, QUILL.lite)
    + shape(rib([at(0, side * q.w * 0.24).concat(q.w * 0.48), at(0.3, side * q.w * 0.25).concat(q.w * 0.5), at(0.65, side * q.w * 0.14).concat(q.w * 0.28), at(1, 0).concat(0)]), QUILL.mid, 0.9)
    + glint([at(0.12, -side * q.w * 0.18).concat(0), at(0.4, -side * q.w * 0.16).concat(q.w * 0.16), at(0.7, -side * 3).concat(0)], QUILL.hi, 0.6)
    + shape(rib([at(0.68, 0).concat(q.w * 0.4), at(0.84, 0).concat(q.w * 0.22), at(1, 0).concat(0)]), QUILL.deep, 0.92);
}

// ---------- le visage (lu sur un gros plan quadrillé) ----------
const headBody = use('head', 'url(#g-head)') + clip('head',
  // le dessus de la tête gris-brun, avec des mèches claires, jusqu'au museau ; la bande claire du dessus du museau
  shape(sm('300,198 330,190 362,196 394,212 424,232 448,254 432,254 406,242 384,236 362,232 340,228 316,222'), '#6e5c4c')
  + glint([[322, 196, 0], [352, 202, 3.4], [384, 214, 0]], '#c8b498', 0.8) + glint([[340, 214, 0], [374, 222, 3], [404, 236, 0]], '#a8947a', 0.7)
  + glint([[380, 238, 0], [410, 246, 4], [436, 256, 0]], FACE.hi, 0.7)
  // la joue claire, quelques points de moustache, le dessous du museau à l'ombre
  + shape(sm('318,250 342,256 360,276 356,300 330,306 314,290'), FACE.lite, 0.7)
  + dot(344, 262, 1.8, FACE.deep) + dot(352, 268, 1.6, FACE.deep) + dot(342, 272, 1.5, FACE.deep)
  + shape(sm('360,296 400,300 430,292 440,304 360,314'), FACE.shade, 0.7)
  // le grand œil jaune, l'iris rouge, la pupille, le reflet
  + oval(368, 248, 17, 15, '#140a08') + oval(368, 248, 15, 13, 'url(#g-eye)') + dot(374, 250, 6.5, '#b8201a') + dot(375, 250, 3.2, '#1a0606') + dot(371, 246, 2, '#fff')
  + `<g class="a-blink" opacity="0">${oval(368, 248, 16, 14, FACE.base)}${line('M352 250 Q368 258 384 249', '#140a08', 2.6)}</g>`
  // le gros sourcil noir, qui plonge vers le museau et coupe le haut de l'œil (regard furieux)
  + shape('M344 226 C362 228 384 234 400 244 L398 252 C384 246 368 240 350 240 C344 238 342 230 344 226 Z', '#120806')
  + glint([[348, 228, 0], [372, 231, 1.6], [396, 242, 0]], '#5a4838', 0.8)
  // la truffe noire au bout du museau
  + `<path d="M430 258 C436 252 448 254 452 262 C454 270 448 276 440 276 C432 274 428 266 430 258 Z" fill="url(#g-nose)"/>` + oval(444, 258, 3.6, 2, '#c8c0d0', 0.9, -10)
  // la gueule ouverte, étroite : l'intérieur sombre, une petite langue, une rangée de petits crocs en haut et en bas
  + `<g class="a-mouth"><path d="M352 280 C374 276 404 276 430 280 C428 290 414 298 394 299 C372 299 358 292 352 280 Z" fill="url(#g-mouth)"/>`
  + oval(372, 290, 8, 3.4, '#c84a5a')
  + [366, 376, 386, 397, 408, 419].map((x, i) => tooth([x - 4, 278.5], [x + 4, 278.5], [x, 287 + (i % 2) * 2])).join('')
  + [382, 393, 404, 415].map((x, i) => tooth([x - 4, 298], [x + 4, 297.5], [x, 290 - (i % 2) * 2])).join('') + '</g>'
);

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
// le fond : toute la silhouette d'origine, couleur des piquants (ce que les piquants dessinés ne couvrent pas)
const SIL = require('./silhouettes/ronciers-3.json');
const parts = [
  { id: 'base', cls: 'a-quills', d: SIL.out, body: use('base', 'url(#g-quills)') },
  ...QUILLS.map((q, i) => ({ id: `q${i}`, cls: 'a-quills', d: quillD(q), body: quillBody(q) })),
  ...INNER.map((q, i) => ({ id: `qi${i}`, cls: 'a-quills', d: quillD(q), body: quillBody(q) })),
  { id: 'body', cls: 'a-body', d: BODY, shadow: [sh(QUILLS.map((q, i) => `q${i}`).concat('base'), -4, 6, SH.dark, 0.45)], body: use('body', 'url(#g-body)') + clip('body',
    // la fourrure : de grandes mèches (un creux sombre, une pointe claire), le ventre plus clair, les pattes à l'ombre
    [[150, 250, 130, 280], [190, 236, 176, 270], [236, 230, 228, 266], [280, 230, 284, 262], [120, 290, 108, 316], [200, 290, 196, 318], [270, 286, 276, 316]].map(([x0, y0, x1, y1]) =>
      glint([[x0, y0, 0], [(x0 + x1) / 2 - 2, (y0 + y1) / 2, 5], [x1, y1, 0]], FUR.shade, 0.6) + glint([[x0 + 4, y0, 0], [(x0 + x1) / 2 + 2, (y0 + y1) / 2, 2.6], [x1 + 4, y1, 0]], FUR.hi, 0.45)).join('')
    + shape(sm('90,300 150,312 220,318 300,312 336,300 336,350 90,350'), FUR.deep, 0.45)
    // les griffes claires au bout des pattes
    + [[132, 336], [146, 338], [160, 337], [306, 336], [320, 338], [334, 336]].map(([x, y]) => `<path d="M${x - 4} ${y - 8} Q${x - 3} ${y - 2} ${x + 1} ${y + 1} Q${x + 3} ${y - 4} ${x + 3} ${y - 9} Z" fill="#eee8e0"/>`).join('')) },
  // la guirlande de feuilles au pied des piquants (le long du dos, comme sur l'original) et les baies rouges
  { id: 'leaves', cls: 'a-quills', d: LEAVES.map(leafD).join('') + rib(ARC), shadow: [sh(['body', 'base'], -3, 4, SH.dark, 0.45)],
    body: shape(rib(ARC), '#5a8a22') + LEAVES.map((l) => shape(leafD(l), 'url(#g-leaf)') + shape(leafHalfD(l), '#e4f8a0', 0.45)).join('') },
  { id: 'berries', cls: 'a-body', d: BERRIES.map(([x, y, r]) => `M${x - r} ${y}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0Z`).join(''), shadow: [sh(['body', 'leaves'], -2, 3, SH.dark, 0.45)],
    body: BERRIES.map(([x, y, r]) => dot(x, y, r, 'url(#g-berry)') + oval(x + r * 0.3, y - r * 0.35, r * 0.3, r * 0.2, '#ffffff', 0.85)).join('') },
  { id: 'head', cls: 'a-head', d: HEAD, shadow: [sh(['body', 'base', 'leaves'], -3, 6, SH.dark, 0.45)], body: headBody },
  // l'oreille ronde, sur la crête
  { id: 'ear', cls: 'a-head', d: sm('304,196 318,188 336,190 344,204 340,220 326,226 310,220 302,208'), shadow: [sh(['head'], -2, 4, SH.dark, 0.4)],
    body: use('ear', FACE.shade) + clip('ear', oval(322, 208, 10, 11, '#3a2228') + glint([[310, 196, 0], [326, 190, 2.4], [340, 200, 0]], FACE.lite, 0.8)) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : les piquants se hérissent et se couchent doucement (ils respirent), le corps se soulève, la tête gronde
// (la gueule tremble), il cligne. Attaque (classe « atk », 0,75 s) : il se ramasse en hérissant tous ses piquants,
// puis charge en avant la gueule ouverte ; tout revient à la pose de repos.
const PIV = { quills: [236, 262], body: [220, 330], head: [320, 270] };
const IDLE = {
  'a-quills': ['quills', 'quills 1.6s ease-in-out infinite alternate'],
  'a-body': ['body', 'body 1.6s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 2.2s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-root{transform-origin:220px 340px}
.a-mouth{transform-origin:386px 286px;animation:mouth .45s ease-in-out infinite alternate}
.a-blink{animation:blink 4.2s linear infinite}
@keyframes quills{from{transform:none}to{transform:scale(1.03,1.04)}}
@keyframes body{from{transform:none}to{transform:translate(0,-2px) scale(1.004,1.01)}}
@keyframes head{from{transform:none}to{transform:rotate(-1.6deg)}}
@keyframes mouth{from{transform:scale(1,.9)}to{transform:scale(1,1.08)}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-quills', 'quills-atk')}${atk('a-head', 'head-atk')}
@keyframes root-atk{0%{transform:none}28%{transform:translate(-8px,2px)}46%{transform:translate(24px,-4px)}60%{transform:translate(20px,0)}80%{transform:translate(4px,0)}100%{transform:none}}
@keyframes quills-atk{0%{transform:none}28%{transform:scale(1.1,1.12)}46%{transform:scale(1.04,1.06)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}28%{transform:rotate(-6deg)}46%{transform:translate(4px,3px) rotate(5deg)}100%{transform:none}}
`.replace(/\n/g, '');

function svg(anime = true) {
  let s = figure({ master: SIL, w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'ronciers-3', w: W, h: H, pad: PAD, foot: [220, 344], svg };
