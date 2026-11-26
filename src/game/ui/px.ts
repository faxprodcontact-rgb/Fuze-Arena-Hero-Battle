// Les pièces de l'interface en pixel art HD (nouvelle DA, 26/11/2026) : cadres, panneaux, boutons, plaques, médaillons,
// pastilles, jauges. Tout est dessiné ici, pixel par pixel, à partir d'une seule palette (`PAL`), puis :
// - posé dans le CSS sous forme de variables (`--px-<pièce>`, installées une fois par `installPx()` au lancement) :
//   chaque variable est un fond en 9 morceaux (coins fixes, bords et milieu étirés) agrandi ×2 sans flou ;
// - donné à Phaser (panneau des combats, `hud-art.tsx`) par `pxCanvas()` à la taille voulue.
// Règles du dessin (voir refonte-graphique/pixel/ui/STYLE.md) : un seul contour sombre par objet, une seule lumière en haut
// à droite (arête claire en haut et à droite, ombre en bas et à gauche), gammes décalées en teinte, coins arrondis en
// escalier, aucun ornement (ni losange, ni clou, ni double cadre).
// Les petits signes (étoiles, coche, croix, chevrons, plus / égal, pastilles, petits boutons ronds) et le halo ne sont
// plus en pixels : ils sont dans le style moderne (lisses, HD), dessinés en SVG par
// refonte-graphique/ui-moderne/pictos/signes.py (→ signs-art.ts) ; on garde ici leurs noms de variables CSS.
import { SIGN_SVG } from './signs-art';

/** Un pixel du dessin = PX pixels CSS (toujours un entier : l'image reste nette). */
export const PX = 2;

/** Le contour unique de toutes les pièces (le même violet très sombre que les héros HD, uilib.py). */
export const INK = '#221022';

/** Les gammes (du plus sombre au plus clair), décalées en teinte : ombres vers le violet, lumières vers le jaune. */
export const PAL = {
  navy: ['#121636', '#1c2457', '#273479', '#34489c', '#5a76d0'],
  gold: ['#8a3f16', '#c76a1a', '#f0a830', '#ffd650', '#fff4b0'],
  cream: ['#a8805e', '#dcc093', '#f3e3c0', '#fff3da', '#ffffff'],
  green: ['#145040', '#1f8a4a', '#3dbb4c', '#7fe05c', '#d0ff94'],
  blue: ['#1c2f7a', '#2456b8', '#2f8be8', '#64c6ff', '#c2f2ff'],
  red: ['#5c1438', '#ad2846', '#e5434d', '#ff7f6a', '#ffd2b4'],
  purple: ['#3a1c78', '#6636bd', '#9459e8', '#c58fff', '#f2d0ff'],
  teal: ['#0f4450', '#16807e', '#22b6a4', '#5fe6c0', '#c8fff0'],
  grey: ['#4b4c62', '#77788f', '#a2a3b6', '#c9cad6', '#ececf2'],
  // les creux : une jauge vide, une fente de monnaie
  well: ['#07081a', '#0d1030', '#161b45', '#222a62', '#3a4690'],
} as const;
export type Tone = keyof typeof PAL;

type Ramp = readonly string[];
type Px = string | null;

// ---------- Le dessin ----------

/** Les coins en escalier : combien de pixels sont retirés au début de chaque ligne, selon le rayon. */
const CORNERS: Record<number, number[]> = {
  0: [], 1: [1], 2: [2, 1], 3: [3, 1, 1], 4: [4, 2, 1, 1], 5: [5, 3, 2, 1, 1], 6: [6, 4, 3, 2, 1, 1], 7: [7, 5, 3, 2, 2, 1, 1],
};

/** Le masque d'un rectangle aux coins arrondis en escalier. */
function roundRect(w: number, h: number, r: number): boolean[][] {
  const cut = CORNERS[r] ?? [];
  const m: boolean[][] = [];
  for (let y = 0; y < h; y++) {
    const row: boolean[] = [];
    const cy = y < cut.length ? cut[y]! : h - 1 - y < cut.length ? cut[h - 1 - y]! : 0;
    for (let x = 0; x < w; x++) row.push(x >= cy && x < w - cy);
    m.push(row);
  }
  return m;
}

