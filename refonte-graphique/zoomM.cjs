// Monstres : vue en grand (contrôle) ou planche d'une famille.
//   node zoomM.cjs abysses sortie.html            → la famille en grand (3 par rangée)
//   node zoomM.cjs abysses sortie.html planche    → la planche à montrer (6 sur une rangée, nom et place)
const fs = require('fs');
const { all, FAMILIES, SLOT_FR, MON_DEFS } = require('./mon6.cjs');
const { SHARED_DEFS } = require('./kit.cjs');
const key = process.argv[2], sheet = process.argv[4] === 'planche';
const list = all([key]), fam = FAMILIES.find((x) => x.key === key);
const BG = { fire: '#f1d6c2', wind: '#d3ece4', water: '#cfe0f4', earth: '#e2dcc0' }[fam.element];
const cols = sheet ? 6 : 3, CW = sheet ? 350 : 690, CH = sheet ? 470 : 600, K = sheet ? 1.15 : 2.1, TOP = sheet ? 90 : 0;
let body = '', defs = '';
list.forEach((x, n) => {
  const col = n % cols, row = Math.floor(n / cols), k = K * Math.min(sheet ? 1.2 : 1.12, x.scale), ox = (sheet ? 20 : 0) + col * CW, oy = TOP + row * CH, gy = oy + CH - (sheet ? 104 : 40);
  defs += x.fig.defs;
  const tr = `translate(${ox + CW / 2 - 106 * k} ${gy - 228 * k}) scale(${k})`;
  if (sheet) body += `<rect x="${ox + 8}" y="${oy + 6}" width="${CW - 16}" height="${CH - 14}" rx="18" fill="#fff" opacity="0.45"/><rect x="${ox + 8}" y="${oy + CH - 96}" width="${CW - 16}" height="88" rx="18" fill="${x.slot === 'boss' ? '#e6a020' : x.slot === 'elite' ? '#9a4cf0' : '#8c95a6'}" opacity="0.2"/>`;
  body += `<ellipse cx="${ox + CW / 2}" cy="${gy}" rx="${66 * k}" ry="${11 * k}" fill="#1a1c2c" opacity="0.22"/>` + (x.slot === 'boss' || x.slot === 'elite' ? `<g transform="${tr}" filter="url(#${x.slot === 'boss' ? 'auraBo' : 'auraEl'})">${x.fig.body}</g>` : '') + `<g transform="${tr}">${x.fig.glow}</g><g transform="${tr}" filter="url(#sil2)">${x.fig.body}</g><g transform="${tr}">${x.fig.fx}</g>`;
  body += sheet ? `<text x="${ox + CW / 2}" y="${oy + CH - 62}" text-anchor="middle" font-size="24" font-weight="800" fill="#241a2c">${x.name.replace(/&/g, '&amp;')}</text><text x="${ox + CW / 2}" y="${oy + CH - 34}" text-anchor="middle" font-size="18" font-weight="700" fill="#4a4050">${SLOT_FR[x.slot]}</text>`
    : `<text x="${ox + 16}" y="${oy + 30}" font-size="22" font-weight="700" fill="#241a2c">${x.index} · ${x.name.replace(/&/g, '&amp;')} (${SLOT_FR[x.slot]})</text>`;
});
const W = (sheet ? 40 : 0) + CW * cols, H = TOP + CH * Math.ceil(list.length / cols) + (sheet ? 20 : 0);
const title = sheet ? `<text x="30" y="62" font-size="44" font-weight="900" fill="#241a2c">${fam.name.toUpperCase().replace(/&/g, '&amp;')}</text>` : '';
fs.writeFileSync(process.argv[3], `<html><head><meta charset="utf-8"></head><body style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="system-ui, 'Segoe UI', sans-serif"><defs>${SHARED_DEFS}${MON_DEFS}${defs}</defs><rect width="${W}" height="${H}" fill="${sheet ? BG : '#d9e2d0'}"/>${title}${body}</svg></body></html>`);
console.log(W, H);
