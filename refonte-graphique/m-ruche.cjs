// LA RUCHE (vent) — une colonie d'abeilles : tête, thorax velu, taille fine, abdomen annelé, pattes à articulations,
// mandibules, ailes de verre nervurées, miel et cire.
// Un seul contour par créature : ailes, pattes, mandibules et abdomen partent de SOUS le thorax (voir LISEZMOI, « Les monstres »).
const { Mo } = require('./mon6.cjs');
const Y = '#f0b020', K = '#2a2226', FUZZ = '#dc9a1c', HONEY = '#ffb020', GLASS = '#cfe4f0';
const F = (v) => Math.round(v * 10) / 10, P = (p) => `${F(p[0])} ${F(p[1])}`;
/** Aile de verre nervurée : part de « root », tournée de « a » degrés, longueur len, demi-largeur w. Pas de contour à elle. */
const iwing = (h, root, a, len, w, o = {}) => h.at(`translate(${root[0]} ${root[1]}) rotate(${a})`, () => h.S(
  `M0 0 C${F(len * 0.25)} ${F(-w * 0.9)} ${F(len * 0.85)} ${F(-w * 1.15)} ${F(len)} ${F(-w * 0.2)} C${F(len * 1.02)} ${F(w * 0.5)} ${F(len * 0.45)} ${F(w * 0.55)} 0 0 Z`,
  h.TK(o.t ?? GLASS), { sh: 3, hl: 3, far: o.far, inner: `<g stroke="${o.vein ?? '#5a7a96'}" stroke-width="1.5" fill="none" opacity="0.7" stroke-linecap="round"><path d="M2 -1 C${F(len * 0.3)} ${F(-w * 0.55)} ${F(len * 0.7)} ${F(-w * 0.72)} ${F(len * 0.96)} ${F(-w * 0.2)}"/><path d="M${F(len * 0.12)} ${F(-w * 0.1)} L${F(len * 0.92)} ${F(w * 0.14)}"/><path d="M${F(len * 0.4)} ${F(-w * 0.62)} L${F(len * 0.5)} ${F(w * 0.34)}"/><path d="M${F(len * 0.66)} ${F(-w * 0.74)} L${F(len * 0.74)} ${F(w * 0.26)}"/></g>` }));
/** Patte (ou antenne) à articulations : une suite de points, un segment droit entre chaque, de plus en plus fin. */
const jleg = (h, pts, w, t, far) => { for (let i = pts.length - 2; i >= 0; i--) { const a = pts[i], b = pts[i + 1]; h.S(h.limb([a, [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], b], w * (1 - 0.2 * i), w * (1 - 0.2 * (i + 1)), 8), t, { sh: 2, far }); } };
/** Mandibule : un croc courbe qui s'affine jusqu'à la pointe. */
const mand = (h, pts, w, t, far) => h.S(h.limb(pts, w, 1.6, 12), t, { sh: 2, hl: 1.5, far });
/** Bandes sombres et anneaux d'un abdomen (pour « inner »). */
const bands = (h, list, w, c = K, rings = []) => h.stripes(list, c, w, 1) + h.stripes(rings, '#7a4a08', 1.6, 0.55);
/** Œil à facettes : une amande sombre penchée, un reflet, la paupière en biais. */
const ceye = (h, x, y, rx, ry, rot, glint, lid = 0.34) => h.at(`rotate(${rot} ${x} ${y})`, () => h.eye(x, y, rx, ry, { sclera: '#1c1418', iris: glint, pupil: 'none', irisK: 0.5, lid, tilt: 0.9, look: [rx * 0.25, -ry * 0.1], lidC: '#7a4a08' }));