/** Le masque d'un disque (diamètre d), propre au pixel. */
function disc(d: number): boolean[][] {
  const c = (d - 1) / 2, r2 = (d / 2) ** 2 - d * 0.08;
  return Array.from({ length: d }, (_, y) => Array.from({ length: d }, (_, x) => (x - c) ** 2 + (y - c) ** 2 <= r2));
}

const inside = (m: boolean[][], x: number, y: number) => y >= 0 && y < m.length && x >= 0 && x < m[0]!.length && m[y]![x]!;

/** Le côté d'un pixel du bord : 'top', 'right', 'bottom' ou 'left' (le haut et la droite reçoivent la lumière). */
type Side = 'top' | 'right' | 'bottom' | 'left';
function sideOf(m: boolean[][], x: number, y: number): Side | null {
  if (!inside(m, x, y - 1)) return 'top';
  if (!inside(m, x, y + 1)) return 'bottom';
  if (!inside(m, x + 1, y)) return 'right';
  if (!inside(m, x - 1, y)) return 'left';
  return null;
}

/** Une couche d'anneau : sa couleur selon le côté (lumière en haut à droite, ombre en bas à gauche). */
interface Ring { top: string; right: string; bottom: string; left: string }
const flat = (c: string): Ring => ({ top: c, right: c, bottom: c, left: c });
/** Un anneau de métal ou d'émail pris dans une gamme : clair en haut, moyen à droite, sombre à gauche et en bas. */
const lit = (g: Ramp, hi = 4, mid = 3, lo = 2, low = 1): Ring => ({ top: g[hi]!, right: g[mid]!, left: g[lo]!, bottom: g[low]! });

/**
 * Dessine une forme : `rings` (de l'extérieur vers l'intérieur) puis le remplissage `fill(dx, dy, iw, ih)` (position dans
 * l'intérieur et sa taille). Le premier anneau est toujours le contour.
 */
function paint(m: boolean[][], rings: Ring[], fill: (dx: number, dy: number, iw: number, ih: number) => Px): Px[][] {
  const h = m.length, w = m[0]!.length;
  const out: Px[][] = Array.from({ length: h }, () => Array<Px>(w).fill(null));
  let cur = m.map((r) => r.slice());
  for (const ring of rings) {
    const next = cur.map((r) => r.slice());
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      if (!cur[y]![x]) continue;
      const s = sideOf(cur, x, y);
      if (s) { out[y]![x] = ring[s]; next[y]![x] = false; }
    }
    cur = next;
  }
  // l'intérieur : sa boîte
  let x0 = w, y0 = h, x1 = -1, y1 = -1;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (cur[y]![x]) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) if (cur[y]![x]) out[y]![x] = fill(x - x0, y - y0, x1 - x0 + 1, y1 - y0 + 1);
  return out;
}

function toCanvas(p: Px[][], scale = 1): HTMLCanvasElement {
  const h = p.length, w = p[0]!.length;
  const c = document.createElement('canvas');
  c.width = w * scale; c.height = h * scale;
  const g = c.getContext('2d')!;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const v = p[y]![x];
    if (!v) continue;
    g.fillStyle = v;
    g.fillRect(x * scale, y * scale, scale, scale);
  }
  return c;
}

// ---------- Les pièces ----------

/** Une pièce en 9 morceaux : son dessin et la taille (en pixels du dessin) des bords fixes [haut, droite, bas, gauche]. */
export interface Piece { px: Px[][]; slice: [number, number, number, number] }

