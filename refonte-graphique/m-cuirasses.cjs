// LES CUIRASSÉS (terre) — les bêtes à carapace : plaques, écailles, cornes, pierre et poussière.
// Gueule ouverte découpée dans la silhouette, membres attachés sous le corps (voir LISEZMOI, « Les monstres »).
const { Mo, metal } = require('./mon6.cjs');
const IVORY = '#f0e4c8', MAW = '#2a1016', GEM = '#8fe08a';
const bands = (list, c = '#5a4630') => `<g stroke="${c}" stroke-width="2.6" fill="none" opacity="0.65" stroke-linecap="round">${list.map((d) => `<path d="${d}"/>`).join('')}</g>`;

// 0 · rapide — Tatou : il se met en boule et roule sur l'ennemi
Mo('cuirasses', 0, 'Tatou', { scale: 0.92, atk: 'slash', wind: -12, hit: 18, colors: { shell: '#b89a70', skin: '#d8b8a0', dark: '#8a6a4a' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', shell: 'torso' }, piv: { swing: [126, 180], back: [44, 190], torso: [90, 200] } },
  ({ S, raw, T, G, L, beast, eye }) => {
    const legs = beast({ front: 118, hind: 62, top: 200, w: 13, t: 'skin', dark: 'dark', claws: true, gap: 10 });
    G('tail', () => L([[[[46, 192], [20, 200], [8, 222]], 13, 3]], 'shell', { inner: bands(['M36 194 l-2 10', 'M26 200 l-2 10']) }));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    // la tête sort de sous le bord de la carapace
    G('head', () => {
      S('M124 160 C118 136 126 120 136 114 C142 126 144 144 140 160 Z', T.skin, { sh: 3 }); S('M142 160 C142 138 152 124 162 120 C166 134 162 150 154 162 Z', T.dark, { sh: 3 });
      S('M118 184 C118 166 134 158 152 162 C170 166 190 180 198 192 C196 200 186 202 176 200 C158 204 136 204 124 196 C120 192 118 188 118 184 Z', T.skin, { sh: 7, hl: 5,
        inner: '<path d="M132 162 C144 158 160 164 170 174 C160 176 142 174 132 162 Z" fill="#b89a70"/><ellipse cx="193" cy="191" rx="3" ry="2.4" fill="#3a2416"/><path d="M190 198 C182 200 174 200 166 198" stroke="#3a2416" stroke-width="2.2" fill="none" stroke-linecap="round"/>' });
      eye(156, 182, 7.5, 7, { iris: '#ffb020', pupilK: 0.5, lid: 0.5, tilt: 1 });
    });
    G('shell', () => S('M38 200 C34 160 60 132 92 132 C122 132 144 156 142 196 C140 204 40 206 38 200 Z', T.shell, { sh: 10, hl: 7,
      inner: bands(['M62 142 C54 160 52 182 56 202', 'M78 134 C72 156 72 182 76 204', 'M96 132 C94 156 94 182 98 204', 'M114 138 C116 158 118 182 118 204', 'M130 150 C134 166 136 184 134 202']) + '<g fill="#8a6a4a" opacity="0.6"><circle cx="46" cy="180" r="3"/><circle cx="48" cy="192" r="3"/><circle cx="136" cy="178" r="3"/></g>' }));
  });

// 1 · costaud — Scarabée-rhinocéros : une carapace luisante, une corne fourchue
Mo('cuirasses', 1, 'Scarabée-rhinocéros', { scale: 1.1, atk: 'smash', wind: -24, hit: 30, colors: { shell: metal('#6a3e24'), dark: '#2e1c14', leg: '#3a261c' }, swing: ['head'], grp: { farLegs: 'legs', legs: 'legs', shell: 'torso' }, piv: { swing: [132, 170], torso: [92, 200] } },
  ({ S, raw, T, G, L, eye, limb }) => {
    G('farLegs', () => L([[[[70, 180], [48, 196], [40, 226]], 8, 5], [[[100, 184], [106, 204], [98, 226]], 8, 5], [[[132, 182], [150, 204], [158, 226]], 8, 5]], 'dark', { far: true }));
    G('legs', () => L([[[[60, 186], [34, 200], [24, 226]], 10, 6], [[[90, 190], [84, 208], [74, 226]], 10, 6], [[[122, 190], [130, 208], [140, 226]], 10, 6]], 'leg'));
    // la tête et la corne partent de sous le pronotum
    G('head', () => {
      S(limb([[156, 160], [196, 150], [190, 96]], 20, 9, 18), T.shell, { sh: 5, hl: 4 }); S('M184 104 L170 82 L190 92 L196 70 L206 100 Z', T.shell, { sh: 4, hl: 3 });
      S('M128 172 C128 154 142 146 158 150 C172 154 180 166 178 180 C176 190 164 196 150 194 C136 192 128 184 128 172 Z', T.dark, { sh: 6, hl: 4, inner: '<path d="M168 184 l8 8 M158 190 l4 10" stroke="#120a0e" stroke-width="3" stroke-linecap="round"/>' });
      eye(160, 168, 7.5, 7, { iris: '#ffb020', pupilK: 0.5, lid: 0.46, tilt: 1 });
    });
    G('shell', () => { S('M34 188 C30 150 54 124 88 122 C112 122 128 136 132 160 C134 176 130 188 124 196 C100 202 60 202 34 188 Z', T.shell, { sh: 11, hl: 8, inner: '<path d="M84 122 C80 150 80 178 86 200" stroke="#2e1c14" stroke-width="3" fill="none"/><path d="M48 150 C56 136 72 130 84 130" stroke="#f4d8a0" stroke-width="6" fill="none" opacity="0.5" stroke-linecap="round"/>' }); S('M112 132 C132 128 148 140 150 158 C150 172 142 182 130 186 C122 172 116 152 112 132 Z', T.shell, { sh: 6, hl: 5 }); });
  });

// 2 · tireur — Pangolin : debout sur ses pattes arrière, il lance ses écailles comme des lames
Mo('cuirasses', 2, 'Pangolin lanceur', { atk: 'shoot', colors: { scale: '#a87a4a', skin: '#e0c0a0', dark: '#7a5632' }, swing: ['arm'], grp: { tail: 'back', farLeg: 'legs', leg: 'legs', body: 'torso' }, piv: { swing: [100, 140], head: [118, 124], back: [80, 190], torso: [100, 206] } },
  ({ S, raw, T, G, L, eye, ell }) => {
    const sc = (rows) => `<g fill="none" stroke="#5a3e22" stroke-width="2.2" opacity="0.7">${rows.map(([x, y, n]) => Array.from({ length: n }, (_, i) => `<path d="M${x + i * 15} ${y} q7.500 10 15 0"/>`).join('')).join('')}</g>`;
    G('tail', () => L([[[[84, 190], [30, 212], [10, 176]], 34, 8]], 'scale', { N: 18, inner: sc([[20, 190, 4], [28, 202, 4]]) }));
    G('farLeg', () => { L([[[[110, 196], [120, 212], [116, 222]], 14, 12]], 'dark', { far: true }); S(ell(122, 224, 12, 5), T.dark, { sh: 2, far: true }); });
    G('leg', () => { L([[[[90, 198], [84, 212], [88, 222]], 15, 13]], 'scale'); S(ell(92, 224, 13, 5), T.scale, { sh: 2 }); });
    // le bras levé tient une écaille, prêt à la lancer ; il part de sous l'épaule
    G('arm', () => { S('M52 82 L70 76 L72 102 L56 100 Z', T.scale, { sh: 3, hl: 3 }); L([[[[100, 142], [74, 130], [64, 104]], 12, 10]], 'skin'); });
    G('body', () => S('M70 170 C66 140 82 122 102 122 C122 122 136 138 134 166 C132 192 120 208 102 208 C84 208 72 194 70 170 Z', T.scale, { sh: 10, hl: 6,
      inner: '<path d="M108 136 C124 140 132 156 130 172 C128 190 118 202 108 204 C104 184 104 158 108 136 Z" fill="#e0c0a0"/>' + sc([[68, 140, 3], [62, 154, 3], [62, 168, 3], [66, 182, 3], [72, 196, 2]]) }));
    G('head', () => {
      S('M100 128 C96 108 108 94 126 94 C142 94 156 102 170 114 C178 120 180 128 174 132 C160 136 144 140 128 140 C112 140 102 136 100 128 Z', T.skin, { sh: 7, hl: 5,
        inner: '<path d="M98 124 C96 106 108 94 126 94 C136 94 144 98 150 104 C136 104 118 112 108 128 Z" fill="#a87a4a"/><ellipse cx="174" cy="124" rx="2.6" ry="2.2" fill="#3a2416"/>' });
      eye(140, 116, 7.5, 7, { iris: '#ffb020', pupilK: 0.5, lid: 0.5, tilt: 1 });
    });
  });

// 3 · sorts — Escargot de pierre : sa coquille est un rocher couvert de mousse et de cristaux
Mo('cuirasses', 3, 'Escargot de pierre', { atk: 'cast', heal: true, fx: GEM, colors: { rock: '#8a8478', skin: '#c8b890', moss: '#6aa84a', gem: '#8fe08a' }, grp: { foot: 'legs', shell: 'torso' }, piv: { head: [142, 180], torso: [96, 200] }, shine: [[84, 96, 10, GEM]] },
  ({ S, raw, T, G, L, halo, eye }) => {
    halo(84, 96, 16, GEM, 0.8);
    G('foot', () => S('M30 222 C40 206 80 200 130 202 C150 202 162 210 172 222 C150 230 60 230 30 222 Z', T.skin, { sh: 5, hl: 4 }));
    // le cou et les tiges des yeux partent de sous la coquille
    G('head', () => {
      L([[[[152, 150], [150, 128], [158, 112]], 6, 5], [[[166, 152], [174, 134], [186, 124]], 6, 5]], 'skin');
      S('M128 208 C126 178 138 152 156 148 C172 146 182 158 180 174 C178 190 170 204 172 220 L130 220 Z', T.skin, { sh: 7, hl: 5, inner: '<path d="M160 190 q8 4 14 -2" stroke="#5a4a30" stroke-width="2.4" fill="none" stroke-linecap="round"/>' });
      eye(158, 108, 8, 8, { iris: '#1c1020', pupil: 'none', irisK: 0.6, lid: 0.4, tilt: 1 }); eye(188, 120, 7, 7, { iris: '#1c1020', pupil: 'none', irisK: 0.6, lid: 0.4, tilt: -1 });
    });
    G('shell', () => {
      S('M70 110 L78 78 L90 104 Z M92 104 L102 70 L112 104 Z', T.gem, { sh: 3, hl: 4 });
      S('M34 180 C28 136 56 100 96 100 C132 100 156 130 152 172 C150 196 136 210 112 212 C80 216 40 210 34 180 Z', T.rock, { sh: 12, hl: 8,
        inner: '<path d="M96 196 C66 196 54 172 60 150 C66 130 90 122 108 132 C124 142 126 164 114 174 C104 182 88 178 86 166 C84 158 92 152 100 156" stroke="#5a564c" stroke-width="5" fill="none" stroke-linecap="round"/><g fill="#6aa84a" opacity="0.85"><ellipse cx="60" cy="126" rx="14" ry="7"/><ellipse cx="124" cy="116" rx="12" ry="6"/><ellipse cx="44" cy="170" rx="8" ry="5"/></g>' });
    });
  });

// 4 · élite — Tricératops : une collerette d'os, trois cornes, il charge tête baissée
Mo('cuirasses', 4, 'Tricératops', { scale: 1.2, atk: 'smash', wind: -18, hit: 26, colors: { skin: '#9a8a5a', dark: '#6e6240', frill: '#c8a060', horn: IVORY }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [112, 166], back: [36, 170], torso: [84, 196] } },
  ({ S, raw, T, G, L, beast, eye, limb }) => {
    const legs = beast({ front: 104, hind: 52, top: 190, w: 22, t: 'skin', dark: 'dark', claws: true });
    G('tail', () => L([[[[40, 172], [14, 184], [4, 206]], 24, 5]], 'skin'));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M28 176 C26 142 54 126 88 128 C114 130 132 144 132 170 C132 192 112 204 82 204 C52 204 30 198 28 176 Z', T.skin, { sh: 11, hl: 7, inner: '<path d="M36 196 C64 208 108 206 132 188 L134 214 L34 214 Z" fill="#d8cc9a" opacity="0.7" filter="url(#g3)"/>' + bands(['M56 140 l4 8', 'M74 134 l4 8', 'M92 134 l2 8', 'M46 158 l6 6'], '#6e6240') }));
    G('head', () => {
      // la collerette, derrière la tête
      S('M110 176 C92 160 86 126 100 104 L96 88 L110 96 L116 78 L128 92 L140 78 L146 96 C150 110 148 130 140 150 Z', T.frill, { sh: 7, hl: 5, inner: '<g fill="#8a6a34" opacity="0.7"><circle cx="110" cy="124" r="6"/><circle cx="126" cy="108" r="5"/><circle cx="118" cy="146" r="5"/></g>' });
      S(limb([[150, 128], [176, 108], [198, 74]], 12, 2, 16), T.horn, { sh: 3, far: true }); S(limb([[134, 132], [150, 100], [176, 68]], 14, 2, 16), T.horn, { sh: 4, hl: 3 });
      S('M112 162 C110 140 126 128 148 130 C166 132 180 142 190 156 C198 164 200 174 194 180 C188 186 180 184 174 188 C158 196 138 196 124 188 C116 182 112 172 112 162 Z', T.skin, { sh: 10, hl: 6,
        inner: '<path d="M192 178 C184 182 176 182 168 180" stroke="#3a3020" stroke-width="2.4" fill="none" stroke-linecap="round"/><ellipse cx="186" cy="164" rx="2.4" ry="2" fill="#3a3020"/>' });
      S('M184 160 L196 138 L198 164 Z', T.horn, { sh: 3 });
      eye(148, 154, 8.5, 7.5, { iris: '#ffb020', pupil: 'slit', lid: 0.46, tilt: 1 });
    });
  });

// 5 · boss — Ankylosaure : un char d'assaut vivant, une massue au bout de la queue
Mo('cuirasses', 5, 'Ankylosaure', { scale: 1.36, atk: 'smash', wind: -50, hit: 60, colors: { skin: '#7a6a4a', dark: '#544830', plate: '#a89868', horn: IVORY }, swing: ['tail'], grp: { farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [40, 172], head: [128, 180], torso: [86, 196] } },
  ({ S, raw, T, G, L, beast, eye, limb, ell }) => {
    const legs = beast({ front: 112, hind: 52, top: 196, w: 20, t: 'skin', dark: 'dark', claws: true, gap: 12 });
    // la queue se dresse au-dessus du dos, massue en l'air
    G('tail', () => { S(limb([[42, 174], [-6, 150], [26, 96]], 22, 10, 18), T.skin, { sh: 5 }); S(ell(30, 86, 22, 17), T.plate, { sh: 6, hl: 4, inner: '<path d="M16 82 C24 74 38 74 46 82" stroke="#f0e4c8" stroke-width="4" fill="none" opacity="0.6" stroke-linecap="round"/>' }); S('M12 78 L0 66 L18 72 Z M42 72 L52 58 L50 78 Z', T.horn, { sh: 2 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M24 190 C22 166 40 152 54 150 L58 132 L72 146 L82 124 L94 144 L106 126 L114 148 L128 136 L130 156 C142 162 146 176 144 190 C140 206 112 210 84 210 C54 210 26 206 24 190 Z', T.skin, { sh: 11, hl: 7,
      inner: '<g fill="#a89868">' + [[50, 168], [70, 160], [92, 158], [114, 162], [60, 184], [82, 180], [104, 180], [126, 180]].map(([x, y]) => `<ellipse cx="${x}" cy="${y}" rx="9" ry="6"/>`).join('') + '</g><path d="M30 200 C60 212 116 212 144 196 L146 220 L28 220 Z" fill="#d8cc9a" opacity="0.6" filter="url(#g3)"/>' }));
    G('head', () => {
      S('M126 162 L118 142 L138 152 Z', T.horn, { sh: 3 }); S('M150 158 L158 140 L166 162 Z', T.horn, { sh: 3, far: true });
      S('M118 184 C116 164 132 154 152 156 C170 158 188 168 196 180 C200 188 198 196 190 198 C174 204 148 206 132 200 C122 196 118 190 118 184 Z', T.skin, { sh: 9, hl: 6,
        inner: '<path d="M124 164 C140 156 162 158 176 168 C160 172 138 172 124 164 Z" fill="#a89868"/><path d="M194 190 C184 194 174 194 164 192" stroke="#3a3020" stroke-width="2.4" fill="none" stroke-linecap="round"/><ellipse cx="190" cy="180" rx="2.4" ry="2" fill="#3a3020"/>' });
      eye(156, 178, 8, 7, { iris: '#ffb020', pupil: 'slit', lid: 0.48, tilt: 1 });
    });
  });
