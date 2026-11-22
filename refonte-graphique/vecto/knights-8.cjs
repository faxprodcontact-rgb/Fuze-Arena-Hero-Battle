// Garvin, le golem de lave (knights-8) : redessiné par le code d'après le dessin d'origine, dans le même cadre
// (489 × 421, mêmes proportions, même pose) : tête cubique de basalte, sourcils en dalles qui surplombent des yeux de
// lave, bouche en zigzag, poing levé près du visage, poing droit en avant, épaule droite hérissée, torse fendu d'un
// grand Y de lave, ceinture et pagne de pierre, jambes trapues ; des veines de lave courent sur tout le corps.
// La roche est un basalte brun-charbon taillé en plans nets (un plan éclairé en haut à droite, un plan moyen, un plan
// sombre en bas à gauche, des coins ébréchés). La lumière vient d'en haut à droite : les ombres portées tombent en bas
// à gauche. La lave éclaire la roche : le bord des fissures, et tout le centre du corps autour de la poitrine.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 489, H = 421;

// ---------- couleurs ----------
// la roche : plan éclairé, plan moyen, plan sombre (≈ #3b3437 comme l'original), creux
const ROCK = { hi: '#c2b3a6', lite: '#7b6d64', base: '#5e534e', mid: '#4d4341', shade: '#3b3437', deep: '#2a2228', line: '#211a20' };
const COOL = '#93a2cf'; // reflet froid, en filet, sur les bords de gauche
const EDGE = '#e4d8cc'; // éclat clair sur les arêtes tournées vers la lumière
const LAVA = { hot: '#fffbe6', core: '#fff07e', yel: '#ffc935', org: '#ff8c22', red: '#ea4a1a', deep: '#8e1f10' };
const SH = '#1a1116'; // ombres portées

// ---------- outils ----------
/** Chemin lisse (Catmull-Rom) passant par des points. */
function cr(P) {
  let d = '';
  for (let i = 0; i < P.length - 1; i++) {
    const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)];
    d += `C${n(p1[0] + (p2[0] - p0[0]) / 6)} ${n(p1[1] + (p2[1] - p0[1]) / 6)} ${n(p2[0] - (p3[0] - p1[0]) / 6)} ${n(p2[1] - (p3[1] - p1[1]) / 6)} ${n(p2[0])} ${n(p2[1])}`;
  }
  return d;
}
/** Ruban effilé le long d'une ligne : pts = [[x, y, largeur], …] ; k = facteur de largeur ; jag = arêtes droites. */
function rib(pts, k = 1, jag = false) {
  const L = [], R = [];
  pts.forEach(([x, y, w], i) => {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1];
    const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
    const h = (w * k) / 2;
    L.push([x - dy * h, y + dx * h]); R.push([x + dy * h, y - dx * h]);
  });
  R.reverse();
  if (jag) return 'M' + [...L, ...R].map(([x, y]) => `${Math.round(x)} ${Math.round(y)}`).join('L') + 'Z';
  return `M${n(L[0][0])} ${n(L[0][1])}${cr(L)}L${n(R[0][0])} ${n(R[0][1])}${cr(R)}Z`;
}
/** Brise une ligne en éclair : un point milieu par segment, décalé d'un côté ou de l'autre (irrégulier mais fixe). */
function bolt(pts, amp = 0.12) {
  const out = [pts[0]];
  for (let i = 1; i < pts.length; i++) {
    const [x0, y0, w0] = pts[i - 1], [x1, y1, w1] = pts[i];
    const dx = x1 - x0, dy = y1 - y0, r = Math.sin(x0 * 12.9898 + y0 * 78.233) * 43758.5453;
    const s = (r - Math.floor(r) - 0.5) * 2 * amp;
    out.push([x0 + dx / 2 - dy * s, y0 + dy / 2 + dx * s, ((w0 + w1) / 2) * 1.15], pts[i]);
  }
  return out;
}
/**
 * Une veine de lave : la roche rougie de part et d'autre (deux lueurs, elles pulsent), puis la fente brisée, du bord
 * rouge sombre au cœur blanc-jaune.
 */
const crack = (pts, k = 1) => {
  const b = bolt(pts), w = Math.max(...pts.map((p) => p[2])) * k;
  const mid = `M${Math.round(pts[0][0])} ${Math.round(pts[0][1])}` + cr(pts.map(([x, y]) => [Math.round(x), Math.round(y)]));
  const halo = (sw, c, o) => `<path d="${mid}" fill="none" stroke="${c}" stroke-width="${n(sw)}" opacity="${o}"/>`;
  return `<g class="a-glow">${halo(w * 3.6, LAVA.org, 0.13)}${halo(w * 1.9, '#ff7424', 0.3)}</g>`
    + shape(rib(b, 1.7 * k, true), LAVA.deep, 0.95) + shape(rib(b, 1.3 * k, true), '#ff6f1c')
    + shape(rib(b, 0.92 * k, true), '#ffad2c') + shape(rib(b, 0.48 * k, true), '#fff3b0');
};
/** Une arête de pierre : éclat anguleux, clair (lumière) ou sombre (creux). */
const edge = (pts, color, o = 1) => shape(rib(pts, 1, true), color, o);
/** Un reflet qui suit un bord arrondi (lumière froide ou chaude sur le contour). */
const glint = (pts, color, o = 1) => shape(rib(pts), color, o);
/** Une fêlure sèche dans la pierre : une fente sombre brisée et son bord éclairé juste dessous. */
const fissure = (pts) => {
  const b = bolt(pts, 0.22);
  return shape(rib(b.map(([x, y, w]) => [x + 0.9, y + 1.3, w]), 1, true), ROCK.hi, 0.35) + shape(rib(b, 1, true), ROCK.line, 0.95);
};
/** Lueur de la lave sur la roche : un ovale flou orangé. */
const spill = (cx, cy, rx, ry, o = 1, rot = 0) => oval(cx, cy, rx, ry, 'url(#g-spill)', o, rot);
/** La lumière de la poitrine sur la roche du morceau (plus forte près du cœur du Y) ; elle pulse avec la lave. */
const chestLight = (o = 1) => `<g opacity="${o}"><g class="a-glow"><circle cx="248" cy="246" r="175" fill="url(#g-lavaLight)"/></g></g>`;

/** Bord de pierre cassé : chaque côté du polygone est recoupé tous les `step` px, chaque point décalé un peu (fixe). */
function rough(P, a = 1.9, step = 5) {
  const out = [];
  P.forEach(([x0, y0], i) => {
    const [x1, y1] = P[(i + 1) % P.length], len = Math.hypot(x1 - x0, y1 - y0) || 1;
    const m = Math.max(1, Math.round(len / step)), nx = -(y1 - y0) / len, ny = (x1 - x0) / len;
    for (let j = 0; j < m; j++) {
      const x = x0 + ((x1 - x0) * j) / m, y = y0 + ((y1 - y0) * j) / m, r = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453;
      const o = j ? (r - Math.floor(r) - 0.5) * 2 * a : 0;
      out.push([x + nx * o, y + ny * o]);
    }
  });
  return 'M' + out.map(([x, y]) => `${Math.round(x)} ${Math.round(y)}`).join('L') + 'Z';
}
/** Lit une liste « x y x y … » en points. */
const pts = (str) => str.trim().split(/[\s,]+/).map(Number).reduce((o, v, i) => (i % 2 ? o[o.length - 1].push(v) : o.push([v]), o), []);
/** Un plan de pierre au bord un peu ébréché (polygone « x y x y … »). */
const stone = (poly, fill, o = 1, a = 1.1) => shape(rough(pts(poly), a, 6), fill, o);
/** Un coin cassé : une petite facette claire et sa face d'ombre, posées sur une arête (a = orientation en degrés). */
const chip = (x, y, s, a = 0) => {
  const c = Math.cos((a * Math.PI) / 180), si = Math.sin((a * Math.PI) / 180);
  const P = (px, py) => `${n(x + px * c - py * si)} ${n(y + px * si + py * c)}`;
  return shape(`M${P(0, 0)}L${P(s, s * 0.25)}L${P(s * 0.3, s * 0.85)}Z`, '#a19288')
    + shape(`M${P(s * 0.3, s * 0.85)}L${P(s, s * 0.25)}L${P(s * 0.95, s * 0.9)}Z`, ROCK.deep, 0.75);
};
/**
 * Un bloc de pierre : son plan moyen, puis son plan éclairé (haut / droite) et son plan sombre (bas / gauche),
 * l'arête vive entre les deux premiers (un filet clair). Les trois plans sont des polygones « x y x y … ».
 */
const block = (mid, lit, dark, ridge = null, cols = {}) => stone(mid, cols.mid || ROCK.base)
  + (lit ? stone(lit, cols.lit || ROCK.lite, 1, 0.8) : '') + (dark ? stone(dark, cols.dark || ROCK.shade, 1, 0.8) : '')
  + (ridge ? edge(ridge, cols.edge || '#b4a599', 0.85) : '');

