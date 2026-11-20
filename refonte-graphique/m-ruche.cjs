// LA RUCHE (vent) — une colonie d'abeilles : rayures jaune et noir, ailes de verre, miel et cire.
// Membres attachés sous le corps, rien de posé par-dessus avec un contour (voir LISEZMOI, « Les monstres »).
const { Mo } = require('./mon6.cjs');
const Y = '#f0b020', K = '#2a2226', HONEY = '#ffb020', WING = '#dff4ff';
/** Une paire d'ailes transparentes (derrière le corps). */
const wings = (h, x, y, k = 1, far = false) => { for (const [a, l] of [[-58, 62], [-28, 50]]) h.raw(`<ellipse cx="${x - 20 * k}" cy="${y - l * 0.5 * k}" rx="${11 * k}" ry="${l * 0.5 * k}" transform="rotate(${a} ${x} ${y})" fill="${WING}" opacity="${far ? 0.5 : 0.8}" stroke="#2c1626" stroke-width="2"/>`); };
const stripes = (list) => `<g fill="${K}">${list.map((d) => `<path d="${d}"/>`).join('')}</g>`;

// 0 · rapide — Ouvrière : petite, vive, toujours la première sur l'intrus
Mo('ruche', 0, 'Ouvrière', { scale: 0.86, atk: 'stab', wind: -10, hit: 14, colors: { y: Y, k: K }, grp: { wings: 'back', sting: 'torso', legs: 'torso', body: 'torso' }, piv: { back: [96, 124], head: [132, 132], torso: [106, 150] } },
  (h) => { const { S, raw, T, G, L, eye } = h;
    G('wings', () => wings(h, 98, 124));
    G('sting', () => S('M52 160 L28 170 L54 172 Z', T.k, { sh: 2 }));
    G('legs', () => L([[[[100, 172], [96, 188], [104, 198]], 5, 3], [[[116, 170], [118, 188], [126, 196]], 5, 3], [[[130, 164], [140, 180], [148, 186]], 5, 3]], 'k'));
    G('body', () => S('M48 164 C46 144 62 132 84 134 C100 136 112 146 114 160 C114 176 98 184 80 184 C62 184 50 178 48 164 Z', T.y, { sh: 8, hl: 6, inner: stripes(['M62 134 C58 150 60 170 66 186 L78 186 C72 170 72 150 76 134 Z', 'M88 134 C86 150 88 170 94 186 L106 186 C102 170 100 150 102 134 Z']) }));
    G('head', () => {
      L([[[[130, 112], [134, 92], [148, 86]], 3.5, 3], [[[144, 112], [154, 96], [166, 96]], 3.5, 3]], 'k');
      S('M106 138 C104 120 118 108 136 110 C152 112 162 124 160 140 C158 156 144 164 130 162 C116 160 108 152 106 138 Z', T.y, { sh: 8, hl: 6, inner: '<path d="M140 150 l6 6 M148 148 l6 5" stroke="#2a2226" stroke-width="2.6" stroke-linecap="round"/>' });
      eye(138, 132, 11, 12, { sclera: '#2a2226', iris: '#fff', pupil: 'none', irisK: 0.42, lid: 0.3, tilt: 1, look: [3, -3], lidC: '#a8700a' });
    });
  });

