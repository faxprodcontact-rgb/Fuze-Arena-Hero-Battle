// VENT — bleu-vert, ciel, blanc, argent, violet d'orage, jaune de foudre.
const { H, tone, metal } = require('./heroes72.cjs');
const BOLT = '#ffe14a';

H('wind', 0, 'Garde des cimes', 'montagnard gardien des cols', {
  colors: { skin: '#eebf98', cloth: '#2f8f8a', pants: '#3d4a5e', hood: '#2f8f8a', fur: '#f4f0e6', shieldFace: '#2f8f8a', steel: metal('#a9b4c2') },
  gear: [['hood', {}]], neck: [['fur']], eyes: { color: '#2a8a9a' },
  near: ['axe', { end: [170, 84], z: 0.8 }], far: ['shield', { kind: 'kite', emblem: 'swirl', ec: '#f4f8ff' }] });

H('wind', 1, 'Pillard du nord', 'guerrier viking', {
  colors: { skin: '#f2c9a4', hair: '#e8c05a', cloth: '#4a6a8a', pants: '#5a4634', fur: '#8a6a4a', steel: metal('#a9b4c2') },
  gear: [['helm', { nose: true, plain: true }]], neck: [['fur']], face: { beard: 'fork' }, eyes: { color: '#3f8fd8' },
  near: ['shoulder', { kind: 'axe' }] });

H('wind', 2, 'Archer des steppes', 'cavalier-archer des steppes', {
  colors: { skin: '#e6b88a', hair: '#2a2226', cloth: '#8a5a3a', pants: '#3d4a5e', hat: '#b8483a', fur: '#f4f0e6', belt: '#2f8f8a', bow: '#c9a070' },
  back: [['braid']], gear: [['furhat', {}]], eyes: { color: '#5a3a20' },
  near: ['pull'], far: ['bow', { top: 74, bot: 184, bulge: 192 }] });

H('wind', 3, 'Chevalier-griffon', 'chevalier des cieux', {
  colors: { skin: '#f2c9a4', cloth: '#f4f8ff', pants: '#3d4a5e', steel: metal('#c2ccda'), crest: '#f4f8ff', shieldFace: '#2f8f8a', cape: '#2f8f8a' },
  armor: 'steel', back: [['cape', { len: 'long' }]], gear: [['helm', { crest: 'low', cheek: true }]], neck: [['pad']], eyes: { color: '#3f8fd8' },
  near: ['mace', {}], far: ['shield', { kind: 'tower', emblem: 'star', ec: '#ffd76a' }] });

H('wind', 4, 'Ombre du vent', 'shinobi au grand shuriken', {
  build: 'slim', colors: { skin: '#e6b88a', hair: '#2a2226', cloth: '#1f4a52', pants: '#18383e', boot: '#12282c', glove: '#12282c', sleeve: '#1f4a52', belt: '#6fd8c8' },
  band: { tone: '#6fd8c8', y: 58, k: 8 }, back: [['shuriken'], ['pony']], gear: [['hair', { style: 'short' }]], face: { mask: 97 }, brows: false,
  eyes: { color: '#6fd8c8' }, near: ['dagger', { kind: 'kunai' }], far: ['dagger', { kind: 'kunai' }] });

H('wind', 5, 'Sylphe', 'sylphe, esprit de l\'air', {
  scale: 0.86, legs: 'robe', build: 'slim', colors: { skin: '#f8e0cc', hair: '#9fe0b0', cloth: '#e4f6ee', belt: '#8fd67a' },
  back: [['fairy', { color: '#c8f4ff' }]], gear: [['elfears'], ['hair', { style: 'bun' }]], face: { mouth: 'smile' }, eyes: { color: '#2fa37a', calm: true },
  near: ['chest'], far: ['hold', { kind: 'orb', color: '#b8ffd0', r: 11 }] });

H('wind', 6, 'Barde des tempêtes', 'Orphée, le musicien des légendes grecques', {
  legs: 'robe', colors: { skin: '#f2c9a4', hair: '#7a4a2a', cloth: '#f4f8ff', belt: '#2f8f8a', cape: '#2f8f8a', leaf: '#e6ac3c' },
  bareArms: true, back: [['cape', { len: 'short' }]], gear: [['hair', { style: 'short' }], ['leaves', { t: 'leaf' }]], face: { mouth: 'smile' },
  eyes: { color: '#2a8a9a', calm: true }, near: ['chest'], far: ['hold', { kind: 'lyre' }] });

