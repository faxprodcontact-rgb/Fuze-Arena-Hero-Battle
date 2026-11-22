// La lanterne (parade-4), monstre de la Parade des pétards : redessinée par le code d'après le dessin d'origine, dans le
// même cadre (305 × 411, mêmes proportions, même pose) : une lanterne chinoise vivante qui flotte ; un toit en pagode
// rouge et or à côtes, surmonté d'une boule dorée ; un corps de papier rouge bombé, éclairé de l'intérieur (le milieu
// jaune-orangé), où brillent deux yeux fendus et une bouche en colère ; des clous dorés en haut et en bas ; deux
// glands rouges à boule dorée pendent aux coins du toit ; dessous, un socle doré et une boule de lumière.
// La lumière vient d'en haut à droite (et de l'intérieur) : les ombres portées tombent en bas à gauche. Contour
// décalqué sur l'original (outils/contour.py). Elle flotte : son ombre est posée au sol sous elle.
const { figure, lin, rad, n, use, clip, line, shape, dot, oval } = require('./lib.cjs');

const W = 305, H = 411, PAD = 40;

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
const RED = { hi: '#ff8a5a', lite: '#f25a32', base: '#d8301c', mid: '#b42016', shade: '#7a1010', deep: '#4a0808' };
const GOLD = { hi: '#fff4c0', lite: '#ffdc78', base: '#f2b440', mid: '#d08a22', shade: '#9a5a14', deep: '#5a3008' };
const LIGHT = { core: '#fffbe8', hi: '#fff0a8', lite: '#ffd060', base: '#ffa830', deep: '#e86a18' };
const SH = { red: '#3a0606', gold: '#4a2408' };

// ---------- dégradés ----------
const defs = [
  lin('g-roof', 0, 40, 0, 120, [[0, RED.lite], [0.6, RED.base], [1, RED.shade]]),
  lin('g-body', 64, 0, 254, 0, [[0, RED.shade], [0.14, RED.mid], [0.3, RED.lite], [0.5, LIGHT.base], [0.7, RED.lite], [0.86, RED.mid], [1, RED.shade]]),
  rad('g-inner', 158, 210, 100, [[0, LIGHT.hi, 0.9], [0.35, LIGHT.lite, 0.7], [0.7, LIGHT.base, 0.35], [1, LIGHT.base, 0]]),
  lin('g-gold', 0, 0, 0, 1, [[0, GOLD.hi], [0.4, GOLD.base], [1, GOLD.shade]], false),
  lin('g-goldX', 0, 0, 1, 0, [[0, GOLD.shade], [0.45, GOLD.base], [0.8, GOLD.hi], [1, GOLD.mid]], false),
  rad('g-ball', 0.62, 0.32, 0.8, [[0, GOLD.hi], [0.4, GOLD.lite], [0.8, GOLD.mid], [1, GOLD.shade]], false),
  lin('g-tassel', 0, 0, 0, 1, [[0, RED.base], [0.6, RED.mid], [1, RED.deep]], false),
  rad('g-glow', 0.5, 0.5, 0.5, [[0, '#fffbe0', 0.85], [0.42, '#ffd060', 0.45], [1, '#ffa830', 0]], false),
  rad('g-orb', 0.5, 0.42, 0.6, [[0, '#ffffff'], [0.4, '#fff4c0'], [0.8, '#ffd070'], [1, '#e8a040']], false),
].join('');

