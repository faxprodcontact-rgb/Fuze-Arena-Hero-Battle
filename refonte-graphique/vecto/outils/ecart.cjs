// Mesure la fidélité d'un personnage vectoriel à son dessin d'origine (demande du propriétaire : « à chaque fois
// fidèle »). Compare la silhouette du nouveau dessin (image fixe, cadre exact) à celle de l'original :
//   - le score de recouvrement (0 à 100 %) : la part commune des deux silhouettes ;
//   - une image d'écart : l'original pâli, en ROUGE ce qui manque au nouveau dessin, en BLEU ce qui dépasse ;
//   - la liste des zones où l'écart est le plus grand (boîtes de 40 px), à corriger en premier.
// node refonte-graphique/vecto/outils/ecart.cjs <id> [sortie.png] [zoom=2]
// Repère : le deuxième renard (ronciers-1, refait par décalque) fait 95 % ; viser au moins 93 % partout.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const VECTO = path.resolve(__dirname, '..');
const [id, out = `/tmp/${id}-ecart.png`, zs] = process.argv.slice(2);
const zoom = +(zs || 2);
const hero = require(`${VECTO}/${id}.cjs`);
const svg = hero.svg(false);
const src = fs.readFileSync(`${VECTO}/originaux/${id}.jpg`).toString('base64');
const W = hero.w, H = hero.h;
// la silhouette de référence : celle relevée par outils/silhouette.py si elle existe (même règle que la découpe)
const silFile = `${VECTO}/silhouettes/${id}.json`;
const ref = fs.existsSync(silFile) ? JSON.parse(fs.readFileSync(silFile, 'utf8')).out : null;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const res = await p.evaluate(async ({ svg, src, W, H, zoom, ref }) => {
    const load = (url) => new Promise((ok) => { const i = new Image(); i.onload = () => ok(i); i.src = url; });
    const orig = await load(`data:image/jpeg;base64,${src}`);
    const mine = await load(`data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`);
    const px = (img) => { const c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d'); g.drawImage(img, 0, 0, W, H); return g.getImageData(0, 0, W, H).data; };
    const o = px(orig), m = px(mine);
    const A = new Uint8Array(W * H), B = new Uint8Array(W * H);
    // l'original : tout sauf le fond blanc/gris RELIÉ AU BORD de l'image (le blanc des yeux et des dents reste dedans)
    const isBg = (i) => { const r = o[4 * i], gg = o[4 * i + 1], bb = o[4 * i + 2]; const mx = Math.max(r, gg, bb), mn = Math.min(r, gg, bb); return mn > 200 && (mx - mn) / Math.max(mx, 1) < 0.1; };
    const bg = new Uint8Array(W * H), stack = [];
    for (let x = 0; x < W; x++) { stack.push(x, (H - 1) * W + x); }
    for (let y = 0; y < H; y++) { stack.push(y * W, y * W + W - 1); }
    while (stack.length) {
      const i = stack.pop();
      if (bg[i] || !isBg(i)) continue;
      bg[i] = 1;
      const x = i % W, y = (i - x) / W;
      if (x > 0) stack.push(i - 1); if (x < W - 1) stack.push(i + 1); if (y > 0) stack.push(i - W); if (y < H - 1) stack.push(i + W);
    }
    let R = null;
    if (ref) { const c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d'); g.fillStyle = '#000'; g.fill(new Path2D(ref), 'evenodd'); R = g.getImageData(0, 0, W, H).data; }
    for (let i = 0; i < W * H; i++) {
      A[i] = R ? (R[4 * i + 3] > 128 ? 1 : 0) : (bg[i] ? 0 : 1);
      B[i] = m[4 * i + 3] > 128 ? 1 : 0; // le nouveau : ce qui est opaque
    }
    let inter = 0, uni = 0, miss = 0, extra = 0;
    for (let i = 0; i < W * H; i++) { inter += A[i] & B[i]; uni += A[i] | B[i]; miss += A[i] & !B[i]; extra += B[i] & !A[i]; }
    // les zones les plus en écart (boîtes de 40 px)
    const S = 40, zones = [];
    for (let y = 0; y < H; y += S) for (let x = 0; x < W; x += S) {
      let e = 0;
      for (let yy = y; yy < Math.min(H, y + S); yy++) for (let xx = x; xx < Math.min(W, x + S); xx++) { const i = yy * W + xx; e += A[i] !== B[i] ? 1 : 0; }
      if (e > S * S * 0.08) zones.push([x, y, e]);
    }
    zones.sort((a, b) => b[2] - a[2]);
    // l'image d'écart
    const c = document.createElement('canvas'); c.width = W * zoom; c.height = H * zoom;
    const g = c.getContext('2d'); g.imageSmoothingEnabled = false;
    const d = g.createImageData(W, H);
    for (let i = 0; i < W * H; i++) {
      let r = 255 - (255 - o[4 * i]) * 0.35, gg = 255 - (255 - o[4 * i + 1]) * 0.35, bb = 255 - (255 - o[4 * i + 2]) * 0.35;
      if (A[i] && !B[i]) { r = 230; gg = 20; bb = 20; } else if (B[i] && !A[i]) { r = 20; gg = 80; bb = 240; }
      d.data[4 * i] = r; d.data[4 * i + 1] = gg; d.data[4 * i + 2] = bb; d.data[4 * i + 3] = 255;
    }
    const t = document.createElement('canvas'); t.width = W; t.height = H; t.getContext('2d').putImageData(d, 0, 0);
    g.drawImage(t, 0, 0, W * zoom, H * zoom);
    return { score: inter / uni, miss: miss / uni, extra: extra / uni, zones: zones.slice(0, 8), png: c.toDataURL('image/png') };
  }, { svg, src, W, H, zoom, ref });
  fs.writeFileSync(out, Buffer.from(res.png.split(',')[1], 'base64'));
  await b.close();
  console.log(`${id} : recouvrement ${(res.score * 100).toFixed(1)} % (manque ${(res.miss * 100).toFixed(1)} %, dépasse ${(res.extra * 100).toFixed(1)} %)`);
  console.log('zones à reprendre (x, y, boîte 40 px) :', res.zones.map(([x, y]) => `${x},${y}`).join('  '));
  console.log(out);
})();