// 0 · rapide — Ouvrière : petite, tendue comme une flèche, la tête basse et les mandibules ouvertes
Mo('ruche', 0, 'Ouvrière', { scale: 0.9, atk: 'stab', wind: -10, hit: 14, colors: { y: Y, k: K, fuzz: FUZZ },
  grp: { wings: 'back', abdomen: 'back', legs: 'torso', body: 'torso' }, piv: { back: [92, 148], head: [124, 160], torso: [106, 154] } },
  (h) => { const { S, raw, T, G, tuft, eye } = h;
    G('wings', () => { iwing(h, [102, 138], -150, 58, 13, { far: true }); iwing(h, [104, 136], -122, 68, 15); });
    G('abdomen', () => {
      S('M34 128 L4 118 L28 140 Z', T.k, { sh: 2 });
      S('M94 142 C84 124 56 114 38 120 C26 124 24 136 30 144 C42 160 72 170 92 162 C98 158 98 148 94 142 Z', T.y, { sh: 7, hl: 5,
        inner: bands(h, ['M76 120 C70 134 72 152 80 166', 'M56 114 C50 128 52 146 62 160', 'M38 118 C34 128 36 140 44 150'], 9, K, ['M66 116 C60 130 62 148 70 162', 'M46 116 C42 128 44 142 52 154']) });
    });
    G('legs', () => { jleg(h, [[100, 168], [88, 184], [72, 186]], 5, T.k); jleg(h, [[110, 170], [106, 190], [90, 198]], 5, T.k); jleg(h, [[120, 170], [128, 190], [116, 202]], 5, T.k); });
    G('body', () => { S('M84 152 C84 138 96 128 110 130 C122 132 130 142 128 156 C126 168 114 176 102 174 C92 172 84 164 84 152 Z', T.fuzz, { sh: 7, hl: 5 }); tuft(100, 132, -14, 8, 26, 'fuzz', { n: 5 }); });
    G('head', () => {
      jleg(h, [[136, 148], [128, 128], [110, 122]], 4, T.k); jleg(h, [[146, 150], [146, 128], [130, 116]], 4, T.k, true);
      mand(h, [[150, 176], [164, 180], [166, 194]], 8, T.k); mand(h, [[140, 180], [146, 192], [158, 198]], 8, T.k, true);
      S('M120 162 C118 148 130 140 142 142 C154 144 160 154 158 166 C156 178 146 184 136 182 C126 180 121 172 120 162 Z', T.y, { sh: 7, hl: 5 });
      ceye(h, 144, 160, 9.5, 12, -24, '#ffe9a0');
    });
  });

// 1 · costaud — Soldat à dard : cuirasse de chitine, six pattes plantées, des mandibules de lucane
Mo('ruche', 1, 'Soldat à dard', { scale: 1.12, atk: 'smash', wind: -16, hit: 22, colors: { y: Y, k: K, plate: '#4c3e34', fuzz: FUZZ },
  swing: ['head'], grp: { wings: 'back', abdomen: 'legs', legF: 'legs', legs: 'legs', shield: 'torso', body: 'torso' }, piv: { swing: [128, 158], back: [92, 144], torso: [106, 200] } },
  (h) => { const { S, raw, T, G, tuft, stripes, under } = h;
    G('wings', () => { iwing(h, [96, 142], -172, 70, 13, { far: true }); iwing(h, [98, 140], -156, 76, 14); });
    G('abdomen', () => {
      S('M24 180 L2 190 L24 200 Z', T.k, { sh: 2 });
      S('M86 166 C72 148 40 146 24 160 C10 174 12 196 28 206 C48 216 78 210 90 192 C96 184 92 172 86 166 Z', T.y, { sh: 9, hl: 6,
        inner: bands(h, ['M70 150 C62 168 64 192 74 210', 'M48 150 C40 166 42 190 52 210', 'M28 160 C22 174 24 190 32 204'], 11, K, ['M60 148 C52 166 54 192 64 212', 'M38 152 C30 168 32 192 42 208']) });
    });
    G('legF', () => { jleg(h, [[98, 186], [82, 172], [76, 222], [86, 226]], 9, T.k, true); jleg(h, [[136, 182], [160, 164], [170, 222], [180, 226]], 9, T.k, true); });
    G('legs', () => { jleg(h, [[90, 190], [66, 178], [56, 222], [66, 226]], 10, T.k); jleg(h, [[108, 194], [104, 176], [112, 222], [122, 226]], 10, T.k); jleg(h, [[124, 188], [146, 170], [152, 222], [162, 226]], 10, T.k); });
    G('body', () => S('M72 172 C70 148 88 134 108 134 C128 134 142 148 140 170 C138 188 124 198 106 198 C88 198 74 188 72 172 Z', T.plate, { sh: 9, hl: 6,
      inner: stripes(['M78 158 C92 150 120 150 136 160', 'M76 174 C94 168 120 168 138 176'], Y, 4.5, 1) + h.spots([[84, 166, 2.2], [130, 168, 2.2], [106, 186, 2.2]], '#c8b090', 0.8) }));
    // le bouclier du cou : une plaque qui remonte derrière la tête
    G('shield', () => S('M88 148 C88 124 108 112 128 118 C138 122 142 130 140 138 C128 138 116 146 110 158 Z', T.plate, { sh: 5, hl: 4, inner: stripes(['M96 142 C100 130 114 122 130 124'], Y, 4, 1) }));
    G('head', () => {
      jleg(h, [[150, 132], [150, 112], [166, 104]], 4.5, T.k); jleg(h, [[160, 136], [168, 118], [184, 116]], 4.5, T.k, true);
      // mandibules de lucane, de sous la tête
      mand(h, [[164, 170], [194, 166], [196, 194]], 13, T.k); mand(h, [[150, 176], [168, 196], [190, 200]], 13, T.k, true);
      S('M124 156 C122 138 136 126 154 128 C170 130 180 142 178 158 C176 174 162 184 148 182 C134 180 125 170 124 156 Z', T.y, { sh: 8, hl: 6,
        inner: under('M124 150 C128 134 144 126 158 128 C168 130 174 136 178 144 C162 136 140 138 124 150 Z', '#4c3e34', 1) });
      ceye(h, 158, 154, 10, 12, -22, '#ff5a3a', 0.4);
    });
  });

