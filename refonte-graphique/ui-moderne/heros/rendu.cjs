// Rend un dessin SVG en PNG (fond transparent), à une hauteur donnée, avec le vrai moteur du navigateur (Chromium).
//   node rendu.cjs <dessin.svg> <sortie.png> <hauteur> [fond CSS]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [src, out, hs, bg] = process.argv.slice(2);
  const svg = fs.readFileSync(src, 'utf8');
  const vb = svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number);
  const h = +hs;
  const w = Math.round((h * vb[2]) / vb[3]);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  const url = 'data:image/svg+xml;base64,' + Buffer.from(svg).toString('base64');
  await page.setContent(`<html><body style="margin:0;background:${bg || 'transparent'}"><img src="${url}" style="display:block;width:${w}px;height:${h}px"></body></html>`);
  await page.evaluate(() => Promise.all([...document.images].map((i) => i.decode().catch(() => null))));
  await page.screenshot({ path: out, omitBackground: !bg, fullPage: false });
  await browser.close();
})();
