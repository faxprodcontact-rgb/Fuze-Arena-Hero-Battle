// LES ABYSSES (eau) — créatures des grands fonds : corps sombres, lumières vivantes, dents en aiguilles.
// Règles (propriétaire, 20/11/2026) : une gueule ouverte est DÉCOUPÉE dans la silhouette (aucun trait devant la bouche) ;
// pattes, pinces, tiges et tentacules partent de SOUS le corps (dessinés avant lui), jamais posés dessus avec un contour.
const { Mo, tone, metal } = require('./mon6.cjs');
const LUM = '#6ff0ff', LURE = '#ffe27a', MAW = '#1c0f1e';

// 0 · rapide — Poisson-hache : corps en lame d'argent, mâchoire en avant, rangée de lumières sous le ventre
Mo('abysses', 0, 'Poisson-hache', { scale: 0.9, atk: 'stab', wind: -8, hit: 10, colors: { body: metal('#8fb2c4'), fin: '#2f5f7a' }, grp: { tail: 'back', body: 'torso' }, piv: { back: [62, 146], torso: [106, 150] }, fx: LUM },
  ({ S, raw, T, G, halo, eye, teeth }) => {
    for (const [x, y] of [[88, 196], [102, 203], [117, 205], [132, 201]]) halo(x, y, 9, LUM, 0.75);
    G('tail', () => S('M72 146 L30 112 C40 138 40 158 28 184 L72 156 Z', T.fin, { sh: 5, inner: '<path d="M62 148 L40 126 M62 154 L40 172" stroke="#17323f" stroke-width="2" opacity="0.5"/>' }));
    G('body', () => {
      S('M88 110 L96 70 L112 98 L120 74 L132 104 Z', T.fin, { sh: 3 });
      // l'intérieur de la gueule, derrière le corps : son bord avant est creusé, il ne ferme pas la bouche
      raw(`<path d="M168 143 L128 153 L178 161 C158 158 152 150 168 143 Z" fill="${MAW}"/>`);
      // le corps : la gueule est une vraie encoche dans la silhouette (lèvre du haut → coin → menton en avant)
      S('M58 148 C66 122 94 104 128 102 C150 101 166 112 170 128 C171 135 170 140 167 144 L134 153 L178 160 C176 170 168 177 158 181 C150 196 136 208 118 210 C98 212 82 200 74 180 C68 168 62 158 58 148 Z', T.body, { sh: 10, hl: 6,
        inner: '<path d="M66 150 C92 170 118 174 132 156" stroke="#24465c" stroke-width="2.4" fill="none" opacity="0.4"/><path d="M96 152 C92 170 96 190 108 204" stroke="#24465c" stroke-width="2" fill="none" opacity="0.35"/>' });
      teeth([166, 144], [138, 152], 4, 8, 1); teeth([176, 160], [140, 154], 5, -9, 1);
      S('M100 152 C90 160 86 174 90 186 C100 180 108 168 110 154 Z', T.fin, { sh: 3 });
      for (const [x, y] of [[88, 194], [102, 201], [117, 203], [132, 199]]) raw(`<circle cx="${x}" cy="${y}" r="4.4" fill="${LUM}" stroke="#24465c" stroke-width="1.4"/><circle cx="${x - 1}" cy="${y - 1}" r="1.5" fill="#fff"/>`);
      eye(142, 123, 14, 13, { iris: '#ffe14a', pupil: 'slit', lid: 0.34, tilt: 1, look: [3, 1] });
    });
  });

