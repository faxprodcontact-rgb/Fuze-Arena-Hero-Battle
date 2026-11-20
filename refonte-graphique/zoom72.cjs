// Vue en grand de quelques héros pour le contrôle de cohérence :  node zoom72.cjs "fire:4,wind:9" sortie.html
const fs = require('fs');
const { all } = require('./heroes72.cjs');
const { SHARED_DEFS } = require('./kit.cjs');
const want = process.argv[2].split(',').map((s) => s.split(':'));
const list = all(), K = 1.95, CW = 520, CH = 560;
let body = '', defs = '';
want.forEach(([el, i], n) => {
  const x = list.find((h) => h.element === el && h.index === +i), col = n % 4, row = Math.floor(n / 4), k = K * Math.min(1.05, x.scale);
  defs += x.fig.defs;
  const tr = `translate(${col * CW + CW / 2 - 106 * k} ${row * CH + CH - 50 - 228 * k}) scale(${k})`;
  body += `<g transform="${tr}">${x.fig.glow}</g><g transform="${tr}" filter="url(#sil)">${x.fig.body}</g><text x="${col * CW + 16}" y="${row * CH + 30}" font-size="22" font-weight="700" fill="#241a2c">${x.name}</text>`;
});
const W = CW * 4, H = CH * Math.ceil(want.length / 4);
fs.writeFileSync(process.argv[3], `<html><head><meta charset="utf-8"></head><body style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="system-ui"><defs>${SHARED_DEFS}${defs}</defs><rect width="${W}" height="${H}" fill="#d9e2d0"/>${body}</svg></body></html>`);
console.log(W, H);
