// LA HORDE DES GLACES (eau) — les bêtes de l'âge de glace : fourrures épaisses, givre, ivoire.
// Bêtes trapues (grosse tête, pattes courtes), regard dur. Gueule ouverte découpée dans la silhouette, membres sous le corps.
const { Mo } = require('./mon6.cjs');
const ICE = '#dff4ff', IVORY = '#f6ecd4', MAW = '#2a1016';

// 0 · rapide — Tigre à dents de sabre : corps long, épaules lourdes, deux sabres sous la lèvre
Mo('glaces', 0, 'Tigre à dents de sabre', { scale: 1.04, atk: 'slash', wind: -14, hit: 20, colors: { fur: '#d09a58', dark: '#9a6a34' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [122, 160], back: [36, 160], torso: [88, 190] } },
  ({ S, raw, T, G, L, beast, eye }) => {
    const legs = beast({ front: 116, hind: 54, top: 184, w: 19, t: 'fur', dark: 'dark', claws: true });
    G('tail', () => L([[[[38, 162], [8, 164], [12, 128]], 12, 8]], 'fur', { inner: '<g stroke="#7a4a22" stroke-width="5" stroke-linecap="round" opacity="0.7"><path d="M14 150 l10 -2 M12 138 l10 2"/></g>' }));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M30 172 C28 146 56 132 90 134 C120 136 142 148 144 170 C146 192 120 206 88 206 C54 206 32 196 30 172 Z', T.fur, { sh: 10, hl: 6,
      inner: '<path d="M38 196 C70 212 118 208 146 186 L148 214 L36 214 Z" fill="#f6e8cc" opacity="0.8" filter="url(#g3)"/><g stroke="#7a4a22" stroke-width="6" stroke-linecap="round" opacity="0.75"><path d="M50 142 L54 164 M68 136 L70 160 M88 134 L88 158 M106 138 L104 158"/></g>' }));
    G('head', () => {
      S('M126 126 L116 104 L138 114 Z', T.fur, { sh: 3 }); S('M148 116 L154 98 L164 118 Z', T.dark, { sh: 3 });
      // les sabres sortent de sous la lèvre du haut, devant le menton : la gueule reste fermée
      raw(`<path d="M182 160 L182 196 L170 162 Z M166 164 L164 190 L155 165 Z" fill="${IVORY}" stroke="#3a2416" stroke-width="1.6" stroke-linejoin="round"/>`);
      S('M114 150 C112 128 130 114 150 114 C168 114 182 124 188 138 C192 148 190 158 184 164 C176 170 164 168 156 172 C140 180 122 176 116 162 C115 158 114 154 114 150 Z', T.fur, { sh: 9, hl: 6,
        inner: '<path d="M158 148 C170 144 184 148 192 156 L188 170 L154 174 Z" fill="#f6e8cc" opacity="0.85" filter="url(#g2)"/><path d="M180 138 C185 136 191 140 190 146 C185 148 180 144 180 138 Z" fill="#3a1c1c"/><path d="M188 160 C178 164 166 166 154 164" stroke="#3a1c1c" stroke-width="2.4" fill="none" stroke-linecap="round"/><g stroke="#7a4a22" stroke-width="5" stroke-linecap="round" opacity="0.7"><path d="M118 142 L130 146 M118 154 L130 154 M138 118 L140 128"/></g>' });
      raw('<path d="M146 124 L172 132" stroke="#5a3214" stroke-width="5" stroke-linecap="round"/>');
      eye(158, 138, 9, 7, { iris: '#ffb020', pupil: 'slit', lid: 0.5, tilt: 1 });
    });
  });

