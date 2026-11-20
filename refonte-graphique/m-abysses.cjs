// LES ABYSSES (eau) — créatures des grands fonds : corps sombres, lumières vivantes, dents en aiguilles.
// Règles (propriétaire, 20/11/2026) : une gueule ouverte est DÉCOUPÉE dans la silhouette (aucun trait devant la bouche) ;
// pattes, pinces, tiges et tentacules partent de SOUS le corps (dessinés avant lui), jamais posés dessus avec un contour.
// Niveau de la famille de référence (m-glaces.cjs) : chaque bête a son plan de corps (lame, globe, cloche, torpille),
// des nageoires à rayons, des ouïes, des pattes articulées, des pinces en deux doigts, un regard dur.
const { Mo, tone, metal } = require('./mon6.cjs');
const LUM = '#6ff0ff', LURE = '#ffe27a', MAW = '#1c0f1e';

/** Trois points presque alignés (a → b), légèrement arqués : un segment de patte. */
const seg = (a, b, bend = 0) => [a, [(a[0] + b[0]) / 2 - (b[1] - a[1]) * bend, (a[1] + b[1]) / 2 + (b[0] - a[0]) * bend], b];
/** Patte articulée de crustacé : cuisse, genou noueux, jambe effilée jusqu'à la pointe. */
const jleg = ({ S, limb, disc }, root, knee, foot, w, t, o = {}) => {
  S(limb(seg(root, knee, o.b0 ?? 0.08), w, w * 0.8, 14), t, { sh: 3, far: o.far });
  S(limb(seg(knee, foot, o.b1 ?? -0.05), w * 0.76, w * 0.26, 16), t, { sh: 3, far: o.far });
  S(disc(knee[0], knee[1], w * 0.58), t, { sh: 2, far: o.far });
};
/** Un ruban qui ondule : deux courbes bout à bout (5 points : départ, courbe, milieu, courbe, bout). */
const wavy = ({ S, limb }, p, w0, w1, t, o = {}) => { const wm = (w0 + w1) / 2; S(limb([p[0], p[1], p[2]], w0, wm, 16), t, o); S(limb([p[2], p[3], p[4]], wm, w1, 16), t, o); };

