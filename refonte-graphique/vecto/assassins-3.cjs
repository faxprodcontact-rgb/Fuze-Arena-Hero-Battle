// Sable (assassins-3), héroïne Légendaire : une déesse lionne debout, tournée vers la droite, derrière elle un grand
// disque solaire ; tête de lionne à la coiffe sombre qui tombe sur les épaules, cobra d'or au front, deux grands yeux
// d'ambre fardés, museau clair ; large collier turquoise et or, haut et jupe de lin blanc, ceinture d'or, tablier d'or
// à pointes ; cape lie-de-vin ; elle tient en éventail trois lames d'or en forme de feuille.
// DESSINÉE (et non plus décalquée, demande du propriétaire du 23/11) : chaque pièce a sa couleur franche et son propre
// relief (dégradé, ombre franche en bas à gauche, liseré clair en haut à droite) et porte son ombre sur les pièces de
// derrière, pour que la fourrure, le lin, l'or et la turquoise se distinguent. La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');
const { sm, rib, glint, cel, almond, ellipse, shiftPath } = require('./formes.cjs');
// la tête (et sa coiffe) posée plus en avant sur le corps
const HD = [22, 4];

const W = 532, H = 566, PAD = 44;

// ---------- couleurs ----------
const FUR = { hi: '#ffe0a8', base: '#e3a24e', sh: '#b8742e', deep: '#84501e' };
const LIGHT = { hi: '#fffaf0', base: '#fbe6c4', sh: '#e6c08e', deep: '#c49a66' };
const MANE = { hi: '#9a6a4c', base: '#5a3424', sh: '#3a2016', deep: '#22120a' };
const LINEN = { hi: '#ffffff', base: '#f6f0e4', sh: '#d8ccb6', deep: '#aa9c86' };
const GOLD = { hi: '#fff6c0', base: '#f6c446', sh: '#c8841e', deep: '#8a5414' };
const TURQ = { hi: '#9cf0ee', base: '#2eb0bc', sh: '#1a7888', deep: '#0e4a56' };
const CAPE = { hi: '#c45478', base: '#86284c', sh: '#5a1632', deep: '#360a1c' };
const SH = '#2a1008';

// ---------- outils ----------
const lock = (pts, color, o, w = 4) => glint(pts.map(([x, y], i) => [x, y, i === 0 || i === pts.length - 1 ? 0 : w]), color, o);
const relief = (d, grad, pal, w = 7, hw = 3) => `<path d="${d}" fill="url(#${grad})"/>` + cel(d, { ...pal, base: 'none' }, w, hw);
const ell = ellipse;