// ---------- silhouettes (le bord extérieur suit le contour mesuré sur l'original) ----------
const S = {
  // les glands : le cordon, la boule dorée, la houppe rouge
  cordL: rib([[46, 118, 6], [42, 140, 6], [41, 168, 5]]),
  cordR: rib([[278, 118, 6], [281, 140, 6], [282, 168, 5]]),
  ballL: sm('28,182 40,170 52,170 62,182 60,196 48,202 34,200'),
  ballR: sm('266,182 278,170 290,170 298,182 296,196 284,202 270,200'),
  tasselL: sm('28,198 58,198 50,230 49,248! 43,248 40,255 33,259 28,257 20,247! 14,247 9,250! 8,247 19,229 25,213'),
  tasselR: sm('266,198 294,198 283,209 286,236 296,248! 289,247 286,250 282,254 276,258 273,257 269,248! 264,248 264,230'),
  // le corps de la lanterne : un tonneau de papier bombé
  body: sm('72,118 120,116 160,114 200,116 248,118 256,140 254,187 252,223 244,261 244,268 253,276 250,283 240,296 226,307 212,310 106,308 86,309 74,300 62,288 62,271 72,262 72,254 63,211 64,173 62,168 69,141'),
  // le socle doré sous la lanterne, et la boule de lumière
  base: sm('100,300 220,300 212,318 203,335 187,335 184,344 140,344 137,335 117,335 108,318'),
  orb: sm('128,361 131,355 140,345 184,345 190,347 196,365 196,371 193,379 188,384 169,395 152,392 149,389 133,384 126,375'),
  // le toit en pagode : la boule du faîte, le toit et ses deux coins relevés
  knob: sm('150,28 151,19 157,11 163,8 172,10 176,14 179,22 178,29 173,37 173,43 157,44 157,38'),
  roof: sm('140,51 146,48 154,47 176,46 199,58 209,58 214,68 218,72 248,90 269,96 276,96 279,94 290,95! 285,104 283,118 270,124 240,124 200,122 160,122 120,122 80,124 53,118 44,121 41,129 34,113! 34,104 33,93 41,93 47,97 57,97 79,91 113,73 117,69 117,63 135,56'),
};

// ---------- le visage (la lumière qui passe par les trous du papier) ----------
const faceBody = `<g class="a-face">`
  // les yeux fendus, penchés vers le milieu (en colère), et la bouche ouverte, tordue
  + shape('M108 186 C122 180 140 184 152 196 C140 206 120 208 108 198 Z', LIGHT.core) + shape('M110 188 C124 184 138 188 148 196 C136 202 122 202 112 196 Z', '#ffffff')
  + shape('M214 186 C200 180 182 184 170 196 C182 206 202 208 214 198 Z', LIGHT.core) + shape('M212 188 C198 184 184 188 174 196 C186 202 200 202 210 196 Z', '#ffffff')
  + shape('M134 248 C146 240 172 238 190 246 C184 256 172 262 158 262 C146 262 138 256 134 248 Z', LIGHT.core) + shape('M140 248 C150 244 170 242 184 248 C178 254 168 258 158 258 C148 258 142 254 140 248 Z', '#ffffff')
  // les sourcils : deux plis sombres du papier, froncés
  + glint([[104, 176, 0], [124, 172, 4], [150, 186, 0]], RED.shade, 0.8) + glint([[218, 176, 0], [198, 172, 4], [172, 186, 0]], RED.shade, 0.8)
  + '</g>';

// ---------- les morceaux, du fond vers le devant ----------
const sh = (on, dx, dy, color, o) => ({ on, dx, dy, color, o });
const tasselBody = (id, x) => use(id, 'url(#g-tassel)') + clip(id,
  // les brins de la houppe : quelques fuseaux plus clairs et plus sombres (pas de rayures régulières)
  glint([[x - 6, 200, 0], [x - 10, 226, 3.4], [x - 14, 252, 0]], RED.hi, 0.5) + glint([[x + 4, 200, 0], [x + 6, 228, 3.4], [x + 4, 254, 0]], RED.deep, 0.6)
  + glint([[x - 16, 204, 4], [x, 206, 5], [x + 14, 204, 4]], GOLD.base, 0.9));