// 0 · rapide — Poisson-hache : un corps haut et mince comme une lame, un manche de queue, un œil énorme, des lumières sous la quille
Mo('abysses', 0, 'Poisson-hache', { scale: 0.92, atk: 'stab', wind: -8, hit: 10, colors: { body: metal('#a9c4d2'), fin: '#2f5f7a' }, grp: { tail: 'back', body: 'torso' }, piv: { back: [84, 148], torso: [120, 150] }, fx: LUM },
  ({ S, raw, T, G, halo, eye, brow, teeth, stripes, under }) => {
    const ph = [[154, 188, -32], [143, 201, -20], [129, 208, -4], [114, 205, 14], [103, 193, 28]];
    for (const [x, y] of ph) halo(x, y + 3, 9, LUM, 0.7);
    // le « manche » : un pédoncule mince, puis une queue fourchue
    G('tail', () => S('M90 136 C74 138 62 140 52 143 L20 112 C30 132 34 144 36 151 C34 160 30 174 18 196 L52 161 C64 160 76 162 90 162 Z', T.fin, { sh: 5,
      inner: stripes(['M50 146 L28 124', 'M48 150 L34 138', 'M48 156 L34 168', 'M50 160 L26 186'], '#14303f', 1.8, 0.55) }));
    G('body', () => {
      // dorsale en lame, anale sous le ventre : rayons visibles
      S('M98 110 L90 70 L112 92 L122 64 L136 92 L148 76 L152 100 Z', T.fin, { sh: 3, inner: stripes(['M100 106 L93 78', 'M118 98 L122 72', 'M142 96 L147 82'], '#14303f', 1.8, 0.55) });
      S('M100 176 L76 200 L92 194 L90 212 L110 198 Z', T.fin, { sh: 3, inner: stripes(['M98 182 L82 196', 'M102 190 L92 206'], '#14303f', 1.8, 0.55) });
      raw(`<path d="M176 124 L154 137 L171 146 C163 142 163 132 176 124 Z" fill="${MAW}"/>`);
      // la lame : dos droit, quille très profonde, bouche tournée vers le haut (mâchoire du bas en avant)
      S('M84 138 C90 120 100 106 114 100 L148 95 C162 96 172 108 176 124 L154 137 L176 149 C176 164 170 180 160 194 C151 208 139 217 127 217 C113 216 103 200 97 180 C93 168 90 162 84 160 Z', T.body, { sh: 10, hl: 7,
        inner: under('M80 140 C96 104 150 90 180 122 L182 80 L76 80 Z', '#1f4258', 0.7)
          + stripes(['M104 112 C100 140 102 168 110 196', 'M118 104 C114 140 116 176 124 210', 'M132 136 C130 164 132 190 138 210'], '#24465c', 1.6, 0.3)
          + '<path d="M126 136 C128 152 138 166 154 172" stroke="#17323f" stroke-width="2.6" fill="none" stroke-linecap="round" opacity="0.7"/><path d="M132 140 C134 152 142 162 152 166" stroke="#17323f" stroke-width="1.6" fill="none" opacity="0.4"/>'
          + '<path d="M170 152 C168 172 158 192 144 206" stroke="#fff" stroke-width="4" fill="none" opacity="0.45" stroke-linecap="round"/>'
          + '<path d="M162 178 C152 200 136 212 124 210 C112 208 104 196 98 180 L96 200 L128 222 L164 204 Z" fill="#17323f" opacity="0.55" filter="url(#g2)"/>' });
      teeth([174, 125.5], [157, 135.5], 3, 6, 1); teeth([173, 147.5], [157, 139], 3, -6, 1);
      // nageoire de poitrine, rabattue vers l'arrière
      S('M122 152 C106 156 96 170 96 186 C110 182 124 172 130 158 Z', T.fin, { sh: 3, inner: stripes(['M122 158 L102 180', 'M124 162 L110 180'], '#14303f', 1.6, 0.55) });
      // les organes lumineux, en rang le long de la quille
      for (const [x, y, a] of ph) raw(`<ellipse cx="${x}" cy="${y}" rx="4.2" ry="6.4" transform="rotate(${a} ${x} ${y})" fill="${LUM}" stroke="#17323f" stroke-width="1.4"/><circle cx="${x - 1}" cy="${y - 2}" r="1.5" fill="#fff"/>`);
      eye(140, 122, 14, 13, { iris: '#ffe14a', pupil: 'slit', lid: 0.36, tilt: 1, look: [3, 0] }); brow(140, 108, 28, 1, '#17323f', 5);
    });
  });