H('wind', 7, 'Valkyrie', 'valkyrie, guerrière d\'Odin', {
  colors: { skin: '#f6d2b4', hair: '#f0d070', cloth: '#f4f8ff', pants: '#3d4a5e', steel: metal('#c2ccda'), bone: '#f4f8ff', shieldFace: '#3f6fd8' },
  armor: 'steel', back: [['braid']], gear: [['helm', { wings: true }]], eyes: { color: '#3f8fd8' },
  near: ['spear', {}], far: ['shield', { kind: 'round', emblem: 'star', ec: '#ffd76a' }] });

H('wind', 8, 'Tengu', 'tengu, démon-corbeau des montagnes (Japon)', {
  colors: { skin: '#c83a3a', hair: '#f4f0e6', cloth: '#f4f0e6', pants: '#2a2630', wing: '#2a2630', boot: '#2a2630', belt: '#2a2630', fan: '#e6ac3c' },
  back: [['wings', { kind: 'feather' }]], gear: [['hair', { style: 'wild' }], ['nose']], neck: [['beads', { t: '#f4f0e6' }]], face: { noMouth: true }, browColor: '#f4f0e6',
  eyes: { color: '#ffe14a', sclera: '#fff3a8' }, near: ['sword', { tip: [190, 44], w: 13, curve: 7, guard: 9 }], far: ['hold', { kind: 'fan' }] });

H('wind', 9, 'Garuda', 'Garuda, l\'homme-aigle (Inde)', {
  beast: true, colors: { skin: '#f4ead8', hair: '#e6ac3c', cloth: '#c8502a', pants: '#c8502a', boot: '#e6ac3c', wing: '#c8502a', sleeve: '#e6ac3c', bow: metal('#e6ac3c'), belt: '#e6ac3c', glove: '#e6ac3c' },
  back: [['wings', { kind: 'feather' }]], gear: [['mohawk', { t: 'hair' }]], face: { beak: 'gold' }, neck: [['collar', { gem: '#c8502a' }]],
  eyes: { color: '#c8502a', sclera: '#fff3a8' }, near: ['pull'], far: ['bow', {}] });

H('wind', 10, 'Kamaitachi', 'kamaitachi, la belette aux faucilles (Japon)', {
  scale: 0.9, beast: true, build: 'slim', colors: { skin: '#d8b078', muz: '#f6ead6', cloth: '#2f8f8a', pants: '#d8b078', boot: '#b8905a', tail: '#d8b078', tip: '#f6ead6', scarf: '#f4f8ff', glove: '#d8b078' },
  bareArms: true, back: [['tail', { kind: 'fox' }]], gear: [['roundears']], neck: [['scarf']],
  face: { snout: { len: 26, w: 20, y: 90, tone: 'muz' }, muzzle: 'muz' }, eyes: { color: '#2a2226' }, near: ['dagger', { kind: 'sickle' }], far: ['dagger', { kind: 'sickle' }] });

H('wind', 11, 'Apsara', 'apsara, danseuse céleste (Inde)', {
  legs: 'robe', build: 'slim', colors: { skin: '#d9a074', hair: '#2a2226', cloth: '#2fa39a', belt: '#e6ac3c', scarf: '#ffb0cf' },
  bareArms: true, robeInner: '<path d="M98 110 L120 110 L132 236 L84 236 Z" fill="#e6ac3c"/>',
  back: [['cloud'], ['scarf2']], gear: [['hair', { style: 'bun' }], ['tiara', { gem: '#ff5a8a' }]], neck: [['collar', { gem: '#ff5a8a' }]], face: { mouth: 'smile' },
  eyes: { color: '#5a3a20', calm: true }, near: ['chest'], far: ['hold', { kind: 'flower', color: '#ffb0cf' }] });

H('wind', 12, 'Fūjin', 'Fūjin, dieu du vent (Japon)', {
  scale: 1.05, build: 'heavy', colors: { skin: '#5fae6a', hair: '#f4f0e6', cloth: '#5fae6a', pants: '#5fae6a', boot: '#4a8a54', bag: '#f4f0e6', pelt: '#e8c070', belt: '#c83a3a', bone: '#f4ead8' },
  bare: true, bareArms: true, loin: 'pelt', torsoInner: '<g fill="#7a5a2a"><circle cx="80" cy="184" r="3.5"/><circle cx="104" cy="188" r="3.5"/><circle cx="128" cy="184" r="3.5"/></g>',
  back: [['bag']], gear: [['hair', { style: 'wild' }], ['horns', { kind: 'small' }]], face: { fangs: true }, browColor: '#f4f0e6',
  eyes: { color: '#ffe14a', sclera: '#fff3a8' }, near: ['fist', { r: 13 }], far: ['fist', { r: 12 }] });

