// TERRE — bruns, verts, ocre, pierre, or ancien.
const { H, tone, metal } = require('./heroes6.cjs');
const gold = metal('#e6ac3c'), bronze = metal('#b8823a');

H('earth', 0, 'Nain des forges', 'nain forgeron des sagas nordiques', {
  scale: 0.96, body: 'small', shape: { sw: 40, ww: 38, hw: 44, arm: [26, 22] },
  colors: { skin: '#eebf98', hair: '#d8642a', cloth: '#6a5a4a', steel: metal('#8a94a4'), iron: metal('#5a5a6c'), pants: '#4a3a30', boot: '#3a2a22', belt: '#3a2a22', shieldFace: '#8a4a2a' },
  chest: [['plate', { t: 'steel' }]], legs: { kind: 'legs', leg: 'thick', foot: 'sabaton', stance: 'wide' },
  head: { kind: 'human', jaw: 'square', eyes: { style: 'angry', color: '#5a3a20' }, brow: { k: 7.5, c: '#b84a1a' }, nose: 'big', beard: 'braids', mustache: 'walrus', ear: false },
  gear: [['hair', { style: 'mane' }]],
  near: { hand: [46, 128], el: [52, 150], item: ['mace', { kind: 'ball', to: [28, 54], t: 'iron' }] },
  far: { noArm: true, handKind: 'none', item: ['shield', { kind: 'kite', c: [160, 158], }] }, atk: 'smash' });

H('earth', 1, 'Satyre', 'satyre, compagnon des bois (Grèce)', {
  shine: [[76, 44, 'head']],
  body: 'slim', shape: { sw: 31, lean: 12, hdx: 4 }, colors: { skin: '#d9a074', hair: '#5a3a22', fur: '#6a4a2e', pants: '#6a4a2e', bone: '#d8c8a0', wood: '#7a5230', boot: '#2a2226', belt: '#4f8a3a' },
  bare: true, bareArms: true, chest: [['muscle']], skirt: { len: 14, t: 'fur', ragged: true }, legs: { kind: 'beast', foot: 'hoof', t: 'fur' },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'sly', color: '#6a8a2a' }, brow: { k: 5.5, shape: 'arch' }, mouth: 'grin', beard: 'chin', nose: 'hook', ear: false },
  gear: [['hair', { style: 'curly' }], ['horns', { kind: 'ram' }], ['ears', { kind: 'elf' }]],
  near: { hand: [56, 158], el: [64, 142], r: 12 }, far: { hand: [150, 168], el: [158, 150], r: 11 }, atk: 'smash', rig: { wind: -16, hit: 24 } });

H('earth', 2, 'Frondeur', 'berger à la fronde (David, Proche-Orient)', {
  shine: [[32, 49, 'near']],
  grp: { top: 'swing' },
  colors: { skin: '#e2a878', hair: '#3a2a20', cloth: '#d8c8a0', belt: '#8a5a34', boot: '#e2a878', strap: '#8a5a34', rope: '#8a5a34' },
  bareArms: true, chest: [['sash', { t: 'strap' }]], skirt: { len: 24, flare: 6 }, legs: { kind: 'legs', leg: 'bare', foot: 'sandal', stance: 'lunge', strapT: 'strap' },
  head: { kind: 'human', eyes: { style: 'calm', color: '#5a3a20' }, brow: { k: 5, lift: [2, -2] }, mouth: 'smirk', band: { t: 'belt', y: 58, k: 7 } },
  gear: [['hair', { style: 'short' }]],
  near: { hand: [62, 96], el: [54, 124] }, far: { pose: 'fwd', handKind: 'open', dir: [1, -0.1] },
  top: [['raw', { svg: '<path d="M62 96 L26 56 M62 96 L40 46" stroke="#8a5a34" stroke-width="3" stroke-linecap="round"/>' }], ['shape', { d: 'M18 58 C16 44 34 34 46 44 C48 56 30 68 18 58 Z', t: 'strap', sh: 3 }], ['disc', { x: 32, y: 49, r: 7.5, t: '#9a9aa8' }]], atk: 'shoot' });

