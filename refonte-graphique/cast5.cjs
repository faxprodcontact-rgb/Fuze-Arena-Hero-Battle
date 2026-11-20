// Les 5 héros et les 5 ennemis en version épurée (v5). Chaque personnage : un ou deux éléments forts.
const { figure, limb, blade, bar, disc, HOOD, tone, metal, mix, ln, sf, blob } = require('./mini.cjs');
const LE = [-0.5, -0.85]; // les ennemis sont retournés dans la scène : leur lumière aussi

// ---------- pièces communes ----------
const SPIKY = 'M152 72 L141 60 L137 75 L123 58 L117 77 L103 60 L95 80 L85 66 L80 92 L72 104 L46 108 L64 90 L30 82 L58 70 L28 50 L62 50 L44 22 L78 34 L72 6 L100 24 L104 2 L122 24 L132 8 L142 30 C149 40 153 56 152 72 Z';
const LONGF = 'M66 86 C60 58 80 34 108 34 C136 34 152 52 150 80 C142 74 134 66 130 54 C122 66 110 76 96 78 C90 78 84 74 82 68 C80 84 78 104 74 120 C68 110 64 98 66 86 Z';
const MOHAWK = 'M132 50 L114 16 L113 40 L94 10 L95 38 L74 12 L79 40 L58 28 L72 58 C92 46 114 44 132 50 Z';
function dagger(h, a, b) { const B = blade(a, b, 9, 0.7); h.S(B.d, h.T.steel, { sh: 3, hl: 2, inner: ln(B.mid, '#fff', 1.2, 0.6) }); const g = B.at(0, 0); h.S(bar([g[0] - B.n[0] * 8, g[1] - B.n[1] * 8], [g[0] + B.n[0] * 8, g[1] + B.n[1] * 8], 4.5), h.T.gold, { sh: 2, hl: 1.5, rim: false }); }
function bow(h, t, x = 162, top = 60, bot = 198, bulge = 200, pull = [120, 128]) {
  h.raw(`<path d="M${x} ${top + 2} L${pull[0]} ${pull[1]} L${x} ${bot - 2}" stroke="#f4efe2" stroke-width="1.8" fill="none" stroke-linejoin="round"/>`);
  h.S(limb([[x, top], [bulge, (top + bot) / 2], [x, bot]], 7.5, 7.5, 18), t, { sh: 3, hl: 2 });
  const sh = bar([pull[0] - 2, pull[1]], [x + 20, pull[1] + 1], 4);
  h.S(sh, h.T.wood, { sh: 2, hl: 1, rim: false });
  h.S(`M${x + 37} ${pull[1] + 1} L${x + 19} ${pull[1] - 8} L${x + 19} ${pull[1] + 10} Z`, h.T.steel, { sh: 2, hl: 1.5, rim: false });
}
const hoodOn = (t, trim) => (h) => h.S(HOOD, t, { eo: true, sh: 10, inner: trim ? `<path d="M84 86 C84 66 98 56 116 56 C134 56 150 68 150 86 C150 100 142 112 128 117 C116 120 102 120 94 115 C86 109 84 98 84 86 Z" fill="none" stroke="${trim}" stroke-width="5" opacity="0.9"/>` : sf('M66 60 C80 40 100 34 122 36', t.light, 5, 0.4, 2) });