// 1 · costaud — Bernard-l'ermite : il a élu domicile dans un vieux casque de scaphandrier, et sa grosse pince fait le reste
Mo('abysses', 1, 'Bernard-l\'ermite au casque', { scale: 1.08, atk: 'smash', wind: -55, hit: 38, colors: { brass: metal('#c9903c'), crab: '#e0603a', dark: '#8a2f24', pale: '#f4c8a0' },
  swing: ['claw'], grp: { farLegs: 'legs', legs: 'legs', shell: 'torso', body: 'torso', eyes: 'head', farClaw: 'far' }, piv: { swing: [158, 180], far: [156, 190], head: [140, 160], torso: [106, 200] } },
  (h) => {
    const { S, raw, T, G, eye, brow, limb, disc, ell, spots, stripes } = h;
    G('farLegs', () => { jleg(h, [122, 188], [112, 204], [100, 227], 11, T.dark, { far: true }); jleg(h, [146, 190], [160, 204], [154, 227], 11, T.dark, { far: true }); });
    G('farClaw', () => { S(limb([[156, 188], [176, 204], [190, 200]], 13, 11), T.dark, { sh: 4, far: true }); S(limb([[186, 198], [202, 188], [212, 202]], 14, 3), T.dark, { sh: 3, far: true }); S(limb([[186, 206], [202, 214], [212, 206]], 9, 3), T.dark, { sh: 3, far: true }); });
    G('shell', () => {
      // casque de cuivre : robinet d'air, dôme bosselé, hublots grillagés, vert-de-gris, bernacles, collerette boulonnée
      S('M70 74 L72 58 L98 58 L100 74 Z', T.brass, { sh: 3, hl: 2, inner: '<path d="M72 64 L98 64" stroke="#8a5a1c" stroke-width="2" opacity="0.6"/>' });
      S('M36 96 L30 78 L44 74 L52 86 Z', h.TK('#d8d0b8'), { sh: 3, inner: '<path d="M36 80 L44 78" stroke="#5a5040" stroke-width="2.4" stroke-linecap="round"/>' });
      S(disc(84, 122, 54), T.brass, { sh: 12, hl: 8,
        inner: '<path d="M36 150 C52 138 60 150 74 160 C60 176 44 168 36 150 Z M100 70 C114 72 126 82 132 96 C120 96 108 88 100 70 Z" fill="#4fae96" opacity="0.6" filter="url(#g2)"/>'
          + '<path d="M84 68 C80 100 80 140 86 176" stroke="#8a5a1c" stroke-width="3" fill="none" opacity="0.45"/><path d="M32 132 C60 152 110 152 138 130" stroke="#8a5a1c" stroke-width="4" fill="none" opacity="0.4"/>'
          + '<path d="M58 88 C52 96 48 106 48 118" stroke="#fff3c0" stroke-width="5" fill="none" opacity="0.55" stroke-linecap="round"/>'
          + '<g fill="#d8d0b8" stroke="#5a5040" stroke-width="1.2"><circle cx="46" cy="96" r="5"/><circle cx="54" cy="86" r="3.6"/></g><g fill="#5a5040"><circle cx="46" cy="96" r="1.8"/><circle cx="54" cy="86" r="1.3"/></g>' });
      S(disc(66, 124, 26), T.brass, { sh: 5, hl: 3, inner: '<circle cx="66" cy="124" r="18" fill="#10303c"/><circle cx="72" cy="126" r="7" fill="#6ff0ff" opacity="0.25" filter="url(#g2)"/><path d="M57 108 L57 140 M66 106 L66 142 M75 108 L75 140 M49 124 L83 124" stroke="#c9903c" stroke-width="3.2"/><path d="M53 114 Q59 108 67 109" stroke="#6ff0ff" stroke-width="2.6" fill="none" opacity="0.6" stroke-linecap="round"/>'
        + [0, 60, 120, 180, 240, 300].map((a) => `<circle cx="${(66 + 22 * Math.cos(a * Math.PI / 180)).toFixed(1)}" cy="${(124 + 22 * Math.sin(a * Math.PI / 180)).toFixed(1)}" r="2" fill="#6e4414"/>`).join('') });
      S(disc(114, 96, 12), T.brass, { sh: 3, hl: 2, inner: '<circle cx="114" cy="96" r="7" fill="#10303c"/><path d="M109 93 Q113 89 118 91" stroke="#6ff0ff" stroke-width="2" fill="none" opacity="0.5" stroke-linecap="round"/>' });
      for (const [x, y] of [[102, 76], [130, 124], [38, 124], [42, 148]]) raw(`<circle cx="${x}" cy="${y}" r="3.4" fill="#8a5a1c"/><circle cx="${x - 1}" cy="${y - 1}" r="1.2" fill="#fff3c0"/>`);
      // la collerette : l'ouverture par où sort le crabe
      S(ell(120, 172, 42, 19), T.brass, { sh: 5, hl: 3, inner: '<ellipse cx="124" cy="175" rx="31" ry="11" fill="#22141c"/>' + [84, 96, 110].map((x, i) => `<circle cx="${x}" cy="${[168, 161, 157][i]}" r="2.4" fill="#6e4414"/>`).join('') });
    });
    // tout ce qui sort du crabe part de sous sa carapace : yeux par le haut, pattes par le bas, pince par le côté
    G('eyes', () => { S(limb([[130, 168], [128, 150], [132, 138]], 6.5, 6.5), T.crab, { sh: 2 }); S(limb([[148, 168], [152, 152], [156, 142]], 6, 6), T.dark, { sh: 2 });
      eye(133, 134, 9, 8.5, { iris: '#ffe14a', pupilK: 0.5, lid: 0.42, tilt: 1 }); eye(158, 138, 7.5, 7.5, { iris: '#ffe14a', pupilK: 0.5, lid: 0.42, tilt: -1 }); });
    G('legs', () => { jleg(h, [108, 188], [90, 200], [78, 227], 13, T.crab); jleg(h, [126, 192], [122, 208], [112, 227], 13, T.crab); jleg(h, [146, 192], [168, 204], [170, 227], 13, T.crab);
      raw('<g fill="#5a1c18"><path d="M74 219 L84 219 L77 228 Z M108 219 L118 219 L111 228 Z M165 219 L175 219 L171 228 Z"/></g>'); });
    G('claw', () => {
      // bras en deux articles, puis la pince : un doigt fixe en bas, une grosse main bombée et son doigt du haut, dentés à l'intérieur
      S(limb([[156, 182], [178, 178], [186, 160]], 18, 17), T.crab, { sh: 5 });
      S('M176 160 C186 150 198 152 206 158 C216 162 226 158 232 148 C234 166 220 182 200 180 C186 178 178 170 176 160 Z', T.dark, { sh: 4, inner: '<path d="M204 160 l3 -5 l4 6 l4 -5 l4 5" stroke="#f4c8a0" stroke-width="2.2" fill="none" stroke-linejoin="round" opacity="0.8"/>' });
      S('M170 154 C160 126 174 98 200 94 C222 92 238 108 238 130 C230 120 220 120 211 127 L207 121 L203 131 L197 127 L196 138 C190 142 188 150 190 160 C182 162 174 160 170 154 Z', T.crab, { sh: 8, hl: 6,
        inner: spots([[186, 116, 3], [198, 106, 2.4], [182, 132, 2.4], [208, 108, 2]], '#f4c8a0', 0.75) + '<path d="M176 140 C176 122 186 108 200 104" stroke="#fff" stroke-width="4" fill="none" opacity="0.3" stroke-linecap="round"/><path d="M226 112 C232 116 236 122 237 128" stroke="#5a1c18" stroke-width="3" fill="none" opacity="0.5" stroke-linecap="round"/>' });
      S(disc(182, 160, 12), T.crab, { sh: 4, inner: '<path d="M174 156 C180 152 186 152 190 156" stroke="#5a1c18" stroke-width="1.8" fill="none" opacity="0.5"/>' });
    });
    G('body', () => S('M96 178 C100 154 140 146 162 160 C176 170 176 190 164 198 C146 208 112 206 100 194 C94 188 94 184 96 178 Z', T.crab, { sh: 9, hl: 6,
      inner: h.under('M100 190 C122 202 150 200 168 186 L172 214 L96 214 Z', '#f4c8a0', 0.6) + stripes(['M110 160 C118 172 120 184 116 196', 'M128 154 C134 168 136 182 132 198'], '#8a2f24', 2.2, 0.45)
        + spots([[116, 168, 2.4], [140, 160, 2.6], [150, 172, 2]], '#f4c8a0', 0.7) + '<path d="M146 184 L149 197 L154 189 L159 197 L163 183 Z" fill="#5a1c18"/>' }));
  });

