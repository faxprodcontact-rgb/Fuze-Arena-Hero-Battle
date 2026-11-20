// Gabarit des 72 héros (style épuré v5) : même squelette que mini.cjs, mais tout se choisit par options
// (carrure, jambes, tête humaine ou animale, coiffe, dos, arme de la main de devant, objet de la main du fond).
// Repère : boîte 200 × 240, pieds à y = 228, tourné vers la droite.
const { painter, tone, metal, mix, ln, sf, blob } = require('./kit.cjs');
const { limb, blade, bar, disc, eye, HEAD, GHEAD } = require('./mini.cjs');
const f = (n) => (Math.round(n * 10) / 10).toString();
const pt = (p) => `${f(p[0])} ${f(p[1])}`;
const poly = (pts) => 'M' + pts.map(pt).join(' L') + ' Z';
const add = (a, b, k = 1) => [a[0] + b[0] * k, a[1] + b[1] * k];
const unit = (a, b) => { const v = [b[0] - a[0], b[1] - a[1]], l = Math.hypot(...v) || 1; return [v[0] / l, v[1] / l]; };
const perp = (u) => [-u[1], u[0]];
const ring = (x, y, rx, ry, w) => `M${f(x - rx)} ${f(y)} A${rx} ${ry} 0 1 0 ${f(x + rx)} ${f(y)} A${rx} ${ry} 0 1 0 ${f(x - rx)} ${f(y)} Z M${f(x - rx + w)} ${f(y)} A${rx - w} ${Math.max(1, ry - w)} 0 1 1 ${f(x + rx - w)} ${f(y)} A${rx - w} ${Math.max(1, ry - w)} 0 1 1 ${f(x - rx + w)} ${f(y)} Z`;
const ell = (x, y, rx, ry) => `M${f(x - rx)} ${f(y)} A${rx} ${ry} 0 1 0 ${f(x + rx)} ${f(y)} A${rx} ${ry} 0 1 0 ${f(x - rx)} ${f(y)} Z`;
/** Dents de scie couchées dans un seul sens (cheveux, fourrure, flammes) le long d'une ligne de points. */
function saw(base, len, lean) {
  let d = '';
  for (let i = 0; i < base.length - 1; i++) {
    const a = base[i], b = base[i + 1], n = perp(unit(a, b));
    const tip = [(a[0] + b[0]) / 2 - n[0] * len + lean[0], (a[1] + b[1]) / 2 - n[1] * len + lean[1]];
    d += ` L${pt(tip)} L${pt(b)}`;
  }
  return d;
}
/** Points sur un arc d'ellipse (angles en degrés, 0 = droite, 90 = bas). */
const arcPts = (cx, cy, rx, ry, a0, a1, n) => Array.from({ length: n + 1 }, (_, i) => { const a = (a0 + (a1 - a0) * i / n) * Math.PI / 180; return [cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]; });

const TORSO = {
  normal: 'M75 121 C92 112 122 112 139 121 C141 136 142 150 143 160 L147 177 C122 187 92 187 67 177 L71 160 C72 148 73 134 75 121 Z',
  heavy: 'M66 122 C90 110 126 110 148 122 C151 137 152 150 152 160 L156 179 C124 191 90 191 58 179 L62 160 C62 148 63 135 66 122 Z',
  slim: 'M80 121 C94 114 120 114 134 121 C135 136 136 150 137 160 L141 176 C120 185 94 185 73 176 L77 160 C78 148 79 134 80 121 Z',
};
const ROBE = 'M80 118 C94 112 120 112 134 118 C142 150 152 190 160 222 C130 232 82 232 52 222 C60 190 72 150 80 118 Z';
const ARMW = { normal: [21, 18], heavy: [27, 23], slim: [18, 15] };
const HOOD = 'M56 86 C54 72 58 58 66 48 C56 44 46 46 34 54 C44 38 62 30 78 32 C88 27 98 26 108 26 C142 26 162 52 158 88 C156 106 148 118 136 126 L84 126 C68 118 58 104 56 86 Z ' +
  'M84 86 C84 66 98 56 116 56 C134 56 150 68 150 86 C150 100 142 112 128 117 C116 120 102 120 94 115 C86 109 84 98 84 86 Z';
