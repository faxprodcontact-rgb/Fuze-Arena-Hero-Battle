// Captures du calendrier de connexion et de la boutique : node boutique-captures.cjs <dossier> [port] [écrans...]
// (npm run build ; npx vite preview --port 4622 ; puis ce script, avec NODE_PATH vers playwright.)
// Écrans : jour (bienvenue, jour 3) gros (bienvenue, jour 7) mois (calendrier de 28 jours) reclame (le moment où l'on
// prend : 3 images) offres gemmes passe echange
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4622';
const ONLY = process.argv.slice(4);
fs.mkdirSync(OUT, { recursive: true });
const URL = `http://localhost:${PORT}/${process.env.QUERY || ''}`;
const KEY = 'hero-battle-v2';

function save(s, login) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 18, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5, arenaTokens: 640, guildCoins: 220 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 23, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.login = { day: '2000-1-1', count: login };
  s.shop = { ...s.shop, bought: { growth: 1 }, cardUntil: now + 12.4 * 86400e3 };
  return s;
}

const SIZES = (process.env.SIZES || '390x844n,360x640').split(',').map((x) => {
  const m = x.match(/(\d+)x(\d+)(n?)/); return [+m[1], +m[2], !!m[3]];
});

async function boot(browser, w, h, notch, login) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, reducedMotion: 'no-preference' });
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
  await page.evaluate(([K, f, c]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s, c))); }, [KEY, '(' + save.toString() + ')', login]);
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
  await page.waitForTimeout(1500);
  for (let i = 0; i < 4; i++) { const x = await page.$('.modal .x'); if (!x) break; await x.click(); await page.waitForTimeout(250); }
  return [ctx, page];
}

async function openEdge(page, i) {
  await page.click('.edge-left .edge-toggle'); await page.waitForTimeout(600);
  await page.click(`.edge-left .edge-btn:nth-child(${i})`); await page.waitForTimeout(1200);
}

(async () => {
  const browser = await chromium.launch();
  const want = (n) => !ONLY.length || ONLY.includes(n);
  for (const [w, h, notch] of SIZES) {
    const tag = `${w}x${h}`;
    const errs = [];
    const run = async (name, login, fn) => {
      if (!want(name)) return;
      const [ctx, page] = await boot(browser, w, h, notch, login);
      await fn(page, (n) => page.screenshot({ path: `${OUT}/${n}-${tag}.png` }));
      errs.push(...page.errors);
      await ctx.close();
    };
    await run('jour', 2, async (p, shot) => { await openEdge(p, 1); await shot('jour'); });
    await run('gros', 6, async (p, shot) => { await openEdge(p, 1); await shot('gros'); });
    await run('mois', 7 + 9, async (p, shot) => { await openEdge(p, 1); await shot('mois'); });
    await run('reclame', 3, async (p, shot) => {
      await openEdge(p, 1);
      // une capture prend plus d'une seconde (le combat tourne derrière) : on fige les mouvements à l'instant voulu,
      // et la fenêtre des gains attend la fin des trois images
      await p.evaluate(() => {
        const st = window.setTimeout;
        window.setTimeout = (f, d, ...a) => st(f, d === 1250 ? 8000 : d, ...a);
        // fige les mouvements (sauf ceux déjà finis) au bout de ms millisecondes, dans la page même
        window.__hold = (ms) => new Promise((ok) => st(() => {
          window.__held = document.getAnimations().filter((x) => x.playState === 'running');
          window.__held.forEach((x) => x.pause()); ok();
        }, ms));
        window.__go = () => (window.__held || []).forEach((x) => x.play());
      });
      await p.evaluate(() => { document.querySelector('.modal .lg-claim').click(); return window.__hold(420); });
      await shot('reclame-1');
      await p.evaluate(() => { window.__go(); return window.__hold(450); });
      await shot('reclame-2');
      await p.evaluate(() => window.__go());
      await p.waitForTimeout(8500); await shot('reclame-3');
    });
    await run('offres', 3, async (p, shot) => { await openEdge(p, 4); await shot('offres'); });
    const tab = async (p, i) => { await p.click(`.modal .tabs .tab:nth-child(${i})`); await p.waitForTimeout(900); };
    await run('gemmes', 3, async (p, shot) => { await openEdge(p, 4); await tab(p, 2); await shot('gemmes'); });
    await run('passe', 3, async (p, shot) => { await openEdge(p, 4); await tab(p, 3); await shot('passe'); });
    await run('echange', 3, async (p, shot) => { await openEdge(p, 4); await tab(p, 4); await shot('echange'); });
    await run('achat', 3, async (p, shot) => {
      await openEdge(p, 4);
      await p.click('.modal .bq-feat .bt, .modal .offer .btn'); await p.waitForTimeout(500); await shot('achat');
    });
    console.log(tag, 'erreurs :', errs.length ? errs.slice(0, 5) : 'aucune');
  }
  await browser.close();
})();