// 2 · tireur — Méduse : cloche penchée vers l'avant, côtes lumineuses, bras ourlés, un bras chargé de foudre
Mo('abysses', 2, 'Méduse', { atk: 'cast', fx: '#ff8ad8', colors: { bell: '#a45fd0', arm: '#e6a0e6', frill: '#ffc8ec', core: '#ffd0f4', dark: '#7a3fae' }, swing: ['arm'], grp: { tent: 'back', frills: 'torso', bell: 'head' }, piv: { swing: [136, 124], back: [96, 126], head: [106, 116], torso: [104, 150] }, shine: [[186, 156, 10, '#ff8ad8']], shineGrp: 'swing' },
  (h) => {
    const { S, raw, T, G, at, halo, eye, brow, limb, disc, stripes, spots } = h;
    halo(110, 92, 46, '#ff8ad8', 0.45);
    // les filaments traînent derrière elle
    G('tent', () => { wavy(h, [[70, 122], [40, 150], [50, 180], [60, 206], [34, 224]], 7, 2.5, T.arm, { sh: 3, so: 0.6 }); wavy(h, [[84, 126], [60, 160], [74, 190], [86, 212], [66, 226]], 7, 2.5, T.arm, { sh: 3, so: 0.6 });
      wavy(h, [[58, 116], [26, 132], [26, 164], [26, 190], [8, 204]], 6, 2, T.dark, { sh: 3, far: true }); wavy(h, [[122, 132], [128, 166], [112, 192], [100, 212], [112, 226]], 7, 2.5, T.arm, { sh: 3, so: 0.6 }); });
    // les bras de la bouche : deux rubans froncés
    G('frills', () => { for (const [x, y, k] of [[92, 124, -1], [112, 130, 1]]) S(`M${x - 10} ${y} C${x - 20} ${y + 22} ${x - 2} ${y + 34} ${x - 14} ${y + 52} C${x - 22} ${y + 66} ${x - 6} ${y + 76} ${x - 10 + 4 * k} ${y + 92} C${x + 6} ${y + 80} ${x + 20} ${y + 68} ${x + 10} ${y + 52} C${x + 22} ${y + 36} ${x + 4} ${y + 22} ${x + 12} ${y} Z`, T.frill, { sh: 4, so: 0.6,
      inner: stripes([`M${x} ${y + 6} C${x - 8} ${y + 26} ${x + 6} ${y + 40} ${x - 2} ${y + 58} C${x - 8} ${y + 70} ${x + 2} ${y + 78} ${x - 2} ${y + 88}`], '#d870c8', 2.4, 0.6) }); });
    // le bras qui tire : il descend de sous la cloche puis se recourbe vers l'avant
    G('arm', () => { S(limb([[140, 124], [146, 186], [184, 160]], 12, 7, 18), T.arm, { sh: 3 }); S(disc(186, 156, 9.5), T.core, { sh: 2, hl: 3 }); });
    G('bell', () => at('rotate(12 106 116)', () => {
      S('M46 126 C38 76 70 48 106 48 C142 48 172 76 164 126 C158 116 150 132 140 124 C132 116 124 132 114 124 C106 116 98 132 88 124 C80 116 72 132 62 124 C56 118 50 124 46 126 Z', T.bell, { sh: 11, hl: 8, so: 0.75,
        inner: '<path d="M40 130 C56 102 154 102 170 130 L170 100 C150 92 60 92 40 100 Z" fill="#4a2478" opacity="0.5" filter="url(#g3)"/>'
          + stripes(['M106 50 C80 60 60 90 58 122', 'M106 50 C94 70 86 96 88 122', 'M106 50 C114 70 118 96 114 122', 'M106 50 C132 62 144 92 140 122'], '#ffd0f4', 2.4, 0.4)
          + '<g fill="#ffd0f4" opacity="0.6" filter="url(#g2)"><ellipse cx="92" cy="74" rx="10" ry="7" transform="rotate(-30 92 74)"/><ellipse cx="118" cy="72" rx="10" ry="7" transform="rotate(30 118 72)"/><ellipse cx="88" cy="90" rx="8" ry="5"/><ellipse cx="124" cy="88" rx="8" ry="5"/></g>'
          + '<path d="M62 106 C62 86 74 68 92 60" stroke="#fff" stroke-width="5" fill="none" opacity="0.5" stroke-linecap="round"/>' + spots([[140, 76, 3.4], [150, 90, 2.6], [130, 64, 2.4]], '#ffd0f4', 0.7) });
      eye(112, 106, 11, 8, { sclera: '#fff6a8', iris: '#ff8a20', pupil: 'slit', lid: 0.4, tilt: 1, lidC: '#34185a' }); eye(140, 106, 8.5, 7, { sclera: '#fff6a8', iris: '#ff8a20', pupil: 'slit', lid: 0.4, tilt: -1, lidC: '#34185a' });
      brow(111, 96, 26, 1, '#34185a', 5); brow(141, 97, 20, -1, '#34185a', 4.5);
    }));
  });

