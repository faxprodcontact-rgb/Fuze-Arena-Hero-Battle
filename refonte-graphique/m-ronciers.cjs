// LES RONCIERS (terre) — des bêtes faites de ronces, de mousse, de feuilles et d'écorce : la forêt qui se défend.
// Niveau de la famille de référence (m-glaces.cjs) : cou, dos travaillé, museau d'un seul tenant, matière végétale lisible
// (plaques d'écorce veinées, lianes à épines, feuilles en couches, mousse, baies), yeux de sève qui luisent.
// Un seul contour par créature, gueule ouverte découpée dans la silhouette, membres attachés sous le corps.
const { Mo } = require('./mon6.cjs');
const BARK = '#6a4a30', BARKD = '#46301e', LEAF = '#5fa83a', FALL = '#e08a2a', MOSS = '#7ab84a', THORN = '#3a2618', GLOW = '#b8ff6a', MAW = '#1c120a';
const grain = (list) => `<g stroke="#2e1e12" stroke-width="2.4" fill="none" opacity="0.55" stroke-linecap="round">${list.map((d) => `<path d="${d}"/>`).join('')}</g>`;
const veins = (list, c = '#a85a14') => `<g stroke="${c}" stroke-width="2.2" fill="none" opacity="0.6" stroke-linecap="round">${list.map((d) => `<path d="${d}"/>`).join('')}</g>`;
/** Une ronce : une liane sombre et ses épines, qui alternent d'un côté et de l'autre (à mettre dans « inner »). */
const bramble = (pts, w = 4, c = '#7fae3e') => { let d = `M${pts[0][0]} ${pts[0][1]}`, th = ''; for (let i = 1; i < pts.length; i++) { const [x0, y0] = pts[i - 1], [x1, y1] = pts[i]; d += ` L${x1} ${y1}`; const mx = (x0 + x1) / 2, my = (y0 + y1) / 2, dx = x1 - x0, dy = y1 - y0, l = Math.hypot(dx, dy) || 1, k = i % 2 ? 1 : -1, nx = -dy / l * k, ny = dx / l * k; th += `<path d="M${(mx - dx / l * 3.5).toFixed(1)} ${(my - dy / l * 3.5).toFixed(1)} L${(mx + nx * 9).toFixed(1)} ${(my + ny * 9).toFixed(1)} L${(mx + dx / l * 3.5).toFixed(1)} ${(my + dy / l * 3.5).toFixed(1)} Z"/>`; } return `<g fill="${THORN}" stroke="${THORN}" stroke-width="1.6" stroke-linejoin="round">${th}</g><path d="${d}" stroke="${THORN}" stroke-width="${w + 2.6}" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="${d}" stroke="${c}" stroke-width="${w}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`; };
const berries = (list) => `<g fill="#d8382e" stroke="#5a1410" stroke-width="1">${list.map(([x, y, r = 3.6]) => `<circle cx="${x}" cy="${y}" r="${r}"/>`).join('')}</g><g fill="#fff" opacity="0.7">${list.map(([x, y]) => `<circle cx="${x - 1}" cy="${y - 1.2}" r="1"/>`).join('')}</g>`;
/** Une feuille peinte dans une forme (pour « inner ») : pointe tournée de « a » degrés. */
const leafIn = (x, y, a, len, w, c) => `<g transform="translate(${x} ${y}) rotate(${a})"><path d="M0 0 C${-w} ${-len * 0.3} ${-w * 0.8} ${-len * 0.8} 0 ${-len} C${w * 0.8} ${-len * 0.8} ${w} ${-len * 0.3} 0 0 Z" fill="${c}" stroke="#8a3c0c" stroke-width="1.3"/><path d="M0 -2 L0 ${-len + 4}" stroke="#8a3c0c" stroke-width="1.3" opacity="0.75"/></g>`;
/** Œil de sève : il luit en vert. */
const sap = (h, x, y, rx, ry, o = {}) => { h.halo(x, y, rx + 5, GLOW, 0.6); h.eye(x, y, rx, ry, { sclera: '#f4ffd8', iris: GLOW, pupil: 'slit', lid: 0.44, tilt: 1, ...o }); };
/** Une feuille posée : pointe vers (x, y − len), tournée de « a » degrés. */
const leafAt = (h, x, y, a, len, w, t, far) => h.at(`translate(${x} ${y}) rotate(${a})`, () => h.S(`M0 0 C${-w} ${-len * 0.3} ${-w * 0.8} ${-len * 0.8} 0 ${-len} C${w * 0.8} ${-len * 0.8} ${w} ${-len * 0.3} 0 0 Z`, h.TK(t), { sh: 3, hl: 3, far, inner: `<path d="M0 -2 L0 ${-len + 3}" stroke="#2e5a1e" stroke-width="1.4" opacity="0.6"/>` }));

