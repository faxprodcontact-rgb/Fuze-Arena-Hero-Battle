// Gabarit des héros, version 6 : rien n'est commun d'office entre deux héros.
//  - carrure : largeur d'épaules, taille, hanches, ventre, longueur des jambes, taille et position de la tête, buste penché ;
//  - bras : chaque main a sa place (et son coude), l'objet tenu se dessine à partir de la main ;
//  - chaque couche (dos, cou, coiffe, objets) est une liste de commandes : pièces de bibliothèque ou formes propres au héros.
// Repère : boîte 200 × 240, pieds à y = 228, tourné vers la droite. Ordre des couches :
//   dos → bras du fond → jambes → buste → manche de devant → épaule → cou → tête → par-dessus la tête → main du fond → main de devant.
const { painter, tone, metal, mix, ln, sf, blob } = require('./kit.cjs');
const f = (n) => (Math.round(n * 10) / 10).toString();
const pt = (p) => `${f(p[0])} ${f(p[1])}`;
const poly = (pts) => 'M' + pts.map(pt).join(' L') + ' Z';
const add = (a, b, k = 1) => [a[0] + b[0] * k, a[1] + b[1] * k];
const unit = (a, b) => { const v = [b[0] - a[0], b[1] - a[1]], l = Math.hypot(...v) || 1; return [v[0] / l, v[1] / l]; };
const perp = (u) => [-u[1], u[0]];
const disc = (x, y, r) => `M${f(x - r)} ${f(y)} A${f(r)} ${f(r)} 0 1 0 ${f(x + r)} ${f(y)} A${f(r)} ${f(r)} 0 1 0 ${f(x - r)} ${f(y)} Z`;
const ell = (x, y, rx, ry) => `M${f(x - rx)} ${f(y)} A${f(rx)} ${f(ry)} 0 1 0 ${f(x + rx)} ${f(y)} A${f(rx)} ${f(ry)} 0 1 0 ${f(x - rx)} ${f(y)} Z`;
const ring = (x, y, rx, ry, w) => ell(x, y, rx, ry) + ' ' + `M${f(x - rx + w)} ${f(y)} A${f(rx - w)} ${f(Math.max(1, ry - w))} 0 1 1 ${f(x + rx - w)} ${f(y)} A${f(rx - w)} ${f(Math.max(1, ry - w))} 0 1 1 ${f(x - rx + w)} ${f(y)} Z`;
/** Un membre d'un seul tenant : courbe épaisse (largeur w0 → w1), bouts arrondis. */
function limb([a, c, b], w0, w1 = w0, N = 14) {
  const L = [], R = [];
  for (let i = 0; i <= N; i++) {
    const t = i / N, u = 1 - t;
    const x = u * u * a[0] + 2 * u * t * c[0] + t * t * b[0], y = u * u * a[1] + 2 * u * t * c[1] + t * t * b[1];
    let dx = 2 * u * (c[0] - a[0]) + 2 * t * (b[0] - c[0]), dy = 2 * u * (c[1] - a[1]) + 2 * t * (b[1] - c[1]);
    const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
    const w = (w0 + (w1 - w0) * t) / 2;
    L.push([x - dy * w, y + dx * w]); R.push([x + dy * w, y - dx * w]);
  }
  const r0 = f(Math.max(0.5, w0 / 2)), r1 = f(Math.max(0.5, w1 / 2));
  return `M${L.map(pt).join(' L')} A${r1} ${r1} 0 0 0 ${pt(R[N])} L${R.slice(0, N).reverse().map(pt).join(' L')} A${r0} ${r0} 0 0 0 ${pt(L[0])} Z`;
}
const qpoint = ([a, c, b], t) => { const u = 1 - t; return [u * u * a[0] + 2 * u * t * c[0] + t * t * b[0], u * u * a[1] + 2 * u * t * c[1] + t * t * b[1]]; };
function blade(a, b, w, tip = 0.8) {
  const u = unit(a, b), n = perp(u), len = Math.hypot(b[0] - a[0], b[1] - a[1]);
  const at = (t, k) => [a[0] + u[0] * t * len + n[0] * k, a[1] + u[1] * t * len + n[1] * k];
  return { d: `M${pt(at(0, -w / 2))} L${pt(at(tip, -w / 2))} L${pt(at(1, 0))} L${pt(at(tip, w / 2))} L${pt(at(0, w / 2))} Z`, mid: `M${pt(at(0.04, 0))} L${pt(at(0.93, 0))}`, at, u, n, len };
}
const bar = (a, b, w) => { const u = unit(a, b), n = perp(u); return poly([add(a, n, -w / 2), add(b, n, -w / 2), add(b, n, w / 2), add(a, n, w / 2)]); };
/** Dents de scie couchées dans un seul sens (cheveux, fourrure, flammes). La ligne se parcourt du bas vers le haut. */
function saw(base, len, lean) {
  let d = '';
  for (let i = 0; i < base.length - 1; i++) {
    const a = base[i], b = base[i + 1], n = perp(unit(a, b));
    d += ` L${pt([(a[0] + b[0]) / 2 - n[0] * len + lean[0], (a[1] + b[1]) / 2 - n[1] * len + lean[1]])} L${pt(b)}`;
  }
  return d;
}
const arcPts = (cx, cy, rx, ry, a0, a1, n) => Array.from({ length: n + 1 }, (_, i) => { const a = (a0 + (a1 - a0) * i / n) * Math.PI / 180; return [cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]; });

