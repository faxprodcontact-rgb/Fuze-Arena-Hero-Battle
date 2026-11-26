// Les boutons « Pierre de l'arène » (choisis par le propriétaire le 26/11/2026, parmi les 4 familles de
// refonte-graphique/ui-moderne/boutons/) : une dalle taillée aux coins éclatés, comme le sol de l'arène. L'action principale
// est une pierre sombre où brûle une lumière (lettres qui luisent) ; les autres, une pierre claire
// gravée. Chaque bouton est un dessin vectoriel (SVG) fait ici par le code :
// - `installButtons()` (main.tsx, au lancement) pose les dessins dans des variables CSS `--bt-pierre-<teinte>-<taille>[-down]`
//   et `--bt-pierre-rond-<teinte>[-down]`, et les règles qui les relient aux classes `bt-<teinte>` + `bt-<taille>` ;
// - style.css (« Boutons ») les pose sur le ::before des `.bt` en « 3 morceaux » (bouts fixes, milieu étiré) : un bouton peut
//   avoir n'importe quelle largeur ;
// - au combat, hud-art.tsx en fait des textures Phaser (`pierreSvg`, `roundSvg`).
// Règles : une seule lumière en haut à droite (arêtes claires en haut et à droite, ombre en bas et à gauche), un seul contour
// sombre autour de chaque bouton, pas de rayures ni de hachures, des signes dessinés (jamais de lettres).

const INK = '#1c0f26';

/** Les tailles : hauteur totale (épaisseur comprise), épaisseur (la « lèvre » qui disparaît quand on appuie), largeur d'un bout. */
export const SIZES = {
  rail: { h: 46, lip: 0, L: 17, fs: 15 },
  xxl: { h: 84, lip: 7, L: 23, fs: 28 },
  xl: { h: 72, lip: 6, L: 21, fs: 27 },
  l: { h: 62, lip: 6, L: 20, fs: 25 },
  m: { h: 48, lip: 5, L: 17, fs: 18 },
  s: { h: 38, lip: 4, L: 14, fs: 15 },
} as const;
export type BtSize = keyof typeof SIZES;

/** Les teintes : la pierre [arête claire, haut, bas, épaisseur] et sa lumière intérieure (rien = pierre éteinte). */
type Stone = { st: [string, string, string, string]; light?: string; core?: string };
export type BtTone = 'basalte' | 'or' | 'arcane' | 'feu' | 'eau' | 'terre' | 'vent' | 'ardoise' | 'galet' | 'creux' | 'off';
export const PIERRE: Record<BtTone, Stone> = {
  basalte: { st: ['#8a86a8', '#4d4a6a', '#2e2c47', '#1f1d33'], light: '#ffb53a', core: '#fff1b8' },
  or: { st: ['#a8927c', '#5c4a4c', '#382a2e', '#261c20'], light: '#ffd23a', core: '#fffbe0' },
  arcane: { st: ['#9a8ab8', '#4f4270', '#2e2549', '#1f1834'], light: '#b07bff', core: '#f3e6ff' },
  feu: { st: ['#9a7f8e', '#56404f', '#33232f', '#22161f'], light: '#ff6a2a', core: '#ffe0a0' },
  eau: { st: ['#7f93ad', '#3f4f6c', '#232f47', '#161f33'], light: '#2fa4ff', core: '#d4f6ff' },
  terre: { st: ['#a08e78', '#5b4c3f', '#372c24', '#251d17'], light: '#f0a02f', core: '#fff0c0' },
  vent: { st: ['#7fa497', '#3f5e55', '#243a34', '#172722'], light: '#3fd884', core: '#dcffe6' },
  ardoise: { st: ['#f6eedc', '#d3c6ad', '#a89a80', '#6f624f'] },
  galet: { st: ['#8a86a8', '#4d4a6a', '#2e2c47', '#1f1d33'] },
  creux: { st: ['#57536f', '#2a2840', '#1d1b2f', '#141224'] },
  off: { st: ['#7a7790', '#4f4c63', '#38364a', '#28263a'] },
};

/** La pierre allumée de chaque élément (filtres, pastilles d'élément). */
export const ELEMENT_TONE: Record<string, BtTone> = { fire: 'feu', water: 'eau', earth: 'terre', wind: 'vent' };

