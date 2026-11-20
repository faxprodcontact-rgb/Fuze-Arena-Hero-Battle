// LA VOLIÈRE D'ORAGE (vent) — les oiseaux de la tempête : plumes d'ardoise, éclairs, nuages.
// Becs ouverts découpés dans la silhouette, ailes et pattes attachées sous le corps (voir LISEZMOI, « Les monstres »).
const { Mo } = require('./mon6.cjs');
const BOLT = '#ffe14a', SKY = '#6a7a9a', MAW = '#3a1420';
const talons = (x, c = '#e0b050') => `<path d="M${x - 10} 228 L${x - 5} 216 L${x} 226 L${x + 5} 216 L${x + 11} 228 Z" fill="${c}" stroke="#2c1626" stroke-width="1.4" stroke-linejoin="round"/>`;
const spark = (d) => `<path d="${d}" stroke="${BOLT}" stroke-width="6" fill="none" opacity="0.5" filter="url(#g2)" stroke-linejoin="round"/><path d="${d}" stroke="#fffbe0" stroke-width="2.4" fill="none" stroke-linejoin="round" stroke-linecap="round"/>`;

// 0 · rapide — Faucon : il pique, ailes en flèche, serres ouvertes
Mo('voliere', 0, 'Faucon', { scale: 0.94, atk: 'stab', wind: -12, hit: 16, colors: { fea: '#5a6a8a', dark: '#3a4660', pale: '#f0e8d8', beak: '#e8b83a' }, grp: { tailF: 'back', wingF: 'back', wingN: 'back', claws: 'torso', body: 'torso' }, piv: { back: [88, 140], torso: [112, 150] } },
  ({ S, raw, T, G, eye }) => {
    G('tailF', () => S('M70 152 L16 150 L28 162 L14 172 L32 176 L26 190 L76 170 Z', T.dark, { sh: 4 }));
    G('wingF', () => S('M112 126 C96 84 56 60 14 64 L38 80 L22 88 L46 98 L34 108 L62 116 C82 126 102 132 112 126 Z', T.dark, { sh: 5, far: true }));
    // les serres partent de sous le ventre, tendues vers la proie
    G('claws', () => raw('<g fill="#e8b83a" stroke="#2c1626" stroke-width="1.6" stroke-linejoin="round"><path d="M112 168 L132 178 L154 174 L148 184 L166 192 L146 196 L150 208 L128 196 L106 182 Z"/><path d="M90 170 L104 186 L122 188 L114 196 L126 208 L106 206 L104 216 L90 200 L80 180 Z"/></g>'));
    G('body', () => {
      // bec crochu, sous la tête
      S('M158 134 C172 130 186 138 188 152 C188 160 182 164 176 160 C176 154 170 150 158 152 Z', T.beak, { sh: 3, hl: 2, inner: '<path d="M180 148 C186 152 186 160 178 162 L174 154 Z" fill="#3a2a22"/>' });
      S('M66 158 C72 134 104 118 136 120 C156 122 170 132 170 146 C170 160 152 172 128 176 C102 180 74 176 66 158 Z', T.fea, { sh: 9, hl: 6,
        inner: '<path d="M96 172 C122 176 150 170 170 150 L174 188 L92 188 Z" fill="#f0e8d8" opacity="0.95" filter="url(#g2)"/><path d="M150 148 C152 158 148 168 140 174 L132 166 C140 160 142 154 142 148 Z" fill="#1c2030"/><g stroke="#3a4660" stroke-width="2.6" stroke-linecap="round" opacity="0.7"><path d="M106 168 l8 5 M122 166 l8 4"/></g>' });
      eye(150, 138, 9, 8, { iris: BOLT, pupilK: 0.5, lid: 0.5, tilt: 1 });
    });
    G('wingN', () => S('M124 134 C104 92 62 70 20 76 L44 90 L28 98 L52 108 L40 118 L68 126 C90 138 114 142 124 134 Z', T.fea, { sh: 6, inner: '<g stroke="#3a4660" stroke-width="2.6" opacity="0.6" stroke-linecap="round"><path d="M98 118 l-16 4 M82 106 l-16 2 M64 96 l-14 0"/></g>' }));
  });

