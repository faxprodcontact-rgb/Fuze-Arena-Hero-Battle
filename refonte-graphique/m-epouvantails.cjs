// LES ÉPOUVANTAILS (vent) — les champs abandonnés : paille, toile de jute, bois, girouettes, tout ce que le vent agite.
// Membres attachés sous le corps, rien de posé par-dessus avec un contour (voir LISEZMOI, « Les monstres »).
const { Mo, metal } = require('./mon6.cjs');
const STRAW = '#e0c070', JUTE = '#b89a6a', WOOD = '#7a5230', TEAL = '#2f8f8a', GLOW = '#ffe14a', WIND = '#dffff0';
const hay = (d) => `<path d="${d}" stroke="#a8843a" stroke-width="2.2" fill="none" opacity="0.6" stroke-linecap="round"/>`;
const cut = (pts) => `<path d="${pts}" fill="#2a1c14"/>`;

// 0 · rapide — Girouette-coq : le coq de cuivre du toit, descendu régler ses comptes
Mo('epouvantails', 0, 'Girouette-coq', { scale: 0.96, atk: 'stab', wind: -12, hit: 16, colors: { cu: metal('#c8783a'), iron: metal('#5a5a6c'), red: '#d8382e', gold: metal('#e6ac3c') }, swing: ['head'], grp: { pole: 'legs', tailF: 'back', arrow: 'torso', body: 'torso' }, piv: { swing: [124, 150], back: [78, 150], torso: [106, 180] } },
  ({ S, raw, T, G, eye, limb, bar, ell }) => {
    G('pole', () => { S(bar([106, 176], [106, 222], 6), T.iron, { sh: 2 }); S(ell(106, 224, 22, 5), T.iron, { sh: 2 }); });
    G('tailF', () => { for (const p of [[[82, 146], [60, 110], [66, 80]], [[78, 150], [42, 138], [38, 102]], [[80, 156], [34, 162], [20, 134]]]) S(limb(p, 15, 4, 16), T.cu, { sh: 4 }); });
    G('arrow', () => { S(bar([54, 182], [166, 182], 5), T.iron, { sh: 2 }); S('M184 182 L164 171 L164 193 Z', T.iron, { sh: 3 }); S('M44 171 L62 171 L70 182 L62 193 L44 193 L52 182 Z', T.iron, { sh: 3 }); });
    G('body', () => S('M70 154 C70 134 88 124 108 128 C124 132 134 144 136 158 C136 172 122 180 104 180 C84 180 70 170 70 154 Z', T.cu, { sh: 8, hl: 6, inner: '<path d="M82 150 C94 142 112 146 118 160 C106 168 90 166 82 150 Z" fill="#5fb89a" opacity="0.55"/><g fill="#7a4a22"><circle cx="78" cy="158" r="2.4"/><circle cx="128" cy="160" r="2.4"/></g>' }));
    G('head', () => {
      S('M126 96 L122 74 L136 86 L140 66 L152 84 L162 72 L160 98 Z', T.red, { sh: 3 }); S('M162 112 L186 119 L162 128 Z', T.gold, { sh: 3 }); S('M150 128 C146 140 156 148 160 136 Z', T.red, { sh: 2 });
      S('M114 146 C110 120 122 98 142 96 C158 94 168 106 168 118 C168 130 158 138 146 138 C140 146 134 152 124 154 Z', T.cu, { sh: 7, hl: 5 });
      eye(150, 112, 9, 8.5, { iris: GLOW, pupilK: 0.5, lid: 0.44, tilt: 1 });
    });
  });

