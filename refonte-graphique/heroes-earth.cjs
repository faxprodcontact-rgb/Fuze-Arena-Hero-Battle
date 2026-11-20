// TERRE — verts, bruns, pierre, sable, os ; et le monde souterrain.
const { H, tone, metal } = require('./heroes72.cjs');
const SOUL = '#7dffb0';

H('earth', 0, 'Nain au bouclier', 'nain des montagnes (mythologie nordique)', {
  scale: 0.95, build: 'heavy', colors: { skin: '#eebf98', hair: '#c8642a', cloth: '#3f7a44', pants: '#2e4a3a', boot: '#4a3a2a', glove: '#6a4a2e', shieldFace: '#3f8a4a', bone: '#e9e2d2' },
  gear: [['helm', {}], ['horns', { kind: 'small' }]], face: { beard: 'full' }, browColor: '#7a3f16', eyes: { color: '#4a7a2a' },
  near: ['shoulder', { kind: 'hammer' }], far: ['shield', { kind: 'kite', emblem: 'leaf', ec: '#e6ac3c' }] });

H('earth', 1, 'Satyre', 'satyre, compagnon des bois (Grèce)', {
  hoof: true, colors: { skin: '#d9a074', hair: '#5a3a22', cloth: '#d9a074', pants: '#7a5234', boot: '#2a2226', belt: '#4f8a3a', bone: '#c8b088' },
  bare: true, bareArms: true, noBelt: true, gear: [['elfears'], ['hair', { style: 'short' }], ['horns', { kind: 'ram' }]], face: { beard: 'goat', mouth: 'smirk' },
  eyes: { color: '#4f8a3a' }, near: ['club', {}] });

H('earth', 2, 'Chasseur à la sarbacane', 'chasseur de la forêt profonde', {
  build: 'slim', colors: { skin: '#b87a4a', hair: '#2a2226', cloth: '#b87a4a', pants: '#b87a4a', boot: '#8a5a34', leafc: '#4f8a3a', belt: '#7a5234', leaf: '#4f8a3a', crest: '#e0483a' },
  bare: true, bareArms: true, loin: 'leafc', gear: [['hair', { style: 'short' }], ['leaves', {}]],
  face: { paint: '<path d="M60 98 L160 94" stroke="#f4ead8" stroke-width="4" opacity="0.9"/>' }, eyes: { color: '#5a3a20' }, near: ['gun', { kind: 'blow' }] });

H('earth', 3, 'Cyclope', 'cyclope, géant à l\'œil unique (Grèce)', {
  scale: 1.15, build: 'heavy', colors: { skin: '#c8a078', hair: '#5a3a22', cloth: '#c8a078', pants: '#c8a078', boot: '#a88058', pelt: '#7a5234', belt: '#4a3226', steel: tone('#8a8a80'), shieldFace: '#a8a898' },
  bare: true, bareArms: true, loin: 'pelt', gear: [['horns', { kind: 'small', t: '#e9e2d2' }]], face: { cyclops: true, fangs: true },
  eyes: { color: '#c8641e' }, near: ['club', { w: 34 }], far: ['shield', { kind: 'tower', inner: '<path d="M150 124 L160 150 L152 176 M172 130 L166 160" stroke="#5a5a52" stroke-width="3" fill="none"/>' }] });

H('earth', 4, 'Homme-scorpion', 'homme-scorpion, gardien du désert (Mésopotamie)', {
  build: 'slim', colors: { skin: '#c8905a', cloth: '#7a4a2a', pants: '#5a3a22', boot: '#3a2a1c', tail: '#8a5a2a', turban: '#e0c890', bone: '#3a2a1c', scarf: '#e0c890', belt: '#e6ac3c', steel: metal('#e6ac3c'), glove: '#3a2a1c' },
  back: [['tail', { kind: 'scorpion' }]], gear: [['turban', { gem: '#2fa37a' }]], face: { mask: 97, maskTone: 'scarf' }, brows: false,
  eyes: { color: '#2a2226' }, near: ['dagger', { kind: 'sickle' }], far: ['dagger', { kind: 'sickle' }] });

