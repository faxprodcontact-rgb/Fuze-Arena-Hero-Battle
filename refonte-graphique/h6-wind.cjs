// VENT — bleu-vert, ciel, blanc, argent, violet d'orage, jaune de foudre.
const { H, tone, metal } = require('./heroes6.cjs');
const silver = metal('#c2ccda');

H('wind', 0, 'Garde des cimes', 'montagnard gardien des cols', {
  body: 'heavy', colors: { skin: '#eebf98', cloth: '#2f8f8a', fur: '#f4f0e6', pants: '#3d4a5e', boot: '#5a4634', hood: '#2f8f8a', steel: metal('#a9b4c2'), shieldFace: '#2f8f8a', belt: '#5a4634' },
  chest: [['collarV', { t: 'fur' }]], legs: { kind: 'legs', leg: 'thick', foot: 'fur', furT: 'fur', stance: 'mid' },
  head: { kind: 'human', jaw: 'chubby', eyes: { style: 'soft', color: '#2a8a9a' }, brow: { k: 5.5, shape: 'arch', c: '#7a4a2a' }, mouth: 'grin', nose: 'big', blush: '#e0786a', ear: false },
  gear: [['hood', { kind: 'peak', trim: 'fur', trimW: 8 }]],
  near: { pose: 'up', item: ['mace', { kind: 'pick', to: [188, 88] }] },
  far: { noArm: true, handKind: 'none', item: ['shield', { kind: 'heater', t: 'wood', emblem: 'swirl', ec: '#f4f8ff' }] } });

H('wind', 1, 'Pillard du nord', 'guerrier viking', {
  shape: { sw: 36 }, colors: { skin: '#f2c9a4', hair: '#e8c05a', cloth: '#4a6a8a', pants: '#5a4634', boot: '#3a2a22', fur: '#8a6a4a', shieldFace: '#b8482a', steel: metal('#a9b4c2') },
  chest: [['scales', { t: 'steel' }]], skirt: { len: 18 }, legs: { kind: 'legs', foot: 'fur', furT: 'fur', wrap: '#8a6a4a', stance: 'lunge' },
  head: { kind: 'human', jaw: 'square', eyes: { style: 'fierce', color: '#3f8fd8' }, brow: { k: 6 }, beard: 'short', ear: false },
  gear: [['helm', { kind: 'dome', nose: true, plain: true }]], back: [['roundBack', { t: 'wood', face: 'shieldFace' }]],
  near: { hand: [54, 108], el: [50, 134], item: ['axe', { to: [34, 34], z: 0.95, side: 1 }] }, far: { hand: [176, 150], el: [162, 154] } });

H('wind', 2, 'Archer des steppes', 'cavalier-archer des steppes', {
  colors: { skin: '#e6b88a', hair: '#2a2226', cloth: '#8a5a3a', hat: '#b8483a', fur: '#f4f0e6', belt: '#2f8f8a', bow: '#c9a070', boot: '#3a2a22', pants: '#3d4a5e', quiv: '#5a3a22' },
  chest: [['wrap', { t: 'belt' }]], skirt: { len: 40, trim: 'belt', flare: 10 }, legs: { kind: 'legs', foot: 'boot', stance: 'mid' },
  head: { kind: 'human', eyes: { style: 'wink', color: '#5a3a20' }, brow: { k: 4.5 }, mouth: 'smirk', nose: 'button', stubble: '#3a2a22', ear: false },
  gear: [['furhat', { point: true }]], back: [['shape', { d: 'M62 116 L84 108 L98 176 L78 184 Z', t: 'quiv', sh: 5 }], ['raw', { svg: '<path d="M60 104 l-6 -22 l8 6 l2 -12 l6 26 Z M72 100 l-4 -24 l8 6 l4 -10 l2 26 Z" fill="#f4f0e6" stroke="#2c1626" stroke-width="2" stroke-linejoin="round"/>' }], ['hairBack', { style: 'braid' }]],
  near: { pose: 'pull' }, far: { pose: 'fwd', item: ['bow', { recurve: true, top: 74, bot: 184, layer: 'behind' }] } });

