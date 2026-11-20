// LES IDOLES D'AIRAIN (feu) — d'antiques statues de bronze chauffées au rouge : métal, vert-de-gris, feu intérieur.
// Construction visible : plaques, rivets, gravures en volute, patine, fissures rougeoyantes. Gueule ouverte découpée
// dans la silhouette, membres attachés sous le corps, un seul contour (voir LISEZMOI, « Les monstres »).
const { Mo, metal } = require('./mon6.cjs');
const BR = metal('#b87a3a'), BRD = metal('#7a4a22'), HOT = '#ff8a2a', VERD = '#5fb89a', MAW = '#2a0f14', BONE = '#f4d8a0';
const seams = (d) => `<path d="${d}" stroke="#5a3214" stroke-width="2.4" fill="none" opacity="0.6" stroke-linecap="round"/>`;
const hot = (d) => `<path d="${d}" fill="${HOT}" opacity="0.85"/><path d="${d}" fill="#ffe27a" opacity="0.6" filter="url(#g2)"/>`;
const crack = (d) => `<path d="${d}" stroke="${HOT}" stroke-width="6" fill="none" opacity="0.5" filter="url(#g2)" stroke-linecap="round"/><path d="${d}" stroke="#ffe27a" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
const rivets = (pts, r = 2.4) => pts.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="${r}" fill="#5a3214"/><circle cx="${x + 0.7}" cy="${y - 0.7}" r="${r * 0.42}" fill="${BONE}" opacity="0.8"/>`).join('');
const patina = (d, op = 0.5) => `<path d="${d}" fill="${VERD}" opacity="${op}" filter="url(#g2)"/>`;
const curl = (x, y, r) => `<path d="M${x - r} ${y} a${r} ${r} 0 1 1 ${r} ${r} a${r * 0.55} ${r * 0.55} 0 1 1 ${-r * 0.55} ${-r * 0.55}" stroke="#5a3214" stroke-width="2.4" fill="none" opacity="0.7" stroke-linecap="round"/>`;

// 0 · rapide — Chien de bronze : un chien-lion gardien de temple, crinière en volutes, grelot au cou
Mo('idoles', 0, 'Chien de bronze', { atk: 'slash', wind: -14, hit: 20, colors: { br: BR, dark: BRD }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [124, 160], back: [50, 160], torso: [88, 196] } },
  ({ S, raw, T, G, beast, neck, brow, eye, teeth, disc }) => {
    const legs = beast({ front: 114, hind: 56, top: 188, w: 19, t: 'br', dark: 'dark', claws: true, clawC: BONE });
    G('tail', () => S('M48 168 C22 164 10 138 22 120 C32 104 54 106 58 124 C60 134 50 140 43 134 C44 146 52 154 62 158 Z', T.dark, { sh: 4, hl: 3, inner: curl(38, 126, 8) }));
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      S('M40 178 C38 156 58 146 84 146 C104 144 118 136 130 140 C142 146 144 164 140 180 C136 198 114 206 86 206 C58 206 42 198 40 178 Z', T.br, { sh: 10, hl: 6,
        inner: patina('M46 162 C60 148 86 146 104 146 C86 154 62 160 50 174 Z') + seams('M76 150 C72 170 74 190 80 204') + curl(58, 180, 9) + rivets([[86, 156], [88, 172], [90, 188]]) + crack('M98 176 L106 186 L102 196') });
      neck([114, 160], [130, 150], [146, 150], 50, 44, 'br');
      S(disc(132, 196, 9), T.dark, { sh: 3, hl: 2, inner: hot('M126 197 L138 197 L136 201 L128 201 Z') });
    });
    G('head', () => {
      S('M160 112 C158 98 164 88 172 84 C178 94 176 106 172 114 Z', T.dark, { sh: 3 });
      // la crinière : un seul bloc festonné, gravé de volutes
      S('M152 96 C146 82 128 82 124 94 C110 92 102 106 108 116 C96 122 94 138 102 144 C92 152 94 168 104 172 C100 184 110 194 124 190 L152 150 Z', T.dark, { sh: 5, hl: 3, inner: curl(136, 98, 6) + curl(118, 110, 6) + curl(108, 132, 6) + curl(108, 158, 6) + curl(116, 180, 6) });
      S('M136 114 C128 102 130 90 138 86 C146 94 148 106 146 114 Z', T.br, { sh: 3 });
      raw(`<path d="M193 153 L150 161 L182 176 C168 173 168 161 193 153 Z" fill="${MAW}"/>` + hot('M152 163 C162 159 172 163 178 171 C170 175 160 175 152 169 Z'));
      S('M114 146 C112 122 128 106 150 106 C164 106 174 112 180 120 C190 120 198 128 198 138 C198 144 196 149 193 152 L154 160 L186 177 C178 188 162 192 146 190 C128 188 114 170 114 146 Z', T.br, { sh: 9, hl: 6,
        inner: patina('M118 130 C122 116 134 108 146 108 C136 116 128 128 124 142 Z') + '<path d="M186 124 C192 122 198 128 197 134 C191 136 186 130 186 124 Z" fill="#5a3214"/>' + seams('M172 118 C178 126 178 138 172 146') + rivets([[126, 162], [132, 176]]) });
      teeth([189, 153], [158, 159.5], 4, 7, 1, BONE); teeth([181, 176], [158, 163], 3, -6, 1, BONE);
      eye(156, 132, 10, 8.5, { sclera: '#ffe27a', iris: HOT, pupilK: 0.45, lid: 0.44, tilt: 1, lidC: '#5a3214' }); brow(156, 121, 28, 1, '#5a3214', 6);
    });
  });

