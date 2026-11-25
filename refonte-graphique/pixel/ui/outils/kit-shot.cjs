// node shot.cjs <page.html> <sortie.png> [échelle]
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 452, height: 700 }, deviceScaleFactor: +(process.argv[4] || 2) });
  p.on('pageerror', (e) => console.log('ERR', String(e)));
  await p.goto('file://' + process.argv[2]);
  await p.waitForTimeout(300);
  await p.screenshot({ path: process.argv[3], fullPage: true });
  await b.close();
})();