// 2 · tireur — Cracheuse de cire : l'abdomen gonflé recourbé sous elle, une goutte de cire brûlante au bout
Mo('ruche', 2, 'Cracheuse de cire', { scale: 1, atk: 'cast', fx: HONEY, colors: { y: '#e8c060', k: '#4a3426', fuzz: '#c98a2c', wax: '#ffd76a', pale: '#f6e4b0' },
  swing: ['abdomen'], grp: { wings: 'back', legs: 'torso', body: 'torso' }, piv: { swing: [92, 150], back: [92, 118], head: [124, 124], torso: [100, 140] }, shine: [[176, 190, 11, HONEY]], shineGrp: 'swing' },
  (h) => { const { S, raw, T, G, tuft, halo, limb, stripes, under } = h;
    halo(176, 190, 16, HONEY, 0.8);
    G('wings', () => { iwing(h, [90, 120], -146, 60, 14, { far: true }); iwing(h, [92, 118], -112, 70, 16); });
    // l'abdomen passe sous le corps et vise l'ennemi : un sac de cire qui grossit vers le bout, une buse sombre, la goutte
    G('abdomen', () => {
      S('M162 178 C174 174 188 180 188 190 C188 200 174 206 162 202 Z', T.wax, { sh: 3, hl: 3 });
      S(limb([[90, 150], [70, 216], [156, 192]], 28, 40, 20), T.pale, { sh: 9, hl: 6,
        inner: under('M96 206 C116 214 146 208 166 192 C150 214 116 222 92 214 Z', '#ffb020', 0.55) + bands(h, ['M72 166 L104 174', 'M72 190 L104 190', 'M96 216 L112 184', 'M126 216 L134 178'], 6.5, '#4a3426', []) + '<path d="M152 172 C160 180 160 200 152 210 L164 206 C170 196 170 184 164 176 Z" fill="#4a3426"/>' });
    });
    G('legs', () => { jleg(h, [[102, 150], [120, 160], [116, 176]], 5, T.k); jleg(h, [[112, 146], [134, 152], [134, 168]], 5, T.k); });
    G('body', () => { S('M72 138 C70 122 82 110 98 110 C114 110 126 122 124 138 C122 152 110 162 96 162 C82 162 74 152 72 138 Z', T.fuzz, { sh: 8, hl: 6 }); tuft(88, 112, -16, 8, 26, 'fuzz', { n: 5 }); });
    G('head', () => {
      jleg(h, [[132, 100], [128, 80], [112, 72]], 4, T.k); jleg(h, [[142, 102], [146, 82], [132, 70]], 4, T.k, true);
      mand(h, [[148, 136], [160, 142], [160, 154]], 8, T.k); mand(h, [[138, 140], [142, 152], [152, 158]], 8, T.k, true);
      S('M112 122 C110 106 122 96 136 98 C150 100 158 110 156 124 C154 138 144 146 132 144 C120 142 113 134 112 122 Z', T.y, { sh: 7, hl: 5 });
      ceye(h, 140, 118, 9.5, 11.5, -22, '#ffe9a0', 0.4);
    });
  });

