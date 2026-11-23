// Eldra (mages-8), héroïne Légendaire : une guerrière singe en garde basse, tournée vers la droite ; deux longues plumes
// brunes qui partent du crâne en arcs, bandeau d'or à médaillon, fourrure brune, grand masque clair au museau rond,
// sourcils froncés, deux grands yeux bruns, petit sourire en coin ; cape rouge, tunique rouge à plastron d'or, ceinture
// sombre, jupe d'or ; elle tient en travers un long bâton d'or à deux mains ; la queue s'enroule derrière elle ; bottes
// à revers de fourrure.
// DESSINÉE (et non plus décalquée, demande du propriétaire du 23/11) : chaque pièce est une forme simple et nette, avec
// son propre relief (un dégradé, une ombre franche en bas à gauche, un liseré clair en haut à droite) et une ombre portée
// sur les pièces de derrière, pour que corps, vêtements et accessoires se distinguent. La lumière vient d'en haut à droite.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');
const { sm, rib, glint, cel, almond, ellipse } = require('./formes.cjs');

const W = 580, H = 619, PAD = 44;

// ---------- couleurs ----------
const FUR = { hi: '#d6a07c', base: '#9a6446', sh: '#70442e', deep: '#4a2a1c' };
const PEACH = { hi: '#fff6ea', base: '#ffdcb4', sh: '#eab486', deep: '#c98c62' };
const RED = { hi: '#ff8a76', base: '#d8443a', sh: '#9e2826', deep: '#661818' };
const CAPE = { hi: '#f0705e', base: '#b8302a', sh: '#7e1c1c', deep: '#4e1012' };
const GOLD = { hi: '#fff4b8', base: '#f4b843', sh: '#c47c22', deep: '#80501a' };
const BOOT = { hi: '#b88a68', base: '#6a4430', sh: '#4a2c1e', deep: '#2a1810' };
const DARK = { hi: '#6a5254', base: '#352628', sh: '#1e1416', deep: '#0e080a' };
const SH = '#2a0e0a';

// ---------- outils ----------
const lock = (pts, color, o, w = 4) => glint(pts.map(([x, y], i) => [x, y, i === 0 || i === pts.length - 1 ? 0 : w]), color, o);
// une pièce en relief : son dégradé, puis une ombre franche en bas à gauche et un liseré clair en haut à droite
const relief = (d, grad, pal, w = 7, hw = 3) => `<path d="${d}" fill="url(#${grad})"/>` + cel(d, { ...pal, base: 'none' }, w, hw);
// un bord de fourrure : des petites mèches en pointe vers le bas
const furEdge = (pts, color) => pts.slice(0, -1).map(([x, y], i) => { const [x2, y2] = pts[i + 1], mx = (x + x2) / 2, my = (y + y2) / 2 + (i % 2 ? 8 : 11);
  return shape(`M${x} ${y}Q${n(mx - 2)} ${n(my - 4)} ${n(mx)} ${n(my)}Q${n(mx + 2)} ${n(my - 4)} ${x2} ${y2}Z`, color); }).join('');