// 1 · costaud — Marabout : un grand échassier voûté, au bec comme une pioche
Mo('voliere', 1, 'Marabout', { scale: 1.12, atk: 'smash', wind: -26, hit: 30, colors: { fea: '#4a5266', dark: '#2e3444', pale: '#e8e4d8', skin: '#8a94a8', pouch: '#d88a7a', beak: '#d8c8a0', leg: '#8a8a94' }, swing: ['head'], grp: { legs: 'legs', body: 'torso' }, piv: { swing: [112, 128], torso: [100, 180] } },
  ({ S, raw, T, G, L, eye, limb }) => {
    G('legs', () => { L([[[[90, 176], [86, 204], [90, 222]], 7, 6], [[[112, 176], [116, 204], [114, 222]], 7, 6]], 'leg'); raw(talons(92, '#8a8a94') + talons(116, '#8a8a94')); });
    G('body', () => S('M52 150 C50 120 72 104 98 106 C122 108 138 124 136 148 C134 172 116 184 94 184 C70 184 54 174 52 150 Z', T.fea, { sh: 10, hl: 6,
      inner: '<path d="M88 134 C104 128 124 132 134 146 C128 170 108 182 90 180 C84 164 84 148 88 134 Z" fill="#e8e4d8"/><path d="M56 152 L30 164 L52 164 L36 178 L62 172 Z" fill="#2e3444"/>' }));
    G('head', () => {
      // le bec et la poche de gorge partent de sous la tête
      S('M134 84 C150 96 162 122 164 152 C152 136 140 120 130 108 Z', T.beak, { sh: 4, hl: 3, inner: '<path d="M134 88 C146 104 156 126 162 148" stroke="#8a7a50" stroke-width="2" fill="none" opacity="0.7"/>' });
      S(limb([[124, 108], [134, 126], [124, 142]], 15, 10), T.pouch, { sh: 3 });
      S('M100 124 C96 100 100 78 114 70 C126 64 140 70 142 84 C144 96 136 104 128 106 C124 114 122 122 122 132 Z', T.skin, { sh: 7, hl: 5, inner: '<path d="M104 82 C106 66 122 60 136 68 C126 66 114 72 108 86 Z" fill="#2e3444"/>' });
      eye(124, 84, 7.5, 7, { iris: BOLT, pupilK: 0.5, lid: 0.5, tilt: 1 });
    });
  });

// 2 · tireur — Corbeau : il lâche des pierres de foudre du haut de son vol
Mo('voliere', 2, 'Corbeau lanceur', { scale: 0.94, atk: 'cast', fx: BOLT, colors: { fea: '#2e2a3a', dark: '#1c1a26', beak: '#a8a2b4', stone: '#8a8a9c' }, swing: ['wingN'], far: ['wingF'], grp: { tailF: 'back', stone: 'torso', body: 'torso' }, piv: { swing: [96, 120], far: [124, 118], back: [78, 150], torso: [110, 140] }, shine: [[118, 190, 11, BOLT]] },
  ({ S, raw, T, G, halo, eye }) => {
    halo(118, 190, 18, BOLT, 0.8);
    G('wingF', () => S('M122 116 C140 82 172 72 200 86 L186 96 L196 108 L180 112 L186 126 L168 126 L170 140 C152 140 132 134 122 126 Z', T.dark, { sh: 6, far: true }));
    G('tailF', () => S('M78 146 L44 164 L60 166 L48 180 L66 178 L62 192 L90 168 Z', T.dark, { sh: 4 }));
    // la pierre est dans ses serres, sous le ventre
    G('stone', () => { S('M100 180 L118 172 L136 180 L134 200 L116 208 L102 200 Z', T.stone, { sh: 4, hl: 3, inner: spark('M112 180 L120 188 L114 194 L124 202') }); raw('<g stroke="#4a4654" stroke-width="4" stroke-linecap="round" fill="none"><path d="M106 168 L104 184 M118 166 L118 176 M130 168 L132 184"/></g>'); });
    G('body', () => {
      raw(`<path d="M186 122 L156 126 L176 136 C168 132 168 126 186 122 Z" fill="${MAW}"/>`);
      S('M146 106 C168 104 186 112 196 121 L162 126 L190 140 C176 146 158 144 146 136 Z', T.beak, { sh: 3, hl: 2 });
      S('M72 142 C70 118 90 100 116 100 C140 100 158 112 160 130 C162 152 142 172 114 172 C92 172 74 162 72 142 Z', T.fea, { sh: 9, hl: 6, inner: '<path d="M84 150 C100 164 126 164 144 152" stroke="#4a4660" stroke-width="5" fill="none" opacity="0.6" stroke-linecap="round"/>' });
      S('M104 104 L100 88 L112 98 L118 84 L124 100 Z', T.dark, { sh: 3 });
      eye(138, 122, 9, 8.5, { iris: BOLT, pupilK: 0.5, lid: 0.5, tilt: 1 });
    });
    G('wingN', () => S('M98 118 C76 80 42 68 12 82 L28 94 L16 106 L34 110 L26 124 L46 124 L44 140 C66 140 88 134 98 126 Z', T.fea, { sh: 7, inner: '<g stroke="#1c1a26" stroke-width="3" opacity="0.7" stroke-linecap="round"><path d="M74 100 l-10 14 M56 94 l-10 14 M38 94 l-8 12"/></g>' }));
  });