H('earth', 3, 'Cyclope', 'cyclope, géant à l\'œil unique (Grèce)', {
  shine: [[92, -6, 'near']],
  both: true, grp: { afterHead: 'swing' },
  scale: 1.12, body: 'round', shape: { sw: 40, arm: [28, 24] }, colors: { skin: '#b8a078', hair: '#4a3a30', pelt: '#6a4a2e', belt: '#3a2a22', boot: '#b8a078', rock: '#8a8a94' },
  bare: true, bareArms: true, chest: [['belly', { t: '#c8b088' }]], skirt: { len: 26, t: 'pelt', ragged: true }, legs: { kind: 'legs', leg: 'thick', t: 'skin', foot: 'bare', stance: 'wide' },
  head: { kind: 'cyclops', jaw: 'chubby', eyes: { style: 'wide', color: '#8a5a20' }, brow: { k: 8, c: '#4a3a30', shape: 'flat' }, mouth: 'grin', tusks: 'small', ear: false },
  near: { hand: [62, 46], el: [46, 92], over: true }, far: { hand: [154, 44], el: [170, 92], over: true },
  afterHead: [['shape', { d: 'M56 30 L64 -6 L92 -24 L128 -22 L154 -4 L162 26 L140 46 L84 48 Z', t: 'rock', sh: 9, hl: 6 }], ['raw', { svg: '<path d="M92 -22 L104 6 L84 22 M128 -20 L122 10 L142 24" stroke="#5a5a66" stroke-width="2.6" fill="none" opacity="0.7"/>' }]],
  atk: 'smash', rig: { wind: -20, hit: 40 } });

H('earth', 4, 'Homme-scorpion', 'homme-scorpion, gardien du désert (Mésopotamie)', {
  both: true,
  body: 'slim', colors: { skin: '#b8743a', tail: '#8a4a22', bone: '#2a2226', hood: '#d8c8a0', scarf: '#d8c8a0', belt: '#c83a3a', steel: bronze, wood: '#5a3a22' },
  bare: true, bareArms: true, bracers: 'gold', chest: [['muscle'], ['straps', { t: 'belt' }]], legs: 'scorpion',
  head: { kind: 'human', jaw: 'point', eyes: { style: 'fierce', color: '#ffe14a', sclera: '#fff3a8', slit: true }, brow: { k: 5, c: '#2a2226' }, mask: 98, maskT: 'scarf', ear: false },
  gear: [['hood', { kind: 'tail' }]], back: [['at', { t: 'translate(-8 -18)', list: [['tail', { kind: 'scorpion' }]] }]],
  near: { hand: [118, 150], el: [88, 158] }, far: { pose: 'stab', items: [['pole', { butt: [84, 166], end: [202, 118], head: 'spear', hl: 30, hw: 15 }]] }, atk: 'stab', rig: { wind: -10, hit: 14 } });

H('earth', 5, 'Dryade', 'dryade, nymphe des arbres (Grèce)', {
  shine: [[172, 76, 'far']],
  colors: { skin: '#c8dca0', hair: '#4f9a3a', cloth: '#7a5a3a', belt: '#8fc85a', leaf: '#8fc85a' },
  bareArms: true, legs: { kind: 'ragged', w: 46, folds: true },
  head: { kind: 'human', eyes: { style: 'happy', lash: true }, brow: { shape: 'arch', k: 3, c: '#3a6a2a' }, mouth: 'smile', mouthC: '#3a6a2a', blush: '#8fc85a', ear: false },
  gear: [['hair', { style: 'leaf' }]], neck: [['collar', { t: 'leaf' }]],
  near: { hand: [48, 104], el: [54, 132], handKind: 'open', dir: [-0.4, -1] }, far: { hand: [172, 100], el: [160, 128], handKind: 'open', dir: [0.4, -1], item: ['sprout', {}] },
  top: [['glow', { x: 44, y: 88, r: 16, c: '#8fff9a', op: 0.7 }]] });

