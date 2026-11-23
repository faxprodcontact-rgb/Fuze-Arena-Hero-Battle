// Le papillon de nuit (ronciers-4), monstre des Ronciers : redessiné par le code d'après le dessin d'origine, dans le même
// cadre (433 × 331, mêmes proportions, même pose) : un gros papillon de nuit vu de face, ailes déployées ; ailes du haut
// brunes au bord d'attaque clair, chacune marquée d'un grand œil vert et de petites taches vertes ; ailes du bas brunes
// terminées par deux queues ; corps duveteux crème, petite tête aux yeux verts furieux et aux crocs, deux antennes en plume.
// DÉCALQUÉ : silhouette exacte (master), les quatre ailes et les antennes découpées dans la silhouette
// (outils/decoupe.py), corps relevé sur un gros plan, couleurs du corps et des antennes relevées (couleurs/ronciers-4.json),
// yeux des ailes et taches lus sur gros plans quadrillés. La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');
const { sm, glint, cel, nest } = require('./formes.cjs');

const W = 433, H = 331, PAD = 40;
const SIL = require('./silhouettes/ronciers-4.json');
const MAT = require('./couleurs/ronciers-4.json');

// ---------- couleurs ----------
const WING = { hi: '#e8c49a', lite: '#c8a07a', base: '#7a5a46', shade: '#5a4032', deep: '#3a2820' };
const CREAM = { hi: '#ffffff', base: '#f4e4cc', sh: '#d4bc9c', deep: '#a88e70' };
const TONES = { creme: CREAM, brun: { hi: '#b09080', base: '#7a5a48', sh: '#5a4034', deep: '#3a2a22' },
  vert: { hi: '#e0ff90', base: '#a8d838', sh: '#6a9a20', deep: '#3a5a14' }, sombre: { hi: '#6a5048', base: '#3e2a24', sh: '#2a1c18', deep: '#1a100e' } };
const PAINT_SRC = ['brun', 'creme', 'vert', 'sombre'].map((k) => (MAT[k] && MAT[k].d ? cel(MAT[k].d, TONES[k], 4, 2) : '')).join('');
const PAINT = '<use href="#p-mat"/>';