// 1 · costaud — Soldat : cuirasse épaisse, grosses mandibules
Mo('ruche', 1, 'Soldat à dard', { scale: 1.1, atk: 'smash', wind: -16, hit: 22, colors: { y: Y, k: K, plate: '#5a4a3a' }, swing: ['head'], grp: { wings: 'back', abdomen: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [116, 150], back: [92, 124], torso: [106, 200] } },
  (h) => { const { S, raw, T, G, L, eye } = h;
    G('wings', () => wings(h, 92, 126, 1.1));
    G('abdomen', () => { S('M30 206 L8 218 L34 216 Z', T.k, { sh: 2 }); S('M86 162 C56 158 28 172 26 196 C26 212 44 220 66 218 C88 216 104 200 102 182 C100 172 94 164 86 162 Z', T.y, { sh: 9, hl: 6, inner: stripes(['M44 166 C36 182 38 204 46 220 L58 220 C50 204 50 182 58 162 Z', 'M70 160 C64 178 66 202 74 218 L86 214 C80 198 80 178 84 162 Z']) }); });
    G('legs', () => L([[[[94, 182], [84, 204], [90, 226]], 9, 6], [[[112, 184], [112, 206], [118, 226]], 9, 6], [[[128, 180], [142, 202], [148, 226]], 9, 6]], 'k'));
    G('body', () => S('M70 162 C68 140 84 126 104 126 C124 126 138 138 138 158 C138 178 124 190 104 190 C84 190 72 180 70 162 Z', T.plate, { sh: 9, hl: 6, inner: '<path d="M76 152 C92 142 118 142 134 152 M74 168 C92 160 118 160 136 168" stroke="#f0b020" stroke-width="5" fill="none"/>' }));
    G('head', () => {
      L([[[[140, 110], [142, 90], [156, 82]], 4, 3], [[[154, 112], [166, 96], [178, 98]], 4, 3]], 'k');
      // les mandibules sortent de sous la tête
      S('M156 160 L178 178 L164 152 Z', T.k, { sh: 2 }); S('M142 166 L152 188 L154 162 Z', T.k, { sh: 2 });
      S('M114 140 C112 120 128 108 146 110 C164 112 174 126 172 144 C170 160 156 170 140 168 C124 166 116 156 114 140 Z', T.y, { sh: 8, hl: 6, inner: '<path d="M116 124 C132 112 160 114 172 130 L170 120 C158 106 130 104 116 116 Z" fill="#5a4a3a"/>' });
      eye(148, 138, 11, 11, { sclera: '#2a2226', iris: '#ff5a3a', pupil: 'none', irisK: 0.42, lid: 0.42, tilt: 1, look: [3, -2], lidC: '#a8700a' });
    });
  });

// 2 · tireur — Cracheuse de cire : elle vise avec son abdomen gonflé de cire brûlante
Mo('ruche', 2, 'Cracheuse de cire', { scale: 0.96, atk: 'cast', fx: HONEY, colors: { y: Y, k: K, wax: '#ffd76a' }, grp: { wings: 'back', legs: 'torso', body: 'torso' }, piv: { back: [84, 120], head: [78, 124], torso: [106, 150] }, shine: [[176, 170, 11, HONEY]] },
  (h) => { const { S, raw, T, G, L, halo, eye } = h;
    halo(176, 170, 16, HONEY, 0.8);
    G('wings', () => wings(h, 86, 120));
    G('legs', () => L([[[[84, 156], [76, 172], [84, 182]], 5, 3], [[[98, 160], [98, 176], [106, 184]], 5, 3]], 'k'));
    G('body', () => {
      S('M96 150 C100 130 126 124 148 134 C166 142 178 156 180 170 C170 186 142 190 120 182 C104 176 94 164 96 150 Z', T.y, { sh: 9, hl: 6, inner: stripes(['M116 128 C112 146 114 168 122 184 L134 186 C126 168 126 146 130 128 Z', 'M142 132 C140 148 142 168 150 186 L162 184 C154 166 154 148 156 138 Z']) });
      S('M170 160 C180 158 188 164 188 172 C186 180 176 182 170 178 Z', T.wax, { sh: 3, hl: 3 });
    });
    G('head', () => {
      L([[[[72, 104], [62, 86], [48, 84]], 3.5, 3], [[[86, 102], [84, 82], [72, 74]], 3.5, 3]], 'k');
      S('M52 128 C50 110 64 98 82 100 C98 102 108 114 106 130 C104 146 90 154 76 152 C62 150 54 142 52 128 Z', T.y, { sh: 8, hl: 6, inner: '<path d="M84 142 q6 4 12 -2" stroke="#2a2226" stroke-width="2.6" fill="none" stroke-linecap="round"/>' });
      eye(86, 124, 10.5, 11.5, { sclera: '#2a2226', iris: '#fff', pupil: 'none', irisK: 0.42, lid: 0.4, tilt: 1, look: [3, -2], lidC: '#a8700a' });
    });
  });