H('earth', 6, 'Druide', 'druide des forêts celtes', {
  main: 'far',
  shape: { lean: 6, sw: 30 }, colors: { skin: '#eac4a4', hair: '#f4f0e6', cloth: '#f4f0e6', hood: '#4f7a3a', belt: '#8a5a34', wood: '#6a4a2e', steel: gold, leaf: '#8fc85a' },
  legs: { kind: 'straight', w: 42, folds: true },
  head: { kind: 'human', jaw: 'long', eyes: { style: 'tired', color: '#4f7a3a' }, brow: { k: 7, c: '#f4f0e6', shape: 'worry' }, nose: 'hook', beard: 'long', mustache: 'droop', ear: false },
  gear: [['hood', { kind: 'cowl' }]],
  near: { hand: [70, 150], el: [60, 140], w0: 22, w1: 28, item: ['staff', { kind: 'branch', top: 36 }] },
  far: { pose: 'high', w0: 20, w1: 26, item: ['small', { kind: 'sickle', dir: [10, -30], off: 2 }] } });

H('earth', 7, 'Général d\'argile', 'armée de terre cuite du Premier Empereur (Chine)', {
    body: 'heavy', colors: { skin: '#dba27a', hair: '#4a3a34', cloth: '#a8643c', arm: '#5e5450', pants: '#8a6a52', boot: '#4a3a34', belt: '#4a3a34', steel: metal('#7a9a8a'), gold: metal('#b8823a'), scarf: '#b8483a' },
  chest: [['lamellar', { t: 'arm' }], ['cracks', {}]], skirt: { len: 30, t: 'arm', strips: 5 }, legs: { kind: 'legs', leg: 'baggy', foot: 'shoe', stance: 'mid', cuffT: 'boot' },
  head: { kind: 'human', jaw: 'square', eyes: { style: 'angry', color: '#3a2a20' }, brow: { k: 5.5, c: '#8a5a3a', shape: 'flat' }, mouth: 'flat', mustache: 'handle', beard: 'chin', beardT: 'hair' },
  gear: [['hair', { style: 'bun', bx: 110, by: 28, br: 11 }]], neck: [['scarf', {}]],
  near: { pose: 'hip' }, far: { hand: [180, 148], el: [164, 150], item: ['sword', { to: [184, 42], w: 14, guard: 11 }] }, atk: 'slash' });

H('earth', 8, 'Minotaure', 'le Minotaure du labyrinthe (Crète)', {
  both: true,
  scale: 1.14, body: 'brute', colors: { skin: '#7a4a34', muz: '#c8a080', bone: '#ece4d0', pants: '#3a2a22', pelt: '#8a2a2a', belt: '#e6ac3c', boot: '#2a2226', fur: '#5a3424' },
  bare: true, bareArms: true, bracers: 'gold', chest: [['muscle']], skirt: { len: 26, t: 'pelt', trim: 'gold' }, legs: { kind: 'legs', leg: 'thick', t: 'fur', foot: 'hoof', stance: 'wide' },
  head: { kind: 'bull', eyes: { style: 'glow', color: '#ff5a2a' }, ring: true }, gear: [['horns', { kind: 'bull' }]],
  near: { hand: [108, 176], el: [74, 166], over: true, item: ['axe', { to: [190, 170], double: true, z: 1.05, back: 30 }] }, far: { hand: [150, 173], el: [170, 158], over: true, r: 15 }, atk: 'slash', rig: { wind: -30, hit: 30 } });

H('earth', 9, 'Gorgone', 'Méduse, la gorgone au regard de pierre (Grèce)', {
  shine: [[150, 84, 'head', 11, '#eaff6a']],
  grp: { top: 'head' },
  body: 'curvy', colors: { skin: '#a8c8a0', hair: '#3f7a4a', cloth: '#6a5a8a', tail: '#3f7a4a', belly: '#c8dc9a', belt: '#e6ac3c' },
  bareArms: true, bracers: 'gold', chest: [['scales', { t: '#7a6a9a' }]], legs: 'naga',
  head: { kind: 'human', jaw: 'point', eyes: { style: 'glow', color: '#eaff6a', lid: '#2a4a2a' }, brow: { shape: 'angry', k: 4, c: '#2a4a2a' }, mouth: 'fang', mouthC: '#2a4a2a', ear: false },
  gear: [['hair', { style: 'snakes' }]], neck: [['collar', { gem: '#eaff6a' }]],
  near: { pose: 'hip' }, far: { hand: [174, 158], el: [160, 154], handKind: 'open', dir: [1, 0.2] },
  top: [['glow', { x: 162, y: 84, r: 12, c: '#eaff6a', op: 0.9 }], ['glow', { x: 180, y: 84, r: 18, c: '#eaff6a', op: 0.7 }], ['glow', { x: 202, y: 84, r: 26, c: '#eaff6a', op: 0.5 }]], atk: 'cast' });