// ---------- les formes ----------
const PLUMES = sm('31,138 32,142 37,142 48,133 82,113 114,101 151,95 188,97 221,105 249,120 275,144 292,168 265,178 299,178 300,200 372,200 373,178 396,178 371,168 373,150 368,115 362,98 344,66 320,41 310,33 273,14 242,7 208,6 183,9 163,16 160,22 164,26 188,23 216,23 240,26 263,33 295,52 318,77 333,105 340,131 340,165 335,163 325,164 314,144 299,124 283,108 267,96 253,88 229,78 188,71 155,71 133,74 92,87 74,96 53,111 37,127');
// le bâton : bien droit, d'un bout à l'autre
const STAFF = [[6, 516.0, 22], [40, 505.3, 22], [165, 466.2, 18], [290, 427.0, 17], [365, 403.5, 18], [405, 390.9, 19], [440, 379.9, 20], [470, 370.5, 21], [540, 348.6, 22], [577, 337.0, 24]];
const RINGS = [24, 44, 236, 330, 506, 528, 556];
const along = (x) => { for (let i = 1; i < STAFF.length; i++) { const [x0, y0, w0] = STAFF[i - 1], [x1, y1, w1] = STAFF[i]; if (x <= x1) { const f = (x - x0) / (x1 - x0); return [y0 + (y1 - y0) * f, w0 + (w1 - w0) * f, Math.atan2(y1 - y0, x1 - x0)]; } } return STAFF[STAFF.length - 1].slice(1).concat(0); };
const STAFF_D = rib(STAFF);
// la tête : un crâne rond, l'oreille à gauche, le museau qui avance à droite
// la tête : un crâne de fourrure arrondi (le haut et l'arrière), l'oreille, et le grand visage clair qui forme tout le bas
// de la tête (joues, menton, museau) : pas de fourrure sous le menton, le menton reste loin du bâton
const SKULL = ellipse(348, 250, 98, 84);
const EAR = ellipse(240, 292, 26, 30);
// le visage : une forme de visage humaine (joues rondes, petit menton), sans museau
const FACE_D = sm('258,258 290,240 330,246 362,256 394,246 430,242 454,258 464,284 462,316 448,344 422,366 390,380 360,384 330,378 300,362 278,340 264,312 256,284');
const HEAD = SKULL + EAR + FACE_D;
const BAND = sm('254,226 276,212 310,202 346,198 384,200 418,210 440,222! 438,236! 414,226 380,218 346,216 312,220 280,230 258,242!');
// le corps
const CAPE_D = sm('250,372 210,378 160,388 110,396 66,404 28,414! 50,428 40,446! 70,446 64,466! 96,460 104,476! 130,462 168,450 210,436 248,420');
const TAIL_D = rib([[232, 488, 24], [170, 492, 22], [112, 482, 20], [72, 456, 17], [60, 424, 14], [76, 400, 11], [100, 400, 8], [108, 414, 0]]);
const LEG_B = rib([[360, 488, 64], [420, 520, 56], [458, 548, 50]]);
const LEG_F = rib([[262, 492, 66], [200, 528, 58], [164, 556, 50]]);
const BOOT_B = sm('412,540 470,540 476,566 494,574 518,582 530,594 526,606! 402,606! 402,588 406,562');
const BOOT_F = sm('140,548 198,548 204,588 206,604! 200,612! 98,612! 86,602 88,590 102,580 136,576');
const SOLE_B = sm('402,596 528,596 526,606 402,606'), SOLE_F = sm('86,602 206,602 200,612 98,612');
const CUFF_B = rib([[400, 546, 0], [440, 540, 15], [480, 546, 0]]), CUFF_F = rib([[130, 554, 0], [170, 548, 15], [210, 554, 0]]);
const TORSO = sm('240,376 300,364 372,366 418,386 424,430 414,474 376,492 300,494 250,482 230,440 232,400');
const CHEST = sm('270,404 310,394 366,396 400,410 398,446 360,456 306,456 272,444 264,424');
const COLLAR = sm('234,372 268,358 310,352 356,354 398,362 428,378 420,396 394,388 356,382 310,382 270,388 242,396');
const BELT = sm('246,462 300,468 366,468 414,456 416,476 366,488 300,490 248,482');
const SKIRT = [sm('244,480 296,488 292,530 262,532 236,516'), sm('298,488 362,488 360,534 300,534'), sm('364,488 416,476 432,500 422,524 392,532 364,532')];
// les bras : celui du fond (à gauche) descend vers le bâton, celui de devant (à droite) le tient haut
const ARM_B = rib([[256, 392, 44], [226, 424, 38], [212, 448, 34]]);
const ARM_F = rib([[398, 394, 44], [420, 398, 38], [430, 396, 34]]);
const SLEEVE_B = rib([[258, 390, 52], [240, 410, 48], [232, 420, 0]]);
const FIST_B = sm('180,450 190,438 206,430 224,432 238,444 240,462 230,476 210,482 190,478 178,466');
const FIST_F = sm('402,392 410,376 428,368 448,370 462,382 464,400 456,416 438,424 418,422 404,410');