// 3 · sorts — Nourrice : sa gelée royale remet la colonie sur pattes
Mo('ruche', 3, 'Nourrice', { atk: 'cast', heal: true, fx: '#fff3c0', colors: { y: '#f6cf6a', k: '#6a4a3a', pot: '#b8703a', honey: HONEY }, swing: ['arm'], grp: { wings: 'back', legs: 'legs', body: 'torso' }, piv: { swing: [112, 152], back: [96, 126], head: [108, 118], torso: [106, 200] }, shine: [[154, 150, 10, HONEY]], shineGrp: 'swing' },
  (h) => { const { S, raw, T, G, L, halo, eye, disc } = h;
    halo(154, 150, 14, HONEY, 0.7);
    G('wings', () => wings(h, 94, 128, 0.9));
    G('legs', () => L([[[[94, 198], [90, 212], [96, 224]], 7, 5], [[[118, 198], [122, 212], [128, 224]], 7, 5]], 'k'));
    G('arm', () => { S('M142 152 L166 152 L164 174 C160 180 148 180 144 174 Z', T.pot, { sh: 4, hl: 3, inner: '<path d="M142 152 L166 152 L166 158 L142 158 Z" fill="#ffb020"/>' }); L([[[[112, 152], [130, 164], [146, 162]], 8, 6]], 'k'); });
    G('body', () => S('M76 172 C72 146 88 132 106 132 C124 132 140 146 136 172 C134 192 122 204 106 204 C90 204 78 192 76 172 Z', T.y, { sh: 9, hl: 6, inner: `<g fill="#6a4a3a">${['M74 156 C92 148 120 148 138 156 L138 166 C120 158 92 158 74 166 Z', 'M76 180 C94 174 118 174 136 180 L134 190 C118 184 94 184 78 190 Z'].map((d) => `<path d="${d}"/>`).join('')}</g><path d="M78 138 C92 130 120 130 134 138 C128 146 84 146 78 138 Z" fill="#fff6e0"/>` }));
    G('head', () => {
      L([[[[96, 86], [88, 68], [76, 66]], 3.5, 3], [[[116, 86], [124, 68], [136, 66]], 3.5, 3]], 'k');
      S('M80 110 C78 92 92 82 106 82 C120 82 134 92 132 110 C130 126 120 134 106 134 C92 134 82 126 80 110 Z', T.y, { sh: 8, hl: 6, inner: '<path d="M98 122 q8 6 16 0" stroke="#6a4a3a" stroke-width="2.4" fill="none" stroke-linecap="round"/><g fill="#f08a9a" opacity="0.6"><circle cx="88" cy="116" r="5"/><circle cx="124" cy="116" r="5"/></g>' });
      raw('<path d="M90 106 q6 6 12 0 M110 106 q6 6 12 0" stroke="#3a2a22" stroke-width="2.8" fill="none" stroke-linecap="round"/>');
    });
  });

// 4 · élite — Frelon mercenaire : plus grand, plus sombre, il ne vit pas ici, on le paie
Mo('ruche', 4, 'Frelon mercenaire', { scale: 1.2, atk: 'stab', wind: -34, hit: 30, colors: { y: '#e8782a', k: '#3a1c14', dark: '#241210' }, swing: ['armN'], far: ['armF'], grp: { wings: 'back', sting: 'torso', legs: 'legs', body: 'torso' }, piv: { swing: [110, 138], far: [124, 138], back: [92, 112], head: [128, 104], torso: [106, 190] } },
  (h) => { const { S, raw, T, G, L, eye, limb } = h;
    G('wings', () => wings(h, 92, 112, 1.25));
    G('armF', () => { L([[[[124, 138], [150, 140], [168, 122]], 7, 5]], 'dark', { far: true }); S('M164 126 L192 110 L172 132 Z', T.dark, { sh: 2, far: true }); });
    G('sting', () => { S(limb([[84, 150], [48, 186], [70, 214]], 44, 16, 18), T.y, { sh: 8, inner: `<g fill="#3a1c14"><path d="M44 168 L84 186 L78 198 L42 182 Z"/><path d="M50 196 L80 204 L76 214 L54 208 Z"/></g>` }); S('M64 208 L72 228 L80 210 Z', T.k, { sh: 2 }); });
    G('legs', () => L([[[[96, 164], [92, 196], [98, 224]], 8, 5], [[[116, 164], [124, 196], [130, 224]], 8, 5]], 'k'));
    G('body', () => S('M76 134 C76 114 92 104 108 104 C124 104 138 114 136 136 C134 156 122 168 106 168 C90 168 78 154 76 134 Z', T.k, { sh: 9, hl: 6, inner: '<path d="M82 126 C96 118 120 118 132 126" stroke="#e8782a" stroke-width="5" fill="none"/>' }));
    G('armN', () => { S('M176 150 L208 146 L180 160 Z', T.dark, { sh: 2 }); L([[[[110, 138], [144, 164], [178, 154]], 8, 6]], 'k'); });
    G('head', () => {
      L([[[[122, 72], [124, 52], [140, 44]], 4, 3], [[[138, 74], [152, 58], [166, 62]], 4, 3]], 'k');
      S('M100 100 C98 80 114 68 132 70 C150 72 160 86 158 104 C156 120 142 130 128 128 C112 126 102 116 100 100 Z', T.y, { sh: 8, hl: 6 });
      S('M142 120 L160 132 L150 116 Z', T.k, { sh: 2 }); S('M130 124 L140 140 L140 122 Z', T.k, { sh: 2 });
      eye(134, 96, 12, 11, { sclera: '#241210', iris: '#ffe14a', pupil: 'none', irisK: 0.42, lid: 0.44, tilt: 1, look: [3, -2], lidC: '#a8700a' });
    });
  });

