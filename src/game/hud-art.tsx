// Les pièces de l'interface du combat (battle-scene.ts), style moderne (26/11/2026, demande du propriétaire : « on voit
// tout le terrain, sans bandeau ») : tout flotte sur la scène, léger — des boutons ronds, des pilules de verre sombre, une
// rangée de cartes de héros (portrait, nom, vie, énergie) posée sur un fondu doux en bas de l'écran.
// Dessinées lisses dans des toiles (×2 pour rester nettes sur un téléphone), données à Phaser comme textures. Les boutons
// sont les galets et dalles « Pierre de l'arène » des menus (ui/buttons.ts), rendus depuis le même dessin SVG.
import type Phaser from 'phaser';
import { PIERRE, pierreSvg, roundSvg, svgDataUrl, textColors, type BtTone } from './ui/buttons';

/** Les toiles sont dessinées 2 fois plus grandes que leur taille au combat (puis réduites : bords nets). */
const R = 2;
/** (pour poser une texture faite ici à sa vraie taille : `setScale(1 / HUD_RES)`) */
export const HUD_RES = R;

/** Les teintes des boutons du combat : galet (éteint : pause, vitesse, AUTO coupé), basalte (allumé : AUTO, reprendre), feu (quitter). */
export const HUD_TONES = ['galet', 'basalte', 'feu'] as const;
export type HudTone = (typeof HUD_TONES)[number];

/** Les lettres posées sur une pierre : couleur, et lueur (pierre allumée) ou ombre (pierre éteinte). */
export function hudText(tone: BtTone): { color: string; glow?: string; ink: string } {
  const T = PIERRE[tone];
  return { color: textColors(tone).tc, glow: T.light, ink: '#0a0614' };
}

/** Le haut des cartes, par élément : deux tons (haut clair, bas sombre). */
const TINTS: Record<string, [string, string]> = {
  fire: ['#ff9a6a', '#c8402a'], wind: ['#8be89a', '#2f9a4c'], water: ['#5aa2e6', '#1f4f9e'], earth: ['#ffd07a', '#b8722a'], none: ['#8a86a8', '#2e2c47'],
};

/** Une carte de héros (unités du combat) : sa taille, son arrondi, la hauteur du portrait. */
export const CARD = { w: 128, h: 182, r: 22, face: 120 };
/** Un bouton rond : son diamètre ; sa hauteur (épaisseur de la pierre comprise). */
export const ROUND = 68;
export const ROUND_LIP = Math.max(3, Math.round(ROUND / 11));
/** Un bouton large (fenêtre de pause) : largeur, hauteur, épaisseur. */
export const WIDE = { w: 290, h: 84, lip: 7 };

function add(sc: Phaser.Scene, key: string, w: number, h: number, draw: (g: CanvasRenderingContext2D) => void) {
  if (sc.textures.exists(key)) return;
  const c = document.createElement('canvas');
  c.width = Math.round(w * R); c.height = Math.round(h * R);
  const g = c.getContext('2d')!;
  g.scale(R, R);
  draw(g);
  sc.textures.addCanvas(key, c);
}

function rr(g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number | number[]) {
  g.beginPath();
  g.roundRect(x, y, w, h, r);
}

/** Le fondu du bas (sous les cartes) : du transparent au raisin. Étiré à la largeur de l'écran. */
function fade(g: CanvasRenderingContext2D) {
  const grad = g.createLinearGradient(0, 0, 0, 256);
  grad.addColorStop(0, 'rgba(12, 8, 34, 0)');
  grad.addColorStop(0.45, 'rgba(12, 8, 34, 0.45)');
  grad.addColorStop(1, 'rgba(12, 8, 34, 0.82)');
  g.fillStyle = grad; g.fillRect(0, 0, 8, 256);
}