// 3 · sorts — Nourrice : sa gelée royale remet la colonie sur pattes
Mo('ruche', 3, 'Nourrice', { atk: 'cast', heal: true, fx: '#fff3c0', colors: { y: '#f6d47a', k: '#6a4a3a', fuzz: '#fff3d8', pot: '#b8703a', jelly: '#fff0b0' },
  swing: ['arm'], far: ['armF'], grp: { wings: 'back', legs: 'legs', abdomen: 'torso', body: 'torso' }, piv: { swing: [112, 136], far: [122, 134], back: [92, 120], head: [106, 112], torso: [104, 200] }, shine: [[152, 132, 10, '#fff0b0']], shineGrp: 'swing' },
  (h) => { const { S, raw, T, G, tuft, halo, stripes, under, fringe } = h;
    halo(152, 132, 15, '#fff0b0', 0.8);
    G('wings', () => { iwing(h, [90, 124], -160, 56, 13, { far: true }); iwing(h, [92, 122], -128, 62, 14); });
    G('legs', () => { jleg(h, [[114, 196], [124, 210], [118, 224], [128, 226]], 7, T.k, true); jleg(h, [[94, 198], [86, 212], [92, 224], [102, 226]], 7.5, T.k); });
    G('armF', () => jleg(h, [[122, 136], [134, 154], [150, 152]], 7, T.k, true));
    // l'abdomen pend sous le thorax, rond et annelé
    G('abdomen', () => S('M76 170 C72 150 136 150 134 172 C132 194 122 210 106 212 C90 212 78 194 76 170 Z', T.y, { sh: 9, hl: 6,
      inner: bands(h, ['M74 172 C92 164 120 164 136 172', 'M78 190 C94 184 118 184 132 190'], 8, '#6a4a3a', ['M76 181 C92 174 120 174 134 181', 'M84 201 C96 196 116 196 128 201']) }));
    G('body', () => { S(`M80 140 C80 126 132 126 132 140 C132 152 126 160 120 164${fringe(120, 92, 164, 4, 6)} C84 158 80 150 80 140 Z`, T.fuzz, { sh: 6, hl: 5 }); });
    G('arm', () => {
      // le pot de gelée royale, tenu à deux pattes
      S('M140 128 L166 128 L164 152 C160 158 146 158 142 152 Z', T.pot, { sh: 4, hl: 3, inner: '<path d="M140 128 L166 128 L166 135 L140 135 Z" fill="#fff0b0"/><path d="M146 135 C146 142 150 144 150 138 Z" fill="#fff0b0"/>' });
      jleg(h, [[112, 138], [128, 150], [146, 142]], 7.5, T.k);
    });
    G('head', () => {
      jleg(h, [[98, 78], [92, 60], [78, 58]], 4, T.k); jleg(h, [[116, 78], [124, 60], [138, 60]], 4, T.k, true);
      S('M80 102 C78 84 92 74 108 74 C124 74 136 86 134 102 C132 118 120 128 106 128 C92 128 82 118 80 102 Z', T.y, { sh: 8, hl: 6 });
      // yeux clos, calme : pas de sourire
      raw('<path d="M96 100 q7 7 14 1 M116 100 q6 6 12 0" stroke="#3a2a22" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M110 116 l8 0" stroke="#6a4a3a" stroke-width="2.4" stroke-linecap="round"/>');
    });
  });

