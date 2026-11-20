// L'ÉCHIQUIER (terre) — les pièces d'un jeu d'échecs géant : ivoire tourné, fendillé, des braises rouges dans les fentes,
// des filets d'or, un socle de feutre vert. Chaque pièce a son visage sculpté et sa silhouette.
// Bras et armes partent de sous le corps ; un seul contour par créature (voir LISEZMOI, « Les monstres »).
const { Mo, metal } = require('./mon6.cjs');
const IV = '#ece3cc', IVD = '#b8ac8e', GOLD = metal('#d8a83a'), FELT = '#2f7a4a', RED = '#ff4a2e', HOLLOW = '#2a1c18';
const C = { iv: IV, dark: IVD, gold: GOLD, ebony: '#2c2632' };
const P = (list) => list.map((d) => `<path d="${d}"/>`).join('');
/** Fissure : sombre au bord, braise au fond. */
const crack = (...list) => `<g fill="none" stroke-linecap="round" stroke-linejoin="round"><g stroke="${RED}" stroke-width="6" opacity="0.35" filter="url(#g2)">${P(list)}</g><g stroke="#4a2218" stroke-width="3.4">${P(list)}</g><g stroke="${RED}" stroke-width="1.5">${P(list)}</g></g>`;
/** Trait sculpté : un creux sombre et son arête claire. */
const groove = (list, w = 2.2) => `<g fill="none" stroke-linecap="round" stroke-linejoin="round"><g stroke="#fff8e6" stroke-width="${w * 0.7}" opacity="0.7" transform="translate(0 2)">${P(list)}</g><g stroke="#8a7a5a" stroke-width="${w}" opacity="0.8">${P(list)}</g></g>`;
/** Filet d'or incrusté. */
const inlay = (list, w = 3.4) => `<g fill="none" stroke-linecap="round" stroke-linejoin="round"><g stroke="#8a5a1c" stroke-width="${w + 1.6}">${P(list)}</g><g stroke="#e8c25a" stroke-width="${w}">${P(list)}</g></g>`;
const hollow = (d) => `<path d="${d}" fill="${HOLLOW}"/>`;
/** Braise au fond d'une orbite. */
const ember = (x, y, r) => `<circle cx="${x}" cy="${y}" r="${r * 2.4}" fill="${RED}" opacity="0.5" filter="url(#g2)"/><circle cx="${x}" cy="${y}" r="${r}" fill="${RED}"/><circle cx="${x + r * 0.2}" cy="${y - r * 0.25}" r="${r * 0.45}" fill="#ffd8a8"/>`;
/** Le socle : un tore tourné, un filet d'or, le feutre dessous. */
const base = (h, x0, x1) => { const m = (x0 + x1) / 2; h.S(`M${x0} 228 L${x0} 221 C${x0 - 1} 213 ${x0 + 5} 210 ${x0 + 12} 210 L${x0 + 18} 200 L${x1 - 18} 200 L${x1 - 12} 210 C${x1 - 5} 210 ${x1 + 1} 213 ${x1} 221 L${x1} 228 Z`, h.T.iv, { sh: 6, hl: 4,
  inner: `<path d="M${x0 - 2} 223 L${x1 + 2} 223 L${x1 + 2} 232 L${x0 - 2} 232 Z" fill="${FELT}"/><path d="M${x0 - 2} 223 L${x1 + 2} 223" stroke="#1c4a2c" stroke-width="2"/>` + inlay([`M${x0 + 3} 216 Q${m} 221 ${x1 - 3} 216`], 2.6) + groove([`M${x0 + 15} 208 Q${m} 212 ${x1 - 15} 208`]) }); };
/** Une bague tournée, avec son filet d'or. */
const collar = (h, x, y, rx, ry, gold = true) => h.S(h.ell(x, y, rx, ry), h.T.iv, { sh: 3, hl: 3, inner: gold ? inlay([`M${x - rx} ${y + 1} Q${x} ${y + ry * 1.1} ${x + rx} ${y + 1}`], 2.6) : '' });

