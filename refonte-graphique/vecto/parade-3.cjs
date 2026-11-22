// Le singe aux fusées (parade-3), monstre de la Parade des pétards : redessiné par le code d'après le dessin d'origine,
// dans le même cadre (453 × 362, mêmes proportions, même pose) : un singe brun trapu tourné vers la droite ; une
// couronne de pointes rouges et dorées, un masque crème autour des yeux, un œil jaune furieux (l'autre brille d'orange),
// une grande gueule ouverte aux crocs blancs ; gilet rouge sur chemise blanche, ceinture à boucle d'or ; quatre fusées
// rouges et dorées dressées dans le dos, une cinquième tenue à bout de bras ; longue queue enroulée en spirale.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. Contour décalqué sur l'original
// (outils/contour.py).
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 453, H = 362, PAD = 44;

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
const FUR = { hi: '#b0785a', lite: '#8a5a40', base: '#6a3e2a', mid: '#542e20', shade: '#3a1e16', deep: '#1e0e0a' };
const CREAM = { hi: '#ffffff', base: '#f4e2c4', shade: '#d0b494' };
const RED = { hi: '#ff8a6a', lite: '#f05a40', base: '#d4342a', shade: '#9a1c1c', deep: '#5a0c10' };
const GOLD = { hi: '#fff4b0', base: '#f4c040', shade: '#b07a1a', deep: '#6a4008' };
const SH = { fur: '#140806', red: '#3a0608' };

// ---------- dégradés ----------
const defs = [
  lin('g-fur', 320, 60, 160, 320, [[0, FUR.lite], [0.45, FUR.base], [1, FUR.shade]]),
  lin('g-furX', 0, 0, 1, 0, [[0, FUR.shade], [0.6, FUR.base], [1, FUR.lite]], false),
  lin('g-rocket', 0, 0, 1, 0, [[0, RED.shade], [0.4, RED.base], [0.75, RED.lite], [1, RED.base]], false),
  lin('g-cone', 0, 0, 1, 1, [[0, '#ff7a4a'], [0.5, RED.base], [1, RED.shade]], false),
  lin('g-gold', 0, 0, 0, 1, [[0, GOLD.hi], [0.45, GOLD.base], [1, GOLD.shade]], false),
  lin('g-vest', 340, 190, 220, 300, [[0, RED.lite], [0.5, RED.base], [1, RED.shade]]),
  lin('g-shirt', 0, 0, 0, 1, [[0, '#ffffff'], [0.6, '#eef0f6'], [1, '#c4c4d4']], false),
  lin('g-cream', 0, 0, 0, 1, [[0, CREAM.hi], [0.6, CREAM.base], [1, CREAM.shade]], false),
  rad('g-eye', 0.4, 0.4, 0.75, [[0, '#fffbd8'], [0.45, '#f8d23a'], [1, '#c08010']], false),
  rad('g-fire', 0.5, 0.5, 0.5, [[0, '#fff6c0', 0.9], [0.4, '#ffa040', 0.5], [1, '#ff6a20', 0]], false),
  lin('g-mouth', 0, 150, 0, 210, [[0, '#1a0406'], [0.6, '#3a0a10'], [1, '#6a1a20']]),
].join('');

