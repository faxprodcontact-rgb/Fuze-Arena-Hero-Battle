// Planche d'animation d'un personnage vectoriel : 6 instants du repos, 6 instants de l'attaque, et la taille du jeu.
// node refonte-graphique/vecto/outils/anim.cjs <id> <sortie.png> [zoom=0.5]
// Repos : t = 0, 0.7, 1.4, 2.1, 2.8, 3.5 s. Attaque (classe « atk » sur le <svg>) : t = 0, 0.15, 0.3, 0.45, 0.6, 0.75 s.
// Dernière case : le personnage à la taille du jeu (environ 70 px de haut), à l'endroit et retourné.
// Économie : zoom 0.5 suffit pour voir un trou ou un morceau détaché ; zoomer ensuite seulement là où il y a un doute.
const { chromium } = require('playwright');
const path = require('path');
const VECTO = path.resolve(__dirname, '..');
const [id, out, zs] = process.argv.slice(2);
const zoom = +(zs || 0.5);
const hero = require(`${VECTO}/${id}.cjs`);
const svg = hero.svg(true);
const pad = hero.pad ?? 24;
const W = Math.round((hero.w + 2 * pad) * zoom), H = Math.round((hero.h + 2 * pad) * zoom);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await p.setContent(`<body style="margin:0;background:#111"><div style="width:${W}px;height:${H}px;background:linear-gradient(#2f6f9a,#173f6b)">${svg.replace('<svg ', '<svg id="fig" style="width:100%;height:100%;display:block" ')}</div></body>`);
  await p.waitForTimeout(200);
  const shots = [];
  const at = async (t, label) => {
    await p.evaluate((t) => document.getAnimations().forEach((a) => { a.pause(); a.currentTime = t * 1000; }), t);
    shots.push({ buf: await p.screenshot(), label });
  };
  for (const t of [0, 0.7, 1.4, 2.1, 2.8, 3.5]) await at(t, `repos ${t}s`);
  await p.evaluate(() => document.getElementById('fig').classList.add('atk'));
  await p.waitForTimeout(50);
  for (const t of [0, 0.15, 0.3, 0.45, 0.6, 0.75]) await at(t, `attaque ${t}s`);
  const small = 70 / hero.h, sw = (hero.w + 2 * pad) * small;
  await p.setContent(`<body style="margin:0;background:linear-gradient(#9fd2f0 0,#cfeaf7 55%,#7cbf5a 55%,#5c9e40 100%);width:${W}px;height:${H}px;display:grid;place-items:center">
    <div style="display:flex;gap:30px;align-items:flex-end"><div style="width:${sw}px">${svg.replace('<svg ', '<svg style="width:100%;height:auto;display:block" ')}</div>
    <div style="width:${sw}px;transform:scaleX(-1)">${svg.replace('<svg ', '<svg style="width:100%;height:auto;display:block" ')}</div></div></body>`);
  await p.waitForTimeout(150);
  shots.push({ buf: await p.screenshot(), label: 'taille du jeu' });
  const q = await b.newPage({ viewport: { width: (W + 6) * 4, height: 300 }, deviceScaleFactor: 1 });
  const cells = shots.map((s) => `<div style="position:relative;flex:none"><img src="data:image/png;base64,${s.buf.toString('base64')}" style="display:block;width:${W}px;height:${H}px"><span style="position:absolute;left:4px;top:3px;background:#000b;padding:1px 6px;color:#ffe08a;font:bold 12px sans-serif">${s.label}</span></div>`).join('');
  await q.setContent(`<body style="margin:0;background:#222;display:flex;flex-wrap:wrap;gap:6px;width:${(W + 6) * 4 - 6}px">${cells}</body>`);
  await q.screenshot({ path: out, fullPage: true });
  await b.close();
  console.log(out);
})();