/** Bouton : contour, arête claire, émail, lèvre sombre de 2 pixels en bas (le relief) ; `down` = enfoncé (plus de lèvre). */
function button(g: Ramp, down = false): Piece {
  const w = 12, h = 13;
  // enfoncé : le bouton descend de la hauteur de sa lèvre (deux lignes vides en haut)
  const m = down ? [Array(w).fill(false), Array(w).fill(false), ...roundRect(w, h - 2, 3)] : roundRect(w, h, 3);
  const px = paint(m, [flat(INK)], (dx, dy, iw, ih) => {
    if (!down && dy >= ih - 2) return g[1]!;                           // la lèvre
    if (dy === 0) return dx >= iw - 3 ? g[4]! : g[3]!;                 // l'arête du haut (plus claire vers la droite)
    if (dx === iw - 1 && dy < 3) return g[3]!;                         // la lumière descend un peu à droite
    if (dy === 1 && dx > 0) return mixHex(g[3]!, g[2]!, 0.55);         // le bombé : une ligne entre l'arête et l'émail
    if (dx === 0) return mixHex(g[2]!, g[1]!, 0.35);                   // le bord gauche, dans l'ombre
    return g[2]!;
  });
  return { px, slice: down ? [6, 4, 4, 4] : [4, 4, 5, 4] };
}

/** Panneau clair (parchemin éclairci) : contour, arête claire en haut et à droite, ombre douce en bas. */
function panel(g: Ramp = PAL.cream): Piece {
  const m = roundRect(12, 12, 3);
  const px = paint(m, [flat(INK), { top: g[4]!, right: g[3]!, bottom: g[1]!, left: g[2]! }], (_dx, dy, _iw, ih) => (dy >= ih - 1 ? mixHex(g[2]!, g[1]!, 0.5) : g[2]!));
  return { px, slice: [4, 4, 4, 4] };
}

/** Cadre d'une fenêtre : contour, filet d'or, puis le parchemin clair (arête claire en haut). */
function frame(): Piece {
  const c = PAL.cream;
  const m = roundRect(12, 12, 3);
  const px = paint(m, [flat(INK), lit(PAL.gold, 4, 3, 2, 1), { top: c[4]!, right: c[3]!, bottom: c[1]!, left: c[2]! }], () => c[2]!);
  return { px, slice: [4, 4, 4, 4] };
}

/** Plaque (titres, chapitre, étiquettes) : contour, filet d'or, émail de la couleur donnée (arête claire, ombre en bas). */
function plaque(g: Ramp, gold = true): Piece {
  const m = roundRect(12, 12, 3);
  const rings = gold ? [flat(INK), lit(PAL.gold, 4, 3, 2, 1)] : [flat(INK)];
  const px = paint(m, rings, (dx, dy, iw, ih) => {
    if (dy === 0) return dx >= iw - 3 ? g[4]! : g[3]!;
    if (dy >= ih - 1) return g[1]!;
    return g[2]!;
  });
  return { px, slice: gold ? [4, 4, 4, 4] : [3, 3, 3, 3] };
}

/** Creux sombre (fente d'une monnaie, jauge vide) : contour, ombre en haut dans le creux, reflet en bas. */
function groove(g: Ramp = PAL.well, r = 3): Piece {
  const s = Math.max(4, r + 1), w = 2 * s + 2, h = 2 * s + 2;
  const m = roundRect(w, h, r);
  const px = paint(m, [flat(INK)], (_dx, dy, _iw, ih) => (dy === 0 ? g[0]! : dy === ih - 1 ? g[3]! : g[1]!));
  return { px, slice: [s, s, s, s] };
}

/** Creux clair dans un panneau (une ligne de réglage, une case) : pas de contour, ombre en haut et à gauche, lumière en bas. */
function inset(): Piece {
  const c = PAL.cream;
  const body = mixHex(c[2]!, c[1]!, 0.45);
  const m = roundRect(10, 10, 2);
  const px = paint(m, [{ top: mixHex(c[1]!, c[0]!, 0.35), left: c[1]!, bottom: c[3]!, right: mixHex(body, c[3]!, 0.5) }], () => body);
  return { px, slice: [3, 3, 3, 3] };
}