// ---------- les formes ----------
// ---------- la tête, relevée sur deux gros plans quadrillés de l'original ----------
// le contour de la tête : le crâne (arrondi en haut, sans disque), la grande oreille ronde à gauche, la petite à droite,
// le front, l'arête du museau, le nez, la mâchoire ; à gauche il suit la joue (la coiffe sombre est un morceau derrière)
const HEAD = sm('136,172 134,150 146,132 166,124 186,128 204,120 230,112 258,108 286,110 306,118 314,132! 320,124 334,118 346,124 352,140 352,160 368,176 386,196 402,214 412,234 414,250 408,270 402,288 392,300 386,318 368,330 336,334 304,328 282,312 258,302 228,298 206,292 192,280 186,262 188,240 194,218 196,200 172,198 148,194');
const EAR_L = sm('134,170 136,146 150,130 170,124 192,132 206,150 204,178 196,198 160,198 142,190');
const EAR_L_IN = sm('150,148 166,138 188,146 196,166 190,186 170,190 154,178');
const EAR_R = sm('314,140 324,126 336,120 346,128 350,146 342,158 320,158');
const EAR_R_IN = sm('324,142 331,130 340,130 344,144 336,152 326,152');
// la coiffe sombre : elle part sous la grande oreille, couvre la nuque et passe sous la mâchoire jusqu'au collier
const MANE_L = sm('148,194 198,196 194,218 189,240 187,262 192,280 206,292 222,300 230,318 206,322 176,318 140,318! 118,310 100,312! 104,296 98,276! 106,262 102,244! 114,232 116,214! 130,204!');
// la joue lointaine, plus sombre, entre l'arête du museau et le bord droit de la tête
const RUFF = sm('386,192 400,206 410,224 414,244 412,264 404,280! 400,262 396,244 390,226 384,208');
// le museau : le coussinet clair de la lèvre du haut, la mâchoire claire, le nez, l'arête claire du chanfrein
const MUZZLE = sm('298,262 318,252 340,250 358,256 372,262 388,262 398,268 394,282 372,290 344,292 318,288 302,280');
const JAW = sm('306,292 340,296 372,294 394,286 400,300 390,316 362,328 332,330 310,322 300,306');
const NOSE = sm('340,246 358,240 378,238 390,243 388,254 376,260 358,258 344,254');
// le bas du visage clair : de la joue gauche (sous l'œil) jusqu'au menton
const CHEEK = sm('194,256 222,246 254,250 284,258 300,272 304,292 300,318 276,316 250,306 224,300 204,290 192,274');
const BRIDGE = sm('318,196 336,206 352,222 364,236 352,240 338,228 322,212');
const COBRA = sm('296,108 306,116 316,132 314,150 306,164 304,180! 298,182! 292,164 282,150 278,132 286,116');
const COLLAR = sm('196,318 240,312 300,316 360,312 404,320 410,340 384,362 340,376 300,380 258,376 216,362 192,340');
const COLLAR_IN = sm('214,326 252,322 300,326 350,322 392,328 378,346 340,360 300,364 260,360 222,346');
const TORSO = sm('204,330 300,322 396,330 404,360 388,404 300,412 214,404 198,362');
const BODICE = sm('226,362 266,356 300,366 336,356 376,362 382,400 300,410 220,400');
const BELT = sm('218,398 300,406 384,398 388,420 300,428 214,420');
const SKIRT = sm('214,418 300,426 388,418 398,470 404,520 300,530 198,520 204,470');
const APRON = sm('262,424 340,424 342,500 334,512! 326,500 318,514! 310,500 300,516! 290,500 282,514! 274,500 266,512! 258,500');
const LEG_L = rib([[248, 516, 44], [244, 538, 40], [240, 552, 38]]);
const LEG_R = rib([[350, 516, 44], [356, 538, 40], [360, 552, 38]]);
const PAW_L = sm('204,548 230,540 262,542 274,556 268,566! 206,566! 198,558');
const PAW_R = sm('330,548 358,540 390,542 402,556 396,566! 334,566! 326,558');
const CAPE_D = sm('214,334 176,352 132,392 88,440 52,478! 92,476 80,500! 120,492 128,514! 160,496 196,470 222,430 226,380');
const TAIL_D = rib([[226, 500, 15], [176, 516, 13], [124, 512, 11], [94, 494, 8], [88, 476, 0]]);
const ARM_B = rib([[214, 344, 42], [186, 384, 36], [188, 420, 32]]);
const FIST_B = sm('166,416 180,404 200,402 214,412 216,432 206,446 186,448 170,440');
const ARM_F = rib([[386, 344, 40], [412, 364, 34], [424, 372, 30]]);
const FIST_F = sm('408,360 420,350 438,350 452,360 452,380 440,392 422,394 410,384');
// les trois lames d'or en feuille, du poing vers la pointe, et le manche
const BLADES = [[[432, 360, 6], [440, 330, 13], [452, 290, 12], [462, 250, 0]], [[440, 362, 6], [462, 340, 14], [494, 304, 12], [518, 276, 0]],
  [[444, 368, 6], [470, 362, 14], [504, 352, 11], [528, 344, 0]]];
const HILT = rib([[430, 386, 8], [410, 404, 7], [392, 420, 0]]);

