// Exporte les 72 héros en morceaux pour le site de test (galerie + aperçu des animations) :
//   public/apercu/h/<identifiant du jeu>.png  et  public/apercu/heros.js
//   + refonte-graphique/HEROS.md (la liste)
//   node refonte-graphique/export72.cjs
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { all, ELEMENTS } = require('./heroes6.cjs');
const { SHARED_DEFS } = require('./kit.cjs');

const OUT = path.join(__dirname, '..', 'public', 'apercu');
const E = 1.5, MX = 70, MY = 70, CW = 340, CH = 320; // marges larges : ailes, cornes, halos
const FACTIONS = ['knights', 'assassins', 'mages', 'demons', 'angels', 'myths'];
const gameId = (el, i) => { const n = ELEMENTS.indexOf(el) * 18 + i; return `${FACTIONS[Math.floor(n / 12)]}-${n % 12 + 1}`; };

(async () => {
  fs.mkdirSync(path.join(OUT, 'h'), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const list = [];
  for (const x of all()) {
    const c = x.fig, id = gameId(x.element, x.index);
    const parts = [...(c.glow ? [{ name: 'glow', svg: c.glow }] : []), ...c.parts];
    const svgs = parts.map((p) => `<svg xmlns="http://www.w3.org/2000/svg" width="${CW * E}" height="${CH * E}" viewBox="${-MX} ${-MY} ${CW} ${CH}"><defs>${SHARED_DEFS}${c.defs}</defs>${p.svg}</svg>`);
    const res = await page.evaluate(async ({ svgs, W, H }) => {
      const cut = [];
      for (const svg of svgs) {
        const img = new Image();
        await new Promise((ok, ko) => { img.onload = ok; img.onerror = ko; img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg); });
        const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
        const g = cv.getContext('2d'); g.drawImage(img, 0, 0);
        const d = g.getImageData(0, 0, W, H).data;
        let x0 = W, y0 = H, x1 = -1, y1 = -1;
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (d[(y * W + x) * 4 + 3] > 2) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
        cut.push(x1 < 0 ? null : { cv, x0, y0, w: x1 - x0 + 1, h: y1 - y0 + 1 });
      }
      const AW = 768; let x = 1, y = 1, rowH = 0; const pos = [];
      for (const p of cut) { if (!p) { pos.push(null); continue; } if (x + p.w + 1 > AW) { x = 1; y += rowH + 1; rowH = 0; } pos.push({ x, y }); x += p.w + 1; rowH = Math.max(rowH, p.h); }
      const atlas = document.createElement('canvas'); atlas.width = AW; atlas.height = y + rowH + 1;
      const ag = atlas.getContext('2d');
      cut.forEach((p, i) => p && ag.drawImage(p.cv, p.x0, p.y0, p.w, p.h, pos[i].x, pos[i].y, p.w, p.h));
      return { png: atlas.toDataURL('image/png'), meta: cut.map((p, i) => p && ({ x: pos[i].x, y: pos[i].y, w: p.w, h: p.h, bx: p.x0, by: p.y0 })) };
    }, { svgs, W: CW * E, H: CH * E });
    fs.writeFileSync(path.join(OUT, 'h', id + '.png'), Buffer.from(res.png.split(',')[1], 'base64'));
    const pp = parts.map((p, i) => res.meta[i] && ({ name: p.name, x: res.meta[i].x, y: res.meta[i].y, w: res.meta[i].w, h: res.meta[i].h, ox: +(res.meta[i].bx / E - MX).toFixed(2), oy: +(res.meta[i].by / E - MY).toFixed(2) })).filter(Boolean);
    list.push({ id, element: x.element, index: x.index, rarity: x.rarity, role: x.role, leader: x.leader, name: x.name, from: x.from, scale: x.scale, rig: { ...c.rig, ...(x.role === 'healer' ? { heal: true } : {}) }, parts: pp });
    process.stdout.write('.');
  }
  fs.writeFileSync(path.join(OUT, 'heros.js'), '// Fabriqué par refonte-graphique/export72.cjs — ne pas modifier à la main.\nwindow.HEROS = ' + JSON.stringify({ E, list }) + ';\n');
  // la liste en clair, pour le propriétaire
  const RAR = { common: 'Commun', rare: 'Rare', epic: 'Épique', legendary: 'Légendaire' }, ROLE = { protector: 'Protecteur', warrior: 'Guerrier', marksman: 'Tireur', assassin: 'Assassin', healer: 'Soigneur', support: 'Soutien' };
  const TITLE = { fire: 'Feu', wind: 'Vent', water: 'Eau', earth: 'Terre' };
  let md = '# Les 72 héros (habillage provisoire)\n\nFabriqué par `export72.cjs` (ne pas modifier à la main : changer les fichiers `h6-*.cjs` puis relancer).\nNoms provisoires. ♛ = chef de section. Inspirations : mythologies et légendes du monde, jamais un personnage d\'un autre jeu.\n';
  for (const el of ELEMENTS) { md += `\n## ${TITLE[el]}\n\n| Identifiant | Nom provisoire | Rareté | Rôle | Inspiration |\n|---|---|---|---|---|\n`; for (const h of list.filter((x) => x.element === el)) md += `| \`${h.id}\` | ${h.leader ? '♛ ' : ''}${h.name} | ${RAR[h.rarity]} | ${ROLE[h.role]} | ${h.from} |\n`; }
  fs.writeFileSync(path.join(__dirname, 'HEROS.md'), md);
  console.log('\n' + list.length + ' héros exportés');
  await browser.close();
})();
