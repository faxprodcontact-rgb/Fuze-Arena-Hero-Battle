// Ce qui s'ajoute au corps (version 6) : cheveux et coiffes, dos, cou. Chaque pièce est une commande [nom, options].
// Les coiffes reçoivent une phase : 'back' (derrière la tête) puis 'front' (par-dessus).
const K = require('./fig6.cjs');
const { LIB, CX, f, pt, poly, add, unit, perp, limb, disc, ell, ring, bar, blade, saw, arcPts, sf, tone, metal, mix } = K;
const C = LIB.cmd;
const front = (fn) => (h, o, ph) => { if (ph === 'back') return; fn(h, o); };
const back = (fn) => (h, o, ph) => { if (ph === 'front') return; fn(h, o); };
function emblem(kind, x, y, k, col, line = '#3a2408') {
  const d = { flame: 'M0 -14 C8 -6 12 2 8 10 C6 14 -6 14 -8 10 C-12 2 -6 -2 -4 -8 C-2 -4 0 -4 0 -14 Z', drop: 'M0 -14 C8 -2 10 4 8 9 C5 15 -5 15 -8 9 C-10 4 -8 -2 0 -14 Z',
    swirl: 'M-10 2 C-10 -10 8 -12 10 0 C11 8 0 10 -2 4 C-3 0 2 -2 4 1 M-10 2 C-8 12 6 14 12 8', leaf: 'M-10 10 C-12 -4 0 -14 12 -12 C12 0 4 12 -10 10 Z M-8 8 L8 -8',
    bolt: 'M4 -14 L-8 2 L0 2 L-4 14 L10 -4 L1 -4 Z', sun: 'M0 -7 A7 7 0 1 0 0.1 -7 Z M0 -14 L0 -10 M0 10 L0 14 M-14 0 L-10 0 M10 0 L14 0 M-10 -10 L-7 -7 M7 7 L10 10 M-10 10 L-7 7 M7 -7 L10 -10',
    moon: 'M4 -12 C-8 -10 -10 8 4 12 C-2 6 -2 -6 4 -12 Z', skull: 'M-8 -2 C-8 -12 8 -12 8 -2 C8 4 5 6 5 10 L-5 10 C-5 6 -8 4 -8 -2 Z', star: 'M0 -12 L3 -4 L12 -4 L5 2 L8 11 L0 6 L-8 11 L-5 2 L-12 -4 L-3 -4 Z',
    wing: 'M-12 8 C-8 -6 2 -12 14 -12 C10 -6 8 -2 10 2 C4 0 0 2 -2 6 C-6 4 -10 6 -12 8 Z', wave: 'M-14 2 C-8 -8 0 -8 0 0 C0 8 8 8 14 -2', rune: 'M-6 -12 L-6 12 M-6 -12 L8 -2 L-6 4 M4 12 L8 4', anchor: 'M0 -12 L0 10 M-8 -4 L8 -4 M-10 4 C-8 12 8 12 10 4', eye: 'M-12 0 C-6 -9 6 -9 12 0 C6 9 -6 9 -12 0 Z M0 -4 A4 4 0 1 0 0.1 -4 Z' }[kind];
  const stroke = ['swirl', 'sun', 'wave', 'rune', 'anchor'].includes(kind);
  return `<g transform="translate(${x} ${y}) scale(${k})"><path d="${d}" fill="${stroke ? 'none' : col}" stroke="${stroke ? col : line}" stroke-width="${stroke ? 3 : 1.4}" stroke-linejoin="round" stroke-linecap="round"/></g>`;
}
const bandIn = (h, b) => { if (!b) return ''; const t = h.TK(b.t, 'gold'), y = b.y ?? 62, k = b.k ?? 10; return `<path d="M40 ${y + 8} C84 ${y - 4} 122 ${y - 4} 170 ${y + 10} L170 ${y + 10 + k} C122 ${y - 4 + k} 84 ${y - 4 + k} 40 ${y + 8 + k} Z" fill="${t.base}"/>`; };