// ---------- dégradés ----------
const defs = [
  lin('g-rock', 0, 0, 0, 1, [[0, '#5a4f4a'], [0.5, '#4b4240'], [1, '#3b3437']], false),
  lin('g-head', 0, 0, 0, 1, [[0, '#62574f'], [0.55, '#5a4f4a'], [1, '#463d3b']], false),
  lin('g-headL', 0, 0, 0, 1, [[0, '#362e32'], [0.6, '#2e262b'], [1, '#251e23']], false),
  lin('g-leg', 0, 0, 0, 1, [[0, '#54493f'], [0.5, '#433a39'], [1, '#2c2529']], false),
  lin('g-foot', 0, 0, 0, 1, [[0, '#4c4240'], [1, '#2a2227']], false),
  rad('g-spill', 0.5, 0.5, 0.5, [[0, '#ff9a3c', 0.8], [0.5, '#ff7a2c', 0.34], [1, '#ff6a24', 0]], false),
  // la lumière de la lave du torse : orange vif près du cœur du Y, plus rien à 175 px
  rad('g-lavaLight', 0.5, 0.5, 0.5, [[0, '#ffb050', 0.6], [0.16, '#ff9a40', 0.42], [0.34, '#ff8030', 0.2], [0.56, '#f26a26', 0.06], [1, '#e85a20', 0]], false),
  // la lueur de la poitrine sous le menton
  rad('g-under', 0.5, 0.5, 0.5, [[0.6, '#ff9a3a', 0.75], [0.7, '#ff7a28', 0.3], [0.8, '#f0641f', 0.05], [1, '#e85a20', 0]], false),
  // le creux autour de l'œil, éclairé par la lave de l'œil
  rad('g-socket', 0.5, 0.5, 0.5, [[0.45, '#ff9a2a', 0.95], [0.68, '#f0641f', 0.6], [1, '#c0400f', 0]], false),
  lin('g-browSh', 0, 0, 0, 1, [[0, '#3a0d04', 0.85], [1, '#3a0d04', 0]], false),
  rad('g-heart', 0.5, 0.5, 0.5, [[0, '#fffbe6', 0.9], [0.3, '#ffe68a', 0.55], [0.65, '#ffb040', 0.2], [1, '#ff9a30', 0]], false),
  rad('g-lavaBed', 248, 244, 120, [[0, '#fffbe2'], [0.1, '#ffec8e'], [0.24, '#ffbe40'], [0.45, '#ff8a22'], [0.7, '#e2501a'], [1, '#9a2410']]),
  rad('g-plateLight', 248, 246, 150, [[0, '#ffb050', 0.5], [0.2, '#ff9a40', 0.32], [0.42, '#ff8030', 0.14], [0.7, '#f26a26', 0.04], [1, '#e85a20', 0]]),
  rad('g-plateGlow', 248, 244, 120, [[0, '#ffe08a'], [0.25, '#ffa23a'], [0.55, '#f26a24'], [1, '#c83c16']]),
  lin('g-molten', 0, 300, 0, 342, [[0, '#a8280f'], [0.5, '#e8521a'], [0.8, '#ff9a2a'], [1, '#ffd864']]),
  lin('g-loinGlow', 0, 296, 0, 328, [[0, '#ff7a24', 0], [0.5, '#ff8a2a', 0.7], [1, '#ffc24a']]),
  lin('g-shBot', 0, 150, 0, 200, [[0, '#ff7a28', 0], [0.7, '#ff7a28', 0.1], [1, '#ff9a3a', 0.45]]),
  rad('g-ember', 0.5, 0.5, 0.5, [[0, '#ffe08a', 1], [0.35, '#ff9a30', 0.8], [1, '#ff5a1a', 0]], false),
  rad('g-hit', 0.5, 0.5, 0.5, [[0, '#ffe68a', 0.9], [0.35, '#ff9a30', 0.6], [1, '#ff5a1a', 0]], false),
  rad('g-eye', 0.6, 0.45, 0.62, [[0, LAVA.hot], [0.32, LAVA.core], [0.68, LAVA.yel], [1, LAVA.org]], false),
  lin('g-belt', 0, 0, 0, 1, [[0, '#5e524d'], [0.35, '#463c3b'], [1, '#2a2226']], false),
].join('');

// ---------- silhouettes ----------
const S = {
  shinL: 'M80 330 C110 327 150 330 190 332 C178 342 168 350 164 360 C160 372 154 384 148 396 C120 394 84 392 56 392 C56 372 66 346 80 330 Z',
  footL: 'M54 382 C62 372 84 366 108 366 C128 366 144 372 151 382 C153 390 152 398 148 404 C138 406 128 407 112 408 C90 409 66 408 46 404 C45 395 48 388 54 382 Z',
  thighL: 'M136 262 C160 260 196 266 206 288 C210 306 206 322 196 334 C184 342 150 346 120 342 C106 338 98 332 95 326 C97 312 103 300 114 290 C124 282 130 272 136 262 Z',
  kneeL: 'M116 327 L124 317 L138 312 L150 316 L155 328 L154 342 L148 350 L134 354 L121 351 L114 341 Z',
  shinR: 'M264 342 C290 336 330 336 351 340 C353 352 351 364 353 378 C350 384 340 388 330 390 C300 394 280 396 265 398 C262 380 260 360 264 342 Z',
  footR: 'M263 384 C280 372 320 366 340 368 C358 370 371 378 377 388 C380 394 380 400 378 404 C350 408 300 406 267 402 C264 396 263 390 263 384 Z',
  thighR: 'M252 270 C270 264 292 266 300 274 C302 286 315 294 324 302 C332 312 337 324 348 334 C350 344 346 352 340 356 C310 358 282 354 266 347 C252 342 240 335 238 330 C240 310 244 290 252 270 Z',
  kneeR: 'M301 330 L310 318 L330 313 L345 318 L352 330 L350 345 L340 354 L318 357 L305 351 L300 341 Z',
  armR: 'M326 160 C340 168 360 176 380 184 L420 220 L420 270 C400 286 380 296 366 299 C352 290 338 280 330 272 C322 264 314 256 310 250 L294 252 L298 200 L312 166 Z',
  torso: 'M165 142 L330 150 L332 175 C328 195 318 225 310 250 L304 256 C300 262 297 268 299 278 C290 290 262 298 232 299 C200 299 160 294 134 284 C130 276 132 268 133 262 C140 244 144 214 146 190 C148 170 154 154 165 142 Z',
  loin: 'M209 279 C230 282 250 282 266 279 C268 294 267 306 263 318 L252 328 L242 335 L231 340 L220 334 L212 326 C209 310 208 294 209 279 Z',
  shR: 'M320 152 C326 144 334 140 340 141 L348 137 L355 146 L369 137 L373 150 L380 153 L384 158 C387 164 388 170 388 177 L390 183 C386 194 372 200 356 200 C340 199 326 194 318 188 C316 174 317 162 320 152 Z',
  armL: 'M74 124 C77 113 83 105 92 102 L104 101 L112 103 L146 118 C156 124 162 140 162 156 C160 168 154 174 144 176 C128 174 112 166 100 156 C88 148 79 138 74 124 Z',
  head: 'M186 23 L247 11 L270 9 L300 26 L343 67 C342 80 341 92 340 100 L336 120 C336 132 336 142 333 152 C329 166 321 178 307 186 C289 195 262 198 236 195 C212 192 194 182 182 168 C172 158 166 146 160 136 L152 124 L148 116 L147 96 L150 89 L152 57 L174 37 Z',
  fistL: 'M78 134 C70 135 62 138 54 140 C48 139 44 143 40 148 C34 151 30 155 26 161 C18 171 13 183 11 195 C9 203 10 210 14 216 C16 224 17 232 21 240 C27 250 37 258 49 263 C55 267 59 273 65 276 C75 279 88 279 100 275 C110 271 120 265 128 257 C137 247 143 235 145 221 C147 208 145 196 139 186 C133 178 126 172 118 166 C112 158 108 149 104 141 C96 135 88 133 78 134 Z',
  fistR: 'M380 184 C386 178 395 176 403 178 C410 174 422 173 432 175 C440 175 447 178 451 184 C459 188 467 196 471 206 C477 216 480 230 479 244 C479 252 476 260 471 268 C465 280 455 291 441 299 C431 304 420 305 410 301 C402 303 392 304 384 301 C372 301 362 297 356 289 C350 277 348 262 349 246 C350 228 356 210 366 196 C370 190 375 186 380 184 Z',
};