/** Le fond d'une carte : verre raisin, le haut (le portrait) de la couleur de l'élément. 8 unités de marge pour l'ombre. */
function card(tint: [string, string]) {
  return (g: CanvasRenderingContext2D) => {
    const m = 8, { w, h, r, face } = CARD;
    g.save();
    g.shadowColor = 'rgba(5, 2, 26, 0.6)'; g.shadowBlur = 12; g.shadowOffsetY = 4;
    rr(g, m, m, w, h, r);
    const body = g.createLinearGradient(0, m, 0, m + h);
    body.addColorStop(0, 'rgba(34, 26, 85, 0.94)'); body.addColorStop(1, 'rgba(20, 14, 56, 0.96)');
    g.fillStyle = body; g.fill();
    g.restore();
    rr(g, m, m, w, face, [r, r, 0, 0]);
    const top = g.createLinearGradient(0, m, 0, m + face);
    top.addColorStop(0, tint[0]); top.addColorStop(1, tint[1]);
    g.fillStyle = top; g.fill();
    const glow = g.createRadialGradient(m + w / 2, m + face * 0.35, 4, m + w / 2, m + face * 0.35, w * 0.62);
    glow.addColorStop(0, 'rgba(255, 255, 255, 0.35)'); glow.addColorStop(1, 'rgba(255, 255, 255, 0)');
    g.fillStyle = glow; g.fill();
  };
}

/** Le liseré d'une carte (posé par-dessus le portrait) : blanc, fin ; le bas du portrait fondu dans le verre. */
function cardFrame(g: CanvasRenderingContext2D) {
  const m = 8, { w, h, r, face } = CARD;
  const shade = g.createLinearGradient(0, m + face - 34, 0, m + face);
  shade.addColorStop(0, 'rgba(21, 15, 54, 0)'); shade.addColorStop(1, 'rgba(21, 15, 54, 0.85)');
  g.fillStyle = shade; g.fillRect(m, m + face - 34, w, 34);
  g.strokeStyle = 'rgba(255, 244, 220, 0.9)'; g.lineWidth = 3;
  rr(g, m + 1.5, m + 1.5, w - 3, h - 3, r - 1.5); g.stroke();
}

/** La marge autour d'une carte pour sa lueur (attaque spéciale prête) : la texture fait CARD + 2 × GLOW_PAD. */
export const GLOW_PAD = 28;
/** La couleur de la lueur, par élément (vive, plus claire que le haut de la carte) ; or si l'élément est inconnu. */
const GLOW_TINT: Record<string, string> = { fire: '255, 120, 60', wind: '110, 240, 140', water: '90, 190, 255', earth: '255, 196, 90', none: '255, 210, 80' };

/**
 * Le halo d'une carte dont l'attaque spéciale est prête (demande du 27/11) : une lumière douce à la couleur de l'élément,
 * de plus en plus forte vers la carte. Sans flou (iPhone) : des contours arrondis empilés, de plus en plus opaques.
 */
function cardHalo(rgb: string) {
  return (g: CanvasRenderingContext2D) => {
    const p = GLOW_PAD, { w, h, r } = CARD;
    for (let i = p; i >= 1; i--) {
      const k = 1 - i / p;
      g.strokeStyle = `rgba(${rgb}, ${(0.06 + 0.66 * k * k).toFixed(3)})`;
      g.lineWidth = 2.2;
      rr(g, p - i, p - i, w + 2 * i, h + 2 * i, r + i);
      g.stroke();
    }
  };
}

/** Le liseré qui brille, posé par-dessus le cadre de la carte : or clair, cœur blanc. */
function cardRim(g: CanvasRenderingContext2D) {
  const p = GLOW_PAD, { w, h, r } = CARD;
  g.strokeStyle = 'rgba(255, 196, 46, 0.95)'; g.lineWidth = 7;
  rr(g, p, p, w, h, r); g.stroke();
  g.strokeStyle = '#fff1b8'; g.lineWidth = 3.5;
  rr(g, p, p, w, h, r); g.stroke();
  g.strokeStyle = 'rgba(255, 255, 255, 0.9)'; g.lineWidth = 1.2;
  rr(g, p, p, w, h, r); g.stroke();
}

/** L'éclat qui court le long du liseré : un point de lumière (dégradé rond), blanc au cœur, or autour. */
function spark(g: CanvasRenderingContext2D) {
  const s = 18;
  const grad = g.createRadialGradient(s, s, 0, s, s, s);
  grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
  grad.addColorStop(0.25, 'rgba(255, 246, 200, 0.9)');
  grad.addColorStop(0.6, 'rgba(255, 200, 60, 0.35)');
  grad.addColorStop(1, 'rgba(255, 190, 40, 0)');
  g.fillStyle = grad; g.fillRect(0, 0, 2 * s, 2 * s);
}