// 1 · costaud — Taureau d'airain : il charge tête basse, un brasier dans son ventre creux
Mo('idoles', 1, 'Taureau d\'airain', { scale: 1.12, atk: 'smash', wind: -16, hit: 22, fx: HOT, colors: { br: BR, dark: BRD }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [126, 152], back: [32, 146], torso: [86, 196] }, shine: [[78, 168, 13, HOT]] },
  ({ S, raw, T, G, L, beast, neck, brow, halo, eye, limb }) => {
    const legs = beast({ front: 108, hind: 52, top: 186, w: 23, t: 'br', dark: 'dark', hoof: true, hoofT: '#5a3214' });
    halo(78, 168, 26, HOT, 0.7);
    G('tail', () => { L([[[[32, 146], [8, 138], [14, 104]], 8, 5]], 'dark'); S('M8 108 C0 96 4 80 16 70 C26 82 28 98 22 110 Z', T.br, { sh: 2 }); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      // la cheminée du brasier
      S('M52 126 L54 96 L78 96 L80 122 Z', T.dark, { sh: 3, inner: hot('M56 96 L76 96 L74 103 L58 103 Z') });
      S('M28 166 C26 134 52 116 84 114 C104 104 128 110 138 128 C146 142 146 162 140 178 C134 196 114 204 86 204 C54 204 30 194 28 166 Z', T.br, { sh: 12, hl: 8,
        inner: patina('M36 138 C52 120 90 112 116 112 C92 120 62 126 44 148 Z') + seams('M48 128 C42 150 44 178 52 198 M110 112 C120 138 120 174 110 200') + rivets([[38, 156], [38, 172], [42, 188], [102, 120], [108, 136], [110, 152]])
          + '<path d="M60 150 L96 150 L96 186 L60 186 Z" fill="#2a0f14"/>' + hot('M66 184 C62 170 72 166 74 156 C80 164 84 158 86 152 C92 164 94 174 90 184 Z') + '<g stroke="#5a3214" stroke-width="3.4" fill="none"><path d="M60 150 L96 150 L96 186 L60 186 Z"/><path d="M72 150 L72 186 M84 150 L84 186"/></g>' + rivets([[56, 156], [56, 180]], 3) });
      neck([118, 146], [134, 148], [148, 156], 64, 56, 'br', { inner: seams('M128 124 C136 140 136 164 128 182') });
    });
    G('head', () => {
      // cornes courtes et épaisses, sur les côtés du crâne, recourbées vers l'avant et le haut
      S(limb([[162, 128], [184, 106], [206, 84]], 15, 4, 14), T.dark, { sh: 4, far: true }); S(limb([[140, 136], [146, 98], [180, 80]], 19, 4, 14), T.br, { sh: 4, hl: 3, inner: seams('M140 116 l14 4 M148 102 l12 8') });
      S('M132 142 C120 132 108 134 104 142 C112 152 124 154 132 152 Z', T.dark, { sh: 3 });
      raw('<path d="M190 195 a9 10 0 1 0 14 -2" stroke="#3a2416" stroke-width="7" fill="none" stroke-linecap="round"/><path d="M190 195 a9 10 0 1 0 14 -2" stroke="#d09a50" stroke-width="3.6" fill="none" stroke-linecap="round"/>');
      halo(206, 168, 13, HOT, 0.6);
      // front lourd, mufle court et carré
      S('M124 152 C122 134 134 122 150 122 C162 120 174 124 182 134 L196 146 C204 150 208 158 208 168 L206 184 C204 192 198 196 190 196 L164 196 C146 198 130 188 126 172 C124 164 124 158 124 152 Z', T.br, { sh: 11, hl: 7,
        inner: seams('M180 146 C176 162 176 180 180 196') + rivets([[138, 132], [150, 128], [162, 130]]) + '<ellipse cx="198" cy="166" rx="6" ry="5" fill="#5a3214"/>' + hot('M194 166 C196 162 202 162 203 166 C202 170 196 170 194 166 Z') + '<path d="M206 184 C198 181 190 183 184 190" stroke="#5a3214" stroke-width="2.6" fill="none" stroke-linecap="round"/>' + crack('M134 164 L142 172 L138 182') });
      eye(156, 150, 9.5, 8, { sclera: '#ffe27a', iris: HOT, pupilK: 0.45, lid: 0.48, tilt: 1, lidC: '#5a3214' }); brow(156, 139, 28, 1, '#5a3214', 6.5);
    });
  });

