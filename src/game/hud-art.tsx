// Les pièces de l'interface du combat (battle-scene.ts), style moderne (26/11/2026, demande du propriétaire : « on voit
// tout le terrain, sans bandeau ») : tout flotte sur la scène, léger — des boutons ronds, des pilules de verre sombre, une
// rangée de cartes de héros (portrait, nom, vie, énergie) posée sur un fondu doux en bas de l'écran.
// Dessinées lisses dans des toiles (×2 pour rester nettes sur un téléphone), données à Phaser comme textures.
import type Phaser from 'phaser';

/** Les toiles sont dessinées 2 fois plus grandes que leur taille au combat (puis réduites : bords nets). */
const R = 2;
/** (pour poser une texture faite ici à sa vraie taille : `setScale(1 / HUD_RES)`) */
export const HUD_RES = R;

/** Les boutons : dégradé (haut, milieu, bas), la lèvre, la couleur de l'ombre des lettres. */
export const HUD_BUTTONS = {
  green: { top: '#7cf08a', mid: '#38cc5c', bot: '#25b34a', lip: '#12823a', ink: '#12823a' },
  blue: { top: '#7cc8ff', mid: '#3b95ff', bot: '#2a78f0', lip: '#1a47b8', ink: '#1a47b8' },
  red: { top: '#ff98a2', mid: '#ff5a6c', bot: '#f03e58', lip: '#b01f3a', ink: '#b01f3a' },
  navy: { top: '#4b3c9e', mid: '#3a2d86', bot: '#2e2470', lip: '#150f3a', ink: '#0c0822' },
};
export type HudButton = keyof typeof HUD_BUTTONS;

/** Le haut des cartes, par élément : deux tons (haut clair, bas sombre). */
const TINTS: Record<string, [string, string]> = {
  fire: ['#ff9a6a', '#c8402a'], wind: ['#8be89a', '#2f9a4c'], water: ['#7cc8ff', '#2a68d0'], earth: ['#ffd07a', '#b8722a'], none: ['#a99cf0', '#4b3c9e'],
};

/** Une carte de héros (unités du combat) : sa taille, son arrondi, la hauteur du portrait. */
export const CARD = { w: 128, h: 182, r: 22, face: 120 };
/** Un bouton rond : son diamètre. */
export const ROUND = 68;

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
    body.addColorStop(0, 'rgba(42, 32, 99, 0.94)'); body.addColorStop(1, 'rgba(21, 15, 54, 0.96)');
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
  g.strokeStyle = 'rgba(255, 255, 255, 0.9)'; g.lineWidth = 3;
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

/** Un bouton rond : la lèvre, le dégradé (ou du verre sombre), une lumière en haut ; une ombre douce. */
function round(kind: HudButton | 'glass') {
  return (g: CanvasRenderingContext2D) => {
    const m = 8, d = ROUND, c = m + d / 2;
    g.save();
    g.shadowColor = 'rgba(5, 2, 26, 0.5)'; g.shadowBlur = 10; g.shadowOffsetY = 4;
    g.beginPath(); g.arc(c, c, d / 2, 0, Math.PI * 2);
    g.fillStyle = kind === 'glass' ? 'rgba(13, 8, 38, 0.7)' : HUD_BUTTONS[kind].lip; g.fill();
    g.restore();
    if (kind === 'glass') {
      g.strokeStyle = 'rgba(255, 255, 255, 0.3)'; g.lineWidth = 2;
      g.beginPath(); g.arc(c, c, d / 2 - 1, 0, Math.PI * 2); g.stroke();
      return;
    }
    const b = HUD_BUTTONS[kind];
    g.beginPath(); g.arc(c, c - 2.5, d / 2 - 2.5, 0, Math.PI * 2);
    const grad = g.createLinearGradient(0, m, 0, m + d);
    grad.addColorStop(0, b.top); grad.addColorStop(0.5, b.mid); grad.addColorStop(1, b.bot);
    g.fillStyle = grad; g.fill();
    g.strokeStyle = 'rgba(255, 255, 255, 0.45)'; g.lineWidth = 2;
    g.beginPath(); g.arc(c, c - 2.5, d / 2 - 3.5, Math.PI * 1.15, Math.PI * 1.85); g.stroke();
  };
}

/** Un bouton large arrondi (fenêtre de pause) : la lèvre, le dégradé, une lumière en haut. */
function wide(b: (typeof HUD_BUTTONS)[HudButton], w: number, h: number) {
  return (g: CanvasRenderingContext2D) => {
    const m = 8, bw = w - 2 * m, bh = h - 2 * m, r = Math.min(26, bh / 2);
    g.save();
    g.shadowColor = 'rgba(5, 2, 26, 0.45)'; g.shadowBlur = 10; g.shadowOffsetY = 4;
    rr(g, m, m, bw, bh, r);
    g.fillStyle = b.lip; g.fill();
    g.restore();
    rr(g, m, m, bw, bh - 6, r);
    const grad = g.createLinearGradient(0, m, 0, m + bh - 6);
    grad.addColorStop(0, b.top); grad.addColorStop(0.46, b.mid); grad.addColorStop(1, b.bot);
    g.fillStyle = grad; g.fill();
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
  for (const k of ['glass', 'green', 'blue'] as const) add(sc, `hud-round-${k}`, ROUND + 16, ROUND + 16, round(k));
  add(sc, 'hud-pause', 36, 36, pauseSign);
  for (const [k, b] of Object.entries(HUD_BUTTONS)) add(sc, `hud-btn-${k}`, 306, 100, wide(b, 306, 100));
}
