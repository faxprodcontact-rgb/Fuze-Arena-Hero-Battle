// Captures et films de l'onglet Invoquer et du tirage (style moderne), encoche imitée.
// npx vite preview --port 4393, puis : node invoquer.cjs <dossier> 4393 [captures|films]
// - captures : l'onglet (normal, simple), le tirage ×1 et ×10 à plusieurs moments, en 390 × 844 et 360 × 640 ;
// - films : invoquer-x1.webm / invoquer-x10.webm (Légendaire forcé par la jauge : pity = 39), à passer en GIF par ffmpeg.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4393';
const MODE = process.argv[4] || 'captures';
const KEY = 'hero-battle-v2';
fs.mkdirSync(OUT, { recursive: true });

function save(s) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 18, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 23500, scrolls: 42, basicScrolls: 15 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 23, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.summon = { ...s.summon, pity: 39 };
  s.fragments = { 'angels-2': 30 };
  return s;
}

async function setup(browser, w, h, dsf, video) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: dsf, ...(video ? { recordVideo: { dir: OUT, size: { width: w, height: h } } } : {}) });
  const page = await ctx.newPage();
  const t0 = Date.now();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  const notch = h >= 800;
  await page.route('**/*', async (r) => {
    const u = r.request().url().split('?')[0];
    if (!(u.endsWith('/') || u.endsWith('.css') || u.endsWith('.html'))) return r.fallback();
    const res = await r.fetch();
    let body = await res.text();
    if (notch) body = body.replace(/env\(safe-area-inset-top(,\s*0px)?\)/g, '47px').replace(/env\(safe-area-inset-bottom(,\s*0px)?\)/g, '34px');
    await r.fulfill({ response: res, body });
  });
  await page.goto(`http://localhost:${PORT}/?skin=moderne`);
  await page.waitForSelector('#splash', { state: 'detached', timeout: 20000 });
  await page.waitForTimeout(400);
  const oks = await page.$$('.name-card button'); const ok = oks[oks.length - 1];
  if (ok) { await ok.click(); await page.waitForTimeout(400); }
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
  await page.waitForTimeout(1200);
  await page.click('.tabbar-btn:nth-child(3)');
  await page.waitForTimeout(1200);
  return { ctx, page, errors, t0 };
}

(async () => {
  const browser = await chromium.launch();
  if (MODE === 'captures') {
    for (const [w, h] of [[390, 844], [360, 640]]) {
      const tag = `${w}x${h}`;
      const { ctx, page, errors } = await setup(browser, w, h, 2, false);
      const shot = (n) => page.screenshot({ path: `${OUT}/${n}-${tag}.png` });
      await shot('onglet');
      await page.click('.sum-kind-tab-basic'); await page.waitForTimeout(700); await shot('onglet-simple');
      await page.click('.sum-kind-tab-normal'); await page.waitForTimeout(500);
      // ×1 (Légendaire garanti par la jauge)
      await page.click('.sum-btn-1');
      await page.waitForTimeout(1000); await shot('x1-a-charge');
      await page.waitForTimeout(1500); await shot('x1-b-sortie');
      await page.waitForTimeout(1500); await shot('x1-c-fin');
      await page.click('.reveal-ok'); await page.waitForTimeout(600);
      // ×10
      await page.click('.sum-btn-10');
      await page.waitForTimeout(1900); await shot('x10-a-premier');
      await page.waitForTimeout(1600); await shot('x10-b-suite');
      await page.click('.sr-skip'); await page.waitForTimeout(1200); await shot('x10-c-recap');
      await page.click('.sr-cell'); await page.waitForTimeout(900); await shot('x10-d-zoom');
      console.log(tag, 'erreurs :', errors.length ? errors.slice(0, 5) : 'aucune');
      await ctx.close();
    }
  } else {
    for (const [name, sel, wait, extra] of [['x1', '.sum-btn-1', 4600, null], ['x10', '.sum-btn-10', 17000, true]]) {
      const { ctx, page, t0 } = await setup(browser, 390, 844, 1, true);
      await page.waitForTimeout(300);
      await page.click(sel);
      fs.writeFileSync(`${OUT}/invoquer-${name}.debut`, String((Date.now() - t0 - 400) / 1000));
      await page.waitForTimeout(wait);
      if (extra) { await page.click('.sr-cell:nth-child(1)'); await page.waitForTimeout(1800); await page.mouse.click(195, 400); await page.waitForTimeout(800); }
      const v = page.video();
      await ctx.close();
      fs.renameSync(await v.path(), `${OUT}/invoquer-${name}.webm`);
    }
  }
  await browser.close();
})();
