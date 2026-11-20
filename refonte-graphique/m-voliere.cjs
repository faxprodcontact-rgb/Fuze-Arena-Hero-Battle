// LA VOLIÈRE D'ORAGE (vent) — des oiseaux chargés de foudre : plumes ardoise et nuit, becs crochus, éclairs jaunes.
// Un seul contour par créature : ailes, cous, pattes et queues partent de SOUS le corps (voir LISEZMOI, « Les monstres »).
// Chaque oiseau a sa posture : serres en avant, voûté, perché, en roue, coup de patte, ailes dressées.
const { Mo } = require('./mon6.cjs');
const BOLT = '#ffe14a', MAW = '#3a1420', CLAW = '#241c26';
const F = (v) => Math.round(v * 10) / 10, P = (p) => `${F(p[0])} ${F(p[1])}`;
/** Un éclair (à mettre dans « inner »). */
const spark = (d, w = 3) => `<path d="${d}" stroke="${BOLT}" stroke-width="${w}" fill="none" stroke-linejoin="round" stroke-linecap="round"/><path d="${d}" stroke="#fff" stroke-width="${w * 0.4}" fill="none" stroke-linejoin="round" stroke-linecap="round" opacity="0.8"/>`;
/**
 * Une aile à plumes. A = épaule, C = poignet (point de contrôle du bord d'attaque), B = bout.
 * o : { n (rémiges), len, side (+1 / −1 : de quel côté pendent les plumes), sweep (penchées vers le bout), cov (hauteur des couvertures), m }
 * Renvoie { prim, cov } : chacune { d (silhouette), lines (traits entre les plumes, pour « inner ») }.
 */
const wing = (A, C, B, o = {}) => {
  const n = o.n ?? 7, len = o.len ?? 44, side = o.side ?? 1, sweep = o.sweep ?? 0.6;
  const prof = o.prof ?? ((t) => 0.58 + 0.42 * Math.sin(Math.PI * Math.min(1, 0.12 + t * 0.92)));
  const q = (t) => [(1 - t) ** 2 * A[0] + 2 * t * (1 - t) * C[0] + t * t * B[0], (1 - t) ** 2 * A[1] + 2 * t * (1 - t) * C[1] + t * t * B[1]];
  const fd = (t) => { let tx = (1 - t) * (C[0] - A[0]) + t * (B[0] - C[0]), ty = (1 - t) * (C[1] - A[1]) + t * (B[1] - C[1]); const m = Math.hypot(tx, ty) || 1; tx /= m; ty /= m; const s = sweep * (0.25 + t), x = -ty * side + tx * s, y = tx * side + ty * s, k = Math.hypot(x, y); return [x / k, y / k]; };
  const at = (t, L) => { const p = q(t), d = fd(t); return [p[0] + d[0] * L, p[1] + d[1] * L]; };
  const edge = (L, m, round, notch) => {
    let d = ''; const lines = [];
    for (let i = m; i >= 1; i--) {
      const t1 = i / m, t0 = (i - 1) / m, tm = (t0 + t1) / 2, nt = at(t0, L * prof(t0) * notch);
      d += round ? ` Q${P(at(tm, L * prof(tm) * 1.2))} ${P(nt)}` : ` L${P(at(tm + 0.25 / m, L * prof(tm)))} Q${P(at(tm - 0.1 / m, L * prof(tm) * 0.9))} ${P(nt)}`;
      if (i > 1) lines.push(`M${P(at(t0, L * prof(t0) * 0.12))} L${P(nt)}`);
    }
    return { d: `M${P(A)} Q${P(C)} ${P(B)}${d} Z`, lines };
  };
  return { prim: edge(len, n, false, o.notch ?? 0.66), cov: edge(len * (o.cov ?? 0.46), o.m ?? n + 1, true, 0.82) };
};
/** Une griffe crochue au bout d'un doigt : E = bout du doigt, u = sens du doigt, hk = vers où elle se recourbe. */
const claw = (E, u, hk, k = 1) => `<path d="M${P([E[0] - hk[0] * 2.6 * k, E[1] - hk[1] * 2.6 * k])} Q${P([E[0] + u[0] * 7 * k - hk[0] * 2 * k, E[1] + u[1] * 7 * k - hk[1] * 2 * k])} ${P([E[0] + u[0] * 6 * k + hk[0] * 7 * k, E[1] + u[1] * 6 * k + hk[1] * 7 * k])} Q${P([E[0] + u[0] * 2.5 * k + hk[0] * 1.5 * k, E[1] + u[1] * 2.5 * k + hk[1] * 1.5 * k])} ${P([E[0] + hk[0] * 2.6 * k, E[1] + hk[1] * 2.6 * k])} Z" fill="${CLAW}"/>`;
/** Serres ouvertes (oiseau en vol), tournées de « rot » degrés autour de (x, y). */
const talon = (h, x, y, rot, k, t, far) => h.at(`translate(${x} ${y}) rotate(${rot}) scale(${k})`, () => {
  const toes = [[[[0, 0], [-7, 3], [-12, 9]], [-0.5, 0.85], [0.9, 0.3]], [[[0, 0], [9, -8], [19, -9]], [1, -0.1], [0, 1]], [[[0, 0], [8, 7], [17, 10]], [0.9, 0.35], [-0.3, 1]], [[[0, 0], [11, -1], [22, 1]], [1, 0.1], [0, 1]]];
  for (const [p, u, hk] of toes) { h.raw(claw(p[2], u, hk)); h.S(h.limb(p, 6, 4.4, 10), t, { sh: 2, far }); }
  h.S(h.disc(0, 0, 4.6), t, { sh: 2, far });
});
/** Patte posée au sol : trois doigts devant, un derrière, griffes sombres. (x, y) = la cheville. */
const foot = (h, x, y, k, t, far) => {
  const g = 226.5, toes = [[[[x, y], [x - 6 * k, g - 4], [x - 11 * k, g - 1]], [-1, 0.1]], [[[x, y], [x + 9 * k, g - 7], [x + 19 * k, g - 4]], [1, 0.1]], [[[x, y], [x + 6 * k, g - 3], [x + 13 * k, g - 1]], [1, 0.1]]];
  for (const [p, u] of toes) { h.raw(claw(p[2], u, [0, 1], 0.62 * k)); h.S(h.limb(p, 6.5 * k, 4.6 * k, 10), t, { sh: 2, far }); }
};

