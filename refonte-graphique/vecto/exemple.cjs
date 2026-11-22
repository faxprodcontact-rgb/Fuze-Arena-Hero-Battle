// La page d'exemple des personnages vectoriels (demande du propriétaire, 22/11/2026) : 5 héros contre 5 monstres en
// combat sur la prairie, aux places et à la taille du vrai jeu, chacun son tour ; puis une galerie « dessin actuel /
// nouveau dessin » où chaque personnage peut lancer son attaque.
// node refonte-graphique/vecto/exemple.cjs <sortie.html> [--essai]   (--essai : Ruka à la place des dessins manquants)
//
// Plusieurs dessins dans la même page : chaque SVG est « rangé » sous un préfixe (identifiants, classes, noms
// d'animations), sinon les dégradés et les animations d'un personnage s'appliqueraient aux autres.
const fs = require('fs');
const path = require('path');
const REPO = path.resolve(__dirname, '../..');
const [out = 'exemple.html', ...flags] = process.argv.slice(2);
const essai = flags.includes('--essai');

const HEROES = [
  ['knights-8', 'Garvin', 2], ['mages-10', 'Ozias', 0], ['knights-11', 'Valdis', 1], ['assassins-12', 'Saïko', 3], ['assassins-5', 'Rook', 4],
];
const MONSTERS = [
  ['parade-1', 'Pétard', 0], ['abysses-3', 'Méduse des abysses', 2], ['bayou-4', 'Feu follet', 3], ['glaces-4', 'Chouette des neiges', 4], ['cuirasses-4', 'Escargot de cristal', 1],
];
// le combat du jeu (fight-view.ts) : largeur 720, rangées sous le haut du sol, pieds 47 px plus bas
const HERO_X = { 3: 82, 4: 82, 2: 163, 0: 245, 1: 245 };
const ENEMY_X = { 0: 475, 1: 475, 2: 557, 3: 638, 4: 638 };
const ROW_DY = { 0: 90, 3: 90, 2: 180, 1: 270, 4: 270 };
const GT = 733, FEET = 47, UNIT_PX = 0.56, SW = 720, SH = 1163;
const CROP = 430; // le haut du ciel coupé dans la page

// la place de chaque dessin dans le jeu : [ox, oy, w, h, échelle, stature] (art-meta.ts) ; les pieds au point 106, 228
const meta = fs.readFileSync(`${REPO}/src/game/art-meta.ts`, 'utf8');
const artOf = (id) => JSON.parse(`[${new RegExp(`"${id}":\\[([^\\]]*)\\]`).exec(meta)[1]}]`);

function load(id) {
  const file = `${REPO}/refonte-graphique/vecto/${id}.cjs`;
  if (!fs.existsSync(file)) {
    if (!essai) throw new Error(`dessin manquant : ${id}`);
    return { ...require('./demons-7.cjs'), essai: true };
  }
  delete require.cache[require.resolve(file)];
  return require(file);
}

/** Range un SVG sous un préfixe : identifiants et renvois, classes, sélecteurs et noms d'animations. */
function scope(svg, P) {
  svg = svg.replace(/\bid="([^"]+)"/g, (_, v) => `id="${P}${v}"`)
    .replace(/url\(#([^)]+)\)/g, (_, v) => `url(#${P}${v})`)
    .replace(/href="#([^"]+)"/g, (_, v) => `href="#${P}${v}"`)
    .replace(/\bclass="([^"]+)"/g, (_, v) => `class="${v.trim().split(/\s+/).map((t) => P + t).join(' ')}"`);
  return svg.replace(/<style>([\s\S]*?)<\/style>/, (_, css) => {
    const names = [...css.matchAll(/@keyframes\s+([\w-]+)/g)].map((m) => m[1]);
    css = css.replace(/([^{}]+)\{/g, (m, sel) => {
      const s = sel.trim();
      if (s.startsWith('@') || /^(from|to|[\d.]+%)/.test(s)) return m;
      return `${sel.replace(/\.([a-zA-Z_][\w-]*)/g, (_, c) => `.${P}${c}`)}{`;
    });
    css = css.replace(/@keyframes\s+([\w-]+)/g, (_, n) => `@keyframes ${P}${n}`);
    css = css.replace(/(animation(?:-name)?\s*:\s*)([^;}]+)/g, (_, k, v) => k + v.replace(/[\w-]+/g, (t) => (names.includes(t) ? P + t : t)));
    return `<style>${css}</style>`;
  });
}

