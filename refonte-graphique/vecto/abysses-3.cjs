// La méduse des abysses (abysses-3) : redessinée par le code d'après le dessin d'origine, dans le même cadre
// (455 × 408, mêmes proportions, même pose) : grande ombrelle violette brillante au regard furieux, sous elle un rideau
// de voiles rose pâle rayé de magenta qui descend jusqu'au sol, des voiles lavande et des rubans prune sur la gauche,
// et un long bras qui part à droite et se termine par une boule rose lumineuse.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : l'ombrelle se contracte et le long bras se replie, puis elle se
// détend d'un coup, bondit en avant et le bras fouette vers la droite (la boule s'illumine) ; voiles et tentacules
// traînent derrière le mouvement.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 455, H = 408, PAD = 84;

// ---------- couleurs ----------
const PINK = { streak: '#e44cbc' };
const LAV = { hi: '#f6e8fc', base: '#e2c8f2', mid: '#bc92e6', deep: '#8a52d2' };
const PLUM = { hi: '#c0609e', base: '#7e2866', deep: '#4c0e3e' };
const GLOW = '#ff8ee0';
// les ombres portées : une teinte par matière qui la reçoit
const SH = { pink: '#7a3c9a', lav: '#4a1a86', vio: '#2a0c5a' };

// ---------- outils ----------
/**
 * Un ruban lisse le long d'une ligne : `pts` = [x, y, largeur] ; bords lissés (Catmull-Rom), bouts arrondis.
 * Sert aux voiles, aux rubans et aux rayures : des formes nettes, d'épaisseur variable, sans trait dur.
 */
function strip(pts) {
  const N = pts.length, L = [], R = [];
  for (let i = 0; i < N; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(N - 1, i + 1)];
    let tx = b[0] - a[0], ty = b[1] - a[1];
    const tl = Math.hypot(tx, ty) || 1; tx /= tl; ty /= tl;
    const h = pts[i][2] / 2;
    L.push([pts[i][0] - ty * h, pts[i][1] + tx * h]);
    R.push([pts[i][0] + ty * h, pts[i][1] - tx * h]);
  }
  const smooth = (P) => {
    let d = '';
    for (let i = 0; i < P.length - 1; i++) {
      const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)];
      d += ` C${n(p1[0] + (p2[0] - p0[0]) / 6)} ${n(p1[1] + (p2[1] - p0[1]) / 6)} ${n(p2[0] - (p3[0] - p1[0]) / 6)} ${n(p2[1] - (p3[1] - p1[1]) / 6)} ${n(p2[0])} ${n(p2[1])}`;
    }
    return d;
  };
  const Rr = R.slice().reverse(), he = n(pts[N - 1][2] / 2), hs = n(pts[0][2] / 2);
  return `M${n(L[0][0])} ${n(L[0][1])}${smooth(L)} A${he} ${he} 0 0 0 ${n(Rr[0][0])} ${n(Rr[0][1])}${smooth(Rr)} A${hs} ${hs} 0 0 0 ${n(L[0][0])} ${n(L[0][1])} Z`;
}
/** La même ligne, décalée vers sa gauche (+) ou sa droite (−) et amincie : pour poser un reflet ou une ombre dans un ruban. */
const inner = (pts, off, k) => pts.map((p, i) => {
  const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
  let tx = b[0] - a[0], ty = b[1] - a[1];
  const tl = Math.hypot(tx, ty) || 1; tx /= tl; ty /= tl;
  return [p[0] - ty * off * p[2], p[1] + tx * off * p[2], p[2] * k];
});
const rot = (p, c, deg) => { const a = (deg * Math.PI) / 180, x = p[0] - c[0], y = p[1] - c[1]; return [c[0] + x * Math.cos(a) - y * Math.sin(a), c[1] + x * Math.sin(a) + y * Math.cos(a)]; };