/** Une barre (haut, bas de l'écran, bas de l'accueil) : émail bleu nuit, filet d'or et contour du côté du jeu. */
function band(edge: 'top' | 'bottom'): Piece {
  const n = PAL.navy, go = PAL.gold;
  const rows = edge === 'bottom'
    ? [n[3]!, n[2]!, n[2]!, n[2]!, n[2]!, n[1]!, go[3]!, go[1]!, INK]
    : [INK, go[3]!, go[1]!, n[3]!, n[2]!, n[2]!, n[2]!, n[2]!, n[1]!];
  const px = rows.map((c) => [c, c, c]);
  return { px, slice: edge === 'bottom' ? [1, 1, 4, 1] : [4, 1, 1, 1] };
}

// ---------- Petites pièces entières (non étirées) ----------

/** Médaillon (bouton rond, portrait du joueur) : contour, anneau d'or, disque d'émail bleu nuit éclairé en haut à droite. */
function medal(d: number, tone: Ramp = PAL.navy): Px[][] {
  const m = disc(d);
  const go = PAL.gold;
  const ringW = d >= 22 ? 2 : 1;
  const rings: Ring[] = [flat(INK), ...Array.from({ length: ringW }, (_, i) => (i === 0 ? lit(go, 4, 3, 2, 1) : lit(go, 3, 3, 2, 1))), flat(tone[0]!)];
  return paint(m, rings, (dx, dy, iw, ih) => {
    // la lumière vient d'en haut à droite : un croissant clair sur ce bord, une ombre sur le bord opposé, une tache de lumière
    const r = iw / 2, u = (dx + 0.5 - r) / r, v = (dy + 0.5 - ih / 2) / r;
    const rim = Math.hypot(u, v), side = (u - v) / Math.SQRT2;
    if (Math.hypot(u - 0.38, v + 0.38) < 0.2) return tone[4]!;
    if (rim > 0.7 && side > 0.35) return tone[3]!;
    if (rim > 0.7 && side < -0.35) return tone[1]!;
    return tone[2]!;
  });
}

/** Un signe de signs-art.ts (SVG) en adresse d'image (`data:`). */
export function signUrl(name: string): string {
  return `data:image/svg+xml,${encodeURIComponent(SIGN_SVG[name] ?? '')}`;
}
const signCss = (name: string) => `url("${signUrl(name)}")`;

/** Le chevron d'or d'une languette (vers le bas = déplier, vers le haut = replier). */
export function chevronUrl(up: boolean): string {
  return signUrl(up ? 'chevron-up' : 'chevron-down');
}

/** Les petits signes posés dans le CSS (`--px-<nom>`, mêmes noms qu'en pixel art), et leur dessin dans signs-art.ts. */
const SIGNS: Record<string, string> = {
  star: 'star', 'star-red': 'star-red', check: 'check', cross: 'cross', up: 'up', chev: 'chev', 'chev-s': 'chev-s',
  'back-s': 'back-s', play: 'play', stop: 'stop', 'op-plus': 'op-plus', 'op-eq': 'op-eq', 'op-arrow': 'op-arrow',
  badge: 'badge', 'badge-gold': 'badge-gold', close: 'btn-close', back: 'btn-back', next: 'btn-next', plus: 'btn-plus',
};

/** Recompose une pièce en 9 morceaux à une taille donnée (en pixels du dessin). */
export function compose(p: Piece, w: number, h: number): Px[][] {
  const [t, r, b, l] = p.slice;
  const sh = p.px.length, sw = p.px[0]!.length;
  const out: Px[][] = Array.from({ length: h }, () => Array<Px>(w).fill(null));
  for (let y = 0; y < h; y++) {
    const sy = y < t ? y : y >= h - b ? sh - (h - y) : t;
    for (let x = 0; x < w; x++) {
      const sx = x < l ? x : x >= w - r ? sw - (w - x) : l;
      out[y]![x] = p.px[sy]![sx]!;
    }
  }
  return out;
}

// ---------- Vers le CSS ----------

function crop(p: Px[][], x: number, y: number, w: number, h: number): Px[][] {
  return p.slice(y, y + h).map((r) => r.slice(x, x + w));
}
function url(p: Px[][]): string {
  return `url(${toCanvas(p).toDataURL('image/png')})`;
}