// ---------- la tête ----------
// les yeux : fendus en biais ; leur bord du haut est coupé net par la dalle du sourcil, le bas est arrondi
const EYE_L = 'M213 95 L268 111 C263 119 254 126 242 127 C229 128 219 122 216 113 C214 107 213 101 213 95 Z';
const EYE_R = 'M289 106 L337 92 C340 103 338 115 330 122 C322 129 309 130 300 125 C295 121 291 114 289 106 Z';
// les sourcils : deux dalles épaisses et séparées, en biais vers le nez ; leur bord du bas coupe le haut des yeux
const BROW_L = 'M210 85 L213 77 C214 75 216 74 219 75 L266 90 C269 91 271 94 271 97 L271 106 C271 109 269 111 266 110 L214 95 C211 94 210 91 210 85 Z';
const BROW_R = 'M287 101 L288 95 C288 92 290 90 293 89 L333 77 C336 76 339 78 340 81 L340 88 C340 90 339 92 337 92 L292 106 C289 107 287 105 287 101 Z';
// la bouche : la ligne du milieu du zigzag ; l'épaisseur se compte à la verticale (les pointes restent nettes)
const MOUTH = [[221, 166, 0.72], [238, 153, 1], [250.5, 166.5, 0.75], [272, 154.5, 0.95], [289.5, 165.8, 0.75], [303, 156.5, 0.9], [309, 166, 0.55]];
const zig = (t, c, o = 1) => {
  const up = MOUTH.map(([x, y, m]) => `${x} ${n(y - (t * m) / 2)}`), dn = MOUTH.map(([x, y, m]) => `${x} ${n(y + (t * m) / 2)}`).reverse();
  return shape(`M${up.join('L')}L${dn.join('L')}Z`, c, o);
};

/** Mélange deux couleurs « #rrggbb » (t de 0 à 1). */
const mix = (a, b, t) => '#' + [1, 3, 5].map((i) => Math.round(parseInt(a.substr(i, 2), 16) * (1 - t) + parseInt(b.substr(i, 2), 16) * t).toString(16).padStart(2, '0')).join('');
/** Une lueur en pas serrés : `fn(largeur, couleur)` dessiné `steps` fois, de w0 à w1, couleurs prises sur la rampe. */
function glowSteps(fn, w0, w1, ramp, steps) {
  let out = '';
  for (let i = 0; i < steps; i++) {
    const t = i / (steps - 1);
    let k = 0; while (k < ramp.length - 2 && t > ramp[k + 1][0]) k++;
    const [ta, ca] = ramp[k], [tb, cb] = ramp[k + 1];
    out += fn(n(w0 + (w1 - w0) * t), mix(ca, cb, Math.min(1, Math.max(0, (t - ta) / (tb - ta)))));
  }
  return out;
}

/** Un œil de lave : la lueur en dégradé, cœur blanc (posée sur un fond rouge, qui reste quand l'œil vacille). */
function eyeGlow(d, key) {
  return `<clipPath id="c-${key}"><path d="${d}"/></clipPath>`
    + `<g clip-path="url(#c-${key})"><path d="${d}" fill="url(#g-eye)" transform="translate(1.4 2) scale(0.985)"/></g>`;
}

const headBody = use('head', 'url(#g-head)') + clip('head',
  // le plan de gauche, dans l'ombre, et son filet de reflet froid
  shape('M186 23 L174 37 L152 57 L150 89 L147 96 L148 116 L152 124 L160 136 C166 146 172 158 182 168 C190 176 198 182 206 186 L206 160 C207 150 207 136 205 124 C207 110 207 90 205 70 C203 56 198 40 186 23 Z', 'url(#g-headL)')
  + glint([[153, 92, 0], [152, 70, 2.2], [160, 52, 2.4], [176, 36, 2.2], [186, 25, 0]], COOL, 0.6)
  // le dessus, éclairé, et son arête ; le plan de droite, étroit, et l'éclat de son bord
  + stone('188 23 247 11 270 9 300 26 290 34 268 20 249 22 199 32', '#4a4041', 1, 0.5)
  + edge([[199, 32, 0], [226, 26, 1.6], [249, 22, 1.6], [268, 20, 1.4], [290, 34, 0]], '#b9aa9d', 0.5)
  + stone('300 26 343 67 340 100 336 120 336 136 333 152 326 156 328 136 329 118 333 100 335 72 292 34', '#6d6058', 1, 0.5)
  + glint([[303, 28, 0], [322, 46, 1.8], [340, 68, 1.8], [337, 110, 1.6], [334, 148, 0]], EDGE, 0.8)
  // le front en trois plans (les fissures les séparent) : à gauche un peu dans l'ombre, au milieu, à droite éclairé
  + stone('206 34 232 28 236 50 232 80 210 84 206 60', '#4f4542', 1, 0.6)
  + stone('292 36 326 64 330 96 304 92 296 66', '#675a53', 1, 0.6)
  + fissure([[244, 26, 0], [250, 36, 1.2], [256, 46, 0]]) + fissure([[310, 52, 0], [318, 60, 1.3], [324, 70, 0]])
  // l'oreille de pierre, cerclée de lave
  + shape('M150 92 C146 104 147 118 152 128 C156 134 162 138 168 138 C170 124 170 108 164 96 C160 90 154 89 150 92 Z', '#2f272c')
  + edge([[151, 96, 0], [149, 108, 2.4], [152, 122, 2], [158, 132, 0]], '#4a4042')
  + crack([[152, 93, 0], [160, 98, 2.4], [165, 110, 3], [166, 124, 2.8], [163, 135, 0]], 1)
  // la longue veine de la mâchoire, de l'oreille jusqu'au menton
  + crack([[161, 132, 0], [167, 143, 2.6], [176, 155, 3.2], [187, 167, 3.4], [199, 177, 3], [213, 186, 0]], 1)
  + crack([[176, 155, 0], [186, 152, 1.8], [194, 156, 0]], 0.7)
  // des fêlures sèches (le haut du crâne, le menton)
  + fissure([[262, 22, 0], [268, 30, 1.4], [266, 40, 1.2], [272, 48, 0]])
  + fissure([[256, 176, 0], [260, 182, 1.3], [258, 190, 0]])
  // les deux fissures du front
  + crack([[207, 38, 0], [216, 43, 1.8], [225, 48, 3], [231, 56, 4.4], [233, 66, 3.6], [233, 77, 0]], 1)
  + crack([[285, 18, 0], [292, 29, 4.4], [299, 40, 4], [298, 51, 3.6], [295, 60, 3.4], [296, 74, 0]], 1)
  + crack([[231, 57, 0], [240, 58, 1.6], [247, 55, 0]], 0.8)
  + crack([[298, 51, 0], [306, 56, 1.6], [312, 54, 0]], 0.7)
  // les pommettes, deux plans qui avancent ; le bas du visage, un peu en retrait
  + stone('208 131 230 137 252 136 256 146 236 151 214 148 206 142', '#5b504b', 1, 0.6)
  + edge([[212, 132, 0], [232, 137, 1.6], [252, 136, 0]], '#a39488', 0.7)
  + stone('298 140 316 141 334 133 334 149 316 155 300 152', '#6e6159', 1, 0.6)
  + edge([[302, 141, 0], [318, 141, 1.8], [333, 134, 0]], '#b3a497', 0.8)
  + stone('214 172 236 170 262 172 292 170 314 165 310 182 290 192 262 196 234 193 214 184', '#4b413f', 1, 0.6)
  // le dessous de la tête, rougi par la lave de la poitrine (elle pulse)
  + `<g class="a-glow2"><circle cx="250" cy="252" r="80" fill="url(#g-under)"/></g>`
  + crack([[316, 158, 0], [322, 166, 2], [320, 176, 0]], 0.8)
)
  // les yeux de lave, enfoncés : le creux autour est rougi par leur lumière
  + oval(240, 112, 33, 23, 'url(#g-socket)', 1, 17) + oval(314, 112, 29, 21, 'url(#g-socket)', 1, -17)
  + `<path d="${EYE_L}" fill="${LAVA.red}" stroke="#f2621e" stroke-width="4.4"/><path d="${EYE_R}" fill="${LAVA.red}" stroke="#f2621e" stroke-width="4"/>`
  + `<g class="a-eyes">${eyeGlow(EYE_L, 'eL')}${eyeGlow(EYE_R, 'eR')}`
  + oval(241, 115, 1.9, 4.8, '#6a1c08', 1, -10) + oval(310, 113, 1.7, 4.4, '#6a1c08', 0.9, -6) + '</g>'
  // l'ombre des sourcils sur le haut des yeux
  + `<g clip-path="url(#c-eL)"><path d="M206 92.5 L270 111.2 L270 122 L206 103 Z" fill="url(#g-browSh)"/></g>`
  + `<g clip-path="url(#c-eR)"><path d="M284 108.5 L340 91 L340 102 L284 119.5 Z" fill="url(#g-browSh)"/></g>`
  // les sourcils : deux dalles épaisses ; le dessus éclairé, la face avant moyenne, le dessous dans l'ombre
  // chaque dalle pose son ombre sur le visage (en bas à gauche), puis : la face avant, le plan du dessus éclairé,
  // l'arête vive entre les deux, et le dessous dans l'ombre
  + `<path d="${BROW_L}" transform="translate(-2 4)" fill="#1f181e" opacity="0.6"/><path d="${BROW_R}" transform="translate(-2 4)" fill="#1f181e" opacity="0.6"/>`
  + shape(BROW_L, '#5f534d') + stone('211 80 214 75 266 90 271 96 265 98 214 84', '#94857a', 1, 0.4)
  + edge([[213, 83, 0], [240, 90, 1.6], [267, 98, 0]], EDGE, 0.8)
  + stone('212 91 266 106 271 106 266 110 214 95', '#30282c', 1, 0.3)
  + shape(BROW_R, '#5a4e49') + stone('288 95 293 89 333 77 340 81 334 84 292 97', '#908174', 1, 0.4)
  + edge([[290, 97, 0], [314, 90, 1.6], [337, 83, 0]], EDGE, 0.75)
  + stone('289 102 336 88 340 88 337 92 292 106', '#30282c', 1, 0.3)
  // le nez : un bloc taillé entre les yeux ; l'arête étroite, puis le bout en trois plans (ombre à gauche, face,
  // plan éclairé à droite), les narines, et son ombre portée sur le visage (en bas à gauche)
  + shape('M261 143 L294 143 L291 151 L265 152 Z', '#211a20', 0.75)
  + shape('M270 104 L278 104 L278 122 L268 122 Z', '#3d3436') + shape('M278 104 L288 104 L290 122 L278 122 Z', '#62564f')
  + edge([[286, 105, 0], [288, 113, 1.8], [289, 121, 0]], '#a39386', 0.8)
  + shape('M268 121 L290 121 L297 132 L295 141 L282 146 L268 145 L261 139 L263 130 Z', '#564b47')
  + shape('M268 121 L276 121 L272 134 L267 145 L261 139 L263 130 Z', '#3a3134')
  + shape('M284 121 L290 121 L297 132 L295 141 L287 144 L289 132 Z', '#8a7b70')
  + shape('M271 121 L288 121 L285 127 L274 127 Z', '#76685f')
  + edge([[289, 122, 0], [295, 131, 1.6], [294, 140, 0]], EDGE, 0.75)
  + oval(273, 141, 2, 1.2, '#1f181e', 0.75, 15) + oval(286, 141, 2, 1.2, '#1f181e', 0.75, -15)
  // la bouche : un zigzag de lave taillé dans la pierre
  + zig(14, '#5a1a12') + glowSteps(zig, 12, 3.6, [[0, '#e0481a'], [0.22, '#ff9a2a'], [0.48, '#ffc63c'], [1, '#fff0a0']], 7);