// 1 · costaud — Rhinocéros laineux : tête basse, il charge
Mo('glaces', 1, 'Rhinocéros laineux', { scale: 1.12, atk: 'smash', wind: -18, hit: 24, colors: { fur: '#8a5c3c', dark: '#5e3c26', horn: IVORY }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [116, 160], back: [36, 150], torso: [88, 190] } },
  ({ S, raw, T, G, L, beast, fringe, eye }) => {
    const legs = beast({ front: 108, hind: 54, top: 186, w: 24, t: 'fur', dark: 'dark', hoof: true });
    G('tail', () => L([[[[38, 150], [22, 160], [26, 182]], 8, 5]], 'dark'));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M30 166 C28 122 62 102 98 104 C124 106 142 124 142 156 C142 176 136 190 130 198' + fringe(130, 40, 198, 7, 12) + ' C32 190 30 178 30 166 Z', T.fur, { sh: 11, hl: 7,
      inner: `<path d="M52 110 C72 100 104 100 124 112 C112 120 70 120 52 110 Z" fill="${ICE}" opacity="0.7" filter="url(#g2)"/><g stroke="#5e3c26" stroke-width="3.4" stroke-linecap="round" opacity="0.5" fill="none"><path d="M48 150 q4 14 0 28 M68 156 q4 14 0 28 M90 158 q4 14 0 28 M112 154 q4 14 0 26"/></g>` }));
    G('head', () => {
      S('M124 126 L116 102 L140 114 Z', T.dark, { sh: 3 });
      S('M110 150 C108 126 128 114 150 118 C170 122 188 138 194 158 C198 172 190 184 176 186 C160 188 150 198 136 194 L120 200 L124 184 C114 176 110 162 110 150 Z', T.fur, { sh: 10, hl: 6,
        inner: '<path d="M174 178 C182 174 190 174 194 178" stroke="#3a2416" stroke-width="2.4" fill="none" stroke-linecap="round"/><ellipse cx="190" cy="158" rx="2.6" ry="2" fill="#3a2416"/><g stroke="#5e3c26" stroke-width="3" stroke-linecap="round" opacity="0.5"><path d="M118 152 l8 4 M122 166 l8 2"/></g>' });
      S('M176 146 C186 130 200 106 194 74 C184 96 170 114 162 132 Z', T.horn, { sh: 4, hl: 3 }); S('M154 124 C160 114 164 104 162 92 C154 102 150 112 146 122 Z', T.horn, { sh: 3 });
      eye(150, 144, 8, 7.5, { iris: '#bfe9ff', pupilK: 0.5, lid: 0.44, tilt: 1 });
    });
  });

// 2 · tireur — Narval : il lance des éclats de glace du bout de sa défense
Mo('glaces', 2, 'Narval', { atk: 'cast', fx: ICE, colors: { skin: '#7f9cbc', dark: '#52708e', tusk: IVORY }, swing: ['tusk'], grp: { tail: 'back', body: 'torso' }, piv: { swing: [158, 140], back: [46, 172], torso: [106, 150] }, shine: [[214, 110, 8, ICE]], shineGrp: 'swing' },
  ({ S, raw, T, G, eye, blade }) => {
    G('tail', () => S('M54 166 L14 138 C24 160 22 178 8 198 L56 184 Z', T.dark, { sh: 5 }));
    G('tusk', () => { const b = blade([150, 142], [216, 109], 9, 0.05); S(b.d, T.tusk, { sh: 2, hl: 2, inner: '<g stroke="#b8a070" stroke-width="1.8" opacity="0.7"><path d="M164 132 l4 9 M175 127 l4 8 M186 122 l3 7 M197 117 l2 6"/></g>' }); });
    G('body', () => {
      S('M96 124 L104 100 L122 120 Z', T.dark, { sh: 3 });
      S('M38 172 C40 140 78 116 122 114 C150 113 168 126 170 146 C172 162 158 176 132 182 C104 190 66 194 38 172 Z', T.skin, { sh: 10, hl: 7,
        inner: '<path d="M44 180 C80 196 130 192 168 160 L174 202 L40 202 Z" fill="#eef4ff" opacity="0.85" filter="url(#g3)"/><g fill="#52708e" opacity="0.55"><circle cx="82" cy="136" r="5.5"/><circle cx="104" cy="128" r="4"/><circle cx="68" cy="152" r="4"/><circle cx="122" cy="138" r="3"/><circle cx="94" cy="150" r="2.6"/></g><path d="M168 152 C160 152 152 156 146 162" stroke="#2a3a52" stroke-width="2.4" fill="none" stroke-linecap="round"/><path d="M130 122 l10 6 M124 130 l8 4" stroke="#eef4ff" stroke-width="2.4" stroke-linecap="round" opacity="0.7"/>' });
      S('M102 174 C92 184 88 198 92 208 C106 202 116 188 118 176 Z', T.dark, { sh: 3 });
      eye(148, 136, 9, 8, { iris: '#ffe14a', pupilK: 0.5, lid: 0.42, tilt: 1 });
    });
  });