// 2 · tireur — Archer de bronze : une statue sur son socle, qui bande son arc sans jamais se lasser
Mo('idoles', 2, 'Archer de bronze', { atk: 'shoot', fx: HOT, colors: { br: BR, dark: BRD }, swing: ['bow', 'armN'], grp: { quiver: 'back', base: 'legs', body: 'torso' }, piv: { swing: [92, 126], back: [80, 130], head: [110, 104], torso: [106, 200] } },
  ({ S, raw, T, TK, G, L, eye, limb, disc, bar }) => {
    G('quiver', () => { S('M62 96 L60 72 L68 84 L74 66 L80 84 L88 70 L88 96 Z', TK(BONE), { sh: 2 }); S('M58 92 L92 88 L100 150 L78 156 Z', T.dark, { sh: 4, inner: seams('M64 104 L92 100') + rivets([[70, 102], [84, 100]]) }); });
    G('base', () => {
      S('M60 206 L152 206 L160 228 L52 228 Z', T.dark, { sh: 5, inner: seams('M56 216 L156 216') + patina('M56 222 C80 214 110 214 130 222 L130 230 L56 230 Z') + crack('M132 208 L138 216 L134 226') });
      L([[[[94, 180], [92, 196], [92, 208]], 17, 16], [[[120, 180], [124, 196], [122, 208]], 17, 16]], 'br', { inner: seams('M84 196 L102 196 M114 196 L132 196') });
    });
    G('body', () => {
      S('M80 164 L136 164 L144 196 L132 190 L126 200 L116 190 L108 200 L100 190 L90 200 L84 190 L72 196 Z', T.dark, { sh: 4, inner: seams('M94 168 L92 190 M108 168 L108 192 M122 168 L124 190') });
      S('M78 132 C76 114 90 106 108 106 C126 106 140 114 138 132 L134 168 C132 176 86 176 82 168 Z', T.br, { sh: 9, hl: 6,
        inner: patina('M112 110 C124 108 136 114 138 126 C128 130 118 124 112 110 Z') + seams('M108 112 L108 168 M92 138 C100 144 116 144 124 138 M84 160 L132 160') + crack('M96 118 L104 128 L98 138') + rivets([[88, 166], [108, 168], [128, 166]]) });
    });
    // l'arc passe devant le torse ; la main qui tire la corde est au creux de la poitrine
    G('bow', () => { raw(`<path d="M158 66 L124 128 L158 190" stroke="${BONE}" stroke-width="1.8" fill="none"/>`); S(limb([[158, 64], [198, 128], [158, 192]], 9, 9, 18), T.dark, { sh: 3, inner: seams('M176 86 l8 -4 M176 170 l8 4') }); S(bar([120, 128], [198, 128], 3.5), T.br, { sh: 1 }); S('M212 128 L196 119 L196 137 Z', T.br, { sh: 2 }); S(disc(122, 129, 8.5), T.dark, { sh: 3 }); });
    G('armN', () => { L([[[[94, 126], [136, 144], [178, 130]], 15, 12]], 'br', { inner: seams('M150 132 l4 12 M160 130 l4 12') }); S(disc(180, 129, 9.5), T.br, { sh: 3 }); S(disc(92, 122, 14), T.dark, { sh: 4, hl: 3, inner: curl(92, 122, 6) }); });
    G('head', () => {
      S('M82 64 L78 40 L90 50 L94 28 L104 44 L112 22 L120 42 L132 30 L130 50 L142 46 L136 66 Z', T.dark, { sh: 4, inner: patina('M90 50 L96 34 L104 48 Z') });
      S('M86 84 C84 66 96 56 110 56 C124 56 136 66 134 84 C134 100 124 110 110 110 C96 110 86 100 86 84 Z', T.br, { sh: 8, hl: 5, inner: '<path d="M100 100 C106 97 116 97 122 100" stroke="#5a3214" stroke-width="2.6" fill="none" stroke-linecap="round"/>' });
      eye(97, 84, 7, 6, { sclera: '#ffe27a', iris: HOT, pupil: 'none', irisK: 0.6, lid: 0.46, tilt: 1, lidC: '#5a3214' }); eye(124, 84, 6, 6, { sclera: '#ffe27a', iris: HOT, pupil: 'none', irisK: 0.6, lid: 0.46, tilt: -1, lidC: '#5a3214' });
      // le casque : calotte, protège-nez, garde-joue
      S('M82 82 C78 58 94 48 110 48 C128 48 142 58 138 80 L130 74 L115 74 L113 92 L107 92 L105 74 L90 74 C88 84 88 94 92 102 C86 98 82 90 82 82 Z', T.dark, { sh: 4, hl: 3, inner: rivets([[92, 62], [110, 56], [128, 62]]) });
    });
  });

