const fs = require('fs');
const { HEROES, ENEMIES } = require('./cast.cjs');
const { SHARED_DEFS } = require('./kit.cjs');
const all = [...Object.values(HEROES), ...Object.values(ENEMIES)];
let body = '';
all.forEach((c, i) => {
  const col = i % 5, row = Math.floor(i / 5);
  const x = 20 + col * 330, y = 20 + row * 360;
  body += row === 0 ? `<g transform="translate(${x} ${y}) scale(1.3)" filter="url(#sil)">${c.body}</g>` : `<g transform="translate(${x + 320} ${y}) scale(-1.3 1.3)" filter="url(#sil)">${c.body}</g>`;
});
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="740" viewBox="0 0 1680 740"><defs>${SHARED_DEFS}<radialGradient id="orbg" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#fff" stop-opacity="0.7"/><stop offset="0.5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#001040" stop-opacity="0.5"/></radialGradient>${all.map((c) => c.defs).join('')}</defs><rect width="1680" height="740" fill="#86b872"/>${body}</svg>`;
fs.writeFileSync('sheet.html', `<html><body style="margin:0">${svg}</body></html>`);