// ---------- les fusées ----------
/** Une fusée : un tube rouge (d'axe a → b, large de w), des bagues dorées, la pointe conique au bout b. */
function rocketGeo([ax, ay], [bx, by], w) {
  const L = Math.hypot(bx - ax, by - ay), ux = (bx - ax) / L, uy = (by - ay) / L, nx = -uy, ny = ux, h = w / 2;
  const at = (f, s) => [ax + ux * L * f + nx * h * s, ay + uy * L * f + ny * h * s];
  const P2 = (p) => `${n(p[0])},${n(p[1])}`;
  const tube = sm([at(0, 1), at(0.78, 1), at(0.78, 1.5), `${P2([bx, by])}!`, at(0.78, -1.5), at(0.78, -1), at(0, -1)].map((p) => (typeof p === 'string' ? p : `${P2(p)}!`)));
  const cone = `M${P2(at(0.78, 1.5))} L${P2([bx, by])} L${P2(at(0.78, -1.5))} Z`;
  const band = (f0, f1) => `M${P2(at(f0, 1))} L${P2(at(f1, 1))} L${P2(at(f1, -1))} L${P2(at(f0, -1))} Z`;
  const lite = `M${P2(at(0.02, -0.15))} L${P2(at(0.76, -0.15))} L${P2(at(0.76, -0.75))} L${P2(at(0.02, -0.75))} Z`;
  return { tube, cone, bands: [band(0.18, 0.24), band(0.46, 0.52), band(0.7, 0.78)], lite, coneLite: `M${P2(at(0.8, -0.2))} L${P2([bx, by])} L${P2(at(0.8, -1.3))} Z` };
}
// les quatre fusées du dos (de la plus au fond à la plus devant) et celle de la main
// mesuré sur l'original : les pointes en 71,95 ; 109,59 ; 159,55, les tubes penchés vers le bas à droite
const ROCKETS = [
  { a: [132, 262], b: [70, 93], w: 36 }, { a: [168, 254], b: [108, 56], w: 38 }, { a: [204, 236], b: [159, 52], w: 38 },
];
const HAND_R = { a: [260, 272], b: [440, 172], w: 30 };
const rocketBody = (g, id) => use(id, 'url(#g-rocket)') + clip(id,
  shape(g.lite, RED.hi, 0.45) + g.bands.map((b) => shape(b, 'url(#g-gold)')).join('') + shape(g.cone, 'url(#g-cone)') + shape(g.coneLite, GOLD.base, 0.6));

// ---------- silhouettes (le bord extérieur suit le contour mesuré sur l'original) ----------
const RG = ROCKETS.map((r) => rocketGeo(r.a, r.b, r.w));
const HG = rocketGeo([346, 232], [444, 172], 32);
const S = {
  // la queue : une longue spirale qui part des reins vers la gauche et s'enroule
  tail: rib([[140, 290, 20], [100, 296, 22], [60, 290, 22], [32, 270, 20], [18, 240, 18], [22, 210, 16], [40, 190, 14], [62, 196, 12], [70, 214, 10], [62, 232, 8], [52, 236, 6]]),
  // les jambes, écartées, aux grands pieds de singe
  legL: sm('118,284 160,276 200,288 198,304 180,312 160,318 146,322 136,326 134,340! 88,336! 92,328 100,316 106,298'),
  legR: sm('230,290 270,284 268,307 266,323 262,327 262,333 265,336 290,336 296,343 298,349! 235,348 238,344 238,338 235,335 241,326 241,319 238,316 226,304'),
  // le corps (dans son gilet), la chemise blanche, la ceinture
  body: sm('196,200 240,190 290,192 320,200 340,220 344,250 330,272 304,292 260,300 220,302 192,292 180,262 182,226'),
  // la tête : la couronne, le crâne brun, le masque crème, la gueule
  crown: sm('228,25! 244,39 252,39 257,32 267,8! 280,37 283,40 290,40 293,35 297,34 305,27! 304,52 310,56 300,66 270,64 240,64 226,57 230,53'),
  head: sm('204,92 209,80 220,70 226,64 240,60 270,60 300,62 311,66 316,69 329,85 332,95 332,105 339,115 344,135 342,142 336,151 336,160 329,176 319,186 317,192 310,197 '
    + '300,204 270,208 246,204 228,194 214,178 206,156 204,132 202,110'),
  ear: sm('190,92 202,88 210,100 210,124 202,134 190,130 184,114'),
  mouth: sm('230,160 262,156 296,160 322,164 318,186 302,200 270,206 244,200 232,184'),
  // le bras droit (à gauche) replié devant le ventre, le bras gauche tendu qui tient la fusée
  armR: sm('176,206 204,196 228,208 240,234 238,258 218,268 196,262 180,240'),
  handR: sm('208,250 228,244 246,252 250,268 238,278 220,278 208,266'),
  armL: sm('300,214 326,210 344,226 356,244 360,256 342,262 322,248 306,236'),
  handL: sm('340,232 356,226 372,232 378,246 370,258 354,260 342,252'),
  rocketH: HG.tube,
  // le manche doré de la fusée tenue, qui passe dans la main
  stick: rib([[268, 278, 8], [310, 256, 9], [352, 232, 9]]),
};
ROCKETS.forEach((r, i) => { S[`r${i}`] = RG[i].tube; });