const CX = 106, GROUND = 228, HIP = 172;
// Carrures : sw épaules, ww taille, hw bas du buste (demi-largeurs), belly ventre, drop jambes plus courtes (+) ou plus longues (−),
// hs taille de la tête, arm épaisseur du bras (épaule, poignet), lean buste penché en avant (degrés).
const BODY = {
  normal: { sw: 32, ww: 31, hw: 40 },
  heavy: { sw: 42, ww: 38, hw: 46, arm: [27, 23] },
  brute: { sw: 48, ww: 32, hw: 38, arm: [31, 26], hs: 0.9, sy: 124 },
  slim: { sw: 27, ww: 24, hw: 34, arm: [18, 15] },
  curvy: { sw: 27, ww: 21, hw: 37, arm: [17, 14] },
  round: { sw: 33, ww: 34, hw: 44, belly: 13, arm: [24, 20] },
  small: { sw: 30, ww: 30, hw: 38, drop: 14, hs: 1.05 },
  tall: { sw: 30, ww: 26, hw: 35, drop: -12, hs: 0.93, arm: [19, 16] },
};
// Places de la main (hand) et du coude (el) : bras de devant, puis bras du fond.
const NEAR = {
  up: { hand: [120, 149], el: [88, 158] }, shoulder: { hand: [114, 147], el: [84, 156] }, low: { hand: [118, 147], el: [84, 158] },
  chest: { hand: [114, 145], el: [90, 152] }, pole: { hand: [114, 151], el: [88, 156] }, pull: { hand: [120, 128], el: [96, 150] },
  fwd: { hand: [110, 160], el: [84, 158] }, down: { hand: [80, 176], el: [72, 152] }, hip: { hand: [92, 164], el: [66, 150] },
  raise: { hand: [68, 100], el: [60, 126] }, point: { hand: [150, 136], el: [112, 152] }, cross: { hand: [130, 146], el: [94, 160] },
  guard: { hand: [120, 130], el: [92, 154] }, back: { hand: [62, 158], el: [72, 142] }, center: { hand: [124, 148], el: [92, 158] },
};
const FAR = {
  staff: { hand: [164, 146], el: [148, 142] }, fwd: { hand: [178, 129], el: [150, 124] }, stab: { hand: [168, 126], el: [152, 142] },
  up: { hand: [170, 99], el: [158, 126] }, pole: { hand: [152, 129], el: [146, 136] }, down: { hand: [150, 176], el: [154, 152] },
  hip: { hand: [138, 164], el: [160, 150] }, high: { hand: [162, 84], el: [164, 120] }, open: { hand: [180, 136], el: [154, 142] },
  center: { hand: [140, 144], el: [150, 148] },
};
const LIB = { cmd: {}, legs: {}, head: {}, chest: {} };

