// Personnages « épurés » (v5) : petits à l'écran, silhouette nette, un ou deux éléments forts par personnage,
// regard dur. Repère : boîte 200 × 240, pieds à y = 228, tourné vers la droite (trois-quarts).
// Peu de formes : dos → bras du fond → jambes + buste → tête (visage, coiffe) → bras de devant + arme.
const { painter, tone, metal, mix, ln, sf, blob } = require('./kit.cjs');
const f = (n) => (Math.round(n * 10) / 10).toString();
const pt = (p) => `${f(p[0])} ${f(p[1])}`;

/** Un membre d'un seul tenant : courbe épaisse (largeur w0 → w1), bouts arrondis. */
function limb([a, c, b], w0, w1 = w0, N = 12) {
  const L = [], R = [];
  for (let i = 0; i <= N; i++) {
    const t = i / N, u = 1 - t;
    const x = u * u * a[0] + 2 * u * t * c[0] + t * t * b[0], y = u * u * a[1] + 2 * u * t * c[1] + t * t * b[1];
    let dx = 2 * u * (c[0] - a[0]) + 2 * t * (b[0] - c[0]), dy = 2 * u * (c[1] - a[1]) + 2 * t * (b[1] - c[1]);
    const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
    const w = (w0 + (w1 - w0) * t) / 2;
    L.push([x - dy * w, y + dx * w]); R.push([x + dy * w, y - dx * w]);
  }
  const r0 = f(w0 / 2), r1 = f(w1 / 2);
  return `M${L.map(pt).join(' L')} A${r1} ${r1} 0 0 0 ${pt(R[N])} L${R.slice(0, N).reverse().map(pt).join(' L')} A${r0} ${r0} 0 0 0 ${pt(L[0])} Z`;
}
/** Lame (ou tout objet droit et pointu) de a vers b. */
function blade(a, b, w, tip = 0.8) {
  const v = [b[0] - a[0], b[1] - a[1]], len = Math.hypot(...v), u = [v[0] / len, v[1] / len], n = [-u[1], u[0]];
  const at = (t, k) => [a[0] + u[0] * t * len + n[0] * k, a[1] + u[1] * t * len + n[1] * k];
  return { d: `M${pt(at(0, -w / 2))} L${pt(at(tip, -w / 2))} L${pt(at(1, 0))} L${pt(at(tip, w / 2))} L${pt(at(0, w / 2))} Z`, mid: `M${pt(at(0.03, 0))} L${pt(at(0.95, 0))}`, at, u, n, len };
}
const bar = (a, b, w) => { const B = blade(a, b, w, 1); return `M${pt(B.at(0, -w / 2))} L${pt(B.at(1, -w / 2))} L${pt(B.at(1, w / 2))} L${pt(B.at(0, w / 2))} Z`; };
const disc = (x, y, r) => `M${f(x - r)} ${f(y)} A${r} ${r} 0 1 0 ${f(x + r)} ${f(y)} A${r} ${r} 0 1 0 ${f(x - r)} ${f(y)} Z`;

const HEAD = 'M106 40 C131 40 148 57 148 81 C148 98 139 112 124 118 C114 121 100 121 90 117 C74 111 64 97 64 79 C64 56 82 40 106 40 Z';
const GHEAD = 'M104 46 C130 44 150 60 150 83 C150 100 140 114 124 119 C112 122 98 121 88 116 C72 109 62 97 62 82 C62 60 80 46 104 46 Z';
const TORSO = 'M75 121 C92 112 122 112 139 121 C141 136 142 150 143 160 L147 177 C122 187 92 187 67 177 L71 160 C72 148 73 134 75 121 Z';
const LEGS = 'M72 164 L142 164 L152 198 L170 218 C176 222 176 228 168 228 L136 228 L128 200 L108 184 L94 204 L94 228 L58 228 C52 228 52 220 58 216 L66 198 Z';
const ROBE = 'M80 118 C94 112 120 112 134 118 C142 150 152 190 160 222 C130 232 82 232 52 222 C60 190 72 150 80 118 Z';
// Capuche : un anneau fermé autour du visage, pointe vers l'arrière.
const HOOD = 'M56 86 C54 72 58 58 66 48 C56 44 46 46 34 54 C44 38 62 30 78 32 C88 27 98 26 108 26 C142 26 162 52 158 88 C156 106 148 118 136 126 L84 126 C68 118 58 104 56 86 Z ' +
  'M84 86 C84 66 98 56 116 56 C134 56 150 68 150 86 C150 100 142 112 128 117 C116 120 102 120 94 115 C86 109 84 98 84 86 Z';

