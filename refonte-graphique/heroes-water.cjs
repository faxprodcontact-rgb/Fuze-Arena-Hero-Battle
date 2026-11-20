// EAU — bleus, turquoise, glace, corail, nacre.
const { H, tone, metal } = require('./heroes72.cjs');
const ICE = '#bfe9ff';

H('water', 0, 'Garde-corail', 'soldat des récifs', {
  colors: { skin: '#eebf98', cloth: '#2f6fc8', pants: '#1f3a6a', steel: metal('#7fb8c8'), crest: '#f07a6a', shieldFace: '#f07a6a' },
  armor: 'steel', gear: [['helm', { crest: 'low', plain: true }]], eyes: { color: '#2a8a9a' },
  near: ['spear', {}], far: ['shield', { kind: 'shell', t: '#2fa3b8' }] });

H('water', 1, 'Harponneur', 'pêcheur au harpon', {
  colors: { skin: '#d9a074', hair: '#2a2226', cloth: '#2a4a7a', pants: '#e9e2d2', boot: '#6a4428', straw: '#e0c070', belt: '#c83a3a' },
  bareArms: true, gear: [['kasa']], eyes: { color: '#5a3a20' }, near: ['grip'], far: ['pole', { kind: 'harpoon' }] });

H('water', 2, 'Corsaire', 'pirate des mers du sud', {
  colors: { skin: '#e2a878', hair: '#2a2226', cloth: '#1f3a6a', pants: '#3a3038', hat: '#2a2630', sleeve: '#f4f0e6', belt: '#c83a3a', iron: metal('#5a5a6c') },
  gear: [['hair', { style: 'short' }], ['tricorn', { emblem: 'skull' }]], face: { beard: 'goat', paint: '<path d="M60 70 L160 96" stroke="#1c1a24" stroke-width="3"/><ellipse cx="134" cy="88" rx="10" ry="9" fill="#1c1a24"/>' },
  eyes: { color: '#5a3a20' }, near: ['gun', { kind: 'pistol' }], far: ['dagger', { kind: 'hook' }] });

H('water', 3, 'Kappa', 'kappa, génie des rivières (Japon)', {
  scale: 0.94, beast: true, build: 'heavy', colors: { skin: '#6fae5a', hair: '#2a4a2a', cloth: '#6fae5a', pants: '#6fae5a', boot: '#4a8a44', shell: '#7a5a34', shieldFace: '#5fb84a', belt: '#7a5a34', steel: tone('#4a8a44') },
  bare: true, bareArms: true, torsoInner: '<path d="M96 120 C116 116 134 126 136 154 C122 162 104 162 94 152 Z" fill="#e6dca0"/>',
  back: [['shell']], gear: [['dish']], face: { beak: 'gold' }, eyes: { color: '#2a2226', sclera: '#fff3a8' },
  near: ['fist', { r: 12 }], far: ['shield', { kind: 'round', r: 30, emblem: 'leaf', ec: '#2a4a2a' }] });

H('water', 4, 'Requin', 'homme-requin des légendes du Pacifique', {
  beast: true, colors: { skin: '#6a8aa8', muz: '#e9eef2', cloth: '#6a8aa8', pants: '#1f3a6a', boot: '#162a4c', tail: '#6a8aa8', bone: '#ece4d0', belt: '#c83a3a', steel: tone('#ece4d0') },
  bare: true, bareArms: true, torsoInner: '<path d="M98 120 C118 116 136 126 138 154 C124 162 106 162 96 152 Z" fill="#e9eef2"/>',
  back: [['tail', { kind: 'lizard' }]], gear: [['fin']], face: { snout: { len: 34, w: 26, y: 84, tone: 'skin', nose: false, teeth: 4 }, muzzle: 'muz' }, brows: false,
  eyes: { color: '#12101a', sclera: '#e9eef2' }, near: ['dagger', {}], far: ['dagger', {}] });

H('water', 5, 'Naïade', 'naïade, nymphe des sources (Grèce)', {
  legs: 'robe', build: 'slim', colors: { skin: '#f6dcc8', hair: '#3fb8c8', cloth: '#dff4ff', belt: '#3fb8c8', jar: '#c8824a' },
  bareArms: true, back: [['hair']], gear: [['hair', { style: 'long' }], ['flower', { color: '#fff', x: 84, y: 56 }]], face: { mouth: 'smile' },
  eyes: { color: '#2a8a9a', calm: true }, near: ['chest'], far: ['hold', { kind: 'jar', water: '#6fd0ff' }] });

