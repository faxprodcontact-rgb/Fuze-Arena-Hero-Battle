// Les pièces du panneau des héros en combat (battle-scene.ts), style moderne (26/11/2026) : les mêmes formes que les menus
// (style.css) — une feuille raisin aux coins arrondis posée sur le combat, des tuiles arrondies pour les portraits, des
// pilules pour la vie et l'énergie, des boutons arrondis à lèvre. Dessinées lisses dans des toiles (×2 pour rester nettes
// sur un téléphone), données à Phaser comme textures.
import type Phaser from 'phaser';

/** Les toiles sont dessinées 2 fois plus grandes que leur taille au combat (puis réduites : bords nets). */
const R = 2;

/** Les boutons : dégradé (haut, milieu, bas), la lèvre, la couleur de l'ombre des lettres. */
export const HUD_BUTTONS = {
  green: { top: '#7cf08a', mid: '#38cc5c', bot: '#25b34a', lip: '#12823a', ink: '#12823a' },
  blue: { top: '#7cc8ff', mid: '#3b95ff', bot: '#2a78f0', lip: '#1a47b8', ink: '#1a47b8' },
  navy: { top: '#4b3c9e', mid: '#3a2d86', bot: '#2e2470', lip: '#150f3a', ink: '#0c0822' },
};

/** Le fond des portraits, par élément : deux tons (haut clair, bas sombre). */
const TILES: Record<string, [string, string]> = {
  fire: ['#ff9a6a', '#c8402a'], wind: ['#8be89a', '#2f9a4c'], water: ['#7cc8ff', '#2a68d0'], earth: ['#ffd07a', '#b8722a'], none: ['#a99cf0', '#4b3c9e'],
};

/** Taille d'un portrait (unités du combat) et son arrondi. */
export const TILE = 112;
export const TILE_R = 26;

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

/** La feuille du bas (720 × 460, dont 20 de marge en haut pour son ombre) : raisin, coins de 44 en haut, filet clair. */
export const PANEL_SHADOW = 20;
function panel(g: CanvasRenderingContext2D) {
  const w = 720, h = 440, y0 = PANEL_SHADOW;
  g.save();
  g.shadowColor = 'rgba(5, 2, 26, 0.55)'; g.shadowBlur = 24; g.shadowOffsetY = -6;
  rr(g, 0, y0, w, h, [44, 44, 0, 0]);
  const grad = g.createLinearGradient(0, y0, 0, y0 + h);
  grad.addColorStop(0, '#2a2063'); grad.addColorStop(0.45, '#1e1650'); grad.addColorStop(1, '#150f36');
  g.fillStyle = grad; g.fill();
  g.restore();
  // un filet de lumière sur le bord du haut
  rr(g, 1, y0 + 1, w - 2, 60, [43, 43, 0, 0]);
  g.save(); g.clip();
  g.strokeStyle = 'rgba(255, 255, 255, 0.14)'; g.lineWidth = 2;
  rr(g, 1, y0 + 1, w - 2, h, [43, 43, 0, 0]); g.stroke();
  g.restore();
}

/** Le fond d'un portrait (l'élément) : une tuile arrondie en dégradé, une lumière douce en haut. */
function tile(cols: [string, string]) {
  return (g: CanvasRenderingContext2D) => {
    rr(g, 0, 0, TILE, TILE, TILE_R);
    const grad = g.createLinearGradient(0, 0, 0, TILE);
    grad.addColorStop(0, cols[0]); grad.addColorStop(1, cols[1]);
    g.fillStyle = grad; g.fill();
    const glow = g.createRadialGradient(TILE * 0.5, TILE * 0.3, 4, TILE * 0.5, TILE * 0.3, TILE * 0.6);
    glow.addColorStop(0, 'rgba(255, 255, 255, 0.35)'); glow.addColorStop(1, 'rgba(255, 255, 255, 0)');
    g.fillStyle = glow; g.fill();
  };
}

/** Le liseré d'un portrait (posé par-dessus le visage) : blanc, une ombre douce dessous. */
function frame(g: CanvasRenderingContext2D) {
  const p = 6;
  g.save();
  g.shadowColor = 'rgba(5, 2, 26, 0.55)'; g.shadowBlur = 10; g.shadowOffsetY = 4;
  g.strokeStyle = '#ffffff'; g.lineWidth = 5;
  rr(g, p, p, TILE, TILE, TILE_R); g.stroke();
  g.restore();
  g.strokeStyle = 'rgba(12, 8, 34, 0.25)'; g.lineWidth = 1.5;
  rr(g, p + 3, p + 3, TILE - 6, TILE - 6, TILE_R - 3); g.stroke();
}

