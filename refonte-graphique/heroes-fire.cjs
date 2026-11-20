// FEU — rouges, orangés, or, fer noir, lave.
const { H, tone, metal } = require('./heroes72.cjs');
const bronze = metal('#c9903c'), iron = metal('#4a444e'), LAVA = '#ff7a1a';
const crack = (d) => `<path d="${d}" stroke="${LAVA}" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;

H('fire', 0, 'Garde-braise', 'hoplite, gardien du feu sacré', {
  colors: { skin: '#e2a878', cloth: '#b92b36', pants: '#e2a878', boot: '#6a4428', steel: bronze, crest: '#d8452a', shieldFace: '#b92b36' },
  armor: 'steel', gear: [['helm', { crest: 'low', cheek: true, plain: true }]], eyes: { color: '#5a3a20' },
  near: ['sword', { tip: [176, 62], w: 15, guard: 13 }], far: ['shield', { kind: 'round', emblem: 'flame' }] });

H('fire', 1, 'Forgeron', 'forgeron des dieux', {
  colors: { skin: '#d9a074', hair: '#2a2226', cloth: '#7a4a2a', pants: '#3a3038', belt: '#3a2a22', iron },
  band: { tone: '#c83a3a', y: 54 }, bareArms: true, face: { beard: 'full' }, eyes: { color: '#7a4a1e' },
  near: ['shoulder', { kind: 'hammer', t: 'iron', band: LAVA }] });

H('fire', 2, 'Archer de cendre', 'archer aux flèches enflammées', {
  colors: { skin: '#eebf98', cloth: '#8a3a2e', pants: '#3a3038', hood: '#5a5058', sleeve: '#3a3038', bow: '#3a3038', scarf: '#d8452a', glove: '#3a3038' },
  gear: [['hood', { trim: '#f08a2a' }]], neck: [['scarf']], eyes: { color: '#c8641e' },
  near: ['pull'], far: ['bow', { glow: LAVA }] });

H('fire', 3, 'Légionnaire de lave', 'légionnaire romain, bouclier d\'obsidienne', {
  colors: { skin: '#e2a878', cloth: '#8a2a2a', pants: '#e2a878', boot: '#4a3226', steel: iron, crest: '#ff8a2a', shieldFace: '#2a2228', cape: '#8a2a2a' },
  armor: 'steel', back: [['cape', { len: 'short' }]], gear: [['helm', { crest: 'tall', cheek: true, plain: true }]], eyes: { color: '#5a3a20' },
  near: ['sword', { tip: [176, 62], w: 15, guard: 13 }], far: ['shield', { kind: 'tower', inner: crack('M150 116 L162 138 L152 158 L168 178 L158 202 M162 138 L176 146 M152 158 L142 168') }] });

H('fire', 4, 'Salamandre', 'salamandre, esprit du feu', {
  beast: true, build: 'slim', colors: { skin: '#f08a2a', cloth: '#3a3038', pants: '#f08a2a', boot: '#c8641e', tail: '#f08a2a', fin: '#3a3038', glove: '#f08a2a', belt: '#3a3038' },
  bare: true, bareArms: true, loin: 'cloth', back: [['tail', { kind: 'lizard' }]], gear: [['frill', { len: 26 }]],
  face: { snout: { len: 38, w: 22, y: 88, nose: false }, paint: '<g fill="#3a2a22"><circle cx="84" cy="62" r="5"/><circle cx="100" cy="52" r="4"/><circle cx="118" cy="60" r="4.5"/><circle cx="76" cy="100" r="4"/></g>' },
  torsoInner: '<path d="M100 118 C120 114 136 126 138 152 C124 160 106 160 98 150 Z" fill="#ffd9a0"/><g fill="#3a2a22"><circle cx="84" cy="134" r="5"/><circle cx="80" cy="152" r="4"/></g>',
  eyes: { color: '#ffe14a', sclera: '#fff3a8', slit: true }, near: ['dagger', {}], far: ['dagger', {}] });

H('fire', 5, 'Vestale', 'prêtresse du foyer sacré (Vesta)', {
  legs: 'robe', build: 'slim', colors: { skin: '#f2c9a4', cloth: '#f4ead8', belt: '#c83a3a', veil: '#f4ead8', hair: '#f4ead8' },
  robeInner: '<path d="M98 110 L120 110 L132 236 L84 236 Z" fill="#e9c9a8"/>', band: { tone: '#e6ac3c', y: 60, k: 7 },
  back: [['hair', { t: 'veil' }]], gear: [['veil']], face: { mouth: 'smile' }, eyes: { color: '#8a5a2a', calm: true }, browColor: '#6a4a2a',
  near: ['chest'], far: ['hold', { kind: 'bowl' }] });

H('fire', 6, 'Chamane du volcan', 'Pélé, déesse hawaïenne des volcans', {
  legs: 'robe', build: 'slim', colors: { skin: '#a86a44', hair: '#2a2226', cloth: '#d8452a', belt: '#f0b23a', gold: metal('#f0b23a') },
  robeInner: crack('M70 190 L84 206 L78 222 M120 180 L132 200 L126 220 M100 196 L104 214'), bareArms: true,
  back: [['hair']], gear: [['hair', { style: 'long' }], ['flower', { color: '#ff5a4a', x: 82, y: 58 }]], neck: [['beads', { t: '#ff8a2a' }]],
  eyes: { color: '#ff8a2a' }, near: ['chest'], far: ['staff', { kind: 'flame', top: 36 }] });

H('fire', 7, 'Golem de magma', 'géant de pierre et de lave', {
  scale: 1.15, build: 'heavy', beast: true, colors: { skin: '#4a3c42', cloth: '#4a3c42', pants: '#4a3c42', boot: '#33282e', belt: '#33282e', bone: '#33282e' },
  bare: true, bareArms: true, noBelt: true, torsoInner: crack('M80 126 L96 142 L88 160 L102 176 M132 124 L122 144 L134 160 M96 142 L112 148'),
  gear: [['horns', { kind: 'small' }]], face: { noMouth: true, paint: crack('M82 58 L94 72 L88 84 M132 52 L126 66 M108 104 L116 110 L128 106') },
  brows: false, eyes: { color: LAVA, glow: true, sclera: LAVA, lid: '#2a2026' }, neck: [['pad', { t: 'boot', spike: true, spikeT: 'boot' }]],
  near: ['fist', { r: 16 }], far: ['fist', { r: 14 }] });

H('fire', 8, 'Oni rouge', 'oni, ogre des légendes japonaises', {
  scale: 1.1, build: 'heavy', colors: { skin: '#d8483a', hair: '#2a2226', cloth: '#d8483a', pants: '#d8483a', boot: '#b03a30', belt: '#3a2a22', tiger: '#f0a030', iron },
  bare: true, bareArms: true, loin: 'tiger', torsoInner: '<path d="M70 176 L78 190 M96 180 L100 196 M122 180 L120 196 M142 174 L136 190" stroke="#3a2a22" stroke-width="4" stroke-linecap="round"/>',
  gear: [['hair', { style: 'wild' }], ['horns', { kind: 'oni' }]], face: { fangs: true }, neck: [['beads', { t: 'bone' }]],
  eyes: { color: '#ffe14a', sclera: '#fff3a8' }, near: ['shoulder', { kind: 'kanabo' }] });

H('fire', 9, 'Lancier-dragon', 'artilleur à la lance de feu (Chine ancienne)', {
  colors: { skin: '#e6b88a', hair: '#2a2226', cloth: '#8a2a2a', pants: '#3a3038', steel: bronze, iron, crest: '#d8452a' },
  armor: 'steel', gear: [['helm', { spike: true, cheek: true, tassel: 'crest' }]], face: { beard: 'goat' }, eyes: { color: '#5a3a20' },
  near: ['gun', { kind: 'lance', glow: LAVA }] });

H('fire', 10, 'Kitsune', 'renarde à plusieurs queues (Japon)', {
  scale: 0.96, build: 'slim', colors: { skin: '#f6d2b4', hair: '#f4ead8', cloth: '#f4ead8', pants: '#c83a3a', boot: '#3a2a22', tail: '#f08a2a', sleeve: '#f4ead8', belt: '#c83a3a', fox: '#f08a2a' },
  back: [['tail', { kind: 'fox', n: 3 }]], gear: [['ears', { t: 'fox', inner: 'hair', h: 36 }], ['hair', { style: 'short' }]],
  face: { paint: '<path d="M70 96 L84 98 M70 104 L82 104" stroke="#c83a3a" stroke-width="3" stroke-linecap="round"/>', mouth: 'smirk' },
  eyes: { color: '#f0a020' }, browColor: '#b8a890', near: ['dagger', { kind: 'kunai' }], far: ['dagger', { kind: 'kunai' }] });

H('fire', 11, 'Prêtre du soleil', 'prêtre aztèque du dieu soleil', {
  colors: { skin: '#b87a4a', hair: '#2a2226', cloth: '#b87a4a', pants: '#b87a4a', boot: '#6a4428', red: '#c83a3a', belt: '#e6ac3c' },
  bare: true, bareArms: true, loin: 'red', gear: [['feathers', { colors: ['#e0483a', '#f0b23a', '#2fa37a'], n: 7 }], ['hair', { style: 'short' }]],
  neck: [['collar', { gem: '#2fa37a' }]], face: { paint: '<path d="M60 96 L160 92" stroke="#c83a3a" stroke-width="5" opacity="0.85"/>' },
  eyes: { color: '#5a3a20' }, near: ['chest'], far: ['staff', { kind: 'sun', top: 36 }] });

H('fire', 12, 'Djinn', 'djinn des contes arabes', {
  legs: 'smoke', colors: { skin: '#e8793a', hair: '#2a2226', cloth: '#e8793a', smoke: '#7a4a5a', turban: '#f4ead8', belt: '#e6ac3c' },
  bare: true, bareArms: true, gear: [['turban', { feather: true, gem: '#e04a4a' }]], neck: [['collar', {}]], face: { beard: 'goat' },
  eyes: { color: '#ffe14a', sclera: '#fff3a8' }, near: ['chest'], far: ['hold', { kind: 'orb', color: '#ff8a2a' }] });

H('fire', 13, 'Surt', 'Surt, roi des géants de feu (Scandinavie)', {
  scale: 1.22, build: 'heavy', beast: true, colors: { skin: '#3a2c30', hair: '#ff8a2a', cloth: '#2a2228', pants: '#2a2228', boot: '#1c161a', steel: iron, bone: '#1c161a', cape: '#2a2228', belt: '#8a2a2a' },
  armor: 'steel', bareArms: true, back: [['cape', { len: 'torn' }]], gear: [['horns', { kind: 'bull' }], ['hair', { style: 'flame' }]],
  face: { beard: 'fork', paint: crack('M84 60 L92 72 M132 56 L128 66') }, browColor: '#ff8a2a',
  eyes: { color: '#ffe14a', glow: true, sclera: '#ffcf5a', lid: '#1c161a' }, near: ['sword', { tip: [198, 22], w: 27, guard: 21, glow: LAVA, t: 'steel' }] });

H('fire', 14, 'Sekhmet', 'Sekhmet, déesse lionne (Égypte)', {
  legs: 'robe', beast: true, colors: { skin: '#e0a850', muz: '#f4dca8', cloth: '#f4ead8', belt: '#c83a3a', bow: metal('#e6ac3c'), sleeve: '#e0a850', hair: '#2a3a6a' },
  bareArms: true, back: [['hair']], gear: [['disc', {}], ['roundears', {}], ['hair', { style: 'long' }]], neck: [['collar', { gem: '#3fa8d8' }]],
  face: { snout: { len: 22, w: 24, y: 90, tone: 'muz', nose: '#5a2a22' }, muzzle: 'muz' }, eyes: { color: '#ffb020', sclera: '#fff3a8', slit: true },
  near: ['pull'], far: ['bow', { glow: '#ffb84a' }] });

H('fire', 15, 'Ifrit', 'ifrit, démon de feu', {
  build: 'slim', beast: true, colors: { skin: '#2c2228', hair: '#ff8a2a', cloth: '#8a2a2a', pants: '#2c2228', boot: '#1c161a', wing: '#8a2a2a', bone: '#c83a3a', steel: iron, tail: '#2c2228', belt: '#e6ac3c' },
  bare: true, bareArms: true, loin: 'cloth', back: [['wings', { kind: 'bat', glow: LAVA }], ['tail', { kind: 'devil' }]], gear: [['horns', { kind: 'demon' }]],
  face: { fangs: true, paint: crack('M82 62 L90 74 M134 58 L128 68') }, brows: false, eyes: { color: LAVA, glow: true, sclera: LAVA, lid: '#1c161a' },
  near: ['sword', { tip: [186, 44], w: 17, curve: 13, guard: 12, glow: LAVA }], far: ['dagger', { len: 44 }] });

H('fire', 16, 'Phénix', 'le phénix qui renaît de ses cendres', {
  legs: 'robe', build: 'slim', colors: { skin: '#f6d2b4', hair: '#ff6a2a', cloth: '#f4ead8', belt: '#e6ac3c', wing: '#ff8a2a' },
  robeInner: '<path d="M98 110 L120 110 L132 236 L84 236 Z" fill="#ffb84a"/>',
  back: [['wings', { kind: 'feather', glow: '#ffb84a' }], ['hair']], gear: [['hair', { style: 'long' }], ['tiara', { gem: '#ff5a4a' }]],
  face: { mouth: 'smile' }, eyes: { color: '#ff8a2a', calm: true }, near: ['chest'], far: ['hold', { kind: 'orb', color: '#ffb84a' }] });

H('fire', 17, 'Amaterasu', 'Amaterasu, déesse du soleil (Japon)', {
  legs: 'robe', build: 'slim', colors: { skin: '#f8dcc4', hair: '#2a2226', cloth: '#f4ead8', belt: '#c83a3a' },
  robeInner: '<path d="M98 110 L120 110 L132 236 L84 236 Z" fill="#c83a3a"/>',
  back: [['sun', {}], ['hair']], gear: [['hair', { style: 'long' }], ['tiara', { gem: '#ff5a4a' }]], eyes: { color: '#c8641e', calm: true },
  near: ['chest'], far: ['hold', { kind: 'mirror', color: '#fff3c0' }] });
