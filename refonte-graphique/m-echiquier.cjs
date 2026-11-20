// L'ÉCHIQUIER (terre) — les pièces d'un jeu d'échecs géant : ivoire fendillé, or terni, feutre vert, regards rouges.
// Membres attachés sous le corps, rien de posé par-dessus avec un contour (voir LISEZMOI, « Les monstres »).
const { Mo, metal } = require('./mon6.cjs');
const IV = '#e8dfc8', IVD = '#b8ac8e', GOLD = metal('#d8a83a'), FELT = '#2f7a4a', RED = '#e8442e';
const crack = (d) => `<path d="${d}" stroke="#8a7a5a" stroke-width="2" fill="none" opacity="0.7" stroke-linecap="round" stroke-linejoin="round"/>`;
const glare = (list) => `<path d="${list}" fill="${RED}"/><path d="${list}" fill="#ffb0a0" opacity="0.6" filter="url(#g2)"/>`;
/** Le socle d'une pièce : deux marches et le feutre. */
const base = (h, x0, x1) => { const m = (x0 + x1) / 2; h.S(`M${x0} 228 L${x0 + 4} 214 L${x0 + 14} 210 L${x0 + 18} 198 L${x1 - 18} 198 L${x1 - 14} 210 L${x1 - 4} 214 L${x1} 228 Z`, h.T.iv, { sh: 5, inner: `<path d="M${x0} 222 L${x1} 222 L${x1} 230 L${x0} 230 Z" fill="${FELT}"/><path d="M${x0 + 10} 211 L${x1 - 10} 211" stroke="#8a7a5a" stroke-width="2" opacity="0.6"/>` + `<path d="M${m - 20} 204 L${m + 20} 204" stroke="#d8a83a" stroke-width="4"/>` }); };
const C = { iv: IV, dark: IVD, gold: GOLD };

// 0 · rapide — Cavalier : il saute par-dessus les lignes
Mo('echiquier', 0, 'Cavalier', { scale: 0.98, atk: 'stab', wind: -12, hit: 16, colors: C, grp: { base: 'legs', body: 'torso' }, piv: { torso: [106, 210] } },
  (h) => { const { S, raw, T, G, eye } = h;
    G('base', () => base(h, 56, 156));
    G('body', () => {
      S('M96 96 L74 104 L92 112 L70 124 L90 130 L70 146 L92 148 L78 166 L100 164 Z', T.dark, { sh: 4 });
      S('M84 202 C78 164 86 124 106 98 L100 72 L118 86 C142 84 166 102 176 126 C180 136 174 144 164 142 L142 138 C134 152 136 172 142 202 Z', T.iv, { sh: 10, hl: 7,
        inner: crack('M112 150 L120 162 L114 174 M146 96 L140 108') + '<path d="M176 132 C168 136 158 136 150 132" stroke="#5a4a34" stroke-width="2.4" fill="none" stroke-linecap="round"/><ellipse cx="170" cy="124" rx="2.4" ry="3" fill="#5a4a34"/>' });
      eye(138, 108, 9.5, 8.5, { sclera: '#3a2a22', iris: RED, pupil: 'none', irisK: 0.5, lid: 0.44, tilt: 1, lidC: '#8a7a5a' });
    });
  });

// 1 · costaud — Tour : un donjon qui avance droit devant lui
Mo('echiquier', 1, 'Tour', { scale: 1.1, atk: 'smash', wind: -10, hit: 16, colors: C, grp: { base: 'legs', body: 'torso' }, piv: { torso: [106, 212] } },
  (h) => { const { S, raw, T, G, teeth } = h;
    G('base', () => base(h, 46, 166));
    G('body', () => {
      S('M64 202 L72 110 L58 104 L58 70 L78 70 L78 86 L96 86 L96 70 L116 70 L116 86 L134 86 L134 70 L154 70 L154 104 L140 110 L148 202 Z', T.iv, { sh: 11, hl: 7,
        inner: '<path d="M58 100 L154 100" stroke="#d8a83a" stroke-width="5"/>' + '<path d="M92 202 L92 176 C92 162 120 162 120 176 L120 202 Z" fill="#2a1c14"/>' + glare('M82 128 L100 134 L84 142 Z M130 128 L112 134 L128 142 Z') + crack('M134 150 L142 162 L136 176 M76 156 L82 168') });
      teeth([94, 176], [118, 176], 3, 9, 1, IV);
    });
  });