// ---------- le torse ----------
/**
 * Une plaque de pierre posée sur la lave : sa couleur, ce qu'on peint dedans, la lumière de la poitrine sur elle, puis
 * la lumière de la lave qui gagne son bord (trois passes de plus en plus étroites, peintes DANS la plaque).
 */
const plate = (key, poly, fill, inner = '', glow = 'url(#g-plateGlow)', light = 1) => {
  // le tracé n'est écrit qu'une fois (dans la découpe), puis réutilisé pour la couleur, la lumière et les bords
  const u = (attrs) => `<use href="#p-${key}" ${attrs}/>`;
  return `<clipPath id="c-${key}"><path id="p-${key}" d="${rough(pts(poly))}"/></clipPath>` + u(`fill="${fill}"`)
    + `<g clip-path="url(#c-${key})">${inner}`
    + (light ? `<g opacity="${light}"><g class="a-glow">${u('fill="url(#g-plateLight)"')}</g></g>` : '')
    + u(`fill="none" stroke="${glow}" stroke-width="7" opacity="0.22"`)
    + u(`fill="none" stroke="${glow}" stroke-width="3.2" opacity="0.5"`)
    + u(`fill="none" stroke="${glow}" stroke-width="1.3" opacity="0.95"`) + '</g>';
};

// le torse : un lit de lave (blanc au cœur, rouge sombre au bord), recouvert de plaques ; les fentes sont les crevasses
const torsoBody = use('torso', 'url(#g-lavaBed)') + clip('torso',
  // le col, sous le menton, au-dessus des deux bras du Y
  plate('pCol', '120 110 350 110 346 164 336 171 322 180 306 191 290 202 266 212 254 219 248 223 242 219 232 213 210 202 190 189 166 175 150 168 120 166', '#43393a',
    shape('M120 110 L350 110 L346 150 L300 150 L240 160 L180 156 L120 150 Z', '#382f33'))
  // chaque moitié du torse : une seule plaque (pectoral, ventre, flanc) ; seul le pied du Y les sépare
  + plate('pL', '110 176 150 177 166 183 188 196 208 207 230 218 239 226 242 236 244 250 245 264 245 282 244 300 110 300', '#4e4340',
    shape('M110 176 L150 177 L166 183 L188 196 L208 207 L231 219 L241 227 L243 234 L242 238 L224 230 L200 220 L178 208 L156 198 L110 196 Z', '#86654d')
    + edge([[150, 180, 0], [170, 186, 2.2], [192, 199, 2.4], [214, 211, 2.2], [238, 226, 0]], '#c9b29e', 0.9)
    // le bas du pectoral, dans l'ombre, puis le ventre qui avance (son arête du haut éclairée), le flanc en retrait
    + stone('116 236 150 236 178 241 206 248 232 252 244 254 244 262 214 260 186 262 160 264 116 266', '#3a3134', 0.9, 0.6)
    + stone('166 270 188 265 214 263 240 265 244 272 214 271 190 274 166 280', '#64574f', 1, 0.6)
    + stone('110 262 150 264 160 270 162 300 110 300', '#3a3134', 0.9, 0.6)
    + glint([[150, 200, 0], [149, 224, 2.6], [154, 250, 0]], COOL, 0.35)
    + fissure([[192, 230, 0], [200, 235, 1.4], [204, 241, 0]]))
  + plate('pR', '257 226 268 218 290 208 308 196 324 185 338 175 360 175 360 300 250 300 251 282 252 264 253 250 255 236', '#4e4340',
    shape('M253 230 L253 226 L266 218 L290 208 L308 196 L324 185 L338 175 L360 175 L360 190 L330 206 L300 220 L272 230 L254 238 Z', '#8e6c52')
    + edge([[256, 225, 0], [284, 212, 2.4], [310, 198, 2.4], [334, 179, 0]], '#d2bba6', 0.9)
    + stone('252 254 268 252 296 248 330 244 360 242 360 262 330 262 300 262 270 262 252 264', '#3a3134', 0.9, 0.6)
    + stone('254 270 270 265 290 266 302 270 304 276 288 273 268 274 254 278', '#64574f', 1, 0.6)
    + stone('306 262 360 262 360 300 304 300', '#3a3134', 0.9, 0.6)
    + fissure([[300, 228, 0], [306, 232, 1.3], [308, 239, 0]]))
  // le cœur du Y, rond et doux (il pulse) ; puis les branches qui partent du cœur sous les pectoraux, effilées
  + `<g class="a-glow"><circle cx="248" cy="240" r="26" fill="url(#g-heart)"/></g>`
  + crack([[246, 250, 0], [234, 254, 4.4], [220, 252, 3.8], [208, 257, 3], [198, 263, 2.2], [190, 271, 0]], 1)
  + crack([[220, 252, 0], [214, 243, 1.8], [206, 239, 0]], 0.7) + crack([[208, 257, 0], [206, 266, 1.6], [209, 274, 0]], 0.6)
  + crack([[251, 250, 0], [263, 254, 4.2], [276, 252, 3.6], [288, 257, 2.8], [298, 263, 2], [306, 270, 0]], 1)
  + crack([[276, 252, 0], [282, 244, 1.6], [290, 241, 0]], 0.6)
  + crack([[212, 205, 0], [214, 214, 1.8], [210, 222, 0]], 0.6) + crack([[290, 207, 0], [294, 216, 1.8], [300, 224, 0]], 0.6)
  + crack([[150, 214, 0], [160, 220, 2], [168, 230, 0]], 0.7) + crack([[322, 212, 0], [330, 220, 1.8], [334, 230, 0]], 0.7)
  // les veines des pectoraux et du col
  + crack([[164, 196, 0], [174, 206, 2.6], [180, 218, 2.4], [178, 232, 0]], 0.85) + crack([[180, 218, 0], [192, 222, 1.8], [202, 220, 0]], 0.6)
  + crack([[296, 214, 0], [308, 222, 2.6], [318, 232, 2.2], [324, 244, 0]], 0.85) + crack([[308, 222, 0], [314, 212, 1.6], [322, 206, 0]], 0.6)
  + crack([[206, 204, 0], [210, 194, 2], [216, 186, 1.6], [214, 176, 0]], 0.7) + crack([[288, 206, 0], [292, 196, 2], [298, 188, 0]], 0.7)
  + crack([[178, 182, 0], [186, 178, 1.6], [196, 180, 0]], 0.6) + crack([[300, 186, 0], [310, 182, 1.6], [318, 184, 0]], 0.6)
  // la ceinture : elle fait le tour de la taille, d'un bord à l'autre ; la lave d'au-dessus la rougit
  + `<path d="M120 261 C150 265 184 275 214 280 C240 283 276 278 314 265 L316 286 C280 298 240 302 210 298 C180 294 150 284 120 280 Z" fill="url(#g-belt)"/>`
  + `<g clip-path="url(#c-belt)">${chestLight(0.4)}</g>`
  + edge([[122, 263, 0], [160, 270, 2.2], [212, 281, 2.4], [262, 281, 2.2], [312, 268, 0]], '#c59a78', 0.9)
  + edge([[124, 279, 0], [170, 288, 2], [214, 297, 2.2], [270, 295, 2], [314, 285, 0]], '#1a1418', 0.7)
  + edge([[160, 271, 0], [159, 279, 1.8], [158, 288, 0]], ROCK.line, 0.9) + edge([[290, 276, 0], [291, 284, 1.8], [291, 292, 0]], ROCK.line, 0.9)
  // la boucle, à gauche du pagne
  + shape('M191 277 L211 280 L212 297 L192 294 Z', '#6c5e58') + shape('M195 281 L208 283 L209 293 L196 291 Z', '#281f25')
  + edge([[193, 278, 0], [202, 279, 1.6], [210, 281, 0]], '#d8c0a8', 0.9)
) + `<g class="a-glow">${spill(240, 282, 38, 10, 0.9)}</g>`;
const BELT_CLIP = '<clipPath id="c-belt"><path d="M120 261 C150 265 184 275 214 280 C240 283 276 278 314 265 L316 286 C280 298 240 302 210 298 C180 294 150 284 120 280 Z"/></clipPath>';