// ---------- dégradés ----------
const defs = [
  lin('g-fur', 0, 0, 0, 1, [[0, '#a8704e'], [0.55, FUR.base], [1, FUR.sh]], false),
  lin('g-peach', 0, 0, 0, 1, [[0, '#fff0de'], [1, PEACH.base]], false),
  lin('g-red', 0, 0, 0, 1, [[0, '#ea5a4c'], [0.55, RED.base], [1, RED.sh]], false),
  lin('g-cape', 1, 0, 0, 1, [[0, CAPE.hi], [0.4, CAPE.base], [1, CAPE.deep]], false),
  lin('g-gold', 0, 0, 0, 1, [[0, '#ffe68a'], [0.5, GOLD.base], [1, '#d89030']], false),
  lin('g-boot', 0, 0, 0, 1, [[0, '#8a5c40'], [1, BOOT.base]], false),
  lin('g-dark', 0, 0, 0, 1, [[0, DARK.hi], [1, DARK.base]], false),
  lin('g-staff', 0, 0, 0, 1, [[0, '#fff2b0'], [0.3, '#f6c450'], [0.7, '#d89028'], [1, '#8a5418']], false),
  rad('g-iris', 0.45, 0.4, 0.75, [[0, '#f8c070'], [0.4, '#d07a28'], [0.8, '#8a3e12'], [1, '#4a1e08']], false),
  rad('g-medal', 0.62, 0.35, 0.8, [[0, '#fff6c0'], [0.4, '#f6c04a'], [1, '#a86a1c']], false),
].join('');

