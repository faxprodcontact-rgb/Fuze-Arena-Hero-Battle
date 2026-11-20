// Bibliothèque de pièces pour les 72 héros : dos, jambes, cou, coiffes, armes (main de devant), objets (main du fond).
// Règles : une pièce = une forme simple ; les pics (cheveux, flammes, fourrure) sont tous couchés vers l'arrière ;
// les armes pointent vers l'adversaire (à droite) ; une tête de marteau ou de hache est en travers du manche.
const K = require('./fig72.cjs');
const { LIB, limb, blade, bar, disc, poly, add, unit, perp, ring, ell, saw, arcPts, f, pt, HOOD, FRINGE, POSE, FARPOSE, tone, metal, mix, ln, sf, blob, bandInner } = K;
const TK = (h, k, d) => (k ? (h.T[k] ?? tone(k)) : h.T[d]);

/** Petit emblème (dans une forme) : flamme, goutte, tourbillon, feuille, éclair, soleil, lune, crâne. */
function emblem(kind, x, y, k, col, line = '#3a2408') {
  const d = {
    flame: 'M0 -14 C8 -6 12 2 8 10 C6 14 -6 14 -8 10 C-12 2 -6 -2 -4 -8 C-2 -4 0 -4 0 -14 Z',
    drop: 'M0 -14 C8 -2 10 4 8 9 C5 15 -5 15 -8 9 C-10 4 -8 -2 0 -14 Z',
    swirl: 'M-10 2 C-10 -10 8 -12 10 0 C11 8 0 10 -2 4 C-3 0 2 -2 4 1 M-10 2 C-8 12 6 14 12 8',
    leaf: 'M-10 10 C-12 -4 0 -14 12 -12 C12 0 4 12 -10 10 Z M-8 8 L8 -8',
    bolt: 'M4 -14 L-8 2 L0 2 L-4 14 L10 -4 L1 -4 Z',
    sun: 'M0 -7 A7 7 0 1 0 0.1 -7 Z M0 -14 L0 -10 M0 10 L0 14 M-14 0 L-10 0 M10 0 L14 0 M-10 -10 L-7 -7 M7 7 L10 10 M-10 10 L-7 7 M7 -7 L10 -10',
    moon: 'M4 -12 C-8 -10 -10 8 4 12 C-2 6 -2 -6 4 -12 Z',
    skull: 'M-8 -2 C-8 -12 8 -12 8 -2 C8 4 5 6 5 10 L-5 10 C-5 6 -8 4 -8 -2 Z',
    star: 'M0 -12 L3 -4 L12 -4 L5 2 L8 11 L0 6 L-8 11 L-5 2 L-12 -4 L-3 -4 Z',
  }[kind];
  const stroke = kind === 'swirl' || kind === 'sun';
  return `<g transform="translate(${x} ${y}) scale(${k})"><path d="${d}" fill="${stroke ? 'none' : col}" stroke="${stroke ? col : line}" stroke-width="${stroke ? 3 : 1.4}" stroke-linejoin="round" stroke-linecap="round"/></g>`;
}

// =================== JAMBES ===================
LIB.legs.normal = (h) => {
  const { S, T } = h, hoof = h.s.hoof;
  S(limb([[88, 166], [80, 190], [76, hoof ? 216 : 212]], 25, hoof ? 17 : 21), T.pants, { sh: 6 });
  S(limb([[126, 166], [140, 188], [148, hoof ? 216 : 212]], 25, hoof ? 17 : 21), T.pants, { sh: 6 });
  if (hoof) { S('M64 214 L88 214 L92 228 L60 228 Z', T.boot, { sh: 4 }); S('M138 214 L160 214 L166 228 L134 228 Z', T.boot, { sh: 4 }); return; }
  const cuff = (x) => `<path d="M${x} 207 L${x + 34} 207" stroke="${T.boot.light}" stroke-width="3" opacity="0.6"/>`;
  S('M62 204 L91 204 L93 215 L105 221 C110 224 109 228 104 228 L62 228 C58 228 58 224 60 220 Z', T.boot, { sh: 5, inner: cuff(60) });
  S('M134 204 L163 204 L165 215 L178 221 C183 224 182 228 177 228 L134 228 C130 228 130 224 132 220 Z', T.boot, { sh: 5, inner: cuff(132) });
};
LIB.legs.tail = (h) => { // queue de poisson, nageoire vers l'arrière
  const { S, T } = h;
  S('M96 214 C78 198 58 196 38 180 C46 200 44 216 30 232 C56 226 82 232 104 230 Z', T.fin ?? T.tail, { sh: 5 });
  S(limb([[106, 164], [156, 200], [100, 220]], 48, 18, 16), T.tail, { sh: 8, inner: sf('M92 180 C112 200 132 204 140 196', T.tail.light, 3, 0.5, 1) });
};
LIB.legs.naga = (h) => { // corps de serpent enroulé
  const { S, T } = h;
  S(limb([[120, 218], [70, 234], [36, 204]], 26, 5), T.tail, { sh: 6 });
  S(limb([[106, 164], [164, 196], [116, 220]], 46, 26, 16), T.tail, { sh: 8, inner: `<path d="M96 176 C118 196 138 202 150 198" stroke="${(T.belly ?? T.tail).light}" stroke-width="9" fill="none" opacity="0.55"/>` });
};
LIB.legs.smoke = (h) => { // pas de jambes : une volute (djinn)
  const { S, T } = h;
  h.glow(`<ellipse cx="96" cy="208" rx="40" ry="16" fill="${T.smoke.base}" opacity="0.5" filter="url(#glow)"/>`);
  S(limb([[106, 164], [140, 204], [78, 226]], 48, 4, 16), T.smoke, { sh: 8, inner: sf('M96 178 C112 200 110 214 92 222', T.smoke.light, 4, 0.5, 2) });
};
LIB.legs.tentacles = (h) => {
  const { S, T } = h;
  for (const [a, c, b] of [[[90, 168], [52, 186], [34, 224]], [[122, 168], [162, 186], [184, 222]], [[100, 170], [84, 206], [62, 230]], [[114, 170], [132, 208], [154, 230]]]) S(limb([a, c, b], 22, 4), T.tail, { sh: 5 });
  S(limb([[106, 168], [112, 204], [104, 230]], 22, 5), T.tail, { sh: 5 });
};

