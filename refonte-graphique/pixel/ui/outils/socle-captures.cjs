// Captures du Socle (style moderne) : node socle-captures.cjs <dossier> [port] [écrans...]
// (npm run build ; npx vite preview --port 4471 ; puis ce script.) 390×844 avec encoche imitée (47 px en haut, 34 en bas),
// 360×640 sans encoche. QUERY='?skin=moderne' pour l'ancien essai (v0.58.2).
// Écrans : accueil bords reglages carte rapide butin connexion quetes passe boutique classement tchat courrier amis prep
// combat victoire defaite
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4471';
const ONLY = process.argv.slice(4);
fs.mkdirSync(OUT, { recursive: true });
const URL = `http://localhost:${PORT}/${process.env.QUERY || ''}`;
const KEY = 'hero-battle-v2';

function save(s, cleared) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 18, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.speed = 3;
  return s;
}

const SIZES = (process.env.SIZES || '390x844n,360x640').split(',').map((x) => {
  const m = x.match(/(\d+)x(\d+)(n?)/); return [+m[1], +m[2], !!m[3]];
});

async function boot(browser, w, h, notch, cleared) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  page.errors = [];
  page.on('pageerror', (e) => page.errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') page.errors.push(m.text()); });
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
  await page.evaluate(([K, f, c]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s, c))); }, [KEY, '(' + save.toString() + ')', cleared]);
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
  await page.waitForTimeout(2500);
  return [ctx, page];
}

(async () => {
  const browser = await chromium.launch();
  for (const [w, h, notch] of SIZES) {
    const tag = `${w}x${h}`;
    const want = (n) => !ONLY.length || ONLY.includes(n);
    const [ctx, page] = await boot(browser, w, h, notch, 23);
    const shot = async (n) => { await page.screenshot({ path: `${OUT}/${n}-${tag}.png` }); };
    const closeAll = async () => { for (let i = 0; i < 4; i++) { const x = await page.$('.modal .x, .page .prep-head .x'); if (!x) break; await x.click(); await page.waitForTimeout(250); } };
    const edge = async (side, i, name) => {
      if (!want(name)) return;
      await page.click(`.edge-${side} .edge-toggle`); await page.waitForTimeout(600);
      await page.click(`.edge-${side} .edge-btn:nth-child(${i})`); await page.waitForTimeout(800); await shot(name); await closeAll();
      await page.click(`.edge-${side} .edge-toggle`); await page.waitForTimeout(400);
    };
    if (want('accueil')) await shot('accueil');
    if (want('bords')) {
      for (const b of await page.$$('.edge-toggle')) await b.click();
      await page.waitForTimeout(700); await shot('bords');
      for (const b of await page.$$('.edge-toggle')) await b.click();
      await page.waitForTimeout(400);
    }
    if (want('reglages')) { await page.click('.avatar'); await page.waitForTimeout(600); await shot('reglages'); await closeAll(); }
    if (want('carte')) { await page.click('.stage-title'); await page.waitForTimeout(800); await shot('carte'); await closeAll(); }
    if (want('rapide')) { await page.click('.dock-fast'); await page.waitForTimeout(600); await shot('rapide'); await closeAll(); }
    if (want('butin')) { await page.click('.dock-chest'); await page.waitForTimeout(900); await shot('butin'); await closeAll(); }
    await edge('left', 1, 'connexion'); await edge('left', 2, 'quetes'); await edge('left', 3, 'passe'); await edge('left', 4, 'boutique');
    await edge('right', 1, 'classement'); await edge('right', 2, 'tchat'); await edge('right', 3, 'courrier'); await edge('right', 4, 'amis');
    if (want('prep') || want('combat') || want('victoire')) {
      await page.click('.dock-fight'); await page.waitForTimeout(1300); await shot('prep');
      if (want('combat') || want('victoire')) {
        await page.click('.prep .btn-fight'); await page.waitForTimeout(4500); await shot('combat');
        if (want('victoire')) {
          await page.waitForSelector('.modal .result-title', { timeout: 120000 }).catch(() => {});
          await page.waitForTimeout(1400); await shot('victoire'); await closeAll();
        }
      }
    }
    console.log(tag, 'erreurs :', page.errors.length ? page.errors.slice(0, 5) : 'aucune');
    await ctx.close();
    if (want('defaite')) {
      const [c2, p2] = await boot(browser, w, h, notch, 150);
      await p2.click('.dock-fight'); await p2.waitForTimeout(1300);
      await p2.click('.prep .btn-fight');
      await p2.waitForSelector('.modal .result-title', { timeout: 120000 }).catch(() => {});
      await p2.waitForTimeout(1400); await p2.screenshot({ path: `${OUT}/defaite-${tag}.png` });
      await c2.close();
    }
  }
  await browser.close();
})();