// =================== CHEVEUX ===================
const FRINGE = ' C143 73 133 63 124 54 C114 66 98 72 84 72 C80 80 76 92 72 104'; // une frange lisse : aucun pic ne retombe sur le front
const CAP = 'M64 86 C58 56 80 34 108 34 C138 34 154 54 151 80 C142 72 132 62 124 54 C114 66 98 72 84 72 C80 80 76 92 72 102 C68 98 65 92 64 86 Z';
const HAIR = {
  spiky: `M152 72${FRINGE} L46 108 L64 90 L30 82 L58 70 L28 50 L62 50 L44 22 L78 34 L72 6 L100 24 L104 2 L122 24 L132 8 L142 30 C149 40 153 56 152 72 Z`,
  short: CAP,
  long: 'M66 86 C60 58 80 34 108 34 C136 34 152 52 150 80 C142 74 134 66 130 54 C122 66 110 76 96 78 C90 78 84 74 82 68 C80 84 78 104 74 120 C68 110 64 98 66 86 Z',
  slick: 'M64 86 C58 54 82 32 110 32 C138 32 154 50 152 72 C140 62 120 56 100 60 C86 64 78 78 74 104 L58 112 L64 98 Z',
  bob: 'M62 86 C56 54 80 32 108 32 C138 32 156 52 152 80 C144 70 134 62 124 56 C112 68 96 74 86 74 C84 90 84 106 86 120 C72 116 62 102 62 86 Z',
  curly: 'M64 90 C54 86 54 72 62 67 C56 57 64 45 76 45 C78 34 92 28 102 34 C110 26 126 28 132 37 C144 34 155 45 152 57 C160 63 158 77 150 81 C146 72 138 64 128 60 C116 70 98 74 84 72 C80 80 76 92 72 102 C68 98 66 94 64 90 Z',
  parted: 'M64 86 C58 56 80 34 108 34 C138 34 154 54 151 82 C146 70 138 58 122 50 C120 62 108 74 84 74 C80 82 76 92 72 102 C68 98 65 92 64 86 Z',
  crest: 'M132 50 L114 16 L113 40 L94 10 L95 38 L74 12 L79 40 L58 28 L72 58 C92 46 114 44 132 50 Z',
  strip: 'M134 48 C128 34 112 28 96 30 C82 32 72 42 68 58 C84 46 112 42 134 48 Z',
};
C.hair = front((h, o) => {
  const t = h.TK(o.t, 'hair'), st = o.style ?? 'short', band = bandIn(h, o.band);
  const sp = (pts, len, lean, extra = '') => h.S(`M152 72${FRINGE}` + saw([[72, 104], ...pts], len, lean) + ' C149 40 153 56 152 72 Z', t, { sh: 10, inner: band + extra });
  if (HAIR[st]) return h.S(HAIR[st], t, { sh: st === 'crest' || st === 'strip' ? 6 : 9, inner: band + (st === 'spiky' ? sf('M70 40 C84 30 104 24 124 26', t.light, 5, 0.45, 2) : '') });
  if (st === 'bun' || st === 'topknot') { if (st === 'bun') h.S(disc(o.bx ?? 88, o.by ?? 30, o.br ?? 15), t, { sh: 5 }); else h.S(limb([[100, 38], [98, 18], [82, 6]], 14, 8), t, { sh: 4 }); return h.S(CAP, t, { sh: 9, inner: band }); }
  if (st === 'flame') { h.glow(`<path d="M70 96 C40 60 60 10 110 0 C90 30 110 40 140 30 C150 50 150 70 150 80 Z" fill="${t.base}" opacity="0.7" filter="url(#glow)"/>`); return sp(arcPts(104, 76, 46, 44, 150, 310, 6).slice(1), 34, [-14, -12], `<path d="M80 60 C92 44 112 38 132 42" stroke="${t.light}" stroke-width="9" fill="none" opacity="0.6"/>`); }
  if (st === 'wild') return sp(arcPts(104, 76, 48, 46, 150, 310, 7).slice(1), o.len ?? 24, [-12, -2]);
  if (st === 'mane') return sp(arcPts(104, 80, 52, 50, 140, 312, 9).slice(1), 18, [-8, 0]);
  if (st === 'leaf') return sp(arcPts(104, 76, 46, 44, 150, 310, 6).slice(1), 20, [-8, -8], `<path d="M76 50 C90 40 110 36 130 40" stroke="${t.light}" stroke-width="4" fill="none" opacity="0.6"/>`);
  if (st === 'ice') return sp(arcPts(104, 76, 46, 44, 150, 310, 5).slice(1), 30, [-16, 6]);
  if (st === 'snakes') {
    for (const [a, c, b] of [[[76, 64], [40, 60], [24, 92]], [[82, 50], [46, 28], [26, 44]], [[96, 42], [80, 8], [56, 6]], [[114, 40], [112, 6], [90, -6]], [[130, 44], [142, 14], [126, 0]]]) { h.S(limb([a, c, b], 13, 7), t, { sh: 4 }); h.S(ell(b[0], b[1], 9, 7), t, { sh: 3, inner: `<circle cx="${b[0] - 3}" cy="${b[1] - 2}" r="2" fill="#ffe14a"/><circle cx="${b[0] - 3}" cy="${b[1] - 2}" r="0.9" fill="#1c1218"/><path d="M${b[0] - 8} ${b[1] + 2} l5 1.5" stroke="#1c1218" stroke-width="1.2"/>` }); }
    return h.S('M64 86 C58 56 80 36 108 36 C138 36 154 54 151 78 C140 66 124 58 108 58 C92 58 80 68 76 84 C74 92 72 98 72 102 C68 98 65 92 64 86 Z', t, { sh: 8, inner: band });
  }
  if (st === 'canopy') { for (const [x, y, r] of [[70, 62, 22], [92, 40, 24], [122, 38, 24], [146, 56, 20], [56, 86, 16]]) h.S(disc(x, y, r), t, { sh: 6 }); return h.S('M62 86 C56 56 80 34 108 34 C138 34 156 54 152 78 C140 66 124 58 108 58 C92 58 80 68 76 84 C74 92 72 98 72 104 C66 100 63 94 62 86 Z', t, { sh: 8 }); }
  throw new Error('cheveux inconnus : ' + st);
});
// cheveux derrière la tête (dans la couche « dos »)
const HAIRBACK = {
  long: 'M68 70 C56 100 50 140 46 178 C44 196 38 208 28 216 C48 218 68 208 80 192 C90 174 94 150 94 124 L142 120 C148 108 150 94 150 82 Z',
  mid: 'M68 70 C58 96 54 124 56 150 C66 150 80 144 90 134 L142 120 C148 108 150 94 150 82 Z',
  floor: 'M68 70 C54 104 46 150 40 196 C38 210 32 220 22 226 L70 228 C84 200 92 164 94 124 L142 120 C148 108 150 94 150 82 Z',
  windy: 'M74 56 C50 56 26 68 4 92 C26 88 42 92 52 100 C38 104 26 116 20 132 C44 126 66 114 82 98 L96 80 Z',
  waves: 'M68 70 C54 86 58 102 50 116 C42 130 48 146 40 160 C34 172 38 184 30 196 C50 196 66 186 72 170 C82 160 80 146 88 136 C94 128 94 122 94 118 L142 120 C148 108 150 94 150 82 Z',
};
C.hairBack = (h, o) => { const t = h.TK(o.t, 'hair'), st = o.style ?? 'long';
  if (HAIRBACK[st]) return h.S(HAIRBACK[st], t, { sh: 10, inner: st === 'windy' ? sf('M80 70 C56 70 34 80 16 96', t.light, 3, 0.4, 1) : sf('M72 104 C68 144 60 184 42 212', t.shadow, 6, 0.45, 3) });
  if (st === 'pony') return h.S(limb([[76, 66], [30, 60], [30, 116]], 24, 5), t, { sh: 6 });
  if (st === 'ponyHigh') return h.S(limb([[84, 44], [40, 22], [26, 76]], 22, 5), t, { sh: 6 });
  if (st === 'braid') return h.S(limb([[76, 92], [52, 134], [62, 180]], 16, 8), t, { sh: 5, inner: `<path d="M66 108 l10 6 M60 124 l11 5 M57 140 l11 4 M57 156 l10 3" stroke="${t.shadow}" stroke-width="2" opacity="0.8"/>` });
  if (st === 'twin') { h.S(limb([[72, 84], [44, 110], [50, 160]], 18, 6), t, { sh: 5 }); return h.S(limb([[140, 82], [168, 108], [164, 158]], 16, 5), t, { sh: 5, far: true }); }
  if (st === 'locs') { for (const [x, l] of [[70, 150], [78, 164], [88, 156], [62, 136]]) h.S(limb([[x, 78], [x - 12, 78 + (l - 78) / 2], [x - 8, l]], 11, 7), t, { sh: 4 }); return; }
  throw new Error('cheveux de dos inconnus : ' + st);
};