// ---------- les formes relevées sur l'original ----------
const UL = sm('4,46 5,52 27,84 16,115 35,133 33,159 61,174 60,180 63,199 70,202 89,205 135,204 119,212 205,190 201,113 197,115 179,90 160,71 137,55 119,46 98,38 82,35 40,35 24,38');
const UR = sm('430,37 419,33 395,29 363,31 345,36 321,48 308,58 272,104 275,190 316,202 345,201 359,198 375,191 379,173 378,163 390,157 405,145 405,129 403,119 418,103 418,98 409,74 428,45');
const LL = sm('60,175 63,199 70,202 89,205 135,204 115,214 97,227 81,244 73,256 70,265 78,280 90,292 102,300 112,304 125,305 137,302 138,325 140,328 145,328 154,318 177,275 179,300 185,313 189,314 195,304 200,282 202,283 208,297 211,298 205,175');
const LR = sm('378,175 268,175 264,287 280,323 284,327 289,328 294,303 315,306 331,300 340,294 354,280 362,265 361,260 353,246 332,223 312,209 297,202 339,202 359,198 376,190');
// les antennes en plume (découpées dans la silhouette, sans les ailes)
const ANT = sm('132,4 132,9 136,15 134,17 126,15 126,21 138,31 128,32 156,53 165,54 183,65 198,80 211,100 230,96 250,96 262,104 265,110 283,82 300,64 308,58 304,46 317,42 326,33 326,30 314,28 322,18 322,14 317,15 315,13 317,9 317,4 315,4 301,16 301,7 295,9 288,20 286,18 286,9 282,8 274,23 274,28 270,29 269,37 265,38 262,44 262,51 257,58 252,72 245,98 239,95 236,98 230,94 227,94 228,97 225,98 222,94 221,87 214,71 210,67 208,59 202,53 200,45 196,42 189,29 185,32 179,18 173,16 168,11 166,22 156,8 150,8 150,12 156,23 154,25 147,14 138,5');
// le corps duveteux : une grosse tête ronde hérissée de duvet, puis l'abdomen en anneaux (relevés sur un gros plan)
const fuzz = (cx, cy, rx, ry, k, amp) => sm(Array.from({ length: k }, (_, i) => {
  const a = (i / k) * Math.PI * 2, r = i % 2 ? 1 + amp * (0.35 + 0.65 * Math.abs(Math.sin(i * 2.3))) : 1 - amp * 0.3; // des touffes inégales
  return `${n(cx + Math.cos(a) * rx * r)},${n(cy + Math.sin(a) * ry * r)}${i % 2 ? '!' : ''}`;
}).join(' '));
const HEAD = fuzz(234, 141, 43, 41, 30, 0.06);
const ABD = sm('208,176 260,176 266,200 263,228 257,255 249,280 238,300 231,307 224,300 214,280 207,255 203,228 202,200');
const BODY = HEAD + ABD;
// les bords d'attaque clairs (bord extérieur puis intérieur), les yeux des ailes, les taches vertes
const EDGE_L = sm('4,44 30,36 60,33 100,36 140,52 170,78 192,104 204,130! 186,122 166,96 140,72 104,54 62,50 28,58 8,62!');
const EDGE_R = sm('430,40 404,32 372,30 340,36 306,58 286,84 272,110! 288,112 304,90 330,66 362,52 396,50 424,58!');
const SPOT = { L: [116, 105], R: [325, 107] };
const DOTS = [[55, 93, 4, 6], [80, 155, 4, 5], [160, 155, 4, 5], [150, 140, 3, 4], [385, 90, 4, 6], [362, 142, 4, 5], [300, 155, 4, 5]];
// les nervures : de longs fuseaux doux, plus clairs, qui partent de la racine de l'aile (pas de rayures)
const VEINS = { UL: [[[196, 150], [110, 168], [30, 150]], [[196, 172], [130, 190], [66, 196]], [[196, 120], [140, 70], [70, 60]]],
  UR: [[[276, 150], [340, 168], [400, 140]], [[276, 172], [330, 190], [372, 186]], [[276, 120], [330, 72], [400, 58]]],
  LL: [[[205, 200], [150, 230], [90, 270]], [[205, 220], [170, 260], [130, 300]]], LR: [[[268, 200], [310, 226], [348, 262]], [[268, 220], [290, 262], [300, 300]]] };
const veins = (k) => VEINS[k].map((v) => glint(v.map(([x, y], i) => [x, y, i === 1 ? 3 : 0]), WING.lite, 0.5)).join('');

// ---------- dégradés ----------
const defs = [
  lin('g-wing', 0, 0, 1, 1, [[0, '#8e6a52'], [0.5, WING.base], [1, WING.deep]], false),
  lin('g-lwing', 0, 0, 0, 1, [[0, '#86644e'], [0.6, WING.shade], [1, WING.deep]], false),
  rad('g-spot', 0.42, 0.38, 0.7, [[0, '#f0ff98'], [0.5, '#bfe83a'], [1, '#7ab020']], false),
  rad('g-eye', 0.4, 0.38, 0.7, [[0, '#f4ffb0'], [0.5, '#b8e040'], [1, '#5a8a18']], false),
  `<g id="p-mat">${PAINT_SRC}</g>`,
].join('');

// ---------- un grand œil d'aile ----------
const spot = ([x, y]) => `<circle cx="${x}" cy="${y}" r="36" fill="#2a4418" opacity="0.55"/>` + dot(x, y, 33, '#3a6418') + dot(x, y, 29.5, 'url(#g-spot)')
  + dot(x + 2, y + 2, 20, '#4a7a1c') + dot(x + 1, y + 1, 16.5, '#c8f048') + dot(x + 4, y + 5, 8, '#3a6418')
  + `<path d="M${x - 14} ${y - 4} A15 15 0 0 1 ${x + 2} ${y - 15}" fill="none" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity="0.85"/>`;