// ---------- les morceaux, du fond vers le devant ----------
const parts = [
  // --- jambe gauche : tibia, pied (le tibia entre dans la botte), cuisse, genouillère ---
  { id: 'shinL', d: S.shinL, body: use('shinL', 'url(#g-leg)') + clip('shinL',
    // le plan de devant, éclairé, et le dehors du tibia dans l'ombre ; des bosses de roche
    stone('96 334 150 334 170 342 160 360 150 382 122 378 104 362', '#493f3d', 1, 0.8)
    + stone('60 338 74 330 86 334 90 350 84 366 70 374 58 372', '#352d31')
    + stone('66 336 76 331 84 334 86 344 78 342 68 344', '#5a4f4b', 1, 0.6)
    + glint([[78, 332, 0], [66, 352, 2.4], [60, 372, 2.2], [58, 390, 0]], COOL, 0.55)
    + stone('104 352 126 350 146 354 150 366 136 372 112 370 100 362', '#4b413f', 0.9)
    + edge([[108, 352, 0], [126, 351, 1.6], [144, 355, 0]], '#9a8b80', 0.7)
    + crack([[96, 352, 0], [104, 357, 2.2], [108, 365, 0]], 0.8)
    // la fine veine du bord du tibia
    + crack([[150, 342, 0], [154, 354, 1.8], [152, 368, 1.6], [155, 384, 0]], 0.8)) },
  { id: 'footL', d: S.footL, rim: { on: ['shinL'], color: ROCK.line, w: 1.2 },
    body: use('footL', 'url(#g-foot)') + clip('footL',
      glint([[52, 386, 0], [48, 396, 2.4], [48, 404, 0]], COOL, 0.55)
      // le dessus de la botte, éclairé, et son arête
      + stone('56 382 70 372 92 367 116 367 138 371 150 380 140 384 116 380 92 381 70 386', '#342c30', 1, 0.6)
      + edge([[60, 380, 0], [84, 371, 1.4], [112, 369, 1.4], [146, 380, 0]], '#6e625c', 0.6)
      // le talon, puis trois orteils ronds (le dessus éclairé)
      + stone('46 404 48 392 56 384 66 382 70 392 68 406', '#352d31')
      + stone('68 406 67 396 71 388 80 385 89 386 94 393 95 406', '#463d3e')
      + stone('72 389 80 386 88 387 92 391 84 391 76 393', '#76685f', 1, 0.5)
      + stone('95 406 94 395 99 387 109 385 117 387 121 394 122 406', '#463d3e')
      + stone('99 388 108 386 116 388 119 392 110 391 101 393', '#76685f', 1, 0.5)
      + stone('122 406 122 396 127 389 137 388 145 392 149 399 149 406', '#463d3e')
      + stone('127 390 136 389 143 392 146 396 137 394 129 395', '#76685f', 1, 0.5)) },
  { id: 'thighL', d: S.thighL, shadow: [{ on: ['shinL', 'footL'], dx: -3, dy: 6, color: SH, o: 0.55 }],
    body: use('thighL', 'url(#g-leg)') + clip('thighL',
      // le dessus de la cuisse, éclairé ; le dehors dans l'ombre ; le dedans rougi par la lave du pagne
      stone('128 276 150 272 176 278 196 290 202 304 186 298 164 292 140 294 120 300', '#5d5149', 0.95)
      + edge([[132, 276, 0], [158, 274, 2.2], [184, 282, 2], [198, 294, 0]], '#c0b0a2', 0.8)
      + stone('98 324 104 308 112 296 118 312 116 330 106 336', '#352d31', 1, 0.7)
      + chestLight(0.3)
      + shape('M196 300 C204 312 204 326 196 334 C186 340 176 342 166 342 C182 330 190 316 192 302 Z', '#2b2329', 0.45)
      + glint([[134, 266, 0], [118, 284, 2.6], [104, 302, 2.6], [96, 324, 0]], COOL, 0.5)
      + crack([[146, 299, 0], [153, 306, 3], [151, 315, 2.6], [158, 322, 0]], 1)
      + crack([[153, 306, 0], [162, 304, 1.8], [168, 300, 0]], 0.8)
      + crack([[176, 292, 0], [184, 298, 2], [190, 308, 0]], 0.7)
      + `<g class="a-glow">${spill(200, 330, 16, 12, 0.8)}</g>`) },
  { id: 'kneeL', d: S.kneeL, shadow: [{ on: ['thighL', 'shinL'], dx: -3, dy: 5, color: SH, o: 0.55 }],
    body: use('kneeL', '#4b413f') + clip('kneeL',
      stone('116 322 126 315 140 312 150 317 154 326 146 330 130 330 118 330', '#7a6c63', 1, 0.6)
      + edge([[124, 317, 0], [140, 313, 2], [151, 320, 0]], EDGE, 0.75)
      + shape('M114 340 C120 350 134 354 146 350 C151 346 154 340 155 334 L158 360 L110 360 Z', ROCK.shade, 0.9)
      + chip(150, 318, 5, 60)
      + glint([[117, 336, 0], [118, 324, 2.6], [126, 316, 0]], LAVA.org, 0.85)
      + crack([[136, 314, 0], [145, 319, 2.4], [151, 330, 0]], 0.8)) },

  // --- jambe droite ---
  { id: 'shinR', d: S.shinR, body: use('shinR', 'url(#g-leg)') + clip('shinR',
    stone('270 350 296 344 324 346 346 352 344 364 318 368 290 368 272 364', '#463d3c', 0.95)
    + edge([[276, 349, 0], [300, 345, 1.8], [330, 347, 1.6], [344, 353, 0]], '#a89a8e', 0.75)
    + stone('264 344 276 348 274 372 268 396 262 396', '#352d31', 1, 0.6)
    + glint([[265, 344, 0], [262, 364, 2.2], [264, 384, 2.2], [266, 398, 0]], COOL, 0.55)
    + crack([[318, 356, 0], [326, 360, 2], [334, 358, 0]], 0.8)) },
  { id: 'footR', d: S.footR, rim: { on: ['shinR'], color: ROCK.line, w: 1.2 },
    body: use('footR', 'url(#g-foot)') + clip('footR',
      glint([[265, 386, 0], [264, 396, 2.4], [267, 402, 0]], COOL, 0.55)
      + stone('266 384 290 374 320 369 346 370 366 376 374 384 360 386 334 381 304 383 280 389', '#342c30', 1, 0.6)
      + edge([[268, 384, 0], [300, 371, 1.4], [338, 369, 1.4], [370, 379, 0]], '#6e625c', 0.6)
      + stone('266 402 266 392 276 384 296 382 306 388 306 404', '#352d31')
      + stone('306 404 306 393 312 386 322 384 331 386 336 393 337 404', '#463d3e')
      + stone('310 388 320 385 329 387 333 391 323 390 313 392', '#76685f', 1, 0.5)
      + stone('337 404 337 392 343 384 352 382 360 384 364 391 365 404', '#463d3e')
      + stone('341 386 351 383 359 385 362 389 352 388 343 390', '#76685f', 1, 0.5)
      + stone('365 404 366 393 371 386 377 389 380 396 380 404', '#463d3e')
      + stone('368 389 373 387 377 390 378 394 373 392', '#76685f', 1, 0.4)) },
  { id: 'thighR', d: S.thighR, shadow: [{ on: ['shinR', 'footR'], dx: -3, dy: 6, color: SH, o: 0.55 }],
    body: use('thighR', 'url(#g-leg)') + clip('thighR',
      stone('258 278 280 272 300 276 312 292 326 304 338 320 320 314 298 300 276 296 256 300', '#5d5149', 0.95)
      + edge([[262, 278, 0], [286, 274, 2.2], [306, 284, 2], [324, 302, 0]], '#c6b6a8', 0.8)
      + glint([[300, 276, 0], [314, 293, 2.4], [330, 312, 2.6], [346, 332, 0]], EDGE, 0.5)
      + chestLight(0.3)
      + shape('M240 300 C238 316 240 330 248 338 C258 344 270 348 280 350 C262 340 250 326 246 304 Z', '#2b2329', 0.4)
      + crack([[284, 300, 0], [292, 306, 3], [298, 314, 2.6], [306, 318, 0]], 1)
      + crack([[300, 284, 0], [308, 290, 2.2], [316, 298, 0]], 0.8)
      + glint([[240, 331, 0], [256, 341, 2.4], [276, 350, 0]], COOL, 0.45)
      + `<g class="a-glow">${spill(246, 324, 16, 14, 0.8)}</g>`) },
  { id: 'kneeR', d: S.kneeR, shadow: [{ on: ['thighR', 'shinR'], dx: -3, dy: 5, color: SH, o: 0.55 }],
    body: use('kneeR', '#4b413f') + clip('kneeR',
      stone('302 324 314 316 334 314 346 319 351 330 336 332 316 332 302 333', '#7a6c63', 1, 0.6)
      + edge([[310, 318, 0], [330, 315, 2], [347, 322, 0]], EDGE, 0.75)
      + shape('M300 342 C308 354 330 358 346 351 C350 347 352 341 352 335 L356 362 L298 362 Z', ROCK.shade, 0.9)
      + chip(344, 320, 5, 70)
      + glint([[303, 340, 0], [303, 327, 2.6], [312, 318, 0]], LAVA.org, 0.85)
      + crack([[303, 333, 0], [308, 323, 2.4], [318, 317, 0]], 0.8)) },

  // --- le bras droit (épaule et coude) : il passe sur le flanc ; le biceps est un bloc cerclé de lave ---
  { id: 'armR', cls: 'a-armR', d: S.armR,
    body: use('armR', '#3b2b28') + clip('armR',
      `<g class="a-glow2">${spill(330, 236, 34, 40, 0.9)}${spill(372, 250, 26, 30, 0.6)}</g>`
      // l'avant-bras : deux plaques de roche rougies par la lave, une veine entre elles
      + plate('pFore', '308 246 324 240 350 244 368 252 372 272 366 296 350 292 332 280 316 264', '#4d403c',
        stone('314 247 328 242 350 246 362 252 346 256 328 256', '#6a5a52', 1, 0.6), 'url(#g-plateGlow)', 1)
      + plate('pElb', '372 246 392 236 420 232 420 270 400 284 384 292 374 288 376 268', '#45393a', '', 'url(#g-plateGlow)', 0.9)
      // le haut du bras, derrière le biceps
      + plate('pUpp', '322 160 340 168 362 176 382 186 380 196 360 194 338 192 322 194', '#4a3f3e', '', 'url(#g-plateGlow)', 0.6)
      // le biceps : un gros bloc rond, cerclé d'une fente de lave ; son dessus éclairé, son flanc gauche rougi
      + plate('pBic', '312 210 326 200 340 196 358 197 374 204 380 218 374 232 358 240 340 243 322 241 310 228', '#55473f',
        stone('330 202 344 198 360 199 372 205 362 210 346 210 334 212', '#7d6d61', 1, 0.6)
        + edge([[334, 200, 0], [352, 198, 1.8], [370, 204, 0]], EDGE, 0.75)
        + fissure([[350, 214, 0], [356, 220, 1.3], [354, 228, 0]]), 'url(#g-plateGlow)', 1)
      + crack([[356, 238, 0], [364, 246, 2.2], [372, 256, 0]], 0.8)) },

  // --- le torse ---
  { id: 'torso', cls: 'a-torso', d: S.torso, shadow: [{ on: ['thighL', 'thighR'], dx: -3, dy: 6, color: SH, o: 0.6 }],
    body: BELT_CLIP + torsoBody },
  // le pagne : une plaque de pierre accrochée à la ceinture, sa pointe en fusion
  { id: 'loin', cls: 'a-loin', d: S.loin, shadow: [{ on: ['thighL', 'thighR'], dx: -4, dy: 5, color: SH, o: 0.55 }],
    body: use('loin', 'url(#g-molten)') + clip('loin',
      `<g class="a-glow">${spill(228, 334, 22, 12, 1)}</g>`
      + plate('pLoin', '204 274 272 274 269 296 266 310 258 320 248 326 238 330 228 328 218 324 208 318', '#3f3533',
        stone('204 274 272 274 270 284 252 285 230 285 206 284', '#2b2228', 0.6, 0.5)
        + stone('216 290 240 290 262 289 266 296 252 298 232 299 214 298', '#5e524c', 1, 0.6)
        + edge([[214, 291, 0], [240, 291, 2], [262, 290, 0]], '#d6c0aa', 0.85)
        + fissure([[240, 300, 0], [246, 305, 1.3], [244, 311, 0]]), 'url(#g-loinGlow)', 0.45)
      + crack([[224, 326, 0], [230, 333, 2.2], [232, 340, 0]], 0.7)) },

  // --- l'épaule droite, hérissée de pierres ; la lave sort dessous ---
  { id: 'shR', cls: 'a-shR', d: S.shR, shadow: [{ on: ['torso', 'armR'], dx: -3, dy: 6, color: SH, o: 0.55 }],
    body: use('shR', 'url(#g-rock)') + clip('shR',
      // les pointes : leur face de droite éclairée, celle de gauche dans l'ombre
      shape('M340 141 L348 137 L355 146 L369 137 L373 150 L380 153 L384 158 L377 160 L369 152 L356 153 L346 147 Z', '#86776d')
      + shape('M340 141 L348 137 L346 147 Z', '#3d3436') + shape('M355 146 L369 137 L364 150 Z', '#3d3436')
      + edge([[343, 142, 0], [348, 139, 1.8], [353, 145, 0]], EDGE, 0.85)
      + edge([[360, 143, 0], [368, 139, 1.8], [372, 148, 0]], EDGE, 0.85)
      + glint([[374, 152, 0], [384, 162, 2.2], [387, 176, 0]], EDGE, 0.6)
      // le plan de gauche, dans l'ombre ; le bas rougi par la lave qui sort dessous
      + stone('318 160 330 152 338 160 336 178 328 190 318 186', '#3b3437', 1, 0.7)
      + `<g class="a-glow2"><rect x="310" y="150" width="90" height="55" fill="url(#g-shBot)"/></g>`
      + crack([[343, 140, 0], [347, 150, 2.4], [350, 160, 2.6], [352, 170, 2.8], [349, 181, 2.6]], 0.9)
      + crack([[349, 180, 2.4], [343, 188, 2.2], [337, 198, 0]], 0.9) + crack([[350, 180, 0], [360, 186, 2.4], [372, 191, 1.8], [380, 199, 0]], 0.85)
      + crack([[358, 148, 0], [362, 156, 1.8], [364, 166, 0]], 0.7)
      + fissure([[330, 168, 0], [334, 174, 1.3], [332, 180, 0]])) },

  // --- le bras levé (épaule et haut du bras, derrière le poing) : fendu en X par la lave ---
  { id: 'armL', cls: 'a-armL', d: S.armL, shadow: [{ on: ['torso'], dx: -2, dy: 6, color: SH, o: 0.55 }],
    body: use('armL', 'url(#g-rock)') + clip('armL',
      // le dessus, éclairé ; le dessous, dans l'ombre
      stone('92 102 104 101 112 103 146 118 155 128 140 124 106 110 90 110', '#7b6d63', 1, 0.6)
      + edge([[94, 103, 0], [116, 105, 2.2], [144, 119, 0]], EDGE, 0.7)
      + stone('78 132 92 142 106 154 124 166 144 174 154 174 144 178 126 174 104 162 86 148', '#382f33', 1, 0.6)
      + `<g class="a-glow2">${spill(132, 140, 40, 28, 1, 35)}</g>`
      + crack([[106, 102, 0], [114, 112, 3.4], [124, 128, 5.6], [136, 142, 6.4], [148, 156, 4.8], [158, 167, 0]], 1)
      + crack([[118, 112, 0], [128, 117, 2.6], [137, 123, 0]], 0.8)
      + crack([[126, 130, 0], [114, 134, 2.6], [100, 136, 2], [90, 133, 0]], 0.9)
      + crack([[138, 144, 0], [128, 154, 2.2], [118, 158, 0]], 0.7)
      + glint([[104, 150, 0], [124, 166, 3.4], [146, 174, 3], [160, 166, 0]], LAVA.org, 0.7)) },

  // --- la tête ---
  { id: 'head', cls: 'a-head', d: S.head, shadow: [{ on: ['torso', 'armL', 'shR'], dx: -3, dy: 7, color: SH, o: 0.6 }],
    body: headBody },

  // --- le poing levé : la tranche dans l'ombre à gauche, quatre doigts repliés (le premier finit par le pouce) ---
  { id: 'fistL', cls: 'a-fistL', d: S.fistL, shadow: [{ on: ['torso', 'armL', 'head', 'thighL'], dx: -3, dy: 7, color: SH, o: 0.6 }],
    body: use('fistL', '#463c3a') + clip('fistL',
      // le dos de la main, à gauche, et le dessous : dans l'ombre (en bas à gauche) ; un filet de reflet froid au bord
      shape('M30 164 C20 176 13 188 11 198 C9 206 10 212 14 218 C16 226 17 234 21 242 C27 252 37 259 49 264 C46 244 44 222 44 200 C44 188 42 178 38 170 Z', '#30282c')
      + shape('M20 244 C40 252 80 256 128 250 L122 262 C110 272 92 280 70 279 C52 276 34 264 20 250 Z', '#2b2328')
      + glint([[26, 170, 0], [14, 194, 2.4], [16, 224, 2.4], [30, 252, 0]], COOL, 0.65)
      + stone('22 196 32 188 42 192 44 214 40 234 30 238 22 226', '#3a3134', 1, 0.8)
      + edge([[24, 195, 0], [32, 189, 1.6], [41, 193, 0]], '#857873', 0.75)
      // l'index replié : un gros bloc arrondi en haut, son dessus éclairé
      + stone('18 168 26 152 44 142 66 137 90 136 100 140 104 150 100 162 90 170 66 175 44 177 28 175', '#544944')
      + stone('28 152 46 143 66 138 90 137 99 141 92 146 70 147 50 151 36 158', '#8a7b70', 1, 0.6)
      + edge([[30, 151, 0], [52, 142, 1.8], [78, 138, 1.8], [98, 141, 0]], EDGE, 0.8)
      + stone('28 170 50 173 72 172 92 168 100 163 92 172 66 177 44 178 30 176', '#30282c', 1, 0.5)
      + fissure([[54, 158, 0], [60, 163, 1.3], [62, 170, 0]])
      // le majeur : une jointure ronde, plus petite, à droite de l'index
      + stone('88 150 96 141 108 140 116 147 118 160 112 170 100 173 90 166', '#5c5049')
      + stone('94 143 106 141 114 147 116 154 108 150 98 148', '#9a8a7d', 1, 0.5)
      + chip(110, 142, 5, 35)
      // les deux autres doigts repliés, sous l'index, à gauche (en partie cachés par le pouce)
      + stone('44 184 52 179 62 182 64 200 60 222 56 240 48 244 44 226 43 204', '#4c423f')
      + edge([[46, 184, 0], [54, 180, 1.4], [62, 183, 0]], '#9a8b80', 0.7)
      // le pouce : un gros bloc qui passe en travers devant les doigts, du bas à gauche vers le haut à droite
      + stone('60 196 76 184 96 177 112 175 122 180 124 191 116 200 102 212 90 228 80 242 66 247 58 240 56 220', '#665951')
      + stone('64 194 78 184 96 178 112 176 120 181 112 186 96 190 80 196 68 204', '#a39386', 1, 0.6)
      + edge([[66, 193, 0], [86, 182, 1.8], [110, 176, 1.6], [121, 182, 0]], EDGE, 0.85)
      + stone('58 238 66 246 80 242 90 228 100 214 92 222 78 236 66 240', '#3a3134', 1, 0.5)
      // le bout du pouce, arrondi, et son ongle de pierre
      + stone('104 180 114 175 122 179 125 188 120 196 110 197 104 190', '#7a6c62', 1, 0.5)
      + stone('110 178 118 177 122 182 118 186 112 184', '#bcac9e', 1, 0.4)
      // l'annulaire et l'auriculaire, au bout des doigts, à droite : deux phalanges inégales et un pli courbe
      + stone('98 210 116 200 134 200 145 208 148 222 145 237 134 246 112 248 96 244 92 228', '#5a4f49')
      + stone('104 208 118 201 134 201 143 207 132 210 116 212', '#8f8075', 1, 0.5)
      + edge([[100, 226, 0], [114, 222, 1.6], [130, 224, 1.4], [146, 228, 0]], '#2b2328', 0.8)
      + edge([[104, 228, 0], [124, 226, 1.2], [140, 229, 0]], '#9a8b80', 0.6)
      + stone('98 238 118 240 140 236 145 237 134 246 112 248 96 244', '#30282c', 1, 0.5)
      // les creux : la lave luit au fond, entre l'index et le pouce, et sous le bout du pouce
      + crack([[94, 168, 0], [104, 172, 1.8], [114, 176, 0]], 0.7)
      + crack([[118, 198, 0], [126, 203, 1.8], [136, 202, 0]], 0.6)
      // la lave du torse éclaire le côté du poing tourné vers elle : une lueur large, sans liseré
      + chestLight(0.8)
      + `<g class="a-glow">${spill(140, 205, 26, 52, 0.75)}</g>`) },

  // --- le poing en avant : trois jointures, les doigts repliés et le pouce ; le côté du bras rougi par la lave ---
  { id: 'fistR', cls: 'a-fistR', d: S.fistR, shadow: [{ on: ['armR', 'shR'], dx: -4, dy: 6, color: SH, o: 0.6 }],
    body: use('fistR', '#463c3a') + clip('fistR',
      // la base du pouce, à gauche : un gros bloc arrondi, tourné vers la lave du bras ; son bord rougi
      stone('352 236 362 222 376 216 388 222 392 244 390 270 384 292 370 298 356 290 350 266', '#46393a')
      + stone('362 224 374 218 386 222 388 236 380 230 368 232', '#76665a', 1, 0.5)
      + glint([[364, 222, 0], [354, 244, 3.4], [352, 270, 3], [360, 292, 0]], LAVA.org, 0.75)
      + `<g class="a-glow">${spill(356, 256, 12, 32, 0.6)}</g>`
      + crack([[378, 230, 0], [382, 244, 2], [380, 258, 0]], 0.7)
      // le flanc droit, dans l'ombre, et son filet de reflet froid
      + shape('M466 202 C476 216 480 232 478 250 C476 264 470 277 460 287 C466 272 470 256 471 240 C471 226 469 214 466 202 Z', '#3e3536')
      + glint([[476, 236, 0], [473, 256, 2.2], [464, 276, 0]], COOL, 0.6)
      // les trois jointures du haut : la face du dessus éclairée, la face avant, le dessous dans l'ombre
      + stone('381 192 388 182 400 179 408 183 413 194 413 210 408 221 396 226 386 221 380 208', '#4a403f')
      + stone('381 192 388 182 400 179 408 183 412 192 402 196 390 198 381 200', '#6f6157', 1, 0.6)
      + edge([[384, 188, 0], [394, 181, 1.4], [406, 184, 0]], EDGE, 0.7)
      + stone('384 214 396 218 410 214 408 221 396 226 386 221', '#2c2429', 1, 0.5)
      + stone('413 184 422 177 436 176 446 181 451 192 450 206 446 214 432 218 416 216 412 204', '#4c4240')
      + stone('413 184 422 177 436 176 446 181 450 190 436 192 420 193 413 194', '#73655b', 1, 0.6)
      + edge([[418, 179, 0], [432, 176, 1.8], [446, 182, 0]], EDGE, 0.8)
      + stone('414 208 430 212 448 208 446 214 432 218 416 216', '#2c2429', 1, 0.5)
      + stone('451 194 460 192 467 199 471 210 470 220 464 226 455 224 451 216', '#463c3c')
      + stone('451 194 460 192 467 199 469 205 460 205 452 206', '#65584f', 1, 0.6)
      + chip(444, 180, 5, 40)
      + fissure([[424, 196, 0], [430, 202, 1.3], [428, 210, 0]])
      // les doigts repliés, puis le pouce qui passe devant : sa face du dessus éclairée
      + stone('400 224 420 218 452 219 469 228 474 242 468 260 448 267 420 267 402 262 396 248', '#4a403f')
      + stone('400 224 420 218 452 219 469 228 471 234 452 230 424 230 402 233', '#65584f', 1, 0.6)
      + stone('399 243 410 237 430 238 446 247 451 256 444 264 424 266 404 263 397 254', '#5c514b')
      + stone('399 243 410 237 430 238 446 247 448 252 430 247 412 246 400 248', '#9a8a7e', 1, 0.6)
      + edge([[402, 241, 0], [422, 238, 1.8], [444, 246, 0]], EDGE, 0.85)
      + stone('400 256 424 262 446 258 444 264 424 266 404 263', '#2c2429', 1, 0.5)
      // les creux entre les jointures et sous le pouce : la lave luit au fond
      + crack([[408, 186, 0], [412, 200, 1.8], [410, 214, 0]], 0.6)
      + crack([[404, 228, 0], [418, 230, 1.8], [434, 232, 0]], 0.6)
      // le bas du poing
      + stone('392 268 414 272 446 272 466 264 460 280 448 292 430 299 404 300 391 294', '#2b2328')
      + edge([[398, 270, 0], [430, 273, 1.6], [460, 267, 0]], '#5d5250', 0.85)
      + glint([[396, 297, 0], [418, 300, 2.2], [440, 294, 0]], COOL, 0.4)
      // la lave du bras et de la poitrine sur le côté du poing
      + chestLight(0.35)) },

  // --- braises qui montent des fissures, éclair de chaleur au bout du coup de poing (aucune silhouette : pas de contour) ---
  { id: 'fx', d: 'M-900 -900', body:
    [[138, 128, 2.6], [356, 188, 2.2], [232, 234, 2.4], [302, 212, 2]].map(([x, y, r], i) =>
      `<g class="a-emb${i + 1}" opacity="0">${dot(x, y, r * 2.6, 'url(#g-ember)')}${dot(x, y, r * 0.8, '#fff3b0')}</g>`).join('')
    + `<g class="a-hit" opacity="0">${dot(526, 230, 26, 'url(#g-hit)')}</g>` },
];

