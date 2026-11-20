// LE BAYOU (eau) — les créatures du marais : écailles vertes, vase, mousse, lueurs.
// Gueule ouverte découpée dans la silhouette, membres attachés sous le corps (voir LISEZMOI, « Les monstres »).
const { Mo } = require('./mon6.cjs');
const WATER = '#6fd0ff', WISP = '#8fffd0', MAW = '#2a1016';

// 0 · rapide — Lézard basilic : il court debout, si vite qu'il marche sur l'eau
Mo('bayou', 0, 'Lézard basilic', { scale: 0.96, atk: 'stab', wind: -10, hit: 14, colors: { skin: '#4fae6a', dark: '#2f7a4a', belly: '#e6e8a0', crest: '#f0a030' }, grp: { tail: 'back', farLeg: 'legs', leg: 'legs', arm: 'torso', body: 'torso' }, piv: { head: [124, 126], back: [82, 172], torso: [104, 190] } },
  ({ S, raw, T, G, L, eye, ell }) => {
    G('tail', () => L([[[[84, 172], [26, 184], [8, 138]], 18, 4]], 'skin', { N: 18 }));
    G('farLeg', () => { L([[[[112, 182], [136, 198], [128, 220]], 14, 10]], 'dark', { far: true }); S('M118 227 C118 218 134 216 146 222 L150 227 Z', T.dark, { sh: 2, far: true }); });
    G('leg', () => { L([[[[94, 184], [66, 198], [82, 220]], 16, 11]], 'skin'); S('M70 227 C70 217 88 215 102 222 L106 227 Z', T.skin, { sh: 2 }); });
    G('arm', () => L([[[[118, 158], [136, 172], [150, 160]], 9, 6]], 'skin'));
    G('body', () => {
      S('M82 150 C70 132 78 112 96 110 C96 124 102 134 110 140 Z', T.crest, { sh: 4 });
      S('M74 172 C70 146 90 130 112 130 C130 130 140 146 138 164 C136 186 116 198 98 196 C84 194 76 184 74 172 Z', T.skin, { sh: 9, hl: 6,
        inner: '<path d="M104 196 C122 196 138 182 140 160 L150 200 Z" fill="#e6e8a0" opacity="0.85" filter="url(#g3)"/><g fill="#2f7a4a" opacity="0.6"><circle cx="90" cy="150" r="4"/><circle cx="100" cy="166" r="3.4"/><circle cx="88" cy="174" r="3"/></g>' });
    });
    G('head', () => {
      S('M116 100 C108 72 128 52 150 60 C142 70 140 82 144 92 Z', T.crest, { sh: 4 });
      S('M110 120 C108 98 126 86 148 88 C168 90 184 102 188 116 C190 124 186 130 180 132 C170 142 154 146 140 144 C122 142 112 134 110 120 Z', T.skin, { sh: 9, hl: 6,
        inner: '<path d="M184 128 C172 132 158 134 146 132" stroke="#1f4a30" stroke-width="2.4" fill="none" stroke-linecap="round"/><path d="M144 144 C160 146 176 140 186 128 L190 150 L140 150 Z" fill="#e6e8a0" opacity="0.8" filter="url(#g2)"/><ellipse cx="182" cy="114" rx="2.2" ry="1.7" fill="#1f4a30"/>' });
      eye(154, 108, 11, 10, { iris: '#ffb020', pupil: 'slit', lid: 0.4, tilt: 1 });
    });
  });