H('wind', 3, 'Chevalier-griffon', 'chevalier des cieux', {
  body: 'heavy', colors: { skin: '#eebf98', cloth: '#f4f8ff', steel: silver, sleeve: silver, glove: silver, shieldFace: '#2f8f8a', cape: '#2f8f8a', crest: '#f4f8ff', pants: silver, boot: silver, belt: '#e6ac3c' },
  chest: [['plate', { t: 'steel' }], ['stripe', { t: '#2f8f8a' }]], skirt: { len: 22, flap: '#2f8f8a', flapLen: 12 }, legs: { kind: 'legs', leg: 'thick', foot: 'sabaton', stance: 'mid' },
  head: { kind: 'human', eyes: { style: 'none' }, mouth: 'none', nose: 'none', ear: false },
  gear: [['helm', { kind: 'great' }], ['shape', { d: 'M112 34 C104 6 70 -6 34 10 C54 14 62 24 62 38 C46 36 36 40 26 50 C48 50 66 54 80 44 C92 40 102 38 112 34 Z', t: 'cape', sh: 6 }]],
  back: [['cape', { len: 'long' }]], neck: [['pad', { t: 'steel' }], ['padFar', { t: 'steel' }]],
  near: { hand: [106, 162], el: [80, 160], items: [['pole', { butt: [26, 176], end: [212, 136], head: 'spear', hl: 36, hw: 12, thick: 7.5 }]] }, atk: 'stab',
  far: { noArm: true, handKind: 'none', item: ['shield', { kind: 'tower', emblem: 'wing', ec: '#f4f8ff', es: 1.5 }] } });

H('wind', 4, 'Ombre du vent', 'shinobi au grand shuriken', {
  body: 'slim', colors: { skin: '#e6b88a', hair: '#2a2226', cloth: '#1f4a52', pants: '#18383e', boot: '#12282c', glove: '#12282c', belt: '#6fd8c8', scarf: '#6fd8c8' },
  legs: { kind: 'legs', leg: 'thin', foot: 'shoe', stance: 'lunge', wrap: '#6fd8c8' },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'sly', color: '#6fd8c8' }, brow: { k: 4 }, mask: 97, band: { t: 'belt', y: 58, k: 8 } },
  gear: [['hair', { style: 'short', band: { t: 'belt', y: 58, k: 8 } }]], back: [['scarfTail', {}], ['hairBack', { style: 'ponyHigh' }]],
  near: { pose: 'raise', items: [['shuriken', { c: [48, 88], r: 42, layer: 'back' }]] },
  far: { pose: 'stab', handBehind: true, item: ['small', { kind: 'kunai', dir: [28, -22], layer: 'behind' }] } });

H('wind', 5, 'Sylphe', 'sylphe, esprit de l\'air', {
  shine: [[154, 110, 'near']],
  scale: 0.84, body: 'slim', shape: { hs: 1.1 }, colors: { skin: '#f8e0cc', hair: '#9fe0b0', cloth: '#7fcf8a', belt: '#e6ac3c', boot: '#5fae6a', pants: '#f8e0cc' },
  skirt: { len: 26, ragged: true, flare: 10 }, legs: { kind: 'float' },
  head: { kind: 'human', eyes: { style: 'happy' }, brow: { shape: 'arch', k: 3 }, mouth: 'smile', blush: '#ff9aa8', ear: false },
  gear: [['ears', { kind: 'elf' }], ['hair', { style: 'bun', bx: 104, by: 28, br: 13 }], ['flower', { color: '#fff', x: 132, y: 44, r: 7 }]], back: [['fairy', { color: '#c8f4ff' }]],
  near: { hand: [138, 113], el: [98, 142], over: true, items: [['flute', { a: [116, 111], b: [184, 105], t: '#e6c98a' }]] },
  far: { hand: [164, 109], el: [156, 132], over: true, tint: true } });