// 3 · sorts — Baudroie : un globe sombre et verruqueux, une lanterne au bout du front, la mâchoire du bas en avant, pleine d'aiguilles
Mo('abysses', 3, 'Baudroie à lanterne', { atk: 'cast', fx: LURE, colors: { body: '#3c3f5e', fin: '#252a4a', lure: '#fff3a8' }, swing: ['lure'], grp: { tail: 'back', body: 'torso' }, piv: { swing: [112, 100], back: [42, 156], torso: [106, 156] }, shine: [[178, 78, 12, LURE]], shineGrp: 'swing' },
  ({ S, raw, T, G, halo, eye, brow, teeth, limb, disc, stripes, spots, under }) => {
    halo(178, 78, 22, LURE, 0.85);
    G('tail', () => S('M52 148 C40 142 30 132 18 116 C22 138 22 150 14 158 C22 168 22 182 16 200 C30 186 42 176 54 168 Z', T.fin, { sh: 5, inner: stripes(['M46 152 L24 130', 'M44 158 L22 158', 'M46 164 L22 188'], '#12142c', 2, 0.6) }));
    // la tige de la lanterne sort de derrière le front
    G('lure', () => { S(limb([[112, 102], [124, 40], [174, 70]], 7, 3.5, 18), T.fin, { sh: 2 }); S(disc(178, 78, 10), T.lure, { sh: 2, hl: 4, inner: '<circle cx="178" cy="78" r="5" fill="#fff" opacity="0.7"/>' }); });
    G('body', () => {
      // épines du dos, nageoire du ventre
      S('M62 110 L50 80 L72 96 L74 66 L90 92 L98 72 L106 96 Z', T.fin, { sh: 3, inner: stripes(['M64 104 L54 86', 'M78 96 L75 74', 'M96 94 L98 78'], '#12142c', 1.8, 0.6) });
      S('M70 196 L54 222 L74 212 L80 226 L92 206 Z', T.fin, { sh: 3 });
      raw(`<path d="M170 126 L112 150 L176 170 C154 164 152 142 170 126 Z" fill="${MAW}"/><path d="M130 150 C138 146 148 149 152 156 C146 161 136 161 130 156 Z" fill="#b8485a"/>`);
      // la gueule : une encoche jusqu'au coin de la bouche, la mâchoire du bas dépasse ; rien ne la referme devant
      S('M38 154 C34 116 66 90 104 90 C134 90 158 104 170 126 L116 150 L182 170 C184 180 180 192 170 200 C154 212 130 216 106 216 C70 216 40 194 38 154 Z', T.body, { sh: 11, hl: 7,
        inner: under('M48 190 C80 212 136 214 178 184 L184 222 L42 222 Z', '#7a7ea6', 0.6)
          + spots([[60, 132, 4.5], [78, 116, 3.4], [98, 106, 3], [54, 158, 3.4], [76, 150, 2.6], [150, 196, 3], [128, 204, 2.4], [96, 190, 3]], '#1c1e3a', 0.6)
          + '<path d="M104 132 C98 146 98 164 106 178" stroke="#12142c" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.6"/><path d="M112 136 C108 148 108 160 114 172" stroke="#12142c" stroke-width="1.8" fill="none" opacity="0.4"/>'
          + '<path d="M120 152 C140 164 164 170 182 172" stroke="#12142c" stroke-width="2.4" fill="none" opacity="0.5"/><path d="M64 122 L80 112 M58 140 L70 134" stroke="#8a8eb6" stroke-width="2" stroke-linecap="round" opacity="0.6"/>' });
      teeth([168, 127.5], [122, 147.5], 5, 15, 1); teeth([178, 169], [122, 152.5], 5, -17, 1);
      // nageoire de poitrine : un moignon à rayons
      S('M88 170 C72 172 62 184 62 200 C76 198 90 190 96 176 Z', T.fin, { sh: 3, inner: stripes(['M86 176 L68 194', 'M90 180 L78 196'], '#12142c', 1.8, 0.6) });
      eye(136, 112, 8.5, 8, { iris: '#ffe14a', pupilK: 0.45, lid: 0.46, tilt: 1 }); brow(136, 102, 24, 1, '#12142c', 5.5);
    });
  });