// =================== COIFFES ===================
const horn = (base, ctrl, tip, w) => limb([base, ctrl, tip], w, 1.6, 14);
const HORNS = { oni: [[[88, 52], [82, 30], [92, 12]], [[128, 48], [136, 28], [130, 12]], 13], bull: [[[76, 60], [44, 56], [42, 22]], [[140, 54], [170, 48], [170, 18]], 15],
  demon: [[[86, 50], [64, 30], [40, 30]], [[130, 46], [122, 20], [98, 12]], 13], ram: [[[82, 56], [46, 34], [50, 80]], [[136, 52], [168, 34], [160, 76]], 15],
  small: [[[92, 46], [90, 34], [96, 24]], [[126, 44], [130, 32], [128, 22]], 10], long: [[[84, 52], [70, 20], [84, -6]], [[130, 48], [146, 18], [134, -8]], 12], one: [[[108, 42], [104, 22], [112, 6]], null, 14] };
C.horns = (h, o, ph) => { const [n, fr, w] = HORNS[o.kind ?? 'oni'], t = h.TK(o.t, 'bone'); if (ph === 'back') { if (fr) h.S(horn(...fr, w - 1), t, { sh: 4, far: true }); } else h.S(horn(...n, w), t, { sh: 4 }); };
C.antlers = (h, o, ph) => { const t = h.TK(o.t, 'bone'), z = o.z ?? 1;
  const one = (x, s, far) => { h.S(limb([[x, 52], [x - s * 14 * z, 24], [x - s * 30 * z, 2 - 10 * (z - 1)]], 9, 3), t, { sh: 3, far }); h.S(limb([[x - s * 8 * z, 34], [x - s * 26 * z, 34], [x - s * 36 * z, 22]], 6, 2), t, { sh: 2, far }); h.S(limb([[x - s * 16 * z, 18], [x - s * 8 * z, 6], [x - s * 10 * z, -8 * z]], 6, 2), t, { sh: 2, far }); if (z > 1.1) h.S(limb([[x - s * 22 * z, 10], [x - s * 36 * z, 8], [x - s * 44 * z, -6]], 5, 2), t, { sh: 2, far }); };
  if (ph === 'back') one(132, -1, true); else one(84, 1, false); };