// ---------- dégradés ----------
const defs = [
  lin('g-fur', 0, 0, 0, 1, [[0, '#f2be6c'], [0.55, FUR.base], [1, FUR.sh]], false),
  lin('g-light', 0, 0, 0, 1, [[0, '#fff4e0'], [1, LIGHT.base]], false),
  lin('g-mane', 0, 0, 0, 1, [[0, MANE.hi], [0.4, MANE.base], [1, MANE.sh]], false),
  lin('g-linen', 0, 0, 0, 1, [[0, '#ffffff'], [0.6, LINEN.base], [1, LINEN.sh]], false),
  lin('g-gold', 0, 0, 0, 1, [[0, '#ffe88a'], [0.5, GOLD.base], [1, '#d8922c']], false),
  lin('g-turq', 0, 0, 0, 1, [[0, '#66d8dc'], [0.5, TURQ.base], [1, TURQ.sh]], false),
  lin('g-cape', 1, 0, 0, 1, [[0, CAPE.hi], [0.4, CAPE.base], [1, CAPE.deep]], false),
  lin('g-blade', 0, 0, 1, 1, [[0, '#fff6c0'], [0.4, '#f8d050'], [1, '#c88a20']], false),
  rad('g-sun', 0.6, 0.32, 0.8, [[0, '#fff0b0'], [0.3, '#ffb848'], [0.7, '#f27a22'], [1, '#c85414']], false),
  rad('g-iris', 0.45, 0.4, 0.75, [[0, '#fff0a0'], [0.4, '#e8a030'], [1, '#8a4a10']], false),
].join('');

