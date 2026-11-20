// LA HORDE DES GLACES (eau) — les bêtes de l'âge de glace : fourrures épaisses, givre, ivoire.
// FAMILLE DE RÉFÉRENCE (niveau de qualité à tenir) : un cou relie la tête au corps, épaules et cuisses marquées, museau
// d'un seul tenant avec le crâne, touffes de poils, marques du pelage, ventre clair, griffes, sourcil dur. Un seul contour
// par créature (pas de contour par morceau), gueule ouverte découpée dans la silhouette, membres attachés sous le corps.
const { Mo } = require('./mon6.cjs');
const ICE = '#dff4ff', IVORY = '#f6ecd4', MAW = '#2a1016';

// 0 · rapide — Tigre à dents de sabre : épaules hautes, il avance tête basse, deux sabres sous la lèvre
Mo('glaces', 0, 'Tigre à dents de sabre', { scale: 1.04, atk: 'slash', wind: -14, hit: 20, colors: { fur: '#cf9550', dark: '#96642e', pale: '#f6e8cc' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [128, 150], back: [34, 160], torso: [86, 190] } },
  ({ S, raw, T, G, L, beast, neck, tuft, brow, stripes, under, eye }) => {
    const legs = beast({ front: 114, hind: 50, top: 182, w: 18, t: 'fur', dark: 'dark', claws: true });
    G('tail', () => L([[[[36, 160], [4, 168], [10, 126]], 13, 8]], 'fur', { N: 18, inner: stripes(['M8 152 l12 -2', 'M6 140 l12 2', 'M8 130 l10 4'], '#6e4218', 5) }));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      // dos : croupe basse, garrot haut ; le cou part des épaules
      S('M28 172 C26 152 44 142 68 142 C88 140 102 124 122 126 C140 128 148 146 146 168 C144 192 120 206 88 206 C54 206 30 196 28 172 Z', T.fur, { sh: 10, hl: 6,
        inner: under('M34 194 C66 212 118 208 146 184 L150 214 L32 214 Z', '#f6e8cc') + stripes(['M52 146 L56 170', 'M70 142 L72 168', 'M88 136 L88 162', 'M104 130 L102 154', 'M120 128 L116 148'], '#6e4218', 6) + '<ellipse cx="118" cy="168" rx="20" ry="26" fill="#fff" opacity="0.1"/>' });
      neck([116, 152], [138, 134], [160, 138], 52, 40, 'fur', { inner: stripes(['M128 128 L132 146', 'M142 126 L144 142'], '#6e4218', 5) });
    });
    G('head', () => {
      S('M140 116 L132 90 L156 104 Z', T.fur, { sh: 3, inner: '<path d="M142 110 L138 98 L150 106 Z" fill="#6e4218"/>' }); S('M162 104 L170 84 L180 106 Z', T.dark, { sh: 3 });
      tuft(140, 158, 200, 14, 22, 'fur', { n: 3 });
      // les sabres sortent de sous la lèvre du haut
      raw(`<path d="M202 148 L204 188 L190 150 Z M186 152 L186 182 L176 153 Z" fill="${IVORY}" stroke="#3a2416" stroke-width="1.6" stroke-linejoin="round"/>`);
      S('M130 138 C128 116 146 102 166 102 C182 102 194 110 200 122 C208 124 214 132 213 140 C212 148 206 152 199 152 C192 164 178 172 162 170 C144 168 130 156 130 138 Z', T.fur, { sh: 9, hl: 6,
        inner: under('M176 134 C190 128 206 130 216 138 L214 156 L172 160 Z', '#f6e8cc', 0.95) + '<path d="M203 126 C208 124 214 128 213 134 C208 137 203 132 203 126 Z" fill="#3a1c1c"/><path d="M210 146 C200 150 188 152 176 150" stroke="#3a1c1c" stroke-width="2.2" fill="none" stroke-linecap="round"/><g fill="#3a1c1c" opacity="0.6"><circle cx="190" cy="141" r="1.3"/><circle cx="196" cy="143" r="1.3"/><circle cx="186" cy="145" r="1.3"/></g>' + stripes(['M134 130 L146 134', 'M134 144 L146 144', 'M154 106 L156 116'], '#6e4218', 5) });
      eye(172, 124, 10, 8, { iris: '#ffb020', pupil: 'slit', lid: 0.42, tilt: 1 }); brow(172, 113, 26, 1, '#5a3214', 5);
    });
  });