/** La lueur d'or d'un portrait dont l'attaque spéciale est prête. */
function glow(g: CanvasRenderingContext2D) {
  const p = 22;
  g.save();
  g.shadowColor = '#ffc22e'; g.shadowBlur = 22;
  g.strokeStyle = '#ffe27a'; g.lineWidth = 6;
  rr(g, p, p, TILE, TILE, TILE_R); g.stroke(); g.stroke();
  g.restore();
}

/** Le creux d'une jauge (pilule sombre) : `w` × `h` unités. */
function track(w: number, h: number) {
  return (g: CanvasRenderingContext2D) => {
    rr(g, 0, 0, w, h, h / 2);
    g.fillStyle = 'rgba(5, 2, 26, 0.75)'; g.fill();
    g.strokeStyle = 'rgba(255, 255, 255, 0.12)'; g.lineWidth = 1.5;
    rr(g, 0.75, 0.75, w - 1.5, h - 1.5, h / 2); g.stroke();
  };
}

/** Un bouton arrondi : la lèvre, le dégradé, une lumière en haut ; une ombre douce dessous. */
function button(b: (typeof HUD_BUTTONS)[keyof typeof HUD_BUTTONS], w: number, h: number, glass = false) {
  return (g: CanvasRenderingContext2D) => {
    const m = 8, bw = w - 2 * m, bh = h - 2 * m, r = Math.min(26, bh / 2);
    g.save();
    g.shadowColor = 'rgba(5, 2, 26, 0.45)'; g.shadowBlur = 10; g.shadowOffsetY = 4;
    rr(g, m, m, bw, bh, r);
    g.fillStyle = glass ? 'rgba(13, 8, 38, 0.72)' : b.lip; g.fill();
    g.restore();
    if (glass) {
      g.strokeStyle = 'rgba(255, 255, 255, 0.28)'; g.lineWidth = 2;
      rr(g, m + 1, m + 1, bw - 2, bh - 2, r - 1); g.stroke();
      return;
    }
    rr(g, m, m, bw, bh - 6, r);
    const grad = g.createLinearGradient(0, m, 0, m + bh - 6);
    grad.addColorStop(0, b.top); grad.addColorStop(0.46, b.mid); grad.addColorStop(1, b.bot);
    g.fillStyle = grad; g.fill();
    g.strokeStyle = 'rgba(255, 255, 255, 0.45)'; g.lineWidth = 2;
    g.save(); rr(g, m, m, bw, 14, [r, r, 0, 0]); g.clip();
    rr(g, m + 1, m + 1, bw - 2, bh - 8, r - 1); g.stroke();
    g.restore();
  };
}

/** Le fond du titre du combat (pilule de verre sombre) : étirée à la largeur du titre. */
function pill(g: CanvasRenderingContext2D) {
  rr(g, 0, 0, 120, 56, 28);
  g.fillStyle = 'rgba(13, 8, 38, 0.62)'; g.fill();
  g.strokeStyle = 'rgba(255, 255, 255, 0.18)'; g.lineWidth = 2;
  rr(g, 1, 1, 118, 54, 27); g.stroke();
}

/** Met en file toutes les pièces du panneau (à appeler dans `preload`). Les boutons : une taille par usage. */
export function loadHudArt(sc: Phaser.Scene) {
  add(sc, 'hud-panel', 720, 440 + PANEL_SHADOW, panel);
  add(sc, 'hud-frame', TILE + 12, TILE + 12, frame);
  add(sc, 'hud-glow', TILE + 44, TILE + 44, glow);
  add(sc, 'hud-hp', 116, 18, track(116, 18));
  add(sc, 'hud-en', 116, 10, track(116, 10));
  add(sc, 'hud-pill', 120, 56, pill);
  for (const [el, cols] of Object.entries(TILES)) add(sc, `hud-disc-${el}`, TILE, TILE, tile(cols));
  for (const [k, b] of Object.entries(HUD_BUTTONS)) {
    add(sc, `hud-btn-${k}-290`, 306, 100, button(b, 306, 100));
    add(sc, `hud-btn-${k}-160`, 176, 78, button(b, 176, 78, k === 'navy'));
  }
}