let uid = 0;
const id = (p: string) => `${p}${++uid}`;
const n2 = (v: number) => +v.toFixed(2);
const P = (pts: number[][]) => 'M' + pts.map((p) => p.map(n2).join(' ')).join('L') + 'Z';
type Stop = [number, string, number?];
const stops = (s: Stop[]) => s.map(([o, c, a]) => `<stop offset='${o}' stop-color='${c}'${a != null ? ` stop-opacity='${a}'` : ''}/>`).join('');
const lin = (g: string, x1: number, y1: number, x2: number, y2: number, s: Stop[]) =>
  `<linearGradient id='${g}' gradientUnits='userSpaceOnUse' x1='${n2(x1)}' y1='${n2(y1)}' x2='${n2(x2)}' y2='${n2(y2)}'>${stops(s)}</linearGradient>`;
const rad = (g: string, cx: number, cy: number, rx: number, ry: number, s: Stop[]) =>
  `<radialGradient id='${g}' gradientUnits='userSpaceOnUse' cx='${n2(cx)}' cy='${n2(cy)}' r='${n2(rx)}' gradientTransform='translate(${n2(cx)} ${n2(cy)}) scale(1 ${n2(ry / rx)}) translate(${n2(-cx)} ${n2(-cy)})'>${stops(s)}</radialGradient>`;
/** Une arête éclairée : la forme claire, puis la même décalée vers le bas-gauche par-dessus : un filet clair en haut à droite. */
const lit = (d: string, light: string, base: string, dx: number, dy: number, extra = '') => {
  const c = id('c');
  return `<clipPath id='${c}'><path d='${d}'/></clipPath><g clip-path='url(#${c})'><path d='${d}' fill='${light}'/><path d='${d}' fill='${base}' transform='translate(${-dx} ${dy})'/>${extra}</g>`;
};
/** Octogone (coins coupés) dans x0,y0,x1,y1 ; c = [haut-gauche, haut-droit, bas-droit, bas-gauche]. */
const oct = (x0: number, y0: number, x1: number, y1: number, c: number[]) => {
  const [a = 0, b = 0, d = 0, e = 0] = c;
  return P([[x0 + a, y0], [x1 - b, y0], [x1, y0 + b], [x1, y1 - d], [x1 - d, y1], [x0 + e, y1], [x0, y1 - e], [x0, y0 + a]]);
};

/** Le corps d'une dalle de `w` × `h` (épaisseur `lip`), enfoncée ou non. */
function slab(t: BtTone, w: number, h: number, lip: number, down: boolean): string {
  const T = PIERRE[t];
  const y0 = down ? lip - 1 : 0, yb = down ? h - 1 : h - lip;
  const k = h >= 56 ? 1 : h >= 44 ? 0.82 : 0.66;
  const c1 = 13 * k, cc = [6 * k, c1, 5 * k, 9 * k]; // coins éclatés : haut-gauche, haut-droit, bas-droit, bas-gauche
  const bv = 4.5 * k + 1; // largeur du biseau
  const g1 = id('g'), g2 = id('g'), g3 = id('g'), g4 = id('g');
  let s = `<defs>${lin(g1, w * 0.75, y0, w * 0.25, yb, [[0, T.st[1]], [1, T.st[2]]])}`;
  if (T.light) s += rad(g2, w / 2, (y0 + yb) / 2 + 1, w * 0.4, (yb - y0) * 0.6, [[0, T.light, down ? 0.9 : 0.78], [0.55, T.light, 0.24], [1, T.light, 0]]);
  // la pierre n'est pas lisse : deux taches douces, à des places fixes (pas de grain répété)
  // (dans les bouts, qui ne s'étirent pas : la tache sombre à gauche, la claire en haut à droite)
  const L = SIZES[(Object.keys(SIZES) as BtSize[]).find((z) => SIZES[z].h === h) ?? 'm'].L;
  s += rad(g3, L * 0.7, yb * 0.7, L * 0.9, h * 0.32, [[0, '#000', 0.26], [1, '#000', 0]]);
  s += rad(g4, w - L * 0.75, y0 + h * 0.28, L * 0.85, h * 0.24, [[0, '#fff', 0.2], [1, '#fff', 0]]);
  s += `</defs>`;
  s += `<path d='${oct(0, y0, w, h, cc)}' fill='${INK}' stroke='${INK}' stroke-width='1.2' stroke-linejoin='round'/>`;
  if (!down) s += `<path d='${oct(2, y0 + 2, w - 2, h - 2, cc.map((v) => v - 0.8))}' fill='${T.st[3]}'/>`;
  const face = oct(2, y0 + 2, w - 2, yb, cc.map((v) => v - 0.8));
  const cl = id('c');
  s += `<clipPath id='${cl}'><path d='${face}'/></clipPath><g clip-path='url(#${cl})'>`;
  // le biseau en 4 pans : en haut et à droite éclairés, en bas et à gauche dans l'ombre
  s += `<path d='${face}' fill='${T.st[2]}'/>`;
  s += `<rect x='0' y='${n2(y0)}' width='${w}' height='${n2(bv + 2)}' fill='${T.st[0]}' fill-opacity='0.6'/>`;
  s += `<rect x='${n2(w - bv - 2)}' y='${n2(y0)}' width='${n2(bv + 2)}' height='${h}' fill='${T.st[0]}' fill-opacity='0.5'/>`;
  s += `<rect x='0' y='${n2(yb - bv - 1)}' width='${n2(w - bv - 2)}' height='${n2(bv + 1)}' fill='${T.st[3]}' fill-opacity='0.6'/>`;
  s += `<rect x='0' y='${n2(y0 + bv + 2)}' width='${n2(bv + 2)}' height='${n2(yb - y0)}' fill='${T.st[3]}' fill-opacity='0.45'/>`;
  // le plat de la dalle
  const top = oct(2 + bv, y0 + 2 + bv, w - 2 - bv, yb - bv, cc.map((v) => Math.max(2, v - bv * 0.6)));
  s += `<path d='${top}' fill='url(#${g1})'/><path d='${top}' fill='url(#${g3})'/><path d='${top}' fill='url(#${g4})'/>`;
  // le coin haut-droit est cassé : sa cassure prend la lumière
  s += `<path d='${P([[w - 2 - c1 - 1, y0 + 2], [w - 2, y0 + 2 + c1 + 1], [w - 2 - bv - 2, y0 + 2 + c1 + 1], [w - 2 - c1 - 1, y0 + 2 + bv + 1]])}' fill='#fff' fill-opacity='0.28'/>`;
  if (T.light) {
    s += `<path d='${top}' fill='url(#${g2})'/>`;
    // (plus de fêlures de lumière aux bouts : demande du propriétaire, 26/11)
  }
  s += `</g>`;
  return s;
}