// ---------- les lignes des voiles et des rubans (x, y, largeur), de leur racine sous l'ombrelle à leur bout ----------
const L2 = [[160, 140, 12], [140, 160, 12], [120, 184, 12], [104, 210, 11.5], [94, 240, 11], [90, 272, 11], [86, 302, 11], [77, 328, 11], [63, 348, 12], [48, 362, 14], [38, 371, 15]];
const L3 = [[182, 146, 12], [166, 168, 12], [150, 192, 12], [136, 220, 11.5], [126, 252, 11], [120, 286, 11], [116, 318, 11], [108, 344, 11.5], [94, 364, 12.5], [78, 378, 14], [66, 384, 15]];
const L4 = [[178, 150, 11], [166, 176, 11], [154, 206, 10.5], [146, 240, 10], [141, 276, 10], [138, 310, 10], [132, 338, 10.5], [122, 358, 11], [110, 372, 12], [100, 380, 13]];
const P1 = [[194, 150, 8], [182, 190, 8], [172, 230, 8.5], [164, 270, 8], [158, 304, 7.5], [152, 330, 7], [145, 352, 6.5], [137, 368, 6], [129, 380, 5.5], [122, 388, 5], [117, 385, 4.5], [118, 378, 4]];
const P3 = [[226, 340, 7], [215, 355, 7], [201, 368, 6.5], [189, 378, 6], [183, 388, 5.5], [185, 396, 5], [191, 397, 4.5]];
const P4 = [[284, 270, 6.5], [291, 285, 6.5], [297, 300, 6], [301, 312, 5.5], [306, 320, 5], [311, 322, 4.5]];
// les rayures magenta du rideau : de longues flammèches ondulées, d'épaisseurs différentes
const STREAKS = [
  [[207, 178, 1.2], [209, 204, 4], [205, 240, 5], [209, 276, 4.8], [206, 312, 3.6], [208, 338, 1]],
  [[252, 180, 1.2], [255, 210, 4.2], [250, 250, 5.2], [255, 290, 5], [251, 326, 3.6], [253, 350, 0.8]],
  [[189, 240, 1], [191, 262, 3.6], [186, 294, 4], [189, 322, 2.6], [188, 336, 0.6]],
  [[280, 194, 1], [282, 216, 3.4], [278, 248, 3.8], [281, 276, 2.4], [280, 292, 0.6]],
  [[231, 272, 1], [233, 296, 3.6], [229, 326, 3.8], [232, 350, 2], [231, 362, 0.5]],
];

// ---------- le long bras : trois morceaux en chaîne (haut, bas, boule) ----------
const ROOT = [322, 182], ELBOW = [346, 268], TIP = [412, 261], BALL = [428, 252];
/** La traînée de la boule pendant le coup de fouet : l'arc qu'elle vient de parcourir autour de la racine, effilé. */
const smearD = (() => {
  const out = [], inn = [];
  for (let k = 0; k <= 10; k++) {
    const t = k / 10, w = 19 * (1 - t) + 1, p = rot(BALL, ROOT, 30 * t);
    const dx = p[0] - ROOT[0], dy = p[1] - ROOT[1], l = Math.hypot(dx, dy);
    out.push([p[0] + (dx / l) * w, p[1] + (dy / l) * w]);
    inn.push([p[0] - (dx / l) * w, p[1] - (dy / l) * w]);
  }
  const pts = [...out, ...inn.reverse()];
  return `M${pts.map((q) => `${n(q[0])} ${n(q[1])}`).join(' L')} Z`;
})();
const SM0 = rot(BALL, ROOT, 30);