const b64 = (file) => fs.readFileSync(file).toString('base64');
let n = 0;
/** Un personnage prêt pour la page : SVG rangé, taille et place dans la scène (unités de la scène, 720 de large). */
function unit([id, name, slot], hero) {
  const ch = load(id);
  const P = `v${n++}`;
  const [ox, oy, w, h, sc, norm] = artOf(id);
  const k = UNIT_PX * (norm || Math.max(0.85, Math.min(1.35, sc)));
  const s = (w * k) / ch.w; // unités de la scène par pixel du dessin
  const fx = ((106 - ox) / w) * ch.w, fy = ((228 - oy) / h) * ch.h; // les pieds, en pixels du dessin
  const pad = ch.pad ?? 24;
  const X = hero ? HERO_X[slot] : ENEMY_X[slot], Y = GT + ROW_DY[slot] + FEET;
  const left = hero ? X - (fx + pad) * s : X - (ch.w + pad - fx) * s;
  return {
    id, name, hero, P, svg: scope(ch.svg(true), P).replace('<svg ', `<svg class="fig-svg" data-p="${P}" `),
    still: ch.svg(false), w: ch.w, h: ch.h,
    box: { left, top: Y - (fy + pad) * s, width: (ch.w + 2 * pad) * s, height: (ch.h + 2 * pad) * s }, X, Y, shadow: Math.min(160, w * k * 0.55),
  };
}

const heroes = HEROES.map((u) => unit(u, true));
const monsters = MONSTERS.map((u) => unit(u, false));
const all = [...heroes, ...monsters];

// la galerie : TOUS les personnages déjà redessinés (un fichier <famille>-<n>.cjs dans ce dossier), héros d'abord
const HERO_FAMILIES = ['knights', 'assassins', 'mages', 'demons', 'angels', 'myths'];
const heroNames = {};
for (const m of fs.readFileSync(`${REPO}/src/core/data/heroes.ts`, 'utf8').matchAll(/^\s+(\w+): \[('[^\n]*')\],$/gm)) {
  [...m[2].matchAll(/'([^']*)'/g)].forEach((n, i) => { heroNames[`${m[1]}-${i + 1}`] = n[1]; });
}
/** Les noms des monstres redessinés (les monstres n'ont pas de nom dans le jeu) : à compléter à chaque nouveau monstre. */
const MONSTER_NAMES = {
  'parade-1': 'Pétard', 'abysses-3': 'Méduse des abysses', 'bayou-4': 'Feu follet', 'glaces-4': 'Chouette des neiges', 'cuirasses-4': 'Escargot de cristal',
  'epouvantails-2': 'Épouvantail', 'ronciers-1': 'Renard de feuilles', 'bayou-1': 'Dino-voile', 'parade-2': 'Lion de la parade', 'epouvantails-1': 'Coq-girouette',
};
const isHero = (id) => HERO_FAMILIES.includes(id.split('-')[0]);
const done = fs.readdirSync(__dirname).filter((f) => /^[a-z]+-\d+\.cjs$/.test(f)).map((f) => f.slice(0, -4))
  .sort((a, b) => (isHero(b) - isHero(a)) || a.localeCompare(b, 'fr', { numeric: true }));
