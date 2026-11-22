// Le pétard (parade-1), monstre de la Parade des pétards : redessiné par le code d'après le dessin d'origine, dans le
// même cadre (361 × 410, mêmes proportions, même pose) : corps rouge en tube, un peu penché, deux bagues dorées
// cloutées en haut et en bas, couronne de pointes d'or, mèche tressée allumée avec sa gerbe d'étincelles, visage en
// colère (sourcils épais, yeux jaunes, grande gueule aux dents pointues), petits bras et jambes noirs qui courent,
// des moufles et des chaussures crème ; la moufle gauche serre un petit pétard rouge.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 361, H = 410;

// ---------- couleurs ----------
const GOLD = { hi: '#fff3c4', lite: '#fde08a', base: '#f6b83c', mid: '#e3931f', shade: '#b0661a', deep: '#7a3e0e', line: '#6a3a10' };
const INK = { hi: '#9a95a4', lite: '#625c6c', base: '#3c3644', shade: '#28222e', deep: '#18131c' };
const CREAM = { hi: '#f4ece0', lite: '#d8ccbe', base: '#b4a698', shade: '#857668', deep: '#54474a' };
const SH = { red: '#4a0610', gold: '#6a300a', ink: '#0c080e' };

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
/** Ruban effilé le long d'une ligne : pts = [[x, y, largeur], …]. */
function rib(pts, k = 1) {
  const L = [], R = [];
  pts.forEach(([x, y, w], i) => {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    let dx = b[0] - a[0], dy = b[1] - a[1];
    const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
    const h = (w * k) / 2;
    L.push([x - dy * h, y + dx * h]); R.push([x + dy * h, y - dx * h]);
  });
  R.reverse();
  return `M${n(L[0][0])} ${n(L[0][1])}${cr(L)}L${n(R[0][0])} ${n(R[0][1])}${cr(R)}Z`;
}
/** Un reflet ou une ombre effilée le long d'une ligne. */
const glint = (pts, color, o = 1) => shape(rib(pts), color, o);
/** Un clou doré : dôme, ombre portée en bas à gauche, reflet en haut à droite. */
const stud = (x, y, r = 4.4) => oval(x - 1.2, y + 1.6, r, r * 0.9, GOLD.line, 0.55)
  + `<circle cx="${x}" cy="${y}" r="${r}" fill="url(#g-stud)"/>` + oval(x + r * 0.3, y - r * 0.35, r * 0.38, r * 0.28, GOLD.hi, 0.95, -25);
/**
 * Une dent pointue : un triangle aux flancs un peu bombés, la moitié gauche dans l'ombre, un reflet sur le flanc droit.
 * b1, b2 = les deux coins de la racine ; t = la pointe.
 */
function tooth([x1, y1], [x2, y2], [tx, ty]) {
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2, bulge = 0.18;
  const c1 = [n(x1 + (tx - x1) * 0.5 - (ty - y1) * bulge * Math.sign(x2 - x1) * 0.4), n(y1 + (ty - y1) * 0.5 + (tx - x1) * bulge * 0.4)];
  const c2 = [n(x2 + (tx - x2) * 0.5 + (ty - y2) * bulge * Math.sign(x2 - x1) * 0.4), n(y2 + (ty - y2) * 0.5 - (tx - x2) * bulge * 0.4)];
  const d = `M${x1} ${y1}Q${c1[0]} ${c1[1]} ${tx} ${ty}Q${c2[0]} ${c2[1]} ${x2} ${y2}Z`;
  const half = `M${x1} ${y1}Q${c1[0]} ${c1[1]} ${tx} ${ty}L${n(mx + (tx - mx) * 0.15)} ${n(my + (ty - my) * 0.15)}Z`;
  return shape(d, '#f4eee2') + shape(half, '#cdbfb2', 0.85) + line(`M${n(mx + (x2 - mx) * 0.55)} ${n(my + (y2 - my) * 0.55)}L${n(tx + (x2 - tx) * 0.18)} ${n(ty + (y2 - ty) * 0.18)}`, '#ffffff', 1.3, 0.9);
}

