// EAU — bleus, turquoise, glace, corail, nacre.
const { H, tone, metal } = require('./heroes6.cjs');
const ICE = '#bfe9ff', gold = metal('#e6ac3c');

H('water', 0, 'Garde-corail', 'soldat des récifs', {
  colors: { skin: '#eebf98', cloth: '#2f6fc8', steel: metal('#7fb8c8'), shell: '#f4c8b8', coral: '#f07a6a', iron: metal('#5a6a7a'), boot: '#eebf98', belt: '#f07a6a' },
  chest: [['scales', { t: 'steel' }]], skirt: { len: 24, strips: 5 }, legs: { kind: 'legs', leg: 'bare', foot: 'sandal', stance: 'mid' },
  head: { kind: 'human', eyes: { style: 'fierce', color: '#2a8a9a' }, brow: { k: 5, c: '#7a4a2a' }, mouth: 'shout', nose: 'button' },
  gear: [['shape', { d: 'M100 36 C82 18 58 16 40 32 C56 30 66 40 70 54 Z', t: 'shell', sh: 5 }], ['helm', { kind: 'dome', t: 'shell', plain: true }], ['raw', { svg: '<path d="M70 62 C84 46 110 40 132 44 M64 74 C84 58 118 52 148 60" stroke="#c8907a" stroke-width="2.4" fill="none" opacity="0.7"/>' }]],
  near: { hand: [124, 150], el: [90, 158], items: [['bar', { a: [116, 156], b: [192, 100], w: 7, t: 'iron' }], ['bar', { a: [148.4, 118.3], b: [161.4, 136.1], w: 6, t: 'iron' }], ['limb', { pts: [[195, 128], [208, 88], [166.5, 89]], w0: 9, w1: 9, t: 'iron', sh: 3 }]] },
  far: { noArm: true, handKind: 'none', item: ['shield', { kind: 'clam', t: 'shell' }] }, atk: 'smash' });

H('water', 1, 'Harponneur', 'pêcheur au harpon', {
  shape: { sw: 34 }, colors: { skin: '#d9a074', hair: '#2a2226', pants: '#2a4a7a', straw: '#e0c070', rope: '#c8b088', belt: '#c83a3a', boot: '#d9a074', bone: '#c8b088' },
  bare: true, bareArms: true, chest: [['muscle'], ['sash', { t: 'rope' }]], legs: { kind: 'legs', leg: 'baggy', foot: 'bare', cuffT: 'pants', stance: 'lunge' },
  head: { kind: 'human', jaw: 'square', eyes: { style: 'tired', color: '#5a3a20' }, brow: { k: 5 }, mouth: 'grin', stubble: '#2a2226' },
  gear: [['kasa']], back: [['net', {}]],
  near: { pose: 'pole' }, far: { pose: 'pole', items: [['pole', { butt: [56, 186], end: [176, 114], head: 'harpoon' }]] }, atk: 'stab', rig: { wind: -10, hit: 12 } });

H('water', 2, 'Corsaire', 'pirate des mers du sud', {
  colors: { skin: '#e2a878', hair: '#2a2226', cloth: '#f4f0e6', coat: '#1f3a6a', sleeve: '#1f3a6a', pants: '#3a3038', hat: '#2a2630', belt: '#c83a3a', boot: '#2a2226' },
  chest: [['vest', { t: 'coat' }]], skirt: { len: 44, t: 'coat', flare: 10, trim: 'gold' }, legs: { kind: 'legs', foot: 'boot', stance: 'mid' },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'angry', color: '#5a3a20' }, brow: { k: 5 }, mouth: 'grin', mustache: 'handle', stubble: '#2a2226' },
  gear: [['hair', { style: 'short' }], ['raw', { svg: '<path d="M66 74 L150 96" stroke="#1c1a24" stroke-width="3"/><ellipse cx="134" cy="88" rx="10.5" ry="9.5" fill="#1c1a24"/>' }], ['tricorn', { emblem: 'skull', feather: '#c83a3a' }]],
  near: { hand: [152, 134], el: [112, 152], over: true, item: ['gun', { kind: 'pistol' }] },
  far: { hand: [176, 162], el: [160, 158], handKind: 'none', item: ['small', { kind: 'hook', dir: [20, -14], off: -2 }] } });