C.ears = (h, o, ph) => { // oreilles dressées : tall (chacal), fox, round, side (singe), elf, cat
  const t = h.TK(o.t, 'skin'), k = o.kind ?? 'fox', inn = h.TK(o.inner, 'skin').shadow, H = k === 'tall' ? 50 : k === 'cat' ? 26 : 36;
  if (k === 'round') { if (ph === 'back') h.S(disc(140, 50, 13), t, { sh: 3, far: true }); else h.S(disc(74, 56, 15), t, { sh: 3, inner: `<circle cx="74" cy="56" r="8" fill="${inn}"/>` }); return; }
  if (k === 'side') { if (ph !== 'back') h.S(disc(66, 90, 14), t, { sh: 3, inner: `<circle cx="66" cy="90" r="7.5" fill="${inn}"/>` }); return; }
  if (k === 'elf') { if (ph !== 'back') h.S('M72 84 C56 76 42 72 28 74 C40 86 54 96 72 100 Z', t, { sh: 4, inner: `<path d="M68 88 C56 82 46 80 38 80" stroke="${inn}" stroke-width="2" fill="none" opacity="0.7"/>` }); return; }
  if (ph === 'back') h.S(`M120 50 L${134 + (k === 'tall' ? 2 : 0)} ${50 - H} L146 56 Z`, t, { sh: 4, far: true });
  else h.S(`M70 62 L${80 + (k === 'tall' ? 4 : 0)} ${56 - H} L102 46 Z`, t, { sh: 4, inner: `<path d="M78 56 L${82 + (k === 'tall' ? 3 : 0)} ${62 - H * 0.7} L94 50 Z" fill="${inn}"/>` });
};
C.fin = back((h, o) => h.S('M96 44 C84 22 66 10 46 8 C60 24 66 40 70 58 Z', h.TK(o.t, 'skin'), { sh: 5 }));
C.frill = back((h, o) => h.S('M84 88 L64 96' + saw([[64, 96], [62, 76], [70, 56], [86, 44], [106, 38]], o.len ?? 24, [-8, -4]) + ' Z', h.TK(o.t, 'fin'), { sh: 5 }));
const HOODS = {
  tail: 'M56 86 C54 72 58 58 66 48 C56 44 46 46 34 54 C44 38 62 30 78 32 C88 27 98 26 108 26 C142 26 162 52 158 88 C156 106 148 118 136 126 L84 126 C68 118 58 104 56 86 Z',
  cowl: 'M54 88 C50 50 78 24 108 24 C142 24 164 52 158 88 C156 106 148 118 136 126 L84 126 C68 118 58 104 54 88 Z',
  parka: 'M50 88 C46 46 76 20 108 20 C144 20 168 50 162 90 C160 108 150 120 138 128 L82 128 C64 120 54 106 50 88 Z',
  peak: 'M56 88 C52 58 70 34 96 26 C100 12 110 2 124 -4 C120 8 122 18 128 28 C150 38 162 60 158 88 C156 106 148 118 136 126 L84 126 C68 118 58 104 56 88 Z',
};
const HOOD_OPEN = 'M84 86 C84 66 98 56 116 56 C134 56 150 68 150 86 C150 100 142 112 128 117 C116 120 102 120 94 115 C86 109 84 98 84 86 Z';
C.hood = front((h, o) => { const t = h.TK(o.t, 'hood'), k = o.kind ?? 'tail';
  let inner = sf('M66 60 C80 40 100 34 122 36', t.light, 5, 0.4, 2);
  if (o.trim) inner += `<path d="${HOOD_OPEN}" fill="none" stroke="${h.TK(o.trim).base}" stroke-width="${o.trimW ?? 5}" opacity="0.95"/>`;
  if (o.ears) { h.S('M76 44 L78 12 L100 30 Z', t, { sh: 4 }); h.S('M118 30 L138 10 L144 42 Z', t, { sh: 4, far: true }); }
  h.S(HOODS[k] + ' ' + HOOD_OPEN, t, { eo: true, sh: 10, inner });
  if (o.teeth) h.raw(`<path d="M96 60 l5 10 l5 -10 M112 57 l5 10 l5 -10 M128 59 l5 10 l5 -9" fill="#fff8e0" stroke="#2a1a20" stroke-width="1.2" stroke-linejoin="round"/>`);
  if (o.nose) h.S('M108 30 C116 26 130 28 136 36 C128 40 116 40 108 36 Z', tone(o.nose), { sh: 2, hl: 2, rim: false });
});
const HELM = 'M58 82 C54 52 78 30 108 30 C136 30 156 50 154 78 L142 74 C126 68 86 70 66 84 Z';
C.helm = (h, o, ph) => { const t = h.TK(o.t, 'steel'), g = h.TK(o.band, 'gold'), k = o.kind ?? 'dome';
  if (ph === 'back') { if (o.wings) h.S('M134 58 C146 44 156 26 160 6 C148 16 140 22 130 26 C132 36 132 48 134 58 Z', h.TK(o.wingT, 'bone'), { sh: 4, far: true }); return; }
  if (o.crest === 'tall') h.S('M150 48 C146 2 70 -8 42 38 C36 58 42 78 50 92 C54 70 62 56 74 48 C92 30 124 30 138 50 Z', h.TK(o.crestT, 'crest'), { sh: 6 });
  if (o.crest === 'low') h.S('M148 46 C142 12 78 6 60 44 L72 48 C86 28 128 28 138 48 Z', h.TK(o.crestT, 'crest'), { sh: 6 });
  if (o.crest === 'cross') h.S('M56 50 C54 20 80 0 108 0 C136 0 160 18 158 48 C146 34 128 28 108 28 C88 28 68 36 56 50 Z', h.TK(o.crestT, 'crest'), { sh: 6, inner: `<path d="M70 30 L84 14 M92 26 L98 6 M116 26 L118 4 M136 28 L134 10" stroke="${h.TK(o.crestT, 'crest').shadow}" stroke-width="2" opacity="0.6"/>` });
  if (o.neck) h.S('M62 76 C52 86 48 100 50 114 C60 114 70 108 76 98 Z', t, { sh: 5 });
  if (o.tassel) h.S('M108 8 C96 12 88 22 86 34 C96 30 104 22 108 8 Z', h.TK(o.tassel, 'crest'), { sh: 3 });
  if (k === 'dome') h.S(HELM, t, { sh: 9, inner: o.plain ? '' : `<path d="M56 78 C80 62 124 60 156 72 L156 82 C124 70 80 72 56 88 Z" fill="${g.base}"/>` });
  if (k === 'cone') h.S('M58 84 C62 58 86 44 106 16 C128 44 150 56 154 80 L142 76 C126 70 86 72 66 86 Z', t, { sh: 9, inner: `<path d="M56 80 C80 64 124 62 156 74 L156 84 C124 72 80 74 56 90 Z" fill="${g.base}"/>` });
  if (k === 'corinth') { h.S('M60 80 C56 50 80 30 108 30 C138 30 156 50 154 82 C154 100 146 114 134 123 L96 123 C76 116 62 100 60 80 Z M90 78 C106 70 136 69 152 74 L152 97 L137 98 L134 123 L120 123 L120 98 L90 99 Z', t, { eo: true, sh: 9 }); return; }
  if (k === 'great') { h.S('M60 62 L64 36 L148 34 L154 60 L154 104 C142 118 126 125 108 125 C90 125 72 118 60 104 Z', t, { sh: 9, inner: `<path d="M94 82 L152 79 L152 88 L94 91 Z" fill="#14101c"/><path d="M124 34 L126 125" stroke="${g.base}" stroke-width="6"/><path d="M60 62 L154 60" stroke="${t.shadow}" stroke-width="2.4" opacity="0.7"/><g fill="#14101c"><circle cx="104" cy="104" r="2.2"/><circle cx="112" cy="108" r="2.2"/><circle cx="138" cy="104" r="2.2"/><circle cx="146" cy="100" r="2.2"/></g>` }); return; }
  if (o.cheek) h.S('M64 80 C62 96 66 110 76 118 L88 112 C80 102 78 90 80 78 Z', t, { sh: 5 });
  if (o.nose) h.S('M116 70 L128 70 L126 96 L119 96 Z', t, { sh: 3 });
  if (o.moon) h.S('M96 36 C88 8 118 -8 142 4 C128 6 118 18 120 36 Z', g, { sh: 3 });
  if (o.spike) h.S('M100 32 L108 4 L116 32 Z', t, { sh: 3 });
  if (o.wings) h.S('M78 66 C62 52 48 32 42 8 C56 18 68 24 80 28 C78 18 80 10 84 4 C92 20 96 40 94 60 Z', h.TK(o.wingT, 'bone'), { sh: 5 });
};
C.crown = front((h, o) => h.S(o.kind === 'spire' ? 'M72 60 C92 52 126 52 146 58 L140 44 L128 50 L122 30 L114 46 L108 -4 L102 46 L94 30 L88 50 L76 46 Z' : o.kind === 'shards' ? 'M70 62 L62 30 L84 48 L88 14 L104 44 L112 4 L122 44 L138 16 L138 48 L154 34 L148 62 C124 52 94 52 70 62 Z' : 'M70 60 L72 34 L88 48 L98 24 L110 46 L124 24 L132 48 L148 36 L148 62 C124 52 94 52 70 60 Z', h.TK(o.t, 'gold'), { sh: 5, inner: o.gem ? `<circle cx="110" cy="52" r="4.5" fill="${o.gem}"/>` : '' }));
C.tiara = front((h, o) => h.S('M76 62 C92 54 126 52 146 58 L140 40 L128 52 L116 30 L104 52 L90 42 Z', h.TK(o.t, 'gold'), { sh: 4, inner: o.gem ? `<circle cx="116" cy="46" r="4" fill="${o.gem}"/>` : '' }));
C.turban = front((h, o) => { const t = h.TK(o.t, 'turban');
  if (o.feather) h.S('M118 34 C116 12 124 -4 138 -10 C138 6 134 22 128 36 Z', h.TK(o.featherT, 'bone'), { sh: 3 });
  if (o.kind === 'gele') { h.S('M52 70 C40 40 60 8 96 6 C132 4 164 24 164 52 C164 62 160 70 154 76 C128 60 88 62 60 80 Z', t, { sh: 10, inner: `<path d="M58 60 C84 36 130 30 160 46 M66 40 C90 20 128 18 152 30 M62 74 C88 54 128 52 156 66" stroke="${t.shadow}" stroke-width="2.6" fill="none" opacity="0.55"/>` }); return; }
  h.S('M58 78 C50 46 78 24 108 24 C140 24 160 46 154 74 C128 60 88 62 58 78 Z', t, { sh: 9, inner: `<path d="M62 62 C90 44 126 42 152 54 M70 46 C92 34 124 32 146 42" stroke="${t.shadow}" stroke-width="2.5" fill="none" opacity="0.6"/><circle cx="122" cy="52" r="6" fill="${o.gem ?? '#e04a4a'}" stroke="${h.T.gold.base}" stroke-width="2.5"/>` });
});
C.tricorn = front((h, o) => { const t = h.TK(o.t, 'hat'); if (o.feather) h.S(limb([[80, 46], [52, 20], [28, 30]], 14, 3), h.TK(o.feather), { sh: 3 }); h.S('M72 62 C74 40 92 30 110 30 C128 30 144 40 146 58 Z', t, { sh: 6 }); h.S('M44 66 C62 50 90 52 108 62 C126 48 152 46 172 60 C150 62 128 70 108 78 C90 68 66 64 44 66 Z', t, { sh: 5, inner: `<path d="M48 65 C68 56 90 58 108 68 C126 56 150 54 168 60" stroke="${h.T.gold.base}" stroke-width="3" fill="none"/>` + (o.emblem ? emblem(o.emblem, 108, 46, 0.7, '#f4efe2') : '') }); });
C.kasa = front((h, o) => { const t = h.TK(o.t, 'straw'); h.S('M36 72 L106 22 L176 72 C140 82 72 82 36 72 Z', t, { sh: 8, inner: `<path d="M106 22 L60 76 M106 22 L84 80 M106 22 L128 80 M106 22 L152 76" stroke="${t.shadow}" stroke-width="2" opacity="0.5"/>` }); });
C.tophat = front((h, o) => { const t = h.TK(o.t, 'hat'); h.S('M76 58 L72 8 C92 0 124 0 144 6 L142 56 C120 62 96 62 76 58 Z', t, { sh: 7, inner: `<path d="M60 40 L160 34 L160 48 L60 54 Z" fill="${h.TK(o.band, 'scarf').base}"/>` + (o.emblem ? emblem(o.emblem, 108, 24, 0.75, '#f4efe2') : '') }); h.S('M48 62 C70 50 146 46 168 56 C150 70 70 74 48 62 Z', t, { sh: 4 }); });
C.furhat = front((h, o) => { const t = h.TK(o.t, 'hat'), fu = h.TK(o.fur, 'fur'); h.S('M62 70 C56 42 80 26 108 26 C136 26 158 42 152 66 Z', t, { sh: 7 }); if (o.point) h.S('M96 30 L110 4 L122 30 Z', t, { sh: 3 }); h.S('M54 78 C82 62 130 60 158 70 L156 52 C130 42 82 44 56 60 Z', fu, { sh: 5 }); h.S('M56 70 C52 86 54 100 62 110 L74 104 C70 94 70 84 72 74 Z', fu, { sh: 4 }); });
C.feathers = (h, o, ph) => { if (ph !== 'back') { h.S('M64 72 C88 56 128 54 152 64 L152 76 C128 66 88 68 64 84 Z', h.TK(o.band, 'gold'), { sh: 4 }); return; }
  const cols = o.colors ?? ['#e0483a', '#f0b23a', '#2fa37a'], n = o.n ?? 7;
  for (let i = 0; i < n; i++) { const a = (208 - i * (150 / (n - 1))) * Math.PI / 180, c = [104, 76], p0 = add(c, [Math.cos(a) * 34, -Math.sin(a) * 34]), p1 = add(c, [Math.cos(a) * (o.len ?? 84), -Math.sin(a) * (o.len ?? 84)]); h.S(limb([p0, add(p0, [(p1[0] - p0[0]) / 2 - 4, (p1[1] - p0[1]) / 2 - 4]), p1], 16, 5), tone(cols[i % cols.length]), { sh: 4 }); } };
