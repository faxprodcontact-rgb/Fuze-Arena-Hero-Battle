// Armes de la main de devant (LIB.near) et objets de la main du fond (LIB.far) pour les 72 héros.
// Tout pointe vers l'adversaire (à droite). Les têtes de hache et de marteau sont en travers du manche.
const K = require('./fig72.cjs');
const { emblem, TK } = require('./lib72.cjs');
const { LIB, limb, blade, bar, disc, poly, add, unit, perp, ring, ell, saw, f, pt, POSE, FARPOSE, tone, metal, ln, sf } = K;

function axeHead(h, c, u, n, s, z, t) {
  const P = (a, b) => add(add(c, u, a), n, b * s);
  h.S(`M${pt(P(-9, 0))} L${pt(P(-25 * z, 27 * z))} Q${pt(P(0, 48 * z))} ${pt(P(25 * z, 27 * z))} L${pt(P(9, 0))} Z`, t, { sh: 6, inner: `<path d="M${pt(P(-21 * z, 28 * z))} Q${pt(P(0, 43 * z))} ${pt(P(21 * z, 28 * z))}" stroke="#fff" stroke-width="2.5" fill="none" opacity="0.55"/>` });
}
function hammerHead(h, c, u, n, L, W, t, band) {
  const P = (a, b) => add(add(c, u, a), n, b);
  h.S(poly([P(W / 2, L / 2), P(-W / 2, L / 2), P(-W / 2, -L / 2), P(W / 2, -L / 2)]), t, { sh: 8, inner: band ? `<path d="M${pt(P(W / 2, L * 0.3))} L${pt(P(-W / 2, L * 0.3))} M${pt(P(W / 2, -L * 0.3))} L${pt(P(-W / 2, -L * 0.3))}" stroke="${band}" stroke-width="6"/>` : '' });
}
function swordAt(h, hand, tip, o) {
  const T = h.T, u = unit(hand, tip), n = perp(u), g = add(hand, u, 13), w = o.w ?? 19, t = TK(h, o.t, 'steel');
  const len = Math.hypot(tip[0] - g[0], tip[1] - g[1]);
  const d = o.curve ? limb([g, add(add(g, u, len * 0.5), n, o.curve), tip], w, 2.5, 16) : blade(g, tip, w, 0.84).d;
  if (o.glow) h.glow(`<path d="${d}" fill="${o.glow}" opacity="0.85" filter="url(#glow)"/>`);
  h.S(bar(add(hand, u, -13), g, 7), T.wood, { sh: 2, hl: 1.5 });
  const mid = `M${pt(add(g, u, 4))} L${pt(add(tip, u, -len * 0.08))}`;
  h.S(d, t, { sh: 5, inner: o.curve ? '' : o.glow ? `<path d="${mid}" stroke="${o.glow}" stroke-width="5" opacity="0.9"/><path d="${mid}" stroke="#fff3c0" stroke-width="1.6"/>` : `<path d="${mid}" stroke="#fff" stroke-width="1.6" opacity="0.6"/>` });
  const gw = o.guard ?? 17; h.S(bar(add(g, n, -gw), add(g, n, gw), 8), TK(h, o.guardT, 'gold'), { sh: 3, hl: 2 });
}
/** Petite arme tenue poing fermé : a = sortie du poing, dir = vers où elle pointe. */
function small(h, kind, a, dir, o) {
  const u = unit([0, 0], dir), n = perp(u), t = TK(h, o.t, 'steel'), P = (x, y) => add(add(a, u, x), n, y);
  if (kind === 'dagger') { const B = blade(a, P(o.len ?? 36, 0), 9, 0.7); h.S(B.d, t, { sh: 3, hl: 2, inner: ln(B.mid, '#fff', 1.2, 0.6) }); h.S(bar(P(0, -8), P(0, 8), 4.5), h.T.gold, { sh: 2, hl: 1.5, rim: false }); }
  if (kind === 'kunai') { h.S(blade(P(2, 0), P(34, 0), 13, 0.45).d, t, { sh: 3, hl: 2 }); }
  if (kind === 'sickle') { h.S(bar(P(-6, 0), P(26, 0), 5.5), h.T.wood, { sh: 2, hl: 1.5 }); h.S(limb([P(24, -3), P(50, -8), P(52, 26)], 11, 2, 12), t, { sh: 3, hl: 2 }); }
  if (kind === 'claw') for (const y of [-7, 0, 7]) h.S(blade(P(2, y), P(30, y * 1.5), 5.5, 0.5).d, t, { sh: 2, hl: 1.5, rim: false });
  if (kind === 'hook') { h.S(bar(P(-4, 0), P(20, 0), 5.5), h.T.wood, { sh: 2, hl: 1.5 }); h.S(limb([P(18, 0), P(44, -4), P(34, 22)], 8, 2, 12), t, { sh: 3, hl: 2 }); }
  if (kind === 'fan') { const p1 = P(40, -22), p2 = P(40, 22); h.S(`M${pt(a)} L${pt(p1)} Q${pt(P(54, 0))} ${pt(p2)} Z`, TK(h, o.t, 'fan'), { sh: 4, inner: `<path d="M${pt(a)} L${pt(P(46, -10))} M${pt(a)} L${pt(P(48, 0))} M${pt(a)} L${pt(P(46, 10))}" stroke="#2a2030" stroke-width="1.6" opacity="0.6"/>` }); }
  if (kind === 'stick') h.S(limb([a, P(18, 0), P(34, 0)], 5, 9), TK(h, o.t, 'wood'), { sh: 2, hl: 1.5 });
  if (kind === 'feather') h.S(limb([a, P(20, -6), P(44, 0)], 14, 3), TK(h, o.t, 'bone'), { sh: 3 });
}

