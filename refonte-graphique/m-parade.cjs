// LA PARADE DES PÉTARDS (feu) — une fête du Nouvel An qui tourne mal : rouge, or, papier, poudre.
// Gueule ouverte découpée dans la silhouette, membres attachés sous le corps (voir LISEZMOI, « Les monstres »).
const { Mo, metal } = require('./mon6.cjs');
const RED = '#d8382e', GOLD = metal('#e6ac3c'), SPARK = '#ffd76a', MAW = '#2a0f14', FUR = '#fff6e0';
const dancer = (h, xs, far) => { for (const x of xs) { h.S(h.limb([[x, 190], [x + 2, 208], [x, 220]], 13, 11), h.TK('#2a2630'), { sh: 3, far }); h.S(h.ell(x + 4, 223, 11, 5), h.TK('#f4efe2'), { sh: 2, far }); } };

// 0 · rapide — Pétard sauteur : mèche allumée, il bondit avant d'éclater
Mo('parade', 0, 'Pétard sauteur', { scale: 0.9, atk: 'stab', wind: -10, hit: 12, fx: SPARK, colors: { body: RED, gold: GOLD, dark: '#2a2630' }, grp: { fuse: 'head', farLeg: 'legs', leg: 'legs', body: 'torso' }, piv: { head: [108, 108], torso: [106, 200] }, shine: [[134, 74, 9, SPARK]], shineGrp: 'head' },
  ({ S, raw, T, G, L, halo, eye, ell }) => {
    halo(134, 74, 16, SPARK, 0.9);
    G('fuse', () => { L([[[[108, 116], [110, 84], [132, 76]], 5, 3.5]], '#8a6a3a'); raw('<path d="M134 74 l8 -8 M134 74 l10 2 M134 74 l2 -11 M134 74 l-6 -8" stroke="#ffb020" stroke-width="2.6" stroke-linecap="round"/><circle cx="134" cy="74" r="4" fill="#fff3a8"/>'); });
    G('farLeg', () => { L([[[[122, 190], [132, 206], [126, 220]], 10, 8]], 'dark', { far: true }); S(ell(130, 223, 10, 5), T.dark, { sh: 2, far: true }); });
    G('leg', () => { L([[[[94, 192], [86, 206], [94, 220]], 11, 9]], 'dark'); S(ell(98, 223, 11, 5), T.dark, { sh: 2 }); });
    G('body', () => {
      S('M84 110 L130 104 C136 104 139 108 139 114 L143 186 C143 192 139 196 133 196 L88 200 C82 200 78 196 78 190 L74 118 C74 113 78 110 84 110 Z', T.body, { sh: 9, hl: 6,
        inner: '<path d="M70 124 L142 116 L143 128 L71 136 Z M74 178 L146 172 L146 184 L75 190 Z" fill="#e6ac3c"/><path d="M96 168 C106 176 122 176 132 166" stroke="#2a0f14" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M102 170 l4 6 l4 -5 l4 5 l4 -6 l4 5" stroke="#fff6e0" stroke-width="2.2" fill="none" stroke-linejoin="round"/>' });
      eye(102, 148, 9.5, 9, { iris: '#ffe14a', pupilK: 0.5, lid: 0.44, tilt: 1, lidC: '#7a1a16' }); eye(126, 146, 8.5, 9, { iris: '#ffe14a', pupilK: 0.5, lid: 0.44, tilt: -1, lidC: '#7a1a16' });
    });
  });