// =================== COU / ÉPAULES ===================
LIB.neck.scarf = (h, o) => h.S('M74 114 C92 126 122 126 140 112 L142 126 C122 140 92 140 72 128 Z', TK(h, o.t, 'scarf'), { sh: 5 });
LIB.neck.mask = (h, o) => h.S('M72 108 C92 122 124 122 146 106 L148 124 C124 140 92 140 70 126 Z', TK(h, o.t, 'scarf'), { sh: 5 });
LIB.neck.pad = (h, o) => { h.S('M62 124 C66 108 90 104 104 118 C104 132 94 140 80 142 C70 140 64 132 62 124 Z', TK(h, o.t, 'steel'), { sh: 6 }); if (o.spike) h.S('M70 114 L66 92 L84 108 Z', TK(h, o.spikeT, 'bone'), { sh: 3 }); };
LIB.neck.fur = (h, o) => h.S('M64 120 C84 108 128 108 148 118 L153 136 L143 130 L137 138 L128 130 L120 140 L110 131 L101 140 L93 131 L85 139 L78 130 L66 136 Z', TK(h, o.t, 'fur'), { sh: 6 });
LIB.neck.beads = (h, o) => { const t = TK(h, o.t, 'gold'); for (let i = 0; i < 7; i++) { const u = i / 6, x = 78 + u * 58, y = 124 + Math.sin(u * Math.PI) * 12; h.S(disc(x, y, 4.6), t, { sh: 2, hl: 1.5, rim: false }); } };
LIB.neck.collar = (h, o) => h.S('M70 116 C90 126 124 126 144 114 L150 130 C126 142 90 142 66 130 Z', TK(h, o.t, 'gold'), { sh: 5, inner: o.gem ? `<circle cx="110" cy="130" r="5" fill="${o.gem}"/>` : '' });

