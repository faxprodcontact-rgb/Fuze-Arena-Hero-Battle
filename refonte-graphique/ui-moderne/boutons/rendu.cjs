// Rend la proposition de boutons : planche des familles et maquettes d'écrans (390 × 844, ×2).
//   node refonte-graphique/ui-moderne/boutons/rendu.cjs [dossier de sortie]
// → familles.png ; <famille>-accueil.png et <famille>-invoquer.png (fonds : fonds/*.jpg, refaits par fonds.cjs)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const OUT = process.argv[2] || path.join(__dirname, '../../pixel/sortie/ui/moderne/boutons');
const ONLY = (process.env.ONLY || '').split(',').filter(Boolean);
const PAGE = 'file://' + path.join(__dirname, 'proposition.html');
const FAMS = ['email', 'pierre', 'cristal', 'etendard'];
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1700, height: 1200 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  const go = async (q) => { await page.goto(`${PAGE}?${q}`); await page.evaluate(() => document.fonts.ready); await page.waitForTimeout(300); };
  if (!ONLY.length || ONLY.includes('planche')) {
    await go('vue=planche');
    await (await page.$('.board')).screenshot({ path: `${OUT}/familles.png` });
  }
  for (const f of FAMS) {
    if (ONLY.length && !ONLY.includes(f)) continue;
    for (const v of ['accueil', 'invoquer']) {
      await go(`vue=${v}&f=${f}`);
      await (await page.$('.phone')).screenshot({ path: `${OUT}/${f}-${v}.png` });
    }
  }
  console.log('erreurs :', errors.length ? errors.slice(0, 5) : 'aucune');
  await browser.close();
})();