/** Un point du bord d'une carte (repère : son centre), `t` de 0 à 1 fait le tour dans le sens des aiguilles d'une montre. */
export function cardRimPoint(t: number): [number, number] {
  const { w, h, r } = CARD, sw = w - 2 * r, sh = h - 2 * r, arc = (Math.PI * r) / 2;
  let d = (((t % 1) + 1) % 1) * (2 * sw + 2 * sh + 4 * arc);
  const corner = (cx: number, cy: number, a0: number): [number, number] => {
    const a = a0 + (d / arc) * (Math.PI / 2);
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
  };
  const x0 = -w / 2, y0 = -h / 2;
  if (d < sw) return [x0 + r + d, y0]; d -= sw;
  if (d < arc) return corner(x0 + w - r, y0 + r, -Math.PI / 2); d -= arc;
  if (d < sh) return [x0 + w, y0 + r + d]; d -= sh;
  if (d < arc) return corner(x0 + w - r, y0 + h - r, 0); d -= arc;
  if (d < sw) return [x0 + w - r - d, y0 + h]; d -= sw;
  if (d < arc) return corner(x0 + r, y0 + h - r, Math.PI / 2); d -= arc;
  if (d < sh) return [x0, y0 + h - r - d]; d -= sh;
  return corner(x0 + r, y0 + r, Math.PI);
}

/** Le creux d'une jauge (pilule sombre) : `w` × `h` unités. */
function track(w: number, h: number) {
  return (g: CanvasRenderingContext2D) => {
    rr(g, 0, 0, w, h, h / 2);
    g.fillStyle = 'rgba(5, 2, 26, 0.8)'; g.fill();
  };
}

/** Le signe « pause » (deux barres) et « fermer » : blancs, arrondis. */
function pauseSign(g: CanvasRenderingContext2D) {
  g.fillStyle = '#ffffff';
  rr(g, 6, 4, 8, 28, 4); g.fill();
  rr(g, 22, 4, 8, 28, 4); g.fill();
}

/** Une pilule de verre sombre de `w` × `h` (titre, vague, score) : une texture par taille, faite à la demande. */
export function pillKey(sc: Phaser.Scene, w: number, h = 48): string {
  const key = `hud-pill-${Math.round(w)}x${h}`;
  add(sc, key, Math.round(w), h, (g) => {
    rr(g, 0, 0, Math.round(w), h, h / 2);
    g.fillStyle = 'rgba(13, 8, 38, 0.62)'; g.fill();
    g.strokeStyle = 'rgba(255, 255, 255, 0.2)'; g.lineWidth = 2;
    rr(g, 1, 1, Math.round(w) - 2, h - 2, h / 2 - 1); g.stroke();
  });
  return key;
}

/** Met en file toutes les pièces (à appeler dans `preload`). */
export function loadHudArt(sc: Phaser.Scene) {
  add(sc, 'hud-fade', 8, 256, fade);
  for (const [el, tint] of Object.entries(TINTS)) add(sc, `hud-card-${el}`, CARD.w + 16, CARD.h + 16, card(tint));
  add(sc, 'hud-card-frame', CARD.w + 16, CARD.h + 16, cardFrame);
  for (const [el, rgb] of Object.entries(GLOW_TINT)) add(sc, `hud-card-glow-${el}`, CARD.w + 2 * GLOW_PAD, CARD.h + 2 * GLOW_PAD, cardHalo(rgb));
  add(sc, 'hud-card-rim', CARD.w + 2 * GLOW_PAD, CARD.h + 2 * GLOW_PAD, cardRim);
  add(sc, 'hud-spark', 36, 36, spark);
  add(sc, 'hud-hp', 108, 14, track(108, 14));
  add(sc, 'hud-en', 108, 8, track(108, 8));
  add(sc, 'hud-pause', 36, 36, pauseSign);
  // les galets et les dalles de pierre (SVG de ui/buttons.ts, dessinés R fois plus grands : nets au combat)
  for (const t of HUD_TONES) {
    for (const down of [false, true]) {
      const k = down ? '-down' : '';
      if (!sc.textures.exists(`hud-round-${t}${k}`)) sc.load.image(`hud-round-${t}${k}`, svgDataUrl(roundSvg(t, ROUND, down, R)));
      if (!sc.textures.exists(`hud-btn-${t}${k}`)) sc.load.image(`hud-btn-${t}${k}`, svgDataUrl(pierreSvg(t, WIDE.w, WIDE.h, WIDE.lip, down, R)));
    }
  }
}
