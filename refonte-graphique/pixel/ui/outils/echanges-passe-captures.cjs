// Captures des onglets « Échanges » et « Passe » de la boutique : node echanges-passe-captures.cjs <dossier> [port] [écrans...]
// (npm run build ; npx vite preview --port 4744 ; puis ce script, avec NODE_PATH=/opt/node22/lib/node_modules.)
// Écrans : echange (jetons d'arène + pièces de guilde), echange-pauvre (bourses presque vides), achat (le moment de
// l'achat), passe (niveau 12, voie premium à prendre), passe-bas (la fin de la liste, le grand final), passe-premium
// (passe pris, niveau 24)
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4744';
const ONLY = process.argv.slice(4);
fs.mkdirSync(OUT, { recursive: true });
const URL = `http://localhost:${PORT}/${process.env.QUERY || ''}`;
const KEY = 'hero-battle-v2';

function save(s, o) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 18, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5,
    arenaTokens: o.poor ? 60 : 640, guildCoins: o.poor ? 40 : 220 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 23, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.login = { day: '2000-1-1', count: 3 };
  s.shop = { ...s.shop, bought: { growth: 1 }, cardUntil: now + 12.4 * 86400e3, passPremium: !!o.premium };
  s.pass = { ...s.pass, points: o.points ?? 1240, claimedFree: Array.from({ length: 9 }, (_, i) => i),
    claimedPremium: o.premium ? [0, 1, 2, 3, 4, 5] : [] };
  return s;
}

const SIZES = (process.env.SIZES || '390x844n,360x640').split(',').map((x) => {
  const m = x.match(/(\d+)x(\d+)(n?)/); return [+m[1], +m[2], !!m[3]];
});

async function boot(browser, w, h, notch, o) {
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
  await page.evaluate(([K, f, c]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s, c))); }, [KEY, '(' + save.toString() + ')', o]);
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

async function openShop(page, tab) {
  await page.click('.edge-left .edge-toggle'); await page.waitForTimeout(600);
  await page.click('.edge-left .edge-btn:nth-child(4)'); await page.waitForTimeout(1000);
  await page.click(`.modal .tabs .tab:nth-child(${tab})`); await page.waitForTimeout(900);
}

(async () => {
  const browser = await chromium.launch();
  const want = (n) => !ONLY.length || ONLY.includes(n);
  for (const [w, h, notch] of SIZES) {
    const tag = `${w}x${h}`;
    const errs = [];
    const run = async (name, o, fn) => {
      if (!want(name)) return;
      const [ctx, page] = await boot(browser, w, h, notch, o);
      await fn(page, (n) => page.screenshot({ path: `${OUT}/${n}-${tag}.png` }));
      // contrôle : défilement de la page, du corps de la fenêtre, et ce qui dépasse à droite
      const m = await page.evaluate(() => {
        const b = document.querySelector('.modal-body');
        return { page: document.documentElement.scrollHeight - innerHeight, body: b ? b.scrollHeight - b.clientHeight : -1,
          wide: [...document.querySelectorAll('.modal *')].filter((e) => e.getBoundingClientRect().right > innerWidth + 1).length };
      });
      console.log(tag, name, JSON.stringify(m));
      errs.push(...page.errors);
      await ctx.close();
    };
    await run('echange', {}, async (p, shot) => { await openShop(p, 4); await shot('echange'); });
    await run('echange-pauvre', { poor: true }, async (p, shot) => { await openShop(p, 4); await shot('echange-pauvre'); });
    await run('achat', {}, async (p, shot) => {
      await openShop(p, 4);
      // une capture prend du temps (le combat tourne derrière) : on fige les mouvements à l'instant voulu
      await p.evaluate(() => {
        const st = window.setTimeout;
        window.setTimeout = (f, d, ...a) => st(f, d === 720 ? 8000 : d, ...a);
        window.__hold = (ms) => new Promise((ok) => st(() => {
          document.getAnimations().filter((x) => x.playState === 'running').forEach((x) => x.pause()); ok();
        }, ms));
      });
      await p.evaluate(() => { const b = document.querySelector('.modal .mx-top .mx-price:not([disabled])') || document.querySelector('.modal .mx-card .mx-price:not([disabled])');
        if (b) b.click(); return window.__hold(280); });
      await shot('achat');
    });
    await run('passe', {}, async (p, shot) => { await openShop(p, 3); await shot('passe'); });
    await run('passe-bas', {}, async (p, shot) => {
      await openShop(p, 3);
      await p.evaluate(() => { document.querySelectorAll('.modal-body, .ps-list').forEach((e) => { e.scrollTop = 1e5; }); });
      await p.waitForTimeout(500); await shot('passe-bas');
    });
    await run('passe-premium', { premium: true, points: 2460 }, async (p, shot) => { await openShop(p, 3); await shot('passe-premium'); });
    await run('passe-prend', { premium: true, points: 2460 }, async (p, shot) => {
      await openShop(p, 3);
      await p.evaluate(() => {
        const st = window.setTimeout;
        window.setTimeout = (f, d, ...a) => st(f, d === 800 ? 8000 : d, ...a);
        window.__hold = (ms) => new Promise((ok) => st(() => {
          document.getAnimations().filter((x) => x.playState === 'running').forEach((x) => x.pause()); ok();
        }, ms));
      });
      await p.evaluate(() => { const c = document.querySelector('.modal .ps-cell.ps-prem.ps-ready'); if (c) c.click(); return window.__hold(260); });
      await shot('passe-prend');
    });
    console.log(tag, 'erreurs :', errs.length ? errs.slice(0, 5) : 'aucune');
  }
  await browser.close();
})();