/** Œil au regard dur : amande coupée par une paupière en biais (dir = +1 : côté nez à droite). */
function eye(id, cx, cy, w, h, col, dir, o = {}) {
  const lens = `M${f(cx - w / 2)} ${f(cy)} Q${f(cx)} ${f(cy - h * 0.8)} ${f(cx + w / 2)} ${f(cy)} Q${f(cx)} ${f(cy + h * 0.8)} ${f(cx - w / 2)} ${f(cy)} Z`;
  const ox = cx - dir * (w / 2 + 2), ix = cx + dir * (w / 2 + 2);
  const so = o.calm ? 0.36 : 0.46, si = o.calm ? 0.24 : 0.02;
  const lid = `M${f(ox)} ${f(cy - h)} L${f(ix)} ${f(cy - h)} L${f(ix)} ${f(cy - h * si)} L${f(ox)} ${f(cy - h * so)} Z`;
  let s = `<defs><clipPath id="${id}"><path d="${lens}"/></clipPath></defs>`;
  if (o.glow) s += `<ellipse cx="${cx}" cy="${cy}" rx="${w * 0.8}" ry="${h * 0.7}" fill="${col}" opacity="0.55" filter="url(#g2)"/>`;
  s += `<path d="${lens}" fill="${o.sclera ?? '#fbf6ef'}"/><g clip-path="url(#${id})">`;
  if (o.glow) s += `<ellipse cx="${cx}" cy="${cy + 1}" rx="${w * 0.3}" ry="${h * 0.34}" fill="#fff" opacity="0.85"/>`;
  else {
    const r = h * 0.46;
    s += `<circle cx="${f(cx + dir * w * 0.1)}" cy="${f(cy + 0.5)}" r="${f(r)}" fill="${col}"/>`;
    s += o.slit ? `<ellipse cx="${f(cx + dir * w * 0.1)}" cy="${f(cy + 0.5)}" rx="${f(w * 0.07)}" ry="${f(r * 0.9)}" fill="#170a12"/>` : `<circle cx="${f(cx + dir * w * 0.1)}" cy="${f(cy + 0.8)}" r="${f(r * 0.52)}" fill="#170a12"/>`;
    s += `<circle cx="${f(cx - w * 0.12)}" cy="${f(cy - h * 0.12)}" r="${f(w * 0.1)}" fill="#fff"/>`;
  }
  s += `<path d="${lid}" fill="${o.lid ?? '#2a1424'}"/></g>`;
  s += `<path d="M${f(ox + dir * 2)} ${f(cy - h * so)} L${f(ix - dir * 2)} ${f(cy - h * si)}" stroke="${o.lid ?? '#2a1424'}" stroke-width="2.2" stroke-linecap="round"/>`;
  return s;
}
const brow = (cx, cy, w, h, dir, col, k = 4.6, calm = false) => `<path d="M${f(cx - dir * (w / 2 + 4))} ${f(cy - h * (calm ? 0.36 : 0.46) - 8)} L${f(cx + dir * (w / 2 + 2))} ${f(cy - h * (calm ? 0.24 : 0.02) - (calm ? 8 : 6))}" stroke="${col}" stroke-width="${k}" stroke-linecap="round"/>`;