function build(s) {
  const P = painter(s.light ?? [0.5, -0.85]);
  const { S, raw } = P;
  const T = {};
  for (const [k, v] of Object.entries(s.colors)) T[k] = typeof v === 'string' ? tone(v) : v;
  T.steel ??= metal('#b9c2d0'); T.gold ??= metal('#e6ac3c'); T.wood ??= tone('#8a5a34'); T.boot ??= tone('#4a3226'); T.belt ??= tone('#5e3a22');
  T.pants ??= tone('#3a3550'); T.cloth ??= T.skin; T.sleeve ??= T.cloth; T.glove ??= T.skin; T.hair ??= tone('#33303a'); T.bone ??= tone('#ece4d0'); T.iron ??= metal('#5a5a6c');
  const TK = (k, d) => (k ? (T[k] ?? tone(k)) : T[d]);
  const B = { sw: 32, ww: 31, hw: 40, sy: 122, wy: 158, hy: 177, drop: 0, belly: 0, hs: 1, hdx: 0, hdy: 0, lean: 0, arm: [21, 18], ...(BODY[s.body] ?? {}), ...(s.shape ?? {}) };
  const U = ((B.lean ? `rotate(${B.lean} ${CX} ${HIP + B.drop}) ` : '') + (B.drop ? `translate(0 ${B.drop})` : '')).trim();
  const HT = (U + ` translate(${CX + B.hdx} ${121 + B.hdy}) scale(${B.hs}) translate(${-CX} -121)`).trim();
  const marks = [], glows = [];
  let cur = '';
  const G = (name, fn, tr = U) => { const start = P.body.length; cur = tr; raw(`<g${tr ? ` transform="${tr}"` : ''} filter="url(#ol)">`); fn(); raw('</g>'); cur = ''; if (P.body.length - start > 60) marks.push({ name, start, end: P.body.length }); };
  const at = (t, fn) => { const prev = cur; cur = (cur + ' ' + t).trim(); raw(`<g transform="${t}">`); fn(); raw('</g>'); cur = prev; };
  const glow = (svg) => glows.push(`<g${cur ? ` transform="${cur}"` : ''}>${svg}</g>`);
  const halo = (x, y, r, c, op = 0.8) => glow(`<circle cx="${f(x)}" cy="${f(y)}" r="${f(r)}" fill="${c}" opacity="${op}" filter="url(#glow)"/>`);
  const h = { S, raw, T, TK, B, s, at, glow, halo, tone, metal, ground: GROUND - B.drop, hipY: 166 + B.drop };
  /** Une main : poing fermé (défaut) ou main ouverte tournée vers « dir ». */
  h.hand = (p, o = {}) => {
    const t = TK(o.t, 'glove'), r = o.r ?? (B.arm[1] / 2 + 1.5);
    if ((o.kind ?? 'fist') === 'fist') return S(disc(p[0], p[1], r), t, { sh: 4, hl: 3, rim: false, far: o.far, inner: `<path d="M${f(p[0] - r * 0.1)} ${f(p[1] - r * 0.7)} q${f(r * 0.55)} ${f(r * 0.35)} ${f(r * 0.3)} ${f(r)}" stroke="${t.shadow}" stroke-width="1.5" fill="none" opacity="0.55"/>` });
    const d = o.dir ?? [1, 0], a = Math.atan2(d[1], d[0]) * 180 / Math.PI, k = r / 9.5;
    at(`translate(${f(p[0])} ${f(p[1])}) rotate(${f(a)}) scale(${f(k)})`, () => { S('M-3 -8 C-2 -15 5 -17 8 -13 C9 -10 6 -8 3 -8 Z', t, { sh: 2, hl: 2, rim: false, far: o.far }); S('M-9 -7 C-2 -11 9 -10 15 -5 C18 -1 18 3 15 6 C9 10 -2 10 -9 7 C-12 3 -12 -3 -9 -7 Z', t, { sh: 3, hl: 3, rim: false, far: o.far, inner: `<path d="M6 -6 L14 -3 M7 0 L16 1 M6 5 L13 5" stroke="${t.shadow}" stroke-width="1.2" opacity="0.5"/>` }); });
  };
  /** Exécute une liste de commandes [nom, options] ; « phase » sert aux coiffes (avant / après la tête). */
  const run = (list, extra = {}, phase) => { for (const c of list ?? []) { const [n, o] = Array.isArray(c) ? c : [c, {}]; const fn = LIB.cmd[n]; if (!fn) throw new Error(`pièce inconnue : ${n} (${s.id})`); fn(h, { ...extra, ...(o ?? {}) }, phase); } };
  h.run = run;
  const norm = (v, table) => { if (!v) return null; const o = typeof v === 'string' ? { pose: v } : v; const p = { ...(table[o.pose] ?? {}), ...o }; p.items = p.items ?? (p.item ? [p.item] : []); return p; };
  const near = norm(s.near, NEAR), far = norm(s.far, FAR);
  const shN = [CX - B.sw + 9, B.sy + 7], shF = [CX + B.sw - 9, B.sy + 7];
  const sleeve = (a) => TK(a.sleeve, s.bareArms ? 'skin' : 'sleeve');
  const armShape = (sh, a, w, tint) => {
    const pts = [sh, a.el, a.hand], t = sleeve(a); let inner = '';
    const br = a.bracer ?? s.bracers;
    if (br) { const p = qpoint(pts, 0.74), q = qpoint(pts, 0.8), n = perp(unit(p, q)); inner = `<path d="M${pt(add(p, n, -20))} L${pt(add(p, n, 20))}" stroke="${TK(br).base}" stroke-width="${f(w[1] * 0.6)}"/>`; }
    S(limb(pts, a.w0 ?? w[0], a.w1 ?? w[1]), t, { sh: 6, far: tint, inner });
  };
  const items = (a, layer, dflt) => run(a.items.filter((it) => ((it[1] ?? {}).layer ?? dflt) === layer), { hand: a.hand });

  // ---- 1. derrière
  G('back', () => { run(s.back); if (far) items(far, 'back', 'front'); if (near) items(near, 'back', 'front'); });
  // ---- 2. bras du fond (derrière le buste)
  if (far && !far.noArm && !far.over) G('farArm', () => { items(far, 'behind', 'front'); armShape(shF, far, [B.arm[1], B.arm[1] - 3], far.tint !== false); if (far.handBehind) h.hand(far.hand, { far: true, kind: far.handKind, dir: far.dir, r: far.r }); });
  // ---- 3. jambes (ou bas du corps), puis 4. buste
  const legs = s.legs ?? { kind: 'boots' }, lk = typeof legs === 'string' ? { kind: legs } : legs;
  if (!LIB.legs[lk.kind]) throw new Error(`jambes inconnues : ${lk.kind} (${s.id})`);
  const L = LIB.legs[lk.kind];
  if (!L.robe) G('legs', () => L.draw(h, lk), '');
  const band = (t, y, k = 9) => `<path d="M30 ${y} C90 ${y + 10} 126 ${y + 10} 184 ${y} L184 ${y + k} C126 ${y + k + 10} 90 ${y + k + 10} 30 ${y + k} Z" fill="${t.base}"/><path d="M30 ${y + k} C90 ${y + k + 10} 126 ${y + k + 10} 184 ${y + k}" stroke="${t.shadow}" stroke-width="2" fill="none" opacity="0.8"/>`;
  h.band = band;
  const chest = () => (s.chest ?? []).map(([n, o]) => { if (!LIB.chest[n]) throw new Error('buste inconnu : ' + n); return LIB.chest[n](h, o ?? {}); }).join('');
  G('torso', () => {
    if (L.robe) { L.draw(h, lk, chest() + (s.noBelt ? '' : band(T.belt, B.wy - 2, lk.belt ?? 10))); return; }
    const { sw, ww, hw, sy, wy, hy, belly } = B;
    const d = `M${CX - sw} ${sy} Q${CX} ${sy - 11} ${CX + sw} ${sy} C${CX + sw + 3} ${sy + 14} ${CX + ww + belly + 2} ${wy - 16} ${CX + ww + belly * 0.7} ${wy} L${CX + hw} ${hy} Q${CX} ${hy + 12} ${CX - hw} ${hy} L${CX - ww - belly * 0.15} ${wy} C${CX - ww - 2} ${wy - 16} ${CX - sw - 3} ${sy + 14} ${CX - sw} ${sy} Z`;
    S(d, s.bare ? T.skin : T.cloth, { sh: 9, inner: chest() + (s.noBelt ? '' : band(T.belt, wy - 2)) });
    if (s.skirt) { const k = s.skirt, len = k.len ?? 30, t = TK(k.t, 'cloth'), x0 = CX - ww - 3, x1 = CX + ww + belly * 0.7 + 3, y0 = wy + 6, y1 = wy + len, fl = k.flare ?? 8;
      let inner = ''; if (k.strips) for (let i = 1; i < k.strips; i++) { const x = x0 - fl + (x1 - x0 + 2 * fl) * i / k.strips; inner += `<path d="M${f(x0 + (x1 - x0) * i / k.strips)} ${y0} L${f(x)} ${y1 + 6}" stroke="${t.shadow}" stroke-width="2.2" opacity="0.7"/>`; }
      if (k.trim) inner += `<path d="M${x0 - fl - 4} ${y1 - 4} Q${CX} ${y1 + 8} ${x1 + fl + 4} ${y1 - 4}" stroke="${TK(k.trim).base}" stroke-width="5" fill="none"/>`;
      S(k.ragged ? `M${x0} ${y0} L${x1} ${y0} L${x1 + fl} ${y1}` + saw(Array.from({ length: 6 }, (_, i) => [x1 + fl - (x1 - x0 + 2 * fl) * i / 5, y1]), 7, [0, 0]) + ' Z' : `M${x0} ${y0} L${x1} ${y0} L${x1 + fl} ${y1} Q${CX} ${y1 + 10} ${x0 - fl} ${y1} Z`, t, { sh: 7, inner });
      if (k.flap) S(`M${CX - 8} ${y0 - 2} L${CX + 24} ${y0 - 2} L${CX + 22} ${y1 + (k.flapLen ?? 10)} L${CX + 8} ${y1 + (k.flapLen ?? 10) + 6} L${CX - 6} ${y1 + (k.flapLen ?? 10)} Z`, TK(k.flap), { sh: 4, inner: k.flapInner ?? '' });
    }
  });
  // ---- 5. manche de devant (sous le cou et la tête), 6. arme posée sur l'épaule, puis cou
  if (near && !near.noArm && !near.over) G('nearArm', () => armShape(shN, near, B.arm, false));
  if (near && near.items.some((it) => (it[1] ?? {}).layer === 'shoulder')) G('shoulderItem', () => items(near, 'shoulder', 'front'));
  G('afterBody', () => run(s.neck));
  // ---- 7. tête
  const hd = s.head ?? { kind: 'human' }, hk = typeof hd === 'string' ? { kind: hd } : hd;
  if (!LIB.head[hk.kind]) throw new Error(`tête inconnue : ${hk.kind} (${s.id})`);
  G('head', () => { run(s.gear, {}, 'back'); LIB.head[hk.kind](h, hk); run(s.gear, {}, 'front'); }, HT);
  G('afterHead', () => run(s.afterHead));
  // ---- 8. main du fond et ce qu'elle tient devant le corps
  if (far) G('farFront', () => { if (far.over && !far.noArm) armShape(shF, far, [B.arm[1], B.arm[1] - 3], far.tint === true); items(far, 'front', 'front'); if (!far.handBehind && far.handKind !== 'none') h.hand(far.hand, { kind: far.handKind, dir: far.dir, r: far.r, far: far.over ? false : undefined }); items(far, 'top', 'front'); });
  // ---- 9. main de devant et son arme, en dernier
  if (near) G('front', () => { if (near.over && !near.noArm) armShape(shN, near, B.arm, false); items(near, 'front', 'front'); if (near.handKind !== 'none') h.hand(near.hand, { kind: near.handKind, dir: near.dir, r: near.r }); items(near, 'top', 'front'); });
  G('top', () => run(s.top));

  // ---- squelette pour l'animation : articulations (avec la carrure), morceaux qui suivent chaque bras
  const tp = (p) => { const y = p[1] + B.drop, a = B.lean * Math.PI / 180, dx = p[0] - CX, dy = y - (HIP + B.drop); return [+(CX + dx * Math.cos(a) - dy * Math.sin(a)).toFixed(1), +(HIP + B.drop + dx * Math.sin(a) + dy * Math.cos(a)).toFixed(1)]; };
  const hasShoulder = marks.some((m) => m.name === 'shoulderItem');
  // Quel bras frappe ? Celui qui tient l'arme ; les deux ensemble pour une arme tenue à deux mains.
  const nearParts = ['nearArm', 'front', ...(hasShoulder ? ['shoulderItem'] : [])], farParts = ['farArm', 'farFront'];
  const armed = (a) => !!a && !a.noArm && a.items.some((it) => !['shield', 'glow'].includes(it[0]));
  const atk = s.atk ?? 'slash', melee = !['shoot', 'cast'].includes(atk);
  const both = s.both ?? (!!near && !!far && near.pose === 'pole' && armed(far));
  const main = s.main ?? (melee && !armed(near) && armed(far) ? 'far' : 'near');
  const [wind, hit] = atk === 'stab' ? [-14, 14] : both ? [-34, 30] : atk === 'smash' ? [-80, 42] : [-60, 45];
  const rig = { ...(both ? { swing: [...nearParts, ...farParts], far: [] } : main === 'far' ? { swing: farParts, far: nearParts } : { swing: nearParts, far: farParts, ...(hasShoulder ? { top: nearParts } : {}) }),
    piv: { swing: tp(main === 'far' && !both ? shF : shN), far: tp(main === 'far' && !both ? shN : shF), head: tp([CX, 119]), back: tp([96, 122]), torso: [CX, HIP + 4 + B.drop] },
    atk, wind, hit, ...(atk === 'stab' && !both && armed(near) && armed(far) ? { farWind: -25, farHit: 55 } : {}), ...(s.grp ? { grp: s.grp } : {}), ...(s.rig ?? {}) };
  // ---- l'élément qui brille : pour certains héros, un petit élément entier s'illumine (dessiné par-dessus, sans contour)
  const ELC = { fi: '#ffd76a', wi: '#eafff2', wa: '#dff4ff', ea: '#f0ffb0' }[String(s.id).slice(0, 2)] ?? '#fff6c8';
  const spotOf = (a) => { if (!a) return null; for (const [n, o0] of a.items) { const o = o0 ?? {}, hd = o.hand ?? a.hand;
    if (n === 'sword') return [hd[0] + (o.to[0] - hd[0]) * 0.72, hd[1] + (o.to[1] - hd[1]) * 0.72];
    if (['axe', 'mace', 'club'].includes(n)) return o.to;
    if (n === 'pole' && o.end) return o.end;
    if (n === 'staff') return [(o.x ?? hd[0]) + (o.leanX ?? 0), (o.top ?? 34) + 4];
    if (n === 'orb') return [hd[0] + (o.dx ?? 2), hd[1] - (o.dy ?? (o.r ?? 14) + 12)];
    if (n === 'shield') return [(o.c ?? [160, 166])[0] - 8, (o.c ?? [160, 166])[1] - 14];
    if (n === 'chakram') return o.c ?? [hd[0], hd[1] - (o.r ?? 20)];
    if (n === 'bolt') return [hd[0] + 30, hd[1] - 62];
    if (n === 'gun') return [hd[0] + 58, hd[1] - 12];
    if (n === 'small') { const d = o.dir ?? [33, 13], k = ((o.len ?? 36) * 0.8 + (o.off ?? 8)) / Math.hypot(d[0], d[1]); return [hd[0] + d[0] * k, hd[1] + d[1] * k]; }
    if (n === 'bow') return [(o.x ?? hd[0] - 16) + 36, (o.pull ?? [120, 128])[1]]; } return null; };
  const auto = () => { const n = spotOf(near), fa = spotOf(far); return n ? [[...n, 'near']] : fa ? [[...fa, 'far']] : []; };
  // pas pour tout le monde : seulement les héros dont la fiche le demande (shine: true = sur l'objet tenu, ou une liste de points)
  const shine = !s.shine ? [] : s.shine === true ? auto() : s.shine;
  // pas d'étoile : l'élément entier s'illumine (un halo doux par-dessus, cœur plus clair)
  const bloom = (x, y, r, c) => `<g transform="translate(${f(x)} ${f(y)})"><circle r="${f(r * 1.25)}" fill="${c}" opacity="0.7" filter="url(#glow)"/><circle r="${f(r * 0.6)}" fill="#fff" opacity="0.55" filter="url(#glow)"/></g>`;
  const fx = shine.map(([x, y, src = 'near', r = 11, c = ELC]) => `<g${(src === 'head' ? HT : U) ? ` transform="${src === 'head' ? HT : U}"` : ''}>${bloom(x, y, r, c)}</g>`).join('');
  if (shine.length) { const src = shine[0][2] ?? 'near'; rig.grp = { ...(rig.grp ?? {}), shine: src === 'head' ? 'head' : src === 'torso' ? 'torso' : both ? 'swing' : (src === 'near') === (main === 'far') ? 'far' : 'swing' }; }
  const body = P.body;
  return { defs: P.defs, body, glow: glows.join(''), fx, parts: marks.map((k) => ({ name: k.name, svg: body.slice(k.start, k.end) })), rig, spec: s };
}

