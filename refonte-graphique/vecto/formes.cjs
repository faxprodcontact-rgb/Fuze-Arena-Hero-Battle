// Outils de forme communs aux personnages vectoriels « décalqués » (repris du harfang et du renard) :
// sm (courbe lisse par des points, « ! » = angle vif), P, cw, rib (ruban effilé), glint (reflet ou ombre en fuseau),
// tooth (une dent), nest (emboîter des groupes animés). const { sm, rib, glint, tooth, nest } = require('./formes.cjs');
const { n, shape, line } = require('./lib.cjs');

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

/** Une dent pointue : la moitié du fond dans l'ombre, un filet de lumière sur l'autre flanc. b1, b2 = la racine, t = la pointe. */
function tooth([x1, y1], [x2, y2], [tx, ty]) {
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  const d = `M${x1} ${y1}Q${n((x1 + tx) / 2 - (ty - y1) * 0.08)} ${n((y1 + ty) / 2)} ${tx} ${ty}Q${n((x2 + tx) / 2 + (ty - y2) * 0.08)} ${n((y2 + ty) / 2)} ${x2} ${y2}Z`;
  const half = `M${x1} ${y1}L${tx} ${ty}L${n(mx)} ${n(my)}Z`;
  return shape(d, '#fbf4e8') + shape(half, '#d8c8bc', 0.8) + line(`M${n(mx + (x2 - mx) * 0.5)} ${n(my + (y2 - my) * 0.5)}L${n(tx + (x2 - tx) * 0.2)} ${n(ty + (y2 - ty) * 0.2)}`, '#ffffff', 1.2, 0.9);
}

/** Enveloppe chaque groupe de classe `cls` dans un groupe de classe `outer` (la tête emporte la mâchoire, etc.). */
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

/** Tout le personnage dans un groupe `a-root` (pour un bond, un vol). */
const rooted = (s) => { const i0 = s.indexOf('<g fill="#2a1430"'); return s.slice(0, i0) + '<g class="a-root">' + s.slice(i0).replace(/<\/svg>$/, '</g></svg>'); };

module.exports = { sm, P, cw, rib, glint, tooth, nest, rooted };