// ---------- le visage ----------
/** Une dent pointue (silhouette sans contour propre, posée dans la gueule). */
function tooth([x1, y1], [x2, y2], [tx, ty]) {
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  const d = `M${x1} ${y1}Q${n((x1 + tx) / 2 - (ty - y1) * 0.08)} ${n((y1 + ty) / 2)} ${tx} ${ty}Q${n((x2 + tx) / 2 + (ty - y2) * 0.08)} ${n((y2 + ty) / 2)} ${x2} ${y2}Z`;
  const half = `M${x1} ${y1}L${tx} ${ty}L${n(mx)} ${n(my)}Z`;
  return shape(d, '#fbf4e8') + shape(half, '#d8c8bc', 0.8) + line(`M${n(mx + (x2 - mx) * 0.5)} ${n(my + (y2 - my) * 0.5)}L${n(tx + (x2 - tx) * 0.2)} ${n(ty + (y2 - ty) * 0.2)}`, '#ffffff', 1.2, 0.9);
}
const TEETH_T = [[[236, 162], [248, 160], [244, 182]], [[252, 159], [264, 158], [259, 176]], [[268, 158], [280, 159], [276, 184]], [[284, 160], [296, 161], [291, 178]], [[300, 162], [312, 164], [307, 184]]];
const TEETH_B = [[[244, 200], [254, 202], [250, 190]], [[262, 204], [272, 205], [268, 192]], [[280, 205], [290, 204], [286, 192]], [[296, 201], [306, 198], [302, 188]]];