H('water', 3, 'Kappa', 'kappa, génie des rivières (Japon)', {
  scale: 0.94, body: 'round', shape: { drop: 10 }, colors: { skin: '#6fae5a', muz: '#e6dca0', shell: '#7a5a34', hair: '#2a4a2a', boot: '#4a8a44' },
  bare: true, bareArms: true, noBelt: true, chest: [['belly', { t: 'muz' }], ['raw', { svg: '<path d="M100 132 L134 134 M102 146 L134 148" stroke="#b8a868" stroke-width="2.4"/>' }]],
  legs: { kind: 'legs', leg: 'thick', t: 'skin', foot: 'webbed', stance: 'mid' },
  head: { kind: 'turtle', eyes: { style: 'wide', color: '#2a2226', sclera: '#fff3a8' }, brow: { shape: 'none' } }, gear: [['dish', {}]], back: [['shell', {}]],
  near: { pose: 'guard', r: 12 }, far: { noArm: true, handKind: 'none', item: ['shield', { kind: 'leaf', t: '#5fb84a' }] }, atk: 'smash', rig: { wind: -40, hit: 30 } });

H('water', 4, 'Requin', 'homme-requin des légendes du Pacifique', {
  body: 'brute', shape: { sw: 44, hs: 1 }, colors: { skin: '#6a8aa8', muz: '#e9eef2', pants: '#1f3a6a', boot: '#6a8aa8', tail: '#6a8aa8', bone: '#ece4d0', belt: '#c83a3a' },
  bare: true, bareArms: true, chest: [['belly', { t: 'muz' }], ['muscle']], skirt: { len: 22, t: 'pants', ragged: true }, legs: { kind: 'legs', leg: 'thick', t: 'skin', foot: 'webbed' },
  head: { kind: 'shark', eyes: { style: 'dot' }, brow: { shape: 'none' } }, gear: [['fin', {}]], back: [['tail', { kind: 'lizard', w: 24 }]],
  near: { hand: [128, 172], el: [92, 160], item: ['small', { kind: 'tooth', dir: [36, 12], len: 56, t: 'bone', off: 0 }] },
  far: { hand: [172, 142], el: [162, 150], r: 14, item: ['small', { kind: 'claw', dir: [30, -8], t: 'bone', off: 6 }] }, atk: 'slash' });

H('water', 5, 'Naïade', 'naïade, nymphe des sources (Grèce)', {
  body: 'curvy', colors: { skin: '#f6dcc8', hair: '#3fb8c8', cloth: '#dff4ff', belt: '#3fb8c8', jar: '#c8824a' },
  bareArms: true, legs: { kind: 'mermaid', w: 50 },
  head: { kind: 'human', eyes: { style: 'wide', color: '#2a8a9a', lash: true }, brow: { shape: 'arch', k: 3, c: '#2a8a9a' }, mouth: 'smile', ear: false },
  gear: [['hair', { style: 'parted' }], ['flower', { color: '#fff', x: 84, y: 56 }]], back: [['hairBack', { style: 'waves' }]],
  near: { hand: [132, 152], el: [94, 162] },
  far: { hand: [158, 142], el: [154, 152], over: true, items: [['jar', { hand: [146, 146], tilt: 62, water: '#6fd0ff', stream: 'M172 148 C188 154 192 180 190 214' }]] } });

H('water', 6, 'Sirène', 'sirène au chant envoûtant', {
  body: 'curvy', colors: { skin: '#f6dcc8', hair: '#f0604a', tail: '#2fa3b8', fin: '#6fd8c8', belt: '#e6ac3c' },
  bare: true, bareArms: true, chest: [['raw', { svg: '<path d="M20 114 L190 114 L190 138 C130 148 90 148 20 138 Z" fill="#f07a6a"/>' }]], legs: 'tail',
  head: { kind: 'human', jaw: 'point', eyes: { style: 'sly', color: '#2a8a9a', lash: true }, brow: { shape: 'arch', k: 3 }, mouth: 'shout', mouthC: '#b83a4a', ear: false },
  gear: [['hair', { style: 'long' }], ['emblem', { kind: 'star', x: 84, y: 58, k: 0.8, c: '#ffd76a' }]], back: [['hairBack', { style: 'floor' }]],
  near: { pose: 'chest', handKind: 'open', dir: [1, -0.2] }, far: { pose: 'open', handKind: 'open', dir: [1, -0.5] },
  top: [['raw', { svg: '<g fill="#2f6fc8" stroke="#2f6fc8" stroke-width="2.4"><ellipse cx="168" cy="98" rx="5" ry="4"/><path d="M173 98 L173 78 L184 82" fill="none"/><ellipse cx="190" cy="66" rx="4.4" ry="3.6"/><path d="M194 66 L194 50" fill="none"/></g>' }]] });