// =================== DOS ===================
const CAPES = {
  long: 'M88 116 C64 128 46 168 40 216 C60 220 86 212 104 196 L104 122 Z',
  short: 'M86 118 C66 130 54 156 50 186 C68 182 86 172 98 156 Z',
  torn: 'M88 116 C64 128 46 168 36 214 L50 202 L56 220 L68 204 L76 222 L88 202 L98 214 L104 194 L104 122 Z',
  wide: 'M84 116 C52 126 34 168 26 218 C50 224 84 216 104 198 L104 122 Z',
};
LIB.back.cape = (h, o) => h.S(CAPES[o.len ?? 'long'], TK(h, o.t, 'cape'), { sh: 9, far: o.far, inner: o.inner ?? '' });
LIB.back.scarf = (h, o) => h.S('M94 120 C72 110 46 114 20 132 C42 136 58 140 70 146 C60 154 52 166 48 180 C70 170 88 154 100 134 Z', TK(h, o.t, 'scarf'), { sh: 7 });
LIB.back.scarf2 = (h, o) => h.S('M98 120 C72 102 44 98 10 108 C32 116 50 124 62 132 C44 136 28 148 18 164 C46 160 76 150 102 134 Z', TK(h, o.t, 'scarf'), { sh: 7 });
LIB.back.hair = (h, o) => h.S('M68 70 C56 100 50 140 46 178 C44 196 38 208 28 216 C48 218 68 208 80 192 C90 174 94 150 94 124 L142 120 C148 108 150 94 150 82 Z', TK(h, o.t, 'hair'), { sh: 10, inner: sf('M72 104 C68 144 60 184 42 212', TK(h, o.t, 'hair').shadow, 6, 0.45, 3) });
LIB.back.pony = (h, o) => h.S(limb([[76, 66], [30, 60], [30, 116]], 24, 5), TK(h, o.t, 'hair'), { sh: 6 });
LIB.back.braid = (h, o) => { const t = TK(h, o.t, 'hair'); h.S(limb([[76, 92], [52, 134], [62, 180]], 16, 8), t, { sh: 5, inner: `<path d="M66 108 l10 6 M60 124 l11 5 M57 140 l11 4 M57 156 l10 3" stroke="${t.shadow}" stroke-width="2" opacity="0.8"/>` }); };
const WINGS = {
  feather: ['M92 126 C72 104 48 76 22 44 C26 68 30 84 38 98 C26 94 16 96 8 92 C18 110 30 122 44 132 C34 134 26 138 20 142 C40 152 66 152 92 142 Z', 'M122 124 C140 102 160 78 184 48 C182 70 178 86 172 98 C182 94 190 96 196 94 C188 110 178 122 164 130 C150 136 136 136 122 132 Z'],
  bat: ['M92 124 C70 100 44 82 10 72 C22 88 26 100 26 114 C36 108 46 110 52 122 C58 112 68 114 74 126 C80 120 88 124 92 134 Z', 'M122 122 C142 100 166 84 198 76 C188 90 184 102 184 114 C174 108 164 110 158 122 C152 114 144 116 140 126 C134 122 126 124 122 132 Z'],
  small: ['M90 128 C74 116 58 100 46 82 C48 98 50 108 54 116 C46 114 40 116 36 114 C44 128 56 138 70 142 C78 142 86 138 90 136 Z', 'M124 126 C138 114 152 100 164 84 C162 98 160 108 156 116 C164 114 168 116 172 116 C164 128 152 136 140 138 C134 138 128 134 124 132 Z'],
};
LIB.back.wings = (h, o) => {
  const t = TK(h, o.t, 'wing'), W = WINGS[o.kind ?? 'feather'];
  if (o.glow) h.glow(`<path d="${W[0]}" fill="${o.glow}" opacity="0.7" filter="url(#glow)"/><path d="${W[1]}" fill="${o.glow}" opacity="0.5" filter="url(#glow)"/>`);
  const lines = o.kind === 'bat' ? `<path d="M90 126 L28 112 M90 126 L52 120 M90 126 L74 124" stroke="${t.shadow}" stroke-width="2.5" opacity="0.6"/>` : sf('M86 130 C66 112 46 92 30 66', t.shadow, 4, 0.35, 1) + sf('M82 138 C62 130 42 122 24 108', t.shadow, 3, 0.3, 1);
  h.S(W[1], t, { sh: 7, far: true });
  h.S(W[0], t, { sh: 8, inner: lines });
};
LIB.back.fairy = (h, o) => { const c = o.color ?? '#bfefff'; h.raw(`<g opacity="0.8"><path d="M92 126 C60 96 30 80 14 58 C10 86 40 124 92 138 Z" fill="${c}" stroke="#2c1626" stroke-width="2"/><path d="M92 136 C64 138 40 152 30 172 C54 172 78 160 94 144 Z" fill="${c}" stroke="#2c1626" stroke-width="2"/><path d="M90 128 C64 106 40 90 22 70" stroke="#fff" stroke-width="2" fill="none" opacity="0.7"/></g>`); };
LIB.back.tail = (h, o) => {
  const t = TK(h, o.t, 'tail'), k = o.kind ?? 'lizard';
  if (k === 'lizard') h.S(limb([[84, 176], [38, 184], [22, 226]], 22, 3), t, { sh: 5 });
  if (k === 'monkey') h.S(limb([[84, 178], [40, 196], [34, 146]], 9, 7), t, { sh: 3 });
  if (k === 'devil') { h.S(limb([[84, 178], [40, 200], [30, 150]], 7, 4), t, { sh: 3 }); h.S('M30 152 L18 134 L40 136 Z', t, { sh: 2 }); }
  if (k === 'fox') { const n = o.n ?? 1; for (let i = n - 1; i >= 0; i--) h.at(`rotate(${-(i - (n - 1) / 2) * 26 - (n > 1 ? 18 : 0)} 86 178)`, () => h.S('M88 176 C60 166 30 172 12 198 C8 214 18 226 30 224 C26 210 40 200 60 196 C74 194 84 190 90 184 Z', t, { sh: 6, inner: `<path d="M12 198 C8 214 18 226 30 224 C26 212 34 204 44 200 C34 196 22 196 12 198 Z" fill="${(h.T.tip ?? tone('#fff6e6')).base}"/>` })); }
  if (k === 'scorpion') { h.S(limb([[86, 174], [26, 172], [26, 104]], 17, 13), t, { sh: 5 }); h.S(limb([[26, 108], [28, 44], [82, 26]], 13, 8), t, { sh: 4 }); h.S('M78 16 L112 34 L80 36 Z', TK(h, o.tipT, 'bone'), { sh: 3 }); }
};
LIB.back.shell = (h, o) => { const t = TK(h, o.t, 'shell'); h.S(ell(84, 152, 40, 44), t, { sh: 9, inner: `<path d="M84 110 L84 194 M48 140 L120 140 M50 166 L118 166" stroke="${t.shadow}" stroke-width="3" opacity="0.7"/>` }); };
LIB.back.halo = (h, o) => { const c = o.color ?? '#ffe27a'; h.glow(`<ellipse cx="104" cy="26" rx="38" ry="12" fill="${c}" opacity="0.8" filter="url(#glow)"/>`); h.S(ring(104, 26, 34, 10, 5), TK(h, o.t, 'gold'), { eo: true, sh: 2, hl: 1.5 }); };
LIB.back.sun = (h, o) => { // grand disque rayonnant derrière la tête
  const t = TK(h, o.t, 'gold'), c = o.color ?? '#ffcf5a'; let rays = '';
  for (let i = 0; i < 12; i++) { const a = i * 30 * Math.PI / 180, r0 = 50, r1 = 70; rays += `M${f(104 + Math.cos(a - 0.1) * r0)} ${f(74 + Math.sin(a - 0.1) * r0)} L${f(104 + Math.cos(a) * r1)} ${f(74 + Math.sin(a) * r1)} L${f(104 + Math.cos(a + 0.1) * r0)} ${f(74 + Math.sin(a + 0.1) * r0)} Z `; }
  h.glow(`<circle cx="104" cy="74" r="66" fill="${c}" opacity="0.6" filter="url(#glow)"/>`);
  h.S(rays, t, { sh: 3, hl: 2 }); h.S(ring(104, 74, 52, 52, 7), t, { eo: true, sh: 4 });
};
LIB.back.drums = (h, o) => { // couronne de tambours (dieu du tonnerre)
  const t = TK(h, o.t, 'drum'), g = h.T.gold; const pts = arcPts(104, 96, 84, 84, 172, 368, 5);
  h.S(limb([pts[0], [104, -26], pts[5]], 6, 6, 18), g, { sh: 2, hl: 1.5 });
  for (const p of pts) h.S(disc(p[0], p[1], 17), t, { sh: 5, inner: `<circle cx="${f(p[0])}" cy="${f(p[1])}" r="11" fill="none" stroke="${g.base}" stroke-width="3"/><circle cx="${f(p[0])}" cy="${f(p[1])}" r="4" fill="${g.base}"/>` });
};
LIB.back.spider = (h, o) => { const t = TK(h, o.t, 'leg'); for (const [p, far] of [[[[122, 136], [160, 40], [192, 112]], 1], [[[124, 142], [186, 86], [198, 176]], 1], [[[90, 136], [50, 34], [16, 104]], 0], [[[88, 142], [22, 84], [6, 176]], 0]]) h.S(limb(p, 10, 2, 16), t, { sh: 3, far: !!far }); };
LIB.back.shuriken = (h, o) => { const t = TK(h, o.t, 'steel'); let d = ''; const c = [66, 150]; for (let i = 0; i < 4; i++) { const a = i * 90 + 20, r = (x) => x * Math.PI / 180; d += `${i ? 'L' : 'M'}${f(c[0] + Math.cos(r(a)) * 46)} ${f(c[1] + Math.sin(r(a)) * 46)} L${f(c[0] + Math.cos(r(a + 45)) * 14)} ${f(c[1] + Math.sin(r(a + 45)) * 14)} `; } h.S(d + 'Z', t, { sh: 5, inner: `<circle cx="66" cy="150" r="6" fill="#2a2030"/>` }); };
LIB.back.banner = (h, o) => { const t = TK(h, o.t, 'cape'); h.S(bar([86, 170], [72, 4], 5), h.T.wood, { sh: 2, hl: 1.5 }); h.S('M70 8 L30 14 L34 74 L74 66 Z', t, { sh: 6, inner: o.emblem ? emblem(o.emblem, 52, 40, 1.3, o.emblemColor ?? '#ffd76a') : '' }); };
LIB.back.bag = (h, o) => { const t = TK(h, o.t, 'bag'); h.S(limb([[40, 156], [100, -34], [170, 140]], 30, 30, 20), t, { sh: 8, inner: sf('M52 120 C80 30 130 30 158 110', t.shadow, 4, 0.4, 2) }); };
LIB.back.quills = (h, o) => { const t = TK(h, o.t, 'hair'); h.S('M96 190 L62 192' + saw([[62, 192], [56, 172], [60, 150], [72, 132], [92, 120]], 26, [-10, -6]) + ' Z', t, { sh: 6 }); };
LIB.back.cloud = (h, o) => { const c = o.color ?? '#f4f8ff'; h.raw(`<g opacity="0.95"><path d="M36 226 C22 226 20 208 34 206 C36 192 58 190 64 202 C74 192 96 194 100 206 C112 198 132 202 134 214 C150 208 170 214 172 226 Z" fill="${c}" stroke="#2c1626" stroke-width="2.5" stroke-linejoin="round"/></g>`); };
LIB.back.flames = (h, o) => { const t = TK(h, o.t, 'flame'); h.glow(`<path d="M60 190 C40 150 50 110 86 96 C70 130 80 160 100 186 Z" fill="${t.base}" opacity="0.7" filter="url(#glow)"/>`); h.S('M98 186 L62 190' + saw([[62, 190], [58, 168], [64, 146], [78, 128], [98, 122]], 30, [-14, -12]) + ' Z', t, { sh: 6, inner: `<path d="M94 132 C80 140 72 156 72 176" stroke="${t.light}" stroke-width="8" fill="none" opacity="0.7"/>` }); };