/** Le fond CSS d'une pièce en 9 morceaux, agrandie ×PX : à poser sur un ::before avec `image-rendering: pixelated`. */
function nineCss(p: Piece): string {
  const [t, r, b, l] = p.slice;
  const sh = p.px.length, sw = p.px[0]!.length;
  const T = t * PX, R = r * PX, B = b * PX, L = l * PX;
  const midW = `calc(100% - ${L + R}px)`, midH = `calc(100% - ${T + B}px)`;
  const L1 = [
    `${url(crop(p.px, 0, 0, l, t))} 0 0 / ${L}px ${T}px`,
    `${url(crop(p.px, sw - r, 0, r, t))} 100% 0 / ${R}px ${T}px`,
    `${url(crop(p.px, 0, sh - b, l, b))} 0 100% / ${L}px ${B}px`,
    `${url(crop(p.px, sw - r, sh - b, r, b))} 100% 100% / ${R}px ${B}px`,
    `${url(crop(p.px, l, 0, 1, t))} ${L}px 0 / ${midW} ${T}px`,
    `${url(crop(p.px, l, sh - b, 1, b))} ${L}px 100% / ${midW} ${B}px`,
    `${url(crop(p.px, 0, t, l, 1))} 0 ${T}px / ${L}px ${midH}`,
    `${url(crop(p.px, sw - r, t, r, 1))} 100% ${T}px / ${R}px ${midH}`,
    `${url(crop(p.px, l, t, 1, 1))} ${L}px ${T}px / ${midW} ${midH}`,
  ];
  return L1.map((s) => `${s} no-repeat`).join(', ');
}

/** Toutes les pièces du jeu, par nom de variable CSS (`--px-<nom>`). */
let cache: Record<string, Piece> | null = null;
function pieces(): Record<string, Piece> {
  if (cache) return cache;
  const out: Record<string, Piece> = {
    panel: panel(),
    frame: frame(),
    inset: inset(),
    groove: groove(),
    'groove-s': groove(PAL.well, 2),
    'bar-top': band('bottom'),
    'bar-bottom': band('top'),
  };
  for (const tone of ['green', 'blue', 'gold', 'red', 'purple', 'teal', 'grey', 'cream', 'navy'] as Tone[]) {
    out[`btn-${tone}`] = button(PAL[tone]);
    out[`btn-${tone}-down`] = button(PAL[tone], true);
  }
  for (const tone of ['navy', 'blue', 'purple', 'red', 'green', 'teal', 'gold'] as Tone[]) out[`plaque-${tone}`] = plaque(PAL[tone]);
  out['chip'] = plaque(PAL.navy, false);
  out['well-green'] = groove(PAL.green, 3);
  cache = out;
  return out;
}

/** Un cadre seul (contour, anneau de la couleur, contour intérieur sombre ; le milieu reste vide) : cases des héros, objets. */
function rim(g: Ramp): Piece {
  const m = roundRect(12, 12, 3);
  const px = paint(m, [flat(INK), lit(g, 4, 3, 2, 1), lit(g, 3, 2, 1, 1), flat(mixHex(g[0]!, INK, 0.5))], () => null);
  return { px, slice: [4, 4, 4, 4] };
}

/** Une gamme de 5 tons tirée d'une seule couleur : ombres vers le violet, lumières vers le jaune (comme PAL). */
export function rampFrom(hex: string): string[] {
  return [mixHex(mixHex(hex, '#2a0f4a', 0.6), '#000000', 0.15), mixHex(hex, '#3a1660', 0.35), hex, mixHex(hex, '#fff2b0', 0.4), mixHex(hex, '#fffbe6', 0.75)];
}

const dynamic = new Map<string, string>();
/**
 * Le fond CSS d'une pièce dans n'importe quelle couleur (rareté, élément…), à poser dans le style d'un élément :
 * `style={{ '--pxf': pxBg('rim', couleur) }}` (avec la classe `pxf`). Gardé en mémoire : chaque couleur n'est dessinée qu'une fois.
 */
export function pxBg(kind: 'plaque' | 'btn' | 'rim' | 'panel', hex: string): string {
  const key = `${kind}${hex}`;
  let v = dynamic.get(key);
  if (!v) {
    const g = rampFrom(hex);
    v = nineCss(kind === 'plaque' ? plaque(g) : kind === 'btn' ? button(g) : kind === 'rim' ? rim(g) : panel(g));
    dynamic.set(key, v);
  }
  return v;
}