H('water', 7, 'Samouraï-crabe', 'crabes Heike, guerriers réincarnés (Japon)', {
  body: 'heavy', colors: { skin: '#e6b88a', cloth: '#c8483a', carap: '#c8483a', pants: '#3a2a30', belt: '#2a2630', boot: '#f4ead8' },
  chest: [['lamellar', { t: 'carap' }]], skirt: { len: 22, t: 'carap', strips: 5 }, legs: { kind: 'legs', leg: 'hakama', foot: 'geta' },
  head: { kind: 'human', jaw: 'square', eyes: { style: 'angry', color: '#ffe14a', sclera: '#fff3a8' }, brow: { k: 5.5, c: '#2a2630' }, mask: 98, maskT: 'carap', ear: false },
  gear: [['helm', { kind: 'dome', t: 'carap', neck: true, moon: true }]], neck: [['pad', { t: 'carap' }], ['padFar', { t: 'carap' }]],
  near: { hand: [126, 152], el: [90, 162], handKind: 'none', w0: 27, w1: 23, sleeve: 'carap', items: [['limb', { pts: [[124, 156], [152, 176], [168, 152]], w0: 15, w1: 4, t: 'carap', sh: 4 }], ['limb', { pts: [[122, 146], [150, 110], [174, 142]], w0: 23, w1: 4, t: 'carap', sh: 5 }], ['disc', { x: 124, y: 152, r: 14, t: 'carap', sh: 4 }]] },
  far: { hand: [174, 108], el: [164, 132], item: ['sword', { to: [208, 26], w: 13, curve: 7, guard: 9 }] } });

H('water', 8, 'Jötunn des glaces', 'géant du givre (mythologie nordique)', {
  scale: 1.2, body: 'brute', colors: { skin: '#8ab8e0', hair: '#f4f8ff', fur: '#f4f8ff', belt: '#5a4634', ice: ICE, boot: '#5a4634' },
  bare: true, bareArms: true, chest: [['muscle']], skirt: { len: 28, t: 'fur', ragged: true }, legs: { kind: 'legs', leg: 'thick', t: 'skin', foot: 'fur', furT: 'fur' },
  head: { kind: 'human', jaw: 'long', eyes: { style: 'angry', color: '#2f6fc8', sclera: '#f4f8ff' }, brow: { k: 6.5, c: '#f4f8ff' }, beard: 'ice', nose: 'big', ear: false },
  gear: [['hair', { style: 'ice' }]],
  near: { pose: 'hip', r: 15 }, far: { hand: [178, 118], el: [166, 140], r: 15, item: ['axe', { to: [198, 34], z: 1.15, t: 'ice', back: 30 }] }, atk: 'smash' });

H('water', 9, 'Chasseuse des glaces', 'Sedna, déesse inuite de la mer', {
  main: 'far', grp: { back: 'swing' },
  shape: { sw: 34 }, colors: { skin: '#d9a074', cloth: '#b88a5a', pants: '#8a6a44', hood: '#b88a5a', fur: '#f4f0e6', boot: '#8a6a44', glove: '#f4f0e6', bone: '#ece4d0', belt: '#6a4a2e' },
  skirt: { len: 20, trim: 'fur' }, legs: { kind: 'legs', leg: 'thick', foot: 'fur', furT: 'fur', stance: 'lunge' },
  head: { kind: 'human', eyes: { style: 'angry', color: '#2a2226' }, brow: { k: 4.5, c: '#2a2226' }, mouth: 'flat', blush: '#e0786a', ear: false },
  gear: [['hood', { kind: 'parka', trim: 'fur', trimW: 11 }]],
  near: { pose: 'point', handKind: 'open', dir: [1, -0.1] },
  far: { hand: [170, 92], el: [160, 124], items: [['pole', { butt: [20, 148], end: [204, 80], head: 'harpoon', t: 'bone', layer: 'back' }]] } });

H('water', 10, 'Roussalka', 'roussalka, esprit des noyées (monde slave)', {
  body: 'slim', colors: { skin: '#b8e0d0', hair: '#1f4a3a', cloth: '#e9f4f0', boot: '#b8e0d0', belt: '#3f8a6a', steel: tone('#dff4ff') },
  bareArms: true, skirt: { len: 40, t: 'cloth', ragged: true, flare: 8 }, legs: { kind: 'legs', leg: 'bare', foot: 'bare', stance: 'narrow' },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'wide', color: '#1f4a3a', sclera: '#f4fffa' }, brow: { shape: 'none' }, mouth: 'grin', mouthC: '#1f4a3a', nose: 'none', ear: false },
  gear: [['hair', { style: 'long' }], ['leaves', { t: '#3f8a6a' }]], back: [['hairBack', { style: 'mid' }]],
  near: { hand: [150, 152], el: [112, 160], over: true, item: ['small', { kind: 'claw', dir: [30, -4], off: 2, len: 26 }] },
  far: { pose: 'open', hand: [176, 122], el: [154, 138], item: ['small', { kind: 'claw', dir: [28, -16], off: 2, len: 26 }] } });