H('wind', 6, 'Barde des tempêtes', 'Orphée, le musicien des légendes grecques', {
  shine: [[166, 120, 'far']],
  colors: { skin: '#f2c9a4', hair: '#7a4a2a', cloth: '#f4f8ff', belt: '#2f8f8a', cape: '#2f8f8a', leaf: '#e6ac3c', boot: '#f2c9a4' },
  bare: true, bareArms: true, chest: [['muscle'], ['toga', { t: 'cloth' }]], skirt: { len: 26 }, legs: { kind: 'legs', leg: 'bare', foot: 'sandal', stance: 'narrow' },
  head: { kind: 'human', eyes: { style: 'soft', color: '#2a8a9a' }, brow: { shape: 'arch', k: 3.6 }, mouth: 'o' },
  gear: [['hair', { style: 'curly' }], ['leaves', { t: 'leaf' }]], back: [['cape', { len: 'wind' }]],
  far: { pose: 'staff', hand: [162, 152], item: ['lyre', {}] }, near: { hand: [150, 132], el: [112, 150], over: true, handKind: 'open', dir: [1, -0.5] } });

H('wind', 7, 'Valkyrie', 'valkyrie, guerrière d\'Odin', {
  body: 'curvy', shape: { sw: 30 }, colors: { skin: '#f6d2b4', hair: '#f0d070', cloth: '#f4f8ff', steel: silver, bone: '#f4f8ff', shieldFace: '#3f6fd8', boot: silver, belt: '#8a6a4a', cape: '#3f6fd8' },
  chest: [['scales', { t: 'steel' }]], skirt: { len: 28, strips: 5, trim: 'gold' }, legs: { kind: 'legs', leg: 'bare', foot: 'sabaton', shin: 'steel', stance: 'mid' },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'angry', color: '#3f8fd8', lash: true }, brow: { k: 3.6 }, mouth: 'flat', ear: false },
  gear: [['helm', { kind: 'dome', wings: true }]], back: [['cape', { len: 'short' }], ['hairBack', { style: 'braid' }]],
  near: { pose: 'up', item: ['pole', { butt: [84, 182], end: [176, 98], head: 'spear' }] },
  far: { noArm: true, handKind: 'none', item: ['shield', { kind: 'round' }] }, atk: 'stab', rig: { wind: -14, hit: 16 } });

H('wind', 8, 'Tengu', 'tengu, démon-corbeau des montagnes (Japon)', {
  shape: { sw: 34 }, colors: { skin: '#c83a3a', hair: '#f4f0e6', cloth: '#f4f0e6', pants: '#2a2630', wing: '#2a2630', belt: '#2a2630', fan: '#e6ac3c', boot: '#f4f0e6' },
  chest: [['wrap', { t: '#2a2630' }]], legs: { kind: 'legs', leg: 'hakama', foot: 'geta', stance: 'mid' },
  head: { kind: 'human', jaw: 'long', eyes: { style: 'angry', color: '#ffe14a', sclera: '#fff3a8' }, brow: { k: 7, c: '#f4f0e6' }, mouth: 'frown', nose: 'none', ear: false },
  gear: [['hair', { style: 'slick' }], ['shape', { d: 'M98 32 L122 30 L124 48 L100 50 Z', t: 'pants', sh: 3 }], ['longnose', {}]],
  back: [['wings', { kind: 'feather' }], ['hairBack', { style: 'mid' }]], neck: [['beads', { t: '#f0a030', r: 6 }]],
  main: 'far', near: { hand: [58, 112], el: [54, 136], item: ['small', { kind: 'fan', dir: [-8, -30], t: 'fan' }] },
  far: { hand: [170, 152], el: [156, 152], item: ['sword', { to: [216, 122], w: 13, curve: 7, guard: 9 }] } });

