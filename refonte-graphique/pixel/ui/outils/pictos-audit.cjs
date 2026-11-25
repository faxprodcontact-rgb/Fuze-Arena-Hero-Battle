// Recherche, dans le vrai jeu, des petits dessins qui ne sont pas des pictos pixel art de la planche :
//   npx vite --port 4392   (serveur de développement : on pilote la navigation par ses modules)
//   node refonte-graphique/pixel/ui/outils/pictos-audit.cjs <dossier> [port] [--shots] [écrans…]
// Pour chaque écran et chaque fenêtre : dessins SVG visibles, symboles écrits (★ ✓ ✕ 🔒…), contenus des ::before /
// ::after, images et fonds qui ne viennent ni de la planche ni des dessins HD. Résultat : <dossier>/audit.json (+ captures
// <écran>-<taille>.png avec --shots). Tailles : 390×844 (encoche imitée) et 360×640 (SIZES=390x844n,360x640).
const { chromium } = require('playwright');
const fs = require('fs');
const args = process.argv.slice(2);
const OUT = args[0];
const PORT = args[1] && /^\d+$/.test(args[1]) ? args[1] : '4392';
const SHOTS = args.includes('--shots');
const ONLY = args.slice(1).filter((a) => !/^\d+$/.test(a) && !a.startsWith('--'));
fs.mkdirSync(OUT, { recursive: true });
const URL = `http://localhost:${PORT}/`;
const KEY = 'hero-battle-v2';

function save(s) {
  const now = Date.now();
  const ids = ['knights-8', 'mages-8', 'assassins-2', 'angels-2', 'myths-3', 'demons-4', 'knights-1', 'mages-2', 'angels-6', 'demons-12', 'myths-9', 'assassins-11'];
  s.named = true; s.name = 'Aria'; s.tutorial = -1; s.lang = 'fr';
  s.account = { level: 60, xp: 420 };
  s.wallet = { ...s.wallet, gold: 125400, essence: 8420, gems: 2350, scrolls: 12, basicScrolls: 5, dust: 300, crystals: 40, arenaTokens: 90, guildCoins: 400 };
  s.heroes = ids.map((id, i) => ({ uid: i + 1, defId: id, stars: i < 3 ? 7 : i < 6 ? 5 : 3, level: 60 - i * 3 }));
  s.discovered = ids; s.nextUid = ids.length + 1;
  s.formation = [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]];
  s.campaign = { cleared: 460, idleFrom: now - 5.5 * 3600e3, itemHours: 0 };
  const slots = ['weapon', 'armor', 'helmet', 'boots'];
  s.items = Array.from({ length: 14 }, (_, i) => ({ uid: 1000 + i, slot: slots[i % 4], rarity: i % 6, tier: 3, ...(i % 6 >= 2 ? { set: ['fury', 'guard', 'rampart', 'storm', 'vampire'][i % 5] } : {}), ...(i < 4 ? { heroUid: 1 } : {}) }));
  s.speed = 3;
  return s;
}

const SIZES = (process.env.SIZES || '390x844n,360x640').split(',').map((x) => {
  const m = x.match(/(\d+)x(\d+)(n?)/); return [+m[1], +m[2], !!m[3]];
});