// 1 · costaud — Lion de papier : deux danseurs sous le tissu, une tête qui claque des mâchoires
Mo('parade', 1, 'Lion de papier', { scale: 1.1, atk: 'smash', wind: -16, hit: 22, colors: { body: '#f0b030', red: RED, gold: GOLD, fur: FUR, green: '#2fa36a' }, swing: ['head'], grp: { farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [110, 150], torso: [84, 200] } },
  (h) => { const { S, raw, T, G, fringe, eye, teeth } = h;
    G('farLegs', () => dancer(h, [66, 120], true));
    G('legs', () => dancer(h, [50, 104], false));
    G('body', () => S('M30 176 C30 146 54 130 84 132 C108 134 124 146 128 164 L130 196' + fringe(130, 32, 196, 8, 9) + ' Z', T.body, { sh: 10, hl: 6,
      inner: '<g fill="none" stroke="#d8382e" stroke-width="3"><path d="M40 160 q8 10 16 0 q8 10 16 0 q8 10 16 0 q8 10 16 0 q8 10 16 0 M36 178 q8 10 16 0 q8 10 16 0 q8 10 16 0 q8 10 16 0 q8 10 16 0 q8 10 16 0"/></g><path d="M34 150 C54 132 100 130 126 150" stroke="#fff6e0" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.9"/>' }));
    G('head', () => {
      S('M112 100 L90 86 L102 108 L80 110 L98 124 L80 134 L100 142 L88 158 L110 156 L140 120 Z', T.fur, { sh: 4 });
      S('M140 86 L146 60 L158 84 Z', T.red, { sh: 3 });
      S('M128 182 L132 204 L142 190 L150 208 L158 190 L168 204 L174 182 Z', T.fur, { sh: 3 });
      raw(`<path d="M194 140 L150 151 L185 167 C172 164 172 150 194 140 Z" fill="${MAW}"/>`);
      S('M102 134 C98 102 120 82 148 82 C174 82 192 100 195 124 C196 131 195 136 193 140 L154 151 L188 168 C180 182 162 188 144 186 C120 184 104 162 102 134 Z', T.body, { sh: 10, hl: 7,
        inner: '<path d="M116 104 L128 92 L134 104 L146 90 L152 104 L164 92 L168 104 L180 96 L182 110" stroke="#fff6e0" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="150" cy="98" r="7" fill="#d8382e" stroke="#fff6e0" stroke-width="2.5"/><path d="M184 122 C189 120 194 124 193 130 C188 132 184 128 184 122 Z" fill="#d8382e"/><path d="M112 150 q8 6 4 16" stroke="#d8382e" stroke-width="4" fill="none" stroke-linecap="round"/>' });
      teeth([190, 141], [158, 150], 4, 8, 1, '#fff6e0'); teeth([184, 167], [158, 154], 3, -7, 1, '#fff6e0');
      eye(134, 126, 13, 12, { iris: '#1c1020', pupil: 'none', irisK: 0.6, lid: 0.36, tilt: 1, lidC: '#d8382e' }); eye(166, 124, 10, 11, { iris: '#1c1020', pupil: 'none', irisK: 0.6, lid: 0.36, tilt: -1, lidC: '#d8382e' });
    });
  });