// 0 · rapide — Cavalier : un cheval de guerre qui mord, crinière en dents de scie
Mo('echiquier', 0, 'Cavalier', { scale: 0.98, atk: 'stab', wind: -12, hit: 18, colors: C, grp: { base: 'legs', mane: 'torso', body: 'torso' }, piv: { torso: [106, 210] } },
  (h) => { const { S, raw, T, G, teeth } = h;
    G('base', () => base(h, 58, 154));
    G('mane', () => S('M102 90 L76 90 L92 104 L66 112 L86 124 L60 138 L84 146 L64 164 L88 166 L76 188 L100 182 Z', T.dark, { sh: 4, inner: groove(['M96 100 L80 96', 'M90 120 L72 118', 'M88 142 L68 144', 'M90 164 L72 170']) }));
    G('body', () => {
      S('M104 92 L90 58 L114 80 Z', T.dark, { sh: 3 });
      raw(`<path d="M186 158 L156 146 L168 169 C176 168 183 164 186 158 Z" fill="${HOLLOW}"/>`);
      S('M80 204 C72 166 78 124 100 96 L104 62 L120 84 C140 84 158 98 172 116 L190 138 C196 146 194 156 186 158 L156 146 L173 172 C164 181 150 178 142 166 C134 172 134 190 140 204 Z', T.iv, { sh: 10, hl: 7,
        inner: hollow('M122 100 L148 108 L143 117 L128 113 Z') + ember(138, 110, 3.4) + '<path d="M116 94 L150 104" stroke="#6a5a40" stroke-width="5" stroke-linecap="round"/><ellipse cx="184" cy="144" rx="3" ry="4.6" fill="#4a3a2a" transform="rotate(-35 184 144)"/>'
          + inlay(['M168 112 C161 122 158 134 160 146', 'M118 86 C130 100 146 122 158 140', 'M92 190 Q112 198 138 190'], 2.6) + '<circle cx="159" cy="142" r="4.6" fill="#e8c25a" stroke="#8a5a1c" stroke-width="1.4"/>'
          + groove(['M112 132 C124 124 140 130 144 148', 'M88 150 C96 146 104 146 110 150', 'M86 170 C94 166 104 166 114 170']) + crack('M112 142 L120 154 L112 166 L118 178', 'M146 90 L152 100') });
      teeth([160, 148], [183, 157], 3, 6, 1, '#fff8e6'); teeth([161, 154], [170, 169], 2, 5, -1, '#fff8e6');
    });
  });

