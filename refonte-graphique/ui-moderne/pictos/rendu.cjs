// Rend des dessins SVG en images PNG haute définition, avec le vrai moteur du navigateur (Chromium, par Playwright).
//   node rendu.cjs <page.html> <sortie.png> <largeur> <hauteur>
// La page (écrite par fabrique.py) pose chaque SVG dans sa case ; on photographie toute la page sur fond transparent.
const { chromium } = require('playwright');
(async () => {
  const [html, out, w, h] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  await page.goto('file://' + require('path').resolve(html));
  await page.evaluate(() => Promise.all([...document.images].map((i) => i.decode().catch(() => null))));
  await page.screenshot({ path: out, omitBackground: true, fullPage: false });
  await browser.close();
})();