C.plumes = back((h, o) => { const t = h.TK(o.t, 'crest'); h.S(limb([[96, 44], [70, -20], [14, 10]], 7, 2, 18), t, { sh: 2, hl: 2 }); h.S(limb([[112, 42], [112, -30], [50, -24]], 7, 2, 18), t, { sh: 2, hl: 2, far: true }); });
C.veil = front((h, o) => h.S('M62 86 C56 54 80 30 108 30 C136 30 154 50 152 76 C140 62 124 54 108 54 C92 54 78 64 74 82 C72 94 70 106 68 118 C62 108 60 96 62 86 Z', h.TK(o.t, 'veil'), { sh: 8, inner: bandIn(h, o.band) }));
C.nemes = (h, o, ph) => { const t = h.TK(o.t, 'cloth'), st = h.TK(o.stripe, 'gold'); let lines = ''; for (let i = 0; i < 7; i++) lines += `<path d="M30 ${44 + i * 14} L190 ${36 + i * 14}" stroke="${st.base}" stroke-width="5"/>`;
  if (ph === 'back') return h.S('M62 70 C50 96 46 122 50 146 L92 140 L96 120 L140 120 C148 108 150 94 150 82 Z', t, { sh: 8, inner: lines });
  h.S('M62 88 C54 56 80 32 108 32 C138 32 156 52 152 78 C140 64 124 56 108 56 C92 58 80 68 76 86 C74 100 74 116 76 130 C66 122 60 104 62 88 Z', t, { sh: 8, inner: lines }); };
C.skullcap = front((h, o) => h.S('M66 70 C64 42 86 28 108 28 C132 28 150 42 148 66 C138 58 130 64 124 60 L120 70 L114 60 C106 60 100 64 96 60 L92 72 L86 62 C78 62 72 66 66 70 Z', h.TK(o.t, 'bone'), { sh: 7, inner: `<ellipse cx="96" cy="46" rx="8" ry="9" fill="#2a1a30"/><ellipse cx="126" cy="44" rx="7" ry="8.5" fill="#2a1a30"/><path d="M110 50 L114 58 L106 58 Z" fill="#2a1a30"/>` }));
C.sundisc = (h, o, ph) => { if (ph === 'back') { h.halo(104, 26, 34, o.color ?? '#ffb84a', 0.75); h.S(disc(104, 26, 27), h.TK(o.t, 'gold'), { sh: 4, hl: 3, inner: `<circle cx="104" cy="26" r="20" fill="${o.core ?? '#e8552a'}"/><circle cx="97" cy="18" r="7" fill="#ff9a5a" opacity="0.7"/>` }); return; }
  h.S('M118 60 C112 50 114 40 122 36 C132 34 138 42 134 50 C132 46 128 44 125 46 C122 50 124 56 128 60 Z', h.TK(o.t, 'gold'), { sh: 3, hl: 2, inner: '<circle cx="127" cy="41" r="1.6" fill="#3a2408"/>' }); };