// 1 · costaud — Bernard-l'ermite : il a élu domicile dans un vieux casque de scaphandrier
Mo('abysses', 1, 'Bernard-l\'ermite au casque', { scale: 1.06, atk: 'smash', wind: -55, hit: 38, colors: { brass: metal('#c9903c'), crab: '#e0603a', dark: '#8a2f24' },
  swing: ['claw'], grp: { farLegs: 'legs', legs: 'legs', shell: 'torso', body: 'torso', eyes: 'head', farClaw: 'far' }, piv: { swing: [160, 176], far: [156, 190], head: [140, 156], torso: [106, 200] } },
  ({ S, raw, T, G, eye, limb, disc, ell }) => {
    G('farLegs', () => { for (const p of [[[120, 186], [116, 206], [102, 227]], [[142, 188], [150, 208], [142, 227]]]) S(limb(p, 12, 5), T.dark, { sh: 3, far: true }); });
    G('farClaw', () => { S(limb([[154, 186], [174, 204], [190, 198]], 13, 11), T.crab, { sh: 4, far: true }); S(limb([[186, 196], [202, 186], [208, 202]], 14, 3), T.crab, { sh: 3, far: true }); S(limb([[186, 204], [200, 212], [208, 204]], 9, 3), T.crab, { sh: 3, far: true }); });
    G('shell', () => {
      S(ell(84, 72, 16, 8), T.brass, { sh: 3, hl: 2 });
      S(disc(84, 122, 54), T.brass, { sh: 12, hl: 8, inner: '<path d="M40 146 C64 170 108 172 132 148" stroke="#8a5a1c" stroke-width="5" fill="none" opacity="0.5"/><path d="M58 88 C52 96 48 106 48 118" stroke="#fff3c0" stroke-width="5" fill="none" opacity="0.55" stroke-linecap="round"/><path d="M96 70 C116 76 130 92 136 112" stroke="#8a5a1c" stroke-width="3" fill="none" opacity="0.4"/>' });
      S(disc(66, 122, 25), T.brass, { sh: 5, hl: 3, inner: '<circle cx="66" cy="122" r="17" fill="#163642"/><path d="M66 105 L66 139 M49 122 L83 122" stroke="#c9903c" stroke-width="4.5"/><path d="M54 112 Q60 106 68 108" stroke="#6ff0ff" stroke-width="3" fill="none" opacity="0.6" stroke-linecap="round"/>' });
      S(disc(112, 96, 11), T.brass, { sh: 3, hl: 2, inner: '<circle cx="112" cy="96" r="6.5" fill="#163642"/>' });
      for (const [x, y] of [[104, 76], [128, 122], [44, 152], [34, 124], [42, 92]]) raw(`<circle cx="${x}" cy="${y}" r="3.6" fill="#8a5a1c"/><circle cx="${x - 1}" cy="${y - 1}" r="1.3" fill="#fff3c0"/>`);
      S(ell(118, 170, 38, 17), T.brass, { sh: 5, hl: 3, inner: '<ellipse cx="121" cy="172" rx="28" ry="10" fill="#2a1820"/>' });
    });
    // tout ce qui sort du crabe part de sous sa carapace : yeux par le haut, pattes par le bas, pince par le côté
    G('eyes', () => { S(limb([[128, 164], [126, 146], [130, 134]], 6, 6), T.crab, { sh: 2 }); S(limb([[146, 164], [150, 148], [154, 138]], 6, 6), T.crab, { sh: 2 }); eye(131, 130, 8.5, 8.5, { iris: '#ffe14a', pupilK: 0.5, lid: 0.34, tilt: 1 }); eye(156, 134, 7.5, 7.5, { iris: '#ffe14a', pupilK: 0.5, lid: 0.34, tilt: -1 }); });
    G('legs', () => { for (const p of [[[108, 186], [94, 206], [84, 227]], [[126, 190], [126, 210], [116, 227]], [[144, 188], [162, 206], [166, 227]]]) S(limb(p, 13, 5), T.crab, { sh: 4 }); });
    G('claw', () => { S(limb([[154, 178], [176, 170], [188, 152]], 17, 16), T.crab, { sh: 5 }); S(limb([[184, 158], [210, 176], [222, 148]], 19, 4), T.crab, { sh: 5 }); S(limb([[180, 146], [200, 102], [224, 138]], 30, 4), T.crab, { sh: 7, inner: '<path d="M194 128 l5 7 M204 130 l4 7 M212 134 l3 6" stroke="#f4c8a0" stroke-width="2.6" stroke-linecap="round"/>' }); S(disc(184, 152, 16), T.crab, { sh: 5 }); });
    G('body', () => S('M94 174 C102 148 142 142 162 158 C174 168 174 188 162 196 C144 206 112 204 98 192 C92 186 92 180 94 174 Z', T.crab, { sh: 9, hl: 6, inner: '<path d="M106 190 C126 198 148 196 162 186" stroke="#f4c8a0" stroke-width="7" fill="none" opacity="0.5"/><path d="M132 184 l6 6 l6 -6 l6 6" stroke="#5a1c18" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' }));
  });

