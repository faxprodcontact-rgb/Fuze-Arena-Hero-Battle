// Le carillon (epouvantails-4), monstre des Épouvantails : redessiné par le code d'après le dessin d'origine, dans le
// même cadre (247 × 442, mêmes proportions, même pose) : un carillon à vent pendu à un crochet d'acier ; un chapeau en
// cloche vert-de-gris (dôme, couture rouillée, large bord) dont le dessous sombre cache deux yeux jaunes furieux ;
// dessous pendent quatre tubes d'argent (deux finissent par un battant) et, au milieu, une tige qui porte une boule de
// bronze et une voile blanche à bande rouge, fendue en queue d'aronde.
// DÉCALQUÉ : silhouette exacte (master), crochet, chapeau et tubes découpés dans la silhouette (outils/decoupe.py), yeux
// relevés sur l'original (outils/zone.py), boule, tige et voile lues sur gros plans quadrillés.
// La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');
const { sm, glint } = require('./formes.cjs');

const W = 247, H = 442, PAD = 40;

// ---------- couleurs ----------
const TEAL = { hi: '#b4e8cc', lite: '#7cc4aa', base: '#4e9484', shade: '#2e5c58', deep: '#183634' };
const STEEL = { hi: '#e4e8f0', lite: '#a8acb6', base: '#70747c', shade: '#46484f', deep: '#24262b' };
const SILVER = { hi: '#f6f8fc', lite: '#d4d8e0', base: '#a0a4ac', shade: '#6a6e76', deep: '#3c3e44' };
const SH = { dark: '#0c1414' };

// ---------- les formes relevées sur l'original ----------
const HOOK = sm('153,10 143,5 132,5 124,9 116,16 111,31 113,46 104,52 101,60 103,69 109,68 116,72 112,78 112,83 99,86 111,89 141,89 149,86 146,85 141,82 141,77 138,73 141,70 141,61 137,53 125,44 125,31 128,26 135,21 140,21 145,27 146,41 149,43 159,42 160,22');
const CAP = sm('5,157 13,164 21,163 29,168 35,169 41,175 43,179 44,182 47,185 50,195 54,197 194,197 204,176 211,169 225,163 230,159 238,157 244,148 244,143 241,139 240,133 236,132 225,120 199,101 172,89 154,85 106,84 84,88 69,93 45,107 6,143');
// les tubes : la silhouette coupée par une boîte (ils filent sous le bord du chapeau)
const TUBES = [
  { id: 't1', x0: 41, x1: 71, y0: 201, y1: 313, d: sm('74,186 47,186 50,195 54,199 52,201 41,201 41,312 45,314 48,319 46,336 50,344 53,344 54,332 58,326 56,317 59,315 69,314 71,310 72,204 66,201 64,197 74,197'), stub: [51, 314, 344] },
  { id: 't2', x0: 77, x1: 107, y0: 200, y1: 358, d: sm('74,186 74,197 84,198 87,200 78,204 77,212 78,262 80,267 78,357 80,360 99,358 100,364 108,364 108,186') },
  { id: 't3', x0: 142, x1: 170, y0: 201, y1: 371, d: sm('174,186 141,186 141,199 150,199 152,201 143,207 144,239 143,275 141,277 141,376 144,370 148,372 167,371 169,368 169,249 171,203 166,199 169,197 174,197') },
  { id: 't4', x0: 175, x1: 203, y0: 203, y1: 321, d: sm('174,186 174,197 184,196 186,201 183,204 177,205 174,210 176,321 182,324 190,325 188,338 192,339 196,335 196,325 203,320 203,204 194,203 192,201 199,186'), stub: [191, 322, 339] },
];
// les yeux jaunes (relevés), le haut coupé en biais : le regard furieux
const EYE_L = sm('72,152! 97,163 106,167 112,170! 90,180 80,182 74,171');
const EYE_R = sm('178,159! 178,166 173,180 165,182 147,171! 164,164');
// la voile : bord haut, flanc droit, pointe droite, l'encoche, pointe gauche, flanc gauche
const SAIL = sm('104,321 126,319 147,321 146,331 142,350 137,375 133,400 133,415 138,432! 125,421 114,411! 104,424 89,437! 91,405 95,380 100,350 103,331');
const BALL = [126, 288, 21];
const PEND = `M119.5 184H127.5V270H119.5Z${`M${BALL[0] - BALL[2]} ${BALL[1]}a${BALL[2]} ${BALL[2]} 0 1 0 ${2 * BALL[2]} 0a${BALL[2]} ${BALL[2]} 0 1 0 ${-2 * BALL[2]} 0Z`}M116 262H136V273H116ZM119 306H133V324H119Z${SAIL}`;