/** Un galet rond (pause, automatique, vitesse, fermer, retour) de diamètre `d` ; hauteur `d + 4` (son épaisseur). */
function pebble(t: BtTone, d: number, down: boolean): string {
  const T = PIERRE[t];
  const lip = Math.max(3, Math.round(d / 11)), r = d / 2;
  const cy = down ? r + lip - 1 : r, cx = r;
  const g1 = id('g'), g2 = id('g');
  let s = `<defs>${lin(g1, d * 0.8, cy - r, d * 0.2, cy + r, [[0, T.st[1]], [1, T.st[2]]])}`;
  if (T.light) s += rad(g2, cx, cy, r * 0.8, r * 0.8, [[0, T.light, down ? 0.7 : 0.55], [1, T.light, 0]]);
  s += `</defs>`;
  // une pierre ronde un peu irrégulière (galet taillé)
  const K = [1, 0.97, 1.01, 0.96, 1, 0.98, 1.02, 0.95, 1, 0.97, 1.01, 0.97];
  const blob = (rr: number, yc: number) => P(K.map((k, i) => [cx + rr * k * Math.cos((i * Math.PI) / 6), yc + rr * k * Math.sin((i * Math.PI) / 6)]));
  const e = d / 44; // l'épaisseur des arêtes suit la taille
  s += `<path d='${blob(r - 0.8, down ? cy : cy + lip / 2)}' fill='${INK}' stroke='${INK}' stroke-width='1.5' stroke-linejoin='round'/>`;
  if (!down) s += `<path d='${blob(r - 2 * e, cy + lip - 0.5)}' fill='${T.st[3]}' stroke='${T.st[3]}' stroke-linejoin='round'/>`;
  s += lit(blob(r - 2 * e, cy), T.st[0], `url(#${g1})`, 2.2 * e, 2.2 * e, T.light ? `<path d='${blob(r - 2 * e, cy)}' fill='url(#${g2})'/>` : '');
  return s;
}

const svg = (w: number, h: number, body: string, scale = 1) =>
  `<svg xmlns='http://www.w3.org/2000/svg' width='${n2(w * scale)}' height='${n2(h * scale)}' viewBox='0 0 ${w} ${h}'>${body}</svg>`;
/** Une image SVG en adresse CSS (échappement léger : le dessin n'utilise que des apostrophes). */
const cssUrl = (s: string) => `url("data:image/svg+xml,${s.replace(/%/g, '%25').replace(/#/g, '%23').replace(/</g, '%3C').replace(/>/g, '%3E').replace(/"/g, '%22')}")`;
/** Une image SVG en adresse `data:` (pour Phaser). */
export const svgDataUrl = (s: string) => `data:image/svg+xml;charset=utf-8,${encodeURIComponent(s)}`;

