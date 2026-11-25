// Essai des habillages (pixel | moderne | hybride) : captures des mêmes écrans dans chaque habillage, 390 × 844 avec encoche
// imitée. npx vite preview --port 4392, puis : node essai-style.cjs <dossier> 4392 [habillages...] (défaut : les trois).
// Les images de chaque habillage vont dans <dossier>/<habillage>/<écran>.png ; essai-style.py les met côte à côte.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4392';
const SKINS = process.argv.slice(4).length ? process.argv.slice(4) : ['pixel', 'moderne', 'hybride'];
const ONLY = (process.env.ONLY || '').split(',').filter(Boolean);
const KEY = 'hero-battle-v2';

function save(s) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 18, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 23, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.speed = 3;
  return s;
}

(async () => {
  const browser = await chromium.launch();
  for (const skin of SKINS) {
    const dir = `${OUT}/${skin}`;
    fs.mkdirSync(dir, { recursive: true });
    const URL = `http://localhost:${PORT}/?skin=${skin}`;
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    await page.route('**/*', async (r) => {
      const u = r.request().url().split('?')[0];
      if (!(u.endsWith('/') || u.endsWith('.css') || u.endsWith('.html'))) return r.fallback();
      const res = await r.fetch();
      let body = await res.text();
      body = body.replace(/env\(safe-area-inset-top(,\s*0px)?\)/g, '47px').replace(/env\(safe-area-inset-bottom(,\s*0px)?\)/g, '34px');
      await r.fulfill({ response: res, body });
    });
    await page.goto(URL);
    await page.waitForSelector('#splash', { state: 'detached', timeout: 20000 });
    await page.waitForTimeout(500);
    const oks = await page.$$('.name-card button'); const ok = oks[oks.length - 1];
    if (ok) { await ok.click(); await page.waitForTimeout(500); }
    await page.evaluate(([K, f]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s))); }, [KEY, '(' + save.toString() + ')']);
    await page.reload();
    await page.waitForSelector('#splash', { state: 'detached', timeout: 20000 });
    await page.evaluate(() => {
      const d = document.createElement('div');
      d.style.cssText = 'position:fixed;z-index:99999;left:50%;top:0;width:126px;height:34px;margin-left:-63px;background:#000;border-radius:0 0 18px 18px;pointer-events:none';
      document.body.appendChild(d);
      const b = document.createElement('div');
      b.style.cssText = 'position:fixed;z-index:99999;left:50%;bottom:8px;width:134px;height:5px;margin-left:-67px;background:#fff;border-radius:3px;pointer-events:none';
      document.body.appendChild(b);
    });
    const want = (n) => !ONLY.length || ONLY.includes(n);
    const shot = async (n) => { await page.screenshot({ path: `${dir}/${n}.png` }); };
    const closeAll = async () => { for (let i = 0; i < 4; i++) { const x = await page.$('.modal .x'); if (!x) break; await x.click(); await page.waitForTimeout(250); } };
    await page.waitForTimeout(2500);
    if (want('accueil')) await shot('accueil');
    if (want('bords')) {
      for (const b of await page.$$('.edge-toggle')) await b.click();
      await page.waitForTimeout(700); await shot('bords');
      for (const b of await page.$$('.edge-toggle')) await b.click();
      await page.waitForTimeout(400);
    }
    if (want('reglages')) { await page.click('.avatar'); await page.waitForTimeout(600); await shot('reglages'); await closeAll(); }
    for (const [n, name] of [[2, 'heros'], [3, 'invoquer'], [4, 'aventure']]) {
      if (!want(name)) continue;
      await page.click(`.tabbar-btn:nth-child(${n})`); await page.waitForTimeout(1300); await shot(name);
    }
    await page.click('.tabbar-btn:nth-child(1)'); await page.waitForTimeout(1500);
    if (want('victoire')) {
      await page.click('.dock-fight'); await page.waitForTimeout(1200);
      await page.click('.prep .btn-fight');
      await page.waitForSelector('.modal .result-title', { timeout: 120000 }).catch(() => {});
      await page.waitForTimeout(1400); await shot('victoire'); await closeAll();
    }
    console.log(skin, 'erreurs :', errors.length ? errors.slice(0, 5) : 'aucune');
    await ctx.close();
  }
  await browser.close();
})();