// ---------- la vie au repos et le coup de poing ----------
// Repos : le torse respire (il gonfle depuis les hanches), la tête, les épaules et les bras montent avec lui, les poings
// se serrent chacun à leur rythme, la lave pulse, les yeux vacillent, des braises montent des fissures.
// Coup de poing (classe « atk » sur le <svg>, 0,75 s) : tout le haut du corps bascule autour des hanches (HIP), d'abord en
// arrière (élan), puis en avant pendant que le poing droit part vers la droite ; retour exact à la pose du repos.
const HIP = [220, 296];
/**
 * Une image clé du coup : le haut du corps glisse de tx, bascule de lean et se tasse (sx, sy) autour des hanches,
 * puis le morceau fait son mouvement propre autour de son pivot O. Même liste de fonctions partout.
 */
const key = (O, [p, [lean, tx, sx, sy], dx = 0, dy = 0, r = 0, sc = 1]) =>
  `${p}%{transform:translate(${HIP[0] - O[0]}px,${HIP[1] - O[1]}px) translate(${tx}px,0px) rotate(${lean}deg) scale(${sx},${sy}) translate(${O[0] - HIP[0]}px,${O[1] - HIP[1]}px) translate(${dx}px,${dy}px) rotate(${r}deg) scale(${sc})}`;