/** Une dalle entière de `w` × `h` (SVG), dessinée `scale` fois plus grande (pour une texture nette). */
export function pierreSvg(t: BtTone, w: number, h: number, lip: number, down = false, scale = 1): string {
  return svg(w, h, slab(t, w, h, lip, down), scale);
}
/** Un galet rond de diamètre `d` (SVG de `d` × `d + épaisseur`), `scale` fois plus grand. */
export function roundSvg(t: BtTone, d: number, down = false, scale = 1): string {
  return svg(d, d + Math.max(3, Math.round(d / 11)), pebble(t, d, down), scale);
}

/** Les couleurs des lettres posées sur une teinte : `tc` (lettre), `ts` (ombre ou lueur). */
export function textColors(t: BtTone): { tc: string; ts: string } {
  const T = PIERRE[t];
  if (T.light) return { tc: T.core!, ts: `0 0 5px ${T.light}, 0 0 12px ${T.light}b3, 0 2px 0 #0a0614b3` };
  if (t === 'ardoise') return { tc: '#3d3224', ts: '-1px 1px 0 #fff8e8a6' };
  if (t === 'off') return { tc: '#a9a5c2', ts: '-1px 1px 0 #0000004d' };
  return { tc: '#ece8fa', ts: '0 2px 0 #0a0614b3' };
}

/** Les teintes qui ont leurs dessins dans le CSS (toutes, sauf le creux : seulement en rail, pour les onglets). */
const CSS_TONES = (Object.keys(PIERRE) as BtTone[]).filter((t) => t !== 'creux');
const CSS_SIZES: BtSize[] = ['xxl', 'xl', 'l', 'm', 's'];

let installed = false;
/** Pose les dessins (variables CSS sur <html>) et les règles qui les relient aux classes `bt-<teinte>` / `bt-<taille>`. */
export function installButtons() {
  if (installed || typeof document === 'undefined') return;
  installed = true;
  const root = document.documentElement.style;
  const rules: string[] = [];
  const W = (sz: BtSize) => 2 * SIZES[sz].L + 40;
  for (const t of CSS_TONES) {
    const { tc, ts } = textColors(t);
    rules.push(`:where(.bt-${t}){--tc:${tc};--ts:${ts}}`);
    for (const sz of CSS_SIZES) {
      const { h, lip } = SIZES[sz];
      for (const down of [false, true]) root.setProperty(`--bt-pierre-${t}-${sz}${down ? '-down' : ''}`, cssUrl(pierreSvg(t, W(sz), h, lip, down)));
      rules.push(`:where(.bt-${t}.bt-${sz}){--sk:var(--bt-pierre-${t}-${sz});--skd:var(--bt-pierre-${t}-${sz}-down)}`);
    }
    for (const down of [false, true]) root.setProperty(`--bt-pierre-rond-${t}${down ? '-down' : ''}`, cssUrl(roundSvg(t, 44, down)));
    rules.push(`:where(.bt-rond.bt-${t}){--skr:var(--bt-pierre-rond-${t});--skrd:var(--bt-pierre-rond-${t}-down)}`);
  }
  // le rail des onglets (un creux de pierre)
  root.setProperty('--bt-pierre-creux-rail', cssUrl(pierreSvg('creux', W('rail'), SIZES.rail.h, 0)));
  for (const sz of Object.keys(SIZES) as BtSize[]) {
    const { h, lip, L, fs } = SIZES[sz];
    rules.push(`:where(.bt-${sz}){--h:${h}px;--lip:${lip}px;--L:${L}px;--Ln:${L};--fs:${fs}px}`);
  }
  // impossible : la pierre éteinte (en dernier : elle passe devant la teinte)
  const off = textColors('off');
  rules.push(`:where(.bt:disabled,.bt.bt-is-off,.bt-rond:disabled){--tc:${off.tc};--ts:${off.ts}}`);
  for (const sz of CSS_SIZES) rules.push(`:where(.bt-${sz}:disabled,.bt-${sz}.bt-is-off){--sk:var(--bt-pierre-off-${sz});--skd:var(--bt-pierre-off-${sz})}`);
  rules.push(`:where(.bt-rond:disabled){--skr:var(--bt-pierre-rond-off);--skrd:var(--bt-pierre-rond-off)}`);
  const style = document.createElement('style');
  style.id = 'bt-rules';
  style.textContent = rules.join('\n');
  document.head.appendChild(style);
}

/** Les classes d'un bouton de pierre (à poser avec `bt` sur un <button>). */
export function btClass(t: BtTone, sz: BtSize): string {
  return `bt bt-${t} bt-${sz}`;
}