/** Une queue en éventail : n plumes serrées autour de la direction « ang » (degrés), bande sombre au bout. */
const tailFan = (h, base, ang, len, n, spread, w, tones, far) => {
  for (let i = 0; i < n; i++) { const a = (ang + spread * (i / (n - 1) - 0.5)) * Math.PI / 180, k = len * (1 - 0.12 * Math.abs(i / (n - 1) - 0.5) * 2), tip = [base[0] + Math.cos(a) * k, base[1] + Math.sin(a) * k], mid = [base[0] + Math.cos(a) * k * 0.5, base[1] + Math.sin(a) * k * 0.5];
    const b0 = [base[0] + Math.cos(a) * k * 0.8, base[1] + Math.sin(a) * k * 0.8], nx = -Math.sin(a) * w * 0.6, ny = Math.cos(a) * w * 0.6;
    const c = Math.cos(a), sn = Math.sin(a), q = (p, k) => P([p[0] - sn * w * k, p[1] + c * w * k]), end = [tip[0] + c * w * 0.3, tip[1] + sn * w * 0.3];
    h.S(`M${q(base, -0.3)} L${q(tip, -0.5)} Q${P(end)} ${q(tip, 0.5)} L${q(base, 0.3)} Z`, tones[i % tones.length], { sh: 3, far, inner: `<path d="M${P([b0[0] - nx, b0[1] - ny])} L${P([b0[0] + nx, b0[1] + ny])}" stroke="#10121e" stroke-width="${F(w * 0.5)}" opacity="0.5"/>` }); }
};