// ---------- dégradés ----------
const defs = [
  lin('g-dome', 190, 84, 70, 150, [[0, TEAL.lite], [0.5, TEAL.base], [1, TEAL.shade]]),
  lin('g-steel', 1, 0, 0, 1, [[0, STEEL.lite], [0.5, STEEL.base], [1, STEEL.deep]], false),
  lin('g-tube', 0, 0, 1, 0, [[0, SILVER.deep], [0.22, SILVER.shade], [0.5, SILVER.base], [0.72, SILVER.hi], [0.86, SILVER.lite], [1, SILVER.shade]], false),
  lin('g-inner', 0, 146, 0, 190, [[0, '#050a0a'], [1, '#18282a']]),
  lin('g-sail', 0, 0, 1, 0, [[0, '#b8b0a6'], [0.3, '#ece6da'], [0.7, '#fbf8f0'], [1, '#d8d0c4']], false),
  rad('g-eye', 0.7, 0.6, 0.7, [[0, '#fffde0'], [0.4, '#ffe85a'], [1, '#e8901a']], false),
  rad('g-ball', 0.68, 0.3, 0.8, [[0, '#f0eee0'], [0.25, '#b8ae98'], [0.6, '#6a5a44'], [1, '#2a2018']], false),
].join('');

// ---------- un tube d'argent ----------
function tubeBody(t) {
  const { id, x0, x1, y0, y1 } = t, w = x1 - x0;
  return use(id, SILVER.shade) + clip(id,
    // l'attache sombre sous le chapeau, le corps du tube, son cerclage du haut et du bas
    `<rect x="${n((x0 + x1) / 2 - 3)}" y="184" width="6" height="${y0 - 182}" fill="${STEEL.shade}"/>`
    + `<rect x="${x0}" y="${y0}" width="${w}" height="${y1 - y0}" fill="url(#g-tube)"/>`
    + `<rect x="${x0}" y="${y0}" width="${w}" height="6" fill="${SILVER.deep}" opacity="0.55"/>`
    + `<rect x="${x0}" y="${y1 - 6}" width="${w}" height="6" fill="${SILVER.deep}" opacity="0.4"/>`
    // le long reflet du côté de la lumière, quelques taches de ternissure
    + glint([[x0 + w * 0.74, y0 + 10, 0], [x0 + w * 0.76, (y0 + y1) / 2, 3.4], [x0 + w * 0.74, y1 - 10, 0]], '#ffffff', 0.75)
    + oval(x0 + w * 0.35, y0 + (y1 - y0) * 0.3, 2.6, 5, SILVER.shade, 0.35) + oval(x0 + w * 0.3, y0 + (y1 - y0) * 0.72, 2, 4, SILVER.shade, 0.3)
    // le battant qui pend dessous (tubes de bord)
    + (t.stub ? `<rect x="${t.stub[0] - 4}" y="${t.stub[1]}" width="8" height="${t.stub[2] - t.stub[1]}" rx="3" fill="${STEEL.shade}"/>`
      + dot(t.stub[0], t.stub[2] - 5, 4.6, STEEL.deep) + glint([[t.stub[0] + 1.5, t.stub[1] + 2, 0], [t.stub[0] + 2, t.stub[1] + 12, 1.4], [t.stub[0] + 1.5, t.stub[2] - 8, 0]], STEEL.hi, 0.7) : ''));
}

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color = SH.dark, o = 0.45) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'hook', cls: 'a-hook', d: HOOK, body: use('hook', 'url(#g-steel)') + clip('hook',
    // le reflet le long du crochet, la boule du nœud, le collet sur le chapeau
    glint([[114, 40, 0], [116, 22, 2.2], [126, 11, 2.6], [142, 9, 2.4], [154, 16, 1.8], [156, 34, 0]], STEEL.hi, 0.8)
    + dot(128, 51, 5.5, STEEL.base) + dot(129, 50, 3.6, STEEL.lite) + dot(130.5, 48.6, 1.3, '#ffffff', 0.85)
    + dot(129, 64, 9, STEEL.base) + dot(130.5, 62.5, 6.5, STEEL.lite) + dot(133, 59.5, 2.2, '#ffffff', 0.85)
    + glint([[104, 58, 0], [106, 66, 1.6], [110, 70, 0]], STEEL.hi, 0.6)
    + shape(sm('110,76 142,76 146,88 106,88'), STEEL.shade) + glint([[118, 79, 0], [130, 78, 1.6], [140, 80, 0]], STEEL.hi, 0.7)) },
  ...TUBES.map((t) => ({ id: t.id, cls: `a-${t.id}`, d: t.d, body: tubeBody(t) })),
  // la tige, la boule de bronze, la perle et la voile (tout se balance ensemble)
  { id: 'pend', cls: 'a-pend', d: PEND, shadow: [sh(['t2', 't3'], -3, 4, SH.dark, 0.35)], body: clip('pend',
    `<rect x="119.5" y="184" width="8" height="86" fill="#2a1418"/>` + glint([[125, 190, 0], [125.4, 230, 1.4], [125, 266, 0]], '#7a5a5a', 0.8)
    + `<circle cx="${BALL[0]}" cy="${BALL[1]}" r="${BALL[2]}" fill="url(#g-ball)"/>` + oval(133, 279, 6, 3.4, '#ffffff', 0.7, -30)
    + `<rect x="116" y="262" width="20" height="10" rx="3" fill="${STEEL.shade}"/>` + glint([[120, 265, 0], [128, 264, 1.4], [134, 266, 0]], STEEL.hi, 0.7)
    + dot(126, 315, 6, STEEL.deep) + dot(127.5, 313, 2, STEEL.hi, 0.8)
    + `<path d="${SAIL}" fill="url(#g-sail)"/>`
    // l'ombre du flanc gauche, les côtes de la plume (larges et douces), la bande rouge
    + glint([[105, 324, 0], [102, 360, 3.2], [96, 400, 3], [90, 434, 0]], '#b8b0a4', 0.55)
    + glint([[112, 330, 0], [108, 372, 2], [101, 414, 0]], '#d8d0c4', 0.5) + glint([[136, 330, 0], [134, 372, 2.4], [132, 412, 0]], '#ffffff', 0.7)
    + glint([[122, 324, 3.2], [122.6, 360, 3.2], [122, 402, 0]], '#e02a14')
    + glint([[123.6, 330, 0], [124, 362, 1], [123, 395, 0]], '#ff8a6a', 0.7)
    + shape('M118 318H132L130 328H120Z', '#7a1a14')) },
  // le chapeau en cloche : il couvre le haut des tubes et de la tige
  { id: 'cap', cls: 'a-cap', d: CAP, shadow: [sh(['t1', 't2', 't3', 't4', 'pend', 'hook'], -3, 5)], body: use('cap', 'url(#g-dome)') + clip('cap',
    // la lueur du dôme en haut à droite, des coulures claires de vert-de-gris, quelques taches de rouille
    oval(168, 100, 40, 12, TEAL.hi, 0.45, 16)
    + glint([[96, 92, 0], [104, 104, 2.4], [112, 116, 0]], TEAL.hi, 0.5) + glint([[150, 92, 0], [158, 104, 2.2], [170, 114, 0]], TEAL.hi, 0.5)
    + glint([[60, 104, 0], [54, 114, 2], [50, 122, 0]], TEAL.shade, 0.6) + glint([[128, 88, 0], [132, 100, 2], [128, 114, 0]], TEAL.hi, 0.4)
    + glint([[196, 104, 0], [206, 112, 2], [214, 122, 0]], TEAL.hi, 0.45) + glint([[84, 96, 0], [76, 106, 1.8], [72, 116, 0]], TEAL.deep, 0.45) + dot(186, 106, 2.4, '#a86a3a', 0.6) + dot(80, 110, 2, '#a86a3a', 0.55)
    // la couture rouillée et ses rivets
    + shape(sm('40,130 70,121 100,118 130,117 160,118 190,121 210,128 208,133 190,127 160,123 130,122 100,123 70,126 42,134'), '#5a4428')
    + glint([[44, 129, 0], [100, 119.5, 1.4], [160, 119.5, 1.4], [206, 128, 0]], '#d8c098', 0.8)
    + [[60, 125], [90, 121], [120, 120], [150, 120], [180, 123]].map(([x, y]) => dot(x, y, 1.6, '#e8d4b0', 0.85)).join('')
    // le large bord : plus clair dessus, dans l'ombre dessous
    + shape(sm('0,146! 30,136 60,131 100,129 150,129 190,131 220,135 247,140! 247,160! 0,160!'), TEAL.lite, 0.55)
    + shape(sm('0,150! 30,151 70,147 128,145 190,147 220,149 247,146! 247,170! 0,170!'), TEAL.shade)
    // les flancs de la cloche sous le bord, l'intérieur sombre, la lèvre du bas
    + shape(sm('36,148! 214,148! 206,197! 46,197!'), TEAL.shade)
    + glint([[200, 152, 0], [204, 170, 3], [200, 190, 0]], TEAL.lite, 0.55) + glint([[46, 152, 0], [44, 170, 3], [50, 190, 0]], TEAL.deep, 0.7)
    + `<path d="${sm('66,147 128,146 188,147 190,170 188,188! 66,188! 64,170')}" fill="url(#g-inner)"/>`
    + shape(sm('46,184! 128,186 206,184! 204,197! 50,197!'), '#243838') + glint([[54, 186, 0], [128, 187.4, 1.4], [200, 186, 0]], TEAL.base, 0.8)
    // les yeux jaunes, leurs petites pupilles sous le sourcil
    + `<path d="${EYE_L}" fill="url(#g-eye)"/><path d="${EYE_R}" fill="url(#g-eye)"/>`
    + shape('M92 164L101 168L97 172Z', '#3a1a06', 0.85) + shape('M156 168L164 165L160 171Z', '#3a1a06', 0.85)
    + `<g class="a-blink" opacity="0"><path d="${EYE_L}" fill="#0a1212"/><path d="${EYE_R}" fill="#0a1212"/>${line('M76 176 Q92 182 110 172', '#c89a30', 2)}${line('M149 172 Q164 182 176 170', '#c89a30', 2)}</g>`) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : tout le carillon se balance doucement au bout de son crochet, chaque tube oscille à son rythme, la voile
// suit avec du retard, il cligne. Attaque (classe « atk », 0,75 s) : il prend son élan en arrière puis se jette en avant,
// les tubes et la voile volent en tous sens et s'entrechoquent ; tout revient à la pose de repos.
const PIV = { root: [133, 10], hook: [133, 10], t1: [56, 188], t2: [92, 188], t3: [156, 188], t4: [189, 188], pend: [123.5, 188], cap: [125, 150] };
const IDLE = {
  'a-t1': ['t1', 'tube 1.3s ease-in-out infinite alternate'],
  'a-t2': ['t2', 'tube 1.1s ease-in-out -.4s infinite alternate'],
  'a-t3': ['t3', 'tube 1.2s ease-in-out -.8s infinite alternate'],
  'a-t4': ['t4', 'tube 1.4s ease-in-out -.2s infinite alternate'],
  'a-pend': ['pend', 'pend 1.6s ease-in-out -.5s infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-root{transform-origin:${PIV.root[0]}px ${PIV.root[1]}px;animation:sway 3.2s ease-in-out infinite alternate}
.a-blink{animation:blink 4.4s linear infinite}
@keyframes sway{from{transform:rotate(-1.6deg)}to{transform:rotate(1.6deg)}}
@keyframes tube{from{transform:rotate(-2.5deg)}to{transform:rotate(2.5deg)}}
@keyframes pend{from{transform:rotate(-4deg)}to{transform:rotate(4deg)}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
.atk .a-root{animation:sway 3.2s ease-in-out infinite alternate,root-atk .75s ease-in-out;animation-composition:replace,add}
${atk('a-t1', 't-atk')}${atk('a-t2', 't-atk2')}${atk('a-t3', 't-atk')}${atk('a-t4', 't-atk2')}${atk('a-pend', 'pend-atk')}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-6px,0) rotate(-7deg)}50%{transform:translate(14px,-4px) rotate(9deg)}66%{transform:translate(10px,0) rotate(4deg)}100%{transform:none}}
@keyframes t-atk{0%{transform:none}30%{transform:rotate(10deg)}50%{transform:rotate(-16deg)}70%{transform:rotate(8deg)}100%{transform:none}}
@keyframes t-atk2{0%{transform:none}30%{transform:rotate(8deg)}50%{transform:rotate(-12deg)}70%{transform:rotate(10deg)}100%{transform:none}}
@keyframes pend-atk{0%{transform:none}30%{transform:rotate(14deg)}50%{transform:rotate(-22deg)}72%{transform:rotate(10deg)}100%{transform:none}}
`.replace(/\n/g, '');

const SIL = require('./silhouettes/epouvantails-4.json');
function svg(anime = true) {
  const s = figure({ master: SIL, w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'epouvantails-4', w: W, h: H, pad: PAD, foot: [124, 440], svg };