// 1 · costaud — Épouvantail : planté là, les bras en croix, il encaisse
Mo('epouvantails', 1, 'Épouvantail', { scale: 1.08, atk: 'smash', wind: -40, hit: 34, colors: { straw: STRAW, jute: JUTE, wood: WOOD, coat: TEAL, hat: '#8a6a3a' }, swing: ['armN'], far: ['armF'], grp: { pole: 'legs', body: 'torso' }, piv: { swing: [86, 128], far: [126, 128], head: [108, 114], torso: [106, 190] } },
  ({ S, raw, T, G, L, bar }) => {
    G('pole', () => S(bar([106, 160], [106, 228], 9), T.wood, { sh: 3 }));
    G('armF', () => { S('M184 122 L204 114 L194 128 L208 134 L192 140 L202 152 L182 142 Z', T.straw, { sh: 3, far: true }); L([[[[126, 128], [160, 122], [188, 132]], 20, 18]], 'coat', { far: true }); });
    G('armN', () => { S('M28 124 L8 116 L18 130 L4 136 L20 142 L10 154 L30 144 Z', T.straw, { sh: 3 }); L([[[[86, 128], [52, 122], [24, 134]], 22, 20]], 'coat', { inner: '<path d="M44 118 L60 116 L62 134 L46 136 Z" fill="#e0a030"/>' }); });
    G('body', () => S('M78 124 C78 110 134 110 134 124 L144 180 L132 172 L124 186 L114 174 L106 188 L98 174 L88 186 L80 172 L68 180 Z', T.coat, { sh: 9, hl: 6,
      inner: '<path d="M70 152 L142 152 L142 160 L70 160 Z" fill="#8a6a3a"/><path d="M112 126 L128 128 L126 146 L110 144 Z" fill="#d8382e"/><path d="M112 126 L128 128 L126 146 L110 144 Z" fill="none" stroke="#2a1c14" stroke-width="1.6" stroke-dasharray="3 3"/>' }));
    G('head', () => {
      S('M88 116 L84 130 L96 122 L102 134 L108 122 L116 134 L120 122 L132 130 L128 114 Z', T.straw, { sh: 3 });
      S('M82 96 C78 72 92 58 108 58 C124 58 138 72 134 96 C132 110 122 118 108 118 C94 118 84 110 82 96 Z', T.jute, { sh: 8, hl: 5,
        inner: cut('M90 80 L104 86 L92 94 Z M128 80 L114 86 L126 94 Z') + '<circle cx="97" cy="87" r="2.6" fill="#ffe14a"/><circle cx="121" cy="87" r="2.6" fill="#ffe14a"/><path d="M92 104 L98 100 L104 106 L110 100 L116 106 L122 100 L126 104" stroke="#2a1c14" stroke-width="2.6" fill="none" stroke-linejoin="round" stroke-linecap="round"/>' });
      S('M88 64 C90 40 104 30 118 34 C130 38 132 54 128 64 Z', T.hat, { sh: 5 }); S('M66 66 C84 54 132 54 150 66 C132 74 84 74 66 66 Z', T.hat, { sh: 4, inner: '<path d="M88 60 C100 56 118 56 128 60" stroke="#d8382e" stroke-width="5" fill="none"/>' });
    });
  });

// 2 · tireur — Cerf-volant : il pique du ciel et lâche des rafales
Mo('epouvantails', 2, 'Cerf-volant', { atk: 'cast', fx: WIND, colors: { paper: '#e85a3a', paper2: TEAL, wood: WOOD, bow: GLOW }, grp: { tail: 'back', body: 'torso' }, piv: { back: [98, 186], torso: [108, 110] } },
  ({ S, raw, T, G, L, eye }) => {
    G('tail', () => { L([[[[98, 184], [66, 198], [86, 224]], 4, 3]], 'wood', { N: 18 }); S('M70 196 L58 186 L62 204 Z M70 196 L82 190 L78 208 Z', T.bow, { sh: 2 }); S('M82 216 L70 208 L72 226 Z M82 216 L94 212 L90 228 Z', T.paper2, { sh: 2 }); });
    G('body', () => {
      S('M122 30 L172 100 L98 188 L48 116 Z', T.paper, { sh: 10, hl: 7,
        inner: '<path d="M122 30 L172 100 L110 108 Z" fill="#2f8f8a"/><path d="M48 116 L110 108 L98 188 Z" fill="#2f8f8a"/><path d="M122 30 L98 188 M48 116 L172 100" stroke="#7a5230" stroke-width="4"/><path d="M106 140 L114 150 L121 141 L128 148 L135 138 L142 144" stroke="#2a1c14" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' });
      eye(98, 104, 11, 10, { iris: GLOW, pupilK: 0.5, lid: 0.44, tilt: 1 }); eye(136, 98, 10, 10, { iris: GLOW, pupilK: 0.5, lid: 0.44, tilt: -1 });
    });
  });