// 1 · costaud — Rhinocéros laineux : une bosse d'épaules sous le givre, la tête au ras du sol, il charge
Mo('glaces', 1, 'Rhinocéros laineux', { scale: 1.12, atk: 'smash', wind: -18, hit: 24, colors: { fur: '#86583a', dark: '#5a3a24', horn: IVORY, pale: '#b8906a' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [124, 160], back: [30, 150], torso: [84, 190] } },
  ({ S, raw, T, G, L, beast, fringe, neck, tuft, brow, stripes, eye }) => {
    const legs = beast({ front: 108, hind: 50, top: 186, w: 24, t: 'fur', dark: 'dark', hoof: true });
    G('tail', () => { L([[[[32, 150], [18, 160], [20, 178]], 7, 5]], 'dark'); tuft(20, 180, 180, 14, 12, 'dark'); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      S('M26 168 C22 134 44 116 70 112 C92 100 120 102 136 122 C146 136 148 156 144 176 C140 190 136 196 130 200' + fringe(130, 38, 200, 8, 13) + ' C28 192 26 180 26 168 Z', T.fur, { sh: 12, hl: 7,
        inner: `<path d="M60 116 C80 100 116 100 134 118 C116 124 80 126 60 116 Z" fill="${ICE}" opacity="0.75" filter="url(#g2)"/>` + stripes(['M44 148 q5 16 0 32', 'M64 152 q5 16 0 32', 'M86 152 q5 18 0 34', 'M108 150 q5 16 0 32'], '#5a3a24', 3.4, 0.5) });
      neck([120, 150], [138, 160], [156, 166], 62, 52, 'fur');
    });
    G('head', () => {
      S('M138 132 L128 108 L152 120 Z', T.dark, { sh: 3 }); tuft(138, 196, 185, 14, 26, 'dark', { n: 3 });
      S('M124 158 C122 136 140 124 160 128 C178 132 196 146 206 164 C212 176 208 188 198 192 C184 198 160 200 144 194 C130 188 124 174 124 158 Z', T.fur, { sh: 10, hl: 6,
        inner: '<path d="M178 186 C188 182 198 182 206 186" stroke="#3a2416" stroke-width="2.4" fill="none" stroke-linecap="round"/><ellipse cx="200" cy="170" rx="2.8" ry="2.2" fill="#3a2416"/>' + stripes(['M130 160 l10 4', 'M134 174 l10 2', 'M150 132 l4 10'], '#5a3a24', 3, 0.5) });
      S('M188 156 C200 136 212 104 204 70 C194 96 178 122 170 144 Z', T.horn, { sh: 4, hl: 3, inner: '<path d="M196 96 L190 112 M200 116 L192 130" stroke="#b8a070" stroke-width="2" opacity="0.6"/>' }); S('M162 134 C168 122 172 110 170 96 C162 108 158 120 154 132 Z', T.horn, { sh: 3 });
      eye(160, 152, 8.5, 7.5, { iris: '#bfe9ff', pupilK: 0.5, lid: 0.46, tilt: 1 }); brow(160, 142, 22, 1, '#3a2416', 5);
    });
  });

