// LE BAYOU (eau) — les créatures du marais : écailles vertes, vase, mousse, lueurs.
// Gueule ouverte découpée dans la silhouette, membres attachés sous le corps (voir LISEZMOI, « Les monstres »).
// Niveau de la famille de référence (m-glaces.cjs) : un cou relie la tête au corps, crêtes à rayons, écussons sur le dos,
// plaques du ventre, griffes, arcade dure au-dessus de l'œil. Chaque bête a son plan de corps.
const { Mo } = require('./mon6.cjs');
const WATER = '#6fd0ff', WISP = '#8fffd0', MAW = '#2a1016';

// 0 · rapide — Lézard basilic : il court debout, penché en avant, crêtes dressées, si vite qu'il marche sur l'eau
Mo('bayou', 0, 'Lézard basilic', { scale: 0.98, atk: 'stab', wind: -10, hit: 14, colors: { skin: '#4fae6a', dark: '#2f7a4a', belly: '#e6e8a0', crest: '#e8802a' }, grp: { tail: 'back', farLeg: 'legs', leg: 'legs', arm: 'torso', body: 'torso' }, piv: { head: [146, 112], back: [84, 162], torso: [104, 186] } },
  ({ S, raw, T, G, L, neck, eye, brow, teeth, stripes, spots, under, ell }) => {
    const rays = (l) => stripes(l, '#8a3a10', 1.8, 0.6);
    G('tail', () => {
      // la voile de la queue, puis la queue en fouet
      S('M84 152 C68 132 44 134 30 158 C48 156 66 162 80 170 Z', T.crest, { sh: 3, inner: rays(['M76 156 L62 142', 'M64 156 L50 146', 'M52 158 L40 152']) });
      L([[[[86, 162], [28, 180], [4, 118]], 19, 3]], 'skin', { N: 20, inner: stripes(['M62 162 l-4 14', 'M46 166 l-6 13', 'M30 164 l-9 9', 'M18 150 l-9 4', 'M12 134 l-8 0'], '#2f7a4a', 4, 0.6) });
    });
    // patte du fond : elle pousse en arrière
    G('farLeg', () => { L([[[[98, 172], [72, 178], [60, 206]], 15, 9]], 'dark', { far: true }); S('M66 204 C58 208 50 216 44 228 L72 228 C74 220 72 212 70 206 Z', T.dark, { sh: 2, far: true }); });
    // patte du devant de l'image : grande foulée, longs doigts
    G('leg', () => {
      S(ell(106, 172, 17, 15), T.skin, { sh: 5 });
      L([[[[108, 172], [138, 186], [120, 210]], 17, 9]], 'skin', { inner: stripes(['M120 176 l-6 12', 'M130 184 l-8 10'], '#2f7a4a', 3.4, 0.5) });
      S('M112 210 C108 216 108 222 110 228 L158 228 L140 224 L160 221 L138 218 C132 212 122 208 112 210 Z', T.skin, { sh: 2 });
    });
    G('arm', () => L([[[[128, 154], [146, 170], [160, 160]], 9, 4]], 'dark'));
    G('body', () => {
      // la voile du dos
      S('M84 148 C76 116 94 98 120 102 C114 114 116 126 124 136 Z', T.crest, { sh: 4, inner: rays(['M90 140 L88 114', 'M100 136 L100 106', 'M110 134 L112 106']) });
      S('M72 168 C70 146 88 132 108 130 C126 128 140 138 142 152 C144 168 132 182 112 187 C92 191 76 184 72 168 Z', T.skin, { sh: 9, hl: 6,
        inner: under('M78 180 C100 196 130 186 146 160 L150 200 L76 200 Z', '#e6e8a0', 0.85) + stripes(['M86 138 L90 160', 'M100 132 L102 156', 'M114 130 L114 152', 'M128 134 L126 150'], '#2f7a4a', 5, 0.6) + spots([[94, 168, 2.4], [108, 164, 2], [122, 160, 2.2]], '#bff0e0', 0.8) });
      neck([126, 150], [142, 132], [150, 108], 28, 22, 'skin', { inner: under('M136 150 C150 134 158 120 160 104 L170 150 Z', '#e6e8a0', 0.8) + stripes(['M132 134 l12 6', 'M138 120 l12 4'], '#2f7a4a', 4, 0.6) });
    });
    G('head', () => {
      // le casque : une crête qui part du crâne vers l'arrière
      S('M140 96 C122 70 134 44 162 40 C154 54 156 70 166 84 Z', T.crest, { sh: 4, inner: rays(['M146 88 L140 62', 'M154 86 L150 54']) });
      raw(`<path d="M194 100 L160 108 L183 118 C174 114 174 106 194 100 Z" fill="${MAW}"/>`);
      S('M134 104 C132 90 144 80 158 82 C174 84 186 92 194 100 L162 108 L187 120 C178 127 160 128 148 123 C140 120 135 112 134 104 Z', T.skin, { sh: 7, hl: 5,
        inner: under('M146 124 C160 130 178 128 190 120 L190 132 L144 132 Z', '#e6e8a0', 0.85) + '<ellipse cx="186" cy="96" rx="1.8" ry="1.3" fill="#1f4a30"/>' + stripes(['M138 100 l8 4', 'M140 110 l8 2'], '#2f7a4a', 3, 0.6) });
      teeth([190, 101.5], [165, 107.5], 4, 5, 1); teeth([184, 118.5], [165, 110.5], 3, -4.5, 1);
      eye(158, 95, 7.5, 6.5, { iris: '#ffb020', pupil: 'slit', lid: 0.44, tilt: 1 }); brow(158, 87, 19, 1, '#1f4a30', 4);
    });
  });