H('earth', 10, 'Anubis', 'Anubis, gardien des morts (Égypte)', {
  main: 'far', rig: { farWind: 0, farHit: 0 },
  body: 'slim', shape: { sw: 31 }, colors: { skin: '#2a2630', muz: '#2a2630', nem: '#2f6fc8', cloth: '#f4f0e6', belt: '#e6ac3c', boot: '#2a2630', steel: gold },
  bare: true, bareArms: true, bracers: 'gold', chest: [['muscle']], skirt: { len: 30, t: 'cloth', flap: 'gold', flapLen: 0, flare: 4 }, legs: { kind: 'legs', leg: 'bare', foot: 'sandal', anklet: 'gold', stance: 'narrow' },
  head: { kind: 'jackal', eyes: { style: 'fierce', color: '#ffe14a', sclera: '#fff3a8' } },
  gear: [['nemes', { t: 'nem', stripe: 'gold' }], ['ears', { kind: 'tall' }]], neck: [['collar', { t: 'gold', stripes: '#2f6fc8' }]],
  near: { hand: [56, 146], el: [56, 132], items: [['raw', { svg: '<g stroke="#e6ac3c" stroke-width="3" fill="none" stroke-linecap="round"><path d="M56 150 L56 162 M36 162 L76 162 M36 162 L30 182 M36 162 L42 182 M76 162 L70 182 M76 162 L82 182"/></g><path d="M26 182 Q36 193 46 182 Z M66 182 Q76 193 86 182 Z" fill="#e6ac3c" stroke="#2c1626" stroke-width="2"/>' }]] },
  far: { hand: [174, 152], el: [158, 150], item: ['sword', { to: [216, 104], w: 16, curve: 16, guard: 0 }] } });

H('earth', 11, 'Isis', 'Isis, la magicienne aux ailes (Égypte)', {
  shine: [[188, 100, 'far']],
  body: 'curvy', grp: { top: 'far' },
  colors: { skin: '#d9a074', hair: '#1c1a24', cloth: '#f4f0e6', belt: '#2fa3a0', wing: '#2fa3a0', wood: '#e6ac3c' },
  bareArms: true, bracers: 'gold', legs: { kind: 'mermaid', w: 40, trim: 'gold' },
  head: { kind: 'human', eyes: { style: 'calm', color: '#2a2226', lash: true }, brow: { shape: 'flat', k: 3.4, c: '#1c1a24' }, mouth: 'smile', mouthC: '#b83a4a', ear: false,
    paint: '<path d="M88 92 L74 94 M140 90 L150 90" stroke="#1c1a24" stroke-width="2.6" stroke-linecap="round"/>' },
  gear: [['hair', { style: 'bob', band: 'gold' }], ['shape', { d: 'M96 36 L96 14 L108 14 L108 4 L122 4 L122 36 Z', t: 'gold', sh: 4 }]], neck: [['collar', { t: 'gold', stripes: '#2fa3a0' }]],
  near: { hand: [46, 142], el: [62, 136], handKind: 'open', dir: [-1, 0.1], items: [['shape', { d: 'M86 142 L44 147 L42 166 L52 159 L54 182 L66 165 L70 190 L80 171 L88 192 L92 152 Z', t: 'wing', sh: 5 }]] },
  far: { hand: [184, 134], el: [160, 134], handKind: 'open', dir: [1, 0], items: [['shape', { d: 'M136 140 L184 140 L186 160 L176 153 L174 176 L162 161 L158 186 L147 167 L140 188 L136 164 Z', t: 'wing', sh: 5 }]] },
  top: [['raw', { svg: '<g stroke="#e6ac3c" stroke-width="5" fill="none" stroke-linecap="round"><ellipse cx="188" cy="98" rx="6" ry="8"/><path d="M188 106 L188 126 M180 112 L196 112"/></g>' }]] });