const headBody = use('head', 'url(#g-fur)') + clip('head',
  // le masque crème autour des yeux et du museau ; l'ombre à gauche ; la lueur orange autour de l'œil de droite
  shape(sm('214,120 232,104 258,98 286,106 304,118 320,124 334,136 330,156 316,160 290,156 262,156 236,158 220,150 212,134'), 'url(#g-cream)')
  + shape(sm('204,110 218,126 224,160 236,190 214,190 204,160'), FUR.shade, 0.5)
  + `<g class="a-glow">${oval(316, 132, 26, 22, 'url(#g-fire)')}</g>`
  // le front brun froncé qui descend entre les yeux, la petite fleur rouge
  + shape(sm('256,96 282,98 300,112 296,128 284,124 276,134 268,124 256,118 246,114'), FUR.base)
  + oval(284, 104, 4, 3, RED.base) + oval(282, 102, 1.4, 1, '#ffb0a0')
  // l'œil de gauche (jaune, furieux) et celui de droite qui brille
  + oval(256, 130, 16, 12.5, '#1a0a06') + oval(256, 131, 13.5, 10.5, 'url(#g-eye)') + oval(259, 131, 3.4, 7.6, '#1a0806') + dot(251, 126, 2.8, '#fff')
  + shape(sm('238,116 256,114 276,124 270,128 254,122 240,124'), FUR.deep)
  + oval(314, 132, 11, 9, '#3a1408') + oval(314, 132, 9, 7, '#ffb040') + oval(315, 132, 4, 4.4, '#fff6c0')
  + shape(sm('298,120 312,116 330,122 326,126 312,122 300,126'), FUR.deep)
  // le nez : deux narines
  + oval(282, 144, 2.4, 1.8, FUR.deep) + oval(292, 144, 2.4, 1.8, FUR.deep)
  // le dessus du crâne éclairé
  + glint([[228, 72, 0], [270, 64, 4], [310, 72, 0]], FUR.hi, 0.6)
  // la grande gueule ouverte : le bord crème du museau, l'intérieur sombre, la langue et les dents du bas (qui claquent),
  // les crocs du haut
  + `<path d="${S.mouth}" fill="${CREAM.shade}" transform="translate(0 3)"/><path d="${S.mouth}" fill="url(#g-mouth)"/>`
  + `<clipPath id="c-mouth"><path d="${S.mouth}"/></clipPath><g clip-path="url(#c-mouth)">`
  + `<g class="a-jaw">${shape('M244 200 C254 186 274 182 292 188 C300 192 300 200 292 204 L244 206 Z', '#c84a5a') + TEETH_B.map((t) => tooth(...t)).join('')}</g>`
  + TEETH_T.map((t) => tooth(...t)).join('') + '</g>'
);

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  // les fonds pris dans la silhouette de l'original (tout derrière) : la queue, les fusées du dos, la fusée tenue, les pieds
  { id: 'tailBase', cls: 'a-tail', d: sm('17,183 16,189 4,212 4,235 6,238 5,243 10,252 10,257 22,275 21,278 28,285 33,287 37,293 62,303 90,304 100,302 101,303 98,310 150,310 150,170 87,170 103,197 103,201 107,205 121,233 120,244 123,248 121,256 124,258 128,251 132,259 129,262 120,261 117,259 112,259 107,262 97,261 99,264 109,267 99,274 91,274 86,277 71,276 62,273 47,263 35,247 30,235 29,227 31,216 35,209 47,201 54,202 62,208 65,214 65,221 63,227 57,232 52,228 49,230 48,236 50,239 50,246 62,254 65,252 70,252 80,245 85,236 87,227 87,213 84,203 75,188 68,182 54,176 38,177 33,180 27,178 24,184 21,180'), body: use('tailBase', 'url(#g-fur)') },
  { id: 'rkBase', cls: 'a-rockets', d: sm('229,21 225,22 227,52 223,55 223,63 219,64 216,70 211,71 212,74 206,79 204,83 205,87 203,89 199,87 198,83 192,82 185,70 182,69 180,73 164,52 158,52 155,54 151,64 150,87 148,90 144,88 121,62 112,55 108,55 106,57 103,75 98,86 95,108 74,90 70,90 70,149 73,148 75,150 77,156 84,164 90,177 103,197 103,200 135,201 150,262 250,250 250,38 245,34 248,30 247,28 243,31') + sm('70,184 70,200 82,200 75,188'), body: use('rkBase', RED.deep) },
  { id: 'feetBase', cls: 'a-legL', d: sm('60,300 60,302 68,304 101,303 92,325 85,333 85,341 82,348 82,355 84,357 104,357 109,359 113,359 115,357 128,358 130,356 145,357 146,352 139,340 134,336 125,334 123,330 128,322 134,325 151,324 170,306 192,314 203,315 218,313 237,321 239,323 235,327 235,330 231,336 231,339 235,341 232,347 232,355 236,357 269,356 283,358 285,355 297,354 300,356 304,355 302,344 295,334 289,332 282,334 277,331 269,333 267,331 271,326 273,317 273,306 269,300'), body: use('feetBase', 'url(#g-furX)') },
  { id: 'tail', cls: 'a-tail', d: S.tail, body: use('tail', 'url(#g-fur)') + clip('tail',
    glint([[136, 284, 0], [96, 288, 4], [54, 280, 4], [28, 256, 3], [24, 220, 0]], FUR.hi, 0.55)
    + glint([[130, 298, 0], [80, 304, 4], [40, 290, 0]], FUR.deep, 0.5)) },
  ...ROCKETS.map((r, i) => ({ id: `r${i}`, cls: 'a-rockets', d: S[`r${i}`], shadow: i ? [sh([`r${i - 1}`], -4, 5, SH.red, 0.4)] : [], body: rocketBody(RG[i], `r${i}`) })),
  { id: 'legL', cls: 'a-legL', d: S.legL, shadow: [sh(['tail', 'r0', 'r1'], -4, 5, SH.fur, 0.45)], body: use('legL', 'url(#g-furX)') + clip('legL',
    shape(sm('88,324 130,320 142,332 134,342 88,342'), FUR.lite, 0.7) + glint([[104, 326, 0], [106, 334, 2], [106, 340, 0]], FUR.deep, 0.6) + glint([[118, 324, 0], [120, 332, 2], [120, 340, 0]], FUR.deep, 0.6)
    + oval(150, 292, 18, 10, FUR.hi, 0.4, -10))
    + [[94, 336], [110, 338], [126, 338]].map(([x, y]) => oval(x, y, 4, 2.4, '#f6ecdc')).join('') },
  { id: 'legR', cls: 'a-legR', d: S.legR, shadow: [sh(['tail'], -4, 5, SH.fur, 0.45)], body: use('legR', 'url(#g-furX)') + clip('legR',
    shape(sm('236,336 262,330 290,334 298,349 236,349'), FUR.lite, 0.7) + glint([[256, 336, 0], [258, 342, 2], [258, 348, 0]], FUR.deep, 0.6) + glint([[272, 336, 0], [274, 342, 2], [274, 348, 0]], FUR.deep, 0.6))
    + [[248, 346], [266, 347], [284, 346]].map(([x, y]) => oval(x, y, 4, 2.4, '#f6ecdc')).join('') },
  { id: 'body', cls: 'a-body', d: S.body, shadow: [sh(['r0', 'r1', 'r2', 'r3', 'tail', 'legL', 'legR'], -4, 6, SH.red, 0.45)], body: use('body', 'url(#g-vest)') + clip('body',
    // la chemise blanche au milieu, le gilet rouge à galons dorés, la ceinture et sa boucle d'or
    shape(sm('186,206 214,200 226,230 222,262 196,268 184,240'), 'url(#g-shirt)')
    + glint([[270, 198, 0], [274, 240, 3], [276, 280, 0]], RED.deep, 0.7) + glint([[274, 198, 0], [278, 240, 2], [280, 280, 0]], RED.hi, 0.6)
    + [[300, 226], [316, 248], [236, 226], [240, 256]].map(([x, y]) => dot(x, y, 2.4, GOLD.base)).join('')
    + shape(sm('196,272 250,280 300,276 330,266 332,282 300,292 250,296 196,288'), FUR.deep, 0.9)
    + oval(276, 284, 14, 10, 'url(#g-gold)') + oval(274, 282, 6, 3, GOLD.hi, 0.8)) },
  { id: 'rhBase', cls: 'a-armL', d: sm('450,172 447,170 437,171 382,167 382,173 386,178 383,183 352,198 351,202 347,206 330,207 330,256 336,254 340,257 345,257 348,254 353,253 361,245 366,236 373,236 383,230 386,231 395,225 402,234 407,234 412,229 416,230 433,200 447,182') + sm('344,150 330,150 330,184 341,164 341,154'), body: use('rhBase', 'url(#g-rocket)') },
  { id: 'stick', cls: 'a-armL', d: S.stick, shadow: [sh(['body'], -3, 5, SH.red, 0.4)], body: use('stick', 'url(#g-gold)') + clip('stick', glint([[272, 274, 0], [312, 252, 2], [350, 230, 0]], GOLD.hi, 0.9)) },
  { id: 'rocketH', cls: 'a-armL', d: S.rocketH, shadow: [sh(['body', 'stick'], -4, 6, SH.red, 0.4)], body: rocketBody(HG, 'rocketH') },
  { id: 'armL', cls: 'a-armL', d: S.armL, shadow: [sh(['body', 'rocketH'], -3, 5, SH.fur, 0.45)], body: use('armL', 'url(#g-furX)') + clip('armL',
    glint([[304, 218, 0], [330, 222, 3], [352, 240, 0]], FUR.hi, 0.6)) },
  { id: 'handL', cls: 'a-armL', d: S.handL, shadow: [sh(['rocketH', 'armL', 'stick'], -3, 5, SH.fur, 0.45)], body: use('handL', 'url(#g-furX)') + clip('handL',
    [[350, 234, 352, 256], [360, 232, 362, 256], [370, 236, 370, 254]].map(([x0, y0, x1, y1]) => glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 2.4], [x1, y1, 0]], FUR.deep, 0.6)).join('')) },
  { id: 'ear', cls: 'a-head', d: S.ear, shadow: [sh(['r2', 'r3'], -3, 4, SH.fur, 0.4)], body: use('ear', 'url(#g-fur)') + clip('ear', oval(198, 112, 6, 12, CREAM.shade, 0.8)) },
  { id: 'head', cls: 'a-head', d: S.head, shadow: [sh(['body', 'r1', 'r2', 'ear'], -3, 6, SH.fur, 0.45)], body: headBody },
  { id: 'crown', cls: 'a-head', d: S.crown, shadow: [sh(['head'], -3, 5, SH.red, 0.5)], body: use('crown', 'url(#g-cone)') + clip('crown',
    // trois pointes rouges : une face claire, une face sombre, un liseré d'or ; le bandeau doré
    [[228, 25, 248, 60], [267, 8, 268, 60], [305, 27, 290, 60]].map(([tx, ty, bx, by]) => shape(`M${bx - 14} ${by} L${tx} ${ty} L${bx} ${by} Z`, RED.shade, 0.6)
      + glint([[tx, ty + 6, 0], [(tx + bx) / 2 + 4, (ty + by) / 2, 3], [bx + 8, by - 4, 0]], GOLD.base, 0.8)).join('')
    + glint([[226, 56, 4], [266, 62, 5], [306, 56, 4]], GOLD.base, 0.95) + glint([[228, 54, 0], [266, 60, 1.6], [304, 54, 0]], GOLD.hi, 0.9)) },
  { id: 'armR', cls: 'a-armR', d: S.armR, shadow: [sh(['body'], -3, 5, SH.fur, 0.45)], body: use('armR', 'url(#g-shirt)') + clip('armR',
    // la manche blanche bouffante, une ombre au coude
    glint([[206, 220, 0], [222, 240, 5], [226, 262, 0]], '#c4c4d4', 0.7) + glint([[230, 212, 0], [238, 230, 3], [238, 250, 0]], '#ffffff', 0.9)) },
  { id: 'handR', cls: 'a-armR', d: S.handR, shadow: [sh(['body', 'armR'], -3, 5, SH.fur, 0.45)], body: use('handR', 'url(#g-furX)') + clip('handR',
    [[220, 254, 220, 272], [230, 252, 232, 274], [240, 256, 240, 272]].map(([x0, y0, x1, y1]) => glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 2.4], [x1, y1, 0]], FUR.deep, 0.6)).join('')) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : il trépigne. Le corps rebondit, la tête hoche, la gueule claque, la queue ondule, les fusées du dos tremblent,