// 0 · rapide — Faucon : il arrive serres en avant, les ailes rabattues en arrière
Mo('voliere', 0, 'Faucon', { scale: 0.96, atk: 'stab', wind: -14, hit: 18, colors: { slate: '#5d6f8f', dark: '#37445f', cream: '#f2e7d0', yel: '#f0b828' },
  grp: { wingF: 'back', wingN: 'back', wingNc: 'back', tailF: 'back', legF: 'torso', legN: 'torso', body: 'torso' }, piv: { back: [116, 132], head: [140, 110], torso: [106, 150] } },
  (h) => { const { S, raw, T, G, L, neck, brow, stripes, under, eye } = h;
    const wf = wing([126, 126], [146, 46], [96, 8], { n: 6, len: 36, side: -1, sweep: 0.5 }), wn = wing([112, 136], [116, 46], [36, 28], { n: 7, len: 50, side: -1, sweep: 0.5 });
    G('wingF', () => S(wf.prim.d, T.dark, { sh: 5, far: true, inner: stripes(wf.prim.lines, '#141a2a', 1.8, 0.6) }));
    G('tailF', () => tailFan(h, [84, 168], 158, 58, 5, 40, 15, [T.dark, T.slate]));
    G('wingN', () => S(wn.prim.d, T.slate, { sh: 7, hl: 3, inner: stripes(wn.prim.lines, '#1c2438', 1.8, 0.6) + stripes(['M46 52 L58 60', 'M56 44 L70 54', 'M70 40 L82 52'], '#2a3550', 4, 0.45) }));
    G('wingNc', () => S(wn.cov.d, T.dark, { sh: 5, hl: 3, inner: stripes(wn.cov.lines, '#141a2a', 1.6, 0.5) }));
    G('legF', () => { S(h.limb([[124, 158], [140, 164], [152, 176]], 20, 11, 12), T.cream, { sh: 4, far: true }); L([[[[150, 174], [158, 178], [166, 182]], 6.5, 5.5]], 'yel', { far: true }); talon(h, 166, 182, 14, 1, T.yel, true); });
    G('body', () => {
      S('M138 112 C152 126 150 152 132 168 C114 182 86 188 68 180 C56 174 58 162 70 152 C90 134 108 108 138 112 Z', T.slate, { sh: 9, hl: 6,
        inner: under('M148 122 C152 148 138 166 114 176 C98 182 80 184 68 178 C92 172 120 152 130 120 Z', '#f2e7d0', 0.95) + stripes(['M126 140 L142 146', 'M118 152 L136 160', 'M106 162 L124 172', 'M94 170 L108 180'], '#37445f', 3.2, 0.7) });
      neck([128, 128], [138, 116], [146, 106], 30, 27, 'slate');
    });
    G('legN', () => { S(h.limb([[108, 166], [124, 176], [136, 190]], 22, 12, 12), T.cream, { sh: 4, inner: stripes(['M112 166 L122 176', 'M120 174 L130 184'], '#37445f', 3, 0.6) }); L([[[[134, 188], [142, 194], [150, 198]], 7, 6]], 'yel'); talon(h, 150, 198, 22, 1.08, T.yel); });
    G('head', () => {
      // le bec crochu sort de sous la tête
      S('M158 88 C172 84 186 92 187 106 C187 112 184 118 180 121 C180 112 176 108 164 108 Z', T.yel, { sh: 3, hl: 2, inner: '<path d="M176 90 C186 96 188 108 180 122 C180 112 176 106 170 104 Z" fill="#2a2430"/>' });
      S('M128 104 C126 88 138 77 152 79 C164 81 171 92 169 103 C167 115 155 123 143 121 C134 119 128 113 128 104 Z', T.slate, { sh: 7, hl: 5,
        inner: under('M134 108 C144 104 158 106 168 104 C166 116 154 124 142 122 C136 120 132 114 134 108 Z', '#f2e7d0', 0.95) + '<path d="M150 100 C150 110 146 118 140 120 C142 112 142 104 144 98 Z" fill="#1c2438"/><path d="M128 100 C130 86 140 78 152 79 C160 80 166 86 168 92 C156 88 140 90 128 100 Z" fill="#37445f"/>' });
      eye(156, 96, 7.6, 7.2, { iris: BOLT, pupilK: 0.55, lid: 0.3, tilt: 0.9, lidC: '#1c2438' }); brow(157, 87, 20, 1, '#141a2a', 4.6);
    });
  });

