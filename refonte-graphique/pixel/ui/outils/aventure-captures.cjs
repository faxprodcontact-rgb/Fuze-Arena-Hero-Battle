// Captures de la section Aventure (onglet, tour, missions, donjons, boss du jour, arène, Colisée) dans un habillage.
// npx vite preview --port 4393, puis : node aventure-captures.cjs <dossier> 4393 [habillage=moderne]
// 390 × 844 avec encoche imitée (47 px en haut, 34 en bas) et 360 × 640 sans encoche : <dossier>/<taille>/<écran>.png
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4393';
const SKIN = process.argv[4] || 'moderne';
const ONLY = (process.env.ONLY || '').split(',').filter(Boolean);
const KEY = 'hero-battle-v2';

// une partie avancée : tous les modes du quotidien ouverts (sauf le Colisée, qu'on ouvre à part), une mission en cours, une finie
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
  s.dungeons = { gold: 6, essence: 3, gear: 1 };
  s.arena.points = 1340;
  s.seen = ['tower', 'missions', 'dungeons', 'dailyBoss', 'arena', 'guild', 'defense'];
  if (s.daily) {
    s.daily.bossBest = 0; s.daily.bossAttempts = 1; s.daily.arenaFights = 2;
    s.daily.entries = { gold: 1, essence: 0, gear: 3 };
    const ms = s.daily.missions || [];
    if (ms[0]) { ms[0].startedAt = now - 40 * 60e3; ms[0].heroUids = [6, 7]; }
    if (ms[1]) { ms[1].startedAt = now - 200 * 3600e3; ms[1].heroUids = [8, 9]; }
  }
  s.speed = 3;
  return s;
}

const SIZES = [[390, 844, true], [360, 640, false]];

(async () => {
  const browser = await chromium.launch();
  for (const [w, h, notch] of SIZES) {
    const dir = `${OUT}/${w}x${h}`;
    fs.mkdirSync(dir, { recursive: true });
    const URL = `http://localhost:${PORT}/?skin=${SKIN}`;
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2 });
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
    const boot = async () => {
      await page.waitForSelector('#splash', { state: 'detached', timeout: 20000 });
      await page.waitForTimeout(400);
    };
    const load = async (cleared) => {
      await page.evaluate(([K, f, c]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s, c))); }, [KEY, '(' + save.toString() + ')', cleared]);
      await page.reload(); await boot();
      if (notch) await page.evaluate(() => {
        const d = document.createElement('div');
        d.style.cssText = 'position:fixed;z-index:99999;left:50%;top:0;width:126px;height:34px;margin-left:-63px;background:#000;border-radius:0 0 18px 18px;pointer-events:none';
        document.body.appendChild(d);
        const b = document.createElement('div');
        b.style.cssText = 'position:fixed;z-index:99999;left:50%;bottom:8px;width:134px;height:5px;margin-left:-67px;background:#fff;border-radius:3px;pointer-events:none';
        document.body.appendChild(b);
      });
    };
    await page.goto(URL); await boot();
    const oks = await page.$$('.name-card button'); const ok = oks[oks.length - 1];
    if (ok) { await ok.click(); await page.waitForTimeout(500); }
    await load(85);
    const want = (n) => !ONLY.length || ONLY.includes(n);
    const shot = async (n) => {
      await page.waitForTimeout(900);
      await page.screenshot({ path: `${dir}/${n}.png` });
      // défilement : la hauteur du contenu dépasse-t-elle la zone ?
      const over = await page.evaluate(() => Math.max(0, ...[...document.querySelectorAll('.adv-scroll, .page-body, .modal-body')].map((e) => e.scrollHeight - e.clientHeight)));
      if (over > 2) console.log(`  ${w}x${h} ${n} : défile de ${over} px`);
    };
    const closeAll = async () => { for (let i = 0; i < 4; i++) { const x = await page.$('.modal .x, .page .x, .page-close'); if (!x) break; await x.click(); await page.waitForTimeout(250); } };
    const tab = async () => { await page.click('.tabbar-btn:nth-child(4)'); await page.waitForTimeout(900); };
    const sub = async (cls) => { await tab(); await page.click(`.tile-${cls}`); await page.waitForTimeout(700); };
    const back = async () => { const b = await page.$('.av-back'); if (b) { await b.click(); await page.waitForTimeout(400); } };
    await tab();
    if (want('aventure')) await shot('aventure');
    if (want('tour')) { await sub('tower'); await shot('tour'); await back(); }
    if (want('missions')) { await sub('missions'); await shot('missions'); }
    if (want('mission')) {
      if (!want('missions')) await sub('missions');
      const send = await page.$('.av-mission .btn-blue');
      if (send) { await send.click(); await page.waitForTimeout(700); await shot('mission'); await closeAll(); }
    }
    await back();
    if (want('donjons')) { await sub('dungeons'); await shot('donjons'); }
    if (want('donjon')) {
      if (!want('donjons')) await sub('dungeons');
      await page.click('.dungeon-gold'); await page.waitForTimeout(700); await shot('donjon'); await closeAll();
    }
    await back();
    if (want('boss')) { await sub('dailyBoss'); await shot('boss'); await back(); }
    if (want('arene')) { await sub('arena'); await shot('arene'); }
    if (want('arene-boutique')) {
      if (!want('arene')) await sub('arena');
      const tabs = await page.$$('.av-seg button');
      if (tabs[1]) { await tabs[1].click(); await page.waitForTimeout(500); await shot('arene-boutique'); }
    }
    await back();
    if (want('colisee')) {
      await load(400); await tab();
      await shot('aventure-tout');
      await page.click('.tile-defense'); await page.waitForTimeout(700); await shot('colisee');
    }
    console.log(w, h, 'erreurs :', errors.length ? errors.slice(0, 5) : 'aucune');
    await ctx.close();
  }
  await browser.close();
})();