// 1 · costaud — Tour : un bastion trapu sur ses deux poings crénelés, une herse pour bouche
Mo('echiquier', 1, 'Tour', { scale: 1.1, atk: 'smash', wind: -34, hit: 28, colors: C, swing: ['arm'], far: ['armB'], grp: { base: 'legs', body: 'torso' }, piv: { swing: [146, 140], far: [66, 142], torso: [106, 212] } },
  (h) => { const { S, raw, T, G, at, limb } = h;
    const fist = (x, y, a) => at(`translate(${x} ${y}) rotate(${a})`, () => S('M-17 15 L-17 -7 L-11 -7 L-11 -14 L-4 -14 L-4 -7 L4 -7 L4 -14 L11 -14 L11 -7 L17 -7 L17 15 Z', T.iv, { sh: 5, hl: 3, inner: inlay(['M-18 5 L18 5'], 2.6) + groove(['M-6 9 L-6 15', 'M6 9 L6 15']) }));
    // le poing arrière, posé au sol
    G('armB', () => { S(limb([[68, 142], [36, 156], [28, 196]], 20, 18, 16), T.dark, { sh: 5, inner: groove(['M40 160 L52 156']) }); fist(28, 211, 0); });
    // le poing avant, levé pour s'abattre
    G('arm', () => { S(limb([[146, 140], [178, 142], [184, 106]], 20, 18, 16), T.iv, { sh: 5, inner: groove(['M168 150 L180 146']) }); fist(184, 92, 8); });
    G('base', () => base(h, 48, 164));
    G('body', () => {
      S('M62 204 L70 124 L56 114 L50 72 L72 68 L74 86 L94 86 L94 64 L118 64 L118 86 L138 86 L140 68 L162 72 L156 114 L142 124 L150 204 Z', T.iv, { sh: 11, hl: 7,
        inner: inlay(['M52 102 Q106 110 160 102'], 4) + groove(['M68 150 L144 150', 'M66 176 L146 176', 'M84 124 L84 150', 'M128 124 L128 150', 'M76 150 L76 176', 'M136 150 L136 176', 'M70 124 Q106 130 142 124'])
          + hollow('M74 127 L106 137 L138 127 L136 142 L106 150 L76 142 Z') + ember(92, 138, 4) + ember(120, 138, 4)
          + hollow('M86 206 L86 180 C86 162 126 162 126 180 L126 206 Z') + `<ellipse cx="106" cy="202" rx="16" ry="8" fill="${RED}" opacity="0.6" filter="url(#g3)"/>`
          + inlay(['M96 168 L96 190', 'M106 166 L106 192', 'M116 168 L116 190', 'M87 178 L125 178'], 2.2) + '<path d="M92 189 L96 198 L100 189 Z M102 191 L106 200 L110 191 Z M112 189 L116 198 L120 189 Z" fill="#e8c25a" stroke="#8a5a1c" stroke-width="1.2" stroke-linejoin="round"/>'
          + crack('M134 152 L142 164 L136 178 L142 192', 'M68 74 L74 88 L70 98') });
    });
  });

// 2 · tireur — Pion lanceur : petit, fêlé, les dents serrées, un boulet d'ébène à bout de bras
Mo('echiquier', 2, 'Pion lanceur', { scale: 0.9, atk: 'shoot', colors: C, swing: ['arm'], grp: { base: 'legs', body: 'torso' }, piv: { swing: [94, 150], head: [106, 138], torso: [106, 212] } },
  (h) => { const { S, raw, T, G, L, disc } = h;
    G('base', () => base(h, 64, 148));
    G('arm', () => { S(disc(54, 94, 14), T.ebony, { sh: 4, hl: 4, inner: '<path d="M44 88 Q52 80 62 84" stroke="#8a84a0" stroke-width="2.4" fill="none" stroke-linecap="round" opacity="0.8"/>' }); L([[[[94, 150], [66, 144], [58, 114]], 11, 9]], 'iv'); S(disc(57, 110, 8), T.iv, { sh: 3 }); });
    G('body', () => { S('M70 204 C80 196 92 180 94 150 L118 150 C120 180 132 196 142 204 Z', T.iv, { sh: 8, hl: 5, inner: groove(['M88 178 Q106 184 124 178']) + crack('M112 160 L118 172 L112 184') }); collar(h, 106, 148, 26, 8); collar(h, 106, 139, 17, 5, false); });
    G('head', () => S(disc(106, 106, 31), T.iv, { sh: 9, hl: 7,
      inner: hollow('M88 100 L108 106 L104 112 L90 109 Z') + ember(98, 106, 2.6) + `<circle cx="124" cy="104" r="8.5" fill="${HOLLOW}"/>` + ember(125, 104, 4.2)
        + '<path d="M84 92 L108 100 M136 90 L116 98" stroke="#6a5a40" stroke-width="5" stroke-linecap="round"/>'
        + hollow('M97 121 L130 118 L129 131 L99 134 Z') + '<path d="M100 123.4 L127.4 121 L127 128.6 L101 131 Z" fill="#fff8e6"/><path d="M107 122.6 L107.4 130.6 M113.8 122 L114.2 130 M120.6 121.4 L121 129.4" stroke="#2a1c18" stroke-width="1.6"/>'
        + crack('M82 82 L92 92 L88 100 L100 108 L94 118 L98 128') }));
  });