let installed = false;
/** Pose les variables CSS des pièces (une fois, au lancement, avant le premier dessin). */
export function installPx() {
  if (installed || typeof document === 'undefined') return;
  installed = true;
  const root = document.documentElement.style;
  for (const [name, p] of Object.entries(pieces())) root.setProperty(`--px-${name}`, nineCss(p));
  for (const [name, svg] of Object.entries(SIGNS)) root.setProperty(`--px-${name}`, signCss(svg));
}

const medalCache = new Map<string, string>();
/** L'image d'un médaillon de `size` pixels CSS (diamètre du dessin = size / PX). */
export function medalUrl(size: number, tone: Tone = 'navy'): string {
  const d = Math.max(9, Math.round(size / PX)), key = `${d}-${tone}`;
  let u = medalCache.get(key);
  if (!u) { u = toCanvas(medal(d, PAL[tone])).toDataURL('image/png'); medalCache.set(key, u); }
  return u;
}

// ---------- Vers Phaser (panneau des combats) ----------

/** Une pièce recomposée à w × h pixels du dessin, agrandie `scale` fois (une toile, pour une texture Phaser). */
export function pxCanvas(name: 'panel' | 'frame' | 'groove' | `btn-${Tone}` | `plaque-${Tone}`, w: number, h: number, scale: number): HTMLCanvasElement {
  const all = pieces();
  return toCanvas(compose(all[name]!, w, h), scale);
}
/** Un médaillon (anneau d'or + disque) en toile, pour Phaser. */
export function medalCanvas(d: number, scale: number, tone: Tone = 'navy'): HTMLCanvasElement {
  return toCanvas(medal(d, PAL[tone]), scale);
}
/**
 * Une toile ronde faite de couches (du centre vers le bord) : `layers` = [rayon extérieur en pixels du dessin, couleur ou
 * gamme]. Une gamme est éclairée en haut à droite (clair de ce côté, sombre à l'opposé). `null` = vide. Pour Phaser.
 */
export function radialCanvas(d: number, layers: [number, string | Ramp | null][], scale: number): HTMLCanvasElement {
  const c = (d - 1) / 2;
  const p: Px[][] = Array.from({ length: d }, (_, y) => Array.from({ length: d }, (_, x) => {
    const r = Math.hypot(x - c, y - c) + 0.5;
    const layer = layers.find(([rr]) => r <= rr);
    if (!layer || layer[1] === null) return null;
    const v = layer[1];
    if (typeof v === 'string') return v;
    const side = ((x - c) - (y - c)) / Math.max(1, Math.hypot(x - c, y - c)) / Math.SQRT2;
    return side > 0.45 ? v[4]! : side > 0.05 ? v[3]! : side < -0.55 ? v[1]! : v[2]!;
  }));
  return toCanvas(p, scale);
}

/** Un anneau seul (contour, or, contour intérieur ; centre vide), pour poser sur un portrait. */
export function ringCanvas(d: number, hole: number, scale: number): HTMLCanvasElement {
  const p = medal(d);
  const c = (d - 1) / 2, r2 = (hole / 2) ** 2;
  for (let y = 0; y < d; y++) for (let x = 0; x < d; x++) if ((x - c) ** 2 + (y - c) ** 2 <= r2) p[y]![x] = null;
  // le bord du trou : un pixel sombre (le contour intérieur de l'anneau)
  for (let y = 0; y < d; y++) for (let x = 0; x < d; x++) {
    if (!p[y]![x]) continue;
    const near = [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([a, b]) => { const xx = x + a!, yy = y + b!; return (xx - c) ** 2 + (yy - c) ** 2 <= r2; });
    if (near) p[y]![x] = INK;
  }
  return toCanvas(p, scale);
}

// ---------- Couleurs ----------

