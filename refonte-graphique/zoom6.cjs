// Vue en grand pour le contrôle héros par héros :  node zoom6.cjs "fire:0,fire:1" sortie.html [colonnes]
const fs = require('fs');
const { all } = require('./heroes6.cjs');
const { SHARED_DEFS } = require('./kit.cjs');
const want = process.argv[2].split(',');
const list = all(want), cols = +(process.argv[4] || 3), K = 1.95, CW = 2070 / cols, CH = 560;
let body = '', defs = '';
want.forEach((key, n) => {
  const [el, i] = key.split(':'), x = list.find((h) => h.element === el && h.index === +i), col = n % cols, row = Math.floor(n / cols), k = K * Math.min(1.08, x.scale);
  defs += x.fig.defs;
  const tr = `translate(${col * CW + CW / 2 - 106 * k} ${row * CH + CH - 40 - 228 * k}) scale(${k})`;
  body += `<g transform="${tr}">${x.fig.glow}</g><g transform="${tr}" filter="url(#sil)">${x.fig.body}</g><text x="${col * CW + 16}" y="${row * CH + 30}" font-size="22" font-weight="700" fill="#241a2c">${i} · ${x.name}</text>`;
});
const W = CW * cols, Hh = CH * Math.ceil(want.length / cols);
fs.writeFileSync(process.argv[3], `<html><head><meta charset="utf-8"></head><body style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${Hh}" viewBox="0 0 ${W} ${Hh}" font-family="system-ui"><defs>${SHARED_DEFS}${defs}</defs><rect width="${W}" height="${Hh}" fill="#d9e2d0"/>${body}</svg></body></html>`);
console.log(W, Hh);