// 4 · élite — Frelon mercenaire : taille de guêpe, bras en lames, on le paie pour tuer
Mo('ruche', 4, 'Frelon mercenaire', { scale: 1.22, atk: 'stab', wind: -34, hit: 30, colors: { y: '#e8782a', k: '#3a1c14', dark: '#241210', blade: '#58382a', amber: '#e8c890' },
  swing: ['armN'], far: ['armF'], grp: { wings: 'back', abdomen: 'torso', legF: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [110, 138], far: [122, 132], back: [90, 108], head: [124, 112], torso: [104, 190] } },
  (h) => { const { S, raw, T, G, limb, stripes, under, saw } = h;
    const blade = (a, b, t, far) => { const dx = b[0] - a[0], dy = b[1] - a[1], m = Math.hypot(dx, dy), u = [dx / m, dy / m], n = [-u[1], u[0]]; let d = `M${P([a[0] - n[0] * 5, a[1] - n[1] * 5])} L${P(b)}`; for (let i = 4; i >= 1; i--) { const p = [a[0] + dx * i / 5, a[1] + dy * i / 5]; d += ` L${P([p[0] + n[0] * 9 + u[0] * 3, p[1] + n[1] * 9 + u[1] * 3])} L${P([p[0] + n[0] * 4 - u[0] * 3, p[1] + n[1] * 4 - u[1] * 3])}`; } S(d + ` L${P([a[0] + n[0] * 6, a[1] + n[1] * 6])} Z`, t, { sh: 2, hl: 2, far }); };
    G('wings', () => { iwing(h, [88, 110], -152, 70, 14, { far: true, t: '#e8c890', vein: '#8a5a2a' }); iwing(h, [90, 108], -118, 84, 17, { t: '#e8c890', vein: '#8a5a2a' }); });
    G('armF', () => { blade([166, 112], [200, 92], T.blade, true); jleg(h, [[122, 132], [148, 136], [168, 112]], 8, T.dark, true); });
    // l'abdomen se recourbe sous lui, le dard pointé vers l'avant
    G('abdomen', () => {
      S('M70 204 L108 224 L72 218 Z', T.dark, { sh: 2 });
      S(limb([[88, 146], [42, 180], [78, 214]], 44, 13, 20), T.y, { sh: 9, hl: 6, inner: bands(h, ['M52 152 L86 176', 'M42 176 L78 190', 'M50 200 L74 202'], 8, '#3a1c14', ['M48 164 L82 184', 'M44 188 L76 196']) });
    });
    G('legF', () => jleg(h, [[110, 158], [140, 176], [136, 222], [148, 226]], 8, T.dark, true));
    G('legs', () => jleg(h, [[98, 162], [124, 186], [112, 222], [124, 226]], 9, T.k));
    G('body', () => S('M74 132 C74 112 90 100 108 102 C126 104 138 118 136 136 C134 154 120 166 104 164 C88 162 76 150 74 132 Z', T.k, { sh: 9, hl: 6, inner: stripes(['M80 124 C94 114 120 116 132 126', 'M78 142 C94 136 120 138 134 146'], '#e8782a', 4.5, 1) }));
    G('armN', () => { blade([172, 150], [208, 138], T.blade); jleg(h, [[110, 138], [140, 162], [174, 150]], 9, T.k); });
    G('head', () => {
      jleg(h, [[122, 70], [118, 46], [136, 34]], 4.5, T.k); jleg(h, [[138, 72], [146, 50], [164, 46]], 4.5, T.k, true);
      mand(h, [[146, 116], [164, 124], [162, 142]], 11, T.dark); mand(h, [[132, 122], [140, 138], [154, 144]], 11, T.dark, true);
      // tête en coin, joues larges, front bas
      S('M102 96 C100 78 114 66 132 68 C150 70 162 84 158 100 C154 116 144 128 132 126 C118 124 104 112 102 96 Z', T.y, { sh: 8, hl: 6,
        inner: under('M104 90 C108 74 122 66 136 68 C146 70 154 76 158 86 C142 78 122 80 104 90 Z', '#3a1c14', 0.9) + stripes(['M112 108 L124 118'], '#3a1c14', 2.4, 0.8) });
      ceye(h, 138, 96, 11, 13.5, -26, '#ffe14a', 0.42);
    });
  });