H('wind', 9, 'Garuda', 'Garuda, l\'homme-aigle (Inde)', {
  colors: { skin: '#f4ead8', cloth: '#d8a040', sleeve: '#d8a040', glove: '#d8a040', pants: '#c8502a', wing: '#c8502a', belt: '#e6ac3c', boot: '#e6ac3c', crest: '#c8502a' },
  bracers: 'gold', legs: { kind: 'legs', leg: 'baggy', foot: 'talon', cuffT: 'gold', stance: 'mid' }, neck: [['collar', { gem: '#c8502a' }]],
  head: { kind: 'eagle', eyes: { style: 'fierce', color: '#c8502a', sclera: '#fff3a8' }, browC: '#8a3a1c' },
  gear: [['hair', { style: 'crest', t: 'crest' }]], back: [['wings', { kind: 'big' }]],
  near: { hand: [46, 120], el: [54, 140], items: [['chakram', { c: [34, 98], r: 20, glow: '#ffe27a' }]] },
  far: { hand: [178, 158], el: [160, 154], item: ['chakram', { c: [190, 140], r: 16 }] } });

H('wind', 10, 'Kamaitachi', 'kamaitachi, la belette aux faucilles (Japon)', {
  scale: 0.9, body: 'slim', shape: { lean: 5, hdx: 2 }, colors: { skin: '#d8b078', muz: '#f6ead6', cloth: '#2f8f8a', tail: '#d8b078', tip: '#f6ead6', scarf: '#c83a3a', boot: '#b8905a', belt: '#5a4634' },
  bare: true, bareArms: true, chest: [['belly', { t: 'muz' }], ['vest', { t: 'cloth' }]], legs: { kind: 'legs', leg: 'thin', t: 'skin', foot: 'paw', stance: 'lunge' },
  head: { kind: 'weasel', eyes: { style: 'fierce', color: '#c83a3a', sclera: '#fff3a8' } }, gear: [['ears', { kind: 'cat' }]],
  back: [['tail', { kind: 'fox' }], ['scarfTail', {}]], neck: [['scarf']],
  near: { hand: [48, 112], el: [52, 136], item: ['small', { kind: 'sickle', dir: [-4, -32] }] },
  far: { hand: [174, 152], el: [158, 152], item: ['small', { kind: 'sickle', dir: [30, -10] }] } });

H('wind', 11, 'Apsara', 'apsara, danseuse céleste (Inde)', {
  shine: [[164, 66, 'far', 10, '#ffd0e6']],
  body: 'curvy', colors: { skin: '#d9a074', hair: '#2a2226', cloth: '#2fa39a', belt: '#e6ac3c', scarf: '#ffb0cf', pants: '#2fa39a', boot: '#d9a074' },
  bare: true, bareArms: true, bracers: 'gold', chest: [['raw', { svg: '<path d="M20 114 L190 114 L190 138 C130 148 90 148 20 138 Z" fill="#2fa39a"/><path d="M20 138 C90 148 130 148 190 138" stroke="#e6ac3c" stroke-width="4" fill="none"/>' }]],
  skirt: { len: 24, flare: 4, trim: 'gold' }, legs: { kind: 'dance' },
  head: { kind: 'human', eyes: { style: 'calm', color: '#5a3a20', lash: true }, brow: { shape: 'arch', k: 3 }, mouth: 'smile', mouthC: '#b83a4a' },
  gear: [['hair', { style: 'bun', bx: 106, by: 26, br: 12 }], ['crown', { kind: 'spire', gem: '#ff5a8a' }]], back: [['scarfTail', { two: true }]], neck: [['beads', { t: 'gold', r: 3.4 }]],
  far: { pose: 'high', handKind: 'open', dir: [0.3, -1], item: ['lotus', { color: '#ffb0cf' }] }, near: { hand: [148, 148], el: [110, 156], over: true, handKind: 'open', dir: [1, 0.3] } });

