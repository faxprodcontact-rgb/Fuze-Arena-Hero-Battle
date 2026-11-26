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

/** La lueur d'or d'une carte dont l'attaque spéciale est prête. */
function cardGlow(g: CanvasRenderingContext2D) {
  const p = 22, { w, h, r } = CARD;
  g.save();
  g.shadowColor = '#ffc22e'; g.shadowBlur = 20;
  g.strokeStyle = '#ffe27a'; g.lineWidth = 5;
  rr(g, p, p, w, h, r); g.stroke(); g.stroke();
  g.restore();
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
  add(sc, 'hud-card-glow', CARD.w + 44, CARD.h + 44, cardGlow);
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