// l'œil de droite brille par à-coups.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : il arme la fusée en arrière (élan), puis la lance en avant d'un grand
// coup de bras ; tout revient à la pose de repos.
const PIV = { body: [240, 330], head: [270, 200], tail: [140, 290], rockets: [220, 260], armL: [306, 220], armR: [214, 212], jaw: [270, 196], legL: [170, 296], legR: [250, 290] };
const IDLE = {
  'a-body': ['body', 'body .9s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 1.8s ease-in-out infinite alternate'],
  'a-tail': ['tail', 'tail 2.4s ease-in-out infinite alternate'],
  'a-rockets': ['rockets', 'rockets .45s ease-in-out infinite alternate'],
  'a-armL': ['armL', 'armL 1.8s ease-in-out infinite alternate'],
  'a-armR': ['armR', 'armR 1.6s ease-in-out infinite alternate'],
  'a-jaw': ['jaw', 'jaw .4s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('') + `
.a-glow{transform-origin:316px 132px;animation:glow .8s ease-in-out infinite alternate}
@keyframes body{from{transform:none}to{transform:translate(0,-2.4px)}}
@keyframes head{from{transform:none}to{transform:rotate(-2deg)}}
@keyframes tail{from{transform:rotate(-2deg)}to{transform:rotate(3deg)}}
@keyframes rockets{from{transform:rotate(-.6deg)}to{transform:rotate(.6deg)}}
@keyframes armL{from{transform:none}to{transform:rotate(-2deg)}}
@keyframes armR{from{transform:none}to{transform:rotate(3deg)}}
@keyframes jaw{from{transform:none}to{transform:translate(0,2px)}}
@keyframes glow{from{transform:scale(.85);opacity:.7}to{transform:scale(1.1);opacity:1}}
${atk('a-armL', 'armL-atk')}${atk('a-head', 'head-atk')}${atk('a-body', 'body-atk')}${atk('a-tail', 'tail-atk')}${atk('a-jaw', 'jaw-atk')}
@keyframes armL-atk{0%{transform:none}32%{transform:rotate(-22deg)}50%{transform:rotate(14deg)}64%{transform:rotate(10deg)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}32%{transform:rotate(-4deg)}50%{transform:translate(3px,1px) rotate(4deg)}100%{transform:none}}
@keyframes body-atk{0%{transform:none}32%{transform:translate(-4px,0) rotate(-2deg)}50%{transform:translate(6px,0) rotate(2deg)}100%{transform:none}}
@keyframes tail-atk{0%{transform:none}32%{transform:rotate(5deg)}50%{transform:rotate(-6deg)}100%{transform:none}}
@keyframes jaw-atk{0%{transform:none}32%{transform:translate(0,4px)}50%{transform:translate(0,7px)}100%{transform:none}}
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
  let s = figure({ master: require('./silhouettes/parade-3.json'), w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  // le corps emporte la tête, les bras, les fusées et la queue
  for (const c of ['a-head', 'a-armL', 'a-armR', 'a-rockets', 'a-tail']) s = nest(s, c, 'a-body');
  return s;
}

module.exports = { id: 'parade-3', w: W, h: H, pad: PAD, foot: [210, 346], svg };