H('earth', 5, 'Dryade', 'dryade, nymphe des arbres (Grèce)', {
  legs: 'robe', build: 'slim', colors: { skin: '#a8d088', hair: '#3f7a3a', cloth: '#5f9a4a', belt: '#7a5234' },
  bareArms: true, robeInner: '<path d="M70 190 C84 180 96 190 100 206 M112 176 C126 172 138 184 138 204" stroke="#3f7a3a" stroke-width="4" fill="none"/>',
  gear: [['elfears'], ['hair', { style: 'leaf' }], ['flower', { color: '#ffb0cf', x: 84, y: 54 }]], face: { mouth: 'smile', mouthColor: '#3f6a2a' }, browColor: '#3f6a2a',
  eyes: { color: '#e6ac3c', calm: true }, near: ['chest'], far: ['staff', { kind: 'branch', top: 40 }] });

H('earth', 6, 'Druide', 'druide des forêts celtes', {
  legs: 'robe', colors: { skin: '#eebf98', hair: '#f4f0e6', cloth: '#7a6a4a', belt: '#4f8a3a', hood: '#4f6a3a', wood: '#7a5234', steel: metal('#e6ac3c') },
  gear: [['hood', {}]], face: { beard: 'long' }, browColor: '#c8c0b0', eyes: { color: '#4f8a3a' },
  near: ['small', { kind: 'sickle', dir: [26, -22] }], far: ['staff', { kind: 'crook', topT: 'wood', top: 38 }] });

H('earth', 7, 'Golem d\'argile', 'le golem des légendes de Prague', {
  scale: 1.15, build: 'heavy', beast: true, colors: { skin: '#b8a888', hair: '#5f8a4a', cloth: '#b8a888', pants: '#b8a888', boot: '#98886a', belt: '#98886a', steel: tone('#98886a'), shieldFace: '#a89878', moss: '#5f8a4a' },
  bare: true, bareArms: true, noBelt: true, torsoInner: '<path d="M84 128 L96 146 L90 164 M130 126 L124 148" stroke="#7a6a50" stroke-width="3" fill="none"/>',
  gear: [['hair', { style: 'short', t: 'moss' }]], neck: [['pad', { t: 'moss' }]],
  face: { noMouth: true, paint: '<path d="M112 56 L112 70 M106 60 L118 60 M106 68 L118 68" stroke="' + SOUL + '" stroke-width="3.4" stroke-linecap="round"/>' }, brows: false,
  eyes: { color: SOUL, glow: true, sclera: SOUL, lid: '#5a4a38' }, near: ['fist', { r: 16 }], far: ['shield', { kind: 'tower', emblem: 'star', ec: SOUL }] });

H('earth', 8, 'Minotaure', 'le Minotaure du labyrinthe (Crète)', {
  scale: 1.18, build: 'heavy', beast: true, hoof: true, colors: { skin: '#7a4a34', muz: '#c8a088', cloth: '#7a4a34', pants: '#7a4a34', boot: '#2a2226', red: '#a82a2a', belt: '#e6ac3c', bone: '#ece4d0', steel: metal('#b9c2d0') },
  bare: true, bareArms: true, loin: 'red', gear: [['horns', { kind: 'bull' }]], face: { snout: { len: 24, w: 28, y: 88, tone: 'muz', nose: '#3a2018', ring: true }, muzzle: 'muz' },
  eyes: { color: '#c83a3a', sclera: '#ffe9c0' }, near: ['shoulder', { kind: 'axe', double: true, z: 1.1 }] });

