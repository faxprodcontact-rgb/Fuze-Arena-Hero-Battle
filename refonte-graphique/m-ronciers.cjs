// LES RONCIERS (terre) — des bêtes faites de ronces, de mousse, de feuilles et d'écorce : la forêt qui se défend.
// Gueule ouverte découpée dans la silhouette, membres attachés sous le corps (voir LISEZMOI, « Les monstres »).
const { Mo } = require('./mon6.cjs');
const BARK = '#6a4a30', BARKD = '#46301e', LEAF = '#5fa83a', FALL = '#e08a2a', MOSS = '#7ab84a', GLOW = '#b8ff6a', MAW = '#1c120a';
const grain = (list) => `<g stroke="#2e1e12" stroke-width="2.4" fill="none" opacity="0.55" stroke-linecap="round">${list.map((d) => `<path d="${d}"/>`).join('')}</g>`;
const veins = (list, c = '#a85a14') => `<g stroke="${c}" stroke-width="2.2" fill="none" opacity="0.6" stroke-linecap="round">${list.map((d) => `<path d="${d}"/>`).join('')}</g>`;

// 0 · rapide — Renard de feuilles : un pelage de feuilles d'automne, il file entre les troncs
Mo('ronciers', 0, 'Renard de feuilles', { scale: 0.94, atk: 'slash', wind: -14, hit: 20, colors: { leaf: FALL, dark: '#b8601a', bark: BARKD, pale: '#f6e0b0' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [116, 164], back: [52, 170], torso: [90, 196] } },
  ({ S, raw, T, G, beast, eye }) => {
    const legs = beast({ front: 114, hind: 62, top: 190, w: 12, t: 'bark', dark: 'bark', claws: false });
    G('tail', () => S('M58 176 C40 180 22 172 14 156 L26 152 L10 138 L26 134 L12 118 L30 118 L22 100 L40 108 C56 122 66 148 64 168 Z', T.leaf, { sh: 7, hl: 5, inner: veins(['M56 166 C44 146 34 128 26 112']) + '<path d="M22 100 L40 108 C36 116 28 120 20 118 L30 118 Z" fill="#f6e0b0"/>' }));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M48 178 C46 164 54 156 64 152 L62 138 L76 148 L82 132 L92 146 L102 132 L108 148 L122 140 L122 156 C132 162 136 170 134 180 C132 196 112 204 88 204 C64 204 50 196 48 178 Z', T.leaf, { sh: 9, hl: 6,
      inner: veins(['M70 156 L78 190', 'M90 152 L94 194', 'M110 156 L108 190']) + '<path d="M56 194 C76 206 112 204 134 186 L136 212 L54 212 Z" fill="#f6e0b0" opacity="0.8" filter="url(#g3)"/>' }));
    G('head', () => {
      S('M118 132 L110 96 L136 118 Z', T.leaf, { sh: 3 }); S('M140 120 L148 90 L162 122 Z', T.dark, { sh: 3 });
      S('M108 154 C106 132 124 120 144 122 C160 124 174 136 192 152 C196 156 194 162 188 162 C174 168 158 178 140 180 C122 180 109 168 108 154 Z', T.leaf, { sh: 9, hl: 6,
        inner: '<path d="M142 160 C158 156 176 156 192 158 L190 172 L138 180 Z" fill="#f6e0b0" opacity="0.9" filter="url(#g2)"/><path d="M184 150 C189 149 194 153 193 158 C188 160 184 156 184 150 Z" fill="#1c120a"/><path d="M186 164 C176 168 166 170 156 170" stroke="#1c120a" stroke-width="2.2" fill="none" stroke-linecap="round"/>' });
      eye(150, 144, 9.5, 8, { sclera: '#f4ffd8', iris: LEAF, pupil: 'slit', lid: 0.46, tilt: 1 });
    });
  });

