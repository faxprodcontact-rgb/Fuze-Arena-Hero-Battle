// LES IDOLES D'AIRAIN (feu) — d'antiques statues de bronze chauffées au rouge : métal, vert-de-gris, feu intérieur.
// Gueule ouverte découpée dans la silhouette, membres attachés sous le corps (voir LISEZMOI, « Les monstres »).
const { Mo, metal } = require('./mon6.cjs');
const BR = metal('#b87a3a'), BRD = metal('#7a4a22'), HOT = '#ff8a2a', VERD = '#5fb89a', MAW = '#2a0f14';
const seams = (d) => `<path d="${d}" stroke="#5a3214" stroke-width="2.4" fill="none" opacity="0.6" stroke-linecap="round"/>`;
const hot = (d) => `<path d="${d}" fill="${HOT}" opacity="0.85"/><path d="${d}" fill="#ffe27a" opacity="0.6" filter="url(#g2)"/>`;

// 0 · rapide — Chien de bronze : un chien de garde de temple, crinière en boucles
Mo('idoles', 0, 'Chien de bronze', { atk: 'slash', wind: -14, hit: 20, colors: { br: BR, dark: BRD }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [118, 160], back: [46, 160], torso: [88, 196] } },
  ({ S, raw, T, G, L, beast, eye, teeth, disc }) => {
    const legs = beast({ front: 112, hind: 58, top: 188, w: 18, t: 'br', dark: 'dark', claws: true });
    G('tail', () => { for (const [x, y, r] of [[40, 166, 11], [32, 148, 10], [38, 130, 9]]) S(disc(x, y, r), T.br, { sh: 4 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M42 176 C40 154 62 144 90 144 C114 144 134 154 136 174 C138 194 116 206 88 206 C60 206 44 198 42 176 Z', T.br, { sh: 9, hl: 6, inner: seams('M70 148 C66 168 68 188 74 204 M104 146 C108 166 106 188 100 204') + `<circle cx="88" cy="176" r="7" fill="${VERD}" opacity="0.7"/>` }));
    G('head', () => {
      // la crinière : des boucles rondes, derrière la tête
      for (const [x, y, r] of [[108, 124, 12], [104, 146, 12], [110, 168, 11], [124, 106, 12], [144, 98, 11]]) S(disc(x, y, r), T.dark, { sh: 4, inner: `<circle cx="${x}" cy="${y}" r="${r * 0.45}" fill="none" stroke="#5a3214" stroke-width="2" opacity="0.7"/>` });
      raw(`<path d="M192 152 L150 160 L181 175 C168 172 168 160 192 152 Z" fill="${MAW}"/>` + hot('M152 162 C162 158 172 162 178 170 C170 174 160 174 152 168 Z'));
      S('M112 146 C110 122 128 108 150 108 C170 108 186 120 192 138 C194 144 194 148 192 151 L154 159 L184 176 C176 186 160 190 144 188 C126 186 112 170 112 146 Z', T.br, { sh: 9, hl: 6,
        inner: seams('M166 112 C172 120 172 130 168 138') + '<path d="M180 132 C186 130 192 134 192 140 C186 142 180 138 180 132 Z" fill="#5a3214"/>' });
      teeth([188, 152], [158, 158.5], 4, 7, 1, '#f4d8a0'); teeth([180, 175], [158, 162], 3, -6, 1, '#f4d8a0');
      eye(154, 130, 10, 9, { sclera: '#ffe27a', iris: HOT, pupilK: 0.45, lid: 0.42, tilt: 1, lidC: '#5a3214' });
    });
  });

// 1 · costaud — Taureau d'airain : un ventre creux où brûle un brasier
Mo('idoles', 1, 'Taureau d\'airain', { scale: 1.12, atk: 'smash', wind: -16, hit: 22, fx: HOT, colors: { br: BR, dark: BRD }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [116, 156], back: [36, 150], torso: [86, 196] }, shine: [[82, 168, 14, HOT]] },
  ({ S, raw, T, G, L, beast, halo, eye, limb }) => {
    const legs = beast({ front: 108, hind: 54, top: 186, w: 23, t: 'br', dark: 'dark', hoof: true, hoofT: '#5a3214' });
    halo(82, 168, 26, HOT, 0.7);
    G('tail', () => L([[[[38, 150], [20, 162], [24, 190]], 7, 5]], 'dark'));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M30 168 C28 128 60 110 96 112 C124 114 142 130 142 158 C142 186 120 202 88 202 C54 202 32 194 30 168 Z', T.br, { sh: 12, hl: 8,
      inner: seams('M56 120 C50 146 52 176 60 198 M118 120 C124 146 122 176 114 198') + '<path d="M68 152 L96 152 L96 184 L68 184 Z" fill="#2a0f14"/>' + hot('M72 182 C70 170 78 166 80 158 C86 166 92 170 90 182 Z') + '<path d="M68 152 L96 152 L96 184 L68 184 Z" fill="none" stroke="#5a3214" stroke-width="3"/><g fill="#5a3214"><circle cx="40" cy="160" r="2.6"/><circle cx="42" cy="178" r="2.6"/><circle cx="132" cy="150" r="2.6"/><circle cx="130" cy="172" r="2.6"/></g>' }));
    G('head', () => {
      S(limb([[156, 116], [192, 108], [190, 76]], 13, 3, 16), T.dark, { sh: 4, far: true }); S(limb([[128, 120], [96, 108], [102, 74]], 15, 3, 16), T.br, { sh: 4, hl: 3 });
      S('M112 146 C110 122 128 110 150 112 C168 114 182 126 188 144 C194 158 192 174 184 182 C174 190 160 188 148 190 C132 192 118 184 114 168 C112 160 112 152 112 146 Z', T.br, { sh: 11, hl: 7,
        inner: seams('M170 118 C176 130 176 146 170 158') + '<path d="M176 178 C182 176 188 172 190 166" stroke="#5a3214" stroke-width="2.4" fill="none" stroke-linecap="round"/>' + hot('M180 160 C184 158 188 160 188 164 C184 166 180 164 180 160 Z') + '<path d="M176 170 a7 8 0 1 0 10 -1" stroke="#7a4a22" stroke-width="3" fill="none"/>' });
      eye(146, 144, 9.5, 8.5, { sclera: '#ffe27a', iris: HOT, pupilK: 0.45, lid: 0.44, tilt: 1, lidC: '#5a3214' });
    });
  });