// ---------- le visage : deux yeux pareils, fardés, de part et d'autre du nez ----------
const EL = almond(262, 222, 56, 26, -1, 6), ER = almond(351, 212, 34, 20, 1, 4.6);
function eye(cx, cy, r, A) {
  const id = `c-se${cx}`;
  return `<clipPath id="${id}"><path d="${A.white}"/></clipPath><path d="${A.white}" fill="#fffaf0"/><g clip-path="url(#${id})">`
    + dot(cx, cy, r, 'url(#g-iris)') + oval(cx + 1, cy, r * 0.3, r * 0.7, '#1a0a04') + dot(cx - r * 0.35, cy - r * 0.4, r * 0.28, '#ffffff') + dot(cx + r * 0.4, cy + r * 0.35, r * 0.12, '#ffffff', 0.9)
    + `<path d="M${cx - 40} ${cy - 30}L${cx + 40} ${cy - 30}L${cx + 40} ${cy - 4 + A.tilt}L${cx - 40} ${cy - 4 - A.tilt}Z" fill="${FUR.sh}"/></g>` + shape(A.lash, '#1a0c06') + line(A.lower, '#5a2c10', 2, 0.8)
    + `<g class="a-blink" opacity="0"><path d="${A.white}" fill="${FUR.base}" stroke="${FUR.base}" stroke-width="3"/>${line(A.shut, '#1a0c06', 3)}</g>`;
}
EL.tilt = 7; ER.tilt = -5; // la paupière penche vers le nez (regard furieux)
const FACE = eye(268, 224, 13, EL) + eye(353, 213, 9, ER)
  // les sourcils sombres et épais, relevés : le gauche arqué, le droit court au-dessus du petit œil
  + shape(rib([[222, 196, 0], [240, 190, 8], [266, 196, 10], [288, 206, 9], [306, 218, 0]]), '#2a1610') + lock([[232, 192], [258, 191], [282, 199]], '#6a4a3a', 0.8, 1.6)
  + shape(rib([[378, 190, 0], [364, 192, 7], [348, 199, 7], [334, 210, 0]]), '#2a1610')
  // les plis du nez froncé
  + lock([[338, 226], [346, 232], [352, 240]], FUR.deep, 0.6, 1.6) + lock([[348, 222], [356, 228], [362, 236]], FUR.deep, 0.5, 1.4)
  // le bas du visage clair, l'arête claire du museau, la joue lointaine plus sombre
  + `<path d="${CHEEK}" fill="${FUR.hi}" opacity="0.35"/>`
  + `<path d="${BRIDGE}" fill="${FUR.hi}" opacity="0.7"/>` + `<path d="${RUFF}" fill="#9a6438"/>` + cel(RUFF, { hi: '#c88a52', base: 'none', sh: MANE.base }, 3, 1.6)
  + lock([[392, 212], [404, 236], [406, 260]], '#d8a060', 0.6, 2)
  // le museau clair et la mâchoire, le nez, la bouche, les points des moustaches
  + `<path d="${JAW}" fill="${LIGHT.sh}"/>` + cel(JAW, { hi: LIGHT.base, base: 'none', sh: LIGHT.deep }, 4, 2)
  + `<path d="${MUZZLE}" transform="translate(-2 3)" fill="${FUR.deep}" opacity="0.3"/>` + `<path d="${MUZZLE}" fill="url(#g-light)"/>` + cel(MUZZLE, { ...LIGHT, base: 'none' }, 3, 1.6)
  + cel(NOSE, { hi: '#c87a5a', base: '#7a3a26', sh: '#3a1a10' }, 2.4, 1.4) + oval(372, 243, 6, 2, '#ffffff', 0.55, -6)
  + line('M296 274 Q300 286 310 290 Q336 296 360 290 Q372 282 384 284 Q392 286 398 280', '#2a140a', 2.8)
  + shape('M364 288 L370 302 L376 287 Z', '#fbf3e4') + shape('M364 288 L370 302 L368 288 Z', '#d8c6ae') + line('M318 300 Q340 306 362 300', LIGHT.deep, 2, 0.7)
  + [[318, 264], [328, 270], [338, 264], [322, 276], [334, 278]].map(([x, y]) => dot(x, y, 1.9, '#7a4a28', 0.85)).join('');

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx = -4, dy = 6, o = 0.42) => ({ on, dx, dy, color: SH, o });
const parts = [
  { id: 'cape', cls: 'a-cape', d: CAPE_D, body: relief(CAPE_D, 'g-cape', CAPE, 7, 3) + lock([[208, 352], [150, 400], [96, 456]], CAPE.hi, 0.5, 4) + lock([[218, 400], [170, 450], [130, 490]], CAPE.deep, 0.5, 4) },
  { id: 'tail', cls: 'a-tail', d: TAIL_D + ell(86, 470, 12, 14), shadow: [sh(['cape'])], body: relief(TAIL_D, 'g-fur', FUR, 4, 2) + relief(ell(86, 470, 12, 14), 'g-mane', MANE, 3, 1.6) },
  { id: 'legs', cls: 'a-body', d: LEG_L + LEG_R + PAW_L + PAW_R, shadow: [sh(['cape', 'tail'])], body: relief(LEG_L, 'g-fur', FUR, 5, 2.4) + relief(LEG_R, 'g-fur', FUR, 5, 2.4)
    + relief(PAW_L, 'g-fur', FUR, 5, 2.4) + relief(PAW_R, 'g-fur', FUR, 5, 2.4)
    + [[218, 556], [236, 558], [254, 556], [344, 556], [362, 558], [380, 556]].map(([x, y]) => lock([[x, y - 8], [x, y], [x, y + 8]], FUR.deep, 0.7, 1.8)).join('')
    + relief(rib([[226, 532, 0], [244, 534, 7], [266, 532, 0]]), 'g-gold', GOLD, 2, 1) + relief(rib([[334, 532, 0], [354, 534, 7], [376, 532, 0]]), 'g-gold', GOLD, 2, 1) },
  { id: 'skirt', cls: 'a-body', d: SKIRT, shadow: [sh(['legs', 'cape', 'tail'])], body: relief(SKIRT, 'g-linen', LINEN, 7, 3)
    + [[230, 432, 222, 514], [376, 432, 386, 514]].map(([x0, y0, x1, y1]) => lock([[x0, y0], [(x0 + x1) / 2, (y0 + y1) / 2], [x1, y1]], LINEN.sh, 0.7, 4)).join('')
    + `<path d="${APRON}" transform="translate(-2 4)" fill="${SH}" opacity="0.3"/>` + relief(APRON, 'g-gold', GOLD, 5, 2.4)
    + lock([[276, 440], [278, 470], [276, 492]], GOLD.sh, 0.6, 3) + lock([[324, 440], [326, 470], [324, 492]], GOLD.hi, 0.7, 2.4)
    + dot(300, 478, 12, GOLD.deep) + dot(300, 478, 10, '#b02a1c') + dot(303, 474, 3, '#ffb0a0', 0.9) },
  { id: 'torso', cls: 'a-body', d: TORSO, shadow: [sh(['cape', 'skirt'])], body: relief(TORSO, 'g-fur', FUR, 7, 3)
    + relief(BODICE, 'g-linen', LINEN, 5, 2.4) + lock([[300, 372], [300, 388], [300, 404]], LINEN.sh, 0.7, 2.6) },
  { id: 'belt', cls: 'a-body', d: BELT, shadow: [sh(['torso', 'skirt'], -2, 5)], body: relief(BELT, 'g-gold', GOLD, 4, 2)
    + dot(300, 414, 9, GOLD.deep) + dot(300, 414, 7.4, TURQ.base) + dot(302.5, 411.5, 2.4, '#e0ffff', 0.9) },
  // la coiffe sombre, derrière la tête : sous la grande oreille, la nuque, et sous la mâchoire (le collier passe devant)
  { id: 'mane', cls: 'a-head', d: shiftPath(MANE_L, ...HD), shadow: [sh(['torso', 'cape'], -4, 6)], body: `<g transform="translate(${HD})"><path d="${MANE_L}" fill="url(#g-mane)"/>` + cel(MANE_L, { ...MANE, base: 'none' }, 5, 2.4)
    + [[[150, 204], [128, 240], [116, 286]], [[172, 210], [158, 252], [146, 300]], [[186, 290], [204, 302], [216, 314]]].map((h) => lock(h, MANE.hi, 0.55, 3.4)).join('') + '</g>' },
  { id: 'collar', cls: 'a-body', d: COLLAR, shadow: [sh(['torso', 'cape', 'mane'], -3, 6)], body: relief(COLLAR, 'g-gold', GOLD, 5, 2.4)
    + relief(COLLAR_IN, 'g-turq', TURQ, 4, 2)
    + lock([[222, 334], [262, 344], [300, 348], [340, 344], [380, 334]], GOLD.base, 1, 2.6)
    + [[236, 352], [266, 362], [300, 366], [334, 362], [364, 352]].map(([x, y]) => dot(x, y, 4, GOLD.base) + dot(x + 1, y - 1, 1.4, GOLD.hi)).join('') },
  { id: 'armB', cls: 'a-body', d: ARM_B, shadow: [sh(['torso', 'cape', 'collar'])], body: relief(ARM_B, 'g-fur', FUR, 6, 3)
    + relief(rib([[172, 398, 0], [190, 398, 9], [208, 400, 0]]), 'g-gold', GOLD, 2.4, 1.2) },
  { id: 'fistB', cls: 'a-body', d: FIST_B, shadow: [sh(['armB', 'torso', 'skirt'], -3, 5)], body: relief(FIST_B, 'g-fur', FUR, 5, 2.4)
    + [180, 192, 204].map((x) => lock([[x, 414], [x + 0.5, 428], [x, 442]], FUR.deep, 0.8, 2)).join('') },
  { id: 'armF', cls: 'a-arm', d: ARM_F, shadow: [sh(['torso', 'collar', 'mane'])], body: relief(ARM_F, 'g-fur', FUR, 5, 2.4)
    + relief(rib([[400, 350, 0], [408, 360, 8], [414, 372, 0]]), 'g-gold', GOLD, 2.4, 1.2) },
  { id: 'head', cls: 'a-head', d: shiftPath(HEAD, ...HD), shadow: [sh(['mane', 'collar', 'armF'], -4, 7, 0.6)], body: `<g transform="translate(${HD})"><path d="${HEAD}" fill="url(#g-fur)"/>` + cel(HEAD, { ...FUR, base: 'none' }, 7, 3)
    + `<clipPath id="c-headU"><path d="${HEAD}"/></clipPath><g clip-path="url(#c-headU)">` + (''
    +
    // les oreilles : le bord doré, l'intérieur brun ; le front éclairé ; la joue gauche un peu plus claire
    `<path d="${EAR_L}" fill="${FUR.base}"/>` + cel(EAR_L, { ...FUR, base: 'none' }, 4, 2) + `<path d="${EAR_L_IN}" fill="#8e5a3e"/>` + cel(EAR_L_IN, { hi: '#c08058', base: 'none', sh: MANE.sh }, 4, 2)
    + `<path d="${EAR_R_IN}" fill="#8e5a3e"/>`
    + lock([[220, 132], [270, 116], [312, 124]], FUR.hi, 0.7, 6) + lock([[200, 236], [204, 268], [226, 290]], FUR.sh, 0.45, 6)
    + `<path d="${COBRA}" transform="translate(-2 3)" fill="${FUR.deep}" opacity="0.5"/>` + relief(COBRA, 'g-gold', GOLD, 3, 1.6) + dot(298, 148, 4, '#c02818') + dot(299, 146.6, 1.3, '#ffd0c0')
    + FACE) + '</g></g>' },
  { id: 'blades', cls: 'a-arm', d: BLADES.map(rib).join('') + HILT, shadow: [sh(['armF', 'mane', 'head', 'torso'], -3, 5, 0.35)], body: relief(HILT, 'g-gold', GOLD, 2, 1)
    + BLADES.map((b) => shape(rib(b), 'url(#g-blade)') + shape(rib(b.map(([x, y, w]) => [x - w * 0.18, y + w * 0.22, w * 0.5])), GOLD.sh, 0.7)
      + glint(b.map(([x, y, w], i) => [x + w * 0.12, y - w * 0.15, i === 0 || i === b.length - 1 ? 0 : 1.6]), '#ffffff', 0.85)).join('') },
  { id: 'fistF', cls: 'a-arm', d: FIST_F, shadow: [sh(['blades', 'armF'], -3, 5)], body: relief(FIST_F, 'g-fur', FUR, 5, 2.4)
    + [422, 434, 446].map((x) => lock([[x, 356], [x + 0.5, 372], [x, 388]], FUR.deep, 0.8, 2)).join('') },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : elle respire, la tête hoche, le disque solaire palpite, la cape et la queue ondulent, les lames oscillent,
// elle cligne. Attaque (classe « atk », 0,75 s) : elle arme son bras puis lance d'un geste vif les lames vers l'avant
// en bondissant ; retour en garde.
const PIV = { body: [300, 560], sun: [250, 96], head: [300, 330], arm: [386, 350], cape: [214, 340], tail: [226, 500] };
const IDLE = {
  'a-body': ['body', 'body 2s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 2.6s ease-in-out infinite alternate'],
  'a-arm': ['arm', 'arm 1.8s ease-in-out infinite alternate'],
  'a-cape': ['cape', 'cape 2.2s ease-in-out infinite alternate'],
  'a-tail': ['tail', 'tail 1.6s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-root{transform-origin:300px 560px}
.a-blink{animation:blink 4.4s linear infinite}
@keyframes body{from{transform:none}to{transform:translate(0,-2px) scale(1.004,1.008)}}
@keyframes sun{from{transform:scale(1)}to{transform:scale(1.03)}}
@keyframes head{from{transform:none}to{transform:rotate(-1.4deg) translate(0,-1px)}}
@keyframes arm{from{transform:rotate(-2deg)}to{transform:rotate(2deg)}}
@keyframes cape{from{transform:rotate(0deg)}to{transform:rotate(2.4deg)}}
@keyframes tail{from{transform:rotate(-5deg)}to{transform:rotate(4deg)}}
@keyframes blink{0%,93%{opacity:0}94.5%,97%{opacity:1}98.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-head', 'head-atk')}${atk('a-arm', 'arm-atk')}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-8px,2px) rotate(-2deg)}48%{transform:translate(20px,-6px) rotate(2deg)}62%{transform:translate(16px,-2px)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}30%{transform:rotate(-2deg)}48%{transform:rotate(2deg)}100%{transform:none}}
@keyframes arm-atk{0%{transform:none}30%{transform:rotate(-12deg)}48%{transform:rotate(10deg) translate(6px,0)}64%{transform:rotate(5deg)}100%{transform:none}}
`.replace(/\n/g, '');

function svg(anime = true) {
  const s = figure({ w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'assassins-3', w: W, h: H, pad: PAD, foot: [300, 564], svg };