// =================== COIFFES (phase 'back' : avant la tête ; 'front' : par-dessus) ===================
const horn = (base, ctrl, tip, w) => limb([base, ctrl, tip], w, 1.6, 14);
const HORNS = {
  oni: [[[88, 52], [82, 30], [92, 12]], [[128, 48], [136, 28], [130, 12]], 13],
  bull: [[[76, 60], [44, 56], [42, 22]], [[140, 54], [170, 48], [170, 18]], 15],
  demon: [[[86, 50], [64, 30], [40, 30]], [[130, 46], [122, 20], [98, 12]], 13],
  ram: [[[82, 56], [46, 34], [50, 80]], [[136, 52], [168, 34], [160, 76]], 15],
  small: [[[92, 46], [90, 34], [96, 24]], [[126, 44], [130, 32], [128, 22]], 10],
};
LIB.gear.horns = (h, o, ph) => { const [n, fr, w] = HORNS[o.kind ?? 'oni'], t = TK(h, o.t, 'bone'); if (ph === 'back') h.S(horn(...fr, w - 1), t, { sh: 4, far: true }); else h.S(horn(...n, w), t, { sh: 4 }); };
LIB.gear.antlers = (h, o, ph) => {
  const t = TK(h, o.t, 'bone');
  const one = (x, s, far) => { h.S(limb([[x, 52], [x - s * 14, 24], [x - s * 30, 2]], 9, 3), t, { sh: 3, far }); h.S(limb([[x - s * 8, 34], [x - s * 26, 34], [x - s * 36, 22]], 6, 2), t, { sh: 2, far }); h.S(limb([[x - s * 16, 18], [x - s * 8, 6], [x - s * 10, -8]], 6, 2), t, { sh: 2, far }); };
  if (ph === 'back') one(132, -1, true); else one(84, 1, false);
};
LIB.gear.ears = (h, o, ph) => { // oreilles dressées (loup, renard, chacal, lapin…)
  const t = TK(h, o.t, 'skin'), H = o.h ?? 34, inn = TK(h, o.inner, 'skin').shadow;
  if (ph === 'back') h.S(`M120 50 L${134 + (o.lean ?? 0)} ${50 - H} L146 56 Z`, t, { sh: 4, far: true });
  else h.S(`M70 62 L${80 + (o.lean ?? 0)} ${56 - H} L102 46 Z`, t, { sh: 4, inner: `<path d="M78 56 L${82 + (o.lean ?? 0)} ${62 - H * 0.7} L94 50 Z" fill="${inn}"/>` });
};
LIB.gear.roundears = (h, o, ph) => { const t = TK(h, o.t, 'skin'); if (ph === 'back') h.S(disc(140, 50, 13), t, { sh: 3, far: true }); else h.S(disc(74, 56, 15), t, { sh: 3, inner: `<circle cx="74" cy="56" r="8" fill="${t.shadow}"/>` }); };
LIB.gear.sideears = (h, o, ph) => { const t = TK(h, o.t, 'skin'); if (ph === 'front') h.S(disc(66, 90, 13), t, { sh: 3, inner: `<circle cx="66" cy="90" r="7" fill="${t.shadow}"/>` }); };
LIB.gear.elfears = (h, o, ph) => { if (ph === 'front') h.S('M70 84 C56 76 42 72 30 74 C40 84 52 94 70 100 Z', h.T.skin, { sh: 4 }); };
LIB.gear.fin = (h, o, ph) => { if (ph === 'back') h.S('M96 44 C84 22 66 10 46 8 C60 24 66 40 70 58 Z', TK(h, o.t, 'skin'), { sh: 5 }); };
LIB.gear.hair = (h, o, ph) => {
  const t = TK(h, o.t, 'hair'), st = o.style ?? 'short', band = h.s.band ? bandInner(h.s.band, h.T) : '';
  if (ph === 'back') return;
  const sp = (pts, len, lean, extra = '') => h.S(`M152 72${FRINGE}` + saw([[72, 104], ...pts], len, lean) + ' C149 40 153 56 152 72 Z', t, { sh: 10, inner: band + extra });
  if (st === 'spiky') h.S(`M152 72${FRINGE} L46 108 L64 90 L30 82 L58 70 L28 50 L62 50 L44 22 L78 34 L72 6 L100 24 L104 2 L122 24 L132 8 L142 30 C149 40 153 56 152 72 Z`, t, { sh: 10, inner: band + sf('M70 40 C84 30 104 24 124 26', t.light, 5, 0.45, 2) });
  if (st === 'short') h.S('M64 86 C58 56 80 34 108 34 C138 34 154 54 151 80 C142 72 132 62 124 54 C114 66 98 72 84 72 C80 80 76 92 72 102 C68 98 65 92 64 86 Z', t, { sh: 9, inner: band });
  if (st === 'long') h.S('M66 86 C60 58 80 34 108 34 C136 34 152 52 150 80 C142 74 134 66 130 54 C122 66 110 76 96 78 C90 78 84 74 82 68 C80 84 78 104 74 120 C68 110 64 98 66 86 Z', t, { sh: 9, inner: band });
  if (st === 'bun') { h.S(disc(88, 30, 15), t, { sh: 5 }); h.S('M64 86 C58 56 80 34 108 34 C138 34 154 54 151 80 C142 72 132 62 124 54 C114 66 98 72 84 72 C80 80 76 92 72 102 C68 98 65 92 64 86 Z', t, { sh: 9, inner: band }); }
  if (st === 'topknot') { h.S(limb([[100, 38], [98, 18], [82, 6]], 14, 8), t, { sh: 4 }); h.S('M64 86 C58 56 80 34 108 34 C138 34 154 54 151 80 C142 72 132 62 124 54 C114 66 98 72 84 72 C80 80 76 92 72 102 C68 98 65 92 64 86 Z', t, { sh: 9, inner: band }); }
  if (st === 'flame') { h.glow(`<path d="M70 96 C40 60 60 10 110 0 C90 30 110 40 140 30 C150 50 150 70 150 80 Z" fill="${t.base}" opacity="0.7" filter="url(#glow)"/>`); sp(arcPts(104, 76, 46, 44, 150, 310, 6).slice(1), 34, [-14, -12], `<path d="M80 60 C92 44 112 38 132 42" stroke="${t.light}" stroke-width="9" fill="none" opacity="0.6"/>`); }
  if (st === 'wild') sp(arcPts(104, 76, 48, 46, 150, 310, 7).slice(1), 24, [-12, -2]);
  if (st === 'mane') sp(arcPts(104, 80, 52, 50, 140, 312, 9).slice(1), 18, [-8, 0]);
  if (st === 'leaf') sp(arcPts(104, 76, 46, 44, 150, 310, 6).slice(1), 20, [-8, -8], `<path d="M76 50 C90 40 110 36 130 40" stroke="${t.light}" stroke-width="4" fill="none" opacity="0.6"/>`);
  if (st === 'snakes') {
    for (const [a, c, b] of [[[76, 64], [40, 60], [24, 92]], [[82, 50], [46, 28], [26, 44]], [[96, 42], [80, 8], [56, 6]], [[114, 40], [112, 6], [90, -6]], [[130, 44], [142, 14], [126, 0]]]) { h.S(limb([a, c, b], 13, 7), t, { sh: 4 }); h.S(disc(b[0], b[1], 6.5), t, { sh: 3, inner: `<circle cx="${b[0] - 2}" cy="${b[1] - 1}" r="1.6" fill="#ffe14a"/>` }); }
    h.S('M64 86 C58 56 80 36 108 36 C138 36 154 54 151 78 C140 66 124 58 108 58 C92 58 80 68 76 84 C74 92 72 98 72 102 C68 98 65 92 64 86 Z', t, { sh: 8, inner: band });
  }
};
LIB.gear.helm = (h, o, ph) => {
  const t = TK(h, o.t, 'steel'), g = TK(h, o.band, 'gold');
  if (ph === 'back') { if (o.wings) h.S('M134 58 C146 44 156 26 160 6 C148 16 140 22 130 26 C132 36 132 48 134 58 Z', TK(h, o.wingT, 'bone'), { sh: 4, far: true }); return; }
  if (o.crest) h.S(o.crest === 'tall' ? 'M150 48 C146 2 70 -8 42 38 C36 58 42 78 50 92 C54 70 62 56 74 48 C92 30 124 30 138 50 Z' : 'M148 46 C142 12 78 6 60 44 L72 48 C86 28 128 28 138 48 Z', TK(h, o.crestT, 'crest'), { sh: 6 });
  if (o.neck) h.S('M62 76 C52 86 48 100 50 114 C60 114 70 108 76 98 Z', t, { sh: 5 });
  if (o.tassel) h.S('M108 8 C96 12 88 22 86 34 C96 30 104 22 108 8 Z', TK(h, o.tassel, 'crest'), { sh: 3 });
  h.S('M58 82 C54 52 78 30 108 30 C136 30 156 50 154 78 L142 74 C126 68 86 70 66 84 Z', t, { sh: 9, inner: o.plain ? '' : `<path d="M56 78 C80 62 124 60 156 72 L156 82 C124 70 80 72 56 88 Z" fill="${g.base}"/>` });
  if (o.cheek) h.S('M64 80 C62 96 66 110 76 118 L88 112 C80 102 78 90 80 78 Z', t, { sh: 5 });
  if (o.nose) h.S('M116 70 L128 70 L126 96 L119 96 Z', t, { sh: 3 });
  if (o.moon) h.S('M96 36 C88 8 118 -8 142 4 C128 6 118 18 120 36 Z', g, { sh: 3 });
  if (o.spike) h.S('M100 32 L108 4 L116 32 Z', t, { sh: 3 });
  if (o.wings) h.S('M78 66 C62 52 48 32 42 8 C56 18 68 24 80 28 C78 18 80 10 84 4 C92 20 96 40 94 60 Z', TK(h, o.wingT, 'bone'), { sh: 5 });
};
LIB.gear.hood = (h, o, ph) => {
  const t = TK(h, o.t, 'hood');
  if (ph === 'back') return;
  h.S(HOOD, t, { eo: true, sh: 10, inner: o.trim ? `<path d="${K.HOOD_OPEN}" fill="none" stroke="${o.trim}" stroke-width="5" opacity="0.9"/>` : sf('M66 60 C80 40 100 34 122 36', t.light, 5, 0.4, 2) });
  if (o.ears) { h.S('M76 44 L78 12 L100 30 Z', t, { sh: 4 }); h.S('M118 30 L138 10 L144 42 Z', t, { sh: 4, far: true }); }
  if (o.teeth) h.raw(`<path d="M96 60 l5 10 l5 -10 M112 57 l5 10 l5 -10 M128 59 l5 10 l5 -9" fill="#fff8e0" stroke="#2a1a20" stroke-width="1.2" stroke-linejoin="round"/>`);
};
LIB.gear.crown = (h, o, ph) => { if (ph === 'front') h.S('M70 60 L72 34 L88 48 L98 24 L110 46 L124 24 L132 48 L148 36 L148 62 C124 52 94 52 70 60 Z', TK(h, o.t, 'gold'), { sh: 5, inner: o.gem ? `<circle cx="110" cy="52" r="4.5" fill="${o.gem}"/>` : '' }); };
LIB.gear.tiara = (h, o, ph) => { if (ph === 'front') h.S('M76 62 C92 54 126 52 146 58 L140 40 L128 52 L116 30 L104 52 L90 42 Z', TK(h, o.t, 'gold'), { sh: 4, inner: o.gem ? `<circle cx="116" cy="46" r="4" fill="${o.gem}"/>` : '' }); };
LIB.gear.turban = (h, o, ph) => {
  if (ph !== 'front') return; const t = TK(h, o.t, 'turban');
  if (o.feather) h.S('M118 34 C116 12 124 -4 138 -10 C138 6 134 22 128 36 Z', TK(h, o.featherT, 'bone'), { sh: 3 });
  h.S('M58 78 C50 46 78 24 108 24 C140 24 160 46 154 74 C128 60 88 62 58 78 Z', t, { sh: 9, inner: `<path d="M62 62 C90 44 126 42 152 54 M70 46 C92 34 124 32 146 42" stroke="${t.shadow}" stroke-width="2.5" fill="none" opacity="0.6"/><circle cx="122" cy="52" r="6" fill="${o.gem ?? '#e04a4a'}" stroke="${h.T.gold.base}" stroke-width="2.5"/>` });
};
LIB.gear.tricorn = (h, o, ph) => { if (ph === 'front') { const t = TK(h, o.t, 'hat'); h.S('M72 62 C74 40 92 30 110 30 C128 30 144 40 146 58 Z', t, { sh: 6 }); h.S('M44 66 C62 50 90 52 108 62 C126 48 152 46 172 60 C150 62 128 70 108 78 C90 68 66 64 44 66 Z', t, { sh: 5, inner: `<path d="M48 65 C68 56 90 58 108 68 C126 56 150 54 168 60" stroke="${h.T.gold.base}" stroke-width="3" fill="none"/>` + (o.emblem ? emblem(o.emblem, 108, 46, 0.7, '#f4efe2') : '') }); } };
LIB.gear.kasa = (h, o, ph) => { if (ph === 'front') { const t = TK(h, o.t, 'straw'); h.S('M36 72 L106 22 L176 72 C140 82 72 82 36 72 Z', t, { sh: 8, inner: `<path d="M106 22 L60 76 M106 22 L84 80 M106 22 L128 80 M106 22 L152 76" stroke="${t.shadow}" stroke-width="2" opacity="0.5"/>` }); } };
LIB.gear.tophat = (h, o, ph) => { if (ph === 'front') { const t = TK(h, o.t, 'hat'); h.S('M76 58 L72 8 C92 0 124 0 144 6 L142 56 C120 62 96 62 76 58 Z', t, { sh: 7, inner: `<path d="M60 40 L160 34 L160 48 L60 54 Z" fill="${TK(h, o.band, 'scarf').base}"/>` + (o.emblem ? emblem(o.emblem, 108, 26, 0.75, '#f4efe2') : '') }); h.S('M48 62 C70 50 146 46 168 56 C150 70 70 74 48 62 Z', t, { sh: 4 }); } };
LIB.gear.furhat = (h, o, ph) => { if (ph === 'front') { const t = TK(h, o.t, 'hat'), fu = TK(h, o.fur, 'fur'); h.S('M62 70 C56 42 80 26 108 26 C136 26 158 42 152 66 Z', t, { sh: 7 }); h.S('M54 78 C82 62 130 60 158 70 L156 52 C130 42 82 44 56 60 Z', fu, { sh: 5 }); h.S('M56 70 C52 86 54 100 62 110 L74 104 C70 94 70 84 72 74 Z', fu, { sh: 4 }); } };
LIB.gear.feathers = (h, o, ph) => { // grande coiffe de plumes, en éventail vers l'arrière
  if (ph !== 'back') { h.S('M64 72 C88 56 128 54 152 64 L152 76 C128 66 88 68 64 84 Z', TK(h, o.band, 'gold'), { sh: 4 }); return; }
  const cols = o.colors ?? ['#e0483a', '#f0b23a', '#2fa37a'], n = o.n ?? 7;
  for (let i = 0; i < n; i++) { const a = (208 - i * (150 / (n - 1))) * Math.PI / 180, c = [104, 76], p0 = add(c, [Math.cos(a) * 34, -Math.sin(a) * 34]), p1 = add(c, [Math.cos(a) * (o.len ?? 84), -Math.sin(a) * (o.len ?? 84)]); h.S(limb([p0, add(p0, [(p1[0] - p0[0]) / 2 - 4, (p1[1] - p0[1]) / 2 - 4]), p1], 16, 5), tone(cols[i % cols.length]), { sh: 4 }); }
};
LIB.gear.veil = (h, o, ph) => { if (ph === 'front') h.S('M62 86 C56 54 80 30 108 30 C136 30 154 50 152 76 C140 62 124 54 108 54 C92 54 78 64 74 82 C72 94 70 106 68 118 C62 108 60 96 62 86 Z', TK(h, o.t, 'veil'), { sh: 8, inner: h.s.band ? bandInner(h.s.band, h.T) : '' }); };
LIB.gear.skullcap = (h, o, ph) => { if (ph === 'front') h.S('M66 70 C64 42 86 28 108 28 C132 28 150 42 148 66 C138 58 130 64 124 60 L120 70 L114 60 C106 60 100 64 96 60 L92 72 L86 62 C78 62 72 66 66 70 Z', TK(h, o.t, 'bone'), { sh: 7, inner: `<ellipse cx="96" cy="46" rx="8" ry="9" fill="#2a1a30"/><ellipse cx="126" cy="44" rx="7" ry="8.5" fill="#2a1a30"/><path d="M110 50 L114 58 L106 58 Z" fill="#2a1a30"/>` }); };
LIB.gear.disc = (h, o, ph) => { if (ph === 'back') { h.glow(`<circle cx="108" cy="22" r="24" fill="${o.color ?? '#ffb84a'}" opacity="0.7" filter="url(#glow)"/>`); h.S(disc(108, 22, 18), TK(h, o.t, 'gold'), { sh: 5 }); } };
LIB.gear.mohawk = (h, o, ph) => { if (ph === 'front') h.S('M132 50 L114 16 L113 40 L94 10 L95 38 L74 12 L79 40 L58 28 L72 58 C92 46 114 44 132 50 Z', TK(h, o.t, 'hair'), { sh: 6 }); };
LIB.gear.frill = (h, o, ph) => { if (ph === 'back') h.S('M84 88 L64 96' + saw([[64, 96], [62, 76], [70, 56], [86, 44], [106, 38]], o.len ?? 24, [-8, -4]) + ' Z', TK(h, o.t, 'fin'), { sh: 5 }); };
LIB.gear.leaves = (h, o, ph) => { if (ph === 'front') { const t = TK(h, o.t, 'leaf'); for (const [x, y, r] of [[78, 52, -40], [98, 40, -15], [120, 38, 10], [140, 48, 35]]) h.at(`translate(${x} ${y}) rotate(${r})`, () => h.S('M0 6 C-8 -4 -6 -16 0 -22 C6 -16 8 -4 0 6 Z', t, { sh: 3, hl: 2 })); } };
LIB.gear.flower = (h, o, ph) => { if (ph === 'front') { const c = o.color ?? '#ff8ab0'; h.raw(`<g transform="translate(${o.x ?? 80} ${o.y ?? 56})"><circle r="9" fill="${c}" stroke="#2c1626" stroke-width="2"/><circle r="3.5" fill="#ffe27a"/></g>`); } };
LIB.gear.nose = (h, o, ph) => { if (ph === 'front') h.S(limb([[134, 96], [156, 98], [180, 94]], 11, 9), TK(h, o.t, 'skin'), { sh: 4, hl: 3 }); }; // long nez (tengu)

