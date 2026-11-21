// Planches de l'interface peinte (22/11/2026) : cadres, barres, boutons, cases de héros et d'équipement, à faire peindre par Hailuo.
//   node planches-ui.cjs cadres|boutons sortie.png
// Croquis simples, de face, sans texte : Hailuo fait la matière (bois sculpté, parchemin, or). Format 4K 16:9.
// Les emplacements de chaque pièce sont écrits dans ui-pieces.json : la découpe du rendu s'en sert.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const [, , which, out] = process.argv;
const W = 3840, H = 2160;
const INK = '#2a1c12', WOOD = 'linear-gradient(#94683a,#5c3a1e)', WOOD_D = 'linear-gradient(#6e4826,#472b14)', GOLD = '#e3b548', PARCH = '#ecd9a8';
const pieces = {};
const box = (name, x, y, w, h, style, inner = '') => { pieces[name] = [x, y, w, h]; return `<div style="position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${h}px;box-sizing:border-box;${style}">${inner}</div>`; };
const abs = (style, inner = '') => `<div style="position:absolute;box-sizing:border-box;${style}">${inner}</div>`;
const diamond = (x, y, s, col = GOLD) => abs(`left:${x - s / 2}px;top:${y - s / 2}px;width:${s}px;height:${s}px;background:${col};border:8px solid ${INK};transform:rotate(45deg)`);

function cadres() {
  let s = '';
  // 1. grande fenêtre : cadre de bois, coins d'or, parchemin, bandeau de titre en haut
  s += box('window', 140, 130, 1000, 1900, `background:${WOOD};border:12px solid ${INK};border-radius:60px`,
    abs(`inset:50px;background:${PARCH};border:10px solid ${INK};border-radius:30px;box-shadow:0 0 0 14px ${GOLD}`)
    + abs(`left:38px;right:38px;top:38px;height:230px;background:${WOOD_D};border:10px solid ${INK};border-radius:30px 30px 0 0;box-shadow:inset 0 -16px 0 ${GOLD}`)
    + diamond(60, 60, 80) + diamond(916, 60, 80) + diamond(60, 1816, 80) + diamond(916, 1816, 80) + diamond(488, 152, 70));
  // 2. panneau en creux
  s += box('inset', 1420, 160, 1000, 720, `background:#dfc58c;border:14px solid #6b4521;border-radius:44px;box-shadow:inset 0 14px 0 #c9ab6e`);
  // 3. plaque du chapitre : pancarte suspendue, rubans de chaque côté
  s += box('plaque', 1420, 1180, 1000, 520, '',
    abs(`left:240px;top:0;width:14px;height:120px;background:#8a8f98;border:5px solid ${INK}`) + abs(`right:240px;top:0;width:14px;height:120px;background:#8a8f98;border:5px solid ${INK}`)
    + abs(`left:0;top:190px;width:200px;height:200px;background:#c8860f;border:10px solid ${INK};clip-path:polygon(0 0,100% 0,100% 100%,0 100%,35% 50%)`)
    + abs(`right:0;top:190px;width:200px;height:200px;background:#c8860f;border:10px solid ${INK};clip-path:polygon(0 0,100% 0,65% 50%,100% 100%,0 100%)`)
    + abs(`left:110px;right:110px;top:110px;height:360px;background:${WOOD};border:12px solid ${INK};border-radius:40px;box-shadow:inset 0 0 0 16px ${GOLD}`)
    + diamond(500, 110, 70));
  // 4. barre (haut et bas de l'écran) : planche de bois, filet d'or, clous
  s += box('bar', 2620, 200, 1080, 300, `background:${WOOD};border:12px solid ${INK};box-shadow:inset 0 -22px 0 ${GOLD}`,
    diamond(60, 130, 50) + diamond(996, 130, 50));
  // 5. ruban de titre (victoire)
  s += box('ribbon', 2620, 820, 1080, 340, '',
    abs(`left:0;top:90px;width:220px;height:220px;background:#a83232;border:10px solid ${INK};clip-path:polygon(0 0,100% 0,100% 100%,0 100%,35% 50%)`)
    + abs(`right:0;top:90px;width:220px;height:220px;background:#a83232;border:10px solid ${INK};clip-path:polygon(0 0,100% 0,65% 50%,100% 100%,0 100%)`)
    + abs(`left:120px;right:120px;top:20px;height:250px;background:#dc4f4f;border:12px solid ${INK};border-radius:24px;box-shadow:inset 0 16px 0 ${GOLD},inset 0 -16px 0 ${GOLD}`));
  // 6. dalle de pierre (étages de la tour)
  s += box('slab', 2620, 1420, 1080, 240, `background:linear-gradient(#cfc9d9,#9d95ad);border:12px solid ${INK};border-radius:30px`,
    abs(`left:120px;top:60px;width:160px;height:10px;background:${INK}`) + abs(`right:200px;bottom:70px;width:120px;height:10px;background:${INK}`));
  return s;
}