// 2 · tireur — Pion : petit, têtu, il lance des boulets
Mo('echiquier', 2, 'Pion lanceur', { scale: 0.88, atk: 'shoot', colors: C, swing: ['arm'], grp: { base: 'legs', body: 'torso' }, piv: { swing: [92, 150], head: [106, 132], torso: [106, 212] } },
  (h) => { const { S, raw, T, G, L, eye, disc, ell } = h;
    G('base', () => base(h, 62, 150));
    // le bras qui lance part de sous le col
    G('arm', () => { S(disc(58, 100, 12), T.gold, { sh: 4, hl: 3 }); L([[[[92, 150], [66, 140], [60, 110]], 11, 9]], 'iv'); });
    G('body', () => { S('M84 202 C88 180 92 164 92 150 L120 150 C120 164 124 180 128 202 Z', T.iv, { sh: 8, hl: 5 }); S(ell(106, 148, 24, 8), T.iv, { sh: 3, inner: '<path d="M84 148 L128 148" stroke="#d8a83a" stroke-width="4"/>' }); });
    G('head', () => {
      S(disc(106, 112, 30), T.iv, { sh: 9, hl: 7, inner: crack('M90 90 L98 100 L92 110') + '<path d="M100 128 C106 124 116 124 122 128" stroke="#5a4a34" stroke-width="2.6" fill="none" stroke-linecap="round"/>' });
      eye(100, 110, 8.5, 8, { sclera: '#3a2a22', iris: RED, pupil: 'none', irisK: 0.5, lid: 0.44, tilt: 1, lidC: '#8a7a5a' }); eye(122, 110, 7.5, 8, { sclera: '#3a2a22', iris: RED, pupil: 'none', irisK: 0.5, lid: 0.44, tilt: -1, lidC: '#8a7a5a' });
    });
  });

// 3 · sorts — Fou : il glisse en diagonale et murmure des bénédictions aux siens
Mo('echiquier', 3, 'Fou', { atk: 'cast', heal: true, fx: '#fff3c0', colors: C, grp: { base: 'legs', body: 'torso' }, piv: { head: [106, 120], torso: [106, 212] }, shine: [[106, 40, 9, '#ffe27a']], shineGrp: 'head' },
  (h) => { const { S, raw, T, G, halo, disc, ell } = h;
    halo(106, 40, 14, '#ffe27a', 0.8);
    G('base', () => base(h, 58, 154));
    G('body', () => { S('M82 202 C90 176 94 150 96 128 L116 128 C118 150 122 176 130 202 Z', T.iv, { sh: 9, hl: 6, inner: crack('M104 150 L110 164 L104 178') }); S(ell(106, 128, 26, 8), T.iv, { sh: 3, inner: '<path d="M82 128 L130 128" stroke="#d8a83a" stroke-width="4"/>' }); });
    G('head', () => {
      S(disc(106, 38, 11), T.gold, { sh: 3, hl: 3 });
      S('M106 46 C128 62 138 86 134 104 C130 118 120 124 106 124 C92 124 82 118 78 104 C74 86 84 62 106 46 Z', T.iv, { sh: 9, hl: 7,
        inner: '<path d="M112 52 L126 78 L118 82 L106 58 Z" fill="#3a2a22"/>' + glare('M88 96 L102 100 L90 106 Z M126 96 L112 100 L124 106 Z') + '<path d="M98 114 q8 4 16 0" stroke="#5a4a34" stroke-width="2.4" fill="none" stroke-linecap="round"/>' });
    });
  });