// 2 · tireur — Méduse : cloche lumineuse, bras ourlés, elle lance des décharges
Mo('abysses', 2, 'Méduse', { atk: 'cast', fx: '#ff8ad8', colors: { bell: '#a45fd0', arm: '#e6a0e6', frill: '#ffc8ec', core: '#ffd0f4' }, swing: ['arm'], grp: { tent: 'back', frills: 'torso', bell: 'head' }, piv: { swing: [132, 118], back: [104, 122], head: [104, 118], torso: [104, 150] }, shine: [[182, 150, 10, '#ff8ad8']], shineGrp: 'swing' },
  ({ S, raw, T, G, halo, eye, limb, disc }) => {
    halo(104, 92, 44, '#ff8ad8', 0.5);
    G('tent', () => { for (const p of [[[66, 112], [48, 160], [66, 212]], [[84, 112], [70, 176], [88, 220]], [[124, 112], [140, 178], [122, 220]]]) S(limb(p, 7, 2.5), T.arm, { sh: 3, so: 0.6 }); });
    G('frills', () => { for (const [x, k] of [[92, -1], [114, 1]]) S(`M${x - 9} 108 C${x - 16 * k - 9} 138 ${x + 10 * k - 9} 154 ${x - 6 * k - 9} 172 C${x - 16 * k - 9} 186 ${x + 4 * k - 9} 198 ${x - 4} 210 C${x + 12} 198 ${x + 18 * k + 9} 186 ${x + 8 * k + 9} 172 C${x + 20 * k + 9} 154 ${x - 4 * k + 9} 138 ${x + 9} 108 Z`, T.frill, { sh: 4, so: 0.6 }); });
    // le bras qui tire : il descend de sous la cloche puis se recourbe vers l'avant
    G('arm', () => { S(limb([[136, 108], [148, 178], [182, 152]], 11, 7, 18), T.arm, { sh: 3 }); S(disc(183, 150, 9), T.core, { sh: 2, hl: 3 }); });
    G('bell', () => {
      S('M48 122 C42 80 72 56 104 56 C136 56 166 80 160 122 C152 112 142 126 132 118 C124 110 114 126 104 118 C94 110 84 126 76 118 C66 110 56 126 48 122 Z', T.bell, { sh: 11, hl: 8, so: 0.75,
        inner: '<path d="M44 124 C56 104 152 104 164 124 L164 96 C150 90 58 90 44 96 Z" fill="#6a3a9a" opacity="0.45" filter="url(#g3)"/><ellipse cx="98" cy="80" rx="32" ry="15" fill="#ffd0f4" opacity="0.5" filter="url(#g4)"/><path d="M64 104 C66 84 78 70 94 64" stroke="#fff" stroke-width="5" fill="none" opacity="0.5" stroke-linecap="round"/><g fill="#ffd0f4" opacity="0.7"><circle cx="128" cy="72" r="4"/><circle cx="142" cy="84" r="3"/><circle cx="116" cy="66" r="2.6"/></g>' });
      eye(110, 100, 10, 8, { sclera: '#fff6a8', iris: '#ffb020', pupil: 'slit', lid: 0.36, tilt: 1, lidC: '#4a2470' }); eye(136, 100, 8, 7, { sclera: '#fff6a8', iris: '#ffb020', pupil: 'slit', lid: 0.36, tilt: -1, lidC: '#4a2470' });
    });
  });