// 1 · costaud — Blaireau de mousse : trapu, têtu, le dos couvert de mousse et de champignons
Mo('ronciers', 1, 'Blaireau de mousse', { scale: 1.08, atk: 'smash', wind: -16, hit: 22, colors: { bark: BARK, dark: BARKD, moss: MOSS, birch: '#e8e0cc', cap: '#d8482e' }, swing: ['head'], grp: { farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [116, 176], torso: [86, 200] } },
  ({ S, raw, T, G, beast, fringe, eye, ell }) => {
    const legs = beast({ front: 110, hind: 54, top: 196, w: 20, t: 'bark', dark: 'dark', claws: true, gap: 12 });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      raw('<path d="M66 144 L66 128 M94 136 L94 120" stroke="#e8e0cc" stroke-width="5" stroke-linecap="round"/>');
      S(ell(66, 124, 13, 8), T.cap, { sh: 3, hl: 3 }); S(ell(94, 116, 11, 7), T.cap, { sh: 3, hl: 3 });
      S('M28 184 C26 156 52 140 84 140 C112 140 134 154 136 178 C137 190 132 198 126 204' + fringe(126, 38, 204, 7, 9) + ' C30 198 28 192 28 184 Z', T.bark, { sh: 11, hl: 6,
        inner: '<path d="M30 172 C40 146 70 136 96 138 C116 140 130 150 136 166 C112 156 60 156 30 172 Z" fill="#7ab84a"/><path d="M40 162 C56 148 80 144 100 146" stroke="#b8e88a" stroke-width="5" fill="none" opacity="0.6" stroke-linecap="round"/>' });
    });
    G('head', () => {
      S(ell(120, 152, 9, 10), T.dark, { sh: 3 }); S(ell(148, 146, 8, 9), T.dark, { sh: 3 });
      S('M108 176 C106 156 122 144 142 146 C160 148 178 160 194 176 C198 182 196 190 188 190 C172 198 150 202 132 198 C116 194 109 186 108 176 Z', T.dark, { sh: 9, hl: 6,
        inner: '<path d="M124 148 C140 152 164 164 194 178 L192 188 C166 176 142 166 122 162 Z" fill="#e8e0cc"/><path d="M130 198 C150 202 172 198 190 190 L190 204 L128 206 Z" fill="#e8e0cc" opacity="0.8" filter="url(#g2)"/><path d="M186 176 C191 175 196 179 195 184 C190 186 186 182 186 176 Z" fill="#1c120a"/>' });
      eye(150, 176, 8, 7, { sclera: '#f4ffd8', iris: LEAF, pupilK: 0.5, lid: 0.5, tilt: 1 });
    });
  });