H('earth', 9, 'Gorgone', 'Méduse, la gorgone au regard de pierre (Grèce)', {
  legs: 'naga', build: 'slim', colors: { skin: '#a8c8a0', hair: '#3f7a4a', cloth: '#2a4a3a', tail: '#4f8a5a', belly: '#c8e0a8', belt: '#e6ac3c', bow: metal('#c9903c'), sleeve: '#a8c8a0', glove: '#a8c8a0' },
  bareArms: true, gear: [['hair', { style: 'snakes' }]], neck: [['collar', { gem: '#c83a3a' }]], face: { mouthColor: '#2a4a3a', fangs: true }, browColor: '#2a4a3a',
  eyes: { color: '#ffe14a', glow: true, sclera: '#ffe14a', lid: '#2a4a3a' }, near: ['pull'], far: ['bow', {}] });

H('earth', 10, 'Anubis', 'Anubis, gardien des morts (Égypte)', {
  build: 'slim', beast: true, colors: { skin: '#2a2630', cloth: '#2a2630', pants: '#2a2630', boot: '#e6ac3c', white: '#f4ead8', belt: '#e6ac3c', gold: metal('#e6ac3c'), steel: metal('#e6ac3c'), earin: '#e6ac3c' },
  bare: true, bareArms: true, loin: 'white', gear: [['ears', { h: 46, inner: 'earin' }]], neck: [['collar', { gem: '#3fa8d8' }]],
  face: { snout: { len: 36, w: 17, y: 90, nose: '#12101a' } }, brows: false, eyes: { color: '#ffe14a', glow: true, sclera: '#ffe14a', lid: '#12101a' },
  near: ['sword', { tip: [186, 48], w: 15, curve: 15, guard: 9 }], far: ['dagger', { kind: 'sickle' }] });

H('earth', 11, 'Isis', 'Isis, la magicienne aux ailes (Égypte)', {
  legs: 'robe', build: 'slim', colors: { skin: '#d9a074', hair: '#1c1a24', cloth: '#f4ead8', belt: '#e6ac3c', wing: '#2fa39a' },
  bareArms: true, robeInner: '<path d="M98 110 L120 110 L132 236 L84 236 Z" fill="#2fa39a"/>',
  back: [['wings', { kind: 'feather' }], ['hair']], gear: [['disc', { color: '#ffcf5a' }], ['hair', { style: 'long' }]], band: { tone: '#e6ac3c', y: 60, k: 7, gem: '#3fa8d8' },
  neck: [['collar', { gem: '#3fa8d8' }]], eyes: { color: '#2a8a9a', calm: true }, near: ['chest'], far: ['staff', { kind: 'ankh', top: 40 }] });

H('earth', 12, 'Baron des ombres', 'Baron Samedi, maître des cimetières (Haïti)', {
  build: 'slim', colors: { skin: '#ece4d0', hair: '#1c1a24', cloth: '#4a2a5a', pants: '#1c1a24', boot: '#12101a', hat: '#1c1a24', scarf: '#8a4ce0', sleeve: '#4a2a5a', belt: '#8a4ce0', glove: '#ece4d0' },
  gear: [['tophat', { emblem: 'skull', band: 'scarf' }]], neck: [['scarf']],
  face: { noMouth: true, paint: '<ellipse cx="103" cy="90" rx="15" ry="13" fill="#1c1a24"/><ellipse cx="134" cy="90" rx="11" ry="12" fill="#1c1a24"/><path d="M108 108 L134 106 M112 104 L112 112 M119 104 L119 112 M126 103 L126 111" stroke="#1c1a24" stroke-width="2.2"/>' },
  brows: false, eyes: { color: SOUL, glow: true, sclera: SOUL, lid: '#1c1a24' }, near: ['chest'], far: ['staff', { kind: 'skull', top: 60, color: SOUL }] });