// 3 · sorts — Baudroie : une lanterne au bout du front, une gueule pleine d'aiguilles
Mo('abysses', 3, 'Baudroie à lanterne', { atk: 'cast', fx: LURE, colors: { body: '#3a4468', fin: '#283058', lure: '#fff3a8' }, swing: ['lure'], grp: { tail: 'back', body: 'torso' }, piv: { swing: [112, 104], back: [46, 152], torso: [106, 156] }, shine: [[172, 80, 12, LURE]], shineGrp: 'swing' },
  ({ S, raw, T, G, halo, eye, teeth, limb, disc }) => {
    halo(172, 80, 22, LURE, 0.85);
    G('tail', () => S('M52 150 L14 122 C24 144 24 160 12 182 L52 162 Z', T.fin, { sh: 5 }));
    // la tige de la lanterne sort de derrière le front
    G('lure', () => { S(limb([[112, 110], [128, 48], [170, 74]], 6, 3.5), T.fin, { sh: 2 }); S(disc(172, 80, 9.5), T.lure, { sh: 2, hl: 4 }); });
    G('body', () => {
      S('M78 108 L70 82 L88 100 L92 76 L104 98 Z', T.fin, { sh: 3 });
      raw(`<path d="M175 142 L108 155 L173 176 C150 168 150 150 175 142 Z" fill="${MAW}"/><path d="M130 153 C138 150 146 152 150 158 C144 163 136 163 130 159 Z" fill="#b8485a"/>`);
      // la gueule : une encoche jusqu'au coin de la bouche, rien ne la referme devant
      S('M40 152 C38 116 72 94 106 96 C138 98 166 114 172 136 C173 138 174 140 174 142 L114 155 L172 174 C163 197 132 208 100 208 C70 208 42 188 40 152 Z', T.body, { sh: 11, hl: 7,
        inner: '<path d="M52 186 C80 206 130 208 166 184 L176 214 L44 214 Z" fill="#6a6f96" opacity="0.7" filter="url(#g3)"/>' });
      teeth([172, 142], [120, 153.5], 6, 13, 1); teeth([170, 173], [120, 157], 6, -12, 1);
      S('M84 168 C70 172 62 184 64 196 C76 192 86 184 92 172 Z', T.fin, { sh: 3 });
      eye(130, 122, 8.5, 8, { iris: '#bfe9ff', pupilK: 0.4, lid: 0.36, tilt: 1 });
    });
  });

// 4 · élite — Crabe-araignée : petite carapace hérissée perchée sur de longues pattes, pinces dressées
Mo('abysses', 4, 'Crabe-araignée', { scale: 1.14, atk: 'stab', wind: -34, hit: 30, colors: { shell: '#d8552e', leg: '#e88a4a', dark: '#8a3a22' }, swing: ['claws'], grp: { farLegs: 'legs', legs: 'legs', shell: 'torso', eyes: 'torso', farClaw: 'far' }, piv: { swing: [136, 140], far: [112, 110], torso: [106, 150] } },
  ({ S, raw, T, G, eye, limb, disc }) => {
    G('farLegs', () => { for (const p of [[[94, 132], [70, 60], [46, 227]], [[120, 132], [146, 60], [164, 227]]]) S(limb(p, 8, 3.5, 20), T.dark, { sh: 3, far: true }); });
    G('farClaw', () => { S(limb([[112, 112], [124, 80], [112, 58]], 9, 7), T.dark, { sh: 3, far: true }); S(limb([[114, 62], [98, 44], [114, 34]], 12, 3), T.dark, { sh: 3, far: true }); S(limb([[110, 60], [122, 48], [118, 36]], 8, 3), T.dark, { sh: 3, far: true }); });
    G('legs', () => { for (const p of [[[86, 136], [36, 74], [18, 227]], [[94, 142], [62, 110], [56, 227]], [[120, 142], [150, 110], [150, 227]], [[128, 136], [180, 74], [192, 227]]]) S(limb(p, 9, 4, 20), T.leg, { sh: 3 }); });
    // la pince sort de sous le bord de la carapace, loin des yeux
    G('claws', () => { S(limb([[132, 142], [182, 138], [178, 80]], 11, 9, 18), T.leg, { sh: 3 }); S(limb([[176, 84], [168, 50], [192, 48]], 16, 3), T.shell, { sh: 4 }); S(limb([[182, 84], [198, 68], [196, 52]], 10, 3), T.shell, { sh: 3 }); S(disc(178, 82, 9), T.shell, { sh: 3 }); });
    G('shell', () => S('M68 134 C66 120 72 108 80 102 L72 84 L90 96 C94 94 98 93 102 93 L104 72 L113 93 C119 94 125 97 129 101 L143 85 L138 107 C142 115 144 123 143 132 C141 148 126 160 106 160 C87 160 70 150 68 134 Z', T.shell, { sh: 10, hl: 6,
      inner: '<g fill="#ffd9b0" opacity="0.8"><circle cx="88" cy="114" r="3.6"/><circle cx="102" cy="107" r="3"/><circle cx="94" cy="128" r="2.6"/><circle cx="82" cy="134" r="2.4"/></g><path d="M108 148 l6 5 l6 -5 l6 5" stroke="#5a1c12" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' }));
    G('eyes', () => { eye(112, 126, 9, 9, { iris: '#ffe14a', pupilK: 0.5, lid: 0.36, tilt: 1 }); eye(131, 126, 7, 8, { iris: '#ffe14a', pupilK: 0.5, lid: 0.36, tilt: -1 }); });
  });