H('wind', 12, 'Fūjin', 'Fūjin, dieu du vent (Japon)', {
  shine: [[84, 10, 'torso']],
  scale: 1.05, body: 'heavy', shape: { belly: 10 }, colors: { skin: '#5fae6a', hair: '#3a3a4e', pelt: '#e8c070', belt: '#c83a3a', bag: '#f4f0e6', bone: '#f4ead8', boot: '#5fae6a' },
  bare: true, bareArms: true, chest: [['muscle']], skirt: { len: 28, t: 'pelt', flare: 5 }, legs: { kind: 'legs', leg: 'thick', t: 'skin', foot: 'bare', anklet: 'gold', stance: 'lunge' },
  head: { kind: 'human', jaw: 'chubby', eyes: { style: 'wide', color: '#ffe14a', sclera: '#fff3a8' }, brow: { k: 6, c: '#3a3a4e', shape: 'angry' }, mouth: 'grin', tusks: 'small', nose: 'big', ear: false },
  gear: [['hair', { style: 'wild', len: 28 }], ['horns', { kind: 'one' }]], back: [['windbag', { a: [42, 172], b: [176, 166], top: [108, -4], t: '#bfeee0' }]],
  near: { hand: [44, 134], el: [50, 146] }, far: { hand: [174, 128], el: [166, 142] } });

H('wind', 13, 'Roi singe', 'le Roi singe du Voyage en Occident (Chine)', {
  body: 'slim', colors: { skin: '#c8843a', muz: '#f4d8b0', cloth: '#c83a3a', steel: metal('#e6ac3c'), pants: '#c83a3a', tail: '#c8843a', scarf: '#c83a3a', wood: '#c83a3a', boot: '#2a2630', tiger: '#f0a030', crest: '#c83a3a', belt: '#2a2630' },
  bareArms: true, bracers: 'gold', chest: [['scales', { t: 'steel' }]], skirt: { len: 22, t: 'tiger', strips: 4 }, legs: { kind: 'legs', leg: 'baggy', foot: 'boot', stance: 'lunge', cuffT: 'gold' },
  head: { kind: 'monkey', eyes: { style: 'sly', color: '#c8641e', sclera: '#fff3a8' }, band: { t: 'gold', y: 54, k: 8 } },
  gear: [['plumes', {}], ['ears', { kind: 'side' }]], back: [['tail', { kind: 'monkey' }], ['scarfTail', {}]], neck: [['scarf']],
  near: { pose: 'pole' }, far: { pose: 'pole', items: [['pole', { butt: [50, 190], end: [178, 110], head: 'staff', thick: 8 }]] } });

H('wind', 14, 'Maître de la foudre', 'Zeus, roi des dieux (Grèce)', {
  main: 'far',
  scale: 1.1, body: 'brute', colors: { boot: '#f2c9a4', skin: '#f2c9a4', hair: '#e8c05a', cloth: '#f4f8ff', belt: '#e6ac3c', leaf: '#e6ac3c', cape: '#5a4a8a' },
  bareArms: true, bracers: 'gold', chest: [['raw', { svg: '<path d="M0 80 L130 80 C122 122 92 144 0 156 Z" fill="#f2c9a4"/><path d="M130 86 C122 124 94 146 30 156" stroke="#b8c4d8" stroke-width="3" fill="none"/>' }], ['muscle']],
  skirt: { len: 34, t: 'cloth', flare: 6, trim: 'gold' }, legs: { kind: 'legs', leg: 'bare', foot: 'sandal', stance: 'wide' }, head: { kind: 'human', jaw: 'square', eyes: { style: 'glow', color: '#dff4ff', lid: '#8a6a2a' }, brow: { k: 6.5, c: '#b8902a' }, nose: 'big', beard: 'full' },
  gear: [['hair', { style: 'slick' }], ['leaves', { t: 'leaf' }]], back: [['cape', { len: 'long' }], ['hairBack', { style: 'mid' }]],
  near: { pose: 'hip', r: 13 }, far: { hand: [168, 92], el: [166, 126], item: ['bolt', {}] } });