// 3 · sorts — Carillon : son tintement redonne courage aux épouvantails
Mo('epouvantails', 3, 'Carillon', { atk: 'cast', heal: true, fx: WIND, colors: { roof: TEAL, tube: metal('#b8c4d0'), wood: WOOD, paper: '#f4efe2' }, grp: { tubes: 'back', strip: 'back', body: 'torso' }, piv: { back: [106, 112], torso: [106, 90] } },
  ({ S, raw, T, G, L, bar, disc }) => {
    G('tubes', () => { for (const [x, l] of [[76, 158], [92, 178], [120, 184], [136, 162]]) { raw(`<path d="M${x} 108 L${x} 120" stroke="#2a1c14" stroke-width="1.6"/>`); S(bar([x, 118], [x, l], 10), T.tube, { sh: 3, hl: 2 }); } });
    G('strip', () => { raw('<path d="M106 108 L106 150" stroke="#2a1c14" stroke-width="1.6"/>'); S(disc(106, 154, 9), T.wood, { sh: 3 }); S('M98 164 L114 164 L118 208 L108 200 L96 212 Z', T.paper, { sh: 3, inner: '<path d="M106 172 L107 196" stroke="#d8382e" stroke-width="3" stroke-linecap="round"/>' }); });
    G('body', () => {
      raw('<path d="M106 46 C106 30 120 30 120 40" stroke="#7a5230" stroke-width="4" fill="none" stroke-linecap="round"/>'); S('M98 58 C98 46 114 46 114 58 Z', T.wood, { sh: 2 });
      S('M54 92 C70 58 142 58 158 92 C150 100 142 96 138 112 L74 112 C70 96 62 100 54 92 Z', T.roof, { sh: 9, hl: 6,
        inner: '<path d="M70 96 L142 96 L138 114 L74 114 Z" fill="#12222a"/>' + '<path d="M82 100 L98 104 L84 110 Z M130 100 L114 104 L128 110 Z" fill="#ffe14a"/><path d="M66 84 C84 70 128 70 146 84" stroke="#dffff0" stroke-width="4" fill="none" opacity="0.5" stroke-linecap="round"/>' });
    });
  });

// 4 · élite — Faucheur de paille : une botte de foin encapuchonnée, la faux levée
Mo('epouvantails', 4, 'Faucheur de paille', { scale: 1.18, atk: 'slash', wind: -44, hit: 40, colors: { straw: STRAW, jute: '#8a7250', wood: WOOD, steel: metal('#b9c2d0') }, swing: ['scythe'], grp: { body: 'torso' }, piv: { swing: [90, 132], head: [108, 118], torso: [106, 210] } },
  ({ S, raw, T, G, L, limb, bar, disc }) => {
    G('body', () => S('M60 170 C56 132 76 110 104 110 C132 110 150 132 148 168 L156 224 L140 212 L132 228 L120 214 L108 228 L96 214 L84 228 L76 212 L58 224 Z', T.straw, { sh: 11, hl: 7,
      inner: hay('M76 140 L72 200 M92 132 L90 210 M108 130 L108 214 M124 132 L128 210 M140 142 L144 200') + '<path d="M62 170 C90 180 124 180 148 168 L149 178 C124 190 90 190 62 180 Z" fill="#7a5230"/>' }));
    // la faux et le bras qui la tient partent de sous la capuche
    G('scythe', () => { S(bar([150, 224], [168, 46], 6), T.wood, { sh: 2 }); S(limb([[166, 50], [204, 52], [216, 98]], 16, 2, 18), T.steel, { sh: 3, hl: 3 }); L([[[[94, 118], [124, 156], [156, 146]], 18, 16]], 'straw', { inner: hay('M110 140 L140 150') }); S(disc(158, 146, 10), T.straw, { sh: 3 }); });
    G('head', () => {
      S('M72 102 C66 70 86 52 108 52 C132 52 150 70 144 102 C140 120 126 128 108 128 C90 128 76 120 72 102 Z', T.jute, { sh: 9, hl: 6,
        inner: '<path d="M90 98 C88 80 100 70 114 70 C128 70 138 80 136 98 C134 110 124 116 112 116 C100 116 92 110 90 98 Z" fill="#1c140e"/><path d="M98 90 L112 96 L100 102 Z M134 90 L120 96 L132 102 Z" fill="#ffe14a"/><path d="M98 90 L112 96 L100 102 Z M134 90 L120 96 L132 102 Z" fill="#ffe14a" opacity="0.6" filter="url(#g2)"/>' });
      S('M104 54 L96 36 L110 46 L116 30 L122 48 L134 40 L128 58 Z', T.straw, { sh: 3 });
    });
  });