// 1 · costaud — Marabout : voûté comme un croque-mort, un bec en pioche, un jabot nu
Mo('voliere', 1, 'Marabout', { scale: 1.14, atk: 'smash', wind: -18, hit: 26, colors: { slate: '#465068', dark: '#2c3348', white: '#ece8de', skin: '#c98a86', beak: '#d9c79c', leg: '#a9a79c', pouch: '#d86a72' },
  swing: ['head'], grp: { legF: 'legs', legs: 'legs', body: 'torso', wing: 'torso' }, piv: { swing: [118, 128], torso: [100, 180] } },
  (h) => { const { S, raw, T, G, L, neck, tuft, brow, stripes, spots, under, eye, fringe } = h;
    G('legF', () => { L([[[[112, 170], [108, 198], [116, 221]], 8, 6.5]], 'leg', { far: true }); foot(h, 116, 219, 1, T.leg, true); });
    G('legs', () => { L([[[[96, 172], [90, 200], [98, 221]], 9, 7]], 'leg'); foot(h, 98, 219, 1.1, T.leg); });
    G('body', () => {
      S('M60 152 C58 124 82 106 108 108 C132 110 144 130 140 152 C136 172 118 184 96 184 C84 184 74 180 68 172 L52 184 L58 166 C58 162 60 156 60 152 Z', T.white, { sh: 9, hl: 6, inner: stripes(['M104 170 q4 6 0 10', 'M116 162 q4 6 0 10', 'M92 174 q4 5 0 9'], '#a39c8c', 2.2, 0.6) });
      // le cou nu rentre dans une collerette de duvet
      neck([118, 128], [128, 112], [126, 90], 30, 24, 'skin', { inner: stripes(['M116 118 q8 -3 16 1', 'M118 106 q7 -3 14 1'], '#9a5c5c', 2, 0.6) });
      S('M98 122 C104 108 132 108 142 124 L138 136 L130 128 L124 140 L116 130 L108 140 L104 128 Z', T.white, { sh: 4, hl: 3 });
    });
    G('wing', () => S('M66 140 C70 116 96 106 120 116 C132 124 132 144 122 154 C108 164 92 166 80 164 L44 190 L62 158 Z', T.slate, { sh: 8, hl: 5,
      inner: stripes(['M78 132 q8 8 20 4', 'M98 126 q8 8 20 4', 'M72 148 q10 8 22 3', 'M94 144 q10 8 22 3', 'M62 160 L52 180', 'M72 162 L60 178'], '#1a2030', 2.2, 0.6) + under('M70 150 C90 160 110 158 124 150 C112 164 92 168 78 164 L50 184 Z', '#2c3348', 0.8) }));
    G('head', () => {
      // le jabot pend sous la gorge, le bec part de sous le crâne
      S(h.limb([[128, 104], [140, 122], [136, 148]], 13, 17, 14), T.pouch, { sh: 4, hl: 3, inner: stripes(['M134 122 q6 2 8 8', 'M132 134 q6 2 8 8'], '#a8404c', 1.8, 0.6) });
      S('M132 70 C146 66 156 72 162 84 L192 150 C180 142 160 122 140 100 C134 94 130 82 132 70 Z', T.beak, { sh: 5, hl: 4, inner: stripes(['M142 84 C156 100 172 124 186 142'], '#8a7850', 2.4, 0.7) + under('M176 122 L192 150 C184 144 176 136 170 130 Z', '#6a5a3c', 0.8) });
      S('M106 84 C104 68 116 58 130 60 C143 62 150 72 148 84 C146 96 136 104 124 102 C114 100 107 94 106 84 Z', T.skin, { sh: 7, hl: 5, inner: spots([[114, 76, 2.4], [120, 68, 2], [112, 88, 2.2], [124, 94, 2], [130, 66, 1.8]], '#7a4444', 0.6) });
      tuft(110, 72, -60, 9, 14, 'white', { n: 3 });
      eye(134, 78, 6.6, 6.2, { iris: BOLT, pupilK: 0.55, lid: 0.34, tilt: 0.9 }); brow(134, 69, 20, 1, '#3a1c22', 4.6);
    });
  });

