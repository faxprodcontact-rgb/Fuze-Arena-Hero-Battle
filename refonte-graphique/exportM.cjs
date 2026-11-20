// Exporte les monstres en morceaux pour le site de test (combats de l'aperçu) :
//   public/apercu/m/<famille>-<place>.png  et  public/apercu/monstres.js
//   node refonte-graphique/exportM.cjs
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { all } = require('./mon6.cjs');
const { SHARED_DEFS } = require('./kit.cjs');

const OUT = path.join(__dirname, '..', 'public', 'apercu');
const E = 1.5, MX = 70, MY = 70, CW = 340, CH = 320;

(async () => {
  fs.mkdirSync(path.join(OUT, 'm'), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const list = [];
  for (const x of all()) {
    const c = x.fig, id = x.id;
    const parts = [...(c.glow ? [{ name: 'glow', svg: c.glow }] : []), ...c.parts, ...(c.fx ? [{ name: 'shine', svg: c.fx }] : [])];
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
    fs.writeFileSync(path.join(OUT, 'm', id + '.png'), Buffer.from(res.png.split(',')[1], 'base64'));
    const pp = parts.map((p, i) => res.meta[i] && ({ name: p.name, x: res.meta[i].x, y: res.meta[i].y, w: res.meta[i].w, h: res.meta[i].h, ox: +(res.meta[i].bx / E - MX).toFixed(2), oy: +(res.meta[i].by / E - MY).toFixed(2) })).filter(Boolean);
    list.push({ id, family: x.family, familyName: x.familyName, element: x.element, index: x.index, slot: x.slot, name: x.name, scale: x.scale, rig: c.rig, parts: pp });
    process.stdout.write('.');
  }
  fs.writeFileSync(path.join(OUT, 'monstres.js'), '// Fabriqué par refonte-graphique/exportM.cjs — ne pas modifier à la main.\nwindow.MONSTRES = ' + JSON.stringify({ E, list }) + ';\n');
  // la liste en clair, pour le propriétaire
  const { FAMILIES, SLOT_FR } = require('./mon6.cjs');
  const EL = { fire: 'Feu', wind: 'Vent', water: 'Eau', earth: 'Terre' };
  let md = '# Les monstres (72, en 12 familles de 6)\n\nFabriqué par `exportM.cjs` (ne pas modifier à la main : changer les fichiers `m-<famille>.cjs` puis relancer).\nDans chaque famille : rapide, costaud (devant) · tireur, sorts ou soin (derrière) · élite · boss.\n';
  for (const fam of FAMILIES) { const ms = list.filter((m) => m.family === fam.key); if (!ms.length) continue; md += `\n## ${fam.name} (${EL[fam.element]})\n\n| Identifiant | Monstre | Place |\n|---|---|---|\n` + ms.map((m) => `| \`${m.id}\` | ${m.name} | ${SLOT_FR[m.slot]} |`).join('\n') + '\n'; }
  fs.writeFileSync(path.join(__dirname, 'MONSTRES.md'), md);
  console.log('\n' + list.length + ' monstres exportés');
  await browser.close();
})();