function boutons() {
  const cw = W / 7, ch = H / 4;
  const cell = (name, i, w, h, style, inner) => box(name, Math.round((i % 7) * cw + (cw - w) / 2), Math.round(Math.floor(i / 7) * ch + (ch - h) / 2), w, h, style, inner);
  let s = '';
  // rangée 1 : boutons larges
  [['green', '#3fae5a', '#2a8442'], ['blue', '#3f86e0', '#2a5fb5'], ['gold', '#f0b530', '#c8860f'], ['red', '#dc4f4f', '#a83232'], ['purple', '#9360e0', '#6b3fb5'], ['grey', '#9a9aa6', '#74747f'], ['wood', '#e9d3a0', '#c9ab6e']]
    .forEach(([n, a, b], i) => { s += cell('btn-' + n, i, 470, 170, `background:linear-gradient(${a} 55%,${b});border:10px solid ${INK};border-radius:50px;box-shadow:inset 0 0 0 10px ${n === 'grey' ? '#c9c9d2' : GOLD}`, abs(`left:40px;right:40px;top:26px;height:40px;border-radius:20px;background:#ffffff66`)); });
  // rangée 2 : petites pièces
  s += cell('medal', 7, 380, 380, `background:#2f5a94;border:12px solid ${INK};border-radius:50%;box-shadow:inset 0 0 0 30px ${GOLD},inset 0 0 0 40px ${INK}`);
  s += cell('close', 8, 300, 300, `background:#dc4f4f;border:12px solid ${INK};border-radius:60px;box-shadow:inset 0 0 0 14px ${GOLD}`, abs(`left:60px;right:60px;top:126px;height:34px;background:#fff;transform:rotate(45deg);border-radius:12px`) + abs(`left:60px;right:60px;top:126px;height:34px;background:#fff;transform:rotate(-45deg);border-radius:12px`));
  s += cell('back', 9, 300, 300, `background:${WOOD};border:12px solid ${INK};border-radius:60px;box-shadow:inset 0 0 0 14px ${GOLD}`, `<svg viewBox="0 0 100 100" style="position:absolute;inset:0"><path d="M60 26 L34 50 L60 74" fill="none" stroke="#fff" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/></svg>`);
  s += cell('plus', 10, 260, 260, `background:#3fae5a;border:12px solid ${INK};border-radius:60px`, abs(`left:50px;right:50px;top:104px;height:30px;background:#fff;border-radius:10px`) + abs(`top:50px;bottom:50px;left:104px;width:30px;background:#fff;border-radius:10px`));
  s += cell('pill', 11, 470, 150, `background:#2a1c12;border:10px solid ${INK};border-radius:75px;box-shadow:inset 0 0 0 8px ${GOLD}`);
  s += cell('gauge', 12, 480, 110, `background:#3a2a1c;border:10px solid ${INK};border-radius:55px;box-shadow:inset 0 0 0 8px ${GOLD}`, diamond(0, 45, 60) + diamond(460, 45, 60));
  s += cell('check', 13, 260, 260, `background:#3fae5a;border:12px solid ${INK};border-radius:50%;box-shadow:inset 0 0 0 12px #c8f5d2`, `<svg viewBox="0 0 100 100" style="position:absolute;inset:0"><path d="M28 52 L44 68 L74 34" fill="none" stroke="#fff" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/></svg>`);
  // rangée 3 : cadres des cases de héros (4 raretés), cadre d'avatar, onglets
  [['common', '#9aa0b5', '#c9ced6'], ['rare', '#3d8bff', '#9cc8ff'], ['epic', '#a35cff', '#d3a8ff'], ['legendary', '#f0b530', '#ffe58a']].forEach(([n, c, l], i) => {
    s += cell('hero-' + n, 14 + i, 380, 500, `background:radial-gradient(90% 70% at 50% 38%,${l},${c} 55%,#0008 140%);border:12px solid ${INK};border-radius:44px;box-shadow:inset 0 0 0 22px ${c},inset 0 0 0 30px ${INK}`,
      diamond(30, 30, 46, l) + diamond(326, 30, 46, l) + diamond(30, 446, 46, l) + diamond(326, 446, 46, l) + (n === 'legendary' ? `<svg viewBox="0 0 100 100" style="position:absolute;left:128px;top:-70px;width:100px;height:100px"><path d="M50 6 L62 38 L96 40 L69 60 L79 94 L50 74 L21 94 L31 60 L4 40 L38 38 Z" fill="#ffe58a" stroke="${INK}" stroke-width="7"/></svg>` : ''));
  });
  s += cell('avatar', 18, 380, 380, `background:radial-gradient(circle at 50% 35%,#8fc0ee,#2f5a94);border:12px solid ${INK};border-radius:50%;box-shadow:inset 0 0 0 26px ${GOLD},inset 0 0 0 36px ${INK}`, diamond(178, 6, 60) + diamond(178, 350, 60));
  s += cell('tab-on', 19, 440, 170, `background:linear-gradient(#ffd978,#f0b530 55%,#c8860f);border:10px solid ${INK};border-radius:36px 36px 0 0`, abs(`left:36px;right:36px;top:22px;height:34px;border-radius:17px;background:#ffffff80`));
  s += cell('tab-off', 20, 440, 170, `background:${WOOD_D};border:10px solid ${INK};border-radius:36px 36px 0 0`);
  // rangée 4 : cadres des cases d'équipement (6 raretés) ; la dernière case reste vide
  [['#9aa0b5', '#c9ced6'], ['#4cc46b', '#a6e08f'], ['#3d8bff', '#9cc8ff'], ['#a35cff', '#d3a8ff'], ['#f0b530', '#ffe58a'], ['#e0404e', '#ff9a8a']].forEach(([c, l], i) => {
    s += cell('item-' + i, 21 + i, 400, 400, `background:radial-gradient(85% 75% at 50% 40%,${l},${c} 60%,#0008 150%);border:12px solid ${INK};border-radius:60px;box-shadow:inset 0 0 0 20px ${c},inset 0 0 0 28px ${INK}`,
      i >= 3 ? diamond(188, 6, 50, l) : '');
  });
  return s;
}

const body = which === 'cadres' ? cadres() : which === 'boutons' ? boutons() : null;
if (!body) throw new Error('planche inconnue : ' + which);
const html = `<html><body style="margin:0;width:${W}px;height:${H}px;position:relative;background:#fff;overflow:hidden">${body}</body></html>`;
(async () => {
  const tmp = path.join(require('os').tmpdir(), `planche-ui-${which}.html`);
  fs.writeFileSync(tmp, html);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: W, height: H } });
  await pg.goto('file://' + tmp); await pg.waitForTimeout(400); await pg.screenshot({ path: out }); await b.close();
  const file = path.join(__dirname, 'ui-pieces.json');
  const all = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : {};
  all[which] = pieces;
  fs.writeFileSync(file, JSON.stringify(all, null, 1));
  console.log(out, Object.keys(pieces).length + ' pièces');
})();
