// Le lion de la parade (parade-2), monstre de la Parade des pétards : redessiné par le code d'après le dessin d'origine,
// dans le même cadre (460 × 410, mêmes proportions, même pose) : un lion de danse chinoise doré, tourné vers la droite ;
// corps couvert d'écailles d'or bordées de rouge, grosse tête ornée (cornes rouges à cœur blanc, plume blanche, bijou
// vert, gemme au front), un énorme œil rond (bord orange, iris vert) et un petit œil au fond, gros nez rouge, gueule
// ouverte aux crocs, barbe et crinière blanches en touffes, queue en plumet blanc, quatre pattes aux chevilles touffues.
// La lumière vient d'en haut à droite : les ombres portées tombent en bas à gauche. Contour décalqué sur l'original
// (outils/contour.py).
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 460, H = 410, PAD = 44;

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
const GOLD = { hi: '#fff4bc', lite: '#ffda6e', base: '#f6b93c', mid: '#e2962a', shade: '#b8661c', deep: '#7a3a10' };
const RED = { hi: '#ff8a62', base: '#e3402c', shade: '#b0241a', deep: '#741010' };
const FUR = { hi: '#ffffff', base: '#f6efe0', shade: '#d6c6b2', deep: '#a8927e' };
const SH = { gold: '#6a2c08', fur: '#6a5444', dark: '#24080a' };

// ---------- dégradés ----------
const defs = [
  lin('g-gold', 360, 80, 160, 360, [[0, GOLD.lite], [0.45, GOLD.base], [1, GOLD.mid]]),
  lin('g-goldFar', 0, 0, 0, 1, [[0, GOLD.mid], [1, GOLD.shade]], false),
  lin('g-head', 420, 80, 280, 260, [[0, '#ffe282'], [0.5, '#fcc44a'], [1, '#e8a032']]),
  lin('g-scale', 0, 0, 0, 1, [[0, '#ffe68a'], [0.55, GOLD.base], [1, '#e88a2a']], false),
  lin('g-fur', 0, 0, 0, 1, [[0, FUR.hi], [0.6, FUR.base], [1, FUR.shade]], false),
  lin('g-red', 0, 0, 0, 1, [[0, '#ff6a4a'], [0.5, RED.base], [1, RED.shade]], false),
  rad('g-orn', 0.6, 0.35, 0.8, [[0, '#eaffb0'], [0.4, '#a8d850'], [0.8, '#5a9a2a'], [1, '#2a5a16']], false),
  rad('g-gem', 0.6, 0.35, 0.8, [[0, '#eafffc'], [0.4, '#7ae0d0'], [0.8, '#2a9a94'], [1, '#14585a']], false),
  rad('g-eyeO', 0.55, 0.4, 0.75, [[0, '#ffd28a'], [0.6, '#f08a2a'], [1, '#b04a14']], false),
  rad('g-iris', 0.6, 0.35, 0.75, [[0, '#d8fff0'], [0.4, '#6ad8b0'], [0.8, '#2a9a74'], [1, '#145a44']], false),
  lin('g-lid', 0, 0, 0, 1, [[0, '#3a1408', 0.7], [0.5, '#3a1408', 0]], false),
  rad('g-nose', 0.6, 0.3, 0.8, [[0, '#ff9a7a'], [0.45, '#e8402e'], [1, '#8a1410']], false),
  lin('g-mouth', 0, 196, 0, 252, [[0, '#2a060c'], [0.55, '#5a1420'], [1, '#8a2834']]),
  lin('g-claw', 0, 0, 0, 1, [[0, '#f4f2ee'], [0.5, '#b8b4b0'], [1, '#6a6670']], false),
].join('');