// 0 · rapide — Renard de feuilles : un pelage de feuilles d'automne, une queue en feuille d'érable, des pattes de brindille
Mo('ronciers', 0, 'Renard de feuilles', { scale: 0.96, atk: 'slash', wind: -14, hit: 20, colors: { leaf: FALL, dark: '#b8601a', bark: BARKD, pale: '#f6e0b0' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [126, 158], back: [56, 174], torso: [90, 196] } },
  (h) => { const { S, raw, T, G, beast, brow, under } = h;
    const legs = beast({ front: 114, hind: 60, top: 190, w: 11, t: 'leaf', dark: 'dark' });
    G('tail', () => S('M60 180 C44 184 26 176 16 160 L30 156 L8 142 L28 136 L8 120 L30 118 L18 96 L40 106 L42 84 L58 106 C68 122 74 150 68 174 Z', T.leaf, { sh: 7, hl: 5,
      inner: veins(['M62 172 C52 148 42 126 36 100', 'M54 152 L28 138', 'M48 134 L28 120', 'M44 118 L38 102']) + '<path d="M18 96 L40 106 L42 84 L52 100 C46 108 34 108 26 104 Z" fill="#f6e0b0"/>' }));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      // les feuilles du dos, couchées vers l'arrière
      S('M60 162 L44 142 L70 152 L62 126 L86 148 L84 122 L104 144 L106 124 L122 148 Z', T.dark, { sh: 4 });
      S('M44 178 C42 162 54 152 72 152 C88 148 102 140 120 142 C132 140 142 136 154 134 L160 172 C150 182 142 192 132 197 C120 204 104 204 88 204 C62 204 46 196 44 178 Z', T.leaf, { sh: 9, hl: 6,
        inner: under('M52 194 C76 208 114 206 138 186 L140 214 L50 214 Z', '#f6e0b0', 0.9) + leafIn(82, 186, -98, 26, 9, '#f0b030') + leafIn(80, 168, -80, 28, 9, '#d8501c') + leafIn(110, 182, -96, 30, 10, '#c8461a') + leafIn(108, 162, -80, 30, 10, '#f0b030') + leafIn(138, 186, -98, 28, 9, '#f0b030') + leafIn(138, 168, -78, 30, 10, '#d8501c') });
    });
    G('head', () => {
      S('M136 130 L126 94 L152 116 Z', T.leaf, { sh: 3, inner: '<path d="M136 122 L132 104 L146 116 Z" fill="#5a2a0c"/>' }); S('M156 120 L164 90 L178 124 Z', T.dark, { sh: 3 });
      S('M128 148 C126 130 140 120 156 120 C170 120 182 128 190 138 C200 144 212 150 214 156 C214 162 208 164 202 164 C190 168 176 174 162 174 C142 174 129 164 128 148 Z', T.leaf, { sh: 9, hl: 6,
        inner: under('M160 160 C176 152 196 152 216 158 L214 172 L156 178 Z', '#f6e0b0', 0.95) + '<path d="M206 152 C211 151 216 155 215 160 C210 162 206 158 206 152 Z" fill="#1c120a"/><path d="M208 166 C198 170 186 172 174 172" stroke="#1c120a" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M197 160 L195 169 L191 162 Z" fill="#fff8e6" stroke="#1c120a" stroke-width="1" stroke-linejoin="round"/>' + veins(['M132 142 L146 146', 'M134 156 L146 156']) });
      sap(h, 164, 142, 9.5, 7.5); brow(164, 131, 24, 1, '#5a2a0c', 5);
    });
  });