H('water', 11, 'Mazu', 'Mazu, protectrice des marins (Chine)', {
  colors: { skin: '#f8dcc4', hair: '#2a2226', cloth: '#c83a3a', belt: '#e6ac3c', iron: gold },
  chest: [['wrap', { t: 'gold' }]], legs: { kind: 'straight', w: 42, panel: 'gold', trim: 'gold' },
  head: { kind: 'human', eyes: { style: 'closed', lash: true }, brow: { shape: 'flat', k: 3 }, mouth: 'smile', mouthC: '#c83a3a' },
  gear: [['hair', { style: 'short' }], ['mian', {}]],
  near: { hand: [128, 152], el: [92, 166], w0: 24, w1: 32, handKind: 'none' }, far: { pose: 'staff', w0: 20, w1: 26, item: ['staff', { kind: 'lantern', top: 44 }] } });

H('water', 12, 'Yuki-onna', 'la femme des neiges (Japon)', {
  grp: { top: 'far' },
  body: 'slim', colors: { skin: '#e9f2ff', hair: '#1c1a24', cloth: '#f4f8ff', belt: '#6fc8f0' },
  chest: [['wrap', { t: 'belt' }]], legs: { kind: 'straight', w: 40, base: 'mist', baseC: '#dff4ff', folds: true },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'tired', color: '#6fc8f0', lash: true }, brow: { shape: 'flat', k: 3, c: '#3a3a5a' }, mouth: 'o', mouthC: '#6f8fc8', ear: false },
  gear: [['hair', { style: 'long' }]], back: [['hairBack', { style: 'windy' }]],
  near: { pose: 'chest', w0: 20, w1: 30, handKind: 'none' }, far: { hand: [160, 118], el: [156, 140], handKind: 'open', dir: [1, -0.25] },
  top: [['glow', { x: 184, y: 100, r: 20, c: ICE, op: 0.7 }], ['raw', { svg: '<g fill="#dff4ff" stroke="#6f8fc8" stroke-width="1.5" stroke-linejoin="round"><path d="M182 86 l7 12 l-7 12 l-7 -12 Z"/><path d="M199 104 l5 8 l-5 8 l-5 -8 Z"/><path d="M197 76 l4 6 l-4 6 l-4 -6 Z"/></g>' }]] });

H('water', 13, 'Poséidon', 'Poséidon, dieu des mers (Grèce)', {
  scale: 1.15, body: 'brute', colors: { skin: '#e2a878', hair: '#dff4ff', scale: '#2fa3b8', belt: '#e6ac3c', cape: '#1f5a8a', steel: gold, wood: '#c9903c', boot: '#e2a878' },
  bare: true, bareArms: true, bracers: 'gold', chest: [['muscle']], skirt: { len: 26, t: 'scale', strips: 6, trim: 'gold' }, legs: { kind: 'legs', leg: 'bare', foot: 'sandal', shin: 'gold', stance: 'lunge' },
  head: { kind: 'human', jaw: 'square', eyes: { style: 'fierce', color: '#2a8a9a' }, brow: { k: 6.5, c: '#b8d8e8' }, beard: 'curly', nose: 'big', ear: false },
  gear: [['hair', { style: 'curly' }], ['crown', { gem: '#3fb8c8' }]], back: [['cape', { len: 'wind' }], ['hairBack', { style: 'waves' }]], neck: [['pad', { t: 'gold' }]],
  both: true, near: { hand: [100, 159], el: [78, 166] }, far: { pose: 'pole', items: [['pole', { butt: [50, 190], end: [172, 114], head: 'trident', thick: 7.5 }]] }, atk: 'stab', rig: { wind: -10, hit: 12 } });