// 4 · élite — Crabe-araignée : carapace en poire hérissée, perchée sur d'immenses pattes articulées, pinces fines dressées
Mo('abysses', 4, 'Crabe-araignée', { scale: 1.16, atk: 'stab', wind: -34, hit: 30, colors: { shell: '#d8552e', leg: '#e88a4a', dark: '#8a3a22', pale: '#ffd9b0' }, swing: ['claws'], grp: { farLegs: 'legs', legs: 'legs', shell: 'torso', farClaw: 'far' }, piv: { swing: [140, 134], far: [110, 108], torso: [106, 150] } },
  (h) => {
    const { S, raw, T, G, eye, brow, limb, disc, spots, stripes, under } = h;
    G('farLegs', () => { jleg(h, [92, 132], [60, 60], [38, 227], 8, T.dark, { far: true }); jleg(h, [118, 134], [150, 58], [168, 227], 8, T.dark, { far: true }); });
    G('farClaw', () => { S(limb([[108, 110], [124, 86], [112, 62]], 9, 7), T.dark, { sh: 3, far: true }); S(limb([[114, 66], [96, 46], [110, 28]], 11, 2.5), T.dark, { sh: 3, far: true }); S(limb([[112, 64], [124, 48], [118, 32]], 7, 2.5), T.dark, { sh: 3, far: true }); });
    G('legs', () => { jleg(h, [80, 138], [26, 78], [10, 227], 10, T.leg); jleg(h, [90, 146], [54, 110], [48, 227], 10, T.leg); jleg(h, [114, 150], [140, 120], [146, 227], 10, T.leg); jleg(h, [126, 148], [188, 118], [200, 227], 10, T.leg, { b0: -0.06 }); });
    // la pince part de sous le bord de la carapace, loin des yeux : bras, avant-bras dressé, deux doigts fins
    G('claws', () => { S(limb([[140, 136], [164, 128], [178, 108]], 12, 10), T.leg, { sh: 3 }); S(limb([[178, 108], [186, 86], [178, 66]], 11, 12), T.shell, { sh: 4 });
      S(limb([[176, 70], [164, 44], [184, 22]], 13, 2.5, 18), T.shell, { sh: 4, inner: '<path d="M172 54 l5 -2 M172 44 l5 -3 M176 34 l4 -3" stroke="#ffd9b0" stroke-width="2" stroke-linecap="round" opacity="0.8"/>' });
      S(limb([[182, 70], [198, 54], [194, 30]], 8, 2.5, 18), T.shell, { sh: 3 }); S(disc(178, 108, 7.5), T.leg, { sh: 2 }); S(disc(179, 68, 8.5), T.shell, { sh: 3 }); });
    G('shell', () => {
      // deux cornes de rostre au-dessus des yeux, des épines sur le dos
      S('M64 132 C60 112 68 98 80 92 L70 70 L92 88 C96 87 100 86 104 86 L104 62 L116 88 C122 90 128 93 132 98 L150 76 L142 106 L166 96 L148 118 C150 124 150 132 148 138 C144 152 128 162 108 162 C86 162 68 152 64 132 Z', T.shell, { sh: 10, hl: 6,
        inner: under('M70 148 C90 166 130 166 150 144 L152 170 L66 170 Z', '#ffd9b0', 0.5) + spots([[82, 110, 4], [96, 102, 3], [78, 128, 3], [92, 122, 2.4], [70, 118, 2.2], [100, 136, 2.4], [86, 142, 2]], '#ffd9b0', 0.8)
          + stripes(['M74 100 C86 96 100 96 112 100', 'M70 136 C78 146 90 152 104 154'], '#8a3a22', 2.2, 0.45) + '<path d="M118 146 L121 158 L126 150 L131 158 L135 145 Z" fill="#5a1c12"/>' });
      eye(116, 126, 9.5, 9, { iris: '#ffe14a', pupilK: 0.5, lid: 0.42, tilt: 1 }); eye(137, 126, 7, 8, { iris: '#ffe14a', pupilK: 0.5, lid: 0.42, tilt: -1 });
      brow(115, 115, 24, 1, '#5a1c12', 5); brow(138, 116, 16, -1, '#5a1c12', 4.5);
    });
  });