C.leaves = front((h, o) => { const t = h.TK(o.t, 'leaf'); for (const [x, y, r] of o.at ?? [[78, 52, -40], [98, 40, -15], [120, 38, 10], [140, 48, 35]]) h.at(`translate(${x} ${y}) rotate(${r})`, () => h.S('M0 6 C-8 -4 -6 -16 0 -22 C6 -16 8 -4 0 6 Z', t, { sh: 3, hl: 2 })); });
C.flower = front((h, o) => { const c = o.color ?? '#ff8ab0', x = o.x ?? 80, y = o.y ?? 56, r = o.r ?? 9; h.raw(`<g transform="translate(${x} ${y})"><circle r="${r}" fill="${c}" stroke="#2c1626" stroke-width="2"/><circle r="${r * 0.4}" fill="#ffe27a"/></g>`); });
C.longnose = front((h, o) => h.S(limb([[134, 96], [156, 98], [180, 94]], 11, 9), h.TK(o.t, 'skin'), { sh: 4, hl: 3 }));
C.dish = front((h, o) => { h.S('M62 74 C70 58 86 52 106 52 C126 52 142 58 150 68 C140 64 126 62 106 63 C88 64 74 70 64 82 Z', h.TK(o.t, 'hair'), { sh: 4 }); h.S(ell(106, 44, 28, 9), tone(o.color ?? '#bfe9ff'), { sh: 3, hl: 2 }); });
C.mian = front((h, o) => { const g = h.TK(o.t, 'gold'); h.S('M76 62 C92 50 126 48 144 56 L142 40 C124 34 94 36 80 46 Z', h.TK(o.cap, 'cloth'), { sh: 4 }); h.S('M56 42 L160 30 L162 42 L58 54 Z', g, { sh: 3, hl: 2 });
  h.raw(`<g stroke="${g.base}" stroke-width="2"><path d="M146 40 L146 62 M154 39 L154 60 M138 41 L138 60"/></g><g fill="${o.gem ?? '#e04a4a'}"><circle cx="146" cy="64" r="3"/><circle cx="154" cy="62" r="3"/><circle cx="138" cy="62" r="3"/></g>`); });
C.thirdeyes = front((h, o) => h.raw(`<g fill="${o.color ?? '#ff4a4a'}" stroke="#1c1218" stroke-width="1.5"><circle cx="96" cy="66" r="4"/><circle cx="116" cy="62" r="4"/><circle cx="136" cy="66" r="3.4"/></g>`));
C.whiskers = front((h, o) => { const t = h.TK(o.t, 'gold'); h.S(limb([[176, 96], [196, 84], [202, 56]], 4, 1.6), t, { sh: 1, hl: 1, rim: false }); h.S(limb([[172, 104], [190, 122], [208, 116]], 4, 1.6), t, { sh: 1, hl: 1, rim: false }); });
C.emblem = (h, o) => h.raw(emblem(o.kind, o.x, o.y, o.k ?? 1, o.c ?? h.T.gold.light));

// =================== DOS ===================
const CAPES = { long: 'M88 116 C64 128 46 168 40 216 C60 220 86 212 104 196 L104 122 Z', short: 'M86 118 C66 130 54 156 50 186 C68 182 86 172 98 156 Z',
  torn: 'M88 116 C64 128 46 168 36 214 L50 202 L56 220 L68 204 L76 222 L88 202 L98 214 L104 194 L104 122 Z', wide: 'M84 116 C52 126 34 168 26 218 C50 224 84 216 104 198 L104 122 Z',
  wind: 'M92 116 C66 112 38 122 10 146 C30 148 44 154 54 164 C40 170 30 182 24 198 C52 192 80 176 100 150 Z', high: 'M70 126 C56 110 54 86 62 70 C70 86 82 98 96 106 L104 122 L104 200 C84 214 60 220 40 216 C46 168 58 140 70 126 Z' };
C.cape = (h, o) => h.S(CAPES[o.len ?? 'long'], h.TK(o.t, 'cape'), { sh: 9, far: o.far, inner: o.inner ?? '' });
C.scarfTail = (h, o) => h.S(o.two ? 'M98 120 C72 102 44 98 10 108 C32 116 50 124 62 132 C44 136 28 148 18 164 C46 160 76 150 102 134 Z' : 'M94 120 C72 110 46 114 20 132 C42 136 58 140 70 146 C60 154 52 166 48 180 C70 170 88 154 100 134 Z', h.TK(o.t, 'scarf'), { sh: 7 });
const WINGS = {
  feather: ['M92 126 C72 104 48 76 22 44 C26 68 30 84 38 98 C26 94 16 96 8 92 C18 110 30 122 44 132 C34 134 26 138 20 142 C40 152 66 152 92 142 Z', 'M122 124 C140 102 160 78 184 48 C182 70 178 86 172 98 C182 94 190 96 196 94 C188 110 178 122 164 130 C150 136 136 136 122 132 Z'],
  bat: ['M92 124 C70 100 44 82 10 72 C22 88 26 100 26 114 C36 108 46 110 52 122 C58 112 68 114 74 126 C80 120 88 124 92 134 Z', 'M122 122 C142 100 166 84 198 76 C188 90 184 102 184 114 C174 108 164 110 158 122 C152 114 144 116 140 126 C134 122 126 124 122 132 Z'],
  small: ['M90 128 C74 116 58 100 46 82 C48 98 50 108 54 116 C46 114 40 116 36 114 C44 128 56 138 70 142 C78 142 86 138 90 136 Z', 'M124 126 C138 114 152 100 164 84 C162 98 160 108 156 116 C164 114 168 116 172 116 C164 128 152 136 140 138 C134 138 128 134 124 132 Z'],
  big: ['M94 128 C70 100 40 60 6 18 C12 50 18 72 28 90 C14 86 4 88 -6 84 C6 106 20 120 36 130 C24 132 14 138 8 144 C36 158 68 158 94 146 Z', 'M120 126 C142 98 168 62 198 24 C194 52 190 74 182 92 C194 88 202 90 210 88 C200 110 186 124 170 132 C154 140 136 140 120 134 Z'],
  down: ['M90 132 C66 138 44 156 30 186 C26 200 28 212 34 222 C40 206 50 196 62 190 C58 200 60 210 66 218 C74 198 86 182 98 168 Z', 'M124 132 C146 138 166 156 178 184 C182 198 180 210 176 220 C170 206 162 196 152 190 C154 200 152 208 148 216 C140 198 130 182 118 168 Z'],
};
C.wings = (h, o) => { const t = h.TK(o.t, 'wing'), W = WINGS[o.kind ?? 'feather'];
  if (o.glow) h.glow(`<path d="${W[0]}" fill="${o.glow}" opacity="0.7" filter="url(#glow)"/><path d="${W[1]}" fill="${o.glow}" opacity="0.5" filter="url(#glow)"/>`);
  const lines = o.kind === 'bat' ? `<path d="M90 126 L28 112 M90 126 L52 120 M90 126 L74 124" stroke="${t.shadow}" stroke-width="2.5" opacity="0.6"/>` : sf('M86 130 C66 112 46 92 30 66', t.shadow, 4, 0.35, 1) + sf('M82 138 C62 130 42 122 24 108', t.shadow, 3, 0.3, 1);
  if (!o.nearOnly) h.S(W[1], t, { sh: 7, far: true }); h.S(W[0], t, { sh: 8, inner: lines }); };