// ---------- dégradés ----------
// le corps est un tube penché : ses couleurs vont d'un bord à l'autre, en travers de son axe
const ACROSS = [110, 280, 255, 297];
const defs = [
  lin('g-red', ...ACROSS, [[0, '#b04a6a'], [0.06, '#86182a'], [0.16, '#b82422'], [0.32, '#de372b'], [0.52, '#f25a3a'], [0.7, '#ee4a32'], [0.87, '#c8301f'], [1, '#801712']]),
  lin('g-goldT', ...ACROSS, [[0, '#8a4e1c'], [0.08, '#c07a22'], [0.28, '#f0bc48'], [0.52, '#ffe9a2'], [0.72, '#f6c556'], [0.9, '#b8701a'], [1, '#cf8a22']]),
  lin('g-goldB', ...ACROSS, [[0, '#7a3e0e'], [0.1, '#b0641a'], [0.34, '#e89e30'], [0.58, '#f6c25a'], [0.8, '#dc962c'], [0.94, '#8e4e14'], [1, '#a8681c']]),
  lin('g-top', 0, 0, 0, 1, [[0, '#f6b88a'], [1, '#e0805a']], false),
  rad('g-stud', 0.62, 0.35, 0.75, [[0, '#ffe7a8'], [0.4, '#d89a3a'], [1, '#7a4410']], false),
  lin('g-spike', 0, 0, 1, 0, [[0, '#d4841c'], [0.45, '#f6b938'], [0.7, '#ffe27a'], [1, '#fff3b8']], false),
  lin('g-ink', 0, 0, 0, 1, [[0, '#4c4656'], [0.55, INK.base], [1, INK.deep]], false),
  lin('g-cream', 0, 0, 0, 1, [[0, '#d9cec2'], [0.5, CREAM.base], [1, CREAM.shade]], false),
  lin('g-stick', 0, 0, 1, 1, [[0, '#ff8a6a'], [0.3, '#e8402e'], [0.75, '#b42420'], [1, '#6e1012']], false),
  lin('g-fuse', 0, 0, 0, 1, [[0, '#6e3820'], [0.5, '#4a2214'], [1, '#22100a']], false),
  lin('g-mouth', 0, 0, 0, 1, [[0, '#14040a'], [0.6, '#2c0a12'], [1, '#4a1420']], false),
  rad('g-sclera', 0.35, 0.4, 0.8, [[0, '#fffbe2'], [0.35, '#fff0a0'], [0.7, '#f8cf48'], [1, '#e39624']], false),
  rad('g-pupil', 0.4, 0.35, 0.7, [[0, '#5a1a14'], [0.6, '#2e0a0a'], [1, '#160404']], false),
  lin('g-socket', 0, 0, 0, 1, [[0, '#3a0408', 0.95], [0.5, '#5a0a12', 0.75], [1, '#8a1a1a', 0]], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#3a0608', 0.75], [0.45, '#3a0608', 0]], false),
  rad('g-halo', 0.5, 0.5, 0.5, [[0, '#fff6d0', 0.95], [0.25, '#ffc850', 0.72], [0.6, '#ff962a', 0.36], [1, '#ff7a1e', 0]], false),
  rad('g-burst', 0.5, 0.5, 0.5, [[0, '#ffffff'], [0.3, '#fff4b0'], [0.65, '#ffc442'], [1, '#ff8a1c']], false),
  rad('g-ember', 0.5, 0.5, 0.5, [[0, '#fff2b0', 1], [0.4, '#ffb03a', 0.9], [1, '#ff7a1e', 0]], false),
  rad('g-soft', 0.5, 0.5, 0.5, [[0, '#fff2e0', 0.75], [1, '#fff2e0', 0]], false),
].join('');

// ---------- silhouettes ----------
const S = {
  // la jambe de derrière, lancée en arrière ; sa chaussure vue de dos
  legL: 'M140 335 L140 341 C134 348 126 356 117 360 C108 363 99 361 93 356 C90 362 88 368 87 374 L60 372 C60 360 63 348 69 341 C72 338 75 336 80 335 C92 335 108 336 124 335 Z',
  shoeL: 'M60 367 C68 363 80 363 88 366 C90 372 89 380 88 386 C85 391 79 394 72 393 C65 391 60 386 59 379 C58 375 59 370 60 367 Z',
  // la jambe de devant, qui avance ; sa chaussure, la pointe relevée
  legR: 'M150 336 L202 336 C204 346 206 356 208 366 L208 372 L182 372 C181 366 179 361 175 357 C168 352 160 348 151 346 Z',
  shoeR: 'M182 367 C190 364 202 364 208 367 C211 370 214 371 218 369 C224 365 231 362 238 361 C244 362 247 367 247 373 C246 380 241 385 234 389 C222 395 208 400 194 401 C187 401 182 397 181 390 C180 382 180 373 182 367 Z',
  // le bras droit (derrière le corps) et sa moufle crème
  armR: 'M240 290 C250 289 262 296 270 304 L278 312 L280 332 C270 338 258 341 246 341 L240 341 Z',
  fistR: 'M267 306 C275 302 287 301 296 304 C303 308 306 316 305 324 C304 332 298 338 289 340 C282 341 276 339 270 337 C264 334 261 326 262 318 C263 312 264 308 267 306 Z',
  // le petit pétard tenu dans la main gauche
  stick: 'M11 259 L50 223 C55 219 61 220 65 225 L69 230 C73 235 72 239 68 243 L29 281 A14.2 7 50.7 0 1 11 259 Z',
  // la moufle qui serre le bout du petit pétard
  handL: 'M50 237 C48 229 52 222 59 219 C65 216 72 217 76 222 C80 227 80 235 78 241 C76 247 71 252 64 253 C57 253 52 249 50 237 Z',
  // le bras gauche, qui sort d'un trou sur le flanc ; sa moufle (handL) serre le bout du petit pétard
  armL: 'M62 236 C66 228 76 226 86 232 C96 240 106 248 118 252 L122 254 L124 276 L116 276 C104 274 92 268 84 260 C78 256 72 254 66 252 C60 248 59 241 62 236 Z',
  // le corps : le tube, ses deux bagues, le dessous dans l'ombre
  body: 'M127 147 C150 139 185 136 210 137 C235 138 258 143 271 152 L271 184 C268 205 263 235 258 262 C255 280 253 292 252 300 L253 304 L251 333 C240 340 215 345 190 345 C160 345 128 340 105 330 L105 303 C107 300 109 298 110 296 C113 268 117 240 121 218 C123 200 125 186 126 180 Z',
  // la couronne : quatre pointes d'or plantées sur le dessus
  crown: 'M139 141 Q141 130 150 120 Q155 126 158 131 Q164 115 177 105 Q186 113 191 122 Q198 110 212 103 Q223 113 229 126 Q235 116 244 109 Q253 122 255 140 C238 146 200 147 160 145 C150 144 143 143 139 141 Z',
};
// la mèche : elle sort du dessus, derrière la grande pointe, se coude puis file vers la droite ; tracée par sa ligne
// du milieu (largeur qui s'affine vers le bout allumé)
const FUSE = [[226, 138, 13], [224, 122, 13.5], [217, 109, 14], [213, 100, 14], [220, 91, 14], [234, 85, 13.5], [249, 80, 13], [263, 76, 12], [276, 72, 9.5]];
S.fuse = rib(FUSE);

// ---------- les yeux ----------
const EYE_L = 'M161 212 L197 229 C197 235 193 240 185 241 C175 242 165 238 161 230 C159 225 159 218 161 212 Z';
const EYE_R = 'M219 226 L249 216 C251 222 250 232 245 238 C240 243 231 244 225 240 C220 236 218 231 219 226 Z';
/** Un œil : orbite sombre, blanc jaune en dégradé, grande pupille, ombre de la paupière, reflets ; puis le clignement. */
function eye(key, d, px, py, pr, shut, lid) {
  return `<path d="${d}" fill="#5a0a10" stroke="#5a0a10" stroke-width="5"/>`
    + `<clipPath id="c-${key}"><path d="${d}"/></clipPath><path d="${d}" fill="url(#g-sclera)"/>`
    + `<g clip-path="url(#c-${key})">`
    + `<circle cx="${px}" cy="${py}" r="${pr}" fill="url(#g-pupil)"/>`
    + `<circle cx="${px}" cy="${py}" r="${pr - 0.8}" fill="none" stroke="#7a2416" stroke-width="1.4" opacity="0.8"/>`
    + `<rect x="150" y="200" width="110" height="20" fill="url(#g-lid)" transform="translate(0 ${py - 222})"/>`
    + dot(n(px - pr * 0.38), n(py - pr * 0.34), n(pr * 0.3), '#fff') + dot(n(px + pr * 0.36), n(py + pr * 0.3), n(pr * 0.14), '#fff', 0.85)
    + '</g>'
    + line(lid, '#3a0408', 4.4)
    + `<g class="a-blink" opacity="0"><path d="${d}" fill="#d8382a" stroke="#d8382a" stroke-width="3"/>${line(lid, '#3a0408', 4.4)}${line(shut, '#4a060c', 3)}</g>`;
}

// ---------- la bouche ----------
const MOUTH = 'M154 260 C170 258 210 260 246 263 C248 276 248 292 246 303 C228 307 196 307 172 304 C164 303 158 301 154 299 C152 286 152 272 154 260 Z';
const TEETH_TOP = [[[160, 261], [174, 262], [166, 273]], [[180, 262], [196, 264], [187.5, 279]], [[202, 265], [217, 264], [209, 281]], [[221, 266], [236, 268], [229, 281]], [[236, 267], [244, 268], [238, 277]]];
const TEETH_LOW = [[[157, 297], [165, 297], [161, 291]], [[163, 297], [176, 297], [170.5, 285]], [[184, 299], [197, 300], [193, 290]], [[201, 302], [213, 302], [208, 294]], [[213, 302], [223, 303], [217.5, 292]]];

// ---------- le corps ----------
const BAND_T = 'M120 150 C121 161 274 166 276 154 L276 183 C274 195 121 190 120 178 Z';
const BAND_B = 'M100 300 C130 306 215 310 258 307 L258 334 C215 340 130 336 100 326 Z';
const bodyBody = use('body', 'url(#g-red)') + clip('body',
  // le reflet rose du bord gauche, la lumière douce du milieu, le bord droit dans l'ombre
  glint([[112, 300, 0], [116, 260, 4], [120, 220, 4.4], [124, 186, 3], [126, 176, 0]], '#e06a8a', 0.55)
  + oval(214, 232, 22, 60, 'url(#g-soft)', 0.35, 7)
  + glint([[266, 186, 0], [262, 220, 3.4], [257, 262, 3.4], [253, 296, 0]], '#ff9a6a', 0.55)
  // l'ombre portée de la bague du haut sur le tube, et le dessous du tube
  + shape('M118 180 C122 194 274 198 274 184 L274 196 C270 206 122 202 118 192 Z', SH.red, 0.3)
  + shape('M100 330 C130 342 215 346 258 336 L258 350 L100 350 Z', '#3a060c', 0.75)
  // le dessus du tube, vu d'un peu haut
  + `<ellipse cx="199" cy="147" rx="74" ry="9" transform="rotate(4 199 147)" fill="url(#g-top)"/>`
  + `<ellipse cx="199" cy="145" rx="64" ry="5.5" transform="rotate(4 199 145)" fill="#c8583c" opacity="0.45"/>`
  // la bague du haut et ses clous
  + `<path d="${BAND_T}" fill="url(#g-goldT)"/>`
  + glint([[124, 156, 0], [160, 161, 2.4], [200, 163, 2.6], [240, 162, 2.4], [272, 158, 0]], GOLD.hi, 0.9)
  + glint([[124, 182, 0], [160, 187, 2.4], [200, 189, 2.6], [240, 188, 2.4], [272, 184, 0]], GOLD.shade, 0.7)
  + stud(148, 167) + stud(184, 169) + stud(218, 171) + stud(252, 171, 4)
  // la bague du bas et ses clous (le petit losange entre deux clous)
  + `<path d="${BAND_B}" fill="url(#g-goldB)"/>`
  + glint([[104, 303, 0], [140, 307, 2.4], [190, 310, 2.6], [250, 309, 0]], GOLD.lite, 0.85)
  + glint([[104, 327, 0], [150, 334, 2.4], [200, 337, 2.6], [252, 334, 0]], GOLD.deep, 0.6)
  + stud(132, 315) + stud(170, 318) + stud(198, 320.5) + stud(234, 321, 4.2)
  + shape('M210 317 L214 322 L210 327 L206 322 Z', '#c86a1c') + shape('M210 317 L214 322 L210 322 Z', '#ffd27a')
  // le trou d'où sort le bras gauche : un bord de carton clair
  + shape('M114 252 C122 254 126 262 126 268 C126 274 122 279 115 280 C119 274 120 262 114 252 Z', '#f2dcc4', 0.95)
  // les orbites : l'ombre des sourcils creuse le dessus des yeux
  + shape('M149 198 C168 198 194 208 210 222 C210 234 203 242 190 244 C176 246 160 243 152 234 C147 224 147 210 149 198 Z', 'url(#g-socket)')
  + shape('M212 229 C228 216 248 203 267 196 C270 210 267 227 259 237 C250 245 236 248 225 246 C215 242 211 235 212 229 Z', 'url(#g-socket)')
  // les sourcils froncés : deux gros boudins rouges
  + `<path d="M154 190 Q183 197 205 216" fill="none" stroke="#6a0c12" stroke-width="17" stroke-linecap="round" transform="translate(-1.5 2.5)" opacity="0.6"/>`
  + `<path d="M154 190 Q183 197 205 216" fill="none" stroke="#d4362a" stroke-width="15" stroke-linecap="round"/>`
  + `<path d="M156 186 Q183 192 205 210" fill="none" stroke="#ff8a62" stroke-width="3.2" stroke-linecap="round" opacity="0.85"/>`
  + `<path d="M224 221 Q244 206 263 195" fill="none" stroke="#6a0c12" stroke-width="17" stroke-linecap="round" transform="translate(-1.5 2.5)" opacity="0.6"/>`
  + `<path d="M224 221 Q244 206 263 195" fill="none" stroke="#d4362a" stroke-width="15" stroke-linecap="round"/>`
  + `<path d="M224 215 Q243 200 262 189" fill="none" stroke="#ff8a62" stroke-width="3.2" stroke-linecap="round" opacity="0.85"/>`
  // les yeux
  + eye('eL', EYE_L, 187, 223, 8, 'M161 226 C170 236 186 238 197 231', 'M159 210 L199 230') + eye('eR', EYE_R, 232, 228, 7.5, 'M219 230 C228 240 243 238 250 226', 'M217 227 L251 215')
  // le nez : deux petites narines
  + oval(209.5, 244.5, 1.8, 1.3, '#5a0a10') + oval(215.5, 245.5, 1.8, 1.3, '#5a0a10')
  // la grande gueule : l'intérieur sombre, l'ombre de la lèvre du haut, les dents une à une
  + `<clipPath id="c-mouth"><path d="${MOUTH}"/></clipPath><path d="${MOUTH}" fill="#5a0a10" stroke="#5a0a10" stroke-width="3"/>`
  + `<path d="${MOUTH}" fill="url(#g-mouth)"/>`
  + `<g clip-path="url(#c-mouth)">`
  + `<g class="a-teethB">${TEETH_LOW.map((t) => tooth(...t)).join('')}</g>`
  + `<g class="a-teethT">${TEETH_TOP.map((t) => tooth(...t)).join('')}</g>`
  + '</g>'
  // la lèvre du bas, posée sur la bague
  + shape('M152 300 C170 305 208 307 246 302 L246 307 C210 311 170 309 152 305 Z', '#c22c24')
  + glint([[160, 304, 0], [200, 307, 2], [240, 304, 0]], '#ff7a5a', 0.8)
  // un reflet sur la joue, sous l'œil
  + glint([[174, 248, 0], [179, 248.5, 2], [184, 248, 0]], '#ffd2b8', 0.85)
);

// ---------- les morceaux, du fond vers le devant ----------
const parts = [
  // --- la jambe de derrière, lancée en arrière : cuisse vers la gauche, genou, tibia qui descend ---
  { id: 'legL', cls: 'a-legL', d: S.legL, body: use('legL', 'url(#g-ink)') + clip('legL',
    glint([[78, 337, 0], [70, 346, 3.4], [64, 358, 3.2], [61, 370, 0]], INK.hi, 0.5)
    + glint([[86, 337, 0], [104, 338, 3], [126, 337, 0]], INK.lite, 0.8)
    + shape('M93 356 C99 361 108 363 117 360 C126 356 134 348 140 341 L142 366 L90 366 Z', INK.deep, 0.6)) },
  { id: 'shoeL', cls: 'a-legL', d: S.shoeL, shadow: [{ on: ['legL'], dx: -2, dy: 4, color: SH.ink, o: 0.55 }],
    body: use('shoeL', 'url(#g-cream)') + clip('shoeL',
      // le talon et la semelle, vus de dos ; le reflet du dessus
      shape('M58 381 C61 388 66 392 73 393 C80 394 86 390 89 384 L92 398 L56 398 Z', CREAM.deep, 0.85)
      + oval(77, 370, 7, 3.4, CREAM.hi, 0.75, -8) + line('M64 383 C70 386 78 386 85 382', CREAM.shade, 1.4, 0.8)) },
  // --- la jambe de devant, qui avance ---
  { id: 'legR', cls: 'a-legR', d: S.legR, body: use('legR', 'url(#g-ink)') + clip('legR',
    glint([[198, 338, 0], [202, 352, 3.2], [205, 366, 0]], INK.hi, 0.55)
    + glint([[160, 340, 0], [180, 341, 3], [198, 340, 0]], INK.lite, 0.7)
    + shape('M151 346 C160 348 168 352 175 357 C179 361 181 366 182 372 L150 372 Z', INK.deep, 0.6)) },
  { id: 'shoeR', cls: 'a-legR', d: S.shoeR, shadow: [{ on: ['legR'], dx: -2, dy: 4, color: SH.ink, o: 0.55 }],
    body: use('shoeR', 'url(#g-cream)') + clip('shoeR',
      // la semelle sombre, le bout relevé éclairé, le pli de la cheville
      shape('M180 390 C186 397 198 398 212 395 C226 391 238 384 246 376 L250 392 L176 408 Z', CREAM.deep, 0.9)
      + oval(234, 368, 9, 4.4, CREAM.hi, 0.85, -18) + oval(195, 369, 8, 3.4, CREAM.hi, 0.55, -4)
      + line('M209 369 C213 375 214 383 210 391', CREAM.shade, 1.6, 0.85)) },

  // --- le bras droit, derrière le corps, et sa moufle ---
  { id: 'armR', cls: 'a-armR', d: S.armR, body: use('armR', 'url(#g-ink)')
    + glint([[252, 293, 0], [266, 302, 3], [276, 312, 0]], INK.hi, 0.5) },
  { id: 'fistR', cls: 'a-armR', d: S.fistR, shadow: [{ on: ['armR'], dx: -3, dy: 4, color: SH.ink, o: 0.5 }],
    body: use('fistR', 'url(#g-cream)') + clip('fistR',
      shape('M262 322 C266 332 276 338 290 340 C298 338 304 332 305 324 L308 344 L258 344 Z', CREAM.shade, 0.8)
      + oval(288, 309, 9, 4, CREAM.hi, 0.75, 8))
    + line('M281 307 C285 312 285 318 282 322', CREAM.deep, 1.6, 0.85)
    + line('M291 313 C296 312 300 315 300 319', CREAM.deep, 1.5, 0.85) },

  // --- le petit pétard, puis le bras gauche qui le tient ---
  { id: 'stick', cls: 'a-armL', d: S.stick, body: use('stick', 'url(#g-stick)') + clip('stick',
    // le reflet le long du dessus, l'ombre du dessous
    glint([[18, 256, 0], [34, 241, 3], [52, 225, 0]], '#ffb39a', 0.9)
    + glint([[30, 279, 0], [48, 262, 3.4], [66, 244, 0]], '#5a0a10', 0.5)
    // le bout : une rondelle de carton, son trou
    + `<ellipse cx="20" cy="270" rx="14.2" ry="7" transform="rotate(50.7 20 270)" fill="#d6c29c"/>`
    + `<ellipse cx="19.4" cy="270.6" rx="8.6" ry="3.9" transform="rotate(50.7 19.4 270.6)" fill="#8a7458"/>`
    + `<ellipse cx="22" cy="266" rx="6" ry="2" transform="rotate(50.7 22 266)" fill="#fff4dc" opacity="0.8"/>`) },
  { id: 'armL', cls: 'a-armL', d: S.armL, shadow: [{ on: ['stick'], dx: -3, dy: 4, color: SH.red, o: 0.5 }],
    body: use('armL', 'url(#g-ink)') + clip('armL',
      glint([[70, 232, 0], [84, 233, 3], [98, 242, 3], [114, 251, 0]], INK.hi, 0.55)
      + shape('M60 246 C66 252 76 256 84 260 C92 266 104 272 118 276 L118 282 L58 282 Z', INK.deep, 0.5)) },
  { id: 'handL', cls: 'a-armL', d: S.handL, shadow: [{ on: ['stick', 'armL'], dx: -2, dy: 4, color: SH.ink, o: 0.5 }],
    body: use('handL', 'url(#g-cream)') + clip('handL',
      // une lumière chaude sur le dessus, l'ombre du dessous (les doigts repliés sous le tube)
      oval(66, 228, 14, 11, '#ffd25a', 0.5)
      + shape('M49 236 C50 246 56 253 65 254 C74 254 79 248 80 240 C74 246 66 248 59 246 C54 244 51 240 49 236 Z', CREAM.shade, 0.85)
      // le pouce, qui passe par-dessus le tube ; son pli
      + shape('M62 223 C67 219 74 220 77 226 C79 231 77 236 72 237 C67 237 63 233 62 228 Z', '#e8d6b0')
      + oval(71, 224, 4.6, 2.4, CREAM.hi, 0.95, 25)
      + oval(55, 228, 3.6, 2.4, CREAM.hi, 0.6, -30))
      + line('M61 225 C61 231 65 236 71 238', CREAM.deep, 1.6, 0.9) },

  // --- le corps ---
  { id: 'body', cls: 'a-body', d: S.body,
    shadow: [{ on: ['legL', 'legR'], dx: -3, dy: 6, color: SH.ink, o: 0.6 }, { on: ['armL', 'armR'], dx: -3, dy: 5, color: SH.ink, o: 0.5 }],
    body: bodyBody },

  // --- la mèche, derrière la grande pointe ---
  { id: 'fuse', cls: 'a-fuse', d: S.fuse, shadow: [{ on: ['body'], dx: -2, dy: 4, color: SH.red, o: 0.4 }],
    body: use('fuse', 'url(#g-fuse)') + clip('fuse',
      // la tresse : un reflet sur le dessus, deux torsades marquées, le bout rougi par le feu
      glint([[220, 128, 0], [218, 115, 2.6], [212, 103, 3.2], [218, 92, 3.2], [232, 85, 3], [248, 80, 2.8], [260, 76, 0]], '#a0603a', 0.85)
      + glint([[222, 104, 0], [228, 97, 3], [231, 91, 0]], '#1a0a06', 0.5) + glint([[240, 94, 0], [244, 87, 3], [246, 81, 0]], '#1a0a06', 0.5)
      + glint([[217, 120, 0], [222, 114, 2.6], [225, 108, 0]], '#1a0a06', 0.45)
      + glint([[250, 82, 0], [263, 78, 3.6], [277, 72, 0]], '#ff9a3a', 0.9)
      + `<circle cx="275" cy="72" r="8" fill="url(#g-ember)"/>`) },

  // --- la couronne : quatre pointes bombées (A au fond, pâle ; B ; C la plus grande ; D) ---
  { id: 'crown', cls: 'a-crown', d: S.crown, shadow: [{ on: ['body'], dx: -2, dy: 4, color: SH.gold, o: 0.45 }, { on: ['fuse'], dx: -3, dy: 4, color: '#1a0a06', o: 0.45 }],
    body: use('crown', 'url(#g-spike)') + clip('crown',
      // A, au fond : pâle et sans relief marqué
      shape('M138 145 Q141 130 150 120 Q155 128 160 134 L160 146 Z', '#f2d9a6') + shape('M138 145 Q141 130 150 120 Q148 134 149 146 Z', '#d4a872')
      // B, C, D : la face gauche dans l'ombre, un éclat sur le galbe de droite
      + shape('M156 147 Q164 115 177 105 Q186 113 192 123 L196 148 Z', '#ffd24c') + shape('M156 147 Q164 115 177 105 Q172 124 174 148 Z', '#e08e1c')
      + shape('M190 149 Q198 110 212 103 Q223 113 230 127 L232 150 Z', '#ffdc62') + shape('M190 149 Q198 110 212 103 Q206 126 208 150 Z', '#e7941e')
      + shape('M228 150 Q235 116 244 109 Q253 124 256 143 L256 150 Z', '#ffcf48') + shape('M228 150 Q235 116 244 109 Q240 128 242 150 Z', '#d6821a')
      + glint([[179, 109, 0], [184, 122, 2.6], [188, 138, 0]], GOLD.hi, 0.9)
      + glint([[214, 107, 0], [220, 120, 3], [224, 140, 0]], GOLD.hi, 0.95)
      + glint([[246, 113, 0], [250, 126, 2.4], [253, 140, 0]], GOLD.hi, 0.85)
      // le pied des pointes, plus sombre là où elles se plantent dans le dessus du tube
      + shape('M136 137 C150 143 200 146 258 140 L258 152 L136 152 Z', GOLD.shade, 0.55)) },

  // --- l'étincelle au bout de la mèche, et ses éclats (aucune silhouette : pas de contour) ---
  { id: 'spark', cls: 'a-fuse', d: 'M-900 -900', body: sparkBody() },
];

/** La gerbe : halo, éclaboussure lobée orange puis jaune, cœur blanc ; des éclats qui filent surtout vers la droite. */
function sparkBody() {
  const C = [279, 69];
  // une éclaboussure : des pointes de longueurs inégales, reliées par des creux arrondis
  const splash = (radii, inner, rot) => {
    const k = radii.length;
    let d = '';
    radii.forEach((r, i) => {
      const a = rot + (i * Math.PI * 2) / k, b = a + Math.PI / k;
      const tip = [C[0] + Math.cos(a) * r, C[1] + Math.sin(a) * r];
      const val = [C[0] + Math.cos(b) * inner, C[1] + Math.sin(b) * inner];
      const ctl = [C[0] + Math.cos(b - 0.12) * inner * 1.25, C[1] + Math.sin(b - 0.12) * inner * 1.25];
      d += `${i ? 'L' : 'M'}${n(tip[0])} ${n(tip[1])}Q${n(ctl[0])} ${n(ctl[1])} ${n(val[0])} ${n(val[1])}`;
    });
    return d + 'Z';
  };
  // les éclats : [x, y de la tête ; longueur ; largeur], dirigés depuis le centre
  const flecks = [[340, 9, 16, 3.4], [302, 30, 7, 2.4], [250, 27, 7, 2.2], [233, 55, 6, 2], [331, 51, 8, 2.4], [345, 66, 7, 2.2], [339, 83, 9, 2.6], [346, 99, 7, 2.2], [319, 95, 7, 2.2], [306, 104, 6, 2], [329, 104, 6, 2]];
  return `<g class="a-halo"><circle cx="${C[0]}" cy="${C[1]}" r="58" fill="url(#g-halo)"/></g><g class="a-spark">`
    + shape(splash([37, 30, 41, 28, 35, 31, 39, 27, 34, 32, 38, 29], 24, -0.3), '#ff8a1e', 0.95)
    + shape(splash([29, 23, 32, 21, 27, 24, 30, 22, 26, 25, 28], 17, -0.2), 'url(#g-burst)')
    + shape(splash([15, 11, 17, 10, 14, 12, 16], 7.5, 0.3), '#fff8dc')
    + dot(C[0], C[1], 6, '#ffffff')
    + '</g>'
    + flecks.map(([x, y, len, w], i) => {
      const dx = x - C[0], dy = y - C[1], l = Math.hypot(dx, dy), ux = dx / l, uy = dy / l;
      const tail = [x - ux * len, y - uy * len];
      return `<g class="a-fleck${(i % 4) + 1}">${glint([[tail[0], tail[1], 0], [x - ux * len * 0.35, y - uy * len * 0.35, w], [x, y, w * 0.8]], '#ff9a2a')}${dot(x, y, w * 0.55, '#fff2b0')}</g>`;
    }).join('');
}

// ---------- la vie au repos et l'attaque ----------
// Repos : il trottine sur place. Le corps rebondit et s'écrase un peu (pivot B, le bas du tube), la couronne, la mèche
// et les bras suivent le rebond exactement (même cadence, même déplacement à leur hauteur) ; les jambes et les bras
// se balancent ; la mèche se tord sur deux rebonds ; l'étincelle crépite, des éclats jaillissent, les dents grincent.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : il se tasse sur ses pieds (élan), bondit en avant vers la droite en s'étirant,
// claque des dents, l'étincelle explose ; il retombe écrasé puis revient exactement à sa place.
const B = [180, 342];
const PIV = { body: B, legL: [128, 338], legR: [176, 338], armL: [120, 264], armR: [244, 300], fuse: [226, 140], crown: [198, 146] };
const at = (k) => `transform-origin:${PIV[k][0]}px ${PIV[k][1]}px`;
/** Le déplacement dû au rebond du corps (translateY puis écrasement autour de B) au point (x, y). */
const BOB = { dy: -2.5, sx: 0.99, sy: 1.012 };
const bobAt = ([x, y]) => [n((x - B[0]) * (BOB.sx - 1)), n(BOB.dy + (y - B[1]) * (BOB.sy - 1))];
// le bond s'écrase et s'étire autour du point au sol entre les pieds (G) : les pieds restent posés pendant l'élan
const G = [160, 401];
/**
 * Une image clé du bond : le mouvement commun (déplacement d, bascule r et écrasement sx, sy autour de G), puis le
 * mouvement propre du morceau autour de son pivot O. Toutes les images clés ont la même liste de fonctions, et le
 * mouvement commun est le même pour tous les morceaux à chaque instant : rien ne se détache.
 */
const key = (O, p, [dx, dy, r, sx, sy], [odx = 0, ody = 0, orot = 0, osc = 1] = []) =>
  `${p}%{transform:translate(${dx}px,${dy}px) translate(${G[0] - O[0]}px,${G[1] - O[1]}px) rotate(${r}deg) scale(${sx},${sy}) translate(${O[0] - G[0]}px,${O[1] - G[1]}px) translate(${odx}px,${ody}px) rotate(${orot}deg) scale(${osc})}`;
// le bond : 0 → tassé (élan) → en l'air, étiré, penché en avant → retombe écrasé → revient
const HOP = { 0: [0, 0, 0, 1, 1], 28: [0, 0, -3, 1.06, 0.88], 45: [24, -28, 5, 0.94, 1.08], 62: [20, 0, 2, 1.07, 0.9], 80: [4, 0, -1, 0.98, 1.03], 100: [0, 0, 0, 1, 1] };
const atk = (name, O, own = {}) => `@keyframes ${name}{${Object.keys(HOP).map((p) => key(O, p, HOP[p], own[p])).join('')}}`;
const [fx, fy] = bobAt(PIV.fuse), [cx, cy] = bobAt(PIV.crown), [lx, ly] = bobAt(PIV.armL), [rx, ry] = bobAt(PIV.armR);
const style = [
  `.a-body{${at('body')};animation:bob .8s ease-in-out infinite alternate}`,
  `.a-crown{${at('crown')};animation:crown .8s ease-in-out infinite alternate}`,
  `.a-fuse{${at('fuse')};animation:fuse 3.2s ease-in-out infinite}`,
  `.a-armL{${at('armL')};animation:armL .8s ease-in-out infinite alternate}`,
  `.a-armR{${at('armR')};animation:armR .8s ease-in-out infinite alternate}`,
  `.a-legL{${at('legL')};animation:legL .8s ease-in-out infinite alternate}`,
  `.a-legR{${at('legR')};animation:legR .8s ease-in-out infinite alternate}`,
  '.a-spark{transform-origin:279px 69px;animation:spark .26s ease-in-out infinite alternate}',
  '.a-halo{transform-origin:279px 69px;animation:halo .9s ease-in-out infinite alternate}',
  '.a-teethT{animation:teethT 1.3s ease-in-out infinite alternate}.a-teethB{animation:teethB 1.3s ease-in-out infinite alternate}',
  '.a-blink{animation:blink 4.2s linear infinite}',
  '.a-fleck1,.a-fleck2,.a-fleck3,.a-fleck4{transform-origin:279px 69px;opacity:0}',
  '.a-fleck1{animation:fleck 1.1s ease-out infinite}.a-fleck2{animation:fleck 1.4s ease-out -0.5s infinite}',
  '.a-fleck3{animation:fleck 1.7s ease-out -1.1s infinite}.a-fleck4{animation:fleck 1.25s ease-out -0.8s infinite}',
  `@keyframes bob{from{transform:none}to{transform:translateY(${BOB.dy}px) scale(${BOB.sx},${BOB.sy})}}`,
  `@keyframes crown{from{transform:none}to{transform:translate(${cx}px,${cy}px) rotate(1deg)}}`,
  // la mèche : quatre demi-rebonds (le rebond du corps à sa base) et une torsion qui change à chacun
  `@keyframes fuse{0%{transform:translate(0,0) rotate(0deg)}25%{transform:translate(${fx}px,${fy}px) rotate(-3deg)}50%{transform:translate(0,0) rotate(1.5deg)}75%{transform:translate(${fx}px,${fy}px) rotate(-1deg)}100%{transform:translate(0,0) rotate(0deg)}}`,
  `@keyframes armL{from{transform:none}to{transform:translate(${lx}px,${ly}px) rotate(-5deg)}}`,
  `@keyframes armR{from{transform:none}to{transform:translate(${rx}px,${ry}px) rotate(5deg)}}`,
  '@keyframes legL{from{transform:none}to{transform:rotate(3deg)}}',
  '@keyframes legR{from{transform:none}to{transform:rotate(-3deg)}}',
  '@keyframes spark{from{transform:scale(0.9) rotate(-4deg)}to{transform:scale(1.08) rotate(4deg)}}',
  '@keyframes halo{from{transform:scale(0.92);opacity:0.85}to{transform:scale(1.06);opacity:1}}',
  '@keyframes teethT{from{transform:none}to{transform:translateY(1.4px)}}',
  '@keyframes teethB{from{transform:none}to{transform:translateY(-1.2px)}}',
  '@keyframes blink{0%,90%{opacity:0}92%,95%{opacity:1}97%,100%{opacity:0}}',
  '@keyframes fleck{0%{opacity:0;transform:scale(0.55)}20%{opacity:1}100%{opacity:0;transform:scale(1.35)}}',
  // l'attaque
  ...['body', 'crown', 'fuse', 'armL', 'armR', 'legL', 'legR'].map((k) => `.atk .a-${k}{animation:${k}-atk .75s ease-in-out}`),
  '.atk .a-spark{animation:spark-atk .75s ease-in-out}.atk .a-halo{animation:halo-atk .75s ease-in-out}',
  '.atk .a-teethT{animation:teethT-atk .75s ease-in-out}.atk .a-teethB{animation:teethB-atk .75s ease-in-out}',
  '.atk .a-fleck1,.atk .a-fleck2,.atk .a-fleck3,.atk .a-fleck4{animation:fleck-atk .75s ease-out}',
  atk('body-atk', PIV.body),
  atk('crown-atk', PIV.crown, { 28: [0, 1, -3], 45: [0, -2, 4], 62: [0, 1, -2] }),
  atk('fuse-atk', PIV.fuse, { 28: [0, 0, 6], 45: [0, 0, -9], 62: [0, 0, 5], 80: [0, 0, -2] }),
  atk('armL-atk', PIV.armL, { 28: [0, 0, 10], 45: [0, 0, -24], 62: [0, 0, -8], 80: [0, 0, 2] }),
  atk('armR-atk', PIV.armR, { 28: [0, 0, -8], 45: [0, 0, 20], 62: [0, 0, 6] }),
  atk('legL-atk', PIV.legL, { 28: [0, 0, -4], 45: [0, 0, 16], 62: [0, 0, 2] }),
  atk('legR-atk', PIV.legR, { 28: [0, 0, 3], 45: [0, 0, -14], 62: [0, 0, -2] }),
  '@keyframes spark-atk{0%{transform:none}28%{transform:scale(0.75)}45%{transform:scale(1.75) rotate(12deg)}62%{transform:scale(1.3)}100%{transform:none}}',
  '@keyframes halo-atk{0%{transform:none}28%{transform:scale(0.85)}45%{transform:scale(1.35)}62%{transform:scale(1.15)}100%{transform:none}}',
  '@keyframes teethT-atk{0%{transform:none}28%{transform:translateY(-3px)}40%{transform:translateY(-3px)}48%{transform:translateY(9px)}62%{transform:translateY(7px)}100%{transform:none}}',
  '@keyframes teethB-atk{0%{transform:none}28%{transform:translateY(3px)}40%{transform:translateY(3px)}48%{transform:translateY(-8px)}62%{transform:translateY(-6px)}100%{transform:none}}',
  '@keyframes fleck-atk{0%,30%{opacity:0;transform:scale(0.5)}45%{opacity:1;transform:scale(1.2)}75%{opacity:0;transform:scale(1.45)}100%{opacity:0;transform:scale(1.45)}}',
].join('');

module.exports = { id: 'parade-1', w: W, h: H, pad: 66, foot: [160, 401], svg: (anime = true) => figure({ w: W, h: H, pad: 66, defs, style, parts, anime }) };