// ---------- silhouettes (le bord extérieur suit le contour mesuré sur l'original) ----------
const S = {
  // la queue : écailles d'or, puis le plumet blanc en flammes
  tail: sm('9,156! 16,156 19,153 19,137 30,107 31,98! 34,109 38,113 44,113 55,93! 63,114 63,125 66,128 72,128 80,118! 82,130 86,133 85,146 88,149 93,149 94,162 91,171 80,181 80,187 '
    + '99,215 107,222 114,222 129,211 134,203 140,230 120,260 100,290 83,268 83,262 77,258 69,258 64,251 59,250 45,225 45,220 41,210 39,191 36,188 29,188 22,184 13,173 13,164'),
  // les pattes arrière (au fond)
  leg1: sm('62,296 100,298 104,330 98,356 99,397! 50,398 49,391 53,383 53,376 41,367! 49,359 56,359 60,355 61,341 65,330'),
  leg2: sm('108,298 160,298 176,330 171,351 162,355 153,355 149,359 149,372 153,376 159,376 164,379 174,392! 156,392 152,394 125,392 122,397! 100,397 104,370 106,340'),
  // la patte avant droite (au fond, sous la barbe)
  leg4: sm('322,286 360,290 366,314 363,317 363,323 361,325 361,332 367,340 366,348 374,361 383,361 393,358 398,359 406,365 412,377 414,397! 404,396 400,398 340,396! 339,379 336,376 327,376 329,371 328,359 318,351 314,326'),
  // le corps couvert d'écailles
  body: sm('96,212 120,200 160,188 200,178 240,188 280,212 310,236 340,268 352,300 342,330 318,350 300,344 265,346 211,346 200,346 191,352 177,344 162,355 150,358 130,350 100,330 84,300 80,260'),
  // la patte avant gauche (devant)
  leg3: sm('212,296 262,298 266,346 257,355 258,368 261,371 270,371 275,373 278,376 289,399! 271,399 269,401 259,402 210,401! 206,396 212,388 212,382 209,379 203,379! 214,363 214,349 210,326'),
  // la crinière blanche, en grandes touffes derrière la tête
  mane: sm('258,96 250,96 242,87 234,82 224,70 220,69 211,62! 214,84 220,100 231,118 231,124 226,128 213,131 187,144! 207,155 207,161 204,164 190,166 184,169! 198,186 214,206! 212,214 232,236! 240,252 262,266! 280,272 300,268 300,240 270,200 262,150 264,112'),
  // la coiffe : la grande corne rouge de gauche, la plume blanche du milieu, le bijou vert, les deux cornes de droite
  earL: sm('246,98 246,56 250,30 259,13 263,12! 269,16 288,37 294,50 290,82 272,102'),
  hornM: sm('298,72 308,40 314,36 319,8! 322,9 334,21 346,44 352,62 346,78 320,82'),
  orn: sm('286,46 300,31 316,34 328,46 330,64 318,78 298,78 286,64'),
  earR: sm('346,74 355,54 362,44 372,30 385,20! 393,36 397,52 392,72 374,80'),
  earFR: sm('394,64 400,55 406,55 410,52! 417,53 421,62 421,74 418,89 406,90 396,80'),
  // la gueule (l'intérieur, derrière la mâchoire et la tête), la mâchoire du bas, la barbe blanche
  mouth: sm('358,194 442,200 434,214 420,232 410,248 382,252 362,242 354,214'),
  jaw: sm('360,236 380,242 404,238 409,225 420,214 428,214 431,217 431,222! 428,236 418,247 404,256 380,258 362,252'),
  beard: sm('352,246 380,256 404,254 418,247 417,262 422,266 422,270 419,279 415,282 416,296 413,307 409,311 406,322 401,322 398,325 397,341! 385,326 372,314 366,314 363,317 363,323 361,325 361,332 367,340! 352,322 344,292 344,264'),
  // la tête : le crâne (sous la coiffe), le front bosselé, la truffe, la lèvre du haut, la joue
  head: sm('250,102 270,86 300,76 340,72 380,74 410,86 425,94 433,93 437,108 441,111 441,118 438,126 429,133 429,144 438,156 448,164 452,180 450,194 442,202 436,205 '
    + '410,206 386,200 366,198 356,214 360,240 362,262 340,274 310,272 288,258 270,236 260,210 254,180 252,150 250,124'),
};