// 5 · boss — Reine : un abdomen énorme, une couronne de cire, un sceptre dégoulinant de miel
Mo('ruche', 5, 'Reine', { scale: 1.34, atk: 'smash', wind: -50, hit: 40, fx: HONEY, colors: { y: Y, k: K, gold: '#ffd76a', fur: '#fff6e0', wood: '#7a5230' }, swing: ['arm'], grp: { wings: 'back', abdomen: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [118, 132], back: [98, 116], head: [120, 96], torso: [106, 200] }, shine: [[180, 76, 12, HONEY]], shineGrp: 'swing' },
  (h) => { const { S, raw, T, G, L, halo, eye, limb, bar, disc } = h;
    halo(180, 76, 18, HONEY, 0.8);
    G('wings', () => wings(h, 98, 116, 1.3));
    G('abdomen', () => S('M100 150 C64 146 28 160 22 188 C18 210 44 226 76 226 C104 226 124 210 124 186 C124 170 114 156 100 150 Z', T.y, { sh: 12, hl: 8, inner: stripes(['M40 158 C32 178 34 204 46 222 L62 226 C48 206 48 178 56 154 Z', 'M72 150 C66 172 68 204 80 226 L98 222 C86 200 84 170 90 150 Z']) }));
    G('legs', () => L([[[[110, 168], [112, 198], [120, 224]], 8, 5], [[[128, 164], [138, 196], [146, 224]], 8, 5]], 'k'));
    G('arm', () => { S(bar([146, 150], [176, 86], 5), T.wood, { sh: 2 }); S(disc(180, 76, 13), T.gold, { sh: 4, hl: 4, inner: '<path d="M172 82 C174 92 178 98 182 90 Z" fill="#ffb020"/>' }); L([[[[118, 134], [140, 146], [156, 132]], 9, 7]], 'k'); });
    G('body', () => { S('M92 142 C90 120 104 110 120 110 C136 110 148 122 146 142 C144 160 132 170 118 170 C104 170 94 158 92 142 Z', T.k, { sh: 8, hl: 5 }); S('M90 116 L96 130 L104 118 L112 132 L120 118 L128 132 L136 118 L144 130 L150 116 C136 104 104 104 90 116 Z', T.fur, { sh: 4 }); });
    G('head', () => {
      L([[[[112, 62], [106, 44], [94, 40]], 4, 3], [[[134, 62], [146, 46], [158, 48]], 4, 3]], 'k');
      S('M94 90 C92 70 106 60 122 60 C138 60 152 70 150 90 C148 106 136 116 122 116 C108 116 96 106 94 90 Z', T.y, { sh: 8, hl: 6, inner: '<path d="M126 104 q8 4 14 -2" stroke="#2a2226" stroke-width="2.6" fill="none" stroke-linecap="round"/>' });
      S('M102 64 L100 42 L112 54 L122 36 L132 54 L144 42 L142 64 Z', T.gold, { sh: 4, hl: 3, inner: '<circle cx="122" cy="52" r="3.5" fill="#d8382e"/>' });
      eye(130, 86, 11.5, 11, { sclera: '#2a2226', iris: '#ff5ad8', pupil: 'none', irisK: 0.42, lid: 0.42, tilt: 1, look: [3, -2], lidC: '#a8700a' });
    });
  });