// 2 · tireur — Corbeau lanceur : perché sur une patte, l'autre serre une pierre de foudre prête à partir
Mo('voliere', 2, 'Corbeau lanceur', { scale: 0.98, atk: 'cast', fx: BOLT, colors: { k: '#2b2a3c', dark: '#1c1b2a', blue: '#43426a', beak: '#3a3a4c', leg: '#55546a', stone: '#6f7c96' },
  swing: ['legN'], grp: { tailF: 'back', legF: 'legs', body: 'torso', wing: 'torso' }, piv: { swing: [112, 176], back: [62, 164], head: [132, 138], torso: [100, 180] }, shine: [[156, 204, 11, BOLT]], shineGrp: 'swing' },
  (h) => { const { S, raw, T, G, L, neck, tuft, brow, stripes, under, halo, eye, teeth } = h;
    halo(156, 204, 17, BOLT, 0.75);
    G('tailF', () => tailFan(h, [70, 164], 170, 56, 4, 24, 15, [T.dark, T.k]));
    G('legF', () => { L([[[[98, 178], [94, 202], [102, 221]], 7.5, 6]], 'leg', { far: true }); foot(h, 102, 219, 1, T.leg, true); });
    G('body', () => {
      S('M54 162 C56 142 80 130 106 132 C128 134 140 150 136 166 C132 182 108 190 86 188 C66 186 52 178 54 162 Z', T.k, { sh: 9, hl: 6, inner: under('M70 178 C92 186 118 182 134 168 C128 184 108 190 88 188 Z', '#43426a', 0.6) });
      neck([116, 152], [128, 138], [138, 126], 38, 30, 'k');
      tuft(132, 152, 150, 13, 22, 'k', { n: 4 });
    });
    // l'aile repliée : couvertures en écailles, longues rémiges croisées sur la queue
    G('wing', () => S('M108 140 C96 132 78 134 68 144 L28 172 L60 168 L34 186 L72 178 C92 178 112 166 114 152 C114 146 112 142 108 140 Z', T.blue, { sh: 7, hl: 5,
      inner: stripes(['M100 142 q-2 10 -12 12', 'M88 142 q-2 10 -12 12', 'M104 154 q-6 10 -18 12', 'M84 158 L44 174', 'M88 166 L52 180'], '#12111c', 2.2, 0.6) }));
    G('legN', () => {
      S('M142 196 L154 190 L168 196 L170 210 L160 218 L146 214 Z', T.stone, { sh: 4, hl: 3, inner: spark('M152 196 L160 202 L154 206 L162 212', 2.6) });
      L([[[[112, 176], [128, 186], [142, 196]], 9, 6]], 'leg');
      for (const [p, u] of [[[[142, 196], [150, 192], [158, 194]], [1, 0.2]], [[[142, 196], [148, 200], [154, 206]], [0.7, 0.7]], [[[142, 196], [142, 204], [146, 212]], [0.3, 1]]]) { raw(claw(p[2], u, [u[1] * -1 + 0.2, u[0]], 0.7)); S(h.limb(p, 5.6, 4.4, 8), T.leg, { sh: 2 }); }
    });
    G('head', () => {
      // bec ouvert : le fond de la gorge d'abord, puis le bec entaillé
      raw(`<path d="M180 127 L158 126 L176 139 C172 134 174 130 180 127 Z" fill="${MAW}"/>`);
      S('M150 110 C166 108 184 114 192 126 L158 126 L180 142 C170 146 156 144 148 138 Z', T.beak, { sh: 4, hl: 3 });
      S('M118 128 C116 112 128 102 142 104 C155 106 162 116 160 128 C158 140 148 148 136 146 C126 144 119 138 118 128 Z', T.k, { sh: 7, hl: 5, inner: under('M120 122 C126 108 140 102 152 108 C140 108 128 114 120 122 Z', '#43426a', 0.7) });
      tuft(126, 108, -50, 10, 16, 'k', { n: 3 });
      eye(146, 120, 7, 6.6, { iris: BOLT, pupilK: 0.55, lid: 0.34, tilt: 0.9 }); brow(146, 111, 20, 1, '#0c0b14', 4.6);
    });
  });