// ---------- le visage ----------
/** Une dent pointue : la moitié du fond dans l'ombre, un filet de lumière sur l'autre flanc. b1, b2 = la racine, t = la pointe. */
function tooth([x1, y1], [x2, y2], [tx, ty]) {
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  const d = `M${x1} ${y1}Q${n((x1 + tx) / 2 - (ty - y1) * 0.08)} ${n((y1 + ty) / 2)} ${tx} ${ty}Q${n((x2 + tx) / 2 + (ty - y2) * 0.08)} ${n((y2 + ty) / 2)} ${x2} ${y2}Z`;
  const half = `M${x1} ${y1}L${tx} ${ty}L${n(mx)} ${n(my)}Z`;
  return shape(d, '#fbf4e8') + shape(half, '#d8c8bc', 0.8) + line(`M${n(mx + (x2 - mx) * 0.5)} ${n(my + (y2 - my) * 0.5)}L${n(tx + (x2 - tx) * 0.2)} ${n(ty + (y2 - ty) * 0.2)}`, '#ffffff', 1.2, 0.9);
}
const TEETH_T = [[[368, 198], [378, 199], [374, 214]], [[384, 200], [396, 201], [392, 230]], [[404, 202], [412, 203], [409, 214]], [[418, 203], [430, 203], [426, 226]]];
const TEETH_B = [[[372, 246], [380, 248], [377, 236]], [[388, 249], [398, 249], [394, 232]], [[402, 246], [410, 242], [407, 230]]];

/** Un œil de lion : anneau rouge, blanc orangé, iris vert, grosse pupille, reflets ; le sourcil rouge ourlé d'or.
 *  Les deux yeux sont bâtis pareil ; celui du fond (k < 1) est un peu plus petit. */
function lionEye(x, y, k, key) {
  const brow = sm(`${n(x - 39 * k)},${n(y - 22 * k)} ${n(x - 23 * k)},${n(y - 40 * k)} ${n(x + 5 * k)},${n(y - 46 * k)} ${n(x + 31 * k)},${n(y - 36 * k)} ${n(x + 51 * k)},${n(y - 12 * k)} ${n(x + 41 * k)},${n(y - 4 * k)} ${n(x + 21 * k)},${n(y - 16 * k)} ${n(x - 1 * k)},${n(y - 22 * k)} ${n(x - 21 * k)},${n(y - 16 * k)}`);
  return oval(x, y, 34 * k, 31 * k, RED.deep) + oval(x, y, 32 * k, 29.5 * k, RED.base)
    + `<clipPath id="c-${key}"><ellipse cx="${x}" cy="${y}" rx="${n(28 * k)}" ry="${n(26 * k)}"/></clipPath>` + oval(x, y, 28 * k, 26 * k, 'url(#g-eyeO)')
    + `<g clip-path="url(#c-${key})">` + dot(n(x + 5 * k), n(y - k), n(19 * k), '#1a2a20') + dot(n(x + 5 * k), n(y - k), n(17 * k), 'url(#g-iris)') + dot(n(x + 7 * k), n(y - k), n(8.4 * k), '#0c0808')
    + `<rect x="${n(x - 32 * k)}" y="${n(y - 30 * k)}" width="${n(64 * k)}" height="${n(28 * k)}" fill="url(#g-lid)"/>`
    + dot(n(x + k), n(y - 8 * k), n(4.2 * k), '#fff') + dot(n(x + 13 * k), n(y + 7 * k), n(2 * k), '#fff', 0.9) + '</g>'
    + `<g class="a-blink" opacity="0">${oval(x, y, 29 * k, 27 * k, 'url(#g-gold)')}${line(`M${n(x - 28 * k)} ${n(y + 2 * k)} Q${x} ${n(y + 14 * k)} ${n(x + 28 * k)} ${n(y + 2 * k)}`, '#2a1008', 3)}</g>`
    + `<path d="${brow}" transform="translate(-2 4)" fill="#3a1008" opacity="0.4"/>` + shape(brow, 'url(#g-red)')
    + glint([[x - 29 * k, y - 30 * k, 0], [x + k, y - 40 * k, 3 * k], [x + 29 * k, y - 32 * k, 2.4 * k], [x + 45 * k, y - 14 * k, 0]], GOLD.hi, 0.85);
}
// les deux yeux sur une même ligne, au-dessus du nez ; celui du fond un peu plus petit (trois quarts)
const bigEye = () => lionEye(316, 152, 0.92, 'eyeA');
const smallEye = () => lionEye(396, 136, 0.74, 'eyeB');

