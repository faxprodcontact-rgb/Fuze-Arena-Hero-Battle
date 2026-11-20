// LA PARADE DES PÉTARDS (feu) — une fête du Nouvel An qui tourne mal : rouge, or, papier, poudre.
// Costumes travaillés : écailles peintes, galons dorés, fourrure, pompons, cordages. Gueule ouverte découpée dans la
// silhouette, membres attachés sous le corps, un seul contour (voir LISEZMOI, « Les monstres »).
const { Mo, metal } = require('./mon6.cjs');
const RED = '#d8382e', GOLD = metal('#e6ac3c'), SPARK = '#ffd76a', MAW = '#2a0f14', FUR = '#fff6e0', YEL = '#f0b030';
// rangées d'écailles peintes (dans `inner`, donc coupées par la forme)
const scaleGrid = (x0, y0, x1, y1, s, c, w = 2.4, op = 0.8) => { let d = ''; for (let y = y0, r = 0; y <= y1; y += s * 0.7, r++) { d += `M${x0 - (r % 2) * s / 2} ${y}`; for (let x = x0; x <= x1 + s; x += s) d += ` q${s / 2} ${s * 0.6} ${s} 0`; } return `<path d="${d}" stroke="${c}" stroke-width="${w}" fill="none" opacity="${op}"/>`; };
const studs = (pts, r = 2.6, c = '#fff3c0') => pts.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${c}"/>`).join('');
// jambes de danseur : pantalon du costume, chausson noir
const dancer = (h, xs, far) => { for (const x of xs) { h.S(h.ell(x + 4, 223, 11, 5), h.TK('#2a2630'), { sh: 2, far }); h.S(h.limb([[x, 188], [x + 2, 206], [x, 219]], 15, 12), h.TK(YEL), { sh: 3, far, inner: `<path d="M${x - 8} 198 q8 8 16 0" stroke="${RED}" stroke-width="2.4" fill="none"/><path d="M${x - 10} 214 L${x + 10} 214" stroke="${RED}" stroke-width="5"/>` }); } };

// 0 · rapide — Pétard sauteur : mèche allumée, chapelet de pétards à la traîne, il bondit avant d'éclater
Mo('parade', 0, 'Pétard sauteur', { scale: 0.94, atk: 'stab', wind: -10, hit: 12, fx: SPARK, colors: { body: RED, gold: GOLD, dark: '#2a2630' }, grp: { tail: 'back', fuse: 'head', farLeg: 'legs', leg: 'legs', body: 'torso' }, piv: { head: [108, 108], back: [78, 172], torso: [106, 200] }, shine: [[134, 70, 9, SPARK]], shineGrp: 'head' },
  ({ S, raw, T, G, L, halo, eye, brow, ell, bar }) => {
    halo(134, 70, 16, SPARK, 0.9);
    G('tail', () => { L([[[[80, 172], [56, 168], [40, 150]], 4, 3]], '#8a6a3a'); S(bar([60, 172], [50, 202], 8), T.body, { sh: 3 }); S(bar([42, 154], [24, 176], 8), T.body, { sh: 3 }); });
    G('fuse', () => { L([[[[108, 116], [108, 82], [132, 72]], 6, 4]], '#8a6a3a'); raw('<path d="M134 70 l9 -9 M134 70 l11 2 M134 70 l2 -12 M134 70 l-7 -8" stroke="#ffb020" stroke-width="2.8" stroke-linecap="round"/><circle cx="134" cy="70" r="4.5" fill="#fff3a8"/>'); });
    G('farLeg', () => { L([[[[122, 190], [136, 200], [150, 190]], 10, 8]], 'dark', { far: true }); S(ell(154, 188, 9, 6), T.dark, { sh: 2, far: true }); });
    G('leg', () => { L([[[[94, 192], [84, 208], [94, 220]], 11, 9]], 'dark'); S(ell(98, 223, 11, 5), T.dark, { sh: 2 }); });
    G('body', () => {
      // le haut du tube est déchiré : la mèche en sort
      S('M80 114 L78 98 L88 104 L94 90 L102 100 L110 86 L118 98 L126 88 L130 100 L138 96 L136 110 Z', T.gold, { sh: 3 });
      S('M84 110 L130 104 C136 104 139 108 139 114 L143 186 C143 192 139 196 133 196 L88 200 C82 200 78 196 78 190 L74 118 C74 113 78 110 84 110 Z', T.body, { sh: 9, hl: 6,
        inner: '<path d="M70 118 L142 110 L143 121 L71 129 Z M75 186 L146 180 L146 192 L76 198 Z" fill="#e6ac3c"/>' + studs([[84, 122], [100, 120], [116, 118], [132, 116], [88, 191], [104, 190], [120, 188], [136, 187]], 2.2, '#b8482a')
          + '<path d="M92 166 C106 160 124 158 136 162 L132 178 C120 184 106 184 96 179 Z" fill="#2a0f14"/><path d="M94 165 L99 173 L104 164 L109 172 L114 163 L119 171 L124 162 L129 170 L135 162 Z" fill="#fff6e0"/><path d="M98 180 L103 174 L108 182 L113 175 L118 183 L123 175 L129 180 Z" fill="#fff6e0"/>' });
      eye(102, 146, 9.5, 8.5, { iris: '#ffe14a', pupilK: 0.5, lid: 0.46, tilt: 1, lidC: '#7a1a16' }); eye(126, 144, 8.5, 8.5, { iris: '#ffe14a', pupilK: 0.5, lid: 0.46, tilt: -1, lidC: '#7a1a16' });
      brow(102, 135, 22, 1, '#5a0f0c', 5); brow(126, 133, 20, -1, '#5a0f0c', 5);
    });
  });

