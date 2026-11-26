// Captures de l'essai « héros vectoriel » (Célia) dans le vrai jeu, pixel art (?vecto=0) contre vectoriel (?vecto=1),
// en 390 × 844 avec encoche imitée : tirage devant le portail, page du héros, cartes de l'onglet Héros (+ la salle).
//   npm run build ; npx vite preview --port 4822 --strictPort ; node captures.cjs <dossier> [port]
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4846';
const KEY = 'hero-battle-v2';
fs.mkdirSync(OUT, { recursive: true });

// La sauvegarde de test : Célia en tête ; la jauge du tirage à 39 et le hasard calé pour que le prochain tirage ×1
// donne Kael (graine trouvée en rejouant summonOne : s.rng = 10, createdAt fixe).
function save(s) {
  const now = Date.now();
  const ids = ['sorai', 'angels-1', 'angels-6', 'knights-8', 'mages-8', 'angels-2', 'myths-3', 'demons-4', 'knights-1', 'mages-3'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 18, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 23500, scrolls: 42, basicScrolls: 15 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 23, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.summon = { ...s.summon, pity: 39 };
  s.createdAt = 1700000000000; s.rng = 10;
  return s;
}

async function boot(browser, query) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  page.errors = [];
  page.on('pageerror', (e) => page.errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') page.errors.push(m.text()); });
  await page.route('**/*', async (r) => {
    const u = r.request().url().split('?')[0];
    if (!(u.endsWith('/') || u.endsWith('.css') || u.endsWith('.html'))) return r.fallback();
    const res = await r.fetch();
    let body = await res.text();
    body = body.replace(/env\(safe-area-inset-top(,\s*0px)?\)/g, '47px').replace(/env\(safe-area-inset-bottom(,\s*0px)?\)/g, '34px');
    await r.fulfill({ response: res, body });
  });
  const url = `http://localhost:${PORT}/${query}`;
  await page.goto(url);
  await page.waitForSelector('#splash', { state: 'detached', timeout: 20000 });
  await page.waitForTimeout(500);
  const oks = await page.$$('.name-card button'); const ok = oks[oks.length - 1];
  if (ok) { await ok.click(); await page.waitForTimeout(500); }
  await page.evaluate(([K, f]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s))); }, [KEY, '(' + save.toString() + ')']);
  await page.goto(url);
  await page.waitForSelector('#splash', { state: 'detached', timeout: 20000 });
  await page.evaluate(() => {
    const d = document.createElement('div');
    d.style.cssText = 'position:fixed;z-index:99999;left:50%;top:0;width:126px;height:34px;margin-left:-63px;background:#000;border-radius:0 0 18px 18px;pointer-events:none';
    document.body.appendChild(d);
    const b = document.createElement('div');
    b.style.cssText = 'position:fixed;z-index:99999;left:50%;bottom:8px;width:134px;height:5px;margin-left:-67px;background:#fff;border-radius:3px;pointer-events:none';
    document.body.appendChild(b);
  });
  await page.waitForTimeout(1500);
  // fermer ce qui s'ouvre tout seul (connexion du jour, courrier…)
  for (let i = 0; i < 4; i++) { const x = await page.$('.modal .x'); if (!x) break; await x.click(); await page.waitForTimeout(300); }
  return [ctx, page];
}

(async () => {
  const browser = await chromium.launch();
  for (const [tag, query] of [['pixel', '?vecto=0'], ['vecto', '?vecto=1']]) {
    const [ctx, page] = await boot(browser, query);
    const shot = (n) => page.screenshot({ path: `${OUT}/${n}-${tag}.png` });
    // l'onglet Héros : la salle et les cartes
    await page.click('.tabbar-btn:nth-child(2)'); await page.waitForTimeout(1200); await shot('salle');
    const card = await page.$('.hcard');
    if (card) {
      await card.scrollIntoViewIfNeeded(); await page.waitForTimeout(500); await shot('cartes');
      await card.click(); await page.waitForTimeout(1500); await shot('fiche');
      for (let i = 0; i < 3; i++) { const x = await page.$('.hx-act-back, .modal .x'); if (!x) break; await x.click(); await page.waitForTimeout(400); }
    }
    await ctx.close();
  }
  await browser.close();
})();