// Ce que la page cherche (exécuté dans le navigateur).
function scan() {
  const out = [];
  const vis = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth && getComputedStyle(e).visibility !== 'hidden'; };
  const cls = (n) => { const c = typeof n.className === 'string' ? n.className : n.className?.baseVal ?? ''; return c.trim() ? '.' + c.trim().split(/\s+/).join('.') : ''; };
  const path = (e) => { const s = []; for (let n = e; n && n !== document.body && s.length < 3; n = n.parentElement) s.push(n.tagName.toLowerCase() + cls(n)); return s.reverse().join(' > '); };
  for (const e of document.querySelectorAll('svg')) {
    if (!vis(e) || e.parentElement.closest('svg') || e.classList.contains('chrome-defs')) continue;
    const r = e.getBoundingClientRect();
    out.push(['svg', `${Math.round(r.width)}x${Math.round(r.height)}`, path(e)]);
  }
  const sym = /^[^\p{L}\p{N}\s]{1,3}$|\p{Extended_Pictographic}|[★☆✓✔✕✖✚✦⚄⧉▲▼∅🔒👆]/u;
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n; (n = w.nextNode());) {
    const tx = n.textContent.trim();
    if (!tx || !sym.test(tx) || !n.parentElement || !vis(n.parentElement) || n.parentElement.closest('svg, script, style')) continue;
    out.push(['texte', tx.slice(0, 24), path(n.parentElement)]);
  }
  for (const e of document.body.querySelectorAll('*')) {
    if (!vis(e)) continue;
    for (const p of ['::before', '::after']) {
      const c = getComputedStyle(e, p).content;
      if (c && c !== 'none' && c !== 'normal' && c !== '""') out.push(['pseudo' + p, c, path(e)]);
    }
    const bg = getComputedStyle(e).backgroundImage;
    for (const m of bg.matchAll(/url\("?([^")]+)"?\)/g)) {
      const u = m[1];
      if (u.startsWith('data:') || /art\/(icons\.webp|hd\/|px\/)/.test(u)) continue;
      out.push(['fond', u.replace(location.origin, ''), path(e)]);
    }
  }
  for (const i of document.images) if (vis(i) && !/art\/(hd|px)\//.test(i.src)) out.push(['img', i.src.replace(location.origin, ''), path(i)]);
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const report = {};
  for (const [w, h, notch] of SIZES) {
    const tag = `${w}x${h}`;
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2 });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
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
    await page.waitForSelector('#splash', { state: 'detached', timeout: 30000 });
    await page.waitForTimeout(500);
    const oks = await page.$$('.name-card button'); const ok = oks[oks.length - 1];
    if (ok) { await ok.click(); await page.waitForTimeout(500); }
    const setSave = async (extra) => {
      await page.evaluate(([K, f, x]) => { const s = (0, eval)(f)(JSON.parse(localStorage.getItem(K))); Object.assign(s, x ? (0, eval)(x)(s) : {}); localStorage.setItem(K, JSON.stringify(s)); }, [KEY, '(' + save.toString() + ')', extra]);
      await page.reload();
      await page.waitForSelector('#splash', { state: 'detached', timeout: 30000 });
      await page.waitForTimeout(1500);
    };
    await setSave();
    const nav = (code) => page.evaluate(`import('/src/game/ui/nav.ts').then((m) => { ${code} })`);
    const want = (n) => !ONLY.length || ONLY.includes(n);
    const look = async (name, code, wait = 900) => {
      if (!want(name)) return;
      if (code) await nav(code);
      await page.waitForTimeout(wait);
      const found = await page.evaluate(scan);
      (report[name] ??= {})[tag] = found;
      if (SHOTS) await page.screenshot({ path: `${OUT}/${name}-${tag}.png` });
    };
    const closeModals = async () => { await nav('for (let i = 0; i < 6; i++) m.close();'); await page.waitForTimeout(200); };

    await look('accueil', null, 1500);
    if (want('bords')) { for (const b of await page.$$('.edge-toggle')) await b.click(); await look('bords', null, 800); for (const b of await page.$$('.edge-toggle')) await b.click(); }
    const modals = [
      ['reglages', "m.open({ type: 'settings' })"], ['quetes', "m.open({ type: 'quests' })"], ['boutique', "m.open({ type: 'shop' })"],
      ['boutique-pass', "m.open({ type: 'shop', tab: 'pass' })"], ['boutique-echange', "m.open({ type: 'shop', tab: 'exchange' })"],
      ['classement', "m.open({ type: 'ranking' })"], ['tchat', "m.open({ type: 'chat' })"], ['chances', "m.open({ type: 'odds' })"],
      ['fragments', "m.open({ type: 'fragments' })"], ['confirmer', "m.open({ type: 'confirm', text: 'Sûr ?', onYes: () => {} })"],
      ['pub', "m.open({ type: 'ad', onDone: () => {} })"], ['butin-rapide', "m.open({ type: 'fastLoot' })"], ['carte', "m.open({ type: 'worldMap' })"],
      ['nom', "m.open({ type: 'rename' })"], ['fusion', "m.open({ type: 'fusion' })"], ['fusion-heros', "m.open({ type: 'fusion', uid: 4 })"],
      ['forge', "m.open({ type: 'forge' })"], ['renaissance', "m.open({ type: 'reset', uid: 2 })"], ['mission', "m.open({ type: 'mission', id: 'patrol' })"],
      ['donjon-or', "m.open({ type: 'dungeon', kind: 'gold' })"], ['donjon-objets', "m.open({ type: 'dungeon', kind: 'gear' })"],
      ['amis', "m.open({ type: 'friends' })"], ['connexion', "m.open({ type: 'login' })"], ['courrier', "m.open({ type: 'mail' })"],
      ['objet', "m.open({ type: 'item', uid: 1005 })"], ['legal', "m.open({ type: 'legal', doc: 'privacy' })"],
      ['gain', "m.open({ type: 'gain', title: 'Victoire', gain: { currencies: { gold: 1200, gems: 30 }, heroes: [], items: [] }, win: true })"],
      ['defaite', "m.open({ type: 'gain', title: 'Défaite', gain: { currencies: {}, heroes: [], items: [] }, win: false })"],
      ['prep', "m.open({ type: 'prep', plan: null })"], ['fiche', "m.open({ type: 'hero', uid: 1 })"], ['fiche-2', "m.open({ type: 'hero', uid: 9 })"],
    ];
    for (const [n, c] of modals) { await look(n, c); await closeModals(); }
    if (want('fiche-objets')) {
      await nav("m.open({ type: 'hero', uid: 1 })"); await page.waitForTimeout(900);
      const tab = await page.$('.hp-gear .hp-slot, .hp-slot'); if (tab) await tab.click();
      await look('fiche-objets', null, 700); await closeModals();
    }
    const tabs = [['heros', "m.go('heroes')"], ['invoquer', "m.go('summon')"], ['aventure', "m.go('adventure')"], ['guilde', "m.go('guild')"]];
    for (const [n, c] of tabs) await look(n, c, 1300);
    for (const f of ['tower', 'missions', 'dungeons', 'dailyBoss', 'arena', 'defense']) await look(`mode-${f}`, `m.go('adventure'); m.openSub('${f}')`, 1200);
    if (want('guilde-membre')) { await setSave("(s) => ({ guild: { ...s.guild, joined: 'Lames d’Aube' } })"); await look('guilde-membre', "m.go('guild')", 1300); }
    if (want('invocation')) {
      await nav("m.go('summon')"); await page.waitForTimeout(800);
      await look('invocation', "m.open({ type: 'summon', heroes: [{ uid: 1, defId: 'knights-8', stars: 4, level: 1 }, { uid: 2, defId: 'mages-8', stars: 3, level: 1 }] })", 4000);
      await closeModals();
    }
    if (want('combat')) {
      await nav("m.go('campaign')"); await page.waitForTimeout(600);
      await page.click('.dock-fight').catch(() => {}); await page.waitForTimeout(1200);
      await page.click('.prep .btn-fight').catch(() => {}); await look('combat', null, 5000);
    }
    if (want('tutoriel')) { await setSave('(s) => ({ tutorial: 0 })'); await look('tutoriel', null, 1500); }
    console.log(tag, 'erreurs :', errors.length ? errors.slice(0, 5) : 'aucune');
    fs.writeFileSync(`${OUT}/audit.json`, JSON.stringify(report, null, 1));
    await ctx.close();
  }
  fs.writeFileSync(`${OUT}/audit.json`, JSON.stringify(report, null, 1));
  // résumé : chaque trouvaille une fois, avec les écrans où elle apparaît
  const seen = new Map();
  for (const [screen, bySize] of Object.entries(report)) for (const list of Object.values(bySize)) for (const [k, v, p] of list) {
    const key = `${k} | ${v} | ${p.split(' > ').slice(-2).join(' > ')}`;
    if (!seen.has(key)) seen.set(key, new Set());
    seen.get(key).add(screen);
  }
  const lines = [...seen].map(([k, s]) => `${k}   ← ${[...s].join(', ')}`).sort();
  fs.writeFileSync(`${OUT}/audit.txt`, lines.join('\n') + '\n');
  console.log(lines.length, 'trouvailles →', `${OUT}/audit.txt`);
  await browser.close();
})();
