// Les pièces du panneau des héros en combat (battle-scene.ts), nouvelle DA (26/11/2026) : les mêmes dessins en pixels que
// les menus (ui/px.ts : une seule palette, un seul contour, lumière en haut à droite), recomposés à la bonne taille et
// agrandis ×4 (un pixel du dessin = 4 unités du combat, à peu près 2 pixels CSS sur un téléphone), sans flou.
import type Phaser from 'phaser';
import { INK, PAL, pxCanvas, radialCanvas, rampFrom, type Tone } from './ui/px';

/** Unités du combat par pixel du dessin. */
const U = 4;

/** Les couleurs des boutons : la teinte du dessin et la couleur du cerne des lettres. */
export const HUD_BUTTONS = {
  green: { tone: 'green' as Tone, ink: '#145040' },
  blue: { tone: 'blue' as Tone, ink: '#1c2f7a' },
  navy: { tone: 'navy' as Tone, ink: '#121636' },
};

/** Les disques des portraits, par élément (la couleur du milieu de leur gamme). */
const DISCS: Record<string, string> = { fire: '#d8502e', wind: '#4fae5a', water: '#3f86e0', earth: '#b8822e', none: '#4a5fc0' };

function add(sc: Phaser.Scene, key: string, make: () => HTMLCanvasElement) {
  if (sc.textures.exists(key)) return;
  const tex = sc.textures.addCanvas(key, make());
  tex?.setFilter(1 as Phaser.Textures.FilterMode); // au plus proche : les pixels restent nets
}

/** Le panneau (720 × 400) : émail bleu nuit, le plateau creusé des portraits cerclé d'or. */
function panel(): HTMLCanvasElement {
  const w = 180, h = 100;
  const c = document.createElement('canvas');
  c.width = w * U; c.height = h * U;
  const g = c.getContext('2d')!;
  g.imageSmoothingEnabled = false;
  g.fillStyle = PAL.navy[2]; g.fillRect(0, 0, c.width, c.height);
  g.fillStyle = PAL.navy[1]; g.fillRect(0, (h - 2) * U, c.width, 2 * U);
  const tray = pxCanvas('plaque-navy', 176, 56, U);
  // le creux du plateau : la plaque, assombrie au milieu (les portraits s'y posent)
  g.drawImage(tray, 2 * U, 7 * U);
  g.fillStyle = PAL.well[1]; g.fillRect(4 * U, 10 * U, 172 * U, 50 * U);
  g.fillStyle = PAL.well[0]; g.fillRect(4 * U, 9 * U, 172 * U, U);
  return c;
}

/** Le rail (720 × 16) posé à cheval sur le bas du terrain : contour, filet d'or, contour. */
function rail(): HTMLCanvasElement {
  const c = document.createElement('canvas');
  c.width = 720; c.height = 4 * U;
  const g = c.getContext('2d')!;
  [INK, PAL.gold[3], PAL.gold[1], INK].forEach((col, i) => { g.fillStyle = col; g.fillRect(0, i * U, 720, U); });
  return c;
}

/** Met en file toutes les pièces du panneau (à appeler dans `preload`). Les boutons : une taille par usage. */
export function loadHudArt(sc: Phaser.Scene) {
  add(sc, 'hud-panel', panel);
  add(sc, 'hud-rail', rail);
  // l'anneau d'un portrait (144) : contour, or, contour, la rainure sombre où court l'énergie, contour ; le centre vide
  add(sc, 'hud-ring', () => radialCanvas(36, [[12.5, null], [12.9, INK], [14.7, PAL.well[1]], [15.5, INK], [17.2, PAL.gold], [18, INK]], U));
  // la rainure de la barre de vie (120 × 24)
  add(sc, 'hud-hp', () => pxCanvas('groove', 30, 6, U));
  for (const [el, col] of Object.entries(DISCS)) add(sc, `hud-disc-${el}`, () => radialCanvas(25, [[13, rampFrom(col)]], U));
  for (const [k, b] of Object.entries(HUD_BUTTONS)) {
    add(sc, `hud-btn-${k}-290`, () => pxCanvas(`btn-${b.tone}`, 73, 21, U));
    add(sc, `hud-btn-${k}-160`, () => pxCanvas(`btn-${b.tone}`, 40, 16, U));
  }
}
