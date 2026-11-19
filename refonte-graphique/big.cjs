const fs = require('fs');
const { HEROES, ENEMIES } = require('./cast.cjs');
const { SHARED_DEFS } = require('./kit.cjs');
const list = [...Object.values(HEROES), ...Object.values(ENEMIES)];
const all = [...Object.values(HEROES), ...Object.values(ENEMIES)];
let body = '';
list.forEach((c, i) => { body += `<g transform="translate(${20 + (i % 5) * 420} ${30 + Math.floor(i / 5) * 480}) scale(1.7)" filter="url(#sil)">${c.body}</g>`; });
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="2100" height="980" viewBox="0 0 2100 980"><defs>${SHARED_DEFS}<radialGradient id="orbg" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#fff" stop-opacity="0.7"/><stop offset="0.5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#001040" stop-opacity="0.5"/></radialGradient>${all.map((c) => c.defs).join('')}</defs><rect width="2100" height="980" fill="#86b872"/>${body}</svg>`;
fs.writeFileSync('big.html', `<html><body style="margin:0">${svg}</body></html>`);