export function mixHex(a: string, b: string, t: number): string {
  const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
  const ch = (s: number) => {
    const x = (pa >> s) & 255, y = (pb >> s) & 255;
    return Math.round(x + (y - x) * t);
  };
  return `#${((1 << 24) | (ch(16) << 16) | (ch(8) << 8) | ch(0)).toString(16).slice(1)}`;
}

/** La teinte la plus proche parmi les plaques (pour les anciens appels qui donnent trois couleurs de ruban). */
export function nearestTone(hex: string): Tone {
  const n = parseInt(hex.slice(1), 16);
  const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  if (max - min < 30) return 'navy';
  let h = 0;
  if (max === r) h = ((g - b) / (max - min)) % 6; else if (max === g) h = (b - r) / (max - min) + 2; else h = (r - g) / (max - min) + 4;
  h = (h * 60 + 360) % 360;
  if (h < 25 || h >= 330) return 'red';
  if (h < 70) return 'gold';
  if (h < 160) return 'green';
  if (h < 195) return 'teal';
  if (h < 255) return 'blue';
  return 'purple';
}

// ---------- Le halo (derrière un trophée, un héros fusionné, un tirage rare, un Légendaire) ----------

const haloCache = new Map<string, { glow: string; spin: string }>();
/** Une étincelle à 4 branches rentrantes (signe inventé), centrée en (x, y), de rayon r. */
function sparklePath(x: number, y: number, r: number): string {
  const f = (v: number) => v.toFixed(1);
  return `M${f(x)} ${f(y - r)}Q${f(x)} ${f(y)} ${f(x + r)} ${f(y)}Q${f(x)} ${f(y)} ${f(x)} ${f(y + r)}Q${f(x)} ${f(y)} ${f(x - r)} ${f(y)}Q${f(x)} ${f(y)} ${f(x)} ${f(y - r)}Z`;
}
/**
 * Le halo, dans le style moderne : une lueur douce de la couleur demandée et un anneau de lumière (`glow`, qui respire),
 * et huit étincelles posées sur un cercle (`spin`, qui tourne lentement ; anim.css). Pas de rayons. Deux images SVG
 * (adresses `url(…)`), gardées en mémoire par couleur.
 */
export function haloLayers(hex: string): { glow: string; spin: string } {
  const hit = haloCache.get(hex);
  if (hit) return hit;
  const g = rampFrom(hex);
  const glow = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs>`
    + `<radialGradient id="a"><stop offset="0" stop-color="${g[4]}" stop-opacity="0.75"/><stop offset="0.38" stop-color="${hex}" stop-opacity="0.42"/>`
    + `<stop offset="0.72" stop-color="${hex}" stop-opacity="0.14"/><stop offset="1" stop-color="${hex}" stop-opacity="0"/></radialGradient>`
    + `<filter id="b" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.2"/></filter></defs>`
    + `<circle cx="50" cy="50" r="50" fill="url(#a)"/>`
    + `<circle cx="50" cy="50" r="41" fill="none" stroke="${g[3]}" stroke-width="2.4" opacity="0.55" filter="url(#b)"/>`
    + `<circle cx="50" cy="50" r="41" fill="none" stroke="${g[4]}" stroke-width="0.8" opacity="0.8"/></svg>`;
  let stars = '';
  for (let i = 0; i < 8; i++) {
    const a = (i * Math.PI) / 4 - Math.PI / 2, big = i % 2 === 0, x = 50 + Math.cos(a) * 41, y = 50 + Math.sin(a) * 41;
    stars += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${big ? 6 : 4}" fill="url(#c)"/>`
      + `<path d="${sparklePath(x, y, big ? 5.5 : 3.2)}" fill="#ffffff"/>`;
  }
  const spin = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><radialGradient id="c">`
    + `<stop offset="0" stop-color="${g[4]}" stop-opacity="0.9"/><stop offset="1" stop-color="${hex}" stop-opacity="0"/></radialGradient></defs>${stars}</svg>`;
  const css = (svg: string) => `url("data:image/svg+xml,${encodeURIComponent(svg)}")`;
  const out = { glow: css(glow), spin: css(spin) };
  haloCache.set(hex, out);
  return out;
}