// 5 · boss — Grand Moulin : il s'est arraché à sa colline, ses ailes fauchent tout
Mo('epouvantails', 5, 'Grand Moulin', { scale: 1.34, atk: 'smash', wind: -70, hit: 110, colors: { stone: '#c8b89a', roof: TEAL, wood: WOOD, sail: '#f4efe2' }, swing: ['sails'], grp: { feet: 'legs', body: 'torso' }, piv: { swing: [106, 112], torso: [106, 214] } },
  ({ S, raw, T, G, teeth, eye, bar, ell, disc, poly }) => {
    const R = (x, y, a) => { const c = Math.cos(a * Math.PI / 180), s = Math.sin(a * Math.PI / 180); return [106 + x * c - y * s, 112 + x * s + y * c]; };
    G('feet', () => { S(ell(80, 221, 20, 8), T.stone, { sh: 3 }); S(ell(132, 221, 20, 8), T.stone, { sh: 3 }); });
    G('body', () => {
      S('M70 112 C72 96 140 96 142 112 L156 216 L56 216 Z', T.stone, { sh: 11, hl: 7,
        inner: '<g stroke="#8a7a60" stroke-width="2.2" opacity="0.6" fill="none"><path d="M68 134 L144 134 M64 160 L148 160 M60 188 L152 188 M92 134 L90 160 M122 134 L124 160 M106 160 L106 188"/></g><path d="M90 216 L90 190 C90 174 122 174 122 190 L122 216 Z" fill="#1c140e"/>' });
      teeth([92, 190], [120, 190], 4, 9, 1, '#e8dcc0');
      S('M62 114 C74 72 138 72 150 114 Z', T.roof, { sh: 8, hl: 5, inner: '<path d="M74 104 C90 86 122 86 138 104" stroke="#dffff0" stroke-width="4" fill="none" opacity="0.4" stroke-linecap="round"/>' });
    });
    G('sails', () => {
      for (const a of [45, 135, 225, 315]) {
        S(poly([R(14, -4, a), R(88, -4, a), R(88, -28, a), R(14, -28, a)]), T.sail, { sh: 4, inner: `<g stroke="#7a5230" stroke-width="2" opacity="0.7">${[32, 50, 68].map((x) => `<path d="M${R(x, -4, a).map((v) => v.toFixed(1)).join(' ')} L${R(x, -28, a).map((v) => v.toFixed(1)).join(' ')}"/>`).join('')}<path d="M${R(14, -16, a).map((v) => v.toFixed(1)).join(' ')} L${R(88, -16, a).map((v) => v.toFixed(1)).join(' ')}"/></g>` });
        S(bar(R(0, 0, a), R(92, 0, a), 6), T.wood, { sh: 2 });
      }
      // le moyeu est son œil unique : rien ne passe jamais devant
      S(disc(106, 112, 19), T.wood, { sh: 4 }); eye(106, 112, 13, 13, { iris: '#ffe14a', pupil: 'slit', lid: 0.36, tilt: 0.6 });
    });
  });