// 3 · sorts — Paon d'orage : sa roue crépite, chaque ocelle est un œil d'orage
Mo('voliere', 3, 'Paon d\'orage', { scale: 1.02, atk: 'cast', fx: BOLT, colors: { teal: '#1f7fa8', deep: '#1c3a6a', fan: '#2a3a78', fan2: '#22507a', gold: '#d8a838', leg: '#8a8272', buff: '#c9a070' },
  grp: { fan: 'back', fan2: 'back', legs: 'legs', body: 'torso' }, piv: { back: [102, 190], head: [116, 170], torso: [102, 200] }, shine: [[100, 106, 9, BOLT]], shineGrp: 'back' },
  (h) => { const { S, raw, T, G, L, tuft, brow, stripes, under, eye, halo } = h;
    const O = [100, 198], ray = (a, r) => [O[0] + r * Math.sin(a * Math.PI / 180), O[1] - r * Math.cos(a * Math.PI / 180)];
    const ocelle = (p, k = 1) => `<ellipse cx="${F(p[0])}" cy="${F(p[1])}" rx="${F(10 * k)}" ry="${F(12 * k)}" fill="#35d0d8"/><ellipse cx="${F(p[0])}" cy="${F(p[1] + 1)}" rx="${F(6.4 * k)}" ry="${F(8 * k)}" fill="${BOLT}"/><ellipse cx="${F(p[0])}" cy="${F(p[1] + 2)}" rx="${F(3.4 * k)}" ry="${F(4.6 * k)}" fill="#141a3a"/>`;
    halo(100, 106, 16, BOLT, 0.5);
    G('fan', () => { for (const a of [-80, -60, -40, -20, 0, 20, 40, 60, 80]) { const tip = ray(a, 106), sp = ray(a, 92); S(h.limb([O, ray(a, 50), tip], 10, 30, 14), T.fan, { sh: 4, hl: 3, inner: `<path d="M${P(O)} L${P(sp)}" stroke="#9fb4e8" stroke-width="1.6" opacity="0.5"/>` + ocelle(sp, 0.86) }); } });
    G('fan2', () => { for (const a of [-70, -50, -30, -10, 10, 30, 50, 70]) { const sp = ray(a, 60); S(h.limb([O, ray(a, 34), ray(a, 72)], 10, 22, 12), T.fan2, { sh: 4, hl: 2, inner: ocelle(sp, 0.6) }); } });
    G('legs', () => { L([[[[108, 204], [112, 214], [110, 221]], 7, 5.5]], 'leg', { far: true }); foot(h, 110, 219, 0.9, T.leg, true); L([[[[94, 204], [96, 214], [94, 221]], 7.5, 6]], 'leg'); foot(h, 94, 219, 0.95, T.leg); });
    // la tête et le cou partent de sous le corps
    G('head', () => {
      S(h.limb([[112, 178], [96, 138], [124, 110]], 26, 15, 18), T.teal, { sh: 6, hl: 4, inner: stripes(['M104 160 q10 -4 18 2', 'M104 146 q9 -4 16 2'], '#1c3a6a', 2.2, 0.5) });
      tuft(122, 92, -8, 22, 18, 'gold', { n: 5 });
      S('M138 104 L164 113 L138 119 Z', T.gold, { sh: 3, inner: '<path d="M140 111 L160 113" stroke="#6a4a18" stroke-width="1.6"/>' });
      S('M112 108 C110 96 120 88 131 90 C141 92 146 100 144 109 C142 119 134 124 125 122 C117 120 112 115 112 108 Z', T.teal, { sh: 6, hl: 4, inner: under('M120 106 C126 98 138 98 144 106 C138 112 126 112 120 106 Z', '#f4f0e0', 0.9) });
      eye(132, 105, 6.4, 6, { iris: BOLT, pupilK: 0.55, lid: 0.32, tilt: 0.9 }); brow(132, 96, 18, 1, '#10203c', 4.2);
    });
    G('body', () => S('M64 190 C62 172 80 162 102 162 C122 162 134 174 132 190 C130 204 116 212 98 212 C80 212 66 204 64 190 Z', T.teal, { sh: 9, hl: 6,
      inner: under('M66 186 C76 170 104 168 118 180 C112 196 86 202 66 186 Z', '#1c3a6a', 0.85) + stripes(['M78 180 q8 8 18 3', 'M96 178 q8 7 17 2', 'M72 190 q10 7 20 2', 'M92 192 q9 6 18 0'], '#0e2244', 2.2, 0.7) }));
  });

