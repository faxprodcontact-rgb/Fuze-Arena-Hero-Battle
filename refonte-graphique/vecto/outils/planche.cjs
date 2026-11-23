// Planche de contrôle : plusieurs personnages (images fixes) côte à côte, avec leur id. Sert à comparer les visages.
// node planche.cjs out.png cell cols id1 id2 ...   (option : id@x0,y0,x1,y1 = seulement cette zone, ex. la tête)
const { chromium } = require('playwright');
const V = require('path').resolve(__dirname, '..') + '/';
const [out, cellS, colsS, ...ids] = process.argv.slice(2);
const cell = +cellS, cols = +colsS;
const cells = ids.map((spec) => {
  const [id, box] = spec.split('@');
  delete require.cache[require.resolve(V + id + '.cjs')];
  const h = require(V + id + '.cjs');
  const [x0, y0, x1, y1] = box ? box.split(',').map(Number) : [0, 0, h.w, h.h];
  const svg = h.svg(false).replace(/viewBox="[^"]*"/, `viewBox="${x0} ${y0} ${x1 - x0} ${y1 - y0}"`).replace(/ width="[^"]*" height="[^"]*"/, '');
  return `<div style="width:${cell}px;height:${cell + 16}px;background:linear-gradient(#2f6f9a,#173f6b);position:relative"><div style="position:absolute;inset:0 0 16px 0"><img style="width:100%;height:100%;object-fit:contain" src="data:image/svg+xml;base64,${Buffer.from(svg.replace('<svg ', '<svg width="' + cell * 2 + '" height="' + cell * 2 + '" preserveAspectRatio="xMidYMid meet" ')).toString('base64')}"></div><div style="position:absolute;bottom:0;left:0;right:0;font:11px sans-serif;color:#fff;text-align:center">${id}</div></div>`;
});
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: cols * (cell + 4) + 4, height: 400 }, deviceScaleFactor: 1 });
  await p.setContent(`<body style="margin:0;background:#111;display:grid;grid-template-columns:repeat(${cols},${cell}px);gap:4px;padding:4px">${cells.join('')}</body>`);
  await p.screenshot({ path: out, fullPage: true });
  await b.close();
  console.log(out);
})();
