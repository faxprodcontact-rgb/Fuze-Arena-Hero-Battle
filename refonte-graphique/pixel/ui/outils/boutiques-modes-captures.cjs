// Captures des boutiques de la guilde et de l'arène : node boutiques-modes-captures.cjs <dossier> [port] [écrans...]
// (npm run build ; npx vite preview --port 4722 --strictPort ; puis ce script, avec NODE_PATH vers playwright.)
// Écrans : guilde (onglet Boutique de la guilde), arene (onglet Boutique de l'arène), achat-guilde, achat-arene (le moment
// où l'on achète), pauvre (peu de monnaie : objets trop chers). Tailles : SIZES=390x844n,360x640 (n = encoche imitée).
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4722';
const ONLY = process.argv.slice(4);
fs.mkdirSync(OUT, { recursive: true });
const URL = `http://localhost:${PORT}/?tout=1`;
const KEY = 'hero-battle-v2';

function save(s, poor) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 34, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5,
    arenaTokens: poor ? 120 : 1260, guildCoins: poor ? 90 : 640 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 85, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.arena.points = 1340;
  s.guild = { ...s.guild, joined: 'Ordre du Corbeau' };
  s.seen = ['tower', 'missions', 'dungeons', 'dailyBoss', 'arena', 'guild', 'defense'];
  return s;
}

const SIZES = (process.env.SIZES || '390x844n,360x640').split(',').map((x) => {
  const m = x.match(/(\d+)x(\d+)(n?)/); return [+m[1], +m[2], !!m[3]];
});

async function boot(browser, w, h, notch, poor) {
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
  await page.evaluate(([K, f, c]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s, c))); }, [KEY, '(' + save.toString() + ')', poor]);
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

async function guildShop(page) {
  await page.click('.tabbar-btn:nth-child(5)'); await page.waitForTimeout(900);
  await page.click('.g-tabs > button:nth-child(5)'); await page.waitForTimeout(900);
}
async function arenaShop(page) {
  await page.click('.tabbar-btn:nth-child(4)'); await page.waitForTimeout(900);
  await page.click('.tile-arena'); await page.waitForTimeout(800);
  const tabs = await page.$$('.av-seg button'); await tabs[1].click(); await page.waitForTimeout(900);
}
async function overflow(page) {
  return page.evaluate(() => {
    const out = [];
    for (const e of document.querySelectorAll('.adv-scroll, .g-scroll, .mx-list, .content')) {
      const d = e.scrollHeight - e.clientHeight;
      if (d > 2) out.push(`${e.className.split(' ')[0]} +${d}`);
    }
    const doc = document.scrollingElement; if (doc.scrollHeight > innerHeight + 1) out.push(`page +${doc.scrollHeight - innerHeight}`);
    if (doc.scrollWidth > innerWidth + 1) out.push(`largeur +${doc.scrollWidth - innerWidth}`);
    return out;
  });
}

(async () => {
  const browser = await chromium.launch();
  const want = (n) => !ONLY.length || ONLY.includes(n);
  for (const [w, h, notch] of SIZES) {
    const tag = `${w}x${h}`;
    const errs = [];
    const run = async (name, poor, fn) => {
      if (!want(name)) return;
      const [ctx, page] = await boot(browser, w, h, notch, poor);
      await fn(page, async (n) => {
        await page.screenshot({ path: `${OUT}/${n}-${tag}.png` });
        const o = await overflow(page); if (o.length) console.log(`  ${tag} ${n} : défile ${o.join(', ')}`);
      });
      errs.push(...page.errors);
      await ctx.close();
    };
    const buy = async (p, shot, n) => {
      await p.evaluate(() => {
        const st = window.setTimeout;
        window.__hold = (ms) => new Promise((ok) => st(() => {
          window.__held = document.getAnimations().filter((x) => x.playState === 'running');
          window.__held.forEach((x) => x.pause()); ok();
        }, ms));
      });
      await p.evaluate(() => { document.querySelector('.mx-feat .bt, .shop-tile .btn').click(); return window.__hold(380); });
      await shot(n);
      // puis la fenêtre des gains (ouverte quand l'animation est finie)
      await p.evaluate(() => (window.__held || []).forEach((x) => x.play()));
      await p.waitForTimeout(1200); await shot(`${n}-gain`);
    };
    await run('guilde', false, async (p, shot) => { await guildShop(p); await shot('guilde'); });
    await run('arene', false, async (p, shot) => { await arenaShop(p); await shot('arene'); });
    await run('pauvre', true, async (p, shot) => { await guildShop(p); await shot('pauvre-guilde'); await arenaShop(p); await shot('pauvre-arene'); });
    await run('achat-guilde', false, async (p, shot) => { await guildShop(p); await buy(p, shot, 'achat-guilde'); });
    await run('achat-arene', false, async (p, shot) => { await arenaShop(p); await buy(p, shot, 'achat-arene'); });
    console.log(tag, 'erreurs :', errs.length ? errs.slice(0, 5) : 'aucune');
  }
  await browser.close();
})();