H('wind', 13, 'Roi singe', 'le Roi singe du Voyage en Occident (Chine)', {
  beast: true, colors: { skin: '#c8843a', face: '#f4d8b0', cloth: '#c83a3a', pants: '#e6ac3c', boot: '#2a2630', steel: metal('#e6ac3c'), tail: '#c8843a', scarf: '#c83a3a', glove: '#c8843a', sleeve: '#c8843a', wood: '#c83a3a' },
  armor: 'steel', band: { tone: '#e6ac3c', y: 56, k: 8 }, back: [['cloud'], ['tail', { kind: 'monkey' }], ['scarf']], gear: [['sideears']], neck: [['scarf']],
  face: { paint: '<path d="M84 74 C96 62 110 68 118 76 C126 66 142 66 150 78 C154 98 146 114 124 118 C100 120 82 106 84 74 Z" fill="#f4d8b0"/>', snout: { len: 12, w: 22, y: 94, tone: 'face', nose: '#7a4a2a', x: 132 } },
  eyes: { color: '#c8641e', sclera: '#fff3a8' }, near: ['spear', { kind: 'staff', thick: 8, butt: [80, 186], end: [182, 92] }] });

H('wind', 14, 'Maître de la foudre', 'Zeus, roi des dieux (Grèce)', {
  scale: 1.1, build: 'heavy', legs: 'robe', colors: { skin: '#f2c9a4', hair: '#f4f8ff', cloth: '#f4f8ff', belt: '#e6ac3c', leaf: '#e6ac3c', cape: '#5a4a8a' },
  bareArms: true, back: [['cape', { len: 'long' }], ['hair']], gear: [['hair', { style: 'long' }], ['leaves', { t: 'leaf' }]], face: { beard: 'long' }, browColor: '#c8d4e4',
  eyes: { color: '#6fc8f0' }, near: ['chest'], far: ['bolt', {}] });

H('wind', 15, 'Morrigane', 'la Morrígan, déesse-corbeau (Irlande)', {
  build: 'slim', colors: { skin: '#f0e2d8', hair: '#1c1a24', cloth: '#2a2630', pants: '#1c1a24', boot: '#12101a', wing: '#1c1a24', fur: '#1c1a24', gold: metal('#8a8a9c'), belt: '#8a2a3a', steel: metal('#c2ccda'), glove: '#12101a' },
  back: [['wings', { kind: 'small' }], ['hair']], gear: [['hair', { style: 'long' }], ['tiara', { gem: '#c83a3a' }]], neck: [['fur']],
  face: { mouthColor: '#8a2a3a' }, eyes: { color: '#c83a3a' }, near: ['sword', { tip: [184, 50], w: 14, guard: 10 }], far: ['dagger', { len: 44 }] });

H('wind', 16, 'Séraphin', 'ange gardien', {
  legs: 'robe', colors: { skin: '#f8dcc4', hair: '#f0d070', cloth: '#f4f8ff', belt: '#e6ac3c', wing: '#f4f8ff', bone: metal('#e6ac3c') },
  robeInner: '<path d="M98 110 L120 110 L132 236 L84 236 Z" fill="#cfe6ff"/>',
  back: [['halo'], ['wings', { kind: 'feather', glow: '#fff3c0' }]], gear: [['hair', { style: 'short' }]], face: { mouth: 'smile' },
  eyes: { color: '#3f8fd8', calm: true }, near: ['chest'], far: ['hold', { kind: 'horn' }] });

H('wind', 17, 'Raijin', 'Raijin, dieu du tonnerre (Japon)', {
  scale: 1.08, build: 'heavy', colors: { skin: '#7a82c8', hair: '#ffe14a', cloth: '#7a82c8', pants: '#7a82c8', boot: '#5a62a8', drum: '#c83a3a', pelt: '#3a3058', belt: '#e6ac3c', bone: '#f4ead8', wood: '#f4ead8' },
  bare: true, bareArms: true, loin: 'pelt', back: [['drums']], gear: [['hair', { style: 'wild' }], ['horns', { kind: 'small' }]], neck: [['collar', { gem: '#ffe14a' }]],
  face: { fangs: true }, browColor: '#3a3058', eyes: { color: '#ffe14a', glow: true, sclera: '#ffe14a', lid: '#3a3058' },
  near: ['small', { kind: 'stick', dir: [26, -26] }], far: ['hold', { kind: 'stick' }] });
