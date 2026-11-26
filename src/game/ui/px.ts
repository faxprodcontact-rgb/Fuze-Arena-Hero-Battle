// Les couleurs communes des dessins faits par le code (style moderne, 26/11/2026). Jusqu'à la v0.58, ce fichier dessinait
// toutes les pièces de l'interface en pixels (cadres, boutons, plaques, médaillons, halo) ; elles sont maintenant lisses et
// faites par le CSS (style.css, jetons en tête du fichier) et, au combat, par hud-art.tsx. Il ne reste ici que la palette
// (`PAL` : les teintes des boutons, plaques et médaillons), quelques outils de couleur, les petits signes lisses
// (signs-art.ts, posés dans le CSS par `installSigns()`) et le halo (`haloLayers`, anim.tsx).
import { SIGN_SVG } from './signs-art';

/** (ancien) Un pixel du dessin = PX pixels CSS. */
export const PX = 2;

/** Le contour des personnages HD (uilib.py). */
export const INK = '#221022';

/** Les gammes du style moderne (du plus sombre au plus clair) : raisin, or, surfaces claires, et les couleurs à rôle. */
export const PAL = {
  navy: ['#0c0822', '#1e1648', '#2e2470', '#4b3c9e', '#7a6ad8'],
  gold: ['#9a4f00', '#e58a00', '#ffb21f', '#ffd65c', '#fff1a8'],
  cream: ['#a29bc6', '#d7d1ec', '#eeebf8', '#f6f4fd', '#ffffff'],
  green: ['#0f6a30', '#12823a', '#2fc457', '#7cf08a', '#d4ffd9'],
  blue: ['#13368c', '#1a47b8', '#2f8cff', '#6cc4ff', '#d4f0ff'],
  red: ['#8a1030', '#b01f3a', '#ff5468', '#ff98a2', '#ffe0e4'],
  purple: ['#3a1490', '#5420c4', '#9b5cff', '#c8a4ff', '#efe4ff'],
  teal: ['#085a50', '#0b7a6c', '#22c9b0', '#7ff2de', '#dcfff8'],
  grey: ['#5a5774', '#8a87a3', '#bdbad1', '#dcdaea', '#f2f1f8'],
  well: ['#05031a', '#0c0822', '#150f36', '#1e1648', '#2a1f63'],
} as const;
export type Tone = keyof typeof PAL;

// ---------- Couleurs ----------

export function mixHex(a: string, b: string, t: number): string {
  const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
  const ch = (s: number) => {
    const x = (pa >> s) & 255, y = (pb >> s) & 255;
    return Math.round(x + (y - x) * t);
  };
  return `#${((1 << 24) | (ch(16) << 16) | (ch(8) << 8) | ch(0)).toString(16).slice(1)}`;
}

/** Une gamme de 5 tons tirée d'une seule couleur : ombres vers le violet, lumières vers le jaune (comme PAL). */
export function rampFrom(hex: string): string[] {
  return [mixHex(mixHex(hex, '#2a0f4a', 0.6), '#000000', 0.15), mixHex(hex, '#3a1660', 0.35), hex, mixHex(hex, '#fff2b0', 0.4), mixHex(hex, '#fffbe6', 0.75)];
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

// ---------- Les petits signes (signs-art.ts, style moderne) ----------

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

let installed = false;
/** Pose les petits signes dans le CSS (`--px-<nom>`), une fois, au lancement, avant le premier dessin. */
export function installSigns() {
  if (installed || typeof document === 'undefined') return;
  installed = true;
  const root = document.documentElement.style;
  for (const [name, svg] of Object.entries(SIGNS)) root.setProperty(`--px-${name}`, signCss(svg));
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