// 1 · costaud — Lion de papier : deux danseurs sous le tissu, une tête carrée qui claque des mâchoires
Mo('parade', 1, 'Lion de papier', { scale: 1.1, atk: 'smash', wind: -16, hit: 22, colors: { body: YEL, red: RED, gold: GOLD, fur: FUR, green: '#2fa36a' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [110, 150], back: [36, 160], torso: [84, 200] } },
  (h) => { const { S, raw, T, G, fringe, eye, brow, teeth, disc } = h;
    G('tail', () => { S('M38 166 C16 158 6 132 14 108 C30 118 42 136 48 156 Z', T.body, { sh: 4, inner: scaleGrid(4, 116, 50, 160, 14, RED) }); S('M4 112 L10 90 L16 104 L24 86 L26 108 L36 100 L28 120 Z', T.fur, { sh: 3 }); });
    G('farLegs', () => dancer(h, [66, 120], true));
    G('legs', () => dancer(h, [50, 104], false));
    G('body', () => S('M30 176 C30 146 54 130 84 132 C108 134 124 146 128 164 L130 196' + fringe(130, 32, 196, 8, 9) + ' Z', T.body, { sh: 10, hl: 6,
      inner: scaleGrid(30, 152, 130, 190, 18, RED, 3) + '<path d="M34 150 C54 132 100 130 126 150" stroke="#fff6e0" stroke-width="9" fill="none" stroke-linecap="round"/><path d="M32 190 L130 190" stroke="#d8382e" stroke-width="5"/>' + studs([[44, 190], [62, 190], [80, 190], [98, 190], [116, 190]], 2.2, SPARK) }));
    G('head', () => {
      // collerette de fourrure, oreille, corne et pompons sortent de sous la tête
      S('M112 100 L90 86 L102 108 L80 110 L98 124 L80 134 L100 142 L88 158 L110 156 L140 120 Z', T.fur, { sh: 4 });
      S('M118 96 C104 86 102 70 110 60 C122 68 128 82 128 96 Z', T.red, { sh: 3, inner: '<path d="M116 90 C110 82 110 74 112 68 C118 74 122 82 122 90 Z" fill="#e6ac3c"/>' });
      S('M146 86 L152 56 L164 84 Z', T.red, { sh: 3 }); S(disc(176, 86, 9), T.red, { sh: 3, hl: 2 }); S(disc(134, 80, 8), T.green, { sh: 3, hl: 2 });
      S('M128 182 L132 206 L142 190 L150 210 L158 190 L168 206 L176 182 Z', T.fur, { sh: 3 });
      raw(`<path d="M194 140 L150 151 L185 167 C172 164 172 150 194 140 Z" fill="${MAW}"/><path d="M156 154 C166 151 174 155 178 162 C170 166 162 165 156 160 Z" fill="#f08a9a"/>`);
      S('M102 134 C98 102 120 82 148 82 C174 82 192 100 195 124 C196 131 195 136 193 140 L154 151 L188 168 C180 182 162 188 144 186 C120 184 104 162 102 134 Z', T.body, { sh: 10, hl: 7,
        inner: '<path d="M116 104 L128 92 L134 104 L146 90 L152 104 L164 92 L168 104 L180 96 L182 110" stroke="#fff6e0" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="150" cy="97" r="7" fill="#bfe8f4" stroke="#e6ac3c" stroke-width="3"/><path d="M182 120 C188 117 195 122 194 130 C188 133 182 128 182 120 Z" fill="#d8382e"/><path d="M110 148 q10 4 6 18 M114 168 q8 2 8 10" stroke="#d8382e" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M126 176 C140 184 162 184 180 172" stroke="#d8382e" stroke-width="4" fill="none" stroke-linecap="round"/>' });
      teeth([190, 141], [158, 150], 4, 8, 1, FUR); teeth([184, 167], [158, 154], 3, -7, 1, FUR);
      eye(134, 127, 12.5, 11, { iris: '#7ad04a', pupilK: 0.42, lid: 0.42, tilt: 1, lidC: '#d8382e' }); eye(166, 125, 10, 10, { iris: '#7ad04a', pupilK: 0.42, lid: 0.42, tilt: -1, lidC: '#d8382e' });
      brow(134, 112, 30, 1, '#7a1a16', 6); brow(166, 111, 24, -1, '#7a1a16', 6);
    });
  });