// le buste : 0 → élan (en arrière, tassé) → frappe (en avant, étiré) → tient → petit rebond → repos
const LEAN = { 0: [0, 0, 1, 1], 30: [-6, -5, 1.03, 0.95], 46: [9, 8, 0.98, 1.03], 60: [7.5, 7, 0.99, 1.02], 80: [-1, 0, 1, 1], 100: [0, 0, 1, 1] };
const atk = (name, O, own = {}) => `@keyframes ${name}{${Object.keys(LEAN).map((p) => key(O, [p, LEAN[p], ...(own[p] || [])])).join('')}}`;
const PIV = { torso: HIP, loin: [238, 280], head: [252, 192], shR: [352, 180], armR: [338, 180], armL: [150, 140], fistL: [115, 165], fistR: [372, 250] };
const at = (k) => `transform-origin:${PIV[k][0]}px ${PIV[k][1]}px`;
const style = [
  `.a-torso{${at('torso')};animation:breathe 3.2s ease-in-out infinite alternate}`,
  `.a-loin{${at('loin')};animation:loin 3.2s ease-in-out infinite alternate}`,
  `.a-head{${at('head')};animation:head 3.2s ease-in-out infinite alternate}`,
  `.a-shR{${at('shR')};animation:lift 3.2s ease-in-out infinite alternate}`,
  `.a-armR{${at('armR')};animation:armR 3.2s ease-in-out infinite alternate}`,
  `.a-armL{${at('armL')};animation:lift 3.2s ease-in-out infinite alternate}`,
  `.a-fistL{${at('fistL')};animation:fistL 2.6s ease-in-out infinite alternate}`,
  `.a-fistR{${at('fistR')};animation:fistR 2.1s ease-in-out infinite alternate}`,
  '.a-glow{animation:glow 1.7s ease-in-out infinite alternate}',
  '.a-glow2{animation:glow 2.3s ease-in-out -0.8s infinite alternate}',
  '.a-eyes{animation:eyes 3.8s linear infinite}',
  '.a-emb1,.a-emb2,.a-emb3,.a-emb4{transform-box:fill-box;transform-origin:center;opacity:0}',
  '.a-emb1{animation:emb1 2.6s ease-out infinite}.a-emb2{animation:emb2 3.1s ease-out -1.2s infinite}',
  '.a-emb3{animation:emb3 2.2s ease-out -0.7s infinite}.a-emb4{animation:emb4 2.9s ease-out -2s infinite}',
  '@keyframes breathe{from{transform:none}to{transform:scale(1.008,1.016)}}',
  '@keyframes loin{from{transform:none}to{transform:rotate(0.8deg)}}',
  '@keyframes head{from{transform:none}to{transform:translateY(-2.4px) rotate(-0.8deg)}}',
  '@keyframes lift{from{transform:none}to{transform:translateY(-2.2px)}}',
  '@keyframes armR{from{transform:none}to{transform:translateY(-1.6px) rotate(-0.6deg)}}',
  '@keyframes fistL{from{transform:none}to{transform:translate(1px,-2.6px) rotate(-2deg)}}',
  '@keyframes fistR{from{transform:none}to{transform:translateY(-1.6px) rotate(1.6deg) scale(1.015)}}',
  '@keyframes glow{from{opacity:1}to{opacity:0.5}}',
  '@keyframes eyes{0%,60%{opacity:1}62%{opacity:0.6}64%,88%{opacity:1}90%,94%{opacity:0.35}97%,100%{opacity:1}}',
  '@keyframes emb1{0%{opacity:0;transform:none}15%{opacity:1}100%{opacity:0;transform:translate(-7px,-28px) scale(0.4)}}',
  '@keyframes emb2{0%{opacity:0;transform:none}15%{opacity:1}100%{opacity:0;transform:translate(8px,-26px) scale(0.4)}}',
  '@keyframes emb3{0%{opacity:0;transform:none}15%{opacity:1}100%{opacity:0;transform:translate(-5px,-22px) scale(0.4)}}',
  '@keyframes emb4{0%{opacity:0;transform:none}15%{opacity:1}100%{opacity:0;transform:translate(6px,-24px) scale(0.4)}}',
  // le coup de poing
  ...['torso', 'loin', 'head', 'shR', 'armR', 'armL', 'fistL', 'fistR'].map((k) => `.atk .a-${k}{animation:${k}-atk .75s ease-in-out}`),
  '.atk .a-eyes{animation:none}.atk .a-glow,.atk .a-glow2{animation:glow-atk .75s ease-in-out}.atk .a-hit{animation:hit .75s linear}',
  atk('torso-atk', PIV.torso), atk('loin-atk', PIV.loin),
  atk('head-atk', PIV.head, { 30: [0, 2, -4], 46: [4, 0, 4], 60: [3, 0, 3], 80: [0, 0, -0.5] }),
  atk('shR-atk', PIV.shR, { 30: [-8, 2], 46: [16, -3], 60: [13, -3] }),
  atk('armR-atk', PIV.armR, { 30: [-14, 4, 6], 46: [34, -10, -12], 60: [28, -8, -10], 80: [2, 0, 0] }),
  atk('armL-atk', PIV.armL, { 30: [0, -2] }),
  atk('fistL-atk', PIV.fistL, { 30: [2, -5, -3], 46: [6, 3, 4], 60: [5, 2, 3] }),
  atk('fistR-atk', PIV.fistR, { 30: [-24, 4, -10, 0.96], 46: [70, -36, 8, 1.14], 60: [62, -31, 6, 1.1], 80: [5, -2, 0, 1] }),
  '@keyframes glow-atk{0%{opacity:1}30%{opacity:0.45}46%,60%{opacity:1}100%{opacity:1}}',
  '.a-hit{transform-box:fill-box;transform-origin:center}',
  '@keyframes hit{0%,40%{opacity:0;transform:scale(0.5)}48%{opacity:1;transform:scale(1)}70%{opacity:0;transform:scale(1.35)}100%{opacity:0;transform:scale(1.35)}}',
].join('');

module.exports = { id: 'knights-8', w: W, h: H, pad: 110, foot: [212, 406], svg: (anime = true) => figure({ w: W, h: H, pad: 110, defs, style, parts, anime }) };