// 4 · élite — Casoar : un casque de corne, un cou bleu, et une griffe-poignard au bout de la patte
Mo('voliere', 4, 'Casoar', { scale: 1.22, atk: 'slash', wind: -30, hit: 34, colors: { k: '#25232e', sheen: '#3a3a52', blue: '#2a62c8', violet: '#5a3aa8', red: '#d8382e', horn: '#a08a5a', leg: '#7a7668', beak: '#3c3a44' },
  swing: ['legN'], grp: { legF: 'legs', body: 'torso' }, piv: { swing: [112, 172], head: [112, 130], torso: [96, 190] } },
  (h) => { const { S, raw, T, G, L, tuft, brow, stripes, under, eye, fringe } = h;
    const dagger = (p, u, k = 1) => `<path d="M${P([p[0] - u[1] * 3 * k, p[1] + u[0] * 3 * k])} L${P([p[0] + u[0] * 20 * k, p[1] + u[1] * 20 * k])} L${P([p[0] + u[1] * 3 * k, p[1] - u[0] * 3 * k])} Z" fill="${CLAW}"/>`;
    G('legF', () => { L([[[[96, 190], [88, 206], [96, 221]], 13, 10]], 'leg', { far: true, inner: stripes(['M88 204 l8 2', 'M90 212 l8 2'], '#4a463c', 1.8, 0.6) }); foot(h, 96, 218, 1.35, T.leg, true); });
    // la patte qui frappe : cuisse cachée dans les plumes, trois doigts écartés, le poignard en avant
    G('legN', () => {
      raw(dagger([172, 190], [0.94, 0.34], 1.15) + dagger([170, 180], [0.98, -0.2], 0.7) + dagger([166, 198], [0.7, 0.72], 0.7));
      S(h.limb([[160, 184], [166, 180], [172, 180]], 7, 6, 8), T.leg, { sh: 2 }); S(h.limb([[160, 186], [164, 192], [168, 198]], 7, 6, 8), T.leg, { sh: 2 }); S(h.limb([[158, 184], [166, 186], [174, 190]], 8, 7, 8), T.leg, { sh: 2 });
      L([[[[112, 174], [132, 198], [160, 184]], 17, 11]], 'leg', { N: 18, inner: stripes(['M134 190 l6 8', 'M142 186 l6 8', 'M150 182 l6 8'], '#4a463c', 1.8, 0.6) });
    });
    G('head', () => {
      // le cou nu sort des plumes ; caroncules rouges dessous, casque de corne dessus
      S(h.limb([[108, 150], [112, 112], [136, 84]], 26, 16, 18), T.blue, { sh: 6, hl: 4, inner: under('M96 150 C100 124 108 108 122 96 C112 112 110 130 112 150 Z', '#5a3aa8', 0.85) + stripes(['M106 132 q8 -3 14 2', 'M108 118 q8 -3 13 2'], '#1a3a80', 2, 0.5) });
      S(h.limb([[132, 104], [136, 118], [130, 132]], 8, 11, 10), T.red, { sh: 3, hl: 2 }); S(h.limb([[124, 108], [124, 122], [118, 134]], 8, 10, 10), T.red, { sh: 3, far: true });
      S('M126 70 C122 44 136 26 156 24 C150 40 156 56 160 70 Z', T.horn, { sh: 5, hl: 4, inner: stripes(['M136 62 C134 48 140 36 150 30', 'M146 64 C144 52 148 42 154 34'], '#6a5a34', 2, 0.6) });
      raw(`<path d="M184 91 L164 92 L182 102 C179 98 180 94 184 91 Z" fill="${MAW}"/>`);
      S('M154 76 C170 76 186 82 194 92 L164 92 L186 105 C176 108 162 106 154 100 Z', T.beak, { sh: 4, hl: 3 });
      S('M122 86 C120 72 132 62 146 64 C158 66 165 76 163 87 C161 98 151 105 140 103 C130 101 123 95 122 86 Z', T.blue, { sh: 6, hl: 4, inner: under('M124 80 C130 68 144 62 156 68 C144 68 132 72 124 80 Z', '#7ab0ff', 0.5) });
      eye(149, 82, 7, 6.6, { iris: '#ffb020', pupilK: 0.55, lid: 0.34, tilt: 0.9 }); brow(149, 73, 20, 1, '#10204a', 4.6);
    });
    G('body', () => S(`M40 186 C38 150 64 122 98 122 C124 122 140 140 138 164 C136 178 132 188 126 198${fringe(126, 62, 200, 7, 12)} L52 208 L50 196 L38 204 Z`, T.k, { sh: 10, hl: 6,
      inner: stripes(['M66 140 C60 158 60 176 64 194', 'M80 132 C74 152 74 176 78 198', 'M94 128 C90 150 90 176 92 198', 'M108 130 C108 150 108 176 106 198', 'M122 138 C124 156 122 176 118 196'], '#4a4a66', 2.6, 0.7) + under('M60 150 C70 132 100 126 124 136 C100 134 76 138 60 150 Z', '#3a3a52', 0.7) }));
  });