const wing = (id, d, grad, k, extra) => ({ id, cls: `a-${id}`, d, body: use(id, `url(#${grad})`) + clip(id, veins(k) + extra) });

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color = '#1a0e0a', o = 0.4) => ({ on, dx, dy, color, o });
const parts = [
  wing('LL', LL, 'g-lwing', 'LL', glint([[200, 186, 0], [130, 214, 4], [80, 250, 4], [76, 268, 0]], WING.lite, 0.8)
    + shape(sm('130,280 154,286 176,280 200,286 206,300 190,316 160,330 136,328'), WING.shade, 0.6)),
  wing('LR', LR, 'g-lwing', 'LR', glint([[272, 192, 0], [320, 210, 4], [350, 244, 4], [358, 262, 0]], WING.lite, 0.8)
    + shape(sm('262,284 280,286 296,292 300,312 288,330 270,316'), WING.shade, 0.6)),
  wing('UL', UL, 'g-wing', 'UL', cel(EDGE_L, { hi: '#fff0d8', base: WING.lite, sh: '#a8805e' }, 4, 2) + spot(SPOT.L)
    + DOTS.slice(0, 4).map(([x, y, rx, ry]) => oval(x, y, rx, ry, '#c8f048', 0.9)).join('')),
  wing('UR', UR, 'g-wing', 'UR', cel(EDGE_R, { hi: '#fff0d8', base: WING.lite, sh: '#a8805e' }, 4, 2) + spot(SPOT.R)
    + DOTS.slice(4).map(([x, y, rx, ry]) => oval(x, y, rx, ry, '#c8f048', 0.9)).join('')),
  { id: 'ant', cls: 'a-ant', d: ANT, shadow: [sh(['UL', 'UR'], -3, 4)], body: use('ant', TONES.brun.base) + clip('ant', PAINT) },
  { id: 'body', cls: 'a-body', d: BODY, shadow: [sh(['UL', 'UR', 'LL', 'LR', 'ant'], -4, 6)], body: cel(ABD, CREAM, 5, 2.4) + `<path d="${HEAD}" transform="translate(-2 5)" fill="#a88e70" opacity="0.5"/>` + cel(HEAD, CREAM, 5, 2.4) + clip('body',
    // le duvet : des mèches claires et des creux doux, des anneaux sur l'abdomen
    [[210, 112], [234, 104], [258, 110], [200, 146], [272, 150], [214, 172], [252, 172], [222, 190], [244, 190]].map(([x, y]) => glint([[x - 6, y + 4, 0], [x, y - 2, 2.4], [x + 6, y + 4, 0]], '#ffffff', 0.7)).join('')
    + [[212, 206, 260, 206], [208, 232, 258, 232], [212, 258, 252, 258], [218, 282, 244, 282]].map(([x0, y, x1, y1]) => glint([[x0, y, 0], [(x0 + x1) / 2, y + 3, 2.4], [x1, y1, 0]], CREAM.deep, 0.55)).join('')
    // les yeux verts furieux (le droit est le gauche en miroir autour du milieu de la tête), leurs sourcils, les crocs
    + [['196.8,134.9 212.2,131.6 227.4,141.8 229.2,151.9 218.9,158.8 205.3,155.3 197.7,146.8', '199.4,136.7 212.2,133.7 225.8,142.6 227,151.1 218.1,156.6 206.2,153.2 200.2,146', 218, 147], ['271.2,134.9 255.8,131.6 240.6,141.8 238.8,151.9 249.1,158.8 262.7,155.3 270.3,146.8', '268.6,136.7 255.8,133.7 242.2,142.6 241,151.1 249.9,156.6 261.8,153.2 267.8,146', 250, 147]].map(([o, i, px, py]) => shape(sm(o), '#1a1012') + shape(sm(i), 'url(#g-eye)')
      + dot(px, py, 5.6, '#0e0a0a') + dot(px - 2.6, py - 3.6, 2, '#ffffff')).join('')
    + shape(sm('193.4,123 208.8,124.8 227.4,136.7 229.2,141.8 208.8,131.6 195.2,129.8'), '#2a1a16') + shape(sm('274.6,123 259.2,124.8 240.6,136.7 238.8,141.8 259.2,131.6 272.8,129.8'), '#2a1a16')
    + `<g class="a-blink" opacity="0">${shape(sm('196.8,134.9 212.2,131.6 227.4,141.8 229.2,151.9 218.9,158.8 205.3,155.3 197.7,146.8'), CREAM.base)}${shape(sm('271.2,134.9 255.8,131.6 240.6,141.8 238.8,151.9 249.1,158.8 262.7,155.3 270.3,146.8'), CREAM.base)}`
    + `${line('M199 147 Q214 156 229 149', '#1a1012', 2.2)}${line('M269 147 Q254 156 239 149', '#1a1012', 2.2)}</g>`
    + shape(sm('226,168 246,166 244,176 236,181 228,176'), '#3a1418') + shape('M229 170L232 178L234 170Z', '#ffffff') + shape('M238 169L240 177L242 169Z', '#ffffff')) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : les ailes battent doucement (celles du haut et du bas un peu décalées), les antennes frémissent, le corps
// flotte, il cligne. Attaque (classe « atk », 0,75 s) : il replie les ailes puis les rabat d'un grand coup en fonçant ;
// tout revient à la pose de repos.
const PIV = { UL: [206, 150], UR: [272, 150], LL: [208, 196], LR: [266, 196], ant: [238, 104], body: [236, 200] };
const IDLE = {
  'a-UL': ['UL', 'wl .7s ease-in-out infinite alternate'],
  'a-UR': ['UR', 'wr .7s ease-in-out infinite alternate'],
  'a-LL': ['LL', 'wl .7s ease-in-out -.15s infinite alternate'],
  'a-LR': ['LR', 'wr .7s ease-in-out -.15s infinite alternate'],
  'a-ant': ['ant', 'ant 1.6s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-root{transform-origin:236px 200px;animation:float 1.4s ease-in-out infinite alternate}
.a-blink{animation:blink 4.2s linear infinite}
@keyframes float{from{transform:none}to{transform:translate(0,-5px)}}
@keyframes wl{from{transform:scale(1,1)}to{transform:scale(.9,.97) rotate(3deg)}}
@keyframes wr{from{transform:scale(1,1)}to{transform:scale(.9,.97) rotate(-3deg)}}
@keyframes ant{from{transform:rotate(-1.5deg)}to{transform:rotate(1.5deg)}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
.atk .a-root{animation:float 1.4s ease-in-out infinite alternate,root-atk .75s ease-in-out;animation-composition:replace,add}
${atk('a-UL', 'wl-atk')}${atk('a-LL', 'wl-atk')}${atk('a-UR', 'wr-atk')}${atk('a-LR', 'wr-atk')}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-6px,-6px)}50%{transform:translate(18px,4px) scale(1.04)}66%{transform:translate(14px,2px)}100%{transform:none}}
@keyframes wl-atk{0%{transform:none}30%{transform:scale(.7,.95) rotate(8deg)}50%{transform:scale(1.05,1) rotate(-6deg)}70%{transform:rotate(-2deg)}100%{transform:none}}
@keyframes wr-atk{0%{transform:none}30%{transform:scale(.7,.95) rotate(-8deg)}50%{transform:scale(1.05,1) rotate(6deg)}70%{transform:rotate(2deg)}100%{transform:none}}
`.replace(/\n/g, '');

function svg(anime = true) {
  const s = figure({ master: SIL, w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'ronciers-4', w: W, h: H, pad: PAD, foot: [236, 326], svg };
