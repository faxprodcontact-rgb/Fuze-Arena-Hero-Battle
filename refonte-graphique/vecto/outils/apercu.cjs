// Aperçu d'un personnage vectoriel à côté de son dessin d'origine.
// node refonte-graphique/vecto/outils/apercu.cjs <id> <zoom> <x0> <y0> <x1> <y1> <sortie.png> [mode]
//   x0..y1 = la zone à montrer (coordonnées du dessin d'origine) ; « - - - - » = tout le personnage.
//   mode « duo » (défaut) : dessin actuel du jeu | nouveau dessin (fond bleu), puis nouveau à 50 % sur l'original | original
//   mode « seul » : le nouveau seulement, sur fond bleu ; « calque » : nouveau à 50 % sur l'original | original
// Économie : préférer « seul » ou « calque » sur une petite zone ; le « duo » entier une fois à la fin.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const VECTO = path.resolve(__dirname, '..');
const REPO = path.resolve(VECTO, '../..');
const [id, zs, ...rest] = process.argv.slice(2);
const zoom = +(zs || 2);
const box = rest.slice(0, 4).map(Number);
const out = rest[4] || `${id}-apercu.png`;
const mode = rest[5] || 'duo';
const hero = require(`${VECTO}/${id}.cjs`);
const svg = hero.svg(false);
const src = fs.readFileSync(`${VECTO}/originaux/${id}.jpg`).toString('base64');
const cur = fs.readFileSync(`${REPO}/public/art/p/${id}.webp`).toString('base64');
const [x0, y0, x1, y1] = box.length === 4 && box.every((v) => !isNaN(v)) ? box : [0, 0, hero.w, hero.h];
const w = Math.round((x1 - x0) * zoom), h = Math.round((y1 - y0) * zoom);
const cell = (inner, bg) => `<div style="position:relative;width:${w}px;height:${h}px;overflow:hidden;background:${bg};flex:none"><div style="position:absolute;left:${-x0 * zoom}px;top:${-y0 * zoom}px;width:${hero.w * zoom}px;height:${hero.h * zoom}px">${inner}</div></div>`;
const img = (b64, type, extra = '') => `<img src="data:image/${type};base64,${b64}" style="position:absolute;inset:0;width:100%;height:100%;${extra}">`;
const vec = (extra = '') => `<div style="position:absolute;inset:0;${extra}">${svg.replace('<svg ', '<svg style="width:100%;height:100%;display:block" ')}</div>`;
const bg = 'linear-gradient(#2f6f9a,#173f6b)';
const cells = mode === 'seul' ? [cell(vec(), bg)]
  : mode === 'calque' ? [cell(img(src, 'jpeg') + vec('opacity:.5'), '#fff'), cell(img(src, 'jpeg'), '#fff')]
  : [cell(img(cur, 'webp'), bg), cell(vec(), bg), cell(img(src, 'jpeg') + vec('opacity:.5'), '#fff'), cell(img(src, 'jpeg'), '#fff')];
const cols = mode === 'seul' ? 1 : 2;
const html = `<body style="margin:0;background:#111;display:flex;gap:6px;padding:6px;flex-wrap:wrap;width:${w * cols + 6 * (cols - 1)}px">${cells.join('')}</body>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: Math.ceil(w * cols + 6 * (cols + 1)), height: 400 }, deviceScaleFactor: 1 });
  await p.setContent(html);
  await p.screenshot({ path: out, fullPage: true });
  await b.close();
  console.log(out, svg.length, 'octets');
})();
