// Têtes et visages (version 6). Têtes humaines : 5 mâchoires, oreille, nez, bouches et yeux à expression.
// Têtes d'animaux : la tête ET le museau forment une seule courbe continue (pas de museau rajouté).
const K = require('./fig6.cjs');
const { LIB, f, pt, poly, add, limb, disc, ell, saw, mix, sf, blob, tone } = K;

// ---------- yeux ----------
const SLOPE = { angry: [0.46, 0.02], calm: [0.36, 0.24], fierce: [0.52, -0.06], sly: [0.12, 0.12], tired: [0.04, 0.04], sad: [0.06, 0.4], soft: [0.3, 0.3] };
/** Un œil. dir = +1 : le coin intérieur (côté nez) est à droite. Styles : angry, calm, fierce, sly, tired, sad, soft, wide, closed, happy, dot, glow. */
function eye(id, cx, cy, w, hh, dir, E) {
  const st = E.style ?? 'angry', col = E.color ?? '#5a3a20', lid = E.lid ?? '#2a1424';
  const ox = cx - dir * (w / 2 + 2), ix = cx + dir * (w / 2 + 2);
  const lash = E.lash ? `<path d="M${f(cx - dir * w / 2)} ${f(cy - hh * 0.2)} l${f(-dir * 6)} ${f(-4.5)}" stroke="${lid}" stroke-width="2.2" stroke-linecap="round"/>` : '';
  if (st === 'closed' || st === 'happy') { const k = st === 'happy' ? -1 : 1; return `<path d="M${f(cx - w / 2)} ${f(cy + (k < 0 ? 2 : -1))} Q${f(cx)} ${f(cy + k * hh * 0.6)} ${f(cx + w / 2)} ${f(cy + (k < 0 ? 2 : -1))}" stroke="${lid}" stroke-width="2.8" fill="none" stroke-linecap="round"/>` + lash; }
  if (st === 'dot') return `<ellipse cx="${f(cx)}" cy="${f(cy)}" rx="${f(w * 0.24)}" ry="${f(hh * 0.36)}" fill="#170a12"/><circle cx="${f(cx - w * 0.08)}" cy="${f(cy - hh * 0.14)}" r="${f(w * 0.08)}" fill="#fff"/>`;
  const wide = st === 'wide';
  const lens = wide ? `M${f(cx - w / 2)} ${f(cy)} A${f(w / 2)} ${f(hh * 0.62)} 0 1 0 ${f(cx + w / 2)} ${f(cy)} A${f(w / 2)} ${f(hh * 0.62)} 0 1 0 ${f(cx - w / 2)} ${f(cy)} Z`
    : `M${f(cx - w / 2)} ${f(cy)} Q${f(cx)} ${f(cy - hh * 0.8)} ${f(cx + w / 2)} ${f(cy)} Q${f(cx)} ${f(cy + hh * 0.8)} ${f(cx - w / 2)} ${f(cy)} Z`;
  const [so, si] = SLOPE[st] ?? SLOPE.angry;
  let s = `<defs><clipPath id="${id}"><path d="${lens}"/></clipPath></defs>`;
  if (st === 'glow' || E.glow) s += `<ellipse cx="${f(cx)}" cy="${f(cy)}" rx="${f(w * 0.8)}" ry="${f(hh * 0.7)}" fill="${col}" opacity="0.55" filter="url(#g2)"/>`;
  s += `<path d="${lens}" fill="${E.sclera ?? (st === 'glow' ? col : '#fbf6ef')}"${wide ? ` stroke="${lid}" stroke-width="1.8"` : ''}/><g clip-path="url(#${id})">`;
  if (st === 'glow') s += `<ellipse cx="${f(cx)}" cy="${f(cy + 1)}" rx="${f(w * 0.3)}" ry="${f(hh * 0.34)}" fill="#fff" opacity="0.85"/>`;
  else {
    const r = hh * (wide ? 0.3 : st === 'fierce' ? 0.38 : 0.46), dx = dir * w * (st === 'sly' ? 0.2 : 0.1) + (E.look ?? 0);
    s += `<circle cx="${f(cx + dx)}" cy="${f(cy + 0.5)}" r="${f(r)}" fill="${col}"/>`;
    s += E.slit ? `<ellipse cx="${f(cx + dx)}" cy="${f(cy + 0.5)}" rx="${f(w * 0.07)}" ry="${f(r * 0.92)}" fill="#170a12"/>` : `<circle cx="${f(cx + dx)}" cy="${f(cy + 0.8)}" r="${f(r * 0.52)}" fill="#170a12"/>`;
    s += `<circle cx="${f(cx + dx - w * 0.14)}" cy="${f(cy - hh * 0.14)}" r="${f(w * 0.1)}" fill="#fff"/>`;
  }
  if (!wide) s += `<path d="M${f(ox)} ${f(cy - hh)} L${f(ix)} ${f(cy - hh)} L${f(ix)} ${f(cy - hh * si)} L${f(ox)} ${f(cy - hh * so)} Z" fill="${lid}"/>`;
  s += '</g>';
  if (!wide) s += `<path d="M${f(ox + dir * 2)} ${f(cy - hh * so)} L${f(ix - dir * 2)} ${f(cy - hh * si)}" stroke="${lid}" stroke-width="2.2" stroke-linecap="round"/>`;
  if (st === 'tired') s += `<path d="M${f(cx - w * 0.4)} ${f(cy + hh * 0.7)} Q${f(cx)} ${f(cy + hh * 0.95)} ${f(cx + w * 0.4)} ${f(cy + hh * 0.7)}" stroke="${lid}" stroke-width="1.4" fill="none" opacity="0.5"/>`;
  return s + lash;
}
/** Sourcil : suit la paupière par défaut ; shape = 'arch' | 'flat' | 'worry' ; lift le remonte. */
function brow(cx, cy, w, hh, dir, E, Bw, col, far) {
  if (Bw.shape === 'none') return '';
  const st = E.style ?? 'angry'; let [so, si] = SLOPE[st] ?? (st === 'wide' ? [0.5, 0.5] : [0.3, 0.3]);
  if (Bw.shape === 'flat') { so = 0.3; si = 0.3; } if (Bw.shape === 'worry') { so = 0.1; si = 0.5; } if (Bw.shape === 'angry') { so = 0.5; si = 0; }
  const lift = (Array.isArray(Bw.lift) ? Bw.lift[far ? 1 : 0] : Bw.lift) ?? 0, k = (Bw.k ?? 5) * (far ? 0.86 : 1);
  const a = [cx - dir * (w / 2 + 4), cy - hh * so - 8 - lift], b = [cx + dir * (w / 2 + 2), cy - hh * si - 6 - lift];
  const d = Bw.shape === 'arch' ? `M${pt(a)} Q${f((a[0] + b[0]) / 2)} ${f(Math.min(a[1], b[1]) - 6)} ${pt(b)}` : `M${pt(a)} L${pt(b)}`;
  return `<path d="${d}" stroke="${col}" stroke-width="${f(k)}" stroke-linecap="round" fill="none"/>`;
}
// ---------- bouches (autour de 120, 108) ----------
function mouth(st, x, y, col = '#5a2a22') {
  const T = (d, extra = '') => `<g transform="translate(${f(x)} ${f(y)})">${d}${extra}</g>`;
  const line = (d, w = 2.4) => `<path d="${d}" stroke="${col}" stroke-width="${w}" fill="none" stroke-linecap="round"/>`;
  switch (st) {
    case 'none': return '';
    case 'smirk': return T(line('M-8 0 C-2 2 4 2 10 -3'));
    case 'smile': return T(line('M-8 -2 C-3 3 5 3 10 -3'));
    case 'frown': return T(line('M-8 2 C-3 -2 5 -2 10 1'));
    case 'o': return T(`<ellipse cx="1" cy="0" rx="4.2" ry="5.2" fill="#4a141c" stroke="${col}" stroke-width="1.4"/>`);
    case 'grin': return T(`<path d="M-10 -3 C-4 -1 6 -1 12 -5 C11 3 4 6 -2 6 C-7 5 -10 2 -10 -3 Z" fill="#4a141c" stroke="${col}" stroke-width="1.4" stroke-linejoin="round"/><path d="M-8 -2.2 C-3 -0.4 5 -0.4 10 -3.4 L9 -0.4 C4 1.6 -2 1.6 -7 0.4 Z" fill="#fff8ee"/>`);
    case 'shout': return T(`<path d="M-10 -5 C-4 -7 6 -7 12 -6 C13 4 7 10 0 10 C-6 10 -10 4 -10 -5 Z" fill="#4a141c" stroke="${col}" stroke-width="1.4" stroke-linejoin="round"/><path d="M-8 -4.6 C-3 -6 5 -6 10 -5.2 L9.6 -2.4 C5 -3 -3 -3 -7.6 -2 Z" fill="#fff8ee"/><ellipse cx="1" cy="6" rx="5" ry="2.6" fill="#c8505a"/>`);
    case 'gritted': return T(`<path d="M-10 -4 L12 -6 L12 3 L-10 5 Z" fill="#fff8ee" stroke="${col}" stroke-width="1.5" stroke-linejoin="round"/><path d="M-10 0.5 L12 -1.5 M-4.5 -4.5 L-4.5 4.5 M1 -5 L1 4 M6.5 -5.5 L6.5 3.5" stroke="${col}" stroke-width="1.1"/>`);
    case 'fang': return T(line('M-8 0 C-2 2 4 2 10 -1') + `<path d="M3 1 L5.5 8 L8 0.4 Z" fill="#fff8ee" stroke="${col}" stroke-width="0.9"/>`);
    default: return T(line('M-7 0.5 L8 -0.5'));
  }
}
function nose(st, col) {
  if (st === 'none') return '';
  if (st === 'button') return `<path d="M121 96 C127 95 130 100 126 103" stroke="${col}" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  if (st === 'hook') return `<path d="M120 90 C130 92 135 100 127 105" stroke="${col}" stroke-width="2.2" fill="none" stroke-linecap="round"/>`;
  return `<path d="M122 99 L127 101" stroke="${col}" stroke-width="2" stroke-linecap="round"/>`;
}
// ---------- barbes et moustaches ----------
const BEARD = {
  full: 'M70 94 C84 104 96 98 106 104 C118 98 136 102 148 92 C152 112 142 136 120 144 C96 144 74 124 70 94 Z',
  long: 'M70 94 C84 104 96 98 106 104 C118 98 136 102 148 92 C150 118 140 150 118 174 C98 150 74 124 70 94 Z',
  fork: 'M70 94 C84 104 96 98 106 104 C118 98 136 102 148 92 C150 116 142 140 134 162 L122 140 L110 166 C92 146 74 124 70 94 Z',
  goat: 'M108 110 C118 114 128 112 136 107 C134 124 126 136 121 142 C114 132 109 121 108 110 Z',
  braids: 'M94 108 C104 118 126 118 136 108 C139 120 135 130 131 137 L130 160 L122 168 L117 142 L111 142 L108 168 L99 160 L100 137 C94 129 91 119 94 108 Z',
  short: 'M92 108 C104 118 126 118 138 106 C140 120 134 132 128 142 L122 134 L117 148 L110 135 L103 145 C96 135 91 122 92 108 Z',
  bushy: 'M66 92 C82 104 96 98 106 104 C118 98 138 102 152 90 C158 118 152 148 136 168 C126 180 104 182 92 172 C76 156 64 122 66 92 Z',
  chin: 'M100 112 C112 118 128 116 138 108 C138 120 130 128 120 130 C110 128 102 122 100 112 Z',
  curly: 'M70 94 C84 104 96 98 106 104 C118 98 136 102 148 92 C154 104 152 114 146 120 C150 130 144 140 136 142 C136 152 128 160 118 158 C108 160 100 152 98 142 C88 140 82 130 84 122 C74 116 68 106 70 94 Z',
  ice: 'M70 94 C84 104 96 98 106 104 C118 98 136 102 148 92 L146 124 L138 112 L134 148 L124 122 L118 166 L110 126 L100 150 L96 118 L84 132 L82 110 Z',
  thin: 'M114 112 C119 115 126 114 130 110 C132 124 125 136 127 150 C128 160 124 168 120 176 C120 162 113 150 115 136 C116 126 114 120 114 112 Z',
};
function beard(h, kind, t) {
  h.S(BEARD[kind], t, { sh: 8, inner: ['goat', 'chin', 'thin', 'ice', 'braids', 'short'].includes(kind) ? '' : sf('M96 112 C104 118 114 118 124 110', t.shadow, 4, 0.5, 1) });
  if (kind === 'bushy') h.raw(`<path d="M96 150 C104 156 116 156 124 150 M100 134 C108 140 116 140 122 134" stroke="${t.shadow}" stroke-width="2.4" fill="none" opacity="0.55" stroke-linecap="round"/>`);
}
function mustache(h, kind, t) {
  if (kind === 'droop') { h.S(limb([[116, 103], [106, 108], [102, 128]], 5, 2), t, { sh: 1, hl: 1, rim: false }); h.S(limb([[126, 102], [138, 106], [142, 126]], 5, 2), t, { sh: 1, hl: 1, rim: false }); }
  if (kind === 'handle') h.S('M120 104 C114 100 104 102 98 96 C98 104 106 110 118 108 C126 110 136 108 142 98 C136 102 128 100 120 104 Z', t, { sh: 2, hl: 2, rim: false });
  if (kind === 'walrus') h.S('M100 100 C110 96 132 96 142 100 C146 108 142 118 136 120 C132 112 126 108 120 108 C114 108 108 112 106 120 C98 118 96 108 100 100 Z', t, { sh: 3, hl: 2, rim: false });
}

// ---------- tête humaine ----------
const JAW = {
  round: 'C148 98 139 112 124 118 C114 121 100 121 90 117 C74 111 64 97 64 79',
  square: 'C148 100 147 113 136 120 C124 125 102 125 90 121 C74 114 64 99 64 79',
  point: 'C148 96 140 110 127 121 C121 126 112 127 105 123 C84 116 64 100 64 79',
  chubby: 'C151 98 147 114 131 121 C117 126 98 126 86 121 C69 113 62 98 64 79',
  long: 'C148 100 143 116 129 126 C119 131 107 130 96 125 C76 115 64 100 64 79',
};
const headPath = (jaw) => `M106 40 C131 40 148 57 148 81 ${JAW[jaw] ?? JAW.round} C64 56 82 40 106 40 Z`;
/** Ce qui se peint DANS la tête (ombre, masque, bandeau, peintures) : toujours d'un bord à l'autre. */
function headInner(h, o) {
  const T = h.T; let s = blob('M140 60 C152 76 152 100 138 116 L164 126 L164 54 Z', T.skin.shadow, 0.45, 3);
  if (o.stubble) s += `<path d="M66 96 C84 112 124 114 150 92 L150 132 L66 132 Z" fill="${mix(T.skin.base, h.TK(o.stubble).base, 0.45)}"/>`;
  if (o.mask) { const mt = h.TK(o.maskT, 'cloth'), y = o.mask; s += `<path d="M40 ${y} L170 ${y - 6} L170 140 L40 140 Z" fill="${mt.base}"/><path d="M40 ${y} L170 ${y - 6}" stroke="${mt.shadow}" stroke-width="2" opacity="0.7"/>`; }
  if (o.band) { const b = o.band, t = h.TK(b.t, 'gold'), y = b.y ?? 62, k = b.k ?? 10; s += `<path d="M40 ${y + 8} C84 ${y - 4} 122 ${y - 4} 170 ${y + 10} L170 ${y + 10 + k} C122 ${y - 4 + k} 84 ${y - 4 + k} 40 ${y + 8 + k} Z" fill="${t.base}"/><path d="M40 ${y + 8 + k} C84 ${y - 4 + k} 122 ${y - 4 + k} 170 ${y + 10 + k}" stroke="${t.shadow}" stroke-width="1.8" fill="none" opacity="0.8"/>` + (b.gem ? `<circle cx="126" cy="${y + 4}" r="4.5" fill="${b.gem}" stroke="${t.shadow}" stroke-width="1.4"/>` : ''); }
  return s + (o.paint ?? '');
}
/** Yeux, sourcils, nez, bouche aux places données (P = positions). */
function features(h, o, P) {
  const T = h.T, E = o.eyes ?? {}, Bw = o.brow ?? {}, id = h.s.id;
  const lidC = E.lid ?? P.lid ?? '#2a1424', bc = h.TK(Bw.t ?? o.browT, 'hair').shadow, EE = { ...E, lid: lidC };
  let s = '';
  if (E.style === 'wink') s += eye(`e${id}n`, P.n[0], P.n[1], P.n[2], P.n[3], 1, { ...EE, style: 'happy' }) + eye(`e${id}f`, P.f[0], P.f[1], P.f[2], P.f[3], -1, { ...EE, style: 'angry' });
  else if (E.style !== 'none') s += eye(`e${id}n`, P.n[0], P.n[1], P.n[2], P.n[3], 1, EE) + (P.f ? eye(`e${id}f`, P.f[0], P.f[1], P.f[2], P.f[3], -1, EE) : '');
  if (E.style !== 'none') { const ES = E.style === 'wink' ? { style: 'angry' } : E; s += brow(P.n[0], P.n[1], P.n[2], P.n[3], 1, ES, Bw, Bw.c ?? P.browC ?? bc, false) + (P.f ? brow(P.f[0], P.f[1], P.f[2], P.f[3], -1, ES, Bw, Bw.c ?? P.browC ?? bc, true) : ''); }
  if (o.scar) s += `<path d="M96 70 L112 104" stroke="${mix(T.skin.base, '#7a2a2a', 0.6)}" stroke-width="2.6" stroke-linecap="round"/>`;
  if (o.blush) s += `<ellipse cx="94" cy="102" rx="8" ry="4.5" fill="${o.blush}" opacity="0.45"/>`;
  if (P.nose !== false) s += nose(o.nose ?? 'tick', T.skin.shadow);
  if (P.mouth) s += mouth(o.mouth ?? 'flat', P.mouth[0], P.mouth[1], o.mouthC ?? P.mouthC ?? '#5a2a22');
  if (o.tusks) s += `<g transform="translate(${P.mouth[0] - 120} ${P.mouth[1] - 108})"><path d="M108 112 L111 ${o.tusks === 'big' ? 94 : 100} L116 111 Z M129 110 L133 ${o.tusks === 'big' ? 93 : 99} L137 109 Z" fill="#fff8e0" stroke="#3a1c1c" stroke-width="1.1" stroke-linejoin="round"/></g>`;
  h.raw(s);
}
LIB.head.human = (h, o) => {
  const { S, T } = h, my = (o.jaw === 'long' ? 4 : 0) + (o.my ?? 0);
  S(headPath(o.jaw), T.skin, { sh: 9, hl: 6, inner: headInner(h, o) });
  if (o.ear !== false) S('M72 82 C62 79 57 88 60 96 C63 103 70 102 73 96 Z', T.skin, { sh: 3, hl: 2, inner: `<path d="M68 86 C63 88 63 94 67 97" stroke="${T.skin.shadow}" stroke-width="1.6" fill="none" opacity="0.7"/>` });
  if (o.nose === 'big') S('M119 91 C130 88 138 97 134 105 C130 110 120 108 118 102 Z', tone(mix(T.skin.base, '#c8503a', 0.25)), { sh: 3, hl: 3, rim: false });
  features(h, { ...o, nose: o.nose === 'big' ? 'none' : o.nose }, { n: [103, 88 + (o.ey ?? 0), 20 * (o.eyeK ?? 1), 16 * (o.eyeK ?? 1)], f: [134, 88 + (o.ey ?? 0), 13.5 * (o.eyeK ?? 1), 15 * (o.eyeK ?? 1)], mouth: o.mask || ['full', 'long', 'fork', 'bushy', 'curly', 'ice'].includes(o.beard) ? null : [120, 108 + my] });
  if (o.beard) beard(h, o.beard, h.TK(o.beardT, 'hair'));
  if (o.mustache) mustache(h, o.mustache, h.TK(o.beardT, 'hair'));
};
LIB.head.cyclops = (h, o) => {
  const { S, T } = h; S(headPath(o.jaw ?? 'square'), T.skin, { sh: 9, hl: 6, inner: headInner(h, o) });
  S('M72 82 C62 79 57 88 60 96 C63 103 70 102 73 96 Z', T.skin, { sh: 3, hl: 2 });
  features(h, o, { n: [120, 82, 30, 24], f: null, mouth: [122, 110] });
};
LIB.head.goblin = (h, o) => {
  const { S, T } = h, lid = mix(T.skin.base, '#140c10', 0.72);
  S('M142 70 C154 56 170 48 184 48 C178 62 166 76 150 86 Z', T.skin, { far: true });
  S('M104 46 C130 44 150 60 150 83 C150 100 140 114 124 119 C112 122 98 121 88 116 C72 109 62 97 62 82 C62 60 80 46 104 46 Z', T.skin, { sh: 9, hl: 6, inner: headInner(h, o) });
  features(h, { ...o, nose: 'none' }, { n: [103, 85, 20, 14], f: [134, 85, 13.5, 13], mouth: null, lid, browC: lid });
  h.raw(`<path d="M110 107 C120 112 132 110 142 103" stroke="#1c2a10" stroke-width="2.4" fill="none" stroke-linecap="round"/><path d="M114 109.5 L118 100 L123 110.5 Z" fill="#fff8e0" stroke="#1c2a10" stroke-width="1"/>`);
  S('M138 88 C150 86 166 92 174 103 C162 106 148 105 138 100 Z', T.skin, { sh: 4, hl: 3, rim: false });
  S('M72 80 C56 66 36 58 16 60 C28 76 46 94 70 102 Z', T.skin, { sh: 6, inner: sf('M64 86 C50 76 38 70 26 67', T.skin.shadow, 3, 0.5, 1) });
};

// ---------- têtes d'animaux : une seule courbe du crâne au bout du museau ----------
const BACK = 'C64 58 80 43 104 42 Z'; // l'arrière du crâne, commun
const beastLid = (h) => mix(h.T.skin.base, '#140c10', 0.74);
const SPECIES = {
  // chacal, loup : museau long et fin, légèrement plongeant
  jackal: { d: 'M98 40 C116 38 132 46 142 60 C148 68 156 74 166 79 C178 84 190 90 192 97 C193 103 188 106 180 106 C168 107 156 109 146 114 C136 119 124 122 112 122 C98 122 86 117 78 108 L64 112 L70 97 C64 84 66 66 74 54 C80 46 88 41 98 40 Z',
    n: [108, 80, 18, 14], f: [135, 77, 12, 12.5], nose: [187, 97, 5.2, 4.6], mouth: 'M189 103 C176 104 162 106 149 112', patch: 'M152 96 C166 94 182 96 192 100 L192 124 L122 126 C132 112 142 100 152 96 Z' },
  // lionne : museau court et large, menton fort
  lion: { d: 'M104 40 C126 38 142 46 151 58 C159 67 172 74 182 84 C188 90 188 100 184 106 C180 113 172 118 160 120 C150 124 138 125 126 124 C112 126 98 124 88 119 L72 126 L77 111 L58 112 L67 97 C61 88 61 78 64 70 C68 53 84 41 104 40 Z',
    n: [106, 82, 20, 15], f: [135, 79, 12.5, 13.5], noseD: 'M172 82 C178 80 186 85 187 91 C185 96 179 96 175 92 Z', mouth: 'M181 95 L179 104 C173 111 163 111 157 106 M179 104 C183 108 187 106 187 102', patch: 'M152 98 C162 90 176 88 190 94 L190 128 L130 128 C136 114 142 104 152 98 Z' },
  // taureau : mufle massif
  bull: { d: 'M70 62 C78 47 94 40 112 40 C130 40 145 48 152 61 C158 70 170 76 182 82 C193 87 198 98 196 108 C193 119 182 125 168 126 C152 128 136 128 122 126 C100 128 78 120 68 104 C61 92 62 74 70 62 Z',
    n: [106, 82, 20, 14], f: [136, 79, 12.5, 13], nostril: [[188, 99], [178, 97]], mouth: 'M193 114 C182 119 168 119 156 114', patch: 'M154 97 C166 88 188 87 198 98 L198 130 L138 130 C140 115 144 103 154 97 Z' },
  // requin : museau pointu vers l'avant, gueule dessous
  shark: { d: 'M100 40 C122 36 142 44 156 58 C168 66 182 76 190 86 C193 90 192 94 188 96 C176 106 160 117 140 120 C116 124 64 112 64 80 C64 56 80 42 100 40 Z',
    n: [122, 77, 18, 14], f: [150, 70, 12.5, 11.5], teeth: [[182, 100], [162, 113], [138, 114], 7], belly: 'M194 92 C176 100 150 104 120 102 C100 100 80 96 60 90 L60 130 L194 130 Z' },
  // lézard, salamandre : museau plat et long, grande bouche
  lizard: { d: 'M66 86 C65 70 76 56 92 53 C96 44 110 39 121 45 C124 47 127 49 128 52 C132 45 143 43 149 49 C153 53 154 59 152 64 C160 69 170 73 178 77 C188 82 194 89 192 97 C190 104 180 107 168 108 C152 110 138 117 124 121 C102 125 67 112 66 86 Z',
    n: [110, 68, 20, 15], f: [140, 63, 12.5, 13], nostril: [[184, 87]], mouth: 'M192 98 C174 100 150 103 126 115' },
  // dragon : museau long avec la bosse des naseaux
  dragon: { d: 'M66 70 C72 52 90 40 110 40 C124 40 136 46 142 55 L151 52 L150 64 C158 70 166 72 174 71 C180 66 190 68 194 76 C199 84 198 95 191 100 C180 105 166 105 154 109 C144 113 136 119 124 122 C112 124 100 122 90 117 L70 126 L79 106 L56 106 L70 90 C66 84 65 77 66 70 Z',
    n: [112, 78, 19, 14], f: [138, 72, 12, 12], nostril: [[187, 81]], mouth: 'M192 99 C177 102 163 104 147 112', fangs: [[178, 102], [164, 105]], patch: 'M150 104 C166 100 182 100 196 96 L196 130 L116 130 C128 116 138 108 150 104 Z' },
  // singe : petit museau rond et bas, masque clair autour des yeux
  monkey: { d: 'M104 44 C126 42 144 54 148 74 C149 83 154 88 160 92 C167 96 169 105 165 111 C160 118 146 122 130 123 C112 125 96 122 84 114 L66 120 L72 104 L54 100 L66 88 C62 66 80 45 104 44 Z',
    n: [105, 84, 19, 15], f: [134, 82, 13, 14], nostril: [[161, 100], [155, 99]], mouth: 'M166 109 C155 116 141 116 131 111', patch: 'M86 82 C92 66 110 66 118 80 C124 66 146 66 150 82 C156 95 171 100 167 113 C157 125 100 129 88 108 C84 100 84 90 86 82 Z' },
  // belette, renard : petit museau pointu
  weasel: { d: 'M104 44 C124 42 139 51 146 64 C151 74 161 82 173 91 C181 97 187 102 187 107 C186 112 179 113 173 113 C161 114 148 118 136 121 C104 125 66 110 66 82 C66 60 82 45 104 44 Z',
    n: [107, 82, 18, 14], f: [135, 79, 12, 12.5], nose: [184, 106, 4.4, 3.8], mouth: 'M182 112 C171 113 158 114 148 119', patch: 'M142 102 C156 98 172 102 188 108 L188 130 L106 130 C118 116 130 106 142 102 Z' },
  // tortue (kappa) : tête ronde qui s'avance en bec court, d'une seule forme
  turtle: { d: 'M100 46 C122 44 139 54 146 69 C151 78 161 82 173 88 C181 92 183 101 177 107 C169 113 155 112 145 115 C135 120 120 122 106 122 C84 122 64 106 64 84 C64 62 80 47 100 46 Z',
    n: [106, 86, 17, 15], f: [131, 84, 12.5, 14], nostril: [[168, 94]], mouth: 'M179 104 C167 105 155 107 147 111', patch: 'M146 76 C158 79 173 86 184 94 L184 120 L138 120 C146 108 149 92 146 76 Z' },
  // crâne de cerf : os, orbites creuses
  skull: { d: 'M104 42 C126 40 142 50 147 66 C149 76 156 84 164 92 C172 100 180 108 180 116 C178 122 170 122 164 118 C154 114 146 116 138 120 C124 124 64 112 64 80 ' + BACK,
    sockets: [[106, 84, 12, 11], [136, 80, 8, 9]], nasal: 'M166 104 C170 104 174 108 172 112 C168 112 164 108 166 104 Z', teethLine: 'M178 118 C166 116 154 116 144 120' },
};
function species(kind) {
  return (h, o) => {
    const { S, T } = h, sp = SPECIES[kind], lid = beastLid(h), pt2 = h.TK(o.patchT, 'muz');
    let inner = blob('M140 56 C152 72 152 96 138 112 L200 126 L200 50 Z', T.skin.shadow, 0.35, 3);
    if (sp.patch && (o.patchT || T.muz)) inner += `<path d="${sp.patch}" fill="${pt2.base}" opacity="${o.patchOp ?? 1}" filter="url(#g2)"/>`;
    if (sp.belly) inner += `<path d="${sp.belly}" fill="${h.TK(o.patchT, 'muz').base}"/>`;
    inner += headInner(h, { ...o, stubble: null }).replace(/^<path[^>]*filter[^>]*\/>/, '');
    S(sp.d, T.skin, { sh: 9, hl: 6, inner });
    let s = '';
    if (sp.sockets) { for (const [x, y, rx, ry] of sp.sockets) s += `<ellipse cx="${x}" cy="${y}" rx="${rx}" ry="${ry}" fill="#1c1a22"/>` + ((o.eyes ?? {}).color ? `<circle cx="${x + 1}" cy="${y + 1}" r="${rx * 0.42}" fill="${o.eyes.color}"/><circle cx="${x + 1}" cy="${y + 1}" r="${rx * 0.9}" fill="${o.eyes.color}" opacity="0.5" filter="url(#g2)"/>` : ''); s += `<path d="${sp.nasal}" fill="#1c1a22"/><path d="${sp.teethLine}" stroke="#1c1a22" stroke-width="1.8" fill="none"/><path d="M150 117 l0 5 M158 116 l0 5 M166 117 l0 5" stroke="#1c1a22" stroke-width="1.4"/>`; h.raw(s); return; }
    h.raw('');
    features(h, { ...o, nose: 'none' }, { n: sp.n, f: sp.f, mouth: null, nose: false, lid, browC: o.browC ?? lid });
    const dark = o.noseC ?? '#1c1218';
    if (sp.nose) s += `<ellipse cx="${sp.nose[0]}" cy="${sp.nose[1]}" rx="${sp.nose[2]}" ry="${sp.nose[3]}" fill="${dark}"/><ellipse cx="${sp.nose[0] - 1.5}" cy="${sp.nose[1] - 1.5}" rx="1.6" ry="1.1" fill="#fff" opacity="0.5"/>`;
    if (sp.noseD) s += `<path d="${sp.noseD}" fill="${o.noseC ?? '#7a3a34'}" stroke="${dark}" stroke-width="1.2" stroke-linejoin="round"/>`;
    for (const [x, y] of sp.nostril ?? []) s += `<ellipse cx="${x}" cy="${y}" rx="2.8" ry="2.1" fill="${dark}" transform="rotate(-20 ${x} ${y})"/>`;
    if (sp.mouth) s += `<path d="${sp.mouth}" stroke="${dark}" stroke-width="2.1" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
    for (const [x, y] of sp.fangs ?? []) s += `<path d="M${x - 3.5} ${y - 0.5} L${x} ${y + 9} L${x + 3.5} ${y - 1.5} Z" fill="#fff8e0" stroke="${dark}" stroke-width="1"/>`;
    if (sp.teeth) { const [a, c, b, n] = sp.teeth; s += `<path d="M${pt(a)} Q${pt(c)} ${pt(b)}" stroke="${dark}" stroke-width="2.2" fill="none" stroke-linecap="round"/>`; for (let i = 0; i < n; i++) { const t0 = (i + 0.15) / n, t1 = (i + 0.85) / n, q = (t) => K.qpoint([a, c, b], t), p0 = q(t0), p1 = q(t1); s += `<path d="M${pt(p0)} L${f((p0[0] + p1[0]) / 2 + 1.5)} ${f((p0[1] + p1[1]) / 2 + 7)} L${pt(p1)} Z" fill="#fff8e0" stroke="${dark}" stroke-width="0.9" stroke-linejoin="round"/>`; } s += `<path d="M84 92 q6 8 4 18 M94 96 q6 8 4 18 M104 99 q5 7 4 16" stroke="${T.skin.shadow}" stroke-width="2" fill="none" opacity="0.7"/>`; }
    if (o.tongue) s += `<path d="M186 104 C196 106 200 112 204 108 M200 110 L206 114" stroke="#e0485a" stroke-width="2.4" fill="none" stroke-linecap="round"/>`;
    if (o.ring) s += `<path d="M183 110 a6.5 7.5 0 1 0 9 -1" stroke="${T.gold.base}" stroke-width="2.8" fill="none"/>`;
    if (o.whiskerDots) s += `<g fill="${dark}" opacity="0.6"><circle cx="160" cy="100" r="1.3"/><circle cx="165" cy="103" r="1.3"/><circle cx="158" cy="105" r="1.3"/></g>`;
    h.raw(s);
    if (o.beard) beard(h, o.beard, h.TK(o.beardT, 'hair'));
  };
}
for (const k of Object.keys(SPECIES)) LIB.head[k] = species(k);
// oiseaux : tête ronde, bec posé à fleur de visage (mandibule du haut crochue pour l'aigle)
LIB.head.eagle = (h, o) => {
  const { S, T } = h, bk = h.TK(o.beakT, 'gold'), lid = beastLid(h);
  S('M104 44 C126 42 146 56 148 78 C149 96 140 112 124 118 C112 122 98 121 88 115 L70 122 L76 106 L56 104 L68 92 C64 84 63 74 66 66 L52 58 L70 54 C78 47 90 44 104 44 Z', T.skin, { sh: 9, hl: 6, inner: headInner(h, o) });
  features(h, { ...o, nose: 'none' }, { n: [103, 84, 20, 15], f: [131, 82, 12, 13], mouth: null, nose: false, lid, browC: o.browC ?? lid });
  S('M137 99 C148 100 160 100 168 104 C162 111 150 113 138 110 C140 106 139 102 137 99 Z', bk, { sh: 3, hl: 2, far: true, rim: false });
  S('M134 74 C152 70 172 78 181 91 C185 98 184 105 178 110 C176 103 170 99 160 99 C150 99 142 101 135 101 C139 93 139 82 134 74 Z', bk, { sh: 4, hl: 3 });
  h.raw(`<ellipse cx="157" cy="88" rx="2.6" ry="1.8" fill="#3a2408" transform="rotate(20 157 88)"/>`);
};
// golems : tête taillée à facettes, yeux en fentes de lumière
LIB.head.golem = (h, o) => {
  const { S, T } = h, c = (o.eyes ?? {}).color ?? '#ff7a1a';
  S(o.round ? 'M82 46 C100 38 126 40 142 52 C152 62 154 84 150 100 C146 114 132 122 112 122 C92 122 72 114 66 98 C60 80 66 56 82 46 Z' : 'M76 50 L126 40 L152 62 L150 102 L132 122 L88 122 L64 100 L62 68 Z', T.skin, { sh: 10, hl: 6, inner: headInner(h, o) });
  h.raw(`<path d="M92 80 L114 86 L112 94 L92 90 Z M124 86 L144 80 L144 90 L126 94 Z" fill="${c}"/><path d="M92 80 L114 86 L112 94 L92 90 Z M124 86 L144 80 L144 90 L126 94 Z" fill="${c}" opacity="0.7" filter="url(#g2)"/>` + (o.maw ? `<path d="M96 108 L104 104 L110 110 L118 104 L126 110 L134 104 L140 108" stroke="${c}" stroke-width="3.4" fill="none" stroke-linejoin="round"/>` : ''));
};
module.exports = { eye, brow, mouth, nose, beard, BEARD, JAW, headPath, SPECIES, features, headInner };