H('earth', 13, 'Héraclès', 'Héraclès et la peau du lion de Némée (Grèce)', {
  scale: 1.15, build: 'heavy', colors: { skin: '#d9a074', hair: '#5a3a22', cloth: '#d9a074', pants: '#d9a074', boot: '#6a4428', hood: '#e0a850', pelt: '#e0a850', belt: '#4a3226', cape: '#e0a850' },
  bare: true, bareArms: true, loin: 'pelt', back: [['cape', { len: 'short' }]], gear: [['hood', { ears: true, teeth: true }]], face: { beard: 'full' },
  eyes: { color: '#5a3a20' }, near: ['club', { w: 38 }], far: ['fist', { r: 13 }] });

H('earth', 14, 'Herne le Veneur', 'Herne, le chasseur aux bois de cerf (Angleterre)', {
  beast: true, colors: { skin: '#ece4d0', cloth: '#2a4a3a', pants: '#2a3a30', boot: '#1c2a22', cape: '#1f3a2c', bone: '#ece4d0', sleeve: '#2a4a3a', bow: '#3a2a22', belt: '#7a5234', glove: '#1c2a22' },
  back: [['cape', { len: 'torn' }]], gear: [['antlers', {}]], neck: [['fur', { t: '#1f3a2c' }]],
  face: { noMouth: true, paint: '<path d="M118 100 L124 110 L112 110 Z" fill="#1c2a22"/><path d="M104 114 L140 110" stroke="#1c2a22" stroke-width="2"/>' }, brows: false,
  eyes: { color: SOUL, glow: true, sclera: SOUL, lid: '#1c2a22' }, near: ['pull'], far: ['bow', { glow: SOUL, top: 52, bot: 206 }] });

H('earth', 15, 'Arachné', 'Arachné, la tisseuse changée en araignée (Grèce)', {
  build: 'slim', colors: { skin: '#e8d8e0', hair: '#1c1a24', cloth: '#3a2a4a', pants: '#2a2038', boot: '#1c1a24', leg: '#2a2038', belt: '#c83a3a', gold: metal('#8a8a9c'), steel: tone('#7dffb0'), glove: '#1c1a24' },
  back: [['spider']], gear: [['hair', { style: 'bun' }], ['eyes', { color: '#ff4a4a' }]], face: { mouthColor: '#8a2a3a', mouth: 'smirk' },
  eyes: { color: '#c83a3a' }, near: ['dagger', {}], far: ['dagger', {}] });

H('earth', 16, 'Gaïa', 'Gaïa, la Terre-mère (Grèce)', {
  legs: 'robe', colors: { skin: '#a8744a', hair: '#4f8a3a', cloth: '#7a5a34', belt: '#4f8a3a', leaf: '#8fd67a' },
  bareArms: true, robeInner: '<path d="M98 110 L120 110 L132 236 L84 236 Z" fill="#4f8a3a"/>',
  back: [['hair']], gear: [['hair', { style: 'long' }], ['leaves', {}], ['flower', { color: '#ffd76a', x: 110, y: 40 }]], face: { mouth: 'smile', mouthColor: '#3a1c1c' }, browColor: '#3a5a2a',
  eyes: { color: '#8fd67a', calm: true }, near: ['chest'], far: ['hold', { kind: 'orb', color: '#8fff9a' }] });

H('earth', 17, 'Roi des enfers', 'Hadès, souverain du monde souterrain (Grèce)', {
  scale: 1.1, legs: 'robe', colors: { skin: '#b8c0d0', hair: '#5fe0b0', cloth: '#1c1a24', belt: '#3fb88a', cape: '#12101a', gold: metal('#4a444e'), steel: metal('#4a444e'), wood: '#2a2630', sleeve: '#1c1a24' },
  robeInner: '<path d="M98 110 L120 110 L132 236 L84 236 Z" fill="#3fb88a"/>',
  back: [['cape', { len: 'wide' }]], gear: [['hair', { style: 'flame' }], ['crown', {}]], face: { beard: 'goat', beardTone: 'hair' }, browColor: '#2a2630',
  eyes: { color: SOUL, glow: true, sclera: SOUL, lid: '#12101a' }, near: ['grip'], far: ['pole', { kind: 'bident', glow: SOUL }] });
