// FEU — rouges, orangés, or, fer noir, lave. Chaque héros a sa carrure, ses jambes, son visage et sa pose.
const { H, tone, metal } = require('./heroes6.cjs');
const bronze = metal('#c9903c'), iron = metal('#4a444e'), LAVA = '#ff7a1a';
const crack = (d, w = 3.2) => `<path d="${d}" stroke="${LAVA}" stroke-width="${w}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;

H('fire', 0, 'Garde-braise', 'hoplite, gardien du feu sacré', {
  colors: { skin: '#e2a878', cloth: '#b92b36', steel: bronze, crest: '#d8452a', shieldFace: '#b92b36', belt: '#6a4428', boot: '#e2a878' },
  chest: [['plate', { t: 'steel' }]], skirt: { len: 26, strips: 6, trim: 'gold' }, legs: { kind: 'legs', leg: 'bare', foot: 'sandal', shin: 'steel' },
  head: { kind: 'human', eyes: { style: 'fierce', color: '#5a3a20' }, mouth: 'none', nose: 'none', ear: false, brow: { shape: 'none' } },
  gear: [['helm', { kind: 'corinth', crest: 'tall', crestT: 'crest' }]],
  near: { hand: [50, 154], el: [52, 140], items: [['pole', { butt: [48, 228], end: [52, 10], head: 'spear', hl: 30, hw: 15 }]] },
  far: { noArm: true, handKind: 'none', item: ['shield', { kind: 'round', r: 40, c: [158, 164], emblem: 'flame', t: 'steel' }] } });

H('fire', 1, 'Forgeron', 'forgeron des dieux', {
  body: 'round', shape: { sw: 38, arm: [28, 24] }, colors: { skin: '#d9a074', hair: '#2a2226', apron: '#7a4a2a', pants: '#3a3038', boot: '#2a2226', belt: '#3a2a22', iron },
  bare: true, bareArms: true, chest: [['muscle'], ['apron', { t: 'apron' }]], legs: { kind: 'legs', leg: 'baggy', foot: 'boot', cuffT: 'belt', stance: 'mid' },
  head: { kind: 'human', jaw: 'square', eyes: { style: 'sly', color: '#7a4a1e' }, brow: { k: 6.5, lift: [3, 0] }, nose: 'big', mustache: 'walrus', stubble: '#2a2226', mouth: 'none', band: { t: '#c83a3a', y: 52 } },
  near: { pose: 'shoulder', over: true, items: [['mace', { kind: 'hammer', to: [34, 100], layer: 'shoulder', t: 'iron', band: LAVA, L: 56, W: 30 }]] },
  far: { pose: 'down' }, atk: 'smash', rig: { wind: -18, hit: 125 } });

H('fire', 2, 'Cracheur de feu', 'saltimbanque cracheur de feu', {
  grp: { top: 'head' },
  body: 'slim', colors: { skin: '#e6b88a', hair: '#2a2226', vest: '#8a2a2a', pants: '#e0b040', boot: '#3a2a22', belt: '#3a2a22' },
  bare: true, bareArms: true, chest: [['muscle'], ['vest', { t: 'vest' }]], legs: { kind: 'legs', leg: 'baggy', stripe: '#b8482a', foot: 'shoe', cuffT: 'vest' },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'wide', color: '#5a3a20' }, brow: { shape: 'arch', lift: 4, k: 4 }, mouth: 'o', mustache: 'handle' },
  gear: [['hair', { style: 'strip' }], ['disc', { x: 78, y: 30, r: 10, t: 'hair', sh: 3 }]],
  near: { pose: 'down', item: ['bottle', { t: '#6a8a5a' }] },
  far: { hand: [160, 128], el: [158, 142], item: ['torch', {}] },
  top: [['breath', { from: [140, 107], len: 62 }]] });

H('fire', 3, 'Légionnaire de lave', 'légionnaire romain, bouclier d\'obsidienne', {
  colors: { skin: '#e2a878', cloth: '#8a2a2a', steel: iron, crest: '#ff8a2a', shieldFace: '#2a2228', boot: '#e2a878', belt: '#e6ac3c', cape: '#8a2a2a' },
  chest: [['segments', { t: 'steel' }]], skirt: { len: 24, strips: 7 }, legs: { kind: 'legs', leg: 'bare', foot: 'sandal', stance: 'mid' },
  head: { kind: 'human', jaw: 'square', eyes: { style: 'angry', color: '#5a3a20' }, mouth: 'frown', nose: 'hook', stubble: '#3a2a22', ear: false },
  gear: [['helm', { kind: 'dome', crest: 'cross', crestT: 'crest', cheek: true, plain: true }]], back: [['cape', { len: 'short' }]],
  near: { hand: [54, 108], el: [52, 134], item: ['sword', { to: [36, 40], w: 15, guard: 12 }] },
  far: { noArm: true, handKind: 'none', item: ['shield', { kind: 'scutum', t: 'steel', inner: crack('M148 112 L160 136 L150 156 L168 180 L158 204 M160 136 L176 146 M150 156 L140 168') }] } });

H('fire', 4, 'Salamandre', 'salamandre, esprit du feu', {
  body: 'slim', shape: { lean: 9, hdx: 4 }, colors: { skin: '#f08a2a', muz: '#ffd9a0', tail: '#f08a2a', fin: '#3a3038', cloth: '#3a3038', belt: '#3a3038', boot: '#c8641e' },
  bare: true, bareArms: true, chest: [['belly', { t: 'muz' }], ['spots']], skirt: { len: 18, ragged: true }, legs: { kind: 'beast', t: 'skin', foot: 'paw' },
  head: { kind: 'lizard', eyes: { style: 'sly', color: '#ffe14a', sclera: '#fff3a8', slit: true }, tongue: true, paint: '<g fill="#3a2a22"><circle cx="84" cy="64" r="5"/><circle cx="100" cy="54" r="4"/><circle cx="78" cy="98" r="4"/></g>' },
  back: [['tail', { kind: 'lizard', w: 24 }]], gear: [['frill', { len: 26 }]],
  near: { hand: [118, 166], el: [88, 164], item: ['small', { kind: 'dagger', t: '#2a2228', dir: [32, 2] }] },
  far: { hand: [172, 146], el: [158, 150], item: ['small', { kind: 'dagger', t: '#2a2228', dir: [30, -12] }] } });

H('fire', 5, 'Vestale', 'prêtresse du foyer sacré (Vesta)', {
  body: 'slim', colors: { skin: '#f2c9a4', cloth: '#f4ead8', belt: '#c83a3a', veil: '#f4ead8' },
  legs: { kind: 'straight', panel: '#ecd9be', folds: true },
  head: { kind: 'human', eyes: { style: 'closed', lash: true }, brow: { shape: 'arch', k: 3, c: '#6a4a2a' }, mouth: 'smile', nose: 'button', ear: false },
  gear: [['veil', { band: { t: 'gold', y: 60, k: 7 } }]], back: [['hairBack', { style: 'long', t: 'veil' }]],
  near: { pose: 'center', hand: [118, 162], el: [90, 168] },
  far: { pose: 'center', hand: [150, 162], el: [152, 162], over: true, items: [['bowl', { hand: [134, 160] }]] } });

H('fire', 6, 'Chamane du volcan', 'Pélé, déesse hawaïenne des volcans', {
  body: 'curvy', colors: { skin: '#a86a44', hair: '#2a2226', cloth: '#d8452a', belt: '#f0b23a' },
  bare: true, bareArms: true, chest: [['raw', { svg: '<path d="M20 116 L190 116 L190 140 C130 150 90 150 20 140 Z" fill="#d8452a"/>' }]], skirt: { len: 46, strips: 9, ragged: true, flare: 12 },
  legs: { kind: 'legs', leg: 'bare', foot: 'bare', footT: 'skin', stance: 'narrow', anklet: 'gold' },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'wide', color: '#ff8a2a', sclera: '#fff3a8', lash: true }, brow: { k: 4, shape: 'angry' }, mouth: 'shout', mouthC: '#7a1c1c' },
  gear: [['hair', { style: 'long' }], ['flower', { color: '#ff5a4a', x: 82, y: 58 }]], back: [['hairBack', { style: 'waves' }]], neck: [['beads', { t: '#ff8a2a', r: 5.5 }]],
  near: { pose: 'hip', over: true },
  far: { pose: 'high', handKind: 'open', dir: [0, -1], item: ['orb', { color: LAVA, flame: true, r: 13, dy: 30 }] } });

H('fire', 7, 'Golem de magma', 'géant de pierre et de lave', {
  scale: 1.15, body: 'brute', shape: { arm: [34, 30], hs: 0.88, hdy: 8 }, colors: { skin: '#4a3c42', boot: '#33282e', rock: '#33282e' },
  bare: true, bareArms: true, noBelt: true, chest: [['cracks', { c: LAVA }]], legs: { kind: 'stone', t: 'skin' },
  head: { kind: 'golem', eyes: { color: LAVA }, maw: true, paint: crack('M82 58 L94 72 L88 84 M132 52 L126 66') },
  neck: [['pad', { t: 'rock' }], ['padFar', { t: 'rock' }]],
  near: { hand: [126, 172], el: [80, 168], r: 19 }, far: { hand: [170, 152], el: [160, 152], r: 16 }, atk: 'smash', rig: { wind: -50, hit: 30 } });

H('fire', 8, 'Oni rouge', 'oni, ogre des légendes japonaises', {
  scale: 1.1, body: 'heavy', shape: { belly: 8 }, colors: { skin: '#d8483a', hair: '#2a2226', tiger: '#f0a030', belt: '#3a2a22', iron, boot: '#d8483a' },
  bare: true, bareArms: true, chest: [['muscle']], skirt: { len: 30, t: 'tiger', strips: 5, flare: 5 }, legs: { kind: 'legs', leg: 'thick', t: 'skin', foot: 'bare', anklet: 'gold', stance: 'wide' },
  head: { kind: 'human', jaw: 'square', eyes: { style: 'fierce', color: '#ffe14a', sclera: '#fff3a8' }, brow: { k: 6.5, c: '#2a2226' }, mouth: 'shout', tusks: 'big', nose: 'big', ear: false },
  gear: [['horns', { kind: 'oni' }]], neck: [['beads', { t: 'bone', r: 5.5 }]],
  near: { hand: [126, 152], el: [90, 160], item: ['club', { to: [200, 88], studs: true, bend: 6, w1: 30 }] },
  far: { hand: [166, 160], el: [164, 152] }, atk: 'smash' });

H('fire', 9, 'Lancier-dragon', 'artilleur à la lance de feu (Chine ancienne)', {
  colors: { skin: '#e6b88a', hair: '#2a2226', cloth: '#8a2a2a', pants: '#3a3038', steel: bronze, iron, crest: '#d8452a', boot: '#2a2226' },
  chest: [['lamellar', { t: 'steel' }]], skirt: { len: 20, strips: 5 }, legs: { kind: 'legs', leg: 'baggy', foot: 'shoe', cuffT: 'cloth', stance: 'mid' },
  head: { kind: 'human', jaw: 'long', eyes: { style: 'wink', color: '#5a3a20' }, mouth: 'flat', mustache: 'droop', ear: false },
  gear: [['helm', { kind: 'cone', tassel: 'crest' }]],
  near: { hand: [112, 158], el: [84, 158], item: ['gun', { kind: 'cannon', glow: LAVA }] },
  far: { hand: [150, 150], el: [152, 152], over: true, tint: true } });

H('fire', 10, 'Kitsune', 'renarde à plusieurs queues (Japon)', {
  scale: 0.97, body: 'curvy', colors: { skin: '#f6d2b4', hair: '#f4ead8', cloth: '#f4ead8', pants: '#c83a3a', tail: '#f08a2a', fox: '#f08a2a', belt: '#c83a3a', boot: '#f4ead8' },
  chest: [['wrap', { t: '#c83a3a' }]], legs: { kind: 'legs', leg: 'hakama', foot: 'geta', stance: 'lunge' },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'wink', color: '#f0a020', lash: true }, brow: { shape: 'arch', k: 3.4, c: '#b8a890' }, mouth: 'grin', ear: false,
    paint: '<path d="M70 98 L84 100 M70 106 L82 106" stroke="#c83a3a" stroke-width="3" stroke-linecap="round"/>' },
  gear: [['ears', { kind: 'fox', t: 'fox', inner: 'hair' }], ['hair', { style: 'bob' }]], back: [['tail', { kind: 'fox', n: 3 }]],
  near: { pose: 'fwd', item: ['small', { kind: 'kunai', dir: [33, 6] }] },
  far: { pose: 'open', handKind: 'open', dir: [0.2, -1], item: ['orb', { color: '#6fd8ff', flame: true, r: 10, dy: 26 }] } });

H('fire', 11, 'Prêtre du soleil', 'prêtre aztèque du dieu soleil', {
  colors: { skin: '#b87a4a', hair: '#2a2226', red: '#c83a3a', belt: '#e6ac3c', boot: '#b87a4a' },
  bare: true, bareArms: true, bracers: 'gold', chest: [['muscle']], skirt: { len: 20, t: 'red', flap: 'gold', flapLen: 0, trim: 'gold' },
  legs: { kind: 'legs', leg: 'bare', foot: 'sandal', stance: 'narrow', anklet: 'gold' },
  head: { kind: 'human', jaw: 'square', eyes: { style: 'closed' }, brow: { k: 5 }, mouth: 'shout', ear: false, paint: '<path d="M40 100 L170 96" stroke="#c83a3a" stroke-width="5" opacity="0.85"/>' },
  gear: [['feathers', { colors: ['#e0483a', '#f0b23a', '#2fa37a'], n: 7 }], ['hair', { style: 'short' }]], neck: [['collar', { gem: '#2fa37a', stripes: '#c83a3a' }]],
  near: { pose: 'chest', handKind: 'open', dir: [1, -0.2] },
  far: { pose: 'high', hand: [164, 88], items: [['glow', { x: 168, y: 58, r: 30, c: '#ffcf5a', layer: 'front' }], ['disc', { x: 168, y: 58, r: 22, t: 'gold', sh: 4, layer: 'front', inner: '<circle cx="168" cy="58" r="13" fill="none" stroke="#b8482a" stroke-width="3"/><circle cx="168" cy="58" r="5" fill="#b8482a"/>' }]] } });

H('fire', 12, 'Djinn', 'djinn des contes arabes', {
  body: 'round', colors: { skin: '#e8793a', hair: '#2a2226', smoke: '#7a4a5a', vest: '#5a3a8a', turban: '#f4ead8', belt: '#e6ac3c' },
  bare: true, bareArms: true, bracers: 'gold', chest: [['muscle'], ['vest', { t: 'vest' }]], legs: 'smoke',
  head: { kind: 'human', jaw: 'chubby', eyes: { style: 'sly', color: '#ffe14a', sclera: '#fff3a8' }, brow: { shape: 'arch', lift: [6, 0], k: 5.5 }, mouth: 'grin', mustache: 'handle', nose: 'big' },
  gear: [['turban', { feather: true, gem: '#e04a4a' }]], neck: [['collar', {}]],
  far: { hand: [98, 152], el: [144, 162], over: true, tint: true }, near: { pose: 'cross', over: true } });

H('fire', 13, 'Surt', 'Surt, roi des géants de feu (Scandinavie)', {
  scale: 1.22, body: 'brute', colors: { skin: '#3a2c30', hair: '#ff8a2a', cloth: '#2a2228', pants: '#2a2228', boot: '#1c161a', steel: iron, bone: '#1c161a', cape: '#2a2228', belt: '#8a2a2a' },
  bareArms: true, chest: [['plate', { t: 'steel' }], ['cracks', { c: LAVA, d: 'M96 128 L110 142 L104 154 M120 126 L126 138' }]], skirt: { len: 26, ragged: true },
  legs: { kind: 'legs', leg: 'thick', foot: 'sabaton', footT: 'steel', shin: 'steel' },
  head: { kind: 'human', jaw: 'long', eyes: { style: 'glow', color: '#ffcf5a', lid: '#1c161a' }, brow: { k: 6, c: '#ff8a2a' }, mouth: 'gritted', nose: 'none', ear: false, paint: crack('M84 60 L92 72 M132 56 L128 66', 2.6) },
  gear: [['horns', { kind: 'bull', t: 'bone' }], ['hair', { style: 'flame' }]], back: [['cape', { len: 'torn' }]],
  neck: [['pad', { t: 'steel', spike: true, spikeT: 'bone' }], ['padFar', { t: 'steel' }]],
  near: { pose: 'up', over: true, item: ['sword', { to: [214, 40], w: 28, guard: 22, glow: LAVA, flame: true }] }, far: { hand: [170, 146], el: [166, 152] } });

H('fire', 14, 'Sekhmet', 'Sekhmet, déesse lionne (Égypte)', {
  body: 'curvy', colors: { skin: '#e0a850', muz: '#f0cf90', boot: '#e0a850', cloth: '#f4ead8', belt: '#c83a3a', bow: metal('#e6ac3c'), nem: '#2a3a6a' },
  bareArms: true, bracers: 'gold', skirt: { len: 46, t: 'cloth', trim: 'gold', flare: 8 }, legs: { kind: 'legs', leg: 'bare', foot: 'sandal', stance: 'narrow', anklet: 'gold' }, neck: [['collar', { gem: '#3fa8d8', stripes: '#3fa8d8' }]],
  head: { kind: 'lion', eyes: { style: 'fierce', color: '#ffb020', sclera: '#fff3a8', slit: true }, whiskerDots: true, band: { t: 'gold', y: 56, k: 8, gem: '#c83a3a' } },
  gear: [['sundisc', {}], ['ears', { kind: 'cat' }]], back: [['cape', { len: 'short', t: '#c83a3a' }]],
  near: { pose: 'pull' }, far: { pose: 'fwd', item: ['bow', { glow: '#ffb84a', top: 56, bot: 200, layer: 'behind' }] } });

H('fire', 15, 'Ifrit', 'ifrit, démon de feu', {
  body: 'tall', colors: { skin: '#2c2228', cloth: '#8a2a2a', wing: '#8a2a2a', bone: '#c83a3a', steel: iron, tail: '#2c2228', belt: '#e6ac3c', pants: '#5a1c22', boot: '#2c2228' },
  bare: true, bareArms: true, bracers: 'gold', chest: [['muscle'], ['cracks', { c: LAVA, d: 'M92 126 L100 140 M124 124 L118 138', w: 2.6 }]],
  legs: { kind: 'legs', leg: 'baggy', foot: 'bare', stance: 'lunge', cuffT: 'gold' },
  head: { kind: 'human', jaw: 'point', eyes: { style: 'glow', color: LAVA, lid: '#1c161a' }, brow: { shape: 'none' }, mouth: 'grin', nose: 'none', ear: false },
  gear: [['ears', { kind: 'elf' }], ['horns', { kind: 'long', t: 'bone' }]], back: [['wings', { kind: 'bat', glow: LAVA }], ['tail', { kind: 'devil' }]],
  near: { pose: 'up', item: ['sword', { to: [188, 50], w: 17, curve: 13, guard: 12, glow: LAVA }] },
  far: { pose: 'high', item: ['sword', { to: [202, 36], w: 15, curve: 11, guard: 10 }] } });

H('fire', 16, 'Phénix', 'le phénix qui renaît de ses cendres', {
  body: 'curvy', colors: { skin: '#f6d2b4', hair: '#ff6a2a', cloth: '#f4ead8', belt: '#e6ac3c', wing: '#ff8a2a' },
  legs: { kind: 'ragged', w: 50, panel: '#ffb84a', base: 'mist', baseC: '#ffb84a' },
  head: { kind: 'human', eyes: { style: 'soft', color: '#c8641e', lash: true }, brow: { shape: 'arch', k: 3 }, mouth: 'smile', blush: '#ff8a6a', ear: false },
  gear: [['hair', { style: 'parted' }], ['tiara', { gem: '#ff5a4a' }]], back: [['wings', { kind: 'big', glow: '#ffb84a' }], ['tail', { kind: 'feathers', t: 'wing' }], ['hairBack', { style: 'long' }]],
  near: { hand: [60, 144], el: [70, 152], handKind: 'open', dir: [-1, -0.5] },
  far: { pose: 'open', handKind: 'open', dir: [0.4, -1], item: ['orb', { flame: true, color: '#ffb84a', r: 11, dy: 28 }] } });

H('fire', 17, 'Amaterasu', 'Amaterasu, déesse du soleil (Japon)', {
  body: 'slim', colors: { skin: '#f8dcc4', hair: '#2a2226', cloth: '#f4ead8', belt: '#c83a3a' },
  chest: [['wrap', { t: '#c83a3a' }]], legs: { kind: 'bell', w: 56, panel: '#c83a3a', tiers: true, trim: 'gold' },
  head: { kind: 'human', eyes: { style: 'soft', color: '#c8641e', lash: true }, brow: { shape: 'flat', k: 3 }, mouth: 'smile', mouthC: '#c83a3a', ear: false },
  gear: [['hair', { style: 'long' }], ['crown', { kind: 'spire', gem: '#ff5a4a' }]], back: [['sun', {}], ['hairBack', { style: 'floor' }]],
  near: { pose: 'center', hand: [120, 156], el: [88, 164], w0: 22, w1: 30 },
  far: { pose: 'center', hand: [152, 156], el: [154, 158], over: true, w0: 20, w1: 28, items: [['mirror', { hand: [132, 172], handle: false, r: 20, color: '#fff3c0' }]] } });