const gallery = done.map((id) => {
  const ch = load(id);
  return { id, hero: isHero(id), name: (isHero(id) ? heroNames[id] : MONSTER_NAMES[id]) || id, w: ch.w, h: ch.h };
});
const pc = (v, of) => `${((v / of) * 100).toFixed(3)}%`;
const sceneUnit = (u, i) => `<div class="unit${u.hero ? '' : ' foe'}" data-p="${u.P}" style="left:${pc(u.box.left, SW)};top:${pc(u.box.top - CROP, SH - CROP)};width:${pc(u.box.width, SW)};z-index:${Math.round(u.Y)}">`
  + `<span class="shadow" style="left:${pc(u.X - u.box.left - u.shadow / 2, u.box.width)};top:${pc(u.Y - u.box.top - 10, u.box.height)};width:${pc(u.shadow, u.box.width)}"></span>`
  + `<div class="fig" style="animation-duration:${(2.6 + (i % 5) * 0.23).toFixed(2)}s">${u.svg}</div></div>`;

const card = (u) => {
  const P = `g${n++}`;
  // dans la galerie, le dessin est cadré sur son cadre d'origine (sans la marge des animations) : même taille que l'ancien
  const svg = scope(load(u.id).svg(true), P)
    .replace(/<svg ([^>]*?)viewBox="[^"]*" width="[^"]*" height="[^"]*"/, `<svg $1viewBox="0 0 ${u.w} ${u.h}" width="${u.w}" height="${u.h}"`)
    .replace('<svg ', `<svg class="fig-svg" data-p="${P}" `);
  return `<article class="card">
  <h2>${u.name}<small>${u.hero ? 'héros' : 'monstre'}</small></h2>
  <div class="pair">
    <figure><img src="data:image/webp;base64,${b64(`${REPO}/public/art/p/${u.id}.webp`)}" alt=""><figcaption>Avant</figcaption></figure>
    <figure class="new" data-p="${P}">${svg}<figcaption>Nouveau</figcaption></figure>
  </div>
  <button class="atk-btn" data-p="${P}">Attaque</button>
</article>`;
};