const HOOD_OPEN = 'M84 86 C84 66 98 56 116 56 C134 56 150 68 150 86 C150 100 142 112 128 117 C116 120 102 120 94 115 C86 109 84 98 84 86 Z';
const FRINGE = ' L141 60 L137 75 L123 58 L117 77 L103 60 L95 80 L85 66 L80 92 L72 104';
// Bras de devant : courbe de la manche + place de la main, selon la pose.
const POSE = {
  up: { arm: [[84, 128], [88, 158], [118, 150]], hand: [120, 149] },
  shoulder: { arm: [[82, 130], [84, 156], [112, 148]], hand: [114, 147] },
  low: { arm: [[82, 130], [84, 158], [116, 146]], hand: [118, 147] },
  chest: { arm: [[84, 128], [90, 152], [112, 146]], hand: [114, 145] },
  pole: { arm: [[84, 128], [88, 156], [112, 152]], hand: [114, 151] },
  pull: { arm: [[84, 128], [96, 150], [118, 130]], hand: [120, 128] },
  fwd: { arm: [[84, 130], [84, 158], [108, 160]], hand: [110, 160] },
};
const FARPOSE = {
  staff: { arm: [[130, 128], [148, 142], [160, 146]], hand: [164, 146] },
  fwd: { arm: [[130, 128], [150, 124], [170, 128]], hand: [178, 129] },
  stab: { arm: [[132, 128], [152, 142], [166, 128]], hand: [168, 126] },
  up: { arm: [[132, 128], [158, 126], [168, 102]], hand: [170, 99] },
  pole: { arm: [[132, 128], [146, 136], [150, 131]], hand: [152, 129] },
};
const brow = (cx, cy, w, h, dir, col, k, calm) => `<path d="M${f(cx - dir * (w / 2 + 4))} ${f(cy - h * (calm ? 0.36 : 0.46) - 8)} L${f(cx + dir * (w / 2 + 2))} ${f(cy - h * (calm ? 0.24 : 0.02) - (calm ? 8 : 6))}" stroke="${col}" stroke-width="${k}" stroke-linecap="round"/>`;

const LIB = { back: {}, gear: {}, near: {}, far: {}, neck: {}, legs: {} };