// 2 · tireur — Narval : il lance des éclats de glace du bout de sa défense torsadée
Mo('glaces', 2, 'Narval', { atk: 'cast', fx: ICE, colors: { skin: '#7f9cbc', dark: '#4e6c8a', tusk: IVORY }, swing: ['tusk'], grp: { tail: 'back', body: 'torso' }, piv: { swing: [158, 140], back: [46, 172], torso: [106, 150] }, shine: [[214, 110, 8, ICE]], shineGrp: 'swing' },
  ({ S, raw, T, G, eye, brow, blade, spots, under }) => {
    G('tail', () => S('M56 166 C40 160 24 148 10 132 C18 156 18 176 6 200 C24 190 42 184 58 184 Z', T.dark, { sh: 5, inner: '<path d="M50 172 L22 150 M50 178 L22 190" stroke="#2a3a52" stroke-width="2" opacity="0.5"/>' }));
    G('tusk', () => { const b = blade([150, 142], [216, 109], 9, 0.05); S(b.d, T.tusk, { sh: 2, hl: 2, inner: '<g stroke="#b8a070" stroke-width="1.8" opacity="0.7"><path d="M164 132 l4 9 M175 127 l4 8 M186 122 l3 7 M197 117 l2 6"/></g>' }); });
    G('body', () => {
      S('M94 126 C96 112 102 102 110 96 C116 106 122 116 124 124 Z', T.dark, { sh: 3 });
      S('M38 172 C40 140 78 116 122 114 C150 113 168 126 170 146 C172 162 158 176 132 182 C104 190 66 194 38 172 Z', T.skin, { sh: 10, hl: 7,
        inner: under('M44 180 C80 196 130 192 168 160 L174 202 L40 202 Z', '#eef4ff', 0.9) + spots([[82, 136, 6], [104, 128, 4.5], [68, 152, 4.5], [122, 138, 3.4], [94, 150, 3], [58, 164, 3]], '#4e6c8a', 0.6) + '<path d="M168 152 C160 152 152 156 146 162" stroke="#2a3a52" stroke-width="2.4" fill="none" stroke-linecap="round"/><path d="M110 122 L128 132" stroke="#eef4ff" stroke-width="3" stroke-linecap="round" opacity="0.6"/>' });
      S('M102 174 C90 182 84 198 88 212 C104 204 116 190 120 176 Z', T.dark, { sh: 3 });
      eye(148, 136, 9, 8, { iris: '#ffe14a', pupilK: 0.5, lid: 0.42, tilt: 1 }); brow(148, 125, 22, 1, '#2a3a52', 4.5);
    });
  });

// 3 · sorts — Harfang : la chouette des neiges appelle le blizzard, serres en avant
Mo('glaces', 3, 'Harfang', { atk: 'cast', fx: ICE, colors: { white: '#f4f8ff', bar: '#7a869c', dark: '#aab4c8' }, swing: ['wingN'], far: ['wingF'], grp: { tailF: 'back', claws: 'torso', body: 'torso' }, piv: { swing: [94, 122], far: [128, 122], back: [110, 180], torso: [110, 140] } },
  ({ S, raw, T, G, eye, stripes }) => {
    const bars = (l) => stripes(l, '#7a869c', 3.4, 0.6);
    G('wingF', () => S('M124 118 C144 78 182 66 212 82 L198 94 L210 106 L194 112 L202 126 L184 128 L186 144 L166 142 C148 144 132 138 124 130 Z', T.white, { sh: 6, far: true, inner: '<path d="M130 122 C150 100 176 92 200 96 L190 110 C170 108 150 116 136 130 Z" fill="#aab4c8" opacity="0.5"/>' + bars(['M152 104 l8 12', 'M170 96 l8 14', 'M188 96 l6 10']) }));
    G('wingN', () => S('M98 118 C78 78 40 66 10 82 L24 94 L12 106 L28 112 L20 126 L38 128 L36 144 L56 142 C74 144 90 138 98 130 Z', T.white, { sh: 7, inner: '<path d="M92 122 C72 100 46 92 22 96 L32 110 C52 108 72 116 86 130 Z" fill="#aab4c8" opacity="0.5"/>' + bars(['M70 104 l-8 12', 'M52 96 l-8 14', 'M34 96 l-6 10']) }));
    G('tailF', () => S('M96 174 L88 210 L102 198 L110 216 L118 198 L132 210 L124 174 Z', T.white, { sh: 4, inner: bars(['M100 196 l20 0']) }));
    // les serres sortent de sous le ventre, ouvertes
    G('claws', () => raw('<g fill="#3a3a44" stroke="#1c1020" stroke-width="1.4" stroke-linejoin="round"><path d="M88 176 L78 198 L90 190 L92 206 L100 190 L110 198 L104 176 Z"/><path d="M114 176 L112 198 L122 190 L128 206 L132 190 L144 196 L132 176 Z"/></g>'));
    G('body', () => {
      S('M96 82 L90 66 L104 76 Z', T.white, { sh: 2 }); S('M124 82 L130 66 L116 76 Z', T.white, { sh: 2 });
      S('M80 126 C78 96 92 78 110 78 C128 78 142 96 140 126 C140 160 128 188 110 188 C92 188 80 160 80 126 Z', T.white, { sh: 10, hl: 7,
        inner: '<path d="M84 110 C84 92 98 86 110 100 C122 86 136 92 136 110 C134 126 122 134 110 128 C98 134 86 126 84 110 Z" fill="#e2e8f4"/>' + bars(['M92 146 l10 4', 'M110 150 l10 -2', 'M96 162 l10 4', 'M114 164 l10 -3', 'M104 176 l8 2']) });
      raw('<path d="M105 116 L115 116 L110 134 Z" fill="#3a3a44" stroke="#1c1020" stroke-width="1.4" stroke-linejoin="round"/>');
      eye(96, 108, 11.5, 10.5, { iris: '#ffd23a', pupilK: 0.5, lid: 0.42, tilt: 1 }); eye(125, 108, 10.5, 10.5, { iris: '#ffd23a', pupilK: 0.5, lid: 0.42, tilt: -1 });
      raw('<path d="M84 96 L106 106 M136 96 L114 106" stroke="#5a6478" stroke-width="5" stroke-linecap="round"/>');
    });
  });