// 3 · sorts — Paon d'orage : sa roue crépite d'éclairs
Mo('voliere', 3, 'Paon d\'orage', { atk: 'cast', fx: BOLT, colors: { fea: '#2a7aa8', dark: '#1f4a6a', fan: '#3a4a7a', beak: '#e0b050' }, grp: { fan: 'back', legs: 'legs', body: 'torso' }, piv: { back: [100, 170], head: [116, 140], torso: [104, 200] } },
  ({ S, raw, T, G, L, halo, eye, limb }) => {
    halo(96, 96, 60, '#8fb8ff', 0.4);
    G('fan', () => S('M100 174 L18 150 L30 124 L14 100 L40 88 L34 60 L62 60 L66 32 L90 42 L104 20 L118 42 L142 32 L146 60 L174 60 L168 88 L194 100 L178 124 L190 150 Z', T.fan, { sh: 10, hl: 6,
      inner: [[40, 118], [58, 80], [104, 56], [150, 80], [168, 118]].map(([x, y]) => `<ellipse cx="${x}" cy="${y}" rx="11" ry="13" fill="#2fc8d8"/><ellipse cx="${x}" cy="${y + 2}" rx="6" ry="7.5" fill="#ffe14a"/><ellipse cx="${x}" cy="${y + 3}" rx="3" ry="4" fill="#1c1a26"/>`).join('') + spark('M82 150 L70 128 L84 122 L76 100 M126 150 L138 128 L124 122 L134 100') }));
    G('legs', () => { L([[[[94, 198], [92, 212], [94, 222]], 6, 5], [[[112, 198], [116, 212], [114, 222]], 6, 5]], 'beak'); raw(talons(96) + talons(116)); });
    G('head', () => {
      S('M140 100 L162 106 L140 114 Z', T.beak, { sh: 3 });
      raw('<g stroke="#1f4a6a" stroke-width="2.4" stroke-linecap="round"><path d="M118 82 L112 62 M124 80 L126 58 M130 82 L140 64"/></g><g fill="#2fc8d8" stroke="#2c1626" stroke-width="1.4"><circle cx="112" cy="60" r="4.5"/><circle cx="126" cy="56" r="4.5"/><circle cx="141" cy="62" r="4.5"/></g>');
      S('M96 166 C94 140 100 118 110 104 C110 90 122 80 134 84 C144 88 148 100 144 110 C140 118 132 120 126 120 C122 134 122 150 124 168 Z', T.fea, { sh: 8, hl: 5 });
      eye(130, 100, 7.5, 7, { iris: BOLT, pupilK: 0.5, lid: 0.46, tilt: 1 });
    });
    G('body', () => S('M70 180 C68 160 84 150 104 150 C124 150 138 162 136 180 C134 196 120 204 102 204 C84 204 72 196 70 180 Z', T.fea, { sh: 9, hl: 6, inner: '<path d="M76 184 C86 196 118 198 132 186" stroke="#1f4a6a" stroke-width="5" fill="none" opacity="0.6" stroke-linecap="round"/>' }));
  });

// 4 · élite — Casoar : un grand coureur au casque d'os, un coup de patte qui ouvre une armure
Mo('voliere', 4, 'Casoar', { scale: 1.2, atk: 'slash', wind: -30, hit: 34, colors: { fea: '#2a2c3a', dark: '#1a1c28', neck: '#2f6fd8', casque: '#a8946a', wattle: '#d8382e', leg: '#8a8a94', beak: '#3a3a44' }, swing: ['legN'], grp: { legF: 'legs', body: 'torso' }, piv: { swing: [112, 176], head: [118, 120], torso: [96, 180] } },
  ({ S, raw, T, G, L, fringe, eye, limb }) => {
    const foot = (x, y, far) => S(`M${x - 8} ${y} L${x - 6} ${y - 10} L${x + 6} ${y - 12} L${x + 28} ${y - 4} L${x + 14} ${y - 3} L${x + 22} ${y} Z`, T.leg, { sh: 3, far });
    G('legF', () => { L([[[[90, 176], [82, 200], [88, 220]], 12, 9]], 'leg', { far: true }); foot(88, 228, true); });
    // la patte qui frappe est levée, griffe en avant
    G('legN', () => { L([[[[112, 176], [136, 186], [150, 172]], 13, 10]], 'leg'); S('M144 176 L148 164 L160 162 L186 172 L170 174 L180 180 L152 182 Z', T.leg, { sh: 3 }); });
    G('head', () => {
      S('M126 88 C120 102 130 112 134 98 Z', T.wattle, { sh: 2 }); S('M136 88 C134 102 144 108 144 94 Z', T.wattle, { sh: 2 });
      S('M146 68 L176 78 L146 86 Z', T.beak, { sh: 3 });
      S('M100 124 C98 100 106 80 118 70 C120 58 132 52 142 58 C150 62 152 74 148 82 C144 90 136 92 130 90 C126 100 126 112 128 126 Z', T.neck, { sh: 8, hl: 5 });
      S('M118 64 C118 40 132 28 146 34 C142 44 142 54 146 62 C138 56 126 58 118 64 Z', T.casque, { sh: 4, hl: 3 });
      eye(136, 72, 7.5, 7, { iris: BOLT, pupilK: 0.5, lid: 0.5, tilt: 1 });
    });
    G('body', () => S('M44 156 C42 124 68 106 98 108 C124 110 140 128 138 154 C137 166 132 176 124 184' + fringe(124, 52, 186, 6, 12) + ' C46 176 44 166 44 156 Z', T.fea, { sh: 11, hl: 7, inner: '<g stroke="#1a1c28" stroke-width="3" opacity="0.6" stroke-linecap="round"><path d="M64 134 l-4 30 M80 126 l-2 40 M98 124 l0 42 M114 130 l4 36"/></g>' }));
  });

