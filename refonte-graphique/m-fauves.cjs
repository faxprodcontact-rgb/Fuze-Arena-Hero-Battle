// LES FAUVES DE CENDRE (feu) — les prédateurs d'une savane brûlée : pelages de suie, braises sous la peau.
// Niveau de la famille de référence (m-glaces.cjs) : cou, profil de dos, museau d'un seul tenant, marques du pelage,
// griffes, sourcil dur. Gueule ouverte découpée dans la silhouette, membres attachés sous le corps, un seul contour.
const { Mo } = require('./mon6.cjs');
const EMBER = '#ff7a1a', IVORY = '#f6ecd4', MAW = '#2a0f14';
// crête de crins : une seule bande déchiquetée qui épouse la ligne du dos (pts de l'arrière vers l'avant), poils couchés vers l'arrière
const bristle = (pts, n, h, lean, drop = 14) => {
  const seg = []; let tot = 0; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); seg.push(d); tot += d; }
  const at = (t) => { let d = t * tot; for (let i = 0; i < seg.length; i++) { if (d <= seg[i] || i === seg.length - 1) { const k = d / seg[i]; return [pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k]; } d -= seg[i]; } };
  const V = [1, 0.62, 0.9, 0.55, 1, 0.7, 0.85, 0.6], f = ([x, y]) => x.toFixed(1) + ' ' + y.toFixed(1);
  let d = '';
  for (let i = 0; i < n; i++) { const a = at(i / n), b = at((i + 1) / n), l = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, k = h * V[i % 8];
    d += (i ? ' L' : 'M') + f(a) + ' L' + f([(a[0] + b[0]) / 2 + (b[1] - a[1]) / l * k - lean * V[i % 8], (a[1] + b[1]) / 2 - (b[0] - a[0]) / l * k]); }
  const e = at(1), s0 = at(0);
  return d + ' L' + f(e) + ' L' + f([e[0], e[1] + drop]) + ' L' + f([s0[0], s0[1] + drop]) + ' Z';
};
const cracks = (d) => `<path d="${d}" stroke="${EMBER}" stroke-width="5" fill="none" opacity="0.5" filter="url(#g2)" stroke-linecap="round"/><path d="${d}" stroke="#ffd76a" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;

// 0 · rapide — Hyène : garrot haut, croupe basse, crinière hérissée, elle ricane
Mo('fauves', 0, 'Hyène', { scale: 1.02, atk: 'slash', wind: -14, hit: 20, colors: { fur: '#b89a78', dark: '#5a463c', mane: '#3a2c2a' }, swing: ['head'], grp: { tail: 'back', mane: 'torso', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [128, 152], back: [36, 178], torso: [88, 196] } },
  ({ S, raw, T, G, L, beast, neck, tuft, brow, spots, under, eye, teeth }) => {
    const legs = beast({ front: 116, hind: 52, top: 186, w: 16, t: 'fur', dark: 'dark', claws: true });
    G('tail', () => { L([[[[38, 178], [22, 184], [18, 198]], 10, 7]], 'fur'); S('M12 192 C6 202 8 214 16 220 C26 214 28 202 24 190 Z', T.mane, { sh: 3 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    // brosse courte et drue, de la nuque au milieu du dos
    G('mane', () => S(bristle([[72, 154], [96, 140], [118, 130], [144, 120]], 12, 11, 5), T.mane, { sh: 3 }));
    G('body', () => {
      // dos en pente : la croupe est basse, les épaules hautes
      S('M30 182 C28 166 40 156 56 152 C76 146 96 128 118 126 C136 126 146 142 144 166 C142 190 118 204 86 204 C56 204 32 198 30 182 Z', T.fur, { sh: 10, hl: 6,
        inner: under('M36 196 C64 210 116 208 144 184 L148 214 L34 214 Z', '#e0cca8') + spots([[58, 168, 5], [74, 158, 4.4], [70, 180, 4], [90, 150, 4.4], [92, 172, 4.6], [108, 140, 4], [50, 184, 3.4], [110, 160, 3.6]], '#5a463c', 0.75) + '<ellipse cx="118" cy="166" rx="18" ry="24" fill="#fff" opacity="0.1"/>' });
      neck([116, 150], [136, 138], [154, 142], 48, 40, 'fur', { inner: spots([[130, 136, 3.6], [144, 146, 3.2]], '#5a463c', 0.7) });
    });
    G('head', () => {
      S('M134 122 C120 110 118 92 126 82 C138 88 146 104 146 118 Z', T.fur, { sh: 4, inner: '<path d="M132 114 C126 106 126 96 128 90 C136 96 140 106 140 114 Z" fill="#5a463c"/>' }); S('M158 112 C156 96 162 84 172 80 C178 92 176 106 170 116 Z', T.dark, { sh: 3 });
      tuft(134, 180, 205, 14, 20, 'fur');
      raw(`<path d="M199 155 L152 163 L184 177 C170 174 168 164 199 155 Z" fill="${MAW}"/><path d="M154 166 C162 164 170 167 174 172 C168 175 160 175 154 171 Z" fill="#c8586a"/>`);
      S('M124 148 C122 124 138 110 158 110 C172 110 184 118 192 130 C200 132 206 138 205 146 C204 150 202 153 199 154 L158 162 L190 178 C182 188 166 192 150 190 C134 188 124 170 124 148 Z', T.fur, { sh: 9, hl: 6,
        inner: under('M168 140 C182 134 198 136 208 144 L206 156 L162 162 Z', '#3a2c2a', 0.85) + '<path d="M194 132 C199 130 205 134 204 140 C199 142 194 138 194 132 Z" fill="#1c1218"/>' + spots([[136, 150, 3.4], [142, 164, 3]], '#5a463c', 0.7) });
      teeth([196, 155], [162, 161.5], 5, 7, 1); teeth([186, 177], [162, 165], 4, -6, 1);
      eye(164, 130, 10, 8.5, { iris: '#ff9a2a', pupilK: 0.45, lid: 0.42, tilt: 1 }); brow(164, 119, 26, 1, '#3a2c2a', 5);
    });
  });

// 1 · costaud — Phacochère : longue face plate, verrues, groin large, deux défenses qui remontent des coins de la gueule
Mo('fauves', 1, 'Phacochère', { scale: 1.1, atk: 'smash', wind: -16, hit: 22, colors: { fur: '#6a5248', dark: '#46342e', mane: '#b8482a', tusk: IVORY }, swing: ['head'], grp: { tail: 'back', mane: 'torso', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [116, 164], back: [40, 160], torso: [86, 196] } },
  ({ S, raw, T, G, L, beast, neck, brow, under, eye, limb, ell, disc }) => {
    const legs = beast({ front: 108, hind: 54, top: 190, w: 17, t: 'fur', dark: 'dark', hoof: true });
    G('tail', () => { L([[[[42, 164], [28, 136], [36, 106]], 5, 4]], 'dark'); S('M30 110 C24 98 28 84 38 76 C46 86 48 100 42 112 Z', T.mane, { sh: 3 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    // longue crinière fine, couchée vers l'arrière, sur l'encolure et les épaules
    G('mane', () => S(bristle([[76, 146], [100, 134], [122, 126], [140, 120]], 8, 20, 14), T.mane, { sh: 3 }));
    G('body', () => {
      S('M32 180 C30 160 44 148 62 146 C82 138 104 130 122 138 C136 146 140 162 138 178 C136 196 114 206 84 206 C56 206 34 198 32 180 Z', T.fur, { sh: 10, hl: 6,
        inner: under('M40 198 C66 210 112 208 138 188 L140 214 L38 214 Z', '#8a6e60', 0.7) + cracks('M52 170 L66 178 L78 166 M92 182 L104 172') + '<ellipse cx="112" cy="170" rx="18" ry="24" fill="#fff" opacity="0.08"/>' });
      neck([108, 158], [120, 158], [134, 160], 58, 52, 'fur');
    });
    G('head', () => {
      S('M116 126 L106 98 L130 114 Z', T.fur, { sh: 3, inner: '<path d="M117 121 L112 107 L125 115 Z" fill="#46342e"/>' }); S('M138 118 L146 94 L156 118 Z', T.dark, { sh: 3 });
      // les verrues de l'autre côté dépassent du profil
      S(disc(162, 123, 6.5), T.dark, { sh: 2 }); S(disc(181, 140, 5.5), T.dark, { sh: 2 });
      // les défenses sortent des coins de la gueule, vers l'extérieur puis vers le haut
      S(limb([[182, 184], [210, 198], [226, 166]], 9, 2, 16), T.tusk, { sh: 3, far: true }); S(limb([[166, 186], [200, 214], [218, 160]], 13, 2, 18), T.tusk, { sh: 3, hl: 2 });
      S('M104 150 C102 128 118 114 138 116 C150 116 160 122 170 132 L190 150 C200 156 204 168 202 178 C200 190 188 194 176 192 C158 196 136 198 122 192 C110 186 104 168 104 150 Z', T.fur, { sh: 10, hl: 6,
        inner: '<g fill="#46342e"><ellipse cx="152" cy="151" rx="8.5" ry="7"/><ellipse cx="172" cy="171" rx="7" ry="6"/></g><g fill="#8a6e60" opacity="0.75"><ellipse cx="154" cy="148" rx="3.2" ry="2.2"/><ellipse cx="174" cy="168" rx="2.6" ry="1.9"/></g><path d="M182 190 C170 188 158 190 148 194" stroke="#2a1c18" stroke-width="2.2" fill="none" stroke-linecap="round"/>' });
      S(ell(197, 170, 9, 15), T.dark, { sh: 3, inner: '<ellipse cx="197" cy="163" rx="2.6" ry="3.4" fill="#1c1218"/><ellipse cx="198" cy="177" rx="2.6" ry="3.4" fill="#1c1218"/>' });
      eye(134, 133, 7, 6, { iris: '#ff9a2a', pupilK: 0.5, lid: 0.46, tilt: 1 }); brow(134, 125, 20, 1, '#2a1c18', 5);
    });
  });

// 2 · tireur — Serpent cracheur : dressé sur ses anneaux, capuchon déployé, il crache des braises
Mo('fauves', 2, 'Serpent cracheur', { atk: 'cast', fx: EMBER, colors: { skin: '#4a4046', dark: '#2e262c', belly: '#e0b070' }, grp: { tail: 'back', coil: 'legs', neck: 'torso' }, piv: { head: [104, 170], back: [48, 206], torso: [104, 206] }, shine: [[194, 106, 9, EMBER]], shineGrp: 'head' },
  ({ S, raw, T, G, L, halo, eye, brow, stripes, ell, limb }) => {
    const scales = (rows) => `<g fill="none" stroke="#2e262c" stroke-width="2" opacity="0.6">${rows.map(([x, y, n]) => Array.from({ length: n }, (_, i) => `<path d="M${x + i * 14} ${y} q7 8 14 0"/>`).join('')).join('')}</g>`;
    halo(194, 106, 16, EMBER, 0.85);
    G('tail', () => { L([[[[56, 210], [18, 204], [14, 166]], 14, 4]], 'skin', { N: 18 }); });
    G('coil', () => {
      S(limb([[40, 214], [104, 236], [168, 214]], 26, 26, 18), T.dark, { sh: 5, inner: scales([[52, 214, 8]]) });
      S(limb([[156, 200], [104, 184], [54, 200]], 26, 24, 18), T.skin, { sh: 6, inner: scales([[60, 190, 6]]) + cracks('M120 198 L132 192 L142 200') });
    });
    G('neck', () => L([[[[104, 196], [84, 160], [104, 128]], 30, 28]], 'skin', { inner: '<path d="M98 196 C86 170 94 144 110 128" stroke="#e0b070" stroke-width="12" fill="none" opacity="0.8"/>' + stripes(['M92 176 l12 -2', 'M90 160 l12 -3', 'M94 144 l12 -4'], '#8a6a3a', 2.4, 0.7) }));
    G('head', () => {
      // le capuchon : large, avec sa marque en lunettes
      S('M112 56 C78 58 58 86 62 120 C66 148 90 166 106 172 L122 172 C142 162 160 146 162 120 C166 86 146 56 112 56 Z', T.skin, { sh: 9, hl: 6,
        inner: '<path d="M96 100 C92 122 98 148 112 166 C128 150 134 126 130 102 Z" fill="#e0b070" opacity="0.9"/>' + stripes(['M98 118 L130 116', 'M100 132 L130 130', 'M104 146 L126 144'], '#8a6a3a', 2.4, 0.7) + cracks('M74 92 L82 106 L74 120 L82 134 M150 92 L146 108 L152 124') + scales([[66, 84, 2], [136, 76, 2]]) });
      raw(`<path d="M188 96 L132 108 L171 126 C152 122 150 110 188 96 Z" fill="${MAW}"/><path d="M140 112 C148 110 156 113 160 118 C154 121 146 120 140 117 Z" fill="#e0485a"/>`);
      S('M96 98 C96 76 116 64 138 66 C160 68 180 80 189 94 L138 108 L176 128 C168 140 148 142 132 138 C110 134 96 118 96 98 Z', T.skin, { sh: 8, hl: 5, inner: '<ellipse cx="178" cy="87" rx="2.2" ry="1.7" fill="#1c1218"/>' + scales([[106, 76, 3]]) });
      raw(`<path d="M182 98 L178 124 L170 101 Z M164 103 L162 121 L155 105 Z" fill="${IVORY}" stroke="#2a1420" stroke-width="1" stroke-linejoin="round"/><path d="M168 124 L170 114 L174 126 Z M154 118 L156 110 L160 120 Z" fill="${IVORY}" stroke="#2a1420" stroke-width="1" stroke-linejoin="round"/>`);
      eye(142, 90, 10, 8, { iris: '#ff9a2a', pupil: 'slit', lid: 0.44, tilt: 1 }); brow(142, 79, 26, 1, '#1c1218', 5);
    });
  });

// 3 · sorts — Vautour : de trois quarts, une aile levée, l'autre à demi repliée ; il attend que les blessés tombent
Mo('fauves', 3, 'Vautour', { atk: 'cast', fx: EMBER, colors: { feather: '#3a3238', dark: '#241e24', skin: '#c8604e', ruff: '#e8dcc8', beak: '#e0b050' }, swing: ['wingN'], far: ['wingF'], grp: { legs: 'legs', body: 'torso' }, piv: { swing: [116, 124], far: [98, 130], head: [108, 110], torso: [106, 200] } },
  ({ S, raw, T, G, L, eye, brow, stripes }) => {
    // l'aile du fond est levée haut, derrière le corps
    G('wingF', () => S('M104 132 C90 100 66 68 28 42 L40 68 L16 64 L36 88 L10 92 L36 108 L18 122 L48 126 L40 142 L74 140 C90 142 100 138 104 132 Z', T.dark, { sh: 6, far: true,
      inner: '<path d="M98 128 C84 102 64 78 38 58 L46 76 C62 90 76 108 86 130 Z" fill="#3a3238" opacity="0.7"/>' + stripes(['M58 96 l-16 4', 'M66 110 l-18 4', 'M74 124 l-18 4'], '#120e14', 3, 0.6) + `<path d="M26 66 L34 74 M22 94 L32 98" stroke="${EMBER}" stroke-width="2.4" stroke-linecap="round" opacity="0.8"/>` }));
    G('legs', () => { L([[[[96, 192], [94, 208], [96, 220]], 8, 6], [[[118, 192], [120, 208], [120, 220]], 8, 6]], 'beak'); raw('<g fill="#e0b050" stroke="#2c1626" stroke-width="1.4" stroke-linejoin="round"><path d="M84 228 L90 216 L96 226 L102 216 L110 228 Z"/><path d="M110 228 L116 216 L122 226 L126 216 L134 228 Z"/></g>'); });
    G('body', () => S('M74 156 C70 126 88 108 110 108 C132 108 146 126 144 158 C142 186 128 204 108 204 C88 204 78 184 74 156 Z', T.feather, { sh: 10, hl: 6,
      inner: stripes(['M124 150 l10 -3', 'M122 166 l10 -3', 'M116 182 l10 -3', 'M104 194 l8 2'], '#120e14', 3, 0.55) }));
    // l'aile de devant est à demi repliée contre le flanc
    G('wingN', () => S('M118 120 C98 114 78 128 70 152 C64 170 58 188 46 206 L64 198 L62 214 L78 200 L82 216 L96 198 C110 180 122 160 124 138 C124 130 122 124 118 120 Z', T.feather, { sh: 7, hl: 4,
      inner: '<path d="M116 124 C100 122 86 132 80 150 C92 144 106 142 120 146 Z" fill="#241e24" opacity="0.65"/>' + stripes(['M108 150 l-22 30', 'M96 150 l-22 34', 'M84 152 l-20 34'], '#120e14', 3, 0.6) + `<path d="M58 200 L64 192 M74 204 L78 196" stroke="${EMBER}" stroke-width="2.4" stroke-linecap="round" opacity="0.8"/>` }));
    G('head', () => {
      // collerette, bec crochu, puis le long cou nu d'un seul tenant avec le crâne
      S('M84 122 L74 100 L92 110 L96 88 L108 106 L118 88 L126 108 L144 98 L134 124 C118 134 100 134 84 122 Z', T.ruff, { sh: 4 });
      S('M144 54 C164 48 184 58 186 76 C186 86 178 94 170 90 C172 82 164 74 148 74 Z', T.beak, { sh: 3, hl: 2, inner: '<path d="M176 70 C184 76 184 88 172 92 L168 82 Z" fill="#3a2a22"/><ellipse cx="160" cy="62" rx="2.6" ry="1.8" fill="#3a2a22"/>' });
      S('M98 116 C92 94 100 74 114 62 C120 46 138 42 148 50 C156 54 158 68 154 76 C150 86 138 88 130 84 C122 92 122 104 124 118 Z', T.skin, { sh: 7, hl: 5, inner: stripes(['M104 100 l12 2', 'M106 88 l10 4', 'M110 76 l8 5'], '#8a3428', 2.2, 0.6) });
      eye(138, 62, 8, 6.5, { iris: '#ffe14a', pupilK: 0.5, lid: 0.48, tilt: 1 }); brow(138, 53, 20, 1, '#5a2018', 4.5);
    });
  });

// 4 · élite — Lionne noire : aplatie contre le sol, la gueule ouverte, prête à bondir, des braises dans le regard
Mo('fauves', 4, 'Lionne noire', { scale: 1.2, atk: 'slash', wind: -14, hit: 22, colors: { fur: '#3a3238', dark: '#241e24', pale: '#7a6a6c' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [126, 180], back: [28, 150], torso: [86, 200] }, shine: [[8, 90, 9, EMBER]], shineGrp: 'back' },
  ({ S, raw, T, TK, G, L, beast, neck, brow, under, halo, eye, teeth, disc }) => {
    const legs = beast({ front: 116, hind: 44, top: 194, w: 20, t: 'fur', dark: 'dark', claws: true });
    halo(8, 90, 14, EMBER, 0.85);
    G('tail', () => { L([[[[30, 152], [-2, 148], [6, 102]], 9, 5]], 'fur', { N: 18 }); S('M0 104 C-4 92 4 84 6 72 C14 84 18 94 12 104 C10 108 2 108 0 104 Z', TK('#ff9a2a'), { sh: 2, hl: 3 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      // l'arrière-train est haut, les omoplates saillent, le poitrail frôle le sol
      S('M20 164 C18 138 40 126 64 130 C80 132 92 142 104 148 C112 138 126 138 134 150 C142 162 146 178 144 188 C142 202 122 208 94 208 C56 208 22 196 20 164 Z', T.fur, { sh: 10, hl: 6,
        inner: under('M30 196 C62 212 116 210 144 190 L146 216 L28 216 Z', '#5a4e52', 0.7) + cracks('M40 150 L54 162 L66 150 L82 166 M96 176 L106 186') });
      neck([120, 170], [134, 164], [150, 172], 54, 50, 'fur');
    });
    G('head', () => {
      // oreilles rondes de lionne
      S(disc(162, 131, 11), T.dark, { sh: 3 }); S(disc(131, 140, 13.5), T.fur, { sh: 4, inner: '<circle cx="130" cy="140" r="7" fill="#7a6a6c"/>' });
      raw(`<path d="M207 181 L164 188 L196 203 C180 200 178 190 207 181 Z" fill="${MAW}"/><path d="M168 191 C178 188 186 192 190 199 C182 202 174 201 168 196 Z" fill="#c8586a"/>`);
      S('M118 172 C116 146 134 132 156 132 C172 132 186 138 196 150 C206 152 214 160 213 170 C212 175 210 178 207 180 L168 187 L200 204 C192 213 176 217 158 215 C136 213 118 196 118 172 Z', T.fur, { sh: 10, hl: 6,
        inner: under('M176 160 C190 154 206 158 216 168 L210 182 L172 188 Z', '#7a6a6c', 0.8) + under('M170 196 C182 206 194 210 204 206 L198 218 L160 218 Z', '#7a6a6c', 0.6) + '<path d="M202 152 C208 150 214 156 213 163 C207 165 202 159 202 152 Z" fill="#120a0e"/><g fill="#120a0e" opacity="0.6"><circle cx="188" cy="168" r="1.4"/><circle cx="194" cy="172" r="1.4"/><circle cx="184" cy="174" r="1.4"/></g>' + cracks('M130 176 L138 186 L134 196') });
      teeth([203, 181.5], [174, 186.5], 4, 8, 1); teeth([196, 203], [174, 191], 3, -7, 1);
      halo(172, 160, 12, EMBER, 0.7);
      eye(172, 160, 10, 7.5, { sclera: '#ffd76a', iris: EMBER, pupil: 'slit', lid: 0.46, tilt: 1 }); brow(172, 149, 28, 1, '#120a0e', 6);
    });
  });

// 5 · boss — Buffle de braise : tête basse, il mugit des braises ; bosse énorme, arrière-train sec, cornes fendues qui rougeoient
Mo('fauves', 5, 'Buffle de braise', { scale: 1.38, atk: 'smash', wind: -18, hit: 24, fx: EMBER, colors: { fur: '#3e3438', dark: '#261f24', horn: '#d8c8a8', pale: '#6a5a5c' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [124, 150], back: [26, 150], torso: [86, 196] }, shine: [[214, 178, 12, EMBER]], shineGrp: 'swing' },
  ({ S, raw, T, TK, G, L, beast, fringe, neck, brow, stripes, halo, eye, teeth, limb }) => {
    const legs = beast({ front: 106, hind: 44, top: 184, w: 24, t: 'fur', dark: 'dark', hoof: true });
    halo(10, 188, 16, EMBER, 0.8);
    G('tail', () => { L([[[[26, 148], [2, 158], [10, 198]], 7, 4]], 'dark', { N: 18 }); S('M2 200 C-4 188 4 178 8 164 C16 178 22 190 18 202 C16 210 4 210 2 200 Z', TK('#ff9a2a'), { sh: 2, hl: 3 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      // croupe sèche, creux derrière la bosse, puis la bosse des épaules, très haute
      S('M24 170 C22 150 34 138 52 136 C64 134 74 138 82 128 C90 106 112 90 132 104 C146 116 150 140 148 160 C146 178 140 190 132 198' + fringe(132, 72, 198, 5, 12) + ' C56 198 32 190 24 170 Z', T.fur, { sh: 13, hl: 8,
        inner: cracks('M40 148 L54 160 L48 174 M92 116 L104 132 L96 150 L108 164 M120 150 L128 168') + stripes(['M88 170 q4 12 0 24', 'M112 172 q4 12 0 22'], '#261f24', 3.4, 0.5) });
      neck([118, 134], [136, 148], [150, 162], 74, 60, 'fur');
    });
    G('head', () => {
      // les cornes partent de sous le front ; leurs pointes fendues rougeoient
      S(limb([[160, 130], [216, 118], [208, 56]], 18, 3, 18), T.horn, { sh: 4, far: true, inner: stripes(['M184 118 l4 12', 'M200 108 l8 8'], '#8a7a5a', 2, 0.6) + cracks('M208 66 L212 78 L206 88') });
      S(limb([[138, 136], [82, 130], [78, 64]], 22, 3, 18), T.horn, { sh: 5, hl: 3, inner: stripes(['M118 126 l-2 14', 'M100 122 l-6 12', 'M86 106 l-10 4'], '#8a7a5a', 2, 0.6) + cracks('M79 74 L84 88 L78 98') });
      halo(214, 178, 24, EMBER, 0.85); halo(226, 172, 12, '#ffd76a', 0.6);
      raw(`<path d="M205 188 L162 189 L191 207 C176 204 174 194 205 188 Z" fill="${MAW}"/><path d="M166 192 C176 190 184 194 188 201 C180 204 172 203 166 198 Z" fill="#e0485a"/>`);
      S('M120 158 C118 138 132 124 152 126 C170 128 186 138 198 154 C206 160 212 170 210 180 C209 184 207 186 204 187 L166 188 L194 208 C184 215 164 215 148 209 C130 202 120 180 120 158 Z', T.fur, { sh: 11, hl: 7,
        inner: '<path d="M176 160 C188 158 202 166 210 178 L204 188 L170 188 Z" fill="#6a5a5c" opacity="0.8" filter="url(#g2)"/><ellipse cx="200" cy="170" rx="4.6" ry="3.6" fill="#ffb04a"/><ellipse cx="189" cy="164" rx="3.8" ry="3" fill="#ffb04a"/>' + cracks('M128 164 L138 172 L134 184') });
      teeth([200, 188], [172, 188.5], 4, 6, 1); teeth([190, 206], [172, 193], 3, -6, 1);
      // le bouclier d'os qui réunit les deux cornes
      S('M126 138 C138 122 164 122 176 134 C164 144 140 146 126 138 Z', T.horn, { sh: 4, hl: 3, inner: '<path d="M150 124 L150 144" stroke="#8a7a5a" stroke-width="2" opacity="0.6"/>' });
      eye(158, 160, 10, 7.5, { sclera: '#ffd76a', iris: EMBER, pupilK: 0.45, lid: 0.5, tilt: 1 }); brow(158, 149, 30, 1, '#120a0e', 7);
    });
  });