C.fairy = (h, o) => { const c = o.color ?? '#bfefff'; h.raw(`<g opacity="0.82"><path d="M92 126 C60 96 30 80 14 58 C10 86 40 124 92 138 Z" fill="${c}" stroke="#2c1626" stroke-width="2"/><path d="M92 136 C64 138 40 152 30 172 C54 172 78 160 94 144 Z" fill="${c}" stroke="#2c1626" stroke-width="2"/><path d="M90 128 C64 106 40 90 22 70" stroke="#fff" stroke-width="2" fill="none" opacity="0.7"/></g>`); };
C.tail = (h, o) => { const t = h.TK(o.t, 'tail'), k = o.kind ?? 'lizard';
  if (k === 'lizard') h.S(limb([[84, 176], [38, 184], [22, 226]], o.w ?? 22, 3), t, { sh: 5 });
  if (k === 'up') h.S(limb([[84, 176], [30, 190], [26, 110]], o.w ?? 16, 3), t, { sh: 5 });
  if (k === 'monkey') h.S(limb([[84, 178], [40, 196], [34, 146]], 9, 7), t, { sh: 3 });
  if (k === 'devil') { h.S(limb([[84, 178], [40, 200], [30, 150]], 7, 4), t, { sh: 3 }); h.S('M30 152 L18 134 L40 136 Z', t, { sh: 2 }); }
  if (k === 'fox') { const n = o.n ?? 1; for (let i = n - 1; i >= 0; i--) h.at(`rotate(${-(i - (n - 1) / 2) * 26 - (n > 1 ? 18 : 0)} 86 178)`, () => h.S('M88 176 C60 166 30 172 12 198 C8 214 18 226 30 224 C26 210 40 200 60 196 C74 194 84 190 90 184 Z', t, { sh: 6, inner: `<path d="M12 198 C8 214 18 226 30 224 C26 212 34 204 44 200 C34 196 22 196 12 198 Z" fill="${(h.T.tip ?? tone('#fff6e6')).base}"/>` })); }
  if (k === 'scorpion') { h.S(limb([[86, 174], [26, 172], [26, 104]], 17, 13), t, { sh: 5 }); h.S(limb([[26, 108], [28, 44], [82, 26]], 13, 8), t, { sh: 4 }); h.S('M78 16 L112 34 L80 36 Z', h.TK(o.tipT, 'bone'), { sh: 3 }); }
  if (k === 'feathers') for (const [c2, e] of [[[50, 190], [20, 226]], [[44, 176], [8, 200]], [[52, 164], [14, 168]]]) h.S(limb([[86, 172], c2, e], 15, 4), t, { sh: 4 });
};
C.shell = (h, o) => { const t = h.TK(o.t, 'shell'); h.S(ell(82, 150, 42, 46), t, { sh: 9, inner: `<path d="M82 106 L82 196 M44 136 L120 136 M46 166 L118 166" stroke="${t.shadow}" stroke-width="3" opacity="0.7"/>` }); };
C.halo = (h, o) => { h.glow(`<ellipse cx="104" cy="${o.y ?? 26}" rx="38" ry="12" fill="${o.color ?? '#ffe27a'}" opacity="0.8" filter="url(#glow)"/>`); h.S(ring(104, o.y ?? 26, 34, 10, 5), h.TK(o.t, 'gold'), { eo: true, sh: 2, hl: 1.5 }); };
C.sun = (h, o) => { const t = h.TK(o.t, 'gold'), c = o.color ?? '#ffcf5a', R = o.r ?? 52; let rays = '';
  for (let i = 0; i < 12; i++) { const a = i * 30 * Math.PI / 180; rays += `M${f(104 + Math.cos(a - 0.1) * (R - 2))} ${f(74 + Math.sin(a - 0.1) * (R - 2))} L${f(104 + Math.cos(a) * (R + 18))} ${f(74 + Math.sin(a) * (R + 18))} L${f(104 + Math.cos(a + 0.1) * (R - 2))} ${f(74 + Math.sin(a + 0.1) * (R - 2))} Z `; }
  h.halo(104, 74, R + 14, c, 0.6); h.S(rays, t, { sh: 3, hl: 2 }); h.S(ring(104, 74, R, R, 7), t, { eo: true, sh: 4 }); };
C.drums = (h, o) => { const t = h.TK(o.t, 'drum'), g = h.T.gold, pts = arcPts(104, 96, 84, 84, 172, 368, 5);
  h.S(ring(104, 96, 84, 84, 5), g, { eo: true, sh: 2, hl: 1.5 });
  for (const p of pts) h.S(disc(p[0], p[1], 17), t, { sh: 5, inner: `<circle cx="${f(p[0])}" cy="${f(p[1])}" r="11" fill="none" stroke="${g.base}" stroke-width="3"/><circle cx="${f(p[0])}" cy="${f(p[1])}" r="4" fill="${g.base}"/>` }); };