H('water', 6, 'Sirène', 'sirène au chant envoûtant', {
  legs: 'tail', build: 'slim', colors: { skin: '#f6dcc8', hair: '#f0604a', cloth: '#f07a6a', tail: '#2fa3b8', fin: '#6fd8c8', belt: '#e6ac3c', bone: '#ffc8b8' },
  bare: true, bareArms: true, torsoInner: '<path d="M40 116 L176 116 L176 140 C130 150 90 150 40 140 Z" fill="#f07a6a"/>',
  back: [['hair']], gear: [['hair', { style: 'long' }], ['tiara', { gem: '#dff4ff' }]], face: { mouth: 'smile' },
  eyes: { color: '#2a8a9a' }, near: ['chest'], far: ['hold', { kind: 'lyre' }] });

H('water', 7, 'Samouraï-crabe', 'crabes Heike, guerriers réincarnés (Japon)', {
  build: 'heavy', colors: { skin: '#e6b88a', cloth: '#c8483a', pants: '#3a2a30', carap: '#c8483a', gold: metal('#e6ac3c'), belt: '#2a2630', boot: '#2a2630' },
  armor: 'carap', gear: [['helm', { neck: true, moon: true, t: 'carap' }]], neck: [['pad', { t: '#c8483a' }]], face: { mask: 96, maskTone: 'belt' }, brows: false,
  eyes: { color: '#ffe14a', sclera: '#fff3a8' }, near: ['sword', { tip: [188, 44], w: 13, curve: 7, guard: 9 }], far: ['pincer', {}] });

H('water', 8, 'Jötunn des glaces', 'géant du givre (mythologie nordique)', {
  scale: 1.2, build: 'heavy', colors: { skin: '#8ab8e0', hair: '#f4f8ff', cloth: '#8ab8e0', pants: '#8ab8e0', boot: '#6a98c0', fur: '#f4f8ff', belt: '#5a4634', gold: tone(ICE), steel: tone(ICE) },
  bare: true, bareArms: true, loin: 'fur', gear: [['hair', { style: 'wild' }], ['crown', {}]], face: { beard: 'fork' }, browColor: '#f4f8ff',
  eyes: { color: '#dff4ff', glow: true, sclera: '#dff4ff', lid: '#3a5a8a' }, near: ['axeLow', {}] });

H('water', 9, 'Chasseuse des glaces', 'Sedna, déesse inuite de la mer', {
  colors: { skin: '#d9a074', cloth: '#b88a5a', pants: '#8a6a44', boot: '#f4f0e6', hood: '#b88a5a', glove: '#f4f0e6', bone: '#ece4d0' },
  gear: [['hood', { trim: '#f4f0e6' }]], face: { paint: '<path d="M112 112 L112 120 M120 113 L120 121 M128 112 L128 119" stroke="#2f6fc8" stroke-width="2.4" stroke-linecap="round"/>' },
  eyes: { color: '#2a2226' }, near: ['spear', { kind: 'harpoon', t: 'bone' }] });

H('water', 10, 'Roussalka', 'roussalka, esprit des noyées (monde slave)', {
  legs: 'robe', build: 'slim', colors: { skin: '#b8e0d0', hair: '#1f4a3a', cloth: '#e9f4f0', belt: '#3f8a6a', steel: tone('#dff4ff') },
  back: [['hair']], gear: [['hair', { style: 'long' }], ['flower', { color: '#fff', x: 86, y: 54 }]], face: { noMouth: true }, brows: false,
  eyes: { color: '#dffff0', glow: true, sclera: '#dffff0', lid: '#1f4a3a' }, near: ['dagger', { kind: 'claw' }], far: ['dagger', { kind: 'claw' }] });

H('water', 11, 'Mazu', 'Mazu, protectrice des marins (Chine)', {
  legs: 'robe', colors: { skin: '#f8dcc4', hair: '#2a2226', cloth: '#c83a3a', belt: '#e6ac3c', iron: metal('#e6ac3c') },
  robeInner: '<path d="M98 110 L120 110 L132 236 L84 236 Z" fill="#e6ac3c"/>',
  gear: [['hair', { style: 'short' }], ['mian', {}]], face: { mouth: 'smile' }, eyes: { color: '#5a3a20', calm: true },
  near: ['chest'], far: ['staff', { kind: 'lantern', top: 30, color: '#ffe9a0' }] });

H('water', 12, 'Yuki-onna', 'la femme des neiges (Japon)', {
  legs: 'robe', build: 'slim', colors: { skin: '#e9f2ff', hair: '#1c1a24', cloth: '#f4f8ff', belt: '#6fc8f0', fan: ICE },
  back: [['hair']], gear: [['hair', { style: 'long' }]], face: { mouthColor: '#6f8fc8' }, browColor: '#3a3a5a',
  eyes: { color: '#6fc8f0' }, near: ['small', { kind: 'fan', dir: [24, -26] }], far: ['staff', { kind: 'crystal', top: 36 }] });

