// Captures des fonds des menus (onglets Héros, Invoquer, Aventure, Guilde ; une page : le courrier).
// npm run build ; npx vite preview --port 4593 --strictPort ; puis : node fonds-captures.cjs <dossier> [port] [écrans...]
// 390×844 avec encoche imitée (47 px en haut, 34 en bas) et 360×640 : <dossier>/<écran>-<taille>.png
// Vérifie aussi : aucune erreur dans la console, pas de défilement de la page. REDUCED=1 : mouvements réduits.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4593';
const ONLY = process.argv.slice(4);
fs.mkdirSync(OUT, { recursive: true });
const URL = `http://localhost:${PORT}/`;
const KEY = 'hero-battle-v2';

function save(s) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1', 'mages-3', 'demons-9'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 34, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 120, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.seen = ['tower', 'missions', 'dungeons', 'dailyBoss', 'arena', 'guild', 'defense'];
  s.speed = 3;
  return s;
}

const SIZES = (process.env.SIZES || '390x844n,360x640').split(',').map((x) => { const m = x.match(/(\d+)x(\d+)(n?)/); return [+m[1], +m[2], !!m[3]]; });

(async () => {
  const browser = await chromium.launch();
  for (const [w, h, notch] of SIZES) {
    const tag = `${w}x${h}`;
    const want = (n) => !ONLY.length || ONLY.includes(n);
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, reducedMotion: process.env.REDUCED ? 'reduce' : 'no-preference' });
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
    await page.waitForTimeout(1500);
    const scroll = async (n) => { const s = await page.evaluate(() => [document.documentElement.scrollHeight - innerHeight, document.documentElement.scrollWidth - innerWidth]); if (s[0] > 0 || s[1] > 0) console.log(tag, n, 'défilement de la page :', s); };
    const shot = async (n) => { await scroll(n); await page.screenshot({ path: `${OUT}/${n}-${tag}.png` }); };
    const tab = async (i) => { await page.click(`.tabbar-btn:nth-child(${i})`); await page.waitForTimeout(1400); };
    const back = async () => { await page.click('.prep .prep-head .x, .page .prep-head .x, .hx-act-back').catch(() => {}); await page.waitForTimeout(400); };
    if (want('heros')) { await tab(2); await shot('heros'); }
    if (want('equipe')) { await tab(2); await page.click('.hall-team'); await page.waitForTimeout(1300); await shot('equipe'); await back(); }
    if (want('fiche')) { await tab(2); await page.click('.hall-scroll .hcard'); await page.waitForTimeout(1300); await shot('fiche'); await back(); }
    if (want('prep')) { await tab(1); await page.click('.dock-fight'); await page.waitForTimeout(1300); await shot('prep'); await back(); }
    if (want('invoquer')) { await tab(3); await shot('invoquer'); }
    if (want('aventure')) { await tab(4); await shot('aventure'); }
    if (want('guilde')) { await tab(5); await shot('guilde'); }
    if (want('page')) {
      await tab(1);
      await page.click('.edge-right .edge-toggle'); await page.waitForTimeout(600);
      await page.click('.edge-right .edge-btn:nth-child(3)'); await page.waitForTimeout(1000); await shot('page');
      await page.click('.page .prep-head .x').catch(() => {}); await page.waitForTimeout(300);
    }
    console.log(tag, 'erreurs :', errors.length ? errors.slice(0, 5) : 'aucune');
    await ctx.close();
  }
  await browser.close();
})();