// 2 · tireur — Singe artificier : des fusées dans le dos, une autre à la main, il ricane toutes dents dehors
Mo('parade', 2, 'Singe artificier', { scale: 0.98, atk: 'cast', fx: SPARK, colors: { fur: '#8a5a34', dark: '#5a3a20', pale: '#f0cfa0', vest: RED, gold: GOLD }, swing: ['rocket'], grp: { tail: 'back', pack: 'back', farLeg: 'legs', leg: 'legs', body: 'torso' }, piv: { swing: [116, 164], head: [128, 138], back: [86, 186], torso: [106, 200] } },
  ({ S, raw, T, G, L, eye, brow, ell, bar, disc }) => {
    G('tail', () => L([[[[88, 190], [40, 212], [26, 176]], 10, 6], [[[26, 178], [22, 160], [36, 158]], 6, 4.5]], 'fur', { N: 18 }));
    // les fusées de réserve, en bandoulière
    G('pack', () => { S('M40 122 L46 100 L62 116 Z', T.gold, { sh: 2 }); S(bar([88, 180], [52, 120], 9), T.vest, { sh: 3, inner: '<path d="M60 150 l14 -8 M52 136 l14 -8" stroke="#e6ac3c" stroke-width="3.4"/>' }); S('M56 110 L64 88 L78 106 Z', T.gold, { sh: 2 }); S(bar([98, 174], [68, 110], 9), T.vest, { sh: 3, inner: '<path d="M76 142 l14 -8 M68 128 l14 -8" stroke="#e6ac3c" stroke-width="3.4"/>' }); });
    G('farLeg', () => { L([[[[120, 194], [134, 208], [128, 220]], 13, 10]], 'dark', { far: true }); S(ell(134, 223, 12, 5), T.dark, { sh: 2, far: true }); });
    G('leg', () => { L([[[[96, 196], [84, 208], [92, 220]], 14, 11]], 'fur'); S(ell(98, 223, 13, 5), T.fur, { sh: 2 }); });
    // la fusée et le bras qui la tient partent de sous le corps
    G('rocket', () => { S(bar([118, 178], [152, 160], 3), T.gold, { sh: 1 }); S(bar([146, 164], [190, 140], 15), T.vest, { sh: 4, hl: 3, inner: '<path d="M158 147 l8 16 M172 139 l8 16" stroke="#e6ac3c" stroke-width="4"/><path d="M164 156 l4 -8 l5 5 Z" fill="#fff6e0"/>' }); S('M184 128 L210 130 L196 152 Z', T.gold, { sh: 3 }); L([[[[112, 164], [134, 174], [160, 158]], 12, 10]], 'fur'); S(disc(162, 156, 9.5), T.fur, { sh: 3 }); });
    G('body', () => S('M84 180 C80 156 94 142 110 142 C126 142 136 156 134 176 C132 196 118 206 106 206 C94 206 86 194 84 180 Z', T.fur, { sh: 9, hl: 6,
      inner: '<path d="M80 150 C96 142 124 142 138 152 L136 186 C120 196 98 196 84 186 Z" fill="#d8382e"/><path d="M104 144 L102 194 M118 144 L120 194" stroke="#e6ac3c" stroke-width="3.4"/><path d="M103 144 L119 144 L120 194 L102 194 Z" fill="#f0cfa0"/><path d="M82 180 C98 190 122 190 136 178" stroke="#2a2630" stroke-width="6" fill="none"/>' + studs([[111, 186]], 4.5, '#e6ac3c') + studs([[96, 160], [96, 172], [126, 158], [126, 170]], 2.2, SPARK) }));
    G('head', () => {
      S('M100 102 L76 92 L84 104 L72 114 L98 112 Z', T.vest, { sh: 3 });
      S('M110 88 L106 64 L118 76 L124 56 L134 76 L146 62 L146 88 Z', T.dark, { sh: 4 });
      S(disc(96, 114, 13), T.fur, { sh: 4, inner: '<circle cx="96" cy="114" r="6.5" fill="#f0cfa0"/>' });
      S('M96 116 C94 94 110 80 130 80 C148 80 162 94 162 112 C162 130 148 146 130 146 C110 146 98 132 96 116 Z', T.fur, { sh: 9, hl: 6,
        inner: '<path d="M112 110 C116 96 132 96 136 108 C140 96 156 98 158 112 C162 126 150 142 134 142 C120 142 108 128 112 110 Z" fill="#f0cfa0"/><path d="M98 98 C114 84 146 84 160 96" stroke="#d8382e" stroke-width="7" fill="none"/>'
          + '<path d="M116 124 C130 120 146 120 156 122 L152 136 C142 141 128 141 120 136 Z" fill="#3a1c14"/><path d="M118 124 L122 131 L127 123 L131 130 L136 122 L140 130 L145 122 L149 129 L155 122 Z" fill="#fff6e0"/><path d="M122 137 L125 130 L129 139 Z M146 137 L149 130 L152 136 Z" fill="#fff6e0"/><path d="M134 114 l-3 4 l6 0" stroke="#5a3a20" stroke-width="2" fill="none" stroke-linecap="round"/>' });
      eye(124, 110, 9, 7.5, { iris: '#ffe14a', pupilK: 0.42, lid: 0.5, tilt: 1, lidC: '#5a3a20' }); eye(146, 110, 8, 7, { iris: '#ffe14a', pupilK: 0.42, lid: 0.5, tilt: -1, lidC: '#5a3a20' });
      brow(124, 100, 20, 1, '#3a1c14', 4.5); brow(146, 100, 18, -1, '#3a1c14', 4.5);
    });
  });