// 3 · sorts — Fou : il bénit les siens, les yeux clos, une lueur dans la fente de sa mitre
Mo('echiquier', 3, 'Fou', { atk: 'cast', heal: true, fx: '#fff3c0', colors: C, grp: { base: 'legs', nimbus: 'head', body: 'torso' }, piv: { head: [106, 128], torso: [106, 212] }, shine: [[106, 34, 9, '#ffe27a']], shineGrp: 'head' },
  (h) => { const { S, raw, T, G, halo, disc } = h;
    halo(106, 34, 14, '#ffe27a', 0.8);
    G('base', () => base(h, 60, 152));
    // le nimbe : un anneau d'or derrière la tête
    G('nimbus', () => S(disc(106, 84, 47) + ' ' + disc(106, 84, 39), T.gold, { sh: 3, hl: 3, eo: true }));
    G('body', () => { S('M80 204 C92 190 98 162 98 132 L114 132 C114 162 120 190 132 204 Z', T.iv, { sh: 9, hl: 6,
      inner: inlay(['M106 138 L106 200'], 2.4) + '<path d="M106 148 L112 157 L106 166 L100 157 Z M106 172 L112 181 L106 190 L100 181 Z" fill="#e8c25a" stroke="#8a5a1c" stroke-width="1.4" stroke-linejoin="round"/>' + groove(['M88 192 Q106 198 124 192']) });
      collar(h, 106, 132, 26, 8); collar(h, 106, 123, 17, 5, false); });
    G('head', () => {
      S(disc(106, 34, 10), T.gold, { sh: 3, hl: 3 });
      S('M106 42 C130 58 140 86 136 104 C132 118 120 124 106 124 C92 124 80 118 76 104 C72 86 82 58 106 42 Z', T.iv, { sh: 9, hl: 7,
        inner: hollow('M114 50 L131 80 L122 85 L107 57 Z') + '<path d="M114 50 L131 80 L122 85 L107 57 Z" fill="#ffe27a" opacity="0.55" filter="url(#g2)"/>'
          + '<g transform="translate(3 0)">' + groove(['M84 110 Q106 122 128 110'], 2) + '<path d="M86 98 Q94 105 102 99 M110 99 Q118 105 126 98" stroke="#4a3a2a" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M84 90 L102 93 M128 90 L110 93" stroke="#6a5a40" stroke-width="3.4" stroke-linecap="round"/><path d="M106 96 L104 108 L109 108" stroke="#8a7a5a" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M99 115 L113 115" stroke="#4a3a2a" stroke-width="2.4" stroke-linecap="round"/></g>'
          + '<path d="M92 70 L97 78 L92 86 L87 78 Z" fill="#e8c25a" stroke="#8a5a1c" stroke-width="1.4" stroke-linejoin="round"/>' });
    });
  });