// 2 · tireur — Archer de bronze : une statue qui bande son arc sans jamais se lasser
Mo('idoles', 2, 'Archer de bronze', { atk: 'shoot', fx: HOT, colors: { br: BR, dark: BRD }, swing: ['armN'], far: ['bow'], grp: { base: 'legs', body: 'torso' }, piv: { swing: [92, 126], far: [130, 126], head: [110, 104], torso: [106, 200] } },
  ({ S, raw, T, G, L, eye, limb, disc, bar }) => {
    G('bow', () => { raw('<path d="M158 66 L122 128 L158 190" stroke="#f4d8a0" stroke-width="1.8" fill="none"/>'); S(limb([[158, 64], [196, 128], [158, 192]], 8, 8, 18), T.dark, { sh: 3 }); L([[[[128, 126], [150, 122], [176, 128]], 14, 12]], 'dark', { far: true }); S(disc(178, 128, 8), T.dark, { sh: 3 }); S(bar([118, 128], [196, 128], 3.5), T.br, { sh: 1 }); S('M208 128 L194 120 L194 136 Z', T.br, { sh: 2 }); });
    G('base', () => { S('M64 206 L148 206 L156 228 L56 228 Z', T.dark, { sh: 5, inner: seams('M60 216 L152 216') }); L([[[[94, 176], [92, 194], [92, 208]], 17, 16], [[[120, 176], [124, 194], [122, 208]], 17, 16]], 'br'); });
    G('body', () => S('M78 132 C76 114 90 106 108 106 C126 106 140 114 138 132 L132 176 C130 184 86 184 84 176 Z', T.br, { sh: 9, hl: 6,
      inner: seams('M108 110 L108 180 M84 156 L132 156') + `<path d="M92 128 C100 120 116 120 124 128 C120 140 96 140 92 128 Z" fill="${VERD}" opacity="0.6"/>` }));
    G('armN', () => { L([[[[92, 128], [78, 140], [116, 130]], 15, 12]], 'br'); S(disc(120, 129, 8), T.br, { sh: 3 }); });
    G('head', () => {
      S('M88 60 C96 40 124 40 132 60 L128 70 L92 70 Z', T.dark, { sh: 4 }); S('M104 46 L110 24 L116 46 Z', T.br, { sh: 3 });
      S('M86 84 C84 66 96 56 110 56 C124 56 136 66 134 84 C134 100 124 110 110 110 C96 110 86 100 86 84 Z', T.br, { sh: 8, hl: 5, inner: seams('M100 98 C106 102 116 102 122 98') + '<path d="M118 86 l5 6 l-6 1" stroke="#5a3214" stroke-width="2" fill="none" stroke-linecap="round"/>' });
      eye(104, 80, 8, 6.5, { sclera: '#ffe27a', iris: HOT, pupil: 'none', irisK: 0.6, lid: 0.44, tilt: 1, lidC: '#5a3214' }); eye(124, 80, 6.5, 6.5, { sclera: '#ffe27a', iris: HOT, pupil: 'none', irisK: 0.6, lid: 0.44, tilt: -1, lidC: '#5a3214' });
    });
  });

