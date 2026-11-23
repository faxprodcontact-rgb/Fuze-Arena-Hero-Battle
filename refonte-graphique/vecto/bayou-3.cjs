// Le poisson-archer (bayou-3), monstre du Bayou : redessiné par le code d'après le dessin d'origine, dans le même cadre
// (374 × 277, mêmes proportions, même pose) : un poisson trapu tourné vers le haut à droite, blanc crème barré de larges
// bandes vert sombre ; nageoires orange à pointes mauves (queue, dorsale en épines, ventrales, pectorale) ; gros œil
// orange au sourcil froncé, gueule ouverte pointée vers le ciel ; devant la gueule, une boule d'eau qui brille.
// DÉCALQUÉ : silhouette exacte (master), nageoires et corps découpés dans la silhouette (outils/decoupe.py), bandes et
// pointes relevées par leur couleur (outils/couleurs.py --vote → couleurs/bayou-3.json), œil et gueule lus sur un gros
// plan quadrillé. La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');
const { sm, glint, cel } = require('./formes.cjs');

const W = 374, H = 277, PAD = 40;
const SIL = require('./silhouettes/bayou-3.json');
const MAT = require('./couleurs/bayou-3.json');

// ---------- chaque matière, en aplats nets ----------
const TONES = {
  blanc: { hi: '#ffffff', base: '#e6e8d8', sh: '#b4b8a2', deep: '#8a8e78' },
  vert: { hi: '#7a866a', base: '#4c5640', sh: '#363e2c', deep: '#22281c' },
  or: { hi: '#ffe08a', base: '#f6aa2e', sh: '#c8781a', deep: '#8a4c10' },
  violet: { hi: '#b4a4a8', base: '#7e6c72', sh: '#5a4a50', deep: '#3a2c32' },
  sombre: { hi: '#4a4a40', base: '#24241e', sh: '#141410', deep: '#0a0a08' },
  rose: { hi: '#c88aa0', base: '#8a4a60', sh: '#5a2a3c', deep: '#3a1424' },
};
const PAINT_SRC = ['blanc', 'vert', 'or', 'violet', 'rose', 'sombre'].map((k) => (MAT[k] && MAT[k].d ? cel(MAT[k].d, TONES[k], 5, 2.4) : '')).join('');
const PAINT = '<use href="#p-mat"/>';

// ---------- les formes relevées sur l'original ----------
const DORSAL = sm('96,21 92,23 94,36 93,68 89,69 77,64 63,62 56,63 58,70 63,76 74,97 58,100 58,104 77,125 77,131 85,135 99,113 126,87 149,71 161,67 152,54 136,39 108,24');
const TAIL = sm('6,116 4,121 23,147 36,177 34,184 38,196 39,210 35,244 41,245 53,236 86,202 84,147 41,123 29,119');
const FINS = sm('108,197 118,199 125,203 107,219 99,231 98,236 128,236 129,248 134,252 136,252 146,242 157,255 168,274 172,274 188,241 191,206 196,203 196,198 146,201');
const BODY = sm('313,33! 302,35 259,38 217,47 187,59 183,59 164,69 159,66 126,87 99,113 86,134 86,136 90,139 84,147 86,198 89,198 97,189 108,197 146,201 195,198 196,203 198,202 201,207 209,206 214,215 219,214 221,216 222,224 226,225 246,199 254,179 254,173 266,164 298,130 307,125 313,115 313,107 306,104 304,101 317,73 320,72!');
const PECT = sm('228,142 244,146 254,160 254,179 246,199 226,225 222,224 214,215 209,206 201,207 204,190 212,168 220,150');
// la gueule ouverte (l'intérieur), la lèvre du bas
const MOUTH = sm('309,53! 300,74 290,92 284,103! 296,106 305,108!');
const GLOW = [334, 39];
// les rayons des nageoires : de longs fuseaux doux qui partent de la base (pas de rayures)
const RAYS = {
  dorsal: [[[90, 120], [76, 80]], [[104, 104], [94, 40]], [[120, 92], [116, 46]], [[136, 80], [140, 52]], [[86, 126], [66, 104]]],
  tail: [[[80, 160], [20, 128]], [[80, 172], [36, 160]], [[80, 184], [44, 204]], [[80, 194], [40, 236]]],
  fins: [[[118, 202], [104, 230]], [[140, 204], [132, 244]], [[164, 204], [168, 266]], [[182, 202], [186, 240]]],
  pect: [[[232, 150], [210, 200]], [[240, 152], [222, 214]], [[248, 160], [240, 200]]],
};
const rays = (k) => RAYS[k].map(([[x0, y0], [x1, y1]]) => glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 2.4], [x1, y1, 0]], '#c8781a', 0.55)
  + glint([[x0 + 2, y0 - 1, 0], [(x0 + x1) / 2 + 2.4, (y0 + y1) / 2 - 1, 1.4], [x1 + 2, y1 - 1, 0]], '#ffe8a0', 0.6)).join('');