// ---------- dégradés ----------
const defs = [
  // l'ombrelle : claire en haut à droite, profonde en bas à gauche
  rad('g-bell', 330, 26, 330, [[0, '#cc94ff'], [0.3, '#9e54e6'], [0.6, '#7632c6'], [1, '#4a1a98']]),
  lin('g-rimR', 0, 0, 1, 0, [[0, '#c898ff', 0], [1, '#d8b0ff', 0.75]], false),
  rad('g-face', 0.5, 0.35, 0.7, [[0, '#5a20a8', 0.6], [1, '#5a20a8', 0]], false),
  lin('g-rib', 0, 0, 0, 1, [[0, '#f0dcff', 0.75], [0.6, '#e0c0ff', 0.35], [1, '#e0c0ff', 0]], false),
  lin('g-lip', 0, 0, 0, 1, [[0, '#e8c8ff'], [1, '#b888ee']], false),
  rad('g-spot', 0.4, 0.35, 0.65, [[0, '#ffffff', 0.85], [0.6, '#f0d8ff', 0.5], [1, '#e0c0ff', 0.25]], false),
  // le rideau de voiles
  lin('g-col', 0, 150, 0, 400, [[0, '#f8d2ee'], [0.35, '#fde6f5'], [0.7, '#f8d4ee'], [1, '#e8bee8']]),
  lin('g-colL', 150, 0, 210, 0, [[0, '#b084dc', 0.9], [0.4, '#d4b0e6', 0.45], [1, '#e2c0ec', 0]]),
  lin('g-colTop', 0, 150, 0, 216, [[0, '#6a2aa6', 0.55], [0.4, '#8a4ab8', 0.22], [1, '#8a4ab8', 0]]),
  lin('g-colLow', 0, 296, 0, 400, [[0, '#9a66d2', 0], [0.45, '#9a66d2', 0.6], [1, '#8050c4', 0.92]]),
  lin('g-streak', 0, 0, 0, 1, [[0, PINK.streak, 0.2], [0.2, PINK.streak, 0.9], [0.8, '#d846b4', 0.75], [1, '#d846b4', 0.1]], false),
  // les tentacules
  lin('g-t1', 0, 0, 1, 0, [[0, '#5a24b0'], [0.45, '#8442d8'], [1, '#a466ec']], false),
  lin('g-veil', 0, 0, 1, 0, [[0, LAV.deep], [0.35, LAV.mid], [0.7, LAV.base], [1, LAV.hi]], false),
  lin('g-veil2', 0, 0, 1, 0, [[0, '#a86ad6'], [0.35, '#d8a8e6'], [0.7, '#f2d2ee'], [1, '#fff0fa']], false),
  lin('g-plum', 0, 0, 1, 0, [[0, PLUM.deep], [0.5, PLUM.base], [1, '#9a3a80']], false),
  // le bras et sa boule
  lin('g-arm', 0, 0, 1, 0, [[0, '#a886d6'], [0.35, '#dcc6f0'], [0.7, '#f8eefc'], [1, '#e6d4f4']], false),
  lin('g-armL', 0, 0, 0, 1, [[0, '#f8eefc'], [0.5, '#ead8f6'], [1, '#c6a4e4']], false),
  lin('g-armTop', 0, 172, 0, 222, [[0, '#4a1c96', 0.75], [1, '#4a1c96', 0]]),
  rad('g-ball', 0.62, 0.35, 0.75, [[0, '#ffffff'], [0.35, '#ffd8f4'], [0.75, '#f6a6e2'], [1, '#e078c8']], false),
  rad('g-glow', 0.5, 0.5, 0.5, [[0, GLOW, 0.75], [0.45, GLOW, 0.32], [1, GLOW, 0]], false),
  lin('g-smear', n(BALL[0]), n(BALL[1]), n(SM0[0]), n(SM0[1]), [[0, '#ffe2f6', 0.9], [0.5, '#ffb8ea', 0.45], [1, '#ffb8ea', 0]]),
  // les yeux
  rad('g-iris', 0.5, 0.62, 0.62, [[0, '#fff2a6'], [0.35, '#ffcc30'], [0.75, '#e8980e'], [1, '#a65a06']], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#3a0e5a', 0.7], [0.5, '#3a0e5a', 0]], false),
].join('');

// ---------- silhouettes ----------
const S = {
  // le grand tentacule violet de gauche, qui part sous l'ombrelle et descend en S jusqu'au sol
  t1: 'M188 138 C160 140 128 148 104 157 C96 160 90 164 84 168 C64 180 50 198 45 220 C40 244 45 262 45 280 C45 296 39 310 27 322 C19 330 10 334 4 337 C1 341 5 347 12 346 C23 343 35 335 45 325 C57 311 63 296 64 280 C65 262 59 246 63 227 C67 208 79 194 97 184 C118 172 148 166 190 162 Z',
  // deux voiles lavande au bout en palette, sur la gauche
  t2: strip(L2),
  t3: strip(L3),
  // un troisième voile, plus rose, et le ruban prune, plus fin, au bout recourbé
  t4: strip(L4),
  tp1: strip(P1),
  // les rubans prune qu'on voit entre les deux pieds du rideau, et à droite
  tp3: strip(P3),
  tp4: strip(P4),
  // le rideau de voiles : il part sous l'ombrelle et se pose au sol sur deux « pieds »
  col: 'M178 148 L300 148 C302 180 302 220 301 252 C301 274 300 292 297 308 C294 326 288 342 280 354 C273 364 264 371 256 376 C251 380 249 385 250 390 C251 394 252 398 250 401 C246 404 236 404 230 401 C226 398 225 392 225 384 C224 374 224 364 222 354 C212 360 198 366 186 372 C178 377 172 383 169 389 C166 395 160 399 150 399 C142 399 136 398 132 396 C128 393 128 389 131 385 C137 377 144 368 148 358 C152 346 153 332 153 316 C153 302 155 290 160 278 C164 262 168 236 170 210 C172 188 174 166 178 148 Z',
  // le long bras : le haut (jusqu'au coude), le bas (jusqu'à la boule), la boule
  armU: 'M303 160 L343 160 C341 188 339 216 342 236 C344 248 349 257 357 262 C361 266 362 272 360 278 C356 283 349 284 342 281 C332 276 323 266 317 254 C310 240 306 222 305 204 C304 188 304 174 303 160 Z',
  armL: 'M336 262 C340 256 349 255 356 261 C362 266 370 269 380 268 C390 267 398 263 405 257 C410 253 416 252 419 256 C422 261 419 268 414 271 C406 277 396 281 384 282 C370 284 356 282 345 277 C337 274 333 268 336 262 Z',
  ball: 'M408 244 C411 236 419 231 428 231 C439 231 448 238 450 248 C452 259 446 268 436 271 C428 274 418 272 412 266 C408 262 406 258 406 254 C404 251 405 247 408 244 Z',
  // l'ombrelle, devant tout
  bell: 'M108 149 C106 128 110 104 120 85 C132 60 152 36 180 22 C204 10 234 4 265 4 C300 4 332 14 354 32 C372 48 382 76 384 110 C386 132 384 156 380 176 C377 188 374 198 370 206 C368 210 366 212 364 212 C361 210 359 205 356 200 C352 196 346 194 340 192 C328 190 316 190 305 190 C296 189 286 186 276 182 C264 177 250 172 236 170 C222 168 210 165 200 161 C186 158 168 156 154 155 C150 152 148 148 146 146 C140 144 132 143 124 144 C118 145 112 147 108 149 Z',
};

// ---------- les yeux ----------
/** Un œil de bête : tout doré (pas de blanc), pupille fendue, ombre de la paupière, reflets ; la paupière furieuse. */
function eye(key, white, cx, cy, r, pr, lid, lower, shut, hl) {
  return `<clipPath id="c-${key}"><path d="${white}"/></clipPath>`
    + `<path d="${white}" fill="#c87a0c"/>`
    + `<g clip-path="url(#c-${key})">`
    + `<circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#g-iris)"/>`
    + oval(n(cx + pr[0]), n(cy + pr[1]), pr[2], pr[3], '#1c0626')
    + `<rect x="${cx - r - 14}" y="${cy - r - 8}" width="${2 * r + 28}" height="${n(r * 1.3)}" fill="url(#g-lid)"/>`
    + dot(n(cx + hl[0]), n(cy + hl[1]), hl[2], '#fff')
    + dot(n(cx + hl[3]), n(cy + hl[4]), hl[5], '#fff', 0.9)
    + `</g>`
    + line(lower, '#5a2a8a', 1.4, 0.8) + line(lid, '#1c0838', 2.6)
    + `<g class="a-blink" opacity="0"><path d="${white}" fill="#5e24ac" stroke="#5e24ac" stroke-width="3"/>${line(shut, '#1c0838', 2.6)}</g>`;
}

/** Un voile : sa couleur, l'ombre de son bord gauche, une nappe de lumière, un reflet vif. */
const veil = (id, pts, grad = 'url(#g-veil)') => use(id, grad) + clip(id,
  shape(strip(inner(pts, 0.42, 0.42)), LAV.deep, 0.5)
  + shape(strip(inner(pts.slice(1, -2), -0.18, 0.3)), '#ffffff', 0.55));

// ---------- les morceaux, du fond vers le devant ----------
const parts = [
  // --- le grand tentacule violet ---
  { id: 't1', cls: 'a-t1', d: S.t1,
    body: use('t1', 'url(#g-t1)') + clip('t1',
      shape('M84 168 C64 180 50 198 45 220 C40 244 45 262 45 280 C45 296 39 310 27 322 C19 330 10 334 4 337 L10 340 C22 334 34 324 42 312 C50 298 52 282 52 266 C52 250 50 232 56 214 C62 198 74 184 90 174 Z', '#3e148a', 0.5)
      + shape('M150 152 C128 156 106 164 90 176 C104 168 124 162 148 158 Z', '#d4a8ff', 0.7)
      + shape('M88 184 C76 194 66 208 62 226 C58 246 62 264 62 280 C62 296 56 310 46 322 C58 308 66 294 66 278 C66 262 62 244 66 226 C70 210 78 196 88 184 Z', '#c494ff', 0.55)
      + shape('M58 300 C54 312 46 322 36 330 C46 324 54 316 58 306 Z', '#e6ccff', 0.7)
    ) },
  // --- les voiles lavande et les rubans prune ---
  { id: 't2', cls: 'a-t2', d: S.t2, shadow: [{ on: ['t1'], dx: -4, dy: 3, color: SH.lav, o: 0.4 }], body: veil('t2', L2) },
  { id: 't3', cls: 'a-t3', d: S.t3, shadow: [{ on: ['t1', 't2'], dx: -4, dy: 3, color: SH.lav, o: 0.4 }], body: veil('t3', L3) },
  { id: 't4', cls: 'a-t2', d: S.t4, shadow: [{ on: ['t3'], dx: -4, dy: 3, color: SH.lav, o: 0.4 }], body: veil('t4', L4, 'url(#g-veil2)') },
  { id: 'tp1', cls: 'a-tp', d: S.tp1, shadow: [{ on: ['t4', 't3'], dx: -4, dy: 3, color: SH.lav, o: 0.45 }],
    body: use('tp1', 'url(#g-plum)') + clip('tp1', shape(strip(inner(P1.slice(0, -3), -0.2, 0.3)), PLUM.hi, 0.75)) },
  { id: 'tp3', cls: 'a-col', d: S.tp3,
    body: use('tp3', 'url(#g-plum)') + clip('tp3', shape(strip(inner(P3.slice(0, -2), -0.2, 0.3)), PLUM.hi, 0.75)) },
  { id: 'tp4', cls: 'a-col', d: S.tp4,
    body: use('tp4', 'url(#g-plum)') + clip('tp4', shape(strip(inner(P4.slice(0, -1), -0.2, 0.3)), PLUM.hi, 0.8)) },

  // --- le rideau de voiles : deux grands plis, rayures magenta, bas lavande dans l'ombre ---
  { id: 'col', cls: 'a-col', d: S.col, shadow: [{ on: ['tp1', 't4', 't3', 'tp3', 'tp4'], dx: -5, dy: 3, color: SH.pink, o: 0.45 }],
    body: use('col', 'url(#g-col)') + clip('col',
      // le pli de gauche, dans l'ombre ; le bas lavande
      `<rect x="126" y="150" width="98" height="256" fill="url(#g-colL)"/>`
      + `<path d="M126 290 L226 290 L226 406 L126 406 Z" fill="url(#g-colLow)"/>`
      // le galbe du pli de gauche (un reflet doux)
      + shape('M180 214 C190 242 194 274 190 306 C188 326 182 342 174 356 C188 342 198 322 202 300 C206 270 198 238 182 214 Z', '#ffffff', 0.22)
      // le creux entre les deux plis, jusqu'à l'encoche du bas
      + shape('M214 250 C218 280 220 316 222 354 C216 330 212 300 208 276 C208 266 210 256 214 250 Z', '#b484d8', 0.55)
      // les rayures magenta
      + STREAKS.map((s, i) => shape(strip(s), 'url(#g-streak)', [1, 1, 0.8, 0.75, 0.7][i])).join('')
      // la lumière sur le pli de droite, venue d'en haut à droite
      + shape('M272 200 C286 230 290 264 286 298 C282 324 272 344 260 360 C278 340 292 310 294 276 C296 246 288 220 276 200 Z', '#ffffff', 0.55)
      + shape('M226 362 C228 376 232 390 238 398 C232 386 230 374 230 362 Z', '#ffffff', 0.5)
      // le haut du rideau, dans l'ombre de l'ombrelle
      + `<rect x="150" y="146" width="160" height="70" fill="url(#g-colTop)"/>`
    ) },

  // --- le long bras et sa boule ---
  { id: 'armU', cls: 'a-au', d: S.armU, shadow: [{ on: ['col', 'tp4'], dx: -4, dy: 3, color: SH.pink, o: 0.4 }],
    body: use('armU', 'url(#g-arm)') + clip('armU',
      `<rect x="296" y="160" width="70" height="64" fill="url(#g-armTop)"/>`
      + shape('M305 204 C306 222 310 240 317 254 C323 266 332 276 342 281 C330 280 318 268 312 254 C306 240 304 222 305 204 Z', '#9a76cc', 0.6)
      + shape('M332 196 C330 216 332 236 338 250 C344 260 350 266 356 270 C346 260 340 248 337 234 C334 220 334 208 334 196 Z', '#ffffff', 0.75)
    ) },
  { id: 'armL', cls: 'a-al', d: S.armL, shadow: [{ on: ['armU'], dx: -2, dy: 3, color: SH.lav, o: 0.2 }],
    body: use('armL', 'url(#g-armL)') + clip('armL',
      shape('M336 266 C344 276 360 281 378 281 C394 281 408 276 418 266 L420 274 C406 284 388 286 370 285 C352 284 340 278 334 270 Z', '#a886d6', 0.55)
      + shape('M356 266 C366 271 378 272 390 270 C398 268 405 264 410 259 C404 266 396 271 386 273 C374 275 364 273 356 268 Z', '#ffffff', 0.8)
    ) },
  { id: 'ball', cls: 'a-ball', d: S.ball,
    body: `<g class="a-smear" opacity="0"><path d="${smearD}" fill="url(#g-smear)"/></g>`
      + use('ball', 'url(#g-ball)') + clip('ball',
        shape('M406 254 C408 266 420 274 434 272 C444 270 450 262 451 252 C446 264 436 270 424 268 C416 266 410 262 406 254 Z', '#d468b8', 0.45)
        + oval(436, 242, 7, 4.5, '#ffffff', 0.9, 28) + dot(424, 238, 1.8, '#ffffff', 0.85)
      ) },

  // --- l'ombrelle : violet brillant, nervures, taches, reflets, puis le visage ---
  { id: 'bell', cls: 'a-bell', d: S.bell,
    shadow: [{ on: ['col', 't1', 't2', 't3', 't4', 'tp1', 'armU'], dx: -4, dy: 7, color: SH.vio, o: 0.5 }],
    body: use('bell', 'url(#g-bell)') + clip('bell',
      // le bord clair du côté de l'ombre (la lumière qui traverse l'ombrelle)
      shape('M108 149 C106 128 110 104 120 85 C132 60 152 36 180 22 C204 10 234 4 265 4 L262 12 C234 13 208 19 186 31 C160 46 140 68 128 92 C118 112 114 130 114 148 Z', '#d6a8ff', 0.55)
      // les nervures : quatre larges bandes claires qui partent du sommet et s'effacent vers le bord
      + shape('M252 10 C222 24 192 46 172 76 C158 98 150 122 150 148 C156 124 166 102 180 82 C200 54 226 32 258 14 Z', 'url(#g-rib)')
      + shape('M266 10 C246 34 230 64 222 96 C216 120 214 142 216 162 C222 140 228 118 236 96 C246 66 258 38 272 12 Z', 'url(#g-rib)')
      + shape('M284 10 C290 34 293 62 292 90 C291 104 290 116 288 126 C296 112 300 96 300 78 C300 54 296 32 290 10 Z', 'url(#g-rib)')
      + shape('M300 12 C326 34 346 64 356 98 C362 120 362 142 358 162 C368 140 370 116 366 94 C358 62 336 32 306 10 Z', 'url(#g-rib)')
      // la lèvre claire du bord, à gauche
      + shape('M108 149 C118 145 132 143 146 146 C150 150 152 153 156 155 C170 156 188 158 202 161 C214 165 226 168 238 170 L238 162 C226 160 214 157 202 153 C188 149 170 147 158 146 C152 141 140 137 126 137 C118 139 112 143 108 149 Z', 'url(#g-lip)', 0.85)
      // le visage : une plaque plus sombre autour des yeux, les orbites, le museau plus sombre au milieu
      + shape('M224 170 C222 146 228 120 242 104 C262 96 288 108 302 126 C318 118 340 110 356 112 C366 132 366 162 356 190 C340 194 318 192 300 190 C284 188 268 182 254 176 C242 172 232 171 224 170 Z', 'url(#g-face)')
      + shape('M244 124 C254 124 268 130 280 140 C290 148 296 154 298 160 C292 164 282 164 272 162 C260 160 250 154 246 146 C242 138 242 130 244 124 Z', '#4a1890', 0.45)
      + shape('M304 160 C314 152 328 144 344 140 C350 146 350 160 344 170 C334 176 320 176 310 172 C304 168 302 164 304 160 Z', '#4a1890', 0.4)
      + shape('M286 150 C292 154 300 156 306 156 C312 166 314 178 312 190 C304 190 294 189 284 186 C288 176 288 162 286 150 Z', '#4a1890', 0.45)
      // les taches claires et brillantes
      + `<circle cx="340" cy="94" r="6.5" fill="url(#g-spot)"/>` + `<circle cx="355" cy="131" r="5" fill="url(#g-spot)"/>`
      + `<circle cx="214" cy="54" r="4.5" fill="url(#g-spot)"/>` + `<circle cx="160" cy="112" r="4" fill="url(#g-spot)"/>`
      // le grand reflet brillant, en haut à droite, et son écho
      + shape('M292 14 C326 18 354 38 370 68 C374 78 376 88 375 98 C366 74 348 50 322 32 C312 25 302 19 292 14 Z', '#ffffff', 0.7)
      + oval(318, 34, 13, 5, '#ffffff', 0.55, 24) + oval(376, 122, 2.6, 9, '#ffffff', 0.5, 4)
      // le bord translucide, à droite et en bas à droite (la lumière passe au travers)
      + shape('M384 110 C386 132 384 156 380 176 C377 188 374 198 370 206 C368 210 366 212 364 212 C361 210 359 205 356 200 C362 200 366 196 370 188 C374 176 376 158 376 140 C376 128 376 118 374 110 Z', 'url(#g-rimR)')
      + shape('M305 190 C316 190 328 190 340 192 C346 194 352 196 356 200 C346 198 336 197 326 196 C318 195 310 193 305 190 Z', '#d2a6ff', 0.6)
      // un pli clair sous l'œil de droite, qui coule vers le bord
      + shape('M320 172 C322 178 322 186 320 192 C326 186 327 178 324 170 Z', '#c89cff', 0.6)
    )
      // les sourcils furieux : deux arêtes sombres qui plongent vers le milieu
      + shape('M236 107 C250 102 268 108 284 120 C294 128 302 138 306 150 C301 153 296 153 292 150 C284 141 273 134 261 129 C251 125 242 123 234 122 C230 118 231 111 236 107 Z', '#3c147e')
      + shape('M244 108 C258 106 274 113 288 126 C276 118 262 112 248 112 Z', '#9a60e2', 0.7)
      + shape('M300 152 C312 142 328 133 346 126 C352 124 356 127 354 132 C340 138 324 147 312 156 C306 159 300 158 300 152 Z', '#3c147e')
      + shape('M306 148 C318 140 332 133 346 128 C334 134 320 142 310 150 Z', '#9a60e2', 0.6)
      + dot(352, 128, 2.4, '#b880f0', 0.8)
      // les yeux
      + eye('eL', 'M251 136 C260 131 272 136 285 149 C281 155 272 159 263 158 C255 156 250 148 251 136 Z', 267, 147, 13, [5.5, 1, 4.6, 6.8],
        'M249 135 C260 129 273 135 287 150', 'M253 151 C258 157 268 160 278 156', 'M250 145 C260 152 274 154 286 150', [8.5, -4.5, 2.3, -3, 6, 1.3])
      + eye('eR', 'M313 156 C320 150 330 146 341 148 C343 157 338 166 329 168 C320 169 314 164 313 156 Z', 328, 158, 11, [-1.5, 0, 3.8, 5.8],
        'M311 156 C320 149 331 145 343 147', 'M315 163 C320 168 330 170 338 165', 'M312 160 C322 164 334 162 342 156', [1.5, -4, 2, -5, 4.5, 1.1]) },
];

// ---------- la vie au repos, puis l'attaque ----------
// Au repos : elle flotte, l'ombrelle bat doucement, chaque groupe de voiles ondule à son rythme, le bras se balance,
// la boule luit. Attaque : chaque morceau a sa version « .atk », qui finit exactement sur la pose de départ de son
// mouvement de repos (le passage de l'un à l'autre ne se voit pas).
const kf = (name, frames) => `@keyframes ${name}{${frames.map(([t, v, ease]) => `${n(t * 100)}%{transform:${v}${ease ? `;animation-timing-function:${ease}` : ''}}`).join('')}}`;
const R = (d) => `rotate(${d}deg)`;
const v = (a, b) => [b[0] - a[0], b[1] - a[1]];
const RE = v(ROOT, ELBOW), ET = v(ELBOW, TIP);
const armL = (A, B) => `rotate(${A}deg) translate(${RE[0]}px,${RE[1]}px) rotate(${B}deg) translate(${-RE[0]}px,${-RE[1]}px)`;
const ball = (A, B, C) => `rotate(${A}deg) translate(${RE[0]}px,${RE[1]}px) rotate(${B}deg) translate(${ET[0]}px,${ET[1]}px) rotate(${C}deg) translate(${-RE[0] - ET[0]}px,${-RE[1] - ET[1]}px)`;
// la chaîne du bras : [instant, A (racine), B (coude), C (boule)] — repos, replié, fouet, rebond, repos
const IDLE_ARM = [[-1.5, 2, -4], [2, -3, 5]];
const WHIP = [[0, ...IDLE_ARM[0]], [0.28, 18, 34, 24], [0.45, -38, 28, -10], [0.58, -30, 16, 4], [0.76, -6, 6, -2], [1, ...IDLE_ARM[0]]];
const EASE = ['cubic-bezier(.3,0,.4,1)', 'cubic-bezier(.6,0,.85,.5)', 'cubic-bezier(.2,.6,.4,1)', 'ease-in-out', 'ease-in-out'];
const lag = (base, a, b) => [[0, R(base)], [0.28, R(base + a)], [0.47, R(base + b)], [0.66, R(base - b * 0.35)], [0.84, R(base + b * 0.12)], [1, R(base)]];
const style = [
  `.a-bob{animation:bob 3.6s ease-in-out infinite alternate}`,
  `.a-bell{transform-origin:246px 176px;animation:bell 1.7s ease-in-out infinite alternate}`,
  `.a-t1{transform-origin:170px 150px;animation:t1 3s ease-in-out infinite alternate}`,
  `.a-t2{transform-origin:156px 146px;animation:t2 2.6s ease-in-out infinite alternate-reverse}`,
  `.a-t3{transform-origin:178px 150px;animation:t3 2.8s ease-in-out infinite alternate}`,
  `.a-tp{transform-origin:186px 152px;animation:tp 2.2s ease-in-out infinite alternate-reverse}`,
  `.a-col{transform-origin:238px 152px;animation:col 3.4s ease-in-out infinite alternate}`,
  `.a-au,.a-al,.a-ball{transform-origin:${ROOT[0]}px ${ROOT[1]}px}`,
  `.a-au{animation:au 2.4s ease-in-out infinite alternate}.a-al{animation:al 2.4s ease-in-out infinite alternate}.a-ball{animation:ba 2.4s ease-in-out infinite alternate}`,
  `.a-glow{transform-origin:${BALL[0]}px ${BALL[1]}px;animation:glow 1.3s ease-in-out infinite alternate}`,
  `.a-blink{animation:blink 5.2s linear infinite}`,
  kf('bob', [[0, 'translate(0px,-3px)'], [1, 'translate(0px,3px)']]),
  kf('bell', [[0, 'scale(1.02,0.975)'], [1, 'scale(0.985,1.02)']]),
  kf('t1', [[0, R(-2)], [1, R(2.5)]]),
  kf('t2', [[0, R(2)], [1, R(-2.2)]]),
  kf('t3', [[0, R(-1.8)], [1, R(2.2)]]),
  kf('tp', [[0, R(2.5)], [1, R(-2)]]),
  kf('col', [[0, R(-0.8)], [1, R(1)]]),
  kf('au', IDLE_ARM.map(([A], i) => [i, R(A)])),
  kf('al', IDLE_ARM.map(([A, B], i) => [i, armL(A, B)])),
  kf('ba', IDLE_ARM.map(([A, B, C], i) => [i, ball(A, B, C)])),
  kf('glow', [[0, 'scale(0.92)'], [1, 'scale(1.08)']]),
  `@keyframes blink{0%,94%{opacity:0}95.5%,97.5%{opacity:1}99%,100%{opacity:0}}`,
  // l'attaque
  `.atk .a-bob{animation:bob-atk .75s linear both}.atk .a-bell{animation:bell-atk .75s linear both}`,
  `.atk .a-au{animation:au-atk .75s linear both}.atk .a-al{animation:al-atk .75s linear both}.atk .a-ball{animation:ba-atk .75s linear both}`,
  `.atk .a-glow{animation:glow-atk .75s ease-in-out both}.atk .a-smear{animation:smear .75s linear both}`,
  `.atk .a-t1{animation:t1-atk .75s ease-in-out both}.atk .a-t2{animation:t2-atk .75s ease-in-out both}.atk .a-t3{animation:t3-atk .75s ease-in-out both}`,
  `.atk .a-tp{animation:tp-atk .75s ease-in-out both}.atk .a-col{animation:col-atk .75s ease-in-out both}`,
  kf('bob-atk', [[0, 'translate(0px,-3px)', EASE[0]], [0.28, 'translate(-8px,3px)', EASE[1]], [0.45, 'translate(14px,-7px)', EASE[2]], [0.6, 'translate(10px,-5px)', EASE[3]], [1, 'translate(0px,-3px)']]),
  kf('bell-atk', [[0, 'scale(1.02,0.975)', EASE[0]], [0.28, 'scale(1.1,0.85)', EASE[1]], [0.44, 'scale(0.93,1.1)', EASE[2]], [0.58, 'scale(1.04,0.96)', EASE[3]], [0.78, 'scale(0.99,1.01)', EASE[4]], [1, 'scale(1.02,0.975)']]),
  kf('au-atk', WHIP.map(([t, A], i) => [t, R(A), EASE[i]])),
  kf('al-atk', WHIP.map(([t, A, B], i) => [t, armL(A, B), EASE[i]])),
  kf('ba-atk', WHIP.map(([t, A, B, C], i) => [t, ball(A, B, C), EASE[i]])),
  kf('glow-atk', [[0, 'scale(0.92)'], [0.3, 'scale(0.8)'], [0.46, 'scale(1.45)'], [0.62, 'scale(1.15)'], [1, 'scale(0.92)']]),
  `@keyframes smear{0%,33%{opacity:0}39%{opacity:.85}45%{opacity:1}51%{opacity:.35}56%,100%{opacity:0}}`,
  kf('t1-atk', lag(-2, -4, 6)),
  kf('t2-atk', lag(-2.2, -5, 7)),
  kf('t3-atk', lag(-1.8, -5, 7)),
  kf('tp-atk', lag(-2, -6, 8)),
  kf('col-atk', lag(-0.8, -2, 3)),
].join('');

// la lueur de la boule : derrière tout le personnage (sinon elle salirait le contour), et elle suit la boule
const GLOW_SVG = `<g class="a-ball"><g class="a-glow"><circle cx="${BALL[0]}" cy="${BALL[1]}" r="40" fill="url(#g-glow)"/></g></g>`;

const svg = (anime = true) => {
  const s = figure({ w: W, h: H, pad: PAD, defs, style, parts, anime });
  // la lueur avant le contour, puis le tout dans un groupe qui flotte
  const at = s.indexOf('<g fill=');
  const body = s.slice(at, s.lastIndexOf('</svg>'));
  return `${s.slice(0, at)}<g class="a-bob">${anime ? GLOW_SVG : GLOW_SVG.replace(/ class="[^"]+"/g, '')}${body}</g></svg>`;
};

module.exports = { id: 'abysses-3', w: W, h: H, pad: PAD, foot: [195, 400], svg };