// 1 · costaud — Tortue-alligator : carapace à pointes, bec crochu
Mo('bayou', 1, 'Tortue-alligator', { scale: 1.1, atk: 'smash', wind: -16, hit: 22, colors: { shell: '#5a5238', skin: '#6a7a4a', dark: '#46522e', moss: '#7ab84a' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', shell: 'torso' }, piv: { swing: [134, 178], back: [44, 192], torso: [92, 200] } },
  ({ S, raw, T, G, L, beast, eye }) => {
    const legs = beast({ front: 124, hind: 56, top: 198, w: 20, t: 'skin', dark: 'dark', claws: true, gap: 12 });
    G('tail', () => L([[[[46, 192], [18, 200], [8, 218]], 14, 4]], 'skin'));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    // la tête sort de sous le bord de la carapace
    G('head', () => {
      raw(`<path d="M196 180 L162 184 L185 193 C178 192 178 186 196 180 Z" fill="${MAW}"/>`);
      S('M126 184 C130 162 150 152 170 156 C184 160 194 170 196 179 L164 184 L190 194 C182 204 164 206 148 202 C134 198 126 192 126 184 Z', T.skin, { sh: 8, hl: 5,
        inner: '<path d="M178 162 l8 6 M168 158 l6 5" stroke="#46522e" stroke-width="2.4" stroke-linecap="round" opacity="0.6"/>' });
      raw('<path d="M196 179 L190 190 L184 181 Z" fill="#e8dcb0" stroke="#2a2416" stroke-width="1.4" stroke-linejoin="round"/>');
      eye(166, 170, 8, 7, { iris: '#ffb020', pupil: 'slit', lid: 0.44, tilt: 1 });
    });
    G('shell', () => S('M30 198 C28 164 44 146 58 138 L62 118 L76 132 C84 130 92 128 100 130 L108 108 L120 132 C130 136 138 142 144 150 L160 142 L154 164 C158 174 160 186 158 198 Z', T.shell, { sh: 11, hl: 7,
      inner: '<g stroke="#2e2a1c" stroke-width="2.6" fill="none" opacity="0.6"><path d="M62 140 C56 160 54 180 56 198 M100 132 C98 156 98 178 100 198 M134 144 C136 162 136 182 134 198 M34 176 C70 168 120 168 156 176"/></g><g fill="#7ab84a" opacity="0.8"><ellipse cx="80" cy="150" rx="12" ry="6"/><ellipse cx="120" cy="160" rx="9" ry="5"/><ellipse cx="50" cy="170" rx="7" ry="4"/></g>' }));
  });

// 2 · tireur — Poisson-archer : il crache un jet d'eau
Mo('bayou', 2, 'Poisson-archer', { scale: 0.92, atk: 'cast', fx: WATER, colors: { body: '#d8d8a0', bar: '#3a4630', fin: '#e0a830' }, grp: { tail: 'back', body: 'torso' }, piv: { back: [52, 172], torso: [106, 160] }, shine: [[190, 126, 9, WATER]] },
  ({ S, raw, T, G, halo, eye }) => {
    halo(190, 126, 14, WATER, 0.8);
    G('tail', () => S('M58 168 L20 140 C30 160 30 176 18 198 L60 182 Z', T.fin, { sh: 5 }));
    G('body', () => {
      S('M84 132 L88 104 L106 118 L112 98 L126 122 Z', T.fin, { sh: 3 });
      // la bouche pointe vers le haut : c'est par là que part le jet
      S('M46 176 C48 146 78 124 116 122 C140 121 158 128 170 138 C178 132 186 130 190 134 C190 142 184 148 176 152 C168 174 142 192 108 196 C80 198 56 192 46 176 Z', T.body, { sh: 10, hl: 6,
        inner: '<g fill="#3a4630" opacity="0.8"><path d="M82 128 C78 144 80 160 86 172 L98 170 C92 156 92 142 96 126 Z"/><path d="M112 124 C108 140 110 156 116 168 L128 164 C122 152 122 138 126 124 Z"/><path d="M60 150 C58 160 60 170 64 178 L74 176 C70 168 70 158 72 148 Z"/></g><path d="M50 184 C80 200 130 196 170 160 L176 206 L46 206 Z" fill="#fffbe0" opacity="0.7" filter="url(#g3)"/>' });
      raw('<ellipse cx="189" cy="134" rx="3" ry="4" fill="#2a2416" transform="rotate(35 189 134)"/><circle cx="190" cy="126" r="5" fill="#6fd0ff" stroke="#2a4a6a" stroke-width="1.4"/><circle cx="188.500" cy="124.500" r="1.6" fill="#fff"/>');
      S('M100 176 C90 184 86 196 90 206 C102 200 110 188 112 178 Z', T.fin, { sh: 3 });
      eye(150, 142, 11, 10.5, { iris: '#ffe14a', pupilK: 0.5, lid: 0.36, tilt: 1, look: [3, -3] });
    });
  });

// 3 · sorts — Feu follet : la lueur qui égare les voyageurs
Mo('bayou', 3, 'Feu follet', { atk: 'cast', fx: WISP, colors: { flame: '#3fd0a8', core: '#c8fff0', dark: '#1f8a7a' }, swing: ['handN'], far: ['handF'], grp: { tailW: 'back', body: 'torso' }, piv: { swing: [80, 150], far: [132, 150], back: [106, 186], torso: [106, 150] } },
  ({ S, raw, T, G, halo, eye }) => {
    halo(106, 140, 56, WISP, 0.55);
    G('tailW', () => S('M92 180 C96 196 110 200 104 216 C96 210 86 204 82 192 Z', T.dark, { sh: 4 }));
    G('handF', () => S('M132 146 C146 140 156 148 160 136 C164 152 154 164 140 160 Z', T.flame, { sh: 3, far: true }));
    G('handN', () => S('M80 146 C66 140 56 148 52 136 C48 152 58 164 72 160 Z', T.flame, { sh: 3 }));
    G('body', () => {
      S('M106 62 C114 84 126 92 134 104 C138 96 138 88 136 82 C150 100 146 122 142 136 C146 160 130 190 106 190 C82 190 66 164 70 138 C72 118 82 110 88 96 C92 104 96 108 98 100 C100 88 104 76 106 62 Z', T.flame, { sh: 10, hl: 7, so: 0.7,
        inner: '<path d="M106 110 C120 126 126 144 122 160 C118 176 94 176 90 160 C86 144 94 128 106 110 Z" fill="#c8fff0" opacity="0.8" filter="url(#g3)"/>' });
      raw('<path d="M88 134 L104 142 L90 148 Z M124 134 L110 142 L122 148 Z" fill="#0f3a34"/><path d="M98 160 C102 156 110 156 114 160 C110 166 102 166 98 160 Z" fill="#0f3a34"/>');
    });
  });

// 4 · élite — Silure géant : une gueule large comme une barque, de longs barbillons
Mo('bayou', 4, 'Silure géant', { scale: 1.16, atk: 'smash', wind: -12, hit: 18, colors: { skin: '#5a6444', dark: '#3e4830', belly: '#d8d4a8' }, swing: ['barb'], grp: { tail: 'back', fin: 'legs', body: 'torso' }, piv: { swing: [172, 168], back: [40, 182], torso: [106, 200] } },
  ({ S, raw, T, G, L, eye, teeth }) => {
    G('tail', () => S('M46 178 L10 150 C20 172 20 190 8 212 L48 196 Z', T.dark, { sh: 5 }));
    G('fin', () => { S('M116 200 C104 206 98 218 102 227 L138 227 C136 216 128 206 116 200 Z', T.dark, { sh: 3 }); S('M70 204 C62 210 60 220 64 227 L90 227 C88 218 80 208 70 204 Z', T.dark, { sh: 3, far: true }); });
    // les barbillons partent de sous la lèvre
    G('barb', () => { L([[[[170, 172], [206, 148], [210, 196]], 4.5, 1.6], [[[160, 170], [186, 126], [204, 140]], 4, 1.6]], 'dark', { N: 18 }); });
    G('body', () => {
      S('M84 150 L92 126 L112 146 Z', T.dark, { sh: 3 });
      raw(`<path d="M190 178 L134 186 L181 197 C164 194 164 186 190 178 Z" fill="${MAW}"/><path d="M144 186 C150 184 158 186 162 190 C156 193 148 193 144 190 Z" fill="#b8485a"/>`);
      S('M32 188 C38 160 78 142 120 142 C150 142 178 154 188 174 L190 177 L140 186 L186 198 C176 212 142 216 106 214 C70 214 40 208 32 188 Z', T.skin, { sh: 11, hl: 7,
        inner: '<path d="M36 196 C70 214 150 216 186 198 L190 222 L34 222 Z" fill="#d8d4a8" opacity="0.8" filter="url(#g3)"/><g fill="#3e4830" opacity="0.5"><circle cx="80" cy="164" r="5"/><circle cx="104" cy="156" r="4"/><circle cx="62" cy="178" r="3.6"/><circle cx="124" cy="168" r="3"/></g>' });
      teeth([186, 178], [146, 185.5], 5, 6, 1); teeth([182, 197], [146, 188], 5, -6, 1);
      eye(160, 160, 8, 7.5, { iris: '#ffe14a', pupilK: 0.5, lid: 0.44, tilt: 1 });
    });
  });

// 5 · boss — Vieux Crocodile : gueule béante, dos couvert de mousse
Mo('bayou', 5, 'Vieux Crocodile', { scale: 1.34, atk: 'smash', wind: -14, hit: 20, colors: { skin: '#4a6a3e', dark: '#33492a', belly: '#d8d8a0', moss: '#8fc85a' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [122, 172], back: [44, 186], torso: [86, 200] } },
  ({ S, raw, T, G, L, beast, eye, teeth }) => {
    const legs = beast({ front: 108, hind: 52, top: 198, w: 20, t: 'skin', dark: 'dark', claws: true, gap: 12 });
    G('tail', () => L([[[[46, 186], [4, 204], [10, 150]], 26, 6]], 'skin', { N: 18, inner: '<g stroke="#33492a" stroke-width="3" stroke-linecap="round" opacity="0.6"><path d="M20 188 l6 -8 M12 172 l8 -4"/></g>' }));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M34 196 C30 168 50 154 62 150 L68 134 L80 148 L90 130 L102 148 L114 134 L124 152 C136 158 142 170 142 186 C140 204 116 212 86 212 C58 212 36 208 34 196 Z', T.skin, { sh: 11, hl: 7,
      inner: '<path d="M40 204 C70 216 116 214 142 196 L146 222 L38 222 Z" fill="#d8d8a0" opacity="0.8" filter="url(#g3)"/><g fill="#8fc85a" opacity="0.85"><ellipse cx="70" cy="160" rx="12" ry="6"/><ellipse cx="104" cy="164" rx="10" ry="5"/><ellipse cx="50" cy="176" rx="7" ry="4"/></g>' }));
    G('head', () => {
      raw(`<path d="M210 152 L140 166 L199 187 C176 180 176 164 210 152 Z" fill="${MAW}"/><path d="M150 168 C160 165 168 168 172 174 C166 178 156 178 150 173 Z" fill="#b8485a"/>`);
      S('M112 170 C110 148 124 132 140 132 C150 126 162 130 164 142 C178 142 192 138 204 140 C212 142 213 150 208 153 L146 166 L202 186 C206 192 200 198 192 198 C168 202 142 200 126 192 C116 186 112 178 112 170 Z', T.skin, { sh: 10, hl: 6,
        inner: '<path d="M130 196 C156 202 184 200 204 190 L206 206 L128 206 Z" fill="#d8d8a0" opacity="0.8" filter="url(#g2)"/><ellipse cx="202" cy="144" rx="2.6" ry="2" fill="#1f2a18"/><g stroke="#33492a" stroke-width="2.6" stroke-linecap="round" opacity="0.6"><path d="M172 146 l8 3 M186 144 l8 3 M120 160 l10 2"/></g>' });
      teeth([206, 153], [152, 164.5], 7, 9, 1); teeth([200, 186], [152, 168], 6, -9, 1);
      eye(148, 144, 9, 8, { iris: '#ffe14a', pupil: 'slit', lid: 0.46, tilt: 1 });
    });
  });