H('earth', 12, 'Baron des ombres', 'Baron Samedi, maître des cimetières (Haïti)', {
  shine: [[126, 138, 'near', 10, '#e0b0ff']],
  main: 'far',
  body: 'tall', colors: { skin: '#5a3a2e', hair: '#1c1a24', cloth: '#f4f0e6', coat: '#3a2a4a', sleeve: '#3a2a4a', pants: '#2a2230', hat: '#2a2230', scarf: '#8a3a9a', belt: '#8a3a9a', boot: '#1c1a24', jar: '#6fae5a', wood: '#1c1a24', bone: '#f4efe2' },
  chest: [['vest', { t: 'coat' }]], skirt: { len: 40, t: 'coat', flare: 6 }, legs: { kind: 'legs', leg: 'thin', foot: 'shoe', stance: 'narrow' },
  head: { kind: 'human', jaw: 'long', eyes: { style: 'sly', color: '#c86aff', sclera: '#f4efe2' }, brow: { shape: 'arch', k: 4 }, mouth: 'gritted', ear: false,
    paint: '<path d="M86 78 C96 70 110 72 114 84 C112 96 96 100 86 92 Z M124 76 C134 70 146 74 148 84 C144 96 130 96 124 88 Z" fill="#f4efe2" opacity="0.92"/>' },
  gear: [['tophat', { emblem: 'skull' }]],
  near: { hand: [124, 164], el: [88, 164], item: ['cane', { top: 'skull', lean: 2 }] }, far: { pose: 'up', item: ['bottle', {}] } });

H('earth', 13, 'Héraclès', 'Héraclès et la peau du lion de Némée (Grèce)', {
  shine: [[130, 160, 'near']],
  scale: 1.12, body: 'brute', colors: { skin: '#e2a878', hair: '#6a4a2e', pelt: '#d8a050', cape: '#d8a050', fur: '#8a5a2a', belt: '#5e3a22', boot: '#e2a878', strap: '#5e3a22' },
  bare: true, bareArms: true, bracers: 'belt', chest: [['muscle'], ['sash', { t: 'pelt' }]], skirt: { len: 24, t: 'pelt', ragged: true }, legs: { kind: 'legs', leg: 'bare', foot: 'bare', wrap: 'strap', stance: 'lunge' },
  head: { kind: 'human', jaw: 'square', eyes: { style: 'angry', color: '#5a3a20' }, brow: { k: 7, c: '#4a3220' }, mouth: 'grin', beard: 'full', nose: 'big', scar: true, band: { t: 'pelt', y: 56, k: 7 } },
  gear: [['hair', { style: 'short' }]], back: [['cape', { len: 'torn' }]], neck: [['fur', {}]],
  near: { hand: [128, 162], el: [90, 170], r: 15 }, far: { hand: [178, 150], el: [162, 150], r: 15, item: ['club', { to: [184, 210], w0: 10, w1: 28, spikes: false }] }, atk: 'smash', rig: { wind: -30, hit: 36 } });

H('earth', 14, 'Herne le Veneur', 'Herne, le chasseur aux bois de cerf (Angleterre)', {
  scale: 1.08, body: 'tall', colors: { skin: '#ece4d0', bone: '#ece4d0', cloth: '#3a4a34', hood: '#3a4a34', belt: '#6a4a2e', bow: '#6a4a2e', cape: '#2a3426', fur: '#5a4634', glove: '#2a2226' },
  legs: { kind: 'ragged', w: 44, base: 'mist', baseC: '#8fff9a' },
  head: { kind: 'skull', eyes: { style: 'glow', color: '#8fff9a' } }, gear: [['antlers', { z: 1.2 }]], back: [['cape', { len: 'wide' }]], neck: [['fur', {}]],
  near: { hand: [112, 158], el: [84, 160] }, far: { hand: [178, 158], el: [154, 152], item: ['bow', { top: 100, bot: 218, pull: [112, 158], glow: '#8fff9a' }] } });

