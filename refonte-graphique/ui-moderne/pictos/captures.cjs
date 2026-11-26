// Vérifie les pictos modernes dans le vrai jeu (habillage moderne) : captures des écrans où on les voit.
//   npx vite --port 4417     (serveur de développement : la navigation est pilotée par ses modules)
//   node refonte-graphique/ui-moderne/pictos/captures.cjs <dossier> [port]
// → <dossier>/<écran>-<taille>.png, en 390 × 844 (encoche imitée) et 360 × 640. Écrans : accueil, bords, héros, sac,
//   fiche, invoquer, aventure, guilde, boutique, quêtes, combat, victoire.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4417';
const ONLY = (process.env.ONLY || '').split(',').filter(Boolean);
const URL = `http://localhost:${PORT}/?skin=moderne`;
const KEY = 'hero-battle-v2';
fs.mkdirSync(OUT, { recursive: true });

function save(s) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1', 'mages-2', 'angels-6', 'demons-12'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 60, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5, dust: 300, crystals: 40, arenaTokens: 90, guildCoins: 400 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: i < 2 ? 7 : i < 5 ? 5 : 3, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 460, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  const slots = ['weapon', 'armor', 'helmet', 'boots'];
  s.items = Array.from({ length: 18 }, (_, i) => ({ uid: 1000 + i, slot: slots[i % 4], rarity: i % 6, tier: 3, ...(i % 6 >= 2 ? { set: ['fury', 'guard', 'rampart', 'storm', 'vampire'][i % 5] } : {}), ...(i < 4 ? { heroUid: 1 } : {}) }));
  s.speed = 3;
  return s;
}

(async () => {
  const browser = await chromium.launch();
  for (const [w, h, notch] of [[390, 844, true], [360, 640, false]]) {
    const tag = `${w}x${h}`;
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2 });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    if (notch) await page.route('**/*', async (r) => {
      const u = r.request().url().split('?')[0];
      if (!(u.endsWith('/') || u.endsWith('.css') || u.endsWith('.html'))) return r.fallback();
      const res = await r.fetch();
      let body = await res.text();
      body = body.replace(/env\(safe-area-inset-top(,\s*0px)?\)/g, '47px').replace(/env\(safe-area-inset-bottom(,\s*0px)?\)/g, '34px');
      await r.fulfill({ response: res, body });
    });
    await page.goto(URL);
    await page.waitForSelector('#splash', { state: 'detached', timeout: 30000 });
    await page.waitForTimeout(500);
    const oks = await page.$$('.name-card button'); const ok = oks[oks.length - 1];
    if (ok) { await ok.click(); await page.waitForTimeout(500); }
    await page.evaluate(([K, f]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s))); }, [KEY, '(' + save.toString() + ')']);
    await page.reload();
    await page.waitForSelector('#splash', { state: 'detached', timeout: 30000 });
    if (notch) await page.evaluate(() => {
      const d = document.createElement('div');
      d.style.cssText = 'position:fixed;z-index:99999;left:50%;top:0;width:126px;height:34px;margin-left:-63px;background:#000;border-radius:0 0 18px 18px;pointer-events:none';
      document.body.appendChild(d);
    });
    const nav = (code) => page.evaluate(`import('/src/game/ui/nav.ts').then((m) => { ${code} })`);
    const want = (n) => !ONLY.length || ONLY.includes(n);
    const shot = async (n) => { await page.screenshot({ path: `${OUT}/${n}-${tag}.png` }); };
    const closeAll = async () => { await nav('m.close(); m.close(); m.close()').catch(() => {}); await page.waitForTimeout(300); };
    await page.waitForTimeout(2500);
    if (want('accueil')) await shot('accueil');
    if (want('bords')) {
      for (const b of await page.$$('.edge-toggle')) await b.click();
      await page.waitForTimeout(800); await shot('bords');
      for (const b of await page.$$('.edge-toggle')) await b.click();
      await page.waitForTimeout(400);
    }
    for (const [tab, name] of [['heroes', 'heros'], ['summon', 'invoquer'], ['adventure', 'aventure'], ['guild', 'guilde']]) {
      if (!want(name) && !(name === 'heros' && want('sac'))) continue;
      await nav(`m.go('${tab}')`); await page.waitForTimeout(1400);
      if (want(name)) await shot(name);
      if (name === 'heros' && want('sac')) {
        const tabs = await page.$$('.heroes-tab .tabs .tab'); if (tabs[1]) { await tabs[1].click(); await page.waitForTimeout(700); await shot('sac'); await tabs[0].click(); }
      }
    }
    await nav("m.go('campaign')"); await page.waitForTimeout(1000);
    for (const [name, code, wait] of [
      ['fiche', "m.open({ type: 'hero', uid: 1 })", 1200], ['boutique', "m.open({ type: 'shop' })", 900],
      ['quetes', "m.open({ type: 'quests' })", 900], ['fusion', "m.open({ type: 'fusion', uid: 4 })", 1200],
      ['victoire', "m.open({ type: 'gain', title: 'Victoire', gain: { currencies: { gold: 1200, gems: 30 }, heroes: [], items: [] }, win: true })", 1200],
    ]) {
      if (!want(name)) continue;
      await nav(code); await page.waitForTimeout(wait); await shot(name); await closeAll();
    }
    if (want('combat')) {
      await page.click('.dock-fight').catch(() => {}); await page.waitForTimeout(1200);
      await page.click('.prep .btn-fight').catch(() => {}); await page.waitForTimeout(6500); await shot('combat');
      await page.waitForTimeout(5000); await shot('combat-2');
    }
    console.log(tag, 'erreurs :', errors.length ? errors.slice(0, 5) : 'aucune');
    await ctx.close();
  }
  await browser.close();
})();