// 3 · sorts — Harfang : la chouette des neiges appelle le blizzard
Mo('glaces', 3, 'Harfang', { atk: 'cast', fx: ICE, colors: { white: '#f4f8ff', bar: '#7a869c' }, swing: ['wingN'], far: ['wingF'], grp: { tailF: 'back', claws: 'torso', body: 'torso' }, piv: { swing: [94, 122], far: [128, 122], back: [110, 180], torso: [110, 140] } },
  ({ S, raw, T, G, eye }) => {
    const bars = '<g stroke="#7a869c" stroke-width="3.4" stroke-linecap="round" opacity="0.6">';
    G('wingF', () => S('M124 118 C146 84 182 78 208 96 L196 106 L204 118 L190 122 L194 136 L178 136 L178 150 L162 146 C146 146 132 138 124 130 Z', T.white, { sh: 6, far: true, inner: bars + '<path d="M150 104 l8 12 M168 98 l8 14 M186 100 l6 10"/></g>' }));
    G('wingN', () => S('M98 118 C74 82 36 76 8 96 L22 106 L12 120 L28 122 L24 138 L42 136 L42 152 L60 146 C76 146 90 138 98 130 Z', T.white, { sh: 7, inner: bars + '<path d="M70 104 l-8 12 M52 98 l-8 14 M34 100 l-6 10"/></g>' }));
    G('tailF', () => S('M96 174 L90 208 L102 196 L110 212 L118 196 L130 208 L124 174 Z', T.white, { sh: 4 }));
    G('claws', () => raw('<g fill="#3a3a44" stroke="#1c1020" stroke-width="1.4" stroke-linejoin="round"><path d="M92 178 l-6 16 l8 -6 l2 12 l5 -12 l8 6 l-5 -16 Z"/><path d="M112 178 l-5 16 l8 -6 l2 12 l5 -12 l8 6 l-6 -16 Z"/></g>'));
    G('body', () => {
      S('M80 126 C78 96 92 78 110 78 C128 78 142 96 140 126 C140 160 128 188 110 188 C92 188 80 160 80 126 Z', T.white, { sh: 10, hl: 7,
        inner: bars + '<path d="M92 146 l10 4 M110 150 l10 -2 M96 162 l10 4 M114 164 l10 -3 M104 176 l8 2"/></g><path d="M84 96 L110 108 L136 96" stroke="#7a869c" stroke-width="5" fill="none" stroke-linejoin="round" opacity="0.5"/>' });
      raw('<path d="M106 118 L116 118 L111 134 Z" fill="#3a3a44" stroke="#1c1020" stroke-width="1.4" stroke-linejoin="round"/>');
      eye(96, 108, 11.5, 10.5, { iris: '#ffd23a', pupilK: 0.5, lid: 0.4, tilt: 1 }); eye(125, 108, 10.5, 10.5, { iris: '#ffd23a', pupilK: 0.5, lid: 0.4, tilt: -1 });
    });
  });

// 4 · élite — Ours des cavernes : dressé, il rugit
Mo('glaces', 4, 'Ours des cavernes', { scale: 1.2, atk: 'smash', wind: -50, hit: 40, colors: { fur: '#7a5238', dark: '#573824' }, swing: ['armN'], far: ['armF'], grp: { farLeg: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [84, 118], far: [136, 118], head: [124, 96], torso: [106, 200] } },
  ({ S, raw, T, G, L, fringe, eye, teeth, ell }) => {
    const claws = (x, y, a) => `<g transform="translate(${x} ${y}) rotate(${a})" fill="${IVORY}" stroke="#3a2416" stroke-width="1.2"><path d="M-10 2 L-8 -14 L-3 2 Z M-3 2 L0 -17 L4 2 Z M4 2 L8 -14 L11 2 Z"/></g>`;
    G('armF', () => { L([[[[134, 126], [166, 150], [186, 168]], 26, 22]], 'dark', { far: true }); raw(claws(194, 178, 125)); });
    G('farLeg', () => { L([[[[128, 190], [134, 212], [134, 220]], 28, 26]], 'dark', { far: true }); S(ell(138, 222, 18, 7), T.dark, { sh: 3, far: true }); });
    G('legs', () => { L([[[[84, 192], [80, 214], [80, 220]], 30, 28]], 'fur'); S(ell(84, 222, 20, 7), T.fur, { sh: 3 }); });
    G('armN', () => { L([[[[84, 120], [52, 98], [60, 58]], 28, 24]], 'fur'); raw(claws(60, 48, -8)); });
    G('body', () => S('M64 150 C58 110 80 84 108 84 C136 84 154 110 150 150 C149 172 144 190 136 200' + fringe(136, 76, 202, 5, 10) + ' C68 188 65 170 64 150 Z', T.fur, { sh: 12, hl: 8,
      inner: `<path d="M86 130 C100 122 120 122 132 132 C132 170 122 196 108 198 C94 196 84 168 86 130 Z" fill="#c8a078" opacity="0.5" filter="url(#g3)"/><path d="M72 104 C88 90 124 88 142 100" stroke="${ICE}" stroke-width="7" fill="none" opacity="0.6" stroke-linecap="round" filter="url(#g2)"/>` }));
    G('head', () => {
      S('M96 70 C90 60 96 50 106 52 C112 54 114 62 110 68 Z', T.fur, { sh: 3 }); S('M128 62 C128 50 138 46 146 52 C150 58 146 66 140 68 Z', T.dark, { sh: 3 });
      raw(`<path d="M178 99 L136 107 L167 123 C156 118 156 108 178 99 Z" fill="${MAW}"/>`);
      S('M92 98 C88 74 104 56 124 56 C140 56 152 68 155 82 C165 84 175 90 177 99 L142 106 L170 123 C162 132 146 134 132 130 L112 134 L116 122 C102 118 94 108 92 98 Z', T.fur, { sh: 9, hl: 6,
        inner: '<path d="M150 84 C160 84 172 90 178 100 L178 106 L146 104 Z" fill="#c8a078" opacity="0.8" filter="url(#g2)"/><path d="M170 90 C174 88 180 92 179 97 C174 99 170 96 170 90 Z" fill="#2a1612"/>' });
      teeth([173, 100], [146, 105.5], 3, 9, 1); teeth([167, 121], [146, 109], 3, -8, 1);
      eye(134, 84, 9, 8, { iris: '#bfe9ff', pupilK: 0.5, lid: 0.46, tilt: 1 });
    });
  });