// 3 · sorts — Lanterne volante : une lanterne de palais au visage découpé dans le papier ; sa lueur ranime la parade
Mo('parade', 3, 'Lanterne volante', { atk: 'cast', heal: true, fx: SPARK, colors: { paper: '#f08a3a', dark: '#b8482a', gold: GOLD, cord: RED }, grp: { cords: 'back', flame: 'torso', body: 'torso' }, piv: { back: [106, 78], torso: [106, 130] }, shine: [[106, 200, 11, SPARK]] },
  ({ S, raw, T, G, L, halo, ell, disc }) => {
    halo(106, 124, 60, '#ffb84a', 0.55); halo(106, 200, 18, SPARK, 0.9);
    // deux cordons pendent des coins du toit : un nœud doré, puis une frange
    G('cords', () => { L([[[[58, 76], [54, 94], [58, 112]], 4, 3], [[[154, 76], [158, 94], [154, 112]], 4, 3]], 'cord'); S('M54 116 L62 116 L64 146 L61 138 L58 148 L55 138 L52 146 Z', T.cord, { sh: 2 }); S(disc(58, 113, 5.5), T.gold, { sh: 2 }); S('M150 116 L158 116 L160 146 L157 138 L154 148 L151 138 L148 146 Z', T.cord, { sh: 2, far: true }); S(disc(154, 113, 5.5), T.gold, { sh: 2, far: true }); });
    G('flame', () => S('M98 202 C94 192 102 188 104 178 C110 186 118 192 114 202 C112 208 100 208 98 202 Z', T.gold, { sh: 2, hl: 3 }));
    G('body', () => {
      S(disc(106, 44, 7), T.gold, { sh: 2 });
      S('M70 96 C66 76 88 68 106 68 C124 68 146 76 142 96 C150 120 146 150 134 170 C130 176 82 176 78 170 C66 150 62 120 70 96 Z', T.paper, { sh: 10, hl: 8, so: 0.7,
        inner: '<ellipse cx="106" cy="126" rx="28" ry="42" fill="#ffe27a" opacity="0.6" filter="url(#g4)"/><g stroke="#b8482a" stroke-width="2.4" fill="none" opacity="0.6"><path d="M86 70 C74 104 76 140 88 176 M126 70 C138 104 136 140 124 176 M106 66 L106 178"/></g><path d="M66 92 C90 86 122 86 146 92 M66 158 C90 166 122 166 146 158" stroke="#d8382e" stroke-width="7" fill="none"/>' + studs([[78, 90], [96, 88], [116, 88], [134, 90], [80, 162], [98, 164], [114, 164], [132, 162]], 2, SPARK)
          + '<g fill="#fff3a8" stroke="#8a2a14" stroke-width="2" stroke-linejoin="round"><path d="M80 112 L102 120 L84 127 Z M132 112 L110 120 L128 127 Z"/><path d="M96 144 C102 140 110 140 116 144 C110 148 102 148 96 144 Z"/></g>' });
      S('M54 70 C74 72 90 62 106 50 C122 62 138 72 158 70 L150 80 C130 86 82 86 62 80 Z', T.gold, { sh: 3, hl: 3, inner: '<path d="M64 78 C84 82 128 82 148 78" stroke="#b8482a" stroke-width="2.4" fill="none" opacity="0.7"/>' });
      S('M82 168 L130 168 L124 184 L88 184 Z', T.gold, { sh: 3, inner: '<path d="M84 174 L128 174" stroke="#b8482a" stroke-width="2.4" opacity="0.7"/>' });
    });
  });