H('water', 14, 'Skadi', 'Skadi, chasseresse de l\'hiver (Scandinavie)', {
  colors: { skin: '#f6dcc8', hair: '#f0d070', cloth: '#5a7a9a', pants: '#3d4a5e', hood: '#c8ccd6', fur: '#f4f0e6', bow: '#dff4ff', boot: '#3d4a5e', glove: '#3d4a5e', ski: '#8a5a34', belt: '#5a4634' },
  skirt: { len: 18, trim: 'fur' }, legs: { kind: 'legs', foot: 'fur', furT: 'fur', stance: 'mid' },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'angry', color: '#6fc8f0', lash: true }, brow: { k: 4 }, mouth: 'frown', ear: false,
    paint: '<path d="M88 100 L104 104 M88 108 L100 110" stroke="#2f6fc8" stroke-width="3" stroke-linecap="round"/>' },
  gear: [['hood', { kind: 'cowl', ears: true, teeth: true, nose: '#2a2630' }]], back: [['shape', { d: 'M30 224 L180 224 L196 212 L200 217 L184 232 L30 232 Z', t: 'ski', sh: 3 }]], neck: [['fur']],
  near: { hand: [124, 152], el: [92, 160], items: [['glow', { x: 184, y: 128, r: 14, c: ICE, op: 0.7 }], ['bar', { a: [102, 162], b: [178, 129], w: 4, t: 'wood' }], ['shape', { d: 'M196 121 L180 138 L174 122 Z', t: 'bow', sh: 2 }]] },
  far: { pose: 'fwd', item: ['bow', { top: 50, bot: 206, pull: [162, 129], arrow: false }] } });

H('water', 15, 'Scylla', 'Scylla, monstre du détroit (Grèce)', {
  body: 'curvy', colors: { skin: '#c8b8e0', hair: '#3a2a5a', cloth: '#3a2a5a', tail: '#6a4a9a', belt: '#f07a6a', coral: '#f07a6a' },
  bareArms: true, chest: [['scales', { t: '#4a3a6a' }]], legs: 'tentacles',
  head: { kind: 'human', jaw: 'point', eyes: { style: 'fierce', color: '#ffe14a', sclera: '#fff3a8', slit: true, lash: true }, brow: { shape: 'arch', k: 3.6 }, mouth: 'fang', mouthC: '#5a2a6a', ear: false },
  gear: [['hair', { style: 'long' }], ['shape', { d: 'M86 80 C72 60 54 56 42 62 C52 68 52 78 44 86 C56 86 62 94 58 104 C72 102 84 94 86 80 Z', t: 'coral', sh: 4 }]], back: [['hairBack', { style: 'locs' }]],
  near: { pose: 'up', item: ['small', { kind: 'hook', dir: [26, -30], off: 4 }] }, far: { pose: 'high', item: ['small', { kind: 'hook', dir: [20, -30], off: 4 }] } });

H('water', 16, 'Mère des eaux', 'Yemoja, mère des eaux (Yoruba)', {
  body: 'round', shape: { sw: 30, ww: 28, belly: 6 }, colors: { skin: '#7a4a34', cloth: '#f4f8ff', belt: '#3f8fd8', turban: '#f4f8ff', cape: '#3f8fd8', fan: '#dff4ff' },
  bareArms: true, legs: { kind: 'bell', w: 58, tiers: true, panel: '#6fc8f0', trim: '#3f8fd8' },
  head: { kind: 'human', jaw: 'chubby', eyes: { style: 'happy', lash: true }, brow: { shape: 'arch', k: 3.4, c: '#2a1c18' }, mouth: 'smile', mouthC: '#3a1c1c', nose: 'button' },
  gear: [['turban', { kind: 'gele' }]], back: [['cape', { len: 'wide' }]], neck: [['beads', { t: '#f4f8ff', r: 5 }]],
  near: { pose: 'hip', over: true }, far: { hand: [162, 106], el: [162, 132], item: ['fanRound', { emblem: 'wave', ec: '#3f8fd8' }] } });

H('water', 17, 'Roi dragon', 'Ryūjin, roi dragon des mers (Japon)', {
  scale: 1.1, body: 'tall', shape: { sw: 32 }, colors: { skin: '#2fa39a', muz: '#bfe8d8', hair: '#f4f8ff', cloth: '#1f3a6a', belt: '#e6ac3c', tail: '#2fa39a', bone: gold },
  skirt: { len: 42, t: 'cloth', flap: 'gold', flapLen: 0, trim: 'gold', flare: 7 }, legs: { kind: 'legs', leg: 'baggy', t: 'cloth', foot: 'talon', footT: 'skin', stance: 'mid' },
  head: { kind: 'dragon', eyes: { style: 'tired', color: '#ffe14a', sclera: '#fff3a8', slit: true } },
  gear: [['antlers', { t: 'bone' }], ['frill', { t: 'hair', len: 20 }], ['whiskers', {}]], back: [['tail', { kind: 'up', w: 18 }]],
  near: { hand: [70, 162], el: [66, 146], w0: 22, w1: 28, handKind: 'none' },
  far: { hand: [174, 178], el: [156, 166], handKind: 'open', dir: [0.2, -1], w0: 18, w1: 26, item: ['orb', { color: '#dff4ff', r: 13, dy: 26 }] } });