// 4 · élite — Dame : la pièce la plus dangereuse du plateau ; col en éventail, regard en amande, une lance d'or
Mo('echiquier', 4, 'Dame', { scale: 1.18, atk: 'stab', wind: -22, hit: 26, colors: C, swing: ['arm'], grp: { base: 'legs', ruff: 'head', body: 'torso' }, piv: { swing: [118, 144], head: [106, 128], torso: [106, 212] } },
  (h) => { const { S, raw, T, G, L, disc, blade, bar } = h;
    G('base', () => base(h, 56, 156));
    G('arm', () => { S(bar([132, 153], [200, 102], 4), T.gold, { sh: 2 }); S(blade([192, 108], [222, 85], 13, 0.45).d, T.gold, { sh: 3, hl: 3 }); S(disc(192, 108, 5.5), T.gold, { sh: 2, hl: 2 }); L([[[[118, 146], [132, 160], [148, 142]], 10, 8]], 'iv'); S(disc(148, 141, 7.5), T.iv, { sh: 3 }); });
    G('ruff', () => { S('M82 132 C62 116 54 92 60 64 L74 90 L78 70 L88 96 L92 128 Z', T.dark, { sh: 5, inner: inlay(['M60 66 L74 90 L78 72 L88 96'], 2) }); S('M130 132 C150 116 158 92 152 64 L138 90 L134 70 L124 96 L120 128 Z', T.dark, { sh: 5, inner: inlay(['M152 66 L138 90 L134 72 L124 96'], 2) }); });
    G('body', () => { S('M70 204 C92 190 100 166 96 134 L116 134 C112 166 120 190 142 204 Z', T.iv, { sh: 9, hl: 6,
      inner: inlay(['M82 202 C96 188 104 168 104 142', 'M130 202 C116 188 108 168 108 142'], 2.2) + groove(['M84 190 Q106 198 128 190']) + crack('M118 160 L124 172 L118 184') });
      collar(h, 106, 133, 27, 8); });
    G('head', () => {
      S('M78 80 L70 42 L88 62 L94 30 L106 58 L118 30 L124 62 L142 42 L134 80 Z', T.gold, { sh: 5, hl: 4, inner: `<g fill="${RED}" stroke="#7a1c10" stroke-width="1.2"><circle cx="92" cy="66" r="3.6"/><circle cx="120" cy="66" r="3.6"/><path d="M106 62 L110 68 L106 74 L102 68 Z"/></g>` });
      for (const [x, y] of [[70, 42], [94, 30], [118, 30], [142, 42]]) S(disc(x, y, 4.6), T.gold, { sh: 2, hl: 2 });
      S('M78 92 C76 76 90 68 106 68 C122 68 136 76 134 92 C132 108 122 120 109 127 C96 122 80 108 78 92 Z', T.iv, { sh: 9, hl: 7,
        inner: '<g transform="translate(3 0)">' + hollow('M84 91 C90 83 99 85 104 95 C97 99 89 98 84 91 Z M130 91 C124 83 115 85 110 95 C117 99 125 98 130 91 Z') + ember(95, 92, 2.6) + ember(119, 92, 2.6)
          + '<path d="M84 91 L78 85 M130 91 L136 85" stroke="#2a1c18" stroke-width="2.6" stroke-linecap="round"/><path d="M82 81 L102 88 M132 81 L112 88" stroke="#6a5a40" stroke-width="3" stroke-linecap="round"/>'
          + `<path d="M98 110 C104 114 113 113 120 105" stroke="#a02818" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M106 98 L105 104" stroke="#8a7a5a" stroke-width="2" stroke-linecap="round"/></g>` + crack('M126 100 L131 108 L126 116') });
    });
  });

