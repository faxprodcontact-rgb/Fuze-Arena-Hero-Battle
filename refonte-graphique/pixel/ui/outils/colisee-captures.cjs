// Captures du Colisée : node colisee-captures.cjs <dossier> [port] [gif]
// (npm run build ; npx vite preview --port 4733 ; puis ce script, avec NODE_PATH vers playwright.)
// 390×844 avec encoche imitée (47 px en haut, 34 en bas) et 360×640. « gif » : images d'un combat dans <dossier>/gif/.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4733';
const GIF = process.argv[4] === 'gif';
fs.mkdirSync(OUT, { recursive: true });
const URL = `http://localhost:${PORT}/?tout=1`;
const KEY = 'hero-battle-v2';

function save(s, extra) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1', 'mages-3', 'demons-5'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = extra.lang || 'fr';
  s.account = { level: 48, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5, badge: 940 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 100 - i * 4 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 420, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.seen = ['tower', 'missions', 'dungeons', 'dailyBoss', 'arena', 'guild', 'defense'];
  s.speed = extra.speed || 2;
  if (extra.coliseum) s.coliseum = { ...s.coliseum, ...extra.coliseum };
  return s;
}

const SIZES = GIF ? [[390, 844, true]] : [[390, 844, true], [360, 640, false]];

let bornAt = 0;
async function boot(browser, w, h, notch, extra = {}) {
  bornAt = Date.now();
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: GIF ? 1 : 2, ...(GIF ? { recordVideo: { dir: `${OUT}/video`, size: { width: w, height: h } } } : {}) });
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
  const apply = async (x) => {
    await page.evaluate(([K, f, c]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s, c))); }, [KEY, '(' + save.toString() + ')', x]);
    await page.reload();
    await page.waitForSelector('#splash', { state: 'detached', timeout: 20000 });
  };
  await apply(extra);
  // le Colisée est créé à l'ouverture : la sauvegarde a maintenant son groupe de la semaine
  if (extra.after) { await page.waitForTimeout(800); await apply({ ...extra, coliseum: extra.after }); }
  if (notch) await page.evaluate(() => {
    const d = document.createElement('div');
    d.style.cssText = 'position:fixed;z-index:99999;left:50%;top:0;width:126px;height:34px;margin-left:-63px;background:#000;border-radius:0 0 18px 18px;pointer-events:none';
    document.body.appendChild(d);
    const b = document.createElement('div');
    b.style.cssText = 'position:fixed;z-index:99999;left:50%;bottom:8px;width:134px;height:5px;margin-left:-67px;background:#fff;border-radius:3px;pointer-events:none';
    document.body.appendChild(b);
  });
  await page.waitForTimeout(1500);
  return [ctx, page];
}

async function openColisee(page) {
  await page.click('.tabbar-btn:nth-child(4)');
  await page.waitForTimeout(700);
  await page.click('.av-tile.tile-defense');
  await page.waitForTimeout(900);
}

(async () => {
  const browser = await chromium.launch();
  for (const [w, h, notch] of SIZES) {
    const tag = `${w}x${h}`;
    const [ctx, page] = await boot(browser, w, h, notch, GIF ? { speed: 3 } : {});
    const shot = async (n) => { await page.screenshot({ path: `${OUT}/${n}-${tag}.png` }); };
    const check = async (n) => {
      const r = await page.evaluate(() => {
        const sc = document.scrollingElement;
        const over = [...document.querySelectorAll('.app *')].filter((e) => { const b = e.getBoundingClientRect(); return b.width && (b.right > innerWidth + 1 || b.left < -1) && !e.closest('svg'); }).slice(0, 4).map((e) => e.tagName + '.' + e.className);
        return { pageScroll: sc.scrollHeight > innerHeight + 1, over };
      });
      if (r.pageScroll || r.over.length) console.log(tag, n, JSON.stringify(r));
    };
    if (GIF) {
      await openColisee(page);
      await page.click('.col-go .btn');
      await page.waitForTimeout(800);
      await page.click('.modal .btn-fight');
      fs.mkdirSync(`${OUT}/video`, { recursive: true });
      fs.writeFileSync(`${OUT}/video/start.txt`, String((Date.now() - bornAt) / 1000 + 2.2));
      // le combat est filmé (vidéo de playwright), colisee-apercu.py en fait le GIF
      for (let i = 0; i < 240 && !(await page.$('.col-delta')); i++) await page.waitForTimeout(500);
      await page.waitForTimeout(1500);
      await ctx.close();
      console.log('vidéo', fs.readdirSync(`${OUT}/video`));
      continue;
    }
    await page.click('.tabbar-btn:nth-child(4)');
    await page.waitForTimeout(800);
    await shot('aventure');
    await page.click('.av-tile.tile-defense');
    await page.waitForTimeout(900);
    await shot('colisee'); await check('colisee');
    await page.click('.col-tabs button:nth-child(2)'); await page.waitForTimeout(400);
    await shot('recompenses'); await check('recompenses');
    await page.click('.col-tabs button:nth-child(3)'); await page.waitForTimeout(400);
    await shot('boutique'); await check('boutique');
    await page.click('.col-tabs button:nth-child(1)'); await page.waitForTimeout(300);
    await page.click('.col-team'); await page.waitForTimeout(600);
    await shot('equipe'); await check('equipe');
    await page.click('.modal .x'); await page.waitForTimeout(400);
    await page.click('.col-go .btn'); await page.waitForTimeout(800);
    await shot('adversaire'); await check('adversaire');
    await page.click('.modal .btn-fight');
    await page.waitForTimeout(2600); await shot('combat-1');
    await page.waitForTimeout(5000); await shot('combat-2');
    for (let i = 0; i < 240 && !(await page.$('.col-delta')); i++) await page.waitForTimeout(500);
    await page.waitForTimeout(600);
    await shot('resultat'); await check('resultat');
    await page.click('.modal .btn'); await page.waitForTimeout(500);
    await shot('apres');
    console.log(tag, 'erreurs', page.errors.length ? page.errors : 'aucune');
    await ctx.close();
    // la fin de semaine : premier, il monte en Argent
    const [ctx2, page2] = await boot(browser, w, h, notch, { after: { pending: { week: 'x', league: 0, rank: 1, next: 1, gems: 300, badge: 600 }, league: 1 } });
    await openColisee(page2);
    await page2.waitForTimeout(800);
    await page2.screenshot({ path: `${OUT}/semaine-${tag}.png` });
    console.log(tag, 'erreurs semaine', page2.errors.length ? page2.errors : 'aucune');
    await ctx2.close();
  }
  await browser.close();
})();
