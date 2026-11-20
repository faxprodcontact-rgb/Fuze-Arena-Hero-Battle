// LES CUIRASSÉS (terre) — les bêtes à carapace : plaques, écailles, cornes, pierre et poussière.
// Gueule ouverte découpée dans la silhouette, membres attachés sous le corps (voir LISEZMOI, « Les monstres »).
// Niveau de la famille de référence (m-glaces.cjs) : plaques qui se recouvrent, bandes articulées, écailles en pomme de pin,
// cornes annelées, becs, pattes articulées, arcade dure au-dessus de l'œil. Chaque bête a son plan de corps.
const { Mo, metal } = require('./mon6.cjs');
const IVORY = '#f0e4c8', MAW = '#2a1016', GEM = '#8fe08a';
const bands = (list, c = '#5a4630', w = 2.6) => `<g stroke="${c}" stroke-width="${w}" fill="none" opacity="0.65" stroke-linecap="round">${list.map((d) => `<path d="${d}"/>`).join('')}</g>`;
const r1 = (v) => Math.round(v * 10) / 10;
/** Écailles en pomme de pin sur une zone : rangées décalées, celles du haut recouvrent celles du bas. À mettre dans « inner ». */
const pine = (x0, y0, x1, y1, s, fill, line) => {
  let g = '';
  for (let r = Math.ceil((y1 - y0) / (s * 0.62)); r >= 0; r--) { const y = r1(y0 + r * s * 0.62);
    for (let x = x0 - s + (r % 2 ? s / 2 : 0); x < x1; x += s) g += `<path d="M${r1(x)} ${y} C${r1(x + s * 0.08)} ${r1(y + s * 0.55)} ${r1(x + s * 0.34)} ${r1(y + s * 0.86)} ${r1(x + s / 2)} ${r1(y + s)} C${r1(x + s * 0.66)} ${r1(y + s * 0.86)} ${r1(x + s * 0.92)} ${r1(y + s * 0.55)} ${r1(x + s)} ${y} Z"/>`; }
  return `<g fill="${fill}" stroke="${line}" stroke-width="1.5" stroke-linejoin="round">${g}</g>`;
};
/** Écussons en pyramide (dos des cuirassés) : une face éclairée, une face dans l'ombre. */
const studs = (list, light, dark) => list.map(([x, y, s]) => `<path d="M${x - s} ${r1(y + s * 0.7)} L${x + 2} ${y - s} L${x + s} ${r1(y + s * 0.7)} Z" fill="${light}"/><path d="M${x - s} ${r1(y + s * 0.7)} L${x + 2} ${y - s} L${x + 2} ${r1(y + s * 0.7)} Z" fill="${dark}" opacity="0.5"/>`).join('');
const seg = (a, b, bend = 0) => [a, [(a[0] + b[0]) / 2 - (b[1] - a[1]) * bend, (a[1] + b[1]) / 2 + (b[0] - a[0]) * bend], b];