// 5 · boss — Roi : il n'avance que d'une case, mais il écrase tout ce qui s'y trouve
Mo('echiquier', 5, 'Roi', { scale: 1.38, atk: 'smash', wind: -60, hit: 40, colors: C, swing: ['arm'], far: ['armF'], grp: { base: 'legs', body: 'torso' }, piv: { swing: [78, 138], far: [134, 138], head: [106, 122], torso: [106, 212] } },
  (h) => { const { S, raw, T, G, disc, ell, bar, blade, limb } = h;
    const fist = (x, y) => S(disc(x, y, 13), T.iv, { sh: 4, hl: 3, inner: groove([`M${x - 5} ${y - 4} L${x - 5} ${y + 8}`, `M${x + 2} ${y - 4} L${x + 2} ${y + 8}`]) });
    // le poing avant : du même ivoire que le reste
    G('armF', () => { S(limb([[134, 140], [166, 146], [174, 170]], 19, 17, 16), T.iv, { sh: 5, inner: inlay(['M162 160 L184 154'], 3) }); fist(175, 178); });
    G('base', () => base(h, 40, 172));
    // l'épée d'or, levée derrière lui
    G('arm', () => { const b = blade([52, 104], [32, -2], 20, 0.82); S(b.d, T.gold, { sh: 4, hl: 4, inner: '<path d="M51 98 L35 14" stroke="#8a5a1c" stroke-width="2.4" stroke-linecap="round" opacity="0.8"/>' }); S(bar([52, 104], [57, 130], 5), T.gold, { sh: 2 }); S(disc(58, 133, 6.5), T.gold, { sh: 2, hl: 2 }); S(bar([30, 110], [74, 100], 8), T.gold, { sh: 3, hl: 2 });
      S(limb([[78, 140], [46, 148], [52, 120]], 20, 17, 16), T.iv, { sh: 5 }); fist(53, 116); });
    G('body', () => {
      S('M58 204 C80 186 88 160 84 132 L128 132 C124 160 132 186 154 204 Z', T.iv, { sh: 11, hl: 7,
        inner: '<path d="M94 136 L118 136 L124 206 L88 206 Z" fill="#d8a83a" stroke="#8a5a1c" stroke-width="2"/><path d="M106 146 L112 156 L106 166 L100 156 Z M106 174 L113 185 L106 196 L99 185 Z" fill="#fff0b0" stroke="#8a5a1c" stroke-width="1.4" stroke-linejoin="round"/>'
          + '<g fill="#2a1c18"><path d="M78 176 l3 8 l-6 0 Z M70 192 l3 8 l-6 0 Z M84 194 l3 8 l-6 0 Z M134 176 l3 8 l-6 0 Z M142 192 l3 8 l-6 0 Z M128 194 l3 8 l-6 0 Z M82 156 l3 8 l-6 0 Z M130 156 l3 8 l-6 0 Z"/></g>' + crack('M132 150 L138 164 L132 174') });
      S(ell(106, 133, 44, 12), T.iv, { sh: 4, hl: 3, inner: inlay(['M62 134 Q106 148 150 134'], 3.4) });
    });
    G('head', () => {
      S('M100 52 L100 38 L88 38 L88 26 L100 26 L100 10 L112 10 L112 26 L124 26 L124 38 L112 38 L112 52 Z', T.gold, { sh: 4, hl: 3 });
      S('M68 80 L68 46 L84 58 L92 42 L106 56 L120 42 L128 58 L144 46 L144 80 Z', T.gold, { sh: 5, hl: 4, inner: `<path d="M68 70 L144 70" stroke="#8a5a1c" stroke-width="2"/><g fill="${RED}" stroke="#7a1c10" stroke-width="1.2"><circle cx="86" cy="66" r="3.6"/><circle cx="126" cy="66" r="3.6"/><path d="M106 60 L110 66 L106 72 L102 66 Z"/></g>` });
      S('M70 94 C68 78 88 70 106 70 C124 70 144 78 142 94 C142 106 138 114 132 120 L136 140 L122 132 L118 152 L106 136 L94 152 L90 132 L76 140 L80 120 C74 114 70 106 70 94 Z', T.iv, { sh: 10, hl: 7,
        inner: '<g transform="translate(3 0)"><path d="M76 86 L104 96 L108 96 L136 86 L136 94 L108 104 L104 104 L76 94 Z" fill="#8a7a5a"/><path d="M76 86 L104 96 L108 96 L136 86" stroke="#fff8e6" stroke-width="1.6" fill="none" opacity="0.7"/>'
          + hollow('M82 97 L102 104 L100 110 L86 106 Z M130 97 L110 104 L112 110 L126 106 Z') + ember(94, 104.5, 2.6) + ember(118, 104.5, 2.6)
          + '<path d="M103 102 L109 102 L112 116 L100 116 Z" fill="#cfc4a6"/><path d="M104 118 C94 114 84 118 78 128 C90 130 100 126 106 121 C112 126 122 130 134 128 C128 118 118 114 108 118 Z" fill="#b8ac8e"/><path d="M98 127 Q106 123 114 127" stroke="#2a1c18" stroke-width="2.4" fill="none" stroke-linecap="round"/></g>'
          + groove(['M92 132 L92 144', 'M106 130 L106 134', 'M120 132 L120 144', 'M84 124 L82 134', 'M128 124 L130 134']) + crack('M130 74 L136 84 L131 92') });
    });
  });