function build(s) {
  const P = painter(s.light ?? [0.5, -0.85]);
  const { S, raw } = P;
  const T = {};
  for (const [k, v] of Object.entries(s.colors)) T[k] = typeof v === 'string' ? tone(v) : v;
  T.steel ??= metal('#b9c2d0'); T.gold ??= metal('#e6ac3c'); T.wood ??= tone('#8a5a34'); T.boot ??= tone('#4a3226'); T.belt ??= tone('#5e3a22');
  T.pants ??= tone('#3a3550'); T.sleeve ??= T.cloth; T.glove ??= T.skin; T.hair ??= tone('#33303a'); T.bone ??= tone('#ece4d0'); T.iron ??= metal('#5a5a6c');
  const marks = [];
  const G = (name, fn) => { const start = P.body.length; raw('<g filter="url(#ol)">'); fn(); raw('</g>'); if (P.body.length - start > 30) marks.push({ name, start, end: P.body.length }); };
  const fist = (x, y, r = 9, t = T.glove, o = {}) => S(disc(x, y, r), t, { sh: 4, hl: 3, rim: false, ...o });
  const glows = [];
  const h = { S, raw, T, fist, s, glow: (svg) => glows.push(svg), tone, metal, at: (t, fn) => { raw('<g transform="' + t + '">'); fn(); raw('</g>'); } };
  const bw = ARMW[s.build ?? 'normal'];
  const near = s.near ? LIB.near[s.near[0]](s.near[1] ?? {}, h) : null;
  const far = s.far ? LIB.far[s.far[0]](s.far[1] ?? {}, h) : null;
  const gear = (s.gear ?? []).map(([n, o]) => [LIB.gear[n], o ?? {}, n]);
  for (const [fn, , n] of gear) if (!fn) throw new Error('coiffe inconnue : ' + n);

  // ---- derrière
  G('back', () => { for (const [n, o] of s.back ?? []) { if (!LIB.back[n]) throw new Error('dos inconnu : ' + n); LIB.back[n](h, o ?? {}); } });
  // ---- bras du fond
  if (far && FARPOSE[far.pose]) G('farArm', () => { far.behind?.(h); S(limb(FARPOSE[far.pose].arm, bw[1], bw[1] - 3), s.bareArms ? T.skin : T.sleeve, { far: !far.light, sh: 5 }); if (far.fistBehind) fist(...FARPOSE[far.pose].hand, 8.5, T.glove, { far: true }); });
  // ---- jambes puis buste
  const beltY = s.beltY ?? 156;
  const band = (t, y, k = 9) => `<path d="M40 ${y} C90 ${y + 10} 126 ${y + 10} 174 ${y} L174 ${y + k} C126 ${y + k + 10} 90 ${y + k + 10} 40 ${y + k} Z" fill="${t.base}"/><path d="M40 ${y + k} C90 ${y + k + 10} 126 ${y + k + 10} 174 ${y + k}" stroke="${t.shadow}" stroke-width="2" fill="none" opacity="0.8"/>`;
  const legs = s.legs ?? 'normal';
  let torsoInner = s.torsoInner ?? '';
  if (s.armor) torsoInner += `<path d="M40 100 L176 100 L176 ${beltY - 2} C130 ${beltY + 8} 90 ${beltY + 8} 40 ${beltY - 2} Z" fill="${T[s.armor].base}"/><path d="M106 112 L106 ${beltY + 4}" stroke="${T[s.armor].shadow}" stroke-width="2" opacity="0.6"/><path d="M60 126 C90 118 124 118 152 126" stroke="${T[s.armor].light}" stroke-width="3" fill="none" opacity="0.7"/>`;
  if (s.loin) torsoInner += `<path d="M40 ${beltY + 4} C90 ${beltY + 14} 126 ${beltY + 14} 174 ${beltY + 4} L174 200 L40 200 Z" fill="${T[s.loin].base}"/>`;
  if (legs === 'robe') G('torso', () => S(ROBE, T.cloth, { sh: 10, inner: (s.robeInner ?? '') + torsoInner + (s.noBelt ? '' : band(T.belt, beltY + 2, 11)) }));
  else {
    G('legs', () => LIB.legs[legs](h));
    G('torso', () => S(TORSO[s.build ?? 'normal'], s.bare ? T.skin : T.cloth, { sh: 9, inner: torsoInner + (s.noBelt ? '' : band(T.belt, beltY)) }));
  }
  if (near && near.pose) G('nearArm', () => S(limb(POSE[near.pose].arm, bw[0], bw[1]), s.bareArms ? T.skin : T.sleeve, { sh: 6 }));
  G('afterBody', () => { near?.shoulder?.(h); for (const [n, o] of s.neck ?? []) LIB.neck[n](h, o ?? {}); });
  // ---- tête : ce qui est derrière elle, visage, museau, barbe, coiffe
  const gob = s.head === 'gob';
  const headD = s.headPath ?? (gob ? GHEAD : HEAD);
  G('head', () => {
    for (const [fn, o] of gear) fn(h, o, 'back');
    const F = s.face ?? {}, E = s.eyes ?? {};
    if (gob) S('M142 70 C154 56 170 48 184 48 C178 62 166 76 150 86 Z', T.skin, { far: true });
    const ny = F.eyeY ?? (gob ? 85 : 88);
    const lidC = E.lid ?? (s.beast || gob ? mix(T.skin.base, '#140c10', 0.72) : '#2a1424');
    let inner = blob('M140 60 C152 76 152 100 138 116 L160 122 L160 54 Z', T.skin.shadow, 0.45, 3);
    if (F.mask) inner += `<path d="M50 ${F.mask} L160 ${F.mask - 6} L160 130 L50 130 Z" fill="${(T[F.maskTone] ?? T.cloth).base}"/><path d="M50 ${F.mask} L160 ${F.mask - 6}" stroke="${(T[F.maskTone] ?? T.cloth).shadow}" stroke-width="2" opacity="0.7"/>`;
    if (F.muzzle) inner += `<ellipse cx="138" cy="114" rx="36" ry="19" fill="${T[F.muzzle].base}"/>`;
    if (F.paint) inner += F.paint;
    if (s.band) inner += bandInner(s.band, T);
    S(headD, T.skin, { sh: 9, hl: 6, inner });
    let e = '';
    if (F.cyclops) e += eye(`e${s.id}c`, 120, ny - 2, 28, 22, E.color ?? '#5a3a20', 1, { ...E, lid: lidC }) + brow(120, ny - 4, 28, 22, 1, s.browColor ?? T.hair.shadow, 5.5);
    else if (!F.noEyes) {
      e += eye(`e${s.id}n`, 103, ny, 20, gob ? 14 : 16, E.color ?? '#5a3a20', 1, { ...E, lid: lidC }) + eye(`e${s.id}f`, 134, ny, 13.5, gob ? 13 : 15, E.color ?? '#5a3a20', -1, { ...E, lid: lidC });
      if (s.brows !== false) e += brow(103, ny, 20, 16, 1, s.browColor ?? (s.beast || gob ? lidC : T.hair.shadow), E.calm ? 3.4 : 5, E.calm) + brow(134, ny, 13.5, 15, -1, s.browColor ?? (s.beast || gob ? lidC : T.hair.shadow), E.calm ? 3 : 4.4, E.calm);
    }
    if (gob) e += `<path d="M110 107 C120 112 132 110 142 103" stroke="#1c2a10" stroke-width="2.4" fill="none" stroke-linecap="round"/><path d="M114 109.5 L118 100 L123 110.5 Z" fill="#fff8e0" stroke="#1c2a10" stroke-width="1"/>`;
    else if (!F.mask && !F.beard && !F.snout && !F.beak && !F.noMouth) {
      e += `<path d="M122 99 L127 101" stroke="${T.skin.shadow}" stroke-width="2" stroke-linecap="round"/>`;
      const mc = F.mouthColor ?? '#5a2a22';
      e += F.mouth === 'smile' ? `<path d="M113 107 C118 111 124 111 129 106" stroke="${mc}" stroke-width="2.2" fill="none" stroke-linecap="round"/>` : F.mouth === 'smirk' ? `<path d="M112 108 C118 110 124 110 130 106" stroke="${mc}" stroke-width="2.4" fill="none" stroke-linecap="round"/>` : `<path d="M113 108.5 L128 107.5" stroke="${mc}" stroke-width="2.4" fill="none" stroke-linecap="round"/>`;
    }
    if (F.fangs) e += `<path d="M110 111 L113.5 100 L117 111 Z M129 109 L132 99 L135.5 109 Z" fill="#fff8e0" stroke="#3a1c1c" stroke-width="1"/>`;
    raw(e);
    if (gob) S('M138 88 C150 86 166 92 174 103 C162 106 148 105 138 100 Z', T.skin, { sh: 4, hl: 3, rim: false });
    if (F.snout) snout(h, F.snout);
    if (F.beak) { S('M134 88 C150 84 170 92 180 104 C166 108 148 110 134 106 Z', T[F.beak] ?? T.gold, { sh: 4, hl: 3 }); raw(`<path d="M138 99 C150 100 164 102 176 104" stroke="#3a2408" stroke-width="1.8" fill="none"/>`); }
    if (F.beard) beard(h, F.beard, F.beardTone);
    for (const [fn, o] of gear) fn(h, o, 'front');
    if (gob) S('M72 80 C56 66 36 58 16 60 C28 76 46 94 70 102 Z', T.skin, { sh: 6, inner: sf('M64 86 C50 76 38 70 26 67', T.skin.shadow, 3, 0.5, 1) });
  });
  if (s.afterHead) G('afterHead', () => { for (const [n, o] of s.afterHead) LIB.neck[n](h, o ?? {}); });
  if (far?.front) G('farFront', () => far.front(h));
  if (near) G('front', () => { near.front?.(h); if (near.pose && near.fist !== false) fist(...POSE[near.pose].hand, near.fistR ?? (s.build === 'heavy' ? 11 : 9.5)); });
  const body = P.body;
  const rig = { swing: ['nearArm', 'front', ...(near?.shoulder ? ['afterBody'] : [])], far: ['farArm', 'farFront'], atk: near?.atk ?? far?.atk ?? 'slash', ...(near?.shoulder ? { top: ['nearArm', 'afterBody', 'front'] } : {}), ...(far?.rig ?? {}), ...(near?.rig ?? {}) };
  return { defs: P.defs, body, glow: glows.join(''), parts: marks.map((k) => ({ name: k.name, svg: body.slice(k.start, k.end) })), rig, spec: s };
}

