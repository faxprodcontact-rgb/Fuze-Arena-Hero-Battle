// Sable (assassins-3), héroïne Légendaire : une déesse lionne debout, tournée vers la droite, derrière elle un grand
// disque solaire ; tête de lionne à la coiffe sombre qui tombe sur les épaules, cobra d'or au front, deux grands yeux
// d'ambre fardés, museau clair ; large collier turquoise et or, haut et jupe de lin blanc, ceinture d'or, tablier d'or
// à pointes ; cape lie-de-vin ; elle tient en éventail trois lames d'or en forme de feuille.
// DESSINÉE (et non plus décalquée, demande du propriétaire du 23/11) : chaque pièce a sa couleur franche et son propre
// relief (dégradé, ombre franche en bas à gauche, liseré clair en haut à droite) et porte son ombre sur les pièces de
// derrière, pour que la fourrure, le lin, l'or et la turquoise se distinguent. La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');
const { sm, rib, glint, cel, almond, ellipse } = require('./formes.cjs');

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
const SUN = [250, 96, 70];
const MANE_D = sm('178,176 222,140 290,128 352,140 396,180 410,240 404,306 388,346! 356,334 320,342 280,344 240,340 204,334 176,346! 166,300 162,240');
// la tête de lionne d'une seule forme (oreilles et museau compris), comme avant ; le museau clair est peint dedans
const HEAD = sm('413,234 408,222 391,208 388,201 373,188 368,177 352,163 353,151 351,142 343,126 335,119 327,120 318,126 307,128 298,120 287,115 278,128 267,137 240,138 212,141 196,131 180,126 165,125 145,130 140,135 134,148 133,166 136,177 144,189 133,207 140,250 170,288 205,300 249,308 300,310 340,310 377,305 381,303 388,300 397,289 408,281 411,273 410,252 414,245');
const MUZZLE = sm('318,250 344,240 374,244 402,254 410,270 396,286 362,292 332,288 316,272');
const COBRA = sm('294,132 302,118 312,124 316,144 310,164 302,170 294,160 290,146');
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
const EL = almond(262, 218, 48, 28, -1, 5.4), ER = almond(334, 218, 48, 28, 1, 5.4);
function eye(cx, cy, r, A) {
  const id = `c-se${cx}`;
  return `<clipPath id="${id}"><path d="${A.white}"/></clipPath><path d="${A.white}" fill="#fffaf0"/><g clip-path="url(#${id})">`
    + dot(cx, cy, r, 'url(#g-iris)') + oval(cx + 1, cy, r * 0.3, r * 0.7, '#1a0a04') + dot(cx - r * 0.35, cy - r * 0.4, r * 0.28, '#ffffff') + dot(cx + r * 0.4, cy + r * 0.35, r * 0.12, '#ffffff', 0.9)
    + `<rect x="${cx - 32}" y="${cy - 24}" width="64" height="11" fill="#6a3a10" opacity="0.2"/></g>` + shape(A.lash, '#1a0c06') + line(A.lower, '#5a2c10', 2, 0.8)
    + `<g class="a-blink" opacity="0"><path d="${A.white}" fill="${FUR.base}" stroke="${FUR.base}" stroke-width="3"/>${line(A.shut, '#1a0c06', 3)}</g>`;
}
const FACE = eye(265, 220, 12, EL) + eye(337, 220, 12, ER)
  // les sourcils sombres, le même de chaque côté, froncés vers le nez
  + cel(rib([[236, 192, 0], [252, 184, 5], [274, 186, 5], [288, 196, 0]]), MANE, 2.4, 1.4)
  + cel(rib([[312, 196, 0], [326, 186, 5], [348, 184, 5], [364, 192, 0]]), MANE, 2.4, 1.4)
  // le museau clair, le nez de lionne, la bouche, les points des moustaches
  + `<path d="${MUZZLE}" fill="url(#g-light)"/>` + cel(MUZZLE, { ...LIGHT, base: 'none' }, 4, 2)
  + cel(sm('374,230 390,227 402,233 401,244 390,249 378,245'), { hi: '#c8906a', base: '#8a4a24', sh: '#5a2c12' }, 2.4, 1.4)
  + line('M390 249 L390 262', '#5a2c12', 2.2) + line('M352 276 Q372 282 390 262 Q398 274 408 270', '#5a2c12', 2.4)
  + [[342, 258], [350, 264], [338, 268]].map(([x, y]) => dot(x, y, 1.8, '#8a5a30', 0.8)).join('');

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx = -4, dy = 6, o = 0.42) => ({ on, dx, dy, color: SH, o });
const parts = [
  { id: 'sun', cls: 'a-sun', d: ell(SUN[0], SUN[1], SUN[2], SUN[2]), body: dot(SUN[0], SUN[1], SUN[2], '#f2c040') + dot(SUN[0], SUN[1], SUN[2] - 5, 'url(#g-sun)')
    + `<circle cx="${SUN[0]}" cy="${SUN[1]}" r="${SUN[2] - 12}" fill="none" stroke="#fff4b0" stroke-width="3" opacity="0.5"/>` + lock([[204, 52], [250, 34], [296, 52]], '#ffffff', 0.7, 4) },
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
  { id: 'collar', cls: 'a-body', d: COLLAR, shadow: [sh(['torso', 'cape'], -3, 6)], body: relief(COLLAR, 'g-gold', GOLD, 5, 2.4)
    + relief(COLLAR_IN, 'g-turq', TURQ, 4, 2)
    + lock([[222, 334], [262, 344], [300, 348], [340, 344], [380, 334]], GOLD.base, 1, 2.6)
    + [[236, 352], [266, 362], [300, 366], [334, 362], [364, 352]].map(([x, y]) => dot(x, y, 4, GOLD.base) + dot(x + 1, y - 1, 1.4, GOLD.hi)).join('') },
  { id: 'armB', cls: 'a-body', d: ARM_B, shadow: [sh(['torso', 'cape', 'collar'])], body: relief(ARM_B, 'g-fur', FUR, 6, 3)
    + relief(rib([[172, 398, 0], [190, 398, 9], [208, 400, 0]]), 'g-gold', GOLD, 2.4, 1.2) },
  { id: 'fistB', cls: 'a-body', d: FIST_B, shadow: [sh(['armB', 'torso', 'skirt'], -3, 5)], body: relief(FIST_B, 'g-fur', FUR, 5, 2.4)
    + [180, 192, 204].map((x) => lock([[x, 414], [x + 0.5, 428], [x, 442]], FUR.deep, 0.8, 2)).join('') },
  { id: 'mane', cls: 'a-head', d: MANE_D, shadow: [sh(['sun', 'torso', 'collar', 'cape'], -4, 7)], body: relief(MANE_D, 'g-mane', MANE, 7, 3)
    + lock([[184, 220], [178, 280], [190, 330]], MANE.hi, 0.6, 4) + lock([[398, 220], [402, 280], [392, 330]], MANE.hi, 0.5, 4) },
  { id: 'head', cls: 'a-head', d: HEAD, shadow: [sh(['mane', 'sun', 'collar'], -4, 6)], body: `<path d="${HEAD}" fill="url(#g-fur)"/>` + cel(HEAD, { ...FUR, base: 'none' }, 8, 3) + clip('head',
    // l'intérieur des oreilles, la coiffe sombre derrière la joue et sous la mâchoire, le front éclairé
    dot(167, 160, 20, MANE.base) + dot(169, 163, 13, MANE.sh) + dot(340, 142, 10, MANE.base)
    + cel(sm('100,200 132,188 160,200 172,236 168,280 150,304 126,304 104,288 96,250 98,220'), MANE, 5, 2.4)
    + cel(sm('370,196 392,206 408,234 414,264 404,290 384,284 378,252 370,222'), MANE, 4, 2)
    + lock([[230, 148], [280, 136], [330, 140]], FUR.hi, 0.7, 5) + lock([[180, 236], [196, 276], [226, 300]], FUR.sh, 0.5, 6)
    // le cobra d'or au front, sa gemme rouge
    + `<path d="${COBRA}" transform="translate(-2 3)" fill="${FUR.deep}" opacity="0.5"/>` + relief(COBRA, 'g-gold', GOLD, 3, 1.6) + dot(303, 152, 3.6, '#c02818') + dot(304, 150.6, 1.2, '#ffd0c0')
    + FACE) },
  { id: 'armF', cls: 'a-arm', d: ARM_F, shadow: [sh(['torso', 'collar', 'mane'])], body: relief(ARM_F, 'g-fur', FUR, 5, 2.4)
    + relief(rib([[400, 350, 0], [408, 360, 8], [414, 372, 0]]), 'g-gold', GOLD, 2.4, 1.2) },
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
  'a-sun': ['sun', 'sun 2.4s ease-in-out infinite alternate'],
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
