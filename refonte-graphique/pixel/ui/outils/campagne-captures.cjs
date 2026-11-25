// Captures de la partie Campagne : node tour.cjs <dossier> [port] [écrans...]
// 390×844 avec encoche imitée (47 px en haut, 34 en bas), 360×640 sans encoche.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2]; // (npx vite preview --port 4391, puis NODE_PATH=$(npm root -g) node campagne-captures.cjs <dossier> 4391 [écrans : accueil bords reglages carte rapide butin divers onglets prep combat victoire])
const PORT = process.argv[3] || '4391';
const ONLY = process.argv.slice(4);
fs.mkdirSync(OUT, { recursive: true });
const URL = `http://localhost:${PORT}/`;
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

const SIZES = (process.env.SIZES || '390x844n,360x640').split(',').map((x) => {
  const m = x.match(/(\d+)x(\d+)(n?)/); return [+m[1], +m[2], !!m[3]];
});

(async () => {
  const browser = await chromium.launch();
  for (const [w, h, notch] of SIZES) {
    const tag = `${w}x${h}`;
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2 });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    if (notch) {
      await page.route('**/*', async (r) => {
        const u = r.request().url().split('?')[0];
        if (!(u.endsWith('/') || u.endsWith('.css') || u.endsWith('.html'))) return r.fallback();
        const res = await r.fetch();
        let body = await res.text();
        body = body.replace(/env\(safe-area-inset-top(,\s*0px)?\)/g, '47px').replace(/env\(safe-area-inset-bottom(,\s*0px)?\)/g, '34px');
        await r.fulfill({ response: res, body });
      });
    }
    await page.goto(URL);
    await page.waitForSelector('#splash', { state: 'detached', timeout: 20000 });
    await page.waitForTimeout(500);
    const oks = await page.$$('.name-card button'); const ok = oks[oks.length - 1];
    if (ok) { await ok.click(); await page.waitForTimeout(500); }
    await page.evaluate(([K, f]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s))); }, [KEY, '(' + save.toString() + ')']);
    await page.reload();
    await page.waitForSelector('#splash', { state: 'detached', timeout: 20000 });
    if (notch) await page.evaluate(() => {
      const d = document.createElement('div');
      d.style.cssText = 'position:fixed;z-index:99999;left:50%;top:0;width:126px;height:34px;margin-left:-63px;background:#000;border-radius:0 0 18px 18px;pointer-events:none';
      document.body.appendChild(d);
      const b = document.createElement('div');
      b.style.cssText = 'position:fixed;z-index:99999;left:50%;bottom:8px;width:134px;height:5px;margin-left:-67px;background:#fff;border-radius:3px;pointer-events:none';
      document.body.appendChild(b);
    });
    const want = (n) => !ONLY.length || ONLY.includes(n);
    const shot = async (n) => { await page.screenshot({ path: `${OUT}/${n}-${tag}.png` }); };
    const closeAll = async () => { for (let i = 0; i < 4; i++) { const x = await page.$('.modal .x'); if (!x) break; await x.click(); await page.waitForTimeout(250); } };
    await page.waitForTimeout(2500);
    if (want('accueil')) await shot('accueil');
    if (want('bords')) {
      for (const b of await page.$$('.edge-toggle')) await b.click();
      await page.waitForTimeout(700); await shot('bords');
      for (const b of await page.$$('.edge-toggle')) await b.click();
      await page.waitForTimeout(400);
    }
    if (want('reglages')) { await page.click('.avatar'); await page.waitForTimeout(500); await shot('reglages'); await closeAll(); }
    if (want('carte')) { await page.click('.stage-title'); await page.waitForTimeout(700); await shot('carte'); await closeAll(); }
    if (want('rapide')) { await page.click('.dock-fast'); await page.waitForTimeout(500); await shot('rapide'); await closeAll(); }
    if (want('butin')) { await page.click('.dock-chest'); await page.waitForTimeout(800); await shot('butin'); await closeAll(); }
    if (want('divers')) {
      await page.click('.edge-left .edge-toggle'); await page.waitForTimeout(600);
      await page.click('.edge-left .edge-btn:nth-child(2)'); await page.waitForTimeout(700); await shot('quetes'); await closeAll();
      await page.click('.edge-left .edge-btn:nth-child(4)'); await page.waitForTimeout(700); await shot('boutique'); await closeAll();
      await page.click('.edge-left .edge-btn:nth-child(1)'); await page.waitForTimeout(700); await shot('connexion'); await closeAll();
      await page.click('.edge-left .edge-toggle'); await page.waitForTimeout(400);
      await page.click('.tabbar-btn:nth-child(2)'); await page.waitForTimeout(1000);
      await page.click('.grid .hcard'); await page.waitForTimeout(1200); await shot('fiche');
      const b = await page.$('.hp-back'); if (b) await b.click(); await page.waitForTimeout(400);
      await page.click('.tabbar-btn:nth-child(1)'); await page.waitForTimeout(1500);
    }
    if (want('onglets')) {
      for (const [n, name] of [[2, 'heros'], [3, 'invoquer'], [4, 'aventure'], [5, 'guilde']]) {
        await page.click(`.tabbar-btn:nth-child(${n})`); await page.waitForTimeout(1200); await shot(`onglet-${name}`);
      }
      await page.click('.tabbar-btn:nth-child(1)'); await page.waitForTimeout(1500);
    }
    if (want('prep') || want('combat') || want('victoire')) {
      await page.click('.dock-fight'); await page.waitForTimeout(1200); await shot('prep');
      if (want('combat') || want('victoire')) {
        await page.click('.prep .btn-fight'); await page.waitForTimeout(4500); await shot('combat');
        if (want('victoire')) {
          await page.waitForSelector('.modal .result-title', { timeout: 90000 }).catch(() => {});
          await page.waitForTimeout(1200); await shot('victoire'); await closeAll();
        }
      }
    }
    console.log(tag, 'erreurs :', errors.length ? errors.slice(0, 5) : 'aucune');
    await ctx.close();
  }
  await browser.close();
})();