// 3 · sorts — Porteuse d'encens : sa fumée referme les fissures du bronze
Mo('idoles', 3, 'Porteuse d\'encens', { atk: 'cast', heal: true, fx: '#bfe8d8', colors: { br: BR, dark: BRD }, swing: ['censer'], grp: { skirt: 'legs', body: 'torso' }, piv: { swing: [124, 130], head: [106, 100], torso: [106, 200] }, shine: [[170, 168, 9, HOT]], shineGrp: 'swing' },
  ({ S, raw, T, G, L, glow, halo, eye, disc, ell }) => {
    halo(170, 168, 14, HOT, 0.8);
    G('skirt', () => S('M74 150 C70 180 62 206 56 228 L156 228 C150 206 142 180 138 150 Z', T.br, { sh: 9, hl: 6, inner: seams('M88 156 C84 184 80 208 78 226 M106 156 L106 226 M124 156 C128 184 132 208 134 226') + `<path d="M58 216 L154 216" stroke="${VERD}" stroke-width="6" opacity="0.6"/>` }));
    // l'encensoir pend à ses chaînes ; le bras qui le tient part de sous l'épaule
    G('censer', () => { raw('<path d="M158 126 L162 152 M158 126 L178 152" stroke="#7a4a22" stroke-width="2.4" fill="none"/>'); glow('<g fill="#f4fff8" opacity="0.85" filter="url(#g3)"><circle cx="176" cy="138" r="8"/><circle cx="188" cy="120" r="11"/><circle cx="178" cy="98" r="9"/><circle cx="190" cy="80" r="6"/></g>'); S(ell(170, 164, 15, 14), T.dark, { sh: 4, hl: 3, inner: hot('M160 162 L180 162 L178 168 L162 168 Z') }); S('M162 150 L178 150 L174 140 L166 140 Z', T.dark, { sh: 2 }); L([[[[124, 130], [146, 138], [158, 124]], 13, 11]], 'br'); S(disc(158, 124, 7.5), T.br, { sh: 3 }); });
    G('body', () => S('M80 128 C78 112 92 106 106 106 C120 106 134 112 132 128 L138 156 C120 164 92 164 74 156 Z', T.br, { sh: 8, hl: 5, inner: seams('M82 140 C96 148 116 148 130 140') + `<circle cx="106" cy="128" r="6" fill="${VERD}" opacity="0.8"/>` }));
    G('head', () => {
      S(disc(106, 44, 12), T.dark, { sh: 4 });
      S('M82 82 C78 62 92 50 106 50 C120 50 134 62 130 82 C130 98 120 108 106 108 C92 108 82 98 82 82 Z', T.br, { sh: 8, hl: 5, inner: '<path d="M80 74 C90 58 122 58 132 74 C120 66 92 66 80 74 Z" fill="#7a4a22"/>' + seams('M98 96 C102 99 110 99 114 96') });
      raw('<path d="M92 80 q7 5 14 0 M112 80 q6 5 12 0" stroke="#5a3214" stroke-width="2.6" fill="none" stroke-linecap="round"/>');
    });
  });

// 4 · élite — Colosse : un guerrier de bronze fissuré, le métal rouge par endroits
Mo('idoles', 4, 'Colosse', { scale: 1.2, atk: 'smash', wind: -60, hit: 40, colors: { br: BR, dark: BRD }, swing: ['armN'], far: ['armF'], grp: { farLeg: 'legs', leg: 'legs', body: 'torso' }, piv: { swing: [82, 120], far: [134, 120], head: [108, 96], torso: [106, 200] } },
  ({ S, raw, T, G, L, eye, disc, ell }) => {
    G('armF', () => { L([[[[134, 122], [162, 138], [168, 164]], 22, 20]], 'dark', { far: true }); S(disc(168, 168, 14), T.dark, { sh: 4, far: true }); });
    G('farLeg', () => { L([[[[124, 186], [130, 208], [128, 218]], 24, 22]], 'dark', { far: true }); S('M112 216 L148 216 L152 228 L110 228 Z', T.dark, { sh: 3, far: true }); });
    G('leg', () => { L([[[[88, 188], [82, 208], [84, 218]], 26, 24]], 'br'); S('M66 216 L104 216 L108 228 L64 228 Z', T.br, { sh: 3 }); });
    G('armN', () => { L([[[[82, 122], [50, 110], [52, 74]], 24, 22]], 'br', { inner: hot('M56 100 L64 108 L58 116 Z') }); S(disc(52, 68, 16), T.br, { sh: 5 }); });
    G('body', () => S('M64 124 C62 104 84 96 108 96 C132 96 154 104 152 124 L142 184 C140 196 76 196 74 184 Z', T.br, { sh: 12, hl: 8,
      inner: seams('M108 100 L108 190 M78 150 L138 150') + hot('M92 118 L104 132 L96 146 L110 160 L104 136 L112 124 Z') + `<path d="M124 110 C134 108 144 114 146 124 C138 128 128 124 124 110 Z" fill="${VERD}" opacity="0.6"/>` }));
    G('head', () => {
      S('M96 52 L108 22 L120 52 Z', T.dark, { sh: 4 });
      S('M82 78 C80 58 94 48 108 48 C124 48 138 58 136 78 L136 88 C136 100 124 108 108 108 C94 108 82 100 82 90 Z', T.br, { sh: 9, hl: 6, inner: '<path d="M88 70 L132 70 L132 86 L116 86 L112 104 L104 104 L104 86 L88 86 Z" fill="#2a0f14"/>' });
      raw(`<path d="M94 74 L104 78 L94 82 Z M128 74 L116 78 L128 82 Z" fill="${HOT}"/><path d="M94 74 L104 78 L94 82 Z M128 74 L116 78 L128 82 Z" fill="#ffe27a" opacity="0.6" filter="url(#g2)"/>`);
    });
  });