// 3 · sorts — Porteuse d'encens : sa fumée referme les fissures du bronze
Mo('idoles', 3, 'Porteuse d\'encens', { atk: 'cast', heal: true, fx: '#bfe8d8', colors: { br: BR, dark: BRD, veil: metal('#9a6634') }, swing: ['censer'], grp: { skirt: 'legs', body: 'torso' }, piv: { swing: [124, 130], head: [106, 104], torso: [106, 200] }, shine: [[170, 168, 9, HOT]], shineGrp: 'swing' },
  ({ S, raw, T, G, L, glow, halo, disc, ell }) => {
    halo(170, 168, 14, HOT, 0.8);
    G('skirt', () => S('M74 150 C70 180 62 206 54 228 L158 228 C150 206 142 180 138 150 Z', T.br, { sh: 9, hl: 6,
      inner: seams('M88 156 C84 184 80 208 78 226 M106 156 L106 226 M124 156 C128 184 132 208 134 226') + '<path d="M68 182 C90 192 122 192 144 182" stroke="#5a3214" stroke-width="3.4" fill="none" opacity="0.7"/>' + rivets([[78, 192], [96, 196], [116, 196], [134, 192]]) + `<path d="M56 218 L156 218" stroke="${VERD}" stroke-width="8" opacity="0.55"/>` + patina('M70 160 C76 176 72 196 64 210 L58 210 Z') }));
    // l'encensoir pend à ses chaînes ; le bras qui le tient part de sous l'épaule
    G('censer', () => {
      raw('<path d="M158 126 L160 150 M158 126 L180 150" stroke="#7a4a22" stroke-width="2.6" fill="none"/>');
      glow('<g fill="#f4fff8" opacity="0.85" filter="url(#g3)"><circle cx="176" cy="136" r="8"/><circle cx="188" cy="118" r="11"/><circle cx="178" cy="96" r="9"/><circle cx="190" cy="78" r="6"/></g>');
      S('M158 152 C160 140 180 140 182 152 Z', T.dark, { sh: 2 });
      S(ell(170, 166, 16, 15), T.dark, { sh: 4, hl: 3, inner: hot('M158 160 L182 160 L180 166 L160 166 Z') + hot('M162 172 L178 172 L176 177 L164 177 Z') + rivets([[170, 154]]) });
      L([[[[124, 130], [146, 140], [158, 126]], 13, 11]], 'br'); S(disc(158, 124, 7.5), T.br, { sh: 3 });
    });
    G('body', () => S('M80 128 C78 112 92 106 106 106 C120 106 134 112 132 128 L138 156 C120 164 92 164 74 156 Z', T.br, { sh: 8, hl: 5,
      inner: '<path d="M86 118 C94 134 118 134 126 118" stroke="#5a3214" stroke-width="3" fill="none" opacity="0.7"/>' + `<circle cx="106" cy="136" r="6.5" fill="${VERD}" opacity="0.85"/>` + seams('M80 148 C96 156 116 156 132 148') + rivets([[84, 152], [106, 156], [128, 152]]) }));
    G('head', () => {
      // voile drapé sur les épaules, diadème à trois pointes, visage serein
      S('M84 60 C66 82 62 112 70 136 L142 136 C150 112 146 82 128 60 Z', T.veil, { sh: 5, hl: 4,
        inner: seams('M78 80 C70 98 70 118 76 134 M88 108 C84 118 84 128 88 136 M134 80 C142 98 142 118 136 134 M124 108 C128 118 128 128 124 136') + `<path d="M68 132 L144 132" stroke="${VERD}" stroke-width="7" opacity="0.6"/>` + rivets([[80, 132], [106, 132], [132, 132]], 2) });
      S('M86 58 L84 28 L98 42 L106 14 L114 42 L128 28 L126 58 Z', T.dark, { sh: 3, hl: 2, inner: `<circle cx="106" cy="38" r="5" fill="${VERD}" opacity="0.9"/>` });
      S('M79 84 C75 60 91 47 106 47 C121 47 137 60 133 84 C133 102 121 113 106 113 C91 113 79 102 79 84 Z', T.br, { sh: 8, hl: 5, inner: '<path d="M77 74 C89 55 123 55 135 74 C121 64 91 64 77 74 Z" fill="#7a4a22"/>' + seams('M97 101 C102 104 110 104 115 101') + '<path d="M106 84 l-3 8 l6 0" stroke="#5a3214" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.7"/>' });
      raw('<path d="M88 84 q8 6 16 0 M112 84 q7 6 14 0" stroke="#5a3214" stroke-width="2.8" fill="none" stroke-linecap="round"/>');
    });
  });

