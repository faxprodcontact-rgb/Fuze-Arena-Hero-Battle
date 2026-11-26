// Rend une suite de dessins SVG en PNG (fond transparent), tous à la même taille, dans un seul navigateur (rapide).
//   node rendu-lot.cjs <liste.json>      liste = { "w": 1280, "h": 720, "frames": [["a.svg", "a.png"], …] }
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const job = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: job.w, height: job.h }, deviceScaleFactor: 1 });
  for (const [src, out] of job.frames) {
    const svg = fs.readFileSync(src, 'utf8').replace('<svg ', `<svg width="${job.w}" height="${job.h}" `);
    await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await page.screenshot({ path: out, omitBackground: true, clip: { x: 0, y: 0, width: job.w, height: job.h } });
  }
  await browser.close();
})();