const parts = [
  { id: 'cordL', cls: 'a-tasL', d: S.cordL, body: use('cordL', 'url(#g-goldX)') },
  { id: 'cordR', cls: 'a-tasR', d: S.cordR, body: use('cordR', 'url(#g-goldX)') },
  { id: 'tasselL', cls: 'a-tasL', d: S.tasselL, body: tasselBody('tasselL', 40) },
  { id: 'tasselR', cls: 'a-tasR', d: S.tasselR, body: tasselBody('tasselR', 280) },
  { id: 'ballL', cls: 'a-tasL', d: S.ballL, shadow: [sh(['tasselL'], -2, 4, SH.red, 0.5)], body: use('ballL', 'url(#g-ball)') + clip('ballL', oval(50, 178, 4, 3, '#fff', 0.85)) },
  { id: 'ballR', cls: 'a-tasR', d: S.ballR, shadow: [sh(['tasselR'], -2, 4, SH.red, 0.5)], body: use('ballR', 'url(#g-ball)') + clip('ballR', oval(288, 178, 4, 3, '#fff', 0.85)) },
  { id: 'orb', cls: 'a-orb', d: S.orb, body: `<g class="a-glow">${oval(162, 370, 54, 44, 'url(#g-glow)')}</g>` + use('orb', 'url(#g-orb)') + clip('orb', oval(170, 360, 10, 8, '#ffffff', 0.85)) },
  { id: 'base', d: S.base, shadow: [sh(['orb'], -3, 5, SH.gold, 0.45)], body: use('base', 'url(#g-gold)') + clip('base',
    // deux anneaux dorés, l'ombre du dessous, des clous
    glint([[104, 304, 4], [160, 308, 5], [216, 304, 4]], GOLD.hi, 0.8) + shape(sm('110,322 160,326 210,322 204,344 116,344'), GOLD.shade, 0.6)
    + [[130, 316], [160, 318], [190, 316]].map(([x, y]) => dot(x, y, 3, GOLD.hi)).join('')) },
  { id: 'body', cls: 'a-body', d: S.body, shadow: [sh(['base', 'cordL', 'cordR', 'ballL', 'ballR'], -4, 5, SH.red, 0.45)], body: use('body', 'url(#g-body)') + clip('body',
    // la lumière du dedans, les côtes du papier (une ombre et une arête claire, qui suivent la courbe), les bandeaux
    // rouges du haut et du bas cloutés d'or, le visage
    `<g class="a-light">${oval(158, 210, 96, 116, 'url(#g-inner)')}</g>`
    + [[96, 0.5], [128, 0.35], [190, 0.35], [222, 0.5]].map(([x, o]) => glint([[x + (x < 160 ? 8 : -8), 124, 0], [x, 210, 4], [x + (x < 160 ? 8 : -8), 296, 0]], RED.shade, o)
      + glint([[x + (x < 160 ? 12 : -4), 124, 0], [x + 4, 210, 2], [x + (x < 160 ? 12 : -4), 296, 0]], LIGHT.hi, o * 0.8)).join('')
    + shape(sm('60,118 256,118 256,146 60,146'), RED.mid) + glint([[64, 140, 3], [160, 142, 4], [254, 140, 3]], RED.shade, 0.9)
    + shape(sm('60,278 256,278 256,300 60,300'), RED.mid) + glint([[64, 282, 3], [160, 280, 4], [254, 282, 3]], RED.hi, 0.6)
    + shape(sm('60,300 256,300 256,314 60,314'), GOLD.mid)
    + [[84, 132], [120, 130], [160, 130], [200, 130], [236, 132], [90, 289], [126, 290], [160, 290], [196, 290], [230, 289]].map(([x, y]) => dot(x, y, 3.6, 'url(#g-ball)')).join('')
    + faceBody) },
  { id: 'roof', cls: 'a-roof', d: S.roof, shadow: [sh(['body', 'cordL', 'cordR'], -4, 6, SH.red, 0.5)], body: use('roof', 'url(#g-roof)') + clip('roof',
    // les côtes du toit, de la pointe vers le bord : alternance de pans rouges et dorés (pas de rayures : des pans
    // qui s'élargissent, de tailles différentes)
    [[150, 52, 70, 112, 'r'], [154, 52, 104, 118, 'g'], [158, 52, 136, 120, 'r'], [164, 52, 170, 122, 'g'], [170, 52, 206, 120, 'r'], [176, 54, 240, 118, 'g'], [180, 56, 270, 110, 'r']].map(([x0, y0, x1, y1, c]) =>
      glint([[x0, y0, 0], [(x0 + x1) / 2, (y0 + y1) / 2, 10], [x1, y1, 16]], c === 'g' ? GOLD.base : RED.lite, c === 'g' ? 0.85 : 0.55)).join('')
    // le bord du toit : un galon doré, les coins relevés éclairés
    + glint([[36, 112, 5], [100, 120, 6], [160, 122, 6], [220, 120, 6], [284, 112, 5]], GOLD.lite, 0.95)
    + glint([[40, 106, 0], [100, 114, 2], [160, 116, 2], [220, 114, 2], [282, 106, 0]], GOLD.hi, 0.9)
    + shape(sm('130,58 150,48 176,48 196,58 176,64 150,64'), GOLD.mid, 0.9)) },
  { id: 'knob', cls: 'a-roof', d: S.knob, shadow: [sh(['roof'], -2, 4, SH.gold, 0.5)], body: use('knob', 'url(#g-ball)') + clip('knob', oval(170, 18, 5, 4, '#ffffff', 0.85)) },
];

