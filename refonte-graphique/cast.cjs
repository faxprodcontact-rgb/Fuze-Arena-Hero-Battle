// Les 5 héros et les 5 ennemis de la planche.
const { chibi, tone, metal, mix } = require('./chibi.cjs');
const flame = `<path d="M118 146 C112 156 114 166 122 170 C120 164 124 158 128 154 C128 162 132 166 136 166 C140 160 138 150 130 144 C131 150 127 154 123 154 C124 150 122 148 118 146 Z" fill="#e6ac3c"/>`;
const LE = [-0.5, -0.85]; // les ennemis sont retournés : leur lumière aussi

const HEROES = {
  protector: chibi({ id: 'p', colors: { skin: '#eebf98', hair: '#b8642a', cloth: '#3f7a44', cloth2: '#2e4a3a', accent: '#4fae5a', plate: metal('#a9b8ac'), helm: metal('#aab6c2'), shield: metal('#b9c0d0'), shieldFace: tone('#3f8a4a'), boot: tone('#4a3a2a'), glove: tone('#6a4a2e'), sleeve: tone('#3f7a44'), cape: tone('#2f6a3c') },
    helmet: 'horned', mouth: 'beard', outfit: 'plate', pad: 'big', pose: 'shoulder', weapon: 'hammerShoulder', offhand: 'shield', cape: true, eyes: { color: '#5a9a3a' }, browColor: '#7a3f16',
    shieldEmblem: `<path d="M182 140 L196 166 L186 166 L192 190 L170 162 L180 162 L174 140 Z" fill="#e6ac3c" stroke="#5a3508" stroke-width="1.6" stroke-linejoin="round"/>` }),
  warrior: chibi({ id: 'w', colors: { skin: '#f6c9a4', hair: '#e8502a', cloth: '#b92b36', cloth2: '#3a3550', accent: '#e0344a', scarf: tone('#f0b23a'), band: tone('#f4efe6'), boot: tone('#4a3226'), glove: tone('#5a3826') },
    hairStyle: 'spiky', headband: true, scarf: true, outfit: 'plate', pad: 'small', weapon: 'greatsword', bladeGlow: '#ff8a2a', mouth: 'smirk', eyes: { color: '#e0822a' }, emblem: flame }),
  archer: chibi({ id: 'a', colors: { skin: '#f8d6b8', hair: '#f2cf5a', cloth: '#3aa37a', cloth2: '#5a4634', accent: '#7be0c0', hood: tone('#2a8a66'), boot: tone('#5a4030'), glove: tone('#6a4a2e'), sleeve: tone('#e9f3e6'), bow: tone('#9a6a3c') },
    hairStyle: 'short', hood: true, ears: 'elf', quiver: true, outfit: 'leather', pose: 'draw', offhand: 'bow', bracer: true, mouth: 'calm', eyes: { color: '#2fa870' } }),
  healer: chibi({ id: 'h', colors: { skin: '#fbdcc4', hair: '#58a8f0', cloth: '#eef3ff', accent: '#3f78d8', sash: metal('#e6ac3c'), boot: tone('#3f5a9a'), sleeve: tone('#eef3ff') },
    hairStyle: 'long', circlet: true, outfit: 'robe', offhand: 'staff', orb: '#6fd0ff', mouth: 'smile', eyes: { color: '#6a5cf0' }, leader: true }),
  assassin: chibi({ id: 's', colors: { skin: '#e8b890', hair: '#2a2238', cloth: '#352c55', cloth2: '#272040', accent: '#9b5cf0', hood: tone('#3d3266'), scarf: tone('#8a4ce0'), boot: tone('#2a2238'), glove: tone('#2a2238'), sleeve: tone('#352c55') },
    hood: true, hoodTrim: '#9b5cf0', scarf: true, outfit: 'leather', weapon: 'dagger', offhand: 'dagger', mouth: 'mask', brows: false, eyes: { color: '#6ff0c8', glow: true } }),
};
const g = (skin) => mix(skin, '#1c2a10', 0.6);
const ENEMIES = {
  grunt: chibi({ id: 'g1', light: LE, colors: { skin: '#84c24c', hair: '#b83232', cloth: '#8a6238', cloth2: '#5a4028', accent: '#b83232', boot: tone('#4a3424'), glove: tone('#84c24c'), haft: tone('#8a5a34') },
    ears: 'goblin', nose: 'goblin', mouth: 'fangs', angry: true, hairStyle: 'mohawk', outfit: 'leather', weapon: 'club', browColor: g('#84c24c'), blush: '#4a8a2a', eyes: { color: '#f0b020', sclera: '#fff6b8', slit: true } }),
  rogue: chibi({ id: 'g2', light: LE, colors: { skin: '#6fb05a', hair: '#333', cloth: '#4a3a5a', cloth2: '#33283f', accent: '#c03a3a', band: tone('#c03a3a'), boot: tone('#33283f'), glove: tone('#6fb05a') },
    ears: 'goblin', nose: 'goblin', mouth: 'fangs', angry: true, headband: true, outfit: 'leather', weapon: 'dagger', offhand: 'dagger', browColor: g('#6fb05a'), blush: '#3f7a30', eyes: { color: '#ff7a2a', sclera: '#fff6b8', slit: true } }),
  brute: chibi({ id: 'g3', light: LE, colors: { skin: '#6f9a58', hair: '#2a2430', cloth: '#5a2f2f', cloth2: '#3a2a2a', accent: '#c03a3a', plate: metal('#6a6a7c'), padTone: metal('#6a6a7c'), boot: tone('#33282a'), glove: tone('#6f9a58'), haft: tone('#6a4a30'), sleeve: tone('#6f9a58') },
    ears: 'goblin', nose: 'goblin', mouth: 'fangs', angry: true, hairStyle: 'mohawk', outfit: 'plate', pad: 'big', pose: 'shoulder', weapon: 'axeShoulder', warpaint: '#d83a3a', browColor: g('#6f9a58'), blush: '#3f6a30', eyes: { color: '#ff4a3a', sclera: '#fff0c0', slit: true } }),
  shaman: chibi({ id: 'g4', light: LE, colors: { skin: '#8cc468', hair: '#333', cloth: '#5d3d8a', accent: '#3a2560', sash: tone('#c03a3a'), boot: tone('#3a2560'), glove: tone('#8cc468'), sleeve: tone('#5d3d8a'), haft: tone('#6a4a30') },
    ears: 'goblin', nose: 'goblin', mouth: 'fangs', skullcap: true, outfit: 'robe', offhand: 'skullStaff', orb: '#c070ff', browColor: g('#8cc468'), blush: '#4a8a3a', eyes: { color: '#c070ff', sclera: '#f4e6ff', glow: true } }),
  hunter: chibi({ id: 'g5', light: LE, colors: { skin: '#7ab852', hair: '#333', cloth: '#7a5a34', cloth2: '#4a3a28', accent: '#c03a3a', hood: tone('#6a4a2e'), boot: tone('#4a3424'), glove: tone('#7ab852'), sleeve: tone('#7ab852'), bow: tone('#5a4030') },
    ears: 'goblin', nose: 'goblin', mouth: 'fangs', angry: true, hood: true, hoodTrim: '#c03a3a', quiver: true, outfit: 'leather', pose: 'draw', offhand: 'bow', browColor: g('#7ab852'), blush: '#4a8a3a', eyes: { color: '#f0b020', sclera: '#fff6b8', slit: true } }),
};
module.exports = { HEROES, ENEMIES };