// ---------- le visage : deux yeux pareils, bien posés de part et d'autre du nez ----------
const EL = almond(324, 292, 48, 32, -1, 5.2), ER = almond(398, 292, 48, 32, 1, 5.2);
function eye(cx, cy, r, A) {
  const id = `c-ee${cx}`;
  return `<clipPath id="${id}"><path d="${A.white}"/></clipPath><path d="${A.white}" fill="#fffdf8"/><g clip-path="url(#${id})">`
    + dot(cx, cy, r, 'url(#g-iris)') + dot(cx + 1, cy + 1, r * 0.46, '#1a0806') + dot(cx - r * 0.35, cy - r * 0.4, r * 0.3, '#ffffff') + dot(cx + r * 0.4, cy + r * 0.35, r * 0.13, '#ffffff', 0.9)
    + `<path d="M${cx - 40} ${cy - 30}L${cx + 40} ${cy - 30}L${cx + 40} ${cy - 6 + A.tilt}L${cx - 40} ${cy - 6 - A.tilt}Z" fill="${PEACH.sh}"/></g>` + shape(A.lash, '#2a140c') + line(A.lower, PEACH.deep, 1.6, 0.8)
    + `<g class="a-blink" opacity="0"><path d="${A.white}" fill="${PEACH.base}" stroke="${PEACH.base}" stroke-width="3"/>${line(A.shut, '#2a140c', 3)}</g>`;
}
EL.tilt = 6; ER.tilt = -6; // la paupière penche vers le nez (regard dur)
const FACE = eye(328, 296, 12.5, EL) + eye(402, 296, 12.5, ER)
  // les sourcils bruns, froncés vers le milieu, le même de chaque côté
  + shape(rib([[294, 262, 0], [312, 260, 7], [334, 268, 8], [356, 282, 0]]), FUR.deep)
  + shape(rib([[374, 282, 0], [396, 268, 8], [418, 260, 7], [436, 262, 0]]), FUR.deep)
  // le museau : un relief plus clair, les narines, le sourire en coin, les joues roses
  // un petit nez, un sourire en coin assuré, les joues roses
  + line('M362 318 Q368 326 376 322', '#c98c62', 2.6) + oval(371, 316, 3, 1.6, '#ffffff', 0.6)
  + line('M350 352 Q370 355 390 349', '#4a2014', 2.8) + line('M390 349 Q397 346 400 339', '#4a2014', 2.6);

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx = -4, dy = 6, o = 0.42) => ({ on, dx, dy, color: SH, o });
const parts = [
  { id: 'cape', cls: 'a-cape', d: CAPE_D, body: relief(CAPE_D, 'g-cape', CAPE, 7, 3)
    + lock([[230, 390], [160, 406], [90, 420], [44, 430]], CAPE.hi, 0.5, 4) + lock([[228, 418], [170, 436], [110, 452]], CAPE.deep, 0.5, 4) },
  { id: 'plumes', cls: 'a-plume', d: PLUMES, body: relief(PLUMES, 'g-fur', FUR, 6, 3)
    + clip('plumes', lock([[40, 132], [90, 98], [150, 82], [220, 90], [270, 124], [300, 160]], FUR.hi, 0.8, 3)
      + lock([[176, 14], [240, 14], [300, 40], [340, 84], [360, 130], [362, 168]], FUR.hi, 0.8, 3)) },
  { id: 'tail', cls: 'a-tail', d: TAIL_D, shadow: [sh(['cape'])], body: relief(TAIL_D, 'g-fur', FUR, 5, 2.4)
    + clip('tail', lock([[200, 482], [130, 480], [84, 456], [70, 424]], FUR.hi, 0.7, 3)) },
  { id: 'legB', cls: 'a-body', d: LEG_B, shadow: [sh(['tail', 'cape'])], body: relief(LEG_B, 'g-red', RED, 7, 3)
    + clip('legB', lock([[352, 476], [410, 500], [450, 528]], RED.hi, 0.6, 4) + lock([[392, 528], [430, 548]], RED.deep, 0.5, 4)) },
  { id: 'bootB', cls: 'a-body', d: BOOT_B + CUFF_B, shadow: [sh(['legB'])], body: relief(BOOT_B, 'g-boot', BOOT, 6, 3) + shape(SOLE_B, BOOT.deep)
    + lock([[424, 552], [430, 576], [460, 586], [506, 588]], BOOT.hi, 0.7, 3) + relief(CUFF_B, 'g-fur', FUR, 3, 1.6) },
  { id: 'legF', cls: 'a-body', d: LEG_F, shadow: [sh(['tail', 'cape', 'legB'])], body: relief(LEG_F, 'g-red', RED, 7, 3)
    + clip('legF', lock([[266, 478], [214, 508], [176, 540]], RED.hi, 0.6, 4) + lock([[214, 552], [176, 572]], RED.deep, 0.5, 4)) },
  { id: 'bootF', cls: 'a-body', d: BOOT_F + CUFF_F, shadow: [sh(['legF'])], body: relief(BOOT_F, 'g-boot', BOOT, 6, 3) + shape(SOLE_F, BOOT.deep)
    + lock([[186, 560], [190, 590], [150, 592], [104, 590]], BOOT.hi, 0.6, 3) + relief(CUFF_F, 'g-fur', FUR, 3, 1.6) },
  { id: 'torso', cls: 'a-body', d: TORSO, shadow: [sh(['cape', 'legB', 'legF', 'tail'])], body: relief(TORSO, 'g-red', RED, 8, 3)
    + clip('torso', relief(CHEST, 'g-gold', GOLD, 5, 2.4) + lock([[284, 406], [330, 398], [384, 404]], GOLD.hi, 0.9, 2.6)
      + [[290, 424], [330, 420], [372, 424]].map(([x, y]) => dot(x, y, 3.4, GOLD.deep) + dot(x + 0.8, y - 0.8, 1.2, GOLD.hi)).join('')) },
  { id: 'skirt', cls: 'a-body', d: SKIRT.join(''), shadow: [sh(['legB', 'legF'])], body: SKIRT.map((d, i) => relief(d, 'g-gold', { ...GOLD, sh: ['#b8701c', '#c47c22', '#b06a1a'][i] }, 5, 2.4)).join('')
    + SKIRT.map((_, i) => lock([[262 + i * 62, 498], [264 + i * 62, 514], [262 + i * 62, 528]], GOLD.sh, 0.6, 2.4)).join('') },
  { id: 'belt', cls: 'a-body', d: BELT, shadow: [sh(['torso', 'skirt'], -2, 5)], body: relief(BELT, 'g-dark', DARK, 3, 1.6)
    + `<rect x="316" y="468" width="30" height="16" rx="3" fill="${GOLD.sh}"/><rect x="319" y="470" width="24" height="11" rx="2" fill="url(#g-gold)"/>` + dot(331, 475.5, 2.6, DARK.base) },
  { id: 'collar', cls: 'a-body', d: COLLAR, shadow: [sh(['torso'], -2, 5)], body: relief(COLLAR, 'g-fur', FUR, 4, 2)
    + furEdge([[242, 396], [270, 388], [300, 384], [330, 382], [360, 383], [394, 388], [420, 396]], FUR.sh) },
  { id: 'armB', cls: 'a-body', d: ARM_B, shadow: [sh(['torso', 'cape', 'skirt'])], body: relief(ARM_B, 'g-fur', FUR, 6, 3)
    + clip('armB', relief(SLEEVE_B, 'g-red', RED, 5, 2.4)) },
  { id: 'staff', cls: 'a-body', d: STAFF_D, shadow: [sh(['torso', 'skirt', 'legF', 'legB', 'armB', 'belt', 'cape'], -3, 7)], body: `<path d="${STAFF_D}" fill="url(#g-staff)"/>` + clip('staff',
    RINGS.map((x) => { const [y, w, a] = along(x); return oval(x, y, 3.2, w * 0.62, '#8a5418', 0.85, a * 180 / Math.PI) + oval(x + 4, y - 1, 1.4, w * 0.5, '#fff2b0', 0.8, a * 180 / Math.PI); }).join('')
    + glint(STAFF.map(([x, y, w], i) => [x + 1, y - w * 0.22, i === 0 || i === STAFF.length - 1 ? 0 : w * 0.16]), '#ffffff', 0.7)
    + glint(STAFF.map(([x, y, w], i) => [x - 1, y + w * 0.3, i === 0 || i === STAFF.length - 1 ? 0 : w * 0.2]), '#7a4a14', 0.5)) },
  { id: 'fistB', cls: 'a-body', d: FIST_B, shadow: [sh(['staff', 'armB', 'torso'], -3, 5)], body: relief(FIST_B, 'g-peach', PEACH, 5, 2.4)
    + [196, 210, 224].map((x) => lock([[x, 440], [x + 0.5, 456], [x, 472]], PEACH.deep, 0.8, 2) + lock([[x + 3, 442], [x + 3.5, 454], [x + 3, 466]], '#ffffff', 0.6, 1)).join('') },
  { id: 'head', cls: 'a-head', d: HEAD, shadow: [sh(['torso', 'collar', 'plumes', 'armB', 'staff'], -4, 7)], body: ''
    // l'oreille (l'intérieur clair), le crâne de fourrure éclairé en haut à droite
    + relief(EAR, 'g-fur', FUR, 5, 2.4) + dot(242, 294, 15, PEACH.sh) + dot(244, 292, 11.5, PEACH.base)
    + relief(SKULL, 'g-fur', FUR, 8, 3) + lock([[300, 186], [352, 172], [408, 186]], FUR.hi, 0.7, 5)
    // le bandeau d'or et son médaillon, sur le front
    + `<path d="${BAND}" transform="translate(-2 4)" fill="${FUR.deep}" opacity="0.5"/>` + relief(BAND, 'g-gold', GOLD, 4, 2)
    + dot(352, 214, 16, GOLD.deep) + dot(352.6, 213.4, 14, 'url(#g-medal)') + line('M352 214 m-1 0 a3 3 0 1 1 4 3 a6 6 0 1 1 -8 -6 a8 8 0 0 1 10 2', '#8a5418', 2.4)
    // le visage clair (son ombre douce sur la fourrure), puis les yeux, le nez, la bouche
    + `<path d="${FACE_D}" transform="translate(-3 5)" fill="${FUR.deep}" opacity="0.45"/>` + relief(FACE_D, 'g-peach', PEACH, 7, 3)
    + FACE },
  { id: 'armF', cls: 'a-body', d: ARM_F, shadow: [sh(['torso', 'collar', 'staff'])], body: relief(ARM_F, 'g-fur', FUR, 5, 2.4) },
  { id: 'fistF', cls: 'a-body', d: FIST_F, shadow: [sh(['staff', 'armF', 'head', 'torso'], -3, 5)], body: relief(FIST_F, 'g-peach', PEACH, 5, 2.4)
    + [420, 434, 448].map((x) => lock([[x, 378], [x + 0.5, 394], [x, 410]], PEACH.deep, 0.8, 2) + lock([[x + 3, 380], [x + 3.5, 392], [x + 3, 404]], '#ffffff', 0.6, 1)).join('') },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : elle respire, la tête hoche, les plumes, la queue et la cape ondulent, elle cligne. Attaque (classe « atk »,
// 0,75 s) : elle se ramasse puis bondit en avant, bâton pointé ; plumes et queue fouettent l'air ; retour à la garde.
const PIV = { plume: [330, 185], tail: [230, 488], body: [300, 600], head: [330, 380], cape: [250, 380] };
const IDLE = {
  'a-plume': ['plume', 'plume 2.4s ease-in-out infinite alternate'],
  'a-tail': ['tail', 'tail 1.8s ease-in-out infinite alternate'],
  'a-cape': ['cape', 'cape 2.2s ease-in-out infinite alternate'],
  'a-body': ['body', 'body 2s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 2.6s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-root{transform-origin:300px 600px}
.a-blink{animation:blink 4.4s linear infinite}
@keyframes plume{from{transform:rotate(-1.6deg)}to{transform:rotate(1.4deg)}}
@keyframes tail{from{transform:rotate(-4deg)}to{transform:rotate(3deg)}}
@keyframes cape{from{transform:rotate(0deg)}to{transform:rotate(2.4deg)}}
@keyframes body{from{transform:none}to{transform:translate(0,-2px) scale(1.004,1.008)}}
@keyframes head{from{transform:none}to{transform:rotate(-1.4deg) translate(0,-1px)}}
@keyframes blink{0%,93%{opacity:0}94.5%,97%{opacity:1}98.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-head', 'head-atk')}${atk('a-plume', 'plume-atk')}${atk('a-tail', 'tail-atk')}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-10px,4px) rotate(-3deg)}48%{transform:translate(24px,-8px) rotate(3deg)}62%{transform:translate(20px,-2px) rotate(2deg)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}30%{transform:rotate(-3deg)}48%{transform:rotate(3deg)}100%{transform:none}}
@keyframes plume-atk{0%{transform:none}30%{transform:rotate(4deg)}50%{transform:rotate(-6deg)}72%{transform:rotate(2deg)}100%{transform:none}}
@keyframes tail-atk{0%{transform:none}30%{transform:rotate(8deg)}50%{transform:rotate(-10deg)}100%{transform:none}}
`.replace(/\n/g, '');

function svg(anime = true) {
  const s = figure({ w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'mages-8', w: W, h: H, pad: PAD, foot: [300, 610], svg };