// 0 · rapide — Tatou : bouclier d'épaules, trois bandes articulées, bouclier de croupe ; il fonce tête basse, griffes dehors
Mo('cuirasses', 0, 'Tatou', { scale: 0.94, atk: 'slash', wind: -12, hit: 18, colors: { shell: '#b89a70', skin: '#d8b8a0', dark: '#8a6a4a' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', shell: 'torso' }, piv: { swing: [126, 182], back: [44, 190], torso: [90, 200] } },
  ({ S, raw, T, G, L, beast, eye, brow, spots, under }) => {
    const legs = beast({ front: 118, hind: 60, top: 200, w: 14, t: 'skin', dark: 'dark', claws: true, gap: 10 });
    G('tail', () => L([[[[46, 190], [18, 196], [4, 222]], 15, 3]], 'shell', { N: 18, inner: bands(['M38 188 l-3 13', 'M29 192 l-4 12', 'M21 198 l-5 10', 'M14 206 l-5 8']) }));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    // la tête sort de sous le bord de la carapace : oreilles en cornet, plaque d'armure sur le front, long museau
    G('head', () => {
      S('M124 166 C112 142 118 120 132 108 C144 124 148 148 140 166 Z', T.skin, { sh: 3, inner: '<path d="M128 158 C122 142 124 128 132 118 C138 132 140 148 136 160 Z" fill="#a8785e"/>' }); S('M144 164 C142 138 152 122 166 114 C172 132 168 152 156 166 Z', T.dark, { sh: 3 });
      S('M116 186 C116 166 134 156 152 160 C172 164 192 178 203 190 C205 196 201 201 195 201 C185 201 176 203 166 204 C146 208 128 204 120 196 C117 192 116 190 116 186 Z', T.skin, { sh: 7, hl: 5,
        inner: '<path d="M124 164 C142 154 166 162 182 178 C164 184 138 180 124 164 Z" fill="#b89a70"/>' + bands(['M136 162 l4 14', 'M150 162 l4 16', 'M164 168 l2 12', 'M130 172 C146 176 164 178 178 178'], '#6e5234', 1.8)
          + '<ellipse cx="198" cy="191" rx="3.4" ry="2.6" fill="#3a2416"/><path d="M197 199 C189 198 181 200 173 204" stroke="#3a2416" stroke-width="2.4" fill="none" stroke-linecap="round"/>' + under('M130 202 C150 210 176 206 196 200 L198 214 L126 214 Z', '#f0dcc8', 0.7) });
      eye(156, 184, 7.5, 6.5, { iris: '#ffb020', pupilK: 0.5, lid: 0.46, tilt: 1 }); brow(156, 176, 20, 1, '#3a2416', 4.5);
    });
    G('shell', () => S('M36 198 C30 158 58 128 92 128 C124 128 148 154 146 196 L138 205 L128 198 L116 206 L104 199 L92 206 L80 199 L68 206 L56 199 L44 205 Z', T.shell, { sh: 10, hl: 7,
      inner: '<path d="M30 186 C70 176 116 176 150 186 L150 210 L30 210 Z" fill="#7a5c3c" opacity="0.5"/>'
        // les trois bandes mobiles, entre les deux boucliers
        + '<path d="M70 132 C60 156 60 184 66 206 L112 206 C116 184 116 156 108 130 Z" fill="#a08460" opacity="0.7"/>' + bands(['M70 132 C60 156 60 184 66 206', 'M83 129 C76 156 76 184 81 206', 'M96 128 C92 156 92 184 96 206', 'M108 130 C116 156 116 184 112 206'], '#4a3824', 3)
        + spots([[46, 164, 3.4], [56, 150, 3.4], [50, 180, 3], [62, 170, 2.6], [42, 190, 2.6], [124, 150, 3.4], [134, 166, 3.4], [126, 178, 3], [138, 184, 2.6], [120, 164, 2.6]], '#7a5c3c', 0.7)
        + spots([[74, 150, 1.8], [72, 170, 1.8], [74, 190, 1.8], [88, 146, 1.8], [86, 168, 1.8], [88, 190, 1.8], [102, 146, 1.8], [104, 168, 1.8], [104, 190, 1.8]], '#4a3824', 0.6)
        + '<path d="M50 152 C58 138 72 132 86 132" stroke="#f4e4c4" stroke-width="5" fill="none" opacity="0.5" stroke-linecap="round"/>' }));
  });

// 1 · costaud — Scarabée-rhinocéros : élytres laqués, une corne de tête fourchue qui remonte vers la corne du thorax, six pattes à éperons
Mo('cuirasses', 1, 'Scarabée-rhinocéros', { scale: 1.1, atk: 'smash', wind: -24, hit: 30, colors: { shell: metal('#7a3a20'), pron: metal('#3e221a'), dark: '#2a1814', leg: '#3a241c' }, swing: ['head'], grp: { farLegs: 'legs', legs: 'legs', shell: 'torso' }, piv: { swing: [140, 176], torso: [84, 200] } },
  ({ S, raw, T, G, eye, brow, limb, disc, stripes }) => {
    // patte d'insecte : cuisse épaisse, jambe à éperon, pied crochu posé au sol
    const bleg = (root, knee, foot, w, t, far) => {
      const dx = foot[0] - knee[0], dy = foot[1] - knee[1], n = Math.hypot(dx, dy), mx = knee[0] + dx * 0.55, my = knee[1] + dy * 0.55, px = -dy / n, py = dx / n, k = dx > 0 ? -1 : 1;
      S(`M${r1(mx - dx / n * 5)} ${r1(my - dy / n * 5)} L${r1(mx + px * 9 * k + dx / n * 3)} ${r1(my + py * 9 * k + dy / n * 3)} L${r1(mx + dx / n * 6)} ${r1(my + dy / n * 6)} Z`, t, { sh: 1, far });
      S(limb(seg(root, knee, 0.08), w, w * 0.84, 12), t, { sh: 3, far }); S(limb(seg(knee, foot, -0.04), w * 0.8, w * 0.5, 14), t, { sh: 3, far });
      S(limb([[foot[0], foot[1] - 2], [foot[0] + 8, foot[1] + 1], [foot[0] + 16, foot[1] - 3]], w * 0.5, 2, 10), t, { sh: 2, far }); S(disc(knee[0], knee[1], w * 0.56), t, { sh: 2, far });
    };
    G('farLegs', () => { bleg([60, 182], [36, 190], [30, 226], 9, T.dark, true); bleg([96, 186], [104, 200], [92, 226], 9, T.dark, true); bleg([134, 184], [158, 196], [162, 226], 9, T.dark, true); });
    G('legs', () => { bleg([54, 188], [22, 198], [10, 226], 11, T.leg); bleg([86, 192], [80, 208], [66, 226], 11, T.leg); bleg([124, 192], [140, 206], [142, 226], 11, T.leg); });
    // la tête et sa grande corne partent de sous le thorax
    G('head', () => {
      S(limb([[172, 186], [184, 196], [188, 208]], 4.5, 3, 10), T.dark, { sh: 2 });
      S('M196 112 L182 84 L202 96 L212 72 L218 110 Z', T.pron, { sh: 4, hl: 3 });
      S(limb([[158, 174], [206, 164], [206, 102]], 22, 10, 20), T.pron, { sh: 5, hl: 4, inner: stripes(['M190 160 l12 4', 'M198 144 l12 0', 'M200 126 l11 -2'], '#120a08', 2, 0.5) });
      S('M136 178 C136 160 148 152 162 154 C176 156 184 166 182 180 C180 192 168 199 154 197 C142 195 136 188 136 178 Z', T.dark, { sh: 6, hl: 4, inner: '<path d="M164 190 l4 7 l5 -7 l4 6" stroke="#6a4a3a" stroke-width="2.4" fill="none" stroke-linejoin="round" stroke-linecap="round"/>' });
      eye(164, 172, 7, 6.5, { iris: '#ffb020', pupilK: 0.5, lid: 0.46, tilt: 1 }); brow(164, 164, 18, 1, '#120a08', 4.5);
    });
    G('shell', () => {
      // la corne du thorax pointe vers l'avant, au-dessus de la tête
      S(limb([[132, 138], [164, 116], [190, 128]], 18, 3, 16), T.pron, { sh: 4, hl: 3 });
      S('M24 186 C20 148 46 120 82 118 C104 118 122 130 128 150 C132 168 130 184 122 197 C98 205 54 203 24 186 Z', T.shell, { sh: 11, hl: 8,
        inner: '<path d="M22 186 C54 204 100 206 126 196 L128 210 L20 210 Z" fill="#2a1814" opacity="0.55"/>' + stripes(['M52 132 C40 154 40 178 48 196', 'M66 124 C56 150 58 180 66 200', 'M98 122 C104 148 106 176 102 200', 'M112 130 C120 150 122 174 118 196'], '#3a1c10', 1.8, 0.45)
          + '<path d="M82 118 C74 146 76 178 86 202" stroke="#1c0e08" stroke-width="3.4" fill="none"/><path d="M40 156 C46 138 60 128 76 126" stroke="#ffd9a0" stroke-width="6" fill="none" opacity="0.55" stroke-linecap="round"/><path d="M96 130 C106 134 114 142 118 152" stroke="#ffd9a0" stroke-width="4" fill="none" opacity="0.4" stroke-linecap="round"/>' });
      // le thorax : une plaque bombée qui recouvre le début des élytres et de la tête
      S('M108 134 C130 122 152 134 158 156 C160 172 152 186 138 193 C128 196 120 194 114 188 C122 170 120 150 108 134 Z', T.pron, { sh: 7, hl: 6, inner: '<path d="M126 134 C140 136 150 146 152 160" stroke="#ffd9a0" stroke-width="4" fill="none" opacity="0.4" stroke-linecap="round"/><path d="M116 188 C124 170 122 150 110 134" stroke="#120a08" stroke-width="2.4" fill="none" opacity="0.6"/>' });
    });
  });

// 2 · tireur — Pangolin : debout, appuyé sur sa queue, couvert d'écailles en pomme de pin ; il en arrache une et la lance comme une lame
Mo('cuirasses', 2, 'Pangolin lanceur', { atk: 'shoot', colors: { scale: '#a87a4a', skin: '#e0c0a0', dark: '#7a5632' }, swing: ['arm'], far: ['armF'], grp: { tail: 'back', farLeg: 'legs', leg: 'legs', body: 'torso' }, piv: { swing: [98, 142], far: [122, 150], head: [116, 124], back: [80, 190], torso: [100, 206] } },
  ({ S, raw, T, G, L, neck, eye, brow, ell, limb, under }) => {
    const SC = (x0, y0, x1, y1, s = 16) => pine(x0, y0, x1, y1, s, '#b88a56', '#5a3e22');
    const claws = (x, y, a, far) => `<g transform="translate(${x} ${y}) rotate(${a})" fill="${IVORY}" stroke="#3a2416" stroke-width="1.2" stroke-linejoin="round" opacity="${far ? 0.75 : 1}"><path d="M-7 1 L-6 -11 L-2 1 Z M-2 1 L0 -13 L3 1 Z M3 1 L6 -11 L8 1 Z"/></g>`;
    G('tail', () => {
      // le bord de la queue est hérissé de pointes d'écailles
      S('M84 174 L70 180 L62 172 L54 184 L42 180 L36 194 L22 190 L18 204 L4 196 L6 180 L-4 172 L8 166 L4 154 L16 156 L80 200 Z', T.dark, { sh: 3 });
      S(limb([[86, 192], [26, 216], [8, 160]], 36, 8, 20), T.scale, { sh: 6, inner: SC(-6, 150, 100, 226, 15) });
    });
    G('farLeg', () => { L([[[[110, 196], [122, 212], [116, 222]], 15, 12]], 'dark', { far: true }); S(ell(122, 224, 13, 5), T.dark, { sh: 2, far: true }); });
    G('leg', () => { L([[[[90, 198], [82, 212], [88, 222]], 17, 13]], 'scale', { inner: SC(70, 192, 104, 226, 12) }); S(ell(94, 224, 14, 5), T.skin, { sh: 2 }); raw(claws(104, 226, 100)); });
    G('armF', () => { L([[[[122, 150], [142, 164], [156, 154]], 11, 8]], 'dark', { far: true }); raw(claws(160, 150, 60, true)); });
    // le bras levé tient une écaille tranchante, prêt à la lancer ; il part de sous l'épaule
    G('arm', () => {
      S('M64 106 C44 92 40 64 56 40 C76 58 82 86 72 108 Z', T.scale, { sh: 3, hl: 3, inner: '<path d="M62 100 L57 52" stroke="#5a3e22" stroke-width="2" opacity="0.6"/><path d="M52 56 C46 70 48 88 58 100" stroke="#f4e0b8" stroke-width="2.6" fill="none" opacity="0.8" stroke-linecap="round"/>' });
      L([[[[98, 142], [72, 134], [66, 106]], 14, 11]], 'scale', { inner: SC(56, 100, 106, 150, 12) }); raw(claws(62, 100, -30));
    });
    G('body', () => {
      // dos hérissé (les pointes des écailles), ventre nu et pâle
      S('M102 120 C122 120 136 138 134 166 C132 192 120 208 102 208 L86 206 L74 198 L78 190 L66 182 L72 174 L62 164 L70 156 L64 146 L74 140 L72 130 L84 126 L88 118 Z', T.scale, { sh: 10, hl: 6,
        inner: SC(56, 112, 140, 210) + under('M112 134 C128 140 134 158 132 174 C130 192 120 204 108 206 C102 186 104 156 112 134 Z', '#e8cca8', 1) });
      neck([104, 142], [108, 132], [114, 124], 40, 36, 'scale', { inner: SC(80, 112, 130, 150, 13) + under('M118 118 C128 124 132 136 130 150 L140 150 L140 116 Z', '#e8cca8', 1) });
    });
    G('head', () => {
      S('M104 104 C98 96 100 86 108 84 C114 88 116 96 114 104 Z', T.dark, { sh: 2 });
      S('M98 128 C94 108 108 92 126 92 C146 92 168 106 190 122 C194 126 193 131 188 132 C170 137 148 141 128 141 C112 141 100 137 98 128 Z', T.skin, { sh: 7, hl: 5,
        inner: '<clipPath id="cuirPangoCap"><path d="M92 128 C92 106 108 90 126 90 C142 90 158 98 170 110 C150 112 126 118 104 136 Z"/></clipPath><g clip-path="url(#cuirPangoCap)">' + SC(88, 86, 176, 140, 13) + '</g>'
          + '<ellipse cx="188" cy="125" rx="2.6" ry="2.2" fill="#3a2416"/><path d="M186 132 C176 133 166 135 156 138" stroke="#3a2416" stroke-width="2" fill="none" stroke-linecap="round"/>' });
      eye(146, 120, 7, 6, { iris: '#ffb020', pupilK: 0.5, lid: 0.46, tilt: 1 }); brow(146, 112, 19, 1, '#3a2416', 4.5);
    });
  });

// 3 · sorts — Escargot de pierre : sa coquille est un rocher en spirale, couvert de mousse et de cristaux qui soignent
Mo('cuirasses', 3, 'Escargot de pierre', { atk: 'cast', heal: true, fx: GEM, colors: { rock: '#8a8478', skin: '#b8ac86', dark: '#8a7e5c', moss: '#6aa84a', gem: '#8fe08a' }, grp: { foot: 'legs', shell: 'torso' }, piv: { head: [146, 190], torso: [92, 200] }, shine: [[80, 84, 10, GEM]] },
  ({ S, raw, T, G, L, halo, eye, spots, stripes, under }) => {
    halo(84, 86, 20, GEM, 0.8);
    // le pied : une semelle large, ourlée, qui dépasse derrière la coquille
    G('foot', () => S('M18 224 C22 214 34 208 48 210 C60 204 90 202 130 202 C152 202 172 210 188 224 C160 230 60 230 18 224 Z', T.skin, { sh: 5, hl: 4,
      inner: bands(['M30 218 q6 5 12 0', 'M52 218 q6 5 12 0', 'M76 219 q6 5 12 0', 'M100 219 q6 5 12 0', 'M124 219 q6 5 12 0', 'M150 218 q6 5 12 0'], '#6e6444', 2) }));
    // le cou, les tiges des yeux et les deux petites cornes partent de sous la coquille
    G('head', () => {
      L([[[[156, 150], [150, 124], [158, 102]], 7, 5], [[[172, 150], [184, 130], [198, 118]], 7, 5]], 'skin');
      L([[[[180, 172], [194, 174], [200, 184]], 6, 3.5], [[[176, 180], [188, 186], [190, 196]], 5.5, 3.5]], 'dark');
      S('M124 212 C124 180 138 150 160 144 C176 140 190 152 188 168 C186 184 176 192 176 206 C176 214 180 220 188 224 L124 224 Z', T.skin, { sh: 7, hl: 5,
        inner: under('M150 224 C150 200 158 180 172 166 L196 170 L196 226 Z', '#e0d6b0', 0.6) + spots([[140, 180, 3], [148, 164, 2.4], [136, 198, 2.6], [156, 152, 2]], '#8a7e5c', 0.6)
          + '<path d="M168 186 C174 184 180 184 184 186" stroke="#4a4028" stroke-width="2.4" fill="none" stroke-linecap="round"/>' });
      eye(158, 98, 8.5, 8, { iris: '#3a5a2a', pupilK: 0.55, lid: 0.4, tilt: 0.5 }); eye(200, 114, 7.5, 7, { iris: '#3a5a2a', pupilK: 0.55, lid: 0.4, tilt: -0.5 });
    });
    G('shell', () => {
      // les cristaux poussent au sommet de la coquille
      S('M62 112 L56 78 L66 66 L78 80 L80 110 Z', T.gem, { sh: 3, hl: 4, inner: '<path d="M66 66 L68 112 L80 110 L78 80 Z" fill="#3f9a5a" opacity="0.5"/>' });
      S('M78 108 L80 58 L92 42 L104 60 L102 106 Z', T.gem, { sh: 3, hl: 4, inner: '<path d="M92 42 L92 108 L102 106 L104 60 Z" fill="#3f9a5a" opacity="0.5"/><path d="M84 62 L86 100" stroke="#eafff0" stroke-width="2.4" opacity="0.7" stroke-linecap="round"/>' });
      S('M100 106 L106 78 L116 70 L122 84 L118 108 Z', T.gem, { sh: 3, hl: 4, inner: '<path d="M116 70 L112 108 L118 108 L122 84 Z" fill="#3f9a5a" opacity="0.5"/>' });
      S('M30 182 C24 136 54 98 96 98 C134 98 160 130 156 174 C154 198 138 212 112 214 C78 218 36 212 30 182 Z', T.rock, { sh: 12, hl: 8,
        inner: stripes(['M40 150 l-12 -4', 'M46 130 l-12 -8', 'M62 114 l-8 -12', 'M130 112 l8 -12', 'M146 132 l12 -6', 'M150 160 l12 0', 'M38 180 l-12 4', 'M50 200 l-8 10', 'M134 198 l10 10'], '#5a564c', 2.2, 0.5)
          // la spirale : un sillon sombre doublé d'un filet de lumière
          + '<path d="M100 202 C62 204 44 174 52 146 C60 120 92 110 114 124 C134 138 136 168 120 182 C106 194 84 188 80 170 C78 156 90 146 102 150 C110 154 112 164 104 168" stroke="#4a463c" stroke-width="6" fill="none" stroke-linecap="round"/>'
          + '<path d="M98 196 C68 196 52 172 58 150 C64 128 90 118 110 130" stroke="#c8c2b4" stroke-width="2.4" fill="none" stroke-linecap="round" opacity="0.6"/>'
          + '<path d="M126 142 l10 8 l-4 8 M70 190 l-6 10" stroke="#3a362e" stroke-width="2" fill="none" stroke-linejoin="round" opacity="0.6"/>'
          + '<g fill="#6aa84a" opacity="0.9" filter="url(#g2)"><path d="M40 132 C50 118 68 110 82 112 C74 124 56 134 40 132 Z"/><path d="M118 104 C130 106 142 116 148 128 C136 128 124 118 118 104 Z"/><ellipse cx="42" cy="176" rx="9" ry="6"/><ellipse cx="136" cy="190" rx="10" ry="5"/></g>'
          // la lèvre de la coquille, du côté de la tête
          + '<path d="M128 214 C146 204 156 186 156 164" stroke="#c8c2b4" stroke-width="5" fill="none" opacity="0.5" stroke-linecap="round"/>' });
    });
  });

// 4 · élite — Tricératops : collerette d'os bordée de pointes, deux grandes cornes braquées vers l'avant, un bec ; il charge tête baissée
Mo('cuirasses', 4, 'Tricératops', { scale: 1.2, atk: 'smash', wind: -18, hit: 26, colors: { skin: '#9a8a5a', dark: '#6e6240', frill: '#c8884a', horn: IVORY }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [116, 168], back: [36, 172], torso: [84, 196] } },
  ({ S, raw, T, G, L, beast, neck, eye, brow, limb, stripes, spots, under }) => {
    const legs = beast({ front: 104, hind: 50, top: 190, w: 23, t: 'skin', dark: 'dark', claws: true });
    const rings = (l) => stripes(l, '#a89468', 2, 0.7);
    G('tail', () => L([[[[40, 174], [12, 184], [2, 210]], 28, 5]], 'skin', { N: 18, inner: stripes(['M34 164 l-4 22', 'M22 172 l-6 20', 'M12 184 l-8 14'], '#6e6240', 4, 0.5) }));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      // garrot haut, croupe ronde, ventre lourd
      S('M24 178 C22 146 46 128 72 128 C92 118 122 126 134 148 C140 162 138 180 130 192 C116 204 96 206 80 206 C50 206 26 200 24 178 Z', T.skin, { sh: 12, hl: 7,
        inner: under('M30 196 C62 212 110 210 136 188 L138 218 L28 218 Z', '#d8cc9a', 0.75) + stripes(['M46 138 C42 150 42 162 46 172', 'M62 130 C58 144 58 158 62 170', 'M80 126 C76 140 76 156 80 168', 'M98 126 C96 138 96 152 100 164'], '#6e6240', 5, 0.5)
          + spots([[40, 182, 3], [56, 186, 2.6], [74, 184, 3], [94, 182, 2.6], [112, 178, 3]], '#6e6240', 0.5) });
      neck([112, 160], [124, 158], [134, 160], 56, 50, 'skin');
    });
    G('head', () => {
      // la collerette, derrière la tête : bord festonné de pointes, deux taches en creux
      S('M112 182 C88 166 76 128 92 100 L88 84 L102 90 L108 72 L120 82 L132 66 L140 82 L154 72 L156 90 C164 108 160 132 150 152 Z', T.frill, { sh: 8, hl: 5,
        inner: '<path d="M96 104 C108 92 132 86 150 94 C140 100 112 106 96 104 Z" fill="#f0c890" opacity="0.6"/><g fill="#7a4a22" opacity="0.65"><path d="M96 122 C104 110 118 108 124 118 C126 134 116 148 104 148 C96 142 94 132 96 122 Z"/><path d="M132 112 C140 104 150 106 152 116 C152 128 146 138 138 138 C132 130 130 120 132 112 Z"/></g>'
          + stripes(['M100 160 C92 144 88 126 94 108', 'M128 150 C128 132 130 112 136 94'], '#7a4a22', 2, 0.5) });
      // corne de joue, cornes du front : elles partent de sous le crâne
      S('M124 186 L118 208 L140 194 Z', T.horn, { sh: 3 });
      S(limb([[160, 134], [188, 104], [218, 100]], 14, 2, 18), T.horn, { sh: 3, far: true });
      S(limb([[144, 138], [168, 102], [212, 112]], 17, 2, 18), T.horn, { sh: 4, hl: 3, inner: rings(['M150 124 l12 8', 'M158 114 l11 9', 'M168 108 l8 10']) });
      raw(`<path d="M202 180 L172 185 L192 197 C185 193 185 187 202 180 Z" fill="${MAW}"/>`);
      S('M114 166 C112 144 128 130 150 132 C170 134 184 144 194 158 C202 164 208 174 208 184 C208 188 207 192 205 195 L199 181 L174 185 L194 198 C186 206 170 206 158 202 C140 202 126 196 118 186 C115 180 114 172 114 166 Z', T.skin, { sh: 10, hl: 6,
        inner: '<path d="M190 152 C202 162 210 176 205 195 L199 181 L186 172 Z" fill="#e0b860"/><path d="M176 186 L194 198 C188 204 180 204 174 202 Z" fill="#e0b860" opacity="0.9"/><ellipse cx="190" cy="168" rx="2.4" ry="1.8" fill="#3a3020"/>'
          + stripes(['M122 160 C120 172 122 182 128 190', 'M134 150 l-4 10'], '#6e6240', 2.6, 0.5) + spots([[136, 176, 2.6], [146, 186, 2.4], [160, 180, 2]], '#6e6240', 0.5) });
      // la corne du nez
      S('M176 158 L190 128 L198 160 Z', T.horn, { sh: 3, hl: 2 });
      eye(152, 158, 8.5, 7.5, { iris: '#ffb020', pupil: 'slit', lid: 0.46, tilt: 1 }); brow(152, 148, 24, 1, '#3a3020', 5.5);
    });
  });

