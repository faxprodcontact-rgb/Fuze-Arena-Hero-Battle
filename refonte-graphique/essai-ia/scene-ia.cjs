// La scène du jeu (720 × 980) avec le décor et les personnages de l'essai par IA, aux mêmes places que dans le jeu.
const fs = require('fs');
const SET = process.env.SET || 'a';
const meta = JSON.parse(fs.readFileSync(`meta-${SET}.json`, 'utf8'));
const W = 720, H = 980, GT = 560, SQ = 0.8;
const HERO_X = { 3: 95, 4: 95, 2: 198, 0: 300, 1: 300 }, ENEMY_X = { 0: 420, 1: 420, 2: 522, 3: 625, 4: 625 };
const ROW_DY = { 0: 90, 3: 90, 2: 180, 1: 270, 4: 270 };
const px = (x) => 360 + (x - 360) * SQ;
// emplacement → fichier (héros : protecteur, guerrier, archer, soigneuse, assassin ; ennemis dans l'ordre de la planche)
const heroTeam = { 0: 'hero-0', 1: 'hero-1', 2: 'hero-3', 3: 'hero-2', 4: 'hero-4' };
const foeTeam = { 0: 'foe-0', 1: 'foe-1', 2: 'foe-2', 3: 'foe-3', 4: 'foe-4' };
const hp = { 'hero-0': 1, 'hero-1': 0.82, 'hero-3': 1, 'hero-2': 0.94, 'hero-4': 0.7, 'foe-0': 0.45, 'foe-1': 0.8, 'foe-2': 0.9, 'foe-3': 1, 'foe-4': 0.66 };
const K = +(process.env.K || 1), DY = +(process.env.DY || 0);
const cast = [];
for (const [slot, id] of Object.entries(heroTeam)) cast.push({ id, x: px(HERO_X[slot]), y: GT + ROW_DY[slot] + 56 + DY, foe: false });
for (const [slot, id] of Object.entries(foeTeam)) cast.push({ id, x: px(ENEMY_X[slot]), y: GT + ROW_DY[slot] + 56 + DY, foe: true });
cast.sort((a, b) => a.y - b.y);
let s = '', bars = '';
for (const u of cast) {
  const m = meta[u.id], w = m.w * K, h = m.h * K;
  s += `<div class="sh" style="left:${u.x - 34 * K}px;top:${u.y - 9 * K}px;width:${68 * K}px;height:${18 * K}px"></div>`;
  s += `<img src="s${SET}-${u.id}.png" style="left:${u.x - m.fx * K}px;top:${u.y - m.fy * K}px;width:${w}px;height:${h}px">`;
  const by = u.y - (m.fy - m.top) * K - 14, bw = 52;
  bars += `<div class="bar" style="left:${u.x - bw / 2 - 2}px;top:${by - 2}px;width:${bw + 4}px"><i style="width:${bw * hp[u.id]}px;background:${u.foe ? '#e5484d' : '#3ccf7a'}"></i></div>`;
  if (!u.foe) bars += `<div class="en" style="left:${u.x - bw / 2}px;top:${by + 11}px;width:${bw * (0.3 + hp[u.id] * 0.5)}px"></div>`;
}
const bgH = Math.round(W * 2400 / 1792);
fs.writeFileSync(process.env.OUT || 'scene-ia.html', `<html><body style="margin:0;background:#000"><style>
.sc{position:relative;width:${W}px;height:${H}px;overflow:hidden;background:url(s-bg.jpg) center top/auto ${H}px no-repeat}
.sc img{position:absolute;filter:drop-shadow(0 2px 2px rgba(20,10,30,.35))}
.sh{position:absolute;border-radius:50%;background:rgba(30,20,10,.45);filter:blur(4px)}
.bar{position:absolute;height:12px;border-radius:5px;background:rgba(18,10,28,.85)}
.bar i{position:absolute;left:2px;top:2px;height:8px;border-radius:3.5px;box-shadow:inset 0 3px 0 rgba(255,255,255,.35)}
.en{position:absolute;height:3.4px;border-radius:1.5px;background:#4fd1ff}
</style><div class="sc">${s}${bars}</div></body></html>`);
