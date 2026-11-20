// Planche d'un élément : 18 héros (6 × 3) avec nom provisoire, rareté, rôle, chef, inspiration.
//   node sheet72.cjs fire [sortie.html]
const fs = require('fs');
const { all } = require('./heroes6.cjs');
const { SHARED_DEFS } = require('./kit.cjs');
const { HERO_DEFS } = require('./fig6.cjs');
const el = process.argv[2] || 'fire';
const BG = { fire: '#f1d6c2', wind: '#d3ece4', water: '#cfe0f4', earth: '#e2dcc0' }[el];
const TITLE = { fire: 'FEU', wind: 'VENT', water: 'EAU', earth: 'TERRE' }[el];
const RAR = { common: ['Commun', '#8c95a6'], rare: ['Rare', '#3f7ff0'], epic: ['Épique', '#9a4cf0'], legendary: ['Légendaire', '#e6a020'] };
const ROLE = { protector: 'Protecteur', warrior: 'Guerrier', marksman: 'Tireur', assassin: 'Assassin', healer: 'Soigneur', support: 'Soutien' };
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const list = all().filter((x) => x.element === el);
const CW = 350, CH = 470, K = 1.2, COLS = 6, W = CW * COLS + 40, H = CH * 3 + 110;
let body = '', defs = '';
for (const x of list) {
  const col = x.index % COLS, row = Math.floor(x.index / COLS), ox = 20 + col * CW, oy = 90 + row * CH, k = K * x.scale;
  const [rn, rc] = RAR[x.rarity];
  defs += x.fig.defs;
  body += `<rect x="${ox + 8}" y="${oy + 6}" width="${CW - 16}" height="${CH - 14}" rx="18" fill="#fff" opacity="0.45"/><rect x="${ox + 8}" y="${oy + CH - 96}" width="${CW - 16}" height="88" rx="18" fill="${rc}" opacity="0.2"/>`;
  const tr = `translate(${ox + CW / 2 - 106 * k} ${oy + CH - 104 - 228 * k}) scale(${k})`;
  body += `<ellipse cx="${ox + CW / 2}" cy="${oy + CH - 104}" rx="${70 * k}" ry="${12 * k}" fill="#2a1c10" opacity="0.22"/>`;
  const au = { epic: 'auraE', legendary: 'auraL' }[x.rarity];
  body += (au ? `<g transform="${tr}" filter="url(#${au})">${x.fig.body}</g>` : '') + `<g transform="${tr}">${x.fig.glow}</g><g transform="${tr}" filter="url(#silH)">${x.fig.body}</g><g transform="${tr}">${x.fig.fx}</g>`;
  body += `<text x="${ox + CW / 2}" y="${oy + CH - 66}" text-anchor="middle" font-size="26" font-weight="800" fill="#241a2c">${x.leader ? '♛ ' : ''}${esc(x.name)}</text>`;
  body += `<text x="${ox + CW / 2}" y="${oy + CH - 42}" text-anchor="middle" font-size="18" font-weight="700" fill="${rc}">${rn} · ${ROLE[x.role]}</text>`;
  body += `<text x="${ox + CW / 2}" y="${oy + CH - 20}" text-anchor="middle" font-size="14" fill="#4a4050">${esc(x.from)}</text>`;
}
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="system-ui, 'Segoe UI', sans-serif"><defs>${SHARED_DEFS}${HERO_DEFS}<filter id="auraE" x="-40%" y="-40%" width="180%" height="180%"><feMorphology in="SourceAlpha" operator="dilate" radius="3"/><feGaussianBlur stdDeviation="6" result="b"/><feFlood flood-color="#b06cff" flood-opacity="0.85"/><feComposite in2="b" operator="in"/></filter><filter id="auraL" x="-40%" y="-40%" width="180%" height="180%"><feMorphology in="SourceAlpha" operator="dilate" radius="4"/><feGaussianBlur stdDeviation="7" result="b"/><feFlood flood-color="#ffc94a" flood-opacity="0.95"/><feComposite in2="b" operator="in"/></filter>${defs}</defs><rect width="${W}" height="${H}" fill="${BG}"/><text x="30" y="62" font-size="46" font-weight="900" fill="#241a2c">${TITLE}</text><text x="${W - 30}" y="58" text-anchor="end" font-size="20" fill="#4a4050">noms provisoires · ♛ = chef de section</text>${body}</svg>`;
fs.writeFileSync(process.argv[3] || `sheet-${el}.html`, `<html><head><meta charset="utf-8"></head><body style="margin:0">${svg}</body></html>`);
console.log(el, list.length, 'héros', W + '×' + H);