// 4 · élite — Ours des cavernes : dressé de toute sa hauteur, la gueule ouverte
Mo('glaces', 4, 'Ours des cavernes', { scale: 1.22, atk: 'smash', wind: -50, hit: 40, colors: { fur: '#7a5238', dark: '#573824', pale: '#c8a078' }, swing: ['armN'], far: ['armF'], grp: { farLeg: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [84, 118], far: [136, 122], head: [120, 100], torso: [106, 200] } },
  ({ S, raw, T, G, L, fringe, neck, tuft, brow, under, eye, teeth, ell }) => {
    const claws = (x, y, a) => `<g transform="translate(${x} ${y}) rotate(${a})" fill="${IVORY}" stroke="#3a2416" stroke-width="1.2" stroke-linejoin="round"><path d="M-11 2 L-9 -15 L-4 2 Z M-4 2 L0 -18 L4 2 Z M4 2 L9 -15 L12 2 Z"/></g>`;
    G('armF', () => { L([[[[134, 126], [166, 150], [186, 168]], 27, 23]], 'dark', { far: true }); raw(claws(195, 178, 125)); });
    G('farLeg', () => { L([[[[128, 190], [136, 212], [134, 220]], 30, 26]], 'dark', { far: true }); S(ell(140, 222, 19, 7), T.dark, { sh: 3, far: true }); });
    G('legs', () => { L([[[[84, 192], [78, 214], [80, 220]], 32, 28]], 'fur'); S(ell(84, 222, 21, 7), T.fur, { sh: 3 }); raw(`<g fill="${IVORY}" stroke="#3a2416" stroke-width="1"><path d="M90 222 l8 5 l-2 -8 Z M98 220 l8 4 l-3 -8 Z"/></g>`); });
    G('armN', () => { L([[[[84, 122], [50, 100], [58, 58]], 30, 25]], 'fur'); tuft(58, 104, 250, 12, 22, 'fur'); raw(claws(58, 48, -8)); });
    G('body', () => {
      // bosse des épaules, puis le cou monte vers la tête
      S('M62 152 C56 114 74 90 100 86 C128 82 154 104 150 148 C149 172 144 190 136 200' + fringe(136, 74, 202, 5, 11) + ' C66 190 63 172 62 152 Z', T.fur, { sh: 12, hl: 8,
        inner: under('M84 132 C98 122 122 122 134 134 C134 172 124 198 108 200 C92 198 82 170 84 132 Z', '#c8a078', 0.55) + `<path d="M70 106 C86 90 124 86 142 100" stroke="${ICE}" stroke-width="8" fill="none" opacity="0.6" stroke-linecap="round" filter="url(#g2)"/>` });
      neck([108, 100], [112, 88], [122, 82], 62, 54, 'fur');
    });
    G('head', () => {
      S('M96 68 C88 58 94 46 106 48 C114 50 116 60 112 68 Z', T.fur, { sh: 3, inner: '<circle cx="104" cy="58" r="5" fill="#573824"/>' }); S('M130 60 C130 48 140 44 148 50 C152 56 148 64 142 66 Z', T.dark, { sh: 3 });
      tuft(98, 112, 215, 13, 22, 'fur');
      raw(`<path d="M182 100 L136 107 L170 125 C156 118 156 108 182 100 Z" fill="${MAW}"/><path d="M142 110 C150 108 158 111 162 116 C156 119 148 119 142 115 Z" fill="#c8586a"/>`);
      S('M92 98 C88 72 104 54 126 54 C142 54 154 64 158 80 C168 82 178 90 181 99 L142 106 L174 126 C166 136 148 138 132 132 C110 128 96 116 92 98 Z', T.fur, { sh: 9, hl: 6,
        inner: under('M152 84 C164 84 176 90 182 100 L182 106 L148 104 Z', '#c8a078', 0.9) + '<path d="M172 88 C177 86 183 90 182 96 C177 98 172 94 172 88 Z" fill="#2a1612"/>' });
      teeth([177, 100], [146, 105.5], 4, 9, 1); teeth([170, 124], [146, 109], 3, -8, 1);
      eye(136, 82, 9, 8, { iris: '#bfe9ff', pupilK: 0.5, lid: 0.46, tilt: 1 }); brow(136, 71, 24, 1, '#3a2416', 5.5);
    });
  });