// 5 · boss — Mammouth : la trompe levée, les défenses en avant
Mo('glaces', 5, 'Mammouth', { scale: 1.36, atk: 'smash', wind: -36, hit: 34, colors: { fur: '#6e4a32', dark: '#4a3020', ivory: IVORY }, swing: ['trunk'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso', tuskF: 'head', tusk: 'head' }, piv: { swing: [172, 120], head: [136, 120], back: [30, 140], torso: [86, 190] } },
  ({ S, raw, T, G, L, beast, fringe, eye, limb }) => {
    const legs = beast({ front: 104, hind: 50, top: 184, w: 26, t: 'fur', dark: 'dark', hoof: true, hoofT: '#3a2a22' });
    G('tail', () => L([[[[32, 140], [16, 156], [22, 180]], 8, 5]], 'dark'));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M26 164 C22 112 56 84 96 86 C126 88 142 112 142 150 C142 172 136 188 128 198' + fringe(128, 36, 198, 8, 13) + ' C28 190 26 176 26 164 Z', T.fur, { sh: 12, hl: 8,
      inner: `<path d="M48 96 C70 84 102 86 120 98 C106 106 66 108 48 96 Z" fill="${ICE}" opacity="0.6" filter="url(#g2)"/><g stroke="#4a3020" stroke-width="3.6" stroke-linecap="round" opacity="0.5" fill="none"><path d="M42 148 q4 14 0 30 M62 156 q4 14 0 30 M84 160 q4 14 0 28 M106 158 q4 14 0 28"/></g>` }));
    G('trunk', () => S(limb([[172, 116], [186, 204], [216, 150]], 26, 11, 20), T.fur, { sh: 5, inner: '<g stroke="#4a3020" stroke-width="2.2" opacity="0.5" fill="none"><path d="M168 146 q10 4 20 0 M172 164 q10 4 18 0 M180 180 q8 4 16 -2"/></g>' }));
    G('tuskF', () => S(limb([[160, 144], [176, 200], [216, 188]], 12, 2.5, 18), T.ivory, { sh: 3, far: true }));
    G('tusk', () => S(limb([[140, 142], [150, 206], [196, 196]], 14, 3, 18), T.ivory, { sh: 4, hl: 3 }));
    G('head', () => {
      S('M104 124 C96 84 116 52 144 52 C168 52 186 72 186 98 C186 122 176 140 160 148 C150 152 138 152 128 148 L112 158 L116 142 C108 138 105 132 104 124 Z', T.fur, { sh: 11, hl: 7,
        inner: '<path d="M110 104 C104 122 110 138 124 146 C130 128 128 112 118 100 Z" fill="#4a3020" opacity="0.65"/>' });
      S('M124 58 L118 36 L136 50 L140 30 L152 50 L164 38 L162 60 Z', T.dark, { sh: 4 });
      eye(158, 98, 9, 8.5, { iris: '#bfe9ff', pupilK: 0.5, lid: 0.46, tilt: 1 });
    });
  });