// 1 · costaud — Tortue-alligator : trois rangées d'écussons en pyramide, une tête énorme, un bec crochu grand ouvert
Mo('bayou', 1, 'Tortue-alligator', { scale: 1.1, atk: 'smash', wind: -16, hit: 22, colors: { shell: '#5a5238', skin: '#6a7a4a', dark: '#46522e', moss: '#7ab84a' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', shell: 'torso' }, piv: { swing: [130, 184], back: [40, 194], torso: [92, 200] } },
  ({ S, raw, T, G, L, beast, eye, brow, stripes, spots, under }) => {
    const legs = beast({ front: 122, hind: 54, top: 198, w: 21, t: 'skin', dark: 'dark', claws: true, gap: 12 });
    G('tail', () => { S('M44 184 L34 176 L32 190 L22 186 L22 200 L12 200 L14 214 L40 204 Z', T.dark, { sh: 2 }); L([[[[46, 194], [20, 202], [6, 222]], 16, 4]], 'skin'); });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    // la tête sort de sous le bord de la carapace, au bout d'un cou plissé
    G('head', () => {
      raw(`<path d="M200 181 L164 186 L186 202 C178 196 180 188 200 181 Z" fill="${MAW}"/><path d="M168 187 C174 187 180 190 182 196" stroke="#e8788a" stroke-width="3.4" fill="none" stroke-linecap="round"/>`);
      S('M112 190 C112 164 140 144 166 148 C184 150 198 162 204 176 C208 182 208 188 204 195 L198 181 L166 186 L190 204 C182 212 164 214 146 210 C128 206 112 200 112 190 Z', T.skin, { sh: 9, hl: 6,
        inner: under('M146 210 C164 216 182 212 192 204 L194 222 L140 222 Z', '#c8c890', 0.7) + stripes(['M124 172 C122 182 124 194 130 202', 'M134 164 C130 178 132 194 140 206'], '#46522e', 2.6, 0.55) + spots([[150, 160, 3], [176, 160, 2.4], [160, 196, 2.4], [186, 170, 2]], '#46522e', 0.6)
          + '<path d="M204 176 C208 182 208 188 204 195 L198 181 Z" fill="#e8dcb0" opacity="0.9"/><ellipse cx="197" cy="170" rx="2" ry="1.5" fill="#1f2a18"/><path d="M166 186 L196 182" stroke="#2a2416" stroke-width="1.6" opacity="0.5"/>' });
      eye(164, 168, 8, 7, { iris: '#ffb020', pupil: 'slit', lid: 0.46, tilt: 1 }); brow(164, 159, 22, 1, '#2a3418', 5.5);
    });
    G('shell', () => S('M26 200 C22 170 36 150 52 142 L58 116 L76 134 C82 132 88 130 94 130 L104 102 L120 132 C128 136 134 140 140 148 L160 134 L154 162 C160 174 162 188 160 200 Z', T.shell, { sh: 11, hl: 7,
      inner: '<path d="M22 188 C70 178 120 178 164 188 L164 204 L22 204 Z" fill="#3a3424" opacity="0.75"/>' + stripes(['M44 184 l-2 16', 'M66 181 l-1 19', 'M88 180 l0 20', 'M110 180 l1 20', 'M132 182 l2 18', 'M150 185 l2 15'], '#22201a', 2, 0.6)
        + [[52, 168, 12], [82, 160, 13], [114, 160, 13], [140, 168, 11]].map(([x, y, s]) => `<path d="M${x - s} ${y + s * 0.7} L${x + 2} ${y - s} L${x + s} ${y + s * 0.7} Z" fill="#8a7e58"/><path d="M${x - s} ${y + s * 0.7} L${x + 2} ${y - s} L${x + 2} ${y + s * 0.7} Z" fill="#2e2a1c" opacity="0.55"/>`).join('')
        + stripes(['M58 120 L60 142', 'M104 106 L104 132', 'M158 138 L146 152'], '#2e2a1c', 2, 0.5)
        + '<g fill="#7ab84a" opacity="0.85" filter="url(#g2)"><path d="M64 136 C72 130 84 130 92 134 C86 142 72 144 64 136 Z"/><path d="M120 136 C128 136 136 142 140 150 C132 152 124 146 120 136 Z"/><ellipse cx="36" cy="172" rx="7" ry="5"/></g>' }));
  });

// 2 · tireur — Poisson-archer : dos tout droit, museau pointé vers sa cible, il crache un jet d'eau
Mo('bayou', 2, 'Poisson-archer', { scale: 0.94, atk: 'cast', fx: WATER, colors: { body: '#d8d8a0', bar: '#2a3424', fin: '#e0a830' }, grp: { tail: 'back', body: 'torso' }, piv: { back: [62, 170], torso: [106, 150] }, shine: [[189, 104, 9, WATER]] },
  ({ S, raw, T, G, at, halo, eye, brow, stripes, under }) => {
    halo(189, 104, 14, WATER, 0.8);
    const TILT = 'translate(0 -12) rotate(-22 106 160)', rays = (l) => stripes(l, '#6e4a10', 1.8, 0.6);
    G('tail', () => at(TILT, () => S('M58 156 L22 130 C30 150 30 172 18 196 L60 176 Z', T.fin, { sh: 5, inner: rays(['M52 160 L30 142', 'M50 166 L30 166', 'M52 172 L28 186']) + '<path d="M22 130 C30 150 30 172 18 196" stroke="#2a3424" stroke-width="5" fill="none" opacity="0.7"/>' })));
    G('body', () => at(TILT, () => {
      // dorsale et anale tout à l'arrière, comme l'empennage d'une flèche
      S('M102 134 L92 104 L84 124 L72 102 L68 130 L56 120 L58 154 Z', T.fin, { sh: 3, inner: rays(['M96 130 L92 110', 'M80 132 L73 108', 'M64 140 L58 126']) });
      S('M98 198 L88 224 L78 206 L66 220 L60 184 Z', T.fin, { sh: 3, inner: rays(['M90 200 L86 216', 'M74 196 L68 212']) });
      raw(`<path d="M190 148 L172 155 L184 161 C179 158 180 152 190 148 Z" fill="${MAW}"/>`);
      // dos rectiligne du museau à la dorsale, ventre profond ; la bouche s'ouvre vers le haut
      S('M52 158 C64 150 80 138 98 132 L150 137 C166 139 180 144 190 148 L174 155 L187 162 C178 178 158 194 132 199 C104 204 72 192 52 174 Z', T.body, { sh: 10, hl: 6,
        inner: under('M54 180 C84 204 140 204 186 164 L190 212 L50 212 Z', '#fffbe0', 0.8)
          + '<g fill="#2a3424" opacity="0.85"><path d="M134 134 C130 150 132 166 140 180 L152 174 C146 162 144 148 148 136 Z"/><path d="M108 132 C102 150 104 168 112 184 L126 182 C118 166 118 150 122 133 Z"/><path d="M84 138 C78 152 80 168 86 182 L98 182 C92 168 92 154 96 134 Z"/><path d="M62 150 C58 160 60 170 64 178 L74 180 C70 170 70 160 74 144 Z"/></g>'
          + stripes(['M156 172 q-5 7 0 14', 'M130 184 q-5 6 0 10', 'M102 184 q-5 6 0 10'], '#8a8a50', 1.6, 0.5)
          + '<path d="M104 136 L150 141" stroke="#fff" stroke-width="3" opacity="0.4" stroke-linecap="round"/>' });
      S('M130 176 C116 180 108 192 110 206 C124 202 136 192 140 180 Z', T.fin, { sh: 3, inner: rays(['M130 182 L116 198', 'M134 184 L124 198']) });
      eye(160, 157, 8.5, 8, { iris: '#ffe14a', pupilK: 0.5, lid: 0.42, tilt: 1, look: [2.5, -1.5] }); brow(160, 148, 19, 1, '#2a3424', 4.5);
    }));
  });

// 3 · sorts — Feu follet : la lueur qui égare les voyageurs ; une flamme pâle, des orbites creuses, deux mains griffues
Mo('bayou', 3, 'Feu follet', { atk: 'cast', fx: WISP, colors: { flame: '#2fc09a', core: '#c8fff0', dark: '#157a6c' }, swing: ['handN'], far: ['handF'], grp: { tailW: 'back', body: 'torso' }, piv: { swing: [140, 156], far: [76, 150], back: [102, 186], torso: [108, 150] } },
  ({ S, raw, T, G, halo }) => {
    halo(110, 136, 58, WISP, 0.55);
    G('tailW', () => S('M90 176 C92 196 112 198 104 222 C92 214 76 206 74 186 Z', T.dark, { sh: 4, so: 0.7 }));
    G('handF', () => S('M82 148 C68 144 58 148 50 142 C46 136 44 128 46 118 C38 126 34 136 36 144 C30 142 24 136 22 128 C18 142 22 152 30 158 C26 160 20 160 14 156 C20 168 34 174 46 168 C56 170 70 170 82 164 Z', T.dark, { sh: 3, far: true }));
    G('handN', () => S('M138 150 C152 146 162 150 170 144 C174 138 176 130 174 120 C182 128 186 138 184 146 C190 144 196 138 198 130 C202 144 198 154 190 160 C194 162 200 162 206 158 C200 170 186 176 174 170 C164 172 150 172 138 166 Z', T.flame, { sh: 3, so: 0.7 }));
    G('body', () => {
      // la flamme : des langues couchées vers l'arrière, un cœur plus clair
      S('M120 44 C122 70 138 84 144 104 C150 96 150 86 148 76 C166 100 160 128 154 142 C156 168 138 192 110 192 C84 192 66 168 68 142 C68 124 60 114 54 98 C64 104 74 110 80 104 C76 92 78 78 86 68 C88 82 94 92 100 94 C104 80 114 66 120 44 Z', T.flame, { sh: 10, hl: 7, so: 0.7,
        inner: '<path d="M112 92 C128 114 140 138 134 160 C128 182 92 182 84 160 C78 140 92 124 112 92 Z" fill="#8ff0d0" opacity="0.8" filter="url(#g3)"/><path d="M110 122 C122 136 126 152 120 166 C114 176 100 176 96 164 C92 150 100 138 110 122 Z" fill="#eafff8" opacity="0.75" filter="url(#g3)"/>' });
      // le visage : deux orbites en biais, une lueur au fond, une bouche en dents de scie
      raw('<path d="M90 130 L109 140 C110 151 100 156 93 150 C88 145 87 136 90 130 Z M134 130 L116 140 C115 151 124 156 131 150 C135 145 136 136 134 130 Z" fill="#06302c"/><circle cx="101" cy="145" r="2.6" fill="#eafff8"/><circle cx="124" cy="145" r="2.6" fill="#eafff8"/>'
        + '<path d="M94 162 L100 169 L106 163 L112 169 L118 163 L124 169 L130 162 C126 180 98 180 94 162 Z" fill="#06302c"/>');
    });
  });

// 4 · élite — Silure géant : une tête plate large comme une barque, de longs barbillons, un corps d'anguille dressé derrière lui
Mo('bayou', 4, 'Silure géant', { scale: 1.18, atk: 'smash', wind: -12, hit: 18, colors: { skin: '#5a6444', dark: '#3e4830', belly: '#d8d4a8' }, swing: ['barb'], grp: { tail: 'back', fin: 'legs', body: 'torso' }, piv: { swing: [176, 166], back: [64, 190], torso: [116, 200] } },
  ({ S, raw, T, G, L, eye, brow, teeth, limb, stripes, spots, under }) => {
    const rays = (l) => stripes(l, '#1c2414', 1.8, 0.55);
    G('tail', () => {
      // la longue nageoire du dessous court jusqu'au bout de la queue, arrondie
      S('M96 206 C70 232 20 226 6 190 C-4 160 0 124 14 102 C22 96 30 100 32 110 C20 140 22 176 44 192 Z', T.dark, { sh: 4, inner: rays(['M80 208 l-10 16', 'M60 206 l-12 16', 'M40 198 l-16 12', 'M26 180 l-18 6', 'M20 160 l-18 -2', 'M20 138 l-17 -8', 'M24 118 l-12 -10']) });
      S(limb([[84, 190], [14, 204], [26, 112]], 42, 8, 22), T.skin, { sh: 6, inner: spots([[50, 190, 5], [30, 176, 4], [24, 150, 3.4], [38, 196, 2.6]], '#3e4830', 0.55) });
    });
    G('fin', () => { S('M132 206 C120 212 108 222 104 228 L134 228 C140 222 144 214 144 208 Z', T.dark, { sh: 3, inner: rays(['M130 210 L112 226', 'M136 212 L124 226']) }); L([[[[160, 206], [170, 220], [184, 222]], 4.5, 1.8], [[[148, 208], [152, 222], [164, 228]], 4, 1.8]], 'dark', { N: 16 }); });
    // les grands barbillons partent du bout de la lèvre et filent vers l'arrière, au-dessus du crâne : ni devant l'œil ni devant la gueule
    G('barb', () => { L([[[[188, 171], [204, 146], [180, 126]], 5.5, 4], [[[180, 126], [156, 106], [124, 116]], 4, 1.6], [[[180, 166], [188, 146], [168, 136]], 4.5, 3.4], [[[168, 136], [150, 126], [136, 136]], 3.4, 1.5]], 'dark', { N: 18 }); });
    G('body', () => {
      S('M92 152 L96 126 L104 140 L112 124 L122 148 Z', T.dark, { sh: 3, inner: rays(['M98 146 L98 132', 'M112 144 L112 130']) });
      raw(`<path d="M196 178 L136 187 L186 200 C168 196 168 186 196 178 Z" fill="${MAW}"/><path d="M146 187 C152 185 162 187 166 192 C160 195 150 195 146 191 Z" fill="#b8485a"/>`);
      // tête plate et large, lèvres épaisses ; la gueule est une encoche jusqu'au coin de la bouche
      S('M58 190 C60 164 90 144 126 144 C156 144 184 156 194 172 C196 174 197 176 196 178 L142 187 L192 201 C184 214 152 219 116 217 C86 216 60 208 58 190 Z', T.skin, { sh: 11, hl: 7,
        inner: under('M60 200 C96 220 156 220 192 202 L196 226 L58 226 Z', '#d8d4a8', 0.85) + spots([[86, 168, 6, 4], [108, 158, 4.5, 3], [72, 184, 4, 3], [128, 170, 3.4], [100, 186, 3], [142, 158, 2.6]], '#3e4830', 0.55)
          + '<path d="M194 174 C178 176 160 180 144 184" stroke="#8a9468" stroke-width="3.4" fill="none" stroke-linecap="round" opacity="0.7"/><path d="M188 203 C174 200 160 196 146 190" stroke="#f0ecc8" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.6"/>'
          + '<path d="M126 162 C120 174 120 190 128 204" stroke="#2a3220" stroke-width="2.6" fill="none" stroke-linecap="round" opacity="0.6"/><ellipse cx="188" cy="168" rx="2.2" ry="1.6" fill="#1c2414"/>' });
      teeth([192, 179.5], [148, 186.5], 7, 5, 1); teeth([187, 199.5], [148, 189], 6, -5, 1);
      eye(160, 162, 7, 6.5, { iris: '#ffe14a', pupilK: 0.5, lid: 0.46, tilt: 1 }); brow(160, 154, 20, 1, '#1c2414', 5);
    });
  });

// 5 · boss — Vieux Crocodile : long corps au ras de l'eau, dos d'écussons couvert de mousse, mâchoires grandes ouvertes
Mo('bayou', 5, 'Vieux Crocodile', { scale: 1.36, atk: 'smash', wind: -14, hit: 20, colors: { skin: '#4a6a3e', dark: '#33492a', belly: '#d8d8a0', moss: '#8fc85a' }, swing: ['head'], grp: { tail: 'back', farLegs: 'legs', legs: 'legs', body: 'torso' }, piv: { swing: [124, 174], back: [44, 190], torso: [86, 202] } },
  ({ S, raw, T, G, L, beast, neck, eye, brow, teeth, limb, stripes, spots, under }) => {
    const legs = beast({ front: 106, hind: 48, top: 200, w: 20, t: 'skin', dark: 'dark', claws: true, gap: 12 });
    G('tail', () => {
      // la crête en scie suit le dessus de la queue
      S('M48 176 L36 166 L34 182 L20 178 L22 194 L6 190 L8 174 L-4 166 L8 158 L0 146 L12 144 L8 130 L20 136 L30 190 Z', T.dark, { sh: 3 });
      S(limb([[46, 192], [2, 208], [14, 132]], 32, 6, 22), T.skin, { sh: 6, inner: stripes(['M40 180 l-4 26', 'M28 184 l-8 22', 'M16 180 l-12 12', 'M12 164 l-12 2', 'M12 148 l-10 -4'], '#33492a', 3, 0.55) });
    });
    G('farLegs', () => legs.far());
    G('legs', () => legs.near());
    G('body', () => {
      // deux rangées d'écussons : celle du fond dépasse en dents de scie
      S('M40 170 L46 148 L58 162 L66 142 L78 158 L88 138 L100 156 L110 142 L120 160 L132 152 L134 172 Z', T.dark, { sh: 3 });
      S('M28 198 C24 174 42 160 62 156 C84 150 114 152 132 162 C142 170 146 182 144 194 C140 210 114 216 84 216 C54 216 32 212 28 198 Z', T.skin, { sh: 11, hl: 7,
        inner: under('M30 204 C60 220 116 218 146 198 L150 226 L28 226 Z', '#d8d8a0', 0.85) + stripes(['M48 206 l0 12', 'M64 208 l0 12', 'M80 209 l0 12', 'M96 209 l0 12', 'M112 207 l0 12', 'M128 203 l0 12'], '#8a8a50', 1.8, 0.6)
          + [[50, 176], [68, 170], [86, 168], [104, 168], [122, 172]].map(([x, y]) => `<path d="M${x - 8} ${y + 7} L${x + 1} ${y - 8} L${x + 9} ${y + 7} Z" fill="#6a8a56"/><path d="M${x - 8} ${y + 7} L${x + 1} ${y - 8} L${x + 1} ${y + 7} Z" fill="#22321c" opacity="0.5"/>`).join('')
          + stripes(['M40 190 C70 184 110 184 140 190'], '#33492a', 2.4, 0.5) + '<g fill="#8fc85a" opacity="0.85" filter="url(#g2)"><path d="M54 158 C64 152 78 152 86 158 C78 164 62 166 54 158 Z"/><path d="M100 156 C108 154 118 158 122 164 C114 166 104 164 100 156 Z"/><ellipse cx="38" cy="184" rx="7" ry="4"/></g>' });
      neck([118, 180], [130, 172], [140, 168], 58, 52, 'skin', { inner: under('M110 204 C126 210 140 206 150 198 L152 222 L108 222 Z', '#d8d8a0', 0.85) });
    });
    G('head', () => {
      raw(`<path d="M210 143 L146 167 L199 189 C176 182 174 162 210 143 Z" fill="${MAW}"/><path d="M152 169 C162 165 172 169 176 177 C170 181 158 180 152 174 Z" fill="#b8485a"/>`);
      // crâne à bosses (l'œil, la narine), longues mâchoires ; la gueule est une encoche jusqu'à la charnière
      S('M108 174 C106 152 120 136 138 134 C142 124 158 122 164 134 C178 132 190 128 200 124 C208 120 216 126 216 134 C216 140 212 144 208 145 L150 167 L204 189 C208 195 202 201 194 201 C170 205 142 204 126 196 C114 190 108 182 108 174 Z', T.skin, { sh: 10, hl: 6,
        inner: under('M128 198 C156 206 186 204 206 192 L208 212 L124 212 Z', '#d8d8a0', 0.85) + '<ellipse cx="207" cy="130" rx="2.6" ry="2" fill="#1f2a18"/>'
          + stripes(['M170 138 l3 12', 'M182 134 l3 12', 'M194 130 l3 11', 'M166 192 l1 9', 'M180 193 l1 9', 'M194 192 l0 8'], '#33492a', 2.2, 0.5) + spots([[124, 156, 4, 3], [118, 172, 3.4], [134, 182, 3], [126, 188, 2.4]], '#33492a', 0.55)
          + '<path d="M116 148 L134 166 M122 144 L128 150" stroke="#d8e0b0" stroke-width="2.2" stroke-linecap="round" opacity="0.6"/>' });
      teeth([206, 146.5], [156, 165.5], 7, 9, 1); teeth([201, 188.5], [156, 170], 6, -9, 1);
      eye(150, 144, 8.5, 7.5, { iris: '#ffe14a', pupil: 'slit', lid: 0.46, tilt: 1 }); brow(150, 135, 22, 1, '#1f2a18', 5.5);
    });
  });