// ---------- commandes de base, utilisables dans toutes les couches ----------
const C = LIB.cmd;
const OPT = (o) => ({ sh: o.sh, hl: o.hl, far: o.far, inner: o.inner, eo: o.eo, rim: o.rim, so: o.so });
C.shape = (h, o, ph) => { if (ph && (o.ph ?? 'front') !== ph) return; h.S(o.d, h.TK(o.t, 'cloth'), OPT(o)); };
C.limb = (h, o, ph) => { if (ph && (o.ph ?? 'front') !== ph) return; h.S(limb(o.pts, o.w0, o.w1 ?? o.w0, o.n ?? 14), h.TK(o.t, 'cloth'), OPT(o)); };
C.disc = (h, o, ph) => { if (ph && (o.ph ?? 'front') !== ph) return; h.S(o.ry ? ell(o.x, o.y, o.r, o.ry) : disc(o.x, o.y, o.r), h.TK(o.t, 'cloth'), OPT(o)); };
C.bar = (h, o, ph) => { if (ph && (o.ph ?? 'front') !== ph) return; h.S(bar(o.a, o.b, o.w), h.TK(o.t, 'wood'), { sh: 3, hl: 2, ...OPT(o) }); };
C.blade = (h, o, ph) => { if (ph && (o.ph ?? 'front') !== ph) return; h.S(blade(o.a, o.b, o.w, o.tip ?? 0.8).d, h.TK(o.t, 'steel'), { sh: 4, hl: 2, ...OPT(o) }); };
C.raw = (h, o, ph) => { if (ph && (o.ph ?? 'front') !== ph) return; h.raw(o.svg); };
C.glow = (h, o, ph) => { if (ph && (o.ph ?? 'front') !== ph) return; if (o.d) h.glow(`<path d="${o.d}" fill="${o.c}" opacity="${o.op ?? 0.8}" filter="url(#glow)"/>`); else h.halo(o.x, o.y, o.r, o.c, o.op); };
C.at = (h, o, ph) => { if (ph && (o.ph ?? 'front') !== ph) return; h.at(o.t, () => h.run(o.list)); };
C.hand = (h, o) => h.hand(o.p, o);

module.exports = { build, LIB, BODY, NEAR, FAR, CX, GROUND, HIP, f, pt, poly, add, unit, perp, disc, ell, ring, limb, qpoint, blade, bar, saw, arcPts, tone, metal, mix, ln, sf, blob };
