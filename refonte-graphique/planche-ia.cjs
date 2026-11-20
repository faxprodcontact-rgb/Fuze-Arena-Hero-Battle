// Planches de référence pour une IA d'image (Hailuo) : 18 personnages par image 4K (3840 × 2160), grille 6 × 3,
// fond blanc uni, AUCUN texte (l'IA recopierait des lettres abîmées), pas d'aura de rareté (le jeu l'ajoute lui-même).
//   node planche-ia.cjs heros fire  sortie.png      → les 18 héros d'un élément (rangée 1 = communs/rares, etc.)
//   node planche-ia.cjs monstres fire sortie.png    → les 3 familles de monstres d'un élément (une famille par rangée)
//   node planche-ia.cjs liste "h:fire:6,m:glaces:5" sortie.png → personnages choisis, 21:9, bas à droite laissé vide
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { SHARED_DEFS } = require('./kit.cjs');
const [, , kind, el, out] = process.argv;
// mode « liste » : des personnages choisis (h:fire:6 = héros, m:glaces:5 = monstre), grille 7 × 3 au format 21:9
// (celui que rend Hailuo), cases vides en bas à droite (là où Hailuo pose sa signature)
const LIST = kind === 'liste';
const W = LIST ? 3696 : 3840, H = LIST ? 1584 : 2160, COLS = LIST ? 7 : 6, ROWS = 3, CW = W / COLS, CH = H / ROWS;
const SILS = {};
let list, DEFS = '';
if (LIST) {
  const { all } = require('./heroes6.cjs'), M = require('./mon6.cjs'), HD = require('./fig6.cjs').HERO_DEFS;
  const heroes = all(); DEFS = HD + M.MON_DEFS;
  list = el.split(',').map((k) => { const [t, a, b] = k.split(':');
    const x = t === 'h' ? heroes.find((y) => y.element === a && y.index === +b) : M.all([a]).find((y) => y.index === +b);
    if (!x) throw new Error('inconnu : ' + k); SILS[x.name] = t === 'h' ? 'silH' : 'sil2'; return x; });
} else if (kind === 'heros') {
  const { all } = require('./heroes6.cjs');
  DEFS = require('./fig6.cjs').HERO_DEFS;
  list = all().filter((x) => x.element === el).sort((a, b) => a.index - b.index);
} else {
  const M = require('./mon6.cjs');
  DEFS = M.MON_DEFS;
  const fams = M.FAMILIES.filter((f) => f.element === el).map((f) => f.key);
  list = M.all(fams).sort((a, b) => fams.indexOf(a.family) - fams.indexOf(b.family) || a.index - b.index);
}
const SIL = (x) => SILS[x.name] ?? (kind === 'heros' ? 'silH' : 'sil2');

let body = '', defs = '';
list.forEach((x, n) => {
  const col = n % COLS, row = Math.floor(n / COLS);
  // même taille de base pour tous, les grands gardent un peu plus de place (sans déborder de leur case)
  const k = (LIST ? 1.8 : 2.25) * Math.min(1.1, Math.max(0.9, x.scale)), gy = row * CH + CH - (LIST ? 30 : 52);
  const tr = `translate(${col * CW + CW / 2 - 106 * k} ${gy - 228 * k}) scale(${k})`;
  defs += x.fig.defs;
  body += `<ellipse cx="${col * CW + CW / 2}" cy="${gy}" rx="${60 * k}" ry="${9 * k}" fill="#000" opacity="0.08"/>`
    + `<g transform="${tr}">${x.fig.glow}</g><g transform="${tr}" filter="url(#${SIL(x)})">${x.fig.body}</g><g transform="${tr}">${x.fig.fx}</g>`;
});
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><defs>${SHARED_DEFS}${DEFS}${defs}</defs><rect width="${W}" height="${H}" fill="#ffffff"/>${body}</svg>`;

(async () => {
  const tmp = path.join(require('os').tmpdir(), `planche-${kind}-${el}.html`);
  fs.writeFileSync(tmp, `<html><body style="margin:0">${svg}</body></html>`);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await p.goto('file://' + tmp); await p.waitForTimeout(800);
  await p.screenshot({ path: out });
  await b.close();
  console.log(out, list.map((x) => x.name).join(' | '));
})();