// 2 · tireur — Singe artificier : il allume ses fusées en ricanant
Mo('parade', 2, 'Singe artificier', { scale: 0.96, atk: 'cast', fx: SPARK, colors: { fur: '#8a5a34', pale: '#f0cfa0', vest: RED, gold: GOLD }, swing: ['rocket'], grp: { tail: 'back', farLeg: 'legs', leg: 'legs', body: 'torso' }, piv: { swing: [116, 164], head: [128, 138], back: [86, 186], torso: [106, 200] } },
  ({ S, raw, T, G, L, halo, eye, ell, bar, disc }) => {
    G('tail', () => L([[[[88, 188], [40, 196], [44, 144]], 10, 6]], 'fur', { N: 18 }));
    G('farLeg', () => { L([[[[120, 194], [134, 208], [128, 220]], 13, 10]], 'fur', { far: true }); S(ell(134, 223, 12, 5), T.fur, { sh: 2, far: true }); });
    G('leg', () => { L([[[[96, 196], [84, 208], [92, 220]], 14, 11]], 'fur'); S(ell(98, 223, 13, 5), T.fur, { sh: 2 }); });
    // la fusée et le bras qui la tient partent de sous le corps
    G('rocket', () => { S(bar([118, 178], [152, 160], 3), T.gold, { sh: 1 }); S(bar([146, 164], [190, 140], 15), T.vest, { sh: 4, hl: 3, inner: '<path d="M160 146 l8 16 M174 138 l8 16" stroke="#e6ac3c" stroke-width="4"/>' }); S('M186 132 L206 132 L196 148 Z', T.gold, { sh: 3 }); L([[[[112, 164], [134, 172], [160, 158]], 11, 9]], 'fur'); S(disc(162, 156, 9), T.fur, { sh: 3 }); });
    G('body', () => S('M84 180 C80 156 94 142 110 142 C126 142 136 156 134 176 C132 196 118 206 106 206 C94 206 86 194 84 180 Z', T.fur, { sh: 9, hl: 6,
      inner: '<path d="M80 150 C96 142 124 142 138 152 L136 186 C120 196 98 196 84 186 Z" fill="#d8382e"/><path d="M110 144 L110 196" stroke="#e6ac3c" stroke-width="4"/>' }));
    G('head', () => {
      S(disc(96, 112, 13), T.fur, { sh: 4, inner: '<circle cx="96" cy="112" r="6.5" fill="#f0cfa0"/>' });
      S('M96 116 C94 94 110 80 130 80 C148 80 162 94 162 112 C162 130 148 144 130 144 C110 144 98 132 96 116 Z', T.fur, { sh: 9, hl: 6,
        inner: '<path d="M112 108 C116 94 132 94 136 106 C140 94 156 96 158 110 C162 124 150 140 134 140 C120 140 108 126 112 108 Z" fill="#f0cfa0"/><path d="M120 126 L152 124 L148 136 L124 136 Z" fill="#3a1c14"/><path d="M124 127 l3 6 l3 -6 l3 6 l3 -6 l3 6 l3 -6 l3 6 l3 -6" stroke="#fff6e0" stroke-width="2" fill="none" stroke-linejoin="round"/>' });
      eye(124, 110, 9, 8, { iris: '#ffe14a', pupilK: 0.45, lid: 0.5, tilt: 1, lidC: '#5a3a20' }); eye(146, 110, 8, 7.5, { iris: '#ffe14a', pupilK: 0.45, lid: 0.5, tilt: -1, lidC: '#5a3a20' });
    });
  });

// 3 · sorts — Lanterne volante : sa lueur ranime la parade
Mo('parade', 3, 'Lanterne volante', { atk: 'cast', heal: true, fx: SPARK, colors: { paper: '#f08a3a', dark: '#b8482a', gold: GOLD, cord: RED }, grp: { cords: 'back', flame: 'torso', body: 'torso' }, piv: { back: [106, 176], torso: [106, 130] }, shine: [[106, 196, 12, SPARK]] },
  ({ S, raw, T, G, L, halo, ell }) => {
    halo(106, 124, 60, '#ffb84a', 0.55); halo(106, 196, 18, SPARK, 0.9);
    G('cords', () => { L([[[[84, 172], [70, 196], [78, 214]], 4, 3], [[[128, 172], [142, 196], [134, 214]], 4, 3]], 'cord'); raw('<circle cx="78" cy="216" r="5" fill="#d8382e" stroke="#2c1626" stroke-width="1.6"/><circle cx="134" cy="216" r="5" fill="#d8382e" stroke="#2c1626" stroke-width="1.6"/>'); });
    G('flame', () => S('M98 198 C94 188 102 184 104 174 C110 182 118 188 114 198 C112 204 100 204 98 198 Z', T.gold, { sh: 2, hl: 3 }));
    G('body', () => {
      S('M68 94 C68 76 88 66 106 66 C124 66 144 76 144 94 L136 168 C136 174 130 178 124 178 L88 178 C82 178 76 174 76 168 Z', T.paper, { sh: 10, hl: 8, so: 0.7,
        inner: '<ellipse cx="106" cy="126" rx="26" ry="40" fill="#ffe27a" opacity="0.6" filter="url(#g4)"/><g stroke="#b8482a" stroke-width="2.4" fill="none" opacity="0.6"><path d="M86 70 C80 104 82 140 88 176 M126 70 C132 104 130 140 124 176 M106 66 L106 178"/></g>' });
      S(ell(106, 176, 26, 6), T.gold, { sh: 2 }); S(ell(106, 68, 22, 5), T.gold, { sh: 2 });
      raw('<path d="M82 110 L102 120 L84 128 Z M130 110 L110 120 L128 128 Z" fill="#5a1c12"/><path d="M92 146 C100 140 112 140 120 146 C112 154 100 154 92 146 Z" fill="#5a1c12"/>');
    });
  });

