// Fonds des maquettes de boutons : captures du vrai jeu (habillage moderne, pictos modernes), sans le bas de l'accueil,
// sans le panneau d'invocation et sans la barre des onglets (les maquettes les redessinent avec chaque famille de boutons).
//   npx vite --port 4871 --strictPort          (dans le dossier principal du jeu)
//   node refonte-graphique/ui-moderne/boutons/fonds.cjs [port] [planche-pictos.webp] [icons-meta.ts]
// → refonte-graphique/ui-moderne/boutons/fonds/{accueil,invoquer}.jpg (390 × 844 ×2, encoche imitée) + zones.json
// Les deux derniers arguments (facultatifs) remplacent à la volée la planche des pictos et son index, pour voir les
// pictos modernes avant qu'ils soient dans le jeu (la planche doit avoir des cases de 128 px : Phaser la découpe ainsi).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const PORT = process.argv[2] || '4871';
const ICONS = process.argv[3];
const META = process.argv[4];
const OUT = path.join(__dirname, 'fonds');
const KEY = 'hero-battle-v2';
fs.mkdirSync(OUT, { recursive: true });

function save(s) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1', 'mages-2', 'angels-6', 'demons-12'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 60, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5, dust: 300, crystals: 40 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: i < 2 ? 7 : i < 5 ? 5 : 3, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 460, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.speed = 3;
  return s;
}

(async () => {
  const esbuild = META ? require('esbuild') : null;
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  await page.route('**/*', async (r) => {
    const u = r.request().url().split('?')[0];
    if (ICONS && u.endsWith('/art/icons.webp')) return r.fulfill({ body: fs.readFileSync(ICONS), contentType: 'image/webp' });
    if (META && u.endsWith('/src/game/icons-meta.ts')) {
      const js = esbuild.transformSync(fs.readFileSync(META, 'utf8'), { loader: 'ts', format: 'esm' }).code;
      return r.fulfill({ body: js, contentType: 'application/javascript' });
    }
    if (!(u.endsWith('/') || u.endsWith('.css') || u.endsWith('.html'))) return r.fallback();
    const res = await r.fetch();
    let body = await res.text();
    body = body.replace(/env\(safe-area-inset-top(,\s*0px)?\)/g, '47px').replace(/env\(safe-area-inset-bottom(,\s*0px)?\)/g, '34px');
    await r.fulfill({ response: res, body });
  });
  const url = `http://localhost:${PORT}/?skin=moderne`;
  await page.goto(url);
  await page.waitForSelector('#splash', { state: 'detached', timeout: 30000 });
  await page.waitForTimeout(500);
  const oks = await page.$$('.name-card button'); const ok = oks[oks.length - 1];
  if (ok) { await ok.click(); await page.waitForTimeout(500); }
  await page.evaluate(([K, f]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s))); }, [KEY, '(' + save.toString() + ')']);
  await page.reload();
  await page.waitForSelector('#splash', { state: 'detached', timeout: 30000 });
  await page.addStyleTag({ content: '.icon, .art { image-rendering: auto !important; }' });
  await page.evaluate(() => {
    const d = document.createElement('div');
    d.style.cssText = 'position:fixed;z-index:99999;left:50%;top:0;width:126px;height:34px;margin-left:-63px;background:#000;border-radius:0 0 18px 18px;pointer-events:none';
    document.body.appendChild(d);
  });
  const nav = (code) => page.evaluate(`import('/src/game/ui/nav.ts').then((m) => { ${code} })`);
  const rect = (sel) => page.evaluate((s) => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return { x: r.x, y: r.y, w: r.width, h: r.height }; }, sel);
  const hide = (sels) => page.addStyleTag({ content: sels.map((s) => `${s} { visibility: hidden !important; }`).join('\n') });
  const zones = {};
  await page.waitForTimeout(3000);
  zones.accueil = { dock: await rect('.dock'), tabbar: await rect('.tabbar') };
  await hide(['.dock', '.tabbar']);
  await page.waitForTimeout(200);
  await page.screenshot({ path: `${OUT}/accueil.jpg`, type: 'jpeg', quality: 88 });
  await nav("m.go('summon')"); await page.waitForTimeout(1800);
  zones.invoquer = { panel: await rect('.sum-panel'), tabbar: await rect('.tabbar') };
  await hide(['.sum-panel']);
  await page.waitForTimeout(200);
  await page.screenshot({ path: `${OUT}/invoquer.jpg`, type: 'jpeg', quality: 88 });
  fs.writeFileSync(`${OUT}/zones.json`, JSON.stringify(zones, null, 1));
  console.log(JSON.stringify(zones));
  await browser.close();
})();