// 5 · boss — Reine : un abdomen énorme, un manteau d'ailes, une couronne de cire et un sceptre dégoulinant de miel
Mo('ruche', 5, 'Reine', { scale: 1.36, atk: 'smash', wind: -50, hit: 40, fx: HONEY, colors: { y: Y, k: K, gold: '#ffd76a', fur: '#fff6e0', wood: '#7a5230', royal: '#7a2a8a' },
  swing: ['arm'], far: ['armF'], grp: { wings: 'back', abdomen: 'legs', legF: 'legs', legs: 'legs', body: 'torso', collar: 'torso' }, piv: { swing: [118, 132], far: [130, 130], back: [98, 114], head: [120, 108], torso: [106, 200] }, shine: [[178, 70, 12, HONEY]], shineGrp: 'swing' },
  (h) => { const { S, raw, T, G, halo, limb, bar, disc, stripes, under, spots, fringe } = h;
    halo(178, 70, 18, HONEY, 0.8);
    G('wings', () => { iwing(h, [94, 118], -170, 74, 16, { far: true }); iwing(h, [96, 116], -142, 92, 19, { far: true }); iwing(h, [98, 114], -112, 104, 21); });
    G('abdomen', () => {
      S('M24 196 L4 210 L28 212 Z', T.k, { sh: 2 });
      S('M104 148 C70 138 26 150 16 182 C10 208 40 226 78 226 C108 226 128 210 128 186 C128 170 118 154 104 148 Z', T.y, { sh: 12, hl: 8,
        inner: bands(h, ['M92 144 C82 168 84 204 98 226', 'M66 142 C56 166 58 204 72 228', 'M40 150 C30 170 32 204 46 224', 'M20 172 C16 186 18 204 26 216'], 12, K, ['M80 142 C70 166 72 206 86 228', 'M54 146 C44 168 46 206 60 228', 'M30 158 C22 176 24 204 36 220'])
          + spots([[88, 186, 2.6], [62, 186, 2.6], [36, 188, 2.4]], '#ffd76a', 0.9) });
    });
    G('legF', () => jleg(h, [[126, 166], [148, 190], [142, 222], [154, 226]], 8, T.k, true));
    G('legs', () => jleg(h, [[112, 170], [130, 196], [120, 222], [132, 226]], 9, T.k));
    G('armF', () => { jleg(h, [[130, 132], [154, 130], [172, 142]], 8, T.k, true); S('M170 138 L186 140 L174 146 L184 152 L168 148 Z', T.k, { sh: 2, far: true }); });
    G('body', () => S('M90 140 C88 120 104 110 120 110 C136 110 148 122 146 140 C144 158 132 170 118 170 C104 170 92 158 90 140 Z', T.royal, { sh: 8, hl: 5, inner: stripes(['M96 150 C108 144 130 144 142 150'], '#ffd76a', 4, 1) + spots([[118, 160, 3]], '#ffd76a', 0.9) }));
    // col d'hermine
    G('collar', () => S(`M88 120 C96 104 142 104 150 120 L146 132${fringe(146, 92, 132, 5, 8)} Z`, T.fur, { sh: 4, hl: 3, inner: spots([[102, 120, 2.2, 3], [118, 118, 2.2, 3], [134, 120, 2.2, 3]], '#2a2226', 0.85) }));
    G('arm', () => {
      S(bar([148, 170], [174, 82], 5.5), T.wood, { sh: 2 });
      // la tête du sceptre : une louche à miel striée, une coulure
      S('M164 64 C166 52 190 52 192 64 C196 72 194 86 178 88 C164 86 160 72 164 64 Z', T.gold, { sh: 4, hl: 4, inner: stripes(['M163 66 L193 66', 'M162 74 L194 74', 'M165 81 L191 81'], '#b87a18', 2.4, 0.9) + '<path d="M170 84 C170 96 176 100 176 88 Z" fill="#ffb020"/>' });
      jleg(h, [[118, 134], [140, 150], [158, 136]], 9, T.k);
    });
    G('head', () => {
      jleg(h, [[110, 62], [100, 40], [84, 38]], 4.5, T.k); jleg(h, [[134, 62], [146, 42], [162, 46]], 4.5, T.k, true);
      mand(h, [[138, 106], [152, 112], [150, 126]], 9, T.k); mand(h, [[126, 110], [130, 122], [142, 128]], 9, T.k, true);
      S('M94 88 C92 70 106 60 122 60 C138 60 152 70 150 88 C148 104 136 116 122 116 C108 116 96 104 94 88 Z', T.y, { sh: 8, hl: 6 });
      S('M100 66 L96 40 L110 54 L122 32 L134 54 L148 40 L144 66 C132 60 112 60 100 66 Z', T.gold, { sh: 4, hl: 3, inner: '<circle cx="122" cy="52" r="3.8" fill="#d8382e"/>' });
      ceye(h, 132, 88, 10.5, 12.5, -24, '#ff5ad8', 0.42);
    });
  });