// 4 · élite — Tambour géant : un masque de guerre peint sur la peau, il se frappe lui-même pour donner la cadence
Mo('parade', 4, 'Tambour géant', { scale: 1.18, atk: 'smash', wind: -60, hit: 40, colors: { body: RED, gold: GOLD, skin: '#f4e6c8', dark: '#2a2630', wood: '#8a5a34' }, swing: ['armN'], far: ['armF'], grp: { farLeg: 'legs', leg: 'legs', body: 'torso' }, piv: { swing: [92, 116], far: [124, 112], torso: [100, 200] } },
  ({ S, raw, T, G, L, eye, brow, ell, disc, bar }) => {
    const mallet = (a, b, far) => { S(bar(a, b, 5.5), T.wood, { sh: 2, far }); S(disc(b[0], b[1], 13), T.body, { sh: 4, hl: 3, far, inner: `<path d="M${b[0] - 14} ${b[1] + 2} L${b[0] + 14} ${b[1] - 2}" stroke="#e6ac3c" stroke-width="4"/>` }); };
    G('armF', () => { mallet([152, 76], [180, 48], true); L([[[[124, 114], [148, 104], [152, 78]], 14, 12]], 'dark', { far: true }); });
    G('farLeg', () => { L([[[[124, 192], [130, 210], [128, 220]], 18, 16]], 'dark', { far: true }); S(ell(132, 223, 15, 6), T.dark, { sh: 2, far: true }); });
    G('leg', () => { L([[[[78, 194], [72, 210], [76, 220]], 20, 18]], 'dark'); S(ell(80, 223, 16, 6), T.dark, { sh: 2 }); });
    G('armN', () => { mallet([74, 68], [66, 32], false); L([[[[92, 118], [62, 104], [74, 68]], 16, 14]], 'dark', { inner: '<path d="M62 82 L84 78" stroke="#e6ac3c" stroke-width="5"/>' }); });
    G('body', () => {
      S('M40 152 C40 118 62 104 100 104 C138 104 162 118 162 152 C162 186 138 202 100 202 C62 202 40 186 40 152 Z', T.body, { sh: 12, hl: 8,
        inner: '<path d="M46 122 C80 108 122 108 156 122 L156 133 C122 119 80 119 46 133 Z M46 174 C80 188 122 188 156 174 L156 186 C122 200 80 200 46 186 Z" fill="#e6ac3c"/><path d="M48 134 L58 176 L70 128 L82 180 L94 126 L104 182" stroke="#f4e6c8" stroke-width="3" fill="none" stroke-linejoin="round" opacity="0.9"/>' + studs([[52, 126], [68, 120], [86, 116], [52, 182], [68, 188], [86, 192]], 2.6, '#b8482a') });
      // la peau du tambour : un masque de guerre
      S(ell(134, 152, 31, 47), T.skin, { sh: 6, hl: 5,
        inner: '<ellipse cx="134" cy="152" rx="27" ry="43" fill="none" stroke="#d8382e" stroke-width="3" opacity="0.55"/><path d="M108 132 C120 120 150 118 164 126 L162 152 C148 144 124 146 110 156 Z" fill="#d8382e"/><path d="M114 168 C126 164 146 162 156 164 L152 184 C142 190 128 190 120 186 Z" fill="#2a0f14"/><path d="M116 168 L121 177 L126 167 L131 176 L136 166 L141 175 L146 165 L150 174 L156 165 Z" fill="#fff6e0"/><path d="M122 187 L126 177 L131 189 Z M144 188 L148 177 L152 185 Z" fill="#fff6e0"/><path d="M134 108 L130 122 L140 122 Z" fill="#d8382e"/>' });
      eye(124, 141, 9, 8, { iris: '#ffe14a', pupilK: 0.42, lid: 0.48, tilt: 1, lidC: '#7a1a16' }); eye(147, 139, 7.5, 8, { iris: '#ffe14a', pupilK: 0.42, lid: 0.48, tilt: -1, lidC: '#7a1a16' });
      brow(124, 130, 22, 1, '#2a0f14', 5.5); brow(147, 128, 18, -1, '#2a0f14', 5.5);
    });
  });