function figure(c) {
  const P = painter(c.light ?? [0.5, -0.85]);
  const { S, raw } = P;
  const T = {};
  for (const [k, v] of Object.entries(c.colors)) T[k] = typeof v === 'string' ? tone(v) : v;
  T.steel ??= metal('#b9c2d0'); T.gold ??= metal('#e6ac3c'); T.wood ??= tone('#8a5a34'); T.boot ??= tone('#4a3226'); T.belt ??= tone('#5e3a22');
  T.pants ??= tone('#3a3550'); T.sleeve ??= T.cloth; T.glove ??= T.skin; T.hair ??= tone('#333');
  const G = (fn) => { raw('<g filter="url(#ol)">'); fn(); raw('</g>'); };
  const fist = (x, y, r = 9, t = T.glove, o = {}) => S(disc(x, y, r), t, { sh: 4, hl: 3, rim: false, ...o });
  const glows = [];
  // Les halos (orbe, lame de feu) sont rendus à part, derrière le personnage, pour ne pas être pris dans son contour.
  const glow = (svg) => glows.push(svg);
  const h = { S, raw, G, T, fist, P, c, glow };
  const gob = c.kind === 'goblin';
  const head = gob ? GHEAD : HEAD;
  raw(`<defs><clipPath id="hc${c.id}"><path d="${head}"/></clipPath></defs>`);

  // ---- derrière : cape, écharpe, cheveux longs, oreille du fond
  G(() => {
    c.back?.(h);
    if (gob) S('M142 70 C154 56 170 48 184 48 C178 62 166 76 150 86 Z', T.skin, { far: true });
  });
  // ---- bras du fond (et ce qu'il tient derrière le corps)
  if (c.farArm) G(() => c.farArm(h));
  // ---- corps : jambes + buste, ou robe ; la ceinture est peinte dans la forme, donc d'un bord à l'autre
  const beltY = c.beltY ?? 156;
  const band = (t, y, k = 9) => `<path d="M50 ${y} C90 ${y + 10} 126 ${y + 10} 164 ${y} L164 ${y + k} C126 ${y + k + 10} 90 ${y + k + 10} 50 ${y + k} Z" fill="${t.base}"/><path d="M50 ${y + k} C90 ${y + k + 10} 126 ${y + k + 10} 164 ${y + k}" stroke="${t.shadow}" stroke-width="2" fill="none" opacity="0.8"/>`;
  G(() => {
    if (c.robe) S(ROBE, T.cloth, { sh: 10, inner: (c.robeInner ?? '') + band(T.belt, beltY, 11) });
    else {
      S(limb([[88, 166], [80, 190], [76, 212]], 25, 21), T.pants, { sh: 6 });
      S(limb([[126, 166], [140, 188], [148, 212]], 25, 21), T.pants, { sh: 6 });
      const cuff = (x) => `<path d="M${x} 207 L${x + 34} 207" stroke="${T.boot.light}" stroke-width="3" opacity="0.6"/>`;
      S('M62 204 L91 204 L93 215 L105 221 C110 224 109 228 104 228 L62 228 C58 228 58 224 60 220 Z', T.boot, { sh: 5, inner: cuff(60) });
      S('M134 204 L163 204 L165 215 L178 221 C183 224 182 228 177 228 L134 228 C130 228 130 224 132 220 Z', T.boot, { sh: 5, inner: cuff(132) });
      S(TORSO, T.cloth, { sh: 9, inner: (c.torsoInner ?? '') + band(T.belt, beltY) });
    }
  });
  if (c.nearArm) G(() => c.nearArm(h));
  if (c.afterBody) G(() => c.afterBody(h));
  // ---- tête : visage, puis coiffe (cheveux, casque, capuche) dans le même contour
  G(() => {
    const E = c.eyes ?? {};
    const ny = gob ? 85 : 88;
    const lidC = gob ? mix(T.skin.base, '#14200c', 0.7) : (E.lid ?? '#2a1424');
    let face = '';
    if (c.mask) face += `<path d="M50 ${c.mask} L160 ${c.mask - 6} L160 130 L50 130 Z" fill="${T.cloth.base}"/><path d="M50 ${c.mask} L160 ${c.mask - 6}" stroke="${T.cloth.shadow}" stroke-width="2" opacity="0.7"/>`;
    if (c.warpaint) face += `<path d="M96 96 L112 100 M94 103 L108 107" stroke="${c.warpaint}" stroke-width="3.4" stroke-linecap="round"/>`;
    if (c.headInner) face += c.headInner;
    S(head, T.skin, { sh: 9, hl: 6, inner: blob('M140 60 C152 76 152 100 138 116 L160 122 L160 54 Z', T.skin.shadow, 0.45, 3) + face });
    let s = eye(`e${c.id}n`, 103, ny, 20, gob ? 14 : 16, E.color ?? '#5a3a20', 1, { ...E, lid: lidC }) + eye(`e${c.id}f`, 134, ny, 13.5, gob ? 13 : 15, E.color ?? '#5a3a20', -1, { ...E, lid: lidC });
    if (c.brows !== false) s += brow(103, ny, 20, 16, 1, c.browColor ?? (gob ? lidC : T.hair.shadow), E.calm ? 3.4 : 5, E.calm) + brow(134, ny, 13.5, 15, -1, c.browColor ?? (gob ? lidC : T.hair.shadow), E.calm ? 3 : 4.4, E.calm);
    if (gob) {
      s += `<path d="M110 107 C120 112 132 110 142 103" stroke="#1c2a10" stroke-width="2.4" fill="none" stroke-linecap="round"/><path d="M114 109.5 L118 100 L123 110.5 Z" fill="#fff8e0" stroke="#1c2a10" stroke-width="1"/>`;
    } else if (!c.mask && !c.beard) {
      s += `<path d="M122 99 L127 101" stroke="${T.skin.shadow}" stroke-width="2" stroke-linecap="round"/>`;
      s += c.mouth === 'smile' ? `<path d="M113 107 C118 111 124 111 129 106" stroke="#8a3a3a" stroke-width="2.2" fill="none" stroke-linecap="round"/>` : c.mouth === 'smirk' ? `<path d="M112 108 C118 110 124 110 130 106" stroke="#5a2a22" stroke-width="2.4" fill="none" stroke-linecap="round"/>` : `<path d="M113 108.5 L128 107.5" stroke="#5a2a22" stroke-width="2.4" fill="none" stroke-linecap="round"/>`;
    }
    raw(s);
    if (gob) S('M138 88 C150 86 166 92 174 103 C162 106 148 105 138 100 Z', T.skin, { sh: 4, hl: 3, rim: false });
    c.headgear?.(h);
    if (gob) S('M72 80 C56 66 36 58 16 60 C28 76 46 94 70 102 Z', T.skin, { sh: 6, inner: sf('M64 86 C50 76 38 70 26 67', T.skin.shadow, 3, 0.5, 1) });
  });
  if (c.afterHead) G(() => c.afterHead(h));
  // ---- devant : bras de devant, main et arme en dernier
  if (c.front) G(() => c.front(h));
  return { defs: P.defs, body: P.body, glow: glows.join('') };
}
module.exports = { figure, limb, blade, bar, disc, eye, HOOD, HEAD, GHEAD, tone, metal, mix, ln, sf, blob };