// 5 · boss — Calmar colossal : manteau en torpille penché en arrière, il se dresse sur ses bras, un tentacule à crochets prêt à frapper
Mo('abysses', 5, 'Calmar colossal', { scale: 1.34, atk: 'smash', wind: -46, hit: 40, colors: { skin: '#b8323e', dark: '#7c1c2c' }, swing: ['whip'], grp: { farWhip: 'far', arms: 'legs', head: 'torso' }, piv: { swing: [128, 148], far: [114, 142], torso: [106, 170] } },
  (h) => {
    const { S, raw, T, G, eye, brow, limb, disc, ell, spots, stripes, under } = h;
    const suck = (pts, n) => { let s = ''; for (let i = 1; i <= n; i++) { const t = i / (n + 1), u = 1 - t, x = u * u * pts[0][0] + 2 * u * t * pts[1][0] + t * t * pts[2][0], y = u * u * pts[0][1] + 2 * u * t * pts[1][1] + t * t * pts[2][1]; s += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${(3.6 - t * 1.6).toFixed(1)}" fill="#f0b8a8" opacity="0.85"/><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${(1.5 - t * 0.6).toFixed(1)}" fill="#7c1c2c" opacity="0.7"/>`; } return s; };
    G('farWhip', () => { const p = [[114, 142], [156, 96], [198, 112]]; S(limb(p, 10, 6, 18), T.dark, { sh: 3, far: true }); S('M190 104 C198 96 212 98 218 110 C214 120 200 124 192 118 Z', T.dark, { sh: 3, far: true }); });
    // bras et tentacule partent de sous la tête : elle recouvre leur attache ; les pointes se recourbent
    G('arms', () => {
      for (const p of [[[94, 142], [44, 162], [16, 216]], [[122, 142], [170, 166], [196, 216]]]) S(limb(p, 16, 4, 18), T.dark, { sh: 4, far: true });
      for (const p of [[[86, 144], [56, 190], [30, 222]], [[98, 146], [84, 204], [66, 226]], [[110, 146], [110, 206], [102, 227]], [[122, 144], [136, 202], [142, 227]], [[130, 142], [160, 190], [176, 224]]]) S(limb(p, 18, 5, 18), T.skin, { sh: 4, inner: suck(p, 5) });
      for (const p of [[[32, 222], [22, 232], [12, 218]], [[176, 224], [190, 232], [196, 216]]]) S(limb(p, 6, 2.5), T.skin, { sh: 2 });
    });
    G('whip', () => { const p = [[124, 146], [196, 138], [172, 62]]; S(limb(p, 12, 7, 20), T.skin, { sh: 4, inner: suck(p, 6) });
      // la massue : des crochets au lieu de ventouses
      S('M160 66 C154 46 164 26 178 18 C190 30 192 52 182 70 C176 76 164 74 160 66 Z', T.skin, { sh: 4, inner: '<path d="M164 62 C162 48 168 34 176 26 C182 36 182 52 176 66 Z" fill="#f0b8a8" opacity="0.85"/><g fill="#5a1220"><path d="M166 56 l8 -2 l-6 6 Z M168 44 l8 -2 l-6 6 Z M172 34 l7 -1 l-5 5 Z"/></g>' }); });
    G('head', () => {
      // les deux nageoires en pointe de flèche, au bout du manteau
      S('M70 52 C46 30 26 40 22 64 C36 58 54 64 66 80 Z', T.skin, { sh: 5, inner: stripes(['M62 56 L32 52', 'M64 64 L40 60'], '#7c1c2c', 2, 0.45) }); S('M112 44 C136 24 156 34 160 58 C146 52 130 56 122 70 Z', T.dark, { sh: 5, far: true });
      // le manteau et la tête d'une seule forme : pas de trait entre les deux
      S('M86 4 C112 22 148 68 144 104 C148 112 148 124 146 132 C142 148 126 158 108 158 C90 158 74 148 71 132 C69 124 68 112 70 104 C56 70 66 26 86 4 Z', T.skin, { sh: 12, hl: 8,
        inner: under('M60 96 C62 60 70 30 86 6 L50 6 L50 110 Z', '#f0b8a8', 0.35)
          + '<path d="M70 104 C90 116 126 116 144 103" stroke="#5a1220" stroke-width="3" fill="none" opacity="0.55" stroke-linecap="round"/><path d="M72 110 C92 121 124 121 143 109" stroke="#f0b8a8" stroke-width="2" fill="none" opacity="0.35"/>'
          + spots([[112, 50, 4.5], [124, 74, 3.6], [106, 84, 3], [128, 94, 2.6], [98, 62, 2.4], [116, 30, 2.6], [90, 92, 2]], '#6e1c2c', 0.5)
          + '<path d="M84 94 C78 66 82 42 90 22" stroke="#f0b8a8" stroke-width="6" fill="none" opacity="0.4" stroke-linecap="round"/><g fill="none" stroke="#f0b8a8" stroke-width="1.8" opacity="0.5"><circle cx="126" cy="56" r="5"/><circle cx="110" cy="70" r="4"/></g>' });
      eye(100, 131, 15, 14, { iris: '#ffe14a', pupilK: 0.5, lid: 0.36, tilt: 1 }); eye(133, 130, 9.5, 11, { iris: '#ffe14a', pupilK: 0.5, lid: 0.36, tilt: -1 });
      brow(99, 114, 34, 1, '#4a0f1c', 6); brow(134, 116, 20, -1, '#4a0f1c', 5);
    });
  });