// 1 · costaud — Blaireau de mousse : trapu, têtu, un tapis de mousse et de champignons sur le dos, des griffes de terrassier
Mo('ronciers', 1, 'Blaireau de mousse', { scale: 1.1, atk: 'smash', wind: -16, hit: 22, colors: { bark: BARK, dark: BARKD, moss: MOSS, birch: '#e8e0cc', cap: '#d8482e' }, swing: ['head'], grp: { shrooms: 'torso', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [122, 184], torso: [84, 200] } },
  (h) => { const { S, raw, T, G, beast, fringe, neck, brow, eye, ell } = h;
    const legs = beast({ front: 110, hind: 52, top: 198, w: 21, t: 'bark', dark: 'dark', claws: true, gap: 12 });
    // les champignons poussent sur le dos : leurs pieds partent de sous la mousse
    G('shrooms', () => { raw('<path d="M62 150 L60 126 M90 142 L92 114" stroke="#e8e0cc" stroke-width="6" stroke-linecap="round"/>'); S(ell(60, 122, 15, 9), T.cap, { sh: 3, hl: 3, inner: '<g fill="#fff6e0"><circle cx="54" cy="120" r="2.4"/><circle cx="64" cy="117" r="2"/></g>' }); S(ell(92, 110, 13, 8), T.cap, { sh: 3, hl: 3, inner: '<g fill="#fff6e0"><circle cx="88" cy="108" r="2.2"/><circle cx="97" cy="110" r="1.8"/></g>' }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      S('M24 186 C22 158 46 140 78 138 C108 136 132 150 138 174 C140 188 136 198 128 204' + fringe(128, 36, 204, 7, 10) + ' C26 198 24 192 24 186 Z', T.bark, { sh: 11, hl: 6,
        inner: grain(['M40 180 q4 10 0 20', 'M60 184 q4 10 0 18', 'M84 186 q4 10 0 16', 'M108 184 q4 10 0 16']) + '<path d="M22 180 C30 148 62 134 92 136 C118 138 134 152 140 170 C132 164 126 176 116 168 C108 162 102 176 92 168 C84 162 76 176 66 170 C58 164 50 178 42 172 C36 168 28 176 22 180 Z" fill="#7ab84a"/><path d="M36 160 C52 146 78 142 100 144" stroke="#c8f09a" stroke-width="5" fill="none" opacity="0.6" stroke-linecap="round"/><g fill="#4f8a2e" opacity="0.7"><circle cx="48" cy="164" r="3"/><circle cx="76" cy="156" r="3"/><circle cx="106" cy="158" r="3"/><circle cx="124" cy="164" r="2.4"/></g>' });
      neck([114, 176], [130, 182], [146, 186], 50, 42, 'dark');
    });
    G('head', () => {
      S(ell(128, 158, 10, 11), T.dark, { sh: 3, inner: '<ellipse cx="128" cy="158" rx="5" ry="6" fill="#e8e0cc"/>' }); S(ell(154, 152, 8, 9), T.dark, { sh: 3 });
      S('M118 184 C116 164 132 152 150 154 C168 156 188 168 204 184 C208 190 206 198 198 198 C182 206 158 210 140 206 C124 202 118 194 118 184 Z', T.dark, { sh: 9, hl: 6,
        inner: '<path d="M130 156 C148 158 176 170 206 186 L204 196 C176 182 150 174 128 170 Z" fill="#e8e0cc"/><path d="M138 206 C160 210 184 206 202 198 L202 212 L136 214 Z" fill="#e8e0cc" opacity="0.85" filter="url(#g2)"/><path d="M196 182 C201 181 207 185 206 191 C201 193 196 189 196 182 Z" fill="#1c120a"/><path d="M200 199 C190 202 180 202 170 200" stroke="#1c120a" stroke-width="2.2" fill="none" stroke-linecap="round"/>' });
      eye(158, 184, 8, 7, { sclera: '#f4ffd8', iris: GLOW, pupilK: 0.5, lid: 0.5, tilt: 1 }); brow(158, 174, 22, 1, '#1c120a', 5);
    });
  });

// 2 · tireur — Porc-épic d'épines : un roncier sur pattes, il se hérisse et décoche ses épines
Mo('ronciers', 2, 'Porc-épic d\'épines', { atk: 'shoot', colors: { bark: BARK, dark: BARKD, thorn: THORN, quill: '#5e4028' }, grp: { quillsF: 'back', quills: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { back: [96, 196], head: [132, 192], torso: [96, 206] } },
  (h) => { const { S, raw, T, G, beast, eye, brow, saw, arcPts, pt, ell } = h;
    const legs = beast({ front: 126, hind: 70, top: 204, w: 14, t: 'bark', dark: 'dark', claws: true, gap: 10 });
    G('quillsF', () => { const pts = arcPts(92, 190, 68, 72, 174, 354, 12); S(`M${pt(pts[0])}` + saw(pts, 40, [-4, -6]) + ' Z', T.thorn, { sh: 9, hl: 5 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => S('M40 198 C38 172 62 156 92 156 C120 156 142 170 144 192 C144 208 122 216 92 216 C62 216 42 212 40 198 Z', T.bark, { sh: 9, hl: 6 }));
    // la rangée d'épines de devant : plus courte, avec les baies du roncier
    G('quills', () => { const pts = arcPts(88, 196, 50, 46, 178, 338, 9); S(`M${pt(pts[0])}` + saw(pts, 26, [-3, -4]) + ' Z', T.quill, { sh: 7, hl: 5, inner: bramble([[44, 190], [58, 170], [78, 160], [100, 158], [122, 166]], 3.4) + berries([[60, 182], [84, 172], [108, 174], [72, 190]]) }); });
    G('head', () => {
      S(ell(122, 170, 8, 9), T.dark, { sh: 3, inner: '<ellipse cx="122" cy="171" rx="4" ry="5" fill="#8a5a3a"/>' });
      S('M112 192 C110 174 126 164 144 166 C160 168 176 178 192 192 C196 198 194 204 188 204 C172 210 150 212 134 208 C120 204 113 200 112 192 Z', T.dark, { sh: 8, hl: 5,
        inner: '<path d="M150 198 C164 194 180 196 194 200 L192 210 L146 212 Z" fill="#8a5a3a" opacity="0.8" filter="url(#g2)"/><path d="M184 190 C189 189 195 193 194 199 C189 201 184 197 184 190 Z" fill="#1c120a"/><path d="M188 205 C178 208 168 208 158 206" stroke="#1c120a" stroke-width="2.2" fill="none" stroke-linecap="round"/>' });
      raw('<path d="M178 205 L177 212 L173 206 Z" fill="#fff8e6" stroke="#1c120a" stroke-width="1" stroke-linejoin="round"/>');
      eye(150, 186, 8.5, 7.5, { sclera: '#f4ffd8', iris: FALL, pupilK: 0.45, lid: 0.46, tilt: 1 }); brow(150, 176, 22, 1, '#1c120a', 5);
    });
  });

// 3 · sorts — Phalène d'écorce : ses ailes sont deux écorces à ocelles, sa poussière endort
Mo('ronciers', 3, 'Phalène d\'écorce', { atk: 'cast', fx: GLOW, colors: { wing: '#8a6a48', low: '#6a4e34', dark: BARKD, fuzz: '#d8c8a0' }, swing: ['wingN'], far: ['wingF'], grp: { body: 'torso' }, piv: { swing: [98, 130], far: [118, 130], torso: [108, 150] }, shine: [[56, 104, 11, GLOW]], shineGrp: 'swing' },
  (h) => { const { S, raw, T, G, L, halo, eye, tuft } = h;
    const spot = (x, y) => `<circle cx="${x}" cy="${y}" r="16" fill="#2e1e12"/><circle cx="${x}" cy="${y}" r="11" fill="${GLOW}"/><circle cx="${x}" cy="${y}" r="5.5" fill="#1c120a"/><circle cx="${x - 3}" cy="${y - 3}" r="2" fill="#fff"/>`;
    const lichen = (list) => `<g fill="#b8c88a" opacity="0.6">${list.map(([x, y, r]) => `<circle cx="${x}" cy="${y}" r="${r}"/>`).join('')}</g>`;
    halo(56, 104, 18, GLOW, 0.7); halo(162, 104, 16, GLOW, 0.6);
    G('wingF', () => { S('M118 142 C140 150 168 160 178 180 C172 198 152 204 138 196 L134 208 L124 192 C118 176 116 158 118 142 Z', T.low, { sh: 6, far: true });
      S('M116 128 C130 84 170 60 210 76 L200 90 L210 100 L198 110 L204 124 L188 130 L186 144 C164 152 132 148 116 138 Z', T.wing, { sh: 8, far: true, inner: spot(162, 106) + grain(['M124 130 C146 106 174 92 202 86', 'M126 138 C150 132 172 132 188 138']) + lichen([[190, 98, 5], [140, 124, 4]]) }); });
    G('wingN', () => { S('M98 142 C76 150 48 160 38 180 C44 198 64 204 78 196 L82 208 L92 192 C98 176 100 158 98 142 Z', T.low, { sh: 6, inner: grain(['M92 150 C76 160 60 172 50 184']) });
      S('M100 128 C86 84 46 60 6 76 L16 90 L6 100 L18 110 L12 124 L28 130 L30 144 C52 152 84 148 100 138 Z', T.wing, { sh: 9, hl: 6, inner: spot(56, 106) + grain(['M92 130 C70 106 42 92 14 86', 'M90 138 C66 132 44 132 28 138', 'M82 122 C74 104 62 90 48 82']) + lichen([[26, 98, 5], [78, 126, 4], [40, 126, 3]]) }); });
    G('body', () => {
      // antennes en peigne
      L([[[[100, 96], [84, 74], [64, 70]], 4.5, 2.5], [[[116, 96], [132, 74], [152, 70]], 4.5, 2.5]], 'dark');
      raw('<g stroke="#46301e" stroke-width="2.2" stroke-linecap="round"><path d="M94 86 l-6 -9 M86 78 l-3 -10 M77 73 l0 -10 M69 71 l3 -9 M122 86 l6 -9 M130 78 l3 -10 M139 73 l0 -10 M147 71 l-3 -9"/></g>');
      S('M94 138 C92 150 96 180 108 200 C120 180 124 150 122 138 Z', T.fuzz, { sh: 6, hl: 5, inner: grain(['M96 150 L120 150', 'M98 162 L118 162', 'M101 174 L115 174', 'M104 186 L112 186']) });
      tuft(108, 138, 180, 12, 34, 'wing', { n: 5 });
      S('M90 118 C88 100 96 90 108 90 C120 90 128 100 126 118 C126 130 118 138 108 138 C98 138 90 130 90 118 Z', T.fuzz, { sh: 7, hl: 5 });
      eye(100, 110, 7.5, 7.5, { sclera: '#1c120a', iris: GLOW, pupil: 'none', irisK: 0.55, lid: 0.42, tilt: 1, lidC: '#8a7a5a' }); eye(117, 110, 7, 7.5, { sclera: '#1c120a', iris: GLOW, pupil: 'none', irisK: 0.55, lid: 0.42, tilt: -1, lidC: '#8a7a5a' });
    });
  });

// 4 · élite — Mante-brindille : on la prend pour une branche, jusqu'au coup de faux
Mo('ronciers', 4, 'Mante-brindille', { scale: 1.22, atk: 'slash', wind: -44, hit: 40, colors: { twig: '#7a8a3a', dark: '#4e5a22', leaf: LEAF, blade: '#c8d88a' }, swing: ['armN'], far: ['armF'], grp: { farLegs: 'legs', legs: 'legs', abdomen: 'back', body: 'torso' }, piv: { swing: [116, 114], far: [124, 116], head: [122, 86], back: [92, 150], torso: [100, 160] } },
  (h) => { const { S, raw, T, G, L, eye, brow, limb, disc } = h;
    const spikes = (pts) => `<g fill="#4e5a22">${pts.map(([x, y, a]) => `<path d="M-3 0 L0 -7 L3 0 Z" transform="translate(${x} ${y}) rotate(${a})"/>`).join('')}</g>`;
    // patte ravisseuse du fond : tendue vers l'avant, lame vers le bas
    G('armF', () => { S(limb([[176, 128], [198, 132], [208, 158]], 12, 2, 16), T.dark, { sh: 3, far: true }); L([[[[124, 116], [152, 138], [178, 128]], 9, 7]], 'dark', { far: true }); });
    G('farLegs', () => L([[[[84, 160], [56, 176], [44, 226]], 6, 4], [[[104, 158], [130, 180], [138, 226]], 6, 4]], 'dark', { far: true, N: 16 }));
    // l'abdomen : une feuille repliée, nervures visibles
    G('abdomen', () => { leafAt(h, 60, 158, -70, 40, 13, 'leaf'); S(limb([[98, 150], [58, 172], [20, 150]], 24, 6, 18), T.twig, { sh: 6, inner: '<path d="M90 156 C70 168 46 164 26 152" stroke="#4e5a22" stroke-width="2" fill="none" opacity="0.7"/><path d="M82 158 l-6 10 M66 164 l-6 10 M50 162 l-6 8 M36 156 l-4 7" stroke="#4e5a22" stroke-width="2.2" stroke-linecap="round" opacity="0.7"/>' }); leafAt(h, 98, 148, -68, 56, 12, 'leaf'); });
    G('legs', () => { L([[[[90, 162], [66, 184], [60, 226]], 7, 4], [[[106, 160], [118, 188], [122, 226]], 7, 4]], 'twig', { N: 16 }); S(disc(68, 184, 5.5), T.twig, { sh: 2 }); S(disc(118, 188, 5.5), T.twig, { sh: 2 }); });
    // la patte ravisseuse de devant : levée haut, à droite de la tête ; elle part de sous le thorax
    G('armN', () => { S(limb([[166, 72], [190, 64], [202, 100]], 14, 2, 16), T.blade, { sh: 3, hl: 3, inner: spikes([[176, 74, 200], [186, 76, 190], [194, 84, 170]]) }); L([[[[116, 114], [146, 106], [168, 72]], 10, 8]], 'twig'); S(disc(168, 72, 6.5), T.twig, { sh: 2 }); });
    G('body', () => { leafAt(h, 102, 142, -150, 22, 8, 'leaf'); S(limb([[98, 162], [100, 132], [120, 104]], 21, 16, 16), T.twig, { sh: 7, inner: '<path d="M102 152 L106 126" stroke="#4e5a22" stroke-width="2.4" stroke-linecap="round" opacity="0.6"/><ellipse cx="100" cy="140" rx="4" ry="3" fill="#4e5a22" opacity="0.7"/><ellipse cx="110" cy="120" rx="3.4" ry="2.6" fill="#4e5a22" opacity="0.7"/>' }); });
    G('head', () => {
      L([[[[114, 70], [104, 48], [90, 42]], 3.5, 2.5], [[[130, 68], [136, 46], [150, 42]], 3.5, 2.5]], 'dark');
      S('M98 78 C96 66 108 60 122 60 C136 60 148 66 146 78 C144 90 132 106 122 108 C112 106 100 90 98 78 Z', T.twig, { sh: 7, hl: 5, inner: '<path d="M116 98 l6 6 l6 -6" stroke="#2e3410" stroke-width="2.4" fill="none" stroke-linejoin="round" stroke-linecap="round"/>' });
      eye(108, 76, 9.5, 8.5, { sclera: '#f4ffd8', iris: FALL, pupilK: 0.4, lid: 0.46, tilt: 1 }); eye(137, 76, 8.5, 8.5, { sclera: '#f4ffd8', iris: FALL, pupilK: 0.4, lid: 0.46, tilt: -1 });
      brow(108, 65, 20, 1, '#2e3410', 4); brow(137, 65, 18, -1, '#2e3410', 4);
    });
  });

// 5 · boss — Grand Cerf des ronces : ses bois sont une forêt, ses flancs sont cerclés d'épines, la mousse lui fait un manteau
Mo('ronciers', 5, 'Grand Cerf des ronces', { scale: 1.38, atk: 'smash', wind: -20, hit: 28, colors: { bark: BARK, dark: BARKD, moss: MOSS, leaf: LEAF, antler: '#8a6a44' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [116, 150], back: [30, 150], torso: [82, 190] }, shine: [[170, 116, 9, GLOW]], shineGrp: 'swing' },
  (h) => { const { S, raw, T, G, L, beast, fringe, neck, brow, limb } = h;
    const legs = beast({ front: 102, hind: 48, top: 182, w: 14, t: 'bark', dark: 'dark', hoof: true, hoofT: '#2a1c12', gap: 13 });
    G('tail', () => { leafAt(h, 30, 152, -100, 20, 8, 'leaf'); leafAt(h, 30, 150, -60, 18, 7, 'moss'); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      S('M24 164 C22 138 44 124 72 124 C96 118 116 122 126 138 C132 150 132 172 124 190' + fringe(124, 34, 190, 7, 10) + ' C26 182 24 174 24 164 Z', T.bark, { sh: 11, hl: 7,
        inner: grain(['M40 144 C38 158 40 174 46 186', 'M64 132 C62 152 64 172 70 188', 'M92 128 C94 148 92 170 88 186']) + bramble([[24, 160], [44, 168], [66, 164], [88, 170], [110, 164], [130, 168]], 4.2) + bramble([[28, 178], [50, 184], [74, 180], [98, 186], [122, 180]], 3.6) + '<path d="M26 148 C36 124 70 114 104 118 C118 120 128 130 130 142 C124 138 120 148 112 144 C104 140 100 152 92 148 C84 144 78 154 70 150 C62 146 56 156 48 152 C40 148 34 154 26 148 Z" fill="#7ab84a"/><path d="M44 128 C60 122 82 120 98 124" stroke="#c8f09a" stroke-width="4" fill="none" opacity="0.6" stroke-linecap="round"/>' + berries([[58, 174], [102, 176], [82, 190]]) });
      // l'encolure part vers l'avant, tête baissée pour charger ; crinière de mousse sur la nuque
      neck([108, 152], [126, 130], [148, 122], 50, 36, 'bark', { inner: grain(['M108 150 C116 138 128 130 142 126']) + '<path d="M94 138 C108 116 130 102 154 100 L158 118 C152 114 147 124 141 120 C135 116 132 128 126 126 C120 124 118 136 112 134 C107 132 105 145 99 146 Z" fill="#7ab84a"/><path d="M110 124 C122 114 136 108 150 106" stroke="#c8f09a" stroke-width="3.4" fill="none" opacity="0.6" stroke-linecap="round"/>' });
    });
    G('head', () => {
      // les bois partent de derrière le front : deux grandes branches, des feuilles et des baies
      for (const [p, w, far] of [[[[160, 98], [186, 64], [214, 56]], 9, 1], [[[188, 68], [192, 44], [204, 30]], 6, 1], [[[174, 82], [166, 58], [174, 40]], 6, 1], [[[148, 102], [130, 58], [150, 14]], 11, 0], [[[136, 68], [112, 56], [96, 28]], 8, 0], [[[138, 42], [160, 34], [170, 14]], 7, 0], [[[122, 60], [102, 66], [86, 58]], 6, 0]]) S(limb(p, w, 2.5, 16), T.antler, { sh: 3, far: !!far });
      leafAt(h, 96, 30, -20, 22, 9, 'leaf'); leafAt(h, 86, 60, -80, 20, 8, 'leaf'); leafAt(h, 150, 16, 10, 22, 9, 'leaf'); leafAt(h, 170, 16, 30, 20, 8, 'moss'); leafAt(h, 214, 58, 60, 20, 8, 'leaf', true); leafAt(h, 204, 32, 30, 18, 7, 'leaf', true);
      raw(berries([[110, 48], [156, 36], [130, 38]]));
      S('M138 118 L120 102 L146 106 Z', T.bark, { sh: 3 });
      S('M132 124 C132 106 146 96 162 96 C174 96 184 102 192 112 C202 120 214 132 216 142 C217 150 210 154 202 152 C190 157 172 158 158 154 C142 150 132 140 132 124 Z', T.bark, { sh: 10, hl: 6,
        inner: grain(['M140 122 C144 134 152 144 164 150', 'M152 102 C158 112 160 122 158 132']) + '<path d="M205 134 C210 133 216 137 215 143 C210 145 205 141 205 134 Z" fill="#1c120a"/><path d="M206 152 C198 155 188 156 178 154" stroke="#1c120a" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M136 140 C146 152 160 158 174 156 L172 166 L134 160 Z" fill="#7ab84a" opacity="0.85" filter="url(#g2)"/>' });
      sap(h, 170, 116, 9.5, 7.5, { pupil: 'none', irisK: 0.8 }); brow(170, 105, 26, 1, '#1c120a', 5.5);
    });
  });