// 4 · élite — Tambour géant : il se frappe lui-même pour donner la cadence
Mo('parade', 4, 'Tambour géant', { scale: 1.16, atk: 'smash', wind: -60, hit: 40, colors: { body: RED, gold: GOLD, skin: '#f4e6c8', dark: '#2a2630', wood: '#8a5a34' }, swing: ['armN'], far: ['armF'], grp: { farLeg: 'legs', leg: 'legs', body: 'torso' }, piv: { swing: [92, 116], far: [124, 112], torso: [100, 200] } },
  ({ S, raw, T, G, L, eye, ell, disc, bar }) => {
    const mallet = (a, b, far) => { S(bar(a, b, 5), T.wood, { sh: 2, far }); S(disc(b[0], b[1], 11), T.skin, { sh: 4, far }); };
    G('armF', () => { mallet([150, 78], [176, 52], true); L([[[[124, 114], [146, 104], [152, 78]], 13, 11]], 'dark', { far: true }); });
    G('farLeg', () => { L([[[[124, 192], [130, 210], [128, 220]], 18, 16]], 'dark', { far: true }); S(ell(132, 223, 15, 6), T.dark, { sh: 2, far: true }); });
    G('leg', () => { L([[[[78, 194], [72, 210], [76, 220]], 20, 18]], 'dark'); S(ell(80, 223, 16, 6), T.dark, { sh: 2 }); });
    G('armN', () => { mallet([76, 70], [70, 36], false); L([[[[92, 118], [66, 104], [76, 70]], 15, 13]], 'dark'); });
    G('body', () => {
      S('M40 152 C40 118 62 104 100 104 C138 104 162 118 162 152 C162 186 138 202 100 202 C62 202 40 186 40 152 Z', T.body, { sh: 12, hl: 8,
        inner: '<path d="M46 122 C80 108 122 108 156 122 L156 132 C122 118 80 118 46 132 Z M46 176 C80 190 122 190 156 176 L156 186 C122 200 80 200 46 186 Z" fill="#e6ac3c"/><g fill="#fff3c0"><circle cx="60" cy="150" r="3"/><circle cx="78" cy="152" r="3"/></g>' });
      S(ell(134, 152, 30, 46), T.skin, { sh: 6, hl: 5, inner: '<path d="M120 172 C128 180 142 180 150 170" stroke="#5a1c12" stroke-width="3.4" fill="none" stroke-linecap="round"/><path d="M126 174 l4 6 l4 -5 l4 5 l4 -6" stroke="#5a1c12" stroke-width="2" fill="none" stroke-linejoin="round"/><circle cx="134" cy="152" r="36" fill="none" stroke="#d8382e" stroke-width="3" opacity="0.5"/>' });
      eye(124, 140, 9.5, 10, { iris: '#d8382e', pupilK: 0.5, lid: 0.46, tilt: 1, look: [2, 1] }); eye(146, 138, 8, 10, { iris: '#d8382e', pupilK: 0.5, lid: 0.46, tilt: -1, look: [1, 1] });
    });
  });

