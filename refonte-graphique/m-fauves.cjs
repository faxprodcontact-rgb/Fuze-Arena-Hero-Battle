// LES FAUVES DE CENDRE (feu) — les prédateurs d'une savane brûlée : pelages de suie, braises sous la peau.
// Gueule ouverte découpée dans la silhouette, membres attachés sous le corps (voir LISEZMOI, « Les monstres »).
const { Mo } = require('./mon6.cjs');
const EMBER = '#ff7a1a', IVORY = '#f6ecd4', MAW = '#2a0f14';
const cracks = (d) => `<path d="${d}" stroke="${EMBER}" stroke-width="5" fill="none" opacity="0.5" filter="url(#g2)" stroke-linecap="round"/><path d="${d}" stroke="#ffd76a" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;

// 0 · rapide — Hyène : dos en pente, crinière hérissée, elle ricane
Mo('fauves', 0, 'Hyène', { atk: 'slash', wind: -14, hit: 20, colors: { fur: '#b89a78', dark: '#5a463c', mane: '#3a2c2a' }, swing: ['head'], grp: { tail: 'back', mane: 'torso', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [120, 164], back: [44, 176], torso: [90, 196] } },
  ({ S, raw, T, G, L, beast, eye, teeth, disc }) => {
    const legs = beast({ front: 116, hind: 58, top: 188, w: 17, t: 'fur', dark: 'dark', claws: true });
    G('tail', () => L([[[[44, 176], [24, 178], [20, 200]], 12, 6]], 'mane'));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('mane', () => S('M58 156 L60 136 L72 150 L78 126 L90 142 L98 116 L108 134 L120 110 L126 136 Z', T.mane, { sh: 4 }));
    G('body', () => S('M40 180 C38 162 52 152 70 148 C88 140 104 128 122 130 C138 132 144 148 142 168 C140 190 118 204 88 204 C60 204 42 196 40 180 Z', T.fur, { sh: 9, hl: 6,
      inner: '<g fill="#5a463c" opacity="0.75"><circle cx="64" cy="166" r="5"/><circle cx="82" cy="156" r="4.4"/><circle cx="76" cy="178" r="4"/><circle cx="98" cy="168" r="4.6"/><circle cx="56" cy="184" r="3.4"/><circle cx="100" cy="150" r="3.6"/></g>' }));
    G('head', () => {
      S(disc(124, 116, 12), T.fur, { sh: 4, inner: '<circle cx="124" cy="116" r="6" fill="#5a463c"/>' }); S(disc(154, 106, 10), T.dark, { sh: 3 });
      raw(`<path d="M190 158 L148 165 L179 180 C166 177 166 165 190 158 Z" fill="${MAW}"/><path d="M150 168 C158 166 166 169 170 175 C164 178 156 178 150 174 Z" fill="#c8586a"/>`);
      S('M112 150 C110 126 128 112 150 112 C170 112 186 124 190 142 C192 149 192 153 190 157 L152 164 L182 181 C174 191 158 196 142 194 C126 192 112 172 112 150 Z', T.fur, { sh: 9, hl: 6,
        inner: '<path d="M160 144 C172 140 184 142 192 148 L192 158 L154 164 Z" fill="#5a463c" opacity="0.8" filter="url(#g2)"/><path d="M180 136 C185 134 191 138 190 144 C185 146 180 142 180 136 Z" fill="#1c1218"/>' });
      teeth([186, 158], [156, 163.5], 4, 7, 1); teeth([178, 180], [156, 167], 3, -6, 1);
      eye(156, 132, 10, 9, { iris: '#ff9a2a', pupilK: 0.45, lid: 0.4, tilt: 1 });
    });
  });

// 1 · costaud — Phacochère : une tête énorme, des défenses recourbées
Mo('fauves', 1, 'Phacochère', { scale: 1.08, atk: 'smash', wind: -16, hit: 22, colors: { fur: '#6a5248', dark: '#46342e', mane: '#b8482a', tusk: IVORY }, swing: ['head'], grp: { tail: 'back', mane: 'torso', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [112, 168], back: [44, 160], torso: [86, 196] } },
  ({ S, raw, T, G, L, beast, eye, limb, ell }) => {
    const legs = beast({ front: 108, hind: 58, top: 190, w: 18, t: 'fur', dark: 'dark', hoof: true });
    G('tail', () => { L([[[[46, 164], [32, 136], [40, 106]], 5, 4]], 'dark'); S('M40 110 L28 92 L42 98 L46 82 L54 102 Z', T.mane, { sh: 3 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('mane', () => S('M52 154 L56 130 L68 146 L74 122 L86 142 L94 120 L104 140 L112 124 L118 146 Z', T.mane, { sh: 4 }));
    G('body', () => S('M38 178 C36 154 60 142 88 142 C114 142 132 154 134 174 C136 194 114 206 86 206 C58 206 40 198 38 178 Z', T.fur, { sh: 10, hl: 6, inner: cracks('M56 170 L70 178 L82 168 M96 184 L108 176') }));
    G('head', () => {
      S('M116 126 L102 100 L130 112 Z', T.fur, { sh: 3 }); S('M140 116 L148 92 L160 116 Z', T.dark, { sh: 3 });
      // les défenses sortent de sous le groin
      S(limb([[160, 186], [180, 204], [196, 178]], 9, 2, 16), T.tusk, { sh: 3, far: true }); S(limb([[172, 184], [204, 190], [204, 146]], 11, 2, 16), T.tusk, { sh: 3, hl: 2 });
      S('M104 152 C102 128 120 114 142 116 C158 118 172 128 182 142 C192 150 198 162 196 174 C194 186 182 192 170 190 C154 192 136 196 122 190 C110 184 104 168 104 152 Z', T.fur, { sh: 10, hl: 6,
        inner: '<g fill="#46342e"><circle cx="150" cy="156" r="6"/><circle cx="166" cy="166" r="5"/></g>' });
      S(ell(188, 170, 10, 13), T.dark, { sh: 3, inner: '<ellipse cx="187" cy="165" rx="2.4" ry="3" fill="#1c1218"/><ellipse cx="190" cy="175" rx="2.4" ry="3" fill="#1c1218"/>' });
      eye(138, 138, 8, 7.5, { iris: '#ff9a2a', pupilK: 0.5, lid: 0.46, tilt: 1 });
    });
  });

// 2 · tireur — Serpent cracheur : capuchon déployé, il crache des braises
Mo('fauves', 2, 'Serpent cracheur', { atk: 'cast', fx: EMBER, colors: { skin: '#4a4046', dark: '#2e262c', belly: '#e0b070' }, grp: { tail: 'back', coil: 'legs', neck: 'torso' }, piv: { head: [104, 170], back: [48, 206], torso: [104, 206] }, shine: [[190, 106, 9, EMBER]], shineGrp: 'head' },
  ({ S, raw, T, TK, G, L, halo, eye, ell, disc }) => {
    halo(194, 106, 16, EMBER, 0.85);
    G('tail', () => L([[[[52, 208], [20, 198], [18, 168]], 13, 4]], 'skin'));
    G('coil', () => { S(ell(104, 212, 62, 15), T.dark, { sh: 5 }); S(ell(104, 198, 48, 14), T.skin, { sh: 5, inner: '<path d="M64 200 C84 210 124 210 144 200" stroke="#e0b070" stroke-width="5" fill="none" opacity="0.6"/>' }); });
    G('neck', () => L([[[[104, 196], [86, 160], [104, 128]], 28, 26]], 'skin', { inner: '<path d="M96 196 C84 170 92 144 108 128" stroke="#e0b070" stroke-width="11" fill="none" opacity="0.7"/>' }));
    G('head', () => {
      S('M112 60 C80 62 62 88 66 120 C70 146 92 164 106 170 L122 170 C140 160 158 144 160 120 C162 88 144 60 112 60 Z', T.skin, { sh: 9, hl: 6,
        inner: '<path d="M96 98 C92 120 98 146 112 164 C128 148 134 124 130 100 Z" fill="#e0b070" opacity="0.85"/><g stroke="#4a4046" stroke-width="2.4" opacity="0.6"><path d="M98 116 L130 114 M100 130 L130 128 M104 144 L126 142"/></g>' + cracks('M76 96 L84 108 L78 120 M148 96 L144 110') });
      raw(`<path d="M178 102 L140 108 L167 121 C156 118 156 108 178 102 Z" fill="${MAW}"/><path d="M146 111 C156 111 164 114 172 113" stroke="#e0485a" stroke-width="2.4" fill="none" stroke-linecap="round"/>`);
      S('M100 98 C100 80 116 70 136 72 C154 74 172 84 178 98 L178 101 L144 108 L170 122 C162 130 148 132 134 130 C114 128 100 116 100 98 Z', T.skin, { sh: 8, hl: 5, inner: '<ellipse cx="170" cy="92" rx="2" ry="1.6" fill="#1c1218"/>' });
      raw(`<path d="M170 103 L168 118 L163 104 Z M158 105 L156 116 L152 106 Z" fill="${IVORY}" stroke="#2a1420" stroke-width="1" stroke-linejoin="round"/>`);
      eye(140, 90, 9.5, 8, { iris: '#ff9a2a', pupil: 'slit', lid: 0.42, tilt: 1 });
    });
  });

// 3 · sorts — Vautour : il tourne au-dessus des blessés
Mo('fauves', 3, 'Vautour', { atk: 'cast', fx: EMBER, colors: { feather: '#3a3238', dark: '#241e24', skin: '#d87a6a', ruff: '#e8dcc8', beak: '#e0b050' }, swing: ['wingN'], far: ['wingF'], grp: { legs: 'legs', body: 'torso' }, piv: { swing: [86, 128], far: [128, 126], head: [108, 110], torso: [106, 200] } },
  ({ S, raw, T, G, L, eye }) => {
    G('wingF', () => S('M126 124 C150 96 180 96 200 112 L188 122 L198 136 L182 138 L190 154 L172 150 L174 166 L156 156 C142 150 130 140 126 132 Z', T.dark, { sh: 6, far: true }));
    G('wingN', () => S('M88 126 C58 98 30 102 10 122 L24 130 L12 146 L30 148 L22 166 L42 160 L40 178 L60 166 C76 160 88 146 90 134 Z', T.feather, { sh: 7, inner: '<g stroke="#241e24" stroke-width="3" opacity="0.6" stroke-linecap="round"><path d="M62 120 l-10 16 M46 118 l-10 16 M30 122 l-8 12"/></g>' }));
    G('legs', () => { L([[[[94, 192], [92, 208], [94, 220]], 8, 6], [[[116, 192], [118, 208], [118, 220]], 8, 6]], 'beak'); raw('<g fill="#e0b050" stroke="#2c1626" stroke-width="1.4" stroke-linejoin="round"><path d="M86 228 L90 218 L96 226 L100 218 L106 228 Z"/><path d="M110 228 L114 218 L120 226 L124 218 L130 228 Z"/></g>'); });
    G('body', () => S('M70 154 C66 124 84 108 106 108 C128 108 142 126 140 156 C138 184 124 202 104 202 C84 202 72 182 70 154 Z', T.feather, { sh: 10, hl: 6, inner: '<g stroke="#241e24" stroke-width="3" opacity="0.5" stroke-linecap="round"><path d="M88 160 l8 6 M106 164 l8 -3 M94 178 l8 5 M112 180 l8 -3"/></g>' }));
    G('head', () => {
      S('M82 118 L74 98 L90 106 L94 88 L106 104 L116 88 L122 106 L138 98 L130 120 C116 128 96 128 82 118 Z', T.ruff, { sh: 4 });
      S('M142 58 C160 54 176 62 178 76 C178 84 172 90 166 88 C166 80 160 74 146 74 Z', T.beak, { sh: 3, hl: 2, inner: '<path d="M170 72 C176 76 176 84 168 88 L164 80 Z" fill="#3a2a22"/>' });
      S('M96 112 C92 90 100 74 114 64 C120 50 136 46 146 52 C154 56 156 68 152 76 C148 84 138 86 130 84 C122 90 120 100 120 114 Z', T.skin, { sh: 7, hl: 5, inner: '<g stroke="#a8483a" stroke-width="2" opacity="0.6" stroke-linecap="round"><path d="M102 96 l10 2 M104 84 l8 4"/></g>' });
      eye(136, 64, 7.5, 6.5, { iris: '#ffe14a', pupilK: 0.5, lid: 0.46, tilt: 1 });
    });
  });

// 4 · élite — Lionne noire : elle rampe vers sa proie, des braises dans le regard
Mo('fauves', 4, 'Lionne noire', { scale: 1.16, atk: 'slash', wind: -14, hit: 22, colors: { fur: '#3a3238', dark: '#241e24', pale: '#7a6a6c' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [116, 172], back: [34, 178], torso: [86, 198] }, shine: [[16, 112, 9, EMBER]], shineGrp: 'back' },
  ({ S, raw, T, TK, G, L, beast, halo, eye, disc }) => {
    const legs = beast({ front: 118, hind: 50, top: 192, w: 16, t: 'fur', dark: 'dark', claws: true });
    halo(16, 112, 14, EMBER, 0.85);
    G('tail', () => { L([[[[36, 178], [2, 172], [14, 122]], 10, 5]], 'fur', { N: 18 }); S('M8 124 C4 112 12 104 14 94 C22 104 26 114 20 124 C18 128 10 128 8 124 Z', TK('#ff9a2a'), { sh: 2, hl: 3 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M30 182 C30 162 50 154 80 154 C110 154 136 160 142 178 C144 196 120 206 86 206 C54 206 32 200 30 182 Z', T.fur, { sh: 9, hl: 6, inner: cracks('M50 172 L64 180 L76 168 L90 178 M104 166 L112 178') }));
    G('head', () => {
      S(disc(124, 132, 11), T.fur, { sh: 4, inner: '<circle cx="124" cy="132" r="5.5" fill="#7a6a6c"/>' }); S(disc(152, 124, 9.5), T.dark, { sh: 3 });
      S('M108 164 C106 142 124 128 146 128 C164 128 180 138 186 152 C190 160 189 170 183 177 C173 187 157 192 141 191 C122 190 109 178 108 164 Z', T.fur, { sh: 9, hl: 6,
        inner: '<path d="M156 162 C168 158 180 160 190 166 L188 182 L150 186 Z" fill="#7a6a6c" opacity="0.7" filter="url(#g2)"/><path d="M178 152 C183 150 189 154 188 160 C183 162 178 158 178 152 Z" fill="#120a0e"/><path d="M186 168 C176 174 164 176 152 174" stroke="#120a0e" stroke-width="2.4" fill="none" stroke-linecap="round"/>' });
      raw(`<path d="M178 171 L176 184 L171 173 Z M164 175 L163 186 L158 176 Z" fill="${IVORY}" stroke="#120a0e" stroke-width="1" stroke-linejoin="round"/>`);
      halo(156, 150, 12, EMBER, 0.7);
      eye(156, 150, 9.5, 7.5, { sclera: '#ffd76a', iris: EMBER, pupil: 'slit', lid: 0.42, tilt: 1 });
    });
  });

// 5 · boss — Buffle de braise : une montagne de suie, des cornes immenses, de la fumée aux naseaux
Mo('fauves', 5, 'Buffle de braise', { scale: 1.36, atk: 'smash', wind: -18, hit: 24, fx: EMBER, colors: { fur: '#3e3438', dark: '#261f24', horn: '#d8c8a8', pale: '#6a5a5c' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [118, 160], back: [30, 150], torso: [86, 196] }, shine: [[196, 166, 10, EMBER]], shineGrp: 'swing' },
  ({ S, raw, T, TK, G, L, beast, fringe, halo, eye, limb }) => {
    const legs = beast({ front: 106, hind: 50, top: 186, w: 26, t: 'fur', dark: 'dark', hoof: true });
    G('tail', () => { L([[[[30, 150], [14, 168], [20, 190]], 7, 5]], 'dark'); S('M14 190 C10 200 16 210 22 214 C28 206 28 196 24 188 Z', TK('#ff9a2a'), { sh: 2, hl: 3 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M26 170 C22 130 50 106 86 100 C112 96 136 110 142 142 C146 168 138 188 128 198' + fringe(128, 36, 198, 8, 11) + ' C28 190 26 180 26 170 Z', T.fur, { sh: 12, hl: 8,
      inner: cracks('M48 140 L62 152 L56 168 L72 178 M84 124 L96 138 L90 154 M112 160 L120 174') }));
    G('head', () => {
      // les cornes partent de sous le front
      S(limb([[156, 114], [206, 100], [198, 56]], 17, 3, 18), T.horn, { sh: 4, far: true }); S(limb([[128, 118], [78, 104], [88, 58]], 19, 3, 18), T.horn, { sh: 5, hl: 3 });
      halo(196, 166, 16, EMBER, 0.8);
      S('M112 144 C110 120 128 106 150 108 C168 110 182 122 188 140 C194 154 194 170 186 180 C176 190 160 188 148 192 C134 196 120 188 114 172 C112 162 112 152 112 144 Z', T.fur, { sh: 11, hl: 7,
        inner: '<path d="M160 160 C172 156 186 160 194 168 L190 186 L152 190 Z" fill="#6a5a5c" opacity="0.8" filter="url(#g2)"/><ellipse cx="184" cy="164" rx="3" ry="2.4" fill="#ffb04a"/><ellipse cx="174" cy="170" rx="2.6" ry="2" fill="#ffb04a"/><path d="M186 178 C178 184 168 185 160 182" stroke="#120a0e" stroke-width="2.4" fill="none" stroke-linecap="round"/>' });
      S('M122 118 C136 104 162 104 172 114 C162 124 136 126 122 118 Z', T.horn, { sh: 4, hl: 3 });
      eye(148, 142, 9.5, 8, { sclera: '#ffd76a', iris: EMBER, pupilK: 0.45, lid: 0.46, tilt: 1 });
    });
  });