// 4 · élite — Colosse : un guerrier de bronze fissuré, le métal rouge par endroits
Mo('idoles', 4, 'Colosse', { scale: 1.22, atk: 'smash', wind: -60, hit: 40, colors: { br: BR, dark: BRD }, swing: ['armN'], far: ['armF'], grp: { farLeg: 'legs', leg: 'legs', body: 'torso' }, piv: { swing: [82, 120], far: [134, 120], head: [108, 96], torso: [106, 200] } },
  ({ S, raw, T, G, L, disc }) => {
    G('armF', () => { L([[[[134, 122], [164, 138], [170, 164]], 22, 20]], 'dark', { far: true, inner: seams('M158 146 l14 -4') }); S(disc(170, 170, 15), T.dark, { sh: 4, far: true }); });
    G('farLeg', () => { L([[[[124, 186], [130, 208], [128, 218]], 24, 22]], 'dark', { far: true }); S('M112 216 L148 216 L154 228 L110 228 Z', T.dark, { sh: 3, far: true }); });
    G('leg', () => { L([[[[88, 188], [82, 208], [84, 218]], 26, 24]], 'br', { inner: seams('M72 204 L96 204') + rivets([[84, 198]]) }); S('M64 216 L104 216 L110 228 L62 228 Z', T.br, { sh: 3 }); });
    G('armN', () => { L([[[[82, 122], [48, 110], [50, 72]], 25, 23]], 'br', { inner: crack('M52 104 L62 110 L56 120') + seams('M38 88 L62 86 M38 80 L62 78') }); S(disc(50, 64, 17), T.br, { sh: 5, inner: seams('M40 62 L60 60 M42 70 L60 68') }); });
    G('body', () => {
      S('M70 172 L146 172 L152 202 L134 194 L128 206 L108 196 L90 206 L84 194 L64 202 Z', T.dark, { sh: 4, inner: seams('M90 176 L90 196 M108 176 L108 192 M128 176 L128 196') + rivets([[78, 182], [140, 182]]) });
      S('M64 126 C62 104 84 96 108 96 C132 96 154 104 152 126 L144 174 C142 186 76 186 72 174 Z', T.br, { sh: 12, hl: 8,
        inner: patina('M118 104 C134 102 148 110 150 124 C138 130 124 122 118 104 Z') + seams('M108 100 L108 160 M80 140 C92 148 124 148 136 140') + crack('M92 112 L104 126 L96 140 L108 154 L102 166') + `<path d="M72 164 L146 164 L144 178 L74 178 Z" fill="#5a3214" opacity="0.8"/><circle cx="108" cy="171" r="8" fill="#7a4a22" stroke="#5a3214" stroke-width="2"/>` + hot('M104 171 L108 165 L112 171 L108 177 Z') });
      // les épaulières couvrent l'attache des bras
      S('M124 100 C142 92 162 104 162 126 C150 126 138 128 130 134 C124 124 122 110 124 100 Z', T.dark, { sh: 4, far: true, inner: rivets([[136, 106], [150, 112]]) });
      S('M52 128 C52 104 74 92 94 100 C100 110 98 126 90 136 C78 128 64 126 52 128 Z', T.dark, { sh: 4, hl: 3, inner: rivets([[62, 116], [74, 106], [88, 106]]) + crack('M70 118 L78 124') });
    });
    G('head', () => {
      S('M98 54 C94 28 108 12 128 14 C120 24 118 40 120 54 Z', T.dark, { sh: 4, inner: seams('M106 48 C104 34 110 24 120 18') });
      S('M82 78 C80 58 94 48 108 48 C124 48 138 58 136 78 L136 88 C136 100 124 108 108 108 C94 108 82 100 82 90 Z', T.br, { sh: 9, hl: 6, inner: '<path d="M88 70 L132 70 L132 86 L116 86 L112 104 L104 104 L104 86 L88 86 Z" fill="#2a0f14"/>' + rivets([[90, 62], [108, 56], [128, 62], [88, 96], [130, 96]]) + crack('M124 50 L130 60 L126 68') });
      raw(`<path d="M93 73 L105 78 L93 83 Z M129 73 L115 78 L129 83 Z" fill="${HOT}"/><path d="M93 73 L105 78 L93 83 Z M129 73 L115 78 L129 83 Z" fill="#ffe27a" opacity="0.6" filter="url(#g2)"/>`);
    });
  });

