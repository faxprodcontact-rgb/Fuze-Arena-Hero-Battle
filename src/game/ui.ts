// Petits éléments d'interface réutilisés par tous les écrans.
import Phaser from 'phaser';
import { UI } from './art';

export const W = 720;
export const H = 1280;
export const FONT = '"Trebuchet MS", "Segoe UI", Roboto, sans-serif';

export function text(
  scene: Phaser.Scene, x: number, y: number, value: string, size = 28, color = UI.text, weight = 'bold',
): Phaser.GameObjects.Text {
  return scene.add
    .text(x, y, value, { fontFamily: FONT, fontSize: `${size}px`, color, fontStyle: weight, align: 'center' })
    .setOrigin(0.5)
    .setShadow(0, 2, '#000000', 3, false, true);
}

export interface Button extends Phaser.GameObjects.Container {
  label: Phaser.GameObjects.Text;
  setEnabled(on: boolean): Button;
}

export function button(
  scene: Phaser.Scene, x: number, y: number, w: number, h: number, label: string,
  color: number, onClick: () => void, size = 30,
): Button {
  const c = scene.add.container(x, y) as Button;
  const bg = scene.add.graphics();
  const draw = (fill: number) => {
    bg.clear();
    bg.fillStyle(0x000000, 0.35);
    bg.fillRoundedRect(-w / 2, -h / 2 + 6, w, h, 18);
    bg.fillStyle(fill);
    bg.fillRoundedRect(-w / 2, -h / 2, w, h, 18);
    bg.fillStyle(0xffffff, 0.18);
    bg.fillRoundedRect(-w / 2 + 6, -h / 2 + 5, w - 12, h * 0.38, 12);
  };
  draw(color);
  const label_ = text(scene, 0, 0, label, size);
  c.add([bg, label_]);
  c.label = label_;
  c.setSize(w, h);
  let enabled = true;
  c.setInteractive({ useHandCursor: true });
  c.on('pointerdown', () => enabled && c.setScale(0.95));
  c.on('pointerout', () => c.setScale(1));
  c.on('pointerup', () => {
    c.setScale(1);
    if (enabled) onClick();
  });
  c.setEnabled = (on: boolean) => {
    enabled = on;
    draw(on ? color : 0x4a4f6e);
    label_.setAlpha(on ? 1 : 0.6);
    return c;
  };
  return c;
}

export function panel(scene: Phaser.Scene, x: number, y: number, w: number, h: number, color: number = UI.panel, alpha = 1) {
  const g = scene.add.graphics();
  g.fillStyle(color, alpha);
  g.fillRoundedRect(x - w / 2, y - h / 2, w, h, 22);
  return g;
}

/** Point rouge « il y a quelque chose à faire ici ». */
export function redDot(scene: Phaser.Scene, x: number, y: number) {
  const dot = scene.add.circle(x, y, 13, UI.red).setStrokeStyle(3, 0xffffff);
  scene.tweens.add({ targets: dot, scale: 1.2, yoyo: true, repeat: -1, duration: 500 });
  return dot;
}

/** Un doigt qui montre où toucher, à la place d'une phrase d'explication. */
export function pointAt(scene: Phaser.Scene, x: number, y: number, from: 'below' | 'right' = 'below') {
  if (from === 'right') {
    const f = scene.add.image(x + 70, y, 'finger').setAngle(-90).setDepth(50);
    scene.tweens.add({ targets: f, x: x + 50, yoyo: true, repeat: -1, duration: 450, ease: 'Sine.easeInOut' });
    return f;
  }
  const f = scene.add.image(x, y + 70, 'finger').setDepth(50);
  scene.tweens.add({ targets: f, y: y + 50, yoyo: true, repeat: -1, duration: 450, ease: 'Sine.easeInOut' });
  return f;
}

export function goldBar(scene: Phaser.Scene, amount: number) {
  panel(scene, W - 130, 50, 220, 60, UI.panelLight);
  scene.add.circle(W - 210, 50, 17, UI.gold).setStrokeStyle(3, 0xb8860b);
  return text(scene, W - 120, 50, amount.toLocaleString('fr-FR'), 30, '#ffe27a');
}

export function background(scene: Phaser.Scene, top = 0x23295a, bottom = UI.bg) {
  const g = scene.add.graphics();
  g.fillGradientStyle(top, top, bottom, bottom, 1);
  g.fillRect(0, 0, W, H);
  return g;
}