// 5 · boss — Grande Idole : une statue assise à tête de bête, un brasier dans le ventre
Mo('idoles', 5, 'Grande Idole', { scale: 1.36, atk: 'smash', wind: -50, hit: 36, fx: HOT, colors: { br: BR, dark: BRD }, swing: ['armN'], far: ['armF'], grp: { base: 'legs', body: 'torso' }, piv: { swing: [70, 130], far: [142, 130], head: [106, 96], torso: [106, 200] }, shine: [[106, 168, 18, HOT]] },
  ({ S, raw, T, G, L, halo, eye, teeth, limb, disc }) => {
    halo(106, 168, 34, HOT, 0.75);
    G('armF', () => { L([[[[142, 132], [176, 140], [184, 112]], 22, 18]], 'dark', { far: true }); S(disc(186, 106, 13), T.dark, { sh: 4, far: true }); });
    G('base', () => { S('M40 196 C60 186 152 186 172 196 L180 228 L32 228 Z', T.dark, { sh: 6, inner: seams('M36 212 L176 212') }); S('M52 206 C56 188 84 184 100 196 L100 214 L54 214 Z', T.br, { sh: 4 }); S('M160 206 C156 188 128 184 112 196 L112 214 L158 214 Z', T.br, { sh: 4, far: true }); });
    G('armN', () => { L([[[[70, 132], [38, 138], [34, 104]], 24, 20]], 'br'); S(disc(34, 98, 15), T.br, { sh: 5 }); });
    G('body', () => S('M56 150 C52 118 76 104 106 104 C136 104 160 118 156 150 C154 184 136 202 106 202 C76 202 58 184 56 150 Z', T.br, { sh: 12, hl: 8,
      inner: '<path d="M82 146 C82 134 130 134 130 146 L130 186 L82 186 Z" fill="#2a0f14"/>' + hot('M88 184 C84 168 96 162 98 150 C106 160 112 152 114 144 C122 158 128 170 124 184 Z') + '<g stroke="#5a3214" stroke-width="4" fill="none"><path d="M82 146 C82 134 130 134 130 146 L130 186 L82 186 Z"/><path d="M94 140 L94 186 M106 138 L106 186 M118 140 L118 186"/></g>' + `<path d="M62 132 C70 118 84 112 96 110" stroke="${VERD}" stroke-width="6" fill="none" opacity="0.6" stroke-linecap="round"/>` }));
    G('head', () => {
      S(limb([[132, 60], [164, 48], [162, 18]], 14, 3, 16), T.dark, { sh: 4, far: true }); S(limb([[82, 62], [48, 50], [50, 18]], 16, 3, 16), T.br, { sh: 4, hl: 3 });
      raw(`<path d="M150 92 L108 98 L141 111 C128 108 128 98 150 92 Z" fill="${MAW}"/>` + hot('M112 100 C122 97 132 100 138 106 C130 110 120 110 112 106 Z'));
      S('M68 86 C64 60 84 44 108 44 C130 44 146 56 150 76 C151 82 151 87 150 91 L112 98 L144 113 C136 124 120 128 104 126 C84 124 70 108 68 86 Z', T.br, { sh: 10, hl: 7, inner: seams('M92 48 C88 62 90 76 96 86') + '<path d="M138 72 C143 70 149 74 148 80 C143 82 138 78 138 72 Z" fill="#5a3214"/>' });
      teeth([146, 92], [116, 97.5], 4, 8, 1, '#f4d8a0'); teeth([140, 112], [116, 101], 3, -7, 1, '#f4d8a0');
      eye(112, 70, 11, 9.5, { sclera: '#ffe27a', iris: HOT, pupilK: 0.45, lid: 0.44, tilt: 1, lidC: '#5a3214' });
    });
  });