// 5 · boss — Calmar colossal : il se dresse sur ses bras, deux longs tentacules prêts à frapper
Mo('abysses', 5, 'Calmar colossal', { scale: 1.34, atk: 'smash', wind: -46, hit: 40, colors: { skin: '#b8323e' }, swing: ['whip'], grp: { farWhip: 'far', arms: 'legs', head: 'torso' }, piv: { swing: [126, 148], far: [112, 142], torso: [106, 170] } },
  ({ S, raw, T, G, eye, limb, disc, ell }) => {
    const suck = (pts, n) => { let s = ''; for (let i = 1; i <= n; i++) { const t = i / (n + 1), u = 1 - t, x = u * u * pts[0][0] + 2 * u * t * pts[1][0] + t * t * pts[2][0], y = u * u * pts[0][1] + 2 * u * t * pts[1][1] + t * t * pts[2][1]; s += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${(3.4 - t * 1.6).toFixed(1)}" fill="#f0b8a8" opacity="0.85"/>`; } return s; };
    G('farWhip', () => { const p = [[112, 142], [150, 92], [196, 104]]; S(limb(p, 10, 6), T.skin, { sh: 3, far: true }); S(ell(198, 106, 14, 9), T.skin, { sh: 3, far: true }); });
    // bras et tentacule partent de sous la tête : elle recouvre leur attache
    G('arms', () => { for (const [p, far] of [[[[92, 140], [48, 168], [22, 222]], 1], [[[120, 140], [166, 170], [190, 222]], 1], [[[86, 142], [66, 196], [44, 227]], 0], [[[98, 144], [88, 204], [74, 228]], 0], [[[110, 144], [112, 206], [106, 228]], 0], [[[122, 142], [140, 200], [150, 228]], 0]]) S(limb(p, 17, 4), T.skin, { sh: 4, far: !!far, inner: far ? '' : suck(p, 5) }); });
    G('whip', () => { const p = [[122, 144], [190, 132], [170, 58]]; S(limb(p, 12, 7, 18), T.skin, { sh: 4 }); S('M158 62 C156 44 166 28 176 24 C186 34 186 52 178 66 C172 70 162 68 158 62 Z', T.skin, { sh: 4, inner: '<g fill="#f0b8a8"><circle cx="170" cy="38" r="3"/><circle cx="174" cy="48" r="3.2"/><circle cx="170" cy="58" r="3"/></g>' }); });
    G('head', () => {
      S('M82 54 C58 36 42 46 38 68 C52 62 68 66 78 80 Z', T.skin, { sh: 5 }); S('M130 54 C154 36 170 46 174 68 C160 62 144 66 134 80 Z', T.skin, { sh: 5, far: true });
      // le manteau et la tête d'une seule forme : pas de trait entre les deux
      S('M106 6 C128 24 150 72 142 104 C146 112 145 124 143 131 C140 147 124 157 106 157 C88 157 72 147 69 131 C67 124 66 112 70 104 C62 72 84 24 106 6 Z', T.skin, { sh: 12, hl: 8,
        inner: '<path d="M88 100 C84 70 92 44 104 26" stroke="#f0b8a8" stroke-width="6" fill="none" opacity="0.4" stroke-linecap="round"/><g fill="#6e1c2c" opacity="0.5"><circle cx="118" cy="60" r="4"/><circle cx="126" cy="84" r="3"/><circle cx="110" cy="92" r="2.6"/></g>' });
      eye(100, 128, 14, 14, { iris: '#ffe14a', pupilK: 0.5, lid: 0.3, tilt: 1 }); eye(131, 127, 9.5, 11, { iris: '#ffe14a', pupilK: 0.5, lid: 0.3, tilt: -1 });
    });
  });