// 2 · tireur — Porc-épic d'épines : il se hérisse et décoche ses ronces
Mo('ronciers', 2, 'Porc-épic d\'épines', { atk: 'shoot', colors: { bark: BARK, dark: BARKD, thorn: '#3e2a1a', tip: '#e8e0cc' }, grp: { quills: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { back: [96, 190], head: [128, 186], torso: [96, 204] } },
  ({ S, raw, T, G, beast, eye, saw, arcPts, pt }) => {
    const legs = beast({ front: 124, hind: 70, top: 204, w: 14, t: 'bark', dark: 'dark', claws: true, gap: 10 });
    G('quills', () => { const pts = arcPts(92, 186, 60, 62, 172, 352, 11); S(`M${pt(pts[0])}` + saw(pts, 40, [-4, -4]) + ' Z', T.thorn, { sh: 9, hl: 5, inner: '<path d="M40 176 C50 130 100 112 140 140" stroke="#e8e0cc" stroke-width="3" fill="none" opacity="0.35" stroke-dasharray="3 12" stroke-linecap="round"/>' }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M40 196 C38 170 62 154 92 154 C120 154 142 168 144 190 C144 206 122 214 92 214 C62 214 42 210 40 196 Z', T.bark, { sh: 9, hl: 6 }));
    G('head', () => {
      S('M112 190 C110 172 126 162 144 164 C160 166 176 176 190 190 C194 196 192 202 186 202 C170 208 150 210 134 206 C120 202 113 198 112 190 Z', T.dark, { sh: 8, hl: 5,
        inner: '<path d="M182 190 C187 189 192 193 191 198 C186 200 182 196 182 190 Z" fill="#1c120a"/><path d="M184 203 C174 206 164 206 154 204" stroke="#1c120a" stroke-width="2.2" fill="none" stroke-linecap="round"/>' });
      eye(148, 184, 8.5, 7.5, { sclera: '#f4ffd8', iris: FALL, pupilK: 0.45, lid: 0.44, tilt: 1 });
    });
  });

// 3 · sorts — Phalène d'écorce : ses ailes ont des yeux, sa poussière endort
Mo('ronciers', 3, 'Phalène d\'écorce', { atk: 'cast', fx: GLOW, colors: { wing: '#8a6a48', dark: BARKD, fuzz: '#d8c8a0' }, swing: ['wingN'], far: ['wingF'], grp: { body: 'torso' }, piv: { swing: [98, 130], far: [118, 130], torso: [108, 150] }, shine: [[58, 104, 11, GLOW]], shineGrp: 'swing' },
  ({ S, raw, T, G, L, halo, eye }) => {
    const spot = (x, y) => `<circle cx="${x}" cy="${y}" r="15" fill="#2e1e12"/><circle cx="${x}" cy="${y}" r="10" fill="${GLOW}"/><circle cx="${x}" cy="${y}" r="5" fill="#1c120a"/>`;
    halo(58, 104, 18, GLOW, 0.7); halo(160, 104, 16, GLOW, 0.6);
    G('wingF', () => S('M116 128 C134 80 176 64 204 82 C204 116 186 140 160 146 C176 160 172 190 150 198 C132 190 120 162 116 138 Z', T.wing, { sh: 8, far: true, inner: spot(160, 106) + grain(['M124 130 C146 108 172 96 196 92', 'M122 142 C136 160 146 178 150 192']) }));
    G('wingN', () => S('M100 128 C82 80 40 64 12 82 C12 116 30 140 56 146 C40 160 44 190 66 198 C84 190 96 162 100 138 Z', T.wing, { sh: 9, hl: 6, inner: spot(58, 106) + grain(['M92 130 C70 108 44 96 20 92', 'M94 142 C80 160 70 178 66 192', 'M84 150 C66 146 44 136 26 118']) }));
    G('body', () => {
      L([[[[100, 96], [84, 74], [66, 72]], 4, 2.5], [[[116, 96], [132, 74], [150, 72]], 4, 2.5]], 'dark');
      raw('<g stroke="#46301e" stroke-width="2" stroke-linecap="round"><path d="M92 82 l-4 -8 M84 76 l-2 -9 M76 73 l0 -9 M124 82 l4 -8 M132 76 l2 -9 M140 73 l0 -9"/></g>');
      S('M92 124 C90 104 98 92 108 92 C118 92 126 104 124 124 C124 152 118 186 108 196 C98 186 92 152 92 124 Z', T.fuzz, { sh: 8, hl: 6, inner: grain(['M94 140 L122 140', 'M95 154 L121 154', 'M98 168 L118 168']) });
      eye(101, 108, 7, 7, { sclera: '#1c120a', iris: GLOW, pupil: 'none', irisK: 0.5, lid: 0.4, tilt: 1, lidC: '#8a7a5a' }); eye(116, 108, 6.5, 7, { sclera: '#1c120a', iris: GLOW, pupil: 'none', irisK: 0.5, lid: 0.4, tilt: -1, lidC: '#8a7a5a' });
    });
  });

// 4 · élite — Mante-brindille : on la prend pour une branche, jusqu'au coup de faux
Mo('ronciers', 4, 'Mante-brindille', { scale: 1.2, atk: 'slash', wind: -44, hit: 40, colors: { twig: '#7a8a3a', dark: '#4e5a22', leaf: LEAF, blade: '#c8d88a' }, swing: ['armN'], far: ['armF'], grp: { farLegs: 'legs', legs: 'legs', abdomen: 'back', body: 'torso' }, piv: { swing: [116, 110], far: [126, 108], head: [124, 84], back: [92, 150], torso: [100, 160] } },
  ({ S, raw, T, G, L, eye, limb }) => {
    G('armF', () => { L([[[[126, 110], [152, 96], [150, 62]], 8, 6]], 'dark', { far: true }); S(limb([[150, 66], [176, 54], [196, 84]], 11, 2, 16), T.dark, { sh: 3, far: true }); });
    G('farLegs', () => L([[[[84, 160], [56, 176], [44, 226]], 6, 4], [[[104, 158], [130, 180], [138, 226]], 6, 4]], 'dark', { far: true, N: 16 }));
    G('abdomen', () => S(limb([[98, 150], [58, 170], [22, 148]], 22, 6, 18), T.twig, { sh: 6, inner: '<path d="M82 156 l-4 10 M66 162 l-4 10 M50 160 l-4 8" stroke="#4e5a22" stroke-width="2.4" stroke-linecap="round" opacity="0.7"/>' }));
    G('legs', () => L([[[[90, 162], [66, 184], [60, 226]], 7, 4], [[[106, 160], [118, 188], [122, 226]], 7, 4]], 'twig', { N: 16 }));
    // les bras-faux partent de sous le thorax
    G('armN', () => { L([[[[116, 112], [140, 128], [160, 106]], 9, 7]], 'twig'); S(limb([[158, 110], [184, 82], [206, 106]], 13, 2, 16), T.blade, { sh: 3, hl: 3, inner: '<path d="M168 100 l4 6 M178 92 l4 6 M188 90 l3 6" stroke="#4e5a22" stroke-width="1.8" stroke-linecap="round"/>' }); });
    G('body', () => S(limb([[98, 160], [102, 130], [122, 100]], 20, 16, 16), T.twig, { sh: 7, inner: '<path d="M104 150 L108 124" stroke="#4e5a22" stroke-width="2.4" stroke-linecap="round" opacity="0.6"/>' }));
    G('head', () => {
      L([[[[116, 70], [108, 48], [96, 40]], 3.5, 2.5], [[[130, 68], [136, 46], [148, 40]], 3.5, 2.5]], 'dark');
      S('M100 78 C98 66 110 60 124 60 C138 60 150 66 148 78 C146 90 134 104 124 106 C114 104 102 90 100 78 Z', T.twig, { sh: 7, hl: 5, inner: '<path d="M118 96 l6 6 l6 -6" stroke="#2e3410" stroke-width="2.2" fill="none" stroke-linejoin="round" stroke-linecap="round"/>' });
      eye(110, 76, 9, 8, { sclera: '#f4ffd8', iris: FALL, pupilK: 0.4, lid: 0.44, tilt: 1 }); eye(138, 76, 8, 8, { sclera: '#f4ffd8', iris: FALL, pupilK: 0.4, lid: 0.44, tilt: -1 });
    });
  });

// 5 · boss — Grand Cerf des ronces : ses bois sont une forêt, ses flancs sont cerclés d'épines
Mo('ronciers', 5, 'Grand Cerf des ronces', { scale: 1.36, atk: 'smash', wind: -20, hit: 28, colors: { bark: BARK, dark: BARKD, moss: MOSS, leaf: LEAF, antler: '#8a6a44' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [118, 150], back: [36, 150], torso: [84, 190] }, shine: [[144, 110, 9, GLOW]], shineGrp: 'swing' },
  ({ S, raw, T, G, L, beast, fringe, halo, eye, limb, ell }) => {
    const legs = beast({ front: 104, hind: 52, top: 180, w: 15, t: 'bark', dark: 'dark', hoof: true, gap: 13 });
    const leafAt = (x, y, a, far) => S(`M${x} ${y} C${x - 10} ${y - 8} ${x - 8} ${y - 22} ${x} ${y - 28} C${x + 8} ${y - 22} ${x + 10} ${y - 8} ${x} ${y} Z`.replace(/M|C|Z/g, (m) => m), T.leaf, { sh: 3, hl: 3, far });
    G('tail', () => S('M38 148 L22 136 L26 152 L16 160 L34 162 Z', T.moss, { sh: 3 }));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M28 160 C26 132 52 118 84 120 C110 122 128 136 130 158 C131 170 128 180 122 188' + fringe(122, 36, 188, 7, 9) + ' C30 180 28 170 28 160 Z', T.bark, { sh: 11, hl: 7,
      inner: grain(['M44 140 C42 156 44 172 50 184', 'M70 128 C68 148 70 170 76 186', 'M100 128 C102 148 100 168 96 184']) + '<path d="M30 152 C56 164 104 162 130 148 M32 170 C58 180 102 178 128 166" stroke="#2e1e12" stroke-width="4" fill="none"/><g fill="#2e1e12"><path d="M48 156 l4 -10 l4 10 Z M76 162 l4 -10 l4 10 Z M104 156 l4 -10 l4 10 Z M60 174 l4 -9 l4 9 Z M92 176 l4 -9 l4 9 Z"/></g><path d="M40 128 C56 118 84 116 104 122" stroke="#7ab84a" stroke-width="8" fill="none" stroke-linecap="round" opacity="0.9"/>' }));
    G('head', () => {
      // les bois partent de derrière le front
      for (const [p, w, far] of [[[[142, 92], [168, 54], [200, 44]], 8, 1], [[[170, 62], [176, 34], [190, 20]], 6, 1], [[[128, 94], [112, 46], [130, 8]], 10, 0], [[[118, 58], [92, 44], [80, 20]], 7, 0], [[[122, 34], [144, 26], [152, 6]], 6, 0]]) S(limb(p, w, 2.5, 16), T.antler, { sh: 3, far: !!far });
      leafAt(82, 22, 0, false); leafAt(154, 10, 0, false); leafAt(202, 46, 0, true);
      S('M96 134 L84 118 L106 122 Z', T.bark, { sh: 3 });
      S('M100 170 C96 148 102 122 116 108 C120 94 134 86 148 90 C158 92 166 100 172 110 C182 116 192 124 194 134 C194 142 186 146 178 144 C168 148 156 150 146 150 C140 160 136 172 136 186 C120 190 104 184 100 170 Z', T.bark, { sh: 10, hl: 6,
        inner: grain(['M112 150 C110 162 112 174 116 182', 'M126 130 C122 140 122 150 124 158']) + '<path d="M184 126 C189 125 194 129 193 134 C188 136 184 132 184 126 Z" fill="#1c120a"/><path d="M186 142 C178 144 170 144 162 142" stroke="#1c120a" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M100 168 C110 180 124 186 136 186 L134 200 L100 196 Z" fill="#7ab84a" opacity="0.8" filter="url(#g2)"/>' });
      halo(144, 110, 12, GLOW, 0.7);
      eye(144, 110, 9, 7.5, { sclera: '#f4ffd8', iris: GLOW, pupilK: 0.4, lid: 0.46, tilt: 1 });
    });
  });