const headBody = use('head', 'url(#g-head)') + clip('head',
  // le dessous de la tête à l'ombre ; la joue en fourrure claire ; le front éclairé
  shape(sm('250,190 280,236 310,262 344,268 366,250 370,290 250,290'), GOLD.mid, 0.6)
  + shape(sm('262,196 282,226 306,246 330,252 352,236 348,214 330,224 306,222 286,206'), GOLD.hi, 0.4)
  + glint([[300, 86, 0], [350, 80, 5], [404, 92, 4], [432, 112, 0]], GOLD.hi, 0.7)
  // les ornements rouges du front, la gemme bleu-vert au milieu dans sa monture d'or
  + shape(sm('336,84 360,80 384,88 380,110 360,116 340,108'), 'url(#g-red)') + oval(360, 98, 12, 10, '#7a3a10') + oval(360, 98, 10, 8.4, 'url(#g-gem)') + oval(363, 94, 3, 2, '#ffffff', 0.9)
  // les touffes blanches sous la coiffe et sur la joue, les ornements rouges qui ourlent la joue
  + shape(sm('256,104 272,92! 278,104 292,86! 300,100 318,84! 326,98 346,86! 348,104 300,112 262,118'), 'url(#g-fur)')
  + shape(sm('270,210 286,226! 290,214 304,236! 308,222 324,244! 330,230 346,250! 352,236 352,262 300,262 268,240'), 'url(#g-fur)', 0.95)
  + glint([[276, 192, 3], [300, 206, 4], [330, 214, 4], [356, 208, 3]], RED.base, 0.85) + glint([[280, 190, 0], [306, 203, 1.6], [352, 205, 0]], GOLD.hi, 0.8)
  // la lèvre du haut, rouge, au bord de la gueule
  + glint([[366, 196, 4], [400, 200, 5], [438, 202, 4]], RED.base, 0.9)
  + bigEye() + smallEye()
  // le gros nez rouge et ses narines, devant les yeux
  + `<path d="M392 164 C398 152 418 150 434 154 C446 158 454 168 452 180 C450 190 440 194 428 192 C414 190 400 188 394 180 C390 175 389 170 392 164 Z" transform="translate(-2 4)" fill="#6a1010" opacity="0.4"/>`
  + `<path d="M392 164 C398 152 418 150 434 154 C446 158 454 168 452 180 C450 190 440 194 428 192 C414 190 400 188 394 180 C390 175 389 170 392 164 Z" fill="url(#g-nose)"/>`
  + oval(422, 160, 10, 4, '#ffd2c0', 0.8, -8) + oval(408, 179, 5, 3.4, '#4a0a0a', 0.9, 20) + oval(436, 181, 4.6, 3.2, '#4a0a0a', 0.9, -10)
);

// ---------- les écailles du corps ----------
/**
 * Des rangées de grosses écailles d'or bordées de rouge, décalées d'une rangée à l'autre ; plus petites et plus rouges
 * vers le bas ; celle du dessus recouvre celle du dessous. `k` = la taille de départ. Un léger décalage par écaille
 * (déterministe) évite l'effet de grille.
 */