LIB.gear.dish = (h, o, ph) => { if (ph === 'front') { h.S('M62 72 C70 58 86 52 106 52 C126 52 142 58 150 68 L146 80 L136 66 L126 80 L116 66 L106 80 L96 66 L86 80 L76 68 L66 82 Z', TK(h, o.t, 'hair'), { sh: 4 }); h.S(ell(106, 44, 28, 9), tone(o.color ?? '#bfe9ff'), { sh: 3, hl: 2 }); } }; // coupelle d'eau du kappa
LIB.gear.mian = (h, o, ph) => { // couronne plate à rideaux de perles (impératrice céleste)
  if (ph !== 'front') return; const g = TK(h, o.t, 'gold');
  h.S('M76 62 C92 50 126 48 144 56 L142 40 C124 34 94 36 80 46 Z', TK(h, o.cap, 'cloth'), { sh: 4 });
  h.S('M56 42 L160 30 L162 42 L58 54 Z', g, { sh: 3, hl: 2 });
  h.raw(`<g stroke="${g.base}" stroke-width="2"><path d="M146 40 L146 62 M154 39 L154 60 M138 41 L138 60"/></g><g fill="${o.gem ?? '#e04a4a'}"><circle cx="146" cy="64" r="3"/><circle cx="154" cy="62" r="3"/><circle cx="138" cy="62" r="3"/></g>`);
};
LIB.gear.eyes = (h, o, ph) => { if (ph === 'front') h.raw(`<g fill="${o.color ?? '#ff4a4a'}" stroke="#1c1218" stroke-width="1.5"><circle cx="96" cy="66" r="4"/><circle cx="116" cy="62" r="4"/><circle cx="136" cy="66" r="3.4"/></g>`); }; // yeux en plus sur le front
LIB.gear.whiskers = (h, o, ph) => { if (ph === 'front') { const t = TK(h, o.t, 'gold'); h.S(limb([[150, 100], [176, 92], [186, 64]], 4, 2), t, { sh: 1, hl: 1, rim: false }); h.S(limb([[146, 106], [168, 124], [192, 120]], 4, 2), t, { sh: 1, hl: 1, rim: false }); } };
module.exports = { emblem, TK, horn };
