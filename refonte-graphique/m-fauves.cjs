// LES FAUVES DE CENDRE (feu) — les prédateurs d'une savane brûlée : pelages de suie, braises sous la peau.
// Niveau de la famille de référence (m-glaces.cjs) : cou, profil de dos, museau d'un seul tenant, marques du pelage,
// griffes, sourcil dur. Gueule ouverte découpée dans la silhouette, membres attachés sous le corps, un seul contour.
const { Mo } = require('./mon6.cjs');
const EMBER = '#ff7a1a', IVORY = '#f6ecd4', MAW = '#2a0f14';
const cracks = (d) => `<path d="${d}" stroke="${EMBER}" stroke-width="5" fill="none" opacity="0.5" filter="url(#g2)" stroke-linecap="round"/><path d="${d}" stroke="#ffd76a" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;

// 0 · rapide — Hyène : garrot haut, croupe basse, crinière hérissée, elle ricane
Mo('fauves', 0, 'Hyène', { scale: 1.02, atk: 'slash', wind: -14, hit: 20, colors: { fur: '#b89a78', dark: '#5a463c', mane: '#3a2c2a' }, swing: ['head'], grp: { tail: 'back', mane: 'torso', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [128, 152], back: [36, 178], torso: [88, 196] } },
  ({ S, raw, T, G, L, beast, neck, tuft, brow, spots, under, eye, teeth }) => {
    const legs = beast({ front: 116, hind: 52, top: 186, w: 16, t: 'fur', dark: 'dark', claws: true });
    G('tail', () => { L([[[[38, 178], [22, 184], [18, 198]], 10, 7]], 'fur'); S('M12 192 C6 202 8 214 16 220 C26 214 28 202 24 190 Z', T.mane, { sh: 3 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('mane', () => S('M50 160 L52 140 L64 152 L70 130 L82 144 L90 120 L100 136 L110 110 L120 128 L132 104 L138 128 L152 112 L152 142 Z', T.mane, { sh: 4 }));
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

// 1 · costaud — Phacochère : des épaules en enclume, une tête énorme, des défenses recourbées
Mo('fauves', 1, 'Phacochère', { scale: 1.1, atk: 'smash', wind: -16, hit: 22, colors: { fur: '#6a5248', dark: '#46342e', mane: '#b8482a', tusk: IVORY }, swing: ['head'], grp: { tail: 'back', mane: 'torso', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [116, 164], back: [40, 160], torso: [86, 196] } },
  ({ S, raw, T, G, L, beast, neck, tuft, brow, under, eye, limb, ell }) => {
    const legs = beast({ front: 108, hind: 54, top: 190, w: 17, t: 'fur', dark: 'dark', hoof: true });
    G('tail', () => { L([[[[42, 164], [28, 136], [36, 106]], 5, 4]], 'dark'); S('M30 110 C24 98 28 84 38 76 C46 86 48 100 42 112 Z', T.mane, { sh: 3 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('mane', () => S('M46 158 L50 134 L62 150 L68 124 L80 144 L88 118 L98 138 L108 114 L116 136 L128 118 L130 146 Z', T.mane, { sh: 4 }));
    G('body', () => {
      S('M32 180 C30 160 44 148 62 146 C82 138 104 130 122 138 C136 146 140 162 138 178 C136 196 114 206 84 206 C56 206 34 198 32 180 Z', T.fur, { sh: 10, hl: 6,
        inner: under('M40 198 C66 210 112 208 138 188 L140 214 L38 214 Z', '#8a6e60', 0.7) + cracks('M52 170 L66 178 L78 166 M92 182 L104 172') + '<ellipse cx="112" cy="170" rx="18" ry="24" fill="#fff" opacity="0.08"/>' });
      neck([108, 158], [120, 158], [134, 160], 58, 52, 'fur');
    });
    G('head', () => {
      S('M118 128 L104 100 L132 114 Z', T.fur, { sh: 3, inner: '<path d="M118 122 L112 108 L126 116 Z" fill="#46342e"/>' }); S('M142 118 L150 92 L162 118 Z', T.dark, { sh: 3 });
      // les défenses sortent de sous le groin et se recourbent vers le haut
      S(limb([[162, 186], [184, 208], [202, 176]], 10, 2, 16), T.tusk, { sh: 3, far: true }); S(limb([[174, 184], [212, 194], [208, 138]], 13, 2, 18), T.tusk, { sh: 3, hl: 2 });
      S('M104 154 C102 130 120 116 142 118 C158 120 172 130 184 144 C194 152 200 164 198 176 C196 188 184 194 172 192 C156 194 136 198 122 192 C110 186 104 170 104 154 Z', T.fur, { sh: 10, hl: 6,
        inner: '<g fill="#46342e"><ellipse cx="152" cy="160" rx="7" ry="6"/><ellipse cx="168" cy="170" rx="5.5" ry="5"/><ellipse cx="134" cy="172" rx="5" ry="4.4"/></g><path d="M176 190 C166 188 156 190 148 194" stroke="#2a1c18" stroke-width="2.2" fill="none" stroke-linecap="round"/>' });
      S(ell(190, 172, 10, 13), T.dark, { sh: 3, inner: '<ellipse cx="189" cy="167" rx="2.4" ry="3" fill="#1c1218"/><ellipse cx="192" cy="177" rx="2.4" ry="3" fill="#1c1218"/>' });
      eye(140, 140, 8.5, 7.5, { iris: '#ff9a2a', pupilK: 0.5, lid: 0.46, tilt: 1 }); brow(140, 130, 24, 1, '#2a1c18', 5.5);
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

// 3 · sorts — Vautour : voûté, il attend que les blessés tombent
Mo('fauves', 3, 'Vautour', { atk: 'cast', fx: EMBER, colors: { feather: '#3a3238', dark: '#241e24', skin: '#c8604e', ruff: '#e8dcc8', beak: '#e0b050' }, swing: ['wingN'], far: ['wingF'], grp: { legs: 'legs', body: 'torso' }, piv: { swing: [86, 128], far: [128, 126], head: [108, 110], torso: [106, 200] } },
  ({ S, raw, T, G, L, eye, brow, stripes }) => {
    G('wingF', () => S('M126 122 C150 92 182 90 204 106 L190 118 L202 132 L184 136 L194 152 L174 150 L178 168 L156 158 C142 152 130 140 126 132 Z', T.dark, { sh: 6, far: true, inner: '<path d="M132 126 C150 106 176 102 196 110 L186 122 C170 118 152 124 138 136 Z" fill="#3a3238" opacity="0.7"/>' }));
    G('wingN', () => S('M88 124 C58 92 26 96 4 116 L20 126 L6 142 L26 146 L16 164 L38 160 L34 180 L58 168 C76 162 88 146 90 134 Z', T.feather, { sh: 7,
      inner: '<path d="M84 128 C62 106 36 104 16 112 L28 124 C44 120 62 126 78 140 Z" fill="#241e24" opacity="0.6"/>' + stripes(['M64 124 l-12 18', 'M46 124 l-12 18', 'M28 130 l-8 14'], '#120e14', 3, 0.6) + `<path d="M40 150 L50 142 M22 152 L30 146" stroke="${EMBER}" stroke-width="2.4" stroke-linecap="round" opacity="0.8"/>` }));
    G('legs', () => { L([[[[94, 192], [92, 208], [94, 220]], 8, 6], [[[116, 192], [118, 208], [118, 220]], 8, 6]], 'beak'); raw('<g fill="#e0b050" stroke="#2c1626" stroke-width="1.4" stroke-linejoin="round"><path d="M82 228 L88 216 L94 226 L100 216 L108 228 Z"/><path d="M108 228 L114 216 L120 226 L124 216 L132 228 Z"/></g>'); });
    G('body', () => S('M68 156 C62 124 82 106 106 106 C130 106 144 126 142 158 C140 186 126 204 104 204 C84 204 72 184 68 156 Z', T.feather, { sh: 10, hl: 6,
      inner: stripes(['M86 158 l10 7', 'M106 162 l10 -3', 'M92 176 l10 6', 'M112 178 l10 -3', 'M100 192 l8 3'], '#120e14', 3, 0.55) + '<path d="M74 130 C84 114 126 112 138 130" stroke="#5a5058" stroke-width="5" fill="none" opacity="0.5" stroke-linecap="round"/>' }));
    G('head', () => {
      // collerette, bec crochu, puis le long cou nu d'un seul tenant avec le crâne
      S('M80 120 L70 98 L88 108 L92 86 L106 104 L116 86 L124 106 L142 96 L132 122 C116 132 96 132 80 120 Z', T.ruff, { sh: 4 });
      S('M144 54 C164 48 184 58 186 76 C186 86 178 94 170 90 C172 82 164 74 148 74 Z', T.beak, { sh: 3, hl: 2, inner: '<path d="M176 70 C184 76 184 88 172 92 L168 82 Z" fill="#3a2a22"/><ellipse cx="160" cy="62" rx="2.6" ry="1.8" fill="#3a2a22"/>' });
      S('M96 114 C90 92 98 74 114 62 C120 46 138 42 148 50 C156 54 158 68 154 76 C150 86 138 88 130 84 C122 92 120 102 122 116 Z', T.skin, { sh: 7, hl: 5, inner: stripes(['M102 98 l12 2', 'M104 86 l10 4', 'M110 76 l8 5'], '#8a3428', 2.2, 0.6) });
      eye(138, 62, 8, 6.5, { iris: '#ffe14a', pupilK: 0.5, lid: 0.48, tilt: 1 }); brow(138, 53, 20, 1, '#5a2018', 4.5);
    });
  });

// 4 · élite — Lionne noire : aplatie contre le sol, prête à bondir, des braises dans le regard
Mo('fauves', 4, 'Lionne noire', { scale: 1.22, atk: 'slash', wind: -14, hit: 22, colors: { fur: '#3a3238', dark: '#241e24', pale: '#7a6a6c' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [124, 182], back: [28, 150], torso: [86, 200] }, shine: [[8, 90, 9, EMBER]], shineGrp: 'back' },
  ({ S, raw, T, TK, G, L, beast, neck, tuft, brow, under, halo, eye }) => {
    const legs = beast({ front: 122, hind: 44, top: 194, w: 15, t: 'fur', dark: 'dark', claws: true });
    halo(8, 90, 14, EMBER, 0.85);
    G('tail', () => { L([[[[30, 152], [-2, 148], [6, 102]], 9, 5]], 'fur', { N: 18 }); S('M0 104 C-4 92 4 84 6 72 C14 84 18 94 12 104 C10 108 2 108 0 104 Z', TK('#ff9a2a'), { sh: 2, hl: 3 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      // l'arrière-train est haut, les omoplates saillent, le poitrail frôle le sol
      S('M20 164 C18 138 40 126 64 130 C80 132 92 142 104 150 C112 140 126 140 134 152 C142 164 146 178 144 188 C142 202 122 208 94 208 C56 208 22 196 20 164 Z', T.fur, { sh: 10, hl: 6,
        inner: under('M30 196 C62 212 116 210 144 190 L146 216 L28 216 Z', '#5a4e52', 0.7) + cracks('M40 150 L54 162 L66 150 L82 166 M100 174 L112 184') + '<ellipse cx="118" cy="168" rx="16" ry="20" fill="#fff" opacity="0.08"/>' });
      neck([122, 172], [138, 168], [152, 174], 44, 40, 'fur');
    });
    G('head', () => {
      S('M132 160 L108 142 L140 148 Z', T.fur, { sh: 3, inner: '<path d="M130 156 L116 146 L136 150 Z" fill="#7a6a6c"/>' }); S('M154 152 L146 128 L168 148 Z', T.dark, { sh: 3 });
      tuft(128, 198, 200, 12, 18, 'fur');
      S('M118 180 C116 160 132 148 152 148 C168 148 182 154 192 164 C200 166 207 173 206 181 C205 190 197 196 187 196 C178 204 164 208 150 208 C132 208 120 196 118 180 Z', T.fur, { sh: 9, hl: 6,
        inner: under('M170 174 C182 168 198 172 208 180 L204 196 L164 204 Z', '#7a6a6c', 0.8) + '<path d="M196 168 C201 166 207 170 206 176 C201 179 196 174 196 168 Z" fill="#120a0e"/><path d="M204 188 C194 192 182 194 170 190" stroke="#120a0e" stroke-width="2.4" fill="none" stroke-linecap="round"/><g fill="#120a0e" opacity="0.6"><circle cx="184" cy="180" r="1.3"/><circle cx="190" cy="183" r="1.3"/><circle cx="180" cy="185" r="1.3"/></g>' });
      raw(`<path d="M196 190 L194 204 L188 191 Z M180 192 L179 204 L173 192 Z" fill="${IVORY}" stroke="#120a0e" stroke-width="1" stroke-linejoin="round"/>`);
      halo(164, 170, 12, EMBER, 0.7);
      eye(164, 170, 10, 7, { sclera: '#ffd76a', iris: EMBER, pupil: 'slit', lid: 0.46, tilt: 1 }); brow(164, 160, 26, 1, '#120a0e', 5);
    });
  });

// 5 · boss — Buffle de braise : une montagne de suie, des cornes immenses, de la fumée aux naseaux
Mo('fauves', 5, 'Buffle de braise', { scale: 1.38, atk: 'smash', wind: -18, hit: 24, fx: EMBER, colors: { fur: '#3e3438', dark: '#261f24', horn: '#d8c8a8', pale: '#6a5a5c' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [120, 156], back: [26, 150], torso: [86, 196] }, shine: [[200, 170, 10, EMBER]], shineGrp: 'swing' },
  ({ S, raw, T, TK, G, L, beast, fringe, neck, tuft, brow, stripes, halo, eye, limb }) => {
    const legs = beast({ front: 106, hind: 48, top: 186, w: 26, t: 'fur', dark: 'dark', hoof: true });
    G('tail', () => { L([[[[28, 150], [12, 168], [18, 188]], 7, 5]], 'dark'); S('M12 188 C8 198 14 210 20 214 C26 206 26 196 22 186 Z', TK('#ff9a2a'), { sh: 2, hl: 3 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      // croupe basse, bosse des épaules très haute
      S('M22 170 C18 140 36 124 56 118 C74 100 108 88 130 104 C144 116 148 140 146 160 C144 178 138 190 130 200' + fringe(130, 34, 200, 8, 12) + ' C24 192 22 180 22 170 Z', T.fur, { sh: 13, hl: 8,
        inner: cracks('M44 142 L58 154 L52 170 L68 180 M82 118 L96 134 L88 152 L100 164 M116 150 L124 168') + stripes(['M40 168 q4 12 0 24', 'M64 174 q4 12 0 22', 'M110 172 q4 12 0 22'], '#261f24', 3.4, 0.5) });
      neck([116, 138], [132, 146], [148, 152], 72, 60, 'fur');
    });
    G('head', () => {
      // les cornes partent de sous le front
      S(limb([[158, 114], [212, 100], [202, 50]], 18, 3, 18), T.horn, { sh: 4, far: true, inner: stripes(['M176 104 l4 12', 'M192 98 l6 10'], '#8a7a5a', 2, 0.6) }); S(limb([[130, 118], [74, 104], [86, 52]], 21, 3, 18), T.horn, { sh: 5, hl: 3, inner: stripes(['M112 108 l-4 12', 'M96 100 l-6 10', 'M84 86 l-8 6'], '#8a7a5a', 2, 0.6) });
      tuft(152, 194, 180, 18, 28, 'dark', { n: 3 });
      halo(200, 170, 16, EMBER, 0.8);
      S('M112 146 C110 122 128 108 150 110 C170 112 184 124 190 142 C196 156 198 172 190 182 C180 192 162 190 150 194 C136 198 120 190 114 174 C112 164 112 154 112 146 Z', T.fur, { sh: 11, hl: 7,
        inner: '<path d="M162 162 C174 158 190 162 198 170 L194 188 L154 192 Z" fill="#6a5a5c" opacity="0.8" filter="url(#g2)"/><ellipse cx="188" cy="166" rx="3.2" ry="2.6" fill="#ffb04a"/><ellipse cx="177" cy="172" rx="2.8" ry="2.2" fill="#ffb04a"/><path d="M190 186 C182 182 172 182 164 186" stroke="#120a0e" stroke-width="2.4" fill="none" stroke-linecap="round"/>' + cracks('M122 150 L132 158 L128 170') });
      // le bouclier d'os qui réunit les deux cornes
      S('M120 120 C134 104 164 104 176 116 C164 128 136 130 120 120 Z', T.horn, { sh: 4, hl: 3, inner: '<path d="M148 108 L148 126" stroke="#8a7a5a" stroke-width="2" opacity="0.6"/>' });
      eye(150, 144, 10, 8, { sclera: '#ffd76a', iris: EMBER, pupilK: 0.45, lid: 0.46, tilt: 1 }); brow(150, 133, 26, 1, '#120a0e', 6);
    });
  });