// 5 · boss — Grande Idole : une statue assise au masque de démon, un brasier dans le ventre et dans la gueule
Mo('idoles', 5, 'Grande Idole', { scale: 1.36, atk: 'smash', wind: -50, hit: 36, fx: HOT, colors: { br: BR, dark: BRD }, swing: ['armN'], far: ['armF'], grp: { base: 'legs', body: 'torso' }, piv: { swing: [70, 130], far: [142, 130], head: [106, 104], torso: [106, 200] }, shine: [[106, 170, 16, HOT]] },
  ({ S, raw, T, G, L, halo, eye, brow, teeth, limb, disc }) => {
    halo(106, 170, 34, HOT, 0.75);
    G('armF', () => { L([[[[142, 132], [180, 142], [186, 112]], 22, 18]], 'dark', { far: true, inner: seams('M176 124 l18 2') }); S(disc(188, 102, 14), T.dark, { sh: 4, far: true }); });
    G('base', () => {
      S('M40 196 C60 186 152 186 172 196 L182 228 L30 228 Z', T.dark, { sh: 6, inner: seams('M34 214 L178 214') + patina('M34 220 C70 212 120 212 150 222 L150 230 L34 230 Z') + rivets([[44, 206], [168, 206]], 3) });
      S('M50 208 C54 188 84 184 100 196 L100 216 L52 216 Z', T.br, { sh: 4, inner: seams('M60 200 C72 194 86 196 96 202') }); S('M162 208 C158 188 128 184 112 196 L112 216 L160 216 Z', T.br, { sh: 4, far: true });
    });
    G('armN', () => { L([[[[70, 132], [36, 140], [30, 104]], 24, 20]], 'br', { inner: seams('M20 122 l20 -4 M20 114 l20 -4') + crack('M44 132 L52 138') }); S(disc(30, 94, 16), T.br, { sh: 5, inner: seams('M20 92 L40 90 M22 100 L40 98') }); });
    G('body', () => S('M56 150 C52 118 76 104 106 104 C136 104 160 118 156 150 C154 184 136 202 106 202 C76 202 58 184 56 150 Z', T.br, { sh: 12, hl: 8,
      inner: patina('M60 134 C68 118 86 110 100 108 C86 118 72 130 66 148 Z') + '<path d="M80 148 C80 134 132 134 132 148 L132 188 L80 188 Z" fill="#2a0f14"/>' + hot('M86 186 C82 168 94 162 96 150 C104 162 112 152 114 144 C122 158 130 170 126 186 Z') + '<g stroke="#5a3214" stroke-width="4" fill="none"><path d="M80 148 C80 134 132 134 132 148 L132 188 L80 188 Z"/><path d="M93 140 L93 188 M106 138 L106 188 M119 140 L119 188"/></g>' + rivets([[66, 156], [66, 172], [146, 156], [146, 172]], 3) + crack('M140 122 L148 132 L144 142') }));
    G('head', () => {
      // cornes et couronne partent de sous le masque
      S(limb([[136, 70], [174, 66], [180, 26]], 15, 3, 16), T.dark, { sh: 4, far: true }); S(limb([[78, 70], [38, 66], [32, 24]], 17, 3, 16), T.br, { sh: 4, hl: 3, inner: seams('M56 62 l-2 12 M42 52 l-10 4') });
      S('M80 54 L82 22 L96 38 L106 10 L116 38 L130 22 L132 54 Z', T.dark, { sh: 4, hl: 2, inner: patina('M98 38 L106 16 L114 38 Z', 0.6) });
      S('M70 58 C72 42 140 42 142 58 L148 94 C148 116 128 128 106 128 C84 128 64 116 64 94 Z', T.br, { sh: 10, hl: 7,
        inner: patina('M66 96 C66 80 68 66 72 56 C78 70 76 90 72 106 Z') + '<path d="M78 98 C88 91 124 91 134 98 L130 116 C118 122 94 122 82 116 Z" fill="#2a0f14"/>' + hot('M90 114 C92 106 100 102 106 106 C112 102 120 106 122 114 C112 118 100 118 90 114 Z') + seams('M106 70 L101 88 L111 88') + `<circle cx="106" cy="56" r="5" fill="${VERD}" opacity="0.9"/>` + rivets([[74, 60], [138, 60]]) + crack('M136 78 L142 88 L138 98') });
      teeth([82, 97], [130, 97], 6, 8, 1, BONE); teeth([86, 117], [126, 117], 5, -7, 1, BONE);
      eye(88, 76, 10, 8, { sclera: '#ffe27a', iris: HOT, pupilK: 0.4, lid: 0.46, tilt: 1, lidC: '#5a3214' }); eye(124, 76, 10, 8, { sclera: '#ffe27a', iris: HOT, pupilK: 0.4, lid: 0.46, tilt: -1, lidC: '#5a3214' });
      brow(88, 65, 26, 1, '#5a3214', 6); brow(124, 65, 26, -1, '#5a3214', 6);
    });
  });