const html = `<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Personnages redessinés</title>
<style>
:root { --ink: #0e1433; --gold: #ffd24a; --bg: #121838; --fg: #fff3d6; color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: #121838; color: #fff3d6; font: 15px/1.4 system-ui, -apple-system, 'Segoe UI', sans-serif; }
main { max-width: 480px; margin: 0 auto; }
header { padding-block: 18px 10px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
h1 { margin: 0; font-size: 22px; color: var(--gold); }
header p { margin: 4px 0 0; color: #c9d2f0; font-size: 14px; }
.scene { position: relative; width: 100%; aspect-ratio: ${SW} / ${SH - CROP}; overflow: hidden; background: #8ec6e8; }
.scene > img { position: absolute; left: 0; top: ${((-CROP / (SH - CROP)) * 100).toFixed(3)}%; width: 100%; height: auto; display: block; }
.unit { position: absolute; }
.fig { position: relative; transform-origin: 50% 92%; animation: breathe 2.8s ease-in-out infinite; }
.foe .fig { transform: scaleX(-1); }
.fig-svg { display: block; width: 100%; height: auto; overflow: visible; }
.shadow { position: absolute; aspect-ratio: 8 / 1; border-radius: 50%; background: radial-gradient(closest-side, #000000a6, #00000000); }
@keyframes breathe { 50% { scale: 1 1.018; } }
.hit .fig { animation: hit .32s ease-out; }
@keyframes hit { 30% { translate: 6px 0; opacity: .75; } }
.foe.hit .fig { animation-name: hit-foe; }
@keyframes hit-foe { 30% { translate: -6px 0; opacity: .75; } }
.gallery { padding-block: 8px 40px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); display: grid; gap: 14px; }
.card { background: linear-gradient(180deg, #2a3676, #18204b); border: 1.5px solid #0a0e26; border-radius: 16px; box-shadow: inset 0 0 0 1.5px #d9a63e88, 0 6px 14px #0006; padding: 12px; content-visibility: auto; contain-intrinsic-size: 300px; }
.card h2 { margin: 0 0 8px; font-size: 18px; color: var(--gold); display: flex; justify-content: space-between; align-items: baseline; }
.card h2 small { color: #c9d2f0; font-size: 13px; font-weight: 600; }
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
figure { margin: 0; position: relative; background: radial-gradient(70% 60% at 50% 45%, #4a62b8, #1d2758); border-radius: 12px; aspect-ratio: 1; display: grid; place-items: center; overflow: hidden; }
figure img, figure .fig-svg { max-width: 92%; max-height: 82%; width: auto; height: auto; }
figure .fig-svg { width: 92%; }
figcaption { position: absolute; left: 8px; top: 6px; font-size: 12px; font-weight: 700; color: #fff3d6; background: #0a0e26b3; padding: 1px 8px; border-radius: 8px; }
.atk-btn { margin-top: 10px; width: 100%; padding: 10px; border-radius: 12px; border: 2px solid #0a0e26; color: #fff; font: 700 16px system-ui, sans-serif;
  background: radial-gradient(130% 100% at 50% -10%, #ff9d7a, #dc4f4f 52%, #8f2626); box-shadow: inset 0 0 0 1.5px #e8b84a, 0 3px 0 #0a0e26; }
.atk-btn:active { transform: translateY(2px); }
</style></head><body><main>
<header><h1>Personnages redessinés</h1><p>Par le code, dans le style de Ruka la sirène. En haut, un combat chacun son tour comme dans le jeu ; en dessous, tous les personnages déjà faits.</p></header>
<section class="scene"><img src="data:image/jpeg;base64,${b64(path.join(__dirname, 'prairie.jpg'))}" alt="">
${all.map(sceneUnit).join('\n')}
</section>
<section class="gallery">
${gallery.map(card).join('\n')}
</section>
</main>
<script>
// une attaque : la classe « atk » (préfixée) sur le SVG pendant 0,8 s ; en combat, le personnage fonce un peu vers l'autre camp
function attack(svg) {
  const p = svg.dataset.p;
  svg.classList.remove(p + 'atk'); void svg.getBoundingClientRect(); svg.classList.add(p + 'atk');
  clearTimeout(svg._t); svg._t = setTimeout(() => svg.classList.remove(p + 'atk'), 800);
}
document.querySelectorAll('.atk-btn').forEach((b) => b.addEventListener('click', () => attack(document.querySelector('.new[data-p="' + b.dataset.p + '"] svg'))));
const scene = document.querySelector('.scene');
const heroes = [...scene.querySelectorAll('.unit:not(.foe)')], foes = [...scene.querySelectorAll('.foe')];
let turn = 0;
function play() {
  const side = turn % 2 === 0 ? heroes : foes, other = turn % 2 === 0 ? foes : heroes;
  const u = side[Math.floor(turn / 2) % side.length], target = other[(turn * 3) % other.length];
  const d = (u.classList.contains('foe') ? -1 : 1) * scene.clientWidth * 0.06;
  u.animate([{ transform: 'translateX(0)' }, { transform: 'translateX(' + d + 'px)', offset: 0.45 }, { transform: 'translateX(0)' }], { duration: 900, easing: 'ease-in-out' });
  attack(u.querySelector('svg'));
  setTimeout(() => { target.classList.remove('hit'); void target.offsetWidth; target.classList.add('hit'); setTimeout(() => target.classList.remove('hit'), 340); }, 380);
  turn++;
}
setInterval(play, 1500);
</script>
</body></html>`;
// --artifact : la page pour claude.ai (l'enveloppe doctype / head / body est ajoutée à la publication)
const page = flags.includes('--artifact')
  ? html.replace(/^<!doctype html>\s*<html[^>]*><head>(?:<meta [^>]*>)*/, '').replace('<title>', '<title>').replace('</style></head><body>', '</style>\n').replace('</body></html>', '')
    .replace(/^/, '').replace('<title>Personnages redessinés</title>', '<title>Personnages redessinés</title>\n<meta name="claude:viewport-fit-sides" content="cover">')
  : html;
fs.writeFileSync(out, page);
console.log(out, `${(html.length / 1024).toFixed(0)} Ko`, all.filter((u) => load(u.id).essai).length ? '(essai : Ruka à la place des dessins manquants)' : '');
