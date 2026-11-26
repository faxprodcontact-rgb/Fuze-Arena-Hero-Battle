// Captures « Héros et formation » (vague 3, 26/11/2026) : node heros-captures.cjs <dossier> [port]
// (npm run build ; npx vite preview --port 4655 ; puis ce script.) 390×844 avec encoche imitée et 360×640.
// Écrans : heros (onglet Héros), formation (la page de la formation), reglages, avatar (le choix du visage),
// barre (la barre du haut avec le visage choisi), terrain-<élément> (le terrain de la formation, 4 teintes).
// TERRAIN=1 : seulement les terrains.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4655';
fs.mkdirSync(OUT, { recursive: true });
const URL = `http://localhost:${PORT}/?tout=1`;
const KEY = 'hero-battle-v2';

function save(s, cleared) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1', 'mages-3', 'angels-7'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 18, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 60 - i * 3 }));
  s.discovered = [...ids, 'demons-9', 'myths-9', 'assassins-5', 'knights-5'];
  s.nextUid = ids.length + 1;
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
  });
  await page.waitForTimeout(1500);
  return [ctx, page];
}

/** Le bouton qui ouvre la formation : le nouveau bouton, sinon (avant) les héros de la salle. */
const FORMATION = '.hall-formation, .hall-team';

(async () => {
  const browser = await chromium.launch();
  const closeAll = async (page) => { for (let i = 0; i < 4; i++) { const x = await page.$('.modal .x, .page .prep-head .x, .prep .prep-head .x'); if (!x) break; await x.click(); await page.waitForTimeout(250); } };
  for (const [w, h, notch] of process.env.TERRAIN ? [] : SIZES) {
    const tag = `${w}x${h}`;
    const [ctx, page] = await boot(browser, w, h, notch, 23);
    const shot = (n) => page.screenshot({ path: `${OUT}/${n}-${tag}.png` });
    await page.click('.tabbar-btn:nth-child(2)'); await page.waitForTimeout(900); await shot('heros');
    const scroll = await page.evaluate(() => [document.scrollingElement.scrollHeight, innerHeight, document.scrollingElement.scrollWidth, innerWidth]);
    console.log(tag, 'page (haut, écran, large, écran) :', scroll.join(' '));
    await page.click(FORMATION); await page.waitForTimeout(900); await shot('formation');
    await closeAll(page);
    await page.click('.avatar'); await page.waitForTimeout(600); await shot('reglages');
    const pick = await page.$('.avatar-row');
    if (pick) {
      await pick.click(); await page.waitForTimeout(600); await shot('avatar');
      await page.click('.avatar-pick:nth-child(3)'); await page.waitForTimeout(500);
      await closeAll(page);
    } else await closeAll(page);
    await page.waitForTimeout(400);
    await page.screenshot({ path: `${OUT}/barre-${tag}.png`, clip: { x: 0, y: 0, width: w, height: 130 } });
    console.log(tag, 'erreurs :', page.errors.length ? page.errors.slice(0, 5) : 'aucune');
    await ctx.close();
  }
  // le terrain de la formation dans ses 4 teintes (l'élément du chapitre en cours)
  for (const [el, cleared] of [['feu', 0], ['vent', 40], ['eau', 80], ['terre', 120]]) {
    const [ctx, page] = await boot(browser, 390, 844, true, cleared);
    await page.click('.tabbar-btn:nth-child(2)'); await page.waitForTimeout(700);
    await page.click(FORMATION); await page.waitForTimeout(900);
    const box = await page.$('.prep .field');
    await box.screenshot({ path: `${OUT}/terrain-${el}.png` });
    if (page.errors.length) console.log(el, 'erreurs :', page.errors.slice(0, 5));
    await ctx.close();
  }
  await browser.close();
})();