H('earth', 15, 'Arachné', 'Arachné, la tisseuse changée en araignée (Grèce)', {
  grp: { top: 'swing' },
  body: 'curvy', colors: { skin: '#e0c8a8', hair: '#4a2a3a', cloth: '#8a6a2a', tail: '#2a2230', belt: '#c83a3a', steel: tone('#f4efe2') },
  bareArms: true, chest: [['collarV', { t: 'belt' }]], legs: { kind: 'spider', mark: '#c83a3a' },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'tired', color: '#e6ac3c', lash: true }, brow: { shape: 'arch', k: 3.4 }, mouth: 'fang', mouthC: '#8a2a3a', ear: false },
  gear: [['hair', { style: 'bun', bx: 84, by: 34, br: 14 }], ['thirdeyes', { color: '#c83a3a' }], ['raw', { svg: '<path d="M72 22 L98 46 M96 16 L74 46" stroke="#f4efe2" stroke-width="3" stroke-linecap="round"/>' }]],
  near: { hand: [146, 146], el: [108, 156], over: true, item: ['small', { kind: 'needle', dir: [30, -8], len: 46 }] },
  far: { pose: 'high', item: ['small', { kind: 'needle', dir: [14, -30], len: 46 }] },
  top: [['raw', { svg: '<path d="M150 142 C160 120 164 104 164 88" stroke="#f4efe2" stroke-width="1.6" fill="none" opacity="0.9"/>' }]] });

H('earth', 16, 'Gaïa', 'Gaïa, la Terre-mère (Grèce)', {
  shine: [[146, 138, 'near']],
  both: true, grp: { top: 'swing' },
  scale: 1.06, body: 'round', colors: { skin: '#a8703a', hair: '#3f8a3a', cloth: '#6aa84a', belt: '#e0c070' },
  bareArms: true, legs: { kind: 'bell', w: 60, trim: '#e0c070', panel: '#8fc85a' },
  head: { kind: 'human', jaw: 'chubby', eyes: { style: 'soft', color: '#3a2a20', lash: true }, brow: { shape: 'arch', k: 3.4, c: '#2a1c18' }, mouth: 'smile', mouthC: '#5a2a1c', nose: 'button', blush: '#c8643a' },
  gear: [['hair', { style: 'canopy' }], ['flower', { color: '#ff8ab0', x: 74, y: 60 }], ['flower', { color: '#ffe27a', x: 140, y: 44, r: 7 }]],
  near: { hand: [128, 160], el: [90, 166], handKind: 'open', dir: [1, -0.4] }, far: { hand: [162, 158], el: [166, 160], over: true, handKind: 'open', dir: [-0.4, -1] },
  top: [['glow', { x: 146, y: 136, r: 28, c: '#8fff9a', op: 0.6 }], ['disc', { x: 146, y: 138, r: 19, t: '#3f8fd8' }], ['raw', { svg: '<path d="M134 130 C140 124 150 126 152 132 C150 140 142 140 138 146 C132 142 130 136 134 130 Z M152 142 C158 140 162 144 160 150 C156 154 150 150 152 142 Z" fill="#6aa84a"/>' }]] });

H('earth', 17, 'Roi des enfers', 'Hadès, souverain du monde souterrain (Grèce)', {
  scale: 1.1, body: 'tall', colors: { skin: '#c8ccd8', hair: '#1c1a24', cloth: '#2a2630', pants: '#1c1a24', boot: '#1c1a24', cape: '#3a2a5a', belt: '#8a8a9c', steel: metal('#5a5a6c'), wood: '#2a2630', gold: metal('#8a8a9c') },
  chest: [['collarV', { t: 'cape' }]], skirt: { len: 46, t: 'cloth', trim: 'gold', flare: 5 }, legs: { kind: 'legs', leg: 'thin', foot: 'boot', stance: 'narrow' },
  head: { kind: 'human', jaw: 'long', eyes: { style: 'tired', color: '#6fd0ff', sclera: '#e9f2ff' }, brow: { k: 6, c: '#1c1a24' }, mouth: 'frown', beard: 'goat', nose: 'hook', ear: false },
  gear: [['hair', { style: 'slick' }], ['crown', { kind: 'spire', t: 'steel', gem: '#6fd0ff' }]], back: [['cape', { len: 'high' }]],
  near: { hand: [140, 172], el: [100, 166], over: true, handKind: 'open', dir: [0.2, -1], item: ['orb', { color: '#6fd0ff', r: 10, dy: 22, flame: true }] },
  far: { pose: 'staff', items: [['pole', { butt: [164, 228], end: [164, 26], head: 'bident', thick: 7 }]] } });