// 5 · boss — Oiseau-tonnerre : l'orage en personne, les deux ailes dressées, la tête de profil, le bec grand ouvert
Mo('voliere', 5, 'Oiseau-tonnerre', { scale: 1.38, atk: 'smash', wind: -40, hit: 44, fx: BOLT, colors: { blue: '#33509a', deep: '#1e2c64', night: '#161c48', pale: '#dfe8f8', gold: '#f0b020', yel: '#e8a824' },
  swing: ['wingN', 'wingNc'], far: ['wingF', 'wingFc'], grp: { tailF: 'back', crest: 'head', legF: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [88, 130], far: [128, 130], back: [108, 184], head: [116, 116], torso: [108, 196] }, shine: [[108, 152, 12, BOLT]] },
  (h) => { const { S, raw, T, G, L, at, neck, brow, stripes, under, halo, eye, fringe } = h;
    const wn = wing([88, 132], [66, 14], [12, 24], { n: 8, len: 64, side: -1, sweep: 0.45 }), wf = wing([128, 132], [150, 14], [202, 24], { n: 8, len: 64, side: 1, sweep: 0.45 });
    G('tailF', () => tailFan(h, [108, 182], 96, 42, 5, 76, 19, [T.night, T.deep]));
    G('wingF', () => S(wf.prim.d, T.deep, { sh: 8, hl: 3, inner: stripes(wf.prim.lines, '#0a0e2a', 2.2, 0.6) + spark('M180 62 L164 74 L174 82 L156 98', 3.2) }));
    G('wingFc', () => S(wf.cov.d, T.blue, { sh: 6, hl: 4, inner: stripes(wf.cov.lines, '#121a48', 1.8, 0.55) }));
    G('wingN', () => S(wn.prim.d, T.deep, { sh: 8, hl: 3, inner: stripes(wn.prim.lines, '#0a0e2a', 2.2, 0.6) + spark('M34 62 L50 74 L40 82 L58 98', 3.2) }));
    G('wingNc', () => S(wn.cov.d, T.blue, { sh: 6, hl: 4, inner: stripes(wn.cov.lines, '#121a48', 1.8, 0.55) }));
    // culottes de plumes, tarses épais, serres plantées
    G('legF', () => { S(`M112 176 C112 166 142 166 142 178 L136 204${fringe(136, 118, 206, 3, 7)} Z`, T.deep, { sh: 5, hl: 3 }); L([[[[127, 202], [127, 212], [127, 221]], 11, 10]], 'yel', { inner: stripes(['M123 208 l8 0', 'M123 214 l8 0'], '#8a5a10', 1.6, 0.6) }); foot(h, 127, 218, 1.6, T.yel); });
    G('legs', () => { S(`M74 176 C74 166 104 166 104 178 L98 204${fringe(98, 80, 206, 3, 7)} Z`, T.deep, { sh: 5, hl: 3 }); L([[[[89, 202], [89, 212], [89, 221]], 11, 10]], 'yel', { inner: stripes(['M85 208 l8 0', 'M85 214 l8 0'], '#8a5a10', 1.6, 0.6) }); foot(h, 89, 218, 1.6, T.yel); });
    G('body', () => {
      S('M72 134 C74 110 142 110 146 134 C152 160 140 188 108 198 C78 188 66 160 72 134 Z', T.blue, { sh: 11, hl: 7,
        inner: under('M88 132 C100 124 118 124 130 132 C134 156 126 178 108 190 C92 178 84 156 88 132 Z', '#dfe8f8', 0.9)
          + stripes(['M90 146 q9 8 18 0 q9 8 18 0', 'M92 160 q8 8 16 0 q8 8 16 0', 'M98 174 q5 6 10 0 q5 6 10 0'], '#8496c8', 2.2, 0.7) + spark('M114 132 L102 152 L114 152 L102 176', 3.6) });
      neck([108, 130], [114, 114], [124, 98], 48, 38, 'blue');
    });
    G('crest', () => at('translate(-16 2)', () => { for (const p of [[[134, 66], [118, 50], [92, 50]], [[140, 62], [130, 38], [108, 24]], [[150, 62], [150, 38], [138, 16]]]) S(h.limb(p, 13, 3, 14), T.gold, { sh: 3, hl: 3 }); }));
    G('head', () => at('translate(-16 2)', () => {
      // bec ouvert : le fond de la gueule d'abord, puis le bec entaillé, crochet vers le bas
      raw(`<path d="M177 90 L157 91 L176 104 C172 99 172 94 177 90 Z" fill="${MAW}"/>`);
      S('M150 64 C170 58 192 68 197 88 C198 96 195 103 190 108 C189 99 185 92 177 89 L157 91 L181 107 C173 114 160 112 150 104 Z', T.gold, { sh: 5, hl: 4, inner: '<path d="M186 72 C196 82 199 96 190 108 C189 99 185 92 179 89 Z" fill="#7a4a10" opacity="0.8"/>' });
      S('M120 84 C118 66 131 55 147 57 C161 59 170 71 168 85 C166 99 154 108 141 106 C129 104 121 96 120 84 Z', T.blue, { sh: 8, hl: 5, inner: under('M132 96 C142 90 156 92 166 90 C164 100 154 108 142 106 C136 104 132 100 132 96 Z', '#dfe8f8', 0.9) + '<path d="M122 78 C126 64 138 56 150 58 C158 60 164 66 166 72 C152 68 136 70 122 78 Z" fill="#1e2c64"/>' });
      eye(152, 79, 8.4, 7.6, { iris: BOLT, sclera: '#fff8c0', pupilK: 0.4, lid: 0.3, tilt: 1, lidC: '#141a3a' }); brow(153, 69, 24, 1, '#0a0e2a', 5.2);
    }));
  });