// 5 · boss — Ankylosaure : un char d'assaut vivant, dos de plaques et de piquants, crâne cornu, une massue d'os au bout de la queue
Mo('cuirasses', 5, 'Ankylosaure', { scale: 1.36, atk: 'smash', wind: -50, hit: 60, colors: { skin: '#5e6a6e', dark: '#40494c', plate: '#b8a878', horn: IVORY }, swing: ['tail'], grp: { farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [40, 174], head: [128, 184], torso: [86, 198] } },
  ({ S, raw, T, G, L, beast, neck, eye, brow, teeth, limb, stripes, under }) => {
    const legs = beast({ front: 112, hind: 50, top: 198, w: 21, t: 'skin', dark: 'dark', claws: true, gap: 12 });
    // la queue se dresse au-dessus du dos : anneaux d'os, puis la massue à deux lobes, fendillée
    G('tail', () => {
      S(limb([[42, 176], [-8, 152], [26, 100]], 24, 12, 20), T.skin, { sh: 5, inner: stripes(['M30 162 l-10 14', 'M16 152 l-14 8', 'M8 136 l-14 0', 'M10 120 l-12 -6', 'M18 108 l-10 -10'], '#b8a878', 3.4, 0.7) });
      S('M10 102 C-2 92 -2 72 14 66 C18 52 40 50 48 62 C62 62 70 80 60 94 C52 104 40 102 34 106 C26 110 16 108 10 102 Z', T.plate, { sh: 7, hl: 5,
        inner: '<path d="M28 60 C26 74 30 90 34 104" stroke="#6e6040" stroke-width="2.6" fill="none" opacity="0.7"/><path d="M8 84 l10 2 l4 8 M48 72 l-8 6 l2 8" stroke="#6e6040" stroke-width="1.8" fill="none" stroke-linejoin="round" opacity="0.7"/><path d="M8 78 C12 68 20 64 26 64" stroke="#fff8e0" stroke-width="4" fill="none" opacity="0.6" stroke-linecap="round"/>' });
    });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      // les piquants du dos (rangée du fond), puis le corps large et bas
      S('M34 170 L40 140 L54 156 L62 130 L76 150 L86 124 L98 148 L110 128 L120 152 L132 142 L136 168 Z', T.plate, { sh: 3, far: true });
      S('M20 192 C18 168 36 154 56 152 C80 146 112 148 130 158 C142 166 148 178 146 192 C142 208 114 212 84 212 C52 212 22 208 20 192 Z', T.skin, { sh: 11, hl: 7,
        inner: under('M26 202 C58 216 118 214 146 196 L148 224 L24 224 Z', '#c8c4a8', 0.6) + stripes(['M26 180 C60 170 112 170 144 180'], '#40494c', 2.4, 0.6)
          + studs([[44, 168, 9], [66, 162, 10], [90, 160, 10], [114, 162, 10], [134, 170, 8]], '#d0c090', '#5a4e30')
          // les grands piquants du flanc, tournés vers nous
          + [[36, 192], [58, 196], [82, 198], [106, 197], [128, 192]].map(([x, y]) => `<path d="M${x - 9} ${y - 6} L${x + 9} ${y - 6} L${x - 2} ${y + 13} Z" fill="#e0d0a0"/><path d="M${x - 9} ${y - 6} L${x} ${y - 6} L${x - 2} ${y + 13} Z" fill="#5a4e30" opacity="0.45"/>`).join('') });
      neck([120, 184], [130, 184], [138, 186], 50, 46, 'skin');
    });
    G('head', () => {
      // cornes de l'arrière du crâne et de la joue
      S('M126 168 L112 146 L140 156 Z', T.horn, { sh: 3 }); S('M148 160 L152 138 L166 160 Z', T.horn, { sh: 3, far: true }); S('M126 196 L118 216 L140 204 Z', T.horn, { sh: 3 });
      raw(`<path d="M202 187 L170 191 L193 202 C186 199 186 193 202 187 Z" fill="${MAW}"/>`);
      S('M116 186 C114 166 132 154 152 156 C172 158 190 168 200 180 C202 183 203 185 202 187 L172 191 L197 204 C190 210 176 211 162 210 C146 210 130 206 122 200 C118 196 116 192 116 186 Z', T.skin, { sh: 9, hl: 6,
        inner: '<path d="M120 170 C138 156 164 158 182 172 C164 178 138 180 120 170 Z" fill="#b8a878"/>' + stripes(['M136 160 l2 16', 'M152 158 l2 18', 'M168 164 l0 12'], '#6e6040', 1.8, 0.6)
          + '<path d="M186 172 C194 176 200 182 202 187 L190 188 Z" fill="#d0c090" opacity="0.9"/><ellipse cx="192" cy="178" rx="2.2" ry="1.7" fill="#2a2a24"/>' + under('M130 206 C150 212 178 212 196 204 L198 218 L128 218 Z', '#c8c4a8', 0.6) });
      teeth([198, 188.5], [176, 191], 3, 4.5, 1); teeth([194, 203], [176, 193.5], 3, -4.5, 1);
      eye(156, 184, 8, 6.5, { iris: '#ffb020', pupil: 'slit', lid: 0.48, tilt: 1 }); brow(156, 175, 22, 1, '#2a2a24', 5.5);
    });
  });
