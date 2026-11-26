// Captures « cartes des héros par rareté » (vague 3, 26/11/2026) : node cartes-captures.cjs <dossier> [port]
// (vite build ; vite preview --port 4688 ; puis ce script.) 390×844 avec encoche imitée et 360×640.
// La sauvegarde : les 36 héros (toutes les raretés), un Légendaire Mythique (11 étoiles), une équipe de 5.
// Écrans : heros (onglet Héros), heros-zoom (le haut de la grille, agrandi), formation, chances, butin (fenêtre de gain).
// GIF=1 : une suite d'images de 4 cartes (Commun, Rare, Épique, Légendaire, Mythique) pour cartes.gif.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4688';
fs.mkdirSync(OUT, { recursive: true });
const URL = `http://localhost:${PORT}/?tout=1`;
const KEY = 'hero-battle-v2';

function save(s) {
  const now = Date.now();
  // un ordre mélangé (les raretés côte à côte dans la grille)
  const ids = ['assassins-2', 'mages-8', 'angels-2', 'knights-8', 'myths-3', 'demons-8', 'knights-5', 'demons-4', 'angels-10',
    'knights-1', 'assassins-7', 'demons-3', 'myths-9', 'mages-2', 'assassins-11', 'angels-7', 'assassins-3', 'mages-3',
    'knights-7', 'knights-3', 'angels-6', 'demons-9', 'demons-5', 'assassins-9', 'mages-11', 'myths-4', 'angels-11',
    'myths-10', 'mages-4', 'knights-9', 'assassins-5', 'demons-12', 'angels-1', 'mages-7', 'myths-6', 'myths-7'];
  const RAR = { 'knights-1': 1, 'knights-3': 1, 'assassins-7': 1, 'assassins-9': 1, 'demons-3': 1, 'angels-7': 1,
    'knights-5': 2, 'knights-7': 2, 'assassins-11': 2, 'demons-4': 2, 'demons-5': 2, 'angels-10': 2, 'angels-11': 2,
    'assassins-2': 4, 'assassins-3': 4, 'assassins-5': 4, 'mages-8': 4, 'mages-11': 4, 'angels-2': 4, 'angels-6': 4, 'myths-9': 4, 'myths-10': 4 };
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 40, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5 };
  s.heroes = ids.map((id, i) => {
    const r = RAR[id] ?? 3;
    const stars = i === 0 ? 11 : i === 1 ? 7 : r === 1 ? 1 + (i % 3) : r === 2 ? 2 + (i % 3) : r === 3 ? 3 + (i % 3) : 4 + (i % 3);
    return { uid: i + 1, defId: id, stars, level: Math.max(1, 120 - i * 3) };
  });
  s.discovered = [...ids];
  s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 60, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.speed = 3;
  return s;
}

const SIZES = (process.env.SIZES || '390x844n,360x640').split(',').map((x) => {
  const m = x.match(/(\d+)x(\d+)(n?)/); return [+m[1], +m[2], !!m[3]];
});

async function boot(browser, w, h, notch, scale = 2) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
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
  await page.evaluate(([K, f]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s))); }, [KEY, '(' + save.toString() + ')']);
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

(async () => {
  const browser = await chromium.launch();
  const closeAll = async (page) => { for (let i = 0; i < 4; i++) { const x = await page.$('.modal .x, .page .prep-head .x, .prep .prep-head .x'); if (!x) break; await x.click(); await page.waitForTimeout(250); } };
  if (process.env.GIF) {
    // 5 cartes côte à côte (Commun, Rare, Épique, Légendaire, Mythique), 30 images toutes les 100 ms
    const [ctx, page] = await boot(browser, 390, 844, false, 2);
    await page.click('.tabbar-btn:nth-child(2)'); await page.waitForTimeout(900);
    await page.evaluate(() => {
      const cards = [...document.querySelectorAll('.grid .hcard-wrap')];
      const pick = (sel) => cards.find((c) => c.querySelector(sel));
      const chosen = [pick('.hcard-common'), pick('.hcard-rare'), pick('.hcard-epic'), pick('.hcard-legendary:not(.hcard-mythic)'), pick('.hcard-mythic')];
      const box = document.createElement('div');
      box.id = 'gifbox';
      box.style.cssText = 'position:fixed;z-index:9999;left:0;top:300px;width:390px;padding:14px 8px;display:grid;grid-template-columns:repeat(5,1fr);gap:7px;background:#160e3a';
      for (const c of chosen) box.appendChild(c.cloneNode(true));
      document.body.appendChild(box);
    });
    await page.waitForTimeout(600);
    const el = await page.$('#gifbox');
    for (let i = 0; i < 40; i++) { await el.screenshot({ path: `${OUT}/f${String(i).padStart(3, '0')}.png` }); await page.waitForTimeout(70); }
    console.log('erreurs :', page.errors.length ? page.errors.slice(0, 5) : 'aucune');
    await ctx.close(); await browser.close(); return;
  }
  for (const [w, h, notch] of SIZES) {
    const tag = `${w}x${h}`;
    const [ctx, page] = await boot(browser, w, h, notch);
    const shot = (n) => page.screenshot({ path: `${OUT}/${n}-${tag}.png` });
    await page.click('.tabbar-btn:nth-child(2)'); await page.waitForTimeout(1200); await shot('heros');
    const g = await page.$('.grid');
    const b = await g.boundingBox();
    await page.screenshot({ path: `${OUT}/heros-zoom-${tag}.png`, clip: { x: b.x, y: b.y, width: b.width, height: Math.min(b.height, 300) } });
    const scroll = await page.evaluate(() => [document.scrollingElement.scrollHeight, innerHeight, document.scrollingElement.scrollWidth, innerWidth]);
    console.log(tag, 'page (haut, écran, large, écran) :', scroll.join(' '));
    await page.click('.hall-formation, .hall-team'); await page.waitForTimeout(1200); await shot('formation');
    await closeAll(page);
    await page.click('.tabbar-btn:nth-child(3)'); await page.waitForTimeout(1200);
    const odds = await page.$$('.sum-round'); await odds[0].click(); await page.waitForTimeout(900); await shot('chances');
    await closeAll(page);
    console.log(tag, 'erreurs :', page.errors.length ? page.errors.slice(0, 5) : 'aucune');
    await ctx.close();
  }
  await browser.close();
})();