// 5 · boss — Dragon de parade : un long corps de tissu qui ondule au bout de ses perches, une tête de fête immense
Mo('parade', 5, 'Dragon de parade', { scale: 1.34, atk: 'smash', wind: -16, hit: 22, fx: SPARK, colors: { body: RED, gold: GOLD, fur: FUR, green: '#2fa36a', wood: '#8a5a34' }, swing: ['head'], grp: { poles: 'legs', body: 'back' }, piv: { swing: [116, 150], back: [80, 150], torso: [84, 200] } },
  (h) => { const { S, raw, T, G, L, eye, teeth, limb, bar } = h;
    G('poles', () => { for (const [x, y] of [[28, 150], [70, 112], [112, 160]]) S(bar([x, y], [x, 228], 5), T.wood, { sh: 2 }); });
    G('body', () => {
      S('M22 150 L4 136 L10 156 L-4 168 L20 170 Z', T.green, { sh: 3 });
      S('M20 140 L24 116 L38 126 L46 98 L58 110 L70 84 L80 100 L96 86 L100 108 L114 112 L112 130 Z', T.green, { sh: 4 });
      S(limb([[18, 158], [64, 70], [124, 152]], 26, 44, 20), T.body, { sh: 9, hl: 6, inner: '<g fill="none" stroke="#e6ac3c" stroke-width="3"><path d="M26 146 q8 10 16 0 M40 124 q8 10 16 0 M58 110 q8 10 16 0 M78 112 q8 10 16 0 M96 128 q8 10 16 0"/></g>' });
    });
    G('head', () => {
      S('M112 108 L90 94 L102 116 L80 120 L100 132 L84 146 L106 150 L140 124 Z', T.green, { sh: 4 });
      L([[[[130, 92], [118, 62], [132, 40]], 9, 3], [[[124, 70], [108, 60], [104, 46]], 6, 2.5]], T.gold, { N: 16 }); L([[[[158, 88], [168, 62], [188, 46]], 8, 3], [[[170, 64], [186, 66], [196, 56]], 5, 2.5]], T.gold, { N: 16, far: true });
      // les moustaches partent du nez vers le haut, loin de la gueule
      L([[[[208, 116], [228, 104], [232, 78]], 4.5, 2], [[[200, 110], [212, 92], [208, 72]], 4, 2]], T.gold, { N: 18 });
      raw(`<path d="M216 139 L156 150 L205 169 C182 166 182 150 216 139 Z" fill="${MAW}"/><path d="M162 153 C172 151 180 155 184 161 C176 165 168 164 162 159 Z" fill="#f08a9a"/>`);
      S('M106 142 C102 108 124 86 150 86 C168 86 180 96 188 106 C198 104 210 110 216 120 C220 128 219 134 215 139 L162 149 L208 170 C200 184 174 190 150 186 C126 186 107 166 106 142 Z', T.body, { sh: 11, hl: 7,
        inner: '<path d="M116 104 L128 92 L136 104 L148 92 L154 104 L166 96 L170 108" stroke="#fff6e0" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M204 112 C209 109 215 113 215 119 C210 122 205 119 204 112 Z" fill="#7a1a16"/><path d="M128 172 C146 184 176 186 200 172" stroke="#e6ac3c" stroke-width="5" fill="none" stroke-linecap="round"/>' });
      teeth([210, 141], [168, 148.5], 5, 9, 1, '#fff6e0'); teeth([202, 168], [168, 153], 4, -8, 1, '#fff6e0');
      eye(138, 126, 13, 12, { iris: '#ffe14a', pupil: 'slit', lid: 0.4, tilt: 1, lidC: '#7a1a16' }); eye(168, 122, 10, 10.5, { iris: '#ffe14a', pupil: 'slit', lid: 0.4, tilt: -1, lidC: '#7a1a16' });
    });
  });