// ================= HÉROS =================
const HEROES = {
  // Protecteur : grand bouclier + casque à cornes (marteau sur l'épaule)
  protector: figure({ id: 'p', rig: { swing: ['nearArm', 'afterBody', 'front'], top: ['nearArm', 'afterBody', 'front'], far: ['farFront'], atk: 'smash', wind: -18, hit: 125 }, colors: { skin: '#eebf98', hair: '#b8642a', cloth: '#3f7a44', pants: '#2e4a3a', boot: '#4a3a2a', glove: '#6a4a2e', shieldFace: '#3f8a4a' },
    beard: true, eyes: { color: '#4a7a2a' }, browColor: '#7a3f16',
    afterBody: (h) => { // marteau posé sur l'épaule : manche derrière la tête, masse en haut à gauche
      h.S(bar([116, 150], [34, 100], 8), h.T.wood, { sh: 3, hl: 2 });
      h.S('M35.8 68.3 L61.4 83.9 L32.2 131.7 L6.6 116.1 Z', h.T.steel, { sh: 9, inner: `<path d="M56.2 92.4 L30.6 76.8 M37.4 123.2 L11.8 107.6" stroke="${h.T.gold.base}" stroke-width="6"/>` });
    },
    headgear: (h) => {
      h.S('M70 94 C84 104 96 98 106 104 C118 98 136 102 148 92 C152 112 142 136 120 144 C96 144 74 124 70 94 Z', h.T.hair, { sh: 8, inner: sf('M96 112 C104 118 114 118 124 110', h.T.hair.shadow, 4, 0.5, 1) });
      h.S('M62 66 C46 60 36 42 40 20 C50 34 62 42 78 46 Z', tone('#e9e2d2'), { sh: 5 });
      h.S('M142 50 C156 44 166 30 164 12 C154 24 142 32 130 36 Z', tone('#e9e2d2'), { sh: 5, far: true });
      h.S('M58 82 C54 52 78 30 108 30 C136 30 156 50 154 78 L142 74 C126 68 86 70 66 84 Z', h.T.steel, { sh: 9, inner: `<path d="M56 78 C80 62 124 60 156 72 L156 82 C124 70 80 72 56 88 Z" fill="${h.T.gold.base}"/>` });
    },
    farFront: (h) => { // bouclier porté devant : il cache le bras du fond
      h.S('M130 110 C150 118 172 118 190 108 C194 150 186 192 160 220 C136 196 126 154 130 110 Z', h.T.steel, { sh: 8, inner:
        `<path d="M138 120 C152 126 168 126 182 120 C184 152 178 184 160 206 C144 186 136 152 138 120 Z" fill="${h.T.shieldFace.base}"/><path d="M160 122 C168 124 176 123 182 120 C184 152 178 184 160 206 Z" fill="${h.T.shieldFace.shadow}" opacity="0.5"/><path d="M164 138 L152 164 L161 164 L154 188 L172 158 L163 158 L170 138 Z" fill="${h.T.gold.light}" stroke="#5a3508" stroke-width="1.6" stroke-linejoin="round"/>` });
    },
    nearArm: (h) => h.S(limb([[82, 130], [84, 156], [112, 148]], 21, 18), h.T.sleeve, { sh: 6 }),
    front: (h) => { h.fist(114, 147, 10); } }),

  // Guerrier : grande épée de feu + écharpe au vent
  warrior: figure({ id: 'w', rig: { swing: ['nearArm', 'front'], atk: 'slash', wind: -42, hit: 68, glow: 'swing', fx: '#ff8a2a' }, colors: { skin: '#f2c29c', hair: '#e8502a', cloth: '#b92b36', pants: '#33304a', boot: '#4a3226', scarf: '#f0b23a', glove: '#5a3826' },
    mouth: 'smirk', eyes: { color: '#c8641e' },
    back: (h) => h.S('M94 120 C72 110 46 114 20 132 C42 136 58 140 70 146 C60 154 52 166 48 180 C70 170 88 154 100 134 Z', h.T.scarf, { sh: 7, inner: sf('M88 126 C68 122 48 126 32 134', h.T.scarf.light, 3, 0.5, 1) }),
    afterBody: (h) => h.S('M74 114 C92 126 122 126 140 112 L142 126 C122 140 92 140 72 128 Z', h.T.scarf, { sh: 5 }),
    headgear: (h) => h.S(SPIKY, h.T.hair, { sh: 10, inner: sf('M70 40 C84 30 104 24 124 26', h.T.hair.light, 5, 0.45, 2) }),
    nearArm: (h) => h.S(limb([[84, 128], [88, 158], [118, 150]], 21, 18), h.T.sleeve, { sh: 6 }),
    front: (h) => {
      const B = blade([128, 136], [194, 34], 22, 0.84);
      h.glow(`<path d="${B.d}" fill="#ff7a1a" opacity="0.85" filter="url(#glow)"/>`);
      h.S(bar([112, 160], [128, 136], 7), h.T.wood, { sh: 2, hl: 1.5 });
      h.S(B.d, h.T.steel, { sh: 5, inner: `<path d="${B.mid}" stroke="#ffb040" stroke-width="5" opacity="0.9"/><path d="${B.mid}" stroke="#fff3c0" stroke-width="1.6"/>` });
      const g = B.at(0, 0); h.S(bar([g[0] - B.n[0] * 17, g[1] - B.n[1] * 17], [g[0] + B.n[0] * 17, g[1] + B.n[1] * 17], 8), h.T.gold, { sh: 3, hl: 2 });
      h.fist(120, 149, 10);
    } }),

  // Archer : grand arc + capuche
  archer: figure({ id: 'a', rig: { swing: ['nearArm', 'front'], far: ['farArm', 'farFront'], atk: 'shoot' }, colors: { skin: '#f3cfae', hair: '#e4e9f2', cloth: '#7a5234', pants: '#3d4a5e', boot: '#4a3a30', hood: '#1f8a9c', sleeve: '#f2ecd8', glove: '#5a4030', bow: '#d9c08a' },
    eyes: { color: '#2aa0b8' }, browColor: '#8a93a6',
    back: (h) => h.S('M86 118 C66 130 54 156 50 186 C68 182 86 172 98 156 Z', h.T.hood, { far: true, sh: 7 }),
    farArm: (h) => h.S(limb([[130, 128], [150, 124], [170, 128]], 18, 15), h.T.sleeve, { far: true, sh: 5 }),
    headgear: (h) => { h.S('M82 80 C86 60 106 52 128 55 C140 57 148 64 152 74 C138 68 126 70 114 80 C106 72 94 72 82 80 Z', h.T.hair, { sh: 5 }); hoodOn(h.T.hood)(h); },
    nearArm: (h) => h.S(limb([[84, 128], [96, 150], [118, 130]], 20, 17), h.T.sleeve, { sh: 6 }),
    farFront: (h) => { bow(h, h.T.bow); h.fist(178, 129, 9); },
    front: (h) => h.fist(120, 128, 9.5) }),

  // Soigneuse : bâton à orbe + longue chevelure
  healer: figure({ id: 'h', rig: { swing: ['nearArm', 'front'], far: ['farArm', 'farFront'], atk: 'cast', glow: 'far', fx: '#6fd0ff', heal: true }, robe: true, beltY: 158, colors: { skin: '#fbdcc4', hair: '#58a8f0', cloth: '#eef3ff', belt: metal('#e6ac3c'), accent: '#3f78d8' },
    eyes: { color: '#5a4ce0', calm: true }, browColor: '#2f6fc0', mouth: 'smile',
    robeInner: `<path d="M98 110 L120 110 L132 236 L84 236 Z" fill="#3f78d8"/>`,
    back: (h) => h.S('M68 70 C56 100 50 140 46 178 C44 196 38 208 28 216 C48 218 68 208 80 192 C90 174 94 150 94 124 L142 120 C148 108 150 94 150 82 Z', h.T.hair, { sh: 10, inner: sf('M72 104 C68 144 60 184 42 212', h.T.hair.shadow, 6, 0.45, 3) }),
    farArm: (h) => h.S(limb([[130, 128], [148, 142], [160, 146]], 20, 20), h.T.sleeve, { sh: 5 }),
    headgear: (h) => h.S(LONGF, h.T.hair, { sh: 9, inner: `<path d="M62 66 C90 78 126 74 154 60" stroke="${h.T.belt.base}" stroke-width="4.5" fill="none"/><circle cx="128" cy="70" r="4.5" fill="#bfe9ff" stroke="${h.T.belt.shadow}" stroke-width="1.4"/>` }),
    farFront: (h) => { // bâton planté devant, orbe en haut
      h.glow(`<circle cx="164" cy="32" r="19" fill="#6fd0ff" opacity="0.8" filter="url(#glow)"/>`);
      h.S(bar([164, 52], [164, 228], 7), h.T.wood, { sh: 3, hl: 2 });
      h.S('M146 30 C146 46 154 54 164 54 C174 54 182 46 182 30 C178 40 172 44 164 44 C156 44 150 40 146 30 Z', h.T.belt, { sh: 3, hl: 2 });
      h.S(disc(164, 30, 11), tone('#4fb8f8'), { sh: 4, hl: 3, inner: `<circle cx="160" cy="26" r="4" fill="#fff" opacity="0.85"/>` });
      h.fist(164, 146, 9);
    },
    nearArm: (h) => h.S(limb([[84, 128], [90, 152], [112, 146]], 21, 20), h.T.sleeve, { sh: 6 }),
    front: (h) => { h.fist(114, 145, 9); } }),

  // Assassin : deux dagues + écharpe au vent, visage masqué
  assassin: figure({ id: 's', rig: { swing: ['nearArm', 'front'], far: ['farArm'], atk: 'stab', wind: -30, hit: 38, fx: '#b98cff' }, colors: { skin: '#e2b08a', cloth: '#322a52', pants: '#272040', boot: '#1f1930', hood: '#3d3266', scarf: '#8a4ce0', belt: '#8a4ce0', glove: '#1f1930' },
    mask: 97, brows: false, eyes: { color: '#6ff0c8', glow: true, sclera: '#6ff0c8', lid: '#1a1230' },
    back: (h) => h.S('M98 120 C72 102 44 98 10 108 C32 116 50 124 62 132 C44 136 28 148 18 164 C46 160 76 150 102 134 Z', h.T.scarf, { sh: 7, inner: sf('M92 122 C70 110 46 106 26 110', h.T.scarf.light, 3, 0.5, 1) }),
    farArm: (h) => { dagger(h, [170, 122], [198, 92]); h.S(limb([[132, 128], [152, 142], [166, 128]], 18, 15), h.T.sleeve, { far: true, sh: 5 }); h.fist(168, 126, 8.5, h.T.glove, { far: true }); },
    headgear: hoodOn(tone('#3d3266'), '#8a4ce0'),
    afterHead: (h) => h.S('M72 108 C92 122 124 122 146 106 L148 124 C124 140 92 140 70 126 Z', h.T.scarf, { sh: 5 }),
    nearArm: (h) => h.S(limb([[84, 130], [84, 158], [108, 160]], 20, 17), h.T.sleeve, { sh: 6 }),
    front: (h) => { dagger(h, [117, 163], [150, 176]); h.fist(110, 160, 9.5); } }),
};

