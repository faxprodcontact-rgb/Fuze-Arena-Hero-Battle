// Captures de l'onglet Boss de la guilde : node boss-guilde-captures.cjs <dossier> [port] [jours...]
// (npm run build ; npx vite preview --port 4755 --strictPort ; puis ce script, avec NODE_PATH=$(npm root -g).)
// Chaque « jour » décale l'horloge du jeu (timeShift de la sauvegarde) de 0, 1, 2… jours : le boss de guilde change
// chaque jour, donc son élément aussi (boss-guilde-<jour>-<taille>.png). FORCE=wind : un élément précis. LANG_JEU=en : anglais.
// Tailles : SIZES=390x844n,360x640 (n = encoche).
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '4755';
const DAYS = process.argv.slice(4).length ? process.argv.slice(4).map(Number) : [0, 1, 2];
fs.mkdirSync(OUT, { recursive: true });
const URL = `http://localhost:${PORT}/?tout=1`;
const KEY = 'hero-battle-v2';

function save(s, day, LANG) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = LANG;
  s.account = { level: 34, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5,
    arenaTokens: 1260, guildCoins: 640 };
  s.timeShift = day * 86400e3;
  s.guild = { ...s.guild, bossDamage: 1284500 };
  s.daily = { ...s.daily, guildAttempts: 1 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 85, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  s.arena.points = 1340;
  s.guild = { ...s.guild, joined: 'Ordre du Corbeau' };
  s.seen = ['tower', 'missions', 'dungeons', 'dailyBoss', 'arena', 'guild', 'defense'];
  return s;
}

const SIZES = (process.env.SIZES || '390x844n,360x640').split(',').map((x) => {
  const m = x.match(/(\d+)x(\d+)(n?)/); return [+m[1], +m[2], !!m[3]];
});

async function boot(browser, w, h, notch, day) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, reducedMotion: 'no-preference' });
  const page = await ctx.newPage();
  page.errors = [];
  page.on('pageerror', (e) => page.errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') page.errors.push(m.text()); });
  // FORCE=wind (ou fire, water, earth) : l'image d'un élément précis, quel que soit le jour (le boss de vent n'existe pas
  // encore dans les règles) ; on remplace seulement le choix de l'élément dans le code construit, rien dans le jeu.
  if (process.env.FORCE) {
    await page.route('**/assets/index-*.js', async (r) => {
      const res = await r.fetch();
      const body = (await res.text()).replace(/const (\w+)=\w+\[\w+\(\)\]\?\?"fire";(return \w+\("div",\{class:`g-boss-stage)/, `const $1="${process.env.FORCE}";$2`);
      await r.fulfill({ response: res, body });
    });
  }
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
  await page.evaluate(([K, f, c, l]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s, c, l))); }, [KEY, '(' + save.toString() + ')', day, process.env.LANG_JEU || 'fr']);
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
  for (let i = 0; i < 4; i++) { const x = await page.$('.modal .x'); if (!x) break; await x.click(); await page.waitForTimeout(250); }
  return [ctx, page];
}

async function overflow(page) {
  return page.evaluate(() => {
    const out = [];
    for (const e of document.querySelectorAll('.adv-scroll, .g-scroll, .g-panel, .content')) {
      const d = e.scrollHeight - e.clientHeight;
      if (d > 2) out.push(`${e.className.split(' ')[0]} +${d}`);
    }
    const doc = document.scrollingElement; if (doc.scrollHeight > innerHeight + 1) out.push(`page +${doc.scrollHeight - innerHeight}`);
    if (doc.scrollWidth > innerWidth + 1) out.push(`largeur +${doc.scrollWidth - innerWidth}`);
    return out;
  });
}

(async () => {
  const browser = await chromium.launch();
  for (const [w, h, notch] of SIZES) {
    const tag = `${w}x${h}`;
    const errs = [];
    for (const day of DAYS) {
      const [ctx, page] = await boot(browser, w, h, notch, day);
      await page.click('.tabbar-btn:nth-child(5)'); await page.waitForTimeout(1200);
      await page.screenshot({ path: `${OUT}/boss-guilde-${process.env.FORCE || day}-${tag}.png` });
      const info = await page.evaluate(() => [document.querySelector('.g-boss-title')?.textContent, document.querySelector('.g-boss-time')?.textContent].join(' | '));
      const o = await overflow(page);
      console.log(`  ${tag} jour ${day} : ${info}${o.length ? ' ; défile ' + o.join(', ') : ''}`);
      errs.push(...page.errors);
      await ctx.close();
    }
    console.log(tag, 'erreurs :', errs.length ? errs.slice(0, 5) : 'aucune');
  }
  await browser.close();
})();