// =================== MAIN DE DEVANT ===================
LIB.near.sword = (o) => ({ pose: 'up', atk: 'slash', front: (h) => swordAt(h, POSE.up.hand, o.tip ?? [194, 34], o) });
LIB.near.axe = (o) => ({ pose: 'up', atk: 'slash', front: (h) => {
  const hand = POSE.up.hand, end = o.end ?? [176, 70], u = unit(hand, end), n = perp(u), c = add(end, u, -12);
  h.S(bar(add(hand, u, -18), end, 8), h.T.wood, { sh: 3, hl: 2 });
  h.S(bar(add(c, u, -11), add(c, u, 11), 13), h.T.iron, { sh: 3, rim: false });
  axeHead(h, c, u, n, 1, o.z ?? 1, TK(h, o.t, 'steel')); if (o.double) axeHead(h, c, u, n, -1, o.z ?? 1, TK(h, o.t, 'steel'));
} });
LIB.near.mace = (o) => ({ pose: 'up', atk: 'smash', front: (h) => {
  const hand = POSE.up.hand, end = o.end ?? [172, 78], u = unit(hand, end), n = perp(u);
  h.S(bar(add(hand, u, -16), end, 8), h.T.wood, { sh: 3, hl: 2 });
  if (o.kind === 'hammer') hammerHead(h, end, u, n, o.L ?? 50, o.W ?? 28, TK(h, o.t, 'steel'), o.band);
  else h.S(disc(end[0], end[1], o.r ?? 17), TK(h, o.t, 'steel'), { sh: 6, inner: o.spikes === false ? '' : `<circle cx="${end[0]}" cy="${end[1]}" r="6" fill="${h.T.gold.base}"/>` });
} });
LIB.near.club = (o) => ({ pose: 'up', atk: 'slash', front: (h) => { const t = TK(h, o.t, 'wood'); h.S(limb([[114, 156], [146, 118], [176, 82]], 9, o.w ?? 30, 14), t, { sh: 6, inner: o.studs ? `<g fill="${h.T.steel.light}" stroke="#2a2030" stroke-width="1"><circle cx="150" cy="106" r="3.4"/><circle cx="164" cy="90" r="3.4"/><circle cx="170" cy="108" r="3.4"/><circle cx="156" cy="122" r="3"/></g>` : `<path d="M150 104 l7 -3 l-1 8 Z M164 92 l7 -2 l-2 8 Z M168 108 l8 0 l-4 6 Z" fill="#fff8e0"/>` }); } });
LIB.near.axeLow = (o) => ({ pose: 'low', atk: 'smash', rig: { wind: -118, hit: 14 }, front: (h) => {
  h.S(bar([98, 126], [176, 208], 9), h.T.wood, { sh: 3, hl: 2 }); h.S(bar([150, 181], [169, 201], 14), h.T.iron, { sh: 4, rim: false });
  h.S('M153 173 C163 167 171 157 176 144 C196 156 205 184 196 212 C189 201 179 196 168 197 Z', TK(h, o.t, 'steel'), { sh: 7, inner: sf('M180 152 C194 164 199 186 195 204', '#fff', 3, 0.6, 1) });
} });
LIB.near.shoulder = (o) => ({ pose: 'shoulder', atk: 'smash', rig: { wind: -18, hit: 125 }, shoulder: (h) => {
  const hand = [116, 150], end = o.end ?? [34, 100], u = unit(hand, end), n = perp(u), t = TK(h, o.t, 'steel'), k = o.kind ?? 'hammer';
  if (k === 'club' || k === 'kanabo') { h.S(limb([hand, [78, 128], [30, 96]], 9, o.w ?? 30, 14), TK(h, o.t, k === 'kanabo' ? 'iron' : 'wood'), { sh: 6, inner: k === 'kanabo' ? `<g fill="${h.T.steel.light}" stroke="#2a2030" stroke-width="1"><circle cx="40" cy="96" r="3.6"/><circle cx="54" cy="112" r="3.6"/><circle cx="46" cy="114" r="3"/><circle cx="62" cy="106" r="3.4"/><circle cx="34" cy="106" r="3"/></g>` : '' }); return; }
  if (k === 'sword') { const g = add(hand, u, 16); h.S(bar(hand, g, 7), h.T.wood, { sh: 2, hl: 1.5 }); h.S(blade(g, o.end ?? [14, 88], o.w ?? 24, 0.86).d, t, { sh: 6 }); h.S(bar(add(g, n, -16), add(g, n, 16), 8), h.T.gold, { sh: 3, hl: 2 }); return; }
  h.S(bar(hand, end, 8), h.T.wood, { sh: 3, hl: 2 });
  if (k === 'hammer') hammerHead(h, end, u, n, o.L ?? 56, o.W ?? 30, t, o.band ?? h.T.gold.base);
  if (k === 'axe') { const c = add(end, u, -10); h.S(bar(add(c, u, -11), add(c, u, 11), 13), h.T.iron, { sh: 3, rim: false }); axeHead(h, c, u, n, -1, o.z ?? 1, t); if (o.double) axeHead(h, c, u, n, 1, o.z ?? 1, t); }
  if (k === 'scythe') h.S(limb([add(end, u, -4), [60, 4], [150, 22]], 16, 2, 18), t, { sh: 5 });
  if (k === 'anchor') { h.S(ring(end[0], end[1] - 14, 9, 9, 4), h.T.iron, { eo: true, sh: 2 }); h.S(limb([[2, 104], [30, 140], [66, 112]], 9, 9, 14), t, { sh: 4 }); h.S('M2 104 L-6 88 L14 96 Z M66 112 L78 98 L58 98 Z', t, { sh: 3 }); }
} });
LIB.near.dagger = (o) => ({ pose: 'fwd', atk: 'stab', rig: { wind: -30, hit: 38 }, front: (h) => small(h, o.kind ?? 'dagger', [117, 163], [33, 13], o) });
LIB.near.gun = (o) => ({ pose: 'fwd', atk: 'shoot', front: (h) => {
  const k = o.kind ?? 'pistol', t = TK(h, o.t, 'iron');
  if (k === 'pistol') { h.S('M98 150 L118 150 L114 174 L100 174 Z', h.T.wood, { sh: 3 }); h.S(bar([106, 153], [160, 147], 10), t, { sh: 3, hl: 2 }); h.S(bar([158, 147], [164, 146.4], 14), h.T.gold, { sh: 2, hl: 1.5 }); }
  if (k === 'lance') { if (o.glow) h.glow(`<circle cx="190" cy="142" r="16" fill="${o.glow}" opacity="0.9" filter="url(#glow)"/>`); h.S(bar([92, 158], [176, 146], 10), t, { sh: 3, hl: 2 }); h.S('M172 134 L196 130 L188 144 L198 156 L174 158 Z', h.T.gold, { sh: 3, hl: 2 }); }
  if (k === 'blow') { h.S(bar([112, 152], [190, 130], 6), h.T.wood, { sh: 2, hl: 1.5 }); h.S('M186 124 L200 122 L194 136 Z', TK(h, o.featherT, 'crest'), { sh: 2 }); }
  if (k === 'crossbow') { h.S(limb([[154, 124], [180, 148], [158, 176]], 7, 7, 14), TK(h, o.bowT, 'wood'), { sh: 3 }); h.raw(`<path d="M154 126 L132 152 L158 174" stroke="#f4efe2" stroke-width="1.8" fill="none"/>`); h.S(bar([98, 158], [170, 148], 9), h.T.wood, { sh: 3, hl: 2 }); h.S('M186 146 L168 139 L169 156 Z', h.T.steel, { sh: 2, rim: false }); }
} });
LIB.near.fist = (o) => ({ pose: 'up', atk: 'smash', rig: { wind: -50, hit: 30 }, fistR: o.r ?? 15 });
LIB.near.grip = () => ({ pose: 'pole', atk: 'stab', rig: { wind: -10, hit: 12, farWind: -8, farHit: 10 } });
LIB.near.chest = () => ({ pose: 'chest' });
LIB.near.pull = () => ({ pose: 'pull', atk: 'shoot' });
LIB.near.small = (o) => ({ pose: 'chest', front: (h) => small(h, o.kind, [119, 143], o.dir ?? [30, -20], o) });