// 4 · élite — Dame : la pièce la plus dangereuse du plateau
Mo('echiquier', 4, 'Dame', { scale: 1.16, atk: 'stab', wind: -20, hit: 24, colors: C, swing: ['arm'], grp: { base: 'legs', body: 'torso' }, piv: { swing: [118, 140], head: [106, 116], torso: [106, 212] } },
  (h) => { const { S, raw, T, G, L, disc, ell, bar, blade } = h;
    G('base', () => base(h, 54, 158));
    G('arm', () => { const b = blade([150, 132], [206, 92], 11, 0.75); S(b.d, T.gold, { sh: 3, hl: 3 }); S(bar([142, 128], [154, 142], 5), T.gold, { sh: 2 }); L([[[[118, 142], [136, 150], [148, 136]], 10, 8]], 'iv'); S(disc(148, 136, 7), T.iv, { sh: 3 }); });
    G('body', () => { S('M78 202 C92 180 96 156 94 130 L118 130 C116 156 120 180 134 202 Z', T.iv, { sh: 9, hl: 6, inner: crack('M102 158 L110 170 L104 184') }); S(ell(106, 130, 28, 8), T.iv, { sh: 3, inner: '<path d="M80 130 L132 130" stroke="#d8a83a" stroke-width="4"/>' }); });
    G('head', () => {
      S('M76 76 L70 44 L88 62 L94 34 L106 60 L118 34 L124 62 L142 44 L136 76 Z', T.gold, { sh: 5, hl: 4, inner: '<g fill="#e8442e"><circle cx="94" cy="62" r="3.4"/><circle cx="118" cy="62" r="3.4"/></g>' });
      S('M76 92 C74 76 90 68 106 68 C122 68 138 76 136 92 C134 112 122 124 106 124 C90 124 78 112 76 92 Z', T.iv, { sh: 9, hl: 7,
        inner: glare('M86 90 L102 96 L88 102 Z M128 90 L112 96 L126 102 Z') + '<path d="M98 112 C104 108 112 108 118 112" stroke="#5a4a34" stroke-width="2.4" fill="none" stroke-linecap="round"/>' + crack('M124 76 L128 86') });
    });
  });

// 5 · boss — Roi : il se déplace d'une case, mais il écrase tout ce qui s'y trouve
Mo('echiquier', 5, 'Roi', { scale: 1.36, atk: 'smash', wind: -60, hit: 40, colors: C, swing: ['arm'], far: ['armF'], grp: { base: 'legs', body: 'torso' }, piv: { swing: [80, 134], far: [132, 134], head: [106, 112], torso: [106, 212] } },
  (h) => { const { S, raw, T, G, L, disc, ell, bar } = h;
    G('armF', () => { L([[[[132, 136], [158, 150], [164, 172]], 16, 14]], 'dark', { far: true }); S(disc(164, 176, 10), T.dark, { sh: 3, far: true }); });
    G('base', () => base(h, 44, 168));
    G('arm', () => { S(bar([52, 118], [44, 40], 6), T.gold, { sh: 2 }); S('M26 22 L62 18 L64 46 L28 50 Z', T.gold, { sh: 5, hl: 4, inner: '<path d="M34 28 L56 26 L58 40 L36 42 Z" fill="none" stroke="#8a5a1c" stroke-width="2"/>' }); L([[[[80, 136], [50, 142], [50, 116]], 18, 16]], 'iv'); S(disc(50, 112, 11), T.iv, { sh: 4 }); });
    G('body', () => { S('M68 202 C84 180 90 158 88 130 L124 130 C122 158 128 180 144 202 Z', T.iv, { sh: 11, hl: 7, inner: crack('M100 160 L110 174 L102 188 M124 150 L130 164') + '<path d="M96 138 L116 138 L112 196 L100 196 Z" fill="#d8a83a" opacity="0.5"/>' }); S(ell(106, 130, 34, 9), T.iv, { sh: 3, inner: '<path d="M74 130 L138 130" stroke="#d8a83a" stroke-width="5"/>' }); });
    G('head', () => {
      S('M100 54 L100 40 L88 40 L88 28 L100 28 L100 14 L112 14 L112 28 L124 28 L124 40 L112 40 L112 54 Z', T.gold, { sh: 4, hl: 3 });
      S('M72 72 L74 50 L90 60 L106 48 L122 60 L138 50 L140 72 Z', T.gold, { sh: 4, hl: 3 });
      S('M70 90 C68 74 88 66 106 66 C124 66 144 74 142 90 C140 104 134 114 126 120 L122 136 L114 124 L106 140 L98 124 L90 136 L86 120 C78 114 72 104 70 90 Z', T.iv, { sh: 10, hl: 7,
        inner: glare('M82 88 L100 94 L84 102 Z M130 88 L112 94 L128 102 Z') + '<path d="M96 110 C102 106 110 106 116 110" stroke="#5a4a34" stroke-width="2.6" fill="none" stroke-linecap="round"/>' + crack('M128 72 L134 84') });
    });
  });
