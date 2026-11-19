// Planches de référence pour l'essai d'images par IA : 5 héros (vers la droite), 5 ennemis (vers la gauche), fond uni.
const fs = require('fs');
const { HEROES, ENEMIES } = require('../cast.cjs');
const { SHARED_DEFS } = require('../kit.cjs');
const all = [...Object.values(HEROES), ...Object.values(ENEMIES)];
const defs = `<defs>${SHARED_DEFS}<radialGradient id="orbg" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#fff" stop-opacity="0.7"/><stop offset="0.5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#001040" stop-opacity="0.5"/></radialGradient>${all.map((c) => c.defs).join('')}</defs>`;
function row(list, flip, file) {
  let body = '';
  list.forEach((c, i) => {
    const x = 6 + i * 420, y = 200;
    body += flip ? `<g transform="translate(${x + 408} ${y}) scale(-1.7 1.7)" filter="url(#sil)">${c.body}</g>` : `<g transform="translate(${x} ${y}) scale(1.7)" filter="url(#sil)">${c.body}</g>`;
  });
  fs.writeFileSync(file, `<html><body style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" width="2100" height="900" viewBox="0 0 2100 900">${defs}<rect width="2100" height="900" fill="#ff00ff"/>${body}</svg></body></html>`);
}
row(Object.values(HEROES), false, 'ref-heroes.html');
row(Object.values(ENEMIES), true, 'ref-enemies.html');
