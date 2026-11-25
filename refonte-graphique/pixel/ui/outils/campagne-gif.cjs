// Petit film de l'accueil (390 × 844, encoche imitée) : node gif.cjs <dossier des images>
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
fs.mkdirSync(OUT, { recursive: true });
const KEY = 'hero-battle-v2';
function save(s) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 18, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 23, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  return s;
}
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  await page.route('**/*', async (r) => {
    const u = r.request().url().split('?')[0];
    if (!(u.endsWith('/') || u.endsWith('.css') || u.endsWith('.html'))) return r.fallback();
    const res = await r.fetch();
    const body = (await res.text()).replace(/env\(safe-area-inset-top(,\s*0px)?\)/g, '47px').replace(/env\(safe-area-inset-bottom(,\s*0px)?\)/g, '34px');
    await r.fulfill({ response: res, body });
  });
  await page.goto('http://localhost:4391/');
  await page.waitForSelector('#splash', { state: 'detached', timeout: 20000 });
  const oks = await page.$$('.name-card button'); const ok = oks[oks.length - 1];
  if (ok) { await ok.click(); await page.waitForTimeout(400); }
  await page.evaluate(([K, f]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s))); }, [KEY, '(' + save.toString() + ')']);
  await page.reload();
  await page.waitForSelector('#splash', { state: 'detached', timeout: 20000 });
  await page.evaluate(() => {
    const d = document.createElement('div');
    d.style.cssText = 'position:fixed;z-index:99999;left:50%;top:0;width:126px;height:34px;margin-left:-63px;background:#000;border-radius:0 0 18px 18px;pointer-events:none';
    document.body.appendChild(d);
  });
  await page.waitForTimeout(2000);
  let i = 0;
  const snap = async (n = 1, gap = 110) => { for (let k = 0; k < n; k++) { await page.screenshot({ path: `${OUT}/f${String(i++).padStart(3, '0')}.png` }); await page.waitForTimeout(gap); } };
  await snap(8);
  for (const b of await page.$$('.edge-toggle')) await b.click();
  await snap(12);
  for (const b of await page.$$('.edge-toggle')) await b.click();
  await snap(6);
  await page.hover('.dock-fight'); await page.mouse.down(); await snap(2); await page.mouse.up();
  await page.waitForTimeout(200);
  await snap(10);
  await page.click('.prep .btn-fight'); await page.waitForTimeout(1500);
  await snap(16, 140);
  await browser.close();
})();