function bandInner(b, T) {
  const t = T[b.tone] ?? tone(b.tone), y = b.y ?? 62, k = b.k ?? 10;
  return `<path d="M40 ${y + 8} C84 ${y - 4} 122 ${y - 4} 170 ${y + 10} L170 ${y + 10 + k} C122 ${y - 4 + k} 84 ${y - 4 + k} 40 ${y + 8 + k} Z" fill="${t.base}"/><path d="M40 ${y + 8 + k} C84 ${y - 4 + k} 122 ${y - 4 + k} 170 ${y + 10 + k}" stroke="${t.shadow}" stroke-width="1.8" fill="none" opacity="0.8"/>` + (b.gem ? `<circle cx="126" cy="${y + 4}" r="4.5" fill="${b.gem}" stroke="${t.shadow}" stroke-width="1.4"/>` : '');
}
/** Museau d'animal, vers l'avant : longueur, épaisseur, truffe ; « teeth » pour un museau qui montre les crocs. */
function snout(h, o) {
  const L = o.len ?? 30, y = o.y ?? 90, w = o.w ?? 22, t = h.T[o.tone ?? 'skin'], x0 = o.x ?? 128;
  h.S(`M${x0} ${y} C${f(x0 + L * 0.5)} ${f(y - 5)} ${f(x0 + L)} ${f(y)} ${f(x0 + L + 3)} ${f(y + w * 0.45)} C${f(x0 + L)} ${f(y + w * 0.95)} ${f(x0 + L * 0.5)} ${f(y + w * 1.1)} ${x0} ${f(y + w)} Z`, t, { sh: 5, hl: 3, rim: false });
  let e = '';
  if (o.nose !== false) e += `<ellipse cx="${f(x0 + L)}" cy="${f(y + w * 0.32)}" rx="${o.noseR ?? 4.5}" ry="${(o.noseR ?? 4.5) * 0.8}" fill="${o.nose ?? '#1c1218'}"/>`;
  e += `<path d="M${f(x0 + 4)} ${f(y + w * 0.74)} C${f(x0 + L * 0.5)} ${f(y + w * 0.82)} ${f(x0 + L * 0.8)} ${f(y + w * 0.74)} ${f(x0 + L + 1)} ${f(y + w * 0.6)}" stroke="#1c1218" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  if (o.teeth) for (let i = 0; i < o.teeth; i++) { const x = x0 + 8 + i * ((L - 10) / o.teeth); e += `<path d="M${f(x)} ${f(y + w * 0.78)} L${f(x + 3)} ${f(y + w * 0.78 + 7)} L${f(x + 6)} ${f(y + w * 0.77)} Z" fill="#fff8e0" stroke="#1c1218" stroke-width="0.8"/>`; }
  if (o.ring) e += `<path d="M${f(x0 + L - 4)} ${f(y + w * 0.62)} a6 7 0 1 0 8 -1" stroke="${h.T.gold.base}" stroke-width="2.6" fill="none"/>`;
  h.raw(e);
}
function beard(h, kind, toneKey) {
  const t = h.T[toneKey ?? 'hair'];
  const d = {
    full: 'M70 94 C84 104 96 98 106 104 C118 98 136 102 148 92 C152 112 142 136 120 144 C96 144 74 124 70 94 Z',
    long: 'M70 94 C84 104 96 98 106 104 C118 98 136 102 148 92 C150 118 140 150 118 174 C98 150 74 124 70 94 Z',
    fork: 'M70 94 C84 104 96 98 106 104 C118 98 136 102 148 92 C150 116 142 140 134 162 L122 140 L110 166 C92 146 74 124 70 94 Z',
    goat: 'M108 110 C118 114 128 112 136 107 C134 124 126 136 121 142 C114 132 109 121 108 110 Z',
  }[kind];
  h.S(d, t, { sh: 8, inner: kind === 'goat' ? '' : sf('M96 112 C104 118 114 118 124 110', t.shadow, 4, 0.5, 1) });
}
module.exports = { build, LIB, limb, blade, bar, disc, eye, poly, add, unit, perp, ring, ell, saw, arcPts, f, pt, HOOD, HOOD_OPEN, FRINGE, POSE, FARPOSE, tone, metal, mix, ln, sf, blob, bandInner };
