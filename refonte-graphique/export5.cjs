// Exporte les personnages v5 en morceaux (une planche PNG par personnage + positions) et le décor,
// pour la page d'aperçu des animations : public/apercu/. À relancer après tout changement de dessin :
//   node refonte-graphique/export5.cjs
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');
const { HEROES, ENEMIES } = require('./cast5.cjs');
const { SHARED_DEFS } = require('./kit.cjs');

const OUT = path.join(__dirname, '..', 'public', 'apercu');
const E = 2;                               // pixels par unité de dessin
const MX = 40, MY = 40, CW = 280, CH = 290; // cadre de rendu d'un morceau (unités), marges comprises

(async () => {
  fs.mkdirSync(path.join(OUT, 'a'), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const data = { E, chars: {} };
  for (const [name, c] of [...Object.entries(HEROES), ...Object.entries(ENEMIES)]) {
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
        cut.push(x1 < 0 ? null : { cv, x0, y0, w: x1 - x0 + 1, h: y1 - y0 + 1 }); // null : morceau vide
      }
      // rangement simple par étagères
      const AW = 1024; let x = 1, y = 1, rowH = 0; const pos = [];
      for (const p of cut) { if (!p) { pos.push(null); continue; } if (x + p.w + 1 > AW) { x = 1; y += rowH + 1; rowH = 0; } pos.push({ x, y }); x += p.w + 1; rowH = Math.max(rowH, p.h); }
      const atlas = document.createElement('canvas'); atlas.width = AW; atlas.height = y + rowH + 1;
      const ag = atlas.getContext('2d');
      cut.forEach((p, i) => p && ag.drawImage(p.cv, p.x0, p.y0, p.w, p.h, pos[i].x, pos[i].y, p.w, p.h));
      return { png: atlas.toDataURL('image/png'), meta: cut.map((p, i) => p && ({ x: pos[i].x, y: pos[i].y, w: p.w, h: p.h, bx: p.x0, by: p.y0 })) };
    }, { svgs, W: CW * E, H: CH * E });
    fs.writeFileSync(path.join(OUT, 'a', name + '.png'), Buffer.from(res.png.split(',')[1], 'base64'));
    // ox, oy : coin du morceau dans le repère du personnage (unités de dessin)
    data.chars[name] = { enemy: name in ENEMIES, rig: c.rig, parts: parts.map((p, i) => res.meta[i] && ({ name: p.name, x: res.meta[i].x, y: res.meta[i].y, w: res.meta[i].w, h: res.meta[i].h, ox: res.meta[i].bx / E - MX, oy: res.meta[i].by / E - MY })).filter(Boolean) };
    console.log(name, parts.length, 'morceaux');
  }
  fs.writeFileSync(path.join(OUT, 'data.js'), '// Fabriqué par refonte-graphique/export5.cjs — ne pas modifier à la main.\nwindow.APERCU = ' + JSON.stringify(data) + ';\n');
  // décor seul
  const tmp = path.join(__dirname, 'tmp-bg.html');
  execFileSync('node', [path.join(__dirname, 'scene5.cjs')], { env: { ...process.env, NOCAST: '1', OUT: tmp }, cwd: __dirname });
  const p2 = await browser.newPage({ viewport: { width: 720, height: 980 }, deviceScaleFactor: 2 });
  await p2.goto('file://' + tmp); await p2.waitForTimeout(500);
  await p2.screenshot({ path: path.join(OUT, 'bg.jpg'), type: 'jpeg', quality: 86 });
  fs.unlinkSync(tmp);
  await browser.close();
})();