// 5 · boss — Dragon de parade : un long corps de tissu qui ondule au bout de ses perches, une tête de fête immense
Mo('parade', 5, 'Dragon de parade', { scale: 1.36, atk: 'smash', wind: -16, hit: 22, fx: SPARK, colors: { body: RED, gold: GOLD, fur: FUR, green: '#2fa36a', wood: '#8a5a34' }, swing: ['head'], grp: { poles: 'legs', body: 'back' }, piv: { swing: [116, 150], back: [80, 150], torso: [84, 200] }, shine: [[200, 156, 9, SPARK]], shineGrp: 'swing' },
  (h) => { const { S, raw, T, G, L, halo, eye, brow, teeth, limb, bar, disc } = h;
    G('poles', () => { for (const [x, y] of [[32, 124], [62, 150], [94, 116]]) { S(bar([x, y], [x, 228], 5), T.wood, { sh: 2 }); S(disc(x, 196, 7), T.gold, { sh: 2 }); } });
    G('body', () => {
      // deux boucles : le corps ondule ; la crête dépasse tout le long du dos, la nageoire de queue sort de dessous
      S('M12 170 L-8 156 L0 176 L-10 192 L14 188 Z', T.green, { sh: 3 });
      S('M10 150 L10 114 L22 124 L30 76 L40 100 L48 82 L54 110 L64 100 L62 150 Z', T.green, { sh: 4 }); S('M64 150 L64 102 L76 110 L80 70 L90 92 L96 60 L104 90 L110 150 Z', T.green, { sh: 4 });
      S(limb([[8, 174], [32, 62], [64, 152]], 18, 30, 18), T.body, { sh: 8, hl: 5, inner: scaleGrid(0, 100, 70, 180, 14, '#e6ac3c', 2.6) });
      S(limb([[58, 152], [92, 58], [128, 154]], 30, 46, 20), T.body, { sh: 9, hl: 6, inner: scaleGrid(50, 92, 140, 178, 16, '#e6ac3c', 2.8) });
    });
    G('head', () => {
      S('M112 108 L90 94 L102 116 L80 120 L100 132 L84 146 L106 150 L140 124 Z', T.green, { sh: 4 });
      L([[[[130, 92], [118, 62], [132, 40]], 9, 3], [[[124, 70], [108, 60], [104, 46]], 6, 2.5]], T.gold, { N: 16 }); L([[[[158, 88], [168, 62], [188, 46]], 8, 3], [[[170, 64], [186, 66], [196, 56]], 5, 2.5]], T.gold, { N: 16, far: true });
      // les moustaches partent du nez vers le haut, la barbiche pend sous la mâchoire, loin de la gueule
      L([[[[208, 116], [228, 104], [232, 78]], 4.5, 2], [[[200, 110], [212, 92], [208, 72]], 4, 2]], T.gold, { N: 18 });
      S('M130 180 L128 204 L140 192 L146 214 L156 194 L166 208 L172 184 Z', T.green, { sh: 3 });
      halo(200, 156, 16, SPARK, 0.7);
      raw(`<path d="M216 139 L156 150 L205 169 C182 166 182 150 216 139 Z" fill="${MAW}"/><path d="M162 153 C172 151 180 155 184 161 C176 165 168 164 162 159 Z" fill="#f08a9a"/>`);
      S('M106 142 C102 108 124 86 150 86 C168 86 180 96 188 106 C198 104 210 110 216 120 C220 128 219 134 215 139 L162 149 L208 170 C200 184 174 190 150 186 C126 186 107 166 106 142 Z', T.body, { sh: 11, hl: 7,
        inner: '<path d="M116 104 L128 92 L136 104 L148 92 L154 104 L166 96 L170 108" stroke="#fff6e0" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M204 112 C209 109 215 113 215 119 C210 122 205 119 204 112 Z" fill="#7a1a16"/><path d="M128 172 C146 184 176 186 200 172" stroke="#e6ac3c" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M112 146 q10 4 6 16" stroke="#e6ac3c" stroke-width="4" fill="none" stroke-linecap="round"/>' + scaleGrid(108, 150, 150, 170, 12, '#e6ac3c', 2.2, 0.6) });
      teeth([210, 141], [168, 148.5], 5, 9, 1, FUR); teeth([202, 168], [168, 153], 4, -8, 1, FUR);
      eye(138, 127, 12.5, 11, { iris: '#ffe14a', pupil: 'slit', lid: 0.44, tilt: 1, lidC: '#7a1a16' }); eye(168, 123, 10, 10, { iris: '#ffe14a', pupil: 'slit', lid: 0.44, tilt: -1, lidC: '#7a1a16' });
      brow(138, 112, 30, 1, '#5a0f0c', 6); brow(168, 109, 24, -1, '#5a0f0c', 6);
    });
  });