// 5 · boss — Mammouth : épaules en dôme, toison jusqu'au sol, trompe dressée entre deux défenses immenses
Mo('glaces', 5, 'Mammouth', { scale: 1.38, atk: 'smash', wind: -36, hit: 34, colors: { fur: '#6e4a32', dark: '#4a3020', ivory: IVORY, pale: '#9a7450' }, swing: ['trunk'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso', tuskF: 'head', tusk: 'head' }, piv: { swing: [170, 122], head: [138, 116], back: [26, 150], torso: [84, 190] } },
  ({ S, raw, T, G, L, beast, fringe, neck, tuft, brow, stripes, eye, limb }) => {
    const legs = beast({ front: 104, hind: 48, top: 184, w: 26, t: 'fur', dark: 'dark', hoof: true, hoofT: '#3a2a22' });
    G('tail', () => { L([[[[28, 150], [14, 166], [18, 186]], 7, 5]], 'dark'); tuft(18, 188, 180, 14, 12, 'dark'); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      // le profil du mammouth : croupe basse, épaules très hautes
      S('M22 168 C18 138 34 122 54 116 C72 96 104 80 128 92 C142 100 148 124 146 152 C144 176 138 190 130 200' + fringe(130, 32, 200, 9, 14) + ' C24 192 22 180 22 168 Z', T.fur, { sh: 13, hl: 8,
        inner: `<path d="M70 96 C92 80 120 82 134 96 C118 104 88 106 70 96 Z" fill="${ICE}" opacity="0.65" filter="url(#g2)"/>` + stripes(['M38 150 q5 16 0 34', 'M58 148 q5 18 0 36', 'M80 148 q5 18 0 36', 'M102 148 q5 18 0 36', 'M124 146 q4 16 0 32'], '#4a3020', 3.6, 0.5) });
    });
    // la trompe pend du visage puis se relève ; elle part de sous la tête, comme les défenses
    G('trunk', () => S(limb([[172, 118], [188, 206], [218, 148]], 27, 11, 20), T.fur, { sh: 5, inner: stripes(['M166 146 q12 5 22 0', 'M170 164 q11 5 20 0', 'M180 182 q9 4 16 -2', 'M204 176 q6 -2 8 -8'], '#4a3020', 2.2, 0.5) }));
    G('tuskF', () => S(limb([[160, 144], [178, 204], [220, 186]], 12, 2.5, 18), T.ivory, { sh: 3, far: true }));
    G('tusk', () => S(limb([[140, 142], [148, 212], [200, 198]], 15, 3, 18), T.ivory, { sh: 4, hl: 3 }));
    G('head', () => {
      S('M104 124 C96 84 116 52 144 52 C168 52 186 72 186 98 C186 122 176 140 160 148 C150 152 138 154 128 150 C114 146 105 136 104 124 Z', T.fur, { sh: 11, hl: 7,
        inner: '<path d="M110 100 C102 120 108 140 124 148 C132 130 130 110 120 96 Z" fill="#4a3020" opacity="0.7"/>' });
      // la toison du crâne : une frange qui retombe sur le front, pas une couronne
      S('M112 76 C112 48 132 36 150 40 C168 44 180 58 180 74 L172 66 L166 80 L156 64 L150 80 L140 64 L132 80 L124 68 L118 84 Z', T.dark, { sh: 5 });
      tuft(126, 152, 185, 14, 24, 'dark', { n: 3 });
      eye(158, 100, 9, 8.5, { iris: '#bfe9ff', pupilK: 0.5, lid: 0.46, tilt: 1 }); brow(158, 89, 24, 1, '#2e1c12', 5.5);
    });
  });