C.spiderBack = (h, o) => { const t = h.TK(o.t, 'tail'); for (const [p, far] of [[[[122, 136], [160, 40], [192, 112]], 1], [[[124, 142], [186, 86], [198, 176]], 1], [[[90, 136], [50, 34], [16, 104]], 0], [[[88, 142], [22, 84], [6, 176]], 0]]) h.S(limb(p, 10, 2, 16), t, { sh: 3, far: !!far }); };
C.banner = (h, o) => { const t = h.TK(o.t, 'cape'); h.S(bar([86, 170], [72, 4], 5), h.T.wood, { sh: 2, hl: 1.5 }); h.S('M70 8 L30 14 L34 74 L74 66 Z', t, { sh: 6, inner: o.emblem ? emblem(o.emblem, 52, 40, 1.3, o.ec ?? '#ffd76a') : '' }); };
C.windbag = (h, o) => { const t = h.TK(o.t, 'bag'), a = o.a ?? [40, 168], b = o.b ?? [176, 162], top = o.top ?? [108, -6];
  h.S(limb([a, [a[0] - 14, 34], top], 12, 46, 20), t, { sh: 8 }); h.S(limb([b, [b[0] + 14, 34], top], 12, 46, 20), t, { sh: 8 });
  h.S(ell(top[0], top[1] + 2, 30, 24), t, { sh: 8, hl: 5, inner: sf(`M${top[0] - 22} ${top[1] + 6} C${top[0] - 8} ${top[1] - 10} ${top[0] + 10} ${top[1] - 10} ${top[0] + 22} ${top[1] + 4}`, t.light, 6, 0.5, 2) });
  h.raw(`<g fill="none" stroke="${t.shadow}" stroke-width="2.6" stroke-linecap="round" opacity="0.6"><path d="M${a[0] - 4} ${a[1] - 60} q10 6 20 0 M${b[0] - 14} ${b[1] - 60} q10 6 20 0"/></g>`);
  h.S(disc(a[0], a[1] - 8, 9), h.T.gold, { sh: 3 }); h.S(disc(b[0], b[1] - 8, 8), h.T.gold, { sh: 3 });
  h.raw(`<g fill="none" stroke="#f4fffb" stroke-width="5" stroke-linecap="round"><path d="M${a[0] - 6} ${a[1] + 8} C${a[0] - 30} ${a[1] + 14} ${a[0] - 34} ${a[1] - 16} ${a[0] - 16} ${a[1] - 16} C${a[0] - 6} ${a[1] - 14} ${a[0] - 8} ${a[1] - 2} ${a[0] - 16} ${a[1] - 4}"/><path d="M${b[0] + 8} ${b[1] + 10} C${b[0] + 30} ${b[1] + 16} ${b[0] + 34} ${b[1] - 12} ${b[0] + 18} ${b[1] - 12} C${b[0] + 8} ${b[1] - 10} ${b[0] + 10} ${b[1]} ${b[0] + 18} ${b[1] - 2}"/></g>`); };
C.cloud = (h, o) => { const c = o.color ?? '#f4f8ff', y = h.ground - 228; h.raw(`<g opacity="0.95" transform="translate(0 ${y})"><path d="M36 226 C22 226 20 208 34 206 C36 192 58 190 64 202 C74 192 96 194 100 206 C112 198 132 202 134 214 C150 208 170 214 172 226 Z" fill="${c}" stroke="#2c1626" stroke-width="2.5" stroke-linejoin="round"/></g>`); };
C.flames = (h, o) => { const t = h.TK(o.t, 'flame'); h.glow(`<path d="M60 190 C40 150 50 110 86 96 C70 130 80 160 100 186 Z" fill="${t.base}" opacity="0.7" filter="url(#glow)"/>`); h.S('M98 186 L62 190' + saw([[62, 190], [58, 168], [64, 146], [78, 128], [98, 122]], 30, [-14, -12]) + ' Z', t, { sh: 6, inner: `<path d="M94 132 C80 140 72 156 72 176" stroke="${t.light}" stroke-width="8" fill="none" opacity="0.7"/>` }); };
C.quills = (h, o) => h.S('M96 190 L62 192' + saw([[62, 192], [56, 172], [60, 150], [72, 132], [92, 120]], o.len ?? 26, [-10, -6]) + ' Z', h.TK(o.t, 'hair'), { sh: 6 });
C.roundBack = (h, o) => { const t = h.TK(o.t, 'wood'); h.S(disc(72, 150, 40), t, { sh: 8, inner: `<circle cx="72" cy="150" r="31" fill="${h.TK(o.face, 'cloth').base}"/><circle cx="72" cy="150" r="8" fill="${h.T.steel.base}" stroke="${t.shadow}" stroke-width="2"/>` }); };
C.net = (h, o) => { const t = h.TK(o.t, 'bone'); h.S('M70 116 C48 124 40 150 46 176 C60 184 80 180 92 168 C98 150 94 128 84 116 Z', t, { sh: 6, inner: `<path d="M50 130 L92 170 M46 152 L80 182 M62 118 L96 150 M92 126 L50 170 M80 116 L44 150 M96 144 L66 182" stroke="${t.shadow}" stroke-width="1.6" opacity="0.7"/>` }); };

// =================== COU / ÉPAULES ===================
C.scarf = (h, o) => h.S('M74 114 C92 126 122 126 140 112 L142 126 C122 140 92 140 72 128 Z', h.TK(o.t, 'scarf'), { sh: 5 });
C.maskScarf = (h, o) => h.S('M72 108 C92 122 124 122 146 106 L148 124 C124 140 92 140 70 126 Z', h.TK(o.t, 'scarf'), { sh: 5 });
C.pad = (h, o) => { const x = h.B.sw - 32; h.at(`translate(${-x} 0)`, () => { h.S('M62 124 C66 108 90 104 104 118 C104 132 94 140 80 142 C70 140 64 132 62 124 Z', h.TK(o.t, 'steel'), { sh: 6, inner: o.inner ?? '' }); if (o.spike) h.S('M70 114 L66 92 L84 108 Z', h.TK(o.spikeT, 'bone'), { sh: 3 }); }); };
C.padFar = (h, o) => { const x = h.B.sw - 32; h.at(`translate(${x} 0)`, () => h.S('M116 118 C126 106 146 108 152 122 C150 132 142 138 130 138 C120 136 116 128 116 118 Z', h.TK(o.t, 'steel'), { sh: 5, far: true })); };
C.fur = (h, o) => { const x = h.B.sw - 32; h.S(`M${64 - x} 120 C84 108 128 108 ${148 + x} 118 L${153 + x} 136 L${143 + x} 130 L137 138 L128 130 L120 140 L110 131 L101 140 L93 131 L85 139 L${78 - x} 130 L${66 - x} 136 Z`, h.TK(o.t, 'fur'), { sh: 6 }); };
C.beads = (h, o) => { const t = h.TK(o.t, 'gold'); for (let i = 0; i < 7; i++) { const u = i / 6, x = 78 + u * 58, y = 124 + Math.sin(u * Math.PI) * 12; h.S(disc(x, y, o.r ?? 4.6), t, { sh: 2, hl: 1.5, rim: false }); } };
C.collar = (h, o) => h.S('M70 116 C90 126 124 126 144 114 L150 130 C126 142 90 142 66 130 Z', h.TK(o.t, 'gold'), { sh: 5, inner: (o.stripes ? `<path d="M66 124 C90 134 124 134 150 122" stroke="${h.TK(o.stripes).base}" stroke-width="4" fill="none"/>` : '') + (o.gem ? `<circle cx="110" cy="130" r="5" fill="${o.gem}"/>` : '') });
C.rope = (h, o) => h.S(limb([[72, 116], [106, 150], [146, 112]], 7, 7), h.TK(o.t, 'bone'), { sh: 2, hl: 2 });
module.exports = { emblem, HAIR, HAIRBACK, CAPES, WINGS, HOODS, HOOD_OPEN, CAP, FRINGE };