H('water', 13, 'Poséidon', 'Poséidon, dieu des mers (Grèce)', {
  scale: 1.15, build: 'heavy', colors: { skin: '#e2a878', hair: '#dff4ff', cloth: '#e2a878', pants: '#e2a878', boot: '#e6ac3c', scale: '#2fa3b8', belt: '#e6ac3c', cape: '#1f5a8a', steel: metal('#e6ac3c'), wood: '#e6ac3c' },
  bare: true, bareArms: true, loin: 'scale', back: [['cape', { len: 'wide' }]], gear: [['hair', { style: 'wild' }], ['crown', { gem: '#3fb8c8' }]], face: { beard: 'long' }, browColor: '#b8d8e8',
  eyes: { color: '#2a8a9a' }, near: ['spear', { kind: 'trident', thick: 7.5, butt: [82, 186], end: [178, 92] }] });

H('water', 14, 'Skadi', 'Skadi, chasseresse de l\'hiver (Scandinavie)', {
  colors: { skin: '#f6dcc8', hair: '#f0d070', cloth: '#5a7a9a', pants: '#3d4a5e', boot: '#f4f0e6', hood: '#c8ccd6', fur: '#f4f0e6', sleeve: '#5a7a9a', bow: '#dff4ff', glove: '#3d4a5e' },
  back: [['braid']], gear: [['hood', { ears: true, teeth: true }]], neck: [['fur']], face: { paint: '<path d="M88 100 L104 104 M88 108 L100 110" stroke="#2f6fc8" stroke-width="3" stroke-linecap="round"/>' },
  eyes: { color: '#6fc8f0' }, near: ['pull'], far: ['bow', { glow: ICE, top: 52, bot: 206 }] });

H('water', 15, 'Scylla', 'Scylla, monstre du détroit (Grèce)', {
  legs: 'tentacles', build: 'slim', colors: { skin: '#c8b8e0', hair: '#3a2a5a', cloth: '#3a2a5a', tail: '#6a4a9a', belt: '#f07a6a', gold: tone('#f07a6a'), steel: metal('#c2ccda') },
  bareArms: true, back: [['hair']], gear: [['hair', { style: 'long' }], ['crown', {}]], face: { mouthColor: '#5a2a6a', mouth: 'smirk' }, browColor: '#3a2a5a',
  eyes: { color: '#ffe14a', sclera: '#fff3a8', slit: true }, near: ['dagger', { kind: 'hook' }], far: ['dagger', { kind: 'hook' }] });

H('water', 16, 'Mère des eaux', 'Yemoja, mère des eaux (Yoruba)', {
  legs: 'robe', colors: { skin: '#7a4a34', cloth: '#f4f8ff', belt: '#3f8fd8', turban: '#f4f8ff', cape: '#3f8fd8' },
  robeInner: '<path d="M98 110 L120 110 L132 236 L84 236 Z" fill="#6fc8f0"/>', bareArms: true,
  back: [['cape', { len: 'wide' }]], gear: [['turban', { gem: '#3f8fd8' }]], neck: [['beads', { t: '#f4f8ff' }]], face: { mouth: 'smile', mouthColor: '#3a1c1c' },
  eyes: { color: '#3a2a22', calm: true }, browColor: '#2a1c18', near: ['chest'], far: ['hold', { kind: 'orb', color: '#dff4ff' }] });

H('water', 17, 'Roi dragon', 'Ryūjin, roi dragon des mers (Japon)', {
  scale: 1.1, beast: true, legs: 'robe', colors: { skin: '#2fa39a', muz: '#bfe8d8', hair: '#f4f8ff', cloth: '#1f3a6a', belt: '#e6ac3c', tail: '#2fa39a', bone: metal('#e6ac3c'), sleeve: '#1f3a6a' },
  robeInner: '<path d="M98 110 L120 110 L132 236 L84 236 Z" fill="#e6ac3c"/>',
  back: [['tail', { kind: 'lizard' }]], gear: [['antlers', {}], ['frill', { t: 'hair', len: 22 }], ['whiskers', {}]],
  face: { snout: { len: 36, w: 24, y: 86, nose: '#12303a', teeth: 3 }, muzzle: 'muz' }, eyes: { color: '#ffe14a', sclera: '#fff3a8', slit: true },
  near: ['chest'], far: ['hold', { kind: 'orb', color: '#dff4ff', r: 15 }] });