// ================= ENNEMIS (gobelins) =================
const gob = (o) => figure({ kind: 'goblin', light: LE, ...o, colors: { hair: '#2a2430', glove: o.colors.skin, sleeve: o.colors.skin, ...o.colors } });
const yellow = { color: '#f0a020', sclera: '#fff3a8', slit: true };
const ENEMIES = {
  // Massue : grosse massue + crête rouge
  grunt: gob({ id: 'g1', rig: { swing: ['nearArm', 'front'], atk: 'slash', wind: -42, hit: 72 }, colors: { skin: '#84c24c', hair: '#c23a32', cloth: '#8a6238', pants: '#5a4028', boot: '#4a3424' }, eyes: yellow,
    headgear: (h) => h.S(MOHAWK, h.T.hair, { sh: 6 }),
    nearArm: (h) => h.S(limb([[84, 130], [88, 158], [116, 152]], 20, 17), h.T.sleeve, { sh: 6 }),
    front: (h) => {
      h.S(limb([[114, 156], [146, 118], [176, 82]], 9, 30, 14), h.T.wood, { sh: 6, inner: `<path d="M150 104 l7 -3 l-1 8 Z M164 92 l7 -2 l-2 8 Z M168 108 l8 0 l-4 6 Z" fill="#fff8e0"/>` });
      h.fist(118, 151, 10);
    } }),
  // Dagues : deux lames + bandeau rouge
  rogue: gob({ id: 'g2', rig: { swing: ['nearArm', 'front'], far: ['farArm'], atk: 'stab', wind: -30, hit: 38 }, colors: { skin: '#6fb05a', cloth: '#4a3a5a', pants: '#33283f', boot: '#281f33', sleeve: '#4a3a5a', band: '#c83a3a' }, eyes: { ...yellow, color: '#ff6a2a' },
    back: (h) => h.S('M70 62 L40 50 L50 66 L34 78 L70 76 Z', h.T.band, { sh: 4 }),
    farArm: (h) => { dagger(h, [170, 124], [198, 96]); h.S(limb([[132, 130], [152, 144], [166, 130]], 18, 15), h.T.sleeve, { far: true, sh: 5 }); h.fist(168, 128, 8.5, h.T.glove, { far: true }); },
    headInner: `<path d="M50 62 C84 52 122 52 160 64 L160 76 C122 64 84 64 50 74 Z" fill="#c83a3a"/><path d="M50 74 C84 64 122 64 160 76" stroke="#7a1f24" stroke-width="2" fill="none" opacity="0.8"/>`,
    nearArm: (h) => h.S(limb([[84, 132], [84, 160], [108, 162]], 20, 17), h.T.sleeve, { sh: 6 }),
    front: (h) => { dagger(h, [117, 165], [150, 178]); h.fist(110, 162, 9.5); } }),
  // Brute : hache géante + peinture de guerre
  brute: gob({ id: 'g3', rig: { swing: ['nearArm', 'front'], atk: 'smash', wind: -118, hit: 14 }, colors: { skin: '#6f9a58', hair: '#231d2a', cloth: '#5a2f2f', pants: '#3a2a2a', boot: '#2e2426' }, eyes: { ...yellow, color: '#ff4a3a', sclera: '#ffe9b0' }, warpaint: '#e0403a',
    headgear: (h) => h.S(MOHAWK, h.T.hair, { sh: 6 }),
    nearArm: (h) => h.S(limb([[82, 130], [84, 158], [116, 146]], 23, 20), h.T.sleeve, { sh: 6 }),
    front: (h) => { // grande hache tenue basse devant, fer vers l'avant
      h.S(bar([98, 126], [176, 208], 9), h.T.wood, { sh: 3, hl: 2 });
      h.S(bar([150, 181], [169, 201], 14), tone('#5a5a6c'), { sh: 4, rim: false });
      h.S('M153 173 C163 167 171 157 176 144 C196 156 205 184 196 212 C189 201 179 196 168 197 Z', h.T.steel, { sh: 7, inner: sf('M180 152 C194 164 199 186 195 204', '#fff', 3, 0.6, 1) });
      h.fist(118, 147, 11);
    } }),
  // Chaman : bâton à crâne + crâne en coiffe
  shaman: gob({ id: 'g4', rig: { swing: ['nearArm', 'front'], far: ['farArm', 'farFront'], atk: 'cast', glow: 'far', fx: '#c070ff' }, robe: true, beltY: 158, colors: { skin: '#8cc468', cloth: '#5d3d8a', sleeve: '#5d3d8a', belt: '#c03a3a' }, eyes: { color: '#d08aff', glow: true, sclera: '#d08aff', lid: '#2a1a40' }, brows: false,
    farArm: (h) => h.S(limb([[130, 130], [152, 146], [176, 146]], 20, 20), h.T.sleeve, { far: true, sh: 5 }),
    headgear: (h) => h.S('M66 70 C64 42 86 28 108 28 C132 28 150 42 148 66 C138 58 130 64 124 60 L120 70 L114 60 C106 60 100 64 96 60 L92 72 L86 62 C78 62 72 66 66 70 Z', tone('#ece4d0'), { sh: 7, inner: `<ellipse cx="96" cy="46" rx="8" ry="9" fill="#2a1a30"/><ellipse cx="126" cy="44" rx="7" ry="8.5" fill="#2a1a30"/><path d="M110 50 L114 58 L106 58 Z" fill="#2a1a30"/>` }),
    farFront: (h) => {
      h.glow(`<circle cx="180" cy="42" r="19" fill="#c070ff" opacity="0.8" filter="url(#glow)"/>`);
      h.S(bar([180, 56], [180, 228], 7), h.T.wood, { sh: 3, hl: 2 });
      h.S('M166 40 C166 28 172 22 180 22 C188 22 194 28 194 40 C194 48 190 54 188 58 L172 58 C170 54 166 48 166 40 Z', tone('#ece4d0'), { sh: 4, inner: `<ellipse cx="175" cy="40" rx="3.6" ry="4.4" fill="#2a1a30"/><ellipse cx="186" cy="40" rx="3.6" ry="4.4" fill="#2a1a30"/>` });
      h.fist(180, 146, 9);
    },
    nearArm: (h) => h.S(limb([[84, 130], [90, 154], [112, 148]], 21, 20), h.T.sleeve, { sh: 6 }),
    front: (h) => { h.fist(114, 147, 9); } }),
  // Chasseur : arc sombre + capuche
  hunter: gob({ id: 'g5', rig: { swing: ['nearArm', 'front'], far: ['farArm', 'farFront'], atk: 'shoot' }, colors: { skin: '#7ab852', cloth: '#7a5a34', pants: '#4a3a28', boot: '#3e2e20', hood: '#6a4a2e', bow: '#4a3628' }, eyes: yellow,
    farArm: (h) => h.S(limb([[130, 130], [150, 126], [170, 130]], 18, 15), h.T.sleeve, { far: true, sh: 5 }),
    headgear: hoodOn(tone('#6a4a2e'), '#c03a3a'),
    nearArm: (h) => h.S(limb([[84, 130], [96, 152], [118, 132]], 20, 17), h.T.sleeve, { sh: 6 }),
    farFront: (h) => { bow(h, h.T.bow, 162, 62, 200, 200, [120, 130]); h.fist(178, 131, 9); },
    front: (h) => h.fist(120, 130, 9.5) }),
};
module.exports = { HEROES, ENEMIES };