// ---------- la vie au repos et l'attaque ----------
// Repos : elle flotte (tout monte et descend doucement, l'ombre au sol reste posée), elle se balance un peu, les glands
// oscillent en retard, la lumière intérieure et la boule du dessous palpitent comme une flamme.
// Attaque (classe « atk » sur le <svg>, 0,75 s) : elle se gonfle en reculant (élan), puis fonce en avant et s'embrase
// (la lumière flambe, le visage s'allume) ; tout revient à la pose de repos.
const PIV = { root: [160, 200], tasL: [44, 118], tasR: [280, 118] };
const style = `
.a-root{transform-origin:160px 200px;animation:float 2.6s ease-in-out infinite alternate}
.a-tasL{transform-origin:44px 118px;animation:tas 2.2s ease-in-out infinite alternate}
.a-tasR{transform-origin:280px 118px;animation:tas 2.4s ease-in-out -.6s infinite alternate}
.a-light{transform-origin:158px 210px;animation:light .7s ease-in-out infinite alternate}
.a-glow{transform-origin:162px 370px;animation:light .9s ease-in-out infinite alternate}
.a-face{animation:face 1.4s ease-in-out infinite alternate}
@keyframes float{from{transform:translate(0,0) rotate(-1.2deg)}to{transform:translate(0,-8px) rotate(1.2deg)}}
@keyframes tas{from{transform:rotate(3deg)}to{transform:rotate(-3deg)}}
@keyframes light{from{transform:scale(.94);opacity:.85}to{transform:scale(1.04);opacity:1}}
@keyframes face{from{opacity:.85}to{opacity:1}}
.atk .a-root{animation:float 2.6s ease-in-out infinite alternate,root-atk .75s ease-in-out;animation-composition:replace,add}
.atk .a-light{animation:light-atk .75s ease-in-out}
.atk .a-glow{animation:light-atk .75s ease-in-out}
@keyframes root-atk{0%{transform:none}30%{transform:translate(-8px,-4px) scale(1.06)}50%{transform:translate(18px,2px) scale(.96,1.04)}64%{transform:translate(14px,0)}100%{transform:none}}
@keyframes light-atk{0%{transform:none}30%{transform:scale(.9)}50%{transform:scale(1.35)}64%{transform:scale(1.2)}100%{transform:none}}
`.replace(/\n/g, '');

function svg(anime = true) {
  const s = figure({ master: require('./silhouettes/parade-4.json'), w: W, h: H, pad: PAD, defs, style, parts, anime });
  if (!anime) return s;
  // toute la lanterne flotte (l'ombre au sol est posée par le jeu, pas par le dessin)
  const i0 = s.indexOf('<g fill="#2a1430"');
  return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>');
}

module.exports = { id: 'parade-4', w: W, h: H, pad: PAD, foot: [160, 405], svg };