// ---------- dégradés ----------
const defs = [
  rad('g-eye', 0.4, 0.62, 0.7, [[0, '#fff0a0'], [0.4, '#f8b02a'], [0.8, '#e0701a'], [1, '#a83a10']], false),
  rad('g-glow', 0.5, 0.5, 0.5, [[0, '#ffffff'], [0.35, '#e8faff'], [0.6, '#7ad4ff', 0.75], [1, '#2a9ae8', 0]], false),
  `<g id="p-mat">${PAINT_SRC}</g>`,
].join('');

// ---------- la tête : œil, sourcil, gueule (nets, par-dessus les aplats) ----------
const HEAD = oval(261, 79, 23, 18.5, '#fbfaf0') + dot(263, 80, 17, '#8a3410') + dot(263.4, 79.6, 15.6, 'url(#g-eye)') + dot(267, 80, 8.6, '#1c0a04')
  + dot(259, 74, 3, '#ffffff') + dot(275, 85, 1.5, '#ffffff', 0.9)
  + `<g class="a-blink" opacity="0">${oval(261, 79, 25, 20, TONES.blanc.base)}${line('M238 82 Q261 92 285 80', '#22281c', 2.6)}</g>`
  // le sourcil vert sombre, froncé vers la gueule
  + cel(sm('232,56 258,55 287,60 287,70 270,67 258,66 234,65'), TONES.vert, 3, 1.6)
  // la gueule : l'intérieur mauve, une petite langue, les dents, le pli de la joue
  + shape(MOUTH, '#5a2a3c') + shape(sm('300,78 294,96 302,104 306,92'), '#a8506a', 0.8)
  + shape('M291 104L295 109L298 104Z', '#ffffff') + shape('M297 105L300 110L303 105Z', '#ffffff')
  + glint([[252, 112, 0], [268, 117, 1.8], [282, 114, 0]], '#22281c', 0.7)
  // le bout du museau, vert-de-gris, et son reflet
  + shape(sm('290,36! 312,33! 309,52 298,62'), '#6c8a78', 0.85) + glint([[296, 38, 0], [306, 37, 1.6], [310, 46, 0]], '#d4f0e0', 0.8);

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color = '#14140e', o = 0.4) => ({ on, dx, dy, color, o });
const fin = (id, cls, d, k) => ({ id, cls, d, body: use(id, TONES.or.base) + clip(id, PAINT + rays(k)) });
const parts = [
  fin('tail', 'a-tail', TAIL, 'tail'),
  fin('dorsal', 'a-dorsal', DORSAL, 'dorsal'),
  fin('fins', 'a-fins', FINS, 'fins'),
  { id: 'body', cls: 'a-body', d: BODY, shadow: [sh(['tail', 'dorsal', 'fins'], -3, 5)], body: use('body', TONES.blanc.base) + clip('body', PAINT
    // le ventre plus clair, le dos à l'ombre, un long reflet sur le haut du corps
    + glint([[120, 98, 0], [190, 66, 3], [260, 46, 3], [300, 40, 0]], '#ffffff', 0.6)
    + glint([[96, 190, 0], [150, 198, 4], [200, 194, 0]], '#8a8e78', 0.45)
    + HEAD) },
  { id: 'pect', cls: 'a-pect', d: PECT, shadow: [sh(['body'], -3, 5)], body: cel(PECT, TONES.or, 5, 2.4) + clip('pect', rays('pect')
    + glint([[206, 202, 0], [214, 212, 2], [224, 222, 0]], TONES.violet.base, 0.7)) },
  // la boule d'eau qui brille (sans contour)
  { id: 'glow', free: true, d: 'M-900 -900h1v1z', body: `<g class="a-glow">${dot(GLOW[0], GLOW[1], 34, 'url(#g-glow)')}${dot(GLOW[0], GLOW[1], 11, '#ffffff', 0.95)}</g>` },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : la queue bat, les nageoires ondulent, le corps flotte, la boule d'eau palpite, il cligne. Attaque (classe
// « atk », 0,75 s) : il se cabre puis crache : la boule d'eau file vers l'ennemi et s'éteint, puis en revient une neuve.
const PIV = { tail: [86, 172], dorsal: [118, 104], fins: [150, 200], pect: [238, 148], body: [190, 140], glow: [334, 39] };
const IDLE = {
  'a-tail': ['tail', 'tail .8s ease-in-out infinite alternate'],
  'a-dorsal': ['dorsal', 'dorsal 1.4s ease-in-out infinite alternate'],
  'a-fins': ['fins', 'fins 1.2s ease-in-out infinite alternate'],
  'a-pect': ['pect', 'pect .9s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-root{transform-origin:190px 200px;animation:float 2.4s ease-in-out infinite alternate}
.a-glow{transform-origin:${PIV.glow[0]}px ${PIV.glow[1]}px;animation:glow 1.1s ease-in-out infinite alternate}
.a-blink{animation:blink 4.2s linear infinite}
@keyframes float{from{transform:none}to{transform:translate(0,-4px) rotate(-1deg)}}
@keyframes tail{from{transform:rotate(-7deg)}to{transform:rotate(6deg)}}
@keyframes dorsal{from{transform:rotate(-2deg)}to{transform:rotate(3deg)}}
@keyframes fins{from{transform:rotate(-3deg)}to{transform:rotate(4deg)}}
@keyframes pect{from{transform:rotate(-8deg)}to{transform:rotate(6deg)}}
@keyframes glow{from{transform:scale(.92);opacity:.85}to{transform:scale(1.08);opacity:1}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
.atk .a-root{animation:float 2.4s ease-in-out infinite alternate,root-atk .75s ease-in-out;animation-composition:replace,add}
.atk .a-glow{animation:glow-atk .75s ease-in}
${atk('a-tail', 'tail-atk')}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-8px,6px) rotate(-6deg)}46%{transform:translate(10px,-6px) rotate(4deg)}64%{transform:translate(6px,-2px) rotate(2deg)}100%{transform:none}}
@keyframes tail-atk{0%{transform:none}30%{transform:rotate(14deg)}46%{transform:rotate(-16deg)}100%{transform:none}}
@keyframes glow-atk{0%{transform:none;opacity:1}40%{transform:scale(1.25);opacity:1}60%{transform:translate(30px,-12px) scale(.9);opacity:1}74%{transform:translate(50px,-20px) scale(.5);opacity:0}86%{transform:scale(.2);opacity:0}100%{transform:none;opacity:1}}
`.replace(/\n/g, '');

function svg(anime = true) {
  const s = figure({ master: SIL, w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'bayou-3', w: W, h: H, pad: PAD, foot: [170, 272], svg };
