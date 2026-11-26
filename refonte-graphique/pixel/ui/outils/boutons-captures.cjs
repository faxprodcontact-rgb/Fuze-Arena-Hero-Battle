// Captures des boutons « Pierre de l'arène » dans tout le jeu : node boutons-captures.cjs <dossier> [port] [écrans…]
// (npm run build ; npx vite preview --port 4471 --strictPort ; puis ce script.) 390×844 avec encoche imitée (47 px en haut,
// 34 en bas) et 360×640 sans encoche : <dossier>/<écran>-<taille>.png. Signale : erreurs, défilement, boutons qui débordent.
// Écrans : accueil reglages butin boutique heros heros-fiche invoquer aventure arene tour guilde prep combat auto pause victoire
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4471';
const ONLY = process.argv.slice(4);
fs.mkdirSync(OUT, { recursive: true });
const KEY = 'hero-battle-v2';

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
  await page.goto(`http://localhost:${PORT}/`);
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

// défilement de la page, zones qui défilent sans le vouloir, boutons qui sortent de l'écran ou dont le texte déborde
function audit() {
  const out = [];
  const de = document.documentElement;
  if (de.scrollHeight > innerHeight + 1 || de.scrollWidth > innerWidth + 1) out.push(`page ${de.scrollWidth}x${de.scrollHeight}`);
  for (const e of document.querySelectorAll('.modal-body, .page-body')) if (e.scrollHeight - e.clientHeight > 2) out.push(`${e.className} défile de ${e.scrollHeight - e.clientHeight}px`);
  for (const b of document.querySelectorAll('button, .btn')) {
    const r = b.getBoundingClientRect();
    if (!r.width || getComputedStyle(b).visibility === 'hidden') continue;
    if (r.right > innerWidth + 1 || r.left < -1) out.push(`bouton hors écran : ${b.className} (${Math.round(r.left)}→${Math.round(r.right)})`);
    if (b.classList.contains('btn') && b.scrollWidth > b.clientWidth + 2) out.push(`texte qui déborde : ${b.className} « ${b.textContent.trim().slice(0, 24)} » ${b.scrollWidth}>${b.clientWidth}`);
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
    const back = async () => { const b = await page.$('.av-back'); if (b) { await b.click(); await page.waitForTimeout(400); } };
    if (want('accueil')) await shot('accueil');
    if (want('reglages')) { await page.click('.avatar'); await shot('reglages'); await closeAll(); }
    if (want('butin')) { await page.click('.dock-chest'); await page.waitForTimeout(300); await shot('butin'); await closeAll(); }
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
    if (want('aventure') || want('arene') || want('tour')) {
      await tab(4); if (want('aventure')) await shot('aventure');
      if (want('tour')) { await page.click('.tile-tower'); await shot('tour'); await back(); }
      if (want('arene')) { await page.click('.tile-arena'); await shot('arene'); await back(); }
    }
    if (want('guilde')) { await tab(5); await shot('guilde'); }
    if (want('prep') || want('combat') || want('victoire')) {
      await tab(1);
      await page.click('.dock-fight'); await page.waitForTimeout(800); await shot('prep');
      if (want('combat') || want('victoire')) {
        await page.click('.prep .btn-fight'); await page.waitForTimeout(4000); await shot('combat');
        if (want('auto')) {
          // AUTO (coupé au départ) : vers (590, bas sûr - 276) en unités du jeu ; allumé, il luit
          const k = w / 720;
          await page.mouse.click(590 * k, h - (notch ? 34 : 0) - 276 * k); await page.waitForTimeout(600); await shot('combat-auto');
        }
        if (want('pause')) {
          // le bouton pause : en haut à gauche de la scène (52, haut sûr + 50 en unités du jeu, 720 de large)
          const k = w / 720;
          await page.mouse.click(52 * k, (notch ? 47 : 0) + 50 * k); await page.waitForTimeout(500); await shot('pause');
          await page.mouse.click(w / 2, h / 2 - 30 * k); await page.waitForTimeout(300);
        }
        if (want('victoire')) {
          await page.waitForSelector('.modal .result-title', { timeout: 120000 }).catch(() => {});
          await page.waitForTimeout(1400); await shot('victoire'); await closeAll();
        }
      }
    }
    console.log(tag, 'erreurs :', page.errors.length ? page.errors.slice(0, 5) : 'aucune');
    await ctx.close();
  }
  await browser.close();
})();