// 5 · boss — Oiseau-tonnerre : l'esprit de l'orage, les ailes chargées d'éclairs
Mo('voliere', 5, 'Oiseau-tonnerre', { scale: 1.36, atk: 'smash', wind: -40, hit: 36, fx: BOLT, colors: { fea: '#3a5a9a', dark: '#243a6a', gold: '#ffd23a', pale: '#e8f4ff', beak: '#ffb020' }, swing: ['wingN'], far: ['wingF'], grp: { tailF: 'back', claws: 'legs', body: 'torso' }, piv: { swing: [88, 126], far: [126, 124], head: [110, 104], back: [106, 180], torso: [106, 170] }, shine: [[112, 152, 12, BOLT]] },
  ({ S, raw, T, G, halo, eye }) => {
    halo(106, 120, 70, '#8fb8ff', 0.4);
    G('wingF', () => S('M124 122 C142 66 178 50 208 62 L194 76 L208 88 L190 96 L202 112 L182 114 L190 132 L170 130 L172 150 C150 148 132 136 124 130 Z', T.dark, { sh: 7, far: true, inner: spark('M150 110 L164 96 L158 88 L176 76') }));
    G('tailF', () => S('M90 180 L80 222 L96 206 L106 226 L116 206 L132 222 L122 180 Z', T.gold, { sh: 4 }));
    G('claws', () => raw(talons(92).replace(/228/g, '206').replace(/226/g, '204').replace(/216/g, '192') + talons(122).replace(/228/g, '206').replace(/226/g, '204').replace(/216/g, '192')));
    G('body', () => S('M70 148 C68 122 86 108 106 108 C126 108 144 122 142 148 C140 176 124 192 106 192 C88 192 72 176 70 148 Z', T.fea, { sh: 11, hl: 7,
      inner: '<path d="M84 136 C98 128 118 130 130 140 C128 166 118 184 106 186 C94 184 84 164 84 136 Z" fill="#e8f4ff" opacity="0.9"/>' + spark('M112 136 L102 152 L114 156 L104 174') }));
    G('wingN', () => S('M90 124 C68 64 28 46 -2 60 L12 76 L0 88 L18 96 L8 112 L28 114 L22 132 L42 130 L42 150 C64 148 82 136 90 130 Z', T.fea, { sh: 8, inner: spark('M66 112 L50 98 L58 90 L38 78') + '<g stroke="#243a6a" stroke-width="3" opacity="0.6" stroke-linecap="round"><path d="M30 112 l10 -10 M16 96 l12 -8"/></g>' }));
    G('head', () => {
      S('M92 70 L84 46 L100 58 L106 36 L116 56 L130 42 L130 68 Z', T.gold, { sh: 4, hl: 3 });
      raw(`<path d="M172 96 L140 100 L164 114 C152 108 152 100 172 96 Z" fill="${MAW}"/>`);
      S('M136 80 C152 78 166 86 173 95 L144 100 L168 116 C158 122 142 120 132 112 Z', T.beak, { sh: 4, hl: 3 });
      S('M80 96 C78 74 92 62 110 62 C128 62 142 74 142 94 C142 112 130 124 110 124 C92 124 82 114 80 96 Z', T.fea, { sh: 9, hl: 6, inner: '<path d="M100 104 C112 112 128 110 138 100 L140 122 L96 124 Z" fill="#e8f4ff" opacity="0.8" filter="url(#g2)"/>' });
      halo(122, 88, 12, BOLT, 0.7);
      eye(122, 88, 10.5, 9, { sclera: '#fffbe0', iris: BOLT, pupilK: 0.4, lid: 0.46, tilt: 1 });
    });
  });