H('wind', 15, 'Morrigane', 'la Morrígan, déesse-corbeau (Irlande)', {
  body: 'tall', colors: { skin: '#f0e2d8', hair: '#1c1a24', cloth: '#2a2630', pants: '#1c1a24', boot: '#12101a', wing: '#1c1a24', fur: '#1c1a24', belt: '#8a2a3a', gold: metal('#8a8a9c'), glove: '#12101a' },
  chest: [['collarV', { t: 'belt' }]], skirt: { len: 30, ragged: true }, legs: { kind: 'legs', leg: 'thin', foot: 'boot', stance: 'narrow' },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'sly', color: '#c83a3a', lash: true }, brow: { shape: 'arch', k: 3.4 }, mouth: 'smirk', mouthC: '#8a2a3a', ear: false },
  gear: [['hair', { style: 'parted' }], ['tiara', { gem: '#c83a3a' }]], back: [['wings', { kind: 'down' }], ['hairBack', { style: 'long' }]], neck: [['fur', {}]],
  near: { hand: [122, 164], el: [86, 164], item: ['sword', { to: [188, 138], w: 13, guard: 10 }] }, far: { pose: 'up', handKind: 'open', dir: [0.6, -1] } });

H('wind', 16, 'Séraphin', 'séraphin aux six ailes', {
  shine: [[210, 86, 'far']],
  colors: { boot: '#e6ac3c', skin: '#f8dcc4', hair: '#f0d070', cloth: '#f4f8ff', belt: '#e6ac3c', wing: '#f4f8ff' },
  skirt: { len: 36, t: 'cloth', flare: 8, trim: 'gold' }, legs: { kind: 'float', t: 'skin', footT: 'boot' },
  head: { kind: 'human', eyes: { style: 'calm', color: '#3f8fd8' }, brow: { shape: 'flat', k: 3, c: '#c8a040' }, mouth: 'flat', ear: false },
  gear: [['hair', { style: 'curly' }]], back: [['halo', {}], ['wings', { kind: 'feather', glow: '#fff3c0' }], ['wings', { kind: 'down' }], ['wings', { kind: 'small' }]],
  near: { pose: 'chest', handKind: 'open', dir: [1, -0.2] }, far: { hand: [172, 106], el: [160, 132], item: ['horn', { dir: [1, -0.55], t: 'gold' }] } });

H('wind', 17, 'Raijin', 'Raijin, dieu du tonnerre (Japon)', {
  scale: 1.08, body: 'brute', colors: { skin: '#7a82c8', hair: '#ffe14a', drum: '#c83a3a', pelt: '#3a3058', belt: '#e6ac3c', bone: '#f4ead8', wood: '#f4ead8', boot: '#7a82c8' },
  bare: true, bareArms: true, bracers: 'gold', chest: [['muscle']], skirt: { len: 26, t: 'pelt', ragged: true }, legs: { kind: 'legs', leg: 'thick', t: 'skin', foot: 'bare', anklet: 'gold' },
  head: { kind: 'human', jaw: 'square', eyes: { style: 'glow', color: '#ffe14a', lid: '#3a3058' }, brow: { k: 6, c: '#3a3058' }, mouth: 'gritted', nose: 'none', ear: false },
  gear: [['hair', { style: 'crest' }], ['horns', { kind: 'small' }]], back: [['cloud'], ['drums', {}]],
  near: { pose: 'raise', hand: [64, 98], el: [56, 126], item: ['small', { kind: 'stick', dir: [-8, -30], t: 'wood' }] },
  far: { pose: 'high', item: ['small', { kind: 'stick', dir: [8, -30], t: 'wood' }] } });