function scales(x0, x1, y0, y1, k = 36) {
  const rows = [];
  let y = y0, r = 0;
  while (y < y1) { const sz = Math.max(k * 0.7, k - r * 2.4); rows.push([y, sz, r]); y += sz * 0.62; r++; }
  const nR = rows.length;
  return rows.reverse().map(([yy, sz, rr]) => {
    let out = '', i = 0;
    const warm = rr / nR > 0.5;   // vers le bas, les écailles virent au rouge-orangé (comme l'original), sans damier
    for (let x = x0 + (rr % 2 ? sz / 2 : 0); x < x1 + sz / 2; x += sz, i++) {
      const cx = x + (((i * 7 + rr * 3) % 5) - 2), cy = yy + (((i + rr) % 3) - 1);
      const d = `M${n(cx - sz / 2)} ${n(cy)}C${n(cx - sz / 2)} ${n(cy + sz * 0.7)} ${n(cx + sz / 2)} ${n(cy + sz * 0.7)} ${n(cx + sz / 2)} ${n(cy)}Z`;
      const lip = `M${n(cx - sz / 2 + 2)} ${n(cy + sz * 0.1)}C${n(cx - sz / 2 + 3)} ${n(cy + sz * 0.6)} ${n(cx + sz / 2 - 3)} ${n(cy + sz * 0.6)} ${n(cx + sz / 2 - 2)} ${n(cy + sz * 0.1)}`
        + `C${n(cx + sz / 2 - 4)} ${n(cy + sz * 0.44)} ${n(cx - sz / 2 + 4)} ${n(cy + sz * 0.44)} ${n(cx - sz / 2 + 2)} ${n(cy + sz * 0.1)}Z`;
      out += `<path d="${d}" fill="${warm ? RED.deep : GOLD.shade}" opacity="0.55" transform="translate(-2 4)"/>`
        + shape(d, warm ? '#f08a3a' : GOLD.lite) + shape(lip, warm ? RED.base : GOLD.mid, 0.9)
        + glint([[cx - sz * 0.05, cy + sz * 0.14, 0], [cx + sz * 0.16, cy + sz * 0.16, sz * 0.07], [cx + sz * 0.34, cy + sz * 0.1, 0]], warm ? '#ffd0a0' : GOLD.hi, 0.85);
    }
    return out;
  }).join('');
}

