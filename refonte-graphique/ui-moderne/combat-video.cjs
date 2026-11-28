// Le VRAI combat, image par image, pour contrôler un personnage exporté (consigne EXPORT-JEU.md, étape 4).
// Le temps du jeu est VIRTUEL : requestAnimationFrame, performance.now et Date.now sont tenus par ce script ; chaque pas avance
// de 1000/FPS ms, puis une capture nette (×2) est prise. Aucune image manquée, même si la capture est lente.
//
//   npx vite build --outDir <brouillon>/dist && npx vite preview --outDir <brouillon>/dist --port 5010 &
//   HEROS=assassins-2,assassins-9 CLEARED=25 node refonte-graphique/ui-moderne/combat-video.cjs <brouillon>/video 5010 30 25
//
// HEROS : les héros de l'équipe (ids du jeu, 5 au plus, complétés par d'autres) ; CLEARED : étapes de campagne déjà
// faites (le combat est la suivante : 25 → étape 26 = clan de Kael, 3 golems de lave) ; LVL : niveau des héros ;
// SAUTE : secondes jouées sans capture au début (pour arriver vite aux spéciales).
// Sorties : <dossier>/img/v0000.jpg… (390 × 844 à ×2). Montage : ffmpeg -framerate 25 -i img/v%04d.jpg …
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || '5010';
const SECS = Number(process.argv[4] || 20);
const FPS = Number(process.argv[5] || 25);
const KEY = 'hero-battle-v2';
fs.mkdirSync(`${OUT}/img`, { recursive: true });
const LVL = Number(process.env.LVL || 30), CLEARED = Number(process.env.CLEARED || 25);
const FILL = ['angels-10', 'angels-2', 'myths-3', 'knights-1', 'mages-8'];
const ids = [...new Set([...(process.env.HEROS || 'assassins-2,assassins-9').split(',').filter(Boolean), ...FILL])].slice(0, 5);
const SAVE = `(s) => {
  const ids = ${JSON.stringify(ids)};
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 18, xp: 420 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: 5, level: ${LVL} - i * 2 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = ids.map((_, i) => [i + 1, i]);
  s.campaign = { cleared: ${CLEARED}, idleFrom: Date.now() - 3600e3, itemHours: 0 };
  s.speed = 1; s.auto = true;
  return s;
}`;
/** Dans la page : l'horloge du jeu ne bouge que quand on l'avance (__step). */
function virtualClock() {
  const raf = window.requestAnimationFrame.bind(window);
  const pnow = performance.now.bind(performance);
  let on = false, vt = 0, q = [], v0 = 0, d0 = 0;
  // les tweens de Phaser lisent Date.now : on le tient aussi (sinon projectiles et retours vont à la vitesse réelle)
  const dnow = Date.now.bind(Date);
  Date.now = () => (on ? d0 + (vt - v0) : dnow());
  window.requestAnimationFrame = (cb) => { if (on) { q.push(cb); return q.length; } return raf(cb); };
  performance.now = () => (on ? vt : pnow());
  window.__virtOn = () => { vt = pnow(); v0 = vt; d0 = dnow(); on = true; };
  window.__step = (ms) => { vt += ms; const run = q; q = []; run.forEach((cb) => cb(vt)); };
}
(async () => {
  const browser = await chromium.launch();
  const opts = { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 };
  const url = `http://localhost:${PORT}/`;
  // 1) la sauvegarde d'essai
  let ctx = await browser.newContext(opts);
  let page = await ctx.newPage();
  await page.goto(url);
  await page.waitForSelector('#splash', { state: 'detached', timeout: 30000 });
  await page.waitForTimeout(500);
  const oks = await page.$$('.name-card button');
  if (oks.length) { await oks[oks.length - 1].click(); await page.waitForTimeout(500); }
  await page.evaluate(([K, f]) => { const s = JSON.parse(localStorage.getItem(K)); localStorage.setItem(K, JSON.stringify((0, eval)(f)(s))); }, [KEY, '(' + SAVE + ')']);
  const state = await ctx.storageState();
  await ctx.close();
  // 2) le combat, en temps virtuel
  ctx = await browser.newContext({ ...opts, storageState: state });
  page = await ctx.newPage();
  await page.addInitScript(virtualClock);
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(url);
  await page.waitForSelector('#splash', { state: 'detached', timeout: 30000 });
  await page.waitForTimeout(1200);
  for (let i = 0; i < 4; i++) { const x = await page.$('.modal .x'); if (!x) break; await x.click(); await page.waitForTimeout(300); }
  await page.click('.dock-fight'); await page.waitForTimeout(1200);
  await page.click('.btn-fight');
  await page.waitForTimeout(900);                    // le combat se charge (planches) en temps réel
  await page.evaluate(() => window.__virtOn());
  // SAUTE=<s> : les premières secondes passent sans capture (la spéciale n'arrive qu'à énergie pleine, souvent après 30 s)
  for (let i = 0; i < Math.round(Number(process.env.SAUTE || 0) * FPS); i++) await page.evaluate((ms) => window.__step(ms), 1000 / FPS);
  const n = Math.round(SECS * FPS);
  for (let i = 0; i < n; i++) {
    await page.evaluate((ms) => window.__step(ms), 1000 / FPS);
    await page.screenshot({ path: `${OUT}/img/v${String(i).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  if (errors.length) console.log('erreurs :', errors.slice(0, 8));
  await browser.close();
  console.log(n, 'images dans', `${OUT}/img`);
})();
