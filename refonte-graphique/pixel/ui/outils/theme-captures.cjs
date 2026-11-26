// Captures pour comparer deux habillages (essai « pierre », 26/11) : node theme-captures.cjs <dossier> [port] [écrans…]
// QUERY='?theme=pierre' (ou '?theme=nuit') ; SIZES='390x844n,360x640'. (npm run build ; npx vite preview --port 4799
// --strictPort ; puis ce script.) <dossier>/<écran>-<taille>.png ; signale erreurs, défilement, boutons hors écran.
// Écrans : accueil dock heros heros-fiche invoquer aventure guilde quetes boutique prep combat
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4799';
const ONLY = process.argv.slice(4);
fs.mkdirSync(OUT, { recursive: true });
const KEY = 'hero-battle-v2';
const Q = process.env.QUERY || '';

function save(s, cleared) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1', 'mages-3', 'demons-9'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 34, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5, arenaTokens: 350 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.tower = { floor: 17 };
  s.seen = ['tower', 'missions', 'dungeons', 'dailyBoss', 'arena', 'guild', 'defense'];
  s.speed = 3; s.auto = false;
  return s;
}

const SIZES = (process.env.SIZES || '390x844n').split(',').map((x) => {
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
  await page.goto(`http://localhost:${PORT}/${Q}`);
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

function audit() {
  const out = [];
  const de = document.documentElement;
  if (de.scrollHeight > innerHeight + 1 || de.scrollWidth > innerWidth + 1) out.push(`page ${de.scrollWidth}x${de.scrollHeight}`);
  for (const e of document.querySelectorAll('.modal-body, .page-body')) if (e.scrollHeight - e.clientHeight > 2) out.push(`${e.className} défile de ${e.scrollHeight - e.clientHeight}px`);
  for (const b of document.querySelectorAll('button, .btn')) {
    const r = b.getBoundingClientRect();
    if (!r.width || getComputedStyle(b).visibility === 'hidden') continue;
    if (r.right > innerWidth + 1 || r.left < -1) out.push(`bouton hors écran : ${b.className} (${Math.round(r.left)}→${Math.round(r.right)})`);
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  for (const [w, h, notch] of SIZES) {
    const tag = `${w}x${h}`;
    const want = (n) => !ONLY.length || ONLY.includes(n);
    const [ctx, page] = await boot(browser, w, h, notch, 120);
    const shot = async (n) => {
      await page.waitForTimeout(700);
      await page.screenshot({ path: `${OUT}/${n}-${tag}.png` });
      const a = await page.evaluate(audit);
      if (a.length) console.log(`  ${tag} ${n} :`, [...new Set(a)].slice(0, 6).join(' | '));
    };
    const closeAll = async () => { for (let i = 0; i < 4; i++) { const x = await page.$('.modal .x, .page .prep-head .x, .hx-act-back'); if (!x) break; await x.click(); await page.waitForTimeout(250); } };
    const tab = async (i) => { await page.click(`.tabbar-btn:nth-child(${i})`); await page.waitForTimeout(1000); };
    if (want('accueil')) await shot('accueil');
    if (want('dock')) {
      // le bas de l'accueil, en grand (×2) : de 40 px au-dessus du dock jusqu'en bas de l'écran
      await page.waitForTimeout(700);
      const r = await page.evaluate(() => { const d = document.querySelector('.dock').getBoundingClientRect(); return d.top; });
      const y = Math.max(0, r - 40);
      await page.screenshot({ path: `${OUT}/dock-${tag}.png`, clip: { x: 0, y, width: w, height: h - y } });
    }
    if (want('quetes')) {
      await page.click('.edge-left .edge-toggle'); await page.waitForTimeout(600);
      await page.click('.edge-left .edge-btn:nth-child(2)'); await shot('quetes'); await closeAll();
      await page.click('.edge-left .edge-toggle'); await page.waitForTimeout(400);
    }
    if (want('boutique')) {
      await page.click('.edge-left .edge-toggle'); await page.waitForTimeout(600);
      await page.click('.edge-left .edge-btn:nth-child(4)'); await shot('boutique'); await closeAll();
      await page.click('.edge-left .edge-toggle'); await page.waitForTimeout(400);
    }
    if (want('heros') || want('heros-fiche')) {
      await tab(2); if (want('heros')) await shot('heros');
      if (want('heros-fiche')) { await page.click('.grid .hcard'); await shot('heros-fiche'); await closeAll(); }
    }
    if (want('invoquer')) { await tab(3); await shot('invoquer'); }
    if (want('aventure')) { await tab(4); await shot('aventure'); }
    if (want('guilde')) { await tab(5); await shot('guilde'); }
    if (want('prep') || want('combat')) {
      await tab(1);
      await page.click('.dock-fight'); await page.waitForTimeout(800); await shot('prep');
      if (want('combat')) { await page.click('.prep .btn-fight'); await page.waitForTimeout(4000); await shot('combat'); }
    }
    console.log(tag, Q || '(défaut)', 'erreurs :', page.errors.length ? page.errors.slice(0, 5) : 'aucune');
    await ctx.close();
  }
  await browser.close();
})();