// ---------- les pattes ----------
/** Une patte : or en haut, une touffe blanche à la cheville, la patte claire aux doigts séparés et griffes grises. */
function legBody(id, fill, tuft, paw, toes, claws) {
  return use(id, fill) + clip(id, shape(tuft, 'url(#g-fur)') + shape(paw, FUR.base)
    + toes.map(([x, y]) => glint([[x, y, 0], [x + 1, y + 8, 2.4], [x + 1, y + 16, 0]], FUR.deep, 0.75)).join('')
    + claws.map(([x, y]) => `<path d="M${x - 3} ${y} Q${x} ${y + 8} ${x + 5} ${y + 9} Q${x + 3} ${y + 3} ${x + 3} ${y} Z" fill="url(#g-claw)"/>`).join(''));
}

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const parts = [
  { id: 'tail', cls: 'a-tail', d: S.tail, body: use('tail', 'url(#g-gold)') + clip('tail',
    // le plumet blanc en flammes (en haut), la queue en écailles (en bas)
    shape(sm('6,150 20,130 32,96 44,112 56,92 66,124 80,116 88,148 96,160 90,176 60,184 30,186 10,170'), 'url(#g-fur)')
    + glint([[30, 168, 0], [36, 140, 3], [34, 110, 0]], FUR.deep, 0.5) + glint([[60, 170, 0], [62, 140, 3], [58, 104, 0]], FUR.deep, 0.5)
    + scales(30, 140, 184, 300, 40)) },
  { id: 'leg1', cls: 'a-legB', d: S.leg1, body: legBody('leg1', 'url(#g-goldFar)', sm('40,352 64,340 100,346 102,372 60,378 40,368'), sm('46,376 100,372 100,400 46,400'),
    [[66, 382], [82, 382]], [[54, 392], [72, 393], [90, 393]]) },
  { id: 'leg2', cls: 'a-legB', d: S.leg2, body: legBody('leg2', 'url(#g-goldFar)', sm('146,350 160,346 176,350 172,374 150,376 140,366'), sm('100,372 176,374 176,400 100,400'),
    [[122, 378], [140, 378], [158, 380]], [[110, 392], [130, 393], [150, 391], [166, 389]]) },
  { id: 'leg4', cls: 'a-legF', d: S.leg4, body: legBody('leg4', 'url(#g-goldFar)', sm('356,334 372,340 404,352 410,372 372,372 340,370 330,354'), sm('336,372 414,374 416,400 336,400'),
    [[358, 378], [376, 378], [394, 378]], [[346, 391], [366, 393], [386, 393], [404, 391]]) },
  { id: 'body', cls: 'a-body', d: S.body, shadow: [sh(['tail', 'leg1', 'leg2', 'leg4'], -4, 5, SH.gold, 0.45)], body: use('body', 'url(#g-gold)') + clip('body',
    scales(80, 356, 176, 340, 54) + shape(sm('90,320 140,340 200,348 270,348 330,330 340,360 90,360'), GOLD.shade, 0.5)) },
  { id: 'leg3', cls: 'a-legF', d: S.leg3, shadow: [sh(['body', 'leg4'], -4, 5, SH.gold, 0.45)], body: use('leg3', 'url(#g-gold)') + clip('leg3',
    scales(208, 270, 296, 340, 36)
    + shape(sm('202,352 214,340 240,344 266,346 270,374 238,378 204,376'), 'url(#g-fur)')
    + shape(sm('204,378 280,376 292,402 204,402'), FUR.base)
    + [[226, 382], [246, 382], [264, 382]].map(([x, y]) => glint([[x, y, 0], [x + 1, y + 8, 2.4], [x + 1, y + 16, 0]], FUR.deep, 0.75)).join('')
    + [[214, 394], [234, 396], [254, 396], [274, 394]].map(([x, y]) => `<path d="M${x - 3} ${y} Q${x} ${y + 8} ${x + 5} ${y + 9} Q${x + 3} ${y + 3} ${x + 3} ${y} Z" fill="url(#g-claw)"/>`).join('')) },
  { id: 'mane', cls: 'a-mane', d: S.mane, shadow: [sh(['body', 'leg3'], -4, 5, SH.fur, 0.4)], body: use('mane', 'url(#g-fur)') + clip('mane',
    // de grandes touffes : un creux d'ombre entre elles, la pointe éclairée
    [[230, 110, 212, 66], [224, 140, 190, 146], [232, 180, 188, 168], [244, 214, 212, 210], [262, 244, 236, 246]].map(([x0, y0, x1, y1]) =>
      glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2 + 3, 4], [x1, y1, 0]], FUR.shade, 0.7)).join('')
    + glint([[236, 96, 0], [222, 78, 3], [214, 66, 0]], FUR.hi, 0.9)) },
  { id: 'earL', cls: 'a-earL', d: S.earL, body: use('earL', 'url(#g-red)') + clip('earL',
    shape(sm('254,90 254,56 260,30 262,22 270,34 280,52 282,78 270,94'), 'url(#g-fur)') + glint([[264, 26, 0], [278, 46, 2.6], [286, 70, 0]], RED.hi, 0.7)) },
  { id: 'hornM', cls: 'a-earL', d: S.hornM, body: use('hornM', 'url(#g-fur)') + clip('hornM',
    glint([[318, 14, 0], [330, 36, 3], [342, 62, 0]], FUR.hi, 0.9) + glint([[312, 40, 0], [316, 56, 3], [316, 76, 0]], FUR.shade, 0.7)) },
  { id: 'orn', cls: 'a-earL', d: S.orn, shadow: [sh(['hornM', 'earL'], -3, 4, SH.dark, 0.4)], body: use('orn', 'url(#g-orn)') + clip('orn',
    glint([[288, 52, 3], [306, 62, 3], [326, 58, 3]], '#e8c040', 0.8) + oval(316, 42, 4, 2.4, '#f6ffd8', 0.9)) },
  { id: 'earR', cls: 'a-earR', d: S.earR, body: use('earR', 'url(#g-red)') + clip('earR',
    shape(sm('356,70 360,54 370,38 380,30 386,46 384,64 372,74'), 'url(#g-fur)') + glint([[384, 26, 0], [392, 46, 2.4], [392, 64, 0]], RED.hi, 0.7)) },
  { id: 'earFR', cls: 'a-earR', d: S.earFR, body: use('earFR', 'url(#g-red)') + clip('earFR',
    shape(sm('402,80 404,66 410,58 414,66 414,82'), 'url(#g-fur)', 0.9)) },
  { id: 'mouth', cls: 'a-head', d: S.mouth, body: use('mouth', 'url(#g-mouth)') + clip('mouth',
    `<g class="a-teeth">${shape('M364 242 C372 228 392 224 408 230 C414 234 414 244 408 248 L364 250 Z', '#e0707a')
    + glint([[372, 234, 0], [388, 230, 3], [404, 234, 0]], '#f8a6ae', 0.8) + TEETH_B.map((t) => tooth(...t)).join('')}</g>`
    + TEETH_T.map((t) => tooth(...t)).join('')) },
  { id: 'jaw', cls: 'a-jaw', d: S.jaw, shadow: [sh(['leg4', 'body'], -3, 5, SH.gold, 0.4)], body: use('jaw', 'url(#g-head)') + clip('jaw',
    glint([[364, 240, 4], [396, 242, 5], [424, 226, 4]], RED.base, 0.9) + shape(sm('360,250 404,252 430,232 430,262 360,262'), GOLD.mid, 0.6)) },
  { id: 'head', cls: 'a-head', d: S.head, shadow: [sh(['mane', 'earL', 'hornM', 'orn', 'earR', 'earFR', 'jaw', 'leg4'], -3, 6, SH.gold, 0.45)], body: headBody },
  { id: 'beard', cls: 'a-beard', d: S.beard, shadow: [sh(['leg4', 'body', 'leg3'], -4, 5, SH.fur, 0.4)], body: use('beard', 'url(#g-fur)') + clip('beard',
    // de longues mèches blanches : un creux d'ombre entre deux mèches, la mèche du devant éclairée
    glint([[364, 262, 0], [370, 296, 4], [366, 336, 0]], FUR.shade, 0.75) + glint([[386, 262, 0], [390, 300, 4], [386, 326, 0]], FUR.shade, 0.7)
    + glint([[404, 262, 0], [408, 290, 3.4], [402, 334, 0]], FUR.hi, 0.9)) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : la danse du lion. La tête dodeline (avec la coiffe, la gueule et la barbe), les cornes frémissent, la mâchoire
// claque doucement, la barbe et la queue se balancent, le corps se soulève, il cligne de son gros œil.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : il se ramasse en arrière, se jette en avant la gueule grande ouverte et
// mord, la tête secouée, la barbe et le plumet fouettent ; puis il revient exactement à sa place.
const G = [230, 400];
const PIV = { root: G, body: [220, 340], head: [300, 240], jaw: [362, 236], tail: [110, 250], mane: [250, 200], earL: [290, 90], earR: [380, 84], beard: [380, 252], legB: [120, 310], legF: [240, 310] };
const IDLE = {
  'a-body': ['body', 'body 1.4s ease-in-out infinite alternate'],
  'a-head': ['head', 'head 1.8s ease-in-out infinite alternate'],
  'a-jaw': ['jaw', 'jaw .5s ease-in-out infinite alternate'],
  'a-teeth': ['jaw', 'jaw .5s ease-in-out infinite alternate'],
  'a-tail': ['tail', 'tail 2.2s ease-in-out infinite alternate'],
  'a-mane': ['mane', 'mane 1.8s ease-in-out infinite alternate'],
  'a-earL': ['earL', 'earL 1.3s ease-in-out infinite alternate'],
  'a-earR': ['earR', 'earR 1.5s ease-in-out infinite alternate'],
  'a-beard': ['beard', 'beard 1.6s ease-in-out infinite alternate'],
};
const atk = (cls, name) => (IDLE[cls]
  ? `.atk .${cls}{animation:${IDLE[cls][1]},${name} .75s ease-in-out;animation-composition:replace,add}`
  : `.atk .${cls}{animation:${name} .75s ease-in-out}`);
const style = Object.entries(IDLE).map(([c, [k, a]]) => `.${c}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px;animation:${a}}`).join('')
  + ['root', 'legB', 'legF'].map((k) => `.a-${k}{transform-origin:${PIV[k][0]}px ${PIV[k][1]}px}`).join('') + `
.a-blink{animation:blink 4.4s linear infinite}
@keyframes body{from{transform:none}to{transform:translate(0,-2.4px) scale(1.004,1.01)}}
@keyframes head{from{transform:rotate(-1.6deg)}to{transform:translate(1px,-2px) rotate(2deg)}}
@keyframes jaw{from{transform:none}to{transform:rotate(3deg)}}
@keyframes tail{from{transform:rotate(-2deg)}to{transform:rotate(3deg)}}
@keyframes mane{from{transform:none}to{transform:rotate(-1.4deg)}}
@keyframes earL{from{transform:none}to{transform:rotate(-4deg)}}
@keyframes earR{from{transform:none}to{transform:rotate(4deg)}}
@keyframes beard{from{transform:rotate(1.5deg)}to{transform:rotate(-3deg)}}
@keyframes blink{0%,92%{opacity:0}93.5%,96%{opacity:1}97.5%,100%{opacity:0}}
${atk('a-root', 'root-atk')}${atk('a-body', 'body-atk')}${atk('a-head', 'head-atk')}${atk('a-jaw', 'jaw-atk')}${atk('a-teeth', 'jaw-atk')}${atk('a-tail', 'tail-atk')}
${atk('a-beard', 'beard-atk')}${atk('a-legB', 'legB-atk')}${atk('a-legF', 'legF-atk')}
@keyframes root-atk{0%{transform:none}28%{transform:translate(-8px,2px) rotate(-2deg)}46%{transform:translate(26px,-6px) rotate(2deg)}60%{transform:translate(22px,0) rotate(.5deg)}80%{transform:translate(4px,0)}100%{transform:none}}
@keyframes body-atk{0%{transform:none}28%{transform:scale(0.98,0.96)}46%{transform:scale(1.03,0.99)}100%{transform:none}}
@keyframes head-atk{0%{transform:none}28%{transform:rotate(-8deg)}46%{transform:translate(4px,4px) rotate(7deg)}54%{transform:translate(4px,4px) rotate(2deg)}62%{transform:translate(3px,2px) rotate(5deg)}82%{transform:rotate(-1deg)}100%{transform:none}}
@keyframes jaw-atk{0%{transform:none}28%{transform:rotate(14deg)}40%{transform:rotate(16deg)}50%{transform:rotate(-3deg)}62%{transform:rotate(-2deg)}100%{transform:none}}
@keyframes tail-atk{0%{transform:none}28%{transform:rotate(-8deg)}46%{transform:rotate(10deg)}62%{transform:rotate(5deg)}100%{transform:none}}
@keyframes beard-atk{0%{transform:none}28%{transform:rotate(6deg)}46%{transform:rotate(-10deg)}62%{transform:rotate(-5deg)}100%{transform:none}}
@keyframes legB-atk{0%{transform:none}28%{transform:rotate(-5deg)}46%{transform:rotate(10deg)}62%{transform:rotate(4deg)}100%{transform:none}}
@keyframes legF-atk{0%{transform:none}28%{transform:rotate(5deg)}46%{transform:rotate(-12deg)}62%{transform:rotate(-4deg)}100%{transform:none}}
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
  let s = figure({ master: require('./silhouettes/parade-2.json'), w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  // la tête emporte la coiffe, la mâchoire et la barbe ; le corps emporte la tête, la crinière et la queue
  for (const c of ['a-jaw', 'a-earL', 'a-earR', 'a-beard']) s = nest(s, c, 'a-head');
  for (const c of ['a-head', 'a-tail', 'a-mane']) s = nest(s, c, 'a-body');
  // tout le lion bondit pendant l'attaque
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'parade-2', w: W, h: H, pad: PAD, foot: G, svg };