// =================== MAIN DU FOND ===================
LIB.far.shield = (o) => ({ front: (h) => {
  const t = TK(h, o.t, 'steel'), face = TK(h, o.face, 'shieldFace'), k = o.kind ?? 'kite', em = o.emblem ? emblem(o.emblem, 160, k === 'kite' ? 158 : 166, o.es ?? 1.25, o.ec ?? h.T.gold.light) : '';
  if (k === 'kite') h.S('M130 110 C150 118 172 118 190 108 C194 150 186 192 160 220 C136 196 126 154 130 110 Z', t, { sh: 8, inner: `<path d="M138 120 C152 126 168 126 182 120 C184 152 178 184 160 206 C144 186 136 152 138 120 Z" fill="${face.base}"/><path d="M160 122 C168 124 176 123 182 120 C184 152 178 184 160 206 Z" fill="${face.shadow}" opacity="0.5"/>` + em });
  if (k === 'round') h.S(disc(160, 166, o.r ?? 36), t, { sh: 8, inner: `<circle cx="160" cy="166" r="${(o.r ?? 36) - 8}" fill="${face.base}"/><path d="M160 ${166 - (o.r ?? 36) + 8} A${(o.r ?? 36) - 8} ${(o.r ?? 36) - 8} 0 0 1 160 ${166 + (o.r ?? 36) - 8} Z" fill="${face.shadow}" opacity="0.45"/>` + (em || `<circle cx="160" cy="166" r="7" fill="${t.light}" stroke="${t.shadow}" stroke-width="2"/>`) });
  if (k === 'tower') h.S('M134 104 C150 100 174 100 190 104 L192 206 C176 214 148 214 132 206 Z', t, { sh: 8, inner: `<path d="M142 112 C154 109 170 109 182 112 L184 200 C172 205 152 205 140 200 Z" fill="${face.base}"/><path d="M162 110 L184 112 L184 200 L162 204 Z" fill="${face.shadow}" opacity="0.45"/>` + (o.inner ?? '') + em });
  if (k === 'shell') h.S(ell(160, 166, 34, 40), t, { sh: 8, inner: `<path d="M160 128 L160 204 M128 152 L192 152 M130 180 L190 180" stroke="${t.shadow}" stroke-width="3" opacity="0.7"/><path d="M146 152 L160 140 L174 152 L174 180 L160 192 L146 180 Z" fill="${face.base}" opacity="0.7"/>` });
} });
const TOP = {
  orb: (h, x, y, o) => { const c = o.color ?? '#6fd0ff'; h.glow(`<circle cx="${x}" cy="${y - 2}" r="19" fill="${c}" opacity="0.8" filter="url(#glow)"/>`); h.S(`M${x - 18} ${y - 4} C${x - 18} ${y + 12} ${x - 10} ${y + 20} ${x} ${y + 20} C${x + 10} ${y + 20} ${x + 18} ${y + 12} ${x + 18} ${y - 4} C${x + 14} ${y + 6} ${x + 8} ${y + 10} ${x} ${y + 10} C${x - 8} ${y + 10} ${x - 14} ${y + 6} ${x - 18} ${y - 4} Z`, h.T.gold, { sh: 3, hl: 2 }); h.S(disc(x, y - 4, 11), tone(c), { sh: 4, hl: 3, inner: `<circle cx="${x - 4}" cy="${y - 8}" r="4" fill="#fff" opacity="0.85"/>` }); },
  sun: (h, x, y, o) => { const c = o.color ?? '#ffcf5a'; let r = ''; for (let i = 0; i < 8; i++) { const a = i * 45 * Math.PI / 180; r += `M${f(x + Math.cos(a - 0.22) * 12)} ${f(y + Math.sin(a - 0.22) * 12)} L${f(x + Math.cos(a) * 24)} ${f(y + Math.sin(a) * 24)} L${f(x + Math.cos(a + 0.22) * 12)} ${f(y + Math.sin(a + 0.22) * 12)} Z `; } h.glow(`<circle cx="${x}" cy="${y}" r="24" fill="${c}" opacity="0.8" filter="url(#glow)"/>`); h.S(r, h.T.gold, { sh: 2, hl: 1.5 }); h.S(disc(x, y, 13), h.T.gold, { sh: 4 }); },
  crook: (h, x, y, o) => h.S(limb([[x, y + 30], [x - 2, y - 22], [x + 24, y + 6]], 7, 5, 14), TK(h, o.topT, 'gold'), { sh: 3, hl: 2 }),
  skull: (h, x, y, o) => { if (o.color) h.glow(`<circle cx="${x}" cy="${y + 6}" r="19" fill="${o.color}" opacity="0.8" filter="url(#glow)"/>`); h.S(`M${x - 14} ${y + 6} C${x - 14} ${y - 6} ${x - 8} ${y - 12} ${x} ${y - 12} C${x + 8} ${y - 12} ${x + 14} ${y - 6} ${x + 14} ${y + 6} C${x + 14} ${y + 14} ${x + 10} ${y + 20} ${x + 8} ${y + 24} L${x - 8} ${y + 24} C${x - 10} ${y + 20} ${x - 14} ${y + 14} ${x - 14} ${y + 6} Z`, h.T.bone, { sh: 4, inner: `<ellipse cx="${x - 5}" cy="${y + 6}" rx="3.6" ry="4.4" fill="#2a1a30"/><ellipse cx="${x + 6}" cy="${y + 6}" rx="3.6" ry="4.4" fill="#2a1a30"/>` }); },
  lantern: (h, x, y, o) => { const c = o.color ?? '#ffd76a'; h.glow(`<circle cx="${x + 18}" cy="${y + 34}" r="18" fill="${c}" opacity="0.85" filter="url(#glow)"/>`); h.S(limb([[x, y + 20], [x + 4, y + 2], [x + 20, y + 10]], 6, 5, 12), h.T.wood, { sh: 2 }); h.S(`M${x + 9} ${y + 20} L${x + 29} ${y + 20} L${x + 31} ${y + 46} L${x + 7} ${y + 46} Z`, h.T.iron, { sh: 3, inner: `<rect x="${x + 12}" y="${y + 25}" width="14" height="16" fill="${c}"/>` }); },
  flower: (h, x, y, o) => { const t = tone(o.color ?? '#ff8ab0'); for (const r of [-50, -18, 18, 50]) h.at(`translate(${x} ${y + 12}) rotate(${r})`, () => h.S('M0 2 C-9 -8 -7 -22 0 -30 C7 -22 9 -8 0 2 Z', t, { sh: 3, hl: 2 })); h.S(disc(x, y + 10, 6), h.T.gold, { sh: 2, rim: false }); },
  moon: (h, x, y, o) => { const c = o.color ?? '#cfe6ff'; h.glow(`<circle cx="${x}" cy="${y}" r="20" fill="${c}" opacity="0.8" filter="url(#glow)"/>`); h.S(`M${x + 6} ${y - 20} C${x - 16} ${y - 18} ${x - 20} ${y + 14} ${x + 4} ${y + 20} C${x - 6} ${y + 10} ${x - 6} ${y - 8} ${x + 6} ${y - 20} Z`, TK(h, o.t, 'steel'), { sh: 3, hl: 2 }); },
  ankh: (h, x, y) => { h.S(ring(x, y - 4, 10, 13, 5), h.T.gold, { eo: true, sh: 2, hl: 1.5 }); h.S(bar([x - 15, y + 14], [x + 15, y + 14], 6), h.T.gold, { sh: 2, hl: 1.5 }); },
  flame: (h, x, y, o) => { const t = tone(o.color ?? '#ff8a2a'); h.glow(`<circle cx="${x}" cy="${y}" r="22" fill="${t.base}" opacity="0.85" filter="url(#glow)"/>`); h.S(`M${x - 13} ${y + 14} L${x + 13} ${y + 14} L${x + 8} ${y + 24} L${x - 8} ${y + 24} Z`, h.T.iron, { sh: 2 }); h.S(`M${x - 10} ${y + 14} C${x - 16} ${y} ${x - 8} ${y - 8} ${x - 6} ${y - 22} C${x + 2} ${y - 12} ${x + 4} ${y - 6} ${x + 2} ${y - 2} C${x + 8} ${y - 6} ${x + 8} ${y - 14} ${x + 8} ${y - 18} C${x + 16} ${y - 6} ${x + 16} ${y + 6} ${x + 10} ${y + 14} Z`, t, { sh: 3, inner: `<ellipse cx="${x}" cy="${y + 6}" rx="5" ry="8" fill="#ffe27a"/>` }); },
  crystal: (h, x, y, o) => { const c = o.color ?? '#9fe8ff'; h.glow(`<circle cx="${x}" cy="${y}" r="20" fill="${c}" opacity="0.8" filter="url(#glow)"/>`); h.S(`M${x} ${y - 24} L${x + 12} ${y - 2} L${x} ${y + 20} L${x - 12} ${y - 2} Z`, tone(c), { sh: 3, hl: 3, inner: `<path d="M${x} ${y - 24} L${x} ${y + 20}" stroke="#fff" stroke-width="2" opacity="0.6"/>` }); },
  snake: (h, x, y, o) => { const t = TK(h, o.t, 'tail'); h.S(limb([[x - 6, y + 70], [x + 22, y + 44], [x - 4, y + 22]], 7, 7, 12), t, { sh: 2 }); h.S(limb([[x - 4, y + 24], [x - 22, y + 4], [x + 6, y - 6]], 7, 8, 12), t, { sh: 2 }); h.S(`M${x + 2} ${y - 14} L${x + 24} ${y - 6} L${x + 4} ${y + 2} Z`, t, { sh: 2 }); },
  branch: (h, x, y, o) => { h.S(limb([[x, y + 24], [x - 4, y], [x + 16, y - 16]], 7, 4, 10), h.T.wood, { sh: 2 }); h.S(limb([[x - 1, y + 10], [x - 16, y], [x - 20, y - 14]], 5, 3, 10), h.T.wood, { sh: 2 }); const t = tone(o.color ?? '#5fb84a'); for (const [a, b, r] of [[x + 18, y - 18, 40], [x - 22, y - 16, -30], [x + 4, y - 8, 0]]) h.at(`translate(${a} ${b}) rotate(${r})`, () => h.S('M0 4 C-7 -4 -6 -14 0 -20 C6 -14 7 -4 0 4 Z', t, { sh: 2, hl: 2 })); },
  fork: (h, x, y) => { h.S(blade([x - 8, y + 26], [x - 10, y - 20], 7, 0.6).d, h.T.steel, { sh: 2 }); h.S(blade([x + 8, y + 26], [x + 10, y - 20], 7, 0.6).d, h.T.steel, { sh: 2 }); h.S(bar([x - 13, y + 26], [x + 13, y + 26], 7), h.T.steel, { sh: 2 }); },
  feather: (h, x, y, o) => { for (const [r, c] of [[-28, o.c1 ?? '#e0483a'], [0, o.c2 ?? '#f0b23a'], [28, o.c3 ?? '#2fa37a']]) h.at(`translate(${x} ${y + 20}) rotate(${r})`, () => h.S('M0 0 C-8 -12 -6 -30 0 -40 C6 -30 8 -12 0 0 Z', tone(c), { sh: 3, hl: 2 })); },
};
LIB.far.staff = (o) => ({ pose: 'staff', atk: 'cast', rig: { glow: 'far', fx: o.color }, front: (h) => {
  const x = 164, top = o.top ?? 34; h.S(bar([x, top + 18], [x, 228], 7), TK(h, o.t, 'wood'), { sh: 3, hl: 2 });
  TOP[o.kind ?? 'orb'](h, x, top, o); h.fist(x, 146, 9);
} });
LIB.far.bow = (o) => ({ pose: 'fwd', atk: 'shoot', front: (h) => {
  const x = 162, top = o.top ?? 60, bot = o.bot ?? 198, pull = [120, 128], t = TK(h, o.t, 'bow');
  if (o.glow) h.glow(`<path d="M120 128 L${x + 40} 129" stroke="${o.glow}" stroke-width="12" opacity="0.8" filter="url(#glow)"/>`);
  h.raw(`<path d="M${x} ${top + 2} L${pull[0]} ${pull[1]} L${x} ${bot - 2}" stroke="#f4efe2" stroke-width="1.8" fill="none" stroke-linejoin="round"/>`);
  h.S(limb([[x, top], [o.bulge ?? 200, (top + bot) / 2], [x, bot]], 7.5, 7.5, 18), t, { sh: 3, hl: 2 });
  h.S(bar([pull[0] - 2, pull[1]], [x + 20, pull[1] + 1], 4), o.glow ? tone(o.glow) : h.T.wood, { sh: 2, hl: 1, rim: false });
  h.S(`M${x + 37} ${pull[1] + 1} L${x + 19} ${pull[1] - 8} L${x + 19} ${pull[1] + 10} Z`, o.glow ? tone(o.glow) : h.T.steel, { sh: 2, hl: 1.5, rim: false });
  h.fist(178, 129, 9);
} });
function poleDraw(h, butt, end, o) {
  const u = unit(butt, end), n = perp(u), t = TK(h, o.t, 'steel'), k = o.kind ?? 'spear', P = (a, b) => add(add(end, u, a), n, b);
  if (o.glow) h.glow(`<circle cx="${f(P(18, 0)[0])}" cy="${f(P(18, 0)[1])}" r="20" fill="${o.glow}" opacity="0.8" filter="url(#glow)"/>`);
  h.S(bar(butt, end, o.thick ?? 6.5), TK(h, o.shaft, 'wood'), { sh: 3, hl: 2 });
  if (k === 'spear') h.S(blade(P(-2, 0), P(32, 0), 15, 0.45).d, t, { sh: 3, hl: 2 });
  if (k === 'harpoon') { h.S(blade(P(-2, 0), P(32, 0), 11, 0.5).d, t, { sh: 3, hl: 2 }); h.S(poly([P(10, 4), P(2, 16), P(18, 5)]), t, { sh: 2 }); }
  if (k === 'trident' || k === 'bident') { h.S(bar(P(0, -13), P(0, 13), 6), t, { sh: 2, hl: 1.5 }); if (k === 'trident') h.S(blade(P(0, 0), P(34, 0), 9, 0.6).d, t, { sh: 2, hl: 2 }); for (const s of [-1, 1]) h.S(limb([P(0, 11 * s), P(10, 17 * s), P(28, 13 * s)], 6.5, 2, 10), t, { sh: 2, hl: 2 }); }
  if (k === 'naginata') h.S(limb([P(-2, 0), P(22, 10), P(44, -10)], 14, 2, 14), t, { sh: 3, hl: 2 });
  if (k === 'halberd') { axeHead(h, P(4, 0), u, n, 1, 0.7, t); h.S(blade(P(8, 0), P(34, 0), 9, 0.5).d, t, { sh: 2 }); }
  if (k === 'staff') { h.S(bar(P(-14, 0), P(6, 0), 10), TK(h, o.t, 'gold'), { sh: 2, hl: 2 }); const b = add(butt, u, 0); h.S(bar(b, add(b, u, 18), 10), TK(h, o.t, 'gold'), { sh: 2, hl: 2 }); }
}
LIB.far.pole = (o) => ({ pose: 'pole', atk: 'stab', front: (h) => { poleDraw(h, o.butt ?? [56, 186], o.end ?? [176, 114], o); h.fist(152, 129, 9); } });
LIB.near.spear = (o) => ({ pose: 'up', atk: 'stab', rig: { wind: -14, hit: 16 }, front: (h) => poleDraw(h, o.butt ?? [84, 182], o.end ?? [176, 98], o) });
LIB.far.pincer = (o) => ({ pose: 'stab', front: (h) => { const t = TK(h, o.t, 'cloth'); h.S(limb([[164, 132], [186, 154], [202, 134]], 14, 4, 12), t, { sh: 4 }); h.S(limb([[162, 126], [186, 96], [204, 126]], 20, 4, 12), t, { sh: 5 }); h.S(disc(164, 128, 12), t, { sh: 4 }); } });
LIB.far.dagger = (o) => ({ pose: 'stab', fistBehind: true, rig: { farWind: -25, farHit: 55 }, behind: (h) => small(h, o.kind ?? 'dagger', [170, 122], [28, -30], o) });
LIB.far.fist = (o) => ({ pose: 'stab', front: (h) => h.fist(170, 126, o.r ?? 14) });
LIB.far.bolt = (o) => ({ pose: 'up', atk: 'cast', rig: { glow: 'far', fx: o.color ?? '#ffe14a' }, front: (h) => {
  const c = o.color ?? '#ffe14a'; h.glow(`<path d="M150 130 L196 44" stroke="${c}" stroke-width="20" opacity="0.8" filter="url(#glow)"/>`);
  h.S('M154 132 L172 100 L162 98 L182 66 L200 40 L190 78 L200 80 L176 112 L184 114 Z', tone(c), { sh: 3, hl: 3 }); h.fist(170, 99, 9);
} });
const HOLD = {
  torch: (h, o) => { const t = tone(o.color ?? '#ff8a2a'); h.glow(`<circle cx="168" cy="100" r="22" fill="${t.base}" opacity="0.85" filter="url(#glow)"/>`); h.S(bar([163, 164], [167, 120], 7), h.T.wood, { sh: 2 }); h.S('M158 122 C150 108 158 98 160 84 C166 94 170 98 168 104 C174 100 176 92 176 86 C184 98 184 112 176 122 Z', t, { sh: 3, inner: `<ellipse cx="167" cy="112" rx="5" ry="8" fill="#ffe27a"/>` }); },
  jar: (h, o) => { const t = TK(h, o.t, 'jar'); h.S('M152 150 C144 166 150 184 164 188 C178 184 184 166 176 150 L172 138 L156 138 Z', t, { sh: 5, inner: `<path d="M148 164 C158 170 170 170 180 164" stroke="${t.light}" stroke-width="3" fill="none" opacity="0.7"/>` }); if (o.water) { h.raw(`<path d="M176 140 C190 144 194 170 192 212" stroke="${o.water}" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.85"/>`); } },
  mirror: (h, o) => { const c = o.color ?? '#dff4ff'; h.glow(`<circle cx="168" cy="116" r="22" fill="${c}" opacity="0.8" filter="url(#glow)"/>`); h.S(bar([164, 160], [167, 134], 6), h.T.gold, { sh: 2 }); h.S(disc(168, 116, 19), h.T.gold, { sh: 4, inner: `<circle cx="168" cy="116" r="13" fill="${c}"/><path d="M160 110 L170 106" stroke="#fff" stroke-width="3" stroke-linecap="round"/>` }); },
  fan: (h, o) => small(h, 'fan', [166, 142], [10, -30], o),
  book: (h, o) => { const t = TK(h, o.t, 'book'); h.S('M142 136 L166 130 L190 134 L190 158 L166 154 L142 160 Z', t, { sh: 4, inner: `<path d="M146 140 L164 135 L164 151 L146 156 Z M168 135 L186 138 L186 154 L168 151 Z" fill="#f6efd8"/>` }); },
  horn: (h, o) => h.S(limb([[160, 150], [186, 152], [196, 118]], 8, 22, 14), TK(h, o.t, 'bone'), { sh: 4, inner: `<path d="M186 122 L206 116" stroke="${h.T.gold.base}" stroke-width="4"/>` }),
  lyre: (h, o) => { const t = TK(h, o.t, 'gold'); h.raw(`<path d="M160 104 L160 146 M166 102 L166 146 M172 104 L172 146" stroke="#f4efe2" stroke-width="1.4"/>`); h.S('M148 150 C142 124 146 106 156 94 L162 100 C154 110 152 126 156 142 L176 142 C180 126 178 110 170 100 L176 94 C186 106 190 124 184 150 Z', t, { sh: 3, hl: 2 }); },
  bowl: (h, o) => { const t = tone(o.color ?? '#ff8a2a'); h.glow(`<circle cx="166" cy="122" r="20" fill="${t.base}" opacity="0.85" filter="url(#glow)"/>`); h.S('M158 134 C152 122 158 114 160 102 C166 110 168 114 167 118 C172 114 173 108 173 104 C180 114 180 126 174 134 Z', t, { sh: 3, inner: `<ellipse cx="166" cy="126" rx="4" ry="6" fill="#ffe27a"/>` }); h.S('M148 134 L184 134 C182 148 174 154 166 154 C158 154 150 148 148 134 Z', h.T.gold, { sh: 3, hl: 2 }); },
  orb: (h, o) => { const c = o.color ?? '#6fd0ff'; h.glow(`<circle cx="168" cy="118" r="22" fill="${c}" opacity="0.85" filter="url(#glow)"/>`); h.S(disc(168, 118, o.r ?? 14), tone(c), { sh: 4, hl: 3, inner: `<circle cx="163" cy="113" r="5" fill="#fff" opacity="0.85"/>` }); },
  skull: (h, o) => TOP.skull(h, 168, 112, o),
  flower: (h, o) => TOP.flower(h, 166, 118, o),
  stick: (h, o) => small(h, 'stick', [166, 140], [16, -30], o),
  feather: (h, o) => small(h, 'feather', [166, 140], [20, -30], o),
};
LIB.far.hold = (o) => ({ pose: 'staff', atk: 'cast', rig: { glow: 'far', fx: o.color }, front: (h) => { HOLD[o.kind](h, o); if (o.kind !== 'orb' && o.kind !== 'skull') h.fist(164, 146, 9); else h.fist(166, 144, 9); } });
module.exports = { axeHead, hammerHead, swordAt, small, TOP, HOLD };
